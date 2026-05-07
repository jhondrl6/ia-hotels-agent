# FASE-PROP-D: Google Maps — Asset o Redefinición

**Plan:** PROPOSAL-COMERCIAL-FIX v1.0.0
**Workflow:** `.agents/workflows/phased_project_executor.md` v2.10.0
**Presupuesto:** 60 iteraciones max | **Estimado esta fase:** ~40 iteraciones
**Dependencias:** FASE-PROP-C ✅ (ideal)
**Fase siguiente:** FASE-PROP-F

## Contexto

`PROPOSAL_SERVICE_TO_ASSET` mapea "Google Maps Optimizado" → "geo_playbook". Pero `geo_playbook` nunca se genera. El gate de Termales también reportó:

```json
"missing": [{
  "service": "Google Maps Optimizado",
  "asset": "geo_playbook",
  "message": "Service promises asset but it was not generated",
  "presence_verified": true,
  "presence_status": "not_exists"
}]
```

El pipeline GEO ya genera: `geo_fix_kit.md`, `geo_checklist_min.md`, `geo_dashboard.md`, `geo_badge.md`. Es posible que `geo_playbook` sea redundante.

**Objetivo**: Eliminar la promesa falsa si los assets existentes cubren la función, O crear el asset si no.

## Estado de Fases Anteriores

|| Fase | Estado |
|------|--------|
| FASE-PROP-A | ✅ Completada |
| FASE-PROP-B | ✅ Completada |
| FASE-PROP-C | ✅ Completada |
| FASE-PROP-D | ✅ Completada |

## Base Técnica Disponible

- `modules/commercial_documents/v4_proposal_generator.py`: `PROPOSAL_SERVICE_TO_ASSET` mapping
- `modules/asset_generation/asset_catalog.py`: catálogo centralizado
- `modules/asset_generation/geo_enriched/`: geo_fix_kit.md, geo_checklist_min.md, geo_dashboard.md, geo_badge.md
- `output/v4_complete/hotelcastillareal/geo_enriched/`: evidencia de assets generados

## Tareas Específicas

### Tarea 1: Verificar si assets GEO cubren geo_playbook
**Objetivo**: Entender qué hace cada asset GEO existente y si en conjunto cubren "Google Maps Optimizado".

**Archivos afectados**:
- `modules/asset_generation/geo_enriched/` (todos los archivos)
- `modules/asset_generation/asset_catalog.py`

**Criterios de aceptación**:
- [ ] Leer el contenido/descripción de cada asset GEO existente
- [ ] Determinar si alguno (o la suma de ellos) cubre "optimización de Google Maps"
- [ ] Documentar decisión con evidencia

### Tarea 2: Decisión — eliminar servicio o crear asset
**Objetivo**: Tomar decisión documentada.

**Criterios de aceptación**:
- [ ] Si los assets existentes cubren la función: decisión = ELIMINAR "Google Maps Optimizado" de `PROPOSAL_SERVICE_TO_ASSET` y `SERVICE_CATALOG`
- [ ] Si NO cubren: decisión = CREAR `geo_playbook` en `asset_catalog.py` con generación condicional
- [ ] Documentar la decisión y el motivo en comentarios

### Tarea 3: Implementar decisión
**Objetivo**: Aplicar la decisión en código.

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py` (mapping)
- `modules/asset_generation/asset_catalog.py` (si se crea asset)

**Criterios de aceptación**:
- [ ] Si ELIMINAR: "Google Maps Optimizado" ya no aparece en `PROPOSAL_SERVICE_TO_ASSET`
- [ ] Si CREAR: `geo_playbook` existe en el catálogo con reglas de generación condicional
- [ ] El gate de proposal_asset_alignment ya no reporta "geo_playbook missing"

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Test mapping | `tests/commercial_documents/test_proposal_generator.py` | "Google Maps Optimizado" mapea a asset existente o no aparece |
| Test catalog | `tests/asset_generation/test_asset_catalog.py` | Si se creó geo_playbook, is_asset_implemented retorna True |

**Comando de validación**:
```bash
venv/Scripts/python.exe -m pytest tests/commercial_documents/test_proposal_generator.py -v -k google_maps
venv/Scripts/python.exe -m pytest tests/asset_generation/test_asset_catalog.py -v
venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Archivos Involucrados

| Archivo | Tipo de Cambio | Notas |
|---------|---------------|-------|
| `modules/commercial_documents/v4_proposal_generator.py` | Modificación | `PROPOSAL_SERVICE_TO_ASSET` dict |
| `modules/asset_generation/asset_catalog.py` | Modificación (si creación) | Nuevo asset geo_playbook |

## Criterios de Completitud (CHECKLIST)

- [ ] **Decisión documentada**: Se sabe POR QUÉ se eliminó o se creó
- [ ] **Implementación aplicada**: Mapping actualizado o asset creado
- [ ] **Gate limpio**: proposal_asset_alignment_gate no reporta geo_playbook missing
- [ ] **Tests pasan**: Tests nuevos/existentes pasan
- [ ] **Validaciones del proyecto**: `run_all_validations.py --quick` pasa 4/4

## Restricciones

- **NO ejecutar** v4complete en esta fase — la verificación se hará en RELEASE
- **Máximo 60 iteraciones** (R2)

## Post-Ejecución (OBLIGATORIO)

1. **Actualizar `dependencias-fases.md`**: marcar FASE-PROP-D como ✅
2. **Actualizar `06-checklist-implementacion.md`**: marcar tareas completadas
3. **log_phase_completion.py**:
   ```bash
   cd /mnt/c/Users/Jhond/Github/iah-cli
   venv/Scripts/python.exe scripts/log_phase_completion.py \
       --fase FASE-PROP-D \
       --desc "Google Maps asset: eliminar promesa falsa o crear geo_playbook" \
       --archivos-mod "modules/commercial_documents/v4_proposal_generator.py,modules/asset_generation/asset_catalog.py" \
       --tests "2" \
       --check-manual-docs
   ```

**Siguiente fase:**
```
Carga y ejecuta .opencode/plans/05-prompt-inicio-sesion-fase-PROP-F.md siguiendo .agents/workflows/phased_project_executor.md
```
