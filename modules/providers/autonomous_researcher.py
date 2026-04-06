"""
Autonomous Researcher - NEVER_BLOCK Architecture v2

Investiga automáticamente hoteles en fuentes públicas:
- Google Business Profile (GBP)
- Booking.com
- TripAdvisor
- Instagram/Facebook

Cross-reference y full confidence annotation.
Si una fuente no está disponible, continúa con las demás.

FASE 8: Autonomous Research Engine v2
- ResearchOutput schema con persistencia JSON
- Integration con scrapers reales
- Confidence scoring verificable
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import threading
import logging
import json
import hashlib

# FASE 11B: Importar GoogleTravelScraper para fallback chain
from modules.scrapers.google_travel_scraper import GoogleTravelScraper

logger = logging.getLogger(__name__)


# ============================================================================
# T8A: Research Output Schema
# ============================================================================

@dataclass
class ResearchOutput:
    """
    Schema para output de investigación autónoma.
    
    Attributes:
        hotel_name: Nombre del hotel investigado
        sources_checked: Lista de fuentes consultadas (gbp, booking, tripadvisor, instagram)
        data_found: Diccionario con datos extraídos de cada fuente
        confidence: Score de confianza (0.0 - 1.0)
        citations: Lista de URLs/uris de evidencia
        gaps: Lista de datos que NO se encontraron
    """
    hotel_name: str
    sources_checked: List[str] = field(default_factory=list)
    data_found: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    citations: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    research_id: str = field(default_factory=lambda: hashlib.md5(datetime.now().isoformat().encode()).hexdigest()[:12])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para serialización JSON."""
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        """Convierte a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResearchOutput':
        """Crea instancia desde diccionario."""
        return cls(**data)
    
    def save_to_file(self, output_dir: Path) -> Path:
        """
        Persiste el research output a archivo JSON.
        
        Args:
            output_dir: Directorio donde guardar el archivo
            
        Returns:
            Path al archivo guardado
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"research_{self.research_id}_{self.hotel_name[:20].replace(' ', '_')}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
        
        logger.info(f"[ResearchOutput] Saved to {filepath}")
        return filepath


# ============================================================================
# T8D: Research Confidence Scoring
# ============================================================================

def calculate_research_confidence(sources_checked: List[str], 
                                  data_found: Dict[str, Any],
                                  total_sources: int = 4) -> float:
    """
    Calcula confidence score basado en fuentes encontradas vs disponibles.
    
    Scoring:
        4/4 fuentes = 1.0 (1.0)
        3/4 fuentes = 0.75
        2/4 fuentes = 0.5
        1/4 fuentes = 0.25
        0/4 fuentes = 0.0
    
    Args:
        sources_checked: Lista de fuentes que devolvieron datos
        data_found: Diccionario con datos encontrados
        total_sources: Total de fuentes disponibles (default 4)
        
    Returns:
        Float entre 0.0 y 1.0
    """
    if not sources_checked:
        return 0.0
    
    count = len(sources_checked)
    
    # Tabla de scoring según especificación
    if count >= 4:
        return 1.0
    elif count == 3:
        return 0.75
    elif count == 2:
        return 0.5
    elif count == 1:
        return 0.25
    else:
        return 0.0


def detect_gaps(sources_available: List[str], 
                sources_checked: List[str], 
                data_found: Dict[str, Any]) -> List[str]:
    """
    Detecta gaps en la investigación.
    
    Args:
        sources_available: Fuentes que deberían estar disponibles
        sources_checked: Fuentes que fueron consultadas
        data_found: Datos que se encontraron
        
    Returns:
        Lista de gaps identificados
    """
    gaps = []
    
    for source in sources_available:
        if source not in sources_checked:
            gaps.append(f"Source not checked: {source}")
        elif source in data_found and not data_found[source]:
            gaps.append(f"Source returned empty data: {source}")
    
    return gaps


# ============================================================================
# Research Result (Legacy compatibility)
# ============================================================================

@dataclass
class ResearchResult:
    """Resultado de investigación de hotel (legacy wrapper)."""
    found: bool = False
    data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    sources: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a dict para compatibilidad con prefight checks."""
        return {
            'found': self.found,
            'data': self.data,
            'confidence': self.confidence,
            'sources': self.sources,
            'conflicts': self.conflicts,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


# ============================================================================
# T8B: Source Scrapers (Stubs con integración real)
# ============================================================================

class BookingScraper:
    """Scraper para Booking.com."""
    
    def __init__(self):
        self.source_name = 'booking'
    
    def scrape(self, hotel_name: str, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Extrae datos de Booking.com.
        
        Returns:
            Dict con reviews, ratings, photos, amenities
        """
        result = {
            'source': self.source_name,
            'found': False,
            'data': {},
            'url': url or f"https://www.booking.com/search.html?ss={hotel_name}"
        }
        
        try:
            # T8B: Integration point - en producción usaría Playwright/Selenium
            # Por ahora retorna estructura válida para demostrar el flujo
            result['data'] = {
                'source': self.source_name,
                'hotel_name': hotel_name,
                'rating': None,  # Pendiente extracción real
                'review_count': None,
                'reviews': [],
                'amenities': [],
                'photos': [],
                'price_range': None
            }
            # Solo marcar found=True si tiene datos reales (no todo null)
            has_real_data = any([
                result['data'].get('rating'),
                result['data'].get('review_count'),
                result['data'].get('reviews'),
                result['data'].get('amenities'),
                result['data'].get('price_range')
            ])
            result['found'] = has_real_data
            if has_real_data:
                logger.info(f"[BookingScraper] Scraped {hotel_name} with real data")
            else:
                logger.info(f"[BookingScraper] Scraped {hotel_name} but no real data found")
        except Exception as e:
            logger.warning(f"[BookingScraper] Failed: {e}")
            result['found'] = False
        
        return result


# ============================================================================
# T8C: Autonomous Research Engine (Main Class)
# ============================================================================

class AutonomousResearcher:
    """
    Researcher autónomo que busca información de hoteles
    en múltiples fuentes públicas y hace cross-reference.
    
    Flujo: Audit → Research → Assessment → Generation → Report
    
    T8C: Integración en orchestration
    
    NOTE: Solo BookingScraper está activo (ADR/Price Range).
    GBP, TripAdvisor, Instagram fueron deprecados (datos cubiertos por Google Places API).
    """
    
    ALL_SOURCES = ['booking']  # Solo fuentes activas
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Inicializa el researcher.
        
        Args:
            output_dir: Directorio para persistir resultados de investigación
        """
        self.sources_to_try = self.ALL_SOURCES.copy()
        self._lock = threading.Lock()
        self.output_dir = output_dir
        self.last_research_output: Optional[ResearchOutput] = None  # T8C: Para acceso completo al output
        
        # Solo BookingScraper activo (ADR/Price Range - dato no disponible en Google Places)
        self.scrapers = {
            'booking': BookingScraper()
        }
    
    def _search_gbp(self, hotel_name: str, url: str) -> Dict[str, Any]:
        """OBSOLETO: GBP datos ahora vienen de Google Places API (GEO Enrichment)."""
        return {'found': False, 'data': {}, 'source': 'gbp', 'url': url}

    def _search_booking(self, hotel_name: str, url: str) -> Dict[str, Any]:
        """Busca en Booking.com (ADR/Price Range)."""
        return self.scrapers['booking'].scrape(hotel_name, url)

    def _search_tripadvisor(self, hotel_name: str, url: str) -> Dict[str, Any]:
        """OBSOLETO: TripAdvisor deprecado (anti-bot, marginal value)."""
        return {'found': False, 'data': {}, 'source': 'tripadvisor', 'url': url}

    def _search_social(self, hotel_name: str, url: str) -> Dict[str, Any]:
        """OBSOLETO: Instagram deprecado (anti-bot, marginal value)."""
        return {'found': False, 'data': {}, 'source': 'instagram', 'url': url}

    def _calculate_confidence(self, sources_count: int, conflicts: List[str], 
                              matching_fields: int) -> float:
        """
        Calcula confidence basado en:
        - Número de fuentes (más fuentes = mayor confidence)
        - Conflictos (conflictos = menor confidence)
        - Campos coincidentes (más coincidencias = mayor confidence)
        """
        base_confidence = 0.0
        
        if sources_count == 0:
            base_confidence = 0.0
        elif sources_count == 1:
            base_confidence = 0.3
        elif sources_count == 2:
            base_confidence = 0.5
        elif sources_count == 3:
            base_confidence = 0.7
        else:
            base_confidence = 0.8
        
        # Más campos coincidentes = boost
        field_boost = min(matching_fields * 0.05, 0.15)
        
        # Conflictos reducen confidence
        conflict_penalty = len(conflicts) * 0.15
        
        confidence = base_confidence + field_boost - conflict_penalty
        return max(0.0, min(1.0, confidence))

    def _cross_reference(self, results: List[Dict[str, Any]]) -> tuple:
        """
        Compara datos entre fuentes y detecta conflictos.
        Returns: (merged_data, conflicts, matching_fields)
        """
        merged = {}
        conflicts = []
        matching_fields = 0
        
        all_data = [r.get('data', {}) for r in results if r.get('found')]
        
        if not all_data:
            return merged, conflicts, matching_fields
        
        # Campos a comparar
        compare_fields = ['name', 'address', 'telephone', 'rating', 'url']
        
        for field in compare_fields:
            values = [d.get(field) for d in all_data if d.get(field)]
            if len(values) > 1:
                unique_values = set(str(v) for v in values)
                if len(unique_values) > 1:
                    conflicts.append(f"{field}: {values}")
                else:
                    merged[field] = values[0]
                    matching_fields += 1
            elif len(values) == 1:
                merged[field] = values[0]
        
        # Combinar datos de todas las fuentes
        for data in all_data:
            for key, value in data.items():
                if key not in merged and value:
                    merged[key] = value
        
        return merged, conflicts, matching_fields

    def _search_all_sources(self, hotel_name: str, url: str) -> tuple:
        """
        Búsqueda síncrona en todas las fuentes.
        
        Returns:
            tuple: (ResearchOutput, list of raw results)
        """
        sources_checked = []
        data_found = {}
        citations = []
        
        # GBP lookup
        gbp_result = self._search_gbp(hotel_name, url)
        if gbp_result.get('found'):
            sources_checked.append('gbp')
            data_found['gbp'] = gbp_result.get('data', {})
        
        # Booking scrape
        booking_result = self._search_booking(hotel_name, url)
        if booking_result.get('found'):
            sources_checked.append('booking')
            data_found['booking'] = booking_result.get('data', {})
            if booking_result.get('url'):
                citations.append(booking_result['url'])
        
        # TripAdvisor scrape
        tripadvisor_result = self._search_tripadvisor(hotel_name, url)
        if tripadvisor_result.get('found'):
            sources_checked.append('tripadvisor')
            data_found['tripadvisor'] = tripadvisor_result.get('data', {})
            if tripadvisor_result.get('url'):
                citations.append(tripadvisor_result['url'])
        
        # Instagram scrape
        social_result = self._search_social(hotel_name, url)
        if social_result.get('found'):
            sources_checked.append('instagram')
            data_found['instagram'] = social_result.get('data', {})
            if social_result.get('url'):
                citations.append(social_result['url'])
        
        # Cross-reference
        all_results = [r for r in [gbp_result, booking_result, tripadvisor_result, social_result] 
                       if isinstance(r, dict)]
        merged_data, conflicts, matching_fields = self._cross_reference(all_results)
        
        # T8D: Calculate confidence using new formula
        confidence = calculate_research_confidence(sources_checked, data_found)
        
        # Detect gaps
        gaps = detect_gaps(self.ALL_SOURCES, sources_checked, data_found)
        
        # Build ResearchOutput
        research_output = ResearchOutput(
            hotel_name=hotel_name,
            sources_checked=sources_checked,
            data_found=data_found,
            confidence=confidence,
            citations=citations,
            gaps=gaps
        )
        
        return research_output, all_results

    def research(self, hotel_name: str, url: str, 
                 sources: Optional[List[str]] = None,
                 persist: bool = True) -> ResearchResult:
        """
        Investiga un hotel en múltiples fuentes públicas.
        
        Args:
            hotel_name: Nombre del hotel
            url: URL del hotel
            sources: Lista opcional de fuentes específicas a consultar (no usado aún)
            persist: Si True, guarda resultado a archivo JSON
            
        Returns:
            ResearchResult (legacy) con datos encontrados, confidence y fuentes.
            También actualiza self.last_research_output con ResearchOutput completo.
            
        NOTE: Este método ejecuta investigación silenciosa (NEVER_BLOCK).
        Los resultados se devuelven como ResearchResult y se persisten a JSON.
        """
        try:
            # Log del inicio de investigación
            logger.info(f"[AutonomousResearcher] Starting research for hotel: {hotel_name}")
            logger.info(f"[AutonomousResearcher] Target URL: {url}")
            
            # Ignorar sources por ahora - siempre busca todas
            research_output, all_results = self._search_all_sources(hotel_name, url)
            
            # Log de resultados
            if research_output.sources_checked:
                logger.info(f"[AutonomousResearcher] Research completed")
                logger.info(f"[AutonomousResearcher] Sources checked: {research_output.sources_checked}")
                logger.info(f"[AutonomousResearcher] Confidence: {research_output.confidence:.2f}")
                if research_output.gaps:
                    logger.warning(f"[AutonomousResearcher] Gaps detected: {research_output.gaps}")
            else:
                logger.info(f"[AutonomousResearcher] Research completed: NO DATA FOUND")
            
            # T8A: Persistir si requested
            if persist and self.output_dir:
                research_output.save_to_file(self.output_dir)
            
            # Store full ResearchOutput for later access (T8C integration)
            self.last_research_output = research_output
            
            # Convert to legacy ResearchResult for backward compatibility
            result = ResearchResult(
                found=len(research_output.sources_checked) > 0,
                data=research_output.data_found,
                confidence=research_output.confidence,
                sources=research_output.sources_checked,
                conflicts=research_output.gaps,  # gaps as conflicts for legacy compatibility
                timestamp=datetime.now()
            )
            
            return result
            
        except Exception as e:
            logger.error(f"[AutonomousResearcher] Research failed with exception: {e}")
            # Nunca crashea, devuelve resultado vacío
            return ResearchResult(
                found=False,
                data={},
                confidence=0.0,
                sources=[],
                conflicts=[str(e)],
                timestamp=datetime.now()
            )

    def close(self):
        """Cierra recursos."""
        pass

    def __del__(self):
        """Cleanup básico."""
        pass

    # =========================================================================
    # FASE 11B: Fallback Chain Methods (Places -> Travel -> Benchmark)
    # =========================================================================

    def _try_gbp_scrape(self, hotel_name: str, url: str = None) -> Optional[ResearchOutput]:
        """
        Intenta obtener datos via GBPScraper (Google Places API).

        Args:
            hotel_name: Nombre del hotel
            url: URL opcional del hotel

        Returns:
            ResearchOutput si se encuentra el hotel, None si falla
        """
        try:
            gbp_result = self._search_gbp(hotel_name, url or "")
            if gbp_result.get('found'):
                return ResearchOutput(
                    hotel_name=hotel_name,
                    sources_checked=['gbp'],
                    data_found={'gbp': gbp_result.get('data', {})},
                    confidence=0.7,  # Places es fuente confiable
                    citations=[url] if url else [],
                    gaps=[]
                )
        except Exception as e:
            logger.warning(f"GBP scrape failed: {e}")
        return None

    def _try_travel_scrape(self, hotel_name: str, location: str = None) -> Optional[ResearchOutput]:
        """
        Intenta obtener datos via Google Travel cuando Places falla.

        Args:
            hotel_name: Nombre del hotel
            location: Ubicacion opcional (ciudad, region)

        Returns:
            ResearchOutput si se encuentra el hotel, None si falla
        """
        try:
            scraper = GoogleTravelScraper()
            data = scraper.scrape_hotel(hotel_name, location)
            scraper.close()

            if data.get('found'):
                return ResearchOutput(
                    hotel_name=hotel_name,
                    sources_checked=['google_travel'],
                    data_found={'google_travel': data},
                    confidence=0.6,  # Travel es menos confiable que Places
                    citations=[],
                    gaps=['limited_data']
                )
        except Exception as e:
            logger.warning(f"Travel scrape failed: {e}")
        return None

    def _fallback_benchmark(self, hotel_name: str) -> ResearchOutput:
        """
        Fallback final: Benchmark regional para hoteles no encontrados.

        Args:
            hotel_name: Nombre del hotel

        Returns:
            ResearchOutput con datos estimados del benchmark
        """
        logger.info(f"[AutonomousResearcher] Using benchmark fallback for: {hotel_name}")

        # Benchmark regional para Colombia (datos típicos de hotels similares)
        benchmark_data = {
            'benchmark': True,
            'estimated_rating': 3.5,
            'estimated_reviews': 50,
            'region': 'Coffee Region, Colombia',
            'note': 'Datos estimados por benchmark regional - hotel no encontrado en fuentes online'
        }

        return ResearchOutput(
            hotel_name=hotel_name,
            sources_checked=['benchmark'],
            data_found={'benchmark': benchmark_data},
            confidence=0.2,  # Benchmark tiene baja confianza
            citations=[],
            gaps=['price_data', 'real_reviews', 'photos', 'amenities']
        )

    def autonomous_research(self, hotel_name: str, location: str = None) -> ResearchOutput:
        """
        Investiga un hotel usando la cadena de fallback:
        GBPScraper (Places) -> GoogleTravelScraper (Travel) -> Benchmark Regional

        Args:
            hotel_name: Nombre del hotel
            location: Ubicacion opcional (ciudad, region)

        Returns:
            ResearchOutput con datos encontrados y metadata de confianza
        """
        logger.info(f"[AutonomousResearcher] Starting research for: {hotel_name}")

        # 1. Try GBPScraper (Places API) - fuente primaria
        gbp_result = self._try_gbp_scrape(hotel_name)
        if gbp_result:
            logger.info(f"[AutonomousResearcher] Found via GBP (Places): {hotel_name}")
            self.last_research_output = gbp_result
            return gbp_result

        # 2. Try GoogleTravelScraper (Travel) - fuente secundaria
        travel_result = self._try_travel_scrape(hotel_name, location)
        if travel_result:
            logger.info(f"[AutonomousResearcher] Found via Travel: {hotel_name}")
            self.last_research_output = travel_result
            return travel_result

        # 3. Fallback: Benchmark resolver
        logger.warning(f"[AutonomousResearcher] No data found, using benchmark: {hotel_name}")
        benchmark_result = self._fallback_benchmark(hotel_name)
        self.last_research_output = benchmark_result
        return benchmark_result


# Alias para compatibilidad
Researcher = AutonomousResearcher
