"""
GEO Enriched Bridge - Conecta geo_enriched/ con el pipeline de delivery.

Este módulo proporciona la función de bridge que enrichment los assets
generados por el pipeline original con los datos reales de geo_enriched/.

Arquitectura:
    Pipeline original (confidence 0.5) ──► Bridge ──► geo_enriched (confidence 0.85)

Mapeo de assets:
    | Delivery Asset | geo_enriched Source | Confidence boost |
    |---------------|---------------------|-----------------|
    | hotel_schema  | hotel_schema_rich.json | 0.5 → 0.85    |
    | faq_page      | faq_schema.json        | 0.5 → 0.85    |
    | llms_txt      | llms.txt              | 0.5 → 0.85    |

Referencia: FASE-GEO-BRIDGE prompt
"""

import json
import logging
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# =============================================================================
# FILENAME CONSTANTS - Coinciden con geo_enrichment_layer.py
# =============================================================================

FILENAME_HOTEL_SCHEMA_RICH = "hotel_schema_rich.json"
FILENAME_LLMS_TXT = "llms.txt"
FILENAME_FAQ_SCHEMA = "faq_schema.json"

# Mapeo de asset_type → (geo_enriched filename, boosted confidence)
ASSET_ENRICHMENT_MAP = {
    "hotel_schema": (FILENAME_HOTEL_SCHEMA_RICH, 0.85),
    "faq_page": (FILENAME_FAQ_SCHEMA, 0.85),
    # llms.txt se genera como asset_type="llms_txt" en conditional_generator
    "llms_txt": (FILENAME_LLMS_TXT, 0.85),
}

# Threshold de confianza para intentar enrichment
CONFIDENCE_THRESHOLD = 0.7


def try_enrich_from_geo_enriched(
    asset_type: str,
    current_content: str,
    current_confidence: float,
    geo_enriched_dir: Path,
    hotel_id: str
) -> Tuple[str, float]:
    """
    Intenta enriquecer un asset desde geo_enriched/ si el confidence es bajo.

    Si geo_enriched/ tiene una versión enriquecida de este asset,
    la usa y retorna un confidence_score mejorado.

    Args:
        asset_type: Tipo de asset (e.g., 'hotel_schema', 'llms_txt', 'faq_page')
        current_content: Contenido actual del asset generado
        current_confidence: Confidence score actual del asset
        geo_enriched_dir: Path al directorio geo_enriched/
        hotel_id: Identificador único del hotel

    Returns:
        Tuple[str, float]: (content, new_confidence_score)
        - Si enrichment fue exitoso: retorna el contenido de geo_enriched y nuevo confidence
        - Si no aplica: retorna el contenido original y confidence sin cambios
    """
    # Solo enriquecer si confidence < threshold
    if current_confidence >= CONFIDENCE_THRESHOLD:
        logger.debug(
            f"[GEO-Bridge] Skipping {asset_type}: "
            f"confidence {current_confidence:.2f} >= {CONFIDENCE_THRESHOLD}"
        )
        return current_content, current_confidence

    # Buscar mapping para este asset type
    if asset_type not in ASSET_ENRICHMENT_MAP:
        logger.debug(
            f"[GEO-Bridge] No enrichment mapping for asset_type: {asset_type}"
        )
        return current_content, current_confidence

    geo_filename, boosted_confidence = ASSET_ENRICHMENT_MAP[asset_type]

    # Verificar que geo_enriched_dir existe
    if not geo_enriched_dir.exists():
        logger.debug(
            f"[GEO-Bridge] geo_enriched_dir does not exist: {geo_enriched_dir}"
        )
        return current_content, current_confidence

    # Construir path al archivo geo_enriched
    geo_file_path = geo_enriched_dir / geo_filename

    if not geo_file_path.exists():
        logger.debug(
            f"[GEO-Bridge] geo_enriched file not found: {geo_file_path}"
        )
        return current_content, current_confidence

    # Leer contenido enriquecido
    try:
        with open(geo_file_path, 'r', encoding='utf-8') as f:
            enriched_content = f.read()

        if not enriched_content or len(enriched_content.strip()) == 0:
            logger.warning(
                f"[GEO-Bridge] geo_enriched file is empty: {geo_file_path}"
            )
            return current_content, current_confidence

        # Verificar que el contenido enriquecido tiene datos reales (no placeholders)
        if _is_placeholder_content(enriched_content, asset_type):
            logger.info(
                f"[GEO-Bridge] geo_enriched file contains placeholder content "
                f"(not enriching): {geo_file_path}"
            )
            return current_content, current_confidence

        # Success: enrichment disponible
        logger.info(
            f"[GEO-Bridge] ✓ Enriching {asset_type}: "
            f"confidence {current_confidence:.2f} → {boosted_confidence:.2f} "
            f"(from {geo_filename})"
        )

        return enriched_content, boosted_confidence

    except json.JSONDecodeError as e:
        logger.warning(
            f"[GEO-Bridge] Failed to parse JSON from {geo_file_path}: {e}"
        )
        return current_content, current_confidence
    except Exception as e:
        logger.warning(
            f"[GEO-Bridge] Error reading {geo_file_path}: {e}"
        )
        return current_content, current_confidence


def _is_placeholder_content(content: str, asset_type: str) -> bool:
    """
    Verifica si el contenido es un placeholder genérico.

    Args:
        content: Contenido a verificar
        asset_type: Tipo de asset para contexto

    Returns:
        True si el contenido es un placeholder, False si tiene datos reales
    """
    content_lower = content.lower().strip()

    # Check for generic hotel name placeholders
    if '"name": "hotel"' in content_lower or '"name": "hotel "' in content_lower:
        return True

    # Check for URL placeholders
    if 'https://your-website.com' in content_lower or 'https://example.com' in content_lower:
        return True

    # Check for empty or minimal content
    if len(content.strip()) < 50:
        return True

    # For llms_txt specifically, check for "# Hotel" (placeholder title)
    if asset_type == "llms_txt":
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith('# ') and line.strip().lower() in ['# hotel', '# my hotel', '# hotel name']:
                return True

    return False


def is_geo_enriched_available(geo_enriched_dir: Path) -> bool:
    """
    Verifica si el directorio geo_enriched/ existe y contiene archivos.

    Args:
        geo_enriched_dir: Path al directorio geo_enriched/

    Returns:
        True si geo_enriched/ existe y tiene archivos, False otherwise
    """
    if not geo_enriched_dir.exists():
        return False

    # Check for any of the enrichment files
    for filename, _ in ASSET_ENRICHMENT_MAP.values():
        if (geo_enriched_dir / filename).exists():
            return True

    return False


def get_enrichment_summary(geo_enriched_dir: Path) -> dict:
    """
    Retorna un resumen de qué archivos de enrichment están disponibles.

    Args:
        geo_enriched_dir: Path al directorio geo_enriched/

    Returns:
        Dict con asset_type → disponibilidad
    """
    summary = {}

    for asset_type, (filename, _) in ASSET_ENRICHMENT_MAP.items():
        file_path = geo_enriched_dir / filename
        available = file_path.exists()

        # Additional check: if file exists, verify it's not placeholder
        is_meaningful = False
        if available:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    is_meaningful = (
                        len(content.strip()) > 50
                        and not _is_placeholder_content(content, asset_type)
                    )
            except Exception:
                pass

        summary[asset_type] = {
            "filename": filename,
            "exists": available,
            "has_real_data": is_meaningful
        }

    return summary
