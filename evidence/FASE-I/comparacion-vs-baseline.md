# FASE-I — Comparación de la corrida E2E contra el baseline

**Corrida**: `output/FASE-I_salentoreal_post_estabilizacion/v4_complete/` (2026-09-04 12:01:24 → 12:04:18, EXIT 0)
**Baseline**: `output/FASE-D_salentoreal_post_guard/v4_complete/` (corrida 2026-08-31 12:28:03, **solo lectura**)
**Método**: `comparar_faseI_vs_baseline.py` (adaptado de `evidence/FASE-VUP-D/verificar_no_regresion.py`) +
sondas de estructura (`faseI_probe.py`, `faseI_ocho_caidas.py`) + repro mínimo (`faseI_repro_g2.py`).
**Salida máquina**: `comparacion_resultados.json`

> Esta fase **no corrige código**. Todo lo que apareció se registra y se lleva a VERIFY.

---

## 0. Resultado global: **14 / 16 checks en verde**

| # | Check | Ref | Baseline | Esta corrida | |
|---|-------|-----|----------|--------------|---|
| C1 | identidad `hotel_id`/URL | equivalencia | `hotel_hotelsalentoreal.com` | igual | ✅ |
| C2 | coherence ≥ 0.80 | **NR6**/AC6 | 0.88 | **0.8333** | ✅ |
| C3 | `is_coherent` | **AC6**/V16 | `false` × 4 declaraciones (8 copias en disco) | **`true` × 4 (4 copias)** | ✅ |
| C4 | matriz `no_breach` | **AC5** | **6** NO_BREACH + 1 LINKED (7 entradas) | **0** — 3 PRESENT_IN_PRODUCTION + 1 LINKED (4) | ✅ |
| C5 | `site_presence_snapshot` | **AC9**/A2 | **inexistente** | **existe** (1.421 B; 5 servicios) | ✅ |
| C6 | `asset_path` | **AC9**/A6 | null incluso en la LINKED | **poblado** en LINKED (+1 archivo dentro del ZIP) | ✅ |
| C7 | perfil 11 blocking + 2 advisory | **AC7**/D2 | 13 gates, `severity=null` en todos | 13 gates, **campo `severity` no existe en el artefacto** | ❌ |
| C8 | `doc_audit_consistency` | **NR1**/G1 | PASSED con **`value=null`** | PASSED con **`value=0`** y mensaje real | ✅ |
| C9 | `critical_recall < 1.0` | **NR2**/G2 | 1.0 **vacuo** (0 críticos) | 1.0 con **críticos registrados** — pero el artefacto no lo dice | ❌ |
| C10 | coherencia ↔ veredicto ↔ ZIP | **AC12** | ZIP generado con `is_coherent=false` | ZIP generado con `is_coherent=true`, `ready=true` | ✅ |
| C11 | commercial gates (los 2 archivos) | CG-*/D2 | 3 + 9 = **12**, falla `CG-WHATSAPP-LEAD` | 3 + 9 = **12**, falla `CG-WHATSAPP-LEAD` (idéntico) | ✅ |
| C12 | `pain_ledger_resolved` | AC6/FASE-B | 3 entradas MEDIUM ASSET_GENERATED | **5** entradas (3 ASSET_GENERATED + 2 DETECTED) | ✅ |
| C13 | `low_ota_divergence` de vuelta | V7/FASE-H | **no existe** en el ledger | **existe, HIGH**, en ledger y resolved | ✅ |
| C14 | Tier B con defaults | equivalencia | `"default"`, Tier B | `"Using defaults"`, warning Tier B idéntico | ✅ |
| C15 | plan de assets | AC6/FASE-C | 4 assets, `estimated=2`, 100 % delivery | 4 assets, `estimated=2`, 100 % delivery | ✅ |
| C16 | PageSpeed | anomalía (iii) | `status=ERROR` | `status=ERROR` (misma causa de infra) | ✅ (informativo) |

---

## 1. ACs verificados sobre artefactos reales

**AC5 — `no_breach` 6 → 0.** `proposal_asset_matrix.json` pasó de 7 entradas con 6 `NO_BREACH` a 4
entradas con estados reales: 3 `PRESENT_IN_PRODUCTION` (schema hotel, schema org, página FAQ) y 1
`LINKED` (`llms_txt`). El `summary` que añadió FASE-C está poblado: `{promised: 4, not_promised: 3,
unknown: 0}` — en el baseline el campo `summary` **no existía** (`null`).

**AC6 — `is_coherent` true.** Las 4 declaraciones del campo (2 archivos `coherence_validation*` +
`coherence_report` y `final_coherence_report` dentro de `asset_generation_report.json`) pasaron de
`false` a `true`. Las copias en disco bajaron de 8 a 4. El check que lo causaba — `assets_are_justified`
en **0.75, severity=error** — ahora está en **1.0, pasa**. La causa V16 (`assets_are_justified 3/4`)
está cerrada sobre el artefacto real, no solo en tests.

**AC9 — snapshot + `asset_path`.** `site_presence_snapshot.json` existe (`snapshot_version` + 5
servicios con `status`/`confidence`/`site_verified`: `faq_page exists 0.9`, `hotel_schema
exists_with_issues 0.95`, `org_schema exists_with_issues 0.95`, `llms_txt not_exists 0.7`, …) **y viaja
dentro del ZIP** (`ASSETS/v4_audit/site_presence_snapshot.json`): el diferencial normalizado del ZIP
38 vs 37 archivos es exactamente ese archivo. `asset_path` de la entrada LINKED apunta al `llms_txt`
generado. Los tres `PRESENT_IN_PRODUCTION` traen `asset_path: null` **por diseño**: no hay archivo
local que señalar, su verificación es el snapshot.

**AC12 — coherencia ↔ veredicto ↔ ZIP.** El baseline empaquetó una entrega de 37 archivos con
`is_coherent=false`. Esta corrida empaqueta con `is_coherent=true`, `readiness.ready=true`,
`READY_FOR_PUBLICATION`. El veredicto y el empaquetado son coherentes en ambos sentidos del check.

**AC7 — NO verificable sobre artefactos.** Ver §3 (C7).

---

## 2. NRs verificados

**NR1 — `doc_audit_consistency` dejó de ser vacuo.** Baseline: `status=PASSED, value=null` (nunca vio
los datos). Ahora: `value=0` con mensaje real *"Document consistent with audit data — no
contradictions detected"*. El gate efectivamente recibe `audit_data`: se confirmó leyendo el call site
(`main.py:2939` → `builder.with_audit_data(audit_result.to_dict())`) y el builder lo serializa
(`modules/assessment_builder.py:228`). Cero contradicciones document↔audit es un resultado legítimo, no
un `null` disfrazado.

**NR2 — el criterio literal NO se cumple** (1.0 no es `< 1.0`), pero el 1.0 **ya no es el mismo 1.0**:

| | Baseline | Esta corrida |
|---|---|---|
| value | 1.0 | 1.0 |
| críticos del audit | **0** | **1** — `"PageSpeed API ERROR - performance not measurable (API de PageSpeed no disponible)"` |
| banda GEO | `critical` (no llegaba al gate) | `critical` → `with_geo_flow` la anexa como critical issue |
| `details` | `{"critical_issues_count": 0, "recall_basis": "audit_present_no_critical_issues"}` | **`{}`** |

El baseline era 0/0 sin datos; esta corrida es n/n con evidencia dura. **Y sin embargo el artefacto
nuevo es MENOS auto-descriptivo que el baseline**: su `details` está vacío. Ver §3 (C9) y S-I1.

**NR6 — `coherence 0.8333 ≥ 0.80` y perfil de gates esperado** en cuanto a veredicto: 11 `PASSED` + 2
`WARNING` (`financial_validity`, `pricing_compliance`), `blocking_issues: []`,
`status=READY_FOR_PUBLICATION`. La equivalencia de tier se mantuvo: `"Using defaults"` en el log y el
mismo warning `Financial data uses default/legacy values — Tier B evidence`.

---

## 3. Los dos FAIL: causa raíz medida, no suposición

### C7 — la severidad 11+2 no se serializa (AC7)

`gate_report_*.json` tiene `gate_results[]` con claves `details, gate_name, message, passed, status,
suggestion, value`. **No existe** `severity` ni `blocking` (conteo de la palabra `severity` en el
archivo: **0**). Las 11+2 viven en la config y se aplican para derivar el veredicto — `check_publication_readiness`
lo dice en su propio docstring: *"Overall readiness status (decided by gate SEVERITY, not by `passed`)"*
— pero el artefacto que ve el humano no lo refleja por gate. Solo `readiness.blocking_issues` y
`readiness.warnings` son consecuencia de ello.

Clasificación: **(ii) deuda de divulgación**, no fallo funcional. AC7 queda **sin verificar sobre
artefactos reales**; en código y tests sí está (FASE-D). → **S-I2**.

### C9 — el detector G2 quedó a la sombra del trabajo V6 de FASE-H

Repro mínimo (`faseI_repro_g2.py`, con la forma real de producción): `audit_data` **sí** llega al
assessment, `with_geo_flow` **sí** anexa `"GEO readiness critical (score 29/100, band 'critical')…"`,
y con un `performance.status=ERROR` no cubierto el resultado es **0.5 / BLOCKED**. Es decir: FASE-G predijo
que esta corrida daría `critical_recall` BLOCKED. **En la corrida real dio 1.0 / PASSED.**

La diferencia está medida, no inferida: `_evident_critical_missed()`
(`modules/quality_gates/publication_gates.py:2092-2097`) devuelve 0 si la lista de críticos ya cubre el
eje de rendimiento — y en la corrida real **lo cubre**, porque el auditor mismo registró
`"PageSpeed API ERROR - performance not measurable"` en `overall.critical_issues` (`audit_report_…json:81`),
que `assessment_builder.py:213` propaga al assessment. Con `covered=True`, `missed=0`, y recall = n/n = 1.0.

Es un caso de **interacción entre fases que cancela el mecanismo de la fase anterior sin romper su
intento**: el objetivo de G2 (que el 1.0 no sea vacuo) **sí se cumple en sustancia** — hay 2 críticos
reales y los dos están registrados — pero el detector anti-vacuidad queda **inobservable** en el
artefacto, porque `details={}` no distingue n/n de 0/0 y la anotación de trazabilidad de FASE-SR-H2
solo se escribe cuando `critical_issues` está vacío (`publication_gates.py:712-721`).

Clasificación: **(i) fix esperado** en sustancia + **(ii) deuda de divulgación** en la forma. El criterio
literal de NR2 queda **abierto para VERIFY**. → **S-I1**.

---

## 4. Por qué la coherencia BAJÓ de 0.88 a 0.83 (delta explicado, no "variación natural")

Movimientos opuestos dentro del mismo `coherence_validation.json`:

| Check | Baseline | Esta corrida | Causa |
|-------|----------|--------------|-------|
| `assets_are_justified` | **0.75 — FALLA** (error) | **1.0 — pasa** | FASE-B (biyección) + FASE-C (punto 8 dinámico) |
| `problems_have_solutions` | 1.0 — pasa | **0.6 — pasa** (warning) | el ledger pasó de **3 a 5 pains**; solo 3 tienen asset |
| `financial_data_validated` | 0.7 | 0.7 | sin cambio |
| `whatsapp_verified` | 1.0 | 1.0 | sin cambio |
| `price_matches_pain` | 0.8 | 0.8 | sin cambio |
| `promised_assets_exist` | 1.0 | 1.0 | sin cambio |

El baseline marcaba 1.0 en `problems_have_solutions` porque **no conocía** los dos pains que ahora sí
conoce: `low_ota_divergence` (HIGH, reactivado por V7 en FASE-H) y `missing_llmstxt` (LOW, emisión
reactivada por FASE-B/C). La cifra anterior era un 1.0 sobre un denominador mutilado.

**Consecuencia medida**: 0.88 → 0.8333. Sigue ≥ 0.80 (NR6 intacto), pero el sistema **bajó su propia
nota por decir más verdad**. Los dos pains nuevos están divulgados en los documentos — el gate
`coverage_no_silent_drop` lo confirma con `uncovered: []` y *"Coverage completo: 5 en diagnostico/propuesta,
0 justificadas de 5 detectadas"* — y en cambio `pain_ledger_resolved.summary` reporta
`{asset_generated: 3, mapped_to_service: 0, justified_skip: 0}`: **0 pains mapeados a servicio** pese a
que la Capa 1 de FASE-A existe para eso. Qué se espera de `problems_have_solutions` cuando un pain se
cubre con servicio y no con asset es **decisión de VERIFY**. → **S-I4**.

---

## 5. Las 8 caídas silenciosas del dossier §4, re-evaluadas sobre el diagnóstico nuevo

Evidencia en `faseI_ocho_caidas_new.txt` y `faseI_ocho_caidas_base.txt` (misma sonda en ambos lados).

| # | Caída | Estado tras A-H | Evidencia medida en la corrida |
|---|-------|-----------------|--------------------------------|
| 1 | PageSpeed ERROR | ✅ **SUPERADA** (divulgación) | Ya no es solo log: el diagnóstico dice *"Sin Datos de Campo (Core Web Vitals) \| 🔴 Alta \| API de PageSpeed no disponible"* y el audit lo registra como `critical_issues[0]`. La causa de infra sigue (V12) |
| 2 | GEO crítico 29/100 | ◐ **PARCIAL** | Aparece *"Salud Técnica GEO \| 29/100 \| critical \| 🔴"* y entra a `critical_issues` vía `with_geo_flow`. **Pero los tres números GEO siguen conviviendo**: 79 (tabla principal), 85 (desglose `GEO 85/100 = … ✅ fotos_gbp(15%)`) y 29 (crítico) |
| 3 | Visibilidad LLM = 0 | ◐ **PARCIAL** | `mention_rate 0.0`, `share_of_voice 0.0`, `snippets 0/5`, `ia_readiness.components.llms_txt = 0` — ahora **sí** producen pain `missing_llmstxt` y BRECHA 5. **Pero el doc sigue afirmando** *"Visibilidad en IA: Alta (estimado cualitativo)"*, con disclaimer, sobre los mismos ceros |
| 4 | `missing_llmstxt` muerto | ✅ **SUPERADA** | Pain emitido (LOW) en `pain_ledger` y `pain_ledger_resolved`; BRECHA 5 "Sin llms.txt" en el diagnóstico; servicio `Optimización para IA Generativa` aparece en la propuesta ligado a `#5: Sin llms.txt ($513.430 COP/mes)` |
| 5 | 2 schema warnings | ✗ **SIN CAMBIO** | `recommendations` del audit, 0 pain, 0 mención en el doc. **No estaba en el alcance de A-H** |
| 6 | Fotos GBP 10/40 | ◐ **PARCIAL** | **El fix V11(c) de FASE-H es visible**: el diagnóstico nuevo tiene cabecera `\| Atención manual requerida \| Prioridad \| Acción \|` + separador (líneas 197-198) donde el baseline tenía la fila **huérfana, sin cabecera** (línea 181). **Pero** la caída de fondo sigue: `gbp.photos = 10` sin pain, y la fila "Fotos GBP Insuficientes \| 🟡 Media" coexiste con `✅ fotos_gbp(15%)` en el desglose `GEO 85/100` — la contradicción del matiz C7 del dossier persiste |
| 7 | `title=""` / `description=""` | ✗ **SIN CAMBIO** | Idéntico en ambas corridas (`$.metadata.title = ""`, `has_default_title=false`, `has_default_description=false`) → **no es variación del sitio**. Ningún pain, ninguna mención en el doc. La vía disclosed del dossier (§7, refutación C4) no se activa |
| 8 | `low_ota_divergence` estructuralmente muerto | ✅ **SUPERADA** | Existe, **HIGH**, en ledger y resolved; `opportunity_scores[0] = low_ota_divergence "Alta Dependencia OTAs"`; el doc lo narra: *"Detalle: Solo 20% de reservas por canal directo"*. V7 de FASE-H funcionó sobre artefactos reales |

**Balance para VERIFY**: **cerradas en sustancia 3** (#1 divulgación + registro como crítico, #4
`missing_llmstxt`, #8 `low_ota_divergence`) · **parciales 3** (#2 GEO, #3 visibilidad LLM, #6 — en #6
mejoró el **render** de la tabla pero no su costado de pain/contradicción) · **intactas y fuera del
alcance de A-H 2** (#5 schema warnings, #7 `title=""`/`description=""`).

---

## 6. Anomalías clasificadas

### (i) Fix esperado del plan — 9
`is_coherent` true (×4) · `no_breach` 6→0 · `summary` de la matriz poblado · `site_presence_snapshot`
existente y dentro del ZIP · `asset_path` LINKED poblado · `doc_audit_consistency` con `value=0` ·
pains 3→5 con `low_ota_divergence` HIGH y `missing_llmstxt` LOW · `assets_are_justified` 0.75→1.0 ·
PageSpeed ERROR divulgado como critical issue.

### (ii) Deuda/regresión del plan — 4 (ninguna corregida aquí, por alcance)
1. **S-I1** `critical_recall` 1.0 con `details={}`: el artefacto no distingue n/n del 0/0 vacuo del
   baseline; el detector G2 queda a la sombra del registro V6. Criterio literal de NR2 no cumplido.
2. **S-I2** Severidad 11+2 no serializada en `gate_report_*.json` → AC7 no verificable sobre artefactos.
3. **S-I4** `problems_have_solutions` 1.0→0.6 con `mapped_to_service: 0` y `justified_skip: 0`: los 2
   pains nuevos se divulgan en los docs pero no se mapean a servicio ni a asset.
4. **S-I7** `proposal_asset_alignment` reporta `message: "4/4 servicios comprometidos cubiertos"` pero
   `details: {"total_services": 1, "aligned_count": 1}` — dos conteos del mismo concepto en el mismo
   objeto (patrón de la lección «unificar conteos en DTOs multi-consumer»).

### (iii) Infraestructura preexistente — 3
PageSpeed API no disponible (`performance.status=ERROR`, `has_field_data=false`, `mobile_score=null`,
`desktop_score=11`) con la trampa V12 confirmada: `PAGESPEED_API_KEY` correcta (39 chars) **y**
`GOOGLE_PAGESPEED_API_KEY` placeholder de 3 chars conviviendo en `.env`; `GEMINI_API_KEY` **ausente**;
CG-WHATSAPP-LEAD en `passed:false` (idéntico al baseline, no es regresión).

### (iv) Variación natural del sitio vivo — **0**
Ninguna diferencia se cerró como "variación natural". Se comprobó explícitamente: `gbp.photos=10`,
`rating`, `reviews`, `metadata.title=""`, `competitors[0..4].geo_score_formula` y los tres escenarios
financieros ($6.571.622 / **$4.042.752** / $1.264.435 COP/mes) son **numéricamente idénticos** al
baseline. Lo único que cambió entre 31-08 y 04-09 es el `research_id` (no cacheable, generado por
corrida) y los timestamps.

---

## 7. No-regresión

- Suite **antes** del run: `faseI_pre_baseline.txt` → **944 passed, 2 skipped** en 6.31 s.
  Suite **después** del run: `faseI_post_baseline.txt` → **944 passed, 2 skipped** en 5.86 s. **Delta
  cero**: el `v4complete` no alteró el estado de la suite.
- `run_all_validations.py --quick`: **7/7 antes** (`faseI_validations_quick.txt`) y **7/7 después**
  (`faseI_validations_post.txt`) del run.
- El baseline **no fue modificado** (solo lectura; `git status` sobre `output/FASE-D_salentoreal_post_guard/`
  permanece limpio por estar fuera del índice).
- Ni `VERSION.yaml` ni `clientes/` fueron tocados; no se usó `--force` ni `--ga4-property-id`.

---

## 8. Qué se lleva VERIFY desde esta fase

1. **AC5, AC6, AC9, AC12, NR1, NR6: verificados sobre artefactos reales.** **AC7 y NR2: NO verificados
   sobre artefactos** (S-I1, S-I2) — requieren decisión: se serIALIZA la severidad y la base del recall,
   o el AC se reescribe para exigir solo el veredicto.
2. La **predicción de FASE-G** («esta corrida producirá `critical_recall` BLOCKED») fue **falsada por la
   medición**. No porque el mecanismo falle — el repro aislado sí da BLOCKED — sino porque FASE-H hizo
   que el auditor registre el crítico, y el detector está diseñado para no contar dos veces.
3. La coherencia **bajó 0.047 por honestidad medida**. Si el plan exige «coherencia ≥ baseline», eso es
   otra decisión de diseño, no un defecto.
4. Tres caídas del dossier (§4 #5, #6, #7) **nunca estuvieron en el alcance A-H** y siguen intactas.
5. **S-I5** y **S-I6** son de forma: el directorio expandido de `deliveries/` y la deriva del conteo de
   tests en AGENTS.md.
