"""LLMs.txt Generator - Creates llms.txt for AI discovery.

This generator creates an llms.txt file following the specification
for AI crawlers like ChatGPT, Perplexity, and Claude.

The llms.txt format is a markdown file at the site root that provides
AI systems with a comprehensive summary of the website's content.

Reference: GEO FIELD MAPPING.md, FASE-3 specification
"""

import textwrap
from typing import Optional

from data_models.canonical_assessment import CanonicalAssessment


class LLMsTxtGenerator:
    """Generates llms.txt files for AI discovery optimization.
    
    The llms.txt format is a markdown file that provides AI systems
    with structured, citable information about a website. It is NOT
    robots.txt - it's a new standard for AI-native content discovery.
    
    Specification source: https://llmstxt.org/
    """

    # Maximum line length for readability
    MAX_LINE_LENGTH = 80

    def generate(self, hotel_data: CanonicalAssessment) -> str:
        """Generate complete llms.txt content.
        
        Args:
            hotel_data: CanonicalAssessment with hotel information.
            
        Returns:
            Complete llms.txt content as string.
        """
        sections = []
        
        # H1 - Hotel name as document title
        sections.append(f"# {hotel_data.site_metadata.title}")
        
        # URL
        sections.append(f"**URL:** {hotel_data.url}")
        sections.append("")
        
        # H2: Acerca de
        sections.append("## Acerca de")
        about_text = self._generate_about(hotel_data)
        sections.append(about_text)
        sections.append("")
        
        # H2: Ubicacion
        sections.append("## Ubicacion")
        location_text = self._generate_location(hotel_data)
        sections.append(location_text)
        sections.append("")
        
        # H2: Amenities y Servicios
        sections.append("## Amenities y Servicios")
        amenities_text = self._generate_amenities(hotel_data)
        sections.append(amenities_text)
        sections.append("")
        
        # H2: Contacto
        sections.append("## Contacto")
        contact_text = self._generate_contact(hotel_data)
        sections.append(contact_text)
        sections.append("")
        
        # H2: CTA (Call to Action)
        sections.append("## Reserva y Contacto")
        cta_text = self._generate_cta(hotel_data)
        sections.append(cta_text)
        sections.append("")
        
        return "\n".join(sections)

    def _generate_about(self, hotel_data: CanonicalAssessment) -> str:
        """Generate About section with hotel description.
        
        This description is critical for AI systems to understand
        what the hotel offers and who it caters to.
        """
        lines = []
        
        # Primary description
        description = hotel_data.site_metadata.description
        if description and len(description) > 50:
            lines.append(description)
        else:
            # Fallback description
            lines.append(f"{hotel_data.site_metadata.title} es un hotel boutique ubicado en Colombia, ")
            lines.append("ofreciendo una experiencia única para viajeros que buscan ")
            lines.append("comodidad, servicio personalizado y autenticidad local.")
        
        lines.append("")
        
        # Add key differentiators if available
        if hotel_data.gbp_analysis:
            gbp = hotel_data.gbp_analysis
            
            # Review summary if available
            if gbp.profile_url:
                lines.append(f"**Perfil de Google Business:** {gbp.profile_url}")
                lines.append("")
        
        # Property type
        if hotel_data.site_metadata.cms_detected:
            lines.append(f"**Tipo de propiedad:** Hotel {hotel_data.site_metadata.cms_detected}")
            lines.append("")
        
        return "\n".join(lines)

    def _generate_location(self, hotel_data: CanonicalAssessment) -> str:
        """Generate Location section with precise geographic information.
        
        AI systems need precise location data to answer user queries
        about nearby attractions, transportation, etc.
        """
        lines = []
        
        # Address if available
        if hotel_data.gbp_analysis and hotel_data.gbp_analysis.profile_url:
            lines.append(f"**Perfil de Google Business:** {hotel_data.gbp_analysis.profile_url}")
            lines.append("")
        
        # City extraction from URL or metadata
        url = hotel_data.url
        if url:
            # Extract domain/city hints
            lines.append(f"**Sitio web:** {url}")
            lines.append("")
        
        # Note about Colombia
        lines.append("**País:** Colombia")
        lines.append("")
        
        return "\n".join(lines)

    def _generate_amenities(self, hotel_data: CanonicalAssessment) -> str:
        """Generate Amenities section from GBP categories.
        
        Categories are used to populate this section as they represent
        the hotel's key offerings in a structured way.
        """
        lines = []
        
        if hotel_data.gbp_analysis and hotel_data.gbp_analysis.categories:
            categories = hotel_data.gbp_analysis.categories
            lines.append("**Servicios destacados:**")
            lines.append("")
            
            # Map common categories to formatted list
            for category in categories[:10]:  # Limit to 10
                lines.append(f"- {category}")
            
            lines.append("")
        else:
            lines.append("**Servicios:** Hospedaje, restaurante, WiFi, recepción 24 horas.")
            lines.append("")
        
        return "\n".join(lines)

    def _generate_contact(self, hotel_data: CanonicalAssessment) -> str:
        """Generate Contact section with multiple contact channels."""
        lines = []
        
        # Primary contact info
        contact_info = []
        
        if hotel_data.gbp_analysis:
            gbp = hotel_data.gbp_analysis
            # Phone number from GBP if available
            # Note: actual phone extraction depends on data availability
        
        # Website URL as primary contact channel
        lines.append(f"**Sitio web:** {hotel_data.url}")
        lines.append("")
        
        # Note about direct booking
        lines.append("Para reservas directas y consultas específicas, ")
        lines.append("visite nuestro sitio web o contacte directamente.")
        lines.append("")
        
        return "\n".join(lines)

    def _generate_cta(self, hotel_data: CanonicalAssessment) -> str:
        """Generate Call to Action section.
        
        Clear CTAs help AI systems direct users to take desired actions.
        """
        lines = [
            "## Reserva tu experiencia",
            "",
            f"**Reserva en línea:** Visite nuestro sitio web",
            f"**URL:** {hotel_data.url}",
            "",
            "Para obtener la mejor tarifa garantizada, reserve directamente ",
            "a través de nuestro sitio web oficial.",
            "",
        ]
        
        return "\n".join(lines)
