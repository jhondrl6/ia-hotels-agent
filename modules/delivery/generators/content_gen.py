"""LLM-based content generator for conversion-focused articles.

This module generates persuasive, bottom-of-funnel content designed to
convert website visitors who are ready to book. Uses the unified LLM
provider (DeepSeek/Anthropic).

Target packages: Pro AEO Plus, Elite, Elite PLUS
"""

from __future__ import annotations

from typing import Any, Dict
from modules.providers.llm_provider import ProviderAdapter


class ContentGenerator:
    """Generates conversion-focused content using LLM."""

    def __init__(self, provider_type: str = "auto"):
        """Initialize with the specified LLM provider.
        
        Args:
            provider_type: "auto", "deepseek", or "anthropic"
        """
        self.llm_provider = ProviderAdapter(provider_type)

    def generate_conversion_article(self, hotel_data: Dict[str, Any]) -> Dict[str, str]:
        """Generates a persuasive article for direct booking conversion.
        
        Args:
            hotel_data: Hotel information including nombre, ubicacion, servicios.
            
        Returns:
            Dict with:
            - "article_md": Full article in Markdown format
            - "title": Article title for metadata
            - "meta_description": SEO meta description
        """
        nombre = hotel_data.get("nombre", "Hotel")
        ubicacion = hotel_data.get("ubicacion", "Colombia")
        servicios = hotel_data.get("servicios", [])
        precio = hotel_data.get("precio_promedio", "consultar")
        
        # Build service list for context
        servicios_str = ", ".join(servicios[:8]) if servicios else "alojamiento cómodo, atención personalizada"
        
        prompt = f"""Actúa como un copywriter experto en turismo boutique y reservas directas.

TAREA: Escribe un artículo persuasivo de 400-500 palabras titulado:
"Por qué reservar directamente en {nombre} es tu mejor decisión"

CONTEXTO DEL HOTEL:
- Nombre: {nombre}
- Ubicación: {ubicacion}
- Servicios destacados: {servicios_str}
- Rango de precio: {precio}

ESTRUCTURA REQUERIDA:
1. **Titular atractivo** (el título ya está definido arriba)
2. **Hook emocional** (2-3 oraciones que conecten con el viajero)
3. **Beneficio 1: Mejor Precio Garantizado** (por qué directo = sin comisiones OTA)
4. **Beneficio 2: Atención Personalizada** (comunicación directa, peticiones especiales)
5. **Beneficio 3: Exclusividades** (upgrades, detalles de bienvenida, flexibilidad)
6. **Prueba Social Implícita** (mencionar que viajeros exigentes prefieren directo)
7. **Call-to-Action claro** (WhatsApp o reservar ahora)

TONO: Cálido, exclusivo, urgente pero no agresivo. Como un concierge de confianza.

FORMATO: Markdown con encabezados ##. NO incluyas el título principal (ya lo agrego yo).

REGLAS:
- NO inventes datos específicos (números de habitaciones, precios exactos)
- SÍ usa el nombre del hotel y ubicación naturalmente
- Máximo 500 palabras
- Incluye al menos 2 emojis estratégicos (🏨, ✨, 📞, etc.)
"""

        try:
            response = self.llm_provider.unified_request(
                prompt,
                max_tokens=1200,
                temperature=0.7
            )
            
            # Build final article with title
            title = f"Por qué reservar directamente en {nombre} es tu mejor decisión"
            meta_description = f"Descubre los beneficios exclusivos de reservar directo en {nombre}, {ubicacion}. Mejor precio, atención personalizada y sorpresas especiales."
            
            article_md = f"# {title}\n\n{response.strip()}"
            
            return {
                "article_md": article_md,
                "title": title,
                "meta_description": meta_description,
            }
            
        except Exception as e:
            # Fallback article (template-based, no LLM)
            return self._generate_fallback_article(hotel_data, str(e))

    def _generate_fallback_article(self, hotel_data: Dict[str, Any], error: str) -> Dict[str, str]:
        """Generates a template-based fallback if LLM fails."""
        nombre = hotel_data.get("nombre", "Hotel")
        ubicacion = hotel_data.get("ubicacion", "Colombia")
        
        title = f"Por qué reservar directamente en {nombre} es tu mejor decisión"
        
        article_md = f"""# {title}

> ⚠️ *Artículo generado con plantilla (LLM no disponible: {error})*

## 🏨 Bienvenido a {nombre}

Ubicado en {ubicacion}, nuestro hotel te ofrece una experiencia única que solo puedes aprovechar al máximo reservando directamente.

## ✨ Beneficios de Reservar Directo

### Mejor Precio Garantizado
Al reservar directamente con nosotros, eliminas las comisiones de intermediarios. Esto significa que podemos ofrecerte el mejor precio disponible, siempre.

### Atención Personalizada
Cuando reservas directo, hablas directamente con nuestro equipo. ¿Tienes una petición especial? ¿Celebras algo importante? Podemos prepararlo todo para ti.

### Sorpresas Exclusivas
Los huéspedes que reservan directo reciben detalles de bienvenida y consideraciones especiales que no están disponibles en otras plataformas.

## 📞 ¿Listo para reservar?

Escríbenos por WhatsApp o llámanos directamente. Nuestro equipo te responderá en minutos y te guiará en todo el proceso.

*{nombre} - Tu hogar lejos de casa en {ubicacion}*
"""
        
        return {
            "article_md": article_md,
            "title": title,
            "meta_description": f"Reserva directo en {nombre}, {ubicacion}. Mejor precio y atención personalizada garantizada.",
        }
