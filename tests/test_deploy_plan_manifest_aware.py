"""Tests for v2.5 deploy plan building.

Ensures DeployManager builds a non-empty plan when assets are organized
in role folders and/or referenced via manifest.json.
"""

import json
from pathlib import Path

from modules.deployer.manager import DeployManager


def test_build_plan_finds_files_in_roles_and_manifest(tmp_path: Path):
    assets_dir = tmp_path / "delivery_assets"
    assets_dir.mkdir()

    # Role folder file (direct subfolder)
    role_owner = assets_dir / "01_PARA_EL_DUEÑO_HOY"
    role_owner.mkdir()
    (role_owner / "articulo_reserva_directa.md").write_text("# Artículo", encoding="utf-8")

    role_web = assets_dir / "02_PARA_EL_SITIO_WEB"
    role_web.mkdir()
    (role_web / "boton_whatsapp_codigo.html").write_text("<div>WA</div>", encoding="utf-8")

    # Nested file only discoverable via manifest path
    nested = assets_dir / "nested" / "inner"
    nested.mkdir(parents=True)
    (nested / "hotel-schema.json").write_text("{}", encoding="utf-8")

    manifest = {
        "version": "2.5.0",
        "files_generated": [
            {"path": "01_PARA_EL_DUEÑO_HOY/articulo_reserva_directa.md", "exists": True},
            {"path": "02_PARA_EL_SITIO_WEB/boton_whatsapp_codigo.html", "exists": True},
            {"path": "nested/inner/hotel-schema.json", "exists": True},
        ],
    }
    (assets_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    manager = DeployManager()
    plan = manager._build_plan(assets_dir=assets_dir, method="wp-api", manifest=manifest)

    assert len(plan.actions) >= 3

    sources = {a.source_file for a in plan.actions}
    assert "01_PARA_EL_DUEÑO_HOY/articulo_reserva_directa.md" in sources
    assert "02_PARA_EL_SITIO_WEB/boton_whatsapp_codigo.html" in sources
    assert "nested/inner/hotel-schema.json" in sources
