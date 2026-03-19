"""Delivery Context - Contexto inteligente para generación selectiva de assets.

v3.5: Individualización Radical - Cada asset generado resuelve una brecha específica.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


ALLOWED_PACKAGES_FOR_CERTIFICATE = ["elite_plus", "elite plus", "eliteplus"]


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
