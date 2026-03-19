"""Publication State - Estados de Publicación y Transiciones.

Implementa la máquina de estados para la Fase 5 del flujo v4complete.
Gestiona transiciones entre estados de publicación basado en resultados
de quality gates.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum
from datetime import datetime, timezone


class PublicationState(Enum):
    """Estados posibles de publicación de un assessment.
    
    Estados:
        READY_FOR_CLIENT: Todos los gates pasaron, listo para entrega
        DRAFT_INTERNAL: Falló gate crítico, solo uso interno
        REQUIRES_REVIEW: Solo soft conflicts/warnings, necesita revisión
        BLOCKED: Bloqueado por múltiples fallas críticas
    """
    READY_FOR_CLIENT = "ready_for_client"
    DRAFT_INTERNAL = "draft_internal"
    REQUIRES_REVIEW = "requires_review"
    BLOCKED = "blocked"


@dataclass
class StateTransition:
    """Representa una transición válida entre estados.
    
    Attributes:
        from_state: Estado origen
        to_state: Estado destino
        condition: Condición que permite la transición
        requires_resolution: Lista de issues que deben resolverse
    """
    from_state: PublicationState
    to_state: PublicationState
    condition: str
    requires_resolution: List[str] = field(default_factory=list)


@dataclass
class PublicationStateResult:
    """Resultado de una evaluación de estado de publicación.
    
    Attributes:
        current_state: Estado actual determinado
        previous_state: Estado anterior (si hubo cambio)
        transition_reason: Razón del cambio de estado
        blocking_issues: Lista de issues que bloquean
        improvement_suggestions: Sugerencias para avanzar
        gate_results: Resultados de gates que determinaron estado
        timestamp: Momento de la evaluación
        metadata: Datos adicionales
    """
    current_state: PublicationState
    previous_state: Optional[PublicationState] = None
    transition_reason: str = ""
    blocking_issues: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    gate_results: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_published(self) -> bool:
        """True si el documento puede publicarse al cliente."""
        return self.current_state == PublicationState.READY_FOR_CLIENT
    
    @property
    def is_blocked(self) -> bool:
        """True si está bloqueado por fallas críticas."""
        return self.current_state == PublicationState.BLOCKED
    
    @property
    def can_be_reviewed(self) -> bool:
        """True si puede ser revisado manualmente."""
        return self.current_state in (
            PublicationState.REQUIRES_REVIEW,
            PublicationState.DRAFT_INTERNAL
        )
    
    @property
    def state_changed(self) -> bool:
        """True si hubo cambio de estado."""
        return self.previous_state is not None and self.previous_state != self.current_state
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializa resultado a diccionario."""
        return {
            "current_state": self.current_state.value,
            "previous_state": self.previous_state.value if self.previous_state else None,
            "transition_reason": self.transition_reason,
            "is_published": self.is_published,
            "is_blocked": self.is_blocked,
            "can_be_reviewed": self.can_be_reviewed,
            "state_changed": self.state_changed,
            "blocking_issues": self.blocking_issues,
            "improvement_suggestions": self.improvement_suggestions,
            "gate_results": self.gate_results,
            "timestamp": self.timestamp.isoformat(),
        }
    
    def to_summary(self) -> str:
        """Genera resumen legible del estado."""
        lines = [
            f"Estado: {self.current_state.value.upper()}",
        ]
        
        if self.state_changed:
            lines.append(f"Cambio: {self.previous_state.value} → {self.current_state.value}")
            lines.append(f"Razón: {self.transition_reason}")
        
        if self.blocking_issues:
            lines.append(f"\nIssues bloqueantes ({len(self.blocking_issues)}):")
            for issue in self.blocking_issues[:5]:
                lines.append(f"  • {issue}")
            if len(self.blocking_issues) > 5:
                lines.append(f"  ... y {len(self.blocking_issues) - 5} más")
        
        if self.improvement_suggestions:
            lines.append(f"\nSugerencias:")
            for suggestion in self.improvement_suggestions[:3]:
                lines.append(f"  → {suggestion}")
        
        return "\n".join(lines)


class PublicationStateManager:
    """Gestiona la máquina de estados de publicación.
    
    Responsabilidades:
        - Determinar estado desde resultados de gates
        - Validar transiciones entre estados
        - Proporcionar requisitos para alcanzar estados
        - Generar sugerencias de mejora
    
    Transiciones válidas:
        DRAFT_INTERNAL → REQUIRES_REVIEW (si se resuelven críticos)
        REQUIRES_REVIEW → READY_FOR_CLIENT (si se resuelven warnings)
        Cualquiera → BLOCKED (si empeora)
        READY_FOR_CLIENT → REQUIRES_REVIEW (si cambian gates)
    """
    
    # Umbrales por defecto
    DEFAULT_COHERENCE_THRESHOLD = 0.8
    DEFAULT_EVIDENCE_THRESHOLD = 0.95
    DEFAULT_RECALL_THRESHOLD = 0.90
    DEFAULT_REVIEW_THRESHOLD = 0.5
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Inicializa el manager con configuración.
        
        Args:
            config: Configuración opcional con umbrales
        """
        self.config = config or {}
        self.coherence_threshold = self.config.get(
            "coherence_threshold", 
            self.DEFAULT_COHERENCE_THRESHOLD
        )
        self.evidence_threshold = self.config.get(
            "evidence_threshold",
            self.DEFAULT_EVIDENCE_THRESHOLD
        )
        self.recall_threshold = self.config.get(
            "recall_threshold",
            self.DEFAULT_RECALL_THRESHOLD
        )
        self.review_threshold = self.config.get(
            "review_threshold",
            self.DEFAULT_REVIEW_THRESHOLD
        )
        
        # Definir transiciones válidas
        self._valid_transitions = self._define_transitions()
    
    def _define_transitions(self) -> Dict[Tuple[PublicationState, PublicationState], StateTransition]:
        """Define todas las transiciones de estado válidas."""
        transitions = {}
        
        # De DRAFT_INTERNAL a REQUIRES_REVIEW
        transitions[(PublicationState.DRAFT_INTERNAL, PublicationState.REQUIRES_REVIEW)] = StateTransition(
            from_state=PublicationState.DRAFT_INTERNAL,
            to_state=PublicationState.REQUIRES_REVIEW,
            condition="Se resolvieron todos los issues críticos",
            requires_resolution=["hard_contradictions", "financial_validity", "coherence"]
        )
        
        # De REQUIRES_REVIEW a READY_FOR_CLIENT
        transitions[(PublicationState.REQUIRES_REVIEW, PublicationState.READY_FOR_CLIENT)] = StateTransition(
            from_state=PublicationState.REQUIRES_REVIEW,
            to_state=PublicationState.READY_FOR_CLIENT,
            condition="Se resolvieron todos los warnings y soft conflicts",
            requires_resolution=["evidence_coverage", "critical_recall", "soft_contradictions"]
        )
        
        # De cualquiera a BLOCKED (automático, no requiere validación)
        transitions[(PublicationState.DRAFT_INTERNAL, PublicationState.BLOCKED)] = StateTransition(
            from_state=PublicationState.DRAFT_INTERNAL,
            to_state=PublicationState.BLOCKED,
            condition="Múltiples fallas críticas detectadas",
            requires_resolution=[]
        )
        transitions[(PublicationState.REQUIRES_REVIEW, PublicationState.BLOCKED)] = StateTransition(
            from_state=PublicationState.REQUIRES_REVIEW,
            to_state=PublicationState.BLOCKED,
            condition="Empeoramiento a crítico",
            requires_resolution=[]
        )
        transitions[(PublicationState.READY_FOR_CLIENT, PublicationState.BLOCKED)] = StateTransition(
            from_state=PublicationState.READY_FOR_CLIENT,
            to_state=PublicationState.BLOCKED,
            condition="Degradación crítica",
            requires_resolution=[]
        )
        
        # De READY_FOR_CLIENT a REQUIRES_REVIEW (degradación)
        transitions[(PublicationState.READY_FOR_CLIENT, PublicationState.REQUIRES_REVIEW)] = StateTransition(
            from_state=PublicationState.READY_FOR_CLIENT,
            to_state=PublicationState.REQUIRES_REVIEW,
            condition="Nuevos warnings detectados",
            requires_resolution=["evidence_coverage", "critical_recall"]
        )
        
        return transitions
    
    def determine_publication_state(
        self,
        gate_results: Dict[str, Any],
        previous_state: Optional[PublicationState] = None
    ) -> PublicationStateResult:
        """Determina el estado de publicación desde resultados de gates.
        
        Lógica de estados:
            - hard_contradictions > 0 → DRAFT_INTERNAL
            - financial_validity == False → DRAFT_INTERNAL
            - coherence < 0.8 → DRAFT_INTERNAL
            - evidence_coverage < 0.95 → REQUIRES_REVIEW
            - critical_recall < 0.90 → REQUIRES_REVIEW
            - Múltiples fallas → BLOCKED
            - Todo pasa → READY_FOR_CLIENT
        
        Args:
            gate_results: Resultados de los quality gates
            previous_state: Estado anterior (para detectar cambios)
            
        Returns:
            PublicationStateResult con estado determinado
        """
        # Extraer métricas de gate_results
        hard_contradictions = gate_results.get("hard_contradictions", 0)
        financial_validity = gate_results.get("financial_validity", True)
        coherence = gate_results.get("coherence", 1.0)
        evidence_coverage = gate_results.get("evidence_coverage", 1.0)
        critical_recall = gate_results.get("critical_recall", 1.0)
        soft_contradictions = gate_results.get("soft_contradictions", 0)
        warnings = gate_results.get("warnings", [])
        
        # Contar fallas críticas
        critical_failures = 0
        if hard_contradictions > 0:
            critical_failures += 1
        if not financial_validity:
            critical_failures += 1
        if coherence < self.coherence_threshold:
            critical_failures += 1
        
        # Determinar estado
        blocking_issues = []
        
        # BLOCKED: Múltiples fallas críticas (3 o más)
        if critical_failures >= 3:
            current_state = PublicationState.BLOCKED
            blocking_issues.append(
                f"Múltiples fallas críticas ({critical_failures}): "
                "hard_contradictions, financial_validity, coherence"
            )
        
        # DRAFT_INTERNAL: Al menos una falla crítica
        elif hard_contradictions > 0 or not financial_validity or coherence < self.coherence_threshold:
            current_state = PublicationState.DRAFT_INTERNAL
            
            if hard_contradictions > 0:
                blocking_issues.append(
                    f"{hard_contradictions} contradicción(es) crítica(s) sin resolver"
                )
            if not financial_validity:
                blocking_issues.append("Datos financieros inválidos o con valores por defecto")
            if coherence < self.coherence_threshold:
                blocking_issues.append(
                    f"Coherencia insuficiente ({coherence:.1%} < {self.coherence_threshold:.1%})"
                )
        
        # REQUIRES_REVIEW: Solo warnings o soft conflicts
        elif evidence_coverage < self.evidence_threshold or critical_recall < self.recall_threshold:
            current_state = PublicationState.REQUIRES_REVIEW
            
            if evidence_coverage < self.evidence_threshold:
                blocking_issues.append(
                    f"Cobertura de evidencia baja ({evidence_coverage:.1%} < {self.evidence_threshold:.1%})"
                )
            if critical_recall < self.recall_threshold:
                blocking_issues.append(
                    f"Recall crítico bajo ({critical_recall:.1%} < {self.recall_threshold:.1%})"
                )
        
        # READY_FOR_CLIENT: Todo pasa
        else:
            current_state = PublicationState.READY_FOR_CLIENT
        
        # Agregar warnings como issues menores
        if warnings:
            blocking_issues.extend([f"Warning: {w}" for w in warnings[:3]])
        
        if soft_contradictions > 0:
            blocking_issues.append(f"{soft_contradictions} contradicción(es) suave(s) detectada(s)")
        
        # Determinar razón de transición
        transition_reason = ""
        if previous_state and previous_state != current_state:
            if current_state == PublicationState.BLOCKED:
                transition_reason = "Degradación a estado bloqueado por múltiples fallas"
            elif current_state == PublicationState.DRAFT_INTERNAL:
                transition_reason = "Falla en gate crítico detectada"
            elif current_state == PublicationState.REQUIRES_REVIEW:
                if previous_state == PublicationState.DRAFT_INTERNAL:
                    transition_reason = "Issues críticos resueltos, quedan warnings"
                else:
                    transition_reason = "Nuevos warnings detectados"
            elif current_state == PublicationState.READY_FOR_CLIENT:
                transition_reason = "Todos los gates pasaron exitosamente"
        
        # Generar sugerencias
        suggestions = self._generate_suggestions(
            current_state, gate_results, blocking_issues
        )
        
        return PublicationStateResult(
            current_state=current_state,
            previous_state=previous_state,
            transition_reason=transition_reason,
            blocking_issues=blocking_issues,
            improvement_suggestions=suggestions,
            gate_results=gate_results
        )
    
    def can_transition_to(
        self,
        current: PublicationState,
        target: PublicationState,
        gate_results: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Valida si una transición de estado es permitida.
        
        Args:
            current: Estado actual
            target: Estado destino deseado
            gate_results: Resultados actuales de gates
            
        Returns:
            Tuple de (permitido, mensaje)
        """
        # Mismo estado, siempre permitido
        if current == target:
            return True, "Mismo estado"
        
        # Verificar si la transición está definida
        transition_key = (current, target)
        
        if transition_key not in self._valid_transitions:
            # Transición no válida (ej: DRAFT_INTERNAL → READY_FOR_CLIENT directo)
            return False, (
                f"Transición no válida: {current.value} → {target.value}. "
                f"Debe pasar por estados intermedios."
            )
        
        transition = self._valid_transitions[transition_key]
        
        # Verificar que se cumplan condiciones
        for requirement in transition.requires_resolution:
            if requirement == "hard_contradictions":
                if gate_results.get("hard_contradictions", 0) > 0:
                    return False, "Aún existen contradicciones críticas sin resolver"
            
            elif requirement == "financial_validity":
                if not gate_results.get("financial_validity", True):
                    return False, "Datos financieros aún inválidos"
            
            elif requirement == "coherence":
                coherence = gate_results.get("coherence", 0)
                if coherence < self.coherence_threshold:
                    return False, f"Coherencia aún baja ({coherence:.1%})"
            
            elif requirement == "evidence_coverage":
                coverage = gate_results.get("evidence_coverage", 0)
                if coverage < self.evidence_threshold:
                    return False, f"Cobertura de evidencia aún baja ({coverage:.1%})"
            
            elif requirement == "critical_recall":
                recall = gate_results.get("critical_recall", 0)
                if recall < self.recall_threshold:
                    return False, f"Recall crítico aún bajo ({recall:.1%})"
            
            elif requirement == "soft_contradictions":
                if gate_results.get("soft_contradictions", 0) > 0:
                    return False, "Aún existen contradicciones suaves"
        
        return True, f"Transición permitida: {transition.condition}"
    
    def get_state_requirements(self, state: PublicationState) -> Dict[str, Any]:
        """Obtiene los requisitos para alcanzar un estado.
        
        Args:
            state: Estado objetivo
            
        Returns:
            Diccionario con requisitos del estado
        """
        requirements = {
            PublicationState.READY_FOR_CLIENT: {
                "description": "Listo para entrega al cliente",
                "hard_contradictions": 0,
                "financial_validity": True,
                "coherence": f">= {self.coherence_threshold}",
                "evidence_coverage": f">= {self.evidence_threshold}",
                "critical_recall": f">= {self.recall_threshold}",
                "soft_contradictions": "Preferiblemente 0",
                "warnings": "Mínimos o ninguno",
                "can_skip_states": False,
                "delivery_permitted": True,
            },
            PublicationState.REQUIRES_REVIEW: {
                "description": "Requiere revisión manual",
                "hard_contradictions": 0,
                "financial_validity": True,
                "coherence": f">= {self.coherence_threshold}",
                "evidence_coverage": f"< {self.evidence_threshold}",
                "critical_recall": f"< {self.recall_threshold}",
                "soft_contradictions": ">= 0 permitidos",
                "warnings": "Presentes pero no críticos",
                "can_skip_states": False,
                "delivery_permitted": False,
            },
            PublicationState.DRAFT_INTERNAL: {
                "description": "Solo uso interno",
                "hard_contradictions": "> 0",
                "financial_validity": "Puede ser False",
                "coherence": f"< {self.coherence_threshold}",
                "evidence_coverage": "Cualquiera",
                "critical_recall": "Cualquiera",
                "soft_contradictions": "Cualquiera",
                "warnings": "Cualquiera",
                "can_skip_states": False,
                "delivery_permitted": False,
            },
            PublicationState.BLOCKED: {
                "description": "Bloqueado por fallas graves",
                "hard_contradictions": ">= 3 o combinación crítica",
                "financial_validity": "Puede ser False",
                "coherence": "Muy bajo",
                "evidence_coverage": "Irrelevante",
                "critical_recall": "Irrelevante",
                "soft_contradictions": "Irrelevante",
                "warnings": "Irrelevante",
                "can_skip_states": True,  # Puede ir directo a BLOCKED
                "delivery_permitted": False,
            },
        }
        
        return requirements.get(state, {})
    
    def _generate_suggestions(
        self,
        state: PublicationState,
        gate_results: Dict[str, Any],
        blocking_issues: List[str]
    ) -> List[str]:
        """Genera sugerencias para mejorar el estado.
        
        Args:
            state: Estado actual
            gate_results: Resultados de gates
            blocking_issues: Issues bloqueantes identificados
            
        Returns:
            Lista de sugerencias
        """
        suggestions = []
        
        if state == PublicationState.BLOCKED:
            suggestions.append(
                "Priorice resolver las fallas críticas en orden: "
                "1) Contradicciones, 2) Datos financieros, 3) Coherencia"
            )
            suggestions.append(
                "Considere reiniciar el assessment con datos más completos"
            )
            suggestions.append(
                "Contacte al equipo de soporte si las fallas persisten"
            )
        
        elif state == PublicationState.DRAFT_INTERNAL:
            if gate_results.get("hard_contradictions", 0) > 0:
                suggestions.append(
                    "Resuelva las contradicciones entre fuentes de datos "
                    "(web, GBP, input del usuario)"
                )
            if not gate_results.get("financial_validity", True):
                suggestions.append(
                    "Complete los datos financieros requeridos: rooms, ADR, occupancy"
                )
            if gate_results.get("coherence", 1.0) < self.coherence_threshold:
                suggestions.append(
                    f"Mejore la coherencia agregando más fuentes de evidencia "
                    f"(meta: >{self.coherence_threshold:.0%})"
                )
            suggestions.append(
                "Una vez resueltos los issues críticos, avanzará a REQUIRES_REVIEW"
            )
        
        elif state == PublicationState.REQUIRES_REVIEW:
            if gate_results.get("evidence_coverage", 1.0) < self.evidence_threshold:
                suggestions.append(
                    f"Aumente la cobertura de evidencia verificando más claims "
                    f"con fuentes externas (meta: >{self.evidence_threshold:.0%})"
                )
            if gate_results.get("critical_recall", 1.0) < self.recall_threshold:
                suggestions.append(
                    f"Mejore el recall de datos críticos completando información "
                    f"faltante del hotel (meta: >{self.recall_threshold:.0%})"
                )
            if gate_results.get("soft_contradictions", 0) > 0:
                suggestions.append(
                    "Resuelva las contradicciones suaves para mejorar calidad"
                )
            suggestions.append(
                "Una vez resueltos los warnings, avanzará a READY_FOR_CLIENT"
            )
        
        elif state == PublicationState.READY_FOR_CLIENT:
            suggestions.append("✅ El assessment está listo para entrega al cliente")
            suggestions.append("Genere los documentos comerciales y proceda con el delivery")
        
        return suggestions
    
    def get_valid_next_states(self, current: PublicationState) -> List[PublicationState]:
        """Obtiene los estados válidos a los que puede transicionar.
        
        Args:
            current: Estado actual
            
        Returns:
            Lista de estados destino válidos
        """
        valid = [current]  # Siempre puede mantener el mismo estado
        
        for (from_state, to_state) in self._valid_transitions.keys():
            if from_state == current and to_state not in valid:
                valid.append(to_state)
        
        return valid
    
    def validate_publication_permission(self, state_result: PublicationStateResult) -> Tuple[bool, str]:
        """Valida si se permite la publicación al cliente.
        
        Args:
            state_result: Resultado del estado de publicación
            
        Returns:
            Tuple de (permitido, mensaje)
        """
        if state_result.current_state == PublicationState.READY_FOR_CLIENT:
            return True, "Publicación permitida"
        
        if state_result.current_state == PublicationState.BLOCKED:
            return False, (
                "Publicación BLOQUEADA: El assessment tiene múltiples fallas críticas "
                "que deben resolverse primero"
            )
        
        if state_result.current_state == PublicationState.DRAFT_INTERNAL:
            return False, (
                "Publicación NO PERMITIDA: Documentos DRAFT_INTERNAL nunca llegan al cliente. "
                "Debe resolver issues críticos primero"
            )
        
        if state_result.current_state == PublicationState.REQUIRES_REVIEW:
            return False, (
                "Publicación pendiente de revisión: El assessment requiere revisión manual "
                "antes de la entrega"
            )
        
        return False, "Estado desconocido"


# Funciones de conveniencia para uso directo

def determine_publication_state(
    gate_results: Dict[str, Any],
    previous_state: Optional[PublicationState] = None,
    config: Optional[Dict[str, Any]] = None
) -> PublicationStateResult:
    """Determina estado de publicación desde resultados de gates.
    
    Args:
        gate_results: Resultados de los quality gates
        previous_state: Estado anterior (opcional)
        config: Configuración de umbrales (opcional)
        
    Returns:
        PublicationStateResult con estado determinado
    """
    manager = PublicationStateManager(config)
    return manager.determine_publication_state(gate_results, previous_state)


def can_transition_to(
    current: PublicationState,
    target: PublicationState,
    gate_results: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Tuple[bool, str]:
    """Valida si una transición es permitida.
    
    Args:
        current: Estado actual
        target: Estado destino
        gate_results: Resultados de gates
        config: Configuración (opcional)
        
    Returns:
        Tuple de (permitido, mensaje)
    """
    manager = PublicationStateManager(config)
    return manager.can_transition_to(current, target, gate_results)


def get_state_requirements(
    state: PublicationState,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Obtiene requisitos para alcanzar un estado.
    
    Args:
        state: Estado objetivo
        config: Configuración (opcional)
        
    Returns:
        Diccionario con requisitos
    """
    manager = PublicationStateManager(config)
    return manager.get_state_requirements(state)


def check_can_publish(
    gate_results: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Tuple[bool, PublicationStateResult]:
    """Verifica rápidamente si se puede publicar.
    
    Args:
        gate_results: Resultados de gates
        config: Configuración (opcional)
        
    Returns:
        Tuple de (puede_publicar, resultado_completo)
    """
    result = determine_publication_state(gate_results, config=config)
    manager = PublicationStateManager(config)
    permitted, _ = manager.validate_publication_permission(result)
    return permitted, result
