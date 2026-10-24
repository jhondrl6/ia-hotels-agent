"""FASE-E (AC4, `N5`/`D20`): paridad de la matriz regional — cinco tablas derivadas o retiradas.

La deuda no era dos copias sino cinco tablas (`N5`): el maestro `regional_adr_2026.json`,
`v25_config.regiones`, `Benchmarking.md`, `revpar_targets` de `gap_analyzer` y el dict de
respaldo de `ScraperFallback`. Esta bateria deja tres de ellas **retiradas** (su valor se
deriva del lector unico), comprueba la paridad maestro↔secundario↔derivado y **fija** la
divergencia medida de `Benchmarking.md`, que es de FASE-H2: si la doc se alinea o cambia
sin re-declarar, este archivo cae y obliga a nombrar el hecho.
"""

import ast
import inspect
import json
import re
from pathlib import Path

import pytest

from modules.analyzers.gap_analyzer import GapAnalyzer
from modules.generators.report_builder import ReportBuilder
from modules.scrapers.scraper_fallback import ScraperFallback
from modules.utils.benchmarks import BLOQUES_MAESTRO_DECLARADO, BenchmarkLoader

ROOT = Path(__file__).resolve().parents[2]
BENCHMARKING_MD = ROOT / "data" / "benchmarks" / "Benchmarking.md"
MAESTRO = ROOT / "data" / "benchmarks" / "regional_adr_2026.json"
ARTIFACTO = ROOT / "data" / "benchmarks" / "plan_maestro_data.json"

ETIQUETA_A_REGION = {"Eje Cafetero": "eje_cafetero", "Caribe": "caribe", "Antioquia": "antioquia"}

# Divergencia MEDIDA de Benchmarking.md contra el maestro (columnas ADR/RevPAR 2026).
# FASE-H2 es la duena de ese documento (dependencias-fases.md): aqui vive el pin para
# que la divergencia no se vuelva memoria, sino una afirmacion que alguien tiene que
# re-declarar si mueve el numero.
DIVERGENCIA_BENCHMARKING = {
    "eje_cafetero": {"adr_md": 385_000, "revpar_md": 197_100},
    "caribe": {"adr_md": 880_000, "revpar_md": 602_800},
    "antioquia": {"adr_md": 560_000, "revpar_md": 359_500},
}


@pytest.fixture(scope="module")
def maestro() -> dict:
    return json.loads(MAESTRO.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def arte() -> dict:
    return json.loads(ARTIFACTO.read_text(encoding="utf-8"))


def _filas_benchmarking() -> dict:
    """Regiones de la tabla `ADR (2026) / Ocupacion (2026) / RevPAR (2026)` del doc."""
    fuente = BENCHMARKING_MD.read_text(encoding="utf-8")
    filas = {}
    for linea in fuente.splitlines():
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if len(celdas) < 7 or celdas[0] not in ETIQUETA_A_REGION:
            continue
        region = ETIQUETA_A_REGION[celdas[0]]
        adr = float(re.sub(r"[^\d.]", "", celdas[2])) * 1000
        ocupacion = float(re.sub(r"[^\d.]", "", celdas[3])) / 100
        revpar = float(re.sub(r"[^\d.]", "", celdas[5])) * 1000
        filas[region] = {"adr_md": int(adr), "ocupacion_md": ocupacion, "revpar_md": int(revpar)}
    assert len(filas) == 3, f"la tabla de Benchmarking.md no se leyo completa: {sorted(filas)}"
    return filas


# ---------------------------------------------------------------------------
# Tabla 1 y 2: maestro y v25_config, contra el derivado del lector unico
# ---------------------------------------------------------------------------
def test_maestro_secundario_y_derivado_casan_region_a_region(maestro, arte):
    """Las tres varillas vivas de la matriz: maestro publicado, JSON y `revpar_cop` derivado."""
    loader = BenchmarkLoader()
    publicadas = arte["v25_config"]["regiones"]
    for region, datos in maestro["regions"].items():
        if region == "default":
            continue
        boutique = datos["boutique_10_25"]
        assert publicadas[region]["precio_promedio"] == boutique["adr_cop"], region
        assert publicadas[region]["ocupacion"] == pytest.approx(boutique["occupancy_rate"]), region
        assert loader.get_regional_data(region)["revpar_cop"] == int(
            round(boutique["adr_cop"] * boutique["occupancy_rate"])), region


# ---------------------------------------------------------------------------
# Tabla 5 retirada: ScraperFallback ya no trae valores propios
# ---------------------------------------------------------------------------
def test_scraper_fallback_entrega_la_misma_tabla_que_el_loader():
    """Identidad estructural: dos lectores del mismo numero eran la deuda; ahora es uno."""
    via_fallback = ScraperFallback().benchmarks["regiones"]
    via_loader = BenchmarkLoader().regiones()
    assert via_fallback == via_loader
    assert sorted(via_fallback) == sorted(via_loader) == [
        "antioquia", "bogota", "caribe", "default", "eje_cafetero"]


def test_scraper_fallback_perdio_su_dict_de_respaldo():
    """Los literales del respaldo (330.000 / 410.000 / 0.52 / 0.66) ya no existen en el modulo."""
    fuente = inspect.getsource(ScraperFallback)
    for literal in ("330000", "410000", '"ocupacion": 0.52', '"ocupacion": 0.66', '"precio_promedio"'):
        assert literal not in fuente, f"{literal} sigue vivo en ScraperFallback"
    assert "BenchmarkLoader" in inspect.getsource(ScraperFallback._load_benchmarks)


def test_scraper_fallback_no_abre_el_archivo_por_su_cuenta():
    """Un lector que ademas abre el archivo por su cuenta es el segundo lector disfrazado."""
    fuente = inspect.getsource(ScraperFallback)
    assert "plan_maestro_data.json" not in fuente
    assert "self.benchmarks_path" not in fuente


# ---------------------------------------------------------------------------
# Tabla 4 retirada: gap_analyzer ya no conserva revpar_targets
# ---------------------------------------------------------------------------
def test_gap_analyzer_perdio_la_tabla_de_revpar():
    """AST, no grep de la palabra: el nombre sobrevive solo en el comentario que documenta el retiro."""
    fuente = Path(inspect.getfile(GapAnalyzer)).read_text(encoding="utf-8")
    asignadas = {
        objetivo.id
        for nodo in ast.walk(ast.parse(fuente))
        if isinstance(nodo, (ast.Assign, ast.AnnAssign))
        for objetivo in ([nodo.target] if isinstance(nodo, ast.AnnAssign) else nodo.targets)
        if isinstance(objetivo, ast.Name)
    }
    assert "revpar_targets" not in asignadas
    for literal in ("171600", "270600", "168000"):
        assert literal not in fuente, f"{literal} sigue siendo un objetivo independiente"
    assert "revpar_objetivo = config.revpar_cop" in fuente


def test_el_objetivo_retirado_coincida_con_lo_que_era_el_respaldo():
    """Medicion que sustenta DA-PLAN-8b: los tres literales eran precio x ocupacion del respaldo.

    Si alguien re-valora el respaldo sin tocar la historia, esta prueba lo cuenta: deja
    de casar la identidad que motivo retirar la tabla en lugar de recalibrarla.
    """
    respaldo = {"eje_cafetero": (330000, 0.52), "caribe": (410000, 0.66), "antioquia": (280000, 0.60)}
    objetivo_retirado = {"eje_cafetero": 171600, "caribe": 270600, "antioquia": 168000}
    for region, (precio, ocupacion) in respaldo.items():
        assert int(round(precio * ocupacion)) == objetivo_retirado[region], region


def test_gap_analyzer_objetivo_sale_del_lector_unico():
    """El consumidor del revpar regional cobra el valor por region, no el fossil global."""
    loader = BenchmarkLoader()
    for region in ("caribe", "eje_cafetero", "antioquia", "bogota", "default"):
        config_via_productor = BenchmarkLoader().get_regional_data(region)["revpar_cop"]
        assert config_via_productor == loader.get_regional_data(region)["revpar_cop"]
    assert loader.get_regional_data("caribe")["revpar_cop"] != loader.get_regional_data("default")["revpar_cop"]


# ---------------------------------------------------------------------------
# report_builder: un solo lector instanciado para los datos regionales
# ---------------------------------------------------------------------------
def test_report_builder_no_lee_regiones_por_scraper_fallback():
    fuente = inspect.getsource(ReportBuilder.__init__)
    assert "self._region_profiles = self._benchmark_loader.regiones()" in fuente
    assert "_fallback_helper.benchmarks" not in fuente
    # ScraperFallback sigue instanciado, pero por _detect_region (texto), no por benchmarks
    assert "ScraperFallback()" in fuente
    assert "self.benchmarks" not in inspect.getsource(ReportBuilder)


# ---------------------------------------------------------------------------
# Tabla 3: Benchmarking.md, declarada con su divergencia medida (dueno FASE-H2)
# ---------------------------------------------------------------------------
def test_benchmarking_md_conserva_la_ocupacion_del_maestro():
    """La ocupacion del doc si casa: la divergencia es de ADR, no de toda la fila."""
    filas = _filas_benchmarking()
    maestro = json.loads(MAESTRO.read_text(encoding="utf-8"))["regions"]
    for region, datos in filas.items():
        assert datos["ocupacion_md"] == pytest.approx(
            maestro[region]["boutique_10_25"]["occupancy_rate"]), region


def test_benchmarking_md_divergencia_fijada_con_su_dueno():
    """Fija los valores del doc: moverlos sin re-declarar la divergencia es rojo en FASE-H2."""
    filas = _filas_benchmarking()
    loader = BenchmarkLoader()
    for region, pin in DIVERGENCIA_BENCHMARKING.items():
        assert filas[region]["adr_md"] == pin["adr_md"], region
        assert filas[region]["revpar_md"] == pin["revpar_md"], region
        # y sigue siendo divergencia real contra el lector unico, no paridad declarada
        assert filas[region]["adr_md"] != loader.get_regional_data(region)["precio_promedio"], region


def test_benchmarking_no_esta_en_la_particion_de_maestros():
    """El doc no es un maestro declarado: no hay getter que prometa leerlo."""
    assert "Benchmarking.md" not in BLOQUES_MAESTRO_DECLARADO
