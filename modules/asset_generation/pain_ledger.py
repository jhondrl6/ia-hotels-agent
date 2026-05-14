"""
PainLedger - FASE-0B: Fuente de Verdad de Brechas.

Facade que normaliza y serializa detecciones de Pain desde PainSolutionMapper,
conservando backward compatibility con pain_ids_resolved.
"""

import json
import logging
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Dict, Any

from ..commercial_documents.pain_solution_mapper import Pain

logger = logging.getLogger(__name__)


@dataclass
class PainLedgerEntry:
    """Entrada individual en el PainLedger."""
    pain_id: str
    source_module: str
    source_file: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    confidence: float
    status: str  # DETECTED | DIAGNOSED | MAPPED_TO_SERVICE | ASSET_GENERATED | JUSTIFIED_SKIP | BLOCKED
    human_label: str
    evidence_refs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for JSON export."""
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PainLedgerEntry':
        """Deserialize from dict."""
        return PainLedgerEntry(**data)


class PainLedger:
    """
    Facade para gestionar detecciones de Pain.

    Normaliza pain_ids a lowercase_underscore para consistencia.
    Conserva backward compatibility con pain_ids_resolved.
    """

    # Mapping de normalización: title case / caps → normalized
    NORMALIZATION_RULES = {
        "No WhatsApp Visible": "no_whatsapp_visible",
        "Conflicto de WhatsApp": "whatsapp_conflict",
        "Sin Schema FAQ": "no_faq_schema",
        "Bajo Score GBP": "low_gbp_score",
        "Sin Motor de Reservas": "no_motor_reservas",
        "Sin Schema Hotel": "no_hotel_schema",
        "Performance Deficiente": "poor_performance",
        "Sin Schema Organization": "no_org_schema",
        "Falta de Reviews": "missing_reviews",
        "Alta Dependencia OTAs": "low_ota_divergence",
        "Metadatos por Defecto": "metadata_defaults",
        "Sin llms.txt": "missing_llmstxt",
        "Sin Analytics Configurado": "no_analytics_configured",
        "Baja Visibilidad Organica": "low_organic_visibility",
        "GA4 sin Configuracion Avanzada": "no_ga4_enhanced",
        "Crawlers IA Bloqueados": "ai_crawler_blocked",
        "Contenido Poco Citable": "low_citability",
        "Baja Preparación IA": "low_ia_readiness",
        "Sin Schema de Reviews": "no_schema_reviews",
        "Sin SSL/HTTPS": "no_ssl",
        "Sin Open Graph Tags": "no_og_tags",
        "Imágenes sin Texto Alternativo": "missing_alt_text",
        "Sin Informe Mensual": "no_monthly_report",
        "Blog Inactivo": "no_blog_content",
        "Sin Presencia en Redes Sociales": "no_social_links",
        "Contenido Muy Corto": "low_content_length",
    }

    # Fallback: normalización automática con lower().replace(' ', '_')
    def _normalize_pain_id(self, raw_id: str) -> str:
        """Normalize pain_id to lowercase_underscore."""
        if raw_id in self.NORMALIZATION_RULES:
            return self.NORMALIZATION_RULES[raw_id]
        # Auto-normalize: Title Case → lowercase_underscore
        normalized = raw_id.lower().replace(' ', '_').replace('-', '_')
        return normalized

    def from_pains(self, pains: List[Pain], source_module: str) -> List[PainLedgerEntry]:
        """
        Convert list of Pain objects to PainLedgerEntry list.

        Args:
            pains: List of Pain objects from PainSolutionMapper.detect_pains()
            source_module: Module that detected the pains (e.g., 'pain_solution_mapper')

        Returns:
            List of PainLedgerEntry with normalized pain_ids
        """
        entries = []
        for pain in pains:
            normalized_id = self._normalize_pain_id(pain.id)
            entry = PainLedgerEntry(
                pain_id=normalized_id,
                source_module=source_module,
                source_file=pain.detected_by,  # detected_by maps to source file concept
                severity=pain.severity.upper() if pain.severity else "MEDIUM",
                confidence=pain.confidence,
                status="DETECTED",
                human_label=pain.name,
                evidence_refs=[]  # evidence_refs populated by caller
            )
            entries.append(entry)
        return entries

    def to_dict(self, entries: List[PainLedgerEntry]) -> Dict[str, Any]:
        """
        Serialize entries to a reproducible dict for JSON export.

        Args:
            entries: List of PainLedgerEntry

        Returns:
            Dict with entries serialized
        """
        return {
            "pain_ledger_version": "1.0",
            "entries": [entry.to_dict() for entry in entries]
        }

    def save(self, entries: List[PainLedgerEntry], path: Path) -> None:
        """
        Save entries to JSON file.

        Args:
            entries: List of PainLedgerEntry
            path: Path to save JSON file
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        data = self.to_dict(entries)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)

    def load(self, path: Path) -> List[PainLedgerEntry]:
        """
        Load entries from JSON file.

        Args:
            path: Path to JSON file

        Returns:
            List of PainLedgerEntry
        """
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return [PainLedgerEntry.from_dict(e) for e in data.get("entries", [])]