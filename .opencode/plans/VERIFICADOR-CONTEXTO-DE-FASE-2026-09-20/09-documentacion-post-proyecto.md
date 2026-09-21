# Documentación Post-Proyecto — VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

> Acumulativo. Cada fase de implementación lo actualiza al cerrar; es la fuente de datos de
> FASE-RELEASE para generar CHANGELOG y `GUIA_TECNICA`. **Se crea vacío y se llena por fases.**

## Sección A: Módulos nuevos

| Módulo / archivo | Qué hace | Entra por | Estado |
|---|---|---|---|
| `scripts/validate_governance_numbers.py` | Compara cada aserción sobre un conteo en los documentos de gobierno contra la etiqueta `[N/M]` que el código imprime; publica denominador y tres estados | FASE-A | Pendiente de escribir |
| `scripts/decision_client.py` | Única puerta del repo a un proveedor de decisiones estructuradas: contrato propio, proveedor por entorno, fallo explícito sin decisión por defecto | FASE-B | Pendiente de escribir |
| `scripts/triage_lesson_relevance.py` | Capa de pertinencia **aditiva** sobre `.opencode/lecciones_index.json`: propone lo que el Paso 0 no ancló y nunca elimina una fila anclada | FASE-C | Pendiente de escribir |
| `scripts/build_phase_briefing.py` | Compone por cada fase un pack derivado con las secciones que su prompt **declara** leer, con proveniencia (HEAD + sha por fuente), `--check` de frescura y negativa a emitir un pack más corto en silencio | FASE-D | Pendiente de escribir |
| `…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/` | Directorio de **artefactos generados** dentro del plan (no en `.agents/workflows/`, que tiene contadores de skills) | FASE-D | Pendiente de generar |

## Sección B: Funcionalidades nuevas

- (FASE-A) Detección mecánica de aserciones vencidas sobre conteos, con su población y sus
  familias no cubiertas.
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
| Checks de `run_all_validations.py --quick` | 11 | — | Delta esperado **0** en las cuatro fases de implementación (AC16) |
| Checks del hook `scripts/git_hooks/pre-commit` | 7 | — | Delta esperado **0** |
| `def test_` en `tests/` | — | — | Se publica con su par pre/post y la resta comprobada (R2.3, R2.7) |
| IDs definidos en `.opencode/LECCIONES-INDEX.md` | 320 (re-medido el 2026-09-20) | — | Cambia al archivar; lo regenera RELEASE. A6 documentó que esta cifra vence al escribir cualquier `.md` del corpus |
| **Carga de lectura declarada por fase (bytes / ~tokens)** | **263.973 / ≈65.993** re-medidos el 2026-09-20 sobre las siete lecturas que suma A7 en el plan de referencia (al concebir: 254.010 / ≈63.502; maestro §1, A7 y A6) | — | **AC20 lo mide con el mismo comando en los dos lados**, sobre las fases de este plan; delta cero o negativo es resultado válido y se explica |
| Población bajo el patrón de conteo (A8) | **22 instancias `[N/M]` en 17 líneas** + 2 formas «check N» en `.agents/` (medido el 2026-09-20) | — | El verificador las clasifica en viva / histórica congelada / vigente-correcta y publica las dos últimas con su conteo; sin esa regla AC1 no es verificable |

## Sección E: Archivos afiliados

- [ ] `CHANGELOG.md` (RELEASE)
- [ ] `GUIA_TECNICA.md` (RELEASE)
- [ ] `docs/contributing/REGISTRY.md` (RELEASE — los tres módulos nuevos)
- [ ] `VERSION.yaml` → sync a los seis archivos que lista el executor (RELEASE)
- [ ] `.opencode/LECCIONES-INDEX.md` y `.opencode/lecciones_index.json` (regenerados en cada commit que escribe `.md` de plan con IDs)
