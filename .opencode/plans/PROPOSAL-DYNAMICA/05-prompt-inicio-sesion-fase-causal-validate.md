# FASE-CAUSAL-VALIDATE: Verificación de Refactor y Unitaria

**ID**: FASE-CAUSAL-VALIDATE  
**Objetivo**: Verificar que el refactor genera propuesta dinámica desde pains detectados mediante tests unitarios e inspección de código (sin E2E v4complete)  
**Dependencias**: FASE-CAUSAL-REFACTOR  
**Duración estimada**: 1-2 horas  
**Skill**: Verificación unitaria

---

## Contexto

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-CAUSAL-DIAG | ✅ Completada |
| FASE-CAUSAL-REFACTOR | ✅ Completada |

### Base Técnica Disponible
- Código refactorizado con `SERVICE_CATALOG`
- Tests: 13/13 en `test_proposal_alignment.py`
- Módulos: `v4_proposal_generator.py`, `service_catalog.py`

### Objetivo de Validación
Verificar que la propuesta ahora muestra SOLO los servicios cuyos pains fueron detectados, y que todos los pains detectados tienen servicio correspondiente.

---

## Tareas

### Tarea 1: Ejecutar Tests Unitarios

> NOTA: Esta fase NO ejecuta v4complete E2E (eso ocurre UNA SOLA VEZ en FASE-RELEASE para minimizar costos API).

**Objetivo**: Verificar que los tests unitarios pasan con el código refactorizado.

**Acciones**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Tests de proposal_alignment (backwards compat)
./venv/Scripts/python.exe -m pytest tests/asset_generation/test_proposal_alignment.py -v
```

### Tarea 2: Verificar SERVICE_CATALOG en Código

**Objetivo**: Confirmar que SERVICE_CATALOG existe y tiene el mapeo correcto.

**Acciones**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Verificar que SERVICE_CATALOG existe y tiene entradas
./venv/Scripts/python.exe -c "
import sys
sys.stdout.reconfigure(encoding='utf-8')
from modules.commercial_documents.service_catalog import SERVICE_CATALOG
print(f'Servicios en SERVICE_CATALOG: {len(SERVICE_CATALOG)}')
for name, entry in SERVICE_CATALOG.items():
    print(f'  {name} -> pain_id={entry.pain_id}, asset={entry.asset_type}')
"
```

**Criterio**: SERVICE_CATALOG tiene al menos 7 entradas, cada una con pain_id válido.

### Tarea 3: Verificar _generate_asset_quality_table Usa Pains

**Objetivo**: Confirmar que la refactorización itera sobre pains detectados.

**Acciones**:
```bash
# Verificar en código fuente que la función usa detected_pains
./venv/Scripts/python.exe -c "
import inspect, sys
sys.stdout.reconfigure(encoding='utf-8')
from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator
sig = inspect.signature(V4ProposalGenerator._generate_asset_quality_table)
print(f'Parámetros: {list(sig.parameters.keys())}')
has_pains = 'detected_pains' in sig.parameters
print(f'Usa detected_pains: {has_pains}')
"
```

**Criterio**: `_generate_asset_quality_table` acepta `detected_pains` como parámetro.

### Tarea 4: Ejecutar Validaciones

**Acciones**:
```bash
./venv/Scripts/python.exe -m pytest tests/asset_generation/test_proposal_alignment.py -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

**Criterio**: 13/13 tests PASS y 4/4 validaciones.

---

### Tarea 4: Crear Test de Propuesta Dinámica

**Objetivo**: Verificar que la propuesta realmente filtra servicios según los pains detectados.

**Archivos afectados**: `tests/commercial_documents/test_proposal_dynamic.py` (nuevo)

**Acciones**:
- Crear test que mockee `pain_solution_mapper.detect_pains()` retornando solo 2-3 pains específicos
- Llamar `_generate_asset_quality_table()` con esos pains detectados
- Verificar que la tabla generada SOLO incluye servicios para esos pains
- Verificar que servicios para pains NO detectados NO aparecen en la tabla
- Verificar que si un pain detectado no tiene servicio en SERVICE_CATALOG, se maneja gracefulmente

**Criterio**: El test prueba el comportamiento dinámico real, no solo backwards compatibility.

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Alignment | `test_proposal_alignment.py` | 13/13 PASS |
| SERVICE_CATALOG | import check | >= 7 entradas con pain_id válido |
| Refactor signature | inspect check | `_generate_asset_quality_table` acepta `detected_pains` |
| Propuesta dinámica | `test_proposal_dynamic.py` | PASS: solo servicios de pains detectados |
| Validations | `run_all_validations.py` | 4/4 PASS |

**Comando de validación**:
```bash
./venv/Scripts/python.exe -m pytest tests/asset_generation/test_proposal_alignment.py -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`**
   - Marcar FASE-CAUSAL-VALIDATE como ✅ Completada
   - Actualizar fecha de finalización

2. **`README.md` del plan**
   - Actualizar tabla de progreso
   - Anotar resultados de validación

3. **`evidence/fase-causal-validate/`**
   - Guardar logs de ejecución
   - Guardar propuesta generada para evidencia

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] Tests 13/13 PASS (backwards compat)
- [ ] SERVICE_CATALOG importable con >= 7 entradas y pain_id válido
- [ ] `_generate_asset_quality_table` acepta `detected_pains`
- [ ] Test `test_proposal_dynamic.py` creado y pasa: solo servicios de pains detectados
- [ ] Validaciones 4/4 PASS
- [ ] **NO se ejecutó v4complete E2E** (eso es solo en FASE-RELEASE)
- [ ] `test_proposal_alignment.py` pasa 13/13
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] Post-ejecución completada

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- **Sin E2E v4complete**: Esta fase NO ejecuta v4complete. Solo tests unitarios y verificación de código.
- **Costo API cero**: Validación sin llamadas a API externas.
- **Evidencia**: Documentar resultados de tests y verificaciones en el plan.

---

## Prompt de Ejecución

```
Actúa como QA engineer. Tu objetivo es verificar que la refactorización de propuesta dinámica es correcta.

CONTEXTO:
- FASE-CAUSAL-REFACTOR completada: SERVICE_CATALOG creado, generador refactorizado
- Esta fase NO ejecuta v4complete E2E (eso es solo en FASE-RELEASE para minimizar costos API)

TAREAS:
1. Ejecutar tests: pytest tests/asset_generation/test_proposal_alignment.py -v (13/13)
2. Verificar SERVICE_CATALOG importable con >= 7 entradas y pain_id válido
3. Verificar que _generate_asset_quality_table acepta detected_pains como parámetro
4. Crear test_proposal_dynamic.py: mockear pains detectados y verificar que solo aparecen servicios para esos pains
5. Ejecutar validaciones: run_all_validations.py --quick (4/4)
6. NO ejecutar v4complete — reservado para FASE-RELEASE

CRITERIOS:
- Tests 13/13 PASS
- SERVICE_CATALOG válido
- Función refactorizada acepta detected_pains
- test_proposal_dynamic.py pasa: propuesta filtra servicios por pains detectados
- Validaciones 4/4 PASS
- Sin llamadas a API (costo cero)
```
