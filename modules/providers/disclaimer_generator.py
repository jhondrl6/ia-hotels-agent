"""
Disclaimer Generator for IA Hoteles Agent v4.0

Generates honest disclaimers based on confidence levels and data sources.
Follows the NEVER_BLOCK principle - always provides output with transparency.
"""

from typing import List, Optional


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
