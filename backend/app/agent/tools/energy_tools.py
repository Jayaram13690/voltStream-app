"""
Energy Advisor Tools for the Energy Advisor Agent.

This module contains tool implementations for energy analysis and optimization
using Strands Agents SDK. These tools focus on electricity bill reduction,
energy consumption analysis, solar utilization, and budget monitoring.

Tools exposed to Nova Lite:
  - analyze_energy_usage_tool          -> analyze current energy consumption patterns
  - calculate_cost_analysis_tool       -> calculate energy costs and savings potential
  - solar_utilization_analysis_tool    -> analyze solar energy usage and optimization
  - budget_monitoring_tool             -> check budget compliance and warnings
"""

import logging
from typing import Any, Dict

from strands import tool

# from app.agent.device_data_access import get_devices
from app.agent.devices.backend_client import get_devices
from app.agent.energy_config import energy_simulator, EnergyState

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Helper Functions - No Caching for Fresh Data
# ─────────────────────────────────────────────
# Simple cache for data that changes infrequently
_tool_cache = {
    'billing': None,
    'analytics': {}
    # Note: devices and live_energy intentionally not cached for fresh data
}


def _get_current_devices():
    """Return the live device list."""
    # Always get fresh device data - no caching
    # This ensures we see any device state changes immediately
    return get_devices()


def _get_live_energy_data() -> EnergyState:
    """Get current live energy data using internal simulator."""
    # Use our self-contained energy simulator instead of external hub
    try:
        # Get fresh dynamic data from internal simulator
        return energy_simulator.tick()
    except Exception as e:
        logger.error(f"Energy simulation failed: {e}")
        # Fallback to current state if simulation fails
        return energy_simulator.get_state()


def _get_billing_data():
    """Get current billing summary (mock data)."""
    # Billing data changes infrequently, cache indefinitely
    if _tool_cache['billing'] is None:
        _tool_cache['billing'] = {
            "current_bill": 128.4,
            "predicted_bill": 156.2,
            "budget_limit": 180.0
        }
    return _tool_cache['billing']


def _get_analytics_data(period="daily"):
    """Get historical analytics data (mock data) with caching."""
    # Cache analytics data by period
    if period not in _tool_cache['analytics']:
        if period == "daily":
            points = [
                {"label": "00:00", "consumption": 1.2, "solar": 0.0},
                {"label": "04:00", "consumption": 0.9, "solar": 0.0},
                {"label": "08:00", "consumption": 2.4, "solar": 1.8},
                {"label": "12:00", "consumption": 9.1, "solar": 5.6},
                {"label": "16:00", "consumption": 8.8, "solar": 4.2},
                {"label": "20:00", "consumption": 3.6, "solar": 0.4},
            ]
        elif period == "weekly":
            points = [
                {"label": "Mon", "consumption": 23.4, "solar": 22.1},
                {"label": "Tue", "consumption": 23.3, "solar": 24.0},
                {"label": "Wed", "consumption": 24.1, "solar": 21.3},
                {"label": "Thu", "consumption": 28.8, "solar": 25.4},
                {"label": "Fri", "consumption": 23.2, "solar": 23.0},
                {"label": "Sat", "consumption": 26.9, "solar": 26.8},
                {"label": "Sun", "consumption": 28.2, "solar": 27.5},
            ]
        else:  # monthly
            points = [
                {"label": "Jan", "consumption": 610, "solar": 520},
                {"label": "Feb", "consumption": 698, "solar": 440},
                {"label": "Mar", "consumption": 805, "solar": 720},
                {"label": "Apr", "consumption": 790, "solar": 780},
                {"label": "May", "consumption": 801, "solar": 800},
            ]
        
        # Create a simple object with points attribute
        class MockAnalytics:
            def __init__(self, points):
                self.points = points
        
        _tool_cache['analytics'][period] = MockAnalytics(points)
    
    return _tool_cache['analytics'][period]


# ─────────────────────────────────────────────
# Energy Analysis Tools
# ─────────────────────────────────────────────
@tool
def analyze_energy_usage_tool() -> Dict[str, Any]:
    """
    Analyze current energy usage patterns across all devices and live systems.
    """

    logger.info("Tool Call: analyze_energy_usage()")

    # Get fresh data
    devices = _get_current_devices()
    live_data = _get_live_energy_data()

    # Total current consumption
    total_consumption = sum(
        device.get("power_usage", 0)
        for device in devices
    )
    
    active_devices = []
    inactive_devices = []

    for device in devices:
        if device.get("status") == "on":
            percentage = round((device.get("power_usage", 0)/ total_consumption* 100) if total_consumption > 0 else 0, 1)

            active_devices.append({
                "device_id": device["id"],
                "device_name": device["name"],
                "status": device["status"],
                "power_usage": device["power_usage"],
                "percentage_of_total": percentage
            })
        else:
            inactive_devices.append({
                "device_id": device["id"],
                "device_name": device["name"],
                "status": device["status"]
            })
    # Sort active devices by power usage
    active_devices.sort(
        key=lambda x: x["power_usage"],
        reverse=True
    )

    # Top 3 consuming devices
    peak_devices = [
        device["device_name"]
        for device in active_devices[:3]
    ]

    if total_consumption > 0:
        solar_ratio = min(
            1.0,
            live_data.solar_generation / total_consumption
        )
    else:
        solar_ratio = 1.0
    efficiency_score = round(
        solar_ratio * 100,
        1
    )
    
    if (
        live_data.solar_generation > 0
        and live_data.grid_usage > 0
        and total_consumption > 0
    ):
        savings_potential = min(50.0,(live_data.grid_usage / total_consumption * 100))
    else:
        savings_potential = 10.0

    observation = {
        "total_consumption": round(total_consumption, 2),
        "solar_generation": round(live_data.solar_generation,2),
        "grid_usage": round(live_data.grid_usage,2),
        "battery_level": live_data.battery,
        "active_devices": active_devices,
        "inactive_devices": inactive_devices,
        "active_device_count": len(active_devices),
        "inactive_device_count": len(inactive_devices),
        "peak_devices": peak_devices,
        "efficiency_score": efficiency_score,
        "savings_potential": round(savings_potential,1)
    }

    logger.info(f"Tool Result: {observation}")
    return observation

@tool
def calculate_cost_analysis_tool(period: str = "current") -> Dict[str, Any]:
    """
    Calculate energy costs and identify savings opportunities.
    
    Args:
        period: Time period for analysis (current, daily, weekly, monthly)
    
    Returns:
        {
          "period": str,
          "current_cost": float,              # Current estimated cost for period
          "potential_savings": float,         # Estimated potential savings ($)
          "cost_breakdown": {
            "grid_cost": float,               # Cost from grid usage
            "solar_savings": float,           # Savings from solar usage
            "device_costs": [                 # Cost by device category
              {
                "device_name": str,
                "estimated_cost": float,
                "potential_savings": float
              }
            ]
          },
          "recommendations": [str]            # Top 3 cost-saving recommendations
        }
    """
    logger.info(f"Tool Call: calculate_cost_analysis({period})")
    
    # Get billing and analytics data
    billing = _get_billing_data()
    analytics = _get_analytics_data(period) if period != "current" else None
    live_data = _get_live_energy_data()
    devices = _get_current_devices()
    
    # Use current bill for cost calculations, or estimate from analytics
    if period == "current":
        current_cost = billing["current_bill"]
        # Estimate daily cost (simple approximation)
        daily_cost = current_cost / 30  # Assume 30-day month
    else:
        # For historical periods, use analytics data to estimate cost
        analytics_data = _get_analytics_data(period)
        total_consumption = sum(point["consumption"] for point in analytics_data.points)
        # Simple cost estimation: $0.15 per kWh
        current_cost = round(total_consumption * 0.15, 2)
        daily_cost = current_cost / len(analytics_data.points) if len(analytics_data.points) > 0 else 0
    
    # Calculate grid cost vs solar savings
    grid_cost = round(live_data.grid_usage * 0.15 * 24, 2)  # $0.15/kWh * 24h estimate
    solar_savings = round(live_data.solar_generation * 0.15 * 24, 2)
    
    # Device cost breakdown
    device_costs = []
    for device in devices:
        if device["power_usage"] > 0:
            # Estimate daily cost for this device
            device_daily_cost = round(device["power_usage"] * 0.15 * 24, 2)
            # Estimate potential savings (50% if device can be optimized)
            device_name = device.get("name", "Unknown Device")
            potential_savings = round(device_daily_cost * 0.5, 2) if device_name not in ["Solar inverter"] else 0.0
            
            device_costs.append({
                "device_name": device_name,
                "estimated_cost": device_daily_cost,
                "potential_savings": potential_savings
            })
    
    # Sort by potential savings (highest first)
    device_costs.sort(key=lambda x: x["potential_savings"], reverse=True)
    
    # Calculate total potential savings
    total_potential_savings = sum(item["potential_savings"] for item in device_costs)
    
    # Generate recommendations based on data
    recommendations = []
    
    # Recommendation 1: High consumption devices
    high_consumption_devices = [d.get("name", "Unknown Device") for d in devices if d.get("power_usage", 0) > 1.0]
    if high_consumption_devices:
        recommendations.append(f"Reduce usage of high-consumption devices: {', '.join(high_consumption_devices)}")
    
    # Recommendation 2: Solar optimization
    if live_data.solar_generation > 0 and live_data.grid_usage > live_data.solar_generation:
        recommendations.append(f"Optimize solar usage - you're using more grid ({live_data.grid_usage}kW) than solar ({live_data.solar_generation}kW)")
    
    # Recommendation 3: Peak hours
    if period != "current":
        # Find peak consumption time from analytics
        peak_point = max(analytics.points, key=lambda x: x.consumption)
        recommendations.append(f"Shift usage away from peak hours around {peak_point.label}")
    
    # Add more recommendations if we have fewer than 3
    while len(recommendations) < 3:
        if len(recommendations) == 0:
            recommendations.append("Consider upgrading to energy-efficient appliances")
        elif len(recommendations) == 1:
            recommendations.append("Use smart scheduling to run devices during off-peak hours")
        elif len(recommendations) == 2:
            recommendations.append("Monitor and reduce standby power consumption")
        else:
            break
    
    observation = {
        "period": period,
        "current_cost": round(current_cost, 2),
        "potential_savings": round(total_potential_savings * 30, 2),  # Monthly estimate
        "cost_breakdown": {
            "grid_cost": grid_cost,
            "solar_savings": solar_savings,
            "device_costs": device_costs
        },
        "recommendations": recommendations
    }
    
    logger.info(f"Tool Result: {observation}")
    return observation


@tool
def solar_utilization_analysis_tool() -> Dict[str, Any]:
    """
    Analyze solar energy usage and provide optimization recommendations.
    
    Returns:
        {
          "solar_generation": float,          # Current solar generation (kW)
          "solar_utilization": float,          # Percentage of solar energy used directly (%)
          "battery_status": {
            "level": int,                      # Current battery percentage
            "capacity": float,                 # Estimated capacity (kWh)
            "potential_storage": float         # Potential additional storage (kWh)
          },
          "grid_dependency": float,           # Percentage of energy from grid (%)
          "optimization_opportunities": [str], # Solar optimization recommendations
          "savings_estimate": float           # Estimated monthly savings from optimization ($)
        }
    """
    logger.info("Tool Call: solar_utilization_analysis()")
    
    live_data = _get_live_energy_data()
    devices = _get_current_devices()
    
    # Calculate total consumption
    total_consumption = sum(device["power_usage"] for device in devices)
    
    # Solar utilization calculation
    if total_consumption > 0:
        solar_utilization = min(100.0, (live_data.solar_generation / total_consumption) * 100)
    else:
        solar_utilization = 0.0
    
    # Grid dependency
    if total_consumption > 0:
        grid_dependency = min(100.0, (live_data.grid_usage / total_consumption) * 100)
    else:
        grid_dependency = 0.0
    
    # Battery analysis (simple estimates)
    battery_capacity = round(live_data.battery * 0.05, 2)  # Assume 5kWh total capacity
    potential_storage = round((100 - live_data.battery) * 0.05, 2)
    
    # Optimization opportunities
    opportunities = []
    
    # Opportunity 1: Low solar utilization
    if solar_utilization < 50 and live_data.solar_generation > 0:
        opportunities.append(f"Increase direct solar usage - only {solar_utilization}% of solar energy is being used directly")
    
    # Opportunity 2: High grid dependency
    if grid_dependency > 30:
        opportunities.append(f"Reduce grid dependency - {grid_dependency}% of energy comes from the grid")
    
    # Opportunity 3: Battery optimization
    if live_data.battery < 80 and live_data.solar_generation > live_data.grid_usage:
        opportunities.append(f"Charge battery during peak solar - battery at {live_data.battery}% with excess solar available")
    
    # Opportunity 4: Device scheduling
    solar_peak_devices = [d.get("name", "Unknown Device") for d in devices if d.get("power_usage", 0) > 0.5]
    if solar_peak_devices:
        opportunities.append(f"Schedule high-consumption devices during solar peak: {', '.join(solar_peak_devices)}")
    
    # Savings estimate (rule-based)
    if grid_dependency > 20:
        # Estimate $10 per 10% reduction in grid dependency
        savings_estimate = round((grid_dependency / 10) * 10, 2)
    else:
        savings_estimate = 5.0  # Minimum estimate
    
    observation = {
        "solar_generation": round(live_data.solar_generation, 2),
        "solar_utilization": round(solar_utilization, 1),
        "battery_status": {
            "level": live_data.battery,
            "capacity": battery_capacity,
            "potential_storage": potential_storage
        },
        "grid_dependency": round(grid_dependency, 1),
        "optimization_opportunities": opportunities,
        "savings_estimate": savings_estimate
    }
    
    logger.info(f"Tool Result: {observation}")
    return observation


@tool
def budget_monitoring_tool() -> Dict[str, Any]:
    """
    Monitor energy spending against budget limits and provide alerts.
    
    Returns:
        {
          "current_bill": float,              # Current bill amount ($)
          "predicted_bill": float,             # Predicted end-of-month bill ($)
          "budget_limit": float,              # Monthly budget limit ($)
          "budget_utilization": float,        # Percentage of budget used (%)
          "status": str,                       # Status: safe, warning, critical
          "days_remaining": int,               # Estimated days remaining in billing cycle
          "daily_average": float,              # Current daily average spending ($)
          "projected_overage": float,         # Projected overage if no changes ($)
          "recommendations": [str]             # Budget management recommendations
        }
    """
    logger.info("Tool Call: budget_monitoring()")
    
    billing = _get_billing_data()
    
    # Calculate budget utilization
    budget_utilization = min(100.0, (billing["current_bill"] / billing["budget_limit"] * 100) if billing["budget_limit"] > 0 else 0)
    
    # Determine status
    if budget_utilization < 60:
        status = "safe"
    elif budget_utilization < 85:
        status = "warning"
    else:
        status = "critical"
    
    # Estimate days remaining (simple approximation)
    days_remaining = 30 - int((billing["current_bill"] / billing["predicted_bill"]) * 30) if billing["predicted_bill"] > 0 else 15
    days_remaining = max(1, min(30, days_remaining))  # Clamp between 1-30
    
    # Calculate daily average
    daily_average = round(billing["current_bill"] / (30 - days_remaining), 2) if (30 - days_remaining) > 0 else 0
    
    # Projected overage
    if status == "critical":
        projected_overage = round(billing["predicted_bill"] - billing["budget_limit"], 2)
    else:
        projected_overage = 0.0
    
    # Generate recommendations
    recommendations = []
    
    if status == "critical":
        recommendations.append(f"Immediate action needed - you're projected to exceed budget by ${projected_overage}")
        recommendations.append("Reduce usage of high-consumption devices immediately")
    elif status == "warning":
        recommendations.append(f"Caution - you've used {budget_utilization}% of your budget")
        recommendations.append("Consider implementing energy-saving measures")
    else:
        recommendations.append("Budget usage is within safe limits")
        recommendations.append("Continue monitoring to maintain good usage patterns")
    
    # Add specific recommendations
    if daily_average > (billing["budget_limit"] / 30):
        target_daily = round(billing["budget_limit"] / 30, 2)
        recommendations.append(f"Reduce daily spending from ${daily_average} to ${target_daily}/day")
    
    observation = {
        "current_bill": billing["current_bill"],
        "predicted_bill": billing["predicted_bill"],
        "budget_limit": billing["budget_limit"],
        "budget_utilization": round(budget_utilization, 1),
        "status": status,
        "days_remaining": days_remaining,
        "daily_average": daily_average,
        "projected_overage": projected_overage,
        "recommendations": recommendations
    }
    
    logger.info(f"Tool Result: {observation}")
    return observation