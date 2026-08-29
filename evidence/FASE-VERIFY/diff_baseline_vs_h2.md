# Diff antes/después — Baseline corrida C vs corrida post-hotfix H2 (L-NC12)

> **Baseline**: `evidence/FASE-SR-H/baseline/` (corrida C, 2026-08-27 18:30, URL con UTM, v4.72.x pre-fixes)
> **Intermedio**: `evidence/FASE-SR-H/final/` (corrida SR-H, 2026-08-28 18:53, pre-hotfix critical_recall)
> **Final**: `evidence/FASE-SR-H2/final/` (corrida H2, 2026-08-28 19:19, post-hotfix D-PF7)
> Propósito: verificar que los fixes de SR-A…SR-G (+H2) se reflejan en el E2E real, no solo en tests unitarios.

## Tabla comparativa por dimensión

| Dimensión | Baseline C (18:30) | SR-H pre-fix (18:53) | H2 post-hotfix (19:19) | Fix responsable | ¿Reflejado en E2E? |
|-----------|--------------------|----------------------|------------------------|-----------------|--------------------|
| **readiness** | NOT_READY | NOT_READY (critical_recall BLOCKED) | **READY_FOR_PUBLICATION** | H2 (`_extract_critical_recall`) | ✅ v4_complete_report `ready=true` |
| **Gates de publicación** | 12 PASSED + 1 BLOCKED (`proposal_asset_alignment`, coverage 43%) | 12 PASSED + 1 BLOCKED (`critical_recall`) | **13/13 sin bloqueos** (3 WARNING no bloqueantes: financial_validity, alignment, pricing_compliance) | SR-B (alignment) + H2 (critical_recall) | ✅ gate_report: `passed=true` ×13 |
| **Alineación propuesta-assets** | BLOCKED: 3/7=0.43, 4 "missing" fantasma del catálogo estático | WARNING no bloqueante, coverage 1.0 | WARNING no bloqueante: **coverage_ratio=1.0** (4/4 actionable: 1 generado + 3 en producción), no_breach=3 fuera del denominador | SR-B (D-PF1: fuente única pain_ledger+presencia) | ✅ gate_report `details.alignment` |
| **unresolved (gate vs delivery)** | **4 vs 1** (divergente, N1) | 0 vs 0 | **0 vs 0** (idéntico, mismo DTO) | SR-A (`compute_unresolved`) | ✅ ambos reportes del run H2 |
| **Promesa comercial** | Catálogo estático del tier (fosilizado; promete servicios sin pain) | pain_ledger + presencia | pain_ledger + presencia (4 comprometidos reales; extras "sin compromiso, fuera del coverage"; WhatsApp sin promesa — B7) | SR-B | ✅ 02_PROPUESTA tabla L52-59 |
| **Claim falso vs GBP** | Publicado (CG-CLAIM-VS-EVIDENCE `passed=false` pero doc publicado) | 0 (gate PASSED, condicionales descartados) | **0** (gate PASSED) | SR-C (self-healing con escalada; no activado: no hubo claim falso) | ✅ commercial_gates_report_diagnostic |
| **`no_hotel_schema` (pain)** | DETECTED (falso positivo H7: parser no soporta JSON-LD array) | AUSENTE (8 schemas reales detectados) | **AUSENTE** (audit: total_schemas=8, hotel_confidence="verified") | SR-E (parser polimórfico + error_message) | ✅ audit_report + pain_ledger |
| **critical_issues** | `["No Hotel schema detected - critical for SEO"]` (falso) | `[]` (vacía — expuso bug latente del gate) | `[]` con **critical_recall PASSED 1.0 + `recall_basis=audit_present_no_critical_issues`** | SR-E (elimina falso) + H2 (gate distingue vacío≠ausente) | ✅ gate_report `details.recall_basis` |
| **coherence score** | 0.86 (0.8644) | 0.88 | **0.88** (gate PASSED ≥ 0.8) | — (mejora por cleanup de falso positivo) | ✅ gate_report `coherence.value=0.88` |
| **promised_assets_exist** | `passed=false` — "Assets no implementados: hotel_schema" | PASSED 1.0 | **PASSED 1.0** ("7 servicios verificados via PROPOSAL_SERVICE_TO_ASSET") | SR-E/D-PF3 | ✅ coherence_validation_post_gen |
| **CG-TIER-CONSISTENCY** | FAILED ('B' frontmatter vs 'D' texto — extractor espurio) | PASSED ('B'=='B') | **PASSED** ("Tier consistente: 'B' en frontmatter y texto") | SR-G (regex canónico MAYÚSCULAS+lookahead) | ✅ commercial_gates_report_diagnostic |
| **CG-TECH-JARGON** | FAILED — 4 términos (Schema, AEO, IAO, schema.org) | PASSED (0) | **PASSED (0 jerga)** — reducción 4→0 | SR-G (glosario único + apply_glossary) | ✅ commercial_gates_report_diagnostic |
| **Identidad de memoria** | `hotel_id` contaminado con UTM (`..._utm_source_google_...`) | Canónico (`hotel_hotelsalentoreal.com`) | **Canónico + lookup cross-run**: corrida H2 encontró análisis previo de SR-H (L-SR2 anti-fragmentación E2E) | SR-D (canonicalización en caller) | ✅ v4_complete_report + corrida.log L71/L79 |
| **Sondas robots/llms (varianza)** | Con UTM: medían homepage 200 (robots 1.0, llms.txt=100 falsos) | Ancladas al origen | **Reales**: ai_crawlers.overall_score=0.5, robots_exists=true, 14 crawlers bloqueados (plan de assets determinista) | SR-F (D-PF6) | ✅ audit_report `ai_crawlers` |
| **Escenarios financieros (COP/mes)** | 6,571,622.4 / 4,042,752.0 / 1,264,435.2 | idénticos | **idénticos** ($6.57M/$4.04M/$1.26M) | — (capa INTACTA por restricción) | ✅ smoke check 7 |
| **Docs cliente 01/02** | Eliminados + BLOCKED_BY_GATES.md | Eliminados + BLOCKED_BY_GATES.md (critical_recall) | **Presentes + ZIP creado** (46.5KB), sin BLOCKED_BY_GATES.md | H2 | ✅ inventario final + smoke check 1/5/6 |
| **delivery_quality_report** | FAIL, blocking=true (G9 fallido) | PASS 5/5 | **PASS 5/5, blocking=false** | SR-A/SR-B/H2 | ✅ delivery_quality_report.json |

## Verificación de reflejo E2E de cada fase

| Fase | Fix | Evidencia E2E de que el fix opera en producción (no solo tests) |
|------|-----|------------------------------------------------------------------|
| SR-A | `compute_unresolved` único | unresolved 0==0 en gate_report y delivery_quality_report del MISMO run (baseline: 4 vs 1) |
| SR-B | D-PF1 fuente única promesa | 02_PROPUESTA promete 4 (3 presencia + 1 pain); matriz NO_BREACH/LINKED; gate actionable=4, coverage 1.0, WARNING no bloqueante |
| SR-C | Self-healing + escalada | CG-CLAIM-VS-EVIDENCE PASSED con 0 claims (camino no activado por ausencia de claim falso; escalada BLOCKED soportada por 20 tests — el BLOCKED real se observó en producción vía critical_recall pre-fix, validando el mecanismo de retención de docs) |
| SR-D | target_id canónico | hotel_id limpio en log + report; lookup cross-run H2→SR-H exitoso (memoria no fragmentada) |
| SR-E | Parser JSON-LD array + contabilización única | audit total_schemas=8 con error_message=null; no_hotel_schema ausente del ledger; present_in_production=3 con presence_status=exists |
| SR-F | Sondas ancladas al origen | audit ai_crawlers reales (0.5, 14 bloqueados) con URL limpia; plan de assets determinista (3 pains → 3 assets) |
| SR-G | Tier extractor + glosario | CG-TIER PASSED 'B'=='B'; CG-TECH-JARGON PASSED 0 términos; 01 doc L212 "Tier B" == evidence_tier B |
| SR-H2 | critical_recall distingue vacío≠ausente | gate_report `critical_recall PASSED 1.0` con `recall_basis=audit_present_no_critical_issues` en producción |

## Regresiones vs baseline

**Ninguna regresión funcional detectada.** Observaciones display (no bloqueantes):

1. `coherence_validation_post_gen.assets_are_justified`: 83% (5/6, warning) → 75% (3/4, error). **No es regresión real**: el mismo 1 asset sin justificación (monthly_report) sobre un denominador menor (6→4 assets generados). El gate de publicación usa el score agregado (0.88 PASSED); el comportamiento "score agregado ignora `is_coherent:false`" ya está registrado como seguimiento FUERA DE ALCANCE en `10-analisis`.
2. Gate `proposal_asset_alignment` mensaje lista "2 missing: Schema Hotel, Schema Organization" (como ASSETS generados) mientras coverage_ratio=1.0 los cubre por presencia — correcto por diseño (generar el asset sería el comportamiento incorrecto cuando el sitio ya tiene los schemas, plan maestro §9 smoke check 4); el mensaje podría priorizar la cobertura por presencia (mejora display futura → seguimiento).
