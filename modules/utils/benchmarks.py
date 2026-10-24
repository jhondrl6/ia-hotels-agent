"""Benchmarks loader for Plan Maestro v2.4.2.

Loads deterministic thresholds and packages from `data/benchmarks/plan_maestro_data.json`.
Falls back to in-memory defaults if the file is missing. Keep ASCII for portability.

Note: The JSON puede incluir metadatos `plan_versions` (p.ej. decision_core_v24,
delivery_remote_v25). Los getters nuevos exponen esa info sin alterar el contrato
existente.

Maestros declarados (decision DA-PLAN-8a, FASE-E del plan
CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22)
------------------------------------------------------------------
Este modulo es el UNICO lector de `plan_maestro_data.json`. Las claves regionales
viven bajo `v25_config.regiones` (y tambien se aceptan en el nivel superior, por
compatibilidad), con un vocabulario distinto al de `DEFAULT_DATA`: el JSON publica
`precio_promedio`/`ocupacion` y `DEFAULT_DATA` usaba `revpar_cop`. `regiones()` hace
el puente: superpone los valores publicados sobre las claves que este modulo declara
maestro y deriva `revpar_cop = precio_promedio x ocupacion`, que es la semantica del
master `data/benchmarks/regional_adr_2026.json`.

Los demas bloques de `DEFAULT_DATA` no tienen dato publicado que leer: el JSON no los
contiene en ningun nodo. No son un fallback silencioso, son bloques cuyo maestro es
este modulo, y esa condicion esta declarada en `BLOQUES_MAESTRO_DECLARADO`. La
frontera es verificable: `auditoria_maestros()` lista todo bloque o clave de region
que no este en ninguna de las dos poblaciones, y `assert_coherencia_maestros()`
corta. Anadir un bloque nuevo sin declararlo vuelve rojo el contrato, no verde.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List


DATA_PATH = Path(__file__).parent.parent.parent / "data" / "benchmarks" / "plan_maestro_data.json"


# --- Poblaciones del contrato de maestros (DA-PLAN-8a) -----------------------
# Bloques cuyo dato vive en el JSON publicado y este modulo lo lee.
BLOQUES_LEIDOS_DEL_JSON = frozenset({"regiones"})

# Bloques sin ningun nodo publicado en el JSON: este modulo es su unico maestro.
# Son los cinco que nombro el plan (01-plan-maestro.md §5).
BLOQUES_MAESTRO_DECLARADO = frozenset({
    "actividad_gbp_pesos",
    "kpis_objetivo_v23",
    "terminologia_cliente",
    "disclaimers_cliente",
    "certificados",
})

# Bloques que SI tienen un nodo publicado bajo `v25_config`, con un vocabulario
# distinto y valores divergentes (medido en FASE-E, ver `10-analisis` DA-PLAN-8a):
# el contrato del producto es el de este modulo y la copia publicada no se lee.
# Declararla es lo que impide que el fallback parezca un descuido.
BLOQUES_MAESTRO_CON_FORQUE_PUBLICADO = frozenset({
    "paquetes_servicios_v23",
    "umbrales_decision",
    "addons_v242",
})

# `version` no es un bloque de datos: es la etiqueta que se lee del JSON.
BLOQUES_NO_GOBERNADOS = frozenset({"version"})

# Claves de region que aporta el JSON publicado.
CLAVES_REGION_PUBLICADAS = frozenset({
    "precio_promedio",
    "ocupacion",
    "habitaciones_promedio",
    "geo_score_ref",
    "aeo_score_ref",
    "seo_score_ref",
    "iao_score_ref",
    "adr_sync_note",
})

# Clave de region que no se publica ni se conserva: se calcula del maestro.
CLAVE_REGION_DERIVADA = "revpar_cop"

# Claves de region que son invariables por region y cuyo maestro es este modulo.
# `comision_ota_base` y `penalizacion_invisibilidad_ia` coinciden con el valor que
# el JSON ya publica en `v25_config.thresholds`, asi que no abren segunda varilla.
CLAVES_REGION_MAESTRO_DECLARADO = frozenset({
    "factor_captura_aila",
    "factor_perdida_base",
    "factor_captura_fuente",
    "riesgo_ocupacion",
    "benchmarks",
    "comision_ota_base",
    "penalizacion_invisibilidad_ia",
})

DEFAULT_DATA: Dict[str, Any] = {
    "version": "v2.5.0",
    "regiones": {
        "default": {
            "revpar_cop": 197120,
            "habitaciones_promedio": 15,
            "factor_captura_aila": 0.70,
            "comision_ota_base": 0.20,  # FIX F5: default 0.20 from config/financial_defaults.yaml
            "penalizacion_invisibilidad_ia": 0.05,
            "factor_perdida_base": 0.06,
            "factor_captura_fuente": "Indice AILA Colombia (estimado)",
            "riesgo_ocupacion": "medio",
            "benchmarks": {"gbp_score": 48, "schema_score": 38},
            "geo_score_ref": 85,
            "aeo_score_ref": 40,
            "seo_score_ref": 59,
            "iao_score_ref": 15,
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
        """Devuelve el JSON tal cual: no le inyecta claves normalizadas.

        `regiones` se lee por `regiones()`, no por aqui, para que la forma cruda del
        artefacto siga siendo inspeccionable por quien audita el archivo.
        """
        if self.data_path.exists():
            try:
                with open(self.data_path, "r", encoding="utf-8") as handle:
                    return json.load(handle)
            except Exception:
                # Fall through to defaults on parse errors
                pass
        return DEFAULT_DATA

    # --------------------------------------------------
    # Puente de esquema regional (DA-PLAN-8a / DA-PLAN-8b)
    # --------------------------------------------------
    def regiones(self) -> Dict[str, Dict[str, Any]]:
        """Region publicada + claves del maestro declarado, con `revpar_cop` derivado.

        Acepta `regiones` en el nivel superior y `v25_config.regiones`; el nivel
        superior gana si ambas existen, porque es la forma que el JSON ya uso antes
        de la migracion a `v25_config`.
        """
        data = self.load()
        anidadas = data.get("v25_config", {}).get("regiones", {}) or {}
        superiores = data.get("regiones", {}) or {}
        base_maestro = DEFAULT_DATA["regiones"]["default"]
        resultado: Dict[str, Dict[str, Any]] = {}
        for region in list(anidadas) + [r for r in superiores if r not in anidadas]:
            publicadas = dict(anidadas.get(region) or {})
            publicadas.update(superiores.get(region) or {})
            perfil = dict(base_maestro)
            perfil.update({k: v for k, v in publicadas.items()
                           if k in CLAVES_REGION_PUBLICADAS})
            perfil.pop(CLAVE_REGION_DERIVADA, None)
            precio = perfil.get("precio_promedio")
            ocupacion = perfil.get("ocupacion")
            derivado = isinstance(precio, (int, float)) and isinstance(ocupacion, (int, float))
            perfil["revpar_derivado"] = derivado
            perfil[CLAVE_REGION_DERIVADA] = (
                int(round(precio * ocupacion)) if derivado else base_maestro[CLAVE_REGION_DERIVADA]
            )
            perfil["region"] = region
            resultado[region] = perfil
        return resultado

    def get_all_regions(self) -> List[str]:
        """Regiones reales del lector unico, `default` incluido."""
        return sorted(self.regiones())

    def get_regional_data(self, region: str) -> Dict[str, Any]:
        regiones = self.regiones()
        region_key = (region or "default").strip().lower().replace(" ", "_")
        return regiones.get(region_key) or regiones.get("default") or DEFAULT_DATA["regiones"]["default"]

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


# --------------------------------------------------
# Contrato de maestros (DA-PLAN-8a)
# --------------------------------------------------
def auditoria_maestros(datos_json: Dict[str, Any] = None) -> Dict[str, Any]:
    """Particion real de DEFAULT_DATA contra el JSON publicado, sin afirmar nada.

    Devuelve lo que esta declarado, lo que falta declarar y lo que el JSON publica
    sin que este modulo lo nombre. No lee valores: lee vocabularios, que es lo que
    hace falsa la promesa de «un solo maestro» mientras no haya quien la coteje.
    """
    datos_json = BenchmarkLoader().load() if datos_json is None else datos_json
    v25 = datos_json.get("v25_config", {}) or {}
    publicados_en_cualquier_nivel = set(datos_json) | set(v25)
    poblaciones = {}
    for bloque in sorted(DEFAULT_DATA):
        if bloque in BLOQUES_LEIDOS_DEL_JSON:
            poblaciones[bloque] = "leido_del_json"
        elif bloque in BLOQUES_MAESTRO_DECLARADO:
            poblaciones[bloque] = "maestro_declarado"
        elif bloque in BLOQUES_MAESTRO_CON_FORQUE_PUBLICADO:
            poblaciones[bloque] = "maestro_con_forque_publicado"
        elif bloque in BLOQUES_NO_GOBERNADOS:
            poblaciones[bloque] = "no_gobernado"
        else:
            poblaciones[bloque] = "sin_declarar"
    regiones_maestro = set(DEFAULT_DATA["regiones"]["default"])
    vocabulario_region = (CLAVES_REGION_PUBLICADAS | {CLAVE_REGION_DERIVADA, "revpar_derivado", "region"}
                          | CLAVES_REGION_MAESTRO_DECLARADO)
    return {
        "poblaciones_por_bloque": poblaciones,
        "bloques_sin_declarar": sorted(b for b, p in poblaciones.items() if p == "sin_declarar"),
        # un bloque declarado sin dato publicado SI lo tiene: la declaracion vencio
        "maestro_declarado_con_dato_publicado": sorted(
            b for b in BLOQUES_MAESTRO_DECLARADO if b in publicados_en_cualquier_nivel),
        # un bloque declarado con horque publicado ya no lo tiene: hay que re-decidir
        "forques_sin_nodo": sorted(b for b in BLOQUES_MAESTRO_CON_FORQUE_PUBLICADO if b not in v25),
        "leidos_del_json_sin_nodo": sorted(
            b for b in BLOQUES_LEIDOS_DEL_JSON if b not in publicados_en_cualquier_nivel),
        "claves_region_sin_declarar": sorted(regiones_maestro - vocabulario_region),
    }


def assert_coherencia_maestros(datos_json: Dict[str, Any] = None) -> None:
    """Corta si un bloque o una clave de region entra al maestro sin declaracion."""
    auditoria = auditoria_maestros(datos_json)
    sinsalidas = (auditoria["bloques_sin_declarar"]
                  + auditoria["maestro_declarado_con_dato_publicado"]
                  + auditoria["forques_sin_nodo"]
                  + auditoria["leidos_del_json_sin_nodo"]
                  + auditoria["claves_region_sin_declarar"])
    if sinsalidas:
        raise AssertionError(
            "el contrato de maestros de benchmarks se violo en: " + ", ".join(sinsalidas)
            + " -- declare la poblacion (BLOQUES_MAESTRO_DECLARADO / "
              "BLOQUES_MAESTRO_CON_FORQUE_PUBLICADO / CLAVES_REGION_MAESTRO_DECLARADO) "
              "o publique el dato conforme en el JSON"
        )
