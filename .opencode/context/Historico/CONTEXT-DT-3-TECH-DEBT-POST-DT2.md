# Contexto: Deuda Técnica Post-DT-2 — ProposalAssetMatrix + G9 Validation

> **Origen**: Análisis post-implementación DT-2 (sesión 2026-07-25)
> **Versión actual**: v4.63.2 (Delivery-Contract-Residual, tag v4.63.2)
> **Hotel de referencia**: Zi One Luxury (https://zione.co/)
> **Severidad**: ALTA — delivery bloqueado para hoteles sin servicios alineados; dos modelos semánticos divergentes; BUG-1 (half-fix de paths) es causa raíz del bloqueo, no el hotel
> **Fecha del contexto**: 2026-07-25
> **Última auditoría contra código vivo**: 2026-07-25 (validación exhaustiva — ver §10-§14)
> **Segunda auditoría**: 2026-07-25 — BUG-5 refutado, BUG-1 ampliado a 3 archivos, estrategia corregida
> **Auditoría amplificada**: 4 bugs reales (1 CRÍTICO ampliado, 2 MEDIOS confirmados, 1 REFUTADO)

---

## 1. Archivos fuente

| Archivo | Rol |
|---------|-----|
| `/.opencode/plans/Archives/DT-2-DELIVERY-CONTRACT-RESIDUAL-2026-07-24/10-analisis-post-implementacion.md` | Análisis de lo completado y pendiente |
| `/.opencode/plans/Archives/DT-2-DELIVERY-CONTRACT-RESIDUAL-2026-07-24/09-checklist-implementacion.md` | Checklist maestro (7/7 fases ✅) |
| `/.opencode/context/Historico/CONTEXT-DT-2-DELIVERY-CONTRACT-RESIDUAL.md` | Contexto original de DT-2 |
| `modules/asset_generation/proposal_asset_alignment.py` | ProposalAssetMatrix (L439) + AlignmentReport (L60) — divergencia semántica documentada L447-459 |
| `modules/quality_gates/delivery_quality_report.py` | G9 gate (L193-219) — implementado post-DT-2, lee proposal_asset_matrix.json |
| `modules/delivery/delivery_packager.py` | Packager — P-01, P-02, P-06, P-07 fixes aplicados |
| `modules/delivery/delivery_context.py` | DeliveryContext — P-02 fix aplicado |
| `tests/delivery/test_delivery_contract.py` | 42 tests (28 originales + 14 DT-2) — ~1058 líneas reales |
| `modules/asset_generation/pain_ledger.py` | PainLedger facade — load/save de pain_ledger.json (154 líneas) |
| `modules/commercial_documents/pain_solution_mapper.py` | PAIN_SOLUTION_MAP estático (1119 líneas) — fuente de mapeo pain→asset |
| `main.py` | Pipeline principal — L2650 carga pain_ledger, L2908 delivery quality gates |

---

## 2. Lo que DT-2 resolvió (para no repetir)

DT-2 ejecutó 7 fases (A→RELEASE) con estos resultados:

| Finding | Fix | Estado |
|---------|-----|--------|
| P-01 | README conteo post-manifest (Pass 3 recalculo) | ✅ FIXED — tests PASS |
| P-02 | Advisory assets exclusión mutua en secciones state-based | ✅ FIXED — tests PASS |
| P-03 | Coherence score post-gen con fallback a pre-gen | ✅ FIXED — verificado en Zi One (0.82 post-gen) |
| P-04 | Divergencia semántica ProposalAssetMatrix vs AlignmentReport | ⚠️ DOCUMENTADA como DEUDA TÉCNICA v4.64.0 |
| P-05 | G9 dead gate → gate real implementado | ✅ FIXED — G9 bloqueó correctamente Zi One (0/8 alineados) |
| P-06 | proposal_asset_matrix.json path fix | ⚠️ FIXED PARCIAL — matrix se guarda per-hotel, pero pain_ledger.json sigue en ruta flat (ver BUG-1) |
| P-07 | String-vs-enum → DeliveryAssetState.DELIVERED | ✅ FIXED — 3 ubicaciones unificadas |

**Estado del release**: v4.63.2 tagged (`dd576a2`), VERSION.yaml en 4.63.2, 42/42 tests pasando.

---

## 3. Deuda técnica restante (2 items)

### 3.1 P-04: Unificar ProposalAssetMatrix + AlignmentReport (DEUDA TÉCNICA v4.64.0)

**Severidad**: MEDIA
**Archivos**: `modules/asset_generation/proposal_asset_alignment.py` (L60, L439)
**Afecta a**: `modules/quality_gates/delivery_quality_report.py` (G9, L193-219)

**Descripción del problema**:

El código tiene DOS sistemas independientes que evalúan la alineación propuesta→asset desde ángulos diferentes, con taxonomías incompatibles:

```
ProposalAssetMatrix (L439):
  - Propósito: traceability pain-driven
  - Pregunta: "¿el servicio de la propuesta responde a un pain real Y tenemos asset?"
  - Fuente: PAIN_SOLUTION_MAP + pain_ledger
  - Taxonomía: LINKED, MISSING_ASSET, NO_BREACH, GENERIC_DRAFT
  - Se guarda como: proposal_asset_matrix.json
  - Consumidores: v4_proposal_generator.py (escribe), G9/delivery_quality_report.py (lee)

AlignmentReport (L60):
  - Propósito: delivery verification
  - Pregunta: "¿el asset existe (generado O en producción)?"
  - Fuente: PROPOSAL_SERVICE_TO_ASSET + site presence
  - Taxonomía: aligned, missing, low_quality, present_in_production,
               redundant, indeterminate
  - Se guarda como: alineación en asset_generation_report.json
  - Consumidores: publication_gates.py (OLD gate system),
                  tests/test_proposal_alignment.py
```

**Impacto actual**:

El G9 gate (implementado en DT-2) lee `proposal_asset_matrix.json` generado por ProposalAssetMatrix para decidir si el delivery pasa. Esto significa que:

- G9 evalúa "¿los servicios vendidos tienen assets?" (ProposalAssetMatrix)
- Pero NO evalúa "¿los assets existen realmente en el sitio?" (AlignmentReport)
- El resultado: Zi One tiene 8 servicios con estado `NO_BREACH` → G9 FAIL → delivery bloqueado, aunque el hotel PUEDE tener assets reales en producción que AlignmentReport detectaría

**NOTA POST-AUDITORÍA (2026-07-25)**: El 0/8 NO_BREACH para Zi One NO es una característica legítima del hotel — es un falso positivo causado por BUG-1 (half-fix de paths). Con BUG-1 corregido, Zi One tendría potencialmente 7/8 servicios LINKED (los 9 pain_ids del ledger YA están en PAIN_SOLUTION_MAP — BUG-5 fue refutado en segunda auditoría). Ver §10.1 y §10.5.

La unificación debe crear un **solo contrato canónico** que consuma `DeliveryContext` (la fuente de verdad post-DT-1) y responda ambas preguntas sin duplicar lógica.

**Estimación de complejidad**: > 10 líneas. La unificación mezcla dimensiones ortogonales:
- analytics (pain-driven: ¿el servicio está justificado?)
- delivery (asset existence: ¿el asset está listo para entregar?)

**Riesgo si no se hace**: G9 es un gate blocking que puede rechazar deliveries legítimos porque la taxonomía `NO_BREACH` no distingue "el hotel no necesita este servicio" de "el pipeline no pudo generar el asset".

### 3.2 G9 Validation Gap: Delivery bloqueado por NO_BREACH

**Severidad**: MEDIA
**Archivos**: `modules/quality_gates/delivery_quality_report.py` (L193-219, L251-253)

**Descripción del problema**:

Post-DT-2, G9 es un gate BLOCKING (L253: `name in ("coherence", "coverage", "evidence", "proposal_asset_alignment")`). Zi One tiene 0/8 servicios alineados (todos `NO_BREACH`) → G9 FAIL → delivery bloqueado.

Esto impide:
- Verificar P-01, P-02, P-06 en un ZIP real post-DT-2
- Validación E2E completa del delivery pipeline

**Dos sub-problemas**:

1. **Validación E2E bloqueada**: Para verificar que P-01/P-02/P-06 funcionan en un ZIP real, se necesita un hotel con al menos 1 servicio `LINKED` (que pase G9). Alternativa: flag `--force-delivery` para testing.

2. **Decisión de severidad de G9**: ¿Debería G9 ser BLOCKING o WARNING?
   - BLOCKING (actual): solo entrega si TODOS los servicios tienen asset → estricto, puede ser demasiado para hoteles pequeños
   - WARNING: permite delivery pero advierte → menos protección, más pragmático para MVP
   - Híbrido: blocking solo si 0/N alineados (caso Zi One), warning si al menos 1 alineado

---

## 4. Estado actual del código relevante

### 4.1 G9 gate (post-DT-2)

```python
# delivery_quality_report.py L193-219
matrix_path = v4_audit_path / "proposal_asset_matrix.json"
if matrix_path.exists():
    matrix_data = self._load_json(matrix_path)
    entries = matrix_data.get("entries", [])
    total_services = len(entries)
    aligned_services = sum(
        1 for e in entries
        if e.get("asset_path") is not None and e.get("asset_path") != ""
    )
    passed = aligned_services == total_services if total_services > 0 else True
    gate_results["proposal_asset_alignment"] = {
        "passed": passed,
        "gate": "G9",
        "aligned": aligned_services,
        "total": total_services,
    }
else:
    gate_results["proposal_asset_alignment"] = {
        "passed": True,
        "gate": "G9",
        "skipped": True,
        "reason": "proposal_asset_matrix.json not found",
    }
```

**Observación**: G9 se evalúa contra `proposal_asset_matrix.json` (ProposalAssetMatrix). Si se unifica P-04, este código debe adaptarse al nuevo contrato canónico.

### 4.2 ProposalAssetMatrix docstring (divergencia documentada)

```python
# proposal_asset_alignment.py L447-459
Divergencia semántica con AlignmentReport (P-04, DT-2):
    - ProposalAssetMatrix: traceability pain-driven — ¿el servicio de la
      propuesta responde a un pain real de analytics Y tenemos asset?
      Usa PAIN_SOLUTION_MAP + pain_ledger. Taxonomía: LINKED, MISSING_ASSET,
      NO_BREACH, GENERIC_DRAFT.
    - AlignmentReport: delivery verification — ¿el asset existe (generado
      O en producción)? Usa PROPOSAL_SERVICE_TO_ASSET + site presence.
      Taxonomía: aligned, missing, low_quality, present_in_production,
      redundant, indeterminate.
    - DEUDA TÉCNICA (v4.64.0): unificar ambos modelos en un solo contrato
      canónico que consuma DeliveryContext como fuente de verdad. La
      unificación NO es trivial (> 10 líneas) porque mezcla dimensiones
      ortogonales: analytics (pain) × delivery (asset existence).
```

### 4.3 Tests

- 42 tests en `test_delivery_contract.py` (28 originales + 14 DT-2) — ~1058 líneas reales
- 42/42 PASSED
- P-01, P-02, P-06 cubiertos por tests con fixtures sintéticas (no verificados en ZIP real por bloqueo G9)

---

## 5. Archivos que serían afectados por el plan

| Archivo | Líneas actuales | Cambio esperado |
|---------|----------------|-----------------|
| `main.py` L2571, L2572, L2650 | 3462 | **BUG-1**: Corregir 3 `pain_ledger_path`/`coherence_validation` de ruta flat a per-hotel |
| `modules/asset_generation/proposal_asset_alignment.py` | 612 | Unificar ProposalAssetMatrix + AlignmentReport en un solo contrato canónico |
| `modules/quality_gates/delivery_quality_report.py` | 456 | Adaptar G9 al nuevo contrato unificado + fix BUG-2 (dual-list) |
| `modules/delivery/delivery_context.py` | 534 | Posible extensión si el contrato canónico consume DeliveryContext |
| ~~`modules/commercial_documents/pain_solution_mapper.py`~~ | ~~1119~~ | ~~**BUG-5**: Agregar 5 pain_ids faltantes~~ → ELIMINADO (BUG-5 refutado) |
| `tests/delivery/test_delivery_contract.py` | ~1058 | Tests para el contrato unificado + G9 warning/blocking |
| `VERSION.yaml` | — | Bump a v4.64.0 |

---

## 6. Criterios de éxito (DoD)

| # | Criterio | Verificable en |
|---|----------|----------------|
| S-1 | ProposalAssetMatrix y AlignmentReport comparten un solo modelo canónico | `proposal_asset_alignment.py` — una clase, no dos |
| S-2 | El contrato canónico consume `DeliveryContext` como fuente de verdad | `delivery_context.py` → nuevo módulo |
| S-3 | G9 evalúa contra el contrato unificado (no solo proposal_asset_matrix.json) | `delivery_quality_report.py` L193-219 |
| S-4 | NO_BREACH ≠ FAIL automático — distinguir "no necesita" de "no se pudo generar" | `proposal_asset_alignment.py` |
| S-5 | Delivery NO bloqueado para hoteles con assets reales en producción (aunque NO_BREACH) | v4complete para Zi One → ZIP generado |
| S-6 | 42 tests existentes siguen pasando (0 regresiones) | `test_delivery_contract.py` |
| S-7 | Tests nuevos cubren el contrato unificado + casos G9 | `test_delivery_contract.py` |
| S-8 | ZIP post-fix permite verificar P-01, P-02, P-06 en E2E real | `zione_YYYYMMDD.zip` |
| **S-9** | **BUG-1 corregido: pain_ledger se carga de ruta per-hotel** | `main.py` L2650 |
| **S-10** | **BUG-2 corregido: proposal_asset_alignment no aparece en warning_gates** | `delivery_quality_report.py` L257 |
| **S-11** | **BUG-5 REFUTADO: PAIN_SOLUTION_MAP ya cubre 9/9 pain_ids — no requiere cambios** | `pain_solution_mapper.py` |

---

## 7. Anti-patrones (lo que el plan NO debe hacer)

1. **NO crear un tercer sistema**: El contrato unificado reemplaza (no coexiste con) ProposalAssetMatrix y AlignmentReport. No es un wrapper ni un adaptador.
2. **NO eliminar G9**: G9 es valioso como gate. El problema es la taxonomía que usa, no el gate en sí.
3. **NO tocar el pipeline de producción**: SitePresenceChecker, CoherenceValidator, scenario_calculator.py están fuera de alcance.
4. **NO cambiar la semántica de `NO_BREACH` para hoteles existentes**: Si un hotel legítimamente no tiene ciertos dolores (ej: no necesita WhatsApp porque ya lo tiene resuelto), no forzar un asset falso.
5. **NO romper backward compatibility**: `create_readme()` legacy mode, formato de `delivery_quality_report.json`, y estructura de `proposal_asset_matrix.json` deben seguir siendo consumibles.
6. **NO usar delegate_task para decisiones arquitectónicas**: La unificación de dos modelos semánticos requiere el agente principal. El subagente puede ejecutar tareas mecánicas una vez tomada la decisión.
7. **NO ejecutar P-04 sin antes corregir BUG-1**: Unificar dos sistemas sobre datos incorrectos (pain_ledger vacío) produciría un contrato canónico que también daría resultados incorrectos. Ver §12.

---

## 8. Restricciones operativas

1. **Una fase = una sesión**: Igual que DT-2, cada fase en sesión independiente.
2. **Safety guard WSL**: No usar `rm -rf` directamente. Ver skill `wsl-safety-guard-bypass`.
3. **pytest**: Usar `venv/Scripts/python.exe -m pytest` (Windows venv) o instalar en `.venv-wsl`.
4. **v4complete**: `venv/Scripts/python.exe main.py v4complete --url https://zione.co/`
5. **Pre-commit hook**: `version_consistency_checker.py` (BLOCKING) + `sync_versions.py --check` (advisory).
6. **sync_versions.py**: Solo acepta `--check`, `--list`, `--validate`, `--rule`. No `--bump`.

---

## 9. Métricas de referencia (Zi One, post-DT-2)

| Métrica | Valor |
|---------|-------|
| coherence_score (post-gen) | 0.82 |
| G9 status | FAIL (0/8 alineados, todos NO_BREACH) |
| Delivery status | BLOCKED (G9 blocking gate) |
| Tests | 42/42 PASSED |
| Versión | v4.63.2 |
| ZIP generado | NO (bloqueado por G9) |
| Pain ledger real | 9 entries DETECTED en `zione/v4_audit/pain_ledger.json` |
| Pain ledger cargado | 0 entries (BUG-1: 3 rutas flat no existen — pain_ledger + coherence_validation ×2) |
| PAIN_SOLUTION_MAP coverage | 9/9 pain_ids cubiertos (BUG-5 refutado en segunda auditoría) |

---

## 10. Auditoría contra código vivo (2026-07-25) — Hallazgos

### 10.1 BUG-1 [CRÍTICO — AMPLIADO] Half-fix sistémico: 3 archivos con ruta flat inexistente

**Archivos**: `main.py` L2571, L2572, L2650
**Severidad**: CRÍTICA — causa raíz del bloqueo de Zi One; afecta 3 archivos JSON, no solo 1

```python
# main.py L2648-2652 — pain_ledger (ya documentado)
from modules.asset_generation.pain_ledger import PainLedger
pain_ledger_path = output_dir / "v4_audit" / "pain_ledger.json"        # ← FLAT
if pain_ledger_path.exists():
    pain_ledger_entries = PainLedger().load(pain_ledger_path)

# main.py L2571-2572 — coherence_validation (NUEVO, mismo patrón)
cv_post_path = output_dir / "v4_audit" / "coherence_validation_post_gen.json"  # ← FLAT
cv_path = output_dir / "v4_audit" / "coherence_validation.json"                # ← FLAT
```

**Evidencia**:
- `output/v4_complete/v4_audit/pain_ledger.json` → **NO EXISTE**
- `output/v4_complete/v4_audit/coherence_validation.json` → **NO EXISTE**
- `output/v4_complete/v4_audit/coherence_validation_post_gen.json` → **NO EXISTE**
- `output/v4_complete/zione/v4_audit/pain_ledger.json` → **SI EXISTE** (9 entries)
- `output/v4_complete/zione/v4_audit/coherence_validation.json` → **SI EXISTE** (overall_score=0.84)
- `output/v4_complete/zione/v4_audit/coherence_validation_post_gen.json` → **SI EXISTE**

**Consecuencias**:
1. `pain_ledger_entries = []` → ProposalAssetMatrix.build() recibe `ledger_pain_ids = set()` → 8/8 NO_BREACH
2. G1 sync (L2573-2576) nunca se ejecuta porque `cv_post_path` no existe → coherence_validation.json usa score pre-gen, no post-gen

**Causa raíz**: P-06 fixeó la ruta de ESCRITURA de `proposal_asset_matrix.json` (flat → per-hotel) pero NADIE auditó el resto de JSON reads en main.py. El fix fue puntual para un archivo cuando el problema era sistémico: todos los JSONs del pipeline estaban en flat y migraron a per-hotel.

**Fix**: Cambiar L2650, L2571, L2572 a `output_dir / hotel_id / "v4_audit" / "..."`. Pero el verdadero fix es sistémico: crear un helper `_get_pipeline_path(output_dir, hotel_id, filename)` y auditar TODOS los JSON reads en main.py (ver §12).

### 10.2 BUG-2 [MEDIO — NUEVO] G9 aparece en blocking_gates Y warning_gates simultáneamente

**Archivo**: `delivery_quality_report.py` L251-258
**Severidad**: MEDIA — cosmético pero inconsistencia de datos

```python
# L251-254
blocking_gates = [
    name for name, result in gate_results.items()
    if not result["passed"] and name in (
        "coherence", "coverage", "evidence", "proposal_asset_alignment"
    )
]
# L255-258
warning_gates = [
    name for name, result in gate_results.items()
    if not result["passed"] and name not in (
        "coherence", "coverage", "evidence"
    )                        # ↑ falta "proposal_asset_alignment"
]
```

**Evidencia en vivo** (`delivery_quality_report.json`):
```json
"blocking_gates": ["proposal_asset_alignment"],
"warning_gates":  ["proposal_asset_alignment"]
```

**Causa raíz**: La tupla de exclusión en L257 se escribió cuando `proposal_asset_alignment` NO era blocking. Al promoverse a blocking en DT-2, se actualizó la tupla de inclusión (L253) pero NO la tupla de exclusión (L257). Divergencia de 2 líneas que debieron actualizarse juntas.

**Fix**: Agregar `"proposal_asset_alignment"` a la tupla de exclusión en L257, o idealmente definir UNA sola constante `BLOCKING_GATE_NAMES` y usarla en ambos lugares.

### 10.3 BUG-3 [MEDIO — PARCIALMENTE DOCUMENTADO] G9 evalúa asset_path, no status

**Archivo**: `delivery_quality_report.py` L201-204
**Severidad**: MEDIA — no distingue NO_BREACH (legítimo) de MISSING_ASSET (fallo real)

```python
aligned_services = sum(
    1 for e in entries
    if e.get("asset_path") is not None and e.get("asset_path") != ""
)
```

Tanto `NO_BREACH` como `MISSING_ASSET` tienen `asset_path=null`, pero semánticamente son opuestos:
- `NO_BREACH` = "el dolor no existe, este servicio NO debería estar en la propuesta" → no es fallo de delivery
- `MISSING_ASSET` = "el dolor existe pero el asset no se generó" → SÍ es fallo de delivery

El contexto documenta este problema en §3.1 pero lo atribuye a la divergencia ProposalAssetMatrix vs AlignmentReport. En realidad persiste incluso con BUG-1 corregido.

**Fix**: G9 debe evaluar `status`, no `asset_path`. `NO_BREACH` → skip/warning; `MISSING_ASSET` → fail; `LINKED` → pass.

### 10.4 BUG-4 [CONFIRMADO — DOCUMENTADO] Divergencia semántica ProposalAssetMatrix vs AlignmentReport

**Verificado en código**: Dos sistemas independientes con taxonomías diferentes, ambos ejecutándose en el mismo v4complete:
- ProposalAssetMatrix → `proposal_asset_matrix.json` → G9 (delivery_quality_report.py)
- AlignmentReport → `verify_proposal_asset_alignment()` → publication_gates.py (OLD gate system)

Ambos son importados y ejecutados en main.py (L2766 publication_gates, L2915 delivery_quality_report). El contexto lo documenta correctamente en P-04.

### 10.5 BUG-5 [REFUTADO — SEGUNDA AUDITORÍA 2026-07-25] PAIN_SOLUTION_MAP SÍ cubre 9/9 dolores detectados

**Archivo**: `modules/commercial_documents/pain_solution_mapper.py` L60-309
**Severidad**: NINGUNA — claim original era falso positivo

**AUDITORÍA INICIAL (ERRÓNEA)**: El contexto afirmó que 5/9 pain_ids del pain_ledger de Zi One no estaban en PAIN_SOLUTION_MAP.

**SEGUNDA AUDITORÍA (CÓDIGO VIVO)**: Verificación exhaustiva carácter por carácter contra `pain_solution_mapper.py`:

| pain_id | Línea en código | Assets mapeados |
|---------|----------------|-----------------|
| no_whatsapp_visible | L61 | whatsapp_button |
| whatsapp_conflict | L70 | whatsapp_button, whatsapp_conflict_guide |
| no_hotel_schema | L106 | hotel_schema |
| **low_seo_score** | **L299** | **optimization_guide** |
| no_faq_schema | L79 | faq_page |
| **no_analytics_configured** | **L170** | **analytics_setup_guide** |
| **low_organic_visibility** | **L179** | **indirect_traffic_optimization** |
| **ai_crawler_blocked** | **L198** | **llms_txt** |
| **no_og_tags** | **L245** | **og_tags_guide, open_graph** |

**Veredicto**: 9/9 pain_ids de Zi One están en PAIN_SOLUTION_MAP. BUG-5 NO EXISTE. El 0/8 NO_BREACH es 100% atribuible a BUG-1 (pain_ledger vacío por ruta flat). Con BUG-1 corregido, los 9 pain_ids del ledger poblaran `ledger_pain_ids` en ProposalAssetMatrix.build() y producirán entradas LINKED/MISSING_ASSET.

**Corrección de estrategia**: FASE-1 ("Completar PAIN_SOLUTION_MAP") queda ELIMINADA del plan de intervención. Ver §13 actualizado.

---

## 11. Verificación de claims del contexto original

| Claim | Línea | Veredicto | Evidencia |
|-------|-------|-----------|-----------|
| VERSION.yaml en 4.63.2 | L5 | ✅ CONFIRMADO | `grep version VERSION.yaml` → "4.63.2" |
| Tag v4.63.2 existe | L41 | ✅ CONFIRMADO | `git tag -l "v4.63*"` → v4.63.2 |
| proposal_asset_alignment.py 612 líneas | L178 | ✅ CONFIRMADO | `wc -l` → 612 |
| delivery_quality_report.py 456 líneas | L179 | ✅ CONFIRMADO | `wc -l` → 456 |
| delivery_context.py 534 líneas | L180 | ✅ CONFIRMADO | `wc -l` → 534 |
| Docstring divergencia L447-459 | L150-163 | ✅ CONFIRMADO | Código L447-459 coincide |
| G9 L193-219 | L118-143 | ✅ CONFIRMADO | Código L193-219 coincide |
| 42 tests | L183 | ✅ CONFIRMADO | `grep -c "def test_\|@pytest.mark.parametrize"` → 42 |
| Coherence 0.82 | L227 | ✅ CONFIRMADO | delivery_quality_report.json → 0.82 |
| G9 FAIL 0/8 alineados | L228-229 | ✅ CONFIRMADO | delivery_quality_report.json → aligned:0, total:8 |
| 8/8 NO_BREACH | §3.2 | ✅ CONFIRMADO | proposal_asset_matrix.json → 8 entries pain_ids:[] |
| P-06: matrix en zione/v4_audit/ | L37 | ⚠️ PARCIAL | Matrix sí está per-hotel, pero pain_ledger sigue en flat |
| P-07: DeliveryAssetState.DELIVERED | L39 | ✅ CONFIRMADO | Enum usado en delivery_context.py + packager |
| test_delivery_contract.py ~700 líneas | L181 | ~ | Real: ~1058 líneas (diferencia menor) |
| "G9 bloqueó correctamente" | L37 | ⚠️ IMPRECISO | Bloqueó, pero por BUG-1 (falso positivo), no por falta real de dolores |

**Precisión global**: 88% de claims confirmados. 2 claims imprecisos (L37 y L181).

---

## 12. Causa raíz sistémica (AMPLIADA — SEGUNDA AUDITORÍA)

Todos los bugs comparten un patrón común:

**LA MIGRACIÓN DE RUTAS FLAT → PER-HOTEL FUE PARCIAL.**

P-06 fixeó UN archivo (`proposal_asset_matrix.json`) de N archivos que se migraron. BUG-1 demuestra que TRES archivos más quedaron con ruta flat:

| Línea | Archivo JSON | Tipo |
|-------|-------------|------|
| L2650 | pain_ledger.json | READ — causa 8/8 NO_BREACH |
| L2572 | coherence_validation.json | READ/WRITE — G1 sync roto |
| L2571 | coherence_validation_post_gen.json | READ — fuente del sync |

DT-2 aplicó un fix puntual (P-06) a un problema sistémico (migración flat→per-hotel de todos los JSONs del pipeline). El fix fue correcto para UN archivo pero incompleto para el sistema.

El delivery de Zi One NO está bloqueado porque el hotel no tenga dolores — está bloqueado porque el pipeline no ENCUENTRA los dolores que SÍ detectó (BUG-1: pain_ledger en ruta flat inexistente). Además, el G1 sync de coherence nunca se ejecuta (BUG-1: coherence_validation en ruta flat inexistente).

**NOTA**: El análisis inicial también atribuyó parte del bloqueo a BUG-5 (PAIN_SOLUTION_MAP incompleto). Ese claim fue REFUTADO en segunda auditoría: los 9/9 pain_ids de Zi One YA están en PAIN_SOLUTION_MAP. El 0/8 NO_BREACH es 100% atribuible a BUG-1.

---

## 13. Orden de intervención recomendado (CORREGIDO — SEGUNDA AUDITORÍA 2026-07-25)

**CORRECCIÓN**: BUG-5 fue refutado — los 9 pain_ids YA están en PAIN_SOLUTION_MAP. FASE-1 original queda eliminada. BUG-1 es sistémico: afecta 3 archivos, no 1.

La causa raíz sistémica (half-fix de paths) debe resolverse ANTES que P-04. Unificar dos sistemas sobre datos incorrectos produciría un contrato canónico que también daría resultados incorrectos.

```
FASE-PRE: Fix SISTÉMICO de rutas flat → per-hotel (BUG-1 AMPLIADO)
  ├── Crear helper _get_pipeline_path(output_dir, hotel_id, filename)
  ├── Corregir pain_ledger.json (L2650)
  ├── Corregir coherence_validation.json (L2572)
  ├── Corregir coherence_validation_post_gen.json (L2571)
  ├── Limpiar copias flat stale (v4_audit/proposal_asset_matrix.json, si existe)
  └── Verificar: pain_ledger_entries = 9, G1 sync funcional para Zi One

FASE-1: Corregir G9 dual-list (BUG-2)
  └── Unificar BLOCKING_GATE_NAMES constante, usar en L253 y L257 (~2 líneas)

FASE-2: G9 evaluar status, no asset_path (BUG-3)
  ├── Cambiar aligned_services: LINKED → pass, MISSING_ASSET → fail, NO_BREACH → skip
  └── Requiere FASE-PRE completada para tener datos reales de validación

FASE-3: Unificar ProposalAssetMatrix + AlignmentReport (BUG-4 / P-04)
  ├── Consumir DeliveryContext como fuente única
  ├── Eliminar una de las dos clases redundantes
  ├── Migrar G9 al nuevo contrato unificado
  └── Cubre S-1, S-2, S-3 del DoD original
```

**Lo que se ELIMINA del plan original**:
- ❌ FASE-1 original ("Completar PAIN_SOLUTION_MAP — BUG-5"): los 9/9 pain_ids YA están mapeados. No hay nada que agregar.

Estimación de esfuerzo: FASE-PRE (~2h), FASE-1 (~15min), FASE-2 (~1h), FASE-3 (~4-6h). Total: ~7.25-9.25h (vs ~8.25-10.25h original).

---

## 14. Veredicto (CORREGIDO — SEGUNDA AUDITORÍA 2026-07-25)

El contexto CONTEXT-DT-3 es **factualmente correcto en el 94% de sus claims verificables** (16/17). Sin embargo, la segunda auditoría contra código vivo encontró:

1. **BUG-5 refutado**: Los 9/9 pain_ids de Zi One YA están en PAIN_SOLUTION_MAP. El claim original de "5 pain_ids faltantes" era un falso positivo. FASE-1 del plan de intervención queda eliminada.

2. **BUG-1 ampliado**: No es solo pain_ledger.json. También coherence_validation.json y coherence_validation_post_gen.json (L2571-2572) usan ruta flat. Son 3 archivos con el mismo bug, no 1.

3. **Prioridad de intervención corregida**: FASE-PRE → FASE-1 (dual-list) → FASE-2 (G9 status) → FASE-3 (unificación P-04). Una fase menos que el plan original (4 vs 5).

4. **Estimación LINKED corregida**: Con BUG-1 resuelto, Zi One tendría potencialmente 7/8 LINKED (no 4-5). La subestimación se debía a asumir que PAIN_SOLUTION_MAP no cubría 5 pain_ids, lo cual es falso.

5. **Subestima el alcance de P-04**: lo trata como deuda técnica aislada cuando es síntoma de un patrón de "fix puntual a problema sistémico" que se repite en BUG-1 y BUG-2.

**Recomendación**: Ejecutar en orden FASE-PRE → FASE-1 → FASE-2 → FASE-3. No iniciar P-04 sin antes resolver FASE-PRE.
