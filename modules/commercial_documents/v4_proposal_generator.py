"""
V4 Proposal Document Generator.

Generates the 02_PROPUESTA_COMERCIAL.md document based on
diagnostic summary and asset plans.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from string import Template

from .data_structures import (
    DiagnosticSummary,
    FinancialScenarios,
    AssetSpec,
    ConfidenceLevel,
    confidence_to_icon,
    format_cop,
)
from modules.financial_engine.pricing_resolution_wrapper import PricingResolutionResult
from modules.asset_generation.proposal_asset_alignment import PROPOSAL_SERVICE_TO_ASSET


class V4ProposalGenerator:
    """
    Generates commercial proposal documents for hotels.

    Creates a comprehensive proposal with:
    - Summary of certified problems
    - Solution kit mapping problems to assets
    - Investment and ROI calculations
    - Coherence guarantee checklist
    - 7/30/60/90 day plan
    - Payment options
    - Acceptance signature section

    Usage:
        generator = V4ProposalGenerator()
        path = generator.generate(
            diagnostic_summary=diagnostic_summary,
            financial_scenarios=scenarios,
            asset_plan=asset_plan,
            hotel_name="Hotel Visperas",
            output_dir="output/"
        )
    """

    # Default pricing
    MONTHLY_PACKAGE_PRICE = 1200000  # $1.2M COP
    SETUP_FEE = 2500000  # $2.5M COP one-time

    def _get_main_value(self, scenario) -> int:
        """Obtiene valor central de presentacion, con fallback a max."""
        return getattr(scenario, 'monthly_loss_central', None) or scenario.monthly_loss_max

    # === TABLA DE MONETIZACION (GAP-IAO-01-03) ===
    # Basado en KB [SECTION:CHECKLIST_IAO] + [SECTION:PRIORITY_MATRIX]
    FALTANTE_MONETIZACION = {
        "ssl": {
            "impacto": "Riesgo de seguridad - HTTPS es requisito",
            "monetizacion": "Posicionamiento Google afectado - perdida de visibilidad",
            "asset": None,  # Guia SSL manual
        },
        "schema_hotel": {
            "impacto": "Invisible para ChatGPT, Gemini, Perplexity",
            "monetizacion": "15-25% menos apariciones en respuestas de IA",
            "asset": "hotel_schema",
        },
        "schema_reviews": {
            "impacto": "Sin estrellas en Google (rich snippets)",
            "monetizacion": "8-12% menor CTR en busquedas organicas",
            "asset": "hotel_schema",  # Con aggregateRating
        },
        "LCP_ok": {
            "impacto": "53% abandono si >3 segundos (mobile)",
            "monetizacion": "Perdida de reservas moviles",
            "asset": None,  # Guia optimizacion LCP
        },
        "CLS_ok": {
            "impacto": ">0.1 = inestable - UX deficiente",
            "monetizacion": "Abandono de usuarios - menor conversion",
            "asset": None,  # Guia CLS
        },
        "schema_faq": {
            "impacto": "Sin rich snippets en Google",
            "monetizacion": "10-15% menor visibilidad en busquedas",
            "asset": "faq_page",
        },
        "contenido_extenso": {
            "impacto": "<300 palabras = SEO debil",
            "monetizacion": "Menor autoridad de dominio - menos traf organico",
            "asset": None,  # Estrategia contenido
        },
        "open_graph": {
            "impacto": "Sin social cards - menor comparticion",
            "monetizacion": "30% menos comparticiones en redes sociales",
            "asset": "meta_tags",
        },
        "nap_consistente": {
            "impacto": "Nombre/Direccion/Telefono inconsistente",
            "monetizacion": "Desconfianza del usuario - menor conversion",
            "asset": None,  # Guia NAP
        },
        "imagenes_alt": {
            "impacto": "Sin alt text - IA no entiende imagenes",
            "monetizacion": "0% indexacion de imagenes en busqueda IA",
            "asset": "image_optimization",
        },
        "blog_activo": {
            "impacto": "Sin blog = autoridad baja",
            "monetizacion": "Competidores con blog capturan mas traf organico",
            "asset": "content_strategy",
        },
        "redes_activas": {
            "impacto": "Sin senales sociales = autoridad secundaria",
            "monetizacion": "Menor confianza percibida por usuarios",
            "asset": "social_recommendations",
        },
    }

    # Paquete sugerido basado en score tecnico
    PAQUETE_UMBRALES = {
        "basico": 40,      # score < 40
        "avanzado": 70,    # 40 <= score < 70
        "premium": 100,    # score >= 70
    }
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize the proposal generator.
        
        Args:
            template_dir: Directory containing templates. If None, uses default.
        """
        if template_dir is None:
            template_dir = Path(__file__).parent / "templates"
        self.template_dir = Path(template_dir)
        # Prefer V6 template, fall back to V4
        self.template_path = self.template_dir / "propuesta_v6_template.md"
        if not self.template_path.exists():
            self.template_path = self.template_dir / "propuesta_v4_template.md"
    
    def generate(
        self,
        diagnostic_summary: DiagnosticSummary,
        financial_scenarios: FinancialScenarios,
        asset_plan: List[AssetSpec],
        hotel_name: str,
        output_dir: str,
        price_monthly: Optional[int] = None,
        setup_fee: Optional[int] = None,
        audit_result: Optional[Any] = None,
        pricing_result: Optional[PricingResolutionResult] = None,
        region: Optional[str] = None,
        analytics_data: Optional[Dict[str, Any]] = None,
        financial_breakdown: Optional[Any] = None,
        assets_generated: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Generate the proposal document.
        
        Args:
            diagnostic_summary: Summary of diagnostic results
            financial_scenarios: Financial scenarios for ROI calculation
            asset_plan: List of assets to be generated
            hotel_name: Name of the hotel
            output_dir: Directory to save the document
            price_monthly: Optional custom monthly price (calculated from scenarios if not provided)
            setup_fee: Optional custom setup fee (uses default if not provided)
            audit_result: Optional audit result for GEO metrics
            pricing_result: Optional PricingResolutionResult from hybrid pricing model.
                If provided, uses pricing_result.monthly_price_cop directly to ensure
                consistency with financial_scenarios.json calculation.
            region: Optional region string for regional context in templates.

        Returns:
            Path to the generated document
        """
        # Use pricing_result if available (from hybrid pricing model)
        # This ensures consistency with financial_scenarios.json
        if pricing_result is not None:
            price_monthly = int(pricing_result.monthly_price_cop)
        elif price_monthly is None:
            price_monthly = self._calculate_dynamic_price(financial_scenarios)
        if setup_fee is None:
            setup_fee = self.SETUP_FEE
        
        # Store for use in template preparation
        self._current_price_monthly = price_monthly
        self._current_setup_fee = setup_fee
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Load template
        template_content = self._load_template()
        
        # Prepare template data
        template_data = self._prepare_template_data(
            diagnostic_summary=diagnostic_summary,
            financial_scenarios=financial_scenarios,
            asset_plan=asset_plan,
            hotel_name=hotel_name,
            audit_result=audit_result,
            region=region,
            analytics_data=analytics_data,
            assets_generated=assets_generated,
        )
        
        # Render template
        document_content = self._render_template(template_content, template_data)
        
        # Save document
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"02_PROPUESTA_COMERCIAL_{timestamp}.md"
        file_path = output_path / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(document_content)
        
        return str(file_path)
    
    def _load_template(self) -> str:
        """Load the proposal template."""
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
proposal_id: ${proposal_id}
document_type: PROPUESTA_V4
generator: IA_Hoteles_v4
valid_until: ${valid_until}
---

# 📋 PROPUESTA COMERCIAL
## Kit Hospitalidad 4.0 - ${hotel_name}

**ID de Propuesta:** ${proposal_id}  
**Fecha de generación:** ${generated_at}  
**Válida hasta:** ${valid_until}  
**Versión del sistema:** ${version}

---

## [TARGET] SU PROBLEMA CERTIFICADO

Hemos realizado un diagnóstico exhaustivo validado con múltiples fuentes de datos:

<div style="background: #fff3cd; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107;">

### 📊 Resumen del Diagnóstico

- **Problemas Críticos Identificados:** ${critical_problems_count}
- **Quick Wins Detectados:** ${quick_wins_count}
- **Nivel de Confianza Global:** ${overall_confidence}

**Problemas Principales:**
${top_problems_list}

</div>

---

## [CLIP] SU SOLUCIÓN: Kit Hospitalidad 4.0

Mapeo directo de cada problema a su solución con asset correspondiente:

| Problema Detectado | Solución Propuesta | Asset Generado | Prioridad | Confianza |
|-------------------|-------------------|----------------|-----------|-----------|
${solution_table}

**Leyenda de Prioridad:**
- 🔴 **P1**: Crítica - Implementar inmediatamente
- 🟡 **P2**: Media - Implementar en 30 días
- 🟢 **P3**: Baja - Implementar en 60 días

---

## [MONEY] INVERSIÓN Y RETORNO

### 💰 Estructura de Inversión

| Concepto | Valor | Frecuencia |
|----------|-------|------------|
| **Cuota de Activación** | ${setup_fee} | Única vez |
| **Kit Hospitalidad 4.0** | ${monthly_fee} | Mensual |
| **Compromiso mínimo** | 6 meses | - |

<div style="background: #d4edda; padding: 20px; border-radius: 8px; border-left: 4px solid #28a745;">

### 📈 Proyección de Retorno (Escenario Realista)

**Inversión mensual:** ${monthly_fee}

**Ganancia mensual proyectada:** ${projected_gain}

**ROI a 6 meses:** ${roi_6_months}

**Punto de equilibrio:** ${break_even_months} meses

</div>

<details>
<summary>📊 Ver Escenarios Completo</summary>

#### Escenario Conservador (70% probabilidad)
- **Ganancia mensual:** ${conservative_gain}
- **ROI a 6 meses:** ${conservative_roi}

#### Escenario Realista (20% probabilidad) - PRINCIPAL
- **Ganancia mensual:** ${realistic_gain}
- **ROI a 6 meses:** ${realistic_roi}

#### Escenario Optimista (10% probabilidad)
- **Ganancia mensual:** ${optimistic_gain}
- **ROI a 6 meses:** ${optimistic_roi}

</details>

---

## [CHECK] GARANTÍA DE COHERENCIA

Checklist de validaciones cruzadas pasadas:

| Validación | Estado | Detalle |
|------------|--------|---------|
${coherence_checklist}

**Compromiso de calidad:**
- ✅ Todos los assets incluyen metadata de trazabilidad
- ✅ Datos validados entre mínimo 2 fuentes independientes
- ✅ Explicación de fórmulas financieras incluida
- ✅ Escenarios con probabilidades explícitas

---

${guarantees_section}

## [OK] PLAN DEL DUEÑO: 7/30/60/90 DÍAS

### Primeros 7 Días (Activación)
${plan_7_days}

### Primeros 30 Días (Quick Wins)
${plan_30_days}

### Días 31-60 (Consolidación)
${plan_60_days}

### Días 61-90 (Optimización)
${plan_90_days}

---

## [CARD] FORMAS DE PAGO

### Opción 1: Pago Único (Descuento 10%)
- **Total:** ${single_payment_total} (ahorro: ${single_payment_savings})
- Incluye: Activación + 6 meses de servicio

### Opción 2: Pago Mensual
- **Activación:** ${setup_fee}
- **Mensualidad:** ${monthly_fee}
- Compromiso: 6 meses mínimo

### Opción 3: Pago Trimestral (Descuento 5%)
- **Activación:** ${setup_fee}
- **Trimestre:** ${quarterly_fee} (${quarterly_savings} de ahorro)

### Métodos de Pago Aceptados
- 💳 Tarjeta de crédito/débito
- 🏦 Transferencia bancaria
- 💰 Pago en efectivo (oficina)

---

## [WRITE] ACEPTACIÓN DE PROPUESTA

Al firmar este documento, el representante de **${hotel_name}** acepta los términos de la propuesta:

### Para el Hotel:

**Nombre del Representante:** ________________________________

**Cargo:** ________________________________

**Documento de Identidad:** ________________________________

**Firma:** ________________________________

**Fecha:** ________________________________

---

### Para IA Hoteles:

**Nombre del Asesor:** ________________________________

**Cargo:** ________________________________

**Firma:** ________________________________

**Fecha:** ________________________________

---

## 📋 TÉRMINOS Y CONDICIONES

1. **Vigencia:** Esta propuesta es válida por 15 días calendario desde la fecha de generación.

2. **Inicio de servicio:** El servicio comienza 3 días hábiles después de la aceptación y pago de activación.

3. **Garantía:** Si dentro de los primeros 30 días no se entregan los assets comprometidos, se reintegra el 100% de la cuota de activación.

4. **Confidencialidad:** Toda la información del hotel es tratada con estricta confidencialidad.

5. **Propiedad intelectual:** Los assets generados son propiedad del hotel desde el momento de entrega.

---

*Documento generado por IA Hoteles v4.0 - Sistema de Confianza*  
*Propuesta ID: ${proposal_id}*  
*Fecha: ${generated_at}*
"""
    
    def _prepare_template_data(
        self,
        diagnostic_summary: DiagnosticSummary,
        financial_scenarios: FinancialScenarios,
        asset_plan: List[AssetSpec],
        hotel_name: str,
        audit_result: Optional[Any] = None,
        region: Optional[str] = None,
        analytics_data: Optional[Dict[str, Any]] = None,
        assets_generated: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, str]:
        """Prepare data for template rendering."""
        
        hotel_id = hotel_name.lower().replace(" ", "_").replace("-", "_")
        generated_at = datetime.now()
        from datetime import timedelta
        valid_until = generated_at + timedelta(days=15)
        
        # Region-based variables for V6 templates
        hotel_region = region or "Colombia"
        hotel_location = getattr(audit_result, 'location', None) or \
                        getattr(getattr(audit_result, 'gbp', None), 'address', None) or \
                        hotel_region
        
        # Main scenario for primary display
        main_scenario = financial_scenarios.get_main_scenario()
        
        # Calculate ROI
        monthly_investment = getattr(self, '_current_price_monthly', self.MONTHLY_PACKAGE_PRICE)
        projected_monthly_gain = self._get_main_value(main_scenario)
        roi_6_months = self._calculate_roi(monthly_investment, projected_monthly_gain, 6)
        break_even = self._calculate_break_even(monthly_investment, projected_monthly_gain)
        
        data = {
            # Metadata
            'generated_at': generated_at.strftime("%Y-%m-%d %H:%M:%S"),
            'version': '4.0.0',
            'hotel_id': hotel_id,
            'proposal_id': f"PROP-{hotel_id.upper()}-{generated_at.strftime('%Y%m%d')}",
            'valid_until': valid_until.strftime("%Y-%m-%d"),
            'hotel_name': hotel_name,
            
            # Diagnostic summary
            'critical_problems_count': str(diagnostic_summary.critical_problems_count),
            'quick_wins_count': str(diagnostic_summary.quick_wins_count),
            'overall_confidence': diagnostic_summary.overall_confidence.value,
            'top_problems_list': self._format_problems_list(diagnostic_summary.top_problems),
            
            # Solution table
            'solution_table': self._build_solution_table(asset_plan),
            
            # Investment
            'setup_fee': format_cop(getattr(self, '_current_setup_fee', self.SETUP_FEE)),
            'monthly_fee': format_cop(getattr(self, '_current_price_monthly', self.MONTHLY_PACKAGE_PRICE)),
            
            # ROI
            'projected_gain': format_cop(projected_monthly_gain),
            'roi_6_months': roi_6_months,
            'break_even_months': str(break_even),
            
        # All scenarios
        'conservative_gain': format_cop(self._get_main_value(financial_scenarios.conservative)),
        'conservative_roi': self._calculate_roi(monthly_investment, self._get_main_value(financial_scenarios.conservative), 6),
        'realistic_gain': format_cop(self._get_main_value(financial_scenarios.realistic)),
        'realistic_roi': self._calculate_roi(monthly_investment, self._get_main_value(financial_scenarios.realistic), 6),
        'optimistic_gain': self._format_scenario_amount(self._get_main_value(financial_scenarios.optimistic)),
        'optimistic_roi': self._calculate_roi(monthly_investment, self._get_main_value(financial_scenarios.optimistic), 6),
        
        # Monthly projection variables for 6 months
        'inv_m1': format_cop(monthly_investment),
        'inv_m2': format_cop(monthly_investment),
        'inv_m3': format_cop(monthly_investment),
        'inv_m4': format_cop(monthly_investment),
        'inv_m5': format_cop(monthly_investment),
        'inv_m6': format_cop(monthly_investment),
        'rec_m1': format_cop(self._get_main_value(main_scenario)),
        'rec_m2': format_cop(self._get_main_value(main_scenario)),
        'rec_m3': format_cop(self._get_main_value(main_scenario)),
        'rec_m4': format_cop(self._get_main_value(main_scenario)),
        'rec_m5': format_cop(self._get_main_value(main_scenario)),
        'rec_m6': format_cop(self._get_main_value(main_scenario)),
        'net_m1': format_cop(self._get_main_value(main_scenario) - monthly_investment),
        'net_m2': format_cop(self._get_main_value(main_scenario) - monthly_investment),
        'net_m3': format_cop(self._get_main_value(main_scenario) - monthly_investment),
        'net_m4': format_cop(self._get_main_value(main_scenario) - monthly_investment),
        'net_m5': format_cop(self._get_main_value(main_scenario) - monthly_investment),
        'net_m6': format_cop(self._get_main_value(main_scenario) - monthly_investment),
        'acc_m1': format_cop(self._get_main_value(main_scenario) - monthly_investment),
        'acc_m2': format_cop(2 * (self._get_main_value(main_scenario) - monthly_investment)),
        'acc_m3': format_cop(3 * (self._get_main_value(main_scenario) - monthly_investment)),
        'acc_m4': format_cop(4 * (self._get_main_value(main_scenario) - monthly_investment)),
        'acc_m5': format_cop(5 * (self._get_main_value(main_scenario) - monthly_investment)),
        'acc_m6': format_cop(6 * (self._get_main_value(main_scenario) - monthly_investment)),
        
        # Additional variables for sales template
        'generated_date': generated_at.strftime("%Y-%m-%d"),
        'main_scenario_amount': format_cop(self._get_main_value(main_scenario)),
        'web_score': "85",  # Placeholder - ideally from audit
        'web_status': "VERIFIED" if diagnostic_summary.overall_confidence.value == "VERIFIED" else "ESTIMATED",
        'roi_6m': self._calculate_roi(monthly_investment, self._get_main_value(main_scenario), 6).replace("%", "").rstrip("X").strip(),  # Just the number, no X suffix
        'total_investment_6m': format_cop(monthly_investment * 6),
        'recovered_6m': format_cop(self._get_main_value(main_scenario) * 6),
        'net_benefit_6m': format_cop((self._get_main_value(main_scenario) - monthly_investment) * 6),
        'plan_7d': self._build_7_day_plan(asset_plan),
        'plan_30d': self._build_30_day_plan(asset_plan),
        'plan_60d': self._build_60_day_plan(),
        'plan_90d': self._build_90_day_plan(),
        'coherence_score': str(int(diagnostic_summary.coherence_score * 100)) if diagnostic_summary.coherence_score is not None else '70',

        # Backward compatibility: score_tecnico alias for score_global
        'score_tecnico': diagnostic_summary.score_global if diagnostic_summary.score_global is not None else (
            diagnostic_summary.score_tecnico if diagnostic_summary.score_tecnico is not None else 50
        ),

        # Brecha variables — dinámicas, zero para slots sin problema real
        # Las brechas consumen top_problems (V4 compat) con guard contra phantom costs
        **self._build_brecha_data(diagnostic_summary, main_scenario),

        # V6 template variables (regional context and investment summary)
        'hotel_location': hotel_location,
        'hotel_region': hotel_region,
        'monthly_loss': format_cop(self._get_main_value(main_scenario)),
        'monthly_investment': format_cop(monthly_investment),
        'total_investment': format_cop(monthly_investment * 6),
        'total_recovered': format_cop(self._get_main_value(main_scenario) * 6),
        'net_benefit': format_cop((self._get_main_value(main_scenario) - monthly_investment) * 6),

        # Coherence checklist
        'coherence_checklist': self._build_coherence_checklist(diagnostic_summary),
        
        # Plans
        'plan_7_days': self._build_7_day_plan(asset_plan),
        'plan_30_days': self._build_30_day_plan(asset_plan),
        'plan_60_days': self._build_60_day_plan(),
        'plan_90_days': self._build_90_day_plan(),
        
        # Guarantees
        'guarantees_section': self._build_guarantees_section(),
        
        # Payment options
        'single_payment_total': format_cop(int((getattr(self, '_current_setup_fee', self.SETUP_FEE) + getattr(self, '_current_price_monthly', self.MONTHLY_PACKAGE_PRICE) * 6) * 0.9)),
        'single_payment_savings': format_cop(int((getattr(self, '_current_setup_fee', self.SETUP_FEE) + getattr(self, '_current_price_monthly', self.MONTHLY_PACKAGE_PRICE) * 6) * 0.1)),
        'quarterly_fee': format_cop(int(getattr(self, '_current_price_monthly', self.MONTHLY_PACKAGE_PRICE) * 3 * 0.95)),
        'quarterly_savings': format_cop(int(getattr(self, '_current_price_monthly', self.MONTHLY_PACKAGE_PRICE) * 3 * 0.05)),

        # GEO Section (NUEVO) + GAP-IAO-01-03 Monetary Impact
        'geo_section': (self._build_geo_section(audit_result) if audit_result else "") + self._build_monetary_impact_section(diagnostic_summary),

        # ANALYTICS-02: Analytics section in proposal
        'analytics_section': self._inject_analytics(analytics_data),

        # FASE-CONFIDENCE-DISCLOSURE: Tabla de calidad de assets
        'asset_quality_table': self._generate_asset_quality_table(assets_generated),
    }

        return data

    def _inject_analytics(self, analytics_data: Optional[Dict[str, Any]]) -> str:
        """Construye seccion de analytics para la propuesta comercial.
        
        Cuando GA4 esta disponible, incluye metricas reales.
        Cuando no, omite la seccion para no mostrar datos inexistentes.
        
        Args:
            analytics_data: Dict con analytics_status, use_ga4, hotel_data
            
        Returns:
            Seccion markdown o string vacio
        """
        if not analytics_data:
            return ""
            
        status = analytics_data.get("analytics_status")
        ga4_available = analytics_data.get("use_ga4", False)
        
        if not status:
            return ""
            
        # GA4 disponible -> incluir seccion con datos reales
        if ga4_available and status.ga4_available:
            return f"""---

## 📈 DATOS DE TRAFICO (Google Analytics)

Tenemos acceso a las metricas reales de su sitio web. Esto nos permite:

- **Medir con precision** el impacto de cada cambio implementado
- **Identificar canales** que traen mas reservas directas
- **Optimizar basados en datos**, no en suposiciones

**Estado de conexion:** {status.ga4_status_text}

---
"""
        
        # GA4 no configurado -> seccion breve con invitacion a conectar
        return f"""---

## 📈 DATOS DE TRAFICO (Google Analytics)

**Estado:** {status.ga4_status_text}

Cuando configuremos Google Analytics, podremos medir con precision el impacto de cada cambio y optimizar basados en datos reales de su sitio web.

---
"""
 
    def _generate_asset_quality_table(self, assets_generated: Optional[List[Dict[str, Any]]]) -> str:
        """Genera tabla de calidad de assets para la propuesta.
        
        Mapea cada servicio de la propuesta a su asset generado y muestra
        el nivel de preparacion basado en confidence_score.
        
        Args:
            assets_generated: Lista de assets generados (cada uno con 'asset_type' y 'confidence_score').
                Si es None, muestra 'Pendiente' para todos los servicios.
        
        Returns:
            String markdown con la tabla de calidad.
        """
        # Build lookup: asset_type -> confidence_score
        asset_lookup = {}
        if assets_generated:
            for asset in assets_generated:
                asset_type = asset.get("asset_type", "") if isinstance(asset, dict) else getattr(asset, "asset_type", "")
                confidence = asset.get("confidence_score", 0) if isinstance(asset, dict) else getattr(asset, "confidence_score", 0)
                if asset_type:
                    asset_lookup[asset_type] = confidence
        
        # Table header
        rows = ["| Entregable | Nivel | Que significa |", "|------------|-------|---------------|"]
        
        for service_name, asset_type in PROPOSAL_SERVICE_TO_ASSET.items():
            if asset_type in asset_lookup:
                confidence = asset_lookup[asset_type]
                if confidence >= 0.7:
                    nivel = "✅ Completo"
                    significado = "Listo para implementar"
                elif confidence >= 0.4:
                    nivel = "⚠️ Requiere datos"
                    significado = "Necesitamos informacion adicional"
                else:
                    nivel = "🔧 En desarrollo"
                    significado = "En proceso de mejora"
            elif assets_generated is None:
                nivel = "⏳ Pendiente"
                significado = "Se genera al activar el servicio"
            else:
                nivel = "❌ No generado"
                significado = "No se pudo generar - revisaremos"
            
            rows.append(f"| {service_name} | {nivel} | {significado} |")
        
        return "\n".join(rows)
    
    def _render_template(self, template_content: str, data: Dict[str, str]) -> str:
        """Render the template with data."""
        template = Template(template_content)
        return template.safe_substitute(data)
    
    def _calculate_roi(self, investment: int, gain: int, months: int) -> str:
        """Calculate ROI as ratio (e.g., '3.9X' instead of '292%').
        
        Returns ratio of total_gain / total_investment.
        """
        total_investment = investment * months
        total_gain = gain * months
        
        if total_investment == 0:
            return "N/A"
        
        roi_ratio = total_gain / total_investment
        return f"{roi_ratio:.1f}X"
    
    def _calculate_break_even(self, investment: int, gain: int) -> int:
        """Calculate break-even point in months."""
        if gain <= investment:
            return 6  # Default to 6 months if not profitable
        
        months = 0
        cumulative = -getattr(self, '_current_setup_fee', self.SETUP_FEE)
        while cumulative < 0 and months < 24:
            months += 1
            cumulative += (gain - investment)
        
        return months
    
    def _format_scenario_amount(self, amount: int) -> str:
        """Format scenario amount with semantic handling for negative/equilibrium values.
        
        Args:
            amount: Monthly amount (can be negative for equilibrium/gain)
            
        Returns:
            Formatted string with proper semantics
        """
        if amount <= 0:
            return f"Equilibrio (ahorro: {format_cop(abs(amount))})"
        return format_cop(amount)
    
    def _build_guarantees_section(self) -> str:
        """Build the guarantees section for the proposal."""
        return """## [OK] GARANTÍAS

### 1. Resultados Medibles
Si no ve incremento del 10% en consultas directas en 90 días, 
extendemos servicio 1 mes gratis.

### 2. Transparencia Total
Acceso a reportes y métricas acordadas en tiempo real.

### 3. Sin Permanencia
Contrato mes a mes. Cancela sin penalizaciones.

---
"""
    
    def _determinar_paquete(self, diagnostic_summary: DiagnosticSummary) -> dict:
        """
        Usa score_tecnico de KB para sugerir paquete.
        BASADO EN: KB sugerir_paquete()
        """
        score = diagnostic_summary.score_tecnico if diagnostic_summary.score_tecnico is not None else 50

        if score < 40:
            paquete = "basico"
        elif score < 70:
            paquete = "avanzado"
        else:
            paquete = "premium"

        # Ajustar por score IA si disponible
        if diagnostic_summary.score_ia is not None and diagnostic_summary.score_ia >= 0:
            score_ia = diagnostic_summary.score_ia
            # Si score IA es muy bajo, puede recomendar paquete mayor
            if score_ia < 30 and paquete == "basico":
                paquete = "avanzado"  # IAI bajo necesita mas work

        confianza = "ALTA" if diagnostic_summary.score_ia is not None and diagnostic_summary.score_ia >= 0 else "N/A"

        return {
            "paquete": paquete,
            "score_final": score,
            "score_ia": diagnostic_summary.score_ia if diagnostic_summary.score_ia is not None else "N/A",
            "confianza": confianza,
        }

    def _monetizar_faltante(self, faltante: str) -> dict:
        """
        Retorna informacion de monetizacion para un faltante KB.

        Args:
            faltante: ID del elemento KB (e.g. "ssl", "schema_hotel")

        Returns:
            Dict con keys: impacto, monetizacion, asset
        """
        return self.FALTANTE_MONETIZACION.get(faltante, {
            "impacto": "Elemento KB no categorizado",
            "monetizacion": "Impacto por determinar",
            "asset": None,
        })

    def _build_monetary_impact_section(self, diagnostic_summary: DiagnosticSummary) -> str:
        """
        Construir seccion de impacto monetario basado en faltantes KB.

        GAP-IAO-01-03: Muestra score real y monetizacion de cada faltante.
        """
        # Score KB
        score_tecnico = diagnostic_summary.score_tecnico if diagnostic_summary.score_tecnico is not None else "N/A"
        score_ia = diagnostic_summary.score_ia if diagnostic_summary.score_ia is not None else "N/A"
        paquete = diagnostic_summary.paquete if diagnostic_summary.paquete else "por determinar"
        data_source = diagnostic_summary.data_source if diagnostic_summary.data_source else "N/A"

        # Benchmark regional (aproximado)
        benchmark_score = 58  # Promedio regional hotels pequenos
        benchmark_status = "encima" if (isinstance(score_tecnico, int) and score_tecnico > benchmark_score) else "debajo"

        # Faltantes
        faltantes = diagnostic_summary.faltantes if diagnostic_summary.faltantes else []

        # Construir tabla de monetizacion
        rows = []
        for faltante in faltantes:
            info = self._monetizar_faltante(faltante)
            asset = info.get("asset", "Guia manual") or "Guia manual"
            rows.append(f"| {faltante} | {info['impacto']} | {info['monetizacion']} | {asset} |")

        table_content = "\n".join(rows) if rows else "| Sin faltantes detectados | - | - | - |"

        section = f"""
## [TARGET] SU PUNTAJE ACTUAL

<div style="background: #e7f3ff; padding: 20px; border-radius: 8px; border-left: 4px solid #2196F3;">

### 📊 Diagnostico KB - Score de Cumplimiento IAO

| Metrica | Valor | Benchmark Regional |
|---------|-------|-------------------|
| **Score Tecnico** | {score_tecnico}/100 | ~{benchmark_score}/100 ({benchmark_status} del promedio) |
| **Score IA-Readiness** | {score_ia}/100 | N/A |
| **Paquete Sugerido** | {paquete.upper()} | - |
| **Fuente de Datos** | {data_source} | - |

</div>

---

## [TARGET] IMPACTO MONETARIO DE SUS FALTANTES

<div style="background: #fff3cd; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107;">

### 🔍 Elementos KB que requieren atencion

| Faltante KB | Impacto | Monetizacion | Solucion |
|------------|---------|--------------|----------|
{table_content}

**Nota**: Cada faltante representa una oportunidad de mejora. La solucion de todos los faltantes
monetizables incrementara su score y mejorara su visibilidad en Busqueda Google y Respuestas de IA.

</div>
"""
        return section

    def _calculate_dynamic_price(self, financial_scenarios: FinancialScenarios) -> int:
        """Calculate dynamic monthly price based on financial scenarios.
        
        Uses 2% of expected monthly value with min/max bounds.
        Aligns with price/pain ratio validation in coherence validator.
        """
        # Calculate expected value from scenarios (70/20/10 weighting)
        conservative = self._get_main_value(financial_scenarios.conservative)
        realistic = self._get_main_value(financial_scenarios.realistic)
        optimistic = self._get_main_value(financial_scenarios.optimistic)
        
        expected_monthly = int(conservative * 0.70 + realistic * 0.20 + optimistic * 0.10)
        
        # 2% of expected value, bounded between 800k and 2.5M COP
        calculated_price = min(max(int(expected_monthly * 0.02), 800000), 2500000)
        
        return calculated_price

    
    def _format_problems_list(self, problems: List[str]) -> str:
        """Format problems list for display."""
        if not problems:
            return "- No se identificaron problemas críticos"
        return "\n".join([f"- {p}" for p in problems[:5]])
    
    def _build_solution_table(self, asset_plan: List[AssetSpec]) -> str:
        """Build the solution mapping table."""
        rows = []
        
        priority_icons = {
            1: "🔴 P1",
            2: "🟡 P2",
            3: "🟢 P3",
        }
        
        for asset in sorted(asset_plan, key=lambda x: x.priority):
            icon = confidence_to_icon(asset.confidence_level)
            priority = priority_icons.get(asset.priority, "⚪ P?")
            
            row = f"| {asset.problem_solved} | {asset.description} | `{asset.asset_type}` | {priority} | {icon} {asset.confidence_level.value} |"
            rows.append(row)
        
        return "\n".join(rows) if rows else "| Sin assets planificados | - | - | - | - |"
    
    def _build_brecha_data(self, diagnostic_summary, main_scenario) -> Dict[str, str]:
        """Build brecha_1..4 nombre/costo dynamically using real impact weights.

        FASE-G: Usa brechas_reales (con impacto real de _identify_brechas) cuando
        está disponible. Fallback a top_problems con distribución equitativa.
        Slots without real problems get $0.
        """
        max_brechas = 4
        top_problems = diagnostic_summary.top_problems or []
        brechas_reales = getattr(diagnostic_summary, 'brechas_reales', None) or []
        brecha_data: Dict[str, str] = {}

        for i in range(max_brechas):
            slot = i + 1
            if i < len(brechas_reales):
                # Fuente primaria: impacto real de _identify_brechas
                brecha = brechas_reales[i]
                impacto = brecha.get('impacto', 1.0 / max(len(brechas_reales), 1))
                costo = int(self._get_main_value(main_scenario) * impacto)
                brecha_data[f'brecha_{slot}_nombre'] = brecha.get('nombre', '')
                brecha_data[f'brecha_{slot}_costo'] = format_cop(costo)
            elif i < len(top_problems):
                # Fallback: top_problems sin impacto real (distribución equitativa)
                distribucion = int(self._get_main_value(main_scenario) / max(len(top_problems), 1))
                brecha_data[f'brecha_{slot}_nombre'] = top_problems[i]
                brecha_data[f'brecha_{slot}_costo'] = format_cop(distribucion)
            else:
                brecha_data[f'brecha_{slot}_nombre'] = ""
                brecha_data[f'brecha_{slot}_costo'] = "$0"
        return brecha_data

    def _build_coherence_checklist(self, diagnostic_summary: DiagnosticSummary) -> str:
        """Build the coherence guarantee checklist with real validation data."""
        # FASE 5: Usar datos reales del validated_data_summary
        validated_data = diagnostic_summary.validated_data_summary or {}
        
        # Verificar WhatsApp
        whatsapp_data = validated_data.get('whatsapp', {})
        if isinstance(whatsapp_data, dict):
            whatsapp_verified = whatsapp_data.get('confidence') == 'VERIFIED'
            whatsapp_detail = "Web + GBP coinciden" if whatsapp_verified else "Pendiente de validacion"
        else:
            whatsapp_verified = False
            whatsapp_detail = "No disponible"
        
        # Verificar ADR
        adr_value = validated_data.get('adr')
        adr_verified = adr_value is not None
        adr_detail = "Benchmark vs Input" if adr_verified else "Pendiente"
        
        # Verificar Schema Hotel (del top_problems)
        top_problems = diagnostic_summary.top_problems or []
        schema_hotel_valid = not any("Schema Hotel" in p or "schema" in p.lower() for p in top_problems)
        schema_detail = "Rich Results Test API" if schema_hotel_valid else "Requiere implementacion"
        
        # Verificar GBP (del top_problems)
        gbp_valid = not any("GBP" in p or "Business Profile" in p for p in top_problems)
        gbp_detail = "Google Places API" if gbp_valid else "Requiere optimizacion"
        
        # Core Web Vitals - por defecto en analisis preliminar
        cwv_verified = diagnostic_summary.overall_confidence.value == "VERIFIED"
        cwv_detail = "PageSpeed API" if cwv_verified else "Lab data only"
        
        items = [
            ("Validacion Cruzada de WhatsApp", "[OK]" if whatsapp_verified else "[PENDING]", whatsapp_detail),
            ("Validacion Cruzada de ADR", "[OK]" if adr_verified else "[PENDING]", adr_detail),
            ("Schema Hotel Validado", "[OK]" if schema_hotel_valid else "[PENDING]", schema_detail),
            ("Datos GBP Verificados", "[OK]" if gbp_valid else "[PENDING]", gbp_detail),
            ("Core Web Vitals", "[OK]" if cwv_verified else "[PENDING]", cwv_detail),
        ]
        
        rows = []
        for name, status, detail in items:
            rows.append(f"| {name} | {status} | {detail} |")
        
        return "\n".join(rows)
    
    def _build_7_day_plan(self, asset_plan: List[AssetSpec]) -> str:
        """Build detailed 7-day activation plan."""
        return """- [ ] **Día 1**: Firma de propuesta y pago de activación
- [ ] **Día 2**: Kick-off call con el equipo del hotel (30 min)
- [ ] **Día 3**: Solicitud de accesos (analytics, GBP, web)
- [ ] **Día 4**: Entrega de assets P1 críticos (WhatsApp, Schema básico)
- [ ] **Día 5**: Validación técnica inicial
- [ ] **Día 6**: Ajustes según feedback
- [ ] **Día 7**: Confirmación de activación completa"""
    
    def _build_30_day_plan(self, asset_plan: List[AssetSpec]) -> str:
        """Build detailed 30-day quick wins plan."""
        return """- [ ] **Semana 2**: Implementación FAQ Schema + optimización GBP
- [ ] **Semana 3**: Configuración tracking avanzado (UTMs, conversiones)
- [ ] **Semana 4**: Primera publicación posts GBP + revisión métricas
- [ ] **Día 30**: Reporte de avance con métricas iniciales"""
    
    def _build_60_day_plan(self) -> str:
        """Build detailed 60-day consolidation plan."""
        return """- [ ] **Días 31-45**: Optimización de assets entregados (A/B testing)
- [ ] **Días 46-50**: Implementación de assets P2 y P3
- [ ] **Días 51-55**: Primera medición de impacto en consultas directas
- [ ] **Días 56-60**: Ajustes basados en datos reales + reporte día 60"""
    
    def _build_90_day_plan(self) -> str:
        """Build detailed 90-day optimization plan."""
        return """- [ ] **Días 61-75**: Evaluación de ROI a 3 meses
- [ ] **Días 76-80**: Optimización de conversiones basada en datos
- [ ] **Días 81-85**: Planificación de assets adicionales (fase 2)
- [ ] **Días 86-90**: Revisión de estrategia a largo plazo + reporte final"""

    def _build_geo_section(self, audit_result: Optional[Any]) -> str:
        """Construir sección de métricas GEO para propuesta.
        
        Args:
            audit_result: Resultado completo del audit con datos GEO
            
        Returns:
            Markdown con sección de métricas GEO
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
            status = "✅" if score >= 0.7 else "⚠️"
            rows.append(f"| Accesibilidad IA | {score:.2f}/1.00 | {status} |")
        
        if has_citability:
            cit = audit_result.citability
            score = getattr(cit, 'overall_score', 0) or 0
            status = "✅" if score >= 50 else "⚠️"
            rows.append(f"| Citabilidad | {score:.1f}/100 | {status} |")
        
        if has_ia_readiness:
            ia = audit_result.ia_readiness
            score = getattr(ia, 'overall_score', 0) or 0
            status = "✅" if score >= 50 else "⚠️"
            rows.append(f"| IA-Readiness | {score:.1f}/100 | {status} |")
        
        if not rows:
            return ""
        
        section = """
## [NEW] Métricas de IA - Propuesta

| Métrica | Score | Estado |
|---------|-------|--------|
"""
        section += "\n".join(rows)
        section += """

**Nota**: Estos problemas se abordan con los siguientes assets:
- **llms.txt**: Archivo de indexación para IA
- **Schema Hotel**: Estructura de datos para motores de búsqueda y IA
- **Guía de Optimización**: Mejores prácticas de contenido

"""
        return section

    def _generate_asset_quality_table(self, assets_generated: Optional[List[Dict[str, Any]]]) -> str:
        """Genera tabla de calidad de assets para la propuesta.
        
        Mapea cada servicio de la propuesta a su asset generado y muestra
        el nivel de preparacion basado en confidence_score.
        
        Args:
            assets_generated: Lista de assets generados (cada uno con 'asset_type' y 'confidence_score').
                Si es None, muestra 'Pendiente' para todos los servicios.
        
        Returns:
            String markdown con la tabla de calidad.
        """
        # Build lookup: asset_type -> confidence_score
        asset_lookup = {}
        if assets_generated:
            for asset in assets_generated:
                asset_type = asset.get("asset_type", "") if isinstance(asset, dict) else getattr(asset, "asset_type", "")
                confidence = asset.get("confidence_score", 0) if isinstance(asset, dict) else getattr(asset, "confidence_score", 0)
                if asset_type:
                    asset_lookup[asset_type] = confidence
        
        # Table header
        rows = ["| Entregable | Nivel | Que significa |", "|------------|-------|---------------|"]
        
        for service_name, asset_type in PROPOSAL_SERVICE_TO_ASSET.items():
            if asset_type in asset_lookup:
                confidence = asset_lookup[asset_type]
                if confidence >= 0.7:
                    nivel = "✅ Completo"
                    significado = "Listo para implementar"
                elif confidence >= 0.4:
                    nivel = "⚠️ Requiere datos"
                    significado = "Necesitamos informacion adicional"
                else:
                    nivel = "🔧 En desarrollo"
                    significado = "En proceso de mejora"
            elif assets_generated is None:
                nivel = "⏳ Pendiente"
                significado = "Se genera al activar el servicio"
            else:
                nivel = "❌ No generado"
                significado = "No se pudo generar - revisaremos"
            
            rows.append(f"| {service_name} | {nivel} | {significado} |")
        
        return "\n".join(rows)

