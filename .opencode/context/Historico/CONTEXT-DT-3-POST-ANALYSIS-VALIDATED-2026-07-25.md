# Contexto VALIDADO: Análisis Post-DT-3 (Zione.co) — Validación Exhaustiva 2026-07-25 (sesión actual)

> **Origen validado**: `/.opencode/plans/Archives/DT-3-TECH-DEBT-2026-07-25/08-analisis-post-implementacion.md` (20.7 KB)
> **Sesión de validación**: 2026-07-25 (actual)
> **Versión auditada**: iah-cli v4.64.0
> **Método**: Lectura completa del análisis + verificación de cada claim factual contra:
> - JSON en disco (`output/clientes/v4_complete/zione/v4_audit/*.json`)
> - Código fuente en `modules/` (publication_gates, delivery_quality_report, commercial_gate, scenario_calculator, v4_asset_orchestrator, proposal_asset_alignment, pain_ledger, pain_solution_mapper, v4_proposal_generator, monthly_report_generator)
> - Source code paths y firmas de clase
>
> **Veredicto**: 5 bugs parcialmente caracterizados; 5 hallazgos amplificadores nuevos (N1-N5); 1 causa raíz transversal identificada; 6 correcciones a aplicar; fixes de causa raíz propuestos, NO implementados.

---

## 1. Resumen ejecutivo

El análisis original (08-analisis-post-implementacion.md) acierta en la observación principal (5 bugs post-DT-3) pero **incomplectamente caracteriza causas raíz**. El patrón transversal es: **3 fuentes de verdad (pain_ledger / proposal_asset_matrix / skipped_assets) evalúan "este pain está resuelto?" sin coordinarse.** Un reconciliador post-orquestador las consolidaría en una sola, resolviendo BUG-6, BUG-9 y HALLAZGO-N2 de un solo fix.

Tabla de validación numérica:

| # | Claim | Validación | Resultado |
|---|---|---|---|
| 1 | "47 archivos" | ~24 archivos en disco | INFLADO |
| 2 | "9 pains" | pain_ledger.json: 9 entries | CONFIRMADO |
| 3 | "coverage FAIL 8/9" | gate_report.json: total_detected=9, covered=8, uncovered=["no_whatsapp_visible"] | CONFIRMADO |
| 4 | "delivery G9 5/8" | delivery_quality_report.json: aligned=5, total=8 | CONFIRMADO |
| 5 | "publication G9 8/8" | gate_report §details: 6 aligned + 2 present_in_production = 8 | CONFIRMADO (con matiz) |
| 6 | "10 generated + 1 skipped" | asset_generation_report.json: generated=10, skipped=1 (whatsapp_button) | CONFIRMADO |
| 7 | "coherence 0.84" | 0.8424 (pre) / 0.82 (post) | CONFIRMADO |
| 8 | "conservative $7.2M / realistic $3.7M / optimistic -$270K" | financial_scenarios: 7276953.6 / 3741696.0 / -270950.4 | CONFIRMADO |
| 9 | "CommercialGateBlockedError" | v4_proposal_generator.py:38 (raise en :610) | CONFIRMADO (ruta) |
| 10 | "4 commercial gates" | Solo 3 disparan: CG-SCENARIO-ORDER, CG-SCENARIO-NEGATIVE, CG-ROI-NEGATIVE. CG-CLAIM-VS-EVIDENCE no dispara (place_found=False) | PARCIALMENTE ERRÓNEO |
| 11 | Ruta `commercial_gates.py` en commercial_documents | Real: `modules/quality_gates/commercial_gate.py` (singular) | RUTA MAL CITADA |
| 12 | "AssetAlignmentMatrix unificado" | proposal_asset_alignment.py:638 + uso en v4_proposal_generator.py:641 | CONFIRMADO |
| 13 | "DT-3 L58 marcó coverage legítimo" | No verificado en esta sesión (pertenece a otro doc) | TOMADO POR VERDADERO |

---

## 2. Causa raíz por bug (verificada en código)

### BUG-6 (CRÍTICO) — Causa raíz REAL

El coverage gate `publication_gates.py:1188-1322` lee:
```python
diagnostic_pain_ids = set(assessment.get("diagnostic_pain_ids", []))
proposal_pain_ids = set(assessment.get("proposal_pain_ids", []))
is_justified = entry.status in self._JUSTIFIED_STATUSES  # ={JUSTIFIED_SKIP, BLOCKED, MAPPED_TO_SERVICE}
```

JUSTIFIED_STATUSES = {JUSTIFIED_SKIP, BLOCKED, MAPPED_TO_SERVICE}. **No incluye "ASSET_GENERATED"** (que sí es válido en `pain_ledger.py:27`).

Path del dato:
```
SitePresenceChecker (whatsapp_button EXISTS, site_verified=true)
  → conditional_generator SKIP el asset → guarda en skipped_assets
  → asset_generation_report §skipped_assets graba pain_ids_affected=[no_whatsapp_visible]
  → GAP: nadie actualiza pain_ledger §status → sigue en DETECTED
  → coverage_gate: in_diagnostic=False, in_proposal=False, is_justified=False → FAIL
```

Análisis decía: "el coverage gate debe consultar SitePresenceChecker". Real: **el orchestrator debe propagar `skipped_assets.pain_ids_affected` al pain_ledger cambiando status a MAPPED_TO_SERVICE o ASSET_GENERATED.**

Publication G9 ya tiene patrón equivalente (`_proposal_asset_alignment_gate:863-890` inyecta `site_presence_report` "fake" desde skipped_assets). Debe replicarse en pain_ledger.

### BUG-7 — Causa raíz refutada parcialmente

Análisis: "commercial gates no aparecen en gate_report.json".

Realidad: `gate_report.json` SOLO persiste los **11 publication gates**. Commercial gates viven en `commercial_gate.py` (ruta: `modules/quality_gates/commercial_gate.py`, NO `commercial_documents/commercial_gates.py` como decía el análisis).

Cuando `validate_proposal` falla bloqueantemente, `v4_proposal_generator.py:610` hace `raise CommercialGateBlockedError(...)` → excepción NO capturada → main.py atrapa, escribe BLOCKED_BY_GATES.md desde `gate_report.json` (solo publication gates).

Causa raíz: CommercialGateBlockedError no se persiste antes de raise. BLOCKED_BY_GATES.md se genera solo desde publication gates.

### BUG-8 — Causa raíz refutada en superficie, MÁS PROFUNDA

Análisis: "no aplica `max(0, calculated)`".

`scenario_calculator.py:309-366`: el optimista = `current_ota_commission_loss - savings - ia_revenue`. Para Zione: $7.7M - $774K - $3.2M = -$270K. **Eso NO es bug de cálculo — es matemáticamente correcto**: "los ahorros + IA revenue SUPERAN la pérdida actual" = sin pérdida neta = escenario optimista funcionando.

El problema REAL es la INTERPRETACIÓN COMERCIAL. `_check_scenario_negative` (commercial_gate.py:328) dice "no puede mostrarse como recuperación". `_check_scenario_order` (L282) dice "optimista debe ser ≥ realista". Ambos asumen que los 3 escenarios son variantes del mismo eje (pérdida). Pero el optimista, por construcción matemática, puede caer en territorio de "ganancia neta".

Fix correcto (cambia causa raíz): reformular el optimista como **break-even (0)** cuando se vuelve negativo, no aplicar clamp cieguamente. O reinterpretar comercialmente: "ROI excelente / sin pérdida neta" → WARNING, no BLOCKING.

### BUG-9 (DEUDA DT-3) — Causa raíz refinada

Análisis: "delivery_quality_report.py consume ProposalAssetMatrix que solo cuenta LINKED".

Verificado:
```python
# proposal_asset_alignment.py:834-836
@property
def aligned_count(self) -> int:
    """Number of LINKED services (backward compat)."""
    return sum(1 for e in self.entries if e.status == "LINKED")
```

```python
# delivery_quality_report.py:218-219
delivery_ready = matrix.is_delivery_ready()  # bool
aligned_count = matrix.aligned_count        # 5 (LINKED only)
total_services = matrix.total_services      # 8
```

JSON tiene 8 entries: 5 LINKED + 1 MISSING_ASSET + 2 NO_BREACH. **No tiene campo `present_in_production` separado.** El publication gate G9 ve 8/8 porque llama `verify_proposal_asset_alignment` que SÍ considera `present_in_production`. Los 2 present_in_production (Botón WhatsApp, Schema Organization) son del SitePresenceChecker directo, no del JSON.

Hay DOS sistemas G9:
- (a) `_proposal_asset_alignment_gate` (publication_gates.py:803+): ve SitePresence directo. 8/8.
- (b) `delivery_quality_report._evaluate_alignment` (delivery_quality_report.py:193-225): reconstruye desde JSON limitado. 5/8.

Fix correcto: que `AssetAlignmentMatrix.save()` guarde TODOS los status (incluyendo `present_in_production`) en el JSON. Eliminar el round-trip JSON→objeto→JSON→objeto en delivery_quality_report.

### BUG-10 — Re-caracterizado (no es bug, es decisión de producto)

Análisis: "PainSolutionMapper asigna monthly_report a pain inexistente".

Verificado: `pain_solution_mapper.py:60-78` define `no_whatsapp_visible` → `whatsapp_button`. Monthly_report NO tiene pain en PAIN_SOLUTION_MAP. Se genera siempre (asset "always-on"). En proposal_asset_matrix aparece como `NO_BREACH` con `pain_ids_resolved=[]`. **Eso es correcto por diseño.**

Pregunta real de producto: ¿monthly_report debería contar como servicio prometido (reduciendo alignment%) o excluirse por ser reporting? Decisión pendiente.

---

## 3. Hallazgos amplificadores nuevos (N1-N5)

### HALLAZGO-N1: Dos gates "coverage" diferentes

- Publication **G11 coverage** (`publication_gates.py:1188`): pain_ledger + diagnostic + proposal.
- Delivery quality **G7 coverage** (`delivery_quality_report.py:356-384`): `failure_rate < 0.5` desde asset_generation_report.

Mismo nombre, diferente contrato. Cliente ve solo uno (G11 FAIL) pero internamente son 2.

### HALLAZGO-N2: ASSET_GENERATED falta en _JUSTIFIED_STATUSES

`pain_ledger.py:27` define status válidos: `DETECTED | DIAGNOSED | MAPPED_TO_SERVICE | ASSET_GENERATED | JUSTIFIED_SKIP | BLOCKED`.

`publication_gates.py:1186` define `_JUSTIFIED_STATUSES = {JUSTIFIED_SKIP, BLOCKED, MAPPED_TO_SERVICE}` — **falta ASSET_GENERATED**.

Si el orchestrator actualizara pain→ASSET_GENERATED cuando un asset se genera resolviendo pain, el coverage gate seguiría fallando. **Bloquea también FIX-PRIORITY-1.**

### HALLAZGO-N3: `whatsapp_conflict` cubierto pero `no_whatsapp_visible` no

pain_ledger.json: 9 entries. Coverage: 8 covered, 1 uncovered=[no_whatsapp_visible]. `whatsapp_conflict` SÍ está covered vía `whatsapp_conflict_guide` (asset_generation_report L25-28). Pero en proposal_asset_matrix, el service "Botón de WhatsApp" sigue MISSING_ASSET porque agrupa ambos pains.

### HALLAZGO-N4: Coherence check `whatsapp_verified` con score 0.3

`coherence_validation.json`:
```json
"whatsapp_verified": {"score": 0.3, "message": "WhatsApp con confidence insuficiente (0.30) - requiere >= 0.9"}
```

Score 0.84 global PASS (pesos: whatsapp_verified=0.5). Pero SitePresenceChecker SÍ sabe que el sitio tiene WhatsApp. El check no se beneficia de ese dato — mismo patrón "ghost module / signature-only wiring".

### HALLAZGO-N5: BLOCKED_BY_GATES.md instruye re-ejecutar sin mencionar commercial gates

El archivo `BLOCKED_BY_GATES.md` tiene solo 16 líneas (verificado en disco). Solo menciona el coverage gate de publication. Ningún rastro de los 3 commercial gates que abortaron. Accionable para el cliente dice: "Resuelva los issues... vuelva a ejecutar python main.py v4complete --url https://zione.co/". Si el cliente lo ejecuta sin tocar nada, falla idénticamente.

---

## 4. Causa raíz transversal (cross-cutting)

**El sistema tiene 3 fuentes de verdad DIFERENTES para "este pain está resuelto?":**

1. **pain_ledger[]** (status: DETECTED/DIAGNOSED/MAPPED_TO_SERVICE/ASSET_GENERATED/JUSTIFIED_SKIP/BLOCKED)
2. **proposal_asset_matrix.json** (status: LINKED/MISSING_ASSET/NO_BREACH/GENERIC_DRAFT)
3. **skipped_assets[]** (presence_status: exists/redundant/exists_with_issues)

Publication G9 reconcilia 1+3 (inyecta site_presence_report fake desde skipped_assets). Coverage G11 solo lee 1. Delivery quality G9 lee 2 sin enriquecer con 1 ni 3.

**Ningún punto central es la fuente única post-orquestador.**

Causa raíz REAL = **falta reconciliador post-orchestrator** que consolide las 3 fuentes en `pain_ledger_resolved.json` con status final. Ese único fix resuelve BUG-6 + BUG-9 + HALLAZGO-N2 + HALLAZGO-N4.

---

## 5. Correcciones aplicadas al análisis original

| Claim original | Corrección |
|---|---|
| "47 archivos generados" | "~24 archivos visibles" |
| "4 commercial gates BLOCKING" | "3 activos (CG-SCENARIO-ORDER, CG-SCENARIO-NEGATIVE, CG-ROI-NEGATIVE). CG-CLAIM-VS-EVIDENCE no dispara: requiere place_found=True AND gbp_rating≥4.0 (Zione sin GBP encontrado → no falla)" |
| Ruta `modules/commercial_documents/commercial_gates.py` | `modules/quality_gates/commercial_gate.py` (singular, en quality_gates/) |
| "BUG-8: no aplica max(0, calculated)" | "BUG-8 es semántico, no aritmético: optimista<0 es matemáticamente correcto (más ahorro que pérdida); el problema es la INTERPRETACIÓN de los commercial gates" |
| "BUG-9: delivery_quality_report aún consume ProposalAssetMatrix viejo" | "delivery_quality_report SÍ reconstruye AssetAlignmentMatrix desde JSON, pero el JSON no tiene campo present_in_production separado. Round-trip status MISSING_ASSET/NO_BREACH nunca se traduce a enum del modelo nuevo" |
| "BUG-10: PainSolutionMapper asigna monthly_report a pain inexistente" | "monthly_report NO tiene pain por diseño. La pregunta es si debe contar como servicio prometido o excluirse" |
| "Orden de ataque BUG-8 → BUG-6 → BUG-9 → BUG-7 → BUG-10" | Reordenado con causa raíz transversal: FIX-PRIORITY-1 (reconciliador) cubre BUG-6 + BUG-9 + N2 + N4. Luego BUG-8 + BUG-7 + BUG-10 |

---

## 6. Fixes recomendados — Orientados a causa raíz

### FIX-PRIORITY-1 (causa raíz transversal — resuelve BUG-6 + BUG-9 + N2 + N4)

**Acciones:**
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

**Acciones:**
1. En `v4_proposal_generator.py:610`, antes de raise CommercialGateBlockedError, persistir:
   ```python
   (output_path / hotel_slug / "v4_audit" / "commercial_gates_report.json").write_text(
       json.dumps(commercial_report.to_dict(), indent=2, ensure_ascii=False)
   )
   ```
2. En `main.py`, ampliar generación de `BLOCKED_BY_GATES.md` para incluir sección "🚨 Commercial Gates Bloqueantes" cuando exista `commercial_gates_report.json` con `blocking_passed: false`.
3. Remover la sugerencia de "vuelva a ejecutar" si hay commercial gates bloqueantes (la re-ejecución idéntica fallaría igual).

### FIX-PRIORITY-3 (resuelve BUG-8)

**Opción A (simple, cambia semántica):**
- En `scenario_calculator.py:354`, agregar clamp:
  ```python
  monthly_loss_cop = max(0.0, round(monthly_loss, 2))
  ```
- Nota docstring: "Optimistic scenario represents theoretical MIN of net loss; cannot be negative."

**Opción B (refactor semántico, preserva math):**
- Renombrar "optimistic" a "conservador-alcanzado" cuando se vuelve negativo.
- Cambiar `_check_scenario_negative` (commercial_gate.py:341) para WARNING en lugar de BLOCKING cuando `optimistic < 0` AND `realistic > 0`.

**Recomendación**: Opción B (preserva math, cambia interpretación comercial). Requiere producto-decisión: ¿queremos aceptar "sin pérdida neta" como escenario positivo?

### FIX-PRIORITY-4 (resuelve BUG-10 — decisión de producto)

**Opciones:**
- (A) Marcar `monthly_report` como `STANDALONE_ASSET` (nuevo status) y excluirlo de alignment counts.
- (B) Remover `monthly_report` de `PROPOSAL_SERVICE_TO_ASSET` — no es servicio prometido, es entrega complementaria.

**Recomendación**: (B) — más limpio. `monthly_report` se entrega como anexo del servicio principal, no se factura por separado.

### FIX-PRIORITY-5 (higiene — HALLAZGO-N1)

Renombrar uno de los dos `coverage`:
- `coverage` (publication G11) → `coverage_no_silent_drop`
- `coverage_gate` (delivery quality G7) → `coverage_failure_rate`

---

## 7. Macro-fases sugeridas (siguiendo política 1 fase = 1 sesión)

```
FASE-0 [preparación]: verificar versión, tests baseline
  - Tareas: pytest --collect-only, v4complete prueba Zione
  - Riesgo: 0

FASE-1 [FIX-PRIORITY-3]: scenario_calculator clamp + commercial_gate relabel
  - Tareas: 1 fix + 1 test + 1 v4complete
  - Riesgo: BAJO (cambio acotado)

FASE-2 [FIX-PRIORITY-1]: post-orchestrator reconciler
  - Tareas: 1 nuevo módulo + 2 modificaciones + 2 tests + 1 v4complete
  - Riesgo: MEDIO (reconciliador nuevo, afecta pain_ledger contract)

FASE-3 [FIX-PRIORITY-2]: persistir commercial gates + BLOCKED_BY_GATES ampliado
  - Tareas: 1 nueva persistencia + 1 ampliación BLOCKED_BY_GATES + 1 test
  - Riesgo: BAJO

FASE-4 [FIX-PRIORITY-4]: decidir producto sobre monthly_report
  - Requiere input Jhond ANTES de fase
  - Tareas (si decisión es B): 1 línea en PROPOSAL_SERVICE_TO_ASSET + 1 test
  - Riesgo: BAJO post-decisión

FASE-5 [FIX-PRIORITY-5]: renombrar gates duplicados (higiene)
  - Tareas: 2 renames + 2 test updates + CHANGELOG
  - Riesgo: BAJO

FASE-6 RELEASE v4.65.0: v4complete Zione + version bump + tag
  - Tareas: 1 v4complete + 1 derive_version + 1 sync_versions + 1 tag
  - Riesgo: BAJO
```

Total: 7 fases = 7 sesiones mínimo. R3 cumplido (≤4 tareas + 0 comandos largos por fase).

---

## 8. Restricciones heredadas + nuevas

1. Una fase = una sesión (política Jhond)
2. v4complete via `venv/Scripts/python.exe main.py v4complete --url https://zione.co/ --output output/clientes`
3. NO modificar `scenario_calculator.py` sin N≥5 observaciones — PERO el fix de BUG-8 es REINTERPRETACIÓN comercial, no cambio de fórmula: el código matemático no se toca (Opción B). Si se elige Opción A (clamp), documentar como class-level change con N=1 (Zione).
4. Tests deben capturar bug → fix → test PASS
5. ROADMAP/CONTRIBUTING cross-reference antes de declarar "no encontrado"
6. WSL `search_files` puede retornar 0 para archivos existentes — siempre verificar con `ls` directo
7. Rutas en código son `commercial_gate.py` (singular, en quality_gates), NO `commercial_gates.py` ni en commercial_documents/

---

## 9. Referencias verificadas

- **Análisis original (validado)**: `/mnt/c/Users/Jhond/Github/iah-cli//.opencode/plans/Archives/DT-3-TECH-DEBT-2026-07-25/08-analisis-post-implementacion.md` (20.7 KB)
- **Contexto DT-3 origen**: `/mnt/c/Users/Jhond/Github/iah-cli//.opencode/context/Historico/CONTEXT-DT-3-TECH-DEBT-POST-DT2.md`
- **Evidencia ejecución**: `/mnt/c/Users/Jhond/Github/iah-cli/output/clientes/v4_complete/zione/v4_audit/`
- **BLOCKED_BY_GATES.md**: 16 líneas, solo menciona coverage
- **Versión actual**: `v4.64.0` (VERSION.yaml)
- **Sesión validación**: 2026-07-25 (current)
- **Modelo**: minimax/minimax-m3 (current)

### Archivos de código consultados y referencias clave:

| Archivo | Líneas | Hallazgo |
|---|---|---|
| `modules/quality_gates/publication_gates.py` | 1186, 1188-1322 | coverage gate + _JUSTIFIED_STATUSES falta ASSET_GENERATED |
| `modules/quality_gates/delivery_quality_report.py` | 168-224 | G7 coverage ≠ G11 coverage; G9 round-trip JSON limitado |
| `modules/quality_gates/commercial_gate.py` | 98, 282-362 | Ruta real; 5 BLOCKING + 4 WARNING; CG-CLAIM-VS-EVIDENCE solo dispara con GBP |
| `modules/commercial_documents/v4_proposal_generator.py` | 38, 610 | CommercialGateBlockedError raise sin persistir |
| `modules/financial_engine/scenario_calculator.py` | 309-366 | optimista matemáticamente correcto, gate interpreta mal |
| `modules/asset_generation/proposal_asset_alignment.py` | 439, 638, 834 | ProposalAssetMatrix + AssetAlignmentMatrix + aligned_count solo LINKED |
| `modules/asset_generation/v4_asset_orchestrator.py` | 182-193 | skipped_assets registra pain_ids_affected pero NO propaga a pain_ledger |
| `modules/asset_generation/pain_ledger.py` | 20-27 | PainLedgerEntry con status ASSET_GENERATED válido pero no usado downstream |
| `modules/asset_generation/monthly_report_generator.py` | 1-60 | No pain-driven por diseño |
| `modules/quality/asset_semantics_validator.py` | 34-35 | no_whatsapp_visible → whatsapp_conflict_guide mapping existe |

---

*Contexto validado el 2026-07-25. Listo para formulación de plan DT-4 en nueva sesión, siguiendo política 1 fase = 1 sesión.*
