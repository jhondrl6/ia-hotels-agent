"""
Driver Interface for Browser Automation Abstraction.

Defines the abstract interface that all browser driver implementations must follow,
enabling seamless switching between Selenium, Playwright, and future drivers.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, List, Optional


class DriverInterface(ABC):
    """
    Abstract base class for browser driver implementations.
    
    Provides a unified interface for browser automation operations,
    allowing business logic to remain independent of the underlying driver.
    """
    
    @abstractmethod
    def find_elements(self, selector: str) -> List[Any]:
        """
        Find all elements matching the CSS selector.
        
        Args:
            selector: CSS selector string.
            
        Returns:
            List of element objects.
        """
        pass
    
    @abstractmethod
    def find_element(self, selector: str) -> Optional[Any]:
        """
        Find a single element matching the CSS selector.
        
        Args:
            selector: CSS selector string.
            
        Returns:
            Element object or None if not found.
        """
        pass
    
    @abstractmethod
    def goto(self, url: str, timeout: int = 30000) -> None:
        """
        Navigate to the specified URL.
        
        Args:
            url: The URL to navigate to.
            timeout: Timeout in milliseconds.
        """
        pass
    
    @abstractmethod
    def screenshot(self, path: Path) -> bool:
        """
        Take a screenshot of the current page.
        
        Args:
            path: Path to save the screenshot.
            
        Returns:
            True if screenshot was saved successfully, False otherwise.
        """
        pass
    
    @abstractmethod
    def get_text(self, selector: str) -> str:
        """
        Get the text content of an element.
        
        Args:
            selector: CSS selector string.
            
        Returns:
            Text content of the element, or empty string if not found.
        """
        pass
    
    @abstractmethod
    def click(self, selector: str) -> None:
        """
        Click on an element matching the selector.
        
        Args:
            selector: CSS selector string.
        """
        pass
    
    @abstractmethod
    def fill(self, selector: str, value: str) -> None:
        """
        Fill an input field with the specified value.
        
        Args:
            selector: CSS selector string.
            value: Value to fill in.
        """
        pass
    
    @abstractmethod
    def wait_for_selector(self, selector: str, timeout: int = 10000) -> None:
        """
        Wait for an element to appear on the page.
        
        Args:
            selector: CSS selector string.
            timeout: Timeout in milliseconds.
        """
        pass
    
    @abstractmethod
    def execute_script(self, script: str) -> Any:
        """
        Execute JavaScript code in the browser context.
        
        Args:
            script: JavaScript code to execute.
            
        Returns:
            Result of the script execution.
        """
        pass
    
    @abstractmethod
    def close(self) -> None:
        """
        Close the browser and release resources.
        """
        pass
    
    @property
    @abstractmethod
    def current_url(self) -> str:
        """
        Get the current URL of the page.
        
        Returns:
            Current URL string.
        """
        pass
    
    @property
    @abstractmethod
    def page_source(self) -> str:
        """
        Get the HTML source of the current page.
        
        Returns:
            HTML source string.
        """
        pass
    
    @abstractmethod
    def wait(self, timeout: int = 10000) -> Any:
        """
        Create a wait object for explicit waits.
        
        Args:
            timeout: Timeout in milliseconds.
            
        Returns:
            Wait object driver-specific implementation.
        """
        pass
    
    @abstractmethod
    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """
        Get an attribute value from an element.
        
        Args:
            selector: CSS selector string.
            attribute: Name of the attribute.
            
        Returns:
            Attribute value or None if not found.
        """
        pass
    
    @abstractmethod
    def is_visible(self, selector: str) -> bool:
        """
        Check if an element is visible on the page.
        
        Args:
            selector: CSS selector string.
            
        Returns:
            True if element is visible, False otherwise.
        """
        pass