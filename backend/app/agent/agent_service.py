"""
Device Control Agent Service — 90% Agentic Architecture.

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
from app.core.config import get_settings

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# System prompt — drives 90% agentic behavior
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """You are an intelligent Device Control Agent with full autonomy over smart-home devices.

## Your Responsibilities
You MUST autonomously decide:
1. Which tools to call — never ask the user to confirm tool usage.
2. In what order — plan a multi-step workflow before acting.
3. Which devices are targeted — always call list_devices first if you are unsure of a device's id, even if the user gives a name.
4. When to use bulk vs single tools — use update_multiple_devices when two or more devices need to change.
5. How to resolve pronouns — use the conversation history to map "it", "them", "that device", "the last one", etc.

## Available Tools
- list_devices: Discover all devices, map names to ids, check current statuses
- get_device_status: Inspect one specific device (when you already know its id)
- set_device_status: Change state of exactly ONE device
- update_multiple_devices: Change state of TWO OR MORE devices in a single call

## Agentic ReAct Loop
Follow this loop until the task is complete:
  Thought -> Tool Selection -> Tool Call -> Observation -> Thought -> ... -> Final Response

## Device State Values
ALL devices use only "on" or "off" — there is no "online" or "offline" state.
This applies to every device including Dishwasher and Fan.

## Multi-Step Example
User: "Turn off all devices that are on"
  Step 1 -> list_devices()             (discover which are on)
  Step 2 -> update_multiple_devices()  (bulk set them off)
  Step 3 -> Respond with a clear summary of what changed.

## Context / Memory Example
User: "Turn off Heat pump"        -> act
User: "What was its status?"      -> resolve "its" = Heat pump from history, call get_device_status or recall from prior observation

## Response Style
- Be concise but complete.
- Always confirm WHAT changed and the NEW state.
- If a device was already in the requested state, mention it.
- On errors, explain what went wrong and what you tried.

## CRITICAL RULE
Never hard-code device ids in your reasoning. Always verify via list_devices when unsure.
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
        settings = get_settings()

        self.model_id = settings.bedrock_model_id  # us.amazon.nova-2-lite-v1:0

        # Extended read timeout for multi-step ReAct reasoning chains
        botocore_cfg = BotoCoreConfig(
            read_timeout=300,
            connect_timeout=30,
            retries={"max_attempts": 3},
        )

        # Use BedrockModel with the correct Strands 0.3.0 API
        # streaming=False -> uses converse (not converse_stream) which is
        # stable for multi-turn tool-use flows on Nova 2 Lite.
        # max_tokens=512 reduces throttling on the final synthesis turn.
        model = BedrockModel(
            model_id=self.model_id,
            region_name=settings.aws_region,
            boto_client_config=botocore_cfg,
            temperature=0.3,
            top_p=0.9,
            max_tokens=512,
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
        # Only include the last 10 turns to avoid context bloat
        recent = self.conversation_history[-10:]
        if not recent:
            return ""

        lines = ["[Conversation history - use this to resolve pronouns and references]"]
        for turn in recent:
            role = turn["role"].capitalize()
            content = turn["content"]
            if isinstance(content, dict):
                import json
                content = json.dumps(content)
            # Truncate very long observations
            if len(str(content)) > 500:
                content = str(content)[:500] + "..."
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