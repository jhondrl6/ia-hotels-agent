"""GEO Dashboard Generator - Creates diagnostic dashboards with bands and gaps.

This generator creates markdown dashboards showing:
- Total score with band classification
- Breakdown by 8 evaluation areas
- Prioritized gap list
- Recommendations for next steps

Reference: FASE-3 specification
"""

from typing import List

from data_models.canonical_assessment import CanonicalAssessment

from .geo_diagnostic import GEOAssessment, GEOBand


class GEODashboard:
    """Generates GEO diagnostic dashboards in markdown format.
    
    Provides two output formats:
    - Minimal: For EXCELLENT band (lightweight summary)
    - Full: For GOOD/FOUNDATION/CRITICAL bands (detailed breakdown)
    """

    # Area display names
    AREA_NAMES = {
        "robots": "Robots.txt",
        "llms": "LLMs.txt",
        "schema": "Schema.org",
        "meta": "Meta Tags",
        "content": "Contenido",
        "brand": "Marca/Entidad",
        "signals": "Señales",
        "ai_discovery": "AI Discovery",
    }

    # Area max scores
    AREA_MAX = {
        "robots": 18,
        "llms": 18,
        "schema": 16,
        "meta": 14,
        "content": 12,
        "brand": 10,
        "signals": 6,
        "ai_discovery": 6,
    }

    def generate_full(self, hotel_data: CanonicalAssessment, geo_assessment: GEOAssessment) -> str:
        """Generate full dashboard for GOOD/FOUNDATION/CRITICAL bands.
        
        Args:
            hotel_data: CanonicalAssessment with hotel information.
            geo_assessment: GEOAssessment with diagnostic results.
            
        Returns:
            Complete dashboard markdown.
        """
        band = geo_assessment.band
        
        lines = [
            "# GEO Dashboard - Diagnóstico Completo",
            "",
            f"**Hotel:** {hotel_data.site_metadata.title}",
            f"**URL:** {hotel_data.url}",
            f"**Fecha:** 2026-03-30",
            "",
            "---",
            "",
        ]
        
        # Score section with band
        lines.extend(self._render_score_section(geo_assessment))
        lines.append("")
        
        # Band interpretation
        lines.extend(self._render_band_interpretation(band))
        lines.append("")
        
        # Breakdown by area
        lines.extend(self._render_breakdown(geo_assessment))
        lines.append("")
        
        # Gaps section
        if geo_assessment.gaps_blocking:
            lines.extend(self._render_gaps("Bloqueantes", geo_assessment.gaps_blocking))
            lines.append("")
        
        if geo_assessment.gaps_mitigable:
            lines.extend(self._render_gaps("Mitigables", geo_assessment.gaps_mitigable[:5]))
            lines.append("")
        
        # Recommendations
        if geo_assessment.recommendations:
            lines.extend(self._render_recommendations(geo_assessment.recommendations))
        
        return "\n".join(lines)

    def generate_minimal(self, hotel_data: CanonicalAssessment, geo_assessment: GEOAssessment) -> str:
        """Generate minimal dashboard for EXCELLENT band.
        
        Args:
            hotel_data: CanonicalAssessment with hotel information.
            geo_assessment: GEOAssessment with diagnostic results.
            
        Returns:
            Lightweight dashboard markdown.
        """
        lines = [
            "# GEO Dashboard - Resumen",
            "",
            f"**Hotel:** {hotel_data.site_metadata.title}",
            f"**Score:** {geo_assessment.total_score}/100",
            f"**Banda:** {geo_assessment.band.value.upper()}",
            "",
            "---",
            "",
            "## Estado: Excelente",
            "",
            "Tu hotel está bien posicionado para descubrimiento por IA.",
            "Los fundamentos de SEO y estructura de datos están sólidos.",
            "",
        ]
        
        # Show top areas only
        breakdown = geo_assessment.breakdown
        lines.append("## Áreas Evaluadas")
        lines.append("")
        
        area_scores = [
            ("robots", breakdown.robots, 18),
            ("llms", breakdown.llms, 18),
            ("schema", breakdown.schema, 16),
            ("meta", breakdown.meta, 14),
        ]
        
        for area, score, max_score in area_scores:
            pct = score / max_score * 100 if max_score > 0 else 0
            bar = self._render_bar(pct)
            area_name = self.AREA_NAMES.get(area, area)
            lines.append(f"{area_name}: {bar} {pct:.0f}%")
        
        lines.append("")
        
        # Only show recommendations if there are any
        if geo_assessment.recommendations:
            lines.append("## Siguiente Paso")
            lines.append("")
            lines.append(f"- {geo_assessment.recommendations[0]}")
        
        return "\n".join(lines)

    def _render_score_section(self, geo_assessment: GEOAssessment) -> List[str]:
        """Render score display with band."""
        band = geo_assessment.band
        score = geo_assessment.total_score
        
        # Band emoji and color
        band_icons = {
            GEOBand.EXCELLENT: ("🌟", "EXCELENTE"),
            GEOBand.GOOD: ("👍", "BUENO"),
            GEOBand.FOUNDATION: ("📋", "FUNDACIÓN"),
            GEOBand.CRITICAL: ("🚨", "CRÍTICO"),
        }
        
        emoji, label = band_icons[band]
        
        # Score bar
        score_pct = score
        score_bar = self._render_bar(score_pct, width=40)
        
        lines = [
            "## Score GEO",
            "",
            f"# {emoji} {score}/100 - {label}",
            "",
            f"[{score_bar}]",
            "",
            f"| Rango | Score |",
            f"|-------|-------|",
            f"| CRITICO | 0-35 |",
            f"| FUNDACION | 36-67 |",
            f"| BUENO | 68-85 |",
            f"| EXCELENTE | 86-100 |",
            "",
        ]
        
        return lines

    def _render_band_interpretation(self, band: GEOBand) -> List[str]:
        """Render band interpretation text."""
        interpretations = {
            GEOBand.EXCELLENT: [
                "## Interpretación",
                "",
                "Tu sitio web tiene una base sólida para descubrimiento por IA.",
                "Los crawlers de IA (ChatGPT, Claude, Perplexity) pueden acceder",
                "y entender tu contenido efectivamente.",
                "",
                "**Recomendación:** Mantén las buenas prácticas y considera",
                "enriquecimiento adicional para maximizar visibilidad.",
            ],
            GEOBand.GOOD: [
                "## Interpretación",
                "",
                "Tu sitio web tiene fundamentos adecuados con margen de mejora.",
                "Algunas áreas necesitan atención para maximizar el descubrimiento por IA.",
                "",
                "**Recomendación:** Implementa las mejoras sugeridas en el",
                "checklist para alcanzar el nivel EXCELENTE.",
            ],
            GEOBand.FOUNDATION: [
                "## Interpretación",
                "",
                "Tu sitio web necesita mejoras significativas para ser descubrible por IA.",
                "Existen gaps bloqueantes que impiden que los crawlers de IA",
                "accedan o entiendan tu contenido correctamente.",
                "",
                "**Recomendación:** Prioriza las acciones recomendadas en",
                "geo_fix_kit.md para establecer una base sólida.",
            ],
            GEOBand.CRITICAL: [
                "## Interpretación",
                "",
                "🚨 **INTERVENCIÓN URGENTE REQUERIDA**",
                "",
                "Tu sitio web tiene problemas críticos que impiden",
                "completamente el descubrimiento por IA.",
                "",
                "**Recomendación:** Implementa TODAS las correcciones en",
                "seo_fix_kit.md y robots_fix.txt inmediatamente.",
            ],
        }
        
        return interpretations.get(band, [])

    def _render_breakdown(self, geo_assessment: GEOAssessment) -> List[str]:
        """Render breakdown by 8 areas."""
        breakdown = geo_assessment.breakdown
        
        lines = [
            "## Breakdown por Área",
            "",
            "| Área | Score | Máximo | % |",
            "|------|-------|--------|---|",
        ]
        
        area_scores = [
            ("robots", breakdown.robots, 18),
            ("llms", breakdown.llms, 18),
            ("schema", breakdown.schema, 16),
            ("meta", breakdown.meta, 14),
            ("content", breakdown.content, 12),
            ("brand", breakdown.brand, 10),
            ("signals", breakdown.signals, 6),
            ("ai_discovery", breakdown.ai_discovery, 6),
        ]
        
        for area, score, max_score in area_scores:
            pct = score / max_score * 100 if max_score > 0 else 0
            area_name = self.AREA_NAMES.get(area, area)
            bar = self._render_bar(pct, width=20)
            lines.append(f"| {area_name} | {score}/{max_score} | {bar} | {pct:.0f}% |")
        
        return lines

    def _render_gaps(self, gap_type: str, gaps: List[str]) -> List[str]:
        """Render gap list."""
        lines = [
            f"## Gaps {gap_type}",
            "",
        ]
        
        for i, gap in enumerate(gaps, 1):
            lines.append(f"{i}. {gap}")
        
        lines.append("")
        return lines

    def _render_recommendations(self, recommendations: List[str]) -> List[str]:
        """Render recommendations section."""
        lines = [
            "## Recomendaciones",
            "",
        ]
        
        for i, rec in enumerate(recommendations, 1):
            lines.append(f"{i}. {rec}")
        
        lines.append("")
        return lines

    def _render_bar(self, percentage: float, width: int = 20) -> str:
        """Render ASCII progress bar.
        
        Args:
            percentage: 0-100 value.
            width: Character width of bar.
            
        Returns:
            ASCII progress bar string.
        """
        filled = int(percentage / 100 * width)
        empty = width - filled
        
        # Use block characters for better visualization
        bar = "█" * filled + "░" * empty
        
        return f"[{bar}]"
