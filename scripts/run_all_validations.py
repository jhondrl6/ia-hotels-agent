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
import re
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

    # Directories to skip during rglob traversal (venvs, caches, git, node_modules)
    _SKIP_DIRS = {".venv-wsl", "venv", ".venv", "__pycache__", ".git", "node_modules",
                  ".mypy_cache", ".pytest_cache", ".tox", "dist", "build", ".eggs"}

    # Binarios conocidos: se excluyen del escaneo de secretos PERO se declaran
    # en el mensaje. Lo que no es texto ni binario conocido es NO_CUBIERTO (bloquea).
    _KNOWN_BINARY_EXTS = {
        ".zip", ".gz", ".bz2", ".xz", ".7z", ".tar", ".whl",
        ".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp", ".bmp",
        ".pdf", ".woff", ".woff2", ".ttf", ".eot", ".otf",
        ".pyc", ".pyo", ".exe", ".dll", ".pyd", ".so", ".class", ".o", ".a",
        ".mp3", ".mp4", ".avi", ".mov", ".db", ".sqlite3",
    }
    _MAX_SCAN_BYTES = 5_000_000

    def __init__(self, check_only: bool = False, quick: bool = False, verbose: bool = True,
                 repo_root=None):
        self.check_only = check_only
        self.quick = quick
        self.verbose = verbose
        self.results: list = []
        self.repo_root = Path(repo_root) if repo_root else ROOT_DIR

    def _walk(self, pattern: str):
        """rglob wrapper that prunes _SKIP_DIRS for performance on WSL."""
        for path in ROOT_DIR.rglob(pattern):
            # Skip any path that has a skipped directory as a component
            parts = path.relative_to(ROOT_DIR).parts
            if any(p in self._SKIP_DIRS for p in parts):
                continue
            yield path
    
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
        self._check_client_material()
        self._check_document_integration()
        self._check_prompts_no_release()
        self._check_opencode_refs()
        self._check_plan_citations()
        self._check_lesson_capitalization()
        
        if not self.quick:
            self._check_dependencies()
            self._check_imports()
            self._check_tests_pass()
            self._check_qmind_writeback()
        
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
        print("[1/10] Checking for residual files...")
        
        residual_extensions = {".bak", ".backup", ".tmp", ".old"}
        residual_files = []
        
        for path in self._walk("*"):
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
        print("[2/10] Checking Plan Maestro sync...")
        
        json_path = ROOT_DIR / "data" / "benchmarks" / "plan_maestro_data.json"
        md_path = ROOT_DIR / "data" / "benchmarks" / "Plan_maestro_v2_5.md"
        md_archive = ROOT_DIR / "archives" / "Plan_maestro_v2_5.md"

        if not json_path.exists():
            self.results.append(ValidationResult(
                name="Plan Maestro Sync",
                passed=False,
                message="plan_maestro_data.json not found"
            ))
            return

        # Plan_maestro_v2_5.md is historical/archived — ok if in archives
        if not md_path.exists() and not md_archive.exists():
            self.results.append(ValidationResult(
                name="Plan Maestro Sync",
                passed=False,
                message="Plan_maestro_v2_5.md not found (benchmarks/ or archives/)"
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
        print("[3/10] Checking version synchronization...")
        
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
    
    def _secret_patterns(self) -> list:
        """Patrones de secreto: asignaciones legacy + valores de key en cualquier contexto."""
        return [
            (r'DEEPSEEK_API_KEY\s*=\s*["\'][^"\']+["\']', "DEEPSEEK_API_KEY assignment"),
            (r'ANTHROPIC_API_KEY\s*=\s*["\'][^"\']+["\']', "ANTHROPIC_API_KEY assignment"),
            (r'GOOGLE_API_KEY\s*=\s*["\'][^"\']+["\']', "GOOGLE_API_KEY assignment"),
            (r'GOOGLEMAPS_API_KEY\s*=\s*["\'][^"\']+["\']', "GOOGLEMAPS_API_KEY assignment"),
            (r'AIzaSy[A-Za-z0-9_\-]{30,}', "Google API key (AIzaSy...)"),
            (r'sk-[A-Za-z0-9]{20,}', "OpenAI/secret key (sk-...)"),
            (r'ghp_[A-Za-z0-9]{30,}', "GitHub PAT (ghp_...)"),
            (r'pplx-[A-Za-z0-9]{20,}', "Perplexity key (pplx-...)"),
        ]

    def _git_tracked_files(self) -> list:
        """Archivos versionados (index). Fallback a _walk si git falla."""
        try:
            result = subprocess.run(
                ["git", "ls-files", "-z"],
                capture_output=True, text=True, cwd=self.repo_root, timeout=30
            )
            if result.returncode == 0:
                return [self.repo_root / p for p in result.stdout.split("\0") if p]
        except Exception:
            pass
        return [p for p in self._walk("*") if p.is_file()]

    def _git_staged_paths(self) -> list:
        """Rutas con cambios staged (añadidos/copiados/modificados)."""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "-z", "--diff-filter=ACM"],
                capture_output=True, text=True, cwd=self.repo_root, timeout=30
            )
            if result.returncode == 0:
                return [p for p in result.stdout.split("\0") if p]
        except Exception:
            pass
        return []

    def _check_no_secrets(self) -> None:
        """Check for hardcoded secrets — FASE-P5 AC-S2 (remendada 2026-09-15).

        Alcance: lo que se prepara para publicar = archivos tracked + contenido
        staged. La clasificación es por sniff NUL, no por whitelist de extensiones:
        todo tracked con pinta de texto se lee. Los binarios conocidos se excluyen
        pero se declaran en el mensaje; lo no clasificable es NO_CUBIERTO y bloquea
        (L-PF6: ningún verde por no-leer). Estados NR8: SIN_HALLAZGOS / BLOCKING /
        NO_LEGIBLE / NO_CUBIERTO. Salida redactada: nunca imprime el valor del secreto.
        """
        print("[4/10] Checking for hardcoded secrets (tracked + staged)...")

        patterns = self._secret_patterns()

        # Allowlist: directorios de cuarentena que pueden contener referencias a
        # secrets como parte de su propósito (archivado, evidencia, planificación).
        # El contenido staged y el material de cliente se siguen evaluando sin
        # excepción de lectura directa sobre estos directorios.
        allowed_dirs = {"archives", "evidence", ".opencode"}

        violations = []
        non_readable = []
        non_covered = []
        scanned_count = 0
        binaries_excluded = 0
        symlinks_excluded = 0

        # 1. Escanear archivos versionables (tracked en disco)
        for path in self._git_tracked_files():
            rel_path = path.relative_to(self.repo_root)
            if rel_path.parts and rel_path.parts[0] in allowed_dirs:
                continue
            try:
                if path.is_symlink():
                    symlinks_excluded += 1
                    continue
                if not path.is_file():
                    continue
                if path.suffix.lower() in self._KNOWN_BINARY_EXTS:
                    binaries_excluded += 1
                    continue
                if path.stat().st_size > self._MAX_SCAN_BYTES:
                    non_covered.append(f"{rel_path} (supera {_MAX_SCAN_BYTES} bytes)")
                    continue
                raw = path.read_bytes()
            except (PermissionError, OSError):
                non_readable.append(str(rel_path))
                continue
            if b"\x00" in raw[:8192]:
                non_covered.append(str(rel_path))
                continue
            scanned_count += 1
            content = raw.decode("utf-8", errors="ignore")
            for pattern, description in patterns:
                if re.search(pattern, content):
                    violations.append(f"{rel_path} ({description})")
                    break  # Un archivo = una violación max

        # 2. Escanear contenido staged (git diff --cached)
        violations.extend(self._check_staged_content(patterns))

        # 3. Reportar con estados NR8
        if violations:
            self.results.append(ValidationResult(
                name="Secrets Check",
                passed=False,
                message=f"BLOCKING: {len(violations)} potential secret(s) found",
                details=violations[:5]
            ))
        elif non_readable:
            self.results.append(ValidationResult(
                name="Secrets Check",
                passed=False,
                message=f"NO_LEGIBLE: {len(non_readable)} file(s) could not be scanned",
                details=non_readable[:5]
            ))
        elif non_covered:
            self.results.append(ValidationResult(
                name="Secrets Check",
                passed=False,
                message=f"NO_CUBIERTO: {len(non_covered)} file(s) not classifiable as text",
                details=non_covered[:5]
            ))
        else:
            self.results.append(ValidationResult(
                name="Secrets Check",
                passed=True,
                message=(f"SIN_HALLAZGOS: {scanned_count} tracked files + staged "
                         f"(excluidos declarados: {binaries_excluded} binarios conocidos, "
                         f"{symlinks_excluded} symlinks)")
            ))

    def _check_client_material(self) -> None:
        """Política de material de cliente — AC-S2 remendada, separada de la
        detección de claves.

        Impide versionar (tracked o staged) archivos cuya ruta contenga marcadores
        de cliente fuera de los directorios de cuarentena. Lo ya versionado antes
        de la política queda grandfathered en el config, con dueño declarado y
        disposición pendiente de la puerta AC-S4.
        """
        print("[5/10] Checking client material policy (tracked + staged)...")

        policy_path = ROOT_DIR / "config" / "client_material_policy.yaml"
        policy = None
        try:
            import yaml
            policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
        except Exception:
            policy = None

        if not policy:
            self.results.append(ValidationResult(
                name="Client Material",
                passed=False,
                message="POLICY_MISSING: config/client_material_policy.yaml no encontrado o ilegible"
            ))
            return

        markers = [m.lower() for m in policy.get("client_markers", [])]
        quarantine = [q.lower() for q in policy.get("quarantine_dirs", [])]
        grandfathered = {g.lower() for g in policy.get("grandfathered_paths", [])}

        paths = {p.relative_to(self.repo_root).as_posix() for p in self._git_tracked_files()}
        paths.update(self._git_staged_paths())

        violations = []
        for posix in sorted(paths):
            low = posix.lower()
            if any(low.startswith(q) for q in quarantine):
                continue
            if low in grandfathered:
                continue
            hits = [m for m in markers if m in low]
            if hits:
                violations.append(f"{posix} (marcadores: {', '.join(hits)})")

        if violations:
            self.results.append(ValidationResult(
                name="Client Material",
                passed=False,
                message=f"BLOCKING: {len(violations)} archivo(s) de cliente fuera de cuarentena",
                details=violations[:10]
            ))
        else:
            self.results.append(ValidationResult(
                name="Client Material",
                passed=True,
                message=(f"SIN_HALLAZGOS: {len(paths)} rutas contra {len(markers)} marcadores "
                         f"({len(grandfathered)} grandfathered con dueño)")
            ))

    def _check_staged_content(self, patterns: list) -> list:
        """Check staged content (git diff --cached) for secrets. AC-S2."""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--diff-filter=ACM", "-U0"],
                capture_output=True, text=True, cwd=self.repo_root, timeout=10
            )
            if result.returncode != 0:
                return []  # Not a git repo or no staged changes

            staged_diff = result.stdout
            if not staged_diff:
                return []

            violations = []
            # Extraer solo las líneas añadidas (empiezan con +)
            added_lines = [
                line[1:] for line in staged_diff.split('\n')
                if line.startswith('+') and not line.startswith('+++')
            ]
            added_content = '\n'.join(added_lines)

            for pattern, description in patterns:
                if re.search(pattern, added_content):
                    violations.append(f"STAGED content ({description})")

            return violations
        except Exception:
            return []
    
    def _check_document_integration(self) -> None:
        """Check cross-document integration consistency."""
        print("[6/10] Checking document integration...")
        
        script_path = ROOT_DIR / "scripts" / "validate_document_integration.py"
        if not script_path.exists():
            self.results.append(ValidationResult(
                name="Document Integration",
                passed=False,
                message="validate_document_integration.py not found"
            ))
            return
        
        exit_code, output = self._run_command([sys.executable, str(script_path)])
        
        if exit_code == 0:
            self.results.append(ValidationResult(
                name="Document Integration",
                passed=True,
                message="All cross-document checks passed"
            ))
        else:
            lines = output.split('\n')
            issues = [l for l in lines if '[FAIL]' in l or '[!]' in l][:5]
            self.results.append(ValidationResult(
                name="Document Integration",
                passed=False,
                message="Cross-document validation failed",
                details=issues
            ))
    
    def _check_prompts_no_release(self) -> None:
        """Check that intermediate phase prompts don't use --release flag (L3/L9 enforcement).
        
        Scans 0[2-5]-prompt*.md files in .opencode/plans/ for --release used in
        log_phase_completion.py commands. Excludes Archives, RELEASE plans/prompts,
        and documentation-only references to --release.
        """
        print("[7/10] Checking prompts for --release flag in intermediate phases...")
        
        import re
        
        plans_dir = ROOT_DIR / ".opencode" / "plans"
        if not plans_dir.exists():
            self.results.append(ValidationResult(
                name="Prompts No Release",
                passed=True,
                message="No .opencode/plans/ directory found, skipping"
            ))
            return
        
        # Only flag --release when it appears AFTER log_phase_completion.py on the same line.
        # This matches actual command invocations like:
        #   scripts/log_phase_completion.py --fase FASE-X ... --release 4.70.0
        # but NOT documentation that discusses the flag in reverse order or separately.
        cmd_release_pattern = re.compile(r'log_phase_completion\.py.*--release\s+\d')
        violations = []
        
        for plan_dir in plans_dir.iterdir():
            if not plan_dir.is_dir():
                continue
            # Skip Archives directories (historical, not audited)
            if "archive" in plan_dir.name.lower():
                continue
            # Skip RELEASE plans (those phases DO use --release)
            if "RELEASE" in plan_dir.name:
                continue
            
            for md_file in plan_dir.glob("0[2-5]-prompt*.md"):
                # Exclude RELEASE prompt files even within non-RELEASE plans
                if "RELEASE" in md_file.name:
                    continue
                try:
                    content = md_file.read_text(encoding="utf-8")
                    matches = cmd_release_pattern.findall(content)
                    if matches:
                        rel_path = md_file.relative_to(ROOT_DIR)
                        violations.append(f"{rel_path} ({len(matches)} occurrence(s))")
                except Exception:
                    continue
        
        if violations:
            self.results.append(ValidationResult(
                name="Prompts No Release",
                passed=False,
                message=f"Found --release in {len(violations)} intermediate prompt(s)",
                details=violations
            ))
        else:
            self.results.append(ValidationResult(
                name="Prompts No Release",
                passed=True,
                message="No --release flag in intermediate prompts"
            ))
    
    def _check_opencode_refs(self) -> None:
        """Check that .opencode path references in Markdown docs still exist.

        Catches forgotten reference updates after archiving plans (Archives/)
        or contexts (Historico/). Repair manually with --fix on the script.
        """
        print("[8/10] Checking .opencode references...")
        
        script_path = ROOT_DIR / "scripts" / "validate_opencode_refs.py"
        if not script_path.exists():
            self.results.append(ValidationResult(
                name="OpenCode References",
                passed=False,
                message="validate_opencode_refs.py not found"
            ))
            return
        
        exit_code, output = self._run_command([sys.executable, str(script_path)])
        
        if exit_code == 0:
            self.results.append(ValidationResult(
                name="OpenCode References",
                passed=True,
                message="All .opencode references exist"
            ))
        else:
            lines = output.split('\n')
            issues = [l.strip() for l in lines if '->' in l][:5]
            self.results.append(ValidationResult(
                name="OpenCode References",
                passed=False,
                message="Broken .opencode references (fix: scripts/validate_opencode_refs.py --fix)",
                details=issues
            ))
    
    def _check_plan_citations(self) -> None:
        """Check that plans do not introduce line-number citations (FASE-HOTFIX H9).

        Materializes executor rule R2.2 (`phased_project_executor.md` v2.19.0):
        a multi-phase plan cites SYMBOLS, never `file.py:123`, because every phase
        that edits code invalidates the lines later phases cite (medido: 14 de 16).

        Scope is (1) forward + (2) delta: new plan files cite nothing, and the
        historical inventory may not grow. The validator REPORTS - it never rewrites
        numbers, because a rewritten line citation is the same defect dressed up as
        a fix.
        """
        print("[9/10] Checking plan citations (simbolos, no numeros de linea)...")

        script_path = ROOT_DIR / "scripts" / "validate_plan_citations.py"
        if not script_path.exists():
            self.results.append(ValidationResult(
                name="Plan Citations",
                passed=False,
                message="validate_plan_citations.py not found"
            ))
            return

        exit_code, output = self._run_command([sys.executable, str(script_path)])

        if exit_code == 0:
            self.results.append(ValidationResult(
                name="Plan Citations",
                passed=True,
                message=(output.strip().splitlines() or ["OK"])[-1]
            ))
        else:
            lines = output.split('\n')
            issues = [l.strip()[2:] for l in lines if l.strip().startswith('- ')][:5]
            self.results.append(ValidationResult(
                name="Plan Citations",
                passed=False,
                message=("Line-number citations introduced or grown in plans "
                         "(fix: cite symbols, or --update-baseline if the record legitimately grew)"),
                details=issues
            ))

    def _check_lesson_capitalization(self) -> None:
        """Check that plans conceived under executor v2.22.0 capitalized the corpus.

        Materializes the Paso 0 artifact contract (`00-lecciones-capitalizadas.md`):
        literal queries, lessons whose "what changes" names an AC that really exists,
        >=3 discarded candidates, a declared coverage section, and lesson IDs whose owner
        matches the generated index (>=2 distinct owners, so citing only the immediate
        predecessor stops being enough).

        A green here means FORM AND TRACEABILITY, never relevance: the script publishes
        the population it looked at because an [OK] without a denominator is L-R.3.
        """
        print("[10/10] Checking lesson capitalization (Paso 0 del executor)...")

        script_path = ROOT_DIR / "scripts" / "validate_lesson_capitalization.py"
        if not script_path.exists():
            self.results.append(ValidationResult(
                name="Lesson Capitalization",
                passed=False,
                message="validate_lesson_capitalization.py not found"
            ))
            return

        exit_code, output = self._run_command([sys.executable, str(script_path)])

        if exit_code == 0:
            self.results.append(ValidationResult(
                name="Lesson Capitalization",
                passed=True,
                message=(output.strip().splitlines() or ["OK"])[-1]
            ))
        else:
            lines = output.split('\n')
            issues = [l.strip()[2:] for l in lines if l.strip().startswith('- ')][:5]
            self.results.append(ValidationResult(
                name="Lesson Capitalization",
                passed=False,
                message=("Paso 0 sin capitalizar (fix: completar 00-lecciones-capitalizadas.md "
                         "a mano; el verificador reporta, no reescribe)"),
                details=issues
            ))

    def _check_dependencies(self) -> None:
        """Check if all dependencies are installed."""
        print("[11/14] Checking dependencies...")
        
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
        print("[12/14] Checking core module imports...")
        
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
        print("[13/14] Running tests...")
        
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
    
    def _check_qmind_writeback(self) -> None:
        """Check archived plans have their 10-analisis ingested into QMind.

        Materializes the executor write-back contract (:572-574, :588) via the
        `qmind` CLI. If the CLI is unavailable the validator itself degrades to
        WARN + exit 0 (fallback :468); only a real missing ingestion fails.
        """
        print("[14/14] Checking QMind write-back (planes archivados)...")

        script_path = ROOT_DIR / "scripts" / "validate_qmind_writeback.py"
        if not script_path.exists():
            self.results.append(ValidationResult(
                name="QMind Write-back",
                passed=False,
                message="validate_qmind_writeback.py not found"
            ))
            return

        exit_code, output = self._run_command([sys.executable, str(script_path)])

        if exit_code == 0:
            self.results.append(ValidationResult(
                name="QMind Write-back",
                passed=True,
                message=(output.strip().splitlines() or ["OK"])[-1]
            ))
        else:
            lines = output.split('\n')
            issues = [l.strip()[2:] for l in lines if l.strip().startswith('- ')][:5]
            self.results.append(ValidationResult(
                name="QMind Write-back",
                passed=False,
                message="Archived plans missing QMind write-back "
                        "(fix: python scripts/validate_qmind_writeback.py --upload <PLAN>)",
                details=issues
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
