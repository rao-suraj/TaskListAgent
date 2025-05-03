import queue
from typing import Any, Dict


class CrewService:
    def __init__(self):
        self.question_queue = queue.Queue()
        self.answer_queue = queue.Queue()
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
                result_queue.put({"success": False, "error": str(e)})
        
        thread = threading.Thread(target=run_crew)
        thread.start()
        
        return {
            "status": "processing",
            "message": "CrewAI process started. Connect to WebSocket for interactive session."
        }
    
    def run_crew_process(self,message: str, result_queue: queue.Queue):
        try:
            result = self.crew.kickoff(inputs={"user_input": message})
            print(f"Result from crew: {result}")
            result_queue.put({"type": "final_result", "result": str(result)})
        except Exception as e:
            result_queue.put({"type": "error", "error": str(e)})

    

crew_service = CrewService()