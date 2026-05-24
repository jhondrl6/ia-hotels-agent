# FASE-A-02b: Implementación de Nota de Contexto para WhatsApp Conflict

**ID**: FASE-A-02b  
**Objetivo**: Agregar variable `${whatsapp_conflict_business_note}` en la sección de contexto del template diagnostico_v6, con phrasing de impacto de negocio que rivalice visualmente con las BRECHAS.  
**Dependencias**: FASE-A-02a (investigación completa)  
**Duración estimada**: 45-60 min  
**Skill**: systematic-debugging, constrained-content-generation

---

## Contexto

**Basado en hallazgos de FASE-A-02a** (leer `evidence/FASE-A-02a/hallazgos_02a.md` antes de comenzar):

El problema central: `whatsapp_conflict` aparece solo en la tabla `${manual_attention_table}` (sección "Validación de Calidad"), donde compite visualmente con items de menor urgencia. El hotelero que va directo a BRECHAS no lo ve.

**Ubicación objetivo**: Sección de contexto (`## 📍 CONTEXTO REGIONAL`) del template, después del paragraph de regional_context. Donde el hotelero lee "el reloj corre" y "por qué esto importa en la región".

**Phrasing requerido** (L 127 de FASE-A-01c):
> "Su Google Business muestra un número diferente al de su sitio — cada cliente que intenta reservar por WhatsApp desde Google podría estar escribiendo al número equivocado"

**Restricción de contenido**: Sin costo mensual (no tenemos activo para cuantificarlo).

### Base Técnica Disponible
- `modules/commercial_documents/v4_diagnostic_generator.py` — método `_prepare_template_data()` (L516) donde se wirean las variables de template
- `modules/commercial_documents/templates/diagnostico_v6_template.md` — template v6
- `evidence/FASE-A-02a/hallazgos_02a.md` — hallazgos de investigación

---

## Tareas

### Tarea 1: Leer hallazgos de FASE-A-02a
**Objetivo**: Asegurar que el contexto de investigación está disponible antes de implementar

**Criterios de aceptación**:
- [ ] `evidence/FASE-A-02a/hallazgos_02a.md` existe y fue leído
- [ ] Flujo actual documentado: cómo whatsapp_conflict llega a la tabla

### Tarea 2: Agregar variable de template en diagnostico_v6_template.md
**Objetivo**: Insertar `${whatsapp_conflict_business_note}` en la sección de contexto

**Archivos afectados**:
- `modules/commercial_documents/templates/diagnostico_v6_template.md`

**Criterios de aceptación**:
- [ ] Variable insertada en sección contexto, después de `${regional_context}` (línea ~44)
- [ ] El bloque visual incluye 🔴 ALERTA como prefijo para llamar la atención
- [ ] Phrasing de impacto de negocio: número不一致 → reserva perdida sin conocimiento del hotelero

### Tarea 3: Implementar método `_build_whatsapp_conflict_note` en v4_diagnostic_generator.py
**Objetivo**: Generar el contenido de la nota con datos reales del conflict

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py`

**ATENCIÓN — Verificación pre-ejecución (G1, G2)**:
- El método de wire es `_prepare_template_data()` (L516), NO `_generate_diagnostico_v6()` (NO EXISTE)
- Los números NO se extraen del dict `conflicts` (solo tiene `value` web + `discrepancies` string)
- Usar `audit_result.validation.phone_web` y `audit_result.validation.phone_gbp` directamente
- Verificar existencia de conflicto con `any(c.get('field_name') == 'whatsapp' for c in conflicts)`

**Criterios de aceptación**:
- [ ] Método nuevo `_build_whatsapp_conflict_note(audit_result)` creado
- [ ] Verifica existencia de conflicto whatsapp iterando `validation.conflicts`
- [ ] Obtiene números de `validation.phone_web` y `validation.phone_gbp` (NO del dict conflicts)
- [ ] Retorna string formateado con ambos números y phrasing de impacto de negocio
- [ ] Si NO hay conflicto whatsapp o los números son None: retorna string vacío
- [ ] Wireado en `_prepare_template_data()` → dict `data`, justo después de `'regional_context': regional_context` (L692)

### Tarea 4: Agregar lógica de generación condicional
**Objetivo**: La nota solo aparece cuando hay conflicto whatsapp real

**Criterios de aceptación**:
- [ ] Si `audit_result.validation.conflicts` contiene conflicto con `field_name='whatsapp'`: mostrar nota
- [ ] Si no hay conflicto whatsapp: `${whatsapp_conflict_business_note}` resuelve a string vacío

---

## Tests Obligatorios

|| Test | Archivo | Criterio de Éxito |
|------|--------|---------|-------------------|
|| `test_whatsapp_conflict_note_generated` | `tests/commercial_documents/test_diagnostic_generator.py` | Pasa con conflicto whatsapp → nota no vacía |
|| `test_whatsapp_conflict_note_empty` | `tests/commercial_documents/test_diagnostic_generator.py` | Pasa sin conflicto whatsapp → nota vacía |

**Comando de validación** (NOTA: `tests/unit/` no existe — ruta corregida):
```bash
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_diagnostic_generator.py -k "whatsapp_conflict_note" -v
```

---

## Post-Ejecución (OBLIGATORIO)

Al finalizar, ejecutar en orden:

1. **`dependencias-fases.md`**: Marcar FASE-A-02b como ✅ Completada
2. **`README.md` del plan**: Marcar fase
3. **`09-documentacion-post-proyecto.md`**:
   - Sección A: N/A (sin módulos nuevos)
   - Sección B: Feature "whatsapp_conflict_business_note" 
   - Sección D: +2 tests
   - Sección E: `v4_diagnostic_generator.py`, `diagnostico_v6_template.md`
4. **Ejecutar tests** y verificar pasan
5. **Ejecutar doctor** para verificar no hay regresiones

---

## Criterios de Completitud (CHECKLIST)

- [ ] `diagnostico_v6_template.md` modificado con `${whatsapp_conflict_business_note}`
- [ ] `_build_whatsapp_conflict_note()` implementado en `v4_diagnostic_generator.py`
- [ ] Nota condicional: solo aparece cuando hay conflicto real
- [ ] Tests nuevos pasan (2/2)
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] `doctor.py --status` sin errores críticos
- [ ] `dependencias-fases.md` actualizado
- [ ] `09-documentacion-post-proyecto.md` actualizado

---

## Restricciones

- NO modificar pain_narratives ni impacto de whatsapp_conflict — eso es FASE-A-02c
- NO agregar costo mensual en la nota — es operativa, no tenemos activo para cuantificar
- La nota debe ser CONDICIONAL: solo mostrar si hay conflicto real
- NO modificar el template de propuesta (solo diagnostico)

---

*Fase: WHATSAPP-CONFLICT-VISIBILITY / FASE-A-02b*  
*Depende de: FASE-A-02a*  
*Creado: 2026-05-24*