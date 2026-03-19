"""Stage handlers for IA Hoteles Agent.

Contains the actual business logic for each pipeline stage,
decoupled from the orchestrator to allow agentic delegation.
"""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

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
from modules.decision_engine import DecisionEngine, Diagnostico
from modules.watchdog.truth_validator import TruthValidator
from modules.utils.benchmarks import BenchmarkLoader
from modules.knowledge.graph_manager import GraphManager
from modules.orchestrator.mixins import align_seo_summary
from modules.delivery.manager import DeliveryManager
from modules.delivery.delivery_context import DeliveryContext

try:
    from modules.scrapers.gbp_auditor import GBPAuditor
except ImportError:
    GBPAuditor = None

from modules.scrapers.gbp_photo_auditor import integrate_photo_auditor

try:
    from modules.scrapers.gbp_posts_auditor import integrate_posts_auditor
except ImportError:
    integrate_posts_auditor = None


class StageHandlers:
    """Business logic for analysis stages."""

    def __init__(self, options: Any):
        self.options = options

    def handle_geo_stage(self, payload: Dict[str, Any], context: Any) -> Dict[str, Any]:
        url = payload.get("url") or self.options.url
        print("\n" + "=" * 60)
        print("ETAPA 1: PILAR 1 - GBP Y MAPAS (extraccion + data mining)")
        print("=" * 60)

        web_scraper = WebScraper()
        scraper_fallback = ScraperFallback()

        print("\nIntentando scraping avanzado...")
        hotel_data = web_scraper.extract_hotel_data(url) or {}

        if not hotel_data or hotel_data.get("confidence") == "low":
            print("Datos incompletos, activando modo fallback...")
            hotel_data = scraper_fallback.enrich_data(hotel_data, url)

        # Fallback para habitaciones
        if not hotel_data.get('habitaciones'):
            region = scraper_fallback._detect_region(hotel_data.get('ubicacion', ''))
            region_data = scraper_fallback.benchmarks['regiones'].get(region, {})
            hotel_data['habitaciones'] = region_data.get('habitaciones_promedio', 15)
            hotel_data.setdefault('campos_estimados', []).append('habitaciones')

        print("\nDatos del hotel obtenidos:")
        print(f"   Nombre: {hotel_data.get('nombre', 'No disponible')}")
        print(f"   Ubicacion: {hotel_data.get('ubicacion', 'No disponible')}")
        print(f"   Habitaciones: {hotel_data.get('habitaciones', 'No disponible')}")

        gbp_data = {"existe": False, "score": 0, "issues": [], "reviews": 0, "rating": 0.0}

        if GBPAuditor is not None:
            try:
                auditor = GBPAuditor()
                integrate_photo_auditor(auditor)
                if not self.options.skip_posts and integrate_posts_auditor:
                    integrate_posts_auditor(auditor)

                gbp_data = auditor.check_google_profile(
                    hotel_data.get("nombre", ""),
                    hotel_data.get("ubicacion", ""),
                )
                gbp_data.setdefault("gbp_activity_score", 100)
                gbp_data.setdefault("motor_reservas_gbp", gbp_data.get("motor_gbp", {}).get("existe", True))
                gbp_data.setdefault("motor_reservas_prominente", gbp_data.get("motor_gbp", {}).get("prominente", False))
                hotel_data.setdefault("gbp_activity_score", gbp_data.get("gbp_activity_score"))
                hotel_data.setdefault("gbp_motor_existe", gbp_data.get("motor_reservas_gbp"))
                hotel_data.setdefault("gbp_motor_prominente", gbp_data.get("motor_reservas_prominente"))
            except Exception as gbp_error:
                gbp_data["issues"].append(f"GBP audit skipped: {gbp_error}")

        print(f"\nScore GBP: {gbp_data.get('score', 0)}/100")

        # Location resolution logic
        gbp_meta = gbp_data.get("meta")
        if isinstance(gbp_meta, dict):
            resolved_location = gbp_meta.get("resolved_location")
            if resolved_location:
                hotel_data["ubicacion_validada"] = resolved_location
                hotel_data["ubicacion"] = resolved_location
            
            geo_validation = gbp_meta.get("geo_validation")
            if isinstance(geo_validation, dict) and geo_validation.get("actual_location"):
                actual_loc = geo_validation["actual_location"]
                if isinstance(actual_loc, dict):
                    hotel_data["lat"] = actual_loc.get("lat")
                    hotel_data["lng"] = actual_loc.get("lng")

        print("\nAnalizando Schema.org...")
        schema_finder = SchemaFinder()
        schema_data = schema_finder.analyze(url)

        competitors_data = None
        if not self.options.skip_competitors:
            try:
                from modules.analyzers.competitor_analyzer import CompetitorAnalyzer
                analyzer = CompetitorAnalyzer()
                lat = hotel_data.get('lat')
                lng = hotel_data.get('lng')
                if lat and lng:
                    competitors_data = analyzer.get_nearby_competitors(hotel_data.get('nombre', ''), lat, lng)
            except Exception:
                pass

        from modules.orchestrator.pipeline import GeoStageResult
        return {
            "geo_result": GeoStageResult(
                hotel_data=hotel_data,
                gbp_data=gbp_data,
                schema_data=schema_data,
                competitors_data=competitors_data
            )
        }

    def handle_ia_stage(self, payload: Dict[str, Any], context: Any) -> Dict[str, Any]:
        from modules.orchestrator.pipeline import GeoStageResult, IAStageResult
        geo_result: GeoStageResult = payload["geo_result"]
        
        print("\n" + "=" * 60)
        print("ETAPA 2: PILAR 2 - DATOS PARA IA (analisis inteligente)")
        print("=" * 60)

        hotel_data = geo_result.hotel_data
        gbp_data = geo_result.gbp_data
        schema_data = geo_result.schema_data

        ia_tester = IATester()
        ia_test = ia_tester.test_hotel(hotel_data)

        narrative_mode = getattr(self.options, "mode", "generativo")
        if narrative_mode == "deterministico":
            llm_analysis = self._fallback_gap_analysis(hotel_data, gbp_data, schema_data, ia_test)
            current_provider = "deterministic"
        else:
            try:
                gap_analyzer = GapAnalyzer(provider_type=self.options.provider)
                current_provider = gap_analyzer.llm_adapter.get_current_provider()
                llm_analysis = gap_analyzer.analyze_with_llm(hotel_data, gbp_data, schema_data, ia_test)
            except Exception:
                llm_analysis = self._fallback_gap_analysis(hotel_data, gbp_data, schema_data, ia_test)
                current_provider = "fallback"

        fallback_helper = ScraperFallback()
        region = fallback_helper._detect_region(hotel_data.get("ubicacion", ""))
        from modules.orchestrator.pipeline import _determine_package_decision_engine
        decision_result = _determine_package_decision_engine(
            hotel_data, gbp_data, schema_data, ia_test, llm_analysis, region
        )

        roi_calc = ROICalculator()
        roi_data = roi_calc.calculate(hotel_data, llm_analysis, decision_result=decision_result)

        return {
            "ia_result": IAStageResult(
                ia_test=ia_test,
                llm_analysis=llm_analysis,
                roi_data=roi_data,
                current_provider=current_provider,
                decision_result=decision_result,
                region=region,
            )
        }

    def handle_seo_stage(self, payload: Dict[str, Any], context: Any) -> Dict[str, Any]:
        from modules.orchestrator.pipeline import GeoStageResult, IAStageResult, SEOStageResult
        geo_result: GeoStageResult = payload["geo_result"]
        ia_result: Optional[IAStageResult] = payload.get("ia_result")

        print("\n" + "=" * 60)
        print("ETAPA 2.5: CREDIBILIDAD WEB - SEO ACCELERATOR")
        print("=" * 60)

        hotel_data = geo_result.hotel_data
        accelerator = SEOAccelerator(
            self.options.url,
            business_name=hotel_data.get("nombre", "Hotel"),
            location=hotel_data.get("ubicacion", ""),
            provider_type=self.options.provider,
        )

        analysis = accelerator.analyze_complete(include_competitor_analysis=False)
        report_markdown = accelerator.generate_markdown_report(analysis)
        credibility_score = int(analysis.get("score", {}).get("total", 0))

        ia_web_gap = 0.0
        estimated_lost_bookings = 0.0
        if ia_result:
            ia_test = ia_result.ia_test
            total_mentions = ia_test.get("perplexity", {}).get("menciones", 0) + ia_test.get("chatgpt", {}).get("menciones", 0)
            ia_web_gap = max(total_mentions * 50 * (100 - credibility_score) / 100, 0)
            estimated_lost_bookings = round(ia_web_gap * 0.15, 2)

        summary = align_seo_summary({"score": credibility_score}, analysis)

        return {
            "seo_result": SEOStageResult(
                credibility_score=credibility_score,
                issues=analysis.get("issues", []),
                keyword_opportunities=analysis.get("keywords", []),
                ia_web_gap=ia_web_gap,
                estimated_lost_bookings=estimated_lost_bookings,
                analysis=analysis,
                markdown_report=report_markdown,
                summary=summary,
            )
        }

    def handle_outputs_stage(self, payload: Dict[str, Any], context: Any) -> Dict[str, Any]:
        from modules.orchestrator.pipeline import GeoStageResult, IAStageResult, SEOStageResult, OutputStageResult
        
        geo_result: GeoStageResult = payload["geo_result"]
        ia_result: IAStageResult = payload["ia_result"]
        seo_result: Optional[SEOStageResult] = payload.get("seo_result")
        
        hotel_data = geo_result.hotel_data
        gbp_data = geo_result.gbp_data
        schema_data = geo_result.schema_data
        ia_test = ia_result.ia_test
        llm_analysis = ia_result.llm_analysis
        roi_data = ia_result.roi_data
        decision_result = ia_result.decision_result
        region_code = getattr(ia_result, "region", "default")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hotel_slug = self._safe_slug(hotel_data.get("nombre") or self.options.url)
        output_dir = self.options.output_dir / f"{hotel_slug}_{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            graph = GraphManager()
            graph.save_snapshot(hotel_slug, {
                "gbp_score": gbp_data.get("score"),
                "web_score": hotel_data.get("web_score"),
                "ia_mentions": (ia_test.get("perplexity", {}).get("menciones", 0) + 
                               ia_test.get("chatgpt", {}).get("menciones", 0)),
                "perdida_mensual": llm_analysis.get("perdida_mensual_total"),
                "paquete": decision_result.get("paquete")
            })
            print(f"   [Knowledge] Snapshot historico guardado para {hotel_slug}")
        except Exception as e:
            print(f"   [WARN] No se pudo guardar el snapshot historico: {e}")
        
        print("\nEjecutando Protocolo de Verdad 4.0...")
        truth_validator = TruthValidator()
        truth_results = truth_validator.validate_diagnostic_data(
            hotel_data, gbp_data, ia_test, roi_data, region=region_code
        )
        
        evidencias_dir = output_dir / "evidencias"
        evidencias_dir.mkdir(exist_ok=True)
        
        if truth_results:
            with open(evidencias_dir / "arbitraje_de_verdad.json", "w", encoding="utf-8") as f:
                json.dump(truth_results.get("arbitration_log", []), f, indent=2, ensure_ascii=False)
            
            confidence_label = hotel_data.get('confidence', 'ALTA').upper()
            hotel_data["truth_stamp"] = f"\n> **Certificado de Veracidad**: Este diagnostico ha sido validado mediante Triple Triangulacion. Confianza: {confidence_label}\n"
            judgments = truth_results.get("critical_judgments", [])
            if judgments:
                hotel_data["truth_stamp"] += "> \n"
                for j in judgments:
                    hotel_data["truth_stamp"] += f"> **Juicio Critico**: {j}\n"
        
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
            decision_result=decision_result,
            seo_data=seo_result.summary if seo_result else None,
            competitors_data=geo_result.competitors_data,
            truth_results=truth_results,
        )
        
        print("Generando propuesta comercial PDF...")
        proposal_gen = ProposalGenerator()
        llm_analysis_copy = dict(llm_analysis)
        llm_analysis_copy["gbp_data"] = gbp_data
        llm_analysis_copy.setdefault("schema_data", schema_data)
        llm_analysis_copy["justificacion_paquete"] = decision_result.get("razon", llm_analysis.get("justificacion_paquete"))
        llm_analysis_copy.setdefault("region", decision_result.get("region", region_code))
        proposal_gen.create_pdf(hotel_data, llm_analysis_copy, roi_data, output_dir, seo_data=seo_result.summary if seo_result else None)
        
        print("Generando materiales de contacto...")
        outreach_gen = OutreachGenerator()
        outreach_gen.generate_all(hotel_data, llm_analysis_copy, output_dir)
        
        print("Generando toolkit consultor...")
        toolkit_gen = ToolkitConsultorGenerator()
        toolkit_gen.generate_all(hotel_data, llm_analysis_copy, output_dir)
        
        print("Preparando certificados segun Plan Maestro v2.4.2...")
        paquete_recomendado = decision_result.get("paquete", llm_analysis.get("paquete_recomendado", ""))
        loader = BenchmarkLoader()
        cert_cfg = loader.get_certificates_config()
        allowed_packages = cert_cfg.get("allowed_packages", []) or []
        
        if paquete_recomendado in allowed_packages:
            cert_gen = CertificateGenerator()
            certificates_info = {}
            try:
                cert_rd = cert_gen.generate_reserva_directa_badge(hotel_data)
                certificates_info['reserva_directa'] = cert_rd
                print(f"   [OK] Badge Reserva Directa generado")
            except Exception as e:
                print(f"   [WARN] Error generando Reserva Directa: {e}")
            
            try:
                cert_wo = cert_gen.generate_web_optimizada_badge(hotel_data)
                certificates_info['web_optimizada'] = cert_wo
                print("   [OK] Badge Web Optimizada generado")
            except Exception as e:
                print(f"   [WARN] Error generando Web Optimizada: {e}")
        else:
            print(f"   [INFO] Certificados omitidos (paquete {paquete_recomendado} no autorizado)")
        
        delivery_context = DeliveryContext(
            brechas_criticas=llm_analysis.get("brechas_criticas", []),
            fugas_gbp=gbp_data.get("fugas_detectadas", []),
            seo_issues=seo_result.issues if seo_result else [],
            decision_result=decision_result,
            cms_detected=hotel_data.get("cms_detected", {}),
            motor_reservas={"url": hotel_data.get("motor_reservas_url"), 
                            "nombre": hotel_data.get("motor_reservas_nombre"),
                            "tipo": hotel_data.get("motor_reservas_tipo"),
                            "prominente": gbp_data.get("motor_reservas_prominente", False)} if hotel_data.get("motor_reservas_url") else None,
            web_score=hotel_data.get("web_score", 0),
            hotel_data=hotel_data,
            gbp_data=gbp_data
        )
        
        package = decision_result.get("package_id", "starter_geo")
        print(f"\n[DELIVERY] Generando kit para paquete: {package}")
        
        provider_type = getattr(self.options, "provider", "auto")
        delivery_manager = DeliveryManager(output_dir, provider_type=provider_type)
        recommended_package = decision_result.get("paquete", package)
        delivery_manager.execute(package, hotel_data, context=delivery_context, recommended_package=recommended_package)
        
        perdida_mensual = llm_analysis.get("perdida_mensual_total", 0)
        paquete = decision_result.get("paquete", llm_analysis.get("paquete_recomendado", "No disponible"))
        
        print("\n" + "=" * 60)
        print("ANALISIS COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print(f"\nArchivos generados en: {output_dir}/")
        print(f"Perdida mensual identificada: ${perdida_mensual:,.0f} COP")
        print(f"Paquete recomendado: {paquete}")
        
        return {"outputs": OutputStageResult(
            output_dir=output_dir,
            execution_time=0.0,
            perdida_mensual=perdida_mensual,
            paquete_recomendado=paquete
        )}

    def _safe_slug(self, text: str) -> str:
        import re
        slug = re.sub(r'[^\w\s-]', '', (text or "").lower())
        return re.sub(r'[-\s]+', '_', slug).strip('_')[:50]

    def _fallback_gap_analysis(self, hotel_data, gbp_data, schema_data, ia_test):
        from modules.orchestrator.pipeline import _fallback_gap_analysis
        return _fallback_gap_analysis(hotel_data, gbp_data, schema_data, ia_test)
