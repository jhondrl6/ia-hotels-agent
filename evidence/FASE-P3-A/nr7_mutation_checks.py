"""NR7 mutation checks — FASE-P3-A (AC-F1 dos capas, AC-F2, AC-F4).

Por cada AC de detección/bloqueo, desactiva la detección o el guard y comprueba
que el test dirigido se pone ROJO. Un test que no puede fallar no certifica el
AC (NR7, de L-T4A.5/L-T2C.4/L-VUP-5).

Ejecuta:  python evidence/FASE-P3-A/nr7_mutation_checks.py
Escribe:  evidence/FASE-P3-A/NR7-<ac>.txt  (par verde/rojo por mutación)

Restaura cada archivo mutado desde su contenido original en memoria, así que el
working tree queda intacto al terminar (verificado con el assert final).
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JUDGE = ROOT / "modules" / "quality_gates" / "tribunal" / "judge.py"
ASSET = ROOT / "modules" / "quality_gates" / "tribunal" / "asset_reviewer.py"
TESTFILE = "tests/quality_gates/tribunal/test_p3a_zip_tier_firstfloor.py"
EVIDENCE = ROOT / "evidence" / "FASE-P3-A"


def run(tests):
    """Corre pytest sobre una lista de node-ids; retorna (rc, salida)."""
    cmd = [
        sys.executable, "-m", "pytest", *tests,
        "-v", "--tb=line", "-p", "no:cacheprovider",
    ]
    proc = subprocess.run(
        cmd, cwd=str(ROOT), capture_output=True, text=True,
        encoding="utf-8", errors="replace",
        env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"},
    )
    return proc.returncode, proc.stdout + proc.stderr


# (AC, archivo, viejo, nuevo, tests dirigidos, descripción de la mutación)
MUTATIONS = [
    (
        "AC-F1-capa1",
        ASSET,
        # Desactivar la lectura del miembro desde el ZIP: el bloque ZIP-only se
        # vuelve un no-op (return None como si no hubiera ZIP).
        """        # 2) Régimen ZIP-only: leer el miembro desde el ZIP
        if zip_path is not None:
            try:
                with zipfile.ZipFile(zip_path) as zf:
                    raw = zf.read("IMPLEMENTATION_ORDER.md")
                return raw.decode("utf-8"), IMPL_ORDER_OK, "zip"
            except KeyError:
                return None, IMPL_ORDER_ARTIFACT_MISSING, "zip"
            except (zipfile.BadZipFile, OSError, UnicodeDecodeError):
                return None, IMPL_ORDER_READER_FAILED, "zip\"""",
        """        # 2) MUTACIÓN NR7: lectura del ZIP desactivada
        if zip_path is not None:
            return None, IMPL_ORDER_ARTIFACT_MISSING, "zip\"""",
        [
            f"{TESTFILE}::test_zip_only_stub_detected_from_zip_member",
            f"{TESTFILE}::test_real_baseline_zip_only_stub_detected",
        ],
        "Desactivar la lectura del miembro IMPLEMENTATION_ORDER.md desde el ZIP",
    ),
    (
        "AC-F1-capa2",
        ASSET,
        # Volver al conteo frágil de líneas: el cuerpo estructural se reemplaza
        # por el non_empty_lines<=3 que contaba el boilerplate como contenido.
        """        section_count = 0
        sections_with_content = 0
        current_has_content = False

        for raw_line in content.splitlines():
            stripped = raw_line.strip()
            if not stripped:
                continue
            if is_header(stripped):
                if section_count > 0 and current_has_content:
                    sections_with_content += 1
                section_count += 1
                current_has_content = False
            elif not is_boilerplate(stripped):
                current_has_content = True

        if section_count > 0 and current_has_content:
            sections_with_content += 1

        if section_count == 0:
            return False

        return sections_with_content == 0""",
        """        # MUTACIÓN NR7: criterio viejo de conteo de líneas
        lines = content.strip().splitlines()
        non_empty_lines = sum(
            1 for ln in lines if ln.strip() and not ln.strip().startswith("#")
        )
        return non_empty_lines <= 3""",
        [
            f"{TESTFILE}::test_structural_stub_excludes_boilerplate",
            f"{TESTFILE}::test_zip_only_stub_detected_from_zip_member",
            f"{TESTFILE}::test_real_baseline_zip_only_stub_detected",
            f"{TESTFILE}::test_dir_path_still_reads_unzipped_backward_compat",
        ],
        "Revertir _is_template_stub al conteo non_empty_lines<=3 (boilerplate cuenta como contenido)",
    ),
    (
        "AC-F2",
        JUDGE,
        # Revertir a MANIFEST-only: se elimina la lectura scenarios-first.
        """        scenarios_path = self._resolve_artifact(FINANCIAL_SCENARIOS_PATTERN)
        scenarios = self._load_json(scenarios_path)
        if scenarios is not None:
            tier = scenarios.get("breakdown", {}).get("evidence_tier")
            if tier:
                return tier

        manifest = self._resolve_manifest()""",
        """        # MUTACIÓN NR7: source pre-packaging ignorada, solo MANIFEST
        manifest = self._resolve_manifest()""",
        [
            f"{TESTFILE}::test_tier_read_from_financial_scenarios",
            f"{TESTFILE}::test_scenarios_takes_priority_over_manifest",
            f"{TESTFILE}::test_real_fase_i_tier_from_scenarios",
        ],
        "Revertir _read_evidence_tier a MANIFEST-only (ignora financial_scenarios)",
    ),
    (
        "AC-F4",
        JUDGE,
        'FIRST_FLOOR_TIERS = {"B", "B+", "C"}',
        'FIRST_FLOOR_TIERS = {"B", "C"}  # MUTACIÓN NR7: B+ fuera del primer piso',
        [
            f"{TESTFILE}::test_b_plus_in_first_floor_tiers",
            f"{TESTFILE}::test_first_floor_applies_to_b_plus",
            f"{TESTFILE}::test_first_floor_reason_not_lying_in_b_plus",
            f"{TESTFILE}::test_b_plus_verdict_is_conditional",
        ],
        "Quitar 'B+' de FIRST_FLOOR_TIERS (la razón del acta vuelve a mentir)",
    ),
]


def main():
    originals = {JUDGE: JUDGE.read_text(encoding="utf-8"),
                 ASSET: ASSET.read_text(encoding="utf-8")}
    failures = []

    for ac, path, old, new, tests, desc in MUTATIONS:
        text = originals[path]
        if old not in text:
            print(f"!! {ac}: el texto a mutar no está en {path.name} — abortando")
            failures.append(ac)
            continue

        # VERDE: estado actual (sin mutar) sobre los tests dirigidos
        rc_green, out_green = run(tests)

        # ROJO: aplicar la mutación
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        try:
            rc_red, out_red = run(tests)
        finally:
            path.write_text(text, encoding="utf-8")  # restaurar SIEMPRE

        mutated_failed = rc_red != 0
        report = (
            f"# NR7 mutation check — {ac}\n"
            f"# Mutación: {desc}\n"
            f"# Archivo: {path.relative_to(ROOT)}\n"
            f"# Tests dirigidos: {len(tests)}\n"
            f"#\n"
            f"# VERDE (sin mutar): rc={rc_green} — esperado 0\n"
            f"# ROJO (mutado):     rc={rc_red} — esperado != 0 → "
            f"{'OK, el test puede fallar' if mutated_failed else 'FALLO: el test NO falla, no certifica el AC'}\n"
            f"\n{'='*70}\n=== SALIDA VERDE (rc={rc_green}) ===\n{'='*70}\n"
            f"{out_green}\n"
            f"\n{'='*70}\n=== SALIDA ROJA — MUTADO (rc={rc_red}) ===\n{'='*70}\n"
            f"{out_red}\n"
        )
        out_file = EVIDENCE / f"NR7-{ac}.txt"
        out_file.write_text(report, encoding="utf-8")

        status = "OK" if (rc_green == 0 and mutated_failed) else "FALLO"
        print(f"[{status}] {ac}: verde rc={rc_green}, rojo rc={rc_red} → {out_file.name}")
        if status == "FALLO":
            failures.append(ac)

    # Integridad: los archivos deben quedar idénticos al original
    for path, orig in originals.items():
        assert path.read_text(encoding="utf-8") == orig, f"{path.name} no se restauró"
    print("\nWorking tree restaurado: judge.py y asset_reviewer.py idénticos al original.")

    if failures:
        print(f"\nNR7 NO cumplido en: {failures}")
        sys.exit(1)
    print("\nNR7 cumplido en los 4 pares (AC-F1 capa1, AC-F1 capa2, AC-F2, AC-F4).")


if __name__ == "__main__":
    main()
