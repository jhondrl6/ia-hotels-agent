"""Base connector interface for deployment."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ConnectionResult:
    """Result of a connection attempt."""
    success: bool
    message: str = ""
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class BaseConnector(ABC):
    """Abstract base class for deployment connectors."""

    @abstractmethod
    def validate_connection(self, credentials: Dict[str, str]) -> ConnectionResult:
        """Validate connection credentials without performing actions.
        
        Args:
            credentials: Dict with connection credentials
            
        Returns:
            ConnectionResult with validation status
        """
        pass

    @abstractmethod
    def upload_file(
        self, 
        local_path: str, 
        remote_path: str, 
        credentials: Dict[str, str]
    ) -> ConnectionResult:
        """Upload a file to the remote server.
        
        Args:
            local_path: Path to local file
            remote_path: Destination path on server
            credentials: Connection credentials
            
        Returns:
            ConnectionResult with upload status
        """
        pass

    @abstractmethod
    def inject_code(
        self,
        code: str,
        target: str,  # "header" or "footer"
        credentials: Dict[str, str]
    ) -> ConnectionResult:
        """Inject code into header or footer of the site.
        
        Args:
            code: HTML/JS code to inject
            target: Where to inject ("header" or "footer")
            credentials: Connection credentials
            
        Returns:
            ConnectionResult with injection status
        """
        pass

    def create_post(
        self,
        title: str,
        content: str,
        status: str,
        credentials: Dict[str, str],
    ) -> ConnectionResult:
        """Create a new post/page when the connector supports it.

        Default implementation: not supported.
        """
        return ConnectionResult(
            success=False,
            error="Creación de posts no soportada por este conector",
        )
