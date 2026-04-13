"""Monthly Report Generator - Template for recurring monthly KPI tracking.

Generates a monthly tracking report template that clients can use with their
own GA4/GSC/GBP data. Does not require real metrics - produces a fillable template.
"""

from datetime import datetime
from typing import Dict, Any, Optional


class MonthlyReportGenerator:
    """Generates monthly KPI tracking report for hotels."""

    def generate(
        self,
        hotel_data: Dict[str, Any],
        period: Optional[str] = None
    ) -> str:
        """Generate monthly report markdown.

        Args:
            hotel_data: Dictionary with hotel information (name, city, etc.)
            period: Report period string (e.g., "Enero 2026"). Defaults to current month.

        Returns:
            Markdown string with monthly report template.
        """
        hotel_name = hotel_data.get("name") or hotel_data.get("nombre", "Hotel")
        city = hotel_data.get("city") or hotel_data.get("ubicacion", "")
        website = hotel_data.get("website") or hotel_data.get("url", "")

        if not period:
            period = datetime.now().strftime("%B %Y").capitalize()

        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        md = f"""# Informe Mensual de Marketing Digital — {hotel_name}

**Período**: {period}
**Hotel**: {hotel_name}"""
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
| Sesiones totales | _____ | _____ | ___% |
| Usuarios nuevos | _____ | _____ | ___% |
| Tasa de rebote | ___% | ___% | |
| Páginas/sesión | _____ | _____ | |
| Duración promedio sesión | _____ | _____ | |

### Google Business Profile (GBP)

| Métrica | Este Mes | Mes Anterior | Variación |
|---------|----------|--------------|-----------|
| Vistas en búsqueda | _____ | _____ | ___% |
| Vistas en Maps | _____ | _____ | ___% |
| Acciones totales | _____ | _____ | ___% |
| Llamadas desde GBP | _____ | _____ | ___% |
| Direcciones solicitadas | _____ | _____ | ___% |
| Clicks al sitio web | _____ | _____ | ___% |

### Reservas Directas

| Métrica | Este Mes | Mes Anterior | Variación |
|---------|----------|--------------|-----------|
| Reservas directas (canal propio) | _____ | _____ | ___% |
| Ingresos por reservas directas | $_____ | $_____ | ___% |
| Tasa de conversión | ___% | ___% | |
| ADR (Tarifa Promedio Diaria) | $_____ | $_____ | ___% |

### WhatsApp

| Métrica | Este Mes | Mes Anterior | Variación |
|---------|----------|--------------|-----------|
| Clicks en botón WhatsApp | _____ | _____ | ___% |
| Conversaciones iniciadas | _____ | _____ | ___% |
| Reservas vía WhatsApp | _____ | _____ | ___% |

### SEO y Visibilidad

| Métrica | Este Mes | Mes Anterior | Variación |
|---------|----------|--------------|-----------|
| Clicks orgánicos (GSC) | _____ | _____ | ___% |
| Impresiones (GSC) | _____ | _____ | ___% |
| CTR promedio | ___% | ___% | |
| Posición promedio | _____ | _____ | |

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

## 3. Resumen de Assets Entregados

| Asset | Estado | Última Actualización |
|-------|--------|---------------------|
| Schema Hotel (JSON-LD) | ✅ Entregado | _____ |
| Geo Playbook | ✅ Entregado | _____ |
| Guía de Optimización SEO | ✅ Entregado | _____ |
| Plan de Reseñas | ✅ Entregado | _____ |
| Botón WhatsApp | ✅ Entregado | _____ |
| Voice Assistant Guide | ✅ Entregado | _____ |
| Informe Mensual | ✅ Este documento | {generated_at} |
| FAQ Page | ✅ Entregado | _____ |
| Guía de Tráfico Indirecto | ✅ Entregado | _____ |

---

## 4. Próximos Pasos Recomendados

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

## 5. Notas y Observaciones

| Nota | Fecha |
|------|-------|
| | |
| | |
| | |

---

## 6. Disclaimer

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
*Período: {period}*
*Generado: {generated_at}*
"""
        return md
