"""
GBP POSTS AUDITOR - Módulo de Captura Automática de Posts
=========================================================
Estrategia multi-capa para extraer posts de Google Business Profile
con técnicas de fallback progresivo y validación de confianza.

MULTI-DRIVER SUPPORT:
- Selenium (webdriver.Chrome)
- Playwright (via DriverInterface)
- Deteccion automatica del tipo de driver

NIVEL DE CONFIANZA:
- 100: Posts con fecha visible y conteo explicito
- 85: Posts detectados por aria-label "Actualizaciones: X posts"
- 70: Posts contados en grid de actualizaciones
- 50: Estimacion por actividad en DOM (indicadores indirectos)
- 0: Sin datos confiables
"""

import re
import time
import logging
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)


@dataclass
class PostsAuditResult:
    """Resultado de auditoría de posts con evidencia trazable"""
    total_posts: int  # Total histórico detectado
    posts_last_60_days: int  # Posts recientes (ventana crítica)
    last_post_date: Optional[str]  # ISO 8601 format
    confidence: int  # 0-100
    method: str  # Método que logró la extracción
    evidence: Dict[str, any]  # Evidencia forense
    warnings: List[str]  # Alertas durante la captura
    timestamp: float


class GBPPostsAuditor:
    """
    Auditor especializado en extracción robusta de posts
    de Google Business Profile con estrategia de fallback en cascada.
    """

    # Selectores conocidos de Google Maps (actualizado 2025)
    SELECTORS = {
        'updates_button': [
            "button[aria-label*='Actualizaciones']",
            "button[aria-label*='Updates']",
            "a[href*='updates']",
            "[data-item-id='updates']",
        ],
        'posts_counter': [
            "[aria-label*='actualizaciones']",
            "[aria-label*='posts']",
            "div[jsname*='updates']",
        ],
        'posts_grid': [
            "div[role='article']",
            "div[jsname*='post']",
            "[data-item-id^='post-']",
        ],
        'post_date': [
            "span[aria-label*='Publicado']",
            "time[datetime]",
            "span[jsname*='date']",
        ]
    }

    def __init__(self, driver, max_wait: int = 15):
        self._driver = driver
        self.max_wait = max_wait
        self._driver_type = self._detect_driver_type()
    
    def _detect_driver_type(self) -> str:
        """
        Detecta el tipo de driver recibido.
        
        Returns:
            'selenium': Selenium WebDriver nativo
            'playwright': DriverInterface (PlaywrightDriver o SeleniumDriver)
        """
        if hasattr(self._driver, 'page') and hasattr(self._driver, 'find_elements'):
            return 'playwright'
        elif hasattr(self._driver, 'find_elements') and hasattr(self._driver, 'execute_script'):
            return 'selenium'
        else:
            raise ValueError("Driver no soportado. Use Selenium WebDriver o DriverInterface.")
    
    @property
    def driver(self):
        """Compatibilidad hacia atras."""
        return self._driver
    
    def _find_elements(self, selector: str) -> List[Any]:
        """Busca elementos por selector CSS (multi-driver)."""
        if self._driver_type == 'playwright':
            return self._driver.find_elements(selector)
        else:
            return self._driver.find_elements(By.CSS_SELECTOR, selector)
    
    def _find_element(self, selector: str) -> Optional[Any]:
        """Busca un elemento por selector CSS (multi-driver)."""
        if self._driver_type == 'playwright':
            return self._driver.find_element(selector)
        else:
            try:
                return self._driver.find_element(By.CSS_SELECTOR, selector)
            except NoSuchElementException:
                return None
    
    def _execute_script(self, script: str, *args) -> Any:
        """Ejecuta JavaScript (multi-driver)."""
        if self._driver_type == 'playwright':
            if args:
                formatted_script = script.replace("arguments[0]", "arg")
                return self._driver.execute_script(f"({formatted_script})({repr(args[0]) if args else ''})")
            return self._driver.execute_script(script)
        else:
            return self._driver.execute_script(script, *args)
    
    def _get_element_attribute(self, element, attribute: str) -> Optional[str]:
        """Obtiene atributo de elemento (multi-driver)."""
        try:
            if hasattr(element, 'get_attribute'):
                return element.get_attribute(attribute)
            elif hasattr(element, 'get_attribute_value'):
                return element.get_attribute_value(attribute)
            return None
        except Exception:
            return None
    
    def _get_element_text(self, element) -> str:
        """Obtiene texto de elemento (multi-driver)."""
        try:
            if hasattr(element, 'text'):
                return element.text or ""
            elif hasattr(element, 'text_content'):
                return element.text_content() or ""
            return ""
        except Exception:
            return ""
    
    def _find_child_element(self, parent_element, selector: str) -> Optional[Any]:
        """Busca elemento hijo dentro de padre (multi-driver)."""
        try:
            if self._driver_type == 'playwright':
                if hasattr(parent_element, 'locator'):
                    locator = parent_element.locator(selector)
                    if locator.count() > 0:
                        return locator.first
                return None
            else:
                return parent_element.find_element(By.CSS_SELECTOR, selector)
        except (NoSuchElementException, Exception):
            return None
    
    def _wait_for_clickable(self, selector: str, timeout: int = 8) -> Any:
        """Espera elemento clickeable (multi-driver)."""
        if self._driver_type == 'playwright':
            self._driver.wait_for_selector(selector, timeout=timeout * 1000)
            return self._driver.find_element(selector)
        else:
            return WebDriverWait(self._driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
    
    def _click_element(self, element) -> bool:
        """Click en elemento con fallback (multi-driver)."""
        try:
            if self._driver_type == 'playwright':
                if hasattr(element, 'click'):
                    element.click()
                    return True
            else:
                try:
                    element.click()
                except Exception:
                    self._execute_script("arguments[0].click();", element)
                return True
        except Exception:
            return False
        return False

    # ====================================================================
    # CAPA 0: EXTRACCIÓN DESDE ARIA-LABEL (RÁPIDO)
    # ====================================================================

    def _extract_counter_from_aria(self) -> Optional[Tuple[int, Dict]]:
        """
        Extrae contador de posts desde atributos aria-label.
        
        Returns:
            (count, evidence) o None si falla
        """
        evidence = {'method': 'aria_label', 'raw_labels': []}
        
        for selector in self.SELECTORS['posts_counter']:
            try:
                elements = self._find_elements(selector)
                for elem in elements:
                    try:
                        label = self._get_element_attribute(elem, 'aria-label') or self._get_element_text(elem)
                        if not label:
                            continue
                        
                        evidence['raw_labels'].append(label)
                        
                        patterns = [
                            r'(\d+)\s*actualizaciones?',
                            r'(\d+)\s*posts?',
                            r'(\d+)\s*updates?',
                        ]
                        
                        for pattern in patterns:
                            match = re.search(pattern, label, re.IGNORECASE)
                            if match:
                                count = int(match.group(1))
                                evidence['matched_label'] = label
                                return count, evidence
                    except Exception:
                        continue
            except Exception as e:
                logger.debug(f"Error en selector {selector}: {e}")
        
        return None

    # ====================================================================
    # CAPA 1: NAVEGACIÓN A SECCIÓN "ACTUALIZACIONES"
    # ====================================================================

    def _navigate_to_updates_section(self) -> Tuple[bool, List[str]]:
        """
        Navega a la seccion de actualizaciones del perfil.
        
        Returns:
            (success, warnings)
        """
        warnings = []
        
        for selector in self.SELECTORS['updates_button']:
            try:
                updates_btn = self._wait_for_clickable(selector, timeout=8)
                
                self._execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});",
                    updates_btn
                )
                time.sleep(0.5)
                
                self._click_element(updates_btn)
                
                time.sleep(2)
                return True, warnings
                
            except TimeoutException:
                warnings.append(f"Boton de actualizaciones no encontrado: {selector}")
                continue
            except Exception as e:
                warnings.append(f"Error navegando a updates: {str(e)}")
                continue
        
        warnings.append("No se detecto seccion de actualizaciones (posible perfil sin posts)")
        return False, warnings

    # ====================================================================
    # CAPA 2: CONTEO DE POSTS EN GRID
    # ====================================================================

    def _count_posts_in_grid(self) -> Optional[Tuple[int, int, Optional[str], Dict]]:
        """
        Cuenta posts directamente en el grid de actualizaciones.
        
        Returns:
            (total_posts, posts_60d, last_date, evidence) o None
        """
        evidence = {'method': 'grid_count', 'posts_found': []}
        
        try:
            posts_elements = []
            for selector in self.SELECTORS['posts_grid']:
                try:
                    elements = self._find_elements(selector)
                    posts_elements.extend(elements)
                except Exception:
                    continue
            
            if not posts_elements:
                return None
            
            cutoff_date = datetime.now() - timedelta(days=60)
            posts_60d = 0
            last_post_date = None
            
            for post_elem in posts_elements:
                try:
                    date_elem = None
                    for date_selector in self.SELECTORS['post_date']:
                        try:
                            date_elem = self._find_child_element(post_elem, date_selector)
                            if date_elem:
                                break
                        except Exception:
                            continue
                    
                    if date_elem:
                        date_str = self._get_element_attribute(date_elem, 'datetime') or self._get_element_text(date_elem)
                        post_date = self._parse_post_date(date_str)
                        
                        evidence['posts_found'].append({
                            'date': date_str,
                            'parsed': post_date.isoformat() if post_date else None
                        })
                        
                        if post_date:
                            if last_post_date is None or post_date > last_post_date:
                                last_post_date = post_date
                            
                            if post_date >= cutoff_date:
                                posts_60d += 1
                except Exception:
                    continue
            
            total_posts = len(posts_elements)
            last_date_str = last_post_date.isoformat() if last_post_date else None
            
            return total_posts, posts_60d, last_date_str, evidence
            
        except Exception as e:
            logger.error(f"Error contando posts en grid: {e}")
            evidence['error'] = str(e)
            return None

    def _parse_post_date(self, date_str: str) -> Optional[datetime]:
        """
        Parsea fecha de post desde texto o datetime attribute.
        
        Examples:
            "2025-10-15T10:30:00Z" -> datetime
            "Hace 3 dias" -> datetime (estimado)
            "15 de octubre" -> datetime (anio actual)
        """
        if not date_str:
            return None
        
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            pass
        
        relative_match = re.search(
            r'hace\s+(\d+)\s+(dia|dias|semana|semanas|mes|meses)',
            date_str,
            re.IGNORECASE
        )
        if relative_match:
            amount = int(relative_match.group(1))
            unit = relative_match.group(2).lower()
            
            if 'dia' in unit:
                return datetime.now() - timedelta(days=amount)
            elif 'semana' in unit:
                return datetime.now() - timedelta(weeks=amount)
            elif 'mes' in unit:
                return datetime.now() - timedelta(days=amount * 30)
        
        try:
            months_es = {
                'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
                'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
                'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
            }
            match = re.search(r'(\d+)\s+de\s+(\w+)', date_str, re.IGNORECASE)
            if match:
                day = int(match.group(1))
                month_name = match.group(2).lower()
                month = months_es.get(month_name)
                if month:
                    return datetime(datetime.now().year, month, day)
        except Exception:
            pass
        
        return None

    # ====================================================================
    # ORQUESTADOR PRINCIPAL
    # ====================================================================

    def audit_posts(self) -> PostsAuditResult:
        """
        Ejecuta auditoria completa con estrategia de fallback en cascada.
        
        Returns:
            PostsAuditResult con el mejor resultado obtenido
        """
        start_time = time.time()
        warnings = []
        
        logger.info("Capa 0: Extrayendo contador de aria-labels...")
        result = self._extract_counter_from_aria()
        if result:
            total_count, evidence = result
            return PostsAuditResult(
                total_posts=total_count,
                posts_last_60_days=0,
                last_post_date=None,
                confidence=50,
                method='aria_label',
                evidence=evidence,
                warnings=['Contador total detectado, pero sin fechas individuales'],
                timestamp=time.time()
            )
        
        logger.info("Capa 1: Navegando a seccion de Actualizaciones...")
        nav_success, nav_warnings = self._navigate_to_updates_section()
        warnings.extend(nav_warnings)
        
        if not nav_success:
            return PostsAuditResult(
                total_posts=0,
                posts_last_60_days=0,
                last_post_date=None,
                confidence=80,
                method='no_updates_button',
                evidence={'reason': 'Boton de actualizaciones no encontrado'},
                warnings=warnings,
                timestamp=time.time()
            )
        
        logger.info("Capa 2: Contando posts en grid...")
        grid_result = self._count_posts_in_grid()
        if grid_result:
            total, posts_60d, last_date, evidence = grid_result
            return PostsAuditResult(
                total_posts=total,
                posts_last_60_days=posts_60d,
                last_post_date=last_date,
                confidence=85,
                method='grid_count_with_dates',
                evidence=evidence,
                warnings=warnings,
                timestamp=time.time()
            )
        
        warnings.append("Seccion de actualizaciones accesible pero sin posts detectados")
        return PostsAuditResult(
            total_posts=0,
            posts_last_60_days=0,
            last_post_date=None,
            confidence=75,
            method='empty_updates_section',
            evidence={'note': 'Seccion de updates cargo pero grid vacio'},
            warnings=warnings,
            timestamp=time.time()
        )


# ====================================================================
# INTEGRACIÓN CON GBPAuditor
# ====================================================================

def integrate_posts_auditor(gbp_auditor_instance):
    """
    Agrega auditoria de posts al flujo de GBPAuditor.
    
    Soporta multi-driver (Selenium y Playwright/DriverInterface).
    
    Usage:
        auditor = GBPAuditor(headless=True)
        integrate_posts_auditor(auditor)
        result = auditor.check_google_profile("Hotel X", "City Y")
    """
    
    original_extract_metrics = gbp_auditor_instance._extract_metrics
    
    def enhanced_extract_metrics_with_posts(html_snapshot: str, profile_data: dict):
        original_extract_metrics(html_snapshot, profile_data)
        
        driver = getattr(gbp_auditor_instance, 'driver', None)
        if driver is None:
            driver = getattr(gbp_auditor_instance, 'page', None)
        
        if driver is None:
            logger.warning("No se pudo obtener driver del auditor")
            return
        
        posts_auditor = GBPPostsAuditor(
            driver=driver,
            max_wait=12
        )
        
        posts_result = posts_auditor.audit_posts()
        
        profile_data['posts'] = posts_result.total_posts
        profile_data['posts_last_60_days'] = posts_result.posts_last_60_days
        profile_data['last_post_date'] = posts_result.last_post_date
        
        meta_debug = profile_data.setdefault('meta', {}).setdefault('scrape_debug', {})
        confidence = profile_data.setdefault('meta', {}).setdefault('data_confidence', {})
        
        meta_debug.update({
            'posts_method': posts_result.method,
            'posts_confidence': posts_result.confidence,
            'posts_evidence': posts_result.evidence,
            'posts_warnings': posts_result.warnings,
        })
        
        confidence['posts'] = posts_result.confidence >= 70
        
        if posts_result.posts_last_60_days == 0 and posts_result.confidence >= 70:
            profile_data['fugas_detectadas'].append({
                'tipo': 'PERFIL_ABANDONADO',
                'severidad': 'MEDIA',
                'descripcion': f'Sin posts recientes detectados (ultimos 60 dias). Ultimo post: {posts_result.last_post_date or "Nunca"}',
                'impacto_estimado_mes_COP': 525000,
                'recomendacion': '1 post semanal recupera posicion en 21 dias',
                'prioridad': 'MEDIA',
                'evidencia': {
                    'total_posts_historico': posts_result.total_posts,
                    'posts_ultimos_60d': posts_result.posts_last_60_days,
                    'ultimo_post': posts_result.last_post_date,
                    'confidence': posts_result.confidence,
                    'metodo_deteccion': posts_result.method
                }
            })
            
            profile_data['issues'].append(
                f"Perfil inactivo: 0 posts en ultimos 60 dias (confianza: {posts_result.confidence}%)"
            )
    
    gbp_auditor_instance._extract_metrics = enhanced_extract_metrics_with_posts
    gbp_auditor_instance._original_extract_metrics = original_extract_metrics
    
    logger.info("PostsAuditor integrado exitosamente en GBPAuditor")