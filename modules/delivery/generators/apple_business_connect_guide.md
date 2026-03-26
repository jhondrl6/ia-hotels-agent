# Apple Business Connect Setup Guide

**Platform**: Apple Business Connect + Siri  
**Purpose**: Guide for hotels to enable Siri voice actions and appear in Apple Maps  
**Target**: Hotel boutique en Colombia (Eje Cafetero)

---

## Overview

Apple Business Connect permite a los negocios controlar cómo aparecen en Apple Maps, Siri, y otras apps de Apple. Los hoteles pueden configurar "Showcases" y habilitar acciones de voz como "Llamar al hotel" y "Cómo llegar".

---

## Prerrequisitos

- Apple ID empresarial (o personal con acceso de administrador)
- D-U-N-S Number (Data Universal Numbering System) para verificación
- Sitio web del hotel con información de contacto clara
- Imágenes de alta resolución del establecimiento

---

## D-U-N-S Number (Requisito Obligatorio)

Apple Business Connect requiere verificación de negocio mediante D-U-N-S Number.

### Obtener D-U-N-S Number

1. **Solicitar en línea** (más rápido):
   - URL: https://www.dnb.com/duns-number/get-a-duns-number.html
   - Seleccionar: "Get a D-U-N-S Number for my business"
   - Completar formulario con información del hotel

2. **Tiempo de procesamiento**:
   - Online: 1-2 días hábiles
   - Por teléfono: Mismo día (en inglés)
   - Por correo: 30 días

3. **Costo**: Gratuito para pequeñas empresas

4. **Verificar D-U-N-S existente**:
   - https://www.dnb.com/duns-number/lookup.html
   - Buscar por nombre del hotel y dirección

---

## Paso a Paso: Configuración de Apple Business Connect

### Paso 1: Crear cuenta en Apple Business Connect

1. Navegar a: https://business.apple.com
2. Hacer clic en "Get Started"
3. Iniciar sesión con Apple ID
4. Aceptar Términos y Condiciones

### Paso 2: Agregar y Verificar el Negocio

1. **Buscar el hotel**:
   - Ingresar nombre y dirección exacta
   - Si aparece: seleccionarlo
   - Si no: "Add New Location"

2. **Completar información básica**:
   ```
   - Nombre del negocio: [Nombre oficial del hotel]
   - Categoría: Hotels & Motels (o Hotels)
   - Subcategoría: Boutique Hotel
   - Descripción: [Descripción del hotel en 280 caracteres máximo]
   ```

3. **Verificar con D-U-N-S**:
   - Ingresar D-U-N-S Number
   - Apple verificará con Dun & Bradstreet
   - Proceso: 1-5 días hábiles
   - Si falla: revisar datos del D-U-N-S y reintentar

### Paso 3: Configurar Información de Contacto

- **Teléfono**: Número principal de recepción
- **Email**: Email de contacto del hotel
- **Sitio Web**: URL principal del hotel
- **Horario**:
  - Recepción: 24 horas
  - Servicios adicionales según aplique

### Paso 4: Configurar Showcases (Vitrinas)

Los Showcases son imágenes y información destacada que aparecen cuando alguien busca el negocio en Apple Maps.

#### Imágenes Recomendadas

| Tipo | Cantidad | Especificaciones |
|------|----------|-----------------|
| Logo | 1 | PNG con fondo transparente, 1024x1024px mínimo |
| Header Image | 1 | Foto panorámica del hotel, 4096x2048px |
| Fotos de categoría | 6-10 | Ver below |

#### Categorías de Fotos para Hoteles

- **Habitación**: Foto de habitación estándar con cama
- **Bathroom**: Baño privado
- **Lobby**: Área de recepción
- **Restaurant**: Restaurante o área de desayuno
- **Exterior**: Fachada del hotel
- **Amenities**: Piscina, spa, jardín (si aplica)
- **Guestroom**: Otra habitación para variedad

#### Configurar Showcase

1. En Apple Business Connect, seleccionar el hotel
2. Ir a "Showcase" > "Add Photos"
3. Seleccionar categoría para cada foto
4. Agregar leyenda descriptiva
5. Marcar foto principal

### Paso 5: Habilitar Siri Actions

Apple Business Connect permite que Siri responda preguntas sobre tu negocio.

#### Acciones Disponibles para Hoteles

| Acción | Descripción | Ejemplo de voz |
|--------|-------------|----------------|
| **Llamar** | Click-to-call desde Siri | "Hey Siri, llama al [Hotel]" |
| **Cómo llegar** | Direcciones en Maps | "Hey Siri, cómo llego al [Hotel]" |
| **Sitio web** | Abrir sitio web | "Hey Siri, abre el sitio web del [Hotel]" |

#### Configurar Acciones

1. En Apple Business Connect > "Actions"
2. **Llamar**: Verificar número de teléfono (debe coincidir con verificado)
3. **Cómo llegar**: Confirmar dirección correcta
4. **Sitio web**: URL principal

### Paso 6: Agregar Attributes (Atributos)

Los attributes ayudan a Siri a responder preguntas específicas.

#### Attributes Recomendados para Hoteles

- Wi-Fi: "Free Wi-Fi available"
- Estacionamiento: "Free parking available"
- Accesibilidad: "Wheelchair accessible"
- Habitaciones: Número de habitaciones
- Check-in: Hora de check-in
- Check-out: Hora de check-out

---

## Verificación y Testing

### Probar en Dispositivo iOS/Mac

1. **Probar con Siri**:
   - "Hey Siri, dónde está el [Nombre del Hotel]?"
   - "Hey Siri, llama al [Nombre del Hotel]"
   - "Hey Siri, cómo llego al [Nombre del Hotel]"

2. **Probar en Apple Maps**:
   - Abrir Apple Maps
   - Buscar el hotel por nombre
   - Verificar que la información aparezca correctamente

3. **Probar con Siri Suggestions**:
   - En iPhone: Buscar en Spotlight
   - Verificar que el hotel aparezca en sugerencias

---

## Preguntas Frecuentes

### ¿Cuánto tiempo tarda la verificación?

- D-U-N-S: 1-5 días hábiles
- Apple Business Connect: 1-3 días hábiles adicionales
- Total estimado: 7-14 días

### ¿Qué pasa si no tengo D-U-N-S?

Apple Business Connect lo requiere para verificar la legitimidad del negocio. Sin D-U-N-S no se puede completar el registro.

### ¿Puedo actualizar información después?

Sí. Los cambios en Apple Business Connect se reflejan en Apple Maps y Siri en 24-48 horas.

### ¿Hay costo?

No. Apple Business Connect es gratuito.

---

## Recursos Oficiales

- Apple Business Connect: https://business.apple.com
- D-U-N-S Number: https://www.dnb.com/duns-number.html
- Apple Developer Documentation: https://developer.apple.com/documentation/applebusinessconnect
- Siri and Voice Search Best Practices: https://developer.apple.com/documentation/sirikit

---

## Notas de Privacidad y Seguridad

- Toda información en Apple Business Connect es pública
- No exponer información sensible (datos financieros, personales de empleados)
- Fotos deben tener derechos apropiados
- Cumplir con políticas de Apple para contenido

---

## Integración con Schema.org

Para mejor compatibilidad con Siri y Apple Maps, asegurar que el sitio web tenga:

1. **LocalBusiness Schema** con información de contacto correcta
2. **Hotel Schema** con servicios y amenities
3. **FAQ Schema** con preguntas frecuentes

---

*Documento generado para iah-cli - Hotel Voice Assistant Integration Package*
*Última actualización: 2026-03-25*
