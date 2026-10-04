"""AC6 sobre el **guard real** del triaje (fila 1 de la deuda declarada al cierre de FASE-B, 2026-10-04).

QUE SE CURA. `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-B/mutation.json` sello 14 dientes del arnes
del piloto JEV y dejo esta fila abierta con su motivo: el diente que el prompt de FASE-B pidio —`removed`
vacio con respuestas no vacias, y mutar el guard vuelve rojo el test— pertenece a la superficie de
`scripts/triage_lesson_relevance.py`, que no estaba en el mandato de OLA 2. Faltaba ejercitar **la clausula
del script versionado**, no el simbolo del modulo que carga un fixture.

QUE NO SE TOCA. Los dientes de AC14 (`test_triage_mutation_aditividad.py`) siguen apagando
`GUARD_ADITIVIDAD_ACTIVO`, que es la otra puerta del mismo guard. Este archivo muta el **texto de la
reinsercion**: con el simbolo activo y la clausula cortada, la fila anclada igual desaparece. Si alguno de
los dos caminos se borra, este verde pierde su oportunidad de caer.

CERO RED. El emisor es el proveedor FALSO determinista que monta `conftest.py`, con el guard de sockets
autouse de esa carpeta: el triaje pregunta, la puerta responde sin salir a la red.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import inspect
import subprocess
import sys
from pathlib import Path

from tests.support_resolucion_plan import ruta_plan

ROOT = Path(__file__).resolve().parents[3]
TRIAGE = ROOT / "scripts" / "triage_lesson_relevance.py"
NOMBRE_PLAN = "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
LECCIONES = ruta_plan(NOMBRE_PLAN) / "00-lecciones-capitalizadas.md"
# Las cuatro rutas del suelo, dichas por el arnes y no por la copia que se cargue: ver `_apuntar_a_la_raiz`.
INDICE_JSON = ROOT / ".opencode" / "lecciones_index.json"
INDICE_MD = ROOT / ".opencode" / "LECCIONES-INDEX.md"
PLANS = ROOT / ".opencode" / "plans"
CONTEXT = ROOT / ".opencode" / "context"

# La clausula que sostiene la aditividad, anclada por su texto y no por un ordinal: es la unica
# reinsercion del guard (se verifica antes de mutar) y un renombre de variables hace que el mutante reviente
# en la verificacion de unicidad antes que mutar otra linea en silencio.
ANCLA_GUARD = ("    if intentos:\n"
               "        return list(anteriores) + [f for f in propuesta if f not in anteriores], intentos")
MUTANTE_GUARD = ("    if intentos:\n"
                 "        return list(propuesta), intentos")


def _cargar_por_ruta(nombre: str, ruta: Path):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = mod
    antes = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = antes
    return mod


def _apuntar_a_la_raiz(mod):
    """Una copia del guion fuera del repo resuelve sus rutas contra su propio `__file__` (leccion
    «control versionado copiado a temporal hereda su ruta»).

    Dos mechanisms distintos, y hay que cubrir los dos: los globales que se leen al correr (`SCRIPTS`,
    `INDICE_MD`) se parchan aqui, y los que quedaron atados al `def` de la copia (los defaults de
    `leer_suelo`/`comprobar_frescura`) se pasan a mano en `_correr_triaje`. Medido en la primera pasada de
    esta prueba: solo con el parche, el mutante corto por `AUSENTE` sobre
    `Temp/pytest-.../.opencode/lecciones_index.json`, o sea se estaba midiendo el contexto de la copia.
    """
    mod.ROOT = ROOT
    mod.SCRIPTS = ROOT / "scripts"
    mod.DEFAULT_PLANS = PLANS
    mod.DEFAULT_CONTEXT = CONTEXT
    mod.INDICE_JSON = INDICE_JSON
    mod.INDICE_MD = INDICE_MD
    return mod


def _correr_triaje(mod, entorno: dict) -> dict:
    """El camino completo del triaje sobre el arbol vigente, con EL modulo que se le de.

    Las tres rutas del suelo van explicitas por la razon documentada en `_apuntar_a_la_raiz`. Los insumos
    los lee el propio modulo: si el mutante y el original leyeran poblaciones distintas, la diferencia de
    veredictos no se atribuiria a la clausula.
    """
    indice, estado = mod.leer_suelo(INDICE_JSON, plans_dir=PLANS, context_dir=CONTEXT)
    ancladas = mod.filas_ancladas(LECCIONES)
    pendientes = mod.candidatos_de_pertinencia(indice, NOMBRE_PLAN, ancladas)
    informe = mod.construir_informe(NOMBRE_PLAN, pendientes, ancladas, indice, estado,
                                    entorno=dict(entorno))
    return {"seccion": informe["seccion_dos"], "informe": informe,
            "ids_ancladas": [f["id"] for f in ancladas]}


# ----------------------------------------------------------------------------------- la fila AC6


def test_real_triage_guard_preserves_anchored_rows(trl, informe_real, ancladas_reales):
    """`removed` vacio con respuestas no vacias: las filas ancladas de §2 se preservan.

    Las cotas van juntas a proposito. Sin `intentos_filtrados` el vacio de `removed` podria ser un filtro
    que no tuvo nada en la mano; sin `eleccion` en los candidatos podria ser un emisor que no contesto; y
    sin `anchored_before > 0` podria ser un §2 vacio leido como aditivo (L-HF1).
    """
    s = informe_real["seccion_dos"]
    con_respuesta = [c for c in informe_real["candidatos"] if c.get("eleccion")]

    assert con_respuesta, (
        "el emisor no devolvio ninguna eleccion: no hay respuestas que el guard pueda estar preservando")
    assert s["removed"] == [], f"el triaje filtro filas ancladas de §2: {s['removed']}"
    assert s["anchored_before"] == s["anchored_after"] == len(ancladas_reales) > 0, (
        f"antes={s['anchored_before']} despues={s['anchored_after']} filas leidas={len(ancladas_reales)}")
    assert s["intentos_filtrados"], (
        "el guard no tuvo trabajo: el filtro no intento sacar ninguna fila anclada, asi que el `removed` "
        "vacio no afirma AC6")
    assert sorted(s["intentos_filtrados"]) == sorted(s["filas_cuestionadas_sin_borrar"]), (
        "lo que el filtro intento sacar no es lo que el emisor cuestiono: la aditividad se mide sobre otra "
        "poblacion")
    assert set(s["intentos_filtrados"]) <= set([f["id"] for f in ancladas_reales]), (
        "un intento de filtrado nombra una fila que §2 no ancla")
    assert trl.GUARD_ADITIVIDAD_ACTIVO is True, (
        "el guard llega apagado al modulo cargado: se estaria midiendo un mutante, no el script")
    assert informe_real["status"] == "TRIADO", informe_real["status"]
    assert ANCLA_GUARD in inspect.getsource(trl.guardar_filas_ancladas), (
        "la clausula del guard ya no tiene la forma que esta prueba muta: re-leer el ancla antes de "
        "afirmar que AC6 queda cubierta")


def test_el_guard_reintegra_la_fila_anclada_que_la_propuesta_saca(trl, ancladas_reales):
    """La clausula sola, con las filas ancladas **reales** de §2: la que la propuesta saca vuelve intacta.

    Se compara el objeto-fila y su posicion, no solo el id: `guardar_filas_ancladas` devuelve la fila
    literal de §2, y una reinsercion que la reescribiera tendria el mismo id con otra fila.
    """
    assert len(ancladas_reales) >= 2, f"§2 del plan triado tiene {len(ancladas_reales)} filas ancladas"
    objetivo, propuesta = ancladas_reales[0], ancladas_reales[1:]

    despues, intentos = trl.guardar_filas_ancladas(ancladas_reales, propuesta)

    assert intentos == [objetivo["id"]], intentos
    ids = [f["id"] for f in despues]
    assert ids == [f["id"] for f in ancladas_reales], (
        f"el guard no devolvio §2 en su orden o perdio filas: {ids}")
    assert len(ids) == len(set(ids)), "el guard reintegro duplicando la fila"
    fila = next(f for f in despues if f["id"] == objetivo["id"])
    assert fila == objetivo, "la fila reintegrada no es la literal de §2 sino una reescritura"

    intacta, sin_intento = trl.guardar_filas_ancladas(ancladas_reales, list(ancladas_reales))
    assert sin_intento == [] and [f["id"] for f in intacta] == [f["id"] for f in ancladas_reales], (
        "una propuesta sin recorte deberia devolverse tal cual y no publicar intentos")

    agregada = {"id": "L-PRUEBA", "enunciado": "candidato nuevo", "fila": "| `L-PRUEBA` | x |"}
    despues2, intentos2 = trl.guardar_filas_ancladas(ancladas_reales, propuesta + [agregada])
    assert intentos2 == [objetivo["id"]] and despues2[-1] == agregada, (
        "la reinsercion del guard se trago la propuesta nueva: AC6 no puede pagarse con AC10")


def test_mutar_la_clausula_del_guard_hace_caer_la_afirmacion_de_ac6(trl, tmp_path, entorno_falso):
    """El diente: cortado el TEXTO de la reinsercion, `removed` deja de estar vacio por la causa nombrada.

    No se apaga `GUARD_ADITIVIDAD_ACTIVO` (eso ya lo hacen los dientes de AC14): se corta la otra mitad del
    guard, la clausula que reintegra. La copia vive en `tmp_path` y el arbol de trabajo no se toca.
    """
    fuente = TRIAGE.read_text(encoding="utf-8")
    assert fuente.count(ANCLA_GUARD) == 1, (
        f"el ancla aparece {fuente.count(ANCLA_GUARD)} veces en el guion: el mutante no corta lo que se "
        "cree que corta")
    mutado = fuente.replace(ANCLA_GUARD, MUTANTE_GUARD, 1)
    assert mutado != fuente and mutado.count(MUTANTE_GUARD) == 1
    ast.parse(mutado)

    ruta_mutante = tmp_path / "triage_guard_mutado.py"
    ruta_mutante.write_text(mutado, encoding="utf-8", newline="\n")
    copia = _apuntar_a_la_raiz(_cargar_por_ruta("trl_guard_mutado", ruta_mutante))

    real = _correr_triaje(trl, entorno_falso)
    mutante = _correr_triaje(copia, entorno_falso)

    assert real["ids_ancladas"] == mutante["ids_ancladas"], (
        "el mutante y el original no leyeron las mismas filas ancladas: el rojo no es atribuible a la "
        "clausula")
    assert real["seccion"]["removed"] == [], (
        "premissa perdida: sobre el script versionado `removed` ya no esta vacio, asi que el rojo del "
        "mutante no distingue nada")
    assert mutante["seccion"]["removed"], (
        "cortada la clausula del guard sigue sin borrarse ninguna fila anclada: el mutante no toca el "
        f"guard real (L-T4A.5). removed={mutante['seccion']['removed']}")
    assert sorted(mutante["seccion"]["removed"]) == sorted(mutante["seccion"]["intentos_filtrados"]), (
        "lo que el mutante borra no es lo que el filtro intento sacar: el rojo no nombra a la clausula")
    assert mutante["seccion"]["anchored_after"] < mutante["seccion"]["anchored_before"], (
        "el mutante dejo las filas cuestionadas: el conteo no acompaña la afirmacion de AC6")
    assert real["seccion"]["anchored_before"] == mutante["seccion"]["anchored_before"], (
        "el mutante tambien movio la poblacion de entrada: se esta comparando otra corrida")
    assert hashlib.sha256(_lf(TRIAGE.read_bytes())).hexdigest() == SHA_TRIAGE_LF, (
        "el arbol de trabajo se movio mientras corria la prueba: medir sobre un arbol estable")


def test_el_script_que_carga_el_fixture_es_el_versionado(trl):
    """Licencia la palabra «versionado»: lo que carga el fixture es, byte a byte, el blob de HEAD.

    Un mutante dejado aplicado en el arbol de trabajo cae aqui en vez de leerse como conducta del producto.
    La comparacion normaliza el EOL: `git show` publica el blob y el disco puede venir con CRLF segun el
    clon, y esa diferencia de forma no es un cambio de codigo.
    """
    crudo = TRIAGE.read_bytes()
    proc = subprocess.run(["git", "show", f"HEAD:{TRIAGE.relative_to(ROOT).as_posix()}"],
                          capture_output=True, cwd=str(ROOT))
    assert proc.returncode == 0, proc.stderr[:200]
    assert _lf(proc.stdout) == _lf(crudo), (
        f"el script del arbol ({hashlib.sha256(_lf(crudo)).hexdigest()[:12]}) ya no es el versionado "
        f"({hashlib.sha256(_lf(proc.stdout)).hexdigest()[:12]}): la prueba de AC6 mediria un borrador")
    assert Path(trl.__file__).resolve() == TRIAGE.resolve(), (
        "el fixture no cargo el script de la raiz: AC6 se estaria afirmando sobre un substituto")


def _lf(b: bytes) -> bytes:
    return b.replace(b"\r\n", b"\n")


SHA_TRIAGE_LF = hashlib.sha256(
    _lf(subprocess.run(["git", "show", f"HEAD:scripts/triage_lesson_relevance.py"],
                       capture_output=True, cwd=str(ROOT)).stdout)).hexdigest()
