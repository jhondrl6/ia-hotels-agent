"""Deploy instructions generator (no-LLM).

Generates CMS-specific installation guides and delegation email templates.
Supports: WordPress, Wix, Squarespace, and generic fallback.

Client-facing instructions are Spanish. Code stays conservative and portable.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class DeployInstructionsGenerator:
    """Generates CMS-specific installation guides and delegation emails."""

    def generate(self, hotel_data: Dict[str, Any], assets_generated: List[str]) -> Dict[str, str]:
        """
        Generate deployment instructions based on detected CMS.
        
        Args:
            hotel_data: Hotel data including cms_detected field
            assets_generated: List of asset filenames that were generated
            
        Returns:
            Dict with 'cms_guide', 'delegation_email', 'cms_type'
        """
        hotel_name = str(hotel_data.get("nombre") or "Hotel").strip() or "Hotel"
        cms_info = hotel_data.get("cms_detected", {})
        cms_type = cms_info.get("cms", "unknown") if isinstance(cms_info, dict) else "unknown"
        
        # Generate CMS-specific guide
        if cms_type == "wordpress":
            cms_guide = self._generate_wordpress_guide(hotel_name, assets_generated)
        elif cms_type == "wix":
            cms_guide = self._generate_wix_guide(hotel_name, assets_generated)
        elif cms_type == "squarespace":
            cms_guide = self._generate_squarespace_guide(hotel_name, assets_generated)
        else:
            cms_guide = self._generate_generic_guide(hotel_name, assets_generated)
        
        # Generate delegation email
        delegation_email = self._generate_delegation_email(hotel_name, cms_type, assets_generated)
        
        return {
            "cms_guide": cms_guide,
            "delegation_email": delegation_email,
            "cms_type": cms_type,
        }

    def _generate_wordpress_guide(self, hotel_name: str, assets: List[str]) -> str:
        return f"""# Guía de Instalación para WordPress
## {hotel_name}

Esta guía te explica cómo instalar los archivos de tu kit en WordPress **sin tocar código**.

---

## Método Recomendado: Plugin WPCode (Gratuito)

### Paso 1: Instalar el Plugin
1. En tu panel de WordPress, ve a **Plugins → Añadir nuevo**
2. Busca "**WPCode**" (el que dice "Insert Headers and Footers")
3. Clic en **Instalar** y luego **Activar**

### Paso 2: Agregar el Código
1. Ve a **Code Snippets → Header & Footer**
2. En la sección **Footer**, pega el contenido de cada archivo HTML:
   - `boton_whatsapp.html`
   - `barra_reserva_movil.html` (si aplica)
3. Clic en **Save Changes**

### Paso 3: Verificar
1. Abre tu sitio en modo incógnito
2. Deberías ver el botón de WhatsApp (verde, abajo a la derecha)
3. En móvil, deberías ver la barra de reservas

---

## ⚠️ ¿Algo salió mal?
Si no ves los botones o tu sitio se ve raro:
1. Vuelve a **Code Snippets → Header & Footer**
2. Borra el código que pegaste
3. Clic en **Save Changes**
4. Tu sitio volverá a la normalidad instantáneamente

---

## Archivos a Instalar
{self._format_assets_list(assets)}

---

## ¿Necesitas ayuda?
Reenvía el archivo `email_para_webmaster.txt` a quien te maneja la web.
"""

    def _generate_wix_guide(self, hotel_name: str, assets: List[str]) -> str:
        return f"""# Guía de Instalación para Wix
## {hotel_name}

Esta guía te explica cómo instalar los archivos de tu kit en Wix.

---

## Requisitos
- Plan Wix Premium (Combo o superior) para código personalizado

---

## Pasos de Instalación

### Paso 1: Acceder a Código Personalizado
1. En el Editor de Wix, clic en **Configuración del sitio** (⚙️)
2. Ve a **Avanzado → Código personalizado**

### Paso 2: Agregar el Código
1. Clic en **+ Agregar código personalizado**
2. Nombre: "Botón WhatsApp IAH"
3. Pega el contenido de `boton_whatsapp.html`
4. Ubicación: **Body - End**
5. Páginas: **Todas las páginas**
6. Clic en **Aplicar**

### Paso 3: Repetir para Barra de Reservas
Si tienes `barra_reserva_movil.html`, repite el proceso.

### Paso 4: Publicar
1. Clic en **Publicar** para que los cambios sean visibles

---

## ⚠️ ¿Algo salió mal?
1. Ve a **Código personalizado**
2. Elimina el snippet que agregaste
3. Publica nuevamente

---

## Archivos a Instalar
{self._format_assets_list(assets)}

---

## ¿Necesitas ayuda?
Reenvía el archivo `email_para_webmaster.txt` a quien te maneja la web.
"""

    def _generate_squarespace_guide(self, hotel_name: str, assets: List[str]) -> str:
        return f"""# Guía de Instalación para Squarespace
## {hotel_name}

Esta guía te explica cómo instalar los archivos de tu kit en Squarespace.

---

## Requisitos
- Plan Business o superior (para inyección de código)

---

## Pasos de Instalación

### Paso 1: Acceder a Inyección de Código
1. En tu panel, ve a **Configuración → Avanzado → Inyección de código**

### Paso 2: Agregar el Código
1. En la sección **Footer**, pega el contenido de:
   - `boton_whatsapp.html`
   - `barra_reserva_movil.html` (si aplica)
2. Clic en **Guardar**

### Paso 3: Verificar
1. Abre tu sitio en modo incógnito
2. Verifica que los elementos aparezcan correctamente

---

## ⚠️ ¿Algo salió mal?
1. Ve a **Inyección de código**
2. Borra el código que pegaste
3. Guarda los cambios

---

## Archivos a Instalar
{self._format_assets_list(assets)}
"""

    def _generate_generic_guide(self, hotel_name: str, assets: List[str]) -> str:
        return f"""# Guía de Instalación General
## {hotel_name}

No detectamos un CMS específico en tu sitio. Aquí te damos instrucciones generales.

---

## Instrucciones para tu Webmaster

Los archivos HTML de este kit deben insertarse **justo antes de la etiqueta `</body>`** en todas las páginas de tu sitio.

### Archivos a Instalar
{self._format_assets_list(assets)}

### Ubicación del Código
```html
<!-- Tu contenido de página -->

<!-- INICIO: Kit IAH -->
<!-- Pegar aquí el contenido de boton_whatsapp.html -->
<!-- Pegar aquí el contenido de barra_reserva_movil.html -->
<!-- FIN: Kit IAH -->

</body>
</html>
```

---

## Siguiente Paso
Reenvía el archivo `email_para_webmaster.txt` a tu proveedor web con los archivos adjuntos.
"""

    def _generate_delegation_email(self, hotel_name: str, cms_type: str, assets: List[str]) -> str:
        cms_label = {
            "wordpress": "WordPress",
            "wix": "Wix",
            "squarespace": "Squarespace",
            "shopify": "Shopify",
            "webflow": "Webflow",
        }.get(cms_type, "nuestro sitio web")
        
        assets_list = "\n".join(f"   - {asset}" for asset in assets if asset.endswith('.html') or asset.endswith('.json'))
        
        return f"""Asunto: Solicitud de instalación de mejoras web - {hotel_name}

Hola,

Contraté una auditoría de marketing digital y necesito implementar algunas mejoras en {cms_label}.

Por favor instala los siguientes archivos en el footer de nuestro sitio (antes del </body>):

{assets_list}

Te adjunto los archivos y una guía de instalación específica para {cms_label}.

**Puntos importantes:**
1. El código es seguro y no modifica la estructura del sitio
2. Solo agrega botones flotantes para WhatsApp y reservas
3. Si algo sale mal, solo hay que borrar el código agregado

Por favor confírmame cuando esté listo para poder verificarlo.

Gracias,
{hotel_name}

---
Archivos adjuntos:
- boton_whatsapp.html
- barra_reserva_movil.html (si aplica)
- guia_instalacion_{cms_type}.md
"""

    def _format_assets_list(self, assets: List[str]) -> str:
        relevant = [a for a in assets if a.endswith(('.html', '.json'))]
        if not relevant:
            return "- (Ver carpeta de archivos adjuntos)"
        return "\n".join(f"- `{asset}`" for asset in relevant)
