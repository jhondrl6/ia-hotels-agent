#!/usr/bin/env python3
"""
VALIDATE GBP SELECTORS - Script de Auditoría Forense de Selectores
===================================================================
Script para validar que los selectores CSS de extracción de fotos GBP
funcionan correctamente contra perfiles conocidos.

USO:
    python scripts/validate_gbp_selectors.py
    python scripts/validate_gbp_selectors.py --url "https://www.google.com/maps/place/HOTEL+VISPERAS"
    python scripts/validate_gbp_selectors.py --hotel "Hotel Vísperas" --location "Santa Rosa de Cabal"
    python scripts/validate_gbp_selectors.py --all-cached

SALIDA:
    - Muestra qué selectores funcionan y cuáles fallan
    - Guarda screenshot y HTML para análisis
    - Genera reporte JSON en logs/gbp_debug/
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GBPSelectorValidator:
    """Validador forense de selectores para Google Business Profile."""
    
    # Selectores a validar (deben coincidir con gbp_photo_auditor.py)
    PHOTO_BUTTON_SELECTORS = [
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
    ]
    
    PHOTO_COUNTER_SELECTORS = [
        "[aria-label*='fotos']",
        "[aria-label*='Fotos']",
        "[aria-label*='photos']",
    ]
    
    MODAL_SELECTORS = [
        "div[role='dialog']",
        "div[aria-modal='true']",
        ".gallery-modal",
    ]
    
    IMAGE_SELECTORS = [
        "img[src*='googleusercontent']",
        "img[src*='ggpht']",
        "div[style*='background-image']",
    ]

    def __init__(self, headless: bool = True, output_dir: str = "logs/gbp_debug"):
        self.headless = headless
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.driver = None
        self.results = []
        
    def _init_driver(self) -> bool:
        """Inicializa el WebDriver de Chrome."""
        options = Options()
        if self.headless:
            options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            logger.info("✅ WebDriver inicializado correctamente")
            return True
        except Exception as e:
            logger.error(f"❌ Error inicializando WebDriver: {e}")
            return False
    
    def _close_driver(self):
        """Cierra el WebDriver."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
    
    def validate_url(self, url: str) -> Dict:
        """
        Valida todos los selectores contra una URL de Google Maps.
        
        Args:
            url: URL completa de Google Maps
            
        Returns:
            Dict con resultados de validación
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result = {
            'url': url,
            'timestamp': timestamp,
            'driver_ok': False,
            'page_loaded': False,
            'selectors': {
                'photo_button': {},
                'photo_counter': {},
                'modal': {},
                'images': {},
            },
            'summary': {
                'photo_button_working': 0,
                'photo_counter_working': 0,
                'modal_working': 0,
                'images_found': 0,
            },
            'artifacts': {},
            'errors': [],
        }
        
        if not self._init_driver():
            result['errors'].append("No se pudo inicializar WebDriver")
            return result
        
        result['driver_ok'] = True
        
        try:
            # Navegar a la URL
            logger.info(f"🌐 Navegando a: {url}")
            self.driver.get(url)
            time.sleep(5)  # Esperar carga inicial
            
            result['page_loaded'] = True
            result['page_title'] = self.driver.title
            result['current_url'] = self.driver.current_url
            
            # Validar cada categoría de selectores
            result['selectors']['photo_button'] = self._validate_selectors(
                self.PHOTO_BUTTON_SELECTORS, "photo_button"
            )
            result['selectors']['photo_counter'] = self._validate_selectors(
                self.PHOTO_COUNTER_SELECTORS, "photo_counter"
            )
            result['selectors']['modal'] = self._validate_selectors(
                self.MODAL_SELECTORS, "modal"
            )
            result['selectors']['images'] = self._validate_selectors(
                self.IMAGE_SELECTORS, "images"
            )
            
            # Calcular resumen
            result['summary']['photo_button_working'] = sum(
                1 for v in result['selectors']['photo_button'].values() if v['found']
            )
            result['summary']['photo_counter_working'] = sum(
                1 for v in result['selectors']['photo_counter'].values() if v['found']
            )
            result['summary']['modal_working'] = sum(
                1 for v in result['selectors']['modal'].values() if v['found']
            )
            result['summary']['images_found'] = sum(
                v.get('count', 0) for v in result['selectors']['images'].values()
            )
            
            # Guardar screenshot y HTML
            screenshot_path = self.output_dir / f"validate_{timestamp}.png"
            html_path = self.output_dir / f"validate_{timestamp}.html"
            
            try:
                self.driver.save_screenshot(str(screenshot_path))
                result['artifacts']['screenshot'] = str(screenshot_path)
            except Exception as e:
                result['errors'].append(f"Screenshot error: {e}")
            
            try:
                html_path.write_text(self.driver.page_source, encoding='utf-8')
                result['artifacts']['html'] = str(html_path)
            except Exception as e:
                result['errors'].append(f"HTML dump error: {e}")
            
        except Exception as e:
            result['errors'].append(f"Error general: {e}")
            logger.error(f"❌ Error validando URL: {e}")
        finally:
            self._close_driver()
        
        return result
    
    def _validate_selectors(self, selectors: List[str], category: str) -> Dict:
        """Valida una lista de selectores y retorna resultados."""
        results = {}
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                found = len(elements) > 0
                
                selector_result = {
                    'found': found,
                    'count': len(elements),
                }
                
                if found:
                    # Capturar información adicional del primer elemento
                    first_elem = elements[0]
                    try:
                        selector_result['aria_label'] = first_elem.get_attribute('aria-label')
                        selector_result['text'] = first_elem.text[:100] if first_elem.text else None
                        selector_result['tag'] = first_elem.tag_name
                        selector_result['visible'] = first_elem.is_displayed()
                        selector_result['clickable'] = first_elem.is_enabled()
                    except Exception:
                        pass
                    
                    logger.info(f"  ✅ {selector}: {len(elements)} elementos")
                else:
                    logger.info(f"  ❌ {selector}: no encontrado")
                
                results[selector] = selector_result
                
            except Exception as e:
                results[selector] = {
                    'found': False,
                    'count': 0,
                    'error': str(e),
                }
                logger.warning(f"  ⚠️ {selector}: error - {e}")
        
        return results
    
    def validate_hotel(self, hotel_name: str, location: str) -> Dict:
        """
        Valida selectores buscando un hotel en Google Maps.
        
        Args:
            hotel_name: Nombre del hotel
            location: Ciudad/región
            
        Returns:
            Dict con resultados de validación
        """
        search_query = f"{hotel_name} {location}".replace(' ', '+')
        url = f"https://www.google.com/maps/search/{search_query}"
        return self.validate_url(url)
    
    def validate_cached_hotels(self, cache_path: str = "data/cache/gbp_profiles.json") -> List[Dict]:
        """
        Valida selectores contra todos los hoteles en caché.
        
        Args:
            cache_path: Ruta al archivo de caché
            
        Returns:
            Lista de resultados de validación
        """
        cache_file = Path(cache_path)
        if not cache_file.exists():
            logger.error(f"❌ Archivo de caché no encontrado: {cache_path}")
            return []
        
        try:
            cache_data = json.loads(cache_file.read_text(encoding='utf-8'))
        except Exception as e:
            logger.error(f"❌ Error leyendo caché: {e}")
            return []
        
        results = []
        for cache_key, entry in cache_data.items():
            if '::' not in cache_key:
                continue
            
            parts = cache_key.split('::', 1)
            hotel_name = parts[0].strip()
            location = parts[1].strip() if len(parts) > 1 else ""
            
            if not hotel_name:
                continue
            
            logger.info(f"\n{'='*60}")
            logger.info(f"🏨 Validando: {hotel_name} ({location})")
            logger.info(f"{'='*60}")
            
            result = self.validate_hotel(hotel_name, location)
            result['cache_key'] = cache_key
            result['cached_fotos'] = entry.get('profile', {}).get('fotos', 'N/A')
            result['cached_confidence'] = entry.get('profile', {}).get('meta', {}).get(
                'scrape_debug', {}
            ).get('photos_confidence', 'N/A')
            
            results.append(result)
            
            # Esperar entre validaciones para no saturar
            time.sleep(2)
        
        return results
    
    def print_report(self, result: Dict):
        """Imprime un reporte formateado del resultado."""
        print("\n" + "="*70)
        print("📊 REPORTE DE VALIDACIÓN DE SELECTORES GBP")
        print("="*70)
        print(f"URL: {result.get('url', 'N/A')}")
        print(f"Timestamp: {result.get('timestamp', 'N/A')}")
        print(f"Título página: {result.get('page_title', 'N/A')}")
        
        print("\n" + "-"*70)
        print("📌 RESUMEN")
        print("-"*70)
        summary = result.get('summary', {})
        total_photo_selectors = len(self.PHOTO_BUTTON_SELECTORS)
        working = summary.get('photo_button_working', 0)
        print(f"  • Selectores botón foto: {working}/{total_photo_selectors} funcionando")
        print(f"  • Selectores contador:   {summary.get('photo_counter_working', 0)}/{len(self.PHOTO_COUNTER_SELECTORS)}")
        print(f"  • Selectores modal:      {summary.get('modal_working', 0)}/{len(self.MODAL_SELECTORS)}")
        print(f"  • Imágenes encontradas:  {summary.get('images_found', 0)}")
        
        # Estado general
        if working >= 3:
            print("\n  🟢 ESTADO: SALUDABLE - Múltiples selectores funcionando")
        elif working >= 1:
            print("\n  🟡 ESTADO: DEGRADADO - Pocos selectores funcionando")
        else:
            print("\n  🔴 ESTADO: CRÍTICO - Ningún selector de botón foto funciona")
        
        print("\n" + "-"*70)
        print("📋 DETALLE SELECTORES BOTÓN FOTO")
        print("-"*70)
        for selector, data in result.get('selectors', {}).get('photo_button', {}).items():
            status = "✅" if data.get('found') else "❌"
            count = data.get('count', 0)
            extra = ""
            if data.get('aria_label'):
                extra = f" | aria: {data['aria_label'][:40]}..."
            print(f"  {status} {selector}")
            if data.get('found'):
                print(f"      → {count} elementos{extra}")
        
        if result.get('artifacts'):
            print("\n" + "-"*70)
            print("📁 ARTIFACTS GUARDADOS")
            print("-"*70)
            for key, path in result['artifacts'].items():
                print(f"  • {key}: {path}")
        
        if result.get('errors'):
            print("\n" + "-"*70)
            print("⚠️ ERRORES")
            print("-"*70)
            for error in result['errors']:
                print(f"  • {error}")
        
        print("\n" + "="*70 + "\n")
    
    def save_report(self, results: List[Dict], filename: str = None):
        """Guarda el reporte en JSON."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"selector_validation_{timestamp}.json"
        
        report_path = self.output_dir / filename
        report_path.write_text(
            json.dumps(results, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        logger.info(f"📄 Reporte guardado: {report_path}")
        return str(report_path)


def main():
    parser = argparse.ArgumentParser(
        description="Validador forense de selectores GBP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python scripts/validate_gbp_selectors.py --url "https://www.google.com/maps/place/HOTEL+VISPERAS"
  python scripts/validate_gbp_selectors.py --hotel "Hotel Vísperas" --location "Santa Rosa de Cabal"
  python scripts/validate_gbp_selectors.py --all-cached
  python scripts/validate_gbp_selectors.py --all-cached --visible  # Modo no-headless para debug
        """
    )
    
    parser.add_argument(
        '--url',
        type=str,
        help='URL directa de Google Maps a validar'
    )
    parser.add_argument(
        '--hotel',
        type=str,
        help='Nombre del hotel a buscar'
    )
    parser.add_argument(
        '--location',
        type=str,
        default='',
        help='Ubicación del hotel'
    )
    parser.add_argument(
        '--all-cached',
        action='store_true',
        help='Validar todos los hoteles en caché'
    )
    parser.add_argument(
        '--visible',
        action='store_true',
        help='Ejecutar en modo visible (no headless) para debugging'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='logs/gbp_debug',
        help='Directorio de salida para reportes'
    )
    
    args = parser.parse_args()
    
    validator = GBPSelectorValidator(
        headless=not args.visible,
        output_dir=args.output
    )
    
    results = []
    
    if args.url:
        result = validator.validate_url(args.url)
        results.append(result)
        validator.print_report(result)
        
    elif args.hotel:
        result = validator.validate_hotel(args.hotel, args.location)
        results.append(result)
        validator.print_report(result)
        
    elif args.all_cached:
        results = validator.validate_cached_hotels()
        for result in results:
            validator.print_report(result)
    else:
        # Default: validar Hotel Vísperas como caso de prueba
        logger.info("🏨 Ejecutando validación por defecto con Hotel Vísperas")
        result = validator.validate_hotel("Hotel Vísperas", "Santa Rosa de Cabal, Risaralda")
        results.append(result)
        validator.print_report(result)
    
    if results:
        report_path = validator.save_report(results)
        print(f"\n📊 Reporte completo guardado en: {report_path}")
        
        # Resumen final
        total_hotels = len(results)
        healthy = sum(1 for r in results if r.get('summary', {}).get('photo_button_working', 0) >= 3)
        degraded = sum(1 for r in results if 0 < r.get('summary', {}).get('photo_button_working', 0) < 3)
        critical = sum(1 for r in results if r.get('summary', {}).get('photo_button_working', 0) == 0)
        
        print(f"\n🏁 RESUMEN FINAL: {total_hotels} perfiles validados")
        print(f"   🟢 Saludables: {healthy}")
        print(f"   🟡 Degradados: {degraded}")
        print(f"   🔴 Críticos:   {critical}")


if __name__ == "__main__":
    main()
