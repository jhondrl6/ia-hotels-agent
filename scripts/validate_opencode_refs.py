#!/usr/bin/env python3
"""
OpenCode Reference Validator for IA Hoteles.

Validates that every ``.opencode/...`` path referenced inside Markdown
documents actually exists on disk. This catches forgotten reference
updates after archiving plans (plans -> Archives/) or contexts
(context -> Historico/).

Scan scope:
  - ``.opencode/plans/**/*.md`` and ``.opencode/context/**/*.md``
  - any extra directory passed via ``--extra-dir`` (repeatable), e.g.
    the agent project memory directory.

Behavior:
  - Read-only by default: reports broken references, exit code 1.
  - ``--fix``: rewrites a broken reference when the referenced basename
    resolves to EXACTLY ONE candidate under ``.opencode/``. Ambiguous or
    missing candidates are reported, never guessed.
  - ``--write-baseline``: freezes the current broken references into
    ``.opencode/refs_baseline.txt`` (one ``file|ref`` per line). Those
    pairs are ignored afterwards, so the gate only fails on NEW breaks.
    Use once to absorb historical debt; keep the file committed.

Template placeholders (e.g. ``.opencode/plans/<nombre-del-plan>/``)
degrade to their nearest valid parent because ``<`` and ``>`` are not
path characters, so they never produce false positives.

Exit codes:
  0 - all references valid (or fixed with --fix)
  1 - broken references remain
  2 - script error (missing .opencode directory)
"""
import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
OPENCODE_DIR = PROJECT_ROOT / ".opencode"
BASELINE_FILE = OPENCODE_DIR / "refs_baseline.txt"

# Matches .opencode/... (forward or back slashes) with common path chars.
# Stops at whitespace, backticks, brackets, pipes, quotes, commas, < >.
REF_RE = re.compile(r"\.opencode[/\\][A-Za-z0-9_\-./\\]+")

# Markdown files never to scan (forensic/frozen artifacts).
EXCLUDE_FILES = set()


def file_key(md: Path) -> str:
    """Stable key for a scanned file: repo-relative when possible."""
    try:
        return md.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return md.as_posix()


def load_baseline() -> Set[Tuple[str, str]]:
    """Read frozen (file_key, ref) pairs from the baseline file."""
    if not BASELINE_FILE.is_file():
        return set()
    entries = set()
    for line in BASELINE_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, ref = line.partition("|")
        if key and ref:
            entries.add((key, ref))
    return entries


def extract_refs(text: str) -> List[str]:
    """Return cleaned .opencode path references found in text.

    Skips false positives: matches truncated by a template placeholder
    (``<...>``), a glob (``{a,b}`` or ``*``), or ellipsis placeholders.
    """
    refs = []
    for match in REF_RE.finditer(text):
        tail = text[match.end():match.end() + 1]
        if tail in ("<", "{", "*"):
            continue
        ref = match.group(0).rstrip("/\\.")
        if not ref or "..." in ref:
            continue
        if ref not in refs:
            refs.append(ref)
    return refs


def normalize(ref: str) -> str:
    """Normalize a reference to forward slashes."""
    return ref.replace("\\", "/")


def ref_target(ref: str) -> Path:
    """Resolve a normalized reference against the project root."""
    return PROJECT_ROOT / normalize(ref).lstrip("/")


def scan_files(scan_dirs: List[Path]) -> List[Path]:
    """Collect Markdown files to scan, pruning excluded files."""
    files: List[Path] = []
    for d in scan_dirs:
        if not d.is_dir():
            continue
        for md in sorted(d.rglob("*.md")):
            if md.name not in EXCLUDE_FILES:
                files.append(md)
    return files


def find_candidates(basename: str) -> List[Path]:
    """Find all files/dirs under .opencode/ with the given basename."""
    if not OPENCODE_DIR.is_dir():
        return []
    return sorted(
        p for p in OPENCODE_DIR.rglob(basename)
        if not any(part.startswith(".") for part in p.relative_to(OPENCODE_DIR).parts)
    )


def archived_promotion(ref: str) -> Optional[Path]:
    """Resolve a ref by promoting it into Archives/ or Historico/, or None.

    Covers the standard archive move: plans/<X> -> plans/Archives/<X> and
    context/<Y> -> context/Historico/<Y>.
    """
    parts = normalize(ref).split("/")
    if len(parts) < 3 or parts[0] != ".opencode":
        return None
    sub, archive = (
        ("plans", "Archives") if parts[1] == "plans"
        else ("context", "Historico") if parts[1] == "context"
        else (None, None)
    )
    if sub is None or parts[2] == archive:
        return None
    candidate = PROJECT_ROOT / "/".join(parts[:2] + [archive] + parts[2:])
    return candidate if candidate.exists() else None


def validate(scan_dirs: List[Path], apply_baseline: bool = True) -> List[Tuple[Path, int, str]]:
    """Return list of (file, line_number, broken_ref).

    Broken references present in the frozen baseline are skipped unless
    apply_baseline is False (used by --write-baseline).
    """
    baseline = load_baseline() if apply_baseline else set()
    broken: List[Tuple[Path, int, str]] = []
    for md in scan_files(scan_dirs):
        try:
            text = md.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for ref in extract_refs(line):
                if not ref_target(ref).exists():
                    if (file_key(md), normalize(ref)) in baseline:
                        continue
                    broken.append((md, lineno, normalize(ref)))
    return broken


def fix_broken(broken: List[Tuple[Path, int, str]]) -> Tuple[int, List[str]]:
    """Rewrite fixable references in-place.

    Returns (fixed_count, list_of_unfixable_reports).
    """
    fixed = 0
    unfixable: List[str] = []
    # Group by file so each file is rewritten once.
    by_file: Dict[Path, List[str]] = {}
    for md, _lineno, ref in broken:
        by_file.setdefault(md, [])
        if ref not in by_file[md]:
            by_file[md].append(ref)

    for md, refs in by_file.items():
        text = md.read_text(encoding="utf-8")
        changed = False
        for ref in refs:
            promoted = archived_promotion(ref)
            if promoted is not None:
                new_rel = "/" + promoted.relative_to(PROJECT_ROOT).as_posix()
                text = text.replace(ref, new_rel)
                fixed += 1
                changed = True
                print(f"  [FIX] {md.name}: {ref} -> {new_rel}")
                continue
            basename = normalize(ref).rstrip("/").rsplit("/", 1)[-1]
            candidates = find_candidates(basename)
            if len(candidates) == 1:
                new_rel = "/" + candidates[0].relative_to(PROJECT_ROOT).as_posix()
                text = text.replace(ref, new_rel)
                fixed += 1
                changed = True
                print(f"  [FIX] {md.name}: {ref} -> {new_rel}")
            else:
                unfixable.append(
                    f"{md}: {ref} (candidatos: {len(candidates)} — "
                    f"{'ambiguo' if candidates else 'sin coincidencias'})"
                )
        if changed:
            md.write_text(text, encoding="utf-8")
    return fixed, unfixable


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Valida referencias .opencode/... en documentos Markdown."
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Reescribe referencias rotas cuando el basename es único bajo .opencode/",
    )
    parser.add_argument(
        "--extra-dir",
        action="append",
        default=[],
        metavar="DIR",
        help="Directorio adicional a escanear (repetible)",
    )
    parser.add_argument(
        "--write-baseline",
        action="store_true",
        help="Congela las referencias rotas actuales en refs_baseline.txt",
    )
    args = parser.parse_args(argv)

    if not OPENCODE_DIR.is_dir():
        print(f"[ERROR] No existe {OPENCODE_DIR}")
        return 2

    scan_dirs = [OPENCODE_DIR / "plans", OPENCODE_DIR / "context"]
    scan_dirs += [Path(d) for d in args.extra_dir]

    if args.write_baseline:
        broken = validate(scan_dirs, apply_baseline=False)
        entries = sorted({(file_key(md), ref) for md, _lineno, ref in broken})
        lines = ["# Referencias históricas rotas congeladas (validate_opencode_refs.py)",
                 "# Formato: archivo|referencia — una por línea."]
        lines += [f"{key}|{ref}" for key, ref in entries]
        BASELINE_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"[BASELINE] {len(entries)} referencia(s) congelada(s) en {BASELINE_FILE}")
        return 0

    broken = validate(scan_dirs)

    if not broken:
        print("[PASS] OpenCode References: todas las referencias existen")
        return 0

    print(f"[!] {len(broken)} referencia(s) rota(s):")
    for md, lineno, ref in broken:
        try:
            rel = md.relative_to(PROJECT_ROOT)
        except ValueError:
            rel = md
        print(f"  {rel}:{lineno} -> {ref}")

    if not args.fix:
        print("[FAIL] OpenCode References: ejecutar con --fix para intentar reparar")
        return 1

    fixed, unfixable = fix_broken(broken)
    print(f"[FIX] {fixed} referencia(s) reparada(s)")
    for item in unfixable:
        print(f"  [SIN-FIX] {item}")

    if unfixable:
        print("[FAIL] OpenCode References: quedan referencias irreparables")
        return 1
    print("[PASS] OpenCode References: todas las referencias reparadas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
