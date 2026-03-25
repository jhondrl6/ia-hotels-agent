
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

class GraphManager:
    def __init__(self, base_path: str = "data/knowledge/hotels"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_path(self, hotel_slug: str) -> Path:
        return self.base_path / f"{hotel_slug}.json"

    def save_snapshot(self, hotel_slug: str, metrics: Dict[str, Any]):
        """Guarda un snapshot del estado actual del hotel para tracking histórico."""
        path = self._get_path(hotel_slug)
        data = {"hotel_id": hotel_slug, "timeline": [], "delta": {}}
        
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass
        
        snapshot = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat(),
            "gbp_score": metrics.get("gbp_score"),
            "web_score": metrics.get("web_score"),
            "ia_mentions": metrics.get("ia_mentions"),
            "perdida_mensual": metrics.get("perdida_mensual"),
            "paquete": metrics.get("paquete")
        }
        
        # Evitar duplicados exactos el mismo día si se desea, o simplemente añadir
        data["timeline"].append(snapshot)
        
        # Cálculo de deltas si hay al menos 2 puntos
        if len(data["timeline"]) >= 2:
            prev = data["timeline"][-2]
            curr = data["timeline"][-1]
            
            data["delta"] = {
                "gbp_change": (curr["gbp_score"] or 0) - (prev["gbp_score"] or 0),
                "web_change": (curr["web_score"] or 0) - (prev["web_score"] or 0),
                "last_check": curr["date"]
            }
                
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    def get_history(self, hotel_slug: str) -> Dict[str, Any]:
        """Obtiene la historia completa de un hotel."""
        path = self._get_path(hotel_slug)
        if not path.exists():
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def get_evolution_narrative(self, hotel_slug: str) -> str:
        """Genera una breve narrativa de la evolución para el LLM."""
        history = self.get_history(hotel_slug)
        timeline = history.get("timeline", [])
        if len(timeline) < 2:
            return "Primer análisis registrado para este hotel."
        
        delta = history.get("delta", {})
        gbp_change = delta.get("gbp_change", 0)
        web_change = delta.get("web_change", 0)
        
        msg = f"Evolución detectada: GBP {'mejoró' if gbp_change >= 0 else 'cayó'} {abs(gbp_change)} pts"
        msg += f", Web {'mejoró' if web_change >= 0 else 'cayó'} {abs(web_change)} pts."
        return msg
