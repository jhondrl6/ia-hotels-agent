"""Deploy Manager - Orchestrates remote deployment of assets.

MVP v2.5: Dry-run mode only
- Validates credentials
- Lists actions to be performed
- Does NOT execute actual uploads

v2.6+: Full execution mode
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

try:  # optional at runtime
    from dotenv import find_dotenv, load_dotenv
except Exception:  # pragma: no cover
    find_dotenv = None
    load_dotenv = None

from modules.deployer.connectors.base import BaseConnector, ConnectionResult
from modules.deployer.connectors.ftp_connector import FTPConnector
from modules.deployer.connectors.wordpress_connector import WordPressConnector


@dataclass
class DeployAction:
    """Represents a single deployment action."""
    action_type: str  # "upload", "publish", "inject"
    source_file: str
    destination: str
    description: str
    risk_level: str = "low"  # low, medium, high


@dataclass
class DeployPlan:
    """Represents a complete deployment plan."""
    target: str
    method: str
    actions: List[DeployAction] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    credentials_valid: bool = False
    preflight_passed: bool = False


class DeployManager:
    """Orchestrates remote deployment of assets."""

    EXIT_SUCCESS = 0
    EXIT_ERROR = 1
    EXIT_CREDENTIALS_INVALID = 2
    EXIT_ASSETS_MISSING = 3
    EXIT_CONFIG_INCOMPLETE = 4

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize deploy manager.
        
        Args:
            config_path: Optional path to deploy_config.yaml
        """
        self.config_path = config_path
        self.connectors: Dict[str, BaseConnector] = {
            "ftp": FTPConnector(),
            "wp-api": WordPressConnector(),
        }

        # Ensure .env is loaded so deploy can run in the same way as other modules.
        if load_dotenv and find_dotenv:
            try:
                load_dotenv(find_dotenv(usecwd=True), override=False)
            except Exception:
                pass

    def execute(
        self,
        target: str,
        method: str,
        dry_run: bool = True,
        verbose: bool = False,
    ) -> int:
        """Execute deployment (or dry-run).
        
        Args:
            target: Hotel name or path to delivery_assets folder
            method: Connection method ("ftp" or "wp-api")
            dry_run: If True, only validate and plan (default in v2.5)
            verbose: If True, show detailed logs
            
        Returns:
            Exit code (0=success, see EXIT_* constants)
        """
        print(f"\n[DEPLOY] Iniciando despliegue...")
        print(f"   Target: {target}")
        print(f"   Método: {method}")
        print(f"   Modo: {'DRY-RUN (simulación)' if dry_run else 'EJECUCIÓN REAL'}")

        # Step 1: Locate assets
        assets_dir = self._locate_assets(target)
        if assets_dir is None:
            print(f"   [ERROR] No se encontró carpeta de assets para: {target}")
            return self.EXIT_ASSETS_MISSING

        print(f"   [OK] Assets encontrados: {assets_dir}")

        # Step 2: Load manifest
        manifest = self._load_manifest(assets_dir)
        if manifest is None:
            print(f"   [WARN] No se encontró manifest.json")
        else:
            print(f"   [OK] Manifest cargado: v{manifest.get('version', '?')}")

        # Step 3: Validate connector
        if method not in self.connectors:
            print(f"   [ERROR] Método no soportado: {method}")
            return self.EXIT_CONFIG_INCOMPLETE

        connector = self.connectors[method]

        # Step 4: Load credentials
        credentials = self._load_credentials(target, method)
        if credentials is None:
            print(f"   [ERROR] Credenciales no encontradas para {target}")
            return self.EXIT_CREDENTIALS_INVALID

        # Step 5: Validate connection (dry-run always does this)
        print(f"\n[PREFLIGHT] Validando conexión...")
        result = connector.validate_connection(credentials)
        
        if not result.success:
            print(f"   [ERROR] Conexión fallida: {result.error}")
            return self.EXIT_CREDENTIALS_INVALID

        print(f"   [OK] Conexión válida: {result.message}")

        # Step 6: Build deployment plan
        plan = self._build_plan(assets_dir, method, manifest)

        # Step 7: Display plan
        self._display_plan(plan)

        # Step 8: Execute or dry-run
        if dry_run:
            print(f"\n[DRY-RUN] Simulación completada. No se realizaron cambios.")
            print(f"   Para ejecutar de verdad, quita el flag --dry-run")
            return self.EXIT_SUCCESS

        if not plan.actions:
            print("\n[EXECUTE] No hay acciones para ejecutar (plan vacío)")
            return self.EXIT_ASSETS_MISSING

        print(f"\n[EXECUTE] Iniciando despliegue real (v2.6 experimental)")
        for action in plan.actions:
            result = self._execute_action(connector, assets_dir, credentials, action)
            if result.success:
                msg = result.message or action.description
                print(f"   [OK] {msg}")
            else:
                err = result.error or "Acción fallida"
                plan.errors.append(f"{action.description}: {err}")
                print(f"   [ERROR] {action.description}: {err}")

        if plan.errors:
            print("\n[EXECUTE] Despliegue completado con errores")
            for err in plan.errors:
                print(f"   - {err}")
            return self.EXIT_ERROR

        print("\n[EXECUTE] Despliegue completado sin errores críticos")
        return self.EXIT_SUCCESS

    def preflight(self, target: str) -> int:
        """Run preflight checks without attempting connection.
        
        Validates:
        - Assets exist
        - Manifest exists
        - Credentials configured
        - Required files present
        """
        print(f"\n[PREFLIGHT] Verificando requisitos para: {target}")

        # Check assets
        assets_dir = self._locate_assets(target)
        if assets_dir is None:
            print(f"   ❌ Assets no encontrados")
            return self.EXIT_ASSETS_MISSING
        print(f"   ✅ Assets: {assets_dir}")

        # Check manifest
        manifest = self._load_manifest(assets_dir)
        if manifest is None:
            print(f"   ⚠️  Manifest.json no encontrado")
        else:
            print(f"   ✅ Manifest: v{manifest.get('version', '?')}")

        # Check required files
        required_files = [
            "boton_whatsapp_codigo.html",
            "barra_reserva_movil.html",
            "hotel-schema.json",
            "50_optimized_faqs.csv",
            "geo_playbook.md",
        ]
        missing = [f for f in required_files if not self._find_file(assets_dir, f)]
        if missing:
            print(f"   ⚠️  Archivos faltantes: {missing}")
        else:
            print(f"   ✅ Archivos requeridos presentes")

        print(f"\n[PREFLIGHT] Verificación completada")
        return self.EXIT_SUCCESS

    def _locate_assets(self, target: str) -> Optional[Path]:
        """Locate delivery_assets folder for target."""
        # Try as direct path
        direct = Path(target)
        if direct.exists() and direct.is_dir():
            if (direct / "manifest.json").exists():
                return direct
            if (direct / "delivery_assets").exists():
                return direct / "delivery_assets"

        # Try in output/clientes/
        client_path = Path("output/clientes") / target / "delivery_assets"
        if client_path.exists():
            return client_path

        # Try in output/ directly
        output_path = Path("output") / target / "delivery_assets"
        if output_path.exists():
            return output_path

        return None

    def _load_manifest(self, assets_dir: Path) -> Optional[Dict[str, Any]]:
        """Load manifest.json from assets directory."""
        manifest_path = assets_dir / "manifest.json"
        if not manifest_path.exists():
            return None
        
        try:
            with open(manifest_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def _find_file(self, assets_dir: Path, filename: str) -> Optional[Path]:
        """Busca un archivo en raíz, roles o manifest (rutas relativas)."""
        direct = assets_dir / filename
        if direct.exists():
            return direct

        for folder in assets_dir.iterdir():
            if folder.is_dir():
                candidate = folder / filename
                if candidate.exists():
                    return candidate

        manifest = self._load_manifest(assets_dir)
        if manifest:
            for entry in manifest.get("files_generated", []):
                path_str = entry.get("path")
                if not path_str:
                    continue
                p = assets_dir / path_str
                if p.name == filename and p.exists():
                    return p
        return None

    def _load_credentials(self, target: str, method: str) -> Optional[Dict[str, str]]:
        """Load credentials from environment or config file.
        
        Priority:
        1. Environment variables (IAH_FTP_*, IAH_WP_*)
        2. .env file
        3. deploy_config.yaml
        """
        credentials: Dict[str, str] = {}

        if method == "ftp":
            credentials = {
                "host": os.environ.get("IAH_FTP_HOST", ""),
                "user": os.environ.get("IAH_FTP_USER", ""),
                "password": os.environ.get("IAH_FTP_PASS", ""),
                "port": os.environ.get("IAH_FTP_PORT", "21"),
            }
        elif method == "wp-api":
            credentials = {
                "site_url": os.environ.get("IAH_WP_URL", ""),
                "username": os.environ.get("IAH_WP_USER", ""),
                "app_password": os.environ.get("IAH_WP_APP_PASS", ""),
            }

        # Fill missing values from YAML config if available.
        if not all(v for v in credentials.values()):
            yaml_creds = self._load_credentials_from_yaml(target, method)
            if yaml_creds:
                for k, v in yaml_creds.items():
                    if not credentials.get(k) and v:
                        credentials[k] = str(v)

        if not all(v for v in credentials.values()):
            return None

        return credentials

    def _candidate_config_paths(self) -> List[Path]:
        paths: List[Path] = []

        env_path = os.environ.get("IAH_DEPLOY_CONFIG", "").strip()
        if env_path:
            paths.append(Path(env_path))

        if self.config_path is not None:
            paths.append(self.config_path)
        else:
            paths.extend([
                Path("config") / "deploy_config.yaml",
                Path("deploy_config.yaml"),
            ])

        # De-duplicate while keeping order
        seen = set()
        unique: List[Path] = []
        for p in paths:
            key = str(p)
            if key in seen:
                continue
            seen.add(key)
            unique.append(p)
        return unique

    def _load_deploy_config(self) -> Optional[Dict[str, Any]]:
        for path in self._candidate_config_paths():
            try:
                if not path.exists():
                    continue
                with open(path, encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                if isinstance(data, dict):
                    return data
            except Exception:
                continue
        return None

    def _target_key_candidates(self, target: str) -> List[str]:
        raw = (target or "").strip()
        if not raw:
            return []
        lower = raw.lower()
        underscored = lower.replace(" ", "_")
        dashed = lower.replace(" ", "-")
        return [raw, lower, underscored, dashed]

    def _load_credentials_from_yaml(self, target: str, method: str) -> Optional[Dict[str, str]]:
        config = self._load_deploy_config()
        if not config:
            return None

        targets = config.get("targets") if isinstance(config, dict) else None
        if not isinstance(targets, dict):
            return None

        for key in self._target_key_candidates(target):
            node = targets.get(key)
            if not isinstance(node, dict):
                continue
            creds = node.get(method)
            if isinstance(creds, dict):
                return {str(k): str(v) for k, v in creds.items()}
        return None

    def _build_plan(
        self, 
        assets_dir: Path, 
        method: str, 
        manifest: Optional[Dict[str, Any]]
    ) -> DeployPlan:
        """Build deployment plan based on assets."""
        plan = DeployPlan(
            target=str(assets_dir),
            method=method,
            credentials_valid=True,
            preflight_passed=True,
        )

        # Add actions based on files present (roles/manifest-aware)
        wa_button = self._find_file(assets_dir, "boton_whatsapp_codigo.html")
        if wa_button:
            plan.actions.append(DeployAction(
                action_type="inject",
                source_file=wa_button.relative_to(assets_dir).as_posix(),
                destination="footer (antes de </body>)",
                description="Inyectar botón WhatsApp flotante",
                risk_level="low",
            ))

        booking_bar = self._find_file(assets_dir, "barra_reserva_movil.html")
        if booking_bar:
            plan.actions.append(DeployAction(
                action_type="inject",
                source_file=booking_bar.relative_to(assets_dir).as_posix(),
                destination="footer (antes de </body>)",
                description="Inyectar barra de reserva móvil",
                risk_level="low",
            ))

        schema = self._find_file(assets_dir, "hotel-schema.json")
        if schema:
            plan.actions.append(DeployAction(
                action_type="inject",
                source_file=schema.relative_to(assets_dir).as_posix(),
                destination="<head>",
                description="Agregar Schema.org JSON-LD",
                risk_level="medium",
            ))

        article = self._find_file(assets_dir, "articulo_reserva_directa.md")
        if article:
            plan.actions.append(DeployAction(
                action_type="publish",
                source_file=article.relative_to(assets_dir).as_posix(),
                destination="Blog (nuevo post borrador)",
                description="Publicar artículo de reserva directa",
                risk_level="low",
            ))

        if not plan.actions:
            hint = "No se detectaron archivos accionables en raíz/roles"
            if manifest:
                hint += " (manifest presente)"
            else:
                hint += " (manifest ausente)"
            plan.warnings.append(hint)

        return plan

    def _execute_action(
        self,
        connector: BaseConnector,
        assets_dir: Path,
        credentials: Dict[str, str],
        action: DeployAction,
    ) -> ConnectionResult:
        source_path = assets_dir / action.source_file
        if not source_path.exists():
            return ConnectionResult(success=False, error=f"Archivo no encontrado: {action.source_file}")

        try:
            if action.action_type == "inject":
                code = source_path.read_text(encoding="utf-8")
                target_hint = action.destination.lower()
                target = "footer" if "footer" in target_hint else "header"
                return connector.inject_code(code, target, credentials)

            if action.action_type == "publish":
                content = source_path.read_text(encoding="utf-8")
                title = self._extract_title_from_markdown(content) or action.source_file
                return connector.create_post(
                    title=title,
                    content=content,
                    status="draft",
                    credentials=credentials,
                )

            if action.action_type == "upload":
                return connector.upload_file(
                    local_path=str(source_path),
                    remote_path=action.destination,
                    credentials=credentials,
                )

            return ConnectionResult(success=False, error=f"Tipo de acción no soportado: {action.action_type}")
        except Exception as exc:  # pragma: no cover - protección defensiva
            return ConnectionResult(success=False, error=f"Excepción ejecutando acción: {exc}")

    def _extract_title_from_markdown(self, content: str) -> str:
        for line in content.splitlines():
            cleaned = line.strip()
            if not cleaned:
                continue
            if cleaned.startswith("#"):
                return cleaned.lstrip("# ").strip() or ""
            return cleaned
        return ""

    def _display_plan(self, plan: DeployPlan) -> None:
        """Display deployment plan to user."""
        print(f"\n[PLAN] Acciones a ejecutar ({len(plan.actions)} total):")
        print("-" * 60)

        for i, action in enumerate(plan.actions, 1):
            risk_icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(action.risk_level, "⚪")
            print(f"   {i}. [{risk_icon}] {action.description}")
            print(f"      Archivo: {action.source_file}")
            print(f"      Destino: {action.destination}")
            print()

        if plan.warnings:
            print("[WARNINGS]")
            for warn in plan.warnings:
                print(f"   ⚠️  {warn}")
