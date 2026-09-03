# FASE-B — Biyección mapa↔emisión de `detect_pains` (V1)

**ID**: ESTABILIZACION-PRE-TRIBUNAL-2026-09-03 / FASE-B
**Objetivo**: Fijar la biyección entre lo que `PAIN_SOLUTION_MAP` declara y lo que `detect_pains` puede
realmente emitir. Hoy el mapa declara **27** entradas y `detect_pains` implementa **~18**: hay **9 pains
muertos** que ningún punto de emisión produce. Cada uno recibe una decisión explícita (implementar /
retirar / diferir) y un candado que impide que el drift reaparezca.
**Dependencias**: FASE-A ✅ (el candado de biyección valida contra el registro canónico, no contra una copia)
**Duración estimada**: 3-4 horas
**Complejidad técnica**: **MEDIA-ALTA**
**Modo de ejecución**: **DIRECTO** (no delegable)
**Skill**: `phased_project_executor.md` v2.18.0
**Presupuesto**: ≤40 iteraciones (R2 tope: 60)
**ACs que cierra**: AC4

---

## Contexto

El dossier §12.3 **V1** establece que la caída silenciosa #4 (`missing_llmstxt`) **no es un caso, es un
patrón sistemático**:

> *"Además de `missing_llmstxt`, `detect_pains` nunca emite: `no_motor_reservas`, `no_ssl`,
> `no_schema_reviews`, `missing_alt_text`, `no_monthly_report`, `no_blog_content`, `no_social_links`,
> `low_content_length` (grep: 0 puntos de emisión en `modules/`). El mapa declara 27 (C5),
> `detect_pains` implementa ~18."*

Esto es la manifestación **aguas arriba** de la causa raíz: módulos que detectan pero no llegan al
ledger. Y tiene una consecuencia comercial directa — el mapa promete soluciones para brechas que el
pipeline es estructuralmente incapaz de diagnosticar.

El caso confirmado más claro es `missing_llmstxt`: existe en el mapa
(`pain_solution_mapper.py:160-168`), el asset **se implementa y se generó** en la corrida SalenteReal,
pero **ninguna rama de `detect_pains` lo emite** — y el sitio realmente no tiene `llms.txt`
(`ia_readiness llms_txt=0`). Es decir: había una brecha real, un asset generado para ella, y el
diagnóstico no la mencionó.

### Por qué es DIRECTO y no delegable

La dificultad no es el código — es la **decisión de producto** por cada pain muerto. Implementar una
detección agrega una brecha vendible al diagnóstico; retirarla del mapa deja de prometerla. Ambas
cambian lo que se le ofrece al cliente. Un subagente no tiene el contexto comercial para decidirlo.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A — Fuente única de identidad | ✅ Completada (verificar en `06-checklist-implementacion.md`) |

### Base Técnica Disponible

- **Registro canónico** de FASE-A (ubicación y forma: ver `evidence/FASE-A/censo-registros.md`)
- **Contract tests** de FASE-A en verde
- **Baseline**: 848 passed / 2 skipped + los tests nuevos de FASE-A
- **Patrón de test**: guardián AST de FASE-SR-A
- **Punto de emisión central**: `modules/commercial_documents/pain_solution_mapper.py:339` `detect_pains`
  (y `:646` `detect_pains_for_analytics`)

---

## Tareas

### Tarea B1: Decisión por pain muerto

**Objetivo**: Tabla de decisión con una fila por cada uno de los 9 pains muertos: implementar / retirar
/ diferir, con justificación y **señal de dato necesaria**.

**Archivos afectados**: ninguno (análisis) + salida nueva `evidence/FASE-B/decision-pains-muertos.md`

**Los 9 pains a decidir** (V1):

| pain_id | En el mapa | Señal de dato disponible en el pipeline | Decisión |
|---------|-----------|------------------------------------------|----------|
| `missing_llmstxt` | `pain_solution_mapper.py:160-168` | ✅ `ia_readiness llms_txt=0` — **caso confirmado** | (decidir) |
| `no_motor_reservas` | sí | (verificar) | (decidir) |
| `no_ssl` | sí | (verificar — nota: `ELEMENTO_KB_TO_PAIN_ID["ssl"] = ("no_ssl", "ssl_guide", None)` en `conditional_generator.py:320`) | (decidir) |
| `no_schema_reviews` | sí | (verificar — el audit trae 986 reseñas / 4.5) | (decidir) |
| `missing_alt_text` | sí | (verificar) | (decidir) |
| `no_monthly_report` | sí | (verificar — es el pain correcto según `service_catalog`, ver AC3) | (decidir) |
| `no_blog_content` | sí | (verificar) | (decidir) |
| `no_social_links` | sí | (verificar) | (decidir) |
| `low_content_length` | sí | (verificar) | (decidir) |

**Criterios de aceptación**:
- [ ] Las 9 filas completas con decisión + justificación + señal de dato
- [ ] **Regla dura**: ningún pain se marca "implementar" sin una señal de dato **verificable en el
      pipeline actual**. Implementar una detección sin señal real produce pains que disparan en falso —
      exactamente el defecto de `ai_crawler_blocked` (score 0.50 EXACTO = los 14 crawlers marcados
      bloqueados por un parser que devuelve `False` al primer `Disallow:` no vacío, dossier §3)
- [ ] Cada decisión "retirar" indica si el asset asociado sigue existiendo en el catálogo (retirar el
      pain no debe huérfanizar un asset implementado)
- [ ] Cada decisión "diferir" tiene un seguimiento abierto registrado para `10-analisis`
- [ ] Salida escrita en `evidence/FASE-B/decision-pains-muertos.md`

### Tarea B2: Ejecutar la decisión

**Objetivo**: Puntos de emisión reales en `detect_pains` para los pains que se implementan; retiro del
mapa para los que no.

**Archivos afectados**:
- `modules/commercial_documents/pain_solution_mapper.py:339` `detect_pains` (ramas de emisión)
- `modules/commercial_documents/pain_solution_mapper.py:60` `PAIN_SOLUTION_MAP` (retiros)
- `modules/commercial_documents/pain_solution_mapper.py:160-168` (`missing_llmstxt`)
- `modules/commercial_documents/pain_solution_mapper.py:311` `ASSET_NAMES` (si algún retiro deja un asset sin nombre)

**Criterios de aceptación**:
- [ ] Cada pain "implementar" tiene un punto de emisión real, verificable por grep
- [ ] Cada pain "retirar" fue eliminado del mapa **y** su retiro está justificado en B1
- [ ] `missing_llmstxt` emite cuando `ia_readiness llms_txt == 0` (caso confirmado del dossier)
- [ ] **NO se introduce narrativa paralela**: si un pain necesita texto en el documento, debe derivar
      del registro canónico de FASE-A (guardrail **L-NC4**: crear tablas paralelas pain_id→texto
      re-fosiliza)
- [ ] El conteo de entradas del mapa post-cambio queda registrado (era 27 según C5)
- [ ] Tests unitarios por rama de emisión nueva

### Tarea B3: Candado de biyección

**Objetivo**: Test que falla fuerte si el mapa declara un `pain_id` que `detect_pains` no puede emitir.
Es el candado que faltaba y que el dossier señala como parte de la causa raíz (*"0 tests fijan la
biyección"*).

**Archivos afectados**:
- `tests/commercial_documents/test_pain_map_bijection.py` (nuevo)

**Criterios de aceptación**:
- [ ] Test escrito y **visto en rojo** contra el estado pre-B2 (TDD)
- [ ] Falla si existe un `pain_id` en `PAIN_SOLUTION_MAP` sin punto de emisión en `detect_pains`
- [ ] Falla si existe un punto de emisión cuyo `pain_id` no está en el mapa (dirección inversa)
- [ ] Implementado con **guardián AST** (patrón FASE-SR-A), no con regex sobre el fuente
- [ ] **NO fija valores**: el test verifica la **relación**, no el conteo. Un test que afirma
      `len(PAIN_SOLUTION_MAP) == 27` fosiliza el estado actual en vez de proteger la biyección
      (anti-lección **L-NC10**)
- [ ] Valida los IDs contra el registro canónico de FASE-A, no contra una copia

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Candado de biyección | `tests/commercial_documents/test_pain_map_bijection.py` | Verde post-B2; visto en rojo pre-B2 |
| Emisión de `missing_llmstxt` | `tests/commercial_documents/test_pain_solution_mapper.py` (existente) o nuevo | Verde con fixture `llms_txt=0` |
| Ramas de emisión nuevas | ídem | Una por pain implementado |
| Contract tests de FASE-A | `tests/common/test_service_identity_registry.py` | Siguen en verde (no regresión) |
| Baseline | `tests/quality_gates` + `tests/asset_generation` | 848 passed / 2 skipped + delta de FASE-A preservado |

**Comando de validación**:
```bash
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_pain_map_bijection.py -v > temp/faseB_bijection.txt 2>&1
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_pain_solution_mapper.py -q > temp/faseB_mapper.txt 2>&1
./venv/Scripts/python.exe -m pytest tests/quality_gates tests/asset_generation -q > temp/faseB_baseline.txt 2>&1
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

⚠️ **NUNCA** correr `tests/commercial_documents` completo (~8GB). Solo archivos específicos.

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase, actualizar INMEDIATAMENTE (antes de cerrar la sesión):

1. **`dependencias-fases.md`** — marcar FASE-B ✅, fecha, notas
2. **`README.md` del plan** — tabla de progreso + métricas
3. **`06-checklist-implementacion.md`** — fila FASE-B, AC4, trazabilidad V1 y caída #4 de §4
4. **`09-documentacion-post-proyecto.md`** — Sección A (si hay módulo nuevo), B (funcionalidad:
   biyección + candado), D (métricas acumulativas), E (archivos afiliados)
5. **`10-analisis-post-implementacion.md`**
   - Resumen de Ejecución: fila FASE-B
   - **Decisiones Arquitectónicas**: las 9 decisiones de B1 con rationale (obligatorio)
   - Lecciones Aprendidas + Métricas + Seguimientos abiertos (los pains "diferir" van aquí)
6. **`evidence/FASE-B/`** — `decision-pains-muertos.md` + logs de tests

**Cierre con script**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-B --desc "Biyeccion mapa-emision detect_pains + candado (V1)" --check-manual-docs
```
**SIN `--release`.**

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] **Tests nuevos pasan**: candado de biyección + ramas de emisión
- [ ] **TDD respetado**: el candado fue visto en rojo antes de B2
- [ ] **AC4 cerrado**: cada `pain_id` del mapa tiene punto de emisión real **o** fue retirado con
      justificación registrada. 0 pains muertos sin decisión
- [ ] **Las 9 decisiones documentadas** en `evidence/FASE-B/decision-pains-muertos.md`
- [ ] **Ningún pain implementado sin señal de dato verificable**
- [ ] **Contract tests de FASE-A siguen en verde**
- [ ] **Baseline preservado**: 848 passed / 2 skipped + delta FASE-A
- [ ] **Validaciones**: `run_all_validations.py --quick` 7/7
- [ ] **`dependencias-fases.md` actualizado**
- [ ] **`06-checklist-implementacion.md` actualizado**
- [ ] **`09-documentacion-post-proyecto.md` actualizado** (A/B/D/E)
- [ ] **`10-analisis-post-implementacion.md` actualizado** (incl. las 9 Decisiones)
- [ ] **Evidencia preservada**: `evidence/FASE-B/`
- [ ] **`log_phase_completion.py` ejecutado SIN `--release`**
- [ ] **Commit hecho** referenciando FASE-B

---

## Restricciones

**Alcance — qué NO está en esta fase**:
- ❌ **NO agregar el 8º servicio** al registro (dossier §8.5) — la unificación 7→8 empeora
  `coverage_ratio` (0.571 → 0.500), medido
- ❌ **NO tocar `proposal_asset_alignment.py`** — FASE-C
- ❌ **NO tocar `publication_gates.py`** — FASE-D/F/G
- ❌ **NO implementar la propuesta dinámica** (punto 8) — FASE-C
- ❌ **NO corregir el guard `__iter__` de `low_ota_divergence`** (`pain_solution_mapper.py:453`, V7) —
  FASE-H. Aunque esté en el mismo archivo, es un defecto distinto
- ❌ **NO deduplicar `low_organic_visibility`** (`:677-701`, V8) — FASE-H
- ❌ **NO tocar `VERSION.yaml`** — FASE-RELEASE

**Restricciones técnicas**:
- Python del venv: `./venv/Scripts/python.exe`
- Pytest en lotes pequeños con salida a archivo; **nunca** `tests/commercial_documents` completo
- Al editar `pain_solution_mapper.py`, recordar que FASE-G y FASE-H también lo tocarán: mantener los
  cambios confinados a `detect_pains` y `PAIN_SOLUTION_MAP` para no generar conflictos
  (`dependencias-fases.md` §3)

**Dependencia que no se puede modificar**: el registro canónico de FASE-A. Si B1 descubre que el
canónico necesita una entrada nueva, registrarla como seguimiento y **no** editar el registro en esta
fase — volver a FASE-A o abrir un fix específico.

---

## Prompt de Ejecución

```
Actúa como arquitecto de software senior en el repo iah-cli (Python, Windows, ./venv/Scripts/python.exe).

OBJETIVO: Fijar la biyección PAIN_SOLUTION_MAP ↔ detect_pains. El mapa declara 27 entradas y
detect_pains implementa ~18: hay 9 pains muertos. Cada uno recibe decisión explícita + candado.

CONTEXTO:
- Plan: .opencode/plans/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/
- Dossier: .opencode/context/CONTEXT-AUDITORIA-BRECHAS-VS-MODULOS-SALENTOREAL-2026-09-03.md §12.3 V1 y §4 caída #4
- FASE-A completada: registro canónico disponible (ver evidence/FASE-A/censo-registros.md)
- Archivo central: modules/commercial_documents/pain_solution_mapper.py (:60 mapa, :311 ASSET_NAMES,
  :339 detect_pains, :160-168 missing_llmstxt, :646 detect_pains_for_analytics)

TAREAS:
1. B1 Decisión por pain muerto (9 filas: missing_llmstxt, no_motor_reservas, no_ssl, no_schema_reviews,
   missing_alt_text, no_monthly_report, no_blog_content, no_social_links, low_content_length). Cada una
   con implementar/retirar/diferir + justificación + SEÑAL DE DATO VERIFICABLE. Salida:
   evidence/FASE-B/decision-pains-muertos.md
2. B2 Ejecutar: puntos de emisión reales para los implementados; retiro del mapa para los demás.
   missing_llmstxt emite con ia_readiness llms_txt==0 (caso confirmado).
3. B3 Candado de biyección: tests/commercial_documents/test_pain_map_bijection.py — guardián AST,
   valida la RELACIÓN (no el conteo), visto en rojo antes de B2.

CRITERIOS:
- AC4: cada pain_id del mapa tiene emisión real o fue retirado con justificación. 0 pains muertos sin decisión
- Regla dura: ningún pain "implementar" sin señal de dato verificable en el pipeline actual
- Baseline 848/2 + delta FASE-A preservado; run_all_validations.py --quick 7/7

RESTRICCIONES (críticas):
- NO agregar el 8º servicio; NO tocar proposal_asset_alignment.py, publication_gates.py, VERSION.yaml
- NO corregir el guard __iter__ (:453, V7) ni deduplicar low_organic_visibility (:677-701, V8) → FASE-H
- NO crear tablas paralelas pain_id→texto (L-NC4); el texto deriva del canónico de FASE-A
- Pytest en lotes pequeños con salida a archivo; NUNCA tests/commercial_documents completo (~8GB)

POST-EJECUCIÓN (obligatoria):
Actualizar dependencias-fases.md, README.md, 06-checklist-implementacion.md,
09-documentacion-post-proyecto.md (A/B/D/E), 10-analisis-post-implementacion.md (incl. las 9 Decisiones
Arquitectónicas + seguimientos de los "diferir"), evidence/FASE-B/.
Luego: log_phase_completion.py --fase FASE-B --desc "..." --check-manual-docs  (SIN --release).
Commit referenciando FASE-B.
```
