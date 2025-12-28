import queue
import litellm
from typing import Any, Dict
from ..common.logger import logger


class CrewService:
    def __init__(self):
        self.question_queue = queue.Queue()
        self.answer_queue = queue.Queue()
        self.message_queue = queue.Queue()
        self.crew = None
    
    def set_crew(self, crew):
        """Set the pre-initialized crew"""
        self.crew = crew
        return self
    
    async def start_process(self, message: str) -> Dict[str, Any]:
        """Start the processing with the pre-initialized crew"""
        if not self.crew:
            raise ValueError("Crew not initialized")
        
        # Start crew in a separate thread
        import threading
        
        result_queue = queue.Queue()
        
        def run_crew():
            try:
                # Use the pre-initialized crew
                result = self.crew.kickoff(inputs={"user_input": message})
                result_queue.put({"success": True, "result": result})
            except Exception as e:
                logger.error(f"[CrewServic] {e}")
                result_queue.put({"success": False, "error": str(e)})
        
        thread = threading.Thread(target=run_crew)
        thread.start()
        
        return {
            "status": "processing",
            "message": "CrewAI process started. Connect to WebSocket for interactive session."
        }
    
    def run_crew_process(self, message: str, result_queue: queue.Queue):
        try:
            # Clear queues
            self.question_queue = queue.Queue()
            self.answer_queue = queue.Queue()
            self.message_queue = queue.Queue()
            
            result = self.crew.kickoff(inputs={"user_input": message})
            result_queue.put({"type": "final_result", "result": str(result)})

        except litellm.RateLimitError as e:
            # Specifically handles the 429 Resource Exhausted error
            logger.warning(f"[CrewService] Rate Limit Hit: {e}")
            result_queue.put({
                "type": "error", 
                "message": "Rate limit exceeded. Please wait a moment before trying again.",
                "code": 429
            })

        except litellm.AuthenticationError as e:
            logger.error(f"[CrewService] Auth Error: {e}")
            result_queue.put({
                "type": "error", 
                "message": "Authentication failed. Please check API keys.",
                "code": 401
            })

        except Exception as e:
            # Fallback string matching for other providers or general errors
            error_str = str(e).lower()
            logger.error(f"[CrewService] {e}")
            
            if "quota exceeded" in error_str or "429" in error_str:
                msg = "Resource exhausted: You have reached your API quota limit."
            elif "invalid api key" in error_str or "401" in error_str:
                msg = "Invalid API key provided."
            elif "context_length_exceeded" in error_str:
                msg = "The request is too long for the model's context window."
            else:
                msg = "An unexpected error occurred within the Crew process."

            result_queue.put({"type": "error", "message": msg})

    def send_message(self, message: str):
        """Send a message to the crew"""
        self.message_queue.put(message)
        print(f"Message sent to crew: {message}")
