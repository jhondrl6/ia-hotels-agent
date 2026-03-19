from pathlib import Path

from modules.generators.proposal_gen import ProposalGenerator


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
    normalized = content.lower().replace("ñ", "n")
    assert "plan del dueno" in normalized
