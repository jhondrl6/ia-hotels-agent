from typing import Dict, Any
import json

class SchemaGenerator:
    """Generates JSON-LD Schema.org markup for hotels."""
    
    def generate(self, hotel_data: Dict[str, Any]) -> str:
        """
        Generates a comprehensive Hotel Schema.
        
        Args:
            hotel_data: Dictionary containing hotel details (name, address, etc.)
            
        Returns:
            String containing the JSON-LD script.
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "LodgingBusiness",
            "name": hotel_data.get("nombre") or hotel_data.get("name", "Hotel"),
            "description": hotel_data.get("description", f"Hotel en {hotel_data.get('ubicacion', 'Colombia')}"),
            "url": hotel_data.get("url", ""),
            "address": {
                "@type": "PostalAddress",
                "streetAddress": hotel_data.get("direccion") or hotel_data.get("ubicacion", ""),
                "addressLocality": hotel_data.get("ciudad") or self._extract_city(hotel_data.get("ubicacion", "")),
                "addressRegion": hotel_data.get("region") or "",
                "addressCountry": "CO"
            },
        }

        # Add images if available
        images = hotel_data.get("imagenes", []) or hotel_data.get("images", [])
        if images:
            schema["image"] = images[:5]  # Limit to top 5 images

        # Add price range if available - v3.3.1 Fix: Use proper range separator
        min_price = hotel_data.get("precio_min")
        max_price = hotel_data.get("precio_max")
        if min_price and max_price:
            schema["priceRange"] = f"{min_price} - {max_price} COP"
        elif hotel_data.get("precio_promedio"):
            schema["priceRange"] = f"{hotel_data.get('precio_promedio')} COP"
        
        # Add star rating - v3.3.1 Hierarchical
        rating = hotel_data.get("rating")
        if rating:
            schema["starRating"] = {
                "@type": "Rating",
                "ratingValue": str(rating)
            }
            # Also keep aggregateRating for SEO
            schema["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": str(rating),
                "reviewCount": str(hotel_data.get("reviews", 0))
            }

        # Add amenities - v3.3.1 Enhanced
        services = hotel_data.get("servicios", [])
        if services:
            schema["amenityFeature"] = [
                {
                    "@type": "LocationFeatureSpecification", 
                    "name": service, 
                    "value": True
                }
                for service in services
            ]

        # v3.3.1: FAQPage Integration
        faqs = hotel_data.get("faqs", [])
        if faqs and isinstance(faqs, list):
            faq_main_entity = []
            for faq in faqs:
                if isinstance(faq, dict) and "pregunta" in faq and "respuesta" in faq:
                    faq_main_entity.append({
                        "@type": "Question",
                        "name": faq["pregunta"],
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": faq["respuesta"]
                        }
                    })
            
            if faq_main_entity:
                # We append FAQPage to the graph if we were using @graph, 
                # but here we just nest it or use a list if needed.
                # Standard practice for single block is including it in a @graph or separate.
                # Here we will return a list [LodgingBusiness, FAQPage] to be valid JSON-LD
                faq_page = {
                    "@context": "https://schema.org",
                    "@type": "FAQPage",
                    "mainEntity": faq_main_entity
                }
                return json.dumps([schema, faq_page], indent=2, ensure_ascii=False)

        return json.dumps(schema, indent=2, ensure_ascii=False)

    def _extract_city(self, location: str) -> str:
        if not location:
            return ""
        parts = location.split(',')
        return parts[0].strip()
