"""
HTTP Client con Fallback SSL Inteligente

Cliente HTTP centralizado que maneja errores de certificados SSL de forma
resiliente, permitiendo degradación controlada en 3 niveles:
  1. HTTPS con verify=True (seguro, por defecto)
  2. HTTPS con verify=False (SSL bypass, warning logged)
  3. HTTP fallback (último recurso, si allow_http_downgrade=True)

Uso:
    from modules.utils.http_client import HttpClient
    
    client = HttpClient(config)
    response, fallback_info = client.get("https://example.com")
    
    if fallback_info['ssl_bypassed']:
        print(f"Warning: SSL bypassed for {url}")

Autor: IA Hoteles Agent
Fecha: 27 Noviembre 2025
"""

import requests
from requests.exceptions import SSLError, RequestException, Timeout
from typing import Tuple, Dict, Any, Optional
from urllib.parse import urlparse, urlunparse
import warnings


class HttpClient:
    """
    Cliente HTTP resiliente con fallback SSL multinivel.
    
    Attributes:
        timeout: Tiempo máximo de espera por request (segundos)
        verify_ssl: Si True, verifica certificados SSL por defecto
        ssl_fallback_enabled: Si True, permite bypass SSL cuando falla
        allow_http_downgrade: Si True, permite fallback a HTTP como último recurso
        seo_penalty: Puntos a restar del score SEO cuando SSL falla
        logger: Instancia de SSLLogger para registrar eventos
    """
    
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa el cliente HTTP con configuración.
        
        Args:
            config: Diccionario de configuración. Estructura esperada:
                {
                    'timeout': 15,
                    'verify_ssl': True,
                    'ssl_fallback': {
                        'enabled': True,
                        'allow_http_downgrade': False,
                        'log_to_file': True,
                        'seo_penalty': 30
                    }
                }
        """
        config = config or {}
        ssl_config = config.get('ssl_fallback', {})
        
        self.timeout = config.get('timeout', 15)
        self.verify_ssl = config.get('verify_ssl', True)
        self.ssl_fallback_enabled = ssl_config.get('enabled', True)
        self.allow_http_downgrade = ssl_config.get('allow_http_downgrade', False)
        self.seo_penalty = ssl_config.get('seo_penalty', 30)
        self.log_to_file = ssl_config.get('log_to_file', True)
        
        # Logger se inicializa de forma lazy para evitar imports circulares
        self._logger = None
    
    @property
    def logger(self):
        """Lazy initialization del logger."""
        if self._logger is None:
            try:
                from modules.utils.ssl_logger import SSLLogger
                self._logger = SSLLogger(enabled=self.log_to_file)
            except ImportError:
                self._logger = None
        return self._logger
    
    def get(
        self, 
        url: str, 
        headers: Optional[Dict[str, str]] = None,
        allow_redirects: bool = True,
        **kwargs
    ) -> Tuple[Optional[requests.Response], Dict[str, Any]]:
        """
        Realiza GET request con fallback SSL inteligente.
        
        Args:
            url: URL a consultar
            headers: Headers HTTP adicionales
            allow_redirects: Si permite redirecciones
            **kwargs: Argumentos adicionales para requests.get()
        
        Returns:
            Tuple de (Response, fallback_info) donde fallback_info contiene:
                - success: bool - Si la request fue exitosa
                - ssl_bypassed: bool - Si se usó verify=False
                - http_downgraded: bool - Si se degradó a HTTP
                - fallback_chain: list - Cadena de intentos realizados
                - error: str | None - Mensaje de error si falló
                - seo_penalty: int - Penalización a aplicar al score SEO
        """
        merged_headers = {**self.DEFAULT_HEADERS, **(headers or {})}
        
        fallback_info = {
            'success': False,
            'ssl_bypassed': False,
            'http_downgraded': False,
            'fallback_chain': [],
            'error': None,
            'seo_penalty': 0,
            'original_url': url,
            'final_url': url
        }
        
        # Nivel 1: HTTPS con verificación SSL
        response, error = self._try_request(
            url, 
            verify=True, 
            headers=merged_headers, 
            allow_redirects=allow_redirects,
            **kwargs
        )
        
        if response is not None:
            fallback_info['success'] = True
            fallback_info['fallback_chain'].append('https_verified')
            return response, fallback_info
        
        fallback_info['fallback_chain'].append(f'https_verified_failed:{self._sanitize_error(error)}')
        
        # Verificar si es error SSL
        is_ssl_error = self._is_ssl_error(error)
        
        if not is_ssl_error:
            # Error no relacionado con SSL, no intentar fallback
            fallback_info['error'] = str(error)
            return None, fallback_info
        
        # Nivel 2: HTTPS sin verificación SSL (si habilitado)
        if self.ssl_fallback_enabled:
            self._log_ssl_bypass(url, str(error))
            
            response, error2 = self._try_request(
                url,
                verify=False,
                headers=merged_headers,
                allow_redirects=allow_redirects,
                **kwargs
            )
            
            if response is not None:
                fallback_info['success'] = True
                fallback_info['ssl_bypassed'] = True
                fallback_info['seo_penalty'] = self.seo_penalty
                fallback_info['fallback_chain'].append('https_unverified')
                return response, fallback_info
            
            fallback_info['fallback_chain'].append(f'https_unverified_failed:{self._sanitize_error(error2)}')
        
        # Nivel 3: HTTP fallback (si habilitado)
        if self.allow_http_downgrade:
            http_url = self._downgrade_to_http(url)
            self._log_http_downgrade(url, http_url)
            
            response, error3 = self._try_request(
                http_url,
                verify=False,  # HTTP no usa SSL
                headers=merged_headers,
                allow_redirects=allow_redirects,
                **kwargs
            )
            
            if response is not None:
                fallback_info['success'] = True
                fallback_info['ssl_bypassed'] = True
                fallback_info['http_downgraded'] = True
                fallback_info['seo_penalty'] = self.seo_penalty
                fallback_info['final_url'] = http_url
                fallback_info['fallback_chain'].append('http_fallback')
                return response, fallback_info
            
            fallback_info['fallback_chain'].append(f'http_fallback_failed:{self._sanitize_error(error3)}')
        
        # Todos los intentos fallaron
        fallback_info['error'] = str(error)
        return None, fallback_info
    
    def _try_request(
        self, 
        url: str, 
        verify: bool,
        headers: Dict[str, str],
        allow_redirects: bool,
        **kwargs
    ) -> Tuple[Optional[requests.Response], Optional[Exception]]:
        """
        Intenta realizar request HTTP.
        
        Returns:
            Tuple de (Response, Error) - uno será None
        """
        try:
            # Suprimir warnings de SSL cuando verify=False
            if not verify:
                warnings.filterwarnings('ignore', message='Unverified HTTPS request')
            
            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout,
                verify=verify,
                allow_redirects=allow_redirects,
                **kwargs
            )
            response.raise_for_status()
            return response, None
            
        except SSLError as e:
            return None, e
        except Timeout as e:
            return None, e
        except RequestException as e:
            return None, e
        except Exception as e:
            return None, e
    
    def _is_ssl_error(self, error: Optional[Exception]) -> bool:
        """Determina si el error es relacionado con SSL."""
        if error is None:
            return False
        
        error_str = str(error).lower()
        ssl_keywords = [
            'ssl', 
            'certificate', 
            'cert', 
            'handshake',
            'sslcertverificationerror',
            'certificate_verify_failed',
            'certificate has expired'
        ]
        return any(kw in error_str for kw in ssl_keywords)
    
    def _sanitize_error(self, error: Optional[Exception]) -> str:
        """Extrae mensaje de error corto para logging."""
        if error is None:
            return 'unknown'
        error_str = str(error)
        # Truncar errores largos
        if len(error_str) > 100:
            return error_str[:97] + '...'
        return error_str
    
    def _downgrade_to_http(self, url: str) -> str:
        """Convierte URL HTTPS a HTTP."""
        parsed = urlparse(url)
        if parsed.scheme == 'https':
            return urlunparse(parsed._replace(scheme='http'))
        return url
    
    def _log_ssl_bypass(self, url: str, error: str):
        """Registra evento de SSL bypass."""
        message = f"SSL bypass activado para {url}: {error}"
        print(f"[WARN] {message}")
        
        if self.logger:
            self.logger.log_ssl_bypass(url, error)
    
    def _log_http_downgrade(self, original_url: str, http_url: str):
        """Registra evento de downgrade a HTTP."""
        message = f"HTTP downgrade: {original_url} → {http_url}"
        print(f"[WARN] {message}")
        
        if self.logger:
            self.logger.log_http_downgrade(original_url, http_url)


def get_default_client(settings: Optional[Dict] = None) -> HttpClient:
    """
    Factory function para obtener cliente HTTP con configuración de settings.yaml.
    
    Args:
        settings: Diccionario de settings (opcional, se carga de archivo si None)
    
    Returns:
        HttpClient configurado
    """
    if settings is None:
        try:
            import yaml
            with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                settings = yaml.safe_load(f)
        except Exception:
            settings = {}
    
    scraper_config = settings.get('scrapers', {}).get('requests', {})
    return HttpClient(scraper_config)
