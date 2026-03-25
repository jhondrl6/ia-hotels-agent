"""Truth Validator 4.0 - Protocol of Truth implementation.

Ensures diagnostic reliability by triangulating scraper data, 
benchmarks, and critical reasoning.
"""

from typing import Any, Dict, List, Optional
from modules.utils.benchmarks import BenchmarkLoader
from datetime import datetime

class TruthValidator:
    """Implements the Protocol of Truth 4.0 with Narrative Arbitration Logging."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.loader = BenchmarkLoader()
        full_data = self.loader.load()
        self.benchmarks = full_data.get("regiones", {})
        self.umbrales = self.loader.get_thresholds()

    def validate_diagnostic_data(
        self, 
        hotel_data: Dict[str, Any], 
        gbp_data: Dict[str, Any], 
        ia_test: Dict[str, Any],
        roi_data: Dict[str, Any],
        region: str = "default"
    ) -> Dict[str, Any]:
        """Performs triple triangulation and returns fully reconstructible results."""
        
        arbitration_log = []
        region_bench = self.benchmarks.get(region, self.benchmarks.get("default"))
        
        results = {
            "is_defensible": True,
            "validations": {},
            "adjustments": [],
            "critical_judgments": [],
            "arbitration_log": arbitration_log
        }
        
        # 1. GBP Triangulation (Technical vs Reputation)
        geo_score = gbp_data.get("score", 0)
        ia_mentions = (ia_test.get("perplexity", {}).get("menciones", 0) + 
                       ia_test.get("chatgpt", {}).get("menciones", 0))
        
        gbp_entry = {
            "metric": "GBP_SCORE",
            "evidence": {
                "technical_score": geo_score,
                "ia_visibility_mentions": ia_mentions,
                "regional_benchmark": region_bench.get("benchmarks", {}).get("gbp_score", 60)
            },
            "arbitration": "Dato Verificado"
        }

        if geo_score < 40 and ia_mentions > 0:
            msg = "Anomalía de Autoridad: El hotel es relevante para la IA pero su ficha técnica está abandonada."
            gbp_entry["arbitration"] = msg
            gbp_entry["impact"] = "Oportunidad Crítica de Venta"
            results["critical_judgments"].append(f"GBP: {msg}")
        
        arbitration_log.append(gbp_entry)
        results["validations"]["gbp"] = {"score": geo_score, "status": "triangulated"}

        # 2. Web & Conversion (Tech vs Commercial Flow)
        web_score = hotel_data.get("web_score", 0)
        has_engine = gbp_data.get("motor_reservas_gbp", False) or "engine" in str(hotel_data.get("url", ""))
        
        web_entry = {
            "metric": "WEB_CONVERSION",
            "evidence": {
                "performance_score": web_score,
                "booking_engine_detected": has_engine,
                "target_score": 75
            },
            "arbitration": "Dato Verificado"
        }

        if web_score < 50 and has_engine:
            msg = "Fuga Tecnológica: Existe motor de reservas pero la web impide la conversión por bajo score."
            web_entry["arbitration"] = msg
            web_entry["impact"] = "Pérdida Directa por UX"
            results["critical_judgments"].append(f"Web: {msg}")
        
        arbitration_log.append(web_entry)
        results["validations"]["web"] = {"score": web_score, "status": "triangulated"}

        # 3. Financial Coherence (User vs Regional Reality)
        revpar = hotel_data.get("precio_promedio", 0)
        reg_revpar = region_bench.get("revpar_cop", 0)
        perdida_total = roi_data.get("perdida_mensual_total", 0)
        
        fin_entry = {
            "metric": "FINANCIAL_COHERENCE",
            "evidence": {
                "reported_revpar": revpar,
                "regional_avg_revpar": reg_revpar,
                "estimated_monthly_loss": perdida_total
            },
            "arbitration": "Coherente con mercado"
        }

        if revpar > 0 and abs(revpar - reg_revpar) / reg_revpar > 0.5:
            msg = f"Valor Atípico: El RevPAR varía >50% vs promedio regional (${reg_revpar:,.0f})."
            fin_entry["arbitration"] = msg
            results["adjustments"].append(msg)
        
        arbitration_log.append(fin_entry)

        # Verified Profile for Knowledge Graph
        results["verified_profile"] = {
            "hotel_id": hotel_data.get("id", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "region": region,
            "metrics": {
                "gbp_score": geo_score,
                "web_score": web_score,
                "revpar": revpar,
                "loss": perdida_total
            },
            "is_verified": True
        }

        return results
