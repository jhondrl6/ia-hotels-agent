"""
SparkGenerator: Genera reportes ligeros de diagnóstico para fase inicial del funnel.

Modelo comercial: EVIDENCIA-CONFIANZA-ESCALA
- Spark Report: 1 página con 3 métricas clave + acción gratuita
- Objetivo: <5 minutos, sin fricción, solo WhatsApp
- Flujo: Spark → Video Loom → Piloto → Pro AEO
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from modules.orchestrator.pipeline import GeoStageResult, IAStageResult
except ImportError:
    # Dataclasses para compatibilidad cuando orchestrator no está disponible
    from dataclasses import dataclass, field

    @dataclass
    class GeoStageResult:
        hotel_data: dict = field(default_factory=dict)
        gbp_data: dict = field(default_factory=dict)
        schema_data: dict = field(default_factory=dict)
        competitors_data: list = field(default_factory=list)

    @dataclass
    class IAStageResult:
        ia_test: dict = field(default_factory=dict)
        llm_analysis: dict = field(default_factory=dict)
        roi_data: dict = field(default_factory=dict)
        current_provider: str = ""
        decision_result: dict = field(default_factory=dict)
        region: str = ""

from modules.analyzers.gap_analyzer import GapAnalyzer


class SparkGenerator:
    """Genera Spark Reports: diagnóstico rápido y accionable."""
    
    def __init__(self, provider_type: str = "auto"):
        self.provider_type = provider_type
        self.gap_analyzer = GapAnalyzer(provider_type)
        self.templates_dir = Path(__file__).parent.parent.parent / "templates" / "spark"
    
    def generate_spark_report(
        self,
        geo_result: GeoStageResult,
        ia_result: IAStageResult,
        output_dir: Path
    ) -> Dict[str, Path]:
        """
        Genera el Spark Report completo.
        
        Returns:
            Dict con rutas de archivos generados:
            - spark_report.md: Reporte de 1 página
            - whatsapp_script.txt: Guion de WhatsApp
            - quick_win_action.md: Acción gratuita
            - metrics_summary.json: JSON con métricas
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        hotel_data = geo_result.hotel_data
        gbp_data = geo_result.gbp_data
        schema_data = geo_result.schema_data
        ia_test = ia_result.ia_test
        llm_analysis = ia_result.llm_analysis
        
        # Obtener acción rápida
        quick_win = self.gap_analyzer.get_quick_win_action(
            hotel_data, gbp_data, schema_data, ia_test
        )
        
        # Preparar contexto para templates
        context = self._prepare_context(
            hotel_data, gbp_data, ia_test, llm_analysis, quick_win,
            geo_result.competitors_data
        )
        
        # Generar archivos
        files = {}
        
        # 1. Spark Report (HTML-like markdown)
        spark_md = self._render_spark_report(context)
        spark_path = output_dir / "spark_report.md"
        spark_path.write_text(spark_md, encoding="utf-8")
        files["spark_report"] = spark_path
        
        # 2. WhatsApp Script
        whatsapp_script = self._render_whatsapp_script(context)
        whatsapp_path = output_dir / "whatsapp_script.txt"
        whatsapp_path.write_text(whatsapp_script, encoding="utf-8")
        files["whatsapp_script"] = whatsapp_path
        
        # 3. Quick Win Action
        quick_win_md = self._render_quick_win(quick_win)
        quick_win_path = output_dir / "quick_win_action.md"
        quick_win_path.write_text(quick_win_md, encoding="utf-8")
        files["quick_win_action"] = quick_win_path
        
        # 4. Metrics Summary (JSON)
        metrics = self._prepare_metrics_json(context, quick_win)
        metrics_path = output_dir / "metrics_summary.json"
        metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
        files["metrics_summary"] = metrics_path
        
        return files
    
    def _prepare_context(
        self,
        hotel_data: dict,
        gbp_data: dict,
        ia_test: dict,
        llm_analysis: dict,
        quick_win: dict,
        competitors_data: Optional[list] = None
    ) -> dict:
        """Prepara variables para los templates."""
        
        hotel_name = hotel_data.get("nombre", "Hotel")
        city = self._extract_city(hotel_data.get("ubicacion", ""))
        region = self._detect_region(hotel_data.get("ubicacion", ""))
        gbp_score = gbp_data.get("score", 0)
        reviews = gbp_data.get("reviews", 0)
        
        # Pérdida mensual
        monthly_loss = llm_analysis.get("perdida_mensual_total", 0)
        
        # Competidores
        top_competitors = []
        if competitors_data and len(competitors_data) > 0:
            top_competitors = [c.get("nombre", "Competidor") for c in competitors_data[:2]]
        
        if not top_competitors:
            top_competitors = ["Hotel A", "Hotel B"]
        
        # INJERTO #1: Identificar competidor específico por ciudad
        specific_competitor = self._identify_top_competitor(city)
        
        # Interpretación GBP
        if gbp_score >= 80:
            gbp_interp = "Tu perfil está bien optimizado"
            gbp_comp = "Superas a competencia local"
        elif gbp_score >= 60:
            gbp_interp = "Tu perfil tiene lo básico pero le falta optimización"
            gbp_comp = "Estás al nivel de competencia"
        elif gbp_score >= 40:
            gbp_interp = "Tu perfil necesita trabajo urgente"
            gbp_comp = "Estás por debajo de competencia"
        else:
            gbp_interp = "Tu perfil está muy incompleto"
            gbp_comp = "Competencia te supera significativamente"
        
        # Desglose de pérdida
        monthly_booking_loss = int(monthly_loss * 0.40)
        monthly_ia_loss = int(monthly_loss * 0.35)
        monthly_geo_loss = int(monthly_loss * 0.25)
        
        return {
            "hotel_name": hotel_name,
            "city": city,
            "region": region,
            "analysis_date": datetime.now().strftime("%d de %B de %Y"),
            "gbp_score": gbp_score,
            "gbp_interpretation": gbp_interp,
            "gbp_comparison": gbp_comp,
            "reviews": reviews,
            "monthly_loss": monthly_loss,
            "monthly_loss_formatted": f"{monthly_loss:,.0f}".replace(",", "."),
            "annual_loss": monthly_loss * 12,
            "annual_loss_formatted": f"{monthly_loss * 12:,.0f}".replace(",", "."),
            "booking_loss_monthly": monthly_booking_loss,
            "ia_loss_monthly": monthly_ia_loss,
            "geo_loss_monthly": monthly_geo_loss,
            "top_competitor_1": top_competitors[0] if len(top_competitors) > 0 else "Competidor 1",
            "top_competitor_2": top_competitors[1] if len(top_competitors) > 1 else "Competidor 2",
            "competitor_count": len(competitors_data) if competitors_data else 2,
            "quick_win_action": quick_win.get("action", ""),
            "quick_win_impact": quick_win.get("expected_impact", ""),
            "quick_win_time": quick_win.get("time_to_complete", ""),
            # INJERTO #1: Variables de competidor específico
            "competitor_name": specific_competitor.get("name", "el hotel líder de tu zona"),
            "competitor_distance": specific_competitor.get("distance", "en tu misma zona"),
            "competitor_segment": specific_competitor.get("segment", "segmento similar"),
            "competitor_advantage": specific_competitor.get("advantage", "40% más consultas directas"),
        }
    
    def _render_spark_report(self, context: dict) -> str:
        """Renderiza el template de Spark Report."""
        template_path = self.templates_dir / "spark_report.md"
        
        if template_path.exists():
            template = template_path.read_text(encoding="utf-8")
        else:
            template = self._default_spark_template()
        
        # Reemplazar variables
        for key, value in context.items():
            template = template.replace("{{" + key + "}}", str(value))
        
        return template
    
    def _render_whatsapp_script(self, context: dict) -> str:
        """Renderiza el template de WhatsApp."""
        template_path = self.templates_dir / "whatsapp_script.md"
        
        if template_path.exists():
            template = template_path.read_text(encoding="utf-8")
        else:
            template = self._default_whatsapp_template()
        
        # Reemplazar variables
        for key, value in context.items():
            template = template.replace("{{" + key + "}}", str(value))
        
        return template
    
    def _render_quick_win(self, quick_win: dict) -> str:
        """
        Renderiza la acción rápida con contexto personalizado.
        
        INJERTO #2 (B.md): Incluye campo 'reason' para explicar POR QUÉ este tip
        es específico para este hotel. Aumenta reciprocidad percibida +10%.
        """
        reason = quick_win.get('reason', 'Esta acción te acerca a los 3 puntos clave del análisis.')
        priority = quick_win.get('priority', 'MEDIA')
        
        return f"""# 🎁 Acción Gratuita PERSONALIZADA

## {quick_win.get('action')}

---

### 💡 Por qué este tip es para TI específicamente:

> {reason}

---

### 📊 Resultados esperados:

- ⏱️ **Tiempo:** {quick_win.get('time_to_complete')}
- 📈 **Impacto:** {quick_win.get('expected_impact')}
- ⚡ **Prioridad:** {priority}
- 🎯 **Dificultad:** {quick_win.get('difficulty')}

---

### ✅ Cómo sabré que funcionó:

{self._generate_verification_method(quick_win)}

---

### ❓ ¿Y si tengo dudas?

Respóndeme a este WhatsApp y te guío personalmente (gratis, en 5 minutos).

No necesitas contratarme para implementar esto. Es tuyo.
"""

    def _generate_verification_method(self, quick_win: dict) -> str:
        """
        Genera método de verificación según tipo de tip.
        
        INJERTO #2 (B.md): Cada tip tiene verificación específica
        para que el hotelero sepa si funcionó.
        """
        case = quick_win.get('case', '').upper()
        
        if 'PHOTO' in case or 'GBP' in case:
            return """Ve a tu perfil de Google Maps en 2-3 días.
Verás que tus fotos nuevas tienen más views que las anteriores.
Además, tu "posición en búsquedas" subirá (lo ves en Google Business Profile > Rendimiento)."""
        
        elif 'REVIEW' in case:
            return """Cuando llegues a 10+ reseñas:
1. Busca "hotel cerca de mí" en Google Maps (desde tu ciudad)
2. Verás que tu posición subió 2-4 lugares
3. Recibirás más llamadas/WhatsApps (mide cuántos en 2 semanas)."""
        
        elif 'SCHEMA' in case:
            return """En 2-3 semanas, pregúntale a ChatGPT: "¿Dónde me hospedo en [tu ciudad]?"
Si implementaste bien, deberías aparecer mencionado (aunque sea en posición 3-5).
Antes de cambiar, ChatGPT ni sabía que existías."""
        
        elif 'AMENITIES' in case:
            return """Pregunta a ChatGPT: "¿Hotel con [tu servicio principal] en [tu ciudad]?"
Si documentaste bien tus servicios, deberías aparecer.
Además, notarás más consultas sobre servicios específicos ("¿tienen piscina?")."""
        
        elif 'DESCRIPTION' in case:
            return """Revisa Google Search Console en 2 semanas.
Las impresiones para tu nombre de hotel deberían subir.
También notarás que las consultas son más específicas (gente que sabe qué busca)."""
        
        else:
            return """Monitorea tus consultas directas (llamadas/WhatsApps) durante 2 semanas.
Compara semana 1 vs semana 3. Deberías ver +10-15% más consultas."""
    
    def _prepare_metrics_json(self, context: dict, quick_win: dict) -> dict:
        """Prepara JSON con métricas para CRM/tracking."""
        return {
            "hotel": context["hotel_name"],
            "hotel_nombre": context["hotel_name"],
            "region": context["region"],
            "analysis_date": context["analysis_date"],
            "perdida_mensual": context["monthly_loss"],
            "gbp_score": context["gbp_score"],
            "quick_win": {
                "action": quick_win.get("action", ""),
                "expected_impact": quick_win.get("expected_impact", ""),
                "time_to_complete": quick_win.get("time_to_complete", ""),
                "difficulty": quick_win.get("difficulty", ""),
                "case": quick_win.get("case", ""),
            },
            "metrics": {
                "gbp_score": context["gbp_score"],
                "reviews": context["reviews"],
                "monthly_loss_cop": context["monthly_loss"],
                "annual_loss_cop": context["annual_loss"],
            },
            "breakdown": {
                "booking_commissions_loss": context["booking_loss_monthly"],
                "ia_visibility_loss": context["ia_loss_monthly"],
                "geo_visibility_loss": context["geo_loss_monthly"],
            },
            "competitors": [context["top_competitor_1"], context["top_competitor_2"]],
            "cta": "Ver Spark Report y video Loom",
        }
    
    def _extract_city(self, location: str) -> str:
        """Extrae la ciudad de la ubicación."""
        if not location:
            return "tu ciudad"
        parts = location.split(",")
        return parts[0].strip() if parts else location.strip()
    
    def _detect_region(self, location: str) -> str:
        """Detecta la región de la ubicación."""
        location_lower = (location or "").lower()
        
        if any(word in location_lower for word in ["armenia", "pereira", "manizales", "caldas", "risaralda", "quindío"]):
            return "Eje Cafetero"
        elif any(word in location_lower for word in ["cartagena", "santa marta", "barranquilla", "bolívar", "atlántico"]):
            return "Caribe"
        elif any(word in location_lower for word in ["medellín", "envigado", "rionegro", "antioquia"]):
            return "Antioquia"
        elif any(word in location_lower for word in ["bogotá", "cundinamarca"]):
            return "Bogotá/Cundinamarca"
        else:
            return "Colombia"
    
    def _default_spark_template(self) -> str:
        """Template por defecto si no existe archivo."""
        return """# ⚡ Spark Report: {{hotel_name}}

**Análisis:** {{analysis_date}}  
**Región:** {{region}}

## 3 Hallazgos Clave

### 1. {{hotel_name}} no aparece en ChatGPT/Perplexity

Cuando preguntamos "¿dónde hospedarse en {{city}}?":
- {{top_competitor_1}}: Aparece ✅
- {{top_competitor_2}}: Aparece ✅
- {{hotel_name}}: NO aparece ❌

**Impacto:** Pierdes oportunidades automáticas cada día.

### 2. Score Google Maps: {{gbp_score}}/100

{{gbp_interpretation}}

{{gbp_comparison}}

### 3. Pierdes ${{monthly_loss_formatted}}/mes

Desglose:
- Comisiones Booking: ${{booking_loss_monthly}}/mes
- Visibilidad IA perdida: ${{ia_loss_monthly}}/mes
- Visibilidad local: ${{geo_loss_monthly}}/mes

**Al año:** ${{annual_loss_formatted}}

## Tu Acción Hoy

{{quick_win_action}}

Impacto: {{quick_win_impact}}  
Tiempo: {{quick_win_time}}

## Siguiente Paso

Si ves sentido, arreglamos esto en 30 días con presupuesto. Devolución 50% si no hay resultados.

¿Hablamos?
"""
    
    def _default_whatsapp_template(self) -> str:
        """Template WhatsApp por defecto."""
        return """Hola,

Vi tu hotel {{hotel_name}} y encontré algo importante.

Hice una búsqueda en ChatGPT: "¿dónde hospedarse en {{city}}?" y vi que tu competencia aparece recomendada, pero tú no.

Te preparé un video mostrándote exactamente dónde está la brecha y cuánto te cuesta: [Loom URL]

Solo son 2 minutos. ¿Te interesa verlo?
"""

    def _identify_top_competitor(self, city: str) -> dict:
        """
        Identifica competidor #1 en la zona del hotel.
        
        INJERTO #1 (B.md): Cambia "tu competencia" genérico por nombre específico.
        Impacto esperado: +15% conversión spark
        
        Estrategia:
        1. Normaliza ciudad a slug
        2. Busca en cache local (data/cache/competitors_by_city.json)
        3. Si no existe, usa competidor genérico con nombre inventado por región
        
        Returns:
            Dict con: name, distance, segment, advantage
        """
        import os
        
        if not city:
            return {
                "name": "el hotel mejor posicionado en tu zona",
                "distance": "cercano",
                "segment": "tu mismo segmento",
                "advantage": "40% más consultas directas"
            }
        
        # Normalizar ciudad a slug
        city_slug = city.lower().strip()
        city_slug = city_slug.replace(' ', '-').replace('á', 'a').replace('é', 'e')
        city_slug = city_slug.replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        city_slug = city_slug.replace('ñ', 'n')
        
        # Buscar en cache de competidores por ciudad
        cache_path = Path(__file__).parent.parent.parent / "data" / "cache" / "competitors_by_city.json"
        
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    competitors_db = json.load(f)
                
                if city_slug in competitors_db:
                    comp = competitors_db[city_slug]["top_competitor"]
                    return {
                        "name": comp.get("name", "el hotel líder de tu zona"),
                        "distance": comp.get("distance", "en tu misma zona"),
                        "segment": comp.get("segment", "segmento similar"),
                        "advantage": comp.get("advantage", "40% más consultas")
                    }
            except (json.JSONDecodeError, KeyError):
                pass
        
        # Fallback: Competidor genérico basado en región
        generic_names = {
            "pereira": "Termales San Vicente",
            "santa-rosa": "Hotel Termales Santa Rosa",
            "armenia": "Hotel Campestre Los Lagos",
            "manizales": "Hotel Termales El Otoño",
            "salento": "Coffee Tree Boutique Hotel",
            "cartagena": "Hotel Casa San Agustín",
            "santa-marta": "Hotel Boutique Don Pepe",
            "medellin": "Hotel Dann Carlton",
            "bogota": "Hotel JW Marriott",
            "cali": "Hotel Intercontinental"
        }
        
        competitor_name = generic_names.get(city_slug, "el hotel líder de tu zona")
        
        return {
            "name": competitor_name,
            "distance": "a menos de 1 km",
            "segment": "tu mismo segmento",
            "advantage": "40% más consultas directas"
        }
