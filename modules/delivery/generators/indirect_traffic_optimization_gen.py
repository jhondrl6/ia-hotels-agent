"""Generador de guia de optimizacion de trafico indirecto para hoteles."""

from typing import Any, Dict


class IndirectTrafficOptimizationGenerator:
    """Genera guia de optimizacion de trafico organico e indirecto."""

    TEMPLATE_PATH = "asset_generation/templates/indirect_traffic_optimization_template.md"

    def generate(self, hotel_data: Dict[str, Any]) -> str:
        """
        Genera guia de optimizacion de trafico indirecto.

        Args:
            hotel_data: Datos del hotel para personalizar la guia.
        """
        nombre = hotel_data.get("nombre") or hotel_data.get("name", "tu hotel")

        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        template_path = os.path.join(base_dir, self.TEMPLATE_PATH)

        if os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = self._generate_fallback()

        # Personalizacion con nombre del hotel
        content = content.replace("tu hotel", nombre)

        return content

    def _generate_fallback(self) -> str:
        """Contenido fallback si el template no existe."""
        return """# Guia de Optimizacion de Trafico Indirecto

## Diagnostico
Tu sitio muestra trafico organico por debajo del esperado. Esta perdida de visibilidad
significa reservas potenciales que van a la competencia.

## Estrategia 1: SEO Local
1. Reclama y verifica tu Google Business Profile
2. Completa TODA la info: fotos, horarios, servicios
3. Usa palabras clave locales en la descripcion
4. Sube al menos 10 fotos de alta calidad
5. Responde a TODAS las reviews

## Estrategia 2: Contenido que Atrae
- Crear blog con guias de destino
- Responder preguntas reales de viajeros
- optimizar cada pagina para voz (AEO)
- FAQ page con SpeakableSpecification

## Estrategia 3: Directorios y OTAs
- TripAdvisor, Booking.com, Google Hotels, Expedia
- Ofrecer valor agregado en el sitio directo

## Estrategia 4: Link Building
- Prensa local, partnerships, guias turisticas

## Estrategia 5: Redes Sociales
- Instagram (maxima prioridad), Facebook, TikTok

## Metricas (con GA4)
1. Sesiones organicas mensuales
2. Tasa de conversion organica
3. Paginas por sesion
4. Fuente de trafico

---
*Documento generado por sistema de diagnostico comercial IAH-CLI*
"""

__all__ = ["IndirectTrafficOptimizationGenerator"]
