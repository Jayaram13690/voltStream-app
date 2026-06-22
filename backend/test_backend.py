from app.agent.agent_coordinator import get_coordinator

coordinator = get_coordinator()

result = coordinator.process_request(
    "what is the status of HVAC"
)

print(result)