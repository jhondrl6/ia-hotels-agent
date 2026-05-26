# FASE-C: Mapping brecha→servicio (CROSS-2) + WhatsApp conflict (CROSS-4)

**ID**: FASE-C
**Objetivo**: Agregar trazabilidad brecha→servicio en la tabla de propuesta + corregir el indicador de WhatsApp para reflejar el conflicto detectado.
**Dependencias**: FASE-B (el template de propuesta ya tiene el puente dual)
**Duración estimada**: 1-2 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

La auditoría identificó:

- **CROSS-2**: El diagnóstico identifica 7 brechas con costos específicos, pero la propuesta lista 8 servicios sin indicar cuál resuelve cuál. Las brechas 2 ("Metadatos CMS") y 3 ("Baja preparación IA") son AMBIGUAS — el cliente no puede verificar que su problema será resuelto. El asset `optimization_guide` tiene confidence=0.5 (el más bajo).

- **CROSS-4**: La propuesta muestra "Botón de WhatsApp | ℹ️ Presente en sitio" (implica que todo está bien), pero el diagnóstico alerta "🚨 Conflicto de WhatsApp detectado" (números no coinciden). La propuesta debe reflejar el conflicto.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada (asumido) |
| FASE-B | ✅ Completada (asumido) |

### Base Técnica Disponible

- Tabla de servicios: `_generate_dynamic_services_table()` en `v4_proposal_generator.py`
- Tabla de assets técnicos: `_generate_technical_assets_table()` en `v4_proposal_generator.py`
- Template propuesta: `propuesta_v6_template.md` — sección de servicios (alrededor de L47)
- WhatsApp: el flag `whatsapp_conflict_detected` ya existe en el diagnóstico; verificar si el generador de propuesta tiene acceso
- Datos de brechas: disponibles en `diagnostic_summary` dentro del generador de propuesta

---

## Tareas

### Tarea 1: Investigar estructura de datos de brechas en el generador de propuesta

**Objetivo**: Determinar qué datos de brechas están disponibles en `v4_proposal_generator.py` para construir el mapping.

**Archivos a investigar**:
- `modules/commercial_documents/v4_proposal_generator.py` — buscar `diagnostic_summary`, `breach`, `gap`
- `modules/commercial_documents/data_structures.py` — clase `DiagnosticSummary`

**Comandos**:
```bash
grep -n 'breach\|gap\|diagnostic_summary' modules/commercial_documents/v4_proposal_generator.py | head -30
grep -n 'class DiagnosticSummary' modules/commercial_documents/data_structures.py
```

**Criterios de aceptación**:
- [ ] Documentar qué campos de brechas están disponibles (nombre, costo, score)
- [ ] Identificar si hay un mapping service→breach existente (aunque incompleto)

### Tarea 2: Agregar mapping brecha→servicio en tabla de propuesta

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py` — `_generate_dynamic_services_table()`

**Cambio**: Agregar una columna "Problema que resuelve" a la tabla de servicios con el formato `Brecha #N: [nombre] ($X/mes)`.

Si los datos de brechas no están disponibles directamente, crear un mapping manual basado en la tabla de la auditoría:
```python
SERVICE_TO_BREACH = {
    "hotel_schema": ("Brecha #1: Sin Schema Hotel", "$1,005,768/mes"),
    "optimization_guide": ("Brecha #2: Metadatos CMS", "$402,232/mes"),
    "llms_txt": ("Brecha #3: Baja preparación IA", "$603,536/mes"),
    "local_content_page": ("Brecha #3: Baja preparación IA", "$603,536/mes"),
    "faq_page": ("Brecha #4: Sin FAQ", "$482,679/mes"),
    "og_tags_guide": ("Brecha #5: IA sin guía", "$603,536/mes"),
    "open_graph": ("Brecha #6: Sin OG Tags", "$321,786/mes"),
    "org_schema": ("Brecha #7: Sin Schema Org", "$321,786/mes"),
}
```

**Criterios de aceptación**:
- [ ] Cada servicio muestra qué brecha(s) del diagnóstico resuelve
- [ ] El costo de la brecha es visible (conecta urgencia con solución)
- [ ] La tabla no se rompe con la nueva columna (anchos, formato markdown)

### Tarea 3: Corregir indicador de WhatsApp en propuesta

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py` — donde se genera la fila de WhatsApp en la tabla de presencia digital.

**Cambio**: Si `whatsapp_conflict_detected == True`, mostrar:
```
Botón de WhatsApp | ⚠️ Requiere corrección (guía incluida)
```
En lugar de:
```
Botón de WhatsApp | ℹ️ Presente en sitio
```

**Verificación**:
```bash
grep -n 'WhatsApp\|whatsapp' modules/commercial_documents/v4_proposal_generator.py
```

**Criterios de aceptación**:
- [ ] WhatsApp conflict → indicador de advertencia con referencia a la guía
- [ ] WhatsApp sin conflict → mantiene indicador actual "Presente en sitio"

### Tarea 4: Verificar tests y coherencia de templates

**Objetivo**: Ejecutar tests de propuesta para confirmar que los cambios no introducen regresiones.

**Comandos**:
```bash
pytest tests/commercial_documents/ -v -k "proposal" --timeout=60
python scripts/run_all_validations.py --quick
```

**Criterios de aceptación**:
- [ ] Tests de propuesta pasan (o se actualizan si es necesario)
- [ ] `run_all_validations.py --quick` pasa

---

## Tests Obligatorios

| Test | Comando | Criterio |
|------|---------|----------|
| Tests de propuesta | `pytest tests/commercial_documents/ -v -k "proposal" --timeout=60` | Sin regresiones |
| Validación rápida | `python scripts/run_all_validations.py --quick` | 4/4+ checks |

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar FASE-C como ✅ Completada
2. **`06-checklist-implementacion.md`**: Marcar items C1-C4 como ✅
3. **`09-documentacion-post-proyecto.md`**: Agregar cambios
4. Ejecutar:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-C \
    --desc "CROSS-2: Mapping brecha→servicio en propuesta + CROSS-4: WhatsApp conflict reflejado" \
    --archivos-mod "modules/commercial_documents/v4_proposal_generator.py" \
    --tests "0" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] Tabla de servicios incluye columna "Problema que resuelve" con referencia a brecha
- [ ] Las 7 brechas del diagnóstico están mapeadas a los 8 servicios
- [ ] WhatsApp conflict → "⚠️ Requiere corrección (guía incluida)"
- [ ] WhatsApp sin conflict → mantiene "ℹ️ Presente en sitio"
- [ ] `run_all_validations.py --quick` pasa
- [ ] `dependencias-fases.md` actualizado
- [ ] `06-checklist-implementacion.md` actualizado
- [ ] `09-documentacion-post-proyecto.md` actualizado
- [ ] `log_phase_completion.py` ejecutado

---

## Restricciones

- NO modificar templates de diagnóstico
- NO ejecutar v4complete
- NO modificar la lógica de detección de WhatsApp — solo la presentación
- Máximo 60 iteraciones de agente
