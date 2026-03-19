"""Pipeline orchestration helpers for IA Hoteles Agent."""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from modules.scrapers.web_scraper import WebScraper
from modules.scrapers.scraper_fallback import ScraperFallback
from modules.scrapers.schema_finder import SchemaFinder
from modules.scrapers.seo_accelerator_pro import SEOAcceleratorProEnhanced as SEOAccelerator
from modules.analyzers.ia_tester import IATester
from modules.analyzers.gap_analyzer import GapAnalyzer
from modules.analyzers.roi_calculator import ROICalculator
from modules.generators.report_builder_fixed import ReportBuilder
from modules.generators.proposal_gen import ProposalGenerator
from modules.generators.outreach_gen import OutreachGenerator
from modules.generators.toolkit_consultor_gen import ToolkitConsultorGenerator
from modules.generators.seo_report_builder import SEOAcceleratorReportBuilder
from modules.generators.certificate_gen import CertificateGenerator
from modules.orchestrator.mixins import align_seo_summary
from modules.orchestrator.stage_handlers import StageHandlers
from modules.decision_engine import DecisionEngine, Diagnostico
from modules.watchdog.truth_validator import TruthValidator
from modules.utils.benchmarks import BenchmarkLoader
from modules.knowledge.graph_manager import GraphManager

try:
    from modules.scrapers.gbp_factory import GBPAuditorAuto
    GBPAuditorAutoAvailable = True
except ImportError:
    GBPAuditorAutoAvailable = False

try:
    from modules.scrapers.gbp_auditor import GBPAuditor  # type: ignore
except Exception:  # pragma: no cover - environments sin selenium
    GBPAuditor = None  # type: ignore

from modules.scrapers.gbp_photo_auditor import integrate_photo_auditor

try:
    from modules.scrapers.gbp_posts_auditor import integrate_posts_auditor
except Exception:  # pragma: no cover - posts auditor opcional
    integrate_posts_auditor = None  # type: ignore


@dataclass
class PipelineOptions:
    url: str
    output_dir: Path
    provider: str = "auto"
    mode: str = "generativo"
    skip_posts: bool = False
    posts_max_wait: Optional[int] = None
    skip_competitors: bool = False
    debug: bool = False
    onboarding_data: Optional[Dict[str, Any]] = None
    input_data_path: Optional[Path] = None


@dataclass
class GeoStageResult:
    hotel_data: Dict
    gbp_data: Dict
    schema_data: Dict
    competitors_data: Optional[List[Dict]] = None


@dataclass
class IAStageResult:
    ia_test: Dict
    llm_analysis: Dict
    roi_data: Dict
    current_provider: str
    decision_result: Dict
    region: str


@dataclass
class OutputStageResult:
    output_dir: Path
    execution_time: float
    perdida_mensual: int
    paquete_recomendado: str
    seo_summary: Optional["SEOStageResult"] = None


@dataclass
class SEOStageResult:
    credibility_score: int
    issues: List[Dict[str, Any]]
    keyword_opportunities: List[str]
    ia_web_gap: float
    estimated_lost_bookings: float
    analysis: Dict[str, Any]
    markdown_report: str
    summary: Dict[str, Any]


class AnalysisPipeline:
    """Runs the IA Hoteles pipeline in modular stages."""

    def __init__(self, options: PipelineOptions, harness: Optional["AgentHarness"] = None) -> None:
        self.options = options
        self.harness = harness
        self.handlers = StageHandlers(options)
        self._start_time: Optional[float] = None
        self._results: Dict[str, Any] = {}
        self._load_onboarding_data()

    def _load_onboarding_data(self) -> None:
        """Load onboarding data from file if path is provided."""
        if self.options.input_data_path and not self.options.onboarding_data:
            try:
                from modules.onboarding.data_loader import load_onboarding_data
                self.options.onboarding_data = load_onboarding_data(self.options.input_data_path)
                campos = len(self.options.onboarding_data.get('campos_confirmados', []))
                print(f"[ONBOARDING] Cargados {campos} campos confirmados desde {self.options.input_data_path}")
            except FileNotFoundError as e:
                print(f"[WARN] Archivo de onboarding no encontrado: {e}")
            except Exception as e:
                print(f"[WARN] No se pudo cargar datos de onboarding: {e}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(self, stages: Sequence[str]) -> Dict[str, object]:
        """Run pipeline stages in optimized order: geo → seo → ia → outputs.
        
        Uses AgentHarness for delegation if available (Meta-Architecture Nivel 3).
        """
        self._validate_stage_dependencies(list(stages))
        return asyncio.run(self._run_async(stages))

    def _validate_stage_dependencies(self, stages: List[str]) -> None:
        """Valida que las dependencias entre etapas se cumplan.
        
        Raises:
            ValueError: Si alguna etapa tiene dependencias no cumplidas.
        """
        normalized_stages = [s.lower() for s in stages]
        
        required_deps = {
            "seo": ["geo"],
            "ia": ["geo"],
            "outputs": ["geo", "ia"]
        }
        
        for stage in normalized_stages:
            deps = required_deps.get(stage, [])
            for dep in deps:
                if dep not in normalized_stages:
                    raise ValueError(
                        f"La etapa '{stage}' requiere que '{dep}' esté en la lista de etapas. "
                        f"Etapas actuales: {stages}"
                    )

    async def _run_async(self, stages: Sequence[str]) -> Dict[str, object]:
        """Internal async implementation of pipeline run."""
        self._start_time = time.time()
        self._results = {}

        normalized_stages = [stage.lower() for stage in stages]

        geo_result: Optional[GeoStageResult] = None
        ia_result: Optional[IAStageResult] = None
        seo_result: Optional[SEOStageResult] = None

        from agent_harness.types import AgentTask

        # Stage 1: GEO (always first - BLOCKING)
        if "geo" in normalized_stages:
            if self.harness:
                res = self.harness.run_task(AgentTask(name="geo_stage", payload={"url": self.options.url}))
                
                # DEBUG: Loggear estructura del resultado si debug está activo
                if self.options.debug:
                    print(f"[DEBUG] geo_stage result: success={res.success}, data_keys={list(res.data.keys()) if hasattr(res.data, 'keys') else type(res.data)}")
                
                # VALIDACIÓN: Verificar éxito y resultado
                if not res.success:
                    print(f"[WARN] geo_stage failed in harness: {res.error}, ejecutando fallback...")
                    geo_result = self.run_geo_stage()
                else:
                    geo_result = res.data.get("geo_result")
                    
                    # FALLBACK: Si geo_result es None pero no hubo error, ejecutar sin harness
                    if geo_result is None:
                        print("[WARN] geo_result es None con harness, ejecutando fallback sin harness...")
                        geo_result = self.run_geo_stage()
            else:
                geo_result = self.run_geo_stage()
            self._results["geo"] = geo_result

        # Stage 2: IA y SEO en paralelo después de GEO
        if "ia" in normalized_stages or "seo" in normalized_stages:
            
            # Definir tareas async
            async def run_ia_async():
                if self.harness:
                    res = self.harness.run_task(AgentTask(name="ia_stage", payload={"geo_result": geo_result}))
                    if not res.success:
                        raise RuntimeError(f"ia_stage failed: {res.error}")
                    ia_result = res.data.get("ia_result")
                    if ia_result is None:
                        ia_result = self.run_ia_stage(geo_result)
                else:
                    ia_result = self.run_ia_stage(geo_result)
                return ia_result
            
            async def run_seo_async():
                if self.harness:
                    res = self.harness.run_task(AgentTask(name="seo_stage", payload={"geo_result": geo_result, "ia_result": None}))
                    if not res.success:
                        raise RuntimeError(f"seo_stage failed: {res.error}")
                    seo_result = res.data.get("seo_result")
                    if seo_result is None:
                        seo_result = self.run_seo_stage(geo_result, ia_result=None)
                else:
                    seo_result = self.run_seo_stage(geo_result, ia_result=None)
                return seo_result
            
            # Ejecutar en paralelo
            if "ia" in normalized_stages and "seo" in normalized_stages:
                ia_result, seo_result = await asyncio.gather(run_ia_async(), run_seo_async())
            elif "ia" in normalized_stages:
                ia_result = await run_ia_async()
                seo_result = None
            else:
                seo_result = await run_seo_async()
                ia_result = None
            
            # Guardar resultados
            if ia_result:
                self._results["ia"] = ia_result
            if seo_result:
                self._results["seo"] = seo_result
                # Actualizar web_score
                if geo_result and seo_result:
                    geo_result.hotel_data['web_score'] = seo_result.credibility_score
            
            # Actualizar SEO con datos de IA si ambos están disponibles
            if ia_result and seo_result:
                seo_result = self._update_seo_ia_gap(seo_result, ia_result)
                self._results["seo"] = seo_result

        # Stage 4: Outputs
        if "outputs" in normalized_stages:
            
            if self.harness:
                res = self.harness.run_task(AgentTask(name="outputs_stage", payload={"geo_result": geo_result, "ia_result": ia_result, "seo_result": seo_result}))
                outputs = res.data.get("outputs")
            else:
                outputs = self.run_outputs_stage(geo_result, ia_result, seo_result)
            self._results["outputs"] = outputs

        execution_time = (time.time() - self._start_time) if self._start_time else 0.0
        self._results["execution_time"] = execution_time
        return self._results

    # ------------------------------------------------------------------
    # Stages
    # ------------------------------------------------------------------
    def run_geo_stage(self) -> GeoStageResult:
        print("\n" + "=" * 60)
        print("ETAPA 1: PILAR 1 - GBP Y MAPAS (extraccion + data mining)")
        print("=" * 60)

        web_scraper = WebScraper()
        scraper_fallback = ScraperFallback()

        print("\nIntentando scraping avanzado...")
        hotel_data = web_scraper.extract_hotel_data(self.options.url) or {}

        # Preparar datos confirmados de onboarding
        confirmed_data = self.options.onboarding_data
        if confirmed_data:
            campos_onboarding = len(confirmed_data.get('datos_operativos', {}))
            print(f"[ONBOARDING] Usando {campos_onboarding} campos confirmados del formulario")

        if not hotel_data or hotel_data.get("confidence") == "low":
            print("Datos incompletos, activando modo fallback...")
            hotel_data = scraper_fallback.enrich_data(
                hotel_data,
                self.options.url,
                confirmed_data=confirmed_data
            )
        elif confirmed_data:
            # Aplicar datos confirmados incluso si scraping fue exitoso
            hotel_data = scraper_fallback.enrich_data(
                hotel_data,
                self.options.url,
                confirmed_data=confirmed_data
            )

        # v2.4.2: Fallback para habitaciones si no fue detectado
        if not hotel_data.get('habitaciones'):
            region = scraper_fallback._detect_region(hotel_data.get('ubicacion', ''))
            region_data = scraper_fallback.benchmarks['regiones'].get(region, {})
            hotel_data['habitaciones'] = region_data.get('habitaciones_promedio', 15)
            hotel_data.setdefault('campos_estimados', []).append('habitaciones')

        # Log de campos confirmados vs estimados
        confirmed = hotel_data.get('campos_confirmados', [])
        estimated = hotel_data.get('campos_estimados', [])

        print("\nDatos del hotel obtenidos:")
        print(f"   Nombre: {hotel_data.get('nombre', 'No disponible')}")
        print(f"   Ubicacion: {hotel_data.get('ubicacion', 'No disponible')}")
        print(f"   Habitaciones: {hotel_data.get('habitaciones', 'No disponible')}")
        print(f"   Confianza de datos: {hotel_data.get('confidence', 'desconocida')}")
        
        if confirmed:
            print(f"   [OK] Campos confirmados: {', '.join(confirmed)}")
        if estimated:
            print(f"   [!] Campos estimados: {', '.join(estimated)}")

        gbp_data = {
            "existe": False,
            "score": 0,
            "issues": [],
            "reviews": 0,
            "rating": 0.0,
        }

        if GBPAuditorAutoAvailable:
            try:
                auditor = GBPAuditorAuto(headless=True)
                print(f"   [GBP] Usando driver: {auditor.driver_type}")
                integrate_photo_auditor(auditor.auditor)
                if not self.options.skip_posts and integrate_posts_auditor:
                    integrate_posts_auditor(auditor.auditor)

                gbp_data = auditor.check_google_profile(
                    hotel_data.get("nombre", ""),
                    hotel_data.get("ubicacion", ""),
                    hotel_data=hotel_data,
                    region=region,
                )
                # Asegurar que activity/motor viajen al motor de decisión y entregables
                gbp_data.setdefault("gbp_activity_score", 100)
                gbp_data.setdefault("motor_reservas_gbp", gbp_data.get("motor_gbp", {}).get("existe", True))
                gbp_data.setdefault("motor_reservas_prominente", gbp_data.get("motor_gbp", {}).get("prominente", False))
                hotel_data.setdefault("gbp_activity_score", gbp_data.get("gbp_activity_score"))
                hotel_data.setdefault("gbp_motor_existe", gbp_data.get("motor_reservas_gbp"))
                hotel_data.setdefault("gbp_motor_prominente", gbp_data.get("motor_reservas_prominente"))
            except Exception as gbp_error:  # pragma: no cover - dependencias externas
                gbp_data["issues"].append(f"GBP audit skipped: {gbp_error}")
        elif GBPAuditor is not None:
            try:
                auditor = GBPAuditor()
                integrate_photo_auditor(auditor)
                if not self.options.skip_posts and integrate_posts_auditor:
                    integrate_posts_auditor(auditor)

                gbp_data = auditor.check_google_profile(
                    hotel_data.get("nombre", ""),
                    hotel_data.get("ubicacion", ""),
                    hotel_data=hotel_data,
                    region=region,
                )
                # Asegurar que activity/motor viajen al motor de decisión y entregables
                gbp_data.setdefault("gbp_activity_score", 100)
                gbp_data.setdefault("motor_reservas_gbp", gbp_data.get("motor_gbp", {}).get("existe", True))
                gbp_data.setdefault("motor_reservas_prominente", gbp_data.get("motor_gbp", {}).get("prominente", False))
                hotel_data.setdefault("gbp_activity_score", gbp_data.get("gbp_activity_score"))
                hotel_data.setdefault("gbp_motor_existe", gbp_data.get("motor_reservas_gbp"))
                hotel_data.setdefault("gbp_motor_prominente", gbp_data.get("motor_reservas_prominente"))
            except Exception as gbp_error:  # pragma: no cover - dependencias externas
                gbp_data["issues"].append(f"GBP audit skipped: {gbp_error}")
        else:
            gbp_data["issues"].append("GBP audit skipped: No driver available")

        print(f"\nScore GBP: {gbp_data.get('score', 0)}/100")

        resolved_location = None
        gbp_meta = gbp_data.get("meta")
        if isinstance(gbp_meta, dict):
            resolved_location = gbp_meta.get("resolved_location")
            location_source = gbp_meta.get("location_source")
            if resolved_location:
                original_location = hotel_data.get("ubicacion")
                if (
                    original_location
                    and original_location.strip()
                    and original_location.strip().lower() != resolved_location.strip().lower()
                ):
                    hotel_data["ubicacion_original"] = original_location
                if location_source == "geo_validation" or not original_location:
                    hotel_data["ubicacion"] = resolved_location
                hotel_data["ubicacion_validada"] = resolved_location
                if location_source:
                    hotel_data["ubicacion_fuente"] = location_source
            
            # Extraer coordenadas de geo_validation si están disponibles
            geo_validation = gbp_meta.get("geo_validation")
            if isinstance(geo_validation, dict) and geo_validation.get("actual_location"):
                actual_loc = geo_validation["actual_location"]
                if isinstance(actual_loc, dict):
                    lat = actual_loc.get("lat")
                    lng = actual_loc.get("lng")
                else:  # Lista/tupla [lat, lng]
                    lat = actual_loc[0] if len(actual_loc) > 0 else None
                    lng = actual_loc[1] if len(actual_loc) > 1 else None
                
                if lat and lng:
                    # Almacenar en gbp_data para CompetitorAnalyzer
                    gbp_data["coordinates"] = {
                        "lat": lat,
                        "lng": lng
                    }
                    # También en hotel_data como fallback
                    hotel_data["lat"] = lat
                    hotel_data["lng"] = lng
                    print(f"   Coordenadas extraídas: {lat:.6f}, {lng:.6f}")

        print("\nAnalizando Schema.org...")
        schema_finder = SchemaFinder()
        schema_data = schema_finder.analyze(self.options.url)
        print(f"   Schemas encontrados: {len(schema_data.get('schemas_encontrados', []))}")

        # NUEVO: Analizar competidores cercanos (opcional)
        competitors_data = None
        if not self.options.skip_competitors:
            try:
                from modules.analyzers.competitor_analyzer import CompetitorAnalyzer
                
                print("\nAnalizando competidores cercanos...")
                analyzer = CompetitorAnalyzer()
                
                # Obtener coordenadas del hotel (de GBP o de hotel_data)
                lat = hotel_data.get('lat') or gbp_data.get('coordinates', {}).get('lat')
                lng = hotel_data.get('lng') or gbp_data.get('coordinates', {}).get('lng')
                
                if lat and lng:
                    competitors_data = analyzer.get_nearby_competitors(
                        hotel_name=hotel_data.get('nombre', ''),
                        lat=lat,
                        lng=lng,
                        radius_km=15
                    )
                    if competitors_data:
                        print(f"   [OK] {len(competitors_data)} competidores analizados")
                    else:
                        print("   [INFO] No se encontraron competidores cercanos")
                else:
                    print("   [WARN] Coordenadas no disponibles - competidores omitidos")
                    print(f"   [INFO] hotel_data.lat={hotel_data.get('lat')}, gbp_data.coordinates={gbp_data.get('coordinates')}")
                    print("   [HINT] Verifica que GOOGLE_MAPS_API_KEY esté configurada para validación geográfica")
            except ImportError:
                print("   [WARN] CompetitorAnalyzer no disponible - competidores omitidos")
            except Exception as e:
                print(f"   [WARN] Error en análisis de competidores: {e}")

        return GeoStageResult(
            hotel_data=hotel_data,
            gbp_data=gbp_data,
            schema_data=schema_data,
            competitors_data=competitors_data
        )

    def run_ia_stage(self, geo_result: GeoStageResult) -> IAStageResult:
        print("\n" + "=" * 60)
        print("ETAPA 2: PILAR 2 - DATOS PARA IA (analisis inteligente)")
        print("=" * 60)

        hotel_data = geo_result.hotel_data
        gbp_data = geo_result.gbp_data
        schema_data = geo_result.schema_data

        ia_tester = IATester()
        print("\nEvaluando visibilidad en asistentes IA...")
        ia_test = ia_tester.test_hotel(hotel_data)
        print(f"   Menciones Perplexity: {ia_test.get('perplexity', {}).get('menciones', 0)}")
        print(f"   Menciones ChatGPT: {ia_test.get('chatgpt', {}).get('menciones', 0)}")

        narrative_mode = getattr(self.options, "mode", "generativo")
        llm_analysis: Dict
        current_provider = "fallback"

        if narrative_mode == "deterministico":
            print("   [MODO] Analisis determinista (sin LLM)...")
            llm_analysis = _fallback_gap_analysis(hotel_data, gbp_data, schema_data, ia_test)
            current_provider = "deterministic"
        else:
            try:
                gap_analyzer = GapAnalyzer(provider_type=self.options.provider)
                current_provider = gap_analyzer.llm_adapter.get_current_provider()
                llm_analysis = gap_analyzer.analyze_with_llm(
                    hotel_data, gbp_data, schema_data, ia_test
                )
            except Exception as llm_error:  # pragma: no cover - dependencias externas
                print(
                    f"   Aviso: no fue posible usar un proveedor LLM ({llm_error}). Se usa analisis offline."
                )
                llm_analysis = _fallback_gap_analysis(hotel_data, gbp_data, schema_data, ia_test)

        # Deterministic package selection (DecisionEngine v2.4.2)
        fallback_helper = ScraperFallback()
        region = fallback_helper._detect_region(hotel_data.get("ubicacion", ""))

        decision_result = _determine_package_decision_engine(
            hotel_data=hotel_data,
            gbp_data=gbp_data,
            schema_data=schema_data,
            ia_test=ia_test,
            llm_analysis=llm_analysis,
            region=region,
        )
        decision_result["region"] = region

        if getattr(self.options, "debug", False):
            print(
                "   [DEBUG] DecisionEngine inputs:",
                {
                    "gbp_score": gbp_data.get("score"),
                    "gbp_activity_score": gbp_data.get("gbp_activity_score"),
                    "motor_reservas_gbp": gbp_data.get("motor_reservas_gbp"),
                    "motor_reservas_prominente": gbp_data.get("motor_reservas_prominente"),
                    "revpar": hotel_data.get("precio_promedio"),
                    "llm_perdida": llm_analysis.get("perdida_mensual_total"),
                },
            )
            print("   [DEBUG] DecisionEngine result:", decision_result)

        # Alinear ROI con paquete determinista
        llm_analysis = dict(llm_analysis)
        llm_analysis["paquete_recomendado"] = decision_result.get("paquete")
        llm_analysis["package_id"] = decision_result.get("package_id")
        llm_analysis["modo_narrativa"] = narrative_mode
        llm_analysis["decision_engine_confianza"] = decision_result.get("confianza")
        llm_analysis["decision_engine_razon"] = decision_result.get("razon")
        llm_analysis["decision_plan_version"] = decision_result.get("plan_version")
        llm_analysis["decision_plan_document"] = decision_result.get("plan_document")

        perdida_mensual = llm_analysis.get("perdida_mensual_total", 0)
        print(f"   Proveedor LLM activo: {current_provider}")
        print(f"   Perdida mensual estimada: ${perdida_mensual:,.0f} COP")
        print(f"   Paquete recomendado (DecisionEngine v2.4.2): {decision_result.get('paquete')} [{decision_result.get('package_id')}]")

        print("\nCalculando ROI y proyecciones...")
        roi_calc = ROICalculator()
        roi_data = roi_calc.calculate(hotel_data, llm_analysis, decision_result=decision_result)
        roas = roi_data.get("totales_6_meses", {}).get("roas")
        mes_recuperacion = roi_data.get("mes_recuperacion")
        if roas is not None:
            print(f"   ROAS 6 meses: {roas}X")
        if mes_recuperacion:
            print(f"   Mes de recuperacion estimado: {mes_recuperacion}")

        return IAStageResult(
            ia_test=ia_test,
            llm_analysis=llm_analysis,
            roi_data=roi_data,
            current_provider=current_provider,
            decision_result=decision_result,
            region=region,
        )

    def run_outputs_stage(
        self,
        geo_result: GeoStageResult,
        ia_result: IAStageResult,
        seo_result: Optional[SEOStageResult],
    ) -> OutputStageResult:
        print("\n" + "=" * 60)
        print("ETAPA 3: ACTIVACION 3 PILARES - ENTREGABLES")
        print("=" * 60)

        hotel_data = geo_result.hotel_data
        gbp_data = geo_result.gbp_data
        schema_data = geo_result.schema_data
        ia_test = ia_result.ia_test
        llm_analysis = ia_result.llm_analysis
        roi_data = ia_result.roi_data
        region_code = getattr(ia_result, "region", "default")

        # CENTRALIZACIÓN: Aplicar addon ANTES de cualquier generador (DRY)
        roi_data = self._apply_addon_to_roi(roi_data, gbp_data)

        # GUARDAR SNAPSHOT HISTÓRICO (Evolución del Auditor al Guardián)
        try:
            graph = GraphManager()
            hotel_slug = self._safe_slug(hotel_data.get("nombre") or self.options.url)
            graph.save_snapshot(hotel_slug, {
                "gbp_score": gbp_data.get("score"),
                "web_score": hotel_data.get("web_score"),
                "ia_mentions": (ia_test.get("perplexity", {}).get("menciones", 0) + 
                               ia_test.get("chatgpt", {}).get("menciones", 0)),
                "perdida_mensual": llm_analysis.get("perdida_mensual_total"),
                "paquete": ia_result.decision_result.get("paquete")
            })
            print(f"   [Knowledge] Snapshot histórico guardado para {hotel_slug}")
        except Exception as e:
            print(f"   [WARN] No se pudo guardar el snapshot histórico: {e}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hotel_slug = self._safe_slug(
            hotel_data.get("nombre") or hotel_data.get("url") or self.options.url
        )
        output_dir = self.options.output_dir / f"{hotel_slug}_{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)

        # 🛡️ PROTOCOLO DE VERDAD 4.0
        print("\nEjecutando Protocolo de Verdad 4.0...")
        truth_validator = TruthValidator()
        truth_results = truth_validator.validate_diagnostic_data(
            hotel_data, gbp_data, ia_test, roi_data, region=region_code
        )
        
        # PERSISTENCIA PUNTO 3: Guardar arbitraje y actualizar Knowledge Graph
        evidencias_dir = output_dir / "evidencias"
        evidencias_dir.mkdir(exist_ok=True)
        
        if truth_results:
            # 1. Guardar Log de Arbitraje para el consultor
            with open(evidencias_dir / "arbitraje_de_verdad.json", "w", encoding="utf-8") as f:
                json.dump(truth_results.get("arbitration_log", []), f, indent=2, ensure_ascii=False)
            
            # 2. Inyectar sello en hotel_data para generadores
            confidence_label = hotel_data.get('confidence', 'ALTA').upper()
            hotel_data["truth_stamp"] = f"\n> **🛡️ Certificado de Veracidad**: Este diagnóstico ha sido validado mediante Triple Triangulación (Datos Técnicos + Visibilidad IA + Benchmarking 2026). Confianza: {confidence_label}\n"
            judgments = truth_results.get("critical_judgments", [])
            if judgments:
                hotel_data["truth_stamp"] += "> \n"
                for j in judgments:
                    hotel_data["truth_stamp"] += f"> 💡 **Juicio Crítico**: {j}\n"
            
            # 3. Retroalimentación al Knowledge Graph (Persistencia de Verdad)
            try:
                knowledge_dir = Path("data/knowledge/hotels")
                knowledge_dir.mkdir(parents=True, exist_ok=True)
                hotel_id = self._safe_slug(hotel_data.get("nombre") or self.options.url)
                with open(knowledge_dir / f"{hotel_id}_verified.json", "w", encoding="utf-8") as f:
                    json.dump(truth_results.get("verified_profile", {}), f, indent=2, ensure_ascii=False)
                print(f"   [Knowledge] Perfil verificado guardado para {hotel_id}")
            except Exception as e:
                print(f"   [WARN] Error persistiendo en Knowledge Graph: {e}")

        narrative_mode = getattr(self.options, "mode", "generativo")
        print(f"\nGenerando diagnostico ejecutivo... (modo {narrative_mode})")
        report_builder = ReportBuilder()
        report_builder.generate(
            hotel_data,
            gbp_data,
            schema_data,
            ia_test,
            llm_analysis,
            roi_data,
            output_dir,
            mode=narrative_mode,
            decision_result=ia_result.decision_result,
            seo_data=seo_result.summary if seo_result else None,
            competitors_data=geo_result.competitors_data,
            truth_results=truth_results,
        )

        print("Generando propuesta comercial PDF...")
        proposal_gen = ProposalGenerator()
        llm_analysis = dict(llm_analysis)
        llm_analysis["gbp_data"] = gbp_data
        llm_analysis.setdefault("schema_data", schema_data)
        llm_analysis["justificacion_paquete"] = ia_result.decision_result.get("razon", llm_analysis.get("justificacion_paquete"))
        llm_analysis.setdefault("region", ia_result.decision_result.get("region", region_code))

        proposal_gen.create_pdf(hotel_data, llm_analysis, roi_data, output_dir, seo_data=seo_result.summary if seo_result else None)

        print("Generando materiales de contacto...")
        outreach_gen = OutreachGenerator()
        outreach_gen.generate_all(hotel_data, llm_analysis, output_dir)

        print("Generando toolkit consultor...")
        toolkit_gen = ToolkitConsultorGenerator()
        toolkit_gen.generate_all(hotel_data, llm_analysis, output_dir)

        print("Preparando certificados segun Plan Maestro v2.4.2...")
        paquete_recomendado = ia_result.decision_result.get("paquete", llm_analysis.get("paquete_recomendado", ""))
        loader = BenchmarkLoader()
        cert_cfg = loader.get_certificates_config()
        allowed_packages = cert_cfg.get("allowed_packages", []) or []

        if paquete_recomendado in allowed_packages:
            cert_gen = CertificateGenerator()
            certificates_info = {}

            try:
                cert_rd = cert_gen.generate_reserva_directa_badge(hotel_data)
                certificates_info['reserva_directa'] = cert_rd
                print(f"   [OK] Badge Reserva Directa generado (se activa en {cert_rd['vigencia_hasta']})")
            except Exception as e:
                print(f"   [WARN] Error generando Reserva Directa: {e}")

            try:
                cert_wo = cert_gen.generate_web_optimizada_badge(hotel_data)
                certificates_info['web_optimizada'] = cert_wo
                print("   [OK] Badge Web Optimizada generado")
            except Exception as e:
                print(f"   [WARN] Error generando Web Optimizada: {e}")

            try:
                hotel_id = hotel_data.get('id', hotel_slug)
                cert_export_path = cert_gen.export_certificates_json(hotel_id, certificates_info)
                print(f"   [OK] Certificados exportados: {cert_export_path}")
            except Exception as e:
                print(f"   [WARN] Error exportando certificados: {e}")
        else:
            print(f"   [INFO] Certificados omitidos (paquete {paquete_recomendado} no autorizado para certificados)")

        # if seo_result:
        #     self._persist_seo_markdown(output_dir, seo_result)

        perdida_mensual = llm_analysis.get("perdida_mensual_total", 0)
        paquete = ia_result.decision_result.get("paquete", llm_analysis.get("paquete_recomendado", "No disponible"))

        execution_time = (time.time() - self._start_time) if self._start_time else 0.0

        print("\n" + "=" * 60)
        print("ANALISIS COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print(f"\nTiempo total: {execution_time:.1f} segundos")
        print(f"Proveedor LLM usado: {ia_result.current_provider}")
        print(f"Archivos generados en: {output_dir}/")
        print(f"Perdida mensual identificada: ${perdida_mensual:,.0f} COP")
        print(f"Paquete recomendado: {paquete}")

        print("\nPasos sugeridos:")
        print("   1. Revisar: 01_DIAGNOSTICO_Y_OPORTUNIDAD.md (10-12 min)")
        print("   2. Revisar: 02_PROPUESTA_COMERCIAL.md (8-10 min)")
        print("   3. Usar _toolkit_consultor/ para preparar videollamada")
        print("   4. Agendar videollamada con cliente (usar call_script_20min.md)")

        print(
            "\nProximo paso: Agenda tu diagnostico 2-Pilares en 15 min -> escribe a jhondrl@gmail.com o WhatsApp +57 317 362 8690"
        )

        if ia_result.current_provider == "deepseek":
            print("\nCosto estimado del analisis: $0.003 (DeepSeek)")
        elif ia_result.current_provider == "anthropic":
            print("\nCosto estimado del analisis: $0.060 (Anthropic)")

        print("\n" + "=" * 60)

        return OutputStageResult(
            output_dir=output_dir,
            execution_time=execution_time,
            perdida_mensual=perdida_mensual,
            paquete_recomendado=paquete,
            seo_summary=seo_result,
        )

    def run_seo_stage(
        self,
        geo_result: GeoStageResult,
        ia_result: Optional[IAStageResult] = None,
    ) -> SEOStageResult:
        """Run SEO credibility analysis.
        
        Args:
            geo_result: Result from GEO stage (required)
            ia_result: Result from IA stage (optional). If None, ia_web_gap 
                      will be 0 and should be updated post-IA via _update_seo_ia_gap()
        """
        print("\n" + "=" * 60)
        print("ETAPA 2.5: CREDIBILIDAD WEB - SEO ACCELERATOR")
        print("=" * 60)

        hotel_data = geo_result.hotel_data
        location = (
            hotel_data.get("ubicacion")
            or hotel_data.get("ubicacion_validada")
            or hotel_data.get("ubicacion_detectada")
            or ""
        )
        business_name = hotel_data.get("nombre") or hotel_data.get("hotel_name") or "Hotel"

        accelerator = SEOAccelerator(
            self.options.url,
            business_name=business_name,
            location=location,
            provider_type=self.options.provider,
        )

        analysis = accelerator.analyze_complete(include_competitor_analysis=False)
        report_markdown = accelerator.generate_markdown_report(analysis)

        keywords = analysis.get("keywords", [])
        score_data = analysis.get("score", {})
        credibility_score = int(score_data.get("total", 0))

        # Calculate ia_web_gap only if ia_result is available
        if ia_result is not None:
            ia_test = ia_result.ia_test
            total_mentions = ia_test.get("perplexity", {}).get("menciones", 0) + ia_test.get("chatgpt", {}).get("menciones", 0)
            base_visibility = max(total_mentions, 1) * 50
            ia_web_gap = max(base_visibility * (100 - credibility_score) / 100, 0)
            estimated_lost_bookings = round(ia_web_gap * 0.15, 2)
        else:
            # Will be recalculated after IA stage via _update_seo_ia_gap()
            ia_web_gap = 0.0
            estimated_lost_bookings = 0.0

        print(f"   Score credibilidad web: {credibility_score}/100")
        if ia_result is not None:
            print(f"   Brecha IA-Web estimada: {ia_web_gap:.0f} visitantes perdidos/mes")
        else:
            print("   Brecha IA-Web: (se calculará después de etapa IA)")

        summary = align_seo_summary({"score": credibility_score}, analysis)

        seo_result = SEOStageResult(
            credibility_score=credibility_score,
            issues=analysis.get("issues", []),
            keyword_opportunities=keywords,
            ia_web_gap=ia_web_gap,
            estimated_lost_bookings=estimated_lost_bookings,
            analysis=analysis,
            markdown_report=report_markdown,
            summary=summary,
        )

        self._persist_seo_tracking(seo_result)
        return seo_result

    def _persist_seo_markdown(self, output_dir: Path, seo_result: SEOStageResult) -> None:
        metadata = seo_result.analysis.get("metadata", {})
        builder = SEOAcceleratorReportBuilder(
            analysis_result=seo_result.analysis,
            hotel_name=metadata.get("business_name") or metadata.get("title") or "Hotel",
            url=self.options.url,
        )
        builder.write(output_dir)

    def _update_seo_ia_gap(self, seo_result: SEOStageResult, ia_result: IAStageResult) -> SEOStageResult:
        """Recalculate ia_web_gap after IA stage completes.
        
        Called when SEO runs before IA stage to update the gap metric.
        """
        ia_test = ia_result.ia_test
        total_mentions = (
            ia_test.get("perplexity", {}).get("menciones", 0)
            + ia_test.get("chatgpt", {}).get("menciones", 0)
        )
        base_visibility = max(total_mentions, 1) * 50
        ia_web_gap = max(base_visibility * (100 - seo_result.credibility_score) / 100, 0)
        estimated_lost_bookings = round(ia_web_gap * 0.15, 2)
        
        # Update the result object
        seo_result.ia_web_gap = ia_web_gap
        seo_result.estimated_lost_bookings = estimated_lost_bookings
        
        print(f"   [SEO] Brecha IA-Web actualizada: {ia_web_gap:.0f} visitantes perdidos/mes")
        return seo_result

    def _persist_seo_tracking(self, seo_result: SEOStageResult) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tracking_dir = self.options.output_dir / "seo_runs"
        tracking_dir.mkdir(parents=True, exist_ok=True)
        
        # v2.5.2: Extraer penalty_metadata del analysis si disponible
        score_data = seo_result.analysis.get("score", {})
        penalty_metadata = score_data.get("penalty_metadata") if isinstance(score_data, dict) else None
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "credibility_score": seo_result.credibility_score,
            "issues": seo_result.issues[:5],
            "keywords": seo_result.keyword_opportunities,
            "ia_web_gap": seo_result.ia_web_gap,
            "estimated_lost_bookings": seo_result.estimated_lost_bookings,
            "financial_loss": seo_result.analysis.get("financial_impact", {}).get("estimated_monthly_loss", 0),
        }
        
        # Incluir penalty_metadata si existe (v2.5.2 trazability)
        if penalty_metadata:
            data["penalty_metadata"] = penalty_metadata
        
        with open(tracking_dir / f"seo_summary_{timestamp}.json", "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _safe_slug(self, value: str, default: str = "hotel") -> str:
        text = (value or "").strip().lower()
        text = text.replace("http://", "").replace("https://", "")
        for char in ["/", "?", "&", "=", ":", "@", "#", "%", "+", ".", ","]:
            text = text.replace(char, " ")
        text = "_".join(filter(None, text.split()))
        return text or default

    def _apply_addon_to_roi(self, roi_data: Dict, gbp_data: Dict) -> Dict:
        """Aplica lógica de addon (ej. GBP Activation) al ROI data.
        
        CENTRALIZADO: Esta es la ÚNICA fuente de verdad para cálculos de addon.
        Debe ejecutarse ANTES de pasar roi_data a cualquier generador.
        """
        loader = BenchmarkLoader()
        thresholds = loader.get_thresholds()
        addons = loader.get_addons()
        
        gbp_score = gbp_data.get('score', 0)
        activity_score = gbp_data.get('gbp_activity_score', gbp_data.get('activity_score', 100))
        
        addon = None
        addon_precio = 0
        
        # Detectar si aplica GBP Activation
        if gbp_score >= thresholds.get('gbp_score_bajo', 60) and activity_score < thresholds.get('gbp_activity_score_bajo', 30):
            addon = "GBP Activation"
            addon_data = addons.get(addon, {})
            addon_precio = int(addon_data.get('precio_cop', 800_000) or 0)
        
        if not addon:
            return roi_data
        
        # Crear copia para no mutar el original en IAStageResult
        roi_data = dict(roi_data)
        roi_data['addon_aplicado'] = addon
        roi_data['addon_precio'] = addon_precio
        
        # Actualizar inversión mensual
        inversion_mensual = roi_data.get('inversion_mensual', 0)
        roi_data['inversion_mensual'] = inversion_mensual + addon_precio
        
        # Actualizar totales de 6 meses
        totales = dict(roi_data.get('totales_6_meses', {}))
        if totales:
            addon_6_meses = addon_precio * 6
            totales['inversion_total'] = totales.get('inversion_total', 0) + addon_6_meses
            ingreso = totales.get('ingreso_recuperado', 0)
            totales['beneficio_neto'] = ingreso - totales['inversion_total']
            if totales['inversion_total'] > 0:
                totales['roas'] = round(ingreso / totales['inversion_total'], 1)
            roi_data['totales_6_meses'] = totales
        
        # Actualizar proyección mensual si existe
        if roi_data.get('proyeccion_6_meses'):
            proyeccion = []
            for mes in roi_data['proyeccion_6_meses']:
                mes_copy = dict(mes)
                mes_copy['inversion'] = mes.get('inversion', 0) + addon_precio
                mes_copy['beneficio_neto'] = mes.get('ingreso_recuperado', 0) - mes_copy['inversion']
                # Recalcular acumulado
                if proyeccion:
                    mes_copy['acumulado'] = proyeccion[-1].get('acumulado', 0) + mes_copy['beneficio_neto']
                else:
                    mes_copy['acumulado'] = mes_copy['beneficio_neto']
                proyeccion.append(mes_copy)
            roi_data['proyeccion_6_meses'] = proyeccion
        
        print(f"   [Pipeline] Addon aplicado: {addon} (+${addon_precio:,}/mes)")
        return roi_data


def _determine_package_decision_engine(
    hotel_data: Dict[str, Any],
    gbp_data: Dict[str, Any],
    schema_data: Dict[str, Any],
    ia_test: Dict[str, Any],
    llm_analysis: Dict[str, Any],
    region: str,
) -> Dict[str, Any]:
    """Centraliza la selección de paquete usando DecisionEngine v2.4.2."""

    fallback_helper = ScraperFallback()
    region_data = fallback_helper.benchmarks["regiones"].get(
        region, fallback_helper.benchmarks["regiones"]["default"]
    )

    gbp_score = int(gbp_data.get("score", 0) or 0)
    gbp_activity_score = int(gbp_data.get("gbp_activity_score", 100) or 100)
    gbp_motor_existe = bool(
        gbp_data.get("motor_reservas_gbp", gbp_data.get("motor_reservas") or gbp_data.get("motor_gbp", {}).get("existe", True))
    )
    gbp_motor_prominente = bool(
        gbp_data.get("motor_reservas_prominente", gbp_data.get("motor_gbp", {}).get("prominente", False))
    )
    web_score = int(hotel_data.get("web_score") or llm_analysis.get("web_score") or 50)

    # RevPAR: usar benchmark regional del Plan Maestro v2.5.0
    # No calcular desde ADR del hotel (confunde ADR con RevPAR)
    revpar = hotel_data.get("revpar") or region_data.get("revpar_cop", 0)

    # Extraer brecha de conversión desde análisis LLM/brechas para evitar inflar con pérdida total
    sin_motor_reservas = 0
    brechas_llm = llm_analysis.get("brechas_criticas") or []
    for brecha in brechas_llm:
        nombre = (brecha.get("nombre") or "").lower()
        impacto = int(brecha.get("impacto_mensual", 0) or 0)
        if any(token in nombre for token in ["motor", "reserva", "convers"]):
            sin_motor_reservas = impacto
            break
    if sin_motor_reservas <= 0 and brechas_llm:
        sin_motor_reservas = max(int(b.get("impacto_mensual", 0) or 0) for b in brechas_llm)
    if sin_motor_reservas <= 0:
        sin_motor_reservas = int(
            llm_analysis.get("perdida_conversion")
            or hotel_data.get("perdida_conversion", 0)
            or hotel_data.get("perdida_mensual", 0)
            or 0
        )
    if sin_motor_reservas <= 0:
        # Fallback conservador: 25% del RevPAR regional mensual
        sin_motor_reservas = int(region_data.get("revpar_cop", 0) * region_data.get("habitaciones_promedio", 15) * 0.25)

    def _safe_score(value):
        try:
            return float(value)
        except Exception:
            return 0.0

    schema_score_raw = schema_data.get("score_schema", schema_data.get("score", 0))
    schema_score = max(0, min(100, int(_safe_score(schema_score_raw))))
    schema_gap = min(100, max(0, 100 - schema_score))
    schema_ausente = int(schema_gap * 50_000)

    menciones_ia = int(
        ia_test.get("perplexity", {}).get("menciones", 0)
        + ia_test.get("chatgpt", {}).get("menciones", 0)
    )

    # Validar coherencia de pérdidas: suma de brechas vs total reportado
    perdida_total_reportada = llm_analysis.get("perdida_mensual_total")
    if perdida_total_reportada and brechas_llm:
        suma_brechas = sum(int(b.get("impacto_mensual", 0) or 0) for b in brechas_llm)
        if abs(suma_brechas - perdida_total_reportada) > max(500_000, 0.1 * perdida_total_reportada):
            print(f"[WARN] Desalineación pérdidas: brechas={suma_brechas} vs total={perdida_total_reportada}")

    engine = DecisionEngine()
    diag = Diagnostico(
        sin_motor_reservas=sin_motor_reservas,
        schema_ausente=schema_ausente,
        gbp_score=gbp_score,
        web_score=web_score,
        revpar=revpar,
        region=region,
        menciones_ia=menciones_ia,
        gbp_activity_score=gbp_activity_score,
        gbp_motor_existe=gbp_motor_existe,
        gbp_motor_prominente=gbp_motor_prominente,
    )

    return engine.recomendar(diag)


def _fallback_gap_analysis(hotel_data, gbp_data, schema_data, ia_test):
    """Replica del analisis offline usado cuando falla el proveedor LLM."""

    fallback_helper = ScraperFallback()
    ubicacion = hotel_data.get("ubicacion", "")
    region = fallback_helper._detect_region(ubicacion)
    region_data = fallback_helper.benchmarks["regiones"].get(
        region, fallback_helper.benchmarks["regiones"]["default"]
    )

    habitaciones = (
        hotel_data.get("habitaciones")
        or region_data.get("habitaciones_promedio", 15)
    )
    precio_promedio = hotel_data.get("precio_promedio") or region_data.get("precio_promedio")
    ocupacion = hotel_data.get("ocupacion_actual") or region_data.get("ocupacion")
    if not precio_promedio:
        precio_promedio = region_data.get("precio_promedio", 280000)
    if not ocupacion:
        ocupacion = region_data.get("ocupacion", 0.6)

    revpar_targets = {
        "eje_cafetero": 171600,
        "caribe": 270600,
        "antioquia": 168000,
        "default": int(region_data.get("precio_promedio", 280000) * region_data.get("ocupacion", 0.6)),
    }
    revpar_objetivo = revpar_targets.get(region, revpar_targets["default"])
    revpar_actual = precio_promedio * ocupacion
    revpar_gap = max(revpar_objetivo - revpar_actual, 0)
    impacto_factor = 0.5 if revpar_gap == 0 else 0.45
    perdida_mensual = int(revpar_objetivo * habitaciones * 30 * impacto_factor)
    reservas_perdidas = max(int(perdida_mensual / max(precio_promedio, 1)), 6)

    # Usar DecisionEngine v2.4.2
    llm_stub = {
        "perdida_mensual_total": perdida_mensual,
        "web_score": hotel_data.get("web_score", 50),
    }

    decision_result = _determine_package_decision_engine(
        hotel_data=hotel_data,
        gbp_data=gbp_data,
        schema_data=schema_data,
        ia_test=ia_test,
        llm_analysis=llm_stub,
        region=region,
    )

    return {
        "brechas_criticas": [
            {
                "nombre": "Pilar 1: GBP sin optimizar",
                "impacto_mensual": int(perdida_mensual * 0.4),
                "descripcion": "65% de las busquedas 'cerca de mi' no encuentran el hotel por falta de activa en GBP.",
                "prioridad": 1,
            },
            {
                "nombre": "Pilar 2: Datos JSON incompletos",
                "impacto_mensual": int(perdida_mensual * 0.35),
                "descripcion": "Asistentes IA no comprenden el inventario del hotel por ausencia de Schema detallado.",
                "prioridad": 1,
            },
            {
                "nombre": "Sin momentum en IA conversacional",
                "impacto_mensual": int(perdida_mensual * 0.25),
                "descripcion": "Perplexity/ChatGPT ignoran a la marca; se pierde demanda directa en respuestas generativas.",
                "prioridad": 2,
            },
        ],
        "perdida_mensual_total": perdida_mensual,
        "quick_wins": [
            "Optimizar Pilar 1: GBP con fotos, Q&A y reseñas verificadas en 7 dias.",
            "Lanzar Pilar 2: JSON-LD Hotel + FAQ con tarifas y amenities críticos.",
            "Publicar mini ficha 2-Pilares para asistentes IA y perfiles de voz.",
            "Califica al Certificado Reserva Directa alcanzando 60% de reservas propias.",
        ],
        "paquete_recomendado": decision_result.get("paquete"),
        "justificacion_paquete": decision_result.get("razon"),
        "confianza": decision_result.get("confianza"),
        "propuesta_valor": (
            "Activamos los 2 Pilares (GBP + JSON-LD) para recuperar demanda orgánica y reducir comisiones OTA en 90 dias."
        ),
        "roi_6meses": "5.0X",
        "recuperacion_inversion": "Mes 2",
        "metricas_clave": {
            "reservas_perdidas_mes": reservas_perdidas,
            "reservas_potenciales_recuperadas": max(int(reservas_perdidas * 0.65), 6),
            "ahorro_comisiones_6meses": int(perdida_mensual * 0.18 * 6),
            "revpar_objetivo": revpar_objetivo,
            "revpar_actual": int(revpar_actual),
        },
        "confianza_datos": hotel_data.get("confidence", "media"),
        "campos_estimados": hotel_data.get("campos_estimados", []),
        "fecha_analisis": datetime.now().strftime("%Y-%m-%d"),
        "proveedor_llm": "fallback",
        "modelo_pilares": "2 Pilares GBP + JSON",
    }
