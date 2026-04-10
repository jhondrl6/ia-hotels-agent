from pathlib import Path

import pytest

try:
    from modules.generators.proposal_gen import ProposalGenerator
except ImportError:
    ProposalGenerator = None  # Module removed/deprecated — existing tests will skip
from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator
from modules.commercial_documents.data_structures import (
    DiagnosticSummary,
    Scenario,
    ConfidenceLevel,
)


@pytest.mark.skipif(ProposalGenerator is None, reason="modules.generators.proposal_gen no longer exists")
def test_pro_plus_uses_client_copy_and_no_cert(tmp_path: Path) -> None:
    gen = ProposalGenerator()
    hotel_data = {"nombre": "Hotel Prueba"}
    claude_analysis = {
        "paquete_recomendado": "Pro AEO Plus",
        "gbp_data": {"score": 80, "gbp_activity_score": 100},
        "perdida_mensual_total": 1_000_000,
    }
    roi_data = {"totales_6_meses": {"roas": 1.5}}

    gen.create_pdf(hotel_data, claude_analysis, roi_data, tmp_path)

    content = (tmp_path / "02_PROPUESTA_COMERCIAL.md").read_text(encoding="utf-8")
    assert "Boton de WhatsApp directo" in content
    assert "Motor de reservas integrado" not in content
    assert "Certificado Reserva Directa" not in content


@pytest.mark.skipif(ProposalGenerator is None, reason="modules.generators.proposal_gen no longer exists")
def test_elite_plus_includes_certificate_block(tmp_path: Path) -> None:
    gen = ProposalGenerator()
    hotel_data = {"nombre": "Hotel Elite"}
    claude_analysis = {
        "paquete_recomendado": "Elite PLUS",
        "gbp_data": {"score": 85, "gbp_activity_score": 90},
        "perdida_mensual_total": 9_000_000,
    }
    roi_data = {"totales_6_meses": {"roas": 2.5}}

    gen.create_pdf(hotel_data, claude_analysis, roi_data, tmp_path)

    content = (tmp_path / "02_PROPUESTA_COMERCIAL.md").read_text(encoding="utf-8")
    assert "Certificados" in content
    assert "Reserva Directa" in content


@pytest.mark.skipif(ProposalGenerator is None, reason="modules.generators.proposal_gen no longer exists")
def test_owner_bundle_section_present(tmp_path: Path) -> None:
    gen = ProposalGenerator()
    hotel_data = {"nombre": "Hotel Bundle", "ubicacion": "Eje Cafetero"}
    claude_analysis = {
        "paquete_recomendado": "Starter GEO",
        "gbp_data": {"score": 55, "gbp_activity_score": 20},
        "perdida_mensual_total": 2_000_000,
        "region": "default",
    }
    roi_data = {"totales_6_meses": {"roas": 1.2}}

    gen.create_pdf(hotel_data, claude_analysis, roi_data, tmp_path)

    content = (tmp_path / "02_PROPUESTA_COMERCIAL.md").read_text(encoding="utf-8")
    for tag in ["[PLAN]", "[KPIS]", "[NECESITAMOS]", "[IMPLEMENTACION]", "[CADENCIA]", "[CIERRE]", "[UPGRADE]"]:
        assert tag in content, f"Falta bloque owner-friendly {tag} en propuesta"


# ── Phantom Cost Fix — Tests de Regresión (FASE-F) ──────────────────────────

def _make_scenario(monthly_loss: int = 10_000_000) -> Scenario:
    """Helper: crea un Scenario mínimo para tests."""
    return Scenario(
        monthly_loss_min=int(monthly_loss * 0.8),
        monthly_loss_max=monthly_loss,
        probability=1.0,
        description="test",
    )


def _make_diagnostic(top_problems=None) -> DiagnosticSummary:
    """Helper: crea un DiagnosticSummary mínimo para tests."""
    return DiagnosticSummary(
        hotel_name="Hotel Test",
        critical_problems_count=0,
        quick_wins_count=0,
        overall_confidence=ConfidenceLevel.VERIFIED,
        top_problems=top_problems if top_problems is not None else [],
    )


def test_no_phantom_costs_with_one_problem() -> None:
    """Con 1 top_problem, solo brecha_1 tiene costo no-cero; brechas 2-4 = $0."""
    gen = V4ProposalGenerator()
    scenario = _make_scenario(10_000_000)
    diag = _make_diagnostic(["SEO técnico deficiente"])

    result = gen._build_brecha_data(diag, scenario)

    assert result["brecha_1_nombre"] == "SEO técnico deficiente"
    assert result["brecha_1_costo"] != "$0"
    assert result["brecha_2_costo"] == "$0"
    assert result["brecha_2_nombre"] == ""
    assert result["brecha_3_costo"] == "$0"
    assert result["brecha_4_costo"] == "$0"


def test_no_phantom_costs_with_zero_problems() -> None:
    """Con 0 top_problems, todas las brechas = $0 y nombres vacíos."""
    gen = V4ProposalGenerator()
    scenario = _make_scenario(10_000_000)
    diag = _make_diagnostic([])

    result = gen._build_brecha_data(diag, scenario)

    for slot in range(1, 5):
        assert result[f"brecha_{slot}_costo"] == "$0"
        assert result[f"brecha_{slot}_nombre"] == ""


def test_no_phantom_costs_with_none_problems() -> None:
    """Con top_problems=None, no TypeError y todas las brechas = $0."""
    gen = V4ProposalGenerator()
    scenario = _make_scenario(5_000_000)
    diag = _make_diagnostic(None)

    # No debe lanzar TypeError
    result = gen._build_brecha_data(diag, scenario)

    for slot in range(1, 5):
        assert result[f"brecha_{slot}_costo"] == "$0"
        assert result[f"brecha_{slot}_nombre"] == ""


def test_costs_distributed_when_4_problems() -> None:
    """Con 4 problemas, todos los slots tienen costo no-cero y nombre asignado."""
    gen = V4ProposalGenerator()
    scenario = _make_scenario(12_000_000)
    problems = ["SEO técnico", "Contenido duplicado", "Sin schema markup", "Lentitud móvil"]
    diag = _make_diagnostic(problems)

    result = gen._build_brecha_data(diag, scenario)

    for slot in range(1, 5):
        idx = slot - 1
        assert result[f"brecha_{slot}_nombre"] == problems[idx]
        assert result[f"brecha_{slot}_costo"] != "$0"
    # Distribución equitativa: 12M / 4 = 3M por brecha
    assert "3.000.000" in result["brecha_1_costo"]


def test_empty_name_for_missing_brechas() -> None:
    """Slots sin problema tienen nombre vacío, no placeholder genérico."""
    gen = V4ProposalGenerator()
    scenario = _make_scenario(10_000_000)
    diag = _make_diagnostic(["Solo un problema"])

    result = gen._build_brecha_data(diag, scenario)

    # Nombre vacío, NO "Segundo problema" / "Tercer problema" / etc.
    assert result["brecha_2_nombre"] == ""
    assert result["brecha_3_nombre"] == ""
    assert result["brecha_4_nombre"] == ""
    # Sin phantom costs
    for slot in range(2, 5):
        assert result[f"brecha_{slot}_costo"] == "$0"
