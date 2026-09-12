#!/usr/bin/env python3
"""Generador del indice de lecciones del corpus de planes (capa fria del Paso 0).

POR QUE EXISTE (medido, no supuesto)
    El Paso 0 del executor ordena consultar las lecciones de planes anteriores,
    pero el corpus no tenia indice: 24 planes archivados con IDs dispersos
    (`L-VUP-*`, `L-PF*`, `D-T1.*`, `S-C3`...) y ninguna forma barata de saber
    que existe. Consultar cuesta, y lo que cuesta se omite: medido sobre los 34
    analisis archivados, la seccion «Lecciones capitalizadas» aparece en **6**
    (18 %) y la plantilla del executor la marcaba `(si aplica)`. Senal concreta:
    el plan TRIBUNAL-ENFORCEMENT-OBS-2026-09-11 citaba solo a su predecesor, con
    24 planes mas sin consultar.

QUE HACE
    Escanea dos corpus: el de **definiciones** (análisis de plan +
    `.opencode/context/`, que es donde el Paso 0 del executor declara que viven las
    lecciones — medido: `L-SR3` y `L-SR5`, las más citadas del repo con 36 y 34
    menciones, estaban definidas SOLO en un CONTEXT y ningún análisis) y el de
    **citas** (todos los `.md` de ambos directorios). Emite dos artefactos generados:
      - `.opencode/LECCIONES-INDEX.md`    (lectura humana / grep)
      - `.opencode/lecciones_index.json`  (consumo por scripts)
    Cada ID lleva: enunciado, dueño (plan o CONTEXT), sección donde se define,
    cuántas veces y en qué planes se cita, y en qué planes se re-definió.

PROHIBIDO EDITAR A MANO
    Los dos artefactos se regeneran. Un indice mantenido a mano deriva y deja de
    servir como evidencia. `--check` falla si estan vencidos.

Uso:
    python scripts/build_lesson_index.py                  # generar
    python scripts/build_lesson_index.py --check          # verificar frescura
    python scripts/build_lesson_index.py --plans-dir D --context-dir C --out-dir O  # tests

Salida: 0 = ok (o fresco con --check); 1 = vencidos con --check; 2 = error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PLANS = ROOT / ".opencode" / "plans"
DEFAULT_CONTEXT = ROOT / ".opencode" / "context"
DEFAULT_OUT = ROOT / ".opencode"
MD_NAME = "LECCIONES-INDEX.md"
JSON_NAME = "lecciones_index.json"

# Familias indexadas. AC-* queda fuera a proposito: son criterios de aceptacion
# de un plan, no conocimiento durable. NR/R2.x viven en el executor, no aqui.
FAMILIES = ("L", "DA", "D", "S")
FAMILY_LABEL = {
    "L": "Lecciones aprendidas",
    "DA": "Decisiones / reglas de alineación",
    "D": "Deuda, defectos y decisiones registradas",
    "S": "Hallazgos y seguimientos de plan",
}
ID_RE = re.compile(r"\b((?:DA|D|L|S)-[A-Z0-9][A-Za-z0-9._-]*)")
ANALISIS_RE = re.compile(r"^(?:09|10)-.*an[aá]lisis.*\.md$", re.IGNORECASE)
HEADING_RE = re.compile(r"^(#{2,6})\s+(.*)$")
DATE_RE = re.compile(r"(20\d{2}-\d{2}-\d{2})")
MAX_STATEMENT_CHARS = 200
MIN_STATEMENT_CHARS = (
    12  # los enunciados falsos cortos medían 1-8 chars; los largos se caen por `_plausible`
)


def _clean(text: str) -> str:
    """Normaliza un fragmento de tabla o enunciado para publicarlo en el indice."""
    text = text.replace("**", "").replace("`", "")
    text = re.sub(r"\s+", " ", text).strip(" \t:—-,.;")
    return text


def _truncate(text: str) -> str:
    if len(text) <= MAX_STATEMENT_CHARS:
        return text
    cut = text[:MAX_STATEMENT_CHARS]
    return cut[: cut.rfind(" ")].rstrip(" ,;:") + "…"


def _escape(text: str) -> str:
    return text.replace("|", "\\|")


def _sort_key(lesson_id: str):
    """Orden natural: `L-VUP-9` antes que `L-VUP-10`."""
    parts = re.split(r"([0-9]+)", lesson_id)
    return tuple((1, int(p)) if p.isdigit() else (0, p.lower()) for p in parts)


def _plan_of(path: Path, plans_dir: Path) -> str:
    """Nombre del plan dueño = primer segmento bajo `plans_dir` (o `Archives/X`)."""
    rel = path.relative_to(plans_dir)
    if rel.parts and rel.parts[0] == "Archives" and len(rel.parts) > 2:
        return f"Archives/{rel.parts[1]}"
    return rel.parts[0] if len(rel.parts) > 1 else "(raíz)"


def _plan_date(plan: str, files: list[Path]) -> tuple[str, str]:
    """Fecha del plan: la del nombre; si no, la mtime del archivo (aprox)."""
    match = DATE_RE.search(plan)
    if match:
        return match.group(1), "nombre"
    mtimes = [f.stat().st_mtime for f in files]
    if mtimes:
        import datetime

        stamp = datetime.datetime.fromtimestamp(max(mtimes)).date()
        return stamp.isoformat(), "mtime"
    return "0000-00-00", "desconocida"


def _valid_match(match: re.Match, text: str) -> bool:
    """Descarta prefijos incrustados (`AC-D1` no define la familia `D`)."""
    start = match.start()
    return start == 0 or text[start - 1] not in "-_." and not text[start - 1].isalnum()


def _plausible(statement: str) -> bool:
    """Suelo de calidad del enunciado: descarta rangos (`L-PF1+`) y cabos sueltos.

    Medido en la primera corrida del índice: 5 de 248 filas (2 %) capturaron el
    paréntesis de un título (`### Lecciones nuevas de este plan (L-PF1+ — …)`) o
    un `)` huérfano en vez de un enunciado. Esos IDs pasan a «citados sin
    definición», que es donde un ID mal redactado debe verse.
    """
    if len(statement) < MIN_STATEMENT_CHARS or not re.search(r"[A-Za-zÀ-ÿ0-9]", statement):
        return False
    return statement[0] not in "+—–-:)|].,;"


def _extract_definition(line: str, lesson_id: str) -> str | None:
    """Devuelve el enunciado si la linea DEFINICION el ID, o None si solo lo cita.

    Definicion = el ID ocupa la primera celda de una fila de tabla, abre un titulo,
    o abre una linea en negrita seguido de su texto. Una cita inline («ver L-SR5»)
    o un ID entre parentesis en un encabezado no definen.
    """
    escaped = re.escape(lesson_id)
    stripped = line.strip()
    statement = None
    if stripped.startswith("|"):
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) >= 2 and _clean(cells[0]) == lesson_id:
            statement = _clean(" — ".join(c for c in cells[1:3] if c))
    elif HEADING_RE.match(stripped):
        heading = HEADING_RE.match(stripped).group(2)
        match = re.match(r"^\*{0,2}" + escaped + r"\*{0,2}\s*[—:\-–]?\s*(.+)$", heading)
        if match:
            statement = _clean(match.group(1))
    else:
        inline = re.match(r"^[-*]?\s*\*{0,2}" + escaped + r"\*{0,2}\s*[—:\-–]\s*(.+)$", stripped)
        if inline:
            statement = _clean(inline.group(1))
    return statement if statement and _plausible(statement) else None


def _section_at(lines: list[str], index: int) -> str:
    for back in range(index, -1, -1):
        match = HEADING_RE.match(lines[back].strip())
        if match:
            return _clean(match.group(2))
    return "(sin sección)"


def _scan(sources: list[dict]) -> tuple[dict, dict]:
    """Barrido por línea: definiciones (donde pueden definirse) y citas (en todo).

    Un ID no se cuenta como cita de sí mismo: en la línea donde se define, ese ID
    registra definición y no suma cita; los demás IDs de esa misma línea sí.
    """
    definitions: dict[str, list[dict]] = {}
    citations: dict[str, dict] = {}
    for source in sources:
        path, lines = source["path"], source["text"].splitlines()
        owner = source["owner"]
        for i, line in enumerate(lines):
            for match in ID_RE.finditer(line):
                lesson_id = match.group(1).rstrip("._-")
                if not _valid_match(match, line):
                    continue
                statement = _extract_definition(line, lesson_id) if source["defines"] else None
                if statement:
                    definitions.setdefault(lesson_id, []).append(
                        {
                            "plan": owner,
                            "archivo": path.name,
                            "seccion": _section_at(lines, i),
                            "enunciado": statement,
                            "origen": source["origen"],
                        }
                    )
                    continue
                entry = citations.setdefault(lesson_id, {"total": 0, "planes": {}})
                entry["total"] += 1
                entry["planes"][owner] = entry["planes"].get(owner, 0) + 1
    return definitions, citations


def _family_of(lesson_id: str) -> str:
    return "DA" if lesson_id.startswith("DA-") else lesson_id.split("-", 1)[0]


def _sources(plans_dir: Path, context_dir: Path | None) -> tuple[list[dict], dict]:
    """Fuentes etiquetadas + conteos de cobertura.

    Corpus de **definiciones**: los análisis de plan (`09-/10-…análisis…md`, salvo
    `*OBSOLETO*`) y todo `.opencode/context/` — el Paso 0 del executor declara que
    las lecciones viven en esos dos sitios, y medido: `L-SR3`/`L-SR5` (34 y 30
    citas) estaban definidos solo en un CONTEXT.
    Corpus de **citas**: ambos directorios completos.
    """
    stats = {"archivos_analysis": 0, "archivos_contexto": 0, "archivos_md": 0}
    sources: list[dict] = []

    def _add(path: Path, owner: str, origen: str, defines: bool):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return
        sources.append(
            {"path": path, "text": text, "owner": owner, "origen": origen, "defines": defines}
        )
        stats["archivos_md"] += 1

    if plans_dir.is_dir():
        for p in sorted(x for x in plans_dir.rglob("*.md") if x.is_file()):
            owner = _plan_of(p, plans_dir)
            defines = bool(ANALISIS_RE.match(p.name)) and "obsoleto" not in p.name.lower()
            if defines:
                stats["archivos_analysis"] += 1
            _add(p, owner, "plan", defines)

    if context_dir and context_dir.is_dir():
        for p in sorted(x for x in context_dir.rglob("*.md") if x.is_file()):
            stats["archivos_contexto"] += 1
            _add(p, f"context/{p.stem}", "contexto", True)

    return sources, stats


def _owner_dates(sources: list[dict]) -> dict[str, list[Path]]:
    files: dict[str, list[Path]] = {}
    for source in sources:
        files.setdefault(source["owner"], []).append(source["path"])
    return files


def build(plans_dir: Path, context_dir: Path | None = None) -> tuple[dict, dict]:
    """Devuelve (indice, cobertura). Puro: no escribe archivos."""
    sources, stats = _sources(plans_dir, context_dir)
    raw_definitions, citations = _scan(sources)
    owner_files = _owner_dates(sources)

    lessons: dict[str, dict] = {}
    for lesson_id, defs in raw_definitions.items():
        ordered = sorted(
            defs,
            key=lambda d: (
                _plan_date(d["plan"], owner_files.get(d["plan"], []))[0],
                d["plan"],
            ),
        )
        owner = ordered[0]
        fecha, fuente_fecha = _plan_date(owner["plan"], owner_files.get(owner["plan"], []))
        cite = citations.get(lesson_id, {"total": 0, "planes": {}})
        citing = sorted(cite["planes"].items(), key=lambda kv: (-kv[1], kv[0]))
        lessons[lesson_id] = {
            "id": lesson_id,
            "familia": _family_of(lesson_id),
            "enunciado": owner["enunciado"],
            "plan": owner["plan"],
            "origen": owner["origen"],
            "archivo": owner["archivo"],
            "seccion": owner["seccion"],
            "fecha_plan": fecha,
            "fuente_fecha": fuente_fecha,
            "total_citas": cite["total"],
            "planes_que_lo_citan": [p for p, _ in citing if p != owner["plan"]][:6],
            "redefiniciones": [d["plan"] for d in ordered[1:]],
        }

    # IDs que se citan pero nunca se definen en el corpus de definiciones.
    undefined = sorted(
        (
            {
                "id": lesson_id,
                "familia": _family_of(lesson_id),
                "total_citas": cite["total"],
                "planes_que_lo_citan": [
                    p for p, _ in sorted(cite["planes"].items(), key=lambda kv: (-kv[1], kv[0]))
                ][:6],
            }
            for lesson_id, cite in citations.items()
            if lesson_id not in lessons
        ),
        key=lambda e: (-e["total_citas"], _sort_key(e["id"])),
    )

    coverage = {
        "archivos_analysis_escaneados": stats["archivos_analysis"],
        "archivos_contexto_escaneados": stats["archivos_contexto"],
        "archivos_md_escaneados": stats["archivos_md"],
        "ids_con_definicion": len(lessons),
        "ids_citados_sin_definicion": len(undefined),
        "familias_incluidas": list(FAMILIES),
        "familias_excluidas": [
            "AC-* (criterios de aceptación por plan)",
            "NR*/R2.x (reglas del executor, no del corpus)",
        ],
        "exclusiones_nombre": ["*OBSOLETO* fuera del corpus de definiciones"],
    }
    return {"lessons": lessons, "undefined": undefined}, coverage


def render_md(index: dict, coverage: dict) -> str:
    lessons = index["lessons"]
    by_family: dict[str, list[dict]] = {}
    for entry in lessons.values():
        by_family.setdefault(entry["familia"], []).append(entry)

    lines = [
        "# Índice de Lecciones — corpus de planes iah-cli",
        "",
        "> **Artefacto generado. NO editar a mano.** Regenerar con",
        "> `python scripts/build_lesson_index.py` (se ejecuta en FASE-RELEASE, tras el",
        "> write-back de QMind y antes de archivar el plan).",
        "",
        "**Para qué sirve**: es la capa fría del Paso 0 de",
        "`.agents/workflows/phased_project_executor.md`. Antes de diseñar un plan,",
        "`grep`-ear este archivo por módulo, síntoma o palabra clave responde la",
        "pregunta cara: *¿este error ya se resolvió antes, y con qué lección?*",
        "Cada fila apunta al plan dueño, que tiene el texto completo.",
        "",
        "## Cobertura medida (lo que este índice NO garantiza)",
        "",
        f"- Corpus de **definiciones**: `{coverage['archivos_analysis_escaneados']}` análisis de "
        f"plan + `{coverage['archivos_contexto_escaneados']}` archivos de `.opencode/context/`. "
        f"`{coverage['archivos_md_escaneados']}` `.md` en total como corpus de **citas**.",
        f"- {coverage['ids_con_definicion']} IDs con definición detectada; "
        f"{coverage['ids_citados_sin_definicion']} IDs citados sin definición (ver última sección).",
        f"- Familias incluidas: {', '.join(f'`{f}-*`' for f in coverage['familias_incluidas'])}.",
        *[f"- Excluida a propósito: {e}" for e in coverage["familias_excluidas"]],
        f"- {coverage['exclusiones_nombre'][0]}.",
        "- **Una fila no prueba que la lección sea pertinente al plan que la consulta.**",
        "  El índice elimina el costo de mirar; decidir qué capitalizar sigue siendo del",
        "  autor del plan, y se registra en `00-lecciones-capitalizadas.md`.",
        "- Detecta definiciones por convención de formato (ID en la primera celda de una",
        "  tabla, o encabezando un título/línea en negrita). Una lección redactada fuera",
        "  de esa convención aparece como «citada sin definición», no se pierde.",
        "",
        "## Sumario",
        "",
        "| Familia | Significado | IDs |",
        "|---------|-------------|-----|",
    ]
    for family in FAMILIES:
        entries = by_family.get(family, [])
        lines.append(f"| `{family}-*` | {FAMILY_LABEL[family]} | {len(entries)} |")
    lines.append(f"| — | Citados sin definición | {len(index['undefined'])} |")

    for family in FAMILIES:
        entries = sorted(by_family.get(family, []), key=lambda e: _sort_key(e["id"]))
        if not entries:
            continue
        lines += [
            "",
            f"## `{family}-*` — {FAMILY_LABEL[family]} ({len(entries)})",
            "",
            "| ID | Enunciado | Plan dueño | Sección | Citas |",
            "|----|-----------|------------|---------|-------|",
        ]
        for e in entries:
            if e["planes_que_lo_citan"]:
                cited = f"{e['total_citas']} en " + ", ".join(e["planes_que_lo_citan"][:3])
            else:
                cited = f"{e['total_citas']} (solo el plan dueño)"
            extra = f" (+{len(e['redefiniciones'])} redefiniciones)" if e["redefiniciones"] else ""
            lines.append(
                f"| `{e['id']}` | {_escape(_truncate(e['enunciado']))}{extra} "
                f"| {e['plan']} | {_escape(e['seccion'])} "
                f"| {cited} |"
            )

    undefined = index["undefined"]
    lines += [
        "",
        f"## Citados sin definición ({len(undefined)})",
        "",
        "> Señal accionable: el ID circula por los planes pero nadie lo redactó con la",
        "> convención de definición. O está mal formulado, o la lección nunca se escribió.",
        "",
        "| ID | Citas | Dónde se cita |",
        "|----|-------|---------------|",
    ]
    for e in undefined[:60]:
        lines.append(
            f"| `{e['id']}` | {e['total_citas']} | {', '.join(e['planes_que_lo_citan']) or '—'} |"
        )
    if len(undefined) > 60:
        lines.append(f"| … | +{len(undefined) - 60} más en el JSON | |")
    lines.append("")
    return "\n".join(lines)


def render_json(index: dict, coverage: dict) -> str:
    payload = {
        "_generated_by": "scripts/build_lesson_index.py",
        "_notice": "Artefacto generado: no editar a mano. Ejecutar el script para actualizar.",
        "cobertura": coverage,
        "lecciones": [index["lessons"][k] for k in sorted(index["lessons"], key=_sort_key)],
        "citados_sin_definicion": index["undefined"],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def _is_stale(path: Path, content: str) -> bool:
    return (not path.exists()) or path.read_text(encoding="utf-8") != content


def _visible(path: Path) -> str:
    """Ruta relativa al repo cuando existe tal relación; absoluta si no."""
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera el índice de lecciones del corpus")
    parser.add_argument("--plans-dir", type=Path, default=DEFAULT_PLANS)
    parser.add_argument("--context-dir", type=Path, default=DEFAULT_CONTEXT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true", help="no escribe; falla si está vencido")
    args = parser.parse_args()

    if not args.plans_dir.is_dir():
        print(f"[2] el directorio de planes no existe: {args.plans_dir}")
        return 2

    index, coverage = build(args.plans_dir, args.context_dir)
    md = render_md(index, coverage)
    js = render_json(index, coverage)
    md_path = args.out_dir / MD_NAME
    json_path = args.out_dir / JSON_NAME

    if args.check:
        stale = [p.name for p, c in ((md_path, md), (json_path, js)) if _is_stale(p, c)]
        if stale:
            print(f"[FAIL] Índice de lecciones vencido: {', '.join(stale)}")
            print("Regenera: python scripts/build_lesson_index.py")
            return 1
        print(f"[OK] Índice de lecciones fresco ({coverage['ids_con_definicion']} IDs)")
        return 0

    args.out_dir.mkdir(parents=True, exist_ok=True)
    md_path.write_text(md, encoding="utf-8", newline="\n")
    json_path.write_text(js, encoding="utf-8", newline="\n")
    print(
        f"[OK] {coverage['ids_con_definicion']} IDs definidos + "
        f"{coverage['ids_citados_sin_definicion']} sin definición "
        f"({coverage['archivos_analysis_escaneados']} análisis, "
        f"{coverage['archivos_md_escaneados']} .md citados)"
    )
    print(f"  -> {_visible(md_path)}")
    print(f"  -> {_visible(json_path)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
