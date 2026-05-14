"""
Human Checklist Generator — FASE-0F.

Generates a reduced human-review checklist (<= 10 items) from a
DeliveryQualityReport. The human reviews exceptions only; they do NOT
reconstruct coherence or re-validate gates.

Design:
- Derives items from delivery_quality_report.json data.
- Items cover: pending exceptions, data conflicts, asset specificity estimates,
  commercial decision, and final tone.
- Max 10 checkbox items total.
"""

import logging
from datetime import datetime
from pathlib import Path

from modules.quality_gates.delivery_quality_report import DeliveryQualityReport

logger = logging.getLogger(__name__)

MAX_ITEMS = 10


class HumanChecklistGenerator:
    """
    Generates a human-readable markdown checklist from a DeliveryQualityReport.

    Usage:
        generator = HumanChecklistGenerator()
        checklist_md = generator.generate(report)
        generator.save(checklist_md, Path("output/.../human_checklist.md"))
    """

    def generate(self, report: DeliveryQualityReport) -> str:
        """
        Generate a markdown checklist with <= 10 human-review items.

        Args:
            report: DeliveryQualityReport from quality gate evaluation.

        Returns:
            Markdown string with checkbox items for human review.
        """
        items: list[str] = []

        # ── 1. Exceptions from human_review_items ─────────────────────────
        for exc in report.human_review_items:
            items.append(f"Review exception: {exc}")

        # ── 2. Coverage gate data conflicts ──────────────────────────────
        coverage = report.coverage_gate
        if coverage and not coverage.get("passed", True):
            details = coverage.get("details", {})
            reason = details.get("reason", "Coverage check failed")
            items.append(f"Coverage gap: {reason}")

        # ── 3. Asset specificity / confidence concerns ───────────────────
        specificity = report.asset_specificity_gate
        if specificity and not specificity.get("passed", True):
            details = specificity.get("details", {})
            avg_conf = details.get("avg_confidence", 0)
            low_count = details.get("low_confidence_count", 0)
            total = details.get("total_assets", 0)
            if low_count > 0:
                items.append(
                    f"Asset confidence: {low_count}/{total} assets below threshold "
                    f"(avg confidence {avg_conf:.2f})"
                )
            else:
                items.append(f"Asset specificity issue: {details.get('reason', 'unknown')}")

        # ── 4. Evidence gate ─────────────────────────────────────────────
        evidence = report.evidence_gate
        if evidence and not evidence.get("passed", True):
            details = evidence.get("details", {})
            items.append(f"Evidence quality: {details.get('reason', 'Insufficient evidence')}")

        # ── 5. Blocking gates summary ────────────────────────────────────
        summary = report.summary
        blocking = summary.get("blocking_gates", [])
        warning = summary.get("warning_gates", [])
        if blocking:
            gates_str = ", ".join(blocking)
            items.append(f"BLOCKING gates active: {gates_str} — delivery cannot proceed")
        if warning:
            gates_str = ", ".join(warning)
            items.append(f"WARNING gates active: {gates_str} — review before proceeding")

        # ── 6. Commercial decision ───────────────────────────────────────
        if report.status == "FAIL":
            items.append("Commercial decision: Delivery is BLOCKED — review exceptions and decide path forward")
        elif report.status == "WARNING":
            items.append("Commercial decision: Delivery can proceed with warnings — confirm risk acceptance")
        else:
            items.append("Commercial decision: All gates passed — confirm delivery is ready")

        # ── 7. Final quality / tone check ────────────────────────────────
        coherence_score = summary.get("coherence_score")
        if coherence_score is not None:
            if coherence_score < 0.8:
                items.append(f"Final review: Coherence score {coherence_score:.2f} — manually verify narrative consistency")
            else:
                items.append(f"Final review: Coherence score {coherence_score:.2f} — acceptable range")
        else:
            items.append("Final review: No coherence score available — manually verify narrative consistency")

        # ── Truncate to MAX_ITEMS ────────────────────────────────────────
        items = items[:MAX_ITEMS]

        # ── Build markdown ───────────────────────────────────────────────
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = [
            "# Human Review Checklist",
            "",
            f"> Generated: {timestamp} | Status: **{report.status}** | Blocking: **{report.blocking}**",
            f"> Gates: {summary.get('passed', 0)}/{summary.get('total_gates', 0)} passed",
            "",
            "The human reviews **exceptions only** — do NOT reconstruct coherence or re-validate gates.",
            "",
        ]

        for i, item in enumerate(items, 1):
            lines.append(f"- [ ] {item}")

        # Edge case: no items at all
        if not items:
            lines.append("- [ ] No exceptions to review — all gates passed cleanly")

        lines.append("")
        lines.append("---")
        lines.append("*Checklist generated by HumanChecklistGenerator (FASE-0F)*")

        return "\n".join(lines) + "\n"

    def save(self, checklist: str, path: Path) -> None:
        """
        Save the checklist markdown to a file.

        Args:
            checklist: Markdown string from generate().
            path: Destination file path.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(checklist, encoding="utf-8")
        logger.info(f"Human checklist saved to {path}")
