"""
Asset Metadata Module for IA Hoteles Agent v4.0

This module enforces metadata requirements on all generated assets.
Provides standardized metadata tracking for traceability and compliance.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json
import re

from ..data_validation.confidence_taxonomy import ConfidenceLevel


class AssetStatus(Enum):
    """Status of an asset in the generation pipeline.
    
    FASE-CAUSAL-01: Agregados SKIPPED y REDUNDANT para manejar
    casos donde el asset ya existe en sitio de producción.
    """
    PENDING = "pending"
    GENERATED = "generated"
    VALIDATED = "validated"
    FAILED = "failed"
    DEPRECATED = "deprecated"
    # FASE-CAUSAL-01: Estados de skip por presencia
    SKIPPED = "skipped"           # Asset skippeado por no necesitarse
    REDUNDANT = "redundant"       # Asset ya existe en sitio y fue entregado


@dataclass
class AssetMetadata:
    """
    Standardized metadata for all generated assets.
    
    Tracks generation details, confidence levels, validation sources,
    and usage permissions for complete asset traceability.
    """
    asset_name: str = ""
    asset_type: str = ""
    generated_at: datetime = field(default_factory=datetime.now)
    confidence_level: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    confidence_score: float = 0.0  # 0.0 - 1.0
    validation_sources: List[str] = field(default_factory=list)  # ["web_scraping", "gbp_api", "user_input"]
    preflight_status: str = ""  # "PASSED", "WARNING", "BLOCKED"
    can_use: bool = False
    disclaimer: Optional[str] = None
    generated_by: str = "IAH_v4.0"
    version: str = "4.0.0"
    # Additional fields for conditional generator
    hotel_id: str = ""
    hotel_name: str = ""
    status: AssetStatus = AssetStatus.PENDING
    source_data_hash: str = ""
    fallback_used: bool = False
    fallback_reason: Optional[str] = None
    disclaimers: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    # FASE 9: Intelligent Disclaimer Generator v2 fields
    missing_data: List[str] = field(default_factory=list)
    benchmark_used: Optional[str] = None
    improvement_steps: List[str] = field(default_factory=list)
    confidence_after_fix: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for serialization."""
        result = {
            "asset_name": self.asset_name,
            "asset_type": self.asset_type,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "confidence_level": self.confidence_level.value if self.confidence_level else None,
            "confidence_score": self.confidence_score,
            "validation_sources": self.validation_sources,
            "preflight_status": self.preflight_status,
            "can_use": self.can_use,
            "disclaimer": self.disclaimer,
            "generated_by": self.generated_by,
            "version": self.version,
            "hotel_id": self.hotel_id,
            "hotel_name": self.hotel_name,
            "status": self.status.value if self.status else None,
            "source_data_hash": self.source_data_hash,
            "fallback_used": self.fallback_used,
            "fallback_reason": self.fallback_reason,
            "disclaimers": self.disclaimers,
            "tags": self.tags,
            # FASE 9: Intelligent Disclaimer Generator v2
            "missing_data": self.missing_data,
            "benchmark_used": self.benchmark_used,
            "improvement_steps": self.improvement_steps,
            "confidence_after_fix": self.confidence_after_fix,
        }
        return result


class AssetMetadataEnforcer:
    """
    Enforces metadata requirements on all generated assets.
    
    Provides methods for creating, validating, injecting, and extracting
    metadata from assets in various formats (HTML, JSON, CSV, Markdown).
    """

    REQUIRED_FIELDS = [
        "asset_name",
        "asset_type",
        "generated_at",
        "confidence_level",
        "confidence_score",
        "validation_sources",
        "preflight_status",
        "can_use"
    ]

    VALID_PREFLIGHT_STATUSES = ["PASSED", "WARNING", "BLOCKED", "SKIPPED"]  # SKIPPED = FASE-CAUSAL-01
    VALID_ASSET_TYPES = ["html", "json", "csv", "markdown", "txt", "xml", "yaml"]

    def __init__(self):
        """Initialize the metadata enforcer."""
        self._validation_errors: List[str] = []

    def _generate_disclaimer(self, confidence_level: ConfidenceLevel, 
                            confidence_score: float,
                            validation_sources: List[str]) -> Optional[str]:
        """
        Generate appropriate disclaimer based on confidence level.
        
        Args:
            confidence_level: The confidence level of the asset
            confidence_score: Numerical confidence score (0.0 - 1.0)
            validation_sources: List of validation source types
            
        Returns:
            Disclaimer string or None if not needed
        """
        if confidence_level == ConfidenceLevel.VERIFIED and confidence_score >= 0.9:
            return None
        elif confidence_level == ConfidenceLevel.CONFLICT:
            return "⚠️ Este activo contiene conflictos de datos. Requiere revisión manual antes de usar."
        elif confidence_level == ConfidenceLevel.UNKNOWN:
            return "⚠️ Datos insuficientes. Este activo no debe usarse sin verificación adicional."
        elif confidence_score < 0.7:
            return f"⚠️ Confianza baja ({confidence_score:.0%}). Validar antes de publicar."
        else:
            sources_str = ", ".join(validation_sources) if validation_sources else "fuente única"
            return f"ℹ️ Basado en: {sources_str}. Recomendado: verificación adicional."

    def _calculate_can_use(self, confidence_level: ConfidenceLevel, 
                          confidence_score: float,
                          preflight_status: str) -> bool:
        """
        Determine if asset can be used based on confidence and preflight status.
        
        Args:
            confidence_level: The confidence level
            confidence_score: Numerical score (0.0 - 1.0)
            preflight_status: Preflight check status
            
        Returns:
            True if asset can be used, False otherwise
        """
        if preflight_status == "BLOCKED":
            return False
        if confidence_level == ConfidenceLevel.CONFLICT:
            return False
        if confidence_level == ConfidenceLevel.UNKNOWN:
            return False
        if confidence_score < 0.5:
            return False
        return True

    def create_metadata(
        self,
        asset_name: str = "",
        asset_type: str = "",
        confidence_level: ConfidenceLevel = ConfidenceLevel.UNKNOWN,
        confidence_score: float = 0.0,
        validation_sources: List[str] = None,
        preflight_status: str = "WARNING",
        sources: List[str] = None,
        gaps: List[str] = None,
        **kwargs
    ) -> AssetMetadata:
        """
        Create a metadata object for an asset.
        
        Args:
            asset_name: Name of the asset
            asset_type: Type of asset (html, json, csv, markdown, etc.)
            confidence_level: Confidence level from validation
            confidence_score: Numerical confidence (0.0 - 1.0)
            validation_sources: List of source types used for validation
            preflight_status: Result of preflight checks (PASSED, WARNING, BLOCKED)
            sources: Alias for validation_sources (for backward compatibility)
            gaps: List of data gaps for the disclaimer
            **kwargs: Additional arguments for backward compatibility
            
        Returns:
            AssetMetadata instance with calculated fields
        """
        # Handle aliases and backward compatibility
        if sources is not None and validation_sources is None:
            validation_sources = sources
        if validation_sources is None:
            validation_sources = []
        
        # Convert enum to string if needed
        if hasattr(preflight_status, 'value'):
            preflight_status = preflight_status.value
        
        # Normalize to uppercase for validation
        preflight_status_upper = preflight_status.upper() if preflight_status else ""
        
        # Validate preflight status
        if preflight_status_upper not in [s.upper() for s in self.VALID_PREFLIGHT_STATUSES]:
            raise ValueError(
                f"Invalid preflight_status: {preflight_status}. "
                f"Must be one of: {self.VALID_PREFLIGHT_STATUSES}"
            )

        # Determine if asset can be used
        can_use = self._calculate_can_use(
            confidence_level, confidence_score, preflight_status_upper
        )

        # Generate disclaimer if needed
        disclaimer = self._generate_disclaimer(
            confidence_level, confidence_score, validation_sources
        )

        return AssetMetadata(
            asset_name=asset_name,
            asset_type=asset_type.lower() if asset_type else "",
            generated_at=datetime.now(),
            confidence_level=confidence_level,
            confidence_score=confidence_score,
            validation_sources=validation_sources,
            preflight_status=preflight_status_upper,
            can_use=can_use,
            disclaimer=disclaimer,
            generated_by="IAH_v4.0",
            version="4.0.0",
            disclaimers=[f"Data gaps: {', '.join(gaps)}"] if gaps else []
        )

    def validate_metadata(self, metadata: AssetMetadata) -> bool:
        """
        Validate that metadata meets all requirements.
        
        Args:
            metadata: AssetMetadata instance to validate
            
        Returns:
            True if valid, False otherwise
        """
        self._validation_errors = []
        
        # Check all required fields are present and not None
        for field_name in self.REQUIRED_FIELDS:
            value = getattr(metadata, field_name, None)
            if value is None:
                self._validation_errors.append(f"Missing required field: {field_name}")

        # Validate confidence_score range
        if metadata.confidence_score is not None:
            if not 0.0 <= metadata.confidence_score <= 1.0:
                self._validation_errors.append(
                    f"confidence_score must be between 0.0 and 1.0, got {metadata.confidence_score}"
                )

        # Validate generated_at is datetime
        if metadata.generated_at is not None:
            if not isinstance(metadata.generated_at, datetime):
                self._validation_errors.append(
                    f"generated_at must be datetime, got {type(metadata.generated_at)}"
                )

        # Validate confidence_level is valid enum
        if metadata.confidence_level is not None:
            if not isinstance(metadata.confidence_level, ConfidenceLevel):
                self._validation_errors.append(
                    f"confidence_level must be ConfidenceLevel enum, got {type(metadata.confidence_level)}"
                )

        # Validate preflight_status
        if metadata.preflight_status is not None:
            if metadata.preflight_status not in self.VALID_PREFLIGHT_STATUSES:
                self._validation_errors.append(
                    f"preflight_status must be one of {self.VALID_PREFLIGHT_STATUSES}, "
                    f"got {metadata.preflight_status}"
                )

        # Validate validation_sources is a list
        if metadata.validation_sources is not None:
            if not isinstance(metadata.validation_sources, list):
                self._validation_errors.append(
                    f"validation_sources must be a list, got {type(metadata.validation_sources)}"
                )

        return len(self._validation_errors) == 0

    def get_validation_errors(self) -> List[str]:
        """Get list of validation errors from last validation."""
        return self._validation_errors.copy()

    def inject_metadata_into_asset(
        self,
        content: str,
        metadata: AssetMetadata,
        asset_type: str
    ) -> str:
        """
        Inject metadata into asset content based on asset type.
        
        Args:
            content: Original asset content
            metadata: AssetMetadata to inject
            asset_type: Type of asset (html, json, csv, markdown)
            
        Returns:
            Content with metadata injected
        """
        asset_type_lower = asset_type.lower()

        if asset_type_lower == "html":
            return self._inject_into_html(content, metadata)
        elif asset_type_lower == "json":
            return self._inject_into_json(content, metadata)
        elif asset_type_lower == "csv":
            return self._inject_into_csv(content, metadata)
        elif asset_type_lower == "markdown":
            return self._inject_into_markdown(content, metadata)
        elif asset_type_lower in ["txt", "xml", "yaml"]:
            return self._inject_as_comment(content, metadata, asset_type_lower)
        else:
            # Default to comment injection
            return self._inject_as_comment(content, metadata, "txt")

    def _metadata_to_dict(self, metadata: AssetMetadata) -> Dict[str, Any]:
        """Convert metadata to dictionary for serialization."""
        return {
            "asset_name": metadata.asset_name,
            "asset_type": metadata.asset_type,
            "generated_at": metadata.generated_at.isoformat(),
            "confidence_level": metadata.confidence_level.value,
            "confidence_score": metadata.confidence_score,
            "validation_sources": metadata.validation_sources,
            "preflight_status": metadata.preflight_status,
            "can_use": metadata.can_use,
            "disclaimer": metadata.disclaimer,
            "generated_by": metadata.generated_by,
            "version": metadata.version
        }

    def _inject_into_html(self, content: str, metadata: AssetMetadata) -> str:
        """Inject metadata as HTML comment before content."""
        meta_dict = self._metadata_to_dict(metadata)
        meta_lines = [f"<!-- IAH_METADATA_START"]
        for key, value in meta_dict.items():
            meta_lines.append(f"  {key}: {value}")
        meta_lines.append("IAH_METADATA_END -->")
        
        metadata_comment = "\n".join(meta_lines)
        return f"{metadata_comment}\n{content}"

    def _inject_into_json(self, content: str, metadata: AssetMetadata) -> str:
        """Inject metadata as _metadata field in JSON object."""
        try:
            data = json.loads(content)
            if isinstance(data, dict):
                data["_metadata"] = self._metadata_to_dict(metadata)
                return json.dumps(data, indent=2, ensure_ascii=False)
            else:
                # Wrap in object with metadata
                wrapped = {
                    "_metadata": self._metadata_to_dict(metadata),
                    "data": data
                }
                return json.dumps(wrapped, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            # If content is not valid JSON, return with metadata prepended as comment
            return self._inject_as_comment(content, metadata, "json")

    def _inject_into_csv(self, content: str, metadata: AssetMetadata) -> str:
        """Inject metadata as first comment row in CSV."""
        meta_dict = self._metadata_to_dict(metadata)
        # Create JSON comment for CSV
        meta_json = json.dumps(meta_dict, ensure_ascii=False)
        csv_comment = f"# {meta_json}\n"
        return csv_comment + content

    def _inject_into_markdown(self, content: str, metadata: AssetMetadata) -> str:
        """Inject metadata as YAML frontmatter in Markdown."""
        meta_dict = self._metadata_to_dict(metadata)
        frontmatter_lines = ["---"]
        for key, value in meta_dict.items():
            if value is None:
                frontmatter_lines.append(f"{key}:")
            elif isinstance(value, list):
                frontmatter_lines.append(f"{key}:")
                for item in value:
                    frontmatter_lines.append(f"  - {item}")
            elif isinstance(value, bool):
                frontmatter_lines.append(f"{key}: {str(value).lower()}")
            elif isinstance(value, float):
                frontmatter_lines.append(f"{key}: {value}")
            else:
                frontmatter_lines.append(f'{key}: "{value}"')
        frontmatter_lines.append("---")
        
        frontmatter = "\n".join(frontmatter_lines)
        return f"{frontmatter}\n\n{content}"

    def _inject_as_comment(self, content: str, metadata: AssetMetadata, 
                          asset_type: str) -> str:
        """Inject metadata as generic comment block."""
        meta_dict = self._metadata_to_dict(metadata)
        meta_json = json.dumps(meta_dict, indent=2, ensure_ascii=False)
        
        comment_styles = {
            "txt": f"""<!--
IAH Asset Metadata
==================
{meta_json}
-->
""",
            "xml": f"""<!--
IAH Asset Metadata
==================
{meta_json}
-->
""",
            "yaml": f"""# IAH Asset Metadata
# ==================
# {meta_json.replace(chr(10), chr(10)+'# ')}
""",
            "json": f"""// IAH Asset Metadata
// ==================
// {meta_json.replace(chr(10), chr(10)+'// ')}
"""
        }
        
        comment = comment_styles.get(asset_type, comment_styles["txt"])
        return comment + content

    def extract_metadata_from_asset(
        self,
        content: str,
        asset_type: str
    ) -> Optional[AssetMetadata]:
        """
        Parse metadata from asset content.
        
        Args:
            content: Asset content with embedded metadata
            asset_type: Type of asset (html, json, csv, markdown)
            
        Returns:
            AssetMetadata instance or None if not found/invalid
        """
        asset_type_lower = asset_type.lower()

        try:
            if asset_type_lower == "html":
                return self._extract_from_html(content)
            elif asset_type_lower == "json":
                return self._extract_from_json(content)
            elif asset_type_lower == "csv":
                return self._extract_from_csv(content)
            elif asset_type_lower == "markdown":
                return self._extract_from_markdown(content)
            else:
                return self._extract_from_comment(content, asset_type_lower)
        except Exception:
            return None

    def _dict_to_metadata(self, data: Dict[str, Any]) -> Optional[AssetMetadata]:
        """Convert dictionary to AssetMetadata."""
        try:
            # Parse datetime
            generated_at = data.get("generated_at")
            if isinstance(generated_at, str):
                # Handle ISO format with or without timezone
                generated_at = generated_at.replace('Z', '+00:00')
                try:
                    generated_at = datetime.fromisoformat(generated_at)
                except ValueError:
                    generated_at = datetime.now()
            elif not isinstance(generated_at, datetime):
                generated_at = datetime.now()

            # Parse confidence level - handle both enum value and string
            confidence_level_str = data.get("confidence_level", "unknown")
            if isinstance(confidence_level_str, str):
                try:
                    confidence_level = ConfidenceLevel(confidence_level_str.lower())
                except ValueError:
                    confidence_level = ConfidenceLevel.UNKNOWN
            else:
                confidence_level = ConfidenceLevel.UNKNOWN
            
            # Parse AssetStatus if present
            status_str = data.get("status")
            status = AssetStatus.PENDING
            if isinstance(status_str, str):
                try:
                    status = AssetStatus(status_str)
                except ValueError:
                    status = AssetStatus.PENDING

            return AssetMetadata(
                asset_name=data.get("asset_name", ""),
                asset_type=data.get("asset_type", ""),
                generated_at=generated_at,
                confidence_level=confidence_level,
                confidence_score=data.get("confidence_score", 0.0),
                validation_sources=data.get("validation_sources", []),
                preflight_status=data.get("preflight_status", ""),
                can_use=data.get("can_use", False),
                disclaimer=data.get("disclaimer"),
                generated_by=data.get("generated_by", "IAH_v4.0"),
                version=data.get("version", "4.0.0"),
                hotel_id=data.get("hotel_id", ""),
                hotel_name=data.get("hotel_name", ""),
                status=status,
                source_data_hash=data.get("source_data_hash", ""),
                fallback_used=data.get("fallback_used", False),
                fallback_reason=data.get("fallback_reason"),
                disclaimers=data.get("disclaimers", []),
                tags=data.get("tags", [])
            )
        except Exception:
            return None

    def _extract_from_html(self, content: str) -> Optional[AssetMetadata]:
        """Extract metadata from HTML comment."""
        pattern = r"<!-- IAH_METADATA_START(.*?)IAH_METADATA_END -->"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            meta_text = match.group(1).strip()
            # Parse key-value pairs
            data = {}
            for line in meta_text.split("\n"):
                line = line.strip()
                if ": " in line:
                    key, value = line.split(": ", 1)
                    # Try to parse values
                    if value == "None":
                        data[key] = None
                    elif value == "True":
                        data[key] = True
                    elif value == "False":
                        data[key] = False
                    elif value.startswith("[") and value.endswith("]"):
                        # Parse list
                        data[key] = [v.strip().strip('"').strip("'") 
                                    for v in value[1:-1].split(",") if v.strip()]
                    else:
                        data[key] = value
            return self._dict_to_metadata(data)
        return None

    def _extract_from_json(self, content: str) -> Optional[AssetMetadata]:
        """Extract metadata from JSON _metadata field."""
        try:
            data = json.loads(content)
            if isinstance(data, dict) and "_metadata" in data:
                return self._dict_to_metadata(data["_metadata"])
        except json.JSONDecodeError:
            pass
        return None

    def _extract_from_csv(self, content: str) -> Optional[AssetMetadata]:
        """Extract metadata from CSV comment row."""
        lines = content.split("\n")
        if lines and lines[0].startswith("#"):
            meta_json = lines[0][1:].strip()
            try:
                data = json.loads(meta_json)
                return self._dict_to_metadata(data)
            except json.JSONDecodeError:
                pass
        return None

    def _extract_from_markdown(self, content: str) -> Optional[AssetMetadata]:
        """Extract metadata from Markdown YAML frontmatter."""
        if content.startswith("---"):
            end_pos = content.find("---", 3)
            if end_pos != -1:
                frontmatter = content[3:end_pos].strip()
                data = {}
                current_key = None
                lines = frontmatter.split("\n")
                for i, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("-"):
                        # List item
                        if current_key:
                            if current_key not in data or data[current_key] is None:
                                data[current_key] = []
                            data[current_key].append(line[1:].strip())
                    elif ":" in line:
                        # Handle both "key: value" and "key:" (empty value)
                        if ": " in line:
                            key, value = line.split(": ", 1)
                        else:
                            key = line.rstrip(":")
                            value = ""
                        current_key = key
                        
                        # Check if next non-empty line is a list item
                        next_is_list = False
                        for j in range(i + 1, len(lines)):
                            next_line = lines[j].strip()
                            if not next_line:
                                continue
                            if next_line.startswith("-"):
                                next_is_list = True
                            break
                        
                        if next_is_list:
                            data[key] = []  # Will be populated by list items
                        elif value.startswith('"') and value.endswith('"'):
                            data[key] = value[1:-1]
                        elif value == "":
                            data[key] = None
                        elif value == "true":
                            data[key] = True
                        elif value == "false":
                            data[key] = False
                        else:
                            try:
                                data[key] = float(value)
                            except ValueError:
                                data[key] = value
                return self._dict_to_metadata(data)
        return None

    def _extract_from_comment(self, content: str, asset_type: str) -> Optional[AssetMetadata]:
        """Extract metadata from generic comment block."""
        patterns = {
            "txt": r"<!--\s*IAH Asset Metadata.*?({.*?})\s*-->",
            "xml": r"<!--\s*IAH Asset Metadata.*?({.*?})\s*-->",
            "yaml": r"# IAH Asset Metadata.*?\n#\s*({.*?})",
            "json": r"// IAH Asset Metadata.*?\n//\s*({.*?})"
        }
        
        pattern = patterns.get(asset_type, patterns["txt"])
        match = re.search(pattern, content, re.DOTALL)
        if match:
            try:
                meta_json = match.group(1).replace("\n# ", "").replace("\n// ", "")
                data = json.loads(meta_json)
                return self._dict_to_metadata(data)
            except (json.JSONDecodeError, IndexError):
                pass
        return None

    @staticmethod
    def format_metadata_for_report(metadata: AssetMetadata) -> str:
        """
        Format metadata as readable text for reports.
        
        Args:
            metadata: AssetMetadata to format
            
        Returns:
            Formatted string with confidence icon, sources, disclaimer
        """
        confidence_icons = {
            ConfidenceLevel.VERIFIED: "✅",
            ConfidenceLevel.ESTIMATED: "⚡",
            ConfidenceLevel.CONFLICT: "⚠️",
            ConfidenceLevel.UNKNOWN: "❓"
        }
        
        icon = confidence_icons.get(metadata.confidence_level, "❓")
        status_icons = {
            "PASSED": "✓",
            "WARNING": "⚠",
            "BLOCKED": "✗"
        }
        status_icon = status_icons.get(metadata.preflight_status, "?")
        
        lines = [
            f"{icon} {metadata.asset_name} ({metadata.asset_type})",
            f"   Confianza: {metadata.confidence_level.value} ({metadata.confidence_score:.0%})",
            f"   Fuentes: {', '.join(metadata.validation_sources)}",
            f"   Preflight: {status_icon} {metadata.preflight_status}",
            f"   Usable: {'Sí' if metadata.can_use else 'No'}",
        ]
        
        if metadata.disclaimer:
            lines.append(f"   Nota: {metadata.disclaimer}")
        
        lines.append(f"   Generado: {metadata.generated_at.strftime('%Y-%m-%d %H:%M')}")
        
        return "\n".join(lines)

    def tag_as_estimated(self, metadata: AssetMetadata, reason: str) -> None:
        """Tag metadata as estimated with given reason.
        
        Args:
            metadata: AssetMetadata to tag
            reason: Reason for estimated status
        """
        metadata.status = AssetStatus.GENERATED
        metadata.confidence_level = ConfidenceLevel.ESTIMATED
        metadata.fallback_used = True
        metadata.fallback_reason = reason
        if reason not in metadata.disclaimers:
            metadata.disclaimers.append(reason)

    @staticmethod
    def check_asset_usability(metadata: AssetMetadata) -> Dict[str, Any]:
        """
        Check if asset can be used and return detailed status.
        
        Args:
            metadata: AssetMetadata to check
            
        Returns:
            Dictionary with usable status, reason, and warnings
        """
        result = {
            "usable": metadata.can_use,
            "reason": "",
            "warnings": []
        }
        
        if metadata.can_use:
            result["reason"] = "Activo validado y listo para uso"
            
            if metadata.confidence_level == ConfidenceLevel.ESTIMATED:
                result["warnings"].append("Datos estimados - considerar verificación adicional")
            
            if metadata.preflight_status == "WARNING":
                result["warnings"].append("Advertencias en preflight checks")
                
            if metadata.confidence_score < 0.8:
                result["warnings"].append(f"Confianza moderada ({metadata.confidence_score:.0%})")
        else:
            if metadata.preflight_status == "BLOCKED":
                result["reason"] = "Bloqueado por errores en preflight checks"
            elif metadata.confidence_level == ConfidenceLevel.CONFLICT:
                result["reason"] = "Conflicto de datos detectado - requiere resolución manual"
            elif metadata.confidence_level == ConfidenceLevel.UNKNOWN:
                result["reason"] = "Datos insuficientes para usar el activo"
            elif metadata.confidence_score < 0.5:
                result["reason"] = f"Confianza muy baja ({metadata.confidence_score:.0%})"
            else:
                result["reason"] = "Activo no usable por razones de validación"
        
        return result
