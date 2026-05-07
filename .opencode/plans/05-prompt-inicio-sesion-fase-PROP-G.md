# FASE-PROP-G: Sobrescritura de Evidencia — Rutas Persistentes

**Plan:** PROPOSAL-COMERCIAL-FIX v1.0.0
**Workflow:** `.agents/workflows/phased_project_executor.md` v2.10.0
**Presupuesto:** 60 iteraciones max | **Estimado esta fase:** ~40 iteraciones
**Dependencias:** FASE-PROP-A ✅ (estricto: ambas tocan main.py)
**Fase siguiente:** FASE-RELEASE-4.41.0

## Contexto

Los JSON de evidencia en `output/v4_complete/` se sobrescriben en cada ejecución de v4complete:
- `gate_report.json`
- `audit_report.json`
- `financial_scenarios.json`

Si se corre v4complete para Hotel A y luego Hotel B, los JSON del Hotel A desaparecen. Solo los .md y subdirectorios por hotel persisten.

**Objetivo**: Guardar JSON reports dentro de `output/v4_complete/{hotel_id}/v4_audit/` con timestamp.

## Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-PROP-A | ✅ Completada |
| FASE-PROP-B | ✅ Completada |
| FASE-PROP-C | ✅ Completada |
| FASE-PROP-D | ✅ Completada |
| FASE-PROP-E | ✅ Completada |
| FASE-PROP-F | ✅ Completada |

## Base Técnica Disponible

- `main.py` (L2719~): escritores de JSON
- `output/v4_complete/hotelcastillareal/v4_audit/`: ya existe estructura para coherence_validation.json

## Tareas Específicas

### Tarea 1: Cambiar rutas de escritura a subdirectorio por hotel
**Objetivo**: Los JSONs se escriban en `output/v4_complete/{hotel_id}/v4_audit/`.

**Archivos afectados**:
- `main.py`

**Criterios de aceptación**:
- [ ] Identificar TODOS los lugares en main.py donde se escriben `gate_report.json`, `audit_report.json`, `financial_scenarios.json`
- [ ] Cambiar la ruta para que incluya `hotel_id` (variable disponible en el pipeline)
- [ ] Crear el subdirectorio si no existe (`os.makedirs(..., exist_ok=True)`)

### Tarea 2: Agregar timestamp al nombre de archivo
**Objetivo**: Evitar sobrescritura incluso dentro del mismo hotel.

**Archivos afectados**:
- `main.py`

**Criterios de aceptación**:
- [ ] Nombre resultante: `gate_report_20260505_202709.json`
- [ ] Timestamp en formato `%Y%m%d_%H%M%S`
- [ ] Los archivos .md en la raíz se mantienen con nombre actual (no se cambian)

### Tarea 3: Actualizar lectores de estos archivos
**Objetivo**: Cualquier código que LEA estos JSONs debe saber buscar en la nueva ruta.

**Archivos afectados**:
- `main.py` (si hay lecturas propias)
- `modules/audit/` (si aplica)
- Cualquier otro módulo que referencie `output/v4_complete/gate_report.json`

**Criterios de aceptación**:
- [ ] Buscar `output/v4_complete/gate_report.json` en todo el código
- [ ] Actualizar las referencias para apuntar a la ruta con hotel_id + timestamp
- [ ] Si no se encuentra un lector específico, documentar que los únicos lectores son humanos (auditorías)

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Test ruta JSON | `tests/test_main.py` o nuevo | Después de v4complete, JSONs existen en `output/v4_complete/{hotel_id}/v4_audit/` |
| Test no sobrescritura | (mismo archivo) | Segunda ejecución crea archivos nuevos sin borrar los anteriores |

**Comando de validación**:
```bash
venv/Scripts/python.exe -m pytest tests/ -v -k json_path
venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Archivos Involucrados

| Archivo | Tipo de Cambio | Notas |
|---------|---------------|-------|
| `main.py` | Modificación | Escritores de JSON (L2719~) |

## Criterios de Completitud (CHECKLIST)

- [ ] **Rutas cambiadas**: JSONs se escriben en subdirectorio por hotel
- [ ] **Timestamp**: Nombre incluye fecha/hora
- [ ] **No sobrescritura**: Ejecuciones sucesivas preservan archivos anteriores
- [ ] **Lectores actualizados**: Código que lee estos JSONs apunta a nueva ruta (o se documenta que no hay lectores automáticos)
- [ ] **Tests pasan**: Tests nuevos/existentes pasan
- [ ] **Validaciones del proyecto**: `run_all_validations.py --quick` pasa 4/4

## Restricciones

- **NO modificar** la estructura de los JSONs — solo su ubicación y nombre
- **NO cambiar** la ubicación de los archivos .md generados — solo los .json de evidencia
- **Máximo 60 iteraciones** (R2)

## Post-Ejecución (OBLIGATORIO)

1. **Actualizar `dependencias-fases.md`**: marcar FASE-PROP-G como ✅
2. **Actualizar `06-checklist-implementacion.md`**: marcar tareas completadas
3. **log_phase_completion.py**:
   ```bash
   cd /mnt/c/Users/Jhond/Github/iah-cli
   venv/Scripts/python.exe scripts/log_phase_completion.py \
       --fase FASE-PROP-G \
       --desc "Sobrescritura de evidencia: JSONs persisten por hotel+timestamp" \
       --archivos-mod "main.py" \
       --tests "2" \
       --check-manual-docs
   ```

**Siguiente fase:**
```
Carga y ejecuta .opencode/plans/05-prompt-inicio-sesion-fase-RELEASE-4.41.0.md siguiendo .agents/workflows/phased_project_executor.md
```
