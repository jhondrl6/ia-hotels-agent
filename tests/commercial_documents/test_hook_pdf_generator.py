"""
Tests unitarios para HookPDFGenerator (FASE-1 + FASE-2).

Cubre:
- extract_data(): parsing de 3 archivos fuente → HookPDFData
- validate_data(): 8 checks de validación
- render_html(): reemplazo de todos los {{PLACEHOLDER}}
- generate(): dry_run y generación real de PDF
- Helpers: _format_cop, _slugify

Aislamiento: cada test crea sus propios archivos en tmp_path.
"""

import json
import re
from dataclasses import asdict
from pathlib import Path

import pytest

from modules.commercial_documents.data_structures import HookPDFData
from modules.commercial_documents.hook_pdf_generator import (
    HookPDFGenerator,
    _format_cop,
    _slugify,
)

# ---------------------------------------------------------------------------
# Ruta al template real del repo (solo para render_html / generate)
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REAL_TEMPLATE = REPO_ROOT / "templates" / "hook_template.md"
REAL_STYLE = REPO_ROOT / "templates" / "hook_styles.css"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _write_fixtures(base: Path) -> None:
    """Crea los 3 archivos fuente de Luxorhotel en *base*."""

    # 1. Diagnóstico
    diag = base / "01_DIAGNOSTICO_Y_OPORTUNIDAD_20260707_121029.md"
    diag.write_text(
        """\
---
financial_evidence_tier: B
financial_value_range:
  - 2619187
  - 374170
gbp_resenas: "277"
gbp_rating: "4.1"
financial_ota_commission_real: "$7.741.440 COP"
---

## Luxorhotel - Cl. 24 #8-35, Pereira, Risaralda, Colombia

277 reviews, 4.1/5 rating en Google Business Profile.

## Score de Visibilidad Digital

| Pilar | Hotel | Regional |
|-------|-------|----------|
| SEO | 25/100 | 45/100 |
| GEO | 30/100 | 50/100 |
| AEO | 20/100 | 40/100 |
| IAO | 15/100 | 35/100 |
""",
        encoding="utf-8",
    )

    # 2. Propuesta comercial
    prop = base / "02_PROPUESTA_COMERCIAL_20260707_121029.md"
    prop.write_text(
        """\
---
precio_mensual: "400.000"
setup_fee: "2.500.000"
---

ROICR: 3.5x

Plan mensual: $400.000 COP/mes
Setup: $2.500.000 COP
""",
        encoding="utf-8",
    )

    # 3. v4_complete_report.json
    report = base / "v4_complete_report.json"
    report.write_text(
        json.dumps(
            {
                "hotel_name": "Luxorhotel",
                "url": "http://www.luxorhotel.com.co/",
                "region": "Pereira, Risaralda, Colombia",
                "financial_data": {"expected_monthly": 3741696},
                "opportunity_scores": [
                    {
                        "rank": 1,
                        "brecha_name": "SEO Local",
                        "estimated_monthly_cop": 1500000,
                        "justification": "Falta Google Business Profile optimizado",
                    },
                    {
                        "rank": 2,
                        "brecha_name": "Contenido Web",
                        "estimated_monthly_cop": 1200000,
                        "justification": "Sitio web sin estructura semántica",
                    },
                    {
                        "rank": 3,
                        "brecha_name": "Presencia en Maps",
                        "estimated_monthly_cop": 800000,
                        "justification": "Ficha de Google incompleta",
                    },
                ],
                "phases": {
                    "phase_4_publication_gates": {
                        "gate_results": [
                            {
                                "gate_name": "tier_c_onboarding_required",
                                "details": {"tier": "B"},
                            }
                        ]
                    }
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


@pytest.fixture()
def luxor_gen(tmp_path: Path) -> HookPDFGenerator:
    """Generador con archivos fuente de Luxorhotel en tmp_path."""
    _write_fixtures(tmp_path)
    return HookPDFGenerator(
        output_dir=tmp_path,
        template_path=REAL_TEMPLATE,
        style_path=REAL_STYLE if REAL_STYLE.exists() else None,
    )


@pytest.fixture()
def luxor_data(luxor_gen: HookPDFGenerator) -> HookPDFData:
    """HookPDFData ya extraído de los fixtures de Luxorhotel."""
    return luxor_gen.extract_data()


# ---------------------------------------------------------------------------
# 1. test_extract_data
# ---------------------------------------------------------------------------

class TestExtractData:
    """Verificar que HookPDFData se llena correctamente."""

    def test_hotel_fields(self, luxor_data: HookPDFData) -> None:
        assert luxor_data.hotel_nombre == "Luxorhotel"
        assert luxor_data.hotel_url == "http://www.luxorhotel.com.co/"
        assert luxor_data.hotel_region == "Pereira, Risaralda, Colombia"
        assert "Pereira" in luxor_data.hotel_direccion

    def test_financial_fields(self, luxor_data: HookPDFData) -> None:
        assert luxor_data.fuga_mensual == "3.741.696"
        # fuga_minima y fuga_maxima vienen del frontmatter (range)
        assert luxor_data.fuga_minima == "2.619.187"
        assert luxor_data.fuga_maxima == "374.170"

    def test_gbp_fields(self, luxor_data: HookPDFData) -> None:
        assert luxor_data.gbp_resenas == "277"
        assert luxor_data.gbp_rating == "4.1"

    def test_scores(self, luxor_data: HookPDFData) -> None:
        assert luxor_data.seo_score == "25"
        assert luxor_data.seo_regional == "45"
        assert luxor_data.geo_score == "30"
        assert luxor_data.geo_regional == "50"
        assert luxor_data.aeo_score == "20"
        assert luxor_data.aeo_regional == "40"
        assert luxor_data.iao_score == "15"
        assert luxor_data.iao_regional == "35"

    def test_brechas(self, luxor_data: HookPDFData) -> None:
        assert luxor_data.brecha_1_nombre == "SEO Local"
        assert luxor_data.brecha_1_cop == "1.500.000"
        assert "Google Business Profile" in luxor_data.brecha_1_justificacion
        assert luxor_data.brecha_2_nombre == "Contenido Web"
        assert luxor_data.brecha_3_nombre == "Presencia en Maps"

    def test_pricing_constants(self, luxor_data: HookPDFData) -> None:
        assert luxor_data.precio_express == "120.000"
        assert luxor_data.precio_mensual == "400.000"
        assert luxor_data.setup_fee == "2.500.000"

    def test_evidence_tier(self, luxor_data: HookPDFData) -> None:
        assert luxor_data.evidence_tier == "B"

    def test_roi(self, luxor_data: HookPDFData) -> None:
        assert luxor_data.roi == "3.5x"


# ---------------------------------------------------------------------------
# 2. test_validate_data_ok
# ---------------------------------------------------------------------------

def test_validate_data_ok(luxor_gen: HookPDFGenerator, luxor_data: HookPDFData) -> None:
    """Datos completos válidos → sin errores fatales."""
    warnings = luxor_gen.validate_data(luxor_data)
    fatal = [w for w in warnings if w.startswith("[ERROR]")]
    assert fatal == [], f"Errores fatales inesperados: {fatal}"


# ---------------------------------------------------------------------------
# 3. test_validate_data_missing_required
# ---------------------------------------------------------------------------

def test_validate_data_missing_required(luxor_gen: HookPDFGenerator) -> None:
    """Campo obligatorio crítico vacío → [ERROR]."""
    data = HookPDFData(
        hotel_nombre="Luxorhotel",
        fuga_mensual="",  # ← crítico vacío
        brecha_1_nombre="SEO Local",
        seo_score="25",
        precio_mensual="400.000",
        hotel_url="http://example.com",
        hotel_region="Pereira",
        hotel_direccion="Cl. 24",
        gbp_resenas="277",
        gbp_rating="4.1",
        seo_regional="45",
        geo_score="30",
        geo_regional="50",
        aeo_score="20",
        aeo_regional="40",
        iao_score="15",
        iao_regional="35",
        brecha_1_cop="1.500.000",
        brecha_1_justificacion="Justificación",
        precio_express="120.000",
        setup_fee="2.500.000",
        evidence_tier="B",
    )
    warnings = luxor_gen.validate_data(data)
    assert any("[ERROR]" in w and "fuga_mensual" in w for w in warnings), (
        f"Esperaba ERROR para fuga_mensual, got: {warnings}"
    )


# ---------------------------------------------------------------------------
# 4. test_validate_data_empty_optional
# ---------------------------------------------------------------------------

def test_validate_data_empty_optional(luxor_gen: HookPDFGenerator, luxor_data: HookPDFData) -> None:
    """Campos opcionales vacíos NO deben generar warnings."""
    luxor_data.fuga_minima = ""
    luxor_data.fuga_maxima = ""
    luxor_data.comision_ota_real = ""
    luxor_data.recuperacion_6m = ""
    luxor_data.roi = ""
    luxor_data.fuga_6m = ""

    warnings = luxor_gen.validate_data(luxor_data)
    # No debería haber warnings sobre campos opcionales vacíos
    for w in warnings:
        for field in ("fuga_minima", "fuga_maxima", "comision_ota_real",
                       "recuperacion_6m", "roi", "fuga_6m"):
            assert field not in w, f"Warning inesperado sobre campo opcional '{field}': {w}"


# ---------------------------------------------------------------------------
# 5. test_validate_data_invalid_tier
# ---------------------------------------------------------------------------

def test_validate_data_invalid_tier(luxor_gen: HookPDFGenerator, luxor_data: HookPDFData) -> None:
    """evidence_tier='X' → [WARN] tier inválido."""
    luxor_data.evidence_tier = "X"
    warnings = luxor_gen.validate_data(luxor_data)
    assert any("tier" in w.lower() and "[WARN]" in w for w in warnings), (
        f"Esperaba WARN sobre tier inválido, got: {warnings}"
    )


# ---------------------------------------------------------------------------
# 6. test_validate_data_accent_warning
# ---------------------------------------------------------------------------

def test_validate_data_accent_warning(luxor_gen: HookPDFGenerator, luxor_data: HookPDFData) -> None:
    """Nombre con acento → [WARN] sobre acentos."""
    luxor_data.hotel_nombre = "Hotel José"
    warnings = luxor_gen.validate_data(luxor_data)
    assert any("acento" in w.lower() for w in warnings), (
        f"Esperaba WARN sobre acentos, got: {warnings}"
    )


# ---------------------------------------------------------------------------
# 7. test_format_cop
# ---------------------------------------------------------------------------

class TestFormatCOP:

    @pytest.mark.parametrize(
        "value, expected",
        [
            (3741696, "3.741.696"),
            (1500000, "1.500.000"),
            (0, "0"),
            (100, "100"),
            (1000, "1.000"),
            (3741696.0, "3.741.696"),
        ],
    )
    def test_format_cop_int_float(self, value, expected):
        assert _format_cop(value) == expected

    @pytest.mark.parametrize(
        "value, expected",
        [
            ("3741696", "3.741.696"),
            ("3,741,696", "3.741.696"),
            ("7.741.440", "7.741.440"),
        ],
    )
    def test_format_cop_str(self, value, expected):
        assert _format_cop(value) == expected

    def test_format_cop_none(self):
        assert _format_cop(None) == ""

    def test_format_cop_non_numeric_str(self):
        assert _format_cop("abc") == "abc"


# ---------------------------------------------------------------------------
# 8. test_slugify
# ---------------------------------------------------------------------------

class TestSlugify:

    @pytest.mark.parametrize(
        "text, expected",
        [
            ("Luxorhotel", "luxorhotel"),
            ("Hotel José", "hotel_jose"),
            ("  Hotel Playa  ", "hotel_playa"),
            ("Hotel & Spa!", "hotel_spa"),
            ("Café del Mar", "cafe_del_mar"),
        ],
    )
    def test_slugify(self, text, expected):
        assert _slugify(text) == expected


# ---------------------------------------------------------------------------
# 9. test_render_html — cero {{...}} restantes
# ---------------------------------------------------------------------------

def test_render_html_no_remaining_placeholders(luxor_gen: HookPDFGenerator, luxor_data: HookPDFData) -> None:
    """El HTML renderizado NO debe contener {{...}} sin reemplazar."""
    html = luxor_gen.render_html(luxor_data)
    remaining = re.findall(r"\{\{[A-Z_0-9]+\}\}", html)
    assert remaining == [], f"Placeholders sin reemplazar: {remaining}"


def test_render_html_contains_hotel_name(luxor_gen: HookPDFGenerator, luxor_data: HookPDFData) -> None:
    """El nombre del hotel debe aparecer en el HTML renderizado."""
    html = luxor_gen.render_html(luxor_data)
    assert "Luxorhotel" in html


def test_render_html_contains_scores(luxor_gen: HookPDFGenerator, luxor_data: HookPDFData) -> None:
    """Los scores deben estar presentes en el HTML."""
    html = luxor_gen.render_html(luxor_data)
    assert "3.741.696" in html
    assert "1.500.000" in html


# ---------------------------------------------------------------------------
# 10. test_glob_pattern — archivos con timestamp variable
# ---------------------------------------------------------------------------

def test_glob_pattern_finds_timestamped_files(luxor_gen: HookPDFGenerator) -> None:
    """El glob 01_DIAGNOSTICO_*.md localiza archivos con cualquier timestamp."""
    matches = list(luxor_gen.output_dir.glob("01_DIAGNOSTICO_*.md"))
    assert len(matches) >= 1, "Glob no encontró archivos 01_DIAGNOSTICO_*.md"
    assert "20260707" in matches[0].name


def test_extract_data_missing_file_raises(tmp_path: Path) -> None:
    """Falta un archivo fuente → FileNotFoundError."""
    # Solo crear el diagnóstico, no la propuesta ni el JSON
    diag = tmp_path / "01_DIAGNOSTICO_Y_OPORTUNIDAD_20260707_121029.md"
    diag.write_text("---\n---\n", encoding="utf-8")

    gen = HookPDFGenerator(
        output_dir=tmp_path,
        template_path=REAL_TEMPLATE,
    )
    with pytest.raises(FileNotFoundError):
        gen.extract_data()


# ---------------------------------------------------------------------------
# 11. test_generate_dry_run
# ---------------------------------------------------------------------------

def test_generate_dry_run_no_pdf(luxor_gen: HookPDFGenerator) -> None:
    """dry_run=True NO debe crear archivo PDF."""
    result_path = luxor_gen.generate(dry_run=True)
    assert not result_path.exists(), f"dry_run creó el archivo: {result_path}"


# ---------------------------------------------------------------------------
# 12. test_generate_creates_pdf
# ---------------------------------------------------------------------------

def test_generate_creates_pdf(luxor_gen: HookPDFGenerator) -> None:
    """generate(force=True) crea un .pdf con contenido > 0 bytes."""
    pdf_path = luxor_gen.generate(force=True)
    assert pdf_path.exists(), f"PDF no creado: {pdf_path}"
    assert pdf_path.suffix == ".pdf"
    assert pdf_path.stat().st_size > 0, "PDF vacío"
