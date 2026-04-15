"""Generadores para integración con plataformas de voz (Alexa, Siri, Google Assistant)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


class VoiceGuideGenerator:
    """Genera guías de integración para plataformas de voz.
    
    Produce un directorio voice_assistant_guide/ con:
    - google_assistant_checklist.md
    - apple_business_connect_guide.md
    - alexa_skill_blueprint.md
    
    Estos documentos son generados por iah-cli basándose en templates
    personalizadas para hotels boutique en el Eje Cafetero de Colombia.
    """

    def generate(self, hotel_data: Dict[str, Any]) -> Dict[str, str]:
        """Genera las 3 guías de integración de voz.
        
        Args:
            hotel_data: Datos del hotel (nombre, ubicación, etc.)
            
        Returns:
            Dict con los contenidos de cada guía
        """
        nombre = hotel_data.get("nombre") or hotel_data.get("name", "Hotel")
        ubicacion = hotel_data.get("ubicacion") or hotel_data.get("city", "Colombia")

        google_guide = self._render_google_assistant_checklist(nombre, ubicacion)
        apple_guide = self._render_apple_business_connect_guide(nombre, ubicacion)
        alexa_guide = self._render_alexa_skill_blueprint(nombre, ubicacion)

        return {
            "google_assistant_checklist": google_guide,
            "apple_business_connect_guide": apple_guide,
            "alexa_skill_blueprint": alexa_guide,
        }

    def _render_google_assistant_checklist(self, nombre: str, ubicacion: str) -> str:
        """Renderiza el checklist de Google Assistant."""
        return f"""# Google Assistant Integration Checklist

**Platform**: Google Assistant + Google Business Profile  
**Purpose**: Step-by-step checklist for hotels to enable voice search and reservations via Google  
**Target**: Hotel boutique en Colombia (Eje Cafetero)  

---

## Prerrequisitos

- Cuenta Google con acceso a Google Business Profile (GBP)
- Sitio web del hotel con HTTPS activo
- Información de contacto verificada (teléfono, email)

---

## Checklist de Implementación

### Fase 1: Configuración de Google Business Profile

- [ ] **1.1** Crear o reclamar Google Business Profile
  - URL: https://business.google.com/create
  - Buscar el hotel por nombre y dirección

- [ ] **1.2** Verificación de ubicación con PIN postal
  - Esperar carta de Google (5-14 días hábiles)
  - Ingresar PIN en Google Business Profile

- [ ] **1.3** Completar información básica del establecimiento
  - Categoría principal: "Hotel Boutique"
  - Horario de atención: 24 horas para recepción

- [ ] **1.4** Agregar fotos de alta resolución
  - Mínimo 10 fotos profesionales
  - Fachada, recepción, habitación, baño, áreas comunes

### Fase 2: Configuración de Reservas con Google

- [ ] **2.1** Verificar compatibilidad con "Reserve with Google"
- [ ] **2.2** Configurar vínculo de reserva (WhatsApp directo recomendado)

### Fase 3: Optimización para Búsqueda por Voz

- [ ] **3.1** Asegurar NAP Consistency en directorios
- [ ] **3.2** Agregar preguntas frecuentes (FAQ) en GBP
- [ ] **3.3** Habilitar mensajes con respuesta automática
- [ ] **3.4** Configurar atributos de experiencia

---

## Recursos

- Google Business Profile: https://business.google.com
- Reserve with Google: https://developers.google.com/business-profile/how-reservations-work

*Generado para {nombre} - {ubicacion}*
"""

    def _render_apple_business_connect_guide(self, nombre: str, ubicacion: str) -> str:
        """Renderiza la guía de Apple Business Connect."""
        return f"""# Apple Business Connect Setup Guide

**Platform**: Apple Business Connect + Siri  
**Purpose**: Guide for hotels to enable Siri voice actions and appear in Apple Maps  
**Target**: Hotel boutique en Colombia (Eje Cafetero)  

---

## Prerrequisitos

- Apple ID empresarial
- D-U-N-S Number (Data Universal Numbering System)
- Sitio web del hotel

---

## Paso a Paso

### Paso 1: Obtener D-U-N-S Number

1. Solicitar en: https://www.dnb.com/duns-number/get-a-duns-number.html
2. Tiempo: 1-2 días hábiles (online)
3. Costo: Gratuito

### Paso 2: Apple Business Connect

1. Navegar a: https://business.apple.com
2. Buscar el hotel por nombre y dirección
3. Verificar con D-U-N-S Number

### Paso 3: Configurar Showcases

- Logo PNG con fondo transparente (1024x1024px mínimo)
- Header image panorámica (4096x2048px)
- 6-10 fotos de categorías: Habitación, Baño, Lobby, Restaurant, Exterior

### Paso 4: Habilitar Siri Actions

| Acción | Descripción |
|--------|-------------|
| Llamar | Click-to-call desde Siri |
| Cómo llegar | Direcciones en Maps |
| Sitio web | Abrir sitio web |

---

## Recursos

- Apple Business Connect: https://business.apple.com
- D-U-N-S Number: https://www.dnb.com/duns-number.html

*Generado para {nombre} - {ubicacion}*
"""

    def _render_alexa_skill_blueprint(self, nombre: str, ubicacion: str) -> str:
        """Renderiza el blueprint de Alexa Skill."""
        return f"""# Alexa Skill Blueprint para Hoteles

**Platform**: Amazon Alexa Skills Kit (ASK)  
**Purpose**: Blueprint técnico para crear Alexa Skill básica de hotel  
**Target**: Hotel boutique en Colombia (Eje Cafetero)  

---

## Arquitectura

```
Alexa → Skill (Invocation Name) → Lambda → API Bridge → PMS Hotel
```

## Invocation Name

```
{nombre.lower().replace(' ', '')}
```

**Reglas**: 2-3 palabras, sin "skill/app/alexa", pronunciable claramente.

## Intents Mínimos (3)

### DisponibilidadIntent
- "¿Tienen disponible para mañana?"
- "¿Hay habitaciones libres?"

### ServiciosIntent
- "¿Qué servicios ofrecen?"
- "¿El hotel tiene piscina?"

### UbicacionIntent
- "¿Dónde está el hotel?"
- "Dame la dirección"

## Lambda Handler (Python)

```python
class DisponibilidadIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("DisponibilidadIntent")(handler_input)
    
    def handle(self, handler_input):
        speech = "Para mañana tenemos 3 habitaciones disponibles."
        return handler_input.response_builder.speak(speech).response
```

## ASP for Hospitality (In-Room)

> ⚠️ Requiere invitación directa de AWS. Consultar con AWS account manager.

---

## Recursos

- Alexa Skills Kit: https://developer.amazon.com
- ASK CLI: https://developer.amazon.com/docs/smapi/ask-cli-intro.html

*Generado para {nombre} - {ubicacion}*
"""
