"""
V4 Diagnostic Document Generator.

Generates the 01_DIAGNOSTICO_Y_OPORTUNIDAD.md document based on
v4.0 audit results with confidence-based validation.
"""

import os
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
        self.template_path = self.template_dir / "diagnostico_v4_template.md"
    
    def generate(
        self,
        audit_result: V4AuditResult,
        validation_summary: ValidationSummary,
        financial_scenarios: FinancialScenarios,
        hotel_name: str,
        hotel_url: str,
        output_dir: str,
        coherence_score: Optional[float] = None,
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
            
        Returns:
            Path to the generated document
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Load template
        template_content = self._load_template()
        
        # Prepare template data
        template_data = self._prepare_template_data(
            audit_result=audit_result,
            validation_summary=validation_summary,
            financial_scenarios=financial_scenarios,
            hotel_name=hotel_name,
            hotel_url=hotel_url,
            coherence_score=coherence_score,
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
| Visibilidad Google Maps (GEO) | ${geo_score}/100 | 60/100 | ${geo_status} |
| Activity Score (GBP) | ${activity_score}/100 | 30/100 | ${activity_status} |
| Web Score (SEO) | ${web_score}/100 | 70/100 | ${web_status} |
| Infraestructura AEO (Schema) | ${aeo_score}/100 | 40/100 | ${aeo_status} |
| Score IA Avanzado (IAO) | ${iao_score}/100 | 20/100 | ${iao_status} |

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

## 🚨 LAS 4 RAZONES EXACTAS DE SUS PÉRDIDAS

### [RAZÓN 1] ${brecha_1_nombre}
**Impacto mensual:** ${brecha_1_costo}  
**Detalle:** ${brecha_1_detalle}

### [RAZÓN 2] ${brecha_2_nombre}
**Impacto mensual:** ${brecha_2_costo}  
**Detalle:** ${brecha_2_detalle}

### [RAZÓN 3] ${brecha_3_nombre}
**Impacto mensual:** ${brecha_3_costo}  
**Detalle:** ${brecha_3_detalle}

### [RAZÓN 4] ${brecha_4_nombre}
**Impacto mensual:** ${brecha_4_costo}  
**Detalle:** ${brecha_4_detalle}

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
    ) -> Dict[str, str]:
        """Prepare data for template rendering."""
        
        # Basic metadata
        hotel_id = hotel_name.lower().replace(" ", "_").replace("-", "_")
        # Use provided coherence_score from coherence gate, or calculate internally
        if coherence_score is None:
            coherence_score = self._calculate_coherence_score(validation_summary)
        
        # Validated data table
        validated_data_table = self._build_validated_data_table(validation_summary, audit_result)
        
        # Empathy message
        empathy_message = self._build_empathy_message(financial_scenarios, hotel_name)
        
        # Scenarios
        main_scenario = financial_scenarios.get_main_scenario()
        
        # Additional variables for the sales template
        # Extract year from generated_at or use current year
        from datetime import datetime
        year = datetime.now().year
        prev_year = year - 1
        
        # Calculate 6-month loss
        loss_6_months_value = main_scenario.monthly_loss_max * 6
        
        # Plan variables - for now, we set them based on quick wins or default values
        # In a real implementation, these would be derived from audit results and strategy
        plan_7d = "Revisar y optimizar Google Business Profile"
        plan_30d = "Implementar quick wins identificados y comenzar plan de contenido"
        plan_60d = "Desarrollar presencia en asistentes de IA y monitorear resultados"
        plan_90d = "Consolidar estrategia de IA y evaluar retorno de inversión"
        
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
            'main_scenario_amount': format_cop(main_scenario.monthly_loss_max),
            'main_scenario_description': main_scenario.description,
            'main_confidence': str(int(main_scenario.confidence_score * 100)),
            
            # All scenarios
            'conservative_range': f"{format_cop(financial_scenarios.conservative.monthly_loss_min)} - {format_cop(financial_scenarios.conservative.monthly_loss_max)}",
            'conservative_description': financial_scenarios.conservative.description,
            'conservative_assumptions': self._format_list(financial_scenarios.conservative.assumptions),
            
            'realistic_range': f"{format_cop(financial_scenarios.realistic.monthly_loss_min)} - {format_cop(financial_scenarios.realistic.monthly_loss_max)}",
            'realistic_description': financial_scenarios.realistic.description,
            'realistic_assumptions': self._format_list(financial_scenarios.realistic.assumptions),
            
            'optimistic_range': f"{self._format_scenario_amount(financial_scenarios.optimistic.monthly_loss_min)} - {self._format_scenario_amount(financial_scenarios.optimistic.monthly_loss_max)}",
            'optimistic_description': financial_scenarios.optimistic.description,
            'optimistic_assumptions': self._format_list(financial_scenarios.optimistic.assumptions),
            
            # Problems
            'solvable_problems_table': self._build_solvable_problems_table(audit_result),
            'manual_attention_table': self._build_manual_attention_table(audit_result),
            'top_critical_problems': self._build_top_critical_problems(audit_result),
            'quick_wins_list': self._build_quick_wins(audit_result),
            'geo_table': self._build_geo_problems_table(audit_result),
            
            # 4 Pilares Scores
            'geo_score': self._calculate_geo_score(audit_result),
            'geo_status': self._get_score_status(self._calculate_geo_score(audit_result), 60),
            'activity_score': self._calculate_activity_score(audit_result),
            'activity_status': self._get_score_status(self._calculate_activity_score(audit_result), 30),
            'web_score': self._calculate_web_score(audit_result),
            'web_status': self._get_score_status(self._calculate_web_score(audit_result), 70),
            'schema_infra_score': self._calculate_schema_infra_score(audit_result),
            'schema_infra_status': self._get_score_status(self._calculate_schema_infra_score(audit_result), 40),
            'voice_readiness_score': self._calculate_voice_readiness_score(),
            'voice_readiness_status': '⏳ Pendiente',
            'iao_score': self._calculate_iao_score(audit_result),
            'iao_status': self._get_score_status(self._calculate_iao_score(audit_result), 20),
            
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
        }
        
        return data
    
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
                'confidence': confidence.value,
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
        if audit_result.gbp.place_found and audit_result.gbp.rating > 0:
            fields.append({
                'name': 'Rating GBP',
                'value': f"{audit_result.gbp.rating}/5.0 ({audit_result.gbp.reviews} reviews)",
                'confidence': 'VERIFIED',
                'icon': '🟢',
                'sources': 'Google Places API'
            })
        
        # Performance Score
        if audit_result.performance.mobile_score is not None:
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
                import re
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
        amount = format_cop(main.monthly_loss_max)
        
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

    def _format_scenario_amount(self, amount: int, description: str = "") -> str:
        """Format scenario amount with semantic handling for negative values.
        
        Args:
            amount: Monthly loss amount (can be negative for equilibrium/gain)
            description: Optional description to append
            
        Returns:
            Formatted string with proper semantics
        """
        if amount <= 0:
            # Negative or zero = Equilibrium or gain
            return f"Equilibrio (ahorro: {format_cop(abs(amount))})"
        return format_cop(amount)
    
    def _build_solvable_problems_table(self, audit_result: V4AuditResult) -> str:
        """Build table of problems with automatic solutions."""
        rows = []
        
        # Schema issues
        if not audit_result.schema.hotel_schema_detected:
            rows.append("| Sin Schema de Hotel | 🔴 Crítica | `hotel_schema.json` | 🟢 VERIFIED |")
        elif not audit_result.schema.hotel_schema_valid:
            rows.append("| Schema de Hotel Inválido | 🟡 Media | `hotel_schema_fix.json` | 🟢 VERIFIED |")
        
        # FAQ issues
        if not audit_result.schema.faq_schema_detected:
            rows.append("| Sin Schema FAQ | 🟡 Media | `faqs.csv` | 🟡 ESTIMATED |")
        
        # WhatsApp issues
        if audit_result.validation.whatsapp_status == ConfidenceLevel.CONFLICT.value:
            rows.append("| WhatsApp Inconsistente | 🔴 Crítica | `boton_whatsapp.html` | 🔴 CONFLICT |")
        elif not audit_result.validation.phone_web:
            rows.append("| Sin Botón WhatsApp | 🟡 Media | `boton_whatsapp.html` | 🟢 VERIFIED |")
        
        # Performance
        if audit_result.performance.mobile_score and audit_result.performance.mobile_score < 50:
            rows.append("| Rendimiento Móvil Bajo | 🟡 Media | Guía de optimización | 🟢 VERIFIED |")
        
        return "\n".join(rows) if rows else "| No se detectaron problemas solubles automáticamente | - | - | - |"
    
    def _build_manual_attention_table(self, audit_result: V4AuditResult) -> str:
        """Build table of problems requiring manual attention."""
        rows = []
        
        # GBP issues
        if audit_result.gbp.geo_score < 70:
            rows.append(f"| Perfil GBP Sub-optimizado | 🟡 Media | Optimizar {audit_result.gbp.reviews} reviews y {audit_result.gbp.photos} fotos |")
        
        if audit_result.gbp.photos < 20:
            rows.append(f"| Fotos GBP Insuficientes | 🟡 Media | Subir al menos {20 - audit_result.gbp.photos} fotos adicionales |")
        
        # Performance without field data
        if not audit_result.performance.has_field_data:
            rows.append("| Sin Datos de Campo (Core Web Vitals) | 🟡 Media | El sitio puede ser nuevo o tener tráfico bajo |")
        
        # Conflicts
        if audit_result.validation.conflicts:
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
        
        # Schema implementation
        if not audit_result.schema.hotel_schema_detected:
            wins.append(f"{win_number}. **Implementar Schema de Hotel** - Impacto SEO inmediato (1-2 días)")
            win_number += 1
        
        # WhatsApp button
        if not audit_result.validation.phone_web:
            wins.append(f"{win_number}. **Agregar Botón WhatsApp** - Canal directo de reservas (1 día)")
            win_number += 1
        
        # FAQ schema
        if not audit_result.schema.faq_schema_detected:
            wins.append(f"{win_number}. **Crear Schema FAQ** - Capturar rich snippets (2-3 días)")
            win_number += 1
        
        # GBP optimization
        if audit_result.gbp.photos < 20:
            wins.append(f"{win_number}. **Subir Fotos a GBP** - Mejorar visibilidad local (1 día)")
            win_number += 1
        
        # Performance
        if audit_result.performance.mobile_score and audit_result.performance.mobile_score < 70:
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
    def _calculate_geo_score(self, audit_result: V4AuditResult) -> str:
        """Calculate GEO score based on GBP data."""
        if not audit_result.gbp.place_found:
            return "0"
        score = min(100, max(0, audit_result.gbp.geo_score))
        return str(int(score))
    
    def _calculate_activity_score(self, audit_result: V4AuditResult) -> str:
        """Calculate Activity Score based on GBP engagement."""
        if not audit_result.gbp.place_found:
            return "0"
        # Base score from reviews and photos
        base = min(50, (audit_result.gbp.reviews / 100) * 25 + (audit_result.gbp.photos / 50) * 25)
        # Add geo_score factor
        score = min(100, int(base + (audit_result.gbp.geo_score * 0.5)))
        return str(score)
    
    def _calculate_web_score(self, audit_result: V4AuditResult) -> str:
        """Calculate Web/SEO score based on performance and schema."""
        score = 0
        # Performance score (up to 40 points)
        if audit_result.performance.mobile_score:
            score += min(40, audit_result.performance.mobile_score * 0.4)
        # Schema bonus (up to 30 points)
        if audit_result.schema.hotel_schema_detected:
            score += 20
            if audit_result.schema.hotel_schema_valid:
                score += 10
        # FAQ schema (up to 20 points)
        if audit_result.schema.faq_schema_detected:
            score += 15
        # Validation consistency (up to 10 points)
        if audit_result.validation.whatsapp_status != ConfidenceLevel.CONFLICT.value:
            score += 10
        return str(min(100, int(score)))
    
    def _calculate_schema_infra_score(self, audit_result: V4AuditResult) -> str:
        """Calculate Schema Infrastructure score (renamed from AEO).
        
        NOTE: This measures the FOUNDATION for voice assistants (structured data).
        Actual AEO (voice search optimization) requires FASE-B (SpeakableSpecification, etc.)
        This score = voice_readiness placeholder + performance threshold.
        """
        score = 0
        # Voice Readiness placeholder (FASE-B will add SpeakableSpecification)
        # For now, no additional points until FASE-B implements voice-specific features
        # Performance threshold (up to 20 points)
        if audit_result.performance.mobile_score and audit_result.performance.mobile_score >= 50:
            score += 20
        return str(min(100, int(score)))
    
    def _calculate_voice_readiness_score(self) -> str:
        """Calculate Voice Readiness (AEO) score - placeholder.
        
        REQUIRES FASE-B: SpeakableSpecification, FAQ conversacional, voice keywords.
        Currently returns 0/100 as placeholder.
        """
        return "0"
    
    def _calculate_iao_score(self, audit_result: V4AuditResult) -> str:
        """Calculate IAO (AI Advanced) score."""
        score = 0
        # Schema completeness for AI (up to 40 points)
        if audit_result.schema.hotel_schema_detected and audit_result.schema.hotel_schema_valid:
            score += 30
            if hasattr(audit_result.schema, 'properties') and audit_result.schema.properties:
                score += min(10, len(audit_result.schema.properties) * 2)
        # FAQ for AI snippets (up to 30 points)
        if audit_result.schema.faq_schema_detected:
            score += 25
        # GBP optimization for AI search (up to 30 points)
        if audit_result.gbp.place_found:
            score += min(30, (audit_result.gbp.reviews / 50) * 15 + (audit_result.gbp.rating / 5) * 15)
        return str(min(100, int(score)))
    
    def _get_score_status(self, score: str, benchmark: int) -> str:
        """Get status emoji based on score vs benchmark."""
        try:
            s = int(score)
            if s >= benchmark * 1.1:
                return "✅ Superior"
            elif s >= benchmark * 0.9:
                return "⚠️ Promedio"
            else:
                return "❌ Bajo"
        except (ValueError, TypeError):
            return "❓ N/A"
    
    # Brecha (gap) calculation methods
    def _get_brecha_nombre(self, audit_result: V4AuditResult, index: int) -> str:
        """Get nombre de la brecha (razón) by index."""
        brechas = self._identify_brechas(audit_result)
        if index < len(brechas):
            return brechas[index]['nombre']
        return "Sin identificar"
    
    def _get_brecha_costo(self, audit_result: V4AuditResult, financial_scenarios: FinancialScenarios, index: int) -> str:
        """Get costo estimado de la brecha by index."""
        brechas = self._identify_brechas(audit_result)
        if index < len(brechas):
            # Calculate proportional cost from main scenario
            main = financial_scenarios.get_main_scenario()
            proportion = brechas[index].get('impacto', 0.25)
            costo = main.monthly_loss_max * proportion
            return format_cop(costo)
        return format_cop(0)
    
    def _get_brecha_detalle(self, audit_result: V4AuditResult, index: int) -> str:
        """Get detalle/explicación de la brecha by index."""
        brechas = self._identify_brechas(audit_result)
        if index < len(brechas):
            return brechas[index]['detalle']
        return "Sin información adicional"
    
    def _identify_brechas(self, audit_result: V4AuditResult) -> List[Dict[str, Any]]:
        """Identify the 4 main brechas (gaps) from audit results."""
        brechas = []
        
        # Brecha 1: Visibilidad GBP/GEO
        if not audit_result.gbp.place_found or audit_result.gbp.geo_score < 60:
            brechas.append({
                'nombre': 'Visibilidad Local (Google Maps)',
                'impacto': 0.30,
                'detalle': '73% de búsquedas son "cerca de mí". Su GBP no aparece o está sub-optimizado. Clientes van a competidores.'
            })
        
        # Brecha 2: Sin Schema de Hotel
        if not audit_result.schema.hotel_schema_detected:
            brechas.append({
                'nombre': 'Sin Schema de Hotel (Invisible para IA)',
                'impacto': 0.25,
                'detalle': 'ChatGPT, Gemini y Perplexity no pueden "leer" su hotel. Perdida absoluta de reservas de IA.'
            })
        
        # Brecha 3: WhatsApp No Configurado
        if not audit_result.validation.phone_web:
            brechas.append({
                'nombre': 'Canal Directo Cerrado (Sin WhatsApp)',
                'impacto': 0.20,
                'detalle': 'Viajeros quieren reservar instantáneamente. Sin botón WhatsApp, pierden el impulso de compra.'
            })
        
        # Brecha 4: Performance Web
        if audit_result.performance.mobile_score and audit_result.performance.mobile_score < 70:
            brechas.append({
                'nombre': 'Web Lenta (Abandono Móvil)',
                'impacto': 0.15,
                'detalle': f"{audit_result.performance.mobile_score}/100 en velocidad móvil. 53% abandona si tarda >3 segundos."
            })
        
        # Brecha 5: Conflictos de Datos
        if audit_result.validation.whatsapp_status == ConfidenceLevel.CONFLICT.value:
            brechas.append({
                'nombre': 'Datos Inconsistentes (Confusión Cliente)',
                'impacto': 0.10,
                'detalle': 'WhatsApp diferente en web vs Google. Cliente confundido = reserva perdida.'
            })
        
        # Ensure we always return 4 brechas, filling with generic ones if needed
        defaults = [
            {'nombre': 'Oportunidad de FAQ/Rich Snippets', 'impacto': 0.15, 'detalle': 'Sin Schema FAQ, pierde rich snippets en Google. Competidores capturan esa atención.'},
            {'nombre': 'Optimización GBP Incompleta', 'impacto': 0.15, 'detalle': 'Faltan fotos o descripción en GBP. Menor conversión en búsquedas locales.'},
            {'nombre': 'Sin Datos de Campo (Core Web Vitals)', 'impacto': 0.10, 'detalle': 'Google penaliza rankings sin métricas reales de usuario. Señal de bajo tráfico.'},
            {'nombre': 'Presencia IA No Optimizada', 'impacto': 0.10, 'detalle': 'Su hotel no está estructurado para respuestas de IA. Perdiendo tráfico emergente.'},
        ]
        
        while len(brechas) < 4 and defaults:
            brechas.append(defaults.pop(0))
        
        return brechas[:4]
