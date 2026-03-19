"""Domain Gates - Quality Gates por Dominio.

Implementa gates especializados por dominio para validar
que el assessment cumple con los criterios de calidad.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from enum import Enum
from datetime import datetime, timezone


class GateType(Enum):
    """Tipos de gates por dominio."""
    TECHNICAL = "technical"
    COMMERCIAL = "commercial"
    FINANCIAL = "financial"


class GateStatus(Enum):
    """Estados posibles de un gate."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class GateCheck:
    """Una verificación individual dentro de un gate."""
    name: str
    passed: bool
    message: str
    severity: str = "info"  # info, warning, error, critical
    value: Any = None


@dataclass
class DomainGateResult:
    """Resultado de ejecución de un gate."""
    gate_type: GateType
    status: GateStatus
    checks: List[GateCheck] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        """True si el gate pasó (PASSED o WARNING)."""
        return self.status in (GateStatus.PASSED, GateStatus.WARNING)

    @property
    def failed(self) -> bool:
        """True si el gate falló."""
        return self.status == GateStatus.FAILED

    @property
    def critical_failures(self) -> List[GateCheck]:
        """Lista de checks críticos que fallaron."""
        return [c for c in self.checks if c.severity == "critical" and not c.passed]

    def to_dict(self) -> Dict[str, Any]:
        """Serializa resultado a diccionario."""
        return {
            "gate_type": self.gate_type.value,
            "status": self.status.value,
            "passed": self.passed,
            "checks": [
                {
                    "name": c.name,
                    "passed": c.passed,
                    "message": c.message,
                    "severity": c.severity,
                }
                for c in self.checks
            ],
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class TechnicalGate:
    """Gate Técnico - Valida aspectos técnicos del sitio.

    Checks:
    - schema_valid: Schema.org válido y completo
    - performance_measured: Performance medido con PageSpeed
    - no_critical_errors: Sin errores críticos técnicos
    - metadata_complete: Metadatos del sitio completos
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.min_schema_coverage = self.config.get("min_schema_coverage", 0.5)
        self.max_performance_score = self.config.get("max_performance_score", 50)

    def execute(self, assessment: Dict[str, Any]) -> DomainGateResult:
        """Ejecuta todas las validaciones técnicas."""
        checks = [
            self._check_schema_valid(assessment),
            self._check_performance_measured(assessment),
            self._check_no_critical_errors(assessment),
            self._check_metadata_complete(assessment),
        ]

        # Determinar estado basado en checks
        critical_failures = [c for c in checks if c.severity == "critical" and not c.passed]
        error_failures = [c for c in checks if c.severity == "error" and not c.passed]
        warning_failures = [c for c in checks if c.severity == "warning" and not c.passed]

        if critical_failures:
            status = GateStatus.FAILED
        elif error_failures:
            status = GateStatus.FAILED
        elif warning_failures:
            status = GateStatus.WARNING
        else:
            status = GateStatus.PASSED

        return DomainGateResult(
            gate_type=GateType.TECHNICAL,
            status=status,
            checks=checks,
            metadata={
                "schema_coverage_threshold": self.min_schema_coverage,
                "performance_threshold": self.max_performance_score,
            }
        )

    def _check_schema_valid(self, assessment: Dict[str, Any]) -> GateCheck:
        """Valida que el schema sea válido y tenga cobertura mínima."""
        schema_data = assessment.get("schema", {})

        if not schema_data:
            return GateCheck(
                name="schema_valid",
                passed=False,
                message="No se encontraron datos de Schema.org",
                severity="critical"
            )

        # Verificar si hay errores críticos en el schema
        errors = schema_data.get("errors", [])
        critical_schema_errors = [e for e in errors if e.get("severity") == "critical"]

        if critical_schema_errors:
            return GateCheck(
                name="schema_valid",
                passed=False,
                message=f"Schema tiene {len(critical_schema_errors)} errores críticos",
                severity="critical",
                value={"errors": critical_schema_errors}
            )

        # Verificar cobertura mínima
        coverage = schema_data.get("coverage", 0)
        if coverage < self.min_schema_coverage:
            return GateCheck(
                name="schema_valid",
                passed=False,
                message=f"Cobertura de schema ({coverage:.1%}) inferior al mínimo ({self.min_schema_coverage:.1%})",
                severity="error",
                value={"coverage": coverage, "threshold": self.min_schema_coverage}
            )

        return GateCheck(
            name="schema_valid",
            passed=True,
            message=f"Schema válido con cobertura {coverage:.1%}",
            severity="info",
            value={"coverage": coverage}
        )

    def _check_performance_measured(self, assessment: Dict[str, Any]) -> GateCheck:
        """Valida que se haya medido performance."""
        performance = assessment.get("performance", {})

        if not performance:
            return GateCheck(
                name="performance_measured",
                passed=False,
                message="No se encontraron métricas de performance",
                severity="error"
            )

        # Verificar que se usó PageSpeed (no datos inventados)
        data_source = performance.get("data_source", "")
        if data_source != "pagespeed_api":
            return GateCheck(
                name="performance_measured",
                passed=False,
                message=f"Performance no medido con PageSpeed API (fuente: {data_source or 'desconocida'})",
                severity="error",
                value={"data_source": data_source}
            )

        # Verificar métricas clave presentes
        required_metrics = ["lighthouse_score", "first_contentful_paint", "largest_contentful_paint"]
        missing_metrics = [m for m in required_metrics if m not in performance]

        if missing_metrics:
            return GateCheck(
                name="performance_measured",
                passed=False,
                message=f"Métricas de performance incompletas: faltan {missing_metrics}",
                severity="warning",
                value={"missing": missing_metrics}
            )

        # Verificar si el score es muy bajo
        lighthouse_score = performance.get("lighthouse_score", 100)
        if lighthouse_score < self.max_performance_score:
            return GateCheck(
                name="performance_measured",
                passed=True,
                message=f"Performance medido pero score bajo ({lighthouse_score})",
                severity="warning",
                value={"lighthouse_score": lighthouse_score}
            )

        return GateCheck(
            name="performance_measured",
            passed=True,
            message=f"Performance medido correctamente (score: {lighthouse_score})",
            severity="info",
            value={"lighthouse_score": lighthouse_score}
        )

    def _check_no_critical_errors(self, assessment: Dict[str, Any]) -> GateCheck:
        """Valida que no haya errores críticos."""
        errors = assessment.get("errors", [])

        if not errors:
            return GateCheck(
                name="no_critical_errors",
                passed=True,
                message="No se encontraron errores",
                severity="info"
            )

        # Filtrar errores críticos técnicos
        critical_errors = [
            e for e in errors
            if e.get("severity") == "critical" and e.get("category") == "technical"
        ]

        if critical_errors:
            return GateCheck(
                name="no_critical_errors",
                passed=False,
                message=f"Se encontraron {len(critical_errors)} errores críticos técnicos",
                severity="critical",
                value={"errors": critical_errors}
            )

        return GateCheck(
            name="no_critical_errors",
            passed=True,
            message=f"Errores encontrados pero ninguno crítico técnico",
            severity="info",
            value={"total_errors": len(errors)}
        )

    def _check_metadata_complete(self, assessment: Dict[str, Any]) -> GateCheck:
        """Valida que los metadatos del sitio estén completos."""
        metadata = assessment.get("metadata", {})

        required_fields = ["title", "description"]
        missing_fields = [f for f in required_fields if not metadata.get(f)]

        if missing_fields:
            return GateCheck(
                name="metadata_complete",
                passed=False,
                message=f"Metadatos incompletos: faltan {missing_fields}",
                severity="warning",
                value={"missing": missing_fields}
            )

        # Verificar longitud del título
        title = metadata.get("title", "")
        if len(title) < 10 or len(title) > 70:
            return GateCheck(
                name="metadata_complete",
                passed=True,
                message=f"Título presente pero longitud subóptima ({len(title)} caracteres)",
                severity="warning",
                value={"title_length": len(title)}
            )

        return GateCheck(
            name="metadata_complete",
            passed=True,
            message="Metadatos completos",
            severity="info",
            value={"title_length": len(title)}
        )


class CommercialGate:
    """Gate Comercial - Valida datos comerciales del hotel.

    Checks:
    - whatsapp_verified: WhatsApp verificado (confianza >= 0.9)
    - gbp_status_known: Estado de GBP conocido
    - basic_info_complete: Información básica completa
    - contact_data_present: Datos de contacto presentes
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.whatsapp_confidence_threshold = self.config.get(
            "whatsapp_confidence_threshold", 0.9
        )

    def execute(self, assessment: Dict[str, Any]) -> DomainGateResult:
        """Ejecuta todas las validaciones comerciales."""
        checks = [
            self._check_whatsapp_verified(assessment),
            self._check_gbp_status_known(assessment),
            self._check_basic_info_complete(assessment),
            self._check_contact_data_present(assessment),
        ]

        # Determinar estado
        critical_failures = [c for c in checks if c.severity == "critical" and not c.passed]
        error_failures = [c for c in checks if c.severity == "error" and not c.passed]
        warning_failures = [c for c in checks if c.severity == "warning" and not c.passed]

        if critical_failures:
            status = GateStatus.FAILED
        elif error_failures:
            status = GateStatus.WARNING
        elif warning_failures:
            status = GateStatus.WARNING
        else:
            status = GateStatus.PASSED

        return DomainGateResult(
            gate_type=GateType.COMMERCIAL,
            status=status,
            checks=checks,
            metadata={
                "whatsapp_confidence_threshold": self.whatsapp_confidence_threshold,
            }
        )

    def _check_whatsapp_verified(self, assessment: Dict[str, Any]) -> GateCheck:
        """Valida que WhatsApp esté verificado."""
        contact = assessment.get("contact", {})
        whatsapp_data = contact.get("whatsapp", {})

        if not whatsapp_data:
            return GateCheck(
                name="whatsapp_verified",
                passed=False,
                message="No se encontraron datos de WhatsApp",
                severity="warning"
            )

        confidence = whatsapp_data.get("confidence", 0)
        source = whatsapp_data.get("source", "unknown")
        number = whatsapp_data.get("number", "")

        if confidence >= self.whatsapp_confidence_threshold:
            return GateCheck(
                name="whatsapp_verified",
                passed=True,
                message=f"WhatsApp verificado (confianza: {confidence:.1%}, fuente: {source})",
                severity="info",
                value={"confidence": confidence, "source": source, "number": number}
            )

        if confidence >= 0.5:
            return GateCheck(
                name="whatsapp_verified",
                passed=True,
                message=f"WhatsApp parcialmente verificado (confianza: {confidence:.1%})",
                severity="warning",
                value={"confidence": confidence, "source": source, "number": number}
            )

        return GateCheck(
            name="whatsapp_verified",
            passed=False,
            message=f"WhatsApp no verificado (confianza: {confidence:.1%})",
            severity="warning",
            value={"confidence": confidence, "source": source}
        )

    def _check_gbp_status_known(self, assessment: Dict[str, Any]) -> GateCheck:
        """Valida que el estado de GBP sea conocido."""
        gbp = assessment.get("google_business_profile", {})

        if not gbp:
            return GateCheck(
                name="gbp_status_known",
                passed=False,
                message="No se encontraron datos de Google Business Profile",
                severity="info"
            )

        status = gbp.get("status", "unknown")

        if status == "active":
            return GateCheck(
                name="gbp_status_known",
                passed=True,
                message="GBP activo y verificado",
                severity="info",
                value={"status": status}
            )

        if status == "inactive":
            return GateCheck(
                name="gbp_status_known",
                passed=True,
                message="GBP existe pero está inactivo",
                severity="warning",
                value={"status": status}
            )

        return GateCheck(
            name="gbp_status_known",
            passed=True,
            message=f"Estado de GBP: {status}",
            severity="info",
            value={"status": status}
        )

    def _check_basic_info_complete(self, assessment: Dict[str, Any]) -> GateCheck:
        """Valida información básica del hotel."""
        hotel_info = assessment.get("hotel_info", {})

        required_fields = ["name", "address"]
        missing_fields = [f for f in required_fields if not hotel_info.get(f)]

        if missing_fields:
            return GateCheck(
                name="basic_info_complete",
                passed=False,
                message=f"Información básica incompleta: faltan {missing_fields}",
                severity="error",
                value={"missing": missing_fields}
            )

        # Verificar campos adicionales recomendados
        recommended_fields = ["phone", "email", "stars", "category"]
        missing_recommended = [f for f in recommended_fields if not hotel_info.get(f)]

        if missing_recommended:
            return GateCheck(
                name="basic_info_complete",
                passed=True,
                message=f"Información básica completa, pero faltan datos recomendados: {missing_recommended}",
                severity="warning",
                value={"missing_recommended": missing_recommended}
            )

        return GateCheck(
            name="basic_info_complete",
            passed=True,
            message="Información básica del hotel completa",
            severity="info"
        )

    def _check_contact_data_present(self, assessment: Dict[str, Any]) -> GateCheck:
        """Valida que los datos de contacto estén presentes."""
        contact = assessment.get("contact", {})

        # Verificar al menos un método de contacto
        has_phone = bool(contact.get("phone") or contact.get("mobile"))
        has_email = bool(contact.get("email"))
        has_whatsapp = bool(contact.get("whatsapp", {}).get("number"))

        contact_methods = []
        if has_phone:
            contact_methods.append("phone")
        if has_email:
            contact_methods.append("email")
        if has_whatsapp:
            contact_methods.append("whatsapp")

        if not contact_methods:
            return GateCheck(
                name="contact_data_present",
                passed=False,
                message="No se encontraron métodos de contacto",
                severity="error"
            )

        if len(contact_methods) < 2:
            return GateCheck(
                name="contact_data_present",
                passed=True,
                message=f"Solo un método de contacto encontrado: {contact_methods[0]}",
                severity="warning",
                value={"methods": contact_methods}
            )

        return GateCheck(
            name="contact_data_present",
            passed=True,
            message=f"Datos de contacto completos: {', '.join(contact_methods)}",
            severity="info",
            value={"methods": contact_methods}
        )


class FinancialGate:
    """Gate Financiero - Valida datos financieros completos.

    Checks:
    - no_defaults: Sin valores por defecto (usa NoDefaultsValidator)
    - inputs_validated: Inputs validados completamente
    - data_source_verified: Fuente de datos financieros verificada
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.require_whatsapp = self.config.get("require_whatsapp", True)

    def execute(
        self,
        assessment: Dict[str, Any],
        financial_data: Optional[Dict] = None
    ) -> DomainGateResult:
        """Ejecuta todas las validaciones financieras."""
        if financial_data is None:
            financial_data = assessment.get("financial", {})

        checks = [
            self._check_no_defaults(financial_data),
            self._check_inputs_validated(financial_data),
            self._check_data_source_verified(financial_data),
            self._check_adr_reasonable(financial_data, assessment),
        ]

        # Determinar estado
        critical_failures = [c for c in checks if c.severity == "critical" and not c.passed]
        error_failures = [c for c in checks if c.severity == "error" and not c.passed]

        if critical_failures:
            status = GateStatus.FAILED
        elif error_failures:
            status = GateStatus.WARNING
        else:
            status = GateStatus.PASSED

        return DomainGateResult(
            gate_type=GateType.FINANCIAL,
            status=status,
            checks=checks,
            metadata={
                "require_whatsapp": self.require_whatsapp,
            }
        )

    def _check_no_defaults(self, financial_data: Dict[str, Any]) -> GateCheck:
        """Valida que no haya valores por defecto."""
        # Lista de valores que indican "default" o placeholder
        default_indicators = [
            "default", "placeholder", "unknown", "not_set",
            "por_definir", "pendiente", "tbd", "TODO"
        ]

        inputs = financial_data.get("inputs", {})
        defaults_found = []

        for key, value in inputs.items():
            if value is None:
                defaults_found.append(f"{key}=None")
            elif isinstance(value, str):
                if any(ind in value.lower() for ind in default_indicators):
                    defaults_found.append(f"{key}={value}")
            elif isinstance(value, (int, float)) and value == 0:
                # Cero puede ser válido en algunos casos, pero marcamos como warning
                if key in ["rooms", "adr", "occupancy"]:
                    defaults_found.append(f"{key}=0")

        if defaults_found:
            return GateCheck(
                name="no_defaults",
                passed=False,
                message=f"Se encontraron valores por defecto: {defaults_found}",
                severity="error",
                value={"defaults": defaults_found}
            )

        return GateCheck(
            name="no_defaults",
            passed=True,
            message="No se detectaron valores por defecto",
            severity="info",
            value={"inputs_checked": list(inputs.keys())}
        )

    def _check_inputs_validated(self, financial_data: Dict[str, Any]) -> GateCheck:
        """Valida que los inputs estén validados."""
        inputs = financial_data.get("inputs", {})

        if not inputs:
            return GateCheck(
                name="inputs_validated",
                passed=False,
                message="No hay inputs financieros",
                severity="error"
            )

        # Verificar campos financieros esenciales
        essential_fields = ["rooms", "adr", "occupancy"]
        missing_fields = [f for f in essential_fields if f not in inputs]

        if missing_fields:
            return GateCheck(
                name="inputs_validated",
                passed=False,
                message=f"Faltan campos financieros esenciales: {missing_fields}",
                severity="error",
                value={"missing": missing_fields}
            )

        # Verificar validación específica
        validation = financial_data.get("validation", {})
        if not validation.get("validated", False):
            return GateCheck(
                name="inputs_validated",
                passed=True,
                message="Inputs presentes pero no marcados como validados",
                severity="warning",
                value={"validated": False}
            )

        return GateCheck(
            name="inputs_validated",
            passed=True,
            message="Inputs financieros validados correctamente",
            severity="info",
            value={"fields": list(inputs.keys())}
        )

    def _check_data_source_verified(self, financial_data: Dict[str, Any]) -> GateCheck:
        """Valida que la fuente de datos financieros esté verificada."""
        data_source = financial_data.get("data_source", {})

        if not data_source:
            return GateCheck(
                name="data_source_verified",
                passed=False,
                message="No se especificó fuente de datos financieros",
                severity="warning"
            )

        source_type = data_source.get("type", "unknown")
        confidence = data_source.get("confidence", 0)

        verified_sources = ["user_input", "benchmark", "validated_estimate", "cross_referenced"]

        if source_type in verified_sources and confidence >= 0.7:
            return GateCheck(
                name="data_source_verified",
                passed=True,
                message=f"Fuente de datos verificada: {source_type} (confianza: {confidence:.1%})",
                severity="info",
                value={"source": source_type, "confidence": confidence}
            )

        if confidence >= 0.5:
            return GateCheck(
                name="data_source_verified",
                passed=True,
                message=f"Fuente de datos con confianza media: {source_type} ({confidence:.1%})",
                severity="warning",
                value={"source": source_type, "confidence": confidence}
            )

        return GateCheck(
            name="data_source_verified",
            passed=False,
            message=f"Fuente de datos no verificada: {source_type} ({confidence:.1%})",
            severity="warning",
            value={"source": source_type, "confidence": confidence}
        )

    def _check_adr_reasonable(self, financial_data: Dict[str, Any], assessment: Dict[str, Any]) -> GateCheck:
        """Valida que el ADR sea razonable comparado con benchmarks."""
        inputs = financial_data.get("inputs", {})
        adr = inputs.get("adr")

        if adr is None:
            return GateCheck(
                name="adr_reasonable",
                passed=False,
                message="ADR no especificado",
                severity="warning"
            )

        # Obtener benchmark regional si existe
        benchmark = assessment.get("benchmark", {})
        benchmark_adr = benchmark.get("adr_range", {})

        if not benchmark_adr:
            return GateCheck(
                name="adr_reasonable",
                passed=True,
                message=f"ADR especificado ({adr}) pero no hay benchmark para comparar",
                severity="info",
                value={"adr": adr}
            )

        min_adr = benchmark_adr.get("min", 0)
        max_adr = benchmark_adr.get("max", float('inf'))

        if min_adr <= adr <= max_adr:
            return GateCheck(
                name="adr_reasonable",
                passed=True,
                message=f"ADR ({adr}) dentro del rango esperado ({min_adr}-{max_adr})",
                severity="info",
                value={"adr": adr, "range": [min_adr, max_adr]}
            )

        # Si está fuera de rango, verificar si es significativamente diferente
        if adr < min_adr * 0.5 or adr > max_adr * 2:
            return GateCheck(
                name="adr_reasonable",
                passed=False,
                message=f"ADR ({adr}) significativamente diferente al benchmark ({min_adr}-{max_adr})",
                severity="warning",
                value={"adr": adr, "range": [min_adr, max_adr], "ratio": adr / ((min_adr + max_adr) / 2)}
            )

        return GateCheck(
            name="adr_reasonable",
            passed=True,
            message=f"ADR ({adr}) ligeramente fuera de rango pero aceptable",
            severity="warning",
            value={"adr": adr, "range": [min_adr, max_adr]}
        )


class DomainGatesOrchestrator:
    """Orquestador de todos los gates por dominio.

    Ejecuta los 3 gates y determina si el assessment está listo
    para generar documentos comerciales.
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.technical_gate = TechnicalGate(self.config.get("technical", {}))
        self.commercial_gate = CommercialGate(self.config.get("commercial", {}))
        self.financial_gate = FinancialGate(self.config.get("financial", {}))

    def execute_all(
        self,
        assessment: Dict[str, Any],
        financial_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Ejecuta todos los gates y retorna resultados consolidados.

        Args:
            assessment: Datos del assessment canónico
            financial_data: Datos financieros opcionales

        Returns:
            Dict con resultados de todos los gates y estado consolidado
        """
        # Ejecutar cada gate
        technical_result = self.technical_gate.execute(assessment)
        commercial_result = self.commercial_gate.execute(assessment)
        financial_result = self.financial_gate.execute(assessment, financial_data)

        # Determinar estado consolidado
        all_results = [technical_result, commercial_result, financial_result]

        # Contar fallas
        total_critical = sum(len(r.critical_failures) for r in all_results)
        total_failed = sum(1 for r in all_results if r.failed)
        total_warnings = sum(
            1 for r in all_results
            if r.status == GateStatus.WARNING
        )

        # Estado global
        if total_critical > 0 or total_failed > 0:
            overall_status = "blocked"
        elif total_warnings > 0:
            overall_status = "warning"
        else:
            overall_status = "ready"

        return {
            "overall_status": overall_status,
            "can_proceed": overall_status in ("ready", "warning"),
            "all_passed": overall_status == "ready",
            "gates": {
                "technical": technical_result.to_dict(),
                "commercial": commercial_result.to_dict(),
                "financial": financial_result.to_dict(),
            },
            "summary": {
                "total_checks": sum(len(r.checks) for r in all_results),
                "passed": sum(1 for r in all_results for c in r.checks if c.passed),
                "failed": sum(1 for r in all_results for c in r.checks if not c.passed),
                "critical_failures": total_critical,
                "warnings": total_warnings,
            },
            "blocking_issues": self._get_blocking_issues_list(all_results),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def can_generate_documents(self, results: Dict[str, Any]) -> bool:
        """Determina si se pueden generar documentos comerciales.

        Args:
            results: Resultados de execute_all()

        Returns:
            True si todos los gates pasaron
        """
        return results.get("can_proceed", False)

    def get_blocking_issues(self, results: Dict[str, Any]) -> List[str]:
        """Obtiene lista de issues que bloquean generación.

        Args:
            results: Resultados de execute_all()

        Returns:
            Lista de mensajes descriptivos de bloqueos
        """
        return results.get("blocking_issues", [])

    def _get_blocking_issues_list(self, results: List[DomainGateResult]) -> List[str]:
        """Genera lista de issues bloqueantes de los resultados."""
        issues = []

        for result in results:
            gate_name = result.gate_type.value

            # Agregar fallas críticas
            for check in result.critical_failures:
                issues.append(f"[{gate_name}] CRITICAL: {check.message}")

            # Agregar errores no críticos
            for check in result.checks:
                if not check.passed and check.severity == "error":
                    issues.append(f"[{gate_name}] ERROR: {check.message}")

        return issues


# Funciones de conveniencia para uso directo

def run_all_gates(
    assessment: Dict[str, Any],
    financial_data: Optional[Dict] = None,
    config: Optional[Dict] = None
) -> Dict[str, Any]:
    """Ejecuta todos los gates de calidad.

    Args:
        assessment: Datos del assessment
        financial_data: Datos financieros opcionales
        config: Configuración de los gates

    Returns:
        Resultados consolidados de todos los gates
    """
    orchestrator = DomainGatesOrchestrator(config)
    return orchestrator.execute_all(assessment, financial_data)


def quick_check_technical(assessment: Dict[str, Any]) -> DomainGateResult:
    """Verificación rápida solo del gate técnico."""
    gate = TechnicalGate()
    return gate.execute(assessment)


def quick_check_commercial(assessment: Dict[str, Any]) -> DomainGateResult:
    """Verificación rápida solo del gate comercial."""
    gate = CommercialGate()
    return gate.execute(assessment)


def quick_check_financial(
    financial_data: Dict[str, Any],
    assessment: Optional[Dict] = None
) -> DomainGateResult:
    """Verificación rápida solo del gate financiero."""
    gate = FinancialGate()
    assessment = assessment or {}
    return gate.execute(assessment, financial_data)
