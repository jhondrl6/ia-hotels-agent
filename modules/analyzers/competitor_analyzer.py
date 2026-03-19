"""
Competitor Analyzer v3 - Análisis de Competidores Cercanos con Auditoría GBP Real
==================================================================================

Utiliza Google Places API para identificar hoteles competidores cercanos
y ejecuta auditoría GBP completa para obtener GEO Scores reales (no estimados).

Author: IA Hoteles Team
Date: 2025-11-30
Version: 3.0 - Parallel GBP Audit
"""

import os
import time
import random
import logging
import requests
from typing import List, Dict, Optional
from math import radians, cos, sin, asin, sqrt
from concurrent.futures import ThreadPoolExecutor, as_completed

from modules.scrapers.google_places_client import get_places_client, GooglePlacesClient

logger = logging.getLogger(__name__)


class CompetitorAnalyzer:
    """Analiza competidores cercanos usando Google Places API (New) + Auditoría GBP Real"""

    def __init__(self, enable_full_audit: bool = True, use_places_client: bool = True):
        """
        Args:
            enable_full_audit: Si True, ejecuta auditoría GBP completa para competidores.
                              Si False, usa Places API directo (más rápido).
            use_places_client: Si True, usa el nuevo GooglePlacesClient con geo_score real.
        """
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        self.base_url_new = "https://places.googleapis.com/v1/places"
        self.base_url_legacy = "https://maps.googleapis.com/maps/api/place"
        self.enable_full_audit = enable_full_audit
        self.use_places_client = use_places_client
        self._places_client = None
        self._gbp_auditor = None

    def _get_places_client(self) -> Optional[GooglePlacesClient]:
        """Lazy load del Places Client."""
        if self._places_client is None and self.use_places_client:
            self._places_client = get_places_client()
        return self._places_client if self._places_client and self._places_client.is_available else None

    def _get_gbp_auditor(self):
        """Lazy load del GBP Auditor para evitar imports circulares."""
        if self._gbp_auditor is None:
            try:
                from modules.scrapers.gbp_auditor import GBPAuditor
                self._gbp_auditor = GBPAuditor(headless=True)
            except ImportError as e:
                logger.warning(f"No se pudo importar GBPAuditor: {e}")
                self._gbp_auditor = False  # Marcar como no disponible
        return self._gbp_auditor if self._gbp_auditor else None

    def get_nearby_competitors(
        self,
        hotel_name: str,
        lat: float,
        lng: float,
        radius_km: int = 15,
        location: str = ""
    ) -> List[Dict]:
        """
        Busca hoteles competidores cercanos usando Google Places API.
        
        Si use_places_client=True, usa GooglePlacesClient con geo_score real.
        Si enable_full_audit=True y use_places_client=False, ejecuta auditoría GBP completa.

        Args:
            hotel_name: Nombre del hotel cliente (para excluirlo)
            lat: Latitud del hotel cliente
            lng: Longitud del hotel cliente
            radius_km: Radio de búsqueda en kilómetros (default: 15 km)
            location: Ubicación textual para auditoría GBP (ej: "Santa Rosa de Cabal, Risaralda")

        Returns:
            Lista de hasta 5 competidores con información relevante:
            [
                {
                    'nombre': 'Hotel Termales San Vicente',
                    'rating': 4.8,
                    'reviews': 156,
                    'distancia_km': 3.2,
                    'fotos': 22,
                    'geo_score': 85,  # Score real (no estimado)
                    'geo_score_formula': {...},  # Desglose
                    'score_source': 'places_api_real'  # Indica fuente
                },
                ...
            ]

        Fallback: Si falla API o no hay key, retorna [] sin romper pipeline.
        """
        places_client = self._get_places_client()
        
        if places_client:
            print(f"   [INFO] Usando GooglePlacesClient con geo_score real")
            return self._get_competitors_with_places_client(
                places_client, hotel_name, lat, lng, radius_km
            )
        
        if not self.api_key:
            print("   [WARN] GOOGLE_MAPS_API_KEY no configurada - competidores omitidos")
            return []

        if not lat or not lng:
            print("   [WARN] Coordenadas inválidas - competidores omitidos")
            return []

        try:
            # Convertir radio a metros (Places API usa metros)
            radius_meters = radius_km * 1000

            # 1. Nearby Search usando Places API (New)
            # Endpoint: POST https://places.googleapis.com/v1/places:searchNearby
            nearby_url = f"{self.base_url_new}:searchNearby"
            
            headers = {
                'Content-Type': 'application/json',
                'X-Goog-Api-Key': self.api_key,
                'X-Goog-FieldMask': 'places.displayName,places.rating,places.userRatingCount,places.location,places.id,places.photos'
            }
            
            payload = {
                'includedTypes': ['lodging'],
                'maxResultCount': 20,
                'locationRestriction': {
                    'circle': {
                        'center': {
                            'latitude': lat,
                            'longitude': lng
                        },
                        'radius': float(radius_meters)
                    }
                }
            }

            response = requests.post(nearby_url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()

            results = data.get('places', [])
            
            if not results:
                print(f"   [INFO] Places API (New): No se encontraron hoteles cercanos")
                return []

            # 2. Procesar y filtrar competidores
            competitors = []
            for place in results:
                # Places API (New) uses displayName.text instead of name
                display_name = place.get('displayName', {})
                if isinstance(display_name, dict):
                    place_name = display_name.get('text', '')
                else:
                    place_name = str(display_name) if display_name else ''
                
                if not place_name:
                    continue

                # Excluir el hotel del cliente (comparación por similitud básica)
                if self._is_same_hotel(place_name, hotel_name):
                    continue

                # Calcular distancia desde el hotel cliente
                # Places API (New) uses location.latitude/longitude directly
                place_location = place.get('location', {})
                place_lat = place_location.get('latitude')
                place_lng = place_location.get('longitude')
                
                if not place_lat or not place_lng:
                    continue

                distance_km = self._haversine_distance(lat, lng, place_lat, place_lng)

                # Recopilar datos del competidor
                # Places API (New) field names
                rating = place.get('rating', 0.0)
                reviews = place.get('userRatingCount', 0)
                
                # Estimación de fotos (Places API no devuelve count directo)
                photos = len(place.get('photos', []))
                
                # GEO Score: Se auditará después si enable_full_audit=True
                # Por ahora usar estimación como placeholder
                geo_score = int(rating * 20) if rating > 0 else None

                competitor_data = {
                    'nombre': place_name,
                    'rating': rating,
                    'reviews': reviews,
                    'distancia_km': round(distance_km, 1),
                    'fotos': photos if photos > 0 else 'N/D',
                    'geo_score': geo_score,
                    'place_id': place.get('id'),  # New API uses 'id' instead of 'place_id'
                    'score_source': 'estimation'  # Será actualizado si se audita
                }

                competitors.append(competitor_data)

            # 3. Ordenar por rating descendente (proxy de calidad/relevancia)
            competitors.sort(key=lambda x: x['rating'], reverse=True)

            # 4. Tomar top 5 para auditoría
            top_competitors = competitors[:5]

            # 5. Si auditoría completa está habilitada, ejecutar en paralelo
            if self.enable_full_audit and top_competitors and location:
                top_competitors = self._audit_competitors_parallel(top_competitors, location)

            return top_competitors

        except requests.exceptions.Timeout:
            print("   [WARN] Timeout en Places API - competidores omitidos")
            return []
        except requests.exceptions.RequestException as e:
            print(f"   [WARN] Error en Places API: {e} - competidores omitidos")
            return []
        except Exception as e:
            print(f"   [WARN] Error inesperado en análisis de competidores: {e}")
            return []

    def _audit_competitors_parallel(
        self, 
        competitors: List[Dict], 
        location: str,
        max_workers: int = 3
    ) -> List[Dict]:
        """
        Ejecuta auditoría GBP completa para competidores en paralelo.
        
        Args:
            competitors: Lista de competidores con datos básicos de Places API
            location: Ubicación para búsqueda GBP
            max_workers: Número máximo de workers paralelos (default: 3)
            
        Returns:
            Lista de competidores con GEO Scores auditados
        """
        auditor = self._get_gbp_auditor()
        if not auditor:
            logger.warning("GBP Auditor no disponible - usando estimaciones")
            return competitors
        
        print(f"   [INFO] Auditando GBP de {len(competitors)} competidores...")
        
        def audit_single(competitor: Dict) -> Dict:
            """Audita un competidor individual con delay anti-bloqueo."""
            # Delay aleatorio para evitar rate limiting (2-5 segundos)
            delay = random.uniform(2.0, 5.0)
            time.sleep(delay)
            
            try:
                audit_result = auditor.audit_competitor_profile(
                    hotel_name=competitor['nombre'],
                    location=location
                )
                
                if audit_result and audit_result.get('geo_score') is not None:
                    # Actualizar con datos auditados
                    competitor['geo_score'] = audit_result['geo_score']
                    competitor['reviews'] = audit_result.get('reviews', competitor['reviews'])
                    competitor['rating'] = audit_result.get('rating', competitor['rating'])
                    competitor['fotos'] = audit_result.get('fotos', competitor['fotos'])
                    competitor['score_source'] = audit_result.get('source', 'gbp_audit')
                    logger.info(f"   ✓ {competitor['nombre']}: GEO {audit_result['geo_score']}/100")
                else:
                    logger.warning(f"   ⚠ {competitor['nombre']}: Auditoría sin resultados, usando estimación")
                    
            except Exception as e:
                logger.warning(f"   ⚠ Error auditando {competitor['nombre']}: {e}")
            
            return competitor
        
        # Ejecutar auditorías en paralelo con ThreadPoolExecutor
        audited_competitors = []
        
        try:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_competitor = {
                    executor.submit(audit_single, comp): comp 
                    for comp in competitors
                }
                
                for future in as_completed(future_to_competitor):
                    try:
                        result = future.result(timeout=120)  # 2 min timeout por competidor
                        audited_competitors.append(result)
                    except Exception as e:
                        original = future_to_competitor[future]
                        logger.warning(f"   ⚠ Timeout/Error en {original['nombre']}: {e}")
                        audited_competitors.append(original)
                        
        except Exception as e:
            logger.error(f"Error en auditoría paralela: {e}")
            return competitors
        
        # Mantener orden original por rating
        audited_competitors.sort(key=lambda x: x.get('rating', 0), reverse=True)
        
        audited_count = sum(1 for c in audited_competitors if c.get('score_source') == 'gbp_audit')
        print(f"   [OK] {audited_count}/{len(audited_competitors)} competidores auditados correctamente")
        
        return audited_competitors

    def _get_competitors_with_places_client(
        self,
        client: GooglePlacesClient,
        hotel_name: str,
        lat: float,
        lng: float,
        radius_km: float
    ) -> List[Dict]:
        """
        Obtiene competidores usando el nuevo GooglePlacesClient.
        
        Ventajas:
        - geo_score real (no estimación rating*20)
        - Caché automático con TTL 30 días
        - Datos verificados desde Places API
        """
        try:
            places = client.search_nearby_lodging(lat, lng, radius_km, max_results=20)
            
            if not places:
                print(f"   [INFO] Places API: No se encontraron hoteles cercanos")
                return []
            
            competitors = []
            for place in places:
                if self._is_same_hotel(place.name, hotel_name):
                    continue
                
                competitor_data = {
                    'nombre': place.name,
                    'rating': place.rating,
                    'reviews': place.reviews,
                    'distancia_km': round(self._haversine_distance(lat, lng, place.lat, place.lng), 1),
                    'fotos': place.photos,
                    'geo_score': place.geo_score,
                    'geo_score_formula': place.geo_score_formula,
                    'place_id': place.place_id,
                    'score_source': 'places_api_real',
                    'has_hours': place.has_hours,
                    'has_website': place.has_website,
                    'data_source': place.data_source,
                }
                competitors.append(competitor_data)
            
            competitors.sort(key=lambda x: x.get('geo_score', 0), reverse=True)
            
            return competitors[:5]
            
        except Exception as e:
            print(f"   [WARN] Error en Places Client: {e}")
            return []

    def _is_same_hotel(self, name1: str, name2: str) -> bool:
        """
        Compara dos nombres de hoteles para determinar si son el mismo.
        """
        if not name1 or not name2:
            return False
        
        def normalize(s: str) -> str:
            s = s.lower().strip()
            replacements = {
                'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ü': 'u', 'ñ': 'n'
            }
            for old, new in replacements.items():
                s = s.replace(old, new)
            return s
        
        norm1 = normalize(name1)
        norm2 = normalize(name2)
        
        stop_words = {'hotel', 'hostal', 'boutique', 'lodge', 'resort', 'spa', 'the', 'la', 'el', 'de', 'del'}
        
        words1 = set(w for w in norm1.split() if w not in stop_words and len(w) > 2)
        words2 = set(w for w in norm2.split() if w not in stop_words and len(w) > 2)
        
        common_words = words1 & words2
        
        is_substring = norm1 in norm2 or norm2 in norm1
        
        return len(common_words) >= 2 or is_substring

    def _haversine_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calcula la distancia en kilómetros entre dos puntos geográficos
        usando la fórmula de Haversine.
        """
        # Radio de la Tierra en kilómetros
        R = 6371.0

        # Convertir grados a radianes
        lat1_rad = radians(lat1)
        lng1_rad = radians(lng1)
        lat2_rad = radians(lat2)
        lng2_rad = radians(lng2)

        # Diferencias
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad

        # Fórmula de Haversine
        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlng / 2)**2
        c = 2 * asin(sqrt(a))

        distance = R * c
        return distance
