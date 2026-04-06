"""GEO Enrichment Layer - Conditional asset generation by score band.

This module implements the enrichment phase of GEO Integration, generating
enriched assets conditionally based on the GEO assessment band.

Architecture:
- Receives: hotel_data (CanonicalAssessment) + geo_assessment (GEOAssessment)
- Decision: Band determines which assets to generate
- Output: Files in geo_enriched/ subdirectory (no collision with existing)

Bands and Assets:
- EXCELLENT (86-100): geo_badge.md, geo_dashboard_min.md
- GOOD (68-85): geo_badge.md, geo_dashboard.md, geo_checklist_min.md
- FOUNDATION (36-67): + llms.txt, hotel_schema_rich.json, faq_schema.json, geo_fix_kit.md
- CRITICAL (0-35): + robots_fix.txt, seo_fix_kit.md, seccion_propuesta

Reference: FASE-3 prompt, dependencies-fases.md
"""

import os
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from data_models.canonical_assessment import CanonicalAssessment

from .geo_diagnostic import GEOAssessment, GEOBand
from .llms_txt_generator import LLMsTxtGenerator
from .hotel_schema_enricher import HotelSchemaEnricher
from .geo_dashboard import GEODashboard
from .sync_contract import SyncContractAnalyzer, SyncResult, analyze_sync

logger = logging.getLogger(__name__)


# =============================================================================
# FILENAME CONSTANTS
# =============================================================================

FILENAME_GEO_BADGE = "geo_badge.md"
FILENAME_GEO_DASHBOARD_MIN = "geo_dashboard_min.md"
FILENAME_GEO_DASHBOARD = "geo_dashboard.md"
FILENAME_GEO_CHECKLIST_MIN = "geo_checklist_min.md"
FILENAME_LLMS_TXT = "llms.txt"
FILENAME_HOTEL_SCHEMA_RICH = "hotel_schema_rich.json"
FILENAME_FAQ_SCHEMA = "faq_schema.json"
FILENAME_GEO_FIX_KIT = "geo_fix_kit.md"
FILENAME_ROBOTS_FIX = "robots_fix.txt"
FILENAME_SEO_FIX_KIT = "seo_fix_kit.md"


class GEOEnrichmentLayer:
    """Conditional GEO enrichment layer.
    
    Generates enriched assets based on GEO band classification.
    Designed to be ORTHOGONAL to existing pipeline - only generates
    NEW assets in geo_enriched/ subdirectory.
    
    Usage:
        layer = GEOEnrichmentLayer()
        files = layer.generate(hotel_data, geo_assessment, output_dir)
    """

    def __init__(self):
        """Initialize enrichment layer with all generators."""
        self.llms_generator = LLMsTxtGenerator()
        self.schema_enricher = HotelSchemaEnricher()
        self.dashboard_generator = GEODashboard()
        self.sync_analyzer = SyncContractAnalyzer()

    def generate(
        self,
        hotel_data: CanonicalAssessment,
        geo_assessment: GEOAssessment,
        output_dir: str,
        commercial_diagnosis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate enriched assets conditionally based on GEO band.
        
        Args:
            hotel_data: CanonicalAssessment with site data.
            geo_assessment: GEOAssessment with diagnostic results.
            output_dir: Base directory for output files.
            commercial_diagnosis: Optional commercial diagnosis dict for sync.
                If provided, sync analysis is performed before generating assets.
            
        Returns:
            Dict with 'files' (list of generated paths) and 'sync_result' (SyncResult).
        """
        band = geo_assessment.band
        generated = []
        sync_result = None
        
        logger.info(f"[GEO-Enrichment] Starting for band: {band.value} ({geo_assessment.total_score}/100)")
        
        # Perform sync analysis if commercial_diagnosis is provided
        if commercial_diagnosis is not None:
            sync_result = self.sync_analyzer.analyze(commercial_diagnosis, geo_assessment)
            logger.info(f"[GEO-Enrichment] Sync analysis: {sync_result.combination_tag} (score: {sync_result.sync_score:.2f})")
            
            if not sync_result.is_consistent:
                logger.warning(f"[GEO-Enrichment] Sync inconsistency detected: {sync_result.combination_tag}")
        
        # Create output subdirectory
        geo_dir = Path(output_dir) / "geo_enriched"
        geo_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate assets based on band
        if band == GEOBand.EXCELLENT:
            generated.extend(self._generate_excellent(hotel_data, geo_assessment, geo_dir))
        elif band == GEOBand.GOOD:
            generated.extend(self._generate_good(hotel_data, geo_assessment, geo_dir))
        elif band == GEOBand.FOUNDATION:
            generated.extend(self._generate_foundation(hotel_data, geo_assessment, geo_dir))
        elif band == GEOBand.CRITICAL:
            generated.extend(self._generate_critical(hotel_data, geo_assessment, geo_dir))
        
        logger.info(f"[GEO-Enrichment] Generated {len(generated)} files: {generated}")
        
        # Generate sync report if commercial_diagnosis was provided
        if sync_result is not None:
            sync_report_path = geo_dir / "sync_report.md"
            sync_report_content = self._generate_sync_report(
                hotel_data, geo_assessment, commercial_diagnosis, sync_result
            )
            sync_report_path.write_text(sync_report_content, encoding="utf-8")
            generated.append(str(sync_report_path))
            logger.info(f"[GEO-Enrichment] Generated sync report: {sync_report_path}")
        
        return {
            "files": generated,
            "sync_result": sync_result
        }

    def _generate_excellent(
        self,
        hotel_data: CanonicalAssessment,
        geo_assessment: GEOAssessment,
        geo_dir: Path
    ) -> List[str]:
        """Generate EXCELLENT band assets: minimal enrichment.
        
        EXCELLENT (86-100): GEO is in great shape, minimal intervention.
        """
        generated = []
        
        # geo_badge.md - positive reinforcement
        badge_path = geo_dir / FILENAME_GEO_BADGE
        badge_content = self._generate_badge(hotel_data, geo_assessment, positive=True)
        badge_path.write_text(badge_content, encoding="utf-8")
        generated.append(str(badge_path))
        logger.info(f"[GEO-Enrichment] Generated EXCELLENT badge: {badge_path}")
        
        # geo_dashboard_min.md - lightweight summary
        dashboard_path = geo_dir / FILENAME_GEO_DASHBOARD_MIN
        dashboard_content = self.dashboard_generator.generate_minimal(hotel_data, geo_assessment)
        dashboard_path.write_text(dashboard_content, encoding="utf-8")
        generated.append(str(dashboard_path))
        logger.info(f"[GEO-Enrichment] Generated EXCELLENT dashboard min: {dashboard_path}")
        
        return generated

    def _generate_good(
        self,
        hotel_data: CanonicalAssessment,
        geo_assessment: GEOAssessment,
        geo_dir: Path
    ) -> List[str]:
        """Generate GOOD band assets: light enrichment.
        
        GOOD (68-85): Minor improvements recommended.
        """
        generated = []
        
        # geo_badge.md - positive with suggestions
        badge_path = geo_dir / FILENAME_GEO_BADGE
        badge_content = self._generate_badge(hotel_data, geo_assessment, positive=True)
        badge_path.write_text(badge_content, encoding="utf-8")
        generated.append(str(badge_path))
        
        # geo_dashboard.md - full dashboard
        dashboard_path = geo_dir / FILENAME_GEO_DASHBOARD
        dashboard_content = self.dashboard_generator.generate_full(hotel_data, geo_assessment)
        dashboard_path.write_text(dashboard_content, encoding="utf-8")
        generated.append(str(dashboard_path))
        
        # geo_checklist_min.md - quick wins
        checklist_path = geo_dir / FILENAME_GEO_CHECKLIST_MIN
        checklist_content = self._generate_mini_checklist(geo_assessment)
        checklist_path.write_text(checklist_content, encoding="utf-8")
        generated.append(str(checklist_path))
        
        logger.info(f"[GEO-Enrichment] Generated GOOD assets: {len(generated)} files")
        return generated

    def _generate_foundation(
        self,
        hotel_data: CanonicalAssessment,
        geo_assessment: GEOAssessment,
        geo_dir: Path
    ) -> List[str]:
        """Generate FOUNDATION band assets: full enrichment.
        
        FOUNDATION (36-67): Significant work needed.
        """
        generated = []
        
        # Core assets (from GOOD)
        badge_path = geo_dir / FILENAME_GEO_BADGE
        badge_content = self._generate_badge(hotel_data, geo_assessment, positive=False)
        badge_path.write_text(badge_content, encoding="utf-8")
        generated.append(str(badge_path))
        
        dashboard_path = geo_dir / FILENAME_GEO_DASHBOARD
        dashboard_content = self.dashboard_generator.generate_full(hotel_data, geo_assessment)
        dashboard_path.write_text(dashboard_content, encoding="utf-8")
        generated.append(str(dashboard_path))
        
        checklist_path = geo_dir / FILENAME_GEO_CHECKLIST_MIN
        checklist_content = self._generate_mini_checklist(geo_assessment)
        checklist_path.write_text(checklist_content, encoding="utf-8")
        generated.append(str(checklist_path))
        
        # FOUNDATION+ assets
        # llms.txt
        llms_path = geo_dir / FILENAME_LLMS_TXT
        llms_content = self.llms_generator.generate(hotel_data)
        llms_path.write_text(llms_content, encoding="utf-8")
        generated.append(str(llms_path))
        
        # hotel_schema_rich.json
        schema_path = geo_dir / FILENAME_HOTEL_SCHEMA_RICH
        schema_content = self.schema_enricher.enrich(hotel_data)
        schema_path.write_text(schema_content, encoding="utf-8")
        generated.append(str(schema_path))
        
        # faq_schema.json
        faq_path = geo_dir / FILENAME_FAQ_SCHEMA
        faq_content = self.schema_enricher.generate_faq_schema(hotel_data)
        faq_path.write_text(faq_content, encoding="utf-8")
        generated.append(str(faq_path))
        
        # geo_fix_kit.md
        fix_kit_path = geo_dir / FILENAME_GEO_FIX_KIT
        fix_kit_content = self._generate_fix_kit(hotel_data, geo_assessment)
        fix_kit_path.write_text(fix_kit_content, encoding="utf-8")
        generated.append(str(fix_kit_path))
        
        logger.info(f"[GEO-Enrichment] Generated FOUNDATION assets: {len(generated)} files")
        return generated

    def _generate_critical(
        self,
        hotel_data: CanonicalAssessment,
        geo_assessment: GEOAssessment,
        geo_dir: Path
    ) -> List[str]:
        """Generate CRITICAL band assets: full enrichment + urgent fixes.
        
        CRITICAL (0-35): Urgent intervention needed.
        """
        generated = []
        
        # All FOUNDATION assets
        generated.extend(self._generate_foundation(hotel_data, geo_assessment, geo_dir))
        
        # CRITICAL+ additional assets
        # robots_fix.txt
        robots_path = geo_dir / FILENAME_ROBOTS_FIX
        robots_content = self._generate_robots_fix(geo_assessment)
        robots_path.write_text(robots_content, encoding="utf-8")
        generated.append(str(robots_path))
        
        # seo_fix_kit.md
        seo_path = geo_dir / FILENAME_SEO_FIX_KIT
        seo_content = self._generate_seo_fix_kit(hotel_data, geo_assessment)
        seo_path.write_text(seo_content, encoding="utf-8")
        generated.append(str(seo_path))
        
        logger.info(f"[GEO-Enrichment] Generated CRITICAL assets: {len(generated)} files")
        return generated

    def _generate_badge(
        self,
        hotel_data: CanonicalAssessment,
        geo_assessment: GEOAssessment,
        positive: bool = True
    ) -> str:
        """Generate geo_badge.md content."""
        band_labels = {
            GEOBand.EXCELLENT: ("EXCELENTE", "🌟"),
            GEOBand.GOOD: ("BUENO", "👍"),
            GEOBand.FOUNDATION: ("FUNDACION", "📋"),
            GEOBand.CRITICAL: ("CRITICO", "🚨"),
        }
        
        label, emoji = band_labels[geo_assessment.band]
        
        if positive:
            headline = f"# {emoji} GEO {label} - ¡Tu hotel está bien posicionado!"
        else:
            headline = f"# {emoji} GEO {label} - Se requiere intervención"
        
        lines = [
            headline,
            "",
            f"**Score:** {geo_assessment.total_score}/100",
            f"**Banda:** {geo_assessment.band.value.upper()}",
            "",
            "## Resumen",
            "",
            f"- **Hotel:** {hotel_data.site_metadata.title}",
            f"- **URL:** {hotel_data.url}",
            "",
        ]
        
        if geo_assessment.gaps_blocking:
            lines.extend([
                "## Gaps Bloqueantes",
                "",
            ])
            for gap in geo_assessment.gaps_blocking:
                lines.append(f"- {gap}")
            lines.append("")
        
        if geo_assessment.recommendations:
            lines.extend([
                "## Próximos Pasos",
                "",
            ])
            for rec in geo_assessment.recommendations[:5]:
                lines.append(f"- {rec}")
            lines.append("")
        
        return "\n".join(lines)

    def _generate_mini_checklist(self, geo_assessment: GEOAssessment) -> str:
        """Generate geo_checklist_min.md content."""
        lines = [
            "# Checklist GEO - Quick Wins",
            "",
            f"**Score Actual:** {geo_assessment.total_score}/100",
            f"**Banda:** {geo_assessment.band.value.upper()}",
            "",
            "## Acciones Inmediatas",
            "",
        ]
        
        # Prioritize quick wins from recommendations
        quick_wins = [r for r in geo_assessment.recommendations if "generar" in r.lower() or "crear" in r.lower()]
        if not quick_wins:
            quick_wins = geo_assessment.recommendations[:5]
        
        for rec in quick_wins:
            lines.append(f"- [ ] {rec}")
        
        lines.extend([
            "",
            "## Áreas Prioritarias",
            "",
        ])
        
        breakdown = geo_assessment.breakdown
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
        
        # Sort by lowest score
        area_scores.sort(key=lambda x: x[1] / x[2] if x[2] > 0 else 1)
        
        for area, score, max_score in area_scores[:4]:
            pct = (score / max_score * 100) if max_score > 0 else 0
            lines.append(f"- **{area}**: {score}/{max_score} ({pct:.0f}%)")
        
        return "\n".join(lines)

    def _generate_fix_kit(
        self,
        hotel_data: CanonicalAssessment,
        geo_assessment: GEOAssessment
    ) -> str:
        """Generate geo_fix_kit.md for FOUNDATION/CRITICAL bands."""
        lines = [
            "# GEO Fix Kit - Plan de Acción Completo",
            "",
            f"**Hotel:** {hotel_data.site_metadata.title}",
            f"**Score:** {geo_assessment.total_score}/100",
            f"**Banda:** {geo_assessment.band.value.upper()}",
            "",
            "## Archivos Generados",
            "",
            "Este kit incluye los siguientes archivos de enriquecimiento:",
            "",
            "| Archivo | Propósito |",
            "|---------|-----------|",
            "| `llms.txt` | Archivo para crawlers de IA (ChatGPT, Perplexity, Claude) |",
            "| `hotel_schema_rich.json` | Schema.org Hotel enriquecido con 16+ campos |",
            "| `faq_schema.json` | FAQ Schema para rich snippets |",
            "",
        ]
        
        if geo_assessment.gaps_blocking:
            lines.extend([
                "## Gaps Bloqueantes - Requieren Atención Inmediata",
                "",
            ])
            for gap in geo_assessment.gaps_blocking:
                lines.append(f"### {gap}")
                lines.append("")
                lines.append("_Acción requerida: Completa la implementación del componente mencionado._")
                lines.append("")
        
        if geo_assessment.gaps_mitigable:
            lines.extend([
                "## Gaps Mitigables - Mejoras Recomendadas",
                "",
            ])
            for gap in geo_assessment.gaps_mitigable[:5]:
                lines.append(f"- {gap}")
            lines.append("")
        
        lines.extend([
            "## Instrucciones de Implementación",
            "",
            "1. **Descarga** todos los archivos del directorio `geo_enriched/`",
            "2. **Revisa** cada archivo y personaliza según necesidad",
            "3. **Implementa** en tu CMS o hosting",
            "4. **Valida** con las herramientas de tu elección",
            "",
        ])
        
        return "\n".join(lines)

    def _generate_robots_fix(self, geo_assessment: GEOAssessment) -> str:
        """Generate robots_fix.txt with recommended robots.txt rules."""
        lines = [
            "# robots.txt - Recomendaciones de GEO",
            "",
            "# ===========================================================================",
            "# REGISTRO DE CAMBIOS",
            "# ===========================================================================",
            f"# Fecha: 2026-03-30",
            f"# Score GEO: {geo_assessment.total_score}/100",
            "",
            "# ===========================================================================",
            "# USER AGENTS",
            "# ===========================================================================",
            "",
            "# Permitir crawlers de IA principales",
            "User-agent: GPTBot",
            "Allow: /",
            "",
            "User-agent: ChatGPT-User",
            "Allow: /",
            "",
            "User-agent: Claude-Web",
            "Allow: /",
            "",
            "User-agent: Google-Extended",
            "Allow: /",
            "",
            "# ===========================================================================",
            "# SITEMAP",
            "# ===========================================================================",
            f"Sitemap: {geo_assessment.site_url}/sitemap.xml",
            "",
            "# ===========================================================================",
            "# RATE LIMITING (opcional)",
            "# ===========================================================================",
            "# Crawl-delay: 1",
            "",
        ]
        
        # Add any blocking gaps as comments
        if geo_assessment.gaps_blocking:
            lines.append("# ===========================================================================")
            lines.append("# GAPS BLOQUEANTES DETECTADOS")
            lines.append("# ===========================================================================")
            for gap in geo_assessment.gaps_blocking:
                lines.append(f"# ATENCION: {gap}")
            lines.append("")
        
        return "\n".join(lines)

    def _generate_seo_fix_kit(
        self,
        hotel_data: CanonicalAssessment,
        geo_assessment: GEOAssessment
    ) -> str:
        """Generate seo_fix_kit.md with comprehensive SEO fixes."""
        lines = [
            "# SEO Fix Kit - Intervención Crítica",
            "",
            f"**Hotel:** {hotel_data.site_metadata.title}",
            f"**Score GEO:** {geo_assessment.total_score}/100 (CRITICO)",
            "",
            "## Urgencia: ALTA",
            "",
            "Tu hotel tiene un score GEO crítico. Se requiere intervención inmediata",
            "para mejorar la visibilidad en motores de búsqueda AI-native.",
            "",
            "## Prioridades Inmediatas",
            "",
        ]
        
        # Map gaps to fix instructions
        gap_fixes = {
            "robots": ("## 1. Robots.txt", "Ver archivo robots_fix.txt en este directorio"),
            "llms": ("## 2. Archivo llms.txt", "Generar y subir llms.txt a la raíz del sitio"),
            "schema": ("## 3. Schema.org", "Implementar hotel_schema_rich.json en el sitio"),
            "meta": ("## 4. Meta Tags", "Actualizar meta tags según recomendaciones de diagnóstico"),
        }
        
        for area_key, (title, instruction) in gap_fixes.items():
            breakdown = geo_assessment.breakdown
            area_score = getattr(breakdown, area_key, 0)
            max_score = {"robots": 18, "llms": 18, "schema": 16, "meta": 14}.get(area_key, 10)
            
            if area_score < max_score * 0.5:  # Less than 50%
                lines.append(title)
                lines.append("")
                lines.append(f"- Score actual: {area_score}/{max_score}")
                lines.append(f"- {instruction}")
                lines.append("")
        
        lines.extend([
            "## Timeline Recomendado",
            "",
            "| Semana | Acción |",
            "|--------|--------|",
            "| 1 | Implementar robots.txt y llms.txt |",
            "| 2 | Enriquecer schema.org y meta tags |",
            "| 3 | Agregar FAQ schema y contenido citable |",
            "| 4 | Validar cambios con herramientas GEO |",
            "",
        ])
        
        return "\n".join(lines)

    def _generate_sync_report(
        self,
        hotel_data: CanonicalAssessment,
        geo_assessment: GEOAssessment,
        commercial_diagnosis: Dict[str, Any],
        sync_result: SyncResult
    ) -> str:
        """Generate sync_report.md for commercial + GEO sync analysis."""
        lines = [
            "# Sync Contract Report",
            "",
            "## Diagnóstico Comercial vs GEO",
            "",
            f"**Hotel:** {hotel_data.site_metadata.title}",
            f"**URL:** {hotel_data.url}",
            "",
            "---",
            "",
            "### Diagnóstico Comercial",
            "",
        ]
        
        # Commercial diagnosis summary
        perdida = commercial_diagnosis.get("perdida_mensual_total", 0)
        perdida_fmt = f"${perdida:,.0f} COP" if perdida > 0 else "No especificada"
        lines.append(f"- **Pérdida mensual:** {perdida_fmt}")
        lines.append(f"- **Paquete recomendado:** {commercial_diagnosis.get('paquete_recomendado', 'N/A')}")
        
        metricas = commercial_diagnosis.get("metricas_clave", {})
        if metricas:
            reservas = metricas.get("reservas_perdidas_mes", "N/A")
            reservas_rec = metricas.get("reservas_potenciales_recuperadas", "N/A")
            lines.append(f"- **Reservas perdidas/mes:** {reservas}")
            lines.append(f"- **Reservas recuperables:** {reservas_rec}")
        
        lines.extend([
            "",
            "### Diagnóstico GEO",
            "",
            f"- **Score GEO:** {geo_assessment.total_score}/100",
            f"- **Banda:** {geo_assessment.band.value.upper()}",
        ])
        
        if geo_assessment.gaps_blocking:
            lines.append("- **Gaps bloqueantes:**")
            for gap in geo_assessment.gaps_blocking[:3]:
                lines.append(f"  - {gap}")
        
        lines.extend([
            "",
            "---",
            "",
            "## Análisis de Consistencia",
            "",
            f"**Consistente:** {'✅ Sí' if sync_result.is_consistent else '❌ NO'}",
            f"**Combinación:** {sync_result.combination_tag}",
            f"**Sync Score:** {sync_result.sync_score:.2f}",
            "",
            "### Recomendación",
            "",
            sync_result.recommendation,
        ])
        
        if sync_result.contradiction_report:
            lines.extend([
                "",
                "### ⚠️ Contradicción Detectada",
                "",
                f"**Tipo:** {sync_result.contradiction_report.get('type', 'N/A')}",
                f"**Detalle:** {sync_result.contradiction_report.get('detail', 'N/A')}",
                f"**Acción requerida:** {sync_result.contradiction_report.get('action', 'N/A')}",
            ])
        
        lines.extend([
            "",
            "---",
            f"*Generado: {hotel_data.analyzed_at.strftime('%Y-%m-%d %H:%M')} UTC*",
        ])
        
        return "\n".join(lines)
