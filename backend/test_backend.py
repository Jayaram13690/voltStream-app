from app.agent.agent_coordinator import get_coordinator

coordinator = get_coordinator()

result = coordinator.process_request(
    "turn off the heat pump and provide how it impact?"
)

print(result)