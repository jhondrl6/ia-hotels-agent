"""
GBP AUDITOR FACTORY
===================
Factory con fallback automatico: Playwright -> Selenium.

Uso:
    from modules.scrapers.gbp_factory import get_gbp_auditor
    
    auditor = get_gbp_auditor(headless=True)
    result = auditor.check_google_profile("Hotel X", "City Y")
"""

import logging
from typing import Any, Dict, Optional, Union

from modules.scrapers.drivers import create_driver, DriverInterface

logger = logging.getLogger(__name__)


def get_gbp_auditor(headless: bool = True, prefer_playwright: bool = False):
    """
    Factory que retorna el auditor GBP disponible.
    
    Orden de preferencia:
    1. Playwright (si prefer_playwright=True y está disponible)
    2. Selenium (fallback)
    
    Args:
        headless: Ejecutar en modo headless
        prefer_playwright: Preferir Playwright sobre Selenium
        
    Returns:
        Instancia de GBPAuditorPlaywright o GBPAuditor
        
    Raises:
        RuntimeError: Si ningún driver está disponible
    """
    if prefer_playwright:
        try:
            from modules.scrapers.gbp_auditor_playwright import GBPAuditorPlaywright
            auditor = GBPAuditorPlaywright(headless=headless)
            if auditor._init_browser():
                logger.info("Usando GBPAuditorPlaywright")
                return auditor
            else:
                logger.warning("Playwright disponible pero falló inicialización, intentando Selenium...")
        except ImportError as e:
            logger.warning(f"Playwright no disponible: {e}, usando Selenium...")
        except Exception as e:
            logger.warning(f"Error inicializando Playwright: {e}, usando Selenium...")
    
    try:
        from modules.scrapers.gbp_auditor import GBPAuditor
        auditor = GBPAuditor(headless=headless)
        logger.info("Usando GBPAuditor (Selenium)")
        return auditor
    except ImportError as e:
        raise RuntimeError(f"Ningún driver disponible. Playwright: no instalado, Selenium: {e}")


def get_horarios_detector(driver_or_page):
    """
    Factory que retorna el detector de horarios apropiado según el tipo de driver.
    
    Detecta automáticamente si es Playwright Page o Selenium WebDriver
    y retorna la instancia correcta.
    
    Args:
        driver_or_page: Instancia de Page (Playwright) o WebDriver (Selenium)
        
    Returns:
        HorariosDetectorPlaywright si es Page, HorariosDetector si es WebDriver
        
    Raises:
        TypeError: Si el argumento no es un driver reconocido
    """
    try:
        from playwright.sync_api import Page
        if isinstance(driver_or_page, Page):
            from modules.utils.horarios_detector_playwright import HorariosDetectorPlaywright
            logger.debug("Usando HorariosDetectorPlaywright")
            return HorariosDetectorPlaywright(driver_or_page)
    except ImportError:
        pass
    
    try:
        from selenium.webdriver.remote.webdriver import WebDriver
        if isinstance(driver_or_page, WebDriver):
            from modules.utils.horarios_detector import HorariosDetector
            logger.debug("Usando HorariosDetector (Selenium)")
            return HorariosDetector(driver_or_page)
    except ImportError:
        pass
    
    raise TypeError(
        f"driver_or_page debe ser Page (Playwright) o WebDriver (Selenium), "
        f"no {type(driver_or_page).__name__}"
    )


class GBPAuditorAuto:
    """
    Wrapper que gestiona automáticamente el driver óptimo.
    
    Usage:
        auditor = GBPAuditorAuto(headless=True)
        result = auditor.check_google_profile("Hotel X", "City Y")
        # Internamente usa Playwright si está disponible, sino Selenium
    """
    
    def __init__(self, headless: bool = True, prefer_playwright: bool = False):
        self._auditor = get_gbp_auditor(headless, prefer_playwright)
        self._driver_type = "playwright" if "Playwright" in type(self._auditor).__name__ else "selenium"
        
    def check_google_profile(
        self,
        hotel_name: str,
        location: str,
        hotel_data: Optional[Dict[str, Any]] = None,
        region: str = "default",
    ) -> dict:
        """Proxy al método del auditor subyacente."""
        return self._auditor.check_google_profile(
            hotel_name=hotel_name,
            location=location,
            hotel_data=hotel_data,
            region=region,
        )
    
    def validate_location_only(
        self,
        hotel_name: str,
        location: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Proxy al método del auditor subyacente."""
        return self._auditor.validate_location_only(
            hotel_name=hotel_name,
            location=location,
            **kwargs
        )
    
    @property
    def driver_type(self) -> str:
        """Retorna el tipo de driver en uso: 'playwright' o 'selenium'."""
        return self._driver_type
    
    @property
    def auditor(self):
        """Acceso directo al auditor subyacente."""
        return self._auditor


def get_driver_instance(
    driver_type: str = "playwright",
    headless: bool = True,
    **kwargs
) -> DriverInterface:
    """
    Retorna una instancia que implementa DriverInterface.
    
    Permite usar Selenium o Playwright de forma transparente.
    
    Args:
        driver_type: Tipo de driver ("selenium" o "playwright").
        headless: Ejecutar en modo headless.
        **kwargs: Argumentos adicionales para el driver.
        
    Returns:
        Instancia que implementa DriverInterface.
        
    Raises:
        ValueError: Si el tipo de driver no es valido.
        RuntimeError: Si el driver solicitado no esta disponible.
    """
    try:
        driver = create_driver(driver_type, headless=headless, **kwargs)
        logger.info(f"Driver creado: {driver_type}")
        return driver
    except ValueError:
        raise
    except Exception as e:
        if driver_type == "playwright":
            logger.warning(f"Playwright no disponible: {e}, intentando Selenium...")
            return create_driver("selenium", headless=headless, **kwargs)
        raise RuntimeError(f"No se pudo crear el driver: {e}")


def create_auditor_with_interface(
    driver_type: str = "playwright",
    headless: bool = True,
) -> Dict[str, Any]:
    """
    Crea auditor con interfaz unificada.
    
    Util para codigo nuevo que no depende de Selenium especificamente.
    
    Args:
        driver_type: Tipo de driver ("selenium" o "playwright").
        headless: Ejecutar en modo headless.
        
    Returns:
        Dict con:
            - 'driver': Instancia de DriverInterface
            - 'auditor': GBPAuditorAuto configurado
            - 'driver_type': Tipo de driver en uso
            
    Raises:
        RuntimeError: Si no se puede crear el driver.
    """
    driver = get_driver_instance(driver_type, headless)
    actual_type = type(driver).__name__.replace("Driver", "").lower()
    
    prefer_pw = actual_type == "playwright"
    auditor = GBPAuditorAuto(headless=headless, prefer_playwright=prefer_pw)
    
    return {
        "driver": driver,
        "auditor": auditor,
        "driver_type": actual_type,
    }
