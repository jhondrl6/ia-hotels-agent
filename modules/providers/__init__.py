"""Providers module - LLM providers and external service integrations."""

from .llm_provider import LLMProvider
from .benchmark_resolver import BenchmarkResolver, BenchmarkResult

# T8A/C: Autonomous Research Engine
from .autonomous_researcher import (
    AutonomousResearcher,
    Researcher,
    ResearchOutput,
    ResearchResult,
    calculate_research_confidence,
    detect_gaps,
)

__all__ = [
    "LLMProvider",
    "BenchmarkResolver",
    "BenchmarkResult",
    # T8A/C: Autonomous Research
    "AutonomousResearcher",
    "Researcher",
    "ResearchOutput",
    "ResearchResult",
    "calculate_research_confidence",
    "detect_gaps",
]
