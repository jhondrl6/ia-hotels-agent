"""
Browser Drivers Module.

Exports driver implementation for browser automation abstraction layer.
Selenium es el driver activo para este proyecto.
"""

from .driver_interface import DriverInterface
from .selenium_driver import SeleniumDriver
from .humanized import (
    random_delay,
    type_humanlike,
    scroll_natural,
    get_random_user_agent,
    simulate_reading_time,
)

__all__ = [
    "DriverInterface",
    "SeleniumDriver",
    "random_delay",
    "type_humanlike",
    "scroll_natural",
    "get_random_user_agent",
    "simulate_reading_time",
]


def create_driver(driver_type: str = "selenium", **kwargs):
    """
    Factory function to create a driver instance.
    
    Args:
        driver_type: Type of driver (must be "selenium").
        **kwargs: Additional arguments passed to the driver constructor.
        
    Returns:
        SeleniumDriver instance.
        
    Raises:
        ValueError: If driver_type is not recognized.
    """
    driver_type = driver_type.lower()
    
    if driver_type == "selenium":
        return SeleniumDriver(**kwargs)
    else:
        raise ValueError(f"Unknown driver type: {driver_type}. Use 'selenium'.")