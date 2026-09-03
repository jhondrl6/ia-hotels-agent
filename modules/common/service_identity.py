"""Identidad canónica servicio↔asset↔pain (FASE-A, Capa 2).

POR QUÉ EXISTE
El censo de FASE-A (`evidence/FASE-A/censo-registros.md`) contó catorce registros que
declaran, cada uno por su lado, qué servicio comercial entrega qué asset y resuelve qué
pain. Ningún test fijaba la biyección. El resultado documentado en el dossier §12.3:

  V2  — seis pain_ids que no existen en `PAIN_SOLUTION_MAP`: la brecha se declaraba y
        nunca podía detectarse.
  V3  — `ASSET_TO_PAIN_ID["monthly_report"] = "no_faq_schema"` mientras SERVICE_CATALOG
        decía `no_monthly_report`. Fósil de la inversión de claves previa a FASE-2
        (asset_type usado como pain_id), ya auditada en `asset_semantics_validator.py`.
  V14 — la narrativa declaraba un conteo de servicios que el código no cumplía, en tres
        copias independientes.

DOS CAPAS
  Capa 1 — `PainSolutionMapper.PAIN_SOLUTION_MAP`: universo canónico de pain_ids. No se
           modifica aquí (la biyección mapa↔emisión de `detect_pains` es FASE-B).
  Capa 2 — este módulo: identidad del SERVICIO COMERCIAL.

Regla: ningún registro derivado puede declarar un pain_id ausente de Capa 1, ni un
asset_type ausente de `ASSET_CATALOG`, ni atribuir a un asset un pain distinto del que
declara su identidad. Lo exige `tests/common/test_service_identity_registry.py`.

QUÉ NO ES ESTE MÓDULO
No declara textos de pain, ni narrativas, ni precios: eso seguiría siendo una tabla
paralela compitiendo con Capa 1 (guardrail L-NC4). Este módulo no importa nada del
proyecto, de modo que `asset_generation`, `commercial_documents` y `financial_engine`
pueden consumirlo sin cerrar un ciclo.

TRIGGER ≠ ATRIBUCIÓN
`pain_id` es el DISPARADOR (qué pain hace vendible el servicio). `brecha_candidates` es
la ATRIBUCIÓN (qué brecha del diagnóstico se le imputa en la tabla, con su costo). No
son lo mismo y ambos están sostenidos por Capa 1; hasta FASE-A ninguna estructura
expresaba la diferencia. Ver `REVIEWED_TRIGGER_DIVERGENCES`.
"""

from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Tuple


@dataclass(frozen=True)
class ServiceIdentity:
    """Identidad de un servicio comercial vendible.

    Attributes:
        key: identificador estable (clave de SERVICE_CATALOG).
        service_name: nombre que se imprime en la propuesta.
        asset_type: asset que entrega el servicio; debe existir en ASSET_CATALOG.
        pain_id: DISPARADOR — debe existir en PAIN_SOLUTION_MAP.
        description: texto comercial de la fila.
        brecha_candidates: ATRIBUCIÓN — brechas imputables al servicio en la tabla,
            en orden de preferencia. Cada una debe existir en PAIN_SOLUTION_MAP.
        counts_in_alignment: si el servicio entra en PROPOSAL_SERVICE_TO_ASSET y por
            tanto en el recuento del gate de alignment. `False` para el complemento
            siempre-activo (BUG-10 / FASE-3), que se genera pero no se promete por pain.
    """

    key: str
    service_name: str
    asset_type: str
    pain_id: str
    description: str
    brecha_candidates: Tuple[str, ...] = ()
    counts_in_alignment: bool = True


# El ORDEN ES PARTE DEL CONTRATO: la tabla de servicios de la propuesta recorre
# PROPOSAL_SERVICE_TO_ASSET en orden de inserción. Esta secuencia reproduce la de
# SERVICE_CATALOG antes de FASE-A, de modo que la derivación no mueve ninguna fila.
SERVICE_IDENTITIES: Tuple[ServiceIdentity, ...] = (
    ServiceIdentity(
        key="seo_local",
        service_name="SEO Local",
        asset_type="optimization_guide",
        pain_id="poor_performance",
        description="Para aparecer en las primeras posiciones de Google tradicional",
        brecha_candidates=("low_seo_score", "low_content_length"),
    ),
    ServiceIdentity(
        key="boton_whatsapp",
        service_name="Botón de WhatsApp",
        asset_type="whatsapp_button",
        pain_id="no_whatsapp_visible",
        description="Sus huéspedes reservan con 1 clic desde su web",
        brecha_candidates=("whatsapp_conflict", "no_whatsapp_visible"),
    ),
    ServiceIdentity(
        key="schema_hotel",
        service_name="Schema Hotel",
        asset_type="hotel_schema",
        pain_id="no_hotel_schema",
        description="Datos estructurados para Google y IA sobre tu hotel",
        brecha_candidates=("no_hotel_schema",),
    ),
    ServiceIdentity(
        key="schema_organization",
        service_name="Schema Organization",
        asset_type="org_schema",
        pain_id="no_org_schema",
        description="Datos estructurados sobre la organización del hotel",
        brecha_candidates=("no_org_schema",),
    ),
    ServiceIdentity(
        key="pagina_faq",
        service_name="Página de FAQ",
        asset_type="faq_page",
        pain_id="no_faq_schema",
        description="Sus huéspedes encuentran respuestas sin salir de su web",
        brecha_candidates=("no_faq_schema",),
    ),
    ServiceIdentity(
        key="meta_tags_sociales",
        service_name="Meta Tags Sociales (Open Graph)",
        asset_type="open_graph",
        pain_id="no_og_tags",
        description="Sus fotos brillan cuando alguien comparte su link en redes",
        brecha_candidates=("no_og_tags",),
    ),
    # BUG-10 / FASE-3: complemento siempre-activo. Se genera, pero no se promete por
    # pain y no cuenta en el alignment: incluirlo empeora coverage_ratio (0.571→0.500,
    # medido en dossier §8.5). De ahí counts_in_alignment=False y sin brecha atribuible.
    ServiceIdentity(
        key="informe_mensual",
        service_name="Informe Mensual",
        asset_type="monthly_report",
        pain_id="no_monthly_report",
        description="Reporte mensual con metricas de rendimiento y oportunidades",
        brecha_candidates=(),
        counts_in_alignment=False,
    ),
    ServiceIdentity(
        key="optimizacion_ia_generativa",
        service_name="Optimización para IA Generativa",
        asset_type="llms_txt",
        pain_id="low_ia_readiness",
        description="Aparece cuando clientes preguntan a ChatGPT/Gemini 'dónde hospedarme en [región]'",
        brecha_candidates=("missing_llmstxt",),
    ),
)


# Divergencias trigger↔atribución REVISADAS A MANO: el pain que dispara el servicio no
# está entre las brechas que se le atribuyen en la tabla. Ambas mitades son legítimas y
# existen en Capa 1, pero son decisiones distintas que ningún registro expresaba.
# FASE-C (propuesta dinámica) debe vaciar este conjunto o justificar cada entrada.
REVIEWED_TRIGGER_DIVERGENCES: FrozenSet[str] = frozenset({
    # optimization_guide dispara por poor_performance, pero en la tabla se le imputan
    # low_seo_score / low_content_length (las brechas con costo atribuible por RC1).
    "seo_local",
    # llms_txt dispara por low_ia_readiness (score AEO compuesto) y se le imputa
    # missing_llmstxt (el artefacto concreto que falta).
    "optimizacion_ia_generativa",
})


def identidad_por_clave() -> Dict[str, ServiceIdentity]:
    return {i.key: i for i in SERVICE_IDENTITIES}


def identidad_por_asset() -> Dict[str, ServiceIdentity]:
    return {i.asset_type: i for i in SERVICE_IDENTITIES}


def servicio_por_asset() -> Dict[str, str]:
    return {i.asset_type: i.service_name for i in SERVICE_IDENTITIES}


def identidades_alineables() -> List[ServiceIdentity]:
    """Servicios que sí se prometen por pain (entran en el recuento de alignment)."""
    return [i for i in SERVICE_IDENTITIES if i.counts_in_alignment]


__all__ = [
    "ServiceIdentity",
    "SERVICE_IDENTITIES",
    "REVIEWED_TRIGGER_DIVERGENCES",
    "identidad_por_clave",
    "identidad_por_asset",
    "servicio_por_asset",
    "identidades_alineables",
]
