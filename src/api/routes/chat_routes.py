import queue
import threading
from typing import Dict, Optional
from uuid import uuid4
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from litellm import BaseModel, Field
from pydantic import Extra
from api.auth.jwt_handler import create_jwt, verify_jwt
from api.services.crew_service import crew_service
import asyncio
import json
import jwt

from tasklist_agent_crew_ai.crew import TasklistAgentCrewAi


router = APIRouter(tags=["chat"])

session_env_store: Dict[str, Dict] = {}
session_ttl: Dict[str, asyncio.Task] = {}


class EnvPayload(BaseModel):
    google_api_key: str = Field(
        ..., 
        min_length=1, 
        description="Your Google API key"
    )
    tavily_api_key: Optional[str] = Field(
        None, 
        min_length=1, 
        description="Your Tavily API key (optional)"
    )

    class Config:
        extra = Extra.forbid 

@router.post("/create-session")
async def create_session(payload: EnvPayload):
    session_id = str(uuid4())

    clean_envs: dict[str, str] = {
        "GOOGLE_API_KEY": payload.google_api_key,
    }
    if payload.tavily_api_key:
        clean_envs["TAVILY_API_KEY"] = payload.tavily_api_key

    session_env_store[session_id] = clean_envs

    token = create_jwt(session_id)

    # TTL task to expire session
    session_ttl[session_id] = asyncio.create_task(expire_session(session_id, delay=900))  # 15 minutes
    return {"token": token}

async def expire_session(session_id: str, delay: int):
    await asyncio.sleep(delay)
    session_env_store.pop(session_id, None)
    session_ttl.pop(session_id, None)

@router.websocket("/ws")    
async def websocket_endpoint(websocket: WebSocket):
    print("WebSocket connection attempt")
    
    # Accept connection without authentication
    await websocket.accept()
    print("WebSocket connection established, waiting for authentication")
    
    # Wait for authentication message
    authenticated = False
    session_id = None
    envs = None
    
    try:
        # Wait for auth message with timeout
        auth_data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
        auth_message = json.loads(auth_data)
        
        if auth_message.get("event") != "auth":
            await websocket.send_json({
                "type": "error",
                "message": "First message must be authentication"
            })
            await websocket.close(code=1008)
            return
            
        token = auth_message.get("token")
        if not token:
            await websocket.send_json({
                "type": "error", 
                "message": "Token is required"
            })
            await websocket.close(code=1008)
            return
            
        try:
            session_id = verify_jwt(token)
            print(f"Token verified for session: {session_id}")
        except jwt.PyJWTError as e:
            print(f"JWT verification failed: {e}")
            await websocket.send_json({
                "type": "error",
                "message": "Invalid token"
            })
            await websocket.close(code=1008)
            return
        
        if not session_id or session_id not in session_env_store:
            await websocket.send_json({
                "type": "error",
                "message": "Invalid or expired session"
            })
            await websocket.close(code=1008)
            return
            
        # Authentication successful
        authenticated = True
        envs = session_env_store[session_id]
        await websocket.send_json({
            "type": "auth_success",
            "message": "Authentication successful"
        })
        print(f"Authentication successful for session: {session_id}")
        
    except asyncio.TimeoutError:
        print("Authentication timeout")
        await websocket.send_json({
            "type": "error",
            "message": "Authentication timeout"
        })
        await websocket.close(code=1008)
        return
    except json.JSONDecodeError:
        print("Invalid JSON in auth message")
        await websocket.send_json({
            "type": "error",
            "message": "Invalid JSON format"
        })
        await websocket.close(code=1008)
        return
    except Exception as e:
        print(f"Authentication error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": "Authentication failed"
        })
        await websocket.close(code=1008)
        return

    # Initialize CrewAI after successful authentication
    task_list_crew = TasklistAgentCrewAi(
        google_api_key=envs.get("GOOGLE_API_KEY"),
        tavily_api_key=envs.get("TAVILY_API_KEY", None)
    ).crew()
    crew_service.set_crew(task_list_crew)
    result_queue = queue.Queue()
    current_thread: Optional[threading.Thread] = None

    try:
        while True:
            # Check for CrewAI questions
            while not crew_service.question_queue.empty():
                question = crew_service.question_queue.get_nowait()
                await websocket.send_json({
                    "type": "question",
                    "question": question
                })

            # Check for final result from crew thread
            while not result_queue.empty():
                msg = result_queue.get_nowait()
                await websocket.send_json(msg)

            while not crew_service.question_queue.empty():
                question = crew_service.question_queue.get_nowait()
                await websocket.send_json({
                    "type": "question",
                    "question": question
                })

            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                user_message = json.loads(data)

                # Skip auth events since we're already authenticated
                if user_message.get("event") == "auth":
                    await websocket.send_json({
                        "type": "info",
                        "message": "Already authenticated"
                    })
                    continue

                if user_message.get("event") == "start":
                    message = user_message.get("message", "")
                    if current_thread is not None and current_thread.is_alive():
                        # Don't wait here - let it finish in background
                        print("Previous thread still running, starting new conversation anyway")
        
                    # Step 2: Create fresh queue for new conversation
                    result_queue = queue.Queue()
                    current_thread = threading.Thread(target=crew_service.run_crew_process, args=(message, result_queue))
                    current_thread.daemon = True
                    current_thread.start()
                    await websocket.send_json({
                        "type": "status",
                        "message": "CrewAI process started"
                    })

                elif "answer" in user_message:
                    print(f"Received answer: {user_message['answer']}")
                    crew_service.answer_queue.put(user_message["answer"])
                    print(f"Answer queue size: {crew_service.answer_queue.qsize()}")
                    await websocket.send_json({
                        "type": "confirmation",
                        "message": "Answer received"
                    })

            except asyncio.TimeoutError:
                await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close(code=1011)