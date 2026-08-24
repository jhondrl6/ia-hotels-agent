# Análisis Post-Implementación — REFACTOR-COHERENCIA-NARRATIVA-2026-08-22

> **Estado**: Preparación completada (2026-08-22) — 13 archivos del plan creados; 0 fases ejecutadas.
> **Plan**: REFACTOR-COHERENCIA-NARRATIVA-2026-08-22 (v4.72.0 → v4.72.1 "Coherencia Narrativa Dinámica")
> **Causa raíz tratada**: fosilización narrativa — templates con texto estático que ignoran el pain_ledger (fuente de verdad dinámica).
> **Regla**: este archivo se crea DESDE LA CONCEPCIÓN del plan (executor v2.15.0) y se actualiza al cierre de CADA fase.

---

## Resumen de Ejecución (llenar al cierre de cada fase)

| Fase | Sesión | Estado | Iteraciones | delegate_task | Notas |
|------|---------|--------|-------------|---------------|-------|
| FASE-R0-A (B2 Quick Win) | Sesión 1 | ✅ COMPLETADA | ~15 | NO (directo) | Fix B2: texto Quick Win #1 ahora corresponde a condición `not hotel_schema_detected`. 2 tests nuevos (clase TestB2QuickWinSchemaText). 59/59 pasan. Grep AC12 limpio. |
| FASE-R0-B (B1+B4 Sección 4) ⚠️ | Sesión 2 | ✅ COMPLETADA | ~14 | NO (directo, DT-3) | Fix B1+B4: `_build_fugas_principales_section()` + template dinámico (`${fugas_title}` + `${fugas_principales_section}`). D-NC1/2/3/6 implementadas (extensión menor D-NC1: pluralización del título). 4 tests nuevos (total 3,365). Suites 27+42+6+26 = 101/101 pasan. Greps AC7/B1 limpios. |
| FASE-R0-C (B3+B5 títulos) | Sesión 3 | ✅ COMPLETADA | ~12 | NO (directo) | Fix B3+B5: helper `_has_whatsapp_conflict()` extraído (signal compartido); título S1 `${seccion_1_canales}` + cláusula `${seccion_1_whatsapp_clausula}` condicionales; contador S6 `${brechas_total_count}` dinámico. 3 tests nuevos (total 3,368). Suites 9+27+26 = 62/62 pasan. |
| FASE-R0-D (B6+B7 propuesta) | Sesión 4 | ✅ COMPLETADA | ~15 | NO (directo) | Fix B6+B7: `_build_30_day_plan()` con parámetro `whatsapp_conflict` cableado; B7: botón WhatsApp fuera de "Servicios adicionales" sin brecha (signal `breach_by_asset`). 4 tests nuevos (total 3,372). Suites pasan. |
| FASE-R0-E (E2E Zione) | Sesión 5 | ✅ COMPLETADA | ~20 | NO (terminal bg) | Corrida inicial bloqueada por tier_c falso (regresión externa: commit 3e88251 "FIX V6" — `FinancialFactors` sin import en `run_v4_complete_mode`). Recuperación en misma sesión (autorizada): import + 6 tests + re-ejecución 20260824_113525. Coherence 0.9485, gates 12P+1W, tier B+, READY. Smoke 7/7 ✅, narrativa E2E verificada (LAS 7 FUGAS, S1 sin WhatsApp, contador dinámico, plan sin WhatsApp, botón fuera de adicionales). |
| FASE-R0-F (verificación ACs) | Sesión 6 | ✅ COMPLETADA | ~12 | NO (directo, presupuesto holgado) | Verificación formal AC1-AC12 sobre output E2E Zione (20260824_113525): **12/12 PASA**. Diff narrativo antes/después documentado (7 zonas). Greps residuales 0 matches. Pain_ledger pre/post idéntico (7 pain_ids, sin WhatsApp). Gates 12 PASSED + 1 WARNING (idéntico baseline). Coherence 0.9485 (sin delta). 3 lecciones nuevas L-NC10 a L-NC12. |
| FASE-RELEASE-4.72.1 | Sesión 7 | ✅ COMPLETADA | ~20 | NO (directo) | Version bump 4.72.1. CHANGELOG + GUIA_TECNICA + sync 6 archivos. SYSTEM_STATUS + DOMAIN_PRIMER regenerados. README/AGENTS audit (test count 3,379). run_all_validations 6/6 TOTAL PASS. validate_agents_md ALL PASS. Version Sync Gate OK. |

---

## Matriz de Verificación de Hallazgos (llenar en FASE-R0-F; fuentes: `evidence/FASE-R0-E/` vs `evidence/FASE-R0-E/baseline/`)

### Parte 1: Bugs B1-B7

| # | Hallazgo | Expected | Real | Status |
|---|----------|----------|------|--------|
| B1 | Sección 4 con 3 fugas hardcoded (WhatsApp/Maps/IA) ignorando pain_ledger | Fugas derivadas del pain_ledger (7 pains Zione, sin WhatsApp) | **E2E verificado**: Sección 4 post-fix lista 7 fugas derivadas del pain_ledger (Sin Schema Hotel, SEO Local Bajo, Sin Schema FAQ, Sin Analytics, Baja Visibilidad, Crawlers IA, OG Tags). 0 menciones WhatsApp. Test unitario + output real coinciden. | ✅ FIX VERIFICADO (unit + E2E) |
| B2 | Quick Win "Corregir WhatsApp en Google Maps" disparado por `not hotel_schema_detected` | Quick Win menciona datos/Schema en Google; WhatsApp solo si `whatsapp_conflict=True` | **E2E verificado**: Quick Win #1 post-fix (L135): "Verificar qué datos de su hotel faltan en Google (ficha y resultados de búsqueda)." → nota DIY. Baseline (L123): "Corregir el número de WhatsApp en Google Maps." | ✅ FIX VERIFICADO (unit + E2E) |
| B3 | Título Sección 1 "…POR WHATSAPP, GOOGLE MAPS E IA" + "o el número no responde" sin condición | Título con canales dinámicos derivados del signal de conflicto | **E2E verificado**: Post-fix L29: "HOY HAY RESERVAS ESCAPÁNDOSE POR GOOGLE MAPS E IA" (sin WhatsApp). L39 sin cláusula de WhatsApp. Baseline L29: "…POR WHATSAPP, GOOGLE MAPS E IA"; L39: "o el número de WhatsApp no responde". | ✅ FIX VERIFICADO (unit + E2E) |
| B4 | "LAS 3 FUGAS PRINCIPALES" con número fijo (Zione: 7 brechas) | "LAS {N} FUGAS" con N = `len(brechas_destacadas)` | **E2E verificado**: Post-fix L105: "LAS 7 FUGAS PRINCIPALES". Baseline L105: "LAS 3 FUGAS PRINCIPALES". N=7 = len(brechas_destacadas) = fugas listadas (1-7). | ✅ FIX VERIFICADO (unit + E2E) |
| B5 | "Detecta las 3 fugas digitales" con número fijo | "Detecta las {N} fugas digitales" con N = `brechas_total_count` | **E2E verificado**: Post-fix L143: "Detecta las 7 fugas digitales". Baseline L131: "Detecta las 3 fugas digitales". N=7 = brechas_total_count. | ✅ FIX VERIFICADO (unit + E2E) |
| B6 | "(WhatsApp + datos para IA)" hardcoded en plan 30 días | Mención condicional a `whatsapp_conflict` | **E2E verificado**: Post-fix L203: "Implementación Fase 1 (datos para IA): Hotel Schema". Baseline L203: "Implementación Fase 1 (WhatsApp + datos para IA): Hotel Schema". Sin "WhatsApp + " en output. | ✅ FIX VERIFICADO (unit + E2E) |
| B7 | "Botón de WhatsApp" como servicio adicional cuando no es brecha | Botón fuera de "Servicios adicionales disponibles" cuando no hay brecha/conflicto WhatsApp (signal: `breach_by_asset` + `whatsapp_conflict`); sin claim de "ya presente" (los servicios excluidos carecen de señal de presencia) | **E2E verificado**: Post-fix L60: "Servicios adicionales disponibles: Schema Organization" (sin botón WhatsApp). Baseline L60: "Servicios adicionales disponibles: Botón de WhatsApp, Schema Organization". Zione: whatsapp VERIFIED, sin brecha → botón correctamente excluido. | ✅ FIX VERIFICADO (unit + E2E) |

### Parte 2: Criterios de Aceptación AC1-AC12

| AC | Criterio | Expected | Real | Status |
|----|----------|----------|------|--------|
| AC1 | Diagnóstico sin "Fuga 1 — Contacto perdido por WhatsApp incorrecto" con VERIFIED | 0 menciones en output post-fix | **E2E verificado**: Post-fix Sección 4 (L110-130): 7 fugas listadas, ninguna menciona WhatsApp. Fuga 1 = "Sin Schema Hotel". Test unitario + output real coinciden. grep "WhatsApp incorrecto" en output = 0. | ✅ PASA (unit + E2E) |
| AC2 | Quick Win #1 menciona Schema/datos (no WhatsApp) | Texto alineado a condición `not hotel_schema_detected` | **E2E verificado**: Post-fix L135: "Verificar qué datos de su hotel faltan en Google (ficha y resultados de búsqueda)." 0 menciones WhatsApp en Quick Wins. Baseline L123: "Corregir el número de WhatsApp en Google Maps." | ✅ PASA (unit + E2E) |
| AC3 | Fugas Sección 4 ↔ pain_ids pain_ledger 1:1 | Cada "### Fuga {n}" corresponde a un pain_id real | **E2E verificado**: 7 fugas listadas ↔ 7 pain_ids del pain_ledger (no_hotel_schema→Fuga1, low_seo_score→Fuga2, no_faq_schema→Fuga3, no_analytics_configured→Fuga4, low_organic_visibility→Fuga5, ai_crawler_blocked→Fuga6, no_og_tags→Fuga7). Correspondencia 1:1 confirmada. | ✅ PASA (unit + E2E) |
| AC4 | Conflicto real WhatsApp → fuga SÍ aparece | Test `test_fugas_principales_con_whatsapp_conflict` PASA | **E2E N/A** (Zione no tiene conflicto WhatsApp). Test unitario `test_fugas_principales_con_whatsapp_conflict` PASA: fuga "Conflicto de WhatsApp" aparece en Sección 4 cuando conflicto=True. | ✅ PASA (unit test) |
| AC5 | 0 regresiones en gates | 13/13 mismo estado que baseline (12 PASSED + 1 WARNING) | **E2E verificado**: Gate report 20260824_113525: 12 PASSED + 1 WARNING (pricing_compliance, pain_ratio 0.0724, floor $500K, tier standard gate_max 0.32: OK). Idéntico al baseline. `readiness.status = READY_FOR_PUBLICATION`. Tier B+. | ✅ PASA |
| AC6 | Coherence ≥ 0.8 | ≥ 0.8 (referencia baseline: 0.9485) | **E2E verificado**: Coherence = 0.9485 (idéntico al baseline 0.9485185185185185). Delta = 0. ≥ 0.8 ✅. Coherencia numérica completamente intacta tras refactor narrativo. | ✅ PASA |
| AC7 | grep "WhatsApp incorrecto" en `modules/` | 0 resultados (con D-NC6 la narrativa es dinámica y el string literal ya no existe en `modules/`) | 0 resultados (verificado 2026-08-24 post-fix) | ✅ PASA |
| AC8 | Pain_ledger sin alterar | Mismos 7 pain_ids (schema, seo, faq, analytics, visibility, crawlers, og) | **E2E verificado**: Comparación JSON baseline/pain_ledger.json vs pain_ledger_20260824.json: **idénticos** (byte-for-byte). 7 pain_ids: no_hotel_schema, low_seo_score, no_faq_schema, no_analytics_configured, low_organic_visibility, ai_crawler_blocked, no_og_tags. Sin WhatsApp. Confidence, severity, source_file, status: todos iguales. | ✅ PASA |
| AC9 | Título Sección 4 con número dinámico | N título = N fugas listadas = `brechas_destacadas_count` | **E2E verificado**: Post-fix L105: "LAS 7 FUGAS PRINCIPALES". Count("### Fuga ") = 7. Intro (L107): "estas 7 son las que más dinero". Triple coherencia: título=7, listado=7, intro=7. Baseline: título=3 vs listado=3 vs intro=7 (incoherente). | ✅ PASA (unit + E2E) |
| AC10 | Sección 6 con contador real | "Detecta las 7 fugas digitales" (caso Zione) | **E2E verificado**: Post-fix L143: "Detecta las 7 fugas digitales". Baseline L131: "Detecta las 3 fugas digitales". N=7 = brechas_total_count. | ✅ PASA (unit + E2E) |
| AC11 | Plan 30 días sin WhatsApp cuando `whatsapp_conflict=False` | "Implementación Fase 1 (datos para IA)" | **E2E verificado**: Post-fix L203: "Implementación Fase 1 (datos para IA): Hotel Schema". Baseline L203: "Implementación Fase 1 (WhatsApp + datos para IA): Hotel Schema". 0 menciones "WhatsApp + " en propuesta post-fix. | ✅ PASA (unit + E2E) |
| AC12 | grep "Corregir el número de WhatsApp" en `modules/` | 0 resultados | **E2E verificado**: grep en `modules/` = 0 resultados. grep en output post-fix = 0 resultados. String residual eliminado. | ✅ PASA |

### Parte 3: Diff narrativo antes/después (evidencia textual — llenar en R0-F)

| Zona del documento | Baseline anómalo (20260821_175706) | Post-fix (FASE-R0-E) |
|--------------------|-------------------------------------|----------------------|
| Sección 1 título | "…POR WHATSAPP, GOOGLE MAPS E IA" (L29) | "…POR GOOGLE MAPS E IA" (L29) — WhatsApp eliminado dinámicamente (Zione sin conflicto) ✅ |
| Sección 1 cláusula | "o el número de WhatsApp no responde" (L39) | Eliminada — `${seccion_1_whatsapp_clausula}` vacía cuando `whatsapp_conflict=False` ✅ |
| Sección 4 título | "LAS 3 FUGAS PRINCIPALES" (L105, incoherente con intro "7") | "LAS 7 FUGAS PRINCIPALES" (L105, coherente con intro "estas 7") ✅ |
| Sección 4 contenido | 3 fugas hardcoded: Fuga1=WhatsApp incorrecto, Fuga2=Google Maps, Fuga3=IAs (L110-118) | 7 fugas dinámicas del pain_ledger: Fuga1=Sin Schema Hotel, Fuga2=SEO Local Bajo, ..., Fuga7=OG Tags (L110-130) ✅ |
| Sección 5/8 Quick Wins | "Corregir el número de WhatsApp en Google Maps" (L123/L260) | "Verificar qué datos de su hotel faltan en Google (ficha y resultados de búsqueda)" (L135/L272) ✅ |
| Sección 6 | "Detecta las 3 fugas digitales" (L131) | "Detecta las 7 fugas digitales" (L143) ✅ |
| Propuesta L60-equiv. | "Servicios adicionales: Botón de WhatsApp, Schema Organization" | "Servicios adicionales: Schema Organization" (botón excluido — sin brecha WhatsApp) ✅ |
| Propuesta L203-equiv. | "Implementación Fase 1 (WhatsApp + datos para IA): Hotel Schema" | "Implementación Fase 1 (datos para IA): Hotel Schema" ✅ |

---

## Lecciones Aprendidas

### Lecciones capitalizadas de planes anteriores (CONTEXT §3 — CREDIBILIDAD-NUMERICA-2026-08-20)

| Lección | ID original | Aplicación en este plan |
|---------|-------------|--------------------------|
| Tras parametrizar constantes, verificar TAMBIÉN los strings de display que citan el valor | L30 | Sección 4 dinámica + verificación de Quick Wins, título S1 y toda narrativa de WhatsApp coherente con datos |
| Docs comerciales citan la fuente de verdad, no hardcodean valores | L27 | Fugas narrativas derivadas del pain_ledger |
| Nunca declarar bug sin leer el archivo completo | CONTEXT §1.3 | Verificación de TODAS las secciones que mencionan WhatsApp antes de modificar el template (evitar residuos) |
| Preferir extensión de taxonomía + whitelist sobre lógica paralela | L21 | Condición de WhatsApp extiende `_build_whatsapp_conflict_note()` existente |
| Verificar si el parámetro ya existe y el gap está en el caller | L16 | B6: `whatsapp_conflict` ya se extrae (L792-798) — solo faltaba pasarlo; B5: `${brechas_total_count}` ya existe |
| Verificar con grep que no queden referencias residuales | L2 | AC7/AC12: greps globales post-refactor (0 residuos) |
| Tests de contrato contra fuente dinámica, no valores fijos | L3 | Tests verifican fugas ↔ pain_ids reales, no expectativas de texto hardcodeadas |
| Para contratos transversales, AST en vez de regex | L7 | Test estático de template como guardián anti-re-fosilización |

### Lecciones nuevas de este plan (L-NC1+ — registrar al cierre de cada fase; mínimo 3 totales en R0-F)

> Formato: **qué pasó / por qué / qué lo previene** + pertinencia (INCLUIR/EXCLUIR de memoria).

| ID | Lección | Fase |
|----|---------|------|
| L-NC1 | Fix de copy-paste bug: el texto de un Quick Win decía “Corregir WhatsApp” cuando la condición era `not hotel_schema_detected`. / Por qué: el texto se escribió para una condición distinta y se reusó sin alinear. / Qué lo previene: cada rama condicional de `_build_quick_wins()` debe tener su texto validado contra la condición que lo dispara (test unitario con assert de contenido + grep de residuos). INCLUIR. | FASE-R0-A |
| L-NC2 | Contadores derivados: calcular `fugas_count_display` como `min(3, len(brechas_pesos))` (sugerencia original del CONTEXT) habría mostrado "3" en el título mientras la intro decía "estas 7" — recreando exactamente la incoherencia que el plan corrige. / Por qué: un contador acotado por constante pierde contacto con la lista que renderiza el cuerpo. / Qué lo previene: todo contador/título derivado DEBE calcularse desde la MISMA lista que renderiza el contenido (aquí `brechas_destacadas`), nunca desde una constante o un cap arbitrario. INCLUIR. | FASE-R0-B |
| L-NC3 | `string.Template.safe_substitute()` degrada en silencio: una variable faltante no crashea, deja el literal `${var}` en el documento comercial (corrupción invisible). / Por qué: safe_substitute está diseñado para tolerancia, no para contratos de template. / Qué lo previene: todo cambio de variables de template debe incluir un guard anti-residuos en tests (`assert "${" not in content` sobre el documento renderizado) — ahora presente en `test_fugas_principales_sin_whatsapp_conflict`. INCLUIR. | FASE-R0-B |
| L-NC4 | Cuando la narrativa ya existe dinámica en el pipeline (`pain.name`/`pain.description` vía `_pain_to_brecha()`), crear una nueva tabla estática pain_id→texto re-fosiliza (viola L27) y arriesga errores semánticos (la tabla original del CONTEXT confundía `low_seo_score` con la narrativa de `low_gbp_score`). / Por qué: las tablas paralelas se desincronizan del mapper. / Qué lo previene: antes de crear un mapping narrativo nuevo, verificar si el pipeline ya produce el texto dinámico (D-NC6). INCLUIR. | FASE-R0-B |
| L-NC5 | Extracción de helper compartido: al necesitar el mismo signal booleano en dos sitios (render dict + `_build_whatsapp_conflict_note()`), se extrajo `_has_whatsapp_conflict()` en lugar de duplicar la lógica. / Por qué: duplicar el criterio de conflicto (conflicts list + phone_web/phone_gbp) habría creado dos fuentes de verdad que pueden desincronizarse. / Qué lo previene: cuando dos consumidores necesitan el mismo signal, extraer un método compartido (bool) y que ambos lo invoquen — nunca copiar la lógica de detección. INCLUIR. | FASE-R0-C |
| L-NC6 | Cableado de parámetro existente: `whatsapp_conflict` ya se extraía en L792-798 pero no se pasaba a `_build_30_day_plan()`. / Por qué: el gap estaba en el caller, no en la fuente del dato (lección L16 confirmada). / Qué lo previene: al necesitar un signal en un método downstream, verificar primero si el valor ya existe en el scope del caller antes de crear una nueva fuente de verdad. INCLUIR. | FASE-R0-D |
| L-NC7 | Derivación dinámica de service_name: en vez de hardcodear "Botón de WhatsApp" para el filtro B7, se derivó de `PROPOSAL_SERVICE_TO_ASSET` (asset_type == "whatsapp_button"). / Por qué: los display names pueden cambiar en el catálogo; hardcodear crearía una fuente de verdad duplicada. / Qué lo previene: siempre derivar identificadores de negocio del catálogo fuente, nunca hardcodear strings de display en lógica de filtrado. INCLUIR. | FASE-R0-D |
| L-NC8 | Gate `tier_c_onboarding_required` con default destructivo: `assessment.get("financial_evidence_tier", "C")` en L1137 de `publication_gates.py` retorna el tier más restrictivo ("C") cuando la key está ausente. En la corrida E2E inicial, `financial_evidence_tier` no se inyectó en el assessment dict → gate BLOCKED → eliminación de diagnostic/proposal .md (pérdida de evidencia narrativa). Baseline tenía "B+". / Por qué: causa raíz final = commit 3e88251 "FIX V6" usó `FinancialFactors()` en el bloque FASE-K de main.py sin el import en `run_v4_complete_mode`; el NameError era atrapado silenciosamente por el except del bloque → breakdown=None → tier default "C". / Qué lo previene: (1) contrato AST que verifica el import (ya agregado en recovery); (2) un except que solo atrapa excepciones esperadas en vez de `Exception` genérico habría hecho visible el fallo; (3) considerar default menos destructivo o WARNING cuando la key está ausente. INCLUIR. | FASE-R0-E |
| L-NC9 | NameError silencioso por import faltante + except amplio: el bloque FASE-K usa `except Exception` y solo imprime warning, degradando en silencio (financial_breakdown=None) — el fallo tardó 2 días y una corrida E2E en manifestarse (como gate BLOCKED falso, no como error de import). / Por qué: `except Exception` + warning por print convierte errores de programación (NameError) en degradación funcional invisible. / Qué lo previene: al introducir una referencia nueva en un bloque con except amplio, verificar el import con test estático (AST) o ejecutar el bloque una vez; preferir except tipados (NameError nunca debería atraparse). INCLUIR. | FASE-R0-E |
| L-NC10 | Fosilización narrativa como clase de bug: los 7 bugs (B1-B7) compartían una única causa raíz — templates con texto estático que ignoraban la fuente dinámica de verdad (pain_ledger). No eran 7 bugs independientes sino 7 manifestaciones de un mismo defecto arquitectónico. / Por qué: cuando la capa de datos evoluciona (pain_ledger agrega VERIFIED_IN_SITE, filtrado por severidad) pero la capa narrativa permanece estática, se produce una divergencia silenciosa que no rompe ningún test pero genera documentos comercialmente contradictorios. / Qué lo previene: (1) tests de contrato que vinculan narrativa ↔ fuente dinámica (no valores fijos); (2) detección proactiva de strings hardcodeados que contradicen la fuente de verdad; (3) al agregar datos dinámicos nuevos, auditar si la capa narrativa los consume. INCLUIR. | FASE-R0-F |
| L-NC11 | Verificación E2E sobre unit tests exclusivamente: los tests unitarios de R0-A a R0-D cubrían cada fix aisladamente, pero solo la verificación E2E del output real (diagnóstico + propuesta renderizados) confirmó la integración coherente de los 7 fixes simultáneamente (p. ej., título S4 = 7 ↔ listado = 7 ↔ intro = 7 ↔ contador S6 = 7 ↔ pain_ledger = 7). / Por qué: tests unitarios validan contratos individuales; la integración de múltiples cambios en un documento renderizado puede producir incoherencias transversales que ningún test individual captura. / Qué lo previene: toda refactorización multi-punto debe incluir verificación E2E del output renderizado (no solo passing tests) antes de certificar. INCLUIR. | FASE-R0-F |
| L-NC12 | Diff antes/después como evidencia formal: la comparación byte-a-byte del baseline vs post-fix (7 zonas narrativas) fue la herramienta más efectiva para certificar que los fixes funcionaron correctamente en contexto real — más conclusiva que cualquier test unitario. / Por qué: un diff narrativo muestra exactamente qué cambió en lenguaje natural, mientras que un test solo verifica una condición booleana. / Qué lo previene: en planes de refactorización narrativa, incluir diff antes/después como deliverable obligatorio de la fase de verificación (no como opcional). El diff debe cubrir todas las zonas afectadas, no solo las obvias. INCLUIR. | FASE-R0-F |

---

## Seguimientos abiertos (llenar conforme avancen las fases)

| Tema | Estado | Acción futura |
|------|--------|---------------|
| Gate `tier_c_onboarding_required` BLOCKED falso: `FinancialFactors` sin import en `run_v4_complete_mode` | ✅ RESUELTO (recuperación FASE-R0-E, 2026-08-24) | Fix aplicado + 6 tests anti-regresión + corrida 20260824_113525 con 12 PASSED + 1 WARNING. Sin acción pendiente. |
| Gate tier_c default "C" cuando key ausente (defensivo) | 💡 MEJORA OPCIONAL | Considerar en plan futuro: default menos destructivo o WARNING (L-NC8 punto 3). No bloquea este plan. |

---

## Métricas de Ejecución (llenar al cierre)

| Métrica | Baseline (pre-fix) | Post-fix | Delta |
|---------|--------------------|----------|-------|
| Tests totales | 3,360 | 3,379 (3,372 plan + 6 recovery + 1 adicional) | +19 |
| Coherence E2E Zione | 0.9485 | 0.9485 | 0 (idéntico — coherencia numérica intacta; corrida 20260824_113525) |
| Gates de publicación | 13/13 (12 PASSED + 1 WARNING pricing_compliance) | 12 PASSED + 1 WARNING (idéntico baseline, tier B+, READY_FOR_PUBLICATION) | 0 (sin regresión) |
| Pain_ids detectados | 7 (schema, seo, faq, analytics, visibility, crawlers, og) | 7 (no_hotel_schema, low_seo_score, no_faq_schema, no_analytics_configured, low_organic_visibility, ai_crawler_blocked, no_og_tags) | 0 (idénticos, sin WhatsApp ✅) |
| Bugs narrativos abiertos (B1-B7) | 7 | 0 (verificado en output E2E real — narrativa dinámica en diagnóstico y propuesta) | -7 |
| ACs certificados | 0/12 | 12/12 PASA (10 con verificación E2E + 2 por unit test exclusivo) | +12 |
| Menciones "WhatsApp incorrecto" en `modules/` | >0 | 0 (narrativa dinámica D-NC6 elimina string literal) | eliminado |

---

## Decisiones Arquitectónicas (tomadas en preparación; confirmar implementación en cada fase)

| ID | Decisión | Rationale | Alternativas rechazadas | Fase |
|----|----------|-----------|-------------------------|------|
| D-NC1 | `fugas_count_display = str(len(brechas_destacadas))` | Para Zione destacadas=7; `min(3, …)` recrearía la incoherencia título-vs-contadores que el plan corrige | `min(3, len(brechas_pesos))` sugerido por CONTEXT §4.5 | R0-B ✅ (implementada 2026-08-24; extensión menor: título vía `${fugas_title}` pluralizado N=0/1/N, manteniendo `fugas_count_display` en el dict) |
| D-NC2 | Minimal-diff en template: conservar intro con contadores dinámicos (L67-68), reemplazar solo bloques de fugas (L70-77) por `${fugas_principales_section}` | Reduce superficie de cambio en la plantilla oficial v4.72.0; las variables existentes siguen usándose | Reescribir toda la Sección 4 | R0-B ✅ (implementada 2026-08-24 sin desviaciones) |
| D-NC3 | Narrativa directa vía `brecha['nombre']`/`brecha['detalle']` del dict ya calculado por `_pain_to_brecha()` | Nunca crash, nunca invención, sin desalineación de índices. El render usa `safe_substitute()` (variable faltante = residuo `${var}`, no crash total) | `_get_brecha_nombre(audit_result, idx)` — re-calcula la lista COMPLETA sin filtrar (L2515-2520) y sus índices absolutos se desalinearían con `brechas_destacadas` | R0-B ✅ (implementada 2026-08-24 sin desviaciones) |
| D-NC4 | B3 vía variable dinámica de canales (Opción B CONTEXT §4.3) | La Opción A (texto estático alternativo) reemplaza una fosilización por otra; la variable deriva del mismo signal que `_build_whatsapp_conflict_note()` | Opción A: dos textos estáticos condicionales | R0-C ✅ (implementada 2026-08-24 sin desviaciones; helper `_has_whatsapp_conflict()` extraído como fuente única de verdad para el signal) |
| D-NC5 | B5 reutiliza la variable EXISTENTE `${brechas_total_count}` | Lección L16: el gap está en el caller (template), no en el generador; cero código nuevo | Nueva variable de contador en el generador | R0-C ✅ (implementada 2026-08-24 sin desviaciones) |
| D-NC6 | NO crear nueva tabla estática pain_id → narrativa: reutilizar `nombre`/`detalle` dinámicos de `_pain_to_brecha()` (16 pain_ids) | Una tabla nueva re-fosilizaría la narrativa (viola L27) y la propuesta original contenía un error semántico (`low_seo_score` → narrativa de Google Maps que corresponde a `low_gbp_score`) | Tabla estática de 8 entradas del CONTEXT §4.1 | R0-B ✅ (implementada 2026-08-24 sin desviaciones) |
| D-NC7 | B7: el botón de WhatsApp sale de "Servicios adicionales" cuando no hay brecha ni conflicto (signal dinámico `breach_by_asset`); NUNCA afirmar "ya presente" sin señal de presencia | `excluded_services` contiene display names (no asset_types) y sus servicios entran por `not has_asset and not is_present` — no hay señal de presencia que respalde ese claim | Opción B original ("ya presente y funcional") — factualmente falsa sin señal de presencia | R0-D |

---

## Checklist de Cierre (FASE-RELEASE — 2026-08-24)

- [x] Todas las fases ✅ en `06-checklist-implementacion.md` (R0-A a R0-F)
- [x] Matriz de Verificación completa: 7/7 bugs + 12/12 ACs con Real/Status
- [x] Lecciones nuevas registradas (mínimo 3, formato qué pasó/por qué/qué lo previene) — 12 lecciones L-NC1 a L-NC12
- [x] Métricas de Ejecución post-fix completadas
- [x] VERSION.yaml == "4.72.1" + sync 6 archivos + Version Sync Gate OK
- [x] CHANGELOG `[4.72.1]` + GUIA_TECNICA "Notas de Cambios v4.72.1"
- [x] `run_all_validations.py --quick` TOTAL PASS (6/6)
- [x] README/AGENTS audit: test count 3,379 verificado contra `pytest --collect-only`
- [ ] Commit de release ejecutado — pendiente de ejecución por el usuario
- [x] Seguimientos abiertos: ninguno o con plan asignado (gate tier_c default “C” → mejora opcional futura)
