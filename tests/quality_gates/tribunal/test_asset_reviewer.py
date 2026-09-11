"""Tests del AssetReviewer — Bot 3 del tribunal de certificación.

Tests deterministas sobre fixtures. Verifica cobertura por servicio,
P12 (fuente catálogo estático), IMPLEMENTATION_ORDER.md vacío,
assets huérfanos, assets genéricos, y serialización (R2.4).
"""

import json
from pathlib import Path

import pytest

from modules.quality_gates.tribunal.asset_reviewer import (
    AssetReviewer,
    FINDING_EMPTY_DELIVERY_TEMPLATE,
    FINDING_GENERIC_ASSET,
    FINDING_ORPHAN_ASSET,
    FINDING_P12_UNVERIFIABLE,
    FINDING_UNLABELED_ESTIMATED,
    STATUS_ASSET_ESTIMATED_NO_ETIQUETADO,
    STATUS_ASSET_GENERICO,
    STATUS_CON_ASSET,
    STATUS_SIN_ASSET,
    VERDICT_APROBADO,
    VERDICT_BLOQUEAR,
    VERDICT_DEVOLVER,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _make_matrix(entries=None, **kwargs):
    """Construye proposal_asset_matrix.json mínimo."""
    return {
        "proposal_asset_matrix_version": "2.1",
        "delivery_ready": kwargs.get("delivery_ready", True),
        "coverage_ratio": kwargs.get("coverage_ratio", 1.0),
        "alignment": {
            "coverage_ratio": kwargs.get("coverage_ratio", 1.0),
            "actionable_total": len(entries or []),
            "unresolved": 0,
        },
        "summary": {
            "promised": len(entries or []),
            "not_promised": 0,
            "unknown": 0,
            "actionable_total": len(entries or []),
            "unresolved": 0,
        },
        "entries": entries or [],
    }


def _make_asset_report(generated_assets=None, coherence_checks=None):
    """Construye asset_generation_report.json mínimo."""
    assets = generated_assets or []
    return {
        "hotel_id": "test_hotel",
        "summary": {
            "total_assets": len(assets),
            "generated": len(assets),
            "failed": 0,
            "skipped": 0,
        },
        "generated_assets": assets,
        "coherence_report": {
            "is_coherent": True,
            "overall_score": 0.85,
            "checks": coherence_checks or [],
        },
    }


@pytest.fixture
def audit_with_full_coverage(tmp_path):
    """Fixture con 2 servicios, ambos CON-ASSET, archivos reales en disco."""
    audit = tmp_path / "v4_audit"
    audit.mkdir()
    deliveries = tmp_path / "deliveries" / "test_hotel_20260910"
    deliveries.mkdir(parents=True)

    assets_dir = deliveries / "ASSETS"
    assets_dir.mkdir()

    faq_content = "# FAQ para Hotel Salento Real\n\n## Brecha: sin FAQ visible\n"
    faq_file = assets_dir / "faq_page_salento.html"
    faq_file.write_text(faq_content, encoding="utf-8")

    schema_content = "# Schema Hotel Salento\n\nImplementación para brecha schema\n"
    schema_file = assets_dir / "hotel_schema.json"
    schema_file.write_text(schema_content, encoding="utf-8")

    matrix = _make_matrix(entries=[
        {
            "service_name": "faq_page",
            "pain_ids": ["no_faq_visible"],
            "asset_type": "faq_page",
            "asset_path": str(faq_file),
            "confidence": 0.95,
            "status": "LINKED",
            "alignment": "aligned",
        },
        {
            "service_name": "hotel_schema",
            "pain_ids": ["no_schema"],
            "asset_type": "hotel_schema",
            "asset_path": str(schema_file),
            "confidence": 1.0,
            "status": "LINKED",
            "alignment": "aligned",
        },
    ])
    (audit / "proposal_asset_matrix.json").write_text(
        json.dumps(matrix), encoding="utf-8"
    )

    asset_report = _make_asset_report(
        generated_assets=[
            {
                "asset_type": "faq_page",
                "filename": "faq_page_salento.html",
                "path": str(faq_file),
                "confidence_score": 0.95,
                "pain_ids_resolved": ["no_faq_visible"],
                "can_use": True,
                "preflight_status": "PASSED",
            },
            {
                "asset_type": "hotel_schema",
                "filename": "hotel_schema.json",
                "path": str(schema_file),
                "confidence_score": 1.0,
                "pain_ids_resolved": ["no_schema"],
                "can_use": True,
                "preflight_status": "PASSED",
            },
        ],
        coherence_checks=[
            {
                "name": "promised_assets_exist",
                "passed": True,
                "score": 1.0,
                "message": "Todos los assets prometidos están implementados (2 assets verificados en esta pasada via generated_assets)",
                "severity": "info",
            },
        ],
    )
    (audit / "asset_generation_report.json").write_text(
        json.dumps(asset_report), encoding="utf-8"
    )

    impl_order = deliveries / "IMPLEMENTATION_ORDER.md"
    impl_order.write_text(
        "# Orden de Implementación\n\n"
        "## 1. FAQ Page\n"
        "Implementar FAQ con 10 preguntas frecuentes del Hotel Salento Real.\n\n"
        "## 2. Hotel Schema\n"
        "Implementar schema JSON-LD para el Hotel Salento Real.\n\n"
        "## Checklist\n"
        "- [ ] FAQ publicada\n- [ ] Schema validado\n",
        encoding="utf-8",
    )

    (deliveries / "MANIFEST.json").write_text(
        json.dumps({"files": [], "quality_metadata": {"evidence_tier": "B"}}),
        encoding="utf-8",
    )

    return audit, tmp_path / "deliveries"


@pytest.fixture
def audit_with_empty_impl_order(tmp_path):
    """Fixture con IMPLEMENTATION_ORDER.md vacío (plantilla stub)."""
    audit = tmp_path / "v4_audit"
    audit.mkdir()
    deliveries = tmp_path / "deliveries" / "test_hotel_20260910"
    deliveries.mkdir(parents=True)

    matrix = _make_matrix(entries=[
        {
            "service_name": "faq_page",
            "pain_ids": ["no_faq_visible"],
            "asset_type": "faq_page",
            "asset_path": None,
            "confidence": 0.95,
            "status": "LINKED",
            "alignment": "aligned",
        },
    ])
    (audit / "proposal_asset_matrix.json").write_text(
        json.dumps(matrix), encoding="utf-8"
    )

    asset_report = _make_asset_report(
        generated_assets=[
            {
                "asset_type": "faq_page",
                "filename": "faq_page.html",
                "path": None,
                "confidence_score": 0.95,
                "pain_ids_resolved": ["no_faq_visible"],
                "can_use": True,
                "preflight_status": "PASSED",
            },
        ],
    )
    (audit / "asset_generation_report.json").write_text(
        json.dumps(asset_report), encoding="utf-8"
    )

    stub_content = (
        "# Orden de Implementación\n\n"
        "## ORDEN de implementación\n\n"
        "## GUÍA paso a paso\n\n"
        "## CHECKLIST final\n"
    )
    impl_order = deliveries / "IMPLEMENTATION_ORDER.md"
    impl_order.write_text(stub_content, encoding="utf-8")

    (deliveries / "MANIFEST.json").write_text(
        json.dumps({"files": []}), encoding="utf-8"
    )

    return audit, tmp_path / "deliveries"


@pytest.fixture
def audit_with_zero_byte_impl_order(tmp_path):
    """Fixture con IMPLEMENTATION_ORDER.md de 0 bytes."""
    audit = tmp_path / "v4_audit"
    audit.mkdir()
    deliveries = tmp_path / "deliveries" / "test_hotel_20260910"
    deliveries.mkdir(parents=True)

    matrix = _make_matrix(entries=[])
    (audit / "proposal_asset_matrix.json").write_text(
        json.dumps(matrix), encoding="utf-8"
    )

    asset_report = _make_asset_report()
    (audit / "asset_generation_report.json").write_text(
        json.dumps(asset_report), encoding="utf-8"
    )

    impl_order = deliveries / "IMPLEMENTATION_ORDER.md"
    impl_order.write_text("", encoding="utf-8")

    (deliveries / "MANIFEST.json").write_text(
        json.dumps({"files": []}), encoding="utf-8"
    )

    return audit, tmp_path / "deliveries"


@pytest.fixture
def audit_with_p12_catalog_source(tmp_path):
    """Fixture con promised_assets_exist message via catalogo_estatico."""
    audit = tmp_path / "v4_audit"
    audit.mkdir()
    deliveries = tmp_path / "deliveries" / "test_hotel_20260910"
    deliveries.mkdir(parents=True)

    matrix = _make_matrix(entries=[
        {
            "service_name": "faq_page",
            "pain_ids": ["no_faq_visible"],
            "asset_type": "faq_page",
            "asset_path": None,
            "confidence": 0.95,
            "status": "LINKED",
            "alignment": "aligned",
        },
    ])
    (audit / "proposal_asset_matrix.json").write_text(
        json.dumps(matrix), encoding="utf-8"
    )

    asset_report = _make_asset_report(
        generated_assets=[
            {
                "asset_type": "faq_page",
                "filename": "faq_page.html",
                "path": None,
                "confidence_score": 0.95,
                "pain_ids_resolved": ["no_faq_visible"],
                "can_use": True,
                "preflight_status": "PASSED",
            },
        ],
        coherence_checks=[
            {
                "name": "promised_assets_exist",
                "passed": True,
                "score": 1.0,
                "message": "Todos los assets prometidos están implementados (2 assets verificados en esta pasada via catalogo_estatico)",
                "severity": "info",
            },
        ],
    )
    (audit / "asset_generation_report.json").write_text(
        json.dumps(asset_report), encoding="utf-8"
    )

    (deliveries / "MANIFEST.json").write_text(
        json.dumps({"files": []}), encoding="utf-8"
    )

    return audit, tmp_path / "deliveries"


@pytest.fixture
def audit_with_p12_generated_assets(tmp_path):
    """Fixture con promised_assets_exist message via generated_assets + asset en disco."""
    audit = tmp_path / "v4_audit"
    audit.mkdir()
    deliveries = tmp_path / "deliveries" / "test_hotel_20260910"
    deliveries.mkdir(parents=True)

    assets_dir = deliveries / "ASSETS"
    assets_dir.mkdir()

    faq_content = "# FAQ Hotel Salento Real\n\nBrecha: sin FAQ\n"
    faq_file = assets_dir / "faq_page.html"
    faq_file.write_text(faq_content, encoding="utf-8")

    matrix = _make_matrix(entries=[
        {
            "service_name": "faq_page",
            "pain_ids": ["no_faq_visible"],
            "asset_type": "faq_page",
            "asset_path": str(faq_file),
            "confidence": 0.95,
            "status": "LINKED",
            "alignment": "aligned",
        },
    ])
    (audit / "proposal_asset_matrix.json").write_text(
        json.dumps(matrix), encoding="utf-8"
    )

    asset_report = _make_asset_report(
        generated_assets=[
            {
                "asset_type": "faq_page",
                "filename": "faq_page.html",
                "path": str(faq_file),
                "confidence_score": 0.95,
                "pain_ids_resolved": ["no_faq_visible"],
                "can_use": True,
                "preflight_status": "PASSED",
            },
        ],
        coherence_checks=[
            {
                "name": "promised_assets_exist",
                "passed": True,
                "score": 1.0,
                "message": "Todos los assets prometidos están implementados (1 assets verificados en esta pasada via generated_assets)",
                "severity": "info",
            },
        ],
    )
    (audit / "asset_generation_report.json").write_text(
        json.dumps(asset_report), encoding="utf-8"
    )

    (deliveries / "MANIFEST.json").write_text(
        json.dumps({"files": []}), encoding="utf-8"
    )

    return audit, tmp_path / "deliveries"


@pytest.fixture
def audit_with_orphan_asset(tmp_path):
    """Fixture con asset generado sin servicio en la matriz."""
    audit = tmp_path / "v4_audit"
    audit.mkdir()
    deliveries = tmp_path / "deliveries" / "test_hotel_20260910"
    deliveries.mkdir(parents=True)

    matrix = _make_matrix(entries=[])
    (audit / "proposal_asset_matrix.json").write_text(
        json.dumps(matrix), encoding="utf-8"
    )

    asset_report = _make_asset_report(
        generated_assets=[
            {
                "asset_type": "monthly_report",
                "filename": "informe_mensual.md",
                "path": None,
                "confidence_score": 1.0,
                "pain_ids_resolved": [],
                "can_use": True,
                "preflight_status": "PASSED",
            },
        ],
    )
    (audit / "asset_generation_report.json").write_text(
        json.dumps(asset_report), encoding="utf-8"
    )

    (deliveries / "MANIFEST.json").write_text(
        json.dumps({"files": []}), encoding="utf-8"
    )

    return audit, tmp_path / "deliveries"


@pytest.fixture
def audit_with_generic_asset(tmp_path):
    """Fixture con asset que no menciona hotel ni brecha específica."""
    audit = tmp_path / "v4_audit"
    audit.mkdir()
    deliveries = tmp_path / "deliveries" / "test_hotel_20260910"
    deliveries.mkdir(parents=True)

    assets_dir = deliveries / "ASSETS"
    assets_dir.mkdir()

    generic_content = "# Guía de configuración\n\nPaso 1: Configurar analytics.\nPaso 2: Verificar tracking.\n"
    generic_file = assets_dir / "analytics_guide.md"
    generic_file.write_text(generic_content, encoding="utf-8")

    matrix = _make_matrix(entries=[
        {
            "service_name": "analytics_setup",
            "pain_ids": ["no_analytics"],
            "asset_type": "analytics_setup_guide",
            "asset_path": str(generic_file),
            "confidence": 1.0,
            "status": "LINKED",
            "alignment": "aligned",
        },
    ])
    (audit / "proposal_asset_matrix.json").write_text(
        json.dumps(matrix), encoding="utf-8"
    )

    asset_report = _make_asset_report(
        generated_assets=[
            {
                "asset_type": "analytics_setup_guide",
                "filename": "analytics_guide.md",
                "path": str(generic_file),
                "confidence_score": 1.0,
                "pain_ids_resolved": ["no_analytics"],
                "can_use": True,
                "preflight_status": "PASSED",
            },
        ],
    )
    (audit / "asset_generation_report.json").write_text(
        json.dumps(asset_report), encoding="utf-8"
    )

    (deliveries / "MANIFEST.json").write_text(
        json.dumps({"files": []}), encoding="utf-8"
    )

    return audit, tmp_path / "deliveries"


@pytest.fixture
def empty_dirs(tmp_path):
    """Directorios vacíos (never-block)."""
    audit = tmp_path / "v4_audit"
    audit.mkdir()
    deliveries = tmp_path / "deliveries"
    deliveries.mkdir()
    return audit, tmp_path / "deliveries"


# ── Tests obligatorios ────────────────────────────────────────────────


def test_coverage_by_service_populated(audit_with_full_coverage):
    """Salida tiene coverage_by_service con entradas por servicio."""
    audit_dir, deliveries_dir = audit_with_full_coverage
    reviewer = AssetReviewer(v4_audit_dir=audit_dir, deliveries_dir=deliveries_dir)
    report = reviewer.review()

    assert "coverage_by_service" in report
    assert isinstance(report["coverage_by_service"], list)
    assert len(report["coverage_by_service"]) == 2

    for entry in report["coverage_by_service"]:
        assert "service" in entry
        assert "status" in entry
        assert entry["status"] in (
            STATUS_CON_ASSET, STATUS_SIN_ASSET,
            STATUS_ASSET_GENERICO, STATUS_ASSET_ESTIMATED_NO_ETIQUETADO,
        )
        assert "asset_path" in entry
        assert "asset_exists_on_disk" in entry

    statuses = [e["status"] for e in report["coverage_by_service"]]
    assert all(s == STATUS_CON_ASSET for s in statuses)


def test_empty_implementation_order_detected(audit_with_empty_impl_order):
    """Fixture con IMPLEMENTATION_ORDER.md plantilla stub → EMPTY_DELIVERY_TEMPLATE."""
    audit_dir, deliveries_dir = audit_with_empty_impl_order
    reviewer = AssetReviewer(v4_audit_dir=audit_dir, deliveries_dir=deliveries_dir)
    report = reviewer.review()

    empty_findings = [
        f for f in report["findings"]
        if f["finding_type"] == FINDING_EMPTY_DELIVERY_TEMPLATE
    ]

    assert len(empty_findings) >= 1
    assert empty_findings[0]["severity"] == "CRITICAL"


def test_empty_implementation_order_zero_bytes(audit_with_zero_byte_impl_order):
    """IMPLEMENTATION_ORDER.md de 0 bytes → EMPTY_DELIVERY_TEMPLATE."""
    audit_dir, deliveries_dir = audit_with_zero_byte_impl_order
    reviewer = AssetReviewer(v4_audit_dir=audit_dir, deliveries_dir=deliveries_dir)
    report = reviewer.review()

    empty_findings = [
        f for f in report["findings"]
        if f["finding_type"] == FINDING_EMPTY_DELIVERY_TEMPLATE
    ]

    assert len(empty_findings) >= 1
    assert "0 bytes" in empty_findings[0]["description"]


def test_p12_catalog_source_detected(audit_with_p12_catalog_source):
    """Fixture con message 'via catalogo_estatico' → P12_UNVERIFIABLE."""
    audit_dir, deliveries_dir = audit_with_p12_catalog_source
    reviewer = AssetReviewer(v4_audit_dir=audit_dir, deliveries_dir=deliveries_dir)
    report = reviewer.review()

    p12_findings = [
        f for f in report["findings"]
        if f["finding_type"] == FINDING_P12_UNVERIFIABLE
    ]

    assert len(p12_findings) == 1
    assert "catálogo estático" in p12_findings[0]["description"]


def test_p12_generated_assets_not_flagged(audit_with_p12_generated_assets):
    """Fixture con message 'via generated_assets' + asset en disco → sin finding P12."""
    audit_dir, deliveries_dir = audit_with_p12_generated_assets
    reviewer = AssetReviewer(v4_audit_dir=audit_dir, deliveries_dir=deliveries_dir)
    report = reviewer.review()

    p12_findings = [
        f for f in report["findings"]
        if f["finding_type"] == FINDING_P12_UNVERIFIABLE
    ]

    assert len(p12_findings) == 0


def test_orphan_asset_detected(audit_with_orphan_asset):
    """Asset en disco sin servicio en matriz → ORPHAN_ASSET."""
    audit_dir, deliveries_dir = audit_with_orphan_asset
    reviewer = AssetReviewer(v4_audit_dir=audit_dir, deliveries_dir=deliveries_dir)
    report = reviewer.review()

    orphan_findings = [
        f for f in report["findings"]
        if f["finding_type"] == FINDING_ORPHAN_ASSET
    ]

    assert len(orphan_findings) >= 1
    assert "monthly_report" in orphan_findings[0]["description"]


def test_generic_asset_flagged(audit_with_generic_asset):
    """Asset sin mención de hotel → ASSET-GENERICO."""
    audit_dir, deliveries_dir = audit_with_generic_asset
    reviewer = AssetReviewer(v4_audit_dir=audit_dir, deliveries_dir=deliveries_dir)
    report = reviewer.review()

    generic_entries = [
        e for e in report["coverage_by_service"]
        if e["status"] == STATUS_ASSET_GENERICO
    ]

    assert len(generic_entries) >= 1
    assert generic_entries[0]["service"] == "analytics_setup"


def test_serialization_to_disk(tmp_path, audit_with_full_coverage):
    """Escribe JSON, lo re-lee, verifica claves (R2.4)."""
    audit_dir, deliveries_dir = audit_with_full_coverage
    reviewer = AssetReviewer(v4_audit_dir=audit_dir, deliveries_dir=deliveries_dir)
    output_path = tmp_path / "output" / "revision_assets.json"

    written_path = reviewer.write_report(output_path=output_path)

    assert written_path.exists()
    assert written_path.suffix == ".json"

    with open(written_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)

    required_keys = {
        "reviewer", "clauses", "coverage_by_service",
        "findings", "summary", "verdict_recommendation",
    }
    assert required_keys.issubset(loaded.keys())
    assert isinstance(loaded["coverage_by_service"], list)
    assert isinstance(loaded["summary"], dict)
    assert "services_covered" in loaded["summary"]
    assert "services_total" in loaded["summary"]
    assert "coverage_ratio" in loaded["summary"]


def test_asset_exists_on_disk_verified(audit_with_full_coverage):
    """asset_path poblado + archivo existe → asset_exists_on_disk: true."""
    audit_dir, deliveries_dir = audit_with_full_coverage
    reviewer = AssetReviewer(v4_audit_dir=audit_dir, deliveries_dir=deliveries_dir)
    report = reviewer.review()

    for entry in report["coverage_by_service"]:
        if entry["asset_path"]:
            assert entry["asset_exists_on_disk"] is True


def test_never_block_on_missing_artifacts(empty_dirs):
    """El revisor NUNCA lanza excepción por artefacto ausente (never-block)."""
    audit_dir, deliveries_dir = empty_dirs
    reviewer = AssetReviewer(v4_audit_dir=audit_dir, deliveries_dir=deliveries_dir)
    report = reviewer.review()

    assert report["reviewer"] == "asset_reviewer"
    assert isinstance(report["coverage_by_service"], list)
    assert report["verdict_recommendation"] in (
        VERDICT_APROBADO, VERDICT_DEVOLVER, VERDICT_BLOQUEAR,
    )


def test_does_not_import_gate_internals():
    """Grep: asset_reviewer.py no importa publication_gates internals."""
    reviewer_path = (
        PROJECT_ROOT / "modules" / "quality_gates" / "tribunal" / "asset_reviewer.py"
    )
    content = reviewer_path.read_text(encoding="utf-8")

    forbidden_imports = [
        "from modules.quality_gates.publication_gates import",
        "from modules.quality_gates import publication_gates",
        "import publication_gates",
        "check_publication_readiness",
        "BLOCKING_GATE_NAMES",
    ]

    for forbidden in forbidden_imports:
        assert forbidden not in content, (
            f"asset_reviewer.py contains forbidden import: {forbidden}"
        )


def test_verdict_blocks_on_empty_template(audit_with_empty_impl_order):
    """Finding CRITICAL (EMPTY_DELIVERY_TEMPLATE) → veredicto BLOQUEAR."""
    audit_dir, deliveries_dir = audit_with_empty_impl_order
    reviewer = AssetReviewer(v4_audit_dir=audit_dir, deliveries_dir=deliveries_dir)
    report = reviewer.review()

    assert report["verdict_recommendation"] == VERDICT_BLOQUEAR
    assert report["summary"]["services_total"] >= 0
