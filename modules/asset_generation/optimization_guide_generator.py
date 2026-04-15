"""Optimization Guide Generator - R4 Architecture.

Generates optimization_guide using the R4 (Real Research, Rich Results) methodology
with full hotel_data propagation from the audit pipeline.

Usage:
    from modules.asset_generation.optimization_guide_generator import OptimizationGuideGenerator
    
    generator = OptimizationGuideGenerator()
    content = generator.generate(hotel_data, metadata_data)
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class OptimizationGuideGenerator:
    """Generates SEO optimization guide with full hotel_data enrichment."""

    def generate(
        self,
        hotel_data: Dict[str, Any],
        metadata_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate optimization guide markdown with enriched hotel_data.

        Args:
            hotel_data: Dictionary with hotel information (name, city, url, etc.)
            metadata_data: Optional metadata analysis data for SEO-specific recommendations

        Returns:
            Optimization guide markdown string
        """
        # Extract hotel info with fallbacks
        hotel_name = hotel_data.get("name") or hotel_data.get("nombre") or "Hotel"
        website = hotel_data.get("url") or hotel_data.get("website") or ""
        city = hotel_data.get("city") or hotel_data.get("ubicacion") or ""
        
        # Default values for metadata analysis
        has_default_title = False
        has_default_description = False
        title_tag = None
        meta_description = None
        title_length = 0
        description_length = 0
        missing_h1 = True
        h1_count = 0
        schema_types: List[str] = []
        
        # Override with actual metadata if available
        if metadata_data and isinstance(metadata_data, dict):
            has_default_title = metadata_data.get("has_default_title", False)
            has_default_description = metadata_data.get("has_default_description", False)
            title_tag = metadata_data.get("title_tag")
            meta_description = metadata_data.get("meta_description")
            title_length = metadata_data.get("title_length", 0)
            description_length = metadata_data.get("description_length", 0)
            missing_h1 = metadata_data.get("missing_h1", True)
            h1_count = metadata_data.get("h1_count", 0)
            schema_types = metadata_data.get("schema_types", [])

        # Status indicators - unified logic considering both default CMS and optimal length
        title_length_status = "⚠️ Longitud no óptima" if title_length < 30 or title_length > 60 else "✅ Longitud correcta"
        description_length_status = "⚠️ Longitud no óptima" if description_length < 120 or description_length > 160 else "✅ Longitud correcta"
        # General status considers BOTH: default CMS flag AND length optimization
        title_needs_attention = has_default_title or (title_length < 30 or title_length > 60)
        description_needs_attention = has_default_description or (description_length < 120 or description_length > 160)
        title_status = "⚠️ Necesita atención" if title_needs_attention else "✅ Correcto"
        description_status = "⚠️ Necesita atención" if description_needs_attention else "✅ Correcto"
        
        # Schema recommendations
        schema_recommendations = ""
        if "Hotel" not in schema_types:
            schema_recommendations += "- Implementar schema Hotel\n"
        if "BreadcrumbList" not in schema_types:
            schema_recommendations += "- Implementar schema BreadcrumbList\n"
        if "FAQPage" not in schema_types:
            schema_recommendations += "- Considerar schema FAQPage si hay sección de preguntas frecuentes\n"
        if not schema_recommendations:
            schema_recommendations = "- Schema markup ya implementado correctamente"

        # Build complete guide
        md = f"""# Guía de Optimización SEO para {hotel_name}

**Fecha de generación:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Hotel:** {hotel_name}
**Ubicación:** {city if city else "Colombia"}
**Website:** {website if website else "Por configurar"}

---

## 1. Revisión de Metadatos

### Title Tag (Título de Página)

| Aspecto | Estado |
|---------|--------|
| Valor actual | {title_tag if title_tag else "⚠️ Sin title tag configurado"} |
| Longitud | {title_length} caracteres {title_length_status} |
| Estado general | {title_status} |

**Recomendaciones:**
"""

        if has_default_title:
            md += """- ❌ El title tag parece ser genérico (default del CMS)
- ✅ Crear un title único que incluya: nombre del hotel + diferenciador + ubicación
- 📝 Referencia: "Hotel [Nombre] - Mejor Tarifa Garantizada | [Ciudad]"
- 📝 Longitud recomendada: 50-60 caracteres

"""
        else:
            md += """- ✅ Title tag personalizado detectado
- 📝 Verificar que incluya palabras clave relevantes

"""

        md += f"""### Meta Description (Descripción Meta)

| Aspecto | Estado |
|---------|--------|
| Valor actual | {(meta_description[:80] + "...") if meta_description else "⚠️ Sin meta description"} |
| Longitud | {description_length} caracteres {description_length_status} |
| Estado general | {description_status} |

**Recomendaciones:**
"""

        if has_default_description:
            md += """- ❌ La descripción parece ser genérica (default del CMS)
- ✅ Crear una descripción única de 150-160 caracteres
- 📝 Incluir: propuesta de valor + amenities principales + llamada a la acción
- 📝 Referencia: "Hotel [Nombre] en [Ciudad]. WiFi gratis, piscina, desayuno incluido. Reserva directa con la mejor tarifa."

"""
        else:
            md += """- ✅ Descripción personalizada detectada
- 📝 Verificar que incluya palabras clave y llamada a la acción

"""

        md += f"""---

## 2. Checklist de Implementación

### Metadatos (Prioridad Alta)

- [ ] Crear title tag único: "{hotel_name} - [Diferenciador] | {city}"
- [ ] Crear meta description de 150-160 caracteres
- [ ] Verificar que title y description sean diferentes

### Estructura de Contenido

- [ ] Implementar un solo H1 por página
- [ ] Usar encabezados H2-H6 en orden jerárquico
- [ ] Incluir palabras clave locales en contenido

### Schema Markup

{schema_recommendations}

### Velocidad y Performance

- [ ] Optimizar imágenes (WebP, <200KB)
- [ ] Habilitar compression gzip
- [ ] Implementar lazy loading para imágenes below the fold
- [ ] Verificar Core Web Vitals en PageSpeed Insights

### SEO Local

- [ ] Verificar que el nombre del hotel sea consistente en todo la web
- [ ] Incluir NAP (Nombre, Dirección, Teléfono) en pie de página
- [ ] Crear página de contacto con mapa de Google Maps embebido
- [ ] Añadir schema LocalBusiness además de Hotel

---

## 3. Estrategia de Contenido

### Blog Recomendado (4 artículos/mes)

1. **Guía de destino**: "Qué hacer en {city} en 3 días"
2. **Lista práctica**: "10 restaurantes cerca de nuestro hotel"
3. **Contenido estacional**: "Mejor época para visitar {city}"
4. **Experiencia única**: "Rutas secretas cerca del hotel"

### Optimización para Voz (AEO)

- Usar preguntas como títulos: "¿Cuál es el mejor hotel en {city}?"
- Respuestas directas de 40-60 palabras debajo del título
- FAQ page con preguntas frecuentes reales
- Markup SpeakableSpecification para Alexa/Google Assistant

---

## 4. KPI's a Monitorear

| Métrica | Meta | Herramienta |
|---------|------|------------|
| Posición promedio | Top 10 | Google Search Console |
| CTR | >3% | Google Search Console |
| Core Web Vitals | Verde | PageSpeed Insights |
| Reseñas GBP | ≥4.5⭐ | Google Business Profile |
| Tráfico orgánico | +20% mensual | Google Analytics 4 |

---

## 5. Recursos y Referencias

- [Google Search Console](https://search.google.com/search-console)
- [PageSpeed Insights](https://pagespeed.web.dev/)
- [Schema.org/Hotel](https://schema.org/Hotel)
- [Schema.org/LocalBusiness](https://schema.org/LocalBusiness)

---

*Guía generada automáticamente por IA Hoteles Agent - Pipeline R4*
*Para implementación técnica, contactar al equipo especializado*
"""

        return md


def get_optimization_guide_generator() -> OptimizationGuideGenerator:
    """Factory function to get OptimizationGuideGenerator instance."""
    return OptimizationGuideGenerator()
