"""
Contradiction Engine - Fase 2

Sistema de detección de conflictos entre claims con clasificación
HARD (bloquea exportación) y SOFT (incluye disclaimer).

Uso:
    engine = ContradictionEngine()
    conflicts = engine.detect_conflicts(claims)
    if engine.has_hard_conflicts(claims):
        report = engine.generate_conflict_report(conflicts)
"""

import re
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set


class ConflictType(Enum):
    """Tipo de conflicto detectado."""
    HARD = "hard"  # Bloquea exportación
    SOFT = "soft"  # Incluye disclaimer


@dataclass
class Claim:
    """Representa una afirmación/claim del sistema."""
    claim_id: uuid.UUID
    category: str
    message: str
    confidence: float
    evidence_excerpt: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el claim a diccionario."""
        return {
            "claim_id": str(self.claim_id),
            "category": self.category,
            "message": self.message,
            "confidence": self.confidence,
            "evidence_excerpt": self.evidence_excerpt,
            "metadata": self.metadata,
        }


@dataclass
class Conflict:
    """Representa un conflicto detectado entre dos claims."""
    conflict_id: uuid.UUID
    conflict_type: ConflictType
    claim_a_id: uuid.UUID
    claim_b_id: uuid.UUID
    description: str
    field: str
    resolution_hint: str

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el conflicto a diccionario."""
        return {
            "conflict_id": str(self.conflict_id),
            "conflict_type": self.conflict_type.value,
            "claim_a_id": str(self.claim_a_id),
            "claim_b_id": str(self.claim_b_id),
            "description": self.description,
            "field": self.field,
            "resolution_hint": self.resolution_hint,
        }


class ContradictionEngine:
    """
    Motor de detección de conflictos entre claims.

    Detecta contradicciones entre afirmaciones del sistema y las clasifica
    como HARD (bloquean exportación) o SOFT (requieren disclaimer).
    """

    # Keywords para detección de presencia/ausencia
    PRESENCE_KEYWORDS = [
        "detectado", "encontrado", "presente", "existe", "visible",
        "registrado", "implementado", "activo", "disponible"
    ]
    ABSENCE_KEYWORDS = [
        "no detectado", "no encontrado", "ausente", "no existe", "no visible",
        "no registrado", "no implementado", "inactivo", "falta", "sin ",
        "missing", "not found", "no presente"
    ]

    # Campos de alta importancia
    HIGH_IMPORTANCE_FIELDS = [
        "schema_presence", "whatsapp_presence", "gbp_presence",
        "performance_severity", "financial_data"
    ]

    # Reglas HARD: Bloquean exportación
    HARD_CONFLICT_RULES: List[Callable[[List[Claim]], List[Conflict]]] = []

    # Reglas SOFT: Requieren disclaimer
    SOFT_CONFLICT_RULES: List[Callable[[List[Claim]], List[Conflict]]] = []

    def __init__(self):
        """Inicializa el motor y registra las reglas."""
        self._register_hard_rules()
        self._register_soft_rules()

    def _register_hard_rules(self):
        """Registra todas las reglas HARD."""
        self.HARD_CONFLICT_RULES = [
            self._schema_presence_conflict,
            self._whatsapp_verified_not_visible,
            self._gbp_exists_not_registered,
            self._performance_severity_mismatch,
            self._whatsapp_number_mismatch,
        ]

    def _register_soft_rules(self):
        """Registra todas las reglas SOFT."""
        self.SOFT_CONFLICT_RULES = [
            self._low_confidence_high_importance,
            self._benchmark_vs_actual_pending,
            self._confidence_gap_significant,
        ]

    @staticmethod
    def _extract_phone(text: str) -> Optional[str]:
        """
        Extrae número de teléfono del texto.

        Args:
            text: Texto que puede contener número de teléfono

        Returns:
            Número de teléfono normalizado o None
        """
        if not text:
            return None

        # Patrones comunes de teléfono
        patterns = [
            r'(?:\+?34\s?)?(?:6\d{8}|7\d{8}|8\d{8}|9\d{8})',  # España
            r'(?:\+?1\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}',  # USA
            r'\+?\d{1,4}[\s.-]?\d{1,4}[\s.-]?\d{1,4}[\s.-]?\d{1,4}',  # Genérico
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                # Normalizar: quitar espacios, guiones, paréntesis
                phone = re.sub(r'[\s\-\(\).]', '', match.group())
                return phone

        return None

    def _schema_presence_conflict(self, claims: List[Claim]) -> List[Conflict]:
        """
        Detecta si Schema está marcado como existente y no existente simultáneamente.
        """
        conflicts = []
        schema_claims = [c for c in claims if "schema" in c.category.lower()]

        present = []
        absent = []

        for claim in schema_claims:
            msg_lower = claim.message.lower()
            if any(kw in msg_lower for kw in self.PRESENCE_KEYWORDS):
                present.append(claim)
            elif any(kw in msg_lower for kw in self.ABSENCE_KEYWORDS):
                absent.append(claim)

        for p_claim in present:
            for a_claim in absent:
                conflict = Conflict(
                    conflict_id=uuid.uuid4(),
                    conflict_type=ConflictType.HARD,
                    claim_a_id=p_claim.claim_id,
                    claim_b_id=a_claim.claim_id,
                    description=f"Schema marcado como existente y no existente: '{p_claim.message}' vs '{a_claim.message}'",
                    field="schema_presence",
                    resolution_hint="Verificar manualmente la presencia de Schema.org en el sitio web",
                )
                conflicts.append(conflict)

        return conflicts

    def _whatsapp_verified_not_visible(self, claims: List[Claim]) -> List[Conflict]:
        """
        Detecta WhatsApp VERIFIED pero marcado como no visible.
        """
        conflicts = []
        whatsapp_claims = [c for c in claims if "whatsapp" in c.category.lower()]

        verified = []
        not_visible = []

        for claim in whatsapp_claims:
            msg_lower = claim.message.lower()
            # Verificar si está verificado (alta confianza)
            if claim.confidence >= 0.9 and ("verified" in msg_lower or "verificado" in msg_lower):
                verified.append(claim)
            # Verificar si está marcado como no visible
            elif any(kw in msg_lower for kw in ["no visible", "no detectado", "ausente", "falta"]):
                not_visible.append(claim)

        for v_claim in verified:
            for nv_claim in not_visible:
                conflict = Conflict(
                    conflict_id=uuid.uuid4(),
                    conflict_type=ConflictType.HARD,
                    claim_a_id=v_claim.claim_id,
                    claim_b_id=nv_claim.claim_id,
                    description=f"WhatsApp VERIFIED (confianza {v_claim.confidence}) pero marcado como no visible",
                    field="whatsapp_visibility",
                    resolution_hint="Revisar si el botón WhatsApp está realmente visible en la página",
                )
                conflicts.append(conflict)

        return conflicts

    def _gbp_exists_not_registered(self, claims: List[Claim]) -> List[Conflict]:
        """
        Detecta si GBP existe pero está marcado como no registrado.
        """
        conflicts = []
        gbp_claims = [c for c in claims if "gbp" in c.category.lower() or "business" in c.category.lower()]

        exists = []
        not_registered = []

        for claim in gbp_claims:
            msg_lower = claim.message.lower()
            if any(kw in msg_lower for kw in ["existe", "encontrado", "detectado", "activo"]):
                exists.append(claim)
            elif any(kw in msg_lower for kw in ["no registrado", "no existe", "ausente", "falta"]):
                not_registered.append(claim)

        for e_claim in exists:
            for nr_claim in not_registered:
                conflict = Conflict(
                    conflict_id=uuid.uuid4(),
                    conflict_type=ConflictType.HARD,
                    claim_a_id=e_claim.claim_id,
                    claim_b_id=nr_claim.claim_id,
                    description=f"GBP existe pero marcado como no registrado: '{e_claim.message}' vs '{nr_claim.message}'",
                    field="gbp_registration",
                    resolution_hint="Verificar estado real del Google Business Profile",
                )
                conflicts.append(conflict)

        return conflicts

    def _performance_severity_mismatch(self, claims: List[Claim]) -> List[Conflict]:
        """
        Detecta severidad inconsistente en métricas de performance.
        """
        conflicts = []
        perf_claims = [c for c in claims if "performance" in c.category.lower() or "speed" in c.category.lower()]

        # Buscar claims con severidades diferentes
        severities = {}
        for claim in perf_claims:
            msg_lower = claim.message.lower()
            # Extraer severidad del mensaje
            for level in ["critical", "crítico", "high", "alto", "medium", "medio", "low", "bajo"]:
                if level in msg_lower:
                    if level not in severities:
                        severities[level] = []
                    severities[level].append(claim)
                    break

        # Si hay múltiples severidades para el mismo campo, es un conflicto
        severity_keys = list(severities.keys())
        for i, sev_a in enumerate(severity_keys):
            for sev_b in severity_keys[i + 1:]:
                # Mapear a valores numéricos
                severity_values = {
                    "critical": 4, "crítico": 4,
                    "high": 3, "alto": 3,
                    "medium": 2, "medio": 2,
                    "low": 1, "bajo": 1,
                }
                val_a = severity_values.get(sev_a, 0)
                val_b = severity_values.get(sev_b, 0)

                if abs(val_a - val_b) >= 2:  # Diferencia significativa
                    for claim_a in severities[sev_a]:
                        for claim_b in severities[sev_b]:
                            conflict = Conflict(
                                conflict_id=uuid.uuid4(),
                                conflict_type=ConflictType.HARD,
                                claim_a_id=claim_a.claim_id,
                                claim_b_id=claim_b.claim_id,
                                description=f"Severidad inconsistente: {sev_a} vs {sev_b}",
                                field="performance_severity",
                                resolution_hint="Revisar métricas de performance para confirmar severidad real",
                            )
                            conflicts.append(conflict)

        return conflicts

    def _whatsapp_number_mismatch(self, claims: List[Claim]) -> List[Conflict]:
        """
        Detecta diferentes números de WhatsApp en claims relacionados.
        """
        conflicts = []
        whatsapp_claims = [c for c in claims if "whatsapp" in c.category.lower()]

        # Extraer teléfonos de cada claim
        phones = {}
        for claim in whatsapp_claims:
            phone = self._extract_phone(claim.message)
            if phone:
                if phone not in phones:
                    phones[phone] = []
                phones[phone].append(claim)

        # Si hay más de un número diferente, es un conflicto
        phone_numbers = list(phones.keys())
        if len(phone_numbers) > 1:
            for i, phone_a in enumerate(phone_numbers):
                for phone_b in phone_numbers[i + 1:]:
                    for claim_a in phones[phone_a]:
                        for claim_b in phones[phone_b]:
                            conflict = Conflict(
                                conflict_id=uuid.uuid4(),
                                conflict_type=ConflictType.HARD,
                                claim_a_id=claim_a.claim_id,
                                claim_b_id=claim_b.claim_id,
                                description=f"Números de WhatsApp diferentes detectados: {phone_a} vs {phone_b}",
                                field="whatsapp_number",
                                resolution_hint="Verificar cuál es el número de WhatsApp correcto del hotel",
                            )
                            conflicts.append(conflict)

        return conflicts

    def _low_confidence_high_importance(self, claims: List[Claim]) -> List[Conflict]:
        """
        Detecta claims importantes con baja confianza.
        """
        conflicts = []

        for claim in claims:
            if claim.category in self.HIGH_IMPORTANCE_FIELDS and claim.confidence < 0.7:
                conflict = Conflict(
                    conflict_id=uuid.uuid4(),
                    conflict_type=ConflictType.SOFT,
                    claim_a_id=claim.claim_id,
                    claim_b_id=claim.claim_id,  # Auto-conflicto
                    description=f"Claim importante '{claim.category}' con baja confianza ({claim.confidence:.2f})",
                    field=claim.category,
                    resolution_hint="Recolectar más evidencia para aumentar confianza",
                )
                conflicts.append(conflict)

        return conflicts

    def _benchmark_vs_actual_pending(self, claims: List[Claim]) -> List[Conflict]:
        """
        Detecta uso de benchmark cuando hay dato real pendiente.
        """
        conflicts = []

        # Buscar claims que mencionen benchmark
        benchmark_claims = [
            c for c in claims
            if "benchmark" in c.message.lower() or c.metadata.get("source") == "benchmark"
        ]

        for b_claim in benchmark_claims:
            # Verificar si hay un claim relacionado con dato real pendiente
            field = b_claim.category.replace("_benchmark", "")
            related_claims = [c for c in claims if field in c.category and c != b_claim]

            for r_claim in related_claims:
                if any(kw in r_claim.message.lower() for kw in ["pendiente", "pending", "no disponible", "estimado"]):
                    conflict = Conflict(
                        conflict_id=uuid.uuid4(),
                        conflict_type=ConflictType.SOFT,
                        claim_a_id=b_claim.claim_id,
                        claim_b_id=r_claim.claim_id,
                        description=f"Uso de benchmark para '{field}' mientras dato real está pendiente",
                        field=field,
                        resolution_hint="Obtener dato real para reemplazar estimación por benchmark",
                    )
                    conflicts.append(conflict)

        return conflicts

    def _confidence_gap_significant(self, claims: List[Claim]) -> List[Conflict]:
        """
        Detecta diferencia > 0.3 entre claims relacionados.
        """
        conflicts = []

        # Agrupar claims por categoría relacionada
        categories: Dict[str, List[Claim]] = {}
        for claim in claims:
            cat = claim.category.split("_")[0]  # Base category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(claim)

        # Buscar gaps significativos
        for cat, cat_claims in categories.items():
            if len(cat_claims) < 2:
                continue

            for i, claim_a in enumerate(cat_claims):
                for claim_b in cat_claims[i + 1:]:
                    gap = abs(claim_a.confidence - claim_b.confidence)
                    if gap > 0.3:
                        conflict = Conflict(
                            conflict_id=uuid.uuid4(),
                            conflict_type=ConflictType.SOFT,
                            claim_a_id=claim_a.claim_id,
                            claim_b_id=claim_b.claim_id,
                            description=f"Diferencia de confianza significativa ({gap:.2f}) en '{cat}'",
                            field=cat,
                            resolution_hint="Investigar por qué hay diferencia de certeza entre fuentes",
                        )
                        conflicts.append(conflict)

        return conflicts

    def detect_conflicts(self, claims: List[Claim]) -> List[Conflict]:
        """
        Detecta todos los conflictos (HARD y SOFT) en los claims.

        Args:
            claims: Lista de claims a analizar

        Returns:
            Lista de todos los conflictos detectados
        """
        all_conflicts: List[Conflict] = []

        # Ejecutar reglas HARD
        for rule in self.HARD_CONFLICT_RULES:
            try:
                conflicts = rule(claims)
                all_conflicts.extend(conflicts)
            except Exception as e:
                # Log error pero no fallar completamente
                print(f"Error en regla HARD {rule.__name__}: {e}")

        # Ejecutar reglas SOFT
        for rule in self.SOFT_CONFLICT_RULES:
            try:
                conflicts = rule(claims)
                all_conflicts.extend(conflicts)
            except Exception as e:
                print(f"Error en regla SOFT {rule.__name__}: {e}")

        return all_conflicts

    def detect_hard_conflicts(self, claims: List[Claim]) -> List[Conflict]:
        """
        Detecta solo conflictos HARD.

        Args:
            claims: Lista de claims a analizar

        Returns:
            Lista de conflictos HARD
        """
        conflicts: List[Conflict] = []

        for rule in self.HARD_CONFLICT_RULES:
            try:
                conflicts.extend(rule(claims))
            except Exception as e:
                print(f"Error en regla HARD {rule.__name__}: {e}")

        return conflicts

    def detect_soft_conflicts(self, claims: List[Claim]) -> List[Conflict]:
        """
        Detecta solo conflictos SOFT.

        Args:
            claims: Lista de claims a analizar

        Returns:
            Lista de conflictos SOFT
        """
        conflicts: List[Conflict] = []

        for rule in self.SOFT_CONFLICT_RULES:
            try:
                conflicts.extend(rule(claims))
            except Exception as e:
                print(f"Error en regla SOFT {rule.__name__}: {e}")

        return conflicts

    def has_hard_conflicts(self, claims: List[Claim]) -> bool:
        """
        Verifica si hay al menos un conflicto HARD.

        Args:
            claims: Lista de claims a analizar

        Returns:
            True si hay conflictos HARD
        """
        return len(self.detect_hard_conflicts(claims)) > 0

    def _generate_recommendations(self, conflicts: List[Conflict]) -> List[str]:
        """
        Genera recomendaciones basadas en los conflictos.

        Args:
            conflicts: Lista de conflictos detectados

        Returns:
            Lista de recomendaciones
        """
        recommendations: List[str] = []
        hard_count = sum(1 for c in conflicts if c.conflict_type == ConflictType.HARD)
        soft_count = sum(1 for c in conflicts if c.conflict_type == ConflictType.SOFT)

        if hard_count > 0:
            recommendations.append(
                f"⚠️ Se detectaron {hard_count} conflictos HARD que deben resolverse antes de exportar assets"
            )

        if soft_count > 0:
            recommendations.append(
                f"ℹ️ Se detectaron {soft_count} conflictos SOFT - se incluirán disclaimers en los assets"
            )

        # Recomendaciones específicas por campo
        fields_with_conflicts = set(c.field for c in conflicts)
        for field in fields_with_conflicts:
            field_conflicts = [c for c in conflicts if c.field == field]
            if field_conflicts:
                hard_in_field = any(c.conflict_type == ConflictType.HARD for c in field_conflicts)
                if hard_in_field:
                    recommendations.append(f"→ Priorizar resolución de conflictos en campo '{field}'")

        if not recommendations:
            recommendations.append("✅ No se detectaron conflictos")

        return recommendations

    def generate_conflict_report(self, conflicts: List[Conflict]) -> Dict[str, Any]:
        """
        Genera un reporte estructurado de conflictos.

        Args:
            conflicts: Lista de conflictos detectados

        Returns:
            Diccionario con el reporte completo
        """
        hard_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.HARD]
        soft_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.SOFT]

        # Agrupar por campo
        conflicts_by_field: Dict[str, List[Dict]] = {}
        for conflict in conflicts:
            if conflict.field not in conflicts_by_field:
                conflicts_by_field[conflict.field] = []
            conflicts_by_field[conflict.field].append(conflict.to_dict())

        report = {
            "summary": {
                "total_conflicts": len(conflicts),
                "hard_conflicts": len(hard_conflicts),
                "soft_conflicts": len(soft_conflicts),
                "fields_affected": list(conflicts_by_field.keys()),
                "can_export": len(hard_conflicts) == 0,
            },
            "hard_conflicts": [c.to_dict() for c in hard_conflicts],
            "soft_conflicts": [c.to_dict() for c in soft_conflicts],
            "conflicts_by_field": conflicts_by_field,
            "recommendations": self._generate_recommendations(conflicts),
        }

        return report

    def get_conflicts_by_field(
        self, conflicts: List[Conflict], field: str
    ) -> List[Conflict]:
        """
        Filtra conflictos por campo específico.

        Args:
            conflicts: Lista de conflictos
            field: Campo a filtrar

        Returns:
            Lista de conflictos del campo especificado
        """
        return [c for c in conflicts if c.field == field]
