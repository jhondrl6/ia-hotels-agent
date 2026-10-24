"""Diente de frontera AC3 — contrato GBP único en los dos caminos (FASE-D).

POR QUÉ EXISTE (D28, DA-PLAN-9)
`get_detected_issues` exigía claves en inglés (`claimed`, `photos`,
`has_whatsapp`, `has_hours`) que `_base_profile()` de `gbp_auditor` nunca
escribe: sobre un perfil PERFECTO devolvía 6 brechas incondicionales y
`calculate_impacts` inventaba 39.600.000 COP/mes (reproductor de D28). El test
no construye un fixture del detector: construye la forma REAL del productor
(`GBPAuditor._base_profile()`) y el audit REAL de `v4complete`
(`modules.auditors.v4_comprehensive.V4AuditResult`).

QUÉ PRUEBA ADEMÁS DEL CASO FELIZ
El schema tri-estado (DA-C3, lección «vacío ≠ ausente»):
  · `schema_data=None`              → no medido → ninguna brecha de schema
  · `schema_data={}` o `{'tiene_hotel_schema': False}` → medido ausente → `SIN_FAQ`
  · schema válido                    → presente → sin brecha
`tiene_hotel_schema` ausente NO es brecha GBP (canal web: `no_hotel_schema`).

MUTATION CHECK (R2.8, L-T4A.5): el mutante M1 restaura las cuatro claves
inglesas en `get_detected_issues`; este diente cae en ROJO con «6 brechas»
(= el defecto medido de D28). El par rojo/verde vive en
`evidence/CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22/FASE-D/`.
"""

import pytest

from modules.auditors.v4_comprehensive import (
    AICrawlerAuditResult,
    CrossValidationResult,
    GBPApiResult,
    MetadataAuditResult,
    PerformanceResult,
    SchemaAuditResult,
    V4AuditResult,
)
from modules.auditors.seo_elements_detector import SEOElementsResult
from modules.commercial_documents.data_structures import (
    ValidatedField,
    ValidationSummary,
)
from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper
from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
from modules.data_validation.confidence_taxonomy import ConfidenceLevel
from modules.scrapers.gbp_auditor import GBPAuditor
from modules.utils.dynamic_impact import get_detected_issues

SCHEMA_VALIDO = {'tiene_hotel_schema': True, 'has_faq': True}


def _perfil_completo() -> dict:
    """Forma REAL del productor: `_base_profile()` de `GBPAuditor`, poblado con
    el perfil completo del reproductor de D28 (reclamado, 40 fotos, 4.6, 120
    reseñas, horarios, whatsapp, website, actividad, Q&A)."""
    auditor = GBPAuditor.__new__(GBPAuditor)  # sin __init__: solo la forma
    perfil = auditor._base_profile()
    perfil.update({
        'existe': True,
        'fotos': 40,
        'rating': 4.6,
        'reviews': 120,
        'horarios': True,
        'whatsapp_visible': True,
        'website': True,
        'telefono': True,
        'posts': 5,
        'tiene_qa': True,
        'ultima_actividad_dias': None,  # no medido → sin brecha (DA-C3)
    })
    return perfil


def _auditor_real() -> GBPAuditor:
    """`GBPAuditor` sin efectos de `__init__` (cache/driver), con su
    `benchmark_loader` real: `_detectar_fugas` es la ruta de producción."""
    from modules.utils.benchmarks import BenchmarkLoader
    auditor = GBPAuditor.__new__(GBPAuditor)
    auditor.benchmark_loader = BenchmarkLoader()
    return auditor


class TestDientePerfilCompleto:
    """AC3: perfil completo → 0 brechas y 0 COP en el camino v4audit."""

    def test_cero_brechas_con_schema_valido(self):
        issues = get_detected_issues(_perfil_completo(), SCHEMA_VALIDO)
        assert issues == [], f"perfil completo produjo {len(issues)} brechas: {issues}"

    def test_cero_brechas_con_schema_no_medido(self):
        issues = get_detected_issues(_perfil_completo(), None)
        assert issues == [], f"perfil completo produjo {len(issues)} brechas: {issues}"

    def test_cero_cop_con_la_ruta_de_produccion(self):
        auditor = _auditor_real()
        fugas, perdida_mes = auditor._detectar_fugas(_perfil_completo())
        resumen = f"fugas={[f['tipo'] for f in fugas]}, perdida={perdida_mes} COP/mes"
        assert fugas == [] and perdida_mes == 0, f"perfil completo: {resumen}"

    def test_no_consume_claves_inglesas_del_contrato_viejo(self):
        """Las cuatro claves inglesas no existen en el productor: si el contrato
        volviera a leerlas, este perfil completo (forma real) daría 6 brechas."""
        perfil = _perfil_completo()
        for clave_inglesa in ('claimed', 'photos', 'has_whatsapp', 'has_hours'):
            assert clave_inglesa not in perfil


class TestSchemaTriEstado:
    """DA-C3: `None` ≠ `{}`; dos resultados legibles."""

    def test_none_no_dispara_brecha(self):
        issues = get_detected_issues(_perfil_completo(), None)
        assert issues == []

    def test_dict_vacio_es_medido_ausente(self):
        issues = get_detected_issues(_perfil_completo(), {})
        assert issues == ['SIN_FAQ'], f"schema medido ausente dio {issues}"

    def test_tiene_hotel_schema_false_es_el_mismo_estado_que_dict_vacio(self):
        issues = get_detected_issues(_perfil_completo(), {'tiene_hotel_schema': False})
        assert issues == ['SIN_FAQ']

    def test_schema_valido_no_dispara_brecha(self):
        issues = get_detected_issues(_perfil_completo(), SCHEMA_VALIDO)
        assert issues == []

    def test_none_y_dict_vacio_dan_resultados_distintos(self):
        assert get_detected_issues(_perfil_completo(), None) != \
            get_detected_issues(_perfil_completo(), {})


class TestActividadVsSchema:
    """`PERFIL_ABANDONADO` es actividad, no schema (N2)."""

    def test_perfil_abandono_por_posts_cero_con_schema_valido(self):
        perfil = _perfil_completo()
        perfil['posts'] = 0
        issues = get_detected_issues(perfil, SCHEMA_VALIDO)
        assert 'PERFIL_ABANDONADO' in issues

    def test_sin_schema_no_produce_perfil_abandonado(self):
        issues = get_detected_issues(_perfil_completo(), {})
        assert 'PERFIL_ABANDONADO' not in issues

    def test_cero_actividad_reciente_es_etiqueta_propia(self):
        perfil = _perfil_completo()
        perfil['ultima_actividad_dias'] = 90  # medida y antigua
        issues = get_detected_issues(perfil, SCHEMA_VALIDO)
        assert issues == ['CERO_ACTIVIDAD_RECIENTE'], issues

    def test_ultima_actividad_no_medida_no_dispara(self):
        perfil = _perfil_completo()
        perfil['ultima_actividad_dias'] = None
        assert 'CERO_ACTIVIDAD_RECIENTE' not in get_detected_issues(perfil, SCHEMA_VALIDO)


def _audit_v4complete_completo() -> V4AuditResult:
    """Forma REAL del audit de `v4complete` (`V4AuditResult` de
    `v4_comprehensive`), todo completo: schema, GBP, performance, OG tags."""
    og = {f'og:tag_{i}': 'v' for i in range(10)}
    return V4AuditResult(
        url='https://hotel-completo.com',
        hotel_name='Hotel Completo',
        timestamp='2026-10-23T10:00:00',
        schema=SchemaAuditResult(
            hotel_schema_detected=True, hotel_schema_valid=True,
            hotel_confidence='high', faq_schema_detected=True,
            faq_schema_valid=True, faq_confidence='high',
            org_schema_detected=True, total_schemas=3,
        ),
        gbp=GBPApiResult(
            place_found=True, place_id='p1', name='Hotel Completo',
            rating=4.6, reviews=120, photos=40, phone='+573001234567',
            website='https://hotel-completo.com', address='Cra 1 # 2-3',
            geo_score=85, geo_score_breakdown={}, confidence='verified',
        ),
        performance=PerformanceResult(
            has_field_data=True, mobile_score=92, desktop_score=96,
            lcp=1.5, fid=40, cls=0.05, status='ok', message='',
        ),
        validation=CrossValidationResult(
            whatsapp_status='verified', phone_web='+573001234567',
            phone_gbp='+573001234567', adr_status='ok', adr_web=300000.0,
            adr_benchmark=280000.0, conflicts=[], validated_fields={},
            whatsapp_html_detected=True,
        ),
        overall_confidence='verified',
        metadata=MetadataAuditResult(
            cms_detected='wp', has_default_title=False, title='Hotel Completo',
            has_default_description=False, description='Desc', has_issues=False,
        ),
        seo_elements=SEOElementsResult(
            open_graph=True, imagenes_alt=True, redes_activas=True,
            confidence='high', open_graph_tags=og, images_without_alt=0,
        ),
    )


def _validation_summary_completo() -> ValidationSummary:
    whatsapp = ValidatedField(
        field_name='whatsapp_number',
        value='+573001234567',
        confidence=ConfidenceLevel.VERIFIED,
        sources=['web_scraping'],
        match_percentage=1.0,
        can_use_in_assets=True,
    )
    return ValidationSummary(fields=[whatsapp], overall_confidence=ConfidenceLevel.VERIFIED)


class TestPainSolutionMapperCaminoV4Complete:
    """AC3 en el camino que sí entrega el diagnóstico."""

    def test_perfil_completo_cero_brechas(self):
        mapper = PainSolutionMapper()
        pains = mapper.detect_pains(
            audit_result=_audit_v4complete_completo(),
            validation_summary=_validation_summary_completo(),
            analytics_data=None,
            whatsapp_html_detected=True,
        )
        ids = [p.id for p in pains]
        assert ids == [], f"audit completo produjo {len(ids)} pains: {ids}"

    def test_map_no_convierte_sin_schema_en_perfil_abandonado(self):
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        assert gen._map_brecha_to_issue_type('no_hotel_schema') != 'PERFIL_ABANDONADO'
        assert gen._map_brecha_to_issue_type('low_citability') != 'PERFIL_ABANDONADO'

    def test_map_no_convierte_no_og_tags_en_fotos(self):
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        assert gen._map_brecha_to_issue_type('no_og_tags') != 'FOTOS_INSUFICIENTES'

    def test_los_tres_pains_web_quedan_sin_issue_type_gbp(self):
        """Justificación por escrito (DA-PLAN-9e): schema hotel, citability y OG
        tags son markup/contenido del SITIO, no perfil GBP; conservan su peso
        propio en `_identify_brechas` y no reclaman etiqueta GBP."""
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        for pain_id in ('no_hotel_schema', 'low_citability', 'no_og_tags'):
            assert gen._map_brecha_to_issue_type(pain_id) == ''

    def test_los_demas_pains_conservan_su_issue_type(self):
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        assert gen._map_brecha_to_issue_type('no_faq_schema') == 'SIN_FAQ'
        assert gen._map_brecha_to_issue_type('no_whatsapp_visible') == 'SIN_WHATSAPP'
        assert gen._map_brecha_to_issue_type('missing_reviews') == 'RESENAS_CRITICAS'
