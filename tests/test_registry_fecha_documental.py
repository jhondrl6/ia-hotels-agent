"""Fecha de REGISTRY: un unico escritor, con la interaccion real medida.

Cubre el tramo de fecha de REGISTRY del bloque B de
`ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` y su continuacion correctiva (§3 del mandato de
remediacion). La cabecera "> **Ultima actualizacion:**" de REGISTRY.md la produce solo
`log_phase_completion.py` (el dia que se registra una fase) y ya NO la re-escribe `sync_versions.py`
con la fecha de release anclada en VERSION.yaml. Antes habia dos escritores con semantica distinta,
y al dia siguiente de loguear una fase el `sync_versions --check` marcaba FAIL contra una fecha de
entrada correcta — el conflicto repetido.

Por que este archivo se reescribio: la version que dejo el cierre retirado probaba la **estructura**
(`sync_config.yaml` ya no tiene regla sobre REGISTRY) y lamia el `SyncEngine` en modo `--check`, que
no escribe por diseño. No ejercitaba lo que el mandato pide: registrar → **sincronizar en modo
escritura** → verificar, sobre el MISMO expediente, con todas las rutas redirigidas a un repositorio
temporal coherente con los consumidores reales (incluido `VERSION.yaml`), con la configuracion real de
sincronizacion, con fechas de release distintas de la de entrada, con cambio de dia, con repeticion de
ambos comandos y con su control negativo. Y el escritor publicaba garantias que no ejecuto.

Las aserciones de ausencias de escritura comparan contenido, metadatos y **operaciones observadas**
(`tests/support_observador_escrituras.py`, el mismo observador que usa S13): bytes identicos no
prueban que nadie abrio el archivo.
"""

import importlib.util
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SYNC_CONFIG = ROOT / "scripts" / "sync_config.yaml"
SYNC_SCRIPT = ROOT / "scripts" / "sync_versions.py"
REGISTRY = ROOT / "docs" / "contributing" / "REGISTRY.md"
LPC = ROOT / "scripts" / "log_phase_completion.py"
REGISTRY_REL = "docs/contributing/REGISTRY.md"
OBSERVADOR = ROOT / "tests" / "support_observador_escrituras.py"
# Commiteado ANTES de todo el bloque B: es el escritor permisivo real, no una parodia dentro del test.
REV_ESCRITOR_DEFECTUOSO = "da382b1"

# Los consumidores reales que la configuracion vigente si toca. Se copian al repositorio temporal
# para que «sincronizar en modo escritura» sea un camino real, no un vacio.
CONSUMIDORES_VERSIONADOS = ["README.md", "AGENTS.md", ".cursorrules",
                            "docs/CONTRIBUTING.md", "docs/GUIA_TECNICA.md"]

FECHA_RELEASE = "2026-09-19"        # igual que VERSION.yaml vigente: NO es el dia de la entrada
NUEVA_FECHA_RELEASE = "2026-09-20"  # release publicada despues del registro: lo que sync difunde
NUEVA_VERSION = "4.78.0"
DIA_1 = "2026-09-23"
DIA_2 = "2026-09-24"
CABECERA = "> **Ultima actualizacion:**"

# La autoridad competidora, tal y como estaba en `scripts/sync_config.yaml` antes de retirarla
# (leida con `git show HEAD~:…` en la remediacion). Solo se restituye en COPIAS temporales.
REGLA_COMPETIDORA = """
  - id: "registry_last_update"
    file: "docs/contributing/REGISTRY.md"
    description: "Last update timestamp in registry"
    replacements:
      - pattern: '> \\*\\*Ultima actualizacion:\\*\\*\\s*[\\d-]+'
        template: '> **Ultima actualizacion:** {date}'
"""


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


def _fuente_versionada(tmp_path: Path, rev: str, rel: str) -> Path:
    """Materializa `rev:rel` con `git show` (solo lectura) en un temporal: no hay `checkout` ni
    `stash` que puedan mover el arbol ajeno. Sin fuente, el control falla ruidosamente: un
    instrumento caido no puede leerse como «el defecto ya no existe» (R2.9)."""
    proc = subprocess.run(["git", "show", f"{rev}:{rel}"], capture_output=True, text=True,
                          encoding="utf-8", cwd=str(ROOT))
    assert proc.returncode == 0, (
        f"no se pudo leer {rel} en {rev} (git salio {proc.returncode}: {proc.stderr.strip()}): sin "
        "fuente versionada el control negativo no demuestra nada")
    destino = tmp_path / "instrumento" / Path(rel).name
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(proc.stdout, encoding="utf-8")
    return destino


def _observador():
    return _cargar("observador_escrituras_registry", OBSERVADOR)


def _huella(path: Path):
    """Contenido + metadatos: la pareja que delata la re-escritura de bytes identicos."""
    obs = _observador()
    return obs.huellas(path.parent)[path.as_posix()]


# --------------------------------------------------------------------- (0) estructura

def test_sync_config_no_tiene_regla_sobre_registry():
    config = yaml.safe_load(SYNC_CONFIG.read_text(encoding="utf-8"))
    files = [rule.get("file", "") for rule in config.get("rules", [])]
    registry_rules = [f for f in files if Path(f).name == "REGISTRY.md"]
    assert registry_rules == [], (
        f"sync_versions vuelve a aduenarse de la fecha de REGISTRY ({registry_rules}): habria dos "
        "escritores y reaparece el conflicto de fechas")


def test_ya_no_existe_la_regla_registry_last_update():
    config = yaml.safe_load(SYNC_CONFIG.read_text(encoding="utf-8"))
    ids = {rule.get("id") for rule in config.get("rules", [])}
    assert "registry_last_update" not in ids


# ----------------------------------------------------------------- (1) repositorio temporal

class Expediente:
    """Repo temporal coherente con los consumidores reales + los dos instrumentos redirigidos."""

    def __init__(self, tmp_path: Path, *, config_src: Path = None):
        self.rai = tmp_path / "repo"
        self.escrituras = []
        self._crear(config_src or SYNC_CONFIG)

    def _crear(self, config_src: Path):
        import shutil
        (self.rai / "scripts").mkdir(parents=True, exist_ok=True)
        (self.rai / "docs" / "contributing").mkdir(parents=True, exist_ok=True)
        (self.rai / "VERSION.yaml").write_text(
            "project: \"iah-cli (expediente temporal)\"\n"
            "version: \"4.77.3\"\n"
            "codename: \"LLMReport honesto cuando ningún provider responde\"\n"
            f"release_date: \"{FECHA_RELEASE}\"\n"
            f"date: \"{FECHA_RELEASE}\"\n"
            "plan_maestro_version: \"v2.6.0\"\n", encoding="utf-8")
        shutil.copyfile(config_src, self.rai / "scripts" / "sync_config.yaml")
        for rel in CONSUMIDORES_VERSIONADOS:
            origen = ROOT / rel
            if not origen.exists():
                continue
            destino = self.rai / rel
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(origen.read_bytes())
        self.registry = self.rai / "docs" / "contributing" / "REGISTRY.md"
        self.registry.write_text(
            "# Registro de Fases\n\n"
            f"{CABECERA} 2020-01-01\n"
            "> **Total fases completadas:** 1\n\n---\n\n"
            "## FASE-ANterior - 2020-01-01\n\n**Descripcion:** entrada ya cerrada, no se toca\n\n"
            "---\n\n## Formato\n\nnada\n", encoding="utf-8")
        self.tracker = self.rai / "docs" / "contributing" / ".last_doc_phase.json"
        self.config = self.rai / "scripts" / "sync_config.yaml"

    def registrar(self, fase: str, dia: str, *, tests: str = "", coherence=None,
                  escritor: Path = None):
        """Corre el ESCRITOR REAL (`main()` de log_phase_completion) sobre este expediente.

        Con `escritor=` se le pasa otra versi&oacute;n del archivo (p. ej. la commiteada antes de B)
        para que un control negativo ejercite al instrumento defectuoso real, no una parodia escrita
        dentro de la prueba. Las aperturas de escritura del propio registro quedan observadas en
        `self.escrituras`.
        """
        lpc = _cargar(f"lpc_reg_{dia}_{fase}_{escritor or 'vigente'}", escritor or LPC)
        lpc.ROOT_DIR = self.rai
        lpc.CONTRIBUTING_FILE = self.rai / "docs" / "CONTRIBUTING.md"
        lpc.DOCS_CONTRIBUTING_DIR = self.rai / "docs" / "contributing"
        lpc.REGISTRY_FILE = self.registry
        lpc.LAST_DOC_TRACKER = self.tracker
        _exigir_rutas_en_temporal(self.rai, [
            lpc.ROOT_DIR, lpc.CONTRIBUTING_FILE, lpc.DOCS_CONTRIBUTING_DIR,
            lpc.REGISTRY_FILE, lpc.LAST_DOC_TRACKER,
        ])
        lpc.datetime = _dia_fijo(dia)
        argv = ["log_phase_completion.py", "--fase", fase, "--desc", "registro de prueba",
                "--archivos-mod", "modules/ejemplo.py"]
        if tests:
            argv += ["--tests", tests]
        if coherence is not None:
            argv += ["--coherence", str(coherence)]
        argv_orig, sys.argv = sys.argv, argv
        obs = _observador()
        try:
            with obs.observador_de_escrituras() as registro:
                rc = lpc.main()
            self.escrituras = [(op, r) for op, r, _ in registro.operaciones]
            _exigir_rutas_en_temporal(self.rai, [r for _, r in self.escrituras])
        finally:
            sys.argv = argv_orig
        return rc, lpc

    def sincronizar(self, *, check_only: bool = False):
        """Corre el motor REAL de sincronizacion sobre este expediente, con la config real."""
        sync = _cargar(f"sync_reg_{int(check_only)}_{id(self)}", SYNC_SCRIPT)
        sync.ROOT_DIR = self.rai
        sync.VERSION_FILE = self.rai / "VERSION.yaml"
        sync.CONFIG_FILE = self.config
        _exigir_rutas_en_temporal(self.rai, [
            sync.ROOT_DIR, sync.VERSION_FILE, sync.CONFIG_FILE,
        ])
        with _observador().observador_de_escrituras() as registro:
            engine = sync.SyncEngine(sync.CONFIG_FILE)
            _exigir_rutas_en_temporal(self.rai, [
                sync.ROOT_DIR / rule["file"] for rule in engine.config["rules"]
            ])
            ok = engine.sync_all(check_only=check_only)
        escrituras = [(op, r) for op, r, _ in registro.operaciones]
        _exigir_rutas_en_temporal(self.rai, [r for _, r in escrituras])
        return ok, engine.results, escrituras

    def publicar_nueva_release(self, fecha: str, version: str) -> None:
        """VERSION.yaml del expediente pasa a una release posterior: es lo que sync propaga a los
        encabezados versionados y lo que hace que «modo escritura» escriba de verdad. Sin esto, un
        copia-ya-sincronizada dara un verde vacio."""
        yaml_path = self.rai / "VERSION.yaml"
        texto = yaml_path.read_text(encoding="utf-8")
        texto = re.sub(r'release_date: "\d{4}-\d{2}-\d{2}"', f'release_date: "{fecha}"', texto)
        texto = re.sub(r'(?m)^date: "\d{4}-\d{2}-\d{2}"', f'date: "{fecha}"', texto)
        texto = re.sub(r'(?m)^version: "[\d.]+"', f'version: "{version}"', texto)
        yaml_path.write_text(texto, encoding="utf-8")

    def fecha_cabecera(self) -> str:
        for linea in self.registry.read_text(encoding="utf-8").splitlines():
            if linea.startswith(CABECERA):
                return linea.split(CABECERA)[1].strip()
        raise AssertionError(f"no hay cabecera de fecha en {self.registry}")

    def cabeceras(self) -> int:
        return self.registry.read_text(encoding="utf-8").count(CABECERA)

    def entradas(self, fase: str) -> int:
        return self.registry.read_text(encoding="utf-8").count(f"## {fase} - ")

    def texto(self) -> str:
        return self.registry.read_text(encoding="utf-8")


def _dia_fijo(iso: str):
    """Sustituto de `datetime` con `now()` anclado: el mandato exige probar el cambio de dia."""
    ancla = datetime.fromisoformat(f"{iso}T12:00:00")

    class _Datetime:
        @classmethod
        def now(cls, tz=None):
            return ancla

        @classmethod
        def strptime(cls, *a, **k):
            return datetime.strptime(*a, **k)

    return _Datetime


def _dentro(ruta: str, raiz: Path) -> bool:
    try:
        p = Path(ruta).resolve()
        r = raiz.resolve()
    except OSError:
        return False
    return p == r or r in p.parents


def _exigir_rutas_en_temporal(raiz: Path, rutas):
    escapadas = [str(ruta) for ruta in rutas if not _dentro(ruta, raiz)]
    assert escapadas == [], (
        f"rutas fuera del mismo temporal {raiz.as_posix()}: {escapadas}")


# ------------------------------------------------- (2) interaccion real: registrar → sync escribe

def _interaccion(espejo: Expediente) -> dict:
    """El trabajo completo que el mandato pide, en un solo lugar para poder repetirlo.

    Devuelve el estado observado; **no** afirma nada. La afirmacion vive en `_exigir_interaccion`,
    que usan por igual la prueba positiva y el control negativo: asi el rojo del control viene de la
    MISMA exigencia, no de una configuracion rota.

    Secuencia: registrar (escritor real, dia 1) → publicar una release nueva en VERSION.yaml →
    sincronizar en **modo escritura** → verificar con `--check` → repetir el `--check`.
    """
    observador = _observador()

    huella_antes = _huella(espejo.registry) if espejo.registry.exists() else None
    with observador.observador_de_escrituras() as registro:
        rc_registro, _ = espejo.registrar("FASE-X", DIA_1, tests="7")
    escrituras_registro = [(op, r) for op, r, _ in registro.operaciones]
    _exigir_rutas_en_temporal(espejo.rai, [r for _, r in escrituras_registro])

    espejo.publicar_nueva_release(NUEVA_FECHA_RELEASE, NUEVA_VERSION)
    ok_escritura, resultados_escritura, escrituras_sync = espejo.sincronizar(check_only=False)
    fecha_tras_escritura = espejo.fecha_cabecera()
    ok_check, resultados_check, escrituras_check = espejo.sincronizar(check_only=True)
    ok_check2, _, escrituras_check2 = espejo.sincronizar(check_only=True)

    return {
        "rc_registro": rc_registro,
        "fecha_cabecera": espejo.fecha_cabecera(),
        "fecha_tras_escritura": fecha_tras_escritura,
        "numero_cabeceras": espejo.cabeceras(),
        "entradas_FASE_X": espejo.entradas("FASE-X"),
        "texto": espejo.texto(),
        "sync_escritura_ok": ok_escritura,
        "sync_escritura_resultados": dict(resultados_escritura),
        "sync_check_ok": ok_check,
        "sync_check2_ok": ok_check2,
        "escrituras_registro": escrituras_registro,
        "escrituras_sync": escrituras_sync,
        "escrituras_check": escrituras_check + escrituras_check2,
        "fecha_en_otros_docs": _fechas_en_otros(espejo),
        "registry_toco_check": [r for _, r in (escrituras_check + escrituras_check2)
                                if "REGISTRY.md" in r],
        "huella_antes": huella_antes,
        "nueva_fecha_release": NUEVA_FECHA_RELEASE,
        "nueva_version": NUEVA_VERSION,
        "tracker": (json.loads(espejo.tracker.read_text(encoding="utf-8"))
                    if espejo.tracker.exists() else None),
        "tracker_ruta": espejo.tracker.as_posix(),
    }


def _fechas_en_otros(espejo: Expediente) -> dict:
    """Fecha que dejo la sincronizacion en los encabezados versionados del expediente."""
    salida = {}
    for rel in CONSUMIDORES_VERSIONADOS:
        p = espejo.rai / rel
        if not p.exists():
            continue
        texto = p.read_text(encoding="utf-8", errors="replace")
        salida[rel] = re.findall(r"(?m)^.*?(?:last_update|Última actualización|Actualizado)"
                                 r"[^\d]{0,12}(\d{4}-\d{2}-\d{2})", texto)
    return salida


def _exigir_interaccion(oc: dict):
    """La exigencia unica: tras registrar y sincronizar en modo escritura, la fecha de la ENTRADA
    manda sobre la de release, y `--check` ya no la discute."""
    assert oc["rc_registro"] == 0, (
        f"el registro salio {oc['rc_registro']}: el instrumento no llego a escribir, y un rojo "
        "posterior no seria por discrepancia de fecha")
    assert oc["escrituras_registro"], (
        "el escritor no abrio ningun archivo del expediente: la interaccion no se ejercito")
    assert any("REGISTRY.md" in r for _, r in oc["escrituras_registro"]), (
        f"el escritor no abrio REGISTRY.md: {oc['escrituras_registro']}")
    # El auxiliar tambien esta redirigido al expediente: "redirigir todas las rutas" no vale si nadie
    # comprueba a donde fue a parar lo que escribe esa ruta (mandato §3 de la remediacion).
    assert any(".last_doc_phase.json" in r for _, r in oc["escrituras_registro"]), (
        f"el registro no escribio el tracker auxiliar dentro del expediente "
        f"({oc['tracker_ruta']}); las aperturas observadas fueron: {oc['escrituras_registro']}")
    assert oc["tracker"] == {"modules/ejemplo.py": "FASE-X"}, (
        f"el tracker del expediente no quedo como se le paso: {oc['tracker']}")
    assert oc["sync_escritura_ok"] is True, (
        f"la sincronizacion en modo escritura no cuadro: {oc['sync_escritura_resultados']}")
    assert oc["escrituras_sync"], (
        "la sincronizacion en modo escritura no escribio nada: el verde seria vacio")
    assert set(oc["fecha_en_otros_docs"]) >= {"AGENTS.md", "docs/GUIA_TECNICA.md"}, (
        f"el expediente no es coherente con los consumidores reales: "
        f"{sorted(oc['fecha_en_otros_docs'])}")
    assert any(oc["fecha_en_otros_docs"]["AGENTS.md"]) and \
        NUEVA_FECHA_RELEASE in oc["fecha_en_otros_docs"]["AGENTS.md"], (
        f"la release nueva no llego a AGENTS.md ({oc['fecha_en_otros_docs']['AGENTS.md']}): sin "
        "este ancla, «REGISTRY conservo su fecha» podria deberse a que sync no hizo nada")

    # Y aqui, la propiedad gobernada — primero, para que un expediente con la autoridad competidora
    # caiga por la discrepancia de fecha y no por un efecto colateral posterior:
    assert oc["fecha_cabecera"] == DIA_1, (
        f"la cabecera de REGISTRY quedo en {oc['fecha_cabecera']!r} en lugar de la fecha de la "
        f"ultima entrada documental ({DIA_1!r}); la de release recien sincronizada es "
        f"{NUEVA_FECHA_RELEASE!r}. Un segundo escritor de la fecha habria vuelto a ganar")
    assert oc["fecha_tras_escritura"] == DIA_1, (
        f"justo tras sincronizar la cabecera valia {oc['fecha_tras_escritura']!r}, no {DIA_1!r}")
    assert REGISTRY_REL not in " ".join(r for _, r in oc["escrituras_sync"]), (
        f"la sincronizacion abrio REGISTRY.md en modo escritura: {oc['escrituras_sync']}")
    assert oc["sync_check_ok"] is True and oc["sync_check2_ok"] is True, (
        "`sync_versions --check` vuelve a discutir la fecha de la entrada: reaparece el conflicto "
        "del dia siguiente")
    assert oc["escrituras_check"] == [], (
        f"`--check` escribio: {oc['escrituras_check']}")
    assert oc["registry_toco_check"] == [], (
        f"`--check` abrio REGISTRY.md: {oc['registry_toco_check']}")


def test_interaccion_real_registro_sync_escritura_y_check(tmp_path):
    """Registrar → sincronizar en modo escritura → verificar, sobre el mismo expediente temporal."""
    espejo = Expediente(tmp_path)
    oc = _interaccion(espejo)
    assert oc["fecha_cabecera"] == DIA_1, "precondition: el registro tiene que haber estampado hoy"
    assert oc["entradas_FASE_X"] == 1, oc["texto"]
    assert oc["numero_cabeceras"] == 1, f"una cabecera por expediente: {oc['numero_cabeceras']}"
    _exigir_interaccion(oc)


def test_control_negativo_escritor_real_fuera_del_temporal(tmp_path, monkeypatch):
    espejo = Expediente(tmp_path)
    protegido = tmp_path / "tracker_protegido_de_prueba.json"
    assert _dentro(protegido, tmp_path) and not _dentro(protegido, espejo.rai)
    protegido.write_bytes(b"{}\n")
    cargar_real = _cargar
    ejecucion = {}

    def cargar_con_escritura_extra(nombre, ruta):
        mod = cargar_real(nombre, ruta)
        if ruta == LPC:
            main_real = mod.main

            def main_con_escritura_extra():
                rc = main_real()
                ejecucion["rc"] = rc
                tracker_temporal = mod.LAST_DOC_TRACKER
                try:
                    mod.LAST_DOC_TRACKER = protegido
                    mod.save_last_documented_phase("FASE-ESCAPADA", ["modules/escape.py"])
                finally:
                    mod.LAST_DOC_TRACKER = tracker_temporal
                return rc

            monkeypatch.setattr(mod, "main", main_con_escritura_extra)
        return mod

    monkeypatch.setattr(sys.modules[__name__], "_cargar", cargar_con_escritura_extra)
    with pytest.raises(AssertionError, match="rutas fuera del mismo temporal") as rojo:
        _interaccion(espejo)
    assert ejecucion["rc"] == 0, "el escritor real debe terminar antes del fallo por ruta"
    assert espejo.fecha_cabecera() == DIA_1
    assert espejo.entradas("FASE-X") == 1
    assert json.loads(espejo.tracker.read_bytes()) == {"modules/ejemplo.py": "FASE-X"}
    assert json.loads(protegido.read_bytes()) == {"modules/escape.py": "FASE-ESCAPADA"}
    assert ("Path.write_text", protegido.as_posix()) in espejo.escrituras
    assert protegido.as_posix() in str(rojo.value)


def test_la_entrada_cerrada_antes_no_se_toca(tmp_path):
    """«No borrar entradas previas ni aceptar cambios silenciosos de una entrada» (§3).

    Se afirma sobre el **contenido** de la entrada historica, no sobre su separador `---`: el escritor
    inserta la entrada nueva justo antes del ultimo `---` del expediente (cada entrada lleva el suyo
    al final), de modo que ese separador pasa a cerrar la nueva. Eso no borra ni reescribe nada.
    """
    espejo = Expediente(tmp_path)
    antes = espejo.texto()
    contenido_antes = antes[antes.index("## FASE-ANterior"):antes.index("no se toca") + len("no se toca")]
    oc = _interaccion(espejo)
    despues = oc["texto"]

    assert contenido_antes in despues, (
        "el contenido de una entrada cerrada cambio al registrar la nueva:\n"
        f"{contenido_antes!r}")
    assert despues.count("**Descripcion:** entrada ya cerrada, no se toca") == 1, (
        "la descripcion de la entrada anterior se duplico")
    assert despues.index("## FASE-ANterior") < despues.index("## FASE-X"), (
        "el registro inserto la entrada nueva antes de la historica: no es append")
    assert oc["entradas_FASE_X"] == 1
    # La poblacion de entradas crece exactamente en una: nada previo desaparecio.
    assert despues.count("\n## ") - antes.count("\n## ") == 1, (
        f"el numero de entradas del registro salto en mas de una: antes {antes.count(chr(10)+'## ')}"
        f", despues {despues.count(chr(10)+'## ')}")


def test_repetir_el_registro_y_cambiar_de_dia(tmp_path):
    """Comportamiento explícito al repetir: append de entradas, cabecera unica, fecha del dia nuevo.

    Se afirma el comportamiento real, no una «idempotencia» que el script no implementa:
    `log_phase_completion` apila una entrada `## FASE-…` por corrida (eso no es la fuente del
    conflicto) y la cabecera "> **Ultima actualizacion:**" permanece UNICA y con la fecha de la
    ultima entrada, que al cambiar el dia TIENE que moverse.
    """
    espejo = Expediente(tmp_path)
    patron_entradas = r"(?ms)^## FASE-.*?(?=^---$|^## |\Z)"
    entradas_previas = re.findall(patron_entradas, espejo.texto())
    assert len(entradas_previas) == 1
    for numero, dia in enumerate((DIA_1, DIA_1, DIA_2), start=1):
        version = f"{NUEVA_VERSION.rsplit('.', 1)[0]}.{numero - 1}"
        espejo.publicar_nueva_release(NUEVA_FECHA_RELEASE, version)
        rc, _ = espejo.registrar("FASE-REP", dia)
        assert rc == 0
        rutas_registro = {Path(r).resolve() for op, r in espejo.escrituras
                          if op == "Path.write_text"}
        assert rutas_registro >= {espejo.registry.resolve(), espejo.tracker.resolve()}
        assert espejo.fecha_cabecera() == dia
        assert espejo.cabeceras() == 1, "repetir no puede duplicar la cabecera de fecha"
        assert espejo.entradas("FASE-REP") == numero, (
            "el append por fase es el comportamiento vigente: no se vende como idempotencia")
        texto = espejo.texto()
        assert f"> **Total fases completadas:** {numero + 1}\n" in texto
        entradas = re.findall(patron_entradas, texto)
        assert len(entradas) == len(entradas_previas) + 1
        assert entradas[:-1] == entradas_previas, "se muto o desaparecio una entrada previa"
        assert entradas[-1].startswith(f"## FASE-REP - {dia}\n")
        assert "**Descripcion:** registro de prueba\n" in entradas[-1]
        assert "`modules/ejemplo.py`" in entradas[-1]
        assert json.loads(espejo.tracker.read_bytes()) == {"modules/ejemplo.py": "FASE-REP"}
        huellas_registradas = {p: _huella(p) for p in (espejo.registry, espejo.tracker)}

        ok_escritura, resultados, escrituras = espejo.sincronizar(check_only=False)
        assert ok_escritura is True, resultados
        assert "UPDATED" in resultados.values(), "cada ronda debe ejercitar escritura real"
        assert ("Path.write_text", (espejo.rai / "AGENTS.md").as_posix()) in escrituras
        assert all(Path(r).resolve() not in rutas_registro for _, r in escrituras)
        assert version in (espejo.rai / "AGENTS.md").read_text(encoding="utf-8")
        assert NUEVA_FECHA_RELEASE in _fechas_en_otros(espejo)["AGENTS.md"]
        assert espejo.fecha_cabecera() == dia, "sync sustituyo la fecha de la entrada"
        assert espejo.texto() == texto
        assert {p: _huella(p) for p in huellas_registradas} == huellas_registradas

        ok_check, resultados_check, escrituras_check = espejo.sincronizar(check_only=True)
        assert ok_check is True, resultados_check
        assert escrituras_check == [], f"check escribio en la ronda {numero}: {escrituras_check}"
        assert espejo.fecha_cabecera() == dia
        assert espejo.cabeceras() == 1
        assert espejo.entradas("FASE-REP") == numero
        assert espejo.texto() == texto
        assert {p: _huella(p) for p in huellas_registradas} == huellas_registradas
        entradas_previas = entradas
    assert espejo.entradas("FASE-REP") == 3


def test_fecha_de_release_distinta_de_la_de_entrada_llega_a_los_otros_docs(tmp_path):
    """La fecha de release sigue viajando por su camino: si sync no escribiese, el resto cede.

    Sin esta prueba, «REGISTRY conserva su fecha» podria salir de que la sincronizacion no hizo nada
    en todo el expediente.
    """
    espejo = Expediente(tmp_path)
    espejo.registrar("FASE-REL", DIA_1)
    espejo.publicar_nueva_release(NUEVA_FECHA_RELEASE, NUEVA_VERSION)
    ok, resultados, escrituras = espejo.sincronizar(check_only=False)
    assert ok is True, resultados
    assert any("AGENTS.md" in r or "GUIA_TECNICA" in r for _, r in escrituras), (
        f"la sincronizacion no toco los encabezados versionados: {escrituras}")
    assert NUEVA_VERSION in (espejo.rai / "AGENTS.md").read_text(encoding="utf-8", errors="replace")
    assert espejo.fecha_cabecera() == DIA_1, (
        "REGISTRY perdio su fecha de entrada mientras sync actualizaba los demas encabezados")


# --------------------------------------------------------------- (3) control negativo por causa

def _ids_regla(config_path: Path) -> set:
    return {rule.get("id") for rule in yaml.safe_load(
        config_path.read_text(encoding="utf-8")).get("rules", [])}


def test_control_negativo_restituir_la_autoridad_rompe_la_misma_exigencia(tmp_path):
    """Restituir `registry_last_update` **solo en la copia temporal** tiene que poner roja la MISMA
    exigencia, por discrepancia de fecha.

    Un fallo de importacion o de configuracion no vale como rojo por causa: antes de exigir la
    discrepancia se comprueba que el registro y la sincronizacion funcionaron, que la regla
    restituida es la unica diferencia con la prueba positiva y que fue ESA regla la que abrio
    REGISTRY.md en modo escritura.
    """
    config_viciada = tmp_path / "sync_config_viciada.yaml"
    texto = SYNC_CONFIG.read_text(encoding="utf-8")
    assert "registry_last_update" not in _ids_regla(SYNC_CONFIG), (
        "precondition: la regla competidora ya no esta en la config real; si reaparecio, este "
        "control deja de ser un control")
    config_viciada.write_text(texto + REGLA_COMPETIDORA, encoding="utf-8")
    assert _ids_regla(config_viciada) == _ids_regla(SYNC_CONFIG) | {"registry_last_update"}, (
        "la copia viciada no difiere de la real solo en la autoridad competidora")

    espejo = Expediente(tmp_path / "sub", config_src=config_viciada)
    rc, _ = espejo.registrar("FASE-NEG", DIA_1)
    assert rc == 0, "el escritor no funciono: el rojo no seria por la causa nombrada"
    assert espejo.fecha_cabecera() == DIA_1, (
        "precondition: el registro debe estampar la fecha de la entrada antes de sincronizar")
    espejo.publicar_nueva_release(NUEVA_FECHA_RELEASE, NUEVA_VERSION)
    ok, resultados, escrituras = espejo.sincronizar(check_only=False)
    assert "registry_last_update" in resultados, resultados
    assert any("REGISTRY.md" in r for _, r in escrituras), (
        "la autoridad restituida no volvio a escribir REGISTRY.md: el rojo por causa no se podria "
        f"atribuir. Escrituras: {escrituras}")
    assert espejo.fecha_cabecera() == NUEVA_FECHA_RELEASE, (
        f"se restituyo la regla y AUN ASI la cabecera vale {espejo.fecha_cabecera()!r}: el control "
        "negativo no esta reproduciendo el defecto, con lo que la prueba positiva no estaria "
        "midiendo nada")

    with pytest.raises(AssertionError) as rojo:
        _exigir_interaccion(_interaccion(Expediente(tmp_path / "sub2",
                                                    config_src=config_viciada)))
    mensaje = str(rojo.value)
    assert DIA_1 in mensaje and NUEVA_FECHA_RELEASE in mensaje, (
        "el rojo no es por discrepancia de fecha (entrada vs release), sino por otra causa: "
        f"{mensaje[:400]}")


# ------------------------------------------------------------------- (4) contenido del registro

def _aprobaciones_no_ejecutadas(texto: str, fase: str) -> list:
    """Lineas `- [x]` de la entrada `fase`: garantias que el script no verifico.

    Se ancla a la cabecera de la entrada, no a «el ultimo bloque» ni a «un bloque nuevo al final»:
    el escritor inserta la entrada antes del ultimo separador, asi que el ultimo bloque del expediente
    es `## Formato` y una busqueda por posicion daria `[]` siempre (verde vacio, R2.9).
    """
    for bloque in re.split(r"(?m)^## ", texto):
        if bloque.startswith(f"{fase.upper()} - "):
            return [linea.strip() for linea in bloque.splitlines()
                    if linea.strip().startswith("- [x]")]
    raise AssertionError(f"no hay entrada `## {fase}` en el registro:\n{texto}")


def test_el_registro_no_publica_aprobaciones_que_no_ejecuto(tmp_path):
    """El escritor no ejecuta tests ni contratos: no puede publicarlos como pass.

    Antes cada entrada llevaba `- [x] Tests passing`, `- [x] Suite NEVER_BLOCK passing` y
    `- [x] Capability contract verificado` sin tener ninguna de esas garantias, y ademas un
    coherence por debajo del umbral se imprimia como `- [x] … (FALLO)`.
    """
    espejo = Expediente(tmp_path)
    rc, _ = espejo.registrar("FASE-HONESTA", DIA_1, tests="7", coherence=0.5)
    assert rc == 0
    texto = espejo.texto()
    assert _aprobaciones_no_ejecutadas(texto, "FASE-HONESTA") == [], (
        f"la entrada publicada sigue afirmando garantias no verificadas: "
        f"{_aprobaciones_no_ejecutadas(texto, 'FASE-HONESTA')}")
    assert "7" in texto and "declarado" in texto.lower(), (
        "el dato declarado debe seguir constando, marcado como declarado: " + texto[-700:])
    assert "FALLO" in texto, "un coherence 0.5 no puede desaparecer del registro"
    assert "- [x] Coherence" not in texto, (
        "el coherence incumplido no puede llevar casilla marcada")
    assert "NO verificados por este instrumento" in texto or "no verific" in texto.lower()


def test_control_negativo_el_escritor_permisivo_vuelve_a_afirmar_de_mas(tmp_path):
    """Rojo por causa con el instrumento DEFECTUOSO REAL: el escritor commiteado en
    `da382b1` (leido con `git show`, ejecutado con su propio `main()`) publica `- [x] Tests passing`
    y con eso rompe la MISMA exigencia de arriba, por la MISMA razon.

    Antes este control escribia a mano una entrada defectuosa: probaba la tecnica del predicate, no
    que el codigo anterior cayera aqui. Ahora el rojo sale del archivo versionado.
    """
    bueno = Expediente(tmp_path / "bueno")
    rc, _ = bueno.registrar("FASE-OK", DIA_1, tests="7", coherence=0.5)
    assert rc == 0
    assert _aprobaciones_no_ejecutadas(bueno.texto(), "FASE-OK") == [], (
        "precondition: el escritor del arbol de trabajo ya no debe afirmar nada no verificado")

    defectuoso = Expediente(tmp_path / "defectuoso")
    escritor_anterior = _fuente_versionada(tmp_path / "defectuoso", REV_ESCRITOR_DEFECTUOSO,
                                           "scripts/log_phase_completion.py")
    rc, _ = defectuoso.registrar("FASE-OK", DIA_1, tests="7", coherence=0.5,
                                 escritor=escritor_anterior)
    assert rc == 0, "el escritor versionado debe correr bien: el rojo lo causa su contenido"
    aprobadas = _aprobaciones_no_ejecutadas(defectuoso.texto(), "FASE-OK")
    assert aprobadas, (
        "el escritor anterior no publico aprobaciones no ejecutadas: el control no ejercita la causa "
        f"nombrada y el verde de la prueba buena no significaria nada;\n{defectuoso.texto()}")
    assert any("Tests passing" in linea for linea in aprobadas), (
        "el rojo no vino de la garantia nombrada sino de otra linea: " + str(aprobadas))


def test_sin_datos_no_se_afirma_una_ausencia(tmp_path):
    """`_Ninguno_` en una seccion vacia afirma que no habia archivos: el script no inspecciona el
    arbol, asi que lo suyo es «sin dato declarado». Es la misma familia que `- [x] Tests passing`."""
    lpc = _cargar("lpc_sin_datos", LPC)
    args = SimpleNamespace(fase="FASE-VACIA", desc="d", archivos_nuevos=None, archivos_mod=None,
                           tests=None, coherence=None)
    entrada = lpc.generar_entrada_registry(args)
    assert "_Ninguno_" not in entrada, (
        "el escritor vuelve a publicar una ausencia como si la hubiera comprobado:\n" + entrada)
    assert entrada.count("Sin dato declarado") == 2, entrada
    assert _aprobaciones_no_ejecutadas(entrada, "FASE-VACIA") == []


def test_generar_entrada_registry_conserva_los_datos_declarados(tmp_path):
    """Retirar afirmaciones no borra datos: lo declarado por quien registra sigue en la entrada."""
    lpc = _cargar("lpc_entrada", LPC)
    args = SimpleNamespace(fase="FASE-DATOS", desc="descripcion larga del tramo",
                           archivos_nuevos="modules/nuevo.py,tests/test_nuevo.py",
                           archivos_mod="modules/viejo.py", tests="13", coherence=0.91)
    entrada = lpc.generar_entrada_registry(args)
    for esperado in ("## FASE-DATOS", "descripcion larga del tramo", "modules/nuevo.py",
                     "tests/test_nuevo.py", "modules/viejo.py", "13", "0.91", "PASO"):
        assert esperado in entrada, f"falta {esperado!r} en:\n{entrada}"


def _exigir_bytes_lf(datos: bytes, ruta: Path):
    assert b"\r" not in datos, f"CR inesperado en los bytes de {ruta}"
    assert b"\n" in datos and datos.endswith(b"\n"), f"faltan finales LF en {ruta}"


def test_escritor_y_tracker_reales_guardan_bytes_lf(tmp_path):
    espejo = Expediente(tmp_path)
    rc, _ = espejo.registrar("FASE-LF", DIA_1)
    assert rc == 0
    assert espejo.fecha_cabecera() == DIA_1
    assert espejo.entradas("FASE-LF") == 1
    assert json.loads(espejo.tracker.read_bytes()) == {"modules/ejemplo.py": "FASE-LF"}
    for ruta in (espejo.registry, espejo.tracker):
        assert ("Path.write_text", ruta.as_posix()) in espejo.escrituras
        datos = ruta.read_bytes()
        _exigir_bytes_lf(datos, ruta)
        with pytest.raises(AssertionError, match="CR inesperado"):
            _exigir_bytes_lf(datos.replace(b"\n", b"\r\n"), ruta)


# ------------------------------------------------------- (5) el expediente real: no se toca a mano

def test_sync_check_repetido_no_reescribe_la_fecha_del_registry_real():
    assert REGISTRY.exists()
    obs = _observador()
    sync = _cargar("sync_registry_real_check_in_process", SYNC_SCRIPT)
    sync.ROOT_DIR = ROOT
    sync.VERSION_FILE = ROOT / "VERSION.yaml"
    sync.CONFIG_FILE = SYNC_CONFIG
    config = yaml.safe_load(SYNC_CONFIG.read_text(encoding="utf-8"))
    protegidos = {REGISTRY, REGISTRY.parent / ".last_doc_phase.json",
                  sync.VERSION_FILE, sync.CONFIG_FILE}
    protegidos.update(ROOT / regla["file"] for regla in config["rules"])

    def huellas_configuradas():
        huellas = obs.huellas(ROOT, archivos=protegidos)
        return {p.as_posix(): huellas.get(p.as_posix()) for p in protegidos}

    antes = huellas_configuradas()
    for _ in range(2):
        with obs.observador_de_escrituras() as registro:
            engine = sync.SyncEngine(sync.CONFIG_FILE)
            ok = engine.sync_all(check_only=True)
        assert registro.operaciones == [], f"check in-process escribio: {registro.operaciones}"
        assert huellas_configuradas() == antes, "check altero contenido o metadatos protegidos"
        assert set(engine.results) == {regla["id"] for regla in config["rules"]}
        assert ok is True, engine.results
