# FASE-E: Validación E2E — Test Completo con Hotelvisperas

**ID**: FASE-E  
**Objetivo**: Validar que todos los componentes AEO funcionan end-to-end  
**Dependencias**: FASE-D completada  
**Duración estimada**: 1-2 horas  
**Skill**: `dogfood` + `systematic-debugging`

---

## Contexto

### Qué se implementó en FASE-D

- KPI Framework en data_models/aeo_kpis.py
- Mock clients para Profound/Semrush
- Dashboard template aeo_metrics_report.md

### Validación E2E

Esta fase verifica que todo el pipeline AEO funciona correctamente con el caso real hotelvisperas.

---

## Tareas

### Tarea E.1: Generar Delivery Completo con AEO

**Objetivo**: Generar el delivery package completo para hotelvisperas con todos los nuevos assets.

**Comando**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python main.py --hotel hotelvisperas --output output/v4_complete_hotelvisperas_aoe
```

**Assets esperados**:
- `01_DIAGNOSTICO_Y_OPORTUNIDAD.md` (con Schema Infrastructure, no AEO)
- `02_PROPUESTA_COMERCIAL.md`
- `hotelvisperas/`
  - `hotel_schema/` (con speakable)
  - `faq_page/` (con FAQ conversacional)
  - `llms_txt/` (mejorado)
  - `voice_assistant_guide/` (nuevo - FASE-C)
  - `aeo_metrics/` (nuevo - FASE-D)

**Criterios de aceptación**:
- [ ] Delivery genera sin errores
- [ ] Todos los assets AEO presentes
- [ ] Documentos con naming correcto

### Tarea E.2: Verificar Speakable en Schema

**Objetivo**: Confirmar que el schema generado tiene SpeakableSpecification.

**Verificación**:
```bash
cat output/v4_complete_hotelvisperas_aoe/hotelvisperas/hotel_schema/*.json | grep -i speakable
```

**Criterios de aceptación**:
- [ ] `speakable` property presente
- [ ] CSS selector apunta a contenido válido

### Tarea E.3: Verificar FAQ Conversacional

**Objetivo**: Confirmar que el FAQ tiene respuestas de 40-60 palabras.

**Verificación**:
- Abrir FAQ y contar palabras de respuestas

**Criterios de aceptación**:
- [ ] Cada respuesta entre 40-60 palabras
- [ ] Tono conversacional

### Tarea E.4: Verificar Voice Assistant Guide

**Objetivo**: Confirmar que los 3 blueprints/checklists están en el delivery.

**Verificación**:
```bash
ls output/v4_complete_hotelvisperas_aoe/hotelvisperas/voice_assistant_guide/
```

**Criterios de aceptación**:
- [ ] `google_assistant_checklist.md` existe
- [ ] `apple_business_connect_guide.md` existe
- [ ] `alexa_skill_blueprint.md` existe

### Tarea E.5: Coherence Score Validation

**Objetivo**: Verificar que el coherence score del sistema se mantiene alto.

**Comando**:
```bash
cat output/v4_complete_hotelvisperas_aoe/v4_audit/coherence_validation.json
```

**Criterios de aceptación**:
- [ ] Coherence score >= 0.80
- [ ] is_coherent = true
- [ ] No nuevos errores

### Tarea E.6: Run Full Regression Suite

**Objetivo**: Confirmar que ningún cambio rompió funcionalidad existente.

**Comando**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python -m pytest tests/ -v --tb=short
```

**Criterios de aceptación**:
- [ ] 28/28 regression tests pasan
- [ ] + nuevos tests de FASE-A a FASE-D pasan

---

## Tests Obligatorios

| Test | Criterio de Éxito |
|------|-------------------|
| Full regression suite | 28+ tests pasan |
| E2E delivery generation | Sin errores |
| Speakable verification | Presente en schema |
| FAQ length check | 40-60 palabras |
| Voice guide files | 3 archivos existen |
| Coherence validation | Score >= 0.80 |

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar FASE-E como ✅ Completada
2. **`09-documentacion-post-proyecto.md`**: Completar todas las secciones
3. **Actualizar CHANGELOG.md**: Documentar cambios de AEO re-architecture
4. **Actualizar README-FASES-TRACKING.md**: Marcar proyecto como completado
5. **Ejecutar log_phase_completion** para FASE-E

---

## Criterios de Completitud (CHECKLIST)

- [ ] **Delivery genera** sin errores
- [ ] **Speakable** presente en schema
- [ ] **FAQ conversacional** verificado (40-60 palabras)
- [ ] **Voice guide** con 3 archivos
- [ ] **Coherence score** >= 0.80
- [ ] **28+ tests** pasan
- [ ] **Documentación** completamente actualizada
- [ ] **Proyecto marcado** como completado en README-FASES

---

## Restricciones

- NO hacer cambios de código en esta fase (solo validación)
- Si algo falla, documentar y crear issue para siguiente sesión
- Esta fase es puramente validación, no implementación

---

## Prompt de Ejecución

```
Actúa como QA engineer.

OBJETIVO: Validar E2E todos los componentes AEO implementados.

CONTEXTO:
- FASE-A a FASE-D completadas
- Hotelvisperas como caso de prueba
- Coherence gate funcionando

TAREAS:
1. Generar delivery completo con AEO
2. Verificar speakable en schema JSON
3. Verificar FAQ conversacional (40-60 palabras)
4. Verificar voice_assistant_guide con 3 archivos
5. Verificar coherence score >= 0.80
6. Run full regression suite

CRITERIOS:
- Delivery genera sin errores
- Todos los assets AEO presentes y correctos
- 28+ tests pasan
- Coherence >= 0.80
```
