"""Tests for deploy execution (v2.6 experimental).

Ensures DeployManager can run without --dry-run and triggers connector actions
for inject/publish when assets are organized in roles.
"""

from pathlib import Path

from modules.deployer.manager import DeployManager
from modules.deployer.connectors.base import BaseConnector, ConnectionResult


class FakeConnector(BaseConnector):
    def __init__(self):
        self.inject_calls = []
        self.publish_calls = []
        self.upload_calls = []

    def validate_connection(self, credentials):
        return ConnectionResult(success=True, message="ok")

    def upload_file(self, local_path: str, remote_path: str, credentials):
        self.upload_calls.append((local_path, remote_path))
        return ConnectionResult(success=True, message="uploaded")

    def inject_code(self, code: str, target: str, credentials):
        self.inject_calls.append((code, target))
        return ConnectionResult(success=True, message=f"inject {target}")

    def create_post(self, title: str, content: str, status: str, credentials):
        self.publish_calls.append((title, content, status))
        return ConnectionResult(success=True, message="post created")


def test_execute_real_triggers_actions(tmp_path: Path):
    assets_dir = tmp_path / "delivery_assets"
    assets_dir.mkdir()

    # Manifest so _locate_assets accepts direct path
    (assets_dir / "manifest.json").write_text("{\"files_generated\": []}", encoding="utf-8")

    role_web = assets_dir / "02_PARA_EL_SITIO_WEB"
    role_web.mkdir()
    (role_web / "boton_whatsapp_codigo.html").write_text("<div>WA</div>", encoding="utf-8")

    role_owner = assets_dir / "01_PARA_EL_DUEÑO_HOY"
    role_owner.mkdir()
    (role_owner / "articulo_reserva_directa.md").write_text("# Titulo\nContenido", encoding="utf-8")

    manager = DeployManager()
    fake = FakeConnector()
    manager.connectors = {"wp-api": fake}

    # Force credentials to exist
    manager._load_credentials = lambda target, method: {  # type: ignore
        "site_url": "https://example.com",
        "username": "user",
        "app_password": "pass",
    }

    exit_code = manager.execute(
        target=str(assets_dir),
        method="wp-api",
        dry_run=False,
        verbose=False,
    )

    assert exit_code == DeployManager.EXIT_SUCCESS
    assert fake.inject_calls, "inject should be executed"
    assert fake.publish_calls, "publish should be executed"
