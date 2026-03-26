# Prompt: FASE-H-01 - Diagnóstico Causa Raíz WhatsApp

## Proyecto: iah-cli | hotelvisperas.com
## Fecha: 2026-03-26

---

## Contexto

El flujo V4COMPLETE para Hotel Vísperas presenta 2 desconexiones críticas:

1. **WhatsApp Button**: Se detecta conflicto de números (web vs GBP), pero el asset `whatsapp_button` NO se genera.
2. **Optimization Guide**: Se prometió en la propuesta comercial, pero falló en validación de contenido.

**Experiencia previa (FASE-G 2026-03-25)**:
- Se aplicó fix en `main.py:1705` para propagar `ConfidenceLevel.CONFLICT`
- Se aplicó fix en `conditional_generator.py` para eliminar placeholders
- Los fixes parecían funcionar (coherence 0.82, status READY_FOR_PUBLICATION)

**Problema actual**: Los mismos problemas persisten en ejecución 2026-03-26. Esto indica:
- ¿Regresión del código?
- ¿Fix no persistido correctamente?
- ¿Diferente entorno de ejecución?

---

## Tareas de FASE-H-01

### 1. Investigar Cadena de Detección WhatsApp

Buscar y documentar el flujo completo:

```
V4ComprehensiveAuditor
    ↓ ¿Qué confidence devuelve para WhatsApp?
CrossValidator.calculate_whatsapp_confidence()
    ↓ ¿Convierte a CONFLICT cuando hay 2 números diferentes?
PainSolutionMapper.detect_pains()
    ↓ ¿Recibe y procesa CONFLICT?
PainSolutionMapper._detect_whatsapp_issues()
    ↓ ¿Agrega whatsapp_conflict a detected_pains?
PainSolutionMapper.generate_asset_plan()
    ↓ ¿Incluye whatsapp_button?
V4AssetOrchestrator.generate_assets()
    ↓ ¿Genera el asset?
```

### 2. Comandos de Verificación

Ejecutar los siguientes grep para localizar código relevante:

```bash
# Buscar cómo el auditor detecta WhatsApp
grep -n "confidence.*whatsapp" modules/auditors/v4_comprehensive_auditor.py

# Buscar calculate_whatsapp_confidence
grep -n "calculate_whatsapp_confidence" modules/data_validation/cross_validator.py -A 20

# Buscar cómo pain_mapper procesa whatsapp_conflict
grep -n "whatsapp_conflict" modules/commercial_documents/pain_solution_mapper.py -B 2 -A 5

# Buscar si hay CONFLICT handling
grep -n "CONFLICT" modules/data_validation/cross_validator.py
grep -n "CONFLICT" modules/commercial_documents/pain_solution_mapper.py
```

### 3. Verificar Imports y Enums

Verificar que `ConfidenceLevel.CONFLICT` existe y se importa correctamente:

```python
# En modules/data_validation/cross_validator.py
from enums.validation_enums import ConfidenceLevel  # ¿Existe?

# Verificar valores
# HIGH, MEDIUM, LOW, ESTIMATED, CONFLICT
```

### 4. Documentar Causa Raíz

Crear documento `CAUSA_RAIZ_WHATSAPP.md` con:
- Punto exacto donde se corta la cadena
- Código actual vs código esperado
- Comando para verificar el bug

---

## Post-Ejecución

Después de completar FASE-H-01:

1. **Marcar checklist**: Editar `06-checklist-GAPS-V4COMPLETE.md`:
   - [x] FASE-H-01 completada
   - Causa raíz documentada

2. **Actualizar estado**: En el checklist, mover FASE-H-02 a "en progreso"

3. **Documentación incremental**: Agregar a `09-documentacion-post-proyecto.md`:
   - Sección: FASE-H-01
   - Causa raíz identificada
   - siguiente paso

---

## Criterios de Completitud

- [ ] Flujo completo de WhatsApp documentado
- [ ] Causa raíz identificada con ubicación exacta (archivo:línea)
- [ ] Comando de verificación proporcionado
- [ ] Documento `CAUSA_RAIZ_WHATSAPP.md` creado en `.opencode/plans/`
- [ ] Checklist actualizado

---

## Notas

- Esta es una fase de DIAGNÓSTICO. NO modificar código.
- Si se encuentra que el fix de FASE-G ya está aplicado pero no funciona,
  investigar por qué no surte efecto (orden de ejecución, lógica condicional, etc.)

---

*Prompt creado: 2026-03-26*
*Proyecto: iah-cli | hotelvisperas.com*
