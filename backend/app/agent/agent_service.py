"""
Powered by:
  * Amazon Bedrock  Nova 2 Lite  (us.amazon.nova-2-lite-v1:0)
  * Strands Agents SDK 0.3.0
  * ReAct  (Reason -> Tool Call -> Observe -> Reason -> ... -> Respond)

Decision-making that is now handled entirely by Nova Lite (not Python):
  - Intent classification
  - Target device discovery & name->id resolution
  - Workflow sequencing  (which tool, in what order)
  - Multi-device bulk operations via update_multiple_devices
  - Pronoun / context resolution from conversation memory
  - Error recovery reasoning

The only Python logic that remains:
  - Conversation memory appending
  - Strands Agent initialisation
  - HTTP error propagation
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

import boto3
from botocore.config import Config as BotoCoreConfig
from botocore.exceptions import BotoCoreError, ClientError
from pydantic import BaseModel
from strands import Agent
from strands.models.bedrock import BedrockModel

from app.agent.tools.device_tools import (
    get_device_status_tool,
    list_devices_tool,
    set_device_status_tool,
    update_multiple_devices_tool,
)
# from app.core.config import get_settings
from app.agent.agent_blackboard import get_blackboard

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# System prompt — concise agentic instructions
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """You are a Device Control Agent managing smart-home devices autonomously.

## Rules
1. Never ask for confirmation - decide and act
2. Use list_devices first when unsure of device IDs
3. Use update_multiple_devices for 2+ devices, set_device_status for single devices
4. Resolve pronouns using conversation history
5. All devices use only "on"/"off" states

## Tools
- list_devices: List all devices with IDs and statuses
- get_device_status(device_id): Get single device status
- set_device_status(device_id, state): Set single device (state: "on"/"off")
- update_multiple_devices(updates): Bulk update multiple devices

## Workflow
1. Analyze request
2. Select appropriate tool(s)
3. Execute and observe results
4. Respond with clear confirmation of changes

## Response Requirements
- Be concise (50 words max)
- Confirm what changed and new state
- Mention if device was already in requested state
- Explain errors clearly

## Critical
Always verify device IDs via list_devices - never hardcode IDs.
"""


# ─────────────────────────────────────────────
# Response schema (for API layer)
# ─────────────────────────────────────────────
class DeviceStatusResponse(BaseModel):
    """Response model for device status"""
    device_id: int
    device_name: str
    status: str


# ─────────────────────────────────────────────
# Agent
# ─────────────────────────────────────────────
class DeviceControlAgent:
    """
    90% Agentic Device Control Agent.

    Nova Lite drives all decision-making through Strands' native tool-calling
    loop.  Python only:
      - builds the conversation message list
      - calls agent()
      - appends history entries
    """
    

    def __init__(self):
        # settings = get_settings()
        self.bedrock_model_id = "global.amazon.nova-2-lite-v1:0"
        self.aws_region = "us-east-1"

        self.model_id = self.bedrock_model_id  # us.amazon.nova-2-lite-v1:0
        
        # Initialize blackboard for multi-agent coordination
        self.blackboard = get_blackboard()

        botocore_cfg = BotoCoreConfig(
            read_timeout=300,
            connect_timeout=30,
            retries={"max_attempts": 3},
        )

        model = BedrockModel(
            model_id=self.model_id,
            region_name=self.aws_region,
            boto_client_config=botocore_cfg,
            temperature=0.1,
            top_p=0.8,
            max_tokens=200,
            streaming=False,
        )

        # Build the Strands Agent with all four device tools
        self.agent = Agent(
            model=model,
            system_prompt=SYSTEM_PROMPT,
            tools=[
                list_devices_tool,
                get_device_status_tool,
                set_device_status_tool,
                update_multiple_devices_tool,
            ],
        )

        # Conversation memory — persisted across requests within one process
        self.conversation_history: List[Dict[str, Any]] = []

        logger.info(
            "DeviceControlAgent ready | model=%s | tools=[list_devices, "
            "get_device_status, set_device_status, update_multiple_devices]",
            self.model_id,
        )

    # ──────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────

    def process_request(self, user_request: str) -> str:
        """
        Process a natural-language device-control request.

        The Strands Agent handles the full ReAct loop:
          Reason -> Select tool -> Execute -> Observe -> Reason -> ... -> Respond

        Args:
            user_request: Natural language input from the user.

        Returns:
            Natural language response string.
        """
        logger.info("User Request: %s", user_request)

        # Build context-enriched message with recent conversation history
        # so Nova Lite can resolve pronouns and maintain continuity
        context_block = self._format_history_context()

        full_message = (
            f"{context_block}\n\nUser: {user_request}"
            if context_block
            else user_request
        )

        # Record user turn in memory
        self.conversation_history.append(
            {
                "role": "user",
                "content": user_request,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Let Strands / Nova Lite drive the full ReAct loop
        try:
            result = self.agent(full_message)
            final_response = self._extract_text(result)

        except (ClientError, BotoCoreError) as exc:
            logger.error("Bedrock error: %s", exc)
            final_response = (
                "I encountered an AWS service error while processing your request. "
                "Please check your credentials and try again."
            )
        except Exception as exc:
            logger.error("Agent error: %s", exc, exc_info=True)
            final_response = (
                "I encountered an unexpected error. "
                "Please try again or rephrase your request."
            )

        # Record assistant turn in memory
        self.conversation_history.append(
            {
                "role": "assistant",
                "content": final_response,
                "timestamp": datetime.now().isoformat(),
            }
        )

        logger.info("Final Response: %s", final_response)
        
        # Update blackboard with device changes
        # Parse response to extract device changes and trigger events
        self.blackboard.add_action({
            "type": "device_agent_response",
            "query": user_request,
            "response": final_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Trigger device status update event for frontend synchronization
        # This ensures frontend gets notified of device changes
        import json
        try:
            # Simple parsing to detect device changes in response
            if "turned on" in final_response.lower() or "turned off" in final_response.lower():
                # This would be more sophisticated in production
                # For now, we'll add a simple event trigger mechanism
                pass  # Event triggering will be handled by coordinator
        except Exception as e:
            logger.error("Error parsing device changes from response: %s", e)
        
        return final_response

    def reset_memory(self) -> None:
        """Clear conversation history (useful between sessions)."""
        self.conversation_history.clear()
        logger.info("Conversation history cleared.")

    # ──────────────────────────────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────────────────────────────

    def _format_history_context(self) -> str:
        """
        Render the last N conversation turns as a compact text block so Nova
        Lite can use it for pronoun resolution and continuity.
        """
        # Reduced from 10 to 6 turns to save tokens
        recent = self.conversation_history[-6:]
        if not recent:
            return ""

        lines = ["[Conversation context]"]
        for turn in recent:
            role = turn["role"].capitalize()
            content = turn["content"]
            if isinstance(content, dict):
                import json
                content = json.dumps(content)
            # More aggressive truncation - reduced from 500 to 250 chars
            if len(str(content)) > 250:
                content = str(content)[:250] + "..."
            lines.append(f"{role}: {content}")

        return "\n".join(lines)

    @staticmethod
    def _extract_text(result: Any) -> str:
        """
        Extract the final text response from a Strands AgentResult object or
        a plain string fallback.
        """
        # Strands AgentResult has a .message attribute (dict) in some versions
        if hasattr(result, "message"):
            msg = result.message
            if isinstance(msg, dict):
                content = msg.get("content", [])
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            return block["text"]
                        if isinstance(block, dict) and "text" in block:
                            return block["text"]
                if isinstance(content, str):
                    return content

        # Direct string conversion fallback
        text = str(result)
        return text if text and text != "None" else "I completed the request."


# ─────────────────────────────────────────────
# Singleton factory — one agent per process
# ─────────────────────────────────────────────
_agent_instance: "DeviceControlAgent | None" = None


def get_device_agent() -> DeviceControlAgent:
    """
    Return the shared DeviceControlAgent instance.

    Creates it on first call so that the Strands Agent is initialised once
    and conversation memory persists across requests within the same process.
    """
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = DeviceControlAgent()
    return _agent_instance