"""
Site Presence Checker - Verificación del estado REAL del sitio de producción.

Este módulo solve la desconexión fundamental: el sistema genera assets
SIN verificar si el sitio de producción ya tiene la funcionalidad implementada.

SOLUCION: Verificar ANTES de generar, no después.

Arquitectura de decisión:
━━━━━━━━━━━━━━━━━━━━━━━━━
                    ┌─────────────────────────────┐
                    │  SITE PRESENCE CHECK          │
                    │  (scraping + rich results)   │
                    └──────────────┬────────────────┘
                                   │
                    ┌──────────────▼────────────────┐
                    │  ¿Existe en sitio real?       │
                    └──────────────┬────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
      ┌───────────────┐   ┌─────────────────┐   ┌───────────────┐
      │    YA EXISTE  │   │  NO EXISTE      │   │  NO SE PUEDE  │
      │               │   │                 │   │  VERIFICAR    │
      │ → SKIP Asset  │   │ → Generar Asset │   │               │
      │ → Marcar      │   │ → Entregar con  │   │ → Warning     │
      │   ALREADY_    │   │   CAN_USE=True  │   │ → Generar con │
      │   EXISTS      │   │                 │   │   disclaimers  │
      └───────────────┘   └─────────────────┘   └───────────────┘

Causa raíz que solve:
- "El sistema asume pain = needs asset" 
- "No distingue entre sitio ya tiene vs necesita crear"
- "Genera sin verificar si ya existe"
- "Regenera sin смысла múltiples veces"

Created: FASE-CAUSAL-01
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
from urllib.parse import urlparse

# Importar scrapers existentes
from modules.scrapers.schema_finder import SchemaFinder
from modules.data_validation.external_apis.rich_results_client import (
    RichResultsTestClient,
    SchemaType
)


class PresenceStatus(Enum):
    """Estado de presencia de un asset en el sitio real."""
    EXISTS = "exists"                    # Ya existe en el sitio
    EXISTS_WITH_ISSUES = "exists_with_issues"  # Existe pero tiene problemas
    NOT_EXISTS = "not_exists"            # No existe
    VERIFICATION_FAILED = "verification_failed"  # No se pudo verificar
    REDUNDANT = "redundant"              # Ya existe delivery previo


@dataclass
class PresenceCheckResult:
    """Resultado de verificar si un asset ya existe en el sitio."""
    asset_type: str
    status: PresenceStatus
    verified_at: datetime
    site_url: str
    details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    confidence: float = 1.0  # 0.0-1.0 en la verificación
    
    @property
    def should_generate(self) -> bool:
        """¿Deberíamos generar este asset?"""
        return self.status in (
            PresenceStatus.NOT_EXISTS,
            PresenceStatus.VERIFICATION_FAILED,
            # NOT REDUNDANT - si ya existe y fue entregado, no regenerar
        )
    
    @property
    def skip_reason(self) -> Optional[str]:
        """¿Por qué se skippea?"""
        if self.status == PresenceStatus.EXISTS:
            return "Asset ya implementado en sitio de producción"
        elif self.status == PresenceStatus.EXISTS_WITH_ISSUES:
            return f"Asset existe pero tiene problemas: {self.details.get('issues', [])}"
        elif self.status == PresenceStatus.VERIFICATION_FAILED:
            return f"No se pudo verificar: {self.details.get('error', 'Unknown')}"
        return None


@dataclass
class SitePresenceReport:
    """Reporte completo de presencia de todos los assets en un sitio."""
    site_url: str
    checked_at: datetime
    results: Dict[str, PresenceCheckResult] = field(default_factory=dict)
    site_reachable: bool = True
    verification_errors: List[str] = field(default_factory=list)
    
    def get_assets_to_generate(self) -> List[str]:
        """Lista de assets que SÍ deberían generarse."""
        return [
            asset_type 
            for asset_type, result in self.results.items()
            if result.should_generate
        ]
    
    def get_assets_to_skip(self) -> List[Tuple[str, str]]:
        """Lista de assets a skip con razón."""
        return [
            (asset_type, result.skip_reason)
            for asset_type, result in self.results.items()
            if not result.should_generate
        ]
    
    def get_delivery_readiness_score(self) -> float:
        """Score de readiness basado en verificación real."""
        if not self.results:
            return 0.0
        
        skip_count = sum(
            1 for r in self.results.values() 
            if not r.should_generate and r.status == PresenceStatus.EXISTS
        )
        total = len(self.results)
        return (total - skip_count) / total if total > 0 else 0.0


class SitePresenceChecker:
    """
    Verifica el estado REAL de implementaciones en el sitio de producción.
    
    Se integra ANTES de ConditionalGenerator para evitar generar assets
    que ya existen o son redundantes.
    
    Uso:
        checker = SitePresenceChecker()
        report = checker.check_site("https://hotelvisperas.com/")
        
        for asset_type, result in report.results.items():
            if result.should_generate:
                print(f"Generar {asset_type}")
            else:
                print(f"Skip {asset_type}: {result.skip_reason}")
    """
    
    # Mapping de asset_type → qué schema/elemento verificar
    ASSET_TO_SCHEMA_MAP = {
        "faq_page": {
            "schema_type": "FAQPage",
            "check_methods": ["schema", "rich_results"],
            "fallback_text": ["faq", "preguntas frecuentes", "pregunta"]
        },
        "hotel_schema": {
            "schema_type": "Hotel",
            "check_methods": ["schema", "rich_results"],
            "fallback_text": []
        },
        "org_schema": {
            "schema_type": "Organization",
            "check_methods": ["schema", "rich_results"],
            "fallback_text": []
        },
        "whatsapp_button": {
            "schema_type": None,  # No es schema, es elemento HTML
            "check_methods": ["html"],
            "fallback_text": ["whatsapp", "wa.me", "chat"]
        },
        "llms_txt": {
            "schema_type": None,  # Es archivo
            "check_methods": ["direct_fetch"],
            "fallback_text": ["llms.txt"]
        },
        "geo_playbook": {
            "schema_type": None,  # Es contenido, no schema
            "check_methods": ["schema"],  # Solo verificar GBP
            "fallback_text": ["google", "maps", "reseñas"]
        },
        "review_plan": {
            "schema_type": None,
            "check_methods": ["schema"],
            "fallback_text": ["reviews", "reseñas", "google business"]
        },
        "review_widget": {
            "schema_type": "Review",
            "check_methods": ["schema", "html"],
            "fallback_text": []
        },
    }
    
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.schema_finder = SchemaFinder()
        self.rich_results_client = RichResultsTestClient()
        self._cache: Dict[str, SitePresenceReport] = {}
    
    def check_site(
        self, 
        site_url: str,
        asset_types: Optional[List[str]] = None,
        force_refresh: bool = False
    ) -> SitePresenceReport:
        """
        Verifica presencia de assets en un sitio.
        
        Args:
            site_url: URL del sitio a verificar
            asset_types: Lista específica de assets a verificar (None = todos)
            force_refresh: Si True, ignora cache
            
        Returns:
            SitePresenceReport con estado de cada asset
        """
        # Validar URL
        parsed = urlparse(site_url)
        if not parsed.scheme:
            site_url = f"https://{site_url}"
        
        # Check cache
        cache_key = site_url
        if not force_refresh and cache_key in self._cache:
            return self._cache[cache_key]
        
        report = SitePresenceReport(
            site_url=site_url,
            checked_at=datetime.now()
        )
        
        # Obtener schema findings del sitio
        schema_report = self._get_schema_report(site_url)
        
        if not schema_report.get("schemas_encontrados") and "error" in schema_report:
            report.site_reachable = False
            report.verification_errors.append(schema_report["error"])
        
        # Verificar cada asset type
        assets_to_check = asset_types or list(self.ASSET_TO_SCHEMA_MAP.keys())
        
        for asset_type in assets_to_check:
            if asset_type not in self.ASSET_TO_SCHEMA_MAP:
                continue
                
            result = self._check_asset_presence(
                asset_type, 
                site_url, 
                schema_report
            )
            report.results[asset_type] = result
        
        # Guardar en cache
        self._cache[cache_key] = report
        return report
    
    def _get_schema_report(self, url: str) -> Dict[str, Any]:
        """Obtiene reporte de schemas del sitio."""
        try:
            return self.schema_finder.analyze(url)
        except Exception as e:
            return {"error": str(e), "schemas_encontrados": []}
    
    def _check_asset_presence(
        self,
        asset_type: str,
        site_url: str,
        schema_report: Dict[str, Any]
    ) -> PresenceCheckResult:
        """Verifica presencia de un asset específico."""
        config = self.ASSET_TO_SCHEMA_MAP.get(asset_type, {})
        schema_type = config.get("schema_type")
        check_methods = config.get("check_methods", ["schema"])
        
        details = {}
        recommendations = []
        
        # MÉTODO 1: Verificación por Schema
        if "schema" in check_methods and schema_type:
            schema_result = self._check_schema_exists(schema_type, schema_report)
            if schema_result["found"]:
                return PresenceCheckResult(
                    asset_type=asset_type,
                    status=PresenceStatus.EXISTS if not schema_result["has_issues"] 
                           else PresenceStatus.EXISTS_WITH_ISSUES,
                    verified_at=datetime.now(),
                    site_url=site_url,
                    details={
                        "schema_type": schema_type,
                        "issues": schema_result.get("issues", []),
                        "properties": schema_result.get("properties", {})
                    },
                    recommendations=schema_result.get("recommendations", []),
                    confidence=0.95
                )
        
        # MÉTODO 2: Verificación por Rich Results
        if "rich_results" in check_methods:
            rr_result = self._check_rich_results(site_url, schema_type)
            if rr_result["detected"]:
                return PresenceCheckResult(
                    asset_type=asset_type,
                    status=PresenceStatus.EXISTS,
                    verified_at=datetime.now(),
                    site_url=site_url,
                    details=rr_result,
                    confidence=0.90
                )
        
        # MÉTODO 3: Verificación HTML directa (WhatsApp, widgets)
        if "html" in check_methods:
            html_result = self._check_html_element(site_url, config.get("fallback_text", []))
            if html_result["found"]:
                return PresenceCheckResult(
                    asset_type=asset_type,
                    status=PresenceStatus.EXISTS,
                    verified_at=datetime.now(),
                    site_url=site_url,
                    details=html_result,
                    confidence=0.85
                )
        
        # MÉTODO 4: Fetch directo (llms.txt)
        if "direct_fetch" in check_methods:
            direct_result = self._check_direct_resource(site_url, asset_type)
            if direct_result["found"]:
                return PresenceCheckResult(
                    asset_type=asset_type,
                    status=PresenceStatus.EXISTS,
                    verified_at=datetime.now(),
                    site_url=site_url,
                    details=direct_result,
                    confidence=0.95
                )
        
        # NO EXISTE o NO SE PUDO VERIFICAR
        status = PresenceStatus.NOT_EXISTS
        confidence = 0.7  # Menor confianza si no encontramos nada
        
        if not schema_report.get("schemas_encontrados"):
            if "error" in schema_report:
                status = PresenceStatus.VERIFICATION_FAILED
                confidence = 0.3
                recommendations.append("Sitio no accesible o error en verificación")
        
        return PresenceCheckResult(
            asset_type=asset_type,
            status=status,
            verified_at=datetime.now(),
            site_url=site_url,
            details=details,
            recommendations=recommendations,
            confidence=confidence
        )
    
    def _check_schema_exists(
        self, 
        schema_type: str, 
        schema_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verifica si un schema type existe en el reporte."""
        schemas_found = schema_report.get("schemas_encontrados", [])
        schema_types = [s.get("type") for s in schemas_found]
        
        # Normalizar
        target_types = [schema_type]
        if schema_type == "Hotel":
            target_types.extend(["LodgingBusiness", "LocalBusiness"])
        elif schema_type == "Organization":
            target_types.append("Organization")
        
        found_schema = None
        for schema in schemas_found:
            if schema.get("type") in target_types:
                found_schema = schema
                break
        
        if not found_schema:
            return {"found": False}
        
        # Verificar issues
        missing_fields = schema_report.get("campos_faltantes", [])
        issues = []
        recommendations = []
        
        if missing_fields:
            issues.append(f"Campos faltantes: {missing_fields}")
            recommendations.append(f"Completar campos: {', '.join(missing_fields[:3])}")
        
        return {
            "found": True,
            "has_issues": len(issues) > 0,
            "issues": issues,
            "properties": found_schema.get("data", {}),
            "recommendations": recommendations
        }
    
    def _check_rich_results(
        self, 
        site_url: str, 
        schema_type: str
    ) -> Dict[str, Any]:
        """Verifica via Google Rich Results API."""
        try:
            result = self.rich_results_client.test_url(site_url)
            detected_types = [s.schema_type for s in result.schemas]
            
            return {
                "detected": schema_type in detected_types if schema_type else result.detected_items > 0,
                "valid_items": result.valid_items,
                "all_types": detected_types
            }
        except Exception:
            return {"detected": False}
    
    def _check_html_element(
        self, 
        site_url: str, 
        search_texts: List[str]
    ) -> Dict[str, Any]:
        """Verifica presencia de elemento/botón en HTML."""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(site_url, headers=headers, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            found_texts = []
            for text in search_texts:
                if text.lower() in soup.text.lower():
                    found_texts.append(text)
            
            return {
                "found": len(found_texts) > 0,
                "matched_texts": found_texts
            }
        except Exception:
            return {"found": False}
    
    def _check_direct_resource(
        self, 
        site_url: str, 
        asset_type: str
    ) -> Dict[str, Any]:
        """Verifica acceso directo a recurso (ej: /llms.txt)."""
        resource_paths = {
            "llms_txt": ["/llms.txt", "/llm.txt", "/.well-known/llm.txt"]
        }
        
        paths = resource_paths.get(asset_type, [])
        if not paths:
            return {"found": False}
        
        try:
            import requests
            headers = {"User-Agent": "Mozilla/5.0"}
            
            for path in paths:
                full_url = site_url.rstrip("/") + path
                try:
                    response = requests.get(full_url, headers=headers, timeout=5)
                    if response.status_code == 200:
                        return {
                            "found": True,
                            "url": full_url,
                            "size": len(response.content)
                        }
                except requests.RequestException:
                    continue
            
            return {"found": False}
        except Exception:
            return {"found": False}
    
    def check_asset_delivery_history(
        self,
        hotel_id: str,
        asset_type: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Verifica si un asset ya fue entregado previamente.
        
        Args:
            hotel_id: ID del hotel
            asset_type: Tipo de asset
            
        Returns:
            Tuple (ya_entregado, path_del_ultimo)
        """
        # Esta función se conecta con el delivery context para verificar
        # si ya existe un delivery previo para este asset
        from pathlib import Path
        import os
        
        base_output = Path(os.environ.get(
            "IAH_OUTPUT_DIR", 
            "/mnt/c/Users/Jhond/Github/iah-cli/output/v4_complete/deliveries"
        ))
        
        # Buscar entregas previas del mismo asset
        hotel_dir = base_output / f"{hotel_id}_*"
        
        # Pattern de archivo sin ESTIMATED/FAILED prefix
        asset_patterns = {
            "faq_page": "faqs*.csv",
            "hotel_schema": "hotel_schema*.json",
            "org_schema": "org_schema*.json",
            "whatsapp_button": "boton_whatsapp*.html",
            "llms_txt": "llms*.txt",
            "geo_playbook": "geo_playbook*.md",
            "review_plan": "plan_reviews*.md",
            "review_widget": "widget_reviews*.html",
        }
        
        pattern = asset_patterns.get(asset_type)
        if not pattern:
            return False, None
        
        # Buscar archivos
        for delivery_dir in base_output.glob(f"{hotel_id}_*"):
            if not delivery_dir.is_dir():
                continue
            assets_dir = delivery_dir / "ASSETS" / asset_type
            if not assets_dir.exists():
                continue
            
            for match in assets_dir.glob(pattern):
                if "ESTIMATED" not in match.name and "FAILED" not in match.name:
                    return True, str(match)
        
        return False, None
    
    def get_full_presence_decision(
        self,
        site_url: str,
        hotel_id: str,
        asset_type: str
    ) -> PresenceCheckResult:
        """
        Obtiene decisión completa de presencia para un asset.
        
        Combina:
        1. Verificación de sitio real
        2. Historial de deliveries
        
        Returns:
            PresenceCheckResult con decisión final
        """
        # Step 1: Verificar sitio real
        site_report = self.check_site(site_url, asset_types=[asset_type])
        site_result = site_report.results.get(asset_type)
        
        if not site_result:
            return PresenceCheckResult(
                asset_type=asset_type,
                status=PresenceStatus.VERIFICATION_FAILED,
                verified_at=datetime.now(),
                site_url=site_url,
                details={"error": "No se pudo verificar sitio"},
                confidence=0.0
            )
        
        # Step 2: Verificar historial de delivery
        was_delivered, delivery_path = self.check_asset_delivery_history(
            hotel_id, asset_type
        )
        
        # Modificar resultado basado en historial
        if was_delivered and site_result.status == PresenceStatus.EXISTS:
            # El sitio YA tiene y YA se entregó → REDUNDANT
            site_result.status = PresenceStatus.REDUNDANT
            site_result.details["delivery_path"] = delivery_path
            site_result.details["message"] = "Asset ya implementado y entregado previamente"
            site_result.recommendations.append(
                "No regenerar: ya existe en producción y fue entregado"
            )
        
        return site_result


def check_before_generate(
    site_url: str,
    hotel_id: str,
    asset_type: str
) -> Tuple[bool, PresenceCheckResult]:
    """
    Función helper para integrar en ConditionalGenerator.
    
    Usage:
        should_generate, result = check_before_generate(
            "https://hotelvisperas.com/",
            "hotelvisperas",
            "faq_page"
        )
        
        if not should_generate:
            print(f"SKIP: {result.skip_reason}")
    """
    checker = SitePresenceChecker()
    result = checker.get_full_presence_decision(site_url, hotel_id, asset_type)
    return result.should_generate, result
