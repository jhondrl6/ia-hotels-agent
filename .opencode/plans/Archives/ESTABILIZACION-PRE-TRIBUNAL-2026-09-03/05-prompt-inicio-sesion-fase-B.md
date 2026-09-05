# FASE-B — Biyección **triple** mapa↔emisión↔narrativa (V1 + N-A1)

**ID**: ESTABILIZACION-PRE-TRIBUNAL-2026-09-03 / FASE-B
**Objetivo**: Fijar la biyección entre lo que `PAIN_SOLUTION_MAP` declara y lo que `detect_pains` puede
realmente emitir. Hoy el mapa declara **27** entradas y `detect_pains` implementa **~18**: hay **9 pains
muertos** que ningún punto de emisión produce. Cada uno recibe una decisión explícita (implementar /
retirar / diferir) y un candado que impide que el drift reaparezca.

> ⚠️ **Enmienda post-FASE-A (N-A1, medida)**: la biyección es **triple**, no doble —
> **mapa ↔ emisión ↔ narrativa**. `detect_pains` es solo la primera mitad del agujero; la segunda es
> `narratives` en `_pain_to_brecha`, que **descarta en silencio** todo `pain_id` que no tenga entrada.
> Cerrar solo mapa↔emisión deja el fix **inerte**: los pains llegan a `_pain_to_brecha` y rebotan.
> Ver §Contexto «N-A1» abajo. A los 9 pains muertos se suman **2 pains vivos que hoy se emiten y se
> descartan** (`no_ga4_enhanced`, `low_ota_divergence`) ⟹ **11 filas** en B1, no 9.

**Dependencias**: FASE-A ✅ (el candado de biyección valida contra el registro canónico, no contra una copia)
**Duración estimada**: 3-4 horas
**Complejidad técnica**: **MEDIA-ALTA**
**Modo de ejecución**: **DIRECTO** (no delegable)
**Skill**: `phased_project_executor.md` v2.18.0
**Presupuesto**: ≤40 iteraciones (R2 tope: 60). ⚠️ **N-A1 agrandó el alcance**: 11 decisiones en vez de
9, un segundo archivo fuente (`v4_diagnostic_generator.py`) y una decisión arquitectónica sobre cómo
`narratives` se relaciona con Capa 1. Las 40 van justas; la regla de partición está en §Restricciones.
**ACs que cierra**: AC4 (biyección **triple** — ver enmienda arriba)

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

### N-A1 — La segunda mitad del agujero (hallazgo de FASE-A, medido)

V1 describe solo **aguas arriba**. FASE-A midió la otra mitad y el resultado cambia el alcance de AC4.

En `modules/commercial_documents/v4_diagnostic_generator.py`:

```python
# :3246  def _pain_to_brecha(self, pain, region=..., audit_result=None) -> Optional[Dict]:
# :3263-3344      narratives = { ...16 claves literales... }
# :3346-3347
        if pain.id not in narratives:
            return None                     # ← caída silenciosa, sin log ni estado
```

Y el consumidor no distingue `None` de «no aplicable»:

```python
# :3205-3209  _identify_brechas
        for pain in pains:
            brecha = self._pain_to_brecha(pain, region=..., audit_result=audit_result)
            if brecha:
                brechas.append(brecha)      # ← el descarte no deja rastro
```

**Medición** (`evidence/FASE-A/faseA_narratives_audit.txt`, script re-ejecutable
`evidence/FASE-A/faseA_narratives_audit.py` — `temp/` está en `.gitignore`, usar la copia de evidence):

| Conjunto | Cardinal |
|----------|----------|
| Capa 1 — `PAIN_SOLUTION_MAP` (universo de `pain_id`) | **27** |
| `narratives` en `_pain_to_brecha` | **16** |
| `pain_id` que `detect_pains` puede emitir | **18** |
| Capa 1 − `narratives` (ausentes) | **11** |
| `narratives` − Capa 1 (huérfanos) | **0** ✅ |

Los **11 ausentes** se parten en **dos grupos disjuntos** que nunca se habían medido juntos:

- **(a) Los 9 pains muertos de V1** — no se emiten *y* no tienen narrativa. Doble muerte: arreglar
  solo la emisión los deja rebotando en `:3346`.
- **(b) 2 pains que SÍ se emiten hoy y SÍ se descartan hoy**: `no_ga4_enhanced`
  (`pain_solution_mapper.py:703-712`, alcanzable) y `low_ota_divergence` (`:452-464`, detrás del guard
  defectuoso de V7). Son **caídas silenciosas vivas en producción**, no hipotéticas.

**Consecuencia para AC4**: cerrar únicamente mapa↔emisión produce un candado **verde con el
diagnóstico igual de mudo** — el patrón exacto de la lección `revalidar-citas-de-código-no-revalida-premisas`.
La biyección debe ser **triple**: mapa ↔ emisión ↔ narrativa.

**`no_ga4_enhanced` es un hallazgo nuevo**: no está en el dossier (§12.3 V1-V16), ni en el plan, ni en
el censo A1 de FASE-A. Es la **novena caída silenciosa viva**. Se registra como seguimiento S12 en
`10-analisis-post-implementacion.md` §5; FASE-B decide su narrativa o su retiro del mapa.

**Los números de impacto tampoco son de `narratives`** (hallazgo posterior, **C-5 / S14**): cada entrada
del dict lee `pain_narratives.get('<pain_id>', <default>)` desde
`config/regional_benchmarks.yaml`, que tiene **4 copias literales** de las mismas 16 claves (una por
región, sin anclajes YAML) y las 4 son **idénticas entre sí** — medido: 0 divergencias. Con los 16
fallbacks hardcodeados en Python son **80 literales para 16 valores**. Rellenar `narratives` a 27 sin
tocar el YAML deja los 11 pains nuevos viviendo solo de su default Python (familia V6/P11/S7:
degradación silenciosa en código dinero-adyacente). Es el **registro #15** que el censo de FASE-A no
contó. Medido en `evidence/FASE-A/faseA_yaml_narratives_audit.txt` y `faseA_yaml_region_blind.txt`.

**Riesgo de orden nuevo B→H**: V7 (FASE-H) arregla el guard `__iter__` de `low_ota_divergence`. Si H se
ejecuta sin que B le haya dado entrada en `narratives`, el pain pasa de **«nunca dispara»** a **«dispara
y se desvanece»** — *peor* para auditabilidad, porque el test de V7 pasa y la caída se vuelve invisible
en vez de inexistente. Ver `dependencias-fases.md` §0.

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
- **Punto de narrativa central** (N-A1): `modules/commercial_documents/v4_diagnostic_generator.py:3246`
  `_pain_to_brecha` → dict `narratives` en `:3263-3344`, guard de descarte en `:3346-3347`
- **Medición de los tres conjuntos**: `evidence/FASE-A/faseA_narratives_audit.txt` (script
  `evidence/FASE-A/faseA_narratives_audit.py`, re-ejecutable para verificar el delta post-B2)

---

## Tareas

### Tarea B1: Decisión por pain muerto

**Objetivo**: Tabla de decisión con una fila por cada uno de los **11** `pain_id` ausentes de
`narratives` (9 muertos de V1 + 2 vivos que se descartan): implementar / retirar / diferir, con
justificación, **señal de dato necesaria** y **decisión de narrativa**.

**Archivos afectados**: ninguno (análisis) + salida nueva `evidence/FASE-B/decision-pains-muertos.md`

> ⚠️ **Colisión de nombre**: `evidence/FASE-B/` **ya existe** y contiene artefactos de la FASE-B de
> **otro plan** (commit `d2a9700`, 2026-08-05, *«tabla de servicios dinámica desde opportunity_scores»*:
> `fase_b_preexist.txt`, `fase_b_safe*.txt`, `verify_breach_consistency_static*`). **No son evidencia de
> esta fase** y no deben leerse como tal ni citarse en B1/B3. Los archivos nuevos de esta fase usan los
> nombres indicados aquí (`decision-pains-muertos.md`, `narratives_post_B2.txt`, `faseB_*.txt`), que no
> chocan con los anteriores.

**Grupo (a) — Los 9 pains muertos de V1** (no se emiten *y* no tienen narrativa):

| pain_id | En el mapa | Narrativa (N-A1) | Señal de dato disponible en el pipeline | Decisión |
|---------|-----------|------------------|------------------------------------------|----------|
| `missing_llmstxt` | `pain_solution_mapper.py:160-168` | ❌ ausente | ✅ `ia_readiness llms_txt=0` — **caso confirmado** | (decidir) |
| `no_motor_reservas` | sí | ❌ ausente | (verificar) | (decidir) |
| `no_ssl` | sí | ❌ ausente | (verificar — nota: `ELEMENTO_KB_TO_PAIN_ID["ssl"] = ("no_ssl", "ssl_guide", None)` en `conditional_generator.py:320`) | (decidir) |
| `no_schema_reviews` | sí | ❌ ausente | (verificar — el audit trae 986 reseñas / 4.5) | (decidir) |
| `missing_alt_text` | sí | ❌ ausente | (verificar) | (decidir) |
| `no_monthly_report` | sí | ❌ ausente | (verificar — es el pain correcto según `service_catalog`, ver AC3) | (decidir) |
| `no_blog_content` | sí | ❌ ausente | (verificar) | (decidir) |
| `no_social_links` | sí | ❌ ausente | (verificar) | (decidir) |
| `low_content_length` | sí | ❌ ausente | (verificar) | (decidir) |

**Grupo (b) — 2 pains VIVOS que se emiten y se descartan hoy** (N-A1, medido). Para estos la pregunta
**no** es «implementar la emisión» — ya existe — sino **«darle entrada en `narratives` o retirarlo del
mapa»**:

| pain_id | Emisión real | Narrativa (N-A1) | Pregunta a decidir | Decisión |
|---------|--------------|------------------|--------------------|----------|
| `no_ga4_enhanced` | ✅ `pain_solution_mapper.py:703-712`, alcanzable | ❌ ausente ⟹ **se descarta en silencio en producción** | ¿Entra en `narratives` (brecha vendible nueva) o se retira del mapa? **Hallazgo nuevo**: no está en el dossier ni en el censo A1 | (decidir) |
| `low_ota_divergence` | ⚠️ `:452-464`, bloqueada por el guard `__iter__` de V7 | ❌ ausente | ¿Entra en `narratives` **ahora**? Obligatorio si se quiere que V7 (FASE-H) no convierta el pain en «dispara y se desvanece» | (decidir) |

**Criterios de aceptación**:
- [ ] Las **11** filas completas (9 del grupo (a) + 2 del grupo (b)) con decisión + justificación +
      señal de dato
- [ ] **Toda decisión "implementar" nombra la entrada de `narratives` que requerirá** (N-A1): un pain
      con emisión nueva y sin narrativa no llega al documento — la decisión estaría incompleta
- [ ] Las 2 filas del grupo (b) tienen decisión explícita **narrativa-o-retiro**, no «implementar»
- [ ] **Regla dura**: ningún pain se marca "implementar" sin una señal de dato **verificable en el
      pipeline actual**. Implementar una detección sin señal real produce pains que disparan en falso —
      exactamente el defecto de `ai_crawler_blocked` (score 0.50 EXACTO = los 14 crawlers marcados
      bloqueados por un parser que devuelve `False` al primer `Disallow:` no vacío, dossier §3)
- [ ] Cada decisión "retirar" indica si el asset asociado sigue existiendo en el catálogo (retirar el
      pain no debe huérfanizar un asset implementado)
- [ ] Cada decisión "diferir" tiene un seguimiento abierto registrado para `10-analisis`
- [ ] Salida escrita en `evidence/FASE-B/decision-pains-muertos.md`

### Tarea B2: Ejecutar la decisión

**Objetivo**: Puntos de emisión reales en `detect_pains` **y su entrada de narrativa correspondiente**
para los pains que se implementan; retiro del mapa para los que no. Un pain con emisión y sin narrativa
no llega al documento (N-A1) — la tarea queda a medias.

**Archivos afectados**:
- `modules/commercial_documents/pain_solution_mapper.py:339` `detect_pains` (ramas de emisión)
- `modules/commercial_documents/pain_solution_mapper.py:60` `PAIN_SOLUTION_MAP` (retiros)
- `modules/commercial_documents/pain_solution_mapper.py:160-168` (`missing_llmstxt`)
- `modules/commercial_documents/pain_solution_mapper.py:311` `ASSET_NAMES` (si algún retiro deja un asset sin nombre)
- **`modules/commercial_documents/v4_diagnostic_generator.py:3263-3344` `narratives`** (N-A1 — la
  segunda mitad; el guard de descarte queda en `:3346-3347`)

**Criterios de aceptación**:
- [ ] Cada pain "implementar" tiene un punto de emisión real, verificable por grep
- [ ] **Cada pain "implementar" tiene además entrada en `narratives`** (o la deriva — ver L-NC4 abajo),
      verificable por grep
- [ ] Cada pain "retirar" fue eliminado del mapa **y** su retiro está justificado en B1
- [ ] `missing_llmstxt` emite cuando `ia_readiness llms_txt == 0` (caso confirmado del dossier)
- [ ] **Los 2 pains del grupo (b) dejan de descartarse en silencio**: `no_ga4_enhanced` y
      `low_ota_divergence` o tienen narrativa o salen del mapa. Ninguno queda en el estado actual
      (emitido + descartado)
- [ ] **NO se introduce narrativa paralela**: si un pain necesita texto en el documento, debe derivar
      del registro canónico de FASE-A (guardrail **L-NC4**: crear tablas paralelas pain_id→texto
      re-fosiliza). ⚠️ **Tensión explícita**: `narratives` *es* una tabla paralela pain_id→texto de 16
      entradas. Rellenarla literal a 27 reproduce el defecto que L-NC4 prohíbe. Camino preferido:
      que `narratives` **derive de Capa 1** o se valide contra ella, y que la decisión quede registrada
      como Decisión Arquitectónica en `10-analisis` §6 (alternativas: derivar / validar / mantener
      literal con candado)
- [ ] **Decisión sobre los pesos de impacto** (S14 / C-5): los números que `narratives` sirve vienen de
      `config/regional_benchmarks.yaml::pain_narratives` — **4 copias literales idénticas** (una por
      región, sin anclajes YAML) + **16 fallbacks hardcodeados** en Python. Si un pain entra en
      `narratives` hay que decidir de dónde sale su peso: ¿YAML en las 4 regiones?, ¿solo el fallback
      Python?, ¿se colapsan las 4 copias en una? Dejarlo sin decidir = los pains nuevos viven de su
      default (degradación silenciosa, familia V6/P11/S7). Va en la **misma** Decisión Arquitectónica
      del punto anterior
- [ ] **Delta re-medido post-B2** con `evidence/FASE-A/faseA_narratives_audit.py`:
      `Capa 1 − narratives = 0`, o cada resto con decisión registrada en B1. Guardar la salida en
      `evidence/FASE-B/narratives_post_B2.txt`
- [ ] El conteo de entradas del mapa post-cambio queda registrado (era 27 según C5)
- [ ] Tests unitarios por rama de emisión nueva

### Tarea B3: Candado de biyección

**Objetivo**: Test que falla fuerte si el mapa declara un `pain_id` que `detect_pains` no puede emitir
**o** que `_pain_to_brecha` no sabe narrar. Es el candado que faltaba y que el dossier señala como parte
de la causa raíz (*"0 tests fijan la biyección"*). Con N-A1 la biyección es **triple**:
`PAIN_SOLUTION_MAP` ↔ `detect_pains` ↔ `narratives`.

**Archivos afectados**:
- `tests/commercial_documents/test_pain_map_bijection.py` (nuevo)

**Criterios de aceptación**:
- [ ] Test escrito y **visto en rojo** contra el estado pre-B2 (TDD)
- [ ] Falla si existe un `pain_id` en `PAIN_SOLUTION_MAP` sin punto de emisión en `detect_pains`
- [ ] Falla si existe un punto de emisión cuyo `pain_id` no está en el mapa (dirección inversa)
- [ ] **Falla si existe un `pain_id` en `PAIN_SOLUTION_MAP` sin entrada en `narratives`** (N-A1)
- [ ] **Falla si `narratives` tiene una clave que no está en `PAIN_SOLUTION_MAP`** (dirección inversa;
      hoy mide 0 huérfanos — el candado debe preservar ese 0)
- [ ] **Habría fallado en rojo contra el estado actual**: los 11 ausentes medidos en
      `evidence/FASE-A/faseA_narratives_audit.txt` son la prueba de que el candado detecta el defecto
      real, no uno sintético
- [ ] Implementado con **guardián AST** (patrón FASE-SR-A), no con regex sobre el fuente — incluye
      extraer las claves del dict literal `narratives` por AST
- [ ] **NO fija valores**: el test verifica la **relación**, no el conteo. Un test que afirma
      `len(PAIN_SOLUTION_MAP) == 27` o `len(narratives) == 16` fosiliza el estado actual en vez de
      proteger la biyección (anti-lección **L-NC10**)
- [ ] Valida los IDs contra el registro canónico de FASE-A, no contra una copia
- [ ] Si B2 decide que `narratives` **derive** de Capa 1 (camino preferido, ver L-NC4 en B2), el candado
      valida la derivación en vez de comparar dos dicts literales

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Candado de biyección | `tests/commercial_documents/test_pain_map_bijection.py` | Verde post-B2; visto en rojo pre-B2 |
| **Candado de narrativa (N-A1)** | ídem | Verde post-B2; **visto en rojo pre-B2 con los 11 ausentes** |
| **`no_ga4_enhanced` llega a `brechas`** | `tests/commercial_documents/` (nuevo o existente) | Emitido por `detect_pains` **y** presente en la salida de `_identify_brechas` — no descartado en `:3346` |
| Emisión de `missing_llmstxt` | `tests/commercial_documents/test_pain_solution_mapper.py` (existente) o nuevo | Verde con fixture `llms_txt=0` |
| Ramas de emisión nuevas | ídem | Una por pain implementado |
| Contract tests de FASE-A | `tests/common/test_service_identity_registry.py` | Siguen en verde (no regresión) |
| Baseline | `tests/quality_gates` + `tests/asset_generation` | 848 passed / 2 skipped + delta de FASE-A preservado |

**Comando de validación**:
```bash
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_pain_map_bijection.py -v > temp/faseB_bijection.txt 2>&1
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_pain_solution_mapper.py -q > temp/faseB_mapper.txt 2>&1
./venv/Scripts/python.exe -m pytest tests/quality_gates tests/asset_generation -q > temp/faseB_baseline.txt 2>&1
./venv/Scripts/python.exe evidence/FASE-A/faseA_narratives_audit.py > evidence/FASE-B/narratives_post_B2.txt 2>&1   # delta N-A1
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

- [ ] **Tests nuevos pasan**: candado de biyección **triple** + ramas de emisión
- [ ] **TDD respetado**: el candado fue visto en rojo antes de B2 (incluida la arista de narrativa,
      con los 11 ausentes)
- [ ] **AC4 cerrado (biyección TRIPLE)**: cada `pain_id` del mapa tiene punto de emisión real **y**
      entrada en `narratives`, **o** fue retirado con justificación registrada. 0 pains muertos sin
      decisión y 0 pains emitidos-y-descartados
- [ ] **Las 11 decisiones documentadas** en `evidence/FASE-B/decision-pains-muertos.md` (9 del grupo
      (a) + `no_ga4_enhanced` y `low_ota_divergence` del grupo (b))
- [ ] **Delta N-A1 re-medido**: `evidence/FASE-B/narratives_post_B2.txt` muestra `Capa 1 − narratives = 0`
      (o cada resto con decisión registrada)
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
  FASE-H. Aunque esté en el mismo archivo, es un defecto distinto.
  ✅ **PERO SÍ darle entrada en `narratives`** (N-A1): es lo que evita que el fix de V7 en FASE-H
  convierta el pain de **«nunca dispara»** a **«dispara y se desvanece»**. Orden forzoso **B→H**;
  si B no lo hace, H hereda una caída invisible con el test en verde. Ver `dependencias-fases.md` §0
- ❌ **NO deduplicar `low_organic_visibility`** (`:677-701`, V8) — FASE-H
- ❌ **NO tocar `VERSION.yaml`** — FASE-RELEASE

**Restricciones técnicas**:
- Python del venv: `./venv/Scripts/python.exe`
- Pytest en lotes pequeños con salida a archivo; **nunca** `tests/commercial_documents` completo
- Al editar `pain_solution_mapper.py`, recordar que FASE-G y FASE-H también lo tocarán: mantener los
  cambios confinados a `detect_pains` y `PAIN_SOLUTION_MAP` para no generar conflictos
  (`dependencias-fases.md` §3)
- Al editar `v4_diagnostic_generator.py` (nuevo por N-A1), **confinarse a `_pain_to_brecha` y su dict
  `narratives` (`:3246-3347`)**. FASE-H tocará el mismo archivo para V6 (`:3197-3202`, el
  `except Exception: return brechas` + caché) y V11 (`:1952`, residuos D6): no entrar en esas regiones
- El guard `if pain.id not in narratives: return None` puede quedarse como está **si** el candado triple
  de B3 lo vuelve inalcanzable para pains del mapa. Hacerlo ruidoso (log/estado) es opcional y debe
  registrarse como decisión; no es el fix estructural

**Dependencia que no se puede modificar**: el registro canónico de FASE-A. Si B1 descubre que el
canónico necesita una entrada nueva, registrarla como seguimiento y **no** editar el registro en esta
fase — volver a FASE-A o abrir un fix específico.

---

## Prompt de Ejecución

```
Actúa como arquitecto de software senior en el repo iah-cli (Python, Windows, ./venv/Scripts/python.exe).

OBJETIVO: Fijar la biyección TRIPLE PAIN_SOLUTION_MAP ↔ detect_pains ↔ narratives. El mapa declara 27
entradas, detect_pains implementa ~18 y narratives solo 16: hay 9 pains muertos (V1) + 2 pains vivos que
se emiten y se descartan en silencio hoy (N-A1, medido por FASE-A). Cada uno recibe decisión explícita +
candado.

CONTEXTO:
- Plan: /.opencode/plans/Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/
- Dossier: .opencode/context/CONTEXT-AUDITORIA-BRECHAS-VS-MODULOS-SALENTOREAL-2026-09-03.md §12.3 V1 y §4 caída #4
- FASE-A completada: registro canónico disponible (ver evidence/FASE-A/censo-registros.md §1-7 y las
  correcciones §8). Capa 1 = PAIN_SOLUTION_MAP; Capa 2 = modules/common/service_identity.py
- N-A1 (precondición dura): evidence/FASE-A/faseA_narratives_audit.txt — Capa 1=27, narratives=16,
  detect_pains=18, ausentes=11, huérfanos=0. Ver 05-prompt §Contexto «N-A1» y 10-analisis §5 S6/S12/S13
- Archivos centrales:
  · modules/commercial_documents/pain_solution_mapper.py (:60 mapa, :311 ASSET_NAMES, :339 detect_pains,
    :160-168 missing_llmstxt, :646 detect_pains_for_analytics, :703-712 no_ga4_enhanced)
  · modules/commercial_documents/v4_diagnostic_generator.py (:3246 _pain_to_brecha, :3263-3344
    narratives, :3346-3347 guard de descarte silencioso)

TAREAS:
1. B1 Decisión por pain muerto — 11 filas. Grupo (a) 9 muertos: missing_llmstxt, no_motor_reservas,
   no_ssl, no_schema_reviews, missing_alt_text, no_monthly_report, no_blog_content, no_social_links,
   low_content_length. Grupo (b) 2 vivos que se descartan: no_ga4_enhanced (hallazgo NUEVO, no está en
   el dossier) y low_ota_divergence (interacción con V7/FASE-H). Cada una con implementar/retirar/diferir
   + justificación + SEÑAL DE DATO VERIFICABLE + entrada de narratives que requerirá. Salida:
   evidence/FASE-B/decision-pains-muertos.md
2. B2 Ejecutar: puntos de emisión reales Y entrada de narrativa para los implementados; retiro del mapa
   para los demás. missing_llmstxt emite con ia_readiness llms_txt==0 (caso confirmado). Los 2 del grupo
   (b) dejan de descartarse. Preferir que narratives DERIVE de Capa 1 antes que rellenarlo literal
   (L-NC4) y registrar la elección como Decisión Arquitectónica.
3. B3 Candado de biyección TRIPLE: tests/commercial_documents/test_pain_map_bijection.py — guardián AST
   sobre los tres conjuntos, ambas direcciones, valida la RELACIÓN (no el conteo), visto en rojo antes
   de B2 con los 11 ausentes reales.
4. Re-medir el delta con evidence/FASE-A/faseA_narratives_audit.py > evidence/FASE-B/narratives_post_B2.txt

CRITERIOS:
- AC4 (triple): cada pain_id del mapa tiene emisión real Y narrativa, o fue retirado con justificación.
  0 pains muertos sin decisión y 0 pains emitidos-y-descartados
- Regla dura: ningún pain "implementar" sin señal de dato verificable en el pipeline actual
- Baseline 848/2 + delta FASE-A preservado; run_all_validations.py --quick 7/7

RESTRICCIONES (críticas):
- NO agregar el 8º servicio; NO tocar proposal_asset_alignment.py, publication_gates.py, VERSION.yaml
- NO corregir el guard __iter__ (:453, V7) ni deduplicar low_organic_visibility (:677-701, V8) → FASE-H.
  SÍ darle narratives a low_ota_divergence: orden forzoso B→H, si no H lo vuelve "dispara y se desvanece"
- En v4_diagnostic_generator.py confinarse a :3246-3347; NO entrar en :3197-3202 (V6) ni :1952 (V11)
- NO crear tablas paralelas pain_id→texto (L-NC4); el texto deriva del canónico de FASE-A. OJO: los
  pesos de impacto viven en config/regional_benchmarks.yaml::pain_narratives (4 copias literales
  IDENTICAS, una por region) + 16 fallbacks Python = 80 literales para 16 valores (S14/C-5). Decidir
  explicitamente de donde sale el peso de cada pain nuevo o hereda un default en silencio
- NO editar el registro canónico de FASE-A; si falta una entrada, registrar seguimiento
- Pytest en lotes pequeños con salida a archivo; NUNCA tests/commercial_documents completo (~8GB)
- Si se agota el presupuesto: NUNCA dejar el candado de B3 en rojo en master. B1 (las 11 decisiones) es
  la parte barata y debe completarse; particionar B2 y entregar la fase 🟡 En curso con handoff

POST-EJECUCIÓN (obligatoria):
Actualizar dependencias-fases.md, README.md, 06-checklist-implementacion.md,
09-documentacion-post-proyecto.md (A/B/D/E), 10-analisis-post-implementacion.md (incl. las 11 Decisiones
Arquitectónicas + la decisión N-A1 sobre narratives↔Capa 1 + seguimientos de los "diferir"),
evidence/FASE-B/ (decision-pains-muertos.md + narratives_post_B2.txt + logs).
Luego: log_phase_completion.py --fase FASE-B --desc "..." --check-manual-docs  (SIN --release).
Commit referenciando FASE-B.
```
