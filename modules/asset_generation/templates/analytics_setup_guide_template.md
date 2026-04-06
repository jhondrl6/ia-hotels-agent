# Guia de Configuracion de Google Analytics 4

## Resumen
Esta guia te acompaña paso a paso para configurar Google Analytics 4 (GA4) en tu sitio web hotelero. GA4 es la plataforma de analitica de Google que permite medir el trafico, las conversiones y el comportamiento de los usuarios en tu sitio.

## Por que es importante para tu hotel

Sin GA4 configurado no puedes:
- Saber cuantos visitantes llegan a tu sitio web
- Medir cuantas personas hacen clic en tu boton de reservas
- Identificar desde que canales llega tu trafico (organico, directo, redes sociales)
- Evaluar el retorno de inversion de tus campanas de marketing
- Tomar decisiones basadas en datos reales

## Paso 1: Crear una cuenta de Google Analytics

1. Visita https://analytics.google.com/
2. Haz clic en **Comenzar a medir**
3. Inicia sesion con tu cuenta de Google (preferiblemente la asociada a tu empresa)
4. Acepta los terminos del servicio y la politica de datos

## Paso 2: Crear una propiedad para tu hotel

1. En el asistente de configuracion, selecciona **Crear propiedad**
2. Ingresa el nombre de tu hotel como nombre de la propiedad
3. Selecciona tu zona horaria y moneda (COP para Colombia)
4. Selecciona la categoria **Viajes y turismo > Alojamiento**
5. Indica el tamano de tu empresa
6. Selecciona los objetivos que mejor apliquen:
   - Generar leads (solicitudes de reserva)
   - Aumentar las ventas online (reservas directas)
   - Obtener informacion sobre los usuarios

## Paso 3: Instalar el codigo de seguimiento en tu sitio

### Opcion A: Si tu sitio usa WordPress

1. Instala el plugin **Site Kit by Google** (gratuito)
2. Conecta tu cuenta de Google
3. Site Kit automaticamente instalara el tag de GA4
4. Verifica en **Admin > Etiquetas de datos** que el tag este activo

### Opcion B: Si tu sitio es personalizado

1. Ve a **Admin > Flujo de datos > Web** en GA4
2. Copia el **ID de Medicion** (formato: G-XXXXXXXXXX)
3. Pega el snippet de javascript antes del cierre de </head> en todas las paginas
4. O usa **Google Tag Manager** para una gestion mas limpia

## Paso 4: Configurar eventos de conversion

Para un hotel, los eventos mas importantes son:

1. **Clic en boton de reservar**
   - Evento recomendado: select_date o begin_checkout
   - Se activa cuando el usuario hace clic en "Reservar Ahora"

2. **Visualizacion de paginas de habitacion**
   - Evento recomendado: view_item
   - Permite saber que habitaciones generan mas interes

3. **Envio de formulario de contacto**
   - Evento recomendado: generate_lead o contact
   - Registra las consultas recibidas via formulario

4. **Clic en enlace de WhatsApp**
   - Evento recomendado: contact (con parametro method=whatsapp)
   - Muchas reservas hoteleras se cierran por WhatsApp

5. **Clic en numero de telefono**
   - Evento recomendado: contact (con parametro method=phone)

Para configurar estos eventos:
- Ve a **Admin > Eventos** en GA4
- Haz clic en **Crear evento**
- O usa **Data Layer** con Google Tag Manager para mayor precision

## Paso 5: Configurar Enhanced Ecommerce (Recomendado)

Si tu hotel tiene motor de reservas propio, habilita **Medicion mejorada de comercio electronico**:

1. En GA4, ve a **Admin > Flujo de datos > Web**
2. Activa la **Medicion mejorada**
3. Asegurate de que tu motor de reservas envie los eventos:
   - view_item (ver habitacion)
   - begin_checkout (iniciar reserva)
   - purchase (completar reserva con revenue)

Esto te permite medir el **revenue generado directamente por tu sitio web**.

## Paso 6: Verificar que todo funciona

1. Instala la extension de Chrome **Google Tag Assistant**
2. Visita tu sitio web
3. Verifica que el tag de GA4 se dispare correctamente
4. En GA4, ve a **Informes en tiempo real** y confirma que tu visita aparece
5. Espera 24-48 horas para tener los primeros datos recopilados

## Paso 7: Conectar con Google Ads y Search Console

Para maximizar el valor de GA4:

1. **Google Search Console**: Vinculalo en **Admin > Vinculaciones de productos**
   - Te permite ver las busquedas organicas que llevan trafico a tu sitio
   - Identifica oportunidades de SEO

2. **Google Ads**: Vinculalo en la misma seccion
   - Te permite medir las conversiones de tus campanas pagadas
   - Optimizar el ROI de tu inversion publicitaria

## Recursos utiles

- Documentacion oficial de GA4: https://support.google.com/analytics/
- GA4 para hoteles (guia de Google): https://www.thinkwithgoogle.com/
- Google Tag Manager: https://tagmanager.google.com/
- Site Kit by Google (WordPress): https://wordpress.org/plugins/google-site-kit/

---
*Documento generado por sistema de diagnostico comercial IAH-CLI*
*Para soporte en la implementacion, contactar al equipo tecnico*
