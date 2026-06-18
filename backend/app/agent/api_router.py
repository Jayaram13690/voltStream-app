"""
API Router Integration for Multi-Agent System.

This module provides the FastAPI router that can be imported and included
in the main API setup while keeping all multi-agent code within the /agent folder.
"""

from fastapi import APIRouter
from app.agent.multi_agent_api import router as multi_agent_router

# Create a router that includes the multi-agent endpoint
def get_multi_agent_router() -> APIRouter:
    """
    Get the multi-agent router for integration with main API.
    
    Returns:
        APIRouter with multi-agent endpoint
    """
    return multi_agent_router