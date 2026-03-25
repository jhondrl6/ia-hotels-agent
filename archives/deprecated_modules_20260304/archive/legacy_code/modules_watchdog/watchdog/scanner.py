
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from modules.scrapers.gbp_auditor import GBPAuditor
from modules.scrapers.scraper_fallback import ScraperFallback
from modules.knowledge.graph_manager import GraphManager

class WatchdogScanner:
    def __init__(self):
        self.graph = GraphManager()
        self.fallback = ScraperFallback()

    def scan_lite(self, hotel_name: str, location: str, url: str) -> Dict[str, Any]:
        """Ejecuta una auditoría rápida (sin IA costosa) para monitoreo."""
        print(f"[Watchdog] Iniciando escaneo ligero para {hotel_name}...")
        
        # 1. Auditoría GBP (Pilar 1)
        auditor = GBPAuditor()
        gbp_data = auditor.check_google_profile(hotel_name, location)
        
        # 2. Verificación Web básica (Pilar 2)
        # Solo verificamos si el sitio carga y SSL
        web_status = "ok"
        try:
            import requests
            resp = requests.get(url, timeout=15)
            if not resp.ok: web_status = "error_loading"
            if not url.startswith("https://"): web_status = "no_ssl"
        except Exception:
            web_status = "down"

        metrics = {
            "gbp_score": gbp_data.get("score", 0),
            "web_status": web_status,
            "timestamp": time.time()
        }
        
        return metrics

    def check_for_alerts(self, hotel_slug: str, current_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compara métricas actuales con el historial y genera alertas si hay caídas."""
        history = self.graph.get_history(hotel_slug)
        timeline = history.get("timeline", [])
        if not timeline:
            return []

        last_snapshot = timeline[-1]
        alerts = []

        # Alerta por caída de GBP Score
        last_gbp = last_snapshot.get("gbp_score", 0)
        curr_gbp = current_metrics.get("gbp_score", 0)
        if curr_gbp < last_gbp - 5:
            alerts.append({
                "type": "gbp_drop",
                "severity": "high",
                "msg": f"Caída detectada en Google Business Profile: {last_gbp} -> {curr_gbp}"
            })

        # Alerta por estado web
        if current_metrics.get("web_status") in ["down", "error_loading"]:
            alerts.append({
                "type": "web_down",
                "severity": "critical",
                "msg": f"El sitio web parece estar fuera de línea o con errores: {current_metrics.get('web_status')}"
            })

        return alerts
