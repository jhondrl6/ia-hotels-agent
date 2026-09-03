# FASE-C — Contrato de propuesta dinámica (punto 8)

**Plan**: ESTABILIZACION-PRE-TRIBUNAL-2026-09-03 · **Fase**: C · **Tarea**: C1
**Fecha**: 2026-09-03 · **Estado**: contrato cerrado antes de tocar código
**Cierra**: AC5, AC6 · **Hallazgos**: B1-B5, §10#1 · **Deuda que paga**: CONTEXT-H Zione 2026-07-23 Fase 3

---

## 0. Premisa corregida por medición (S-C1)

El dossier §9.2 B5 atribuye el `is_coherent = false` estructural a dos candados de
`promised_assets_exist`: la rama de éxito que hardcodea `score = 1.0`
(`coherence_validator.py:689-700`) y la UNIÓN de la rama de fallo (`:703`).
**Esa atribución es incompleta y no es la causa operativa.**

Re-procesando los artefactos reales del corpus con código vivo
(`evidence/FASE-C/faseC_antes.txt`, arnés `faseC_contrafactual.py`):

| Check de coherencia | score | passed | severity |
|---|---|---|---|
| problems_have_solutions | 1.0 | True | — |
| **assets_are_justified** | **0.75** | **False** | **error** |
| financial_data_validated | 0.7 | True | — |
| whatsapp_verified | 1.0 | True | — |
| price_matches_pain | 0.8 | True | — |
| promised_assets_exist | 1.0 | **True** | — |

`overall_score = 0.88 ≥ 0.80`, pero `is_coherent = len(errors) == 0 and overall >= threshold`
(`coherence_validator.py:185`) ⟹ **el false lo produce `errors` no vacío, y el único error es
`assets_are_justified`**. `promised_assets_exist` pasa en verde: los dos candados de B5 son reales
pero **inertes para este veredicto**.

**Causa medida**: `_check_assets_are_justified` (`coherence_validator.py:283-288`) exige
`any(pid in problem_ids for pid in asset.pain_ids)`. La lista de `assets` que recibe es
`asset_specs` de `V4AssetOrchestrator` (`v4_asset_orchestrator.py:300-304`), y el bloque
**D4-FIX** (`:724-750`) inyecta todo asset con `promised_by ∈ {always, always_aeo}` con
**`pain_ids=[]`** — una lista vacía nunca satisface `any(...)`. En el corpus hay exactamente un
asset así: **`monthly_report`** (`promised_by=['always']`, verificado sobre `ASSET_CATALOG`).

```
asset_specs medidos: [('analytics_setup_guide', ['no_analytics_configured']),
                      ('indirect_traffic_optimization', ['low_organic_visibility']),
                      ('llms_txt', ['ai_crawler_blocked']),
                      ('monthly_report', [])]        ← 3/4 = 0.75 → error → is_coherent False
```

⟹ **El punto 8 no puede cerrarse solo en la capa de propuesta.** La promesa que coherence
audita vive en la capa de **assets**. Esta es la tercera aplicación de
*«revalidar citas de código no revalida premisas»* en este plan (tras S-B7 y la nota de A5).
El prompt de fase no lista `v4_asset_orchestrator.py` entre los archivos afectados de C2/C3:
**alcance ampliado por evidencia**, registrado como **S-C1** para `10-analisis` §5.

---

## 1. Fuente única

La promesa deriva de **dos** fuentes canónicas y de ninguna otra:

| Capa | Fuente | Qué aporta |
|---|---|---|
| Identidad | `modules/common/service_identity.py` → `SERVICE_IDENTITIES` (FASE-A) | servicio ↔ asset_type ↔ pain_id (disparador) ↔ `brecha_candidates` (atribución) ↔ `counts_in_alignment` |
| Realidad del run | `pain_ledger` **resuelto** (entries con `pain_id`) | qué brechas se detectaron de verdad |
| Realidad del sitio | snapshot SitePresence normalizado | qué assets ya existen en producción |

**Regla del contrato (punto 8)**:

> Un servicio se **promete** si y solo si su identidad está en `SERVICE_IDENTITIES` con
> `counts_in_alignment=True` **Y** (al menos uno de los `pain_id` que su `asset_type` resuelve
> en `PAIN_SOLUTION_MAP` está en el ledger resuelto **O** su asset ya existe en producción).

Ninguna lista estática puede sustituir a esa derivación. En particular:

- `ALL_PROMISED_SERVICES` / `PROPOSAL_SERVICE_TO_ASSET` son el **universo de identidad**
  (qué servicios existen y en qué orden), **no** la promesa del run.
- El orden de inserción de `SERVICE_IDENTITIES` **es parte del contrato** (FASE-A): ordena las
  filas. Ninguna derivación de esta fase lo altera ni lo convierte en `set`.

### 1.1 Las tres superficies de promesa (todas deben derivar de la misma regla)

| # | Superficie | Estado antes de C | Qué hace C |
|---|---|---|---|
| 1 | Tabla de servicios de la propuesta (`_generate_dynamic_services_table`) | **ya dinámica** vía `committed_services` (FASE-SR-B / D-PF1) | conserva la regla; corrige el colapso vacío↔ausente (§4) |
| 2 | Matriz `AssetAlignmentMatrix.build` / `ProposalAssetMatrix.build` | **estática**: itera `ALL_PROMISED_SERVICES` (7) ⟹ `no_breach = 6` | itera solo lo prometido ⟹ **`no_breach = 0` por construcción** (AC5) |
| 3 | Lista de assets prometidos que audita coherence (`asset_specs`) | **estática**: D4-FIX inyecta `monthly_report` con `pain_ids=[]` ⟹ 3/4 | el complemento siempre-activo **se genera pero no se promete** ⟹ `is_coherent` sin relajar el umbral (AC6) |

Dejar cualquiera de las tres estática produce el estado intermedio prohibido por el prompt
(artefactos que se contradicen entre sí).

---

## 2. «Servicio con brecha detectada» — definición operativa

*Brecha detectada* = `pain_id` presente en el **ledger resuelto** del run
(`pain_ledger_resolved.json` / entries pasadas al builder). No basta con que el `pain_id`
exista en Capa 1 (`PAIN_SOLUTION_MAP`): Capa 1 es el universo de lo *posible*; el ledger es lo
*ocurrido*. Esta distinción es exactamente la que el dossier B1 mide como la doble falla de
mapeo: «SEO Local» promete `optimization_guide`, que se mapea desde 5 pains, y **ninguno se
detectó** en esa corrida.

La atribución de costo en la tabla sigue viniendo de `brecha_candidates` (Capa 2) cruzada con
`opportunity_scores` del run — **trigger ≠ atribución** (`REVIEWED_TRIGGER_DIVERGENCES`,
FASE-A). Este contrato **no** unifica ambos campos: los 2 divergentes (`seo_local`,
`optimizacion_ia_generativa`) siguen revisados a mano y declarados.

---

## 3. Los 2 assets huérfanos — decisión registrada

**Hecho medido** (dossier B1 + confirmado sobre el corpus): `low_organic_visibility` y
`no_analytics_configured` **sí se detectaron** y produjeron `indirect_traffic_optimization` y
`analytics_setup_guide`. Ambos assets se generan, se entregan y están **justificados** en
coherence (sus `pain_ids` sí están en el diagnóstico). Lo que no tienen es **servicio comercial**
en `SERVICE_IDENTITIES`: son huérfanos del lado de la venta, no del lado de la entrega.

**Decisión**: **NO se les crea servicio prometido y NO se deja de generarlos.** Se los
**visibiliza como asset técnico** derivado del ledger.

**Rationale**:

1. **Crear un servicio vendible es una decisión de producto/precio, no de estabilización.**
   Añadir entradas a `SERVICE_IDENTITIES` re-abre AC1/AC2 (el censo de 14 registros y los
   contract tests que lo fijan) y cambia lo que se cobra. Esta fase cura una causa estructural;
   no expande el catálogo comercial.
2. **El dossier midió que crecer el registro empeora, no mejora.** R8 (8 servicios) →
   `coverage_ratio` 0.125 con oráculo estricto; añadir `monthly_report` al registro →
   0.571 → **0.500**. La dirección de la evidencia es *no* agrandar la lista de servicios.
3. **El síntoma comercial es benigno y es el inverso del bug que se cura.** El bug de B1 es
   *vender lo no diagnosticado* (cliente paga por nada). Los huérfanos son *entregar lo
   diagnosticado sin venderlo* (cliente recibe de más). No hay daño al cliente; hay una
   oportunidad comercial no capturada.
4. **Dejar de generarlos rompería lo que sí funciona**: ambos tienen pain real, asset
   IMPLEMENTED en `ASSET_CATALOG` (`promised_by=['low_organic_visibility']` /
   `['no_analytics_configured']`) y justifican coherence. Eliminarlos bajaría
   `assets_are_justified` de 4 a 2 assets y perdería entrega real.
5. **Lo que sí se corrige ahora**: `TECHNICAL_ASSET_CATALOG` tiene **1 sola entrada**
   (`analytics_setup_guide`) desde `9623a44`, y `_generate_technical_assets_table` la recorre
   **incondicionalmente** (`v4_proposal_generator.py:1625`) — una cuarta superficie de promesa
   estática. Se (a) incorpora `indirect_traffic_optimization` y (b) hace la tabla **dinámica**:
   solo muestra assets técnicos con brecha detectada o asset generado. Esto resuelve **S-B10**
   en la dirección que la evidencia indica (re-incorporar el asset, no aggiornar el test a la
   baja) y cierra el costado simétrico de la causa raíz.

**Seguimiento que queda abierto** (no es de esta fase): decidir si `indirect_traffic_optimization`
y `analytics_setup_guide` merecen servicio comercial propio con precio. → **S-C2** para
`10-analisis` §5, dueño sugerido: post-tribunal / ROADMAP §7.2.

---

## 4. Ledger vacío — comportamiento definido (no implementado en el gate)

**Regla**: *vacío ≠ ausente*. Es la lección SR-H2 (familia D6/L-SR5) aplicada a la promesa.

| Entrada | Significado | Comportamiento |
|---|---|---|
| `pain_ledger is None` | el caller **no suministró** ledger (ruta legacy) | modo legacy: catálogo estático. Se conserva para no romper consumidores sin ledger |
| `pain_ledger == []` | el ledger **se suministró y está vacío** | **0 servicios comprometidos.** La propuesta NO promete los 7 por defecto ni se queda muda: renderiza el estado explícito «sin brechas detectadas» y remite a onboarding |

**Por qué importa**: hoy `v4_proposal_generator._derive_committed_services:1201` hace
`if not pain_ledger: return None` y `publication_gates.py:997` hace `if pain_ledger:` — **ambos
colapsan vacío con ausente**. Con ledger vacío el sistema cae al catálogo estático y vuelve a
prometer los 7: exactamente la enfermedad que el punto 8 cura. Corregir ese colapso **sí** es
alcance de C (es la regla de promesa); **no** lo es cambiar el veredicto del gate.

**Interacción explícita con V9** (que FASE-G cierra): con 0 servicios comprometidos,
`actionable_total = 0` y `coverage_ratio` toma la rama `1.0` (`alignment_result.py:269`,
«nada comprometido → nada puede estar faltante»), y `publication_gates.py:1015-1030` devuelve
**PASS trivial**. Ese PASS es la **escotilla V9**: un ledger vacío no debe pasar como PASS sino
como BLOCKED (o enrutarse a `tier_c_onboarding_required`).

> **C1 DEFINE, G4 IMPLEMENTA.** Esta fase hace el caso **visible** (log + estado en la matriz y
> en la propuesta) y deja el veredicto intacto. Cerrar la escotilla aquí violaría la restricción
> explícita del prompt («NO cerrar las escotillas V5/V9 del `_coverage_gate` — FASE-G»).

---

## 5. «Presencia en producción» — qué significa y qué NO se unifica

Un servicio cuyo asset **ya existe en el sitio en producción** se promete igual que uno con
brecha detectada: el cliente lo recibe, no hay deuda de entrega. Es la mitad (b) de la regla de
FASE-SR-B (D-PF1) y se conserva.

**Criterio canónico consumido**: `is_present_in_production(status)` de
`modules/asset_generation/site_presence_checker.py` — acepta `exists` **y** `exists_with_issues`
(FASE-SR-E, H7/L-SR3: los campos faltantes de un asset presente son mejora sugerida, no brecha).

⚠️ **El oráculo de presencia es DOBLE (A4/V15) y aquí NO se unifica** — la unificación es
FASE-F. Las dos implementaciones vigentes se consumen tal cual:

| Función | Archivo | Formas que acepta |
|---|---|---|
| `_presence_exists()` | `proposal_asset_alignment.py:432-466` | dict normalizado `{"results": {...}}`, dict plano, objeto con `.results` |
| `_presence_resolved()` | `alignment_result.py:62-76` | **solo** dict normalizado plano `{asset_type: {"status": ...}}` |

Ambas delegan en el mismo predicado `is_present_in_production`, pero divergen en la
**normalización de entrada**. Consecuencia conocida y **no corregida aquí**: un snapshot en forma
de objeto puede resolver presencia en la matriz y no en el `AlignmentResult`. FASE-F lo unifica;
`details.missing_count` vs conteo de matriz dejan de divergir allí (AC10). Registrar en el delta
que C mide con `site_presence_report = None` (el corpus no lo persiste — A2 es FASE-E), así que
esta divergencia **no afecta** la medición de C.

---

## 6. Lo que este contrato NO propone (límites explícitos)

- ❌ **NO cambiar el denominador de `coverage_ratio`.** Es un interruptor global que bloquea en
  10/10 configuraciones medidas (dossier §8.5, B4) y es insatisfacible por medios honestos:
  bajo S2.3 el rango en las 10 es 0.125–0.714 y ninguna alcanza 0.8. El veredicto bloqueante
  queda donde está: en `unresolved`. Con punto 8, `no_breach = 0` ⟹ `actionable_total ==
  promised_services_total` ⟹ **los denominadores convergen solos**, sin tocar la fórmula.
- ❌ **NO implementar S2.3.**
- ❌ **NO agregar el 8º servicio** al registro (`monthly_report` con
  `counts_in_alignment=True`): empeora coverage 0.571 → 0.500 y en coherence cuesta +0.0000
  exacto (medido, B5).
- ❌ **NO unificar el oráculo de presencia** (A4) — FASE-F.
- ❌ **NO tocar `_coherence_gate`** (`publication_gates.py:458`) **ni la semántica del campo
  `is_coherent`** — FASE-F (N11/P9). C cambia **la lista de assets que se le audita**, no el
  check ni el umbral.
- ❌ **NO relajar el umbral de coherence 0.8.** AC6 se cierra eliminando la promesa estática que
  fabrica el error, no moviendo el palo.
- ❌ **NO cerrar V5/V9** — FASE-G.

---

## 7. Invariantes que C debe preservar (y testear)

| Invariante | Dónde | Por qué |
|---|---|---|
| `effective_total + unresolved + no_breach == promised_services_total` | `alignment_result.py:101-102` | Con `no_breach = 0` la identidad pasa a ser `effective_total + unresolved == total`. Se testea **como identidad**, no como valores fijos (L-NC10) |
| `AlignmentResult.compute_unresolved()` es el **único** cómputo de «sin cubrir» | `alignment_result.py:175-212` | FASE-SR-A N1: sin sumas paralelas. Ningún builder nuevo puede contar unresolved por su lado |
| El orden de inserción de `SERVICE_IDENTITIES` ordena las filas | `service_identity.py:68-70` | FASE-A: el orden es contrato |
| Los **dos** builders de matriz quedan idénticos | `proposal_asset_alignment.py:574` y `:747` | **Trampa A5**: son idénticos en 5/5 variantes medidas; tocar uno re-introduce el drift |
| El skip de servicio desconocido es **visible** | `:609-612` y `:792-794` | «Unknown service — skip silently» da Δ = 0 y hace parecer que el cambio no hizo nada |
| La narrativa se **deriva** de la fuente, no se duplica | L-NC4 / L-NC10 | Prohibido crear una tabla paralela `pain_id → texto` |

---

## 8. Criterio de cierre de C1

- [x] Fuente única declarada (§1) y las 3 superficies de promesa identificadas (§1.1)
- [x] Definición operativa de «brecha detectada»: ledger resuelto, no Capa 1 (§2)
- [x] Decisión sobre los 2 huérfanos con rationale de 5 puntos (§3) + seguimiento S-C2
- [x] Ledger vacío definido con la regla *vacío ≠ ausente* e interacción explícita con V9 (§4)
- [x] «Presencia en producción» definida; oráculo doble señalado y **no** unificado (§5)
- [x] NO propone cambiar el denominador de `coverage_ratio` (§6)
- [x] Premisa de B5 corregida por medición, no por lectura (§0) → S-C1
