#!/usr/bin/env python3
"""IA Hoteles Agent - Validation CLI.

Validates different aspects of the project without Gemini CLI dependency.

Usage:
    python scripts/validate.py                    # Validate all
    python scripts/validate.py --plan             # Plan Maestro only
    python scripts/validate.py --content <file>   # Validate file content
    python scripts/validate.py --security         # Scan for secrets
    python scripts/validate.py --quick            # Essential validations only
    python scripts/validate.py --json             # JSON output format
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from modules.validation import PlanValidator, ContentValidator, SecurityValidator

ANSI_RESET = "\033[0m"
ANSI_RED = "\033[91m"
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_CYAN = "\033[96m"
ANSI_BOLD = "\033[1m"


def colorize(text: str, color: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"{color}{text}{ANSI_RESET}"


class ValidationCLI:
    def __init__(self, use_json: bool = False):
        self.use_json = use_json
        self.results: List[Dict[str, Any]] = []
        self.total_checks = 0
        self.total_errors = 0
        self.total_warnings = 0

    def add_result(self, name: str, passed: bool, errors: List[str], warnings: List[str], checks_run: int) -> None:
        self.results.append({
            "name": name,
            "passed": passed,
            "errors": errors,
            "warnings": warnings,
            "checks_run": checks_run,
        })
        self.total_checks += checks_run
        self.total_errors += len(errors)
        self.total_warnings += len(warnings)

    def print_result(self, name: str, passed: bool, errors: List[str], warnings: List[str]) -> None:
        if self.use_json:
            return

        status = colorize("[PASS]", ANSI_GREEN) if passed else colorize("[FAIL]", ANSI_RED)
        print(f"{status} {name}")

        for err in errors:
            print(f"  {colorize('ERROR:', ANSI_RED)} {err}")

        for warn in warnings:
            print(f"  {colorize('WARN:', ANSI_YELLOW)} {warn}")

    def print_header(self, title: str) -> None:
        if self.use_json:
            return
        print()
        print(colorize("=" * 60, ANSI_CYAN))
        print(colorize(f" {title}", ANSI_BOLD))
        print(colorize("=" * 60, ANSI_CYAN))

    def print_summary(self) -> bool:
        overall_passed = self.total_errors == 0

        if self.use_json:
            output = {
                "passed": overall_passed,
                "total_checks": self.total_checks,
                "total_errors": self.total_errors,
                "total_warnings": self.total_warnings,
                "results": self.results,
            }
            print(json.dumps(output, indent=2))
            return overall_passed

        print()
        print(colorize("-" * 60, ANSI_CYAN))
        print(colorize(" SUMMARY", ANSI_BOLD))
        print(colorize("-" * 60, ANSI_CYAN))
        print(f"  Checks run: {self.total_checks}")
        print(f"  Errors:     {colorize(str(self.total_errors), ANSI_RED if self.total_errors > 0 else ANSI_GREEN)}")
        print(f"  Warnings:   {colorize(str(self.total_warnings), ANSI_YELLOW if self.total_warnings > 0 else ANSI_GREEN)}")
        print()

        if overall_passed:
            print(colorize("All validations passed!", ANSI_GREEN))
        else:
            print(colorize(f"Validation failed with {self.total_errors} error(s)", ANSI_RED))

        return overall_passed

    def validate_plan(self) -> None:
        self.print_header("PLAN MAESTRO VALIDATION")

        try:
            validator = PlanValidator()
            result = validator.validate()
            self.add_result("Plan Maestro", result.passed, result.errors, result.warnings, result.checks_run)
            self.print_result("Plan Maestro", result.passed, result.errors, result.warnings)
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            self.add_result("Plan Maestro", False, [error_msg], [], 0)
            self.print_result("Plan Maestro", False, [error_msg], [])

    def validate_content(self, file_path: Path, content_type: str = "") -> None:
        self.print_header(f"CONTENT VALIDATION: {file_path.name}")

        if not file_path.exists():
            error_msg = f"File not found: {file_path}"
            self.add_result("Content", False, [error_msg], [], 0)
            self.print_result("Content", False, [error_msg], [])
            return

        try:
            content = file_path.read_text(encoding="utf-8")
            validator = ContentValidator()
            result = validator.validate(content, content_type)
            self.add_result("Content", result.passed, result.errors, result.warnings, result.checks_run)
            self.print_result("Content", result.passed, result.errors, result.warnings)
        except Exception as e:
            error_msg = f"Error reading file: {e}"
            self.add_result("Content", False, [error_msg], [], 0)
            self.print_result("Content", False, [error_msg], [])

    def validate_security(self, target: Path = None) -> None:
        if target is None:
            target = ROOT_DIR

        self.print_header(f"SECURITY SCAN: {target}")

        try:
            validator = SecurityValidator()

            if target.is_file():
                result = validator.validate_file(target)
            else:
                result = validator.validate_directory(target)

            self.add_result("Security", result.passed, result.errors, result.warnings, result.checks_run)
            self.print_result("Security", result.passed, result.errors, result.warnings)
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            self.add_result("Security", False, [error_msg], [], 0)
            self.print_result("Security", False, [error_msg], [])

    def validate_quick(self) -> None:
        self.print_header("QUICK VALIDATION (Essential Checks)")

        try:
            plan_validator = PlanValidator()
            result = plan_validator.validate()
            self.add_result("Plan Maestro", result.passed, result.errors, result.warnings, result.checks_run)
            self.print_result("Plan Maestro", result.passed, result.errors, result.warnings)
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            self.add_result("Plan Maestro", False, [error_msg], [], 0)
            self.print_result("Plan Maestro", False, [error_msg], [])

        try:
            security_validator = SecurityValidator()
            modules_dir = ROOT_DIR / "modules"
            if modules_dir.exists():
                result = security_validator.validate_directory(modules_dir)
                self.add_result("Security (modules)", result.passed, result.errors, result.warnings, result.checks_run)
                self.print_result("Security (modules)", result.passed, result.errors, result.warnings)
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            self.add_result("Security (modules)", False, [error_msg], [], 0)
            self.print_result("Security (modules)", False, [error_msg], [])

    def validate_all(self) -> None:
        self.validate_plan()
        self.validate_security()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate IA Hoteles Agent project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/validate.py                    # Run all validations
    python scripts/validate.py --plan             # Validate Plan Maestro only
    python scripts/validate.py --content file.md  # Validate file content
    python scripts/validate.py --security         # Scan for hardcoded secrets
    python scripts/validate.py --quick            # Essential validations only
    python scripts/validate.py --json             # Output as JSON
        """
    )

    parser.add_argument(
        "--plan",
        action="store_true",
        help="Validate Plan Maestro data only"
    )

    parser.add_argument(
        "--content",
        type=str,
        metavar="FILE",
        help="Validate content of specified file"
    )

    parser.add_argument(
        "--content-type",
        type=str,
        default="",
        metavar="TYPE",
        help="Content type for validation (e.g., definition_page, data_research)"
    )

    parser.add_argument(
        "--security",
        action="store_true",
        help="Scan code for hardcoded secrets"
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run only essential validations"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()
    cli = ValidationCLI(use_json=args.json)

    try:
        if args.content:
            content_path = Path(args.content)
            if not content_path.is_absolute():
                content_path = ROOT_DIR / content_path
            cli.validate_content(content_path, args.content_type)
        elif args.plan:
            cli.validate_plan()
        elif args.security:
            cli.validate_security()
        elif args.quick:
            cli.validate_quick()
        else:
            cli.validate_all()

        passed = cli.print_summary()
        return 0 if passed else 1

    except KeyboardInterrupt:
        if not args.json:
            print("\nValidation interrupted by user")
        return 130
    except Exception as e:
        if args.json:
            print(json.dumps({"passed": False, "error": str(e)}))
        else:
            print(colorize(f"Fatal error: {e}", ANSI_RED))
        return 1


if __name__ == "__main__":
    sys.exit(main())
