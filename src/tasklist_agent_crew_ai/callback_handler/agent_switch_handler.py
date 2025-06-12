

class AgentSwitchHandler():
    def __init__(self,crew_service_instance=None):
        super().__init__()
        self.crew_service_instance = crew_service_instance


    def task_callback(self,step_output):
        message = "SWITCH: TASK COMPLETED"
        agent_name = step_output.agent.strip().lower()
        print(f"AgentSwitchHandler: task_callback called with step_output:{agent_name}")
        match agent_name:
            case "business analyst":
                message = "SWITCH: Experienced Developer"
            case "expereinced developer":
                message = "SWITCH: Project Manager"
        self.crew_service_instance.send_message(message=message)