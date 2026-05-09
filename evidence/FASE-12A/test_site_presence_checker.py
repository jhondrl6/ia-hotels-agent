"""Tests for SitePresenceChecker._check_schema_exists — FASE-12A.

Fix: Eliminar expansion Hotel->[LocalBusiness, Organization] en site_presence_checker.py L365.
Hotel solo acepta [Hotel, LodgingBusiness] — NO LocalBusiness ni Organization.

Causa rafz: rich_results_client.py:537 solo procesa Hotel y LodgingBusiness.
Sites con solo Organization reportaban hotel_schema=EXISTS -> asset SKIPPED -> falso positivo.
"""

import pytest

from modules.asset_generation.site_presence_checker import (
    SitePresenceChecker,
    PresenceStatus,
)


class TestCheckSchemaExists:
    """Test suite for _check_schema_exists fix (FASE-12A)."""

    def _make_checker(self):
        """Create a SitePresenceChecker instance for testing."""
        return SitePresenceChecker()

    def _schema_report(self, *types):
        """Build a schema_report with the given schema types."""
        return {
            "schemas_encontrados": [{"type": t, "data": {}} for t in types],
            "campos_faltantes": [],
        }

    def test_hotel_present_found(self):
        """Hotel schema presente -> found=True."""
        checker = self._make_checker()
        result = checker._check_schema_exists("Hotel", self._schema_report("Hotel"))
        assert result["found"] is True

    def test_organization_only_not_found(self):
        """Solo Organization (sin Hotel/LodgingBusiness) -> found=False.

        Este es el caso que causaba el falso positivo antes del fix.
        El audit path (rich_results_client:537) no procesa Organization para hotel_schema.
        """
        checker = self._make_checker()
        result = checker._check_schema_exists("Hotel", self._schema_report("Organization"))
        assert result["found"] is False

    def test_localbusiness_only_not_found(self):
        """Solo LocalBusiness (sin Hotel/LodgingBusiness) -> found=False.

        LocalBusiness ya no se incluye en la expansion de Hotel.
        """
        checker = self._make_checker()
        result = checker._check_schema_exists("Hotel", self._schema_report("LocalBusiness"))
        assert result["found"] is False

    def test_lodgingbusiness_present_found(self):
        """LodgingBusiness presente -> found=True (expansion legitima de Hotel)."""
        checker = self._make_checker()
        result = checker._check_schema_exists("Hotel", self._schema_report("LodgingBusiness"))
        assert result["found"] is True

    def test_empty_schema_not_found(self):
        """Schema vacio (sin tipos) -> found=False."""
        checker = self._make_checker()
        result = checker._check_schema_exists("Hotel", self._schema_report())
        assert result["found"] is False
