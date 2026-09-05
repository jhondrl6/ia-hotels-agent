# FASE-C — Punto 8: propuesta dinámica (cura estructural)

**ID**: ESTABILIZACION-PRE-TRIBUNAL-2026-09-03 / FASE-C
**Objetivo**: Que la propuesta comercial **solo prometa servicios con brecha detectada**. Hoy promete
los 7-8 servicios del registro haya o no brecha, lo que produce `no_breach = 6/7` y hace que
`coverage_ratio = 1.000` sea algebraico. Con propuesta dinámica, `no_breach = 0` **por construcción** ⟹
`total == actionable` ⟹ los denominadores convergen y se disuelven la tautología de coverage **y** el
`is_coherent = false` estructural (B5).
**Dependencias**: FASE-A ✅ (registro canónico), FASE-B ✅ (biyección triple mapa↔emisión↔narrativa)
**Duración estimada**: 6-9 horas
**Complejidad técnica**: **MÁXIMA**
**Modo de ejecución**: **DIRECTO** (no delegable)
**Skill**: `phased_project_executor.md` v2.18.0
**Presupuesto**: ≤60 iteraciones (**tope R2**)
**ACs que cierra**: AC5, AC6

---

## Contexto

El dossier §8.5 lo dice sin ambigüedad:

> *"**No tratar el punto 8 como opcional.** La causa raíz es que la propuesta es **estática**: promete
> los 7-8 servicios del registro haya o no brecha detectada. Una **propuesta dinámica que solo prometa
> servicios con brecha detectada** hace `no_breach = 0` por construcción ⟹ `total == actionable` ⟹ los
> denominadores convergen y toda la discusión anterior se disuelve. Advisory es un parche legítimo;
> el punto 8 es la cura."*

ROADMAP v4.2 §7.2 lo registra como *"Causa raíz por debajo de T0"*. Es la **precondición dura nº 1**
del tribunal (dossier §10).

### Precedente crítico: la cura ya se prescribió una vez y NO se ejecutó

QMind `CONTEXT-H Zione 2026-07-23`: la Fase 3 del plan de ataque Zione ("propuesta condicional") decía
*"`_generate_dynamic_services_table()`: excluir servicios sin asset generado y sin presencia en
producción"*, y su CAPA 1 ya diagnosticaba *"promete 8 servicios siempre... el Gate 9 es el
sintomizador, no la causa"*. **La Fase 3 no se ejecutó.**

El fenómeno NO_BREACH-hueco es **cross-hotel**: en Zione 2 de 8 servicios prometidos eran promesas
vacías (SEO Local, Open Graph). Eso refuerza B1: es *"por construcción del mapper, no por los datos del
hotel"*.

⟹ **Esta fase existe para cerrar una deuda de dos meses.** Si vuelve a quedarse a medias, el hallazgo
se repetirá en el tercer hotel.

### El mecanismo causal medido (dossier §9.2, B1-B5) — insumo directo

**B1 — La matriz real de SalenteReal, entrada por entrada.** 7 servicios: **6 NO_BREACH + 1 LINKED**,
`delivery_ready: True`.

| Servicio prometido | `asset_type` | Estado | conf | `pain_ids` |
|---|---|---|---|---|
| SEO Local | `optimization_guide` | NO_BREACH | 0.0 | `[]` |
| Botón de WhatsApp | `whatsapp_button` | NO_BREACH | 0.0 | `[]` |
| Schema Hotel | `hotel_schema` | NO_BREACH | 0.0 | `[]` |
| Schema Organization | `org_schema` | NO_BREACH | 0.0 | `[]` |
| Página de FAQ | `faq_page` | NO_BREACH | 0.0 | `[]` |
| Meta Tags Sociales (Open Graph) | `open_graph` | NO_BREACH | 0.0 | `[]` |
| **Optimización para IA Generativa** | `llms_txt` | **LINKED** | 1.0 | `["ai_crawler_blocked"]` |

El ledger resuelto tiene **exactamente 3 entradas**, las tres MEDIUM y ASSET_GENERATED:
`no_analytics_configured`, `low_organic_visibility`, `ai_crawler_blocked`.

**La doble falla de mapeo (causa raíz):**
- `low_organic_visibility` **sí se detectó** y produjo `indirect_traffic_optimization`
  (`pain_solution_mapper.py:179`; `asset_catalog.py:300-313` IMPLEMENTED) — pero **ningún servicio
  prometido mapea a ese asset**: es un **huérfano**. Se genera, se entrega y no responde a nada vendido.
- `no_analytics_configured` produjo `analytics_setup_guide` — **segundo huérfano**, mismo mecanismo
  (`pain_solution_mapper.py:170`).
- "SEO Local" promete `optimization_guide`, que se mapea desde **5 pains** (`poor_performance`,
  `metadata_defaults`, `low_citability`, `low_content_length`, `low_seo_score`; corrección C6) —
  **ninguno se detectó** en esa corrida. El servicio prometido queda NO_BREACH.

⟹ *"El registro promete por pains que no aparecieron, y los pains que aparecieron producen assets que
nadie promete."* De 4 assets generados, **2 son huérfanos** y 1 (`monthly_report`) no tiene pain.

**Simetría estructural con las 8 caídas de §4 (no deduplicar)**: las 8 caídas son producción de módulos
que nunca se convierte en pain; los 2 huérfanos de B1 son pains que producen assets que nadie promete.
**El pipeline pierde información en ambos costados del mapper** — la simetría es el hallazgo.

**B2 — Brecha runtime vs estática.** El registro estático está **completo: 7/7 con asset implementado**.
El problema **no es el registro**. En runtime se generan **4 assets**
(`asset_generation_report.json`: `analytics_setup_guide` WARNING, `indirect_traffic_optimization`
WARNING, `llms_txt` PASSED, `monthly_report` PASSED; `total_assets = 4`, `estimated = 2`,
`delivery_ready_percentage = 100.0`) y la **intersección prometido ∩ generado = {`llms_txt`}** — un solo
elemento. `monthly_report` se genera pero **no está en el registro** (comentado en
`proposal_asset_alignment.py:27-29`, FASE-3 BUG-10).

⚠️ **Falso positivo ya cometido por esta misma auditoría** (§9.5 #3): quien confunda "registro completo"
con "cobertura real" llega a la conclusión opuesta. No repetir.

**B4 — Palancas medidas.** Bajo el régimen actual `coverage_ratio = 1.000` **en las 10 configuraciones**
(tautología, §8.3). Bajo S2.3 (denominador = `promised_services_total`):

| Configuración | coverage bajo S2.3 |
|---|---|
| Rango en las 10 (5 registros × 2 oráculos) | **0.125 – 0.714** |
| Registro actual (7), oráculo permisivo | **0.571** (4/7) |
| Registro actual + S1.2 (añadir `monthly_report`) | **0.500** — *empeora*, porque `no_monthly_report` no se detecta |
| **R8c** (remapear "SEO Local" → `indirect_traffic_optimization`) | **0.714** (5/7) — única palanca que sube |
| R8 (8 servicios), oráculo estricto | **0.125** |

- **S2.3 bloquea en las 10** (ninguna alcanza 0.8) ⟹ por eso §8.5 lo descarta
- `unresolved = 0` y **G9 = PASS en las 10** ⟹ S2.4 no tiene efecto alguno
- **Ninguna variante de registro llega a 1.0 sin punto 8.** La mejor (R8c) se queda en 0.714

**B5 — Δcoherence medido, y por qué es cero.** Añadir `monthly_report` (7→8) da **+0.0000 exacto** por
dos candados independientes: (1) la rama de éxito hardcodea `score=1.0`
(`coherence_validator.py:689-700`) y el tamaño del registro solo entra al mensaje; (2) la rama de fallo
usa una **UNIÓN** (`:703`, `total_checked = len(promised_types | set(PROPOSAL_SERVICE_TO_ASSET.values()))`)
y `monthly_report` ya está en `promised_types` ⟹ la unión vale 10 para R7 y para R8.

**Datos de sensibilidad si se toca coherencia**: pesos en `coherence_validator.py:101-108`
(1.5/1.0/1.5/0.5/1.0/**2.0**, total **7.5**) ⟹ sensibilidad 0.2667 por unidad; headroom actual **0.08**;
score mínimo de un check para mantener overall ≥ 0.8 = **0.7000** (M=3 de 10 faltantes).

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A — Fuente única de identidad | ✅ Completada |
| FASE-B — Biyección triple mapa↔emisión↔narrativa | ✅ Completada |

### Base Técnica Disponible

- **Registro canónico** de FASE-A — la promesa debe derivar de él, nunca de una copia
- **Biyección fija** de FASE-B — los pains que se emiten son exactamente los declarados
- **Corpus de referencia**: `output/FASE-D_salentoreal_post_guard/v4_complete/hotelsalentoreal/v4_audit/`
  (corrida 2026-08-31 12:28:03, re-verificada 2026-09-02)
- **Baseline de tests de alignment/gates**: 140 passed, 1 skipped, 8 warnings en ~1.23s sobre los 7
  archivos de tests de alignment/gates (141 tests, 32 asserts de bloqueo) — dossier §8.6
- **Costo esperado declarado**: ~6 tests específicos de alignment a actualizar. **No hay candados en
  `tests/regression/` ni `tests/e2e/`**

---

## Tareas

### Tarea C1: Contrato de propuesta dinámica

**Objetivo**: Especificar qué significa «servicio con brecha detectada» y de qué fuente única deriva.
Definir el comportamiento cuando el ledger está vacío (interacción con **V9**, que FASE-G cierra).

**Archivos afectados**: ninguno (diseño) + salida nueva `evidence/FASE-C/contrato-propuesta-dinamica.md`

**Criterios de aceptación**:
- [ ] El contrato declara la fuente única: el registro canónico de FASE-A + el `pain_ledger` resuelto
- [ ] Define qué pasa con los **2 assets huérfanos** de B1 (`indirect_traffic_optimization`,
      `analytics_setup_guide`): ¿se les crea servicio prometido, o se deja de generarlos? **Decisión
      registrada con rationale** — es el costado simétrico de la causa raíz
- [ ] Define el comportamiento con **ledger vacío**: la propuesta no puede quedar sin servicios ni
      prometer los 7 por defecto. Interacción explícita con V9 (ledger vacío PASS vs BLOCKED)
- [ ] Define qué significa «presencia en producción» para excluir un servicio (el precedente Zione decía
      *"excluir servicios sin asset generado **y** sin presencia en producción"*) — y señala que el
      oráculo de presencia es **doble** (A4) y se unifica en FASE-F, por lo que aquí se consume el
      existente sin unificarlo
- [ ] **NO propone cambiar el denominador de `coverage_ratio`**: es un interruptor global que bloquea en
      10/10 configuraciones medidas y es insatisfacible por medios honestos. El veredicto bloqueante
      queda en `unresolved`
- [ ] Salida escrita en `evidence/FASE-C/contrato-propuesta-dinamica.md`

### Tarea C2: Implementar en la propuesta

**Objetivo**: `service_brecha_candidates` derivado del ledger real, no de la lista estática.

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py:1281-1289` (`service_brecha_candidates`)
- `modules/commercial_documents/v4_proposal_generator.py:1332` (drift «8 vs 7», si FASE-A no lo cerró del todo)
- `modules/commercial_documents/templates/propuesta_v6_template.md` (`${dynamic_services_table}` en `:52`)
- `modules/commercial_documents/v4_diagnostic_generator.py` (sección de servicios, si deriva de la misma lista)

**Criterios de aceptación**:
- [ ] La tabla de servicios de la propuesta se genera **solo** con servicios cuya brecha está en el ledger
- [ ] `_generate_dynamic_services_table()` (o equivalente) excluye servicios sin asset generado **y** sin
      presencia en producción — cerrando el precedente Zione Fase 3 que nunca se ejecutó
- [ ] **Narrativa derivada de la fuente, no duplicada** (L-NC10 / L-NC4): el texto de cada fila sale del
      registro canónico; no hay una tabla paralela de pain_id→texto
- [ ] El título y los contadores de la propuesta son dinámicos (precedente FASE-R0-B: `LAS {N} FUGAS`)
- [ ] Tests de contrato narrativa↔fuente (no valores fijos)

### Tarea C3: Propagar a matriz y gate

**Objetivo**: `no_breach` deja de ser categoría poblada. `AlignmentResult.compute_unresolved()` sigue
siendo el **único** punto de cómputo.

**Archivos afectados**:
- `modules/asset_generation/proposal_asset_alignment.py:575` (`build` del primer builder), `:609-612` (skip silencioso), `:748` (segundo builder), `:792-794` (segundo skip)
- `modules/quality_gates/alignment_result.py:62` (`_presence_resolved`), `:106-108` (`passed`), `:175-212` (`compute_unresolved`), `:222-276` (`_from_entries`), `:282`, `:332`
- `modules/quality_gates/publication_gates.py:842` (`_proposal_asset_alignment_gate`)

**Criterios de aceptación**:
- [ ] En una corrida con el registro actual, `no_breach = 0` (AC5)
- [ ] `compute_unresolved()` sigue siendo el único cómputo — **sin sumas paralelas** (FASE-SR-A N1, L-NC10)
- [ ] La identidad `effective_total + unresolved + no_breach == promised_services_total`
      (`alignment_result.py:101-102`) se preserva como invariante y queda testeada
- [ ] ⚠️ **Esquivar la trampa A5**: los **dos** builders tienen ruta de skip silencioso
      (`:609-612` comentario literal *"Unknown service — skip silently"* y `:792-794`). Un servicio que
      no esté en el registro da **Δ = 0** y parece que el cambio no hizo nada. Los dos builders son
      **idénticos en 5/5 variantes medidas** — tocar uno sin el otro re-introduce el drift
- [ ] El skip silencioso pasa a ser **visible** (log o estado), no eliminado en silencio
- [ ] Los ~6 tests de alignment afectados quedan actualizados (costo esperado declarado en §8.6)

### Tarea C4: Medir el delta (experimento contrafactual)

**Objetivo**: Medir `no_breach`, `coverage_ratio`, `unresolved`, `effective_total` e `is_coherent`
antes/después sobre los artefactos reales de SalenteReal. **Sin este delta, AC5 y AC6 no se pueden
certificar** — y VERIFY solo certifica contra salidas reales.

**Archivos afectados**: lectura de `output/FASE-D_salentoreal_post_guard/v4_complete/` + salida nueva
`evidence/FASE-C/delta-medido.md`

**Criterios de aceptación**:
- [ ] Tabla antes/después con los 5 valores, obtenida **re-procesando los artefactos reales** del baseline
      (no de un fixture inventado)
- [ ] `no_breach`: 6 → **0** verificado
- [ ] `coverage_ratio`: documentar que deja de ser algebraicamente 1.0 y explicar el nuevo valor
- [ ] **AC6**: `is_coherent` — demostrar que el `false` estructural de B5 desaparece **por la vía del
      punto 8**, no por relajar el umbral de 0.8
- [ ] ⚠️ **P12/A3 — límite explícito de la medición**: `promised_assets_exist` pesa **2.0 de 7.5** y está
      acotado por `if not generated_assets:` (`coherence_validator.py:670`, comentario H6 FIX) ⟹
      **post-gen P6.3 no tiene verificación de score**. C4 **no puede apoyarse en ese check** para
      certificar P6.3. Declararlo en la tabla como limitación, no ocultarlo
- [ ] Salida escrita en `evidence/FASE-C/delta-medido.md`

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Invariante `effective + unresolved + no_breach == total` | `tests/quality_gates/test_alignment_result.py` | Verde; testeado como invariante, no como valor |
| Propuesta dinámica excluye servicio sin brecha | `tests/commercial_documents/test_proposal_dynamic.py` (existe, 14 tests) | Verde con ledger parcial |
| Propuesta dinámica con ledger vacío | ídem | Comportamiento definido por C1, no crash ni los 7 por defecto |
| Ambos builders idénticos (anti-A5) | `tests/asset_generation/test_proposal_asset_alignment.py` | Verde en las 5/5 variantes + el nuevo caso |
| Skip silencioso ahora visible | ídem | Falla si vuelve a ser silencioso |
| Contract tests FASE-A + biyección FASE-B | `tests/common/...`, `tests/commercial_documents/test_pain_map_bijection.py` | Siguen en verde |
| Baseline alignment/gates | 7 archivos de alignment/gates | 140 passed / 1 skipped (o delta explicado) |
| Baseline dossier §8.6 | `tests/quality_gates` + `tests/asset_generation` | 848 passed / 2 skipped + delta A/B |

**Comando de validación**:
```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/test_alignment_result.py tests/asset_generation/test_proposal_asset_alignment.py -v > temp/faseC_alignment.txt 2>&1
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_proposal_dynamic.py -v > temp/faseC_dynamic.txt 2>&1
./venv/Scripts/python.exe -m pytest tests/quality_gates tests/asset_generation -q > temp/faseC_baseline.txt 2>&1
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

⚠️ **NUNCA** correr `tests/commercial_documents` completo (~8GB).

---

## Punto de partición predefinido (no improvisar en la sesión)

Si esta fase agota las 60 iteraciones de R2, **partir** en:

- **C1'** (sesión nueva): tareas C1 + C2 — contrato y propuesta dinámica en `v4_proposal_generator`
- **C2'** (sesión nueva): tareas C3 + C4 — propagación a matriz/gate/`alignment_result` + medición del delta

Las sesiones siguientes se re-numeran y el cambio se registra en
`10-analisis-post-implementacion.md` §Decisiones Arquitectónicas **con la razón del agotamiento**.
NO dejar la fase a medio hacer: un estado intermedio donde la propuesta es dinámica pero la matriz no,
produce artefactos que se contradicen entre sí (el patrón exacto de los 3 artefactos de SalenteReal
con `is_coherent: false`).

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`** — marcar FASE-C ✅, fecha, notas
2. **`README.md` del plan** — tabla de progreso + métricas
3. **`06-checklist-implementacion.md`** — fila FASE-C, AC5/AC6, trazabilidad B1-B5, V4, A5, P12 y punto 5 del «qué NO hacer»
4. **`09-documentacion-post-proyecto.md`** — Sección A (si hay módulo nuevo), B (propuesta dinámica),
   D (métricas), E (archivos afiliados)
5. **`10-analisis-post-implementacion.md`**
   - Resumen de Ejecución: fila FASE-C (iteraciones reales — **crítico**: es la fase con riesgo de agotar R2)
   - **Decisiones Arquitectónicas**: el tratamiento de los 2 assets huérfanos; el comportamiento con
     ledger vacío; si se activó el punto de partición
   - Lecciones Aprendidas + Métricas + Seguimientos abiertos
6. **`evidence/FASE-C/`** — `contrato-propuesta-dinamica.md`, `delta-medido.md`, logs de tests

**Cierre con script**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-C --desc "Punto 8 propuesta dinamica - no_breach=0 por construccion (B1-B5)" --check-manual-docs
```
**SIN `--release`.**

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] **Tests nuevos pasan**: invariante, propuesta dinámica (incl. ledger vacío), anti-A5
- [ ] **TDD respetado**: el invariante y el test anti-A5 fueron vistos en rojo antes del fix
- [ ] **AC5 cerrado**: `no_breach = 0` por construcción, **medido** en `delta-medido.md`
- [ ] **AC6 cerrado**: `is_coherent = false` estructural disuelto por el punto 8, no por relajar el umbral
- [ ] **Los 2 builders tratados** (no solo uno)
- [ ] **El skip silencioso es visible**
- [ ] **Los 2 assets huérfanos tienen decisión registrada**
- [ ] **Limitación P12 declarada explícitamente** en la medición (no ocultada)
- [ ] **Contract tests de FASE-A y biyección de FASE-B siguen en verde**
- [ ] **Baseline preservado**: 140/1 alignment + 848/2 dossier (o delta explicado)
- [ ] **Validaciones**: `run_all_validations.py --quick` 7/7
- [ ] **Los 5 archivos de plan actualizados** (dependencias, README, 06, 09, 10)
- [ ] **Evidencia preservada**: `evidence/FASE-C/` con contrato + delta medido
- [ ] **`log_phase_completion.py` ejecutado SIN `--release`**
- [ ] **Commit hecho** referenciando FASE-C

---

## Restricciones

**Alcance — qué NO está en esta fase**:
- ❌ **NO cambiar el denominador de `coverage_ratio`** — es un interruptor global, bloquea en 10/10
      configuraciones medidas. El veredicto bloqueante queda en `unresolved`
- ❌ **NO implementar S2.3** (dossier §8.5)
- ❌ **NO agregar el 8º servicio** — empeora coverage (0.571 → 0.500) y en coherence cuesta +0.0000 exacto
- ❌ **NO unificar el oráculo de presencia** (A4) — FASE-F. Aquí se consume el existente
- ❌ **NO tocar la severidad de los gates** (H10) — FASE-D
- ❌ **NO tocar `_coherence_gate`** (`publication_gates.py:458`) ni `is_coherent` — FASE-F (N11)
- ❌ **NO cerrar las escotillas V5/V9 del `_coverage_gate`** — FASE-G. C1 solo **define** el
      comportamiento con ledger vacío; G4 lo implementa en el gate
- ❌ **NO tocar `VERSION.yaml`** — FASE-RELEASE
- ❌ **NO relajar el umbral de coherence 0.8** para que AC6 pase. Si `is_coherent` sigue en false tras
      el punto 8, el punto 8 está incompleto — no el umbral mal puesto

**Restricciones técnicas**:
- Python del venv: `./venv/Scripts/python.exe`
- Pytest en lotes pequeños con salida a archivo; **nunca** `tests/commercial_documents` completo
- **Revalidar premisas contra salidas reales, no contra citas de código**: el dossier fue validado el
  2026-09-03 contra código vivo, pero esta fase re-escribe parte de ese código — las citas de §9.2
  pueden moverse. Verificar línea por línea antes de editar
- No dejar el sistema en estado intermedio (propuesta dinámica + matriz estática ⟹ artefactos que se
  contradicen)

---

## Prompt de Ejecución

```
Actúa como arquitecto de software senior en el repo iah-cli (Python, Windows, ./venv/Scripts/python.exe).

OBJETIVO: Punto 8 — propuesta dinámica. La propuesta comercial solo promete servicios con brecha
detectada. Hoy promete los 7-8 del registro haya o no brecha → no_breach = 6/7 y coverage_ratio = 1.000
algebraico. Con propuesta dinámica, no_breach = 0 POR CONSTRUCCIÓN.

CONTEXTO:
- Plan: /.opencode/plans/Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/
- Dossier §9.2 (B1-B5, mecanismo causal medido), §8.5 (punto 8 no es opcional), §12.5 Nivel 1.1
- FASE-A ✅ (registro canónico) y FASE-B ✅ (biyección) completadas
- Corpus real: output/FASE-D_salentoreal_post_guard/v4_complete/hotelsalentoreal/v4_audit/ (2026-08-31 12:28)
- Precedente NO ejecutado: CONTEXT-H Zione 2026-07-23 Fase 3 "_generate_dynamic_services_table()" —
  esta fase cierra esa deuda de dos meses
- Baseline tests alignment/gates: 140 passed / 1 skipped (7 archivos); ~6 tests a actualizar

TAREAS:
1. C1 Contrato: qué es «servicio con brecha detectada», fuente única, tratamiento de los 2 assets
   huérfanos (indirect_traffic_optimization, analytics_setup_guide), comportamiento con ledger vacío,
   qué significa «presencia en producción». Salida: evidence/FASE-C/contrato-propuesta-dinamica.md
2. C2 Implementar en v4_proposal_generator.py:1281-1289 (service_brecha_candidates) +
   modules/commercial_documents/templates/propuesta_v6_template.md (${dynamic_services_table}).
   Narrativa derivada, no duplicada.
3. C3 Propagar a proposal_asset_alignment.py:575/:609-612/:748/:792-794 (LOS DOS builders),
   alignment_result.py:62/:106-108/:175-212/:222-276, publication_gates.py:842.
   Invariante effective+unresolved+no_breach==total testeada. Skip silencioso → visible.
4. C4 Medir el delta contrafactual sobre los artefactos REALES: no_breach, coverage_ratio, unresolved,
   effective_total, is_coherent antes/después. Salida: evidence/FASE-C/delta-medido.md

CRITERIOS:
- AC5: no_breach = 0 por construcción, MEDIDO (6 → 0)
- AC6: is_coherent=false estructural disuelto por el punto 8, NO por relajar el umbral 0.8
- compute_unresolved() sigue siendo el único cómputo (sin sumas paralelas, L-NC10)
- Baseline 140/1 + 848/2 preservado o delta explicado; run_all_validations.py --quick 7/7

RESTRICCIONES (críticas):
- NO cambiar el denominador de coverage_ratio (interruptor global, bloquea en 10/10 medidas)
- NO implementar S2.3; NO agregar el 8º servicio (empeora 0.571→0.500, Δcoherence +0.0000)
- NO unificar el oráculo de presencia (A4→FASE-F); NO tocar severidad (FASE-D), _coherence_gate ni
  is_coherent (FASE-F); NO cerrar escotillas V5/V9 del _coverage_gate (FASE-G)
- NO tocar VERSION.yaml; NO relajar el umbral de coherence
- TRAMPA A5: los DOS builders tienen skip silencioso; un servicio fuera del registro da Δ=0 y parece
  que no hizo nada. Tocar uno sin el otro re-introduce el drift (son idénticos en 5/5 variantes)
- LÍMITE P12: promised_assets_exist está acotado por `if not generated_assets:`
  (coherence_validator.py:670) → post-gen P6.3 no tiene verificación de score. C4 NO puede apoyarse en
  ese check; declararlo como limitación
- NO dejar estado intermedio (propuesta dinámica + matriz estática = artefactos contradictorios)
- Pytest en lotes pequeños con salida a archivo; NUNCA tests/commercial_documents completo (~8GB)

SI AGOTAS LAS 60 ITERACIONES (R2): partir en C1' (C1+C2) y C2' (C3+C4), re-numerar sesiones y
registrar la decisión + la razón del agotamiento en 10-analisis-post-implementacion.md. NO dejar a medias.

POST-EJECUCIÓN (obligatoria):
Actualizar dependencias-fases.md, README.md, 06-checklist-implementacion.md,
09-documentacion-post-proyecto.md (A/B/D/E), 10-analisis-post-implementacion.md (iteraciones reales +
Decisiones: huérfanos, ledger vacío, partición), evidence/FASE-C/.
Luego: log_phase_completion.py --fase FASE-C --desc "..." --check-manual-docs  (SIN --release).
Commit referenciando FASE-C.
```
