#!/usr/bin/env python3
"""
Config Checker para IA Hoteles Agent
Verifica variables de entorno, dependencias y configuraciones
"""

import os
import sys
import importlib.util
from pathlib import Path

# ✅ NUEVO: Cargar variables de entorno desde .env
from dotenv import load_dotenv

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Cargar .env desde el directorio raíz del proyecto
ENV_PATH = PROJECT_ROOT / '.env'

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
    print(f"[INFO] Variables cargadas desde: {ENV_PATH}")
else:
    print(f"[WARN] No se encontró .env en: {ENV_PATH}")

class ConfigChecker:
    def __init__(self):
        self.warnings = []
        self.errors = []
        self.checks = []
        
    def check(self, args=None):
        """Ejecuta todas las verificaciones"""
        print("[INFO] VERIFICANDO CONFIGURACION DEL SISTEMA...")
        
        self._check_python_version()
        self._check_core_dependencies()
        self._check_optional_dependencies()
        self._check_env_variables()
        self._check_file_permissions()
        self._check_output_directory(args)
        self._check_api_connectivity()
        
        # Obtener resultados de verificaciones especificas y anadirlos a checks
        deepseek_checks = self._check_deepseek_specifics()
        migration_checks = self._check_migration_readiness()
        geo_checks = self._check_geographic_validation_config()
        
        self.checks.extend(deepseek_checks)
        self.checks.extend(migration_checks)
        self.checks.extend(geo_checks)
        
        return self._generate_report()
    
    def _check_python_version(self):
        """Verifica version de Python"""
        import sys
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            self.checks.append(("[OK] Python 3.8+", "ok"))
        else:
            self.errors.append("Python 3.8 o superior requerido")
    
    def _check_core_dependencies(self):
        """Verifica dependencias core"""
        core_deps = {
            'requests': 'requests',
            'beautifulsoup4': 'bs4',
            'selenium': 'selenium',
            'pandas': 'pandas',
            'openpyxl': 'openpyxl',
            'reportlab': 'reportlab',
            'pillow': 'PIL',
        }
        
        for pkg, import_name in core_deps.items():
            try:
                __import__(import_name)
                self.checks.append((f"[OK] {pkg}", "ok"))
            except ImportError:
                self.errors.append(f"Dependencia faltante: {pkg}")
    
    def _check_optional_dependencies(self):
        """Verifica dependencias opcionales"""
        optional_deps = {
            'playwright': 'playwright',
            'lxml': 'lxml',
        }
        
        for pkg, import_name in optional_deps.items():
            if importlib.util.find_spec(import_name):
                self.checks.append((f"[OK] {pkg} (opcional)", "ok"))
            else:
                self.warnings.append(f"Dependencia opcional no disponible: {pkg}")
    
    def _check_env_variables(self):
        """Verifica variables de entorno criticas"""
        env_vars = {
            'DEEPSEEK_API_KEY': 'optional',
            'ANTHROPIC_API_KEY': 'optional', 
            'OPENAI_API_KEY': 'optional',
            'GOOGLE_API_KEY': 'optional',
            'GOOGLE_MAPS_API_KEY': 'optional',  # For geographic validation
            'WEBDRIVER_PATH': 'optional',
        }
        
        api_keys_found = 0
        for var, required in env_vars.items():
            value = os.getenv(var)
            if value:
                if 'API' in var:
                    # Mostrar solo primeros y ultimos 4 caracteres por seguridad
                    masked = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
                    self.checks.append((f"[OK] {var}: {masked}", "ok"))
                    api_keys_found += 1
                else:
                    self.checks.append((f"[OK] {var}: {value}", "ok"))
            elif required == 'required':
                self.errors.append(f"Variable de entorno requerida faltante: {var}")
            else:
                self.warnings.append(f"Variable de entorno opcional no configurada: {var}")
        
        # Verificacion especifica de proveedores LLM
        if not api_keys_found:
            self.warnings.append("No hay claves API configuradas - Solo analisis basico disponible")
    
    def _check_file_permissions(self):
        """Verifica permisos de archivos y directorios"""
        paths_to_check = [
            './output',
            './modules',
            './data',
            './temp'
        ]
        
        for path_str in paths_to_check:
            path = Path(path_str)
            try:
                if path.exists():
                    # Verificar permisos de escritura
                    test_file = path / ".write_test"
                    try:
                        test_file.write_text("test")
                        test_file.unlink()
                        self.checks.append((f"[OK] Permisos: {path_str}", "ok"))
                    except (IOError, OSError):
                        self.errors.append(f"Sin permisos de escritura en: {path_str}")
                else:
                    # Intentar crear directorio
                    try:
                        path.mkdir(parents=True, exist_ok=True)
                        self.checks.append((f"[OK] Directorio creado: {path_str}", "ok"))
                    except (IOError, OSError):
                        self.warnings.append(f"No se pudo crear directorio: {path_str}")
            except Exception as e:
                self.warnings.append(f"Error verificando {path_str}: {str(e)}")
    
    def _check_output_directory(self, args):
        """Verifica directorio de salida especifico"""
        if args and hasattr(args, 'output'):
            output_path = Path(args.output)
            try:
                output_path.mkdir(parents=True, exist_ok=True)
                # Test de escritura
                test_file = output_path / "write_test.txt"
                test_file.write_text("test")
                test_file.unlink()
                self.checks.append((f"[OK] Directorio salida: {args.output}", "ok"))
            except Exception as e:
                self.errors.append(f"Directorio de salida no accesible: {args.output} - {str(e)}")
    
    def _check_api_connectivity(self):
        """Verifica conectividad basica a APIs externas"""
        import requests
        import urllib.parse
        
        accepted_status = {200, 201, 202, 204, 400, 401, 403, 404, 405}
        endpoints = [
            {
                "name": "DeepSeek",
                "url": "https://api.deepseek.com/v1/chat/completions",
                "env": "DEEPSEEK_API_KEY",
                "headers": lambda key: {"Authorization": f"Bearer {key}"},
            },
            {
                "name": "Anthropic",
                "url": "https://api.anthropic.com/v1/messages",
                "env": "ANTHROPIC_API_KEY",
                "headers": lambda key: {"x-api-key": key},
            },
        ]
        
        for endpoint in endpoints:
            headers = {}
            api_key = os.getenv(endpoint["env"], "")
            if api_key:
                headers = endpoint["headers"](api_key)
            try:
                response = requests.head(endpoint["url"], headers=headers, timeout=5)
                status_ok = response.status_code in accepted_status
                if response.status_code == 405:  # algunos endpoints no aceptan HEAD
                    response = requests.get(endpoint["url"], headers=headers, timeout=5)
                    status_ok = response.status_code in accepted_status
                if status_ok:
                    host = urllib.parse.urlparse(endpoint["url"]).netloc
                    self.checks.append((f"[OK] Conectividad: {host}", "ok"))
                else:
                    self.warnings.append(
                        f"Conectividad limitada a: {endpoint['url']} (HTTP {response.status_code})"
                    )
            except requests.RequestException as exc:
                self.warnings.append(
                    f"No se pudo conectar a: {endpoint['url']} ({exc.__class__.__name__})"
                )
    
    def _check_deepseek_specifics(self):
        """Verificaciones especificas de DeepSeek"""
        deepseek_checks = []
        
        # Verificar que DeepSeek este disponible como opcion
        try:
            from modules.providers.llm_provider import ProviderAdapter
            adapter = ProviderAdapter()
            
            # Verificar que puede cambiar a DeepSeek
            try:
                adapter.switch_provider("deepseek")
                current = adapter.get_current_provider()
                deepseek_checks.append(("[OK] DeepSeek provider funcional", "ok"))
                
                # Verificar que tiene API key configurada
                if os.getenv('DEEPSEEK_API_KEY'):
                    if hasattr(adapter, 'provider') and hasattr(adapter.provider, 'chat_completion'):
                        deepseek_checks.append(("[OK] DeepSeek configurado correctamente", "ok"))
                    else:
                        self.warnings.append("DeepSeek configurado pero provider sin interfaz chat_completion")
                else:
                    self.warnings.append("DeepSeek seleccionable pero sin API_KEY")
                    
            except Exception as e:
                self.errors.append(f"No se puede cambiar a DeepSeek: {e}")
                
        except Exception as e:
            self.errors.append(f"Error en ProviderAdapter: {e}")
        
        return deepseek_checks

    def _check_migration_readiness(self):
        """Verificar que los modulos migrados funcionan"""
        migration_checks = []
        
        try:
            from modules.analyzers.gap_analyzer import GapAnalyzer
            analyzer = GapAnalyzer()
            if hasattr(analyzer, "analyze_with_llm"):
                migration_checks.append(("[OK] GapAnalyzer migrado", "ok"))
            else:
                self.errors.append("GapAnalyzer no tiene metodo analyze_with_llm")
        except Exception as e:
            self.errors.append(f"Error en GapAnalyzer migrado: {e}")
        
        try:
            from modules.analyzers.ia_tester import IATester
            tester = IATester()
            if hasattr(tester, "_test_llm_simulation"):
                migration_checks.append(("[OK] IATester migrado", "ok"))
            else:
                self.warnings.append("IATester no tiene simulacion LLM")
        except Exception as e:
            self.warnings.append(f"Advertencia en IATester: {e}")
        
        return migration_checks

    def _check_geographic_validation_config(self):
        """Verifica configuración de validación geográfica"""
        geo_checks = []
        
        # Check if Google Maps API key is available for geographic validation
        google_maps_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if google_maps_key:
            geo_checks.append(("Google Maps API Key disponible", "ok"))
            # Basic format validation
            if len(google_maps_key) >= 20:  # Google API keys are typically long
                geo_checks.append(("Google Maps API Key formato válido", "ok"))
            else:
                self.warnings.append("Google Maps API Key parece demasiado corta")
        else:
            self.warnings.append("Google Maps API Key no encontrada - Validación geográfica deshabilitada")
        
        # Check geographic validation settings
        geo_validation_enabled = os.getenv('GBP_GEOGRAPHIC_VALIDATION_ENABLED', 'true').lower()
        if geo_validation_enabled in ['true', 'false']:
            geo_checks.append(("GBP_GEOGRAPHIC_VALIDATION_ENABLED configurado", "ok"))
        else:
            self.warnings.append("GBP_GEOGRAPHIC_VALIDATION_ENABLED tiene valor inválido (debe ser true/false)")
        
        # Check validation threshold
        try:
            threshold = float(os.getenv('GBP_VALIDATION_THRESHOLD_KM', '30'))
            if 1 <= threshold <= 200:  # Reasonable range
                geo_checks.append((f"Umbral de validación geográfica: {threshold}km", "ok"))
            else:
                self.warnings.append(f"Umbral de validación geográfico fuera de rango: {threshold}km (recomendado: 1-200km)")
        except ValueError:
            self.warnings.append("GBP_VALIDATION_THRESHOLD_KM no es un número válido")
        
        # Check if required dependencies are installed
        try:
            import googlemaps
            geo_checks.append(("googlemaps dependency instalada", "ok"))
        except ImportError:
            self.errors.append("googlemaps dependency no instalada - Ejecutar: pip install googlemaps>=4.10.0")
        
        try:
            import geopy
            geo_checks.append(("geopy dependency instalada", "ok"))
        except ImportError:
            self.errors.append("geopy dependency no instalada - Ejecutar: pip install geopy>=2.4.0")
        
        # Test geographic validator initialization
        try:
            from modules.utils.geo_validator import get_geo_validator
            validator = get_geo_validator()
            if validator.is_available():
                geo_checks.append(("GeoValidator inicializado correctamente", "ok"))
            else:
                self.warnings.append("GeoValidator no disponible - Requiere Google Maps API Key")
        except Exception as e:
            self.warnings.append(f"Error al inicializar GeoValidator: {e}")
        
        return geo_checks

    def _generate_report(self):
        """Genera reporte final"""
        print("\n" + "="*50)
        print("REPORTE DE CONFIGURACION")
        print("="*50)
        
        # Mostrar checks exitosos
        for check, status in self.checks:
            if status == "ok":
                print(f"  {check}")
        
        # Mostrar advertencias
        if self.warnings:
            print(f"\n[WARN]  ADVERTENCIAS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  -  {warning}")
        
        # Mostrar errores
        if self.errors:
            print(f"\n[FAIL] ERRORES CRITICOS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  -  {error}")
            return False
        
        # Resumen
        total_checks = len(self.checks) + len(self.warnings) + len(self.errors)
        print(f"\n[CHART] RESUMEN: {len(self.checks)} OK, {len(self.warnings)} advertencias, {len(self.errors)} errores")
        
        if not self.errors and not self.warnings:
            print("[CELEBRATE] Configuracion optima - Listo para ejecutar!")
            return True
        elif not self.errors:
            print("[WARN]  Configuracion aceptable - Puede continuar")
            return True
        else:
            print("[FAIL] Problemas de configuracion - Corrija los errores antes de continuar")
            return False

def main():
    """Funcion principal para ejecutar verificacion independiente"""
    import argparse
    parser = argparse.ArgumentParser(description='Verificador de configuracion')
    parser.add_argument('--output', default='./output', help='Directorio de salida a verificar')
    args = parser.parse_args()
    
    checker = ConfigChecker()
    success = checker.check(args)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()