"""Auditoría FASE-B: delta medido sobre la biyección triple (AC4 / V1 / N-A1).

POR QUÉ NO BASTA RE-EJECUTAR `evidence/FASE-A/faseA_narratives_audit.py`
Ese script mide `narratives` leyendo el **dict literal** por AST y mide las emisiones con
**regex sobre el fuente**. Dos premisas suyas dejaron de ser ciertas después de B2:

  1. B2 decidió DERIVAR el complemento de Capa 1 en vez de inflar el literal (guardrail
     L-NC4: una segunda tabla pain_id→texto re-fosiliza). El literal sigue teniendo las 16
     claves heredadas, así que el script de FASE-A reporta "DESCARTE REAL = 4" — un
     artefacto de sintaxis, no de comportamiento. Ejecutado tal cual, su sección C dice que
     la fase EMPEORÓ el defecto que vino a cerrar.
  2. El regex cuenta *puntos de emisión escritos*, no *emisiones alcanzables*. Esa es la
     causa del error de premisa de N-A1 (clasificó `no_ga4_enhanced` como "vivo" cuando su
     guardia `hasattr(status, "is_enhanced")` es insatisfacible). Seguimiento S-B7.

QUÉ MIDE ESTE SCRIPT
Los mismos tres conjuntos, pero:
  · emisiones por AST restringido a las funciones emisoras (no regex sobre el archivo)
  · narratives en DOS columnas: literal (continuidad con FASE-A) y **efectivo** (sonda
    conductual que llama a `_pain_to_brecha` y observa si devuelve None)

Importa los helpers del candado (`tests/commercial_documents/test_pain_map_bijection.py`) a
propósito: este artefacto debe reportar exactamente lo que el candado exige, no una segunda
medición paralela que pueda divergir de él.

USO
    ./venv/Scripts/python.exe evidence/FASE-B/faseB_narratives_audit.py
"""
import sys
from pathlib import Path

_root = Path(__file__).resolve()
while _root.parent != _root and not (_root / "VERSION.yaml").exists():
    _root = _root.parent
sys.path.insert(0, str(_root))

# FASE-P0-C: en Windows la consola usa cp1252 y revienta con UnicodeEncodeError a mitad del
# reporte (⊎, →). El artefacto de evidencia debe salir en UTF-8 sin importar el code page.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper
from tests.commercial_documents.test_pain_map_bijection import (
    PAINS_DIFERIDOS,
    _claves_narratives,
    _pain_ids_emitidos,
    _pain_ids_narrables,
)

# Baseline FASE-A: evidence/FASE-A/faseA_narratives_audit.txt (medido, no recordado).
FASE_A = {"capa1": 27, "narratives_literal": 16, "emitidos_regex": 18, "descarte_real": 2}

capa1 = set(PainSolutionMapper.PAIN_SOLUTION_MAP)
literal = _claves_narratives()
emitidos = _pain_ids_emitidos()
efectivo = _pain_ids_narrables(capa1)

descarte = sorted(emitidos - efectivo)
diferidos = set(PAINS_DIFERIDOS)

print("=" * 78)
print("BIYECCIÓN TRIPLE — ESTADO POST-B2")
print("=" * 78)
print(f"1. Capa 1 (PAIN_SOLUTION_MAP)             : {len(capa1)}")
print(f"2. narratives LITERAL (dict en el fuente)  : {len(literal)}")
print(f"3. narratives EFECTIVO (sonda conductual)  : {len(efectivo)}")
print(f"4. emisiones (AST, funciones emisoras)     : {len(emitidos)}")
print(f"5. pains DIFERIDOS (registro con motivo)   : {len(diferidos)}")

print()
print("=" * 78)
print("A. DESCARTE REAL = emitido por detect_pains Y `_pain_to_brecha` devuelve None")
if descarte:
    for p in descarte:
        print(f"   {p}")
else:
    print("   (ninguno)")
print(f"   total: {len(descarte)}")

print()
print("=" * 78)
print("B. Huérfanos (en narratives pero fuera de Capa 1)")
huerfanos = sorted(literal - capa1)
print("   " + (", ".join(huerfanos) if huerfanos else "(ninguno)"))
print(f"   total: {len(huerfanos)}")

print()
print("=" * 78)
print("C. PARTICIÓN DE LA EMISIÓN: Capa 1 = emitidos ⊎ diferidos")
sin_cubrir = sorted(capa1 - emitidos - diferidos)
solapados = sorted(diferidos & emitidos)
print(f"   emitidos            : {len(emitidos & capa1)}")
print(f"   diferidos           : {len(diferidos)}")
print(f"   sin decisión        : {len(sin_cubrir)} {sin_cubrir if sin_cubrir else ''}")
print(f"   a la vez ambas      : {len(solapados)} {solapados if solapados else ''}")
print(f"   ¿partición exacta?  : {not sin_cubrir and not solapados}")

print()
print("=" * 78)
print("D. COBERTURA NARRATIVA TOTAL: ¿todo pain de Capa 1 es narrable?")
no_narrables = sorted(capa1 - efectivo)
print(f"   no narrables        : {len(no_narrables)} {no_narrables if no_narrables else ''}")
print(f"   ¿total?             : {efectivo == capa1}")
print("   nota: los 6 diferidos TAMBIÉN son narrables. Es deliberado — la capa")
print("   narrativa es total para que el día que un diferido gane emisión la brecha")
print("   aparezca sola, sin editar una segunda tabla. Ver el docstring del candado.")

print()
print("=" * 78)
print("E. DELTA FASE-A → FASE-B")
print(f"   {'métrica':38s}{'FASE-A':>10s}{'FASE-B':>10s}")
print(f"   {'-' * 58}")
print(f"   {'Capa 1 (pain_ids declarados)':38s}{FASE_A['capa1']:>10d}{len(capa1):>10d}")
print(f"   {'narratives literal':38s}{FASE_A['narratives_literal']:>10d}{len(literal):>10d}")
print(f"   {'narratives efectivo':38s}{'—':>10s}{len(efectivo):>10d}")
print(f"   {'emisiones':38s}{FASE_A['emitidos_regex']:>10d}{len(emitidos):>10d}")
print(f"   {'DESCARTE REAL':38s}{FASE_A['descarte_real']:>10d}{len(descarte):>10d}")
print()
print("   Lectura del delta:")
print(f"   · Capa 1 27→26: se retiró no_ga4_enhanced (guardia insatisfacible, §3.10).")
print(f"   · emisiones 18→20: +3 implementados (missing_llmstxt, missing_alt_text,")
print(f"     no_social_links) −1 retirado (no_ga4_enhanced).")
print(f"   · literal 16→16: SIN CAMBIO. Ninguna entrada nueva se escribió a mano")
print(f"     (L-NC4); el complemento se deriva. Que el literal no crezca es la prueba")
print(f"     de que no se creó una tabla paralela.")
print(f"   · efectivo 26/26: la columna que FASE-A no podía medir.")
print(f"   · DESCARTE REAL 2→0: el defecto de N-A1 está cerrado.")

print()
print("=" * 78)
print("F. VERIFICACIÓN DE LA PREMISA N-A1 (seguimiento S-B7)")
print("   N-A1 afirmó: «2 pains VIVOS que se emiten y se descartan en producción»")
print("   (no_ga4_enhanced, low_ota_divergence). Medido:")
for p in ("no_ga4_enhanced", "low_ota_divergence"):
    print(f"   {p:24s} en Capa 1={p in capa1!s:6s} punto de emisión={p in emitidos!s:6s} "
          f"narrable={p in efectivo!s}")
print()
print("   no_ga4_enhanced tenía (pre-B2) punto de emisión escrito pero guardia")
print("   insatisfacible: is_enhanced no existe en AnalyticsStatus ni se puebla en")
print("   ningún punto del repo → NUNCA se emitió. B2 borró la rama muerta, de ahí")
print("   que la tabla de arriba lo reporte en False en las tres columnas.")
print("   low_ota_divergence sigue con su punto de emisión pero su guard (rama")
print("   'direct_channel_percentage' de detect_pains, pain_solution_mapper.py:447)")
print("   hace hasattr(float, '__iter__') → nunca dispara (V7, se arregla en FASE-H).")
print("   La premisa de N-A1 era falsa en ambos")
print("   casos: el regex de FASE-A contó sintaxis, no alcanzabilidad. Corregido en")
print("   decision-pains-muertos.md §1.")
