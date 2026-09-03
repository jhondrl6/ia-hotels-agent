# CONTEXT: Dossier de estabilización pre-tribunal — SalenteReal (2026-09-03)

> **Eje 1 (brechas↔módulos):** auditoría original §0-§7.
> **Eje 2 (servicios↔assets):** severidad de gates (§8) y causa raíz del punto 8 (§9), migrados desde `CONTEXT-BOTS-POTENCIALIZACION-IAH-CLI-2026-09-01.md` el 2026-09-03 (mapa en §10).
> **Aporte durable autodeclarado (v2.18.0):** este CONTEXT introduce un inventario verificado de 8 caídas
> silenciosas entre la producción de los módulos de auditoría y el diagnóstico comercial, la confirmación
> en código de que `coverage_no_silent_drop` es una tautología extremo a extremo (ledger y documento salen
> de la MISMA llamada `detect_pains`), la detección muerta de `missing_llmstxt`, el guard `hasattr(__iter__)`
> que bloquea `low_ota_divergence` para valores numéricos, la línea de tiempo completa del tema PageSpeed
> (Zione D6 → SR-F → fix OPS 2026-08-31) con el delta que sigue abierto, y —desde la reestructuración del
> 2026-09-03— la corrección medida de la severidad de gates (advisory = 2, no 3; H10), los seis agujeros
> vivos A1-A6, el mecanismo causal B1-B5 del `no_breach = 6/7` (insumo del punto 8), la tabla consolidada
> de mediciones y los falsos positivos corregidos con su lección de forma. No contiene secretos.

---

## 0. Objetivo, alcance y reestructuración (2026-09-03)

Pregunta del usuario (2026-09-03): las brechas del diagnóstico
`output/FASE-D_salentoreal_post_guard/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260831_122803.md`
¿corresponden a la producción de los módulos, o hay producción de módulos que se queda por fuera del diagnóstico?

Método: contraste doc ↔ artefactos de `hotelsalentoreal/v4_audit/` (corrida 2026-08-31 12:28) ↔ código.
El doc auditado es idéntico byte a byte al `DIAGNOSTICO.md` del ZIP entregado (`deliveries/hotelsalentoreal_20260831/`).
Cero archivos de código modificados (sigue vigente: la reestructuración documental del 2026-09-03 tampoco tocó código).
Originalmente extendía el eje servicios↔assets de `CONTEXT-BOTS-POTENCIALIZACION-IAH-CLI-2026-09-01.md` §13 al eje brechas↔módulos.

**Reestructuración del 2026-09-03 (aprobada por el usuario):** este documento absorbió **§12.1-12.6 y §13** de
CONTEXT-BOTS y es ahora el **dossier de estabilización pre-tribunal**. CONTEXT-BOTS quedó exclusivo de bots
(tribunal §5, capas §2, análisis Capa 4 §3). Criterio de corte aplicado: *"¿lo arreglaríamos aunque nunca
construyamos los bots?"* — todo lo que corrige integridad del pipeline/diagnóstico vive aquí; lo que solo
tiene sentido con bots existentes quedó allá. Mapa completo de migración en §10.

**Una causa raíz, tres manifestaciones** (por qué los dos ejes son un solo dossier):
1. **Upstream** — los módulos producen hallazgos que `detect_pains` nunca convierte en pains (§4, ocho caídas silenciosas).
2. **Medio** — el doc refleja el ledger por construcción (§5) y la propuesta estática vende pains que no se detectaron (§9.2, `no_breach = 6/7`).
3. **Downstream** — los gates que podrían verlo son ciegos (§5; §9.1-A1), y la severidad que los docs prometen está mal declarada en 4 regímenes contradictorios (§8).

El orden acordado: **este dossier primero (estabilización), el plan de bots después** — que es exactamente la
secuencia que ROADMAP v4.2 §7.2 ya registró (precondiciones T0.1-T0.4 antes de T1; "causa raíz por debajo de T0").

## 1. Validación previa contra lecciones QMIND (notebook `iah-cli-lecciones`)

Fuentes recuperadas (Paso 0 del ciclo de capitalización):

| Fuente (QMind) | Lección relevante |
|---|---|
| `CONTEXT-H: Diagnóstico coherencia módulo entrega (2026-08-02)` (sourceId `01a04d9b-c7db-7cde-a940-830dec18a59f`) | **D6 (ALTA)**: "Falsa explicación Core Web Vitals" — el doc decía "el sitio puede ser nuevo o tener tráfico bajo" (hardcode `v4_diagnostic_generator.py:1741` de entonces) enmascarando la causa real: API key de PageSpeed inválida. Diseño acordado: `status == "ERROR" → "API de PageSpeed no disponible (verificar clave)"`. Misma fuente: D2 (doble invocación de `detect_pains`), D5 (gate de cobertura con covered=0). |
| `CONTEXT: Salento Real v4complete ejecución (2026-08-27)` (sourceId `01a04d9a-e267-7ae7-b486-0ea19addf5f3`) | Hallazgo 6: mismo `Status: ERROR — API key not valid` en corrida del 27-08; no bloquea, degrada evidencia. |
| `10-analisis: SR-PIPELINE-FIXES-2026-08-27` (sourceId `01a04d99-e68b-778a-a86b-40ff5f41ec8a`) | PageSpeed API key inválida → **✅ VERIFICADO (SR-F, 2026-08-28) → ACCIÓN USUARIO (OPS)**. Causa: `.env` resolvía `GOOGLE_PAGESPEED_API_KEY` (presente PERO inválida o sin PSI habilitada). Fallback chain `PAGESPEED_API_KEY → GOOGLE_PAGESPEED_API_KEY → GOOGLE_API_KEY`. También registra: `critical_recall` colapsaba lista vacía con dato ausente (resuelto SR-H2, L-SR5 — familia "vacío vs ausente"). |
| `VALIDADOR-URL-PROPIA 10-analisis-post-implementacion` (sourceId `01a0590c-6979-70ce-94dc-c6987f36f188`) | **GOOGLE_PAGESPEED_API_KEY inválida → RESUELTO 2026-08-31**: la variable era un placeholder de 3 caracteres. Fix OPS: `PAGESPEED_API_KEY` (canónica de `.env.template`) sembrada con la key de Maps del mismo proyecto; verificado empíricamente `PageSpeedClient` → status VERIFIED con datos CrUX (perf 55, LCP 3.03s). |

**Verificación local de la línea de tiempo (evidencia en repo):**
- Fix de presentación D6: commit `e544a59` (2026-08-03 18:49) `feat(FASE-C-B): D6+D7+D8 — textos dinámicos`.
  Es el código vigente en `v4_diagnostic_generator.py:1945-1952` (lee `performance.status/message` reales).
- Cadena de fallback vigente: `modules/data_validation/external_apis/pagespeed_client.py:25`.
- Release v4.74.0 (donde se cerró el fix OPS): commits `f914e0e`/`f77f8ae` del **2026-08-31 15:08**.
- `.env` actual contiene `PAGESPEED_API_KEY` y `GOOGLE_PAGESPEED_API_KEY` (nombres verificados; valores no leídos).
- **La corrida auditada es 2026-08-31 12:28 — anterior al cierre del fix OPS (~15:08).** Por eso el doc todavía
  muestra el error de la key: la corrección de credenciales llegó después de la corrida, no falta por hacer.
- No existe corrida `v4_complete` posterior persistida en `output/` con `performance.status: "VERIFIED"`
  (grep sobre `output/*/*/v4_audit/audit_report_*.json` → 0 resultados). La verificación del 31-08 fue del
  cliente aislado (`PageSpeedClient`), no de un pipeline completo persistido.

**Re-encuadre del hallazgo 1 de la auditoría (antes: "caída silenciosa sin abordaje previo"):**
el tema PageSpeed tiene 3 ciclos previos. Lo ya resuelto: causa raíz OPS (31-08), lectura dinámica de
status/message (e544a59), y el principio "no colapsar ERROR con ausencia" (familia D6/L-SR5). Lo que sigue
abierto y NO fue abordado por ningún ciclo previo: (a) la capa de pain sigue descartando el ERROR sin pain
ni justificación (`poor_performance` exige `mobile_score is not None`, `pain_solution_mapper.py:416-417`);
(b) el doc inserta el string crudo en inglés del API ("Invalid URL or request: API key not valid...") en vez
del mensaje sanitizado que CONTEXT-H especificó ("API de PageSpeed no disponible (verificar clave)");
(c) esa fila vive en una tabla sin header ni separador (no renderiza como tabla); (d) `execution_trace` lista
`pagespeed_api` en `executed` Y en `skipped` simultáneamente; (e) el placeholder inválido de 3 caracteres
sigue en `.env` como trampa latente: si se elimina `PAGESPEED_API_KEY`, el fallback vuelve a resolver la
inválida y el síntoma reaparece.

## 2. Respuesta a las dos preguntas

1. **¿Las 3 brechas corresponden a la producción de los módulos?** Sí en origen, con premisas frágiles (§3).
2. **¿Hay producción de módulos que se queda fuera?** Sí: al menos 8 hallazgos sin brecha ni justificación (§4),
   y ningún gate puede verlo (§5).

## 3. Las 3 brechas publicadas

| # | Brecha | Fuente | Problema de premisa |
|---|---|---|---|
| 1 | Sin Analytics Configurado | `pain_solution_mapper.py:677-691` vía `use_ga4=False`; `main.py:2424` define el flag como "True only if GA4 credentials exist" | No mide el sitio del hotel: es nuestra credencial ausente. El detalle filtra el flag CLI `--ga4-property-id` al cliente |
| 2 | Baja Visibilidad de Tráfico Orgánico | `pain_solution_mapper.py:693-701` | No es medición independiente: compañera hardcoded de la 1, confidence 0.8 fija |
| 3 | Crawlers de IA Bloqueados | `ai_crawler_auditor.py` | Score 0.50 exacto ⇒ los 14 crawlers marcados bloqueados (`:234-243`: bloqueado = 0.5×conf; conf=1.0 si robots existe). El parser (`:148-196`) retorna False al primer `Disallow:` no vacío del bloque que matchee (incluida regla `*`), ignora `Allow:` y no implementa longest-match; un robots WordPress típico (`Disallow: /wp-admin/`) marcaría los 14, incluidos Googlebot/Bingbot — incoherente con sitio indexado (SEO 60, 986 reseñas). Además mezcla buscadores (Bingbot/Baiduspider) en un pain de "IA" |

Consecuencia comercial: **57% del dinero ($2.31M/mes de $4.04M) deriva de UN hecho** (credencial GA4 propia
ausente) presentado como 2 brechas con costos idénticos (28%+28%+42% mostrados = 98% por truncamiento int,
`v4_diagnostic_generator.py:2689`).

## 4. Ocho caídas silenciosas (ni brecha ni justificación)

1. **PageSpeed ERROR** — re-enmarcado por QMind (§1): presentación y causa raíz ya abordadas en 3 ciclos;
   quedan abiertos (a)-(e) de §1. En la corrida auditada el error era esperable (12:28 < 15:08).
2. **GEO crítico 29/100** — `geo_flow_result.json`: band "critical", 10 assets generados, sync "CRISIS TÉCNICA".
   Sin pain; solo fila de anexo (`v4_diagnostic_generator.py:2153-2166`). Tres números GEO conviven
   (79 Places / 85 checklist ✅ / 29 crítico) y el desglose marca ✅ `fotos_gbp` contra otra fila
   "Fotos GBP Insuficientes".
3. **Visibilidad LLM = 0** — `llm_report` mention_rate 0.0, SoV 0.0 (3 queries); `aeo_snippets` 0/5
   (`source: "stub"`). No existe pain_id de visibilidad LLM/snippets en el mapa de 24. El doc afirma
   "Visibilidad en IA: Alta" y "Recomendaciones de IA ✅ Superior" — contradicción directa no cubierta
   por `hard_contradictions`.
4. **`missing_llmstxt` detección muerta** — existe en el mapa (`pain_solution_mapper.py:160-168`), el asset
   se implementa y se generó, pero ninguna rama de `detect_pains` lo emite. El sitio no tiene llms.txt
   (`ia_readiness.components.llms_txt = 0`).
5. **2 schema warnings** (image, priceRange) — solo recommendation (`v4_comprehensive.py:1828-1829`).
6. **Fotos GBP 10/40** — solo fila en la tabla rota (`v4_diagnostic_generator.py:1942-1943`).
7. **`title=""`/`description=""` vacíos** — el validador solo detecta defaults; vacío ⇒ `has_issues=false`,
   sin pain (`pain_solution_mapper.py:469-484`).
8. **`low_ota_divergence` estructuralmente muerto** — guard `hasattr(direct_field.value,'__iter__')`
   (`pain_solution_mapper.py:453`) excluye float/int; el pipeline conoce `direct_channel_percentage=0.2`
   ("default"). Pain HIGH, priority 1, imposible de disparar para valores escalares.

Por umbral (visibles, discutibles): `low_citability` <50 (hay 57.42 con recomendación de 20 bloques),
`low_ia_readiness` <50 (73.8), `low_gbp_score` <70 (79; photos_score 5/15), `low_seo_score` <40 (60).

## 5. Los gates no pueden verlo

- **`coverage_no_silent_drop` tautología extremo a extremo (confirmado en código):** el gate cuenta
  `total = len(pain_ledger_resolved)` (`publication_gates.py:1288-1373`); ledger y brechas del doc salen de
  LA MISMA llamada `detect_pains` (`v4_asset_orchestrator.py:280`; `v4_diagnostic_generator.py:3178`, DEP-03).
  La brecha que no entra al ledger es invisible por construcción. Histórico conexo: D2 (Zione, doble
  invocación con inputs distintos) fue corregido unificando la llamada — la unificación creó la tautología.
  **Familia de tautologías:** esta es la del eje brechas↔módulos. Existe una segunda del mismo patrón en el
  eje servicios↔assets — `coverage_ratio` de alignment vale 1.000 algebraicamente cuando `unresolved == 0`
  porque numerador y denominador se mueven juntos (§8.3; mecanismo completo en §9.2-B4).
- **`doc_audit_consistency` corrió vacío:** único gate doc-vs-audit; llegó sin `audit_data`/`diagnostico_text`
  (`publication_gates.py:1494-1514`) → PASSED con `value=null` pese a que `audit_report_20260831_122757.json`
  existía en disco. Aún con datos, Check 2 espera `gbp.reviews` como dict `{"total":...}` y el audit trae int.
- **`critical_recall = 1.0` vacuo:** `recall_basis "audit_present_no_critical_issues"`; `_identify_critical_issues`
  (`v4_comprehensive.py:1789-1814`) solo consulta schema/whatsapp/geo_score<50/perf con field_data.
  Nota: el colapso vacío→1.0 ya fue materia de SR-H2 (L-SR5) con traza obligatoria — la traza funciona;
  lo que no se resolvió es que `_identify_critical_issues` no clasifica ERROR de PageSpeed ni banda GEO
  critical como críticos.
- **`hard_contradictions = 0`:** el eje doc-vs-audit (LLM "Alta" vs 0 menciones, fotos ✅ vs insuficientes)
  está fuera del alcance del motor.

## 6. Contradicciones entre módulos del mismo run

- `geo_enriched/sync_report.md`: "S1: No Hotel schema detected" y "C2: No statistics (rating/reviews)
  available" contra un audit con schema verified y 986 reseñas/4.5; aun así declara "✅ consistente — Crisis
  técnica confirma pérdida" con "Pérdida mensual: No especificada". `robots_fix.txt` lleva fecha 2026-03-30
  (stale) en un run del 31-08.
- Gate alignment autocontradictorio: `alignment_percentage: 0.333` + `missing_count: 2` en details vs mensaje
  "Alignment 100%: 0 services still missing"; `no_breach: 3` en el gate vs 6 NO_BREACH en
  `proposal_asset_matrix.json`.
- `financial_scenarios.pricing.is_compliant: false` vs gate `pricing_compliance` PASSED (WARNING); tres
  doctrinas de ratio (9.9x coherence / 0.2041 gate / 3x-6x AGENTS.md).
- coherence `is_coherent=false` (assets_are_justified 3/4) vs gate PASSED 0.88 y frontmatter del doc
  (mecanismo completo: §9.2, B5/N11 — el gate decide con el score y nunca consulta `is_coherent`).

## 7. Pendientes de verificación

1. **robots.txt real** de hotelsalentoreal.com (solo lectura) para confirmar/refutar el falso positivo de la
   brecha 3 — el fetch externo fue denegado en la sesión de auditoría.
2. **Corrida v4_complete post-fix** que persista `performance.status: "VERIFIED"` y CWV reales en
   `v4_audit/audit_report_*.json`, para cerrar el ciclo PageSpeed a nivel pipeline (no solo cliente aislado).

Ambos pendientes son candidatos naturales a línea base / criterio de salida del plan de estabilización.

## 8. Corrección medida — la lista advisory es de 2, no de 3 (auditado 2026-09-02)

> **Estado:** decisión tomada, **no implementada**. Ningún archivo de código fue modificado durante la auditoría. Esta sección es autocontenida: una sesión nueva puede ejecutarla sin leer la conversación que la produjo.
> **Migrada desde CONTEXT-BOTS §12.1-12.6 el 2026-09-03** (reestructuración: correcciones de pipeline al dossier de estabilización; decisión registrada también como deuda H10 en ROADMAP v4.2).

### 8.1 El hecho a corregir

El repo dice cosas incompatibles sobre la severidad de sus 13 publication gates:

| Lugar | Qué afirma | Realidad |
|---|---|---|
| `AGENTS.md` (tabla "Módulos Activos", fila `quality_gates/`) | 10 blocking + **3 advisory** (`content_quality`, `asset_confidence`, `proposal_asset_alignment`) | Falso en el código |
| `publication_gates.py:4` (docstring de módulo) | "13 publication gates (10 blocking + 3 advisory)" | Falso |
| `publication_gates.py:162` (docstring de clase) | "manages 10 blocking gates and 3 advisory gates" | Falso |
| `publication_gates.py:1967-1968` `check_publication_readiness` | — | `blocking_gates = [r for r in results if not r.passed]` / `ready = len(blocking_gates) == 0` → **los 13 bloquean**; el concepto advisory no existe |
| `publication_gates.py:239-249` `get_blocking_gates` | — | `return [r for r in results if not r.passed]` — idéntico, vestigial |
| `delivery_quality_report.py:289` | `BLOCKING_GATE_NAMES = ("coherence", "coverage", "evidence", "proposal_asset_alignment")` | **Tercer régimen**: aquí `proposal_asset_alignment` SÍ es bloqueante explícito |

Resultado: **cuatro regímenes contradictorios** para la misma severidad. El único lugar del repo donde la distinción blocking/advisory está realmente implementada es `commercial_gate.py:99-113` (`BLOCKING_GATE_IDS` de 6 + `WARNING_GATE_IDS` de 4) — **ese es el patrón a copiar**.

### 8.2 Evidencia medida — por qué `asset_confidence` no puede ser advisory

Corpus completo de corridas históricas en `output/`: **29 corridas únicas, 10 hoteles**.

**4 de 29 (14%) tienen 100% de assets ESTIMATED** — exactamente el caso que `asset_confidence` bloquea en `publication_gates.py:802-820`:

| Hotel | Fecha | ESTIMATED / total | `coherence_score_final` |
|---|---|---|---|
| `hotel_visperas` | 2026-04-05 | 9/9 | `None` |
| `hotelvisperas` | 2026-04-04 | 9/9 | `None` |
| `hotel_vísperas` | 2026-03-26 | 6/6 | `None` |
| `hotelvisperas` | 2026-03-25 | 6/6 | `None` |

Las cuatro comparten `coherence_score_final = None`: no hay score canónico que las rescate. Si `asset_confidence` fuera advisory, **el 14% del histórico saldría a entrega sin un solo dato real** — el escenario exacto que la cláusula P6.5 y el primer piso del Juez (diseño: CONTEXT-BOTS §5, regla determinista) existen para impedir.

Distribución de `ESTIMATED/total` en las 29 corridas: 0.00→1, 0.50→4, 0.54→3, 0.55→4, 0.56→2, 0.62→3, 0.67→1, 0.75→1, 0.77→1, 0.80→1, 0.86→1, 0.88→1, 0.90→2, **1.00→4**.

El bloque duro de `asset_confidence` (`all_estimated` → `GateStatus.BLOCKED`, mensaje *"Delivery bloqueado hasta onboarding o datos reales"*) es hoy **el único mecanismo** que convierte un paquete Tier C en no-entregable. No hay sustituto.

### 8.3 Decisión

- Lista advisory = **2 miembros**: `content_quality` y `proposal_asset_alignment`.
- `asset_confidence` **conserva su bloqueo**.
- La documentación correcta es **"11 blocking + 2 advisory"**. Hay que corregir `AGENTS.md` y `publication_gates.py:4,162` hacia esta decisión — **no al revés**: el código no debe relajarse para coincidir con un docstring que nunca fue implementado.

Fundamento de que `proposal_asset_alignment` sí puede ser advisory: su bloqueo actual es redundante. `alignment_result.py:105-108` define `passed = (unresolved == 0)` y `alignment_result.py:268-269` define `actionable = max(total - no_breach, 0)` / `coverage = (generated + present) / actionable if actionable > 0 else 1.0`.

**La tautología es demostrable algebraicamente, no solo medible.** La misma llamada `_presence_resolved` que resuelve una entrada NO_BREACH la saca de `no_breach` (L259-263, encoge el denominador) y la mete en `present` (L251-255, agranda el numerador). Si `unresolved == 0`, las entradas se particionan en `generated + present + no_breach == total` ⟹ `generated + present == total - no_breach == actionable` ⟹ **`coverage == 1.0` siempre que `passed == True`**. Numerador y denominador se mueven juntos por construcción.

Por eso el umbral `< 0.8` de `publication_gates.py:1156` no añade protección *independiente* sobre `unresolved`. Ojo con la lectura: es **redundante, no muerto** — sí disparó BLOCKED en 2 de las 4 configuraciones históricas y 3 tests lo ejercitan. Medido en **10 configuraciones** (5 variantes de registro × 2 oráculos de presencia): `coverage_ratio = 1.000` en las 10 y `unresolved = 0` en las 10, con ambos oráculos. Demoterlo no pierde cobertura y **gana** coherencia con lo que los docs ya prometen. Ver §9.2 para el mecanismo completo.

### 8.4 Tareas para la sesión que culmina el tema

1. **Implementar la distinción** en `publication_gates.py`: estructura explícita (`ADVISORY_GATE_NAMES` / `BLOCKING_GATE_NAMES`) copiando `commercial_gate.py:99-113`, y consumirla en `check_publication_readiness:1967-1968` y en `get_blocking_gates:239-249`. Los advisory fallidos deben reportarse con estado WARNING pero no impedir `ready = True`. Dos requisitos inseparables de esa tarea:
   - **Piso explícito (riesgo B).** Advisory sin umbral mínimo deja pasar en silencio coberturas de 0.125 (medido, ver §9.2). Definir un piso bajo el cual el advisory degrada a blocking, o justificar por escrito por qué no hace falta.
   - **Divulgación con consumidor nombrado (riesgo C).** El WARNING debe aterrizar en `human_checklist_generator.py` (≤10 items) y en el `acta_revision.md` del Bot 5 (diseño: CONTEXT-BOTS §5; el acta aún no existe — consumidor mínimo hoy: `human_checklist_generator.py`). Un advisory que no entra en un artefacto que el humano lee es indistinguible de un advisory que no existe.
2. **Corregir `AGENTS.md`** (tabla Módulos Activos, fila `quality_gates/`, y el bloque FASE 4.5 del flujo v4) **y `publication_gates.py:4` y `:162`** a "11 blocking + 2 advisory".
3. **NO tocar `delivery_quality_report.py:289`** (`BLOCKING_GATE_NAMES`). Ese tuple rige el ZIP (`main.py:3198` "⛔ ZIP ABORTED") y pertenece a un régimen distinto — delivery, no publicación. Unificarlos es una decisión separada con su propio radio de impacto.
4. **Añadir candado de regresión**: hoy **0 tests** referencian `BLOCKING_GATE_NAMES` y ningún test de `tests/regression/` ni `tests/e2e/` fija la lista advisory. Sin candado, el cuarto régimen reaparece.
5. **Cerrar el ciclo en el plan de registro, no en el dossier.** Una vez implementado, actualizar **ROADMAP §6.4** (la columna "Objetivo decidido" de la tabla de severidad pasa a "Implementado") y dar de baja la deuda **H10**. La redacción original de este ítem —"actualizar §8 y §10 de este documento"— quedó **sin objeto** desde el 2026-09-02: el §10 de CONTEXT-BOTS es un stub supersedido (su §10.2 lista lo refutado) y su §8 es estado histórico del proyecto cuya fuente única es `VERSION.yaml` + `python scripts/doctor.py --status` (ROADMAP §3: no replicar datos sincronizables).

### 8.5 Qué NO hacer

- **No demoter `asset_confidence`** — ver §8.2 (14% del histórico).
- **No implementar S2.3** (cambiar el denominador de `coverage_ratio` de `actionable_total` a `promised_services_total`). Es **revertir la decisión D-PF1** de FASE-SR-B (`alignment_result.py:115-123`, *"los servicios 'sin costo (fallback)' no comprometidos no cuentan como deuda de entrega"*). Efecto medido: convierte un 0.571 BLOCKED en 1.000 WARNING. Bloquearía **3 de las 4 configuraciones históricas de alignment (75%)**. En 3 de esas 4, `no_breach = None` ⟹ históricamente `coverage == coverage/total`: S2.3 no corrige nada real, penaliza una deuda que D-PF1 decidió explícitamente no contar.
- **No añadir todavía el octavo servicio al registro.** `PROPOSAL_SERVICE_TO_ASSET` tiene 7 entradas (`monthly_report` comentado en `proposal_asset_alignment.py:27-29`, FASE-3 BUG-10), mientras `service_catalog` declara 8 y el comentario de L35-37 dice "All 8". Medido: **Δcoherence = +0.0000 exacto** (la rama de éxito hardcodea `score=1.0` en `coherence_validator.py:689-700` y solo pone el tamaño del registro en el mensaje; la rama de fallo usa una **UNIÓN** en L703 donde `monthly_report` ya está en `promised_types`), pero **`promise_coverage` cae 0.571 → 0.500** porque el pain `no_monthly_report` no se detecta. Neutro en coherencia, negativo en coverage: no vale la pena sin el punto 8.
- **No tratar el punto 8 como opcional.** La causa raíz es que la propuesta es **estática**: promete los 7-8 servicios del registro haya o no brecha detectada. Una **propuesta dinámica que solo prometa servicios con brecha detectada** hace `no_breach = 0` por construcción ⟹ `total == actionable` ⟹ los denominadores convergen y toda la discusión anterior se disuelve. Advisory es un parche legítimo; el punto 8 es la cura.
- Datos de sensibilidad útiles si se toca coherencia: pesos en `coherence_validator.py:101-108` (1.5/1.0/1.5/0.5/1.0/2.0, total 7.5) ⟹ sensibilidad 0.2667 por unidad; headroom actual 0.08; score mínimo de un check para mantener overall ≥ 0.8 = **0.7000** (M=3 de 10 faltantes).

### 8.6 Criterio de aceptación

- **Baseline antes de tocar nada:** 140 passed, 1 skipped, 8 warnings en ~1.23s sobre los 7 archivos de tests de alignment/gates (141 tests, 32 asserts de bloqueo).
- **Costo esperado:** ~6 tests específicos de alignment a actualizar. No hay candados en `tests/regression/` ni `tests/e2e/`.
- **Verificación:**
  ```bash
  python -m pytest tests/quality_gates tests/asset_generation -q
  python scripts/run_all_validations.py --quick
  python scripts/validate_agents_md.py    # gate de coherencia AGENTS.md (conteo de gates)
  ```
- **Definición de hecho:** un gate advisory fallido produce WARNING visible en el acta y `ready` sigue siendo `True`; un gate blocking fallido produce `ready = False`; `AGENTS.md`, `publication_gates.py:4`, `:162` y el código dicen los mismos 11 + 2; existe al menos un test que fija ambas listas.

## 9. Hallazgos estructurales del eje servicios↔assets (auditados 2026-09-02)

> **Propósito:** preservar medición verificada para evitar reproceso. Nada de esto está implementado y ningún archivo de código fue modificado durante la auditoría. §8 resuelve la severidad de los gates; §9 documenta lo que la auditoría encontró *alrededor*, que necesitan (a) la sesión del **punto 8** —propuesta dinámica, causa raíz en ROADMAP §7.2— y (b) la del **tribunal** (diseño por bot: **CONTEXT-BOTS §5**; plan: **ROADMAP §7.2**). Los seis agujeros A1-A6 ya están registrados como deuda en ROADMAP v4.2 §13 — la equivalencia de nomenclaturas vive en **CONTEXT-BOTS §10.4**.
> **Corpus de referencia:** `output/FASE-D_salentoreal_post_guard/v4_complete/hotelsalentoreal/v4_audit/` (corrida 2026-08-31 12:28:03), re-verificado el 2026-09-02.
> **Migrado desde CONTEXT-BOTS §13 el 2026-09-03** (reestructuración: hallazgos de pipeline al dossier de estabilización; el diseño del tribunal permanece en CONTEXT-BOTS §5).
> **Simetría estructural con §4 (no deduplicar):** las 8 caídas de §4 son producción de módulos que nunca se convierte en pain; los 2 huérfanos de B1 son pains que producen assets que nadie promete. El pipeline pierde información en ambos costados del mapper — la simetría es el hallazgo.

### 9.1 Seis agujeros vivos (bloque A)

Verificados contra código vivo y artefactos reales el 2026-09-02. Al momento del hallazgo **ninguno estaba documentado en el repo**; desde **ROADMAP v4.2** los seis están registrados como deuda o precondición — A1→**H9**, A2→**H7**, A3→**P12**, A4→**T0.2**, A5→**P10**, A6→§6.4/**G11**. Se conservan aquí con su evidencia por archivo.

**A1 — G9 se salta en verde.**
- *Qué:* si no existe `proposal_asset_matrix.json`, el gate de alignment de delivery se marca como pasado.
- *Evidencia:* `delivery_quality_report.py:250-257` → `{"passed": True, "gate": "G9", "skipped": True, "reason": "proposal_asset_matrix.json not found"}`. El summary (`:310-319`) cuenta `passed_count` sobre `gate_results.values()` ⟹ **un gate saltado se cuenta como gate pasado**. Hay además un **segundo default independiente** en `:325` (`{"passed": True, "gate": "G9"}`) para cuando la clave no existe.
- *Consecuencia:* un paquete sin matriz pasa el gate de delivery de forma vacuamente verde. Dos defaults para la misma clave = dos fuentes de verdad.
- *Requisito:* `skipped` no debe contar como `passed`; debe ser `NOT_EVALUATED` y visible en el acta. Unificar los dos defaults.

**A2 — El oráculo de presencia no se persiste.**
- *Qué:* `site_presence_report` es la entrada que decide `present_in_production` y por tanto `no_breach`, `unresolved`, `coverage_ratio` y G9. No se escribe a disco.
- *Evidencia:* `find output -iname "*site_presence*"` → **0 resultados** en todo el histórico. Para medir hubo que reconstruir el snapshot a mano.
- *Consecuencia:* el número más decisivo del gate de alignment **no es auditable post-hoc**. El Bot 3 del tribunal (diseño: CONTEXT-BOTS §5) no puede revisar lo que no existe y ninguna corrida pasada puede re-evaluarse bajo un oráculo distinto.
- *Requisito:* persistir el snapshot canónico — el concepto ya existe (`main.py:2535` lo pasa como `site_presence_snapshot`, DT4-R2); falta escribirlo junto a los demás artefactos de `v4_audit/`.

**A3 — `promised_assets_exist`, el check más pesado, solo corre pre-gen.**
- *Qué:* el cross-check contra el registro estático se ejecuta únicamente cuando no hay assets generados.
- *Evidencia:* `coherence_validator.py:670` `if not generated_assets:`, con comentario H6 FIX explícito (*"With real generated_assets, we trust the orchestrator's actual output"*). El acoplamiento oculto con el registro está en `:622`.
- *Consecuencia:* el check de peso **2.0** (el mayor de los 6, sobre total 7.5) devuelve `score=1.0` **hardcoded** en la rama de éxito (`:689-700`); el tamaño del registro solo entra al *mensaje*. Post-generación —que es cuando importa— el check confía en el orquestador sin re-verificar el contrato. Esto explica por qué Δcoherence = 0.0000 al cambiar el registro (B5).
- *Requisito:* si el Bot 1 va a certificar P6.3, no puede apoyarse en este check tal como está.

**A4 — Doble oráculo de presencia: decisión y narrativa divergen.**
- *Qué:* un mismo resultado de gate puede afirmar que un asset falta y a la vez listarlo como presente en producción.
- *Evidencia:* reproducido con nombres reales sobre SalenteReal — el resultado dice que **Schema Hotel** está `missing` y simultáneamente lo incluye en `present_assets`. Mecanismo: el oráculo **permisivo** (`PRODUCTION_PRESENT_STATUSES = ("exists", "exists_with_issues")`, `site_presence_checker.py:73`, decisión FASE-SR-E H7/L-SR3) es el que **decide**; el **estricto** es el que **escribe el mensaje**.
- *Consecuencia:* el humano (y el Bot 3) lee una narrativa que no corresponde con la decisión tomada. Misma forma de defecto que R2 (`site_verification_applied`, CONTEXT-BOTS §13).
- *Requisito:* un solo oráculo para decidir y para narrar, o narrativa derivada de la decisión.

**A5 — Parámetro fantasma y skip silencioso en los dos builders de matriz.**
- *Qué:* hay dos constructores de matriz y ambos tienen rutas de silencio.
- *Evidencia:* `AssetAlignmentMatrix.build` (`proposal_asset_alignment.py:748-789`) declara `delivery_context` como fuente de verdad preferida en su docstring, pero **lo ignora** cuando `generated_assets is not None` (L779-789). `ProposalAssetMatrix.build` (`:575-659`) hace **skip silencioso** en `:610-612` (`if not expected_asset: continue`): un servicio sin asset esperado desaparece de la matriz sin dejar rastro. Medido: los dos builders son **empíricamente idénticos en las 5 variantes probadas**.
- *Consecuencia:* hoy no divergen, pero hay dos rutas por las que un servicio puede esfumarse sin señal. Duplicación sin divergencia es deuda latente, no seguridad.
- *Requisito:* un solo builder; el skip de `:610-612` debe dejar una entrada con estado explícito (`NO_ASSET_MAPPED`), no desaparecer.

**A6 — La matriz persistida pierde el puntero al artefacto.**
- *Qué:* `asset_path` se serializa como `null` incluso para la entrada LINKED cuyo asset sí se generó.
- *Evidencia* (entrada real de `proposal_asset_matrix.json`, versión 2.0):
  ```json
  {"alignment": "linked", "asset_path": null, "asset_type": "llms_txt",
   "confidence": 1.0, "pain_ids": ["ai_crawler_blocked"],
   "service_name": "Optimización para IA Generativa", "status": "LINKED"}
  ```
- *Consecuencia:* la trazabilidad P6.3 (*"recomendación vendida → asset específico trazable"*) **no se puede verificar desde el artefacto**: no hay ruta al archivo. El Bot 3 tendría que adivinar el nombre.
- *Requisito:* poblar `asset_path` cuando el asset existe; es el campo que hace auditable P6.3.

### 9.2 Mecanismo causal de `no_breach = 6/7` (bloque B) — insumo del punto 8

Esto es lo que necesita la sesión del **punto 8** (propuesta dinámica, causa raíz en ROADMAP §7.2 "Causa raíz por debajo de T0"). Sin esto se vuelve a medir desde cero.

**B1 — La matriz real, verificada entrada por entrada.** 7 servicios: **6 NO_BREACH + 1 LINKED**, `delivery_ready: True`.

| Servicio prometido | `asset_type` | Estado | conf | `pain_ids` |
|---|---|---|---|---|
| SEO Local | `optimization_guide` | NO_BREACH | 0.0 | `[]` |
| Botón de WhatsApp | `whatsapp_button` | NO_BREACH | 0.0 | `[]` |
| Schema Hotel | `hotel_schema` | NO_BREACH | 0.0 | `[]` |
| Schema Organization | `org_schema` | NO_BREACH | 0.0 | `[]` |
| Página de FAQ | `faq_page` | NO_BREACH | 0.0 | `[]` |
| Meta Tags Sociales (Open Graph) | `open_graph` | NO_BREACH | 0.0 | `[]` |
| **Optimización para IA Generativa** | `llms_txt` | **LINKED** | 1.0 | `["ai_crawler_blocked"]` |

Y el ledger resuelto tiene **exactamente 3 entradas**, las tres MEDIUM y ASSET_GENERATED: `no_analytics_configured`, `low_organic_visibility`, `ai_crawler_blocked`.

**La doble falla de mapeo, que es la causa raíz:**
- `low_organic_visibility` **sí se detectó** y produjo `indirect_traffic_optimization` (`pain_solution_mapper.py:179`; `asset_catalog.py:300-313` IMPLEMENTED) — pero **ningún servicio prometido mapea a ese asset**: es un **huérfano**. Se genera, se entrega y no responde a nada vendido.
- `no_analytics_configured` produjo `analytics_setup_guide` — **segundo huérfano**, mismo mecanismo (`pain_solution_mapper.py:170`).
- "SEO Local" promete `optimization_guide`, que solo se mapea desde `low_citability` (`pain_solution_mapper.py:207-215`) — pain que **no se detectó**. El servicio prometido queda NO_BREACH.

⟹ **El registro promete por pains que no aparecieron, y los pains que aparecieron producen assets que nadie promete.** Los dos extremos del contrato comercial están desalineados por construcción del mapper, no por los datos del hotel. De 4 assets generados, **2 son huérfanos** y 1 (`monthly_report`) no tiene pain.

**B2 — Brecha runtime vs estática.** El registro estático `PROPOSAL_SERVICE_TO_ASSET` está **completo: 7/7 con asset implementado**. El problema no es el registro. En runtime se generan **4 assets** (`asset_generation_report.json`: `analytics_setup_guide` WARNING, `indirect_traffic_optimization` WARNING, `llms_txt` PASSED, `monthly_report` PASSED; `total_assets = 4`, `estimated = 2`, `delivery_ready_percentage = 100.0`) y la **intersección prometido ∩ generado = {`llms_txt`}** — un solo elemento. `monthly_report` se genera pero **no está en el registro** (comentado en `proposal_asset_alignment.py:27-29`, FASE-3 BUG-10).
⟹ Quien confunda "registro completo" con "cobertura real" llega a la conclusión opuesta. Fue un falso positivo de esta misma auditoría (§9.5, #3).

**B3 — Los seis registros de identidad de servicios.** Punto 8 es imposible sin decidir cuál manda.

| Registro | Ubicación | Tamaño | Rol |
|---|---|---|---|
| `service_catalog` | config | **8** | lo que se declara vendible |
| `PROPOSAL_SERVICE_TO_ASSET` | `proposal_asset_alignment.py:22-33` | **7** | lo que la propuesta promete → asset |
| `ASSET_CATALOG` | `asset_catalog.py` | **25** | lo que se sabe generar |
| `PAIN_SOLUTION_MAP` | `pain_solution_mapper.py` | **22 mapeables** | pain → asset |
| Output runtime del orquestador | `asset_generation_report.json` | **4** | lo que de hecho se generó |
| Contract registry | `asset_responsibility_contract.py` | **3 CORE + 3 GEO** | responsabilidad de deploy |

Seis fuentes, ninguna canónica. `ALL_PROMISED_SERVICES = list(PROPOSAL_SERVICE_TO_ASSET.keys())` (`:45`) hace que el registro de 7 mande sobre el de 8, mientras el comentario de `:35-37` dice "All 8".

**B4 — Palancas medidas sobre la cobertura.** Bajo el régimen actual `coverage_ratio` = **1.000 en las 10 configuraciones** (tautología, §8.3). Lo que varía es el resultado bajo **S2.3** (denominador = `promised_services_total`):

| Configuración | coverage bajo S2.3 |
|---|---|
| Rango en las 10 (5 registros × 2 oráculos) | **0.125 – 0.714** |
| Registro actual (7), oráculo permisivo | **0.571** (4/7) |
| Registro actual + S1.2 (añadir `monthly_report`) | **0.500** — *empeora*, porque el pain `no_monthly_report` no se detecta |
| **R8c** (remapear "SEO Local" → `indirect_traffic_optimization`) | **0.714** (5/7) — única palanca que sube |
| R8 (8 servicios), oráculo estricto | **0.125** |

- **S2.3 bloquea en las 10** (ninguna alcanza 0.8) ⟹ por eso §8.5 lo descarta.
- `unresolved = 0` y **G9 = PASS en las 10** ⟹ **S2.4 no tiene efecto alguno**.
- **Ninguna variante de registro llega a 1.0 sin punto 8.** La mejor (R8c) se queda en 0.714.

**B5 — Δcoherence medido, y por qué es cero.**

| Cambio de registro | Δ coherence_score | Mecanismo |
|---|---|---|
| 7 → 8 servicios (añadir `monthly_report`) | **+0.0000 exacto** | Dos candados independientes: (1) la rama de éxito hardcodea `score=1.0` (`coherence_validator.py:689-700`) y el tamaño del registro solo entra al mensaje; (2) la rama de fallo usa una **UNIÓN** (`:703`, `total_checked = len(promised_types \| set(PROPOSAL_SERVICE_TO_ASSET.values()))`) y `monthly_report` ya está en `promised_types` ⟹ la unión vale 10 para R7 y para R8 |
| R22 (vocabulario completo de 22 del mapper) | **−0.0121** (0.88 → 0.8679) | Único cambio que sí mueve el score. Causa: `direct_booking_campaign` es **MANUAL_ONLY** en `asset_catalog.py` ⟹ `is_asset_implemented` False ⟹ entra a `missing_service_assets` |

- **Sensibilidad:** pesos `1.5/1.0/1.5/0.5/1.0/2.0` (total 7.5, `coherence_validator.py:101-108`) ⟹ **0.2667 por unidad**. Headroom actual **0.08**. Score mínimo de un check para mantener overall ≥ 0.8 = **0.7000** (M=3 de 10 faltantes).
- **Landmine:** unificar los registros con el vocabulario del mapper (22) cuesta 0.0121 de coherencia por un asset MANUAL_ONLY. Unificar no es gratis.
- **Cierre con N11:** el gate decide con `coherence_score`, **nunca con `is_coherent`**; los artefactos dicen `is_coherent: false` en cuatro lugares y el gate PASÓ. Causa única: `_check_assets_are_justified` = **3/4 = 0.75** → `severity="error"` (`coherence_validator.py:255-309`). **Ese 3/4 está confirmado por el artefacto real**: 4 assets generados, 3 con pain en el ledger, 1 (`monthly_report`) always-on sin pain. ⟹ **La misma falla estructural de B1 (assets sin pain y pains sin servicio) produce a la vez el `no_breach = 6/7` y el `is_coherent = false`.** Punto 8 elimina las dos.

### 9.3 Costos comparados (bloque C)

| Cambio | Tests a tocar | Candados de regresión | Δ protección real |
|---|---|---|---|
| Advisory 2 (§8.4) | **~6** de alignment | 0 hoy; hay que crearlos (§8.4, ítem 4) | **0** — coverage es 1.000 siempre; no se pierde nada |
| S2.3 (denominador) | **~41 tests / 152 asserts** | 0 | **Negativo** — revierte D-PF1 y bloquea 3 de 4 configuraciones históricas (75%) |

Baseline medido antes de tocar nada: **140 passed, 1 skipped, 8 warnings, ~1.23s** sobre los 7 archivos de tests de alignment/gates (141 tests, 32 asserts de bloqueo). **0 tests** referencian `BLOCKING_GATE_NAMES`.

### 9.4 Tabla consolidada de mediciones (para no re-medir)

| Magnitud | Valor | Dónde |
|---|---|---|
| Corridas históricas únicas en `output/` | **29** (10 hoteles) | §8.2 |
| Corridas con 100% assets ESTIMATED | **4 (14%)** — `hotel_visperas`/`hotel_vísperas`, 2026-03-25 → 2026-04-05, todas con `coherence_score_final = None` | §8.2 |
| Configuraciones únicas de alignment en el histórico | **4**, con `no_breach = None` en 3 | §8.5 |
| Matriz SalenteReal | 7 entradas: 6 NO_BREACH + 1 LINKED, `delivery_ready: True`, versión 2.0 | B1 |
| Ledger resuelto | **3 pains**, todos MEDIUM / ASSET_GENERATED | B1 |
| Assets generados en runtime | **4** (2 WARNING, 2 PASSED), `estimated = 2`, `delivery_ready_percentage = 100.0` | B2 |
| Intersección prometido ∩ generado | **{`llms_txt`}** — 1 elemento; 2 assets huérfanos | B1/B2 |
| `coverage_ratio` (régimen actual) | **1.000** en 10/10 | §8.3 |
| `coverage_ratio` bajo S2.3 | **0.125 – 0.714**, bloquea en 10/10 | B4 |
| `unresolved` / G9 | **0** / **PASS** en 10/10 ⟹ S2.4 sin efecto | B4 |
| Δcoherence 7→8 | **+0.0000** | B5 |
| Δcoherence R22 | **−0.0121** (0.88 → 0.8679) | B5 |
| coherence canónico SalenteReal | **0.88** (DT4-N4); `0.9133` es `pre_coherence_score`, **no canónico** | CONTEXT-BOTS §13 R3 |
| `is_coherent` | **false** en 4 lugares del artefacto; el gate PASÓ igual. Causa: 3/4 = 0.75 | N11 / B5 |
| Sensibilidad de coherence | **0.2667**/unidad; headroom **0.08**; mínimo por check **0.7000** | B5 |
| ZIP de la entrega | `hotelsalentoreal_20260831.zip`, **46,552 bytes**; directorio expandido **37 archivos** | CONTEXT-BOTS §13 R1 |
| Artefactos `site_presence*` persistidos | **0** en todo `output/` | A2 |
| Tests que fijan la lista advisory | **0** | §8.4 |

### 9.5 Falsos positivos de esta auditoría (corregidos, para no repetirlos)

Siete afirmaciones que se hicieron durante el análisis y que la medición refutó. Se listan porque son las trampas naturales de este código:

1. "Dos rutas de veredicto independientes desde un mismo DTO" → **algebraicamente redundantes** (§8.3).
2. "S2.4 volteaba G9 → ZIP ABORTED" → **falso en SalenteReal**: hay cero MISSING_ASSET en la matriz.
3. "La intersección prometido × generado es solo `{llms_txt}`" → cierto **en runtime**, falso **para el registro estático** (7/7 completo). Ver B2.
4. "Los dos builders de matriz divergen" → **empíricamente idénticos** en las 5 variantes. Ver A5.
5. "El umbral de coverage es código muerto" → **impreciso: redundante, no muerto** (3 tests lo ejercitan, disparó en 2 de 4 configuraciones históricas).
6. "S2.3 es insatisfacible" → **refinado**: insatisfacible bajo el régimen de SalenteReal; una configuración histórica sí lo pasa.
7. "El 0.88 canónico no es estable bajo S1.2" → **refutado**: Δ = 0.0000 exacto.

**Lección de forma:** en este pipeline, revalidar citas de código **no** revalida premisas. Las siete afirmaciones de arriba eran coherentes con el código leído y falsas contra el artefacto real. Todo hallazgo de §9 está anclado a un artefacto o a una corrida, no a una lectura.

## 10. Mapa de migración (2026-09-03)

| Antes (CONTEXT-BOTS 2026-09-01/02) | Ahora | Contenido |
|---|---|---|
| §12.1-12.6 | §8.1-8.6 (este dossier) | severidad advisory = 2, no 3 (H10) |
| §13.1 | §9.1 (este dossier) | A1-A6 |
| §13.2 | §9.2 (este dossier) | B1-B5 — punto 8 |
| §13.3 | §9.3 (este dossier) | costos comparados |
| §13.4 | §9.4 (este dossier) | tabla consolidada de mediciones |
| §13.5 | §9.5 (este dossier) | falsos positivos + lección de forma |
| §12.7 | CONTEXT-BOTS §13 (se queda) | correcciones adyacentes de §3/§8; N11 → puntero a §9.2 |

Etiquetas **invariables** (vocabulario compartido con ROADMAP v4.2): A1-A6, B1-B5, R*, N11, H10, T0.x, G9/G11, P6/P9/P10/P12, D-PF1, S1.2/S2.3/S2.4, R8c, R22.

**Hard precondiciones del tramo offline del tribunal** (orden sugerido para el plan de estabilización):
1. **Punto 8** (§9.2) — sin él el Bot 2 marcaría SIN-BRECHA-ASOCIADA en 6/7 servicios de toda corrida: el tribunal devolvería todo paquete y no añadiría valor.
2. **A2** persistir el oráculo de presencia (§9.1) — Bot 3 no puede auditar post-hoc lo que no existe en disco.
3. **A6** poblar `asset_path` (§9.1) — P6.3 no verificable desde el artefacto.
4. **N11/P9** (§9.2-B5) — el pipeline debe respetar `is_coherent` antes de que Bot 1 lo certifique.
5. **H10** (§8) — severidad correcta para el veredicto del Juez.

El resto del dossier (§4, §5, §6, §7) es **completitud del diagnóstico**: valioso en sí, faseable después de las precondiciones.

## 11. Fuentes

- Artefactos: `output/FASE-D_salentoreal_post_guard/v4_complete/` (doc, `v4_audit/*.json`, `geo_enriched/`, ZIP).
- Código: `pain_solution_mapper.py`, `v4_diagnostic_generator.py`, `publication_gates.py`,
  `v4_comprehensive.py`, `ai_crawler_auditor.py`, `pagespeed_client.py`, `v4_asset_orchestrator.py`,
  `proposal_asset_alignment.py`, `alignment_result.py`, `coherence_validator.py`, `asset_catalog.py`,
  `delivery_quality_report.py`, `site_presence_checker.py`, `commercial_gate.py`.
- QMind `iah-cli-lecciones`: CONTEXT-H (Zione 2026-08-02/03), CONTEXT Salento Real ejecución (2026-08-27),
  10-analisis SR-PIPELINE-FIXES (2026-08-28), 10-analisis VALIDADOR-URL-PROPIA (2026-08-31).
- Git: `e544a59` (2026-08-03), `f914e0e`/`f77f8ae` (2026-08-31).
- CONTEXT-BOTS `CONTEXT-BOTS-POTENCIALIZACION-IAH-CLI-2026-09-01.md`: origen del material migrado (§12.1-12.6 → §8; §13 → §9); su §10.4 conserva el puente de nomenclaturas con ROADMAP.
- ROADMAP v4.2: §7.2 (plan del tribunal, tramos, precondiciones T0), §13 (registro de deudas A1-A6 → H9/H7/P12/T0.2/P10/G11).
- Memoria de proyecto: `auditoria-brechas-diagnostico-vs-modulos-salentoreal.md`,
  `medicion-deltas-coverage-ratio-y-coherence-salento-real.md`, `plan-tribunal-bots-anclado-en-p6.md`,
  `decision-advisory-gates-2-no-3.md`.
