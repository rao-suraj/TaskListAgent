import queue
import threading
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from api.services.crew_service import crew_service
import asyncio
import json

from tasklist_agent_crew_ai.crew import TasklistAgentCrewAi

router = APIRouter(tags=["chat"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    task_list_crew = TasklistAgentCrewAi().crew()
    crew_service.set_crew(task_list_crew)

    result_queue = queue.Queue()

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

                if user_message.get("event") == "start":
                    message = user_message.get("message", "")
                    thread = threading.Thread(target=crew_service.run_crew_process, args=(message,result_queue))
                    thread.start()
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
