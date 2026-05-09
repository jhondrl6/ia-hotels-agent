"""Generador de guia de optimizacion de trafico indirecto para hoteles.

FIX-6: Lee audit_report.json para generar recomendaciones contextualizadas
basadas en datos reales del hotel (GBP reviews, etc.).
"""

import json
import os
from typing import Any, Dict, Optional


class IndirectTrafficOptimizationGenerator:
    """Genera guia de optimizacion de trafico organico e indirecto."""

    TEMPLATE_PATH = "asset_generation/templates/indirect_traffic_optimization_template.md"

    def generate(self, hotel_data: Dict[str, Any], audit_report_path: Optional[str] = None) -> str:
        """
        Genera guia de optimizacion de trafico indirecto.

        Args:
            hotel_data: Datos del hotel para personalizar la guia.
            audit_report_path: Ruta opcional al audit_report.json para
                               recomendaciones contextualizadas.
        """
        nombre = hotel_data.get("nombre") or hotel_data.get("name", "tu hotel")

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        template_path = os.path.join(base_dir, self.TEMPLATE_PATH)

        if os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = self._generate_fallback()

        # Personalizacion con nombre del hotel
        content = content.replace("tu hotel", nombre)

        # FIX-6: Agregar diagnostico data-driven si hay audit_context
        if audit_report_path:
            audit_context = self._read_audit_context(audit_report_path)
            if audit_context:
                data_section = self._build_data_driven_section(audit_context, nombre)
                content += "\n\n" + data_section

        return content

    def _read_audit_context(self, audit_report_path: str) -> Optional[Dict[str, Any]]:
        """Lee y parsea el audit_report.json.

        Args:
            audit_report_path: Ruta al archivo audit_report.json.

        Returns:
            Dict con datos del audit o None si no se pudo leer.
        """
        if not audit_report_path or not os.path.exists(audit_report_path):
            return None
        try:
            with open(audit_report_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError, IOError):
            return None

    def _build_data_driven_section(self, audit_data: Dict[str, Any], hotel_name: str) -> str:
        """Construye seccion de diagnostico basado en datos reales del audit.

        Args:
            audit_data: Datos del audit_report.json.
            hotel_name: Nombre del hotel.

        Returns:
            Seccion markdown con diagnostico data-driven.
        """
        lines = ["## Diagnostico Data-Driven (basado en audit real)", ""]

        # GBP data
        gbp = audit_data.get("google_business_profile", {})
        if gbp:
            review_count = gbp.get("review_count", 0)
            rating = gbp.get("rating", 0)
            place_found = gbp.get("place_found", False)

            if place_found:
                lines.append(f"- **Google Business Profile**: Verificado ✅")
                lines.append(f"  - Reseñas: {review_count}")
                lines.append(f"  - Rating: {rating}/5")
                if review_count > 1000:
                    lines.append("  - ✅ Perfil GBP ya establecido. Enfocarse en respuesta a reseñas.")
                elif review_count > 100:
                    lines.append("  - 📈 Perfil con tracción. Priorizar responder reseñas y mantener info actualizada.")
                elif review_count > 0:
                    lines.append("  - 🔄 Perfil existe pero necesita promoción. Incentivar reseñas de huéspedes.")
                else:
                    lines.append("  - ⚠️ Sin reseñas. Reclama y optimiza tu perfil GBP.")
                lines.append("")
            else:
                lines.append("- **Google Business Profile**: No encontrado ❌")
                lines.append("  - 🔄 Reclama y verifica tu Google Business Profile.")
                lines.append("  - Completa TODA la info: fotos, horarios, servicios.")
                lines.append("")

        # Schema/SEO data
        schema = audit_data.get("schema", {})
        if schema:
            hotel_schema = schema.get("hotel_schema_detected", False)
            faq_schema = schema.get("faq_schema_detected", False)
            total_schemas = schema.get("total_schemas", 0)
            lines.append(f"- **Datos Estructurados**: {total_schemas} schemas detectados")
            if not hotel_schema:
                lines.append("  - ⚠️ Falta Hotel schema. Fundamental para rich results.")
            if not faq_schema:
                lines.append("  - ⚠️ Falta FAQ schema. Reduce visibilidad en búsqueda por voz.")
            lines.append("")

        # Performance data
        perf = audit_data.get("performance", {})
        if perf:
            mobile = perf.get("mobile_score", 0)
            desktop = perf.get("desktop_score", 0)
            lines.append(f"- **PageSpeed**: Mobile {mobile}/100 | Desktop {desktop}/100")
            if mobile < 50:
                lines.append("  - 🚨 Mobile score crítico. Priorizar optimización de imágenes y lazy loading.")
            elif mobile < 80:
                lines.append("  - ⚠️ Mobile score mejorable. Revisar Core Web Vitals.")
            lines.append("")

        # Resumen de acciones prioritarias
        lines.append("### Acciones Prioritarias")
        lines.append("")
        actions = self._build_prioritized_actions(audit_data)
        for i, action in enumerate(actions, 1):
            lines.append(f"{i}. {action}")
        lines.append("")

        return "\n".join(lines)

    def _build_prioritized_actions(self, audit_data: Dict[str, Any]) -> list:
        """Construye lista de acciones priorizadas basadas en datos del audit."""
        actions = []

        gbp = audit_data.get("google_business_profile", {})
        schema = audit_data.get("schema", {})
        perf = audit_data.get("performance", {})

        # GBP actions
        if not gbp.get("place_found", False):
            actions.append("🔴 [Crítico] Reclama y verifica tu Google Business Profile")
        elif gbp.get("review_count", 0) < 10:
            actions.append("🟡 [Alta] Incentiva a huéspedes a dejar reseñas en GBP")

        # Schema actions
        if not schema.get("hotel_schema_detected", False):
            actions.append("🔴 [Crítico] Implementa Hotel schema para rich results en Google")
        if not schema.get("faq_schema_detected", False):
            actions.append("🟡 [Media] Agrega FAQ schema para búsqueda por voz")

        # Performance actions
        mobile = perf.get("mobile_score", 100)
        if mobile < 50:
            actions.append("🔴 [Crítico] Optimiza rendimiento mobile (PageSpeed < 50)")
        elif mobile < 80:
            actions.append("🟡 [Media] Mejora Core Web Vitals en mobile")

        if not actions:
            actions.append("✅ Sin acciones críticas detectadas. Mantén monitoreo trimestral.")

        return actions

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
