#!/usr/bin/env python3
"""
Context Integrity Validator for IA Hoteles Agent.

Validates that all references in configuration files are valid:
1. File paths in AGENTS.md (or .cursorrules fallback) exist
2. Skills in error_catalog.json exist in .agents/workflows/
3. Methods in DOMAIN_PRIMER.md exist in actual code
4. Internal references are not broken

Exit codes:
  0 - All validations passed
  1 - One or more validations failed
"""
import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class ValidationResult:
    passed: bool
    check_name: str
    issues: List[str] = field(default_factory=list)
    details: List[str] = field(default_factory=list)


class ContextIntegrityValidator:
    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.results: List[ValidationResult] = []
        
    def log(self, message: str, level: str = "INFO"):
        if self.verbose or level == "ERROR":
            prefix = "  " if level == "DETAIL" else ""
            print(f"{prefix}{message}")
    
    def add_result(self, result: ValidationResult):
        self.results.append(result)
    
    def run_all_validations(self) -> bool:
        print("=" * 60)
        print("CONTEXT INTEGRITY VALIDATOR")
        print("=" * 60)
        print()
        
        self.validate_cursorrules_paths()
        self.validate_error_catalog_skills()
        self.validate_domain_primer_methods()
        self.validate_domain_primer_files()
        self.check_agents_vs_agent_path()
        
        return self.print_report()
    
    def _resolve_context_file(self) -> Optional[Path]:
        candidates = [
            self.project_root / "AGENTS.md",
            self.project_root / ".cursorrules",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

    def validate_cursorrules_paths(self) -> ValidationResult:
        result = ValidationResult(
            passed=True,
            check_name="context_file_paths"
        )

        context_path = self._resolve_context_file()
        if not context_path:
            result.passed = False
            result.issues.append("No context file found (expected AGENTS.md or .cursorrules)")
            self.add_result(result)
            return result

        content = context_path.read_text(encoding="utf-8")
        
        file_patterns = [
            r'data/benchmarks/[^\s\)\]\"]+',
            r'docs/[^\s\)\]\"]+\.md',
            r'\.agent/[^\s\)\]\"]+',
            r'\.agents/[^\s\)\]\"]+',
            r'modules/[^\s\)\]\"]+\.py',
        ]
        
        referenced_files: Set[str] = set()
        
        for pattern in file_patterns:
            matches = re.findall(pattern, content)
            referenced_files.update(matches)
        
        file_url_pattern = r'file:///[^)]+'
        file_urls = re.findall(file_url_pattern, content)
        for url in file_urls:
            local_path = url.replace('file:///', '').replace('/', os.sep)
            referenced_files.add(local_path)
        
        result.details.append(
            f"Found {len(referenced_files)} file references in {context_path.relative_to(self.project_root)}"
        )
        
        for ref in sorted(referenced_files):
            clean_ref = ref.rstrip('.,;:').strip('`')
            
            if 'C:' in clean_ref or 'Users' in clean_ref:
                abs_path = Path(clean_ref)
            else:
                abs_path = self.project_root / clean_ref
            
            if not abs_path.exists():
                result.passed = False
                issue = f"Missing file: {clean_ref}"
                result.issues.append(issue)
                self.log(f"[MISSING] {clean_ref}", "ERROR")
            else:
                self.log(f"[OK] {clean_ref}", "DETAIL")
        
        self.add_result(result)
        return result
    
    def validate_error_catalog_skills(self) -> ValidationResult:
        result = ValidationResult(
            passed=True,
            check_name="error_catalog_skills"
        )
        
        error_catalog_paths = [
            self.project_root / ".agent" / "memory" / "error_catalog.json",
            self.project_root / ".agents" / "memory" / "error_catalog.json",
        ]
        
        error_catalog_path = None
        for path in error_catalog_paths:
            if path.exists():
                error_catalog_path = path
                break
        
        if not error_catalog_path:
            result.passed = False
            result.issues.append("error_catalog.json not found in expected locations")
            self.add_result(result)
            return result
        
        result.details.append(f"Found error_catalog.json at: {error_catalog_path.relative_to(self.project_root)}")
        
        try:
            with open(error_catalog_path, 'r', encoding='utf-8') as f:
                catalog = json.load(f)
        except json.JSONDecodeError as e:
            result.passed = False
            result.issues.append(f"Invalid JSON in error_catalog.json: {e}")
            self.add_result(result)
            return result
        
        skill_patterns = [
            r'/skill_([a-z_]+)',
            r'skill_([a-z_]+)',
        ]
        
        referenced_skills: Set[str] = set()
        
        errors = catalog.get("errors", [])
        for error_entry in errors:
            recovery = error_entry.get("recovery", {})
            message = recovery.get("message", "")
            
            for pattern in skill_patterns:
                matches = re.findall(pattern, message, re.IGNORECASE)
                for match in matches:
                    referenced_skills.add(f"{match}.md")
        
        result.details.append(f"Found {len(referenced_skills)} skill references in error_catalog.json")
        
        workflows_dir = self.project_root / ".agents" / "workflows"
        if not workflows_dir.exists():
            result.passed = False
            result.issues.append(".agents/workflows/ directory not found")
            self.add_result(result)
            return result
        
        existing_skills = set()
        if workflows_dir.exists():
            for f in workflows_dir.glob("*.md"):
                existing_skills.add(f.name)
        
        for skill in sorted(referenced_skills):
            if skill in existing_skills:
                self.log(f"[OK] Skill exists: {skill}", "DETAIL")
            else:
                result.passed = False
                issue = f"Missing skill: {skill}"
                result.issues.append(issue)
                self.log(f"[MISSING] Skill: {skill}", "ERROR")
        
        self.add_result(result)
        return result
    
    def validate_domain_primer_methods(self) -> ValidationResult:
        result = ValidationResult(
            passed=True,
            check_name="domain_primer_methods"
        )
        
        domain_primer_paths = [
            self.project_root / ".agent" / "knowledge" / "DOMAIN_PRIMER.md",
            self.project_root / ".agents" / "knowledge" / "DOMAIN_PRIMER.md",
        ]
        
        domain_primer_path = None
        for path in domain_primer_paths:
            if path.exists():
                domain_primer_path = path
                break
        
        if not domain_primer_path:
            result.passed = False
            result.issues.append("DOMAIN_PRIMER.md not found in expected locations")
            self.add_result(result)
            return result
        
        result.details.append(f"Found DOMAIN_PRIMER.md at: {domain_primer_path.relative_to(self.project_root)}")
        
        content = domain_primer_path.read_text(encoding="utf-8")
        
        method_patterns = [
            r'\b([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)+)\(\)',
            r'`([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)+)\(\)`',
        ]
        
        referenced_methods: Set[str] = set()
        for pattern in method_patterns:
            matches = re.findall(pattern, content)
            referenced_methods.update(matches)
        
        result.details.append(f"Found {len(referenced_methods)} method references in DOMAIN_PRIMER.md")
        
        module_files = {
            'web_scraper': self.project_root / "modules" / "scrapers" / "web_scraper.py",
            'gap_analyzer': self.project_root / "modules" / "analyzers" / "gap_analyzer.py",
            'deployer': self.project_root / "modules" / "deployer" / "manager.py",
            'package_recommender': self.project_root / "modules" / "utils" / "package_recommender.py",
            'orchestration_v4': self.project_root / "modules" / "orchestration_v4" / "onboarding_controller.py",
            'financial_engine': self.project_root / "modules" / "financial_engine" / "scenario_calculator.py",
            'analytics': self.project_root / "modules" / "analytics" / "google_analytics_client.py",
            'geo_enrichment': self.project_root / "modules" / "geo_enrichment" / "geo_flow.py",
            'quality_gates': self.project_root / "modules" / "quality_gates" / "coherence_gate.py",
            'auditors': self.project_root / "modules" / "auditors" / "v4_comprehensive.py",
            'scrapers': self.project_root / "modules" / "scrapers" / "web_scraper.py",
            'commercial_documents': self.project_root / "modules" / "commercial_documents" / "v4_diagnostic_generator.py",
            'delivery': self.project_root / "modules" / "delivery" / "manager.py",
            'providers': self.project_root / "modules" / "providers" / "llm_provider.py",
        }
        
        for method_ref in sorted(referenced_methods):
            if '.' not in method_ref:
                continue
            
            parts = method_ref.split('.')
            
            if len(parts) == 3:
                # modulo.clase.metodo
                module_name, class_name, method_name = parts
            elif len(parts) == 2:
                # modulo.metodo
                module_name, method_name = parts
                class_name = None
            else:
                # Formato no soportado
                continue
            
            module_path = module_files.get(module_name)
            
            if not module_path:
                module_path = self._find_module_file(module_name)
            
            if not module_path or not module_path.exists():
                result.passed = False
                issue = f"Module not found for method: {method_ref}"
                result.issues.append(issue)
                self.log(f"[MISSING] Module for: {method_ref}", "ERROR")
                continue
            
            method_found = self._check_method_exists(module_path, method_name, class_name)
            
            if method_found:
                self.log(f"[OK] Method exists: {method_ref}", "DETAIL")
            else:
                result.passed = False
                issue = f"Method not found: {method_ref} in {module_path.relative_to(self.project_root)}"
                result.issues.append(issue)
                self.log(f"[MISSING] Method: {method_ref}", "ERROR")
        
        self.add_result(result)
        return result
    
    def validate_domain_primer_files(self) -> ValidationResult:
        result = ValidationResult(
            passed=True,
            check_name="domain_primer_file_references"
        )
        
        domain_primer_paths = [
            self.project_root / ".agent" / "knowledge" / "DOMAIN_PRIMER.md",
            self.project_root / ".agents" / "knowledge" / "DOMAIN_PRIMER.md",
        ]
        
        domain_primer_path = None
        for path in domain_primer_paths:
            if path.exists():
                domain_primer_path = path
                break
        
        if not domain_primer_path:
            self.add_result(result)
            return result
        
        content = domain_primer_path.read_text(encoding="utf-8")
        
        file_patterns = [
            r'\[([^\]]+)\]\(\.\./([^\)]+)\)',
            r'\[([^\]]+)\]\((data/[^\)]+)\)',
            r'\[([^\]]+)\]\((docs/[^\)]+)\)',
        ]
        
        referenced_files: Set[str] = set()
        for pattern in file_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    referenced_files.add(match[1])
                else:
                    referenced_files.add(match)
        
        result.details.append(f"Found {len(referenced_files)} file references in DOMAIN_PRIMER.md")
        
        for ref in sorted(referenced_files):
            if ref.startswith('../'):
                clean_ref = ref[3:]
                abs_path = self.project_root / clean_ref
            else:
                abs_path = self.project_root / ref
            
            if not abs_path.exists():
                result.passed = False
                issue = f"Missing file reference: {ref}"
                result.issues.append(issue)
                self.log(f"[MISSING] {ref}", "ERROR")
            else:
                self.log(f"[OK] {ref}", "DETAIL")
        
        self.add_result(result)
        return result
    
    def check_agents_vs_agent_path(self) -> ValidationResult:
        result = ValidationResult(
            passed=True,
            check_name="agents_path_consistency"
        )
        
        context_path = self._resolve_context_file()
        if not context_path:
            self.add_result(result)
            return result

        content = context_path.read_text(encoding="utf-8")
        
        agents_pattern = r'\.agents/workflows'
        agent_pattern = r'\.agent/workflows'
        
        agents_matches = re.findall(agents_pattern, content)
        agent_matches = re.findall(agent_pattern, content)
        
        agents_exists = (self.project_root / ".agents" / "workflows").exists()
        try:
            agent_path = self.project_root / ".agent" / "workflows"
            agent_exists = agent_path.exists()
            # Check if .agent/workflows is a valid symlink to .agents/workflows
            is_valid_symlink = agent_path.is_symlink() and agents_exists
        except OSError:
            agent_exists = True  # Symlink exists but Windows stat fails
            is_valid_symlink = agents_exists  # Assume valid if target exists
            
        result.details.append(f".agents/workflows exists: {agents_exists}")
        result.details.append(f".agent/workflows exists: {agent_exists} (may need elevated access for stat)")
        result.details.append(f"References to .agents/workflows: {len(agents_matches)}")
        result.details.append(f"References to .agent/workflows: {len(agent_matches)}")
        result.details.append(f"Valid symlink .agent/workflows -> .agents/workflows: {is_valid_symlink}")
        
        # Only flag if .agent/workflows references exist but symlink is NOT valid
        if agents_exists and agent_matches and not is_valid_symlink:
            result.passed = False
            issue = "Found .agent/workflows references but .agents/workflows is the active directory"
            result.issues.append(issue)
            self.log(f"[WARN] Path inconsistency: using .agent/workflows but .agents/workflows exists", "ERROR")
        
        if agents_exists and not agents_matches and not agent_matches:
            result.details.append(
                f"No workflow path references found in {context_path.relative_to(self.project_root)}"
            )
        
        self.add_result(result)
        return result
    
    def _find_module_file(self, module_name: str) -> Optional[Path]:
        search_paths = [
            self.project_root / "modules" / f"{module_name}.py",
            self.project_root / "modules" / "scrapers" / f"{module_name}.py",
            self.project_root / "modules" / "analyzers" / f"{module_name}.py",
            self.project_root / "modules" / "utils" / f"{module_name}.py",
            self.project_root / "modules" / "deployer" / f"{module_name}.py",
            self.project_root / "modules" / "delivery" / f"{module_name}.py",
            self.project_root / "modules" / "generators" / f"{module_name}.py",
            self.project_root / "modules" / "orchestrator" / f"{module_name}.py",
            self.project_root / "modules" / "providers" / f"{module_name}.py",
        ]
        
        for path in search_paths:
            if path.exists():
                return path
        
        return None
    
    def _check_method_exists(self, module_path: Path, method_name: str, class_name: str = None) -> bool:
        try:
            content = module_path.read_text(encoding="utf-8")
            
            if class_name:
                # Buscar método dentro de clase específica
                class_pattern = rf'class {class_name}[^:]*:'
                class_match = re.search(class_pattern, content)
                if not class_match:
                    return False
                
                # Extraer contenido de la clase (simplificado)
                class_start = class_match.start()
                next_class = re.search(r'\nclass ', content[class_start+1:])
                if next_class:
                    class_content = content[class_start:class_start+1+next_class.start()]
                else:
                    class_content = content[class_start:]
                
                method_pattern = rf'def {method_name}\s*\('
                return bool(re.search(method_pattern, class_content))
            else:
                # Buscar método global
                patterns = [
                    rf'def {method_name}\s*\(',
                    rf'self\.{method_name}\s*=',
                    rf'@property.*\n.*def {method_name}\s*\(',
                ]
                
                for pattern in patterns:
                    if re.search(pattern, content, re.MULTILINE | re.DOTALL):
                        return True
                
                return False
        except Exception:
            return False
    
    def print_report(self) -> bool:
        print()
        print("=" * 60)
        print("VALIDATION REPORT")
        print("=" * 60)
        
        total_issues = 0
        all_passed = True
        
        for result in self.results:
            status = "PASS" if result.passed else "FAIL"
            status_icon = "OK" if result.passed else "X"
            
            print(f"\n[{status_icon}] {result.check_name}: {status}")
            
            if self.verbose:
                for detail in result.details:
                    print(f"    - {detail}")
            
            if result.issues:
                all_passed = False
                total_issues += len(result.issues)
                for issue in result.issues:
                    print(f"    [!] {issue}")
        
        print()
        print("-" * 60)
        
        if all_passed:
            print("RESULT: All validations passed")
            return True
        else:
            print(f"RESULT: {total_issues} issue(s) found")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Validate context integrity for IA Hoteles Agent"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Project root directory (default: auto-detect)"
    )
    
    args = parser.parse_args()
    
    if args.project_root:
        project_root = args.project_root
    else:
        project_root = Path(__file__).parent.parent.resolve()
    
    validator = ContextIntegrityValidator(
        project_root=project_root,
        verbose=args.verbose
    )
    
    all_passed = validator.run_all_validations()
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
