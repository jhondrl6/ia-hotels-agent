"""Tests AC-G2: Entrada de datos independiente del entorno.

Verifica que _load_latest_onboarding_data funcione correctamente cuando:
- clientes_dir no existe (debe caer al fallback observations.json)
- clientes_dir existe pero no tiene el YAML del hotel (debe caer al fallback)
- clientes_dir existe y tiene el YAML del hotel (no necesita fallback)
"""
import json
import tempfile
from pathlib import Path
import pytest


def test_load_onboarding_fallback_to_observations_when_clientes_dir_missing():
    """AC-G2: Cuando clientes_dir no existe, debe usar observations.json."""
    from main import _load_latest_onboarding_data

    with tempfile.TemporaryDirectory() as tmpdir:
        # Crear observations.json con un hotel
        obs_dir = Path(tmpdir) / "data" / "hotel_observations"
        obs_dir.mkdir(parents=True)
        obs_file = obs_dir / "observations.json"
        obs_data = {
            "observations": [
                {
                    "hotel_name": "Hotel Test",
                    "website": "https://hoteltest.com/",
                    "rooms": 10,
                    "monthly_reservations": 50,
                    "avg_reservation_cop": 250000,
                    "direct_channel_percentage": 40.0,
                    "confidence": 0.95,
                    "epistemic_status": "verified",
                }
            ]
        }
        obs_file.write_text(json.dumps(obs_data), encoding="utf-8")

        # Cambiar al directorio temporal
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            # clientes_dir NO existe (output/clientes no existe)
            result = _load_latest_onboarding_data(
                hotel_url="https://hoteltest.com/",
                hotel_name="Hotel Test",
                output_dir=None,
            )
            # Debe encontrar el hotel via observations.json
            assert result is not None, "Debe encontrar el hotel via observations.json"
            assert result["hotel"]["nombre"] == "Hotel Test"
            assert result["metadatos"]["fuente"] == "observations_tier_a"
        finally:
            os.chdir(old_cwd)


def test_load_onboarding_fallback_when_yaml_not_found():
    """AC-G2: Cuando clientes_dir existe pero no tiene el YAML, debe usar observations.json."""
    from main import _load_latest_onboarding_data

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Crear clientes_dir vacío
        clientes_dir = tmpdir / "output" / "clientes"
        clientes_dir.mkdir(parents=True)

        # Crear observations.json con un hotel
        obs_dir = tmpdir / "data" / "hotel_observations"
        obs_dir.mkdir(parents=True)
        obs_file = obs_dir / "observations.json"
        obs_data = {
            "observations": [
                {
                    "hotel_name": "Hotel Fallback",
                    "website": "https://hotelfallback.com/",
                    "rooms": 15,
                    "monthly_reservations": 80,
                    "avg_reservation_cop": 300000,
                    "direct_channel_percentage": 50.0,
                    "confidence": 0.92,
                    "epistemic_status": "verified",
                }
            ]
        }
        obs_file.write_text(json.dumps(obs_data), encoding="utf-8")

        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            result = _load_latest_onboarding_data(
                hotel_url="https://hotelfallback.com/",
                hotel_name="Hotel Fallback",
                output_dir=clientes_dir,
            )
            # Debe encontrar el hotel via observations.json
            assert result is not None, "Debe caer al fallback observations.json"
            assert result["hotel"]["nombre"] == "Hotel Fallback"
            assert result["metadatos"]["fuente"] == "observations_tier_a"
        finally:
            os.chdir(old_cwd)


def test_load_onboarding_prefers_yaml_over_observations():
    """AC-G2: Cuando el YAML existe, NO debe usar observations.json."""
    from main import _load_latest_onboarding_data
    import yaml

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Crear clientes_dir con YAML
        clientes_dir = tmpdir / "output" / "clientes"
        clientes_dir.mkdir(parents=True)
        yaml_file = clientes_dir / "hotel_yaml_test_onboarding.yaml"
        yaml_data = {
            "metadatos": {"fecha_captura": "2026-09-15T10:00:00Z"},
            "hotel": {
                "nombre": "Hotel YAML",
                "url": "https://hotelyaml.com/",
            },
        }
        yaml_file.write_text(yaml.dump(yaml_data, allow_unicode=True), encoding="utf-8")

        # Crear observations.json con el mismo hotel (pero diferente data)
        obs_dir = tmpdir / "data" / "hotel_observations"
        obs_dir.mkdir(parents=True)
        obs_file = obs_dir / "observations.json"
        obs_data = {
            "observations": [
                {
                    "hotel_name": "Hotel OBS",
                    "website": "https://hotelyaml.com/",  # Misma URL
                    "rooms": 99,
                    "monthly_reservations": 999,
                    "avg_reservation_cop": 999999,
                    "direct_channel_percentage": 99.0,
                    "confidence": 0.99,
                    "epistemic_status": "verified",
                }
            ]
        }
        obs_file.write_text(json.dumps(obs_data), encoding="utf-8")

        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            result = _load_latest_onboarding_data(
                hotel_url="https://hotelyaml.com/",
                hotel_name="Hotel YAML",
                output_dir=clientes_dir,
            )
            # Debe preferir el YAML sobre observations.json
            assert result is not None
            assert result["hotel"]["nombre"] == "Hotel YAML", "Debe preferir el YAML"
            assert "metadatos" in result
            # NO debe tener el campo "fuente" = "observations.json"
            assert result["metadatos"].get("fuente") != "observations.json"
        finally:
            os.chdir(old_cwd)


def test_load_onboarding_returns_none_when_no_data():
    """AC-G2: Cuando no hay YAML ni observations.json, debe retornar None."""
    from main import _load_latest_onboarding_data

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Crear clientes_dir vacío
        clientes_dir = tmpdir / "output" / "clientes"
        clientes_dir.mkdir(parents=True)

        # NO crear observations.json

        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            result = _load_latest_onboarding_data(
                hotel_url="https://hotelinexistente.com/",
                hotel_name="Hotel Inexistente",
                output_dir=clientes_dir,
            )
            assert result is None, "Debe retornar None cuando no hay datos"
        finally:
            os.chdir(old_cwd)
