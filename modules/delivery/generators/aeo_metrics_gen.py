"""
Generador de reportes de métricas AEO.

Utiliza el template aeo_metrics_report.md para generar
reportes completos con datos de KPIs de AEO.
"""
import os
from datetime import datetime
from typing import Optional

from data_models.aeo_kpis import AEOKPIs, DataSource
from modules.analytics.profound_client import ProfoundClient
from modules.analytics.semrush_client import SemrushClient


def _render_bar(value: float, max_val: float = 100, width: int = 20) -> str:
    """Renderiza una barra ASCII para visualizar scores."""
    if value is None:
        return "[" + "?" * width + "]"
    filled = int((value / max_val) * width)
    return "[" + "=" * filled + " " * (width - filled) + "]"


def _render_sov_visualization(domain_sov: Optional[float], competitors: list) -> str:
    """Renderiza visualización de Share of Voice."""
    lines = []
    all_values = [domain_sov] if domain_sov else []
    all_values.extend([c.get("sov") for c in competitors if c.get("sov")])
    
    if not all_values:
        return "No data available"
    
    max_val = max(all_values) if all_values else 100
    lines.append(f"Max: {max_val:.1f}%")
    
    if domain_sov is not None:
        lines.append(f"You:  {domain_sov:.1f}% {_render_bar(domain_sov, max_val)}")
    
    for c in competitors:
        sov = c.get("sov")
        if sov is not None:
            lines.append(f"{c['domain'][:20]:20s}: {sov:.1f}% {_render_bar(sov, max_val)}")
    
    return "\n".join(lines)


def generate_aeo_metrics_report(
    hotel_name: str,
    url: str,
    aeo_kpis: Optional[AEOKPIs] = None,
    competitors: Optional[list[str]] = None,
    output_path: Optional[str] = None,
) -> str:
    """
    Genera un reporte de métricas AEO.
    
    Args:
        hotel_name: Nombre del hotel.
        url: URL del sitio web.
        aeo_kpis: Objeto AEOKPIs con métricas. Si es None, usa mock.
        competitors: Lista de dominios competidores para SoV.
        output_path: Ruta donde guardar el reporte. Si es None, retorna string.
        
    Returns:
        Contenido del reporte generado.
    """
    # Load template
    template_path = os.path.join(
        os.path.dirname(__file__), "aeo_metrics_report.md"
    )
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # Build context
    kpis = aeo_kpis or _build_mock_kpis(hotel_name, url, competitors)
    
    # Determine data source string
    source_map = {
        DataSource.PROFOUND_API: "Profound API",
        DataSource.SEMRUSH_API: "Semrush API",
        DataSource.GOOGLE_SEARCH_CONSOLE: "Google Search Console",
        DataSource.MOCK: "Mock Data (no API configured)",
    }
    data_source_str = source_map.get(kpis.data_source, "Unknown")

    # AI Visibility
    ai_vis_score = kpis.ai_visibility_score
    ai_vis_bar = _render_bar(ai_vis_score)
    ai_vis_trend = kpis.to_dict().get("ai_visibility_trend")
    ai_vis_insights = _get_ai_vis_insights(ai_vis_score)

    # Share of Voice
    sov_pct = kpis.share_of_voice
    comp_list = []
    if competitors:
        for c in competitors:
            comp_list.append({"domain": c, "sov": None})
    sov_viz = _render_sov_visualization(sov_pct, comp_list)

    # Citation Rate
    cit_rate = kpis.citation_rate
    cit_details = {
        "total_mentions": None,
        "citations_with_link": None,
    }

    # Voice Readiness
    vr = kpis.voice_readiness
    vr_score = vr.overall if vr else None
    vr_bar = _render_bar(vr_score)
    sq = vr.schema_quality if vr else None
    sc = vr.speakable_coverage if vr else None
    ft = vr.faq_tts_compliance if vr else None
    sd = vr.structured_data_score if vr else None

    # Composite Score
    composite = kpis.calculate_composite_score()

    # Status indicators
    def status(val, target, inverse: bool = False):
        if val is None:
            return "⚠️ No Data"
        if inverse:
            return "✅" if val < target else "🔴"
        return "✅" if val >= target else "⚠️"

    # Render template
    report = template
    replacements = {
        "{{HOTEL_NAME}}": hotel_name,
        "{{HOTEL_URL}}": url,
        "{{TIMESTAMP}}": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "{{DATA_SOURCE}}": data_source_str,
        "{{AI_VISIBILITY_SCORE}}": f"{ai_vis_score:.1f}" if ai_vis_score else "N/A",
        "{{AI_VISIBILITY_BAR}}": ai_vis_bar,
        "{{AI_VISIBILITY_TREND}}": ai_vis_trend or "",
        "{{AI_VISIBILITY_INSIGHTS}}": ai_vis_insights,
        "{{SOV_PERCENTAGE}}": f"{sov_pct:.1f}" if sov_pct else "N/A",
        "{{COMPETITORS}}": "\n".join([f"| {c['domain']} | {{sov}}% |" for c in comp_list]) or "| - | N/A |",
        "{{SOV_VISUALIZATION}}": sov_viz,
        "{{CITATION_RATE}}": f"{cit_rate:.1f}" if cit_rate else "N/A",
        "{{CITATION_DETAILS}}": str(cit_details),
        "{{VOICE_READINESS}}": f"{vr_score:.1f}" if vr_score else "N/A",
        "{{VOICE_READINESS_BAR}}": vr_bar,
        "{{SCHEMA_QUALITY}}": f"{sq:.1f}" if sq else "N/A",
        "{{SPEAKABLE_COVERAGE}}": f"{sc:.1f}" if sc else "N/A",
        "{{FAQ_TTS_COMPLIANCE}}": f"{ft:.1f}" if ft else "N/A",
        "{{STRUCTURED_DATA}}": f"{sd:.1f}" if sd else "N/A",
        "{{COMPOSITE_SCORE}}": f"{composite:.1f}" if composite >= 0 else "N/A",
        "{{STATUS_AI_VISIBILITY}}": status(ai_vis_score, 70),
        "{{STATUS_SOV}}": status(sov_pct, 25),
        "{{STATUS_CITATION}}": status(cit_rate, 60),
        "{{STATUS_VOICE_READINESS}}": status(vr_score, 80),
        "{{STATUS_COMPOSITE}}": status(composite, 75),
        "{{COMPETITORS_ANALYZED}}": str(kpis.competitors_analyzed),
        "{{COMPETITOR_AVG_VISIBILITY}}": f"{kpis.competitor_avg_viscosity:.1f}" if kpis.competitor_avg_viscosity else "N/A",
        "{{GAP_ANALYSIS}}": "Configure API keys for competitor analysis",
        "{{RECOMMENDATIONS}}": _get_recommendations(kpis),
        "{{NEXT_STEP_1}}": "Configure Profound API key for real AI Visibility data",
        "{{NEXT_STEP_2}}": "Add competitor domains for Share of Voice analysis",
        "{{NEXT_STEP_3}}": "Monitor Voice Readiness improvements",
        "{{VERSION}}": kpis.version,
        "{{IS_MOCK}}": str(kpis.data_source == DataSource.MOCK).lower(),
    }

    for key, val in replacements.items():
        report = report.replace(key, str(val))

    # Cleanup empty conditionals (simple approach)
    report = report.replace("{{#if DATA_SOURCE}}\n{{/if}}\n", "")
    
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
    
    return report


def _build_mock_kpis(hotel_name: str, url: str, competitors: list[str] = None) -> AEOKPIs:
    """Builds a mock AEOKPIs object for testing/demo."""
    from data_models.aeo_kpis import VoiceReadinessScore
    
    vr = VoiceReadinessScore(
        schema_quality=75.0,
        speakable_coverage=60.0,
        faq_tts_compliance=80.0,
        structured_data_score=70.0,
    )
    
    return AEOKPIs(
        hotel_name=hotel_name,
        url=url,
        ai_visibility_score=None,  # Requires Profound API
        share_of_voice=None,  # Requires Profound API
        citation_rate=None,  # Requires Profound API
        voice_search_impressions=None,  # Not measurable
        voice_readiness=vr,
        competitors_analyzed=len(competitors) if competitors else 0,
        competitor_avg_viscosity=None,
        data_source=DataSource.MOCK,
    )


def _get_ai_vis_insights(score: Optional[float]) -> str:
    """Genera insights basados en AI Visibility Score."""
    if score is None:
        return "AI Visibility Score requires API configuration. Configure PROFOUND_API_KEY for real data."
    if score >= 80:
        return "Excellent AI visibility. Your hotel is well-represented in AI-generated responses."
    elif score >= 60:
        return "Good AI visibility. Consider optimizing for specific queries to improve further."
    elif score >= 40:
        return "Moderate AI visibility. Focus on FAQ content and structured data improvements."
    else:
        return "Low AI visibility. Prioritize Schema markup, FAQ TTS content, and voice search optimization."


def _get_recommendations(kpis: AEOKPIs) -> str:
    """Genera recomendaciones basadas en KPIs disponibles."""
    recs = []
    
    if kpis.ai_visibility_score is None or kpis.ai_visibility_score < 60:
        recs.append("- Configure Profound API to measure AI Visibility")
    
    if kpis.share_of_voice is None or kpis.share_of_voice < 25:
        recs.append("- Implement FAQ schema with TTS-optimized answers for better AI citation")
    
    if kpis.voice_readiness:
        vr = kpis.voice_readiness
        if vr.speakable_coverage < 70:
            recs.append("- Increase speakable content coverage using SpeakableSpecification")
        if vr.faq_tts_compliance < 75:
            recs.append("- Optimize FAQ answers for text-to-speech (40-60 words per FAQ)")
    
    if not recs:
        recs.append("- Continue monitoring AEO metrics weekly")
    
    return "\n".join(recs) if recs else "- Maintain current optimization efforts"
