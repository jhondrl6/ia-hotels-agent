"""Tests de FASE-P3-A — AC-F1 (ZIP-only dos capas), AC-F2 (tier pre-packaging),
AC-F4 (primer piso en B+).

Plan TRIBUNAL-ENFORCEMENT-OBS-2026-09-11. Cada AC de detección/bloqueo lleva su
par NR7 (mutación → rojo) documentado en evidence/FASE-P3-A/. Los tests R2.6
corren sobre el baseline real ``output/FASE-D_salentoreal_post_guard/`` con
``skipif`` explícito; la evidencia declara si corrieron o se saltaron.
"""

import json
import shutil
import zipfile
from pathlib import Path

import pytest

from modules.quality_gates.tribunal.asset_reviewer import (
    AssetReviewer,
    FINDING_EMPTY_DELIVERY_TEMPLATE,
    IMPL_ORDER_ARTIFACT_MISSING,
    IMPL_ORDER_OK,
    IMPL_ORDER_READER_FAILED,
    SEVERITY_CRITICAL,
)
from modules.quality_gates.tribunal.judge import (
    FIRST_FLOOR_TIERS,
    TribunalJudge,
    VERDICT_CONDITIONAL,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]

BASELINE_DELIVERIES = (
    PROJECT_ROOT
    / "output"
    / "FASE-D_salentoreal_post_guard"
    / "v4_complete"
    / "deliveries"
)
BASELINE_ZIP = BASELINE_DELIVERIES / "hotelsalentoreal_20260831.zip"
BASELINE_DIR = BASELINE_DELIVERIES / "hotelsalentoreal_20260831"
FASE_I_AUDIT_DIR = (
    PROJECT_ROOT / "evidence" / "FASE-I" / "corrida" / "hotelsalentoreal" / "v4_audit"
)

# Stub REAL de 468 bytes copiado del ZIP del baseline FASE-D. Es la plantilla que
# AC8 no detectó en régimen ZIP-only: tiene 5 secciones declaradas pero todas sin
# contenido por-hotel (solo boilerplate Fecha/Score/REGLA DE ORO/footer/---).
REAL_STUB_468 = (
    "# 📦 Delivery Package - Hotelsalentoreal\n\n"
    "**Fecha:** 2026-08-31 12:28\n"
    "**Score GEO:** 79 (OPCIONAL)\n\n"
    "---\n\n"
    "## ⚠️ REGLA DE ORO: NUNCA REEMPLAZAR, SIEMPRE ENRIQUECER\n\n"
    "Los archivos CORE son **OBLIGATORIOS**.\n"
    "Los archivos GEO son **ENRICHMENT ADICIONAL**.\n\n"
    "---\n\n"
    "## 📋 ORDEN DE IMPLEMENTACIÓN\n\n"
    "---\n\n"
    "## 🔗 GUÍA DE RELACIONES ENTRE ARCHIVOS\n\n"
    "---\n\n"
    "## ✅ CHECKLIST DE IMPLEMENTACIÓN\n\n\n"
    "---\n\n"
    "*Generado por IA Hoteles Agent v4.0 - FASE-5 Asset Responsibility Contract*"
)

# Entrega REAL con contenido por-hotel: la sección ORDEN lleva entradas ### y la
# CHECKLIST lleva ítems marcados. NO es stub.
REAL_CONTENT = (
    "# 📦 Delivery Package - HotelX\n\n"
    "**Fecha:** 2026-08-31 12:28\n"
    "**Score GEO:** 79 (OPCIONAL)\n\n"
    "---\n\n"
    "## ⚠️ REGLA DE ORO: NUNCA REEMPLAZAR, SIEMPRE ENRIQUECER\n\n"
    "Los archivos CORE son **OBLIGATORIOS**.\n"
    "Los archivos GEO son **ENRICHMENT ADICIONAL**.\n\n"
    "---\n\n"
    "## 📋 ORDEN DE IMPLEMENTACIÓN\n\n"
    "### 1. boton_whatsapp.html ✅ [CORE]\n"
    "   - **Descripción:** Botón de WhatsApp para Hotel X\n"
    "   - **Prioridad:** ALTA\n\n"
    "---\n\n"
    "## 🔗 GUÍA DE RELACIONES ENTRE ARCHIVOS\n\n"
    "### boton_whatsapp.html ↔ geo_whatsapp\n"
    "- **boton_whatsapp.html** (CORE): Implementar PRIMERO\n\n"
    "---\n\n"
    "## ✅ CHECKLIST DE IMPLEMENTACIÓN\n\n"
    "- [x] boton_whatsapp.html\n\n"
    "---\n\n"
    "*Generado por IA Hoteles Agent v4.0 - FASE-5 Asset Responsibility Contract*"
)


# ── Helpers ───────────────────────────────────────────────────────────

def _make_zip_only_deliveries(tmp_path, members: dict, zip_name="testhotel_20260914.zip"):
    """Crea un deliveries_dir ZIP-only (sin directorio descomprimido)."""
    deliveries = tmp_path / "deliveries"
    deliveries.mkdir(parents=True, exist_ok=True)
    zip_path = deliveries / zip_name
    with zipfile.ZipFile(zip_path, "w") as zf:
        for name, content in members.items():
            zf.writestr(name, content)
    return deliveries


def _empty_audit(tmp_path):
    audit = tmp_path / "v4_audit"
    audit.mkdir(parents=True, exist_ok=True)
    return audit


def _impl_findings(report):
    return [
        f for f in report["findings"]
        if f.get("finding_type") == FINDING_EMPTY_DELIVERY_TEMPLATE
    ]


def _make_judge(tmp_path, scenarios_tier=None, manifest_tier=None, hotel_id="testhotel"):
    """Construye un TribunalJudge con scenarios y/o MANIFEST opcionales."""
    audit = tmp_path / "v4_audit"
    audit.mkdir(parents=True, exist_ok=True)
    if scenarios_tier is not None:
        (audit / "financial_scenarios_20260914_120000.json").write_text(
            json.dumps({"breakdown": {"evidence_tier": scenarios_tier}}),
            encoding="utf-8",
        )
    deliveries = tmp_path / "deliveries"
    deliveries.mkdir(parents=True, exist_ok=True)
    if manifest_tier is not None:
        hotel_dir = deliveries / f"{hotel_id}_20260914"
        hotel_dir.mkdir(parents=True)
        (hotel_dir / "MANIFEST.json").write_text(
            json.dumps({"quality_metadata": {"evidence_tier": manifest_tier}}),
            encoding="utf-8",
        )
    return TribunalJudge(
        v4_audit_dir=audit, deliveries_dir=deliveries, hotel_id=hotel_id
    )


# ══ AC-F1 — capa 1: lectura desde el ZIP en régimen ZIP-only ══════════

def test_zip_only_stub_detected_from_zip_member(tmp_path):
    """AC-F1 capa 1: el stub real de 468 B se detecta leyéndolo DESDE el ZIP."""
    deliveries = _make_zip_only_deliveries(
        tmp_path, {"IMPLEMENTATION_ORDER.md": REAL_STUB_468}
    )
    reviewer = AssetReviewer(_empty_audit(tmp_path), deliveries)
    report = reviewer.review()

    assert report["implementation_order_check"]["status"] == IMPL_ORDER_OK
    assert report["implementation_order_check"]["source"] == "zip"
    findings = _impl_findings(report)
    assert len(findings) == 1
    assert findings[0]["severity"] == SEVERITY_CRITICAL


def test_zip_only_real_content_not_flagged(tmp_path):
    """AC-F1: contenido real por-hotel dentro del ZIP NO es stub."""
    deliveries = _make_zip_only_deliveries(
        tmp_path, {"IMPLEMENTATION_ORDER.md": REAL_CONTENT}
    )
    reviewer = AssetReviewer(_empty_audit(tmp_path), deliveries)
    report = reviewer.review()

    assert report["implementation_order_check"]["status"] == IMPL_ORDER_OK
    assert report["implementation_order_check"]["source"] == "zip"
    assert _impl_findings(report) == []


def test_zip_member_missing_is_artifact_missing(tmp_path):
    """AC-F1/NR8: ZIP sin el miembro → ARTIFACT_MISSING, sin finding (no bloquea)."""
    deliveries = _make_zip_only_deliveries(
        tmp_path, {"MANIFEST.json": json.dumps({"files": []})}
    )
    reviewer = AssetReviewer(_empty_audit(tmp_path), deliveries)
    report = reviewer.review()

    assert report["implementation_order_check"]["status"] == IMPL_ORDER_ARTIFACT_MISSING
    assert report["implementation_order_check"]["source"] == "zip"
    assert _impl_findings(report) == []


def test_corrupt_zip_is_reader_failed(tmp_path):
    """AC-F1/NR8: ZIP ilegible → READER_FAILED, sin finding (no bloquea)."""
    deliveries = tmp_path / "deliveries"
    deliveries.mkdir(parents=True)
    (deliveries / "testhotel_20260914.zip").write_bytes(b"not a real zip content")

    reviewer = AssetReviewer(_empty_audit(tmp_path), deliveries)
    report = reviewer.review()

    assert report["implementation_order_check"]["status"] == IMPL_ORDER_READER_FAILED
    assert _impl_findings(report) == []


def test_nothing_in_deliveries_is_artifact_missing(tmp_path):
    """AC-F1/NR8: deliveries vacío (ni dir ni ZIP) → ARTIFACT_MISSING, sin finding."""
    deliveries = tmp_path / "deliveries"
    deliveries.mkdir(parents=True)

    reviewer = AssetReviewer(_empty_audit(tmp_path), deliveries)
    report = reviewer.review()

    assert report["implementation_order_check"]["status"] == IMPL_ORDER_ARTIFACT_MISSING
    assert report["implementation_order_check"]["source"] is None
    assert _impl_findings(report) == []


def test_dir_path_still_reads_unzipped_backward_compat(tmp_path):
    """AC-F1: el directorio descomprimido sigue leyéndose (compatibilidad FASE-D)."""
    deliveries = tmp_path / "deliveries"
    hotel_dir = deliveries / "testhotel_20260914"
    hotel_dir.mkdir(parents=True)
    (hotel_dir / "IMPLEMENTATION_ORDER.md").write_text(REAL_STUB_468, encoding="utf-8")

    reviewer = AssetReviewer(_empty_audit(tmp_path), deliveries)
    report = reviewer.review()

    assert report["implementation_order_check"]["status"] == IMPL_ORDER_OK
    assert report["implementation_order_check"]["source"] == "dir"
    assert len(_impl_findings(report)) == 1


# ══ AC-F1 — capa 2: criterio estructural del stub ═════════════════════

def test_structural_stub_excludes_boilerplate(tmp_path):
    """AC-F1 capa 2: el boilerplate (Fecha/Score/REGLA/footer/---) no cuenta como
    contenido; todas las secciones vacías → stub."""
    reviewer = AssetReviewer(_empty_audit(tmp_path), tmp_path / "deliveries")
    assert reviewer._is_template_stub(REAL_STUB_468) is True


def test_structural_real_content_not_stub(tmp_path):
    """AC-F1 capa 2: entradas ### y ítems de checklist cuentan como contenido real."""
    reviewer = AssetReviewer(_empty_audit(tmp_path), tmp_path / "deliveries")
    assert reviewer._is_template_stub(REAL_CONTENT) is False


def test_structural_checklist_items_alone_make_it_real(tmp_path):
    """AC-F1 capa 2: una sola sección con ítems ``- [x]`` ya NO es stub
    (el conteo viejo de líneas las ignoraba por empezar con '-')."""
    content = (
        "# Title\n\n"
        "## 📋 ORDEN DE IMPLEMENTACIÓN\n\n"
        "---\n\n"
        "## ✅ CHECKLIST DE IMPLEMENTACIÓN\n\n"
        "- [x] boton_whatsapp.html\n"
    )
    reviewer = AssetReviewer(_empty_audit(tmp_path), tmp_path / "deliveries")
    assert reviewer._is_template_stub(content) is False


def test_structural_blank_content_is_stub(tmp_path):
    """AC-F1 capa 2: contenido en blanco → stub."""
    reviewer = AssetReviewer(_empty_audit(tmp_path), tmp_path / "deliveries")
    assert reviewer._is_template_stub("   \n\n  ") is True


# ══ AC-F1 — R2.6 sobre el baseline REAL (ZIP-only y dir) ══════════════

@pytest.mark.skipif(
    not BASELINE_ZIP.is_file(), reason="baseline ZIP SalentoReal no disponible"
)
def test_real_baseline_zip_only_stub_detected(tmp_path):
    """R2.6/AC-F1: el ZIP real del baseline, en régimen ZIP-only (sin dir),
    detecta el stub de 468 B que AC8 dejó pasar. Lee el miembro desde el ZIP."""
    deliveries = tmp_path / "deliveries"
    deliveries.mkdir(parents=True)
    shutil.copy(BASELINE_ZIP, deliveries / BASELINE_ZIP.name)

    reviewer = AssetReviewer(_empty_audit(tmp_path), deliveries)
    report = reviewer.review()

    assert report["implementation_order_check"]["status"] == IMPL_ORDER_OK
    assert report["implementation_order_check"]["source"] == "zip"
    findings = _impl_findings(report)
    assert len(findings) == 1, "el stub real de 468 B debe detectarse desde el ZIP"
    assert findings[0]["severity"] == SEVERITY_CRITICAL


@pytest.mark.skipif(
    not BASELINE_DIR.is_dir(), reason="baseline dir SalentoReal no disponible"
)
def test_real_baseline_dir_stub_detected(tmp_path):
    """R2.6/AC-F1: sobre el baseline real con dir+ZIP, la lectura dir-first
    detecta el mismo stub (compatibilidad hacia atrás verificada con artefacto real)."""
    reviewer = AssetReviewer(_empty_audit(tmp_path), BASELINE_DELIVERIES)
    report = reviewer.review()

    assert report["implementation_order_check"]["status"] == IMPL_ORDER_OK
    assert report["implementation_order_check"]["source"] == "dir"
    assert len(_impl_findings(report)) == 1


# ══ AC-F2 — tier del acta desde la fuente pre-packaging ═══════════════

def test_tier_read_from_financial_scenarios(tmp_path):
    """AC-F2: sin MANIFEST, el tier sale de financial_scenarios → breakdown."""
    judge = _make_judge(tmp_path, scenarios_tier="A")
    acta = judge.evaluate()
    assert acta["evidence_tier"] == "A"


def test_scenarios_takes_priority_over_manifest(tmp_path):
    """AC-F2/DA-P1.5: scenarios (pre-packaging) gana sobre MANIFEST (post-packaging)."""
    judge = _make_judge(tmp_path, scenarios_tier="A", manifest_tier="C")
    acta = judge.evaluate()
    assert acta["evidence_tier"] == "A"


def test_manifest_fallback_when_no_scenarios(tmp_path):
    """AC-F2: sin scenarios, el MANIFEST sigue siendo el fallback."""
    judge = _make_judge(tmp_path, scenarios_tier=None, manifest_tier="B")
    acta = judge.evaluate()
    assert acta["evidence_tier"] == "B"


def test_tier_c_when_no_source(tmp_path):
    """AC-F2: sin scenarios ni MANIFEST → 'C' (último recurso, nunca vacío)."""
    judge = _make_judge(tmp_path, scenarios_tier=None, manifest_tier=None)
    acta = judge.evaluate()
    assert acta["evidence_tier"] == "C"


@pytest.mark.skipif(
    not FASE_I_AUDIT_DIR.is_dir(), reason="baseline FASE-I no disponible"
)
def test_real_fase_i_tier_from_scenarios(tmp_path):
    """R2.6/AC-F2: sobre el audit REAL de FASE-I (scenarios tier 'B') y sin
    deliveries, el acta lee 'B' desde la fuente pre-packaging, no el 'C' fallback."""
    judge = TribunalJudge(
        v4_audit_dir=FASE_I_AUDIT_DIR,
        deliveries_dir=tmp_path / "no_deliveries",
        hotel_id="hotelsalentoreal",
    )
    acta = judge.evaluate()
    assert acta["evidence_tier"] == "B"


# ══ AC-F4 — primer piso coherente en B+ ═══════════════════════════════

def test_b_plus_in_first_floor_tiers():
    """AC-F4: EvidenceTier.B_PLUS se serializa como 'B+' y está en FIRST_FLOOR_TIERS."""
    assert "B+" in FIRST_FLOOR_TIERS


def test_first_floor_applies_to_b_plus(tmp_path):
    """AC-F4: tier 'B+' → primer piso aplicado, razón coherente (no miente)."""
    judge = _make_judge(tmp_path, scenarios_tier="B+")
    acta = judge.evaluate()
    rule = acta["first_floor_rule"]
    assert rule["applied"] is True
    assert "B+" in rule["reason"]
    assert "máximo condicional" in rule["reason"]


def test_first_floor_reason_not_lying_in_b_plus(tmp_path):
    """AC-F4: la razón en 'B+' NO dice 'sin restricción' (el bug del acta vieja)."""
    judge = _make_judge(tmp_path, scenarios_tier="B+")
    acta = judge.evaluate()
    assert "sin restricción" not in acta["first_floor_rule"]["reason"]


def test_b_plus_verdict_is_conditional(tmp_path):
    """AC-F4: tier 'B+' → veredicto condicional, nunca APROBADO-PARA-ENTREGA."""
    judge = _make_judge(tmp_path, scenarios_tier="B+")
    acta = judge.evaluate()
    assert acta["verdict"] == VERDICT_CONDITIONAL
