# Plan Maestro — Refactorización de Coherencia Narrativa en Documentos Comerciales (FUGAS-WHATSAPP)

**ID del Plan**: REFACTOR-COHERENCIA-NARRATIVA-2026-08-22
**Fecha de concepción**: 2026-08-22
**Versión base**: v4.72.0 → **Versión objetivo**: v4.72.1 (patch — bugfix capa narrativa)
**Fuente de contexto**: `.opencode/context/CONTEXT-REFACTOR-COHERENCIA-NARRATIVA-FUGAS-WHATSAPP-2026-08-22.md` (hallazgos validados factualmente contra código vivo el 2026-08-22)
**Workflow rector**: `.agents/workflows/phased_project_executor.md` v2.15.0
**Reglas mandatorias**: R1 (1 fase por sesión) · R2 (máx. 60 iteraciones por fase) · R3 (scope de fase)

---

## 1. Problema

Anomalía detectada en el output E2E de Zione (v4.72.0): la Sección 4 del diagnóstico reporta **"Fuga 1 — Contacto perdido por WhatsApp incorrecto"** cuando los datos técnicos confirman WhatsApp **VERIFIED** y funcional (+573103724544). La capa de datos (pain_ledger, proposal_asset_matrix, v4_complete_report, delivery_quality_report) es 100% coherente; la **capa narrativa** está fosilizada en templates y métodos de generación.

**7 manifestaciones, 1 causa raíz** (fosilización narrativa en templates):

| Bug | Manifestación | Ubicación |
|-----|--------------|-----------|
| B1 | 3 fugas hardcoded (WhatsApp, Maps, IA) ignorando el pain_ledger | `templates/diagnostico_v6_template.md` L70-77 |
| B2 | Quick Win "Corregir WhatsApp en Google Maps" disparado por condición `not hotel_schema_detected` (copy-paste) | `v4_diagnostic_generator.py` L1883-1888 |
| B3 | Título Sección 1 "…POR WHATSAPP, GOOGLE MAPS E IA" + cláusula "o el número de WhatsApp no responde" sin condición | Template L29, L39 |
| B4 | Título "LAS 3 FUGAS PRINCIPALES" con número fijo (Zione: 7 brechas) | Template L65 |
| B5 | "Detecta las 3 fugas digitales" con número fijo | Template L89 |
| B6 | "(WhatsApp + datos para IA)" hardcoded en plan de 30 días | `v4_proposal_generator.py` L2195 |
| B7 | "Botón de WhatsApp" listado como servicio adicional cuando no es brecha | `v4_proposal_generator.py` L1455-1457 |

**Impacto comercial**: el cliente lee una contradicción directa entre la Sección 4 (WhatsApp = fuga #1) y la Sección 2 ("✅ WhatsApp verificado"), erosionando la credibilidad del documento completo.

## 2. Objetivo

Eliminar las 7 manifestaciones haciendo que la narrativa de los documentos comerciales **derive del pain_ledger** (fuente única de verdad), con verificación E2E final mediante **UNA única ejecución de `v4complete`** sobre Zi One Luxury (https://zione.co/) con datos de onboarding reales (`output/clientes/zi-one-luxury_onboarding.yaml`), y análisis post-implementación que certifique que los fixes fueron superados y capture lecciones aprendidas.

**Alcance IN**: `modules/commercial_documents/` (template + 2 generadores) + tests + docs oficiales.
**Alcance OUT**: publication gates, coherence score, pain_ledger (detección), proposal_asset_matrix, outputs históricos, ROADMAP.md.

## 3. Estructura de Fases

| Fase | Bugs | Contenido | Archivos principales | Modo de ejecución | Estimación |
|------|------|-----------|----------------------|-------------------|------------|
| FASE-R0-A | B2 | Fix Quick Win #1 (texto ↔ condición) | `v4_diagnostic_generator.py` | DIRECTO | 30-45 min |
| **FASE-R0-B** ⚠️ | **B1+B4** | **Sección 4 dinámica desde pain_ledger + contador en título** | template + generator | DIRECTO (decisión de diseño) | 60-90 min |
| FASE-R0-C | B3+B5 | Título Sección 1 condicional + contador dinámico Sección 6 | template + generator | DIRECTO | 45 min |
| FASE-R0-D | B6+B7 | Propuesta condicional (plan 30 días + servicios adicionales) | `v4_proposal_generator.py` | DIRECTO | 45-60 min |
| FASE-R0-E | E2E | **Única ejecución v4complete Zione** + preservación baseline + evidencia + smoke | `output/`, `evidence/` | **DELEGATE_TASK** (subagente comando) | 30 min + corrida 5-10 min |
| FASE-R0-F | Verificación | AC1-AC12 + matriz de verificación + lecciones aprendidas | `10-analisis-post-implementacion.md` | DIRECTO (+ delegate opcional track greps) | 45 min |
| FASE-RELEASE-4.72.1 | Docs | Version bump + CHANGELOG + GUIA_TECNICA + validaciones E1-E8b | `VERSION.yaml`, docs oficiales | **DELEGABLE** (subagente) | 45 min |

**Nota sobre el plan sugerido en el CONTEXT (§7)**: R0-A y R0-B se mantienen. **B4 se mueve a R0-B** (misma zona del template L65 que B1 reemplaza; hacerlo separado dejaría el título incoherente una fase entera). **B5 se mueve a R0-C** (contador + variables de render, mismo perfil que B3). R0-D queda con B6+B7. Se **agrega FASE-R0-F** (verificación profunda AC1-AC12 + análisis post-implementación — requisito del usuario). R0-F del contexto (documentación) se convierte en **FASE-RELEASE-4.72.1** conforme al executor (§Convenciones-de-Nomenclatura: la fase que cambia la versión usa `FASE-RELEASE-X.Y.Z`).

## 4. Fase de Mayor Complejidad Técnica: FASE-R0-B

**FASE-R0-B es la fase de mayor complejidad técnica del plan.** Justificación:

1. **Única fase que crea lógica de generación nueva** (las demás son reemplazos de texto condicionales): nuevo método `_build_fugas_principales_section()` que REUTILIZA la narrativa dinámica ya producida por `_pain_to_brecha()` (dicts con `pain_id`/`nombre`/`detalle`/`impacto` — D-NC6), con selección de brechas destacadas por `impacto > 0` y numeración dinámica (el orden de la lista es por SEVERIDAD, `v4_diagnostic_generator.py` L3059-3061, no por impacto).
2. **Integra tres capas simultáneamente**: template (L65-77), generador (nuevo método) y dict de renderizado (zona L838-992, anclar por `'brechas_section'`). El render usa `string.Template.safe_substitute()` (L1542-1546): una variable omitida NO rompe la generación — deja el literal `${var}` visible en el output (corrupción silenciosa). El guard correcto es un smoke test con 0 residuos `${` en el documento renderizado.
3. **Debe respetar el filtrado VERIFIED_IN_SITE** (FASE-P1-D / D8): consumir la lista de pains YA filtrada dentro de `_identify_brechas()` (L3043-3044, vía `_get_brecha_pesos()`). Consumir la lista sin filtrar reintroduciría fugas verificadas en sitio vivo.
4. **Soporta la mayoría de los criterios de aceptación**: AC1, AC3, AC4, AC7, AC9 (+AC5/AC6 por no-regresión).
5. **Decisiones de diseño no triviales** (ver §Decisiones del prompt R0-B):
   - D-NC1: `fugas_count_display = len(brechas_destacadas)` — NO `min(3, len(brechas_pesos))` como sugería el CONTEXT §4.5: para Zione destacadas=7 y `min(3,…)` recrearía exactamente la incoherencia título-vs-contadores que este plan corrige.
   - D-NC2: diseño minimal-diff — mantener en el template las líneas de intro con contadores dinámicos (L67-68, ya correctas) y reemplazar solo los bloques de fugas (L70-77).
   - D-NC3: fallback narrativo directo vía `brecha['nombre']`/`brecha['detalle']` del dict ya calculado — NO vía `_get_brecha_nombre(audit_result, idx)`, que re-calcula la lista COMPLETA sin filtrar y desalinearían los índices (nunca crash, nunca invención).
   - D-NC6: NO crear una nueva tabla estática pain_id → narrativa: `_pain_to_brecha()` (L3094-3230) YA produce `nombre`/`detalle` dinámicos (`pain.name or narrative['nombre']`) para los 16 pain_ids conocidos. Una tabla nueva duplicaría narrativas estáticas (re-fosilización, viola L27) y contenía un error semántico en la propuesta original (`low_seo_score` → narrativa de Google Maps que corresponde a `low_gbp_score`).
6. **Riesgo de regresión concentrado**: toca el archivo más grande del módulo (`v4_diagnostic_generator.py`, 3,544 líneas) y el template oficial de v4.72.0.

Las fases A, C y D son correcciones condicionales acotadas; E y F son ejecución/verificación sin cambios de código. El presupuesto de complejidad de las 7 fases (escala `Baja → Baja-Media → Media → Media-Alta → Alta → MÁXIMA`, misma del plan CREDIBILIDAD-NUMERICA §3) está en §5.

## 5. Cumplimiento R3 (Scope de Fase) y Presupuesto de Complejidad — Análisis por Fase

| Fase | Tareas | Comandos largos | Complejidad | ¿Cumple R3? |
|------|--------|-----------------|-------------|-------------|
| R0-A | 4 (fix, test, no-regresión+greps, docs) | 0 | Baja (un solo sitio, condición copy-paste acotada) | ✅ (máx. 4 + 0) |
| **R0-B** | 4 (método+inyección, template, tests, docs) | 0 | **MÁXIMA** (ver §4: única lógica de generación nueva, 3 capas, filtro VERIFIED_IN_SITE) | ✅ |
| R0-C | 4 (título condicional, contador S6, tests, docs) | 0 | Baja-Media (3 puntos de template + variables de render; reusa contadores, sin lógica nueva) | ✅ |
| R0-D | 4 (fix B6, fix B7, tests, docs) | 0 | Baja-Media (2 sitios con condicional simple en archivo independiente) | ✅ |
| R0-E | 3 (baseline+v4complete, evidencia+smoke, docs) | 1 (v4complete) | Media (ejecución: corrida irrepetible, preservación disciplinada de baseline) | ✅ (máx. 3 + 1) |
| R0-F | 4 (ACs narrativos, greps+comparativa, matriz+lecciones, docs) | 0 | Media (juicio analítico sobre diff antes/después, sin cambios de código) | ✅ |
| RELEASE | 4 (bump+sync, CHANGELOG+GUIA, validaciones E1-E8b, log) | 0 | Baja (mecánica documental con scripts) | ✅ |

## 6. Mapa de Delegación (delegate_task)

| Fase | ¿Delegable? | Justificación (regla del executor) |
|------|-------------|-------------------------------------|
| R0-A | ❌ NO | Código+tests puro → ejecución directa más eficiente (§Regla-de-Decisión-código+tests) |
| R0-B | ❌ NO | Decisión de diseño cross-layer (mapeo + integración VERIFIED_IN_SITE) → directa (lección DT-3) |
| R0-C | ❌ NO | Código+tests con venv Windows → directa (regla venv WSL prevalece) |
| R0-D | ❌ NO | Ídem R0-C |
| R0-E | ✅ SÍ | v4complete vía subagente: `delegate_task(timeout=900, notify_on_complete=True, toolsets=["terminal"])` (§Protocolo-de-Subagente-para-v4complete). El parent preserva baseline/evidencia, verifica y documenta |
| R0-F | 🟡 PARCIAL | Track de greps residuales (AC7/AC12/AC8) delegable como trabajo paralelo independiente sin imports del proyecto. Matriz de verificación y lecciones: directo (requiere juicio y contexto completo del plan) |
| RELEASE | ✅ SÍ | Solo edita YAML/MD + ejecuta scripts stdlib → delegable (TIP §Paso-7; confirmado en BUGS-ONBOARDING-ADR: 18 tool calls, ~4 min). El parent verifica resultados |

## 7. Criterios de Aceptación (AC1-AC12) — Mapeo a Fases

| AC | Criterio | Implementa | Verifica |
|----|----------|-----------|----------|
| AC1 | Diagnóstico NO menciona "Fuga 1 — Contacto perdido por WhatsApp incorrecto" con `whatsapp_status=VERIFIED` | R0-B | R0-F |
| AC2 | Quick Win #1 menciona Schema/datos en Google (no WhatsApp) cuando `not hotel_schema_detected` | R0-A | R0-F |
| AC3 | Fugas de Sección 4 corresponden 1:1 con pain_ids del pain_ledger (sin inventos) | R0-B | R0-F |
| AC4 | Conflicto real de WhatsApp (phone_web ≠ phone_gbp) → la fuga de WhatsApp SÍ aparece | R0-B | R0-F |
| AC5 | 0 regresiones en gates de publicación (13/13) | todas | R0-E |
| AC6 | Coherence score ≥ 0.8 | — | R0-E |
| AC7 | grep "WhatsApp incorrecto" en `modules/` = 0 resultados (con el diseño D-NC6 el string literal ya no existe en `modules/`) | R0-B | R0-F |
| AC8 | Pain_ledger no alterado (mismos 7 pain_ids para Zione, sin WhatsApp) | — | R0-E/R0-F |
| AC9 | Título Sección 4 muestra número dinámico coincidente con fugas listadas | R0-B | R0-F |
| AC10 | Sección 6 muestra "Detecta las N fugas" con N = brechas reales | R0-C | R0-F |
| AC11 | Plan 30 días NO menciona WhatsApp cuando `whatsapp_conflict=False` | R0-D | R0-F |
| AC12 | grep "Corregir el número de WhatsApp" en `modules/` = 0 resultados | R0-A | R0-F |

## 8. Restricciones y Guardas (heredadas del CONTEXT §6)

- **Cambio puramente narrativo**: NO alterar publication gates (deben seguir 13/13 en el mismo estado que el baseline: 12 PASSED + 1 WARNING pricing_compliance), coherence score (≥ 0.8), detección de pains ni proposal_asset_matrix.
- **Compatibilidad backwards**: el template `diagnostico_v6_template.md` es la plantilla oficial desde v4.72.0. Las variables `${brechas_total_count}`, `${brechas_destacadas_count}`, `${brechas_restantes_count}` se conservan (las dos últimas siguen usadas en la intro de la Sección 4).
- **Outputs históricos** en `output/` y `evidence/` NO se modifican (registro de lo que el sistema produjo).
- **Filtro VERIFIED_IN_SITE**: el nuevo método consume la lista YA filtrada dentro de `_identify_brechas()` (L3043-3044, vía `_get_brecha_pesos()`).
- **Fuente única**: las fugas narrativas derivan del pain_ledger, nunca de lógica independiente.
- **`log_phase_completion.py` SIN `--release`** en fases intermedias (check "Prompts No Release" de `run_all_validations.py`).
- **Suites pytest**: ejecutar archivos específicos (no la suite completa de 3,360 tests) — ver conftest de `tests/commercial_documents/` (archivos patológicos excluidos L1/L11).

## 9. Ejecución Única de v4complete (FASE-R0-E)

- **URL**: https://zione.co/ (Zi One Luxury, Pereira, Eje Cafetero)
- **Onboarding real**: `output/clientes/zi-one-luxury_onboarding.yaml` — auto-cargado por v4complete desde `output/clientes/` (mecanismo FASE-D S7, `main.py` L1759-1781, con fallback a la ruta default). 4 campos confirmados Tier A (habitaciones=34, reservas_mes=800, valor_reserva_cop=290000, canal_directo_pct=40.0). NO requiere flags adicionales.
- **ÚNICA ejecución del plan**. Si falla: NO re-ejecutar; aplicar el Protocolo de Recuperación de Agotamiento del executor y documentar.
- **Baseline anómalo** (output 20260821_175706) preservado ANTES de la corrida en `evidence/FASE-R0-E/baseline/` para el diff antes/después en R0-F.
- Datos de referencia del baseline: coherence 0.9485, 7 pain_ids (schema, seo, faq, analytics, visibility, crawlers, og), whatsapp VERIFIED.

## 10. Entregables del Plan

1. 7 bugs narrativos corregidos (capa de datos intacta).
2. ~12 tests nuevos (4 en R0-B, 3 en R0-C, 4 en R0-D, 1 en R0-A) con 0 regresiones.
3. Evidencia E2E en `evidence/FASE-R0-E/` (baseline + output post-fix).
4. Matriz de verificación AC1-AC12 completa + lecciones aprendidas en `10-analisis-post-implementacion.md`.
5. Release v4.72.1 documentada (CHANGELOG + GUIA_TECNICA + VERSION.yaml + sync 6 archivos).

## 11. Cómo Retomar una Sesión

1. Leer `README.md` de este plan (tabla de progreso).
2. Leer `06-checklist-implementacion.md` (estado de cada fase).
3. Leer `dependencias-fases.md` (conflictos y checkpoint).
4. Ejecutar el prompt `05-prompt-inicio-sesion-fase-{X}.md` de la siguiente fase pendiente en UNA sesión nueva de agente.
