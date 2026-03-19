"""PageSpeedAuditorV2 - Auditor de performance con severidad automática.

Sprint 1, Fase 1: Auditor de performance basado en umbrales de severidad.
Procesa datos de PageSpeed API ya obtenidos (no llama a la API).
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from enums.severity import Severity
from data_models.canonical_assessment import PerformanceAnalysis, PerformanceMetrics
from data_models.claim import Claim


# Umbrales de severidad para métricas de performance
PERFORMANCE_THRESHOLDS = {
    "CRITICAL": {"performance": 50, "lcp": 4.0, "fcp": 3.0, "cls": 0.25},
    "HIGH": {"performance": 70, "lcp": 2.5, "fcp": 1.8, "cls": 0.1},
    "MEDIUM": {"performance": 90, "lcp": 1.8, "fcp": 1.0, "cls": 0.05},
}

# Confianza de datos de PageSpeed API
PAGESPEED_CONFIDENCE = 0.95


@dataclass
class PageSpeedMetrics:
    """Métricas extraídas de PageSpeed API."""
    performance_score: float
    lcp: Optional[float] = None
    fcp: Optional[float] = None
    cls: Optional[float] = None
    ttfb: Optional[float] = None
    accessibility_score: Optional[float] = None


class PageSpeedAuditorV2:
    """Auditor de performance con severidad automática basada en umbrales.

    Procesa datos crudos de PageSpeed API y genera:
    - PerformanceAnalysis con métricas y severidad calculada
    - Lista de Claims basados en los umbrales excedidos

    Args:
        pagespeed_data: Datos crudos de la API de PageSpeed
        url: URL del sitio analizado

    Example:
        auditor = PageSpeedAuditorV2()
        analysis = auditor.analyze(pagespeed_data, "https://hotel.com")
        claims = auditor.generate_claims(analysis)
    """

    def analyze(self, pagespeed_data: dict, url: str) -> PerformanceAnalysis:
        """Analiza datos de PageSpeed API y genera PerformanceAnalysis.

        Args:
            pagespeed_data: Respuesta cruda de PageSpeed API
            url: URL del sitio analizado

        Returns:
            PerformanceAnalysis con métricas extraídas y severidad calculada
        """
        normalized = self.normalize_pagespeed_response(pagespeed_data)
        metrics = self._extract_metrics(normalized)

        severity = self.calculate_severity({
            "performance": metrics.performance_score,
            "lcp": metrics.lcp,
            "fcp": metrics.fcp,
            "cls": metrics.cls,
        })

        performance_metrics = PerformanceMetrics(
            lcp=metrics.lcp,
            fcp=metrics.fcp,
            cls=metrics.cls,
            ttfb=metrics.ttfb,
        )

        return PerformanceAnalysis(
            performance_score=metrics.performance_score,
            accessibility_score=metrics.accessibility_score,
            metrics=performance_metrics,
            severity=severity,
            has_critical_issues=severity in (Severity.CRITICAL, Severity.HIGH),
        )

    def calculate_severity(self, metrics: dict) -> Severity:
        """Calcula severidad general basada en umbrales.

        Args:
            metrics: Dict con performance, lcp, fcp, cls

        Returns:
            Severity: CRITICAL, HIGH, MEDIUM, o LOW

        Rules:
            - CRITICAL: performance < 50 o lcp > 4s o fcp > 3s o cls > 0.25
            - HIGH: performance < 70 o lcp > 2.5s o fcp > 1.8s o cls > 0.1
            - MEDIUM: performance < 90 o lcp > 1.8s o fcp > 1.0s o cls > 0.05
            - LOW: Ningún umbral excedido
        """
        performance = metrics.get("performance", 100)
        lcp = metrics.get("lcp", 0)
        fcp = metrics.get("fcp", 0)
        cls = metrics.get("cls", 0)

        critical = PERFORMANCE_THRESHOLDS["CRITICAL"]
        high = PERFORMANCE_THRESHOLDS["HIGH"]
        medium = PERFORMANCE_THRESHOLDS["MEDIUM"]

        # Check CRITICAL thresholds
        if (performance < critical["performance"] or
            (lcp and lcp > critical["lcp"]) or
            (fcp and fcp > critical["fcp"]) or
            (cls and cls > critical["cls"])):
            return Severity.CRITICAL

        # Check HIGH thresholds
        if (performance < high["performance"] or
            (lcp and lcp > high["lcp"]) or
            (fcp and fcp > high["fcp"]) or
            (cls and cls > high["cls"])):
            return Severity.HIGH

        # Check MEDIUM thresholds
        if (performance < medium["performance"] or
            (lcp and lcp > medium["lcp"]) or
            (fcp and fcp > medium["fcp"]) or
            (cls and cls > medium["cls"])):
            return Severity.MEDIUM

        return Severity.LOW

    def generate_claims(self, analysis: PerformanceAnalysis) -> List[Claim]:
        """Genera claims basados en el análisis de performance.

        Args:
            analysis: PerformanceAnalysis con métricas y severidad

        Returns:
            Lista de Claims con categoría "performance"

        Rules:
            - CRITICAL severity → Claim CRITICAL sobre pérdida de usuarios
            - HIGH severity → Claim HIGH por cada métrica que excede umbral
            - Incluir valores exactos en evidence_excerpt
        """
        claims = []
        metrics = analysis.metrics

        # Claim CRITICAL si severidad es CRITICAL
        if analysis.severity == Severity.CRITICAL:
            claims.append(Claim(
                source_id="pagespeed_auditor_v2",
                evidence_excerpt=f"Performance {analysis.performance_score}/100",
                severity=Severity.CRITICAL,
                category="performance",
                message=f"Performance {analysis.performance_score}/100 - ~90% abandono por lentitud",
                confidence=PAGESPEED_CONFIDENCE,
            ))

            # Claim específico para LCP si es crítico
            if metrics.lcp and metrics.lcp > PERFORMANCE_THRESHOLDS["CRITICAL"]["lcp"]:
                claims.append(Claim(
                    source_id="pagespeed_auditor_v2",
                    evidence_excerpt=f"LCP {metrics.lcp}s (umbral: <{PERFORMANCE_THRESHOLDS['CRITICAL']['lcp']}s)",
                    severity=Severity.CRITICAL,
                    category="performance",
                    message=f"LCP {metrics.lcp}s (umbral: <{PERFORMANCE_THRESHOLDS['CRITICAL']['lcp']}s)",
                    confidence=PAGESPEED_CONFIDENCE,
                ))

            # Claim específico para FCP si es crítico
            if metrics.fcp and metrics.fcp > PERFORMANCE_THRESHOLDS["CRITICAL"]["fcp"]:
                claims.append(Claim(
                    source_id="pagespeed_auditor_v2",
                    evidence_excerpt=f"FCP {metrics.fcp}s (umbral: <{PERFORMANCE_THRESHOLDS['CRITICAL']['fcp']}s)",
                    severity=Severity.CRITICAL,
                    category="performance",
                    message=f"FCP {metrics.fcp}s (umbral: <{PERFORMANCE_THRESHOLDS['CRITICAL']['fcp']}s)",
                    confidence=PAGESPEED_CONFIDENCE,
                ))

        # Claims HIGH para métricas que exceden umbral HIGH (pero no críticas)
        elif analysis.severity == Severity.HIGH:
            if metrics.lcp and metrics.lcp > PERFORMANCE_THRESHOLDS["HIGH"]["lcp"]:
                claims.append(Claim(
                    source_id="pagespeed_auditor_v2",
                    evidence_excerpt=f"LCP {metrics.lcp}s (umbral: <{PERFORMANCE_THRESHOLDS['HIGH']['lcp']}s)",
                    severity=Severity.HIGH,
                    category="performance",
                    message=f"LCP {metrics.lcp}s excede umbral recomendado",
                    confidence=PAGESPEED_CONFIDENCE,
                ))

            if metrics.fcp and metrics.fcp > PERFORMANCE_THRESHOLDS["HIGH"]["fcp"]:
                claims.append(Claim(
                    source_id="pagespeed_auditor_v2",
                    evidence_excerpt=f"FCP {metrics.fcp}s (umbral: <{PERFORMANCE_THRESHOLDS['HIGH']['fcp']}s)",
                    severity=Severity.HIGH,
                    category="performance",
                    message=f"FCP {metrics.fcp}s excede umbral recomendado",
                    confidence=PAGESPEED_CONFIDENCE,
                ))

        return claims

    def normalize_pagespeed_response(self, api_response: dict) -> dict:
        """Normaliza respuesta de PageSpeed API a formato estándar.

        Soporta mobile y desktop. Extrae métricas de:
        - loadingExperience (field data)
        - lighthouseResult (lab data)

        Args:
            api_response: Respuesta cruda de PageSpeed API

        Returns:
            Dict normalizado con métricas estándar
        """
        normalized = {
            "performance_score": 0,
            "lcp": None,
            "fcp": None,
            "cls": None,
            "ttfb": None,
            "accessibility_score": None,
        }

        lighthouse = api_response.get("lighthouseResult", {})
        loading_exp = api_response.get("loadingExperience", {})
        metrics = loading_exp.get("metrics", {})

        # Performance score from lighthouse
        categories = lighthouse.get("categories", {})
        perf_category = categories.get("performance", {})
        if perf_category.get("score") is not None:
            normalized["performance_score"] = perf_category["score"] * 100

        # Accessibility score
        acc_category = categories.get("accessibility", {})
        if acc_category.get("score") is not None:
            normalized["accessibility_score"] = acc_category["score"] * 100

        # Try loadingExperience metrics first (field data)
        if "LARGEST_CONTENTFUL_PAINT_MS" in metrics:
            lcp_data = metrics["LARGEST_CONTENTFUL_PAINT_MS"]
            normalized["lcp"] = lcp_data.get("percentile", 0) / 1000  # Convert ms to s

        if "FIRST_CONTENTFUL_PAINT_MS" in metrics:
            fcp_data = metrics["FIRST_CONTENTFUL_PAINT_MS"]
            normalized["fcp"] = fcp_data.get("percentile", 0) / 1000

        if "CUMULATIVE_LAYOUT_SHIFT_SCORE" in metrics:
            cls_data = metrics["CUMULATIVE_LAYOUT_SHIFT_SCORE"]
            normalized["cls"] = cls_data.get("percentile", 0)

        # Fallback to lighthouse audits (lab data)
        audits = lighthouse.get("audits", {})

        if normalized["lcp"] is None and "largest-contentful-paint" in audits:
            lcp_audit = audits["largest-contentful-paint"]
            normalized["lcp"] = lcp_audit.get("numericValue", 0) / 1000  # ms to s

        if normalized["fcp"] is None and "first-contentful-paint" in audits:
            fcp_audit = audits["first-contentful-paint"]
            normalized["fcp"] = fcp_audit.get("numericValue", 0) / 1000

        if normalized["cls"] is None and "cumulative-layout-shift" in audits:
            cls_audit = audits["cumulative-layout-shift"]
            normalized["cls"] = cls_audit.get("numericValue", 0)

        # TTFB from server-response-time audit
        if "server-response-time" in audits:
            ttfb_audit = audits["server-response-time"]
            normalized["ttfb"] = ttfb_audit.get("numericValue", 0)

        return normalized

    def _extract_metrics(self, normalized: dict) -> PageSpeedMetrics:
        """Extrae métricas normalizadas a objeto PageSpeedMetrics."""
        return PageSpeedMetrics(
            performance_score=normalized.get("performance_score", 0),
            lcp=normalized.get("lcp"),
            fcp=normalized.get("fcp"),
            cls=normalized.get("cls"),
            ttfb=normalized.get("ttfb"),
            accessibility_score=normalized.get("accessibility_score"),
        )
