"""Postprocessors - Document quality gates and content scrubbers for client delivery.

Modules:
- document_quality_gate: Blocker and warning checks for commercial documents
- content_scrubber: Idempotent text fixes for common LLM output issues

Usage:
    from modules.postprocessors import DocumentQualityGate, ContentScrubber
"""


def __getattr__(name):
    """Lazy imports to avoid cascade failures on WSL."""
    if name == "DocumentQualityGate":
        from modules.postprocessors.document_quality_gate import DocumentQualityGate
        return DocumentQualityGate
    if name == "DocumentQualityIssue":
        from modules.postprocessors.document_quality_gate import DocumentQualityIssue
        return DocumentQualityIssue
    if name == "DocumentQualityResult":
        from modules.postprocessors.document_quality_gate import DocumentQualityResult
        return DocumentQualityResult
    if name == "ContentScrubber":
        from modules.postprocessors.content_scrubber import ContentScrubber
        return ContentScrubber
    if name == "ScrubResult":
        from modules.postprocessors.content_scrubber import ScrubResult
        return ScrubResult
    raise AttributeError(f"module postprocessors has no attribute {name!r}")


__all__ = [
    "DocumentQualityGate",
    "DocumentQualityIssue",
    "DocumentQualityResult",
    "ContentScrubber",
    "ScrubResult",
]
