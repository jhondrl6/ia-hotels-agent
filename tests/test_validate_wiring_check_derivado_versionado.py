"""Paso 3: el derivado versionado `.opencode/wiring_report.json` se contra-verifica con `--check`.

QUE SE CURA (parte evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/PREPARACION-DECISION-2026-09-30/
    04-reinvestigacion-alerta-wiring-2026-09-30.md, seccion 5)
    El artefacto esta **versionado** y publica `schema_version 1.0` con `git_sha d7ff932` (del
    2026-09-20), o sea describe un arbol que ya no existe: `archivos_en_alcance 611` contra los 687
    de hoy, y su linea `receptores_no_resueltos_en_produccion = 0` es la garantia que un lector
    razonaria como vigente. Nadie lo corta: el script no tenia `--check` y
    `run_all_validations.py:698` lo invoca **sin** `--write-report`, asi que la cola re-calcula pero
    no publica ni compara. El derivado y la corrida viva pueden divergir indefinidamente (familia de
    S19 / L-VCF-17, con la agravante de que aqui el derivado lleva un contador de seguridad).

QUE ES `--check`
    Regenera el reporte **en memoria** y lo compara contra el artefacto, con los dos campos de
    procedencia neutralizados (`generado`, `git_sha`) al estilo `NORMALIZAR` del escritor de packs:
    la comparacion se hace sobre el texto canonico re-serializado con esos patrones aplicados, asi
    que el orden de claves, el EOL del fichero y la fecha de la corrida no cuentan. Dos arboles
    correctos del mismo commit tienen que dar verde; un numero tocado tiene que dar rojo con nombre
    y ruta.

CODIGOS DEL CLI (el contrato de siempre, mas un rojo que antes no existia)
    0 conforme · 1 hallazgos de cableado o de clausula · 2 error de uso o **lector fallido** (aqui
    entra el artefacto AUSENTE o ILEGIBLE: R2.9, tres estados y no dos con un default) · 3 el
    derivado **DIVERGE** del calculo fresco. Se anade 3 en vez de re-usar 1 porque la cola traduce
    cada codigo con un diagnostico distinto: mezclar «falta una senal» con «el artefacto esta
    vencido» mandaria a quien repara a buscar un caller que no existe.

LO QUE ESTE ARCHIVO NO AFIRMA
    Que el artefacto publicado sea **correcto**, solo que cuadra con el emisor. La autoridad del
    numero la sigue teniendo la clausula del paso 2.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_wiring.py"
RUNNER = ROOT / "scripts" / "run_all_validations.py"

# Revision publicada y fija: la que ya tiene la capa de alcance (abd181c) y el criterio del EXIT
# (paso 2), y TODAVIA NO tiene `--check`. Nunca HEAD.
REV_SIN_CHECK = "5145173"
BANDERA = "--check"

_spec = importlib.util.spec_from_file_location("validate_wiring_check", SCRIPT)
vw = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(vw)


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


def _rev_existe(rev: str) -> bool:
    return subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}"],
        cwd=str(ROOT), capture_output=True,
    ).returncode == 0


def _fuente_versionada(destino: Path, rev: str, rel: str) -> Path:
    proc = subprocess.run(["git", "show", f"{rev}:{rel}"], capture_output=True, text=True,
                          encoding="utf-8", cwd=str(ROOT))
    assert proc.returncode == 0, f"no se pudo leer {rel} en {rev}: {proc.stderr[:200]}"
    ruta = destino / Path(rel).name
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(proc.stdout, encoding="utf-8", newline="\n")
    return ruta


def _correr(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True)


def _mutante(ancla: str, reemplazo: str, tmp_path: Path, nombre: str) -> Path:
    """Mutante anclado a un ancla **unica**, verificado con `ast.parse` antes de fiarse de el."""
    fuente = SCRIPT.read_text(encoding="utf-8")
    assert fuente.count(ancla) == 1, (
        f"el ancla del mutante aparece {fuente.count(ancla)} veces en el script: la cura cambio de "
        "forma y el mutante no apaga lo que se cree que apaga")
    mutado = fuente.replace(ancla, reemplazo, 1)
    assert mutado != fuente and reemplazo in mutado
    ast.parse(mutado)
    copia = tmp_path / f"validate_wiring_{nombre}.py"
    copia.write_text(mutado, encoding="utf-8", newline="\n")
    return copia


@pytest.fixture(scope="module")
def arbol_y_derivado(tmp_path_factory):
    """Un arbol pequeno, su derivado escrito por el writer real, y la ruta donde vive.

    Se publica con `publicar()` (no a mano): si el writer dejara de emitir un campo, el contraste
    tiene que verlo. El arbol lleva un caller gobernado conforme para que la poblacion no este vacia.
    """
    base = tmp_path_factory.mktemp("derivado")
    (base / "modules").mkdir(parents=True, exist_ok=True)
    (base / "modules" / "productores.py").write_text(
        "class PainSolutionMapper:\n"
        "    def detect_pains(self, a, s, x, whatsapp_html_detected=False):\n"
        "        return []\n\n\n"
        "class CoherenceValidator:\n"
        "    def validate(self, d, p, a, s, whatsapp_html_detected=False):\n"
        "        return None\n\n\n"
        "class AssessmentBuilder:\n"
        "    def with_validation(self, validation_summary):\n"
        "        return self\n\n\n"
        "class V4ProposalGenerator:\n"
        "    def _generate_dynamic_services_table(self, site_presence_report=None,\n"
        "                                         whatsapp_conflict=False):\n"
        '        return ""\n',
        encoding="utf-8", newline="\n")
    (base / "modules" / "conforme.py").write_text(
        "from .productores import PainSolutionMapper\n"
        "mapper = PainSolutionMapper()\n"
        "mapper.detect_pains(a, s, x, whatsapp_html_detected=html)\n",
        encoding="utf-8", newline="\n")
    destino = base / "wiring_report.json"
    # Sin `--ignore-known`: el campo `modo_excepciones` forma parte del artefacto, y un fixture que
    # publicara en un modo y comparara en otro daria DIVERGE por la bandera, no por el contenido.
    reporte = vw.construir_reporte(base)
    vw.publicar(reporte, destino)
    return base, destino


# --------------------------------------------------------------- el verde sobre el arbol real


def test_el_derivado_versionado_del_repo_pasa_su_propio_check():
    """El estado que la orden deja como condicion de cierre: el artefacto publicado cuadra.

    Antes de la cura este CLI ni siquiera conocia la bandera y salia 2 por argparse; con el
    artefacto del 2026-09-20 todavia en disco tiene que salir 3.
    """
    corrido = _correr(BANDERA)
    assert corrido.returncode == 0, (
        f"EXIT {corrido.returncode}\n{corrido.stdout}\n{corrido.stderr}")
    assert "derivado" in corrido.stdout.lower(), corrido.stdout


def test_la_clausula_roja_manda_sobre_el_check_del_derivado(tmp_path):
    """Orden de la salida: un EXIT 1 de cableado no se puede disfrazar de 3, ni al reves.

    El arbol tiene un hueco de produccion (rojo del paso 2) y un derivado expreso y correcto de ese
    mismo arbol. Si el `--check` se evaluara primero, la cola diria «el artefacto esta vencido» y
    quien repareiria mirando el JSON un defecto que esta en el codigo.
    """
    base = tmp_path / "roto-y-derivado"
    (base / "modules").mkdir(parents=True)
    (base / "modules" / "productores.py").write_text(
        "class PainSolutionMapper:\n"
        "    def detect_pains(self, a, s, x, whatsapp_html_detected=False):\n        return []\n\n"
        "class CoherenceValidator:\n"
        "    def validate(self, d, p, a, s, whatsapp_html_detected=False):\n        return None\n\n"
        "class AssessmentBuilder:\n"
        "    def with_validation(self, validation_summary):\n        return self\n\n"
        "class V4ProposalGenerator:\n"
        "    def _generate_dynamic_services_table(self, site_presence_report=None,\n"
        "                                         whatsapp_conflict=False):\n        return ''\n",
        encoding="utf-8", newline="\n")
    (base / "modules" / "ajeno.py").write_text(
        "def correr(cosa):\n    return cosa.detect_pains(a, s, x)\n",
        encoding="utf-8", newline="\n")
    destino = base / "wiring_report.json"
    vw.publicar(vw.construir_reporte(base, ignore_known=True), destino)

    corrido = _correr("--root", str(base), BANDERA, str(destino))
    assert corrido.returncode == 1, corrido.stdout
    assert "HUECO_DE_COBERTURA_EN_PRODUCCION" in corrido.stdout
    assert "DIVERGE" not in corrido.stdout


# ----------------------------------------------------------- el divergir, con nombre y ruta


def test_un_derivado_tocado_a_mano_deja_de_ser_verde(arbol_y_derivado):
    """El diente central: la cola tenia que poder decir «el artefacto publicado esta vencido».

    Se parten **tres** poblaciones distintas del mismo artefacto, porque una sola prueba de
    divergence podria pasar por una comparacion que solo mira un rincon: un escalar de `cobertura`,
    un elemento de `poblacion` y una clave que el emisor ya no produce.
    """
    _base, destino = arbol_y_derivado
    intacto = json.loads(destino.read_text(encoding="utf-8"))
    assert _correr("--root", str(_base), BANDERA, str(destino)).returncode == 0

    for mutacion, senal in (
        ({"cobertura.archivos_en_alcance": 999999}, "cobertura.archivos_en_alcance"),
        ({"poblacion.0.kwargs_presentes": ["TOCADO"]}, "poblacion"),
    ):
        datos = json.loads(json.dumps(intacto))
        ruta, valor = next(iter(mutacion.items()))
        _escribir_en(datos, ruta, valor)
        destino.write_text(json.dumps(datos, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                           encoding="utf-8")
        corrido = _correr("--root", str(_base), BANDERA, str(destino))
        assert corrido.returncode == 3, f"{ruta}: EXIT {corrido.returncode}\n{corrido.stdout}"
        assert senal in corrido.stdout, (
            f"{ruta}: el rojo no nombra la ruta divergente: {corrido.stdout}")
        assert "DIVERGE" in corrido.stdout

    # Una clave que el emisor actual ya no publica (el caso del 1.0 -> 1.1).
    datos = json.loads(json.dumps(intacto))
    del datos["excluidos_por_declaracion_git"]
    destino.write_text(json.dumps(datos, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                       encoding="utf-8")
    corrido = _correr("--root", str(_base), BANDERA, str(destino))
    assert corrido.returncode == 3, corrido.stdout
    assert "excluidos_por_declaracion_git" in corrido.stdout

    destino.write_text(json.dumps(intacto, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                       encoding="utf-8")


def test_los_dos_campos_de_procedencia_no_rompen_el_check(arbol_y_derivado):
    """`generado` y `git_sha` son volatiles a proposito: se normalizan, no se pinean.

    Se afirma ademas que los dos textos **crudos** si difieren: sin la normalizacion el check seria
    un rojo en cada corrida, que es la otra forma de no gobernar nada. Y el digest del artefacto con
    fecha y sha distintos tiene que ser identico al del original.
    """
    _base, destino = arbol_y_derivado
    intacto = json.loads(destino.read_text(encoding="utf-8"))
    crudo_original = json.dumps(intacto, indent=2, ensure_ascii=False, sort_keys=True)

    otros = json.loads(json.dumps(intacto))
    otros["generado"] = "2001-01-01T00:00:00+00:00"
    otros["git_sha"] = "0000000"
    crudo_otros = json.dumps(otros, indent=2, ensure_ascii=False, sort_keys=True)

    assert crudo_original != crudo_otros, (
        "premissa: los dos textos crudo si difieren, si no la normalizacion no esta probando nada")
    digest_a = hashlib.sha256(vw._normalizado(crudo_original).encode("utf-8")).hexdigest()
    digest_b = hashlib.sha256(vw._normalizado(crudo_otros).encode("utf-8")).hexdigest()
    assert digest_a == digest_b, "NORMALIZAR no neutraliza los dos campos de procedencia"

    destino.write_text(crudo_otros + "\n", encoding="utf-8")
    assert _correr("--root", str(_base), BANDERA, str(destino)).returncode == 0
    destino.write_text(crudo_original + "\n", encoding="utf-8")


def test_un_arbol_con_crlf_en_el_derivado_siguiendo_conforme(arbol_y_derivado):
    """Trampa medida del repo (S20): el writer emite CRLF en Windows y el blob viaja en LF.

    La comparacion es sobre el objeto re-serializado canonico, asi que el final de linea del fichero
    en disco no puede convertir un conforme en divergente.
    """
    _base, destino = arbol_y_derivado
    crudo = destino.read_text(encoding="utf-8")
    destino.write_bytes(crudo.replace("\n", "\r\n").encode("utf-8"))
    try:
        assert _correr("--root", str(_base), BANDERA, str(destino)).returncode == 0
    finally:
        destino.write_text(crudo, encoding="utf-8")


# ------------------------------------------------------------------- los otros estados del lector


def test_derivado_ausente_o_ilegible_no_es_verde(arbol_y_derivado, tmp_path):
    """R2.9: ausente, ilegible y conforme son tres estados, y los dos rojos se publican distintos.

    Un artefacto que no se puede leer no puede reportarse como «sin divergencias»: ese era el hueco
    que dejo al derivado vencido sin instrumento que lo cortara.
    """
    _base, destino = arbol_y_derivado
    fantasma = tmp_path / "no-existe.json"

    ausente = _correr("--root", str(_base), BANDERA, str(fantasma))
    assert ausente.returncode == 2, ausente.stdout
    assert "AUSENTE" in ausente.stdout, ausente.stdout

    crudo = destino.read_text(encoding="utf-8")
    destino.write_text("{ esto no es json", encoding="utf-8")
    try:
        ilegible = _correr("--root", str(_base), BANDERA, str(destino))
        assert ilegible.returncode == 2, ilegible.stdout
        assert "ILEGIBLE" in ilegible.stdout, ilegible.stdout
        assert "AUSENTE" not in ilegible.stdout, (
            "los dos estados del lector se imprimen con la misma palabra")
    finally:
        destino.write_text(crudo, encoding="utf-8")


# ------------------------------------------------------------------------- la cola de validaciones


@pytest.fixture(scope="module")
def runner():
    return _cargar("run_all_validations_wiring_check", RUNNER)


def test_la_cola_invoca_al_verificador_con_la_bandera_de_check(runner):
    """S32 en miniatura: una cola que re-calcula sin comparar no corta el derivado vencido.

    Se lee el argumento con el que el runner invoca al script, no solo que lo invoca: sin la bandera
    la cola seguia recalculando y tirando el resultado, que es exactamente el defecto de la seccion 5.
    """
    fuente = RUNNER.read_text(encoding="utf-8")
    bloque = fuente[fuente.index("def _check_wiring"):fuente.index("def _check_governance_numbers")]
    assert f'str(script_path), "{BANDERA}"' in bloque, (
        "la cola volvio a invocar al verificador sin `--check`: el derivado vuelve a poder "
        "divergir indefinidamente")


def test_el_exit_3_de_la_cola_es_rojo_con_nombre_propio(runner, monkeypatch):
    """Y la cola traduce el codigo nuevo: 3 no es verde ni LECTOR-FALLIDO.

    Se ejercita el metodo real del runner con `_run_command` sustituido, asi que el verde sale del
    codigo cableado y no de una lectura del texto fuente.
    """
    for exit_code, esperado_pass, senal in (
        (0, True, "1 llamadas"),
        (3, False, "vencido"),
        (2, False, "no pudo medir"),
        (1, False, "divergente"),
    ):
        instancia = runner.ValidationRunner(quick=True, verbose=False)
        monkeypatch.setattr(instancia, "_run_command",
                            lambda *a, **k: (exit_code, "[OK] Wiring: 1 llamadas | derivado conforme"))
        instancia._check_wiring()
        resultado = instancia.results[-1]
        assert resultado.passed is esperado_pass, f"EXIT {exit_code} -> {resultado.passed}"
        assert resultado.name == "Wiring"
        texto = " ".join([resultado.message] + list(resultado.details))
        assert senal in texto, f"EXIT {exit_code} se divulga como {texto!r}"


def test_la_bandera_check_no_se_cuenta_como_arbol_inexistente(tmp_path):
    """`--root` inexistente sigue siendo 2 aunque se pida `--check`: el orden del uso no se invierte."""
    corrido = _correr("--root", str(tmp_path / "no-existe"), BANDERA)
    assert corrido.returncode == 2
    assert "no existe el arbol" in corrido.stdout


# ---------------------------------------------------------------- control negativo y dientes


def test_control_negativo_el_instrumento_versionado_de_5145173_no_puede_comparar(tmp_path):
    """El instrumento de la revision anclada, ejecutado: no conoce la bandera.

    La premissa se comprueba en la fuente leida con `git show` (tiene la capa de alcance y el
    criterio del paso 2, no tiene `--check`) y despues se **ejecuta** la copia versionada contra el
    mismo arbol que al curado lo da rojo. Si la inhabilidad la describiera solo este test, no
    probaria nada.
    """
    assert _rev_existe(REV_SIN_CHECK), f"la revision {REV_SIN_CHECK} no esta en el repo"
    viejo = _fuente_versionada(tmp_path / "instrumento-viejo", REV_SIN_CHECK,
                               "scripts/validate_wiring.py")
    fuente = viejo.read_text(encoding="utf-8")
    assert "--exclude-" + "standard" in fuente, (
        f"{REV_SIN_CHECK} ya no tiene la capa de alcance: la revision anclada no es la del paso 1")
    assert "HUECO_DE_COBERTURA_EN_PRODUCCION" in fuente, (
        f"{REV_SIN_CHECK} ya no tiene el criterio del paso 2: la revision anclada no es la anterior "
        "a esta cura")
    assert f'"{BANDERA}"' not in fuente and "--check" not in fuente.replace("--check-manual", ""), (
        f"{REV_SIN_CHECK} ya implementa `--check`: el control dejo de ser anterior a la cura")

    base = tmp_path / "arbol-control"
    base.mkdir()
    (base / "x.py").write_text("y = 1\n", encoding="utf-8")
    viejo_corrido = subprocess.run([sys.executable, str(viejo), BANDERA, "--root", str(base)],
                                   capture_output=True, text=True)
    assert viejo_corrido.returncode == 2, viejo_corrido.stdout + viejo_corrido.stderr
    assert "unrecognized arguments" in (viejo_corrido.stderr + viejo_corrido.stdout)

    curado = _correr(BANDERA, str(tmp_path / "sin-derivado.json"), "--root", str(ROOT))
    assert curado.returncode == 2, (
        f"EXIT {curado.returncode}: el curado tenia que dar AUSENTE sobre un derivado que no esta, "
        f"no un verde ni un rojo de cableado\n{curado.stdout}")
    assert "AUSENTE" in curado.stdout, curado.stdout


def test_dientes_un_mutante_por_cada_rama_del_check(tmp_path):
    """Los dos dientes del `--check`, cada uno con su caida nombrada.

    Mutante 1 apaga la normalizacion de los campos de procedencia: el check pasa a ser un rojo
    permanente, que es la otra manera de no gobernar nada. Mutante 2 apaga la divergencia: el check
    vuelve al estado de hoy (verdero sin mirar). Ninguno de los dos se comprueba leyendo la fuente:
    se **ejecutan** contra el mismo artefacto.
    """
    base = tmp_path / "mutantes"
    base.mkdir()
    (base / "modules").mkdir()
    (base / "modules" / "a.py").write_text(
        "class PainSolutionMapper:\n"
        "    def detect_pains(self, a, s, x, whatsapp_html_detected=False):\n        return []\n\n"
        "class CoherenceValidator:\n"
        "    def validate(self, d, p, a, s, whatsapp_html_detected=False):\n        return None\n\n"
        "class AssessmentBuilder:\n"
        "    def with_validation(self, validation_summary):\n        return self\n\n"
        "class V4ProposalGenerator:\n"
        "    def _generate_dynamic_services_table(self, site_presence_report=None,\n"
        "                                         whatsapp_conflict=False):\n        return ''\n"
        "\n\nfrom .a import PainSolutionMapper\nmapper = PainSolutionMapper()\n"
        "mapper.detect_pains(a, s, x, whatsapp_html_detected=html)\n",
        encoding="utf-8", newline="\n")
    destino = base / "wiring_report.json"
    vw.publicar(vw.construir_reporte(base, ignore_known=True), destino)
    # Se le corre la fecha al artefacto: es el caso real (publicado ayer, calculado hoy). Sin este
    # desplazamiento las dos corridas pueden caer en el MISMO segundo y el mutante 1 daria CONFORME
    # por suerte, no por logica -- un diente que muerde a veces no es un diente.
    diferido = json.loads(destino.read_text(encoding="utf-8"))
    diferido["generado"] = "2001-01-01T00:00:00+00:00"
    destino.write_text(json.dumps(diferido, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                       encoding="utf-8")
    intacto = destino.read_text(encoding="utf-8")

    # Mutante 1: sin normalizar, la fecha del calculo fresco choca con la publicada y el check se
    # vuelve un rojo permanente: la otra forma de no gobernar nada.
    sin_normalizar = _mutante(
        "return json.loads(_normalizado(texto_canonico(",
        "return json.loads(texto_canonico((  # MUTADO-SIN-NORMALIZAR",
        tmp_path, "sin_normalizar")
    mod1 = _cargar("vw_mutado_sin_normalizar", sin_normalizar)
    fresco = mod1.construir_reporte(base, ignore_known=True)
    estado1, lineas1, _ = mod1.comparar_derivado(destino, fresco)
    assert estado1 == mod1.ESTADO_DIVERGE, (
        f"el mutante 1 dio {estado1}: sin normalizar el check deberia divergir siempre")
    assert any("generado" in l or "git_sha" in l for l in lineas1), lineas1
    assert vw.comparar_derivado(destino, vw.construir_reporte(base, ignore_known=True))[0] == \
        vw.ESTADO_CONFORME, "el instrumento curado no da conforme sobre el mismo par: el fixture esta roto"

    # Mutante 2: la divergencia se calcula y se tira.
    ciega = _mutante(
        "divergencias = _divergencias(leido, reporte, rutas_procedencia=rutas)",
        "divergencias = []  # MUTADO-CIEGO",
        tmp_path, "ciega")
    mod2 = _cargar("vw_mutado_ciega", ciega)
    tocado = json.loads(intacto)
    _escribir_en(tocado, "cobertura.archivos_en_alcance", 424242)
    destino.write_text(json.dumps(tocado, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                       encoding="utf-8")
    try:
        estado2, _lineas2, _ = mod2.comparar_derivado(
            destino, mod2.construir_reporte(base, ignore_known=True))
        assert estado2 == mod2.ESTADO_CONFORME, (
            f"el mutante 2 dio {estado2}: apagar la divergencia no deberia dejar el check verde")
        assert vw.comparar_derivado(
            destino, vw.construir_reporte(base, ignore_known=True))[0] == vw.ESTADO_DIVERGE
    finally:
        destino.write_text(intacto, encoding="utf-8")


# ----------------------------------------------------------------------------------- utilidades
# (a nivel de modulo: los fixtures de pytest no pueden devolver funciones locales no picklable)


def _escribir_en(obj: object, ruta: str, valor) -> None:
    """Escribe `a.b.0.c` dentro de un objeto JSON ya parseado."""
    partes = ruta.split(".")
    actual = obj
    for parte in partes[:-1]:
        if isinstance(actual, list):
            actual = actual[int(parte)]
        else:
            actual = actual[parte]
    ultima = partes[-1]
    if isinstance(actual, list):
        actual[int(ultima)] = valor
    else:
        actual[ultima] = valor
