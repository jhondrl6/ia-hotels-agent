"""Content Standards Validator.

Validates content against GEO/AEO standards defined in guidelines.yaml.
Checks first paragraph length, forbidden words, and data table requirements.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    passed: bool
    errors: List[str]
    warnings: List[str]
    checks_run: int


CONTENT_TYPES_REQUIRE_TABLE: Set[str] = {
    "definition_page",
    "data_research",
}


class ContentValidator:
    """Validates content against GEO/AEO standards.
    
    Checks:
    1. First paragraph word count <= max_words
    2. Forbidden words are not present
    3. Content types that require data tables have them
    """
    
    DEFAULT_FORBIDDEN_WORDS: Set[str] = {
        "delve",
        "comprehensive",
        "in today's landscape",
        "integral",
        "profundicemos",
    }
    
    DEFAULT_MAX_FIRST_PARAGRAPH_WORDS = 40
    
    TABLE_PATTERN = re.compile(
        r"<table|"
        r"\|[^\n]+\|[^\n]*\n\|[-:| ]+\||"
        r"\{\|\s*$",
        re.IGNORECASE | re.MULTILINE
    )
    
    def __init__(self, guidelines_path: Path | None = None):
        """Initialize validator with optional custom guidelines path."""
        if guidelines_path is None:
            guidelines_path = Path(__file__).parent.parent.parent / ".conductor" / "guidelines.yaml"
        self.guidelines_path = guidelines_path
        self._config: Dict[str, Any] | None = None
        self._forbidden_words: Set[str] = self.DEFAULT_FORBIDDEN_WORDS
        self._max_first_paragraph_words = self.DEFAULT_MAX_FIRST_PARAGRAPH_WORDS
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from guidelines.yaml."""
        if self._config is not None:
            return self._config
        
        if not self.guidelines_path.exists():
            return {}
        
        with open(self.guidelines_path, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f) or {}
        
        self._parse_config()
        return self._config
    
    def _parse_config(self) -> None:
        """Parse loaded config into validator settings."""
        if not self._config:
            return
        
        rules = self._config.get("rules", [])
        
        for rule in rules:
            rule_id = rule.get("id", "")
            
            if rule_id == "geo-content-style":
                max_words = rule.get("max_words")
                if max_words is not None:
                    self._max_first_paragraph_words = max_words
            
            elif rule_id == "forbidden-words":
                forbidden = rule.get("forbidden", [])
                if forbidden:
                    self._forbidden_words = set(w.lower() for w in forbidden)
    
    def validate(self, content: str, content_type: str = "") -> ValidationResult:
        """Validate content against all configured rules.
        
        Args:
            content: The text content to validate.
            content_type: Optional content type for type-specific checks.
        
        Returns:
            ValidationResult with pass/fail status and details.
        """
        errors: List[str] = []
        warnings: List[str] = []
        checks_run = 0
        
        self._load_config()
        
        result = self._check_first_paragraph(content)
        errors.extend(result["errors"])
        warnings.extend(result["warnings"])
        checks_run += result["checks_run"]
        
        result = self._check_forbidden_words(content)
        errors.extend(result["errors"])
        warnings.extend(result["warnings"])
        checks_run += result["checks_run"]
        
        if content_type:
            result = self._check_data_tables(content, content_type)
            errors.extend(result["errors"])
            warnings.extend(result["warnings"])
            checks_run += result["checks_run"]
        
        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            checks_run=checks_run,
        )
    
    def _get_first_paragraph(self, content: str) -> str:
        """Extract the first paragraph from content."""
        content = content.strip()
        
        paragraphs = re.split(r"\n\s*\n|\r\n\s*\r\n", content)
        
        for para in paragraphs:
            para = para.strip()
            if para and not para.startswith("#") and not para.startswith("<"):
                return para
        
        return ""
    
    def _count_words(self, text: str) -> int:
        """Count words in text, handling HTML and markdown."""
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\[[^\]]+\]\([^)]+\)", " ", text)
        text = re.sub(r"[#*_`~\[\]]", " ", text)
        words = text.split()
        return len(words)
    
    def _check_first_paragraph(self, content: str) -> Dict[str, Any]:
        """Check that first paragraph does not exceed max words."""
        errors: List[str] = []
        warnings: List[str] = []
        checks_run = 1
        
        first_para = self._get_first_paragraph(content)
        
        if not first_para:
            warnings.append("No first paragraph found in content")
            return {"errors": errors, "warnings": warnings, "checks_run": checks_run}
        
        word_count = self._count_words(first_para)
        
        if word_count > self._max_first_paragraph_words:
            errors.append(
                f"First paragraph has {word_count} words, "
                f"exceeds maximum of {self._max_first_paragraph_words}"
            )
        elif word_count > self._max_first_paragraph_words * 0.9:
            warnings.append(
                f"First paragraph has {word_count} words, "
                f"approaching limit of {self._max_first_paragraph_words}"
            )
        
        return {"errors": errors, "warnings": warnings, "checks_run": checks_run}
    
    def _check_forbidden_words(self, content: str) -> Dict[str, Any]:
        """Check for forbidden AI-generated phrases."""
        errors: List[str] = []
        warnings: List[str] = []
        checks_run = 1
        
        content_lower = content.lower()
        found_words: List[str] = []
        
        for word in self._forbidden_words:
            if word.lower() in content_lower:
                found_words.append(word)
        
        if found_words:
            errors.append(
                f"Forbidden words detected: {', '.join(found_words)}. "
                "Use direct, natural language instead."
            )
        
        return {"errors": errors, "warnings": warnings, "checks_run": checks_run}
    
    def _check_data_tables(self, content: str, content_type: str) -> Dict[str, Any]:
        """Check that content requiring tables has them."""
        errors: List[str] = []
        warnings: List[str] = []
        checks_run = 1
        
        if content_type not in CONTENT_TYPES_REQUIRE_TABLE:
            return {"errors": errors, "warnings": warnings, "checks_run": 0}
        
        has_table = bool(self.TABLE_PATTERN.search(content))
        
        if not has_table:
            errors.append(
                f"Content type '{content_type}' requires a data table, "
                "but none was found."
            )
        
        return {"errors": errors, "warnings": warnings, "checks_run": checks_run}
    
    def get_forbidden_words(self) -> Set[str]:
        """Return the current set of forbidden words."""
        self._load_config()
        return self._forbidden_words.copy()
    
    def get_max_first_paragraph_words(self) -> int:
        """Return the maximum allowed words in first paragraph."""
        self._load_config()
        return self._max_first_paragraph_words
