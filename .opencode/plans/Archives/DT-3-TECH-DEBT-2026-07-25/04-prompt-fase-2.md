# FASE-2: Unificar ProposalAssetMatrix + AlignmentReport (BUG-4 / P-04)

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DIRECTA (delegate_task NO viable — requiere decisión arquitectónica del agente principal)
> **Complejidad**: **ALTA** ⚠️ — Fase de mayor complejidad técnica del plan
> **Iteraciones máx**: 60
> **Depende de**: FASE-0 ✅ (BUG-1 corregido), FASE-1 ✅ (G9 corregido)
> **Bloquea a**: FASE-3

---

## Objetivo

Resolver P-04 (deuda técnica v4.64.0): unificar `ProposalAssetMatrix` y `AlignmentReport` en un solo contrato canónico que:

1. **Consuma `DeliveryContext`** como fuente de verdad (post-DT-1)
2. **Responda ambas preguntas** sin duplicar lógica:
   - "¿el servicio responde a un pain real?" (analytics, pain-driven)
   - "¿el asset existe (generado O en producción)?" (delivery, asset-existence)
3. **Elimine UNA de las dos clases** (no wrapper, no adapter — reemplazo real)
4. **Mantenga backward compatibility**: `create_readme()` legacy mode, `delivery_quality_report.json`, `proposal_asset_matrix.json`

---

## Contexto de Fases Anteriores

**FASE-0 completada**: `_get_pipeline_path()` existe en main.py. Las 3 rutas flat (pain_ledger, coherence_validation ×2) usan paths per-hotel correctos. `pain_ledger_entries` ya no está vacío.

**FASE-1 completada**: `BLOCKING_GATE_NAMES` constante unificada. G9 evalúa `status` (no `asset_path`). `NO_BREACH` no bloquea el delivery. `actionable_services` excluye `NO_BREACH`.

---

## Análisis de los Dos Sistemas Actuales

### ProposalAssetMatrix (L439)
```python
# Propósito: traceability pain-driven
# Pregunta: "¿el servicio de la propuesta responde a un pain real Y tenemos asset?"
# Fuente: PAIN_SOLUTION_MAP + pain_ledger
# Taxonomía: LINKED, MISSING_ASSET, NO_BREACH, GENERIC_DRAFT
# Archivo: proposal_asset_matrix.json
# Consumidores: v4_proposal_generator.py (escribe), G9/delivery_quality_report.py (lee)
```

### AlignmentReport (L60)
```python
# Propósito: delivery verification
# Pregunta: "¿el asset existe (generado O en producción)?"
# Fuente: PROPOSAL_SERVICE_TO_ASSET + site presence
# Taxonomía: aligned, missing, low_quality, present_in_production, redundant, indeterminate
# Archivo: asset_generation_report.json (campo "alineación")
# Consumidores: publication_gates.py (OLD gate system), tests/test_proposal_alignment.py
```

### Problema Central

Dos sistemas independientes que se ejecutan en el mismo `v4complete`:
- ProposalAssetMatrix → `proposal_asset_matrix.json` → G9 (delivery_quality_report.py)
- AlignmentReport → `verify_proposal_asset_alignment()` → publication_gates.py (OLD gate system)

Ambos son importados y ejecutados en main.py (L2766 publication_gates, L2915 delivery_quality_report).

---

## Tareas

### T1: Diseñar el contrato canónico unificado

Crear UNA sola clase `AssetAlignmentMatrix` que reemplace ambas. La taxonomía unificada debe ser:

```python
class AlignmentStatus(Enum):
    """Estado de alineación propuesta→asset unificado.
    
    Combina las dimensiones ortogonales:
    - analytics (pain-driven): ¿el servicio está justificado?
    - delivery (asset-existence): ¿el asset está listo?
    """
    LINKED = "linked"                    # Pain real + asset existe → ✅
    MISSING_ASSET = "missing_asset"      # Pain real + asset NO existe → ❌ (fallo real)
    NO_BREACH = "no_breach"             # Pain NO existe → ⏭️ (no aplica)
    GENERIC_DRAFT = "generic_draft"      # Placeholder genérico → ❌
    # De AlignmentReport (mantener para backward compat):
    PRESENT_IN_PRODUCTION = "present_in_production"  # Asset existe en sitio → ✅
    LOW_QUALITY = "low_quality"          # Asset generado pero baja calidad → ⚠️
    INDETERMINATE = "indeterminate"      # No se pudo determinar → ⚠️
```

**Ubicación**: `modules/asset_generation/proposal_asset_alignment.py`

**Métodos clave**:
- `build(delivery_context, pain_ledger) → AssetAlignmentMatrix` — constructor canónico
- `get_alignment(service_name: str) → AlignmentStatus` — lookup individual
- `to_dict() → dict` — serialización para proposal_asset_matrix.json
- `is_delivery_ready() → bool` — ¿todos los servicios accionables tienen asset?

### T2: Implementar la clase unificada

1. Crear `AssetAlignmentMatrix` en `proposal_asset_alignment.py`
2. Implementar `build()` que:
   - Recibe `DeliveryContext` (fuente de verdad post-DT-1)
   - Itera sobre servicios de la propuesta
   - Para cada servicio, determina si el pain existe (PAIN_SOLUTION_MAP + pain_ledger)
   - Si pain existe: verifica si asset está generado O en producción → LINKED o MISSING_ASSET
   - Si pain no existe: NO_BREACH
3. Implementar `to_dict()` compatible con el formato actual de `proposal_asset_matrix.json` (backward compat)
4. Implementar `is_delivery_ready()` para G9

### T3: Migrar consumidores

1. **G9 (delivery_quality_report.py)**: Cambiar para consumir `AssetAlignmentMatrix.is_delivery_ready()` en vez de leer `proposal_asset_matrix.json` manualmente
2. **main.py**: Actualizar imports y llamadas — reemplazar `ProposalAssetMatrix` por `AssetAlignmentMatrix`
3. **publication_gates.py**: Actualizar para consumir el contrato unificado en vez de `AlignmentReport`
4. **v4_proposal_generator.py**: Actualizar para usar `AssetAlignmentMatrix.to_dict()` al escribir `proposal_asset_matrix.json`

### T4: Tests

1. Verificar que los 42 tests existentes en `test_delivery_contract.py` siguen pasando
2. Agregar tests nuevos para:
   - `AssetAlignmentMatrix.build()` con DeliveryContext real
   - `is_delivery_ready()` con casos: todos LINKED, mixto LINKED+NO_BREACH, MISSING_ASSET presente
   - `to_dict()` compatibilidad con formato legacy
   - Edge cases: sin servicios, todos NO_BREACH, todos MISSING_ASSET

---

## Criterios de Completitud

- [ ] `AssetAlignmentMatrix` implementada como ÚNICA clase (ProposalAssetMatrix y AlignmentReport eliminadas o deprecated)
- [ ] `build()` consume `DeliveryContext`
- [ ] Taxonomía unificada con `AlignmentStatus` enum
- [ ] G9 consume `AssetAlignmentMatrix.is_delivery_ready()`
- [ ] `to_dict()` mantiene formato compatible con `proposal_asset_matrix.json`
- [ ] 42 tests existentes siguen pasando (0 regresiones)
- [ ] Tests nuevos cubren contrato unificado + edge cases
- [ ] `grep "ProposalAssetMatrix\|AlignmentReport" modules/` solo muestra referencias históricas en comentarios
- [ ] `grep "AssetAlignmentMatrix" modules/quality_gates/delivery_quality_report.py` confirma uso

---

## Restricciones

- **NO crear un tercer sistema**: `AssetAlignmentMatrix` reemplaza (no coexiste con) ProposalAssetMatrix y AlignmentReport
- **NO wrapper ni adapter**: eliminación real de las clases viejas
- **NO romper backward compat**: `create_readme()` legacy mode, `delivery_quality_report.json`, `proposal_asset_matrix.json`
- **NO modificar PAIN_SOLUTION_MAP** (BUG-5 refutado)
- **NO modificar SitePresenceChecker, CoherenceValidator, scenario_calculator.py**
- **NO ejecutar v4complete** (eso es FASE-3)
- **NO usar delegate_task**: la decisión arquitectónica de cómo fusionar dos taxonomías requiere el agente principal (§7.6 del contexto)

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Regresión en G9 (gate blocking) | MEDIA | ALTO | 42 tests como red de seguridad; verificar en FASE-3 con v4complete |
| Incompatibilidad de formato en proposal_asset_matrix.json | MEDIA | MEDIO | `to_dict()` debe ser byte-identical al formato actual |
| Romper publication_gates.py (OLD gate system) | BAJA | BAJO | El OLD gate system es secundario; G9 es el primario |
| DeliveryContext no tiene todos los datos necesarios | MEDIA | ALTO | Si falta algún campo, extender `DeliveryContext` (está permitido en §5) |

---

## Post-Ejecución (OBLIGATORIO)

```bash
cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe scripts\log_phase_completion.py --fase FASE-2 --plan DT-3-TECH-DEBT-2026-07-25 --desc P04_AssetAlignmentMatrix_unification"
```

---

## Próxima Sesión

**FASE-3**: Ejecutar v4complete para Zi One Luxury + verificación E2E post-fix + análisis de que los bugs fueron superados.
