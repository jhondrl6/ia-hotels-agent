"""FTP Connector for file uploads.

MVP v2.5: Connection validation only.
v2.6+: Full file upload capability.
"""

from __future__ import annotations

from typing import Dict

from modules.deployer.connectors.base import BaseConnector, ConnectionResult


class FTPConnector(BaseConnector):
    """FTP connector for file uploads."""

    def validate_connection(self, credentials: Dict[str, str]) -> ConnectionResult:
        """Validate FTP connection credentials.
        
        In v2.5 MVP, we only validate that credentials are properly formatted.
        In v2.6+, we'll actually attempt FTP connection.
        """
        host = credentials.get("host", "")
        user = credentials.get("user", "")
        password = credentials.get("password", "")
        port = credentials.get("port", "21")

        # Basic validation
        if not host:
            return ConnectionResult(
                success=False,
                error="Host FTP no configurado (IAH_FTP_HOST)",
            )
        
        if not user:
            return ConnectionResult(
                success=False,
                error="Usuario FTP no configurado (IAH_FTP_USER)",
            )

        if not password:
            return ConnectionResult(
                success=False,
                error="Contraseña FTP no configurada (IAH_FTP_PASS)",
            )

        # In v2.5 MVP, we simulate successful validation
        # In v2.6+, we'll attempt actual FTP connection
        return ConnectionResult(
            success=True,
            message=f"Credenciales FTP válidas para {user}@{host}:{port}",
            details={
                "host": host,
                "user": user,
                "port": port,
                "password": "****",  # Redacted
            }
        )

    def upload_file(
        self, 
        local_path: str, 
        remote_path: str, 
        credentials: Dict[str, str]
    ) -> ConnectionResult:
        """Upload a file via FTP.
        
        v2.5 MVP: Not implemented (dry-run only).
        """
        return ConnectionResult(
            success=False,
            error="Subida FTP no disponible en v2.5 MVP. Use --dry-run.",
        )

    def inject_code(
        self,
        code: str,
        target: str,
        credentials: Dict[str, str]
    ) -> ConnectionResult:
        """FTP cannot inject code directly.
        
        For FTP, code injection requires uploading modified files.
        """
        return ConnectionResult(
            success=False,
            error="Inyección de código no soportada vía FTP. Use archivos completos.",
        )
