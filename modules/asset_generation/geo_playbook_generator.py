"""Geo Playbook Generator - R4 Architecture.

Generates geo_playbook using the R4 (Real Research, Rich Results) methodology
with full hotel_data propagation from the audit pipeline.

Usage:
    from modules.asset_generation.geo_playbook_generator import GeoPlaybookGenerator
    
    generator = GeoPlaybookGenerator()
    content = generator.generate(hotel_data, gbp_data)
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class GeoPlaybookGenerator:
    """Generates geo_playbook with full hotel_data enrichment."""

    # Platforms for directory catalog
    DIRECTORY_CATALOG: List[Dict[str, str]] = [
        {"platform": "Google Business Profile", "url": "https://www.google.com/business/", "action": "Optimizar ficha, subir 3 posts, actualizar atributos"},
        {"platform": "Google Maps Q&A", "url": "https://maps.google.com", "action": "Publicar FAQs en web /preguntas-frecuentes"},
        {"platform": "Bing Places", "url": "https://www.bingplaces.com", "action": "Clonar información GBP"},
        {"platform": "Tripadvisor", "url": "https://www.tripadvisor.com/Owners", "action": "Actualizar servicios, subir imágenes"},
        {"platform": "Expedia Partner Central", "url": "https://www.expediapartnercentral.com", "action": "Sincronizar tarifas directas"},
        {"platform": "Despegar Hoteliers", "url": "https://www.despegar.com.co/hoteliers", "action": "Alinear CTA y WhatsApp"},
        {"platform": "Hoteles.com", "url": "https://www.hoteles.com/", "action": "Actualizar amenities clave"},
        {"platform": "Booking.com", "url": "https://admin.booking.com", "action": "Reforzar narrativa"},
        {"platform": "Airbnb", "url": "https://www.airbnb.com/host/homes", "action": "Duplicar copy para escapadas"},
        {"platform": "Apple Business Register", "url": "https://register.apple.com/business", "action": "Asegurar consistencia NAP"},
    ]

    def generate(
        self,
        hotel_data: Dict[str, Any],
        gbp_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate geo_playbook markdown with enriched hotel_data.

        Args:
            hotel_data: Dictionary with hotel information (name, city, amenities, etc.)
            gbp_data: Optional Google Business Profile data for geo enrichment

        Returns:
            Geo playbook markdown string
        """
        # Extract hotel info with fallbacks
        nombre = hotel_data.get("name") or hotel_data.get("nombre") or "Hotel"
        ubicacion = hotel_data.get("city") or hotel_data.get("ubicacion") or ""
        if not ubicacion:
            ubicacion = hotel_data.get("address", "") or "Colombia"
        
        amenities = hotel_data.get("amenities") or hotel_data.get("servicios") or []
        if not isinstance(amenities, list):
            amenities = []
        
        website = hotel_data.get("url") or hotel_data.get("website") or ""
        phone = hotel_data.get("telephone") or hotel_data.get("phone") or ""
        
        # Extract GBP data if available
        gbp_rating = None
        gbp_reviews = None
        if gbp_data:
            gbp_rating = getattr(gbp_data, 'rating', None) or gbp_data.get("rating")
            gbp_reviews = getattr(gbp_data, 'reviews', None) or gbp_data.get("reviews")

        # Generate sections
        posts_md = self._render_posts_md(nombre, ubicacion, amenities)
        directories_csv = self._render_directories_csv()
        review_playbook = self._render_review_playbook(nombre, ubicacion, amenities)
        gbp_audit = self._render_gbp_audit_checklist(hotel_data)

        # Build complete playbook
        md = f"""# Geo Playbook: {nombre}

> **Hotel:** {nombre}
> **Ubicación:** {ubicacion}
> **Website:** {website}
> **Teléfono:** {phone}
> **GBP Rating:** {gbp_rating if gbp_rating else "Por calificar"}
> **Reviews GBP:** {gbp_reviews if gbp_reviews else "0"}

---

## 1. Optimización de Google Business Profile (GBP)

### Estado Actual

| Métrica | Valor | Estado |
|---------|-------|--------|
| Rating GBP | {gbp_rating if gbp_rating else "N/A"} | {"✅" if gbp_rating and gbp_rating >= 4.0 else "⚠️"} |
| Reviews | {gbp_reviews if gbp_reviews else "0"} | {"✅" if gbp_reviews and gbp_reviews >= 10 else "⚠️"} |

### Checklist de Acciones GBP

- [ ] Verificar información básica (nombre, dirección, teléfono)
- [ ] Confirmar horarios de atención
- [ ] Agregar 10+ fotos de alta calidad
- [ ] Configurar TODOS los atributos del hotel
- [ ] Activar mensajería
- [ ] Configurar reservas directas
- [ ] Publicar posts semanales (mínimo 4/mes)

---

## 2. Posts Recomendados para GBP

"""

        md += posts_md

        md += f"""

---

## 3. Directorios y OTAs

### Directorio Esencial

| Plataforma | Estado | Acción Prioritaria |
|------------|--------|-------------------|
| Google Business Profile | ⭐ | Optimizar al 100% |
| TripAdvisor | ⭐ | Completar perfil |
| Booking.com | ⭐ | Sincronizar tarifas |
| Expedia | ⭐ | Mantener actualizado |
| Despegar | ⭐ | Alinear CTA |

### CSV de Directorios

```csv
{directories_csv}
```

---

## 4. Plan de Reseñas

"""

        md += review_playbook

        md += f"""

---

## 5. Auditoría de Atributos GBP

"""

        md += gbp_audit

        md += f"""

---

## 6. Información de Contacto Verificada

| Canal | Valor |
|-------|-------|
| **Nombre** | {nombre} |
| **Dirección** | {hotel_data.get("address", "Por configurar")} |
| **Teléfono** | {phone or "Por configurar"} |
| **WhatsApp** | {hotel_data.get("whatsapp", "Por configurar")} |
| **Email** | {hotel_data.get("email", "Por configurar")} |
| **Website** | {website or "Por configurar"} |

---

## 7. Servicios y Amenities

### Amenities Principales

"""
        
        if amenities:
            for amenity in amenities[:15]:
                md += f"- {amenity}\n"
        else:
            md += "- Por documentar amenities del hotel\n"

        md += f"""

---

## 8. Métricas a Monitorear

### Google Business Profile
- Vistas en búsqueda
- Vistas en Maps
- Acciones totales (llamadas, direcciones, website)
- Clics al sitio web
- Rating promedio
- Número de reseñas nuevas/mes

### Tráfico Directo
- Sesiones directas mensuales
- Reservas directas (canal propio)
- Tasa de conversión directa

---

*Geo Playbook generado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*IA Hoteles Agent - Pipeline R4*
"""

        return md

    def _render_posts_md(
        self,
        nombre: str,
        ubicacion: str,
        servicios: List[str]
    ) -> str:
        """Render recommended GBP posts section."""
        amenity_a = servicios[0] if servicios else "experiencia única"
        amenity_b = servicios[1] if len(servicios) > 1 else "atención personalizada"

        posts = [
            {
                "titulo": "Post 1 · Escapada Termal",
                "copy": f"Descubre {nombre} en {ubicacion}. Incluye acceso a {amenity_a} y late checkout. Reserva directo y recibe bebida de bienvenida.",
            },
            {
                "titulo": "Post 2 · Viaja con Mascotas",
                "copy": f"Somos pet friendly: espacios verdes, kit de cortesía y rutas guiadas. Agenda por WhatsApp y asegura tu cupo.",
            },
            {
                "titulo": "Post 3 · Experiencia Gastronómica",
                "copy": f"Chef local con ingredientes del Eje Cafetero. Menú degustación con vista a las montañas. Reserva la mesa al confirmar.",
            },
        ]

        qnas = [
            ("¿Aceptan mascotas en todas las habitaciones?", "Sí, tenemos habitaciones diseñadas para viajes con mascota, con áreas verdes asignadas."),
            ("¿El desayuno está incluido?", "Incluimos desayuno campesino con ingredientes locales servido entre 7 a.m. y 10 a.m."),
            ("¿Cuál es el horario de check-in/check-out?", "Check-in 3 p.m. · Check-out 12 m. Late checkout sujeto a ocupación."),
            ("¿Tienen termales o spa cercano?", "Estamos a 15 minutos de Termales Santa Rosa; coordinamos transporte y reservas."),
            ("¿Cuentan con parqueadero?", "Sí, parqueadero privado cubierto sin costo."),
        ]

        md = "### Posts Recomendados\n\n"
        for post in posts:
            md += f"- **{post['titulo']}**: {post['copy']}\n"

        md += "\n### Preguntas y Respuestas Semilla\n\n"
        for question, answer in qnas:
            md += f"- **{question}** → {answer}\n"

        md += "\n### Checklist GBP (Semana 1)\n\n"
        md += "- [ ] Subir 3 posts con CTA directos\n"
        md += "- [ ] Publicar FAQs en web /preguntas-frecuentes (Q&A deshabilitado para hoteles)\n"
        md += "- [ ] Cargar 15 fotos verticales actualizadas\n"
        md += "- [ ] Activar mensajes y respuesta automática en GBP\n"

        return md

    def _render_directories_csv(self) -> str:
        """Render directories CSV."""
        lines = ["platform,url,action,status"]
        for entry in self.DIRECTORY_CATALOG:
            # Escape quotes if needed
            action = entry["action"].replace('"', '""')
            lines.append(f'{entry["platform"]},{entry["url"]},"{action}",pending')
        return "\n".join(lines)

    def _render_review_playbook(
        self,
        nombre: str,
        ubicacion: str,
        servicios: List[str]
    ) -> str:
        """Render review management playbook."""
        destacado = servicios[0] if servicios else "tu experiencia favorita"
        
        lines = [
            f"### Objetivo",
            f"Conseguir 20 reseñas verificadas en 30 días con puntaje ≥4.6.",
            "",
            f"### Pasos Operativos",
            f"1. Recolectar WhatsApp de cada huésped al check-in",
            f"2. Enviar mensaje automatizado 2 horas después del checkout con enlace directo a reseña",
            f"3. Responder cada reseña en menos de 24 horas",
            f"4. Publicar resumen semanal de reseñas positivas en redes/GBP",
            "",
            f"### Script Sugerido",
            f"- Hola {{nombre}}, gracias por elegirnos para tu estancia en {ubicacion}. ¿Podrías contarnos tu experiencia? Tu reseña nos ayuda a seguir siendo la mejor opción.",
            f"- Fue un gusto recibirte. Si disfrutaste del {destacado}, cuéntalo aquí: {{link reseña}}",
            "",
            f"### Métricas a Monitorear",
            f"- % huéspedes que reciben el link",
            f"- Reseñas nuevas por semana",
            f"- Puntaje promedio GBP",
        ]

        return "\n".join(lines)

    def _render_gbp_audit_checklist(self, hotel_data: Dict[str, Any]) -> str:
        """Render GBP attributes audit checklist."""
        servicios = hotel_data.get("amenities") or hotel_data.get("servicios", [])
        if not isinstance(servicios, list):
            servicios = []

        # Critical attributes for hotels
        critical_attributes = [
            ("Wi-Fi gratuito", "wifi" in str(servicios).lower()),
            ("Piscina", "piscina" in str(servicios).lower() or "pool" in str(servicios).lower()),
            ("Parking privado", "parking" in str(servicios).lower() or "parqueadero" in str(servicios).lower()),
            ("Spa / Zona húmeda", "spa" in str(servicios).lower() or "termal" in str(servicios).lower()),
            ("Gimnasio", "gym" in str(servicios).lower() or "gimnasio" in str(servicios).lower()),
            ("Restaurante on-site", "restaurante" in str(servicios).lower()),
            ("Pet-friendly", "mascota" in str(servicios).lower() or "pet" in str(servicios).lower()),
            ("Accesibilidad", "accesib" in str(servicios).lower()),
            ("Desayuno incluido", "desayuno" in str(servicios).lower()),
        ]

        lines = [
            "| Atributo | Detectado | Verificar en GBP |",
            "| :--- | :---: | :---: |",
        ]

        for attr_name, detected in critical_attributes:
            status = "✅" if detected else "⚠️"
            check = "[ ]"
            lines.append(f"| {attr_name} | {status} | {check} |")

        lines.extend([
            "",
            "### Acciones Prioritarias",
            "",
            "1. **Revisar Panel GBP** → Detalles del Hotel → Marcar TODOS los atributos aplicables",
            "2. **Sincronizar con web**: Cada atributo debe tener página/sección correspondiente",
            "3. **Auditoría mensual**: Los atributos desactualizados generan respuestas incorrectas de IA",
            "",
            "> **Nota**: Los atributos del perfil alimentan directamente las respuestas de IA en Google Maps.",
        ])

        return "\n".join(lines)


def get_geo_playbook_generator() -> GeoPlaybookGenerator:
    """Factory function to get GeoPlaybookGenerator instance."""
    return GeoPlaybookGenerator()
