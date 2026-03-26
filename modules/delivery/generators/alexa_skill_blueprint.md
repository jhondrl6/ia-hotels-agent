# Alexa Skill Blueprint para Hoteles

**Platform**: Amazon Alexa Skills Kit (ASK)  
**Purpose**: Blueprint técnico para crear Alexa Skill básica de hotel  
**Target**: Hotel boutique en Colombia (Eje Cafetero)

---

## Overview

Este blueprint documenta la arquitectura básica para crear un Alexa Skill que permita a los huéspedes y potenciales clientes interactuar con el hotel mediante voz. El skill actúa como puente entre Alexa y el Property Management System (PMS) del hotel.

---

## Arquitectura del Skill

```
┌─────────────────────────────────────────────────────────────┐
│                    ALEXA VOICE REQUEST                      │
│              "Alexa, pregunta al [Hotel]..."                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   ALEXA SKILL (Cloud)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Invocation   │  │   Intents   │  │  Lambda Function    │  │
│  │   Name      │──│  Handler    │──│  (Node.js/Python)   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   API BRIDGE LAYER                          │
│           (Hotel PMS Integration Layer)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  REST API   │  │   GraphQL   │  │  WhatsApp/Messages  │  │
│  │  (generic) │  │  (generic)  │  │    (fallback)       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 PROPERTY MANAGEMENT SYSTEM                   │
│              (Motor de Reservas del Hotel)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Componentes del Skill

### 1. Invocation Name (Nombre de Invocación)

El nombre que Alexa usa para activar el skill.

#### Ejemplos para Hoteles Boutique

| Invocation Name | Descripción |
|-----------------|-------------|
| `Hotel Visperas` | Nombre directo del hotel |
| `Hotel {ciudad}` | Para cadenas |
| `mi hotel favorito` | Genérico pero memorable |

#### Reglas de Amazon para Invocation Names

- Mínimo 2 palabras, máximo 3 palabras
- No puede incluir "skill", "app", "Alexa"
- No puede ser confundible con built-in skills
- Debe ser pronunciable claramente

#### Invocation Name Recomendado

```
hotel visperas
```

**Nota**: Invocation names en español pueden tener limitaciones. Para hotels en Colombia, considerar nombre en español primero.

---

## Intents (Intenciones)

Los intents definen qué puede hacer el skill.

### Intents Requeridos (Mínimo 3)

#### Intent 1: DisponibilidadIntent

```
{
  "name": "DisponibilidadIntent",
  "slots": [
    {
      "name": "fecha",
      "type": "AMAZON.DATE",
      "prompt": "¿Para qué fecha necesitas la habitación?",
      "samples": [
        "para mañana",
        "para el {fecha}",
        "tengo disponibilidad para {fecha}",
        "está disponible el {fecha}"
      ]
    },
    {
      "name": "noches",
      "type": "AMAZON.NUMBER",
      "prompt": "¿Cuántas noches te vas a quedar?",
      "samples": [
        "{noches} noches",
        "una noche",
        "dos noches"
      ]
    }
  ],
  "samples": [
    "¿Tienen disponible para mañana?",
    "¿Hay habitaciones libres?",
    "Quiero saber si tienen espacio",
    "¿Está disponible el hotel?"
  ]
}
```

#### Intent 2: ServiciosIntent

```
{
  "name": "ServiciosIntent",
  "slots": [],
  "samples": [
    "¿Qué servicios ofrecen?",
    "Qué tiene el hotel",
    "dime los servicios del hotel",
    "amenidades del hotel",
    "que incluye el desayuno"
  ]
}
```

#### Intent 3: UbicacionIntent

```
{
  "name": "UbicacionIntent",
  "slots": [],
  "samples": [
    "¿Dónde está el hotel?",
    "dame la dirección",
    "cómo llego al hotel",
    "ubicación del hotel",
    "dirección"
  ]
}
```

### Intents Adicionales Recomendados

#### Intent 4: ReservasIntent

```
{
  "name": "ReservasIntent",
  "slots": [
    {
      "name": "nombre",
      "type": "AMAZON.US_FIRST_NAME",
      "prompt": "¿A nombre de quién hago la reserva?"
    },
    {
      "name": "telefono",
      "type": "AMAZON.PHONE_NUMBER",
      "prompt": "¿Cuál es tu número de contacto?"
    }
  ],
  "samples": [
    "quiero hacer una reserva",
    "reservar una habitación",
    "hacer una reserva"
  ]
}
```

#### Intent 5: PrecioIntent

```
{
  "name": "PrecioIntent",
  "slots": [
    {
      "name": "tipo_habitacion",
      "type": "LIST_OF_ROOM_TYPES"
    }
  ],
  "samples": [
    "¿Cuánto cuesta una habitación?",
    "precios del hotel",
    "costo por noche",
    "tarifas"
  ]
}
```

#### Intent 6: HelpIntent / CancelIntent / StopIntent

```
{
  "name": "AMAZON.HelpIntent",
  "samples": ["ayuda", "qué puedes hacer", "cómo te uso"]
}

{
  "name": "AMAZON.CancelIntent",
  "samples": ["cancela", "cancelar", "salir"]
}

{
  "name": "AMAZON.StopIntent",
  "samples": ["para", "detente", "apaga"]
}
```

---

## Sample Utterances (Expresiones de Ejemplo)

Alexa necesita muchas ejemplo para entender variaciones.

### DisponibilidadIntent

```
hay disponibilidad para mañana
tienen quartos para pasado mañana
quiero saber si tienen espacio para el quince
están reservados para el veinte
puedo reservar para este fin de semana
disponibilidad para dos noches
hay huecos para navidad
reserva para tres personas
```

### ServiciosIntent

```
qué servicios ofrecen
que tiene el hotel
dime las amenidades
incluyen desayuno
el hotel tiene piscina
tienen wifi gratis
horario del restaurante
servicio de lavandería
actividades que ofrecen
```

### UbicacionIntent

```
dónde está ubicado el hotel
dame la dirección
cómo llego al hotel
está cerca del centro
como llego desde el aeropuerto
puntos de referencia
dirección exacta
```

---

## Lambda Function (Backend)

### Handler Basic (Python)

```python
import logging
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.handler_input import HandlerInput

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# Intent Handlers
# ─────────────────────────────────────────────────────────────

class DisponibilidadIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("DisponibilidadIntent")(handler_input)
    
    def handle(self, handler_input):
        fecha = ask_utils.request_util.get_slot_value(handler_input, "fecha")
        noches = ask_utils.request_util.get_slot_value(handler_input, "noches")
        
        # API Bridge: Consultar PMS
        disponibilidad = consultar_disponibilidad(fecha, noches)
        
        speech = f"Para el {fecha}, tenemos {disponibilidad} habitaciones disponibles por {noches} noches."
        return handler_input.response_builder.speak(speech).response

class ServiciosIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ServiciosIntent")(handler_input)
    
    def handle(self, handler_input):
        speech = ("Ofrecemos Wi-Fi gratuito, desayuno incluido, "
                  "piscina al aire libre, servicio de spa, "
                  "restaurante con cocina local e internacional, "
                  "y habitaciones con aire acondicionado.")
        return handler_input.response_builder.speak(speech).response

class UbicacionIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("UbicacionIntent")(handler_input)
    
    def handle(self, handler_input):
        speech = ("Estamos ubicados en la zona centro de Pereira, "
                  "a 15 minutos del aeropuerto internacional Matecaña. "
                  "La dirección exacta es: Calle 5 número 45-67.")
        return (handler_input.response_builder
                .speak(speech)
                .add_link_account_card()
                .response)

# ─────────────────────────────────────────────────────────────
# API Bridge Functions
# ─────────────────────────────────────────────────────────────

def consultar_disponibilidad(fecha: str, noches: int) -> int:
    """
    Bridge para consultar disponibilidad en PMS del hotel.
    
    Returns:
        Número de habitaciones disponibles
    
    Nota: Esta función requiere integración real con el PMS.
    Para demo/testing, retorna valor simulado.
    """
    # TODO: Implementar llamada real a API del hotel
    # PMS_COMMON_APIS = ["cloudbeds", "littlehotelier", "siteminder"]
    return 3  # Demo: 3 habitaciones disponibles
```

---

## API Bridge Architecture

### Propósito

El API Bridge aísla la lógica del Alexa Skill del sistema interno del hotel. Esto permite cambiar el PMS sin modificar el skill.

### Patrones de Integración

#### Pattern 1: Direct REST API

```
Alexa → Lambda → Hotel REST API → PMS
```

**Pros**: Simple, bajo costo  
**Cons**: Expone credenciales si no hay API gateway

#### Pattern 2: WhatsApp Fallback (Recomendado)

```
Alexa → Lambda → Hotel API → WhatsApp Business API → Cliente
```

**Pros**: Fallback familiar en Colombia  
**Cons**: Latencia mayor, requiere cuenta WhatsApp Business

#### Pattern 3: GraphQL Aggregator

```
Alexa → Lambda → GraphQL Gateway → Multiple Services
```

**Pros**: Flexible, permite agregar servicios  
**Cons**: Más complejo de implementar

### Endpoints Típicos del PMS

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/availability` | GET | Consultar disponibilidad |
| `/reservations` | POST | Crear reserva |
| `/rooms/{id}` | GET | Detalles de habitación |
| `/services` | GET | Lista de servicios |
| `/pricing` | GET | Tarifas actuales |

---

## Amazon ASP for Hospitality (Para Experiencia In-Room)

### ¿Qué es ASP for Hospitality?

Amazon Alexa Smart Properties (ASP) for Hospitality permite que hotels desplieguen Alexa en habitaciones para experiencia personalizada in-room.

### Requisitos

1. **Cuenta AWS Organizations** con ASP habilitado
2. **Invitación de AWS** (no cualquier hotel puede apply)
3. **Dispositivos Alexa** compatibiles (Echo Dot, Echo Show)
4. **Integration con PMS** del hotel

### Características In-Room

- Control por voz de luces, temperatura, cortinas
- Información del hotel por voz
- Pedidos a room service
- Late check-out requests
- Wake-up calls

### Limitaciones

- **No está disponible públicamente**: Requiere invitación de AWS
- **Costo de licenciamiento**: Por dispositivo/mes
- **Proceso de certificación**: AWS revisa cada integración

### Nota Importante

> ⚠️ **ASP for Hospitality requiere invitación directa de Amazon/AWS.**  
> Hotels interesados deben contactar a su AWS account manager o apply via:  
> https://aws.amazon.com/about-aws/smart-property/hospitality/

---

## Deployment Checklist

### Fase 1: Desarrollo Local

- [ ] Configurar ASK CLI
- [ ] Crear skill manifest (skill.json)
- [ ] Definir interaction model (language model)
- [ ] Implementar Lambda handlers
- [ ] Probar con Alexa Simulator (Developer Console)

### Fase 2: Testing

- [ ] Unit tests para Lambda functions
- [ ] Integration tests con API bridge
- [ ] Beta testing con usuarios seleccionados
- [ ] Validar en dispositivos reales

### Fase 3: Certification y Deployment

- [ ] Submit to Amazon for certification
- [ ] Review de políticas de Amazon
- [ ] Aprobación (3-5 días hábiles)
- [ ] Publicación en Alexa Skills Store

---

## Recursos Oficiales

- Amazon Developer Portal: https://developer.amazon.com
- Alexa Skills Kit Documentation: https://developer.amazon.com/docs/ask-overviews/alexa-skills-kit.html
- ASK CLI Reference: https://developer.amazon.com/docs/smapi/ask-cli-intro.html
- Alexa Design Guidelines: https://developer.amazon.com/docs/alexa-design/overview.html
- AWS ASP for Hospitality: https://aws.amazon.com/alexa/smart-properties/hospitality/
- Colombia Alexa Locale: Configure es-CO como locale

---

## Configuración Regional (Colombia)

```json
{
  "languageModel": {
    "language": "es-CO",
    "invocationName": "hotel visperas",
    "intents": [...],
    "types": [...]
  }
}
```

**Nota**: es-CO (Español de Colombia) es el locale recomendado. Amazon soporta es-ES y es-MX más comúnmente; verificar disponibilidad para es-CO.

---

## Notas de Costo

- **Alexa Skills Kit**: Gratuito para developers
- **AWS Lambda**: Tier gratuito (1M requests/mes)
- **ASK Hosting**: Opcional, desde $0.20/millon requests
- **ASP for Hospitality**: Costo por licenciamiento (consultar con AWS)

---

*Documento generado para iah-cli - Hotel Voice Assistant Integration Package*
*Última actualización: 2026-03-25*
