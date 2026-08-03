# FASE-A: Contenido Veraz — D1 (brecha OG falsa) + D2 (detección única de brechas)

**ID**: COHERENCIA-FASE-A
**Objetivo**: Que el diagnóstico diga la verdad sobre Open Graph (D1) y que doc, ledger y pesos usen UNA sola detección de brechas (D2).
**Dependencias**: Ninguna (primera fase).
**Duración estimada**: 1 sesión (~45 iteraciones de 60).
**Skill**: `phased_project_executor` v2.13.0 · skills de apoyo: `iah-cli-code-modification`, `iah-cli-execution-conventions`.

## Contexto

El diagnóstico 2026-08-01 vendió "Sin Meta Tags Sociales (Open Graph)" con costo $958.694/mes cuando el propio audit detectó 8 tags OG completos (D1), y mostró 3 conteos de brechas distintos: 9 en pain_ledger, 4 con costo en el doc, "7" hardcodeado en el template (D2). Causa raíz: `_pain_to_brecha` ignora `pain.name` del mapper (que YA distingue "Sin" vs "Incompletos") y `_identify_brechas` construye un `ValidationSummary` sintético con caché, divergiendo del orquestador.

Fuente completa: `.opencode/context/CONTEXT-DIAGNOSTICO-COHERENCIA-MODULO-ENTREGA-2026-08-02.md` §5 FASE-1.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A | ▶️ EN CURSO (esta sesión) |

### Base Técnica Disponible
- Tests base: 3,185 funciones / 253 archivos (0 regresión).
- Baseline auditado (NO re-ejecutar v4complete): `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260801_170539.md`, `output/v4_complete/zione/v4_audit/pain_ledger.json`.

## Modo de ejecución (delegate_task)

**DIRECTO con el agente principal.** Fix puro de código+tests sin decisión arquitectónica cross-module ni comandos largos → regla §Regla-código+tests del executor. NO spawn de subagentes.

## Tareas

### T1 — Fix D1: `_pain_to_brecha` usa pain.name/description (P0)
**Objetivo**: La brecha refleja el estado real detectado por el mapper.

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` (L2886-3006, `_pain_to_brecha`)

**Cambio**:
```python
# ANTES: narrative = narratives[pain.id]; nombre/detalle SIEMPRE de narrativa estática
# DESPUÉS: preferir pain.name / pain.description del mapper
nombre = pain.name or narrative['nombre']
detalle = pain.description or narrative['detalle']
```
- MANTENER el special-case de `ai_crawler_blocked` (L2983-2998).
- Mapear TODOS los `pain.name` del mapper vs narrativas del generator antes de cambiar; conservar fallback a narrativa cuando `pain.name` esté vacío.
- Verificar que `_og_tags_incomplete` (pain_solution_mapper.py:633-644, umbral <10) ya distingue missing vs incomplete.

**Criterios de aceptación**:
- [ ] Con 8 tags OG detectados, la brecha resultante es "Open Graph Tags Incompletos — Se detectaron 8 OG tags pero faltan tags importantes" (o equivalente del mapper), NUNCA "Sin Meta Tags".
- [ ] Breakdown AEO (`open_graph(15%)`) y la brecha ya no se contradicen.

### T2 — Fix D2: detección única de brechas (P0)
**Objetivo**: Doc, pain_ledger y pesos convergen al mismo N (9 para Zione).

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` (`_identify_brechas` L2823-2864, caché L2839-2840, `_get_brecha_pesos` L3069, `_compute_opportunity_scores` L3173)
- `main.py` (L2638, L3290 — puntos de invocación)
- `modules/commercial_documents/templates/diagnostico_v6_template.md` (L66-67)

**Cambios**:
1. Nueva firma: `_identify_brechas(self, audit_result, validation_summary=None, analytics_data=None, whatsapp_html_detected=None)`.
2. Usar parámetros reales; SOLO construir VS sintético si `validation_summary is None` (fallback).
3. **CRÍTICO — manejar el caché `_cached_brechas` (L2839-2840)**: hoy el orden real es `generate()` (main.py:2542) → `_get_brecha_pesos` (L3069) → `_identify_brechas(audit_result)` puebla el caché con el VS sintético ANTES de que main.py:2638 pueda pasar inputs reales. Si el caché no se invalida, main.py:2638 devolverá la detección sintética congelada y D2 NO se resuelve. Solución: (a) guardar en `generate()` los inputs reales como atributos (`self._current_validation_summary = validation_summary`, `self._current_analytics_data = analytics_data`, `self._current_whatsapp_html_detected = whatsapp_html_detected`) y que `_identify_brechas` los use cuando la firma no los reciba; Y (b) keyear el caché por inputs (hash de los 3 valores) o eliminarlo. Verificar con test de orden: generate() primero, luego `_identify_brechas` con inputs reales → mismo N que `detect_pains` del orquestador.
4. **CRÍTICO — narrativas faltantes en `_pain_to_brecha`**: el mapper detecta 9 pains para Zione, pero el dict `narratives` de `_pain_to_brecha` (L2903-2974) NO incluye `low_seo_score` ni `low_organic_visibility` → L2976-2977 (`if pain.id not in narratives: return None`) los descarta silenciosamente. Con inputs reales el doc daría 7 brechas, NO 9 → D2 seguiría abierto. Añadir esas 2 narrativas (nombre/detalle/impacto) al dict del generator Y sus pesos a `config/regional_benchmarks.yaml::pain_narratives` (hoy ausentes — verificado 2026-08-03). Sin esto, `pain_ledger.json == doc` es imposible.
5. Actualizar los 4 consumidores con inputs reales: main.py:2638 (brechas_reales), main.py:3290 (channel_context — NO eliminar: alimenta `_compute_opportunity_scores`), generator:3069 (`_get_brecha_pesos`), generator:3173 (`_compute_opportunity_scores`). Los 2 internos heredan los inputs reales vía atributos de generate() (punto 3a).
6. El ledger del orquestador se construye DESDE la misma lista (`brechas_reales` ya existe en main.py:2638) — eliminar la segunda invocación divergente.
7. Template L66-67: reemplazar "De las 7 brechas técnicas detectadas" → `${brechas_total_count}`, "estas 3 son las que más dinero" → `${brechas_destacadas_count} son las que más dinero` (número real de brechas con costo que muestra la sección) y "Las otras 4" → `${brechas_restantes_count}`. Verificar qué variable puebla `_build_brechas_section` (L2445: itera TODAS las brechas dinámicamente) y derivar los 3 contadores de la MISMA lista.

**⚠️ Matemática corregida (2026-08-03, verificado contra YAML)**: la suma de pesos de los 9 pains del ledger NO es 1.20 (contexto §3.1) — los 7 pains con peso en `pain_narratives` (eje_cafetero) suman **1.10** (0.20+0.20+0.25+0.12+0.10+0.15+0.08), y `low_seo_score`/`low_organic_visibility` NO tienen peso en el YAML. La suma TOTAL del YAML es 2.08 (incluye pains no detectados: low_gbp_score 0.30, poor_performance 0.15, etc.). Tras añadir los 2 pesos faltantes (punto 4), la normalización real sobre 9 pains dependerá de los pesos asignados — NO asumir 20.8%. El test debe calcular la expectativa desde los pesos reales del YAML, no desde 0.25/1.2.

**Criterios de aceptación**:
- [ ] `pain_ledger.json` y las brechas del doc tienen el mismo N para un mismo input (9 para Zione — requiere las narrativas añadidas en T2 punto 4; sin ellas el doc daría 7).
- [ ] `_get_brecha_pesos` normaliza sobre N real; expectativa calculada desde pesos reales del YAML (NO 0.25/1.2 — suma real de los 9 con pesos añadidos).
- [ ] **Caché no congela la detección sintética**: test que llama `generate()` primero (puebla caché) y luego `_identify_brechas` con inputs reales → resultado igual a `detect_pains` del orquestador (mismo N). Assert EXACTO (==), sin tolerancia (lección DELIVERY-ZIP: la tolerancia 5% enmascaró el bug del tamaño).
- [ ] `low_seo_score` y `low_organic_visibility` aparecen como brechas con costo cuando se detectan (narrativas + peso en YAML añadidos).
- [ ] Ningún conteo de brechas hardcodeado en el template.
- [ ] Documentar en el commit que los costos de brecha CAMBIAN para todos los hoteles (pesos sobre N real) — es el comportamiento correcto.

### T3 — Tests nuevos (TDD donde sea viable)
**Archivos**: `tests/commercial_documents/test_diagnostic_brechas.py` (EXISTE, 816 líneas — extenderlo; verificado 2026-08-03: ya cubre `_identify_brechas` con tests de N dinámico, sin defaults, hotel perfecto, orden por impacto) + extensiones si hacen falta.

- [ ] Test: audit con 8 OG tags → brecha con nombre "Incompletos", no "Sin".
- [ ] Test: misma input en generator y orquestador → mismo conjunto de brechas (mismo N).
- [ ] Test: `_normalize_weights` sobre lista de 9 suma 1.0; expectativa calculada desde pesos reales del YAML (NO 0.25/1.2).
- [ ] Test: template renderizado contiene conteo dinámico, nunca "7 brechas".
- [ ] Test: `low_seo_score` y `low_organic_visibility` producen brechas con costo cuando se detectan (narrativas añadidas).
- [ ] Test: caché no congela detección sintética (generate() primero, luego inputs reales → mismo N que orquestador).

## Tests Obligatorios

| Test | Comando | Criterio |
|------|---------|----------|
| Suite afectada | `./venv/Scripts/python.exe -m pytest tests/ -k "pain_solution_mapper or diagnostic_generator" -x -q` | 0 fallos |
| Módulos core | `./venv/Scripts/python.exe -m pytest tests/commercial_documents tests/data_validation -q` | 0 regresiones |
| Validaciones | `./venv/Scripts/python.exe scripts/run_all_validations.py --quick` | 4/4 |

**Verificación estática**:
```bash
grep -rn "7 brechas técnicas" modules/   # → 0 hits
grep -rn "De las 7 brechas" modules/     # → 0 hits
```

## Post-Ejecución (OBLIGATORIO)

⚠️ NO OMITIR ⚠️

1. Marcar FASE-A ✅ en `dependencias-fases.md`, `09-checklist-implementacion.md` y `README.md` del plan.
2. Actualizar `11-documentacion-post-proyecto.md` (secciones B, D, E).
3. Ejecutar:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-A \
    --desc "D1 brecha OG veraz + D2 detección única de brechas" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py,main.py,modules/commercial_documents/templates/diagnostico_v6_template.md" \
    --tests "<N nuevos>" --check-manual-docs --release 4.70.0
```
4. NO editar CHANGELOG/GUIA_TECNICA todavía (se acumulan para RELEASE).

## Criterios de Completitud (CHECKLIST)

- [ ] D1 y D2 cerrados según criterios de T1/T2
- [ ] Tests nuevos pasan + 0 regresiones en suites afectadas
- [ ] `run_all_validations.py --quick` 4/4
- [ ] `dependencias-fases.md` actualizado
- [ ] `log_phase_completion.py` ejecutado

## Restricciones

- Máximo 60 iteraciones (R2).
- NO ejecutar v4complete (la única ejecución del plan es FASE-E).
- NO tocar costos de brecha ni escenarios financieros (eso es FASE-B).
- NO tocar `publication_gates.py` (FASE-C-A) ni textos de performance/reviews (FASE-C-B).
- NO modificar `pain_solution_mapper.py` salvo bug bloqueante: ya produce los nombres correctos (contexto §4.1: "mantener esa info").
- Regla executor: si la sesión alcanza 60 iteraciones → marcar ⏳ INCOMPLETA con checkpoint y cerrar.
