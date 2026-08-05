# -*- coding: utf-8 -*-
"""RC1 (FASE-B): Gate de no-regresión de consistencia propuesta ↔ diagnóstico.

Verifica que la tabla de servicios de la propuesta cite el MISMO costo, rank y
label de brecha que el diagnóstico del mismo run, consumiendo opportunity_scores
del pipeline en lugar del mapa estático hardcodeado (hallazgos N10/N17/N18/N19).

Fixture: opportunity_scores del run real 20260804_124443 (Zi One Luxury).
"""

import re

import pytest

from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator


# Fixture: 8 entries de opportunity_scores del run 20260804_124443
# (output/v4_verify_4.70.0/v4_complete/v4_complete_report.json)
OPPORTUNITY_SCORES_ZIONE = [
    {"brecha_id": "whatsapp_conflict", "rank": 1, "estimated_monthly_cop": 1198906, "brecha_name": "Conflicto de WhatsApp"},
    {"brecha_id": "no_hotel_schema", "rank": 2, "estimated_monthly_cop": 1498094, "brecha_name": "Sin Schema Hotel"},
    {"brecha_id": "no_faq_schema", "rank": 3, "estimated_monthly_cop": 719200, "brecha_name": "Sin Schema FAQ"},
    {"brecha_id": "low_seo_score", "rank": 4, "estimated_monthly_cop": 1198906, "brecha_name": "SEO Local Bajo"},
    {"brecha_id": "no_analytics_configured", "rank": 5, "estimated_monthly_cop": 599094, "brecha_name": "Sin Analytics Configurado"},
    {"brecha_id": "low_organic_visibility", "rank": 6, "estimated_monthly_cop": 599094, "brecha_name": "Baja Visibilidad de Trafico Organico"},
    {"brecha_id": "ai_crawler_blocked", "rank": 7, "estimated_monthly_cop": 899000, "brecha_name": "Crawlers de IA Bloqueados"},
    {"brecha_id": "no_og_tags", "rank": 8, "estimated_monthly_cop": 479706, "brecha_name": "Open Graph Tags Incompletos"},
]

# Assets del área propuesta generados (confianza alta → estado ✅ Alineado)
ASSETS_GENERATED = [
    {"asset_type": "optimization_guide", "confidence_score": 0.9},
    {"asset_type": "whatsapp_button", "confidence_score": 0.9},
    {"asset_type": "hotel_schema", "confidence_score": 0.9},
    {"asset_type": "org_schema", "confidence_score": 0.9},
    {"asset_type": "faq_page", "confidence_score": 0.9},
    {"asset_type": "open_graph", "confidence_score": 0.9},
    {"asset_type": "llms_txt", "confidence_score": 0.9},
]

COST_LITERAL_RE = re.compile(r"\$\d{1,3}[.,]\d{3}[.,]\d{3}")


@pytest.fixture
def gen():
    return V4ProposalGenerator()


class TestDynamicBreachMap:
    """_build_dynamic_breach_map: mapa inverso asset_type → brecha viva del run."""

    def test_mapa_resuelve_5_services_con_costo(self, gen):
        """Los 5 services con brecha en opportunity_scores resuelven costo vivo."""
        result = gen._build_dynamic_breach_map(OPPORTUNITY_SCORES_ZIONE)

        assert result["whatsapp_button"]["brecha_id"] == "whatsapp_conflict"
        assert result["whatsapp_button"]["rank"] == 1
        assert result["whatsapp_button"]["cost"] == 1198906

        assert result["hotel_schema"]["brecha_id"] == "no_hotel_schema"
        assert result["hotel_schema"]["cost"] == 1498094

        assert result["faq_page"]["brecha_id"] == "no_faq_schema"
        assert result["faq_page"]["cost"] == 719200

        assert result["open_graph"]["brecha_id"] == "no_og_tags"
        assert result["open_graph"]["cost"] == 479706

    def test_seo_local_resuelve_low_seo_score(self, gen):
        """N17: optimization_guide → low_seo_score (NO 'Sin Schema Hotel')."""
        result = gen._build_dynamic_breach_map(OPPORTUNITY_SCORES_ZIONE)

        assert result["optimization_guide"]["brecha_id"] == "low_seo_score"
        assert result["optimization_guide"]["rank"] == 4
        assert result["optimization_guide"]["label"] == "SEO Local Bajo"
        assert result["optimization_guide"]["cost"] == 1198906

    def test_org_schema_y_llms_txt_ausentes(self, gen):
        """N19: no_org_schema y missing_llmstxt no están en opportunity_scores."""
        result = gen._build_dynamic_breach_map(OPPORTUNITY_SCORES_ZIONE)

        assert "org_schema" not in result
        assert "llms_txt" not in result

    def test_sin_scores_retorna_vacio(self, gen):
        """Fallback: sin opportunity_scores el mapa queda vacío (sin cifras)."""
        assert gen._build_dynamic_breach_map(None) == {}
        assert gen._build_dynamic_breach_map([]) == {}


class TestServicesTableConsistency:
    """Tabla de servicios: costo/rank/label == opportunity_scores del fixture."""

    def _row(self, table: str, service: str) -> str:
        for line in table.splitlines():
            if service in line:
                return line
        raise AssertionError(f"Servicio '{service}' no aparece en la tabla:\n{table}")

    def test_costos_identicos_a_opportunity_scores(self, gen):
        """Cada service con brecha cita el MISMO costo que opportunity_scores."""
        table = gen._generate_dynamic_services_table(
            assets_generated=ASSETS_GENERATED,
            whatsapp_conflict=True,
            opportunity_scores=OPPORTUNITY_SCORES_ZIONE,
        )

        # WhatsApp: rank vivo 1 (N18 — era hardcode '#5')
        wa_row = self._row(table, "Botón de WhatsApp")
        assert "Brecha #1: Conflicto de WhatsApp ($1.198.906 COP/mes)" in wa_row

        # SEO Local: label vivo 'SEO Local Bajo' (N17 — era 'Sin Schema Hotel')
        seo_row = self._row(table, "SEO Local")
        assert "#4: SEO Local Bajo ($1.198.906 COP/mes)" in seo_row

        # Schema Hotel / FAQ / OG Tags: costos vivos del run
        assert "#2: Sin Schema Hotel ($1.498.094 COP/mes)" in self._row(table, "Schema Hotel")
        assert "#3: Sin Schema FAQ ($719.200 COP/mes)" in self._row(table, "Página de FAQ")
        assert "#8: Open Graph Tags Incompletos ($479.706 COP/mes)" in self._row(
            table, "Meta Tags Sociales (Open Graph)"
        )

    def test_org_schema_sin_cifras_inventadas(self, gen):
        """N19: org_schema generado pero sin brecha en scores → columna '—'."""
        table = gen._generate_dynamic_services_table(
            assets_generated=ASSETS_GENERATED,
            opportunity_scores=OPPORTUNITY_SCORES_ZIONE,
        )

        org_row = self._row(table, "Schema Organization")
        # Columna brecha vacía, sin costo inventado
        assert "| — |" in org_row
        assert not COST_LITERAL_RE.search(org_row)

    def test_llms_txt_sin_cifras_inventadas(self, gen):
        """llms_txt sin brecha en opportunity_scores → sin cifras inventadas."""
        table = gen._generate_dynamic_services_table(
            assets_generated=ASSETS_GENERATED,
            opportunity_scores=OPPORTUNITY_SCORES_ZIONE,
        )

        llms_row = self._row(table, "Optimización para IA Generativa")
        assert not COST_LITERAL_RE.search(llms_row)

    def test_fallback_sin_scores_no_inventa_cifras(self, gen):
        """Fallback explícito: opportunity_scores=None → tabla sin costos."""
        table = gen._generate_dynamic_services_table(
            assets_generated=ASSETS_GENERATED,
            whatsapp_conflict=True,
            opportunity_scores=None,
        )

        # Ninguna cifra de brecha inventada en toda la tabla
        for line in table.splitlines():
            if line.startswith("|") and "---" not in line and "Servicio" not in line:
                assert not COST_LITERAL_RE.search(line), f"Cifra inventada en: {line}"

    def test_whatsapp_conflict_fallback_sin_scores(self, gen):
        """WhatsApp conflict sin scores → label sin rank/costo inventados."""
        table = gen._generate_dynamic_services_table(
            assets_generated=ASSETS_GENERATED,
            whatsapp_conflict=True,
            opportunity_scores=None,
        )

        wa_row = self._row(table, "Botón de WhatsApp")
        assert "Conflicto de WhatsApp (—)" in wa_row
        assert not COST_LITERAL_RE.search(wa_row)
