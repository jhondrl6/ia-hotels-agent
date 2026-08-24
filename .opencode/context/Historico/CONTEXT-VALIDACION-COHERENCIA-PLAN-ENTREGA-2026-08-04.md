# CONTEXT — Validación de Coherencia + Capitalización de Lecciones (COHERENCIA-MODULO-ENTREGA-2026-08-03)

> **Fecha**: 2026-08-04 (post-FASE-RELEASE)
> **Alcance**: Validación de coherencia y alineación entre los 13 documentos del plan `COHERENCIA-MODULO-ENTREGA-2026-08-03` (`.opencode/plans/`), los 2 documentos E2E generados en FASE-E (`output/v4_verify_4.70.0/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260804_124443.md` y `02_PROPUESTA_COMERCIAL_20260804_124443.md`) y los módulos de producción involucrados.
> **Método**: Verificación contra código vivo (grep/read_file) + evidencia JSON del run E2E + diff entre runs + pytest --collect-only. Sin modificaciones de código.
> **Fuente de experiencia**: `10-analisis-post-implementacion.md` del plan — **NO se audita ese archivo; se capitalizan sus lecciones L1-L15** para enriquecer las recomendaciones y el protocolo de ejecución de los hallazgos.
> **Resultado**: 26/26 claims verificados (21 del 10-analisis + 5 hallazgos N10-N14) **CONFIRMADOS contra código vivo** y evidencia del run final; **7 amplificaciones nuevas (N15-N21)** derivadas de la misma cadena causal; **causas raíz RC1-RC3 identificadas con evidencia de commit**; lecciones L1-L15 integradas como protocolo operativo. Actualización post-re-validación: 2026-08-04 (§2.5, §2.6, §5, §6).

---

## Veredicto Ejecutivo

Los documentos del plan están **coherentes entre sí y alineados con el código de producción** en lo que el plan declaró haber corregido: la matriz de verificación E2E (D1-D12 + N1-N9) se confirmó **21/21 contra código vivo y contra la evidencia JSON del run final (20260804_124443)**. La versión no tiene drift (VERSION.yaml / CHANGELOG / AGENTS.md / GUIA_TECNICA = 4.70.0 ✅) y el conteo de tests live es 3,215 (✅ coincide con RELEASE).

**PERO** la validación encontró **1 hallazgo de ALTA severidad que el plan declaró resuelto y no lo está**: los costos y numeración de brechas en la **tabla de servicios de la PROPUESTA** (`BREACH_BY_ASSET` hardcodeado en `v4_proposal_generator.py` L1193-1206) **NO coinciden con el diagnóstico del mismo run** — exactamente la clase de incoherencia módulo↔entrega que este plan fue creado para eliminar (regla de oro del plan maestro: "una fuente de verdad por concepto — costos (1)"). La matriz D3 solo verificó report↔diagnóstico, no diagnóstico↔propuesta.

**Veredicto**: ✅ Plan y módulos alineados en 21/21 hallazgos declarados; ⚠️ 1 hallazgo residual de ALTA (N10, propuesta con costos divergentes) + 1 de MEDIA (N11, commercial gate BLOCKING no documentado) requieren decisión de seguimiento (release posterior o FASE adicional). Las lecciones L1-L15 del 10-analisis proveen el protocolo operativo para ejecutar esas acciones sin repetir los bloqueos ya vividos.

**Post-validación ampliada (misma sesión, 2026-08-04)**: la re-validación exhaustiva contra código vivo confirma 26/26 claims SIN falsos positivos y añade **7 hallazgos nuevos (N15-N21)** que agrandan el alcance de los hallazgos originales:
- **N15 (MEDIA)**: CG-TIER-CONSISTENCY es un **no-op estructural** — `validate_diagnostic` nunca pasa `frontmatter_tier`/`text_tier` (defaults None), el texto del diagnóstico menciona Tier 6 veces, pero el gate siempre responde "Sin datos de tier para comparar" (pasa vacuo SIEMPRE).
- **N16 (MEDIA)**: el **ZIP de entrega transporta evidence BLOCKING junto a un doc PASSED** — `commercial_gates_report_diagnostic_20260804_124443.json` (all_passed=false) viaja en `zione_20260804.zip` al lado del diagnóstico cuyo frontmatter dice `gate_status: PASSED` y que oculta el BLOCKING al cliente (document_audience=client → solo logging).
- **N17 (MEDIA)**: el **mapeo servicio→brecha está invertido** — la fila "SEO Local" muestra "#1: Sin Schema Hotel" (`BREACH_BY_ASSET["optimization_guide"]`) cuando su brecha real es `low_seo_score` (BRECHA 3 SEO Local Bajo $1,198,906).
- **N18 (BAJA)**: "Brecha #5: WhatsApp no coincide" es un **hardcode separado** en `v4_proposal_generator.py` L1250 (fuera del mapa; rank stale #5 vs rank vivo 1).
- **N19 (BAJA)**: "Schema Organization" es un **servicio fantasma** (L61) — org_schema no fue generado en el run y no existe brecha "Sin Schema Org" en el diagnóstico.
- **N20 (BAJA)**: **drift documental en el PROPIO contexto** — §4 cita `_coverage_gate` def real L1187, pero hoy está en L1160 (−27); y la evidencia del diff N3 (97 líneas) **no es reproducible** (los .md del run 123637 ya no existen en disco).
- **N21 (INFO)**: el ZIP contiene **artefactos de AMBOS runs** del día (123637 y 124443), incluyendo la evidencia del run fallido sin onboarding.

**Causa raíz dominante (RC1)**: la unificación de costos (D3/FASE-B) se aplicó al diagnóstico y al report (`opportunity_scores`), **NO a la tabla de servicios de la propuesta**, que quedó con su mapa estático pre-D3 del commit `3c3b9f8` (era FASE-C PROPUESTA-COMERCIAL). El pipeline YA produce la data correcta; el generador de propuesta no la consume. Recomendaciones R1.x/R2.x/R3.x por causa raíz en **§2.6**.

---

## 1. Matriz de Verificación — Claims del 10-analisis vs Código Vivo (21/21 CONFIRMADOS)

> Método: cada claim verificado con grep sobre el código de producción, lectura del JSON de evidencia del run final (timestamps 20260804_124443 / 124429) y/o lectura directa de los docs E2E. Los valores citados del doc corresponden a `01_DIAGNOSTICO_Y_OPORTUNIDAD_20260804_124443.md` (L#) y `02_PROPUESTA_COMERCIAL_20260804_124443.md` (L#).

| # | Claim | Verificación contra código vivo / evidencia | Status |
|---|-------|---------------------------------------------|--------|
| D1 | Brecha OG veraz: "Open Graph Tags Incompletos (8 tags)" | Doc L82-83: "[BRECHA 8] Open Graph Tags Incompletos — Se detectaron 8 OG tags"; L158 breakdown "✅ open_graph(15%)"; L198 "Open Graph: Configurado"; audit_report_124429.json `"open_graph": true` con og:title/og:image/og:description | ✅ CONFIRMADO |
| D2 | N brechas consistente (8 en doc, 9 en ledger = 8+1 justificada) | Doc L113: "De las 8 brechas técnicas detectadas, estas 8... Las otras 0"; costos 8 brechas suman **$7.192.000 exacto** (L50-85: 1,198,906+1,498,094+1,198,906+719,200+599,094+599,094+899,000+479,706); pain_ledger.json = 9 entries (incluye `no_whatsapp_visible` HIGH conf 0.3); gate coverage "8 en diagnostico/propuesta, 1 justificadas de 9" | ✅ CONFIRMADO |
| D3 | estimated_monthly_cop report == costos doc (8/8) | v4_complete_report.json `opportunity_scores` = 8 entries: whatsapp_conflict 1,198,906 / no_hotel_schema 1,498,094 / no_faq_schema 719,200 / low_seo_score 1,198,906 / no_analytics 599,094 / low_organic 599,094 / ai_crawler 899,000 / no_og 479,706 — suma **7,192,000 = doc** | ✅ CONFIRMADO (nota: la lista citada en el 10-analisis omite el 2º 1,198,906 — ver drift N14) |
| D4 | Escenarios reales 19.6M/7.19M/−6.8M con labels; CG-SCENARIO-ORDER | Doc L216-218: "Peor caso (conservador) $19.627.200 70% / Más probable $7.192.000 20% / Mejor caso (optimista) Ganancia neta $6.820.800 10%"; `commercial_gates_report_diagnostic_20260804_124443.json` contiene CG-SCENARIO-ORDER (passed=true, BLOCKING) | ✅ CONFIRMADO (⚠️ ver N11: el MISMO archivo tiene all_passed=False con CG-CLAIM-VS-EVIDENCE BLOCKING) |
| D5 | coverage honesto: covered>0 | gate_report_20260804_124443.json: "Coverage completo: 8 en diagnostico/propuesta, 1 justificadas de 9 detectadas" (covered=8) | ✅ CONFIRMADO |
| D6 | CWV estado real ("API key inválida") | Doc L209: "Invalid URL or request: API key not valid. Please pass a valid API key." (error real del run, key `***` de test) | ✅ CONFIRMADO |
| D7 | Reviews parametrizadas (no "203") | Doc L193: "966 reviews, 4.4/5 rating"; L169 "966 reseñas"; grep "203 reseñas" = 0 hits | ✅ CONFIRMADO |
| D8 | Atribución GEO correcta | Doc L161 + L326: "algoritmo propio de IA Hoteles Agent sobre datos de Google Places" (2 menciones); grep "algoritmo de Google" = 0 hits | ✅ CONFIRMADO |
| D9 | Target fotos 40 compartido | Doc L208: "Subir al menos 30 fotos adicionales" (actual 10 + 30 = 40); código: `TARGET_GBP_PHOTOS = 40` en v4_diagnostic_generator.py L1807, usado en L1811-1812 | ✅ CONFIRMADO |
| D10 | Redes sin duplicados + TikTok/YouTube | Doc L194: "Instagram, Facebook, TikTok, YouTube" | ✅ CONFIRMADO |
| D11 | commercial_gates_report fresco (timestamp == run) | `commercial_gates_report.json` mtime 12:44 == run final; `commercial_gates_report_diagnostic_20260804_124443.json` del mismo run; código: v4_proposal_generator.py L612-616 escribe SIEMPRE (fuera del branch de error) | ✅ CONFIRMADO |
| D12 | occupancy label por origen ("onboarding") | gate_report: `financial_sources.occupancy_rate = "onboarding"` (también direct_channel_percentage=onboarding, adr_cop=user_provided); valor 0.7843 = 800/(34×30) ✅; **residuo S5 CONFIRMADO en vivo**: financial_scenarios_20260804_124429.json `breakdown.data_sources.occupancy = "regional"` | ✅ CONFIRMADO (residuo S5 real) |
| N1 | Recuperación 6m idéntica diag ↔ propuesta | Diagnóstico L224: "$9.691.220 COP"; Propuesta L134 y L154: "$9.691.220 COP" (3 menciones); ambos con curva 3.85 meses × 35% | ✅ CONFIRMADO |
| N2 | Gate doc↔audit (WARNING) detecta contradicciones | `_doc_audit_consistency_gate` existe en publication_gates.py L1380 (registrado L185); gate_report: "No audit data available for doc-audit consistency check" (PASSED, limpio con fundamento); hard_contradictions = 0 (count) | ✅ CONFIRMADO |
| N3 | Docs NO byte-idénticos entre runs (>3 líneas) | diff run1 (123637, sin onboarding) vs run final (124443): **97 líneas** de diferencia (generated_at, coherence 0.867→0.917, tier B→B+, costos $623K→$1.198.906, escenarios completos) | ⚠️ CONFIRMADO PARCIAL — los .md del run1 ya no existen en disco (solo quedan audit_report_20260804_123620.json, gate_report_20260804_123637.json, commercial_gates_report_diagnostic_20260804_123637.json); el diff de 97 líneas NO es reproducible hoy → evidencia E2E no preservada (ver N20) |
| N4 | ZIP solo artefactos del run actual | `zione_20260804.zip` (76 entries): **0 entries con mtime < 2026-08-04 12:00**; código: delivery_packager.py L286-304 `freshness_cutoff = now - 86400` filtra v4_audit | ✅ CONFIRMADO (⚠️ ver N21: incluye artefactos de 2 runs del mismo día) |
| N5 | "arriba" (no "acima") | diagnostico_v6_template.md L58 "La cifra arriba..."; propuesta_v6_template.md L128 "Las cifras arriba..."; grep "acima" = 0 hits en templates y docs | ✅ CONFIRMADO |
| N6 | "Por qué importa" | v4_diagnostic_generator.py L2558 (claim decía L2555 — offset +3, drift menor); doc L49 usa "Por qué importa" en las 8 brechas | ✅ CONFIRMADO (drift línea) |
| N7 | Truncamiento por palabra | v4_diagnostic_generator.py L2528 + L2574: `detalle[:80].rsplit(' ', 1)[0]` + '...' | ✅ CONFIRMADO |
| N8 | Label de confianza coherente (prob_realista) | Pre-resuelto FASE-B; doc L254: "escenario más probable (probabilidad 20% de ocurrencia)" — sin "70% de confianza" mal atribuido (grep = 0 hits) | ✅ CONFIRMADO |
| N9 | execution_trace coherente con texto | Doc refleja error real de PageSpeed (D6); audit_report_20260804_124429.json `execution_trace`: `pagespeed_api` en executed Y skipped — duplicación residual aceptada como seguimiento S6 (no re-verificada el 08-04) | ✅ CONFIRMADO (parcial, S6) |

**Verificación de conteos live adicionales:**
- `pytest --collect-only` = **3,215 tests collected** (2.52s) — coincide con 11-doc "3,215 (+30 vs baseline 3,185)" ✅
- VERSION.yaml 4.70.0 == CHANGELOG `[4.70.0]` == AGENTS.md v4.70.0 (3 menciones) == docs/GUIA_TECNICA.md v4.70.0 (3 menciones) ✅ **sin drift de versión**
- Módulos: 205 archivos .py (sin tests/__pycache__) / 391 clases (criterio: incl. anidadas, grep `^class |^    class `; solo columna-0 = 387) / 27 dirs con __init__ vs claim 11-doc "194 archivos, 373 clases, 25 módulos" → **N14 drift documental menor** (criterio de conteo no especificado en el doc)
- gate_report_20260804_124443.json: **12/12 gates PASSED**, readiness `READY_FOR_PUBLICATION` (respaldan el "12 gates PASSED" del 10-analisis — que se refiere al report de PUBLICACIÓN, no al commercial report del diagnóstico, ver N11)

---

## 2. Hallazgos NUEVOS (mantenidos de la validación — no documentados en el plan)

### N10 (ALTA) — BREACH_BY_ASSET hardcodeado: la propuesta muestra costos y numeración de brechas que NO coinciden con el diagnóstico del mismo run

**Ubicación**: `modules/commercial_documents/v4_proposal_generator.py` L1193-1206 (`BREACH_BY_ASSET`).

**Evidencia** (run E2E 20260804_124443, MISMA ejecución para ambos docs):

| Servicio (propuesta L54-59) | Propuesta muestra | Diagnóstico (mismo run) | Diferencia |
|---|---|---|---|
| SEO Local | "#1: Sin Schema Hotel ($1,005,768/mes)" | BRECHA 3 SEO Local Bajo = $1,198,906 | # y costo mal; mapea a Schema (ver N17) |
| Schema Hotel | "#1: Sin Schema Hotel ($1,005,768/mes)" | BRECHA 2 Sin Schema Hotel = **$1,498,094** | costo ≈ 0.671× |
| Página de FAQ | "#4: Sin FAQ ($482,679/mes)" | BRECHA 4 Sin Schema FAQ = **$719,200** | costo ≈ 0.671× |
| Meta Tags Sociales (OG) | "#6: Sin OG Tags ($321,786/mes)" | BRECHA 8 OG Incompletos = **$479,706** | # y costo; costo ≈ 0.671× |
| Optimización IA Generativa | "#3: Baja prep. IA ($603,536/mes)" | BRECHA 7 Crawlers IA = **$899,000** | # y costo; costo ≈ 0.671× |
| Botón de WhatsApp | "Brecha #5: WhatsApp no coincide" | BRECHA 1 Conflicto de WhatsApp = $1,198,906 | # erróneo (hardcode separado L1250, ver N18) |
| Schema Organization | "#7: Sin Schema Org ($321,786)" (servicio adicional) | No existe como brecha en Zione | fantasma (ver N19) |

**Análisis**: factor uniforme ≈ 0.671 (1,005,768/1,498,094; 482,679/719,200; 321,786/479,706; 603,536/899,000) → los costos de la propuesta provienen de OTRA fuente de pesos (pesos pre-normalización de la era pre-D3), NO de `estimated_monthly_cop` que FASE-B alineó. La **regla de oro del plan ("una fuente de verdad por concepto — costos (1)") se cumple para diagnóstico↔report (D3 ✅) pero NO para propuesta↔diagnóstico**: la propuesta muestra al cliente cifras de fuga por brecha que contradicen el diagnóstico que la acompaña.

**Causa raíz a nivel commit (ampliada en re-validación)**: el mapa nació en `3c3b9f8` (FASE-C PROPUESTA-COMERCIAL, era v4.34) con estos valores exactos; FASE-A (`c70d68a`) tocó solo `v4_diagnostic_generator.py` + main.py; FASE-B (`ee3f13f`) tocó la propuesta SOLO para N1 (recuperación 6m: 10 inserciones/9 borrados, todos de `calcular_recuperacion_6m` — los costos del mapa nunca se actualizaron); FASE-D (`338c46b`) tampoco. El pipeline YA produce `opportunity_scores` con el costo correcto (8 entries, suma 7,192,000); el generador de propuesta simplemente no lo consume.

**Por qué el plan lo dejó pasar**: la matriz D3 verificó "estimated_monthly_cop del report == costos del doc" (report↔diagnóstico) y N1 verificó la recuperación 6m; ninguna fila cruza la tabla de servicios de la propuesta contra el diagnóstico. El mapa BREACH_BY_ASSET es un literal estático del generador de propuesta (clase Pitfall 6 de iah-cli-audit-verification-pitfalls: hardcoded strings en campos supuestamente dinámicos).

**Acción futura sugerida**: parametrizar `BREACH_BY_ASSET` desde `opportunity_scores` del report (brecha_id → rank + estimated_monthly_cop) keyed por asset_type vía `ASSET_TO_PAIN_ID`/`pain_solution_mapper`, o al menos verificar en FASE-E de releases futuras que propuesta y diagnóstico citen las mismas cifras por brecha. Añadir check de cierre: "grep BREACH_BY_ASSET" + "costo propuesta == costo diagnóstico". **Protocolo operativo → §3.1.** Alcance ampliado por N17/N18/N19 → **§2.5/§2.6 (RC1)**.

### N11 (MEDIA) — commercial_gates_report_diagnostic del run E2E tiene all_passed=False con un BLOCKING no documentado

**Evidencia**: `output/v4_verify_4.70.0/v4_complete/zione/v4_audit/commercial_gates_report_diagnostic_20260804_124443.json`:
- `all_passed: False`, `blocking_passed: False`
- summary: "1 BLOCKING failure(s): **CG-CLAIM-VS-EVIDENCE** | 3 WARNING(s): CG-SCENARIO-NEGATIVE, CG-WHATSAPP-LEAD, CG-TECH-JARGON"
- CG-CLAIM-VS-EVIDENCE (passed=false, BLOCKING): "El documento dice 'no aparece' pero place_found=True y rating=4.4/5.0. El hotel SÍ aparece en Google."

**Contexto**: la frase que dispara el gate es del diagnóstico L123: "si su web no tiene los datos correctos, no aparece en la respuesta" — texto **hipotético/condicional** ("si..."), no una afirmación literal de que el hotel no aparece. El gate parece interpretar "no aparece" como claim factual → **falso positivo probable del patrón del gate** (texto condicional mal parseado).

**Causa raíz a nivel código (ampliada)**: `commercial_gate.py` L523-530 usa el regex `[Nn]o\s+aparece|[Nn]o\s+figura|no\s+est[aá]\s+en\s+Google|invisible\s+en\s+b[uú]squedas` sobre el texto COMPLETO, sin parseo de oraciones ni manejo de cláusulas condicionales ("si X, no aparece"). El falso positivo es estructural, no un caso puntual. Además, el veredicto BLOCKING del diagnóstico se OCULTA al cliente (`document_audience=client` → solo `logging.warning("hidden from client")`, v4_diagnostic_generator.py L676) pero el report viaja dentro del ZIP de entrega (ver N16).

**Por qué importa**: el 10-analisis D4 verifica "CG-SCENARIO-ORDER presente" ✅ (cierto) pero **no menciona el estado global del archivo** (all_passed=False). El 10-analisis/11-doc declaran "12 gates PASSED" — cierto para el gate_report de publicación (12/12 ✅ verificado), pero la evidencia E2E incluye un commercial gate report con un BLOCKING que ningún documento del plan reporta. No bloqueó la publicación (el gate de publicación es otro), pero la declaración "gates honestos PASSED" del checklist es incompleta sin este matiz.

**Acción futura sugerida**: (a) documentar el estado all_passed=False del commercial report en el análisis E2E; (b) afinar el patrón CG-CLAIM-VS-EVIDENCE para ignorar oraciones condicionales ("si X entonces no aparece"); o (c) aceptar como falso positivo conocido y registrarlo. **Protocolo operativo → §3.2. Alcance ampliado por N15/N16 → §2.5/§2.6 (RC2).**

### N12 (BAJA) — Docs E2E versionados 4.69.0 (pre-bump), no 4.70.0

**Evidencia**: frontmatter de `01_DIAGNOSTICO_Y_OPORTUNIDAD_20260804_124443.md` y `02_PROPUESTA_COMERCIAL_20260804_124443.md`: `version: 4.69.0`; mientras VERSION.yaml/CHANGELOG/GUIA_TECNICA están en 4.70.0.

**Análisis**: correcto por diseño — FASE-E ejecutó v4complete ANTES del bump de FASE-RELEASE (el run verifica los fixes, el bump ocurre después). No es un bug; es un detalle de interpretación: los artefactos del directorio `v4_verify_4.70.0` son pre-release (4.69.0 + fixes). Debe quedar documentado para que un futuro lector no interprete el frontmatter como drift.

**Acción futura sugerida**: nota en 10-analisis/11-doc: "los artefactos E2E llevan la versión del código que corrió (4.69.0 + fixes); el bump a 4.70.0 es posterior y no se re-ejecutó v4complete". **→ R3.3.**

### N13 (BAJA) — Prompts 02-05 aún traen `--release 4.70.0` en la plantilla (L3/L9 no se aplicó)

**Evidencia**: `.opencode/plans/COHERENCIA-MODULO-ENTREGA-2026-08-03/0{2,3,4,5}-prompt-*.md` contienen `log_phase_completion.py ... --release 4.70.0` (1 ocurrencia c/u); 06/07/08 no lo traen. La lección L3 (FASE-A) y L9 (FASE-B) documentaron que `--release` en fases intermedias dispara el VERSION SYNC GATE imposible; el seguimiento abierto del 10-analisis decía "corregir plantillas en FASE-RELEASE" — **no se corrigió**. Nota de re-validación: `01-plan-maestro.md` también contiene `--release 4.70.0` (esperable para la fase RELEASE, pero el contexto original no lo listó).

**Acción futura sugerida**: eliminar `--release 4.70.0` de los prompts 02-05 (o añadir nota "NO usar --release en fases intermedias"). Aplica también a cualquier re-ejecución del plan. **→ R3.1.**

### N14 (BAJA) — Drift documental en conteos del 11-documentacion-post-proyecto.md

- **Módulos**: claim "194 archivos, 373 clases, 25 módulos (24 en modules/, 1 root)" vs live: 205 archivos .py (sin tests/__pycache__), 391 clases (incl. anidadas), 27 dirs con `__init__.py`. Criterio de conteo no especificado en el doc.
- **Aritmética acumulativa**: fila "Hallazgos cerrados 17/21" en FASE-D — la suma de filas anteriores (2+3+2+3=10) + los 9 listados (+D9..+N8) = **19**, no 17. El total final 21/21 es correcto; el acumulado parcial está mal calculado.
- **D3 lista de costos**: la fila D3 cita "(1,198,906 / 1,498,094 / 719,200 / 599,094 ×2 / 899,000 / 479,706)" = 7 valores; el report real tiene **8** (el 2º 1,198,906 de `low_seo_score` se omite). La suma es correcta (7,192,000), solo la lista está incompleta.

**Acción futura sugerida**: corregir los tres puntos en el 11-doc (o marcarlos como criterio distinto de conteo). **Protocolo operativo → §3.4 (L8: contar siempre desde el diff/fuente viva, no desde notas previas). → R3.2.**

---

## 2.5 Amplificación de la re-validación (2026-08-04, post-contexto) — Hallazgos N15-N21

> Método: re-validación exhaustiva contra código vivo (grep/read_file), evidencia JSON del run 124443, contenido del ZIP de entrega (`zione_20260804.zip`, 76 entries) y diff de commits (`git show`). 26/26 claims confirmados sin falsos positivos. Los 7 hallazgos nuevos son amplificaciones de N10/N11 — misma cadena causal.

### N15 (MEDIA) — CG-TIER-CONSISTENCY es un no-op estructural (gate que valida inputs nunca poblados)

**Evidencia**: `modules/commercial_documents/v4_diagnostic_generator.py` L617-654 llama `validator.validate_diagnostic(...)` SIN pasar `frontmatter_tier`/`text_tier` (defaults None en `modules/quality_gates/commercial_gate.py` L125-126, invocado en L167). El texto del diagnóstico menciona Tier 6 veces (A, B, B+×2, C×2) y el frontmatter tiene `coherence_score`, pero el gate siempre responde "Sin datos de tier para comparar (frontmatter o texto no disponibles)" (passed=true WARNING, L640). **El gate NUNCA valida nada.** Clase Pitfall 12 (gates que validan inputs, no el artefacto — inputs que el productor no puebla). El 11-doc lo lista entre los gates verificados como si cubriera algo.

**Fix sugerido (R2.2)**: añadir `evidence_tier` al frontmatter del diagnóstico (el dato ya existe en `financial_breakdown.evidence_tier`) y extraer tier del texto con regex; si los inputs siguen None, el gate debe FALLAR (o eliminarse), nunca pasar vacuo.

### N16 (MEDIA) — El ZIP de entrega transporta evidence BLOCKING junto a un doc PASSED

**Evidencia**: `zione_20260804.zip` incluye `ASSETS/v4_audit/commercial_gates_report_diagnostic_20260804_124443.json` (all_passed=false, "1 BLOCKING failure(s): CG-CLAIM-VS-EVIDENCE") al lado del diagnóstico cuyo frontmatter dice `gate_status: PASSED` y que NO lleva sección de alertas (grep "Alertas Comerciales" = 0 hits; `document_audience=client` → el BLOCKING solo se loguea "hidden from client", v4_diagnostic_generator.py L676). El entregable al cliente transporta evidencia interna contradictoria con el estado publicado del documento — exactamente la clase de incoherencia módulo↔entrega que el plan debía eliminar. El report de la PROPUESTA (`commercial_gates_report.json`) sí pasó blocking (blocking_passed=true, solo warnings) — por eso no abortó la generación (v4_proposal_generator.py L630-645 RAISE solo si `document_audience != "internal"`).

**Fix sugerido (R2.3)**: excluir `commercial_gates_report*` del ZIP de cliente, O incluir la sección "Alertas Comerciales" cuando hay BLOCKING (document_audience=internal).

### N17 (MEDIA) — Mapeo servicio→brecha invertido: "SEO Local" muestra "Sin Schema Hotel"

**Evidencia**: propuesta L54 "SEO Local | ... | #1: Sin Schema Hotel ($1,005,768/mes)" porque `BREACH_BY_ASSET["optimization_guide"]` (L1196) apunta a la brecha de Schema, no a `low_seo_score` (BRECHA 3 SEO Local Bajo $1,198,906, rank 4 vivo en opportunity_scores). No es solo costo desactualizado: la asignación semántica servicio→problema es incorrecta (el cliente lee "SEO Local resuelve Sin Schema Hotel"). El fix de N10 debe corregir el mapeo, no solo el número.

**Fix sugerido (R1.2)**: mapear vía `ASSET_TO_PAIN_ID`/`pain_solution_mapper` (ya existe en v4_proposal_generator.py L1185-1191): `optimization_guide → low_seo_score`.

### N18 (BAJA) — "Brecha #5: WhatsApp no coincide" es un hardcode separado (L1250)

**Evidencia**: `BREACH_BY_ASSET["whatsapp_button"]=None` (L1197); la fila de WhatsApp viene de `v4_proposal_generator.py` L1250: `brecha_col = "Brecha #5: WhatsApp no coincide"` — literal con rank stale (#5 vs rank vivo 1 = whatsapp_conflict) y label distinto del diagnóstico ("Conflicto de WhatsApp"). Un fix de N10 que solo parametrice el mapa dejaría esta línea mintiendo.

**Fix sugerido (R1.1/R1.2)**: incluir L1250 en la parametrización desde `opportunity_scores` (whatsapp_conflict, rank 1, costo 1,198,906).

### N19 (BAJA) — Servicio fantasma "Schema Organization" con costo de fuga inexistente

**Evidencia**: propuesta L61 "Servicios adicionales disponibles: Schema Organization" (costo $321,786 del mapa estático L1199); `org_schema` NO fue generado en este run (ausente del directorio de assets de zione: analytics_setup_guide, faq_page, geo_enriched, hotel_schema, indirect_traffic_optimization, llms_txt, monthly_report, og_tags_guide, open_graph, optimization_guide, whatsapp_conflict_guide) y no existe brecha "Sin Schema Org" en el diagnóstico.

**Fix sugerido (R1.2)**: eliminar la fila fantasma o generarla condicionalmente solo si el asset existe.

### N20 (BAJA) — Drift documental en el PROPIO contexto + evidencia N3 no preservada

**Evidencia**: §4 cita "_coverage_gate L1263-1276 → def real L1187"; el def real HOY está en `modules/quality_gates/publication_gates.py` **L1160** (la corrección citada ya driftó −27). Además, los .md del run 1 (123637) fueron sobrescritos/eliminados: el diff de 97 líneas (N3) no es reproducible; solo quedan los JSON 123637 (audit_report_20260804_123620.json, gate_report_20260804_123637.json, commercial_gates_report_diagnostic_20260804_123637.json).

**Fix sugerido (R3.3/R3.4)**: corregir la cita a L1160; preservar evidencia de diff E2E (copiar docs de run1 a temp/ o incluir el diff en el 10-analisis).

### N21 (INFO) — El ZIP contiene artefactos de AMBOS runs del día

**Evidencia**: ZIP incluye audit_report_123620+124429, gate_report_123637+124443, financial_scenarios_123620+124429, commercial_gates_report_diagnostic_123637+124443. El freshness cutoff de 24h (delivery_packager.py L286-304) no distingue runs: la evidencia del run fallido (sin onboarding) viaja junto a la del final — riesgo de confusión para el lector del entregable.

**Fix sugerido (R2.3/R3.x)**: filtrar por run (timestamp de referencia) o separar en subdirectorio.

---

## 2.6 Causas raíz y recomendaciones (RC1-RC3)

### RC1 (N10, N17, N18, N19) — Fuente de verdad de costos aplicada a medias: diagnóstico sí, propuesta no

La unificación D3/FASE-B alineó diagnóstico↔report (`opportunity_scores` ← `_get_brecha_costo`, pesos normalizados suma=100% del escenario más probable = 7,192,000) pero la tabla de servicios de la propuesta quedó con su fuente pre-D3: `BREACH_BY_ASSET` (commit `3c3b9f8`, era FASE-C PROPUESTA-COMERCIAL) + hardcode L1250. Factor uniforme 0.6713 = peso_old/peso_new. El pipeline YA produce la data correcta; el generador de propuesta no la consume.

**Recomendaciones (NO implementadas aún):**
- **R1.1** Parametrizar `BREACH_BY_ASSET` + L1250 desde `opportunity_scores` del run (brecha_id → rank + estimated_monthly_cop), keyed por asset_type vía `ASSET_TO_PAIN_ID`/`pain_solution_mapper`.
- **R1.2** Corregir el mapeo semántico: `optimization_guide → low_seo_score`; whatsapp → `whatsapp_conflict` (rank 1); eliminar fila fantasma `org_schema`.
- **R1.3** Test aislado de consistencia (L1/L11: SOLO archivos que ejerciten v4_proposal_generator) con fixture fijo: "costo por servicio en tabla == opportunity_scores del fixture".
- **R1.4** Check de cierre E2E **OBLIGATORIO** (no opcional — regla D10): costos/numeración de brechas IDÉNTICOS en diagnóstico Y propuesta del mismo run (parseo Python UTF-8, L15).

### RC2 (N11, N15, N16) — Gates comerciales del diagnóstico: inputs no cableados + veredicto oculto pero enviado

(a) CG-CLAIM-VS-EVIDENCE: regex de superficie sin parseo de condicionales (commercial_gate.py L523-530) → falso positivo en texto hipotético "si...no aparece". (b) CG-TIER-CONSISTENCY: inputs None siempre → pasa vacuo (nunca valida). (c) BLOCKING oculto al cliente (solo logging) pero el report viaja en el ZIP de entrega.

**Recomendaciones (NO implementadas aún):**
- **R2.1** CG-CLAIM-VS-EVIDENCE: limitar el regex a oraciones afirmativas (split por oración; ignorar cláusulas con "si..."), o exigir sujeto ("el hotel no aparece" ≠ "no aparece en la respuesta").
- **R2.2** CG-TIER-CONSISTENCY: cablear inputs reales (frontmatter tier + extracción de texto); si None → FALLAR o eliminar el gate, nunca pasar vacuo.
- **R2.3** Política de entrega: excluir `commercial_gates_report*` del ZIP de cliente O incluir la sección "Alertas Comerciales" cuando hay BLOCKING.

### RC3 (N12, N13, N14, N20) — Higiene documental sin verificación automatizada

Prompts con `--release` (L3/L9 violadas en plantillas), conteos a mano (L8 violada en 11-doc), artefactos pre-bump sin anotar, citas de líneas que driftan, evidencia E2E (diff) no preservada. Las reglas ya existen (L3/L8/L9/L15); falla el ENFORCEMENT, no el conocimiento.

**Recomendaciones (NO implementadas aún):**
- **R3.1** Eliminar `--release` de prompts 02-05 + nota "NO usar en fases intermedias"; añadir grep de prompts a `run_all_validations.py`.
- **R3.2** Conteos del 11-doc desde fuente viva (find/pytest/grep) — L8.
- **R3.3** Anotar artefactos pre-bump ("versión del código que corrió: 4.69.0 + fixes") y preservar evidencia de diff E2E.
- **R3.4** Corregir cita `_coverage_gate` → L1160.

### Pendiente CRÍTICO (heredado, sin decisión)

Tests patológicos L1/L11 (`test_proposal_generator.py` ~8GB RAM, `test_price_consistency.py` cuelgue indefinido, `test_proposal_generator_dict.py` 16/38 fallos) siguen sin diagnosticar/excluir. **PREREQUISITO de cualquier fix de RC1** (los tests del área de propuesta son precisamente los patológicos).

---

## 3. Capitalización de Experiencia Previa — Lecciones L1-L15 del 10-analisis aplicadas a los hallazgos

> Enfoque: las lecciones NO se auditan; se **capitalizan** como protocolo operativo. Cada bloque traduce la lección vivida en una regla ejecutable para abordar N10-N14, N15-N21 y los seguimientos S5-S7.

### 3.1 Protocolo para ejecutar el fix de N10/RC1 (costos unificados de la propuesta)

| Lección capitalizada | Regla aplicable al fix de RC1 |
|----------------------|-------------------------------|
| **L1/L11** (tests patológicos: `test_proposal_generator.py` ~8GB RAM, `test_price_consistency.py` cuelgue — la suite completa bloqueó el equipo 2 veces) | NUNCA correr la suite completa de `tests/commercial_documents` ni `tests/financial_engine` en un solo proceso; correr SOLO los archivos de test que ejercitan `v4_proposal_generator.py` (ej. `test_fase_f_financial_placeholders.py`, `test_financial_coherence.py`), en lotes pequeños secuenciales. Si algo se cuelga: `taskkill /F /IM python.exe /T` (el timeout del agente NO mata el proceso). |
| **L4/L5** (forense de baseline: `git stash` está DENEGADO por el sandbox; usar backup `Copy-Item` + `git checkout HEAD -- <archivos>` + restauración obligatoria) | Antes de tocar `v4_proposal_generator.py`, copiar el archivo a `temp/n10_backup/`; probar el test en HEAD; restaurar SIEMPRE al cerrar la sesión y verificar con `git status`. |
| **L7** (evidencia mixta dinámica + estática para declarar "0 regresiones" con tests patológicos aislados) | Si algún test del área de propuesta no puede correr: probar el subconjunto seguro byte-idéntico en HEAD vs fix, y usar `git show HEAD:` + diff de la fase como evidencia estática del área no cubierta. |
| **L8** (conteo de tests nuevos se verifica con `git diff tests/` patrón `^\+.*def test_`, no con notas previas) | Registrar "+N tests" del fix de RC1 contando desde `git diff tests/` con `grep -E '^\+\s*def test_'`, nunca desde estimaciones previas. |
| **L3/L9** (log_phase_completion SIN `--release` en fases intermedias; el flag exige CHANGELOG inexistente) | Al cerrar la fase de RC1: `log_phase_completion.py --fase FASE-X --desc "..." --archivos-mod "..." --tests N --coherence 0.XX --check-manual-docs` **sin** `--release`. El bump/CHANGELOG/`--release` solo en FASE-RELEASE. |
| **L15** (greps con acentos: PowerShell `Select-String` miente, usar Python/ripgrep UTF-8) | Verificar "costo propuesta == costo diagnóstico" parseando `v4_complete_report.json` y el MD de la propuesta con Python (`encoding='utf-8'`), no con regex de consola. |
| **L2** (clasificar el tipo de fallo ANTES de re-ejecutar: test/código vs documental/versionado) | Si `run_all_validations.py --quick` falla durante el fix de RC1, clasificar: Version Sync → `scripts/sync_versions.py`; Document Integration → actualizar README con conteo real; NO re-correr la suite esperando que pase. |

### 3.2 Protocolo para la verificación E2E futura (N11, N12, N15, N16 y cualquier re-ejecución)

| Lección capitalizada | Regla aplicable |
|----------------------|-----------------|
| **L13** (el loader de onboarding busca SOLO en `{--output}/clientes` — main.py L1746 `clientes_dir = Path(args.output)/"clientes"`; con `--output` alternativo cae en "Using defaults") | Para cualquier run E2E con `--output` personalizado: poblar `{output}/clientes` con el YAML (copia) ANTES de lanzar; confirmar en el log "Onboarding data loaded: N campos confirmados" antes de dar el run por válido. Si aparece "Using defaults" → el run NO sirve para verificar D12/Tier B+. |
| **L14** (clasificar la causa del fallo antes de decidir si un retry es legítimo: infraestructura/config ≠ código) | Si un run E2E falla su requisito central, reproducir el fallo en el mínimo scope (llamar la función con inputs reales) y clasificar; solo un fallo de infraestructura habilita el retry, un fallo de código obliga a marcar ⏳ INCOMPLETA. |
| **L15** (verificación de texto con acentos: Python/ripgrep, no Select-String; checks numéricos parseando JSON con Python) | Verificar N11/N15/N16 (gates BLOCKING, tier, ZIP) leyendo los JSON y MD con scripts Python UTF-8. |
| **L12** (integrar tracks delegados directamente cuando tocan los mismos archivos; el criterio es overlap de archivos, no complejidad) | Si el fix de RC1 incluye verificación E2E, el subagente puede correr v4complete en background pero el agente principal verifica la salida — mismo patrón validado en FASE-E. |
| **L6** (pipes de PowerShell sobre pytest cuelgan la captura; redirigir a archivo) | Cualquier pytest en verificación: `pytest ... > temp/x.txt 2>&1` y leer el archivo después; nunca pipear a `Select-String`. |
| **L10** (el usuario puede revertir cambios parciales; verificar `git diff --stat` + `git status --short` antes de continuar tras cualquier intervención) | Si el usuario interviene durante el fix de RC1 (o revierte partes), verificar el estado real del disco antes de seguir editando. |

### 3.3 Reglas transversales de tests y suite (heredadas, vigentes para TODO)

1. **NUNCA** ejecutar la suite completa de directorios con tests patológicos, ni siquiera con timeout (L1, L11 — el proceso no se mata automáticamente).
2. Archivos patológicos conocidos: `test_proposal_generator.py` (fuga ~8GB RAM), `test_price_consistency.py` (cuelgue indefinido), `test_proposal_generator_dict.py` (16 de los 38 fallos preexistentes) — **pendientes de diagnóstico/exclusión** (seguimiento CRÍTICO del plan, no resuelto al 08-04).
3. Forense de regresión: backup `Copy-Item` + `git checkout HEAD --` + restaurar SIEMPRE (L4/L5). `git stash` denegado por sandbox.
4. Conteo de tests nuevos: `git diff tests/ | grep -E '^\+\s*def test_'` (L8).
5. Evidencia mixta dinámica + estática cuando un test no pueda correr (L7).
6. Pipes de PowerShell sobre pytest → redirigir a archivo (L6).

### 3.4 Reglas transversales de log_phase y documentación (heredadas, vigentes)

1. `log_phase_completion.py` SIN `--release` en fases intermedias (L3, L9 — confirmado 2 veces; N13: los prompts 02-05 aún lo traen por corregir).
2. Clasificar el tipo de fallo de validación antes de re-ejecutar: test/código vs documental/versionado (L2).
3. Contar métricas acumulativas desde el diff/fuente viva, no desde notas previas (L8) — N14 es la manifestación de esta lección en el 11-doc.
4. Si el usuario interviene manualmente: `git diff --stat` + `git status --short` primero (L10).

### 3.5 Seguimientos abiertos del plan (S5-S7 + pendientes) con lección asociada

| Seguimiento | Estado (08-04) | Lección que lo gobierna |
|-------------|----------------|--------------------------|
| S5: label `"occupancy": "regional"` residual en `breakdown.data_sources` de financial_scenarios.json | Detectado en FASE-E, CONFIRMADO en vivo por esta validación (D12) | Verificar con Python parseando el JSON (L15); fix candidato release posterior |
| S6: execution_trace lista `pagespeed_api` en executed Y skipped (N9 residual) | Detectado en FASE-E, aceptado | Mejora de dedup; texto del doc ya coherente (D6) |
| S7: loader de onboarding sin fallback a `output/clientes` con `--output` alternativo (L13) | Detectado en FASE-E, workaround documentado | Fix de código candidato; la lección L13 ya es regla operativa (§3.2) |
| Tests patológicos L1 (3 archivos) | **CRÍTICO — pendiente** (causó bloqueo real en FASE-C-B) | L1/L11; NUNCA suite completa mientras siga abierto; PREREQUISITO del fix RC1 |
| Gate N2 en modo WARNING | ✅ Implementado (FASE-C-A) | Upgrade a BLOCKING en release posterior tras catalogar contradicciones conocidas |
| Prompts 02-05 con `--release` (N13) | Pendiente de corrección | L3/L9; corregir plantillas o añadir nota "NO usar en fases intermedias" (R3.1) |
| Gate CG-TIER-CONSISTENCY no-op (N15) | NUEVO (re-validación 08-04) | R2.2: cablear inputs o fallar; nunca pasar vacuo |
| ZIP con evidence BLOCKING + artefactos de 2 runs (N16/N21) | NUEVO (re-validación 08-04) | R2.3: política de entrega del ZIP |
| Mapeo servicio→brecha + hardcodes (N17/N18/N19) | NUEVO (re-validación 08-04) | RC1: parametrizar desde opportunity_scores (R1.1-R1.4) |
| Citas de líneas del propio contexto (N20) | NUEVO (re-validación 08-04) | R3.3/R3.4: _coverage_gate → L1160; preservar evidencia E2E |

---

## 4. Coherencia entre documentos del plan (verificada ✅)

| Par | Resultado |
|-----|-----------|
| README ↔ dependencias-fases ↔ 09-checklist ↔ 10-analisis: 7 fases, hallazgos 21, modo de ejecución por fase | ✅ Coherentes (README: "21 desconexiones (D1-D12 + N1-N9)"; FASE-D "D9-D12+N3-N8 parcial" consistente en los 4 docs) |
| 10-analisis matriz ↔ 09-checklist cobertura: 21/21 con severidades y fases | ✅ Coherentes (N8 en FASE-B pre-resuelto, N3 verificación E, N9 C-B/E — consistente en ambos) |
| 11-doc secciones A/B/E (módulos/features/archivos) ↔ código: doc_audit_consistency gate, pillar_maturity_curve, TARGET_GBP_PHOTOS, _occupancy_source, freshness cutoff | ✅ Coherentes (todos verificados en código, ver matriz §1) |
| 11-doc métricas tests ↔ live: 3,215 collected; suites quality_gates 303 ✅ / delivery 59 ✅ | ✅ Coherentes |
| dependencias-fases diagrama ↔ ejecución real (A→B→C-A→C-B→D→E→RELEASE) | ✅ Coherentes |
| FASE-E prerrequisito T0 (url en onboarding YAML) ↔ evidencia: onboarding cargado (run 2) | ✅ Coherente (workaround L13: copia a `{output}/clientes`; `clientes_dir = Path(args.output)/"clientes"` en main.py L1746 confirmado) |
| git status: 3 cambios sin commitear (CONTEXT-DELIVERY movido a Historico, REGISTRY.md borrado) | ⚠️ Higiene: pendiente commit de la reorganización Historico |

**Pitfalls de la skill aplicados y confirmados**: Pitfall 15 (line drift en citas: N6 L2555→L2558, _coverage_gate L1263-1276→def real **L1160** — la corrección citada en versiones previas de este contexto (L1187) también driftó, ver N20), Pitfall 6 (hardcoded strings en campos dinámicos → N10/N17/N18), Pitfall 12 (gates que validan inputs no el artefacto → N11 CG-CLAIM-VS-EVIDENCE matiz + N15 CG-TIER-CONSISTENCY no-op), Pitfall 13 (byte-diff entre runs → N3 verificado con 97 líneas, evidencia no preservada — N20), Pitfall 14 (auditar TODO el ZIP → 76 entries verificadas + N16/N21), Pitfall 16 (nuevo, cross-document verification gap → N10: matriz verificó report↔doc pero no doc↔doc).

---

## 5. Próximos pasos (con causas raíz y lecciones capitalizadas integradas)

1. **Decisión sobre RC1 (ALTA — N10+N17+N18+N19)**: parametrizar la tabla de servicios de la propuesta desde `opportunity_scores` del run (R1.1: reemplazar `BREACH_BY_ASSET` L1193-1206 + hardcode L1250; R1.2: corregir mapeo servicio→brecha vía ASSET_TO_PAIN_ID; R1.3: tests aislados L1/L11; R1.4: check de cierre OBLIGATORIO). Implica: fix + una sola re-ejecución E2E con workaround L13 + verificar propuesta↔diagnóstico. FASE dedicada o release posterior (v4.70.1).
2. **Decisión sobre RC2 (MEDIA — N11+N15+N16)**: (R2.1) afinar CG-CLAIM-VS-EVIDENCE para ignorar condicionales "si..."; (R2.2) cablear CG-TIER-CONSISTENCY o eliminarlo (no-op actual); (R2.3) política de entrega del ZIP (excluir reports internos o incluir alertas). Verificación con Python/JSON (L15).
3. **Acción inmediata (heredada del plan, sin decisión)**: tests patológicos L1/L11 — diagnosticar/excluir los 3 archivos antes de cualquier suite futura. **PREREQUISITO del fix RC1** (los tests del área de propuesta son los patológicos).
4. **Limpieza documental (baja prioridad)**: R3.1 (prompts 02-05 sin `--release`, regla L3/L9), R3.2 (conteos 11-doc desde fuente viva, regla L8), R3.3 (nota versión 4.69.0 en artefactos E2E + preservar evidencia de diff), R3.4 (cita `_coverage_gate` → L1160), git commit de la reorganización Historico.

---

## 6. Prompt sugerido para la próxima sesión (enriquecido con causas raíz y lecciones capitalizadas)

```
Valida contra código vivo y diseña el fix de RC1 (contexto .opencode/context/CONTEXT-VALIDACION-COHERENCIA-PLAN-ENTREGA-2026-08-04.md):
BREACH_BY_ASSET en modules/commercial_documents/v4_proposal_generator.py L1193-1206 + hardcode L1250 ("Brecha #5: WhatsApp no coincide")
muestran costos, ranks y labels de brechas que NO coinciden con el diagnóstico del mismo run, y el mapeo servicio→brecha está
INVERTIDO (SEO Local → "Sin Schema Hotel"; optimization_guide debe apuntar a low_seo_score — N17). Alcance confirmado por N18
(hardcode separado L1250) y N19 (servicio fantasma org_schema).
Objetivo: la tabla de servicios de la propuesta debe citar el MISMO costo, rank y label que el diagnóstico (opportunity_scores
del v4_complete_report.json), keyed por asset_type vía ASSET_TO_PAIN_ID/pain_solution_mapper.

PROTOCOLO OBLIGATORIO (lecciones capitalizadas del 10-analisis-post-implementacion.md):
- 1 fase = 1 sesión (R1); log_phase_completion SIN --release en fase intermedia (L3/L9)
- NUNCA correr la suite completa de commercial_documents/financial_engine (L1/L11 — tests patológicos
  test_proposal_generator.py/test_price_consistency.py/test_proposal_generator_dict.py siguen pendientes);
  correr SOLO archivos de test que ejercitan v4_proposal_generator.py, secuenciales; si cuelga: taskkill /F /IM python.exe /T
- Forense de regresión: backup Copy-Item a temp/ + git checkout HEAD -- <archivos> + restaurar SIEMPRE (L4/L5; git stash DENEGADO)
- Conteo de tests nuevos desde git diff tests/ (L8); evidencia mixta dinámica+estática si un test no corre (L7)
- Verificación E2E (1 sola ejecución v4complete): poblar {output}/clientes con el YAML ANTES del run (L13);
  confirmar "Onboarding data loaded" en el log; clasificar fallos antes de decidir retry (L14)
- Verificación de texto con acentos/costos: scripts Python UTF-8 o ripgrep, nunca Select-String inline (L15)
- Si el usuario interviene: git diff --stat + git status --short antes de continuar (L10)
- Check de cierre OBLIGATORIO (gate de no-regresión, no opcional — D10): costos/numeración de brechas IDÉNTICOS
  en diagnóstico Y propuesta del mismo run
- Post-fix documental: R3.1 (--release en prompts 02-05), R3.2 (conteos desde fuente viva), R3.3 (anotación de
  artefactos pre-bump + preservar evidencia de diff E2E), R3.4 (cita _coverage_gate → L1160)
```
