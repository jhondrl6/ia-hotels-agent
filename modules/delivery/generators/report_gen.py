"""Reporte mínimo de KPIs IA para seguimiento del paquete Pro AEO."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict


class IAReportGenerator:
    """Construye un dashboard textual con las métricas clave del Plan Maestro."""

    def generate(self, hotel_data: Dict[str, Any]) -> str:
        nombre = hotel_data.get("nombre") or hotel_data.get("name", "Hotel")
        ubicacion = hotel_data.get("ubicacion") or hotel_data.get("city", "Colombia")
        perdida = hotel_data.get("perdida_mensual_total") or 6_900_000
        seo_loss = hotel_data.get("seo_loss") or 3_850_000
        fecha = date.today().isoformat()

        report_lines = [
            f"# IA Visibility Report · {nombre}",
            f"Fecha: {fecha} · Ubicación: {ubicacion}",
            "\n## KPIs Clave",
            "| KPI | Línea Base | Meta 90 días | Observaciones |",
            "|-----|-----------|--------------|---------------|",
            "| ACS (Agent Citation Share) | 12% estimado | 40% | Priorizar FAQs y citas verificadas |",
            "| AOIR (AI Overview Inclusion Rate) | 1 de 8 prompts | 4 de 8 | Publicar schema completo y guías citables |",
            "| DVL (Direct Visibility Lift) | +0% actual | +35% | Medir clics GBP + sesiones orgánico |",
            "| OTA Independence Index | 78% dependencia | 65% | Vincular CTA directo en todos los canales |",
            "| Score Credibilidad Web | 71/100 | 82/100 | Aplicar kit SEO Accelerator |",
            "\n## Impacto Financiero",
            f"- Pérdida mensual total estimada: ${perdida:,.0f} COP",
            f"- Impacto atribuible al Acelerador SEO: ${seo_loss:,.0f} COP",
            "- Meta Pro AEO: recuperar 2X la inversión en 6 meses.",
            "\n## Próximos pasos sugeridos",
            "1. Publicar assets GEO y FAQs (Semana 1).",
            "2. Instalar schema + CTA + Lighthouse fix (Semana 1-2).",
            "3. Activar dashboard compartido (Sheet + Data Studio) para ACS/AOIR (Semana 2).",
            "4. Revisión conjunta semana 4 con métricas y evidencias.",
        ]

        return "\n".join(report_lines)
