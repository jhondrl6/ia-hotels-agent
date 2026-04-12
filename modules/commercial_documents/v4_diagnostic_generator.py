"""
V4 Diagnostic Document Generator.

Generates the 01_DIAGNOSTICO_Y_OPORTUNIDAD.md document based on
v4.0 audit results with confidence-based validation.
"""

import copy
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from string import Template

from .data_structures import (
    V4AuditResult,
    ValidationSummary,
    FinancialScenarios,
    ConfidenceLevel,
    confidence_to_icon,
    confidence_to_label,
    format_cop,
    extract_top_problems,
)

from data_models.analytics_status import AnalyticsStatus


def _get_opportunity_scorer():
    """Lazy import del OpportunityScorer para evitar import circular."""
    try:
        from modules.financial_engine.opportunity_scorer import OpportunityScorer
        return OpportunityScorer()
    except Exception:
        return None

# Analytics imports (lazy-loaded to avoid hard dependency on google-analytics-data)
# Used by _get_analytics_summary() and _get_analytics_fallback()


# ============================================================
# ELEMENTO_KB_TO_PAIN_ID — ÚNICA FUENTE DE VERDAD
# Conecta cada elemento del CHECKLIST_IAO (KB) con su pain_id
# y el asset que lo resuelve.
# Sincronizar con:
#   - PainSolutionMapper.PAIN_SOLUTION_MAP
#   - ASSET_CATALOG
# ============================================================

ELEMENTO_KB_TO_PAIN_ID: Dict[str, tuple] = {
    # Elemento KB: (pain_id, asset_principal, asset_secundario)
    # CORREGIDO v3: schema_reviews → no_schema_reviews (no missing_reviews)
    "ssl":                ("no_ssl",              "ssl_guide",           None),
    "schema_hotel":      ("no_hotel_schema",     "hotel_schema",        None),
    "schema_reviews":     ("no_schema_reviews",   "hotel_schema",        None),
    "LCP_ok":             ("poor_performance",    "performance_audit",   "optimization_guide"),
    "CLS_ok":             ("poor_performance",    "optimization_guide",  None),
    "contenido_extenso":  ("low_citability",      "optimization_guide",  None),
    "open_graph":         ("no_og_tags",          "og_tags_guide",       None),
    "schema_faq":         ("no_faq_schema",       "faq_page",            None),
    "nap_consistente":    ("whatsapp_conflict",   "whatsapp_button",     None),
    "imagenes_alt":       ("missing_alt_text",    "alt_text_guide",      None),
    "blog_activo":        ("no_blog_content",     "blog_strategy_guide", None),
    "redes_activas":      ("no_social_links",     "social_strategy_guide", None),
    # Nuevos elementos (FASE-A: 4-pilar scoring)
    "speakable_schema":   ("no_speakable",        "voice_guide",         None),
    "llms_txt_exists":    ("no_llms_txt",         "llms_txt",            None),
    "crawler_access":     ("ia_crawler_blocked",  "optimization_guide",  None),
    "brand_signals":      ("weak_brand_signals",  "org_schema",          None),
    "schema_advanced":    ("no_entity_schema",    "org_schema",          None),
    "contenido_factual":  ("no_factual_data",     "hotel_schema",        None),
}

ELEMENTOS_MONETIZABLES: set = {
    elem for elem, (_, asset, _) in ELEMENTO_KB_TO_PAIN_ID.items()
    if asset is not None
}


# ============================================================
# 4-PILAR CHECKLISTS (FASE-A)
# Reemplazan el CHECKLIST_IAO monolico por 4 pilares coherentes.
# Cada diccionario suma exactamente 100pts.
# ============================================================

CHECKLIST_SEO: Dict[str, int] = {
    "ssl":              15,
    "schema_hotel":     20,  # Schema base = SEO fundamental
    "LCP_ok":           20,
    "CLS_ok":           10,
    "imagenes_alt":     15,
    "blog_activo":      10,
    "schema_reviews":   10,  # Reviews en schema = credibility SEO
}
# Total: 100pts

CHECKLIST_GEO: Dict[str, int] = {
    "nap_consistente":      15,
    "redes_activas":        10,
    "geo_score_gbp":        30,  # Ya existe: audit_result.gbp.geo_score
    "fotos_gbp":            15,  # Ya existe: audit_result.gbp.photos
    "horario_gbp":          15,  # Ya existe: audit_result.gbp (check horarios)
    "schema_reviews_geo":   15,  # Reviews con ubicacion
}
# Total: 100pts

CHECKLIST_AEO: Dict[str, int] = {
    "schema_faq":           25,  # FAQ = fuente directa para snippets
    "open_graph":           15,  # OG = metadatos para posicion cero
    "schema_hotel_aeo":     15,  # Schema detallado para extraccion factual
    "contenido_factual":    20,  # Horarios, precios, servicios accesibles
    "speakable_schema":     10,  # Schema especifico voz (nuevo campo, default False)
    "imagenes_alt_aeo":     15,  # Alt text como fuente para image snippets
}
# Total: 100pts

CHECKLIST_IAO: Dict[str, int] = {
    "citability_score":     20,  # Ya existe: audit_result.citability.overall_score
    "contenido_extenso":    15,  # Ya existe como elemento KB
    "llms_txt_exists":      15,  # Nuevo: check si llms.txt generado
    "crawler_access":       15,  # Ya existe: ai_crawler_auditor
    "brand_signals":        10,  # Nuevo: SameAs, enlaces sociales
    "ga4_indirect":         10,  # Ya existe (ADVISORY): GA4 indirect traffic
    "schema_advanced":      15,  # Schema Entity + SameAs (nuevo campo)
}
# Total: 100pts


def calcular_score_seo(elementos: dict) -> int:
    """Score SEO: Para que te ENCUENTREN (0-100)."""
    if not elementos:
        return 0
    return min(100, sum(CHECKLIST_SEO[k] for k, v in elementos.items() if v is True and k in CHECKLIST_SEO))


def calcular_score_geo(elementos: dict) -> int:
    """Score GEO: Para que te UBICQUEN (0-100)."""
    if not elementos:
        return 0
    return min(100, sum(CHECKLIST_GEO[k] for k, v in elementos.items() if v is True and k in CHECKLIST_GEO))


def calcular_score_aeo(elementos: dict) -> int:
    """Score AEO: Para que te CITEN (0-100)."""
    if not elementos:
        return 0
    return min(100, sum(CHECKLIST_AEO[k] for k, v in elementos.items() if v is True and k in CHECKLIST_AEO))


def calcular_score_iao(elementos: dict) -> int:
    """Score IAO: Para que te RECOMIENDEN (0-100)."""
    if not elementos:
        return 0
    return min(100, sum(CHECKLIST_IAO[k] for k, v in elementos.items() if v is True and k in CHECKLIST_IAO))


def calcular_score_global(seo: int, geo: int, aeo: int, iao: int) -> int:
    """Visibilidad Digital = promedio ponderado 4 pilares (0-100)."""
    return int((seo * 0.25) + (geo * 0.25) + (aeo * 0.25) + (iao * 0.25))


def calcular_cumplimiento(elementos: dict) -> int:
    """
    DEPRECATED: Usar calcular_score_global(calcular_score_seo(...), ...) en su lugar.
    Calcula score de cumplimiento del CHECKLIST_IAO (0-100).
    DE LA KB: [SECTION:SCORING_ALGORITHM]

    Args:
        elementos: Dict con 12 elementos KB, cada uno True/False.
                   Usar _extraer_elementos_de_audit() para obtener.

    Returns:
        int 0-100. Si elementos esta vacio o es None, retorna 0.
    """
    if not elementos:
        return 0
    
    pesos = {
        "ssl":               10,
        "schema_hotel":      15,
        "schema_reviews":    15,
        "LCP_ok":            10,
        "CLS_ok":             5,
        "contenido_extenso": 10,
        "open_graph":         5,
        "schema_faq":         8,
        "nap_consistente":    7,
        "imagenes_alt":       5,
        "blog_activo":        5,
        "redes_activas":      5,
    }
    
    score = sum(
        pesos[k] for k, v in elementos.items()
        if v is True and k in pesos
    )
    return min(score, 100)


def sugerir_paquete(score_tecnico: int) -> str:
    """
    Recomienda paquete segun score (tecnico o global).
    DE LA KB: [SECTION:PACKAGE_TIERS]

    Args:
        score_tecnico: Score 0-100. Acepta calcular_cumplimiento() (legacy)
                      o calcular_score_global() (4-pilar).

    Returns:
        "basico" (<40), "avanzado" (40-69), "premium" (>=70)
    """
    if score_tecnico < 40:
        return "basico"
    elif score_tecnico < 70:
        return "avanzado"
    else:
        return "premium"

class V4DiagnosticGenerator:
    """
    Generates diagnostic documents for hotel audits.
    
    Creates a comprehensive diagnostic report with:
    - Validated data table with confidence levels
    - Certified financial impact with scenarios
    - Identified problems categorized by solution availability
    - Top 3 critical problems
    - Quick wins for 30 days
    
    Usage:
        generator = V4DiagnosticGenerator()
        path = generator.generate(
            audit_result=audit_result,
            validation_summary=validation_summary,
            financial_scenarios=scenarios,
            hotel_name="Hotel Visperas",
            hotel_url="https://hotelvisperas.com",
            output_dir="output/"
        )
    """
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize the diagnostic generator.
        
        Args:
            template_dir: Directory containing templates. If None, uses default.
        """
        if template_dir is None:
            template_dir = Path(__file__).parent / "templates"
        self.template_dir = Path(template_dir)
        # Prefer V6 template, fall back to V4
        self.template_path = self.template_dir / "diagnostico_v6_template.md"
        if not self.template_path.exists():
            self.template_path = self.template_dir / "diagnostico_v4_template.md"
        
        # Transparencia de datos analytics (default: True)
        # Si True, agrega seccion "Fuentes de Datos Usadas en Este Diagnostico"
        # cuando alguna fuente (GA4/Profound/Semrush) no esta disponible.
        self.show_analytics_transparency = True 
    
    def generate(
        self,
        audit_result: V4AuditResult,
        validation_summary: ValidationSummary,
        financial_scenarios: FinancialScenarios,
        hotel_name: str,
        hotel_url: str,
        output_dir: str,
        coherence_score: Optional[float] = None,
        region: Optional[str] = None,
        analytics_data: Optional[Dict[str, Any]] = None,
        financial_breakdown: Optional['FinancialBreakdown'] = None,
    ) -> str:
        """
        Generate the diagnostic document.
        
        Args:
            audit_result: Complete v4.0 audit results
            validation_summary: Summary of data validation
            financial_scenarios: Financial scenarios (conservative/realistic/optimistic)
            hotel_name: Name of the hotel
            hotel_url: Hotel website URL
            output_dir: Directory to save the document
            coherence_score: Optional pre-calculated coherence score from coherence gate.
                              If provided, uses this value instead of calculating internally.
            region: Optional region string for regional context in templates.
            analytics_data: Optional dict with analytics configuration. Can contain:
                - use_ga4: bool (true para usar GA4 real, False para usar estimados)
                - hotel_data: dict adicional para IATester integration
                
        Returns:
            Path to the generated document
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Reset brechas cache per generate() call (FASE-H)
        self._cached_brechas = None

        # Load template
        template_content = self._load_template()
        
        # Prepare template data (passes analytics_data through)
        template_data = self._prepare_template_data(
            audit_result=audit_result,
            validation_summary=validation_summary,
            financial_scenarios=financial_scenarios,
            hotel_name=hotel_name,
            hotel_url=hotel_url,
            coherence_score=coherence_score,
            region=region,
            analytics_data=analytics_data,
        )
        
        # Render template
        document_content = self._render_template(template_content, template_data)
        
        # Save document
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"01_DIAGNOSTICO_Y_OPORTUNIDAD_{timestamp}.md"
        file_path = output_path / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(document_content)
        
        return str(file_path)
    
    def _load_template(self) -> str:
        """Load the diagnostic template."""
        if self.template_path.exists():
            with open(self.template_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Return default template if file doesn't exist
            return self._get_default_template()
    
    def _get_default_template(self) -> str:
        """Get the default template content."""
        return """---
generated_at: ${generated_at}
version: ${version}
hotel_id: ${hotel_id}
coherence_score: ${coherence_score}
document_type: DIAGNOSTICO_V4
generator: IA_Hoteles_v4
---

# 📊 DIAGNÓSTICO Y OPORTUNIDAD
## ${hotel_name}

**URL:** ${hotel_url}  
**Fecha de generación:** ${generated_at}  
**Versión del sistema:** ${version}  
**Coherence Score:** ${coherence_score}%

---

## 📍 PARTE 1: ¿QUÉ ESTÁ PASANDO EN EL EJE CAFETERO?

### El Cambio en la Industria Hotelera (2024-2025)
**Antes:** Huésped busca en Google → Click en web → Reserva  
**Ahora:** Huésped pregunta a ChatGPT → **Si no está, pierde la reserva**

### Los Nuevos "Gerentes Digitales"
1. **ChatGPT** → 65% de viajeros jóvenes
2. **Google Maps** → 73% de búsquedas "cerca de mí"
3. **Perplexity, Gemini** → Crecimiento 300%

---

## [CERTIFIED] DATOS VALIDADOS

Los siguientes datos han sido validados cruzando múltiples fuentes (Web, Google Business Profile, Input del hotelero, Benchmarks regionales):

| Dato | Valor | Confianza | Fuentes |
|------|-------|-----------|---------|
${validated_data_table}

**Leyenda de Confianza:**
- 🟢 **VERIFIED**: 2+ fuentes coinciden (≥90% match)
- 🟡 **ESTIMATED**: 1 fuente disponible o discrepancia menor
- 🔴 **CONFLICT**: Fuentes contradicen - requiere revisión

---

## 📊 SU POSICIÓN HOY vs PROMEDIO REGIONAL

| Indicador | Su Hotel | Promedio Regional | Estado |
|-----------|----------|-------------------|--------|
| Visibilidad Google Maps (GEO) | ${geo_score}/100 | ${geo_regional_avg}/100 | ${geo_status} |
| Posicion Competitiva (vs cercanos) | ${activity_score}/100 | ${competitive_regional_avg}/100 | ${activity_status} |
| Web Score (SEO) | ${web_score}/100 | ${seo_regional_avg}/100 | ${web_status} |
| Infraestructura AEO (Schema) | ${aeo_score}/100 | ${aeo_regional_avg}/100 | ${aeo_status} |

---

## [TARGET] IMPACTO FINANCIERO CERTIFICADO

### ${empathy_message}

<div style="background: #f0f8ff; padding: 20px; border-radius: 8px; border-left: 4px solid #0066cc;">

### 💰 Pérdida Mensual Estimada (Escenario Realista)

**${main_scenario_amount}**

*${main_scenario_description}*

**Probabilidad:** 20% | **Confianza:** ${main_confidence}%

</div>

> ✅ **Label:** Escenario más probable basado en datos validados

<details>
<summary>📋 Ver Anexo Técnico con Todos los Escenarios</summary>

### Escenario Conservador (70% probabilidad)
- **Rango:** ${conservative_range}
- **Descripción:** ${conservative_description}
- **Supuestos:**
${conservative_assumptions}

### Escenario Realista (20% probabilidad) - PRINCIPAL
- **Rango:** ${realistic_range}
- **Descripción:** ${realistic_description}
- **Supuestos:**
${realistic_assumptions}

### Escenario Optimista (10% probabilidad)
- **Rango:** ${optimistic_range}
- **Descripción:** ${optimistic_description}
- **Supuestos:**
${optimistic_assumptions}

</details>

---

## [ALERT] PROBLEMAS IDENTIFICADOS

### Con Solución Inmediata (Assets Automáticos)

Estos problemas tienen solución mediante assets generados automáticamente:

| Problema | Severidad | Asset Generado | Confianza |
|----------|-----------|----------------|-----------|
${solvable_problems_table}

### Requieren Atención (Sin Asset Automático)

Estos problemas requieren acción manual o decisión del hotelero:

| Problema | Severidad | Recomendación |
|----------|-----------|---------------|
${manual_attention_table}

---

## 🚨 BRECHAS CRÍTICAS IDENTIFICADAS

${brechas_section}

---

## [OK] QUICK WINS (30 DÍAS)

Acciones de alto impacto que pueden implementarse en los próximos 30 días:

${quick_wins_list}

---

## 📋 RESUMEN DE VALIDACIÓN

- **Datos Validados:** ${validated_count}
- **Conflictos Detectados:** ${conflicts_count}
- **Nivel de Confianza Global:** ${overall_confidence}

---

*Documento generado por IA Hoteles v4.0 - Sistema de Confianza*  
*Validación cruzada: Web + GBP + Input + Benchmarks*
"""
    
    def _prepare_template_data(
        self,
        audit_result: V4AuditResult,
        validation_summary: ValidationSummary,
        financial_scenarios: FinancialScenarios,
        hotel_name: str,
        hotel_url: str,
        coherence_score: Optional[float] = None,
        region: Optional[str] = None,
        analytics_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """Prepare data for template rendering."""
        
        # Basic metadata
        hotel_id = hotel_name.lower().replace(" ", "_").replace("-", "_")
        # Use provided coherence_score from coherence gate, or calculate internally
        if coherence_score is None:
            coherence_score = self._calculate_coherence_score(validation_summary)
        
        # Region-based variables for V6 templates
        _raw = region or "Colombia"
        if _raw.lower() in ("nacional", "general", "default", "unknown"):
            hotel_region = "Colombia"
        else:
            hotel_region = _raw.replace("_", " ").title()
        hotel_location = getattr(audit_result, 'location', None) or \
                        getattr(getattr(audit_result, 'gbp', None), 'address', None) or \
                        hotel_region
        hotel_landmark = f"zona de {hotel_region}" if hotel_region else "zona turística"
        regional_context = self._build_regional_context(hotel_region)
        
        # Validated data table
        validated_data_table = self._build_validated_data_table(validation_summary, audit_result)
        
        # Empathy message
        empathy_message = self._build_empathy_message(financial_scenarios, hotel_name)
        
        # Scenarios
        main_scenario = financial_scenarios.get_main_scenario()
        
        # Additional variables for the sales template
        # Extract year from generated_at or use current year
        year = datetime.now().year
        prev_year = year - 1
        
        # Calculate 6-month projection using central value (not max)
        base_value = getattr(main_scenario, 'monthly_loss_central', None) or main_scenario.monthly_loss_max
        loss_6_months_value = base_value * 6
        
        # Plan variables - for now, we set them based on quick wins or default values
        # In a real implementation, these would be derived from audit results and strategy
        plan_7d = "Revisar y optimizar Google Business Profile"
        plan_30d = "Implementar quick wins identificados y comenzar plan de contenido"
        plan_60d = "Desarrollar presencia en asistentes de IA y monitorear resultados"
        plan_90d = "Consolidar estrategia de IA y evaluar retorno de inversión"
        
        # Regional averages (3-tier fallback: competitors > regional config > default)
        # Computed here so both template sections can reference them
        geo_regional = self._calculate_regional_average(audit_result, 'geo', hotel_region)
        competitive_regional = self._calculate_regional_average(audit_result, 'competitive', hotel_region)
        seo_regional = self._calculate_regional_average(audit_result, 'seo', hotel_region)
        aeo_regional = self._calculate_regional_average(audit_result, 'aeo', hotel_region)
        
        data = {
            'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'version': '4.0.0',
            'hotel_id': hotel_id,
            'coherence_score': str(coherence_score),
            'hotel_name': hotel_name,
            'hotel_url': hotel_url,
            
            # Validated data
            'validated_data_table': validated_data_table,
            
            # Financial impact
            'empathy_message': empathy_message,
            'main_scenario_amount': main_scenario.format_loss_cop(),
            'main_scenario_description': main_scenario.description,
            'main_confidence': str(int(main_scenario.confidence_score * 100)),
            
            # All scenarios
            'conservative_range': f"{format_cop(financial_scenarios.conservative.monthly_loss_min)} - {format_cop(financial_scenarios.conservative.monthly_loss_max)}",
            'conservative_description': financial_scenarios.conservative.description,
            'conservative_assumptions': self._format_list(financial_scenarios.conservative.assumptions),
            
            'realistic_range': f"{format_cop(financial_scenarios.realistic.monthly_loss_min)} - {format_cop(financial_scenarios.realistic.monthly_loss_max)}",
            'realistic_description': financial_scenarios.realistic.description,
            'realistic_assumptions': self._format_list(financial_scenarios.realistic.assumptions),
            
            'optimistic_range': f"{format_cop(financial_scenarios.optimistic.monthly_loss_min)} - {format_cop(financial_scenarios.optimistic.monthly_loss_max)}",
            'optimistic_description': financial_scenarios.optimistic.description,
            'optimistic_assumptions': self._format_list(financial_scenarios.optimistic.assumptions),
            
            # Problems
            'solvable_problems_table': self._build_solvable_problems_table(audit_result),
            'manual_attention_table': self._build_manual_attention_table(audit_result),
            'top_critical_problems': self._build_top_critical_problems(audit_result),
            'quick_wins_list': self._build_quick_wins(audit_result),
            'geo_table': self._build_geo_problems_table(audit_result),
            
            # Regional averages (3-tier fallback: competitors > regional config > default)
            'geo_regional': geo_regional,
            'competitive_regional': competitive_regional,
            'seo_regional': seo_regional,
            'aeo_regional': aeo_regional,
            
            # 4 Pilares Scores (using dynamic regional benchmarks)
            'geo_score': (geo_sc := self._calculate_geo_score(audit_result)),
            'geo_status': self._get_score_status(geo_sc, geo_regional['value']),
            'activity_score': (act_sc := self._calculate_competitive_score(audit_result)),
            'activity_status': self._get_score_status(act_sc, competitive_regional['value']),
            'web_score': (web_sc := self._calculate_web_score(audit_result)),
            'web_status': self._get_score_status(web_sc, seo_regional['value']),
            'schema_infra_score': (aeo_sc := self._calculate_aeo_score(audit_result)),
            'schema_infra_status': self._get_score_status(aeo_sc, aeo_regional['value']),

            # === 4-PILAR SCORING (FASE-A) ===
            'iao_score': (iao_sc := self._calculate_iao_score_from_audit(audit_result)),
            'iao_status': self._get_score_status(iao_sc, 50),  # Regional default 50 (sin benchmarks IAO)
            'iao_regional_avg': '50',
            'score_global': (sg_sc := self._calculate_score_global_from_audit(audit_result)),
            'score_global_status': self._get_score_status(sg_sc, 50),
            
            # Brechas (4 Razones)
            'brecha_1_nombre': self._get_brecha_nombre(audit_result, 0),
            'brecha_1_costo': self._get_brecha_costo(audit_result, financial_scenarios, 0),
            'brecha_1_detalle': self._get_brecha_detalle(audit_result, 0),
            'brecha_2_nombre': self._get_brecha_nombre(audit_result, 1),
            'brecha_2_costo': self._get_brecha_costo(audit_result, financial_scenarios, 1),
            'brecha_2_detalle': self._get_brecha_detalle(audit_result, 1),
            'brecha_3_nombre': self._get_brecha_nombre(audit_result, 2),
            'brecha_3_costo': self._get_brecha_costo(audit_result, financial_scenarios, 2),
            'brecha_3_detalle': self._get_brecha_detalle(audit_result, 2),
            'brecha_4_nombre': self._get_brecha_nombre(audit_result, 3),
            'brecha_4_costo': self._get_brecha_costo(audit_result, financial_scenarios, 3),
            'brecha_4_detalle': self._get_brecha_detalle(audit_result, 3),

            # Brechas dinamicas (N brechas, no fijo 4) - fuente de verdad para templates V6
            'brechas_section': self._build_brechas_section(audit_result, financial_scenarios),
            'brechas_resumen_section': self._build_brechas_resumen_section(audit_result, financial_scenarios),



            # Additional variables for sales template
            'year': str(year),
            'prev_year': str(prev_year),
            'loss_6_months': format_cop(loss_6_months_value),
            'plan_7d': plan_7d,
            'plan_30d': plan_30d,
            'plan_60d': plan_60d,
            'plan_90d': plan_90d,
            
            # Summary
            'validated_count': str(len(validation_summary.fields)),
            'conflicts_count': str(len(validation_summary.conflicts)),
            'overall_confidence': confidence_to_label(validation_summary.overall_confidence),
            
            # V6 template variables (regional context and aliases)
            'hotel_location': hotel_location,
            'hotel_region': hotel_region,
            'hotel_landmark': hotel_landmark,
            'regional_context': regional_context,
            'monthly_loss': format_cop(base_value),
            'urgencia_contenido': self._build_urgencia_content(financial_scenarios, hotel_name),
            'quick_wins_content': self._build_quick_wins_content(audit_result),
            
            # V6 Score aliases (competitive = activity, SEO = web, AEO = schema_infra)
            'competitive_score': self._calculate_competitive_score(audit_result),
            'competitive_status': self._get_score_status(self._calculate_competitive_score(audit_result), competitive_regional['value']),
            'seo_score': self._calculate_web_score(audit_result),
            'seo_status': self._get_score_status(self._calculate_web_score(audit_result), seo_regional['value']),
            'aeo_score': self._calculate_aeo_score(audit_result),
            'aeo_status': self._get_score_status(self._calculate_aeo_score(audit_result), aeo_regional['value']),
            
            # Regional average display values
            'geo_regional_avg': str(geo_regional['value']),
            'competitive_regional_avg': str(competitive_regional['value']),
            'seo_regional_avg': str(seo_regional['value']),
            'aeo_regional_avg': str(aeo_regional['value']),
            'regional_transparency': self._build_regional_transparency(
                geo_regional, competitive_regional, seo_regional, aeo_regional
            ),
            
            # Brecha impactos y resúmenes
            'brecha_1_impacto': self._get_brecha_impacto(audit_result, 0),
            'brecha_2_impacto': self._get_brecha_impacto(audit_result, 1),
            'brecha_3_impacto': self._get_brecha_impacto(audit_result, 2),
            'brecha_4_impacto': self._get_brecha_impacto(audit_result, 3),
            'brecha_1_resumen': self._get_brecha_resumen(audit_result, 0),
            'brecha_2_resumen': self._get_brecha_resumen(audit_result, 1),
            'brecha_3_resumen': self._get_brecha_resumen(audit_result, 2),
            'brecha_4_resumen': self._get_brecha_resumen(audit_result, 3),

            # Brecha recuperaciones (valores numericos para template V6)
            'brecha_1_recuperacion': self._get_brecha_recuperacion(audit_result, financial_scenarios, 0),
            'brecha_2_recuperacion': self._get_brecha_recuperacion(audit_result, financial_scenarios, 1),
            'brecha_3_recuperacion': self._get_brecha_recuperacion(audit_result, financial_scenarios, 2),
        }

        # --- FASE-C: Opportunity Scores injection ---
        score_vars = self._inject_brecha_scores(audit_result, financial_scenarios)
        # Only override if scores are available (non-empty string or value)
        data.update(score_vars)
        
        # --- Analytics integration (GA4 / fallback) ---
        analytics_vars = self._inject_analytics(audit_result, analytics_data)
        data.update(analytics_vars)
        
        # --- Analytics status (transparency de datos) ---
        ga4_property_id = analytics_data.get("ga4_property_id") if analytics_data else None
        analytics_status = self._check_analytics_status(ga4_property_id=ga4_property_id, hotel_url=hotel_url)
        
        # Texto resumen legible para el diagnostico
        data['analytics_missing_credentials'] = ', '.join(analytics_status.missing_credentials()) or 'Ninguna'
        
        # Per-source status fragments
        data['ga4_status_text'] = analytics_status.ga4_status_for_template()
        data['profound_status_text'] = analytics_status.profound_status_for_template()
        data['semrush_status_text'] = analytics_status.semrush_status_for_template()
        data['gsc_status_text'] = analytics_status.gsc_status_for_template()
        
        # Seccion opcional de transparencia de datos
        data['analytics_transparency_section'] = self._build_transparency_section(analytics_status)
        
        # --- Financial Placeholders (FASE-F: Comisión OTA + Evidence Tiers) ---
        # FASE-J: pass source_reliability from analytics_data if available
        _source_reliability = "verified"
        if analytics_data and isinstance(analytics_data, dict):
            _source_reliability = analytics_data.get("source_reliability", "verified")
        financial_ph = self._build_financial_placeholders(
            financial_scenarios, analytics_data, source_reliability=_source_reliability,
        )
        data.update(financial_ph)
        
        return data
    
    def _inject_analytics(self, audit_result: V4AuditResult, analytics_data: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Construye variables de template relacionadas con analytics.
        
        Logica:
        1. Si analytics_data tiene use_ga4=True -> intenta _get_analytics_summary() (GA4 real)
        2. Si no -> usa _get_analytics_fallback() basado en senales del audit
        
        RETORNA:
            dict con: aeo_data_source, analytics_summary_text, analytics_footnote
        """
        ga4_enabled = analytics_data is not None and analytics_data.get("use_ga4", False)
        ga4_property_id = analytics_data.get("ga4_property_id") if analytics_data else None
        
        if ga4_enabled:
            summary = self._get_analytics_summary(ga4_property_id=ga4_property_id)
            data_source = summary.get("data_source", "N/A")
            
            # Si GA4 realmente respondio, usarlo; de lo contrario caer a fallback
            if data_source == "GA4":
                return {
                    "aeo_data_source": "GA4",
                    "analytics_summary_text": summary.get("summary_text", "Sin datos de GA4."),
                    "analytics_footnote": "* Nota: Visibilidad en IA basada en datos reales de Google Analytics 4.",
                }
        
        # Fallback: estimado cualitativo basado en audit
        fallback = self._get_analytics_fallback(audit_result)
        
        return {
            "aeo_data_source": "estimado",
            "analytics_summary_text": fallback.get("summary_text", "Visibilidad en IA no evaluada."),
            "analytics_footnote": "* Nota: Visibilidad en IA basada en estimado cualitativo (sin medicion directa). Para medicion en tiempo real, configurar GA4.",
        }

    def _build_transparency_section(self, analytics_status: AnalyticsStatus) -> str:
        """
        Construye la seccion opcional 'Fuentes de Datos Usadas en Este Diagnostico'.

        Solo aparece cuando ALGUNA fuente no esta disponible.
        Si todas las fuentes estan conectadas, retorna string vacio (el template
        no lo renderiza).
        """
        if not self.show_analytics_transparency:
            return ""

        if not analytics_status.is_any_missing():
            # Todo conectado: no mostrar la seccion
            return ""

        ga4 = analytics_status.ga4_status_for_template()
        gsc = analytics_status.gsc_status_for_template()

        # Construir lista de fuentes con solo las que tienen estado
        sources = []
        sources.append(f"- **Google Analytics 4**: {ga4}")
        sources.append(f"- **Google Search Console**: {gsc}")
        sources.append("- **Audit Web (schema, metadatos, contenido)**: ✅ Disponible")
        sources.append("- **Google Places / GBP**: ✅ Disponible")

        # Solo mostrar nota si alguna fuente real falta
        has_missing = not analytics_status.ga4_available or not analytics_status.gsc_available
        note = ""
        if has_missing:
            note = "\n> *Nota: Las fuentes marcadas como no configuradas requieren credenciales API.\n> Los valores mostrados provienen del análisis web, Places API y estimaciones cualitativas.*"

        section = f"""### Fuentes de Datos Usadas en Este Diagnostico

{chr(10).join(sources)}
{note}
"""
        return section
    
    def _build_scenario_table_rows(self, scenarios: FinancialScenarios) -> str:
        """Construye filas de tabla markdown para los 3 escenarios de recuperación."""
        rows = []
        for name, scenario in [
            ("Conservador", scenarios.conservative),
            ("Realista", scenarios.realistic),
            ("Optimista", scenarios.optimistic),
        ]:
            central = getattr(scenario, 'monthly_loss_central', None) or scenario.monthly_loss_max
            prob_pct = int(scenario.probability * 100)
            rows.append(
                f"| {name} | {format_cop(central)} COP/mes | {prob_pct}% |"
            )
        return "\n".join(rows)
    
    def _build_financial_title_label(self, source_reliability: str) -> str:
        """Retorna label honesto para la seccion financiera segun confiabilidad de datos.

        Args:
            source_reliability: "verified" o "unverified"

        Returns:
            Label para el titulo de la seccion financiera.
        """
        labels = {
            "verified": "Comisión OTA Actual (verificable)",
            "unverified": "Comisión OTA Estimada (benchmarks regionales)",
        }
        return labels.get(source_reliability, "Comisión OTA Estimada")

    def _build_financial_placeholders(
        self,
        scenarios: FinancialScenarios,
        analytics_data: Optional[Dict[str, Any]] = None,
        source_reliability: str = "verified",
    ) -> Dict[str, Any]:
        """
        Construye los placeholders financieros para el template V6.

        Presenta "Comisión OTA verificable" como dato principal + escenarios
        de recuperación con evidence tier.
        FASE-J: label condicional segun source_reliability.
        """
        main = scenarios.get_main_scenario()
        base_value = getattr(main, 'monthly_loss_central', None) or main.monthly_loss_max

        # Determine evidence tier based on available data sources
        ga4_enabled = analytics_data is not None and analytics_data.get("use_ga4", False)
        if ga4_enabled:
            tier = "A"
            disclaimer = (
                "Este diagnóstico usa datos reales de Google Analytics 4 y Search Console. "
                "Los escenarios representan el potencial de mejora basado en su tráfico actual."
            )
        else:
            tier = "C"
            disclaimer = (
                "Este diagnóstico se basa en datos limitados de su web y benchmarks regionales. "
                "Los valores son estimaciones. Para mayor precisión, configure GA4 y Search Console."
            )

        # OTA commission: derive from the scenario value
        # The monthly_loss_max represents the opportunity cost (commissions going to OTAs)
        ota_commission = format_cop(base_value)

        # Build scenario table
        scenario_table = self._build_scenario_table_rows(scenarios)

        # FASE-J: conditional labels and asterisk
        is_verified = source_reliability == "verified"
        financial_title_label = self._build_financial_title_label(source_reliability)
        estimate_asterisk = "" if is_verified else "*"
        estimate_footnote = "" if is_verified else (
            "> * Dato basado en estimaciones. "
            "Conecte GA4 para mayor precisión."
        )

        return {
            'ota_commission_formatted': ota_commission,
            'ota_commission_basis': (
                f"Estimación basada en escenario {main.description.lower()}"
                if main.description else "Estimación basada en datos del hotel"
            ),
            'ota_commission_source': 'onboarding' if ga4_enabled else 'benchmark',
            'scenario_table_rows': scenario_table,
            'evidence_tier': tier,
            'financial_disclaimer': disclaimer,
            'financial_source_ref': 'financial_scenarios.json#realistic',
            'financial_value_central': str(base_value),
            'financial_value_min': str(main.monthly_loss_min),
            'financial_value_max': str(main.monthly_loss_max),
            'financial_method': 'proportional_normalized',
            # FASE-J: source-aware template honesty
            'financial_title_label': financial_title_label,
            'estimate_asterisk': estimate_asterisk,
            'estimate_footnote': estimate_footnote,
            # Backward compatibility
            'loss_6_months': format_cop(base_value * 6),
        }
    
    def _render_template(self, template_content: str, data: Dict[str, str]) -> str:
        """Render the template with data."""
        # Use string.Template for substitution
        template = Template(template_content)
        return template.safe_substitute(data)
    
    def _calculate_coherence_score(self, validation_summary: ValidationSummary) -> int:
        """Calculate overall coherence score from validation summary."""
        if not validation_summary.fields:
            return 0
        
        total_score = 0
        for field in validation_summary.fields:
            if field.confidence == ConfidenceLevel.VERIFIED:
                total_score += 100
            elif field.confidence == ConfidenceLevel.ESTIMATED:
                total_score += 70
            elif field.confidence == ConfidenceLevel.CONFLICT:
                total_score += 30
            else:
                total_score += 0
        
        return int(total_score / len(validation_summary.fields))
    
    def _build_validated_data_table(self, validation_summary: ValidationSummary, audit_result: Optional[V4AuditResult] = None) -> str:
        """Build the validated data table with real audit data."""
        rows = []
        # First, try to get fields from validation_summary
        for field in validation_summary.fields:
            icon = confidence_to_icon(field.confidence)
            label = confidence_to_label(field.confidence)
            sources_str = ", ".join(field.sources) if field.sources else "N/A"
            
            # Format value
            value = field.value
            # Special handling for default values - fields that typically come from defaults
            # and should be marked as N/D to indicate they're not real data
            fields_with_defaults = ['occupancy_rate', 'direct_channel_percentage']
            
            # Check if this field should show N/D
            show_nd = (field.field_name in fields_with_defaults or 
                      (field.sources and "Default" in field.sources))
            
            if show_nd:
                display_value = "N/D (valor por defecto)"
            elif isinstance(value, float):
                display_value = f"{value:,.0f}"
            elif value is None:
                display_value = "N/A"
            elif isinstance(value, (int, float)) and value == 0:
                display_value = "0"
            else:
                display_value = str(value)
            
            row = f"| {icon} {field.field_name} | {display_value} | {label} | {sources_str} |"
            rows.append(row)
        
        # If no fields from summary, extract from audit_result
        if not rows and audit_result:
            validated_fields = self._extract_validated_fields(audit_result)
            for field in validated_fields:
                row = f"| {field['icon']} {field['name']} | {field['value']} | {field['confidence']} | {field['sources']} |"
                rows.append(row)
        
        return "\n".join(rows) if rows else "| Sin datos | - | ⚪ UNKNOWN | - |"
    
    def _extract_validated_fields(self, audit_result: V4AuditResult) -> List[Dict[str, Any]]:
        """Extract validated fields from audit result for the data table."""
        fields = []
        
        # WhatsApp - cross-validated between web and GBP
        phone_web = getattr(audit_result.validation, 'phone_web', None)
        phone_gbp = getattr(audit_result.validation, 'phone_gbp', None)
        
        if phone_web or phone_gbp:
            # Determine confidence level based on cross-validation
            if phone_web and phone_gbp and phone_web == phone_gbp:
                confidence = ConfidenceLevel.VERIFIED
                icon = "🟢"
                sources = "Web + GBP"
                value = phone_web
            elif phone_web:
                confidence = ConfidenceLevel.ESTIMATED
                icon = "🟡"
                sources = "Web"
                value = phone_web
            elif phone_gbp:
                confidence = ConfidenceLevel.ESTIMATED
                icon = "🟡"
                sources = "GBP"
                value = phone_gbp
            else:
                confidence = ConfidenceLevel.UNKNOWN
                icon = "⚪"
                sources = "N/A"
                value = phone_web or phone_gbp or "N/A"
            
            # Format phone number for display
            phone_display = value if value != "N/A" else "No detectado"
            
            fields.append({
                'name': 'WhatsApp',
                'value': phone_display,
                'confidence': confidence.value.upper() if hasattr(confidence, 'value') else str(confidence).upper(),
                'icon': icon,
                'sources': sources
            })
        
        # Habitaciones - from schema properties
        rooms = self._extract_rooms_from_audit(audit_result)
        if rooms:
            fields.append({
                'name': 'Habitaciones',
                'value': str(rooms),
                'confidence': 'ESTIMATED',
                'icon': '🟡',
                'sources': 'Schema/Web'
            })
        
        # ADR - from schema priceRange or benchmark
        adr = self._extract_adr_from_audit(audit_result)
        if adr:
            fields.append({
                'name': 'ADR',
                'value': f"${adr:,.0f} COP",
                'confidence': 'ESTIMATED',
                'icon': '🟡',
                'sources': 'Benchmark'
            })
        
        # GBP Rating
        if audit_result.gbp and audit_result.gbp.place_found and audit_result.gbp.rating > 0:
            fields.append({
                'name': 'Rating GBP',
                'value': f"{audit_result.gbp.rating}/5.0 ({audit_result.gbp.reviews} reviews)",
                'confidence': 'VERIFIED',
                'icon': '🟢',
                'sources': 'Google Places API'
            })
        
        # Performance Score
        if audit_result.performance and audit_result.performance.mobile_score is not None:
            score = audit_result.performance.mobile_score
            # Determine confidence based on having field data
            if audit_result.performance.has_field_data:
                perf_confidence = 'VERIFIED'
                perf_icon = '🟢'
                perf_sources = 'PageSpeed + Field Data'
            else:
                perf_confidence = 'ESTIMATED'
                perf_icon = '🟡'
                perf_sources = 'PageSpeed (Lab)'
            
            fields.append({
                'name': 'Performance Móvil',
                'value': f"{score}/100",
                'confidence': perf_confidence,
                'icon': perf_icon,
                'sources': perf_sources
            })
        
        return fields
    
    def _extract_rooms_from_audit(self, audit_result: V4AuditResult) -> Optional[int]:
        """Extract room count from schema or audit data."""
        # Try schema properties first
        if hasattr(audit_result.schema, 'properties') and audit_result.schema.properties:
            props = audit_result.schema.properties
            # Common property names for room count
            for key in ['numberOfRooms', 'rooms', 'numberOfUnits']:
                if key in props and props[key]:
                    try:
                        return int(props[key])
                    except (ValueError, TypeError):
                        continue
        return None
    
    def _extract_adr_from_audit(self, audit_result: V4AuditResult) -> Optional[float]:
        """Extract ADR from schema priceRange or validation data."""
        # Try schema properties for priceRange
        if hasattr(audit_result.schema, 'properties') and audit_result.schema.properties:
            props = audit_result.schema.properties
            if 'priceRange' in props and props['priceRange']:
                # Parse price range like "$100 - $200" or "$150"
                price_str = str(props['priceRange'])
                # Extract numbers from string
                numbers = re.findall(r'[\d,]+', price_str)
                if numbers:
                    # Take the average of min and max if range, or just the number
                    try:
                        clean_nums = [int(n.replace(',', '')) for n in numbers]
                        return sum(clean_nums) / len(clean_nums)
                    except (ValueError, TypeError):
                        pass
        
        # Try validation ADR
        adr_web = getattr(audit_result.validation, 'adr_web', None)
        if adr_web:
            return float(adr_web)
        
        adr_benchmark = getattr(audit_result.validation, 'adr_benchmark', None)
        if adr_benchmark:
            return float(adr_benchmark)
        
        return None
    
    def _build_empathy_message(self, scenarios: FinancialScenarios, hotel_name: str) -> str:
        """Build an empathy message for the hotel owner."""
        main = scenarios.get_main_scenario()
        amount = format_cop(getattr(main, 'monthly_loss_central', None) or main.monthly_loss_max)
        
        messages = [
            f"Cada mes que pasa, **{hotel_name}** deja de recibir aproximadamente **{amount}** en reservas que podrían ser directas.",
            f"Nuestro análisis certificado revela que **{hotel_name}** está perdiendo **{amount}** mensuales en comisiones de OTAs.",
            f"Basado en datos validados de múltiples fuentes, **{hotel_name}** tiene un potencial de recuperación de **{amount}** al mes.",
        ]
        
        # Use hash of hotel name to get consistent message
        import hashlib
        idx = int(hashlib.md5(hotel_name.encode()).hexdigest(), 16) % len(messages)
        return messages[idx]
    
    def _format_list(self, items: List[str]) -> str:
        """Format a list as markdown bullet points."""
        if not items:
            return "  - Sin supuestos definidos"
        return "\n".join([f"  - {item}" for item in items])


    def _build_solvable_problems_table(self, audit_result: V4AuditResult) -> str:
        """Build table of problems with automatic solutions."""
        rows = []
        
        # Guard against None audit_result
        if audit_result is None:
            return "| Datos de auditoria no disponibles | - | - | - |"
        
        # Guard against None schema
        if audit_result.schema is None:
            return "| Datos de schema no disponibles | - | - | - |"
        
        # Guard against None validation
        if audit_result.validation is None:
            validation_note = "| Datos de validacion no disponibles | - | - | - |"
            # Still check schema issues
            if not audit_result.schema.hotel_schema_detected:
                return "| Sin Schema de Hotel | 🔴 Crítica | `hotel_schema.json` | 🟢 VERIFIED |"
            return validation_note
        
        # Schema issues
        if not audit_result.schema.hotel_schema_detected:
            rows.append("| Sin Schema de Hotel | 🔴 Crítica | `hotel_schema.json` | 🟢 VERIFIED |")
        elif not audit_result.schema.hotel_schema_valid:
            rows.append("| Schema de Hotel Inválido | 🟡 Media | `hotel_schema_fix.json` | 🟢 VERIFIED |")
        
        # FAQ issues
        if not audit_result.schema.faq_schema_detected:
            rows.append("| Sin Schema FAQ | 🟡 Media | `faqs.csv` | 🟡 ESTIMATED |")
        
        # WhatsApp issues - distinguir visual vs Schema
        whatsapp_status = getattr(audit_result.validation, 'whatsapp_status', 'unknown')
        phone_web = getattr(audit_result.validation, 'phone_web', None)
        raw_whatsapp_html = getattr(audit_result.validation, 'whatsapp_html_detected', None)
        whatsapp_html = raw_whatsapp_html if isinstance(raw_whatsapp_html, bool) else False
        if whatsapp_status == ConfidenceLevel.CONFLICT.value:
            rows.append("| WhatsApp Inconsistente | 🔴 Crítica | `boton_whatsapp.html` | 🔴 CONFLICT |")
        elif not phone_web and not whatsapp_html:
            # Ni Schema ni HTML → brecha real
            rows.append("| Sin Botón WhatsApp | 🟡 Media | `boton_whatsapp.html` | 🟢 VERIFIED |")
        
        # Performance
        if audit_result.performance and audit_result.performance.mobile_score is not None and audit_result.performance.mobile_score < 50:
            rows.append("| Rendimiento Móvil Bajo | 🟡 Media | Guía de optimización | 🟢 VERIFIED |")
        
        return "\n".join(rows) if rows else "| No se detectaron problemas solubles automáticamente | - | - | - |"
    
    def _build_manual_attention_table(self, audit_result: V4AuditResult) -> str:
        """Build table of problems requiring manual attention."""
        rows = []
        
        # Guard against None audit_result or gbp
        if audit_result is None or audit_result.gbp is None:
            return "| Datos de GBP no disponibles | - | - | - |"
        
        # GBP issues
        if audit_result.gbp.geo_score < 70:
            rows.append(f"| Perfil GBP Sub-optimizado | 🟡 Media | Optimizar {audit_result.gbp.reviews} reviews y {audit_result.gbp.photos} fotos |")
        
        if audit_result.gbp.photos < 20:
            rows.append(f"| Fotos GBP Insuficientes | 🟡 Media | Subir al menos {20 - audit_result.gbp.photos} fotos adicionales |")
        
        # Performance without field data
        if audit_result.performance and not audit_result.performance.has_field_data:
            rows.append("| Sin Datos de Campo (Core Web Vitals) | 🟡 Media | El sitio puede ser nuevo o tener tráfico bajo |")
        
        # Conflicts
        if audit_result.validation and audit_result.validation.conflicts:
            for conflict in audit_result.validation.conflicts:
                rows.append(f"| Conflicto: {conflict.get('field_name', 'Desconocido')} | 🔴 Alta | Revisión manual requerida |")
        
        return "\n".join(rows) if rows else "| No se detectaron problemas que requieran atención manual | - | - |"
    
    def _build_top_critical_problems(self, audit_result: V4AuditResult) -> str:
        """Build the top 3 critical problems section using shared function."""
        problems = extract_top_problems(audit_result, limit=3)

        if not problems:
            return "No se identificaron problemas críticos. ¡El hotel está bien posicionado!"

        # Format with numbers
        formatted = []
        for i, problem in enumerate(problems, 1):
            formatted.append(f"{i}. **{problem}**")

        return "\n\n".join(formatted)
    
    def _build_quick_wins(self, audit_result: V4AuditResult) -> str:
        """Build the quick wins list with correct numbering."""
        wins = []
        win_number = 1
        
        # Guard against None
        if audit_result is None:
            return "Datos de auditoria no disponibles."
        
        # Schema implementation
        if audit_result.schema and not audit_result.schema.hotel_schema_detected:
            wins.append(f"{win_number}. **Implementar Schema de Hotel** - Impacto SEO inmediato (1-2 días)")
            win_number += 1
        
        # WhatsApp button - guard against None validation
        # Solo sugerir si NO hay boton HTML ni Schema telephone
        if audit_result.validation:
            phone_web = getattr(audit_result.validation, 'phone_web', None)
            raw_whatsapp_html = getattr(audit_result.validation, 'whatsapp_html_detected', None)
            whatsapp_html = raw_whatsapp_html if isinstance(raw_whatsapp_html, bool) else False
            if not phone_web and not whatsapp_html:
                wins.append(f"{win_number}. **Agregar Botón WhatsApp** - Canal directo de reservas (1 día)")
                win_number += 1
        
        # FAQ schema
        if audit_result.schema and not audit_result.schema.faq_schema_detected:
            wins.append(f"{win_number}. **Crear Schema FAQ** - Capturar rich snippets (2-3 días)")
            win_number += 1
        
        # GBP optimization
        if audit_result.gbp and audit_result.gbp.photos < 20:
            wins.append(f"{win_number}. **Subir Fotos a GBP** - Mejorar visibilidad local (1 día)")
            win_number += 1
        
        # Performance
        if audit_result.performance and audit_result.performance.mobile_score and audit_result.performance.mobile_score < 70:
            wins.append(f"{win_number}. **Optimizar Velocidad Móvil** - Mejorar experiencia usuario (3-5 días)")
            win_number += 1
        
        if not wins:
            wins.append("El hotel está bien optimizado. Enfocarse en estrategia de contenido.")
        
        return "\n".join(wins)
    
    def _build_geo_problems_table(self, audit_result: V4AuditResult) -> str:
        """Construir tabla de problemas y métricas GEO.
        
        Args:
            audit_result: Resultado del audit con datos GEO
            
        Returns:
            Markdown con tabla de métricas GEO
        """
        if not audit_result:
            return ""
        
        has_ai_crawlers = hasattr(audit_result, 'ai_crawlers') and audit_result.ai_crawlers is not None
        has_citability = hasattr(audit_result, 'citability') and audit_result.citability is not None
        has_ia_readiness = hasattr(audit_result, 'ia_readiness') and audit_result.ia_readiness is not None
        
        if not any([has_ai_crawlers, has_citability, has_ia_readiness]):
            return ""
        
        rows = []
        
        if has_ai_crawlers:
            ai = audit_result.ai_crawlers
            score = getattr(ai, 'overall_score', 0) or 0
            status_icon = "🟢" if score >= 0.7 else ("🟡" if score >= 0.4 else "🔴")
            blocked = getattr(ai, 'blocked_crawlers', []) or []
            blocked_count = len(blocked)
            rows.append(f"| Accesibilidad IA | {score:.2f}/1.00 | {blocked_count} bloqueados | {status_icon} |")
        
        if has_citability:
            cit = audit_result.citability
            score = getattr(cit, 'overall_score', 0) or 0
            status_icon = "🟢" if score >= 50 else ("🟡" if score >= 30 else "🔴")
            blocks = getattr(cit, 'blocks_analyzed', 0) or 0
            rows.append(f"| Citabilidad | {score:.1f}/100 | {blocks} bloques | {status_icon} |")
        
        if has_ia_readiness:
            ia = audit_result.ia_readiness
            score = getattr(ia, 'overall_score', 0) or 0
            status_icon = "🟢" if score >= 50 else ("🟡" if score >= 30 else "🔴")
            status_text = getattr(ia, 'status', 'Unknown') or 'Unknown'
            rows.append(f"| IA-Readiness | {score:.1f}/100 | {status_text} | {status_icon} |")
        
        if not rows:
            return ""
        
        table = """
## [NEW] Métricas de Optimización para IA

| Métrica | Score | Detalle | Estado |
|---------|-------|---------|--------|
"""
        table += "\n".join(rows)
        table += """
> Estas métricas evalúan cómo los motores de IA (ChatGPT, Claude, Perplexity) pueden descubrir y citar su contenido.

"""
        return table
    
    # Score calculation methods

    def _build_regional_transparency(
        self,
        geo: Dict, competitive: Dict, seo: Dict, aeo: Dict
    ) -> str:
        """Build transparency footnote explaining data sources for regional averages.

        Only includes entries where source is NOT the default (to avoid noise).
        """
        sources = []
        for label, data in [
            ('GEO', geo), ('Competitiva', competitive),
            ('SEO', seo), ('AEO', aeo),
        ]:
            if data['source'] != 'default':
                sources.append(f"- **{label}**: {data['detail']}")
        
        if not sources:
            return ''
        
        return (
            '\n> **Fuente de promedios regionales**\n>\n'
            + '\n'.join(f'> {s}' for s in sources)
        )

    def _get_regional_benchmarks(self, region: str) -> Dict[str, int]:
        """Load regional benchmark scores from plan_maestro_data.json.

        Returns dict with geo_score_ref, aeo_score_ref, seo_score_ref
        for the given region, falling back to 'default' if region not found.
        """
        try:
            from modules.scrapers.scraper_fallback import ScraperFallback
            fallback = ScraperFallback()
            regiones = fallback.benchmarks.get('regiones', {})
            region_data = regiones.get(region.lower().replace(' ', '_'), regiones.get('default', {}))
            return {
                'geo_score_ref': region_data.get('geo_score_ref', 55),
                'aeo_score_ref': region_data.get('aeo_score_ref', 20),
                'seo_score_ref': region_data.get('seo_score_ref', 50),
            }
        except Exception:
            return {'geo_score_ref': 85, 'aeo_score_ref': 40, 'seo_score_ref': 59}

    def _calculate_regional_average(
        self,
        audit_result: V4AuditResult,
        pillar: str,
        region: str,
        min_competitors: int = 3
    ) -> Dict[str, Any]:
        """Calculate regional average with 3-tier fallback chain.

        Tier 1 (REAL): If >= min_competitors have valid scores, use their mean.
        Tier 2 (REGION): Use regional benchmark from plan_maestro_data.json.
        Tier 3 (DEFAULT): Use hardcoded national default.

        Args:
            audit_result: Full audit result with competitors data.
            pillar: One of 'geo', 'competitive', 'seo', 'aeo'.
            region: Region string (e.g., 'eje_cafetero', 'antioquia').
            min_competitors: Minimum valid competitors for Tier 1.

        Returns:
            Dict with:
              - value (int): The average score to display.
              - source (str): 'competidores', 'benchmark_regional', or 'default'.
              - detail (str): Human-readable explanation for transparency.
        """
        # --- TIER 1: Real competitor data (only for GEO, which competitors have) ---
        if pillar == 'geo' and audit_result and hasattr(audit_result, 'competitors') and audit_result.competitors:
            valid = [
                c['geo_score']
                for c in audit_result.competitors
                if isinstance(c.get('geo_score'), (int, float)) and c['geo_score'] > 0
            ]
            if len(valid) >= min_competitors:
                avg = int(sum(valid) / len(valid))
                return {
                    'value': avg,
                    'source': 'competidores',
                    'detail': f'Promedio de {len(valid)} competidores cercanos auditados',
                }

        # --- TIER 2: Regional benchmark from config ---
        benchmarks = self._get_regional_benchmarks(region)
        key = f'{pillar}_score_ref'
        if key in benchmarks:
            return {
                'value': benchmarks[key],
                'source': 'benchmark_regional',
                'detail': f'Benchmark regional ({region.replace("_", " ").title()}, Q1 2026)',
            }

        # --- TIER 3: National default ---
        defaults = {
            'geo': 85,
            'competitive': 50,
            'seo': 59,
            'aeo': 40,
        }
        return {
            'value': defaults.get(pillar, 50),
            'source': 'default',
            'detail': 'Promedio nacional estimado',
        }

    def _calculate_geo_score(self, audit_result: V4AuditResult) -> str:
        """Calculate GEO score based on GBP data."""
        if not audit_result or not audit_result.gbp or not audit_result.gbp.place_found:
            return "0"
        score = min(100, max(0, audit_result.gbp.geo_score))
        return str(int(score))
    
    def _calculate_competitive_score(self, audit_result: V4AuditResult) -> str:
        """Calculate Competitive Position Score vs nearby competitors.

        Uses competitor geo_scores from Places API to determine where the hotel
        ranks among its nearby peers. This is genuinely independent of GEO:
        GEO = how complete YOUR profile is
        Competitive = how YOUR profile ranks vs everyone around you

        A hotel can have GEO=85 but still be in 4th place because 3 competitors
        score 90+. That IS a real business opportunity.

        Returns 0 if no competitor data available (avoids manufacturing scores).
        """
        if not audit_result or not audit_result.gbp or not audit_result.gbp.place_found:
            return "0"
        if not hasattr(audit_result, 'competitors') or not audit_result.competitors:
            return "0"

        # Gather competitor geo_scores
        my_score = audit_result.gbp.geo_score
        competitors = [c for c in audit_result.competitors if c.get("geo_score") is not None]
        if not competitors:
            return "0"

        competitor_scores = [c["geo_score"] for c in competitors]

        # Rank: how many competitors beat us
        beaten_by = sum(1 for s in competitor_scores if s > my_score)
        total_with_us = len(competitor_scores) + 1  # +1 = us
        rank_percentile = ((total_with_us - 1 - beaten_by) / total_with_us) * 100

        # Gap: distance to the next competitor ahead
        higher_scores = sorted([s for s in competitor_scores if s > my_score])
        if higher_scores:
            gap_to_next = higher_scores[0] - my_score
            # Bigger gap = worse competitive position
            gap_penalty = min(40, gap_to_next * 2)
        else:
            gap_penalty = 0  # We're #1 locally

        # Final: mix percentile ranking with proximity-to-leader gap
        score = max(0, int(rank_percentile - gap_penalty))
        return str(score)
    
    def _calculate_web_score(self, audit_result: V4AuditResult) -> str:
        """Calculate Web/SEO score based on performance and schema."""
        score = 0
        # Guard against None
        if not audit_result:
            return "0"
        # Performance score (up to 40 points)
        if audit_result.performance and audit_result.performance.mobile_score:
            score += min(40, audit_result.performance.mobile_score * 0.4)
        # Schema bonus (up to 30 points)
        if audit_result.schema and audit_result.schema.hotel_schema_detected:
            score += 20
            if audit_result.schema.hotel_schema_valid:
                score += 10
        # FAQ schema (up to 20 points)
        if audit_result.schema and audit_result.schema.faq_schema_detected:
            score += 15
        # Validation consistency (up to 10 points)
        if audit_result.validation and audit_result.validation.whatsapp_status != ConfidenceLevel.CONFLICT.value:
            score += 10
        return str(min(100, int(score)))
    
    def _calculate_aeo_score(self, audit_result: V4AuditResult) -> str:
        """Calculate AEO (AI Engine Optimization) Infrastructure score.

        Measures 4 components (25pts each, 100pts total):
        - Schema Hotel válido (25pts): hotel_schema_valid detectado y válido
        - FAQ Schema válido (25pts): faq_schema_valid detectado y válido
        - Open Graph detectado (25pts): og:title + og:description presentes
        - Citabilidad (25pts): contenido citable por IAs (score > umbral)

        Returns: "XX" string when measured, "0" when no data available.
        """
        if not audit_result:
            return "0"

        score = 0
        components_measured = 0

        # 1. Schema Hotel válido (25 pts)
        if audit_result.schema:
            components_measured += 1
            if audit_result.schema.hotel_schema_valid:
                score += 25
            elif audit_result.schema.hotel_schema_detected:
                score += 10  # Detectado pero no válido = puntos parciales

        # 2. FAQ Schema válido (25 pts)
        if audit_result.schema:
            components_measured += 1
            if audit_result.schema.faq_schema_valid:
                score += 25
            elif audit_result.schema.faq_schema_detected:
                score += 10  # Detectado pero no válido = puntos parciales

        # 3. Open Graph detectado (25 pts)
        if hasattr(audit_result, 'seo_elements') and audit_result.seo_elements:
            components_measured += 1
            if getattr(audit_result.seo_elements, 'open_graph', False):
                score += 25

        # 4. Citabilidad (25 pts)
        if hasattr(audit_result, 'citability') and audit_result.citability and audit_result.citability.overall_score is not None:
            components_measured += 1
            cit_score = audit_result.citability.overall_score
            if cit_score >= 70:
                score += 25
            elif cit_score >= 40:
                score += 15
            elif cit_score > 0:
                score += 5

        # Solo retornar "0" si NINGÚN componente tuvo datos
        if components_measured == 0:
            return "0"

        return str(min(100, score))

    def _calculate_iao_score_from_audit(self, audit_result: V4AuditResult) -> str:
        """Calculate IAO score from audit using 4-pilar extraction (FASE-A)."""
        elementos_iao = self._extraer_elementos_iao(audit_result)
        score = calcular_score_iao(elementos_iao)
        return str(score)

    def _calculate_score_global_from_audit(self, audit_result: V4AuditResult) -> str:
        """Calculate score global from 4 pilar scores (FASE-A)."""
        elementos_seo = self._extraer_elementos_seo(audit_result)
        elementos_geo = self._extraer_elementos_geo(audit_result)
        elementos_aeo = self._extraer_elementos_aeo(audit_result)
        elementos_iao = self._extraer_elementos_iao(audit_result)
        seo = calcular_score_seo(elementos_seo)
        geo = calcular_score_geo(elementos_geo)
        aeo = calcular_score_aeo(elementos_aeo)
        iao = calcular_score_iao(elementos_iao)
        return str(calcular_score_global(seo, geo, aeo, iao))

    # ---------------------------------------------------------------
    # ANALYTICS INTEGRATION
    # ---------------------------------------------------------------

    def _check_analytics_status(self, ga4_property_id: str = None, hotel_url: str = None) -> AnalyticsStatus:
        """
        Verifica el estado de cada fuente de datos analytics SIN hacer
        las llamadas API reales. Esto permite informar al template POR
        QUE no hay datos en vez de mostrar ceros silenciosos.

        RETORNA:
            AnalyticsStatus con ga4/profound/semrush availability + errores.
        """
        status = AnalyticsStatus()

        # --- GA4 ---
        try:
            from modules.analytics.google_analytics_client import GoogleAnalyticsClient
            ga4 = GoogleAnalyticsClient(property_id=ga4_property_id)
            status.ga4_available = ga4.is_available()
            if not status.ga4_available:
                # Leer el error de inicializacion del client
                if ga4._init_error:
                    status.ga4_error = ga4._init_error
                    status.ga4_status_text = f"No configurado ({ga4._init_error})"
                else:
                    status.ga4_error = "GA4 no disponible"
                    status.ga4_status_text = "No disponible (error desconocido)"
        except Exception as e:
            status.ga4_error = str(e)
            status.ga4_status_text = f"Error: {str(e)}"

        # --- GSC (FASE-D) ---
        try:
            from modules.analytics.google_search_console_client import GoogleSearchConsoleClient
            gsc = GoogleSearchConsoleClient(site_url=hotel_url)
            status.gsc_available = gsc.is_configured()
            if not status.gsc_available:
                if gsc._init_error:
                    status.gsc_error = gsc._init_error
                    status.gsc_status_text = f"No configurado ({gsc._init_error})"
                else:
                    status.gsc_status_text = "No configurado (agregue GSC_SITE_URL)"
        except Exception as e:
            status.gsc_error = str(e)
            status.gsc_status_text = f"Error: {str(e)}"

        return status

    def _get_analytics_summary(self, ga4_property_id: str = None) -> Dict[str, Any]:
        """
        Obtiene resumen de analytics desde GA4 (cuando esta configurado).

        RETORNA:
            dict con data_source, summary_text, indirect_sessions, note
        """
        try:
            from modules.analytics.google_analytics_client import GoogleAnalyticsClient

            ga4 = GoogleAnalyticsClient(property_id=ga4_property_id)
            if ga4.is_available():
                resp = ga4.get_indirect_traffic(date_range="last_30_days")
                if resp.get("data_source") == "GA4":
                    indirect = resp.get("sessions_indirect", 0)
                    direct = resp.get("sessions_direct", 0)
                    total = indirect + direct
                    pct = f"{(indirect / total * 100):.1f}" if total > 0 else "0.0"
                    return {
                        "data_source": "GA4",
                        "summary_text": (
                            f"Sesiones (ultimos 30 dias): {total:,} totales, "
                            f"{indirect:,} indirectas ({pct}%). "
                            f"Fuente: Google Analytics 4."
                        ),
                        "indirect_sessions": indirect,
                        "note": None,
                    }

        except Exception as e:
            logging.getLogger(__name__).debug(f"GA4 analytics summary failed: {e}")

        return {
            "data_source": "N/A",
            "summary_text": "Sin medicion de trafico real (GA4 no configurado).",
            "indirect_sessions": 0,
            "note": "Configure GA4_PROPERTY_ID y GA4_CREDENTIALS_PATH para datos reales.",
        }

    def _get_analytics_fallback(self, audit_result: V4AuditResult) -> Dict[str, Any]:
        """
        Genera estimados cualitativos basados en senales del audit.

        Se usa cuando GA4 no esta disponible y Profound/Semrush son stubs.
        Evalua 6 senales: schema_hotel, schema_faq, contenido_extenso,
        open_graph, NAP_consistente, rendimiento_movil.

        RETORNA:
            dict con data_source="estimado", summary_text, iao_qualitative,
            signals (lista)
        """
        if not audit_result:
            return {
                "data_source": "estimado",
                "summary_text": "Visibilidad IA: No evaluado (sin datos de auditoria).",
                "iao_qualitative": "Baja",
                "signals": ["Sin datos de auditoria"],
            }

        signals: list[str] = []
        points = 0

        # 1. Schema Hotel (0/25)
        has_schema = bool(audit_result.schema and audit_result.schema.hotel_schema_detected)
        points += 25 if has_schema else 0
        signals.append(f"Schema Hotel: {'Detectado' if has_schema else 'No detectado'}")

        # 2. FAQ Schema (0/15)
        has_faq = bool(audit_result.schema and audit_result.schema.faq_schema_detected)
        points += 15 if has_faq else 0
        signals.append(f"Schema FAQ: {'Presente' if has_faq else 'Ausente'}")

        # 3. Contenido extenso / Citability (0/25)
        cit_score = 0
        if hasattr(audit_result, 'citability') and audit_result.citability:
            cit_score = getattr(audit_result.citability, 'overall_score', 0) or 0
        if cit_score > 50:
            points += 25
            signals.append(f"Contenido extenso para IA (citability: {cit_score:.0f}/100)")
        elif cit_score > 0:
            points += 10
            signals.append(f"Contenido limitado (citability: {cit_score:.0f}/100)")
        else:
            signals.append("Citabilidad no medida")

        # 4. Open Graph (0/15)
        has_og = False
        if hasattr(audit_result, 'seo_elements') and audit_result.seo_elements:
            has_og = bool(getattr(audit_result.seo_elements, 'open_graph', False))
        points += 15 if has_og else 0
        signals.append(f"Open Graph: {'Configurado' if has_og else 'No configurado'}")

        # 5. NAP consistente (0/10)
        nap_ok = False
        if hasattr(audit_result, 'validation') and audit_result.validation:
            ws = getattr(audit_result.validation, 'whatsapp_status', None)
            nap_ok = (ws == ConfidenceLevel.VERIFIED.value)
        points += 10 if nap_ok else 0
        signals.append(f"NAP consistente: {'Verificado' if nap_ok else 'No verificado'}")

        # 6. Rendimiento movil (0/10)
        mobile_ok = False
        if audit_result.performance:
            ms = getattr(audit_result.performance, 'mobile_score', 0) or 0
            mobile_ok = ms >= 50
        points += 10 if mobile_ok else 0
        signals.append(f"Rendimiento movil: {'Adecuado' if mobile_ok else 'Bajo'}")

        # Clamp to 0-100
        points = min(100, max(0, points))

        # Qualitative label
        if points >= 60:
            label = "Alta"
        elif points >= 35:
            label = "Media"
        else:
            label = "Baja"

        if not signals:
            signals.append("Sin senales disponibles")

        return {
            "data_source": "estimado",
            "summary_text": f"Visibilidad en IA: {label} (estimado cualitativo). Senales: " + "; ".join(signals[:4]),
            "iao_qualitative": label,
            "signals": signals,
        }

    def _get_score_status(self, score: str, benchmark: int) -> str:
        """Get status emoji based on score vs benchmark."""
        # Handle dashes (not measured)
        if not score or score.strip() in ["-", "—"]:
            return "⏳ Pendiente"
        try:
            s = int(score)
            if s >= benchmark * 1.1:
                return "✅ Superior"
            elif s >= benchmark * 0.9:
                return "⚠️ Promedio"
            else:
                return "❌ Bajo"
        except (ValueError, TypeError):
            return "⏳ Pendiente"
    
    # Brecha (gap) calculation methods
    def _get_brecha_nombre(self, audit_result: V4AuditResult, index: int) -> str:
        """Get nombre de la brecha (razón) by index."""
        brechas = self._get_brecha_pesos(audit_result)
        if index < len(brechas):
            return brechas[index]['nombre']
        return "Sin identificar"
    
    def _get_brecha_costo(self, audit_result: V4AuditResult, financial_scenarios: FinancialScenarios, index: int) -> str:
        """Get costo estimado de la brecha by index (usa pesos normalizados + valor central)."""
        brechas = self._get_brecha_pesos(audit_result)
        if index < len(brechas):
            main = financial_scenarios.get_main_scenario()
            # Valor central si existe, sino max (legacy fallback)
            base_value = getattr(main, 'monthly_loss_central', None) or main.monthly_loss_max
            proportion = brechas[index].get('impacto', 0) / 100.0  # peso normalizado a proporcion
            costo = base_value * proportion
            return format_cop(costo)
        return format_cop(0)
    
    def _get_brecha_detalle(self, audit_result: V4AuditResult, index: int) -> str:
        """Get detalle/explicación de la brecha by index."""
        brechas = self._get_brecha_pesos(audit_result)
        if index < len(brechas):
            return brechas[index]['detalle']
        return "Sin informacion adicional"
    
    def _get_brecha_impacto(self, audit_result: V4AuditResult, index: int) -> str:
        """Get impacto porcentual de la brecha by index (usa pesos normalizados)."""
        brechas = self._get_brecha_pesos(audit_result)
        if index < len(brechas):
            impacto = brechas[index].get('impacto', 0)
            # impacto ya esta en escala 0-100 (normalizado)
            return f"{int(impacto)}%"
        return "0%"
    
    def _get_brecha_resumen(self, audit_result: V4AuditResult, index: int) -> str:
        """Get resumen de una línea de la brecha by index."""
        brechas = self._get_brecha_pesos(audit_result)
        if index < len(brechas):
            detalle = brechas[index].get('detalle', 'Sin resumen')
            return detalle[:80] + '...' if len(detalle) > 80 else detalle
        return "brecha no identificada"
    

    def _get_brecha_recuperacion(self, audit_result, financial_scenarios, index):
        """Get recuperacion mensual estimada de la brecha by index (usa pesos normalizados + valor central)."""
        brechas = self._get_brecha_pesos(audit_result)
        if index < len(brechas):
            main = financial_scenarios.get_main_scenario()
            base_value = getattr(main, 'monthly_loss_central', None) or main.monthly_loss_max
            proportion = brechas[index].get('impacto', 0) / 100.0
            recuperacion = base_value * proportion
            return f"{recuperacion:,.0f}"
        return "0"

    def _build_brechas_section(self, audit_result: V4AuditResult, financial_scenarios: FinancialScenarios) -> str:
        """Genera seccion markdown con TODAS las brechas detectadas (0-10+)."""
        brechas = self._get_brecha_pesos(audit_result)
        if not brechas:
            return "No se detectaron brechas criticas. Su presencia digital esta en buen estado."

        sections = []
        for i, b in enumerate(brechas, 1):
            costo = self._get_brecha_costo(audit_result, financial_scenarios, i - 1)
            impacto_pct = int(b.get('impacto', 0))  # ya normalizado a 0-100
            sections.append(
                f"### [BRECHA {i}] {b['nombre']}\n"
                f"- **Detalle:** {b['detalle']}\n"
                f"- **Por que importa:** {impacto_pct}%\n"
                f"- **Costo:** {costo}/mes\n"
            )
        return "\n".join(sections)

    def _build_brechas_resumen_section(self, audit_result: V4AuditResult, financial_scenarios: FinancialScenarios) -> str:
        """Genera tabla resumen dinamica de N brechas -> oportunidades."""
        brechas = self._get_brecha_pesos(audit_result)
        if not brechas:
            return "| Sin brechas detectadas | — |"

        rows = []
        for i, b in enumerate(brechas, 1):
            detalle_corto = b.get('detalle', 'Sin resumen')[:80]
            if len(b.get('detalle', '')) > 80:
                detalle_corto += '...'
            recuperacion = self._get_brecha_recuperacion(audit_result, financial_scenarios, i - 1)
            rows.append(f"| {detalle_corto} | +{recuperacion}/mes |")
        return "\n".join(rows)

    def _build_regional_context(self, region: str) -> str:
        """Build regional context text for the hotel location."""
        if not region:
            return "Colombia es el segundo destino turístico más grande de América Latina, con más de 5 millones de turistas anuales."
        
        region_contexts = {
            'cartagena': 'Cartagena es el destino turístico más importante del Caribe colombiano, con más de 500,000 turistas internacionales anuales.',
            'medellín': 'Medellín se ha convertido en un hub de turismo de negocios e innovación, con una ocupación hotelera promedio del 65%.',
            'bogotá': 'Bogotá recibe más de 1.5 millones de turistas al año, siendo el centro económico y cultural de Colombia.',
            'cali': 'Cali es conocida por el turismo cultural y gastronómico, con una escena hotelera en crecimiento.',
            'barranquilla': 'Barranquilla es un centro económico estratégico con creciente turismo corporativo.',
            'santa marta': 'Santa Marta ofrece turismo histórico y de naturaleza, con acceso a parques nacionales.',
            'eje cafetero': 'El Eje Cafetero (Caldas, Quindío, Risaralda) es una de las principales regiones cafeteras del mundo y un destino turístico en crecimiento. Los viajeros buscan experiencias auténticas de naturaleza, café y cultura. La presencia digital hotelera es clave para captar tanto turismo nacional como internacional.',
            'san andrés': 'San Andrés es un destino caribeño con alta demanda turística internacional, conocido por sus playas y el mar de los siete colores.',
            'llanos orientales': 'Los Llanos Orientales ofrecen turismo de naturaleza y ganadería, con creciente interés en experiencias rurales auténticas.',
            'costa atlántica': 'La Costa Atlántica colombiana concentra importantes destinos turísticos con playa, cultura e historia, liderados por Cartagena y Barranquilla.',
        }
        
        region_lower = region.lower()
        for key, context in region_contexts.items():
            if key in region_lower:
                return context
        
        region_display = region if region and region.lower() not in ("nacional", "colombia", "general", "") else "esta zona"
        return f"{region_display} en Colombia presenta oportunidades de crecimiento en presencia digital hotelera."
    
    def _build_urgencia_content(self, financial_scenarios: FinancialScenarios, hotel_name: str) -> str:
        """Build urgency content explaining why the hotel should act now."""
        main = financial_scenarios.get_main_scenario()
        loss_monthly = main.format_loss_cop()
        confidence = int(main.confidence_score * 100)
        
        return (
            f"{hotel_name} está perdiendo aproximadamente {loss_monthly} mensuales "
            f"debido a brechas en su presencia digital. "
            f"Con {confidence}% de confianza en el análisis, cada mes sin actuar representa "
            f"una oportunidad de recuperación de ingresos no aprovechada. "
            f"El mercado hotelero en Colombia es cada vez más competitivo en el entorno digital, "
            f"y los hoteles que no optimizan su presencia en buscadores, GBP y asistentes de IA "
            f"pierden posicionamiento progresivamente."
        )
    
    def _build_quick_wins_content(self, audit_result: V4AuditResult) -> str:
        """Build quick wins content as markdown text."""
        quick_wins = self._build_quick_wins(audit_result)
        if not quick_wins:
            return "Optimizar Google Business Profile con fotos de alta calidad y descripciones completas.\nImplementar schema markup basico en el sitio web.\nAgregar preguntas frecuentes al sitio."
        
        # Split string into lines before slicing -- [:5] on a string takes chars, not lines
        wins_list = quick_wins.split('\n')
        content_lines = []
        for i, win in enumerate(wins_list[:5], 1):
            win = win.strip()
            if not win:
                continue
            # Remove existing numbering from _build_quick_wins to avoid duplication
            cleaned = re.sub(r'^\d+\.\s*', '', win)
            content_lines.append(f"{i}. {cleaned}")
        return '\n'.join(content_lines)
    
    # ----------------------------------------------------------------
    # 4-PILAR EXTRACTION (FASE-A)
    # ----------------------------------------------------------------

    def _extraer_elementos_seo(self, audit_result: V4AuditResult) -> dict:
        """Extrae elementos del pilar SEO (Para que te ENCUENTREN)."""
        elementos = {}
        if not audit_result:
            return {k: False for k in CHECKLIST_SEO}

        # SSL
        elementos["ssl"] = audit_result.url.startswith('https') if audit_result.url else False
        # Schema hotel
        elementos["schema_hotel"] = bool(audit_result.schema.hotel_schema_detected) if audit_result.schema else False
        # Performance
        elementos["LCP_ok"] = (
            audit_result.performance and audit_result.performance.lcp is not None
            and audit_result.performance.lcp <= 2.5
        )
        elementos["CLS_ok"] = (
            audit_result.performance and audit_result.performance.cls is not None
            and audit_result.performance.cls <= 0.1
        )
        # Imagenes alt
        if hasattr(audit_result, 'seo_elements') and audit_result.seo_elements:
            elementos["imagenes_alt"] = audit_result.seo_elements.imagenes_alt
        else:
            elementos["imagenes_alt"] = False
        # Blog activo (sin detector aun)
        elementos["blog_activo"] = False
        # Schema reviews (proxy: gbp.rating existe)
        elementos["schema_reviews"] = bool(audit_result.gbp.rating) if audit_result.gbp else False

        return elementos

    def _extraer_elementos_geo(self, audit_result: V4AuditResult) -> dict:
        """Extrae elementos del pilar GEO (Para que te UBICQUEN)."""
        elementos = {}
        if not audit_result:
            return {k: False for k in CHECKLIST_GEO}

        # NAP consistente: WhatsApp + Address
        ws_status = getattr(audit_result.validation, 'whatsapp_status', None) if audit_result.validation else None
        address_status = getattr(audit_result.validation, 'address_status', 'unknown') if audit_result.validation else 'unknown'
        elementos["nap_consistente"] = (
            ws_status == ConfidenceLevel.VERIFIED.value
            and address_status == ConfidenceLevel.VERIFIED.value
        ) if ws_status else False

        # Redes activas
        if hasattr(audit_result, 'seo_elements') and audit_result.seo_elements:
            elementos["redes_activas"] = audit_result.seo_elements.redes_activas
        else:
            elementos["redes_activas"] = False

        # GBP-derived elements
        if audit_result.gbp:
            elementos["geo_score_gbp"] = audit_result.gbp.geo_score >= 70
            elementos["fotos_gbp"] = bool(getattr(audit_result.gbp, 'photos', 0) >= 3)
            elementos["horario_gbp"] = bool(getattr(audit_result.gbp, 'hours', None))
            elementos["schema_reviews_geo"] = bool(audit_result.gbp.rating)
        else:
            elementos["geo_score_gbp"] = False
            elementos["fotos_gbp"] = False
            elementos["horario_gbp"] = False
            elementos["schema_reviews_geo"] = False

        return elementos

    def _extraer_elementos_aeo(self, audit_result: V4AuditResult) -> dict:
        """Extrae elementos del pilar AEO (Para que te CITEN)."""
        elementos = {}
        if not audit_result:
            return {k: False for k in CHECKLIST_AEO}

        # Schema FAQ
        elementos["schema_faq"] = bool(audit_result.schema.faq_schema_detected) if audit_result.schema else False
        # Open Graph
        if hasattr(audit_result, 'seo_elements') and audit_result.seo_elements:
            elementos["open_graph"] = audit_result.seo_elements.open_graph
            elementos["imagenes_alt_aeo"] = audit_result.seo_elements.imagenes_alt
        else:
            elementos["open_graph"] = False
            elementos["imagenes_alt_aeo"] = False

        # Schema hotel AEO (same source, separate pilar weight)
        elementos["schema_hotel_aeo"] = bool(audit_result.schema.hotel_schema_valid) if audit_result.schema else False

        # Contenido factual: schema valido + tiene horarios/precios
        elementos["contenido_factual"] = (
            audit_result.schema and audit_result.schema.hotel_schema_valid
            and bool(getattr(audit_result.gbp, 'hours', None) if audit_result.gbp else False)
        )

        # Speakable schema (nuevo, default False - sin detector aun)
        elementos["speakable_schema"] = False

        return elementos

    def _extraer_elementos_iao(self, audit_result: V4AuditResult) -> dict:
        """Extrae elementos del pilar IAO (Para que te RECOMIENDEN)."""
        elementos = {}
        if not audit_result:
            return {k: False for k in CHECKLIST_IAO}

        # Citability score
        elementos["citability_score"] = (
            hasattr(audit_result, 'citability') and audit_result.citability
            and audit_result.citability.overall_score is not None
            and audit_result.citability.overall_score > 50
        )

        # Contenido extenso
        elementos["contenido_extenso"] = (
            hasattr(audit_result, 'citability') and audit_result.citability
            and audit_result.citability.overall_score is not None
            and audit_result.citability.overall_score > 50
        )

        # LLMS.txt (nuevo, default False - sin detector aun)
        elementos["llms_txt_exists"] = False

        # Crawler access (nuevo, default False - sin detector aun)
        elementos["crawler_access"] = False

        # Brand signals (nuevo, default False - sin detector aun)
        elementos["brand_signals"] = False

        # GA4 indirect (nuevo, default False - sin detector aun)
        elementos["ga4_indirect"] = False

        # Schema advanced (nuevo, default False - sin detector aun)
        elementos["schema_advanced"] = False

        return elementos

    def _extraer_elementos_de_audit(self, audit_result: V4AuditResult) -> dict:
        """
        Wrapper backward-compat: llama las 4 funciones de pilar y combina.

        RETORNA:
            dict con todos los elementos de los 4 pilares (backward compat).
            Los elementos originales del CHECKLIST_IAO se mantienen para
            que calcular_cumplimiento() siga funcionando.

        VALIDAR CON: CHECKLIST_SEO/GEO/AEO/IAO keys + ELEMENTO_KB_TO_PAIN_ID.keys()
        """
        seo = self._extraer_elementos_seo(audit_result)
        geo = self._extraer_elementos_geo(audit_result)
        aeo = self._extraer_elementos_aeo(audit_result)
        iao = self._extraer_elementos_iao(audit_result)

        # Combinar todos (4 pilares)
        elementos = {}
        elementos.update(seo)
        elementos.update(geo)
        elementos.update(aeo)
        elementos.update(iao)

        # Backward compat: asegurar que los 12 elementos originales existan
        if not audit_result:
            for elem in ELEMENTO_KB_TO_PAIN_ID.keys():
                elementos[elem] = False
        else:
            for elem in ELEMENTO_KB_TO_PAIN_ID.keys():
                if elem not in elementos:
                    elementos[elem] = False

        return elementos
    
    def _asset_para_pain(self, pain_id: str) -> Optional[str]:
        """
        Retorna el asset principal para un pain_id, o None si es MISSING/inexistente.
        
        Util para filtrar pain_ids antes de pasarlos a la propuesta:
        - Si retorna None → el pain tiene asset MISSING → NO se monetiza
        - Si retorna un string → el asset esta IMPLEMENTED → SI se monetiza
        """
        from .pain_solution_mapper import PainSolutionMapper
        from modules.asset_generation.asset_catalog import is_asset_implemented
        mapping = PainSolutionMapper.PAIN_SOLUTION_MAP.get(pain_id, {})
        assets = mapping.get("assets", [])
        if not assets:
            return None
        return assets[0] if is_asset_implemented(assets[0]) else None
    
    def _identify_brechas(self, audit_result: V4AuditResult) -> List[Dict[str, Any]]:
        """
        Identify N brechas (gaps) from audit results based on real evidence.
        
        RETORNA:
            List[Dict] con campos: pain_id, nombre, impacto, detalle
            - pain_id: conecta con PainSolutionMapper
            - nombre: narrativa comercial para el cliente
            - impacto: peso para calculo de perdida (0.0-1.0)
            - detalle: explicacion tecnica
        
        NOTA: brechas[] alimenta pain_ids en DiagnosticSummary.
              faltantes[] viene de _extraer_elementos_de_audit() por separado.
              Retorna TODAS las brechas detectadas (0 a 10+), sin relleno artificial.
        """
        # Cache: audit_result es inmutable durante generate(), resultado idéntico (FASE-H)
        if hasattr(self, '_cached_brechas') and self._cached_brechas is not None:
            return self._cached_brechas

        brechas = []
        
        # Guard against None
        if not audit_result:
            return brechas
        
        # Brecha 1: Visibilidad GBP/GEO
        if not audit_result.gbp or not audit_result.gbp.place_found or audit_result.gbp.geo_score < 60:
            brechas.append({
                'pain_id': 'low_gbp_score',
                'nombre': 'Visibilidad Local (Google Maps)',
                'impacto': 0.30,
                'detalle': '73% de busquedas son "cerca de mi". Su GBP no aparece o esta sub-optimizado. Clientes van a competidores.'
            })
        
        # Brecha 2: Sin Schema de Hotel
        if not audit_result.schema or not audit_result.schema.hotel_schema_detected:
            brechas.append({
                'pain_id': 'no_hotel_schema',
                'nombre': 'Sin Schema de Hotel (Invisible para IA)',
                'impacto': 0.25,
                'detalle': 'ChatGPT, Gemini y Perplexity no pueden "leer" su hotel. Perdida absoluta de reservas de IA.'
            })
        
        # Brecha 3: WhatsApp No Configurado
        # Distinguimos: WhatsApp visual (boton HTML) vs Schema telephone
        if audit_result.validation:
            phone_web = getattr(audit_result.validation, 'phone_web', None)
            raw_whatsapp_html = getattr(audit_result.validation, 'whatsapp_html_detected', None)
            whatsapp_html = raw_whatsapp_html if isinstance(raw_whatsapp_html, bool) else False
            if not phone_web and not whatsapp_html:
                # Ni Schema telephone ni boton HTML → brecha real
                brechas.append({
                    'pain_id': 'no_whatsapp_visible',
                    'nombre': 'Canal Directo Cerrado (Sin WhatsApp)',
                    'impacto': 0.20,
                    'detalle': 'Viajeros quieren reservar instantaneamente. Sin boton WhatsApp, pierden el impulso de compra.'
                })
            # Si whatsapp_html=True pero phone_web=None → boton existe, NO es brecha
        
        # Brecha 4: Performance Web
        if audit_result.performance and audit_result.performance.mobile_score and audit_result.performance.mobile_score < 70:
            brechas.append({
                'pain_id': 'poor_performance',
                'nombre': 'Web Lenta (Abandono Movil)',
                'impacto': 0.15,
                'detalle': f"{audit_result.performance.mobile_score}/100 en velocidad movil. 53% abandona si tarda >3 segundos."
            })
        
        # Brecha 5: Conflictos de Datos
        if audit_result.validation and audit_result.validation.whatsapp_status == ConfidenceLevel.CONFLICT.value:
            brechas.append({
                'pain_id': 'whatsapp_conflict',
                'nombre': 'Datos Inconsistentes (Confusion Cliente)',
                'impacto': 0.10,
                'detalle': 'WhatsApp diferente en web vs Google. Cliente confundido = reserva perdida.'
            })
        
        # Brecha 6: Metadata por Defecto
        if audit_result and audit_result.metadata and audit_result.metadata.has_issues:
            brechas.append({
                'pain_id': 'metadata_defaults',
                'nombre': 'Metadatos por Defecto del CMS',
                'impacto': 0.10,
                'detalle': 'Titulo y descripcion usan valores por defecto.'
            })
        
        # Brecha 7: Reviews Faltantes
        if audit_result.gbp and audit_result.gbp.reviews < 10:
            brechas.append({
                'pain_id': 'missing_reviews',
                'nombre': 'Falta de Reviews',
                'impacto': 0.10,
                'detalle': f"Solo {audit_result.gbp.reviews} reviews en Google."
            })
        
        # Brecha 8: Sin FAQ Schema para Rich Snippets
        if audit_result.schema and not audit_result.schema.faq_schema_detected:
            brechas.append({
                'pain_id': 'no_faq_schema',
                'nombre': 'Sin FAQ para Rich Snippets',
                'impacto': 0.12,
                'detalle': 'Google no puede mostrar sus preguntas frecuentes en resultados. Competidores con FAQ capturan ese trafico.'
            })
        
        # Brecha 9: Sin Open Graph / SEO social
        if audit_result.seo_elements and not getattr(audit_result.seo_elements, 'open_graph', False):
            brechas.append({
                'pain_id': 'no_og_tags',
                'nombre': 'Sin Meta Tags Sociales (Open Graph)',
                'impacto': 0.08,
                'detalle': 'Cuando alguien comparte su hotel en WhatsApp/Facebook, aparece sin imagen ni descripcion atractiva.'
            })
        
        # Brecha 10: Contenido no citable por IA
        citability_score = getattr(audit_result, 'citability', None)
        if citability_score is not None:
            score_val = getattr(citability_score, 'overall_score', None)
            blocks = getattr(citability_score, 'blocks_analyzed', None)

            if isinstance(score_val, (int, float)) and score_val < 30:
                if blocks == 0 or blocks is None:
                    # Caso: contenido ausente/no discoverable (score=0 por default, no evaluacion real)
                    brechas.append({
                        'pain_id': 'low_citability',
                        'nombre': 'Contenido No Discoverable por IA',
                        'impacto': 0.10,
                        'detalle': 'ChatGPT y Perplexity no pueden recomendar su hotel porque el contenido no es discoverable para crawlers de IA.'
                    })
                else:
                    # Caso: contenido existe pero de baja calidad (score real bajo)
                    brechas.append({
                        'pain_id': 'low_citability',
                        'nombre': 'Contenido Poco Estructurado para IA',
                        'impacto': 0.10,
                        'detalle': 'ChatGPT y Perplexity no recomiendan su hotel porque el contenido es insuficiente o poco estructurado.'
                    })
        
        # Priorizar por impacto (todas las detectadas, sin truncamiento ni relleno)
        brechas.sort(key=lambda x: x.get('impacto', 0), reverse=True)

        # Store cache (FASE-H)
        self._cached_brechas = brechas
        return brechas


    # ========================================================
    # FASE-C: Pesos Normalizados + DynamicImpactCalculator
    # ========================================================

    def _normalize_weights(self, brechas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normaliza pesos de brechas para que sumen exactamente 100%.

        Regla: peso_bruto / suma(pesos_brutos) * 100
        Cada brecha recibe peso proporcional a su impacto relativo.
        La suma siempre sera 100%, sin porcion "sin explicar".
        """
        if not brechas:
            return brechas

        total = sum(b.get('impacto', 0) for b in brechas)
        if total == 0:
            # Distribucion equitativa como fallback
            equal_weight = 100.0 / len(brechas)
            for b in brechas:
                b['impacto'] = round(equal_weight, 2)
                b['impacto_raw'] = 0
                b['normalizado'] = True
            return brechas

        for b in brechas:
            raw = b.get('impacto', 0)
            b['impacto_raw'] = raw  # preservar peso original para auditoria
            b['impacto'] = round(raw / total * 100, 2)
            b['normalizado'] = True

        return brechas

    def _map_brecha_to_issue_type(self, brecha_tipo: str) -> str:
        """Mapea tipo de brecha del diagnostico a issue_type del DynamicImpactCalculator."""
        mapping = {
            'low_gbp_score': 'PERFIL_NO_RECLAMADO',
            'no_hotel_schema': 'PERFIL_ABANDONADO',
            'no_whatsapp_visible': 'SIN_WHATSAPP',
            'poor_performance': 'SIN_WEBSITE',
            'whatsapp_conflict': 'SIN_WHATSAPP',
            'metadata_defaults': 'CERO_ACTIVIDAD_RECIENTE',
            'missing_reviews': 'RESENAS_CRITICAS',
            'no_faq_schema': 'SIN_FAQ',
            'no_og_tags': 'FOTOS_INSUFICIENTES',
            'low_citability': 'PERFIL_ABANDONADO',
        }
        return mapping.get(brecha_tipo, '')

    def _get_brecha_pesos(
        self,
        audit_result: V4AuditResult,
        hotel_data: Optional[Dict[str, Any]] = None,
        region: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene pesos de brechas con escalera de fuentes:
        1. DynamicImpactCalculator (si hay hotel_data + region)
        2. _identify_brechas() hardcoded normalizado (fallback)
        """
        brechas = copy.deepcopy(self._identify_brechas(audit_result))

        # Intentar pesos dinamicos si hay datos
        if hotel_data and region:
            try:
                from modules.utils.dynamic_impact import DynamicImpactCalculator
                calc = DynamicImpactCalculator()
                detected_issues = [
                    self._map_brecha_to_issue_type(b.get('pain_id', ''))
                    for b in brechas
                ]
                # Filtrar vacios
                detected_issues = [i for i in detected_issues if i]
                if detected_issues:
                    impact_report = calc.calculate_impacts(region, detected_issues, hotel_data)

                    # Mapear factores de DynamicImpactCalculator a pesos de brechas
                    impact_map = {r.issue_type: r.factor for r in impact_report.impacts}
                    for b in brechas:
                        issue_type = self._map_brecha_to_issue_type(b.get('pain_id', ''))
                        if issue_type in impact_map:
                            b['impacto'] = impact_map[issue_type] * 100  # factor -> porcentaje
                            b['peso_source'] = 'dynamic_impact'
            except Exception:
                pass  # Fallback a pesos hardcoded

        # Siempre normalizar
        brechas = self._normalize_weights(brechas)
        return brechas

    # ========================================================
    # FASE-C: Oportunidad Ponderada (Opportunity Scores)
    # ========================================================

    def _compute_opportunity_scores(
        self,
        audit_result,
        financial_scenarios: FinancialScenarios,
    ) -> Optional[List[Dict[str, Any]]]:
        """Calcula opportunity_scores desde audit_result usando OpportunityScorer.
        
        Retorna None si el scorer no esta disponible o falla (fallback).
        """
        scorer = _get_opportunity_scorer()
        if scorer is None or audit_result is None:
            return None

        try:
            brechas_list = self._identify_brechas(audit_result)
            pain_to_type = {
                'no_faq_schema': 'faq_schema_missing',
                'low_gbp_score': 'low_gbp_score',
                'whatsapp_conflict': 'whatsapp_conflict',
                'metadata_defaults': 'cms_defaults',
                'missing_reviews': 'missing_reviews',
                'poor_performance': 'poor_performance',
                'no_hotel_schema': 'no_hotel_schema',
                'no_whatsapp_visible': 'no_whatsapp_visible',
                'no_og_tags': 'no_og_tags',
                'low_citability': 'low_citability',
            }
            brechas_for_scorer = []
            for b in brechas_list:
                pain_id = b.get('pain_id', '')
                scorer_type = pain_to_type.get(pain_id, 'cms_defaults')
                brechas_for_scorer.append({
                    'id': pain_id,
                    'type': scorer_type,
                    'name': b.get('nombre', pain_id),
                })

            total_loss = None
            if financial_scenarios:
                try:
                    main = financial_scenarios.get_main_scenario()
                    total_loss = main.monthly_loss_max
                except Exception:
                    pass

            from dataclasses import dataclass as _dc
            scores = scorer.score_brechas(
                brechas_for_scorer,
                assessment=None,
                total_monthly_loss=total_loss,
            )

            return [{
                'brecha_id': s.brecha_id,
                'brecha_name': s.brecha_name,
                'severity_score': s.severity_score,
                'effort_score': s.effort_score,
                'impact_score': s.impact_score,
                'total_score': s.total_score,
                'estimated_monthly_cop': s.estimated_monthly_cop,
                'justification': s.justification,
                'rank': s.rank,
            } for s in scores]
        except Exception:
            return None

    def _inject_brecha_scores(
        self,
        audit_result,
        financial_scenarios: FinancialScenarios,
    ) -> Dict[str, str]:
        """Inyecta variables de opportunity_scores para el template.

        Retorna dict con brecha_N_score, brecha_N_severity, etc.
        """
        scores = self._compute_opportunity_scores(audit_result, financial_scenarios)
        # Obtener perdida total del escenario principal para calcular proporcion real
        total_monthly_loss = None
        if financial_scenarios:
            try:
                main = financial_scenarios.get_main_scenario()
                if main:
                    total_monthly_loss = main.monthly_loss_max
            except Exception:
                pass
        result = {}
        scores_count = len(scores) if scores else 0
        for i in range(1, min(scores_count, 10) + 1):
            n = str(i)
            if scores and len(scores) >= i:
                s = scores[i - 1]
                result[f'brecha_{n}_score'] = f"{s['total_score']:.0f}/100"
                result[f'brecha_{n}_severity'] = f"{s['severity_score']:.0f}/40"
                result[f'brecha_{n}_effort'] = f"{s['effort_score']:.0f}/30"
                result[f'brecha_{n}_impact_score'] = f"{s['impact_score']:.0f}/30"
                # Proporcion real de esta brecha sobre la perdida total
                if total_monthly_loss and total_monthly_loss > 0:
                    impacto_pct = (s['estimated_monthly_cop'] / total_monthly_loss) * 100
                    result[f'brecha_{n}_impacto'] = f"{int(impacto_pct)}%"
                else:
                    result[f'brecha_{n}_impacto'] = f"{int(s['impact_score'] / 30 * 100)}%"
                result[f'brecha_{n}_justification'] = s['justification']
                result[f'brecha_{n}_rank'] = f"#{s['rank']}"
                # NOTE: costo, nombre, detalle are set by _get_brecha_*() using real
                # impactos from _identify_brechas(). We do NOT set them here to avoid
                # the dual-source conflict (FASE-G). Score vars only.
            else:
                result[f'brecha_{n}_score'] = ''
                result[f'brecha_{n}_severity'] = ''
                result[f'brecha_{n}_effort'] = ''
                result[f'brecha_{n}_impact_score'] = ''
                result[f'brecha_{n}_justification'] = ''
                result[f'brecha_{n}_rank'] = ''

        return result
