"""
Data Derivation Layer — Derive missing validated_data fields from audit_report.

FASE-0H-G8: Transforms confidence system from binary (field exists/doesn't exist)
to semantic (derive what's possible, distinguish REQUIRED vs RECOMMENDED).

Principles:
- Zero hardcoding per asset — algorithmic derivation only.
- Zero external APIs — only uses data already in audit_report.
- Never overwrite existing validated_data fields (direct source wins).
- Never invent data — if not derivable, return inferred=False.
"""

from typing import Any, Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DataDerivationLayer:
    """Derives missing validated_data fields from the audit_report JSON.

    Usage:
        layer = DataDerivationLayer()
        derived = layer.derive(audit_report)
        # derived = {"og_tags_detected": DataPoint(source="derived", ...), ...}
    """

    # Substructures of audit_report that may contain derivable data
    AUDIT_SOURCES = [
        "seo_elements",
        "schema",
        "metadata",
        "performance",
        "validation",
        "llm_report",
        "gbp",
        "ai_crawlers",
        "citability",
        "ia_readiness",
        "aeo_snippets",
        "overall",
    ]

    def derive(self, audit_report: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Derive missing fields from the audit_report.

        Args:
            audit_report: Complete audit report dict (from v4_audit/audit_report_*.json)

        Returns:
            Dict mapping field_name → {value, source, inferred, confidence}
            Fields that cannot be derived are omitted entirely.
        """
        if not audit_report or not isinstance(audit_report, dict):
            logger.warning("DataDerivationLayer: empty or invalid audit_report")
            return {}

        derived = {}

        # 1. og_tags_detected — from seo_elements
        og_result = self._derive_og_tags_detected(audit_report)
        if og_result is not None:
            derived["og_tags_detected"] = og_result

        # 2. org_data — from schema
        org_result = self._derive_org_data(audit_report)
        if org_result is not None:
            derived["org_data"] = org_result

        # 3. ga4_available — from tracking scripts in validation/seo
        ga4_result = self._derive_ga4_available(audit_report)
        if ga4_result is not None:
            derived["ga4_available"] = ga4_result

        # 4. organic_traffic — from performance proxy
        traffic_result = self._derive_organic_traffic(audit_report)
        if traffic_result is not None:
            derived["organic_traffic"] = traffic_result

        # 5. metadata — from audit metadata section
        metadata_result = self._derive_metadata(audit_report)
        if metadata_result is not None:
            derived["metadata"] = metadata_result

        logger.info(
            f"DataDerivationLayer: derived {len(derived)} fields: "
            f"{list(derived.keys())}"
        )
        return derived

    def _derive_og_tags_detected(self, audit: Dict) -> Optional[Dict[str, Any]]:
        """Derive og_tags_detected from seo_elements.

        Checks:
        - seo_elements.open_graph (bool)
        - seo_elements.open_graph_tags (dict — if non-empty, tags exist)
        - seo_elements.notes for OG-related mentions

        Returns None if no seo_elements data available (cannot derive anything).
        """
        seo = audit.get("seo_elements")
        if not seo or not isinstance(seo, dict):
            return None  # Cannot derive

        detected = False
        sources = []

        # Primary: open_graph boolean flag
        if "open_graph" in seo:
            if seo["open_graph"]:
                detected = True
                sources.append("seo_elements.open_graph=True")
            else:
                sources.append("seo_elements.open_graph=False")

        # Secondary: open_graph_tags dict (non-empty = tags found)
        og_tags = seo.get("open_graph_tags")
        if isinstance(og_tags, dict) and og_tags:
            detected = True
            sources.append(f"seo_elements.open_graph_tags ({len(og_tags)} tags)")

        # Tertiary: check notes for OG-related content
        notes = seo.get("notes", "")
        if isinstance(notes, str) and "og" in notes.lower():
            if "detected 0 og" in notes.lower():
                # Explicitly zero — reinforces False
                pass
            elif "og tags" in notes.lower():
                sources.append("seo_elements.notes (og mentioned)")

        return {
            "value": detected,
            "source": "; ".join(sources) if sources else "seo_elements",
            "inferred": True,
            "confidence": 0.85,  # High confidence: direct SEO audit data
        }

    def _derive_org_data(self, audit: Dict) -> Optional[Dict[str, Any]]:
        """Derive org_data from schema section.

        Checks:
        - schema.org_schema_detected
        - schema.properties (may contain Organization fields)
        - gbp data (can supplement org info)

        Returns None if no derivable data at all.
        """
        schema = audit.get("schema", {})
        gbp = audit.get("gbp", {})
        hotel_name = audit.get("hotel_name", "")

        org_data = {}
        sources = []
        detected = False

        if isinstance(schema, dict):
            if schema.get("org_schema_detected"):
                detected = True
                sources.append("schema.org_schema_detected=True")

            # Try to extract from schema.properties
            props = schema.get("properties", {})
            if isinstance(props, dict):
                org_data.update({
                    k: v for k, v in props.items()
                    if k in ("name", "url", "address", "telephone",
                             "email", "sameAs", "logo")
                })

        # Fallback: derive minimal org_data from GBP + hotel_name
        if not org_data:
            if hotel_name:
                org_data["name"] = hotel_name
            if isinstance(gbp, dict):
                if gbp.get("website"):
                    org_data["url"] = gbp["website"]
                if gbp.get("address"):
                    org_data["address"] = gbp["address"]
                if gbp.get("phone"):
                    org_data["telephone"] = gbp["phone"]
            if org_data:
                sources.append("gbp (fallback)")
                detected = False

        if not org_data and not detected:
            # Nothing derivable at all
            return {
                "value": {},
                "source": "none available",
                "inferred": False,
                "confidence": 0.3,  # Low confidence: no org data anywhere
            }

        confidence = 0.8 if detected else 0.5

        return {
            "value": org_data,
            "source": "; ".join(sources) if sources else "schema",
            "inferred": True,
            "confidence": confidence,
        }

    def _derive_ga4_available(self, audit: Dict) -> Optional[Dict[str, Any]]:
        """Derive ga4_available from audit data.

        Checks:
        - ai_crawlers (presence of google-analytics crawlers)
        - validation (script detection, if available)
        - seo_elements (any analytics references)

        For this hotel: no GA4 data available in audit.
        Returns inferred=False when no indicators found.
        """
        indicators = []
        found = False

        # Check ai_crawlers for analytics-related crawlers
        crawlers = audit.get("ai_crawlers", {})
        if isinstance(crawlers, dict):
            allowed = crawlers.get("allowed_crawlers", [])
            if isinstance(allowed, list):
                for crawler in allowed:
                    if isinstance(crawler, str) and any(
                        term in crawler.lower()
                        for term in ("google-analytics", "gtag", "ga4", "analytics")
                    ):
                        found = True
                        indicators.append(f"crawler: {crawler}")

        # Check seo_elements notes for analytics mentions
        seo = audit.get("seo_elements", {})
        if isinstance(seo, dict):
            notes = seo.get("notes", "")
            if isinstance(notes, str) and any(
                term in notes.lower()
                for term in ("analytics", "gtag", "ga4", "google tag")
            ):
                found = True
                indicators.append("seo_notes")

        if not found and not indicators:
            # Cannot determine — no evidence either way
            return None  # Omit — don't invent

        return {
            "value": found,
            "source": "; ".join(indicators) if indicators else "none detected",
            "inferred": True,
            "confidence": 0.7 if found else 0.4,
        }

    def _derive_organic_traffic(self, audit: Dict) -> Optional[Dict[str, Any]]:
        """Derive organic_traffic proxy from performance data.

        Checks:
        - performance.mobile_score / desktop_score (PageSpeed)
        - llm_report.mention_rate / share_of_voice (visibility proxy)
        - aeo_snippets.snippet_score

        Returns None if no proxy data available.
        """
        proxies = {}

        perf = audit.get("performance", {})
        if isinstance(perf, dict) and perf.get("has_field_data"):
            if perf.get("mobile_score") is not None:
                proxies["mobile_score"] = perf["mobile_score"]
            if perf.get("desktop_score") is not None:
                proxies["desktop_score"] = perf["desktop_score"]

        llm = audit.get("llm_report", {})
        if isinstance(llm, dict):
            if llm.get("share_of_voice", 0) > 0:
                proxies["share_of_voice"] = llm["share_of_voice"]
            if llm.get("mention_rate", 0) > 0:
                proxies["mention_rate"] = llm["mention_rate"]

        snippets = audit.get("aeo_snippets", {})
        if isinstance(snippets, dict):
            if snippets.get("snippet_score", 0) > 0:
                proxies["snippet_score"] = snippets["snippet_score"]

        if not proxies:
            return None  # Nothing derivable

        # Use proxies as a traffic estimation indicator
        return {
            "value": proxies,
            "source": "performance + llm_report + aeo_snippets (proxy)",
            "inferred": True,
            "confidence": 0.4,  # Low confidence: proxy estimation
        }

    def _derive_metadata(self, audit: Dict) -> Optional[Dict[str, Any]]:
        """Derive metadata from audit metadata section.

        The audit_report has a 'metadata' key with:
        cms_detected, title, description, has_default_title,
        has_default_description, has_issues, issues, confidence
        """
        meta = audit.get("metadata")
        if not meta or not isinstance(meta, dict):
            return None  # Cannot derive

        # If metadata is empty or has no useful keys, skip
        useful_keys = {"cms_detected", "title", "description", "has_issues", "issues"}
        if not any(k in meta for k in useful_keys):
            return None

        return {
            "value": dict(meta),  # Copy to avoid mutation
            "source": "audit.metadata",
            "inferred": True,
            "confidence": 0.8,  # Direct audit data, not estimated
        }


def merge_derived_into_validated(
    validated_data: Dict[str, Any],
    derived: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Merge derived fields into validated_data dict.

    Rules:
    - Never overwrite existing keys (direct source wins).
    - Derived fields are added as dicts with source/confidence/value metadata.

    Args:
        validated_data: Current validated_data dict
        derived: Output from DataDerivationLayer.derive()

    Returns:
        validated_data with derived fields merged in (mutated in place + returned)
    """
    for field_name, field_info in derived.items():
        if field_name in validated_data:
            logger.debug(
                f"merge_derived: skipping '{field_name}' — already in validated_data"
            )
            continue

        validated_data[field_name] = field_info
        logger.info(
            f"merge_derived: added '{field_name}' "
            f"(confidence={field_info.get('confidence')}, "
            f"source={field_info.get('source')})"
        )

    return validated_data
