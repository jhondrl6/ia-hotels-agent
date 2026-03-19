"""WhatsApp floating button generator (no-LLM).

Generates a ready-to-paste HTML/CSS/JS snippet that:
- Opens a WhatsApp chat via wa.me
- Tracks clicks via GA4 (gtag) when available
- Minimal dependency for "Sin IT" clients.

Client-facing instructions are Spanish. Code stays conservative and portable.
"""

from __future__ import annotations

from typing import Any, Dict
from urllib.parse import quote


class WhatsAppButtonGenerator:
    """Generates a floating WhatsApp CTA button snippet."""

    def generate(self, hotel_data: Dict[str, Any], 
                 fuga: Dict = None,
                 reason: str = None) -> Dict[str, Any]:
        """Genera botón WhatsApp con contexto de fuga.
        
        Args:
            hotel_data: Datos del hotel
            fuga: Fuga específica SIN_WHATSAPP_VISIBLE detectada
            reason: Justificación de por qué se genera
        """
        hotel_name = str(hotel_data.get("nombre") or "Hotel").strip() or "Hotel"
        raw_number = hotel_data.get("whatsapp") or hotel_data.get("telefono") or hotel_data.get("phone") or ""
        digits_only = "".join(ch for ch in str(raw_number) if ch.isdigit())

        # Conservative fallback for Colombia if user forgot country code.
        # If the number is 10 digits (e.g. 3xxxxxxxxx) assume +57.
        if len(digits_only) == 10 and digits_only.startswith("3"):
            digits_only = "57" + digits_only

        # Last-resort placeholder (keeps generator deterministic).
        if not digits_only:
            digits_only = "573001234567"

        default_message = f"Hola, quiero reservar en {hotel_name}. ¿Tienen disponibilidad?"
        message_encoded = quote(default_message, safe="")

        html_code = f"""<!-- IAH: Botón WhatsApp Flotante (Directo) -->
<!-- Hotel: {hotel_name} -->
<!-- v3.3.1: No-IT ready, automatic GA4 tracking -->

<style>
  #iah-whatsapp-cta {{
    position: fixed;
    right: 20px;
    bottom: 20px;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: #25D366;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    z-index: 999999;
    transition: transform 0.3s ease;
  }}

  #iah-whatsapp-cta:hover {{ transform: scale(1.1); }}

  #iah-whatsapp-cta svg {{
    width: 32px;
    height: 32px;
    fill: white;
  }}
</style>

<a id="iah-whatsapp-cta" href="https://wa.me/{digits_only}?text={message_encoded}" target="_blank" rel="noopener">
  <svg viewBox="0 0 32 32">
    <path d="M19.11 17.23c-.28-.14-1.64-.81-1.9-.9-.25-.09-.44-.14-.62.14-.19.28-.71.9-.87 1.08-.16.19-.32.21-.6.07-.28-.14-1.16-.43-2.21-1.37-.82-.73-1.37-1.64-1.53-1.92-.16-.28-.02-.43.12-.57.12-.12.28-.32.42-.48.14-.16.19-.28.28-.46.09-.19.05-.35-.02-.5-.07-.14-.62-1.5-.85-2.06-.23-.55-.46-.48-.62-.49h-.53c-.19 0-.5.07-.76.35-.25.28-1 1-1 2.43 0 1.42 1.03 2.8 1.18 2.99.14.19 2.02 3.08 4.89 4.32.68.29 1.2.46 1.61.59.68.22 1.3.19 1.79.11.55-.08 1.64-.67 1.87-1.32.23-.64.23-1.19.16-1.32-.07-.12-.25-.19-.53-.33zM16.04 28c-2.1 0-4.16-.55-5.98-1.6L4 28l1.65-6.02A11.86 11.86 0 0 1 4 16.04C4 9.4 9.4 4 16.04 4c3.2 0 6.21 1.25 8.48 3.52A11.9 11.9 0 0 1 28 16.04C28 22.6 22.6 28 16.04 28zm0-21.9C10.44 6.1 6.1 10.44 6.1 16.04c0 1.87.52 3.69 1.51 5.28l.19.31-.98 3.57 3.66-.96.3.18c1.56.92 3.35 1.41 5.26 1.41 5.6 0 9.94-4.34 9.94-9.94 0-2.66-1.04-5.17-2.92-7.05a9.9 9.9 0 0 0-7.04-2.92z"/>
  </svg>
</a>

<script>
  document.getElementById('iah-whatsapp-cta').addEventListener('click', function() {{
    if (typeof gtag === 'function') {{
      gtag('event', 'conversion', {{
        'send_to': 'whatsapp_click',
        'event_category': 'WhatsApp',
        'event_label': '{hotel_name}'
      }});
    }}
  }});
</script>
"""

        implementation_guide_sections = []
        
        if reason:
            implementation_guide_sections.append(f"> **🎯 Por qué este archivo:** {reason}")
            implementation_guide_sections.append("")
        
        implementation_guide_sections.append(f"# Guía de Implementación - Botón WhatsApp")
        implementation_guide_sections.append(f"## {hotel_name} (v3.3.1 - Sin IT)")
        implementation_guide_sections.append("")
        implementation_guide_sections.append("Este entregable agrega un botón flotante de WhatsApp directo en tu web.")
        
        if fuga:
            implementation_guide_sections.append("\n## 📊 Impacto Detectado\n")
            implementation_guide_sections.append(f"- **Problema:** {fuga.get('detalle', 'Sin WhatsApp visible')}")
            implementation_guide_sections.append(f"- **Pérdida mensual:** ${fuga.get('impacto_estimado_COP_mes', 0):,.0f} COP")
            implementation_guide_sections.append(f"- **Urgencia:** {fuga.get('urgencia', 'ALTA')}")
            implementation_guide_sections.append("")
        
        implementation_guide_sections.extend([
            "\n## Instrucciones Rápidas",
            "1. Abre `boton_whatsapp_codigo.html`.",
            "2. Copia TODO el contenido.",
            "3. Pégalo en tu WordPress usando **WPCode** (sección Footer) o antes de la etiqueta `</body>` en tu sitio.",
            "\n## Ventajas",
            "- **1 Clic**: El cliente te escribe directamente.",
            "- **Sin IT**: No requiere configurar GTM para funcionar.",
            "- **Auto-tracking**: Si tienes Google Analytics, intentará medir el clic automáticamente.",
        ])
        
        implementation_guide = "\n".join(implementation_guide_sections)

        return {
            "html_code": html_code,
            "implementation_guide": implementation_guide,
        }
