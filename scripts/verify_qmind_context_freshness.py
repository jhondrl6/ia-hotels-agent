#!/usr/bin/env python3
"""Verificar que cada `CONTEXT` gobernado tiene una fuente publicada que CASE por bytes (S34).

Existe por la fila 11 del registro unificado del 2026-09-29 (deuda senalada por la tanda de re-ingesta
del `CONTEXT` de JEV, RI §6 y §13): un archivado vence tambien los `CONTEXT` ya publicados, y el
verificador de la casa (`validate_qmind_writeback.py`) no los mira — su poblacion son los `10-analisis`
archivados y decide por **titulo**. Por eso el verde `13/13` convivio nueve dias con un `CONTEXT` vencido
sin decir nada.

**Criterio: DESCARGA + sha256 contra el archivo gobernado. Nunca por titulo.** `metadata.fileSha256` que
publica el listado es **corroboracion**: se compara y se declara su desacuerdo, pero ninguna decision sale
de el (medido el 2026-09-29: la fuente vencida y la fresca tienen titulos que conservan el stem, y la
forma «original + cierre» es legal — hay dos fuentes del mismo CONTEXT y solo una casa por bytes).

Poblacion (se publica en la salida, con sus exclusiones y su razon):
  1. `CONTEXT-*.md` de la raiz de `--context-dir` **que autodeclaren** una leccion durable. El detector
     acepta las dos grafias vivas (linea suelta y encabezado); la copia del write-back solo ve la primera,
     y asi perdio al de JEV (medido 2026-09-27: `scan_context_declarations()` = 0 sobre ese archivo).
  2. Mas los `CONTEXT-*` que citen los planes archivados y que resuelvan en esa misma raiz.
  Fuera, con su razon medida: los que no declaran (la politica del write-back es por aporte declarado,
  executor v2.18.0) y todo `Historico/` (contenido congelado: R2.5 y la nota «QMind y archivado»).

La bajada va **por shell** (`shell=True`), no por `CreateProcess` sobre el shim: `qmind` es un `.cmd` de
npm y desde `subprocess` de Python con el nombre resuelto falla con `FileNotFoundError [WinError 2]`
(medido 2026-09-29). Los ids que entran al comando estan validados por patron, no interpolados crudos.

Salidas (tri-estado, R2.9):
  0 — todos los gobernados tienen al menos una fuente publicada que casa byte a byte.
  1 — al menos uno esta VENCIDO (hay fuentes que lo nombran y ninguna casa), o `--strict` sin `qmind`.
  2 — NO-EVALUABLE: un gobernado desaparecio del disco entre el censo y la corrida, o la poblacion quedo
      vacia habiendo ficheros `CONTEXT-*` (un verde sin candidatos no es un verde).
Sin `qmind` disponible y sin `--strict`: WARN + 0, el mismo fallback del executor (:468) que usa el
verificador hermano.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONTEXT = ROOT / ".opencode" / "context"
DEFAULT_PLANS = ROOT / ".opencode" / "plans"
NOTEBOOK_TITULO = "iah-cli-lecciones"

ID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
NOMBRE_CONTEXT = re.compile(r"CONTEXT-[A-Za-z0-9._-]+")

# Las dos grafias vivas de la autodeclaracion. La copia vieja anclaba `^Lección durable:` a inicio de
# linea y el CONTEXT de JEV la escribe como encabezado: el detector devolvia 0 sobre un archivo que si
# declara (medido 2026-09-27).
MARCA_DURABLE = (
    re.compile(r"(?mi)^\s*(?:#{1,6}\s*)?Lecci[oó]n de forma\s*:"),
    re.compile(r"(?mi)^\s*(?:#{1,6}\s*)?Lecci[oó]n durable\s*:"),
    re.compile(r"(?mi)^\s*(?:#{1,6}\s*)?Lecciones capitalizadas"),
)

EXCLUSION_HISTORICO = ("esta bajo `Historico/`: el contenido archivado queda congelado y no necesita "
                       "mantenimiento (R2.5 y la nota «QMind y archivado» del executor)")
EXCLUSION_NO_DECLARA = ("no autodeclara una leccion durable: la politica del write-back es por aporte "
                        "declarado, no por existencia (executor v2.18.0)")


class QmindNoDisponible(RuntimeError):
    """CLI ausente, sin auth, o notebook no resuelto: el limite del metodo, no un veredicto."""


def sha256_de(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def _qmind_exe() -> str:
    """Ruta resuelta del CLI. `qmind` a secas es un shim `.CMD` de npm y `CreateProcess` no lo encuentra.

    Medido el 2026-09-30 para esta cura: `shutil.which('qmind')` devuelve
    `%APPDATA%\\npm\\qmind.CMD` y `subprocess.run([exe, …])` responde `rc=0`. Lo que fallaba (y de lo que
    habla la nota de la casa del 2026-09-29) es llamar al nombre **sin extension**, no el subprocess en si.
    Se pasa la lista de argumentos y no una cadena de shell para no interpolar rutas de disco dentro de un
    parser de shell: el argumento `-o` lleva un path del scratch, y una ruta con espacios o comillas no
    debe volverse codigo.
    """
    exe = shutil.which("qmind") or shutil.which("qmind", path=str(Path.home() / "AppData" / "Roaming" / "npm"))
    if not exe:
        for extension in (".CMD", ".cmd", ".bat", ".exe"):
            candidato = Path.home() / "AppData" / "Roaming" / "npm" / f"qmind{extension}"
            if candidato.is_file():
                return str(candido)
        raise QmindNoDisponible("el CLI `qmind` no esta instalado ni resuelto en PATH")
    return exe


def _run_qmind(args: list[str]) -> tuple[int, str]:
    """`qmind <args>` con la ruta resuelta y argumentos en lista (sin parser de shell en medio)."""
    try:
        proc = subprocess.run([_qmind_exe(), *args], capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=180)
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except FileNotFoundError as exc:
        raise QmindNoDisponible(f"qmind no resuelve ({exc})") from exc
    except OSError as exc:
        raise QmindNoDisponible(f"qmind no respondio ({type(exc).__name__}: {exc.strerror})") from exc
    except subprocess.TimeoutExpired as exc:
        raise QmindNoDisponible("qmind no respondio (timeout 180s)") from exc


def _validar_id(valor: str, etiqueta: str) -> str:
    if not ID_RE.match(valor or ""):
        raise QmindNoDisponible(f"{etiqueta} no es un UUID valido: {valor!r}")
    return valor


def resolver_notebook(explicito: str) -> str:
    if explicito:
        return _validar_id(explicito, "--nb")
    rc, salida = _run_qmind(["notebook", "list", "--format", "json"])
    if rc != 0:
        raise QmindNoDisponible(f"`qmind notebook list` salio {rc}: {_primera_linea(salida)}")
    try:
        datos = json.loads(salida)
    except json.JSONDecodeError as exc:
        raise QmindNoDisponible(f"listado de notebooks no es JSON: {exc}") from exc
    notebooks = datos.get("notebooks", datos if isinstance(datos, list) else [])
    coincidencias = [nb for nb in notebooks if (nb.get("title") or "").strip() == NOTEBOOK_TITULO]
    if not coincidencias:
        raise QmindNoDisponible(f"no existe el notebook {NOTEBOOK_TITULO!r} en la cuenta")
    return _validar_id(coincidencias[0]["id"], "id del notebook")


def listar_fuentes(nb: str) -> list[dict]:
    """Las fuentes del notebook. La clave del listado es `sources`; con `--all` el `totalSize` viene 0."""
    rc, salida = _run_qmind(["source", "list", "--nb", _validar_id(nb, "nb"), "--all",
                             "--format", "json"])
    if rc != 0:
        raise QmindNoDisponible(f"`qmind source list` salio {rc}: {_primera_linea(salida)}")
    inicio = salida.find("{")
    if inicio < 0:
        raise QmindNoDisponible(f"el listado no trae JSON: {_primera_linea(salida)}")
    datos = json.loads(salida[inicio:])
    fuentes = datos.get("sources", datos.get("items", [] if isinstance(datos, list) else []))
    if isinstance(datos, list):
        fuentes = datos
    return [{"id": f.get("id", ""), "title": f.get("title", ""),
             "sha_metadata": (f.get("metadata") or {}).get("fileSha256", "")}
            for f in fuentes if f.get("id")]


def descargar(nb: str, source_id: str, destino: Path) -> bool:
    """`qmind source download` por shell. Devuelve False si la bajada no dejo archivo legible."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    rc, salida = _run_qmind(["source", "download", "--nb", _validar_id(nb, "nb"),
                             _validar_id(source_id, "source id"), "-o", str(destino)])
    if rc != 0:
        print(f"  [AVISO] descarga {source_id} salio {rc}: {_primera_linea(salida)}")
        return False
    return destino.is_file()


def declara_durable(ruta: Path) -> bool:
    try:
        texto = ruta.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return any(marca.search(texto) for marca in MARCA_DURABLE)


def citados_por_planes_archivados(plans_dir: Path, context_dir: Path) -> list[Path]:
    """`CONTEXT-*` mencionados por los planes archivados, resueltos SOLO dentro de `context_dir`."""
    archives = plans_dir / "Archives"
    if not archives.is_dir():
        return []
    nombres: set[str] = set()
    for plan in sorted(p for p in archives.iterdir() if p.is_dir()):
        for documento in ("10-analisis-post-implementacion.md", "00-lecciones-capitalizadas.md",
                          "dependencias-fases.md"):
            ruta = plan / documento
            if not ruta.is_file():
                continue
            nombres.update(NOMBRE_CONTEXT.findall(ruta.read_text(encoding="utf-8", errors="replace")))
    resueltos = []
    for nombre in sorted(nombres):
        candidato = context_dir / f"{nombre}.md"
        if candidato.is_file():
            resueltos.append(candidato)
    return resueltos


def poblacion_del_context(context_dir: Path, plans_dir: Path) -> tuple[list[Path], list[tuple[Path, str]]]:
    """(gobernados, excluidos con razon). La exclusion se publica, no se silencia (L-HF1)."""
    if not context_dir.is_dir():
        return [], []
    en_raiz = sorted(context_dir.glob("CONTEXT-*.md"))
    declarados = [r for r in en_raiz if declara_durable(r)]
    citados = [r for r in citados_por_planes_archivados(plans_dir, context_dir)
               if r not in declarados]
    gobernados = sorted(set(declarados) | set(citados), key=lambda p: p.name)
    excluidos = [(r, EXCLUSION_NO_DECLARA) for r in en_raiz if r not in gobernados]
    for historico in sorted((context_dir / "Historico").glob("CONTEXT-*.md")) if \
            (context_dir / "Historico").is_dir() else []:
        excluidos.append((historico, EXCLUSION_HISTORICO))
    return gobernados, excluidos


def verificar_frescura(context_dir: Path, plans_dir: Path, nb: str, scratch: Path,
                       tope_barrido: int = 0) -> tuple[int, list[str]]:
    """Cada gobernado necesita una fuente publicada cuyos bytes descargados casen con el disco."""
    gobernados, excluidos = poblacion_del_context(context_dir, plans_dir)
    lineas: list[str] = []
    lineas.append(f"poblacion: {len(gobernados)} CONTEXT gobernado(s) "
                  f"({', '.join(g.name for g in gobernados) or '—'}) | "
                  f"{len(excluidos)} excluido(s)")
    for ruta, razon in excluidos:
        lineas.append(f"  [EXCLUIDO] {ruta.name}: {razon}")

    if not gobernados:
        if list(context_dir.glob("CONTEXT-*.md")):
            for ruta in sorted(context_dir.glob("CONTEXT-*.md")):
                lineas.append(f"  [NO-EVALUABLE] {ruta.name}: hay fichero pero no entra en la poblacion")
            lineas.append("[NO-EVALUABLE] frescura de CONTEXT: hay `CONTEXT-*` en la raiz y ninguno "
                          "gobernado (un verde sin candidatos no es un verde)")
            return 2, lineas
        lineas.append("[NO-EVALUABLE] frescura de CONTEXT: no hay CONTEXT-* en la raiz gobernarada")
        return 2, lineas

    fuentes = listar_fuentes(nb)
    lineas.append(f"notebook {NOTEBOOK_TITULO}: {len(fuentes)} fuente(s) publicada(s)")

    salio = 0
    for gobernado in gobernados:
        if not gobernado.is_file():
            # El censo lo nombro y el disco ya no lo tiene: no es rojo del notebook ni verde propio.
            lineas.append(f"  [NO-EVALUABLE] {gobernado.name}: el archivo gobernado ya no existe en "
                          f"{gobernado} (¿movido, borrado o aun no regenerate?)")
            return 2, lineas
        sha_disco = sha256_de(gobernado)
        candidatas = [f for f in fuentes if gobernado.stem in (f["title"] or "")]
        bajadas = list(candidatas)
        barrido_completo = False
        if not any(sha_disco == _hash_bajado(nb, f["id"], scratch, gobernado.stem) for f in bajadas):
            # Ninguna fuente que lo nombra casa: antes de decir VENCIDO se examinan TODAS las fuentes,
            # porque el criterio es byte a byte y un titulo puede no conservar el stem.
            bajadas = list(fuentes)
            barrido_completo = True
        casadas = []
        for fuente in bajadas:
            if fuente["id"] in [c["id"] for c in casadas]:
                continue
            descargado = _hash_bajado(nb, fuente["id"], scratch, gobernado.stem)
            if descargado is None:
                salio = max(salio, 1)
                lineas.append(f"  [SIN-DESCARGA] {fuente['id']} no bajable para {gobernado.name}")
                continue
            if descargado == sha_disco:
                corrobora = "coincide" if fuente["sha_metadata"] == sha_disco else (
                    f"DESACUERDO metadata={fuente['sha_metadata'][:12] or '(ausente)'}")
                casadas.append(dict(fuente, corroboracion=corrobora))
        if casadas:
            lineas.append(f"  [FRESCO] {gobernado.name}: {len(casadas)} fuente(s) que casan por "
                          f"descarga+sha256 "
                          f"({', '.join(c['id'][:13] + '…' + c['corroboracion'] for c in casadas)})"
                          + (" [barrido completo]" if barrido_completo else ""))
            continue
        salio = 1
        lineas.append(f"  [VENCIDO] {gobernado.name}: sha_disco={sha_disco[:12]}… y ninguna de "
                      f"{len(bajadas)} fuente(s) examinada(s) casa "
                      f"({len(candidatas)} la nombran por titulo)"
                      + (" [barrido completo]" if barrido_completo else ""))
    return salio, lineas


_CACHE_BAJADAS: dict[tuple[str, str], str] = {}


def _hash_bajado(nb: str, source_id: str, scratch: Path, stem: str) -> str | None:
    """sha256 de lo que el notebook publica para `source_id`, descargando una sola vez por corrida."""
    clave = (nb, source_id)
    if clave in _CACHE_BAJADAS:
        return _CACHE_BAJADAS[clave]
    destino = scratch / f"{stem}--{source_id}.bin"
    if not descargar(nb, source_id, destino):
        _CACHE_BAJADAS[clave] = None
        return None
    valor = sha256_de(destino)
    _CACHE_BAJADAS[clave] = valor
    destino.unlink(missing_ok=True)
    return valor


def _primera_linea(texto: str) -> str:
    return ((texto or "").strip().splitlines() or ["(sin salida)"])[0][:200]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Frescura de los CONTEXT gobernados contra el notebook QMind (descarga + sha256)")
    ap.add_argument("--nb", default="", help="ID del notebook (por defecto, se resuelve por titulo)")
    ap.add_argument("--context-dir", type=Path, default=DEFAULT_CONTEXT)
    ap.add_argument("--plans-dir", type=Path, default=DEFAULT_PLANS)
    ap.add_argument("--strict", action="store_true",
                    help="sin qmind disponible, corta rojo en vez de WARN + fallback")
    ap.add_argument("--quiet", action="store_true", help="solo la linea de estado")
    args = ap.parse_args(argv)

    lineas: list[str] = []
    try:
        nb = resolver_notebook(args.nb)
        scratch = Path(tempfile.mkdtemp(prefix="verif-context-"))
        try:
            salio, lineas = verificar_frescura(args.context_dir, args.plans_dir, nb, scratch)
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
            _CACHE_BAJADAS.clear()
    except QmindNoDisponible as exc:
        _CACHE_BAJADAS.clear()
        if args.strict:
            print(f"[FAIL] frescura de CONTEXT: {exc}")
            return 1
        print(f"[WARN] frescura de CONTEXT: verificacion no ejecutada — {exc}")
        print("[WARN] fallback del executor (:468) activo; registrar la limitacion en el plan vigente")
        return 0

    if not args.quiet:
        for linea in lineas:
            print(linea)
    estado = "OK" if salio == 0 else ("NO-EVALUABLE" if salio == 2 else "FAIL")
    resumen = [l for l in lineas if l.startswith("  [VENCIDO]")
               or l.startswith("  [SIN-DESCARGA]")]
    print(f"[{estado}] frescura de CONTEXT: {len([l for l in lineas if '[FRESCO]' in l])} fresco(s), "
          f"{len(resumen)} problema(s)")
    return salio


if __name__ == "__main__":
    sys.exit(main())
