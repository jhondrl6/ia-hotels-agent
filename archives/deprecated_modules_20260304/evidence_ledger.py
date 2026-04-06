"""
Evidence Ledger - Sistema de Registro Inmutable de Evidencias

Fase 2: Sistema de evidencias con hash SHA-256 para integridad.
Cada evidencia se almacena con un hash criptográfico que permite
verificar que no ha sido modificada posteriormente.
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import UUID, uuid4


class EvidenceType(Enum):
    """Tipos de evidencia soportados por el sistema."""
    SCHEMA = "schema"
    WHATSAPP = "whatsapp"
    GBP = "gbp"  # Google Business Profile
    PERFORMANCE = "performance"
    METADATA = "metadata"
    CONTENT = "content"


@dataclass
class Evidence:
    """
    Representa una evidencia individual del sistema.
    
    Attributes:
        evidence_id: UUID único de la evidencia
        claim_id: UUID del claim al que pertenece esta evidencia
        source_type: Tipo de fuente (EvidenceType)
        source_url: URL opcional de la fuente
        raw_data: Datos crudos originales
        extracted_value: Valor extraído procesado
        timestamp: Fecha/hora en formato ISO
        collector_version: Versión del colector que capturó la evidencia
    """
    evidence_id: UUID = field(default_factory=uuid4)
    claim_id: UUID = field(default_factory=uuid4)
    source_type: str = ""
    source_url: Optional[str] = None
    raw_data: Any = None
    extracted_value: Any = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    collector_version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la evidencia a diccionario serializable."""
        return {
            "evidence_id": str(self.evidence_id),
            "claim_id": str(self.claim_id),
            "source_type": self.source_type,
            "source_url": self.source_url,
            "raw_data": self.raw_data,
            "extracted_value": self.extracted_value,
            "timestamp": self.timestamp,
            "collector_version": self.collector_version
        }


class EvidenceLedger:
    """
    Libro mayor inmutable de evidencias con verificación de integridad.
    
    Almacena evidencias indexadas por claim_id con hash SHA-256
    para garantizar que no han sido modificadas.
    
    Attributes:
        _storage: Diccionario interno de evidencias por claim_id
        _hashes: Diccionario de hashes de integridad por claim_id
        _evidence_to_claim: Mapeo de evidence_id a claim_id
    """

    def __init__(self):
        """Inicializa el ledger vacío."""
        self._storage: Dict[UUID, Evidence] = {}
        self._hashes: Dict[UUID, str] = {}
        self._evidence_to_claim: Dict[UUID, UUID] = {}
        self._source_index: Dict[str, Set[UUID]] = {}

    def _calculate_hash(self, evidence: Evidence) -> str:
        """
        Calcula el hash SHA-256 de una evidencia.
        
        Args:
            evidence: Evidencia a hashear
            
        Returns:
            Hash hexadecimal de 64 caracteres
        """
        data = evidence.to_dict()
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

    def store(self, claim_id: UUID, evidence: Evidence) -> str:
        """
        Almacena una evidencia y genera su hash de integridad.
        
        Args:
            claim_id: UUID del claim asociado
            evidence: Evidencia a almacenar
            
        Returns:
            Hash SHA-256 de la evidencia almacenada
        """
        evidence.claim_id = claim_id

        if evidence.evidence_id in self._evidence_to_claim:
            old_claim_id = self._evidence_to_claim[evidence.evidence_id]
            if old_claim_id in self._storage:
                del self._storage[old_claim_id]
                del self._hashes[old_claim_id]

        evidence_hash = self._calculate_hash(evidence)

        self._storage[claim_id] = evidence
        self._hashes[claim_id] = evidence_hash
        self._evidence_to_claim[evidence.evidence_id] = claim_id

        source_key = evidence.source_type.lower()
        if source_key not in self._source_index:
            self._source_index[source_key] = set()
        self._source_index[source_key].add(claim_id)

        return evidence_hash

    def retrieve(self, claim_id: UUID) -> Optional[Evidence]:
        """
        Recupera una evidencia por su claim_id.
        
        Args:
            claim_id: UUID del claim
            
        Returns:
            Evidencia o None si no existe
        """
        return self._storage.get(claim_id)

    def verify_integrity(self, claim_id: UUID) -> bool:
        """
        Verifica que una evidencia no haya sido modificada.
        
        Args:
            claim_id: UUID del claim a verificar
            
        Returns:
            True si la evidencia es íntegra, False si fue modificada o no existe
        """
        if claim_id not in self._storage:
            return False

        stored_evidence = self._storage[claim_id]
        stored_hash = self._hashes.get(claim_id)

        if not stored_hash:
            return False

        current_hash = self._calculate_hash(stored_evidence)
        return current_hash == stored_hash

    def get_all(self) -> Dict[UUID, Evidence]:
        """
        Retorna una copia de todas las evidencias almacenadas.
        
        Returns:
            Diccionario con copia del almacenamiento
        """
        return dict(self._storage)

    def get_by_source(self, source_type: str) -> List[Evidence]:
        """
        Recupera evidencias filtradas por tipo de fuente.
        
        Args:
            source_type: Tipo de fuente a filtrar (case-insensitive)
            
        Returns:
            Lista de evidencias del tipo especificado
        """
        source_key = source_type.lower()
        claim_ids = self._source_index.get(source_key, set())
        return [self._storage[cid] for cid in claim_ids if cid in self._storage]

    def get_by_claim_ids(self, claim_ids: List[UUID]) -> Dict[UUID, Evidence]:
        """
        Recupera múltiples evidencias por sus claim_ids.
        
        Args:
            claim_ids: Lista de UUIDs de claims
            
        Returns:
            Diccionario de evidencias encontradas
        """
        result = {}
        for claim_id in claim_ids:
            evidence = self.retrieve(claim_id)
            if evidence:
                result[claim_id] = evidence
        return result

    def delete(self, claim_id: UUID) -> bool:
        """
        Elimina una evidencia del ledger.
        
        Args:
            claim_id: UUID del claim a eliminar
            
        Returns:
            True si se eliminó, False si no existía
        """
        if claim_id not in self._storage:
            return False

        evidence = self._storage[claim_id]

        del self._storage[claim_id]
        del self._hashes[claim_id]

        if evidence.evidence_id in self._evidence_to_claim:
            del self._evidence_to_claim[evidence.evidence_id]

        source_key = evidence.source_type.lower()
        if source_key in self._source_index:
            self._source_index[source_key].discard(claim_id)

        return True

    def clear(self) -> None:
        """Elimina todas las evidencias del ledger."""
        self._storage.clear()
        self._hashes.clear()
        self._evidence_to_claim.clear()
        self._source_index.clear()

    def count(self) -> int:
        """
        Retorna la cantidad de evidencias almacenadas.
        
        Returns:
            Número entero de evidencias
        """
        return len(self._storage)

    def get_hash(self, claim_id: UUID) -> Optional[str]:
        """
        Obtiene el hash almacenado de una evidencia.
        
        Args:
            claim_id: UUID del claim
            
        Returns:
            Hash hexadecimal o None si no existe
        """
        return self._hashes.get(claim_id)

    def get_stats(self) -> Dict[str, Any]:
        """
        Genera estadísticas del ledger.
        
        Returns:
            Diccionario con estadísticas
        """
        sources = {}
        for source_type, claim_ids in self._source_index.items():
            sources[source_type] = len(claim_ids)

        integrity_count = sum(
            1 for claim_id in self._storage
            if self.verify_integrity(claim_id)
        )

        return {
            "total_evidence": self.count(),
            "by_source": sources,
            "integrity_verified": integrity_count,
            "integrity_failed": self.count() - integrity_count
        }
