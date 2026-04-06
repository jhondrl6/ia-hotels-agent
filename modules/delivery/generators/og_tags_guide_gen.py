"""Generador de guía Open Graph Tags para el Acelerador IAO."""

from typing import Any, Dict


class OGTagsGuideGenerator:
    """Genera guía de implementación de Open Graph tags."""

    def generate(self, hotel_data: Dict[str, Any], audit_result: Any = None) -> str:
        """
        Genera guía de implementación de Open Graph tags.
        
        Args:
            hotel_data: Datos del hotel
            audit_result: Resultado de auditoría (opcional)
        """
        nombre = hotel_data.get("nombre") or hotel_data.get("name", "Hotel")
        url = hotel_data.get("url", "") or ""
        ubicacion = hotel_data.get("ubicacion") or hotel_data.get("city", "[Ciudad]")
        
        # Verificar OG tags actuales si audit_result disponible
        og_status = "No detectable (requiere implementación)"
        if audit_result and hasattr(audit_result, 'seo_elements') and audit_result.seo_elements:
            og_status = "✅ Detectados" if audit_result.seo_elements.open_graph else "❌ No detectados"
        
        sections = [
            f"# Guía de Open Graph Tags - {nombre}",
            "",
            "## ¿Qué son Open Graph Tags?",
            "",
            "Son meta tags que controlan cómo se muestra su sitio cuando se comparte en redes sociales.",
            "",
            "## Estado Actual",
            f"{og_status}",
            "",
            "## Impacto por Red Social",
            "",
            "| Red Social | Sin OG | Con OG |",
            "|-----------|--------|--------|",
            "| Facebook | Imagen aleatoria | Imagen seleccionada por usted |",
            "| LinkedIn | Sin preview rica | Con imagen, título, descripción |",
            "| WhatsApp | Solo URL | Con imagen y título |",
            "| Twitter | Sin imagen | Con tarjeta rica |",
            "",
            "## Implementación",
            "",
            "Agregue en el <head> de su sitio:",
            "",
            "```html",
            "<!-- Open Graph / Facebook -->",
            '<meta property="og:type" content="website" />',
            f'<meta property="og:url" content="{url}" />',
            f'<meta property="og:title" content="{nombre} - Hotel Boutique en {ubicacion}" />',
            '<meta property="og:description" content="[Descripción de 155-200 caracteres]" />',
            '<meta property="og:image" content="[URL de imagen 1200x630px]" />',
            "",
            "<!-- Twitter -->",
            '<meta name="twitter:card" content="summary_large_image" />',
            f'<meta name="twitter:title" content="{nombre}" />',
            '<meta name="twitter:description" content="[Descripción]" />',
            '<meta name="twitter:image" content="[URL de imagen]" />',
            "```",
            "",
            "## Imagen Recomendada",
            "- Dimensiones: 1200x630px (Facebook/LinkedIn)",
            "- Formato: JPG o PNG",
            "- Tamaño máximo: 5MB",
            "- Contenido: Foto atractiva del hotel con buena iluminación",
            "",
            "## Verificación",
            "",
            "1. Facebook Sharing Debugger: https://developers.facebook.com/tools/debug/",
            "2. LinkedIn Post Inspector: https://www.linkedin.com/post-inspector/",
            "3. Twitter Card Validator: https://cards-dev.twitter.com/validator",
        ]
        
        return "\n".join(sections)


__all__ = ["OGTagsGuideGenerator"]
