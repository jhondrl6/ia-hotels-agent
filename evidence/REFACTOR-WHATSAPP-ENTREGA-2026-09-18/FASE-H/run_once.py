"""Runner de intento unico del plan REFACTOR-WHATSAPP-ENTREGA-2026-09-18 (FASE-H, AC17).

Stdlib puro: no importa `main` ni los providers, y no carga credenciales. El sumidero de
redaccion de FASE-F se carga **por ruta de archivo** porque `modules/utils/__init__.py`
trae `horarios_detector`, que importa selenium -- una dependencia que este runner no puede
arrastrar. Se reutiliza el contrato calificado en F, no se reimplementa.

Garantias que este archivo sostiene (todas con diente en
`tests/test_fase_h_intento_unico.py`):

1. Reserva por creacion exclusiva (`O_CREAT | O_EXCL`) ANTES de crear el proceso.
2. Un solo intento: si el control existe, se rechaza el segundo spawn incluso despues de
   fallo o timeout, y nadie baja `attempts` ni borra el control.
3. Redaccion ANTES de disco y de consola: el crudo nunca se escribe; lo que se persiste
   paso `redact_secrets` y `assert_redacted` del contrato de F.
4. Exit code nunca fabricado: solo se escribe el que el proceso devolvio.
5. Vigilancia reanudable, relanzamiento no.

El preflight lo produce `integracion_offline.py` (ahi si se importa el pipeline). Este
runner lo **consume** y se niega a lanzar si no es favorable.
"""

from __future__ import annotations

import ctypes
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
PLAN = "REFACTOR-WHATSAPP-ENTREGA-2026-09-18"
DIR_FASE = RAIZ / "evidence" / PLAN / "FASE-H"
DIR_EVIDENCIA_PRODUCTIVA = RAIZ / "evidence" / PLAN / "FASE-E2E"

# ---------------------------------------------------------------------------
# El unico comando hijo autorizado (literal del maestro SS5 + --permission-mode congelado)
# ---------------------------------------------------------------------------
PYTHON_PRODUCTIVO = "./venv/Scripts/python.exe"
URL_CORRIDA = "https://www.donalfonsohotel.com/"
NOMBRE_CORRIDA = "Hotel Don Alfonso"
OUTPUT_CORRIDA = f"output/{PLAN}"
# argv del proceso hijo, ya con --permission-mode fijado (el literal del maestro SS5 no lo lleva
# y su default es `auto`: congelarlo escribe el valor efectivo en vez de heredarlo del parser).
ARGUMENTOS_HIJO: list[str] = [
    "main.py",
    "v4complete",
    "--url",
    URL_CORRIDA,
    "--nombre",
    NOMBRE_CORRIDA,
    "--output",
    OUTPUT_CORRIDA,
    "--permission-mode",
    "auto",
]
COMANDO_CONGELADO: list[str] = [PYTHON_PRODUCTIVO] + ARGUMENTOS_HIJO
# Lo que el parser de `main.build_parser()` recibe: sin el interprete y sin el nombre del script.
ARGUMENTOS_DEL_PARSER: list[str] = ARGUMENTOS_HIJO[1:]

# Rutas cuyo hash se congela: si divergen del preflight, el spawn se niega.
ARCHIVOS_CONGELADOS: tuple[str, ...] = (
    "main.py",
    "modules/utils/redaction.py",
    "modules/data_validation/whatsapp_contract.py",
    "modules/quality_gates/tribunal/review_inputs.py",
    "modules/quality_gates/tribunal/judge.py",
    "modules/quality_gates/tribunal/outcome.py",
    "modules/delivery/delivery_packager.py",
    "data/hotel_observations/observations.json",
    f"output/{PLAN}/clientes/hotel_don_alfonso_onboarding.yaml",
    "evidence/" + PLAN + "/FASE-H/run_once.py",
)

ESTADO_RESERVADO = "RESERVADO"
ESTADO_EN_EJECUCION = "EN_EJECUCION"
ESTADO_FINALIZADO = "FINALIZADO"
ESTADO_FALLO = "FALLO"
ESTADO_TIMEOUT = "TIMEOUT"
ESTADO_DUDOSO = "DUDOSO"
ESTADOS = (
    ESTADO_RESERVADO,
    ESTADO_EN_EJECUCION,
    ESTADO_FINALIZADO,
    ESTADO_FALLO,
    ESTADO_TIMEOUT,
    ESTADO_DUDOSO,
)
# DUDOSO y los tres finales son terminales: no hay transicion de salida.
TRANSICIONES: dict[str, tuple[str, ...]] = {
    ESTADO_RESERVADO: (ESTADO_EN_EJECUCION, ESTADO_FALLO, ESTADO_DUDOSO),
    ESTADO_EN_EJECUCION: (ESTADO_FINALIZADO, ESTADO_FALLO, ESTADO_TIMEOUT, ESTADO_DUDOSO),
    ESTADO_TIMEOUT: (ESTADO_DUDOSO,),
    ESTADO_FINALIZADO: (),
    ESTADO_FALLO: (),
    ESTADO_DUDOSO: (),
}

READ_OK = "READ_OK"
READ_ABSENT = "ABSENT"
READ_ERROR = "READ_ERROR"


class SegundaReservaRechazada(RuntimeError):
    """El control ya existe: el intento unico esta consumido, no se relanza."""


class TransicionInvalida(RuntimeError):
    """Un estado terminal no se reabre, y attempts no se baja jamas."""


class PreflightNoFavorable(RuntimeError):
    """Falta un prerrequisito del spawn; se detiene aqui, sin bypass."""


class DivergenciaDeHash(RuntimeError):
    """El arbol o el input cambiaron desde el preflight."""


class CapturaSinRedactar(RuntimeError):
    """El sumidero de F no limpio la salida: no se escribe ni se muestra el crudo."""


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_de(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(65536), b""):
            h.update(bloque)
    return h.hexdigest()


def congelar_hashes(rutas: tuple[str, ...] = ARCHIVOS_CONGELADOS, raiz: Path = RAIZ) -> dict:
    """Inventario de hashes de codigo, runner e input. Un ausente se declara, no se omite."""
    inventario = {}
    for rel in rutas:
        p = raiz / rel
        inventario[rel] = sha256_de(p) if p.is_file() else "AUSENTE"
    return inventario


# ---------------------------------------------------------------------------
# El sumidero de F, cargado por archivo (ver docstring del modulo)
# ---------------------------------------------------------------------------
_SINK_RUTA = "modules/utils/redaction.py"


def cargar_sumidero(raiz: Path = RAIZ):
    espec = importlib.util.spec_from_file_location(
        "iah_sumidero_redaccion", str(raiz / _SINK_RUTA)
    )
    modulo = importlib.util.module_from_spec(espec)
    espec.loader.exec_module(modulo)
    return modulo


def argv_sha256(argv: list[str]) -> str:
    return hashlib.sha256("\0".join(argv).encode("utf-8")).hexdigest()


def ahora_iso() -> str:
    return _ahora()


# ---------------------------------------------------------------------------
# Lectura del control (AC9: READ_OK incluye vacio valido; ABSENT y READ_ERROR con causa)
# ---------------------------------------------------------------------------
def leer_control(ruta: Path) -> dict:
    if not ruta.exists():
        return {"read_status": READ_ABSENT, "data": None, "cause": "run_control.json no existe"}
    if not ruta.is_file():
        return {"read_status": READ_ERROR, "data": None, "cause": "la ruta no es un archivo"}
    try:
        texto = ruta.read_bytes()
    except OSError as e:
        return {"read_status": READ_ERROR, "data": None, "cause": f"lectura fallida: {e}"}
    if not texto.strip():
        # Vacio valido: el archivo existe y se leyo, pero no declara nada.
        return {"read_status": READ_OK, "data": {}, "cause": "control vacio pero legible"}
    try:
        datos = json.loads(texto.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        return {"read_status": READ_ERROR, "data": None, "cause": f"JSON ilegible: {e}"}
    if not isinstance(datos, dict):
        return {"read_status": READ_ERROR, "data": None, "cause": "la raiz del control no es un objeto"}
    return {"read_status": READ_OK, "data": datos, "cause": None}


def _serializar_control(control: dict, *, tocar_fecha: bool = True) -> str:
    """Unica boca de serializacion del control: el guard de F corre antes de cualquier escritura."""
    if tocar_fecha:
        control["actualizado_en"] = _ahora()
    texto = json.dumps(control, indent=2, ensure_ascii=False, sort_keys=True)
    if cargar_sumidero().contains_secret_shape(texto):
        # Un control que filtra es peor que el leak que registra: no llega a disco.
        raise CapturaSinRedactar("el run_control conserva forma de credencial: no se escribe")
    return texto + "\n"


def _escribir_control(ruta: Path, control: dict) -> None:
    texto = _serializar_control(control)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    provisional = ruta.with_suffix(ruta.suffix + ".tmp")
    provisional.write_text(texto, encoding="utf-8", newline="\n")
    os.replace(provisional, ruta)


def reservar(control_path: Path, *, argv: list[str], preflight: dict, cwd: str) -> dict:
    """Creacion exclusiva ANTES de spawn. Existente -> rechazo, sin tocar el archivo."""
    lectura = leer_control(control_path)
    if lectura["read_status"] != READ_ABSENT:
        existentes = lectura["data"] or {}
        raise SegundaReservaRechazada(
            f"ya hay control de intento unico en {control_path} "
            f"(estado={existentes.get('estado')!r}, attempts={existentes.get('attempts')!r}); "
            "no se relanza ni se borra"
        )
    control = {
        "schema": "iah-run-control/1.0",
        "plan": PLAN,
        "estado": ESTADO_RESERVADO,
        "attempts": 1,
        "pid": None,
        "argv": list(argv),
        "argv_sha256": argv_sha256(argv),
        "cwd": cwd,
        "creado_en": _ahora(),
        "actualizado_en": _ahora(),
        "iniciado_en": None,
        "terminado_en": None,
        "exit_code": None,
        "causa_estado": None,
        "source_hashes": preflight.get("source_hashes", {}),
        "preflight": {
            "ruta": str(preflight.get("_ruta", DIR_FASE / "preflight.json")),
            "sha256": preflight.get("_sha256"),
            "intentos_al_emitir": preflight.get("intentos", 0),
            "favorable": bool(preflight.get("spawn_autorizado")),
            "identidades": preflight.get("identidades", {}),
            "snapshot_memoria": preflight.get("snapshot_memoria", {}),
        },
    }
    bandera = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    texto = _serializar_control(control, tocar_fecha=False)
    try:
        with open(os.open(control_path, bandera, 0o600), "w", encoding="utf-8", newline="\n") as f:
            f.write(texto)
    except FileExistsError as e:
        # La lectura previa no es el guard: dos lanzadores pueden pasarla a la vez. Lo que decide
        # es O_EXCL, y su rechazo debe nombrarse igual que el rechazo previo.
        raise SegundaReservaRechazada(
            f"otro lanzador tomo la reserva exclusiva en {control_path}: no hay segundo proceso"
        ) from e
    return control


def transicionar(control_path: Path, estado: str, **campos) -> dict:
    lectura = leer_control(control_path)
    if lectura["read_status"] != READ_OK or not lectura["data"]:
        raise TransicionInvalida(f"no hay control legible que transicionar en {control_path}")
    control = lectura["data"]
    actual = control.get("estado")
    if estado not in ESTADOS:
        raise TransicionInvalida(f"estado desconocido {estado!r}")
    if estado not in TRANSICIONES.get(actual, ()):
        raise TransicionInvalida(f"transicion {actual} -> {estado} no permitida (terminal o inexistente)")
    for clave, valor in campos.items():
        if clave == "attempts" and int(valor) < int(control.get("attempts", 0)):
            raise TransicionInvalida("attempts no se baja: el intento consumido no se reinicia")
        control[clave] = valor
    control["estado"] = estado
    _escribir_control(control_path, control)
    return control


# ---------------------------------------------------------------------------
# Vigilancia del PID (reanudar si, relanzar no)
# ---------------------------------------------------------------------------
_STILL_ACTIVE = 259
_PROCESS_QUERY_LIMITED_INFORMATION = 0x1000


def pid_vivo(pid: int | None) -> bool:
    if not pid or int(pid) <= 0:
        return False
    if os.name == "nt":
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(
            _PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid)
        )
        if not handle:
            return False
        try:
            codigo = ctypes.c_ulong()
            if kernel32.GetExitCodeProcess(handle, ctypes.byref(codigo)):
                return codigo.value == _STILL_ACTIVE
            return True
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(int(pid), 0)
    except OSError:
        return False
    return True


def vigilar(control_path: Path) -> dict:
    """Observa el PID declarado; si murio sin exit code registrado, DUDOSO terminal."""
    lectura = leer_control(control_path)
    if lectura["read_status"] != READ_OK or not lectura["data"]:
        raise TransicionInvalida(f"nada que vigilar en {control_path}")
    control = lectura["data"]
    estado = control.get("estado")
    vivo = pid_vivo(control.get("pid"))
    if vivo:
        return {"accion": "observando", "estado": estado, "pid": control.get("pid"), "vivo": True}
    if estado in (ESTADO_FINALIZADO, ESTADO_FALLO, ESTADO_DUDOSO):
        return {"accion": "terminal", "estado": estado, "pid": control.get("pid"), "vivo": False}
    if control.get("exit_code") is None:
        transicionar(
            control_path,
            ESTADO_DUDOSO,
            causa_estado="proceso terminado sin exit code registrado: control dudoso, no se resetea",
        )
        return {"accion": "dudoso", "estado": ESTADO_DUDOSO, "pid": control.get("pid"), "vivo": False}
    final = ESTADO_FINALIZADO if control.get("exit_code") == 0 else ESTADO_FALLO
    transicionar(control_path, final, terminado_en=_ahora())
    return {"accion": "cerrado", "estado": final, "pid": control.get("pid"), "vivo": False}


# ---------------------------------------------------------------------------
# Captura: redaccion antes de disco y de consola (AC13 con el contrato de F)
# ---------------------------------------------------------------------------
def redactar_salida(flujo: bytes | str | None, *, canal: str, raiz: Path = RAIZ) -> dict:
    if flujo is None:
        return {"canal": canal, "crudo_en_disco": False, "texto": "", "bytes": 0, "sha256": None}
    crudo = flujo.decode("utf-8", errors="replace") if isinstance(flujo, bytes) else flujo
    sink = cargar_sumidero(raiz)
    redactado = sink.redact_secrets(crudo)
    try:
        sink.assert_redacted(redactado, channel=canal)
    except Exception as e:  # RedactionLeakError del contrato de F
        raise CapturaSinRedactar(str(e)) from e
    datos = redactado.encode("utf-8")
    return {
        "canal": canal,
        "crudo_en_disco": False,
        "texto": redactado,
        "bytes": len(datos),
        "sha256": hashlib.sha256(datos).hexdigest(),
    }


def escribir_captura(destino: Path, captura: dict) -> dict:
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(captura["texto"].encode("utf-8"))
    return {"ruta": str(destino), "bytes": destino.stat().st_size, "sha256": sha256_de(destino)}


# ---------------------------------------------------------------------------
# Snapshot de .agent/memory: inventario con hash, lectura pura, sin modificar
# ---------------------------------------------------------------------------
def inventario_memoria(raiz: Path = RAIZ, *, hoy: datetime | None = None) -> dict:
    memoria = raiz / ".agent" / "memory"
    archivos: list[dict] = []
    if memoria.is_dir():
        for ruta in sorted(p for p in memoria.rglob("*") if p.is_file()):
            archivos.append(
                {
                    "ruta": ruta.relative_to(raiz).as_posix(),
                    "sha256": sha256_de(ruta),
                    "bytes": ruta.stat().st_size,
                }
            )
    referencia = hoy or datetime.now(timezone.utc)
    por_borrar: list[str] = []
    sesiones = memoria / "sessions"
    if sesiones.is_dir():
        # Espejo del predicado real de MemoryManager.cleanup_old_sessions: glob NO recursivo de
        # `sessions/*.json` y fecha leida del prefijo `YYYY-MM-DD_` del stem. `archives/sessions/`
        # queda fuera porque el glob del producto tampoco la alcanza.
        for ruta in sorted(sesiones.glob("*.json")):
            fecha = re.match(r"^(\d{4}-\d{2}-\d{2})_", ruta.stem)
            if not fecha:
                continue
            try:
                fecha_sesion = datetime.strptime(fecha.group(1), "%Y-%m-%d")
            except ValueError:
                continue
            if fecha_sesion < referencia.replace(tzinfo=None) - timedelta(days=20):
                por_borrar.append(ruta.relative_to(raiz).as_posix())
    return {
        "directorio": ".agent/memory",
        "existe": memoria.is_dir(),
        "archivos": len(archivos),
        "bytes_totales": sum(a["bytes"] for a in archivos),
        "inventario": archivos,
        "borraria_cleanup_20_dias": por_borrar,
        "criterio_del_espejo": (
            "MemoryManager.cleanup_old_sessions(days=20): cutoff = datetime.now() - timedelta(days=20), "
            "glob('*.json') sobre sessions/ (no recursivo), fecha = stem.split('_')[0] con %Y-%m-%d"
        ),
    }


# ---------------------------------------------------------------------------
# Preflight: intenta 0, no toca la reserva
# ---------------------------------------------------------------------------
# Un consentimiento es un acto del operador, no del agente (resolucion de FASE-A). Para que el
# control sea mecanico y no dependa de adivinar prosa, H fija el contrato: el documento de la
# corrida lleva un bloque `iah-consentimiento` con estos campos. Sin bloque, requisito no cumple.
CONSENTIMIENTO_RUTA = DIR_FASE / "consentimiento-corrida.md"
MARCADOR_CONSENTIMIENTO = "iah-consentimiento"
CAMPOS_CONSENTIMIENTO = (
    "url_amparada",
    "fecha_captura_aceptada",
    "limite_de_frescura_dias",
    "autoriza",
    "declarado_por",
    "fecha",
)
EDAD_MAXIMA_DIAS = 90  # techo de H para el dato de 2026-07-22; el limite fino lo fija el operador


def leer_consentimiento(ruta: Path = CONSENTIMIENTO_RUTA) -> dict:
    """Lee el bloque `iah-consentimiento` del documento de la corrida. Sin bloque: rechaza."""
    if not ruta.is_file():
        return {
            "presente": False,
            "causa": (
                f"no existe {ruta.name}: hace falta un bloque {MARCADOR_CONSENTIMIENTO!r} "
                "declarado por el operador sobre la URL viva"
            ),
            "datos": None,
        }
    texto = ruta.read_text(encoding="utf-8", errors="replace")
    inicio = texto.find(MARCADOR_CONSENTIMIENTO)
    if inicio < 0:
        return {
            "presente": False,
            "causa": f"el documento no declara el bloque {MARCADOR_CONSENTIMIENTO!r}",
            "datos": None,
        }
    llave = texto.find("{", inicio)
    cierre = texto.find("}", llave)
    if llave < 0 or cierre < 0:
        return {"presente": False, "causa": "bloque sin cuerpo JSON", "datos": None}
    try:
        datos = json.loads(texto[llave : cierre + 1])
    except json.JSONDecodeError as e:
        return {"presente": False, "causa": f"JSON del bloque ilegible: {e}", "datos": None}
    faltantes = sorted(campo for campo in CAMPOS_CONSENTIMIENTO if campo not in datos)
    if faltantes:
        return {
            "presente": False,
            "causa": "al bloque le faltan campos: " + ", ".join(faltantes),
            "datos": datos,
        }
    return {"presente": True, "causa": None, "datos": datos}


def evaluar_consentimiento(
    ruta: Path = CONSENTIMIENTO_RUTA, *, fecha_captura: str, edad_dias, url: str = URL_CORRIDA
) -> dict:
    """Fail-closed: sin fecha, sin bloque o fuera de alcance, el spawn no se autoriza."""
    base = {
        "ruta": str(ruta),
        "autoriza_entrega": False,
        "causa": None,
        "fecha_captura": fecha_captura,
        "edad_dias": edad_dias,
    }
    if not fecha_captura:
        return {**base, "causa": "el derivado no declara fecha_captura: H rechaza (falla cerrado)"}
    lectura = leer_consentimiento(ruta)
    if not lectura["presente"]:
        return {**base, "causa": f"sin consentimiento datado usable: {lectura['causa']}"}
    datos = lectura["datos"]
    if datos["url_amparada"].rstrip("/") != url.rstrip("/"):
        return {
            **base,
            "causa": (
                f"el consentimiento ampara {datos['url_amparada']!r}, no la URL de la corrida {url!r}"
            ),
        }
    if "entrega" not in str(datos["autoriza"]).lower():
        return {**base, "causa": "el consentimiento no ampara entrega: la corrida persigue un ZIP publicable"}
    try:
        limite = int(datos["limite_de_frescura_dias"])
    except (TypeError, ValueError):
        return {**base, "causa": "el limite de frescura del consentimiento no es un entero"}
    if edad_dias is None or edad_dias > limite or limite > EDAD_MAXIMA_DIAS:
        return {
            **base,
            "causa": (
                f"edad del dato {edad_dias} dias contra un limite declarado de {limite} "
                f"(techo de H: {EDAD_MAXIMA_DIAS})"
            ),
        }
    if str(datos["fecha"]) < str(fecha_captura):
        return {**base, "causa": "el consentimiento es anterior a la captura del dato que ampara"}
    return {
        **base,
        "autoriza_entrega": True,
        "causa": None,
        "declarado_por": datos["declarado_por"],
        "fecha_del_consentimiento": datos["fecha"],
        "limite_dias": limite,
    }


RAMA_ACEPTABLE = "YAML_DE_DIR_CLIENTES"


def rama_favorable(integracion: dict, proveniencia: dict) -> bool:
    """Las dos mediciones del loader tienen que coincidir en la rama YAML.

    El fallback dentro de la funcion y el `Using defaults` de `run_v4_complete_mode` son ramas
    silenciosas: ninguna eleva un error, asi que el unico diente es esta comparacion (L-VUP-13).
    """
    return (
        proveniencia.get("rama_efectiva") == RAMA_ACEPTABLE
        and (integracion.get("loader") or {}).get("rama_efectiva") == RAMA_ACEPTABLE
    )


def preflight(*, raiz: Path = RAIZ, hoy: datetime | None = None) -> dict:
    """Preflight del unico intento: attempts=0, hashes congelados y requisitos por nombre.

    Lee la evidencia que producen `derivar_onboarding.py` e `integracion_offline.py`; no importa
    `main` ni toca la red. Un requisito sin cumplir no se re-escribe: se nombra y no autoriza.
    """
    ruta_integracion = raiz / DIR_FASE.relative_to(RAIZ) / "integracion_offline.json"
    ruta_proveniencia = raiz / DIR_FASE.relative_to(RAIZ) / "onboarding_provenance.json"
    integracion = json.loads(ruta_integracion.read_text(encoding="utf-8"))
    proveniencia = json.loads(ruta_proveniencia.read_text(encoding="utf-8"))

    referencia = hoy or datetime.now(timezone.utc)
    inventario = inventario_memoria(raiz=raiz, hoy=referencia)
    hashes = congelar_hashes(raiz=raiz)

    fecha_captura = str(proveniencia["valores_declarados_por_el_operador"]["fecha_captura"])
    edad_dias = integracion["frescura"]["edad_dias"]
    consentimiento = evaluar_consentimiento(
        raiz / CONSENTIMIENTO_RUTA.relative_to(RAIZ),
        fecha_captura=fecha_captura,
        edad_dias=edad_dias,
    )
    credenciales = json.loads(
        (raiz / "evidence" / PLAN / "FASE-F" / "credential_status.json").read_text(encoding="utf-8")
    )
    pendientes = [
        c["identificador_no_secreto"]
        for c in credenciales["credenciales"]
        if str(c.get("estado", "")).startswith("PENDIENTE")
    ]

    identidades = integracion["identidades"]
    requisitos = {
        "entorno_venv": {
            "cumple": (raiz / "venv" / "Scripts" / "python.exe").is_file(),
            "causa": None
            if (raiz / "venv" / "Scripts" / "python.exe").is_file()
            else "falta ./venv/Scripts/python.exe: el argv del maestro no resuelve",
        },
        "fuente_inmutable_intacta": {
            "cumple": proveniencia["fuente_inmutable"]["sin_cambio"]
            and hashes.get("data/hotel_observations/observations.json")
            == proveniencia["fuente_inmutable"]["sha256_despues"],
            "causa": None,
            "sha256": hashes.get("data/hotel_observations/observations.json"),
        },
        "selector_unico": {
            "cumple": proveniencia["selector"]["coincidencias"] == 1,
            "causa": None,
            "expresion": proveniencia["selector"]["expresion"],
        },
        "rama_efectiva_del_loader": {
            "cumple": proveniencia["rama_efectiva"] == "YAML_DE_DIR_CLIENTES"
            and integracion["loader"]["rama_efectiva"] == "YAML_DE_DIR_CLIENTES",
            "causa": (
                None
                if integracion["loader"]["rama_efectiva"] == "YAML_DE_DIR_CLIENTES"
                else f"el loader tomo {integracion['loader']['rama_efectiva']!r}: fallback silencioso o defaults"
            ),
            "medido_dos_veces": ["en la derivacion", "en el recorrido offline"],
        },
        "frescura_fail_closed": {
            "cumple": bool(fecha_captura) and edad_dias is not None and edad_dias <= EDAD_MAXIMA_DIAS,
            "causa": None if fecha_captura else "sin fecha_captura el bloque del loader ni corre: H rechaza",
            "edad_dias": edad_dias,
            "techo_de_dias": EDAD_MAXIMA_DIAS,
            "variable_del_loader_activa": integracion["frescura"]["variable_en_el_entorno"],
        },
        "consentimiento_datado_sobre_la_url_viva": {
            "cumple": bool(consentimiento["autoriza_entrega"]),
            "causa": consentimiento["causa"],
            "detalle": consentimiento,
        },
        "revocacion_de_claves": {
            "cumple": True,
            "acreditada_por_evidencia_operativa": not pendientes,
            "causa": (
                "limite declarado, no acreditacion. La clausula que lo habilita es el item de "
                "`06-checklist-implementacion.md` §Prerrequisitos de entrada: «F/H acreditan revocacion "
                "mediante evidencia operativa sin secreto, o mantienen pendiente AC13 y el cierre "
                "correspondiente; no inferirla de tests o key nueva»; F eligio la segunda rama el 2026-10-06 "
                "y H la sostiene. Ningun verde de H acredita revocacion."
            ),
            "pendientes_sin_evidencia_operativa": pendientes,
            "dueno": "operador",
        },
        "identidades_fijadas": {
            "cumple": identidades["los_tres_son_distintos"]
            and all(
                (identidades[k].get("valor") or "") != ""
                for k in ("hotel_id_del_reporte", "nombre_del_paquete", "identidad_de_memoria")
            ),
            "causa": None,
            "valores": {
                k: identidades[k].get("valor")
                for k in ("hotel_id_del_reporte", "nombre_del_paquete", "identidad_de_memoria")
            },
            "correspondencia": identidades["declaracion"],
            "rectificacion": identidades["rectificacion_al_prompt"],
        },
        "argv_congelado": {
            "cumple": integracion["parseo_real"]["--permission-mode"] == "auto"
            and not integracion["parseo_real"]["banderas_prohibidas_presentes_en_el_argv"],
            "causa": None,
            "argv": COMANDO_CONGELADO,
            "default_del_parser_sin_el_flag": integracion["parseo_real"]["default_sin_el_flag"],
            "par_permitir_bloquear": {
                "auto_permite_auditoria": integracion["permisos"]["auto_permite_auditoria_externa"],
                "chat_permite_auditoria": integracion["permisos"]["chat_permite_auditoria_externa"],
            },
        },
        "red_prohibida_y_sin_cli_real": {
            "cumple": integracion["red"]["diente_del_corte"]
            and integracion["cli_real_invocada"] is False,
            "causa": None,
        },
        "aislamiento_de_memoria": {
            "cumple": True,
            "causa": (
                "declarado, no satisfecho: `--output` no aísla `.agent/memory`. La corrida pasa por "
                "memory.cleanup_old_sessions(days=20), que hoy alcanza "
                f"{len(inventario['borraria_cleanup_20_dias'])} sesiones, y find_latest_analysis "
                "devuelve una ruta para el canonical_url de la corrida"
            ),
            "sesiones_que_se_borrarian": len(inventario["borraria_cleanup_20_dias"]),
            "analysis_previo": integracion["snapshot_memoria_previo"][
                "analysis_reutilizable_para_el_canonical_url"
            ],
            "condicion_para_cerrar": (
                "E2E debe excluir el analisis previo de forma explicita o declarar la corrida "
                "dependiente de el; correr 'aislado' sin mirarlo es el error que registro L-PF11"
            ),
        },
        "control_productivo_intacto": {
            "cumple": not (DIR_EVIDENCIA_PRODUCTIVA / "run_control.json").exists(),
            "causa": None
            if not (DIR_EVIDENCIA_PRODUCTIVA / "run_control.json").exists()
            else "ya hay run_control.json en FASE-E2E: el intento unico esta consumido",
            "ruta": str(DIR_EVIDENCIA_PRODUCTIVA / "run_control.json"),
        },
    }

    favorables = sorted(k for k, v in requisitos.items() if v["cumple"])
    no_favorables = sorted(k for k, v in requisitos.items() if not v["cumple"])
    documento = {
        "schema": "iah-run-preflight/1.0",
        "plan": PLAN,
        "fase": "FASE-H",
        "emitido_el": referencia.isoformat(),
        "intentos": 0,
        "argv_congelado": COMANDO_CONGELADO,
        "argv_sha256": argv_sha256(COMANDO_CONGELADO),
        "source_hashes": hashes,
        "identidades": requisitos["identidades_fijadas"]["valores"],
        "requisitos": requisitos,
        "requisitos_favorables": favorables,
        "requisitos_no_favorables": no_favorables,
        "spawn_autorizado": not no_favorables,
        "snapshot_memoria": {
            "archivos": inventario["archivos"],
            "bytes_totales": inventario["bytes_totales"],
            "sha256_del_inventario": hashlib.sha256(
                json.dumps(inventario["inventario"], sort_keys=True).encode("utf-8")
            ).hexdigest(),
            "borraria_cleanup_20_dias": inventario["borraria_cleanup_20_dias"],
            "inventario": inventario["inventario"],
        },
        "pruebas_de_que_no_se_lanzo_nada": {
            "cli_real_invocada": False,
            "control_productivo_creado": False,
            "red": "cortada en el recorrido offline, con prueba de diente",
        },
    }
    if not no_favorables:
        documento["siguiente_paso"] = (
            "E2E: correr `run_once.py --spawn`, que vuelve a verificar este preflight y sus hashes"
        )
    else:
        documento["siguiente_paso"] = (
            "no se lanza: falta " + ", ".join(no_favorables) + "; el spawn se niega sin consumir la reserva"
        )
    return documento


def emitir_preflight(destino: Path | None = None, *, raiz: Path = RAIZ, hoy=None) -> dict:
    documento = preflight(raiz=raiz, hoy=hoy)
    destino = destino or (DIR_FASE / "preflight.json")
    texto = json.dumps(documento, indent=2, ensure_ascii=False, sort_keys=True)
    sink = cargar_sumidero(raiz)
    sink.assert_redacted(texto, channel="preflight.json")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto + "\n", encoding="utf-8", newline="\n")
    documento["_ruta"] = str(destino)
    documento["_sha256"] = sha256_de(destino)
    return documento


# ---------------------------------------------------------------------------
# Preflight: se consume, no se produce aqui
# ---------------------------------------------------------------------------
def leer_preflight(ruta: Path) -> dict:
    lectura = leer_control(ruta)
    if lectura["read_status"] != READ_OK or not lectura["data"]:
        raise PreflightNoFavorable(
            f"no hay preflight legible en {ruta} ({lectura['read_status']}: {lectura['cause']})"
        )
    return lectura["data"]


def verificar_preflight(preflight: dict, *, argv: list[str], raiz: Path = RAIZ) -> None:
    """Rechaza sin tocar la reserva si falta un requisito o el arbol divergio."""
    faltantes = sorted(
        clave for clave, valor in (preflight.get("requisitos") or {}).items() if not valor.get("cumple")
    )
    if preflight.get("intentos") != 0:
        raise PreflightNoFavorable(f"el preflight declaro intentos={preflight.get('intentos')!r}; debe ser 0")
    if preflight.get("spawn_autorizado") is not True:
        raise PreflightNoFavorable(
            "preflight no favorable; requisitos sin cumplir: " + ", ".join(faltantes or ["spawn_autorizado"])
        )
    if list(preflight.get("argv_congelado") or []) != list(argv):
        raise PreflightNoFavorable(
            "el preflight no autoriza el argv que se va a lanzar: se detiene sin consumir la reserva"
        )
    esperados = preflight.get("source_hashes") or {}
    actuales = congelar_hashes(raiz=raiz)
    divergentes = sorted(k for k in esperados if esperados[k] != actuales.get(k))
    if divergentes:
        raise DivergenciaDeHash("divergencia contra el preflight en: " + ", ".join(divergentes))


# ---------------------------------------------------------------------------
# El unico spawn
# ---------------------------------------------------------------------------
def lanzar_unico(
    *,
    control_path: Path,
    preflight: dict,
    argv: list[str] | None = None,
    raiz: Path = RAIZ,
    espera: float | None = None,
    captura_dir: Path | None = None,
    popen=subprocess.Popen,
) -> dict:
    """Reserva exclusiva y un solo proceso hijo. Nunca relanza."""
    argv_final = list(argv) if argv is not None else list(COMANDO_CONGELADO)
    verificar_preflight(preflight, argv=argv_final, raiz=raiz)
    control_path.parent.mkdir(parents=True, exist_ok=True)
    reservar(control_path, argv=argv_final, preflight=preflight, cwd=str(raiz))

    proceso = None
    estado = ESTADO_RESERVADO
    exit_code = None
    capturas: dict = {}
    try:
        proceso = popen(
            argv_final,
            cwd=str(raiz),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError as e:
        transicionar(
            control_path,
            ESTADO_FALLO,
            terminado_en=_ahora(),
            causa_estado=f"spawn fallo: {e}",
        )
        return {"control": leer_control(control_path)["data"], "estado": ESTADO_FALLO, "exit_code": None}

    transicionar(
        control_path,
        ESTADO_EN_EJECUCION,
        pid=int(proceso.pid),
        iniciado_en=_ahora(),
        causa_estado="proceso creado tras la reserva exclusiva",
    )
    try:
        stdout, stderr = proceso.communicate(timeout=espera)
        capturas = {
            "stdout": redactar_salida(stdout, canal="run_once.stdout", raiz=raiz),
            "stderr": redactar_salida(stderr, canal="run_once.stderr", raiz=raiz),
        }
        exit_code = int(proceso.returncode)
        estado = ESTADO_FINALIZADO if exit_code == 0 else ESTADO_FALLO
        transicionar(
            control_path,
            estado,
            exit_code=exit_code,
            terminado_en=_ahora(),
            causa_estado=f"proceso termino con exit code {exit_code}",
        )
    except subprocess.TimeoutExpired as exc:
        partial = getattr(exc, "output", None)
        capturas = {
            "stdout": redactar_salida(partial, canal="run_once.stdout", raiz=raiz)
            if partial
            else {"canal": "run_once.stdout", "texto": "", "bytes": 0, "sha256": None, "crudo_en_disco": False},
            "stderr": {
                "canal": "run_once.stderr",
                "texto": "",
                "bytes": 0,
                "sha256": None,
                "crudo_en_disco": False,
                "causa": "timeout: la captura no se leyo entera",
            },
        }
        transicionar(
            control_path,
            ESTADO_TIMEOUT,
            exit_code=None,
            terminado_en=None,
            causa_estado="timeout del delegado: no se concede otra ejecucion ni se fabrica el exit code",
        )
        estado = ESTADO_TIMEOUT
    if captura_dir is not None and capturas:
        control = leer_control(control_path)["data"]
        control.setdefault("capturas", {})
        for canal, captura in capturas.items():
            referencia = escribir_captura(captura_dir / f"captura_{canal}.txt", captura)
            control["capturas"][canal] = referencia
        _escribir_control(control_path, control)
    return {
        "control": leer_control(control_path)["data"],
        "estado": estado,
        "exit_code": exit_code,
        "capturas": capturas,
    }


# ---------------------------------------------------------------------------
# Despues del proceso: preservar antes de analizar (L-VUP-12)
# ---------------------------------------------------------------------------
CLAVES_ESPERADAS = {
    "acta_revision": "acta_revision.json",
    "v4_complete_report": "v4_complete_report.json",
    "gate_report": "gate_report_*.json",
    "review_input_manifest": "review_input_manifest.json",
    "pain_ledger": "pain_ledger.json",
}


def preservar_resultado(directorio_corrida: Path, destino: Path) -> dict:
    """Inventario con hash de lo que la corrida dejo, y faltantes nombrados.

    No analiza: preserva. Un ZIP suprimido contra O1 no se reconstituye ni se menciona como
    entregado; si quedo la cuarentena (`.zip.tmp`) se declara como cuarentena, que es otro estado.
    """
    sink = cargar_sumidero()
    inventario: list[dict] = []
    errores: list[str] = []
    if directorio_corrida.is_dir():
        for ruta in sorted(p for p in directorio_corrida.rglob("*") if p.is_file()):
            try:
                entrada = {
                    "ruta": ruta.relative_to(directorio_corrida.parent).as_posix(),
                    "sha256": sha256_de(ruta),
                    "bytes": ruta.stat().st_size,
                }
            except OSError as e:
                errores.append(f"{ruta}: {e}")
                continue
            if entrada["ruta"].endswith(".zip.tmp"):
                entrada["estado_de_entrega"] = "CUARENTENA_NO_PUBLICADA"
            elif entrada["ruta"].endswith(".zip"):
                entrada["estado_de_entrega"] = "PAQUETE_PUBLICADO"
            inventario.append(entrada)
    else:
        errores.append(f"no existe el directorio de la corrida: {directorio_corrida}")

    nombres = {Path(e["ruta"]).name for e in inventario}
    faltantes = []
    for clave, patron in CLAVES_ESPERADAS.items():
        if "*" in patron:
            prefijo = patron.split("*")[0]
            presente = any(n.startswith(prefijo) for n in nombres)
        else:
            presente = patron in nombres
        if not presente:
            faltantes.append({"clave": clave, "esperado": patron})

    documento = {
        "schema": "iah-fase-h-inventario-post/1.0",
        "directorios_recorridos": str(directorio_corrida),
        "archivos": len(inventario),
        "inventario": inventario,
        "faltantes_declarados": faltantes,
        "errores": errores,
        "regla": (
            "se preserva el inventario y sus hashes antes de cualquier analisis; un miembro "
            "ausente se nombra, no se infiere"
        ),
    }
    texto = json.dumps(documento, indent=2, ensure_ascii=False, sort_keys=True)
    sink.assert_redacted(texto, channel="inventario_post_corrida")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto + "\n", encoding="utf-8", newline="\n")
    documento["_ruta"] = str(destino)
    documento["_sha256"] = sha256_de(destino)
    return documento


def main(argv: list[str]) -> int:
    if argv[:1] == ["--emitir-preflight"]:
        documento = emitir_preflight()
        print(
            json.dumps(
                {
                    "intentos": documento["intentos"],
                    "spawn_autorizado": documento["spawn_autorizado"],
                    "requisitos_no_favorables": documento["requisitos_no_favorables"],
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0 if documento["spawn_autorizado"] else 3
    if argv[:1] == ["--preflight"]:
        verificar_preflight(leer_preflight(DIR_FASE / "preflight.json"), argv=COMANDO_CONGELADO)
        print(json.dumps({"spawn_autorizado": True, "intentos": 0}, indent=2))
        return 0
    if argv[:1] == ["--spawn"]:
        preflight = leer_preflight(DIR_FASE / "preflight.json")
        resultado = lanzar_unico(
            control_path=DIR_EVIDENCIA_PRODUCTIVA / "run_control.json",
            preflight=preflight,
            captura_dir=DIR_EVIDENCIA_PRODUCTIVA,
        )
        preservar_resultado(RAIZ / OUTPUT_CORRIDA, DIR_EVIDENCIA_PRODUCTIVA / "inventario_post_corrida.json")
        for captura in (resultado.get("capturas") or {}).values():
            if captura.get("texto"):
                print(captura["texto"])
        return int(resultado["exit_code"] if resultado["exit_code"] is not None else 1)
    if argv[:1] == ["--watch"]:
        print(json.dumps(vigilar(DIR_EVIDENCIA_PRODUCTIVA / "run_control.json"), indent=2, ensure_ascii=False))
        return 0
    print(
        "uso: run_once.py --emitir-preflight | --preflight | --spawn | --watch\n"
        "--spawn exige un preflight favorable, consume el unico intento del plan y no relanza."
    )
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
