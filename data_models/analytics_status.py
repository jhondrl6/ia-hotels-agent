"""
Analytics Status — estado de disponibilidad de fuentes de datos.

Permite al V4DiagnosticGenerator informar al template POR QUE no hay
datos de analytics, en vez de silenciarlo con ceros o guiones.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class AnalyticsStatus:
    """
    Estado de disponibilidad de cada fuente de datos analytics al
    momento de generar el diagnostico.

    Se construye ANTES de las llamadas API, intentando inicializar
    cada cliente para detectar problemas de configuracion
    (credenciales faltantes, librerias no instaladas, etc.).
    """
    # GA4
    ga4_available: bool = False
    ga4_error: Optional[str] = None
    ga4_status_text: Optional[str] = None

    # Profound
    profound_available: bool = False
    profound_error: Optional[str] = None
    profound_status_text: Optional[str] = None

    # Semrush
    semrush_available: bool = False
    semrush_error: Optional[str] = None
    semrush_status_text: Optional[str] = None

    # GSC (FASE-D)
    gsc_available: bool = False
    gsc_error: Optional[str] = None
    gsc_status_text: Optional[str] = None

    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)

    # ---- Public helpers ----

    def is_complete(self) -> bool:
        """True cuando TODAS las fuentes estan configuradas."""
        return (self.ga4_available and self.profound_available
                and self.semrush_available and self.gsc_available)

    def is_any_missing(self) -> bool:
        """True si ALGUNA fuente no esta disponible."""
        return (not self.ga4_available or not self.profound_available
                or not self.semrush_available or not self.gsc_available)

    def missing_credentials(self) -> list:
        """Lista de variables de entorno/config faltantes."""
        missing: list = []
        if self.ga4_error and ("credentials" in self.ga4_error.lower()
                                or "property" in self.ga4_error.lower()):
            missing.append("GA4_PROPERTY_ID / GA4_CREDENTIALS_PATH")
        if self.profound_error and ("api_key" in self.profound_error.lower()
                                     or "configure" in self.profound_error.lower()):
            missing.append("PROFOUND_API_KEY")
        if self.semrush_error and ("api_key" in self.semrush_error.lower()
                                    or "configure" in self.semrush_error.lower()):
            missing.append("SEMRUSH_API_KEY")
        if self.gsc_error and ("site_url" in self.gsc_error.lower()
                               or "credentials" in self.gsc_error.lower()):
            missing.append("GSC_SITE_URL")
        return missing

    def summary_for_template(self) -> str:
        """
        Texto legible para inyectar en el template.
        """
        parts: list = []

        # GA4
        if self.ga4_available:
            parts.append("GA4: ✅ Conectado")
        elif self.ga4_status_text:
            parts.append(f"GA4: {self.ga4_status_text}")
        else:
            parts.append("GA4: No configurado")

        # Profound
        if self.profound_available:
            parts.append("Profound AI Visibility: ✅ Conectado")
        elif self.profound_status_text:
            parts.append(f"Profound AI Visibility: {self.profound_status_text}")
        else:
            parts.append("Profound AI Visibility: No disponible en esta version")

        # Semrush
        if self.semrush_available:
            parts.append("Semrush SEO: ✅ Conectado")
        elif self.semrush_status_text:
            parts.append(f"Semrush SEO: {self.semrush_status_text}")
        else:
            parts.append("Semrush SEO: No disponible en esta version")

        # GSC
        if self.gsc_available:
            parts.append("GSC: ✅ Conectado — datos de busqueda organica incluidos")
        elif self.gsc_status_text:
            parts.append(f"GSC: {self.gsc_status_text}")
        else:
            parts.append("GSC: No configurado (agregue GSC_SITE_URL)")

        return " | ".join(parts)

    # Per-source status fragments for granular template use
    def ga4_status_for_template(self) -> str:
        if self.ga4_available:
            return "✅ Conectado — datos de GA4 incluidos"
        if self.ga4_status_text:
            return self.ga4_status_text
        return "⚠️ No configurado (ver GA4_PROPERTY_ID)"

    def profound_status_for_template(self) -> str:
        if self.profound_available:
            return "✅ Conectado"
        if self.profound_status_text:
            return self.profound_status_text
        return "⚠️ No disponible en esta version (API pendiente)"

    def semrush_status_for_template(self) -> str:
        if self.semrush_available:
            return "✅ Conectado"
        if self.semrush_status_text:
            return self.semrush_status_text
        return "⚠️ No disponible en esta version (API pendiente)"

    def gsc_status_for_template(self) -> str:
        """GSC status fragment for template use."""
        if self.gsc_available:
            return "✅ Conectado — datos de busqueda organica incluidos"
        if self.gsc_status_text:
            return self.gsc_status_text
        return "⚠️ No configurado (agregue GSC_SITE_URL en el config)"
