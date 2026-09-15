"""FASE-P5 — Prevención en la captura: _save_cache del scraper GBP redacta
valores tipo API key ANTES de escribir el cache en disco.

Causa raíz medida en la auditoría de 2026-09-15: archives/gbp_profiles.json
publicó una key real porque el perfil scrapeado se guardaba en crudo.
Par NR7: el test rojo demuestra que SIN el guard el valor llega al disco.
Usa solo claves sintéticas; nunca imprime valores completos.
"""

import json
import logging

import pytest

from modules.scrapers import gbp_auditor
from modules.scrapers.gbp_auditor import (
    GBPAuditor,
    _redact_secrets_tree,
    _redact_secret_values,
)

# Claves sintéticas (no son credenciales reales)
FAKE_GEMINI = "AIzaSy" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7R"
FAKE_SK = "sk-" + "A1b2C3d4E5f6G7h8I9j0K1l2"
FAKE_GHP = "ghp_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7R8"
FAKE_PPLX = "pplx-" + "A1b2C3d4E5f6G7h8I9j0K1l2"


@pytest.fixture
def auditor(tmp_path):
    aud = GBPAuditor.__new__(GBPAuditor)
    aud.cache = {}
    aud.cache_path = tmp_path / "gbp_profiles.json"
    return aud


class TestRedaccionDePatrones:
    def test_gemini_aiqsy_redacted(self):
        out = _redact_secret_values(f'<script>key={FAKE_GEMINI}&x=1</script>')
        assert FAKE_GEMINI not in out
        assert "***REDACTED***" in out

    @pytest.mark.parametrize("secret", [FAKE_GEMINI, FAKE_SK, FAKE_GHP, FAKE_PPLX])
    def test_cada_patron_del_checker_redactado(self, secret):
        assert secret not in _redact_secret_values(f"texto {secret} texto")

    def test_texto_limpio_inalterado(self):
        clean = "Hotel Salento, Calle Real 12, +57 300 1234567"
        assert _redact_secret_values(clean) == clean

    def test_arbol_anidado_redactado(self):
        data = {
            "html": f"<div>{FAKE_GEMINI}</div>",
            "nested": {"lista": [FAKE_SK, "ok"]},
            "numero": 42,
            "nulo": None,
        }
        out = _redact_secrets_tree(data)
        assert FAKE_GEMINI not in json.dumps(out)
        assert FAKE_SK not in json.dumps(out)
        assert out["nested"]["lista"][1] == "ok"
        assert out["numero"] == 42


class TestSaveCacheIntegration:
    def test_save_cache_escribe_redactado(self, auditor):
        auditor._save_cache("h::loc", {"html": f"<p>{FAKE_GEMINI}</p>"})
        on_disk = auditor.cache_path.read_text(encoding="utf-8")
        assert FAKE_GEMINI not in on_disk
        assert "***REDACTED***" in on_disk

    def test_save_cache_no_mutara_el_diccionario_del_caller(self, auditor):
        profile = {"html": f"<p>{FAKE_GEMINI}</p>"}
        auditor._save_cache("h::loc", profile)
        # El caller conserva su dato en memoria para la sesión; la cura es el disco
        assert FAKE_GEMINI in profile["html"]

    def test_perfil_limpio_se_guarda_intacto(self, auditor, caplog):
        profile = {"name": "Hotel Real", "rating": 4.5}
        with caplog.at_level(logging.WARNING):
            auditor._save_cache("h::loc", profile)
        stored = json.loads(auditor.cache_path.read_text(encoding="utf-8"))
        assert stored["h::loc"]["profile"] == profile
        assert "redactados" not in caplog.text

    def test_avisa_cuando_redacta(self, auditor, caplog):
        with caplog.at_level(logging.WARNING):
            auditor._save_cache("h::loc", {"html": FAKE_SK})
        assert "redactados" in caplog.text
        # El warning no puede imprimir el valor del secreto
        assert FAKE_SK not in caplog.text

    def test_reescritura_no_resucita_secrets(self, auditor):
        """El cache en memoria ya está redactado: un segundo save del cache
        completo no reintroduce el valor."""
        auditor._save_cache("a::a", {"html": FAKE_GEMINI})
        auditor._save_cache("b::b", {"otro": "dato"})
        on_disk = auditor.cache_path.read_text(encoding="utf-8")
        assert FAKE_GEMINI not in on_disk


class TestParNR7Mutacion:
    def test_sin_el_guard_el_valor_llega_al_disco(self, auditor, monkeypatch):
        """ROJO controlado: desactivar los patrones debe hacer fallar la
        contención — prueba que quien protege es el guard, no el azar."""
        monkeypatch.setattr(gbp_auditor, "_SECRET_VALUE_PATTERNS", [])
        auditor._save_cache("h::loc", {"html": f"<p>{FAKE_GEMINI}</p>"})
        on_disk = auditor.cache_path.read_text(encoding="utf-8")
        assert FAKE_GEMINI in on_disk  # fuga con guard apagado

    def test_guard_activo_bloquea_esa_misma_fuga(self, auditor):
        """VERDE: mismo input, guard activo → sin fuga (espejo del rojo)."""
        auditor._save_cache("h::loc", {"html": f"<p>{FAKE_GEMINI}</p>"})
        on_disk = auditor.cache_path.read_text(encoding="utf-8")
        assert FAKE_GEMINI not in on_disk
