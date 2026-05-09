"""Monthly Report Generator - R4 Architecture.

Generates monthly report using the R4 (Real Research, Rich Results) methodology
with full hotel_data propagation from the audit pipeline.

Usage:
    from modules.asset_generation.monthly_report_generator import MonthlyReportGenerator

    generator = MonthlyReportGenerator()
    content = generator.generate(hotel_data, period="Enero 2026")
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional


class MonthlyReportGenerator:
    """Generates monthly KPI tracking report for hotels with full hotel_data enrichment."""

    def generate(
        self,
        hotel_data: Dict[str, Any],
        period: Optional[str] = None,
        asset_report_path: Optional[str] = None,
    ) -> str:
        """Generate monthly report markdown with enriched hotel_data.

        Args:
            hotel_data: Dictionary with hotel information (name, city, website, etc.)
            period: Report period string (e.g., "Enero 2026"). Defaults to current month.
            asset_report_path: Optional path to asset_generation_report.json.
                             Defaults to output_dir/asset_generation_report.json.

        Returns:
            Markdown string with monthly report template.
        """
        # Extract hotel info with fallbacks
        hotel_name = hotel_data.get("name") or hotel_data.get("nombre", "Hotel")
        city = hotel_data.get("city") or hotel_data.get("ubicacion", "")
        website = hotel_data.get("website") or hotel_data.get("url", "")
        phone = hotel_data.get("telephone") or hotel_data.get("phone", "")
        email = hotel_data.get("email", "")
        address = hotel_data.get("address", "")

        # GBP real data
        total_reviews = hotel_data.get("total_reviews") or hotel_data.get("review_count")
        average_rating = hotel_data.get("average_rating") or hotel_data.get("rating")
        total_photos = hotel_data.get("total_photos") or hotel_data.get("photo_count")
        whatsapp = hotel_data.get("whatsapp", "")

        # Determine if we have real GBP data
        has_real_data = bool(total_reviews or average_rating)
        data_source_label = "GBP (Google Business Profile)" if has_real_data else "N/D"

        if not period:
            period = datetime.now().strftime("%B %Y").capitalize()

        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Dynamic assets table
        output_dir = hotel_data.get("output_dir", "")
        assets_table = self._generate_assets_table(output_dir, asset_report_path, generated_at)

        md = f"""# Informe Mensual de Marketing Digital — {hotel_name}

**Período**: {period}
**Hotel**: {hotel_name}
**Datos reales**: {"✅ Sí" if has_real_data else "⚠️ Requiere fuentes adicionales"} ({data_source_label})"""
        if city:
            md += f"  \n**Ubicación**: {city}"
        if website:
            md += f"  \n**Sitio web**: {website}"
        md += f"""
**Generado**: {generated_at}

---

## 1. KPIs a Monitorear

### Tráfico Web (Google Analytics 4)

| Métrica | Este Mes | Mes Anterior | Variación |
|---------|----------|--------------|-----------|
| Sesiones totales | Por confirmar | Por confirmar | —% |
| Usuarios nuevos | Por confirmar | Por confirmar | —% |
| Tasa de rebote | —% | —% | |
| Páginas/sesión | Por confirmar | Por confirmar | |
| Duración promedio sesión | Por confirmar | Por confirmar | |

### Google Business Profile (GBP)

| Métrica | Valor Actual | Fuente |
|---------|-------------|--------|
| Reseñas totales | {total_reviews if total_reviews else "Por confirmar"} | {data_source_label} |
| Rating promedio | {average_rating if average_rating else "Por confirmar"} | {data_source_label} |
| Fotos totales | {total_photos if total_photos else "Por confirmar"} | {data_source_label} |
| Vistas en búsqueda | Por confirmar | Requiere GA4/GSC |
| Vistas en Maps | Por confirmar | Requiere GA4/GSC |
| Acciones totales | Por confirmar | Requiere GA4/GSC |

### Reservas Directas

| Métrica | Este Mes | Mes Anterior | Variación |
|---------|----------|--------------|-----------|
| Reservas directas (canal propio) | Por confirmar | Por confirmar | —% |
| Ingresos por reservas directas | $Por confirmar | $Por confirmar | —% |
| Tasa de conversión | —% | —% | |
| ADR (Tarifa Promedio Diaria) | $Por confirmar | $Por confirmar | —% |

### WhatsApp

| Métrica | Este Mes | Mes Anterior | Variación |
|---------|----------|--------------|-----------|
| Clics en botón WhatsApp | Por confirmar | Por confirmar | —% |
| Conversaciones iniciadas | Por confirmar | Por confirmar | —% |
| Reservas vía WhatsApp | Por confirmar | Por confirmar | —% |

### SEO y Visibilidad

| Métrica | Este Mes | Mes Anterior | Variación |
|---------|----------|--------------|-----------|
| Clics orgánicos (GSC) | Por confirmar | Por confirmar | —% |
| Impresiones (GSC) | Por confirmar | Por confirmar | —% |
| CTR promedio | —% | —% | |
| Posición promedio | Por confirmar | Por confirmar | |

---

## 2. Checklist de Acciones Mensuales

### SEO Técnico
- [ ] Revisar errores en Google Search Console
- [ ] Verificar que schema markup esté activo y sin errores
- [ ] Comprobar velocidad de carga (Core Web Vitals)
- [ ] Revisar indexación de páginas nuevas

### Google Business Profile
- [ ] Publicar al menos 4 posts/actualizaciones
- [ ] Responder TODAS las reseñas (positivas y negativas)
- [ ] Actualizar fotos (agregar 5+ fotos nuevas)
- [ ] Verificar horarios y datos de contacto
- [ ] Revisar preguntas frecuentes y responder

### Contenido
- [ ] Publicar artículo de blog nuevo (si aplica)
- [ ] Actualizar contenido estacional/ofertas
- [ ] Revisar y actualizar FAQ
- [ ] Verificar enlaces internos y externos

### Conversión
- [ ] Revisar funcionamiento del botón WhatsApp
- [ ] Probar proceso de reserva directa
- [ ] Verificar que números de teléfono sean clickeables
- [ ] Revisar formulario de contacto

### Redes Sociales
- [ ] Publicar contenido regular (3-5 posts/semana)
- [ ] Interactuar con comentarios y mensajes
- [ ] Monitorear menciones del hotel

---

## 3. Información de Contacto del Hotel

| Canal | Valor |
|-------|-------|
| **Nombre** | {hotel_name} |
| **Dirección** | {address or "Por configurar"} |
| **Teléfono** | {phone or "Por configurar"} |
| **WhatsApp** | {whatsapp or phone or "Por configurar"} |
| **Email** | {email or "Por configurar"} |
| **Website** | {website or "Por configurar"} |

---

## 4. Resumen de Assets Entregados

{assets_table}

---

## 5. Próximos Pasos Recomendados

### Prioridad Alta (esta semana)
1. Configurar Google Analytics 4 si no está activo
2. Implementar schema Hotel en el sitio web
3. Revisar y optimizar perfil de Google Business Profile

### Prioridad Media (este mes)
1. Crear contenido local optimizado
2. Implementar botón WhatsApp en todas las páginas
3. Configurar seguimiento de conversiones

### Prioridad Baja (próximo trimestre)
1. Desarrollar estrategia de contenido de blog
2. Implementar reseñas automáticas post-estadía
3. Evaluar integración con plataformas de voz

---

## 6. Notas y Observaciones

| Nota | Fecha |
|------|-------|
| | |
| | |
| | |

---

## 7. Disclaimer

> **Nota sobre métricas**: Este informe es una plantilla de seguimiento. Los valores
> numéricos requieren la configuración de las siguientes herramientas:
>
> - **Google Analytics 4 (GA4)**: Para métricas de tráfico web
> - **Google Search Console (GSC)**: Para métricas de SEO
> - **Google Business Profile API**: Para métricas de GBP
> - **Sistema de reservas propio**: Para métricas de conversión
> - **WhatsApp Business API**: Para métricas de mensajería
>
> Sin estas configuraciones, las celdas de métricas permanecerán vacías.
> Contacte a su equipo de IA Hoteles para asistencia con la configuración.

---

*Informe generado automáticamente por IA Hoteles (iah-cli)*
*Pipeline R4 - FASE-PERSONALIZATION*
*Período: {period}*
*Generado: {generated_at}*
"""
        return md

    def _generate_assets_table(
        self,
        output_dir: str = "",
        asset_report_path: Optional[str] = None,
        generated_at: Optional[str] = None,
    ) -> str:
        """Genera tabla dinámica basada en asset_generation_report.json.

        Args:
            output_dir: Directorio de output del pipeline.
            asset_report_path: Path explícito al JSON de assets. Si se provee,
                              se usa directamente y output_dir se ignora.
            generated_at: Timestamp de generación (para columna Última Actualización).

        Returns:
            Markdown string con la tabla de assets.
        """
        if asset_report_path is None and output_dir:
            asset_report_path = os.path.join(output_dir, 'asset_generation_report.json')

        assets_data = {}
        if asset_report_path and os.path.exists(asset_report_path):
            try:
                with open(asset_report_path, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                    assets_data = report.get('generated_assets', {})
            except (json.JSONDecodeError, IOError):
                pass

        if not assets_data:
            return "| No se generaron assets en esta ejecucion |\n"

        if generated_at is None:
            generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        rows = []
        for asset_type, info in assets_data.items():
            can_use = info.get('can_use', False)
            status = "✅ Entregado" if can_use else "⚠️ No disponible"
            confidence = info.get('confidence_score', 0.0)
            rows.append(f"| {asset_type} | {status} | {generated_at} |")

        header = "| Asset | Estado | Última Actualización |\n|-------|--------|---------------------|\n"
        return header + "\n".join(rows)


def get_monthly_report_generator() -> MonthlyReportGenerator:
    """Factory function to get MonthlyReportGenerator instance."""
    return MonthlyReportGenerator()