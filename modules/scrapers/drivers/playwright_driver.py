"""
Playwright Driver Implementation.

Wraps Playwright Page to implement the DriverInterface,
providing a consistent API for browser automation with anti-detection measures.
"""

import logging
import random
from pathlib import Path
from typing import Any, List, Optional

from playwright.sync_api import (
    sync_playwright,
    Page,
    Browser,
    BrowserContext,
    TimeoutError as PlaywrightTimeout,
)

from .driver_interface import DriverInterface
from .humanized import (
    random_delay,
    get_random_user_agent,
    SCROLL_PAUSE_MIN,
    SCROLL_PAUSE_MAX,
)

logger = logging.getLogger(__name__)


class PlaywrightDriver(DriverInterface):
    """
    Playwright implementation of DriverInterface.
    
    Wraps Playwright Page with anti-detection measures,
    humanized behavior utilities, and stealth configurations.
    """
    
    def __init__(
        self,
        headless: bool = True,
        user_agent: Optional[str] = None,
        viewport: Optional[dict] = None,
    ):
        """
        Initialize the Playwright driver.
        
        Args:
            headless: Run browser in headless mode.
            user_agent: Custom user agent string.
            viewport: Viewport configuration dict.
        """
        self._headless = headless
        self._user_agent = user_agent or get_random_user_agent()
        self._viewport = viewport or {"width": 1920, "height": 1080}
        
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        
        self._initialize_driver()
    
    def _initialize_driver(self) -> None:
        """Initialize Playwright browser with anti-detection options."""
        try:
            self._playwright = sync_playwright().start()
            
            self._browser = self._playwright.chromium.launch(
                headless=self._headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                ]
            )
            
            self._context = self._browser.new_context(
                viewport=self._viewport,
                user_agent=self._user_agent,
                locale="en-US",
                timezone_id="America/New_York",
                geolocation={"latitude": 40.7128, "longitude": -74.0060},
                permissions=["geolocation"],
                ignore_https_errors=True,
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                },
            )
            
            self._context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en', 'es']
                });
                window.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'permissions', {
                    get: () => ({
                        query: () => Promise.resolve({ state: 'granted' })
                    })
                });
            """)
            
            self._page = self._context.new_page()
            
            self._page.set_default_timeout(30000)
            
            logger.info("Playwright driver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Playwright driver: {e}")
            self.close()
            raise
    
    @property
    def driver(self) -> "PlaywrightDriver":
        """Return self for compatibility with code expecting a driver property."""
        return self
    
    @property
    def page(self) -> Page:
        """Return the underlying Playwright Page instance."""
        if self._page is None:
            raise RuntimeError("Page not initialized")
        return self._page
    
    @property
    def current_url(self) -> str:
        return self.page.url
    
    @property
    def page_source(self) -> str:
        return self.page.content()
    
    def find_elements(self, selector: str) -> List[Any]:
        try:
            return self.page.locator(selector).all()
        except Exception as e:
            logger.debug(f"Error finding elements '{selector}': {e}")
            return []
    
    def find_element(self, selector: str) -> Optional[Any]:
        try:
            locator = self.page.locator(selector)
            if locator.count() > 0:
                return locator.first
            return None
        except Exception as e:
            logger.debug(f"Error finding element '{selector}': {e}")
            return None
    
    def goto(self, url: str, timeout: int = 30000) -> None:
        try:
            self.page.goto(url, timeout=timeout, wait_until="domcontentloaded")
            random_delay(0.5, 1.5)
        except PlaywrightTimeout:
            logger.warning(f"Page load timeout for {url}")
        except Exception as e:
            logger.error(f"Navigation error for {url}: {e}")
    
    def screenshot(self, path: Path) -> bool:
        try:
            self.page.screenshot(path=str(path))
            return True
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return False
    
    def get_text(self, selector: str) -> str:
        try:
            element = self.find_element(selector)
            if element:
                return element.text_content() or ""
            return ""
        except Exception as e:
            logger.debug(f"Error getting text from '{selector}': {e}")
            return ""
    
    def click(self, selector: str) -> None:
        try:
            self.page.hover(selector)
            random_delay(0.1, 0.3)
            self.page.click(selector, force=False, delay=random.randint(50, 150))
            random_delay(0.2, 0.5)
        except Exception as e:
            logger.debug(f"Click failed for '{selector}': {e}")
            try:
                self.page.evaluate(
                    f"document.querySelector('{selector}')?.click()"
                )
            except Exception:
                logger.warning(f"Force click also failed for '{selector}'")
    
    def fill(self, selector: str, value: str) -> None:
        try:
            self.page.click(selector)
            self.page.fill(selector, "")
            
            for char in value:
                self.page.type(selector, char, delay=random.randint(30, 100))
            
            random_delay(0.2, 0.4)
        except Exception as e:
            logger.debug(f"Humanized fill failed for '{selector}': {e}")
            try:
                self.page.fill(selector, value)
            except Exception:
                logger.warning(f"Fill also failed for '{selector}'")
    
    def wait_for_selector(self, selector: str, timeout: int = 10000) -> None:
        try:
            self.page.wait_for_selector(selector, timeout=timeout, state="attached")
        except PlaywrightTimeout:
            logger.debug(f"Timeout waiting for selector '{selector}'")
    
    def execute_script(self, script: str) -> Any:
        return self.page.evaluate(script)
    
    def close(self) -> None:
        errors = []
        
        if self._page:
            try:
                self._page.close()
            except Exception as e:
                errors.append(f"Page close error: {e}")
        
        if self._context:
            try:
                self._context.close()
            except Exception as e:
                errors.append(f"Context close error: {e}")
        
        if self._browser:
            try:
                self._browser.close()
            except Exception as e:
                errors.append(f"Browser close error: {e}")
        
        if self._playwright:
            try:
                self._playwright.stop()
            except Exception as e:
                errors.append(f"Playwright stop error: {e}")
        
        self._page = None
        self._context = None
        self._browser = None
        self._playwright = None
        
        if errors:
            logger.warning(f"Errors during close: {errors}")
        else:
            logger.info("Playwright driver closed")
    
    def wait(self, timeout: int = 10000) -> Page:
        """Return the page for chaining with Playwright's auto-waiting."""
        return self.page
    
    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        try:
            element = self.find_element(selector)
            if element:
                return element.get_attribute(attribute)
            return None
        except Exception as e:
            logger.debug(f"Error getting attribute from '{selector}': {e}")
            return None
    
    def is_visible(self, selector: str) -> bool:
        try:
            return self.page.is_visible(selector)
        except Exception:
            return False
    
    def scroll_to_element(self, selector: str) -> None:
        """Scroll to make the element visible."""
        try:
            self.page.locator(selector).scroll_into_view_if_needed()
            random_delay(SCROLL_PAUSE_MIN, SCROLL_PAUSE_MAX)
        except Exception as e:
            logger.debug(f"Scroll to element failed: {e}")
    
    def scroll_natural(self, distance: int = 500, steps: int = 5) -> None:
        """Perform a natural scroll with gradual movement."""
        scroll_amount = distance // steps
        
        for _ in range(steps):
            self.page.mouse.wheel(0, scroll_amount)
            random_delay(SCROLL_PAUSE_MIN, SCROLL_PAUSE_MAX)
    
    def __enter__(self) -> "PlaywrightDriver":
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()