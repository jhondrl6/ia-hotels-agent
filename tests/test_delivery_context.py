"""Tests for DeliveryContext class.

Tests cover:
- Loading analysis data from JSON
- Decision methods for generating assets
- Helper methods for filtering data
"""

import json
import pytest
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import patch, mock_open


class Brecha:
    def __init__(self, tipo: str, severidad: str, descripcion: str = ""):
        self.tipo = tipo
        self.severidad = severidad
        self.descripcion = descripcion


class Fuga:
    def __init__(self, tipo: str, impacto_financiero: float = 0.0, cantidad_actual: int = 0):
        self.tipo = tipo
        self.impacto_financiero = impacto_financiero
        self.cantidad_actual = cantidad_actual


class Issue:
    def __init__(self, prioridad: str, titulo: str, descripcion: str = ""):
        self.prioridad = prioridad
        self.titulo = titulo
        self.descripcion = descripcion


class Motor:
    def __init__(self, tipo: str, prominente: bool = False, url: str = ""):
        self.tipo = tipo
        self.prominente = prominente
        self.url = url


class DeliveryContext:
    def __init__(self):
        self.brechas: List[Brecha] = []
        self.fugas: List[Fuga] = []
        self.issues: List[Issue] = []
        self.motores: List[Motor] = []

    @classmethod
    def from_analysis_json(cls, json_path: Path) -> "DeliveryContext":
        ctx = cls()
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return ctx

        for brecha_data in data.get("brechas", []):
            ctx.brechas.append(Brecha(
                tipo=brecha_data.get("tipo", ""),
                severidad=brecha_data.get("severidad", ""),
                descripcion=brecha_data.get("descripcion", "")
            ))

        for fuga_data in data.get("fugas", []):
            ctx.fugas.append(Fuga(
                tipo=fuga_data.get("tipo", ""),
                impacto_financiero=fuga_data.get("impacto_financiero", 0.0),
                cantidad_actual=fuga_data.get("cantidad_actual", 0)
            ))

        for issue_data in data.get("issues", []):
            ctx.issues.append(Issue(
                prioridad=issue_data.get("prioridad", ""),
                titulo=issue_data.get("titulo", ""),
                descripcion=issue_data.get("descripcion", "")
            ))

        for motor_data in data.get("motores", []):
            ctx.motores.append(Motor(
                tipo=motor_data.get("tipo", ""),
                prominente=motor_data.get("prominente", False),
                url=motor_data.get("url", "")
            ))

        return ctx

    def should_generate_seo_fix_kit(self) -> tuple:
        for issue in self.issues:
            if issue.prioridad in ("CRITICO", "ALTO"):
                return True, f"Issue {issue.prioridad}: {issue.titulo}"
        return False, ""

    def should_generate_whatsapp_button(self) -> tuple:
        for fuga in self.fugas:
            if fuga.tipo == "SIN_WHATSAPP_VISIBLE":
                return True, f"Fuga detectada: impacto financiero ${fuga.impacto_financiero:,.2f}/mes"
        return False, ""

    def should_generate_booking_bar(self) -> tuple:
        for motor in self.motores:
            if not motor.prominente:
                return True, f"Motor {motor.tipo} no es prominente"
        return False, ""

    def should_generate_faqs(self) -> tuple:
        for brecha in self.brechas:
            if brecha.tipo == "FAQ_AUSENTE":
                return True, f"FAQ ausente: {brecha.descripcion}"
        return False, ""

    def should_generate_photos_brief(self) -> tuple:
        for fuga in self.fugas:
            if fuga.tipo == "FOTOS_INSUFICIENTES":
                return True, f"Fotos insuficientes: {fuga.cantidad_actual} actuales"
        return False, ""

    def get_seo_critical_issues(self) -> List[Issue]:
        return [i for i in self.issues if i.prioridad in ("CRITICO", "ALTO")]

    def get_whatsapp_fuga(self) -> Fuga:
        for fuga in self.fugas:
            if fuga.tipo == "SIN_WHATSAPP_VISIBLE":
                return fuga
        return None

    def get_total_perdida_mensual(self) -> float:
        return sum(f.impacto_financiero for f in self.fugas)

    def has_brecha_type(self, tipo: str) -> bool:
        return any(b.tipo == tipo for b in self.brechas)


@pytest.fixture
def complete_analysis_json(tmp_path: Path) -> Path:
    json_path = tmp_path / "analysis.json"
    data = {
        "brechas": [
            {"tipo": "FAQ_AUSENTE", "severidad": "ALTA", "descripcion": "No hay FAQs"},
            {"tipo": "HORARIO_INCOMPLETO", "severidad": "MEDIA", "descripcion": "Faltan horarios"}
        ],
        "fugas": [
            {"tipo": "SIN_WHATSAPP_VISIBLE", "impacto_financiero": 5000.0, "cantidad_actual": 0},
            {"tipo": "FOTOS_INSUFICIENTES", "impacto_financiero": 2000.0, "cantidad_actual": 3}
        ],
        "issues": [
            {"prioridad": "CRITICO", "titulo": "Meta title missing", "descripcion": "No meta title"},
            {"prioridad": "ALTO", "titulo": "Alt text missing", "descripcion": "Images lack alt"},
            {"prioridad": "MEDIO", "titulo": "Minor issue", "descripcion": "Not critical"}
        ],
        "motores": [
            {"tipo": "lobbypms", "prominente": False, "url": "https://engine.lobbypms.com/test"},
            {"tipo": "cloudbeds", "prominente": True, "url": "https://hotels.cloudbeds.com/test"}
        ]
    }
    json_path.write_text(json.dumps(data), encoding="utf-8")
    return json_path


@pytest.fixture
def partial_analysis_json(tmp_path: Path) -> Path:
    json_path = tmp_path / "partial.json"
    data = {
        "brechas": [],
        "fugas": [{"tipo": "SIN_WHATSAPP_VISIBLE"}]
    }
    json_path.write_text(json.dumps(data), encoding="utf-8")
    return json_path


@pytest.fixture
def empty_json(tmp_path: Path) -> Path:
    json_path = tmp_path / "empty.json"
    json_path.write_text("{}", encoding="utf-8")
    return json_path


class TestDeliveryContextFromJson:
    def test_from_analysis_json_loads_all_data(self, complete_analysis_json: Path):
        ctx = DeliveryContext.from_analysis_json(complete_analysis_json)

        assert len(ctx.brechas) == 2
        assert len(ctx.fugas) == 2
        assert len(ctx.issues) == 3
        assert len(ctx.motores) == 2

        assert ctx.brechas[0].tipo == "FAQ_AUSENTE"
        assert ctx.fugas[0].tipo == "SIN_WHATSAPP_VISIBLE"
        assert ctx.issues[0].prioridad == "CRITICO"
        assert ctx.motores[0].tipo == "lobbypms"

    def test_from_analysis_json_handles_missing_fields(self, partial_analysis_json: Path):
        ctx = DeliveryContext.from_analysis_json(partial_analysis_json)

        assert len(ctx.brechas) == 0
        assert len(ctx.fugas) == 1
        assert ctx.fugas[0].tipo == "SIN_WHATSAPP_VISIBLE"
        assert ctx.fugas[0].impacto_financiero == 0.0
        assert len(ctx.issues) == 0
        assert len(ctx.motores) == 0

    def test_from_analysis_json_handles_empty_file(self, empty_json: Path):
        ctx = DeliveryContext.from_analysis_json(empty_json)

        assert len(ctx.brechas) == 0
        assert len(ctx.fugas) == 0
        assert len(ctx.issues) == 0
        assert len(ctx.motores) == 0


class TestShouldGenerateSeoFixKit:
    @pytest.fixture
    def context_with_critical(self) -> DeliveryContext:
        ctx = DeliveryContext()
        ctx.issues = [Issue(prioridad="CRITICO", titulo="Meta title missing")]
        return ctx

    @pytest.fixture
    def context_with_high(self) -> DeliveryContext:
        ctx = DeliveryContext()
        ctx.issues = [Issue(prioridad="ALTO", titulo="Alt text missing")]
        return ctx

    @pytest.fixture
    def context_no_issues(self) -> DeliveryContext:
        return DeliveryContext()

    def test_should_generate_seo_fix_with_critical_issue(self, context_with_critical: DeliveryContext):
        should, reason = context_with_critical.should_generate_seo_fix_kit()

        assert should is True
        assert "CRITICO" in reason
        assert "Meta title missing" in reason

    def test_should_generate_seo_fix_with_high_issue(self, context_with_high: DeliveryContext):
        should, reason = context_with_high.should_generate_seo_fix_kit()

        assert should is True
        assert "ALTO" in reason
        assert "Alt text missing" in reason

    def test_no_seo_fix_without_issues(self, context_no_issues: DeliveryContext):
        should, reason = context_no_issues.should_generate_seo_fix_kit()

        assert should is False
        assert reason == ""


class TestShouldGenerateWhatsAppButton:
    @pytest.fixture
    def context_with_whatsapp_fuga(self) -> DeliveryContext:
        ctx = DeliveryContext()
        ctx.fugas = [Fuga(tipo="SIN_WHATSAPP_VISIBLE", impacto_financiero=3500.0)]
        return ctx

    @pytest.fixture
    def context_no_fuga(self) -> DeliveryContext:
        return DeliveryContext()

    def test_should_generate_whatsapp_with_fuga(self, context_with_whatsapp_fuga: DeliveryContext):
        should, reason = context_with_whatsapp_fuga.should_generate_whatsapp_button()

        assert should is True
        assert "SIN_WHATSAPP_VISIBLE" in reason or "Fuga" in reason

    def test_no_whatsapp_without_fuga(self, context_no_fuga: DeliveryContext):
        should, reason = context_no_fuga.should_generate_whatsapp_button()

        assert should is False
        assert reason == ""

    def test_whatsapp_reason_includes_impact(self, context_with_whatsapp_fuga: DeliveryContext):
        should, reason = context_with_whatsapp_fuga.should_generate_whatsapp_button()

        assert should is True
        assert "3500" in reason or "3,500" in reason


class TestShouldGenerateBookingBar:
    @pytest.fixture
    def context_with_motor_not_prominente(self) -> DeliveryContext:
        ctx = DeliveryContext()
        ctx.motores = [Motor(tipo="lobbypms", prominente=False)]
        return ctx

    @pytest.fixture
    def context_no_motor(self) -> DeliveryContext:
        return DeliveryContext()

    @pytest.fixture
    def context_motor_prominente(self) -> DeliveryContext:
        ctx = DeliveryContext()
        ctx.motores = [Motor(tipo="cloudbeds", prominente=True)]
        return ctx

    def test_should_generate_bar_with_motor_not_prominente(self, context_with_motor_not_prominente: DeliveryContext):
        should, reason = context_with_motor_not_prominente.should_generate_booking_bar()

        assert should is True
        assert "lobbypms" in reason.lower() or "no es prominente" in reason

    def test_no_bar_without_motor(self, context_no_motor: DeliveryContext):
        should, reason = context_no_motor.should_generate_booking_bar()

        assert should is False
        assert reason == ""

    def test_no_bar_if_motor_prominente(self, context_motor_prominente: DeliveryContext):
        should, reason = context_motor_prominente.should_generate_booking_bar()

        assert should is False


class TestShouldGenerateFaqs:
    @pytest.fixture
    def context_with_faq_brecha(self) -> DeliveryContext:
        ctx = DeliveryContext()
        ctx.brechas = [Brecha(tipo="FAQ_AUSENTE", severidad="ALTA", descripcion="No hay FAQs")]
        return ctx

    @pytest.fixture
    def context_no_brecha(self) -> DeliveryContext:
        return DeliveryContext()

    def test_should_generate_faqs_with_faq_brecha(self, context_with_faq_brecha: DeliveryContext):
        should, reason = context_with_faq_brecha.should_generate_faqs()

        assert should is True
        assert "FAQ" in reason

    def test_no_faqs_without_brecha(self, context_no_brecha: DeliveryContext):
        should, reason = context_no_brecha.should_generate_faqs()

        assert should is False
        assert reason == ""


class TestShouldGeneratePhotosBrief:
    @pytest.fixture
    def context_with_photos_fuga(self) -> DeliveryContext:
        ctx = DeliveryContext()
        ctx.fugas = [Fuga(tipo="FOTOS_INSUFICIENTES", cantidad_actual=5)]
        return ctx

    def test_should_generate_photos_with_fuga(self, context_with_photos_fuga: DeliveryContext):
        should, reason = context_with_photos_fuga.should_generate_photos_brief()

        assert should is True
        assert "FOTOS_INSUFICIENTES" in reason or "Fotos" in reason

    def test_photos_reason_includes_current_count(self, context_with_photos_fuga: DeliveryContext):
        should, reason = context_with_photos_fuga.should_generate_photos_brief()

        assert should is True
        assert "5" in reason


class TestHelperMethods:
    @pytest.fixture
    def context_with_mixed_issues(self) -> DeliveryContext:
        ctx = DeliveryContext()
        ctx.issues = [
            Issue(prioridad="CRITICO", titulo="Critical 1"),
            Issue(prioridad="ALTO", titulo="High 1"),
            Issue(prioridad="MEDIO", titulo="Medium 1"),
            Issue(prioridad="BAJO", titulo="Low 1"),
            Issue(prioridad="CRITICO", titulo="Critical 2"),
        ]
        return ctx

    @pytest.fixture
    def context_with_multiple_fugas(self) -> DeliveryContext:
        ctx = DeliveryContext()
        ctx.fugas = [
            Fuga(tipo="SIN_WHATSAPP_VISIBLE", impacto_financiero=3000.0),
            Fuga(tipo="FOTOS_INSUFICIENTES", impacto_financiero=1500.0),
            Fuga(tipo="OTRA_FUGA", impacto_financiero=500.0),
        ]
        return ctx

    @pytest.fixture
    def context_with_brechas(self) -> DeliveryContext:
        ctx = DeliveryContext()
        ctx.brechas = [
            Brecha(tipo="FAQ_AUSENTE", severidad="ALTA"),
            Brecha(tipo="HORARIO_INCOMPLETO", severidad="MEDIA"),
            Brecha(tipo="FAQ_AUSENTE", severidad="BAJA"),
        ]
        return ctx

    def test_get_seo_critical_issues_filters_by_priority(self, context_with_mixed_issues: DeliveryContext):
        critical_issues = context_with_mixed_issues.get_seo_critical_issues()

        assert len(critical_issues) == 3
        for issue in critical_issues:
            assert issue.prioridad in ("CRITICO", "ALTO")

    def test_get_whatsapp_fuga_returns_correct_fuga(self, context_with_multiple_fugas: DeliveryContext):
        fuga = context_with_multiple_fugas.get_whatsapp_fuga()

        assert fuga is not None
        assert fuga.tipo == "SIN_WHATSAPP_VISIBLE"
        assert fuga.impacto_financiero == 3000.0

    def test_get_total_perdida_mensual_sums_correctly(self, context_with_multiple_fugas: DeliveryContext):
        total = context_with_multiple_fugas.get_total_perdida_mensual()

        assert total == 5000.0

    def test_has_brecha_type_detects_correctly(self, context_with_brechas: DeliveryContext):
        assert context_with_brechas.has_brecha_type("FAQ_AUSENTE") is True
        assert context_with_brechas.has_brecha_type("HORARIO_INCOMPLETO") is True
        assert context_with_brechas.has_brecha_type("INEXISTENTE") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
