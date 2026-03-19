"""Tests para PageSpeedAuditorV2 - Sprint 1.

Valida cálculo de severidad y generación de claims basados en métricas de performance.
"""
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to Python path for pytest
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest

from modules.auditors.pagespeed_auditor_v2 import PageSpeedAuditorV2
from data_models.canonical_assessment import PerformanceAnalysis, PerformanceMetrics
from data_models.claim import Claim
from enums.severity import Severity


@pytest.fixture
def auditor():
    """Fixture que proporciona una instancia de PageSpeedAuditorV2."""
    return PageSpeedAuditorV2()


@pytest.fixture
def critical_pagespeed_response() -> Dict[str, Any]:
    """Fixture con respuesta de PageSpeed API con métricas CRÍTICAS.
    
    Simula el caso Hotel Vísperas: Performance 51, LCP 21.2s
    """
    return {
        "lighthouseResult": {
            "categories": {
                "performance": {"score": 0.51},  # 51/100
                "accessibility": {"score": 0.75}
            },
            "audits": {
                "largest-contentful-paint": {"numericValue": 21200},  # 21.2s
                "first-contentful-paint": {"numericValue": 8500},     # 8.5s
                "cumulative-layout-shift": {"numericValue": 0.35},
                "server-response-time": {"numericValue": 1200}
            }
        },
        "loadingExperience": {
            "metrics": {
                "LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 21200},
                "FIRST_CONTENTFUL_PAINT_MS": {"percentile": 8500},
                "CUMULATIVE_LAYOUT_SHIFT_SCORE": {"percentile": 0.35}
            }
        }
    }


@pytest.fixture
def high_pagespeed_response() -> Dict[str, Any]:
    """Fixture con respuesta de PageSpeed API con métricas HIGH."""
    return {
        "lighthouseResult": {
            "categories": {
                "performance": {"score": 0.65},  # 65/100
                "accessibility": {"score": 0.80}
            },
            "audits": {
                "largest-contentful-paint": {"numericValue": 3200},   # 3.2s
                "first-contentful-paint": {"numericValue": 2000},     # 2.0s
                "cumulative-layout-shift": {"numericValue": 0.15},
                "server-response-time": {"numericValue": 800}
            }
        }
    }


@pytest.fixture
def medium_pagespeed_response() -> Dict[str, Any]:
    """Fixture con respuesta de PageSpeed API con métricas MEDIUM."""
    return {
        "lighthouseResult": {
            "categories": {
                "performance": {"score": 0.85},  # 85/100
                "accessibility": {"score": 0.90}
            },
            "audits": {
                "largest-contentful-paint": {"numericValue": 2200},   # 2.2s
                "first-contentful-paint": {"numericValue": 1400},     # 1.4s
                "cumulative-layout-shift": {"numericValue": 0.08},
                "server-response-time": {"numericValue": 600}
            }
        }
    }


@pytest.fixture
def good_pagespeed_response() -> Dict[str, Any]:
    """Fixture con respuesta de PageSpeed API con buenas métricas (LOW)."""
    return {
        "lighthouseResult": {
            "categories": {
                "performance": {"score": 0.95},  # 95/100
                "accessibility": {"score": 0.95}
            },
            "audits": {
                "largest-contentful-paint": {"numericValue": 1200},   # 1.2s
                "first-contentful-paint": {"numericValue": 900},      # 0.9s
                "cumulative-layout-shift": {"numericValue": 0.02},
                "server-response-time": {"numericValue": 200}
            }
        }
    }


class TestCalculateSeverityCritical:
    """Tests para cálculo de severidad CRÍTICA."""

    def test_calculate_severity_critical_performance_51(self, auditor, critical_pagespeed_response):
        """Performance 51, LCP 21.2s → CRITICAL."""
        analysis = auditor.analyze(critical_pagespeed_response, "https://hotel.com")
        
        assert analysis.severity == Severity.CRITICAL
        assert analysis.has_critical_issues is True
        assert analysis.performance_score == 51

    def test_calculate_severity_critical_lcp_only(self, auditor):
        """LCP > 4s aunque performance sea aceptable → CRITICAL."""
        metrics = {"performance": 75, "lcp": 5.0, "fcp": 1.5, "cls": 0.05}
        severity = auditor.calculate_severity(metrics)
        
        assert severity == Severity.CRITICAL

    def test_calculate_severity_critical_fcp(self, auditor):
        """FCP > 3s → CRITICAL."""
        metrics = {"performance": 75, "lcp": 2.0, "fcp": 3.5, "cls": 0.05}
        severity = auditor.calculate_severity(metrics)
        
        assert severity == Severity.CRITICAL

    def test_calculate_severity_critical_cls(self, auditor):
        """CLS > 0.25 → CRITICAL."""
        metrics = {"performance": 75, "lcp": 2.0, "fcp": 1.5, "cls": 0.30}
        severity = auditor.calculate_severity(metrics)
        
        assert severity == Severity.CRITICAL

    def test_calculate_severity_critical_performance_threshold(self, auditor):
        """Performance < 50 → CRITICAL."""
        metrics = {"performance": 49, "lcp": 2.0, "fcp": 1.5, "cls": 0.05}
        severity = auditor.calculate_severity(metrics)
        
        assert severity == Severity.CRITICAL


class TestCalculateSeverityHigh:
    """Tests para cálculo de severidad HIGH."""

    def test_calculate_severity_high_performance_65(self, auditor, high_pagespeed_response):
        """Performance 65 → HIGH."""
        analysis = auditor.analyze(high_pagespeed_response, "https://hotel.com")
        
        assert analysis.severity == Severity.HIGH
        assert analysis.has_critical_issues is True

    def test_calculate_severity_high_lcp(self, auditor):
        """LCP > 2.5s → HIGH."""
        metrics = {"performance": 85, "lcp": 3.0, "fcp": 1.5, "cls": 0.05}
        severity = auditor.calculate_severity(metrics)
        
        assert severity == Severity.HIGH

    def test_calculate_severity_high_fcp(self, auditor):
        """FCP > 1.8s → HIGH."""
        metrics = {"performance": 85, "lcp": 2.0, "fcp": 2.0, "cls": 0.05}
        severity = auditor.calculate_severity(metrics)
        
        assert severity == Severity.HIGH

    def test_calculate_severity_high_cls(self, auditor):
        """CLS > 0.1 → HIGH."""
        metrics = {"performance": 85, "lcp": 2.0, "fcp": 1.5, "cls": 0.15}
        severity = auditor.calculate_severity(metrics)
        
        assert severity == Severity.HIGH


class TestCalculateSeverityMedium:
    """Tests para cálculo de severidad MEDIUM."""

    def test_calculate_severity_medium_performance_85(self, auditor, medium_pagespeed_response):
        """Performance 85 → MEDIUM."""
        analysis = auditor.analyze(medium_pagespeed_response, "https://hotel.com")
        
        assert analysis.severity == Severity.MEDIUM
        assert analysis.has_critical_issues is False

    def test_calculate_severity_medium_lcp(self, auditor):
        """LCP > 1.8s → MEDIUM."""
        metrics = {"performance": 95, "lcp": 2.0, "fcp": 0.8, "cls": 0.03}
        severity = auditor.calculate_severity(metrics)
        
        assert severity == Severity.MEDIUM

    def test_calculate_severity_medium_performance_threshold(self, auditor):
        """Performance 89 → MEDIUM (justo debajo de 90)."""
        metrics = {"performance": 89, "lcp": 1.5, "fcp": 0.8, "cls": 0.03}
        severity = auditor.calculate_severity(metrics)
        
        assert severity == Severity.MEDIUM


class TestCalculateSeverityLow:
    """Tests para cálculo de severidad LOW."""

    def test_calculate_severity_low_good_performance(self, auditor, good_pagespeed_response):
        """Performance 95 → LOW."""
        analysis = auditor.analyze(good_pagespeed_response, "https://hotel.com")
        
        assert analysis.severity == Severity.LOW
        assert analysis.has_critical_issues is False

    def test_calculate_severity_low_perfect(self, auditor):
        """Métricas perfectas → LOW."""
        metrics = {"performance": 100, "lcp": 1.0, "fcp": 0.5, "cls": 0.01}
        severity = auditor.calculate_severity(metrics)
        
        assert severity == Severity.LOW


class TestGenerateClaimsCriticalPerformance:
    """Tests para generación de claims."""

    def test_generate_claims_critical_performance(self, auditor, critical_pagespeed_response):
        """Genera claim sobre pérdida de usuarios cuando performance es crítico."""
        analysis = auditor.analyze(critical_pagespeed_response, "https://hotel.com")
        claims = auditor.generate_claims(analysis)
        
        # Debe haber al menos un claim CRITICAL
        critical_claims = [c for c in claims if c.severity == Severity.CRITICAL]
        assert len(critical_claims) >= 1
        
        # El claim debe mencionar pérdida de usuarios o abandono
        messages = " ".join([c.message for c in claims])
        assert "abandono" in messages.lower() or "90%" in messages or "performance" in messages.lower()

    def test_generate_claims_includes_lcp_critical(self, auditor, critical_pagespeed_response):
        """Genera claim específico para LCP cuando es crítico."""
        analysis = auditor.analyze(critical_pagespeed_response, "https://hotel.com")
        claims = auditor.generate_claims(analysis)
        
        lcp_claims = [c for c in claims if "LCP" in c.message or "lcp" in c.message.lower()]
        assert len(lcp_claims) >= 1
        assert lcp_claims[0].severity == Severity.CRITICAL
        assert "21.2" in lcp_claims[0].evidence_excerpt or "21.2" in lcp_claims[0].message

    def test_generate_claims_includes_fcp_critical(self, auditor):
        """Genera claim específico para FCP cuando es crítico."""
        analysis = PerformanceAnalysis(
            performance_score=45,
            accessibility_score=70,
            metrics=PerformanceMetrics(lcp=3.0, fcp=3.5, cls=0.1, ttfb=1000),
            severity=Severity.CRITICAL,
            has_critical_issues=True
        )
        claims = auditor.generate_claims(analysis)
        
        fcp_claims = [c for c in claims if "FCP" in c.message or "fcp" in c.message.lower()]
        assert len(fcp_claims) >= 1
        assert fcp_claims[0].severity == Severity.CRITICAL

    def test_generate_claims_high_severity(self, auditor, high_pagespeed_response):
        """Genera claims HIGH para métricas que exceden umbral HIGH."""
        analysis = auditor.analyze(high_pagespeed_response, "https://hotel.com")
        claims = auditor.generate_claims(analysis)
        
        high_claims = [c for c in claims if c.severity == Severity.HIGH]
        assert len(high_claims) >= 1


class TestNormalizePageSpeedResponse:
    """Tests para normalización de respuestas de PageSpeed API."""

    def test_normalize_pagespeed_response(self, auditor, critical_pagespeed_response):
        """Extrae métricas correctamente de respuesta PageSpeed."""
        normalized = auditor.normalize_pagespeed_response(critical_pagespeed_response)
        
        assert normalized["performance_score"] == 51
        assert normalized["lcp"] == 21.2  # Convertido de ms a s
        assert normalized["fcp"] == 8.5
        assert normalized["cls"] == 0.35
        assert normalized["accessibility_score"] == 75

    def test_normalize_with_field_data_priority(self, auditor):
        """Prioriza loadingExperience (field data) sobre lighthouse."""
        response = {
            "lighthouseResult": {
                "categories": {"performance": {"score": 0.70}},
                "audits": {
                    "largest-contentful-paint": {"numericValue": 3000},  # 3s
                    "first-contentful-paint": {"numericValue": 1500}
                }
            },
            "loadingExperience": {
                "metrics": {
                    "LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 5000},  # 5s
                    "FIRST_CONTENTFUL_PAINT_MS": {"percentile": 2000}
                }
            }
        }
        normalized = auditor.normalize_pagespeed_response(response)
        
        # Debe usar field data (5000ms = 5s)
        assert normalized["lcp"] == 5.0
        assert normalized["fcp"] == 2.0

    def test_normalize_fallback_to_lab_data(self, auditor):
        """Usa lighthouse audits cuando no hay field data."""
        response = {
            "lighthouseResult": {
                "categories": {"performance": {"score": 0.80}},
                "audits": {
                    "largest-contentful-paint": {"numericValue": 2500},
                    "first-contentful-paint": {"numericValue": 1200},
                    "cumulative-layout-shift": {"numericValue": 0.05}
                }
            }
            # Sin loadingExperience
        }
        normalized = auditor.normalize_pagespeed_response(response)
        
        assert normalized["lcp"] == 2.5
        assert normalized["fcp"] == 1.2
        assert normalized["cls"] == 0.05

    def test_normalize_missing_metrics(self, auditor):
        """Maneja respuestas con métricas faltantes."""
        response = {
            "lighthouseResult": {
                "categories": {"performance": {"score": 0.60}}
                # Sin audits ni loadingExperience
            }
        }
        normalized = auditor.normalize_pagespeed_response(response)
        
        assert normalized["performance_score"] == 60
        assert normalized["lcp"] is None
        assert normalized["fcp"] is None
        assert normalized["cls"] is None

    def test_normalize_empty_response(self, auditor):
        """Maneja respuesta vacía o malformada."""
        response = {}
        normalized = auditor.normalize_pagespeed_response(response)
        
        assert normalized["performance_score"] == 0
        assert normalized["lcp"] is None
        assert normalized["fcp"] is None
