# FASE-PROP-B: WhatsApp Conflict Status en Propuesta

**Plan:** PROPOSAL-COMERCIAL-FIX v1.0.0
**Workflow:** `.agents/workflows/phased_project_executor.md` v2.10.0
**Presupuesto:** 60 iteraciones max | **Estimado esta fase:** ~35 iteraciones
**Dependencias:** FASE-PROP-A ✅ (ideal, no estricto)
**Fase siguiente:** FASE-PROP-C

## Contexto

En `v4_proposal_generator.py:1014-1017`:

```python
if presence_verified and present_in_production:
    return ("✅ Verificado en sitio", "Ya existe en su web - nosotros lo entregamos")
```

Este código NUNCA consulta `whatsapp_status` del `audit_report`. Si el audit detecta `whatsapp_status="conflict"` (número landline en web ≠ móvil en GBP), el código igual dice "✅ Verificado".

**Live site verificado**: Hotelcastillareal tiene Joinchat v6.0.10 con teléfono 573104692201. El landline en footer es +57 (606) 333 2192. El botón existe pero hay conflicto de números.

**Objetivo**: Cuando `whatsapp_status == "conflict"`, la propuesta debe mostrar ⚠️ Conflicto detectado en lugar de ✅ Verificado.

## Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-PROP-A | ✅ Completada |

## Base Técnica Disponible

- `modules/commercial_documents/v4_proposal_generator.py` (L1014-1017): `_get_asset_status()`
- `audit_report.json` (actualmente sobrescrito por Termales, pero el patrón es sistémico): campo `whatsapp_status`
- Contexto validado: enum puede ser `"conflict"`, `"CONFLICT"`, o `ConfidenceLevel.CONFLICT`

## Tareas Específicas

### Tarea 1: Verificar enum real de whatsapp_status
**Objetivo**: Confirmar el string/enum exacto que usa el audit report.

**Archivos afectados**:
- `modules/data_validation/` o `modules/auditors/` (buscar definición de whatsapp_status)
- `modules/commercial_documents/v4_proposal_generator.py` (buscar uso actual)

**Criterios de aceptación**:
- [ ] Encontrar la clase/enum donde se define `whatsapp_status`
- [ ] Confirmar valores posibles: `"verified"`, `"conflict"`, `"estimated"`, `"missing"`, etc.
- [ ] Documentar el string exacto a comparar

### Tarea 2: Agregar check de conflict en _get_asset_status()
**Objetivo**: Antes de evaluar `presence_verified`, verificar si hay conflicto de WhatsApp.

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py` (L1014~)

**Criterios de aceptación**:
- [ ] Lógica agregada ANTES del bloque `if presence_verified and present_in_production:`
- [ ] Condición: si `audit_report` existe y `audit_report.validation.whatsapp_status == "conflict"` (o el enum correcto)
- [ ] Retorno: `("⚠️ Conflicto detectado", "Requiere resolución manual - números no coinciden")`

### Tarea 3: Asegurar mensaje claro en propuesta
**Objetivo**: El mensaje de conflicto sea visible y honesto comercialmente.

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py`

**Criterios de aceptación**:
- [ ] El mensaje NO dice "nosotros lo entregamos" cuando hay conflicto
- [ ] El mensaje explica brevemente qué debe resolver el cliente (o nosotros en onboarding)
- [ ] Si no hay conflicto, el comportamiento anterior se preserva (✅ Verificado)

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Test WhatsApp conflict | `tests/commercial_documents/test_proposal_generator.py` | Cuando audit_report.whatsapp_status="conflict", _get_asset_status retorna ⚠️ |
| Test WhatsApp OK | (mismo archivo) | Cuando status="verified" y present_in_production=True, retorna ✅ |
| Test sin audit_report | (mismo archivo) | Cuando no hay audit_report, no falla (manejo seguro de None) |

**Comando de validación**:
```bash
venv/Scripts/python.exe -m pytest tests/commercial_documents/test_proposal_generator.py -v -k whatsapp
venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Archivos Involucrados

| Archivo | Tipo de Cambio | Líneas Aprox. |
|---------|---------------|--------------|
| `modules/commercial_documents/v4_proposal_generator.py` | Modificación | L1014~ (_get_asset_status) |

## Criterios de Completitud (CHECKLIST)

- [x] **Enum verificado**: Se conoce el valor exacto de `whatsapp_status` para conflicto
- [x] **Check implementado**: `_get_asset_status()` detecta conflicto antes de presence_verified
- [x] **Mensaje honesto**: No dice "nosotros lo entregamos" cuando hay conflicto
- [x] **Backwards compatible**: Si no hay conflicto, comportamiento idéntico al anterior
- [x] **Tests pasan**: Nuevos tests pasan, tests existentes no se rompen
- [x] **Validaciones del proyecto**: `run_all_validations.py --quick` pasa 4/4
- [x] **Documentación afiliada**: cambios reflejados

## Restricciones

- **NO modificar** la lógica de detección de WhatsApp en el audit — solo cómo se presenta en la propuesta
- **NO cambiar** `presence_verified` ni `present_in_production` — solo agregar el check de conflicto ANTES
- **Máximo 60 iteraciones** (R2)

## Post-Ejecución (OBLIGATORIO)

1. **Estado**: ✅ COMPLETADA (2026-05-06)
2. **Iteraciones usadas**: ~12
3. **Tests**: 8/8 pasaron
4. **Validaciones**: 4/4 pasaron
5. **Archivos modificados**:
   - `modules/commercial_documents/v4_proposal_generator.py` (L987~, L926~, L969, L987)
6. **Archivos nuevos**:
   - `tests/commercial_documents/test_proposal_generator.py`
7. **log_phase_completion.py**: Ejecutado ✅

**Siguiente fase:**
```
Carga y ejecuta .opencode/plans/05-prompt-inicio-sesion-fase-PROP-C.md siguiendo .agents/workflows/phased_project_executor.md
```
