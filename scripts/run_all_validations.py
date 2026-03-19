#!/usr/bin/env python3
"""
IA Hoteles Agent - Run All Validations
======================================
Orchestrates all validation checks without Gemini CLI dependency.

Usage:
    python scripts/run_all_validations.py          # Run all validations
    python scripts/run_all_validations.py --check  # Check mode (no fixes)
    python scripts/run_all_validations.py --quick  # Quick mode (essential only)
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).parent.parent


class ValidationResult:
    """Result of a single validation."""
    
    def __init__(self, name: str, passed: bool, message: str = "", details: list = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details or []
    
    def __str__(self):
        status = "[PASS]" if self.passed else "[FAIL]"
        return f"{status} {self.name}: {self.message}"


class ValidationRunner:
    """Runs all validation checks."""
    
    def __init__(self, check_only: bool = False, quick: bool = False, verbose: bool = True):
        self.check_only = check_only
        self.quick = quick
        self.verbose = verbose
        self.results: list = []
    
    def run_all(self) -> bool:
        """Run all validations and return overall success."""
        print("=" * 60)
        print(f"IA HOTELES AGENT - VALIDATION ENGINE")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Mode: {'CHECK ONLY' if self.check_only else 'FULL'}")
        print("=" * 60)
        print()
        
        self._check_residual_files()
        self._check_plan_maestro_sync()
        self._check_version_sync()
        self._check_no_secrets()
        
        if not self.quick:
            self._check_dependencies()
            self._check_imports()
            self._check_tests_pass()
        
        return self._print_summary()
    
    def _run_command(self, cmd: list, capture: bool = True) -> tuple:
        """Run a command and return exit code + output."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture,
                text=True,
                cwd=ROOT_DIR
            )
            return result.returncode, result.stdout + result.stderr
        except Exception as e:
            return 1, str(e)
    
    def _check_residual_files(self) -> None:
        """Check for residual/backup files."""
        print("[1/7] Checking for residual files...")
        
        residual_extensions = {".bak", ".backup", ".tmp", ".old"}
        residual_files = []
        
        for path in ROOT_DIR.rglob("*"):
            if path.is_dir():
                continue
            if path.suffix in residual_extensions:
                residual_files.append(path.relative_to(ROOT_DIR))
            if ".backup" in path.name:
                residual_files.append(path.relative_to(ROOT_DIR))
        
        if residual_files:
            self.results.append(ValidationResult(
                name="Residual Files",
                passed=False,
                message=f"Found {len(residual_files)} residual files",
                details=[str(f) for f in residual_files[:10]]
            ))
        else:
            self.results.append(ValidationResult(
                name="Residual Files",
                passed=True,
                message="No residual files found"
            ))
    
    def _check_plan_maestro_sync(self) -> None:
        """Check if Plan Maestro data is synchronized."""
        print("[2/7] Checking Plan Maestro sync...")
        
        json_path = ROOT_DIR / "data" / "benchmarks" / "plan_maestro_data.json"
        md_path = ROOT_DIR / "data" / "benchmarks" / "Plan_maestro_v2_5.md"
        
        if not json_path.exists():
            self.results.append(ValidationResult(
                name="Plan Maestro Sync",
                passed=False,
                message="plan_maestro_data.json not found"
            ))
            return
        
        if not md_path.exists():
            self.results.append(ValidationResult(
                name="Plan Maestro Sync",
                passed=False,
                message="Plan_maestro_v2_5.md not found"
            ))
            return
        
        import json
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            version = data.get("version", "unknown")
            self.results.append(ValidationResult(
                name="Plan Maestro Sync",
                passed=True,
                message=f"Plan Maestro v{version} loaded correctly"
            ))
        except Exception as e:
            self.results.append(ValidationResult(
                name="Plan Maestro Sync",
                passed=False,
                message=f"Error reading plan_maestro_data.json: {e}"
            ))
    
    def _check_version_sync(self) -> None:
        """Check if versions are synchronized across files."""
        print("[3/7] Checking version synchronization...")
        
        version_file = ROOT_DIR / "VERSION.yaml"
        if not version_file.exists():
            self.results.append(ValidationResult(
                name="Version Sync",
                passed=False,
                message="VERSION.yaml not found"
            ))
            return
        
        sync_script = ROOT_DIR / "scripts" / "sync_versions.py"
        if not sync_script.exists():
            self.results.append(ValidationResult(
                name="Version Sync",
                passed=True,
                message="sync_versions.py not found, skipping"
            ))
            return
        
        exit_code, output = self._run_command([
            sys.executable,
            str(sync_script),
            "--check"
        ])
        
        if exit_code == 0:
            self.results.append(ValidationResult(
                name="Version Sync",
                passed=True,
                message="All versions synchronized"
            ))
        else:
            self.results.append(ValidationResult(
                name="Version Sync",
                passed=False,
                message="Versions out of sync",
                details=[line for line in output.split("\n") if "FAIL" in line or "needs update" in line]
            ))
    
    def _check_no_secrets(self) -> None:
        """Check for hardcoded secrets."""
        print("[4/7] Checking for hardcoded secrets...")
        
        import re
        secret_patterns = [
            r'DEEPSEEK_API_KEY\s*=\s*["\'][^"\']+["\']',
            r'ANTHROPIC_API_KEY\s*=\s*["\'][^"\']+["\']',
            r'GOOGLE_API_KEY\s*=\s*["\'][^"\']+["\']',
            r'GOOGLEMAPS_API_KEY\s*=\s*["\'][^"\']+["\']',
        ]
        
        violations = []
        for py_file in ROOT_DIR.rglob("*.py"):
            if "test" in str(py_file).lower():
                continue
            try:
                content = py_file.read_text(encoding="utf-8")
                for pattern in secret_patterns:
                    if re.search(pattern, content):
                        violations.append(str(py_file.relative_to(ROOT_DIR)))
                        break
            except Exception:
                continue
        
        if violations:
            self.results.append(ValidationResult(
                name="Secrets Check",
                passed=False,
                message=f"Found potential hardcoded secrets in {len(violations)} files",
                details=violations[:5]
            ))
        else:
            self.results.append(ValidationResult(
                name="Secrets Check",
                passed=True,
                message="No hardcoded secrets found"
            ))
    
    def _check_dependencies(self) -> None:
        """Check if all dependencies are installed."""
        print("[5/7] Checking dependencies...")
        
        exit_code, output = self._run_command([
            sys.executable, "-m", "pip", "check"
        ])
        
        if exit_code == 0:
            self.results.append(ValidationResult(
                name="Dependencies",
                passed=True,
                message="All dependencies satisfied"
            ))
        else:
            self.results.append(ValidationResult(
                name="Dependencies",
                passed=False,
                message="Dependency conflicts detected",
                details=[line for line in output.split("\n") if line.strip()][:5]
            ))
    
    def _check_imports(self) -> None:
        """Check if core modules can be imported."""
        print("[6/7] Checking core module imports...")
        
        core_modules = [
            "src.config",
            "src.tools",
            "src.utils",
        ]
        
        import_errors = []
        for module in core_modules:
            module_path = ROOT_DIR / module.replace(".", "/")
            if not module_path.exists() and not (module_path.with_suffix(".py")).exists():
                continue
            try:
                __import__(module)
            except ImportError as e:
                import_errors.append(f"{module}: {str(e)}")
            except Exception as e:
                import_errors.append(f"{module}: {str(e)}")
        
        if import_errors:
            self.results.append(ValidationResult(
                name="Module Imports",
                passed=False,
                message=f"Failed to import {len(import_errors)} modules",
                details=import_errors
            ))
        else:
            self.results.append(ValidationResult(
                name="Module Imports",
                passed=True,
                message="All core modules import successfully"
            ))
    
    def _check_tests_pass(self) -> None:
        """Run tests and check if they pass."""
        print("[7/7] Running tests...")
        
        exit_code, output = self._run_command([
            sys.executable, "-m", "pytest", "-q", "--tb=no"
        ])
        
        if exit_code == 0:
            self.results.append(ValidationResult(
                name="Tests",
                passed=True,
                message="All tests passed"
            ))
        else:
            failed_line = ""
            for line in output.split("\n"):
                if "failed" in line.lower() or "error" in line.lower():
                    failed_line = line.strip()
                    break
            self.results.append(ValidationResult(
                name="Tests",
                passed=False,
                message=f"Tests failed: {failed_line}" if failed_line else "Tests failed",
                details=[line for line in output.split("\n") if line.strip()][:10]
            ))
    
    def _print_summary(self) -> bool:
        """Print summary and return overall success."""
        print()
        print("=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        
        passed_count = sum(1 for r in self.results if r.passed)
        total_count = len(self.results)
        
        for result in self.results:
            status = "PASS" if result.passed else "FAIL"
            symbol = "[+]" if result.passed else "[-]"
            print(f"  {symbol} {result.name}: {result.message}")
            if result.details and self.verbose:
                for detail in result.details[:3]:
                    print(f"      - {detail}")
                if len(result.details) > 3:
                    print(f"      ... and {len(result.details) - 3} more")
        
        print()
        print("-" * 60)
        print(f"  TOTAL: {passed_count}/{total_count} validations passed")
        print("=" * 60)
        
        all_passed = passed_count == total_count
        if all_passed:
            print("  STATUS: ALL VALIDATIONS PASSED")
        else:
            print(f"  STATUS: {total_count - passed_count} VALIDATION(S) FAILED")
        
        return all_passed


def main():
    parser = argparse.ArgumentParser(
        description="Run all validations for IA Hoteles Agent project"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check mode (no fixes applied)"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick mode (essential validations only)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce output verbosity"
    )
    
    args = parser.parse_args()
    
    runner = ValidationRunner(
        check_only=args.check,
        quick=args.quick,
        verbose=not args.quiet
    )
    
    success = runner.run_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
