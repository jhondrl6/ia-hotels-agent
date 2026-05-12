"""
Open Graph Meta Tags Generator for IA Hoteles Agent.

Generates Open Graph meta tags for hotels using verified GBP data.
Closes gap B4 ($379K/month exposed).

Created as part of FASE-4: Generar Asset B4 Open Graph.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


@dataclass
class HotelOGData:
    """Data required for Open Graph generation."""
    hotel_name: str
    description: str
    rating: float
    review_count: int
    address: str
    phone: str
    website_url: str = ""
    photo_url: str = ""


class OpenGraphGenerator:
    """
    Generates Open Graph meta tags for hotels.
    
    Uses verified GBP data to create proper Open Graph tags
    for social media sharing and SEO optimization.
    """
    
    def __init__(self):
        """Initialize the Open Graph generator."""
        self.asset_type = "open_graph"
        self.output_extension = ".html"
    
    def generate(self, hotel_data: Dict[str, Any], output_dir: Path) -> Path:
        """
        Generate Open Graph meta tags HTML file.
        
        Args:
            hotel_data: Dictionary containing hotel information
            output_dir: Directory to write the output file
            
        Returns:
            Path to the generated file
        """
        try:
            # Extract data from hotel_data
            og_data = self._extract_og_data(hotel_data)
            
            # Generate HTML content
            html_content = self._generate_html(og_data)
            
            # Write to file
            output_path = output_dir / f"open_graph_meta{self.output_extension}"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Generated Open Graph meta tags at {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating Open Graph meta tags: {e}")
            raise
    
    def generate_content(self, hotel_data: Dict[str, Any]) -> str:
        """
        Generate Open Graph HTML content without writing to file.
        Public API for use by other modules (e.g. conditional_generator).
        
        Args:
            hotel_data: Dictionary containing hotel information
            
        Returns:
            HTML string with Open Graph meta tags
        """
        og_data = self._extract_og_data(hotel_data)
        return self._generate_html(og_data)
    
    def _extract_og_data(self, hotel_data: Dict[str, Any]) -> HotelOGData:
        """
        Extract Open Graph data from hotel data.
        
        Args:
            hotel_data: Raw hotel data dictionary
            
        Returns:
            HotelOGData object with extracted information
        """
        # Get hotel name — validate explicitly, no cross-hotel defaults
        hotel_name = hotel_data.get('hotel_name') or hotel_data.get('name', '')
        if not hotel_name or hotel_name.strip() == '':
            raise ValueError(f"open_graph_generator requiere hotel_name válido. Keys recibidas: {list(hotel_data.keys())}")
        
        # Get description - create from available data
        description = self._create_description(hotel_data)
        
        # Get rating and review count — no hardcoded defaults
        rating = hotel_data.get('rating')
        review_count = hotel_data.get('review_count') or hotel_data.get('reviews')
        
        # Get address
        address = hotel_data.get('address', '')
        if not address:
            address = hotel_data.get('gbp_address', '')
        
        # Get phone
        phone = hotel_data.get('phone', '')
        if not phone:
            phone = hotel_data.get('gbp_phone', '')
        
        # Get website URL — validate explicitly, no cross-hotel defaults
        website_url = hotel_data.get('website_url') or hotel_data.get('website') or hotel_data.get('url', '')
        if not website_url:
            raise ValueError("open_graph_generator requiere website_url válido")
        
        # Get photo URL - prioritize GBP photos
        photo_url = self._get_photo_url(hotel_data)
        
        return HotelOGData(
            hotel_name=hotel_name,
            description=description,
            rating=float(rating) if rating else None,
            review_count=int(review_count) if review_count else None,
            address=address,
            phone=phone,
            website_url=website_url,
            photo_url=photo_url
        )
    
    def _create_description(self, hotel_data: Dict[str, Any]) -> str:
        """
        Create a description from available hotel data.
        
        Args:
            hotel_data: Hotel data dictionary
            
        Returns:
            Formatted description string
        """
        # Try to get existing description
        description = hotel_data.get('description', '')
        if description:
            return description
        
        # Create description from available data
        hotel_name = hotel_data.get('hotel_name') or hotel_data.get('name', 'Hotel')
        address = hotel_data.get('address', '')
        rating = hotel_data.get('rating')
        review_count = hotel_data.get('review_count') or hotel_data.get('reviews')
        
        # Build description
        parts = []
        
        if address:
            # Extract city from address
            city = self._extract_city(address)
            parts.append(f"Hotel boutique en {city}")
        else:
            parts.append("Hotel boutique en el Eje Cafetero")
        
        if rating and review_count:
            parts.append(f"Calificación {rating}/5 con {review_count} reseñas")
        
        parts.append("Experiencia única de hospedaje en Colombia")
        
        return ". ".join(parts) + "."
    
    def _extract_city(self, address: str) -> str:
        """
        Extract city from address string.
        
        Args:
            address: Full address string
            
        Returns:
            City name or default
        """
        if not address:
            return "el Eje Cafetero"
        
        # Common patterns in Colombian addresses
        parts = address.split(',')
        if len(parts) >= 2:
            # Usually city is the second or third part
            for part in parts[1:]:
                part = part.strip()
                if part and not part.isdigit():
                    return part
        
        return "el Eje Cafetero"
    
    def _get_photo_url(self, hotel_data: Dict[str, Any]) -> str:
        """
        Get photo URL from hotel data.
        
        Args:
            hotel_data: Hotel data dictionary
            
        Returns:
            Photo URL or empty string
        """
        # Try to get from GBP photos
        photos = hotel_data.get('photos', hotel_data.get('gbp_photos', []))
        if photos and isinstance(photos, list) and len(photos) > 0:
            # Get first photo
            photo = photos[0]
            if isinstance(photo, dict):
                return photo.get('url', photo.get('photo_url', ''))
            elif isinstance(photo, str):
                return photo
        
        # Try other photo fields
        for field in ['photo_url', 'image_url', 'main_photo']:
            if field in hotel_data and hotel_data[field]:
                return hotel_data[field]
        
        # Return empty - no placeholder
        return ""
    
    def _generate_html(self, og_data: HotelOGData) -> str:
        """
        Generate HTML with Open Graph meta tags.
        
        Args:
            og_data: Open Graph data
            
        Returns:
            HTML string with meta tags
        """
        # Build description with rating if available
        description = og_data.description
        if og_data.rating and og_data.review_count:
            if str(og_data.rating) not in description:
                description += f" Calificación {og_data.rating}/5 con {og_data.review_count} reseñas."
        
        # Start building HTML
        lines = [
            f"<!-- Open Graph Meta Tags for {og_data.hotel_name} -->",
            "<!-- Generated by IA Hoteles Agent - FASE-4 -->",
            "<!-- Inyectar en header.php o plugin SEO de WordPress -->",
            "",
            "<!-- Open Graph / Facebook -->",
            f'<meta property="og:type" content="hotel" />',
            f'<meta property="og:title" content="{og_data.hotel_name}" />',
            f'<meta property="og:description" content="{description}" />',
            f'<meta property="og:url" content="{og_data.website_url}" />',
            f'<meta property="og:site_name" content="{og_data.hotel_name}" />',
            f'<meta property="og:locale" content="es_CO" />',
        ]
        
        # Add image if available
        if og_data.photo_url:
            lines.append(f'<meta property="og:image" content="{og_data.photo_url}" />')
            lines.append(f'<meta property="og:image:alt" content="{og_data.hotel_name}" />')
        
        # Add additional hotel-specific tags
        lines.extend([
            "",
            "<!-- Additional Hotel Meta Tags -->",
            f'<meta name="description" content="{description}" />',
            f'<meta name="rating" content="{og_data.rating}" />',
            f'<meta name="reviewCount" content="{og_data.review_count}" />',
        ])
        
        # Add contact info if available
        if og_data.phone:
            lines.append(f'<meta name="telephone" content="{og_data.phone}" />')
        
        if og_data.address:
            lines.append(f'<meta name="address" content="{og_data.address}" />')
        
        # Add Twitter Card tags
        lines.extend([
            "",
            "<!-- Twitter Card -->",
            f'<meta name="twitter:card" content="summary_large_image" />',
            f'<meta name="twitter:title" content="{og_data.hotel_name}" />',
            f'<meta name="twitter:description" content="{description}" />',
        ])
        
        if og_data.photo_url:
            lines.append(f'<meta name="twitter:image" content="{og_data.photo_url}" />')
        
        # Add structured data for hotels
        lines.extend([
            "",
            "<!-- Structured Data for Hotels -->",
            '<script type="application/ld+json">',
            '{',
            '  "@context": "https://schema.org",',
            '  "@type": "Hotel",',
            f'  "name": "{og_data.hotel_name}",',
            f'  "description": "{description}",',
            f'  "url": "{og_data.website_url}",',
        ])
        
        if og_data.photo_url:
            lines.append(f'  "image": "{og_data.photo_url}",')
        
        if og_data.address:
            lines.extend([
                '  "address": {',
                '    "@type": "PostalAddress",',
                f'    "addressLocality": "{self._extract_city(og_data.address)}",',
                '    "addressCountry": "CO"',
                '  },',
            ])
        
        if og_data.phone:
            lines.append(f'  "telephone": "{og_data.phone}",')
        
        if og_data.rating and og_data.review_count:
            lines.extend([
                '  "aggregateRating": {',
                '    "@type": "AggregateRating",',
                f'    "ratingValue": "{og_data.rating}",',
                f'    "reviewCount": "{og_data.review_count}"',
                '  },',
            ])
        
        lines.extend([
            '  "priceRange": "$"',
            '}',
            '</script>',
        ])
        
        return '\n'.join(lines)


def generate_open_graph_asset(hotel_data: Dict[str, Any], output_dir: Path) -> Path:
    """
    Convenience function to generate Open Graph asset.
    
    Args:
        hotel_data: Hotel data dictionary
        output_dir: Output directory
        
    Returns:
        Path to generated file
    """
    generator = OpenGraphGenerator()
    return generator.generate(hotel_data, output_dir)


__all__ = [
    'OpenGraphGenerator',
    'HotelOGData',
    'generate_open_graph_asset',
]