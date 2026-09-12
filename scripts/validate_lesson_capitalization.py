#!/usr/bin/env python3
"""Verificador de capitalización del Paso 0 (`00-lecciones-capitalizadas.md`).

Materializa como mecánico lo que el Paso 0 del executor (`phased_project_executor.md`
v2.22.0) ordena en prosa: antes de diseñar un plan se consulta el corpus y el resultado
se registra en un artefacto con consultas literales, lecciones con dueño, descartes
motivados y cobertura declarada.

POR QUÉ EXISTE (medido, no supuesto)
    El artefacto nació con v2.22.0 y su cumplimiento seguía dependiendo de la disciplina
    de quien escribe (L-R.4). Medido el 2026-09-12 con los comandos de
    `.opencode/plans/PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12/00-lecciones-capitalizadas.md`
    §1: **1** archivo `00-` sobre **26** planes del repo = **3,8 %** de cobertura de la
    regla. La señal que originó el tramo de deuda fue un plan que citaba **solo** a su
    predecesor teniendo 24 planes más en el corpus, con un defecto ya documentado en otro
    plan desde julio. Y un `✅` sin denominador es L-R.3 (cobertura medida del 12,5 % en
    `validate_plan_closure.py`): por eso este script publica a cuántos planes miró.

QUÉ VERIFICA (forma y trazabilidad; ocho checks, contrato en §3 del plan maestro)
    C0  toda corrida imprime la población mirada y los exentos, con su motivo
    C1  el artefacto existe y se lee
    C2  tiene §1, §2, §3 y §4
    C3  ≥1 consulta dirigida a una capa corpus-wide, con el comando entre backticks
    C4  ≥1 fila de §2 nombra un AC (`AC-F1` o `AC8`) que **existe** en la tabla del maestro
    C5  ≥3 candidatos descartados con motivo
    C6  §4 nombra a este verificador **y** declara un límite
    C7  cada ID de §2 está definido en el corpus y su dueño real aparece en «Definida en»
    C8  los dueños de §2 cubren ≥2 planes o CONTEXTs distintos (anti «solo el predecesor»)

LÍMITE DECLARADO (L-R.4 — no verifico, y lo digo)
    **No verifico la pertinencia.** Este script comprueba forma y trazabilidad: que el
    artefacto tiene la estructura exigida, que los ACs nombrados existen y que los IDs
    citados son reales y están bien atribuidos. **No puede saber** si la lección que debía
    capitalizarse es otra, ni si el efecto alegado en «qué cambia» es verdadero o un AC
    cosmético escrito para satisfacer C4. Un `[OK]` de este script significa «la forma
    exigida está», nunca «capitalicé bien».

    Segundo límite, de alcance: un plan cuyo nombre no lleve fecha `YYYY-MM-DD` no puede
    clasificarse contra el corte y queda **exento**, pero se lista por su nombre en la
    salida para que la exención no sea muda.

ESTADOS (R2.9 — el verificador es él mismo un lector de artefactos)
    `SIN-HALLAZGOS` lo leyó y no encontró violación · `AUSENTE` no había nada que leer
    (dice la ruta buscada) · `LECTOR-FALLIDO` no pudo operar (dice el motivo). Ningún
    verde sale del tercero: si el maestro no tiene tabla de ACs parseable o el índice no
    puede calcularse, eso **es** la violación, no un `[OK]`.

PROHIBIDO AUTO-ARREGLAR: este script reporta. No reescribe el `00-` de nadie, porque la
    capitalización es una decisión de quien diseña el plan y un auto-fix fabricaría la
    apariencia del requisito sin el requisito (patrón de `validate_plan_closure.py`).

Fuente de verdad de C7/C8: el índice se calcula **en memoria** con
`build_lesson_index.build()` (0,30 s medidos sobre 346 `.md`), no se lee
`.opencode/lecciones_index.json`: ese JSON es la salida de otro gate (el hook comprueba su
frescura), y fiarle la conclusión al artefacto de otro verificador es tener un verde prestado.

Uso:
    python scripts/validate_lesson_capitalization.py                      # verificar
    python scripts/validate_lesson_capitalization.py --cutoff 2026-09-11  # medir el corpus histórico
    python scripts/validate_lesson_capitalization.py --plans-dir D --context-dir C   # (tests)
    python scripts/validate_lesson_capitalization.py --quiet              # solo el resumen

Salida: 0 = sin violaciones; 1 = violaciones; 2 = error de uso o de estado.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PLANS = ROOT / ".opencode" / "plans"
DEFAULT_CONTEXT = ROOT / ".opencode" / "context"

ARTIFACTO = "00-lecciones-capitalizadas.md"
MAESTRO = "01-plan-maestro.md"
VERIFICADOR = "validate_lesson_capitalization.py"

# Executor v2.22.0 (2026-09-12) es la versión que convirtió el Paso 0 en artefacto. Antes
# de esa fecha ningún plan pudo tenerlo: exigirlos sería ruido permanente (L-HF1).
CUTOFF_DATE = date(2026, 9, 12)

MIN_DESCARTES = 3
MIN_DUENOS = 2

# Capas que, por construcción, miran al corpus completo y no a un solo plan.
CORPUS_WIDE = ("índice", "indice", "lecciones-index", "qmind", "notebook", "memoria", "repo")
LIMIT_PHRASES = ("no verific", "no comprueba", "no garantiza", "no puede saber")

LESSON_ID_RE = re.compile(r"^(?:DA|D|L|S)-[A-Z0-9][A-Za-z0-9._-]*$")
# Dos formas vivas en el repo: `AC-F1` (plantilla actual) y `AC8` (planes predecesores).
# Exigir una sola convertiría el check en un candado de forma que falla a quien escribe
# bien (L-B1); los bordes de palabra evitan leer un `MACRO2` como AC.
AC_TOKEN_RE = re.compile(r"\bAC-?[A-Z]{0,2}\d+\b")
DATE_RE = re.compile(r"(?<!\d)(20\d{2})-(\d{2})-(\d{2})(?!\d)")
SEP_ROW_RE = re.compile(r"^\s*\|[\s|:-]+\|\s*$")


def _limpiar(texto: str) -> str:
    """Celda de markdown a texto comparable, **conservando los backticks**.

    Los backticks se conservan a propósito: en el template marcan que la consulta es
    copy-pasteable, y esa marca es justo lo que C3 necesita distinguir de «revisé las
    lecciones». Las negritas sí se quitan porque solo decoran.
    """
    out = texto.replace("\\|", "|").replace("**", "")
    return re.sub(r"\s+", " ", out).strip(" \t:—-,.;")


def _celdas(linea: str) -> list[str]:
    """Una fila de tabla en celdas limpias, respetando las barras verticales escapadas."""
    return [_limpiar(c) for c in re.split(r"(?<!\\)\|", linea.strip().strip("|"))]


@dataclass
class Violacion:
    check: str
    estado: str
    mensaje: str

    def __str__(self) -> str:
        return f"[{self.check}/{self.estado}] {self.mensaje}"


# --------------------------------------------------------------------------- alcance


def _fecha_del_plan(nombre: str) -> date | None:
    """Fecha del plan tomada de su nombre (convención `<NOMBRE>-YYYY-MM-DD`)."""
    mejor = None
    for anio, mes, dia in DATE_RE.findall(nombre):
        try:
            candidato = date(int(anio), int(mes), int(dia))
        except ValueError:
            continue
        if mejor is None or candidato > mejor:
            mejor = candidato
    return mejor


def clasificar_planes(plans_dir: Path, cutoff: date) -> dict[str, list[Path]]:
    """Reparto del corpus en los grupos que la salida de C0 publica."""
    grupos: dict[str, list[Path]] = {
        "alcance": [],
        "exento_fecha": [],
        "sin_fecha": [],
        "archivados": [],
    }
    for hijo in sorted(p for p in plans_dir.iterdir() if p.is_dir()):
        if hijo.name == "Archives":
            grupos["archivados"] = sorted(p for p in hijo.iterdir() if p.is_dir())
            continue
        fecha = _fecha_del_plan(hijo.name)
        if fecha is None:
            grupos["sin_fecha"].append(hijo)
        elif fecha >= cutoff:
            grupos["alcance"].append(hijo)
        else:
            grupos["exento_fecha"].append(hijo)
    return grupos


# ------------------------------------------------------------------ lectura de archivos


def _leer(ruta: Path) -> tuple[str | None, str]:
    try:
        return ruta.read_text(encoding="utf-8"), ""
    except (OSError, UnicodeDecodeError) as exc:
        return None, f"{type(exc).__name__}: {exc}"


def _seccion(texto: str, numero: str) -> str | None:
    """Cuerpo de `## N. …` hasta el siguiente `## `. No confunde `## 3.` con `## 3.b`."""
    cabecera = re.search(rf"^##\s*{numero}\.\s.*$", texto, re.MULTILINE)
    if not cabecera:
        return None
    resto = texto[cabecera.end() :]
    siguiente = re.search(r"^##\s", resto, re.MULTILINE)
    return resto[: siguiente.start()] if siguiente else resto


def _filas(seccion: str) -> list[list[str]]:
    """Filas de la primera tabla de la sección; la posición 0 es la cabecera."""
    filas = []
    for linea in seccion.splitlines():
        if not linea.strip().startswith("|") or SEP_ROW_RE.match(linea.strip()):
            continue
        filas.append(_celdas(linea))
    return filas


def _columna(fila_cabecera: list[str], *claves: str) -> int | None:
    for i, celda in enumerate(fila_cabecera):
        if any(clave.lower() in celda.lower() for clave in claves):
            return i
    return None


def duenos_del_corpus(plans_dir: Path, context_dir: Path) -> tuple[dict[str, str] | None, str]:
    """`{ID: plan dueño}` según el corpus de definiciones, calculado en memoria."""
    if str(Path(__file__).resolve().parent) not in sys.path:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        from build_lesson_index import build  # noqa: PLC0415 — mismo directorio, sin paquete
    except ImportError as exc:
        return None, f"no se pudo importar build_lesson_index: {exc}"
    try:
        indice, _ = build(plans_dir, context_dir)
    except Exception as exc:  # R2.9: el lector caído se declara, nunca se lee como ausencia
        return None, f"build_lesson_index.build() lanzo {type(exc).__name__}: {exc}"
    return {lid: e["plan"] for lid, e in indice["lessons"].items()}, ""


def acs_del_maestro(plan: Path) -> tuple[set[str] | None, str]:
    """IDs de AC declarados en las tablas del plan maestro. `(None, motivo)` si no es legible."""
    ruta = plan / MAESTRO
    if not ruta.exists():
        return None, f"AUSENTE: no existe {MAESTRO} en {plan.name}"
    texto, error = _leer(ruta)
    if texto is None:
        return None, f"no se pudo leer {MAESTRO}: {error}"
    acs: set[str] = set()
    for linea in texto.splitlines():
        if not linea.strip().startswith("|") or SEP_ROW_RE.match(linea.strip()):
            continue
        acs.update(AC_TOKEN_RE.findall(_celdas(linea)[0]))
    if not acs:
        return None, f"no se encontró ninguna tabla de ACs en {MAESTRO}"
    return acs, ""


# ------------------------------------------------------------------------- los checks


def c2_secciones(rel: str, texto: str) -> tuple[list[Violacion], dict[str, str | None]]:
    violaciones = []
    secciones: dict[str, str | None] = {}
    for numero in ("1", "2", "3", "4"):
        secciones[numero] = _seccion(texto, numero)
        if secciones[numero] is None:
            violaciones.append(
                Violacion(
                    "C2",
                    "SIN-HALLAZGOS",
                    f"{rel}: falta la sección «## {numero}.» exigida por el template",
                )
            )
    return violaciones, secciones


def c3_consulta_al_corpus(rel: str, seccion: str | None) -> list[Violacion]:
    if seccion is None:
        return [
            Violacion(
                "C3", "LECTOR-FALLIDO", f"{rel}: sin §1 no se puede evaluar la consulta al corpus"
            )
        ]
    filas = _filas(seccion)
    if len(filas) < 2:
        return [
            Violacion(
                "C3",
                "LECTOR-FALLIDO",
                f"{rel}: §1 no tiene una tabla con cabecera y filas de datos",
            )
        ]
    capa = _columna(filas[0], "capa")
    consulta = _columna(filas[0], "consulta")
    if capa is None or consulta is None:
        return [
            Violacion(
                "C3",
                "LECTOR-FALLIDO",
                f"{rel}: la tabla de §1 necesita las columnas «Capa» y «Consulta literal» "
                f"(leída: {filas[0]})",
            )
        ]
    for fila in filas[1:]:
        if max(capa, consulta) >= len(fila):
            continue
        if any(t in fila[capa].lower() for t in CORPUS_WIDE) and "`" in fila[consulta]:
            return []
    return [
        Violacion(
            "C3",
            "SIN-HALLAZGOS",
            f"{rel}: ninguna consulta de §1 mira a una capa corpus-wide (índice generado, QMind, "
            "memoria o repo) con su comando entre backticks. Consultar solo al predecesor es la "
            "señal que este check existe para cazar.",
        )
    ]


def c4_ac_existente(
    rel: str, seccion: str | None, acs: set[str] | None, motivo: str
) -> list[Violacion]:
    if seccion is None:
        return [
            Violacion(
                "C4", "LECTOR-FALLIDO", f"{rel}: sin §2 no se puede evaluar la anti-ceremonia"
            )
        ]
    if acs is None:
        return [
            Violacion(
                "C4", "LECTOR-FALLIDO", f"{rel}: {motivo}; sin ACs legibles C4 no puede dar OK"
            )
        ]
    filas = _filas(seccion)
    if len(filas) < 2:
        return [
            Violacion(
                "C4", "SIN-HALLAZGOS", f"{rel}: §2 no tiene ninguna fila de lección capitalizada"
            )
        ]
    cambia = _columna(filas[0], "qué cambia", "que cambia")
    aplica = _columna(filas[0], "dónde se aplica", "donde se aplica")
    if cambia is None:
        return [
            Violacion(
                "C4",
                "LECTOR-FALLIDO",
                f"{rel}: la tabla de §2 necesita la columna «Qué cambia en ESTE plan» "
                f"(leída: {filas[0]})",
            )
        ]
    prometidos: set[str] = set()
    for fila in filas[1:]:
        leidas = [fila[i] for i in (cambia, aplica) if i is not None and i < len(fila)]
        prometidos.update(AC_TOKEN_RE.findall(" ".join(leidas)))
    if not prometidos:
        return [
            Violacion(
                "C4",
                "SIN-HALLAZGOS",
                f"{rel}: ninguna fila de §2 nombra un AC en «Qué cambia» o «Dónde se aplica». Una "
                "lección sin artefacto afectado citó, pero no capitalizó.",
            )
        ]
    if prometidos & acs:
        return []
    return [
        Violacion(
            "C4",
            "SIN-HALLAZGOS",
            f"{rel}: los ACs nombrados en §2 ({', '.join(sorted(prometidos))}) no existen en la "
            f"tabla de ACs de {MAESTRO} ({len(acs)} declarados). Un AC inventado para rellenar la "
            "fila es la ceremonia que este check busca.",
        )
    ]


def c5_descartes(rel: str, seccion: str | None) -> list[Violacion]:
    if seccion is None:
        return [
            Violacion("C5", "LECTOR-FALLIDO", f"{rel}: sin §3 no se pueden contar los descartes")
        ]
    filas = _filas(seccion)
    datos = [f for f in filas[1:] if any(c for c in f)]
    if len(datos) >= MIN_DESCARTES:
        return []
    return [
        Violacion(
            "C5",
            "SIN-HALLAZGOS",
            f"{rel}: §3 tiene {len(datos)} descartes y la regla exige ≥{MIN_DESCARTES}. Descartar "
            "con motivo es la única prueba de que se miró el corpus.",
        )
    ]


def c6_cobertura_declarada(rel: str, seccion: str | None) -> list[Violacion]:
    if seccion is None:
        return [Violacion("C6", "LECTOR-FALLIDO", f"{rel}: sin §4 no hay declaración de cobertura")]
    bajo = seccion.lower()
    faltan = []
    if VERIFICADOR not in seccion:
        faltan.append(f"nombrar al verificador que lo guarda ({VERIFICADOR})")
    if not any(f in bajo for f in LIMIT_PHRASES):
        faltan.append(
            "declarar su límite con una frase de las formas «no verifico…», «no comprueba…» o "
            "«no garantiza…»"
        )
    if not faltan:
        return []
    return [
        Violacion(
            "C6",
            "SIN-HALLAZGOS",
            f"{rel}: §4 debe {' y '.join(faltan)}. Una norma sin check solo es publicable si lo "
            "declara (L-R.4), y un límite que no se actualiza cuando el check llega es L-NC10.",
        )
    ]


def c7_c8_atribucion(
    rel: str, seccion: str | None, owners: dict[str, str] | None, indice_motivo: str
) -> tuple[list[Violacion], list[str]]:
    if seccion is None:
        return [
            Violacion("C7", "LECTOR-FALLIDO", f"{rel}: sin §2 no hay atribuciones que verificar")
        ], []
    if owners is None:
        return [Violacion("C7", "LECTOR-FALLIDO", f"{rel}: {indice_motivo}")], []
    filas = _filas(seccion)
    if len(filas) < 2:
        return [Violacion("C7", "SIN-HALLAZGOS", f"{rel}: §2 sin filas de lección")], []
    definida = _columna(filas[0], "definida en", "definida")
    if definida is None:
        return [
            Violacion(
                "C7",
                "LECTOR-FALLIDO",
                f"{rel}: la tabla de §2 necesita la columna «Definida en» (leída: {filas[0]})",
            )
        ], []
    violaciones: list[Violacion] = []
    duenos: set[str] = set()
    for fila in filas[1:]:
        if not fila or not fila[0]:
            continue
        lid = fila[0].strip().strip("`")
        if not LESSON_ID_RE.match(lid):
            violaciones.append(
                Violacion(
                    "C7",
                    "SIN-HALLAZGOS",
                    f"{rel}: la primera celda de una fila de §2 debe ser un ID del corpus "
                    f"(L-*, DA-*, D-*, S-*) y se leyó «{lid}»",
                )
            )
            continue
        dueno = owners.get(lid)
        if dueno is None:
            violaciones.append(
                Violacion(
                    "C7",
                    "SIN-HALLAZGOS",
                    f"{rel}: {lid} no está definido en el corpus de definiciones (los "
                    "análisis de plan y .opencode/context/). O está mal escrito o la "
                    "lección nunca se redactó.",
                )
            )
            continue
        duenos.add(dueno)
        publicada = fila[definida] if definida < len(fila) else ""
        if dueno not in publicada:
            violaciones.append(
                Violacion(
                    "C7",
                    "SIN-HALLAZGOS",
                    f"{rel}: {lid} está definido en «{dueno}» según el índice y el "
                    f"artefacto afirma «{publicada[:80] or '(vacío)'}». Atribución "
                    "incorrecta: la fila cita otra cosa.",
                )
            )
    salida = []
    if len(duenos) < MIN_DUENOS:
        salida.append(
            Violacion(
                "C8",
                "SIN-HALLAZGOS",
                f"{rel}: las lecciones capitalizadas proceden de {len(duenos)} fuente(s) "
                f"({', '.join(sorted(duenos)) or 'ninguna'}) y se exigen ≥{MIN_DUENOS}. "
                "Capitalizar solo al predecesor deja el corpus entero sin consultar.",
            )
        )
    return violaciones + salida, sorted(duenos)


# ---------------------------------------------------------------------------- orquestador


def analizar_plan(
    plan: Path, plans_dir: Path, owners: dict[str, str] | None, indice_motivo: str
) -> tuple[list[Violacion], list[str]]:
    rel = plan.relative_to(plans_dir).as_posix()
    ruta = plan / ARTIFACTO
    if not ruta.exists():
        return [
            Violacion(
                "C1",
                "AUSENTE",
                f"{rel}: no existe {ARTIFACTO}. Desde executor v2.22.0 el Paso 0 produce este "
                "artefacto ANTES del plan maestro.",
            )
        ], []
    texto, error = _leer(ruta)
    if texto is None:
        return [
            Violacion("C1", "LECTOR-FALLIDO", f"{rel}: no se pudo leer {ARTIFACTO}: {error}")
        ], []

    acs, motivo_maestro = acs_del_maestro(plan)
    violaciones, secciones = c2_secciones(rel, texto)
    violaciones += c3_consulta_al_corpus(rel, secciones["1"])
    violaciones += c4_ac_existente(rel, secciones["2"], acs, motivo_maestro)
    violaciones += c5_descartes(rel, secciones["3"])
    violaciones += c6_cobertura_declarada(rel, secciones["4"])
    c78, duenos = c7_c8_atribucion(rel, secciones["2"], owners, indice_motivo)
    return violaciones + c78, duenos


def verificar(
    plans_dir: Path, context_dir: Path, cutoff: date, verbose: bool = True
) -> tuple[list[Violacion], dict]:
    """Corrida completa sobre el corpus. Devuelve violaciones y población mirada (C0)."""
    grupos = clasificar_planes(plans_dir, cutoff)
    owners, indice_motivo = duenos_del_corpus(plans_dir, context_dir)
    violaciones: list[Violacion] = []
    if indice_motivo:
        violaciones.append(Violacion("C7", "LECTOR-FALLIDO", f"corpus: {indice_motivo}"))
    for plan in grupos["alcance"]:
        v, duenos = analizar_plan(plan, plans_dir, owners, indice_motivo)
        violaciones += v
        if verbose and duenos:
            print(f"  {plan.name}: {len(duenos)} fuentes capitalizadas -> {', '.join(duenos)}")
    poblacion = {
        "alcance": [p.name for p in grupos["alcance"]],
        "exentos_fecha": [p.name for p in grupos["exento_fecha"]],
        "exentos_sin_fecha": [p.name for p in grupos["sin_fecha"]],
        "archivados": len(grupos["archivados"]),
        "indice_motivo": indice_motivo,
    }
    return violaciones, poblacion


def _linea_de_cobertura(poblacion: dict, cutoff: date) -> str:
    return (
        f"cobertura: {len(poblacion['alcance'])} plan(es) en alcance "
        f"({', '.join(poblacion['alcance']) or '—'}) | "
        f"{poblacion['archivados']} archivados excluidos | "
        f"{len(poblacion['exentos_fecha'])} exentos por fecha anterior a {cutoff.isoformat()} | "
        f"{len(poblacion['exentos_sin_fecha'])} exentos SIN FECHA PARSEABLE "
        f"({', '.join(poblacion['exentos_sin_fecha']) or '—'})"
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Verificador de capitalización del Paso 0 (forma y trazabilidad; NO la pertinencia)"
    )
    ap.add_argument("--plans-dir", type=Path, default=DEFAULT_PLANS)
    ap.add_argument("--context-dir", type=Path, default=DEFAULT_CONTEXT)
    ap.add_argument(
        "--cutoff",
        default=CUTOFF_DATE.isoformat(),
        help="fecha YYYY-MM-DD desde la que un plan se exige (default: %(default)s)",
    )
    ap.add_argument(
        "--quiet", action="store_true", help="no listar violaciones ni fuentes por plan"
    )
    args = ap.parse_args(argv)

    try:
        cutoff = date.fromisoformat(args.cutoff)
    except ValueError:
        print(f"[2] --cutoff no es YYYY-MM-DD: {args.cutoff}")
        return 2
    if not args.plans_dir.is_dir():
        print(f"[2] el directorio de planes no existe: {args.plans_dir}")
        return 2

    violaciones, poblacion = verificar(
        args.plans_dir, args.context_dir, cutoff, verbose=not args.quiet
    )
    if not args.quiet:
        for v in violaciones:
            print(f"  - {v}")
    print(_linea_de_cobertura(poblacion, cutoff))
    if violaciones:
        resumen = ", ".join(
            f"{c}={sum(1 for v in violaciones if v.check == c)}"
            for c in sorted({v.check for v in violaciones})
        )
        print(f"[FAIL] Capitalización del Paso 0: {len(violaciones)} violacion(es) ({resumen})")
        print("El artefacto se corrige a mano: este script reporta, no reescribe.")
        return 1
    print(
        "[OK] Capitalización del Paso 0: forma y trazabilidad verificadas | NO verifica pertinencia "
        "(qué lección debía capitalizarse, ni si el efecto alegado es real)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
