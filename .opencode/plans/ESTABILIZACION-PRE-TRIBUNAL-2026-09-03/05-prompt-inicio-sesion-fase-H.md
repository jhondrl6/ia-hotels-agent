# FASE-H — Quirúrgicos (Nivel 3.8)

**ID**: ESTABILIZACION-PRE-TRIBUNAL-2026-09-03 / FASE-H
**Objetivo**: Seis correcciones localizadas e independientes: V6 (`except Exception` silencioso),
V7 (guard `__iter__` triple defecto), V8 (emisión duplicada), V11 (residuos D6), V13 (dos
`MetadataValidator` gemelos) y V12 (trampa `.env` — **documentar**, no editar).
**Dependencias**: FASE-B ✅ (V8 deduplica una emisión cuya biyección ya está fijada), FASE-F ✅, **FASE-G ✅ (orden forzoso por conflicto de archivo en `pain_solution_mapper.py`)**
**Duración estimada**: 2-3 horas
**Complejidad técnica**: **BAJA-MEDIA**
**Modo de ejecución**: **DELEGADO** — 2 subagentes en paralelo sobre archivos disjuntos; parent integra
**Skill**: `phased_project_executor.md` v2.18.0
**Presupuesto**: ≤35 iteraciones (R2 tope: 60)
**Hallazgos que cierra**: V6, V7, V8, V11, V12 (documentado), V13 · **Deuda relacionada**: P11 (misma familia que V6)

---

## Contexto

Nivel 3.8 del dossier §12.5: *"Quirúrgicos"*. Son defectos reales pero **independientes entre sí** y de
radio local — ninguno cambia una decisión arquitectónica. Por eso esta fase es la segunda delegable del
plan (junto con FASE-E).

El denominador común de V6, V7 y V8 es una familia de defectos ya documentada en memoria de proyecto:
**degradación silenciosa**. El NameError del gate `tier_c` (import faltante + `except` amplio),
`precision_tier` defaulteando a `"C"` bajo `except` desnudo (deuda **P11**), y ahora V6. Misma forma:
el sistema pierde información y no lo dice.

### V6 — Excepción silenciosa en el generador de brechas (verbatim)

> `except Exception: return brechas` + cache (`v4_diagnostic_generator.py:3197-3202`): si `detect_pains`
> lanza, el diagnóstico sale con **cero brechas** y sin señal (mismo patrón que el NameError silencioso
> del gate `tier_c`, ya documentado en memoria de proyecto).

### V7 — `low_ota_divergence` aún más muerto que §4.8 (verbatim, triple defecto)

> El `isinstance(direct_field.value, (int, float, str))` interno (`pain_solution_mapper.py:455`) es
> **código muerto** por el guard de `:453` (un numérico jamás pasa `hasattr(__iter__)`). Además el umbral
> `< 0.3` asume **fracción** (un 20% numérico nunca dispara; un string `"20"` pasaría el guard y
> `float("20") = 20` tampoco; solo un string `"0.2"` podría), y `ota_field` (`:450`) **se lee y no se
> usa**. Triple defecto: guard, unidades, evidencia ignorada.

El pipeline **conoce** `direct_channel=0.2` ("default") — tiene el dato y no puede usarlo.

### V8 — Emisión duplicada (verbatim)

> `low_organic_visibility` puede emitirse **dos veces** en una llamada (rama `not ga4_available` `:694` +
> rama `organic < 1000` `:716`).

**Contexto adicional del dossier §3**: `no_analytics_configured` y `low_organic_visibility`
(`pain_solution_mapper.py:677-701`) se emiten cuando `use_ga4=False`, que `main.py:2424` define como
*"True only if GA4 credentials exist"*. **Ninguna mide el sitio del hotel**; `low_organic_visibility` es
**compañera hardcoded** de la primera (comentario `:693`). 2 de 3 brechas = **57% de los $4.04M/mes**
derivan de UN hecho: nuestra credencial ausente. Y el detalle **filtra el flag CLI `--ga4-property-id`
al cliente**.

⚠️ **Límite de alcance**: V8 es la **deduplicación**, no re-escribir la premisa de las dos brechas. La
premisa (que derivan de nuestra credencial y no del sitio del hotel) es un hallazgo del dossier §3 que
**este plan no aborda** — va como seguimiento abierto para el tribunal / decisión comercial.

### V11 — Residuos D6: el texto viejo sobrevive en dos sitios (verbatim)

> Rama else `v4_diagnostic_generator.py:1952` («El sitio puede ser nuevo o tener tráfico bajo») para
> no-ERROR sin field data, y recomendaciones `v4_comprehensive.py:1841` («site may be new or low
> traffic»). **El fix D6 (`e544a59`) solo cubrió la rama ERROR.**

**Contexto de la línea de tiempo** (dossier §1, re-encuadre post-QMind): el tema PageSpeed tiene **3
ciclos previos** — D6 Zione (2026-08-02/03, commit `e544a59`), SR-F (2026-08-28, causa:
`GOOGLE_PAGESPEED_API_KEY` placeholder inválido) y el fix **OPS RESUELTO** 2026-08-31 con
`PAGESPEED_API_KEY` sembrada y `PageSpeedClient` VERIFIED (CrUX perf 55, LCP 3.03). La corrida auditada
(**12:28**) es **anterior** al cierre del fix (~**15:08**, commits `f914e0e`/`f77f8ae`, release v4.74.0)
— por eso el doc aún muestra el error.

Lo que **sigue abierto** y ningún ciclo previo abordó (los puntos (a)-(d) del dossier §1):
- **(a)** la capa de pain descarta el ERROR sin pain ni justificación (`poor_performance` exige
  `mobile_score is not None`, `pain_solution_mapper.py:416-417`)
- **(b)** el doc inserta el string crudo en inglés del API (*"Invalid URL or request: API key not
  valid..."*) en vez del mensaje sanitizado que CONTEXT-H especificó (*"API de PageSpeed no disponible
  (verificar clave)"*)
- **(c)** esa fila vive en una tabla **sin header ni separador** (no renderiza como tabla)
- **(d)** `execution_trace` lista `pagespeed_api` en `executed` **Y** en `skipped` simultáneamente

### V12 — Trampa `.env` confirmada empíricamente (verbatim)

> `GOOGLE_PAGESPEED_API_KEY` = **3 chars** (placeholder inválido), `PAGESPEED_API_KEY` = **39**. Si se
> elimina la canónica, el fallback resuelve la inválida y el síntoma reaparece.

⚠️ **Es decisión OPS, no de código.** Se **documenta** en `09-documentacion-post-proyecto.md` con la
recomendación explícita; **no se edita `.env`** en una fase de refactorización. Cadena de fallback
vigente: `modules/data_validation/external_apis/pagespeed_client.py:25`.

### V13 — Dos `MetadataValidator` gemelos (verbatim)

> `data_validation/metadata_validator.py` (**live** vía `v4_comprehensive.py:33`) y
> `modules/data_validation/metadata_validator.py` (**solo tests**) con checks idénticos — deuda de duplicación.

**Contexto del dossier §4 caída #7 (corregido por C4)**: el validator **SÍ** detecta vacíos (CRITICAL
`title` `data_validation/metadata_validator.py:150-159`, HIGH `description` `:196-205`); los vacíos
disparan `metadata_defaults` con **narrativa equivocada** («por defecto»). La vía silenciosa real es
`metadata=None` si el audit crashea (`v4_comprehensive.py:811-812`).

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A … FASE-F | ✅ Completadas |
| FASE-G — Ceguera de gates | ✅ Completada (**requisito**: FASE-G tocó `pain_solution_mapper.py`-adyacentes y `v4_comprehensive.py:1789-1814`; esta fase edita `:1841` del mismo archivo) |

### Base Técnica Disponible

- Biyección triple mapa↔emisión↔narrativa fija (FASE-B) — V8 deduplica sobre un contrato ya estable
- Estado `NOT_EVALUATED` (FASE-F) — V6 puede usarlo en vez de degradar en silencio
- Registro canónico (FASE-A) — V11 no debe crear textos paralelos (L-NC4)
- **Baseline**: 848 passed / 2 skipped + delta A-G

---

## Tareas

### Tarea H1: V7 — Guard `__iter__` → validación numérica  · *Subagente 1*

**Archivos afectados**:
- `modules/commercial_documents/pain_solution_mapper.py:450` (`ota_field`, leído y no usado)
- `modules/commercial_documents/pain_solution_mapper.py:453` (guard `hasattr(direct_field.value, '__iter__')`)
- `modules/commercial_documents/pain_solution_mapper.py:455` (`isinstance` muerto)

**Criterios de aceptación**:
- [ ] El guard `__iter__` reemplazado por **validación numérica** con **normalización de unidades**
      (fracción vs porcentaje: `0.2` y `20` deben significar lo mismo)
- [ ] `ota_field` (`:450`) **se usa** — deja de ser evidencia ignorada
- [ ] El código muerto `isinstance(...)` de `:455` queda vivo o se elimina (no dejar ambos)
- [ ] `low_ota_divergence` (HIGH, priority 1) **puede disparar** con el valor que el pipeline ya conoce
      (`direct_channel=0.2` "default")
- [ ] Tests de las combinaciones de unidad: fracción, porcentaje numérico, string fracción, string porcentaje

### Tarea H2: V6 — `except Exception` → logging + estado visible  · *Subagente 1*

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py:3197-3202` (`_identify_brechas`, `except Exception: return brechas` + cache)

**Criterios de aceptación**:
- [ ] La excepción **se loggea** con el traceback (no se traga)
- [ ] El diagnóstico resultante lleva un **estado visible** de que la detección de brechas falló — usar
      `NOT_EVALUATED` de FASE-F si aplica
- [ ] **Cero brechas por fallo ya no es indistinguible de cero brechas por sitio sano** (semántica
      «vacío ≠ ausente», lección SR-H2)
- [ ] La cache no persiste el resultado degradado como si fuera válido
- [ ] Test: `detect_pains` lanzando ⟹ estado visible + log
- [ ] **Alineado con la deuda P11** (`precision_tier` defaulteando a `"C"` bajo `except` desnudo,
      `main.py:2149-2167`): si el patrón de corrección es reutilizable, registrarla como lección — pero
      **NO corregir P11 en esta fase** (está fuera del dossier Nivel 3.8)

### Tarea H3: V8 dedup + V11 residuos D6  · *Subagente 2*

**Archivos afectados**:
- `modules/commercial_documents/pain_solution_mapper.py:694` (rama `not ga4_available`) y `:716` (rama `organic < 1000`)
- `modules/commercial_documents/v4_diagnostic_generator.py:1952` (rama else «El sitio puede ser nuevo o tener tráfico bajo»)
- `modules/auditors/v4_comprehensive.py:1841` («site may be new or low traffic»)

**Criterios de aceptación (V8)**:
- [ ] `low_organic_visibility` **no puede emitirse dos veces** en una llamada
- [ ] Test que ejercita ambas ramas simultáneamente (`not ga4_available` **y** `organic < 1000`)
- [ ] ⚠️ **NO re-escribir la premisa** de las dos brechas analytics (que derivan de nuestra credencial
      ausente, no del sitio del hotel) — va como **seguimiento abierto**, no como fix de esta fase

**Criterios de aceptación (V11)**:
- [ ] Los dos textos residuales leen `performance.status/message` reales, como ya hace la rama ERROR
      desde el fix D6 (`e544a59`, código vigente en `v4_diagnostic_generator.py:1945-1952`)
- [ ] El string crudo en inglés del API queda reemplazado por el **mensaje sanitizado** que CONTEXT-H
      especificó (*"API de PageSpeed no disponible (verificar clave)"*) — punto **(b)** del dossier §1
- [ ] La tabla del punto **(c)** tiene header y separador (renderiza como tabla)
- [ ] El punto **(d)** (`execution_trace` lista `pagespeed_api` en `executed` Y `skipped`) queda
      corregido **o** registrado como seguimiento con justificación si excede el radio de V11
- [ ] El punto **(a)** (la capa de pain descarta el ERROR: `poor_performance` exige
      `mobile_score is not None`, `pain_solution_mapper.py:416-417`) queda **abordado o registrado como
      seguimiento explícito** — no omitido en silencio
- [ ] **NO crear textos paralelos** (L-NC4): el mensaje sanitizado sale de la fuente, no de una tabla nueva

### Tarea H4: V13 gemelos + V12 documentación OPS  · *Subagente 2 + parent*

**Archivos afectados**:
- `data_validation/metadata_validator.py` (**live**, vía `v4_comprehensive.py:33`)
- `modules/data_validation/metadata_validator.py` (**solo tests**)
- `09-documentacion-post-proyecto.md` (documentación de V12)

**Criterios de aceptación (V13)**:
- [ ] Un solo `MetadataValidator`, o uno delega explícitamente al otro
- [ ] Los tests que apuntaban al gemelo muerto siguen cubriendo los checks (CRITICAL `title` `:150-159`,
      HIGH `description` `:196-205`)
- [ ] `v4_comprehensive.py:33` sigue importando el live sin cambio de comportamiento
- [ ] La vía silenciosa real (`metadata=None` si el audit crashea, `v4_comprehensive.py:811-812`) queda
      **registrada como seguimiento** — no es parte de V13

**Criterios de aceptación (V12)**:
- [ ] **Documentado, NO editado**: `09-documentacion-post-proyecto.md` registra que
      `GOOGLE_PAGESPEED_API_KEY` = 3 chars (placeholder inválido) y `PAGESPEED_API_KEY` = 39, que la
      cadena de fallback es `pagespeed_client.py:25`, y que eliminar la canónica **reintroduce el síntoma**
- [ ] Recomendación OPS explícita: eliminar el placeholder inválido o poblarlo con una clave válida
- [ ] ❌ **Ningún cambio a `.env`** en esta fase

---

## Delegación

| Track | Tareas | Archivos | Agente |
|-------|--------|----------|--------|
| 1 | H1 + H2 | `pain_solution_mapper.py:450-455` · `v4_diagnostic_generator.py:3197-3202` | Subagente 1 |
| 2 | H3 + H4 | `pain_solution_mapper.py:694,716` · `v4_diagnostic_generator.py:1952` · `v4_comprehensive.py:1841` · los dos `metadata_validator.py` · `09-documentacion-post-proyecto.md` | Subagente 2 |

⚠️ **Los tracks comparten `pain_solution_mapper.py` y `v4_diagnostic_generator.py`** en regiones
**distintas** (`:450-455` vs `:694,716`; `:3197-3202` vs `:1952`). Son paralelizables, pero el parent
**debe verificar que no hubo solapamiento** al integrar. Si se prefiere cero riesgo, ejecutar H1+H2
primero y H3+H4 después en la misma sesión (sigue siendo una fase, R1 se respeta).

**Prompt de delegación**: cada subagente recibe el verbatim del hallazgo, sus líneas exactas, los
criterios de aceptación y la lista de lo que **no** debe tocar. Los subagentes **no** deciden si un punto
queda como fix o como seguimiento — lo propone y el parent decide.

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Unidades de `low_ota_divergence` | `tests/commercial_documents/test_pain_solution_mapper.py` | Dispara con fracción **y** con porcentaje numérico |
| `ota_field` usado | ídem | Verde |
| V6 excepción visible | `tests/commercial_documents/test_v4_diagnostic_generator.py` | Estado visible + log; vacío ≠ ausente |
| V8 no-duplicación | `tests/commercial_documents/test_pain_solution_mapper.py` | Ambas ramas simultáneas ⟹ una sola emisión |
| V11 textos dinámicos | `tests/commercial_documents/test_v4_diagnostic_generator.py` | Sin string crudo del API; mensaje sanitizado |
| V13 gemelo único | `tests/data_validation/test_metadata_validator.py` | Checks preservados con un solo validador |
| Baseline | `tests/quality_gates` + `tests/asset_generation` | 848/2 + delta A-G preservado |

**Comando de validación**:
```bash
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_pain_solution_mapper.py -v > temp/faseH_mapper.txt 2>&1
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_v4_diagnostic_generator.py -q > temp/faseH_diag.txt 2>&1
./venv/Scripts/python.exe -m pytest tests/data_validation/test_metadata_validator.py -q > temp/faseH_meta.txt 2>&1
./venv/Scripts/python.exe -m pytest tests/quality_gates tests/asset_generation -q > temp/faseH_baseline.txt 2>&1
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
git diff --stat .env 2>/dev/null || echo "OK: .env sin cambios"
```

⚠️ **NUNCA** correr `tests/commercial_documents` completo (~8GB). Solo los archivos nombrados.

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`** — marcar FASE-H ✅, fecha, notas
2. **`README.md` del plan** — tabla de progreso
3. **`06-checklist-implementacion.md`** — fila FASE-H, trazabilidad V6/V7/V8/V11/V12/V13 + caídas #1 y #8 de §4 + deuda P11
4. **`09-documentacion-post-proyecto.md`** — Sección B, D, E **+ la documentación OPS de V12**
5. **`10-analisis-post-implementacion.md`**
   - Resumen de Ejecución: fila FASE-H (notas de la delegación y del solapamiento de archivos)
   - **Seguimientos abiertos** (obligatorio en esta fase — varios puntos se registran en vez de fixearse):
     premisa de las brechas analytics (57% de $4.04M/mes deriva de nuestra credencial), punto (a) de
     PageSpeed, punto (d) `execution_trace`, `metadata=None` en crash del audit, deuda **P11**,
     filtración del flag CLI `--ga4-property-id` al cliente
   - Lecciones + Métricas
6. **`evidence/FASE-H/`** — logs de tests + captura del diff de los textos V11

**Cierre con script**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-H --desc "Quirurgicos V6/V7/V8/V11/V13 + V12 documentado (OPS)" --check-manual-docs
```
**SIN `--release`.**

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] **Tests nuevos pasan** (los 6 grupos de la tabla)
- [ ] **V7 cerrado**: `low_ota_divergence` dispara con el dato que el pipeline ya conoce; `ota_field` usado
- [ ] **V6 cerrado**: excepción loggeada + estado visible; cero brechas por fallo ≠ cero por sitio sano
- [ ] **V8 cerrado**: una sola emisión con ambas ramas activas
- [ ] **V11 cerrado**: los 2 textos residuales leen status/message reales; mensaje sanitizado en vez del string crudo
- [ ] **V13 cerrado**: un solo `MetadataValidator` con los checks preservados
- [ ] **V12 documentado y `.env` SIN cambios** (verificar con `git diff --stat .env`)
- [ ] **Integración de los 2 tracks verificada por el parent** (sin solapamiento en los archivos compartidos)
- [ ] **Seguimientos abiertos registrados** en `10-analisis` (los puntos no fixeados)
- [ ] **Contract tests de FASE-A y biyección de FASE-B siguen en verde**
- [ ] **Baseline preservado**: 848/2 + delta A-G
- [ ] **Validaciones**: `run_all_validations.py --quick` 7/7
- [ ] **Los 5 archivos de plan actualizados**
- [ ] **Evidencia preservada**: `evidence/FASE-H/`
- [ ] **`log_phase_completion.py` ejecutado SIN `--release`**
- [ ] **Commit hecho** referenciando FASE-H

---

## Restricciones

**Alcance — qué NO está en esta fase**:
- ❌ **NO editar `.env`** (V12 es decisión OPS)
- ❌ **NO re-escribir la premisa de las brechas analytics** (`no_analytics_configured` /
      `low_organic_visibility` derivan de nuestra credencial ausente) — seguimiento abierto
- ❌ **NO corregir la deuda P11** (`precision_tier` en `main.py:2149-2167`) — fuera del Nivel 3.8;
      solo registrar la similitud de patrón
- ❌ **NO tocar `publication_gates.py`** — cerrado en FASE-D/F/G
- ❌ **NO tocar `delivery_quality_report.py`** — FASE-F
- ❌ **NO tocar `alignment_result.py` ni `proposal_asset_alignment.py`** — FASE-C/F
- ❌ **NO crear tablas paralelas de pain_id→texto** (L-NC4)
- ❌ **NO tocar `VERSION.yaml`** — FASE-RELEASE
- ❌ **NO ejecutar un `v4complete` completo** — la única corrida E2E es FASE-I

**Restricciones técnicas**:
- Python del venv: `./venv/Scripts/python.exe`
- Pytest en lotes pequeños con salida a archivo; **nunca** `tests/commercial_documents` completo
- Los subagentes en Windows **no pueden** importar `bs4`/`selenium` — si un track lo necesitara, ejecutarlo en el parent
- `pain_solution_mapper.py` fue tocado por FASE-B y `v4_comprehensive.py` por FASE-G: **re-verificar
      líneas** antes de editar
- En Git Bash usar rutas con slash; `sed` falla con rutas Windows — si hace falta edición scripted,
      usar `temp/*.py` con raw-strings

---

## Prompt de Ejecución

```
Actúa como integrador senior en el repo iah-cli (Python, Windows, ./venv/Scripts/python.exe).
Vas a delegar 2 tracks e integrar tú.

OBJETIVO: Seis quirúrgicos independientes del Nivel 3.8 del dossier: V6 (except silencioso), V7 (guard
__iter__ triple defecto), V8 (emisión duplicada), V11 (residuos D6), V13 (MetadataValidator gemelos),
V12 (trampa .env → DOCUMENTAR, no editar).

CONTEXTO:
- Plan: .opencode/plans/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/
- Dossier §12.3 V6/V7/V8/V11/V12/V13 (verbatim), §1 puntos (a)-(d) de PageSpeed, §12.5 Nivel 3.8
- FASE-A…G ✅. pain_solution_mapper.py fue tocado por FASE-B; v4_comprehensive.py por FASE-G →
  re-verificar líneas antes de editar
- Denominador común de V6/V7/V8: DEGRADACIÓN SILENCIOSA (misma familia que el NameError del gate tier_c
  y que precision_tier defaulteando a "C" bajo except desnudo, deuda P11)

TRACKS:
- Subagente 1 → H1 (V7): pain_solution_mapper.py:450 (ota_field leído y no usado), :453 (guard
  hasattr __iter__), :455 (isinstance muerto). Validación numérica + normalización de unidades
  (0.2 y 20 deben significar lo mismo) + usar ota_field. low_ota_divergence debe poder disparar con
  direct_channel=0.2 que el pipeline YA conoce.
            → H2 (V6): v4_diagnostic_generator.py:3197-3202 `except Exception: return brechas` + cache.
  Loggear traceback + estado visible (NOT_EVALUATED de FASE-F si aplica). Cero brechas por fallo ≠ cero
  por sitio sano. La cache no persiste el resultado degradado como válido.
- Subagente 2 → H3 (V8): pain_solution_mapper.py:694 y :716 → low_organic_visibility no puede emitirse
  dos veces. Test con ambas ramas simultáneas.
              → H3 (V11): v4_diagnostic_generator.py:1952 y v4_comprehensive.py:1841 → leer
  performance.status/message reales como ya hace la rama ERROR desde el fix D6 (e544a59). Reemplazar el
  string crudo del API por el mensaje sanitizado "API de PageSpeed no disponible (verificar clave)".
  La tabla del punto (c) con header y separador.
              → H4 (V13): unificar data_validation/metadata_validator.py (LIVE vía
  v4_comprehensive.py:33) con modules/data_validation/metadata_validator.py (solo tests). Preservar
  CRITICAL title (:150-159) y HIGH description (:196-205).
- PARENT → H4 (V12): DOCUMENTAR en 09-documentacion-post-proyecto.md que GOOGLE_PAGESPEED_API_KEY=3
  chars (placeholder inválido) y PAGESPEED_API_KEY=39, fallback en pagespeed_client.py:25, y que
  eliminar la canónica reintroduce el síntoma. Recomendación OPS. NO EDITAR .env.
- Los tracks comparten pain_solution_mapper.py y v4_diagnostic_generator.py en REGIONES DISTINTAS.
  Verificar tú que no hubo solapamiento al integrar. Si prefieres cero riesgo, ejecuta H1+H2 primero y
  H3+H4 después en la misma sesión.

CRITERIOS:
- V6/V7/V8/V11/V13 cerrados con test; V12 documentado con .env SIN cambios (git diff --stat .env)
- Contract tests de FASE-A y biyección de FASE-B siguen en verde
- Baseline 848/2 + delta A-G preservado; run_all_validations.py --quick 7/7

RESTRICCIONES (críticas):
- NO editar .env; NO re-escribir la premisa de las brechas analytics (57% de $4.04M/mes deriva de
  nuestra credencial ausente → SEGUIMIENTO ABIERTO); NO corregir la deuda P11 (solo registrar la
  similitud de patrón)
- NO tocar publication_gates.py, delivery_quality_report.py, alignment_result.py,
  proposal_asset_alignment.py, VERSION.yaml
- NO crear tablas paralelas pain_id→texto (L-NC4); el mensaje sanitizado sale de la fuente
- NO ejecutar un v4complete completo (la única corrida E2E es FASE-I)
- Pytest en lotes pequeños con salida a archivo; NUNCA tests/commercial_documents completo (~8GB)
- Los subagentes en Windows no pueden importar bs4/selenium

SEGUIMIENTOS OBLIGATORIOS a registrar en 10-analisis (puntos NO fixeados en esta fase):
premisa de las brechas analytics · punto (a) PageSpeed (poor_performance exige mobile_score is not
None, pain_solution_mapper.py:416-417) · punto (d) execution_trace (pagespeed_api en executed Y
skipped) · metadata=None en crash del audit (v4_comprehensive.py:811-812) · deuda P11 · filtración del
flag CLI --ga4-property-id al cliente

POST-EJECUCIÓN (obligatoria):
Actualizar dependencias-fases.md, README.md, 06-checklist-implementacion.md,
09-documentacion-post-proyecto.md (B/D/E + documentación OPS de V12),
10-analisis-post-implementacion.md (Seguimientos abiertos + lecciones), evidence/FASE-H/.
Luego: log_phase_completion.py --fase FASE-H --desc "..." --check-manual-docs  (SIN --release).
Commit referenciando FASE-H.
```
