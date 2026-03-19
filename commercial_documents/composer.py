"""Document Composer - Fase 4 de Composición Documental.

Este módulo implementa el Document Composer que genera documentos comerciales
(diagnóstico y propuesta) a partir de un CanonicalAssessment.

Principios:
    - NUNCA texto libre, siempre trazable a claim
    - Diagnóstico y Propuesta son VISTAS del mismo assessment
    - Un cambio en assessment debe reflejarse en ambos docs
    - Plantillas determinísticas, no generativas
    - Disclaimers automáticos según confidence level

Ejemplo de uso:
    >>> from data_models.canonical_assessment import CanonicalAssessment
    >>> from commercial_documents.composer import DocumentComposer
    >>>
    >>> composer = DocumentComposer()
    >>> assessment = CanonicalAssessment.from_dict(data)
    >>>
    >>> diagnostico = composer.compose_diagnostico(assessment)
    >>> propuesta = composer.compose_propuesta(assessment)
    >>>
    >>> print(diagnostico.content)
    >>> print(diagnostico.publication_status)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from string import Template
from pathlib import Path

from data_models.canonical_assessment import CanonicalAssessment, Claim
from enums.severity import Severity
from enums.confidence_level import ConfidenceLevel


@dataclass
class Document:
    """Representa un documento comercial generado.

    Esta clase encapsula el contenido y metadata de un documento
    generado por el DocumentComposer.

    Attributes:
        content: Contenido markdown del documento.
        assessment_id: UUID del CanonicalAssessment fuente.
        document_type: Tipo de documento (diagnostico, propuesta).
        claim_ids: Lista de IDs de claims incluidos.
        disclaimers: Lista de disclaimers aplicados.
        publication_status: Estado de publicación del documento.
        generated_at: Timestamp de generación.
        version: Versión del documento.

    Example:
        >>> doc = Document(
        ...     content="# Diagnóstico\n...",
        ...     assessment_id=uuid4(),
        ...     document_type="diagnostico",
        ...     claim_ids=[uuid4()],
        ...     disclaimers=["Dato estimado"],
        ...     publication_status="READY_FOR_CLIENT"
        ... )
    """

    content: str
    assessment_id: UUID
    document_type: str
    claim_ids: List[UUID] = field(default_factory=list)
    disclaimers: List[str] = field(default_factory=list)
    publication_status: str = "DRAFT_INTERNAL"
    generated_at: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0.0"

    def has_claim(self, claim_id: UUID) -> bool:
        """Verifica si un claim específico está incluido.

        Args:
            claim_id: UUID del claim a verificar.

        Returns:
            bool: True si el claim está en el documento.
        """
        return claim_id in self.claim_ids

    def get_summary(self) -> Dict[str, Any]:
        """Retorna un resumen del documento.

        Returns:
            Dict con métricas clave del documento.
        """
        return {
            "document_type": self.document_type,
            "assessment_id": str(self.assessment_id),
            "claim_count": len(self.claim_ids),
            "disclaimer_count": len(self.disclaimers),
            "publication_status": self.publication_status,
            "generated_at": self.generated_at.isoformat(),
            "version": self.version,
            "content_length": len(self.content),
        }

    def save(self, output_path: Path) -> None:
        """Guarda el documento en un archivo.

        Args:
            output_path: Ruta donde guardar el archivo.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.content, encoding="utf-8")


class DocumentComposer:
    """Componedor de documentos comerciales para auditorías de hotel.

    Esta clase genera documentos comerciales (diagnóstico y propuesta)
    a partir de un CanonicalAssessment, asegurando:

    - Traza de todos los claims incluidos
    - Disclaimers automáticos según nivel de confianza
    - Sincronización entre diagnóstico y propuesta
    - Estados de publicación basados en criterios objetivos

    Attributes:
        DIAGNOSTICO_TEMPLATE: Plantilla base para diagnósticos.
        PROPUESTA_TEMPLATE: Plantilla base para propuestas.

    Example:
        >>> composer = DocumentComposer()
        >>> diagnostico = composer.compose_diagnostico(assessment)
        >>> propuesta = composer.compose_propuesta(assessment)
        >>>
        >>> # Guardar documentos
        >>> diagnostico.save(Path("output/diagnostico.md"))
        >>> propuesta.save(Path("output/propuesta.md"))
    """

    # Plantilla base para diagnósticos
    DIAGNOSTICO_TEMPLATE = """# Diagnóstico de Presencia Digital

## Resumen Ejecutivo

**Hotel:** ${hotel_name}  
**URL analizada:** ${url}  
**Fecha de análisis:** ${analysis_date}  
**Coherence Score:** ${coherence_score}/1.0  
**Status de publicación:** ${publication_status}

${disclaimers_section}

---

## 1. Metadatos del Sitio

${metadata_claims}

## 2. Análisis de Schema.org

${schema_claims}

## 3. Análisis de Performance

${performance_claims}

## 4. Google Business Profile

${gbp_claims}

---

## Claims por Severidad

### 🚨 Críticos (${critical_count})
${critical_claims}

### ⚠️ Altos (${high_count})
${high_claims}

### ℹ️ Medios (${medium_count})
${medium_claims}

### 📝 Bajos (${low_count})
${low_claims}

---

## Evidencia Detallada

${evidence_section}

---

*Documento generado por IA Hoteles v${version}*  
*Assessment ID: ${assessment_id}*
"""

    # Plantilla base para propuestas
    PROPUESTA_TEMPLATE = """# Propuesta Comercial

## Resumen Ejecutivo

**Hotel:** ${hotel_name}  
**URL analizada:** ${url}  
**Fecha de propuesta:** ${proposal_date}  
**Coherence Score:** ${coherence_score}/1.0  
**Status de publicación:** ${publication_status}

${disclaimers_section}

---

## Situación Actual

${situacion_claims}

---

## Oportunidades Identificadas

### 🎯 Prioridad Alta
${oportunidades_alta}

### 📊 Prioridad Media
${oportunidades_media}

### 💡 Quick Wins
${oportunidades_baja}

---

## Propuesta de Valor

Basándonos en el diagnóstico realizado (Assessment ID: ${assessment_id}), 
identificamos las siguientes oportunidades de mejora:

### WhatsApp Status
${whatsapp_status}

### Google Business Profile Status
${gbp_status}

### Schema.org Status
${schema_status}

### Performance Status
${performance_status}

---

## Inversión y Escenarios

${investment_section}

---

## Siguientes Pasos

1. **Revisión de diagnóstico** - Validar findings con el hotel
2. **Priorización** - Definir orden de implementación
3. **Implementación** - Ejecutar mejoras aprobadas
4. **Monitoreo** - Seguimiento de métricas

---

*Documento generado por IA Hoteles v${version}*  
*Assessment ID: ${assessment_id}*  
*Basado en el mismo análisis que el diagnóstico*
"""

    def __init__(self, version: str = "4.2.0"):
        """Inicializa el DocumentComposer.

        Args:
            version: Versión del composer.
        """
        self.version = version

    def compose_diagnostico(self, assessment: CanonicalAssessment) -> Document:
        """Genera el documento de diagnóstico desde el CanonicalAssessment.

        Este método crea un diagnóstico completo que incluye todos los claims
del assessment, con disclaimers automáticos según el nivel de confianza.

        Args:
            assessment: El CanonicalAssessment fuente de verdad.

        Returns:
            Document: Documento de diagnóstico generado.

        Example:
            >>> composer = DocumentComposer()
            >>> doc = composer.compose_diagnostico(assessment)
            >>> print(doc.publication_status)
            'READY_FOR_CLIENT'
        """
        # Generar disclaimers basados en claims
        disclaimers = self._generate_disclaimers(assessment.claims)

        # Determinar status de publicación
        publication_status = self._determine_publication_status(assessment)

        # Obtener claims por severidad
        critical_claims = assessment.get_claims_by_severity(Severity.CRITICAL)
        high_claims = assessment.get_claims_by_severity(Severity.HIGH)
        medium_claims = assessment.get_claims_by_severity(Severity.MEDIUM)
        low_claims = assessment.get_claims_by_severity(Severity.LOW)

        # Obtener claims por categoría
        metadata_claims = assessment.get_claims_by_category("metadata")
        schema_claims = assessment.get_claims_by_category("schema")
        performance_claims = assessment.get_claims_by_category("performance")
        gbp_claims = assessment.get_claims_by_category("gbp")

        # Construir placeholders
        placeholders = {
            "hotel_name": assessment.site_metadata.title.split(" - ")[0]
            if " - " in assessment.site_metadata.title
            else assessment.site_metadata.title,
            "url": assessment.url,
            "analysis_date": assessment.analyzed_at.strftime("%Y-%m-%d %H:%M UTC"),
            "coherence_score": f"{assessment.coherence_score:.2f}",
            "publication_status": publication_status,
            "version": self.version,
            "assessment_id": str(assessment.assessment_id),
            "disclaimers_section": self._build_disclaimers_section(disclaimers),
            "metadata_claims": self._format_claims_section(metadata_claims),
            "schema_claims": self._format_claims_section(schema_claims),
            "performance_claims": self._format_claims_section(performance_claims),
            "gbp_claims": self._format_claims_section(gbp_claims),
            "critical_count": str(len(critical_claims)),
            "high_count": str(len(high_claims)),
            "medium_count": str(len(medium_claims)),
            "low_count": str(len(low_claims)),
            "critical_claims": self._format_claims_list(critical_claims),
            "high_claims": self._format_claims_list(high_claims),
            "medium_claims": self._format_claims_list(medium_claims),
            "low_claims": self._format_claims_list(low_claims),
            "evidence_section": self._build_evidence_section(assessment.claims),
        }

        # Resolver plantilla
        content = self._resolve_placeholders(self.DIAGNOSTICO_TEMPLATE, placeholders)

        # Crear documento
        return Document(
            content=content,
            assessment_id=assessment.assessment_id,
            document_type="diagnostico",
            claim_ids=[c.claim_id for c in assessment.claims],
            disclaimers=disclaimers,
            publication_status=publication_status,
            version=self.version,
        )

    def compose_propuesta(self, assessment: CanonicalAssessment) -> Document:
        """Genera el documento de propuesta desde el mismo CanonicalAssessment.

        Este método crea una propuesta comercial que usa los mismos claim_id
        que el diagnóstico, garantizando consistencia entre ambos documentos.

        Args:
            assessment: El CanonicalAssessment fuente de verdad.

        Returns:
            Document: Documento de propuesta generado.

        Note:
            Usa exactamente los mismos claim_id que el diagnóstico para
            mantener trazabilidad completa.

        Example:
            >>> composer = DocumentComposer()
            >>> diagnostico = composer.compose_diagnostico(assessment)
            >>> propuesta = composer.compose_propuesta(assessment)
            >>> # Ambos comparten los mismos claim_ids
            >>> assert diagnostico.claim_ids == propuesta.claim_ids
        """
        # Generar disclaimers (mismos que diagnóstico)
        disclaimers = self._generate_disclaimers(assessment.claims)

        # Determinar status de publicación
        publication_status = self._determine_publication_status(assessment)

        # Obtener claims por severidad para oportunidades
        critical_high = [
            c
            for c in assessment.claims
            if c.severity in (Severity.CRITICAL, Severity.HIGH)
        ]
        medium = assessment.get_claims_by_severity(Severity.MEDIUM)
        low = assessment.get_claims_by_severity(Severity.LOW)

        # Obtener claims por categoría para status
        whatsapp_claims = [
            c
            for c in assessment.claims
            if "whatsapp" in c.category.lower() or "whatsapp" in c.message.lower()
        ]
        gbp_claims = assessment.get_claims_by_category("gbp")
        schema_claims = assessment.get_claims_by_category("schema")
        performance_claims = assessment.get_claims_by_category("performance")

        # Construir placeholders
        placeholders = {
            "hotel_name": assessment.site_metadata.title.split(" - ")[0]
            if " - " in assessment.site_metadata.title
            else assessment.site_metadata.title,
            "url": assessment.url,
            "proposal_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            "coherence_score": f"{assessment.coherence_score:.2f}",
            "publication_status": publication_status,
            "version": self.version,
            "assessment_id": str(assessment.assessment_id),
            "disclaimers_section": self._build_disclaimers_section(disclaimers),
            "situacion_claims": self._format_situacion_claims(assessment.claims),
            "oportunidades_alta": self._format_oportunidades(critical_high),
            "oportunidades_media": self._format_oportunidades(medium),
            "oportunidades_baja": self._format_oportunidades(low),
            "whatsapp_status": self._format_status_claims(
                whatsapp_claims, "WhatsApp"
            ),
            "gbp_status": self._format_status_claims(gbp_claims, "Google Business Profile"),
            "schema_status": self._format_status_claims(
                schema_claims, "Schema.org"
            ),
            "performance_status": self._format_status_claims(
                performance_claims, "Performance"
            ),
            "investment_section": self._build_investment_section(assessment),
        }

        # Resolver plantilla
        content = self._resolve_placeholders(self.PROPUESTA_TEMPLATE, placeholders)

        # Crear documento con los mismos claim_ids que el diagnóstico
        return Document(
            content=content,
            assessment_id=assessment.assessment_id,
            document_type="propuesta",
            claim_ids=[c.claim_id for c in assessment.claims],
            disclaimers=disclaimers,
            publication_status=publication_status,
            version=self.version,
        )

    def _resolve_placeholders(
        self, template: str, placeholders: Dict[str, str]
    ) -> str:
        """Resuelve los placeholders en una plantilla.

        Reemplaza los placeholders ${key} con los valores proporcionados.

        Args:
            template: Plantilla con placeholders.
            placeholders: Diccionario de valores a insertar.

        Returns:
            str: Plantilla con placeholders resueltos.

        Example:
            >>> template = "Hola ${nombre}"
            >>> result = composer._resolve_placeholders(
            ...     template, {"nombre": "Mundo"}
            ... )
            >>> print(result)
            'Hola Mundo'
        """
        try:
            t = Template(template)
            return t.safe_substitute(placeholders)
        except Exception:
            # Fallback: reemplazo manual
            result = template
            for key, value in placeholders.items():
                result = result.replace(f"${{{key}}}", str(value))
            return result

    def _generate_disclaimers(self, claims: List[Claim]) -> List[str]:
        """Genera disclaimers basados en los niveles de confianza de los claims.

        Analiza todos los claims y genera disclaimers automáticos para:
        - Claims con nivel ESTIMATED (confianza 0.5-0.9)
        - Claims con nivel CONFLICT (< 0.5)

        Args:
            claims: Lista de claims a analizar.

        Returns:
            List[str]: Lista de disclaimers generados.

        Example:
            >>> disclaimers = composer._generate_disclaimers(assessment.claims)
            >>> for d in disclaimers:
            ...     print(f"⚠️ {d}")
        """
        disclaimers = []

        # Contar claims por nivel de confianza
        estimated_count = sum(
            1 for c in claims if c.confidence_level == ConfidenceLevel.ESTIMATED
        )
        conflict_count = sum(
            1 for c in claims if c.confidence_level == ConfidenceLevel.CONFLICT
        )
        insufficient_count = sum(
            1 for c in claims if c.confidence_level == ConfidenceLevel.INSUFFICIENT
        )

        # Generar disclaimers según reglas
        if conflict_count > 0:
            disclaimers.append(
                f"⚠️ **DATOS CON CONFLICTO**: {conflict_count} claim(s) tienen "
                f"fuentes contradictorias (confidence < 0.5). Requiere revisión manual."
            )

        if estimated_count > 0:
            disclaimers.append(
                f"📊 **DATOS ESTIMADOS**: {estimated_count} claim(s) basados en "
                f"benchmarks regionales o fuente única (confidence 0.5-0.9)."
            )

        if insufficient_count > 0:
            disclaimers.append(
                f"❓ **DATOS INSUFICIENTES**: {insufficient_count} claim(s) sin "
                f"evidencia disponible."
            )

        # Disclaimer general si hay datos no verificados
        unverified_count = estimated_count + conflict_count + insufficient_count
        if unverified_count > 0:
            disclaimers.append(
                f"📝 **NOTA**: {unverified_count}/{len(claims)} datos en este "
                f"documento no están completamente verificados. "
                f"Los datos VERIFIED (≥0.9) se usan directamente."
            )

        return disclaimers

    def _determine_publication_status(self, assessment: CanonicalAssessment) -> str:
        """Determina el estado de publicación basado en criterios objetivos.

        Criterios:
            - READY_FOR_CLIENT: coherence_score >= 0.8 AND hard_contradictions == 0
            - DRAFT_INTERNAL: coherence_score < 0.8 OR hard_contradictions > 0
            - REQUIRES_REVIEW: Tiene claims CONFLICT pero no bloquea

        Args:
            assessment: El assessment a evaluar.

        Returns:
            str: Estado de publicación determinado.

        Example:
            >>> status = composer._determine_publication_status(assessment)
            >>> assert status in ["READY_FOR_CLIENT", "DRAFT_INTERNAL", "REQUIRES_REVIEW"]
        """
        # Verificar criterios primarios
        has_high_coherence = assessment.coherence_score >= 0.8
        has_no_contradictions = assessment.hard_contradictions == 0

        # Contar claims conflictivos
        conflict_claims = [
            c for c in assessment.claims if c.confidence_level == ConfidenceLevel.CONFLICT
        ]

        # Determinar status
        if has_high_coherence and has_no_contradictions and len(conflict_claims) == 0:
            return "READY_FOR_CLIENT"

        if len(conflict_claims) > 0 and has_high_coherence:
            return "REQUIRES_REVIEW"

        return "DRAFT_INTERNAL"

    def _format_claim_evidence(self, claim: Claim) -> str:
        """Formatea la evidencia de un claim según estándar.

        Formato: fuente + timestamp + excerpt

        Args:
            claim: Claim a formatear.

        Returns:
            str: Evidencia formateada.

        Example:
            >>> evidence = composer._format_claim_evidence(claim)
            >>> print(evidence)
            'Fuente: web_scraper | 2024-01-15T10:30:00 | "Hotel con 50 habitaciones"'
        """
        timestamp = claim.timestamp.strftime("%Y-%m-%d %H:%M UTC")
        excerpt = claim.evidence_excerpt[:100] + "..." if len(claim.evidence_excerpt) > 100 else claim.evidence_excerpt

        return (
            f"**Fuente:** {claim.source_id} | "
            f"**Timestamp:** {timestamp} | "
            f"**Excerpt:** \"{excerpt}\""
        )

    def _format_claims_section(self, claims: List[Claim]) -> str:
        """Formatea una sección de claims para el documento.

        Args:
            claims: Lista de claims a formatear.

        Returns:
            str: Sección formateada.
        """
        if not claims:
            return "_No se encontraron claims en esta categoría._"

        lines = []
        for claim in claims:
            confidence_emoji = {
                ConfidenceLevel.VERIFIED: "✅",
                ConfidenceLevel.ESTIMATED: "📊",
                ConfidenceLevel.CONFLICT: "⚠️",
                ConfidenceLevel.INSUFFICIENT: "❓",
            }.get(claim.confidence_level, "❓")

            severity_emoji = {
                Severity.CRITICAL: "🚨",
                Severity.HIGH: "⚠️",
                Severity.MEDIUM: "ℹ️",
                Severity.LOW: "📝",
            }.get(claim.severity, "📝")

            lines.append(
                f"### {severity_emoji} {claim.message}\n\n"
                f"- **Claim ID:** `{claim.claim_id}`\n"
                f"- **Severidad:** {claim.severity.value.upper()}\n"
                f"- **Confianza:** {confidence_emoji} {claim.confidence_level.value.upper()} "
                f"({claim.confidence:.2f})\n"
                f"- **Evidencia:** {self._format_claim_evidence(claim)}\n"
            )

        return "\n".join(lines)

    def _format_claims_list(self, claims: List[Claim]) -> str:
        """Formatea una lista simple de claims.

        Args:
            claims: Lista de claims a formatear.

        Returns:
            str: Lista formateada.
        """
        if not claims:
            return "_No hay claims en este nivel._"

        lines = []
        for claim in claims:
            lines.append(
                f"- **{claim.message}** "
                f"(`{claim.claim_id}`, {claim.confidence_level.value}, {claim.confidence:.2f})"
            )

        return "\n".join(lines)

    def _build_disclaimers_section(self, disclaimers: List[str]) -> str:
        """Construye la sección de disclaimers.

        Args:
            disclaimers: Lista de disclaimers.

        Returns:
            str: Sección de disclaimers formateada.
        """
        if not disclaimers:
            return "✅ **Todos los datos están verificados (≥0.9)**"

        lines = ["## Disclaimers Importantes\n"]
        for disclaimer in disclaimers:
            lines.append(f"- {disclaimer}")

        return "\n".join(lines)

    def _build_evidence_section(self, claims: List[Claim]) -> str:
        """Construye la sección detallada de evidencia.

        Args:
            claims: Lista de claims.

        Returns:
            str: Sección de evidencia formateada.
        """
        if not claims:
            return "_No hay evidencia disponible._"

        lines = []
        for claim in claims:
            lines.append(
                f"### {claim.claim_id}\n\n"
                f"- **Categoría:** {claim.category}\n"
                f"- **Mensaje:** {claim.message}\n"
                f"- **Severidad:** {claim.severity.value}\n"
                f"- **Confianza:** {claim.confidence} ({claim.confidence_level.value})\n"
                f"- **Fuente:** {claim.source_id}\n"
                f"- **Timestamp:** {claim.timestamp.isoformat()}\n"
                f"- **Excerpt:** {claim.evidence_excerpt}\n"
            )

        return "\n".join(lines)

    def _format_situacion_claims(self, claims: List[Claim]) -> str:
        """Formatea los claims de situación actual para la propuesta.

        Args:
            claims: Lista de claims.

        Returns:
            str: Situación formateada.
        """
        if not claims:
            return "_Sin datos de situación._"

        # Agrupar por categoría
        by_category: Dict[str, List[Claim]] = {}
        for claim in claims:
            cat = claim.category
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(claim)

        lines = []
        for category, cat_claims in sorted(by_category.items()):
            lines.append(f"### {category.upper()}")
            for claim in cat_claims[:5]:  # Máximo 5 por categoría
                lines.append(f"- {claim.message} ({claim.severity.value})")
            if len(cat_claims) > 5:
                lines.append(f"- ... y {len(cat_claims) - 5} más")
            lines.append("")

        return "\n".join(lines)

    def _format_oportunidades(self, claims: List[Claim]) -> str:
        """Formatea las oportunidades identificadas.

        Args:
            claims: Lista de claims.

        Returns:
            str: Oportunidades formateadas.
        """
        if not claims:
            return "_No hay oportunidades en esta categoría._"

        lines = []
        for claim in claims[:10]:  # Máximo 10 oportunidades
            confidence_indicator = "✅" if claim.is_verified else "📊"
            lines.append(
                f"- **{claim.message}**\n"
                f"  - Claim: `{claim.claim_id}`\n"
                f"  - Confianza: {confidence_indicator} {claim.confidence:.2f}\n"
            )

        return "\n".join(lines)

    def _format_status_claims(self, claims: List[Claim], label: str) -> str:
        """Formatea el status de una categoría de claims.

        Args:
            claims: Lista de claims.
            label: Etiqueta del status.

        Returns:
            str: Status formateado.
        """
        if not claims:
            return f"✅ **{label}:** No se detectaron issues."

        # Determinar status general
        has_critical = any(c.severity == Severity.CRITICAL for c in claims)
        has_high = any(c.severity == Severity.HIGH for c in claims)

        if has_critical:
            status = "🚨 CRÍTICO"
        elif has_high:
            status = "⚠️ REQUIERE ATENCIÓN"
        else:
            status = "✅ OK con mejoras"

        lines = [f"**{label}:** {status}"]

        for claim in claims[:3]:  # Máximo 3 ejemplos
            lines.append(f"- {claim.message} ({claim.severity.value})")

        if len(claims) > 3:
            lines.append(f"- ... y {len(claims) - 3} items más")

        return "\n".join(lines)

    def _build_investment_section(self, assessment: CanonicalAssessment) -> str:
        """Construye la sección de inversión.

        Args:
            assessment: El assessment.

        Returns:
            str: Sección de inversión formateada.
        """
        total_claims = len(assessment.claims)
        actionable = len(
            [c for c in assessment.claims if c.severity in (Severity.CRITICAL, Severity.HIGH)]
        )

        return f"""### Escenarios

Basado en el diagnóstico con {total_claims} claims identificados:

| Escenario | Claims Prioritarios | Tiempo Estimado |
|-----------|---------------------|-----------------|
| Conservador | {actionable} críticos/altos | 2-4 semanas |
| Realista | {actionable + len([c for c in assessment.claims if c.severity == Severity.MEDIUM])} incluyendo medios | 4-8 semanas |
| Optimista | Todos los {total_claims} claims | 8-12 semanas |

**Nota:** Los tiempos son estimaciones basadas en claims VERIFIED.
Los datos estimados pueden requerir validación adicional.

### Coherence Score

El análisis tiene un coherence score de **{assessment.coherence_score:.2f}/1.0**.

- ✅ ≥ 0.8: Datos altamente consistentes
- ⚠️ 0.5-0.8: Algunas inconsistencias detectadas
- ❌ < 0.5: Requiere revisión significativa
"""
