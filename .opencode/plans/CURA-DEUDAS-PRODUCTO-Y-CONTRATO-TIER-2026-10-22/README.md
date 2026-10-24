# CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22

> Plan de absorción de dos contextos: las deudas de producto verificadas (`D16`–`D28` + `N1`–`N7`) y el contrato plantilla↔tier↔veredicto (ítems A y C). Cierre con un ensayo determinista, una corrida `v4complete` de Hotel Don Alfonso, certificación FASE-VERIFY y release 4.82.0.

**Origen**: `.opencode/context/CONTEXT-DEUDAS-PRODUCTO-VERIFICADAS-2026-10-21.md` + `.opencode/context/CONTEXT-CONTRATO-PLANTILLA-TIER-2026-10-12.md` (solo lectura).
**Workflow**: `.agents/workflows/phased_project_executor.md` (v2.27.0). **Una fase = una sesión.**
**Versión objetivo**: 4.82.0.

## Estrategia corregida

La cura se ancla en el camino real del producto:

- `spark` se **retira**; `D19` se cierra por retiro, no por reparación.
- `D28` se cura en **los dos** caminos: `gbp_auditor` (v4audit) y `PainSolutionMapper`/`V4DiagnosticGenerator` (v4complete).
- `D25-ter` exige retirar o derivar las **cinco** tablas regionales, no solo reparar `BenchmarkLoader`.
- `D16` publica el score sobre **`/90`** y retira la rama API muerta.
- `D24` declara **muerto** el stub de `modules/scrapers/booking_scraper.py`; no toca el scraper real de `autonomous_researcher`.
- `D21`/`P6.5` **no se absorben**: quedan con su dueño hasta letra expresa.
- `D26` sigue diferida.
- Antes de la corrida pagada hay un **E2E-PRE** determinista que valida onboarding, render, revisor, juez y ensamblaje de paquete sin inferencia.

## Archivos del plan

| Archivo | Contenido |
|---------|-----------|
| `00-lecciones-capitalizadas.md` | Paso 0: consultas al corpus, lecciones capitalizadas, descartes y frontera Knowledge Center/código local |
| `01-plan-maestro.md` | ACs (AC1–AC8), alcance y vallas, fases, decisiones, pertinencia del E2E y matriz de camino |
| `dependencias-fases.md` | Diagrama, conflictos de archivos, restricciones de secuencia, estado de fases |
| `06-checklist-implementacion.md` | Estado maestro por fase |
| `09-documentacion-post-proyecto.md` | Acumulador de métricas (fuente única del número por fase) |
| `10-analisis-post-implementacion.md` | Resumen de ejecución, matriz de verificación, lecciones, seguimientos, decisiones |
| `05-prompt-inicio-sesion-fase-{A,B,C,D,E,F,H1,H2,E2E-PRE,E2E,VERIFY,RELEASE}.md` | 12 prompts — uno por fase, uno por sesión |

## Progreso

| Fase | Complejidad | Estado |
|------|-------------|--------|
| Preparación | — | ✅ 2026-10-22 |
| FASE-A — retiro de `spark` + guardián | MEDIA-ALTA | ✅ 2026-10-22 (métricas: `09-documentacion-post-proyecto.md` §D) |
| FASE-B — ítem A (2 claims) | ALTA | ✅ 2026-10-23 (métricas: `09-documentacion-post-proyecto.md` §D) |
| FASE-C — ítem C | MEDIA | ✅ 2026-10-23 (métricas: `09-documentacion-post-proyecto.md` §D) |
| FASE-D — contrato GBP (ambos caminos) | ALTA | ✅ 2026-10-23 (métricas: `09-documentacion-post-proyecto.md` §D) |
| FASE-E — lector único de benchmarks | ALTA | ✅ 2026-10-23 (métricas: `09-documentacion-post-proyecto.md` §D) |
| FASE-F — umbrales por semántica | MEDIA | ✅ |
| FASE-H1 — `D16` y `D24` | MEDIA | ✅ 2026-10-23 (métricas: `09-documentacion-post-proyecto.md` §D) |
| FASE-H2 — `D18`/`D22`/`D23`/`D20` | BAJA | ✅ 2026-10-24 (métricas: `09-documentacion-post-proyecto.md` §D) |

| FASE-E2E-PRE — ensayo determinista | MEDIA | ✅ 2026-10-24 → `LISTO_PARA_E2E` (métricas: `09-documentacion-post-proyecto.md` §D; veredicto y condiciones: `evidence/…/FASE-E2E-PRE/pre-vuelo.md`) |
| FASE-E2E — v4complete Don Alfonso | MEDIA | ⏳ |
| FASE-VERIFY — certificación AC1–AC8 | MEDIA | ⏳ |
| FASE-RELEASE-4.82.0 | BAJA | ⏳ |

**Cómo ejecutar una fase**: abrir sesión nueva, leer su `05-prompt-inicio-sesion-fase-*.md`, ejecutar solo esa fase, cerrar con su checklist + `log_phase_completion.py`. Ver `dependencias-fases.md` §Estado.

**Nota de herramientas**: este runtime usa `Agent` para subagentes. Los prompts no usan `delegate_task`, `notify_on_complete` ni `terminal(timeout=…)`.
