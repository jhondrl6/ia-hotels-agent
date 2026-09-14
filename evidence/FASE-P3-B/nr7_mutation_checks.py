"""NR7 mutation checks — FASE-P3-B (AC-F3, AC-F5, AC-F6).

Por cada AC se desactiva la garantia y se comprueba que el test dirigido se pone
ROJO. Un test que no puede fallar no certifica el AC (NR7, de L-T4A.5/L-T2C.4/L-VUP-5).

Seis mutaciones:
  AC-F3-a  retirar la autorizacion de Bot 3 de la whitelist (la barra sigue viva)
  AC-F3-b  aparece un emisor NO contratado en modules/ (la barra no es decorativa)
  AC-F5-a  las banderas de FASE-K vuelven al literal False
  AC-F5-b  el hoist vuelve a quedar envuelto en un `except Exception` (L-T2C.2)
  AC-F5-c  el hoist cae dentro de `if generate_proposal:` (regimen False)
  AC-F6    la version del acta se hardcodea otra vez en el writer

Ejecuta:  python evidence/FASE-P3-B/nr7_mutation_checks.py
Escribe:  evidence/FASE-P3-B/NR7-<ac>.txt   (par verde/rojo por mutacion)

Cada archivo mutado se restaura desde su contenido original en memoria; la sonda de
AC-F3-b se borra en el `finally`. Verifica el arbol al terminar con `git status`.
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = Path(__file__).resolve().parent

MAIN = ROOT / "main.py"
ACTA = ROOT / "modules" / "quality_gates" / "tribunal" / "acta_writer.py"
BARREDA = ROOT / "tests" / "test_asset_path_clave_canonica.py"
PROBE = ROOT / "modules" / "quality_gates" / "tribunal" / "nr7_probe_emisor.py"

WIRING = "tests/quality_gates/tribunal/test_p3b_analytics_flags_wiring.py"
SE2 = "tests/quality_gates/tribunal/test_s_e2_generate_proposal_false.py"
VERSION_TEST = "tests/quality_gates/tribunal/test_acta_version_desde_yaml.py"
BARREDA_ID = "tests/test_asset_path_clave_canonica.py::TestDocumentacionDelContrato::test_barreda_un_solo_emisor_de_la_clave"

# --- textos ---
BANDERAS_FASE_K = """            ga4_enabled=ga4_available,
            gsc_enabled=gsc_available,"""

HOIST = """    ga4_hotel_property_id = getattr(args, 'ga4_property_id', None) or None
    ga4_client = GoogleAnalyticsClient(property_id=ga4_hotel_property_id)
    ga4_available = ga4_client.is_available()
    gsc_available = GoogleSearchConsoleClient().is_configured()"""

FOOTER = ("            f\"*Generado por TribunalJudge v{_read_project_version()} — "
          "{datetime.now().strftime('%Y-%m-%d %H:%M')}*\",")


def run(tests):
    cmd = [sys.executable, "-m", "pytest", *tests,
           "-v", "--tb=line", "-p", "no:cacheprovider"]
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                          encoding="utf-8", errors="replace",
                          env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    return proc.returncode, proc.stdout + proc.stderr


MUTATIONS = [
    {
        "ac": "AC-F3-a",
        "desc": "Retirar la autorizacion de Bot 3 (asset_reviewer) de EMISORES_LEGITIMOS",
        "archivo": BARREDA,
        "viejo": """    # Bot 3: eco de la ruta que ya resolvió al leer la matriz, dentro de su propio
    # `revision_assets.json`. No añade un hecho nuevo sobre la producción del asset.
    "quality_gates/tribunal/asset_reviewer.py",
}
CONSUMIDORES_LEGITIMOS = {""",
        "nuevo": """    # MUTACIÓN NR7: autorización de Bot 3 retirada
}
CONSUMIDORES_LEGITIMOS = {""",
        "tests": [BARREDA_ID],
    },
    {
        "ac": "AC-F3-b",
        "desc": "Aparece un emisor de `asset_path` no contratado en modules/ (sonda)",
        "archivo": None,          # se crea/borra, no se edita
        "viejo": None,
        "nuevo": None,
        "tests": [BARREDA_ID],
    },
    {
        "ac": "AC-F5-a",
        "desc": "Las banderas de FASE-K vuelven al literal False (Tier A otra vez inalcanzable)",
        "archivo": MAIN,
        "viejo": BANDERAS_FASE_K,
        "nuevo": """            ga4_enabled=False,  # MUTACIÓN NR7
            gsc_enabled=False,  # MUTACIÓN NR7""",
        "tests": [f"{WIRING}::TestCableadoBanderasEnFASEK::test_ga4_enabled_no_es_constante",
                  f"{WIRING}::TestCableadoBanderasEnFASEK::test_gsc_enabled_no_es_constante"],
    },
    {
        "ac": "AC-F5-b",
        "desc": "El hoist vuelve a quedar envuelto en try/except Exception (L-T2C.2)",
        "archivo": MAIN,
        "viejo": HOIST,
        "nuevo": """    try:  # MUTACIÓN NR7
        ga4_hotel_property_id = getattr(args, 'ga4_property_id', None) or None
        ga4_client = GoogleAnalyticsClient(property_id=ga4_hotel_property_id)
        ga4_available = ga4_client.is_available()
        gsc_available = GoogleSearchConsoleClient().is_configured()
    except Exception:
        pass""",
        "tests": [f"{WIRING}::TestCableadoBanderasEnFASEK::test_hoist_fuera_de_todo_except_ancho[ga4_available]",
                  f"{WIRING}::TestCableadoBanderasEnFASEK::test_hoist_fuera_de_todo_except_ancho[gsc_available]"],
    },
    {
        "ac": "AC-F5-c",
        "desc": "El hoist cae dentro de `if generate_proposal:` (regimen False → NameError enmascarado)",
        "archivo": MAIN,
        "viejo": HOIST,
        "nuevo": """    if generate_proposal:  # MUTACIÓN NR7
        ga4_hotel_property_id = getattr(args, 'ga4_property_id', None) or None
        ga4_client = GoogleAnalyticsClient(property_id=ga4_hotel_property_id)
        ga4_available = ga4_client.is_available()
        gsc_available = GoogleSearchConsoleClient().is_configured()""",
        "tests": [f"{SE2}::TestAnalyticsFlagsReachableWithoutProposal::test_banderas_no_bajo_el_guard_de_propuesta[ga4_available]",
                  f"{SE2}::TestAnalyticsFlagsReachableWithoutProposal::test_banderas_no_bajo_el_guard_de_propuesta[gsc_available]",
                  f"{WIRING}::TestCableadoBanderasEnFASEK::test_hoist_alcanzable_donde_lo_es_fase_k[ga4_available]"],
    },
    {
        "ac": "AC-F6",
        "desc": "La version del acta se hardcodea de nuevo en acta_writer.py",
        "archivo": ACTA,
        "viejo": FOOTER,
        "nuevo": """            f"*Generado por TribunalJudge v4.76.0 — {datetime.now().strftime('%Y-%m-%d %H:%M')}*",""",
        "tests": [f"{VERSION_TEST}::TestVersionDelActa::test_refleja_un_yaml_distinto_sin_tocar_codigo",
                  f"{VERSION_TEST}::TestVersionDelActa::test_el_writer_no_lleva_un_literal_de_version",
                  f"{VERSION_TEST}::TestVersionDelActa::test_sin_yaml_legible_lo_declara"],
    },
]


def main():
    targets = {m["archivo"] for m in MUTATIONS if m["archivo"]}
    originals = {p: p.read_text(encoding="utf-8") for p in targets}
    failures = []

    for m in MUTATIONS:
        probe_case = m["archivo"] is None
        path = m["archivo"] or PROBE

        if not probe_case and m["viejo"] not in originals[path]:
            print(f"!! {m['ac']}: el texto a mutar no esta en {path.name} — abortando")
            failures.append(m["ac"])
            continue

        rc_green, out_green = run(m["tests"])

        try:
            if probe_case:
                PROBE.write_text(
                    '"""Sonda NR7 AC-F3-b: emisor extra de asset_path sin contrato."""\n'
                    'DATA = {"asset_path": "sonda"}\n',
                    encoding="utf-8",
                )
            else:
                path.write_text(
                    originals[path].replace(m["viejo"], m["nuevo"], 1), encoding="utf-8"
                )
            rc_red, out_red = run(m["tests"])
        finally:
            if probe_case:
                PROBE.unlink(missing_ok=True)
            else:
                path.write_text(originals[path], encoding="utf-8")

        mutated_failed = rc_red != 0
        report = (
            f"# NR7 mutation check — {m['ac']}\n"
            f"# Mutacion: {m['desc']}\n"
            f"# Archivo: {path.relative_to(ROOT).as_posix()}\n"
            f"# Tests dirigidos: {len(m['tests'])}\n"
            f"#\n"
            f"# VERDE (sin mutar): rc={rc_green} — esperado 0\n"
            f"# ROJO (mutado):     rc={rc_red} — esperado != 0 → "
            f"{'OK, el test puede fallar' if mutated_failed else 'FALLO: el test NO falla, no certifica el AC'}\n"
            f"\n{'='*70}\n=== SALIDA VERDE (rc={rc_green}) ===\n{'='*70}\n"
            f"{out_green}\n"
            f"\n{'='*70}\n=== SALIDA ROJA — MUTADO (rc={rc_red}) ===\n{'='*70}\n"
            f"{out_red}\n"
        )
        out_file = EVIDENCE / f"NR7-{m['ac']}.txt"
        out_file.write_text(report, encoding="utf-8")

        status = "OK" if (rc_green == 0 and mutated_failed) else "FALLO"
        print(f"[{status}] {m['ac']}: verde rc={rc_green}, rojo rc={rc_red} → {out_file.name}")
        if status == "FALLO":
            failures.append(m["ac"])

    for p, orig in originals.items():
        assert p.read_text(encoding="utf-8") == orig, f"{p.name} no se restauró"
    assert not PROBE.exists(), "la sonda de AC-F3-b no se borro"
    print("\nArbol restaurado: main.py, acta_writer.py y el test barreda identicos al original; sonda borrada.")

    if failures:
        print(f"\nNR7 NO cumplido en: {failures}")
        sys.exit(1)
    print(f"\nNR7 cumplido en los {len(MUTATIONS)} pares "
          f"(AC-F3 a/b, AC-F5 a/b/c, AC-F6).")


if __name__ == "__main__":
    main()
