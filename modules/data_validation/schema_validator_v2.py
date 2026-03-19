"""Schema Validator V2 - Validación de Schema.org markup.

Sprint 1, Fase 1: Valida Schema.org markup con distinción de tipos y coverage scoring.
"""
import json
import re
from typing import Any, Dict, List, Optional, Tuple

from data_models.canonical_assessment import SchemaAnalysis
from data_models.claim import Claim
from enums.severity import Severity


# Coverage Schema para Hotel
SCHEMA_HOTEL_COVERAGE = {
    "required": ["name", "address", "@type"],
    "critical_for_rich_results": [
        "image", 
        "aggregateRating", 
        "geo",
    ],
    "recommended": [
        "starRating",
        "openingHours",
        "paymentAccepted",
        "telephone",
        "priceRange",
        "sameAs",
        "amenityFeature",
        "checkinTime",
        "checkoutTime",
    ],
}

# Coverage Schema para LodgingBusiness (extends Hotel)
SCHEMA_LODGING_BUSINESS_COVERAGE = {
    "required": ["name", "address", "@type"],
    "critical_for_rich_results": [
        "image", 
        "aggregateRating", 
        "geo",
    ],
    "recommended": [
        "starRating",
        "openingHours",
        "paymentAccepted",
        "telephone",
        "priceRange",
        "sameAs",
        "amenityFeature",
        "checkinTime",
        "checkoutTime",
    ],
}

# Coverage Schema para Organization
SCHEMA_ORGANIZATION_COVERAGE = {
    "required": ["name", "@type"],
    "critical_for_rich_results": ["logo", "url", "sameAs"],
    "recommended": ["description", "contactPoint", "address", "telephone"],
}

# Coverage Schema para LocalBusiness
SCHEMA_LOCALBUSINESS_COVERAGE = {
    "required": ["name", "address", "@type"],
    "critical_for_rich_results": ["geo", "openingHours", "telephone"],
    "recommended": ["priceRange", "paymentAccepted", "image", "url"],
}


class SchemaValidatorV2:
    """Validador de Schema.org markup con coverage scoring.

    Extrae y analiza JSON-LD scripts del HTML para determinar:
    - Tipo de schema (Hotel, Organization, LocalBusiness, etc.)
    - Coverage score (% de campos presentes)
    - Campos críticos faltantes
    - Claims de validación
    """

    # Mapeo de tipos de schema a sus definiciones de coverage
    COVERAGE_MAP = {
        "Hotel": SCHEMA_HOTEL_COVERAGE,
        "LodgingBusiness": SCHEMA_LODGING_BUSINESS_COVERAGE,
        "Organization": SCHEMA_ORGANIZATION_COVERAGE,
        "LocalBusiness": SCHEMA_LOCALBUSINESS_COVERAGE,
    }

    def __init__(self):
        """Inicializa el validador."""
        pass

    def analyze(self, html_content: str, url: str) -> SchemaAnalysis:
        """Analiza el contenido HTML y extrae información de Schema.org.

        Args:
            html_content: Contenido HTML del sitio.
            url: URL del sitio analizado (para referencia).

        Returns:
            SchemaAnalysis: Análisis completo del schema encontrado.
        """
        # Extraer todos los scripts JSON-LD
        schemas = self._extract_json_ld_scripts(html_content)

        if not schemas:
            return SchemaAnalysis(
                schema_type=None,
                coverage_score=0.0,
                missing_critical_fields=[],
                present_fields=[],
                raw_schema=None,
                has_hotel_schema=False,
                has_local_business=False,
            )

        # Detectar el tipo de schema principal
        schema_type = self.detect_schema_type(schemas)

        # Encontrar el schema principal (el del tipo detectado o el primero)
        main_schema = self._find_main_schema(schemas, schema_type)

        # Calcular coverage
        coverage = self.calculate_coverage(main_schema, schema_type)

        # Determinar campos presentes
        present_fields = self._get_present_fields(main_schema)

        # Determinar campos críticos faltantes
        missing_critical = self._get_missing_critical_fields(main_schema, schema_type)

        return SchemaAnalysis(
            schema_type=schema_type,
            coverage_score=coverage["overall"],
            missing_critical_fields=missing_critical,
            present_fields=present_fields,
            raw_schema=main_schema,
            has_hotel_schema=schema_type == "Hotel" or schema_type == "LodgingBusiness",
            has_local_business=schema_type == "LocalBusiness",
        )

    def _extract_json_ld_scripts(self, html_content: str) -> List[Dict[str, Any]]:
        """Extrae todos los scripts JSON-LD del HTML.

        Args:
            html_content: Contenido HTML.

        Returns:
            Lista de diccionarios con los schemas JSON-LD encontrados.
        """
        schemas = []

        # Patrón para encontrar scripts JSON-LD
        pattern = r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>'
        matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)

        for match in matches:
            try:
                # Limpiar el contenido
                json_str = match.strip()
                # Manejar comentarios HTML
                json_str = re.sub(r'<!--.*?-->', '', json_str, flags=re.DOTALL)
                # Parsear JSON
                schema = json.loads(json_str)

                # Si es un @graph, extraer cada elemento
                if isinstance(schema, dict) and "@graph" in schema:
                    for item in schema["@graph"]:
                        if isinstance(item, dict):
                            schemas.append(item)
                elif isinstance(schema, list):
                    schemas.extend(schema)
                else:
                    schemas.append(schema)
            except json.JSONDecodeError:
                # Ignorar scripts malformados
                continue

        return schemas

    def detect_schema_type(self, schemas: List[Dict[str, Any]]) -> str:
        """Detecta el tipo principal de schema.

        Args:
            schemas: Lista de schemas extraídos.

        Returns:
            str: "Hotel", "LodgingBusiness", "Organization", "LocalBusiness", o "Unknown".
        """
        # Prioridad de tipos: Hotel > LodgingBusiness > LocalBusiness > Organization
        type_priority = ["Hotel", "LodgingBusiness", "LocalBusiness", "Organization"]

        for priority_type in type_priority:
            for schema in schemas:
                schema_types = self._get_schema_types(schema)
                if priority_type in schema_types:
                    return priority_type

        # Buscar tipos que extiendan LocalBusiness
        for schema in schemas:
            schema_types = self._get_schema_types(schema)
            # Si tiene @type pero no coincide con los conocidos
            if schema_types:
                return "Unknown"

        return "Unknown"

    def _get_schema_types(self, schema: Dict[str, Any]) -> List[str]:
        """Extrae todos los tipos de un schema (puede ser lista o string).

        Args:
            schema: Schema dict.

        Returns:
            Lista de tipos de schema.
        """
        if not isinstance(schema, dict):
            return []

        schema_type = schema.get("@type", [])
        if isinstance(schema_type, str):
            return [schema_type]
        elif isinstance(schema_type, list):
            return schema_type
        return []

    def _find_main_schema(
        self, schemas: List[Dict[str, Any]], schema_type: str
    ) -> Dict[str, Any]:
        """Encuentra el schema principal del tipo especificado.

        Args:
            schemas: Lista de schemas.
            schema_type: Tipo buscado.

        Returns:
            El schema principal o el primero si no se encuentra.
        """
        for schema in schemas:
            types = self._get_schema_types(schema)
            if schema_type in types or schema_type == "Unknown":
                return schema
        return schemas[0] if schemas else {}

    def calculate_coverage(
        self, schema: Dict[str, Any], schema_type: str
    ) -> Dict[str, float]:
        """Calcula el coverage score del schema.

        Args:
            schema: Schema dict a analizar.
            schema_type: Tipo de schema.

        Returns:
            Dict con: required, critical, recommended, overall (todos 0.0-1.0).
        """
        coverage_def = self.COVERAGE_MAP.get(schema_type, SCHEMA_HOTEL_COVERAGE)

        # Calcular por categoría
        required_score = self._calculate_field_coverage(
            schema, coverage_def.get("required", [])
        )
        critical_score = self._calculate_field_coverage(
            schema, coverage_def.get("critical_for_rich_results", [])
        )
        recommended_score = self._calculate_field_coverage(
            schema, coverage_def.get("recommended", [])
        )

        # Overall ponderado: required (40%), critical (40%), recommended (20%)
        overall = (
            required_score * 0.4 + critical_score * 0.4 + recommended_score * 0.2
        )

        return {
            "required": round(required_score, 4),
            "critical": round(critical_score, 4),
            "recommended": round(recommended_score, 4),
            "overall": round(overall, 4),
        }

    def _calculate_field_coverage(
        self, schema: Dict[str, Any], fields: List[str]
    ) -> float:
        """Calcula el porcentaje de campos presentes.

        Args:
            schema: Schema dict.
            fields: Lista de campos esperados.

        Returns:
            float: Porcentaje de campos presentes (0.0-1.0).
        """
        if not fields:
            return 1.0

        present = sum(1 for field in fields if self._field_exists(schema, field))
        return present / len(fields)

    def _field_exists(self, schema: Dict[str, Any], field: str) -> bool:
        """Verifica si un campo existe y tiene valor en el schema.

        Args:
            schema: Schema dict.
            field: Nombre del campo.

        Returns:
            True si el campo existe y no está vacío.
        """
        if field not in schema:
            return False

        value = schema[field]
        if value is None:
            return False
        if isinstance(value, (list, str, dict)) and len(value) == 0:
            return False
        return True

    def _get_present_fields(self, schema: Dict[str, Any]) -> List[str]:
        """Extrae la lista de campos presentes en el schema.

        Args:
            schema: Schema dict.

        Returns:
            Lista de nombres de campos presentes.
        """
        if not isinstance(schema, dict):
            return []
        return [k for k, v in schema.items() if v is not None and v != [] and v != {}]

    def _get_missing_critical_fields(
        self, schema: Dict[str, Any], schema_type: str
    ) -> List[str]:
        """Determina qué campos críticos faltan.

        Args:
            schema: Schema dict.
            schema_type: Tipo de schema.

        Returns:
            Lista de campos críticos faltantes.
        """
        coverage_def = self.COVERAGE_MAP.get(schema_type, SCHEMA_HOTEL_COVERAGE)
        critical_fields = coverage_def.get("critical_for_rich_results", [])

        return [field for field in critical_fields if not self._field_exists(schema, field)]

    def generate_claims(
        self,
        analysis: SchemaAnalysis,
        is_hotel_site: bool = True,
        url: str = "",
    ) -> List[Claim]:
        """Genera claims de validación basados en el análisis.

        Args:
            analysis: Resultado del análisis de schema.
            is_hotel_site: True si el sitio es de un hotel.
            url: URL del sitio para referencia.

        Returns:
            Lista de claims generados.
        """
        claims = []
        source_id = "schema_validator_v2"

        # Si no hay schema → Claim CRITICAL
        if analysis.schema_type is None:
            claims.append(
                Claim(
                    source_id=source_id,
                    evidence_excerpt=f"No se encontró Schema.org markup en {url}",
                    severity=Severity.CRITICAL,
                    category="schema",
                    message="El sitio no tiene Schema.org markup implementado. "
                    "Esto impide que Google muestre Rich Results.",
                    field_path="schema.org",
                    confidence=0.9,
                )
            )
            return claims

        # Si schema_type != "Hotel" pero el sitio es hotel → Claim HIGH
        if is_hotel_site and analysis.schema_type != "Hotel":
            claims.append(
                Claim(
                    source_id=source_id,
                    evidence_excerpt=f"Schema detectado: {analysis.schema_type}",
                    severity=Severity.HIGH,
                    category="schema",
                    message=f"El sitio usa schema '{analysis.schema_type}' en lugar de 'Hotel'. "
                    "Esto limita las funcionalidades específicas para hoteles en Google.",
                    field_path="@type",
                    raw_evidence=analysis.raw_schema,
                    confidence=0.9,
                )
            )

        # Si faltan campos críticos → Claim HIGH por cada uno
        for field in analysis.missing_critical_fields:
            claims.append(
                Claim(
                    source_id=source_id,
                    evidence_excerpt=f"Campo crítico ausente: {field}",
                    severity=Severity.HIGH,
                    category="schema",
                    message=f"Falta el campo crítico '{field}' necesario para Rich Results. "
                    f"Los hoteles con {field} tienen 3x más visibilidad en búsquedas.",
                    field_path=field,
                    raw_evidence=analysis.raw_schema,
                    confidence=0.9,
                )
            )

        # Si coverage < 50% → Claim MEDIUM
        if analysis.coverage_score < 0.5:
            claims.append(
                Claim(
                    source_id=source_id,
                    evidence_excerpt=f"Coverage score: {analysis.coverage_score:.1%}",
                    severity=Severity.MEDIUM,
                    category="schema",
                    message=f"El coverage del schema es bajo ({analysis.coverage_score:.1%}). "
                    "Se recomienda completar más campos para mejorar la visibilidad.",
                    field_path="coverage",
                    raw_evidence={
                        "coverage_score": analysis.coverage_score,
                        "present_fields": analysis.present_fields,
                        "missing_critical": analysis.missing_critical_fields,
                    },
                    confidence=0.8,
                )
            )

        return claims

    def validate(
        self, html_content: str, url: str = "", is_hotel_site: bool = True
    ) -> Tuple[SchemaAnalysis, List[Claim]]:
        """Método completo de validación: análisis + claims.

        Args:
            html_content: Contenido HTML.
            url: URL del sitio.
            is_hotel_site: True si es sitio de hotel.

        Returns:
            Tupla (SchemaAnalysis, List[Claim]).
        """
        analysis = self.analyze(html_content, url)
        claims = self.generate_claims(analysis, is_hotel_site, url)
        return analysis, claims
