"""FASE-H (AC17/AC9/AC13): runner de intento unico, lector de control y captura saneada.

El hijo es **falso** y stdlib (`sys.executable -c ...`): ninguna prueba de este archivo lanza
`main.py v4complete`, y ninguna toca `evidence/.../FASE-E2E/run_control.json`, que es la reserva
productiva (el ultimo test lo comprueba). Los controles de prueba viven en `tmp_path`.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
import signal
import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
PLAN = "REFACTOR-WHATSAPP-ENTREGA-2026-09-18"
DIR_FASE = RAIZ / "evidence" / PLAN / "FASE-H"
RUTA_RUNNER = DIR_FASE / "run_once.py"
CONTROL_PRODUCTIVO = RAIZ / "evidence" / PLAN / "FASE-E2E" / "run_control.json"


def _cargar(nombre: str, ruta: Path):
    espec = importlib.util.spec_from_file_location(nombre, str(ruta))
    modulo = importlib.util.module_from_spec(espec)
    espec.loader.exec_module(modulo)
    return modulo


run_once = _cargar("run_once_h_ac17", RUTA_RUNNER)

# Hijo falso: escribe en stdout una forma de credencial ARMADA POR CONCATENACION (el literal
# completo no puede vivir en un archivo versionado: lo cazaria `_check_no_secrets`, que lee el
# diff staged). Es la misma tecnica de re-anclaje que dejo FASE-F en `test_p5_ac_s1_...`.
FORMA_CREDENCIAL = "sk-" + "or-" + "SINTETICOPARAPRUEBA0000000000"
# El hijo arma la forma por concatenacion DENTRO del proceso: el argv nunca lleva el literal
# completo, porque el control persiste el argv y ahi yes el guard del control lo cortaria
# (que es exactamente lo que prueba `test_un_control_con_forma_de_credencial_no_llega_a_disco`).
HIJO_QUE_FILTRA = (
    "import sys; "
    "s = 'sk-' + 'or-' + 'SINTETICOPARAPRUEBA0000000000'; "
    "sys.stdout.write('veo ' + s + chr(10)); "
    "sys.stderr.write('key=' + s + chr(10))"
)
HIJO_EXITO = "import sys; sys.stdout.write('pipeline termino\\n')"
HIJO_FALLO = "import sys; sys.stderr.write('reviento\\n'); raise SystemExit(3)"
HIJO_DUERME = "import time; time.sleep(30)"


def preflight_favorable(argv: list[str], raiz: Path | None = None) -> dict:
    return {
        "intentos": 0,
        "spawn_autorizado": True,
        "requisitos": {"todo": {"cumple": True}},
        "argv_congelado": list(argv),
        "source_hashes": run_once.congelar_hashes(raiz=raiz or Path.cwd()),
        "identidades": {"hotel_id_del_reporte": "hotel_prueba"},
        "snapshot_memoria": {"archivos": 0},
    }


def _matar(pid: int | None) -> None:
    if not pid:
        return
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/F"], capture_output=True, check=False
            )
        else:
            os.kill(int(pid), signal.SIGTERM)
    except OSError:
        pass


@pytest.fixture
def control(tmp_path: Path) -> Path:
    return tmp_path / "run_control.json"


# ---------------------------------------------------------------------------
# AC17 — reserva exclusiva y consumo del unico intento
# ---------------------------------------------------------------------------
def test_la_reserva_se_crea_por_exclusion_antes_de_spawn(control):
    argv = [sys.executable, "-c", HIJO_EXITO]
    llamado = {}

    class HijoFalso:
        pid = 424242
        returncode = 0

        def communicate(self, timeout=None):
            # Cuando se crea el proceso, la reserva YA debe existir en disco.
            llamado["control_existente"] = control.exists()
            llamado["contenido"] = json.loads(control.read_text(encoding="utf-8"))
            return b"pipeline termino\n", b""

    def popen_fake(*a, **k):
        return HijoFalso()

    resultado = run_once.lanzar_unico(
        control_path=control, preflight=preflight_favorable(argv), argv=argv, popen=popen_fake
    )
    assert llamado["control_existente"] is True
    assert llamado["contenido"]["attempts"] == 1
    assert llamado["contenido"]["estado"] == run_once.ESTADO_EN_EJECUCION
    assert resultado["estado"] == run_once.ESTADO_FINALIZADO
    assert resultado["exit_code"] == 0


def test_el_intento_queda_consumido_aunque_el_hijo_falla(control):
    argv = [sys.executable, "-c", HIJO_FALLO]
    resultado = run_once.lanzar_unico(
        control_path=control, preflight=preflight_favorable(argv), argv=argv
    )
    assert resultado["estado"] == run_once.ESTADO_FALLO
    assert resultado["exit_code"] == 3
    control_after = json.loads(control.read_text(encoding="utf-8"))
    assert control_after["attempts"] == 1
    with pytest.raises(run_once.SegundaReservaRechazada):
        run_once.lanzar_unico(
            control_path=control,
            preflight=preflight_favorable(argv),
            argv=argv,
            popen=lambda *a, **k: pytest.fail("relanzo tras el fallo"),
        )


def test_la_reserva_existente_no_se_sobrescribe_ni_se_borra(control):
    contenido_viejo = json.dumps({"estado": "FINALIZADO", "attempts": 1, "marca": "intocable"})
    control.write_text(contenido_viejo, encoding="utf-8", newline="\n")
    sha_antes = hashlib.sha256(control.read_bytes()).hexdigest()
    argv = [sys.executable, "-c", HIJO_EXITO]
    with pytest.raises(run_once.SegundaReservaRechazada):
        run_once.reservar(control_path=control, argv=argv, preflight={}, cwd=".")
    assert hashlib.sha256(control.read_bytes()).hexdigest() == sha_antes
    assert control.read_text(encoding="utf-8") == contenido_viejo


def test_timeout_no_concede_segunda_ejecucion_y_no_fabrica_exit_code(control):
    argv = [sys.executable, "-c", HIJO_DUERME]
    resultado = run_once.lanzar_unico(
        control_path=control, preflight=preflight_favorable(argv), argv=argv, espera=0.5
    )
    datos = json.loads(control.read_text(encoding="utf-8"))
    try:
        assert resultado["estado"] == run_once.ESTADO_TIMEOUT
        assert datos["exit_code"] is None, "el exit code no se inventa: no se observo terminacion"
        assert datos["attempts"] == 1
        with pytest.raises(run_once.SegundaReservaRechazada):
            run_once.lanzar_unico(
                control_path=control, preflight=preflight_favorable(argv), argv=argv, espera=0.5
            )
    finally:
        _matar(datos.get("pid"))


def test_la_vigilancia_se_reanuda_sin_relanzar(control):
    argv = [sys.executable, "-c", HIJO_DUERME]
    run_once.lanzar_unico(
        control_path=control, preflight=preflight_favorable(argv), argv=argv, espera=0.5
    )
    datos = json.loads(control.read_text(encoding="utf-8"))
    pid = datos["pid"]
    try:
        observacion = run_once.vigilar(control)
        assert observacion["accion"] == "observando", observacion
        assert observacion["vivo"] is True
        assert run_once.pid_vivo(pid) is True
        # Vigilar no sabe lanzar: el unico spawn del modulo vive en lanzar_unico.
        arbol = ast.parse(RUTA_RUNNER.read_text(encoding="utf-8"))
        cuerpo_vigilar = next(
            n for n in ast.walk(arbol) if isinstance(n, ast.FunctionDef) and n.name == "vigilar"
        )
        nombres = {
            n.func.id
            for n in ast.walk(cuerpo_vigilar)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
        }
        assert "Popen" not in nombres and "lanzar_unico" not in nombres
        assert json.loads(control.read_text(encoding="utf-8"))["attempts"] == 1
    finally:
        _matar(pid)


def test_dos_lanzadores_concurrentes_uno_solo_crea_proceso(control):
    argv = [sys.executable, "-c", HIJO_EXITO]
    procesos_creados = []
    barrida = threading.Barrier(2)

    class HijoFalso:
        pid = 515151
        returncode = 0

        def communicate(self, timeout=None):
            return b"", b""

    def popen_contador(*a, **k):
        procesos_creados.append(a)
        return HijoFalso()

    resultados = {}

    def lanzador(nombre):
        barrida.wait()
        try:
            run_once.lanzar_unico(
                control_path=control,
                preflight=preflight_favorable(argv),
                argv=argv,
                popen=popen_contador,
            )
            resultados[nombre] = "gano"
        except run_once.SegundaReservaRechazada:
            resultados[nombre] = "rechazado"

    hilos = [threading.Thread(target=lanzador, args=(n,), name=n) for n in ("a", "b")]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join(timeout=30)
    assert sorted(resultados.values()) == ["gano", "rechazado"], (
        "los dos lanzadores ganaron: sin O_EXCL la reserva exclusiva no existe"
    )
    assert len(procesos_creados) == 1, "el perdedor tiene que rechazar ANTES de crear proceso"


def test_un_fallo_de_spawn_no_borra_la_reserva_ni_reintenta(control):
    argv = ["este-programa-no-existe-en-ningun-path-iah"]

    def popen_roto(*a, **k):
        raise OSError("el ejecutable no existe")

    resultado = run_once.lanzar_unico(
        control_path=control, preflight=preflight_favorable(argv), argv=argv, popen=popen_roto
    )
    datos = json.loads(control.read_text(encoding="utf-8"))
    assert resultado["estado"] == run_once.ESTADO_FALLO
    assert datos["attempts"] == 1
    assert "spawn fallo" in datos["causa_estado"]
    assert datos["exit_code"] is None, "sin proceso no hay exit code que inventar"
    with pytest.raises(run_once.SegundaReservaRechazada):
        run_once.lanzar_unico(
            control_path=control,
            preflight=preflight_favorable(argv),
            argv=argv,
            popen=lambda *a, **k: pytest.fail("reintento automatico"),
        )


def test_control_dudoso_es_terminal_y_no_se_resea(control):
    argv = [sys.executable, "-c", HIJO_EXITO]
    run_once.reservar(control_path=control, argv=argv, preflight=preflight_favorable(argv), cwd=".")
    run_once.transicionar(control, run_once.ESTADO_EN_EJECUCION, pid=999_998, iniciado_en="x")
    observacion = run_once.vigilar(control)
    assert observacion["accion"] == "dudoso"
    assert observacion["estado"] == run_once.ESTADO_DUDOSO
    with pytest.raises(run_once.TransicionInvalida):
        run_once.transicionar(control, run_once.ESTADO_EN_EJECUCION)


def test_attempts_no_se_baja_jamas(control):
    argv = [sys.executable, "-c", HIJO_EXITO]
    run_once.reservar(control_path=control, argv=argv, preflight=preflight_favorable(argv), cwd=".")
    with pytest.raises(run_once.TransicionInvalida, match="attempts"):
        run_once.transicionar(control, run_once.ESTADO_EN_EJECUCION, attempts=0)


# ---------------------------------------------------------------------------
# AC17 — el preflight manda antes que la reserva
# ---------------------------------------------------------------------------
def test_preflight_no_favorable_no_consume_la_reserva(control):
    argv = [sys.executable, "-c", HIJO_EXITO]
    pf = {**preflight_favorable(argv), "spawn_autorizado": False, "requisitos": {"f": {"cumple": False}}}
    with pytest.raises(run_once.PreflightNoFavorable):
        run_once.lanzar_unico(
            control_path=control,
            preflight=pf,
            argv=argv,
            popen=lambda *a, **k: pytest.fail("spawn con preflight en contra"),
        )
    assert not control.exists(), "el rechazo previo deja el contador en 0/1"


def test_un_preflight_con_intentos_distintos_de_cero_se_rechaza(control):
    argv = [sys.executable, "-c", HIJO_EXITO]
    pf = {**preflight_favorable(argv), "intentos": 1}
    with pytest.raises(run_once.PreflightNoFavorable, match="intentos"):
        run_once.lanzar_unico(control_path=control, preflight=pf, argv=argv)


def test_divergencia_de_hash_contra_el_preflight_detiene_el_spawn(control, tmp_path):
    argv = [sys.executable, "-c", HIJO_EXITO]
    pf = preflight_favorable(argv, raiz=tmp_path)
    pf["source_hashes"] = {k: "deadbeef" for k in pf["source_hashes"]}
    with pytest.raises(run_once.DivergenciaDeHash):
        run_once.lanzar_unico(
            control_path=control,
            preflight=pf,
            argv=argv,
            raiz=tmp_path,
            popen=lambda *a, **k: pytest.fail("spawn con arbol divergente"),
        )
    assert not control.exists()


def test_un_argv_que_el_preflight_no_autorizo_se_rechaza(control):
    pf = preflight_favorable([sys.executable, "-c", HIJO_EXITO])
    with pytest.raises(run_once.PreflightNoFavorable, match="argv"):
        run_once.lanzar_unico(
            control_path=control,
            preflight=pf,
            argv=[sys.executable, "-c", HIJO_EXITO, "--extra"],
            popen=lambda *a, **k: pytest.fail("spawn con argv no autorizado"),
        )


def test_el_congelado_es_el_literal_del_maestro_mas_el_modo_efectivo():
    """L-VUP-9: banderas comprobadas, ninguna inventada, y --permission-mode escrito."""
    assert run_once.ARGUMENTOS_DEL_PARSER[0] == "v4complete"
    for bandera in ("--url", "--nombre", "--output"):
        assert bandera in run_once.ARGUMENTOS_HIJO
    assert run_once.ARGUMENTOS_HIJO.count("--permission-mode") == 1
    assert run_once.ARGUMENTOS_HIJO[-1] == "auto"
    for inventada in ("--force", "--deploy", "--skip-check", "--dry-run", "--onboarding-file"):
        assert inventada not in run_once.ARGUMENTOS_HIJO
    sys.path.insert(0, str(RAIZ))
    import main

    args = main.build_parser().parse_args(run_once.ARGUMENTOS_DEL_PARSER)
    assert args.command == "v4complete"
    assert args.url == run_once.URL_CORRIDA
    assert args.permission_mode == "auto"


def test_congelar_hashes_declara_el_ausente_en_lugar_de_omitirlo(tmp_path):
    inventario = run_once.congelar_hashes(("existe.py", "no-existe.py"), raiz=tmp_path)
    (tmp_path / "existe.py").write_text("x", encoding="utf-8")
    inventario = run_once.congelar_hashes(("existe.py", "no-existe.py"), raiz=tmp_path)
    assert inventario["no-existe.py"] == "AUSENTE"
    assert inventario["existe.py"] != "AUSENTE"


# ---------------------------------------------------------------------------
# AC9 — el lector nuevo del control
# ---------------------------------------------------------------------------
def test_leer_control_distingue_absent_vacio_valido_y_error(control):
    assert run_once.leer_control(control)["read_status"] == run_once.READ_ABSENT
    control.write_text("", encoding="utf-8")
    vacio = run_once.leer_control(control)
    assert vacio["read_status"] == run_once.READ_OK and vacio["data"] == {}, (
        "L-PF10: una lectura vacia valida no es fuente ausente"
    )
    control.write_text("{ no es json", encoding="utf-8")
    assert run_once.leer_control(control)["read_status"] == run_once.READ_ERROR
    control.write_text("[1, 2]", encoding="utf-8")
    erro_raiz = run_once.leer_control(control)
    assert erro_raiz["read_status"] == run_once.READ_ERROR and "objeto" in erro_raiz["cause"]
    assert run_once.leer_control(control.parent)["read_status"] == run_once.READ_ERROR, (
        "una ruta que no es archivo es READ_ERROR, no ABSENT"
    )


def test_leer_control_sobre_un_control_real_de_prueba(control):
    argv = [sys.executable, "-c", HIJO_EXITO]
    run_once.lanzar_unico(
        control_path=control,
        preflight=preflight_favorable(argv),
        argv=argv,
        popen=lambda *a, **k: type(
            "H", (), {"pid": 77, "returncode": 0, "communicate": lambda self, timeout=None: (b"", b"")}
        )(),
    )
    lectura = run_once.leer_control(control)
    assert lectura["read_status"] == run_once.READ_OK
    assert lectura["data"]["estado"] == run_once.ESTADO_FINALIZADO
    assert lectura["data"]["pid"] == 77


def test_el_preflight_productivo_es_legible_por_el_llector_nuevo():
    """Baseline real del lector: el preflight que publico `1c20695`, no un fixture.

    Se lee la copia preservada porque el `preflight.json` del arbol ya es favorable (consentimiento
    del operador emitido el 2026-10-06); su gemelo post-consentimiento lo gobierna
    `test_el_preflight_vigente_es_favorable_por_lectura_no_por_endulzamiento`.
    """
    ruta = DIR_FASE / "preflight_2026-10-06_no_favorable.json"
    if not ruta.is_file():
        pytest.skip("H no emitió preflight: el lector queda sin baseline real")
    lectura = run_once.leer_control(ruta)
    assert lectura["read_status"] == run_once.READ_OK
    assert lectura["data"]["intentos"] == 0
    assert lectura["data"]["spawn_autorizado"] is False
    requisito = lectura["data"]["requisitos"]["consentimiento_datado_sobre_la_url_viva"]
    assert requisito["cumple"] is False
    assert "iah-consentimiento" in requisito["causa"]
    assert lectura["data"]["requisitos"]["revocacion_de_claves"][
        "acreditada_por_evidencia_operativa"
    ] is False, "el informe de H no acredita revocacion por si solo"


# ---------------------------------------------------------------------------
# AC13 — captura saneada antes de disco y de consola (cierra S-F8)
# ---------------------------------------------------------------------------
def test_la_captura_de_stdout_redacta_antes_de_escribir(tmp_path, control):
    argv = [sys.executable, "-c", HIJO_QUE_FILTRA]
    resultado = run_once.lanzar_unico(
        control_path=control,
        preflight=preflight_favorable(argv),
        argv=argv,
        captura_dir=tmp_path / "capturas",
    )
    stdout = (tmp_path / "capturas" / "captura_stdout.txt").read_text(encoding="utf-8")
    stderr = (tmp_path / "capturas" / "captura_stderr.txt").read_text(encoding="utf-8")
    for texto, canal in ((stdout, "stdout"), (stderr, "stderr")):
        assert FORMA_CREDENCIAL not in texto, f"{canal} conserva el valor crudo"
        assert run_once.cargar_sumidero().contains_secret_shape(texto) is False
    assert resultado["capturas"]["stdout"]["crudo_en_disco"] is False
    assert not list((tmp_path / "capturas").glob("*crudo*")), "no puede existir un crudo en disco"
    control_en_disco = control.read_text(encoding="utf-8")
    assert FORMA_CREDENCIAL not in control_en_disco


def test_el_guard_de_fuga_operante_cuando_redaccion_se_apaga(tmp_path, monkeypatch):
    """Desconectar la redaccion tiene que dar rojo por el guard, no escribir el leak."""
    import modules.utils.redaction as redaccion

    monkeypatch.setattr(redaccion, "redact_secrets", lambda texto: texto)
    monkeypatch.setattr(run_once, "cargar_sumidero", lambda raiz=None: redaccion)
    with pytest.raises(run_once.CapturaSinRedactar):
        run_once.redactar_salida(f"voy a filtrar {FORMA_CREDENCIAL}", canal="test", raiz=tmp_path)


def test_un_control_con_forma_de_credencial_no_llega_a_disco(tmp_path):
    control = tmp_path / "run_control.json"
    argv = ["hijo", FORMA_CREDENCIAL]
    with pytest.raises(run_once.CapturaSinRedactar):
        run_once.reservar(control_path=control, argv=argv, preflight={}, cwd=".")
    assert not control.exists()


def test_assert_redacted_tiene_lamador_en_el_producto():
    """S-F8: F definio el guard y no tenia boca productiva; H es esa boca."""
    arbol = ast.parse(RUTA_RUNNER.read_text(encoding="utf-8"))
    cuerpo = next(
        n for n in ast.walk(arbol) if isinstance(n, ast.FunctionDef) and n.name == "redactar_salida"
    )
    llamadas = {
        n.func.attr
        for n in ast.walk(cuerpo)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
    }
    assert "assert_redacted" in llamadas
    assert "redact_secrets" in llamadas


def test_el_runner_es_stdlib_y_no_arrastra_providers_ni_credenciales():
    """AST del import: `modules.*` esta prohibido; el sumidero entra por ruta de archivo."""
    arbol = ast.parse(RUTA_RUNNER.read_text(encoding="utf-8"))
    importados = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            importados.update(a.name.split(".")[0] for a in nodo.names)
        elif isinstance(nodo, ast.ImportFrom):
            if nodo.module:
                importados.add(nodo.module.split(".")[0])
    stdlib_permitida = {
        "ctypes",
        "hashlib",
        "importlib",
        "json",
        "os",
        "re",
        "subprocess",
        "sys",
        "datetime",
        "pathlib",
        "__future__",
    }
    assert importados <= stdlib_permitida, f"importes fuera de stdlib: {importados - stdlib_permitida}"
    assert "main" not in importados and "modules" not in importados
    assert "spec_from_file_location" in RUTA_RUNNER.read_text(encoding="utf-8")


def test_importar_el_runner_no_carga_selenium_ni_dotenv():
    """El arnes: un proceso limpio que solo importa run_once no debe traer el grafo productivo."""
    sentencia = (
        "import importlib.util,sys;"
        f"espec=importlib.util.spec_from_file_location('r',r'{RUTA_RUNNER}');"
        "m=importlib.util.module_from_spec(espec);espec.loader.exec_module(m);"
        "print(sorted(x for x in sys.modules if x in {'selenium','dotenv','main','yaml','requests'}))"
    )
    salida = subprocess.run(
        [sys.executable, "-c", sentencia], capture_output=True, text=True, cwd=str(RAIZ)
    )
    assert salida.returncode == 0, salida.stderr[-500:]
    cargados = json.loads(salida.stdout.strip().splitlines()[-1])
    assert cargados == [], f"el runner arrastro el grafo productivo: {cargados}"


# ---------------------------------------------------------------------------
# Despues del proceso: preservar antes de analizar (L-VUP-12)
# ---------------------------------------------------------------------------
def test_preservar_resultado_nombra_faltantes_y_clasifica_la_cuarentena(tmp_path):
    corrida = tmp_path / "output" / PLAN
    corrida.mkdir(parents=True)
    (corrida / "acta_revision.json").write_text("{}", encoding="utf-8")
    (corrida / "hotel_don_alfonso_20261006.zip.tmp").write_text("cuarentena", encoding="utf-8")
    documento = run_once.preservar_resultado(
        corrida, tmp_path / "inventario_post_corrida.json"
    )
    assert documento["archivos"] == 2
    estados = {
        Path(e["ruta"]).name: e.get("estado_de_entrega") for e in documento["inventario"]
    }
    assert estados["hotel_don_alfonso_20261006.zip.tmp"] == "CUARENTENA_NO_PUBLICADA", (
        "la cuarentena no es un paquete entregado: O1 no se elude por inventario"
    )
    faltantes = {f["clave"] for f in documento["faltantes_declarados"]}
    assert "v4_complete_report" in faltantes and "pain_ledger" in faltantes
    assert documento["errores"] == []


def test_preservar_resultado_declara_el_directorio_ausente_no_un_cero_mudo(tmp_path):
    documento = run_once.preservar_resultado(
        tmp_path / "no-existe", tmp_path / "inv.json"
    )
    assert documento["archivos"] == 0
    assert any("no existe el directorio" in e for e in documento["errores"])


# ---------------------------------------------------------------------------
# AC12 — H no re-decide la entrega: el par real de E sigue vigente y el enforcement intacto
# ---------------------------------------------------------------------------
def test_el_par_permitir_bloquear_real_no_se_re_implementa_en_H():
    """El par con `DeliveryPackager` y `ActaWriter` reales es de FASE-E: aqui se re-ejecuta, no se copia."""
    ruta = RAIZ / "tests" / "quality_gates" / "tribunal" / "test_fase_e_snapshot_resolvedor.py"
    texto = ruta.read_text(encoding="utf-8")
    for nombre in (
        "test_permitir_publica_y_la_rama_publish_registra_package_evidence",
        "test_bloqueo_suprime_la_cuarentena_y_el_acta_conserva_hash_y_conteo",
        "test_el_veredicto_del_juez_sigue_intacto_con_los_mismos_insumos",
    ):
        assert f"def {nombre}(" in texto, f"el par de AC12 que H reusa ya no esta en {ruta.name}"


def test_los_contratos_de_cuarentena_no_se_movieron_en_esta_fase():
    """write/publish/suppress y el Juez siguen identicos a HEAD: H no toca el enforcement."""
    import subprocess

    for ruta in (
        "modules/delivery/delivery_packager.py",
        "modules/quality_gates/tribunal/judge.py",
        "modules/quality_gates/tribunal/outcome.py",
        "modules/utils/redaction.py",
    ):
        diff = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", "--", ruta],
            capture_output=True,
            text=True,
            cwd=str(RAIZ),
        )
        assert diff.stdout.strip() == "", f"{ruta} cambio en esta fase y su contrato esta congelado"
        assert ruta in run_once.ARCHIVOS_CONGELADOS, (
            f"{ruta} no esta en el inventario que el spawn coteja contra el preflight"
        )


def test_el_spawn_bloqueado_no_llega_al_packager(control):
    """El rechazo del preflight ocurre antes de cualquier consecuencia de entrega."""
    argv = [sys.executable, "-c", HIJO_EXITO]
    pf = {**preflight_favorable(argv), "spawn_autorizado": False}
    with pytest.raises(run_once.PreflightNoFavorable):
        run_once.lanzar_unico(
            control_path=control,
            preflight=pf,
            argv=argv,
            popen=lambda *a, **k: pytest.fail("hubo proceso con preflight en contra"),
        )
    assert not control.exists()


# ---------------------------------------------------------------------------
# b1: la edad se computa contra la emision, no contra el artefacto congelado
# ---------------------------------------------------------------------------
def test_la_edad_del_preflight_no_hereda_la_del_artefacto_offline():
    """Caza el mutante de volver el wiring a `integracion["frescura"]["edad_dias"]`.

    El artefacto de H congelo 76 dias medidos el 2026-10-06. Con esa lectura el techo de
    `EDAD_MAXIMA_DIAS` nunca se alcanzaba: la ventana que `dependencias-fases.md` publica como
    mecanica era decorativa, y un spawn en noviembre seguia viendo 76.
    """
    artefacto = json.loads((DIR_FASE / "integracion_offline.json").read_text(encoding="utf-8"))
    edad_artefacto = artefacto["frescura"]["edad_dias"]

    pf = run_once.preflight(hoy=datetime(2026, 11, 1, tzinfo=timezone.utc))
    frescura = pf["requisitos"]["frescura_fail_closed"]

    assert frescura["edad_dias"] == 102, "2026-07-22 a 2026-11-01 hay 102 dias"
    assert frescura["edad_dias_del_artefacto"] == edad_artefacto, (
        "el valor del artefacto se declara, no se descarta"
    )
    assert frescura["artefacto_vencido"] is True
    assert frescura["cumple"] is False, "102 excede el techo de 90: no se autoriza el spawn"


def test_un_artefacto_vencido_bloquea_el_consentimiento_aunque_el_documento_este_bien():
    """El consentimiento del operador esta en disco y es valido: la edad real lo deja fuera."""
    pf = run_once.preflight(hoy=datetime(2026, 11, 1, tzinfo=timezone.utc))
    consentimiento = pf["requisitos"]["consentimiento_datado_sobre_la_url_viva"]

    assert consentimiento["cumple"] is False
    assert consentimiento["detalle"]["edad_dias"] == 102
    assert "limite declarado de 90" in consentimiento["causa"]
    assert pf["spawn_autorizado"] is False


def test_la_edad_es_aritmetica_contra_la_fecha_de_emision():
    edad = run_once.edad_contra_la_emision
    assert edad("2026-07-22", datetime(2026, 10, 7, tzinfo=timezone.utc)) == 77
    assert edad("2026-07-22", datetime(2026, 10, 20, tzinfo=timezone.utc)) == 90
    assert edad("2026-07-22", datetime(2026, 10, 21, tzinfo=timezone.utc)) == 91


@pytest.mark.parametrize("fecha", ["", None, "22-07-2026", "ayer"])
def test_fecha_de_captura_ilegible_no_produce_edad(fecha):
    """Fail-closed: sin edad computable el requisito no puede dar verde."""
    assert (
        run_once.edad_contra_la_emision(fecha, datetime(2026, 10, 7, tzinfo=timezone.utc)) is None
    )


# ---------------------------------------------------------------------------
# b1-bis: el spawn revalida el reloj, no el documento congelado
# ---------------------------------------------------------------------------
def _guardado_favorable() -> dict:
    return json.loads((DIR_FASE / "preflight.json").read_text(encoding="utf-8"))


def test_la_revalidacion_del_spawn_rechaza_por_edad_aunque_el_guardado_siga_favorable():
    """El diente de b1-bis: el preflight favorable del 6 de octubre no autoriza un spawn en noviembre."""
    guardado = _guardado_favorable()
    assert guardado["spawn_autorizado"] is True, "precondition: el arbol tiene el consentimiento del operador"

    with pytest.raises(run_once.PreflightNoFavorable) as exc:
        run_once.revalidar_contra_la_fecha(guardado, hoy=datetime(2026, 11, 1, tzinfo=timezone.utc))
    cause = str(exc.value)
    assert "102" in cause, "la edad rechazada debe ser la del dia del spawn, no la guardada"
    assert "el preflight guardado declaraba" in cause, (
        "el rechazo tiene que venir del guard de edad; el del consentimiento tambien cae en 102 y la causa"
        " comun no prueba que el primero exista"
    )


def test_la_revalidacion_del_spawn_acepta_el_ultimo_dia_de_la_ventana_y_declara_el_drift():
    guardado = _guardado_favorable()
    dato = run_once.revalidar_contra_la_fecha(
        guardado, hoy=datetime(2026, 10, 20, tzinfo=timezone.utc)
    )
    assert dato["edad_dias"] == 90
    assert dato["techo_de_dias"] == 90
    assert dato["limite_del_consentimiento"] == 90
    assert dato["declarado_por"], "la revalidacion consigna quien autorizo"
    assert "edad_dias_del_preacto" in dato, "la edad del preflight guardado se declara, no se oculta"


def test_la_revalidacion_sin_documento_del_operador_se_niega_antes_de_reservar(tmp_path):
    fase = tmp_path / DIR_FASE.relative_to(RAIZ)
    fase.mkdir(parents=True)
    (fase / "onboarding_provenance.json").write_text(
        (DIR_FASE / "onboarding_provenance.json").read_text(encoding="utf-8"),
        encoding="utf-8",
        newline="\n",
    )
    with pytest.raises(run_once.PreflightNoFavorable) as exc:
        run_once.revalidar_contra_la_fecha(
            {"requisitos": {}}, raiz=tmp_path, hoy=datetime(2026, 10, 7, tzinfo=timezone.utc)
        )
    assert "consentimiento" in str(exc.value).lower()


def test_la_rama_del_spawn_revalida_antes_de_llamar_al_lanzador():
    """El guard no existe si nadie lo dispara: la rama del spawn se goberna por AST, no por lectura de prosa."""
    arbol = ast.parse(RUTA_RUNNER.read_text(encoding="utf-8"))
    main = next(n for n in arbol.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    rama = next(
        (n for n in main.body if isinstance(n, ast.If) and "--spawn" in ast.dump(n.test)), None
    )
    assert rama is not None, "main() perdio su rama --spawn"

    llamadas: list[str] = []
    for sentencia in rama.body:
        for nodo in ast.walk(sentencia):
            if isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name):
                llamadas.append(nodo.func.id)

    assert "revalidar_contra_la_fecha" in llamadas, (
        "el --spawn productivo no revalida la edad ni el consentimiento contra la fecha del dia"
    )
    assert llamadas.index("revalidar_contra_la_fecha") < llamadas.index("lanzar_unico"), (
        "revalidar despues de lanzar no protege la reserva"
    )


# ---------------------------------------------------------------------------
# La reserva productiva sigue virgen
# ---------------------------------------------------------------------------
def test_ningun_test_de_esta_bateria_toco_el_control_productivo():
    assert not CONTROL_PRODUCTIVO.exists(), (
        "FASE-E2E/run_control.json pertenece a la corrida unica: H no puede crearlo"
    )
    assert not (RAIZ / "evidence" / PLAN / "FASE-E2E").exists() or list(
        (RAIZ / "evidence" / PLAN / "FASE-E2E").glob("run_control*")
    ) == []
