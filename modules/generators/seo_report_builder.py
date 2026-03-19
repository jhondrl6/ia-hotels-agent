from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List


class SEOAcceleratorReportBuilder:
    """Genera el entregable 03_SEO_ACCELERATOR en formato Markdown."""

    def __init__(self, analysis_result: Dict[str, Any], hotel_name: str, url: str) -> None:
        self.analysis = analysis_result
        self.hotel_name = hotel_name or "Hotel"
        self.url = url
        metadata = analysis_result.get("metadata", {})
        self.location = metadata.get("location") or metadata.get("ubicacion") or "N/D"

    def build_markdown(self) -> str:
        sections = [
            self._build_header(),
            self._build_score_section(),
            self._build_financial_section(),
            self._build_issues_section(),
            self._build_roadmap_section(),
            self._build_content_plan_section(),
            self._build_keywords_section(),
            self._build_recommendations_section(),
        ]
        return "\n\n".join(section for section in sections if section)

    def write(self, output_dir: Path, filename: str = "03_SEO_ACCELERATOR.md") -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / filename
        report_path.write_text(self.build_markdown(), encoding="utf-8")
        return report_path

    # ------------------------------------------------------------------
    # Secciones
    # ------------------------------------------------------------------
    def _build_header(self) -> str:
        score = self.analysis.get("score", {})
        total = score.get("total", 0)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        return (
            "# 🎯 DIAGNÓSTICO SEO ESTRUCTURADO\n"
            f"**Hotel:** {self.hotel_name}\n"
            f"**URL:** {self.url}\n"
            f"**Fecha:** {timestamp}\n\n"
            "---"
        )

    def _build_score_section(self) -> str:
        score = self.analysis.get("score", {})
        return (
            "\n## 📊 RESUMEN EJECUTIVO\n\n"
            f"### Score SEO Global: **{score.get('total', 0)}/100**\n"
            "```\n"
            f"  Técnico:    {score.get('technical', 0)}/100  {'█' * (score.get('technical', 0)//5)}\n"
            f"  Contenido:  {score.get('content', 0)}/100  {'█' * (score.get('content', 0)//5)}\n"
            f"  Conversión: {score.get('conversion', 0)}/100  {'█' * (score.get('conversion', 0)//5)}\n"
            f"  Local SEO:  {score.get('local_seo', 0)}/100  {'█' * (score.get('local_seo', 0)//5)}\n"
            f"  Reputación: {score.get('reputation', 0)}/100  {'█' * (score.get('reputation', 0)//5)}\n"
            "```"
        )

    def _build_financial_section(self) -> str:
        financial = self.analysis.get("financial_impact", {})
        return (
            "\n### 💰 Impacto Financiero\n"
            f"- **Ingresos mensuales perdidos estimados:** ${self._format_currency(financial.get('estimated_monthly_loss'))} COP\n"
            f"- **Potencial de mejora:** {financial.get('potential_improvement_percentage', 0)}%\n"
            f"- **Ganancia mensual proyectada tras fixes:** ${self._format_currency(financial.get('projected_monthly_gain'))} COP\n"
            "- **ROI esperado:** 300-500% en primeros 3 meses"
        )

    def _build_issues_section(self) -> str:
        issues: List[Dict[str, Any]] = self.analysis.get("issues", [])
        if not issues:
            return "\n## ✅ No se detectaron problemas críticos\n"

        grouped = {priority: [] for priority in ("CRÍTICO", "ALTO", "MEDIO", "BAJO")}
        for issue in issues:
            grouped.setdefault(issue.get("priority", "MEDIO"), []).append(issue)

        lines = ["\n## 🚨 ANÁLISIS DETALLADO\n"]
        icons = {"CRÍTICO": "🔴", "ALTO": "🟠", "MEDIO": "🟡", "BAJO": "🟢"}

        for priority in ("CRÍTICO", "ALTO", "MEDIO", "BAJO"):
            bucket = grouped.get(priority)
            if not bucket:
                continue
            lines.append(f"### {icons[priority]} Problemas de Prioridad {priority} ({len(bucket)})\n")
            for issue in bucket:
                lines.extend(self._format_issue(issue))
        return "\n".join(lines)

    def _build_roadmap_section(self) -> str:
        roadmap = self.analysis.get("roadmap", {})
        lines = ["\n## 🗺️ HOJA DE RUTA DE IMPLEMENTACIÓN", ""]
        lines.append("### 📅 Semana 1-2: Correcciones Críticas")
        lines.extend(self._format_tasks(roadmap.get("semana_1_2", [])))
        lines.append("")
        lines.append("### 📅 Semana 3-4: Optimizaciones Principales")
        lines.extend(self._format_tasks(roadmap.get("semana_3_4", [])))
        lines.append("")
        lines.append("### 📅 Mes 2: Mejoras Continuas")
        lines.extend(self._format_tasks(roadmap.get("mes_2", [])))
        return "\n".join(lines)

    def _build_content_plan_section(self) -> str:
        plan = self.analysis.get("content_plan", {})
        if not plan:
            return ""
        lines = ["\n## ✍️ PLAN DE CONTENIDO SEO RECOMENDADO", ""]
        blog_posts = plan.get("blog_posts", [])
        if blog_posts:
            lines.append("### 📝 Artículos de Blog Sugeridos")
            lines.extend(f"{idx}. {idea}" for idx, idea in enumerate(blog_posts[:5], 1))
            lines.append("")
        faqs = plan.get("faqs", [])
        if faqs:
            lines.append("### ❓ Preguntas Frecuentes (FAQ)")
            lines.extend(f"{idx}. {idea}" for idx, idea in enumerate(faqs[:5], 1))
            lines.append("")
        guides = plan.get("local_guides", [])
        if guides:
            lines.append("### 🗺️ Guías Locales")
            lines.extend(f"{idx}. {idea}" for idx, idea in enumerate(guides[:5], 1))
        return "\n".join(lines)

    def _build_keywords_section(self) -> str:
        keywords = self.analysis.get("keywords", [])
        if not keywords:
            return ""
        lines = ["\n## 🔑 KEYWORDS LOCALES RECOMENDADAS", ""]
        lines.extend(f"{idx}. `{keyword}`" for idx, keyword in enumerate(keywords, 1))
        return "\n".join(lines)

    def _build_recommendations_section(self) -> str:
        return (
            "\n## 💡 RECOMENDACIONES FINALES\n\n"
            "### Acciones Inmediatas (Hoy)\n"
            "1. Activar certificado SSL y revisar uptime\n"
            "2. Actualizar título, meta description y H1\n"
            "3. Agregar botones claros de reserva y WhatsApp\n"
            "4. Reclamar/optimizar Google Business Profile\n\n"
            "### Próximos 7 Días\n"
            "1. Optimizar imágenes (peso + ALT)\n"
            "2. Implementar Schema Hotel + FAQ\n"
            "3. Publicar testimonios y reseñas verificadas\n"
            "4. Validar experiencia móvil real\n\n"
            "### Estrategia a 30 Días\n"
            "1. Publicar contenido de blog estratégico\n"
            "2. Automatizar recolección de reseñas\n"
            "3. Configurar Google Analytics y Search Console\n"
            "4. Lanzar campañas de remarketing para tráfico orgánico"
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _format_issue(self, issue: Dict[str, Any]) -> List[str]:
        lines = [
            f"#### {issue.get('icon', '•')} {issue.get('title', 'Issue')}",
            f"**Problema:** {issue.get('problem', 'No disponible')}",
            f"**Impacto:** {issue.get('impact', 'Sin datos de impacto')}",
            f"**Solución:** {issue.get('solution', 'Sin recomendación')}",
        ]
        loss = issue.get('estimated_monthly_loss')
        improvement = issue.get('estimated_improvement')
        if isinstance(loss, int) and loss > 0:
            lines.append(f"**Pérdida estimada:** ${self._format_currency(loss)} COP/mes")
        if improvement:
            lines.append(f"**Mejora esperada:** {improvement}")
        lines.append(f"**Tiempo de implementación:** {issue.get('fix_time', 'N/D')}")
        category = issue.get('category', 'general').replace('_', ' ').title()
        lines.append(f"**Categoría:** {category}\n")
        return lines

    def _format_tasks(self, tasks: Iterable[Dict[str, Any]]) -> List[str]:
        formatted: List[str] = []
        for task in tasks:
            formatted.append(
                f"- [ ] **{task.get('tarea', 'Tarea')}** - {task.get('tiempo', 'N/D')} → {task.get('impacto', 'Impacto no estimado')}"
            )
        if not formatted:
            formatted.append("- (sin tareas registradas)")
        return formatted

    @staticmethod
    def _format_currency(value: Any) -> str:
        if isinstance(value, (int, float)):
            return f"{int(value):,}"
        return "0"
