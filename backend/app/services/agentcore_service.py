# app/services/agentcore_service.py

import boto3
import json
from app.core.config import get_settings

settings = get_settings()

class AgentCoreService:

    def __init__(self):

        self.client = boto3.client(
            "bedrock-agentcore",
            region_name=settings.aws_region
        )

        self.agent_runtime_arn = (
            settings.agentcore_runtime_arn
        )

    def invoke(self, query: str):
        print("=" * 80)
        print("AGENTCORE INVOKE")
        print("QUERY:", query)
        print("RUNTIME ARN:", self.agent_runtime_arn)
        print("=" * 80)

        response = self.client.invoke_agent_runtime(
            agentRuntimeArn=self.agent_runtime_arn,
            contentType="application/json",
            accept="application/json",
            payload=json.dumps({
                "query": query
            }).encode("utf-8")
        )

        body = response["response"].read()
        raw_response = body.decode("utf-8")

        print("=" * 80)
        print("RAW AGENTCORE RESPONSE")
        print(raw_response)
        print("=" * 80)

        print("RUNTIME SESSION ID:",
            response.get("runtimeSessionId"))

        print("REQUEST ID:",
            response["ResponseMetadata"].get("RequestId"))

        result = json.loads(raw_response)

        return {
            "response": result.get("response"),
            "agents_used": result.get("agents_used", []),
            "success": result.get("success", False),
            "session_id": response.get("runtimeSessionId"),
            "request_id": response["ResponseMetadata"].get("RequestId")
        }