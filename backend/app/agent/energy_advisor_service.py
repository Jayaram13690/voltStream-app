"""
Energy Advisor Agent Service — Production-Quality Implementation.

Powered by:
  * Amazon Bedrock Nova 2 Lite (us.amazon.nova-2-lite-v1:0)
  * Strands Agents SDK 0.3.0
  * ReAct Pattern (Reason -> Tool Call -> Observe -> Reason -> ... -> Respond)

Focus Areas:
  - Electricity bill reduction advice
  - Energy consumption analysis
  - Solar utilization recommendations
  - Budget monitoring and alerts

Decision-making handled by Nova Lite:
  - Energy usage pattern analysis
  - Cost-saving opportunity identification
  - Solar optimization strategies
  - Budget compliance monitoring
  - Personalized recommendation generation
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

from app.agent.tools.energy_tools import (
    analyze_energy_usage_tool,
    calculate_cost_analysis_tool,
    solar_utilization_analysis_tool,
    budget_monitoring_tool,
)
# from app.core.config import get_settings
from app.agent.agent_blackboard import get_blackboard


# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# System prompt — drives energy advisory behavior
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """You are an Energy Advisor Agent. 
Use tool data only. Analyze energy, cost, solar, and budget metrics. 
Recommend bill-reduction actions, prioritize by savings impact, quantify savings in dollars, provide concise actionable advice, and avoid unsupported recommendations.
## Tools
- analyze_energy_usage_tool(): Current energy consumption breakdown
- calculate_cost_analysis_tool(period): Cost/savings analysis (period: current, daily, weekly, monthly)
- solar_utilization_analysis_tool(): Solar usage optimization analysis
- budget_monitoring_tool(): Budget compliance and alerts
## Critical
- Never make recommendations without supporting tool data.
- Provide Summarised respose within 50 words.
"""
# SYSTEM_PROMPT = """You are an Energy Advisor Agent providing electricity bill reduction advice, energy analysis, solar optimization, and budget monitoring.

# ## Rules
# 1. Always quantify savings in dollars
# 2. Prioritize recommendations by financial impact
# 3. Use simple, actionable language
# 4. Base all advice on tool data
# 5. Check budget status for context

# ## Tools
# - analyze_energy_usage_tool(): Current energy consumption breakdown
# - calculate_cost_analysis_tool(period): Cost/savings analysis (period: current, daily, weekly, monthly)
# - solar_utilization_analysis_tool(): Solar usage optimization analysis
# - budget_monitoring_tool(): Budget compliance and alerts

# ## Workflow
# 1. analyze_energy_usage_tool() - Understand current usage
# 2. calculate_cost_analysis_tool() - Identify savings opportunities
# 3. solar_utilization_analysis_tool() - Optimize solar usage
# 4. budget_monitoring_tool() - Check budget status
# 5. Synthesize into prioritized recommendations

# ## Response Requirements
# - Quantify savings (e.g., "$25/month")
# - Prioritize by impact (highest first)
# - Provide specific action steps
# - Keep responses concise (under 100 words)
# - Frame as opportunities for savings

# ## Key Assumptions
# - Electricity rate: $0.15/kWh
# - Solar value: $0.15/kWh avoided cost
# - Peak hours: 4 PM - 8 PM
# - High-consumption devices: Heat pump, EV charger, HVAC, Water heater

# ## Critical
# Never make recommendations without supporting tool data.
# """


# ─────────────────────────────────────────────
# Response schema (for API layer)
# ─────────────────────────────────────────────
class EnergyAnalysisResponse(BaseModel):
    """Response model for energy analysis"""
    analysis_type: str
    findings: Dict[str, Any]
    recommendations: List[str]


# ─────────────────────────────────────────────
# Energy Advisor Agent
# ─────────────────────────────────────────────
class EnergyAdvisorAgent:
    """
    Production-quality Energy Advisor Agent.

    Nova Lite drives all energy analysis and recommendation generation through
    Strands' native tool-calling loop. Python only handles:
      - SDK initialization
      - Conversation memory management
      - Error handling
    """

    def __init__(self):
        # settings = get_settings()
        self.bedrock_model_id = "global.amazon.nova-2-lite-v1:0"
        self.aws_region = "us-east-1"

        self.model_id = self.bedrock_model_id  # us.amazon.nova-2-lite-v1:0
        
        # Initialize blackboard for multi-agent coordination
        self.blackboard = get_blackboard()

        # Extended read timeout for multi-step energy analysis
        botocore_cfg = BotoCoreConfig(
            read_timeout=300,
            connect_timeout=30,
            retries={"max_attempts": 3},
        )

        # Use BedrockModel with Strands 0.3.0 API
        # streaming=False for stable multi-turn tool-use flows
        # max_tokens=512 for concise, focused responses
        model = BedrockModel(
            model_id=self.model_id,
            region_name=self.aws_region,
            boto_client_config=botocore_cfg,
            temperature=0.1,  # Reduced from 0.3 for more deterministic responses
            top_p=0.8,       # Reduced from 0.9 for more focused responses
            max_tokens=300,   # Reduced from 512 to limit response length
            streaming=False,
        )

        # Build the Strands Agent with energy-specific tools
        self.agent = Agent(
            model=model,
            system_prompt=SYSTEM_PROMPT,
            tools=[
                analyze_energy_usage_tool,
                calculate_cost_analysis_tool,
                solar_utilization_analysis_tool,
                budget_monitoring_tool,
            ],
        )

        # Conversation memory — persisted across requests within one process
        self.conversation_history: List[Dict[str, Any]] = []

        logger.info(
            "EnergyAdvisorAgent ready | model=%s | tools=[analyze_energy_usage, "
            "calculate_cost_analysis, solar_utilization_analysis, budget_monitoring]",
            self.model_id,
        )

    # ──────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────

    def process_request(self, user_request: str) -> str:
        """
        Process an energy advisory request using ReAct pattern.

        The Strands Agent handles the full analysis workflow:
          Reason -> Select tool -> Execute -> Observe -> Reason -> ... -> Respond

        Args:
            user_request: Natural language energy advisory request.

        Returns:
            Natural language response with analysis and recommendations.
        """
        logger.info("Energy Advisor Request: %s", user_request)

        # Build context-enriched message with recent conversation history
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

        # Let Strands / Nova Lite drive the full analysis workflow
        try:
            result = self.agent(full_message)
            final_response = self._extract_text(result)

        except (ClientError, BotoCoreError) as exc:
            logger.error("Bedrock error: %s", exc)
            final_response = (
                "I encountered an AWS service error while analyzing your energy usage. "
                "Please check your credentials and try again."
            )
        except Exception as exc:
            logger.error("Agent error: %s", exc, exc_info=True)
            final_response = (
                "I encountered an unexpected error while analyzing your energy data. "
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

        logger.info("Energy Advisor Response: %s", final_response)
        
        # Update blackboard with energy analysis results
        self.blackboard.add_action({
            "type": "energy_agent_response",
            "query": user_request,
            "response": final_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Also check if we should update energy metrics based on the response
        # This is a simplified approach - in production you'd parse the response
        if "savings" in final_response.lower() or "cost" in final_response.lower():
            self.blackboard.update_energy_metrics({
                "last_analysis": final_response,
                "analysis_timestamp": datetime.now().isoformat()
            })
        
        return final_response

    def reset_memory(self) -> None:
        """Clear conversation history (useful between sessions)."""
        self.conversation_history.clear()
        logger.info("Energy advisor conversation history cleared.")

    # ──────────────────────────────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────────────────────────────

    def _format_history_context(self) -> str:
        """
        Render the last N conversation turns as a compact text block so Nova
        Lite can use it for context and continuity in multi-step analysis.
        """
        # Reduced from 8 to 5 turns to save tokens
        recent = self.conversation_history[-5:]
        if not recent:
            return ""

        lines = ["[Previous conversation context]"]
        for turn in recent:
            role = turn["role"].capitalize()
            content = turn["content"]
            if isinstance(content, dict):
                import json
                content = json.dumps(content)
            # More aggressive truncation - reduced from 400 to 200 chars
            if len(str(content)) > 200:
                content = str(content)[:200] + "..."
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
        return text if text and text != "None" else "Energy analysis completed."


# ─────────────────────────────────────────────
# Singleton factory — one agent per process
# ─────────────────────────────────────────────
_energy_advisor_instance: "EnergyAdvisorAgent | None" = None


def get_energy_advisor() -> EnergyAdvisorAgent:
    """
    Return the shared EnergyAdvisorAgent instance.

    Creates it on first call so that the Strands Agent is initialised once
    and conversation memory persists across requests within the same process.
    """
    global _energy_advisor_instance
    if _energy_advisor_instance is None:
        _energy_advisor_instance = EnergyAdvisorAgent()
    return _energy_advisor_instance