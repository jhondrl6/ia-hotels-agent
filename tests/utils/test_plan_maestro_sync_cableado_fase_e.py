"""FASE-E (AC4, `N6`/`L-QW.1`): el slot `[2/13]` compara VALORES y conserva el parseo/versión.

Hasta la fase, `Plan Maestro Sync` comprobaba que `plan_maestro_data.json` parseaba. El
verificador que compara ADR/ocupacion contra el maestro existia, estaba versionado y
pasaba verde, pero nadie lo disparaba. Esta bateria prueba tres cosas por separado, porque
son tres defectos distintos:

* que el runner **consume** las divergencias de valor (un script correcto sin caller no goberna);
* que la comparacion **cae** cuando el dato se corrompe (el verde significa «valores cotejados»);
* que el verde **no es vacio** (0 regiones comparadas es rojo, no un verde mas).

Los mutantes corren sobre copias del artefacto en `tmp_path`: el arbol no se toca y la
comparacion real de `validate_benchmark_sync.py` se ejercita con el dato corrupto.
"""

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts" / "run_all_validations.py"
SYNC = ROOT / "scripts" / "validate_benchmark_sync.py"
ARTIFACTO = ROOT / "data" / "benchmarks" / "plan_maestro_data.json"
MAESTRO = ROOT / "data" / "benchmarks" / "regional_adr_2026.json"


def _cargar(nombre: str, ruta: Path):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = mod
    anterior = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = anterior
    return mod


@pytest.fixture(scope="module")
def runner_mod():
    return _cargar("rav_fase_e_sync", RUNNER)


@pytest.fixture(scope="module")
def sync_mod():
    return _cargar("vbs_fase_e", SYNC)


@pytest.fixture()
def datos():
    return {
        "arte": json.loads(ARTIFACTO.read_text(encoding="utf-8")),
        "maestro": json.loads(MAESTRO.read_text(encoding="utf-8")),
    }


def _copias_corruptas(tmp_path: Path, datos: dict, mutar) -> tuple:
    """Copia de los dos JSON con el mutante aplicado; el assert corta el mutante que no toca nada."""
    arte = json.loads(json.dumps(datos["arte"]))
    maestro = json.loads(json.dumps(datos["maestro"]))
    antes = json.dumps({"arte": arte, "maestro": maestro}, sort_keys=True)
    mutar(arte, maestro)
    despues = json.dumps({"arte": arte, "maestro": maestro}, sort_keys=True)
    assert despues != antes, "el mutante no modifico el arbol de datos: la prueba no ejercita nada"
    ruta_arte = tmp_path / "plan_maestro_data.json"
    ruta_maestro = tmp_path / "regional_adr_2026.json"
    ruta_arte.write_text(json.dumps(arte), encoding="utf-8")
    ruta_maestro.write_text(json.dumps(maestro), encoding="utf-8")
    return ruta_maestro, ruta_arte


# ---------------------------------------------------------------------------
# El check cableado: que afirma su verde
# ---------------------------------------------------------------------------
def test_check_verde_afirma_parseo_y_valores_comparados(runner_mod):
    runner = runner_mod.ValidationRunner(quick=True, verbose=False)
    runner._check_plan_maestro_sync()
    resultado = runner.results[-1]
    assert resultado.name == "Plan Maestro Sync"
    assert resultado.passed is True
    # parseo/versión (lo que ya se comprobaba) y valores (lo que se cableo)
    assert "parseado" in resultado.message
    assert "v2.5.0" in resultado.message
    assert "regiones con valores sincronizados con el maestro" in resultado.message
    assert "4" in resultado.message, "el verde debe decir cuantas regiones comparo"
    assert "loaded correctly" not in resultado.message, "el verde vacuo de parseo volvio"


def test_la_region_exenta_se_publica_en_el_mensaje(runner_mod):
    runner = runner_mod.ValidationRunner(quick=True, verbose=False)
    runner._check_plan_maestro_sync()
    mensaje = runner.results[-1].message
    assert "exenta: default" in mensaje
    assert "LEGACY" in mensaje, "la exencion debe decir por que existe"


# ---------------------------------------------------------------------------
# Mutantes sobre el verificador real (compara valores)
# ---------------------------------------------------------------------------
def test_mutante_de_adr_corrompido_cae_en_la_comparcion(sync_mod, datos, tmp_path):
    ruta_maestro, ruta_arte = _copias_corruptas(
        tmp_path, datos,
        lambda arte, maestro: arte["v25_config"]["regiones"]["caribe"].__setitem__("precio_promedio", 449000))
    divergencias = sync_mod.validate(quiet=True, master_path=ruta_maestro, secondary_path=ruta_arte)
    assert any("ADR DIVERGENCE [caribe]" in d for d in divergencias), divergencias


def test_mutante_de_ocupacion_corrompida_cae_en_la_comparcion(sync_mod, datos, tmp_path):
    ruta_maestro, ruta_arte = _copias_corruptas(
        tmp_path, datos,
        lambda arte, maestro: arte["v25_config"]["regiones"]["antioquia"].__setitem__("ocupacion", 0.60))
    divergencias = sync_mod.validate(quiet=True, master_path=ruta_maestro, secondary_path=ruta_arte)
    assert any("OCCUPANCY DIVERGENCE [antioquia]" in d for d in divergencias), divergencias


def test_region_ausente_y_region_extra_cortan(sync_mod, datos, tmp_path):
    def borrar(arte, maestro):
        arte["v25_config"]["regiones"].pop("caribe")
    ruta_maestro, ruta_arte = _copias_corruptas(tmp_path, datos, borrar)
    assert any("MISSING" in d for d in sync_mod.validate(quiet=True, master_path=ruta_maestro,
                                                          secondary_path=ruta_arte))

    def inventar(arte, maestro):
        arte["v25_config"]["regiones"]["regiones_inventada"] = {"precio_promedio": 1, "ocupacion": 0.5}
    ruta_maestro, ruta_arte = _copias_corruptas(tmp_path, datos, inventar)
    assert any("EXTRA REGIONS" in d for d in sync_mod.validate(quiet=True, master_path=ruta_maestro,
                                                               secondary_path=ruta_arte))


def test_el_arbol_actual_pasa_la_comparcion_con_cuatro_regiones(sync_mod):
    divergencias, comparadas, exenta = sync_mod.resumen_sync()
    assert divergencias == []
    assert comparadas == 4
    assert exenta.startswith("default:")


# ---------------------------------------------------------------------------
# El runner consume lo que el verificador devuelve (el cableado en si)
# ---------------------------------------------------------------------------
def test_el_runner_pasa_a_rojo_con_divergencias_reales(runner_mod, sync_mod, datos, tmp_path, monkeypatch):
    """End-to-end del cableado: divergencia producida por el verificador real → FAIL del slot."""
    ruta_maestro, ruta_arte = _copias_corruptas(
        tmp_path, datos,
        lambda arte, maestro: arte["v25_config"]["regiones"]["bogota"].__setitem__("precio_promedio", 1))
    divergencias = sync_mod.validate(quiet=True, master_path=ruta_maestro, secondary_path=ruta_arte)
    assert divergencias

    runner = runner_mod.ValidationRunner(quick=True, verbose=False)
    monkeypatch.setattr(runner, "_sincronia_valores", lambda: (divergencias, 4, "default: exenta"))
    runner._check_plan_maestro_sync()
    resultado = runner.results[-1]
    assert resultado.passed is False
    assert "divergencia" in resultado.message
    assert "4 regiones comparadas" in resultado.message
    assert any("bogota" in d for d in resultado.details), resultado.details


def test_verde_vacio_de_regiones_comparadas_no_es_verde(runner_mod, monkeypatch):
    """El verde sin comparacion es el defecto original del slot: queda cortado por su cuenta."""
    runner = runner_mod.ValidationRunner(quick=True, verbose=False)
    monkeypatch.setattr(runner, "_sincronia_valores", lambda: ([], 0, "default: exenta"))
    runner._check_plan_maestro_sync()
    resultado = runner.results[-1]
    assert resultado.passed is False
    assert "0 regiones comparadas" in resultado.message


def test_si_la_comparacion_no_se_ejecuta_el_check_no_afirma_valores(runner_mod, monkeypatch):
    """Una excepcion del verificador no puede degradarse a «parseado, todo bien»."""
    runner = runner_mod.ValidationRunner(quick=True, verbose=False)

    def fallar():
        raise RuntimeError("verificador no disponible")
    monkeypatch.setattr(runner, "_sincronia_valores", fallar)
    runner._check_plan_maestro_sync()
    resultado = runner.results[-1]
    assert resultado.passed is False
    assert "no se ejecuto" in resultado.message


# ---------------------------------------------------------------------------
# Lo que el check ya sabia comprobar no se perdio
# ---------------------------------------------------------------------------
def test_parseo_roto_sigue_cortando(runner_mod, monkeypatch, tmp_path):
    raiz = tmp_path / "arbol"
    (raiz / "data" / "benchmarks").mkdir(parents=True)
    (raiz / "archives").mkdir(parents=True)
    (raiz / "archives" / "Plan_maestro_v2_5.md").write_text("historico", encoding="utf-8")
    (raiz / "data" / "benchmarks" / "plan_maestro_data.json").write_text("{ no es json", encoding="utf-8")
    monkeypatch.setattr(runner_mod, "ROOT_DIR", raiz)
    runner = runner_mod.ValidationRunner(quick=True, verbose=False)
    runner._check_plan_maestro_sync()
    resultado = runner.results[-1]
    assert resultado.passed is False
    assert "Error reading plan_maestro_data.json" in resultado.message


def test_md_historico_ausente_sigue_cortando(runner_mod, monkeypatch, tmp_path):
    raiz = tmp_path / "arbol_sin_md"
    (raiz / "data" / "benchmarks").mkdir(parents=True)
    (raiz / "data" / "benchmarks" / "plan_maestro_data.json").write_text('{"version": "v1"}', encoding="utf-8")
    monkeypatch.setattr(runner_mod, "ROOT_DIR", raiz)
    runner = runner_mod.ValidationRunner(quick=True, verbose=False)
    runner._check_plan_maestro_sync()
    resultado = runner.results[-1]
    assert resultado.passed is False
    assert "Plan_maestro_v2_5.md not found" in resultado.message


def test_json_ausente_sigue_cortando(runner_mod, monkeypatch, tmp_path):
    raiz = tmp_path / "arbol_vacio"
    raiz.mkdir()
    monkeypatch.setattr(runner_mod, "ROOT_DIR", raiz)
    runner = runner_mod.ValidationRunner(quick=True, verbose=False)
    runner._check_plan_maestro_sync()
    resultado = runner.results[-1]
    assert resultado.passed is False
    assert "not found" in resultado.message


# ---------------------------------------------------------------------------
# Ordinal y denominador del slot (AC de Tarea 3)
# ---------------------------------------------------------------------------
def test_la_etiqueta_2_de_13_conserva_ordinal_y_denominador(runner_mod):
    runner = runner_mod.ValidationRunner(quick=True, verbose=False)
    etiquetas = runner._etiquetas_del_modo()
    orden_rapido, orden_completo = runner._orden_del_modo()
    assert (2, 13) in etiquetas, etiquetas
    assert len(etiquetas) == len(orden_rapido) == 13
    assert [k for k, _ in etiquetas] == list(range(1, len(orden_rapido) + 1))
    assert {t for _, t in etiquetas} == {13}
    assert len(orden_completo) == 18, "el modo completo sigue etiquetado con su propio conteo"


def test_el_metodo_etiquetado_sigue_siendo_el_del_slot(runner_mod):
    """La etiqueta y la invocacion del verificador viven en el mismo bloque del runner."""
    fuente = RUNNER.read_text(encoding="utf-8")
    inicio = fuente.index("    def _sincronia_valores")
    bloque = fuente[inicio:inicio + 3000]
    etiqueta = re.search("print" + r"""\(f?["']\[(\d+)/(\d+)\]""", bloque)
    assert etiqueta is not None and etiqueta.groups() == ("2", "13")
    assert "validate_benchmark_sync.py" in bloque
    assert "Plan Maestro Sync" in bloque
