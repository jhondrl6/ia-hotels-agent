"""S17 y S18: los escritores de sync/doctor emiten LF, y la fecha del README pasa a tener dueño.

Deudas registradas al cerrar `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` (2026-09-25). Su texto,
dueño y disparador viven en `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/
dependencias-fases.md` §S17 y §S18 (fuente única); este archivo es la cura, no el registro.

- **S17** — `SyncEngine.sync_rule` (`scripts/sync_versions.py`), `run_regenerate_domain_primer` y
  `run_status` (`scripts/doctor.py`) cierran con `write_text(..., encoding="utf-8")` sin
  `newline="\n"`. En un SO que traduce `\n` a `\r\n` eso re-escribe en CRLF archivos que git almacena
  en `i/lf` — medido en el cierre de FASE-RELEASE: 6 archivos `[FAIL] Line endings` y una
  normalización manual por bytes.
- **S18** — la regla `readme_version_header` llegaba hasta la palabra `Actualizado` y dejaba la fecha
  detrás: el sync no la goberna, y su `--check` daba `IN_SYNC` con `README.md` diciendo
  «11 Septiembre 2026» mientras `VERSION.yaml` marcaba `release_date: 2026-09-25`.

Cómo se prueba (y por qué no basta con mirar los bytes):

* Corre el **escritor real** sobre un repositorio temporal, nunca sobre el árbol del proyecto.
* Rojo y verde se comparan **en el mismo entorno** contra la versión **del control**
  (`git show REV_CONTROL_DEFECTUOSO:…`, solo lectura; sin `checkout` ni `stash` que muevan árbol
  ajeno). Si el par old-CRLF / new-LF no se resuelve en bytes, la diferencia la hace el parámetro, no
  la máquina.
* La traducción `\n` → `\r\n` es propiedad del SO: se **mide** (`_traduce_a_crlf()`), no se asume.
  Donde no traduzca, las tres pruebas de bytes se saltan con motivo declarado, en lugar de dar un
  verde que no observó nada. Las de S18 son portables: gobiernan texto, no finales de línea.
* Las huellas salen del observador compartido (`tests/support_observador_escrituras.py`); este archivo
  no define su propia función de huellas.
"""

import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SYNC_SCRIPT = ROOT / "scripts" / "sync_versions.py"
DOCTOR_SCRIPT = ROOT / "scripts" / "doctor.py"
SYNC_CONFIG = ROOT / "scripts" / "sync_config.yaml"
OBSERVADOR = ROOT / "tests" / "support_observador_escrituras.py"
README_REL = "README.md"

# Version de trabajo de los espejos: distinta de la que traen los documentos copiados, para que el
# motor tenga algo que escribir. Un sync que no escribe no prueba nada sobre lo que escribe.
VERSION_ESPEJO = "9.9.9"
CODENAME_ESPEJO = "Espejo temporal de prueba"
FECHA_ESPEJO = "2026-09-25"
FECHA_LARGA_ESPEJO = "25 Septiembre 2026"
FECHA_VIEJA_LEIBLE = "11 Septiembre 2026"   # la que dejó la release en el README real

# Ancla del control negativo. **No puede ser `HEAD`**: al comitear esta cura, HEAD pasa a contener el
# writer corregido y el control se queda sin rojo con el que compararse — medido en `bdd1c4c`, donde
# tres pruebas de este archivo cayeron exactamente por eso (`el control negativo no ejercito el
# defecto`). `5817edd` es el último commit con `write_text(...)` sin `newline="\n"` en sync_versions.py
# (:161) y en doctor.py (:331 y :590), y con la regla `readme_version_header` cortando en «Actualizado»
# (`scripts/sync_config.yaml:38-39`). Verificado con `git show` antes de fijarlo. Mismo patrón que su
# hermana `tests/test_registry_fecha_documental.py:44` (`REV_ESCRITOR_DEFECTUOSO`).
REV_CONTROL_DEFECTUOSO = "5817edd"

# La poblacion que `validate_document_integration.py` corta por finales de linea, mas README y
# VERSION.yaml: son los archivos que estas pruebas NO pueden tocar.
VIGILADOS = [README_REL, "VERSION.yaml", "AGENTS.md", ".cursorrules", "CHANGELOG.md",
             "docs/CONTRIBUTING.md", "docs/GUIA_TECNICA.md", ".agent/knowledge/DOMAIN_PRIMER.md",
             ".agents/workflows/phased_project_executor.md",
             ".agents/workflows/templates/lecciones-capitalizadas-template.md"]


def _traduce_a_crlf() -> bool:
    """Mide si `write_text` sin `newline` convierte los saltos en este SO (no asume Windows)."""
    prueba = Path(tempfile.mkdtemp()) / "prueba.txt"
    prueba.write_text("a\nb\n", encoding="utf-8")
    return b"\r\n" in prueba.read_bytes()


TRADUCE_A_CRLF = _traduce_a_crlf()
SIN_TRADUCCION = pytest.mark.skipif(
    not TRADUCE_A_CRLF,
    reason=("este SO no traduce \\n a \\r\\n al escribir texto: el defecto S17 no es observable aqui, "
            "y un verde de bytes no habria visto nada (el control contra la version commiteada se "
            "salta con el mismo motivo)"))


def _cargar(nombre: str, ruta: Path):
    """Carga fresca bajo nombre unico: un nombre fijo reutilizaria el `sys.modules` ya parcheado."""
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


def _fuente_commiteada(rel: str, tmp_path: Path, rev: str = REV_CONTROL_DEFECTUOSO) -> Path:
    """Materializa `rev:rel` con `git show` (solo lectura) en un temporal.

    Sin fuente el control falla ruidosamente: un instrumento caido no puede leerse como «el defecto ya
    no existe» (R2.9).
    """
    proc = subprocess.run(["git", "show", f"{rev}:{rel}"], capture_output=True, text=True,
                          encoding="utf-8", cwd=str(ROOT))
    assert proc.returncode == 0, (
        f"no se pudo leer {rel} en {rev} (git salio {proc.returncode}: {proc.stderr.strip()}): sin "
        "la fuente del control el control negativo no demuestra nada")
    destino = tmp_path / "commiteado" / Path(rel).name
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(proc.stdout.encode("utf-8"))
    return destino


def _huellas(directorio: Path, archivos) -> dict:
    return _cargar("observador_s17_s18", OBSERVADOR).huellas(
        directorio, archivos=[directorio / a for a in archivos])


def _exigir_rutas_en_temporal(raiz: Path, rutas):
    escapadas = [str(r) for r in rutas
                 if not Path(r).resolve().is_relative_to(raiz.resolve())]
    assert escapadas == [], f"el instrumento escribio fuera del temporal {raiz}: {escapadas}"


# --------------------------------------------------------------------- espejos temporales

def _readme_espejo(tmp_path: Path, *, fecha_leible: str, allanar: bool) -> Path:
    """Copia del README real, preparada para que lo único que escriba el motor sea lo que se prueba.

    Se construye a partir del documento del repo para que el patrón se pruebe contra su forma real, no
    contra una línea inventada en el test. `readme_version_header` goberna **dos** líneas, y segun
    `allanar` se deja una cosa distinta:

    * `allanar=True` (S18): version y codename ya coinciden con el VERSION.yaml del espejo, así que lo
      único desfasado es la fecha. Medido: con solo la cabecera allanada el `FAIL` del control llegaba
      por la segunda sustitución de la regla, no por la fecha.
    * `allanar=False` (S17): quedan la version y el codename reales del repo, que contra el
      VERSION.yaml del espejo obligan al motor a escribir de verdad — un escritor que no escribe no
      puede demostrar qué bytes emite.
    """
    lineas = (ROOT / README_REL).read_text(encoding="utf-8").splitlines()
    tocadas = []
    for i, linea in enumerate(lineas):
        if linea.startswith("**v") and "| Actualizado" in linea:
            if allanar:
                lineas[i] = f"**v{VERSION_ESPEJO}** -- {CODENAME_ESPEJO} | Actualizado {fecha_leible}"
            else:
                version_real, _, fecha_real = linea.partition(" | Actualizado ")
                lineas[i] = f"{version_real} | Actualizado {fecha_leible}"
            tocadas.append("cabecera")
        elif linea.startswith("## Estado del Proyecto (v"):
            if allanar:
                lineas[i] = re.sub(r"\(v[\d.]+ -- [^*]+\)",
                                   f"(v{VERSION_ESPEJO} -- {CODENAME_ESPEJO})", linea)
            tocadas.append("estado")
    assert tocadas == ["cabecera", "estado"], (
        f"el README real ya no tiene las dos lineas que goberna la regla (tocadas: {tocadas}): el "
        "espejo no esta probando contra el documento que se quiere corregir")
    destino = tmp_path / "README-espejo.md"
    destino.write_bytes("\n".join(lineas).encode("utf-8"))
    return destino


def _repo_sync(tmp_path: Path, *, script_src: Path, config_src: Path, readme_src: Path) -> Path:
    """Repositorio temporal con el motor real de sync apuntado a si mismo.

    El README entra por `copyfile` (bytes): re-escribirlo aqui con `write_text` lo pasarfa a CRLF por
    la misma traduccion que se esta midiendo y el experimento naceria falseado.
    """
    raiz = tmp_path / "repo"
    (raiz / "scripts").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(script_src, raiz / "scripts" / "sync_versions.py")
    shutil.copyfile(config_src, raiz / "scripts" / "sync_config.yaml")
    shutil.copyfile(readme_src, raiz / README_REL)
    (raiz / "VERSION.yaml").write_text(
        f'project: "iah-cli (espejo temporal)"\nversion: "{VERSION_ESPEJO}"\n'
        f'codename: "{CODENAME_ESPEJO}"\nrelease_date: "{FECHA_ESPEJO}"\ndate: "{FECHA_ESPEJO}"\n'
        'plan_maestro_version: "v2.6.0"\n', encoding="utf-8")
    return raiz


def _correr_sync(raiz: Path, *, check_only: bool = False):
    """Ejecuta `SyncEngine` sobre el espejo, con las tres rutas del modulo redirigidas al temporal."""
    sync = _cargar(f"sync_{int(check_only)}_{len(_correr_sync.vistos)}", raiz / "scripts" / "sync_versions.py")
    _correr_sync.vistos.append(raiz)
    sync.ROOT_DIR = raiz
    sync.VERSION_FILE = raiz / "VERSION.yaml"
    sync.CONFIG_FILE = raiz / "scripts" / "sync_config.yaml"
    _exigir_rutas_en_temporal(raiz, [sync.ROOT_DIR, sync.VERSION_FILE, sync.CONFIG_FILE])
    engine = sync.SyncEngine(sync.CONFIG_FILE)
    _exigir_rutas_en_temporal(raiz, [raiz / r["file"] for r in engine.config["rules"]])
    return engine.sync_all(check_only=check_only), engine.results


_correr_sync.vistos = []


def _proyecto_doctor(tmp_path: Path, *, script_src: Path) -> tuple[Path, object]:
    """Proyecto temporal minimo con `doctor.py` dentro: PROJECT_ROOT/AGENT_ROOT caen solos."""
    raiz = tmp_path
    (raiz / "scripts").mkdir(parents=True, exist_ok=True)
    (raiz / ".agent" / "knowledge").mkdir(parents=True, exist_ok=True)
    (raiz / "modules").mkdir()
    (raiz / "VERSION.yaml").write_text(
        f'project: "espejo"\nversion: "{VERSION_ESPEJO}"\ncodename: "{CODENAME_ESPEJO}"\n'
        f'release_date: "{FECHA_ESPEJO}"\ndate: "{FECHA_ESPEJO}"\n', encoding="utf-8")
    (raiz / ".agent" / "knowledge" / "DOMAIN_PRIMER.md").write_text("# espejo\n", encoding="utf-8")
    shutil.copyfile(script_src, raiz / "scripts" / "doctor.py")
    return raiz, _cargar(f"doctor_{raiz.name}_{script_src.stat().st_size}",
                         raiz / "scripts" / "doctor.py")


# ------------------------------------------------------------------------- S17: bytes LF

@SIN_TRADUCCION
def test_el_writer_de_sync_emite_lf_y_el_commiteado_escribe_crlf(tmp_path):
    """Verde y rojo del mismo camino: el writer de hoy contra el del control, mismo espejo y entorno.

    El control se lee en `REV_CONTROL_DEFECTUOSO` (no en `HEAD`, que desde `bdd1c4c` ya contiene la
    cura y dejaría el control sin rojo que comparar).
    """
    # allanar=False: deja version/codename reales, asi que el motor tiene que escribir y se ve que emite.
    readme = _readme_espejo(tmp_path, fecha_leible=FECHA_VIEJA_LEIBLE, allanar=False)

    nuevo = _repo_sync(tmp_path / "nuevo", script_src=SYNC_SCRIPT, config_src=SYNC_CONFIG,
                       readme_src=readme)
    _correr_sync(nuevo)
    bytes_nuevo = (nuevo / README_REL).read_bytes()

    control = tmp_path / "control"
    viejo = _repo_sync(tmp_path / "viejo",
                       script_src=_fuente_commiteada("scripts/sync_versions.py", control),
                       config_src=SYNC_CONFIG,
                       readme_src=readme)
    _correr_sync(viejo)
    bytes_viejo = (viejo / README_REL).read_bytes()

    assert b"\r" not in bytes_nuevo, (
        f"sync_versions sigue re-CRLF-eando un archivo que git almacena en LF "
        f"({bytes_nuevo.count(bytes([13]))} CR en {len(bytes_nuevo)} bytes): S17")
    assert bytes_viejo.count(b"\r\n") > 0, (
        "el control negativo no ejercito el defecto: la version commiteada del writer tampoco escribio "
        "CRLF, asi que el verde de arriba no habria observado diferencia real")
    assert bytes_nuevo.replace(b"\n", b"\r\n") == bytes_viejo, (
        "los dos escritores difieren en algo distinto de los finales de linea: el verde dejaria de ser "
        "atribuible al parametro `newline`")


@SIN_TRADUCCION
def test_los_dos_writers_de_doctor_emiten_lf_y_los_de_head_no(tmp_path):
    """`run_regenerate_domain_primer` y `run_status`, ambos sobre un proyecto temporal minimo.

    `run_status` no estaba nombrado en S17: es la tercera escritura de la misma familia dentro del
    mismo archivo, hallada al curar, y se declara en el expediente junto con su prueba.

    El nombre dice «head» porque así se escribió la cura; el control es ahora
    `REV_CONTROL_DEFECTUOSO`. No se renombra: `08b-control-pre-cura.txt` y `10-cura-s17-s18.txt` citan
    esta firma textual.
    """
    control = tmp_path / "c-doctor"
    commiteado = _fuente_commiteada("scripts/doctor.py", control)

    raiz_v, doctor_v = _proyecto_doctor(tmp_path / "d-vigente", script_src=DOCTOR_SCRIPT)
    assert doctor_v.run_regenerate_domain_primer() is True
    assert doctor_v.run_status() is True
    par_v = ((raiz_v / ".agent" / "knowledge" / "DOMAIN_PRIMER.md").read_bytes().count(b"\r\n"),
             (raiz_v / ".agent" / "SYSTEM_STATUS.md").read_bytes().count(b"\r\n"))
    assert par_v == (0, 0), (
        f"doctor.py sigue escribiendo CRLF: DOMAIN_PRIMER {par_v[0]} y SYSTEM_STATUS {par_v[1]} pares "
        "(S17: la cura cubre sus dos escrituras)")

    raiz_c, doctor_c = _proyecto_doctor(tmp_path / "d-control", script_src=commiteado)
    assert doctor_c.run_regenerate_domain_primer() is True
    assert doctor_c.run_status() is True
    par_c = ((raiz_c / ".agent" / "knowledge" / "DOMAIN_PRIMER.md").read_bytes().count(b"\r\n"),
             (raiz_c / ".agent" / "SYSTEM_STATUS.md").read_bytes().count(b"\r\n"))
    assert all(n > 0 for n in par_c), (
        f"el control de doctor no ejercio el defecto (crlf={par_c}): sin ese rojo el verde de arriba "
        "no distingue el parametro del entorno")


def test_los_escritores_no_tocan_el_arbol_del_proyecto(tmp_path):
    """Guard de destino: una corrida de sync en modo escritura no mueve ni un byte del repo real."""
    antes = _huellas(ROOT, VIGILADOS)
    readme = _readme_espejo(tmp_path, fecha_leible=FECHA_VIEJA_LEIBLE, allanar=False)
    raiz = _repo_sync(tmp_path / "guard", script_src=SYNC_SCRIPT, config_src=SYNC_CONFIG,
                      readme_src=readme)
    _correr_sync(raiz)
    _exigir_rutas_en_temporal(raiz, [raiz / README_REL])
    despues = _huellas(ROOT, VIGILADOS)
    assert despues == antes, (
        "algun vigilado del proyecto se movio durante una prueba de sync (contenidos o mtimes): las "
        "rutas del motor no estaban redirigidas y la prueba escribio arbol ajeno")


# ---------------------------------------------------------------------- S18: fecha README

def test_check_detecta_la_fecha_desfasada_y_el_commiteado_no(tmp_path):
    """El corte de cobertura declarado en S18: `[3/11] Version Sync` dio PASS con la fecha vieja."""
    readme = _readme_espejo(tmp_path, fecha_leible=FECHA_VIEJA_LEIBLE, allanar=True)
    control = tmp_path / "r-old"

    vigente = _repo_sync(tmp_path / "r-new", script_src=SYNC_SCRIPT, config_src=SYNC_CONFIG,
                         readme_src=readme)
    ok_vigente, results_vigente = _correr_sync(vigente, check_only=True)

    viejo = _repo_sync(tmp_path / "r-old-repo",
                       script_src=_fuente_commiteada("scripts/sync_versions.py", control),
                       config_src=_fuente_commiteada("scripts/sync_config.yaml", control),
                       readme_src=readme)
    ok_viejo, results_viejo = _correr_sync(viejo, check_only=True)

    assert results_vigente["readme_version_header"] == "FAIL", (
        f"la regla sigue sin gobernar la fecha legible: el check dice "
        f"{results_vigente['readme_version_header']!r} sobre un README con "
        f"«{FECHA_VIEJA_LEIBLE}» y un VERSION.yaml con {FECHA_ESPEJO} (S18)")
    assert results_viejo["readme_version_header"] == "IN_SYNC", (
        "el control no reproduce el hueco: con la config commiteada el check tambien deberia decir "
        f"IN_SYNC, dijo {results_viejo['readme_version_header']!r}")
    assert ok_vigente is False and ok_viejo is True


def test_sync_alinea_la_fecha_en_su_formato_largo_sin_escribir_iso(tmp_path):
    """Escribe la fecha que el README muestra hoy, no un ISO que cambie el formato de la cabecera."""
    readme = _readme_espejo(tmp_path, fecha_leible=FECHA_VIEJA_LEIBLE, allanar=True)
    raiz = _repo_sync(tmp_path / "green", script_src=SYNC_SCRIPT, config_src=SYNC_CONFIG,
                      readme_src=readme)
    _correr_sync(raiz)
    linea = next(l for l in (raiz / README_REL).read_text(encoding="utf-8").splitlines()
                 if l.startswith("**v"))

    assert f"Actualizado {FECHA_LARGA_ESPEJO}" in linea, (
        f"la fecha sincronizada no salio en el formato legible del README: {linea!r}")
    assert FECHA_ESPEJO not in linea, (
        f"la regla nueva metio la fecha ISO ({FECHA_ESPEJO}) en la cabecera: eso cambia el formato que "
        "el documento venia mostrando, y S18 no pide eso")
    assert f"v{VERSION_ESPEJO}" in linea and CODENAME_ESPEJO in linea, (
        f"el ancho del patron se comio la version o el codename: {linea!r}")


def test_repeticion_es_idempotente_y_no_toca_la_segunda_mencion(tmp_path):
    """Segunda corrida: `IN_SYNC` y bytes identicos; una linea de contexto con la misma palabra, intacta."""
    readme = _readme_espejo(tmp_path, fecha_leible=FECHA_VIEJA_LEIBLE, allanar=True)
    lineas = readme.read_text(encoding="utf-8").splitlines()
    for i, linea in enumerate(lineas):
        if linea.startswith("**v"):
            lineas.insert(i + 1, f"Otra nota: | Actualizado {FECHA_VIEJA_LEIBLE} en el cuerpo")
            break
    espejo = tmp_path / "README-decoy.md"
    espejo.write_bytes("\n".join(lineas).encode("utf-8"))

    raiz = _repo_sync(tmp_path / "idem", script_src=SYNC_SCRIPT, config_src=SYNC_CONFIG,
                      readme_src=espejo)
    _correr_sync(raiz)
    primero = (raiz / README_REL).read_bytes()
    _, results2 = _correr_sync(raiz)

    assert results2["readme_version_header"] == "IN_SYNC", (
        f"la segunda sincronizacion sigue queriendo escribir: "
        f"{results2['readme_version_header']!r} (un sync que no es fijo re-numera en cada corrida)")
    assert (raiz / README_REL).read_bytes() == primero
    cuerpo = [l for l in (raiz / README_REL).read_text(encoding="utf-8").splitlines() if "cuerpo" in l]
    assert cuerpo == [f"Otra nota: | Actualizado {FECHA_VIEJA_LEIBLE} en el cuerpo"], (
        f"el patron se paso de la cabecera y alcanzo otra linea: {cuerpo}")


def test_la_regla_sigue_vigente_en_el_config_del_repo():
    """El contrato de la regla, leido en su fuente: un solo escritor para version, codename y fecha."""
    config = yaml.safe_load(SYNC_CONFIG.read_text(encoding="utf-8"))
    regla = next((r for r in config["rules"] if r.get("id") == "readme_version_header"), None)
    assert regla is not None, "readme_version_header desaparecio del config"
    pares = [(r["pattern"], r["template"]) for r in regla["replacements"]
             if "Actualizado" in r.get("template", "")]
    assert len(pares) == 1, f"la fecha de la cabecera tiene {len(pares)} escritores en la misma regla"
    pattern, template = pares[0]
    assert "{date_text}" in template, (
        f"el template vuelve a dejar la fecha sin gobernar ({template!r}): S18 reaparece")
    assert re.search(pattern, f"**v{VERSION_ESPEJO}** -- {CODENAME_ESPEJO} | "
                              f"Actualizado {FECHA_VIEJA_LEIBLE}"), (
        f"el patron no caza la linea real del README con su fecha: {pattern!r}")
