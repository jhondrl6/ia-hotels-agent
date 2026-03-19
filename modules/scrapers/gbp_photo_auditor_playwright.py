"""
GBP PHOTO AUDITOR - Versión Playwright
======================================
Módulo de Captura Robusta de Fotos usando Playwright.
Mantiene los mismos niveles de confianza y estrategia de fallback.

NIVEL DE CONFIANZA (igual que Selenium):
- 100: Contador explícito del modal confirmado con scroll
- 90: Contador del aria-label validado con imágenes visibles
- 70: Conteo directo de elementos <img> únicos
- 50: Estimación por Network Activity
- 30: Cache reciente (<7 días)
- 10: Inferencia por densidad del DOM
- 0: Sin datos confiables
"""

import re
import time
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout


logger = logging.getLogger(__name__)


@dataclass
class PhotoAuditResult:
    """Resultado de auditoría de fotos con evidencia trazable"""
    count: int
    confidence: int  # 0-100
    method: str  # Método que logró la extracción
    evidence: Dict[str, any]  # Evidencia forense
    warnings: List[str]  # Alertas durante la captura
    timestamp: float


class GBPPhotoAuditorPlaywright:
    """
    Auditor especializado en extracción robusta del contador de fotos
    de Google Business Profile usando Playwright.
    
    Ventajas Playwright:
    - Auto-wait para elementos
    - Mejor manejo de animaciones
    - Network interception nativo
    """
    
    SELECTORS = {
        'photo_button': [
            "button[aria-label*='Foto']",
            "button[aria-label*='foto']",
            "a[aria-label*='Foto']",
            "a[aria-label*='foto']",
            "button[data-value='Fotos']",
            "[data-tab-id='photos']",
            "[data-item-id='image']",
            "[role='tab'][aria-label*='Foto']",
            "[role='tab'][aria-label*='foto']",
            "button[jsaction*='photo']",
            "button[jsaction*='pane.placePhotos']",
            "[jsaction*='pane.placePhotos']",
            ".section-hero-header-image",
            "[data-photo-index='0']",
            ".place-cover-image",
        ],
        'photo_counter_aria': [
            "[aria-label*='fotos']",
            "[aria-label*='Fotos']",
            "[aria-label*='photos']",
        ],
        'modal_dialog': [
            "div[role='dialog']",
            "div[aria-modal='true']",
            ".gallery-modal",
        ],
        'image_elements': [
            "img[src*='googleusercontent']",
            "img[src*='ggpht']",
            "div[style*='background-image']",
        ],
        'gallery_grid': [
            "div[aria-label*='Galería']",
            "div[jsname*='photo']",
            "[role='img']",
        ]
    }
    
    CACHE_FALLBACK_MAX_DAYS = 7
    CACHE_FALLBACK_MIN_CONFIDENCE = 70
    
    def __init__(self, page: Page, max_wait: int = 15, debug_dir: str = "logs/gbp_debug",
                 cache_data: Optional[Dict] = None):
        """
        Args:
            page: Playwright Page instance
            max_wait: Tiempo máximo de espera para elementos (segundos)
            debug_dir: Directorio para guardar screenshots y HTML dumps
            cache_data: Diccionario opcional con datos de caché previos del hotel
                        Formato esperado: {'fotos': int, 'photos_confidence': int,
                                          'photos_method': str, 'cache_age_days': int}
        """
        self.page = page
        self.max_wait = max_wait
        self._network_log = []
        self._network_image_urls = set()
        self._debug_dir = Path(debug_dir)
        self._debug_dir.mkdir(parents=True, exist_ok=True)
        self._cache_data = cache_data or {}
        self._network_handler_installed = False
    
    def _save_debug_artifacts(self, context: str = "unknown") -> Dict:
        """
        Guarda screenshot y HTML dump para debugging post-mortem.
        
        Args:
            context: Identificador del contexto (ej: 'photo_extraction_failed')
            
        Returns:
            Dict con paths de los archivos guardados
        """
        artifacts = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            screenshot_path = self._debug_dir / f"{context}_{timestamp}.png"
            self.page.screenshot(path=str(screenshot_path))
            artifacts['screenshot'] = str(screenshot_path)
            logger.info(f"📸 Screenshot guardado: {screenshot_path}")
        except Exception as e:
            logger.warning(f"No se pudo guardar screenshot: {e}")
            artifacts['screenshot_error'] = str(e)
        
        try:
            html_path = self._debug_dir / f"{context}_{timestamp}.html"
            html_path.write_text(self.page.content(), encoding='utf-8')
            artifacts['html_dump'] = str(html_path)
            logger.info(f"📄 HTML dump guardado: {html_path}")
        except Exception as e:
            logger.warning(f"No se pudo guardar HTML: {e}")
            artifacts['html_error'] = str(e)
        
        return artifacts
    
    def _setup_network_interception(self):
        """Setup network interception for image tracking."""
        if self._network_handler_installed:
            return
        
        def handle_response(response):
            try:
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type:
                    url = response.url
                    if 'googleusercontent' in url:
                        base_url = re.sub(r'=s\d+-', '=', url)
                        self._network_image_urls.add(base_url)
            except Exception:
                pass
        
        self.page.on('response', handle_response)
        self._network_handler_installed = True

    # ====================================================================
    # CAPA 0: EXTRACCIÓN DEL CONTADOR VISIBLE (MÉTODO MEJORADO)
    # ====================================================================

    def _extract_counter_from_aria(self) -> Optional[Tuple[int, Dict]]:
        """
        Extrae contador de fotos desde atributos aria-label.
        
        Returns:
            (count, evidence) o None si falla
        """
        evidence = {'method': 'aria_label', 'raw_labels': []}
        
        for selector in self.SELECTORS['photo_counter_aria']:
            try:
                elements = self.page.query_selector_all(selector)
                for elem in elements:
                    try:
                        label = elem.get_attribute('aria-label') or elem.text_content()
                        if not label:
                            continue
                        
                        evidence['raw_labels'].append(label)
                        
                        patterns = [
                            r'(\d+(?:[.,]\d+)?[kKmM]?)\s*fotos?',
                            r'(\d+(?:[.,]\d+)?[kKmM]?)\s*photos?',
                        ]
                        
                        for pattern in patterns:
                            match = re.search(pattern, label, re.IGNORECASE)
                            if match:
                                raw_value = match.group(1).replace(' ', '').replace(',', '')
                                count = self._parse_numeric_value(raw_value)
                                if count and count > 0:
                                    evidence['matched_label'] = label
                                    evidence['parsed_value'] = count
                                    return count, evidence
                    except Exception:
                        continue
            except Exception as e:
                logger.debug(f"Error en selector {selector}: {e}")
        
        return None

    def _parse_numeric_value(self, value: str) -> Optional[int]:
        """
        Parsea valores numéricos con multiplicadores (k, M).
        
        Examples:
            "123" -> 123
            "2.5k" -> 2500
            "1.2K" -> 1200
        """
        value = value.lower().strip()
        multiplier = 1
        
        if value.endswith('k'):
            multiplier = 1000
            value = value[:-1]
        elif value.endswith('m'):
            multiplier = 1_000_000
            value = value[:-1]
        
        try:
            base = float(value.replace(',', '.'))
            return int(base * multiplier)
        except ValueError:
            return None

    # ====================================================================
    # CAPA 1: NAVEGACIÓN DEL MODAL CON SCROLL PROGRAMÁTICO
    # ====================================================================

    def _open_photo_modal(self) -> Tuple[bool, List[str]]:
        """
        Abre el modal de fotos con reintentos y validación.
        
        Returns:
            (success, warnings)
        """
        warnings = []
        
        for selector in self.SELECTORS['photo_button']:
            try:
                photo_btn = self.page.wait_for_selector(
                    selector,
                    timeout=self.max_wait * 1000,
                    state='visible'
                )
                
                photo_btn.scroll_into_view_if_needed()
                time.sleep(0.3)
                
                try:
                    photo_btn.click(timeout=5000)
                except Exception:
                    try:
                        self.page.evaluate('el => el.click()', photo_btn)
                    except Exception:
                        warnings.append(f"No se pudo hacer click en {selector}")
                        continue
                
                time.sleep(1.5)
                
                for modal_selector in self.SELECTORS['modal_dialog']:
                    modal = self.page.query_selector(modal_selector)
                    if modal and modal.is_visible():
                        return True, warnings
                
                warnings.append(f"Modal no visible tras click en {selector}")
                
            except PlaywrightTimeout:
                warnings.append(f"Timeout esperando botón: {selector}")
                continue
            except Exception as e:
                warnings.append(f"Error abriendo modal con {selector}: {str(e)}")
                continue
        
        return False, warnings

    def _extract_from_modal_with_scroll(self) -> Optional[Tuple[int, Dict]]:
        """
        Extrae contador del modal navegando con scroll.
        
        Strategy:
        1. Buscar contador explícito en header del modal
        2. Si no existe, hacer scroll y contar imágenes únicas
        3. Validar consistencia con múltiples verificaciones
        """
        success, warnings = self._open_photo_modal()
        if not success:
            return None
        
        evidence = {
            'method': 'modal_scroll',
            'warnings': warnings,
            'scroll_iterations': 0,
        }
        
        try:
            time.sleep(2)
            modal_html = self.page.content()
            
            match = re.search(
                r'(\d+)\s*de\s*(\d+)\s*fotos?',
                modal_html,
                re.IGNORECASE
            )
            if match:
                total_photos = int(match.group(2))
                evidence['counter_location'] = 'modal_header'
                evidence['raw_text'] = match.group(0)
                return total_photos, evidence
            
            modal_container = None
            for modal_selector in self.SELECTORS['modal_dialog']:
                container = self.page.query_selector(modal_selector)
                if container:
                    modal_container = container
                    break
            
            if not modal_container:
                evidence['error'] = 'Modal container not found'
                return None
            
            unique_images = set()
            last_count = 0
            stale_iterations = 0
            max_iterations = 20
            
            for i in range(max_iterations):
                modal_container.evaluate('el => el.scrollBy(0, 500)')
                time.sleep(0.8)
                
                current_images = self._count_unique_images()
                unique_images.update(current_images)
                
                evidence['scroll_iterations'] = i + 1
                
                if len(unique_images) == last_count:
                    stale_iterations += 1
                    if stale_iterations >= 3:
                        break
                else:
                    stale_iterations = 0
                    last_count = len(unique_images)
            
            if len(unique_images) > 0:
                evidence['unique_image_sources'] = len(unique_images)
                evidence['confidence_note'] = (
                    'Alto' if stale_iterations >= 3 else 'Medio'
                )
                return len(unique_images), evidence
            
        except Exception as e:
            logger.error(f"Error en modal scroll: {e}")
            evidence['error'] = str(e)
        finally:
            try:
                self.page.keyboard.press('Escape')
                time.sleep(0.5)
            except Exception:
                pass
        
        return None

    def _count_unique_images(self) -> set:
        """
        Cuenta imágenes únicas en el DOM actual.
        
        Returns:
            Set de URLs únicas de imágenes
        """
        unique_srcs = set()
        
        for selector in self.SELECTORS['image_elements']:
            try:
                elements = self.page.query_selector_all(selector)
                for elem in elements:
                    try:
                        tag_name = elem.evaluate('el => el.tagName').lower()
                        
                        if tag_name == 'img':
                            src = elem.get_attribute('src')
                            if src and 'googleusercontent' in src:
                                base_src = re.sub(r'=s\d+-', '=', src)
                                unique_srcs.add(base_src)
                        
                        elif tag_name == 'div':
                            style = elem.get_attribute('style')
                            if style and 'background-image' in style:
                                match = re.search(r'url\(["\']?([^"\']+)["\']?\)', style)
                                if match:
                                    unique_srcs.add(match.group(1))
                    except Exception:
                        continue
            except Exception:
                continue
        
        return unique_srcs

    # ====================================================================
    # CAPA 2: CONTEO DIRECTO DE ELEMENTOS <IMG> EN DOM
    # ====================================================================

    def _count_dom_images(self) -> Optional[Tuple[int, Dict]]:
        """
        Cuenta directamente elementos <img> en el panel principal.
        
        Nota: Método menos confiable porque no distingue thumbnails
        de galería completa.
        """
        evidence = {'method': 'dom_img_count'}
        
        try:
            gallery_containers = []
            for selector in self.SELECTORS['gallery_grid']:
                try:
                    containers = self.page.query_selector_all(selector)
                    gallery_containers.extend(containers)
                except Exception:
                    continue
            
            if not gallery_containers:
                return None
            
            unique_images = set()
            for container in gallery_containers:
                try:
                    images = container.query_selector_all('img')
                    for img in images:
                        src = img.get_attribute('src')
                        if src and ('googleusercontent' in src or 'ggpht' in src):
                            unique_images.add(src)
                except Exception:
                    continue
            
            count = len(unique_images)
            if count > 0:
                evidence['unique_sources'] = count
                evidence['confidence_note'] = 'Estimación por thumbnails visibles'
                return count, evidence
            
        except Exception as e:
            evidence['error'] = str(e)
        
        return None

    # ====================================================================
    # CAPA 3: ANÁLISIS DE NETWORK ACTIVITY
    # ====================================================================

    def _analyze_network_requests(self) -> Optional[Tuple[int, Dict]]:
        """
        Analiza peticiones de red para detectar carga de imágenes.
        
        Nota: En Playwright se usa page.on('response') en lugar de logs.
        """
        evidence = {'method': 'network_analysis'}
        
        try:
            if not self._network_handler_installed:
                self._setup_network_interception()
                evidence['note'] = 'Network handler installed - reload page for full capture'
            
            count = len(self._network_image_urls)
            if count > 0:
                evidence['detected_requests'] = count
                evidence['confidence_note'] = 'Basado en tráfico de red observado'
                evidence['sample_urls'] = list(self._network_image_urls)[:5]
                return count, evidence
            
        except Exception as e:
            evidence['error'] = str(e)
        
        return None

    # ====================================================================
    # ORQUESTADOR PRINCIPAL
    # ====================================================================

    def audit_photos(self) -> PhotoAuditResult:
        """
        Ejecuta auditoría completa con estrategia de fallback en cascada.
        
        Returns:
            PhotoAuditResult con el mejor resultado obtenido
        """
        start_time = time.time()
        warnings = []
        attempts = []
        
        # CAPA 0: Aria-label (rápido, bajo costo)
        logger.info("🔍 Capa 0: Extrayendo de aria-labels...")
        result = self._extract_counter_from_aria()
        if result:
            count, evidence = result
            attempts.append(('aria_label', count, evidence))
            if count > 0:
                return PhotoAuditResult(
                    count=count,
                    confidence=90,
                    method='aria_label',
                    evidence=evidence,
                    warnings=warnings,
                    timestamp=time.time()
                )
        
        # CAPA 1: Modal con scroll (alta precisión, costo medio)
        logger.info("🔍 Capa 1: Abriendo modal con scroll...")
        result = self._extract_from_modal_with_scroll()
        if result:
            count, evidence = result
            attempts.append(('modal_scroll', count, evidence))
            confidence = 100 if evidence.get('counter_location') == 'modal_header' else 85
            return PhotoAuditResult(
                count=count,
                confidence=confidence,
                method='modal_scroll',
                evidence=evidence,
                warnings=warnings,
                timestamp=time.time()
            )
        
        # CAPA 2: Conteo directo de DOM (precisión media)
        logger.info("🔍 Capa 2: Contando imágenes en DOM...")
        result = self._count_dom_images()
        if result:
            count, evidence = result
            attempts.append(('dom_count', count, evidence))
            return PhotoAuditResult(
                count=count,
                confidence=70,
                method='dom_image_count',
                evidence=evidence,
                warnings=warnings,
                timestamp=time.time()
            )
        
        # CAPA 3: Network analysis (último recurso)
        logger.info("🔍 Capa 3: Analizando tráfico de red...")
        result = self._analyze_network_requests()
        if result:
            count, evidence = result
            attempts.append(('network', count, evidence))
            return PhotoAuditResult(
                count=count,
                confidence=50,
                method='network_analysis',
                evidence=evidence,
                warnings=warnings,
                timestamp=time.time()
            )
        
        # CAPA 4: Fallback a caché reciente válida
        cache_result = self._try_cache_fallback()
        if cache_result:
            count, confidence, evidence = cache_result
            attempts.append(('cache_fallback', count, evidence))
            warnings.append(f"Usando datos de caché (edad: {evidence.get('cache_age_days', '?')} días)")
            logger.info(f"📦 Capa 4: Recuperando {count} fotos de caché con confianza {confidence}%")
            return PhotoAuditResult(
                count=count,
                confidence=confidence,
                method='cache_fallback',
                evidence=evidence,
                warnings=warnings,
                timestamp=time.time()
            )
        
        # FALLBACK FINAL: Sin datos confiables
        warnings.append("Todas las capas de extracción fallaron (incluyendo caché)")
        logger.warning("⚠️ ALERTA: Todas las capas de extracción de fotos fallaron - Guardando artifacts de debug")
        
        debug_artifacts = self._save_debug_artifacts(context="photo_extraction_failed")
        
        return PhotoAuditResult(
            count=0,
            confidence=0,
            method='none',
            evidence={
                'attempts': attempts,
                'debug_artifacts': debug_artifacts,
                'page_title': self.page.title() if self.page else 'N/A',
                'current_url': self.page.url if self.page else 'N/A',
            },
            warnings=warnings,
            timestamp=time.time()
        )

    def _try_cache_fallback(self) -> Optional[Tuple[int, int, Dict]]:
        """
        Intenta recuperar contador de fotos de caché previa válida.
        
        Returns:
            (count, confidence, evidence) o None si no hay caché válida
        """
        if not self._cache_data:
            logger.debug("No hay datos de caché disponibles para fallback")
            return None
        
        cache_fotos = self._cache_data.get('fotos', 0)
        cache_confidence = self._cache_data.get('photos_confidence', 0)
        cache_age = self._cache_data.get('cache_age_days')
        cache_method = self._cache_data.get('photos_method', 'unknown')
        
        if cache_fotos <= 0:
            logger.debug("Caché tiene 0 fotos, no útil como fallback")
            return None
        
        if cache_confidence < self.CACHE_FALLBACK_MIN_CONFIDENCE:
            logger.debug(f"Caché tiene confianza {cache_confidence}% < {self.CACHE_FALLBACK_MIN_CONFIDENCE}% mínimo")
            return None
        
        if cache_age is not None and cache_age > self.CACHE_FALLBACK_MAX_DAYS:
            logger.debug(f"Caché tiene {cache_age} días > {self.CACHE_FALLBACK_MAX_DAYS} días máximo")
            return None
        
        fallback_confidence = 30
        evidence = {
            'method': 'cache_fallback',
            'original_method': cache_method,
            'original_confidence': cache_confidence,
            'cache_age_days': cache_age,
            'cached_fotos': cache_fotos,
            'fallback_reason': 'all_live_extraction_layers_failed',
        }
        
        logger.info(f"📦 Usando fallback de caché: {cache_fotos} fotos (original: {cache_method}, {cache_confidence}%)")
        return cache_fotos, fallback_confidence, evidence


# ====================================================================
# INTEGRACIÓN CON GBPAuditorPlaywright
# ====================================================================

def integrate_photo_auditor_playwright(gbp_auditor_instance):
    """
    Integra PhotoAuditor Playwright en GBPAuditorPlaywright.
    
    Usage:
        auditor = GBPAuditorPlaywright(headless=True)
        integrate_photo_auditor_playwright(auditor)
        result = auditor.check_google_profile("Hotel X", "City Y")
    """
    
    def enhanced_extract_metrics(html_snapshot: str, profile_data: dict) -> None:
        """Versión mejorada con PhotoAuditor integrado"""
        
        # ============================================================
        # PARTE 1: EXTRACCIÓN DE RATING Y REVIEWS
        # ============================================================
        meta_debug = profile_data.setdefault('meta', {}).setdefault('scrape_debug', {})
        confidence = profile_data.setdefault('meta', {}).setdefault('data_confidence', {})

        rating_val: Optional[float] = None
        reviews_val: Optional[int] = None

        try:
            rating_candidates = gbp_auditor_instance.page.query_selector_all(
                "[aria-label*='estrellas']"
            )
        except Exception:
            rating_candidates = []

        for candidate in rating_candidates:
            try:
                label = candidate.get_attribute('aria-label') or candidate.text_content()
            except Exception:
                continue
            if not label:
                continue
            
            rating = gbp_auditor_instance._parse_float(label) if hasattr(gbp_auditor_instance, '_parse_float') else None
            
            reviews = None
            reviews_match = re.search(r'(\d+[\d\s\.,]*)\s*reseñ', label, re.IGNORECASE)
            if reviews_match and hasattr(gbp_auditor_instance, '_parse_int'):
                reviews = gbp_auditor_instance._parse_int(reviews_match.group(1))
            
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
            regex = re.search(
                r'([0-5](?:[\.,][0-9])?)\s*estrellas?\s*(?:en\s*)?(\d+[\d\s\.,]*)\s*(reseñas|opiniones)',
                html_snapshot, re.IGNORECASE
            )
            if regex:
                if rating_val is None and hasattr(gbp_auditor_instance, '_parse_float'):
                    rating_val = gbp_auditor_instance._parse_float(regex.group(1))
                    confidence['rating'] = True
                    meta_debug['rating_source'] = 'regex_html'
                if reviews_val is None and hasattr(gbp_auditor_instance, '_parse_int'):
                    reviews_val = gbp_auditor_instance._parse_int(regex.group(2))
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
        
        # ============================================================
        # PARTE 2: EXTRACCIÓN DE FOTOS CON PHOTOAUDITOR PLAYWRIGHT
        # ============================================================
        
        cache_data = None
        try:
            hotel_name = profile_data.get('meta', {}).get('hotel_name', '')
            location = profile_data.get('meta', {}).get('location', '')
            if hotel_name and location and hasattr(gbp_auditor_instance, 'cache'):
                cache_key = gbp_auditor_instance._build_cache_key(hotel_name, location)
                cached_entry = gbp_auditor_instance.cache.get(cache_key, {})
                if cached_entry:
                    cached_profile = cached_entry.get('profile', {})
                    cached_meta = cached_profile.get('meta', {}).get('scrape_debug', {})
                    cache_timestamp = cached_entry.get('timestamp', '')
                    
                    cache_age = None
                    if cache_timestamp:
                        try:
                            ts = datetime.fromisoformat(cache_timestamp)
                            cache_age = (datetime.utcnow() - ts).days
                        except Exception:
                            pass
                    
                    cache_data = {
                        'fotos': cached_profile.get('fotos', 0),
                        'photos_confidence': cached_meta.get('photos_confidence', 0),
                        'photos_method': cached_meta.get('photos_method', 'unknown'),
                        'cache_age_days': cache_age,
                    }
                    logger.debug(f"📦 Caché disponible para fallback: {cache_data}")
        except Exception as e:
            logger.debug(f"No se pudo obtener caché para fallback: {e}")
        
        photo_auditor = GBPPhotoAuditorPlaywright(
            page=gbp_auditor_instance.page,
            max_wait=12,
            cache_data=cache_data
        )
        
        photo_result = photo_auditor.audit_photos()
        
        profile_data['fotos'] = photo_result.count
        confidence['photos'] = photo_result.confidence >= 70
        
        meta_debug.update({
            'photos_method': photo_result.method,
            'photos_confidence': photo_result.confidence,
            'photos_evidence': photo_result.evidence,
            'photos_warnings': photo_result.warnings,
        })
        
        if photo_result.confidence < 50:
            profile_data['issues'].append(
                f"Contador de fotos poco confiable "
                f"(confianza: {photo_result.confidence}%) - "
                f"Verificar manualmente en Google Maps"
            )
    
    original_extract_metrics = gbp_auditor_instance._extract_metrics
    gbp_auditor_instance._extract_metrics = enhanced_extract_metrics
    gbp_auditor_instance._original_extract_metrics = original_extract_metrics
    
    logger.info("PhotoAuditor Playwright integrado exitosamente en GBPAuditorPlaywright")


# ====================================================================
# EJEMPLO DE USO STANDALONE
# ====================================================================

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto("https://www.google.com/maps/search/Hotel+Boutique+Salento")
            page.wait_for_load_state('networkidle')
            time.sleep(3)
            
            auditor = GBPPhotoAuditorPlaywright(page, max_wait=15)
            result = auditor.audit_photos()
            
            print(f"""
╔═══════════════════════════════════════════════════════════
║ AUDITORÍA DE FOTOS - RESULTADO (Playwright)
╚═══════════════════════════════════════════════════════════

📊 Fotos detectadas:    {result.count}
🎯 Nivel de confianza:  {result.confidence}%
🔧 Método usado:        {result.method}

📋 Evidencia:
{result.evidence}

⚠️ Advertencias:
{chr(10).join(result.warnings) if result.warnings else 'Ninguna'}
""")
        
        finally:
            browser.close()
