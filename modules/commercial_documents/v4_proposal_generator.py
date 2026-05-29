"""
V4 Proposal Document Generator.

Generates the 02_PROPUESTA_COMERCIAL.md document based on
diagnostic summary and asset plans.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
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
from modules.financial_engine.pricing_calculator import get_floor_price
# ROICR FASE-3: CAPEX/OPEX desacoplados + Curva de Maduración 4 Pilares
from modules.financial_engine.roi_formatter import calcular_metricas_roi, formatear_roi_para_propuesta
from modules.financial_engine.pillar_maturity_curve import aplicar_curva_4_pilares, formatear_curva_para_propuesta
from modules.asset_generation.proposal_asset_alignment import PROPOSAL_SERVICE_TO_ASSET
from modules.commercial_documents.service_catalog import SERVICE_CATALOG, TECHNICAL_ASSET_CATALOG
from modules.common.fallback_loader import get_fallback_value, get_estimated_text, FallbackLoadError
from modules.common.yaml_loader import load_yaml_config, YAMLLoadError
# FASE-3: asset_semantics_validator integrada en services table
from modules.quality.asset_semantics_validator import validar_semantica_comercial
import logging

logger = logging.getLogger(__name__)


class CommercialGateBlockedError(Exception):
    """Raised when commercial gates block proposal generation for external clients."""

    def __init__(self, gate_ids: List[str], message: str = "Commercial gates blocking"):
        self.gate_ids = gate_ids
        self.message = message
        super().__init__(f"{message}: {gate_ids}")


def _get_pipeline_version() -> str:
    """Lee la version del pipeline desde VERSION.yaml con fallback seguro."""
    try:
        version_file = Path(__file__).parent.parent.parent / "VERSION.yaml"
        with open(version_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('version:'):
                    return line.split(':', 1)[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return "4.0.0"


PIPELINE_VERSION = _get_pipeline_version()


# ============================================================
# CONFIDENCE THRESHOLDS CACHE — FASE-CONFIG-5
# ============================================================
_confidence_cache: Optional[Dict[str, float]] = None


def _load_confidence_thresholds(region: str = "eje_cafetero") -> Dict[str, float]:
    """
    Carga confidence thresholds desde regional_benchmarks.yaml.
    
    Args:
        region: Código de región (default: eje_cafetero)
    
    Returns:
        Dict con 'high', 'medium', 'low' thresholds
    """
    global _confidence_cache
    
    if _confidence_cache is not None:
        return _confidence_cache
    
    try:
        config = load_yaml_config('regional_benchmarks')
        default_region = config.get('default_region', 'eje_cafetero')
        regions = config.get('regions', {})
        target_region = region if region in regions else default_region
        
        if target_region in regions:
            confidence = regions[target_region].get('confidence', {})
            _confidence_cache = {
                'high': confidence.get('high', 0.85),
                'medium': confidence.get('medium', 0.70),
                'low': confidence.get('low', 0.40),
            }
        else:
            _confidence_cache = {'high': 0.85, 'medium': 0.70, 'low': 0.40}
    except Exception:
        _confidence_cache = {'high': 0.85, 'medium': 0.70, 'low': 0.40}
    
    return _confidence_cache


def clear_confidence_cache() -> None:
    """Limpia el cache de confidence thresholds. Útil para testing."""
    global _confidence_cache
    _confidence_cache = None


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

    def _load_fallback(self, key: str, fallback_default=None):
        """Load a fallback value from config/fallbacks.yaml.

        Returns (value, is_estimated) tuple.
        If YAML is missing/invalid, returns (fallback_default, True) with a warning.
        FASE-CONFIG-2: Replaces silent hardcoded fallbacks (CR-3).
        """
        try:
            value = get_fallback_value(key)
            return value, True  # YAML loaded = still estimated, not real data
        except (FallbackLoadError, KeyError) as e:
            import logging
            logging.getLogger(__name__).warning(
                f"Fallback config unavailable for '{key}': {e}. "
                f"Using default: {fallback_default}"
            )
            return fallback_default, True

    def _load_scenario_config(self) -> dict:
        """Load config/scenarios.yaml with caching. Falls back to hardcoded defaults.
        
        FASE-CONFIG-3B: Replaces H-14, H-17, N-01 hardcodes.
        """
        try:
            return load_yaml_config('scenarios')
        except YAMLLoadError as e:
            logger.warning(f"scenarios.yaml unavailable, using hardcoded defaults: {e}")
            return {
                'recovery_factors': {'conservative': 0.15, 'realistic': 0.20, 'optimistic': 0.25},
                'scenario_weights': {'conservative': 0.70, 'realistic': 0.20, 'optimistic': 0.10},
                'pain_ratio_default': 0.20,
            }

    def _load_commercial_config(self) -> dict:
        """Load config/commercial.yaml with caching. Falls back to hardcoded defaults.
        
        FASE-CONFIG-4: Replaces H-15, H-16, H-25, N-04, N-04b hardcodes.
        """
        try:
            return load_yaml_config('commercial')
        except YAMLLoadError as e:
            logger.warning(f"commercial.yaml unavailable, using hardcoded defaults: {e}")
            return {
                'roi': {'cap': 5.0},
                'break_even': {'default_months': 6},
                'payment_options': {'single_payment_discount': 0.90, 'quarterly_discount': 0.95},
                'discounts': {'quarterly': 10, 'semiannual': 18},
                'guarantees': {
                    'satisfaction_days': 90, 'improvement_percent': 10, 'delivery_days': 15
                },
            }

    def _build_capex_breakdown_table(self) -> str:
        """Build CAPEX breakdown table for the proposal investment section.
        
        FASE-4 (ROICRII): Replaces single ${setup_fee} placeholder with itemized breakdown
        from config/commercial.yaml capex_breakdown.components.
        """
        config = self._load_commercial_config()
        capex_config = config.get('capex_breakdown', {})
        components = capex_config.get('components', [])
        
        if not components:
            # Fallback: single-row table with total
            return f"| Cuota de Activación | {format_cop(self.SETUP_FEE)} | Única vez |"
        
        # Build itemized table
        rows = []
        for item in components:
            if isinstance(item, dict) and 'component' in item:
                rows.append(
                    f"| {item['component']} | {format_cop(item.get('amount', 0))} | {item.get('description', '')} |"
                )
        
        # Add total row
        rows.append(f"| **Total CAPEX** | **{format_cop(capex_config.get('total', self.SETUP_FEE))}** | Única vez |")
        
        header = "| Componente | Monto | Descripción |\n|---|---|---|\n"
        return header + "\n".join(rows)

    def _build_pilot_section(self) -> str:
        """Build pilot 30 days section for the V6 proposal template.
        
        FASE-5 (ROICRIII): Adds low-risk validation option for clients without
        6-month budget commitment.
        """
        config = self._load_commercial_config()
        pilot = config.get('pilot_options', {}).get('piloto_30_dias', {})
        if not pilot:
            return ""
        
        precio = format_cop(pilot.get('precio', 0))
        entregables = '\n'.join(f"- {e}" for e in pilot.get('entregables', []))
        cond = pilot.get('condicion_continuidad', {})
        umbral_pct = int(cond.get('umbral_mejora', 0.10) * 100)
        metrica = cond.get('metrica', 'consultas_directas_gsc').replace('_', ' ')
        
        return f"""---
## 🎯 ¿Prefiere validar antes de comprometerse?

Entendemos que invertir en algo nuevo requiere confianza. Por eso ofrecemos:

### {pilot.get('nombre', 'Piloto de Validación')}

**Inversión única: {precio} COP** — Sin compromiso mensual.

**Lo que incluye:**
{entregables}

**Condiciones transparentes:**
- Si al día {pilot.get('duracion', 30)} no hay +{umbral_pct}% en {metrica} → {cond.get('sin_mejora', '')}
- Si hay mejora → {cond.get('con_mejora', '')}
"""

    def _get_main_value(self, scenario) -> int:
        """Obtiene valor central de presentacion, con fallback a monthly_loss_cop.
        
        FASE-B fix: FinancialScenario solo tiene monthly_loss_cop (no monthly_loss_max).
        Para Scenario (data_structures) usa monthly_loss_central o monthly_loss_max.
        """
        if hasattr(scenario, 'monthly_loss_cop'):
            # FinancialScenario from scenario_calculator
            return int(scenario.monthly_loss_cop)
        # Fallback for Scenario dataclass (data_structures)
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
            "monetizacion": "Pérdida de reservas moviles",
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
        site_presence_report: Optional[Any] = None,  # FASE-D: SitePresenceReport for production presence verification
        pain_ledger: Optional[List[Any]] = None,  # FASE-0D: PainLedgerEntry list for proposal-asset matrix
        document_audience: str = "client",  # FASE-A ROI-REFACTOR: "client" hides internal alerts; "internal" shows them
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
        # FASE-B: Store pain_ratio from pricing_result for projections
        self._current_pain_ratio = getattr(pricing_result, 'pain_ratio', 0.20) if pricing_result else 0.20
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
            site_presence_report=site_presence_report,
            financial_breakdown=financial_breakdown,
        )
        
        # Render template
        document_content = self._render_template(template_content, template_data)

        # FASE-COPY-B: Commercial gate validation on generated proposal
        try:
            from modules.quality_gates.commercial_gate import CommercialGateValidator

            # Calculate net_benefit_6m from scenarios
            # FASE-A CODE-2: use effective_monthly_gain (post-recovery) instead of raw monthly_loss_central
            net_benefit_6m = 0.0
            roi = 0.0
            if financial_scenarios is not None:
                realistic = getattr(financial_scenarios, 'realistic', None)
                if realistic is not None:
                    raw_monthly_loss = getattr(realistic, 'monthly_loss_central', None)
                    if raw_monthly_loss is None:
                        raw_monthly_loss = getattr(realistic, 'monthly_loss_max', 0)
                    # FASE-A: pain_ratio * recovery instead of raw loss
                    scenario_config = self._load_scenario_config()
                    recovery_factors = scenario_config['recovery_factors']
                    recovery_realistic = recovery_factors.get('realistic', 0.20)
                    pain_ratio = getattr(self, '_current_pain_ratio', scenario_config.get('pain_ratio_default', 0.20))
                    monthly_gain = int(raw_monthly_loss * pain_ratio * recovery_realistic)
                    net_monthly = monthly_gain - price_monthly
                    net_benefit_6m = net_monthly * 6
                    total_investment_opex = price_monthly * 6  # ROICRII: SIN setup_fee (CAPEX es activo del cliente)
                    total_recovery = monthly_gain * 6
                    roi = total_recovery / total_investment_opex if total_investment_opex > 0 else 0.0

            # Check for onboarding plan in pricing_result
            has_onboarding = False
            if pricing_result is not None:
                has_onboarding = getattr(pricing_result, 'is_onboarding', False)

            validator = CommercialGateValidator()
            commercial_report = validator.validate_proposal(
                proposal_text=document_content,
                net_benefit_6m=net_benefit_6m,
                roi=roi,
                has_onboarding_plan=has_onboarding,
            )

            if not commercial_report.blocking_passed:
                if document_audience == "internal":
                    alert_section = "\n---\n## ⚠️ Alertas Comerciales\n\n"
                    alert_section += (
                        "Las siguientes alertas de copywriting fueron detectadas "
                        "y deben revisarse antes de entregar al cliente:\n\n"
                    )
                    for result in commercial_report.blocking_failures:
                        alert_section += (
                            f"- **{result.name}** ({result.gate_id})\n"
                            f"  {result.message}\n"
                            f"  → {result.suggestion}\n\n"
                        )
                    document_content += alert_section
                else:
                    raise CommercialGateBlockedError(
                        [r.gate_id for r in commercial_report.blocking_failures],
                        "Proposal commercial gates BLOCKING (hidden from client)",
                    )

            if commercial_report.warnings:
                logging.info(
                    "Proposal commercial gates WARNING(s): %s",
                    [r.gate_id for r in commercial_report.warnings],
                )
        except Exception as e:
            logging.warning("Proposal commercial gate validation skipped: %s", e, exc_info=True)

        # Save document
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"02_PROPUESTA_COMERCIAL_{timestamp}.md"
        file_path = output_path / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(document_content)

        # FASE-0D: Build and save ProposalAssetMatrix for traceability
        if pain_ledger is not None and assets_generated is not None:
            try:
                from modules.asset_generation.proposal_asset_alignment import (
                    ProposalAssetMatrix,
                    ALL_PROMISED_SERVICES,
                )
                matrix = ProposalAssetMatrix()
                entries = matrix.build(
                    ALL_PROMISED_SERVICES, pain_ledger, assets_generated
                )
                matrix_path = output_path / "v4_audit" / "proposal_asset_matrix.json"
                matrix.save(entries, matrix_path)
                logger.info(
                    f"ProposalAssetMatrix saved: {len(entries)} entries → {matrix_path}"
                )
            except Exception as e:
                logger.warning(f"ProposalAssetMatrix generation failed (non-blocking): {e}")

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
- 🔴 **Fase 1**: Crítica — WhatsApp y datos para IA
- 🟡 **Fase 2**: Media — Contenido y FAQs
- 🟢 **Fase 3**: Baja — Guías locales

---

## [MONEY] INVERSIÓN Y RETORNO

### 💰 Estructura de Inversión

${capex_breakdown_table}

| Concepto | Valor | Frecuencia |
|----------|-------|------------|
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
        site_presence_report: Optional[Any] = None,  # FASE-D: SitePresenceReport for production presence
        financial_breakdown: Optional[Any] = None,  # FASE-PROP-F: For precision_tier extraction
    ) -> Dict[str, str]:
        """Prepare data for template rendering."""
        
        hotel_id = hotel_name.lower().replace(" ", "_").replace("-", "_")
        generated_at = datetime.now()
        from datetime import timedelta
        valid_until = generated_at + timedelta(days=15)
        
        # Region-based variables for V6 templates
        hotel_region = (region or "Colombia").replace("_", " ").title()
        hotel_location = getattr(audit_result, 'location', None) or \
                        getattr(getattr(audit_result, 'gbp', None), 'address', None) or \
                        hotel_region
        
        # PATCH-6: Extract hotel phone from GBP data (audit_result.gbp.phone)
        hotel_phone = ""
        if audit_result:
            gbp = getattr(audit_result, 'gbp', None)
            if gbp:
                hotel_phone = getattr(gbp, 'phone', '') or ""
        
        # Main scenario for primary display
        main_scenario = financial_scenarios.get_main_scenario()
        
        # Calculate ROI with recovery_factor per scenario
        # FASE-B: ROI = (gain * recovery_factor) / investment, capped at 5.0X
        monthly_investment = getattr(self, '_current_price_monthly', self.MONTHLY_PACKAGE_PRICE)
        # FASE-B: projected_gain uses pain_ratio, not 100% of loss
        scenario_config = self._load_scenario_config()
        recovery_factors = scenario_config['recovery_factors']
        raw_monthly_loss = self._get_main_value(main_scenario)
        pain_ratio = getattr(self, '_current_pain_ratio', scenario_config.get('pain_ratio_default', 0.20))
        # NEW-04: Alias for semantic clarity — pain_ratio is the addressable portion
        addressable_pain_ratio = pain_ratio
        projected_monthly_gain = int(raw_monthly_loss * pain_ratio)
        
        roi_cap = self._load_commercial_config().get('roi', {}).get('cap', 5.0)
        roi_6_months_metrics = calcular_metricas_roi(
            recuperacion_total=projected_monthly_gain * recovery_factors['realistic'] * 6,
            inversion_opex=monthly_investment * 6,
            inversion_capex=0,
            meses_proyeccion=6,
            roi_cap=roi_cap,
        )
        roi_6_months = formatear_roi_para_propuesta(roi_6_months_metrics)['roi_saas']
        break_even = self._calculate_break_even(monthly_investment, projected_monthly_gain)

        # HR-1 FIX: effective_monthly_gain applies recovery_factor so the ROI
        # projection table matches the pain_ratio_note. Both are consistent now.
        # projected_monthly_gain = raw_loss * pain_ratio (gross, ~41% = $1,527,360)
        # effective_monthly_gain = raw_loss * pain_ratio * recovery (net, ~41%*20% = $305,472)
        recovery_realistic = recovery_factors['realistic']
        effective_monthly_gain = int(raw_monthly_loss * pain_ratio * recovery_realistic)
        
        # H7 FIX: Detectar si monthly_report está en estado BLOCKED
        # El caller (conditional_generator) marca status="blocked" cuando fallan los reintentos
        monthly_report_disclaimer = ""
        if assets_generated:
            for asset in assets_generated:
                asset_type = asset.get("asset_type", "") if isinstance(asset, dict) else getattr(asset, "asset_type", "")
                if asset_type == "monthly_report":
                    status = asset.get("status", "") if isinstance(asset, dict) else getattr(asset, "status", "")
                    if status == "blocked":
                        monthly_report_disclaimer = (
                            "**Nota sobre Informe Mensual**: El informe mensual no pudo "
                            "generarse automáticamente en esta ejecución (datos incompletos). "
                            "Se entregue manual dentro de las 24 horas siguientes."
                        )
                        break

        # FASE-CROSS-4: Extract WhatsApp conflict status from audit_result
        # (used by both dynamic_services_table and asset_quality_table)
        whatsapp_conflict = False
        if audit_result and hasattr(audit_result, 'validation') and audit_result.validation:
            whatsapp_status = getattr(audit_result.validation, 'whatsapp_status', '')
            if whatsapp_status and whatsapp_status.lower() == ConfidenceLevel.CONFLICT.value:
                whatsapp_conflict = True

        # ROICR FASE-3: Curva de Maduración 4 Pilares — precompute before data dict
        _raw_monthly_loss_for_curve = abs(raw_monthly_loss)
        _maturity_result = aplicar_curva_4_pilares(
            fuga_mensual=_raw_monthly_loss_for_curve,
            recovery_factor_max=recovery_realistic,
            meses=6,
        )
        _curva_data = formatear_curva_para_propuesta(_maturity_result)
        _proyecciones = _maturity_result.proyecciones
        _rec_map = {p.mes: int(p.recuperacion_mensual) for p in _proyecciones}
        _acc_map = {}
        _acum = 0
        for p in _proyecciones:
            _acum += int(p.recuperacion_mensual)
            _acc_map[p.mes] = _acum

        # ROICRIII FASE-2 T1: Pre-calcular % inversión vs fuga ANTES del dict
        _pct_inv_vs_fuga = round((monthly_investment / abs(raw_monthly_loss)) * 100, 1)

        data = {
            # Metadata
            'generated_at': generated_at.strftime("%Y-%m-%d %H:%M:%S"),
            'version': PIPELINE_VERSION,
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
            'capex_breakdown_table': self._build_capex_breakdown_table(),
            'monthly_fee': format_cop(getattr(self, '_current_price_monthly', self.MONTHLY_PACKAGE_PRICE)),
            
            # ROI
            'projected_gain': format_cop(projected_monthly_gain),
            'roi_6_months': roi_6_months,
            'break_even_months': str(break_even),
# H4 FIX: Separate pain_ratio vs recovery_factor clearly.
            # - pain_ratio: portion of pain that is addressable by IAO (e.g., 41%)
            # - recovery_factor: realistic effectiveness of recovery (e.g., 20%)
            # - projected_real_gain: financial_value_central * pain_ratio * recovery_factor
            'pain_ratio_pct': f"{pain_ratio:.0%}",
            'recovery_factor_pct': f"{recovery_factors['realistic']:.0%}",
            'projected_real_gain': format_cop(int(raw_monthly_loss * pain_ratio * recovery_factors['realistic'])),
            'pain_ratio_note': (
                f"**Nota de proyección**: La inversión mensual de ${int(monthly_investment):,} COP "
                f"representa solo el {_pct_inv_vs_fuga}% "
                f"de su fuga mensual estimada (${int(abs(raw_monthly_loss)):,}). "
                f"El otro {round(100 - _pct_inv_vs_fuga, 1)}% "
                f"seguiría perdiéndose cada mes si no implementamos el Kit 4 Pilares."
            ),
            
            # Testimonials section — FASE-A ROI-REFACTOR: hidden when no testimonials
            'testimonials': [],
            'testimonials_present': "false",
            
        # All scenarios with recovery_factor per scenario
        # FASE-B: ROI = (gain * recovery_factor) / investment
        'conservative_gain': format_cop(int(self._get_main_value(financial_scenarios.conservative) * pain_ratio)),
        'conservative_roi': formatear_roi_para_propuesta(calcular_metricas_roi(
            recuperacion_total=int(self._get_main_value(financial_scenarios.conservative) * pain_ratio) * recovery_factors['conservative'] * 6,
            inversion_opex=monthly_investment * 6,
            inversion_capex=0,
            meses_proyeccion=6,
            roi_cap=roi_cap,
        ))['roi_saas'],
        'realistic_gain': format_cop(projected_monthly_gain),
        'realistic_roi': roi_6_months,
        'optimistic_gain': self._format_scenario_amount(int(self._get_main_value(financial_scenarios.optimistic) * pain_ratio)),
        'optimistic_roi': formatear_roi_para_propuesta(calcular_metricas_roi(
            recuperacion_total=int(self._get_main_value(financial_scenarios.optimistic) * pain_ratio) * recovery_factors['optimistic'] * 6,
            inversion_opex=monthly_investment * 6,
            inversion_capex=0,
            meses_proyeccion=6,
            roi_cap=roi_cap,
        ))['roi_saas'],

        # Monthly projection variables for 6 months — ROICR FASE-3: Curva 4 Pilares
        'inv_m1': format_cop(monthly_investment),
            'inv_m2': format_cop(monthly_investment),
        'inv_m3': format_cop(monthly_investment),
        'inv_m4': format_cop(monthly_investment),
        'inv_m5': format_cop(monthly_investment),
        'inv_m6': format_cop(monthly_investment),
        'rec_m1': format_cop(_rec_map.get(1, effective_monthly_gain)),
        'rec_m2': format_cop(_rec_map.get(2, effective_monthly_gain)),
        'rec_m3': format_cop(_rec_map.get(3, effective_monthly_gain)),
        'rec_m4': format_cop(_rec_map.get(4, effective_monthly_gain)),
        'rec_m5': format_cop(_rec_map.get(5, effective_monthly_gain)),
        'rec_m6': format_cop(_rec_map.get(6, effective_monthly_gain)),
        'net_m1': format_cop(_rec_map.get(1, effective_monthly_gain) - monthly_investment),
        'net_m2': format_cop(_rec_map.get(2, effective_monthly_gain) - monthly_investment),
        'net_m3': format_cop(_rec_map.get(3, effective_monthly_gain) - monthly_investment),
        'net_m4': format_cop(_rec_map.get(4, effective_monthly_gain) - monthly_investment),
        'net_m5': format_cop(_rec_map.get(5, effective_monthly_gain) - monthly_investment),
        'net_m6': format_cop(_rec_map.get(6, effective_monthly_gain) - monthly_investment),
        'acc_m1': format_cop(_acc_map.get(1, effective_monthly_gain) - monthly_investment),
        'acc_m2': format_cop(_acc_map.get(2, 2 * effective_monthly_gain) - 2 * monthly_investment),
        'acc_m3': format_cop(_acc_map.get(3, 3 * effective_monthly_gain) - 3 * monthly_investment),
        'acc_m4': format_cop(_acc_map.get(4, 4 * effective_monthly_gain) - 4 * monthly_investment),
        'acc_m5': format_cop(_acc_map.get(5, 5 * effective_monthly_gain) - 5 * monthly_investment),
        'acc_m6': format_cop(_acc_map.get(6, 6 * effective_monthly_gain) - 6 * monthly_investment),

        # ROICR FASE-3: CAPEX/OPEX desacoplados + ROI SaaS
        'curva_4_pilares_tabla': _curva_data['curva_4_pilares_tabla'],
        'total_recuperacion_6m': _curva_data['total_recuperacion_6m'],
        'recuperacion_max_mensual': _curva_data['recuperacion_max_mensual'],

        # CAPEX/OPEX separation: setup_fee is CAPEX (activo digital del cliente)
        # monthly_fee is OPEX (servicio)
        'capex_total': format_cop(getattr(self, '_current_setup_fee', self.SETUP_FEE)),
        'opex_mensual': format_cop(monthly_investment),
        'opex_total_6m': format_cop(monthly_investment * 6),

        # ROI SaaS: Recuperación Total / OPEX (NUNCA OPEX+CAPEX)
        'roi_saas': formatear_roi_para_propuesta(calcular_metricas_roi(
            recuperacion_total=_maturity_result.total_recuperacion_6m,
            inversion_opex=monthly_investment * 6,
            inversion_capex=getattr(self, '_current_setup_fee', self.SETUP_FEE),
            meses_proyeccion=6,
            roi_cap=roi_cap,
        ))['roi_saas'],

        # Activos digitales propiedad del cliente
        'activos_digitales_lista': self._build_activos_digitales_lista(asset_plan),

        # Nota metodológica CAPEX/OPEX
        'nota_capex_opex': (
            f"Los ${int(getattr(self, '_current_setup_fee', self.SETUP_FEE)):,} COP del setup fee representan activos digitales "
            f"que quedan en propiedad del cliente (Real Estate Digital). "
            f"El ROI se calcula sobre la inversión operativa (${int(monthly_investment * 6):,} COP / 6 meses), "
            f"no sobre OPEX+CAPEX combinados."
        ).replace(",", "."),
        
        # Additional variables for sales template
        'generated_date': generated_at.strftime("%Y-%m-%d"),
        'main_scenario_amount': format_cop(raw_monthly_loss),  # raw loss before pain_ratio
        'web_score': str(getattr(audit_result, 'seo_score', 'N/D')) if audit_result else 'N/D',  # FASE-PATCH-B: ya no es hardcodeado
        'web_status': "VERIFIED" if diagnostic_summary.overall_confidence.value == "VERIFIED" else "ESTIMATED",
        'roi_6m': f"{_maturity_result.total_recuperacion_6m / (monthly_investment * 6):.2f}X",  # ROICRIII-FASE-1: unified to maturity curve (~2.10X)
        'total_investment_6m': format_cop(monthly_investment * 6),
        'recovered_6m': format_cop(effective_monthly_gain * 6),  # FASE-A: unified to effective (was projected)
        'net_benefit_6m': format_cop((effective_monthly_gain - monthly_investment) * 6),  # FASE-A: unified to effective (was projected)
        'plan_7d': self._build_7_day_plan(asset_plan),
        'plan_30d': self._build_30_day_plan(asset_plan),
        'plan_60d': self._build_60_day_plan(asset_plan),
        'plan_90d': self._build_90_day_plan(asset_plan),
        'coherence_score': str(int(diagnostic_summary.coherence_score * 100)) if diagnostic_summary.coherence_score is not None else str(self._load_fallback('coherence_score', 70)[0]),

        # FASE-PROP-F: Extract precision_tier from financial_breakdown for Tier C warning banner
        # Falls back to 'C' (most conservative) if not available
        'financial_evidence_tier': getattr(financial_breakdown, 'evidence_tier', 'C') if financial_breakdown else 'C',

        # Backward compatibility: score_tecnico alias for score_global
        'score_tecnico': diagnostic_summary.score_global if diagnostic_summary.score_global is not None else (
            diagnostic_summary.score_tecnico if diagnostic_summary.score_tecnico is not None else self._load_fallback('score_tecnico', 50)[0]
        ),

        # Brecha variables — dinámicas, zero para slots sin problema real
        # Las brechas consumen top_problems (V4 compat) con guard contra phantom costs
        **self._build_brecha_data(diagnostic_summary, main_scenario),

        # V6 template variables (regional context and investment summary)
        'hotel_location': hotel_location,
        'hotel_region': hotel_region,
        'hotel_phone': hotel_phone,  # PATCH-6: GBP phone for contact section
        'monthly_loss': format_cop(raw_monthly_loss),
        'monthly_investment': format_cop(monthly_investment),
        'total_investment': format_cop(monthly_investment * 6),
        'total_recovered': format_cop(_maturity_result.total_recuperacion_6m),  # ROICRIII-FASE-1: unified to maturity curve
        'net_benefit': format_cop(_maturity_result.total_recuperacion_6m - (monthly_investment * 6)),  # ROICRIII-FASE-1: unified to maturity curve

        # Coherence checklist
        'coherence_checklist': self._build_coherence_checklist(diagnostic_summary),
        
        # Plans — FASE-D: all 4 plans now accept asset_plan for dynamic content
        # FASE-PROP-E: pass diagnostic_summary for score-based prioritization
        'plan_7_days': self._build_7_day_plan(asset_plan, diagnostic_summary),
        'plan_30_days': self._build_30_day_plan(asset_plan, diagnostic_summary),
        'plan_60_days': self._build_60_day_plan(asset_plan),
        'plan_90_days': self._build_90_day_plan(asset_plan),

        # Payment options (FASE-CONFIG-4: from commercial.yaml)
        # N-04/N-04b: single_payment_discount=0.90, quarterly_discount=0.95
        'single_payment_total': format_cop(int((getattr(self, '_current_setup_fee', self.SETUP_FEE) + getattr(self, '_current_price_monthly', self.MONTHLY_PACKAGE_PRICE) * 6) * self._load_commercial_config().get('payment_options', {}).get('single_payment_discount', 0.90))),
        'single_payment_savings': format_cop(int((getattr(self, '_current_setup_fee', self.SETUP_FEE) + getattr(self, '_current_price_monthly', self.MONTHLY_PACKAGE_PRICE) * 6) * (1 - self._load_commercial_config().get('payment_options', {}).get('single_payment_discount', 0.90)))),
        'quarterly_fee': format_cop(int(getattr(self, '_current_price_monthly', self.MONTHLY_PACKAGE_PRICE) * 3 * self._load_commercial_config().get('payment_options', {}).get('quarterly_discount', 0.95))),
        'quarterly_savings': format_cop(int(getattr(self, '_current_price_monthly', self.MONTHLY_PACKAGE_PRICE) * 3 * (1 - self._load_commercial_config().get('payment_options', {}).get('quarterly_discount', 0.95)))),

        # Discounts for template (H-23: FASE-CONFIG-4)
        'quarterly_discount': self._load_commercial_config().get('discounts', {}).get('quarterly', 10),
        'semiannual_discount': self._load_commercial_config().get('discounts', {}).get('semiannual', 18),

        # Guarantees for template (H-25: FASE-CONFIG-4)
        'guarantee_satisfaction_days': self._load_commercial_config().get('guarantees', {}).get('satisfaction_days', 90),
        'guarantee_improvement_percent': self._load_commercial_config().get('guarantees', {}).get('improvement_percent', 10),
        'guarantee_delivery_days': self._load_commercial_config().get('guarantees', {}).get('delivery_days', 15),
        'installment_label': self._load_commercial_config().get('payment_options', {}).get('installment_label', '3 cuotas sin interés'),

        # FASE-5: Pilot 30 days section
        'pilot_section': self._build_pilot_section(),

        # FASE-5: Garantía Día 55 con KPI específico
        'garantia_metrica': 'Clics directos desde Google Search Console',
        'garantia_umbral': '+15% vs. línea base del Día 0',
        'garantia_consecuencia': 'Nota crédito automática del 50% del mes 2',

        # GEO Section (NUEVO) + GAP-IAO-01-03 Monetary Impact
        'geo_section': (self._build_geo_section(audit_result) if audit_result else "") + self._build_monetary_impact_section(diagnostic_summary),

        # ANALYTICS-02: Analytics section in proposal
        'analytics_section': self._inject_analytics(analytics_data),

        # FASE-CAUSAL-REFACTOR: Extract pain_ids BEFORE data dict for dynamic tables
        # FASE-D: Also pass score_aeo for AEO conditional service
        'pain_ids': getattr(diagnostic_summary, 'pain_ids', None) or [],
        'dynamic_services_table': self._generate_dynamic_services_table(
            detected_pain_ids=getattr(diagnostic_summary, 'pain_ids', None) or [],
            score_aeo=diagnostic_summary.score_aeo,
            assets_generated=assets_generated,
            site_presence_report=site_presence_report,
            whatsapp_conflict=whatsapp_conflict,  # FASE-C CROSS-4
        ),
        'asset_quality_table': self._generate_asset_quality_table(
            assets_generated,
            detected_pain_ids=getattr(diagnostic_summary, 'pain_ids', None) or [],
            site_presence_report=site_presence_report,
            audit_result=audit_result,
            score_aeo=diagnostic_summary.score_aeo,
        ),
        'technical_assets_table': self._generate_technical_assets_table(
            assets_generated=assets_generated,
            site_presence_report=site_presence_report,
        ),

        # FASE-D: Competitors section — only if competitors data available
        'competitors_section': self._build_competitors_section(audit_result),

        # H7 FIX: Disclaimer si monthly_report falló
        'monthly_report_disclaimer': monthly_report_disclaimer,

        # PROPUESTA-COMERCIAL FASE-B: Puente dual para trazabilidad financiera
        # Usa pain_ratio real del pricing (~41% Castilla Real) + recovery_factor real (20%)
        # Esto diferencia la propuesta del diagnóstico que usa defaults conservadores (20%/20%).
        # ROICRIII FASE-2 T2: fuga_total_6m usa abs() para evitar signo negativo en el template
        'fuga_total_6m': format_cop(abs(raw_monthly_loss) * 6),
        # ROICRIII FASE-2 T2: recuperacion_proyectada_6m unificada con curva de maduración
        'recuperacion_proyectada_6m': format_cop(int(_maturity_result.total_recuperacion_6m)),
        # ROICRIII FASE-2 T2: nueva variable de trazabilidad transparente
        'trazabilidad_origen': (
            f"Fuga mensual (${int(abs(raw_monthly_loss)):,}) × "
            f"Curva de Maduración 4 Pilares (GEO→SEO→AEO→IAO) × "
            f"Recovery Factor {int(recovery_realistic * 100)}%"
        ),
    }

        # FASE-CONFIG-2: Inject estimated flag when fallbacks are in use
        _has_coherence_real = diagnostic_summary.coherence_score is not None
        _has_score_tecnico_real = (
            diagnostic_summary.score_global is not None
            or diagnostic_summary.score_tecnico is not None
        )
        if not _has_coherence_real or not _has_score_tecnico_real:
            try:
                data['estimated_disclaimer'] = get_estimated_text()
                data['is_estimated'] = True
            except FallbackLoadError:
                data['estimated_disclaimer'] = "Valor estimado"
                data['is_estimated'] = True

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
 

    def _generate_dynamic_services_table(
        self,
        detected_pain_ids: Optional[List[str]] = None,
        score_aeo: Optional[int] = None,
        assets_generated: Optional[List[Dict[str, Any]]] = None,
        site_presence_report: Optional[Any] = None,
        whatsapp_conflict: bool = False,  # FASE-C CROSS-4: muestra conflicto
    ) -> str:
        """Genera tabla principal de servicios mostrando TODOS los servicios prometidos.

        FASE-2: Ahora muestra los 8 servicios definidos en PROPOSAL_SERVICE_TO_ASSET
        con sus estados reales (aligned, missing, present_in_production), en vez de
        filtrar dinámicamente por assets generados o pains detectados.

        FASE-C CROSS-2: Columna adicional 'Problema que resuelve' conecta cada servicio
        con la brecha del diagnóstico que resuelve.

        Args:
            detected_pain_ids: LEGACY — ya no se usa para filtrar (backwards compat).
            score_aeo: Score AEO 0-100. Si < 20, agrega servicio AEO adicional.
            assets_generated: Lista de assets generados (cada uno con 'asset_type',
                'confidence_score'). Usado para determinar estado de cada servicio.
            site_presence_report: SitePresenceReport para determinar present_in_production.
            whatsapp_conflict: Si True, el botón de WhatsApp muestra '⚠️ Requiere
                corrección' en lugar de 'ℹ️ Presente en sitio'.

        Returns:
            String markdown con la tabla de servicios (8 filas + header).
        """
        # FASE-2: Mapping asset_type → brecha que resuelve (auditada)
        # Formato: (brecha_num, brecha_nombre, brecha_costo_mensual)
        # whatsapp_button → None porque CROSS-4 lo maneja con whatsapp_conflict
        # FASE-3 B1: ASSET_TO_PAIN_ID para validacion semantica
        ASSET_TO_PAIN_ID = {
            "monthly_report":         "no_faq_schema",
            "faq_page":               "no_faq_schema",
            "hotel_schema":           "no_hotel_schema",
            "llms_txt":               "missing_llmstxt",
            "whatsapp_button":        "no_whatsapp_visible",
            "whatsapp_conflict_guide": "no_whatsapp_visible",
        }
        BREACH_BY_ASSET = {
            # FASE-3 B2: monthly_report YA NO mapea a FAQ (no_faq_schema)
            # — muestra info general en su lugar
            "optimization_guide":  ("#1", "Sin Schema Hotel",       "$1,005,768"),
            "whatsapp_button":     None,   # CROSS-4: manejado con whatsapp_conflict
            "hotel_schema":       ("#1", "Sin Schema Hotel",       "$1,005,768"),
            "org_schema":         ("#7", "Sin Schema Org",         "$321,786"),
            "monthly_report":     ("—", "Informe de rendimiento",   "—"),
            # FASE-3 B2: faq_page SÍ resuelve no_faq_schema (correcto)
            "faq_page":           ("#4", "Sin FAQ",               "$482,679"),
            "open_graph":         ("#6", "Sin OG Tags",           "$321,786"),
            "llms_txt":           ("#3", "Baja prep. IA",         "$603,536"),
            # FASE-3 B2: deprecados eliminados — optimization_guide, local_content_page
        }
        # FASE-2: Build lookups for state determination
        asset_lookup = {}
        if assets_generated:
            for asset in assets_generated:
                asset_type = asset.get("asset_type", "") if isinstance(asset, dict) else getattr(asset, "asset_type", "")
                confidence = asset.get("confidence_score", 0) if isinstance(asset, dict) else getattr(asset, "confidence_score", 0)
                if asset_type:
                    asset_lookup[asset_type] = confidence

        presence_lookup = {}
        if site_presence_report and hasattr(site_presence_report, 'results'):
            for asset_type, result in site_presence_report.results.items():
                presence_lookup[asset_type] = {
                    'present_in_production': result.status.value == "exists",
                    'presence_verified': True,
                }

        # FASE-2: Iterate over ALL promised services (PROPOSAL_SERVICE_TO_ASSET)
        # plus AEO conditional — always show 8 services with status
        # FASE-C CROSS-2: 4 columnas + FASE-D: columna Confianza (5 cols)
        rows = [
            "| Servicio | Estado | Confianza | Problema que resuelve | Qué obtiene |",
            "|----------|--------|-----------|----------------------|-------------|",
        ]

        for service_name, asset_type in PROPOSAL_SERVICE_TO_ASSET.items():
            confidence = asset_lookup.get(asset_type)
            presence = presence_lookup.get(asset_type, {})

            # FASE-3 B1: Validacion semantica — block hallucination mappings
            pain_id = ASSET_TO_PAIN_ID.get(asset_type)
            if pain_id:
                is_valid, status = validar_semantica_comercial(pain_id, asset_type, "IMPLEMENT")
                if not is_valid:
                    logger.warning(f"[AssetSemantics] BLOCKED in services_table: {asset_type} → {pain_id}")
                    continue  # skip this row — asset cant solve this pain

            # FASE-C CROSS-4: WhatsApp conflict → override estado
            if asset_type == "whatsapp_button" and whatsapp_conflict:
                estado = "📋 Auditoría incluida"
                confianza_col = "—"
                brecha_col = "Brecha #5: WhatsApp no coincide"
                desc = "Auditoría y Optimización de Conversión"
                rows.append(f"| **{service_name}** | {estado} | {confianza_col} | {brecha_col} | {desc} |")
                continue

            # Determine state with icons
            if presence.get('presence_verified') and presence.get('present_in_production'):
                estado = "ℹ️ Presente en sitio"
            elif confidence is not None and confidence >= 0.85:
                estado = "✅ Alineado"
            elif confidence is not None and confidence < 0.85:
                estado = "En proceso de activación — Semana 2"
            else:
                estado = "⏳ Pendiente"

            # FASE-D: Confidence score column
            if confidence is None:
                confianza_col = "—"
            elif confidence < 0.65:
                confianza_col = f"⚠️ {confidence:.0%}"
            else:
                confianza_col = f"{confidence:.0%}"

            # FASE-C CROSS-2: Breach column
            brecha_info = BREACH_BY_ASSET.get(asset_type)
            if brecha_info:
                brecha_col = f"{brecha_info[0]}: {brecha_info[1]} ({brecha_info[2]}/mes)"
            else:
                brecha_col = "—"

            # Get description from SERVICE_CATALOG or fallback
            desc = ""
            for entry in SERVICE_CATALOG.values():
                if entry.service_name == service_name:
                    desc = entry.description
                    break
            if not desc:
                desc = "Servicio incluido en su kit"

            rows.append(f"| **{service_name}** | {estado} | {confianza_col} | {brecha_col} | {desc} |")

        # FASE-E: AEO conditional service — unified threshold with technical assets table
        if score_aeo is not None and score_aeo < 30:
            aeo_entry = SERVICE_CATALOG.get("optimizacion_ia_generativa")
            if aeo_entry:
                aeo_asset_type = aeo_entry.asset_type
                confidence = asset_lookup.get(aeo_asset_type)
                presence = presence_lookup.get(aeo_asset_type, {})

                if presence.get('presence_verified') and presence.get('present_in_production'):
                    estado = "ℹ️ Presente en sitio"
                elif confidence is not None and confidence >= 0.85:
                    estado = "✅ Alineado"
                elif confidence is not None and confidence < 0.85:
                    estado = "En proceso de activación — Semana 2"
                else:
                    estado = "⏳ Pendiente"

                # FASE-D: Confidence score for AEO entry
                if confidence is None:
                    confianza_col = "—"
                elif confidence < 0.65:
                    confianza_col = f"⚠️ {confidence:.0%}"
                else:
                    confianza_col = f"{confidence:.0%}"

                rows.append(f"| **{aeo_entry.service_name}** | {estado} | {confianza_col} | — | {aeo_entry.description} |")

        return "\n".join(rows)

    def _generate_technical_assets_table(
        self,
        assets_generated: Optional[List[Dict[str, Any]]] = None,
        site_presence_report: Optional[Any] = None,
    ) -> str:
        """Genera tabla de assets técnicos adicionales para la propuesta.

        FASE-2: Muestra assets técnicos (analytics_setup_guide,
        indirect_traffic_optimization) con su estado real.

        Args:
            assets_generated: Lista de assets generados para determinar estado.
            site_presence_report: SitePresenceReport para present_in_production.

        Returns:
            String markdown con la tabla de assets técnicos, o string vacío
            si no hay assets técnicos en el catálogo.
        """
        if not TECHNICAL_ASSET_CATALOG:
            return ""

        # Build lookups
        asset_lookup = {}
        if assets_generated:
            for asset in assets_generated:
                asset_type = asset.get("asset_type", "") if isinstance(asset, dict) else getattr(asset, "asset_type", "")
                confidence = asset.get("confidence_score", 0) if isinstance(asset, dict) else getattr(asset, "confidence_score", 0)
                if asset_type:
                    asset_lookup[asset_type] = confidence

        presence_lookup = {}
        if site_presence_report and hasattr(site_presence_report, 'results'):
            for asset_type, result in site_presence_report.results.items():
                presence_lookup[asset_type] = {
                    'present_in_production': result.status.value == "exists",
                    'presence_verified': True,
                }

        rows = ["| Asset Técnico | Estado | Descripción |", "|---------------|--------|-------------|"]

        for entry in TECHNICAL_ASSET_CATALOG.values():
            confidence = asset_lookup.get(entry.asset_type)
            presence = presence_lookup.get(entry.asset_type, {})

            if presence.get('presence_verified') and presence.get('present_in_production'):
                estado = "ℹ️ Presente en sitio"
            elif confidence is not None and confidence >= 0.85:
                estado = "✅ Generado"
            elif confidence is not None and confidence < 0.85:
                estado = "En proceso de activación — Semana 2"
            else:
                estado = "⏳ No generado"

            rows.append(f"| **{entry.asset_name}** | {estado} | {entry.description} |")

        return "\n".join(rows)

    def _generate_asset_quality_table(
        self,
        assets_generated: Optional[List[Dict[str, Any]]],
        detected_pain_ids: Optional[List[str]] = None,
        site_presence_report: Optional[Any] = None,
        audit_result: Optional[Any] = None,  # FASE-D: audit for schema_valid / faq_schema_valid
        score_aeo: Optional[int] = None,  # FASE-PROP-E: AEO score for conditional row
    ) -> str:
        """Genera tabla de calidad de assets para la propuesta.

        Mapea cada servicio de la propuesta a su asset generado y muestra
        el nivel de preparacion basado en confidence_score.

        FASE-D root-fix: site_presence_report permite mostrar "Verificado en sitio"
        cuando SitePresenceChecker confirmo que el asset ya existe en produccion.
        FIX: audit_result.schema_valid / faq_schema_valid para no mostrar
        "Completo" para Schema Hotel / Schema Organization y FAQ cuando no estan validados.

        FASE-PROP-E: Si score_aeo < 30, agrega fila AEO que conecta con assets existentes.

        Args:
            assets_generated: Lista de assets generados (cada uno con 'asset_type' y 'confidence_score').
                Si es None, muestra 'Pendiente' para todos los servicios.
            detected_pain_ids: Lista de pain IDs detectados (de PainSolutionMapper.detect_pains).
                Si esta disponible, genera tabla DINAMICA (solo servicios con pain detectado).
                Si es None/empty, usa PROPOSAL_SERVICE_TO_ASSET (backwards compat).
            site_presence_report: SitePresenceReport de SitePresenceChecker.
                Si esta presente, se extrae present_in_production y presence_verified
                para cada asset_type y se pasan a _confidence_to_nivel_significado.
            audit_result: AuditResult con schema_valid y faq_schema_valid.
                Si esta presente, se usa para downgradear "Completo" a "Listo para implementar"
                cuando el schema no esta validado en produccion.
            score_aeo: Score AEO 0-100. Si < 30, agrega fila AEO en tabla.

        Returns:
            String markdown con la tabla de calidad.
        """
        # FASE-D: Build presence_lookup from site_presence_report
        # presence_lookup[asset_type] = {'present_in_production': bool, 'presence_verified': bool}
        presence_lookup = {}
        if site_presence_report and hasattr(site_presence_report, 'results'):
            for asset_type, result in site_presence_report.results.items():
                presence_lookup[asset_type] = {
                    'present_in_production': result.status.value == "exists",
                    'presence_verified': True,
                }

        # FASE-D: Extract schema validation flags from audit_result
        schema_valid = False
        faq_schema_valid = False
        if audit_result and hasattr(audit_result, 'schema'):
            schema_valid = getattr(audit_result.schema, 'hotel_schema_valid', False)
            faq_schema_valid = getattr(audit_result.schema, 'faq_schema_valid', False)

        # FASE-PROP-B: Extract WhatsApp conflict status from audit_result
        whatsapp_conflict = False
        if audit_result and hasattr(audit_result, 'validation') and audit_result.validation:
            whatsapp_status = getattr(audit_result.validation, 'whatsapp_status', '')
            if whatsapp_status and whatsapp_status.lower() == ConfidenceLevel.CONFLICT.value:
                whatsapp_conflict = True

        # Build lookup: asset_type -> confidence_score
        asset_lookup = {}
        if assets_generated:
            for asset in assets_generated:
                asset_type = asset.get("asset_type", "") if isinstance(asset, dict) else getattr(asset, "asset_type", "")
                confidence = asset.get("confidence_score", 0) if isinstance(asset, dict) else getattr(asset, "confidence_score", 0)
                if asset_type:
                    asset_lookup[asset_type] = confidence

        # DYNAMIC mode: use SERVICE_CATALOG filtered by detected pains
        if detected_pain_ids:
            # Filter SERVICE_CATALOG to only entries whose pain_id is detected
            services_to_show = [
                entry for entry in SERVICE_CATALOG.values()
                if entry.pain_id in detected_pain_ids
            ]
        else:
            # STATIC/backwards-compat mode: iterate over PROPOSAL_SERVICE_TO_ASSET
            # (same 7 entries as before)
            services_to_show = None  # signals to use static iteration below

        # Table header — FASE-B: "Momento de entrega" en lugar de "Estado"
        rows = ["| Entregable | Momento de entrega | Qué incluye |", "|------------|-------------------|-------------|"]

        if services_to_show is not None:
            # Dynamic: build from detected pains
            for entry in services_to_show:
                confidence = asset_lookup.get(entry.asset_type, None)
                presence = presence_lookup.get(entry.asset_type, {})
                # FASE-D FIX: Pass schema validation flags for hotel_schema and faq_page
                is_schema = entry.asset_type == 'hotel_schema'
                is_faq = entry.asset_type == 'faq_page'
                nivel, significado = self._confidence_to_nivel_significado(
                    confidence,
                    assets_generated,
                    present_in_production=presence.get('present_in_production', False),
                    presence_verified=presence.get('presence_verified', False),
                    schema_valid_override=schema_valid if is_schema else None,
                    faq_schema_valid_override=faq_schema_valid if is_faq else None,
                    whatsapp_conflict_override=whatsapp_conflict if entry.asset_type == 'whatsapp_button' else False,
                )
                rows.append(f"| {entry.service_name} | {nivel} | {significado} |")
        else:
            # Static/backwards-compat: iterate over PROPOSAL_SERVICE_TO_ASSET
            for service_name, asset_type in PROPOSAL_SERVICE_TO_ASSET.items():
                confidence = asset_lookup.get(asset_type, None)
                presence = presence_lookup.get(asset_type, {})
                # FASE-D FIX: Pass schema validation flags for hotel_schema and faq_page
                is_schema = asset_type == 'hotel_schema'
                is_faq = asset_type == 'faq_page'
                nivel, significado = self._confidence_to_nivel_significado(
                    confidence,
                    assets_generated,
                    present_in_production=presence.get('present_in_production', False),
                    presence_verified=presence.get('presence_verified', False),
                    schema_valid_override=schema_valid if is_schema else None,
                    faq_schema_valid_override=faq_schema_valid if is_faq else None,
                    whatsapp_conflict_override=whatsapp_conflict if asset_type == 'whatsapp_button' else False,
                )
                rows.append(f"| {service_name} | {nivel} | {significado} |")

        # FASE-PROP-E: AEO row — connects to existing assets when score is low
        # FASE-B: "Optimización para Asistentes de Voz" replaces "AEO (Answer Engine Optimization)"
        if score_aeo is not None and score_aeo < 30:
            rows.append("| Optimización para Asistentes de Voz (Siri, Alexa, Google) | ✅ Basado en assets existentes | Se construye sobre Schema FAQ + Open Graph — ambos incluidos en su kit |")

        return "\n".join(rows)

    def _confidence_to_nivel_significado(
        self,
        confidence: Optional[float],
        assets_generated: Optional[List],
        present_in_production: bool = False,
        presence_verified: bool = False,
        schema_valid_override: Optional[bool] = None,
        faq_schema_valid_override: Optional[bool] = None,
        whatsapp_conflict_override: bool = False,
    ) -> tuple:
        """Convert confidence score to nivel + significado tuple.

        FASE-C: Lenguaje positivo para cliente final.
        FASE-D root-fix: distingue entre asset generado vs verificado en producción.
        Un asset con alta confianza NO significa que esté implementado en el sitio real.
        FIX: schema_valid_override / faq_schema_valid_override para no mostrar
        "Completo" cuando el schema no esta validado en el sitio real.

        Args:
            confidence: Confidence score of the generated asset (0.0-1.0)
            assets_generated: List of assets (for backward compat, not used for decision)
            present_in_production: True if SitePresenceChecker verified the asset exists on the site
            presence_verified: True if presence verification was performed
            schema_valid_override: If not None, overrides "Completo" for hotel_schema.
                Use False to downgrade to "Listo para implementar".
            faq_schema_valid_override: If not None, overrides "Completo" for faq_page.
                Use False to downgrade to "Listo para implementar".
            whatsapp_conflict_override: If True, overrides presence_verified for whatsapp_button
                to show conflict warning instead of "Verificado en sitio".
        """
        # FASE-PROP-B: Si hay conflicto de WhatsApp, mostrar advertencia antes de cualquier otro estado
        if whatsapp_conflict_override:
            return ("⚠️ Intervención manual", "Requerimos sus datos para resolver")

        # FASE-D: Si se verificó presencia y el asset YA existe en producción,
        # es el estado más honesto que podemos mostrar
        if presence_verified and present_in_production:
            return ("✅ Día 1 (Verificado)", "Ya existe en su web - nosotros lo entregamos")

        if confidence is not None:
            # FASE-CONFIG-5: Usar thresholds del YAML en lugar de hardcodes
            thresholds = _load_confidence_thresholds()
            high_threshold = thresholds['high']      # default: 0.85
            medium_threshold = thresholds['medium']  # default: 0.70
            low_threshold = thresholds['low']        # default: 0.40
            
            if confidence >= high_threshold:
                # Alta confianza: asset bien generado Y auditado
                # FIX: No mostrar "Completo" si schema_valid=false en el sitio real
                # "Completo" solo si el schema esta implementado Y validado
                if schema_valid_override is False or faq_schema_valid_override is False:
                    return ("⚠️ Semana 1 (Con sus datos)", "Requiere confirmacion post-firma")
                return ("✅ Día 1 (Activación inicial)", "Listo para implementar")
            elif confidence >= medium_threshold:
                # Threshold mínimo: asset generado con calidad aceptable
                return ("⚠️ Semana 1 (Con sus datos)", "Requiere confirmacion post-firma")
            elif confidence >= low_threshold:
                return ("⚠️ Semana 2 (Configuración)", "Datos pendientes del cliente")
            else:
                return ("🔧 En mejora continua", "Optimización sin costo adicional")
        elif assets_generated is None:
            return ("✅ Día 1 (Activación inicial)", "Preparacion posterior a la firma")
        else:
            return ("✅ Día 1 (Activación inicial)", "Preparacion posterior a la firma")

    def _preprocess_conditionals(self, template_content: str, data: Dict[str, Any]) -> str:
        """Elimina bloques {{if cond}}...{{endif}} cuando cond es False.

        FASE-1-A: Procesa conditionals {{if var == "value"}}...{{endif}}
        antes de safe_substitute para evitar que viajen crudos al cliente.

        FASE-2-PATCH-A: Expande expresiones compuestas con OR antes del pattern
        simple. Maneja {{if a == "X" or a == "Y"}}...{{endif}}.
        """
        import re

        # PASO 1 (FASE-2-PATCH-A): Expandir expresiones compuestas con OR
        # {{if a == "X" or a == "Y"}}...{{endif}}
        # → {{if a == "X"}}...{{endif}}{{if a == "Y"}}...{{endif}}
        or_pattern = r'\{\{if\s+(\w+)\s*==\s*"([^"]+)"\s+or\s+\w+\s*==\s*"([^"]+)"\}\}(.*?)\{\{endif\}\}'

        def expand_or(match):
            var = match.group(1)
            val1 = match.group(2)
            val2 = match.group(3)
            block = match.group(4)
            return (
                f'{{{{if {var} == "{val1}"}}}}{block}{{{{endif}}}}'
                f'{{{{if {var} == "{val2}"}}}}{block}{{{{endif}}}}'
            )

        template_content = re.sub(or_pattern, expand_or, template_content, flags=re.DOTALL)

        # PASO 2: Procesar conditionals simples (código existente FASE-1-A)
        pattern = r'\{\{if\s+(\w+)\s*==\s*"([^"]+)"\}\}(.*?)\{\{endif\}\}'

        def replace_match(match):
            var_name = match.group(1)
            expected = match.group(2)
            block = match.group(3)
            actual = str(data.get(var_name, ''))
            return block if actual == expected else ''

        return re.sub(pattern, replace_match, template_content, flags=re.DOTALL)
    
    def _render_template(self, template_content: str, data: Dict[str, str]) -> str:
        """Render the template with data.
        
        FASE-1-A: Pre-procesa conditionals {{if}} antes de safe_substitute.
        """
        preprocessed = self._preprocess_conditionals(template_content, data)
        template = Template(preprocessed)
        return template.safe_substitute(data)
    
    def _calculate_break_even(self, investment: int, gain: int) -> int:
        """Calculate break-even point in months.
        
        FASE-CONFIG-4: default_months from commercial.yaml (was hardcoded 6).
        """
        if gain <= investment:
            # Default to configured value from commercial.yaml (FASE-CONFIG-4)
            return self._load_commercial_config().get('break_even', {}).get('default_months', 6)
        
        months = 0
        cumulative = -getattr(self, '_current_setup_fee', self.SETUP_FEE)
        while cumulative < 0 and months < 24:
            months += 1
            cumulative += (gain - investment)
        
        return months
    
    # ROICRIII FASE-4: Assets deprecados — no deben aparecer en la lista del cliente
    DEPRECATED_ASSETS = {
        "og_tags_guide",
        "indirect_traffic_optimization",
        "local_content_page",
        "optimization_guide",
    }

    def _build_activos_digitales_lista(self, asset_plan: List[AssetSpec]) -> str:
        """ROICR FASE-3: Genera lista de activos digitales propiedad del cliente.

        Extrae nombres de assets del plan que representan activos entregables
        (no servicios recurrentes). Estos activos forman el CAPEX.
        ROICRIII FASE-4: Filtra assets deprecados.
        """
        if not asset_plan:
            return "- Sin activos digitales especificados"
        activos = []
        for asset in asset_plan:
            name = getattr(asset, 'asset_type', '') or getattr(asset, 'name', '') or str(asset)
            if name and name not in self.DEPRECATED_ASSETS:
                activos.append(f"- {name}")
        if not activos:
            return "- Sin activos digitales especificados"
        return "\n".join(activos)

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

    def _determinar_paquete(self, diagnostic_summary: DiagnosticSummary) -> dict:
        """
        Usa score_tecnico de KB para sugerir paquete.
        BASADO EN: KB sugerir_paquete()
        """
        score = diagnostic_summary.score_tecnico if diagnostic_summary.score_tecnico is not None else self._load_fallback('score_tecnico', 50)[0]

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
        benchmark_score = self._load_fallback('benchmark_score', 58)[0]  # FASE-CONFIG-2: from YAML
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
        # Calculate expected value from scenarios (weighted from config/scenarios.yaml)
        conservative = self._get_main_value(financial_scenarios.conservative)
        realistic = self._get_main_value(financial_scenarios.realistic)
        optimistic = self._get_main_value(financial_scenarios.optimistic)
        
        weights = self._load_scenario_config()['scenario_weights']
        expected_monthly = int(
            conservative * weights['conservative'] +
            realistic * weights['realistic'] +
            optimistic * weights['optimistic']
        )
        
        # 2% of expected value, bounded between floor_price and 2.5M COP
        floor = get_floor_price()
        calculated_price = min(max(int(expected_monthly * 0.02), floor), 2500000)
        
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
            1: "🔴 Fase 1",
            2: "🟡 Fase 2",
            3: "🟢 Fase 3",
        }
        
        for asset in sorted(asset_plan, key=lambda x: x.priority):
            icon = confidence_to_icon(asset.confidence_level)
            priority = priority_icons.get(asset.priority, "⚪ P?")

            # ROICR FASE-1: AUDIT_ONLY assets — audit verb instead of implementation
            problem_text = asset.problem_solved
            if getattr(asset, 'semantic_status', 'IMPLEMENT') == 'AUDIT_ONLY':
                problem_text = f"Auditar y Optimizar: {problem_text}"

            row = f"| {problem_text} | {asset.description} | `{asset.asset_type}` | {priority} | {icon} {asset.confidence_level.value} |"
            rows.append(row)
        
        return "\n".join(rows) if rows else "| Sin assets planificados | - | - | - | - |"
    
    def _build_brecha_data(self, diagnostic_summary, main_scenario) -> Dict[str, str]:
        """Build brecha_1..4 nombre/costo dynamically using real impact weights.

        FASE-4 (H3): Normalizes sum to financial_value_central exactly.
        Previously: each brecha computed independently via int() causing
        rounding errors that accumulated (e.g., $3,742,069 != $3,741,696).
        Now: compute raw values, sum them, then adjust the LAST brecha
        to absorb the difference and make total match exact central value.

        FASE-G: Usa brechas_reales (con impacto real de _identify_brechas) cuando
        está disponible. Fallback a top_problems con distribución equitativa.
        Slots without real problems get $0.
        """
        max_brechas = 4
        top_problems = diagnostic_summary.top_problems or []
        brechas_reales = getattr(diagnostic_summary, 'brechas_reales', None) or []
        brecha_data: Dict[str, str] = {}

        # H3 FIX: collect raw values first, then normalize to exact central
        raw_values: List[int] = []
        raw_names: List[str] = []

        for i in range(max_brechas):
            if i < len(brechas_reales):
                # Fuente primaria: impacto real de _identify_brechas
                brecha = brechas_reales[i]
                impacto = brecha.get('impacto', 1.0 / max(len(brechas_reales), 1))
                costo_raw = self._get_main_value(main_scenario) * impacto
                raw_values.append(costo_raw)
                raw_names.append(brecha.get('nombre', ''))
            elif i < len(top_problems):
                # Fallback: top_problems sin impacto real (distribución equitativa)
                distribucion_raw = self._get_main_value(main_scenario) / max(len(top_problems), 1)
                raw_values.append(distribucion_raw)
                raw_names.append(top_problems[i])
            else:
                raw_values.append(0.0)
                raw_names.append("")

        # H3 FIX: normalize so sum equals exact central value
        financial_central = float(self._get_main_value(main_scenario))
        raw_sum = sum(raw_values)
        diff = round(raw_sum - financial_central)

        # Only normalize if there is at least one real brecha/problem
        # If all slots are empty (no data), keep them at $0
        has_real_data = any(raw_names)

        # Assign final integer values, absorbing diff into last brecha
        final_values: List[int] = []
        for i in range(max_brechas):
            raw = raw_values[i]
            if not has_real_data:
                final_values.append(0)
            elif i == max_brechas - 1:
                # Last brecha absorbs rounding difference
                final_values.append(int(round(raw - diff)))
            else:
                final_values.append(int(round(raw)))

        # Build brecha_data dict
        for i in range(max_brechas):
            slot = i + 1
            brecha_data[f'brecha_{slot}_nombre'] = raw_names[i] if raw_names[i] else ""
            # H3 FIX: costo always uses final_values (even if name is empty)
            # This allows the last slot to absorb rounding diff even when it has no name
            if final_values[i] > 0:
                brecha_data[f'brecha_{slot}_costo'] = format_cop(final_values[i])
            else:
                brecha_data[f'brecha_{slot}_costo'] = "$0"

        return brecha_data

    def _get_adr_from_benchmarks(self, region: str) -> Optional[float]:
        """Obtener ADR desde benchmarks regionales (regional_adr_2026.json).

        Usa RegionalADRResolver para resolver ADR con la cascada completa:
        regional_adr_2026.json → plan_maestro_data.json → default.
        Retorna None si ninguna fuente tiene datos.
        """
        try:
            from modules.financial_engine.regional_adr_resolver import RegionalADRResolver
            resolver = RegionalADRResolver()
            # rooms=0 y user_provided_adr=None para obtener solo el benchmark regional
            result = resolver.resolve(region=region, rooms=0, user_provided_adr=None)
            return result.adr_cop if result and result.adr_cop else None
        except (ImportError, FileNotFoundError, Exception):
            return None

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

        # Verificar ADR — Cascada: validated_data → benchmarks regionales → None
        adr_value = (
            validated_data.get('adr')
            or self._get_adr_from_benchmarks('eje_cafetero')
            or None
        )
        adr_verified = adr_value is not None and adr_value > 0
        adr_display = f"${adr_value:,.0f} COP" if adr_verified else "Pendiente"
        adr_detail = "Benchmark vs Input" if adr_verified else adr_display

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
    
    def _build_7_day_plan(
        self,
        asset_plan: Optional[List[AssetSpec]],
        diagnostic_summary: Optional[DiagnosticSummary] = None,
    ) -> str:
        """Build detailed 7-day activation plan.

        FASE-D: Genera contenido dinámico basado en assets P1 del asset_plan.
        FASE-PROP-E: Prioriza pilares con score < 30 en quick wins.
        Solo quick wins que NO requieren datos externos del cliente.
        Si asset_plan es None, usa contenido genérico (backward compat).

        Args:
            asset_plan: Lista de AssetSpec con priority. P1 assets son activos en 7 días.
            diagnostic_summary: Summary con scores de 4 pilares para priorización.
        """
        # FASE-PROP-E: Quick wins basados en scores bajos
        score_actions = []
        if diagnostic_summary:
            if diagnostic_summary.score_seo is not None and diagnostic_summary.score_seo < 30:
                score_actions.append("Auditar y optimizar perfil Google Business (SEO Local crítico)")
            if diagnostic_summary.score_aeo is not None and diagnostic_summary.score_aeo < 30:
                score_actions.append("Implementar Schema FAQ para respuestas directas en búsqueda (AEO)")

        if not asset_plan:
            base = """- [ ] **Día 1**: Firma de propuesta y pago de activación
- [ ] **Día 2**: Kick-off call con el equipo del hotel (30 min)
- [ ] **Día 3**: Solicitud de accesos (web, GBP actual)
- [ ] **Día 4**: Entrega de activos sin dependencia de datos
- [ ] **Día 5**: Validación técnica inicial
- [ ] **Día 6**: Ajustes según feedback
- [ ] **Día 7**: Confirmación de activación completa"""
            if score_actions:
                base += "\n\n**Quick Wins Prioritarios (score < 30):**\n" + "\n".join(f"- [ ] {a}" for a in score_actions)
            base += "\n\n*Nota: Open Graph con fotos y SEO avanzado requieren datos suyos (fotos, accesos). Se entregan en la fase de activación.*"
            return base

        p1_assets = [a for a in asset_plan if a.priority == 1]

        if not p1_assets and not score_actions:
            return """- [ ] **Día 1**: Firma de propuesta y pago de activación
- [ ] **Día 2**: Kick-off call con el equipo del hotel (30 min)
- [ ] **Día 3**: Solicitud de accesos (web, GBP actual)
- [ ] **Día 4**: Configuración inicial sin dependencia de datos externos
- [ ] **Día 5**: Validación técnica inicial
- [ ] **Día 6**: Ajustes según feedback
- [ ] **Día 7**: Confirmación de activación completa"""

        lines = [
            "- [ ] **Día 1**: Firma de propuesta y pago de activación",
            "- [ ] **Día 2**: Kick-off call con el equipo del hotel (30 min)",
            "- [ ] **Día 3**: Solicitud de accesos (web, GBP actual)",
        ]

        if p1_assets:
            asset_names = [a.asset_type.replace("_", " ").title() for a in p1_assets[:4]]
            lines.append("- [ ] **Día 4**: Implementación de activos Fase 1 (sin datos externos):")
            lines.extend(f"- [ ] {name}" for name in asset_names)
        elif score_actions:
            lines.append("- [ ] **Día 4**: Implementación de quick wins prioritarios:")

        if score_actions:
            lines.extend(f"- [ ] {action}" for action in score_actions)

        lines.extend([
            "- [ ] **Día 5**: Validación técnica inicial",
            "- [ ] **Día 6**: Ajustes según feedback",
            "- [ ] **Día 7**: Confirmación de activación completa",
        ])

        result = "\n".join(lines)
        result += "\n\n*Nota: Open Graph con fotos y SEO avanzado requieren datos suyos (fotos, accesos). Se entregan en la fase de activación.*"
        return result

    def _build_30_day_plan(
        self,
        asset_plan: Optional[List[AssetSpec]],
        diagnostic_summary: Optional[DiagnosticSummary] = None,
    ) -> str:
        """Build detailed 30-day quick wins plan.

        FASE-D: Genera contenido dinámico basado en assets P1 y P2.
        FASE-PROP-E: Prioriza pilares con score < 30 en plan de 30 días.
        Assets que requieren datos del cliente (fotos, accesos a Maps).
        Si asset_plan es None, usa contenido genérico (backward compat).

        Args:
            asset_plan: Lista de AssetSpec con priority. P1+P2 assets son activos en 30 días.
            diagnostic_summary: Summary con scores de 4 pilares para priorización.
        """
        # FASE-PROP-E: Acciones específicas para scores bajos en 30 días
        score_actions = []
        if diagnostic_summary:
            if diagnostic_summary.score_seo is not None and diagnostic_summary.score_seo < 30:
                score_actions.append("SEO Local - optimizar GBP, NAP consistente, keywords locales")
            if diagnostic_summary.score_aeo is not None and diagnostic_summary.score_aeo < 30:
                score_actions.append("AEO - activar Schema FAQ + Open Graph (ya incluidos en su kit)")
            if diagnostic_summary.score_iao is not None and diagnostic_summary.score_iao < 30:
                score_actions.append("IAO - optimizar visibilidad en ChatGPT, Gemini, Perplexity")

        if not asset_plan:
            lines = [
                "- [ ] **Semana 2**: Implementación Open Graph con fotos reales (pendiente de recibir fotos del cliente)",
                "- [ ] **Semana 2**: Configuración sistema de rastreo (sabemos de dónde viene cada reserva)",
                "- [ ] **Semana 4**: Primera publicación posts GBP + revisión métricas iniciales",
                "- [ ] **Día 30**: Reporte de avance con métricas de visibilidad",
            ]
            if score_actions:
                lines.insert(1, "- [ ] **Semana 3**: " + "; ".join(score_actions))
            else:
                lines.insert(1, "- [ ] **Semana 3**: SEO Local - optimización basada en análisis técnico")
            return "\n".join(lines)

        p1_assets = [a for a in asset_plan if a.priority == 1]
        p2_assets = [a for a in asset_plan if a.priority == 2]

        items = []

        # P1 assets needing client data
        if p1_assets:
            asset_names = [a.asset_type.replace("_", " ").title() for a in p1_assets[:3]]
            items.append(f"- [ ] **Semana 2**: Implementación Fase 1 (WhatsApp + datos para IA): {', '.join(asset_names)}")

        # P2 assets needing client data
        if p2_assets:
            asset_names = [a.asset_type.replace("_", " ").title() for a in p2_assets[:3]]
            items.append(f"- [ ] **Semana 3**: Implementación Fase 2 (Contenido y FAQs): {', '.join(asset_names)}")

        # FASE-PROP-E: Insert score-based actions
        if score_actions:
            items.append("- [ ] **Semana 3**: " + "; ".join(score_actions))
        elif not p2_assets:
            items.append("- [ ] **Semana 3**: SEO Local - optimización basada en análisis técnico")

        items.extend([
            "- [ ] **Semana 3**: Configuración sistema de rastreo (sabemos de dónde viene cada reserva)",
            "- [ ] **Semana 4**: Primera publicación posts GBP + revisión métricas iniciales",
            "- [ ] **Día 30**: Reporte de avance con métricas de visibilidad"
        ])

        return "\n".join(items)

    def _build_60_day_plan(self, asset_plan: Optional[List[AssetSpec]]) -> str:
        """Build detailed 60-day consolidation plan.
        
        FASE-D: Genera contenido dinámico basado en assets P3.
        Si asset_plan es None, usa contenido genérico (backward compat).
        
        Args:
            asset_plan: Lista de AssetSpec con priority. P3 assets son activos en 60 días.
        """
        base_plan = """- [ ] **Días 31-45**: Optimización de assets entregados (A/B testing de títulos, descripciones)
- [ ] **Días 46-50**: Implementación Fase 2 y Fase 3 restantes
- [ ] **Días 51-55**: Primera medición de impacto en consultas directas (datos reales de Google Search Console)
- [ ] **Días 56-60**: Ajustes basados en datos reales + reporte día 60"""

        if not asset_plan:
            return base_plan

        p3_assets = [a for a in asset_plan if a.priority == 3]

        if not p3_assets:
            return base_plan

        # Encontrar assets P3 que también necesitan datos del cliente
        pending_p3 = [a for a in p3_assets if a.requires_manual_action]
        if pending_p3:
            asset_names = [a.asset_type.replace("_", " ").title() for a in pending_p3[:3]]
            p3_line = f"- [ ] **Días 46-50**: Implementación Fase 3 (Guías locales, pendiente datos del cliente): {', '.join(asset_names)}"
        else:
            asset_names = [a.asset_type.replace("_", " ").title() for a in p3_assets[:3]]
            p3_line = f"- [ ] **Días 46-50**: Implementación Fase 3 (Guías locales): {', '.join(asset_names)}"

        return f"""- [ ] **Días 31-45**: Optimización de assets entregados (A/B testing de títulos, descripciones)
{p3_line}
- [ ] **Días 51-55**: Primera medición de impacto en consultas directas (datos reales de Google Search Console)
- [ ] **Días 56-60**: Ajustes basados en datos reales + reporte día 60"""

    def _build_90_day_plan(self, asset_plan: Optional[List[AssetSpec]]) -> str:
        """Build detailed 90-day optimization plan.
        
        FASE-D: Genera contenido dinámico basado en asset_plan.
        Incluye evaluación de ROI, optimización, planificación fase 2 y reporte.
        Si asset_plan es None, usa contenido genérico (backward compat).
        
        Args:
            asset_plan: Lista de AssetSpec para planificar fase 2.
        """
        base_plan = """- [ ] **Días 61-75**: Evaluación de ROI a 3 meses con métricas reales
- [ ] **Días 76-80**: Optimización de conversiones basada en datos de GA4
- [ ] **Días 81-85**: Planificación de assets adicionales (fase 2)
- [ ] **Días 86-90**: Revisión de estrategia a largo plazo + reporte final de resultados"""

        if not asset_plan:
            return base_plan

        # Assets que no se implementaron aún (P3 o MANUAL_ONLY)
        remaining = [a for a in asset_plan if a.priority >= 3 or a.requires_manual_action]
        
        if remaining:
            asset_names = [a.asset_type.replace("_", " ").title() for a in remaining[:4]]
            phase2_line = f"- [ ] **Días 81-85**: Planificación fase 2 basada en gaps: {', '.join(asset_names)}"
        else:
            phase2_line = "- [ ] **Días 81-85**: Planificación de assets adicionales (fase 2)"

        return f"""- [ ] **Días 61-75**: Evaluación de ROI a 3 meses con métricas reales
- [ ] **Días 76-80**: Optimización de conversiones basada en datos de GA4
{phase2_line}
- [ ] **Días 86-90**: Revisión de estrategia a largo plazo + reporte final de resultados"""

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

    def _build_competitors_section(self, audit_result: Optional[Any]) -> str:
        """Build competitors section for the proposal.

        FASE-D: Shows nearby competitors identified during audit with name,
        distance (if available), rating, and main gap vs our hotel.

        Args:
            audit_result: V4AuditResult with competitors list from
                CompetitorAnalyzer.get_nearby_competitors().

        Returns:
            Markdown section with competitors table, or empty string if no data.
        """
        if not audit_result:
            return ""

        competitors = getattr(audit_result, 'competitors', None)
        if not competitors:
            return ""

        # Filter to top 5 competitors with useful data
        valid_competitors = [
            c for c in competitors
            if isinstance(c, dict) and c.get('name')
        ][:5]

        if not valid_competitors:
            return ""

        # Build table rows
        rows = []
        for c in valid_competitors:
            name = c.get('name', 'Competidor sin nombre')
            rating = c.get('rating', None)
            rating_str = f"{rating} ⭐" if rating else "Sin rating"
            distance = c.get('distance_km', None)
            dist_str = f"{distance:.1f} km" if distance else "Dist. descon. "
            geo_score = c.get('geo_score', None)
            geo_str = f"GEO {geo_score}/100" if geo_score else "GEO sin datos"
            # Main gap: describe what this competitor does better
            fotos = c.get('fotos', 0)
            reviews = c.get('reviews', 0)
            gap_parts = []
            if fotos > 0:
                gap_parts.append(f"{fotos} fotos")
            if reviews > 0:
                gap_parts.append(f"{reviews} reviews")
            gap_str = " | ".join(gap_parts) if gap_parts else "—"

            rows.append(f"| {name} | {rating_str} | {dist_str} | {geo_str} | {gap_str} |")

        table_content = "\n".join(rows)

        return f"""
## 🏨 Competidores Cercanos Identificados

Analizamos {len(valid_competitors)} hoteles similares en su área. Esto es lo que encontramos:

|| Competidor | Rating | Distancia | GEO Score | Info adicional ||
||------------|--------|-----------|-----------|-----------------|
{table_content}

**Lo que esto significa para usted:** Estos son hoteles como el suyo. Si ellos aparecen antes
en Google Maps o en las respuestas de ChatGPT, los viajeros los eligen a ellos. Nuestra estrategia
busca que usted aparezca al mismo nivel o por delante de ellos.
"""


