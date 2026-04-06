"""Generador de estrategia de redes sociales para el Acelerador IAO."""

from typing import Any, Dict, List


class SocialStrategyGuideGenerator:
    """Genera estrategia de redes sociales para hotel boutique."""

    def generate(self, hotel_data: Dict[str, Any], audit_result: Any = None) -> str:
        """
        Genera estrategia de redes sociales para hotel boutique.
        
        Args:
            hotel_data: Datos del hotel
            audit_result: Resultado de auditoría (opcional)
        """
        nombre = hotel_data.get("nombre") or hotel_data.get("name", "Hotel")
        url = hotel_data.get("url", "") or ""
        
        # Detectar redes actuales si seo_elements disponible
        redes_actuales = "No detectable"
        redes_list: List[str] = []
        if audit_result and hasattr(audit_result, 'seo_elements') and audit_result.seo_elements:
            if audit_result.seo_elements.social_links_found:
                redes_list = audit_result.seo_elements.social_links_found
                redes_actuales = ", ".join(redes_list)
            else:
                redes_actuales = "No se detectaron enlaces a redes sociales"
        
        sections = [
            f"# Estrategia de Redes Sociales para {nombre}",
            "",
            "## Estado Actual de Presencia Social",
            f"{redes_actuales}",
            "",
            "## ¿Por qué importan las redes sociales para IAO?",
            "",
            "1. **Señales de Confianza**: IA evalúa presencia social como señal de legitimidad",
            '2. **sameAs en Schema.org**: Permite conectar su sitio con redes verificadas',
            "3. **Contenido indexable**: Posts pueden ser citados por LLMs",
            "4. **Señales E-E-A-T**: Demuestra autoridad y trustworthiness",
            "",
            "## Plataformas Prioritarias para Hoteles Boutique",
            "",
            "### 1. Instagram (PRIORIDAD ALTA)",
            "**Por qué**: Visual, orientado a viajes y experiencias",
            "**Frecuencia mínima**: 3-4 posts/semana + stories diarias",
            "**Contenido sugerido**:",
            "- Fotos del hotel (habitaciones, áreas comunes, vistas)",
            "- Detalles de experiencias únicas",
            "- Contenido detrás de escenas",
            "- Stories con respondiendo preguntas",
            "",
            "### 2. Facebook (PRIORIDAD MEDIA-ALTA)",
            "**Por qué**: Audiencia más amplia, especialmente 35+",
            "**Frecuencia mínima**: 2-3 posts/semana",
            "**Contenido sugerido**:",
            "- Ofertas especiales y paquetes",
            "- Eventos y noticias del hotel",
            "- Reseñas y testimonios de huéspedes",
            "- Guías de viaje del destino",
            "",
            "### 3. LinkedIn (PRIORIDAD MEDIA)",
            "**Por qué**: Viajes de negocio, eventos corporativos",
            "**Frecuencia mínima**: 1-2 posts/semana",
            "**Contenido sugerido**:",
            "- Noticias de la industria hotelera",
            "- Articles sobre el destino",
            "- Reconocimientos y certificaciones",
            "- Vacantes y cultura del equipo",
            "",
            "### 4. TikTok (PRIORIDAD BAJA-MEDIA)",
            "**Por qué**: Audiencia joven en crecimiento",
            "**Frecuencia mínima**: 1-2 videos/semana",
            "**Contenido sugerido**:",
            "- Tours rápidos del hotel",
            '- "Day in the life" del equipo',
            "- Momentos destacados del destino",
            "- Trends adaptados al hotel",
            "",
            "## Integración con Schema.org",
            "",
            "Agregue sus redes sociales al Hotel Schema:",
            "",
            "```json",
            "{",
            f'  "@type": "Hotel",',
            f'  "name": "{nombre}",',
            f'  "url": "{url}",',
            '  "sameAs": [',
            '    "https://www.instagram.com/[cuenta]",',
            '    "https://www.facebook.com/[cuenta]",',
            '    "https://www.linkedin.com/company/[cuenta]"',
            "  ]",
            "}",
            "```",
            "",
            "## Checklist de Implementación",
            "",
            "- [ ] Crear cuentas en mínimo 2 plataformas",
            "- [ ] Crear enlace 'Síguenos' visible en web (header o footer)",
            "- [ ] Agregar redes sociales al Schema.org del sitio",
            "- [ ] Crear calendario de contenido mensual",
            "- [ ] Definir horarios óptimos de publicación",
            "- [ ] Configurar links UTM para tracking",
            "",
            "## Métricas Clave",
            "",
            "| Plataforma | Seguidores | Engagement Rate | Respuesta |",
            "|-----------|-----------|-----------------|-----------|",
            "| Instagram | - | >3% | <1 hora |",
            "| Facebook | - | >2% | <2 horas |",
            "| LinkedIn | - | >5% | <24 horas |",
            "",
            "## Vinculación con Web",
            "",
            "Implemente estos enlaces en su sitio:",
            "",
            "```html",
            "<!-- Footer o Header -->",
            '<div class="social-links">',
            '  <a href="https://instagram.com/[cuenta]" target="_blank" rel="noopener">Instagram</a>',
            '  <a href="https://facebook.com/[cuenta]" target="_blank" rel="noopener">Facebook</a>',
            "</div>",
            "```",
        ]
        
        return "\n".join(sections)


__all__ = ["SocialStrategyGuideGenerator"]
