"""WordPress REST API Connector.

MVP v2.5: Connection validation only.
v2.6+: Full post creation and code injection via plugins.
"""

from __future__ import annotations

from typing import Dict

import requests
from requests.auth import HTTPBasicAuth

from modules.deployer.connectors.base import BaseConnector, ConnectionResult


class WordPressConnector(BaseConnector):
    """WordPress REST API connector."""

    def validate_connection(self, credentials: Dict[str, str]) -> ConnectionResult:
        """Validate WordPress API connection credentials.
        
        In v2.5 MVP, we only validate that credentials are properly formatted.
        In v2.6+, we'll actually attempt API connection.
        """
        site_url = credentials.get("site_url", "")
        username = credentials.get("username", "")
        app_password = credentials.get("app_password", "")

        # Basic validation
        if not site_url:
            return ConnectionResult(
                success=False,
                error="URL del sitio no configurada (IAH_WP_URL)",
            )
        
        if not site_url.startswith(("http://", "https://")):
            return ConnectionResult(
                success=False,
                error="URL del sitio debe comenzar con http:// o https://",
            )

        if not username:
            return ConnectionResult(
                success=False,
                error="Usuario WordPress no configurado (IAH_WP_USER)",
            )

        if not app_password:
            return ConnectionResult(
                success=False,
                error="Application Password no configurado (IAH_WP_APP_PASS)",
            )

        api_base = f"{site_url.rstrip('/')}/wp-json/wp/v2"
        try:
            resp = requests.get(
                f"{api_base}/users/me",
                auth=HTTPBasicAuth(username, app_password),
                timeout=12,
            )
        except Exception as exc:
            return ConnectionResult(
                success=False,
                error=f"No se pudo conectar a WP API: {exc}",
            )

        if resp.status_code != 200:
            return ConnectionResult(
                success=False,
                error=f"WP API devolvió {resp.status_code}: {resp.text[:200]}",
            )

        data = resp.json() if resp.content else {}
        user_id = data.get("id") if isinstance(data, dict) else None
        return ConnectionResult(
            success=True,
            message=f"WP API ok para {username}@{site_url}",
            details={
                "site_url": site_url,
                "username": username,
                "app_password": "****",
                "user_id": user_id,
                "api_endpoint": f"{api_base}/",
            },
        )

    def upload_file(
        self, 
        local_path: str, 
        remote_path: str, 
        credentials: Dict[str, str]
    ) -> ConnectionResult:
        """Upload a file to WordPress media library.
        
        v2.5 MVP: Not implemented (dry-run only).
        """
        return ConnectionResult(
            success=False,
            error="Subida de medios no disponible en v2.5 MVP. Use --dry-run.",
        )

    def inject_code(
        self,
        code: str,
        target: str,
        credentials: Dict[str, str]
    ) -> ConnectionResult:
        """Inject code into WordPress header/footer.
        
        This would typically work via:
        1. WPCode plugin API
        2. Theme customizer API
        3. Custom plugin
        
        v2.5 MVP: Not implemented.
        """
        return ConnectionResult(
            success=False,
            error="Inyección de código requiere plugin (ej. WPCode) o endpoint habilitado. No ejecutado.",
        )

    def create_post(
        self,
        title: str,
        content: str,
        status: str = "draft",
        credentials: Dict[str, str] = None
    ) -> ConnectionResult:
        """Create a new WordPress post.
        
        v2.6: Usa /wp-json/wp/v2/posts endpoint (auth: Application Password).
        """
        credentials = credentials or {}
        site_url = (credentials.get("site_url") or "").strip()
        username = (credentials.get("username") or "").strip()
        app_password = (credentials.get("app_password") or "").strip()

        if not site_url or not username or not app_password:
            return ConnectionResult(
                success=False,
                error="Credenciales WP incompletas para crear post",
            )

        api_posts = f"{site_url.rstrip('/')}/wp-json/wp/v2/posts"
        try:
            resp = requests.post(
                api_posts,
                auth=HTTPBasicAuth(username, app_password),
                json={
                    "title": title or "Articulo IA Hoteles",
                    "content": content or "",
                    "status": status or "draft",
                },
                timeout=15,
            )
        except Exception as exc:
            return ConnectionResult(success=False, error=f"Error creando post: {exc}")

        if resp.status_code not in (200, 201):
            return ConnectionResult(
                success=False,
                error=f"WP API devolvió {resp.status_code}: {resp.text[:200]}",
            )

        data = resp.json() if resp.content else {}
        return ConnectionResult(
            success=True,
            message="Post creado en WP (draft)",
            details={
                "id": data.get("id"),
                "link": data.get("link"),
                "status": data.get("status"),
                "title": data.get("title", {}).get("rendered"),
            },
        )
