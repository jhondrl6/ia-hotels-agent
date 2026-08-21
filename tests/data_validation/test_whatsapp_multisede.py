"""Tests de contrato F12 — Validación WhatsApp multi-sede (FASE-P1-D).

Caso de referencia: Zi One Luxury (https://zione.co/) con 2 sedes
(Pereira y Cartagena). El número del GBP pertenece a la sede Pereira y es
idéntico al número web de esa sede; el número de la sede Cartagena NO debe
generar conflicto.

Contratos:
- C1: GBP coincide con ALGÚN número web → VERIFIED, sin conflicto.
- C2: Sin coincidencia + múltiples números sin mapeo de sede confiable →
      degrada a ESTIMATED (WARNING) con disclaimer, nunca CONFLICT.
- C3: Sin coincidencia + label de sede coincide con la sede GBP y difiere →
      CONFLICT real de misma sede.
- C4: Un solo número web que difiere del GBP → CONFLICT (legacy).
- C5: El scanner extrae TODOS los números wa.me/tel con label de sede.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from modules.data_validation.cross_validator import CrossValidator
from modules.data_validation.confidence_taxonomy import ConfidenceLevel
from modules.auditors.v4_comprehensive import V4ComprehensiveAuditor


# ─── Fixture multi-sede (caso Zione) ────────────────────────────────────────

ZIONE_FOOTER_HTML = """
<footer class="site-footer">
  <div class="elementor-widget-wrap">
    <div class="contact-block">
      <h5>Pereira Contact</h5>
      <a href="https://wa.me/573116079036">WhatsApp Pereira</a>
      <a href="tel:+573116079036">+57 311 607 9036</a>
    </div>
    <div class="contact-block">
      <h5>Cartagena Contact</h5>
      <a href="https://wa.me/573103724544">WhatsApp Cartagena</a>
    </div>
    <div class="elementor-element e-fab-whatsapp"></div>
  </div>
</footer>
"""

# Números del caso Zione
PEREIRA_WEB = "+57 311 607 9036"      # sede GBP (Pereira)
CARTAGENA_WEB = "+57 310 372 4544"    # sede alterna
GBP_PEREIRA = "311 6079036"


class _ScannerStub:
    """Acceso a los extractores sin instanciar el auditor completo."""
    _extract_sede_label = staticmethod(V4ComprehensiveAuditor._extract_sede_label)
    _extract_all_whatsapp_candidates = V4ComprehensiveAuditor._extract_all_whatsapp_candidates


def _candidates_from_fixture(html: str = ZIONE_FOOTER_HTML):
    return _ScannerStub._extract_all_whatsapp_candidates(_ScannerStub, html)


# ─── C5: Scanner multi-sede ─────────────────────────────────────────────────

def test_scanner_extracts_all_numbers_deduplicated():
    """Extrae todos los wa.me/tel únicos (tel duplicado del mismo número no cuenta)."""
    candidates = _candidates_from_fixture()
    numbers = [c["number"] for c in candidates]
    assert "573116079036" in numbers
    assert "573103724544" in numbers
    assert len(candidates) == 2, f"Esperados 2 números únicos, got {numbers}"


def test_scanner_extracts_sede_labels():
    """Cada número lleva el label de su sede (best-effort desde el DOM)."""
    candidates = _candidates_from_fixture()
    by_number = {c["number"]: c for c in candidates}
    pereira_label = (by_number["573116079036"].get("label") or "").lower()
    cartagena_label = (by_number["573103724544"].get("label") or "").lower()
    assert "pereira" in pereira_label, f"Label Pereira ausente: {pereira_label!r}"
    assert "cartagena" in cartagena_label, f"Label Cartagena ausente: {cartagena_label!r}"


def test_scanner_empty_html_returns_empty():
    assert _candidates_from_fixture("") == []
    assert _candidates_from_fixture("<html>sin contactos</html>") == []


# ─── C1: Caso Zione — GBP coincide con número de su sede → SIN conflicto ───

def test_zione_case_gbp_matches_same_sede_no_conflict():
    """GBP Pereira vs web Pereira+Cartagena → VERIFIED, sin falso positivo."""
    validator = CrossValidator()
    dp = validator.validate_whatsapp(
        web_value=PEREIRA_WEB,
        gbp_value=GBP_PEREIRA,
        web_alternates=_candidates_from_fixture(),
        gbp_location="Cra 13 # 5-20, Pereira, Risaralda",
    )
    assert dp is not None
    assert dp.confidence == ConfidenceLevel.VERIFIED, (
        f"GBP coincide con el número de la sede Pereira — esperado VERIFIED, "
        f"got {dp.confidence}"
    )
    # El conflicto NO debe aparecer en el reporte de conflictos
    assert validator.get_conflict_report() == []


def test_zione_case_gbp_matches_alternate_not_primary():
    """Si el número GBP solo aparece como alterno, igualmente VERIFIED."""
    validator = CrossValidator()
    dp = validator.validate_whatsapp(
        web_value=CARTAGENA_WEB,   # el primario es de otra sede
        gbp_value=GBP_PEREIRA,
        web_alternates=_candidates_from_fixture(),
    )
    assert dp.confidence == ConfidenceLevel.VERIFIED
    disclaimer = dp._validation_result.disclaimer or ""
    assert "alterna" in disclaimer.lower()


# ─── C2: Multi-sede sin coincidencia → degrada a WARNING ────────────────────

def test_multisede_no_match_degrades_to_warning():
    """GBP desconocido + 2 números web sin mapeo confiable → ESTIMATED, no CONFLICT."""
    validator = CrossValidator()
    alternates = [
        {"number": PEREIRA_WEB, "label": None},
        {"number": CARTAGENA_WEB, "label": None},
    ]
    dp = validator.validate_whatsapp(
        web_value=PEREIRA_WEB,
        gbp_value="+57 300 111 2233",
        web_alternates=alternates,
        gbp_location=None,  # sin metadata de sede confiable
    )
    assert dp.confidence == ConfidenceLevel.ESTIMATED, (
        f"Multi-sede sin mapeo debe degradar a ESTIMATED, got {dp.confidence}"
    )
    disclaimer = dp._validation_result.disclaimer or ""
    assert "multi-sede" in disclaimer.lower()
    assert validator.get_conflict_report() == []


# ─── C3: Conflicto REAL de misma sede se preserva ───────────────────────────

def test_same_sede_label_match_with_different_number_is_real_conflict():
    """Label del número coincide con la sede GBP y difiere → CONFLICT real."""
    validator = CrossValidator()
    alternates = [
        {"number": CARTAGENA_WEB, "label": "Pereira Contact"},  # sede mapeada
        {"number": "+57 300 999 8877", "label": "Cartagena Contact"},
    ]
    dp = validator.validate_whatsapp(
        web_value=CARTAGENA_WEB,
        gbp_value=GBP_PEREIRA,
        web_alternates=alternates,
        gbp_location="Cra 13 # 5-20, Pereira, Risaralda",
    )
    assert dp.confidence == ConfidenceLevel.CONFLICT, (
        f"La misma sede expone un número distinto al GBP — conflicto real, "
        f"got {dp.confidence}"
    )
    conflicts = validator.get_conflict_report()
    assert any(c["field_name"] == "whatsapp" for c in conflicts)


# ─── C4: Backwards compatibility — sitio mono-sede ──────────────────────────

def test_single_number_mismatch_keeps_legacy_conflict():
    """Un solo número web distinto del GBP → CONFLICT (comportamiento legado)."""
    validator = CrossValidator()
    dp = validator.validate_whatsapp(
        web_value=CARTAGENA_WEB,
        gbp_value=GBP_PEREIRA,
    )
    assert dp.confidence == ConfidenceLevel.CONFLICT


def test_single_number_match_keeps_verified():
    validator = CrossValidator()
    dp = validator.validate_whatsapp(web_value=PEREIRA_WEB, gbp_value=GBP_PEREIRA)
    assert dp.confidence == ConfidenceLevel.VERIFIED


def test_no_alternates_no_gbp_behaves_as_before():
    """Sin GBP no aplica reconciliación multi-sede."""
    validator = CrossValidator()
    dp = validator.validate_whatsapp(web_value=PEREIRA_WEB)
    assert dp is not None
    assert dp.confidence in (ConfidenceLevel.ESTIMATED, ConfidenceLevel.UNKNOWN)
