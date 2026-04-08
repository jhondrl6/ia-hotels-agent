"""Benchmarks loader for Plan Maestro v2.4.2.

Loads deterministic thresholds and packages from `data/benchmarks/plan_maestro_data.json`.
Falls back to in-memory defaults if the file is missing. Keep ASCII for portability.

Note: The JSON puede incluir metadatos `plan_versions` (p.ej. decision_core_v24,
delivery_remote_v25). Los getters nuevos exponen esa info sin alterar el contrato
existente.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict


DATA_PATH = Path(__file__).parent.parent.parent / "data" / "benchmarks" / "plan_maestro_data.json"


DEFAULT_DATA: Dict[str, Any] = {
    "version": "v2.5.0",
    "regiones": {
        "default": {
            "revpar_cop": 197120,
            "habitaciones_promedio": 15,
            "factor_captura_aila": 0.70,
            "comision_ota_base": 0.15,
            "penalizacion_invisibilidad_ia": 0.05,
            "factor_perdida_base": 0.06,
            "factor_captura_fuente": "Indice AILA Colombia (estimado)",
            "riesgo_ocupacion": "medio",
            "benchmarks": {"gbp_score": 48, "schema_score": 38},
        }
    },
    "paquetes_servicios_v23": {
        "Starter GEO": {
            "precio_cop": 1_800_000,
            "roi_target": 3.0,
            "componentes_cliente": [
                "Ficha de Google optimizada y visible",
                "Presencia en 5 mapas y guias locales",
                "3 publicaciones al mes",
                "5 preguntas y respuestas clave del hotel",
            ],
        },
        "Pro AEO": {
            "precio_cop": 3_800_000,
            "roi_target": 4.0,
            "componentes_cliente": [
                "Datos del hotel claros para que la IA lo recomiende",
                "50 preguntas frecuentes listas para publicar",
                "10 guias/articulos que los asistentes pueden citar",
            ],
        },
        "Pro AEO Plus": {
            "precio_cop": 4_800_000,
            "roi_target": 5.2,
            "componentes_cliente": [
                "Todo lo de Pro AEO (para atraer consultas)",
                "Boton de WhatsApp directo (1 clic) con medicion de clics y contactos",
                "1 ajuste critico en la web para facilitar la reserva o el contacto",
                "Guia y plantillas para responder resenas y convertir dudas en reservas",
                "1 articulo al mes enfocado en viajeros que ya quieren reservar",
            ],
            "disclaimers_cliente": ["no_software"],
            "requiere_cambio_web": True,
            "implementacion_sin_it": {
                "guia_simplificada": True,
                "kit_freelancer": True,
                "proveedores_estimado_cop": {"min": 200_000, "max": 500_000},
            },
        },
        "Elite": {
            "precio_cop": 7_500_000,
            "roi_target": 5.0,
            "componentes_cliente": [
                "Todo lo de Pro AEO Plus",
                "Datos del hotel conectados para respuestas consistentes",
                "Entrenamiento de 3 agentes IA con contenido del hotel",
            ],
        },
        "Elite PLUS": {
            "precio_cop": 9_800_000,
            "roi_target": 6.0,
            "componentes_cliente": [
                "Todo lo de Elite",
                "Panel de monitoreo semanal de 10 consultas en IA",
                "Certificados de Reserva Directa y Web Optimizada",
                "Kit fisico opcional",
            ],
        },
    },
    "umbrales_decision": {
        "impacto_catastrofico": 8_000_000,
        "brecha_conversion_critica": 3_000_000,
        "revpar_premium": 250_000,
        "web_score_alto": 75,
        "gbp_score_bajo": 60,
        "factor_gbp_punto": 50_000,
    },
    "kpis_objetivo_v23": {
        "cac_maximo_cop": 800_000,
        "roas_minimo_aceptable": 2.0,
        "roas_objetivo_6m": 6.0,
        "tasa_renovacion_objetivo": 0.80,
        "tasa_precision_diagnostico": 0.90,
    },
    "actividad_gbp_pesos": {
        "posts_90d_peso": 0.35,
        "posts_90d_max": 5,
        "fotos_mes_peso": 0.25,
        "fotos_mes_max": 10,
        "fotos_meta": 15,
        "reviews_response_peso": 0.40,
    },
    "terminologia_cliente": {
        "GBP": "ficha de Google",
        "UTM": "medicion de clics",
        "Schema": "informacion clara del hotel",
        "HTTPS": "web segura (con candado)",
        "CTA": "boton principal",
    },
    "disclaimers_cliente": {
        "no_software": "No desarrollamos software; optimizamos el flujo y recomendamos proveedor si se requiere motor de reservas.",
    },
    "certificados": {
        "allowed_packages": ["Elite PLUS"],
        "items": ["Certificado Reserva Directa", "Certificado Web Optimizada"],
    },
    "addons_v242": {
        "GBP Activation": {
            "precio_cop": 800_000,
            "roi_target": 2.5,
            "componentes": [
                "4 posts/mes",
                "10 fotos nuevas",
                "Protocolo respuesta reviews",
            ],
            "condicion": "gbp_score >= 60 AND gbp_activity_score < 30",
        },
        "Implementacion Tecnica": {
            "precio_cop": 500_000,
            "roi_target": 1.5,
            "componentes": [
                "Coordinación con proveedor web",
                "Instalación schema.json",
                "Implementación botón wa.me",
                "Validación post-implementación",
            ],
            "condicion": "has_it_capacity == false AND paquete in ['Pro AEO', 'Pro AEO Plus', 'Elite']",
        }
    },
}


class BenchmarkLoader:
    def __init__(self, data_path: Path = DATA_PATH) -> None:
        self.data_path = data_path

    @lru_cache(maxsize=1)
    def load(self) -> Dict[str, Any]:
        if self.data_path.exists():
            try:
                with open(self.data_path, "r", encoding="utf-8") as handle:
                    return json.load(handle)
            except Exception:
                # Fall through to defaults on parse errors
                pass
        return DEFAULT_DATA

    def get_regional_data(self, region: str) -> Dict[str, Any]:
        data = self.load()
        regiones = data.get("regiones", {})
        region_key = (region or "default").lower().replace(" ", "_")
        return regiones.get(region_key, regiones.get("default", DEFAULT_DATA["regiones"]["default"]))

    # --------------------------------------------------
    # Plan versions metadata (no-op for legacy callers)
    # --------------------------------------------------
    def get_plan_versions(self) -> Dict[str, Any]:
        data = self.load()
        return data.get("plan_versions", {})

    def get_decision_plan_meta(self) -> Dict[str, Any]:
        plan_versions = self.get_plan_versions()
        return plan_versions.get("decision_core_v24", {})

    def get_delivery_plan_meta(self) -> Dict[str, Any]:
        plan_versions = self.get_plan_versions()
        return plan_versions.get("delivery_remote_v25", {})

    def get_packages(self) -> Dict[str, Any]:
        data = self.load()
        return data.get("paquetes_servicios_v23", DEFAULT_DATA["paquetes_servicios_v23"])

    def get_thresholds(self) -> Dict[str, Any]:
        data = self.load()
        return data.get("umbrales_decision", DEFAULT_DATA["umbrales_decision"])

    def get_activity_weights(self) -> Dict[str, Any]:
        data = self.load()
        return data.get("actividad_gbp_pesos", DEFAULT_DATA.get("actividad_gbp_pesos", {}))

    def get_addons(self) -> Dict[str, Any]:
        data = self.load()
        return data.get("addons_v242", DEFAULT_DATA.get("addons_v242", {}))

    def get_kpis(self) -> Dict[str, Any]:
        data = self.load()
        return data.get("kpis_objetivo_v23", DEFAULT_DATA["kpis_objetivo_v23"])

    def get_client_terminology(self) -> Dict[str, str]:
        data = self.load()
        return data.get("terminologia_cliente", DEFAULT_DATA.get("terminologia_cliente", {}))

    def get_client_disclaimers(self) -> Dict[str, str]:
        data = self.load()
        return data.get("disclaimers_cliente", DEFAULT_DATA.get("disclaimers_cliente", {}))

    def get_certificates_config(self) -> Dict[str, Any]:
        data = self.load()
        return data.get("certificados", DEFAULT_DATA.get("certificados", {}))

    # --------------------------------------------------
    # Owner-facing bundles (regional)
    # --------------------------------------------------
    def _region_key(self, region: str) -> str:
        return (region or "default").strip().lower().replace(" ", "_")

    def _get_regional_list(self, pkg: Dict[str, Any], field: str, region: str) -> Any:
        regional = pkg.get(f"{field}_por_region", {}) or {}
        key = self._region_key(region)
        return regional.get(key) or regional.get("default", [])

    def get_owner_bundle(self, package_name: str, region: str) -> Dict[str, Any]:
        """Devuelve bloques owner-friendly (plan/KPIs/dependencias/etc.) por región con fallback seguro."""

        packages = self.get_packages()
        pkg = packages.get(package_name, {}) or {}

        return {
            "plan_7_30_60_90": self._get_regional_list(pkg, "plan_7_30_60_90", region),
            "kpis_cliente": self._get_regional_list(pkg, "kpis_cliente", region),
            "dependencias_cliente": self._get_regional_list(pkg, "dependencias_cliente", region),
            "cadencia_mensual": self._get_regional_list(pkg, "cadencia_mensual", region),
            "triggers_upgrade": self._get_regional_list(pkg, "triggers_upgrade", region),
            "playbook_cierre": self._get_regional_list(pkg, "playbook_cierre", region),
        }
