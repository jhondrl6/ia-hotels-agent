"""AC14 (R2.8) — mutation check sobre **el simbolo real** que impide el filtrado, con rojo y verde.

El guard es `triage_lesson_relevance.GUARD_ADITIVIDAD_ACTIVO`, leido por `guardar_filas_ancladas()` en
el momento del filtrado: apagarlo **no** cambia ninguna otra ruta del programa, pero deja pasar la fila
que el emisor juzgo `no-pertinente`, y entonces `removed` deja de estar vacio — que es exactamente lo
que el test de AC10 afirma. Sin ese rojo, el verde de AC10 no diria que el guard existe (L-T4A.5).

Disciplina S13 (orden de calidad §4.C, heredada del arnes de FASE-A): el destino de la evidencia es
**argumento obligatorio** — no hay constante del archivo apuntando al directorio de otra fase — y la
prueba de que no se piso pasado se hace **observando las operaciones de escritura** del proceso con el
observador compartido, **mas** contenido y metadatos (`huellas`) del expediente protegido. Un `utime`
restaurado deja el estado final identico y solo el observador lo ve.
"""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
import os
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
PLAN = ROOT / ".opencode" / "plans" / "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
LECCIONES = PLAN / "00-lecciones-capitalizadas.md"
NOMBRE = PLAN.name
SUPPORT_OBSERVADOR = ROOT / "tests" / "support_observador_escrituras.py"
# Solo lectura: se observa para probar que NADIE escribe aqui (S13). No es destino de escritura.
EVIDENCIA_SOLO_LECTURA = ROOT / "evidence" / "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20" / "FASE-A"
SIMBOLO_MUTADO = "GUARD_ADITIVIDAD_ACTIVO"
SALIDAS_ESPERADAS = ("verde_baseline.json", "mutante_M-AC10-guard-aditividad.json", "resumen.txt")


def _observador():
    spec = importlib.util.spec_from_file_location("observador_escrituras", SUPPORT_OBSERVADOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _insumos(trl):
    indice, estado = trl.leer_suelo()
    ancladas = trl.filas_ancladas(LECCIONES)
    return indice, estado, ancladas, trl.candidatos_de_pertinencia(indice, NOMBRE, ancladas)


def medir(trl, mut: bool) -> dict:
    """Corre el triaje real sobre el arbol vigente con el guard activo o apagado."""
    indice, estado, ancladas, pendientes = _insumos(trl)
    if mut:
        setattr(trl, SIMBOLO_MUTADO, False)
    try:
        informe = trl.construir_informe(NOMBRE, pendientes, ancladas, indice, estado,
                                       entorno=dict(os.environ))
    finally:
        setattr(trl, SIMBOLO_MUTADO, True)
    s = informe["seccion_dos"]
    return {"mut": mut, "simbolo": f"triage_lesson_relevance.{SIMBOLO_MUTADO}",
            "guard_activo": bool(getattr(trl, SIMBOLO_MUTADO)),
            "anchored_before": s["anchored_before"], "anchored_after": s["anchored_after"],
            "removed": s["removed"], "intentos_filtrados": s["intentos_filtrados"],
            "cuestionadas": s["filas_cuestionadas_sin_borrar"],
            "emisor_falso": informe["coste"]["emisor"]["falso"]}


def correr_a_destino(destino: Path, trl=None) -> dict:
    """Unicas salidas: las que el llamador nombra. Sin destino por defecto (S13)."""
    if trl is None:
        spec = importlib.util.spec_from_file_location(
            "trl_para_evidencia", ROOT / "scripts" / "triage_lesson_relevance.py")
        trl = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(trl)
    verde = medir(trl, mut=False)
    rojo = medir(trl, mut=True)
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "verde_baseline.json").write_text(
        json.dumps(verde, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (destino / "mutante_M-AC10-guard-aditividad.json").write_text(
        json.dumps(rojo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    obs = _observador()
    (destino / "resumen.txt").write_text(
        "\n".join([
            "AC14 — mutation check del guard de no-filtrado (FASE-C)",
            f"simbolo mutado: triage_lesson_relevance.{SIMBOLO_MUTADO} (leido por guardar_filas_ancladas)",
            f"alcance del observador de escrituras: {obs.ALCANCE}",
            f"destino declarado por el cierre: {destino.as_posix()}",
            f"VERDE  (guard activo): anchored {verde['anchored_before']}->{verde['anchored_after']} "
            f"removed={verde['removed']} intentos={verde['intentos_filtrados']}",
            f"ROJO   (guard apagado): anchored {rojo['anchored_before']}->{rojo['anchored_after']} "
            f"removed={rojo['removed']} intentos={rojo['intentos_filtrados']}",
            "lectura: con el guard apagado una fila anclada desaparece de §2; el test de AC10",
            "  (test_triage_no_elimina_fila_anclada) se pone rojo con el mismo insumo. Eso es lo que",
            "  prueba que el verde no es un verde por ausencia de oportunidad de borrar.",
            f"emisor de los juicios: proveedor FALSO (falso={verde['emisor_falso']})",
            "",
        ]) + "\n", encoding="utf-8")
    return {"verde": verde, "rojo": rojo, "destino": destino.as_posix()}


def test_verde_con_el_guard_activo(trl, entorno_falso):
    v = medir(trl, mut=False)
    assert v["removed"] == []
    assert v["anchored_after"] == v["anchored_before"] > 0
    assert v["cuestionadas"], "el guard no tuvo trabajo: no hay nada que mutar (L-HF1)"


def test_rojo_con_el_guard_apagado(trl, entorno_falso):
    r = medir(trl, mut=True)
    assert r["removed"], (
        f"apagado {SIMBOLO_MUTADO} sigue sin filtrar: el mutante no toca el guard real (L-T4A.5)")
    assert sorted(r["removed"]) == sorted(r["cuestionadas"]), (
        "lo que desaparece no es lo que el emisor cuestiono: el rojo no nombra al guard mutado (L-V2.1)")
    assert r["anchored_after"] < r["anchored_before"]


def test_el_rojo_es_el_que_quiebra_la_afirmacion_de_ac10(trl, entorno_falso):
    """La prueba de que el mutante apunta al guard de AC10: la misma asercion del test de AC10."""
    r = medir(trl, mut=True)
    with pytest.raises(AssertionError):
        assert r["removed"] == [], "AC10 violado por el mutante"


def test_apagar_el_guard_no_altera_nada_mas(trl, entorno_falso):
    """Un mutante que apaga el guard no debe cambiar el denominador ni la poblacion miradas."""
    v, r = medir(trl, mut=False), medir(trl, mut=True)
    assert v["anchored_before"] == r["anchored_before"]
    assert v["emisor_falso"] == r["emisor_falso"] is True
    assert set(v["intentos_filtrados"]) == set(r["removed"])


def test_las_dos_salidas_van_a_destino_explicito_y_no_al_expediente_ajeno(tmp_path, entorno_falso):
    obs = _observador()
    protegido_antes = obs.huellas(EVIDENCIA_SOLO_LECTURA)
    assert protegido_antes, f"no hay expediente que proteger en {EVIDENCIA_SOLO_LECTURA}"
    destino = tmp_path / "mutation"
    with obs.observador_de_escrituras() as registro:
        correr_a_destino(destino)
    vistas = registro.dentro_de(destino)
    nombres_vistos = {Path(r).name for _, r, _ in vistas}
    assert set(SALIDAS_ESPERADAS) <= nombres_vistos, (
        f"el observador no vio las escrituras reales del arnes ({nombres_vistos}); sin esa ancla "
        "positiva, una ausencia en evidence/ no probaria nada")
    assert registro.dentro_de(EVIDENCIA_SOLO_LECTURA) == [], (
        f"el arnes escribio dentro del expediente de FASE-A: {registro.dentro_de(EVIDENCIA_SOLO_LECTURA)}")
    assert obs.huellas(EVIDENCIA_SOLO_LECTURA) == protegido_antes, (
        "contenido o metadatos del expediente protegido se movieron")


def test_el_destino_no_puede_apuntar_a_otra_fase_por_defecto():
    """S13: `destino` es obligatorio; el arnes no hereda la constante de FASE-A/B."""
    firma = inspect.signature(correr_a_destino)
    assert firma.parameters["destino"].default is inspect.Parameter.empty, (
        "el arnes define un destino por defecto: eso es lo que re-escribio evidencia cerrada en FASE-A")
    fuente = Path(__file__).read_text(encoding="utf-8")
    constantes = re.findall(r"^([A-Z_]+)\s*=\s*(.+)$", fuente, re.M)
    destinos = [(n, v) for n, v in constantes if "evidence" in v and "SOLO_LECTURA" not in n]
    assert destinos == [], f"el arnes vuelve a fijar un destino de evidencia: {destinos}"
    assert "Solo lectura" in fuente and "No es destino de escritura" in fuente


def test_resumen_publica_el_alcance_del_observador(tmp_path, entorno_falso):
    obs = _observador()
    resumen = Path(correr_a_destino(tmp_path / "m")["destino"]) / "resumen.txt"
    texto = resumen.read_text(encoding="utf-8")
    assert obs.ALCANCE in texto, "el alcance del observador debe publicarse con la evidencia"
    assert "VERDE" in texto and "ROJO" in texto
