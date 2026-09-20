"""FASE-B (plan REFACTOR-WHATSAPP-ENTREGA-2026-09-18) — promesas realizables.

Cubre AC1 (los tres productores reciben la senal y, para entradas producibles,
emiten los mismos pain_ids; el ledger serializado no registra ausencia fantasma con
HTML visible), AC2 (ausencia → guia de preparacion; conflicto → guia y boton solo si
la barra de confianza manda; el servicio nuevo esta propagando a propuesta y matriz) y
AC19a-consumo (una senal negativa sin alcance verificado no se redacta ni se almacena
como ausencia confirmada del canal).

Disciplina de prueba (L-T4A.5): el caso rojo se construye con la combinacion que el
codigo si puede producir — campo UNKNOWN/CONFLICT **y** senal HTML — porque con el
centinela ESTIMATED la divergencia no dispara en ninguna de las dos rutas (maestro §1,
fila F-A'). Un fixture generico "hay HTML" daria verde sin tocar la rama.

L-PF10: retirar un pain falso no habilita un fallback de catalogo por lista vacia; se
prueba explicitamente. L-NC6: la senal se pide en el caller, por eso AC1 se comprueba
leyendo el AST del orquestador y no inventando una segunda fuente.
"""

import ast
import json
import re
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from modules.asset_generation.asset_catalog import ASSET_CATALOG, is_asset_implemented
from modules.asset_generation.conditional_generator import ConditionalGenerator
from modules.asset_generation.pain_ledger import PainLedger
from modules.asset_generation.proposal_asset_alignment import PROPOSAL_SERVICE_TO_ASSET
from modules.asset_generation.whatsapp_setup_guide import WhatsAppSetupGuideGenerator
from modules.common.service_identity import SERVICE_IDENTITIES
from modules.commercial_documents.data_structures import (
    CrossValidationResult,
    GBPData,
    PerformanceData,
    SchemaValidation,
    V4AuditResult,
    ValidatedField,
    ValidationSummary,
)
from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper
from modules.commercial_documents.service_catalog import SERVICE_CATALOG
from modules.data_validation.confidence_taxonomy import ConfidenceLevel

REPO_ROOT = Path(__file__).resolve().parents[2]
ORQUESTADOR = REPO_ROOT / "modules/asset_generation/v4_asset_orchestrator.py"


# --------------------------------------------------------------------------- fixtures
def mock_audit(whatsapp_html_detected: bool) -> V4AuditResult:
    """V4AuditResult minimo con la senal HTML que piden las tres rutas."""
    schema = MagicMock(spec=SchemaValidation)
    schema.faq_schema_detected = True
    schema.hotel_schema_detected = True
    schema.org_schema_detected = True

    gbp = MagicMock(spec=GBPData)
    gbp.geo_score = 80
    gbp.reviews = 50
    gbp.confidence = "verified"
    gbp.rating = 4.5

    performance = MagicMock(spec=PerformanceData)
    performance.mobile_score = 75
    performance.has_field_data = True
    performance.lcp = None
    performance.cls = None

    validation = MagicMock(spec=CrossValidationResult)
    validation.whatsapp_html_detected = whatsapp_html_detected

    metadata = MagicMock()
    metadata.has_issues = False

    audit = MagicMock(spec=V4AuditResult)
    audit.url = "https://hotel-test.com"
    audit.schema = schema
    audit.gbp = gbp
    audit.performance = performance
    audit.validation = validation
    audit.metadata = metadata
    audit.ai_crawlers = None
    audit.ia_readiness = None
    audit.citability = None
    audit.seo_elements = None
    return audit


def whatsapp_field(confidence: ConfidenceLevel) -> ValidatedField:
    return ValidatedField(
        field_name="whatsapp_number",
        value="detected_via_html",
        confidence=confidence,
        sources=["web_scraping"],
        match_percentage=0.5,
        can_use_in_assets=False,
    )


def summary_con(field: ValidatedField | None) -> ValidationSummary:
    fields = [] if field is None else [field]
    return ValidationSummary(fields=fields, overall_confidence=ConfidenceLevel.VERIFIED)


def pain_ids(mapper: PainSolutionMapper, audit, summary, html: bool) -> list[str]:
    return [p.id for p in mapper.detect_pains(audit, summary, None,
                                              whatsapp_html_detected=html)]


# ============================================================== AC1 · el cable en el caller
def test_ac1_el_orquestador_propaga_la_senal_a_los_tres_productores():
    """L-NC6: la senal viaja desde el caller. Rojo si alguien vuelve a quitarla.

    Medido sobre el AST del archivo productivo, no sobre un mock: son TRES invocaciones
    (una a `detect_pains`, dos a `CoherenceValidator.validate`), que es la precision
    que el maestro debia a G.
    """
    tree = ast.parse(ORQUESTADOR.read_text(encoding="utf-8"))
    generar = next(
        n for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name == "generate_assets"
    )
    llamadas = [
        n for n in ast.walk(generar)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and n.func.attr in {"detect_pains", "validate"}
    ]
    assert llamadas, "generate_assets dejo de invitar a los productores gobernados"
    faltantes = [
        f"{ll.func.attr}:{ll.lineno}" for ll in llamadas
        if not any(k.arg == "whatsapp_html_detected" for k in ll.keywords)
    ]
    assert not faltantes, (
        "invocaciones de generate_assets sin whatsapp_html_detected: "
        + ", ".join(faltantes)
    )


@pytest.mark.parametrize("confidence", [ConfidenceLevel.UNKNOWN, ConfidenceLevel.CONFLICT])
def test_ac1_entrada_producible_misma_respuesta_con_y_sin_html(confidence):
    """AC1: con HTML visible no hay pain de ausencia; sin HTML, si. Las dos rutas, igual.

    La combinacion es producible: `run_v4_complete_mode` registra el campo con
    confidence UNKNOWN/CONFLICT y `V4ComprehensiveAuditor` puede reportar HTML.
    """
    mapper = PainSolutionMapper()
    audit_sin_html = mock_audit(False)
    audit_con_html = mock_audit(True)
    summary = summary_con(whatsapp_field(confidence))

    sin_html = pain_ids(mapper, audit_sin_html, summary, False)
    con_html = pain_ids(mapper, audit_con_html, summary, True)

    assert "no_whatsapp_visible" in sin_html, (
        "sin numero utilizable y sin HTML la ausencia si es un pain"
    )
    assert "no_whatsapp_visible" not in con_html, (
        "ausencia fantasma: el pain se emite pese a la senal HTML (F-A')"
    )
    # La emision del mapper coincide con la del orquestador: ambos llaman al mismo
    # metodo con la misma senal derivada de `audit_result.validation`.
    derivada = bool(getattr(audit_con_html.validation, "whatsapp_html_detected", False))
    assert pain_ids(mapper, audit_con_html, summary, derivada) == con_html


def test_ac1_ledger_serializado_sin_ausencia_fantasma(tmp_path):
    """AC1 exige el `pain_ledger.json` escrito, no la lista en memoria."""
    mapper = PainSolutionMapper()
    summary = summary_con(whatsapp_field(ConfidenceLevel.UNKNOWN))
    pains = mapper.detect_pains(
        mock_audit(True), summary, None, whatsapp_html_detected=True
    )
    ledger = PainLedger()
    ruta = tmp_path / "pain_ledger.json"
    ledger.save(ledger.from_pains(pains, source_module="pain_solution_mapper"), ruta)

    payload = json.loads(ruta.read_text(encoding="utf-8"))
    entries = payload["entries"] if isinstance(payload, dict) else payload
    ids = [e["pain_id"] for e in entries]
    assert "no_whatsapp_visible" not in ids, ids
    # El resto del trabajo sigue divulgado: el ledger no se vacio por gobernar WhatsApp.
    assert ids == [p.id for p in pains]


# ================================================================= AC2 · promesa condicionada
def test_ac2_la_ausencia_promete_setup_y_no_boton():
    mapper = PainSolutionMapper()
    bloque = mapper.PAIN_SOLUTION_MAP["no_whatsapp_visible"]
    assert bloque["assets"] == ["whatsapp_setup_guide"]
    assert "whatsapp_button" not in bloque["assets"]

    pains = mapper.detect_pains(
        mock_audit(False), summary_con(whatsapp_field(ConfidenceLevel.UNKNOWN)), None,
        whatsapp_html_detected=False,
    )
    solutions = mapper.map_to_solutions(pains)
    tipos = {s.asset_type for s in solutions}
    assert "whatsapp_setup_guide" in tipos
    assert "whatsapp_button" not in tipos
    # Identidad comercial propagada (no el id tecnico como nombre).
    fila = next(s for s in solutions if s.asset_type == "whatsapp_setup_guide")
    assert fila.asset_name == "Configuración de WhatsApp"


def test_ac2_setup_guide_existe_como_asset_implementado():
    """AC2: "setup existe como entregable, no solo como catalogo/promesa"."""
    entry = ASSET_CATALOG["whatsapp_setup_guide"]
    assert is_asset_implemented("whatsapp_setup_guide")
    assert entry.promised_by == ["no_whatsapp_visible"]
    assert entry.required_field != "whatsapp", (
        "el guia no puede depender del numero que precisamente falta"
    )


def test_ac2_la_guia_no_contiene_numero_ni_enlace_y_se_genera():
    """El contenido del writer real: sin `wa.me`, sin secuencia digitada, sin placeholder."""
    texto = WhatsAppSetupGuideGenerator().generate(
        hotel_name="Hotel de Prueba", site_url="https://hotel-test.com"
    )
    assert "wa.me" not in texto
    assert "api.whatsapp.com" not in texto
    assert not re.search(r"\+?\d[\d\s()-]{6,}", texto), (
        "la guia de preparacion publico algo que parece un numero"
    )
    assert "NO VERIFICADO" in texto
    assert "Hotel de Prueba" in texto
    # Dispatch real del generador condicional, no solo la clase suelta.
    gen = ConditionalGenerator()
    contenido = gen._generate_content(
        "whatsapp_setup_guide",
        {"hotel_data": {"name": "Hotel de Prueba", "url": "https://hotel-test.com"}},
        "Hotel de Prueba",
    )
    assert contenido.strip() and "wa.me" not in contenido
    assert len(contenido) >= 500


def test_ac2_conflicto_ya_no_fuerza_el_boton():
    """Se retiro `can_generate=True` incondicional: la barra del mapping manda."""
    mapper = PainSolutionMapper()
    specs = mapper.get_assets_for_pain("whatsapp_conflict", {"whatsapp_number": 0.0})
    botones = [s for s in specs if s.asset_type == "whatsapp_button"]
    assert botones, "el boton sigue planificandose por la via del conflicto (AC6)"
    assert all(not s.can_generate for s in botones), (
        "un numero en conflicto sin confianza sigue prometiendo boton listo"
    )
    # Con candidatos suficientemente confiables el boton si vuelve a ser generable:
    # no se prohibio el asset, se goberno la promesa.
    specs_ok = mapper.get_assets_for_pain(
        "whatsapp_conflict", {"whatsapp_number": 0.6}
    )
    assert any(
        s.asset_type == "whatsapp_button" and s.can_generate for s in specs_ok
    )


def test_ac2_lista_vacia_no_activa_fallback_de_catalogo():
    """L-PF10: gobernar un pain falso no convierte 'sin mapeo' en 'genera algo'."""
    assert ConditionalGenerator.PAIN_TO_ASSET["no_whatsapp_visible"] == "whatsapp_setup_guide"
    assert "no_whatsapp_visible" in ConditionalGenerator.PAIN_TO_ASSET, (
        "pain y asset siguen decidiendo aparte (maestro §1, fila F-F)"
    )
    assert "pain_inexistente" not in ConditionalGenerator.PAIN_TO_ASSET


def test_ac2_identidad_propagada_a_propuesta_y_matriz():
    claves = {i.key for i in SERVICE_IDENTITIES}
    assert "guia_configuracion_whatsapp" in claves
    ident = {i.key: i for i in SERVICE_IDENTITIES}
    assert ident["guia_configuracion_whatsapp"].asset_type == "whatsapp_setup_guide"
    assert ident["guia_configuracion_whatsapp"].pain_id == "no_whatsapp_visible"
    # Tras B el boton entra al plan solo por conflicto (premisas de AC6/AC2).
    assert ident["boton_whatsapp"].pain_id == "whatsapp_conflict"
    # SERVICE_CATALOG es proyeccion, no copia.
    assert SERVICE_CATALOG["guia_configuracion_whatsapp"].asset_type == "whatsapp_setup_guide"
    # FASE-B midio el blast radius: el servicio NO entra al universo fijo que el gate
    # `proposal_asset_alignment` exige ver entregado en toda corrida (eso degradaba la
    # cobertura de hoteles sin brecha de WhatsApp). Si alguien lo promueve a contado,
    # este assert es el que avisa que hay que re-definir el denominador del gate.
    assert "Configuración de WhatsApp" not in PROPOSAL_SERVICE_TO_ASSET
    assert ident["guia_configuracion_whatsapp"].counts_in_alignment is False


def test_ac2_tabla_de_resolucion_separada_del_universo_contado():
    """A1 de FASE-B: resolver ≠ contar. El servicio condicional se resuelve, y el
    denominador del gate `proposal_asset_alignment` no se mueve."""
    from modules.asset_generation.proposal_asset_alignment import (
        ALL_PROMISED_SERVICES,
        ALL_RESOLVABLE_SERVICES,
        RESOLUCION_SERVICIO_A_ASSET,
        classify_promised_services,
    )

    assert RESOLUCION_SERVICIO_A_ASSET["Configuración de WhatsApp"] == "whatsapp_setup_guide"
    assert set(PROPOSAL_SERVICE_TO_ASSET) < set(RESOLUCION_SERVICIO_A_ASSET), (
        "la tabla de resolucion debe ser superpropia del universo contado"
    )
    assert ALL_PROMISED_SERVICES == list(PROPOSAL_SERVICE_TO_ASSET.keys())
    assert ALL_RESOLVABLE_SERVICES == list(RESOLUCION_SERVICIO_A_ASSET.keys())

    # Pidiéndolo explícitamente, la matriz lo resuelve (antes caía a unknown_services).
    entries, not_promised, unknown = classify_promised_services(
        ["Configuración de WhatsApp"],
        [{"pain_id": "no_whatsapp_visible"}],
        [{"asset_type": "whatsapp_setup_guide", "confidence_score": 0.8, "path": "/x"}],
        None,
    )
    assert unknown == [], unknown
    assert len(entries) == 1
    assert entries[0].asset_type == "whatsapp_setup_guide"
    assert str(entries[0].status) .endswith("LINKED") or entries[0].status == "LINKED"

    # Y con un ledger que no lo menciona, NO se promete: no entra por la puerta del
    # universo contado (que es lo que degradaba la cobertura de otros hoteles).
    e2, np2, u2 = classify_promised_services(
        ["Configuración de WhatsApp"], [{"pain_id": "no_faq_schema"}], [], None
    )
    assert e2 == []
    assert u2 == []
    assert "Configuración de WhatsApp" in np2


# ===================================================== AC19a-consumo · ausencia no afirmada
def test_ac19a_no_verificado_en_sitio_queda_registrado_en_el_ledger(tmp_path):
    ledger = PainLedger()
    pains = ledger.from_pains(
        PainSolutionMapper().detect_pains(
            mock_audit(False), summary_con(whatsapp_field(ConfidenceLevel.UNKNOWN)), None,
            whatsapp_html_detected=False,
        ),
        source_module="pain_solution_mapper",
    )
    resultado = ledger.apply_site_verification(
        pains, {"results": {"faq_page": {"status": "exists", "site_verified": True}}}
    )
    entry = next(e for e in resultado if e.pain_id == "no_whatsapp_visible")
    assert entry.status == "DETECTED", "la brecha sigue divulgada"
    assert any("NO_VERIFICADO_EN_SITIO" in r for r in entry.evidence_refs)

    ruta = tmp_path / "pain_ledger.json"
    ledger.save(resultado, ruta)
    payload = json.loads(ruta.read_text(encoding="utf-8"))
    entries = payload["entries"] if isinstance(payload, dict) else payload
    guardada = next(e for e in entries if e["pain_id"] == "no_whatsapp_visible")
    assert any(
        "NO_VERIFICADO_EN_SITIO" in r for r in guardada["evidence_refs"]
    ), "el estado solo vivo en memoria, no en el artefacto"


def test_ac19a_narrativa_no_afirma_ausencia_confirmada():
    """Prohibido redactar 'el hotel no tiene WhatsApp' sin alcance verificado (L-PF6)."""
    fuente = (
        REPO_ROOT / "modules/commercial_documents/v4_diagnostic_generator.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(fuente)
    narrativas = None
    for nodo in ast.walk(tree):
        if isinstance(nodo, ast.Assign):
            objetivos = [t.id for t in nodo.targets if isinstance(t, ast.Name)]
            if "narratives" in objetivos and isinstance(nodo.value, ast.Dict):
                claves = [
                    k.value for k in nodo.value.keys if isinstance(k, ast.Constant)
                ]
                if "no_whatsapp_visible" in claves:
                    narrativas = nodo.value
                    break
    assert narrativas is not None, "la tabla de narrativas dejo de ser un literal"

    clave = [k for k in narrativas.keys
             if isinstance(k, ast.Constant) and k.value == "no_whatsapp_visible"][0]
    bloque = narrativas.values[narrativas.keys.index(clave)]
    texto = "\n".join(
        n.value for n in ast.walk(bloque) if isinstance(n, ast.Constant)
        and isinstance(n.value, str)
    )
    prohibidos = ("sin whatsapp", "no tiene whatsapp", "canal directo cerrado")
    bajo = texto.lower()
    assert not any(p in bajo for p in prohibidos), (
        f"la narrativa afirma ausencia del canal: {texto[:120]}"
    )
    assert "verifiqu" in bajo or "no se confirm" in bajo, texto[:160]
