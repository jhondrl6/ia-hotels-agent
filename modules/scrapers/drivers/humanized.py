"""
Humanized Behavior Utilities for Browser Automation.

Provides utilities for simulating human-like interactions with web pages,
helping to avoid bot detection and making automated browsing more natural.
"""

import random
import time
import logging
from typing import Any, Union

logger = logging.getLogger(__name__)

DEFAULT_MIN_DELAY = 0.5
DEFAULT_MAX_DELAY = 2.0
TYPING_MIN_DELAY = 0.05
TYPING_MAX_DELAY = 0.15
SCROLL_PAUSE_MIN = 0.3
SCROLL_PAUSE_MAX = 0.8


def random_delay(min_sec: float = DEFAULT_MIN_DELAY, max_sec: float = DEFAULT_MAX_DELAY) -> None:
    """
    Sleep for a random duration between min_sec and max_sec.
    
    Args:
        min_sec: Minimum delay in seconds.
        max_sec: Maximum delay in seconds.
    """
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


def type_humanlike(element: Any, text: str, min_delay: float = TYPING_MIN_DELAY, max_delay: float = TYPING_MAX_DELAY) -> None:
    """
    Type text into an element with human-like timing variation.
    
    Args:
        element: The input element to type into.
        text: The text to type.
        min_delay: Minimum delay between keystrokes in seconds.
        max_delay: Maximum delay between keystrokes in seconds.
    """
    if element is None:
        logger.warning("Cannot type into None element")
        return
    
    try:
        for char in text:
            element.send_keys(char)
            delay = random.uniform(min_delay, max_delay)
            time.sleep(delay)
    except Exception as e:
        logger.error(f"Error during humanized typing: {e}")


def scroll_natural(page: Any, direction: str = "down", distance: int = 500, steps: int = 5) -> None:
    """
    Perform a natural scroll with gradual movement.
    
    Args:
        page: The page object (Playwright Page or Selenium driver).
        direction: Scroll direction ("up" or "down").
        distance: Total distance to scroll in pixels.
        steps: Number of intermediate steps for smooth scrolling.
    """
    if page is None:
        logger.warning("Cannot scroll on None page")
        return
    
    scroll_amount = distance // steps
    sign = 1 if direction == "down" else -1
    
    try:
        for _ in range(steps):
            script = f"window.scrollBy(0, {sign * scroll_amount});"
            if hasattr(page, 'evaluate'):
                page.evaluate(script)
            elif hasattr(page, 'execute_script'):
                page.execute_script(script)
            else:
                logger.warning("Page object does not support script execution")
                return
            
            delay = random.uniform(SCROLL_PAUSE_MIN, SCROLL_PAUSE_MAX)
            time.sleep(delay)
    except Exception as e:
        logger.error(f"Error during natural scroll: {e}")


def random_mouse_movement(page: Any, x_range: tuple = (100, 800), y_range: tuple = (100, 600)) -> None:
    """
    Move mouse to a random position within specified ranges.
    
    Args:
        page: The page object (Playwright Page or Selenium driver).
        x_range: Tuple of (min_x, max_x) for random x coordinate.
        y_range: Tuple of (min_y, max_y) for random y coordinate.
    """
    if page is None:
        return
    
    x = random.randint(x_range[0], x_range[1])
    y = random.randint(y_range[0], y_range[1])
    
    try:
        if hasattr(page, 'mouse'):
            page.mouse.move(x, y)
    except Exception as e:
        logger.debug(f"Mouse movement not supported or failed: {e}")


def get_random_user_agent() -> str:
    """
    Return a random user agent string for Chrome on Windows/Mac.
    
    Returns:
        A randomly selected user agent string.
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    ]
    return random.choice(user_agents)


def simulate_reading_time(min_sec: float = 1.0, max_sec: float = 4.0) -> None:
    """
    Simulate time spent reading content on a page.
    
    Args:
        min_sec: Minimum reading time in seconds.
        max_sec: Maximum reading time in seconds.
    """
    random_delay(min_sec, max_sec)