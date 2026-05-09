"""WhatsApp conflict resolution guide generator.

Generates a Markdown guide when WhatsApp numbers conflict across sources
(web scraping vs Google Business Profile). The guide shows both numbers,
recommends which to use, and provides a resolution checklist.

Generated as part of the v4complete pipeline when whatsapp_conflict pain
is detected.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from datetime import datetime


class WhatsAppConflictGuideGenerator:
    """Generates a resolution guide when WhatsApp numbers conflict."""

    def generate(
        self,
        hotel_name: str,
        phone_web: Optional[str],
        phone_gbp: Optional[str],
        gbp_rating: Optional[float] = None,
        gbp_review_count: Optional[int] = None,
        schema_telephone: Optional[str] = None,
        phone_wa_href: Optional[str] = None,
    ) -> str:
        """Generate a Markdown resolution guide for WhatsApp conflicts.

        Args:
            hotel_name: Name of the hotel.
            phone_web: Phone number found on the hotel website (schema).
            phone_gbp: Phone number found on Google Business Profile.
            gbp_rating: GBP rating (used to recommend the stronger source).
            gbp_review_count: Number of GBP reviews.
            schema_telephone: Phone from schema.org markup.
            phone_wa_href: Phone number extracted from wa.me href in HTML.
                May differ from phone_web if the wa.me link points to a
                different number than the schema telephone.

        Returns:
            Markdown string with the resolution guide.
        """
        recommendation = self._build_recommendation(
            phone_web, phone_gbp, gbp_rating, gbp_review_count
        )
        
        sections = []
        
        # Header
        sections.append(f"# Guia de Resolucion: Conflicto de WhatsApp")
        sections.append(f"## {hotel_name}")
        sections.append("")
        sections.append(f"**Fecha**: {datetime.now().strftime('%Y-%m-%d')}")
        sections.append("")
        
        # Numbers table
        sections.append("### Numeros Detectados")
        sections.append("")
        sections.append("| Fuente | Numero | Referencia |")
        sections.append("|--------|--------|------------|")
        
        web_ref = "Extraido del markup Schema.org del sitio web"
        gbp_ref = f"Perfil verificado con {gbp_review_count} reseñas" if gbp_review_count else "Perfil de Google Business"
        
        sections.append(f"| Sitio web (schema) | {phone_web or 'No detectado'} | {web_ref} |")
        sections.append(f"| Google Business Profile | {phone_gbp or 'No detectado'} | {gbp_ref} |")
        
        # PATCH-6: Show wa.me href number if different from schema phone
        if phone_wa_href and phone_wa_href != phone_web:
            wa_ref = "Numero extraido del enlace wa.me en el HTML del sitio"
            sections.append(f"| Boton WhatsApp (wa.me) | +{phone_wa_href} | {wa_ref} |")
        
        sections.append("")
        
        # Detect wa.me href conflict
        wa_me_conflict = False
        if phone_wa_href and phone_gbp:
            # Normalize both for comparison (strip spaces, dashes, leading +)
            norm_href = phone_wa_href.replace(" ", "").replace("-", "").lstrip("+")
            norm_gbp = phone_gbp.replace(" ", "").replace("-", "").lstrip("+")
            if norm_href != norm_gbp:
                wa_me_conflict = True
                sections.append("### Conflicto: Boton WhatsApp apunta a numero diferente")
                sections.append("")
                sections.append(f"El boton de WhatsApp en su sitio web contiene el enlace `wa.me/{phone_wa_href}`,")
                sections.append(f"pero el numero registrado en Google Business Profile es `{phone_gbp}`.")
                sections.append("")
                sections.append("Esto significa que cuando un visitante hace clic en el boton de WhatsApp,")
                sections.append("se comunicara con un numero **diferente** al que aparece en Google.")
                sections.append("Esto genera confusion y puede resultar en mensajes perdidos.")
                sections.append("")
        
        # Problem description
        sections.append("### El Problema")
        sections.append("")
        sections.append("Cuando un visitante busca su hotel y encuentra numeros diferentes en su")
        sections.append("web vs Google, se genera confusion. Esto resulta en:")
        sections.append("- Pérdida de confianza del potencial huésped")
        sections.append("- Reservas perdidas por frustracion")
        sections.append("- Mensajes a numeros incorrectos o inactivos")
        sections.append("")
        
        # Recommendation
        sections.append("### Numero Recomendado")
        sections.append("")
        sections.append(recommendation)
        sections.append("")
        
        # Checklist
        sections.append("### Checklist de Resolucion")
        sections.append("")
        sections.append("- [ ] Decida cual es el numero de WhatsApp correcto (el que vigila activamente)")
        sections.append("- [ ] Actualice su perfil de Google Business Profile con el numero correcto")
        sections.append("- [ ] Actualice el numero en el schema de su sitio web")
        sections.append("- [ ] Si usa WhatsApp Business, verifique que el perfil este completo")
        sections.append("- [ ] Verifique que el mensaje de bienvenida en WhatsApp este configurado")
        sections.append("- [ ] Haga una prueba: llame/envie mensaje al numero desde otro telefono")
        sections.append("")
        
        # How to update GBP
        sections.append("### Como Actualizar el Numero en Google Business Profile")
        sections.append("")
        sections.append("1. Ingrese a [Google Business Profile](https://business.google.com/)")
        sections.append("2. Seleccione su hotel")
        sections.append('3. Vaya a "Informacion"')
        sections.append('4. Edite el campo "Telefono"')
        sections.append("5. Ingrese el numero correcto con indicativo de pais (+57)")
        sections.append("6. Guarde los cambios")
        sections.append("")
        
        # How to update web
        sections.append("### Como Actualizar el Numero en su Sitio Web")
        sections.append("")
        sections.append("1. Ingrese al administrador de su sitio (WordPress, etc.)")
        sections.append("2. Busque el numero actual de contacto/WhatsApp")
        sections.append("3. Reemplazelo con el numero correcto")
        sections.append("4. Si tiene Schema.org markup, actualice el campo `telephone`")
        sections.append("5. Guarde y verifique que el boton de WhatsApp apunte al numero correcto")
        sections.append("")
        
        # Footer
        sections.append("---")
        sections.append("")
        sections.append("*Guia generada automaticamente por IA Hoteles v4.0*")
        
        return "\n".join(sections)
    
    def _build_recommendation(
        self,
        phone_web: Optional[str],
        phone_gbp: Optional[str],
        gbp_rating: Optional[float],
        gbp_review_count: Optional[int],
    ) -> str:
        """Build recommendation for which number to use.
        
        Logic:
        1. If GBP has 10+ reviews, recommend GBP number (more public trust)
        2. If web number is in schema, recommend it (more recent)
        3. If neither has clear advantage, show both and let client decide
        """
        if phone_gbp and gbp_review_count and gbp_review_count >= 10:
            return (
                f"**Recomendamos usar el numero de Google Business Profile:** "
                f"`{phone_gbp}`\n\n"
                f"Razon: Su perfil de Google tiene {gbp_review_count} reseñas y "
                f"calificacion de {gbp_rating}/5. Este es el numero que los "
                f"viajeros confian al buscar su hotel. Unificarlo en su web "
                f"eliminara la confusion."
            )
        elif phone_web:
            return (
                f"**Recomendamos usar el numero de su sitio web:** "
                f"`{phone_web}`\n\n"
                f"Razon: Este es el numero que aparece en su propio sitio web. "
                f"Unifiquelo en Google Business Profile para que todos los "
                f"canales muestren el mismo contacto."
            )
        elif phone_gbp:
            return (
                f"**Recomendamos usar el numero de Google Business Profile:** "
                f"`{phone_gbp}`\n\n"
                f"Razon: Este es el numero visible en Google. Unifiquelo en "
                f"su sitio web para mantener consistencia."
            )
        else:
            return (
                "No se pudo determinar cual numero es el correcto. "
                "Por favor, verifique cual numero vigila activamente y "
                "actualice ambos canales (web y Google) con ese numero."
            )
