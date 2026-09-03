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

from ..commercial_documents.pain_solution_mapper import Pain, PainSolutionMapper

logger = logging.getLogger(__name__)


@dataclass
class PainLedgerEntry:
    """Entrada individual en el PainLedger."""
    pain_id: str
    source_module: str
    source_file: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    confidence: float
    # DETECTED | DIAGNOSED | MAPPED_TO_SERVICE | ASSET_GENERATED | JUSTIFIED_SKIP
    # | BLOCKED | VERIFIED_IN_SITE (FASE-P1-D F13: asset verificado en el sitio vivo)
    status: str
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

    # Normalización: nombre humano → pain_id canónico.
    # FASE-A (N-A2): derivado de Capa 1 en vez de mantenido a mano. La copia anterior
    # tenía una clave obsoleta ("No WhatsApp Visible", renombrado a "Sin WhatsApp
    # Visible") y le faltaban entradas: declaraba menos reglas que pains existen.
    # Derivar es conservativo porque `_normalize_pain_id` ya tiene fallback
    # lower()/replace() y en la ruta viva `pain.id` llega canonicalizado.
    NORMALIZATION_RULES = {
        solucion["name"]: pain_id
        for pain_id, solucion in PainSolutionMapper.PAIN_SOLUTION_MAP.items()
    }

    # FASE-P1-D (F13): status de primera clase para "verificado en producción".
    # Lo consumirá FASE-P2-A/F14 (promised_assets_exist).
    STATUS_VERIFIED_IN_SITE = "VERIFIED_IN_SITE"

    # Mapping pain_id → asset_type cuya presencia en el sitio vivo resuelve el pain.
    # Base para propagar site_verification al ledger (FASE-P1-D F13).
    PAIN_TO_PRESENCE_ASSET = {
        "no_whatsapp_visible": "whatsapp_button",
        "whatsapp_conflict": "whatsapp_button",
        "no_hotel_schema": "hotel_schema",
        "no_org_schema": "org_schema",
        "no_faq_schema": "faq_page",
        "missing_llmstxt": "llms_txt",
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

    def apply_site_verification(
        self,
        entries: List[PainLedgerEntry],
        site_presence_report: Dict[str, Any]
    ) -> List[PainLedgerEntry]:
        """
        FASE-P1-D (F13): propagar la verdad del sitio vivo al PainLedger.

        Si el site_presence_report (dict canónico de normalize_site_presence)
        confirma que el asset que resuelve un pain YA EXISTE en producción
        (status "exists" o "redundant"), la entrada pasa de DETECTED a
        VERIFIED_IN_SITE y su severidad deja de ser alta: el sitio vivo es la
        fuente única de verdad y ya confirma la presencia del asset.

        Args:
            entries: Entradas del ledger (mutadas in-place y retornadas)
            site_presence_report: Dict canónico {asset: {status, site_verified}}

        Returns:
            Las mismas entradas con estado actualizado donde aplique.
        """
        if not site_presence_report:
            return entries

        results = site_presence_report.get("results", {}) or {}

        for entry in entries:
            if entry.status != "DETECTED":
                continue
            asset_type = self.PAIN_TO_PRESENCE_ASSET.get(entry.pain_id)
            if not asset_type:
                continue
            presence = results.get(asset_type) or site_presence_report.get(asset_type)
            if not isinstance(presence, dict):
                continue
            status = str(presence.get("status", "")).lower()
            # FASE-SR-E (H7, L-SR3): criterio canónico — exists_with_issues
            # también verifica presencia (el asset existe; sus campos faltantes
            # son mejora sugerida, no brecha activa).
            from modules.asset_generation.site_presence_checker import (
                is_present_in_production,
            )
            if (
                status in ("redundant",) or is_present_in_production(status)
            ) and presence.get("site_verified"):
                entry.status = self.STATUS_VERIFIED_IN_SITE
                # La brecha ya no es una fuga activa: severidad baja, evidencia
                # apunta a la verificación del sitio vivo.
                entry.severity = "LOW"
                entry.evidence_refs.append(
                    f"site_verification:{asset_type}:{status}"
                )
                logger.info(
                    "[PainLedger] %s → VERIFIED_IN_SITE (asset %s confirmado "
                    "en sitio vivo)", entry.pain_id, asset_type
                )

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