"""AC10 (sesión de recuperación 2026-10-07): `implementation_order_check` deja de registrar la fuente.

Hallazgo V-2: el ZIP del 2026-10-07 tenía el orden de implementación vacío y
`revision_assets.json` respondía `{status: 'OK', source: 'zip'}` — Bot 3 declaraba
de dónde había leído el documento, no si el documento tenía tareas.

Contrato declarado en la recuperación: el rojo por orden vacío es **WARNING** con
tipo propio (`IMPLEMENTATION_ORDER_SIN_TAREAS`). No es CRITICAL porque el veredicto
bloqueante del revisor exige CRITICAL y esta sesión no reabre la política de
enforcement del Tribunal (V-7 y el primer piso son de otra fila, con otro dueño).
Sin lectura el registro declara **NO-EVALUABLE**, que es abstención y no verde.
"""

import json
import zipfile

import pytest

from modules.quality_gates.tribunal.asset_reviewer import (
    FINDING_EMPTY_DELIVERY_TEMPLATE,
    FINDING_IMPLEMENTATION_ORDER_SIN_TAREAS,
    IMPL_CONTENIDO_NO_EVALUABLE,
    IMPL_CONTENIDO_OK,
    IMPL_CONTENIDO_VACIO,
    IMPL_ORDER_ARTIFACT_MISSING,
    IMPL_ORDER_OK,
    SEVERITY_CRITICAL,
    SEVERITY_WARNING,
    AssetReviewer,
)

# El documento EXACTO que viajó en el ZIP certificado del 2026-10-07: 13 rutas
# bajo ADICIONALES y el ORDEN sin una sola linea.
DOC_CERTIFICADO_SIN_TAREAS = (
    "# 📦 Delivery Package - Hotel Don Alfonso\n\n"
    "**Fecha:** 2026-10-07 09:34\n"
    "**Score GEO:** 63 (OBLIGATORIO)\n\n"
    "---\n\n"
    "## ⚠️ REGLA DE ORO: NUNCA REEMPLAZAR, SIEMPRE ENRIQUECER\n\n"
    "Los archivos CORE son **OBLIGATORIOS**.\n"
    "Los archivos GEO son **ENRICHMENT ADICIONAL**.\n\n"
    "---\n\n"
    "## 📋 ORDEN DE IMPLEMENTACIÓN\n\n"
    "---\n\n"
    "## 📦 ASSETS ADICIONALES (fuera del catálogo CORE/GEO)\n\n"
    "Los siguientes assets no tienen relación CORE↔GEO registrada:\n\n"
    "- **`ASSETS/faq_page/ESTIMATED_faqs_20261007_093402.json`**: Asset adicional sin par conocido.\n"
    "- **`ASSETS/hotel_schema/hotel_schema_20261007_093402.json`**: Asset adicional sin par conocido.\n"
    "\n---\n\n"
    "## 🔗 GUÍA DE RELACIONES ENTRE ARCHIVOS\n\n"
    "---\n\n"
    "## ✅ CHECKLIST DE IMPLEMENTACIÓN\n\n"
    "---\n\n"
    "*Generado por IA Hoteles Agent v4.0 - FASE-5 Asset Responsibility Contract*"
)

DOC_CON_TAREA = DOC_CERTIFICADO_SIN_TAREAS.replace(
    "## 📋 ORDEN DE IMPLEMENTACIÓN\n\n",
    "## 📋 ORDEN DE IMPLEMENTACIÓN\n\n"
    "### 1. ASSETS/hotel_schema/hotel_schema_20261007_093402.json ✅ [CORE]\n"
    "   - **Descripción:** Schema.org básico del hotel\n"
    "   - **Obligatorio:** Sí\n\n",
)

# `###` de la guia de relaciones NO es tarea del orden: el corte es por seccion.
DOC_CON_TAREA = DOC_CON_TAREA.replace(
    "## 🔗 GUÍA DE RELACIONES ENTRE ARCHIVOS\n\n",
    "## 🔗 GUÍA DE RELACIONES ENTRE ARCHIVOS\n\n"
    "### hotel_schema.json ↔ hotel_schema_rich.json\n",
)


def _zip_con(tmp_path, documento, con_miembro=True):
    deliveries = tmp_path / "deliveries"
    deliveries.mkdir(parents=True, exist_ok=True)
    audit = tmp_path / "v4_audit"
    audit.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(deliveries / "hoteltest_20261007.zip", "w") as z:
        if con_miembro:
            z.writestr("IMPLEMENTATION_ORDER.md", documento)
        z.writestr("MANIFEST.json", json.dumps({"files": []}))
    return audit, deliveries


def _hallazgos(report, tipo):
    return [f for f in report["findings"] if f["finding_type"] == tipo]


def test_orden_vacio_del_paquete_certificado_reporta_rojo(tmp_path):
    """El documento que la certificación dejó pasar ahora pinta ORDEN_VACIA."""
    audit, deliveries = _zip_con(tmp_path, DOC_CERTIFICADO_SIN_TAREAS)
    report = AssetReviewer(audit, deliveries).review()

    check = report["implementation_order_check"]
    assert check["status"] == IMPL_ORDER_OK
    assert check["tareas"] == 0
    assert check["contenido"] == IMPL_CONTENIDO_VACIO
    hallazgos = _hallazgos(report, FINDING_IMPLEMENTATION_ORDER_SIN_TAREAS)
    assert len(hallazgos) == 1
    assert hallazgos[0]["severity"] == SEVERITY_WARNING


def test_orden_con_tarea_reporta_ok(tmp_path):
    """Con la tarea numerada del fix, el mismo documento casa OK y no emite hallazgo."""
    audit, deliveries = _zip_con(tmp_path, DOC_CON_TAREA)
    report = AssetReviewer(audit, deliveries).review()

    check = report["implementation_order_check"]
    assert check["contenido"] == IMPL_CONTENIDO_OK
    assert check["tareas"] == 1
    assert _hallazgos(report, FINDING_IMPLEMENTATION_ORDER_SIN_TAREAS) == []


def test_la_tarea_de_la_guia_no_cuenta_como_orden(tmp_path):
    """Si el conteo mirara todo el documento, la guía de relaciones daría verde falso."""
    doc = DOC_CERTIFICADO_SIN_TAREAS.replace(
        "## 🔗 GUÍA DE RELACIONES ENTRE ARCHIVOS\n\n",
        "## 🔗 GUÍA DE RELACIONES ENTRE ARCHIVOS\n\n### 7. algo ↔ algo_rich\n",
    )
    audit, deliveries = _zip_con(tmp_path, doc)
    report = AssetReviewer(audit, deliveries).review()

    assert report["implementation_order_check"]["tareas"] == 0
    assert report["implementation_order_check"]["contenido"] == IMPL_CONTENIDO_VACIO


def test_sin_documento_no_afirma_verde(tmp_path):
    """ARTIFACT_MISSING sigue sin bloquear, pero el contenido es NO-EVALUABLE, no OK."""
    audit, deliveries = _zip_con(tmp_path, "", con_miembro=False)
    report = AssetReviewer(audit, deliveries).review()

    check = report["implementation_order_check"]
    assert check["status"] == IMPL_ORDER_ARTIFACT_MISSING
    assert check["contenido"] == IMPL_CONTENIDO_NO_EVALUABLE
    assert check["tareas"] is None
    assert _hallazgos(report, FINDING_IMPLEMENTATION_ORDER_SIN_TAREAS) == []


def test_los_dos_rojos_no_se_confunden(tmp_path):
    """El rojo nuevo y el stub estructural son canales separados y comparables.

    Con el documento certificado (13 rutas bajo ADICIONALES) solo cae el nuevo:
    `_is_template_stub` contaba contenido de OTRA seccion y lo declaraba bueno.
    Con el stub de secciones todas vacias caen los dos, cada uno con su tipo.
    """
    audit, deliveries = _zip_con(tmp_path, DOC_CERTIFICADO_SIN_TAREAS)
    solo_nuevo = AssetReviewer(audit, deliveries).review()
    assert [f["finding_type"] for f in solo_nuevo["findings"]] == [
        FINDING_IMPLEMENTATION_ORDER_SIN_TAREAS
    ]

    stub = DOC_CERTIFICADO_SIN_TAREAS.split("## 📦 ASSETS ADICIONALES")[0] + (
        "## 🔗 GUÍA DE RELACIONES ENTRE ARCHIVOS\n\n---\n\n"
        "## ✅ CHECKLIST DE IMPLEMENTACIÓN\n\n---\n\n"
        "*Generado por IA Hoteles Agent v4.0*"
    )
    audit2, deliveries2 = _zip_con(tmp_path / "b", stub)
    con_stub = AssetReviewer(audit2, deliveries2).review()
    tipos = {f["finding_type"]: f["severity"] for f in con_stub["findings"]}
    assert tipos[FINDING_EMPTY_DELIVERY_TEMPLATE] == SEVERITY_CRITICAL
    assert tipos[FINDING_IMPLEMENTATION_ORDER_SIN_TAREAS] == SEVERITY_WARNING
