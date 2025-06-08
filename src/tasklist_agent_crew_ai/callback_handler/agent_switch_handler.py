from ...api.services.crew_service import crew_service

class AgentSwitchHandler():
    def __init__(self):
        super().__init__()

    def task_callback(step_output):
        message = "SWITCH: TASK COMPLETED"
        agent_name = step_output.agent.strip().lower()
        print(f"AgentSwitchHandler: task_callback called with step_output:{agent_name}")
        match agent_name:
            case "business analyst":
                message = "SWITCH: Experienced Developer"
            case "expereinced developer":
                message = "SWITCH: Project Manager"
        crew_service.send_message(message=message)