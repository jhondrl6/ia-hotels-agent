"""
Tests for FASE-PROP-A: Coherence Score Unification.

Verifies:
1. Pipeline timing: CoherenceValidator runs before diagnostic generation
2. External coherence_score is used directly (no fallback)
3. gate_status is passed through to template data
4. Fallback _calculate_coherence_score is never auto-invoked
"""

import pytest
import tempfile
from pathlib import Path

from modules.commercial_documents.v4_diagnostic_generator import (
    V4DiagnosticGenerator,
    _build_excluded_factors_section,
)
from modules.commercial_documents.data_structures import (
    V4AuditResult,
    ValidationSummary,
    ValidatedField,
    FinancialScenarios,
    Scenario,
    SchemaValidation,
    GBPData,
    PerformanceData,
    CrossValidationResult,
    ConfidenceLevel,
)


def _make_minimal_audit() -> V4AuditResult:
    """Create a minimal V4AuditResult for testing."""
    return V4AuditResult(
        url="https://example.com",
        hotel_name="Hotel Test",
        timestamp="2026-01-01T00:00:00",
        schema=SchemaValidation(
            hotel_schema_detected=True,
            hotel_schema_valid=True,
            hotel_confidence="verified",
            faq_schema_detected=True,
            faq_schema_valid=True,
            faq_confidence="verified",
            org_schema_detected=True,
            total_schemas=3,
        ),
        gbp=GBPData(
            place_found=True,
            place_id="ChI123",
            name="Hotel Test",
            rating=4.5,
            reviews=100,
            photos=30,
            phone="+571234567890",
            website="https://example.com",
            address="Calle 123, Ciudad, Colombia",
            geo_score=80,
            geo_score_breakdown={},
            confidence="verified",
        ),
        performance=PerformanceData(
            has_field_data=True,
            mobile_score=85,
            desktop_score=90,
            lcp=1.5,
            fid=20,
            cls=0.05,
            status="ok",
            message="Good performance",
        ),
        validation=CrossValidationResult(
            whatsapp_status="verified",
            phone_web="+571234567890",
            phone_gbp="+571234567890",
            adr_status="verified",
            adr_web=300000.0,
            adr_benchmark=280000.0,
        ),
        overall_confidence="verified",
        critical_issues=[],
        recommendations=[],
    )


def _make_minimal_validation_summary() -> ValidationSummary:
    """Create a minimal ValidationSummary for testing."""
    return ValidationSummary(
        fields=[
            ValidatedField(
                field_name="rooms",
                value=10,
                confidence=ConfidenceLevel.VERIFIED,
                sources=["onboarding"],
            ),
        ],
        overall_confidence=ConfidenceLevel.VERIFIED,
        conflicts=[],
    )


def _make_minimal_financial_scenarios() -> FinancialScenarios:
    """Create minimal FinancialScenarios for testing."""
    base = Scenario(
        monthly_loss_min=1_000_000,
        monthly_loss_max=2_000_000,
        probability=0.7,
        description="Test scenario",
        assumptions=["Assumption 1"],
        confidence_score=0.8,
        monthly_loss_central=1_500_000,
    )
    return FinancialScenarios(
        conservative=base,
        realistic=base,
        optimistic=base,
    )


class TestCoherenceScoreUnification:
    """FASE-PROP-A: coherence_score uses external value, no auto-fallback."""

    def test_external_coherence_score_used_directly(self):
        """When coherence_score=0.72 is passed, template data shows 0.72 (not fallback)."""
        gen = V4DiagnosticGenerator()
        audit = _make_minimal_audit()
        validation = _make_minimal_validation_summary()
        financial = _make_minimal_financial_scenarios()

        template_data = gen._prepare_template_data(
            audit_result=audit,
            validation_summary=validation,
            financial_scenarios=financial,
            hotel_name="Hotel Test",
            hotel_url="https://example.com",
            coherence_score=0.72,
            gate_status="PASSED",
        )

        assert template_data["coherence_score"] == "0.72"
        assert template_data["gate_status"] == "PASSED"

    def test_none_coherence_score_shows_pending(self):
        """When coherence_score is None, template data shows 'PENDIENTE'."""
        gen = V4DiagnosticGenerator()
        audit = _make_minimal_audit()
        validation = _make_minimal_validation_summary()
        financial = _make_minimal_financial_scenarios()

        template_data = gen._prepare_template_data(
            audit_result=audit,
            validation_summary=validation,
            financial_scenarios=financial,
            hotel_name="Hotel Test",
            hotel_url="https://example.com",
            coherence_score=None,
            gate_status=None,
        )

        assert template_data["coherence_score"] == "PENDIENTE"
        assert template_data["gate_status"] == "PENDIENTE"

    def test_zero_coherence_score_shows_pending(self):
        """When coherence_score is 0, template data shows 'PENDIENTE'."""
        gen = V4DiagnosticGenerator()
        audit = _make_minimal_audit()
        validation = _make_minimal_validation_summary()
        financial = _make_minimal_financial_scenarios()

        template_data = gen._prepare_template_data(
            audit_result=audit,
            validation_summary=validation,
            financial_scenarios=financial,
            hotel_name="Hotel Test",
            hotel_url="https://example.com",
            coherence_score=0,
            gate_status="FAILED",
        )

        assert template_data["coherence_score"] == "PENDIENTE"
        assert template_data["gate_status"] == "FAILED"

    def test_fallback_never_auto_invoked(self):
        """_calculate_coherence_score must never be called automatically when score is missing."""
        gen = V4DiagnosticGenerator()
        audit = _make_minimal_audit()
        validation = _make_minimal_validation_summary()
        financial = _make_minimal_financial_scenarios()

        # coherence_score=None should NOT trigger fallback calculation
        template_data = gen._prepare_template_data(
            audit_result=audit,
            validation_summary=validation,
            financial_scenarios=financial,
            hotel_name="Hotel Test",
            hotel_url="https://example.com",
            coherence_score=None,
        )

        # If fallback had run, we'd see ~100 (since our mock has VERIFIED field).
        # Instead we should see "PENDIENTE".
        assert template_data["coherence_score"] == "PENDIENTE"

    def test_generate_accepts_gate_status(self):
        """generate() must accept gate_status parameter."""
        gen = V4DiagnosticGenerator()
        audit = _make_minimal_audit()
        validation = _make_minimal_validation_summary()
        financial = _make_minimal_financial_scenarios()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = gen.generate(
                audit_result=audit,
                validation_summary=validation,
                financial_scenarios=financial,
                hotel_name="Hotel Test",
                hotel_url="https://example.com",
                output_dir=tmpdir,
                coherence_score=0.85,
                gate_status="PASSED",
            )
            assert Path(path).exists()
            content = Path(path).read_text(encoding="utf-8")
            assert "gate_status: PASSED" in content
            assert "coherence_score: 0.85" in content

    def test_generate_with_none_shows_pending(self):
        """generate() without coherence_score must show PENDIENTE in output."""
        gen = V4DiagnosticGenerator()
        audit = _make_minimal_audit()
        validation = _make_minimal_validation_summary()
        financial = _make_minimal_financial_scenarios()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = gen.generate(
                audit_result=audit,
                validation_summary=validation,
                financial_scenarios=financial,
                hotel_name="Hotel Test",
                hotel_url="https://example.com",
                output_dir=tmpdir,
                coherence_score=None,
                gate_status=None,
            )
            assert Path(path).exists()
            content = Path(path).read_text(encoding="utf-8")
            assert "gate_status: PENDIENTE" in content
            assert "coherence_score: PENDIENTE" in content


class TestDeprecatedFallback:
    """Verify _calculate_coherence_score still exists for explicit callers."""

    def test_deprecated_method_exists(self):
        """The method must still exist for backward compatibility."""
        gen = V4DiagnosticGenerator()
        validation = _make_minimal_validation_summary()
        score = gen._calculate_coherence_score(validation)
        assert isinstance(score, int)
        # With 1 VERIFIED field, score should be 100
        assert score == 100


# ── FASE-A: IA-Readiness Critical Advisory Alert Tests ──────────────────────────────────────────

class TestIAReadinessAdvisoryAlert:
    """Tests for IA-Readiness Critical warning in diagnostic (FASE-A)."""

    def test_ia_critical_shows_alert(self):
        """IA-Readiness Critical → alert blockquote appears in output."""
        from modules.auditors.ia_readiness_calculator import IAReadinessReport
        gen = V4DiagnosticGenerator()
        audit = _make_minimal_audit()
        validation = _make_minimal_validation_summary()
        financial = _make_minimal_financial_scenarios()

        # Inject IAReadinessReport with Critical status
        ia_report = IAReadinessReport(
            overall_score=35.0,
            components={
                "schema_quality": 30.0,
                "crawler_access": 40.0,
                "citability": 35.0,
                "llms_txt": 0,
                "brand_signals": 40.0,
            },
            status="Critical",
            actionable_items=["Improve schema quality", "Fix crawler access"],
        )
        # Attach ia_readiness to the audit object
        audit = dataclass_replace(audit, ia_readiness=ia_report)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = gen.generate(
                audit_result=audit,
                validation_summary=validation,
                financial_scenarios=financial,
                hotel_name="Hotel Test",
                hotel_url="https://example.com",
                output_dir=tmpdir,
                coherence_score=0.85,
            )
            content = Path(path).read_text(encoding="utf-8")
            assert "Alerta IA-Readiness Critical" in content
            assert "objetivo comercial" in content.lower()

    def test_ia_ready_no_alert(self):
        """IA-Readiness Ready → NO alert blockquote."""
        from modules.auditors.ia_readiness_calculator import IAReadinessReport

        gen = V4DiagnosticGenerator()
        audit = _make_minimal_audit()
        validation = _make_minimal_validation_summary()
        financial = _make_minimal_financial_scenarios()

        ia_report = IAReadinessReport(
            overall_score=78.0,
            components={
                "schema_quality": 80.0,
                "crawler_access": 75.0,
                "citability": 78.0,
                "llms_txt": 100,
                "brand_signals": 70.0,
            },
            status="Ready",
            actionable_items=[],
        )
        audit = dataclass_replace(audit, ia_readiness=ia_report)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = gen.generate(
                audit_result=audit,
                validation_summary=validation,
                financial_scenarios=financial,
                hotel_name="Hotel Test",
                hotel_url="https://example.com",
                output_dir=tmpdir,
                coherence_score=0.85,
            )
            content = Path(path).read_text(encoding="utf-8")
            assert "Alerta IA-Readiness Critical" not in content

    def test_ia_needs_work_no_alert(self):
        """IA-Readiness Needs Work → NO alert blockquote (only Critical triggers)."""
        from modules.auditors.ia_readiness_calculator import IAReadinessReport

        gen = V4DiagnosticGenerator()
        audit = _make_minimal_audit()
        validation = _make_minimal_validation_summary()
        financial = _make_minimal_financial_scenarios()

        ia_report = IAReadinessReport(
            overall_score=55.0,
            components={
                "schema_quality": 50.0,
                "crawler_access": 55.0,
                "citability": 60.0,
                "llms_txt": 100,
                "brand_signals": 50.0,
            },
            status="Needs Work",
            actionable_items=["Improve schema quality"],
        )
        audit = dataclass_replace(audit, ia_readiness=ia_report)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = gen.generate(
                audit_result=audit,
                validation_summary=validation,
                financial_scenarios=financial,
                hotel_name="Hotel Test",
                hotel_url="https://example.com",
                output_dir=tmpdir,
                coherence_score=0.85,
            )
            content = Path(path).read_text(encoding="utf-8")
            assert "Alerta IA-Readiness Critical" not in content


class TestWhatsappConflictNote:
    """FASE-A-02b: Tests for _build_whatsapp_conflict_note."""

    def test_whatsapp_conflict_note_generated(self):
        """With whatsapp conflict in validation.conflicts → note not empty."""
        gen = V4DiagnosticGenerator()

        # Build audit with whatsapp conflict in validation.conflicts
        audit = V4AuditResult(
            url="https://hotel-test.com",
            hotel_name="Hotel Test",
            timestamp="2026-01-01T00:00:00",
            schema=SchemaValidation(
                hotel_schema_detected=True,
                hotel_schema_valid=True,
                hotel_confidence="verified",
                faq_schema_detected=True,
                faq_schema_valid=True,
                faq_confidence="verified",
                org_schema_detected=True,
                total_schemas=3,
            ),
            gbp=GBPData(
                place_found=True,
                place_id="ChI123",
                name="Hotel Test",
                rating=4.5,
                reviews=100,
                photos=30,
                phone="+573001234567",
                website="https://hotel-test.com",
                address="Calle 123, Armenia, Quindío",
                geo_score=80,
                geo_score_breakdown={},
                confidence="verified",
            ),
            performance=PerformanceData(
                has_field_data=True,
                mobile_score=85,
                desktop_score=90,
                lcp=1.5,
                fid=20,
                cls=0.05,
                status="ok",
                message="Good performance",
            ),
            validation=CrossValidationResult(
                whatsapp_status="conflict",
                phone_web="+573001111111",
                phone_gbp="+573002222222",
                adr_status="verified",
                adr_web=300000.0,
                adr_benchmark=280000.0,
                conflicts=[
                    {"field_name": "whatsapp", "value": "conflict", "discrepancies": "phone_web vs phone_gbp"},
                ],
            ),
            overall_confidence="verified",
            critical_issues=[],
            recommendations=[],
        )

        note = gen._build_whatsapp_conflict_note(audit)

        # Should NOT be empty when conflict exists
        assert note != ""
        # Should contain the phone numbers
        assert "+573001111111" in note
        assert "+573002222222" in note
        # Should contain the business impact phrasing
        assert "ALERTA" in note
        assert "número equivocado" in note.lower()

    def test_whatsapp_conflict_note_empty_no_conflict(self):
        """Without whatsapp conflict in validation.conflicts → note empty."""
        gen = V4DiagnosticGenerator()

        # Audit with no whatsapp conflict (different field conflict only)
        audit = V4AuditResult(
            url="https://hotel-test.com",
            hotel_name="Hotel Test",
            timestamp="2026-01-01T00:00:00",
            schema=SchemaValidation(
                hotel_schema_detected=True,
                hotel_schema_valid=True,
                hotel_confidence="verified",
                faq_schema_detected=True,
                faq_schema_valid=True,
                faq_confidence="verified",
                org_schema_detected=True,
                total_schemas=3,
            ),
            gbp=GBPData(
                place_found=True,
                place_id="ChI123",
                name="Hotel Test",
                rating=4.5,
                reviews=100,
                photos=30,
                phone="+573001234567",
                website="https://hotel-test.com",
                address="Calle 123, Armenia, Quindío",
                geo_score=80,
                geo_score_breakdown={},
                confidence="verified",
            ),
            performance=PerformanceData(
                has_field_data=True,
                mobile_score=85,
                desktop_score=90,
                lcp=1.5,
                fid=20,
                cls=0.05,
                status="ok",
                message="Good performance",
            ),
            validation=CrossValidationResult(
                whatsapp_status="conflict",
                phone_web=None,  # Missing phone_web → note should be empty
                phone_gbp="+573002222222",
                adr_status="verified",
                adr_web=300000.0,
                adr_benchmark=280000.0,
                conflicts=[
                    {"field_name": "whatsapp", "value": "conflict", "discrepancies": "phone_web vs phone_gbp"},
                ],
            ),
            overall_confidence="verified",
            critical_issues=[],
            recommendations=[],
        )

        note = gen._build_whatsapp_conflict_note(audit)

        # Should be empty when no whatsapp conflict
        assert note == ""

    def test_whatsapp_conflict_note_empty_no_validation(self):
        """Without whatsapp conflict → note empty (safe fallback)."""
        gen = V4DiagnosticGenerator()

        # Audit with whatsapp_status=conflict but NO whatsapp in conflicts list
        audit = V4AuditResult(
            url="https://hotel-test.com",
            hotel_name="Hotel Test",
            timestamp="2026-01-01T00:00:00",
            schema=SchemaValidation(
                hotel_schema_detected=True,
                hotel_schema_valid=True,
                hotel_confidence="verified",
                faq_schema_detected=True,
                faq_schema_valid=True,
                faq_confidence="verified",
                org_schema_detected=True,
                total_schemas=3,
            ),
            gbp=GBPData(
                place_found=True,
                place_id="ChI123",
                name="Hotel Test",
                rating=4.5,
                reviews=100,
                photos=30,
                phone="+573001234567",
                website="https://hotel-test.com",
                address="Calle 123, Armenia, Quindío",
                geo_score=80,
                geo_score_breakdown={},
                confidence="verified",
            ),
            performance=PerformanceData(
                has_field_data=True,
                mobile_score=85,
                desktop_score=90,
                lcp=1.5,
                fid=20,
                cls=0.05,
                status="ok",
                message="Good performance",
            ),
            # whatsapp_status=conflict BUT no whatsapp conflict in conflicts list
            validation=CrossValidationResult(
                whatsapp_status="conflict",
                phone_web="+573001111111",
                phone_gbp="+573002222222",
                adr_status="verified",
                adr_web=300000.0,
                adr_benchmark=280000.0,
                conflicts=[
                    {"field_name": "email", "value": "conflict", "discrepancies": "different email"},
                ],
            ),
            overall_confidence="verified",
            critical_issues=[],
            recommendations=[],
        )

        note = gen._build_whatsapp_conflict_note(audit)

        # Should be empty when no whatsapp conflict in the list
        assert note == ""


def dataclass_replace(obj, **kwargs):
    """Create a copy of a dataclass with updated fields."""
    from dataclasses import replace
    return replace(obj, **kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# FASE-C-B: Tests para D6 (performance dinámico), D7 (reviews), D8 (atribución GEO)
# ──────────────────────────────────────────────────────────────────────────────


class TestD6PerformanceStatusDinamico:
    """D6: el texto de performance refleja el status real de la API."""

    def test_d6_error_status_muestra_mensaje_api(self):
        """Con performance.status=ERROR, el doc refleja el mensaje de error."""
        gen = V4DiagnosticGenerator()
        audit = _make_minimal_audit()
        audit = dataclass_replace(
            audit,
            performance=PerformanceData(
                has_field_data=False,
                mobile_score=None,
                desktop_score=None,
                lcp=None,
                fid=None,
                cls=None,
                status="ERROR",
                message="API key not valid",
            ),
        )

        result = gen._build_manual_attention_table(audit)

        assert "API key not valid" in result
        assert "🔴 Alta" in result
        # El texto genérico NO debe aparecer
        assert "El sitio puede ser nuevo" not in result

    def test_d6_ok_sin_field_data_muestra_generico(self):
        """Con status OK pero sin field data, muestra texto genérico (amarillo)."""
        gen = V4DiagnosticGenerator()
        audit = _make_minimal_audit()
        audit = dataclass_replace(
            audit,
            performance=PerformanceData(
                has_field_data=False,
                mobile_score=None,
                desktop_score=None,
                lcp=None,
                fid=None,
                cls=None,
                status="ok",
                message="Success",
            ),
        )

        result = gen._build_manual_attention_table(audit)

        assert "El sitio puede ser nuevo o tener tráfico bajo" in result
        assert "🟡 Media" in result
        # NO debe mostrar mensaje de error
        assert "API key not valid" not in result

    def test_d6_con_field_data_no_agrega_fila(self):
        """Con field data disponible, no se agrega fila de performance."""
        gen = V4DiagnosticGenerator()
        audit = _make_minimal_audit()
        # audit ya tiene has_field_data=True por defecto

        result = gen._build_manual_attention_table(audit)

        assert "Sin Datos de Campo" not in result
        assert "Core Web Vitals" not in result


class TestD7ReviewsParametrizadas:
    """D7: el ejemplo de reseñas usa el conteo real del audit, no '203'."""

    def test_d7_con_reviews_count_real(self):
        """Con reviews_count=966, el texto muestra '966 reseñas'."""
        result = _build_excluded_factors_section(reviews_count=966)

        assert "966 reseñas" in result
        assert "203" not in result

    def test_d7_sin_reviews_count_usa_generico(self):
        """Sin reviews_count (None), usa texto genérico sin número."""
        result = _build_excluded_factors_section()

        assert "un hotel con muchas reseñas" in result
        assert "203" not in result

    def test_d7_reviews_count_cero(self):
        """Con reviews_count=0, muestra '0 reseñas' (dato real)."""
        result = _build_excluded_factors_section(reviews_count=0)

        assert "0 reseñas" in result
        assert "203" not in result


class TestD8AtribucionGEO:
    """D8: el template atribuye el GEO score a iah-cli, no a Google."""

    def test_d8_template_sin_algoritmo_de_google(self):
        """El template no contiene 'algoritmo propio de Google' ni 'algoritmo de Google'."""
        template_path = (
            Path(__file__).parent.parent.parent
            / "modules"
            / "commercial_documents"
            / "templates"
            / "diagnostico_v6_template.md"
        )
        content = template_path.read_text(encoding="utf-8")

        assert "algoritmo propio de Google" not in content
        assert "algoritmo de Google" not in content

    def test_d8_template_con_atribucion_iah_cli(self):
        """El template contiene la atribución correcta a IA Hoteles Agent."""
        template_path = (
            Path(__file__).parent.parent.parent
            / "modules"
            / "commercial_documents"
            / "templates"
            / "diagnostico_v6_template.md"
        )
        content = template_path.read_text(encoding="utf-8")

        assert "algoritmo propio de IA Hoteles Agent" in content
        assert "Google Places" in content


class TestB2QuickWinSchemaText:
    """B2: Quick Win para not hotel_schema_detected menciona datos/Schema, no WhatsApp."""

    def test_quick_wins_schema_text_sin_schema(self):
        """Con hotel_schema_detected=False, el Quick Win menciona datos/Google, no WhatsApp."""
        gen = V4DiagnosticGenerator()
        audit = _make_minimal_audit()
        audit = dataclass_replace(
            audit,
            schema=SchemaValidation(
                hotel_schema_detected=False,
                hotel_schema_valid=False,
                hotel_confidence="missing",
                faq_schema_detected=True,
                faq_schema_valid=True,
                faq_confidence="verified",
                org_schema_detected=True,
                total_schemas=2,
            ),
        )

        result = gen._build_quick_wins(audit)

        # Assert 1: NO contiene mención de WhatsApp
        assert "WhatsApp" not in result
        # Assert 2: menciona Google y/o datos (correspondencia con condición Schema)
        assert "Google" in result or "datos" in result

    def test_quick_wins_schema_no_aparece_con_schema_detectado(self):
        """Con hotel_schema_detected=True, el Quick Win de Schema NO aparece."""
        gen = V4DiagnosticGenerator()
        audit = _make_minimal_audit()
        # _make_minimal_audit() ya tiene hotel_schema_detected=True

        result = gen._build_quick_wins(audit)

        # El texto de verificación de datos en Google no debe aparecer
        assert "Verificar qué datos de su hotel faltan en Google" not in result


# ────────────────────────────────────────────────────────────────────────────
# FUGAS-WHATSAPP (FASE-R0-B, B1+B4): Sección 4 dinámica desde pain_ledger
# ────────────────────────────────────────────────────────────────────────────


def _make_zione_like_audit(geo_score: int = 45) -> V4AuditResult:
    """Audit tipo Zione: WhatsApp VERIFIED + brechas reales (schema/GBP/FAQ/org)."""
    audit = _make_minimal_audit()
    return dataclass_replace(
        audit,
        schema=SchemaValidation(
            hotel_schema_detected=False,
            hotel_schema_valid=False,
            hotel_confidence="missing",
            faq_schema_detected=False,
            faq_schema_valid=False,
            faq_confidence="missing",
            org_schema_detected=False,
            total_schemas=0,
        ),
        gbp=dataclass_replace(audit.gbp, geo_score=geo_score),
        validation=dataclass_replace(
            audit.validation,
            whatsapp_status="verified",
            phone_web="+573001111111",
            phone_gbp="+573001111111",
        ),
    )


def _make_validation_with_whatsapp(confidence: ConfidenceLevel) -> ValidationSummary:
    """ValidationSummary con campo whatsapp_number en el nivel de confianza dado."""
    return ValidationSummary(
        fields=[
            ValidatedField(
                field_name="whatsapp_number",
                value="+573001111111",
                confidence=confidence,
                sources=["web", "gbp"],
            ),
        ],
        overall_confidence=confidence,
        conflicts=[],
    )


class TestFugasPrincipalesDinamicas:
    """FASE-R0-B (B1+B4): la Sección 4 se deriva del pain_ledger, no de texto estático."""

    def test_fugas_principales_sin_whatsapp_conflict(self):
        """AC1: con WhatsApp VERIFIED no aparece la fuga estática de WhatsApp."""
        gen = V4DiagnosticGenerator()
        audit = _make_zione_like_audit()
        validation = _make_validation_with_whatsapp(ConfidenceLevel.VERIFIED)
        financial = _make_minimal_financial_scenarios()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = gen.generate(
                audit_result=audit,
                validation_summary=validation,
                financial_scenarios=financial,
                hotel_name="Hotel Test",
                hotel_url="https://example.com",
                output_dir=tmpdir,
                coherence_score=0.85,
                gate_status="PASSED",
            )
            content = Path(path).read_text(encoding="utf-8")

        # AC1: la narrativa estática fosilizada desapareció del output
        assert "Contacto perdido por WhatsApp" not in content
        assert "WhatsApp incorrecto" not in content
        # Guard anti-residuos (safe_substitute): 0 variables sin renderizar
        assert "${" not in content
        # Contiene al menos una fuga derivada de un pain real del audit
        assert "### Fuga 1 —" in content
        # FASE-SR-G (L27/L-SR3): el texto publicado pasa por el glosario único —
        # pain.name "Sin Schema Hotel" (no_hotel_schema) se publica como lenguaje
        # de negocio; la jerga cruda NO aparece al cliente.
        assert "Sin Ficha del Hotel en Google e IA" in content
        assert "Sin Schema Hotel" not in content

    def test_fugas_principales_con_whatsapp_conflict(self):
        """AC4: con conflicto real, la fuga de WhatsApp SÍ aparece (derivada del pain)."""
        gen = V4DiagnosticGenerator()
        audit = _make_zione_like_audit()
        validation = _make_validation_with_whatsapp(ConfidenceLevel.CONFLICT)
        financial = _make_minimal_financial_scenarios()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = gen.generate(
                audit_result=audit,
                validation_summary=validation,
                financial_scenarios=financial,
                hotel_name="Hotel Test",
                hotel_url="https://example.com",
                output_dir=tmpdir,
                coherence_score=0.85,
                gate_status="PASSED",
            )
            content = Path(path).read_text(encoding="utf-8")

        # La fuga aparece con el nombre dinámico del pain (pain.name del mapper),
        # NO con el string estático eliminado
        fuga_lines = [ln for ln in content.splitlines() if ln.startswith("### Fuga")]
        assert any("Conflicto de WhatsApp" in ln for ln in fuga_lines)
        assert "Contacto perdido por WhatsApp incorrecto" not in content

    def test_fugas_count_matches_brechas(self):
        """AC9/D-NC1: el contador del título coincide con las fugas listadas."""
        gen = V4DiagnosticGenerator()
        audit = _make_zione_like_audit()
        validation = _make_validation_with_whatsapp(ConfidenceLevel.VERIFIED)
        financial = _make_minimal_financial_scenarios()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = gen.generate(
                audit_result=audit,
                validation_summary=validation,
                financial_scenarios=financial,
                hotel_name="Hotel Test",
                hotel_url="https://example.com",
                output_dir=tmpdir,
                coherence_score=0.85,
                gate_status="PASSED",
            )
            content = Path(path).read_text(encoding="utf-8")

        n = content.count("### Fuga ")
        assert n > 0
        # Título dinámico coincide con las fugas listadas…
        assert f"LAS {n} FUGAS PRINCIPALES" in content
        # …y con el contador ${brechas_destacadas_count} de la intro
        assert f"estas {n} son las que más dinero" in content

    def test_fugas_derivan_de_pain_ids(self):
        """AC3: cada fuga listada corresponde 1:1 a una brecha real del ledger."""
        import re

        gen = V4DiagnosticGenerator()
        audit = _make_zione_like_audit()
        validation = _make_validation_with_whatsapp(ConfidenceLevel.VERIFIED)
        financial = _make_minimal_financial_scenarios()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = gen.generate(
                audit_result=audit,
                validation_summary=validation,
                financial_scenarios=financial,
                hotel_name="Hotel Test",
                hotel_url="https://example.com",
                output_dir=tmpdir,
                coherence_score=0.85,
                gate_status="PASSED",
            )
            content = Path(path).read_text(encoding="utf-8")

        # Nombres renderizados en la Sección 4
        rendered_names = re.findall(r"### Fuga \d+ — (.+)", content)
        assert rendered_names, "La Sección 4 debe listar al menos una fuga"

        # Brechas destacadas según la misma fuente de verdad del generador.
        # FASE-SR-G (L27): el texto publicado es la fuente interna pasada por el
        # glosario único — la comparación aplica la MISMA transformación compartida
        # (nunca nombres hardcodeados en dos sitios).
        from modules.commercial_documents.tech_jargon_glossary import apply_glossary

        brechas_destacadas = [
            b for b in gen._get_brecha_pesos(audit) if b.get("impacto", 0) > 0
        ]
        expected_names = [apply_glossary(b["nombre"]) for b in brechas_destacadas]

        assert sorted(rendered_names) == sorted(expected_names)
        assert "Contacto perdido por WhatsApp incorrecto" not in rendered_names
