"""Skill Router for Agent Harness.

Scans and catalogs available workflow skills from skills/ (root) and .agents/skills/.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class SkillDefinition:
    """Definition of an available skill.
    
    Attributes:
        name: Skill name (e.g., 'truth-protocol').
        slug: Full slug for invocation (e.g., '/truth-protocol').
        path: Absolute path to the workflow file.
        description: Description from YAML frontmatter.
        has_turbo: Whether any step has `// turbo` annotation.
        steps_count: Number of execution steps in the workflow.
    """
    name: str
    slug: str
    path: Path
    description: str = ""
    has_turbo: bool = False
    steps_count: int = 0
    prerequisites: List[str] = field(default_factory=list)
    trigger: str = ""


class SkillRouter:
    """Scans and catalogs workflow skills.
    
    Loads skills from the new official skills/ root directory
    and legacy .agents/skills/.
    """
    
    # New official semantic path (Meta-Architecture Level 3)
    OFFICIAL_SKILLS_PATH = Path(".agents/workflows")
    # Legacy paths (To be deprecated)
    LEGACY_SKILLS_PATH_1 = Path("skills")
    LEGACY_SKILLS_PATH_2 = Path(".agents/skills")
    
    def __init__(self, workflows_path: Optional[Path] = None, verbose: bool = True):
        """Initialize SkillRouter.
        
        Args:
            workflows_path: Custom path to workflows. If None, scans official and legacy.
            verbose: If True, print scanning info.
        """
        self.workflows_path = workflows_path
        self.verbose = verbose
        self._skills: Dict[str, SkillDefinition] = {}
        self._scan_skills()
    
    def _scan_skills(self) -> None:
        """Scan skills directories and build catalog."""
        paths_to_scan = []
        if self.workflows_path:
            paths_to_scan.append(self.workflows_path)
        else:
            paths_to_scan.extend([self.OFFICIAL_SKILLS_PATH, self.LEGACY_SKILLS_PATH_1, self.LEGACY_SKILLS_PATH_2])
        
        for base_path in paths_to_scan:
            if not base_path.exists():
                continue
            
            # 1. Scan for flat .md files
            for file_path in base_path.glob("*.md"):
                if file_path.name.lower() in ("readme.md", "protocolo_automantenimiento.md"):
                    continue
                self._add_skill(file_path)
            
            # 2. Scan for package-style skill.md files (e.g., skills/truth-protocol/skill.md)
            for skill_dir in base_path.iterdir():
                if skill_dir.is_dir():
                    skill_file = skill_dir / "skill.md"
                    if skill_file.exists():
                        self._add_skill(skill_file, name=skill_dir.name)
        
        if self.verbose:
            print(f"[ROUTER] 📚 Loaded {len(set(s.slug for s in self._skills.values()))} skills")

    def _add_skill(self, file_path: Path, name: Optional[str] = None) -> None:
        """Parse and add a skill to the catalog."""
        skill = self._parse_skill_file(file_path, name)
        if skill:
            # Avoid overwriting official skills with legacy ones if names collide
            if skill.slug not in self._skills:
                self._skills[skill.slug] = skill
                self._skills[skill.name] = skill

    def _parse_skill_file(self, file_path: Path, name_override: Optional[str] = None) -> Optional[SkillDefinition]:
        """Parse a workflow markdown file."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except IOError:
            return None
        
        # Extract YAML frontmatter
        description = ""
        frontmatter_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            desc_match = re.search(r"description:\s*(.+)", frontmatter)
            if desc_match:
                description = desc_match.group(1).strip()
        
        # Count steps (### numbered headers)
        steps = re.findall(r"^###\s+\d+\.", content, re.MULTILINE)
        steps_count = len(steps)
        
        # Check for turbo annotation
        has_turbo = "// turbo" in content or "// turbo-all" in content
        
        # Extract prerequisites
        prereqs = []
        prereq_section = re.search(r"## Pre-requisitos?\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL | re.IGNORECASE)
        if prereq_section:
            prereq_items = re.findall(r"- \[[ x]\] (.+)", prereq_section.group(1))
            prereqs = prereq_items
        
        # Build name and slug
        name = name_override or file_path.stem
        slug = f"/{name}"
        
        trigger_text = ""
        trigger_match = re.search(r">\s*\*\*Trigger\*\*:\s*(.+)", content, re.IGNORECASE)
        if trigger_match:
            trigger_text = trigger_match.group(1).strip()
        
        return SkillDefinition(
            name=name,
            slug=slug,
            path=file_path,
            description=description,
            has_turbo=has_turbo,
            steps_count=steps_count,
            prerequisites=prereqs,
            trigger=trigger_text
        )
    
    def list_skills(self) -> List[SkillDefinition]:
        """Get list of all available skills."""
        seen_slugs = set()
        unique_skills = []
        for skill in self._skills.values():
            if skill.slug not in seen_slugs:
                seen_slugs.add(skill.slug)
                unique_skills.append(skill)
        return unique_skills
    
    def get_skill(self, identifier: str) -> Optional[SkillDefinition]:
        """Get a skill by name or slug."""
        if not identifier.startswith("/"):
            identifier_with_slash = f"/{identifier}"
        else:
            identifier_with_slash = identifier
        
        if identifier_with_slash in self._skills:
            return self._skills[identifier_with_slash]
        
        name = identifier.lstrip("/")
        if name in self._skills:
            return self._skills[name]
        
        return None
    
    def skill_exists(self, identifier: str) -> bool:
        """Check if a skill exists."""
        return self.get_skill(identifier) is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """Export skill catalog as dictionary."""
        skills_list = self.list_skills()
        return {
            "count": len(skills_list),
            "skills": [
                {
                    "name": s.name,
                    "slug": s.slug,
                    "description": s.description,
                    "steps": s.steps_count,
                    "has_turbo": s.has_turbo,
                }
                for s in skills_list
            ],
        }
