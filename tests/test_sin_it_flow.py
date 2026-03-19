"""Tests para el flujo de hoteles sin capacidad IT.

Valida:
1. Generación de botón WhatsApp para paquetes Plus/Elite
2. Estructura de assets generados
"""
import pytest
from pathlib import Path


class TestWhatsAppButtonGeneration:
    """Tests para wa_button_gen.py y su integración en manager.py."""

    def test_wa_button_generator_returns_dict(self):
        """El generador debe retornar un dict con las claves esperadas."""
        from modules.delivery.generators.wa_button_gen import WhatsAppButtonGenerator
        
        gen = WhatsAppButtonGenerator()
        hotel_data = {"nombre": "Hotel Test", "whatsapp": "3001234567"}
        result = gen.generate(hotel_data)
        
        assert isinstance(result, dict)
        assert "html_code" in result
        assert "implementation_guide" in result
        # Nota: gtm_snippet ya no se genera, el tracking esta embebido en html_code

    def test_wa_button_html_contains_wa_link(self):
        """El HTML generado debe contener un link wa.me válido."""
        from modules.delivery.generators.wa_button_gen import WhatsAppButtonGenerator
        
        gen = WhatsAppButtonGenerator()
        hotel_data = {"nombre": "Hotel Boutique", "whatsapp": "573001234567"}
        result = gen.generate(hotel_data)
        
        assert "https://wa.me/573001234567" in result["html_code"]
        assert "iah-whatsapp-cta" in result["html_code"]  # ID para tracking

    def test_wa_button_handles_missing_phone(self):
        """Debe usar fallback si no hay teléfono."""
        from modules.delivery.generators.wa_button_gen import WhatsAppButtonGenerator
        
        gen = WhatsAppButtonGenerator()
        hotel_data = {"nombre": "Hotel Sin Telefono"}
        result = gen.generate(hotel_data)
        
        # Debe generar algo, aunque use placeholder
        assert "wa.me" in result["html_code"]
        assert len(result["html_code"]) > 100

    def test_wa_button_normalizes_colombian_number(self):
        """Números de 10 dígitos colombianos deben prefijarse con 57."""
        from modules.delivery.generators.wa_button_gen import WhatsAppButtonGenerator
        
        gen = WhatsAppButtonGenerator()
        hotel_data = {"nombre": "Hotel Colombia", "whatsapp": "3001234567"}
        result = gen.generate(hotel_data)
        
        # Debe agregar 57 al inicio
        assert "573001234567" in result["html_code"]


class TestDeliveryManagerWAIntegration:
    """Tests de integración del botón WhatsApp en DeliveryManager."""

    def test_delivery_manager_imports_wa_generator(self):
        """DeliveryManager debe importar WhatsAppButtonGenerator."""
        from modules.delivery.manager import DeliveryManager
        
        manager = DeliveryManager(Path("."))
        assert hasattr(manager, 'wa_button_gen')

    def test_execute_generates_wa_assets_for_plus_package(self, tmp_path):
        """Paquete Plus debe generar assets de WhatsApp."""
        from modules.delivery.manager import DeliveryManager
        
        manager = DeliveryManager(tmp_path)
        hotel_data = {
            "nombre": "Hotel Test Plus",
            "whatsapp": "573001234567",
            "ubicacion": "Eje Cafetero"
        }
        
        manager.execute("pro_aeo_plus", hotel_data)
        
        delivery_dir = tmp_path / "delivery_assets"
        assert any(p.name == "boton_whatsapp_codigo.html" for p in delivery_dir.rglob("*") if p.is_file())

    def test_execute_generates_wa_assets_for_elite_package(self, tmp_path):
        """Paquete Elite debe generar assets de WhatsApp."""
        from modules.delivery.manager import DeliveryManager
        
        manager = DeliveryManager(tmp_path)
        hotel_data = {
            "nombre": "Hotel Test Elite",
            "whatsapp": "573009876543",
            "ubicacion": "Caribe"
        }
        
        manager.execute("elite", hotel_data)
        
        delivery_dir = tmp_path / "delivery_assets"
        assert any(p.name == "boton_whatsapp_codigo.html" for p in delivery_dir.rglob("*") if p.is_file())

    def test_execute_skips_wa_for_starter_package(self, tmp_path):
        """Paquete Starter GEO NO debe generar botón WhatsApp."""
        from modules.delivery.manager import DeliveryManager
        
        manager = DeliveryManager(tmp_path)
        hotel_data = {
            "nombre": "Hotel Starter",
            "whatsapp": "573001234567",
            "ubicacion": "Antioquia"
        }
        
        manager.execute("starter_geo", hotel_data)
        
        delivery_dir = tmp_path / "delivery_assets"
        # Starter no incluye Pro assets
        assert not any(p.name == "boton_whatsapp_codigo.html" for p in delivery_dir.rglob("*") if p.is_file())
