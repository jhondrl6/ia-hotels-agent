"""Tests AC-G1: Instrucciones desde la entrega real.

Verifica que:
- El IMPLEMENTATION_ORDER muestra rutas reales del ZIP (con ASSETS/ prefix)
- Preserva prefijos ESTIMATED_
- Assets fuera del catálogo de 6 nombres tienen disposición explícita
"""
import tempfile
from pathlib import Path
import pytest


def test_generate_delivery_template_shows_zip_paths():
    """AC-G1: IMPLEMENTATION_ORDER debe mostrar rutas reales del ZIP."""
    from modules.geo_enrichment.asset_responsibility_contract import AssetResponsibilityContract

    contract = AssetResponsibilityContract()

    core_assets = ["hotel_schema.json", "faq_schema.json"]
    geo_assets = ["hotel_schema_rich.json"]
    asset_zip_paths = {
        "hotel_schema.json": "ASSETS/hotel_schema.json",
        "faq_schema.json": "ASSETS/faq_schema.json",
        "hotel_schema_rich.json": "ASSETS/hotel_schema_rich.json",
    }

    template = contract.generate_delivery_template(
        hotel_name="Hotel Test",
        core_assets=core_assets,
        geo_assets=geo_assets,
        geo_score=50,
        asset_zip_paths=asset_zip_paths,
    )

    # Verificar que muestra las rutas del ZIP, no solo los filenames
    assert "ASSETS/hotel_schema.json" in template
    assert "ASSETS/faq_schema.json" in template
    assert "ASSETS/hotel_schema_rich.json" in template


def test_generate_delivery_template_preserves_estimated_prefix():
    """AC-G1: Debe preservar prefijo ESTIMATED_ en las rutas."""
    from modules.geo_enrichment.asset_responsibility_contract import AssetResponsibilityContract

    contract = AssetResponsibilityContract()

    core_assets = ["ESTIMATED_boton_whatsapp.html"]
    geo_assets = []
    asset_zip_paths = {
        "ESTIMATED_boton_whatsapp.html": "ASSETS/ESTIMATED_boton_whatsapp.html",
    }

    template = contract.generate_delivery_template(
        hotel_name="Hotel Test",
        core_assets=core_assets,
        geo_assets=geo_assets,
        asset_zip_paths=asset_zip_paths,
    )

    # Verificar que preserva el prefijo ESTIMATED_
    assert "ESTIMATED_boton_whatsapp.html" in template
    assert "ASSETS/ESTIMATED_boton_whatsapp.html" in template


def test_generate_delivery_template_unknown_assets_explicit_disposition():
    """AC-G1: Assets fuera del catálogo deben tener disposición explícita."""
    from modules.geo_enrichment.asset_responsibility_contract import AssetResponsibilityContract

    contract = AssetResponsibilityContract()

    # Assets conocidos + assets desconocidos
    core_assets = ["hotel_schema.json"]
    geo_assets = []
    unknown_assets = ["custom_report.html", "analytics_setup.md"]
    all_assets = core_assets + unknown_assets

    asset_zip_paths = {
        "hotel_schema.json": "ASSETS/hotel_schema.json",
        "custom_report.html": "ASSETS/custom_report.html",
        "analytics_setup.md": "ASSETS/analytics_setup.md",
    }

    template = contract.generate_delivery_template(
        hotel_name="Hotel Test",
        core_assets=all_assets,  # Pasamos todos como core_assets
        geo_assets=geo_assets,
        asset_zip_paths=asset_zip_paths,
    )

    # Verificar que hay sección de assets adicionales
    assert "ASSETS ADICIONALES" in template
    assert "fuera del catálogo CORE/GEO" in template

    # Verificar que los assets desconocidos están listados
    assert "custom_report.html" in template
    assert "analytics_setup.md" in template


def test_generate_delivery_template_without_zip_paths():
    """AC-G1: Sin asset_zip_paths, debe funcionar con filenames (backward compat)."""
    from modules.geo_enrichment.asset_responsibility_contract import AssetResponsibilityContract

    contract = AssetResponsibilityContract()

    core_assets = ["hotel_schema.json"]
    geo_assets = ["hotel_schema_rich.json"]

    # Sin asset_zip_paths
    template = contract.generate_delivery_template(
        hotel_name="Hotel Test",
        core_assets=core_assets,
        geo_assets=geo_assets,
    )

    # Debe funcionar con los filenames
    assert "hotel_schema.json" in template
    assert "hotel_schema_rich.json" in template


def test_generate_delivery_template_no_unknown_assets_section():
    """AC-G1: Sin assets desconocidos, NO debe aparecer la sección adicional."""
    from modules.geo_enrichment.asset_responsibility_contract import AssetResponsibilityContract

    contract = AssetResponsibilityContract()

    # Solo assets conocidos
    core_assets = ["hotel_schema.json", "faq_schema.json", "boton_whatsapp.html"]
    geo_assets = ["hotel_schema_rich.json", "faq_schema_rich.json", "boton_whatsapp_rich.html"]

    template = contract.generate_delivery_template(
        hotel_name="Hotel Test",
        core_assets=core_assets,
        geo_assets=geo_assets,
    )

    # NO debe aparecer la sección de assets adicionales
    assert "ASSETS ADICIONALES" not in template
    assert "fuera del catálogo" not in template
