"""Test F3: Fallback de región conservador para direcciones país-genérico.

Este test verifica que cuando la dirección GBP solo dice "Colombia" (común en GBP
incompletos del ICP objetivo), el ADR se resuelve como default conservador ($300K),
NO como caribe ($450K), evitando sobreestimar la fuga 2.3-3.2x en el hook de venta.

FASE-P1-B del plan CREDIBILIDAD-NUMERICA-2026-08-20.
"""
import pytest
from unittest.mock import MagicMock, patch


class TestRegionFallbackConservative:
    """Tests para el fallback de región conservador (F3)."""

    @pytest.fixture
    def auditor_with_mock_resolver(self):
        """Fixture que crea un auditor con un resolver mockeado."""
        from modules.auditors.v4_comprehensive import V4ComprehensiveAuditor

        with patch('modules.auditors.v4_comprehensive.RegionalADRResolver') as mock_resolver_class:
            mock_resolver = MagicMock()
            mock_resolver_class.return_value = mock_resolver

            # Configurar el mock para devolver diferentes ADRs según región
            def resolve_side_effect(region, rooms, user_provided_adr):
                adr_map = {
                    'eje_cafetero': 280000,
                    'caribe': 450000,
                    'antioquia': 500000,
                    'bogota': 350000,
                    'default': 300000,
                }
                result = MagicMock()
                result.adr_cop = adr_map.get(region, 300000)
                return result

            mock_resolver.resolve.side_effect = resolve_side_effect

            auditor = V4ComprehensiveAuditor()
            auditor.adr_resolver = mock_resolver
            yield auditor

    def test_colombia_resolves_to_default_not_caribe(self, auditor_with_mock_resolver):
        """F3: 'colombia' en la dirección debe resolver a default ($300K), NO a caribe ($450K)."""
        auditor = auditor_with_mock_resolver

        # Resetear cache para forzar resolución
        auditor._regional_adr_cache = None

        # Dirección país-genérico (común en GBP incompletos)
        result = auditor._resolve_regional_adr("Colombia")

        # Debe resolver a default ($300K), NO a caribe ($450K)
        assert result == 300000, f"Esperado 300000 (default), obtenido {result}"

    def test_colombia_lowercase_resolves_to_default(self, auditor_with_mock_resolver):
        """F3: 'colombia' (minúscula) también resuelve a default."""
        auditor = auditor_with_mock_resolver
        auditor._regional_adr_cache = None

        result = auditor._resolve_regional_adr("colombia")
        assert result == 300000

    def test_colombia_in_address_resolves_to_default(self, auditor_with_mock_resolver):
        """F3: Dirección que contiene 'colombia' resuelve a default."""
        auditor = auditor_with_mock_resolver
        auditor._regional_adr_cache = None

        result = auditor._resolve_regional_adr("Hotel Boutique, Colombia")
        assert result == 300000

    def test_cartagena_still_resolves_to_caribe(self, auditor_with_mock_resolver):
        """F3: Ciudades específicas aún resuelven a su región correcta."""
        auditor = auditor_with_mock_resolver
        auditor._regional_adr_cache = None

        result = auditor._resolve_regional_adr("Cartagena, Bolívar, Colombia")
        # Cartagena debe resolver a caribe ($450K), no a default
        assert result == 450000

    def test_barranquilla_resolves_to_caribe(self, auditor_with_mock_resolver):
        """F3: Barranquilla resuelve a caribe."""
        auditor = auditor_with_mock_resolver
        auditor._regional_adr_cache = None

        result = auditor._resolve_regional_adr("Barranquilla")
        assert result == 450000

    def test_pereira_resolves_to_eje_cafetero(self, auditor_with_mock_resolver):
        """F3: Pereira resuelve a eje_cafetero."""
        auditor = auditor_with_mock_resolver
        auditor._regional_adr_cache = None

        result = auditor._resolve_regional_adr("Pereira, Risaralda")
        assert result == 280000

    def test_medellin_resolves_to_antioquia(self, auditor_with_mock_resolver):
        """F3: Medellín resuelve a antioquia."""
        auditor = auditor_with_mock_resolver
        auditor._regional_adr_cache = None

        result = auditor._resolve_regional_adr("Medellín")
        assert result == 500000

    def test_bogota_resolves_to_default(self, auditor_with_mock_resolver):
        """F3: Bogotá resuelve a default (según region_map actual)."""
        auditor = auditor_with_mock_resolver
        auditor._regional_adr_cache = None

        result = auditor._resolve_regional_adr("Bogotá")
        # Bogotá está mapeada a 'default' en el region_map
        assert result == 300000

    def test_unknown_city_resolves_to_default(self, auditor_with_mock_resolver):
        """F3: Ciudad no mapeada resuelve a default."""
        auditor = auditor_with_mock_resolver
        auditor._regional_adr_cache = None

        result = auditor._resolve_regional_adr("Ciudad Desconocida")
        assert result == 300000

    def test_no_address_returns_none(self, auditor_with_mock_resolver):
        """F3: Sin dirección, retorna None."""
        auditor = auditor_with_mock_resolver
        auditor._regional_adr_cache = None

        result = auditor._resolve_regional_adr(None)
        assert result is None

    def test_empty_address_returns_none(self, auditor_with_mock_resolver):
        """F3: Dirección vacía retorna None."""
        auditor = auditor_with_mock_resolver
        auditor._regional_adr_cache = None

        result = auditor._resolve_regional_adr("")
        assert result is None

    def test_cache_is_used(self, auditor_with_mock_resolver):
        """F3: El cache se usa para evitar resoluciones redundantes."""
        auditor = auditor_with_mock_resolver

        # Establecer cache manualmente
        auditor._regional_adr_cache = 999999

        # Debe usar el cache, no resolver de nuevo
        result = auditor._resolve_regional_adr("Cartagena")
        assert result == 999999
