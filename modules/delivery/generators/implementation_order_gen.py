"""Implementation Order Generator - FASE-5 Asset Responsibility Contract.

Genera el archivo IMPLEMENTATION_ORDER.md que guía al webmaster sobre qué archivos
implementar y en qué orden, según el AssetResponsibilityContract.

Este generador se invoca desde el delivery packager para incluir la guía de
implementación en el delivery package.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# Importar el contract desde geo_enrichment
from modules.geo_enrichment import (
    AssetResponsibilityContract,
    AssetType,
    get_implementation_order,
    get_replacement_rule,
    generate_delivery_template as generate_template,
)


class ImplementationOrderGenerator:
    """Genera la guía de orden de implementación basada en el AssetResponsibilityContract."""

    def __init__(self):
        """Inicializa el generador."""
        self.contract = AssetResponsibilityContract()

    def generate(
        self,
        hotel_name: str,
        output_dir: Path,
        core_assets: Optional[List[str]] = None,
        geo_assets: Optional[List[str]] = None,
        geo_score: Optional[int] = None,
        include_json: bool = True
    ) -> Dict[str, str]:
        """Genera los archivos de orden de implementación.

        Args:
            hotel_name: Nombre del hotel.
            output_dir: Directorio donde guardar los archivos generados.
            core_assets: Lista de filenames CORE generados.
            geo_assets: Lista de filenames GEO generados.
            geo_score: Score GEO para determinar obligatoriedad de assets GEO.
            include_json: Si True, también genera el JSON del contract.

        Returns:
            Dict con rutas de archivos generados.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        generated = {}

        # Generar IMPLEMENTATION_ORDER.md
        md_content = self.contract.generate_delivery_template(
            hotel_name=hotel_name,
            core_assets=core_assets,
            geo_assets=geo_assets,
            geo_score=geo_score
        )

        md_path = output_dir / "IMPLEMENTATION_ORDER.md"
        md_path.write_text(md_content, encoding='utf-8')
        generated['implementation_order_md'] = str(md_path)

        # Generar ASSET_RESPONSIBILITY.json si se solicita
        if include_json:
            json_content = self.contract.export_contract_json(
                core_assets=core_assets,
                geo_assets=geo_assets
            )

            json_path = output_dir / "ASSET_RESPONSIBILITY.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_content, f, indent=2, ensure_ascii=False)
            generated['asset_responsibility_json'] = str(json_path)

        return generated

    def get_order_summary(
        self,
        core_assets: Optional[List[str]] = None,
        geo_assets: Optional[List[str]] = None
    ) -> str:
        """Genera un resumen corto del orden de implementación.

        Args:
            core_assets: Lista de filenames CORE.
            geo_assets: Lista de filenames GEO.

        Returns:
            String con resumen legible.
        """
        order = get_implementation_order(core_assets, geo_assets)

        lines = ["📋 ORDEN DE IMPLEMENTACIÓN:", ""]
        for i, resp in enumerate(order, 1):
            mandatory = "✅" if resp.mandatory else "⬜"
            type_mark = "[CORE]" if resp.type == AssetType.CORE else "[GEO]"
            lines.append(f"  {i}. {resp.filename} {mandatory} {type_mark}")

        return "\n".join(lines)


def generate_implementation_order(
    hotel_name: str,
    output_dir: str,
    core_assets: Optional[List[str]] = None,
    geo_assets: Optional[List[str]] = None,
    geo_score: Optional[int] = None
) -> Dict[str, str]:
    """Función convenience para generar orden de implementación.

    Args:
        hotel_name: Nombre del hotel.
        output_dir: Directorio donde guardar archivos.
        core_assets: Lista de filenames CORE.
        geo_assets: Lista de filenames GEO.
        geo_score: Score GEO.

    Returns:
        Dict con rutas de archivos generados.
    """
    generator = ImplementationOrderGenerator()
    return generator.generate(
        hotel_name=hotel_name,
        output_dir=Path(output_dir),
        core_assets=core_assets,
        geo_assets=geo_assets,
        geo_score=geo_score
    )
