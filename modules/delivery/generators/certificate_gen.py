"""Certificate Generator v2.5.3

Generates Markdown certificates for Elite PLUS package:
- Certificado Reserva Directa
- Certificado Web Optimizada

Note: PDF generation planned for v2.6. Current version outputs Markdown templates.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional


class CertificateGenerator:
    """Generates certificates for Elite PLUS clients."""

    CERTIFICATE_TYPES = [
        "reserva_directa",
        "web_optimizada",
    ]

    def generate_all(
        self, 
        hotel_data: Dict[str, Any], 
        output_dir: Path
    ) -> List[str]:
        """
        Generate all certificates for Elite PLUS package.
        
        Args:
            hotel_data: Hotel information
            output_dir: Directory to write certificate files
            
        Returns:
            List of generated file paths (relative to output_dir)
        """
        generated_files = []
        
        for cert_type in self.CERTIFICATE_TYPES:
            result = self.generate(hotel_data, cert_type, output_dir)
            if result.get("file_path"):
                generated_files.append(result["file_path"])
        
        return generated_files

    def generate(
        self, 
        hotel_data: Dict[str, Any], 
        certificate_type: str,
        output_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Generate a certificate and optionally write to file.
        
        Args:
            hotel_data: Hotel information
            certificate_type: One of CERTIFICATE_TYPES
            output_dir: Optional output directory for files
            
        Returns:
            Dict with certificate metadata and file path if written
        """
        nombre = hotel_data.get("nombre", "Hotel")
        fecha = date.today().isoformat()
        
        if certificate_type not in self.CERTIFICATE_TYPES:
            raise ValueError(f"Invalid certificate type: {certificate_type}")
        
        template_md = self._generate_template(nombre, certificate_type, fecha)
        
        result = {
            "status": "generated",
            "certificate_type": certificate_type,
            "hotel_name": nombre,
            "issue_date": fecha,
            "template_md": template_md,
        }
        
        # Write to file if output_dir is provided
        if output_dir:
            filename = f"certificado_{certificate_type}.md"
            file_path = output_dir / filename
            file_path.write_text(template_md, encoding="utf-8")
            result["file_path"] = filename
        
        return result

    def _generate_template(self, nombre: str, cert_type: str, fecha: str) -> str:
        """Generate markdown template for certificate."""
        if cert_type == "reserva_directa":
            title = "Certificado de Reserva Directa"
            description = "Este hotel ha implementado un flujo de reserva directa optimizado."
            criteria = [
                "Botón WhatsApp visible y funcional",
                "CTA de reserva directa en homepage",
                "Tiempo de respuesta < 10 minutos",
                "Motor de reservas integrado o alternativa clara",
            ]
        else:  # web_optimizada
            title = "Certificado de Web Optimizada"
            description = "Este hotel ha optimizado su sitio web para visibilidad en IA."
            criteria = [
                "Schema.org JSON-LD implementado",
                "FAQs publicadas y accesibles",
                "Core Web Vitals en rango aceptable",
                "HTTPS activo con certificado válido",
            ]
        
        criteria_list = "\n".join([f"- [x] {c}" for c in criteria])
        
        return f"""# {title}

**Otorgado a**: {nombre}
**Fecha de emisión**: {fecha}
**Válido hasta**: 90 días desde la emisión

---

## Descripción
{description}

## Criterios Cumplidos
{criteria_list}

---

*Emitido por IA Hoteles Agent — "Primera Recomendación en Agentes IA"*

> [!NOTE]
> Este certificado se activa al cumplir los umbrales definidos en onboarding.
> Versión futura (v2.6) incluirá formato PDF con firma digital.
"""

