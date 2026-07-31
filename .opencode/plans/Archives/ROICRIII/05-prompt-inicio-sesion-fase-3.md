# FASE-3 — Validator Semántico + BREACH_BY_ASSET + WhatsApp (B1+B2+B6)

**ID**: ROICRIII-FASE-3
**Objetivo**: Integrar `asset_semantics_validator` en la tabla de servicios de la propuesta y corregir mapeos semánticos incorrectos.
**Dependencias**: FASE-2 ✅ (pain ratio + trazabilidad corregidos)
**Complejidad**: 🟡 MEDIA — Integrar validador existente en nuevo scope
**Skill**: `iah-cli-phased-execution`

---

## Contexto

`asset_semantics_validator.py` EXISTE (verificado en FASE-2 del plan ROICR) y valida correctamente qué asset resuelve qué brecha. Está integrado en `pain_solution_mapper.py` y `publication_gates.py`, pero **NO** en `_generate_dynamic_services_table()` del generator de propuestas.

Resultado: la tabla de servicios muestra "Informe Mensual → #4: Sin FAQ" (incorrecto). El validator bloquearía este mapeo, pero como no está integrado aquí, pasa sin filtro.

Además, `BREACH_BY_ASSET` hardcodea mapeos estáticos que incluyen assets deprecados y narrativa de WhatsApp confusa ("⚠️ Requiere corrección" + "Guía de corrección incluida").

---

## Tareas

### T1: Integrar asset_semantics_validator en services table [B1]

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py`

En `_generate_dynamic_services_table()`:

1. **Verificar import**: Grep para `asset_semantics_validator` en el archivo. Si no está importado:
```python
from modules.quality.asset_semantics_validator import validar_semantica_comercial
```

2. **Verificar firma de la función**: Leer `modules/quality/asset_semantics_validator.py` para confirmar la firma exacta de `validar_semantica_comercial(pain_id, asset_id, asset_status)`.

3. **Crear mapping directo** asset_type → pain_id (NO usar SERVICE_CATALOG lookup frágil):
```python
ASSET_TO_PAIN_ID = {
    "monthly_report": "no_faq_schema",
    "faq_page": "no_faq_schema",
    "hotel_schema": "no_hotel_schema",
    "llms_txt": "missing_llmstxt",
    "whatsapp_button": "no_whatsapp_visible",
    "whatsapp_conflict_guide": "no_whatsapp_visible",
}
```

4. **Añadir validación** en el loop que construye filas de la tabla: antes de construir cada row, validar:
```python
pain_id = ASSET_TO_PAIN_ID.get(asset_type)
if pain_id:
    is_valid, status = validar_semantica_comercial(pain_id, asset_type, "IMPLEMENT")
    if not is_valid:
        logger.warning(f"[AssetSemantics] BLOCKED: {asset_type} → {pain_id}")
        continue  # skip this row
```

**NOTA**: Verificar las claves CORRECTAS del validator. Grep para `INVALID_MAPPINGS` en `asset_semantics_validator.py`. Las claves deben ser pain_ids (prefijo `no_` o `missing_`), NO asset_ids.

**Criterios**:
- [ ] `grep "validar_semantica_comercial" v4_proposal_generator.py` muestra el import y uso
- [ ] `ASSET_TO_PAIN_ID` dict existe con mapping directo
- [ ] Filas bloqueadas por el validator no aparecen en la tabla de servicios

### T2: Corregir BREACH_BY_ASSET [B2]

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py`

Grep para `BREACH_BY_ASSET` en `_generate_dynamic_services_table()`.

**Correcciones**:
- `monthly_report` → cambiar de `("#4", "Sin FAQ", "$482.679")` a `("—", "Informe de rendimiento", "—")`
- ELIMINAR entradas de `"optimization_guide"` y `"local_content_page"` si existen (son deprecados)

**Criterios**:
- [ ] `monthly_report` NO mapea a FAQ
- [ ] No hay entradas de assets deprecados en BREACH_BY_ASSET

### T3: Corregir narrativa WhatsApp [B6]

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py`

Grep para `whatsapp_conflict` o `"Guía de corrección"` en `_generate_dynamic_services_table()`.

**Corrección**: Cuando `whatsapp_conflict` es True, AMBOS campos deben ser coherentes:

**ANTES** (patrón a buscar):
```python
estado = "⚠️ Requiere corrección"
desc = "Guía de corrección incluida"
```

**DESPUÉS**:
```python
estado = "📋 Auditoría incluida"
desc = "Auditoría y Optimización de Conversión"
```

**Criterios**:
- [ ] `grep "Guía de corrección" v4_proposal_generator.py` → vacío
- [ ] `grep "Auditoría y Optimización" v4_proposal_generator.py` → existe
- [ ] Estado y descripción son coherentes entre sí

---

## Tests Obligatorios

| Test | Archivo | Criterio |
|------|---------|----------|
| `test_monthly_report_no_resuelve_faq` | `tests/quality/test_asset_semantics_integration.py` | BLOCKED |
| `test_faq_page_si_resuelve_faq` | `tests/quality/test_asset_semantics_integration.py` | IMPLEMENT |
| `test_mapeos_no_invertidos` | `tests/quality/test_asset_semantics_integration.py` | pain_ids correctos |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/quality/test_asset_semantics_integration.py -v
./venv/Scripts/python.exe -m pytest tests/ -v --tb=short
```

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`** — Marcar FASE-3 como ✅ Completada
2. **`06-checklist-implementacion.md`** — Actualizar estado
3. **`09-documentacion-post-proyecto.md`** — Secciones B + C
4. **log_phase_completion.py**:
```bash
cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe" scripts/log_phase_completion.py --fase FASE-3 --desc "Validator_BREACH_WhatsApp_B1_B2_B6" --archivos-mod "modules/commercial_documents/v4_proposal_generator.py" --tests "3" --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] `asset_semantics_validator` integrado en `_generate_dynamic_services_table`
- [ ] BREACH_BY_ASSET corregido (monthly_report ≠ FAQ, sin deprecados)
- [ ] Narrativa WhatsApp coherente (auditoría, no corrección)
- [ ] 3 tests nuevos pasan + no regresiones
- [ ] run_all_validations.py --quick pasa
- [ ] Post-ejecución completada

---

## Restricciones

- NO modificar `asset_semantics_validator.py` (ya fue corregido en FASE-2 de ROICR)
- NO modificar `pain_solution_mapper.py` ni `publication_gates.py`
- Verificar firma exacta de `validar_semantica_comercial` antes de llamarla
- Límite: 60 iteraciones
