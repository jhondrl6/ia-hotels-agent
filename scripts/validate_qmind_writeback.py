#!/usr/bin/env python3
"""
IA Hoteles Agent - QMind Write-back Validator
=============================================
Materializa el contrato de write-back del executor
(`.agents/workflows/phased_project_executor.md` v2.20.0):

- :572-574 — al cierre de cada fase, el `10-analisis-post-implementacion.md`
  actualizado se re-ingiere al notebook QMind `iah-cli-lecciones`.
- :588    — QMind indexa snapshots de contenido, no rutas; archivar NO requiere
  acción en QMind; re-ingerir SOLO si cambia el contenido.

Este validador comprueba, contra el notebook real (vía CLI `qmind source list`,
no contra un manifest manual), que todo plan archivado en
`.opencode/plans/Archives/` que tenga `10-analisis-post-implementacion.md`
tiene al menos una fuente ingesta cuyo título lo identifique.

Reemplaza la confianza en que la sesión recuerde el write-back (el punto de
fallo histórico del ciclo de capitalización de lecciones).

Uso:
    python scripts/validate_qmind_writeback.py             # verifica
    python scripts/validate_qmind_writeback.py --nb <ID>   # fuerza notebook
    python scripts/validate_qmind_writeback.py --strict    # falla si qmind no está disponible
    python scripts/validate_qmind_writeback.py --upload TRIBUNAL-OFFLINE-2026-09-09
        # write-back: sube 10-analisis + CONTEXT con declaración durable
    python scripts/validate_qmind_writeback.py --upload C:/ruta/al/plan
        # write-back con ruta absoluta

Códigos de salida:
    0 — todo 10-analisis archivado está ingestado; o qmind indisponible
        (fallback del executor :468: registrar limitación y continuar; con
        --strict este caso también falla)
    1 — qmind disponible y al menos un 10-analisis archivado NO está ingestado
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
ARCHIVES_DIR = ROOT_DIR / ".opencode" / "plans" / "Archives"
ANALISIS_FILENAME = "10-analisis-post-implementacion.md"
NOTEBOOK_TITLE = "iah-cli-lecciones"
TRAILING_DATE = re.compile(r"-\d{4}-\d{2}-\d{2}$")
CONTEXT_DIR = ROOT_DIR / ".opencode" / "context"
CONTEXT_DECLARATION_MARKERS = [
    re.compile(r"^Lección de forma:", re.MULTILINE),
    re.compile(r"^Lección durable:", re.MULTILINE),
    re.compile(r"^Lecciones capitalizadas", re.MULTILINE),
]


def norm(value: str) -> str:
    return unicodedata.normalize("NFC", value).strip()


def collect_archived_analisis() -> list:
    """Retorna [(plan_dir_name, ruta_al_10_analisis)] de los planes archivados."""
    if not ARCHIVES_DIR.is_dir():
        return []
    results = []
    for plan_dir in sorted(ARCHIVES_DIR.iterdir()):
        if not plan_dir.is_dir():
            continue
        analisis = plan_dir / ANALISIS_FILENAME
        if analisis.is_file():
            results.append((plan_dir.name, analisis))
    return results


def resolve_notebook_id(explicit: str) -> str:
    """Resuelve el ID del notebook: argumento explícito o búsqueda por título."""
    if explicit:
        return explicit
    exit_code, output = _run_qmind(["notebook", "list", "--format", "json"])
    if exit_code != 0:
        raise QmindUnavailable(f"qmind notebook list falló: {_first_line(output)}")
    data = json.loads(output)
    notebooks = data.get("notebooks", data if isinstance(data, list) else [])
    matches = [nb for nb in notebooks if norm(nb.get("title", "")) == NOTEBOOK_TITLE]
    if not matches:
        raise QmindUnavailable(
            f"No se encontró el notebook '{NOTEBOOK_TITLE}' en la cuenta (fallback :468)"
        )
    return matches[0]["id"]


class QmindUnavailable(RuntimeError):
    """qmind CLI ausente, sin auth, o notebook no encontrado."""


def _qmind_exe() -> str:
    """Resuelve la ruta del CLI. En Windows npm instala qmind.CMD, que CreateProcess
    no puede ejecutar por nombre corto ('qmind' sin extensión) — hay que pasar la ruta resuelta."""
    exe = shutil.which("qmind")
    if exe is None:
        raise QmindUnavailable("CLI 'qmind' no está instalado ni en PATH")
    return exe


def _run_qmind(args: list) -> tuple:
    try:
        result = subprocess.run(
            [_qmind_exe(), *args], capture_output=True,
            encoding="utf-8", errors="replace", timeout=120
        )
        return result.returncode, result.stdout + result.stderr
    except FileNotFoundError:
        raise QmindUnavailable("CLI 'qmind' no está instalado ni en PATH")
    except subprocess.TimeoutExpired:
        raise QmindUnavailable("qmind no respondió (timeout 120s)")


def fetch_source_titles(notebook_id: str) -> list:
    exit_code, output = _run_qmind(
        ["source", "list", "--nb", notebook_id, "--all", "--format", "json"]
    )
    if exit_code != 0:
        raise QmindUnavailable(f"qmind source list falló: {_first_line(output)}")
    data = json.loads(output)
    items = data if isinstance(data, list) else data.get("sources", data.get("items", []))
    return [norm(s.get("title", "")) for s in items]


def is_ingested(plan_dir_name: str, titles: list) -> bool:
    """Un plan está ingestado si hay fuente '10-analisis' que lo nombre.

    Los títulos en el notebook siguen los patrones:
      '10-analisis: <PLAN> (lecciones aprendidas...)'
      '<PLAN> 10-analisis-post-implementacion (...)'
    El stem (nombre del directorio sin fecha final) cubre variantes de título
    como 'VALIDADOR-URL-PROPIA 10-analisis-post-implementacion'.
    """
    stem = TRAILING_DATE.sub("", plan_dir_name)
    for title in titles:
        if "10-analisis" not in title:
            continue
        if plan_dir_name in title or stem in title:
            return True
    return False


def _first_line(text: str) -> str:
    return (text.strip().splitlines() or ["(sin salida)"])[0][:200]


def upload_source(notebook_id: str, file_path: Path, title: str) -> tuple:
    """Ejecuta `qmind source upload`. Retorna (exit_code, output)."""
    exit_code, output = _run_qmind([
        "source", "upload",
        "--nb", notebook_id,
        "--file", str(file_path),
        "--title", title,
    ])
    return exit_code, output


def scan_context_declarations() -> list:
    """Retorna [(ruta, título)] de CONTEXT files en .opencode/context/ que
    autodeclaren una lección durable (executor :577-583)."""
    if not CONTEXT_DIR.is_dir():
        return []
    results = []
    for ctx_file in sorted(CONTEXT_DIR.glob("CONTEXT-*.md")):
        content = ctx_file.read_text(encoding="utf-8", errors="replace")
        if any(marker.search(content) for marker in CONTEXT_DECLARATION_MARKERS):
            title = f"CONTEXT: {ctx_file.stem}"
            results.append((ctx_file, title))
    return results


def do_upload(plan_dir: Path, notebook_id: str, strict: bool) -> int:
    """Write-back de un plan: sube el 10-analisis y los CONTEXT con declaración durable."""
    if not plan_dir.is_dir():
        print(f"[FAIL] Upload: el directorio no existe: {plan_dir}")
        return 1

    analisis = plan_dir / ANALISIS_FILENAME
    if not analisis.is_file():
        print(f"[FAIL] Upload: {ANALISIS_FILENAME} no existe en {plan_dir}")
        return 1

    try:
        titles = fetch_source_titles(notebook_id)
    except QmindUnavailable as exc:
        print(f"[FAIL] Upload: {exc}")
        return 1

    plan_name = plan_dir.name
    uploaded = 0
    skipped = 0
    failed = 0

    analisis_title = f"10-analisis: {plan_name} (lecciones aprendidas y decisiones)"
    if is_ingested(plan_name, titles):
        print(f"[SKIP] {analisis_title} — ya está ingestado (evitando duplicado, executor :584)")
        skipped += 1
    else:
        print(f"[UP] {analisis_title}")
        code, out = upload_source(notebook_id, analisis, analisis_title)
        if code != 0:
            print(f"[FAIL] Upload falló: {_first_line(out)}")
            failed += 1
        else:
            print(f"[OK] Subido: {analisis.stem}")
            uploaded += 1

    context_files = scan_context_declarations()
    for ctx_path, ctx_title in context_files:
        if norm(ctx_title) in titles:
            print(f"[SKIP] {ctx_title} — ya está ingestado")
            skipped += 1
            continue
        print(f"[UP] {ctx_title}")
        code, out = upload_source(notebook_id, ctx_path, ctx_title)
        if code != 0:
            print(f"[FAIL] Upload falló: {_first_line(out)}")
            failed += 1
        else:
            print(f"[OK] Subido: {ctx_path.name}")
            uploaded += 1

    print(f"\n[RESUMEN] upload={uploaded} skip={skipped} fail={failed}")
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida el write-back QMind de los 10-analisis de planes archivados"
    )
    parser.add_argument("--nb", default="", help="ID del notebook (default: buscar 'iah-cli-lecciones')")
    parser.add_argument(
        "--strict", action="store_true",
        help="Falla también cuando qmind no está disponible (en vez de WARN + fallback :468)"
    )
    parser.add_argument(
        "--upload", metavar="PLAN_DIR",
        help="Write-back: sube el 10-analisis y CONTEXT con declaración durable del plan indicado"
    )
    args = parser.parse_args()

    if args.upload:
        try:
            notebook_id = resolve_notebook_id(args.nb)
        except QmindUnavailable as exc:
            print(f"[FAIL] Upload: {exc}")
            return 1
        plan_dir = Path(args.upload)
        if not plan_dir.is_absolute():
            plan_dir = (ROOT_DIR / ".opencode" / "plans" / plan_dir).resolve()
        return do_upload(plan_dir, notebook_id, args.strict)

    archived = collect_archived_analisis()
    if not archived:
        print(f"[PASS] QMind Write-back: sin planes archivados con {ANALISIS_FILENAME}, nada que validar")
        return 0

    try:
        notebook_id = resolve_notebook_id(args.nb)
        titles = fetch_source_titles(notebook_id)
    except QmindUnavailable as exc:
        if args.strict:
            print(f"[FAIL] QMind Write-back: {exc}")
            return 1
        print(f"[WARN] QMind Write-back: verificación no ejecutada — {exc}")
        print(f"[WARN] Fallback executor :468 activo; registrar la limitación en dependencias-fases.md")
        return 0

    missing = [name for name, _ in archived if not is_ingested(name, titles)]

    if missing:
        print(f"[FAIL] QMind Write-back: {len(missing)} de {len(archived)} 10-analisis archivados sin ingesta")
        for name in missing:
            print(f"- {name}: sin fuente '10-analisis' en el notebook '{NOTEBOOK_TITLE}'")
        print("Fix: qmind source upload --nb <ID> --file <10-analisis> --title '10-analisis: <PLAN> (lecciones aprendidas)'")
        print("Contexto: .opencode/context/QMIND-RECOVERY-MANIFEST.md / executor :572-574")
        return 1

    print(f"[PASS] QMind Write-back: {len(archived)}/{len(archived)} 10-analisis archivados ingested en '{NOTEBOOK_TITLE}'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
