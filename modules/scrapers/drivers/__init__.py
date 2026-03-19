"""
Browser Drivers Module.

Exports driver implementations for browser automation abstraction layer.
Provides a unified interface for switching between Selenium and Playwright.
"""

from .driver_interface import DriverInterface
from .selenium_driver import SeleniumDriver
from .playwright_driver import PlaywrightDriver
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
    "PlaywrightDriver",
    "random_delay",
    "type_humanlike",
    "scroll_natural",
    "get_random_user_agent",
    "simulate_reading_time",
]


def create_driver(driver_type: str = "playwright", **kwargs):
    """
    Factory function to create a driver instance.
    
    Args:
        driver_type: Type of driver ("selenium" or "playwright").
        **kwargs: Additional arguments passed to the driver constructor.
        
    Returns:
        DriverInterface implementation.
        
    Raises:
        ValueError: If driver_type is not recognized.
    """
    driver_type = driver_type.lower()
    
    if driver_type == "selenium":
        return SeleniumDriver(**kwargs)
    elif driver_type == "playwright":
        return PlaywrightDriver(**kwargs)
    else:
        raise ValueError(f"Unknown driver type: {driver_type}. Use 'selenium' or 'playwright'.")