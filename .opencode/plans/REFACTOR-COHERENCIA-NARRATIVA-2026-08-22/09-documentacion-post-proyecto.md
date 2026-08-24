# Documentación Post-Proyecto — REFACTOR-COHERENCIA-NARRATIVA-2026-08-22

> **Propósito**: acumular datos por fase para que FASE-RELEASE-4.72.1 genere CHANGELOG y GUIA_TECNICA oficiales sin reproceso.
> **Regla**: cada fase completa su columna "Fase" al cerrar sesión (Post-Ejecución paso 4). FASE-RELEASE SOLO consume este archivo, no registra fases.
> **Pre-poblado**: las filas siguientes reflejan lo PLANIFICADO (01-plan-maestro.md). Cada fase confirma/corrige sus filas al cerrar.

## Sección A: Módulos Nuevos

| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|
| (ninguno — plan de refactor sobre módulos existentes) | — | El alcance es `modules/commercial_documents/` (template + 2 generadores); no crea módulos nuevos | — |

## Sección B: Funcionalidades Nuevas/Afinadas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| Quick Win #1 condicional (B2) | commercial_documents | Quick Win disparado por `not hotel_schema_detected` ahora menciona “Verificar qué datos de su hotel faltan en Google (ficha y resultados de búsqueda)” en lugar de “Corregir el número de WhatsApp en Google Maps” (copy-paste corregido); patrón narrativo DIY mantenido | FASE-R0-A |
| Sección 4 de fugas dinámica (B1) | commercial_documents | `_build_fugas_principales_section()`: reutiliza narrativa dinámica de `_pain_to_brecha()` (`brecha['nombre']`/`['detalle']` — D-NC6, sin tabla estática nueva), selección de brechas destacadas por `impacto > 0` (orden por severidad), numeración dinámica; consume la lista YA filtrada dentro de `_identify_brechas()` (VERIFIED_IN_SITE, L3043-3044) | FASE-R0-B |
| Título Sección 4 dinámico (B4) | commercial_documents | "LAS {N} FUGAS PRINCIPALES" con N = `len(brechas_destacadas)` (D-NC1: NO `min(3, …)`) vía `${fugas_title}` con pluralización completa (N=0 → "SIN FUGAS PRINCIPALES", N=1 → "LA FUGA PRINCIPAL"); `${fugas_count_display}` también inyectado en el dict | FASE-R0-B |
| Título Sección 1 condicional (B3) | commercial_documents | "…POR {canales}" vía variable dinámica derivada del mismo signal que `_build_whatsapp_conflict_note()` (D-NC4 — Opción B del CONTEXT §4.3) | FASE-R0-C |
| Contador Sección 6 dinámico (B5) | commercial_documents | "Detecta las {N} fugas digitales" reutilizando la variable EXISTENTE `${brechas_total_count}` — cero código nuevo en generador (D-NC5) | FASE-R0-C |
| Plan 30 días condicional (B6) | commercial_documents | "Implementación Fase 1 (datos para IA)" sin "WhatsApp + " cuando `whatsapp_conflict=False`; parámetro cableado desde la extracción existente (L792-798) a `_build_30_day_plan()` | FASE-R0-D |
| Botón WhatsApp fuera de adicionales sin brecha (B7) | commercial_documents | Botón de WhatsApp en "Servicios adicionales" SOLO si hay brecha/conflicto real (signal dinámico `breach_by_asset` + `whatsapp_conflict`); sin señal de presencia NO se afirma "ya presente" | FASE-R0-D |
| E2E certificación narrativa | — | Única corrida `v4complete` Zi One Luxury post-fix con preservación de baseline anómalo y evidencia proactiva (`evidence/FASE-R0-E/`) | FASE-R0-E |
| Matriz de verificación AC1-AC12 | — | Certificación formal 12/12 + diff narrativo antes/después + lecciones aprendidas | FASE-R0-F |

## Sección C: Notas de Ejecución por Fase

> Cada fase agrega sus notas al cerrar (comandos, duración, incidencias, resultado de delegate_task).

### FASE-R0-A
- Fecha: 2026-08-22. Modo: DIRECTO. Iteraciones: ~15.
- Fix: reemplazo de texto en `_build_quick_wins()` (L1885-1886) — texto anterior mencionaba WhatsApp cuando la condición real es `not hotel_schema_detected`.
- Texto nuevo: “Verificar qué datos de su hotel faltan en Google (ficha y resultados de búsqueda).” → nota DIY.
- Test nuevo: `test_quick_wins_schema_text_sin_schema` + `test_quick_wins_schema_no_aparece_con_schema_detectado` (clase `TestB2QuickWinSchemaText`).
- Suites: 59/59 pasan (23 diagnostic_generator + 10 top_problems_consistency + 26 regression).
- Grep “Corregir el número de WhatsApp” en `modules/`: 0 resultados (AC12 ✅).
- Sin incidencias.

### FASE-R0-B
- Fecha: 2026-08-24. Modo: DIRECTO (NO delegable, DT-3). Iteraciones: ~14.
- Fix B1: bloques hardcoded de fugas (L70-77) → `${fugas_principales_section}` generada por nuevo método `_build_fugas_principales_section()` (insertado tras `_build_brechas_resumen_section()`), narrativa EXCLUSIVA de `brecha['nombre']`/`brecha['detalle']` (D-NC3/D-NC6 — sin tabla estática nueva).
- Fix B4: título "LAS 3 FUGAS PRINCIPALES" → `${fugas_title}` pluralizado (extensión menor de D-NC1, decidida en implementación: N=0/1/N).
- Inyección en render dict junto a contadores (zona `brechas_restantes_count`): `fugas_principales_section`, `fugas_count_display`, `fugas_title`.
- La lista consumida (`brechas_destacadas`) es la misma que alimenta los contadores del template: filtrada por VERIFIED_IN_SITE en `_identify_brechas()` y ordenada por severidad — título, intro y fugas siempre coherentes.
- 4 tests nuevos (clase `TestFugasPrincipalesDinamicas` + fixtures `_make_zione_like_audit`/`_make_validation_with_whatsapp`): sin-conflicto (AC1 + guard anti-residuos `${` = 0), con-conflicto (AC4), contador título↔fugas↔intro (AC9/D-NC1), derivación 1:1 fugas↔brechas (AC3).
- Suites: 27 diagnostic_generator + 42 diagnostic_brechas + 6 template_conditionals + 26 regression — 101/101 pasan.
- Greps: "WhatsApp incorrecto" en `modules/` = 0 (AC7); "Fuga 1 — Contacto perdido" en templates/ = 0; "FUGAS PRINCIPALES" en `modules/` solo en código dinámico.
- Sin incidencias.

### FASE-R0-C
- Fecha: 2026-08-24. Modo: DIRECTO (NO delegable, regla venv WSL). Iteraciones: ~12.
- Fix B3: título S1 (L29) “HOY HAY RESERVAS ESCAPÁNDOSE POR WHATSAPP, GOOGLE MAPS E IA” → `${seccion_1_canales}` condicional a `_has_whatsapp_conflict()` (helper nuevo compartido). Cláusula L39 “o el número de WhatsApp no responde” → `${seccion_1_whatsapp_clausula}` condicional al mismo signal.
- Fix B5: “Detecta las 3 fugas digitales” (L82) → `${brechas_total_count} fugas digitales` (reutiliza variable existente — D-NC5).
- Helper `_has_whatsapp_conflict()` extraído de `_build_whatsapp_conflict_note()` (mismo signal: `validation.conflicts` con `field_name == 'whatsapp'` + ambos teléfonos presentes). `_build_whatsapp_conflict_note()` refactorizado para usar el helper (sin duplicación de lógica).
- Inyección en render dict: `seccion_1_canales` + `seccion_1_whatsapp_clausula` junto a `whatsapp_conflict_business_note`.
- 3 tests nuevos (clases `TestSeccion1Conditional`, `TestSeccion6Contador`, `TestTemplateNoHardcodedFugas`): título condicional con/sin conflicto, contador dinámico S6, test estático anti-fosilización.
- Suites: 9 template_conditionals + 27 diagnostic_generator + 26 regression = 62/62 pasan.
- Sin incidencias.

### FASE-R0-D
- Fecha: 2026-08-24. Modo: DIRECTO (NO delegable, regla venv WSL). Iteraciones: ~15.
- Fix B6: parámetro `whatsapp_conflict: bool = False` agregado a `_build_30_day_plan()`; caller actualizado (L1010) para pasar el valor ya extraído en L792-798. Mención "WhatsApp + " condicional: `whatsapp_mention = "WhatsApp + " if whatsapp_conflict else ""`. El string literal "WhatsApp + datos para IA" ya no existe en el código — se construye por interpolación.
- Fix B7: `whatsapp_service_name` derivado dinámicamente de `PROPOSAL_SERVICE_TO_ASSET` (NO hardcoded); filtro `whatsapp_sin_brecha` basado en `whatsapp_conflict` + `breach_by_asset.get("whatsapp_button")`; cuando ambos son negativos, el botón se excluye de "Servicios adicionales disponibles" (sin claim de presencia).
- 4 tests nuevos (clases `TestFaseR0DPlan30DaysConditional`, `TestFaseR0DServiciosAdicionalesWhatsApp`): plan sin WhatsApp (AC11), plan con WhatsApp, servicios sin brecha (B7), servicios con brecha.
- Suites: proposal_dynamic + breach_consistency + 26 regression pasan. 13 tests pre-existentes fallan (verificados con `git stash` — fallos del baseline v4.72.0, no regresiones de R0-D).
- Grep "WhatsApp + datos para IA" en `modules/`: 0 resultados (confirmado — el string ya no existe como literal).
- Sin incidencias.

### FASE-R0-E
- Fecha: 2026-08-24. Modo: TERMINAL (background, delegate_task no disponible). Duración: ~5 min.
- Pre-checks: A+B+C+D ✅. Onboarding YAML con 4 campos confirmados. Git status capturado.
- Baseline anómalo preservado en `evidence/FASE-R0-E/baseline/` (5 archivos: diagnóstico, propuesta, v4_complete_report, pain_ledger, pain_ledger_resolved de corrida 20260821_175706).
- v4complete ejecutado UNA vez: `./venv/Scripts/python.exe main.py v4complete --url https://zione.co/`. Comando completó exitosamente.
- **Coherence**: 0.9485 (idéntico al baseline 0.9485). ≥ 0.8 ✅.
- **Pain_ledger**: 7 pain_ids correctos (no_hotel_schema, low_seo_score, no_faq_schema, no_analytics_configured, low_organic_visibility, ai_crawler_blocked, no_og_tags). SIN WhatsApp ✅.
- **WhatsApp**: VERIFIED ✅.
- **Gates**: 11 PASSED + 1 WARNING (pricing_compliance) + 1 BLOCKED (tier_c_onboarding_required). Baseline: 12 PASSED + 1 WARNING.
- **DESVÍO CRÍTICO**: gate `tier_c_onboarding_required` reporta BLOCKED con tier "C". Causa raíz: `assessment.get("financial_evidence_tier", "C")` en `publication_gates.py` L1137 retorna default "C" porque `financial_evidence_tier` NO se inyectó en el assessment dict. Baseline tenía tier "B+". **No relacionado con fixes narrativos B1-B7** — es una regresión del mecanismo de inyección de assessment dict (probablemente de FASE-P2-A “assessment dict injection”).
- **Efecto colateral**: gate BLOCKED → eliminación automática de `01_DIAGNOSTICO_Y_OPORTUNIDAD_20260824_111302.md` y `02_PROPUESTA_COMERCIAL_20260824_111302.md`. Archivos narrativos NO disponibles para análisis textual.
- Evidencia parcial preservada en `evidence/FASE-R0-E/`: v4_complete_report, gate_report, pain_ledger, pain_ledger_resolved, delivery ZIP, BLOCKED_BY_GATES.md.
- **FASE-R0-E NO COMPLETADA** — se requiere sesión de recuperación: (1) fix `financial_evidence_tier` injection, (2) re-ejecución autorizada de v4complete, (3) evidencia narrativa completa.

**Recuperación (misma sesión 5, autorizada por el usuario)**:
- Diagnóstico forense: `git log -L` identificó el commit 3e88251 (2026-08-21, "FIX V6") como introductor de la regresión: reemplazó `ota_commission_rate=0.15` por `FinancialFactors().get_comision_ota()['base']` en el bloque FASE-K sin agregar el import en el scope de `run_v4_complete_mode` (el import de L353 está dentro de otra función y es condicional). El NameError era atrapado por `except Exception` → `financial_breakdown=None` → `AssessmentBuilder.with_financial` inyectaba tier default "C" → gate BLOCKED falso → eliminación de docs. El baseline (20260821) corrió antes/aislado de ese commit por eso reportó tier "B+".
- Fix: `from modules.utils.financial_factors import FinancialFactors` agregado al bloque de imports de `run_v4_complete_mode` (main.py).
- Tests nuevos: 6 (clases `TestR0ERecoveryStaticContract` [2 AST], `TestR0ERecoveryFaseKBehavior` [2], `TestR0ERecoveryAssessmentTierChain` [2]) en `tests/financial_engine/test_fase_r0e_recovery_financial_factors.py`. Suites: recovery 6/6 + regression/assessment_builder/quality_gates 403/403 pasan.
- Re-ejecución autorizada: `v4complete --url https://zione.co/` → timestamp **20260824_113525**. Resultados: coherence **0.9485** (idéntico baseline), gates **12 PASSED + 1 WARNING** (idéntico baseline), tier **B+**, **READY_FOR_PUBLICATION**, pain_ledger 7 ids sin WhatsApp.
- Smoke S1-S7: **7/7 ✅**. Narrativa E2E verificada en output real: título "LAS 7 FUGAS PRINCIPALES" (B1/B4), título S1 "RESERVAS ESCAPÁNDOSE POR GOOGLE MAPS E IA" sin WhatsApp (B3), "Detecta las 7 fugas digitales" (B5), 7 fugas listadas (AC9), plan "Fase 1 (datos para IA)" sin WhatsApp (B6), "Servicios adicionales: Schema Organization" sin botón WhatsApp (B7). 0 menciones "WhatsApp incorrecto" (AC1/AC7 anticipo).
- Evidencia completa en `evidence/FASE-R0-E/` (baseline/ + output 20260824_113525).
- **FASE-R0-E COMPLETADA**. FASE-R0-F desbloqueada.

### FASE-R0-F
- Fecha: 2026-08-24. Modo: DIRECTO (presupuesto holgado, greps ejecutados en sesión). Iteraciones: ~12.
- Verificación formal AC1-AC12 sobre output E2E Zione (corrida 20260824_113525) vs baseline anómalo (20260821_175706).
- **12/12 ACs PASA**: AC1/AC2/AC3/AC5/AC6/AC8/AC9/AC10/AC11 verificados por lectura directa del output post-fix + comparación con baseline. AC4 verificado por unit test (Zione sin conflicto WhatsApp). AC7/AC12 por grep residual (0 matches).
- Diff narrativo antes/después documentado en 8 zonas (Sección 1 título+cláusula, Sección 4 título+contenido, Sección 5/8 Quick Wins, Sección 6, Propuesta L60/L203).
- Pain_ledger comparado byte-a-byte: idéntico (7 pain_ids, sin WhatsApp, mismas confidence/severity/status).
- Gate report verificado: 12 PASSED + 1 WARNING (idéntico baseline). Tier B+. READY_FOR_PUBLICATION.
- Coherence: 0.9485 (delta=0 vs baseline).
- 3 lecciones nuevas registradas: L-NC10 (fosilización como clase de bug), L-NC11 (E2E sobre unit tests), L-NC12 (diff como evidencia formal).
- `10-analisis-post-implementacion.md` completado: matriz B1-B7, AC1-AC12, diff narrativo, métricas, lecciones, seguimientos.
- Sin incidencias.

### FASE-RELEASE-4.72.1
- Fecha: 2026-08-24. Modo: DIRECTO. Iteraciones: ~20.
- Version bump: VERSION.yaml 4.72.0 → 4.72.1 “Coherencia Narrativa Dinámica” + bloque de comentarios del release.
- sync_versions.py: 6 archivos sincronizados (AGENTS.md, README.md, .cursorrules, CONTRIBUTING.md, GUIA_TECNICA.md, REGISTRY.md).
- CHANGELOG.md: entrada [4.72.1] con formato CONTRIBUTING completo (Objetivo/Cambios/Nuevos/Modificados/Tests).
- GUIA_TECNICA.md: sección “Notas de Cambios v4.72.1” con 4 campos (Módulos/Problema/Solución/Backwards).
- SYSTEM_STATUS.md regenerado (doctor.py --status).
- DOMAIN_PRIMER.md regenerado (194 archivos Python, 373 clases, 25 módulos).
- README.md audit: test count 3,360 → 3,379; fecha actualizada; gate count 12 → 13 (pricing_compliance).
- AGENTS.md audit: test count 3,360 → 3,379; archivos test 261 → 253; commercial_documents 251 → 279; financial_engine 500 → 549.
- run_all_validations.py --quick: 6/6 TOTAL PASS.
- validate_agents_md.py: ALL PASS (módulos 32/32, gates 13/13, test count within ±5%).
- Version Sync Gate: OK (CHANGELOG + VERSION.yaml sincronizados en 4.72.1).
- log_phase_completion.py ejecutado con --release automático.
- Sin incidencias.

## Sección D: Métricas Acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| Tests base al inicio del plan | 3,360 funciones / 261 archivos (v4.72.0) | Preparación |
| Tests nuevos R0-A | +1 (clase `TestB2QuickWinSchemaText` con 2 tests: sin_schema + schema_detectado) | FASE-R0-A |
| Tests nuevos R0-B | +4 (clase `TestFugasPrincipalesDinamicas`: sin-conflicto + guard anti-residuos, con-conflicto, contador título↔intro, derivación 1:1 fugas↔brechas) | FASE-R0-B |
| Tests acumulados tras R0-B | 3,365 (3,360 base +1 R0-A +4 R0-B) | FASE-R0-B |
| Tests nuevos R0-C | +3 (clases `TestSeccion1Conditional`, `TestSeccion6Contador`, `TestTemplateNoHardcodedFugas`: título S1 condicional con/sin conflicto, contador S6 dinámico, test estático anti-fosilización) | FASE-R0-C |
| Tests acumulados tras R0-C | 3,368 (3,360 base +1 R0-A +4 R0-B +3 R0-C) | FASE-R0-C |
| Tests nuevos R0-D | +4 (clases `TestFaseR0DPlan30DaysConditional`, `TestFaseR0DServiciosAdicionalesWhatsApp`: plan sin/con WhatsApp, servicios sin/con brecha) | FASE-R0-D |
| Tests acumulados tras R0-D | 3,372 (3,360 base +1 R0-A +4 R0-B +3 R0-C +4 R0-D) | FASE-R0-D |
| Coherence baseline anómalo (pre-fix) | 0.9485 — corrida 20260821_175706 (7 pain_ids, gates 13/13: 12 PASSED + 1 WARNING pricing_compliance, whatsapp VERIFIED) | Preparación |
| Coherence E2E post-fix | 0.9485 (idéntico al baseline — coherencia numérica intacta; corrida 20260824_113525) | FASE-R0-E |
| Gates E2E post-fix | 12 PASSED + 1 WARNING (pricing_compliance) — idéntico al baseline, tier B+ | FASE-R0-E |
| Pain_ids post-fix | 7 (no_hotel_schema, low_seo_score, no_faq_schema, no_analytics_configured, low_organic_visibility, ai_crawler_blocked, no_og_tags) — SIN WhatsApp ✅ | FASE-R0-E |
| Tests nuevos recovery FASE-R0-E | +6 (fix regresión `FinancialFactors` en main.py, clases TestR0ERecovery* — 2 AST estáticos + 2 comportamiento + 2 cadena assessment) | FASE-R0-E (recuperación) |
| Veredicto AC1-AC12 | 12/12 PASA (10 con verificación E2E + 2 por unit test exclusivo) | FASE-R0-F |

## Sección E: Archivos Afiliados Actualizados

| Archivo | Cambio | Fase |
|---------|--------|------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | B2: Quick Win #1 condicionado a `whatsapp_conflict` (texto ↔ condición alineados) | FASE-R0-A |
| `tests/commercial_documents/test_diagnostic_generator.py` | +2 tests: clase `TestB2QuickWinSchemaText` — Quick Win Schema sin WhatsApp cuando VERIFIED + Schema detectado no dispara Quick Win | FASE-R0-A |
| `modules/commercial_documents/v4_diagnostic_generator.py` | B1+B4: +`_build_fugas_principales_section()` (reutiliza narrativa dinámica de `_pain_to_brecha()` — D-NC6, destacadas por `impacto > 0`, orden por severidad, `${fugas_count_display}`); inyección en dict de render (zona L919-923) | FASE-R0-B |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | B1+B4: bloques de fugas hardcoded (L70-77) → `${fugas_principales_section}`; título L65 → `${fugas_title}` (pluralización dinámica) | FASE-R0-B |
| `tests/commercial_documents/test_diagnostic_generator.py` | +4 tests: clase `TestFugasPrincipalesDinamicas` — fugas sin conflicto (AC1 + guard 0 residuos `${`), con conflicto real (AC4, fuga "Conflicto de WhatsApp" derivada del pain), contador título coincide con listadas e intro (AC9/D-NC1), derivación 1:1 fugas↔brechas destacadas (AC3) | FASE-R0-B |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | B3: título S1 (L29) → `${seccion_1_canales}`; cláusula L39 → `${seccion_1_whatsapp_clausula}`; B5: "Detecta las 3 fugas" (L82) → `${brechas_total_count}` | FASE-R0-C |
| `modules/commercial_documents/v4_diagnostic_generator.py` | B3: helper `_has_whatsapp_conflict()` extraído de `_build_whatsapp_conflict_note()` (signal compartido); variables `seccion_1_canales` + `seccion_1_whatsapp_clausula` inyectadas en render dict | FASE-R0-C |
| `tests/commercial_documents/test_template_conditionals.py` | +3 tests: `TestSeccion1Conditional::test_seccion1_titulo_condicional` (con/sin conflicto), `TestSeccion6Contador::test_seccion6_contador_dinamico`, `TestTemplateNoHardcodedFugas::test_template_no_hardcoded_fugas` (estático anti-fosilización) | FASE-R0-C |
| `modules/commercial_documents/v4_proposal_generator.py` | B6: `whatsapp_conflict` cableado a `_build_30_day_plan()` + mención condicional; B7: botón de WhatsApp fuera de "Servicios adicionales" cuando no hay brecha ni conflicto (signal `breach_by_asset`) | FASE-R0-D |
| `tests/commercial_documents/test_proposal_dynamic.py` | +4 tests: plan sin WhatsApp, plan con WhatsApp, servicios sin brecha WhatsApp, servicios con brecha WhatsApp | FASE-R0-D |
| `evidence/FASE-R0-E/baseline/` | Baseline anómalo preservado (diagnóstico, propuesta, report, pain_ledger de corrida 20260821_175706) | FASE-R0-E |
| `evidence/FASE-R0-E/` | Evidencia proactiva post-fix (output completo 20260824_113525: diagnóstico, propuesta, report, gate_report, pain_ledgers, delivery ZIP) | FASE-R0-E |
| `main.py` | Recovery: import `FinancialFactors` en `run_v4_complete_mode` (fix regresión commit 3e88251 "FIX V6" que causaba tier_c BLOCKED falso) | FASE-R0-E (recuperación) |
| `tests/financial_engine/test_fase_r0e_recovery_financial_factors.py` | +6 tests: contrato AST (import presente y precede uso), comportamiento FASE-K, cadena assessment tier B+ | FASE-R0-E (recuperación) |
| `.opencode/plans/REFACTOR-COHERENCIA-NARRATIVA-2026-08-22/10-analisis-post-implementacion.md` | Matriz AC1-AC12 + lecciones + métricas completadas | FASE-R0-F |
| `VERSION.yaml` | bump 4.72.0 → 4.72.1 "Coherencia Narrativa Dinámica" + bloque de comentarios del release | FASE-RELEASE-4.72.1 |
| `CHANGELOG.md` | Entrada `[4.72.1]` (Objetivo/Cambios/Nuevos/Modificados/Tests) | FASE-RELEASE-4.72.1 |
| `docs/GUIA_TECNICA.md` | Sección "Notas de Cambios v4.72.1" | FASE-RELEASE-4.72.1 |
| `README.md` / `AGENTS.md` | Test count 3,360 → 3,379; gate count 12 → 13; fecha actualizada | FASE-RELEASE-4.72.1 |
