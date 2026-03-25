"""Security Validator.

Detects security issues in code files including hardcoded API keys and secrets.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    passed: bool
    errors: List[str]
    warnings: List[str]
    checks_run: int


@dataclass
class SecurityIssue:
    """Represents a detected security issue."""
    line_number: int
    pattern_name: str
    matched_text: str
    severity: str


class SecurityValidator:
    """Validates files for security issues.
    
    Detects:
    1. Hardcoded API keys
    2. Secrets in code
    3. Sensitive environment variable assignments
    """
    
    API_KEY_PATTERNS: Dict[str, re.Pattern] = {
        "DEEPSEEK_API_KEY": re.compile(
            r'(DEEPSEEK_API_KEY\s*=\s*["\'])(sk-[a-zA-Z0-9]{20,})(["\']?)',
            re.IGNORECASE
        ),
        "ANTHROPIC_API_KEY": re.compile(
            r'(ANTHROPIC_API_KEY\s*=\s*["\'])(sk-ant-[a-zA-Z0-9\-]{20,})(["\']?)',
            re.IGNORECASE
        ),
        "GOOGLE_API_KEY": re.compile(
            r'(GOOGLE_API_KEY\s*=\s*["\'])(AIza[a-zA-Z0-9\-]{35})(["\']?)',
            re.IGNORECASE
        ),
        "GOOGLE_PAGESPEED_API_KEY": re.compile(
            r'(GOOGLE_PAGESPEED_API_KEY\s*=\s*["\'])([a-zA-Z0-9]{20,})(["\']?)',
            re.IGNORECASE
        ),
    }
    
    GENERIC_SECRET_PATTERNS: Dict[str, re.Pattern] = {
        "AWS_ACCESS_KEY": re.compile(
            r'(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])',
        ),
        "AWS_SECRET_KEY": re.compile(
            r'(?:AWS_SECRET_ACCESS_KEY|aws_secret_access_key)\s*=\s*["\']([A-Za-z0-9/+=]{40})["\']',
        ),
        "PRIVATE_KEY": re.compile(
            r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----',
            re.IGNORECASE
        ),
        "GENERIC_API_KEY_ASSIGNMENT": re.compile(
            r'(?:api[_-]?key|apikey|secret[_-]?key)\s*[=:]\s*["\'][a-zA-Z0-9_\-]{16,}["\']',
            re.IGNORECASE
        ),
    }
    
    EXCLUDED_EXTENSIONS: Set[str] = {
        ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg",
        ".woff", ".woff2", ".ttf", ".eot",
        ".mp3", ".mp4", ".wav", ".avi",
        ".zip", ".tar", ".gz", ".rar",
        ".pyc", ".pyo", ".exe", ".dll", ".so",
    }
    
    EXCLUDED_FILES: Set[str] = {
        "package-lock.json",
        "yarn.lock",
        "poetry.lock",
        " Pipfile.lock",
    }
    
    def __init__(self, max_file_size_mb: float = 5.0):
        """Initialize validator with max file size limit."""
        self.max_file_size_bytes = int(max_file_size_mb * 1024 * 1024)
    
    def validate_file(self, path: Path) -> ValidationResult:
        """Validate a single file for security issues.
        
        Args:
            path: Path to the file to validate.
        
        Returns:
            ValidationResult with detected issues.
        """
        errors: List[str] = []
        warnings: List[str] = []
        checks_run = 0
        
        if not path.exists():
            errors.append(f"File does not exist: {path}")
            return ValidationResult(
                passed=False,
                errors=errors,
                warnings=warnings,
                checks_run=checks_run,
            )
        
        if not path.is_file():
            errors.append(f"Path is not a file: {path}")
            return ValidationResult(
                passed=False,
                errors=errors,
                warnings=warnings,
                checks_run=checks_run,
            )
        
        if path.suffix.lower() in self.EXCLUDED_EXTENSIONS:
            return ValidationResult(
                passed=True,
                errors=[],
                warnings=[],
                checks_run=0,
            )
        
        if path.name in self.EXCLUDED_FILES:
            return ValidationResult(
                passed=True,
                errors=[],
                warnings=[],
                checks_run=0,
            )
        
        file_size = path.stat().st_size
        if file_size > self.max_file_size_bytes:
            warnings.append(
                f"File exceeds {self.max_file_size_bytes // (1024*1024)}MB, skipping: {path}"
            )
            return ValidationResult(
                passed=True,
                errors=errors,
                warnings=warnings,
                checks_run=0,
            )
        
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            warnings.append(f"Could not read file {path}: {e}")
            return ValidationResult(
                passed=True,
                errors=errors,
                warnings=warnings,
                checks_run=0,
            )
        
        issues = self._scan_content(content)
        checks_run = len(self.API_KEY_PATTERNS) + len(self.GENERIC_SECRET_PATTERNS)
        
        for issue in issues:
            if issue.severity == "HIGH":
                errors.append(
                    f"Line {issue.line_number}: Hardcoded {issue.pattern_name} detected. "
                    "Use environment variables instead."
                )
            else:
                warnings.append(
                    f"Line {issue.line_number}: Potential {issue.pattern_name} found. "
                    "Please verify this is not a secret."
                )
        
        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            checks_run=checks_run,
        )
    
    def validate_directory(self, directory: Path, recursive: bool = True) -> ValidationResult:
        """Validate all files in a directory.
        
        Args:
            directory: Path to directory to validate.
            recursive: Whether to scan subdirectories.
        
        Returns:
            Combined ValidationResult for all files.
        """
        all_errors: List[str] = []
        all_warnings: List[str] = []
        total_checks = 0
        
        if not directory.exists():
            return ValidationResult(
                passed=False,
                errors=[f"Directory does not exist: {directory}"],
                warnings=[],
                checks_run=0,
            )
        
        if recursive:
            pattern = directory.rglob("*")
        else:
            pattern = directory.glob("*")
        
        for file_path in pattern:
            if not file_path.is_file():
                continue
            
            result = self.validate_file(file_path)
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
            total_checks += result.checks_run
        
        return ValidationResult(
            passed=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings,
            checks_run=total_checks,
        )
    
    def _scan_content(self, content: str) -> List[SecurityIssue]:
        """Scan content for security issues."""
        issues: List[SecurityIssue] = []
        lines = content.split("\n")
        
        for pattern_name, pattern in self.API_KEY_PATTERNS.items():
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count("\n") + 1
                
                matched_text = match.group(0)
                if len(matched_text) > 50:
                    matched_text = matched_text[:47] + "..."
                
                issues.append(SecurityIssue(
                    line_number=line_num,
                    pattern_name=pattern_name,
                    matched_text=matched_text,
                    severity="HIGH",
                ))
        
        for pattern_name, pattern in self.GENERIC_SECRET_PATTERNS.items():
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count("\n") + 1
                
                matched_text = match.group(0)
                if len(matched_text) > 50:
                    matched_text = matched_text[:47] + "..."
                
                issues.append(SecurityIssue(
                    line_number=line_num,
                    pattern_name=pattern_name,
                    matched_text=matched_text,
                    severity="MEDIUM",
                ))
        
        return issues
    
    def scan_string(self, content: str) -> List[SecurityIssue]:
        """Scan a string for security issues without file context.
        
        Args:
            content: String content to scan.
        
        Returns:
            List of SecurityIssue objects found.
        """
        return self._scan_content(content)