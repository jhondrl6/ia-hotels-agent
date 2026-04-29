# FASE-PATCH-B: Hardcoded Placeholders + Evidence Integrity

**ID**: FASE-PATCH-B
**Objetivo**: Corregir H-1 (web_score "85" hardcodeado), H-2 (teléfono placeholder), H-6 (Evidence Tier siempre "C")
**Dependencias**: FASE-PATCH-A ✅ (modifica `v4_proposal_generator.py` — aplicar cambios SOBRE código ya modificado)
**Duración estimada**: ~40-50 min
**Skill**: iah-cli-phased-execution

---

## Contexto

La auditoría reveló 3 hardcodes que producen datos falsos en el entregable:

- **H-1**: `v4_proposal_generator.py` L554 tiene `web_score = "85"` como placeholder. El comentario del dev dice `"ideally from audit"`. Si no llega audit_result, la propuesta muestra SEO score 85 en vez del real (25 en AmaziliaHotel).
- **H-2**: `two_phase_flow.py` L553 contiene `"+57 300 123 4567"` — un placeholder de teléfono en código de producción.
- **H-6**: `scenario_calculator.py` L443 fuerza `Evidence Tier = "C"` siempre, sin importar si hay GA4 u otros datos reales.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-1-AMAZILIA-CORRECCION (1A/1B/1C) | ✅ Completada |
| FASE-PATCH-A | ✅ Completada (BUG-1, BUG-2, H-3/4/5, unicode) |

### ⚠️ ALERTA DE CONFLICTO

`v4_proposal_generator.py` fue modificado en FASE-PATCH-A. Las líneas pueden haberse desplazado. **Leer el archivo actual antes de aplicar fixes.** Las referencias de línea en este prompt son aproximadas y deben verificarse contra el código real post-PATCH-A.

### Base Técnica Disponible

- `modules/commercial_documents/v4_proposal_generator.py` — MODIFICADO por PATCH-A (verificar L554 actual)
- `modules/orchestration_v4/two_phase_flow.py` — H-2 L553
- `modules/financial_engine/scenario_calculator.py` — H-6 L443
- `output/v4_complete/amaziliahotel/v4_audit/` — contiene audit_result con seo_score real
- `data_models/analytics_status.py` — AnalyticsStatus con GA4 detection

---

## Tareas

### Tarea 1: Investigar hardcodes en código actual

**Objetivo**: Leer las líneas exactas en el código post-PATCH-A y confirmar las causas raíz.

**Archivos a leer**:
- `modules/commercial_documents/v4_proposal_generator.py`: buscar `"85"` o `web_score` cerca de la sección de template data
- `modules/orchestration_v4/two_phase_flow.py`: buscar `"+57 300` o placeholder de teléfono
- `modules/financial_engine/scenario_calculator.py`: buscar `"C"` o `evidence_tier` o `tier =`
- `modules/commercial_documents/v4_proposal_generator.py`: verificar si `audit_result` está disponible en `_prepare_template_data()` y cómo se pasa `seo_score`

**Criterios de aceptación**:
- [ ] Confirmada ubicación exacta de H-1 (web_score placeholder)
- [ ] Confirmada ubicación exacta de H-2 (teléfono placeholder)
- [ ] Confirmada ubicación exacta de H-6 (Evidence Tier hardcodeado)
- [ ] Entendido el flujo de `audit_result` → template data para web_score

### Tarea 2: Fix H-1 (web_score) en v4_proposal_generator.py

**Objetivo**: Usar audit_result SEO score real en vez del placeholder "85".

**Estrategia**:
```python
# Actual (aproximado):
'web_score': '85',  # placeholder

# Cambiar a:
# Opción A — usar audit_result si existe:
'web_score': str(audit_result.get('seo_score', 'N/D')) if audit_result else 'N/D',

# Opción B — si audit_result no está disponible en este scope, marcar explícitamente:
'web_score': 'No disponible (requiere auditoría)',  
```

**Nota**: Si `audit_result` no está accesible en `_prepare_template_data()`, usar Opción B con un marcador honesto. El objetivo NO es calcular el score (eso es responsabilidad del auditor), sino NO MENTIR con un "85" falso.

**Criterios de aceptación**:
- [ ] web_score ya NO es "85" hardcodeado
- [ ] Usa audit_result real o muestra "No disponible" explícito
- [ ] No rompe el template (el placeholder `${web_score}` debe recibir un string)

### Tarea 3: Fix H-2 (teléfono) + H-6 (Evidence Tier)

**Objetivo**: Eliminar placeholders de teléfono y corregir Evidence Tier.

**H-2 fix en two_phase_flow.py**:
```python
# Buscar y reemplazar el placeholder:
"+57 300 123 4567" → extraer de config o usar valor de validated_data/hotel_schema
# Si no hay fuente de datos, usar marcador explícito:
"[Teléfono no configurado]"
```

**H-6 fix en scenario_calculator.py**:
```python
# Actual (aproximado L443):
evidence_tier = "C"  # hardcodeado sin GA4

# Cambiar a: condicionar a presencia real de analytics
if analytics_data and analytics_data.get('ga4_available'):
    evidence_tier = "A"  # o calcular basado en datos reales
elif analytics_data and analytics_data.get('any_analytics'):
    evidence_tier = "B"
else:
    evidence_tier = "C"  # solo cuando realmente no hay datos
```

**Criterios de aceptación**:
- [ ] Teléfono placeholder "+57 300 123 4567" reemplazado por valor real o marcador honesto
- [ ] Evidence Tier ya NO es siempre "C" — condicionado a presencia real de datos
- [ ] No se introducen errores de sintaxis o imports faltantes

### Tarea 4: Ejecutar tests + documentación de fase

```bash
# Ejecutar tests relevantes
./venv/Scripts/python.exe -m pytest tests/financial_engine/ -x -q --tb=short
./venv/Scripts/python.exe -m pytest tests/commercial_documents/ -x -q --tb=short
./venv/Scripts/python.exe -m pytest tests/orchestration_v4/ -x -q --tb=short

# Documentar fase
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-PATCH-B \
    --desc "Fix H-1 (web_score placeholder), H-2 (telefono placeholder), H-6 (Evidence Tier hardcodeado)" \
    --archivos-mod "modules/commercial_documents/v4_proposal_generator.py,modules/orchestration_v4/two_phase_flow.py,modules/financial_engine/scenario_calculator.py" \
    --check-manual-docs
```

**Criterios de aceptación**:
- [ ] Tests pasan sin regresiones
- [ ] log_phase_completion.py ejecutado

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Tests de financial engine | `tests/financial_engine/` | Sin regresiones |
| Tests de commercial documents | `tests/commercial_documents/` | Sin regresiones |
| Tests de orchestration | `tests/orchestration_v4/` | Sin regresiones |

---

## Post-Ejecución (OBLIGATORIO)

1. Actualizar `dependencias-fases-v2.md`: marcar FASE-PATCH-B como ✅
2. Actualizar `06-checklist-implementacion-v2.md`
3. Actualizar `README-v2.md`: tabla de progreso

---

## Criterios de Completitud (CHECKLIST)

- [ ] H-1: web_score usa audit_result real o "No disponible"
- [ ] H-2: teléfono placeholder eliminado de two_phase_flow.py
- [ ] H-6: Evidence Tier condicionado a datos reales
- [ ] Tests pasan sin regresiones
- [ ] log_phase_completion.py ejecutado

---

## Restricciones

- **NO ejecutar** v4complete (eso es PATCH-C)
- **NO modificar** VERSION.yaml
- **Leer v4_proposal_generator.py ANTES de modificar** — las líneas pueden haberse desplazado por PATCH-A
- **Máximo 60 iteraciones**
