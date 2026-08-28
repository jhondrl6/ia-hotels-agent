"""FASE-SR-D — Tests anti-fragmentación de target_id (canonicalización de URL).

Cubre D-PF4: la identidad de memoria (target_id / hotel_id) se deriva de la
URL canónica via _normalize_url() (main.py) y de la normalización previa en
generate_hotel_id() (onboarding_controller). Con/sin UTM → el MISMO id, lo que
reactiva la reutilización de análisis (find_latest_v4_analysis, vigencia < 20
días) sin tocar agent_harness/memory.py (L-SR2, L16, N3).

Fuente: plan SR-PIPELINE-FIXES-2026-08-27, FASE-SR-D.
"""

from datetime import datetime
from pathlib import Path
import re

import pytest

from main import (
    _detect_region_from_url,
    _normalize_url,
    find_latest_v4_analysis,
)
from agent_harness.memory import MemoryManager
from modules.orchestration_v4.onboarding_controller import OnboardingController

# URL con UTM completo de la corrida C (CONTEXT-SALENTOREAL §3, log L67)
URL_UTM_COMPLETA = (
    "https://www.hotelsalentoreal.com/"
    "?utm_source=google&utm_medium=organic&utm_campaign=googlemybusiness&partner=5792"
)
URL_LIMPIA = "https://www.hotelsalentoreal.com/"
URL_PARTNER = "https://www.hotelsalentoreal.com/?partner=5792"
CANONICO = "hotelsalentoreal.com"
HOTEL_ID_CANONICO = "hotel_hotelsalentoreal.com"

_MAIN_PATH = Path(__file__).resolve().parent.parent / "main.py"
_ONB_PATH = (
    Path(__file__).resolve().parent.parent
    / "modules" / "orchestration_v4" / "onboarding_controller.py"
)


# ---------------------------------------------------------------------------
# T3.1 — target_id anti-fragmentación: UTM ≡ limpia ≡ partner → mismo id
# ---------------------------------------------------------------------------

class TestAntiFragmentacionTargetId:
    """Variaciones de campaña del mismo hotel → un único target_id canónico."""

    @pytest.mark.parametrize("url_variante", [
        URL_LIMPIA,
        URL_UTM_COMPLETA,
        URL_PARTNER,
        "http://hotelsalentoreal.com/",          # protocolo distinto
        "https://hotelsalentoreal.com",          # sin www, sin slash
        "www.hotelsalentoreal.com",              # sin protocolo
        "https://www.hotelsalentoreal.com/habitaciones",  # path distinto
    ])
    def test_variaciones_producen_mismo_target_id(self, url_variante):
        assert _normalize_url(url_variante) == CANONICO

    def test_utm_completa_igual_a_limpia(self):
        assert _normalize_url(URL_UTM_COMPLETA) == _normalize_url(URL_LIMPIA)

    def test_partner_igual_a_limpia(self):
        assert _normalize_url(URL_PARTNER) == _normalize_url(URL_LIMPIA)


# ---------------------------------------------------------------------------
# T3.2 — generate_hotel_id (onboarding_controller): normaliza antes de sanitizar
# ---------------------------------------------------------------------------

class TestGenerateHotelIdCanonico:
    """El log "Phase 1 iniciada" debe mostrar el hotel_id canónico sin UTM."""

    @pytest.mark.parametrize("url_variante", [
        URL_LIMPIA,
        URL_UTM_COMPLETA,
        URL_PARTNER,
        "http://hotelsalentoreal.com/",
        "www.hotelsalentoreal.com",
        "https://www.hotelsalentoreal.com/habitaciones",
    ])
    def test_variaciones_producen_mismo_hotel_id(self, url_variante):
        assert OnboardingController.generate_hotel_id(url_variante) == HOTEL_ID_CANONICO

    def test_hotel_id_canonico_sin_utm(self):
        """El hotel_id del log Phase 1 queda limpio: sin __utm_source_..."""
        hotel_id = OnboardingController.generate_hotel_id(URL_UTM_COMPLETA)
        assert hotel_id == HOTEL_ID_CANONICO
        assert "utm" not in hotel_id

    def test_compatibilidad_url_limpia_formato_previo(self):
        """URLs limpias conservan el formato 'hotel_<dominio>' de tests previos."""
        assert OnboardingController.generate_hotel_id("https://www.hoteltest.com") == "hotel_hoteltest.com"
        assert OnboardingController.generate_hotel_id("https://www.test.com") == "hotel_test.com"


# ---------------------------------------------------------------------------
# T3.3 — _detect_region_from_url con URL normalizada sigue funcionando
# ---------------------------------------------------------------------------

class TestRegionConUrlNormalizada:
    """El dominio canónico conserva la señal de región ('salento' → eje_cafetero)."""

    @pytest.mark.parametrize("url_variante", [
        URL_LIMPIA,
        URL_UTM_COMPLETA,
        "https://www.hotelsalentoreal.com/habitaciones",
        CANONICO,
    ])
    def test_eje_cafetero_con_url_normalizada(self, url_variante):
        assert _detect_region_from_url(_normalize_url(url_variante)) == "eje_cafetero"

    def test_region_url_cruda_con_utm_tambien_detecta(self):
        """La detección sobre la URL cruda (como la usa run_v4_complete_mode) no se rompe."""
        assert _detect_region_from_url(URL_UTM_COMPLETA) == "eje_cafetero"


# ---------------------------------------------------------------------------
# T3.4 — Reutilización de memoria end-to-end con IDs canónicos
# ---------------------------------------------------------------------------

class TestReutilizacionMemoria:
    """Análisis grabado con URL con UTM se recupera buscando por URL limpia."""

    def _entry_v4_valido(self) -> dict:
        return {
            "task_name": "v4complete",
            "outcome": "success",
            "coherence_score": 0.9,          # >= 0.8 (criterio find_latest_v4_analysis)
            "timestamp": datetime.now().isoformat(),  # < 20 días
        }

    def test_corrida_con_utm_reutilizada_por_url_limpia(self, tmp_path):
        memory = MemoryManager(memory_path=tmp_path)
        memory.append_log({"target_id": _normalize_url(URL_UTM_COMPLETA), **self._entry_v4_valido()})

        entry = find_latest_v4_analysis(memory, _normalize_url(URL_LIMPIA))
        assert entry is not None
        assert entry["target_id"] == CANONICO

    def test_corrida_limpia_reutilizada_por_url_con_utm(self, tmp_path):
        memory = MemoryManager(memory_path=tmp_path)
        memory.append_log({"target_id": _normalize_url(URL_LIMPIA), **self._entry_v4_valido()})

        entry = find_latest_v4_analysis(memory, _normalize_url(URL_UTM_COMPLETA))
        assert entry is not None
        assert entry["target_id"] == CANONICO

    def test_sin_fragmentacion_dos_corridas_mismo_hotel(self, tmp_path):
        """Corrida A (limpia) + corrida C (UTM) → UNA sola identidad, ambas visibles."""
        memory = MemoryManager(memory_path=tmp_path)
        memory.append_log({"target_id": _normalize_url(URL_LIMPIA), **self._entry_v4_valido()})
        memory.append_log({"target_id": _normalize_url(URL_UTM_COMPLETA), **self._entry_v4_valido()})

        history = memory.load_history(CANONICO)
        assert len(history) == 2


# ---------------------------------------------------------------------------
# T3.5 — Guardián estático L-SR1: símbolos canónicos presentes, crudos ausentes
# ---------------------------------------------------------------------------

class TestGuardianEstaticoCanonicalizacion:
    """Smoke L-SR1: las ramas modificadas de main.py cubiertas por test estático."""

    def test_main_sin_target_id_crudo(self):
        src = _MAIN_PATH.read_text(encoding="utf-8")
        assert "'target_id': args.url" not in src, "call site crudo residual (append_log/log_entry)"
        assert "target_id=args.url" not in src, "call site crudo residual (save_analysis_reference)"

    def test_main_con_target_id_canonico(self):
        src = _MAIN_PATH.read_text(encoding="utf-8")
        assert "'target_id': canonical_url" in src, "v4complete append_log/log_entry"
        assert "target_id=canonical_url" in src, "v4complete save_analysis_reference"
        assert "memory.find_latest_analysis(canonical_url)" in src, "v4complete búsqueda previa"
        assert "_normalize_url(args.url) if args.url" in src, "execute identidad canónica"
        assert 'canonical_url.split(".")[0]' in src, "validate-guarantee hotel_id canónico"
        assert "_parsed._replace(query='', fragment='')" in src, "onboard URL sin query"

    def test_generate_hotel_id_normaliza_antes_de_sanitizar(self):
        """0 replace() sobre URL cruda dentro de generate_hotel_id (T4 criterio)."""
        src = _ONB_PATH.read_text(encoding="utf-8")
        match = re.search(
            r"def generate_hotel_id.*?(?=\n    @staticmethod|\n    def |\Z)",
            src, re.DOTALL,
        )
        assert match, "generate_hotel_id no encontrado"
        block = match.group(0)
        assert "urlparse(" in block, "debe normalizar via urlparse antes de sanitizar"
        for ch in ("?", "&", "="):
            assert f'.replace("{ch}"' not in block, f"replace crudo residual de '{ch}'"
            assert f".replace('{ch}'" not in block, f"replace crudo residual de '{ch}'"
