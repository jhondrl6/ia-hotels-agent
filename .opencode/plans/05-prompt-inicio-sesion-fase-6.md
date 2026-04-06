# FASE-6: Integración en v4complete Workflow

**ID**: FASE-6
**Objetivo**: Integrar el flujo GEO completo (Diagnostic → Enrichment → Sync → Responsibility) en v4complete como paso post-pipeline
**Dependencias**: FASE-5 (Responsibility Contract implementado)
**Duracion estimada**: 1-2 horas
**Skill**: systematic-debugging

---

## Contexto

La FASE-5 implementó el Responsibility Contract. Ahora se integra todo el flujo GEO en el workflow principal de v4complete.

### Flujo Integrado

```
v4complete workflow:
    │
    ├── FASE 1-4: Pipeline existente (SIN CAMBIOS)
    │       │
    │       ▼
    │   [Assets CORE generados]
    │       │
    │       ▼
    │   [Diagnóstico Comercial]
    │       │
    │
    └── NUEVO: GEO Flow (POST-PIPELINE)
              │
              ├─► GEO Diagnostic (FASE-2)
              │       │
              │       ▼
              ├─► GEO Enrichment Layer (FASE-3)
              │       │     │
              │       │     ├─► MINIMAL (Caso A: EXCELLENT)
              │       │     ├─► LIGHT (Caso B: GOOD)
              │       │     └─► FULL (Casos C/D: FOUNDATION/CRITICAL)
              │       │
              │       ▼
              ├─► Sync Contract (FASE-4)
              │       │     └─► Valida coherencia narrativa
              │       │
              │       ▼
              └─► Responsibility Contract (FASE-5)
                      └─► Genera guía de implementación
```

### Principio de No-Desconexión

1. Pipeline actual NUNCA se modifica
2. GEO Flow es completamente opcional (si falla, v4complete continúa)
3. Data contract entre fases permanece inmutable
4. Assets CORE NUNCA se reemplazan por GEO

---

## Tareas

### Tarea 1: Crear geo_flow.py como orchestrator del flujo GEO

**Objetivo**: Unificar Diagnostic + Enrichment + Sync + Responsibility en un solo módulo

**Archivos afectados**:
- `modules/geo_enrichment/geo_flow.py` (NUEVO)

**Criterios de aceptacion**:
- [ ] Método `execute(hotel_data, commercial_diagnosis, output_dir)` retorna GeoFlowResult
- [ ] Orchestrates: Diagnostic → Enrichment → Sync → Responsibility
- [ ] Graceful degradation: si cualquier paso falla, continúa con lo que tiene

```python
@dataclass
class GeoFlowResult:
    success: bool
    case: GeoCase  # MINIMAL | LIGHT | FULL
    geo_assessment: GEOAssessment | None
    assets_generated: list[str]
    sync_result: SyncResult | None
    responsibility_guide: AssetResponsibilityGuide | None
    errors: list[str]
```

### Tarea 2: Integrar geo_flow en v4_asset_orchestrator

**Objetivo**: El orchestrator invoca geo_flow después de assets CORE

**Archivos afectados**:
- `modules/asset_generation/v4_asset_orchestrator.py` (MODIFICAR)

**Criterios de aceptacion**:
- [ ] geo_flow se ejecuta DESPUÉS de assets CORE
- [ ] NO bloquea si geo_flow falla
- [ ] Logs清清楚楚 de lo que se ejecutó

### Tarea 3: Verificar que assets CORE no se modifican

**Objetivo**: Confirmar que conditional_generator y demás NO cambian

**Archivos afectados**:
- Verificar que NO se modifica nada en `modules/asset_generation/conditional_generator.py`

**Criterios de aceptacion**:
- [ ] conditional_generator.py sin cambios
- [ ] Assets CORE intactos
- [ ] Solo se agrega geo_flow como paso nuevo

### Tarea 4: Actualizar AGENTS.md con nuevo flujo

**Objetivo**: Documentar geo_flow en módulos activos

**Archivos afectados**:
- `AGENTS.md` (MODIFICAR)

**Criterios de aceptacion**:
- [ ] geo_flow documentado como módulo
- [ ] Flujo integrado descrito

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| `test_geo_flow_minimal.py` | `tests/geo_enrichment/` | Caso A: Solo geo_badge |
| `test_geo_flow_full.py` | `tests/geo_enrichment/` | Caso C/D: 7+ archivos |
| `test_geo_flow_graceful.py` | `tests/geo_enrichment/` | No falla si geo falla |
| `test_geo_flow_in_v4orchestrator.py` | `tests/geo_enrichment/` | Se ejecuta en v4complete |

**Comando de validacion**:
```bash
python -m pytest tests/geo_enrichment/ -v
python scripts/run_all_validations.py --quick
```

---

## Post-Ejecucion

1. Marcar FASE-6 como completada en README.md
2. Capability Contract: geo_flow como "conectada"

---

## Criterios de Completitud

- [ ] geo_flow.py implementado como orchestrator
- [ ] Graceful degradation funciona
- [ ] Assets CORE intactos
- [ ] geo_flow en v4_asset_orchestrator
- [ ] AGENTS.md actualizado
- [ ] Tests pasan
