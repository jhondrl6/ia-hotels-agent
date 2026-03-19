"""
Selenium Driver Implementation.

Wraps Selenium WebDriver to implement the DriverInterface,
providing a consistent API for browser automation with anti-detection measures.
"""

import logging
import random
from pathlib import Path
from typing import Any, List, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    ElementNotInteractableException,
)

from .driver_interface import DriverInterface
from .humanized import (
    random_delay,
    type_humanlike,
    random_mouse_movement,
    get_random_user_agent,
)

logger = logging.getLogger(__name__)


class SeleniumDriver(DriverInterface):
    """
    Selenium implementation of DriverInterface.
    
    Wraps selenium.webdriver.Chrome with anti-detection measures
    and humanized behavior utilities.
    """
    
    def __init__(self, headless: bool = True, user_agent: Optional[str] = None):
        """
        Initialize the Selenium driver.
        
        Args:
            headless: Run browser in headless mode.
            user_agent: Custom user agent string.
        """
        self._headless = headless
        self._user_agent = user_agent or get_random_user_agent()
        self._driver: Optional[webdriver.Chrome] = None
        self._actions: Optional[ActionChains] = None
        self._initialize_driver()
    
    def _initialize_driver(self) -> None:
        """Initialize Chrome WebDriver with anti-detection options."""
        options = Options()
        
        if self._headless:
            options.add_argument("--headless=new")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        options.add_argument("--start-maximized")
        options.add_argument("--window-size=1920,1080")
        
        options.add_argument(f"--user-agent={self._user_agent}")
        
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.notifications": 2,
        }
        options.add_experimental_option("prefs", prefs)
        
        try:
            self._driver = webdriver.Chrome(options=options)
            self._actions = ActionChains(self._driver)
            
            self._driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {
                    "source": """
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
                    """
                }
            )
            logger.info("Selenium driver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Selenium driver: {e}")
            raise
    
    @property
    def driver(self) -> webdriver.Chrome:
        """Return the underlying Selenium WebDriver instance."""
        if self._driver is None:
            raise RuntimeError("Driver not initialized")
        return self._driver
    
    @property
    def current_url(self) -> str:
        return self.driver.current_url
    
    @property
    def page_source(self) -> str:
        return self.driver.page_source
    
    def find_elements(self, selector: str) -> List[Any]:
        try:
            return self.driver.find_elements(By.CSS_SELECTOR, selector)
        except Exception as e:
            logger.debug(f"Error finding elements '{selector}': {e}")
            return []
    
    def find_element(self, selector: str) -> Optional[Any]:
        try:
            return self.driver.find_element(By.CSS_SELECTOR, selector)
        except NoSuchElementException:
            return None
        except Exception as e:
            logger.debug(f"Error finding element '{selector}': {e}")
            return None
    
    def goto(self, url: str, timeout: int = 30000) -> None:
        self.driver.set_page_load_timeout(timeout // 1000)
        try:
            self.driver.get(url)
            random_delay(0.5, 1.5)
        except TimeoutException:
            logger.warning(f"Page load timeout for {url}")
            self.driver.execute_script("window.stop()")
    
    def screenshot(self, path: Path) -> bool:
        try:
            return self.driver.save_screenshot(str(path))
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return False
    
    def get_text(self, selector: str) -> str:
        element = self.find_element(selector)
        if element:
            try:
                return element.text
            except StaleElementReferenceException:
                element = self.find_element(selector)
                return element.text if element else ""
        return ""
    
    def click(self, selector: str) -> None:
        element = self.find_element(selector)
        if element:
            try:
                random_mouse_movement(self.driver)
                self._actions.move_to_element(element).pause(random.uniform(0.1, 0.3)).click().perform()
                random_delay(0.2, 0.5)
            except ElementNotInteractableException:
                self.driver.execute_script("arguments[0].click();", element)
            except Exception as e:
                logger.debug(f"Click failed for '{selector}': {e}")
                self.driver.execute_script("arguments[0].click();", element)
    
    def fill(self, selector: str, value: str) -> None:
        element = self.find_element(selector)
        if element:
            try:
                element.clear()
                type_humanlike(element, value)
            except ElementNotInteractableException:
                self.driver.execute_script(
                    f"arguments[0].value = '{value}';", element
                )
            except Exception as e:
                logger.debug(f"Fill failed for '{selector}': {e}")
    
    def wait_for_selector(self, selector: str, timeout: int = 10000) -> None:
        try:
            wait = WebDriverWait(self.driver, timeout // 1000)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        except TimeoutException:
            logger.debug(f"Timeout waiting for selector '{selector}'")
    
    def execute_script(self, script: str) -> Any:
        return self.driver.execute_script(script)
    
    def close(self) -> None:
        if self._driver:
            try:
                self._driver.quit()
                logger.info("Selenium driver closed")
            except Exception as e:
                logger.error(f"Error closing driver: {e}")
            finally:
                self._driver = None
                self._actions = None
    
    def wait(self, timeout: int = 10000) -> WebDriverWait:
        return WebDriverWait(self.driver, timeout // 1000)
    
    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        element = self.find_element(selector)
        if element:
            try:
                return element.get_attribute(attribute)
            except StaleElementReferenceException:
                element = self.find_element(selector)
                return element.get_attribute(attribute) if element else None
        return None
    
    def is_visible(self, selector: str) -> bool:
        element = self.find_element(selector)
        if element:
            try:
                return element.is_displayed()
            except StaleElementReferenceException:
                element = self.find_element(selector)
                return element.is_displayed() if element else False
        return False
    
    def scroll_to_element(self, selector: str) -> None:
        """Scroll to make the element visible."""
        element = self.find_element(selector)
        if element:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                element
            )
            random_delay(0.3, 0.6)
    
    def __enter__(self) -> "SeleniumDriver":
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()