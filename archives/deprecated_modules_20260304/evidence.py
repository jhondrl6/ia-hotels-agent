"""Modelo de datos para evidencia recolectada.

Define la estructura de evidencia, que representa los datos brutos
recolectados desde una fuente específica (web scraping, API, input del usuario).
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Any
from uuid import UUID, uuid4
import json
import hashlib


@dataclass
class Evidence:
    """Representa una fuente de evidencia recolectada.

    La evidencia es la fuente de verdad para los claims. Cada claim
    debe estar respaldado por al menos una evidencia con hash de integridad.

    Attributes:
        evidence_id: UUID único de la evidencia.
        source_type: Tipo de fuente (ej: "web_scraping", "api_pagespeed").
        source_url: URL de origen (opcional).
        timestamp: Fecha/hora de recolección.
        data: Datos recolectados en formato dict.
        hash: Hash SHA-256 de los datos para integridad.
        metadata: Información adicional sobre la recolección.
    """

    # Campos obligatorios
    source_type: str
    data: dict[str, Any]

    # Campos con defaults
    evidence_id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    hash: str = field(default="")

    # Campos opcionales
    source_url: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validaciones y generación automática de hash."""
        if not self.source_type:
            raise ValueError("source_type is required")

        # Generar hash automáticamente si no se proporciona
        if not self.hash and self.data:
            self.hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """Calcula el hash SHA-256 de los datos.

        Returns:
            str: Hash hexadecimal de los datos.
        """
        # Serializar datos de forma consistente
        data_str = json.dumps(self.data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(data_str.encode("utf-8")).hexdigest()

    def verify_integrity(self) -> bool:
        """Verifica la integridad de los datos comparando el hash.

        Returns:
            bool: True si los datos no han sido modificados.
        """
        if not self.hash:
            return False
        calculated = self._calculate_hash()
        return calculated == self.hash

    @property
    def size_bytes(self) -> int:
        """Retorna el tamaño aproximado de los datos en bytes.

        Returns:
            int: Tamaño en bytes.
        """
        return len(json.dumps(self.data, separators=(",", ":")).encode("utf-8"))

    @property
    def is_api_source(self) -> bool:
        """Indica si la fuente es una API externa.

        Returns:
            bool: True si es fuente de API.
        """
        api_sources = {"api_pagespeed", "api_places", "api_rich_results"}
        return self.source_type in api_sources

    @property
    def is_manual_source(self) -> bool:
        """Indica si la fuente es input manual del usuario.

        Returns:
            bool: True si es fuente manual.
        """
        return self.source_type == "user_input"

    def get_nested_value(self, path: str, default: Any = None) -> Any:
        """Obtiene un valor anidado de los datos usando dot notation.

        Args:
            path: Ruta al valor (ej: "hotel.name").
            default: Valor por defecto si no existe.

        Returns:
            Any: Valor encontrado o default.
        """
        keys = path.split(".")
        value = self.data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def add_metadata(self, key: str, value: Any) -> None:
        """Agrega metadata adicional a la evidencia.

        Args:
            key: Clave de la metadata.
            value: Valor de la metadata.
        """
        self.metadata[key] = value

    def to_dict(self) -> dict[str, Any]:
        """Serializa la evidencia a diccionario.

        Returns:
            dict: Representación de la evidencia como diccionario.
        """
        data = asdict(self)
        # Convertir tipos no serializables
        data["evidence_id"] = str(self.evidence_id)
        data["timestamp"] = self.timestamp.isoformat()
        data["size_bytes"] = self.size_bytes
        data["is_api_source"] = self.is_api_source
        data["is_manual_source"] = self.is_manual_source
        data["integrity_verified"] = self.verify_integrity()
        return data

    def to_json(self) -> str:
        """Serializa la evidencia a JSON.

        Returns:
            str: Representación JSON de la evidencia.
        """
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Evidence":
        """Crea un Evidence desde un diccionario.

        Args:
            data: Diccionario con los datos de la evidencia.

        Returns:
            Evidence: Instancia de Evidence.
        """
        evidence_data = data.copy()

        if isinstance(evidence_data.get("evidence_id"), str):
            evidence_data["evidence_id"] = UUID(evidence_data["evidence_id"])

        if isinstance(evidence_data.get("timestamp"), str):
            evidence_data["timestamp"] = datetime.fromisoformat(
                evidence_data["timestamp"]
            )

        # Remover campos calculados si existen
        evidence_data.pop("size_bytes", None)
        evidence_data.pop("is_api_source", None)
        evidence_data.pop("is_manual_source", None)
        evidence_data.pop("integrity_verified", None)

        return cls(**evidence_data)

    @classmethod
    def from_json(cls, json_str: str) -> "Evidence":
        """Crea un Evidence desde un string JSON.

        Args:
            json_str: String JSON con los datos de la evidencia.

        Returns:
            Evidence: Instancia de Evidence.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_web_scraping(
        cls,
        url: str,
        scraped_data: dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
    ) -> "Evidence":
        """Factory method para crear evidencia desde web scraping.

        Args:
            url: URL scrapeada.
            scraped_data: Datos extraídos.
            metadata: Metadata adicional.

        Returns:
            Evidence: Instancia de Evidence.
        """
        return cls(
            source_type="web_scraping",
            source_url=url,
            data=scraped_data,
            metadata=metadata or {},
        )

    @classmethod
    def from_api(
        cls,
        api_name: str,
        endpoint: str,
        response_data: dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
    ) -> "Evidence":
        """Factory method para crear evidencia desde API.

        Args:
            api_name: Nombre de la API (ej: "pagespeed").
            endpoint: Endpoint consultado.
            response_data: Respuesta de la API.
            metadata: Metadata adicional.

        Returns:
            Evidence: Instancia de Evidence.
        """
        meta = metadata or {}
        meta["endpoint"] = endpoint
        return cls(
            source_type=f"api_{api_name}",
            source_url=endpoint,
            data=response_data,
            metadata=meta,
        )

    @classmethod
    def from_user_input(
        cls,
        input_data: dict[str, Any],
        source_description: Optional[str] = None,
    ) -> "Evidence":
        """Factory method para crear evidencia desde input del usuario.

        Args:
            input_data: Datos proporcionados por el usuario.
            source_description: Descripción de la fuente.

        Returns:
            Evidence: Instancia de Evidence.
        """
        metadata = {}
        if source_description:
            metadata["source_description"] = source_description
        return cls(
            source_type="user_input",
            data=input_data,
            metadata=metadata,
        )

    def __str__(self) -> str:
        """Representación string de la evidencia.

        Returns:
            str: Representación legible de la evidencia.
        """
        url_str = f" ({self.source_url})" if self.source_url else ""
        return f"Evidence[{self.source_type}]{url_str} - {self.size_bytes} bytes"

    def __hash__(self) -> int:
        """Hash basado en evidence_id para uso en sets/dicts.

        Returns:
            int: Hash del evidence_id.
        """
        return hash(self.evidence_id)

    def __eq__(self, other: object) -> bool:
        """Comparación de igualdad basada en evidence_id.

        Args:
            other: Otro objeto a comparar.

        Returns:
            bool: True si son iguales.
        """
        if not isinstance(other, Evidence):
            return NotImplemented
        return self.evidence_id == other.evidence_id
