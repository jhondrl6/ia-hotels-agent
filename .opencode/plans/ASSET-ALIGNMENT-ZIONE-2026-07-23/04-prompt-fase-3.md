# FASE-3: Propuesta condicional + unificación de fuentes de verdad

**ID**: ASSET-ALIGNMENT-FASE-3
**Objetivo**: Hacer que la propuesta comercial solo prometa servicios con asset generado (o present_in_production) y unificar las 3 fuentes de verdad divergentes para servicios.
**Dependencias**: FASE-1 completada
**Duración estimada**: 2 horas
**Skill**: `iah-cli-phased-execution` + `iah-cli-execution-conventions`
**delegate_task**: ✅ SUBAGENTE — cambios mecánicos de unificación + condicionales. Spec del contexto (§9.6, §7.C).

---

## Contexto

### Problema 9.6: Tres fuentes de verdad divergentes

El sistema tiene 3 estructuras de datos que definen los servicios, y no están sincronizadas:

1. `proposal_asset_alignment.py:PROPOSAL_SERVICE_TO_ASSET` — 8 entradas (source of truth para Gate 9)
2. `service_catalog.py:SERVICE_CATALOG` — 7+1 entradas (más FASE-D dinámica)
3. `service_catalog.py:SERVICE_TO_ASSET_LOOKUP` — derivado de SERVICE_CATALOG

`_generate_dynamic_services_table()` itera sobre PROPOSAL_SERVICE_TO_ASSET (8 servicios).
`_generate_asset_quality_table()` itera sobre SERVICE_CATALOG filtrado por detected_pain_ids.
Resultado: "Informe Mensual" aparece en asset_quality_table pero NO en la tabla principal de servicios.

### Problema Opción C: Propuesta promete sin verificar

`v4_proposal_generator.py:_generate_dynamic_services_table()` itera TODOS los 8 servicios de
PROPOSAL_SERVICE_TO_ASSET siempre, sin verificar si el asset correspondiente fue generado.
La tabla muestra todos los servicios como "⏳ Pendiente" o "✅ Completado", pero no oculta
los que no tienen asset generado ni presencia en producción.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-1 | ✅ Completada |
| FASE-2 | ✅ Completada |

### Base Técnica Disponible

- Archivos a modificar:
  - `modules/commercial_documents/v4_proposal_generator.py` (_generate_dynamic_services_table)
  - `modules/commercial_documents/service_catalog.py` (SERVICE_CATALOG, SERVICE_TO_ASSET_LOOKUP)
  - `modules/asset_generation/proposal_asset_alignment.py` (PROPOSAL_SERVICE_TO_ASSET — fuente de verdad)
- Tests base: `tests/test_proposal_dynamic.py`, `tests/quality_gates/test_proposal_asset_alignment.py`

---

## Tareas

### Tarea 1: Hacer _generate_dynamic_services_table condicional

**Objetivo**: Que la tabla de servicios en la propuesta solo muestre servicios que tienen asset
generado o están marcados como present_in_production.

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py`

**Lógica actual**: `_generate_dynamic_services_table()` (L1110+) itera TODOS los 8 servicios
de PROPOSAL_SERVICE_TO_ASSET siempre.

**Fix requerido**: Antes de agregar un servicio a la tabla, verificar:
1. ¿El asset correspondiente fue generado? (check asset_generation_report.json)
2. ¿El servicio está marcado como present_in_production? (check Gate 9 data)
3. Si ninguna de las dos → excluir el servicio de la tabla (o marcarlo como "No incluido en esta entrega")

**Opción recomendada**: Excluir el servicio de la tabla principal, pero agregar una nota al pie:
"Servicios adicionales disponibles: [lista de servicios excluidos]"

**Criterios de aceptación**:
- [ ] Servicios sin asset generado ni present_in_production NO aparecen como "⏳ Pendiente"
- [ ] Servicios con asset generado aparecen como "✅ Completado"
- [ ] Servicios present_in_production aparecen con su etiqueta correspondiente
- [ ] La nota al pie lista los servicios excluidos (si hay)
- [ ] Test: mock con 4/8 servicios con asset → tabla muestra 4 + nota con 4 excluidos

### Tarea 2: Unificar SERVICE_TO_ASSET_LOOKUP con PROPOSAL_SERVICE_TO_ASSET

**Objetivo**: Hacer que SERVICE_TO_ASSET_LOOKUP se derive de PROPOSAL_SERVICE_TO_ASSET (fuente
única de verdad), eliminando la divergencia.

**Archivos afectados**:
- `modules/commercial_documents/service_catalog.py`

**Lógica actual**: SERVICE_TO_ASSET_LOOKUP se deriva de SERVICE_CATALOG (que tiene 7+1 entradas,
divergente de PROPOSAL_SERVICE_TO_ASSET que tiene 8).

**Fix requerido**:
1. Hacer que SERVICE_TO_ASSET_LOOKUP se derive de PROPOSAL_SERVICE_TO_ASSET (importándolo o
   redefiniéndolo para que coincida exactamente).
2. Sincronizar SERVICE_CATALOG con PROPOSAL_SERVICE_TO_ASSET: las entradas deben coincidir
   (mismo número de servicios, mismos nombres).

**Opción recomendada**: Importar PROPOSAL_SERVICE_TO_ASSET en service_catalog.py y derivar
SERVICE_TO_ASSET_LOOKUP de ahí. SERVICE_CATALOG puede mantener metadatos adicionales pero
las keys deben coincidir con PROPOSAL_SERVICE_TO_ASSET.

**Criterios de aceptación**:
- [ ] SERVICE_TO_ASSET_LOOKUP tiene las mismas 8 entradas que PROPOSAL_SERVICE_TO_ASSET
- [ ] SERVICE_CATALOG tiene entradas para los mismos 8 servicios
- [ ] No hay servicios en SERVICE_CATALOG que no estén en PROPOSAL_SERVICE_TO_ASSET (o justificados)
- [ ] `_generate_asset_quality_table()` itera sobre la misma fuente que `_generate_dynamic_services_table()`
- [ ] Tests de proposal_dynamic pasan

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_proposal_dynamic.py` | `tests/test_proposal_dynamic.py` | Todos pasan + N nuevos |
| `test_proposal_asset_alignment.py` | `tests/quality_gates/test_proposal_asset_alignment.py` | 24/24 pasan |
| `test_service_catalog.py` | `tests/commercial_documents/test_service_catalog.py` | Si existe, pasa |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/test_proposal_dynamic.py tests/quality_gates/test_proposal_asset_alignment.py -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar FASE-3 como ✅ Completada.
2. **`README.md` del plan**: Actualizar tabla de progreso.
3. **`09-documentacion-post-proyecto.md`**:
   - **Sección B**: Agregar funcionalidad (propuesta condicional, unificación fuentes)
   - **Sección D**: Métricas
   - **Sección E**: Archivos (v4_proposal_generator.py, service_catalog.py)
4. **`evidence/fase-3/`**: Guardar diffs.
5. **log_phase_completion.py**:
   ```bash
   cd /mnt/c/Users/Jhond/Github/iah-cli
   ./venv/Scripts/python.exe scripts/log_phase_completion.py \
       --fase FASE-3-ASSET-ALIGNMENT \
       --desc "Propuesta condicional + unificación SERVICE_TO_ASSET_LOOKUP con PROPOSAL_SERVICE_TO_ASSET" \
       --archivos-mod "modules/commercial_documents/v4_proposal_generator.py,modules/commercial_documents/service_catalog.py" \
       --tests "2" \
       --check-manual-docs
   ```
6. **CHANGELOG.md y GUIA_TECNICA.md**: Editar con cambios.

---

## Criterios de Completitud (CHECKLIST)

- [ ] `_generate_dynamic_services_table()` excluye servicios sin asset ni present_in_production
- [ ] Nota al pie lista servicios excluidos
- [ ] SERVICE_TO_ASSET_LOOKUP tiene 8 entradas (mismas que PROPOSAL_SERVICE_TO_ASSET)
- [ ] SERVICE_CATALOG sincronizado con PROPOSAL_SERVICE_TO_ASSET
- [ ] `_generate_asset_quality_table()` usa misma fuente que `_generate_dynamic_services_table()`
- [ ] Tests nuevos pasan (2+)
- [ ] Tests existentes sin regresión
- [ ] `run_all_validations.py --quick` pasa
- [ ] `dependencias-fases.md` actualizado
- [ ] `09-documentacion-post-proyecto.md` actualizado
- [ ] `log_phase_completion.py` ejecutado
- [ ] CHANGELOG.md + GUIA_TECNICA.md editados
- [ ] `evidence/fase-3/` con diffs

---

## Restricciones

- **Máximo 60 iteraciones del agente por fase**
- **No ejecutar v4complete** (reservado para FASE-5)
- **No modificar** `pain_solution_mapper.py` (eso fue FASE-2)
- **No modificar** `publication_gates.py`
- **No modificar ROADMAP.md**
- **No eliminar** PROPOSAL_SERVICE_TO_ASSET (es la fuente de verdad, Gate 9 la usa)
- **No cambiar** el contenido de los servicios (nombres, descripciones) — solo la lógica de inclusión/exclusión

---

## Prompt de Ejecución (delegate_task subagente)

```
Actúa como especialista en Python con conocimiento del proyecto iah-cli.

OBJETIVO: Hacer la propuesta condicional (solo promete servicios con asset generado) + unificar 3 fuentes de verdad divergentes para servicios.

CONTEXTO:
- Proyecto: /mnt/c/Users/Jhond/Github/iah-cli
- Python: ./venv/Scripts/python.exe
- Versión actual: 4.62.0 (post-FASE-2)
- Problema 1: v4_proposal_generator.py _generate_dynamic_services_table() (L1110+) itera TODOS los 8 servicios de PROPOSAL_SERVICE_TO_ASSET siempre, sin verificar si el asset fue generado.
- Problema 2: 3 fuentes divergentes:
  1. proposal_asset_alignment.py:PROPOSAL_SERVICE_TO_ASSET (8 entradas, fuente de verdad para Gate 9)
  2. service_catalog.py:SERVICE_CATALOG (7+1 entradas)
  3. service_catalog.py:SERVICE_TO_ASSET_LOOKUP (derivado de SERVICE_CATALOG, divergente)
- "Informe Mensual" aparece en asset_quality_table pero NO en la tabla principal de servicios.

TAREAS:
1. En v4_proposal_generator.py _generate_dynamic_services_table():
   - Antes de agregar un servicio a la tabla, verificar:
     a) ¿El asset fue generado? (check asset_generation_report o asset_types generados)
     b) ¿Está marcado como present_in_production?
   - Si ni a ni b → excluir de la tabla principal, agregar a nota al pie
   - Formato nota: "Servicios adicionales disponibles: [lista]"
2. En service_catalog.py:
   - Importar PROPOSAL_SERVICE_TO_ASSET de proposal_asset_alignment
   - Derivar SERVICE_TO_ASSET_LOOKUP de PROPOSAL_SERVICE_TO_ASSET (no de SERVICE_CATALOG)
   - Sincronizar SERVICE_CATALOG: las keys deben coincidir con PROPOSAL_SERVICE_TO_ASSET (8 servicios)
   - Si SERVICE_CATALOG tiene entradas extra no en PROPOSAL_SERVICE_TO_ASSET, moverlas a un campo separado o eliminarlas
3. Verificar que _generate_asset_quality_table() itera sobre la misma fuente que _generate_dynamic_services_table()
4. Escribir 2 tests:
   - test_conditional_services: mock con 4/8 servicios con asset → tabla muestra 4 + nota con 4
   - test_unified_lookup: SERVICE_TO_ASSET_LOOKUP tiene 8 entradas iguales a PROPOSAL_SERVICE_TO_ASSET
5. Ejecutar: ./venv/Scripts/python.exe -m pytest tests/test_proposal_dynamic.py tests/quality_gates/test_proposal_asset_alignment.py -v
6. Ejecutar: ./venv/Scripts/python.exe scripts/run_all_validations.py --quick

CRITERIOS:
- Servicios sin asset ni present_in_production NO aparecen como "⏳ Pendiente" en la propuesta
- SERVICE_TO_ASSET_LOOKUP tiene 8 entradas (mismas que PROPOSAL_SERVICE_TO_ASSET)
- SERVICE_CATALOG sincronizado con PROPOSAL_SERVICE_TO_ASSET
- Tests nuevos pasan, existentes sin regresión
- run_all_validations.py --quick pasa

VALIDACIONES:
- grep -c "Servicios adicionales" en v4_proposal_generator.py (nota al pie implementada)
- python3 -c "from modules.commercial_documents.service_catalog import SERVICE_TO_ASSET_LOOKUP; from modules.asset_generation.proposal_asset_alignment import PROPOSAL_SERVICE_TO_ASSET; assert set(SERVICE_TO_ASSET_LOOKUP.keys()) == set(PROPOSAL_SERVICE_TO_ASSET.keys())"
```
