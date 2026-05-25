# FASE-C: Puente 7 Brechas → 3 Fugas (F3) + Encabezado "+$" → "Fuga Mensual" (F4)

**ID**: FASE-C
**Objetivo**: Corregir 2 fricciones de navegación/claridad: (F3) texto puente entre Sección 2 y 4, (F4) encabezado de columna en tabla resumen.
**Dependencias**: FASE-A ✅, FASE-B ✅ (deseables, no bloqueantes)
**Duración estimada**: 30-60 minutos
**Skill**: `phased_project_executor`

---

## Contexto

- **F3**: Sección 2 lista 7 brechas, Sección 4 lista 3 fugas — sin conexión. El dueño pregunta "¿y las otras 4?".
- **F4**: Tabla resumen usa "+$" sin encabezado claro. El dueño no sabe si es pérdida o recuperación.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A | ⏳ Pendiente |
| FASE-B | ⏳ Pendiente |

---

## Tareas

### Tarea 1: Localizar puntos de inserción (F3 + F4)

**Archivos a investigar**:
- `modules/commercial_documents/templates/diagnostico_v6_template.md` L58-68 (Sección 4)
- `modules/commercial_documents/v4_diagnostic_generator.py` — `_build_brechas_resumen_section()`

**Criterios**:
- [ ] Confirmado punto de inserción para texto puente
- [ ] Localizado `_build_brechas_resumen_section()` y su formato de output

### Tarea 2: Agregar texto puente 7 brechas → 3 fugas (F3)

**Objetivo**: Insertar en template v6, después del título "## 4. 🔍 LAS 3 FUGAS PRINCIPALES":

```
De las 7 brechas técnicas detectadas, estas 3 son las que más dinero le están costando HOY.
Las otras 4 se resuelven en el plan completo de la Fase 2.
```

**Archivos afectados**: `modules/commercial_documents/templates/diagnostico_v6_template.md`

**Criterios**:
- [ ] Texto visible entre título Sección 4 y Fuga 1
- [ ] Explica relación 7 brechas → 3 fugas
- [ ] Menciona Fase 2 como resolución de las otras 4

### Tarea 3: Cambiar "+$" → "Fuga mensual estimada" (F4)

**Objetivo**: Modificar `_build_brechas_resumen_section()` para usar encabezado semántico.

**Archivos afectados**: `modules/commercial_documents/v4_diagnostic_generator.py`

**Criterios**:
- [ ] Columna tiene encabezado "Fuga mensual estimada"
- [ ] Sin "+$" ambiguo
- [ ] Formato markdown correcto

### Tarea 4: Verificar

```bash
python scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-C \
    --desc "Fix F3 (puente 7 brechas → 3 fugas) + F4 (encabezado Fuga mensual estimada)" \
    --archivos-mod "modules/commercial_documents/templates/diagnostico_v6_template.md,modules/commercial_documents/v4_diagnostic_generator.py" \
    --tests "0" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] F3: Texto puente agregado en Sección 4
- [ ] F4: Encabezado "Fuga mensual estimada" en tabla resumen
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] `dependencias-fases.md` actualizado
- [ ] `06-checklist-implementacion.md` actualizado
- [ ] `09-documentacion-post-proyecto.md` actualizado
- [ ] `log_phase_completion.py` ejecutado

---

## Restricciones

- NO modificar lógica de detección de brechas
- NO ejecutar v4complete
- Máximo 60 iteraciones de agente
