"""AC12/E3 — una propuesta del proveedor falso **no** escribe §2, y su destino queda registrado.

Dos cosas separadas y las dos obligatorias:
  * el script no edita `00-lecciones-capitalizadas.md`: se prueba sobre el **arbol real**, comparando
    el sha256 del archivo **y** observando las operaciones de escritura del proceso (una comparacion
    de estado final no demuestra que nadie abrio el archivo en modo escritura — leccion S13);
  * la aceptacion o el rechazo de una propuesta se **registra con quien decidio, fecha y motivo**, y
    una decision incompleta no se aplica: un verde con proveedor falso prueba la mecanica del camino,
    no que la leccion sea pertinente (contrato E3).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
PLAN = ROOT / ".opencode" / "plans" / "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
LECCIONES = PLAN / "00-lecciones-capitalizadas.md"
NOMBRE = PLAN.name
SUPPORT_OBSERVADOR = ROOT / "tests" / "support_observador_escrituras.py"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _observador():
    spec = importlib.util.spec_from_file_location("observador_escrituras", SUPPORT_OBSERVADOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_el_script_no_tiene_camino_de_escribir_seccion_dos(trl, informe_real):
    assert trl.ESCRIBE_SECCION_DOS is False
    assert informe_real["seccion_dos"]["escrita_por_este_script"] is False
    assert informe_real["revision_humana"]["seccion_dos_editada_por_este_script"] is False
    assert "no escribe §2" in " ".join(informe_real["prohibiciones"])


def test_corrida_completa_no_toca_el_plan_real(trl, entorno_falso, tmp_path):
    """Corre el `main()` entero, con `--report` y destino explicito, contra el plan vigente."""
    antes = _sha(LECCIONES)
    ruta_informe = tmp_path / "informe.json"
    obs = _observador()
    with obs.observador_de_escrituras() as registro:
        rc = trl.main(["--plan", NOMBRE, "--report", "--out", str(ruta_informe)])
    assert rc == 0, "la corrida debe terminar en TRIADO con el falso montado por entorno"
    assert _sha(LECCIONES) == antes, "el triaje modifico §2 del plan: E3 lo prohibe"
    dentro_del_plan = registro.dentro_de(PLAN)
    assert dentro_del_plan == [], (
        f"se observaron operaciones de escritura sobre el plan triado: {dentro_del_plan} "
        f"(alcance del observador: {obs.ALCANCE})")
    informe = json.loads(ruta_informe.read_text(encoding="utf-8"))
    assert informe["buckets"]["propuesto"], "sin propuestas la prueba no tendria dientes"
    assert informe["revision_humana"]["n_pendientes"] == len(informe["buckets"]["propuesto"]), (
        "una propuesta dejo de estar pendiente: algo se aplico solo")
    assert informe["seccion_dos"]["propuestas_que_entraron_sin_revision"] == 0


def test_decision_incompleta_no_se_aplica_y_ruena_fuerte(trl, entorno_falso, tmp_path, capsys):
    """Sin `decidio` / `fecha` / `motivo` no hay aceptacion que valga: exit 6, no un verde comodo."""
    objetivo = informe_propuesta(trl, entorno_falso)
    ruta = tmp_path / "decisiones.json"
    ruta.write_text(json.dumps({"decisiones": [{"id": objetivo, "aceptada": True}]}), encoding="utf-8")
    antes = _sha(LECCIONES)
    rc = trl.main(["--plan", NOMBRE, "--decisiones", str(ruta)])
    salida = capsys.readouterr()
    assert rc == 6, f"una decision humana sin quien/fecha/motivo debe dar exit 6, dio {rc}"
    assert "REVISION-INCOMPLETA" in (salida.out + salida.err)
    assert _sha(LECCIONES) == antes


def test_aceptacion_y_rechazo_quedan_registrados_con_quien_decidio(trl, entorno_falso):
    base = correr_informe(trl, entorno_falso, None)
    dos = base["buckets"]["propuesto"][:2]
    assert len(dos) == 2, "se necesitan dos propuestas para registrar una aceptacion y un rechazo"
    decisiones = [{"id": dos[0], "aceptada": True, "decidio": "Jhon (operador)",
                   "fecha": "2026-09-24", "motivo": "revista y aplicada a mano"},
                  {"id": dos[1], "aceptada": False, "decidio": "Jhon (operador)",
                   "fecha": "2026-09-24", "motivo": "cubre el mismo riesgo que otra fila de §2"}]
    informe = correr_informe(trl, entorno_falso, decisiones)
    estados = {r["id"]: r["estado"] for r in informe["revision_humana"]["registros"]}
    assert estados[dos[0]] == "ACEPTADA-PARA-QUE-ESCRIBA-UN-HUMANO"
    assert estados[dos[1]] == "RECHAZADA-PUBLICADA"
    assert informe["revision_humana"]["incompletas"] == []
    for r in informe["revision_humana"]["registros"]:
        assert r["decidio"] and r["fecha"] and r["motivo"], "decision sin quien/fecha/motivo"
    assert informe["revision_humana"]["registros"][1]["fila_no_se_borra"] is True
    assert informe["seccion_dos"]["removed"] == []
    assert informe["seccion_dos"]["escrita_por_este_script"] is False


def test_decision_sobre_algo_que_no_estaba_propuesto_se_publica_fuera_de_lista(trl, entorno_falso):
    base = correr_informe(trl, entorno_falso, None)
    ajena = base["buckets"]["a_revisar_humano"][0]
    informe = correr_informe(trl, entorno_falso, [{"id": ajena, "aceptada": True,
                                                  "decidio": "x", "fecha": "2026-09-24",
                                                  "motivo": "y"}])
    r = informe["revision_humana"]["registros"][0]
    assert r["estado"] == "FUERA-DE-LISTA", (
        "una decision sobre un ID que no estaba propuesto no puede colarse como aceptacion")


# ------------------------------------------------------------------ helpers del propio archivo

def correr_informe(trl, entorno_falso, decisiones):
    indice, estado = trl.leer_suelo()
    ancladas = trl.filas_ancladas(LECCIONES)
    pendientes = trl.candidatos_de_pertinencia(indice, NOMBRE, ancladas)
    return trl.construir_informe(NOMBRE, pendientes, ancladas, indice, estado,
                                 entorno=dict(os.environ), decisiones=decisiones)


def informe_propuesta(trl, entorno_falso):
    return correr_informe(trl, entorno_falso, None)["buckets"]["propuesto"][0]
