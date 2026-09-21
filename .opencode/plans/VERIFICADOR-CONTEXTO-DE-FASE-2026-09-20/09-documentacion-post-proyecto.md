# Documentación Post-Proyecto — VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

> Acumulativo. Cada fase de implementación lo actualiza al cerrar; es la fuente de datos de
> FASE-RELEASE para generar CHANGELOG y `GUIA_TECNICA`. **Se crea vacío y se llena por fases.**

## Sección A: Módulos nuevos

| Módulo / archivo | Qué hace | Entra por | Estado |
|---|---|---|---|
| `scripts/validate_governance_numbers.py` | Compara cada aserción sobre un conteo en los documentos de gobierno contra la etiqueta `[N/M]` que el código imprime; publica denominador y tres estados | FASE-A | **Escrito y verificado offline el 2026-09-21** (914 líneas, stdlib-only, standalone; `--report` / `--json` / inyectables `--governance-doc`/`--source`/`--hook`) |
| `scripts/decision_client.py` | Única puerta del repo a un proveedor de decisiones estructuradas: contrato propio, proveedor por entorno, fallo explícito sin decisión por defecto | FASE-B | Pendiente de escribir |
| `scripts/triage_lesson_relevance.py` | Capa de pertinencia **aditiva** sobre `.opencode/lecciones_index.json`: propone lo que el Paso 0 no ancló y nunca elimina una fila anclada | FASE-C | Pendiente de escribir |
| `scripts/build_phase_briefing.py` | Compone por cada fase un pack derivado con las secciones que su prompt **declara** leer, con proveniencia (HEAD + sha por fuente), `--check` de frescura y negativa a emitir un pack más corto en silencio | FASE-D | Pendiente de escribir |
| `…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/` | Directorio de **artefactos generados** dentro del plan (no en `.agents/workflows/`, que tiene contadores de skills) | FASE-D | Pendiente de generar |

## Sección B: Funcionalidades nuevas

- (FASE-A, **cerrada el 2026-09-21**) Detección mecánica de aserciones vencidas sobre conteos, con
  su población y sus familias no cubiertas. Sobre el árbol vigente reproduce **A1–A4 y ninguna
  otra** (`findings[]` con `assertion_id`, `claimed`, `observed`, `occurrences[]`), clasifica las
  **24 instancias** de la población en viva-hallazgo (5) / viva-correcta (11) / histórica congelada
  (8) / no resuelta (0), y publica `coverage_basis` con las cuatro familias no cubiertas medidas en
  runtime. Tres estados sin colapso (`SIN-HALLAZGOS` / `AUSENTE` / `LECTOR-FALLIDO`), seis mutantes
  del guard real en `evidence/…/FASE-A/mutation/` y delta 0 en los conteos que otros planes pinean.
- (FASE-B) Costura neutra de proveedor, con contract test de forma y **extensibilidad a un segundo
  proveedor probada con un proveedor falso**. Sin llamadas de red: la comparación real es deuda D7.
- (FASE-C) Informe de candidatos de pertinencia por plan, con umbral publicado, sus términos de
  búsqueda y la **aceptabilidad** que dispara la deuda D6.
- (FASE-D) Unificación de la carga de lectura declarada por fase, y medición del delta con el mismo
  comando en los dos lados (AC20).

## Sección C: Correcciones

- Las aserciones A1–A4 medidas en `01-plan-maestro.md` §1 **no se corrigen** en este plan
  (AC17). Quedan como deuda D1 con su disparador.

## Sección D: Métricas acumulativas

| Métrica | Pre (a medir por cada fase) | Post | Notas |
|---|---|---|---|
| Checks de `run_all_validations.py --quick` | 11 | **11** (delta **0**, 2026-09-21) | Delta esperado **0** en las cuatro fases de implementación (AC16) — cumplido por FASE-A |
| Checks del hook `scripts/git_hooks/pre-commit` | 7 | **7** (delta **0**) | Delta esperado **0** — cumplido. Quién lo afirma en `tests/`: `test_validate_plan_closure.py` (`[5/7]`) |
| `def test_` en `tests/` | **4.307** | **4.330** (resta **+23**, verificada: 4.330 − 4.307 = 23) | Se publica con su par pre/post y la resta comprobada (R2.3, R2.7). La selección de la fase es `tests/quality_gates/governance_numbers/`: 23 funciones / 28 casos |
| IDs definidos en `.opencode/LECCIONES-INDEX.md` | 320 (re-medido el 2026-09-20) | — | Cambia al archivar; lo regenera RELEASE. A6 documentó que esta cifra vence al escribir cualquier `.md` del corpus |
| **Carga de lectura declarada por fase (bytes / ~tokens)** | **263.973 / ≈65.993** re-medidos el 2026-09-20 sobre las siete lecturas que suma A7 en el plan de referencia (al concebir: 254.010 / ≈63.502; maestro §1, A7 y A6) | **263.973 / ≈65.993** re-medidos el 2026-09-21 con `stat -c %s` sobre los siete archivos: **sin cambio** (las fases de `REFACTOR-WHATSAPP` no volvieron a escribirlos). FASE-A no reduce lectura: es FASE-D quien debe mover esta fila | **AC20 lo mide con el mismo comando en los dos lados**, sobre las fases de este plan; delta cero o negativo es resultado válido y se explica |
| Población bajo el patrón de conteo (A8) | **22 instancias `[N/M]` en 17 líneas** + 2 formas «check N» en `.agents/` (medido el 2026-09-20) | **22 / 17 / 2, re-medido el 2026-09-21: idéntico** (el verificador las agrupa en 24 instancias auditables = 22 + 2) | El verificador las clasifica en viva / histórica congelada / vigente-correcta y publica las dos últimas con su conteo; sin esa regla AC1 no es verificable |

## Sección E: Archivos afiliados

- [ ] `CHANGELOG.md` (RELEASE)
- [ ] `GUIA_TECNICA.md` (RELEASE)
- [ ] `docs/contributing/REGISTRY.md` (RELEASE — los tres módulos nuevos)
- [ ] `VERSION.yaml` → sync a los seis archivos que lista el executor (RELEASE)
- [ ] `.opencode/LECCIONES-INDEX.md` y `.opencode/lecciones_index.json` (regenerados en cada commit que escribe `.md` de plan con IDs)
