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

        response = self.client.invoke_agent_runtime(
            agentRuntimeArn=self.agent_runtime_arn,
            contentType="application/json",
            accept="application/json",
            payload=json.dumps({
                "query": query
            }).encode("utf-8")
        )

        body = response["response"].read()

        result = json.loads(
            body.decode("utf-8")
        )

        return {
            "response": result.get("response"),
            "agents_used": result.get("agents_used", []),
            "success": result.get("success", False),

            "session_id": response.get(
                "runtimeSessionId"
            ),

            "request_id": response[
                "ResponseMetadata"
            ].get(
                "RequestId"
            )
        }