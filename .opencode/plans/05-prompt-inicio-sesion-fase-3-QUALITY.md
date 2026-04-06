# FASE 3: Mejoras de Calidad - Content Validation y Documentación

**ID**: FASE-3-QUALITY-IMPROVEMENTS
**Objetivo**: Mejorar detección de frases genéricas y clarificar semántica de estados
**Dependencias**: FASE 2 completada
**Duración estimada**: 30-45 minutos
**Skill**: systematic-debugging, code-review

---

## Contexto

### Problemas Identificados

**Problema M1: Falsos positivos en detección de frases genéricas**
```
El archivo optimization_guide.md contiene:
  - "No configurado"
  - "verificar"
  - "..." (elipsis)

El validador marcó estos como:
  - placeholder: \.\.\.
  - generic_phrase: 'no configurado'
  - generic_phrase: 'verificar'

PERO estos SON contenido legítimo para una guía de optimización SEO.
Las frases "verificar", "revisar", "no configurado" son instrucciones normales.
```

**Problema M2: Semántica confusa de can_use vs status**
```
metadata.json muestra:
  can_use: false
  status: "generated"
  
El usuario recibe un archivo que "existe" pero "no puede usarse".
No está claro qué acción debe tomar.
```

**Problema M3: autonomous_researcher sin output documentado**
```
El informe menciona que autonomous_researcher se ejecutó:
"Autonomous Researcher: El sistema intentó investigar en fuentes públicas 
(GBP, Booking, TripAdvisor, Instagram) aunque en este caso específico 
los resultados fueron limitados."

Pero no hay evidencia en el output de que este módulo se haya ejecutado.
No hay archivo de resultados ni metadatos de investigación.
```

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE 1: COP COP | 🚧 Pendiente |
| FASE 2: Asset Bugs | 🚧 Pendiente |

### Base Técnica Disponible
- Archivos existentes:
  - `modules/asset_generation/asset_content_validator.py`
  - `modules/asset_generation/asset_metadata.py`
  - `modules/providers/autonomous_researcher.py`
- Tests base: ~1438 (después de FASE 2)
- Módulos: AssetContentValidator, AssetMetadata, AutonomousResearcher

---

## Tareas

### Tarea 1: Calibrar detector de frases genéricas
**Objetivo**: Reducir falsos positivos en optimization_guide

**Problema**: Las frases "verificar", "revisar", "no configurado" NO son placeholders ni frases genéricas inválidas para una guía de optimización. Son contenido legítimo.

**Archivos a modificar**:
- `modules/asset_generation/asset_content_validator.py`

**Lógica a ajustar**:
- Phrases como "verificar", "revisar", "personalizar", "no configurado" son aceptables en contexto de guías/recetas/checklists
- Solo marcar como generic_phrase si aparece en contextos inapropiados (e.g., descripciones de schema, no en listas de action items)

**Criterios de aceptación**:
- [ ] "verificar", "revisar", "personalizar" NO son marcados como generic_phrase
- [ ] "no configurado" es aceptable en secciones de diagnóstico
- [ ] El archivo optimization_guide.md pasa validación después del cambio

### Tarea 2: Clarificar semántica can_use vs status en documentación
**Objetivo**: Documentar claramente qué significa cada estado

**Documentación a crear/actualizar**:
- `docs/GUIA_TECNICA.md` - Sección de estados de assets
- O crear `docs/ASSET_STATUS_MEANING.md`

**Semántica a documentar**:

| Estado | Significado | Acción del usuario |
|--------|--------------|-------------------|
| `can_use: true, status: "generated"` | Listo para implementar | Implementar |
| `can_use: false, status: "generated"` | Existe pero con warnings | Revisar disclaimer, usar con precaución |
| `can_use: false, status: "failed"` | No se generó | Esperar datos, usar fallback |
| `can_use: false, status: "blocked"` | Bloqueado por validación | Corregir fuente de datos |

**Criterios de aceptación**:
- [ ] Documentación existe y es accesible
- [ ] Tabla de estados documentada
- [ ] Diferencia entre WARNING y BLOCK klarificada

### Tarea 3: Documentar output de autonomous_researcher
**Objetivo**: Definir qué output debe generar este módulo o confirmar que es no-op

**Opciones**:
1. El módulo es no-op cuando GBP no tiene datos → documentar como intencional
2. El módulo debería generar evidencia aunque sea mínima → implementar

**Archivos a revisar**:
- `modules/providers/autonomous_researcher.py`

**Criterios de aceptación**:
- [ ] Comportamiento documentado en el módulo o en docs/
- [ ] Si genera output, los metadatos lo referencian
- [ ] Si es no-op, hay comentario/logger indicando "research skipped due to no data"

### Tarea 4: Crear test de calibración del validator
**Objetivo**: Asegurar que los falsos positivos no regresen

**Archivo a crear**:
- `tests/test_generic_phrase_calibration.py`

**Criterios de aceptación**:
- [ ] Test que verifica phrases legítimas no son marcadas como error
- [ ] Test que verifica true positives siguen siendo detectados
- [ ] Test pasa: `pytest tests/test_generic_phrase_calibration.py -v`

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_legitimate_phrases_not_flagged` | `tests/test_generic_phrase_calibration.py` | "verificar", "revisar" no son errores |
| `test_true_positives_still_detected` | `tests/test_generic_phrase_calibration.py` | Placeholders reales sí son detectados |

**Comando de validación**:
```bash
pytest tests/test_generic_phrase_calibration.py -v
python -m pytest tests/ -v --tb=short | grep -i "phrase\|generic"
```

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`**
   - Marcar FASE 3 como ✅ Completada

2. **`08-plan-correccion-v4-issues.md`**
   - Marcar M1, M2, M3 como completadas

3. **`09-documentacion-post-proyecto.md`**
   - Sección B: Actualizar diagramas de flujo si cambió validación
   - Sección D: Actualizar métricas

4. **`evidence/fase-3-quality/`**
   - Crear directorio
   - Guardar evidencia de calibración

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] **Validator calibrado**: optimization_guide pasa validación
- [ ] **Documentación actualizada**: Estados de assets clarificados
- [ ] **autonomous_researcher documentado**: Comportamiento explicados
- [ ] **Test de calibración pasa**: `pytest tests/test_generic_phrase_calibration.py -v`
- [ ] **Post-ejecución completada**: Todos los puntos anteriores

---

## Restricciones

- [ ] NO cambiar la lógica de validation para false negatives (sigue detectando placeholders reales)
- [ ] NO eliminar autonomous_researcher (solo documentar o confirmar que es no-op)
- [ ] La documentación debe ser accesible para usuarios no técnicos

---

## Prompt de Ejecución

```
Actúa como developer con enfoque en quality assurance.

OBJETIVO: 3 mejoras de calidad en el sistema NEVER_BLOCK:

M1: Falsos positivos en validación
- "verificar", "revisar", "no configurado" son marcados como error
- Pero son contenido legítimo para guías de optimización
- Ajustar asset_content_validator.py para reducir falsos positivos

M2: Documentar semántica de estados
- can_use: false vs status: "generated" vs status: "failed"
- Crear documentación clara para usuarios
- Tabla de estados en docs/

M3: autonomous_researcher sin output
- El módulo se ejecutó pero no hay evidencia en output
- Documentar si es no-op intencional o debe generar output

TAREAS:
1. Revisar asset_content_validator.py - ajustar lista de generic_phrases
2. Crear docs/ASSET_STATUS_MEANING.md con tabla de estados
3. Revisar autonomous_researcher.py y documentar comportamiento
4. Crear test de calibración

CRITERIOS:
- optimization_guide pasa validación
- Estados documentados
- autonomous_researcher tiene comportamiento explicito

VALIDACIONES:
- pytest tests/test_generic_phrase_calibration.py -v
- Revisar que optimization_guide real pasa validación
```
