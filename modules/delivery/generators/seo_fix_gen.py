"""Generador de kits para el Acelerador SEO."""

from __future__ import annotations

from typing import Any, Dict, List


class SEOFixGenerator:
    """Entrega instrucciones accionables para los 4 hallazgos críticos de la propuesta."""

    def generate(self, hotel_data: Dict[str, Any], 
                 seo_issues: List[Dict] = None,
                 reason: str = None) -> str:
        """Genera kit SEO con issues específicos y justificación.
        
        Args:
            hotel_data: Datos del hotel
            seo_issues: Lista de issues SEO detectados (opcional)
            reason: Justificación de por qué se genera este archivo
        """
        nombre = hotel_data.get("nombre") or hotel_data.get("name", "Hotel")
        ubicacion = hotel_data.get("ubicacion") or hotel_data.get("city", "Colombia")
        promedio = hotel_data.get("precio_promedio", "---")
        
        # v3.3.1: CMS Detection & Recommendations
        cms_info = hotel_data.get("cms_detected", {})
        cms_type = cms_info.get("cms", "unknown") if isinstance(cms_info, dict) else "unknown"
        theme = cms_info.get("theme", "unknown") if isinstance(cms_info, dict) else "unknown"

        sections: List[str] = []
        
        # NUEVO v3.5: Justificación dinámica
        if reason:
            sections.append(f"> **🎯 Por qué este archivo:** {reason}")
            sections.append("")
        
        sections.extend([
            f"# Kit de Fixes SEO - {nombre}",
            f"Ubicación: {ubicacion} · ADR promedio reportado: {promedio}",
        ])
        
        # NUEVO v3.5: Issues específicos si existen
        if seo_issues:
            sections.append("\n## 🔍 Issues Detectados en Tu Sitio\n")
            sections.append("_El diagnóstico identificó los siguientes problemas técnicos:_\n")
            
            priority_order = {"CRÍTICO": 0, "ALTO": 1, "MEDIO": 2, "BAJO": 3}
            sorted_issues = sorted(seo_issues, 
                                   key=lambda x: priority_order.get(x.get("priority", "MEDIO"), 2))
            
            for issue in sorted_issues:
                icon = issue.get("icon", "⚠️")
                title = issue.get("title", "Issue detectado")
                problem = issue.get("problem", "")
                impact = issue.get("impact", "")
                solution = issue.get("solution", "")
                monthly_loss = issue.get("estimated_monthly_loss", 0)
                priority = issue.get("priority", "MEDIO")
                fix_time = issue.get("fix_time", "")
                
                sections.append(f"### {icon} {title}")
                sections.append(f"- **Prioridad:** {priority}")
                sections.append(f"- **Problema:** {problem}")
                sections.append(f"- **Impacto:** {impact}")
                if monthly_loss > 0:
                    sections.append(f"- **Pérdida estimada:** ${monthly_loss:,.0f} COP/mes")
                if solution:
                    sections.append(f"- **Solución:** {solution}")
                if fix_time:
                    sections.append(f"- **Tiempo estimado:** {fix_time}")
                sections.append("")
            
            sections.append("---\n")
        
        sections.extend([
            "## 1. CTA claro para reservar",
            "- Actualizar hero del sitio con botón `Reserva Directo` enlazado a motor propio o WhatsApp oficial.",
            "- Añadir CTA secundario en cada sección larga (habitaciones, experiencias).",
            "- Implementar barra fija inferior en móviles con CTA `Planear mi estadía`.",
            "- Validación: ejecutar inspección manual y registrar captura en drive.",
            "\n## 2. Schema.org completo",
            "- Utilizar `hotel-schema.json` generado en delivery_assets.",
            "- Insertar en `<head>` con `<script type=\"application/ld+json\">`.",
            "- Validar en https://search.google.com/test/rich-results",
            "- Registrar fecha y responsable en checklist.",
            "\n## 3. Core Web Vitals (LCP/CLS)",
            "- Ejecutar Lighthouse (Chrome DevTools) en desktop y mobile.",
            "- Prioridad: puntaje LCP < 2.5s, CLS < 0.1, TBT < 200ms.",
            "- Acciones sugeridas: comprimir hero (WebP), lazy load galerías, activar cache HTTP.",
        ])

        # v3.3.1: CMS-Specific Technical Recommendations
        if cms_type == "wordpress":
            sections.append("- [WordPress] Instalar plugin de caché (WP Rocket o LiteSpeed) y desactivar emojis nativos.")
            if "divi" in theme.lower():
                sections.append("- [Divi Fix] Desactivar Sliders en vista Móvil para reducir LCP y mejorar CLS.")
        elif cms_type == "wix":
            sections.append("- [Wix] Optimizar imágenes mediante el panel de control y evitar fuentes personalizadas pesadas.")

        sections.extend([
            "- Configurar monitoreo semanal con https://www.debugbear.com/ (plan free) o PageSpeed API.",
            "\n## 4. Gestión de reseñas",
            "- Activar el playbook en `review_plan.md` (mismo directorio).",
            "- Meta: 20 reseñas nuevas/30 días, rating ≥4.6.",
            "- Conectar automatización con WhatsApp Business o Zapier (plantilla incluida).",
            "\n## Cronograma recomendado",
            "| Día | Actividad | Responsable | Evidencia |",
            "|-----|-----------|-------------|-----------|",
            "| 1 | Actualizar CTA en home + header | Equipo web | URL + captura |",
            "| 2 | Subir schema y validar en Rich Results | Tech/IT | Screenshot reporte |",
            "| 3 | Ejecutar Lighthouse + aplicar quick wins | Web + Agencia | Reporte Lighthouse |",
            "| 4-7 | Lanzar campaña reseñas automatizada | Front desk | Sheet reseñas |",
            "| 7 | Validar checklist completo con IA Hoteles | PM | Checklist firmado |",
            "\n## Métricas de seguimiento",
            "- Incremento CTR web vs OTA (meta +15% en 30 días).",
            "- Score Credibilidad Web (objetivo ≥80/100).",
            "- Conversión visitas→reservas (meta +2 pp).",
        ])

        return "\n".join(sections)
