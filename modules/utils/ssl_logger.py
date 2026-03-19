"""
SSL Fallback Logger

Logger dedicado para registrar eventos de fallback SSL con rotación automática.
Escribe a logs/ssl_fallback.log con límite de 1MB y 5 archivos históricos.

Uso:
    from modules.utils.ssl_logger import SSLLogger
    
    logger = SSLLogger()
    logger.log_ssl_bypass("https://example.com", "certificate expired")
    logger.log_http_downgrade("https://example.com", "http://example.com")

Autor: IA Hoteles Agent
Fecha: 27 Noviembre 2025
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional


class SSLLogger:
    """
    Logger especializado para eventos de fallback SSL.
    
    Características:
        - Escribe a logs/ssl_fallback.log
        - Rotación automática: 1MB máximo, 5 archivos históricos
        - Formato estructurado con timestamp, tipo de evento y detalles
        - Thread-safe
    """
    
    LOG_DIR = "logs"
    LOG_FILE = "ssl_fallback.log"
    MAX_BYTES = 1 * 1024 * 1024  # 1 MB
    BACKUP_COUNT = 5
    
    def __init__(self, enabled: bool = True):
        """
        Inicializa el logger.
        
        Args:
            enabled: Si False, no escribe a archivo (solo consola)
        """
        self.enabled = enabled
        self._logger = None
        
        if enabled:
            self._setup_logger()
    
    def _setup_logger(self):
        """Configura el logger con RotatingFileHandler."""
        # Crear directorio si no existe
        os.makedirs(self.LOG_DIR, exist_ok=True)
        
        log_path = os.path.join(self.LOG_DIR, self.LOG_FILE)
        
        # Crear logger único
        self._logger = logging.getLogger('ssl_fallback')
        self._logger.setLevel(logging.INFO)
        
        # Evitar handlers duplicados
        if not self._logger.handlers:
            # Handler con rotación
            handler = RotatingFileHandler(
                log_path,
                maxBytes=self.MAX_BYTES,
                backupCount=self.BACKUP_COUNT,
                encoding='utf-8'
            )
            
            # Formato del log
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            
            self._logger.addHandler(handler)
    
    def log_ssl_bypass(self, url: str, error: str):
        """
        Registra un evento de SSL bypass (verify=False).
        
        Args:
            url: URL donde ocurrió el bypass
            error: Mensaje de error SSL original
        """
        if not self.enabled or self._logger is None:
            return
        
        # Sanitizar error para logging
        error_clean = self._sanitize_for_log(error)
        
        message = f"SSL_BYPASS | url={url} | error={error_clean}"
        self._logger.warning(message)
    
    def log_http_downgrade(self, original_url: str, http_url: str):
        """
        Registra un evento de downgrade HTTPS → HTTP.
        
        Args:
            original_url: URL HTTPS original
            http_url: URL HTTP resultante
        """
        if not self.enabled or self._logger is None:
            return
        
        message = f"HTTP_DOWNGRADE | original={original_url} | downgraded={http_url}"
        self._logger.warning(message)
    
    def log_ssl_success(self, url: str):
        """
        Registra acceso exitoso con SSL verificado (para métricas).
        
        Args:
            url: URL accedida exitosamente
        """
        if not self.enabled or self._logger is None:
            return
        
        message = f"SSL_SUCCESS | url={url}"
        self._logger.info(message)
    
    def log_complete_failure(self, url: str, attempts: list, final_error: str):
        """
        Registra fallo completo después de todos los intentos.
        
        Args:
            url: URL que no pudo ser accedida
            attempts: Lista de intentos realizados
            final_error: Error final
        """
        if not self.enabled or self._logger is None:
            return
        
        attempts_str = " -> ".join(attempts)
        error_clean = self._sanitize_for_log(final_error)
        
        message = f"COMPLETE_FAILURE | url={url} | attempts={attempts_str} | error={error_clean}"
        self._logger.error(message)
    
    def _sanitize_for_log(self, text: str) -> str:
        """
        Sanitiza texto para logging.
        
        Remueve caracteres problemáticos y trunca si es necesario.
        """
        if not text:
            return "unknown"
        
        # Remover saltos de línea
        text = text.replace('\n', ' ').replace('\r', '')
        
        # Truncar si es muy largo
        max_len = 200
        if len(text) > max_len:
            text = text[:max_len-3] + '...'
        
        return text
    
    def get_stats(self) -> dict:
        """
        Obtiene estadísticas del log actual.
        
        Returns:
            Dict con contadores de cada tipo de evento
        """
        log_path = os.path.join(self.LOG_DIR, self.LOG_FILE)
        
        stats = {
            'ssl_bypass_count': 0,
            'http_downgrade_count': 0,
            'ssl_success_count': 0,
            'complete_failure_count': 0,
            'log_size_bytes': 0,
            'log_exists': False
        }
        
        if not os.path.exists(log_path):
            return stats
        
        stats['log_exists'] = True
        stats['log_size_bytes'] = os.path.getsize(log_path)
        
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if 'SSL_BYPASS' in line:
                        stats['ssl_bypass_count'] += 1
                    elif 'HTTP_DOWNGRADE' in line:
                        stats['http_downgrade_count'] += 1
                    elif 'SSL_SUCCESS' in line:
                        stats['ssl_success_count'] += 1
                    elif 'COMPLETE_FAILURE' in line:
                        stats['complete_failure_count'] += 1
        except Exception:
            pass
        
        return stats


# Singleton para uso global
_global_logger: Optional[SSLLogger] = None


def get_ssl_logger(enabled: bool = True) -> SSLLogger:
    """
    Obtiene instancia singleton del SSLLogger.
    
    Args:
        enabled: Si habilitar logging a archivo
    
    Returns:
        Instancia de SSLLogger
    """
    global _global_logger
    
    if _global_logger is None:
        _global_logger = SSLLogger(enabled=enabled)
    
    return _global_logger
