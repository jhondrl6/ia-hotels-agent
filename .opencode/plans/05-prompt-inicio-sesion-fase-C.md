# FASE-C: Integración con Plataformas de Voz — Checklists y Blueprints

**ID**: FASE-C  
**Objetivo**: Documentar e implementar checklists de integración para Alexa, Siri y Google Assistant  
**Dependencias**: FASE-B completada  
**Duración estimada**: 2-3 horas  
**Skill**: `writing-plans` + `code-review`

---

## Contexto

### Qué se implementó en FASE-B

- SpeakableSpecification en schema
- FAQ conversacional (40-60 palabras)
- Voice keywords para Eje Cafetero
- llms.txt mejorado

### Qué sigue (KB AEO_agent_ready.md)

| Plataforma | Requisito | Estado |
|------------|-----------|--------|
| Google Assistant | Reserve with Google API | ⚠️ Requiere API real del hotel |
| Apple Siri | Apple Business Connect setup | ⚠️ Checklist nomás |
| Amazon Alexa | Alexa Skills Kit | ⚠️ Blueprint nomás |
| Amazon Alexa | ASP for Hospitality | ⚠️ Requiere invitación AWS |

---

## Tareas

### Tarea C.1: Google Assistant — Checklist de Integración

**Objetivo**: Crear checklist documento para que un hotel se registre en Google Assistant.

**Referencia KB**: Sección [PLATAFORMAS] > Google Assistant + GBP (líneas 119-129)

**Checklist incluye**:
- [ ] Verificar/crear Google Business Profile completo
- [ ] Agregar atributos de hotel (Wi-Fi, AC, accesibilidad)
- [ ] ConfigurarReserve with Google API (si motor de reservas lo soporta)
- [ ] Verificar NAP consistency
- [ ] Subir fotos de alta resolución (mín. 10)

**Archivo a crear**: `modules/delivery/generators/google_assistant_checklist.md`

**Criterios de aceptación**:
- [ ] Checklist existe y es usable
- [ ] Cada item tiene acción concrete
- [ ] Incluye links a documentación oficial de Google

### Tarea C.2: Apple Business Connect — Blueprint de Setup

**Objetivo**: Crear guía/setup para integrar hotel con Apple Business Connect para Siri.

**Referencia KB**: Sección [PLATAFORMAS] > Apple Siri (líneas 133-143)

**Blueprint incluye**:
- [ ] Verificación de ubicación con D-U-N-S
- [ ] Configuración de vitrinas (Showcases)
- [ ] Siri Actions: "Llamar", "Cómo llegar"
- [ ] Categorización correcta: "Hotel Boutique"
- [ ] Fotos alta resolución

**Archivo a crear**: `modules/delivery/generators/apple_business_connect_guide.md`

**Criterios de aceptación**:
- [ ] Guía existe con pasos específicos
- [ ] Incluye información de privacidad/seguridad
- [ ] Referencia a herramienta de verificación D-U-N-S

### Tarea C.3: Alexa Skills Kit — Blueprint de Skill Hotel

**Objetivo**: Crear blueprint para que un hotel cree Alexa Skill básica.

**Referencia KB**: Sección [PLATAFORMAS] > Amazon Alexa (líneas 148-171)

**Blueprint incluye**:
- [ ] Estructura básica de Alexa Skill (invocation name, intents)
- [ ] Sample utterances para consultas de hotel
- [ ] API Bridge architecture (Alexa → PMS)
- [ ] ASP for Hospitality info (para hotels que quieran experiencia in-room)

**Archivo a crear**: `modules/delivery/generators/alexa_skill_blueprint.md`

**Criterios de aceptación**:
- [ ] Blueprint con invocation name example
- [ ] Mínimo 3 intents: disponibilidad, servicios, ubicación
- [ ] Arquitectura de API bridge documentada
- [ ] Nota sobre ASP for Hospitality (requiere certificación AWS)

### Tarea C.4: Crear asset "voice_assistant_guide" en conditional_generator

**Objetivo**: Integrar los 3 checklists/blueprints como asset delivery.

**Referencia KB**: Arquitectura SaaS (líneas 356-384)

**Assets generados**:
- `voice_assistant_guide/` directory
  - `google_assistant_checklist.md`
  - `apple_business_connect_guide.md`
  - `alexa_skill_blueprint.md`

**Criterios de aceptación**:
- [ ] conditional_generator produce el asset
- [ ] El delivery package incluye la carpeta voice_assistant_guide
- [ ] Test verifica los 3 archivos existen en output

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_voice_guide_assets` | `tests/` | 3 archivos de guía生成 |
| Regression suite | `tests/` | Todos pasan |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python -m pytest tests/ -v --tb=short
```

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar FASE-C como ✅ Completada
2. **Generar delivery de prueba** con hotelvisperas
3. **Verificar** que voice_assistant_guide aparece en el delivery package

---

## Criterios de Completitud (CHECKLIST)

- [ ] **Google Assistant checklist** existe y es actionable
- [ ] **Apple Business Connect guide** incluye D-U-N-S verification
- [ ] **Alexa Skill blueprint** tiene invocation + 3 intents mínimo
- [ ] **Asset integration** en conditional_generator
- [ ] **Tests pasan**
- [ ] **Delivery incluye** voice_assistant_guide/

---

## Restricciones

- NO implementar APIs reales de Google/Apple/Amazon (requieren cuentas externas)
- Los blueprints son documentos informativos, no código funcional
- FASE-C es principalmente documentación/herramientas, no código Python

---

## Prompt de Ejecución

```
Actúa como technical writer y strategist.

OBJETIVO: Crear checklists y blueprints para integración con plataformas de voz.

CONTEXTO:
- FASE-B completada: assets de voz implementados
- KB: AEO_agent_ready.md secciones [PLATAFORMAS]
- Output: 3 documentos informativos + integración como asset

TAREAS:
1. Google Assistant checklist (GBP setup, Reserve with Google)
2. Apple Business Connect guide (D-U-N-S, Showcases, Siri Actions)
3. Alexa Skill blueprint (invocation, intents, API bridge)
4. Integrar como asset en conditional_generator

CRITERIOS:
- 3 documentos con contenido actionable
- Asset voice_assistant_guide generado
- Tests pasan
```
