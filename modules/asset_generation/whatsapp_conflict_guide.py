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
        """Devuelve la seccion de cierre: NINGUN numero se declara operativo.

        FASE-B (REFACTOR-WHATSAPP, AC2). Logica retirada: hasta aqui la guia elegia
        el numero "correcto" por cantidad de reseñas de GBP (>=10) y, a falta de
        esas, por antiguedad aparente de la web. Un numero en CONFLICTO no es un
        numero verificado: el conteo de reseñas mide confianza del perfil, no que
        alguien conteste ese WhatsApp. Como un numero elegido mal se publica como
        boton operativo, la eleccion corresponde exclusivamente al hotel.

        `gbp_rating` y `gbp_review_count` se conservan en la firma porque son
        contexto que el llamador ya tiene, y ahora son solo informativos: ninguna
        decision se apoya en ellos.
        """
        candidatos = []
        if phone_web:
            candidatos.append(f"- **Web:** `{phone_web}`")
        if phone_gbp:
            linea = f"- **Google Business Profile:** `{phone_gbp}`"
            if gbp_review_count:
                linea += f" (perfil con {gbp_review_count} reseñas"
                linea += (
                    f" y nota {gbp_rating}/5)"
                    if gbp_rating is not None
                    else ")"
                )
            candidatos.append(linea)

        if not candidatos:
            return (
                "**Ningun candidato de numero fue capturado en esta auditoria.** "
                "El canal queda sin resolver hasta que el hotel indique cual es el "
                "numero que atiende. Sin ese dato no se publica boton alguno."
            )

        return (
            "**Los dos numeros son candidatos, ninguno es el oficial hasta que usted "
            "lo confirme.**\n\n"
            + "\n".join(candidatos)
            + "\n\n"
            "Esta guia **no elige** cual de ellos publicar. Elegir por cantidad de "
            "resenas o por cual aparece en la web volveria a producir el defecto que "
            "se esta corrigiendo: un boton operativo apuntando a un numero que nadie "
            "confirma como canal de reservas.\n\n"
            "Acciones requeridas antes de dar el canal por resuelto:\n"
            "1. Confirmar por escrito cual de los numeros atiende WhatsApp hoy.\n"
            "2. Retirar o actualizar el otro en su canal (web o Google Business "
            "Profile) para que no queden dos versiones en publico.\n"
            "3. Verificar que el boton, una vez generado, abre el chat del numero "
            "confirmado.\n\n"
            "Hasta el paso 1 el canal se reporta como **preparacion pendiente**, no "
            "como instalacion realizada, y no se promete boton listo."
        )
