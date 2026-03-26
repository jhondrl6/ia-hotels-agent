# Google Assistant Integration Checklist

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
  - Si existe: "Reclamar este negocio"
  - Si no existe: "Agregar tu negocio"

- [ ] **1.2** Verificación de ubicación con PIN postal
  - Esperar carta de Google (5-14 días hábiles)
  - Ingresar PIN en Google Business Profile
  - Confirmación de propiedad postal

- [ ] **1.3** Completar información básica del establecimiento
  - Nombre oficial del hotel (exactamente como aparece en señalización)
  - Categoría principal: "Hotel Boutique" (o la más específica disponible)
  - Categorías adicionales: "Hotel", "Alojamiento", "Guesthouse"
  - Horario de atención: 24 horas para recepción
  - Descripción del negocio: 750 caracteres máximo
  - Atributos de hotel: Wi-Fi, Aire acondicionado, Acceso para sillas de ruedas, Estacionamiento, Piscina, etc.

- [ ] **1.4** Agregar fotos de alta resolución
  - Mínimo 10 fotos profesionales
  - Fotos requeridas:
    - Fachada exterior (con buena iluminación)
    - Recepción/Lobby
    - Habitación estándar (cama, baño)
    - Baño de habitación
    - Área común (restaurante, sala, jardín)
    - Foto del equipo/ubicación exterior
  - Especificaciones: Mínimo 720px, formato JPG o PNG
  - Consejo: Agregar fotos regularmente para mantener perfil activo

### Fase 2: Configuración de Reservas con Google

- [ ] **2.1** Verificar compatibilidad con "Reserve with Google"
  - Documentación: https://developers.google.com/business-profile/how-reservations-work
  - Requiere: Sistema de reservas que soporte integrations API
  - Alternativa: Redirigir a página de reservas del hotel

- [ ] **2.2** Configurar vínculo de reserva
  - En Google Business Profile > "Reservas"
  - Seleccionar: "Agregar vínculo de reserva de terceros"
  - Opciones compatibles:
    - cloudbeds
    - Little Hotelier
    - Siteminder
    - Booking.com (si aplica)
    - Reservas directas via WhatsApp

- [ ] **2.3** Configurar atributos de reserva
  - Número de habitaciones disponibles
  - Tipos de habitación y precios
  - Políticas de cancelación
  - Hora de check-in/check-out

### Fase 3: Optimización para Búsqueda por Voz

- [ ] **3.1** Asegurar NAP Consistency (Nombre, Dirección, Teléfono)
  - Verificar que NAP sea idéntico en:
    - Google Business Profile
    - Sitio web
    - Directorios locales (TripAdvisor, Booking, Airbnb)
    - Redes sociales
  - Herramienta de verificación: https:// Whitespark.ca/local-ranking-tools/

- [ ] **3.2** Agregar preguntas frecuentes (FAQ)
  - En Google Business Profile > "Preguntas y respuestas"
  - Agregar mínimo 5 preguntas frecuentes:
    - "¿A qué hora es el check-in?"
    - "¿El desayuno está incluido?"
    - "¿Cuál es la política de cancelación?"
    - "¿El hotel tiene Wi-Fi?"
    - "¿Hay estacionamiento?"
  - Usar lenguaje conversacional para coincide con búsquedas por voz

- [ ] **3.3** Habilitar mensajes
  - Google Business Profile > "Mensajes"
  - Configurar respuesta automática para consultas fuera de horario
  - Tiempo de respuesta objetivo: < 1 hora

- [ ] **3.4** Configurar attributes de experiencia
  - Accesibilidad: Rampas, habitaciones accesibles, baño adaptado
  - Servicios: Wi-Fi gratis, Piscina, Spa, Gym, Restaurante
  - Higiene: Protocolos de limpieza mejorados (post-COVID)
  - Sustentabilidad: Certificaciones ambientales

### Fase 4:Monitoreo y Optimización

- [ ] **4.1** Configurar Google Business Profile Manager
  - URL: https://business.google.com
  - Agregar usuarios adicionales con permisos apropiados
  - Habilitar notificaciones por email

- [ ] **4.2** Revisar insights regularmente
  - Búsquedas que llevan al perfil
  - Acciones de los clientes (llamadas, direcciones, reservas)
  - Comparación con competidores cercanos

- [ ] **4.3** Responder reseñas
  - Responder a TODAS las reseñas (positivas y negativas)
  - Tiempo de respuesta: < 24 horas
  - Usar tono amigable y profesional

- [ ] **4.4** Publicar actualizaciones
  - Ofertas especiales
  - Eventos en el hotel
  - Nuevos servicios
  - Fotos de temporada

---

## Verificación Final

Después de completar el checklist:

- [ ] Buscar el hotel por voz en Google Assistant: "Ok Google, reserva hotel en [ciudad]"
- [ ] Verificar que el perfil aparece en Google Maps
- [ ] Confirmar que "Reserve with Google" funciona correctamente
- [ ] Probar desde dispositivo móvil para simular experiencia real

---

## Recursos Oficiales

- Google Business Profile Help: https://support.google.com/business/
- Reserve with Google: https://developers.google.com/business-profile/how-reservations-work
- Best Practices for Hotels: https://www.google.com/business/business-resources/
- Google Search Central (SEO): https://developers.google.com/search

---

## Notas Importantes

1. **D-U-N-S Number**: Google puede requerir D-U-N-S de Dun & Bradstreet para verificación de negocio. Obtener en: https://www.dnb.com/duns-number/get-a-duns-number.html

2. **Verificación puede tomar tiempo**: hasta 30 días para hotels pequeños

3. **Google puede requerir re-verificación**: Si cambias dirección o información crítica

4. **Voice Search**: Google prioriza resultados con Schema.org markup. Asegurar que el sitio tenga JSON-LD para Hotel, FAQ, y Review

---

*Documento generado para iah-cli - Hotel Voice Assistant Integration Package*
*Última actualización: 2026-03-25*
