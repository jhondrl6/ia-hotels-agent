"""
GBP PHOTO AUDITOR - Módulo de Captura Robusta de Fotos
========================================================
Estrategia multi-capa para extraer el contador de fotos de Google Business Profile
con técnicas de fallback progresivo y validación de confianza.

NIVEL DE CONFIANZA:
- 100: Contador explícito del modal confirmado con scroll
- 90: Contador del aria-label validado con imágenes visibles
- 70: Conteo directo de elementos <img> únicos
- 50: Estimación por Network Activity (peticiones de imágenes)
- 30: Cache reciente (<7 días)
- 10: Inferencia por densidad del DOM
- 0: Sin datos confiables

MULTI-DRIVER SUPPORT:
- Selenium WebDriver: Compatible via SeleniumAdapter
- Playwright Page: Compatible via PlaywrightAdapter
"""

import re
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Any, Protocol, runtime_checkable
from dataclasses import dataclass
from abc import ABC, abstractmethod

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    NoSuchElementException
)

logger = logging.getLogger(__name__)


@runtime_checkable
class DriverAdapterProtocol(Protocol):
    """Protocol defining the interface for driver adapters."""
    
    @property
    def current_url(self) -> str: ...
    
    @property
    def page_source(self) -> str: ...
    
    @property
    def title(self) -> str: ...
    
    def find_elements(self, selector: str) -> List[Any]: ...
    def find_element(self, selector: str) -> Optional[Any]: ...
    def execute_script(self, script: str, *args) -> Any: ...
    def save_screenshot(self, path: str) -> bool: ...
    def get_log(self, log_type: str) -> List[Any]: ...
    def wait_for_element(self, selector: str, timeout: int) -> Optional[Any]: ...
    def scroll_into_view(self, element: Any) -> None: ...
    def click_element(self, element: Any) -> None: ...
    def send_keys(self, keys: str) -> None: ...
    def get_attribute(self, element: Any, attribute: str) -> Optional[str]: ...
    def is_displayed(self, element: Any) -> bool: ...
    def get_text(self, element: Any) -> str: ...
    def get_tag_name(self, element: Any) -> str: ...
    def move_to_element(self, element: Any) -> None: ...
    def scroll_by(self, element: Any, x: int, y: int) -> None: ...
    def find_sub_elements(self, element: Any, selector: str) -> List[Any]: ...


class DriverAdapterBase(ABC):
    """Abstract base class for driver adapters."""
    
    @property
    @abstractmethod
    def current_url(self) -> str: pass
    
    @property
    @abstractmethod
    def page_source(self) -> str: pass
    
    @property
    @abstractmethod
    def title(self) -> str: pass
    
    @abstractmethod
    def find_elements(self, selector: str) -> List[Any]: pass
    
    @abstractmethod
    def find_element(self, selector: str) -> Optional[Any]: pass
    
    @abstractmethod
    def execute_script(self, script: str, *args) -> Any: pass
    
    @abstractmethod
    def save_screenshot(self, path: str) -> bool: pass
    
    @abstractmethod
    def get_log(self, log_type: str) -> List[Any]: pass
    
    @abstractmethod
    def wait_for_element(self, selector: str, timeout: int) -> Optional[Any]: pass
    
    @abstractmethod
    def scroll_into_view(self, element: Any) -> None: pass
    
    @abstractmethod
    def click_element(self, element: Any) -> None: pass
    
    @abstractmethod
    def send_keys(self, keys: str) -> None: pass
    
    @abstractmethod
    def get_attribute(self, element: Any, attribute: str) -> Optional[str]: pass
    
    @abstractmethod
    def is_displayed(self, element: Any) -> bool: pass
    
    @abstractmethod
    def get_text(self, element: Any) -> str: pass
    
    @abstractmethod
    def get_tag_name(self, element: Any) -> str: pass
    
    @abstractmethod
    def move_to_element(self, element: Any) -> None: pass
    
    @abstractmethod
    def scroll_by(self, element: Any, x: int, y: int) -> None: pass
    
    @abstractmethod
    def find_sub_elements(self, element: Any, selector: str) -> List[Any]: pass


class SeleniumAdapter(DriverAdapterBase):
    """Adapter for Selenium WebDriver - wraps existing driver instance."""
    
    def __init__(self, driver):
        self._driver = driver
        self._actions: Optional[ActionChains] = None
    
    @property
    def current_url(self) -> str:
        return self._driver.current_url
    
    @property
    def page_source(self) -> str:
        return self._driver.page_source
    
    @property
    def title(self) -> str:
        return self._driver.title
    
    def find_elements(self, selector: str) -> List[Any]:
        return self._driver.find_elements(By.CSS_SELECTOR, selector)
    
    def find_element(self, selector: str) -> Optional[Any]:
        try:
            return self._driver.find_element(By.CSS_SELECTOR, selector)
        except NoSuchElementException:
            return None
    
    def execute_script(self, script: str, *args) -> Any:
        return self._driver.execute_script(script, *args)
    
    def save_screenshot(self, path: str) -> bool:
        return self._driver.save_screenshot(path)
    
    def get_log(self, log_type: str) -> List[Any]:
        try:
            return self._driver.get_log(log_type)
        except Exception:
            return []
    
    def wait_for_element(self, selector: str, timeout: int) -> Optional[Any]:
        try:
            return WebDriverWait(self._driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
        except TimeoutException:
            return None
    
    def scroll_into_view(self, element: Any) -> None:
        self._driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            element
        )
    
    def click_element(self, element: Any) -> None:
        try:
            if self._actions is None:
                self._actions = ActionChains(self._driver)
            self._actions.move_to_element(element).pause(0.3).click().perform()
        except Exception:
            self._driver.execute_script("arguments[0].click();", element)
    
    def send_keys(self, keys: str) -> None:
        if self._actions is None:
            self._actions = ActionChains(self._driver)
        self._actions.send_keys(keys).perform()
    
    def get_attribute(self, element: Any, attribute: str) -> Optional[str]:
        try:
            return element.get_attribute(attribute)
        except StaleElementReferenceException:
            return None
    
    def is_displayed(self, element: Any) -> bool:
        try:
            return element.is_displayed()
        except StaleElementReferenceException:
            return False
    
    def get_text(self, element: Any) -> str:
        try:
            return element.text
        except StaleElementReferenceException:
            return ""
    
    def get_tag_name(self, element: Any) -> str:
        try:
            return element.tag_name
        except StaleElementReferenceException:
            return ""
    
    def move_to_element(self, element: Any) -> None:
        if self._actions is None:
            self._actions = ActionChains(self._driver)
        self._actions.move_to_element(element).perform()
    
    def scroll_by(self, element: Any, x: int, y: int) -> None:
        self._driver.execute_script("arguments[0].scrollBy(arguments[1], arguments[2]);", element, x, y)
    
    def find_sub_elements(self, element: Any, selector: str) -> List[Any]:
        try:
            return element.find_elements(By.CSS_SELECTOR, selector)
        except StaleElementReferenceException:
            return []


class PlaywrightAdapter(DriverAdapterBase):
    """Adapter for Playwright Page - wraps existing page instance."""
    
    def __init__(self, page):
        self._page = page
    
    @property
    def current_url(self) -> str:
        return self._page.url
    
    @property
    def page_source(self) -> str:
        return self._page.content()
    
    @property
    def title(self) -> str:
        return self._page.title()
    
    def find_elements(self, selector: str) -> List[Any]:
        try:
            return self._page.locator(selector).all()
        except Exception:
            return []
    
    def find_element(self, selector: str) -> Optional[Any]:
        try:
            locator = self._page.locator(selector)
            if locator.count() > 0:
                return locator.first
            return None
        except Exception:
            return None
    
    def execute_script(self, script: str, *args) -> Any:
        if args:
            arg_list = ", ".join([f"arguments[{i}]" for i in range(len(args))])
            return self._page.evaluate(f"([{arg_list}]) => {{ {script} }}", list(args))
        return self._page.evaluate(script)
    
    def save_screenshot(self, path: str) -> bool:
        try:
            self._page.screenshot(path=path)
            return True
        except Exception:
            return False
    
    def get_log(self, log_type: str) -> List[Any]:
        return []
    
    def wait_for_element(self, selector: str, timeout: int) -> Optional[Any]:
        try:
            self._page.wait_for_selector(selector, timeout=timeout * 1000, state="visible")
            return self.find_element(selector)
        except Exception:
            return None
    
    def scroll_into_view(self, element: Any) -> None:
        try:
            if hasattr(element, 'scroll_into_view_if_needed'):
                element.scroll_into_view_if_needed()
            else:
                element.evaluate("el => el.scrollIntoView({block: 'center'})")
        except Exception:
            pass
    
    def click_element(self, element: Any) -> None:
        try:
            if hasattr(element, 'click'):
                element.click()
            else:
                element.evaluate("el => el.click()")
        except Exception:
            self._page.evaluate("arguments[0].click()", element)
    
    def send_keys(self, keys: str) -> None:
        self._page.keyboard.press(keys)
    
    def get_attribute(self, element: Any, attribute: str) -> Optional[str]:
        try:
            if hasattr(element, 'get_attribute'):
                return element.get_attribute(attribute)
            return element.evaluate(f"el => el.getAttribute('{attribute}')")
        except Exception:
            return None
    
    def is_displayed(self, element: Any) -> bool:
        try:
            if hasattr(element, 'is_visible'):
                return element.is_visible()
            return element.evaluate("el => el.offsetParent !== null")
        except Exception:
            return False
    
    def get_text(self, element: Any) -> str:
        try:
            if hasattr(element, 'text_content'):
                return element.text_content() or ""
            return element.evaluate("el => el.textContent") or ""
        except Exception:
            return ""
    
    def get_tag_name(self, element: Any) -> str:
        try:
            if hasattr(element, 'evaluate'):
                return element.evaluate("el => el.tagName.toLowerCase()")
            return ""
        except Exception:
            return ""
    
    def move_to_element(self, element: Any) -> None:
        try:
            if hasattr(element, 'hover'):
                element.hover()
            else:
                self._page.hover(element)
        except Exception:
            pass
    
    def scroll_by(self, element: Any, x: int, y: int) -> None:
        try:
            element.evaluate(f"el => el.scrollBy({x}, {y})")
        except Exception:
            pass
    
    def find_sub_elements(self, element: Any, selector: str) -> List[Any]:
        try:
            if hasattr(element, 'locator'):
                return element.locator(selector).all()
            return []
        except Exception:
            return []


def wrap_driver(driver_or_page) -> DriverAdapterBase:
    """
    Wrap a Selenium WebDriver or Playwright Page into a common adapter interface.
    
    Args:
        driver_or_page: Either a Selenium WebDriver instance or Playwright Page instance.
        
    Returns:
        DriverAdapterBase implementation appropriate for the driver type.
        
    Raises:
        ValueError: If the driver type is not recognized.
    """
    driver_type = type(driver_or_page).__name__
    module_name = getattr(type(driver_or_page), '__module__', '')
    
    if 'playwright' in module_name.lower() or driver_type == 'Page':
        logger.debug("Wrapping Playwright Page with PlaywrightAdapter")
        return PlaywrightAdapter(driver_or_page)
    
    if 'selenium' in module_name.lower() or hasattr(driver_or_page, 'find_elements'):
        if hasattr(driver_or_page, 'find_element') and not hasattr(driver_or_page, 'locator'):
            logger.debug("Wrapping Selenium WebDriver with SeleniumAdapter")
            return SeleniumAdapter(driver_or_page)
    
    if hasattr(driver_or_page, 'locator') and hasattr(driver_or_page, 'evaluate'):
        logger.debug("Wrapping Playwright Page (detected by interface) with PlaywrightAdapter")
        return PlaywrightAdapter(driver_or_page)
    
    raise ValueError(f"Unrecognized driver type: {driver_type} from module {module_name}")


@dataclass
class PhotoAuditResult:
    """Resultado de auditoría de fotos con evidencia trazable"""
    count: int
    confidence: int  # 0-100
    method: str  # Método que logró la extracción
    evidence: Dict[str, any]  # Evidencia forense
    warnings: List[str]  # Alertas durante la captura
    timestamp: float


class GBPPhotoAuditor:
    """
    Auditor especializado en extracción robusta del contador de fotos
    de Google Business Profile con estrategia de fallback en cascada.
    """

    # Selectores conocidos de Google Maps (actualizado Nov 2025 - Auditoría Forense)
    SELECTORS = {
        'photo_button': [
            # Selectores primarios (aria-label)
            "button[aria-label*='Foto']",
            "button[aria-label*='foto']",
            "a[aria-label*='Foto']",
            "a[aria-label*='foto']",
            # Selectores por data attributes
            "button[data-value='Fotos']",
            "[data-tab-id='photos']",
            "[data-item-id='image']",
            # Selectores por role/jsaction
            "[role='tab'][aria-label*='Foto']",
            "[role='tab'][aria-label*='foto']",
            "button[jsaction*='photo']",
            "button[jsaction*='pane.placePhotos']",
            "[jsaction*='pane.placePhotos']",
            # Selectores de galería/imágenes clickeables
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

    # Umbral máximo de edad de caché para fallback (en días)
    CACHE_FALLBACK_MAX_DAYS = 7
    CACHE_FALLBACK_MIN_CONFIDENCE = 70

    def __init__(self, driver, max_wait: int = 15,
                 cache_data: Optional[Dict] = None, places_api_data: Optional[Dict] = None):
        """
        Args:
            driver: Selenium WebDriver, Playwright Page, or DriverAdapterBase instance
            max_wait: Tiempo maximo de espera para elementos (segundos)
            cache_data: Diccionario opcional con datos de cache previos del hotel
                        Formato esperado: {'fotos': int, 'photos_confidence': int,
                                          'photos_method': str, 'cache_age_days': int}
            places_api_data: Diccionario opcional con datos de Places API
                        Formato esperado: {'place_id': str, 'photos': int, 'name': str}
        """
        if isinstance(driver, (SeleniumAdapter, PlaywrightAdapter)):
            self.driver = driver
        elif isinstance(driver, DriverAdapterBase):
            self.driver = driver
        else:
            self.driver = wrap_driver(driver)

        self._raw_driver = driver
        self.max_wait = max_wait
        self._network_log = []
        self._cache_data = cache_data or {}
        self._places_api_data = places_api_data or {}

    def _log_debug_context(self, context: str = "unknown") -> Dict:
        """
        Registra informacion de debug estructurada en logs en vez de
        escribir archivos de screenshot/HTML (que en practica nunca
        produjeron contenido diagnostico util).

        Args:
            context: Identificador del contexto (ej: 'photo_extraction_failed')

        Returns:
            Dict con metadata que se inyecta en el evidence del resultado.
        """
        try:
            page_title = self.driver.title if self.driver else 'N/A'
            current_url = self.driver.current_url if self.driver else 'N/A'
        except Exception:
            page_title = 'N/A'
            current_url = 'N/A'

        logger.warning(
            "GBP Photo Auditor debug [%s] | url=%s | title=%s",
            context, current_url, page_title,
        )
        return {
            'page_title': page_title,
            'current_url': current_url,
        }

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
                elements = self.driver.find_elements(selector)
                for elem in elements:
                    try:
                        label = self.driver.get_attribute(elem, 'aria-label') or self.driver.get_text(elem)
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
        Abre el modal de fotos con reintentos y validacion.
        
        Returns:
            (success, warnings)
        """
        warnings = []
        
        for selector in self.SELECTORS['photo_button']:
            try:
                photo_btn = self.driver.wait_for_element(selector, self.max_wait)
                if not photo_btn:
                    warnings.append(f"Timeout esperando boton: {selector}")
                    continue
                
                self.driver.scroll_into_view(photo_btn)
                time.sleep(0.5)
                
                try:
                    self.driver.click_element(photo_btn)
                except Exception:
                    try:
                        self.driver.execute_script("arguments[0].click();", photo_btn)
                    except Exception:
                        pass
                
                time.sleep(1.5)
                modals = []
                for modal_selector in self.SELECTORS['modal_dialog']:
                    modals.extend(self.driver.find_elements(modal_selector))
                
                if modals and any(self.driver.is_displayed(m) for m in modals):
                    return True, warnings
                else:
                    warnings.append(f"Modal no visible tras click en {selector}")
                    
            except Exception as e:
                warnings.append(f"Error abriendo modal con {selector}: {str(e)}")
                continue
        
        return False, warnings

    def _extract_from_modal_with_scroll(self) -> Optional[Tuple[int, Dict]]:
        """
        Extrae contador del modal navegando con scroll.
        
        Strategy:
        1. Buscar contador explicito en header del modal
        2. Si no existe, hacer scroll y contar imagenes unicas
        3. Validar consistencia con multiples verificaciones
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
            modal_html = self.driver.page_source
            
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
                containers = self.driver.find_elements(modal_selector)
                if containers:
                    modal_container = containers[0]
                    break
            
            if not modal_container:
                return None
            
            unique_images = set()
            last_count = 0
            stale_iterations = 0
            max_iterations = 20
            
            for i in range(max_iterations):
                self.driver.scroll_by(modal_container, 0, 500)
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
                self.driver.send_keys("Escape")
                time.sleep(0.5)
            except Exception:
                pass
        
        return None

    def _count_unique_images(self) -> set:
        """
        Cuenta imagenes unicas en el DOM actual.
        
        Returns:
            Set de URLs unicas de imagenes
        """
        unique_srcs = set()
        
        for selector in self.SELECTORS['image_elements']:
            try:
                elements = self.driver.find_elements(selector)
                for elem in elements:
                    try:
                        tag_name = self.driver.get_tag_name(elem)
                        if tag_name == 'img':
                            src = self.driver.get_attribute(elem, 'src')
                            if src and 'googleusercontent' in src:
                                base_src = re.sub(r'=s\d+-', '=', src)
                                unique_srcs.add(base_src)
                        
                        elif 'background-image' in (self.driver.get_attribute(elem, 'style') or ''):
                            style = self.driver.get_attribute(elem, 'style')
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
        
        Nota: Metodo menos confiable porque no distingue thumbnails
        de galeria completa.
        """
        evidence = {'method': 'dom_img_count'}
        
        try:
            gallery_containers = []
            for selector in self.SELECTORS['gallery_grid']:
                try:
                    containers = self.driver.find_elements(selector)
                    gallery_containers.extend(containers)
                except Exception:
                    continue
            
            if not gallery_containers:
                return None
            
            unique_images = set()
            for container in gallery_containers:
                try:
                    images = self.driver.find_sub_elements(container, 'img')
                    for img in images:
                        src = self.driver.get_attribute(img, 'src')
                        if src and ('googleusercontent' in src or 'ggpht' in src):
                            unique_images.add(src)
                except Exception:
                    continue
            
            count = len(unique_images)
            if count > 0:
                evidence['unique_sources'] = count
                evidence['confidence_note'] = 'Estimacion por thumbnails visibles'
                return count, evidence
            
        except Exception as e:
            evidence['error'] = str(e)
        
        return None

    # ====================================================================
    # CAPA 3: ANÁLISIS DE NETWORK ACTIVITY
    # ====================================================================

    def _analyze_network_requests(self) -> Optional[Tuple[int, Dict]]:
        """
        Analiza peticiones de red para detectar carga de imagenes.
        
        Nota: Requiere habilitar logging en ChromeDriver:
            options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        """
        evidence = {'method': 'network_analysis'}
        
        try:
            logs = self.driver.get_log('performance')
            image_requests = set()
            
            for entry in logs:
                try:
                    import json
                    log_data = json.loads(entry['message'])
                    message = log_data.get('message', {})
                    
                    if message.get('method') == 'Network.responseReceived':
                        response = message.get('params', {}).get('response', {})
                        url = response.get('url', '')
                        mime_type = response.get('mimeType', '')
                        
                        if 'image' in mime_type and 'googleusercontent' in url:
                            base_url = re.sub(r'=s\d+-', '=', url)
                            image_requests.add(base_url)
                except Exception:
                    continue
            
            count = len(image_requests)
            if count > 0:
                evidence['detected_requests'] = count
                evidence['confidence_note'] = 'Basado en trafico de red observado'
                return count, evidence
            
        except Exception as e:
            evidence['error'] = str(e)
            evidence['note'] = 'Requiere habilitar performance logging'
        
        return None

    # ====================================================================
    # CAPA 4: PLACES API FALLBACK
    # ====================================================================

    def _try_places_api_fallback(self) -> Optional[Tuple[int, Dict]]:
        """
        Intenta obtener el conteo de fotos desde Google Places API.
        
        Esta capa usa datos oficiales de la API de Google cuando está disponible,
        proporcionando alta confianza (80%) en el conteo.
        
        Requiere:
            - GOOGLE_MAPS_API_KEY configurada en entorno
            - place_id o datos de búsqueda en places_api_data
            
        Returns:
            (count, evidence) o None si no hay datos de API disponibles
        """
        evidence = {'method': 'places_api_fallback'}
        
        if self._places_api_data and self._places_api_data.get('photos') is not None:
            photos = self._places_api_data.get('photos', 0)
            place_name = self._places_api_data.get('name', 'N/D')
            place_id = self._places_api_data.get('place_id', 'N/D')
            
            evidence['photos_count'] = photos
            evidence['place_name'] = place_name
            evidence['place_id'] = place_id
            evidence['source'] = 'google_places_api'
            evidence['confidence_note'] = 'Dato oficial de Google Places API'
            
            logger.info(f"Places API fallback: {photos} fotos para {place_name}")
            return photos, evidence
        
        try:
            from modules.scrapers.google_places_client import get_places_client
            
            client = get_places_client()
            if not client.is_available:
                evidence['note'] = 'GOOGLE_MAPS_API_KEY no configurada'
                logger.debug("Places API no disponible (sin API key)")
                return None
            
            place_id = self._places_api_data.get('place_id')
            if not place_id:
                evidence['note'] = 'No hay place_id disponible para consulta'
                return None
            
            place_data = client.get_place_details(place_id)
            if place_data and place_data.photos is not None:
                evidence['photos_count'] = place_data.photos
                evidence['place_name'] = place_data.name
                evidence['place_id'] = place_id
                evidence['source'] = 'google_places_api'
                evidence['confidence_note'] = 'Dato oficial de Google Places API'
                
                logger.info(f"Places API fallback: {place_data.photos} fotos para {place_data.name}")
                return place_data.photos, evidence
                
        except ImportError:
            evidence['error'] = 'google_places_client no disponible'
            logger.debug("google_places_client module not found")
        except Exception as e:
            evidence['error'] = str(e)
            logger.warning(f"Error en Places API fallback: {e}")
        
        return None

    # ====================================================================
    # ORQUESTADOR PRINCIPAL
    # ====================================================================

    def audit_photos(self) -> PhotoAuditResult:
        """
        Ejecuta auditoria completa con estrategia de fallback en cascada.
        
        Returns:
            PhotoAuditResult con el mejor resultado obtenido
        """
        start_time = time.time()
        warnings = []
        attempts = []
        
        logger.info("Capa 0: Extrayendo de aria-labels...")
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
        
        logger.info("Capa 1: Abriendo modal con scroll...")
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
        
        logger.info("Capa 2: Contando imagenes en DOM...")
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
        
        logger.info("Capa 3: Analizando trafico de red...")
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
        
        logger.info("Capa 4: Intentando Google Places API...")
        result = self._try_places_api_fallback()
        if result:
            count, evidence = result
            attempts.append(('places_api', count, evidence))
            warnings.append("Usando conteo de fotos de Google Places API")
            return PhotoAuditResult(
                count=count,
                confidence=80,
                method='places_api',
                evidence=evidence,
                warnings=warnings,
                timestamp=time.time()
            )
        
        cache_result = self._try_cache_fallback()
        if cache_result:
            count, confidence, evidence = cache_result
            attempts.append(('cache_fallback', count, evidence))
            warnings.append(f"Usando datos de cache (edad: {evidence.get('cache_age_days', '?')} dias)")
            logger.info(f"Capa 5: Recuperando {count} fotos de cache con confianza {confidence}%")
            return PhotoAuditResult(
                count=count,
                confidence=confidence,
                method='cache_fallback',
                evidence=evidence,
                warnings=warnings,
                timestamp=time.time()
            )
        
        warnings.append("Todas las capas de extraccion fallaron (incluyendo cache)")
        logger.warning("ALERTA: Todas las capas de extraccion de fotos fallaron")
        
        debug_context = self._log_debug_context(context="photo_extraction_failed")

        return PhotoAuditResult(
            count=0,
            confidence=0,
            method='none',
            evidence={
                'attempts': attempts,
                'debug_context': debug_context,
            },
            warnings=warnings,
            timestamp=time.time()
        )

    def _try_cache_fallback(self) -> Optional[Tuple[int, int, Dict]]:
        """
        Intenta recuperar contador de fotos de cache previa valida.
        
        Returns:
            (count, confidence, evidence) o None si no hay cache valida
        """
        if not self._cache_data:
            logger.debug("No hay datos de cache disponibles para fallback")
            return None
        
        cache_fotos = self._cache_data.get('fotos', 0)
        cache_confidence = self._cache_data.get('photos_confidence', 0)
        cache_age = self._cache_data.get('cache_age_days')
        cache_method = self._cache_data.get('photos_method', 'unknown')
        
        if cache_fotos <= 0:
            logger.debug("Cache tiene 0 fotos, no util como fallback")
            return None
        
        if cache_confidence < self.CACHE_FALLBACK_MIN_CONFIDENCE:
            logger.debug(f"Cache tiene confianza {cache_confidence}% < {self.CACHE_FALLBACK_MIN_CONFIDENCE}% minimo")
            return None
        
        if cache_age is not None and cache_age > self.CACHE_FALLBACK_MAX_DAYS:
            logger.debug(f"Cache tiene {cache_age} dias > {self.CACHE_FALLBACK_MAX_DAYS} dias maximo")
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
        
        logger.info(f"Usando fallback de cache: {cache_fotos} fotos (original: {cache_method}, {cache_confidence}%)")
        return cache_fotos, fallback_confidence, evidence


# ====================================================================
# INTEGRACIÓN CON GBPAuditor
# ====================================================================

def integrate_photo_auditor(gbp_auditor_instance):
    """
    Reemplaza el metodo _extract_metrics de GBPAuditor con el auditor mejorado.
    
    MULTI-DRIVER SUPPORT:
        - Detecta automaticamente si el auditor usa Selenium (.driver) o Playwright (.page)
        - Envuelve el driver en un adaptador comun para compatibilidad
    
    Usage:
        auditor = GBPAuditor(headless=True)
        integrate_photo_auditor(auditor)
        result = auditor.check_google_profile("Hotel X", "City Y")
    """
    
    def _get_wrapped_driver():
        """Detecta y envuelve el driver apropiado."""
        if hasattr(gbp_auditor_instance, 'driver'):
            driver = gbp_auditor_instance.driver
            if isinstance(driver, (SeleniumAdapter, PlaywrightAdapter)):
                return driver
            return wrap_driver(driver)
        elif hasattr(gbp_auditor_instance, 'page'):
            page = gbp_auditor_instance.page
            if isinstance(page, (SeleniumAdapter, PlaywrightAdapter)):
                return page
            return wrap_driver(page)
        else:
            raise AttributeError("Driver no reconocido: el auditor debe tener .driver o .page")
    
    def enhanced_extract_metrics(html_snapshot: str, profile_data: dict) -> None:
        """Version mejorada con PhotoAuditor integrado"""
        
        meta_debug = profile_data.setdefault('meta', {}).setdefault('scrape_debug', {})
        confidence = profile_data.setdefault('meta', {}).setdefault('data_confidence', {})

        rating_val: Optional[float] = None
        reviews_val: Optional[int] = None
        
        wrapped_driver = _get_wrapped_driver()

        try:
            rating_candidates = wrapped_driver.find_elements("[aria-label*='estrellas']")
        except Exception:
            rating_candidates = []

        for candidate in rating_candidates:
            try:
                label = wrapped_driver.get_attribute(candidate, 'aria-label') or wrapped_driver.get_text(candidate)
            except Exception:
                continue
            if not label:
                continue
            
            rating = gbp_auditor_instance._parse_float(label)
            
            reviews = None
            reviews_match = re.search(r'(\d+[\d\s\.,]*)\s*reseñ', label, re.IGNORECASE)
            if reviews_match:
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
                if rating_val is None:
                    rating_val = gbp_auditor_instance._parse_float(regex.group(1))
                    confidence['rating'] = True
                    meta_debug['rating_source'] = 'regex_html'
                if reviews_val is None:
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
                            from datetime import datetime
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
                    logger.debug(f"Cache disponible para fallback: {cache_data}")
        except Exception as e:
            logger.debug(f"No se pudo obtener cache para fallback: {e}")
        
        places_api_data = None
        try:
            if hasattr(gbp_auditor_instance, '_geo_validation_result'):
                geo_result = gbp_auditor_instance._geo_validation_result
                if geo_result and hasattr(geo_result, 'place_id'):
                    places_api_data = {
                        'place_id': geo_result.place_id,
                        'photos': getattr(geo_result, 'photo_count', None),
                        'name': profile_data.get('meta', {}).get('hotel_name', 'N/D'),
                    }
                    logger.debug(f"Places API data disponible: {places_api_data}")
        except Exception as e:
            logger.debug(f"No se pudo obtener Places API data: {e}")
        
        photo_auditor = GBPPhotoAuditor(
            driver=wrapped_driver,
            max_wait=12,
            cache_data=cache_data,
            places_api_data=places_api_data
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
    
    logger.info("PhotoAuditor integrado exitosamente en GBPAuditor (Multi-Driver)")


# ====================================================================
# EJEMPLO DE USO STANDALONE
# ====================================================================

if __name__ == "__main__":
    import sys
    
    driver_type = sys.argv[1] if len(sys.argv) > 1 else "selenium"
    
    if driver_type == "playwright":
        from playwright.sync_api import sync_playwright
        
        print("=== Multi-Driver Demo: Playwright ===")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                page.goto("https://www.google.com/maps/search/Hotel+Boutique+Salento")
                time.sleep(3)
                
                auditor = GBPPhotoAuditor(page, max_wait=15)
                result = auditor.audit_photos()
                
                print(f"""
===========================================================
AUDITORIA DE FOTOS - RESULTADO (Playwright)
===========================================================

Fotos detectadas:    {result.count}
Nivel de confianza:  {result.confidence}%
Metodo usado:        {result.method}

Evidencia:
{result.evidence}

Advertencias:
{chr(10).join(result.warnings) if result.warnings else 'Ninguna'}
""")
            finally:
                browser.close()
    else:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        print("=== Multi-Driver Demo: Selenium ===")
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        
        driver = webdriver.Chrome(options=options)
        
        try:
            driver.get("https://www.google.com/maps/search/Hotel+Boutique+Salento")
            time.sleep(3)
            
            auditor = GBPPhotoAuditor(driver, max_wait=15)
            result = auditor.audit_photos()
            
            print(f"""
===========================================================
AUDITORIA DE FOTOS - RESULTADO (Selenium)
===========================================================

Fotos detectadas:    {result.count}
Nivel de confianza:  {result.confidence}%
Metodo usado:        {result.method}

Evidencia:
{result.evidence}

Advertencias:
{chr(10).join(result.warnings) if result.warnings else 'Ninguna'}
""")
        finally:
            driver.quit()
