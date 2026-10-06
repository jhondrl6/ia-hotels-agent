"""Tests for whatsapp_button asset generation.

Validates that whatsapp_button:
- Is in the catalog as IMPLEMENTED
- Has promised_by WITHOUT "always" (FASE-5: bug sistemico corregido)
- Generates HTML even without WhatsApp data (fallback)
- Is in fast_assets and standard_assets lists
"""

import pytest
from modules.asset_generation.asset_catalog import ASSET_CATALOG, AssetStatus
from modules.asset_generation.conditional_generator import ConditionalGenerator


class TestWhatsAppButtonCatalog:
    """Test whatsapp_button catalog entry."""

    def test_whatsapp_button_exists_in_catalog(self):
        """whatsapp_button must exist in the catalog."""
        assert "whatsapp_button" in ASSET_CATALOG

    def test_whatsapp_button_is_implemented(self):
        """whatsapp_button must be IMPLEMENTED."""
        entry = ASSET_CATALOG["whatsapp_button"]
        assert entry.status == AssetStatus.IMPLEMENTED

    def test_whatsapp_button_no_always_in_promised_by(self):
        """whatsapp_button promised_by must NOT include 'always' (FASE-5 fix)."""
        entry = ASSET_CATALOG["whatsapp_button"]
        assert "always" not in entry.promised_by

    def test_whatsapp_button_has_real_pain_ids(self):
        """whatsapp_button promised_by must have real pain IDs."""
        entry = ASSET_CATALOG["whatsapp_button"]
        assert len(entry.promised_by) > 0
        # Real pain IDs, not "always"
        valid_ids = {"no_whatsapp_visible", "whatsapp_conflict"}
        assert any(pid in valid_ids for pid in entry.promised_by)

    def test_whatsapp_button_not_blocking(self):
        """whatsapp_button must not block on failure (has fallback)."""
        entry = ASSET_CATALOG["whatsapp_button"]
        assert entry.block_on_failure is False

    def test_whatsapp_button_has_fallback(self):
        """whatsapp_button must have a fallback action."""
        entry = ASSET_CATALOG["whatsapp_button"]
        assert entry.fallback is not None
        assert "generate_basic_whatsapp" in entry.fallback


class TestWhatsAppButtonGeneration:
    """Test whatsapp_button generation."""

    def test_whatsapp_in_fast_assets(self):
        """whatsapp_button must be in _fast_assets for LOW data quality."""
        gen = ConditionalGenerator()
        assert "whatsapp_button" in gen._fast_assets

    def test_whatsapp_in_standard_assets(self):
        """whatsapp_button must be in _standard_assets for MED data quality."""
        gen = ConditionalGenerator()
        assert "whatsapp_button" in gen._standard_assets

    def test_whatsapp_generates_with_data(self, tmp_path):
        """Test generation with WhatsApp phone data.

        FASE-C (AC6): el fixture llevaba un numero sintetico ENMASCARADO
        ("+573****4567"). Con el guard de forma ese valor se rechaza, y con
        razon: los asteriscos son digitos perdidos. Antes el generador los
        borraba en silencio y emitia `wa.me/5734567` — siete digitos fabricados
        por recorte, que es el defecto que AC6 nombra "sin completar partes".
        El fixture pasa a ser sintetico pero de forma valida; la asercion de
        exito no cambió. La clave es `whatsapp_number`, el nombre del campo
        validado del ValidationSummary (AC6: el boton lee ese campo).
        """
        from modules.data_validation import DataPoint, DataSource
        from datetime import datetime

        gen = ConditionalGenerator(output_dir=str(tmp_path))
        dp = DataPoint("whatsapp_number")
        dp.add_source(DataSource("test", "+57 310 401 9049", datetime.now().isoformat()))
        validated_data = {"whatsapp_number": dp}

        result = gen.generate(
            asset_type="whatsapp_button",
            validated_data=validated_data,
            hotel_name="Test Hotel",
            hotel_id="test_hotel",
        )
        assert result["success"] is True
        assert result["status"] in ("success", "warning")

    def test_whatsapp_sin_numero_utilizable_bloquea_sin_producir_href(self, tmp_path):
        """FASE-C (AC3/AC6): sin numero utilizable NO se produce el boton.

        RE-ANCLADO, no afeitado. Este test afirmaba antes que whatsapp_button se
        generaba incluso sin datos (NEVER_BLOCK → exito con warning). Esa es la
        ruta que producía `https://wa.me/` vacio. NEVER_BLOCK sigue vigente para
        los demas assets y para la confianza baja (el preflight sigue
        advirtiendo, no bloqueando: `block_on_failure=False` intacto); lo que
        cambia es que un boton con destino inhabilitado queda en ERROR BLOQUEANTE
        por mandato expreso de AC3. La expectativa se invierte porque el plan la
        define al reves, y el destino se reporta (no basta la ausencia de archivo).
        """
        gen = ConditionalGenerator(output_dir=str(tmp_path))
        result = gen.generate(
            asset_type="whatsapp_button",
            validated_data={},
            hotel_name="Test Hotel",
            hotel_id="test_hotel",
        )
        assert result["success"] is False
        assert result["status"] == "blocked"
        assert result["can_use"] is False
        assert result["reason_code"] == "whatsapp_number_no_utilizable"
        assert result["rejection"]["causa"] == "SIN_CAMPO_VALIDADO"
        assert "file_path" not in result

    def test_whatsapp_in_generation_strategies(self):
        """whatsapp_button must be in GENERATION_STRATEGIES."""
        gen = ConditionalGenerator()
        assert "whatsapp_button" in gen.GENERATION_STRATEGIES
