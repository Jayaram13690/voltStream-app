"""
Internal configuration for Energy Advisor Agent.
Self-contained settings to eliminate external dependencies.
"""

from dataclasses import dataclass
import random
from datetime import datetime


@dataclass
class EnergyState:
    """Represents current energy system state"""
    grid_usage: float        # Current grid power usage in kW
    solar_generation: float  # Current solar power generation in kW
    battery: int             # Current battery percentage (0-100)
    savings: float           # Current savings in dollars
    timestamp: float         # Last update timestamp


class EnergySimulator:
    """Self-contained energy simulation that replaces external LiveEnergyHub"""
    
    def __init__(self):
        """Initialize with realistic starting values"""
        self.state = EnergyState(
            grid_usage=4.2,
            solar_generation=6.8,
            battery=82,
            savings=2340.0,
            timestamp=datetime.now().timestamp()
        )
        self._last_tick = datetime.now().timestamp()

    def tick(self) -> EnergyState:
        """
        Generate new realistic energy data with natural fluctuations.
        Simulates real-world energy system variability.
        """
        current_time = datetime.now().timestamp()
        time_elapsed = current_time - self._last_tick
        self._last_tick = current_time
        
        # Base values from current state
        base_grid = self.state.grid_usage
        base_solar = self.state.solar_generation
        base_battery = self.state.battery
        base_savings = self.state.savings
        
        # Apply realistic fluctuations based on time elapsed
        # Grid usage: ±0.35kW with some random walk
        grid_change = random.uniform(-0.35, 0.35) * min(time_elapsed / 5.0, 1.0)
        new_grid = max(0.1, base_grid + grid_change)  # Never below 0.1kW
        
        # Solar generation: ±0.6kW with time-of-day pattern
        # More variation during "daytime" hours (6AM-6PM)
        hour = datetime.now().hour
        is_daytime = 6 <= hour < 18
        solar_variation = 0.6 if is_daytime else 0.3
        solar_change = random.uniform(-solar_variation, solar_variation) * min(time_elapsed / 3.0, 1.0)
        new_solar = max(0, base_solar + solar_change)
        
        # Battery: ±1% with constraints, influenced by solar/grid balance
        battery_change = random.randint(-1, 1)
        if new_solar > new_grid and base_battery < 95:  # Excess solar -> charge
            battery_change = max(1, battery_change)
        elif new_grid > new_solar and base_battery > 10:  # High grid usage -> discharge
            battery_change = min(-1, battery_change)
        new_battery = max(0, min(100, base_battery + battery_change))
        
        # Savings: ±$5-$12 based on energy balance
        energy_balance = new_solar - new_grid
        savings_change = random.uniform(5, 12) if energy_balance > 0 else random.uniform(-12, -5)
        new_savings = max(0, base_savings + savings_change * min(time_elapsed / 10.0, 1.0))
        
        # Update state
        self.state = EnergyState(
            grid_usage=round(new_grid, 2),
            solar_generation=round(new_solar, 2),
            battery=int(new_battery),
            savings=round(new_savings, 2),
            timestamp=current_time
        )
        
        return self.state
    
    def get_state(self) -> EnergyState:
        """Get current state (used as fallback if tick fails)"""
        return self.state


# Singleton instance for the energy advisor
energy_simulator = EnergySimulator()