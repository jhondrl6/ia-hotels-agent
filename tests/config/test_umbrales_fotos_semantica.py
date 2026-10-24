"""AC6 / `D25` — el vocabulario de umbrales de fotos GBP (FASE-F).

Criterio que gobierna: **un sitio por umbral nombrado, no un valor único para los cinco**.
La población declarada es la lista `POBLACION` de este archivo (los siete módulos vivos del
producto que comparan contra un conteo de fotos). `modules/scrapers/gbp_leak_detector.py` queda
FUERA por decisión: es la copia retirada del servicio que FASE-D conservó como oráculo del
relevo, y sus literales están congelados a propósito.

Los dientes son por AST sobre símbolos, no por grep global de literales (restricción §4.10(c)
del plan: los umbrales y valores se pueblan por símbolo con nombre).
"""

import ast
import re
from pathlib import Path

import pytest

import modules.common.umbrales_fotos as umbrales
from modules.common.umbrales_fotos import (
    CLAVE_BLOQUE,
    FOTOS_BRECHA_DIAGNOSTICO,
    FOTOS_OPORTUNIDAD,
    FOTOS_RUBRICA_EXCELENTE,
    FOTOS_TARGET_DIAGNOSTICO,
    MIN_FOTOS_BRECHA,
    NOMBRE_CONFIG,
    ORDEN_ESCALERA,
    UmbralesFotosError,
)
from modules.common.yaml_loader import load_yaml_config

RAIZ = Path(__file__).resolve().parents[2]

VOCABULARIO = {
    "MIN_FOTOS_BRECHA": MIN_FOTOS_BRECHA,
    "FOTOS_OPORTUNIDAD": FOTOS_OPORTUNIDAD,
    "FOTOS_RUBRICA_EXCELENTE": FOTOS_RUBRICA_EXCELENTE,
    "FOTOS_BRECHA_DIAGNOSTICO": FOTOS_BRECHA_DIAGNOSTICO,
    "FOTOS_TARGET_DIAGNOSTICO": FOTOS_TARGET_DIAGNOSTICO,
}

# Semántica esperada en cada módulo vivo: qué nombres lee y cuántos sitios de comparación
# aporta. La cuenta total (14) es la re-medición de FASE-F: el contexto de deudas publicó 11
# sitios y no contaba el segundo método de score de GBPAuditor ni la banda parcial >= MIN.
POBLACION = {
    "modules/utils/dynamic_impact.py": ({"MIN_FOTOS_BRECHA"}, 1),
    "modules/financial_engine/opportunity_scorer.py": ({"FOTOS_OPORTUNIDAD"}, 1),
    "modules/scrapers/gbp_auditor.py": (
        {"FOTOS_RUBRICA_EXCELENTE", "MIN_FOTOS_BRECHA"},
        5,
    ),
    "modules/generators/report_builder.py": ({"FOTOS_RUBRICA_EXCELENTE"}, 3),
    "modules/auditors/v4_comprehensive.py": (
        {"FOTOS_BRECHA_DIAGNOSTICO", "FOTOS_TARGET_DIAGNOSTICO"},
        1,
    ),
    "modules/commercial_documents/data_structures.py": ({"FOTOS_BRECHA_DIAGNOSTICO"}, 1),
    "modules/commercial_documents/v4_diagnostic_generator.py": (
        {"FOTOS_TARGET_DIAGNOSTICO", "FOTOS_BRECHA_DIAGNOSTICO"},
        2,
    ),
}

PATRON_FOTOS = re.compile(r"fotos|photos|photo_count", re.IGNORECASE)
OPERADORES = (ast.Lt, ast.LtE, ast.Gt, ast.GtE)
VALORES_UMBRAL = set(VOCABULARIO.values())


def _es_umbral(texto_lado: str) -> bool:
    """El otro lado de la comparación es un umbral: nombre del vocabulario o su valor."""
    limpio = texto_lado.strip()
    return limpio in VOCABULARIO or bool(re.fullmatch(r"\d+", limpio) and int(limpio) in VALORES_UMBRAL)


def _sitios_fotos(rel_ruta: str):
    """Sitios de comparación de un conteo de fotos contra un umbral.

    No es «cualquier comparación que mencione fotos»: `api_photos > current_photos` (dos
    variables), `fotos_meta > 0` (guard de división) o `photos >= 3` (piso de existencia) no
    son umbrales del vocabulario y quedan fuera del conteo.
    """
    arbol = ast.parse((RAIZ / rel_ruta).read_text(encoding="utf-8"))
    sitios = []
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Compare):
            continue
        operandos = [nodo.left, *nodo.comparators]
        for indice, operador in enumerate(nodo.ops):
            if not isinstance(operador, OPERADORES):
                continue
            izquierdo = ast.unparse(operandos[indice])
            derecho = ast.unparse(operandos[indice + 1])
            if not PATRON_FOTOS.search(f"{izquierdo} {derecho}"):
                continue
            if not (_es_umbral(izquierdo) or _es_umbral(derecho)):
                continue
            sitios.append((type(operador).__name__, izquierdo, derecho))
    return sitios


def _defaults_inline(rel_ruta: str):
    """`.get(<clave de fotos>, <valor de umbral>)`: el segundo sitio de definición que cura D25."""
    arbol = ast.parse((RAIZ / rel_ruta).read_text(encoding="utf-8"))
    inline = []
    for nodo in ast.walk(arbol):
        if (
            isinstance(nodo, ast.Call)
            and isinstance(nodo.func, ast.Attribute)
            and nodo.func.attr == "get"
            and len(nodo.args) == 2
        ):
            clave = ast.unparse(nodo.args[0])
            default = ast.unparse(nodo.args[1]).strip()
            if PATRON_FOTOS.search(clave) and re.fullmatch(r"\d+", default) and int(default) in VALORES_UMBRAL:
                inline.append(f"{rel_ruta}: {ast.unparse(nodo)}")
    return inline


def _nombres_lectos(rel_ruta: str):
    """Nombres del vocabulario que el módulo importa de modules.common.umbrales_fotos."""
    arbol = ast.parse((RAIZ / rel_ruta).read_text(encoding="utf-8"))
    leidos = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.ImportFrom) and (nodo.module or "").endswith("umbrales_fotos"):
            leidos.update(alias.name for alias in nodo.names)
    return leidos


def test_config_es_el_sito_unico_de_definicion():
    """El lector expone exactamente lo que publica el YAML: no hay un segundo valor en Python."""
    bloque = load_yaml_config(NOMBRE_CONFIG, config_dir=umbrales.CONFIG_DIR)[CLAVE_BLOQUE]
    assert set(bloque) == set(VOCABULARIO), "el vocabulario del YAML y el del lector divergen"
    assert {k: int(v) for k, v in bloque.items()} == VOCABULARIO


def test_el_lector_no_quema_los_cinco_valores():
    """modules/common/umbrales_fotos.py no define ningún umbral con un literal numérico."""
    arbol = ast.parse((RAIZ / "modules/common/umbrales_fotos.py").read_text(encoding="utf-8"))
    literales = {
        nodo.value
        for nodo in ast.walk(arbol)
        if isinstance(nodo, ast.Constant) and isinstance(nodo.value, int)
    }
    quemados = literales & set(VOCABULARIO.values())
    assert not quemados, f"el lector vuelve a ser un segundo sitio de definición: {sorted(quemados)}"


def test_la_escalera_de_umbrales_esta_ordenada():
    """MIN ≤ OPORTUNIDAD ≤ RÚBRICA ≤ BRECHA ≤ TARGET: la relación manda, no un valor único."""
    valores = [VOCABULARIO[nombre] for nombre in ORDEN_ESCALERA]
    assert valores == sorted(valores), f"la escalera está invertida: {dict(zip(ORDEN_ESCALERA, valores))}"
    assert len(set(valores)) == 5, (
        "los cinco umbrales colapsaron a menos de cinco valores: AC6 cura la semántica, "
        "no fuerza un número único"
    )


@pytest.mark.parametrize("rel_ruta", sorted(POBLACION))
def test_cada_sito_lee_su_umbral_nombrado(rel_ruta: str):
    """Cero literales de comparación de fotos y solo nombres del vocabulario por módulo."""
    esperados, cuenta_esperada = POBLACION[rel_ruta]
    sitios = _sitios_fotos(rel_ruta)
    literales = [
        (operador, izquierdo, derecho)
        for operador, izquierdo, derecho in sitios
        if re.fullmatch(r"\d+", derecho.strip()) or re.fullmatch(r"\d+", izquierdo.strip())
    ]
    assert not literales, f"{rel_ruta} sigue comparando contra un número suelto: {literales}"
    assert len(sitios) == cuenta_esperada, (
        f"{rel_ruta} tenía {cuenta_esperada} sitios de comparación y hoy tiene {len(sitios)}: "
        "re-mide y re-declara la población"
    )
    leidos = _nombres_lectos(rel_ruta)
    assert esperados <= leidos, f"{rel_ruta} no lee los nombres que le corresponden: faltan {esperados - leidos}"
    assert leidos <= set(VOCABULARIO), f"{rel_ruta} importa nombres fuera del vocabulario: {leidos - set(VOCABULARIO)}"


def test_ningun_umbral_de_fotos_es_un_default_inline():
    """Un `.get('fotos_meta', 15)` es un segundo sitio de definición: solo queda el nombre."""
    inline = [sitio for rel_ruta in POBLACION for sitio in _defaults_inline(rel_ruta)]
    assert not inline, f"defaults de umbral fuera del vocabulario: {inline}"


def test_la_cuenta_total_de_sitios_es_la_re_medida_de_fase_f():
    """14 sitios vivos en 7 módulos (el contexto de deudas publicó 11; la re-medición cuenta +3)."""
    total = sum(len(_sitios_fotos(rel_ruta)) for rel_ruta in POBLACION)
    assert total == 14, f"sitios de comparación medidos: {total} (la población declara 14)"


def test_el_target_ya_no_se_justifica_por_un_constante_local():
    """`TARGET_GBP_PHOTOS = 40` deja de existir: el objetivo se lee del vocabulario."""
    texto = (RAIZ / "modules/commercial_documents/v4_diagnostic_generator.py").read_text(
        encoding="utf-8"
    )
    assert "TARGET_GBP_PHOTOS" not in texto, "la constante local sigue siendo un segundo sitio"


def test_bloque_incompleto_o_invertido_falla_fuerte(monkeypatch):
    """El lector no deriva en silencio: sin bloque o con la escalera invertida, levanta el guard."""
    ruta_yaml = dict(umbrales._leer_umbrales())  # forma publicada, para no inventarla aquí
    incompleto = {k: v for k, v in ruta_yaml.items() if k != "FOTOS_OPORTUNIDAD"}
    monkeypatch.setattr(umbrales, "load_yaml_config", lambda *a, **k: {CLAVE_BLOQUE: incompleto})
    with pytest.raises(UmbralesFotosError, match="Faltan umbrales"):
        umbrales._leer_umbrales()

    invertido = dict(ruta_yaml)
    invertido["FOTOS_RUBRICA_EXCELENTE"] = 999
    monkeypatch.setattr(umbrales, "load_yaml_config", lambda *a, **k: {CLAVE_BLOQUE: invertido})
    with pytest.raises(UmbralesFotosError, match="escalera"):
        umbrales._leer_umbrales()

    monkeypatch.setattr(umbrales, "load_yaml_config", lambda *a, **k: {})
    with pytest.raises(UmbralesFotosError, match="Falta el bloque"):
        umbrales._leer_umbrales()
