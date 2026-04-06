# FASE-B: AEO Voice-Ready Module — Generador de FAQ Conversacional

**ID**: FASE-B  
**Objetivo**: Implementar assets de AEO real según KB (SpeakableSpecification, FAQ conversacional TTS-ready)  
**Dependencias**: FASE-A completada  
**Duración estimada**: 3-4 horas  
**Skill**: `iah-cli-phased-execution` + `code-review`

---

## Contexto

### Qué se implementó en FASE-A

- "AEO (Schema)" renombrado a "Schema Infrastructure"
- Dual counting eliminado: Schema y FAQ ahora solo en IAO
- Métrica placeholder "Voice Readiness (AEO)" con score 0/100

### Qué falta (KB AEO_agent_ready.md)

| Componente AEO Real | Estado Actual | Requerido |
|---------------------|---------------|-----------|
| SpeakableSpecification en schema | ❌ No existe | ✅ Agregar al schema generator |
| FAQ conversacional (40-60 palabras, TTS) | ❌ Solo schema FAQ técnico | ✅ Generador nuevo |
| Voice keywords para Eje Cafetero | ❌ No existe | ✅ Incluir en guía |
| llms.txt existente | ⚠️ Básico | ✅ Mejorar con contenido conversacional |

---

## Tareas

### Tarea B.1: Agregar SpeakableSpecification al Schema Generator

**Objetivo**: El schema Hotel generado debe incluir la propiedad `speakable` según Schema.org.

**Referencia KB**: Sección [SCHEMA] líneas 108-111 de `AEO_agent_ready.md`

```json
"speakable": {
  "@type": "SpeakableSpecification",
  "cssSelector": ["[SELECTOR_CSS_DESCRIPCION]", "[SELECTOR_CSS_SERVICIOS]"]
}
```

**Archivos afectados**:
- `modules/asset_generation/` (schema generator existente)
- `output/v4_complete/hotelvisperas/hotel_schema/` (output)

**Criterios de aceptación**:
- [ ] Schema JSON-LD generado incluye propiedad `speakable`
- [ ] El CSS selector apunta a secciones de descripción y servicios
- [ ] Tests verifican la presencia de `speakable` en output

### Tarea B.2: Crear Generador FAQ Conversacional (TTS-Ready)

**Objetivo**: Generar FAQ optimizado para ser leído en voz alta por asistentes de voz.

**Referencia KB**: 
- Sección [CONTENIDO] líneas 193-197: "Duración: 20-30 segundos por sección (~2-3 oraciones)"
- Sección [COMPARATIVA] AEO: "40-60 palabras" por respuesta

**Especificaciones**:
- Cada respuesta FAQ: 40-60 palabras (óptimo para TTS)
- Tono: Natural, conversacional
- Estructura: Pregunta directa → Respuesta concisa
- Incluye: cssSelector para speakable

**Archivos afectados**:
- `modules/delivery/generators/faq_gen.py` (modificar)
- `modules/asset_generation/conditional_generator.py` (nuevo asset type)

**Criterios de aceptación**:
- [ ] Generator produce FAQ en formato Markdown + JSON-LD
- [ ] Cada Q&A tiene entre 40-60 palabras
- [ ] Incluye cssSelector para speakable
- [ ] Test verifica longitud de respuestas

### Tarea B.3: Voice Keywords para Eje Cafetero

**Objetivo**: Incluir en la guía de optimización keywords de voz específicas para la región.

**Referencia KB**: Sección [COLOMBIA] líneas 265-283

**Keywords de voz a incluir**:
- "hoteles boutique cerca del Valle del Cocora"
- "hotel con spa en Santa Rosa de Cabal"
- "lugar donde tomar café de origen en Pereira"
- "hoteles termales en el Eje Cafetero"

**Archivos afectados**:
- `modules/delivery/generators/content_gen.py` o nuevo generador

**Criterios de aceptación**:
- [ ] Guía incluye sección de "Voice Search Keywords"
- [ ] Keywords en español para consultas de voz
- [ ] Keywords específicas del Eje Cafetero

### Tarea B.4: Mejorar llms.txt para Contexto de Voz

**Objetivo**: El archivo llms.txt debe incluir información que asista a voice assistants.

**Referencia KB**: Sección [LLMS_TXT] líneas 234-259

**Mejoras**:
- Descripción USP en UNA oración (para respuesta rápida de asistente)
- Políticas en formato legible por voz
- Contexto geográfico explícito

**Criterios de aceptación**:
- [ ] llms.txt tiene sección de contexto geográfico
- [ ] Políticas son concisas y voice-friendly
- [ ] Test verifica presencia de elementos voice-friendly

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_speakable_schema` | `tests/` | Schema incluye speakable |
| `test_faq_conversational_length` | `tests/` | Cada FAQ 40-60 palabras |
| `test_voice_keywords` | `tests/` | Keywords Eje Cafetero presentes |
| Regression suite | `tests/` | 28/28 + nuevos tests pasan |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python -m pytest tests/ -v --tb=short
```

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar FASE-B como ✅ Completada
2. **`09-documentacion-post-proyecto.md`**: Sección A (módulos nuevos), Sección D
3. **Generar assets de prueba** con hotelvisperas

---

## Criterios de Completitud (CHECKLIST)

- [ ] **SpeakableSpecification** presente en schema generado
- [ ] **FAQ conversacional** con respuestas de 40-60 palabras
- [ ] **Voice keywords** específicas para Eje Cafetero incluidas
- [ ] **llms.txt mejorado** con contexto de voz
- [ ] **Tests nuevos pasan**: speakable, FAQ length, voice keywords
- [ ] **Regression**: 28+ tests pasan
- [ ] **Documentación actualizada**

---

## Restricciones

- No modificar el audit_report.json schema
- Mantener backwards compatibility con conditional_generator.py
- El FAQ conversacional es adicional al FAQ schema existente (no lo reemplaza)
- Voice keywords son informativas, no afectan scoring

---

## Prompt de Ejecución

```
Actúa como developer de módulos AEO.

OBJETIVO: Implementar componentes de AEO real (voice search optimization) según KB.

CONTEXTO:
- FASE-A completada: AEO renombrado a Schema Infrastructure, dual counting eliminado
- KB: AEO_agent_ready.md con especificaciones técnicas
- Base: conditional_generator.py, faq_gen.py, schema generators

TAREAS:
1. Agregar SpeakableSpecification al schema generator (JSON-LD speakable property)
2. Crear FAQ conversacional (40-60 palabras por respuesta, TTS-ready)
3. Agregar voice keywords sección para Eje Cafetero
4. Mejorar llms.txt con contexto geográfico voice-friendly

CRITERIOS:
- Schema incluye "speakable": SpeakableSpecification
- FAQ respuestas entre 40-60 palabras
- Voice keywords específicas para región
- Todos los tests pasan

VALIDACIONES:
- python -m pytest tests/ -v
- Generar assets para hotelvisperas
- Verificar speakable en schema JSON
```
