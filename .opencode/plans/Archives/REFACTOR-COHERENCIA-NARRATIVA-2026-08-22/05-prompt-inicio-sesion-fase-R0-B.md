# FASE-R0-B — Fix B1+B4: Sección 4 "Fugas Principales" dinámica desde pain_ledger

**ID**: FASE-R0-B
**⚠️ FASE DE MAYOR COMPLEJIDAD TÉCNICA DEL PLAN ⚠️**
**Objetivo**: Reemplazar las 3 fugas hardcoded de la Sección 4 del diagnóstico por una sección dinámica generada desde el pain_ledger (fuente única de verdad), con contador dinámico en el título. WhatsApp solo aparece como fuga cuando existe un conflicto real.
**Dependencias**: FASE-R0-A ✅ (soft: mismo archivo `.py`, zona distinta).
**Duración estimada**: 60-90 minutos
**Skill**: phased_project_executor v2.15.0
**Lectura previa obligatoria**: `.opencode/context/Historico/CONTEXT-REFACTOR-COHERENCIA-NARRATIVA-FUGAS-WHATSAPP-2026-08-22.md` — §2 (Bug 1, Bug 4), §4.1, §4.5, §6.3, §8 (AC1, AC3, AC4, AC7, AC9)

---

## Contexto

La Sección 4 del template (`diagnostico_v6_template.md` L65-77) contiene 3 fugas de texto estático que siempre mencionan WhatsApp ("Fuga 1 — Contacto perdido por WhatsApp incorrecto"), independiente de los datos del audit. Para Zione (whatsapp VERIFIED, 7 brechas reales) esto produce la contradicción origen de todo el plan. El sistema YA tiene la fuente de verdad dinámica (`PainSolutionMapper.detect_pains()` → `_identify_brechas()` → `_get_brecha_pesos()` → `brechas_section`); el template simplemente la ignora.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-R0-A | ✅ Completada (B2: Quick Win #1 corregido) |

### Base Técnica (verificada contra código vivo 2026-08-22)

- **Template**: `modules/commercial_documents/templates/diagnostico_v6_template.md` (234 líneas). Sección 4 actual:

```markdown
## 4. 🔍 LAS 3 FUGAS PRINCIPALES                                    ← L65 (B4: número fijo)

De las ${brechas_total_count} brechas técnicas detectadas, estas ${brechas_destacadas_count} son las que más dinero le están costando HOY.    ← L67 (dinámico, CORRECTO — conservar)
Las otras ${brechas_restantes_count} se resuelven en el plan completo de la Fase 2.                                                           ← L68 (dinámico, CORRECTO — conservar)

### Fuga 1 — Contacto perdido por WhatsApp incorrecto                ← L70-77 (B1: TODO hardcoded)
Cuando un huésped quiere reservar directo, busca el WhatsApp del hotel. Si el número en Google Maps es diferente al de su web, pierde la reserva.

### Fuga 2 — Visibilidad insuficiente en Google Maps
Cuando alguien busca "hotel boutique cerca de ${hotel_landmark}", su hotel aparece más abajo que la competencia. Pocos llegan a su web.

### Fuga 3 — Las IA no recomiendan su hotel
Cuando alguien le pregunta a ChatGPT o Google AI "hotel boutique en ${hotel_region}", si su web no tiene los datos correctos, no aparece en la respuesta.
```

- **Generador**: `modules/commercial_documents/v4_diagnostic_generator.py` (3,544 líneas):
  - Carga del template: L499 (`string.Template`); render: `_render_template()` L1542-1546 con **`safe_substitute()`** — una variable faltante NO rompe la generación: deja el literal `${var}` en el output (corrupción silenciosa). El guard correcto es verificar 0 residuos `${` en el render.
  - **Dict de renderizado** (zona L838-992, anclar por `'brechas_section'`): ya contiene `'brechas_section'`, `'brechas_resumen_section'`, `'brechas_total_count'` (L921), `'brechas_destacadas_count'` (L922), `'brechas_restantes_count'` (L923). `brechas_pesos` y `brechas_destacadas` se calculan en L835-836, en scope del dict.
  - **Filtro VERIFIED_IN_SITE**: dentro de `_identify_brechas()` L3043-3044 — `pains = [p for p in pains if p.id not in verified_ids]` (NO existe un método `_get_brechas()`). El nuevo método DEBE consumir la lista YA filtrada (vía `_get_brecha_pesos()`).
  - **Estructura de cada brecha** (retorno de `_pain_to_brecha()` L3224-3230): dict con keys `pain_id`, `severity`, `nombre`, `impacto`, `detalle` — `nombre = pain.name or narrative['nombre']`, `detalle = pain.description or narrative['detalle']` (dinámicos, FASE-A-COHERENCIA D1). Ordenamiento por SEVERIDAD (L3059-3061), no por impacto.
  - `_build_brechas_section()` L2574-2590: patrón de referencia EXACTO a replicar (renderiza `### [BRECHA {i}] {b['nombre']}` + detalle dinámico).
  - `_build_whatsapp_conflict_note()` L2635-2675: retorna `""` si no hay conflicto real (referencia de patrón condicional correcto).
- **PainSolutionMapper** (`modules/commercial_documents/pain_solution_mapper.py`): `whatsapp_conflict` ES un pain_id válido del sistema (caso especial L847-850: "El conflicto justifica generar el asset"). Por tanto, cuando exista un conflicto real, el pain aparece en el ledger y la fuga puede derivarse de él — NO se necesita lógica paralela.
- **Tests de referencia**: `tests/commercial_documents/test_diagnostic_generator.py` (D8 tests — fixtures de audit simulado).
- **Base de tests**: 3,361 funciones tras FASE-R0-A. Esta fase agrega 4 tests.

---

## Modo de Ejecución: DIRECTO (agente principal) — NO delegable

**Justificación** (executor §Regla-de-Decisión, lección DT-3): la fase incluye una decisión de diseño cross-layer (reutilización de narrativa dinámica del pain_ledger + integración con el filtrado VERIFIED_IN_SITE + contrato template/generador/render-dict). Un subagente carece del contexto completo para tomarla correctamente. Además, los tests requieren el venv Windows (`./venv/Scripts/python.exe`).

**Presupuesto de iteraciones** (R2, máx. 60): ~10 investigación (leer generate(), _identify_brechas, _pain_to_brecha, brechas_destacadas, template completo) + ~15 implementación + ~15 tests + ~10 docs/post-ejecución + margen.

---

## Decisiones de Diseño (pre-aprobadas en el plan maestro)

| ID | Decisión | Rationale |
|----|----------|-----------|
| **D-NC1** | `fugas_count_display = str(len(brechas_destacadas))` — **NO** `min(3, len(brechas_pesos))` (sugerencia del CONTEXT §4.5) | Para Zione destacadas=7: `min(3,…)` mostraría "3" en el título mientras la intro dice "estas 7" — recrearía exactamente la incoherencia que este plan corrige. El título debe coincidir con las fugas listadas |
| **D-NC2** | **Minimal-diff**: conservar en el template el título (con variable) y las líneas de intro con contadores dinámicos (L67-68, ya correctas); reemplazar SOLO los bloques de fugas (L70-77) por `${fugas_principales_section}` | Reduce superficie de cambio; el render usa `safe_substitute()` (variable faltante = residuo `${var}` visible, no crash); preserva variables existentes (`${brechas_destacadas_count}`, `${brechas_restantes_count}` siguen usadas); la intro ya es dinámica y correcta |
| **D-NC3** | Narrativa directa vía `brecha['nombre']`/`brecha['detalle']` del dict ya calculado | Nunca crash, nunca invención, sin desalineación de índices. **NO usar `_get_brecha_nombre(audit_result, idx)`**: ese método re-calcula la lista COMPLETA sin filtrar (L2515-2520) y sus índices absolutos se desalinearían con `brechas_destacadas` |
| **D-NC6** | NO crear una nueva tabla estática pain_id → narrativa: reutilizar la narrativa dinámica de `_pain_to_brecha()` (16 pain_ids, `nombre`/`detalle` derivados de `pain.name`/`pain.description`) | Una tabla nueva duplicaría narrativas estáticas (re-fosilización, viola L27 que este mismo plan cita) y la propuesta original contenía un error semántico (`low_seo_score` → "Visibilidad insuficiente en Google Maps", narrativa que corresponde a `low_gbp_score`; el human_label real de `low_seo_score` es "SEO Local Bajo", L3182-3186) | Tabla estática de 8 entradas (propuesta original del CONTEXT §4.1) |

---

## Tareas

### Tarea 1: Investigación previa (obligatoria antes de escribir código)

1. Leer el método `generate()` del generador para localizar: cómo se calculan `brechas_pesos` (L835) y `brechas_destacadas` (L836), y qué estructura tienen (dicts con keys `pain_id`, `severity`, `nombre`, `impacto`, `detalle` — confirmar leyendo el retorno de `_pain_to_brecha()` L3224-3230).
2. Leer `_identify_brechas()` (zona L2964-3066) para confirmar el punto exacto donde la lista YA está filtrada por VERIFIED_IN_SITE (L3043-3044) y el ordenamiento por severidad (L3059-3061).
3. Leer el template completo (234 líneas) y confirmar todas las variables que consume la Sección 4.
4. Confirmar con grep que `${fugas_principales_section}` y `${fugas_count_display}` NO existen aún en ningún template (evitar colisiones).

### Tarea 2: Nuevo método `_build_fugas_principales_section()` en el generador

**Archivos afectados**: `modules/commercial_documents/v4_diagnostic_generator.py`

**Firma sugerida** (ajustar a las estructuras reales halladas en Tarea 1):
```python
def _build_fugas_principales_section(self, audit_result, brechas_destacadas) -> str:
```

**Comportamiento requerido**:
1. Iterar sobre `brechas_destacadas` (lista YA filtrada por VERIFIED_IN_SITE — la misma que alimenta los contadores del template).
2. Para cada brecha, generar usando EXCLUSIVAMENTE los campos dinámicos del dict (D-NC6 — NO crear tabla estática nueva):

```markdown
### Fuga {n} — {brecha['nombre']}
{brecha['detalle']}
```

3. **Fuente de la narrativa** (D-NC6): `nombre` y `detalle` ya vienen de `_pain_to_brecha()` — derivados de `pain.name`/`pain.description` del mapper con fallback a las narrativas internas del generador (16 pain_ids). Para referencia, los nombres dinámicos esperados de los 7 pains de Zione:

| pain_id | `brecha['nombre']` esperado (dinámico — NO hardcodear) |
|---------|--------------------------------------------------------|
| `no_hotel_schema` | derivado de `pain.name` (fallback interno: narrativa de datos invisibles) |
| `low_seo_score` | "SEO Local Bajo" (o `pain.name` real) — NO confundir con la narrativa de Google Maps (`low_gbp_score`) |
| `no_faq_schema` | derivado de `pain.name` |
| `no_analytics_configured` | derivado de `pain.name` |
| `low_organic_visibility` | derivado de `pain.name` |
| `ai_crawler_blocked` | "IA Bloqueada" o "IA sin guía" (rename condicional FASE-COPY-B, L3206-3222) |
| `no_og_tags` | derivado de `pain.name` |
| `whatsapp_conflict` | "Conflicto de WhatsApp" (`pain.name` real del mapper L373-380) |

4. Numeración secuencial (`Fuga 1`, `Fuga 2`, …) según el orden de `brechas_destacadas` (orden por SEVERIDAD — critical > high > medium > low, L3059-3061).
5. Si `brechas_destacadas` está vacía: retornar una sección de fallback razonable (texto neutro derivado de `_build_brechas_section` vacío o equivalente) — nunca string vacío que deje la sección sin cuerpo.
6. Pluralización del título (D-NC1 anexo): si `len(brechas_destacadas) == 1`, el título del template renderizaría "LAS 1 FUGAS PRINCIPALES" — considerar que `fugas_count_display` venga acompañado de un string de título completo (p. ej. `fugas_title = "LA FUGA PRINCIPAL" if N == 1 else f"LAS {N} FUGAS PRINCIPALES"`) o aceptar el formato numérico; decidir e implementar coherentemente con AC9 (Zione tiene N=7, no es bloqueante).
7. NO se necesitan `{landmark}`/`{region}` en el nuevo método: la narrativa dinámica de `_pain_to_brecha()` ya está completa (a diferencia de la tabla estática descartada).

### Tarea 3: Cambio en el template + inyección en render dict

**Archivos afectados**:
- `modules/commercial_documents/templates/diagnostico_v6_template.md` (Sección 4)
- `modules/commercial_documents/v4_diagnostic_generator.py` (dict de renderizado, zona `'brechas_section'`)

**Template (antes)**: L65-77 (título con "3" fijo + intro dinámica + 3 fugas hardcoded).
**Template (después)** — diseño minimal-diff D-NC2:

```markdown
## 4. 🔍 LAS ${fugas_count_display} FUGAS PRINCIPALES

De las ${brechas_total_count} brechas técnicas detectadas, estas ${brechas_destacadas_count} son las que más dinero le están costando HOY.
Las otras ${brechas_restantes_count} se resuelven en el plan completo de la Fase 2.

${fugas_principales_section}
```

**Inyección en el dict de renderizado** (junto a la zona de contadores L919-923):

```python
# FUGAS-WHATSAPP (B1+B4): Sección 4 dinámica — fugas derivadas del pain_ledger
# (fuente única de verdad, lista ya filtrada por VERIFIED_IN_SITE en _identify_brechas).
'fugas_principales_section': self._build_fugas_principales_section(audit_result, brechas_destacadas),
'fugas_count_display': str(len(brechas_destacadas)),
```

**Guardas**:
- El render usa `string.Template.safe_substitute()` (L1542-1546): una variable faltante NO rompe la generación pero deja `${var}` literal en el output (corrupción silenciosa). Tras el cambio, crear/ejecutar un smoke test que assertee **0 residuos `${`** en el documento renderizado (guard anti-residuos, lección L2).
- NO eliminar `${brechas_total_count}`, `${brechas_destacadas_count}`, `${brechas_restantes_count}` del dict (siguen en el template).
- NO alterar la detección de pains ni el pain_ledger (AC8).

### Tarea 4: Tests nuevos + no-regresión

**Archivos afectados**: `tests/commercial_documents/test_diagnostic_generator.py`

| Test | Setup | Asserts |
|------|-------|---------|
| `test_fugas_principales_sin_whatsapp_conflict` | Audit tipo Zione: `whatsapp_status=VERIFIED`, 7 pains reales (schema, seo, faq, analytics, visibility, crawlers, og) | La sección NO contiene "Contacto perdido por WhatsApp" ni "WhatsApp incorrecto" (AC1); contiene ≥1 fuga derivada de los pains reales |
| `test_fugas_principales_con_whatsapp_conflict` | Audit simulado con conflicto real (phone_web ≠ phone_gbp → pain `whatsapp_conflict` en ledger) | Una fuga con mención de WhatsApp derivada del pain real SÍ aparece (AC4). Assert correcto: contiene "WhatsApp" y el nombre dinámico "Conflicto de WhatsApp" (`pain.name` del mapper) — NO assertear el string estático "Contacto perdido por WhatsApp incorrecto", que con D-NC6 ya no existe |
| `test_fugas_count_matches_brechas` | Audit con N brechas destacadas | Título renderizado contiene "LAS {N} FUGAS" con N = len(brechas_destacadas) (AC9); coincide con `${brechas_destacadas_count}` de la intro |
| `test_fugas_derivan_de_pain_ids` | Audit con pains conocidos | Cada "### Fuga {n} —" del output corresponde a una brecha/pain real del ledger filtrado; ninguna fuga "inventada" (AC3) |

**Comando de validación**:
```bash
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_diagnostic_generator.py tests/commercial_documents/test_diagnostic_brechas.py tests/commercial_documents/test_template_conditionals.py tests/regression/ -v
```

- [ ] 4 tests nuevos pasan
- [ ] `test_diagnostic_brechas.py` (1,195 líneas) pasa — los contadores y la sección de brechas no se rompieron
- [ ] `test_template_conditionals.py` pasa — el contrato de variables del template sigue íntegro
- [ ] `tests/regression/` pasa (26 tests)
- [ ] grep `WhatsApp incorrecto` en `modules/` → 0 resultados (con D-NC6 la narrativa es dinámica y el string literal desaparece por completo de `modules/` — AC7)
- [ ] grep `Fuga 1 — Contacto perdido` en `modules/commercial_documents/templates/` → 0 resultados

### Tarea 5: Post-ejecución documental

Ver sección **Post-Ejecución** (obligatoria).

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| 4 tests nuevos (tabla de Tarea 4) | `tests/commercial_documents/test_diagnostic_generator.py` | 4/4 pasan |
| Suite brechas | `tests/commercial_documents/test_diagnostic_brechas.py` | 0 fallos |
| Suite template conditionals | `tests/commercial_documents/test_template_conditionals.py` | 0 fallos |
| Regresión | `tests/regression/` | 26/26 |

> NOTA: NO ejecutar la suite completa (3,360+). Los archivos patológicos ya están excluidos por conftest.

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`**: FASE-R0-B ✅ + notas (decisiones de implementación tomadas).
2. **`README.md` del plan**: tabla de progreso actualizada.
3. **`06-checklist-implementacion.md`**: fila FASE-R0-B ✅.
4. **`09-documentacion-post-proyecto.md`**:
   - Sección B: Sección 4 del diagnóstico ahora dinámica (pain_ledger → fugas narrativas).
   - Sección D: +4 tests (3,365).
   - Sección E: `diagnostico_v6_template.md`, `v4_diagnostic_generator.py`, `test_diagnostic_generator.py`.
5. **`10-analisis-post-implementacion.md`**:
   - Resumen de Ejecución: fila FASE-R0-B.
   - **Decisiones Arquitectónicas**: confirmar/registrar D-NC1, D-NC2, D-NC3 con desviaciones reales si las hubo.
   - Lecciones Aprendidas: mínimo 3.
   - Matriz de Verificación: filas B1 y B4.
6. **Evidencia**: no aplica (sin comandos largos).
7. **Registrar la fase**:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-R0-B \
    --desc "Fix B1+B4: Seccion 4 fugas dinamicas desde pain_ledger + contador en titulo" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/templates/diagnostico_v6_template.md" \
    --tests "4" \
    --check-manual-docs
```

> **SIN flag `--release`**. Si el DOCUMENTATION AUDIT marca [GAP] en GUIA_TECNICA.md por tocar archivos de cambio arquitectónico, anotarlo para FASE-RELEASE (la nota técnica v4.72.1 se crea allí; en fase intermedia NO editar GUIA_TECNICA).

8. **Validación final**:
```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```
> Si fallan "Version Sync"/"Document Integration": resolver con `sync_versions.py` y re-validar (NO re-ejecutar tests).

9. **Regenerar DOMAIN_PRIMER**:
```bash
./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer
```

---

## Criterios de Completitud (CHECKLIST)

⚠️ Verificar ANTES de marcar como ✅ COMPLETADA ⚠️

- [ ] 4 tests nuevos pasan (con/sin conflicto WhatsApp, contador, derivación de pain_ids)
- [ ] Suites obligatorias pasan (diagnostic_generator + brechas + template_conditionals + regression)
- [ ] El template ya no contiene fugas hardcoded (grep `Fuga 1 — Contacto perdido` en templates/ = 0)
- [ ] `fugas_count_display` coincide con las fugas listadas y con `${brechas_destacadas_count}` (D-NC1)
- [ ] El método consume la lista YA filtrada por VERIFIED_IN_SITE (verificado en código)
- [ ] `log_phase_completion.py` ejecutado (SIN `--release`)
- [ ] `dependencias-fases.md`, `README.md`, `06-checklist`, `09`, `10` actualizados
- [ ] `run_all_validations.py --quick` TOTAL PASS

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- Máximo 60 iteraciones (R2). Si se alcanza: marcar `⏳ INCOMPLETA` con checkpoint (qué método quedó a medias, qué tests faltan) y cerrar sesión.
- **NO ejecutar `v4complete`** (única ejecución reservada a FASE-R0-E).
- NO modificar `_build_quick_wins()` (ya corregido en R0-A), la Sección 1/6 del template (R0-C) ni el proposal generator (R0-D).
- NO alterar: pain_ledger, `_identify_brechas()` (filtrado), `_pain_to_brecha()` (narrativa), publication gates, coherence score, proposal_asset_matrix.
- NO bump de versión ni CHANGELOG (FASE-RELEASE-4.72.1).
- NO ejecutar la suite completa de tests.
- `log_phase_completion.py` SIN `--release`.
