"""
Device Control Agent Service using Strands Agents SDK and Amazon Bedrock Nova Lite.

This service implements a Single-Agent architecture using the ReAct (Reason + Act) pattern
for controlling devices through natural language requests.

Uses Strands Agents SDK version 0.3.0 with proper Agent and tool integration.
"""

import json
import logging
from typing import Dict, Any, List, Callable

from datetime import datetime

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from pydantic import BaseModel

from app.core.config import get_settings
from app.schemas.device import DeviceRead, DeviceUpdate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Import device data from shared access module
from app.services.device_data_access import get_devices, get_default_power

# Get device data access functions (don't store local copies)
_DEFAULT_POWER = get_default_power()

# Helper function to get fresh device data each time
def _get_current_devices():
    return get_devices()


class DeviceStatusResponse(BaseModel):
    """Response model for device status"""
    device_id: int
    device_name: str
    status: str


class DeviceControlAgent:
    """
    Device Control Agent using Amazon Bedrock Nova Lite.
    
    Implements ReAct pattern: Reason → Tool Call → Observation → Reason → Final Response
    """
    
    def __init__(self):
        """Initialize the Device Control Agent with Strands SDK and Bedrock Nova Lite."""
        settings = get_settings()
        
        # Initialize Bedrock client
        self.bedrock_client = boto3.client(
            service_name="bedrock-runtime",
            region_name=settings.aws_region
        )
        
        self.model_id = settings.bedrock_model_id
        self.conversation_history = []
        
        # Import Strands SDK components
        from strands import Agent, tool
        
        # Import and register tools using Strands SDK
        from app.agent.tools.device_tools import (
            list_devices_tool,
            get_device_status_tool,
            set_device_status_tool
        )
        
        # Create Strands Agent with tools
        self.strands_agent = Agent(
            name="DeviceControlAgent",
            description="Agent for controlling devices through natural language",
            tools=[list_devices_tool, get_device_status_tool, set_device_status_tool]
        )
        
        # Initialize tools dictionary for direct access
        self.tools = {
            "list_devices": list_devices_tool,
            "get_device_status": get_device_status_tool,
            "set_device_status": set_device_status_tool
        }
        
        logger.info("Device Control Agent initialized with Strands SDK and Bedrock Nova Lite")
    
    def _generate_bedrock_response(self, prompt: str) -> str:
        """Generate response using Amazon Bedrock Nova Lite"""
        try:
            request_body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "inferenceConfig": {
                    "max_new_tokens": 500,
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body),
                contentType="application/json",
                accept="application/json"
            )
            
            result = json.loads(response["body"].read().decode("utf-8"))
            
            # Extract the text content
            try:
                return result["output"]["message"]["content"][0]["text"]
            except (KeyError, IndexError):
                if "completion" in result:
                    return result["completion"]
                elif "outputText" in result:
                    return result["outputText"]
                else:
                    logger.warning(f"Unexpected response format: {result}")
                    return str(result)
                    
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Bedrock error: {str(e)}")
            raise Exception(f"Failed to generate response: {str(e)}")
    
    def _simple_intent_analysis(self, user_request: str) -> Dict[str, Any]:
        """Simple intent analysis for device control requests"""
        request_lower = user_request.lower()
        
        # Extract device information
        device_info = {}
        
        # Check for specific device names
        device_names = {
            "dishwasher": 101,
            "fan": 102,
            "heat pump": 1,
            "ev charger": 2,
            "kitchen": 3,
            "hvac": 4,
            "water heater": 5,
            "solar inverter": 6
        }
        
        # Find mentioned device
        for name, device_id in device_names.items():
            if name in request_lower:
                device_info["device_name"] = name
                device_info["device_id"] = device_id
                break
        
        # Extract device ID if mentioned (e.g., "device 101")
        if not device_info.get("device_id"):
            import re
            device_id_match = re.search(r'device\s+(\d+)', request_lower)
            if device_id_match:
                device_id = int(device_id_match.group(1))
                # Get fresh device data to check if device exists
                current_devices = _get_current_devices()
                device = next((d for d in current_devices if d["id"] == device_id), None)
                if device:
                    device_info["device_id"] = device_id
                    device_info["device_name"] = device["name"]
        
        # Determine intent
        intent = "unknown"
        
        if any(word in request_lower for word in ["status", "check", "what is"]):
            intent = "get_status"
        elif any(word in request_lower for word in ["turn off", "off", "disable"]):
            intent = "turn_off"
        elif any(word in request_lower for word in ["turn on", "on", "enable"]):
            intent = "turn_on"
        elif any(word in request_lower for word in ["list", "all", "show"]):
            intent = "list_devices"
        
        return {
            "intent": intent,
            "device_info": device_info,
            "request": user_request
        }
    
    def _build_agent_prompt(self, user_request: str) -> str:
        """Build the prompt for the agent with context and instructions"""
        return f"""
        You are a Device Control Agent that can understand natural language requests 
        and control devices using available tools.

        Current conversation history:
        {json.dumps(self.conversation_history)}

        User request: "{user_request}"

        Available tools:
        1. list_devices() - Returns all available devices
        2. get_device_status(device_id) - Returns device id, device name, and current status
        3. set_device_status(device_id, state) - Updates device status

        Instructions:
        1. Analyze the user request to understand their intent
        2. Determine which tool(s) to use
        3. Call the appropriate tool with correct arguments
        4. Use the tool observations to determine next actions
        5. Provide a final natural language response to the user

        Follow the ReAct pattern:
        Reason → Tool Call → Observation → Reason → Final Response

        Respond with your reasoning and tool calls in JSON format:
        {{
            "thought": "Your reasoning about what to do",
            "action": "tool_name",
            "action_input": {{...}}
        }}

        When you have enough information to answer the user, respond with:
        {{
            "thought": "Final reasoning",
            "response": "Your natural language response to the user"
        }}
        """
    
    def process_request(self, user_request: str) -> str:
        """
        Process a user request using the ReAct pattern.
        
        Args:
            user_request: Natural language request from user
            
        Returns:
            Natural language response to the user
        """
        logger.info(f"User Request: {user_request}")
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_request,
            "timestamp": datetime.now().isoformat()
        })
        
        # Simple intent analysis (fallback if Bedrock is not available)
        intent_analysis = self._simple_intent_analysis(user_request)
        
        # Process based on intent
        if intent_analysis["intent"] == "list_devices":
            logger.info("Selected Tool: list_devices")
            observation = self.tools["list_devices"]()
            logger.info(f"Tool Result: {observation}")
            
            devices = observation["devices"]
            device_statuses = [f"{d['device_name']} ({d['status']})" for d in devices]
            final_response = f"Here are all available devices: {', '.join(device_statuses)}"
            
        elif intent_analysis["intent"] == "get_status":
            if intent_analysis["device_info"]:
                device_id = intent_analysis["device_info"]["device_id"]
                logger.info(f"Selected Tool: get_device_status({device_id})")
                # Get fresh device data before calling tool
                current_devices = _get_current_devices()
                observation = self.tools["get_device_status"](device_id)
                logger.info(f"Tool Result: {observation}")
                
                if "error" in observation:
                    final_response = observation["error"]
                else:
                    final_response = f"The {observation['device_name']} is currently {observation['status']}."
            else:
                final_response = "I couldn't determine which device you're asking about. Please specify a device name or ID."
                
        elif intent_analysis["intent"] in ["turn_off", "turn_on"]:
            if intent_analysis["device_info"]:
                device_id = intent_analysis["device_info"]["device_id"]
                state = "off" if intent_analysis["intent"] == "turn_off" else "on"
                
                # First check current status
                logger.info(f"Selected Tool: get_device_status({device_id})")
                status_observation = self.tools["get_device_status"](device_id)
                logger.info(f"Tool Result: {status_observation}")
                
                if "error" in status_observation:
                    final_response = status_observation["error"]
                else:
                    # Now update status
                    logger.info(f"Selected Tool: set_device_status({device_id}, {state})")
                    update_observation = self.tools["set_device_status"](device_id, state)
                    logger.info(f"Tool Result: {update_observation}")
                    
                    if update_observation["success"]:
                        final_response = f"The {status_observation['device_name']} was {status_observation['status']} and has now been turned {state}."
                    else:
                        final_response = update_observation["message"]
            else:
                final_response = "I couldn't determine which device you want to control. Please specify a device name or ID."
                
        else:
            # Use Bedrock for more complex requests
            try:
                prompt = self._build_agent_prompt(user_request)
                response_text = self._generate_bedrock_response(prompt)
                
                try:
                    agent_response = json.loads(response_text)
                except json.JSONDecodeError:
                    final_response = response_text
                
                # Process agent's reasoning and tool calls
                max_iterations = 3
                iteration = 0
                
                while iteration < max_iterations:
                    iteration += 1
                    
                    if "response" in agent_response:
                        # Final response to user
                        final_response = agent_response["response"]
                        break
                    
                    if "action" in agent_response:
                        # Tool call
                        action_name = agent_response["action"]
                        action_input = agent_response.get("action_input", {})
                        
                        logger.info(f"Selected Tool: {action_name}")
                        logger.info(f"Tool Arguments: {action_input}")
                        
                        # Execute the tool
                        try:
                            if action_name in self.tools:
                                observation = self.tools[action_name](**action_input)
                            else:
                                observation = {"error": f"Unknown tool: {action_name}"}
                            
                            logger.info(f"Observation: {observation}")
                            
                            # Add observation to conversation history
                            self.conversation_history.append({
                                "role": "observation",
                                "content": observation,
                                "timestamp": datetime.now().isoformat()
                            })
                            
                            # Generate next reasoning step
                            followup_prompt = f"""
                            Previous thought: {agent_response.get('thought', '')}
                            Tool call: {action_name}({action_input})
                            Observation: {observation}

                            What should you do next? Continue with the ReAct pattern.
                            """
                            
                            response_text = self._generate_bedrock_response(followup_prompt)
                            
                            try:
                                agent_response = json.loads(response_text)
                            except json.JSONDecodeError:
                                final_response = response_text
                                break
                                
                        except Exception as e:
                            logger.error(f"Tool execution error: {str(e)}")
                            final_response = f"Error executing tool {action_name}: {str(e)}"
                            break
                    else:
                        final_response = "I'm sorry, I couldn't determine what action to take."
                        break
                
                if final_response is None:
                    final_response = "I couldn't complete your request after multiple attempts."
                    
            except Exception as e:
                logger.error(f"Bedrock processing error: {str(e)}")
                final_response = f"I'm sorry, I encountered an error processing your request: {str(e)}"
        
        # Add final response to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": final_response,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Final Response: {final_response}")
        return final_response


def get_device_agent() -> DeviceControlAgent:
    """
    Factory function to create and return a DeviceControlAgent instance.
    
    Returns:
        DeviceControlAgent: Initialized device control agent
    """
    return DeviceControlAgent()