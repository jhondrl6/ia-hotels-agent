import os
from pathlib import Path
import json
import unicodedata
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple

from modules.scrapers.scraper_fallback import ScraperFallback
from modules.utils.benchmarks import BenchmarkLoader
from datetime import datetime


def _is_empty_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) == 0
    return False


def _merge_unique_list(base: Iterable[Any], extra: Iterable[Any]) -> List[Any]:
    seen = set()
    result: List[Any] = []
    for item in list(base or []):
        if item not in seen:
            result.append(item)
            seen.add(item)
    for item in list(extra or []):
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result


def _format_horarios_status(gbp_data: dict) -> Tuple[str, str, str]:
    """
    Formatea estado de horarios con indicador de confianza.
    
    Returns:
        Tuple[valor_display, status_recommendation, nota_explicativa]
    """
    tiene_horarios = gbp_data.get('horarios', False)
    confidence = gbp_data.get('meta', {}).get('data_confidence', {}).get('horarios', 0.0)
    detection_info = gbp_data.get('meta', {}).get('horarios_detection', {})
    
    # Casos especiales
    if confidence == 0.0 and detection_info.get('method') == 'error':
        return "[ERROR]", "VERIFICAR", f"⚠️ Fallo técnico: {detection_info.get('error', 'desconocido')}"
    
    if confidence == 0.0:
        return "[DESCONOCIDO]", "VERIFICAR", "⚠️ No se pudo verificar automáticamente"
    
    # Evaluación por confianza
    if tiene_horarios:
        if confidence >= 0.8:
            return "[OK] Sí", "OK", f"✓ Detectado con {int(confidence*100)}% confianza"
        elif confidence >= 0.5:
            return "[OK] Sí*", "OK", f"⚠️ Confianza media ({int(confidence*100)}%) - revisar manualmente"
        else:
            return "[POSIBLE] Sí*", "VERIFICAR", f"⚠️ Confianza baja ({int(confidence*100)}%) - VERIFICAR"
    else:
        if confidence >= 0.7:
            return "[FAIL] No", "MEJORAR", f"✗ Confirmado ausente (búsqueda exhaustiva)"
        else:
            return "[POSIBLE FAIL] No*", "VERIFICAR", f"⚠️ No detectado, pero revisar manualmente"


def _format_fotos_status(gbp_data: dict) -> Tuple[str, str, str]:
    """
    Formatea estado de fotos con indicador de confianza y disclaimer.
    
    IMPORTANTE: El conteo incluye TANTO fotos del propietario COMO de huéspedes.
    Google Maps no distingue entre ambos tipos via scraping DOM.
    
    Returns:
        Tuple[valor_display, status_recommendation, nota_explicativa]
    """
    fotos = gbp_data.get('fotos', 0)
    meta = gbp_data.get('meta', {}).get('scrape_debug', {})
    confidence = meta.get('photos_confidence', 0)
    method = meta.get('photos_method', 'unknown')
    
    # Nota base sobre tipos de fotos
    nota_tipos = "ℹ️ Conteo incluye fotos del propietario + huéspedes (Google Maps no las distingue)"
    
    # Casos especiales por método de extracción
    if method == 'none' or confidence == 0:
        return (
            f"[⚠️ VERIFICAR] {fotos}",
            "VERIFICAR MANUAL",
            f"⚠️ Extracción falló (confianza: 0%) - VERIFICAR EN GOOGLE MAPS. {nota_tipos}"
        )
    
    if method == 'cache_fallback':
        return (
            f"{fotos}*",
            "OK" if fotos >= 15 else "Mejorar",
            f"⚠️ Dato de caché (confianza: {confidence}%) - Puede estar desactualizado. {nota_tipos}"
        )
    
    # Evaluación normal por confianza
    if confidence >= 80:
        status = "[OK] OK" if fotos >= 15 else "[WARN] Mejorar"
        nota = f"✓ Detectado con {confidence}% confianza ({method}). {nota_tipos}"
    elif confidence >= 50:
        status = "[OK] OK*" if fotos >= 15 else "[WARN] Mejorar*"
        nota = f"⚠️ Confianza media ({confidence}%) - considerar verificar. {nota_tipos}"
    else:
        status = "[⚠️] Verificar"
        nota = f"⚠️ Confianza baja ({confidence}%) - VERIFICAR MANUALMENTE. {nota_tipos}"
    
    return str(fotos), status, nota


@dataclass
class ReportDataBundle:
    hotel_data: Dict[str, Any] = field(default_factory=dict)
    gbp_data: Dict[str, Any] = field(default_factory=dict)
    schema_data: Dict[str, Any] = field(default_factory=dict)
    ia_test: Dict[str, Any] = field(default_factory=dict)
    llm_analysis: Dict[str, Any] = field(default_factory=dict)
    roi_data: Dict[str, Any] = field(default_factory=dict)

    def clone(self) -> "ReportDataBundle":
        return ReportDataBundle(
            hotel_data=deepcopy(self.hotel_data),
            gbp_data=deepcopy(self.gbp_data),
            schema_data=deepcopy(self.schema_data),
            ia_test=deepcopy(self.ia_test),
            llm_analysis=deepcopy(self.llm_analysis),
            roi_data=deepcopy(self.roi_data),
        )


@dataclass
class ReportIntegrationAudit:
    is_compatible: bool
    missing_sections: List[str] = field(default_factory=list)
    missing_fields: Dict[str, List[str]] = field(default_factory=dict)
    conflicts: Dict[str, List[str]] = field(default_factory=dict)
    applied_strategy: str = ""
    notes: List[str] = field(default_factory=list)


class ReportIntegrationAdapter:
    REQUIRED_SECTIONS: Tuple[str, ...] = (
        "hotel_data",
        "gbp_data",
        "schema_data",
        "ia_test",
        "llm_analysis",
        "roi_data",
    )

    SECTION_CORE_FIELDS: Dict[str, Tuple[str, ...]] = {
        "hotel_data": ("nombre", "ubicacion"),
        "gbp_data": ("score",),
        "schema_data": ("score_schema",),
        "ia_test": ("total_queries",),
        "llm_analysis": ("perdida_mensual_total",),
        "roi_data": ("totales_6_meses",),
    }

    CONFIDENCE_ORDER: Dict[str, int] = {"alta": 3, "media": 2, "low": 1, "baja": 1}

    def __init__(
        self,
        prefer_external: Optional[bool] = None,
        dedup_strategy: Optional[str] = None,
    ) -> None:
        env_prefer_external = os.getenv("REPORT_INTEGRATION_PREFER_EXTERNAL", "true").lower()
        self.prefer_external = prefer_external if prefer_external is not None else env_prefer_external in ("1", "true", "yes", "on")
        self.dedup_strategy = dedup_strategy or os.getenv("REPORT_INTEGRATION_STRATEGY", "prefer_high_confidence")

    def combine(
        self,
        base_bundle: ReportDataBundle,
        integration_payload: Optional[Dict[str, Any]],
    ) -> Tuple[ReportDataBundle, ReportIntegrationAudit]:
        if not integration_payload:
            audit = ReportIntegrationAudit(
                is_compatible=True,
                notes=["Carga de integración vacía"],
                applied_strategy=self.dedup_strategy,
            )
            return base_bundle.clone(), audit

        audit = self.evaluate(integration_payload, base_bundle)
        audit.applied_strategy = self.dedup_strategy
        if not audit.is_compatible:
            audit.notes.append("Integración descartada por incompatibilidades")
            return base_bundle.clone(), audit

        external_bundle = self.build_bundle(integration_payload)
        merged_bundle = self.merge_bundles(base_bundle, external_bundle)
        audit.notes.append("Integración aplicada correctamente")
        return merged_bundle, audit

    def build_bundle(self, payload: Dict[str, Any]) -> ReportDataBundle:
        sections: Dict[str, Dict[str, Any]] = {}
        for section in self.REQUIRED_SECTIONS:
            section_payload = payload.get(section, {})
            if section_payload is None:
                section_payload = {}
            if not isinstance(section_payload, dict):
                raise TypeError(f"{section} debe ser un diccionario")
            sections[section] = deepcopy(section_payload)
        return ReportDataBundle(**sections)

    def evaluate(
        self,
        payload: Dict[str, Any],
        base_bundle: Optional[ReportDataBundle] = None,
    ) -> ReportIntegrationAudit:
        missing_sections = [s for s in self.REQUIRED_SECTIONS if s not in payload]
        missing_fields: Dict[str, List[str]] = {}
        for section, fields in self.SECTION_CORE_FIELDS.items():
            section_payload = payload.get(section, {}) or {}
            base_section = getattr(base_bundle, section) if base_bundle else {}
            if not isinstance(base_section, dict):
                base_section = {}
            missing: List[str] = []
            for field_name in fields:
                incoming_has = field_name in section_payload and not _is_empty_value(section_payload.get(field_name))
                base_has = field_name in base_section and not _is_empty_value(base_section.get(field_name))
                if not incoming_has and not base_has:
                    missing.append(field_name)
            if missing:
                missing_fields[section] = missing

        conflicts: Dict[str, List[str]] = {}
        if base_bundle is not None:
            self._detect_conflicts(base_bundle.hotel_data, payload.get("hotel_data", {}), "hotel_data", conflicts)
            self._detect_conflicts(base_bundle.gbp_data, payload.get("gbp_data", {}), "gbp_data", conflicts)
            self._detect_conflicts(base_bundle.schema_data, payload.get("schema_data", {}), "schema_data", conflicts)
            self._detect_conflicts(base_bundle.ia_test, payload.get("ia_test", {}), "ia_test", conflicts)
            self._detect_conflicts(base_bundle.llm_analysis, payload.get("llm_analysis", {}), "llm_analysis", conflicts)
            self._detect_conflicts(base_bundle.roi_data, payload.get("roi_data", {}), "roi_data", conflicts)

        is_compatible = not missing_sections and not missing_fields and not conflicts
        return ReportIntegrationAudit(
            is_compatible=is_compatible,
            missing_sections=missing_sections,
            missing_fields=missing_fields,
            conflicts=conflicts,
        )

    def merge_bundles(
        self,
        base_bundle: ReportDataBundle,
        external_bundle: ReportDataBundle,
    ) -> ReportDataBundle:
        merged = base_bundle.clone()
        merged.hotel_data = self._merge_hotel_data(base_bundle.hotel_data, external_bundle.hotel_data)
        merged.gbp_data = self._merge_generic(base_bundle.gbp_data, external_bundle.gbp_data)
        merged.schema_data = self._merge_generic(base_bundle.schema_data, external_bundle.schema_data)
        merged.ia_test = self._merge_generic(base_bundle.ia_test, external_bundle.ia_test)
        merged.llm_analysis = self._merge_generic(base_bundle.llm_analysis, external_bundle.llm_analysis)
        merged.roi_data = self._merge_generic(base_bundle.roi_data, external_bundle.roi_data)
        return merged

    def _detect_conflicts(
        self,
        base: Dict[str, Any],
        incoming: Dict[str, Any],
        section: str,
        conflicts: Dict[str, List[str]],
    ) -> None:
        if not base or not incoming:
            return
        estimated = set(base.get("campos_estimados", [])) if isinstance(base, dict) else set()
        for key, value in incoming.items():
            if key == "campos_estimados":
                continue
            if _is_empty_value(value):
                continue
            if key not in base:
                continue
            base_value = base.get(key)
            if _is_empty_value(base_value):
                continue
            if key in estimated:
                continue
            if self.prefer_external:
                continue
            if isinstance(base_value, (list, dict)) or isinstance(value, (list, dict)):
                continue
            if base_value != value:
                conflicts.setdefault(section, []).append(key)

    def _merge_generic(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        result = deepcopy(base or {})
        for key, value in (override or {}).items():
            if isinstance(value, list):
                result[key] = _merge_unique_list(result.get(key, []), value)
                continue
            if isinstance(value, dict):
                nested_base = result.get(key, {}) if isinstance(result.get(key), dict) else {}
                result[key] = self._merge_generic(nested_base, value)
                continue
            if _is_empty_value(value):
                continue
            if self.prefer_external or key not in result or _is_empty_value(result.get(key)):
                result[key] = value
        return result

    def _merge_hotel_data(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        result = deepcopy(base or {})
        estimated_fields = set(result.get("campos_estimados", []) or [])
        override_estimated = set((override or {}).get("campos_estimados", []) or [])

        for key, value in (override or {}).items():
            if key == "campos_estimados":
                continue
            if isinstance(value, list):
                result[key] = _merge_unique_list(result.get(key, []), value)
                continue
            if isinstance(value, dict):
                nested_base = result.get(key, {}) if isinstance(result.get(key), dict) else {}
                result[key] = self._merge_generic(nested_base, value)
                continue
            if _is_empty_value(value):
                if key in override_estimated:
                    estimated_fields.add(key)
                continue
            base_value = result.get(key)
            should_replace = self.prefer_external or key in estimated_fields or _is_empty_value(base_value)
            if not should_replace and isinstance(value, (int, float)) and isinstance(base_value, (int, float)):
                should_replace = value > base_value
            if should_replace:
                result[key] = value
                estimated_fields.discard(key)

        final_estimated = {field for field in estimated_fields | override_estimated if _is_empty_value(result.get(field))}
        if final_estimated:
            result["campos_estimados"] = sorted(final_estimated)
        elif "campos_estimados" in result:
            result.pop("campos_estimados")
        return result

class ReportBuilder:

    def __init__(self):
        self.templates_path = Path("templates")
        self.templates_path.mkdir(exist_ok=True)
        self._ensure_default_template()
        self._fallback_helper = ScraperFallback()
        self._region_profiles = self._fallback_helper.benchmarks.get('regiones', {})
        self._default_region_profile = self._region_profiles.get('default', {})
        self._benchmark_loader = BenchmarkLoader()

        env_enabled = os.getenv("REPORT_INTEGRATION_ENABLED", "false").lower()
        self._integration_enabled = env_enabled in ("1", "true", "yes", "on")
        self._integration_adapter = ReportIntegrationAdapter()
        self._last_integration_audit: Optional[ReportIntegrationAudit] = None

    def _ensure_default_template(self):
        template_file = self.templates_path / "diagnostico_ejecutivo.md"
        if not template_file.exists():
            template_file.write_text(self._get_default_template(), encoding="utf-8")

    # ═══════════════════════════════════════════════════════════════
    # 🔧 CORRECCIÓN CRÍTICA: Sistema de Trazabilidad de Calidad (DQT)
    # ═══════════════════════════════════════════════════════════════
    
    def _safe_format_currency(self, value, campo_nombre=None, campos_estimados=None, 
                               mostrar_origen=True, context="table"):
        """
        Formatea valores monetarios con TRAZABILIDAD DE CALIDAD DE DATOS.
        
        Args:
            value: Valor a formatear (puede ser None, 0, o número válido)
            campo_nombre: Nombre del campo (ej: 'precio_promedio') para validación
            campos_estimados: Lista de campos que fueron estimados
            mostrar_origen: Si True, incluye etiqueta de origen/confianza
            context: 'table' (tablas) o 'text' (texto corrido)
        
        Returns:
            str: Valor formateado con contexto de calidad
        
        Ejemplos:
            value=None → "No disponible" o "N/D"
            value=0, campo no validado → "Validar ($0)" o "$0 ⚠️"
            value=0, campo estimado → "Estimado: $0" 
            value=150000 → "$150,000" o "$150,000 COP"
        """
        # 1️⃣ Detectar si el campo fue estimado
        es_estimado = False
        if campo_nombre and campos_estimados:
            es_estimado = campo_nombre in campos_estimados
        
        # 2️⃣ Manejo de valores None (dato faltante)
        if value is None:
            if context == "table":
                return "No disponible"
            else:
                return "N/D"
        
        # 3️⃣ Manejo de valores 0 (ambiguo: ¿real o error?)
        if value == 0:
            if es_estimado:
                # Si fue estimado y es 0, es dato válido pero sospechoso
                if context == "table":
                    return "Estimado: $0 ⚠️"
                else:
                    return "$0 (estimado)"
            else:
                # Si no fue estimado y es 0, requiere validación
                if context == "table":
                    return "Validar ($0)"
                else:
                    return "$0 ⚠️"
        
        # 4️⃣ Valores positivos válidos
        try:
            valor_formateado = f"${value:,.0f}"
            
            if not mostrar_origen:
                return valor_formateado
            
            # Añadir contexto de origen si corresponde
            if context == "table":
                if es_estimado:
                    return f"{valor_formateado} (est.)"
                return valor_formateado
            else:
                # Para texto corrido, siempre incluir moneda
                if es_estimado:
                    return f"{valor_formateado} COP (estimado)"
                return f"{valor_formateado} COP"
                
        except (TypeError, ValueError):
            # Fallback para tipos no numéricos
            if context == "table":
                return "Dato inválido"
            else:
                return "N/D"

    def _get_data_quality_label(self, campo_nombre, valor, campos_estimados, confidence="media"):
        """
        Genera etiqueta de calidad de datos para columna "Fuente" en tablas.
        
        Args:
            campo_nombre: Nombre del campo
            valor: Valor actual del campo
            campos_estimados: Lista de campos estimados
            confidence: Nivel de confianza del dato
        
        Returns:
            str: Etiqueta de calidad (ej: "Web ✓", "Estimado ⚠️", "No disponible")
        """
        # Caso 1: Dato faltante (None o vacío)
        if valor is None or valor == '':
            return "No disponible"
        
        # Caso 2: Campo fue estimado
        if campo_nombre in campos_estimados:
            if confidence == "high":
                return "Estimado ✓"
            elif confidence == "low":
                return "Estimado ⚠️"
            else:
                return "Estimado"
        
        # Caso 3: Valor 0 sospechoso
        if isinstance(valor, (int, float)) and valor == 0:
            return "Revisar ⚠️"
        
        # Caso 4: Dato obtenido correctamente
        if confidence == "high":
            return "Web ✓"
        elif confidence == "low":
            return "Web (baja confianza)"
        else:
            return "Web"

    # ═══════════════════════════════════════════════════════════════
    # 🔄 MÉTODOS EXISTENTES (sin cambios críticos)
    # ═══════════════════════════════════════════════════════════════

    def _safe_get(self, data_dict, key, default=0):
        """Obtiene valores de diccionario de forma segura"""
        if data_dict is None:
            return default
        value = data_dict.get(key, default)
        return value if value is not None else default

    def _normalize_markdown(self, content: str) -> str:
        """Compacta saltos de linea sucesivos y recorta espacios finales.

        También elimina sangrías accidentales (4 espacios) en líneas de Markdown
        que no deberían renderizarse como bloque de código (headings/bold),
        manteniendo intactos los bloques con fences ```.
        """
        if not content:
            return ""

        lines = []
        for raw in content.splitlines():
            keep_two_spaces = raw.endswith("  ")
            line = raw.rstrip()
            if keep_two_spaces and not line.endswith("  "):
                line = line + "  "
            lines.append(line)
        compact_lines = []
        previous_blank = False
        in_fence = False
        for line in lines:
            if line.lstrip().startswith("```"):
                in_fence = not in_fence

            if not in_fence and line.startswith("    "):
                stripped = line[4:]
                if stripped.startswith("#") or stripped.startswith("**"):
                    line = stripped

            if line.strip():
                compact_lines.append(line)
                previous_blank = False
            else:
                if not previous_blank:
                    compact_lines.append("")
                previous_blank = True
        normalized = "\n".join(compact_lines).strip()
        return normalized + "\n" if normalized else ""

    def _detect_region(self, ubicacion: str) -> str:
        if not ubicacion:
            return "default"
        normalized = unicodedata.normalize('NFKD', ubicacion)
        normalized = normalized.encode('ascii', 'ignore').decode('ascii')
        return self._fallback_helper._detect_region(normalized.lower())

    def _get_region_profile(self, ubicacion: str):
        region = self._detect_region(ubicacion)
        return region, self._region_profiles.get(region, self._default_region_profile)

    def _format_visibilidad_estado(self, score):
        try:
            score_int = int(score)
        except (TypeError, ValueError):
            return ""
        if score_int >= 80:
            etiqueta = "✅ Score IA sólido - mantener momentum 2-Pilares"
        elif score_int >= 60:
            etiqueta = "⚠️ Score IA regular - activar mejoras rápidas"
        elif score_int >= 40:
            etiqueta = "🚨 Score IA crítico - hotel casi invisible"
        else:
            etiqueta = "❌ Score IA inexistente - dependencia total de OTAs"
        return f"> **Score IA actual:** {score_int}/100 · {etiqueta}"

    def _map_brecha_to_paquete(self, tipo):
        tipo_lower = (tipo or "").lower()
        if any(keyword in tipo_lower for keyword in ['whatsapp', 'ubicacion', 'ubicación', 'geo', 'motor_reservas', 'motor']):
            return "Starter GEO"
        if any(keyword in tipo_lower for keyword in ['schema', 'faq', 'datos', 'contenido']):
            return "Pro AEO"
        if any(keyword in tipo_lower for keyword in ['revpar', 'adr', 'modelo', 'ota']):
            return "Elite"
        if any(keyword in tipo_lower for keyword in ['web', 'conversión', 'conversion', 'lento', 'carga', 'ux', 'diseño']):
            return "Elite PLUS"
        return "Pro AEO"

    def _format_brechas_scraper(self, brechas):
        if not brechas:
            return "_Sin brechas detectadas por el scraper._"
        def _prioridad_key(brecha):
            prioridad = brecha.get('prioridad', 99)
            severidad = brecha.get('severidad', 'Z')
            return prioridad, severidad
        lineas = []
        for brecha in sorted(brechas, key=_prioridad_key)[:5]:
            tipo = brecha.get('tipo', 'SIN_CLASIFICAR')
            severidad = brecha.get('severidad', 'N/A')
            impacto = brecha.get('impacto_estimado', 'Impacto no estimado')
            paquete = self._map_brecha_to_paquete(tipo)
            solucion = brecha.get('solucion_rapida')
            detalle_solucion = f" · Acción: {solucion}" if solucion else ""
            lineas.append(
                f"- **{tipo}** ({severidad}) · {impacto} · **Paquete sugerido:** {paquete}{detalle_solucion}"
            )
        return "\n".join(lineas)

    def _prepare_deterministic_llm_analysis(
        self,
        llm_analysis: Dict[str, Any],
        roi_data: Dict[str, Any],
        decision_result: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Garantiza campos mínimos para narrativa determinista (sin LLM)."""
        analysis = deepcopy(llm_analysis or {})
        paquete = (decision_result or {}).get("paquete") if decision_result else None
        justificacion = (decision_result or {}).get("justificacion") if decision_result else None

        if paquete and not analysis.get("paquete_recomendado"):
            analysis["paquete_recomendado"] = paquete
        if justificacion and not analysis.get("justificacion_paquete"):
            analysis["justificacion_paquete"] = justificacion

        perdida_mensual = analysis.get("perdida_mensual_total")
        if perdida_mensual is None:
            totales = (roi_data or {}).get("totales_6_meses", {})
            perdida_mensual = totales.get("perdida_mensual") or 0
            analysis["perdida_mensual_total"] = perdida_mensual

        if not analysis.get("brechas_criticas"):
            impact = perdida_mensual if isinstance(perdida_mensual, (int, float)) else 0
            analysis["brechas_criticas"] = [
                {
                    "nombre": "Visibilidad IA insuficiente (deterministico)",
                    "impacto_mensual": int(impact * 0.5),
                    "descripcion": "Reglas v2.3: activar GBP + JSON-LD para entrar en respuestas de asistentes IA.",
                    "prioridad": 1,
                },
                {
                    "nombre": "Momentum IA conversacional bajo",
                    "impacto_mensual": int(impact * 0.3),
                    "descripcion": "Faltan señales frescas (posts, Q&A, reseñas) que eleven ranking en IA.",
                    "prioridad": 2,
                },
            ]

        if not analysis.get("quick_wins"):
            analysis["quick_wins"] = [
                "Actualizar GBP con fotos y Q&A en 7 dias (reglas v2.3).",
                "Publicar JSON-LD Hotel + FAQ con tarifas y amenities críticos.",
                "Enviar micro-post semanal a GBP para subir momentum IA.",
            ]

        analysis["modo_narrativa"] = "deterministico"
        return analysis

    # ═══════════════════════════════════════════════════════════════
    # 📊 MÉTODO PRINCIPAL CORREGIDO: Generación de Diagnóstico
    # ═══════════════════════════════════════════════════════════════

    def generate(
        self,
        hotel_data,
        gbp_data,
        schema_data,
        ia_test,
        llm_analysis,
        roi_data,
        output_dir,
        integration_payload: Optional[Dict[str, Any]] = None,
        force_integration: bool = False,
        mode: str = "generativo",
        decision_result: Optional[Dict[str, Any]] = None,
        seo_data: Optional[Dict[str, Any]] = None,
        competitors_data: Optional[List[Dict]] = None,
        truth_results: Optional[Dict[str, Any]] = None,
    ):
        """Genera reporte ejecutivo completo"""
        
        # 🛡️ Protocolo de Verdad 4.0
        truth_stamp = ""
        if truth_results:
            truth_stamp = f"\n> **🛡️ Certificado de Veracidad**: Este diagnóstico ha sido validado mediante Triple Triangulación (Datos Técnicos + Visibilidad IA + Benchmarking 2026). Confianza: {hotel_data.get('confidence', 'ALTA').upper()}\n"

        base_bundle = ReportDataBundle(
            hotel_data=deepcopy(hotel_data or {}),
            gbp_data=deepcopy(gbp_data or {}),
            schema_data=deepcopy(schema_data or {}),
            ia_test=deepcopy(ia_test or {}),
            llm_analysis=deepcopy(llm_analysis or {}),
            roi_data=deepcopy(roi_data or {}),
        )

        apply_integration = (
            integration_payload is not None
            and (self._integration_enabled or force_integration)
        )

        if integration_payload and not apply_integration:
            self._last_integration_audit = ReportIntegrationAudit(
                is_compatible=True,
                applied_strategy=self._integration_adapter.dedup_strategy,
                notes=["Integración deshabilitada"],
            )

        if apply_integration:
            merged_bundle, audit = self._integration_adapter.combine(
                base_bundle, integration_payload
            )
            self._last_integration_audit = audit
            if not audit.is_compatible:
                print("   [WARN] Integración omitida: datos incompatibles")
                bundle = base_bundle.clone()
            else:
                if audit.notes:
                    print(f"   [OK] {audit.notes[-1]}")
                bundle = merged_bundle
        else:
            bundle = base_bundle.clone()

        hotel_data = bundle.hotel_data
        gbp_data = bundle.gbp_data
        schema_data = bundle.schema_data
        ia_test = bundle.ia_test
        llm_analysis = bundle.llm_analysis
        if mode == "deterministico":
            llm_analysis = self._prepare_deterministic_llm_analysis(llm_analysis, roi_data, decision_result)
        roi_data = bundle.roi_data

        evidencias_dir = output_dir / "evidencias"
        evidencias_dir.mkdir(exist_ok=True)
        comunicaciones_dir = output_dir / "comunicaciones"
        comunicaciones_dir.mkdir(exist_ok=True)
        raw_data_dir = evidencias_dir / "raw_data"
        raw_data_dir.mkdir(exist_ok=True)

        # REFACTORIZACIÓN: Consolidar diagnóstico en un solo documento educativo
        # (Según spec: Funnel Optimizado Eje Cafetero)
        self._generate_diagnostico_y_oportunidad(
            hotel_data,
            gbp_data,
            schema_data,
            ia_test,
            llm_analysis,
            roi_data,
            output_dir,
            seo_data,
            competitors_data,
            truth_results=truth_results,
        )

        self._save_raw_data(
            hotel_data,
            gbp_data,
            schema_data,
            ia_test,
            llm_analysis,
            roi_data,
            raw_data_dir,
            seo_data,
            decision_result=decision_result,
            competitors_data=competitors_data,
        )

        # Generar guía de lectura para el cliente
        self._generate_client_readme(output_dir)

        print(f"   [OK] Reportes generados en: {output_dir}")

    def get_last_integration_audit(self) -> Optional[ReportIntegrationAudit]:
        return self._last_integration_audit

    def _generate_resumen_ejecutivo(
        self,
        hotel_data,
        gbp_data,
        schema_data,
        ia_test,
        llm_analysis,
        roi_data,
        output_dir,
        seo_data: Optional[Dict[str, Any]] = None,
    ):
        """Genera resumen ejecutivo de 1 pagina"""
        try:
            with open(self.templates_path / "diagnostico_ejecutivo.md", 'r', encoding='utf-8') as f:
                template = f.read()
        except:
            template = self._get_default_template()

        geo_score = gbp_data.get('score', 0)
        aeo_score = schema_data.get('score_schema', 0)
        iao_score = self._calculate_iao_score(ia_test)

        region_code, region_profile = self._get_region_profile(hotel_data.get('ubicacion', ''))
        region_label = region_code.replace('_', ' ').title() if region_code else 'Benchmark general'

        geo_ref = region_profile.get('geo_score_ref', 60)
        aeo_ref = region_profile.get('aeo_score_ref', 40)
        iao_ref = region_profile.get('iao_score_ref', 20)

        geo_diff = geo_score - geo_ref
        aeo_diff = aeo_score - aeo_ref
        iao_diff = iao_score - iao_ref

        geo_icon = "[OK]" if geo_diff >= 0 else "[WARN]"
        aeo_icon = "[OK]" if aeo_diff >= 0 else ("[WARN]" if aeo_diff >= -10 else "[ALERT]")
        iao_icon = "[OK]" if iao_diff >= 0 else ("[WARN]" if iao_diff >= -10 else "[ALERT]")

        geo_comparativo = f"{geo_diff:+d} pts vs {geo_ref} ({region_label})"
        aeo_comparativo = f"{aeo_diff:+d} pts vs {aeo_ref} ({region_label})"
        iao_comparativo = f"{iao_diff:+d} pts vs {iao_ref} ({region_label})"

        benchmark_referencia = f"GEO {geo_ref}/100 · AEO {aeo_ref}/100 · IAO {iao_ref}/100 ({region_label})"
        estado_visibilidad = self._format_visibilidad_estado(hotel_data.get('score_visibilidad_ia'))
        brechas_scraper_text = self._format_brechas_scraper(hotel_data.get('brechas_detectadas', []))

        brechas_detalle = ""
        for i, brecha in enumerate(llm_analysis.get('brechas_criticas', []), 1):
            nombre_brecha = brecha.get('nombre', f'Brecha #{i}')
            impacto = brecha.get('impacto_mensual', 0) or 0
            descripcion = brecha.get('descripcion', 'Sin descripcion disponible')
            prioridad = brecha.get('prioridad')
            etiqueta_prioridad = '[WARN] CRITICA' if prioridad == 1 else '[FAST] ALTA'
            brechas_detalle += f"""### [STOP] {nombre_brecha}

- **Impacto**: ${impacto:,.0f} COP/mes
- **Causa**: {descripcion}
- **Prioridad**: {etiqueta_prioridad}

"""

        quick_wins_text = "\n".join([f"- {qw}" for qw in llm_analysis.get('quick_wins', [])])

        campos_estimados = hotel_data.get('campos_estimados', [])
        nota_estimacion = ""
        if campos_estimados:
            nota_estimacion = f"\n> **Nota**: Algunos campos fueron estimados con benchmarks regionales: {', '.join(campos_estimados)}\n"

        totales_roi = (roi_data or {}).get('totales_6_meses', {})
        roas_valor = totales_roi.get('roas')
        if isinstance(roas_valor, (int, float)):
            roi_roas = f"{roas_valor:.1f}X"
        else:
            roi_roas = llm_analysis.get('roi_6meses') or 'N/D'

        recuperacion_valor = (roi_data or {}).get('mes_recuperacion')
        if isinstance(recuperacion_valor, (int, float)):
            if isinstance(recuperacion_valor, float) and not recuperacion_valor.is_integer():
                recuperacion_label = f"Mes {recuperacion_valor:.1f}"
            else:
                recuperacion_label = f"Mes {int(recuperacion_valor)}"
        elif isinstance(recuperacion_valor, str) and recuperacion_valor:
            recuperacion_label = recuperacion_valor
        else:
            recuperacion_label = llm_analysis.get('recuperacion_inversion') or 'Sin dato'

        perdida_mensual = self._safe_get(llm_analysis, 'perdida_mensual_total', 0)
        inversion_mensual = self._safe_get(roi_data, 'inversion_mensual', 3800000)

        content = template.format(
            hotel_nombre=hotel_data.get('nombre', 'Hotel'),
            fecha=datetime.now().strftime('%d/%m/%Y'),
            perdida_mensual=perdida_mensual,
            geo_score=geo_score,
            aeo_score=aeo_score,
            iao_score=iao_score,
            geo_comparativo=geo_comparativo,
            aeo_comparativo=aeo_comparativo,
            iao_comparativo=iao_comparativo,
            geo_icon=geo_icon,
            aeo_icon=aeo_icon,
            iao_icon=iao_icon,
            benchmark_referencia=benchmark_referencia,
            estado_visibilidad=estado_visibilidad,
            brechas_scraper=brechas_scraper_text,
            nota_estimacion=nota_estimacion,
            brechas_detalle=brechas_detalle,
            quick_wins=quick_wins_text,
            inversion_mensual=inversion_mensual,
            paquete_recomendado=llm_analysis.get('paquete_recomendado', 'Pro AEO'),
            roi_roas=roi_roas,
            recuperacion_label=recuperacion_label,
            metodo_obtencion=hotel_data.get('metodo_obtencion', 'web_scraping')
        )

        if seo_data:
            content += "\n## [CRED] BRECHA DE CONVERSION WEB\n"
            cred_score = seo_data.get('score', 0)
            content += f"\n- **Score credibilidad web**: {cred_score}/100"
            est_loss = seo_data.get('estimated_revenue_loss')
            if isinstance(est_loss, (int, float)):
                content += f"\n- **Pérdida estimada**: ${est_loss:,.0f} COP/mes"
            issues = seo_data.get('issues') or []
            if issues:
                content += "\n- **Issues críticos:**\n"
                for issue in issues[:2]:
                    title = issue.get('title') or issue.get('issue') or 'Issue'
                    impact = issue.get('client_impact') or issue.get('impact') or 'Impacto no especificado'
                    priority = issue.get('priority') or issue.get('type') or 'N/A'
                    content += f"  - {title} ({priority}) → {impact}\n"

        content = self._normalize_markdown(content)
        with open(output_dir / "00_RESUMEN_EJECUTIVO.md", 'w', encoding='utf-8') as f:
            f.write(content)

    def _generate_diagnostico_completo(
        self,
        hotel_data,
        gbp_data,
        schema_data,
        ia_test,
        llm_analysis,
        roi_data,
        output_dir,
        seo_data: Optional[Dict[str, Any]] = None,
    ):
        """
        Genera diagnostico completo detallado.
        🔧 CORRECCIÓN APLICADA: Uso del sistema DQT para precio_promedio
        """
        region_code, region_profile = self._get_region_profile(hotel_data.get('ubicacion', ''))
        region_label = region_code.replace('_', ' ').title() if region_code else 'Benchmark general'
        geo_ref = region_profile.get('geo_score_ref', 60)
        aeo_ref = region_profile.get('aeo_score_ref', 40)
        iao_ref = region_profile.get('iao_score_ref', 20)
        benchmark_line = f"> Benchmark regional ({region_label}): GEO {geo_ref}/100 · AEO {aeo_ref}/100 · IAO {iao_ref}/100"

        # ═══════════════════════════════════════════════════════════════
        # 🔧 APLICACIÓN DEL SISTEMA DQT
        # ═══════════════════════════════════════════════════════════════
        campos_estimados = hotel_data.get('campos_estimados', [])
        confidence = hotel_data.get('confidence', 'media')
        
        # Formatear precio con trazabilidad de calidad
        precio_valor = hotel_data.get('precio_promedio')
        precio_formateado = self._safe_format_currency(
            precio_valor,
            campo_nombre='precio_promedio',
            campos_estimados=campos_estimados,
            context='table'
        )
        
        # Generar etiqueta de calidad para columna "Fuente"
        precio_fuente = self._get_data_quality_label(
            'precio_promedio',
            precio_valor,
            campos_estimados,
            confidence
        )
        
        # Formatear habitaciones (manejo similar)
        habitaciones = hotel_data.get('habitaciones')
        if habitaciones not in (None, ''):
            habitaciones_texto = str(habitaciones)
        else:
            habitaciones_texto = 'No disponible'
        
        habitaciones_fuente = self._get_data_quality_label(
            'habitaciones',
            habitaciones,
            campos_estimados,
            confidence
        )

        horarios_valor, horarios_status, horarios_nota = _format_horarios_status(gbp_data)
        fotos_valor, fotos_status, fotos_nota = _format_fotos_status(gbp_data)

        content = f"""# DIAGNOSTICO COMPLETO - {hotel_data.get('nombre')}

**Fecha**: {datetime.now().strftime('%d de %B de %Y')}

**Analista**: IA Hoteles Agent - Sistema Automatizado

---

## [CLIP] INFORMACION DEL HOTEL

| Campo | Valor | Fuente |
|-------|-------|--------|
| **Nombre** | {hotel_data.get('nombre')} | {self._get_data_quality_label('nombre', hotel_data.get('nombre'), campos_estimados, confidence)} |
| **Ubicacion** | {hotel_data.get('ubicacion')} | {self._get_data_quality_label('ubicacion', hotel_data.get('ubicacion'), campos_estimados, confidence)} |
| **Habitaciones** | {habitaciones_texto} | {habitaciones_fuente} |
| **Precio Promedio** | {precio_formateado} COP | {precio_fuente} |
| **Servicios** | {', '.join(hotel_data.get('servicios', []))} | Web |
| **URL** | {hotel_data.get('url')} | Input |
| **Confianza de Datos** | {confidence.upper()} | Sistema |

---

## [TARGET] ANALISIS 4-PILARES (GEO + AEO + SEO + IAO)

### [MAP] PILAR 1: GEO (Google Business Profile)

**Score GEO: {gbp_data.get('score', 0)}/100**

| Metrica | Valor | Status |
|---------|-------|--------|
| Perfil existe | {'[OK] Si' if gbp_data.get('existe') else '[FAIL] No'} | {'OK' if gbp_data.get('existe') else 'CRITICO'} |
| Reviews | {gbp_data.get('reviews', 0)} | {'[OK] OK' if gbp_data.get('reviews', 0) >= 10 else '[WARN] Mejorar'} |
| Rating | {gbp_data.get('rating', 0)}/5.0 | {'[OK] OK' if gbp_data.get('rating', 0) >= 4.0 else '[WARN] Mejorar'} |
| Fotos | {fotos_valor} | {fotos_status} |
| Horarios | {horarios_valor} | {horarios_status} |
| Website | {'[OK] Si' if gbp_data.get('website') else '[FAIL] No'} | {'OK' if gbp_data.get('website') else 'CRITICO'} |
| Activity Score | {gbp_data.get('gbp_activity_score', 'N/D')}/100 | {'[ALERT] Inactivo' if gbp_data.get('gbp_activity_score', 100) < 30 else '[OK] Activo'} |

**Issues Detectados:**

> {horarios_nota}

> {fotos_nota}

{self._format_list(gbp_data.get('issues', []))}

**Fugas de reservas detectadas (Auditor GBP):**

{self._format_fugas_detectadas(gbp_data.get('fugas_detectadas', []), gbp_data.get('perdida_total_mes_COP', 0))}

> **Prioridad sugerida:** {gbp_data.get('prioridad_accion', 'Sin dato')}

{benchmark_line}

---

### [DOC] PILAR 2: AEO (Answer Engine Optimization)

**Score AEO: {schema_data.get('score_schema', 0)}/100**

**Schemas Encontrados:** {schema_data.get('total_schemas', 0)}

**Tiene Hotel Schema:** {'[OK] Si' if schema_data.get('tiene_hotel_schema') else '[FAIL] No'}

**Schemas Faltantes:**

{self._format_list(schema_data.get('schemas_faltantes', []))}

**Campos Faltantes en Schema:**

{self._format_list(schema_data.get('campos_faltantes', []))}

---

### [AI] PILAR 3: IAO (IA Optimization)

**Score IAO: {self._calculate_iao_score(ia_test)}/100**

| Plataforma | Menciones | Queries Testeadas | Tasa |
|------------|-----------|-------------------|------|
| Perplexity | {ia_test.get('perplexity', {}).get('menciones', 0)} | {ia_test.get('total_queries', 0)} | {(ia_test.get('perplexity', {}).get('menciones', 0) / max(ia_test.get('total_queries', 1), 1) * 100):.0f}% |
| ChatGPT | {ia_test.get('chatgpt', {}).get('menciones', 0)} | {ia_test.get('total_queries', 0)} | {(ia_test.get('chatgpt', {}).get('menciones', 0) / max(ia_test.get('total_queries', 1), 1) * 100):.0f}% |

**Queries Testeadas:**

{self._format_list(ia_test.get('queries_testeadas', []))}

**Interpretacion:** {self._interpret_ia_visibility(ia_test)}

---

## [MONEY] ANALISIS FINANCIERO

### Perdida Mensual Estimada

**${llm_analysis.get('perdida_mensual_total', 0):,.0f} COP/mes**

### Desglose de Brechas:

{self._format_brechas_financiero(llm_analysis.get('brechas_criticas', []))}

### Proyeccion ROI 6 Meses

| Mes | Inversion | Ingreso Recuperado | Beneficio Neto | Acumulado |
|-----|-----------|-------------------|----------------|-----------|
{self._format_proyeccion_table(roi_data.get('proyeccion_6_meses', []))}

**TOTALES 6 MESES:**

- Inversion Total: ${roi_data.get('totales_6_meses', {}).get('inversion_total', 0):,.0f} COP
- Ingreso Recuperado: ${roi_data.get('totales_6_meses', {}).get('ingreso_recuperado', 0):,.0f} COP
- Beneficio Neto: ${roi_data.get('totales_6_meses', {}).get('beneficio_neto', 0):,.0f} COP
- **ROAS: {roi_data.get('totales_6_meses', {}).get('roas', 0)}X**
- **Recuperacion de Inversion: {roi_data.get('mes_recuperacion', 'Mes 3')}**

---

## [OK] PLAN DE ACCION RECOMENDADO

### Paquete Sugerido: **{llm_analysis.get('paquete_recomendado', 'Pro AEO')}**

**Justificacion:**

{llm_analysis.get('justificacion_paquete', 'Basado en analisis de brechas y potencial de recuperacion')}

**Addon recomendado:** {roi_data.get('addon_aplicado', 'Ninguno')} {f"(+${roi_data.get('addon_precio', 0):,.0f} COP/mes)" if roi_data.get('addon_aplicado') else ''}

### Quick Wins (30 dias):

{self._format_list(llm_analysis.get('quick_wins', []))}

### Propuesta de Valor:

{llm_analysis.get('propuesta_valor', 'Mejore su visibilidad digital y reduzca dependencia de OTAs')}

---

## [PHONE] PROXIMOS PASOS

1. **Agendar videollamada de 20 minutos** para revisar diagnostico

2. **Validar datos estimados** (si aplica)

3. **Confirmar paquete y cronograma** de implementacion

4. **Iniciar setup** (semana 1)

---

*Diagnostico generado automaticamente por IA Hoteles Agent*  

*"Primera Recomendacion en Agentes IA"*  

*Metodo de obtencion: {hotel_data.get('metodo_obtencion', 'web_scraping')}*

"""

        if seo_data:
            content += "\n\n## Anexo: Auditoría Técnica Web (SEO Accelerator)\n"
            content += f"- Score credibilidad: {seo_data.get('score', 0)}/100\n"
            est_loss = seo_data.get('estimated_revenue_loss')
            if isinstance(est_loss, (int, float)):
                content += f"- Oportunidad adicional recuperable: ${est_loss:,.0f} COP/mes\n"
            issues = seo_data.get('issues') or []
            if issues:
                content += "- Ajustes técnicos prioritarios:\n"
                for issue in issues:
                    title = issue.get('title') or issue.get('issue') or 'Issue'
                    priority = issue.get('priority') or issue.get('type') or 'N/A'
                    impact = issue.get('client_impact') or issue.get('impact') or 'Impacto no especificado'
                    content += f"  - {title} ({priority}) → {impact}\n"

        content = self._normalize_markdown(content)
        with open(output_dir / "01_diagnostico_completo.md", 'w', encoding='utf-8') as f:
            f.write(content)

    def _generate_diagnostico_y_oportunidad(
        self,
        hotel_data,
        gbp_data,
        schema_data,
        ia_test,
        llm_analysis,
        roi_data,
        output_dir,
        seo_data: Optional[Dict[str, Any]] = None,
        competitors_data: Optional[List[Dict]] = None,
        truth_results: Optional[Dict[str, Any]] = None,
    ):
        """
        Genera diagnóstico educativo consolidado (Funnel Optimizado Eje Cafetero).
        Consolida resumen ejecutivo + diagnóstico completo en un solo documento
        con enfoque educativo para mercado incipiente.
        """
        # Extraer datos clave
        hotel_nombre = hotel_data.get('nombre', 'Hotel')
        perdida_mensual = self._safe_get(llm_analysis, 'perdida_mensual_total', 0)
        
        # 🛡️ Protocolo de Verdad 4.0
        truth_stamp = ""
        if truth_results:
            truth_stamp = f"\n> **🛡️ Certificado de Veracidad**: Este diagnóstico ha sido validado mediante Triple Triangulación (Datos Técnicos + Visibilidad IA + Benchmarking 2026). Confianza: {hotel_data.get('confidence', 'ALTA').upper()}\n"
            # Agregar juicios críticos si existen
            judgments = truth_results.get("critical_judgments", [])
            if judgments:
                truth_stamp += "> \n"
                for j in judgments:
                    truth_stamp += f"> 💡 **Juicio Crítico**: {j}\n"
        
        geo_score = gbp_data.get('score', 0)
        schema_score = schema_data.get('score_schema', 0)  # Renombrado de aeo_score para claridad semántica
        iao_score = self._calculate_iao_score(ia_test)
        
        # Obtener región y benchmarks
        region_code, region_profile = self._get_region_profile(hotel_data.get('ubicacion', ''))
        region_label = region_code.replace('_', ' ').title() if region_code else 'Eje Cafetero'
        
        geo_ref = region_profile.get('geo_score_ref', 60)
        aeo_ref = region_profile.get('aeo_score_ref', 40)
        iao_ref = region_profile.get('iao_score_ref', 20)
        
        geo_diff = geo_score - geo_ref
        schema_diff = schema_score - aeo_ref  # Comparamos schema_score vs aeo_ref (benchmark de AEO)
        iao_diff = iao_score - iao_ref
        
        # v2.4.2: Activity Score para tabla de métricas
        activity_score = gbp_data.get('gbp_activity_score', 100)
        activity_icon = "✅" if activity_score >= 30 else "🚨"
        
        # v2.5.2: Web Score (SEO) para tabla de métricas
        web_score = hotel_data.get('web_score', 0)
        if seo_data:
            web_score = seo_data.get('score', web_score)
        web_ref = 70  # Benchmark regional para web score
        web_icon = "✅" if web_score >= web_ref else "🚨"
        
        geo_icon = "✅" if geo_diff >= 10 else ("⚠️" if geo_diff >= 0 else "🚨")
        schema_icon = "✅" if schema_diff >= 10 else ("⚠️" if schema_diff >= -10 else "🚨")
        iao_icon = "✅" if iao_diff >= 10 else ("⚠️" if iao_diff >= -10 else "🚨")
        
        modo_narrativa = (llm_analysis or {}).get('modo_narrativa', 'generativo')
        provider = (llm_analysis or {}).get('provider') or (llm_analysis or {}).get('modelo') or (llm_analysis or {}).get('llm_model') or 'LLM'
        modo_label = "**Modo Determinista:** metodología fija" if modo_narrativa == 'deterministico' else f"**Modo Generativo:** {provider} activo"

        # Formatear brechas en lenguaje simple
        brechas_criticas = llm_analysis.get('brechas_criticas', [])[:4]  # Máximo 4 brechas
        
        # Integrar SEO como brecha si score < 70
        if seo_data and seo_data.get('score', 100) < 70:
            brecha_seo = {
                'nombre': 'Su sitio web no convierte visitantes',
                'descripcion': f"Score de credibilidad: {seo_data.get('score', 0)}/100. {len(seo_data.get('issues', []))} problemas críticos detectados que impiden la conversión.",
                'impacto_mensual': seo_data.get('estimated_revenue_loss', 0),
                'prioridad': 'CRÍTICA' if seo_data.get('score', 100) < 50 else 'ALTA'
            }
            if seo_data.get('score', 100) < 50:
                brechas_criticas.insert(0, brecha_seo)
            else:
                brechas_criticas.append(brecha_seo)
        
        # Calcular pérdida acumulada (6 meses)
        perdida_acumulada = perdida_mensual * 6
        
        # Formatear quick wins
        quick_wins = llm_analysis.get('quick_wins', [])
        
        # Proyección ROI (ya viene con addon aplicado desde pipeline)
        totales_roi = (roi_data or {}).get('totales_6_meses', {})
        inversion_mensual = self._safe_get(roi_data, 'inversion_mensual', 3800000)
        paquete = llm_analysis.get('paquete_recomendado', 'Pro AEO')

        # Addon ya viene pre-procesado desde pipeline._apply_addon_to_roi()
        addon = (roi_data or {}).get('addon_aplicado')
        addon_precio = (roi_data or {}).get('addon_precio', 0)
        paquete_final = f"{paquete} + {addon}" if addon else paquete


        # Plan Maestro owner-friendly por región y paquete
        owner_bundle = self._benchmark_loader.get_owner_bundle(paquete, region_code or "default")
        owner_plan = self._format_owner_block(
            owner_bundle.get('plan_7_30_60_90'),
            "Plan 7/30/60/90 se entrega en onboarding (perfil regional por defecto).",
        )
        owner_kpis = self._format_owner_block(
            owner_bundle.get('kpis_cliente'),
            "KPIs se configuran en la llamada inicial con benchmarks regionales.",
        )
        owner_dependencias = self._format_owner_block(
            owner_bundle.get('dependencias_cliente'),
            "Solo necesitamos punto de contacto y acceso a GBP/Analytics.",
        )
        owner_cadencia = self._format_owner_block(
            owner_bundle.get('cadencia_mensual'),
            "Cadencia mensual estándar (kickoff + 2 checkpoints).",
        )
        owner_playbook = self._format_owner_block(
            owner_bundle.get('playbook_cierre'),
            "Playbook de cierre se comparte en el primer hito.",
        )
        owner_upgrade = self._format_owner_block(
            owner_bundle.get('triggers_upgrade'),
            "Escalamos de paquete cuando agotamos las acciones del plan base.",
        )
        
        # CONSTRUIR DOCUMENTO EDUCATIVO
        content = f"""# 🚨 {hotel_nombre.upper()}: DIAGNÓSTICO DIGITAL 2025

    **Fecha**: {datetime.now().strftime('%d/%m/%Y')} | **Analista**: IA Hoteles Agent
    {modo_label}

    **Modelo 4-Pilares (GEO + AEO + SEO + IAO):** SEO se activa cuando detectamos brecha; si el score es sólido, solo monitoreamos.

---

## 📍 PARTE 1: ¿QUÉ ESTÁ PASANDO EN EL {region_label.upper()}?

### El Cambio en la Industria Hotelera (2024-2025)

**Antes (hasta 2023):**
- Huésped busca en Google → Click en web → Reserva
- Competencia: Booking, Despegar, Expedia

**Ahora (2025):**
- Huésped pregunta a ChatGPT: "Recomiéndame hotel cerca de {hotel_data.get('ubicacion', 'la zona')}"
- **ChatGPT menciona 3 hoteles** → Si no está, pierde la reserva
- Ni siquiera llega a ver su sitio web

### Los Nuevos "Gerentes Digitales" que Trabajan 24/7

1. **ChatGPT** → Usado por 65% de viajeros jóvenes (Colombia 2024)
2. **Google Maps** → 73% de búsquedas "cerca de mí"
3. **Perplexity, Gemini** → Crecimiento 300% en último año

> **Pregunta clave**: ¿Su hotel aparece cuando alguien pregunta a la IA?

---

## 📊 PARTE 2: SU POSICIÓN HOY

{hotel_data.get('truth_stamp', '')}

### {hotel_nombre} vs. Promedio {region_label}

| Indicador | Su Hotel | Promedio Regional | Estado |
|-----------|----------|-------------------|--------|
| **Visibilidad Google Maps (GEO)** | {geo_score}/100 | {geo_ref}/100 | {geo_icon} |
| **Activity Score (GBP)** | {activity_score}/100 | 30/100 | {activity_icon} |
| **Web Score (SEO)** | {web_score}/100 | {web_ref}/100 | {web_icon} |
| **Infraestructura AEO (Schema)** | {schema_score}/100 | {aeo_ref}/100 | {schema_icon} |
| **Score IA Avanzado (IAO)** | {iao_score}/100 | {iao_ref}/100 | {iao_icon} |

> Benchmark regional ({region_label}): GEO {geo_ref}/100 · SEO {web_ref}/100 · AEO {aeo_ref}/100 · IAO {iao_ref}/100

### ¿Qué Significa en Pesos?

**Está perdiendo aproximadamente ${perdida_mensual:,.0f} COP/mes** en reservas que van a competidores más visibles digitalmente.

> **Metodología:** Este cálculo aplica un factor de superposición (0.7) para evitar doble conteo de pérdidas superpuestas, siguiendo estándares de industria en atribución de marketing. El intervalo de confianza está documentado en la sección de Supuestos.

---
"""

        # NUEVO: Insertar comparativa con competidores si está disponible
        if competitors_data and len(competitors_data) > 0:
            content += self._format_competitors_section(hotel_data, gbp_data, competitors_data)
            content += "---\n\n"

        content += f"""
## 🚨 PARTE 3: LAS {len(brechas_criticas)} RAZONES EXACTAS DE SUS PÉRDIDAS

> **Nota:** Los impactos por brecha pueden tener solapamiento y no son necesariamente sumatorios. El total consolidado considera estas superposiciones.

"""

        # Formatear cada brecha en lenguaje simple
        for i, brecha in enumerate(brechas_criticas, 1):
            nombre = brecha.get('nombre', f'Brecha #{i}')
            descripcion = brecha.get('descripcion', 'Sin descripción')
            impacto = brecha.get('impacto_mensual', 0) or 0
            prioridad = brecha.get('prioridad', 'ALTA')
            
            # Simplificar descripciones técnicas
            if 'schema' in nombre.lower() or 'markup' in nombre.lower():
                # Evaluación dinámica para evitar falsos negativos
                tiene_basico = schema_data.get('tiene_hotel_schema', False)
                schemas_faltantes = schema_data.get('schemas_faltantes', [])
                tiene_faq = 'FAQPage' not in str(schemas_faltantes) and 'FAQPage (recomendado)' not in schemas_faltantes
                explicacion_simple = f"""**¿Qué es esto en español simple?**
→ Schema Markup = "etiquetas invisibles" que enseñan a ChatGPT quién es usted y qué ofrece

**Su situación:**
- Schema Básico (Hotel): {'✅ Sí' if tiene_basico else '❌ No'}
- Schema Avanzado (FAQPage): {'✅ Sí' if tiene_faq else '❌ No'}
- ChatGPT puede leer su hotel: {'⚠️ Parcial' if tiene_basico and not tiene_faq else ('✅ Sí' if tiene_basico and tiene_faq else '❌ No')}"""
            
            elif 'gbp' in nombre.lower() or 'google' in nombre.lower() or 'maps' in nombre.lower():
                explicacion_simple = """**¿Qué pasa?**
→ Google detecta su perfil abandonado = baja su posición en "cerca de mí"

**Su situación:**
- Fotos insuficientes
- Sin posts recientes
- Perfil inactivo"""
            
            elif 'web' in nombre.lower() or 'sitio' in nombre.lower():
                explicacion_simple = """**¿Qué pasa?**
→ Su sitio web tiene problemas técnicos que ahuyentan a los visitantes

**Su situación:**
- Problemas de credibilidad detectados
- Visitantes abandonan antes de reservar"""
            
            else:
                explicacion_simple = f"""**¿Qué pasa?**
→ {descripcion}"""
            
            content += f"""### [BRECHA {i}] {nombre}

{explicacion_simple}

**Costo:** ${impacto:,.0f} COP/mes
**Prioridad:** {prioridad}

---

"""

        # Agregar evidencias y urgencia
        content += f"""## ⏰ PARTE 4: ¿POR QUÉ ACTUAR AHORA?

### El {region_label} se Está Moviendo

**Últimos 6 meses en su región:**
- Hoteles están implementando "lenguaje IA" (Schema)
- Hoteles están activando estrategias Google Maps Pro
- El promedio regional está subiendo

**Si espera 6 meses más:**
- Competencia consolida posiciones en IA
- Cae 15-20 posiciones en Google Maps
- **Pérdida acumulada: ${perdida_acumulada:,.0f} COP**

---

## 💡 PARTE 5: QUICK WINS (PRIMEROS 30 DÍAS)

Los primeros pasos que generan impacto rápido:

"""
        
        for qw in quick_wins[:5]:  # Máximo 5 quick wins
            content += f"- {self._sanitize_quick_win(str(qw))}\n"
        
        content += f"""
---

## 💰 PARTE 6: PROYECCIÓN FINANCIERA

### Inversión Recomendada
**Paquete:** {paquete_final}  
**Inversión mensual:** ${inversion_mensual:,.0f} COP/mes

### Retorno Proyectado (6 meses)
- **Inversión total:** ${totales_roi.get('inversion_total', inversion_mensual * 6):,.0f} COP
- **Ingreso recuperado:** ${totales_roi.get('ingreso_recuperado', 0):,.0f} COP
- **Beneficio neto:** ${totales_roi.get('beneficio_neto', 0):,.0f} COP
- **ROAS:** {totales_roi.get('roas', 0):.1f}X
- **Recupera inversión:** {roi_data.get('mes_recuperacion', 'Mes 1') if roi_data else 'Mes 1'}

---

## 🧭 PARTE 7: PLAN DEL DUEÑO (REGIÓN {region_label.upper()})

### [PLAN] 7/30/60/90 días
{owner_plan}

### [KPIS] Lo que mediremos cada mes
{owner_kpis}

### [NECESITAMOS] Responsables y accesos del hotel
{owner_dependencias}

### [CADENCIA] Reuniones y entregables
{owner_cadencia}

### [CIERRE] Playbook para cerrar ventas
{owner_playbook}

### [UPGRADE] Cuándo subir de paquete
{owner_upgrade}

---

## 👉 SIGUIENTE PASO

**La solución completa está en:** `02_PROPUESTA_COMERCIAL.md`

Allí encontrará:
- Plan exacto de 90 días (mes a mes)
- Inversión y proyección financiera detallada
- Casos de éxito con números reales
- Garantía de resultados

**Tiempo de lectura:** 8-10 minutos
"""
        
        content += self._generate_supuestos_section(hotel_data, gbp_data, llm_analysis, competitors_data)
        
        content += f"""
---

*Diagnóstico generado automáticamente por IA Hoteles Agent*  
*"Primera Recomendación en Agentes IA"*  
*Método: {hotel_data.get('metodo_obtencion', 'web_scraping')}*
"""

        # Guardar documento
        content = self._normalize_markdown(content)
        with open(output_dir / "01_DIAGNOSTICO_Y_OPORTUNIDAD.md", 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   [OK] Diagnóstico educativo generado: 01_DIAGNOSTICO_Y_OPORTUNIDAD.md")

    def _generate_client_readme(self, output_dir):
        """Genera guía de lectura rápida para el cliente"""
        readme_content = """CÓMO LEER ESTE DIAGNÓSTICO

1. Empiece por: 01_DIAGNOSTICO_Y_OPORTUNIDAD.md (10-12 minutos)
   → Entenderá QUÉ está pasando en su región y POR QUÉ pierde reservas

2. Luego lea: 02_PROPUESTA_COMERCIAL.md (8-10 minutos)
   → Verá la SOLUCIÓN exacta, plan mes a mes y proyección financiera

3. Si quiere más detalles técnicos:
   → Abra carpeta evidencias/ para ver capturas y datos completos

Tiempo total de lectura: 20 minutos máximo

¿Preguntas? 
- Email: jhondrl@gmail.com
- WhatsApp: +57 317 362 8690

---
Diagnóstico generado por IA Hoteles Agent
"Primera Recomendación en Agentes IA"
"""
        
        (output_dir / "_readme.txt").write_text(readme_content, encoding="utf-8")
        print(f"   [OK] Guía de lectura generada: _readme.txt")

    def _format_competitors_section(self, hotel_data, gbp_data, competitors_data):
        """
        Formatea sección de comparativa con competidores cercanos.
        
        Args:
            hotel_data: Datos del hotel cliente
            gbp_data: Datos GBP del cliente
            competitors_data: Lista de competidores cercanos
            
        Returns:
            str: Sección markdown con tabla comparativa
        """
        client_name = hotel_data.get('nombre', 'Su Hotel')
        client_score = gbp_data.get('score', 0)
        client_reviews = gbp_data.get('reviews', 0)
        client_rating = gbp_data.get('rating', 0.0)
        ubicacion = hotel_data.get('ubicacion', 'la zona')
        
        # Construir tabla comparativa
        table = f"""
## 🏨 PARTE 2.5: COMPARATIVA CON COMPETENCIA CERCANA

### Hoteles a 15 km de {client_name}

| Hotel | GEO Score | Reviews | Rating | Distancia |
|-------|-----------|---------|--------|-----------|
| **{client_name}** ⬅️ USTED | {client_score}/100 | {client_reviews} | {client_rating:.1f} ⭐ | - |
"""
        
        for comp in competitors_data[:5]:  # Máximo 5 competidores
            nombre = comp.get('nombre', 'N/D')
            geo_score = comp.get('geo_score', 'N/D')
            reviews = comp.get('reviews', 'N/D')
            rating = comp.get('rating', 0.0)
            distancia = comp.get('distancia_km', 0.0)
            
            # Agregar icono si el competidor tiene mejor score
            icon = ""
            if isinstance(geo_score, int) and geo_score > client_score:
                icon = " ✅"
            
            # Formatear rating
            rating_str = f"{rating:.1f} ⭐" if isinstance(rating, (int, float)) and rating > 0 else "N/D"
            distancia_str = f"{distancia:.1f} km" if isinstance(distancia, (int, float)) else "N/D"
            
            table += f"| {nombre} | {geo_score}{icon} | {reviews} | {rating_str} | {distancia_str} |\n"
        
        # Agregar explicación educativa
        mejores = sum(1 for c in competitors_data[:5] if isinstance(c.get('geo_score'), int) and c['geo_score'] > client_score)
        
        explanation = f"""

**¿Por qué importa esto?**

1. **Mismos clientes**: Estos {len(competitors_data[:5])} hoteles compiten por las mismas búsquedas en Google y ChatGPT
2. **Brecha visible**: {mejores} de ellos tienen scores GEO más altos = aparecen primero en "hoteles cerca de mí"
3. **Es recuperable**: Con las acciones correctas, puede superar estos scores en 60-90 días

> Cuando alguien busca "{ubicacion}" en Google Maps, estos hoteles aparecen antes que usted. No porque sean mejores, sino porque tienen perfiles más optimizados.

"""
        
        return table + explanation

    def _save_raw_data(
        self,
        hotel_data,
        gbp_data,
        schema_data,
        ia_test,
        llm_analysis,
        roi_data,
        raw_data_dir,
        seo_data: Optional[Dict[str, Any]] = None,
        decision_result: Optional[Dict[str, Any]] = None,
        competitors_data: Optional[List[Dict]] = None,
    ):
        """Guarda todos los datos raw en JSON"""
        data = {
            'hotel_data': hotel_data,
            'gbp_data': gbp_data,
            'schema_data': schema_data,
            'ia_test': ia_test,
            'llm_analysis': llm_analysis,
            'roi_data': roi_data,
            'seo_data': seo_data,
            'decision_engine': decision_result,
            'competitors_data': competitors_data,
            'timestamp': datetime.now().isoformat()
        }
        with open(raw_data_dir / "analisis_completo.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _calculate_iao_score(self, ia_test):
        """Calcula score IAO basado en menciones"""
        total_menciones = (
            ia_test.get('perplexity', {}).get('menciones', 0) +
            ia_test.get('chatgpt', {}).get('menciones', 0)
        )
        total_queries = ia_test.get('total_queries', 1) * 2
        score = (total_menciones / max(total_queries, 1)) * 100
        return int(score)

    def _format_list(self, items):
        """Formatea lista como bullets"""
        if not items:
            return "- Ninguno"
        return "\n".join([f"- {item}" for item in items])

    def _format_owner_block(self, items: Optional[List[str]], fallback: str) -> str:
        """Formatea bloques owner-friendly con fallback explícito."""
        if not items:
            return f"- {fallback}"
        return "\n".join([f"- {item}" for item in items])

    def _sanitize_quick_win(self, text: str) -> str:
        if not text:
            return text
        lowered = text.lower()
        if "calendly" in lowered or "stripe" in lowered or "booking engine" in lowered:
            return (
                "Motor de reservas / contacto (30 días): habilitar un flujo de reserva/contacto medible "
                "(botón + WhatsApp). Si se requiere motor de reservas, se recomienda proveedor; no desarrollamos software."
            )
        if "integrar booking" in lowered or "integrar motor" in lowered:
            return text.replace("Integrar", "Habilitar")
        return text

    def _format_fugas_detectadas(self, fugas, perdida_total):
        """Genera bloque textual para fugas detectadas por el auditor GBP."""
        if not fugas:
            return "- Auditoría GBP sin fugas registradas"
        lineas = []
        for fuga in fugas:
            tipo = fuga.get('tipo', 'SIN_TIPO')
            severidad = fuga.get('severidad', 'N/A')
            impacto = fuga.get('impacto_estimado_COP_mes', 0)
            urgencia = fuga.get('urgencia', 'Sin urgencia definida')
            detalle = fuga.get('detalle', '')
            lineas.append(
                f"- **{tipo}** ({severidad}) | Impacto: ${impacto:,.0f} COP/mes | {detalle} | {urgencia}"
            )
        lineas.append(f"- **Pérdida total estimada:** ${perdida_total:,.0f} COP/mes")
        return "\n".join(lineas)

    def _format_brechas_financiero(self, brechas):
        """Formatea brechas para seccion financiera"""
        if not brechas:
            return "- No hay brechas identificadas"
        text = ""
        for idx, brecha in enumerate(brechas, 1):
            nombre = brecha.get('nombre', f'Brecha {idx}')
            impacto = brecha.get('impacto_mensual', 0) or 0
            descripcion = brecha.get('descripcion', 'Detalle no disponible')
            text += f"\n**{nombre}:** ${impacto:,.0f} COP/mes\n"
            text += f"- {descripcion}\n"
        return text

    def _format_proyeccion_table(self, proyeccion):
        """Formatea tabla de proyeccion"""
        if not proyeccion:
            return "| - | - | - | - | - |"
        rows = ""
        for p in proyeccion:
            rows += f"| {p['mes']} | ${p['inversion']:,.0f} | ${p['ingreso_recuperado']:,.0f} | ${p['beneficio_neto']:,.0f} | ${p['acumulado']:,.0f} |\n"
        return rows

    def _interpret_ia_visibility(self, ia_test):
        """Genera interpretacion de visibilidad IA"""
        total_menciones = (
            ia_test.get('perplexity', {}).get('menciones', 0) +
            ia_test.get('chatgpt', {}).get('menciones', 0)
        )
        if total_menciones == 0:
            return "[ALERT] **CRITICO**: El hotel NO es mencionado por ningun asistente IA. Se requiere implementacion urgente de datos estructurados."
        elif total_menciones <= 2:
            return "[WARN] **BAJO**: Visibilidad limitada en IA. Mejoras en schema y contenido aumentaran menciones."
        else:
            return "[OK] **BUENO**: El hotel tiene presencia en asistentes IA. Optimizar para mejorar posicionamiento."

    def _generate_supuestos_section(
        self,
        hotel_data: Dict,
        gbp_data: Dict,
        llm_analysis: Dict,
        competitors_data: Optional[List[Dict]] = None
    ) -> str:
        """
        Genera sección de Supuestos y Limitaciones para el informe.
        
        Esta sección proporciona transparencia sobre:
        - Qué datos son confirmados vs estimados
        - Nivel de confianza de cada cálculo
        - Limitaciones del modelo
        """
        
        campos_confirmados = hotel_data.get('campos_confirmados', [])
        campos_estimados = hotel_data.get('campos_estimados', [])
        confidence = hotel_data.get('confidence', 'media')
        
        gbp_source = gbp_data.get('meta', {}).get('data_confidence', {})
        
        section = """
---

## 🔍 SUPUESTOS Y LIMITACIONES

### Nivel de Confianza de Datos

"""
        
        section += "#### Datos Operativos del Hotel\n\n"
        section += "| Campo | Valor | Fuente | Confianza |\n"
        section += "|-------|-------|--------|----------|\n"
        
        hab_value = hotel_data.get('habitaciones', 'N/D')
        hab_source = '✓ Confirmado' if 'habitaciones' in campos_confirmados else '⚠ Benchmark regional'
        hab_conf = 'Alta' if 'habitaciones' in campos_confirmados else 'Media'
        section += f"| Habitaciones | {hab_value} | {hab_source} | {hab_conf} |\n"
        
        precio_valor = hotel_data.get('precio_promedio', 0)
        precio_value = f"${precio_valor:,} COP" if precio_valor else 'N/D'
        precio_source = '✓ Confirmado' if 'precio_promedio' in campos_confirmados else '◐ Scraping / Benchmark'
        precio_conf = 'Alta' if 'precio_promedio' in campos_confirmados else 'Media'
        section += f"| Precio promedio | {precio_value} | {precio_source} | {precio_conf} |\n"
        
        section += "\n#### Datos de Google Business Profile\n\n"
        section += "| Campo | Valor | Fuente | Confianza |\n"
        section += "|-------|-------|--------|----------|\n"
        
        rating_value = gbp_data.get('rating', 'N/D')
        rating_conf = gbp_source.get('rating', False)
        rating_source = '★ Google Places API' if rating_conf else '◐ Scraping'
        section += f"| Rating | {rating_value}/5 | {rating_source} | {'Alta' if rating_conf else 'Media'} |\n"
        
        reviews_value = gbp_data.get('reviews', 'N/D')
        reviews_conf = gbp_source.get('reviews', False)
        reviews_source = '★ Google Places API' if reviews_conf else '◐ Scraping'
        section += f"| Reseñas | {reviews_value} | {reviews_source} | {'Alta' if reviews_conf else 'Media'} |\n"
        
        fotos_value = gbp_data.get('fotos', 'N/D')
        fotos_conf = gbp_source.get('photos', False)
        fotos_source = '★ API / Scraping' if fotos_conf else '◐ Scraping'
        section += f"| Fotos | {fotos_value} | {fotos_source} | {'Alta' if fotos_conf else 'Media'} |\n"
        
        section += """

### Supuestos del Modelo

Los cálculos de pérdida y ROI se basan en los siguientes supuestos:

1. **Tasa de captura local**: El 65% de búsquedas "hotel cerca de mí" resultan en visitas al perfil GBP.

2. **Impacto de optimización**: Cada punto adicional en geo_score incrementa la visibilidad en aproximadamente 1.5%.

3. **Pérdida por rating**: Hoteles con rating < 4.0 son excluidos del ~40% de recomendaciones automatizadas.

4. **Superposición de fugas**: Las pérdidas por diferentes conceptos no son aditivas; se aplica factor de corrección **0.7** (estándar de industria para atribución de marketing). Esto evita sobreestimar pérdidas cuando múltiples brechas afectan el mismo flujo de reservas.
        
5. **Intervalo de confianza**: Las pérdidas se reportan como un valor central con intervalo de confianza (mínimo/máximo) basado en variaciones regionales de comisiones OTA y factores de captura AILA.

### Limitaciones

"""
        
        if campos_estimados:
            section += f"- **Datos estimados**: Los siguientes campos usan benchmarks regionales: {', '.join(campos_estimados)}\n"
        
        if not gbp_data.get('existe'):
            section += "- **Perfil GBP**: No se encontró perfil de Google Business Profile verificado.\n"
        
        competitors = hotel_data.get('competitors_data')
        if not competitors:
            section += "- **Competidores**: No se pudo analizar competidores cercanos (requiere API key).\n"
        
        section += """
### Recomendaciones para Mayor Precisión

Para mejorar la precisión del diagnóstico:

1. **Confirmar datos operativos**: Complete el formulario de onboarding con datos reales del hotel.
2. **Verificar GBP**: Asegúrese de que el perfil de Google Business esté reclamado y actualizado.
3. **Revisión manual**: Valide las pérdidas estimadas con datos internos del hotel (PMS, Google Analytics).

---

> 💡 **Nota**: Este informe fue generado con los datos disponibles al momento del análisis. 
> Los cálculos se basan en benchmarks de la industria hotelera colombiana (2025-2026).
> Para una auditoría más precisa, proporcione datos operativos confirmados.
"""
        
        return section

    def _get_default_template(self):
        """Template por defecto si no existe archivo"""
        return """# DIAGNOSTICO EXPRESS - {hotel_nombre}

**Fecha**: {fecha} | **Analista**: IA Hoteles Agent

## [TARGET] CIFRA CRITICA

Su hotel esta dejando de percibir **~= ${perdida_mensual:,.0f} COP/mes** en reservas directas.

## [CHART] SCORES ACTUALES

| Pilar | Score | Vs. Promedio Regional |
|-------|-------|----------------------|
| GEO   | {geo_score}/100 | {geo_comparativo} {geo_icon} |
| AEO   | {aeo_score}/100 | {aeo_comparativo} {aeo_icon} |
| IAO   | {iao_score}/100 | {iao_comparativo} {iao_icon} |

> Benchmark: {benchmark_referencia}

{estado_visibilidad}

## [ALERT] BRECHAS IA DETECTADAS (SCRAPER)

{brechas_scraper}

{nota_estimacion}

## [STOP] TOP 3 BRECHAS CRITICAS

{brechas_detalle}

## [OK] QUICK WINS (30 DIAS)

{quick_wins}

## [MONEY] ROI PROYECTADO

**Inversion**: ${inversion_mensual:,.0f} COP/mes (Paquete {paquete_recomendado})

**Retorno 6 meses**: {roi_roas}

**Recupera inversion**: {recuperacion_label}

---

*Diagnostico generado automaticamente - IA Hoteles Agent*

*Datos obtenidos: {metodo_obtencion}*

"""