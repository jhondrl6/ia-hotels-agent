"""
Provider Registry -- Registro centralizado de proveedores de datos y LLM.

Patron inspirado en Goose (provider catalog). Un solo archivo YAML
donde se configuran TODOS los proveedores: endpoint, auth, costo, retry.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

import yaml


@dataclass
class ProviderConfig:
    id: str
    type: str
    description: str
    auth_type: str
    env_vars: List[str] = field(default_factory=list)
    endpoint: Optional[str] = None
    enabled: bool = True
    cost_per_call: float = 0.0
    retry_count: int = 2
    timeout_seconds: int = 15
    credentials_file: Optional[str] = None
    default_model: Optional[str] = None


class ProviderRegistry:
    """Singleton que carga y consulta el registro centralizado de proveedores."""
    _instance = None
    _providers: Dict[str, ProviderConfig] = {}
    _loaded: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self, config_path: Optional[str] = None) -> None:
        """Carga el archivo YAML de proveedores."""
        if self._loaded:
            return
        if config_path is None:
            project_root = Path(__file__).resolve().parent.parent.parent
            config_path = str(project_root / "config" / "provider_registry.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        for pid, pdata in raw.get("providers", {}).items():
            self._providers[pid] = ProviderConfig(
                id=pid,
                type=pdata.get("type", "unknown"),
                description=pdata.get("description", ""),
                auth_type=pdata.get("auth_type", "none"),
                env_vars=pdata.get("env_vars", []),
                endpoint=pdata.get("endpoint"),
                enabled=pdata.get("enabled", True),
                cost_per_call=pdata.get("cost_per_call", 0.0),
                retry_count=pdata.get("retry_count", 2),
                timeout_seconds=pdata.get("timeout_seconds", 15),
                credentials_file=pdata.get("credentials_file"),
                default_model=pdata.get("default_model"),
            )
        self._loaded = True

    @classmethod
    def reset(cls) -> None:
        """Reinicia el estado del singleton (para tests)."""
        cls._instance = None
        cls._providers = {}
        cls._loaded = False

    def get(self, provider_id: str) -> Optional[ProviderConfig]:
        """Obtiene la configuracion de un proveedor por ID."""
        return self._providers.get(provider_id)

    def list_by_type(self, type_: str) -> List[ProviderConfig]:
        """Lista proveedores por tipo (analytics, search, performance, llm)."""
        return [p for p in self._providers.values() if p.type == type_]

    def list_enabled(self) -> List[ProviderConfig]:
        """Lista todos los proveedores habilitados."""
        return [p for p in self._providers.values() if p.enabled]

    def is_configured(self, provider_id: str) -> bool:
        """Verifica si un proveedor tiene sus credenciales disponibles."""
        p = self._providers.get(provider_id)
        if not p or not p.enabled:
            return False
        if p.auth_type == "none":
            return True
        if p.credentials_file:
            # Check relative to project root
            project_root = Path(__file__).resolve().parent.parent.parent
            cred_path = project_root / p.credentials_file
            return cred_path.exists()
        for env_var in p.env_vars:
            if not os.environ.get(env_var):
                return False
        return True

    def estimated_cost_per_run(self) -> float:
        """Costo estimado por corrida v4complete (solo enabled + configurado)."""
        total = 0.0
        for p in self._providers.values():
            if p.enabled and self.is_configured(p.id) and p.cost_per_call:
                total += p.cost_per_call
        return total
