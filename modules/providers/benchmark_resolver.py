"""
Benchmark Resolver - NEVER_BLOCK Architecture

Resuelve gaps de datos usando benchmark regional (Pereira/Santa Rosa de Cabal)
cuando no hay datos reales del hotel.

Principios:
- NEVER_BLOCK: Nunca devuelve None, siempre entrega algo
- BENCHMARK_FALLBACK: Usa datos regionales cuando falta información
- HONEST_CONFIDENCE: Confidence menor para datos de benchmark vs reales
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any


BENCHMARK_TELEPHONE_FORMAT = "+576-000-0000"
BENCHMARK_REGIONS = {
    "eje_cafetero": {
        "default_city": "Pereira",
        "secondary_city": "Santa Rosa de Cabal",
        "country": "CO",
        "department": "Risaralda"
    },
    "pereira": {
        "default_city": "Pereira",
        "secondary_city": "Santa Rosa de Cabal",
        "country": "CO",
        "department": "Risaralda"
    },
    "santa_rosa": {
        "default_city": "Santa Rosa de Cabal",
        "secondary_city": "Pereira",
        "country": "CO",
        "department": "Risaralda"
    }
}

BENCHMARK_DATA = {
    "telephone": {
        "eje_cafetero": "+576-000-0000",
        "default": "+57-000-0000"
    },
    "addressLocality": {
        "eje_cafetero": "Pereira",
        "pereira": "Pereira",
        "santa_rosa": "Santa Rosa de Cabal"
    },
    "country": {
        "default": "Colombia"
    }
}

BENCHMARK_DESCRIPTIONS = {
    "boutique": {
        "eje_cafetero": "Hotel boutique ubicado en el corazón del Eje Cafetero, "
                       "ofreciendo una experiencia única que combina la calidez de la cultura cafetera "
                       "con comodidades modernas. Ideal para viajeros que buscan autenticidad y "
                       "un servicio personalizado en un ambiente acogedor y Refinando.",
        "default": "Hotel boutique que ofrece una experiencia única con servicios personalizados, "
                  "diseño exclusivo y una atmósfera acolhedora para los huéspedes."
    },
    "standard": {
        "eje_cafetero": "Hotel en el Eje Cafetero con instalaciones cómodas y un servicio amable, "
                       "perfecto para viajeros de negocios y turistas que buscan una estadía placentera "
                       "en esta región turística de Colombia.",
        "default": "Hotel estándar con instalaciones cómodas y servicios de calidad para una "
                  "estadía placentera."
    },
    "luxury": {
        "eje_cafetero": "Hotel de lujo en el Eje Cafetero, combinando elegancia sofisticada con "
                       "la calidez de la región cafetera. Servicios exclusivos, gastronomía de alta "
                       "calidad y vistas espectaculares para una experiencia inolvidable.",
        "default": "Hotel de lujo con servicios exclusivos, instalaciones premium y una "
                  "experiencia inolvidable para los huéspedes más exigentes."
    }
}

BENCHMARK_PRICE_RANGES = {
    "boutique": {
        "eje_cafetero": "$150.000 - $350.000 COP",
        "default": "$150.000 - $350.000 COP"
    },
    "standard": {
        "eje_cafetero": "$80.000 - $180.000 COP",
        "default": "$80.000 - $180.000 COP"
    },
    "luxury": {
        "eje_cafetero": "$350.000 - $800.000 COP",
        "default": "$350.000 - $800.000 COP"
    }
}


@dataclass
class BenchmarkResult:
    """Result from benchmark resolution."""
    value: Optional[str]
    sources: List[str]
    confidence: float
    is_benchmark: bool = False


class BenchmarkResolver:
    """
    Resuelve gaps de datos usando benchmark regional.
    
    Comportamiento:
    - Si value es real (no None, no vacío): devuelve el valor con alta confidence
    - Si value falta: usa benchmark regional según context
    - Nunca bloquea, siempre entrega algo útil
    """

    def __init__(self):
        """Initialize the benchmark resolver."""
        self._benchmark_cache: Dict[str, Any] = {}

    def resolve(
        self,
        field: str,
        value: Optional[str],
        context: Dict[str, Any]
    ) -> BenchmarkResult:
        """
        Resolve a field value using benchmark if needed.

        Args:
            field: Field name to resolve (e.g., 'telephone', 'addressLocality')
            value: Current value (None or empty means use benchmark)
            context: Context with region, country, hotel_type, etc.

        Returns:
            BenchmarkResult with value, sources, and confidence
        """
        region = context.get("region", "").lower()
        country = context.get("country", "").upper()
        hotel_type = context.get("hotel_type", "standard").lower()
        adr_benchmark = context.get("adr_benchmark")

        if value is not None and value != "":
            return self._resolve_with_real_data(value, context)

        if field in ["telephone", "phone", "contact"]:
            return self._resolve_telephone(region, country, context)
        
        if field in ["addressLocality", "city", "locality"]:
            return self._resolve_city(region, context)
        
        if field in ["description", "description_es"]:
            return self._resolve_description(hotel_type, region, context)
        
        if field in ["priceRange", "price_range"]:
            return self._resolve_price_range(hotel_type, region, adr_benchmark, context)
        
        if field in ["country"]:
            return self._resolve_country(region, country, context)
        
        if field in ["addressRegion", "region"]:
            return self._resolve_region(region, context)
        
        if field in ["name", "hotelName"]:
            return BenchmarkResult(
                value=None,
                sources=["benchmark"],
                confidence=0.0,
                is_benchmark=False
            )

        return BenchmarkResult(
            value=None,
            sources=["benchmark"],
            confidence=0.0,
            is_benchmark=False
        )

    def _resolve_with_real_data(
        self,
        value: str,
        context: Dict[str, Any]
    ) -> BenchmarkResult:
        """Handle case where we have real data."""
        source = "scraping" if context.get("from_scraping") else "user_input"
        return BenchmarkResult(
            value=value,
            sources=[source],
            confidence=0.9,
            is_benchmark=False
        )

    def _resolve_telephone(
        self,
        region: str,
        country: str,
        context: Dict[str, Any]
    ) -> BenchmarkResult:
        """Resolve telephone using benchmark format for region."""
        cross_reference = context.get("cross_reference", False)

        if region in ["eje_cafetero", "pereira", "santa_rosa"]:
            base_value = BENCHMARK_TELEPHONE_FORMAT
        else:
            base_value = "+57-000-0000"

        if cross_reference:
            confidence = 0.7
            sources = ["benchmark", "cross_reference"]
        else:
            confidence = 0.6
            sources = ["benchmark"]

        return BenchmarkResult(
            value=base_value,
            sources=sources,
            confidence=confidence,
            is_benchmark=True
        )

    def _resolve_city(
        self,
        region: str,
        context: Dict[str, Any]
    ) -> BenchmarkResult:
        """Resolve city using benchmark regional."""
        cross_reference = context.get("cross_reference", False)

        if region in ["eje_cafetero", "pereira"]:
            city = BENCHMARK_REGIONS.get(region, BENCHMARK_REGIONS["eje_cafetero"])["default_city"]
        elif region == "santa_rosa":
            city = "Santa Rosa de Cabal"
        else:
            city = "Pereira"

        if cross_reference:
            confidence = 0.7
            sources = ["benchmark", "cross_reference"]
        else:
            confidence = 0.6
            sources = ["benchmark"]

        return BenchmarkResult(
            value=city,
            sources=sources,
            confidence=confidence,
            is_benchmark=True
        )

    def _resolve_description(
        self,
        hotel_type: str,
        region: str,
        context: Dict[str, Any]
    ) -> BenchmarkResult:
        """Resolve description using benchmark based on hotel type."""
        descriptions = BENCHMARK_DESCRIPTIONS

        if region in ["eje_cafetero", "pereira", "santa_rosa"]:
            if hotel_type in descriptions:
                desc = descriptions[hotel_type].get("eje_cafetero", descriptions[hotel_type]["default"])
            else:
                desc = descriptions["standard"]["eje_cafetero"]
        else:
            desc = descriptions.get(hotel_type, descriptions["standard"])["default"]

        return BenchmarkResult(
            value=desc,
            sources=["benchmark"],
            confidence=0.6,
            is_benchmark=True
        )

    def _resolve_price_range(
        self,
        hotel_type: str,
        region: str,
        adr_benchmark: Optional[float],
        context: Dict[str, Any]
    ) -> BenchmarkResult:
        """Resolve price range using benchmark or ADR if available."""
        if adr_benchmark:
            price = f"${adr_benchmark:,.0f} COP"
            return BenchmarkResult(
                value=price,
                sources=["benchmark", "adr_reference"],
                confidence=0.75,
                is_benchmark=True
            )

        if region in ["eje_cafetero", "pereira", "santa_rosa"]:
            if hotel_type in BENCHMARK_PRICE_RANGES:
                price = BENCHMARK_PRICE_RANGES[hotel_type].get("eje_cafetero")
            else:
                price = BENCHMARK_PRICE_RANGES["standard"]["eje_cafetero"]
        else:
            price = BENCHMARK_PRICE_RANGES.get(hotel_type, BENCHMARK_PRICE_RANGES["standard"])["default"]

        return BenchmarkResult(
            value=price,
            sources=["benchmark"],
            confidence=0.6,
            is_benchmark=True
        )

    def _resolve_country(
        self,
        region: str,
        country: str,
        context: Dict[str, Any]
    ) -> BenchmarkResult:
        """Resolve country using benchmark."""
        if country == "CO" or region in ["eje_cafetero", "pereira", "santa_rosa"]:
            return BenchmarkResult(
                value="Colombia",
                sources=["benchmark"],
                confidence=0.6,
                is_benchmark=True
            )
        
        return BenchmarkResult(
            value="Colombia",
            sources=["benchmark"],
            confidence=0.5,
            is_benchmark=True
        )

    def _resolve_region(
        self,
        region: str,
        context: Dict[str, Any]
    ) -> BenchmarkResult:
        """Resolve region using benchmark."""
        if region in ["eje_cafetero", "pereira", "santa_rosa"]:
            return BenchmarkResult(
                value="Eje Cafetero",
                sources=["benchmark"],
                confidence=0.6,
                is_benchmark=True
            )
        
        return BenchmarkResult(
            value="Eje Cafetero",
            sources=["benchmark"],
            confidence=0.5,
            is_benchmark=True
        )

    def get_supported_fields(self) -> List[str]:
        """Return list of fields that can be resolved with benchmark."""
        return [
            "telephone",
            "phone",
            "contact",
            "addressLocality",
            "city",
            "locality",
            "description",
            "description_es",
            "priceRange",
            "price_range",
            "country",
            "addressRegion",
            "region"
        ]

    def get_benchmark_cities(self) -> List[str]:
        """Return list of benchmark cities available."""
        return ["Pereira", "Santa Rosa de Cabal"]
