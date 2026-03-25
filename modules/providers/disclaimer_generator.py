"""
Disclaimer Generator for IA Hoteles Agent v4.0

Generates honest disclaimers based on confidence levels and data sources.
Follows the NEVER_BLOCK principle - always provides output with transparency.

v4.5.9: IntelligentDisclaimerGenerator adds contextual improvement steps,
specific missing data details, and expected confidence after fixes.
"""

from typing import List, Optional, Dict, Any


class DisclaimerGenerator:
    """
    Generates disclaimers for assets based on confidence level.
    
    NEVER_BLOCK Principle:
    - Assets with confidence < 0.9 get a disclaimer
    - Disclaimer includes: sources used, gaps in data, recommendations
    - Assets with confidence >= 0.9 may skip disclaimer (minimal)
    """
    
    CONFIDENCE_THRESHOLD = 0.9
    LOW_CONFIDENCE_THRESHOLD = 0.5
    
    def generate(
        self,
        confidence: float,
        sources: List[str],
        gaps: List[str]
    ) -> Optional[str]:
        """
        Generate a disclaimer based on confidence, sources, and gaps.
        
        Args:
            confidence: Confidence score (0.0 - 1.0)
            sources: List of data sources used (e.g., ["web_scraping", "gbp"])
            gaps: List of missing data fields (e.g., ["telephone", "address"])
            
        Returns:
            Disclaimer string, or empty string/None if confidence >= 0.9
        """
        # No disclaimer for high confidence
        if confidence >= self.CONFIDENCE_THRESHOLD:
            if not gaps:
                return ""
            # Even with high confidence, if there are gaps, a minimal note is fine
            # but the threshold says 0.9 exact doesn't need disclaimer
            return ""
        
        # Process sources
        if not sources:
            sources_str = "fuente no disponible"
        else:
            sources_str = self._format_sources(sources)
        
        # Process gaps
        gaps_str = self._format_gaps(gaps)
        
        # Generate disclaimer based on confidence level
        confidence_pct = int(confidence * 100)
        
        if confidence < 0.5:
            return self._generate_detailed_disclaimer(confidence_pct, sources_str, gaps_str)
        elif confidence < 0.7:
            return self._generate_moderate_disclaimer(confidence_pct, sources_str, gaps_str)
        else:
            return self._generate_minimal_disclaimer(confidence_pct, sources_str, gaps_str)
    
    def _format_sources(self, sources: List[str]) -> str:
        """Format sources list into readable string."""
        unique_sources = list(set(sources))
        formatted = []
        for source in unique_sources:
            source_lower = source.lower()
            if "benchmark" in source_lower:
                formatted.append("benchmark regional")
            elif "scraping" in source_lower or "web" in source_lower:
                formatted.append("web scraping")
            elif "gbp" in source_lower or "google" in source_lower:
                formatted.append("Google Business Profile")
            elif "booking" in source_lower:
                formatted.append("Booking.com")
            elif "tripadvisor" in source_lower:
                formatted.append("TripAdvisor")
            elif "user" in source_lower:
                formatted.append("entrada del usuario")
            else:
                formatted.append(source)
        return ", ".join(formatted)
    
    def _format_gaps(self, gaps: List[str]) -> str:
        """Format gaps list into readable string."""
        if not gaps:
            return "sin campos faltantes"
        
        # Keep original gap names but provide translations alongside
        field_names = []
        for gap in gaps:
            gap_lower = gap.lower()
            if "telephone" in gap_lower or "phone" in gap_lower or "tel" in gap_lower:
                field_names.append("telephone/teléfono")
            elif "address" in gap_lower or "direccion" in gap_lower:
                field_names.append("address/dirección")
            elif "description" in gap_lower or "descripcion" in gap_lower:
                field_names.append("description/descripción")
            elif "amenities" in gap_lower or "servicios" in gap_lower:
                field_names.append("amenities/servicios")
            elif "city" in gap_lower or "ciudad" in gap_lower:
                field_names.append("city/ciudad")
            elif "name" in gap_lower or "nombre" in gap_lower:
                field_names.append("name/nombre")
            elif "all" in gap_lower:
                field_names = ["múltiples campos"]
                break
            else:
                field_names.append(gap)
        
        unique_fields = list(dict.fromkeys(field_names))  # Preserve order, remove duplicates
        return ", ".join(unique_fields)
    
    def _generate_detailed_disclaimer(
        self, 
        confidence_pct: int, 
        sources_str: str, 
        gaps_str: str
    ) -> str:
        """Generate detailed disclaimer for very low confidence (< 0.5)."""
        disclaimer_parts = [
            f"⚠️ Estimation muy limitada - confianza {confidence_pct}%",
            "",
            f"Fuentes de datos: {sources_str}",
            f"Datos faltantes: {gaps_str}",
            "",
            "Este asset se basa en datos limitados y requiere verificación manual exhaustiva",
            "antes de cualquier uso en producción.",
            "",
            "Recomendación: Completar los datos faltantes mediante investigación directa",
            "o contacto con el hotel."
        ]
        return "\n".join(disclaimer_parts)
    
    def _generate_moderate_disclaimer(
        self, 
        confidence_pct: int, 
        sources_str: str, 
        gaps_str: str
    ) -> str:
        """Generate moderate disclaimer for medium confidence (0.5 - 0.7)."""
        disclaimer_parts = [
            f"⚠️ Datos estimados - confianza {confidence_pct}%",
            "",
            f"Fuentes: {sources_str}",
            f"Datos faltantes: {gaps_str}",
            "",
            "Este asset contiene estimaciones basadas en fuentes parciales.",
            "Recomendación: validar datos antes de usar."
        ]
        return "\n".join(disclaimer_parts)
    
    def _generate_minimal_disclaimer(
        self, 
        confidence_pct: int, 
        sources_str: str, 
        gaps_str: str
    ) -> str:
        """Generate minimal disclaimer for lower-medium confidence (0.7 - 0.89)."""
        disclaimer_parts = [
            f"ℹ️ Confianza {confidence_pct}% - basado en: {sources_str}",
        ]
        if gaps_str != "sin campos faltantes":
            disclaimer_parts.append(f"Datos faltantes: {gaps_str}")
        disclaimer_parts.append("Recomendación: verificación adicional sugerida.")
        return " ".join(disclaimer_parts)


class IntelligentDisclaimerGenerator:
    """
    v4.5.9: Generates contextual disclaimers with specific missing data,
    benchmark information, and actionable improvement steps.
    
    NEVER_BLOCK Principle:
    - Shows EXACTLY what data is missing and why
    - Names the benchmark used as fallback
    - Provides numbered improvement steps with expected confidence gain
    """

    def generate(
        self,
        asset_type: str,
        confidence: float,
        missing_data: List[str],
        benchmark_used: str,
        improvement_steps: List[str]
    ) -> str:
        """
        Generate contextual disclaimer with improvement guidance.
        
        Args:
            asset_type: Type of asset (hotel_schema, description, etc.)
            confidence: Current confidence score (0.0 - 1.0)
            missing_data: List of specific missing data fields
            benchmark_used: Description of benchmark used as fallback
            improvement_steps: Numbered steps to improve confidence
            
        Returns:
            Formatted disclaimer string with context and guidance
        """
        confidence_pct = int(confidence * 100)
        
        # Format missing data as bullet points
        missing_bullets = self._format_missing_data(missing_data)
        
        # Determine confidence category
        if confidence < 0.4:
            confidence_label = "MUY BAJA"
            emoji = "🚨"
        elif confidence < 0.6:
            confidence_label = "BAJA"
            emoji = "⚠️"
        elif confidence < 0.8:
            confidence_label = "MODERADA"
            emoji = "⚡"
        else:
            confidence_label = "ACEPTABLE"
            emoji = "ℹ️"
        
        # Calculate expected confidence after improvements
        expected_confidence = self._estimate_confidence_after_fix(confidence, len(improvement_steps))
        
        # Build disclaimer sections
        disclaimer_parts = [
            f"{emoji} ASSET CON CONFIANZA {confidence_label} ({confidence_pct}/100)",
            "",
            f"Este {asset_type} fue generado usando {benchmark_used} porque:",
            missing_bullets,
            "",
            "PARA MEJORAR ESTE ASSET:",
        ]
        
        # Add numbered improvement steps
        for i, step in enumerate(improvement_steps, 1):
            disclaimer_parts.append(f"{i}. {step}")
        
        disclaimer_parts.extend([
            "",
            f"CONFIDENCIA ESPERADA DESPUÉS DE APLICAR: {expected_confidence:.0%}+"
        ])
        
        return "\n".join(disclaimer_parts)

    def _format_missing_data(self, missing_data: List[str]) -> str:
        """Format missing data as bullet points."""
        if not missing_data:
            return "• Sin datos faltantes específicos"
        
        bullets = []
        for item in missing_data:
            # Provide human-readable translations
            item_lower = item.lower()
            if "gbp" in item_lower or "google_business" in item_lower:
                bullets.append("• Google Business Profile sin datos suficientes")
            elif "reviews" in item_lower or "reseñas" in item_lower:
                bullets.append(f"• Reseñas de clientes ({item})")
            elif "photos" in item_lower or "fotos" in item_lower:
                bullets.append(f"• Fotos de alta calidad ({item})")
            elif "ratings" in item_lower or "calificaciones" in item_lower:
                bullets.append(f"• Ratings/calificaciones ({item})")
            elif "telephone" in item_lower or "phone" in item_lower:
                bullets.append("• Teléfono del hotel")
            elif "address" in item_lower or "direccion" in item_lower:
                bullets.append("• Dirección física verificada")
            elif "amenities" in item_lower or "servicios" in item_lower:
                bullets.append("• Lista de amenities/servicios")
            elif "description" in item_lower or "descripcion" in item_lower:
                bullets.append("• Descripción del establecimiento")
            elif "all" in item_lower:
                bullets.append("• Múltiples campos críticos sin datos")
            else:
                bullets.append(f"• {item}")
        
        return "\n".join(bullets)

    def _estimate_confidence_after_fix(self, current_confidence: float, num_steps: int) -> float:
        """
        Estimate confidence improvement after applying fix steps.
        
        Each improvement step adds approximately 8-12% confidence,
        with diminishing returns for higher starting confidence.
        """
        if num_steps == 0:
            return current_confidence
        
        # Base improvement per step (10% for low confidence, less for higher)
        if current_confidence < 0.4:
            improvement_per_step = 0.12
        elif current_confidence < 0.6:
            improvement_per_step = 0.10
        elif current_confidence < 0.8:
            improvement_per_step = 0.08
        else:
            improvement_per_step = 0.05
        
        total_improvement = num_steps * improvement_per_step
        
        # Cap at 0.95 (never claim 100% confidence)
        estimated = current_confidence + total_improvement
        return min(estimated, 0.95)

    def generate_metadata_dict(
        self,
        asset_type: str,
        confidence: float,
        missing_data: List[str],
        benchmark_used: str,
        improvement_steps: List[str]
    ) -> Dict[str, Any]:
        """
        Generate disclaimer and return metadata dict with all fields.
        
        Returns dict with:
        - disclaimer: Formatted disclaimer text
        - missing_data: Original missing data list
        - benchmark_used: Benchmark used
        - improvement_steps: Original steps list
        - confidence_after_fix: Estimated confidence after applying fixes
        """
        disclaimer = self.generate(
            asset_type, confidence, missing_data, 
            benchmark_used, improvement_steps
        )
        
        estimated_confidence = self._estimate_confidence_after_fix(
            confidence, len(improvement_steps)
        )
        
        return {
            "disclaimer": disclaimer,
            "missing_data": missing_data,
            "benchmark_used": benchmark_used,
            "improvement_steps": improvement_steps,
            "confidence_after_fix": round(estimated_confidence, 2)
        }


def calculate_improvement_score(current_confidence: float, target_confidence: float) -> float:
    """
    Calculate the improvement score (gap to close).
    
    Args:
        current_confidence: Current confidence score (0.0 - 1.0)
        target_confidence: Target confidence score (0.0 - 1.0)
        
    Returns:
        Improvement score = target - current (0.0 - 1.0 range)
        
    Example:
        current: 0.3, target: 0.85 → improvement_score: 0.55
    """
    if target_confidence < current_confidence:
        return 0.0
    
    improvement = target_confidence - current_confidence
    
    # Cap at 1.0
    return min(improvement, 1.0)
