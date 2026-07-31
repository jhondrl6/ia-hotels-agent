# Contexto: Brechas Post-DT-3 — Zione.co v4complete 2026-07-25

> **Origen**: Ejecución fresca de v4complete para Zione.co (2026-07-25, sesión de validación)
> **Versión actual**: v4.64.0 (DT-3 completado, tag dc303e5)
> **Hotel de referencia**: Zi One Luxury (https://zione.co/)
> **Severidad**: ALTA — delivery bloqueado por 2 capas de gates; 4 bugs nuevos no cubiertos por DT-3
> **Fecha del contexto**: 2026-07-25
> **Output de referencia**: `output/clientes/v4_complete/` (24 archivos generados, exit 0, 149s)
> **ESTADO**: VALIDADO contra código vivo — incluye correcciones a claims erróneas, 5 hallazgos amplificadores nuevos (N1-N5), causa raíz transversal y fixes recomendados.

---

## 1. Archivos fuente de esta ejecución

| Archivo | Rol |
|---------|-----|
| `output/clientes/v4_complete/v4_complete_report.json` | Reporte maestro de la ejecución |
| `output/clientes/v4_complete/BLOCKED_BY_GATES.md` | Documento de bloqueo (reemplaza diagnóstico + propuesta) — 16 líneas, solo menciona coverage |
| `output/clientes/v4_complete/zione/v4_audit/gate_report_*.json` | 11 gates de publicación |
| `output/clientes/v4_complete/zione/v4_audit/delivery_quality_report.json` | 5 gates de delivery quality (G6/G7/G8/G9 + EVIDENCE) |
| `output/clientes/v4_complete/zione/v4_audit/proposal_asset_matrix.json` | AssetAlignmentMatrix (8 entries: 5 LINKED, 1 MISSING_ASSET, 2 NO_BREACH) |
| `output/clientes/v4_complete/zione/v4_audit/asset_generation_report.json` | 10 assets generados + 1 skipped (whatsapp_button) |
| `output/clientes/v4_complete/zione/v4_audit/pain_ledger.json` | 9 pains detectados |
| `output/clientes/v4_complete/zione/v4_audit/financial_scenarios_*.json` | Escenarios financieros Tier B/C |
| `output/clientes/v4_complete/zione/v4_audit/coherence_validation.json` | Coherencia pre-gen (0.84) |
| `output/clientes/v4_complete/zione/v4_audit/coherence_validation_post_gen.json` | Coherencia post-gen (0.82) |

---

## 2. Lo que DT-3 resolvió (para no repetir)

DT-3 (v4.64.0) ejecutó 5 fases + RELEASE con estos resultados verificados:

| Bug | Fix | Evidencia en esta ejecución |
|-----|-----|-----------------------------|
| BUG-1 | Rutas flat → per-hotel (3 paths en main.py) | ✅ pain_ledger.json tiene 9 entries (ya no vacío) |
| BUG-2 | G9 no dual-list (solo en blocking_gates) | ✅ delivery_quality_report: G9 solo en blocking_gates |
| BUG-3 | G9 status-based eval (NO_BREACH=skip) | ✅ NO_BREACH no bloquea delivery |
| BUG-4 | AssetAlignmentMatrix unificado | ✅ proposal_asset_matrix.json version 2.0 |
| P-04 | Unificación ProposalAssetMatrix + AlignmentReport | ⚠️ PARCIAL — ver BUG-9 (divergencia persiste) |

**Estado del release**: v4.64.0 tagged, 100 tests PASS (86 + 14 nuevos), pre-commit hooks limpios.

---

## 3. Resumen de ejecución v4complete Zione.co

| Métrica | Valor |
|---------|-------|
| Exit code | 0 |
| Duración | 149s (~2.5 min) |
| Provider | deepseek |
| Región detectada | Eje Cafetero |
| Tier | B (datos benchmark, sin onboarding real) |
| Publication gates | 10/11 PASSED, 1 FAILED (coverage) |
| Delivery quality gates | 4/5 PASSED, 1 FAILED (G9: 5/8 aligned) |
| Commercial gates | **3 BLOCKING** (no 4 — ver §4.2) |
| Assets generados | 10 (4 PASSED, 6 ESTIMATED/WARNING) + 1 skipped |
| Archivos totales | ~24 visibles (12 v4_audit + subdirectorios) |
| Documentos cliente | ELIMINADOS → reemplazados por BLOCKED_BY_GATES.md |

---

## 4. Brechas detectadas (BUGS NUEVOS — no cubiertos por DT-3)

### 4.1 BUG-6: Coverage gate — falso positivo `no_whatsapp_visible` (CRÍTICO)

**Severidad**: CRÍTICA — bloquea delivery para cualquier hotel con WhatsApp detectado como "conflict" aunque el botón EXISTA en producción.

**Archivos afectados (verificados)**:
- `modules/quality_gates/publication_gates.py:1188` — `_coverage_gate` (L1188-1322)
- `modules/asset_generation/pain_ledger.py:20-27` — `PainLedgerEntry` con status válidos
- `modules/asset_generation/v4_asset_orchestrator.py:182-193` — `skipped_assets` con `pain_ids_affected`

**Comportamiento observado (verificado en JSON)**:
1. El sitio de Zione.co **SÍ tiene WhatsApp** verificado en producción
2. `asset_generation_report.json`: `whatsapp_button` → **skipped**, `presence_status: exists`, `site_verified: true`, `pain_ids_affected: ["no_whatsapp_visible"]`
3. `gate_report.json` §proposal_asset_alignment: `present_in_production: [{service: "Botón de WhatsApp", asset: "whatsapp_button", presence_verified: true}]`
4. `pain_ledger.json`: `no_whatsapp_visible` → confidence 0.3, status **DETECTED** (no cambia)
5. `proposal_asset_matrix.json`: `whatsapp_button` → status **MISSING_ASSET** (no ve presence_verified)
6. `gate_report.json` §coverage: 8/9 covered, `uncovered: ["no_whatsapp_visible"]` → **FAIL**
7. Resultado: delivery bloqueado, documentos cliente eliminados

**Causa raíz REAL verificada**:

El coverage gate `_coverage_gate` (publication_gates.py:1188-1322) evalúa:
```python
diagnostic_pain_ids = set(assessment.get("diagnostic_pain_ids", []))
proposal_pain_ids = set(assessment.get("proposal_pain_ids", []))
is_justified = entry.status in self._JUSTIFIED_STATUSES  # ={JUSTIFIED_SKIP, BLOCKED, MAPPED_TO_SERVICE}
```

JUSTIFIED_STATUSES = {JUSTIFIED_SKIP, BLOCKED, MAPPED_TO_SERVICE}. **No incluye "ASSET_GENERATED"** (que sí existe como status válido en `pain_ledger.py:27`).

El path del dato:
```
SitePresenceChecker (whatsapp_button EXISTS, site_verified=true)
  → conditional_generator SKIP el asset → guarda en skipped_assets
  → asset_generation_report §skipped_assets graba pain_ids_affected=[no_whatsapp_visible]
  → GAP: nadie actualiza pain_ledger §status → sigue en DETECTED
  → coverage_gate: in_diagnostic=False, in_proposal=False, is_justified=False → FAIL
```

Hay 3 sistemas que evalúan WhatsApp independientemente:
- **SitePresenceChecker**: EXISTE (verificado en HTML del sitio)
- **Coherence whatsapp_verified**: CONFLICT (confidence 0.30 < 0.9) — ver HALLAZGO-N4
- **Coverage gate**: NO CUBIERTO (no consulta presence_verified)

**Corrección al análisis original**: El análisis proponía "el coverage gate debe consultar SitePresenceChecker". Solución más precisa: **el orchestrator debe propagar `skipped_assets.pain_ids_affected` al pain_ledger cambiando status a MAPPED_TO_SERVICE o ASSET_GENERATED**. Y agregar `ASSET_GENERATED` a `_JUSTIFIED_STATUSES`.

El publication gate G9 ya tiene patrón equivalente (`_proposal_asset_alignment_gate:863-890` inyecta `site_presence_report` "fake" desde skipped_assets). Debe replicarse en pain_ledger.

**Impacto**: Cualquier hotel con WhatsApp detectado con confidence < 0.9 tendrá delivery bloqueado aunque el botón EXISTA en el sitio. Esto es un falso positivo sistémico, no un caso aislado.

**Nota histórica**: DT-3 marcó este coverage gate como "legítimo, no falso positivo" (ver `07-checklist-implementacion.md` L58). **Esa conclusión fue incorrecta**. El asset_generation_report generado en esta ejecución FRESCA demuestra que el sitio SÍ tiene WhatsApp y el pipeline lo SABE (presence_verified: true), pero el coverage gate no recibe esa información.

---

### 4.2 BUG-7: Commercial gates ocultos — 3 gates bloquean propuesta sin trace en gate_report (CRÍTICO)

**Severidad**: CRÍTICA — la propuesta comercial NUNCA se genera y el sistema no reporta estos gates en el gate_report.json

**Archivos afectados (verificados)**:
- `modules/quality_gates/commercial_gate.py` (SINGULAR, ruta correcta — el análisis original citaba mal `commercial_gates.py` en `commercial_documents/`)
- `modules/commercial_documents/v4_proposal_generator.py:38` — `CommercialGateBlockedError`
- `modules/commercial_documents/v4_proposal_generator.py:610` — raise site

**Comportamiento observado**:

3 commercial gates disparan (verificado en `commercial_gate.py:69-75`: 5 BLOCKING listados, pero CG-IA-BLOCKED-CLAIM no se valida en propuesta y CG-CLAIM-VS-EVIDENCE requiere GBP place_found=True que Zione no tiene):

| Gate | Detalle | Valor | Disparó en Zione |
|------|---------|-------|------------------|
| CG-SCENARIO-ORDER | optimistic < realistic | BLOCKING | ✅ SÍ |
| CG-SCENARIO-NEGATIVE | optimistic < 0 | BLOCKING | ✅ SÍ |
| CG-IA-BLOCKED-CLAIM | "IA Bloqueada" sin evidencia | BLOCKING | N/A (solo en diagnostic) |
| CG-ROI-NEGATIVE | **CommercialGateBlockedError** — aborta propuesta | BLOCKING | ✅ SÍ |
| CG-CLAIM-VS-EVIDENCE | Claims absolutos sin evidencia | BLOCKING | ❌ NO (place_found=False) |

**Corrección al análisis original**: El análisis citaba "4 commercial gates BLOCKING". Real: 3 disparan (CG-IA-BLOCKED-CLAIM solo se valida en `validate_diagnostic`, no en propuesta; CG-CLAIM-VS-EVIDENCE requiere `place_found=True AND gbp_rating>=4.0` para fallar — Zione sin GBP place_found no lo cumple).

**Evidencia**: Estos gates NO aparecen en `gate_report.json` (que solo contiene 11 publication gates) ni en `v4_complete_report.json`. La única evidencia es:
- El output del proceso (stdout/stderr)
- `BLOCKED_BY_GATES.md` no los menciona (solo 16 líneas, solo coverage)
- El hecho de que `01_DIAGNOSTICO_*.md` y `02_PROPUESTA_*.md` NO existen en disco

**Causa raíz REAL verificada**:

`CommercialGateBlockedError` (v4_proposal_generator.py:38) se lanza en L610:
```python
raise CommercialGateBlockedError(
    [r.gate_id for r in commercial_report.blocking_failures],
    "Proposal commercial gates BLOCKING (hidden from client)",
)
```

Excepción NO capturada → main.py atrapa genéricamente → escribe BLOCKED_BY_GATES.md desde `gate_report.json §readiness.blocking_issues` (que solo tiene publication gates).

Causa raíz doble:
1. `CommercialGateBlockedError` NO se traduce en un resultado persistido. Solo aborta.
2. `BLOCKED_BY_GATES.md` se genera desde publication gates únicamente.

**Impacto**: Sin visibilidad de commercial gates, el diagnóstico de por qué una propuesta falló es incompleto. El agente/humano solo ve "coverage gate FAIL" pero la causa real del aborto es CG-ROI-NEGATIVE.

---

### 4.3 BUG-8: Escenario financiero optimista negativo (MEDIO — semántico, no aritmético)

**Severidad**: MEDIA — bloquea CG-SCENARIO-ORDER + CG-SCENARIO-NEGATIVE + CG-ROI-NEGATIVE. Documentado en skill `iah-cli-v4complete-flow-validation` §"Scenarios Financial Logic: Optimista Can Be Negative"

**Archivos afectados (verificados)**:
- `modules/financial_engine/scenario_calculator.py:309-366` — `_calculate_optimistic_scenario()`
- `modules/quality_gates/commercial_gate.py:282-362` — `_check_scenario_order` y `_check_scenario_negative`

**Comportamiento observado (verificado en JSON)**:
```
Conservative: $7,276,954 COP/mes
Realistic:    $3,741,696 COP/mes
Optimistic:  -$270,950 COP/mes  ← NEGATIVO
```

**Causa REAL (NO es bug de cálculo, es bug de interpretación comercial)**:

El código del optimista (scenario_calculator.py:309-366) calcula:
```python
monthly_loss = current_ota_commission_loss - savings - ia_revenue
```

Con valores reales de Zione: $7.7M OTA loss - $774K savings - $3.2M IA revenue = **-$270K**. **Eso NO es bug de cálculo — es matemáticamente correcto**: "los ahorros + IA revenue SUPERAN la pérdida actual" = sin pérdida neta = escenario optimista funcionando al máximo.

**El problema REAL es la INTERPRETACIÓN COMERCIAL.** `_check_scenario_negative` (commercial_gate.py:328-362) dice "no puede mostrarse como recuperación". Y `_check_scenario_order` (L282-326) dice "optimista debe ser ≥ realista". Ambos asumen que los 3 escenarios son variantes del mismo eje (pérdida). Pero el optimista, por construcción matemática, puede caer en territorio de "ganancia neta" (paradójicamente la mejor noticia para el hotel).

**Corrección al análisis original**: El análisis proponía "`max(0, calculated)`". Esto es fix ARITMÉTICO que cambia el significado (deja de reflejar "pérdida neta negativa real"). Fix CORRECTO de causa raíz: reformular el optimista como **break-even (0)** cuando se vuelve negativo, o cambiar `_check_scenario_negative` para que valores <0 se reporten como "ROI excelente / sin pérdida neta" → WARNING en lugar de BLOCKING (Opción B recomendada).

**Impacto**: Este bug es el trigger de CG-SCENARIO-ORDER + CG-SCENARIO-NEGATIVE + CG-ROI-NEGATIVE. Si se fixea, 3 de los commercial gates se resuelven solos.

---

### 4.4 BUG-9: Divergencia publication G9 vs delivery quality G9 (MEDIO — deuda DT-3)

**Severidad**: MEDIA — dos sistemas de evaluación coexisten y reportan resultados contradictorios

**Archivos afectados (verificados)**:
- `modules/asset_generation/proposal_asset_alignment.py:439` — `ProposalAssetMatrix` (viejo)
- `modules/asset_generation/proposal_asset_alignment.py:638` — `AssetAlignmentMatrix` (nuevo DT-3)
- `modules/asset_generation/proposal_asset_alignment.py:834-846` — `aligned_count` property
- `modules/quality_gates/delivery_quality_report.py:193-225` — G9 reconstruction desde JSON
- `modules/quality_gates/publication_gates.py:803-910` — `_proposal_asset_alignment_gate`

**Comportamiento observado**:

| Sistema | Resultado | Qué cuenta |
|---------|-----------|------------|
| Publication G9 (AssetAlignmentMatrix + SitePresence directo) | **8/8 PASS** | LINKED + present_in_production |
| Delivery quality G9 (reconstruye desde JSON limitado) | **5/8 FAIL** | Solo LINKED |

`proposal_asset_matrix.json`:
```
LINKED:          optimization_guide, hotel_schema, faq_page, open_graph, llms_txt  (5)
MISSING_ASSET:   whatsapp_button  (1)
NO_BREACH:       monthly_report, org_schema  (2)
```

**Causa raíz REAL (verificada en código)**:

`proposal_asset_alignment.py:834-836`:
```python
@property
def aligned_count(self) -> int:
    """Number of LINKED services (backward compat)."""
    return sum(1 for e in self.entries if e.status == "LINKED")
```

`delivery_quality_report.py:218-219`:
```python
delivery_ready = matrix.is_delivery_ready()  # bool
aligned_count = matrix.aligned_count        # 5 (LINKED only)
total_services = matrix.total_services      # 8
```

El JSON tiene 8 entries: 5 LINKED + 1 MISSING_ASSET + 2 NO_BREACH. **No tiene campo `present_in_production` separado.** El publication gate G9 ve 8/8 porque llama `verify_proposal_asset_alignment` que SÍ considera `present_in_production` (SitePresence directo). Los 2 present_in_production (Botón WhatsApp, Schema Organization) son del gate, no del JSON.

Hay DOS sistemas G9:
- (a) `_proposal_asset_alignment_gate` (publication_gates.py:803+): ve SitePresence directo. 8/8.
- (b) `delivery_quality_report._evaluate_alignment` (delivery_quality_report.py:193-225): reconstruye `AssetAlignmentMatrix` desde JSON limitado. 5/8.

**Corrección al análisis original**: El análisis decía "delivery_quality_report aún consume ProposalAssetMatrix desde proposal_asset_matrix.json, que solo cuenta LINKED". Refinamiento: ya CONSUME el objeto nuevo (AssetAlignmentMatrix), pero el JSON que reconstruye tiene status limitado. Falta que `AssetAlignmentMatrix.save()` guarde TODOS los status enrichecidos (incluyendo `present_in_production`) en el JSON.

**Nota**: Este bug YA estaba documentado en DT-3 como "discrepancia... fuera de alcance DT-3". Esta ejecución confirma que persiste.

---

### 4.5 BUG-10: AssetSemantics — monthly_report sin pain_ids resueltos (BAJO — decisión de producto, no bug)

**Severidad**: BAJA — no bloquea delivery pero infla conteo de assets

**Archivos afectados (verificados)**:
- `modules/asset_generation/pain_solution_mapper.py:60-78` — `no_whatsapp_visible → whatsapp_button` (no `monthly_report`)
- `modules/asset_generation/monthly_report_generator.py:1-60` — genera desde `hotel_data`, ignora pain_ledger

**Comportamiento observado**:
- `asset_generation_report.json`: `monthly_report` → `pain_ids_resolved: []` (vacío)
- `proposal_asset_matrix.json`: `monthly_report` → status `NO_BREACH`, confidence 0.0
- `pain_ledger.json`: `monthly_report` no tiene pain asociado en el ledger

**Causa raíz REAL (verificada y refutada)**:

`monthly_report` NO tiene pain asignado por diseño. Se genera rutinariamente como asset "always-on" (reporting mensual, no solución a un pain). En `pain_solution_mapper.py` no hay mapping para `monthly_report → pain_id`.

**Corrección al análisis original**: El análisis proponía "PainSolutionMapper no debe asignar assets a pains inexistentes". Eso es lo que YA HACE correctamente. La pregunta real no es el bug sino de producto: **¿debería `monthly_report` contar como 1 de los 8 servicios prometidos (reduciendo "alignment" porque no resuelve nada) o excluirse de la matriz por no estar pain-driven?**

**Recomendación**: Excluirlo de `PROPOSAL_SERVICE_TO_ASSET` — `monthly_report` se entrega como anexo del servicio principal, no se factura por separado.

**Impacto cosmético**: Aparece como `NO_BREACH` en la matriz sin valor comercial real.

---

### 4.6 Warnings no bloqueantes (documentar, no priorizar en plan)

| Issue | Detalle |
|-------|---------|
| PageSpeed API | Key inválida para Google PageSpeed |
| SerpAPI | No configurada — featured snippets en stub |
| ANTHROPIC_API_KEY | No configurado (no bloquea) |
| WEBDRIVER_PATH | No configurado (no bloquea) |
| Rooms subestimado | 10 rooms asumidos para hotel con 2 ubicaciones (Cartagena + Pereira) |
| ADR benchmark | $420K COP es regional, no dato real del hotel |

---

## 5. HALLAZGOS AMPLIFICADORES NUEVOS (N1-N5)

### HALLAZGO-N1: Dos gates "coverage" diferentes con mismo nombre

- Publication **G11 coverage** (`publication_gates.py:1188`): pain_ledger + diagnostic_pain_ids + proposal_pain_ids.
- Delivery quality **G7 coverage** (`delivery_quality_report.py:356-384`): `failure_rate < 0.5` desde asset_generation_report.

Mismo nombre, diferente contrato. Cliente ve solo el G11 FAIL. Internamente son 2 gates independientes. Para Zione: G7 PASS, G11 FAIL.

Recomendación: renombrar uno. Ej: `coverage_no_silent_drop` (publication) vs `coverage_failure_rate` (delivery).

### HALLAZGO-N2: ASSET_GENERATED falta en _JUSTIFIED_STATUSES

`pain_ledger.py:27` define status válidos: `DETECTED | DIAGNOSED | MAPPED_TO_SERVICE | ASSET_GENERATED | JUSTIFIED_SKIP | BLOCKED`.

`publication_gates.py:1186` define `_JUSTIFIED_STATUSES = {JUSTIFIED_SKIP, BLOCKED, MAPPED_TO_SERVICE}` — **falta ASSET_GENERATED**.

Si el orchestrator actualizara pain→ASSET_GENERATED cuando se genera un asset resolviéndolo, el coverage gate seguiría fallando. Bloquea también FIX-PRIORITY-1.

Fix complementario obligatorio: agregar ASSET_GENERATED a `_JUSTIFIED_STATUSES`.

### HALLAZGO-N3: `whatsapp_conflict` cubierto pero `no_whatsapp_visible` no

pain_ledger.json: 9 entries. Coverage: 8 covered, 1 uncovered=[no_whatsapp_visible]. `whatsapp_conflict` SÍ está covered vía `whatsapp_conflict_guide` (asset_generation_report L25-28: pain_ids_resolved=[whatsapp_conflict]).

Pero en proposal_asset_matrix, el service "Botón de WhatsApp" sigue MISSING_ASSET porque agrupa ambos pains en una entry. La entry "Botón de WhatsApp" referencia `pain_ids: [no_whatsapp_visible, whatsapp_conflict]` pero el asset `whatsapp_button` se skipea. El coverage gate ignora esto porque el diagnostic generator sí menciona `whatsapp_conflict` pero no `no_whatsapp_visible` en el BRECHA list (el sitio SÍ tiene botón).

### HALLAZGO-N4: Coherence check `whatsapp_verified` con score 0.3

`coherence_validation.json` (vía asset_generation_report §coherence_report):
```json
"whatsapp_verified": {"score": 0.3, "message": "WhatsApp con confidence insuficiente (0.30) - requiere >= 0.9"}
```

`coherence_score=0.84` global PASS (pesos CHECK_WEIGHTS: whatsapp_verified=0.5, suma menor). Pero SitePresenceChecker SÍ sabe que el sitio tiene WhatsApp. El check no se beneficia de ese dato.

Causa raíz probable: `_check_whatsapp_verified()` lee `assessment.whatsapp_confidence` que se computa ANTES de SitePresenceChecker. Mismo patrón "ghost module / signature-only wiring".

Fix: hacer que `coherence_validator._check_whatsapp_verified()` consulte `site_presence_report.whatsapp.presence_status == "exists"` y aumente confidence a 0.9+ cuando aplique.

### HALLAZGO-N5: BLOCKED_BY_GATES.md instruye re-ejecución idéntica sin mencionar commercial gates

El archivo `BLOCKED_BY_GATES.md` (verificado en disco) tiene 16 líneas. Solo menciona:
- Hotel/URL/Status
- 1 gate fallido (coverage)
- 1 línea: "Resuelva los issues listados arriba y vuelva a ejecutar: python main.py v4complete --url https://zione.co/"

Ningún rastro de los 3 commercial gates que abortaron. Si el cliente lo ejecuta sin tocar nada, falla idénticamente. Esto se combina con BUG-7 — el cliente recibe un mensaje accionable falso.

---

## 6. Causa raíz transversal (cross-cutting)

**El sistema tiene 3 fuentes de verdad DIFERENTES para "este pain está resuelto?":**

1. **pain_ledger[]** (status: DETECTED/DIAGNOSED/MAPPED_TO_SERVICE/ASSET_GENERATED/JUSTIFIED_SKIP/BLOCKED) — `pain_ledger.py:20-27`
2. **proposal_asset_matrix.json** (status: LINKED/MISSING_ASSET/NO_BREACH/GENERIC_DRAFT) — `proposal_asset_alignment.py:419-436`
3. **skipped_assets[]** (presence_status: exists/redundant/exists_with_issues) — `v4_asset_orchestrator.py:182-193`

Publication G9 reconcilia 1+3 (inyecta site_presence_report fake desde skipped_assets, L863-890). Coverage G11 solo lee 1. Delivery quality G9 lee 2 sin enriquecer con 1 ni 3.

**Ningún punto central del código es la fuente única de verdad post-orquestador.**

**Causa raíz transversal**: falta un **reconciliador post-orchestrator** que, después de generar assets + skippearlos por presencia, ACTUALICE el pain_ledger con el estado final correcto:
- Marca pain como `ASSET_GENERATED` cuando hay asset generado con pain_ids_resolved no vacío
- Marca pain como `MAPPED_TO_SERVICE` cuando hay asset skipeado por presencia con pain_ids_affected
- Marca pain como `JUSTIFIED_SKIP` cuando el sitio ya tiene la feature (sin pain real)

Y los gates leen solo el pain_ledger actualizado. **Ese único fix resuelve BUG-6 + BUG-9 + HALLAZGO-N2 + HALLAZGO-N4.**

---

## 7. Lecciones aprendidas de DT-2 y DT-3 (para no repetir errores)

### 7.1 ¿Qué funcionó bien? (replicar)

| Patrón | Evidencia | Aplicar en DT-4 |
|--------|-----------|-----------------|
| delegate_task para ediciones localizadas | FASE-0 y FASE-1 de DT-3: ~4 min c/u, exit 0 | Bugs de <20 líneas en un solo archivo → delegar |
| Tests como red de seguridad | 86→100 tests, 0 regresiones en DT-3 | Todo fix debe incluir test que capture el bug |
| v4complete como verificación E2E | Confirmó 4 bugs superados en DT-3 | Ejecutar v4complete post-fix para Zione |
| Pre-commit hooks | version_consistency_checker + sync_versions limpiaron | Commit frecuente, verificar hooks |
| MIXTO: v4complete delegado + análisis directo | FASE-3 DT-3: 2 min runtime, análisis requirió agente principal | Mismo patrón para verificación post-fix |

### 7.2 ¿Qué se haría diferente? (no repetir)

| Error | Contexto | Prevención en DT-4 |
|-------|----------|---------------------|
| DT-3 marcó coverage gate como "legítimo" cuando era falso positivo | FASE-3 checklist L58: "(no_whatsapp_visible uncovered) — legítimo, no falso positivo" | **Verificar contra asset_generation_report.skipped_assets + SitePresenceChecker** antes de declarar un coverage FAIL como legítimo |
| Delivery quality G9 no migrado a AssetAlignmentMatrix | DT-3 unificó el contrato pero no migró todos los consumidores | Si se toca un contrato, verificar TODOS los consumidores con `grep -rn` |
| Tests pasan pero el pipeline falla en runtime | BUG-1 en DT-2: paths flat pasaban tests pero fallaban con datos reales | Todo fix debe verificarse con v4complete real, no solo tests |
| README test count stale | 3038 vs 3094 real en DT-3 release | `pytest --collect-only -q | tail -1` como paso de release |

### 7.3 Anti-patrones confirmados (NUNCA hacer)

1. **NO modificar PAIN_SOLUTION_MAP sin N≥5 observaciones** en `data/hotel_observations/observations.json`
2. **NO crear un tercer sistema** cuando ya hay dos — unificar en uno solo (lección de DT-3 FASE-2)
3. **NO delegar decisiones arquitectónicas** — delegate_task solo para ediciones localizadas
4. **NO ejecutar múltiples fases en la misma sesión**
5. **NO modificar `scenario_calculator.py` basado en un solo hotel** (mismo principio que PAIN_SOLUTION_MAP) — PERO el fix de BUG-8 puede ser reinterpretación comercial sin tocar la fórmula
6. **NO confiar en que "el gate report dice todo"** — los commercial gates son invisibles en gate_report.json
7. **NO declarar "mismo nombre = mismo gate"** sin verificar el contrato — HALLAZGO-N1

---

## 8. Dependencias entre bugs (orden de ataque REVISADO)

```
[BUG-8 + BUG-7 + BUG-10] (independientes, baja/media severidad)
   |
   └── [FIX-PRIORITY-1: Reconciliador] ← causa raíz transversal
           └── resuelve BUG-6 + BUG-9 + HALLAZGO-N2 + HALLAZGO-N4
```

**Orden recomendado REVISADO** (causa raíz transversal primero):

1. **FIX-PRIORITY-1 (Reconciliador)**: causa raíz transversal — resuelve 4 issues de un solo fix
2. **FIX-PRIORITY-3 (BUG-8)**: reinterpretación comercial del optimista — 1 gate fix + 1 test
3. **FIX-PRIORITY-2 (BUG-7)**: persistir commercial gates + ampliar BLOCKED_BY_GATES
4. **FIX-PRIORITY-4 (BUG-10)**: decisión de producto sobre monthly_report
5. **FIX-PRIORITY-5**: higiene de nombres gates duplicados

Justificación del cambio: el análisis original proponía `BUG-8 → BUG-6 → BUG-9 → BUG-7 → BUG-10`. Con causa raíz transversal verificada, BUG-6 + BUG-9 + HALLAZGO-N2 + HALLAZGO-N4 son síntomas de un único problema (3 fuentes de verdad no consolidadas). El reconciliador los resuelve juntos.

---

## 9. FIXES RECOMENDADOS — Orientados a causa raíz

### FIX-PRIORITY-1 (causa raíz transversal — resuelve BUG-6 + BUG-9 + N2 + N4)

**Acciones**:
1. Crear `modules/orchestration/post_orchestrator_reconciler.py`:
   - Lee `asset_generation_report.json` (generated_assets.pain_ids_resolved + skipped_assets.pain_ids_affected)
   - Lee `pain_ledger.json`
   - Emite `pain_ledger_resolved.json` con status final por pain_id:
     - `ASSET_GENERATED` si aparece en generated_assets.pain_ids_resolved
     - `MAPPED_TO_SERVICE` si aparece en skipped_assets.pain_ids_affected (presence=exists)
     - `JUSTIFIED_SKIP` si skipped con presence=redundant
     - `DETECTED` si no se encontró en ningún asset
2. Modificar `_JUSTIFIED_STATUSES` en `publication_gates.py:1186`:
   ```python
   _JUSTIFIED_STATUSES: Set[str] = {
       "JUSTIFIED_SKIP", "BLOCKED", "MAPPED_TO_SERVICE", "ASSET_GENERATED"
   }
   ```
3. Modificar `_coverage_gate` (L1230) para leer `assessment.get("pain_ledger_resolved")` con fallback a `pain_ledger`.
4. Llamar al reconciliador desde `v4_asset_orchestrator.run()` después de la generación.
5. Modificar `coherence_validator._check_whatsapp_verified()` para consultar `site_presence_report.whatsapp.presence_status == "exists"` y aumentar confidence a 0.9+ cuando aplique.

### FIX-PRIORITY-2 (resuelve BUG-7 + HALLAZGO-N5)

**Acciones**:
1. En `v4_proposal_generator.py:610`, antes de raise `CommercialGateBlockedError`, persistir:
   ```python
   (output_path / hotel_slug / "v4_audit" / "commercial_gates_report.json").write_text(
       json.dumps(commercial_report.to_dict(), indent=2, ensure_ascii=False)
   )
   ```
2. En `main.py`, ampliar generación de `BLOCKED_BY_GATES.md` para incluir sección "🚨 Commercial Gates Bloqueantes" cuando exista `commercial_gates_report.json` con `blocking_passed: false`.
3. Remover la sugerencia de "vuelva a ejecutar" si hay commercial gates bloqueantes (la re-ejecución idéntica fallaría igual).

### FIX-PRIORITY-3 (resuelve BUG-8)

**Opción A (simple, cambia semántica — NO recomendada)**:
- En `scenario_calculator.py:354`, agregar clamp:
  ```python
  monthly_loss_cop = max(0.0, round(monthly_loss, 2))
  ```
- Nota docstring: "Optimistic scenario represents theoretical MIN of net loss; cannot be negative."

**Opción B (refactor semántico, preserva math — RECOMENDADA)**:
- Renombrar "optimistic" a "conservador-alcanzado" cuando se vuelve negativo.
- Cambiar `_check_scenario_negative` (commercial_gate.py:341) para WARNING en lugar de BLOCKING cuando `optimistic < 0` AND `realistic > 0`.

**Recomendación**: Opción B. Requiere producto-decisión: ¿queremos aceptar "sin pérdida neta" como escenario positivo?

### FIX-PRIORITY-4 (resuelve BUG-10 — decisión de producto)

**Opciones**:
- (A) Marcar `monthly_report` como `STANDALONE_ASSET` (nuevo status) y excluirlo de alignment counts.
- (B) Remover `monthly_report` de `PROPOSAL_SERVICE_TO_ASSET` — no es servicio prometido, es entrega complementaria.

**Recomendación**: (B) — más limpio. `monthly_report` se entrega como anexo, no se factura por separado.

### FIX-PRIORITY-5 (higiene — HALLAZGO-N1)

Renombrar uno de los dos `coverage`:
- `coverage` (publication G11) → `coverage_no_silent_drop`
- `coverage_gate` (delivery quality G7) → `coverage_failure_rate`

---

## 10. Criterios de verificación (para el plan)

Cada fix debe verificarse con:
1. **Test unitario** que capture el comportamiento actual (FAIL) → fix → test pasa (PASS)
2. **v4complete fresco** para Zione.co post-fix
3. **Evidencia en disco**: archivo JSON específico con el valor esperado

| Fix | Verificación | Archivo de evidencia |
|-----|-------------|---------------------|
| FIX-1 (causa raíz) | pain_ledger_resolved con ASSET_GENERATED/MAPPED_TO_SERVICE; coverage gate PASS | `pain_ledger_resolved.json` + `gate_report_*.json §coverage` |
| FIX-2 (BUG-7) | commercial_gates_report.json existe en v4_audit | `commercial_gates_report.json` |
| FIX-3 (BUG-8) | optimistic clasificado correctamente (puede ser negativo pero no BLOCKING) | `commercial_gates_report.json §results` |
| FIX-4 (BUG-10) | monthly_report excluido de alignment counts | `proposal_asset_matrix.json §entries` |
| FIX-5 (higiene) | gates renombrados sin regresión | `gate_report_*.json §gate_name` |

---

## 11. Restricciones globales (heredadas de DT-3 + nuevas)

1. Una fase = una sesión — no ejecutar múltiples fases en la misma sesión
2. pytest: `./venv/Scripts/python.exe -m pytest` (Windows venv desde WSL)
3. v4complete: `./venv/Scripts/python.exe main.py v4complete --url https://zione.co/ --output output/clientes`
4. Pre-commit: `version_consistency_checker.py` (BLOCKING) + `sync_versions.py --check` (advisory)
5. NO modificar PAIN_SOLUTION_MAP sin N≥5 observaciones
6. NO modificar scenario_calculator.py sin N≥5 observaciones (mismo principio) — PERO el fix Opción B para BUG-8 no toca la fórmula, solo interpretación comercial
7. WSL safety guard: evitar `rm -rf`, pipes con heredocs. Usar `write_file` para crear inputs.
8. WSL CRLF warnings: cosméticos, no bloquean commits
9. delegate_task: viable para ediciones ≤20 líneas en un solo archivo. NO para decisiones cross-module.
10. v4complete post-fix: patrón MIXTO (delegar ejecución, analizar directo)
11. Nuevo: NO declarar un coverage FAIL como "legítimo" sin verificar `asset_generation_report.json §skipped_assets` para confirmar que el site presence checker NO detectó el asset
12. Nuevo: rutas en código son `commercial_gate.py` (singular, en quality_gates), NO `commercial_gates.py` ni en commercial_documents/
13. Nuevo: "mismo nombre" no significa "mismo contrato" — verificar contrato antes de asumir equivalencia entre gates

---

## 12. Archivos del plan (estructura esperada para DT-4)

```
.opencode/plans/DT-4-<SLUG>-2026-07-25/
├── 01-plan-maestro.md
├── 02-prompt-fase-0.md                ← FIX-PRIORITY-1: Reconciliador post-orchestrator
├── 03-prompt-fase-1.md                ← FIX-PRIORITY-3: BUG-8 reinterpretación optimista
├── 04-prompt-fase-2.md                ← FIX-PRIORITY-2: Persistir commercial gates + BLOCKED_BY_GATES
├── 05-prompt-fase-3.md                ← FIX-PRIORITY-4: Decisión producto monthly_report
├── 06-prompt-fase-4.md                ← FIX-PRIORITY-5: Higiene nombres gates
├── 07-prompt-fase-release.md          ← v4complete verificación + version bump
├── 08-checklist-implementacion.md
├── 09-analisis-post-implementacion.md ← Template (completar post-ejecución)
└── dependencias-fases.md
```

**Cambio respecto al análisis original**: el orden de fases se INVIRTIÓ. FIX-PRIORITY-1 (causa raíz transversal) va PRIMERO porque resuelve 4 issues de un solo fix. BUG-8 baja al segundo lugar porque es independiente. BUG-7 baja al tercero porque requiere FIX-1 listo. BUG-10 y FIX-5 últimos.

---

## 13. Notas para la sesión de planificación

- **FIX-PRIORITY-1 es el de mayor leverage**: 1 nuevo módulo (~80 líneas) + 2 modificaciones de líneas existentes + 1 nueva entrada en `_JUSTIFIED_STATUSES` resuelve BUG-6, BUG-9, HALLAZGO-N2 y HALLAZGO-N4. La auditoría de pain_ledger ya tiene el campo `ASSET_GENERATED` definido (FASE-0B), solo falta usarlo y que el reconciliador lo emita.
- **BUG-8 opción B NO requiere N≥5 observaciones** porque es reinterpretación comercial, no cambio de fórmula matemática. El código del optimista no se toca; solo cambia el label y severity en commercial_gate.py:341.
- **BUG-7 requiere decisión sobre formato del nuevo archivo** `commercial_gates_report.json`. Recomendación: mismo schema que `CommercialGateReport.to_dict()` (ya implementado en commercial_gate.py:56-62).
- **BUG-10 requiere decisión de producto** del usuario. Si la respuesta es "remover de PROPOSAL_SERVICE_TO_ASSET", es 1 línea en `proposal_asset_alignment.py`. Si es "marcar STANDALONE_ASSET", requiere agregar enum value + filtrar en alignment_percentage.
- **La evidencia está en `output/clientes/v4_complete/`** — no en `output/v4_complete/`. DT-3 usaba el path default; esta ejecución usó `--output output/clientes`.

---

## 14. Cambios respecto a la versión original del análisis

| Sección | Cambio |
|---------|--------|
| §1 (archivos) | "47 archivos" → "~24 archivos visibles" |
| §3 (métricas) | "4 BLOCKING commercial gates" → "3 BLOCKING" + nota |
| §4.1 (BUG-6) | Causa raíz expandida con path de datos exacto + refinamiento (orchestrator propaga skipped_assets.pain_ids_affected, no el coverage gate consulta SitePresenceChecker) |
| §4.2 (BUG-7) | Ruta corregida (commercial_gate.py singular en quality_gates, NO commercial_gates.py en commercial_documents) + refinamiento (3 gates, no 4) + causa raíz doble verificada |
| §4.3 (BUG-8) | **Causa raíz REFUTADA**: NO es bug de cálculo (optimista<0 es matemáticamente correcto = "más ahorro que pérdida"). Es bug de INTERPRETACIÓN comercial. Opción B recomendada sobre clamp. |
| §4.4 (BUG-9) | Causa raíz refinada con verificación de las dos rutas (publication_gates vs delivery_quality_report) y la diferencia de contrato |
| §4.5 (BUG-10) | **Refutado como bug**: monthly_report sin pain es por diseño. Decisión de producto pendiente, no fix técnico. |
| §5 (nuevo) | HALLAZGO-N1 a N5 — 5 hallazgos amplificadores nuevos |
| §6 (nuevo) | Causa raíz transversal: 3 fuentes de verdad no consolidadas |
| §8 (orden) | Reordenado: FIX-PRIORITY-1 (reconciliador) primero por leverage |
| §9 (nuevo) | 5 fixes detallados con código específico |
| §10 | Criterios verificación actualizados con el nuevo FIX-1 |
| §11 | Restricciones ampliadas (rutas correctas + chequeo de "mismo nombre ≠ mismo contrato") |
| §12 | Orden de fases invertido (FIX-PRIORITY-1 primero) |

---

*Contexto actualizado el 2026-07-25 desde sesión de validación contra código vivo. Listo para formulación de plan DT-4 en nueva sesión, siguiendo política 1 fase = 1 sesión.*
