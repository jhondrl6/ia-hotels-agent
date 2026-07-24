"""Delivery Context - Contexto inteligente para generación selectiva de assets.

v3.5: Individualización Radical - Cada asset generado resuelve una brecha específica.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


from enum import Enum


class DeliveryAssetState(Enum):
    """Estado canónico de un asset para el delivery package."""
    DELIVERED = "delivered"                    # Archivo generado y presente en el ZIP
    PRESENT_IN_PRODUCTION = "present"          # Existe en sitio, verificado, sin issues
    PRESENT_WITH_ISSUES = "present_issues"     # Existe en sitio pero con conflicto (ej: WhatsApp)
    ESTIMATED = "estimated"                    # Generado con datos estimados (ESTIMATED_ prefix)
    FAILED = "failed"                          # Falló la generación
    INDETERMINATE = "indeterminate"            # No se pudo verificar presencia
    NOT_DELIVERED = "not_delivered"            # No generado y no presente en producción


ALLOWED_PACKAGES_FOR_CERTIFICATE = ["elite_plus", "elite plus", "eliteplus"]


@dataclass
class DeliveryAssetEntry:
    """Entrada canónica de un asset para el delivery README y manifest."""
    asset_type: str                          # ej: "whatsapp_button"
    service_name: str                        # ej: "Botón de WhatsApp"
    state: DeliveryAssetState                # Estado canónico
    delivery_path: Optional[str] = None      # Ruta dentro del ZIP (POSIX), None si no entregado
    site_verified: bool = False              # ¿Se verificó presencia en sitio?
    confidence: float = 0.0                  # Confidence score del asset
    covered: bool = False                    # ¿Está cubierto (entregado O presente verificado)?
    requires_action: bool = False            # ¿Requiere acción del cliente?
    requires_review: bool = False            # ¿Requiere revisión humana antes de instalar?
    is_advisory: bool = False                # True para guías (ej: whatsapp_conflict_guide), no instalable
    message: str = ""                        # Mensaje descriptivo para el README
    source_refs: List[str] = field(default_factory=list)  # Referencias a fuentes de evidencia

    @classmethod
    def from_skipped_asset(cls, skipped: dict, service_name: str = "") -> "DeliveryAssetEntry":
        """Construye desde un skipped_asset del asset_generation_report."""
        presence = skipped.get("presence_status", "")
        asset_type = skipped.get("asset_type", "")
        site_verified = skipped.get("site_verified", False)

        # Determinar estado según presence_status
        if presence == "exists":
            # Verificar si hay issues (whatsapp_conflict => PRESENT_WITH_ISSUES)
            has_issues = skipped.get("pain_ids_affected") and any(
                "conflict" in pid.lower() for pid in skipped.get("pain_ids_affected", [])
            )
            if has_issues:
                state = DeliveryAssetState.PRESENT_WITH_ISSUES
                msg = f"Existe en producción pero requiere revisión: {skipped.get('reason', '')}"
            else:
                state = DeliveryAssetState.PRESENT_IN_PRODUCTION
                msg = f"Existe en producción — verificado el {skipped.get('reason', '')}"
        elif presence == "exists_with_issues":
            state = DeliveryAssetState.PRESENT_WITH_ISSUES
            msg = f"Existe en producción con incidencias: {skipped.get('reason', '')}"
        elif presence in ("redundant",):
            state = DeliveryAssetState.PRESENT_IN_PRODUCTION
            msg = "Redundante — ya fue entregado previamente"
        else:
            state = DeliveryAssetState.INDETERMINATE
            msg = f"No se pudo verificar presencia ({presence})"

        return cls(
            asset_type=asset_type,
            service_name=service_name,
            state=state,
            site_verified=site_verified,
            confidence=0.0,
            covered=(state in (DeliveryAssetState.PRESENT_IN_PRODUCTION,)),
            requires_action=(state == DeliveryAssetState.PRESENT_WITH_ISSUES),
            requires_review=(state in (DeliveryAssetState.PRESENT_WITH_ISSUES, DeliveryAssetState.INDETERMINATE)),
            message=msg,
            source_refs=["asset_generation_report.json"]
        )

    @classmethod
    def from_generated_asset(cls, asset: dict, service_name: str = "", dest_path: str = "") -> "DeliveryAssetEntry":
        """Construye desde un generated_asset del asset_generation_report."""
        asset_type = asset.get("asset_type", "")
        confidence = asset.get("confidence_score", 0.0)
        can_use = asset.get("can_use", True)
        preflight = asset.get("preflight_status", "")

        # Detectar assets advisory (guías, no instalables)
        advisory_types = {"whatsapp_conflict_guide", "og_tags_guide", "analytics_setup_guide"}
        is_advisory = asset_type in advisory_types or "guide" in asset_type.lower() or "guia" in asset_type.lower()

        if preflight == "BLOCKED":
            state = DeliveryAssetState.FAILED
        elif not can_use:
            state = DeliveryAssetState.ESTIMATED
        elif preflight == "WARNING":
            # Generated with warning — still delivered but estimated
            if "ESTIMATED" in asset.get("filename", ""):
                state = DeliveryAssetState.ESTIMATED
            else:
                state = DeliveryAssetState.DELIVERED
        else:
            state = DeliveryAssetState.DELIVERED

        return cls(
            asset_type=asset_type,
            service_name=service_name,
            state=state,
            delivery_path=dest_path,
            site_verified=False,
            confidence=confidence,
            covered=(state == DeliveryAssetState.DELIVERED),
            requires_action=(state in (DeliveryAssetState.DELIVERED, DeliveryAssetState.ESTIMATED) and not is_advisory),
            requires_review=(state == DeliveryAssetState.ESTIMATED or is_advisory),
            is_advisory=is_advisory,
            message=f"Asset {'entregado' if state == DeliveryAssetState.DELIVERED else 'estimado'} (confidence: {confidence:.2f})",
            source_refs=["asset_generation_report.json"]
        )


@dataclass
class DeliveryContext:
    """Contexto enriquecido para generación selectiva de assets.
    
    Extrae brechas, fugas e issues del diagnóstico completo para determinar
    qué assets deben generarse y con qué justificación.
    """
    
    brechas_criticas: List[Dict] = field(default_factory=list)
    fugas_gbp: List[Dict] = field(default_factory=list)
    seo_issues: List[Dict] = field(default_factory=dict)
    decision_result: Dict = field(default_factory=dict)
    
    cms_detected: Dict = field(default_factory=dict)
    motor_reservas: Optional[Dict] = None
    web_score: int = 0
    hotel_data: Dict = field(default_factory=dict)
    gbp_data: Dict = field(default_factory=dict)
    # ── DT-1 FASE-A: Delivery contract fields ──
    hotel_id: str = ""
    zip_filename: str = ""
    assets: List[DeliveryAssetEntry] = field(default_factory=list)
    files: List[Dict[str, Any]] = field(default_factory=list)
    diagnostics_path: Optional[str] = None
    proposal_path: Optional[str] = None
    
    @classmethod
    def from_analysis_json(cls, analisis_path: Path) -> "DeliveryContext":
        """Carga contexto desde analisis_completo.json.
        
        Maneja gracefully campos faltantes con defaults.
        """
        if not analisis_path.exists():
            return cls()
        
        try:
            with open(analisis_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            return cls()
        
        return cls(
            brechas_criticas=data.get("brechas_criticas", []),
            fugas_gbp=data.get("fugas_gbp", []),
            seo_issues=data.get("seo_issues", {}),
            decision_result=data.get("decision_result", {}),
            cms_detected=data.get("cms_detected", {}),
            motor_reservas=data.get("motor_reservas"),
            web_score=data.get("web_score", 0),
            hotel_data=data.get("hotel_data", {}),
            gbp_data=data.get("gbp_data", {}),
        )
    
    def should_generate(self, asset_type: str) -> Tuple[bool, str]:
        """Determina si generar asset + justificación.
        
        Args:
            asset_type: Tipo de asset (seo_fix_kit, whatsapp_button, etc.)
            
        Returns:
            (should_generate: bool, reason: str)
        """
        asset_checkers = {
            "seo_fix_kit": self._check_seo_issues,
            "whatsapp_button": self._check_whatsapp_fuga,
            "booking_bar": self._check_booking_bar,
            "faqs": self._check_faq_brecha,
            "photos_brief": self._check_photos_fuga,
            "certificate": self._check_certificate,
            "schema": self._check_base_asset,
            "geo_playbook": self._check_base_asset,
        }
        
        checker = asset_checkers.get(asset_type)
        if checker:
            return checker()
        
        return (False, f"Asset type '{asset_type}' no reconocido")
    
    def _check_seo_issues(self) -> Tuple[bool, str]:
        """Verifica si hay issues SEO que justifiquen seo_fix_kit."""
        issues = self.seo_issues
        if not issues:
            return (False, "No hay issues SEO detectados")
        
        if isinstance(issues, dict):
            issues_list = issues.get("issues", [])
            if not issues_list:
                total_issues = len([k for k, v in issues.items() if v])
            else:
                total_issues = len(issues_list)
        elif isinstance(issues, list):
            total_issues = len(issues)
        else:
            total_issues = 1 if issues else 0
        
        if total_issues == 0:
            return (False, "No hay issues SEO detectados")
        
        perdida = self._calculate_seo_loss()
        return (True, f"{total_issues} issues SEO detectados. Pérdida: ${perdida}/mes")
    
    def _check_whatsapp_fuga(self) -> Tuple[bool, str]:
        """Verifica si hay fuga SIN_WHATSAPP_VISIBLE."""
        fuga = self.get_whatsapp_fuga()
        if not fuga:
            return (False, "No hay fuga de WhatsApp detectada")
        
        impacto = fuga.get("impacto_mensual", 0)
        if isinstance(impacto, str):
            try:
                impacto = int(impacto.replace("$", "").replace(",", ""))
            except ValueError:
                impacto = 0
        
        return (True, f"Fuga detectada: pierdes ${impacto}/mes por no tener WhatsApp visible")
    
    def _check_booking_bar(self) -> Tuple[bool, str]:
        """Verifica si hay motor de reservas detectado."""
        motor = self.motor_reservas
        if not motor:
            return (False, "No hay motor de reservas detectado")
        
        prominente = motor.get("prominente", True)
        if prominente:
            return (False, "Motor de reservas ya es prominente")
        
        nombre = motor.get("nombre", "Desconocido")
        clics = motor.get("clics_requeridos", 3)
        
        return (True, f"Motor {nombre} detectado pero no prominente. Requiere {clics}+ clics")
    
    def _check_faq_brecha(self) -> Tuple[bool, str]:
        """Verifica si hay brecha FAQ_AUSENTE."""
        if not self.has_brecha_type("FAQ_AUSENTE"):
            return (False, "No hay brecha de FAQ detectada")
        
        for brecha in self.brechas_criticas:
            if brecha.get("tipo") == "FAQ_AUSENTE":
                impacto = brecha.get("perdida_mensual", 0)
                if isinstance(impacto, str):
                    try:
                        impacto = int(impacto.replace("$", "").replace(",", ""))
                    except ValueError:
                        impacto = 0
                return (True, f"Sin FAQPage schema → invisible para Answer Boxes. Pérdida: ${impacto}/mes")
        
        return (True, "Sin FAQPage schema → invisible para Answer Boxes")
    
    def _check_photos_fuga(self) -> Tuple[bool, str]:
        """Verifica si hay fuga FOTOS_INSUFICIENTES."""
        for fuga in self.fugas_gbp:
            if fuga.get("tipo") == "FOTOS_INSUFICIENTES":
                fotos_actuales = fuga.get("fotos_actuales", 0)
                return (True, f"{fotos_actuales} fotos vs meta 15+. Google te considera menos relevante")
        
        return (False, "No hay fuga de fotos insuficientes")
    
    def _check_certificate(self) -> Tuple[bool, str]:
        """Verifica si el paquete califica para certificados."""
        paquete = self.decision_result.get("paquete", "")
        if not paquete:
            return (False, "No hay información de paquete")
        
        paquete_lower = paquete.lower().replace("_", " ").replace("-", " ")
        
        for allowed in ALLOWED_PACKAGES_FOR_CERTIFICATE:
            if allowed in paquete_lower:
                return (True, f"Paquete {paquete} califica para certificación")
        
        return (False, f"Paquete {paquete} no califica para certificación")
    
    def _check_base_asset(self) -> Tuple[bool, str]:
        """Verifica assets base del paquete (schema, geo_playbook)."""
        return (True, "Asset base del paquete")
    
    def get_seo_critical_issues(self) -> List[Dict]:
        """Retorna issues SEO de prioridad CRÍTICO o ALTO."""
        issues = self.seo_issues
        if not issues:
            return []
        
        critical_issues = []
        
        if isinstance(issues, dict):
            issues_list = issues.get("issues", [])
            if issues_list:
                for issue in issues_list:
                    prioridad = str(issue.get("prioridad", "")).upper()
                    if prioridad in ["CRÍTICO", "CRITICO", "ALTO", "HIGH", "CRITICAL"]:
                        critical_issues.append(issue)
            else:
                for key, value in issues.items():
                    if isinstance(value, dict):
                        prioridad = str(value.get("prioridad", "")).upper()
                        if prioridad in ["CRÍTICO", "CRITICO", "ALTO", "HIGH", "CRITICAL"]:
                            critical_issues.append({"tipo": key, **value})
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                prioridad = str(item.get("prioridad", "")).upper()
                                if prioridad in ["CRÍTICO", "CRITICO", "ALTO", "HIGH", "CRITICAL"]:
                                    critical_issues.append(item)
        elif isinstance(issues, list):
            for issue in issues:
                if isinstance(issue, dict):
                    prioridad = str(issue.get("prioridad", "")).upper()
                    if prioridad in ["CRÍTICO", "CRITICO", "ALTO", "HIGH", "CRITICAL"]:
                        critical_issues.append(issue)
        
        return critical_issues
    
    def get_whatsapp_fuga(self) -> Optional[Dict]:
        """Retorna la fuga de WhatsApp si existe."""
        for fuga in self.fugas_gbp:
            if fuga.get("tipo") == "SIN_WHATSAPP_VISIBLE":
                return fuga
        return None
    
    def get_total_perdida_mensual(self) -> int:
        """Suma todas las pérdidas de brechas y fugas."""
        total = 0
        
        for brecha in self.brechas_criticas:
            perdida = brecha.get("perdida_mensual", 0)
            if isinstance(perdida, str):
                try:
                    perdida = int(perdida.replace("$", "").replace(",", ""))
                except ValueError:
                    perdida = 0
            total += perdida
        
        for fuga in self.fugas_gbp:
            impacto = fuga.get("impacto_mensual", 0)
            if isinstance(impacto, str):
                try:
                    impacto = int(impacto.replace("$", "").replace(",", ""))
                except ValueError:
                    impacto = 0
            total += impacto
        
        return total
    
    def has_brecha_type(self, brecha_type: str) -> bool:
        """Verifica si existe un tipo específico de brecha."""
        for brecha in self.brechas_criticas:
            if brecha.get("tipo") == brecha_type:
                return True
        return False
    
    def _calculate_seo_loss(self) -> int:
        """Calcula la pérdida estimada por issues SEO."""
        seo_loss = 0
        
        issues = self.seo_issues
        if isinstance(issues, dict):
            loss = issues.get("perdida_estimada", 0)
            if isinstance(loss, str):
                try:
                    loss = int(loss.replace("$", "").replace(",", ""))
                except ValueError:
                    loss = 0
            seo_loss += loss
        
        for brecha in self.brechas_criticas:
            if "seo" in str(brecha.get("tipo", "")).lower():
                perdida = brecha.get("perdida_mensual", 0)
                if isinstance(perdida, str):
                    try:
                        perdida = int(perdida.replace("$", "").replace(",", ""))
                    except ValueError:
                        perdida = 0
                seo_loss += perdida
        
        return seo_loss

    # ═══ DT-1 FASE-A: Delivery contract properties ═══

    @property
    def delivered_assets(self) -> List[DeliveryAssetEntry]:
        return [a for a in self.assets if a.state == DeliveryAssetState.DELIVERED]

    @property
    def present_assets(self) -> List[DeliveryAssetEntry]:
        return [a for a in self.assets if a.state == DeliveryAssetState.PRESENT_IN_PRODUCTION]

    @property
    def present_with_issues_assets(self) -> List[DeliveryAssetEntry]:
        return [a for a in self.assets if a.state == DeliveryAssetState.PRESENT_WITH_ISSUES]

    @property
    def estimated_assets(self) -> List[DeliveryAssetEntry]:
        return [a for a in self.assets if a.state == DeliveryAssetState.ESTIMATED]

    @property
    def advisory_assets(self) -> List[DeliveryAssetEntry]:
        """Assets que son guías advisory (no instalables, solo de revisión)."""
        return [a for a in self.assets if a.is_advisory]

    @property
    def covered_count(self) -> int:
        return sum(1 for a in self.assets if a.covered)

    @property
    def total_services(self) -> int:
        return len(self.assets)

    @classmethod
    def from_asset_generation_report(
        cls,
        report_path: Path,
        hotel_id: str,
        zip_filename: str,
        files: List[Dict[str, Any]],
        service_name_map: Optional[Dict[str, str]] = None,
    ) -> "DeliveryContext":
        """Construye un DeliveryContext desde asset_generation_report.json.

        Este classmethod es el puente entre el pipeline y el packager:
        lee el reporte, clasifica cada asset en su estado canónico, y
        construye la lista de DeliveryAssetEntry que el README y el
        manifest consumirán.

        Args:
            report_path: Ruta a asset_generation_report.json
            hotel_id: ID del hotel
            zip_filename: Nombre final del ZIP (ej: "zione_20260723.zip")
            files: Lista final de archivos a empaquetar (files_to_package)
            service_name_map: Mapeo opcional asset_type → service_name humano

        Returns:
            DeliveryContext poblado, o con assets=[] si el reporte no existe.
        """
        report_path = Path(report_path)
        if not report_path.exists():
            # Reporte ausente → contexto vacío (README legacy)
            return cls(hotel_id=hotel_id, zip_filename=zip_filename, files=files)

        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report = json.load(f)
        except (json.JSONDecodeError, IOError):
            # Reporte corrupto o ilegible → contexto vacío (graceful degradation)
            return cls(hotel_id=hotel_id, zip_filename=zip_filename, files=files)

        # Mapeo default asset_type → service_name
        default_names = {
            "whatsapp_button": "Botón de WhatsApp",
            "org_schema": "Schema Organization",
            "hotel_schema": "Schema Hotel",
            "local_business_schema": "Schema LocalBusiness",
            "faq_page": "FAQ Page Schema",
            "optimization_guide": "Guía de Optimización SEO",
            "open_graph": "Open Graph Tags",
            "geo_enriched": "Geo Enrichment",
            "analytics_setup": "Analytics Setup Guide",
            "whatsapp_conflict_guide": "Guía de Conflicto WhatsApp",
        }
        names = {**default_names, **(service_name_map or {})}

        assets = []

        # Procesar generated_assets
        for gen in report.get("generated_assets", []):
            asset_type = gen.get("asset_type", "")
            # Buscar el delivery_path real en la lista de files
            dest_path = ""
            for f in files:
                dest = f.get("dest", "")
                if asset_type in dest.lower() or asset_type.replace("_", "") in dest.lower():
                    dest_path = dest
                    break
            entry = DeliveryAssetEntry.from_generated_asset(
                gen, names.get(asset_type, asset_type), dest_path
            )
            assets.append(entry)

        # Procesar skipped_assets
        for skipped in report.get("skipped_assets", []):
            asset_type = skipped.get("asset_type", "")
            entry = DeliveryAssetEntry.from_skipped_asset(
                skipped, names.get(asset_type, asset_type)
            )
            assets.append(entry)

        # Procesar failed_assets
        for failed in report.get("failed_assets", []):
            asset_type = failed.get("asset_type", "")
            entry = DeliveryAssetEntry(
                asset_type=asset_type,
                service_name=names.get(asset_type, asset_type),
                state=DeliveryAssetState.FAILED,
                confidence=failed.get("confidence_score", 0.0),
                covered=False,
                requires_action=False,
                requires_review=True,
                message=f"Generación fallida: {failed.get('reason', 'desconocido')}",
                source_refs=["asset_generation_report.json"],
            )
            assets.append(entry)

        return cls(
            hotel_id=hotel_id,
            zip_filename=zip_filename,
            assets=assets,
            files=files,
        )
