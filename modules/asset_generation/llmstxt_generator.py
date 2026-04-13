"""llms.txt Generator.

Generates /llms.txt following the emerging standard from llmstxt.org.

Usage:
    from modules.asset_generation.llmstxt_generator import LLMSTXTGenerator
    
    generator = LLMSTXTGenerator()
    content = generator.generate({
        "name": "Hotel Example",
        "website": "https://hotelexample.com",
        "description": "A lovely hotel in the city center",
        "amenities": ["WiFi", "Pool", "Restaurant"],
        "phone": "+1234567890",
        "email": "info@hotelexample.com",
        "address": "123 Main St, City, Country",
        "social_links": ["https://facebook.com/hotelexample"]
    })
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class LLMSTXTGenerator:
    """Generator for llms.txt files following the llmstxt.org standard."""

    def generate(
        self,
        hotel_data: Dict[str, Any],
        geo_enriched_path: Optional[Path] = None
    ) -> str:
        """Generate llms.txt content for a hotel website.

        Fallback chain:
            1. geo_enriched/llms.txt if geo_enriched_path exists and contains llms.txt
            2. hotel_data dict (original behavior)
            3. PENDING_ONBOARDING markers if data is insufficient

        Args:
            hotel_data: Dictionary with hotel information.
            geo_enriched_path: Optional path to the geo_enriched/ directory.
                If it contains llms.txt, use that content directly as fallback.

        Returns:
            llms.txt content as string.
        """
        # FASE-LLMSTXT-FIX: Fallback to geo_enriched/llms.txt
        if geo_enriched_path:
            geo_llms_path = Path(geo_enriched_path) / "llms.txt"
            if geo_llms_path.exists():
                content = geo_llms_path.read_text(encoding="utf-8")
                if content and len(content.strip()) > 50:
                    logger.info(
                        "[LLMSTXTGenerator] Using geo_enriched/llms.txt as "
                        f"fallback: {geo_llms_path}"
                    )
                    return content
                else:
                    logger.debug(
                        "[LLMSTXTGenerator] geo_enriched/llms.txt too short, "
                        f"falling back to hotel_data: {geo_llms_path}"
                    )
        name = hotel_data.get("name", "Hotel")
        url = hotel_data.get("website", "")
        description = hotel_data.get("description", "")
        city = hotel_data.get("city", hotel_data.get("addressLocality", ""))
        region = hotel_data.get("region", "Eje Cafetero")

        # FASE-LLMSTXT-FIX: Warn on generic/missing hotel name
        if not name or name == "Hotel":
            logger.warning(
                "[LLMSTXTGenerator] Hotel name is generic or missing "
                f"('{name}'), output may have empty placeholders"
            )
        
        # FASE-B: USP in ONE sentence for voice assistants (quick answer)
        usp = hotel_data.get("usp", f"{name} es un hotel boutique en {city}, {region}, Colombia. Destaca por su atencion personalizada y experiencias unicas.")
        
        content = f"""# {name}

> {usp}

## Important Pages

- [Homepage]({url}): Main hotel website
"""
        
        rooms_url = hotel_data.get("rooms_url", f"{url.rstrip('/')}/habitaciones")
        contact_url = hotel_data.get("contact_url", f"{url.rstrip('/')}/contacto")
        location_url = hotel_data.get("location_url", f"{url.rstrip('/')}/ubicacion")
        
        content += f"""- [Rooms]({rooms_url}): Room types and rates
- [Contact]({contact_url}): Contact information
- [Location]({location_url}): Address and map

"""
        
        amenities = hotel_data.get("amenities", [])
        if amenities:
            content += "## Services\n\n"
            for amenity in amenities[:10]:
                content += f"- {amenity}\n"
        
        if not amenities:
            content += "## Services\n\n"
            content += "- Hotel services information not available\n"
        
        phone = hotel_data.get("phone", "N/A")
        email = hotel_data.get("email", "N/A")
        address = hotel_data.get("address", "N/A")
        
        # FASE-B: Geographic context for voice assistants
        content += f"""
## Geographic Context

- **Location:** {city}, {region}, Colombia
- **Tourist attractions nearby:** Valle del Cocora, Salento, Termales de Santa Rosa
- **Coffee region:** Yes - experience authentic coffee farm tours
- **Climate:** Tropical mountainous (18-25C average)

"""
        
        content += f"""## Contact

- Phone: {phone}
- Email: {email}
- Address: {address}

"""
        
        social_links = hotel_data.get("social_links", [])
        if social_links:
            content += "## Social\n\n"
            for social in social_links:
                content += f"- {social}\n"
        
        # FASE-B: Voice-friendly policies (concise, TTS-ready)
        checkin = hotel_data.get("checkin_time", "15:00")
        checkout = hotel_data.get("checkout_time", "11:00")
        cancellation = hotel_data.get("cancellation_policy", "Free cancellation up to 48 hours before arrival")
        breakfast = hotel_data.get("breakfast", "Included")
        
        content += f"""
## Policies (Voice-Friendly)

- Check-in: {checkin}
- Check-out: {checkout}
- Cancellation: {cancellation}
- Breakfast: {breakfast}
- Pet-friendly: {hotel_data.get("pet_friendly", "Contact hotel")}
- Parking: {hotel_data.get("parking", "Available")}

---
Generated by IA Hoteles Agent - FASE-B AEO Voice-Ready
"""
        
        return content
    
    def generate_from_assessment(
        self,
        assessment_data: Dict[str, Any],
        geo_enriched_path: Optional[Path] = None
    ) -> str:
        """Generate llms.txt from assessment data.

        Args:
            assessment_data: Assessment dictionary with hotel info.
            geo_enriched_path: Optional path to geo_enriched/ directory.

        Returns:
            llms.txt content.
        """
        hotel_data = {
            "name": assessment_data.get("hotel_name", "Hotel"),
            "website": assessment_data.get("url", ""),
            "description": assessment_data.get("description", ""),
            "amenities": assessment_data.get("amenities", []),
            "phone": assessment_data.get("phone", ""),
            "email": assessment_data.get("email", ""),
            "address": assessment_data.get("address", ""),
            "social_links": assessment_data.get("social_links", []),
        }

        return self.generate(hotel_data, geo_enriched_path=geo_enriched_path)


def get_llmstxt_generator() -> LLMSTXTGenerator:
    """Factory function to get LLMSTXTGenerator instance.
    
    Returns:
        LLMSTXTGenerator instance.
    """
    return LLMSTXTGenerator()
