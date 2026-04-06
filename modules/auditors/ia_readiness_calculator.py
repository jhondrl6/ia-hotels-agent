from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class IAReadinessReport:
    """Report containing IA readiness assessment results."""
    overall_score: float
    components: Dict[str, float]
    status: str
    actionable_items: List[str] = field(default_factory=list)


class IAReadinessCalculator:
    """Calculator for IA readiness scoring based on multiple components."""

    WEIGHTS = {
        "schema_quality": 0.22,
        "crawler_access": 0.22,
        "citability": 0.23,
        "llms_txt": 0.09,
        "brand_signals": 0.14,
        "ga4_indirect": 0.10,
    }

    def calculate(
        self,
        schema_coverage: float,
        crawler_score: float,
        citability_score: float,
        has_llmstxt: bool,
        brand_score: float,
        ga4_indirect_score: Optional[float] = None,
    ) -> IAReadinessReport:
        """Calculate IA readiness report from component scores.
        
        Args:
            schema_coverage: Schema coverage ratio (0-1)
            crawler_score: Crawler access score (0-100)
            citability_score: Citability score (0-100)
            has_llmstxt: Whether /llms.txt exists
            brand_score: Brand signals score (0-100)
            ga4_indirect_score: GA4 indirect traffic score (0-100), optional.
                               None means GA4 is not available.
            
        Returns:
            IAReadinessReport with overall score, components, status, and actionable items
        """
        components: Dict[str, float] = {}
        components["schema_quality"] = schema_coverage * 100
        components["crawler_access"] = crawler_score
        components["citability"] = citability_score
        components["llms_txt"] = 100 if has_llmstxt else 0
        components["brand_signals"] = brand_score

        if ga4_indirect_score is not None:
            components["ga4_indirect"] = ga4_indirect_score
            overall = sum(components[k] * self.WEIGHTS[k] for k in self.WEIGHTS)
        else:
            # GA4 unavailable: redistribute its weight proportionally
            available = {k: v for k, v in self.WEIGHTS.items() if k != "ga4_indirect"}
            total_weight = sum(available.values())
            overall = sum(
                components[k] * (available[k] / total_weight)
                for k in available
            )

        if overall >= 70:
            status = "Ready"
        elif overall >= 50:
            status = "Needs Work"
        else:
            status = "Critical"

        actionable = self._generate_actionable_items(components)

        return IAReadinessReport(
            overall_score=overall,
            components=components,
            status=status,
            actionable_items=actionable
        )

    def _generate_actionable_items(self, components: Dict[str, float]) -> List[str]:
        """Generate actionable items based on component scores."""
        items = []

        if components.get("schema_quality", 0) < 70:
            items.append("Improve structured data markup (JSON-LD) for better AI understanding")

        if components.get("crawler_access", 0) < 70:
            items.append("Review robots.txt to ensure AI crawler access is permitted")

        if components.get("citability", 0) < 70:
            items.append("Add clear author attribution and citeable content sections")

        if components.get("llms_txt", 0) == 0:
            items.append("Create /llms.txt file with content inventory for AI crawlers")

        if components.get("brand_signals", 0) < 70:
            items.append("Strengthen brand signals: consistent NAP, social profiles, and entity markup")

        if "ga4_indirect" not in components:
            items.append("Configure Google Analytics 4 to measure indirect traffic from AI referrals")

        return items
