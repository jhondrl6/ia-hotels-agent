"""Diente de la mudanza (a) de la fila 18: schema 1.3 saca el conteo bruto del artefacto y lo deja en la salida.

Las dos mitades se afirman en UNA sola corrida, sobre el mismo arbol sintetico y el mismo scratch
puesto bajo `temp/`:

  (1) la SALIDA impresa nombra el conteo del rol y se mueve con el scratch, y
  (2) el ARTEFACTO publicado no lo lleva, ni en el objeto en memoria ni tras `publicar()`.

Un verde que mire solo un lado es verde vacio: mirando solo la salida se colaria un retiro a medias
del JSON, y mirando solo el JSON se colaria la perdida del dato (que la (d1) prohibe expresamente:
«sigue publicandose en la salida»). Anadido el 2026-10-03 por OLA 2 del piloto JEV, ejecucion de la
fila 18 del `33-registro-unificado-de-pendientes-2026-09-29.md`.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_wiring.py"

_spec = importlib.util.spec_from_file_location("validate_wiring_mudanza", SCRIPT)
vw = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(vw)

PRODUCTORES = '''
class PainSolutionMapper:
    def detect_pains(self, audit_result, validation_summary, analytics_data=None,
                     whatsapp_html_detected=False):
        return []


class CoherenceValidator:
    def validate(self, assessment, documents, evidence_coverage=0.0,
                 hard_contradictions=0):
        return {"ok": True}


class FinancialCalculatorV2:
    def calculate(self, adr, occupancy, scenario="realista", disclaimers=None):
        return {}


class DeliveryQualityReport:
    def build(self, package, pain_ledger, coverage=1.0, justification=""):
        return {}
'''

LLAMADA_CON_SENAL = '''
def usar(mapper, validator):
    mapper.detect_pains(audit_result=1, validation_summary=2,
                        analytics_data=3, whatsapp_html_detected=4)
    validator.validate(assessment=1, documents=2, evidence_coverage=0.9,
                       hard_contradictions=0)
'''


def _arbol_con_scratch(base: Path) -> Path:
    """Arbol minimo con un scratch en `temp/`, directorio que la tabla de roles excluye.

    El `.gitignore` declara `temp/` y hay un `git init` detras: asi `no_versionada` sale True y el
    scratch mueve el conteo BRUTO sin tocar el versionado, que es la distincion que la mudanza
    convierte en forma del artefacto.
    """
    (base / "modules").mkdir(parents=True, exist_ok=True)
    (base / "temp").mkdir(parents=True, exist_ok=True)
    (base / "modules" / "productores.py").write_text(PRODUCTORES, encoding="utf-8")
    (base / "modules" / "conforme.py").write_text(LLAMADA_CON_SENAL, encoding="utf-8")
    (base / "temp" / "scratch_1.py").write_text("x = 1\n", encoding="utf-8")
    (base / ".gitignore").write_text("temp/\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", "."], cwd=str(base), capture_output=True,
                   text=True, timeout=60)
    return base


def test_la_mudanza_subde_el_schema_y_saca_las_dos_claves(tmp_path):
    raiz = _arbol_con_scratch(tmp_path / "a")
    reporte = vw.construir_reporte(raiz)
    assert reporte["schema_version"] == "1.3" == vw.SCHEMA_VERSION
    agrupado = reporte["exclusiones_por_rol"]
    assert "temp" in agrupado, "el rol desaparecio: la mudanza se leyo como un retiro"
    assert sorted(agrupado["temp"]) == ["cantidad_versionada", "motivo"], agrupado["temp"]
    texto = json.dumps(agrupado, ensure_ascii=False)
    assert '"cantidad"' not in texto and '"ejemplo"' not in texto, texto
    # `cobertura` es otra familia: la fila 18 lo declara expresamente fuera de alcance.
    assert "archivos_excluidos_por_rol" in reporte["cobertura"]


def test_scratch_nuevo_muve_la_salida_y_no_el_artefacto_en_la_misma_corrida(tmp_path):
    raiz = _arbol_con_scratch(tmp_path / "b")
    brutos_antes = vw.exclusiones_brutas_por_rol(raiz)
    reporte_antes = vw.construir_reporte(raiz)
    assert brutos_antes["temp"] == 1
    assert reporte_antes["exclusiones_por_rol"]["temp"]["cantidad_versionada"] == 0, (
        "premissa del control: Git declara temp/ ignorado, o sea el bruto no es versionado")

    (raiz / "temp" / "scratch_2.py").write_text("y = 2\n", encoding="utf-8")
    brutos = vw.exclusiones_brutas_por_rol(raiz)
    reporte = vw.construir_reporte(raiz)
    linea = vw.resumen_de(reporte, brutos)

    assert brutos["temp"] == 2, "el scratch no se conto: la mitad (1) no tiene nada que afirmar"
    assert f"temp bruto=2 versionada=0" in linea, linea
    assert reporte["exclusiones_por_rol"]["temp"]["cantidad_versionada"] == 0, (
        "el numero gobernado se movio con un scratch: la cura de la (d1) no se aplico")
    assert '"cantidad"' not in json.dumps(reporte["exclusiones_por_rol"], ensure_ascii=False), (
        "la clave bruta volvio al artefacto (ojo: `cantidad_versionada` si es gobernable)")


def test_lo_que_se_escribe_con_publicar_tampoco_lleva_el_conteo(tmp_path):
    """El criterio se comprueba sobre el bytes del destino, no sobre el dict en memoria."""
    raiz = _arbol_con_scratch(tmp_path / "c")
    reporte = vw.construir_reporte(raiz)
    destino = tmp_path / "fuera" / "wiring_report.json"
    vw.publicar(reporte, destino)
    publicado = json.loads(destino.read_text(encoding="utf-8"))
    bloque = json.dumps(publicado["exclusiones_por_rol"], ensure_ascii=False)
    assert '"cantidad"' not in bloque and '"ejemplo"' not in bloque, bloque
    assert publicado["schema_version"] == "1.3"


def test_sin_el_diccionario_bruto_la_salida_lo_declara(tmp_path):
    """Mitad negativa del diente: `resumen_de` sin `brutos` no puede omitir el desglose a silencio.

    Si se fuera la llamada que lo alimenta, la linea perderia la parte `bruto=` sin avisar, y eso es
    un rojo por vacio de la familia L-R.3.
    """
    raiz = _arbol_con_scratch(tmp_path / "d")
    reporte = vw.construir_reporte(raiz)
    con = vw.resumen_de(reporte, vw.exclusiones_brutas_por_rol(raiz))
    sin = vw.resumen_de(reporte)
    assert "temp bruto=" in con
    assert "bruto=no-publicado" in sin, sin
    assert "exclusiones_por_rol" in con and "exclusiones_por_rol" in sin


def test_la_sentinela_de_procedencia_sigue_viva_para_el_artefacto_previo():
    """El commit de transicion: las rutas de procedencia se conservan aunque hoy sean no-op.

    Se afirma por la funcion, no por lectura: si alguien las retira antes de que el publicado este
    en 1.3, el `--check` contra el derivado del commit previo pone rojo de cableado donde no lo hay.
    """
    rutas = vw._rutas_de_procedencia({"exclusiones_por_rol": {"temp": {"cantidad": 90}}})
    assert "exclusiones_por_rol.temp.cantidad" in rutas
    assert "exclusiones_por_rol.temp.ejemplo" in rutas
    neutralizado = vw._neutralizar_procedencia(
        {"exclusiones_por_rol": {"temp": {"cantidad": 90, "cantidad_versionada": 0,
                                          "motivo": "x", "ejemplo": "temp/a.py"}}}, rutas)
    assert neutralizado["exclusiones_por_rol"]["temp"]["cantidad"] == vw.SENTINELA_PROCEDENCIA
    assert neutralizado["exclusiones_por_rol"]["temp"]["cantidad_versionada"] == 0, (
        "la sentinela se comio tambien lo gobernado")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
