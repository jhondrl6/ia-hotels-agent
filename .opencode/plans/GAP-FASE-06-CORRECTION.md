# GAP-FASE-06-CORRECTION: Bug Fix - FASE-6 Integración Incompleta

**ID**: GAP-FASE-06-CORRECTION
**Fecha**: 2026-03-30
**Prioridad**: CRITICAL
**Estado**: Detectado

---

## Problema

FASE-6 (Integración en v4complete) fue marcada como completada pero la integración está **ROTA**.

**Síntoma**: El bloque FASE-6 en `V4AssetOrchestrator.generate_assets()` ejecuta hasta `_build_canonical_assessment()` pero el método **NO EXISTE** en el archivo, causando `AttributeError` silenciosamente capturada por el `except`.

**Evidencia**:
```
[DEBUG] FASE-6: Reached GEO Flow section
[DEBUG] FASE-6: validated_data keys = ['whatsapp_number', 'rooms', ...]
[DEBUG] FASE-6: About to call _build_canonical_assessment...
[OK] Assets generados: 6   ← geo_flow NUNCA se ejecutó
```

**Causa raíz**: Los métodos helper `_build_canonical_assessment()` y `_build_commercial_diagnosis()` fueron implementados en una versión anterior del código pero fueron **revertidos** (probablemente por `git checkout` no intencionado).

---

## Archivos Afectados

| Archivo | Problema |
|---------|----------|
| `modules/asset_generation/v4_asset_orchestrator.py` | Faltan `_build_canonical_assessment()` y `_build_commercial_diagnosis()` |

---

## Módulos GEO Ya Implementados (que SÍ funcionan)

- ✅ `geo_diagnostic.py` - 42 métodos, 4 bands
- ✅ `geo_enrichment_layer.py` - MINIMAL/LIGHT/FULL
- ✅ `sync_contract.py` - 8 combinaciones narrativas
- ✅ `asset_responsibility_contract.py` - CORE/GEO/ADVISORY
- ✅ `geo_flow.py` - Orchestrator completo
- ✅ 138 tests en `tests/geo_enrichment/` pasan

---

## Solución Requerida

### Tarea 1: Añadir `_build_canonical_assessment()` al orchestrator

**Ubicación**: `modules/asset_generation/v4_asset_orchestrator.py`

**Propósito**: Construir `CanonicalAssessment` desde `validated_data` y `diagnostic_doc`

**Firma**:
```python
def _build_canonical_assessment(
    self,
    hotel_name: str,
    hotel_url: str,
    validated_data: Dict[str, Any],
    diagnostic_doc: DiagnosticDocument
) -> "CanonicalAssessment":
```

### Tarea 2: Añadir `_build_commercial_diagnosis()` al orchestrator

**Ubicación**: `modules/asset_generation/v4_asset_orchestrator.py`

**Propósito**: Construir dict `commercial_diagnosis` para Sync Contract desde `diagnostic_doc` y `proposal_doc`

**Firma**:
```python
def _build_commercial_diagnosis(
    self,
    diagnostic_doc: DiagnosticDocument,
    proposal_doc: ProposalDocument
) -> Dict[str, Any]:
```

### Tarea 3: Verificar integración

Ejecutar E2E y verificar:
- Logs `[V4AssetOrchestrator] FASE-6: Running GEO Flow...`
- Archivo `output/v4_complete/v4_audit/geo_flow_result.json` existe
- Coherence score >= 0.8 se mantiene

---

## Criterios de Éxito

- [ ] `_build_canonical_assessment()` existe y retorna `CanonicalAssessment` válido
- [ ] `_build_commercial_diagnosis()` existe y retorna dict con `loss_amount`
- [ ] E2E muestra logs de geo_flow ejecutándose
- [ ] `v4_audit/geo_flow_result.json` se genera
- [ ] Coherence se mantiene >= 0.8
- [ ] Assets CORE intactos (6 archivos)

---

## Notas

- No se requieren cambios en `geo_flow.py` ni en los otros módulos geo_enrichment
- La integración es "graceful degradation" - si geo_flow falla, v4complete continúa
- El bloque try-except ya existe, solo necesita los métodos helper
