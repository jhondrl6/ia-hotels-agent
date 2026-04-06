"""
GBP AUDITOR FACTORY
===================
Factory que retorna el auditor GBP usando Selenium.

Uso:
    from modules.scrapers.gbp_factory import get_gbp_auditor
    
    auditor = get_gbp_auditor(headless=True)
    result = auditor.check_google_profile("Hotel X", "City Y")
"""

import logging
from typing import Any, Dict, Optional

from modules.scrapers.drivers import create_driver

logger = logging.getLogger(__name__)


def get_gbp_auditor(headless: bool = True):
    """
    Factory que retorna el auditor GBP usando Selenium.

    Args:
        headless: Ejecutar en modo headless

    Returns:
        Instancia de GBPAuditor (Selenium)

    Raises:
        RuntimeError: Si Selenium no esta disponible
    """
    try:
        from modules.scrapers.gbp_auditor import GBPAuditor
        auditor = GBPAuditor(headless=headless)
        logger.info("Usando GBPAuditor (Selenium)")
        return auditor
    except ImportError as e:
        raise RuntimeError(f"Selenium no disponible: {e}")


def get_horarios_detector(driver_instance):
    """
    Retorna el detector de horarios apropiado para Selenium WebDriver.

    Args:
        driver_instance: Instancia de Selenium WebDriver

    Returns:
        HorariosDetector configurado
    """
    from selenium.webdriver.remote.webdriver import WebDriver

    if not isinstance(driver_instance, WebDriver):
        raise TypeError(
            f"driver_instance debe ser Selenium WebDriver, no {type(driver_instance).__name__}"
        )

    from modules.utils.horarios_detector import HorariosDetector
    logger.debug("Usando HorariosDetector (Selenium)")
    return HorariosDetector(driver_instance)


class GBPAuditorAuto:
    """
    Wrapper que expone el auditor GBP de Selenium.

    Usage:
        auditor = GBPAuditorAuto(headless=True)
        result = auditor.check_google_profile("Hotel X", "City Y")
    """

    driver_type = "selenium"

    def __init__(self, headless: bool = True):
        self._auditor = get_gbp_auditor(headless)

    def check_google_profile(
        self,
        hotel_name: str,
        location: str,
        hotel_data: Optional[Dict[str, Any]] = None,
        region: str = "default",
    ) -> dict:
        """Proxy al metodo del auditor subyacente."""
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
        """Proxy al metodo del auditor subyacente."""
        return self._auditor.validate_location_only(
            hotel_name=hotel_name,
            location=location,
            **kwargs
        )

    @property
    def auditor(self):
        """Acceso directo al auditor subyacente."""
        return self._auditor


def get_driver_instance(
    driver_type: str = "selenium",
    headless: bool = True,
    **kwargs
):
    """
    Retorna una instancia que implementa DriverInterface.

    Args:
        driver_type: Tipo de driver ("selenium").
        headless: Ejecutar en modo headless.
        **kwargs: Argumentos adicionales para el driver.

    Returns:
        Instancia que implementa DriverInterface.

    Raises:
        ValueError: Si el tipo de driver no es valido.
        RuntimeError: Si el driver no esta disponible.
    """
    if driver_type != "selenium":
        raise ValueError(f"Tipo de driver no soportado: {driver_type}. Use 'selenium'.")

    driver = create_driver(driver_type, headless=headless, **kwargs)
    logger.info(f"Driver creado: {driver_type}")
    return driver


def create_auditor_with_interface(
    driver_type: str = "selenium",
    headless: bool = True,
) -> Dict[str, Any]:
    """
    Crea auditor con interfaz unificada.

    Args:
        driver_type: Tipo de driver (debe ser "selenium").
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
    auditor = GBPAuditorAuto(headless=headless)

    return {
        "driver": driver,
        "auditor": auditor,
        "driver_type": "selenium",
    }
