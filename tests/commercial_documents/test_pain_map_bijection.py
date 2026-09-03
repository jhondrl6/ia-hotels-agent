"""Candado de biyección TRIPLE: PAIN_SOLUTION_MAP ↔ detect_pains ↔ narratives.

FASE-B (ESTABILIZACION-PRE-TRIBUNAL-2026-09-03), AC4.

POR QUÉ EXISTE
El dossier §12.3 V1 midió que Capa 1 declaraba 27 pain_ids mientras `detect_pains`
implementaba ~18: 9 pains muertos que ninguna emisión produce. N-A1 (FASE-A) midió la
segunda mitad: `narratives` en `_pain_to_brecha` solo tiene 16 claves y

    if pain.id not in narratives:
        return None                      # v4_diagnostic_generator.py:3346-3347

descarta en silencio todo pain sin entrada. Cerrar solo mapa↔emisión dejaba el fix
inerte: los pains llegaban a `_pain_to_brecha` y rebotaban. De ahí que la biyección sea
**triple**.

QUÉ FIJA ESTE CANDADO
    narratives cubre TODA Capa 1           (capa narrativa total, sin excepciones)
    emisiones ⊆ Capa 1                     (sin huérfanos en ninguna dirección)
    Capa 1 = emisiones ⊎ PAINS_DIFERIDOS   (partición: ningún pain queda sin decisión)

La partición vive del lado de la **emisión**, no del lado de la narrativa. Un pain
diferido lo está porque no hay señal de dato verificable que lo emita — nunca porque su
texto sea problemático. Hacer total la capa narrativa es la postura más fuerte contra el
descarte silencioso: ningún pain de Capa 1 puede rebotar en `_pain_to_brecha`, de modo que
el día que un diferido gane emisión la brecha aparece en el documento sin tocar una segunda
tabla. Una partición narrativa exigiría, en cambio, añadir la entrada a mano en el mismo
commit que la emisión — exactamente el acoplamiento de dos registros que produjo V1 y N-A1.

`PAINS_DIFERIDOS` no es un estacionamiento: cada entrada exige motivo y seguimiento, y un
test impide que un pain diferido gane emisión sin salir del registro.

QUÉ NO FIJA (deliberadamente)
- **Conteos.** Ni `len(PAIN_SOLUTION_MAP) == 26` ni `len(narratives) == 20`: eso fosiliza
  el estado actual en vez de proteger la relación (anti-lección L-NC10).
- **Alcanzabilidad en tiempo de ejecución.** El guardián AST ve *puntos de emisión*, no
  guardias insatisfacibles. `low_ota_divergence` tiene punto de emisión en
  `pain_solution_mapper.py` (rama `low_ota_divergence` dentro de `detect_pains`, hoy `:452`)
  pero nunca dispara porque el guard de arriba (`:447`) hace
  `hasattr(direct_field.value, '__iter__')` sobre un float (V7, FASE-H). Esa es exactamente
  la confusión que llevó a N-A1 a clasificar `no_ga4_enhanced` como "vivo": su guardia
  `hasattr(status, "is_enhanced")` es insatisfacible porque `is_enhanced` no existe en el
  repo. Ver seguimiento S-B7 en `evidence/FASE-B/decision-pains-muertos.md`.

VALIDA CONTRA EL CANÓNICO, no contra una copia: los pain_ids se importan de
`PainSolutionMapper.PAIN_SOLUTION_MAP` (Capa 1, FASE-A).
"""

import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple

import pytest

from modules.commercial_documents.pain_solution_mapper import Pain, PainSolutionMapper
from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator

REPO_ROOT = Path(__file__).resolve().parents[2]
MAPPER_REL = "modules/commercial_documents/pain_solution_mapper.py"
DIAG_REL = "modules/commercial_documents/v4_diagnostic_generator.py"

# Métodos de PainSolutionMapper que construyen Pain(...). Si alguno deja de existir el
# candado falla en vez de reportar silenciosamente cero emisiones.
FUNCIONES_EMISORAS = frozenset({"detect_pains", "detect_pains_for_analytics",
                                "_detect_analytics_pains"})


# =============================================================================
# Registro de pains DIFERIDOS (decisión B1, no parking)
# =============================================================================
#
# Cada entrada es un pain_id que permanece en Capa 1 SIN punto de emisión porque
# (a) no existe señal de dato verificable en el pipeline actual, y (b) retirarlo está
# bloqueado por el registro canónico de FASE-A, que esta fase tiene prohibido editar:
#
#   · tests/common/test_service_identity_registry.py::test_elemento_kb_valida_contra_capa1
#     exige que todo ELEMENTO_KB_TO_PAIN_ID[k][0] esté en Capa 1 → bloquea los pains
#     referidos en v4_diagnostic_generator.py:139-165 (región fuera del alcance de FASE-B).
#   · ...::test_pain_to_asset_valida_contra_capa1 → bloquea los referidos en
#     conditional_generator.py:244-263.
#   · ...::test_pain_ids_canonicos_existen_en_pain_solution_map → bloquea los referidos en
#     modules/common/service_identity.py (Capa 2, archivo prohibido).
#
# Justificación completa, señal por señal: evidence/FASE-B/decision-pains-muertos.md §3.
PAINS_DIFERIDOS: Dict[str, Tuple[str, str]] = {
    "no_ssl": (
        "Sin señal verificable: el único candidato (audit_result.url.startswith('https'), "
        "_extraer_elementos_seo:2919) mide la URL de entrada del usuario, no el certificado "
        "del sitio. Dispararía 'Sin SSL' sobre sitios que sí lo tienen. Retiro bloqueado por "
        "ELEMENTO_KB_TO_PAIN_ID['ssl']:142 y PAIN_TO_ASSET['no_ssl']:244.",
        "S-B1",
    ),
    "no_schema_reviews": (
        "Sin señal verificable: el único proxy (bool(audit_result.gbp.rating), "
        "_extraer_elementos_seo:2939) mide la calificación en Google, no el markup "
        "aggregateRating del sitio — invierte la verdad en el caso SalenteReal (986 reseñas "
        "/ 4.5 en Google, cero markup). Ningún auditor detecta aggregateRating. Retiro "
        "bloqueado por ELEMENTO_KB_TO_PAIN_ID['schema_reviews']:144.",
        "S-B2",
    ),
    "no_blog_content": (
        "Sin señal: elementos['blog_activo'] = 'no_evaluado' hardcodeado "
        "(_extraer_elementos_seo:2937, PATCH-A: 'detección real requiere HTML scrapeo'). "
        "Retiro bloqueado por ELEMENTO_KB_TO_PAIN_ID['blog_activo']:152.",
        "S-B2",
    ),
    "low_content_length": (
        "Duplicado de low_citability: ELEMENTO_KB_TO_PAIN_ID['contenido_extenso'] ya apunta a "
        "low_citability (:147) y _extraer_elementos_iao calcula contenido_extenso (:3025-3029) "
        "con la expresión idéntica a citability_score (:3018-3022), mismo asset "
        "optimization_guide. Implementarlo reportaría la misma brecha dos veces. Retiro "
        "bloqueado por Capa 2: service_identity.py:78 seo_local.brecha_candidates.",
        "S-B4",
    ),
    "no_motor_reservas": (
        "Señal existe pero no alcanza detect_pains: web_scraper._detectar_motor_reservas:470 "
        "alimenta modules/delivery/, no el audit — v4_comprehensive no importa web_scraper y "
        "booking_engine_detected nunca se pobla (main.py:2216-2327 construye el "
        "ValidationSummary con 5 campos). Retiro huérfanizaría barra_reserva_movil "
        "(IMPLEMENTED, promised_by=['no_motor_reservas'] como único promotor).",
        "S-B5",
    ),
    "no_monthly_report": (
        "No es un gap del sitio sino un entregable propio: monthly_report_requested no existe "
        "en el repo y el asset monthly_report tiene promised_by=['always'] "
        "(asset_catalog.py:336) — siempre se entrega, la brecha nunca existe. Retiro bloqueado "
        "por Capa 2: service_identity.py:127 pain_id='no_monthly_report'.",
        "S-B6",
    ),
}


# =============================================================================
# Guardían AST (patrón FASE-SR-A) — no regex sobre el fuente
# =============================================================================

def _tree(rel: str) -> ast.Module:
    path = REPO_ROOT / rel
    assert path.exists(), f"No existe {rel}"
    return ast.parse(path.read_text(encoding="utf-8"))


def _pain_ids_emitidos() -> Set[str]:
    """pain_id literales de todo `Pain(id="...")` dentro de las funciones emisoras."""
    tree = _tree(MAPPER_REL)
    funciones = {
        node.name for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    faltantes = sorted(FUNCIONES_EMISORAS - funciones)
    assert not faltantes, (
        f"Dejaron de existir las funciones emisoras {faltantes} en {MAPPER_REL}: "
        f"actualizar FUNCIONES_EMISORAS (y el candado con ellas)"
    )

    emitidos: Set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name not in FUNCIONES_EMISORAS:
            continue
        for sub in ast.walk(node):
            if not isinstance(sub, ast.Call):
                continue
            nombre = sub.func.id if isinstance(sub.func, ast.Name) else (
                sub.func.attr if isinstance(sub.func, ast.Attribute) else None
            )
            if nombre != "Pain":
                continue
            for kw in sub.keywords:
                if kw.arg == "id" and isinstance(kw.value, ast.Constant) \
                        and isinstance(kw.value.value, str):
                    emitidos.add(kw.value.value)
    return emitidos


def _claves_narratives() -> Set[str]:
    """Claves literales del dict `narratives` en `_pain_to_brecha`."""
    tree = _tree(DIAG_REL)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "narratives" \
                    and isinstance(node.value, ast.Dict):
                claves = {
                    k.value for k in node.value.keys
                    if isinstance(k, ast.Constant) and isinstance(k.value, str)
                }
                assert claves, "el dict narratives quedó vacío"
                return claves
    pytest.fail(
        f"No se encontró el dict literal `narratives` en {DIAG_REL}. Si B2 lo volvió "
        f"derivado, actualizar este candado para validar la derivación (AC de B3)."
    )


@pytest.fixture(scope="module")
def capa1() -> Set[str]:
    """Capa 1 importada del canónico, no copiada."""
    return set(PainSolutionMapper.PAIN_SOLUTION_MAP.keys())


@pytest.fixture(scope="module")
def emitidos() -> Set[str]:
    return _pain_ids_emitidos()


@pytest.fixture(scope="module")
def narrados() -> Set[str]:
    """Claves del dict LITERAL `narratives`.

    Desde B2 el literal cubre solo los 16 pains heredados; el resto se **deriva** de Capa 1
    dentro de `_pain_to_brecha`. Por eso este conjunto ya no sirve para medir cobertura
    (eso lo hace `narrables`, conductual) y se usa únicamente para la dirección de
    huérfanos, que es donde una clave literal fuera de Capa 1 sí sería un defecto.
    """
    return _claves_narratives()


def _pain_ids_narrables(universo: Set[str]) -> Set[str]:
    """Sonda conductual: qué pain_ids puede narrar realmente `_pain_to_brecha`.

    Valida la **derivación** en vez de comparar dos dicts literales, que es lo que el AC de
    B3 pide cuando narratives se deriva de Capa 1. Es además inmune a la forma de la tabla:
    mide el guard `if pain.id not in narratives: return None` por su comportamiento, no por
    su sintaxis.
    """
    generador = V4DiagnosticGenerator()
    narrables = set()
    for pain_id in universo:
        entrada = PainSolutionMapper.PAIN_SOLUTION_MAP[pain_id]
        brecha = generador._pain_to_brecha(
            Pain(
                id=pain_id,
                name=entrada.get("name", pain_id),
                description=entrada.get("description", ""),
                severity="medium",
                detected_by="bijection_lock",
                confidence=0.5,
            ),
            region="eje_cafetero",
            audit_result=None,
        )
        if brecha is not None:
            narrables.add(pain_id)
    return narrables


@pytest.fixture(scope="module")
def narrables(capa1) -> Set[str]:
    return _pain_ids_narrables(capa1)


# =============================================================================
# Arista 1 — mapa ↔ emisión (ambas direcciones)
# =============================================================================

def test_todo_pain_del_mapa_tiene_emision_o_esta_diferido(capa1, emitidos):
    """V1: los 9 pains muertos. Ningún pain puede quedarse sin decisión."""
    sin_decision = sorted(capa1 - emitidos - set(PAINS_DIFERIDOS))
    assert not sin_decision, (
        "PAIN_SOLUTION_MAP declara pain_ids que detect_pains no emite y no están "
        f"registrados como diferidos: {sin_decision}. Implementar la emisión (con señal de "
        "dato verificable), retirar el pain, o registrar la decisión en PAINS_DIFERIDOS con "
        "motivo y seguimiento. Ver evidence/FASE-B/decision-pains-muertos.md."
    )


def test_toda_emision_esta_en_el_mapa(emitidos, capa1):
    """Dirección inversa: emitir un pain que Capa 1 no declara lo deja sin asset."""
    huerfanos = sorted(emitidos - capa1)
    assert not huerfanos, (
        f"detect_pains emite pain_ids ausentes de PAIN_SOLUTION_MAP: {huerfanos}"
    )


# =============================================================================
# Arista 2 — mapa ↔ narrativa (N-A1, ambas direcciones)
# =============================================================================

def test_narrativa_es_total_sobre_capa1(capa1, narrables):
    """N-A1: sin narrativa el pain rebota en `_pain_to_brecha` y no llega al documento.

    Sondado conductualmente (¿devuelve None?) en vez de comparando claves literales, porque
    B2 decidió derivar el complemento desde Capa 1 en lugar de inflar el dict (L-NC4).

    La cobertura es TOTAL, sin excepción para diferidos: es lo que vuelve estructuralmente
    inalcanzable el guard `if pain.id not in narratives: return None` para cualquier pain de
    Capa 1. Si un diferido dejara de serlo, la brecha ya sabe narrarse sola.
    """
    sin_narrativa = sorted(capa1 - narrables)
    assert not sin_narrativa, (
        "PAIN_SOLUTION_MAP declara pain_ids que `_pain_to_brecha` no sabe narrar: "
        f"{sin_narrativa}. Los descarta con `return None` y la brecha nunca llega al "
        "diagnóstico, aunque detect_pains la emita."
    )


def test_narratives_no_tiene_huerfanos(narrados, capa1):
    """FASE-A midió 0 huérfanos; este candado preserva ese 0.

    Duplica deliberadamente test_narratives_subset_de_capa1 (registro #13 de FASE-A):
    aquel fija el subconjunto como contrato de registro, este lo fija como arista de la
    biyección triple. Ambos deben seguir en verde.
    """
    huerfanos = sorted(narrados - capa1)
    assert not huerfanos, (
        f"`narratives` habla de pain_ids que no existen en Capa 1: {huerfanos}"
    )


def test_toda_emision_tiene_narrativa(emitidos, narrables):
    """El defecto compuesto: emitido Y descartado. FASE-A midió 2 (low_ota_divergence,
    no_ga4_enhanced). Es la arista que vuelve invisible una caída en producción."""
    descartados = sorted(emitidos - narrables)
    assert not descartados, (
        f"detect_pains emite pain_ids que `_pain_to_brecha` descarta en silencio: "
        f"{descartados}. La brecha se detecta, se paga el costo de detectarla, y no aparece "
        "en ningún documento."
    )


# =============================================================================
# Arista 3 — el registro de diferidos no es un estacionamiento
# =============================================================================

def test_diferidos_estan_en_capa1(capa1):
    """Un pain diferido que no está en Capa 1 es una entrada fósil del registro."""
    colgados = sorted(set(PAINS_DIFERIDOS) - capa1)
    assert not colgados, (
        f"PAINS_DIFERIDOS registra pain_ids ausentes de PAIN_SOLUTION_MAP: {colgados}. "
        "Si el pain fue retirado, eliminar también su entrada del registro."
    )


def test_diferido_no_tiene_emision(emitidos):
    """Si un diferido gana emisión, dejó de estar diferido: hay que sacarlo del registro.

    Sin este test el registro se vuelve un basurero permanente que exime del candado a
    pains que ya funcionan.
    """
    ya_emiten = sorted(set(PAINS_DIFERIDOS) & emitidos)
    assert not ya_emiten, (
        f"Estos pains diferidos ya tienen punto de emisión: {ya_emiten}. Eliminarlos de "
        "PAINS_DIFERIDOS (cerrando el seguimiento asociado): la narrativa ya la deriva "
        "Capa 1, no hay segunda tabla que actualizar."
    )


def test_diferidos_forman_particion_con_emisiones(capa1, emitidos):
    """Capa 1 = emitidos ⊎ PAINS_DIFERIDOS: la partición completa, sin solapamiento.

    Es la forma fuerte de AC4 — «0 pains muertos sin decisión». La partición es del lado de
    la emisión porque ahí es donde se tomó la decisión: cada pain de Capa 1 o tiene señal de
    dato verificable que lo emite, o tiene un motivo registrado de por qué no.
    """
    solapamiento = sorted(set(PAINS_DIFERIDOS) & emitidos)
    assert not solapamiento, f"pain_ids a la vez diferidos y emitidos: {solapamiento}"
    sin_cubrir = sorted(capa1 - emitidos - set(PAINS_DIFERIDOS))
    assert not sin_cubrir, f"pain_ids de Capa 1 sin emisión ni decisión: {sin_cubrir}"


@pytest.mark.parametrize("pain_id", sorted(PAINS_DIFERIDOS))
def test_cada_diferido_tiene_motivo_y_seguimiento(pain_id):
    """La excepción debe ser auditable: motivo sustantivo + ID de seguimiento abierto."""
    motivo, seguimiento = PAINS_DIFERIDOS[pain_id]
    assert len(motivo) >= 80, (
        f"PAINS_DIFERIDOS['{pain_id}'] tiene un motivo demasiado corto para ser auditable"
    )
    assert seguimiento.startswith("S-B"), (
        f"PAINS_DIFERIDOS['{pain_id}'] no referencia un seguimiento del formato S-Bn"
    )


# =============================================================================
# Arista 4 — la narrativa derivada no introduce prosa paralela (L-NC4)
# =============================================================================

def _pain_ids_narrados_por_derivacion() -> List[str]:
    """Capa 1 menos las claves del dict literal: los que `_pain_to_brecha` narra derivando.

    Calculado, no escrito a mano. Una tupla hardcodeada fosiliza en el primer cambio: si Capa 1
    crece, el pain nuevo entraría sin el chequeo de que su texto sale del canónico; si alguien
    literaliza una entrada, el test fallaría contra prosa que sí es legítimamente literal.
    """
    return sorted(set(PainSolutionMapper.PAIN_SOLUTION_MAP) - _claves_narratives())


PAINS_NARRADOS_POR_DERIVACION = _pain_ids_narrados_por_derivacion()


@pytest.mark.parametrize("pain_id", PAINS_NARRADOS_POR_DERIVACION)
def test_narrativa_derivada_sale_de_capa1(pain_id):
    """El texto de la brecha debe salir de Capa 1, no de una tabla paralela nueva.

    Se construye el Pain **sin** nombre ni descripción a propósito: `_pain_to_brecha` hace
    `nombre = pain.name or narrative['nombre']`, así que con el Pain vacío lo que llega al
    documento es exclusivamente lo que la narrativa aporta. Si alguien resolviera la
    derivación escribiendo prosa nueva (el defecto que L-NC4 prohíbe), este test lo atrapa.
    """
    entrada = PainSolutionMapper.PAIN_SOLUTION_MAP[pain_id]
    brecha = V4DiagnosticGenerator()._pain_to_brecha(
        Pain(
            id=pain_id,
            name="",
            description="",
            severity="medium",
            detected_by="bijection_lock",
            confidence=0.5,
        ),
        region="eje_cafetero",
        audit_result=None,
    )
    assert brecha is not None, f"{pain_id} se descarta en silencio"
    assert brecha["pain_id"] == pain_id
    assert brecha["nombre"] == entrada["name"], (
        f"{pain_id}: el nombre de la brecha no viene de Capa 1 sino de prosa paralela"
    )
    assert brecha["detalle"] == entrada["description"], (
        f"{pain_id}: el detalle de la brecha no viene de Capa 1 sino de prosa paralela"
    )


# Solo los pains que SÍ pueden llegar a un documento: narrados por derivación Y con punto de
# emisión. Un pain diferido nunca alcanza `_normalize_weights`, así que exigirle peso en YAML
# sería configuración especulativa. El conjunto se mantiene solo: cuando un seguimiento
# (S-B1…S-B6) cablee una emisión, este test empieza a exigir su peso regional.
PAINS_DERIVADOS_ALCANZABLES = sorted(
    set(PAINS_NARRADOS_POR_DERIVACION) & _pain_ids_emitidos()
)


@pytest.mark.parametrize("pain_id", PAINS_DERIVADOS_ALCANZABLES)
def test_peso_de_impacto_no_vive_de_un_default_mudo(pain_id):
    """S14/C-5: un pain cuyo peso salga solo del fallback Python es degradación silenciosa
    en código dinero-adyacente — `impacto` alimenta `_normalize_weights` y por tanto los
    porcentajes impresos en el diagnóstico.

    Se verifica que el YAML de las 4 regiones declare el peso explícitamente.
    """
    from modules.common.yaml_loader import load_yaml_config

    config = load_yaml_config("regional_benchmarks.yaml")
    regiones = (config or {}).get("regions", {})
    assert regiones, "no se pudo leer config/regional_benchmarks.yaml"
    sin_peso = sorted(
        region for region, datos in regiones.items()
        if pain_id not in (datos.get("pain_narratives") or {})
    )
    assert not sin_peso, (
        f"{pain_id} no tiene peso de impacto declarado en {sin_peso}: viviría del fallback "
        "Python en esas regiones. Añadirlo a las 4 (ver decision-pains-muertos.md §4)."
    )
