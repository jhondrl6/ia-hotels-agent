"""Contract tests del registro canónico de identidad servicio↔asset↔pain (FASE-A).

CIERRA: AC1 (registro canónico + 0 IDs fantasma), AC2 (drift «8 vs 7» en 3 copias),
AC3 (`ASSET_TO_PAIN_ID["monthly_report"]` a favor del canónico).
CORRIGE: V2 (6 IDs fantasma), V3 (fragmentación + perla monthly_report), V14 (drift 8↔7).

DISEÑO — dos capas (decisión arquitectónica de FASE-A, `evidence/FASE-A/censo-registros.md` §5):

  Capa 1 — `PainSolutionMapper.PAIN_SOLUTION_MAP` sigue siendo el universo canónico de
           pain_ids. Regla: ningún registro puede declarar un pain_id ausente de ella.
           No se modifica su contenido (la biyección mapa↔emisión es FASE-B).
  Capa 2 — `modules/common/service_identity.SERVICE_IDENTITIES`: identidad canónica del
           servicio comercial (key, nombre, asset, pain, brechas, si cuenta en alignment).

Los registros que responden «¿qué pain monetiza este servicio?» DERIVAN de Capa 2.
Los que responden otra pregunta (enrutamiento de generación, puente al scorer, narrativa
comercial) se VALIDAN contra Capa 1 sin derivar: derivarlos exigiría duplicar tablas
(guardrail L-NC4) o cambiar semántica de fases posteriores.

ANTI-LECCIONES APLICADAS
  L-NC10 — ningún test fija un valor comercial. Todo esperado se CALCULA desde la fuente.
           En particular el contrato narrativa↔fuente PROHÍBE la forma fosilizante
           (numeral hardcodeado junto a «servic*») en vez de comparar contra un número.
  L-NC4  — el canónico no declara textos de pain; `test_canonico_no_redeclara_tablas`.
  FASE-SR-A — guardián AST, no regex: se analiza el árbol, no el texto del código.
"""

import ast
import io
import re
import sys
import tokenize
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

import pytest

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

sys.path.insert(0, str(REPO_ROOT))

from modules.asset_generation.asset_catalog import ASSET_CATALOG
from modules.asset_generation.conditional_generator import ConditionalGenerator
from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper
from modules.quality.asset_semantics_validator import INVALID_MAPPINGS

PAIN_SOLUTION_MAP = PainSolutionMapper.PAIN_SOLUTION_MAP
PAIN_IDS_CANONICOS: Set[str] = set(PAIN_SOLUTION_MAP)
ASSET_TYPES_CONOCIDOS: Set[str] = set(ASSET_CATALOG)

CANONICO_REL = "modules/common/service_identity.py"

# Alcance exacto del AC1 de FASE-A (mismo alcance que el grep del prompt).
ALCANCE_FANTASMAS = ("modules/commercial_documents", "modules/asset_generation")

# Los 6 IDs fantasma de V2. Confirmados contra PAIN_SOLUTION_MAP en A1:
#   no_llms_txt        → equivalente canónico missing_llmstxt
#   ia_crawler_blocked → equivalente canónico ai_crawler_blocked
#   no_speakable / weak_brand_signals / no_entity_schema / no_factual_data → sin
#   equivalente: el pain_id pasa a None (no se monetiza lo que no existe).
IDS_FANTASMA = (
    "no_speakable",
    "no_llms_txt",
    "ia_crawler_blocked",
    "weak_brand_signals",
    "no_entity_schema",
    "no_factual_data",
)

# Narrativa que fosiliza el conteo: numeral pegado a «servic*», en cualquiera de las
# dos direcciones observadas en las 3 copias del drift V14.
NUMERAL_ANTES = re.compile(r"\b\d+\s+servic", re.IGNORECASE)
NUMERAL_DESPUES = re.compile(r"\bservic\w*\s*\(\d+", re.IGNORECASE)

# Módulos cuya narrativa habla del conteo de servicios del registro de identidad.
# Fuera de alcance a propósito: `analyzers/gap_analyzer.py` (copy comercial del legado
# spark, no migrado en FASE-A), `quality_gates/alignment_result.py` y
# `quality_gates/publication_gates.py` (prohibidos en esta fase: FASE-C/F/G) — sus
# «0 servicios comprometidos» es un mensaje legítimo, no un conteo de catálogo.
#
# FASE-HOTFIX (S-C3 textual, L-V2): `coherence_validator.py` entra a la tupla. Su
# mensaje de `promised_assets_exist` es la superficie que lee el cliente y antes
# no estaba cubierta por el candado. Medido antes de extender: 0 coincidencias de
# la forma numeral en ese archivo, así que la cobertura crece sin relajarse.
MODULOS_NARRATIVA = (
    "modules/asset_generation/proposal_asset_alignment.py",
    "modules/asset_generation/conditional_generator.py",
    "modules/asset_generation/pain_ledger.py",
    "modules/common/service_identity.py",
    "modules/commercial_documents/coherence_validator.py",
    "modules/commercial_documents/service_catalog.py",
    "modules/commercial_documents/v4_proposal_generator.py",
    "modules/commercial_documents/v4_diagnostic_generator.py",
)


# =============================================================================
# Utilidades AST (guardián, no regex)
# =============================================================================

def _ruta(rel: str) -> Path:
    path = REPO_ROOT / rel
    assert path.exists(), f"No existe {rel}"
    return path


def _tree(rel: str) -> ast.Module:
    return ast.parse(_ruta(rel).read_text(encoding="utf-8"))


def _targets(node) -> List[str]:
    if isinstance(node, ast.Assign):
        return [t.id for t in node.targets if isinstance(t, ast.Name)]
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return [node.target.id]
    return []


def _binding(rel: str, nombre: str):
    """Devuelve el nodo de valor asignado a `nombre` en cualquier ámbito.

    Recorre el módulo entero porque tres de los registros censados
    (`ASSET_TO_PAIN_ID`, `service_brecha_candidates`, `pain_to_type`, `narratives`)
    viven dentro de un método, no a nivel de módulo.
    """
    tree = _tree(rel)
    encontrados = [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        and nombre in _targets(node)
        and getattr(node, "value", None) is not None
    ]
    assert encontrados, f"No se encontró la asignación de {nombre} en {rel}"
    return encontrados[0], tree


def _es_literal(node) -> bool:
    return isinstance(node, (ast.Dict, ast.List, ast.Set, ast.Tuple))


def _nombres_referidos(node) -> Set[str]:
    out: Set[str] = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            out.add(n.id)
        elif isinstance(n, ast.Attribute):
            out.add(n.attr)
    return out


def _importa_fuente_unica(tree) -> bool:
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom):
            if "service_identity" in (n.module or "") or "pain_solution_mapper" in (n.module or ""):
                return True
        elif isinstance(n, ast.Import):
            if any("service_identity" in (a.name or "") for a in n.names):
                return True
    return False


def _bindings_derivados(tree, fuentes: Set[str]) -> Set[str]:
    """Cierre transitivo: nombres del módulo cuyo valor referencia una fuente única.

    Necesario porque `ALL_PROMISED_SERVICES = list(PROPOSAL_SERVICE_TO_ASSET.keys())`
    no nombra el canónico directamente: nombra un binding que sí lo hace.
    """
    pendientes: Dict[str, ast.AST] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)) and getattr(node, "value", None) is not None:
            for nombre in _targets(node):
                pendientes.setdefault(nombre, node.value)
    derivados: Set[str] = set()
    for _ in range(len(pendientes) + 1):
        for nombre, value in pendientes.items():
            if nombre in derivados:
                continue
            if _nombres_referidos(value) & (fuentes | derivados):
                derivados.add(nombre)
    return derivados


def _claves_literales(node) -> List[str]:
    assert isinstance(node, ast.Dict), "se esperaba un literal dict"
    return [k.value for k in node.keys if isinstance(k, ast.Constant) and isinstance(k.value, str)]


def _tokens_texto(rel: str) -> Iterable[Tuple[int, str]]:
    with _ruta(rel).open("rb") as fh:
        for tok in tokenize.tokenize(fh.readline):
            if tok.type in (tokenize.COMMENT, tokenize.STRING):
                yield tok.start[0], tok.string


def _canonico():
    from modules.common import service_identity

    return service_identity


# =============================================================================
# SECCIÓN 1 — AC1: el canónico existe y es íntegro
# =============================================================================

def test_existe_modulo_canonico_de_identidad():
    assert _ruta(CANONICO_REL).exists(), (
        f"Falta {CANONICO_REL}: FASE-A AC1 exige UNA fuente de identidad "
        f"servicio↔asset↔pain de la que deriven los registros censados."
    )
    canon = _canonico()
    assert getattr(canon, "SERVICE_IDENTITIES", None), "SERVICE_IDENTITIES vacío o ausente"


def test_identidades_canonicas_tripla_completa_y_unica():
    canon = _canonico()
    identidades = canon.SERVICE_IDENTITIES
    vistos_key, vistos_nombre, vistos_asset, vistos_pain = set(), set(), set(), set()
    for i in identidades:
        for campo in ("key", "service_name", "asset_type", "pain_id", "description"):
            assert getattr(i, campo, None), f"{i!r} tiene '{campo}' vacío"
        assert isinstance(i.brecha_candidates, tuple), (
            f"{i.key}: brecha_candidates debe ser tupla (inmutable) para que ningún "
            f"consumidor la mute en caliente"
        )
        assert isinstance(i.counts_in_alignment, bool), f"{i.key}: counts_in_alignment debe ser bool"
        for campo, vistos in (("key", vistos_key), ("service_name", vistos_nombre),
                              ("asset_type", vistos_asset), ("pain_id", vistos_pain)):
            valor = getattr(i, campo)
            assert valor not in vistos, (
                f"{campo}='{valor}' duplicado en SERVICE_IDENTITIES: dos servicios no "
                f"pueden compartir identidad (eso ES el drift que V3 documenta)"
            )
            vistos.add(valor)


def test_asset_types_canonicos_existen_en_asset_catalog():
    for i in _canonico().SERVICE_IDENTITIES:
        assert i.asset_type in ASSET_TYPES_CONOCIDOS, (
            f"{i.key}: asset_type '{i.asset_type}' no existe en ASSET_CATALOG "
            f"(N-A4: 'voice_guide' era exactamente este error)"
        )


def test_pain_ids_canonicos_existen_en_pain_solution_map():
    """Capa 1: el canónico de Capa 2 no puede inventar pains."""
    for i in _canonico().SERVICE_IDENTITIES:
        assert i.pain_id in PAIN_IDS_CANONICOS, (
            f"{i.key}: pain_id '{i.pain_id}' ausente de PAIN_SOLUTION_MAP"
        )
        for b in i.brecha_candidates:
            assert b in PAIN_IDS_CANONICOS, (
                f"{i.key}: brecha_candidate '{b}' ausente de PAIN_SOLUTION_MAP"
            )


# =============================================================================
# SECCIÓN 2 — AC1 / V2: cero IDs fantasma
# =============================================================================

@pytest.mark.parametrize("fantasma", IDS_FANTASMA)
def test_cero_ids_fantasma_en_alcance_del_ac1(fantasma):
    """Un pain_id que no existe en PAIN_SOLUTION_MAP no puede disparar nada: la brecha
    se declara y nunca se detecta. Es el mecanismo exacto de V2."""
    apariciones = []
    for carpeta in ALCANCE_FANTASMAS:
        for path in sorted((REPO_ROOT / carpeta).rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            for n, linea in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if fantasma in linea:
                    apariciones.append(f"{path.relative_to(REPO_ROOT)}:{n}")
    assert not apariciones, (
        f"ID fantasma '{fantasma}' sigue presente (no existe en PAIN_SOLUTION_MAP): "
        + ", ".join(apariciones)
    )


def test_elemento_kb_no_declara_assets_fantasma():
    """Complemento de N-A4: el asset de la tupla también debe existir."""
    from modules.commercial_documents.v4_diagnostic_generator import ELEMENTO_KB_TO_PAIN_ID

    for kb, tupla in ELEMENTO_KB_TO_PAIN_ID.items():
        for posicion, asset in ((1, tupla[1]), (2, tupla[2])):
            if asset is None:
                continue
            assert asset in ASSET_TYPES_CONOCIDOS, (
                f"ELEMENTO_KB_TO_PAIN_ID['{kb}'][{posicion}] = '{asset}' no existe en "
                f"ASSET_CATALOG"
            )


# =============================================================================
# SECCIÓN 3 — V3: biyección de atribución asset↔pain en los registros de propuesta
# =============================================================================

def _atribuciones_de_propuesta() -> Dict[str, Set[Tuple[str, str]]]:
    """asset_type → {(pain_id, registro)} en los registros que responden la MISMA
    pregunta: ¿qué pain monetiza este servicio en la propuesta comercial?

    Se excluyen a propósito los que responden otra pregunta:
      · ELEMENTO_KB_TO_PAIN_ID — elemento de knowledge-base → (pain, asset que remedia).
        Un mismo asset remedia varios gaps de KB con pains distintos; eso no es drift.
      · ConditionalGenerator.PAIN_TO_ASSET — enrutamiento de generación de archivos.
      · PAIN_TO_PRESENCE_ASSET — oráculo de verificación en sitio (FASE-F).
    """
    from modules.asset_generation.proposal_asset_alignment import PROPOSAL_SERVICE_TO_ASSET
    from modules.commercial_documents.service_catalog import SERVICE_CATALOG

    canon = _canonico()
    por_nombre = {i.service_name: i for i in canon.SERVICE_IDENTITIES}
    out: Dict[str, Set[Tuple[str, str]]] = {}

    def anotar(asset: Optional[str], pain: Optional[str], registro: str) -> None:
        if asset and pain:
            out.setdefault(asset, set()).add((pain, registro))

    for i in canon.SERVICE_IDENTITIES:
        anotar(i.asset_type, i.pain_id, "SERVICE_IDENTITIES")

    for entry in SERVICE_CATALOG.values():
        anotar(entry.asset_type, entry.pain_id, "SERVICE_CATALOG")

    for servicio, asset in PROPOSAL_SERVICE_TO_ASSET.items():
        identidad = por_nombre.get(servicio)
        anotar(asset, identidad.pain_id if identidad else None, "PROPOSAL_SERVICE_TO_ASSET")

    for nombre in ("ASSET_TO_PAIN_ID", "service_brecha_candidates"):
        node, _ = _binding("modules/commercial_documents/v4_proposal_generator.py", nombre)
        if isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                if not (isinstance(k, ast.Constant) and isinstance(k.value, str)):
                    continue
                if isinstance(v, ast.Constant) and isinstance(v.value, str):
                    anotar(k.value, v.value, nombre)
                elif isinstance(v, (ast.List, ast.Tuple, ast.Set)):
                    for e in v.elts:
                        if isinstance(e, ast.Constant) and isinstance(e.value, str):
                            anotar(k.value, e.value, nombre)
    return out


def test_un_asset_no_se_atribuye_a_pains_distintos_entre_registros():
    """Caso V3: `ASSET_TO_PAIN_ID['monthly_report'] = 'no_faq_schema'` mientras
    SERVICE_CATALOG decía `no_monthly_report`. Dos verdades para el mismo asset.

    El esperado se CALCULA desde el canónico (anti-lección L-NC10): pain canónico más
    las brechas declaradas por esa identidad, más las divergencias revisadas a mano.
    """
    canon = _canonico()
    divergencias = getattr(canon, "REVIEWED_TRIGGER_DIVERGENCES", frozenset())
    permitidos: Dict[str, Set[str]] = {}
    for i in canon.SERVICE_IDENTITIES:
        conjunto = {i.pain_id, *i.brecha_candidates}
        if i.key in divergencias:
            conjunto |= set(PAIN_IDS_CANONICOS)
        permitidos[i.asset_type] = conjunto

    culpables = []
    for asset, pares in _atribuciones_de_propuesta().items():
        for pain, registro in sorted(pares):
            if pain not in permitidos.get(asset, set()):
                culpables.append(f"{registro}: {asset}→{pain}")
    assert not culpables, (
        "Atribuciones asset→pain fuera del canónico: " + ", ".join(culpables)
        + " || Corregir el registro derivado o declarar la divergencia en "
        "REVIEWED_TRIGGER_DIVERGENCES con su justificación."
    )


def test_monthly_report_resuelto_a_favor_del_canonico():
    """AC3 explícito. La perla de V3 era un fósil de la inversión de claves previa a
    FASE-2 (asset_type usado como pain_id), ya documentada en
    `asset_semantics_validator.py:23-25`."""
    node, _ = _binding("modules/commercial_documents/v4_proposal_generator.py", "ASSET_TO_PAIN_ID")
    if isinstance(node, ast.Dict):
        literal = {
            k.value: v.value
            for k, v in zip(node.keys, node.values)
            if isinstance(k, ast.Constant) and isinstance(v, ast.Constant)
        }
        assert literal.get("monthly_report") != "no_faq_schema", (
            "ASSET_TO_PAIN_ID sigue atribuyendo monthly_report a no_faq_schema (V3)"
        )
    identidad = {i.key: i for i in _canonico().SERVICE_IDENTITIES}["informe_mensual"]
    assert identidad.pain_id in PAIN_IDS_CANONICOS
    assert identidad.asset_type == "monthly_report"


def test_divergencias_trigger_atribucion_declaradas_y_justificadas():
    """§5.4 del censo: trigger (qué pain dispara el servicio) ≠ atribución (qué brecha
    se le imputa en la tabla). Ambas mitades son legítimas y las sostiene
    PAIN_SOLUTION_MAP, pero NINGÚN registro las expresaba. Ahora se declaran.

    Contrato a dos bandas: toda divergencia real debe estar declarada y ninguna
    declaración obsoleta puede sobrevivir. El complemento siempre-activo
    (`counts_in_alignment=False`) queda exento: no se le atribuye ninguna brecha.
    """
    canon = _canonico()
    declaradas = getattr(canon, "REVIEWED_TRIGGER_DIVERGENCES", None)
    assert declaradas is not None, (
        "REVIEWED_TRIGGER_DIVERGENCES ausente: la divergencia trigger↔atribución "
        "quedaría implícita otra vez"
    )
    identidades = {i.key: i for i in canon.SERVICE_IDENTITIES}
    for key in declaradas:
        assert key in identidades, f"REVIEWED_TRIGGER_DIVERGENCES cita '{key}', que no es un servicio"

    for i in canon.SERVICE_IDENTITIES:
        if not i.counts_in_alignment:
            assert not i.brecha_candidates, (
                f"{i.key} no cuenta en alignment pero declara brechas atribuibles: "
                f"decidir una de las dos cosas"
            )
            continue
        diverge = i.pain_id not in i.brecha_candidates
        assert diverge == (i.key in declaradas), (
            f"{i.key}: trigger '{i.pain_id}' vs atribución {i.brecha_candidates} — "
            f"diverge={diverge} pero declarado={i.key in declaradas}. "
            f"Declararlo con justificación o corregir la identidad."
        )


# =============================================================================
# SECCIÓN 4 — Guardián AST: derivar, no copiar
# =============================================================================

# (archivo, nombre del binding) que DEBEN construirse desde una fuente única.
REGISTROS_DERIVADOS = [
    ("modules/asset_generation/proposal_asset_alignment.py", "PROPOSAL_SERVICE_TO_ASSET"),
    ("modules/asset_generation/proposal_asset_alignment.py", "ALL_PROMISED_SERVICES"),
    ("modules/asset_generation/pain_ledger.py", "NORMALIZATION_RULES"),
    ("modules/commercial_documents/service_catalog.py", "SERVICE_CATALOG"),
    ("modules/commercial_documents/v4_proposal_generator.py", "ASSET_TO_PAIN_ID"),
    ("modules/commercial_documents/v4_proposal_generator.py", "service_brecha_candidates"),
]


@pytest.mark.parametrize("rel,nombre", REGISTROS_DERIVADOS)
def test_registro_derivado_no_es_una_copia_literal(rel, nombre):
    """Una copia literal es drift garantizado: nada la obliga a seguir a la fuente.
    El esperado no es una lista de nombres fijos — se calcula la superficie pública
    del canónico más las fuentes de Capa 1 ya legitimadas."""
    canon = _canonico()
    fuentes = {n for n in dir(canon) if not n.startswith("_")}
    fuentes |= {"PAIN_SOLUTION_MAP", "PainSolutionMapper", "PROPOSAL_SERVICE_TO_ASSET"}

    value, tree = _binding(rel, nombre)
    assert not _es_literal(value), (
        f"{rel}: `{nombre}` sigue siendo un literal. Debe derivarse de "
        f"modules/common/service_identity (Capa 2) o de PAIN_SOLUTION_MAP (Capa 1); "
        f"una copia independiente es exactamente el drift que V3/V14 documentan."
    )
    assert _importa_fuente_unica(tree), f"{rel} no importa ninguna fuente única"
    derivados = _bindings_derivados(tree, fuentes)
    assert _nombres_referidos(value) & (fuentes | derivados), (
        f"{rel}: `{nombre}` no referencia el canónico ni ningún binding derivado de él"
    )


def test_canonico_no_redeclara_tablas_paralelas():
    """Guardrail L-NC4: el canónico debe añadir IDENTIDAD, no una nueva tabla de
    pain_id→texto que compita con PAIN_SOLUTION_MAP."""
    canon = _canonico()
    permitidos = {"ServiceIdentity", "SERVICE_IDENTITIES", "REVIEWED_TRIGGER_DIVERGENCES"}
    tree = _tree(CANONICO_REL)
    colecciones = set()
    for node in tree.body:
        for nombre in _targets(node):
            if nombre.startswith("_"):
                continue
            colecciones.add(nombre)
    publicas = {
        n for n in colecciones
        if isinstance(getattr(canon, n, None), (dict, list, tuple, set, frozenset))
    }
    extra = publicas - permitidos
    assert not extra, (
        f"El canónico declara colecciones no previstas {sorted(extra)}: revisar si son "
        f"tabla paralela (L-NC4) o si el contrato debe ampliarse con justificación."
    )
    textos_pain = set(PAIN_SOLUTION_MAP[p].get("name") for p in PAIN_IDS_CANONICOS)
    for i in canon.SERVICE_IDENTITIES:
        assert i.description not in textos_pain, (
            f"{i.key}.description duplica el texto de PAIN_SOLUTION_MAP: el canónico no "
            f"debe redeclarar narrativa de pain (L-NC4)"
        )


# =============================================================================
# SECCIÓN 5 — AC2 / V14: contrato narrativa↔fuente
# =============================================================================

@pytest.mark.parametrize("rel", MODULOS_NARRATIVA)
def test_narrativa_no_hardcodea_conteo_de_servicios(rel):
    """El drift «8 vs 7» sobrevivió porque la narrativa fijaba un número que el código
    ya no cumplía. Comparar el número contra la fuente solo lo esconde hasta el próximo
    cambio: la forma duradera es PROHIBIR el numeral y nombrar el registro.

    (Anti-lección L-NC10: no se fija `== 7` ni `== 8` en ningún sitio.)
    """
    if not (REPO_ROOT / rel).exists():
        pytest.skip(f"{rel} aún no existe")
    culpables = []
    for lineno, texto in _tokens_texto(rel):
        limpio = " ".join(texto.split())
        if NUMERAL_ANTES.search(limpio) or NUMERAL_DESPUES.search(limpio):
            culpables.append(f"L{lineno}: {limpio[:110]}")
    assert not culpables, (
        f"{rel} hardcodea un conteo de servicios en narrativa: " + " | ".join(culpables)
        + " || Nombrar el registro (PROPOSAL_SERVICE_TO_ASSET / SERVICE_IDENTITIES) en "
        "vez del número: el número es lo que derivó en «8 vs 7» (V14)."
    )


# Registros cuyo `len()` describe el CATALOGO, no lo verificado en runtime.
REGISTROS_ESTATICOS = (
    "PROPOSAL_SERVICE_TO_ASSET",
    "ALL_PROMISED_SERVICES",
    "SERVICE_IDENTITIES",
    "SERVICE_CATALOG",
    "ASSET_CATALOG",
    "PAIN_SOLUTION_MAP",
)


def _funciones_con_mensaje(rel: str) -> List[Tuple[str, List[ast.expr]]]:
    """`(nombre, [expresiones del keyword message])` de cada función del módulo."""
    out: List[Tuple[str, List[ast.expr]]] = []
    for node in ast.walk(_tree(rel)):
        if not isinstance(node, ast.FunctionDef):
            continue
        mensajes = [
            kw.value
            for call in ast.walk(node)
            if isinstance(call, ast.Call)
            for kw in call.keywords
            if kw.arg == "message"
        ]
        if mensajes:
            out.append((node.name, mensajes))
    return out


@pytest.mark.parametrize("rel", MODULOS_NARRATIVA)
def test_mensaje_no_narra_el_tamano_de_un_registro_estatico(rel):
    """FASE-HOTFIX (S-C3, mitad textual) — el candado que la forma numeral no ve.

    `test_narrativa_no_hardcodea_conteo_de_servicios` prohíbe el **numeral**. El
    defecto medido por VERIFY en el artefacto del cliente no usaba un numeral:
    usaba `len(REGISTRO)`, que imprime un número derivado del catálogo estático
    como si fuera el conteo verificado en runtime. Misma clase (B2 / L-V3), otra
    forma — y por eso el candado de forma no la frenó (L-V2).

    Regla mecánica: un `message` no puede contener `len(<registro estático>)`.
    """
    if not (REPO_ROOT / rel).exists():
        pytest.skip(f"{rel} aún no existe")
    culpables = []
    for function_name, mensajes in _funciones_con_mensaje(rel):
        for msg in mensajes:
            for call in ast.walk(msg):
                if (
                    isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Name)
                    and call.func.id == "len"
                    and call.args
                    and isinstance(call.args[0], ast.Name)
                    and call.args[0].id in REGISTROS_ESTATICOS
                ):
                    culpables.append(
                        f"{rel}::{function_name}(message=...len({call.args[0].id}))"
                    )
    assert not culpables, (
        "Un mensaje narra el tamaño de un catálogo, no lo verificado en runtime: "
        + " | ".join(culpables)
        + " || Narrar el conteo de la pasada (partición / matriz) o nombrar el "
        "registro sin contar: el número impreso es la segunda representación del "
        "hecho que ya mide el código (L-V3)."
    )


def test_alignment_excluye_informe_mensual_por_diseno():
    """BUG-10 / FASE-3: `monthly_report` es complemento siempre-activo, no servicio
    dirigido por pain. Contar 8 en alignment empeora coverage_ratio (0.571→0.500,
    medido en dossier §8.5) — de ahí la restricción «NO agregar el 8º servicio».

    El esperado se calcula desde `counts_in_alignment`, no se fija en 7.
    """
    from modules.asset_generation.proposal_asset_alignment import (
        ALL_PROMISED_SERVICES,
        PROPOSAL_SERVICE_TO_ASSET,
    )

    esperados = {i.service_name for i in _canonico().SERVICE_IDENTITIES if i.counts_in_alignment}
    assert set(PROPOSAL_SERVICE_TO_ASSET) == esperados, (
        "PROPOSAL_SERVICE_TO_ASSET diverge de las identidades con counts_in_alignment=True"
    )
    assert set(ALL_PROMISED_SERVICES) == esperados, (
        "ALL_PROMISED_SERVICES diverge del canónico"
    )
    excluidos = {i.service_name for i in _canonico().SERVICE_IDENTITIES if not i.counts_in_alignment}
    assert excluidos and not (excluidos & esperados)


# =============================================================================
# SECCIÓN 6 — Registros validados contra Capa 1 (no derivados)
# =============================================================================

def test_elemento_kb_valida_contra_capa1():
    from modules.commercial_documents.v4_diagnostic_generator import ELEMENTO_KB_TO_PAIN_ID

    invalidos = [
        f"{kb}→{tupla[0]}" for kb, tupla in ELEMENTO_KB_TO_PAIN_ID.items()
        if tupla[0] is not None and tupla[0] not in PAIN_IDS_CANONICOS
    ]
    assert not invalidos, (
        "ELEMENTO_KB_TO_PAIN_ID declara pain_ids fuera de Capa 1: " + ", ".join(invalidos)
    )


def test_pain_to_asset_valida_contra_capa1():
    invalidos = [p for p in ConditionalGenerator.PAIN_TO_ASSET if p not in PAIN_IDS_CANONICOS]
    assert not invalidos, f"PAIN_TO_ASSET declara pain_ids fuera de Capa 1: {invalidos}"
    fantasma = []
    for pain, asset in ConditionalGenerator.PAIN_TO_ASSET.items():
        for a in asset if isinstance(asset, (list, tuple)) else [asset]:
            if a not in ASSET_TYPES_CONOCIDOS:
                fantasma.append(f"{pain}→{a}")
    assert not fantasma, f"PAIN_TO_ASSET declara assets inexistentes: {fantasma}"


def test_pain_to_type_es_un_puente_valido():
    """Registro #10: pain_id (Capa 1) → brecha_type (namespace propio del scorer).
    Son DOS namespaces; confundirlos es lo que hizo parecer fantasma a `no_llms_txt`
    en el scorer. No se cambia su comportamiento (scoring = dinero): se fija el puente.

    El fallback silencioso a 'cms_defaults' queda registrado como insumo de FASE-C/F
    (misma familia que V6 `except Exception` y `precision_tier` default 'C').
    """
    from modules.financial_engine.opportunity_scorer import OpportunityScorer

    node, _ = _binding("modules/commercial_documents/v4_diagnostic_generator.py", "pain_to_type")
    puente = {
        k.value: v.value
        for k, v in zip(node.keys, node.values)
        if isinstance(k, ast.Constant) and isinstance(v, ast.Constant)
    }
    assert puente, "pain_to_type dejó de ser un literal: actualizar este contrato"
    tipos_scorer = set(OpportunityScorer.BRECHA_SEVERITY_MAP)
    dolado_pain = [k for k in puente if k not in PAIN_IDS_CANONICOS]
    dolado_tipo = [v for v in puente.values() if v not in tipos_scorer]
    assert not dolado_pain, f"pain_to_type: claves fuera de Capa 1: {dolado_pain}"
    assert not dolado_tipo, f"pain_to_type: valores fuera del universo del scorer: {dolado_tipo}"


def test_narratives_subset_de_capa1():
    """Registro #13. `if pain.id not in narratives: return None` (v4_diagnostic_generator)
    descarta en silencio los pain_ids sin narrativa — 11 hoy (N-A1). No se toca el guard
    (activaría brechas nuevas en el diagnóstico = narrativa comercial), pero se fija que
    ninguna narrativa hable de un pain inexistente. PRECONDICIÓN DURA de FASE-B."""
    node, _ = _binding("modules/commercial_documents/v4_diagnostic_generator.py", "narratives")
    claves = _claves_literales(node)
    assert claves, "narratives dejó de ser un literal: actualizar este contrato"
    fuera = [k for k in claves if k not in PAIN_IDS_CANONICOS]
    assert not fuera, f"narratives declara pain_ids fuera de Capa 1: {fuera}"


def test_invalid_mappings_valida_contra_capa1():
    """Registro #14 (`modules/quality/asset_semantics_validator.INVALID_MAPPINGS`).
    Su propio comentario :23-25 documenta que una auditoría FASE-2 lo encontró con las
    claves invertidas (asset_type en vez de pain_id) — el mismo defecto que produjo la
    perla de V3. Este contrato hace esa auditoría permanente."""
    dolado_pain = [k for k in INVALID_MAPPINGS if k not in PAIN_IDS_CANONICOS]
    dolado_asset = [
        f"{k}→{a}" for k, bloqueados in INVALID_MAPPINGS.items() for a in bloqueados
        if a not in ASSET_TYPES_CONOCIDOS
    ]
    assert not dolado_pain, f"INVALID_MAPPINGS: claves que no son pain_id: {dolado_pain}"
    assert not dolado_asset, f"INVALID_MAPPINGS: assets inexistentes: {dolado_asset}"


def test_normalization_rules_es_biyeccion_con_capa1():
    """N-A2: 26 reglas para 27 pains, con la clave obsoleta 'No WhatsApp Visible' y sin
    `low_seo_score`. Derivarlo de Capa 1 corrige ambos defectos a costo conductual cero:
    `normalize()` se aplica sobre `pain.id`, que ya viene canonicalizado."""
    from modules.asset_generation.pain_ledger import PainLedger

    NORMALIZATION_RULES = PainLedger.NORMALIZATION_RULES
    esperado = {v["name"]: k for k, v in PAIN_SOLUTION_MAP.items()}
    assert set(NORMALIZATION_RULES) == set(esperado), (
        f"NORMALIZATION_RULES no es biyección con PAIN_SOLUTION_MAP. "
        f"Sobran {sorted(set(NORMALIZATION_RULES) - set(esperado))}, "
        f"faltan {sorted(set(esperado) - set(NORMALIZATION_RULES))}"
    )
    assert NORMALIZATION_RULES == esperado, "NORMALIZATION_RULES mapea a un pain_id distinto"


def test_pain_to_presence_asset_valida_contra_capa1():
    """Registro #8b. NO se deriva: la derivación completa (filtrada por los assets
    verificables en sitio) daría 13 entradas contra 6 actuales y cambiaría la semántica
    de `apply_site_verification` — eso es FASE-F (V15, oráculo único de presencia).
    La brecha 6↔13 queda registrada como insumo de FASE-F."""
    from modules.asset_generation.pain_ledger import PainLedger

    PAIN_TO_PRESENCE_ASSET = PainLedger.PAIN_TO_PRESENCE_ASSET
    for pain, asset in PAIN_TO_PRESENCE_ASSET.items():
        assert pain in PAIN_IDS_CANONICOS, f"PAIN_TO_PRESENCE_ASSET: pain '{pain}' fuera de Capa 1"
        principal = PAIN_SOLUTION_MAP[pain].get("assets", [None])[0]
        assert asset == principal, (
            f"PAIN_TO_PRESENCE_ASSET['{pain}'] = '{asset}' pero Capa 1 declara '{principal}'"
        )


def test_service_catalog_es_biyeccion_con_el_canonico():
    """SERVICE_CATALOG era el único registro con la tripleta completa; por eso es la
    base de Capa 2. Debe quedar en biyección exacta con SERVICE_IDENTITIES."""
    from modules.commercial_documents.service_catalog import SERVICE_CATALOG

    identidades = {i.key: i for i in _canonico().SERVICE_IDENTITIES}
    assert set(SERVICE_CATALOG) == set(identidades), (
        f"SERVICE_CATALOG y SERVICE_IDENTITIES divergen: "
        f"sobran {sorted(set(SERVICE_CATALOG) - set(identidades))}, "
        f"faltan {sorted(set(identidades) - set(SERVICE_CATALOG))}"
    )
    for key, entry in SERVICE_CATALOG.items():
        i = identidades[key]
        assert (entry.service_name, entry.asset_type, entry.pain_id) == \
               (i.service_name, i.asset_type, i.pain_id), f"{key} diverge del canónico"
