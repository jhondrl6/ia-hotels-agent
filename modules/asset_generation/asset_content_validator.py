"""Asset Content Validation - Detect placeholders and generic content."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
import json
import re


class ContentStatus(Enum):
    """Status of content validation."""
    VALID = "valid"
    WARNING = "warning"
    INVALID = "invalid"


@dataclass
class ContentIssue:
    """Single content issue detected."""
    issue_type: str
    field_or_location: str
    detected_value: str
    message: str
    severity: str


@dataclass
class ContentValidationResult:
    """Result of content validation."""
    status: ContentStatus
    issues: List[ContentIssue] = field(default_factory=list)
    word_count: int = 0
    line_count: int = 0
    is_empty: bool = False
    
    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0
    
    @property
    def is_valid(self) -> bool:
        return self.status == ContentStatus.VALID


class AssetContentValidator:
    """Validates content quality of generated assets."""
    
    PLACEHOLDER_PATTERNS = [
        r'Ciudad',
        r'\+57XXX',
        r'\+57\d{10}',
        r'\$\$+',
        r'\.\.\.',
        r'\[INSERT.*\]',
        r'REPLACE_WITH_',
        r'TODO:',
        r'PLACEHOLDER',
        r'Lorem ipsum',
        r'Example:',
        r'Ejemplo:',
    ]
    
    GENERIC_PHRASES = [
        'no configurado',
        'por definir',
        'pendiente',
        'sin especificar',
        'sin configurar',
        'verificar',
        'revisar',
    ]
    
    MIN_CONTENT_LINES = {
        'markdown': 30,
        'json': 5,
        'csv': 3,
        'html': 20,
    }
    
    def __init__(self):
        self.placeholder_regexes = [re.compile(p, re.IGNORECASE) for p in self.PLACEHOLDER_PATTERNS]
    
    def validate_file(self, file_path: str, content: str) -> ContentValidationResult:
        """Validate content based on file type.
        
        Args:
            file_path: Path to the file (used for extension detection)
            content: Content to validate
            
        Returns:
            ContentValidationResult with validation status
        """
        extension = self._get_extension(file_path)
        
        if extension == '.json':
            return self.validate_json(content)
        elif extension in ['.md', '.markdown']:
            return self.validate_markdown(content)
        elif extension == '.csv':
            return self.validate_csv(content)
        elif extension in ['.html', '.htm']:
            return self.validate_html(content)
        else:
            return ContentValidationResult(
                status=ContentStatus.WARNING,
                issues=[ContentIssue(
                    issue_type="unknown_type",
                    field_or_location="file",
                    detected_value=extension,
                    message=f"Unknown file type: {extension}",
                    severity="warning"
                )]
            )
    
    def validate_markdown(self, content: str) -> ContentValidationResult:
        """Validate markdown content for placeholders and generic content.
        
        Args:
            content: Markdown content to validate
            
        Returns:
            ContentValidationResult
        """
        issues = []
        lines = content.strip().split('\n')
        line_count = len(lines)
        
        if line_count < self.MIN_CONTENT_LINES['markdown']:
            issues.append(ContentIssue(
                issue_type="too_short",
                field_or_location="document",
                detected_value=f"{line_count} lines",
                message=f"Content too short: {line_count} lines (minimum: {self.MIN_CONTENT_LINES['markdown']})",
                severity="warning"
            ))
        
        placeholder_issues = self._detect_placeholders(content)
        issues.extend(placeholder_issues)
        
        generic_issues = self._detect_generic_content(content)
        issues.extend(generic_issues)
        
        empty_list_count = self._count_empty_lists(lines)
        if empty_list_count > 0:
            issues.append(ContentIssue(
                issue_type="empty_checklists",
                field_or_location="document",
                detected_value=f"{empty_list_count} empty checklists",
                message=f"Found {empty_list_count} checklists with only headers",
                severity="warning"
            ))
        
        status = self._determine_status(issues)
        
        return ContentValidationResult(
            status=status,
            issues=issues,
            line_count=line_count,
            word_count=len(content.split())
        )
    
    def validate_json(self, content: str) -> ContentValidationResult:
        """Validate JSON content for empty fields.
        
        Args:
            content: JSON content to validate
            
        Returns:
            ContentValidationResult
        """
        issues = []
        
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            return ContentValidationResult(
                status=ContentStatus.INVALID,
                issues=[ContentIssue(
                    issue_type="invalid_json",
                    field_or_location="document",
                    detected_value=str(e),
                    message=f"Invalid JSON: {str(e)}",
                    severity="error"
                )]
            )
        
        empty_fields = self._find_empty_fields(data)
        for field_path, value in empty_fields:
            issues.append(ContentIssue(
                issue_type="empty_field",
                field_or_location=field_path,
                detected_value=str(value),
                message=f"Empty field: {field_path}",
                severity="warning"
            ))
        
        placeholder_issues = self._detect_placeholders(content)
        issues.extend(placeholder_issues)
        
        if not data:
            return ContentValidationResult(
                status=ContentStatus.INVALID,
                issues=issues,
                is_empty=True
            )
        
        status = self._determine_status(issues)
        
        return ContentValidationResult(
            status=status,
            issues=issues,
            line_count=len(content.split('\n')),
            word_count=len(content.split())
        )
    
    def validate_csv(self, content: str) -> ContentValidationResult:
        """Validate CSV content.
        
        Args:
            content: CSV content to validate
            
        Returns:
            ContentValidationResult
        """
        issues = []
        lines = [l.strip() for l in content.strip().split('\n') if l.strip()]
        line_count = len(lines)
        
        if line_count < self.MIN_CONTENT_LINES['csv']:
            issues.append(ContentIssue(
                issue_type="too_short",
                field_or_location="document",
                detected_value=f"{line_count} lines",
                message=f"Content too short: {line_count} lines (minimum: {self.MIN_CONTENT_LINES['csv']})",
                severity="warning"
            ))
        
        if line_count > 0:
            first_line_cols = len(lines[0].split(','))
            for i, line in enumerate(lines[1:], start=2):
                if len(line.split(',')) != first_line_cols:
                    issues.append(ContentIssue(
                        issue_type="inconsistent_columns",
                        field_or_location=f"line {i}",
                        detected_value=line[:50],
                        message=f"Inconsistent column count on line {i}",
                        severity="warning"
                    ))
        
        status = self._determine_status(issues)
        
        return ContentValidationResult(
            status=status,
            issues=issues,
            line_count=line_count
        )
    
    def validate_html(self, content: str) -> ContentValidationResult:
        """Validate HTML content.
        
        Args:
            content: HTML content to validate
            
        Returns:
            ContentValidationResult
        """
        issues = []
        lines = content.strip().split('\n')
        line_count = len(lines)
        
        if line_count < self.MIN_CONTENT_LINES['html']:
            issues.append(ContentIssue(
                issue_type="too_short",
                field_or_location="document",
                detected_value=f"{line_count} lines",
                message=f"Content too short: {line_count} lines (minimum: {self.MIN_CONTENT_LINES['html']})",
                severity="warning"
            ))
        
        placeholder_issues = self._detect_placeholders(content)
        issues.extend(placeholder_issues)
        
        empty_tags = re.findall(r'<(\w+)[^>]*>\s*</\1>', content)
        if empty_tags:
            issues.append(ContentIssue(
                issue_type="empty_tags",
                field_or_location="document",
                detected_value=", ".join(set(empty_tags)),
                message=f"Found empty HTML tags: {', '.join(set(empty_tags))}",
                severity="warning"
            ))
        
        status = self._determine_status(issues)
        
        return ContentValidationResult(
            status=status,
            issues=issues,
            line_count=line_count
        )
    
    def _detect_placeholders(self, content: str) -> List[ContentIssue]:
        """Detect placeholder patterns in content.
        
        Args:
            content: Content to check
            
        Returns:
            List of ContentIssue for placeholders found
        """
        issues = []
        
        for regex in self.placeholder_regexes:
            matches = regex.findall(content)
            if matches:
                issues.append(ContentIssue(
                    issue_type="placeholder",
                    field_or_location="content",
                    detected_value=str(matches[:3]),
                    message=f"Placeholder detected: {regex.pattern}",
                    severity="error"
                ))
        
        for phrase in self.GENERIC_PHRASES:
            if phrase.lower() in content.lower():
                issues.append(ContentIssue(
                    issue_type="generic_phrase",
                    field_or_location="content",
                    detected_value=phrase,
                    message=f"Generic phrase detected: '{phrase}'",
                    severity="warning"
                ))
        
        return issues
    
    def _detect_generic_content(self, content: str) -> List[ContentIssue]:
        """Detect generic/boilerplate content.
        
        Args:
            content: Content to check
            
        Returns:
            List of ContentIssue for generic content
        """
        issues = []
        
        checklist_pattern = re.compile(r'^-\s*\[\s*\]\s+.+$', re.MULTILINE)
        checklists = checklist_pattern.findall(content)
        
        if len(checklists) < 3 and len(content.split('\n')) < 50:
            issues.append(ContentIssue(
                issue_type="generic_checklist",
                field_or_location="document",
                detected_value=f"{len(checklists)} items",
                message="Checklist appears too generic (less than 3 actionable items)",
                severity="warning"
            ))
        
        return issues
    
    def _find_empty_fields(self, data: Any, path: str = "") -> List[tuple]:
        """Recursively find empty fields in nested dict/list.
        
        Args:
            data: Data structure to check
            path: Current path in the structure
            
        Returns:
            List of (field_path, empty_value) tuples
        """
        empty_fields = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                if value == "" or value == []:
                    empty_fields.append((current_path, value))
                elif isinstance(value, (dict, list)):
                    empty_fields.extend(self._find_empty_fields(value, current_path))
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                if item == "" or item == []:
                    empty_fields.append((current_path, item))
                elif isinstance(item, (dict, list)):
                    empty_fields.extend(self._find_empty_fields(item, current_path))
        
        return empty_fields
    
    def _count_empty_lists(self, lines: List[str]) -> int:
        """Count markdown lists that only have headers (no items).
        
        Args:
            lines: Lines of content
            
        Returns:
            Count of empty list sections
        """
        empty_count = 0
        in_list = False
        list_has_item = False
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('- [ ]') or stripped.startswith('- '):
                if not in_list:
                    in_list = True
                    list_has_item = True
                elif stripped != '- [ ]':
                    list_has_item = True
            else:
                if in_list and not list_has_item:
                    empty_count += 1
                in_list = False
                list_has_item = False
        
        return empty_count
    
    def _determine_status(self, issues: List[ContentIssue]) -> ContentStatus:
        """Determine overall status based on issues.
        
        Args:
            issues: List of issues found
            
        Returns:
            ContentStatus
        """
        if not issues:
            return ContentStatus.VALID
        
        has_error = any(i.severity == "error" for i in issues)
        has_warning = any(i.severity == "warning" for i in issues)
        
        if has_error:
            return ContentStatus.INVALID
        elif has_warning:
            return ContentStatus.WARNING
        else:
            return ContentStatus.VALID
    
    def _get_extension(self, file_path: str) -> str:
        """Extract file extension from path.
        
        Args:
            file_path: Path to file
            
        Returns:
            Lowercase extension including dot
        """
        import os
        return os.path.splitext(file_path)[1].lower()
    
    @staticmethod
    def is_placeholder(value: str) -> bool:
        """Check if a value is a placeholder.
        
        Args:
            value: Value to check
            
        Returns:
            True if value appears to be a placeholder
        """
        if not value:
            return True
        
        placeholder_indicators = ['ciudad', '+57xxx', '$$', '...', 'insert', 'replace']
        return any(ind in str(value).lower() for ind in placeholder_indicators)
