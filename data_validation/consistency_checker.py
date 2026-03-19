"""
Consistency Checker - Validador de coherencia interna y cruzada.

Fase 2: Validación de consistencia entre claims y documentos.
"""

from dataclasses import dataclass, field
from typing import List, Any, Tuple, Optional, Dict
from uuid import UUID, uuid4
from datetime import datetime
import json


@dataclass
class ConsistencyReport:
    """
    Reporte de validación de consistencia.
    
    Attributes:
        is_consistent: Indica si el assessment es consistente
        inconsistencies: Lista de inconsistencias detectadas
        recommendations: Lista de recomendaciones para resolver
        hard_conflicts_count: Número de conflictos hard
        soft_conflicts_count: Número de conflictos soft
        confidence_score: Score de confianza (0.0 - 1.0)
    """
    is_consistent: bool
    inconsistencies: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    hard_conflicts_count: int = 0
    soft_conflicts_count: int = 0
    confidence_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el reporte a diccionario."""
        return {
            "is_consistent": self.is_consistent,
            "inconsistencies": self.inconsistencies,
            "recommendations": self.recommendations,
            "hard_conflicts_count": self.hard_conflicts_count,
            "soft_conflicts_count": self.soft_conflicts_count,
            "confidence_score": round(self.confidence_score, 4),
            "summary": self._generate_summary()
        }
    
    def _generate_summary(self) -> str:
        """Genera resumen del reporte."""
        total_conflicts = self.hard_conflicts_count + self.soft_conflicts_count
        if total_conflicts == 0:
            return "Assessment completamente consistente"
        elif self.hard_conflicts_count > 0:
            return f"{self.hard_conflicts_count} conflictos HARD detectados - requieren atención"
        else:
            return f"{self.soft_conflicts_count} conflictos SOFT - revisar recomendaciones"


@dataclass
class CanonicalAssessment:
    """
    Assessment canónico para validación.
    
    Attributes:
        assessment_id: UUID único del assessment
        hotel_name: Nombre del hotel
        claims: Lista de claims extraídos
        generated_at: Timestamp de generación
        version: Versión del formato
    """
    assessment_id: UUID
    hotel_name: str
    claims: List[Any] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0"
    
    def __post_init__(self):
        """Validación post-inicialización."""
        if isinstance(self.assessment_id, str):
            self.assessment_id = UUID(self.assessment_id)


class ConsistencyChecker:
    """
    Validador de coherencia para assessments.
    
    Realiza validaciones internas y cruzadas entre documentos,
    detectando conflictos hard y soft.
    """
    
    CHECKS: List[str] = [
        "whatsapp_consistency",
        "gbp_consistency",
        "schema_consistency",
        "adr_validation",
        "location_verification",
        "contact_data_integrity"
    ]
    
    def __init__(self, contradiction_engine: Optional[Any] = None):
        """
        Inicializa el checker con engine opcional.
        
        Args:
            contradiction_engine: Instancia de ContradictionEngine (opcional)
        """
        self.engine = contradiction_engine
        self._load_engine()
    
    def _load_engine(self) -> None:
        """Carga el ContradictionEngine si no fue proporcionado."""
        if self.engine is None:
            try:
                from data_validation.contradiction_engine import ContradictionEngine
                self.engine = ContradictionEngine()
            except ImportError:
                self.engine = None

    def _convert_claims_to_objects(self, claims: List[Any]) -> List[Any]:
        """
        Convierte claims de diccionario a objetos Claim si es necesario.

        Args:
            claims: Lista de claims (pueden ser dict o Claim objects)

        Returns:
            Lista de claims como objetos Claim
        """
        from data_validation.contradiction_engine import Claim as EngineClaim
        from uuid import UUID

        converted = []
        for claim in claims:
            if isinstance(claim, EngineClaim):
                converted.append(claim)
            elif isinstance(claim, dict):
                # Convertir diccionario a Claim
                claim_id = claim.get('claim_id') or claim.get('id') or uuid4()
                if isinstance(claim_id, str):
                    claim_id = UUID(claim_id)

                converted.append(EngineClaim(
                    claim_id=claim_id,
                    category=claim.get('category', 'unknown'),
                    message=claim.get('message', claim.get('value', '')),
                    confidence=float(claim.get('confidence', 0.5)),
                    evidence_excerpt=claim.get('evidence_excerpt', claim.get('excerpt', '')),
                    metadata=claim.get('metadata', {})
                ))
            else:
                # Intentar extraer atributos del objeto
                converted.append(EngineClaim(
                    claim_id=getattr(claim, 'claim_id', uuid4()),
                    category=getattr(claim, 'category', 'unknown'),
                    message=getattr(claim, 'message', str(claim)),
                    confidence=float(getattr(claim, 'confidence', 0.5)),
                    evidence_excerpt=getattr(claim, 'evidence_excerpt', ''),
                    metadata=getattr(claim, 'metadata', {})
                ))
        return converted

    def check_assessment_consistency(self, assessment: CanonicalAssessment) -> ConsistencyReport:
        """
        Valida consistencia interna de un assessment.
        
        Args:
            assessment: Assessment a validar
            
        Returns:
            ConsistencyReport con resultado de validación
        """
        inconsistencies: List[str] = []
        recommendations: List[str] = []
        hard_conflicts = 0
        soft_conflicts = 0
        
        # Check WhatsApp consistency
        whatsapp_ok = self._check_whatsapp_consistency(assessment.claims)
        if not whatsapp_ok:
            inconsistencies.append("WhatsApp: inconsistencia en número o formato")
            recommendations.append("Verificar número WhatsApp en web y GBP")
            soft_conflicts += 1  # WhatsApp es SOFT

        # Check GBP consistency
        gbp_ok = self._check_gbp_consistency(assessment.claims)
        if not gbp_ok:
            inconsistencies.append("GBP: datos inconsistentes entre fuentes")
            recommendations.append("Sincronizar información en Google Business Profile")
            hard_conflicts += 1  # GBP es HARD

        # Check Schema consistency
        schema_ok = self._check_schema_consistency(assessment.claims)
        if not schema_ok:
            inconsistencies.append("Schema: estructura de datos inválida")
            recommendations.append("Revisar implementación de Schema.org")
            soft_conflicts += 1  # Schema es SOFT
        
        # Usar engine si está disponible
        if self.engine and hasattr(self.engine, 'detect_conflicts'):
            try:
                # Convertir claims a objetos si es necesario
                converted_claims = self._convert_claims_to_objects(assessment.claims)
                engine_conflicts = self.engine.detect_conflicts(converted_claims)
                for conflict in engine_conflicts:
                    # Conflict es un objeto, no un diccionario
                    is_hard = (hasattr(conflict, 'conflict_type') and 
                              conflict.conflict_type.value == 'hard')
                    desc = getattr(conflict, 'description', str(conflict))
                    field = getattr(conflict, 'field', 'unknown')
                    hint = getattr(conflict, 'resolution_hint', '')
                    
                    if is_hard:
                        hard_conflicts += 1
                        inconsistencies.append(f"[HARD] {field}: {desc}")
                    else:
                        soft_conflicts += 1
                        inconsistencies.append(f"[SOFT] {field}: {desc}")
                    
                    if hint:
                        recommendations.append(hint)
            except Exception as e:
                # Silenciar errores del engine pero podríamos logear
                pass
        
        # Calcular score de confianza
        confidence = self._calculate_confidence_score(
            assessment.claims, 
            hard_conflicts + soft_conflicts
        )
        
        # Determinar consistencia
        is_consistent = hard_conflicts == 0 and confidence >= 0.5
        
        return ConsistencyReport(
            is_consistent=is_consistent,
            inconsistencies=inconsistencies,
            recommendations=list(set(recommendations)),  # Eliminar duplicados
            hard_conflicts_count=hard_conflicts,
            soft_conflicts_count=soft_conflicts,
            confidence_score=confidence
        )
    
    def check_cross_document_consistency(
        self, 
        doc1_claims: List[Any], 
        doc2_claims: List[Any]
    ) -> ConsistencyReport:
        """
        Valida consistencia entre dos documentos.
        
        Args:
            doc1_claims: Claims del primer documento
            doc2_claims: Claims del segundo documento
            
        Returns:
            ConsistencyReport con resultado de comparación
        """
        inconsistencies: List[str] = []
        recommendations: List[str] = []
        hard_conflicts = 0
        soft_conflicts = 0
        
        # Comparar claims comunes
        doc1_dict = {self._get_claim_key(c): c for c in doc1_claims}
        doc2_dict = {self._get_claim_key(c): c for c in doc2_claims}
        
        common_keys = set(doc1_dict.keys()) & set(doc2_dict.keys())
        
        for key in common_keys:
            claim1 = doc1_dict[key]
            claim2 = doc2_dict[key]
            
            if not self._claims_match(claim1, claim2):
                severity = self._determine_conflict_severity(claim1, claim2)
                msg = f"Conflicto en '{key}': '{self._get_claim_value(claim1)}' vs '{self._get_claim_value(claim2)}'"
                
                if severity == 'hard':
                    hard_conflicts += 1
                    inconsistencies.append(f"[HARD] {msg}")
                else:
                    soft_conflicts += 1
                    inconsistencies.append(f"[SOFT] {msg}")
                
                recommendations.append(f"Reconciliar valor de '{key}' entre documentos")
        
        # Claims únicos
        unique_to_doc1 = set(doc1_dict.keys()) - set(doc2_dict.keys())
        unique_to_doc2 = set(doc2_dict.keys()) - set(doc1_dict.keys())
        
        if unique_to_doc1:
            soft_conflicts += 1
            inconsistencies.append(f"Claims únicos en doc1: {', '.join(unique_to_doc1)}")
            recommendations.append("Considerar sincronizar claims faltantes en doc2")
        
        if unique_to_doc2:
            soft_conflicts += 1
            inconsistencies.append(f"Claims únicos en doc2: {', '.join(unique_to_doc2)}")
            recommendations.append("Considerar sincronizar claims faltantes en doc1")
        
        all_claims = list(doc1_claims) + list(doc2_claims)
        confidence = self._calculate_confidence_score(
            all_claims,
            hard_conflicts + soft_conflicts
        )
        
        is_consistent = hard_conflicts == 0 and confidence >= 0.5
        
        return ConsistencyReport(
            is_consistent=is_consistent,
            inconsistencies=inconsistencies,
            recommendations=list(set(recommendations)),
            hard_conflicts_count=hard_conflicts,
            soft_conflicts_count=soft_conflicts,
            confidence_score=confidence
        )
    
    def can_export(self, assessment: CanonicalAssessment) -> Tuple[bool, str]:
        """
        Determina si un assessment puede ser exportado.
        
        Args:
            assessment: Assessment a evaluar
            
        Returns:
            Tuple (puede_exportar, mensaje)
        """
        report = self.check_assessment_consistency(assessment)
        
        # HARD conflicts bloquean export
        if report.hard_conflicts_count > 0:
            return (
                False,
                f"BLOQUEADO: {report.hard_conflicts_count} conflictos HARD detectados - "
                f"{report.inconsistencies[0] if report.inconsistencies else 'Requiere corrección'}"
            )
        
        # Score muy bajo bloquea
        if report.confidence_score < 0.5:
            return (
                False,
                f"BLOQUEADO: Score de confianza {report.confidence_score:.2f} < 0.5 - "
                f"Revisar datos de entrada"
            )
        
        # Muchos SOFT conflicts generan advertencia
        if report.soft_conflicts_count > 5:
            return (
                True,
                f"ADVERTENCIA: {report.soft_conflicts_count} conflictos SOFT detectados - "
                f"Export posible pero revisar recomendaciones"
            )
        
        # Todo OK
        return (
            True,
            f"OK: Assessment consistente (confianza: {report.confidence_score:.2f})"
        )
    
    def _check_whatsapp_consistency(self, claims: List[Any]) -> bool:
        """
        Verifica consistencia de datos de WhatsApp.
        
        Args:
            claims: Lista de claims a verificar
            
        Returns:
            True si es consistente, False en caso contrario
        """
        whatsapp_claims = [
            c for c in claims 
            if self._get_claim_key(c).lower() in ['whatsapp', 'whatsapp_number', 'phone_whatsapp']
        ]
        
        if not whatsapp_claims:
            return True  # No hay claims de WhatsApp
        
        # Extraer valores
        values = [self._get_claim_value(c) for c in whatsapp_claims]
        values = [v for v in values if v is not None]
        
        if not values:
            return True
        
        # Normalizar y comparar
        normalized = [self._normalize_phone(str(v)) for v in values]
        return len(set(normalized)) <= 1
    
    def _check_gbp_consistency(self, claims: List[Any]) -> bool:
        """
        Verifica consistencia de Google Business Profile.
        
        Args:
            claims: Lista de claims a verificar
            
        Returns:
            True si es consistente, False en caso contrario
        """
        gbp_claims = [
            c for c in claims
            if 'gbp' in self._get_claim_key(c).lower() or 
               'google_business' in self._get_claim_key(c).lower()
        ]
        
        if len(gbp_claims) < 2:
            return True
        
        # Verificar que no haya datos contradictorios
        ratings = []
        for claim in gbp_claims:
            if 'rating' in self._get_claim_key(claim).lower():
                val = self._get_claim_value(claim)
                if val is not None:
                    try:
                        ratings.append(float(val))
                    except (ValueError, TypeError):
                        pass
        
        # Ratings deben estar en rango válido
        if ratings:
            if any(r < 0 or r > 5 for r in ratings):
                return False
            # Si hay múltiples ratings, no deben diferir mucho
            if len(ratings) > 1 and max(ratings) - min(ratings) > 1.0:
                return False
        
        return True
    
    def _check_schema_consistency(self, claims: List[Any]) -> bool:
        """
        Verifica consistencia de Schema.org.
        
        Args:
            claims: Lista de claims a verificar
            
        Returns:
            True si es consistente, False en caso contrario
        """
        schema_claims = [
            c for c in claims
            if 'schema' in self._get_claim_key(c).lower() or
               '@type' in str(self._get_claim_value(c))
        ]
        
        if not schema_claims:
            return True
        
        # Verificar estructura básica
        required_types = ['Hotel', 'LodgingBusiness']
        has_valid_type = False
        
        for claim in schema_claims:
            val = str(self._get_claim_value(claim)).lower()
            if any(t.lower() in val for t in required_types):
                has_valid_type = True
                break
        
        return has_valid_type or len(schema_claims) == 0
    
    def _calculate_confidence_score(self, claims: List[Any], total_conflicts: int) -> float:
        """
        Calcula score de confianza basado en claims y conflictos.
        
        Args:
            claims: Lista de claims evaluados
            total_conflicts: Número total de conflictos detectados
            
        Returns:
            Score de confianza entre 0.0 y 1.0
        """
        if not claims:
            return 0.5  # Neutral si no hay claims
        
        # Base: 1.0
        base_score = 1.0
        
        # Penalización por conflictos
        conflict_penalty = min(total_conflicts * 0.15, 0.6)
        
        # Penalización por falta de claims verificables
        verifiable_claims = len([c for c in claims if self._is_verifiable(c)])
        coverage_ratio = verifiable_claims / len(claims) if claims else 0
        coverage_penalty = (1 - coverage_ratio) * 0.2
        
        score = base_score - conflict_penalty - coverage_penalty
        return max(0.0, min(1.0, score))
    
    def _get_claim_key(self, claim: Any) -> str:
        """Extrae la clave de un claim."""
        if isinstance(claim, dict):
            return str(claim.get('key', claim.get('field', claim.get('name', 'unknown'))))
        elif hasattr(claim, 'key'):
            return str(claim.key)
        elif hasattr(claim, 'field'):
            return str(claim.field)
        return str(claim)
    
    def _get_claim_value(self, claim: Any) -> Any:
        """Extrae el valor de un claim."""
        if isinstance(claim, dict):
            return claim.get('value', claim.get('data', claim.get('content', None)))
        elif hasattr(claim, 'value'):
            return claim.value
        elif hasattr(claim, 'data'):
            return claim.data
        return claim
    
    def _claims_match(self, claim1: Any, claim2: Any) -> bool:
        """Compara dos claims para determinar si coinciden."""
        val1 = self._get_claim_value(claim1)
        val2 = self._get_claim_value(claim2)
        
        if val1 is None and val2 is None:
            return True
        if val1 is None or val2 is None:
            return False
        
        # Normalizar strings
        if isinstance(val1, str) and isinstance(val2, str):
            return val1.strip().lower() == val2.strip().lower()
        
        # Comparar números con tolerancia
        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            return abs(float(val1) - float(val2)) < 0.01
        
        return str(val1) == str(val2)
    
    def _determine_conflict_severity(self, claim1: Any, claim2: Any) -> str:
        """Determina si un conflicto es hard o soft."""
        key = self._get_claim_key(claim1).lower()
        
        # Conflictos hard: datos críticos del negocio
        hard_fields = [
            'phone', 'telefono', 'email', 'direccion', 'address',
            'hotel_name', 'nombre', 'latitude', 'longitude', 'lat', 'lng'
        ]
        
        if any(field in key for field in hard_fields):
            return 'hard'
        
        return 'soft'
    
    def _normalize_phone(self, phone: str) -> str:
        """Normaliza un número de teléfono para comparación."""
        # Remover todo excepto dígitos
        digits = ''.join(c for c in phone if c.isdigit())
        
        # Si empieza con 52 (México), remover
        if digits.startswith('52') and len(digits) > 10:
            digits = digits[2:]
        
        # Si empieza con 1, remover
        if digits.startswith('1') and len(digits) == 11:
            digits = digits[1:]
        
        return digits[-10:] if len(digits) >= 10 else digits
    
    def _is_verifiable(self, claim: Any) -> bool:
        """Determina si un claim es verificable."""
        key = self._get_claim_key(claim).lower()
        verifiable_types = [
            'phone', 'email', 'address', 'rating', 'price', 'url',
            'whatsapp', 'gbp', 'schema', 'location'
        ]
        return any(t in key for t in verifiable_types)


# Factory function para fácil instanciación
def create_consistency_checker(engine: Optional[Any] = None) -> ConsistencyChecker:
    """
    Factory para crear instancia de ConsistencyChecker.
    
    Args:
        engine: ContradictionEngine opcional
        
    Returns:
        Instancia configurada de ConsistencyChecker
    """
    return ConsistencyChecker(contradiction_engine=engine)