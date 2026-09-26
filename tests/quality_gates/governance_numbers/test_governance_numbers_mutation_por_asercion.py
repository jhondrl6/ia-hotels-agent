"""AC4 — mutation check **por asercion** sobre el simbolo real del guard (R2.8, L-T4A.5, L-V2.1).

Verde a la primera sin rojo es un falso verde potencial (L-VUP-5): este archivo apaga, uno a uno,
los simbolos reales del guard y exige que **la asercion que dice atacar** sea la que desaparece o
cambia su motivo. El anclaje es `assertion_key` (sujeto + afirmacion + documento), **no**
`assertion_id`: los ids son posicionales y se re-numeran cuando un hallazgo cae, anclar en ellos
daria un rojo que nombra a un tercero (la leccion del corpus L-V2.1 en su variante propia, medida
en esta fase y registrada en `10-analisis-post-implementacion.md`).

Tras el bloque B (D1) el arbol de `.agents/` ya no lleva las cifras vencidas, asi que el mutante se
corre contra el **contraejemplo congelado** (`fixtures/`, copia de los documentos antes de D1) y el
mismo `run_all_validations.py` y hook reales: `observed` e historicas quedan identicas al maestro §1.

**S13 — el arnés no escribe en evidencia cerrada, y eso se OBSERVA.** Hasta aqui las salidas se
escribian por ruta hardcodeada en `evidence/…/FASE-A/mutation/`, de modo que correr el test re-pisaba
7 archivos de otra fase (con `git status` limpio cuando el contenido coincidia, y rojo que pisa
cuando ya no). El primer retiro movio el destino a un directorio temporal, pero seguia midiendo
**estado final** (instantaneas antes/despues), que no distingue «nadie abrio un archivo» de «alguien
lo abrio y devolvio los mismos bytes». Ahora:
  * el observador compartido (`tests/support_observador_escrituras.py`) registra las **operaciones de
    escritura** de toda la ejecucion medida, con su ancla positiva (el arnes SI escribe y se ve) antes
    de afirmar la ausencia en `evidence/`;
  * se conserva ademas la comparacion de contenido **y** metadatos del expediente protegido;
  * los tres controles negativos del mandato (a escritor redirigido a destino protegido, b bytes
    identicos, c mtime restaurado) se corren sobre un **expediente desechable** y con el **mismo**
    observador y el **mismo** escritor de la prueba positiva;
  * el alcance del observador esta declarado y probado: cubre el proceso de pytest, no los hijos.
"""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "validate_governance_numbers.py"
WF = "phased_project_executor.md"
TPL = "lecciones-capitalizadas-template.md"
N_WF, N_TPL = WF[:-3], TPL[:-3]          # `name` del documento es su stem
FIXTURES = ROOT / "tests" / "quality_gates" / "governance_numbers" / "fixtures"
DOCS = [{"path": FIXTURES / WF, "name": N_WF},
        {"path": FIXTURES / TPL, "name": N_TPL}]
SOURCE = ROOT / "scripts" / "run_all_validations.py"
HOOK = ROOT / "scripts" / "git_hooks" / "pre-commit"
# Solo lectura: se observa para probar que NADIE escribe aqui (S13). No es destino de escritura.
EVIDENCIA_SOLO_LECTURA = ROOT / "evidence" / "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
# Unica implementacion de `huellas` y del observador de escrituras del repo (mandato §4: no
# duplicar la funcion de huellas dentro del test).
SUPPORT_OBSERVADOR = ROOT / "tests" / "support_observador_escrituras.py"

# Claves de las cuatro aserciones del maestro §1 (estables ante re-numeracion).
K_A1 = "validate_plan_citations.py|check 8|" + N_WF
K_A2 = "validate_lesson_capitalization.py|[9/9]|" + N_WF
K_A3 = "validate_qmind_writeback.py|[12/12]|" + N_WF
K_A4 = "validate_lesson_capitalization.py|[10/10]|" + N_TPL
BASELINE_KEYS = [K_A1, K_A2, K_A3, K_A4]


def _modulo():
    """Nombre de modulo unico por carga: un nombre fijo reutilizaba el `sys.modules` ya cargado
    y el mutante anterior seguia apagado (rojo que no era por el guard mutado)."""
    global _CARGAS
    _CARGAS += 1
    spec = importlib.util.spec_from_file_location(f"vgn_mut_{_CARGAS}", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_CARGAS = 0


def _medir(mut=None) -> dict:
    """Corre el escaneo real contra el arbol vigente con (opcionalmente) un guard apagado."""
    mod = _modulo()
    if mut:
        mut(mod)
    informe = mod.analizar(DOCS, SOURCE, HOOK)
    return {
        "keys": [f["assertion_key"] for f in informe["findings"]],
        "ids": {f["assertion_key"]: f["assertion_id"] for f in informe["findings"]},
        "reasons": {f["assertion_key"]: f["reasons"] for f in informe["findings"]},
        "occurrences": {f["assertion_key"]: len(f["occurrences"])
                        for f in informe["findings"]},
        "no_resueltas": informe["coverage_basis"]["poblacion"]["clase_no_resuelta"],
        "historicas": informe["coverage_basis"]["poblacion"]["clase_historica_congelada"],
    }


MUTANTES = [
    {
        "id": "M-A1",
        "simbolo": "check_n_discrepa()",
        "objetivo": K_A1,
        "apagar": lambda mod: setattr(mod, "check_n_discrepa", lambda claimed, record: False),
        "esperado": {"perdidos": [K_A1], "presentes": [K_A2, K_A3, K_A4]},
    },
    {
        "id": "M-A4",
        "simbolo": "total_discrepa()",
        "objetivo": K_A4 + " (su unico motivo es el denominador: [10/10] vs [10/12])",
        "apagar": lambda mod: setattr(mod, "total_discrepa", lambda claimed, t: False),
        "esperado": {"perdidos": [K_A4], "presentes": [K_A1, K_A2, K_A3],
                     "reasons_de": {K_A2: ["ordinal"], K_A3: ["ordinal"]}},
    },
    {
        "id": "M-A2",
        "simbolo": "ordinal_discrepa()",
        "objetivo": K_A2 + " — el guard mutado aportaba su motivo «ordinal»",
        "apagar": lambda mod: setattr(mod, "ordinal_discrepa", lambda claimed, record: False),
        "esperado": {"perdidos": [], "presentes": BASELINE_KEYS,
                     "reasons_de": {K_A2: ["denominador"], K_A3: ["denominador"]}},
    },
    {
        "id": "M-A3",
        "simbolo": 'KIND_MARKERS["full"]',
        "objetivo": K_A3 + " — sin marcador de modo completo su [12/12] no resuelve fuente",
        "apagar": lambda mod: setattr(mod, "KIND_MARKERS",
                                      {k: v for k, v in mod.KIND_MARKERS.items() if k != "full"}),
        "esperado": {"perdidos": [K_A3], "presentes": [K_A1, K_A2, K_A4],
                     "no_resueltas_suben": True},
    },
    {
        "id": "M-POBLACION",
        "simbolo": "es_mencion_historica()",
        "objetivo": "la regla de poblacion A8 (sin ella «y ninguna otra» se rompe)",
        "apagar": lambda mod: setattr(mod, "es_mencion_historica",
                                      lambda *a, **k: (False, ("sin-guard", "sin-guard"))),
        "esperado": {"perdidos": [], "presentes": BASELINE_KEYS, "hallazgos_extra": True,
                     "historicas_a_cero": True},
    },
    {
        "id": "M-SUJETO",
        "simbolo": "sujeto_de_la_instancia()",
        "objetivo": "la atribucion asercion -> check (sin sujeto no hay contraste posible)",
        "apagar": lambda mod: setattr(mod, "sujeto_de_la_instancia",
                                      lambda ventana, ancla, pool: None),
        "esperado": {"perdidos": BASELINE_KEYS, "presentes": []},
    },
]


@pytest.fixture(scope="module")
def verde() -> dict:
    medida = _medir()
    assert medida["keys"] == BASELINE_KEYS, (
        f"el baseline debe ser exactamente las cuatro aserciones del maestro §1: {medida['keys']}"
    )
    assert medida["historicas"] == 8, "la poblacion congelada tambien forma parte del verde"
    return medida


@pytest.mark.parametrize("mutante", MUTANTES, ids=[m["id"] for m in MUTANTES])
def test_el_rojo_es_causado_por_el_guard_mutado(mutante: dict, verde: dict):
    rojo = _medir(mutante["apagar"])
    esperado = mutante["esperado"]

    perdidos = [k for k in verde["keys"] if k not in rojo["keys"]]
    assert sorted(perdidos) == sorted(esperado["perdidos"]), (
        f"{mutante['id']}: se esperaba perder {esperado['perdidos']}, se perdio {perdidos} "
        "— el rojo debe nombrar la asercion mutada (L-V2.1)"
    )
    for presente in esperado["presentes"]:
        assert presente in rojo["keys"], f"{mutante['id']} no debia tocar {presente}"
    for clave, reasons in esperado.get("reasons_de", {}).items():
        assert rojo["reasons"][clave] == reasons, (
            f"{mutante['id']}: los motivos de {verde['ids'][clave]} debian pasar a {reasons}, "
            f"quedaron {rojo['reasons'][clave]}"
        )
    if esperado.get("no_resueltas_suben"):
        assert rojo["no_resueltas"] > verde["no_resueltas"]
    if esperado.get("hallazgos_extra"):
        assert len(rojo["keys"]) > len(verde["keys"]), (
            "apagar la regla de poblacion debe producir hallazgos adicionales: AC1 dice «y "
            "ninguna otra» justo gracias a ella"
        )
    if esperado.get("historicas_a_cero"):
        assert rojo["historicas"] == 0


def _observador():
    """El observador compartido: la unica implementacion de huellas y de escritura del repo.

    Importado por ruta para que este test y el de interaccion de REGISTRY usen EL MISMO
    observador y la MISMA funcion de huellas (mandato §4: no duplicar la funcion dentro del test).
    """
    global _OBS_MOD
    if _OBS_MOD is None:
        spec = importlib.util.spec_from_file_location(
            "observador_escrituras_compartido", SUPPORT_OBSERVADOR)
        _OBS_MOD = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_OBS_MOD)
    return _OBS_MOD


_OBS_MOD = None


def _escribir_salidas(verde: dict, destino: Path) -> None:
    """Vuelca el verde de baseline y cada mutante en un destino EXPLICITO (nunca en evidence/)."""
    destino.mkdir(parents=True, exist_ok=True)
    verde_txt = [
        "# AC4 VERDE (baseline, guards activos)",
        f"arbol: {ROOT.name} · script: {SCRIPT.relative_to(ROOT).as_posix()}",
        f"assertion_ids: {verde['ids']}",
        f"reasons: {json.dumps(verde['reasons'], ensure_ascii=False, indent=1)}",
        f"occurrences por asercion: {json.dumps(verde['occurrences'], ensure_ascii=False)}",
        f"instancias no resueltas: {verde['no_resueltas']}",
        f"instancias historicas congeladas: {verde['historicas']}",
        "",
        "comando de reproduccion:",
        "  python -m pytest tests/quality_gates/governance_numbers/"
        "test_governance_numbers_mutation_por_asercion.py -q",
    ]
    (destino / "verde_baseline.txt").write_text("\n".join(verde_txt) + "\n", encoding="utf-8")
    for mut in MUTANTES:
        rojo = _medir(mut["apagar"])
        lineas = [
            f"# AC4 ROJO — mutante {mut['id']} · objetivo: {mut['objetivo']}",
            f"simbolo real apagado: {mut['simbolo']}",
            f"aserciones en verde: {verde['keys']}",
            f"aserciones en rojo: {rojo['keys']}",
            f"perdidos: {[k for k in verde['keys'] if k not in rojo['keys']]}",
            f"gained: {[k for k in rojo['keys'] if k not in verde['keys']]}",
            f"reasons en rojo: {json.dumps(rojo['reasons'], ensure_ascii=False)}",
            f"ids en rojo (posicionales, se re-numerican): {json.dumps(rojo['ids'])}",
            f"no resueltas: {rojo['no_resueltas']} | historicas: {rojo['historicas']}",
            f"esperado por el test: {json.dumps(mut['esperado'], ensure_ascii=False, default=str)}",
            "",
            "comando de reproduccion (mismo que genero este archivo):",
            "  python -m pytest tests/quality_gates/governance_numbers/"
            "test_governance_numbers_mutation_por_asercion.py -q",
        ]
        (destino / f"mutante_{mut['id']}.txt").write_text("\n".join(lineas) + "\n",
                                                          encoding="utf-8")


SALIDAS_ESPERADAS = ["verde_baseline.txt"] + [f"mutante_{m['id']}.txt" for m in MUTANTES]


def _es_escritura_de_archivo(operacion: str) -> bool:
    if operacion.startswith(("Path.open(", "open(")) and operacion.endswith(")"):
        modo = operacion.partition("(")[2][:-1]
        return any(c in modo for c in "wax+")
    return operacion in {
        "Path.write_text", "Path.write_bytes", "os.open", "os.truncate",
        "Path.rename->dest", "Path.replace->dest", "os.rename->dst", "os.replace->dst",
        "shutil.copyfile->dst", "shutil.copy->dst", "shutil.copy2->dst", "shutil.move->dst",
    }


def _exigir_escrituras_de_archivos(registro, destino: Path):
    esperadas = {(destino / nombre).resolve() for nombre in SALIDAS_ESPERADAS}
    vistas = {Path(ruta).resolve() for op, ruta, ok in registro.operaciones
              if ok and _es_escritura_de_archivo(op)}
    faltantes = esperadas - vistas
    assert not faltantes, (
        "faltan escrituras de archivos por ruta exacta: "
        f"{sorted(p.as_posix() for p in faltantes)}; observadas: {registro.operaciones}")


def test_las_dos_salidas_quedan_en_destino_exPLICITO(verde: dict, tmp_path: Path):
    """AC4 sin el lado rojo en disco queda ⚠️ (R2.4): aqui se escriben el verde y cada mutante,
    pero en un destino temporal que el llamador nombra, no en el expediente de otra fase."""
    destino = tmp_path / "mutation"
    _escribir_salidas(verde, destino)
    assert (destino / "verde_baseline.txt").exists()
    for mut in MUTANTES:
        assert (destino / f"mutante_{mut['id']}.txt").exists()


def test_la_ejecucion_medida_no_abre_ninguna_escritura_dentro_de_evidence(verde: dict,
                                                                          tmp_path: Path):
    """S13 con el mecanismo real: se observan las APERTURAS de escritura de toda la ejecucion medida.

    Antes esta prueba comparaba instantaneas de estado antes/despues alrededor de funciones puras,
    lo que no distingue «nadie abrio un archivo» de «alguien lo abrio y volvio los mismos bytes».
    Ahora el observador compartido registra cada operacion de escritura del bloque, y se afirma el
    ancla positiva (el arnes SI escribe, y se ve) antes de afirmar la ausencia en `evidence/`:
    sin ese ancla, un observador caido daria verde.
    """
    obs = _observador()
    destino = tmp_path / "mutation"

    with obs.observador_de_escrituras() as registro:
        _medir()
        for mut in MUTANTES:
            _medir(mut["apagar"])
        _escribir_salidas(verde, destino)          # el escritor real, a destino explicito

    # --- ancla positiva: el observador vio las escrituras reales del arnes ---
    vistas = registro.dentro_de(destino)
    rutas_vistas = {Path(r).name for _, r, _ in vistas}
    assert rutas_vistas >= set(SALIDAS_ESPERADAS), (
        "el observador no vio las escrituras que el arnes acaba de hacer; una ausencia en evidence/ "
        f"no significaria nada. Vio: {sorted(rutas_vistas)}")
    _exigir_escrituras_de_archivos(registro, destino)

    # --- propiedad: ninguna de esas operaciones apunta a evidence/ ----------------
    dentro = registro.dentro_de(EVIDENCIA_SOLO_LECTURA)
    assert dentro == [], (
        "el arnés de mutación abrió escrituras dentro de evidence/: re-medir no puede gobernar el "
        f"registro cerrado de otra fase (S13). Observadas: {dentro}")

    # --- y el estado final del expediente protegido tampoco se movio -------------
    assert obs.huellas(EVIDENCIA_SOLO_LECTURA), (
        "el expediente que se protege debe existir para que la prueba signifique algo")


def test_re_medir_no_reescribe_expedientes_cerrados(verde: dict, tmp_path: Path):
    """S13, lado de estado: contenido Y metadatos del expediente protegido no cambian.

    Se conserva ademas de la observacion de operaciones (la prueba anterior): el mandato pide las
    dos cosas. Un `git status` limpio con mtimes movidos es justo lo que solo el mtime delata.
    """
    obs = _observador()
    antes = obs.huellas(EVIDENCIA_SOLO_LECTURA)
    assert antes, "el expediente que se protege debe existir para que la prueba signifique algo"
    _medir()
    for mut in MUTANTES:
        _medir(mut["apagar"])
    _escribir_salidas(verde, tmp_path / "mutation")          # destino explicito, fuera de evidence/
    despues = obs.huellas(EVIDENCIA_SOLO_LECTURA)
    assert despues == antes, (
        "el arnés de mutación volvió a escribir dentro de evidence/: re-medir no puede gobernar el "
        "registro cerrado de otra fase (S13)")


def _expediente_desechable(tmp_path: Path) -> Path:
    """Un expediente «cerrado» simulado, NUNCA evidencia historica real (mandato §4)."""
    protegido = tmp_path / "expediente_cerrado" / "FASE-A" / "mutation"
    protegido.mkdir(parents=True)
    for nombre in SALIDAS_ESPERADAS:
        (protegido / nombre).write_text("contenido cerrado de otra fase\n", encoding="utf-8")
    return tmp_path / "expediente_cerrado"


def test_control_a_el_escritor_real_redirigido_a_destino_protegido_es_cazado(tmp_path: Path,
                                                                             verde: dict):
    """(a) El escritor real, apuntado a un destino protegido, cae en el MISMO observador."""
    obs = _observador()
    raiz_protegida = _expediente_desechable(tmp_path)
    destino_prohibido = raiz_protegida / "FASE-A" / "mutation"

    with obs.observador_de_escrituras() as registro:
        _escribir_salidas(verde, destino_prohibido)

    caza = registro.dentro_de(raiz_protegida)
    assert caza, (
        "el observador NO detecto que el escritor real volco dentro de un expediente protegido: "
        "sin este rojo, la prueba de ausencia anterior no tendria dientes")
    # Misma causa que afirma la prueba positiva: operaciones de escritura, no strings del test.
    ops = {op for op, _, _ in caza}
    assert any("write_text" in op or "mkdir" in op for op in ops), f"observado: {caza}"
    _exigir_escrituras_de_archivos(registro, destino_prohibido)


def test_control_b_reescribir_bytes_identicos_se_observa_aunque_el_hash_no(verde: dict,
                                                                          tmp_path: Path):
    """(b) Bytes identicos: el hash queda igual y el observador sigue viendo la escritura."""
    obs = _observador()
    raiz_protegida = _expediente_desechable(tmp_path)
    destino = raiz_protegida / "FASE-A" / "mutation"

    with obs.observador_de_escrituras() as primera:
        _escribir_salidas(verde, destino)
    _exigir_escrituras_de_archivos(primera, destino)
    estado_1 = obs.huellas(destino)
    assert estado_1, "la primera ronda debe haber creado archivos para que la segunda signifique algo"

    with obs.observador_de_escrituras() as segunda:
        _escribir_salidas(verde, destino)          # mismo contenido, bytes identicos
    estado_2 = obs.huellas(destino)

    hashes_1 = {k: v[0] for k, v in estado_1.items()}
    hashes_2 = {k: v[0] for k, v in estado_2.items()}
    assert hashes_1 == hashes_2, (
        "precondition del control: la re-escritura tiene que dejar bytes identicos; si no, este "
        "rojo seria por otra causa")
    caza = segunda.dentro_de(raiz_protegida)
    assert caza, (
        "el observador no vio la re-escritura de bytes identicos: «sin cambio de contenido» se "
        "leeria como «nadie escribio» (S13)")
    _exigir_escrituras_de_archivos(segunda, destino)
    # Y aqui si que el mtime aporta: la pareja (hash, mtime) cambia donde el hash solo no ve nada.
    assert estado_1 != estado_2, (
        "la pareja (hash, mtime) tampoco se movio: el sistema de archivos no actualizo el mtime y "
        "el control b) perderia su lectura complementaria")


def test_control_c_mtime_restaurado_no_oculta_la_escritura_al_observador(verde: dict,
                                                                        tmp_path: Path):
    """(c) Si alguien restaura el mtime tras escribir, el estado final vuelve a ser igual: solo el
    observador de operaciones lo ve. Es el caso que el cierre anterior no cubria.
    """
    obs = _observador()
    raiz_protegida = _expediente_desechable(tmp_path)
    destino = raiz_protegida / "FASE-A" / "mutation"

    with obs.observador_de_escrituras() as primera:
        _escribir_salidas(verde, destino)
    _exigir_escrituras_de_archivos(primera, destino)
    antes = obs.huellas(destino)

    with obs.observador_de_escrituras() as segunda:
        _escribir_salidas(verde, destino)
    # Restaurar los mtimes al valor previo: mecanismo permitido para este control en desechable.
    for ruta, (h, mtime_ns, tam) in antes.items():           # noqa: B007
        p = Path(ruta)
        if p.exists():
            st = p.stat()
            os.utime(p, ns=(st.st_atime_ns, mtime_ns))
    despues = obs.huellas(destino)

    assert {k: (v[0], v[1]) for k, v in antes.items()} == \
           {k: (v[0], v[1]) for k, v in despues.items()}, (
        "precondition: tras restaurar el mtime el estado final debe volver a ser igual; si no, el "
        "control c) no estaria ejercitando lo que dice")
    assert segunda.dentro_de(raiz_protegida), (
        "con hash e mtime iguales el observador tampoco vio la escritura: «sin escritura» seria "
        "indefendible (S13)")
    _exigir_escrituras_de_archivos(segunda, destino)


def test_control_observador_ciego_a_escrituras_conserva_mkdir(verde: dict, tmp_path: Path,
                                                             monkeypatch):
    obs = _observador()
    referencia = tmp_path / "referencia"
    destino = tmp_path / "ciego"
    with obs.observador_de_escrituras() as visible:
        _escribir_salidas(verde, referencia)
    _exigir_escrituras_de_archivos(visible, referencia)
    assert not destino.exists()

    class NotificacionesSinEscrituras(list):
        def append(self, operacion):
            if not _es_escritura_de_archivo(operacion[0]):
                super().append(operacion)

    with obs.observador_de_escrituras() as ciego:
        monkeypatch.setattr(ciego, "operaciones", NotificacionesSinEscrituras())
        _escribir_salidas(verde, destino)

    assert {nombre: (destino / nombre).read_bytes() for nombre in SALIDAS_ESPERADAS} == {
        nombre: (referencia / nombre).read_bytes() for nombre in SALIDAS_ESPERADAS
    }, "precondition: el escritor real debe producir las siete salidas pese al observador ciego"
    assert ciego.operaciones, "el control no debe vaciar todo el registro del observador"
    assert any(op == "Path.mkdir" and Path(ruta).resolve() == destino.resolve()
               for op, ruta, _ in ciego.operaciones)
    assert all(not _es_escritura_de_archivo(op) for op, _, _ in ciego.operaciones)
    with pytest.raises(AssertionError, match="faltan escrituras de archivos por ruta exacta") as rojo:
        _exigir_escrituras_de_archivos(ciego, destino)
    for nombre in SALIDAS_ESPERADAS:
        assert (destino / nombre).resolve().as_posix() in str(rojo.value)


def test_el_observador_declara_que_no_cubre_procesos_hijos(tmp_path: Path):
    """El alcance del observador se publica, no se supone: un hijo escapa al parcheo in-process.

    Medido, no declarado de oido: se lanza un `subprocess` que escribe dentro de un directorio
    «protegido» desechable y el observador NO lo ve, mientras que si ve la escritura in-process
    del mismo bloque. La limitacion queda asi probada y leida por quien consuma la prueba anterior.
    """
    obs = _observador()
    protegido = tmp_path / "alcance"
    (protegido / "hijo.txt").parent.mkdir(parents=True, exist_ok=True)
    destino_hijo = protegido / "hijo.txt"
    destino_local = protegido / "local.txt"

    with obs.observador_de_escrituras() as registro:
        subprocess.run([sys.executable, "-c",
                        f"open(r{str(destino_hijo)!r}, 'w').write('x')"],
                       check=True, capture_output=True)
        destino_local.write_text("x", encoding="utf-8")

    vistas = {Path(r).name for _, r, _ in registro.dentro_de(protegido)}
    assert "local.txt" in vistas, "el observador perdio la escritura in-process"
    assert "hijo.txt" not in vistas, (
        "el observador dice cubrir procesos hijos pero no puede: hay que retirarlo del alcance "
        "declarado o cubrirlo por otro mecanismo")
    assert "procesos hijos" in obs.ALCANCE and "NO cubre" in obs.ALCANCE, obs.ALCANCE


def test_el_arnes_no_conoce_ruta_de_evidencia_como_destino_de_escritura():
    """Estructura, no solo conducta: si reaparece una ruta de evidencia hardcodeada como destino de
    escritura (`write`/`mkdir` sobre `evidence/`), esto se pone rojo aunque nadie la invoque hoy."""
    texto = Path(__file__).read_text(encoding="utf-8")
    escrituras = [linea.strip() for linea in texto.splitlines()
                  if "evidence" in linea.lower()
                  and not linea.strip().startswith("#")
                  and any(k in linea for k in ("write_text(", ".mkdir(", "open(", ".write("))]
    assert escrituras == [], (
        f"el arnés vuelve a nombrar evidence/ como destino de escritura: {escrituras}")
