from bedrock_agentcore import BedrockAgentCoreApp
from app.agent.agent_coordinator import get_coordinator

app = BedrockAgentCoreApp()


@app.entrypoint
async def invoke(payload):
    """
    AgentCore entrypoint.
    """

    print(f"PAYLOAD RECEIVED: {payload}")

    # Handle different payload formats
    if isinstance(payload, str):
        query = payload
    else:
        query = (
            payload.get("query")
            or payload.get("input")
            or payload.get("message")
            or payload.get("prompt")
            or ""
        )

    print(f"EXTRACTED QUERY: {query}")

    coordinator = get_coordinator()

    result = coordinator.process_request(query)
    
    print("response: [VERSION_JUNE21] ")
    print(result["response"])
    
    return result

print("AGENTCORE STARTED")

if __name__ == "__main__":
    app.run()