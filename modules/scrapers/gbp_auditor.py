import copy
import json
import logging
import os
import time
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

try:  # Dependencia opcional; Selenium Manager se usa como fallback
    from webdriver_manager.chrome import ChromeDriverManager  # type: ignore
except ImportError:  # pragma: no cover - entorno sin webdriver_manager
    ChromeDriverManager = None

# Geographic validation import
from modules.utils.geo_validator import get_geo_validator, ValidationResult
# Horarios detection import
from modules.utils.horarios_detector import HorariosDetector
from modules.utils.benchmarks import BenchmarkLoader
from modules.utils.dynamic_impact import DynamicImpactCalculator, get_detected_issues

logger = logging.getLogger(__name__)


class GBPAuditor:
    """
    AUDITORÍA DE FUGAS DE RESERVAS PARA GOOGLE BUSINESS PROFILE
    Enfocado en calcular el impacto financiero de un perfil GBP suboptimizado.
    """

    PERDIDA_MENSUAL_BASE = 2_800_000  # COP - Benchmark Plan Maestro v2.2 (Caribe RevPAR 270.6k)

    IMPACTOS_FINANCIEROS = {
        'PERFIL_NO_RECLAMADO': {
            'factor': 1.0,
            'cop_mes': 2_100_000,
            'descripcion': 'Invisible total en búsquedas locales'
        },
        'FOTOS_INSUFICIENTES': {
            'factor': 0.35,
            'cop_mes': 735_000,
            'descripcion': 'Google penaliza relevancia local vs competencia'
        },
        'RESENAS_CRITICAS': {
            'factor': 0.40,
            'cop_mes': 840_000,
            'descripcion': 'Descalificado del shortlist de Google Maps'
        },
        'SIN_WHATSAPP': {
            'factor': 0.30,
            'cop_mes': 630_000,
            'descripcion': '30% de consultas inmediatas nunca llegan'
        },
        'PERFIL_ABANDONADO': {
            'factor': 0.25,
            'cop_mes': 525_000,
            'descripcion': 'Google aplica degradación algorítmica'
        },
        'SIN_FAQ': {
            'factor': 0.20,
            'cop_mes': 420_000,
            'descripcion': 'No responde al modelo conversacional de Google'
        },
        'RATING_BAJO': {
            'factor': 0.45,
            'cop_mes': 945_000,
            'descripcion': 'Excluido automáticamente de recomendaciones'
        },
        'SIN_HORARIOS': {
            'factor': 0.15,
            'cop_mes': 315_000,
            'descripcion': 'Señal de negocio informal o cerrado'
        },
        'SIN_WEBSITE': {
            'factor': 0.25,
            'cop_mes': 525_000,
            'descripcion': 'Fuerza dependencia 100% de OTAs'
        },
        'CERO_ACTIVIDAD_RECIENTE': {
            'factor': 0.30,
            'cop_mes': 630_000,
            'descripcion': 'Google interpreta como negocio inactivo'
        },
    }

    CACHE_MAX_AGE_DAYS = 14

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self._driver_status = {"available": False, "error": None}
        self.cache_path = Path("data/cache/gbp_profiles.json")
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache = self._load_cache()
        self.benchmark_loader = BenchmarkLoader()
        self.hotel_data = None
        self.region = "default"

    def _load_cache(self) -> dict:
        if not self.cache_path.exists():
            return {}
        try:
            return json.loads(self.cache_path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning("Cache GBP corrupto: %s", exc)
            return {}

    def _save_cache(self, key: str, data: dict) -> None:
        try:
            profile_copy = copy.deepcopy(data)
            self.cache[key] = {
                "timestamp": datetime.utcnow().isoformat(),
                "profile": profile_copy,
            }
            self.cache_path.write_text(json.dumps(self.cache, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as exc:
            logger.warning("No se pudo guardar cache GBP: %s", exc)

    def _build_cache_key(self, hotel_name: str, location: str) -> str:
        base = f"{(hotel_name or '').strip().lower()}::{(location or '').strip().lower()}"
        return base or "__unknown__"

    def _get_cached_profile(self, hotel_name: str, location: str) -> dict:
        key = self._build_cache_key(hotel_name, location)
        cached = self.cache.get(key)
        if not cached:
            return {}
        try:
            ts = datetime.fromisoformat(cached.get("timestamp"))
            age = (datetime.utcnow() - ts).days
        except Exception:
            age = None
        profile = copy.deepcopy(cached.get("profile", {}))
        profile.setdefault("meta", {})
        profile["meta"].update({
            "fallback_source": "cache",
            "cache_age_days": age,
        })
        return profile

    def _base_profile(self) -> dict:
        return {
            'existe': False,
            'score': 0,
            'issues': [],
            'reviews': 0,
            'rating': 0.0,
            'fotos': 0,
            'horarios': False,
            'descripcion': False,
            'website': False,
            'telefono': False,
            'whatsapp_visible': False,
            'posts': 0,
            'tiene_qa': False,
            'ultima_actividad_dias': None,
            'fugas_detectadas': [],
            'perdida_total_mes_COP': 0,
            'perdida_anual_COP': 0,
            'prioridad_accion': None,
            'meta': {},
        }

    def _init_driver(self) -> bool:
        if self.driver:
            return True

        options = Options()
        if self.headless:
            options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        driver_path = os.getenv('WEBDRIVER_PATH')
        try:
            service: Optional[Service] = None

            if driver_path and Path(driver_path).exists():
                service = Service(driver_path)
            elif ChromeDriverManager is not None:
                service = Service(ChromeDriverManager().install())

            if service is not None:
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                # Selenium Manager (Selenium 4.13+) resuelve driver automáticamente
                self.driver = webdriver.Chrome(options=options)

            self._driver_status = {"available": True, "error": None}
            return True
        except Exception as exc:
            self._driver_status = {"available": False, "error": str(exc)}
            logger.warning("Selenium driver no disponible: %s", exc)
            self.driver = None
            return False

    def _fallback_profile(self, hotel_name: str, location: str) -> dict:
        cached_profile = self._get_cached_profile(hotel_name, location)
        if cached_profile:
            cached_profile.setdefault('issues', []).append('GBP audit reutilizo cache por indisponibilidad del driver')
            cached_profile['meta'].update({
                'audit_status': 'cache_reused',
                'driver_error': self._driver_status.get('error'),
            })
            return cached_profile

        profile = self._base_profile()
        profile['issues'].append('GBP audit no ejecutada: Selenium driver no disponible y sin cache previa')
        profile['meta'].update({
            'audit_status': 'unavailable',
            'driver_error': self._driver_status.get('error'),
        })
        return profile

    def _record_session_meta(self, profile_data: dict) -> None:
        profile_data.setdefault('meta', {})
        profile_data['meta'].update({
            'driver_available': self._driver_status.get('available'),
            'driver_error': self._driver_status.get('error'),
            'timestamp_utc': datetime.utcnow().isoformat(),
        })

    @staticmethod
    def _build_resolved_location(validation_result: Optional[ValidationResult], fallback_location: str) -> str:
        if validation_result and validation_result.resolved_location:
            return validation_result.resolved_location
        return (fallback_location or '').strip()

    @staticmethod
    def _prepare_search_locations(original_location: str, validation_result: Optional[ValidationResult]) -> List[str]:
        candidates: List[str] = []
        original_clean = (original_location or '').strip()
        if validation_result and validation_result.resolved_location:
            resolved_clean = validation_result.resolved_location.strip()
            if resolved_clean and resolved_clean.lower() != original_clean.lower():
                candidates.append(resolved_clean)
        if original_clean:
            candidates.append(original_clean)

        ordered: List[str] = []
        seen = set()
        for item in candidates:
            key = item.lower()
            if key and key not in seen:
                ordered.append(item)
                seen.add(key)
        return ordered or ['']

    @staticmethod
    def _parse_int(value: str) -> Optional[int]:
        if not value:
            return None
        cleaned = value.strip().lower().replace(',', '.').replace('mil', 'k')
        multiplier = 1
        if cleaned.endswith('k'):
            multiplier = 1000
            cleaned = cleaned[:-1].strip()
        digits = re.sub(r'[^0-9\.]', '', cleaned)
        if not digits:
            return None
        try:
            base_value = float(digits)
        except ValueError:
            return None
        return int(base_value * multiplier)

    @staticmethod
    def _parse_float(value: str) -> Optional[float]:
        if not value:
            return None
        cleaned = value.replace(',', '.').strip()
        try:
            return float(cleaned)
        except ValueError:
            match = re.search(r'([0-9]+(?:[.,][0-9]+)?)', cleaned)
            if match:
                return float(match.group(1).replace(',', '.'))
        return None

    def _capture_html_snapshot(self) -> str:
        try:
            html = self.driver.page_source
        except Exception:
            return ""
        if not html:
            return ""
        return html[:5000]

    def _ensure_main_panel(self) -> None:
        try:
            WebDriverWait(self.driver, 12).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='main']"))
            )
        except TimeoutException:
            pass

    def _extract_metrics(self, html_snapshot: str, profile_data: dict) -> None:
        meta_debug = profile_data.setdefault('meta', {}).setdefault('scrape_debug', {})
        confidence = profile_data.setdefault('meta', {}).setdefault('data_confidence', {})

        rating_val: Optional[float] = None
        reviews_val: Optional[int] = None
        photos_val: Optional[int] = None

        try:
            rating_candidates = self.driver.find_elements(By.CSS_SELECTOR, "[aria-label*='estrellas']")
            rating_candidates += self.driver.find_elements(By.XPATH, "//*[contains(@aria-label, 'estrellas')]")
        except Exception:
            rating_candidates = []

        for candidate in rating_candidates:
            try:
                label = candidate.get_attribute('aria-label') or candidate.text
            except StaleElementReferenceException:
                continue
            if not label:
                continue
            rating = self._parse_float(label)
            reviews = None
            reviews_match = re.search(r'(\d+[\d\s\.,]*)\s*reseñ', label, re.IGNORECASE)
            if reviews_match:
                reviews = self._parse_int(reviews_match.group(1))
            if rating is not None:
                rating_val = rating
                confidence['rating'] = True
                meta_debug['rating_source'] = 'aria-label'
            if reviews is not None:
                reviews_val = reviews
                confidence['reviews'] = True
                meta_debug['reviews_source'] = 'aria-label'
            if rating_val is not None and reviews_val is not None:
                break

        if rating_val is None or reviews_val is None:
            regex = re.search(r'([0-5](?:[\.,][0-9])?)\s*estrellas?\s*(?:en\s*)?(\d+[\d\s\.,]*)\s*(reseñas|opiniones)', html_snapshot, re.IGNORECASE)
            if regex:
                if rating_val is None:
                    rating_val = self._parse_float(regex.group(1))
                    confidence['rating'] = True
                    meta_debug['rating_source'] = 'regex_html'
                if reviews_val is None:
                    reviews_val = self._parse_int(regex.group(2))
                    confidence['reviews'] = True
                    meta_debug['reviews_source'] = 'regex_html'

        if rating_val is not None:
            profile_data['rating'] = rating_val
        else:
            confidence.setdefault('rating', False)

        if reviews_val is not None:
            profile_data['reviews'] = reviews_val
        else:
            confidence.setdefault('reviews', False)

        try:
            # v3.3.2: Selectores expandidos para manejar cambios en Maps 2026
            photo_selectors = [
                "button[aria-label*='foto']", "button[aria-label*='Foto']",
                "button[aria-label*='photo']", "button[aria-label*='Photo']",
                "a[aria-label*='foto']", "a[aria-label*='Foto']",
                ".fontHeadlineSmall", "button[data-field-type='10']"
            ]
            photo_candidates = []
            for sel in photo_selectors:
                photo_candidates += self.driver.find_elements(By.CSS_SELECTOR, sel)
            
            photo_candidates += self.driver.find_elements(By.XPATH, "//*[contains(@aria-label, 'Fotos')]")
            photo_candidates += self.driver.find_elements(By.XPATH, "//*[contains(@aria-label, 'photos')]")
        except Exception:
            photo_candidates = []

        for candidate in photo_candidates:
            try:
                label = candidate.get_attribute('aria-label') or candidate.text
            except StaleElementReferenceException:
                continue
            if not label:
                continue
            # Regex mejorado para capturar números con K, mil o puntos
            match = re.search(r'(\d+[\d\s\.,]*)\s*(?:fotos?|photos?)', label, re.IGNORECASE)
            if match:
                photos_val = self._parse_int(match.group(1))
                if photos_val is not None:
                    confidence['photos'] = True
                    meta_debug['photos_source'] = 'aria-label'
                    break

        if photos_val is None:
            # Fallback regex expandido en todo el snapshot
            patterns = [
                r'(\d+[\d\s\.,]*\s*(?:k|mil)?)\s*(?:fotos?|photos?)',
                r'(?:fotos?|photos?)\s*(?:de\s*)?(\d+[\d\s\.,]*\s*(?:k|mil)?)'
            ]
            for pattern in patterns:
                regex = re.search(pattern, html_snapshot, re.IGNORECASE)
                if regex:
                    photos_val = self._parse_int(regex.group(1))
                    if photos_val is not None:
                        confidence['photos'] = True
                        meta_debug['photos_source'] = 'regex_html'
                        break

        if photos_val is not None:
            profile_data['fotos'] = photos_val
        else:
            # v3.3.2: Fallback de conteo visual (mínimo detectable)
            try:
                gallery_imgs = self.driver.find_elements(By.CSS_SELECTOR, "button[style*='background-image']")
                if len(gallery_imgs) > 0:
                    photos_val = len(gallery_imgs)
                    profile_data['fotos'] = photos_val
                    confidence['photos'] = False # Baja confianza pero dato real
                    meta_debug['photos_source'] = 'visual_count'
            except:
                confidence.setdefault('photos', False)


    def _attempt_photo_modal(self, profile_data: dict) -> None:
        confidence = profile_data.setdefault('meta', {}).setdefault('data_confidence', {})
        debug_meta = profile_data.setdefault('meta', {}).setdefault('scrape_debug', {})

        try:
            photo_trigger = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label^='Fotos'], a[aria-label^='Fotos']"))
            )
        except TimeoutException:
            confidence.setdefault('photos', False)
            debug_meta['photos_modal'] = 'trigger_not_found'
            return
        except Exception as exc:
            confidence.setdefault('photos', False)
            debug_meta['photos_modal'] = f'error_trigger:{exc}'
            return

        try:
            actions = ActionChains(self.driver)
            actions.move_to_element(photo_trigger).pause(0.2).click().perform()
        except Exception:
            try:
                photo_trigger.click()
            except Exception as exc:
                confidence.setdefault('photos', False)
                debug_meta['photos_modal'] = f'error_click:{exc}'
                return

        try:
            WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='dialog']"))
            )
        except TimeoutException:
            confidence.setdefault('photos', False)
            debug_meta['photos_modal'] = 'modal_not_opened'
            return

        modal_html = self._capture_html_snapshot()
        modal_regex = re.search(r'(\d+[\d\s\.,]*\s*(?:k|mil)?)\s*fotos', modal_html, re.IGNORECASE)
        if modal_regex:
            photos_val = self._parse_int(modal_regex.group(1))
            if photos_val is not None:
                profile_data['fotos'] = photos_val
                confidence['photos'] = True
                debug_meta['photos_source'] = 'modal'
                debug_meta['photos_modal'] = 'success'

        try:
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        except Exception:
            try:
                close_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label*='cerrar'], button[aria-label*='Cerrar']")
                close_button.click()
            except Exception:
                pass

    def _scrape_maps_profile(
        self,
        hotel_name: str,
        search_location: str,
        original_location: str,
        geo_validation_result: Optional[ValidationResult],
        geo_validation_enabled: bool,
        profile_context: dict,
        attempt_index: int,
        total_attempts: int
    ) -> dict:
        query_location = search_location or original_location or ''
        search_query = f"{hotel_name} {query_location}".strip()
        maps_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"

        self.driver.get(maps_url)
        self._ensure_main_panel()
        time.sleep(1.5)

        profile_data = self._base_profile()
        profile_data['meta'].update(profile_context)
        profile_data['meta'].update({
            'search_query': search_query,
            'search_url': maps_url,
            'search_location_used': query_location,
            'location_requested': original_location,
            'search_attempt': attempt_index,
            'location_attempts': total_attempts,
        })

        resolved_location = self._build_resolved_location(geo_validation_result, query_location)
        location_source = 'input'
        if geo_validation_result and geo_validation_result.resolved_location:
            resolved_clean = geo_validation_result.resolved_location.strip().lower()
            if resolved_location.lower() == resolved_clean:
                location_source = 'geo_validation'

        if resolved_location:
            profile_data['meta']['resolved_location'] = resolved_location
        profile_data['meta']['location_source'] = location_source

        html_snapshot = self._capture_html_snapshot()
        if html_snapshot:
            profile_data['meta'].setdefault('scrape_debug', {})['html_sample_start'] = html_snapshot[:2000]
            profile_data['meta']['scrape_debug']['html_sample_end'] = html_snapshot[-2000:]

        if geo_validation_result:
            profile_data['meta']['geo_validation'] = {
                'enabled': True,
                'performed': True,
                'is_valid': geo_validation_result.is_valid,
                'distance_km': round(geo_validation_result.distance_km, 2),
                'threshold_km': geo_validation_result.threshold_km,
                'confidence': round(geo_validation_result.confidence, 2),
                'expected_location': {
                    'lat': geo_validation_result.expected_location[0],
                    'lng': geo_validation_result.expected_location[1],
                    'address': geo_validation_result.expected_address,
                    'city': geo_validation_result.expected_city,
                },
                'actual_location': {
                    'lat': geo_validation_result.actual_location[0],
                    'lng': geo_validation_result.actual_location[1],
                    'address': geo_validation_result.actual_address,
                    'city': geo_validation_result.actual_city,
                    'state': geo_validation_result.actual_state,
                    'country': geo_validation_result.actual_country,
                    'place_id': geo_validation_result.actual_place_id,
                },
                'resolved_location': geo_validation_result.resolved_location,
                'api_calls_used': geo_validation_result.api_calls_used,
                'error_message': geo_validation_result.error_message,
                'location_override_applied': location_source == 'geo_validation',
            }

            if not geo_validation_result.is_valid:
                alert = (
                    f"CRÍTICO: Validación geográfica fallida - Hotel está a "
                    f"{geo_validation_result.distance_km:.1f}km de la ubicación esperada "
                    f"(umbral: {geo_validation_result.threshold_km}km)"
                )
                if alert not in profile_data['issues']:
                    profile_data['issues'].append(alert)
                if geo_validation_result.resolved_location and location_source == 'geo_validation':
                    override_msg = (
                        f"Se aplicó ubicación detectada por Google Maps: "
                        f"{geo_validation_result.resolved_location}"
                    )
                    if override_msg not in profile_data['issues']:
                        profile_data['issues'].append(override_msg)
        else:
            profile_data['meta']['geo_validation'] = {
                'enabled': geo_validation_enabled,
                'performed': False,
                'reason': 'API no disponible o validación deshabilitada'
            }

        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1")))
            profile_data['existe'] = True
        except Exception:
            fugas, perdida = self._detectar_fugas(profile_data, hotel_data, region)
            profile_data['fugas_detectadas'] = fugas
            profile_data['perdida_total_mes_COP'] = perdida
            profile_data['perdida_anual_COP'] = perdida * 12
            profile_data['prioridad_accion'] = 'CRÍTICA - RECLAMAR PERFIL HOY'
            profile_data['issues'].append("CRÍTICO: Perfil GBP no existe - Pérdida: 2.1M COP/mes")
            return profile_data

        self._extract_metrics(html_snapshot, profile_data)
        if profile_data['meta'].get('data_confidence', {}).get('photos') is not True:
            self._attempt_photo_modal(profile_data)
            
        # v3.3.2: Triangulación con API de Google (Dato de Verdad)
        if geo_validation_result and geo_validation_result.photo_count is not None:
            api_photos = geo_validation_result.photo_count
            current_photos = profile_data.get('fotos', 0)
            
            # Si la API encontró fotos y el scraper no, o si la API reporta más fotos, confiar en API
            if api_photos > current_photos:
                profile_data['fotos'] = api_photos
                profile_data['meta'].setdefault('data_confidence', {})['photos'] = True
                profile_data['meta'].setdefault('scrape_debug', {})['photos_source'] = 'google_places_api'
                logger.info(f"✓ Conteo de fotos corregido vía API: {api_photos}")

        # Detección robusta de horarios (multinivel)
        try:
            detector = HorariosDetector(self.driver)
            tiene_horarios, confidence, metadata = detector.detect_horarios(timeout=8)
            
            profile_data['horarios'] = tiene_horarios
            profile_data['meta'].setdefault('data_confidence', {})['horarios'] = confidence
            profile_data['meta'].setdefault('horarios_detection', {}).update({
                'method': metadata['detection_method'],
                'confidence': round(confidence, 2),
                'keywords': metadata['matched_keywords'][:3],
                'time_formats': metadata['time_formats_found'][:2],
                'sample': metadata['sample_text'][:100] if metadata['sample_text'] else None,
            })
            
            if tiene_horarios:
                logger.info(
                    f"✓ Horarios detectados (confianza: {confidence:.0%}) "
                    f"via {metadata['detection_method']}"
                )
            else:
                logger.warning("⚠️ No se detectaron horarios en GBP")
                
        except Exception as exc:
            logger.error(f"❌ Error en detección de horarios: {exc}")
            profile_data['horarios'] = False
            profile_data['meta'].setdefault('data_confidence', {})['horarios'] = 0.0
            profile_data['meta']['horarios_detection'] = {
                'method': 'error',
                'error': str(exc),
            }

        try:
            self.driver.find_element(By.CSS_SELECTOR, "a[data-item-id='authority']")
            profile_data['website'] = True
            profile_data['meta'].setdefault('data_confidence', {})['website'] = True
        except Exception:
            profile_data['meta'].setdefault('data_confidence', {}).setdefault('website', False)

        try:
            self.driver.find_element(By.CSS_SELECTOR, "[data-item-id*='phone']")
            profile_data['telefono'] = True
            profile_data['meta'].setdefault('data_confidence', {})['telefono'] = True
        except Exception:
            profile_data['meta'].setdefault('data_confidence', {}).setdefault('telefono', False)

        try:
            whatsapp_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'WhatsApp') or contains(@href, 'wa.me') or contains(@href, 'whatsapp')]")
            if whatsapp_elements:
                profile_data['whatsapp_visible'] = True
                profile_data['meta'].setdefault('data_confidence', {})['whatsapp'] = True
            else:
                profile_data['meta'].setdefault('data_confidence', {}).setdefault('whatsapp', False)
        except Exception:
            profile_data['meta'].setdefault('data_confidence', {}).setdefault('whatsapp', False)

        try:
            posts_section = self.driver.find_elements(By.CSS_SELECTOR, "[aria-label*='Actualizaciones']")
            if posts_section:
                profile_data['posts'] = 1
                profile_data['meta'].setdefault('data_confidence', {})['posts'] = True
            else:
                profile_data['meta'].setdefault('data_confidence', {}).setdefault('posts', False)
        except Exception:
            profile_data['meta'].setdefault('data_confidence', {}).setdefault('posts', False)

        try:
            qa_section = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Preguntas y respuestas')]")
            if qa_section:
                profile_data['tiene_qa'] = True
                profile_data['meta'].setdefault('data_confidence', {})['qa'] = True
            else:
                profile_data['meta'].setdefault('data_confidence', {}).setdefault('qa', False)
        except Exception:
            profile_data['meta'].setdefault('data_confidence', {}).setdefault('qa', False)

        score = 0
        if profile_data['existe']:
            score += 20
        if profile_data['reviews'] >= 10:
            score += 15
        elif profile_data['reviews'] > 0:
            score += 10
        if profile_data['rating'] >= 4.0:
            score += 15
        elif profile_data['rating'] > 0:
            score += 10
        if profile_data['fotos'] >= 15:
            score += 15
        elif profile_data['fotos'] >= 5:
            score += 10
        if profile_data['horarios']:
            score += 10
        if profile_data['website']:
            score += 10
        if profile_data['telefono']:
            score += 5

        profile_data['score'] = score

        # v2.4.2: Calcular y exportar activity score compuesto
        try:
            profile_data['gbp_activity_score'] = self._calcular_activity_score(profile_data)
        except Exception as exc:
            logger.warning("No se pudo calcular gbp_activity_score: %s", exc)
            profile_data['gbp_activity_score'] = 100  # Fallback conservador

        # v2.4.2: Detectar motor de reservas en GBP (existencia + prominencia)
        self._detectar_motor_reservas_gbp(profile_data)

        fugas, perdida_mensual = self._detectar_fugas(profile_data, self.hotel_data, self.region)
        profile_data['fugas_detectadas'] = fugas
        profile_data['perdida_total_mes_COP'] = perdida_mensual
        profile_data['perdida_anual_COP'] = perdida_mensual * 12

        if perdida_mensual >= 1_500_000:
            profile_data['prioridad_accion'] = 'CRÍTICA - ACTUAR EN 72 HORAS'
        elif perdida_mensual >= 1_000_000:
            profile_data['prioridad_accion'] = 'ALTA - ACTUAR EN 7 DÍAS'
        elif perdida_mensual >= 500_000:
            profile_data['prioridad_accion'] = 'MEDIA - ACTUAR EN 30 DÍAS'
        else:
            profile_data['prioridad_accion'] = 'BAJA - OPTIMIZACIÓN CONTINUA'

        if profile_data['reviews'] < 10:
            profile_data['issues'].append(f"Pocas reseñas ({profile_data['reviews']}), meta: 10+")
        if profile_data['fotos'] < 15:
            profile_data['issues'].append(f"Pocas fotos ({profile_data['fotos']}), meta: 15+")
        if profile_data['rating'] < 4.0 and profile_data['rating'] > 0:
            profile_data['issues'].append(f"Rating bajo ({profile_data['rating']}), meta: 4.0+")

        return profile_data

    def _detectar_motor_reservas_gbp(self, profile_data: dict) -> dict:
        """
        Detecta si el perfil GBP tiene un motor de reservas embebido.
        
        v2.4.2: Detecta EXISTENCIA y PROMINENCIA del motor.
        - Prominente: enlace con aria-label "Reservar" o similar (1-clic)
        - No prominente: motor existe pero requiere navegación adicional
        
        Returns:
            {'existe': bool, 'prominente': bool, 'proveedor': str|None}
        """
        patrones_motor = [
            'engine.lobbypms.com', 'cloudbeds.com', 'sirvoy.', 'beds24.',
            'myallocator.', 'siteminder.', 'littlehotelier.', 'booking-engine.',
            '/reservar', '/booking', '/disponibilidad', '/availability'
        ]
        
        resultado = {'existe': False, 'prominente': False, 'proveedor': None}
        
        try:
            # Buscar en enlaces del perfil
            enlaces = self.driver.find_elements(By.CSS_SELECTOR, "a[href]")
            for enlace in enlaces:
                try:
                    href = (enlace.get_attribute('href') or '').lower()
                    for patron in patrones_motor:
                        if patron in href:
                            resultado['existe'] = True
                            # Extraer nombre del proveedor
                            if 'engine.' in patron:
                                resultado['proveedor'] = patron.replace('engine.', '').split('.')[0]
                            else:
                                resultado['proveedor'] = patron.replace('.', '').replace('/', '')
                            
                            # Verificar prominencia: aria-label o texto visible con "reservar"
                            label = enlace.get_attribute('aria-label') or enlace.text or ''
                            keywords_prominencia = ['reservar', 'book', 'reserva', 'reserve', 'disponibilidad']
                            if any(kw in label.lower() for kw in keywords_prominencia):
                                resultado['prominente'] = True
                            break
                except Exception:
                    continue
                    
                if resultado['existe']:
                    break
            
            # Buscar en page_source si no encontrado aún
            if not resultado['existe']:
                html = self.driver.page_source.lower()
                for patron in patrones_motor[:8]:  # Solo patrones de proveedores conocidos
                    if patron in html:
                        resultado['existe'] = True
                        resultado['proveedor'] = patron.split('.')[0].replace('engine', 'lobbypms')
                        # Si está en HTML pero no como enlace destacado, no es prominente
                        resultado['prominente'] = False
                        break
                        
        except Exception as e:
            logger.warning(f"Error detectando motor reservas GBP: {e}")
        
        # Guardar en profile_data
        profile_data['motor_gbp'] = resultado
        profile_data['motor_reservas_gbp'] = resultado['existe']
        profile_data['motor_reservas_proveedor'] = resultado['proveedor']
        profile_data['motor_reservas_prominente'] = resultado['prominente']
        
        if resultado['existe']:
            logger.info(f"✓ Motor reservas GBP detectado: {resultado['proveedor']} (prominente: {resultado['prominente']})")
        
        return resultado

    def _calcular_activity_score(self, profile_data: dict) -> int:
        """Calcula activity score compuesto v2.6.2 (posts + fotos + respuestas).

        Usa pesos del Plan Maestro; si faltan datos o pesos, se devuelve 100 para evitar falsas alarmas.
        
        v2.6.2: Usa fotos_meta (total visible) como proxy ya que no podemos medir ritmo mensual.
        """
        pesos = {}
        try:
            pesos = self.benchmark_loader.get_activity_weights()
        except Exception as exc:
            logger.warning("Pesos de actividad no disponibles: %s", exc)

        if not pesos:
            return 100

        posts_90d_max = pesos.get('posts_90d_max', 5)
        fotos_meta = pesos.get('fotos_meta', 15)  # v2.6.2: Meta total de fotos

        posts_90d = profile_data.get('posts', 0)
        fotos_total = profile_data.get('fotos', 0)
        
        # v2.6.2: Usar fotos_meta como proxy (no podemos medir ritmo mensual real)
        fotos_ratio = min(fotos_total / fotos_meta, 1.0) if fotos_meta > 0 else 0
        
        reviews_response_rate = self._calcular_response_rate(profile_data)

        score = (
            min(posts_90d / posts_90d_max, 1) * pesos.get('posts_90d_peso', 0.35) +
            fotos_ratio * pesos.get('fotos_mes_peso', 0.25) +
            reviews_response_rate * pesos.get('reviews_response_peso', 0.40)
        ) * 100

        return int(score)

    def _calcular_response_rate(self, profile_data: dict) -> float:
        """Estimación simple de tasa de respuesta a reviews (0-1).

        Si no hay datos explícitos, devuelve 0.0 para evitar inflar la actividad.
        """
        meta_reviews = profile_data.get('meta', {}).get('reviews', {})
        responded = meta_reviews.get('responded', 0)
        total = meta_reviews.get('total', profile_data.get('reviews', 0))
        if total <= 0:
            return 0.0
        ratio = responded / total
        return max(0.0, min(ratio, 1.0))

    def _calcular_severidad(self, impacto_cop: int) -> str:
        if impacto_cop >= 800_000:
            return "CRÍTICA"
        if impacto_cop >= 500_000:
            return "ALTA"
        if impacto_cop >= 300_000:
            return "MEDIA"
        return "BAJA"

    def _detectar_fugas(
        self, 
        profile_data: dict,
        hotel_data: Optional[Dict[str, Any]] = None,
        region: str = "default",
    ):
        """Detect financial leaks using dynamic impact calculator.
        
        Args:
            profile_data: GBP profile audit data
            hotel_data: Optional hotel-provided data for custom calculations
            region: Region code for benchmark fallback
        """
        calculator = DynamicImpactCalculator(self.benchmark_loader)
        
        detected_issues = get_detected_issues(profile_data, profile_data.get('schema_data', {}))
        
        impact_report = calculator.calculate_impacts(
            region=region,
            detected_issues=detected_issues,
            hotel_data=hotel_data,
        )
        
        profile_data['_impact_data_sources'] = impact_report.data_sources
        profile_data['_impact_base_metrics'] = impact_report.base_metrics
        
        fugas = []
        for impact in impact_report.impacts:
            severidad = self._calcular_severidad(impact.monthly_loss_cop)
            tipo_map = {
                'PERFIL_NO_RECLAMADO': 'PERFIL_NO_RECLAMADO',
                'FOTOS_INSUFICIENTES': 'FOTOS_INSUFICIENTES',
                'RESENAS_CRITICAS': 'RESENAS_CRITICAS',
                'SIN_WHATSAPP': 'SIN_WHATSAPP_VISIBLE',
                'PERFIL_ABANDONADO': 'PERFIL_ABANDONADO',
                'SIN_FAQ': 'SIN_FAQ_CONVERSACIONAL',
                'RATING_BAJO': 'RATING_DESCALIFICANTE',
                'SIN_HORARIOS': 'SIN_HORARIOS',
                'SIN_WEBSITE': 'SIN_WEBSITE_DIRECTO',
                'CERO_ACTIVIDAD_RECIENTE': 'PERFIL_ABANDONADO',
            }
            
            fugas.append({
                'tipo': tipo_map.get(impact.issue_type, impact.issue_type),
                'severidad': severidad,
                'detalle': impact.description,
                'impacto_estimado_COP_mes': impact.monthly_loss_cop,
                'motivo': self._get_motivo_for_issue(impact.issue_type),
                'urgencia': self._get_urgencia_for_issue(impact.issue_type, severidad),
            })
        
        return fugas, impact_report.total_monthly_loss_cop

    def _get_motivo_for_issue(self, issue_type: str) -> str:
        """Get the 'motivo' text for an issue type."""
        motivos = {
            'PERFIL_NO_RECLAMADO': 'El 65% de turistas busca "hoteles cerca de mí"; sin perfil no existes.',
            'FOTOS_INSUFICIENTES': 'Google Maps prioriza perfiles visuales ricos. Pareces abandonado.',
            'RESENAS_CRITICAS': 'Google no recomienda hoteles con <10 reseñas en resultados conversacionales.',
            'SIN_WHATSAPP': '68% de reservas directas en Colombia inician en WhatsApp.',
            'PERFIL_ABANDONADO': 'Google interpreta falta de actividad como cierre temporal.',
            'SIN_FAQ': '40% de búsquedas turísticas son preguntas directas.',
            'RATING_BAJO': 'El 92% de usuarios solo considera hoteles 4.0+. Entregas clientes gratis a competidores.',
            'SIN_HORARIOS': 'Sin check-in visible pareces informal.',
            'SIN_WEBSITE': 'Cada reserva paga 18-25% de comisión.',
            'CERO_ACTIVIDAD_RECIENTE': 'Google interpreta falta de actividad como cierre temporal.',
        }
        return motivos.get(issue_type, 'Impacto en visibilidad y conversión.')

    def _get_urgencia_for_issue(self, issue_type: str, severidad: str) -> str:
        """Get the 'urgencia' text for an issue type."""
        if severidad == 'CRÍTICA':
            return 'CRÍTICA - Atiende este tema hoy'
        elif severidad == 'ALTA':
            return 'ALTA - Solucionable en 24-72 horas'
        elif severidad == 'MEDIA':
            return 'MEDIA - Solucionable en una semana'
        return 'BAJA - Mejora opcional'

    def validate_location_only(
        self,
        hotel_name: str,
        location: str,
        *,
        expected_city: Optional[str] = None,
        threshold_km: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Perform lightweight geographic validation without launching Selenium."""

        response: Dict[str, Any] = {
            "status": "skipped",
            "resolved_location": None,
            "location_source": None,
        }

        geo_validator = get_geo_validator()
        if not geo_validator.is_available():
            response["reason"] = "geo_validator_unavailable"
            return response

        expected_city = (expected_city or (location.split(',')[0] if location else "")).strip()
        threshold_value = threshold_km or float(os.getenv('GBP_VALIDATION_THRESHOLD_KM', '30'))

        try:
            validation = geo_validator.validate_hotel_location(
                hotel_name=hotel_name,
                expected_city=expected_city,
                expected_address=location or None,
                custom_threshold_km=threshold_value,
            )
        except Exception as exc:
            response.update({"status": "error", "reason": str(exc)})
            return response

        resolved_location = validation.resolved_location or location or expected_city
        comparison_source = (location or "").strip().lower()
        location_source = "gbp_validation"
        if not resolved_location:
            location_source = "input"
        elif comparison_source and resolved_location.strip().lower() == comparison_source:
            location_source = "input"

        response.update(
            {
                "status": "ok",
                "resolved_location": resolved_location,
                "distance_km": validation.distance_km,
                "confidence": validation.confidence,
                "is_valid": validation.is_valid,
                "location_source": location_source,
                "meta": {
                    "expected_city": validation.expected_city,
                    "threshold_km": validation.threshold_km,
                    "api_calls_used": validation.api_calls_used,
                    "error_message": validation.error_message,
                },
            }
        )

        return response

    def check_google_profile(
        self, 
        hotel_name: str, 
        location: str,
        hotel_data: Optional[Dict[str, Any]] = None,
        region: str = "default",
    ) -> dict:
        self.hotel_data = hotel_data or {}
        self.region = region
        profile_context = {
            'hotel_name': hotel_name,
            'location': location,
        }

        # Step 1: Geographic validation (if enabled)
        geo_validation_result = None
        geo_validation_enabled = os.getenv('GBP_GEOGRAPHIC_VALIDATION_ENABLED', 'true').lower() == 'true'
        
        if geo_validation_enabled:
            try:
                logger.info(f"Performing geographic validation for '{hotel_name}' in '{location}'")
                geo_validator = get_geo_validator()
                
                if geo_validator.is_available():
                    # Extract city from location (assume format "City, Country" or just "City")
                    expected_city = location.split(',')[0].strip()
                    
                    geo_validation_result = geo_validator.validate_hotel_location(
                        hotel_name=hotel_name,
                        expected_city=expected_city,
                        expected_address=None,  # Could be enhanced to accept specific address
                        custom_threshold_km=float(os.getenv('GBP_VALIDATION_THRESHOLD_KM', '30'))
                    )
                    
                    logger.info(
                        f"Geographic validation result: "
                        f"Valid={geo_validation_result.is_valid}, "
                        f"Distance={geo_validation_result.distance_km:.2f}km, "
                        f"Confidence={geo_validation_result.confidence:.2f}"
                    )
                    
                    # If validation fails, add critical issue
                    if not geo_validation_result.is_valid:
                        logger.warning(
                            f"GEOGRAPHIC VALIDATION FAILED: "
                            f"Hotel '{hotel_name}' is {geo_validation_result.distance_km:.2f}km "
                            f"from expected location '{expected_city}' "
                            f"(threshold: {geo_validation_result.threshold_km}km)"
                        )
                else:
                    logger.warning("Geographic validation requested but API key not available")
                    
            except Exception as e:
                logger.error(f"Error during geographic validation: {e}")
                # Continue without geographic validation if it fails

        search_locations = self._prepare_search_locations(location, geo_validation_result)
        resolved_location = self._build_resolved_location(geo_validation_result, search_locations[0])
        override_applied = (
            geo_validation_result
            and geo_validation_result.resolved_location
            and geo_validation_result.resolved_location.strip().lower() != (location or '').strip().lower()
        )

        if not self._init_driver():
            fallback_profile = self._fallback_profile(hotel_name, location)
            fallback_profile['meta'].update(profile_context)
            fallback_profile['meta'].update({
                'resolved_location': resolved_location,
                'location_source': 'geo_validation' if override_applied else 'input',
                'search_location_used': search_locations[0] if search_locations else location,
            })
            if geo_validation_result:
                fallback_profile['meta']['geo_validation'] = {
                    'enabled': True,
                    'performed': True,
                    'is_valid': geo_validation_result.is_valid,
                    'distance_km': round(geo_validation_result.distance_km, 2),
                    'threshold_km': geo_validation_result.threshold_km,
                    'confidence': round(geo_validation_result.confidence, 2),
                    'expected_location': {
                        'lat': geo_validation_result.expected_location[0],
                        'lng': geo_validation_result.expected_location[1],
                        'address': geo_validation_result.expected_address,
                        'city': geo_validation_result.expected_city,
                    },
                    'actual_location': {
                        'lat': geo_validation_result.actual_location[0],
                        'lng': geo_validation_result.actual_location[1],
                        'address': geo_validation_result.actual_address,
                        'city': geo_validation_result.actual_city,
                        'state': geo_validation_result.actual_state,
                        'country': geo_validation_result.actual_country,
                        'place_id': geo_validation_result.actual_place_id,
                    },
                    'resolved_location': geo_validation_result.resolved_location,
                    'api_calls_used': geo_validation_result.api_calls_used,
                    'error_message': geo_validation_result.error_message,
                    'location_override_applied': override_applied,
                }
            else:
                fallback_profile['meta']['geo_validation'] = {
                    'enabled': geo_validation_enabled,
                    'performed': False,
                    'reason': 'API no disponible o validación deshabilitada'
                }
            self._record_session_meta(fallback_profile)
            return fallback_profile

        profile_data = None
        scrape_error: Optional[Exception] = None

        try:
            total_attempts = len(search_locations)
            for idx, candidate_location in enumerate(search_locations, start=1):
                try:
                    profile_data = self._scrape_maps_profile(
                        hotel_name,
                        candidate_location,
                        location,
                        geo_validation_result,
                        geo_validation_enabled,
                        profile_context,
                        idx,
                        total_attempts,
                    )
                except Exception as e:
                    logger.error(f"Error in _scrape_maps_profile attempt {idx}: {e}")
                    profile_data = self._base_profile()
                    profile_data['issues'].append(f'Error en intento de scraping {idx}: {e}')
                    # Preserve geo_validation data if available
                    if geo_validation_result is not None:
                        try:
                            profile_data['meta']['geo_validation'] = {
                                'enabled': True,
                                'performed': True,
                                'is_valid': bool(geo_validation_result.is_valid),
                                'distance_km': round(float(geo_validation_result.distance_km), 2),
                                'threshold_km': round(float(geo_validation_result.threshold_km), 2),
                                'confidence': round(float(geo_validation_result.confidence), 2),
                                'expected_location': {
                                    'lat': float(geo_validation_result.expected_location[0]),
                                    'lng': float(geo_validation_result.expected_location[1]),
                                    'address': str(geo_validation_result.expected_address or ''),
                                    'city': str(geo_validation_result.expected_city or ''),
                                },
                                'actual_location': {
                                    'lat': float(geo_validation_result.actual_location[0]),
                                    'lng': float(geo_validation_result.actual_location[1]),
                                    'address': str(geo_validation_result.actual_address or ''),
                                    'city': str(geo_validation_result.actual_city or ''),
                                    'state': str(geo_validation_result.actual_state or ''),
                                    'country': str(geo_validation_result.actual_country or ''),
                                    'place_id': str(geo_validation_result.actual_place_id or ''),
                                },
                                'resolved_location': str(geo_validation_result.resolved_location or ''),
                                'api_calls_used': int(geo_validation_result.api_calls_used),
                                'error_message': str(geo_validation_result.error_message or ''),
                                'location_override_applied': bool(override_applied),
                            }
                        except Exception as e2:
                            logger.error(f"Error building geo_validation dict: {e2}")
                            profile_data['meta']['geo_validation'] = {
                                'enabled': geo_validation_enabled,
                                'performed': False,
                                'reason': 'Error al procesar datos de validación geográfica'
                            }
                    else:
                        profile_data['meta']['geo_validation'] = {
                            'enabled': geo_validation_enabled,
                            'performed': False,
                            'reason': 'API no disponible o validación deshabilitada'
                        }
                    # Continue to next attempt
                if profile_data.get('existe'):
                    break
        except Exception as exc:
            logger.error("Error en GBP auditoria: %s", exc)
            scrape_error = exc
            profile_data = self._base_profile()
            profile_data['issues'].append(f"Error al auditar GBP: {exc}")
            profile_data['prioridad_accion'] = 'ERROR - REINTENTAR'
            profile_data['meta'].update(profile_context)
            # Preserve geo_validation data if available
            if geo_validation_result is not None:
                try:
                    profile_data['meta']['geo_validation'] = {
                        'enabled': True,
                        'performed': True,
                        'is_valid': bool(geo_validation_result.is_valid),
                        'distance_km': round(float(geo_validation_result.distance_km), 2),
                        'threshold_km': round(float(geo_validation_result.threshold_km), 2),
                        'confidence': round(float(geo_validation_result.confidence), 2),
                        'expected_location': {
                            'lat': float(geo_validation_result.expected_location[0]),
                            'lng': float(geo_validation_result.expected_location[1]),
                            'address': str(geo_validation_result.expected_address or ''),
                            'city': str(geo_validation_result.expected_city or ''),
                        },
                        'actual_location': {
                            'lat': float(geo_validation_result.actual_location[0]),
                            'lng': float(geo_validation_result.actual_location[1]),
                            'address': str(geo_validation_result.actual_address or ''),
                            'city': str(geo_validation_result.actual_city or ''),
                            'state': str(geo_validation_result.actual_state or ''),
                            'country': str(geo_validation_result.actual_country or ''),
                            'place_id': str(geo_validation_result.actual_place_id or ''),
                        },
                        'resolved_location': str(geo_validation_result.resolved_location or ''),
                        'api_calls_used': int(geo_validation_result.api_calls_used),
                        'error_message': str(geo_validation_result.error_message or ''),
                        'location_override_applied': bool(override_applied),
                    }
                except Exception as e:
                    logger.error(f"Error building geo_validation dict: {e}")
                    profile_data['meta']['geo_validation'] = {
                        'enabled': geo_validation_enabled,
                        'performed': False,
                        'reason': 'Error al procesar datos de validación geográfica'
                    }
            else:
                profile_data['meta']['geo_validation'] = {
                    'enabled': geo_validation_enabled,
                    'performed': False,
                    'reason': 'API no disponible o validación deshabilitada'
                }
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None

        if profile_data is None:
            profile_data = self._base_profile()
            profile_data['issues'].append('GBP audit no generó resultados tras múltiples búsquedas')
            profile_data['meta'].update(profile_context)

        self._record_session_meta(profile_data)

        if scrape_error:
            return profile_data

        cache_key = self._build_cache_key(hotel_name, location)
        self._save_cache(cache_key, profile_data)

        resolved_meta_location = (profile_data.get('meta') or {}).get('resolved_location')
        if resolved_meta_location and resolved_meta_location.strip().lower() != (location or '').strip().lower():
            resolved_key = self._build_cache_key(hotel_name, resolved_meta_location)
            self._save_cache(resolved_key, profile_data)
        return profile_data

    def audit_competitor_profile(self, hotel_name: str, location: str) -> Dict:
        """
        Auditoría simplificada de perfil GBP para competidores.
        
        Retorna los 7 factores del GEO Score para comparación justa:
        - existe, reviews, rating, fotos, horarios, website, telefono
        
        Usa cache con TTL de 14 días para evitar re-scraping.
        
        Args:
            hotel_name: Nombre del hotel competidor
            location: Ubicación (ciudad, región)
            
        Returns:
            Dict con score y factores, o None si falla
        """
        # Sanitize inputs
        if isinstance(hotel_name, dict):
            hotel_name = hotel_name.get('text', str(hotel_name))
        hotel_name = str(hotel_name).strip() if hotel_name else ''
        location = str(location).strip() if location else ''
        
        if not hotel_name:
            logger.warning("audit_competitor_profile: hotel_name vacío")
            return None
            
        cache_key = self._build_cache_key(hotel_name, location)
        cached = self._get_cached_profile(hotel_name, location)
        
        # Si hay cache válido, retornar datos esenciales
        if cached and cached.get('existe'):
            return {
                'nombre': hotel_name,
                'geo_score': cached.get('score', 0),
                'reviews': cached.get('reviews', 0),
                'rating': cached.get('rating', 0.0),
                'fotos': cached.get('fotos', 0),
                'horarios': cached.get('horarios', False),
                'website': cached.get('website', False),
                'telefono': cached.get('telefono', False),
                'source': 'cache',
                'cache_age_days': cached.get('meta', {}).get('cache_age_days')
            }
        
        # Ejecutar auditoría completa
        try:
            profile_data = self.check_google_profile(hotel_name, location)
            
            if profile_data and profile_data.get('existe'):
                return {
                    'nombre': hotel_name,
                    'geo_score': profile_data.get('score', 0),
                    'reviews': profile_data.get('reviews', 0),
                    'rating': profile_data.get('rating', 0.0),
                    'fotos': profile_data.get('fotos', 0),
                    'horarios': profile_data.get('horarios', False),
                    'website': profile_data.get('website', False),
                    'telefono': profile_data.get('telefono', False),
                    'source': 'live_audit'
                }
        except Exception as e:
            logger.warning(f"Error auditando competidor {hotel_name}: {e}")
        
        return None

    def generar_reporte_ejecutivo(self, profile_data: dict, hotel_name: str) -> str:
        reporte = f"""
╔═══════════════════════════════════════════════════════════════════════╗
║     DIAGNÓSTICO DE FUGAS DE RESERVAS - {hotel_name.upper()}
╚═══════════════════════════════════════════════════════════════════════╝

📊 RESUMEN EJECUTIVO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pérdida mensual estimada:  ${profile_data['perdida_total_mes_COP']:,} COP
Pérdida anual proyectada:  ${profile_data['perdida_anual_COP']:,} COP
Prioridad de acción:       {profile_data['prioridad_accion']}
Score actual GBP:          {profile_data['score']}/100

🚨 FUGAS DETECTADAS ({len(profile_data['fugas_detectadas'])})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        for i, fuga in enumerate(profile_data['fugas_detectadas'], 1):
            reporte += f"""
[{i}] {fuga['tipo']} - SEVERIDAD: {fuga['severidad']}
    └─ Impacto: ${fuga['impacto_estimado_COP_mes']:,} COP/mes
    └─ {fuga['detalle']}
    └─ Por qué pierdes dinero: {fuga['motivo']}
    └─ Urgencia: {fuga['urgencia']}
"""

        reporte += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 DATOS DEL PERFIL ACTUAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Perfil reclamado:     {'SÍ' if profile_data['existe'] else 'NO (CRÍTICO)'}
✓ Rating:               {profile_data['rating']}/5.0
✓ Reseñas:              {profile_data['reviews']}
✓ Fotos:                {profile_data['fotos']}
✓ Website visible:      {'SÍ' if profile_data['website'] else 'NO'}
✓ WhatsApp visible:     {'SÍ' if profile_data['whatsapp_visible'] else 'NO'}
✓ Horarios config.:     {'SÍ' if profile_data['horarios'] else 'NO'}
✓ Teléfono visible:     {'SÍ' if profile_data['telefono'] else 'NO'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 LO QUE ESTO SIGNIFICA EN ESPAÑOL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Hoy estás regalando ${profile_data['perdida_total_mes_COP']:,} COP cada mes
a Booking, Expedia y a tu competencia directa.

Cada búsqueda "hoteles cerca de mí" que no te encuentra es una reserva
que va a parar al hotel de al lado.

Este no es un problema técnico. Es un problema de CAJA.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 PRÓXIMO PASO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Solicita tu Plan 2-Pilares (GBP + JSON) y en 30 días recupera
al menos el 40% de esta fuga.

Inversión: $1.8M COP/mes | ROI esperado: 3X en 90 días

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return reporte

    def get_competitor_score(self, competitor: dict, use_api: bool = False) -> dict:
        """
        Obtiene score de competidor con fuente documentada.
        
        Returns:
            dict con 'score', 'score_source', 'confidence', 'metodologia'
        """
        if use_api and competitor.get('place_id'):
            try:
                real_data = self._places_api_lookup(competitor['place_id'])
                return {
                    "score": self._calculate_gbp_score(real_data),
                    "score_source": "api",
                    "confidence": "alta",
                    "metodologia": "Google Places API - datos reales"
                }
            except Exception:
                pass
        
        reviews = competitor.get('reviews', 0)
        rating = competitor.get('rating', 4.0)
        estimated = min(100, int((reviews / 10) * rating * 2))
        
        return {
            "score": estimated,
            "score_source": "estimation",
            "confidence": "baja",
            "metodologia": "reviews x rating x factor_distancia (heuristica local)"
        }

    def calculate_gbp_activity_score_detailed(self, gbp_data: dict, competitors: list = None) -> dict:
        """
        Activity Score GBP con componentes documentados y benchmark competitivo.
        
        Metodologia v3.5.1:
        - posts_90d: peso 35%, meta 5 posts
        - fotos: peso 25%, meta 15 fotos
        - reviews_response: peso 40%
        """
        posts_90d = gbp_data.get('posts_90d', gbp_data.get('posts', 0))
        fotos = gbp_data.get('fotos', 0)
        reviews_response_rate = gbp_data.get('reviews_response_rate', 0)
        
        PESO_POSTS = 0.35
        PESO_FOTOS = 0.25
        PESO_REVIEWS = 0.40
        
        posts_score = min(posts_90d / 5, 1.0) * 100
        fotos_score = min(fotos / 15, 1.0) * 100
        reviews_score = reviews_response_rate * 100
        
        activity_score = (posts_score * PESO_POSTS + 
                          fotos_score * PESO_FOTOS + 
                          reviews_score * PESO_REVIEWS)
        
        result = {
            "activity_score": round(activity_score, 1),
            "componentes": {
                "posts_90d": {
                    "valor": posts_90d,
                    "meta": 5,
                    "score": round(posts_score, 1),
                    "peso": PESO_POSTS
                },
                "fotos": {
                    "valor": fotos,
                    "meta": 15,
                    "score": round(fotos_score, 1),
                    "peso": PESO_FOTOS
                },
                "reviews_response": {
                    "valor": f"{reviews_response_rate*100:.0f}%",
                    "score": round(reviews_score, 1),
                    "peso": PESO_REVIEWS
                }
            },
            "metodologia": "v3.5.1 - Pesos documentados: posts 35%, fotos 25%, reviews 40%"
        }
        
        if competitors:
            scores = [c.get('activity_score', 50) for c in competitors if c.get('activity_score')]
            if scores:
                result["benchmark_competitivo"] = {
                    "promedio_competidores": round(sum(scores) / len(scores), 1),
                    "total_competidores_analizados": len(scores),
                    "percentil_hotel": f"P{int(sum(1 for s in scores if s < activity_score) / len(scores) * 100)}"
                }
        
        return result

    def _places_api_lookup(self, place_id: str) -> dict:
        """Placeholder for Places API lookup - to be implemented with actual API integration."""
        raise NotImplementedError("Places API integration pending")

    def _calculate_gbp_score(self, data: dict) -> int:
        """Calculate GBP score from raw API data."""
        score = 0
        if data.get('existe'):
            score += 20
        if data.get('reviews', 0) >= 10:
            score += 15
        elif data.get('reviews', 0) > 0:
            score += 10
        if data.get('rating', 0) >= 4.0:
            score += 15
        elif data.get('rating', 0) > 0:
            score += 10
        if data.get('fotos', 0) >= 15:
            score += 15
        elif data.get('fotos', 0) >= 5:
            score += 10
        if data.get('horarios'):
            score += 10
        if data.get('website'):
            score += 10
        if data.get('telefono'):
            score += 5
        return score


if __name__ == "__main__":
    auditor = GBPAuditor(headless=False)
    resultado = auditor.check_google_profile(
        hotel_name="Hotel Boutique Ejemplo",
        location="Salento, Quindío",
    )
    print(auditor.generar_reporte_ejecutivo(resultado, "Hotel Boutique Ejemplo"))
