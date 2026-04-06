"""Generador de guia de configuracion de Google Analytics 4 para hoteles."""

from typing import Any, Dict


class AnalyticsSetupGuideGenerator:
    """Genera guia de implementacion de GA4 para un hotel."""

    TEMPLATE_PATH = "asset_generation/templates/analytics_setup_guide_template.md"

    def generate(self, hotel_data: Dict[str, Any]) -> str:
        """
        Genera guia de configuracion de Google Analytics 4.

        Args:
            hotel_data: Datos del hotel para personalizar la guia.
        """
        nombre = hotel_data.get("nombre") or hotel_data.get("name", "tu hotel")
        url = hotel_data.get("url", "") or "tu sitio web"
        ciudad = hotel_data.get("ciudad") or hotel_data.get("city", "tu destino")

        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        template_path = os.path.join(base_dir, self.TEMPLATE_PATH)

        if os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = self._generate_fallback()

        # Personalizacion minima
        content = content.replace("tu sitio web hotelero", f"{nombre} en {ciudad}")
        content = content.replace("tu sitio", url if url else "tu sitio web")

        return content

    def _generate_fallback(self) -> str:
        """Contenido fallback si el template no existe."""
        return """# Guia de Configuracion de Google Analytics 4

## Paso 1: Crear cuenta
1. Visita https://analytics.google.com/
2. Haz clic en **Comenzar a medir**
3. Inicia sesion con tu cuenta de Google

## Paso 2: Crear propiedad
1. Selecciona **Crear propiedad**
2. Ingresa el nombre de tu hotel
3. Selecciona zona horaria y moneda (COP para Colombia)
4. Categoria: **Viajes y turismo > Alojamiento**

## Paso 3: Instalar codigo de seguimiento
### WordPress
Instala el plugin **Site Kit by Google** y conecta tu cuenta.

### Sitio personalizado
1. Ve a **Admin > Flujo de datos > Web** en GA4
2. Copia el **ID de Medicion** (formato: G-XXXXXXXXXX)
3. Pega el snippet antes del cierre de </head>

## Paso 4: Configurar eventos de conversion
- Clic en boton de reservar (select_date)
- Visualizacion de habitaciones (view_item)
- Envio de formulario de contacto (generate_lead)
- Clic en enlace de WhatsApp (contact)

## Verificacion
1. Instala **Google Tag Assistant** (Chrome)
2. Visita tu sitio web
3. Verifica que el tag se dispare
4. En GA4 > Informes en tiempo real confirma tu visita

---
*Documento generado por sistema de diagnostico comercial IAH-CLI*
"""

__all__ = ["AnalyticsSetupGuideGenerator"]
