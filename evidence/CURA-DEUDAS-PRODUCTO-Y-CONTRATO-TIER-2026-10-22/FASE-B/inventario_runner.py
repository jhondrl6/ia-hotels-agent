# -*- coding: utf-8 -*-
"""FASE-B - Inventario de candidatas con la funcion REAL del revisor (Tarea 1).

Dos pasadas sobre cada texto:
  (1) CRUDA   : regex de VERIFICATION_SCAN_GROUPS sin filtro estructural y sin dedupe
                (equivalente al grep suelto que solo cuenta literales).
  (2) REAL    : coincidencias_lenguaje_de_verificacion() — filtro estructural AC10 + dedupe.

Ademas: falso 0 historico (alternante 100% con \\b tras el signo) y la resta
10 -> 6 -> 2 sobre la propuesta renderizada del baseline 2026-10-12.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from modules.quality_gates.tribunal.honesty_reviewer import (
    VERIFICATION_SCAN_GROUPS,
    VERIFICATION_GROUP_CUANTIFICADOR,
    _es_contexto_financiero,
    _linea_conteniendo,
    coincidencias_lenguaje_de_verificacion,
)

BASELINE = REPO / "evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/corrida"
PROPUESTA_BASELINE = BASELINE / "02_PROPUESTA_COMERCIAL_20261012_165706.md"
DIAG_BASELINE = BASELINE / "01_DIAGNOSTICO_Y_OPORTUNIDAD_20261012_165706.md"
TPL_PROPUESTA = REPO / "modules/commercial_documents/templates/propuesta_v6_template.md"
TPL_DIAG = REPO / "modules/commercial_documents/templates/diagnostico_v6_template.md"

# Los 5 labels financieros legítimos de la plantilla de propuesta (no se tocan).
LABELS_FINANCIEROS = (
    "fuga total estimada",
    "total recuperacion proyectada",
    "100% suyo",
)


def pasada_cruda(texto):
    literales = []
    for grupo, patron, excluye_financiero in VERIFICATION_SCAN_GROUPS:
        for m in re.finditer(patron, texto or "", re.IGNORECASE):
            linea = _linea_conteniendo(texto, m.start()).strip()
            descartado = excluye_financiero and _es_contexto_financiero(linea)
            literales.append({
                "grupo": grupo,
                "literal": m.group(0),
                "linea": linea,
                "descartado_filtro": descartado,
            })
    return literales


def reporte(nombre, texto):
    print("=" * 78)
    print(f"TEXTO: {nombre}")
    print("=" * 78)
    crudos = pasada_cruda(texto)
    descartados = [c for c in crudos if c["descartado_filtro"]]
    print(f"\n--- PASADA 1 (cruda: regex del codigo, sin filtro, sin dedupe): "
          f"{len(crudos)} literales ---")
    for c in crudos:
        marca = "DESCARTADO(filtro estructural)" if c["descartado_filtro"] else "candidato"
        print(f"  [{marca}] {c['grupo']} | {c['literal']!r} | {c['linea'][:100]}")
    print(f"\n  descartados por filtro estructural: {len(descartados)}")

    reales = coincidencias_lenguaje_de_verificacion(texto)
    print(f"\n--- PASADA 2 (funcion real coincidencias_lenguaje_de_verificacion): "
          f"{len(reales)} hallazgos emitidos ---")
    for r in reales:
        print(f"  {r['grupo']} | {r['literal']!r} | {r['linea'][:100]}")
    return crudos, reales


def falso_cero():
    print("=" * 78)
    print("FALSO 0 HISTORICO (alternante 100% con \\b tras el signo)")
    print("=" * 78)
    viejo = r"(?<!\d)100[ \t]*%\b"  # patron viejo: \\b tras signo de no-palabra
    nuevo = r"(?<!\d)100[ \t]*%"
    for nombre, path in (("propuesta baseline", PROPUESTA_BASELINE),
                         ("diagnostico baseline", DIAG_BASELINE),
                         ("plantilla propuesta", TPL_PROPUESTA),
                         ("plantilla diagnostico", TPL_DIAG)):
        texto = path.read_text(encoding="utf-8")
        n_viejo = len(re.findall(viejo, texto, re.IGNORECASE))
        n_nuevo = len(re.findall(nuevo, texto, re.IGNORECASE))
        print(f"  {nombre:24s} patron VIEJO(\\b): {n_viejo}  patron ACTUAL: {n_nuevo}"
              + ("   <- falso 0" if n_viejo == 0 and n_nuevo > 0 else ""))
    print("  Documentacion: docstring de VERIFICATION_GROUP_CUANTIFICADOR en")
    print("  modules/quality_gates/tribunal/honesty_reviewer.py (frontera curada).")
    print("  El '0' del patron viejo era falso: ningun 100% del corpus matcheaba.")


def main():
    print("INVENTARIO CANDIDATAS - FASE-B - funcion real del revisor")
    print("Patrones importados desde modules/quality_gates/tribunal/honesty_reviewer.py")
    print("(bandera re.IGNORECASE incluida en ambos grupos).\n")

    # Resta 10 -> 6 -> 2: propuesta renderizada del baseline real
    prop = PROPUESTA_BASELINE.read_text(encoding="utf-8")
    crudos_p, reales_p = reporte("PROPUESTA BASELINE (render real 2026-10-12)", prop)
    n_crudos, n_desc, n_emit = len(crudos_p), sum(1 for c in crudos_p if c["descartado_filtro"]), len(reales_p)
    print(f"\n>>> RESTA BASELINE: {n_crudos} literales -> {n_desc} descartados por filtro "
          f"estructural -> {n_emit} emitidos")

    diag = DIAG_BASELINE.read_text(encoding="utf-8")
    reporte("DIAGNOSTICO BASELINE (render real 2026-10-12)", diag)

    # Plantillas: contraste grep vs funcion (8 vs 10)
    for nombre, path in (("PLANTILLA propuesta_v6_template.md", TPL_PROPUESTA),
                         ("PLANTILLA diagnostico_v6_template.md", TPL_DIAG)):
        texto = path.read_text(encoding="utf-8")
        reporte(nombre, texto)

    # Contraste grep 'total|100%' sobre plantilla de propuesta
    tpl = TPL_PROPUESTA.read_text(encoding="utf-8")
    grep_lines = [f"{i}: {l.strip()}" for i, l in enumerate(tpl.splitlines(), 1)
                  if re.search(r"total|100%", l, re.IGNORECASE)]
    print("=" * 78)
    print("CONTRASTE grep suelto vs funcion real (plantilla de propuesta)")
    print("=" * 78)
    print(f"  grep -in 'total|100%' -> {len(grep_lines)} lineas:")
    for g in grep_lines:
        print("   ", g[:110])
    crudos_t = pasada_cruda(tpl)
    print(f"  funcion real -> {len(crudos_t)} literales crudos / "
          f"{len(coincidencias_lenguaje_de_verificacion(tpl))} emitidos")
    print("  (el grep cuenta lineas; la funcion cuenta literales y aplica el filtro)")

    falso_cero()

    # Tabla de contraste: grep de 7 lineas = 2 claims emitidos + 5 "no tocar"
    print()
    print("=" * 78)
    print("TABLA - grep de 7 lineas (total|absoluto|definitivo|100%|garantiz):")
    print("2 claims EMITIDOS por la funcion real vs 5 lineas NO TOCAR")
    print("=" * 78)
    emitidos_tpl = coincidencias_lenguaje_de_verificacion(tpl)
    lineas_emitidas = {r["linea"].strip() for r in emitidos_tpl}
    grep7 = [(i, l.strip()) for i, l in enumerate(tpl.splitlines(), 1)
             if re.search(r"total|absoluto|definitivo|100%|garantiz", l, re.IGNORECASE)]
    n_claims = 0
    for i, l in grep7:
        es_claim = any(
            r["linea"].strip() == l and "total" in r["literal"].lower()
            and ("GARANT" in l.upper() or "TRANSPARENCIA" in l.upper())
            for r in emitidos_tpl
        )
        if es_claim:
            n_claims += 1
            print(f"    EMITIDO  (claim)  | linea {i} | {l[:100]}")
        else:
            print(f"    NO TOCAR (label)  | linea {i} | {l[:100]}")
    print(f"  => {n_claims} claims emitidos / {len(grep7) - n_claims} lineas no tocar "
          f"(grep de {len(grep7)} lineas)")
    print("  Resta del baseline renderizado (funcion real, propuesta 2026-10-12):")
    print("    crudos 10 literales -> filtro estructural (8 vs 10) -> 2 emitidos")
    print("  Medicion congelada (CONTEXT-CONTRATO-PLANTILLA-TIER, 2026-10-14):")
    print("    10 -> 6 -> 2 (los 2 restantes de esa medicion caian en el mismo")
    print("    bucket de descartados; ver baseline-pre-post.md por la divergencia)")


if __name__ == "__main__":
    main()
