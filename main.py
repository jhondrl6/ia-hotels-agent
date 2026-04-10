#!/usr/bin/env python3
"""IA Hoteles Agent CLI en modo modular."""
import argparse
import sys
import json
from pathlib import Path
from dataclasses import asdict
from typing import Any, Dict, List, Sequence
from uuid import uuid4
from dotenv import load_dotenv
from modules.utils.permission_mode import PermissionMode, OperationPermission, check_permission

# Cargar variables de entorno desde .env al inicio
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)


# Imports condicionales para módulos legacy (archivados en v4.4.1)
try:
    from modules.orchestrator.pipeline import AnalysisPipeline, PipelineOptions
    from modules.orchestrator.stage_handlers import StageHandlers
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False
    AnalysisPipeline = None
    PipelineOptions = None
    StageHandlers = None

# Forzar UTF-8 para evitar errores cp1252 en Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


DEFAULT_STAGES: Sequence[str] = ("geo", "ia", "seo", "outputs")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="IA Hoteles Agent - Analisis Automatizado",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="audit",
        choices=["audit", "v4audit", "v4complete", "stage", "spark", "execute", "deploy", "setup", "onboard"],
        help="Comando a ejecutar: setup (configuración inicial), audit (diagnóstico legacy), v4audit (auditoría v4.0 con APIs), v4complete (flujo completo v4.0 con Meta-Skills), stage (pasos manuales), spark (diagnóstico rápido <5min), execute (implementación paquete), deploy (despliegue remoto), onboard (captura datos operativos)",
    )
    parser.add_argument("--url", required=False, help="URL del hotel a analizar")
    parser.add_argument("--output", default="./output", help="Directorio de salida base")
    parser.add_argument("--nombre", help="Nombre del hotel (opcional)")
    parser.add_argument("--package", help="Paquete a ejecutar (solo para comando execute)", default="pro_aeo")
    parser.add_argument("--input-data", help="Ruta a datos del hotel JSON (opcional para execute)")
    parser.add_argument("--debug", action="store_true", help="Modo debug")
    parser.add_argument(
        "--mode",
        choices=["generativo", "deterministico"],
        default="generativo",
        help="Modo de generación de narrativas (default: generativo)",
    )
    parser.add_argument(
        "--provider",
        choices=["auto", "deepseek", "anthropic"],
        default="auto",
        help="Proveedor LLM a usar",
    )
    parser.add_argument(
        "--skip-check",
        action="store_true",
        help="Saltar verificacion de configuracion",
    )
    parser.add_argument(
        "--skip-posts",
        action="store_true",
        help="Desactivar auditoria de posts (opcional)",
    )
    parser.add_argument(
        "--permission-mode",
        choices=["auto", "smart_approve", "approve", "chat"],
        default="auto",
        help="Modo de permisos: auto (todo sin preguntar), smart_approve (preguntar si costo > $0.05), "
             "approve (preguntar siempre para llamadas externas), chat (sin llamadas externas)",
    )
    parser.add_argument(
        "--posts-max-wait",
        type=int,
        help="Tiempo maximo de espera para auditoria de posts (opcional)",
    )
    parser.add_argument(
        "--skip-competitors",
        action="store_true",
        help="Omitir analisis de competidores cercanos (opcional)",
    )
    parser.add_argument(
        "--ga4-property-id",
        help="GA4 Property ID del hotel (opcional). Si no se pasa, analytics funciona en modo fallback.",
    )
    parser.add_argument(
        "--stages",
        nargs="+",
        help="Listado de etapas a ejecutar (geo ia seo outputs). Solo valido con 'stage'.",
    )
    # Deploy command arguments
    parser.add_argument(
        "--target",
        help="Nombre del hotel o ruta a delivery_assets (para deploy)",
    )
    parser.add_argument(
        "--method",
        choices=["ftp", "wp-api"],
        default="wp-api",
        help="Método de conexión para deploy",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Solo simular despliegue (default en v2.5)",
    )
    parser.add_argument(
        "--no-dry-run",
        dest="dry_run",
        action="store_false",
        help="Ejecutar despliegue real (v2.6 experimental)",
    )
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="Ejecutar solo verificaciones previas",
    )
    parser.add_argument(
        "--bypass-harness",
        action="store_true",
        help="Bypass Agent Harness (legacy CLI mode, no memory)",
    )
    parser.add_argument(
        "--force-new",
        action="store_true",
        help="Force new analysis, ignore prior analysis (for execute command)",
    )
    # Onboard command arguments
    parser.add_argument(
        "--hotel-name",
        help="Nombre del hotel para onboarding (opcional)",
    )
    parser.add_argument(
        "--output-format",
        choices=["yaml", "json"],
        default="yaml",
        help="Formato de salida para datos de onboarding",
    )
    parser.add_argument(
        "--run-audit",
        action="store_true",
        help="Ejecutar auditoria automaticamente despues del onboarding",
    )
    parser.add_argument(
        "--doctor",
        action="store_true",
        help="Ejecutar diagnostico completo del ecosistema de agentes (skills + contexto)",
    )
    return parser


def normalize_stages(raw_stages: List[str] | None) -> List[str]:
    valid = ["geo", "ia", "seo", "outputs"]
    if not raw_stages:
        return ["geo"]
    normalized: List[str] = []
    for stage in raw_stages:
        stage_lower = stage.lower()
        if stage_lower not in valid:
            raise ValueError(f"Etapa desconocida: {stage}")
        if stage_lower not in normalized:
            normalized.append(stage_lower)
    # Asegurar dependencias
    if "ia" in normalized and "geo" not in normalized:
        normalized.insert(normalized.index("ia"), "geo")
    if "seo" in normalized:
        if "geo" not in normalized:
            normalized.insert(normalized.index("seo"), "geo")
        if "ia" not in normalized:
            idx = normalized.index("seo")
            normalized.insert(idx, "ia")
            if "geo" not in normalized:
                normalized.insert(idx, "geo")
        else:
            ia_idx = normalized.index("ia")
            seo_idx = normalized.index("seo")
            if ia_idx > seo_idx:
                normalized.pop(seo_idx)
                normalized.insert(ia_idx + 1, "seo")
    if "outputs" in normalized and "ia" not in normalized:
        idx = normalized.index("outputs")
        if "geo" not in normalized:
            normalized.insert(idx, "geo")
            idx += 1
        normalized.insert(idx, "ia")
        if "seo" in normalized and normalized.index("seo") < normalized.index("ia"):
            seo_value = normalized.pop(normalized.index("seo"))
            normalized.insert(normalized.index("ia") + 1, seo_value)
    return normalized


def ensure_url(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.command not in ("execute", "deploy", "setup", "onboard") and not args.url:
        from agent_harness.memory import MemoryManager
        memory = MemoryManager()
        state = memory.load_state()
        if state.get("last_url"):
            args.url = state["last_url"]
            print(f"[HARNESS] 🔄 Usando URL persistente: {args.url}")
        else:
            parser.error("--url es obligatorio para este comando")


def _audit_handler(payload: dict, context) -> dict:
    """Harness-compatible handler for audit command (DEPRECATED - use v4complete instead)."""
    if not ORCHESTRATOR_AVAILABLE:
        return {"status": "error", "message": "Comando audit deprecado. Use v4complete en su lugar."}
    # Import movido al principio del archivo con manejo condicional
def _audit_handler(payload: dict, context) -> dict:
    """Harness-compatible handler for audit command (DEPRECATED - use v4complete instead)."""
    if not ORCHESTRATOR_AVAILABLE:
        return {"status": "error", "message": "Comando audit deprecado. Use v4complete en su lugar."}
    # Import movido al principio del archivo con manejo condicional
def _audit_handler(payload: dict, context) -> dict:
    """Harness-compatible handler for audit command (DEPRECATED - use v4complete instead)."""
    if not ORCHESTRATOR_AVAILABLE:
        return {"status": "error", "message": "Comando audit deprecado. Use v4complete en su lugar."}
    # Import movido al principio del archivo con manejo condicional
def _audit_handler(payload: dict, context) -> dict:
    """Harness-compatible handler for audit command (DEPRECATED - use v4complete instead)."""
    if not ORCHESTRATOR_AVAILABLE:
        return {"status": "error", "message": "Comando audit deprecado. Use v4complete en su lugar."}
    # Import movido al principio del archivo con manejo condicional
    output_dir = Path(payload.get("output", "./output")).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    options = PipelineOptions(
        url=payload["url"],
        output_dir=output_dir,
        provider=payload.get("provider", "auto"),
        mode=payload.get("mode", "generativo"),
        skip_posts=payload.get("skip_posts", False),
        posts_max_wait=payload.get("posts_max_wait"),
        skip_competitors=payload.get("skip_competitors", False),
        debug=payload.get("debug", False),
    )
    
    stages = payload.get("stages")
    if not stages:
        stages = list(DEFAULT_STAGES)
    
    pipeline = AnalysisPipeline(options, harness=context.harness)
    
    # Log context if available
    if context.previous_runs > 0:
        print(f"[AUDIT] Contexto previo disponible: {context.previous_runs} ejecuciones.")
        if context.last_outcome == "error":
            print(f"[AUDIT] ⚠️  Última ejecución falló. Aplicando cautela en validación.")
    
    results = pipeline.run(stages)
    
    # Extract key data for memory
    summary = {
        "stages_run": stages,
        "execution_time": results.get("execution_time", 0.0),
        "hotel_name": "Hotel",
        "gbp_score": 0,
        "perdida_mensual": 0,
    }
    
    if "geo" in results:
        geo = results["geo"]
        summary["hotel_name"] = getattr(geo, "hotel_data", {}).get("nombre", "Hotel")
        summary["gbp_score"] = getattr(geo, "gbp_data", {}).get("score", 0)
        summary["target_id"] = summary["hotel_name"] # For memory indexing
    
    if "ia" in results:
        ia = results["ia"]
        summary["perdida_mensual"] = getattr(ia, "llm_analysis", {}).get("perdida_mensual_total", 0)

    # Return results and summary for harness logging
    return {
        "results": {k: str(v) for k, v in results.items() if k != "execution_time"},
        "results_raw": results,
        "summary": summary,
        "target_id": summary.get("target_id")
    }


def _spark_handler(payload: dict, context) -> dict:
    """Harness-compatible handler for spark command (DEPRECATED - use v4complete instead)."""
    if not ORCHESTRATOR_AVAILABLE:
        return {"status": "error", "message": "Comando spark deprecado. Use v4complete en su lugar."}
    from modules.generators.spark_generator import SparkGenerator
    
    output_dir = Path(payload.get("output", "./output")).resolve() / "spark"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    options = PipelineOptions(
        url=payload["url"],
        output_dir=output_dir.parent,
        provider=payload.get("provider", "auto"),
        mode=payload.get("mode", "generativo"),
        skip_posts=payload.get("skip_posts", False),
        posts_max_wait=payload.get("posts_max_wait"),
        skip_competitors=payload.get("skip_competitors", False),
        debug=payload.get("debug", False),
    )
    pipeline = AnalysisPipeline(options, harness=context.harness)
    
    # Log context if available
    if context.previous_runs > 0:
        print(f"[SPARK] Contexto previo disponible: {context.previous_runs} ejecuciones.")
    
    results = pipeline.run(["geo", "ia"])
    
    if "geo" not in results or "ia" not in results:
        raise RuntimeError("Análisis incompleto: falta geo o ia")
    
    geo_result = results["geo"]
    ia_result = results["ia"]
    
    spark_gen = SparkGenerator(provider_type=payload.get("provider", "auto"))
    spark_gen.generate_spark_report(geo_result, ia_result, output_dir)
    
    return {
        "hotel_name": geo_result.hotel_data.get("nombre", "Hotel"),
        "gbp_score": geo_result.gbp_data.get("score", 0),
        "monthly_loss": ia_result.llm_analysis.get("perdida_mensual_total", 0),
        "output_dir": str(output_dir),
        "geo_result": geo_result.hotel_data,
        "gbp_data": geo_result.gbp_data,
    }


def run_spark_mode(args: argparse.Namespace) -> None:
    """Maneja el comando 'spark' para diagnóstico rápido (<5 minutos)."""
    # Check for bypass mode (legacy)
    if getattr(args, "bypass_harness", False):
        _run_spark_legacy(args)
        return
    
    # Harness-enabled mode
    from agent_harness import AgentHarness, AgentTask
    
    print("=" * 60)
    print("MODO SPARK - Diagnóstico Rápido (<5 minutos)")
    print("[HARNESS] Modo Agentico Activo")
    print("=" * 60)
    
    harness = AgentHarness(verbose=args.debug or True)
    harness.register_handler("spark", _spark_handler)
    
    task = AgentTask(
        name="spark",
        payload={
            "url": args.url,
            "output": args.output,
            "provider": args.provider,
            "mode": args.mode,
            "skip_posts": args.skip_posts,
            "posts_max_wait": args.posts_max_wait,
            "skip_competitors": args.skip_competitors,
            "debug": args.debug,
        },
    )
    
    result = harness.run_task(task)
    
    if not result.success:
        print(f"\n[ERROR] {result.error}")
        sys.exit(1)
    
    # Display summary
    data = result.data
    print("\n" + "=" * 60)
    print("SPARK REPORT GENERADO")
    print("=" * 60)
    print(f"\nArchivos creados en: {data.get('output_dir', 'output')}/")
    print(f"  ✓ spark_report.md (1 página, 3 métricas)")
    print(f"  ✓ whatsapp_script.txt (guion 60 segundos)")
    print(f"  ✓ quick_win_action.md (acción gratuita)")
    print(f"  ✓ metrics_summary.json (datos para CRM)")
    
    print(f"\n📊 RESUMEN PARA {data.get('hotel_name', 'Hotel')}:")
    print(f"   Pérdida estimada: ${data.get('monthly_loss', 0):,.0f} COP/mes")
    print(f"   GBP Score: {data.get('gbp_score', 0)}/100")
    
    print(f"\n🚀 PRÓXIMO PASO:")
    print(f"   1. Copia el guion de: whatsapp_script.txt")
    print(f"   2. Graba video Loom (2 minutos)")
    print(f"   3. Envía video + spark_report.md por WhatsApp")
    print(f"   4. Cuando muestre interés, presenta el piloto de $800K")


def _run_spark_legacy(args: argparse.Namespace) -> None:
    """Legacy spark mode (bypass harness)."""
    from modules.generators.spark_generator import SparkGenerator
    
    print("=" * 60)
    print("MODO SPARK - Diagnóstico Rápido (<5 minutos)")
    print("[LEGACY] Modo CLI Sin Harness")
    print("=" * 60)
    
    options = build_pipeline_options(args)
    pipeline = AnalysisPipeline(options)
    
    try:
        print("\nEjecutando análisis ligero (GEO + IA)...")
        results = pipeline.run(["geo", "ia"])
        
        if "geo" not in results or "ia" not in results:
            print("[ERROR] Análisis incompleto")
            sys.exit(1)
        
        geo_result = results["geo"]
        ia_result = results["ia"]
        
        output_dir = Path(args.output).resolve() / "spark"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print("\nGenerando Spark Report...")
        spark_gen = SparkGenerator(provider_type=args.provider)
        spark_gen.generate_spark_report(geo_result, ia_result, output_dir)
        
        print("\n" + "=" * 60)
        print("SPARK REPORT GENERADO")
        print("=" * 60)
        print(f"\nArchivos creados en: {output_dir}/")
        print(f"  ✓ spark_report.md (1 página, 3 métricas)")
        print(f"  ✓ whatsapp_script.txt (guion 60 segundos)")
        print(f"  ✓ quick_win_action.md (acción gratuita)")
        print(f"  ✓ metrics_summary.json (datos para CRM)")
        
        hotel_name = geo_result.hotel_data.get("nombre", "Hotel")
        monthly_loss = ia_result.llm_analysis.get("perdida_mensual_total", 0)
        
        print(f"\n📊 RESUMEN PARA {hotel_name}:")
        print(f"   Pérdida estimada: ${monthly_loss:,.0f} COP/mes")
        print(f"   GBP Score: {geo_result.gbp_data.get('score', 0)}/100")
        print(f"   Competidores analizados: {len(geo_result.competitors_data) if geo_result.competitors_data else 0}")
        
        print(f"\n🚀 PRÓXIMO PASO:")
        print(f"   1. Copia el guion de: whatsapp_script.txt")
        print(f"   2. Graba video Loom (2 minutos)")
        print(f"   3. Envía video + spark_report.md por WhatsApp")
        print(f"   4. Cuando muestre interés, presenta el piloto de $800K")
        
    except Exception as error:
        print(f"\nERROR: {error}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def _run_execution_legacy(args: argparse.Namespace) -> None:
    """Legacy execution mode (bypass harness, no memory)."""
    from modules.delivery.manager import DeliveryManager
    from modules.delivery.delivery_context import DeliveryContext
    from modules.scrapers.web_scraper import WebScraper
    from modules.scrapers.scraper_fallback import ScraperFallback
    
    print("=" * 60)
    print(f"MODO EJECUCION - Implementando Paquete: {args.package}")
    print("[LEGACY] Modo CLI Sin Harness")
    print("=" * 60)
    
    GBPAuditorRef = None
    try:
        from modules.scrapers.gbp_auditor import GBPAuditor as _GBPAuditor
        GBPAuditorRef = _GBPAuditor
    except Exception as exc:
        if args.debug:
            print(f"[WARN] GBP Auditor no disponible: {exc}")

    hotel_data = {}
    delivery_context = None

    if args.input_data:
        try:
            with open(args.input_data, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                if "hotel_data" in loaded_data and "llm_analysis" in loaded_data:
                    print(f"[INFO] Detectado analisis_completo.json")
                    delivery_context = DeliveryContext.from_analysis_json(Path(args.input_data))
                    hotel_data = loaded_data.get("hotel_data", {})
                else:
                    hotel_data = loaded_data.get("hotel_data", loaded_data)
                    print(f"[INFO] Datos cargados desde {args.input_data}")
        except FileNotFoundError:
            print(f"[ERROR] Archivo no encontrado: {args.input_data}")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"[ERROR] JSON inválido en: {args.input_data}")
            sys.exit(1)
    elif args.url:
        print("Extrayendo datos frescos del hotel...")
        scraper = WebScraper()
        hotel_data = scraper.extract_hotel_data(args.url) or {}
        if args.nombre:
            hotel_data["nombre"] = args.nombre
    else:
        print("[ERROR] Para 'execute', se requiere --url o --input-data")
        sys.exit(1)

    fallback = ScraperFallback()

    def needs_fallback(data):
        if not data:
            return True
        confidence_label = str(data.get("confidence", "")).lower()
        if confidence_label in {"low", "baja", "desconocida", "fallback_requerido"}:
            return True
        if not data.get("ubicacion") or not data.get("nombre"):
            return True
        return False

    if needs_fallback(hotel_data):
        print("[WARN] Datos incompletos, aplicando fallback...")
        partial = dict(hotel_data or {})
        partial.setdefault("url", args.url)
        try:
            hotel_data = fallback.enrich_data(partial, args.url)
        except Exception as exc:
            print(f"[WARN] Fallback falló: {exc}")
            hotel_data = partial

    if "visperas" in (args.url or "").lower() and not hotel_data.get("ubicacion"):
        visperas_reference = fallback.get_visperas_data()
        merged = visperas_reference.copy()
        for key, value in (hotel_data or {}).items():
            if value not in (None, ""):
                merged[key] = value
        hotel_data = merged

    if not hotel_data:
        print("[ERROR] No se pudieron obtener datos del hotel.")
        sys.exit(1)

    gbp_validation_meta = {}
    if GBPAuditorRef is not None:
        try:
            auditor = GBPAuditorRef()
            gbp_validation_meta = auditor.validate_location_only(
                hotel_name=hotel_data.get("nombre") or args.nombre or args.url or "",
                location=hotel_data.get("ubicacion") or hotel_data.get("ubicacion_validada") or "",
            )
        except Exception as exc:
            print(f"[WARN] Validación geográfica falló: {exc}")

    resolved_location = gbp_validation_meta.get("resolved_location") if gbp_validation_meta else None
    if resolved_location:
        hotel_data["ubicacion_validada"] = resolved_location
        hotel_data["ubicacion"] = resolved_location

    output_dir = Path(args.output).resolve()
    
    if delivery_context:
        print(f"[INFO] Generación selectiva activada - {len(delivery_context.brechas_criticas)} brechas")
    
    manager = DeliveryManager(output_dir, provider_type=args.provider)
    manager.execute(args.package, hotel_data, context=delivery_context)
    
    print("\n[SUCCESS] Ejecución completada (legacy mode).")


def find_latest_v4_analysis(memory, target_id: str) -> dict | None:
    """Busca el último análisis v4.0 válido:
    - task_name = 'v4complete'
    - outcome = 'success'
    - coherence_score >= 0.8
    - age < 20 días
    """
    from datetime import datetime, timedelta

    history = memory.load_history(target_id, limit=10)

    v4_entries = []
    for entry in history:
        if entry.get('task_name') != 'v4complete':
            continue
        if entry.get('outcome') != 'success':
            continue

        # Validar coherence_score >= 0.8
        coherence = entry.get('coherence_score', 0)
        if coherence < 0.8:
            continue

        # Validar vigencia (< 20 días)
        timestamp = entry.get('timestamp')
        if timestamp:
            try:
                entry_date = datetime.fromisoformat(timestamp)
                age_days = (datetime.now() - entry_date).days
                if age_days > 20:
                    continue
            except:
                continue

        v4_entries.append(entry)

    return v4_entries[0] if v4_entries else None


def run_execution_mode(args: argparse.Namespace) -> None:
    """Maneja el comando 'execute' para implementar paquetes."""
    from modules.delivery.manager import DeliveryManager
    from modules.delivery.delivery_context import DeliveryContext
    from modules.scrapers.web_scraper import WebScraper
    from modules.scrapers.scraper_fallback import ScraperFallback
    
    # Check for bypass mode (legacy)
    if getattr(args, "bypass_harness", False):
        _run_execution_legacy(args)
        return
    
    # Harness-enabled mode
    from agent_harness import AgentHarness, AgentTask
    from agent_harness.memory import MemoryManager
    
    # Initialize memory manager and cleanup old sessions
    memory = MemoryManager()
    memory.cleanup_old_sessions(days=20)
    
    GBPAuditorRef = None
    try:
        from modules.scrapers.gbp_auditor import GBPAuditor as _GBPAuditor  # type: ignore
        GBPAuditorRef = _GBPAuditor
    except Exception as exc:  # pragma: no cover - dependencias opcionales
        if args.debug:
            print(f"[WARN] GBP Auditor no disponible para validación rápida: {exc}")
    
    print("=" * 60)
    print(f"MODO EJECUCION - Implementando Paquete: {args.package}")
    print("[HARNESS] Modo Agéntico Activo")
    print("=" * 60)

    # Obtener datos del hotel
    hotel_data = {}
    delivery_context = None
    
    # Auto-discover prior analysis unless --force-new is specified
    target_id = args.url or args.nombre or args.input_data or "unknown"
    discovered_analysis = None
    v4_analysis = None

    if not getattr(args, "force_new", False) and not args.input_data:
        print("[INFO] Buscando análisis v4.0 previo...")

        v4_entry = find_latest_v4_analysis(memory, target_id)

        if v4_entry:
            v4_analysis = v4_entry.get('outputs', {})
            print(f"[INFO] Análisis v4.0 encontrado:")
            print(f"       Hotel: {v4_entry.get('hotel_name', 'N/A')}")
            print(f"       Coherence Score: {v4_entry.get('coherence_score', 0):.2f}")
            print(f"       Assets generados: {v4_entry.get('assets_generated', 0)}")
            print(f"       Fecha: {str(v4_entry.get('timestamp', 'N/A'))[:10]}")

            # Intentar cargar diagnóstico si existe
            diagnostic_path = v4_analysis.get('diagnostic_path')
            if diagnostic_path and Path(diagnostic_path).exists():
                print(f"       Diagnóstico: {diagnostic_path}")
                try:
                    with open(diagnostic_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        hotel_data = _extract_hotel_data_from_diagnostic(content)
                        hotel_data['diagnostic_content'] = content
                except Exception as e:
                    print(f"[WARN] No se pudo cargar diagnóstico: {e}")

            print(f"       Use --force-new para ignorar y generar nuevo análisis")

        else:
            print("[WARN] No se encontró análisis v4.0 válido reciente.")
            print("[INFO] Requisitos: coherence_score >= 0.8, vigencia < 20 días")
            print("[INFO] Ejecute primero: python main.py v4complete --url <URL>")

            # Fallback a análisis legacy
            discovered_analysis = memory.find_latest_analysis(target_id)
            if discovered_analysis:
                print(f"[INFO] Usando análisis legacy: {discovered_analysis}")
                delivery_context = DeliveryContext.from_analysis_json(discovered_analysis)
                try:
                    with open(discovered_analysis, 'r', encoding='utf-8') as f:
                        loaded_data = json.load(f)
                        hotel_data = loaded_data.get("hotel_data", {})
                except (FileNotFoundError, json.JSONDecodeError):
                    pass

    if args.input_data:
        try:
            with open(args.input_data, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                
                # Detectar si es analisis_completo.json
                if "hotel_data" in loaded_data and "llm_analysis" in loaded_data:
                    print(f"[INFO] Detectado analisis_completo.json - cargando contexto completo")
                    delivery_context = DeliveryContext.from_analysis_json(Path(args.input_data))
                    hotel_data = loaded_data.get("hotel_data", {})
                else:
                    # Es un archivo de datos simple
                    hotel_data = loaded_data.get("hotel_data", loaded_data)
                    print(f"[INFO] Datos cargados desde {args.input_data}")
        except FileNotFoundError:
            print(f"[ERROR] Archivo no encontrado: {args.input_data}")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"[ERROR] JSON inválido en: {args.input_data}")
            sys.exit(1)
    elif args.url and not hotel_data:
        print("Extrayendo datos frescos del hotel...")
        scraper = WebScraper()
        hotel_data = scraper.extract_hotel_data(args.url) or {}
        if args.nombre:
            hotel_data["nombre"] = args.nombre
    else:
        print("[ERROR] Para 'execute', se requiere --url o --input-data")
        sys.exit(1)

    fallback = ScraperFallback()

    def needs_fallback(data: Dict[str, Any]) -> bool:
        if not data:
            return True
        confidence_label = str(data.get("confidence", "")).lower()
        if confidence_label in {"low", "baja", "desconocida", "fallback_requerido"}:
            return True
        if not data.get("ubicacion") or not data.get("nombre"):
            return True
        return False

    if needs_fallback(hotel_data):
        print("[WARN] Datos incompletos, aplicando fallback inteligente...")
        partial = dict(hotel_data or {})
        partial.setdefault("url", args.url)
        try:
            hotel_data = fallback.enrich_data(partial, args.url)
        except Exception as exc:  # pragma: no cover - fallback opcional
            print(f"[WARN] Fallback principal falló: {exc}")
            hotel_data = partial

    if "visperas" in (args.url or "").lower() and not hotel_data.get("ubicacion"):
        visperas_reference = fallback.get_visperas_data()
        merged = visperas_reference.copy()
        for key, value in (hotel_data or {}).items():
            if value not in (None, ""):
                merged[key] = value
        hotel_data = merged

    if not hotel_data:
        print("[ERROR] No se pudieron obtener datos del hotel.")
        sys.exit(1)

    gbp_validation_meta: Dict[str, Any] = {}
    if GBPAuditorRef is not None:
        try:
            auditor = GBPAuditorRef()
            gbp_validation_meta = auditor.validate_location_only(
                hotel_name=hotel_data.get("nombre") or args.nombre or args.url or "",
                location=hotel_data.get("ubicacion")
                or hotel_data.get("ubicacion_validada")
                or hotel_data.get("ubicacion_original")
                or "",
            )
        except Exception as exc:  # pragma: no cover - dependencias externas
            print(f"[WARN] Validación geográfica rápida falló: {exc}")
    else:
        print("[WARN] GBP Auditor no disponible, se usará ubicación del scraper")

    resolved_location = gbp_validation_meta.get("resolved_location") if gbp_validation_meta else None
    if resolved_location:
        hotel_data["ubicacion_validada"] = resolved_location
        hotel_data["ubicacion"] = resolved_location
        hotel_data["ubicacion_fuente"] = gbp_validation_meta.get("location_source", "gbp_validation")
        print(
            f"[DATA] Validacion GBP ligera -> {resolved_location} "            f"(distancia: {gbp_validation_meta.get('distance_km', 'N/D')} km)"        )
    elif gbp_validation_meta.get("status") == "error":
        print(f"[WARN] Validación geográfica no disponible: {gbp_validation_meta.get('reason', 'error')}")

    # Ejecutar delivery
    output_dir = Path(args.output).resolve()
    
    if delivery_context:
        print(f"[INFO] Generación selectiva activada - {len(delivery_context.brechas_criticas)} brechas, {len(delivery_context.fugas_gbp)} fugas")
    
    manager = DeliveryManager(output_dir, provider_type=args.provider)
    manager.execute(args.package, hotel_data, context=delivery_context)
    
    # Log execution to memory
    final_target_id = hotel_data.get("nombre") or target_id
    memory.append_log({
        "target_id": final_target_id,
        "task_name": "execute",
        "package": args.package,
        "outcome": "success",
        "analysis_path": str(discovered_analysis.absolute()) if discovered_analysis else None,
    })
    print(f"[HARNESS] Ejecución registrada en memoria")
    
    print("\n[SUCCESS] Ejecución completada.")


def run_deploy_mode(args: argparse.Namespace) -> None:
    """Maneja el comando 'deploy' para despliegue remoto."""
    from modules.deployer.manager import DeployManager

    print("=" * 60)
    print("MODO DEPLOY - Despliegue Remoto v2.5 MVP")
    print("=" * 60)

    if not args.target:
        print("[ERROR] Se requiere --target (nombre del hotel o ruta a delivery_assets)")
        sys.exit(1)

    manager = DeployManager()

    # Run preflight only if requested
    if args.preflight:
        exit_code = manager.preflight(args.target)
        sys.exit(exit_code)

    # Run deploy (dry-run by default in v2.5)
    exit_code = manager.execute(
        target=args.target,
        method=args.method,
        dry_run=args.dry_run,
        verbose=args.debug,
    )
    sys.exit(exit_code)


def maybe_run_config_check(args: argparse.Namespace) -> None:
    if args.skip_check:
        print("[WARN]  Verificacion de configuracion omitida por usuario\n")
        return
    try:
        from modules.utils.config_checker import ConfigChecker

        print("=" * 60)
        print("VERIFICANDO CONFIGURACION DEL SISTEMA...")
        print("=" * 60)
        checker = ConfigChecker()
        if not checker.check(args):
            print("\n[FAIL] Problemas de configuracion detectados.")
            print("[IDEA] Usa --skip-check para continuar a pesar de advertencias")
            sys.exit(1)
        print("[OK] Configuracion validada - Iniciando analisis...\n")
    except Exception as exc:  # pragma: no cover - dependencias opcionales
        print(f"[WARN]  No se pudo ejecutar ConfigChecker: {exc}")
        if args.debug:
            import traceback

            traceback.print_exc()
        print("Continuando sin verificacion completa...\n")


def build_pipeline_options(args: argparse.Namespace) -> PipelineOptions:
    """Construye opciones de pipeline desde argumentos CLI."""
    output_dir = Path(args.output).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    return PipelineOptions(
        url=args.url,
        output_dir=output_dir,
        provider=args.provider,
        mode=args.mode,
        skip_posts=args.skip_posts,
        posts_max_wait=args.posts_max_wait,
        skip_competitors=args.skip_competitors,
        debug=args.debug,
    )


def run_setup_mode(args: argparse.Namespace) -> None:
    """Maneja el comando 'setup' para configuración interactiva y segura."""
    from modules.utils.secure_config_manager import SecureConfigManager
    import getpass

    print("=" * 60)
    print("IA HOTELES AGENT - CONFIGURACION INTERACTIVA (v2.11.0)")
    print("=" * 60)
    print("\nEsta herramienta configurará tus API Keys de forma segura.")
    
    scm = SecureConfigManager()
    
    # 1. Seleccionar Proveedor LLM
    print("\n1. Selecciona tu proveedor LLM principal:")
    print("   [1] DeepSeek (Recomendado - Económico)")
    print("   [2] Anthropic (Premium)")
    choice = input("\nSelección [1]: ").strip() or "1"
    provider = "deepseek" if choice == "1" else "anthropic"
    scm.set_key_secure("LLM_PROVIDER", provider, use_keychain=False)  # Guardamos preferencia en .env
    
    # 2. Configurar Clave del Proveedor
    key_name = "DEEPSEEK_API_KEY" if provider == "deepseek" else "ANTHROPIC_API_KEY"
    print(f"\n2. Ingresa tu {key_name}:")
    api_key = getpass.getpass("   Clave (oculta): ").strip()
    
    if not api_key:
        print("[ERROR] La clave no puede estar vacía.")
        sys.exit(1)

    # 3. Validar Clave (Opcional pero recomendado)
    print(f"\n3. Validando conexión con {provider}...")
    try:
        if provider == "deepseek":
            import requests
            headers = {"Authorization": f"Bearer {api_key}"}
            # Un simple llamado para listar modelos sirve de validación
            resp = requests.get("https://api.deepseek.com/models", headers=headers, timeout=10)
            resp.raise_for_status()
        else:
            from anthropic import Anthropic
            client = Anthropic(api_key=api_key)
            # Validación ligera para Anthropic
            client.models.list(limit=1)
            
        print(f"   [OK] Conexión validada exitosamente.")
    except Exception as e:
        print(f"   [WARN] No se pudo validar la clave: {e}")
        confirm = input("   ¿Deseas guardarla de todas formas? (s/n) [n]: ").lower()
        if confirm != 's':
            print("Configuración cancelada.")
            sys.exit(1)

    # 4. Elegir Almacenamiento
    print("\n4. ¿Dónde deseas guardar la clave?")
    print("   [1] Almacén Seguro (Keychain del sistema - RECOMENDADO)")
    print("   [2] Archivo local .env (Texto plano)")
    store_choice = input("\nSelección [1]: ").strip() or "1"
    use_keychain = store_choice == "1"
    success, location = scm.set_key_secure(key_name, api_key, use_keychain=use_keychain)
    
    if success:
        print(f"\n[SUCCESS] Clave guardada en {location}.")
        print("Tu sistema está listo para ejecutar auditorías.")
    else:
        print("\n[ERROR] No se pudo guardar la clave.")
        sys.exit(1)


def run_onboard_mode(args: argparse.Namespace) -> None:
    """Maneja el comando 'onboard' para capturar datos operativos del hotel."""
    from modules.onboarding import OnboardingForm
    from modules.onboarding.data_loader import load_onboarding_data, generate_slug
    
    print("=" * 60)
    print("IA HOTELES AGENT - ONBOARDING DE DATOS OPERATIVOS")
    print("=" * 60)
    print("\nEste formulario capturará datos operativos del hotel")
    print("para eliminar estimaciones en el análisis.\n")
    
    # Determinar nombre del hotel
    hotel_nombre = args.hotel_name or args.nombre or ""
    if not hotel_nombre and args.url:
        from urllib.parse import urlparse
        domain = urlparse(args.url).netloc.replace('www.', '').split('.')[0]
        hotel_nombre = domain.replace('-', ' ').replace('_', ' ').title()
    
    # Ejecutar formulario interactivo
    form = OnboardingForm(hotel_nombre=hotel_nombre)
    success = form.run_interactive()
    
    if not success:
        print("\n[INFO] Onboarding cancelado por el usuario.")
        sys.exit(0)
    
    # Guardar datos
    output_dir = Path(args.output) / "clientes"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    hotel_slug = generate_slug(hotel_nombre) if hotel_nombre else "hotel"
    if args.output_format == "yaml":
        output_path = output_dir / f"{hotel_slug}_onboarding.yaml"
        form.save_yaml(output_path)
    else:
        output_path = output_dir / f"{hotel_slug}_onboarding.json"
        form.save_json(output_path)
    
    print(f"\n[SUCCESS] Datos guardados en: {output_path}")
    
    # Mostrar resumen
    data = form.to_dict()
    ops = data.get('datos_operativos', {})
    print("\n📊 RESUMEN DE DATOS CAPTURADOS:")
    print(f"   Habitaciones: {ops.get('habitaciones', 'N/D')}")
    print(f"   Reservas/mes: {ops.get('reservas_mes', 'N/D')}")
    print(f"   Valor reserva: ${ops.get('valor_reserva_cop', 0):,} COP")
    print(f"   Canal directo: {ops.get('canal_directo_pct', 'N/A')}%")
    
    # Ejecutar auditoría si se solicitó
    if args.run_audit and args.url:
        print("\n" + "=" * 60)
        print("EJECUTANDO AUDITORÍA CON DATOS CONFIRMADOS...")
        print("=" * 60)
        
        # Cargar datos y ejecutar pipeline
        onboarding_data = load_onboarding_data(output_path)
        
        # Construir opciones con datos de onboarding
        options = PipelineOptions(
            url=args.url,
            output_dir=Path(args.output),
            provider=args.provider,
            mode=args.mode,
        )
        
        pipeline = AnalysisPipeline(options)
        results = pipeline.run(list(DEFAULT_STAGES))
        
        summarize_results(results)
    elif args.run_audit and not args.url:
        print("\n[WARN] No se puede ejecutar auditoría sin --url")
        print(f"   Ejecuta: python main.py audit --url <URL> --input-data {output_path}")
    else:
        print("\n🚀 PRÓXIMOS PASOS:")
        print(f"   1. Revisa el archivo: {output_path}")
        url_hint = args.url or '<URL>'
        print(f"   2. Ejecuta: python main.py audit --url {url_hint} --input-data {output_path}")
        print(f"   3. O usa: python main.py onboard --url {url_hint} --run-audit")


def run_audit_mode(args: argparse.Namespace) -> None:
    """Maneja el comando 'audit' o 'stage' usando el Agent Harness.
    
    ⚠️ DEPRECADO: Este comando usa el pipeline legacy v3.x (AnalysisPipeline).
    Para análisis nuevos, usar: python main.py v4complete --url <URL>
    """
    # Check for bypass mode (legacy)
    if getattr(args, "bypass_harness", False):
        _run_audit_legacy(args)
        return
    
    # Harness-enabled mode
    from agent_harness import AgentHarness, AgentTask
    # from modules.orchestrator.stage_handlers import StageHandlers  # Import moved to module level
    
    stages = list(DEFAULT_STAGES)
    if args.command == "stage":
        try:
            stages = normalize_stages(args.stages)
        except ValueError as exc:
            print(f"[ERROR] {exc}")
            sys.exit(1)

    maybe_run_config_check(args)
    
    # Deprecation warning
    print("\n" + "!" * 60)
    print("⚠️  ADVERTENCIA: Comando 'audit' está DEPRECADO")
    print("!" * 60)
    print("Este comando usa el pipeline legacy v3.x (AnalysisPipeline).")
    print("No aprovecha validación cruzada, escenarios financieros,")
    print("ni generación condicional de assets v4.0.")
    print("\nPara análisis nuevos, usar:")
    print(f"  python main.py v4complete --url {args.url}")
    print("!" * 60 + "\n")
    
    print("=" * 60)
    print(f"MODO AUDITORIA - Etapas: {', '.join(stages).upper()}")
    print("[HARNESS] Modo Agentico Activo")
    print("=" * 60)
    
    harness = AgentHarness(verbose=args.debug or True)
    
    # Register granular stage handlers
    options = build_pipeline_options(args)
    handlers = StageHandlers(options)
    
    harness.register_handler("geo_stage", handlers.handle_geo_stage)
    harness.register_handler("ia_stage", handlers.handle_ia_stage)
    harness.register_handler("seo_stage", handlers.handle_seo_stage)
    harness.register_handler("outputs_stage", handlers.handle_outputs_stage)
    
    # Use TaskContext.harness for delegation
    def _audit_handler_agentic(payload, context):
        # from modules.orchestrator.pipeline import AnalysisPipeline  # Import available at module level
        # context.harness is injected by AgentHarness.run_task
        pipeline = AnalysisPipeline(options, harness=context.harness)
        
        # Log context if available
        if context.previous_runs > 0:
            print(f"[AUDIT] Contexto previo disponible: {context.previous_runs} ejecuciones.")
        
        results = pipeline.run(payload.get("stages", list(DEFAULT_STAGES)))
        
        # Extract summary for memory
        summary = {
            "stages_run": payload.get("stages"),
            "execution_time": results.get("execution_time", 0.0),
            "hotel_name": "Hotel",
        }
        if "geo" in results:
            geo = results["geo"]
            summary["hotel_name"] = getattr(geo, "hotel_data", {}).get("nombre", "Hotel")
            summary["target_id"] = summary["hotel_name"]

        return {
            "results_raw": results,
            "summary": summary,
            "target_id": summary.get("target_id")
        }

    harness.register_handler("audit", _audit_handler_agentic)
    
    task = AgentTask(
        name="audit",
        payload={
            "url": args.url,
            "output": args.output,
            "provider": args.provider,
            "mode": args.mode,
            "skip_posts": args.skip_posts,
            "posts_max_wait": args.posts_max_wait,
            "skip_competitors": args.skip_competitors,
            "debug": args.debug,
            "stages": stages,
        },
    )
    
    # Semantic Routing: Harness will call _audit_handler_agentic
    result = harness.run_task(task)
    
    if not result.success:
        print(f"\n[ERROR] {result.error}")
        sys.exit(1)
    
    results_to_summarize = result.data.get("results_raw", {})
    if "execution_time" not in results_to_summarize:
        results_to_summarize["execution_time"] = result.duration_seconds

    summarize_results(results_to_summarize)


def _run_audit_legacy(args: argparse.Namespace) -> None:
    """Legacy audit mode (bypass harness)."""
    if args.command == "stage":
        try:
            stages = normalize_stages(args.stages)
        except ValueError as exc:
            print(f"[ERROR] {exc}")
            sys.exit(1)
    else:
        stages = list(DEFAULT_STAGES)

    maybe_run_config_check(args)

    options = build_pipeline_options(args)
    pipeline = AnalysisPipeline(options)

    try:
        results = pipeline.run(stages)
    except Exception as error:
        print(f"\nERROR: {error}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

    summarize_results(results)


def run_v4_audit_mode(args: argparse.Namespace) -> None:
    """Maneja el comando 'v4audit' para auditoría completa v4.0 con APIs."""
    from modules.auditors import V4ComprehensiveAuditor
    from pathlib import Path
    
    print("=" * 60)
    print("V4.0 COMPREHENSIVE AUDIT - API Integration Mode")
    print("=" * 60)
    print(f"\nURL: {args.url}")
    print(f"Features:")
    print("  - Rich Results Test API (Schema validation)")
    print("  - Google Places API (GBP data)")
    print("  - PageSpeed API (Performance metrics)")
    print("  - Cross-validation between sources")
    print()
    
    auditor = V4ComprehensiveAuditor()
    
    try:
        result = auditor.audit(args.url, hotel_name=args.nombre)
        
        # Save report
        output_dir = Path(args.output) / "v4_audit"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        safe_name = result.hotel_name.replace(" ", "_").lower()[:30]
        report_path = output_dir / f"{safe_name}_v4_audit.json"
        auditor.save_report(result, report_path)
        
        # Display summary
        print("\n" + "=" * 60)
        print("V4.0 AUDIT SUMMARY")
        print("=" * 60)
        print(f"\nHotel: {result.hotel_name}")
        print(f"Overall Confidence: {result.overall_confidence}")
        print(f"\nSchema Validation:")
        print(f"  - Hotel Schema: {result.schema.hotel_confidence}")
        print(f"  - FAQ Schema: {result.schema.faq_confidence}")
        print(f"  - Total Schemas: {result.schema.total_schemas}")
        print(f"\nGBP Data (via Places API):")
        if result.gbp.place_found:
            print(f"  - Found: {result.gbp.name}")
            print(f"  - Rating: {result.gbp.rating}/5 ({result.gbp.reviews} reviews)")
            print(f"  - Geo Score: {result.gbp.geo_score}/100")
            print(f"  - Photos: {result.gbp.photos}")
        else:
            print(f"  - Status: Not found in Places API")
        print(f"\nPerformance:")
        if result.performance.has_field_data:
            print(f"  - Mobile: {result.performance.mobile_score}/100")
            print(f"  - Desktop: {result.performance.desktop_score}/100")
        else:
            print(f"  - Status: {result.performance.status}")
        print(f"\nCross-Validation:")
        print(f"  - WhatsApp: {result.validation.whatsapp_status}")
        print(f"  - ADR: {result.validation.adr_status}")
        
        if result.critical_issues:
            print(f"\n⚠️  Critical Issues ({len(result.critical_issues)}):")
            for issue in result.critical_issues[:5]:
                print(f"  - {issue}")
        
        if result.recommendations:
            print(f"\n📋 Recommendations ({len(result.recommendations)}):")
            for rec in result.recommendations[:5]:
                print(f"  - {rec}")
        
        print(f"\n📄 Full report saved to: {report_path}")
        
    except Exception as e:
        print(f"\n[ERROR] Audit failed: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def summarize_results(results: Dict[str, object]) -> None:
    """Muestra resumen de resultados del pipeline."""
    from modules.utils.ui_colors import UIColors
    
    stages_run = [stage for stage in ("geo", "ia", "seo", "outputs") if stage in results]
    execution_time = results.get("execution_time", 0.0)
    if not stages_run:
        print(UIColors.warning("No se ejecutaron etapas."))
        return

    print("\n" + UIColors.bold("Resumen de etapas completadas:"))
    print(f"   - " + UIColors.info(", ".join(stage.upper() for stage in stages_run)))
    print(f"   - Tiempo acumulado: {execution_time:.1f} s")

    if "geo" in results:
        geo = results["geo"]  # type: ignore[assignment]
        hotel_name = getattr(geo, "hotel_data", {}).get("nombre", "Hotel")
        gbp_score = getattr(geo, "gbp_data", {}).get("score", 0)
        color = UIColors.get_score_color(gbp_score)
        print(f"   - Hotel: {hotel_name} · Score GBP: " + UIColors.colorize(f"{gbp_score}/100", color))

    if "ia" in results:
        ia = results["ia"]  # type: ignore[assignment]
        perdida = getattr(ia, "llm_analysis", {}).get("perdida_mensual_total", 0)
        provider = getattr(ia, "current_provider", "N/D")
        color = UIColors.RED if perdida > 5000000 else UIColors.YELLOW if perdida > 1000000 else UIColors.GREEN
        print(f"   - Perdida mensual estimada: " + UIColors.colorize(f"${perdida:,.0f} COP", color) + f" · Provider: {provider}")

    if "seo" in results:
        seo = results["seo"]  # type: ignore[assignment]
        credibility_score = getattr(seo, "credibility_score", 0)
        lost_bookings = getattr(seo, "estimated_lost_bookings", 0)
        color = UIColors.get_score_color(credibility_score)
        print(f"   - Credibilidad web: " + UIColors.colorize(f"{credibility_score}/100", color) + f" · Reservas perdidas: {lost_bookings:.1f}/mes")

    if "outputs" not in results:
        print("\n" + UIColors.info("Nota: La etapa de entregables no se ejecutó en esta corrida."))


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Doctor: full ecosystem health check (--doctor)
    if args.doctor:
        import subprocess as _sub
        _sub.run([sys.executable, str(Path(__file__).parent / "scripts" / "doctor.py")])
        sys.exit(0)

    ensure_url(parser, args)

    # Persistir URL si se proporcionó o se cargó
    if args.url:
        from agent_harness.memory import MemoryManager
        MemoryManager().save_state({"last_url": args.url})

    if args.command == "execute":
        maybe_run_config_check(args)
        run_execution_mode(args)
        sys.exit(0)
    
    if args.command == "setup":
        run_setup_mode(args)
        sys.exit(0)
    
    if args.command == "onboard":
        run_onboard_mode(args)
        sys.exit(0)
    
    if args.command == "spark":
        maybe_run_config_check(args)
        run_spark_mode(args)
        sys.exit(0)

    if args.command == "deploy":
        run_deploy_mode(args)
        # run_deploy_mode calls sys.exit internally

    if args.command == "v4audit":
        maybe_run_config_check(args)
        run_v4_audit_mode(args)
        sys.exit(0)

    if args.command == "v4audit":
        maybe_run_config_check(args)
        run_v4_audit_mode(args)
        sys.exit(0)

    if args.command == "v4complete":
        maybe_run_config_check(args)
        run_v4_complete_mode(args)
        sys.exit(0)

    if args.command in ("audit", "stage"):
        run_audit_mode(args)
        sys.exit(0)


def run_v4_complete_mode(args: argparse.Namespace) -> None:
    """Maneja el comando 'v4complete' - flujo completo v4.0 con módulos Python reales.
    
    Este comando integra:
    - AgentHarness para memoria y routing
    - Módulos v4.0: orchestration_v4, data_validation, financial_engine
    - Meta-Skills como orquestadores declarativos
    """
    from datetime import datetime
    from agent_harness import AgentHarness, AgentTask
    from agent_harness.memory import MemoryManager
    from modules.orchestration_v4 import OnboardingController, HotelInputs
    from modules.data_validation import CrossValidator
    from modules.data_validation.confidence_taxonomy import ConfidenceLevel
    from modules.financial_engine import ScenarioCalculator, HotelFinancialData
    from modules.financial_engine.scenario_calculator import ScenarioType
    from modules.financial_engine import resolve_adr_with_shadow, ADRResolutionResult
    from modules.financial_engine import calculate_price_with_shadow, PricingResolutionResult
    from modules.financial_engine.calculator_v2 import FinancialCalculatorV2
    from modules.financial_engine.harness_handlers import register_financial_handlers
    from modules.financial_engine.feature_flags import FinancialFeatureFlags, RolloutMode
    from pathlib import Path
    import json
    
    print("=" * 70)
    print("V4.0 COMPLETE - Flujo Integral con Módulos Reales")
    print("=" * 70)
    print("[HARNESS] Usando AgentHarness + Módulos v4.0 Python")
    print("[HARNESS] Flujo de dos fases: Hook → Validación → Assets")
    print("=" * 70)
    
    # Initialize harness and memory
    harness = AgentHarness(verbose=args.debug or True)
    memory = MemoryManager()
    memory.cleanup_old_sessions(days=20)
    
    # Register financial handlers with the harness
    register_financial_handlers(harness)
    
    # Check feature flags for harness delegation mode
    feature_flags = FinancialFeatureFlags()
    use_harness_for_financials = feature_flags.financial_v410_enabled and \
        feature_flags.financial_v410_mode in [RolloutMode.CANARY, RolloutMode.ACTIVE]
    
    # Create output directory
    output_dir = Path(args.output).resolve() / "v4_complete"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # FASE 1: Hook Generation (Automated)
    print("\n📍 FASE 1: Hook Generation (Automático)")
    print("-" * 70)
    
    # Parse permission mode from CLI args
    perm_mode = PermissionMode(getattr(args, "permission_mode", "auto"))
    print(f"🔐 Permission Mode: {perm_mode.value}")

    # Use Meta-Skill for orchestration but real modules for execution
    controller = OnboardingController(
        permission_mode=perm_mode,
    )
    
    # Detect region from URL or use default
    region = _detect_region_from_url(args.url)
    hotel_name = args.nombre or _extract_hotel_name_from_url(args.url)
    
    print(f"🎯 Hotel: {hotel_name}")
    print(f"🌍 Región detectada: {region}")
    
    # Start Phase 1 onboarding
    try:
        state = controller.start_onboarding(
            hotel_url=args.url,
            hotel_name=hotel_name,
            region=region
        )
        print(f"[OK] Phase 1 iniciada: {state.hotel_id}")
        print(f"📊 Progreso: {state.progress_percentage}%")
        
        if state.phase_1_result:
            print(f"\n💬 Hook Message:")
            print(f"   {state.phase_1_result.hook_message[:200]}...")
    except Exception as e:
        print(f"⚠️  Phase 1 usando estimación simple: {e}")
        state = None
    
    # FASE 2: Data Collection and Validation
    print("\n📍 FASE 2: Validación Cruzada")
    print("-" * 70)
    
    # Initialize cross-validator
    validator = CrossValidator()
    
    # Check for prior analysis
    discovered_analysis = memory.find_latest_analysis(args.url)
    if discovered_analysis:
        print(f"📂 Análisis previo encontrado: {discovered_analysis}")
    
    # Run v4audit to get real data
    print("\n🔍 Ejecutando auditoría v4.0 con APIs...")
    from modules.auditors import V4ComprehensiveAuditor

    # Permission gate: verificar si se permite la llamada externa costosa
    audit_op = OperationPermission(
        name="V4ComprehensiveAuditor.audit",
        estimated_cost=0.03,  # ~$0.03 USD por auditoria (Places API + scraping)
        is_external=True,
    )
    if not check_permission(audit_op, perm_mode):
        print("⚠️  Auditoría externa omitida por permission mode (chat/smart_approve).")
        print("   Usando datos por defecto para continuar.")
        audit_result = None
        audit_path = None
    else:
        try:
            auditor = V4ComprehensiveAuditor()
            audit_result = auditor.audit(args.url, hotel_name=hotel_name)

            print(f"[OK] Auditoría completada")
            print(f"   - Schema Hotel: {audit_result.schema.hotel_confidence}")
            print(f"   - GBP Score: {audit_result.gbp.geo_score}/100")
            print(f"   - WhatsApp: {audit_result.validation.whatsapp_status}")

            # Save audit report
            audit_path = output_dir / "audit_report.json"
            auditor.save_report(audit_result, audit_path)
            print(f"   💾 Guardado: {audit_path}")

        except Exception as e:
            print(f"⚠️  Auditoría falló: {e}")
            audit_result = None
            audit_path = None
    
    # Re-evaluar region si fallback a "nacional" y GBP address disponible
    if region == "nacional" and audit_result and hasattr(audit_result, 'gbp') and audit_result.gbp:
        inferred = _infer_region_from_address(audit_result.gbp.address)
        if inferred:
            region = inferred
            print(f"   Region inferida desde GBP: {region}")
    
    # Cross-validation checks
    print("\n🔍 Validación Cruzada:")
    
    # WhatsApp validation (web vs GBP vs input)
    whatsapp_web = audit_result.validation.phone_web if audit_result else None
    whatsapp_gbp = audit_result.validation.phone_gbp if audit_result else None
    
    if whatsapp_web and whatsapp_gbp:
        whatsapp_validation = validator.validate_whatsapp(whatsapp_web, whatsapp_gbp)
        print(f"   WhatsApp: {whatsapp_validation.confidence.name} (confidence: {whatsapp_validation._validation_result.match_percentage})")
    else:
        print(f"   WhatsApp: Datos insuficientes para validación")
        whatsapp_validation = None
    
    # Calculate Financial Scenarios
    print("\n📍 FASE 3: Escenarios Financieros")
    print("-" * 70)
    
    # Load onboarding data first (highest priority)
    onboarding_data = _load_latest_onboarding_data(args.url, hotel_name)
    
    if onboarding_data:
        campos_confirmados = onboarding_data.get('metadatos', {}).get('campos_confirmados', [])
        print(f"   ✅ Onboarding data loaded: {len(campos_confirmados)} campos confirmados")
        
        # Extract operational data from onboarding
        datos_operativos = onboarding_data.get('datos_operativos', {})
        rooms = datos_operativos.get('habitaciones', 10)
        
        reservas_mes = datos_operativos.get('reservas_mes')
        if reservas_mes and rooms:
            occupancy_rate = reservas_mes / (rooms * 30)
        else:
            occupancy_rate = 0.50
        
        canal_directo = datos_operativos.get('canal_directo_pct', 20.0)
        direct_channel_pct = canal_directo / 100
        
        # Extract ADR from onboarding if available
        adr_from_onboarding = datos_operativos.get('valor_reserva_cop')
        
        # Region is already detected from URL earlier in the flow
    else:
        print(f"   ℹ️  Using defaults (no fresh onboarding data found)")
        
        # Extract operational data from audit or use defaults
        rooms = _extract_rooms_from_audit(audit_result) if audit_result else 10
        
        # Region is already detected from URL (line 1404) — DO NOT overwrite
        # _extract_region_from_audit() always returns "default" (deprecated)
        # region = _extract_region_from_audit(audit_result) if audit_result else "default"
        
        occupancy_rate = 0.50  # Default 50%
        direct_channel_pct = 0.20  # Default 20%
        
        # No ADR from onboarding available
        adr_from_onboarding = None
    
    # Check if we should use harness for financial calculations
    adr_source = "unknown"  # Default, will be updated in fallback
    
    if use_harness_for_financials:
        print(f"[HARNESS] Usando financial handlers v4.1.0 (modo: {feature_flags.financial_v410_mode.value})")
        
        # Create task for v4 financial calculation
        financial_task = AgentTask(
            task_type="v4_financial_calculation",
            payload={
                "rooms": rooms,
                "region": region,
                "occupancy_rate": occupancy_rate,
                "direct_channel_percentage": direct_channel_pct,
                "hotel_id": args.url,
                "hotel_name": hotel_name
            }
        )
        
        # Run task through harness
        financial_result = harness.run_task(financial_task)
        
        if financial_result.success:
            result_data = financial_result.data
            adr_cop = result_data["adr_cop"]
            scenarios = result_data["scenarios"]
            expected_monthly = result_data["expected_monthly"]
            pricing_result_data = result_data["pricing"]
            
            # Convert scenarios back to ScenarioType format for compatibility
            from modules.financial_engine.scenario_calculator import ScenarioResult
            scenario_objects = {
                ScenarioType.CONSERVATIVE: ScenarioResult(
                    scenario_type=ScenarioType.CONSERVATIVE,
                    monthly_loss_cop=scenarios["conservative"]["monthly_loss_cop"],
                    annual_loss_cop=scenarios["conservative"]["annual_loss_cop"],
                    probability=scenarios["conservative"]["probability"]
                ),
                ScenarioType.REALISTIC: ScenarioResult(
                    scenario_type=ScenarioType.REALISTIC,
                    monthly_loss_cop=scenarios["realistic"]["monthly_loss_cop"],
                    annual_loss_cop=scenarios["realistic"]["annual_loss_cop"],
                    probability=scenarios["realistic"]["probability"]
                ),
                ScenarioType.OPTIMISTIC: ScenarioResult(
                    scenario_type=ScenarioType.OPTIMISTIC,
                    monthly_loss_cop=scenarios["optimistic"]["monthly_loss_cop"],
                    annual_loss_cop=scenarios["optimistic"]["annual_loss_cop"],
                    probability=scenarios["optimistic"]["probability"]
                )
            }
            scenarios = scenario_objects
            
            # Create pricing result object
            pricing_result = PricingResolutionResult(
                monthly_price_cop=pricing_result_data["monthly_price_cop"],
                tier=pricing_result_data["tier"],
                pain_ratio=pricing_result_data["pain_ratio"],
                is_compliant=pricing_result_data["is_compliant"],
                source=pricing_result_data["source"]
            )
            
            print(f"[HARNESS] Financial calculation completed via handlers")
        else:
            print(f"[HARNESS] Financial calculation failed: {financial_result.error}")
            print(f"[HARNESS] Falling back to direct calculation...")
            use_harness_for_financials = False
    
    # Fallback to direct calculation if harness not used or failed
    if not use_harness_for_financials:
        # Resolve ADR using v4.1.0 wrapper (backward compatible via feature flags)
        adr_result = resolve_adr_with_shadow(
            region=region,
            rooms=rooms,
            user_provided_adr=adr_from_onboarding,
            hotel_id=args.url,
            hotel_name=hotel_name,
        )
        adr_cop = adr_result.adr_cop
        adr_source = adr_result.source
        
        # Log ADR source for transparency
        source_display = {
            "regional_v410": "regional",
            "legacy_hardcode": "legacy",
            "user_provided": "onboarding",
        }.get(adr_result.source, adr_result.source)
        print(f"   ADR: ${adr_cop:,.0f} COP ({source_display}, confidence: {adr_result.confidence})")
        
        # Use FinancialCalculatorV2 for guaranteed validation
        calc_v2 = FinancialCalculatorV2()
        financial_input = {
            "rooms": rooms,
            "adr_cop": adr_cop,
            "occupancy_rate": occupancy_rate,
            "direct_channel_percentage": direct_channel_pct,
        }

        calc_result = calc_v2.calculate(financial_input)
        
        if calc_result.blocked:
            print(f"   ⚠️  FinancialCalculatorV2 blocked: {calc_result.status.value}")
            if calc_result.error_message:
                print(f"      Error: {calc_result.error_message}")
            if calc_result.validation_result:
                blocks = [b.field for b in calc_result.validation_result.blocks]
                print(f"      Blocked fields: {blocks}")
        
        scenarios = calc_result.scenarios if calc_result.scenarios else {}
        
        print(f"📊 Escenarios calculados:")
        if ScenarioType.CONSERVATIVE in scenarios:
            print(f"   Conservador: ${scenarios[ScenarioType.CONSERVATIVE].monthly_loss_cop:,.0f} COP/mes (70%)")
        if ScenarioType.REALISTIC in scenarios:
            print(f"   Realista: ${scenarios[ScenarioType.REALISTIC].monthly_loss_cop:,.0f} COP/mes (20%)")
        if ScenarioType.OPTIMISTIC in scenarios:
            print(f"   Optimista: ${scenarios[ScenarioType.OPTIMISTIC].monthly_loss_cop:,.0f} COP/mes (10%)")
        
        # Use FinancialCalculatorV2's weighted expected value
        expected_monthly = calc_result.get_realistic_loss() or 0.0
        if expected_monthly == 0.0 and scenarios:
            expected_monthly = (
                scenarios.get(ScenarioType.CONSERVATIVE, type('obj', (object,), {'monthly_loss_cop': 0})()).monthly_loss_cop * 0.70 +
                scenarios.get(ScenarioType.REALISTIC, type('obj', (object,), {'monthly_loss_cop': 0})()).monthly_loss_cop * 0.20 +
                scenarios.get(ScenarioType.OPTIMISTIC, type('obj', (object,), {'monthly_loss_cop': 0})()).monthly_loss_cop * 0.10
            )
        
        print(f"\n💰 Valor Esperado: ${expected_monthly:,.0f} COP/mes")
        
        # Calculate pricing using hybrid model
        pricing_result = calculate_price_with_shadow(
            rooms=rooms,
            expected_loss_cop=expected_monthly,
            hotel_id=args.url,
            hotel_name=hotel_name
        )
    
    print(f"\n💰 Pricing (Hybrid Model):")
    print(f"   Tier: {pricing_result.tier}")
    print(f"   Monthly Price: ${pricing_result.monthly_price_cop:,.0f} COP")
    print(f"   Pain Ratio: {pricing_result.pain_ratio:.2%}")
    print(f"   GATE Compliant: {'✅' if pricing_result.is_compliant else '❌'}")
    print(f"   Source: {pricing_result.source}")
    
    # Helper function to get scenario value safely
    def get_scenario_value(scenarios_dict, stype, default=0):
        if stype in scenarios_dict:
            return scenarios_dict[stype].monthly_loss_cop
        return default
    
    # Handle scenarios format - FinancialCalculatorV2 returns Dict[ScenarioType, FinancialScenario]
    scenarios_dict = {
        'conservative': get_scenario_value(scenarios, ScenarioType.CONSERVATIVE),
        'realistic': get_scenario_value(scenarios, ScenarioType.REALISTIC),
        'optimistic': get_scenario_value(scenarios, ScenarioType.OPTIMISTIC),
    }
    
    # Save scenarios
    scenarios_path = output_dir / "financial_scenarios.json"
    with open(scenarios_path, 'w', encoding='utf-8') as f:
        json.dump({
            'hotel': hotel_name,
            'url': args.url,
            'input_data': {
                'rooms': rooms,
                'adr_cop': adr_cop,
                'occupancy_rate': occupancy_rate,
                'direct_channel_percentage': direct_channel_pct
            },
            'scenarios': scenarios_dict,
            'expected_monthly_cop': expected_monthly,
            'pricing': {
                'tier': pricing_result.tier,
                'monthly_price_cop': pricing_result.monthly_price_cop,
                'pain_ratio': pricing_result.pain_ratio,
                'is_compliant': pricing_result.is_compliant,
                'source': pricing_result.source
            }
        }, f, indent=2, ensure_ascii=False)
    print(f"💾 Guardado: {scenarios_path}")

    # FASE 3.5: Generación de Documentos Comerciales
    print("\n📍 FASE 3.5: Documentos Comerciales v4.0")
    print("-" * 70)

    from modules.commercial_documents import (
        V4DiagnosticGenerator, V4ProposalGenerator,
        ValidationSummary, FinancialScenarios, Scenario
    )
    from modules.commercial_documents.data_structures import (
        DiagnosticDocument, ProposalDocument, AssetSpec, ValidatedField
    )
    from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper, Pain

    # Preparar datos para generadores - FASE 1: Poblar ValidationSummary con datos reales
    validated_fields = []

    # Track if data came from onboarding
    has_onboarding = onboarding_data is not None
    adr_from_onboarding_verified = adr_from_onboarding is not None and adr_from_onboarding > 0

    # WhatsApp field (verificado cruzando Web + GBP)
    if whatsapp_validation and whatsapp_validation.confidence == ConfidenceLevel.VERIFIED:
        validated_fields.append(ValidatedField(
            field_name="whatsapp_number",
            value=whatsapp_web,
            confidence=ConfidenceLevel.VERIFIED,
            sources=["Web", "GBP"],
            match_percentage=whatsapp_validation._validation_result.match_percentage if whatsapp_validation else 0.0,
            can_use_in_assets=True
        ))
    elif whatsapp_validation and whatsapp_validation.confidence == ConfidenceLevel.CONFLICT:
        validated_fields.append(ValidatedField(
            field_name="whatsapp_number",
            value=whatsapp_web,
            confidence=ConfidenceLevel.CONFLICT,
            sources=["Web", "GBP"],
            match_percentage=whatsapp_validation._validation_result.match_percentage if whatsapp_validation else 0.0,
            can_use_in_assets=True
        ))
    elif whatsapp_web:
        validated_fields.append(ValidatedField(
            field_name="whatsapp_number",
            value=whatsapp_web,
            confidence=ConfidenceLevel.ESTIMATED,
            sources=["Web"],
            match_percentage=0.5,
            can_use_in_assets=True
        ))
    elif getattr(audit_result.validation, 'whatsapp_html_detected', False):
        # WhatsApp boton existe en HTML pero no hay telefono en Schema
        validated_fields.append(ValidatedField(
            field_name="whatsapp_number",
            value="detected_via_html",
            confidence=ConfidenceLevel.ESTIMATED,
            sources=["HTML"],
            match_percentage=0.6,
            can_use_in_assets=True
        ))

    # Rooms field (del onboarding o audit o schema)
    if rooms and rooms > 0:
        confidence = ConfidenceLevel.VERIFIED if has_onboarding else ConfidenceLevel.ESTIMATED
        sources = ["Onboarding"] if has_onboarding else ["Audit"]
        validated_fields.append(ValidatedField(
            field_name="rooms",
            value=rooms,
            confidence=confidence,
            sources=sources,
            can_use_in_assets=True
        ))

    # ADR field
    if adr_cop and adr_cop > 0:
        confidence = ConfidenceLevel.VERIFIED if adr_from_onboarding_verified else ConfidenceLevel.ESTIMATED
        sources = ["Onboarding"] if adr_from_onboarding_verified else ["Benchmark"]
        validated_fields.append(ValidatedField(
            field_name="adr_cop",
            value=adr_cop,
            confidence=confidence,
            sources=sources,
            can_use_in_assets=True
        ))

    # Occupancy rate
    if occupancy_rate and occupancy_rate > 0:
        confidence = ConfidenceLevel.VERIFIED if has_onboarding else ConfidenceLevel.ESTIMATED
        sources = ["Onboarding"] if has_onboarding else ["Default"]
        validated_fields.append(ValidatedField(
            field_name="occupancy_rate",
            value=occupancy_rate,
            confidence=confidence,
            sources=sources,
            can_use_in_assets=False
        ))

    # Direct channel percentage
    if direct_channel_pct and direct_channel_pct > 0:
        confidence = ConfidenceLevel.VERIFIED if has_onboarding else ConfidenceLevel.ESTIMATED
        sources = ["Onboarding"] if has_onboarding else ["Default"]
        validated_fields.append(ValidatedField(
            field_name="direct_channel_percentage",
            value=direct_channel_pct,
            confidence=confidence,
            sources=sources,
            can_use_in_assets=False
        ))

    # Calcular overall_confidence basado en campos verificados
    verified_count = sum(1 for f in validated_fields if f.confidence == ConfidenceLevel.VERIFIED)
    overall_confidence = ConfidenceLevel.VERIFIED if verified_count >= 2 else (
        ConfidenceLevel.ESTIMATED if len(validated_fields) >= 2 else ConfidenceLevel.UNKNOWN
    )

    validation_summary = ValidationSummary(
        fields=validated_fields,
        overall_confidence=overall_confidence,
        conflicts=[]
    )

    print(f"[OK] ValidationSummary creado con {len(validated_fields)} campos:")
    for field in validated_fields:
        status = "[OK]" if field.confidence == ConfidenceLevel.VERIFIED else "[WARN]"
        print(f"   {status} {field.field_name}: {field.value} ({field.confidence.value})")

    # FASE 3: Validación semántica de escenarios
    conservative_value = int(get_scenario_value(scenarios, ScenarioType.CONSERVATIVE))
    realistic_value = int(get_scenario_value(scenarios, ScenarioType.REALISTIC))
    optimistic_value = int(get_scenario_value(scenarios, ScenarioType.OPTIMISTIC))
    
    # Permitir valores negativos en optimista (representan equilibrio/ganancia)
    # No ajustar silenciosamente a 0 - persistir valor real
    if optimistic_value < 0:
        print(f"[INFO] Escenario 'optimista' negativo ({optimistic_value}): representa EQUILIBRIO/GANANCIA")
    
    # Validar orden coherente: conservador >= realista >= optimista
    # Nota: Si optimista es negativo, puede ser menor que realista (eso es correcto)
    if conservative_value < realistic_value:
        print(f"[WARN] Escenario conservador (${conservative_value}) < realista (${realistic_value}) - ajustando")
        conservative_value = int(realistic_value * 1.2)
    
    # Solo ajustar optimista si es positivo pero mayor que realista (orden invertido)
    # Si es negativo, es correcto que sea 'menor' (representa ganancia)
    if realistic_value < optimistic_value and optimistic_value > 0:
        print(f"[WARN] Escenario realista (${realistic_value}) < optimista (${optimistic_value}) - ajustando")
        optimistic_value = int(realistic_value * 0.8)
    
    # Calcular opportunity_cop (valor absoluto para escenarios negativos)
    optimistic_opportunity = abs(optimistic_value) if optimistic_value <= 0 else 0
    
    financial_scenarios_obj = FinancialScenarios(
        conservative=Scenario(
            monthly_loss_min=conservative_value,
            monthly_loss_max=int(conservative_value * 1.2),
            probability=0.70,
            description="Peor caso plausible",
            monthly_opportunity_cop=0),
        realistic=Scenario(
            monthly_loss_min=int(realistic_value * 0.8),
            monthly_loss_max=int(realistic_value * 1.2),
            probability=0.20,
            description="Meta esperada",
            monthly_opportunity_cop=0),
        optimistic=Scenario(
            monthly_loss_min=int(optimistic_value * 0.8) if optimistic_value > 0 else int(optimistic_value * 1.2),
            monthly_loss_max=optimistic_value,
            probability=0.10,
            description="Mejor caso" if optimistic_value > 0 else "Caso de equilibrio (ahorro en comisiones)",
            monthly_opportunity_cop=optimistic_opportunity)
    )
    
    print(f"[OK] Escenarios financieros validados:")
    print(f"   Conservador: ${conservative_value:,.0f} COP/mes")
    print(f"   Realista: ${realistic_value:,.0f} COP/mes")
    print(f"   Optimista: ${optimistic_value:,.0f} COP/mes")

    # El diagnóstico se generará DESPUÉS de la validación de coherencia
    # para incluir el coherence_score correcto del gate
    diagnostic_path = None
    print("[INFO] Diagnóstico se generará después de validación de coherencia...")


    # Construir analytics_data para V4DiagnosticGenerator
    # Esto activa la seccion de transparencia analytics en el diagnostico
    from modules.analytics.google_analytics_client import GoogleAnalyticsClient
    from data_models.analytics_status import AnalyticsStatus

    # GA4 Property ID por hotel (CLI flag) — NO global en .env
    # GA4_CREDENTIALS_PATH si es global (mismo service account para todos)
    ga4_hotel_property_id = getattr(args, 'ga4_property_id', None) or None
    ga4_client = GoogleAnalyticsClient(property_id=ga4_hotel_property_id)
    ga4_available = ga4_client.is_available()

    analytics_status = AnalyticsStatus()
    analytics_status.ga4_available = ga4_available
    analytics_status.ga4_status_text = (
        f"✅ Conectado — datos de GA4 incluidos (Property: {ga4_hotel_property_id})"
        if ga4_available
        else "⚠️ No configurado (use --ga4-property-id para conectar)"
    )
    # Profound y Semrush son stubs en esta version
    analytics_status.profound_available = False
    analytics_status.profound_status_text = "⚠️ No disponible en esta version (API pendiente)"
    analytics_status.semrush_available = False
    analytics_status.semrush_status_text = "⚠️ No disponible en esta version (API pendiente)"

    # analytics_data activa el flujo GA4 o fallback cualitativo en _inject_analytics()
    # even when GA4 is not configured (use_ga4=False -> fallback to audit signals)
    analytics_data = {
        "use_ga4": ga4_available,  # True only if GA4 credentials exist
        "analytics_status": analytics_status,
        "ga4_property_id": ga4_hotel_property_id,  # por hotel, no global
        # hotel_data puede agregarse aqui para IATester integration futura
        "hotel_data": None,
    }

    print("\n Generando plan de assets...")
    pain_mapper = PainSolutionMapper()
    if audit_result:
        detected_pains = pain_mapper.detect_pains(audit_result, validation_summary, analytics_data,
                                                   whatsapp_html_detected=getattr(audit_result.validation, 'whatsapp_html_detected', False))
    elif analytics_data:
        # Sin audit pero con analytics: detectar solo pains de analytics
        detected_pains = pain_mapper.detect_pains_for_analytics(analytics_data)
    else:
        detected_pains = []

    print(f"   Problemas detectados: {len(detected_pains)}")
    for pain in detected_pains[:5]:  # Mostrar top 5
        print(f"   - {pain.name}: {pain.severity}")

    # Build extra confidence from metadata audit if available
    extra_confidence = None
    if audit_result and hasattr(audit_result, 'metadata') and audit_result.metadata and audit_result.metadata.has_issues:
        meta_conf = audit_result.metadata.confidence
        conf_score = 0.95 if meta_conf == "verified" else (0.7 if meta_conf == "estimated" else 0.5)
        extra_confidence = {
            "default_title": conf_score,
            "default_description": conf_score
        }
    
    # Generar plan de assets basado en problemas y confianza disponible
    asset_plan = pain_mapper.generate_asset_plan(detected_pains, validation_summary, extra_confidence)

    print(f"   Assets planificados: {len(asset_plan)}")
    for asset in asset_plan:
        print(f"   - {asset.asset_type}: {asset.reason} (confidence: {asset.confidence_required})")

    # Crear DiagnosticDocument completo con problemas reales detectados
    diagnostic_doc = DiagnosticDocument(
        path=str(diagnostic_path),
        problems=detected_pains,
        financial_impact=financial_scenarios_obj.realistic,
        generated_at=datetime.now().isoformat()
    )

    # Usar el precio del pricing wrapper (calculado correctamente con 5% pain ratio)
    # NO recalcular con fórmula legacy que tiene mínimo de 800k
    price_monthly = pricing_result.monthly_price_cop

    # Calcular ROI proyectado (ahorro anual / costo anual)
    # Usar expected_monthly del financial calculator
    annual_savings = expected_monthly * 12
    annual_cost = price_monthly * 12
    roi_projected = round((annual_savings / annual_cost), 2) if annual_cost > 0 else 3.5

    # FASE 4: Gate de Coherencia - Validar antes de generar propuesta
    from modules.commercial_documents.coherence_config import get_coherence_config
    from modules.commercial_documents.coherence_validator import CoherenceValidator
    from modules.commercial_documents.data_structures import DiagnosticDocument, ProposalDocument
    
    config = get_coherence_config()
    
    # Crear documentos temporales para validación completa del GATE
    temp_diagnostic = DiagnosticDocument(
        path="",
        problems=detected_pains,
        financial_impact=financial_scenarios_obj.realistic,
        generated_at=datetime.now().isoformat()
    )
    
    # Crear propuesta temporal para validación (sin guardar)
    temp_proposal = ProposalDocument(
        path="",
        price_monthly=price_monthly,
        assets_proposed=asset_plan,
        roi_projected=roi_projected,
        generated_at=datetime.now().isoformat()
    )
    
    # Usar CoherenceValidator para cálculo real (no simple)
    coherence_validator = CoherenceValidator()
    pre_coherence_report = coherence_validator.validate(
        temp_diagnostic,
        temp_proposal,
        asset_plan,
        validation_summary,
        whatsapp_html_detected=getattr(audit_result.validation, 'whatsapp_html_detected', False) if audit_result else False
    )
    pre_coherence_score = pre_coherence_report.overall_score
    
    # DEBUG: Print each check score
    for check in pre_coherence_report.checks:
        print(f"   [DEBUG] {check.name}: score={check.score:.3f}, passed={check.passed}")
    
    threshold = config.get_threshold('overall_coherence')
    is_blocking = config.is_blocking('overall_coherence')
    
    print(f"🔒 Gate de Coherencia:")
    print(f"   Score calculado: {pre_coherence_score:.2f} (umbral: {threshold})")
    print(f"   Checks: {len([c for c in pre_coherence_report.checks if c.passed])}/{len(pre_coherence_report.checks)} pasados")
    if pre_coherence_report.warnings:
        print(f"   Advertencias: {len(pre_coherence_report.warnings)}")
    
    if pre_coherence_score < threshold:
        warning_msg = f"Coherencia insuficiente ({pre_coherence_score:.2f} < {threshold})"
        if is_blocking:
            print(f"   ❌ BLOQUEADO: {warning_msg}")
            print("   Se generará solo diagnóstico, NO propuesta comercial.")
            generate_proposal = False
        else:
            print(f"   ⚠️  ADVERTENCIA: {warning_msg}")
            print("   Continuando con generación de propuesta (modo no-bloqueante)")
            generate_proposal = True
    else:
        print(f"   [OK] Coherencia aceptable - Generando propuesta completa")
        generate_proposal = True


    # Regenerar diagnóstico con coherence_score correcto del gate
    print("\n📍 Regenerando diagnóstico con coherence_score validado...")
    diagnostic_gen = V4DiagnosticGenerator()
    diagnostic_path = diagnostic_gen.generate(
        audit_result=audit_result,
        validation_summary=validation_summary,
        financial_scenarios=financial_scenarios_obj,
        hotel_name=hotel_name,
        hotel_url=args.url,
        output_dir=str(output_dir),
        coherence_score=pre_coherence_score,
        region=region,  # FASE-DRECONEXION-V6: Pasar region para templates V6
        analytics_data=analytics_data,  # INTEGRACION-ANALYTICS-E2E: activa transparencia analytics
    )
    print(f"[OK] Diagnóstico regenerado con coherence_score: {pre_coherence_score:.2f}")

    # Crear diagnostic_summary para proposal
    from modules.commercial_documents.data_structures import (
        DiagnosticSummary, 
        adapt_validation_confidence,
        calculate_quick_wins,
        extract_top_problems
    )

    # Calcular problemas dinámicamente desde audit_result
    critical_problems_count = len(audit_result.critical_issues) if audit_result else 0
    quick_wins_count = calculate_quick_wins(audit_result, validation_summary)
    top_problems = extract_top_problems(audit_result, limit=5)

    # FASE-G: Extraer brechas reales con impacto desde _identify_brechas
    brechas_reales = diagnostic_gen._identify_brechas(audit_result) if audit_result else []

    diagnostic_summary = DiagnosticSummary(
        hotel_name=hotel_name,
        critical_problems_count=critical_problems_count,
        quick_wins_count=quick_wins_count,
        overall_confidence=adapt_validation_confidence(validation_summary.overall_confidence),
        top_problems=top_problems,
        validated_data_summary={
            'whatsapp': whatsapp_validation.to_dict() if whatsapp_validation else {},
            'rooms': rooms,
            'adr': adr_cop,
            'occupancy_rate': occupancy_rate,
            'direct_channel_percentage': direct_channel_pct,
        },
        coherence_score=pre_coherence_score,  # Usar el score calculado por CoherenceValidator
        brechas_reales=brechas_reales,  # FASE-G: impactos reales para proposal
    )

    # Generar propuesta solo si pasa el gate (o si no es bloqueante)
    proposal_path = None
    if generate_proposal:
        proposal_gen = V4ProposalGenerator()
        proposal_path = proposal_gen.generate(
            diagnostic_summary=diagnostic_summary,
            financial_scenarios=financial_scenarios_obj,
            asset_plan=asset_plan,
            hotel_name=hotel_name,
            output_dir=str(output_dir),
            audit_result=audit_result,
            pricing_result=pricing_result,  # FASE 13: Usar pricing_result para consistencia con financial_scenarios.json
            region=region,  # FASE-DRECONEXION-V6: Pasar region para templates V6
            analytics_data=analytics_data,  # ANALYTICS-02: pasar analytics_data al proposal
        )
    if proposal_path:
        print(f"[OK] Propuesta generada: {proposal_path}")
    else:
        print("⚠️  Propuesta NO generada debido a baja coherencia")

    # Usar el precio del pricing wrapper (calculado correctamente con 5% pain ratio)
    # NO recalcular con fórmula legacy que tiene mínimo de 800k
    price_monthly = pricing_result.monthly_price_cop

    # Calcular ROI proyectado (ahorro anual / costo anual)
    # Usar expected_monthly del financial calculator
    annual_savings = expected_monthly * 12
    annual_cost = price_monthly * 12
    roi_projected = round((annual_savings / annual_cost), 2) if annual_cost > 0 else 3.5

    proposal_doc = ProposalDocument(
        path=str(proposal_path) if proposal_path else "",
        price_monthly=price_monthly,
        assets_proposed=asset_plan,
        roi_projected=roi_projected,
        generated_at=datetime.now().isoformat()
    )
    print(f"   💵 Precio calculado: ${price_monthly:,.0f} COP/mes | ROI: {roi_projected:.1f}x")

    # FASE 3.6: Content Scrubber + Document Quality Gate (FASE-B)
    print("\n📍 FASE 3.6: Content Scrubber + Quality Gate (FASE-B)")
    print("-" * 70)

    try:
        from modules.postprocessors.content_scrubber import ContentScrubber
        from modules.postprocessors.document_quality_gate import DocumentQualityGate
        import json

        # Build hotel_data from available variables
        hotel_data = {}
        if region:
            hotel_data["region"] = region
        # Extract city/state from audit_result if available
        if audit_result and hasattr(audit_result, 'hotel_name'):
            hotel_data["hotel_name"] = audit_result.hotel_name
        # Extract city from GBP address for region placeholder scrubbing
        if audit_result and hasattr(audit_result, 'gbp') and audit_result.gbp and hasattr(audit_result.gbp, 'address'):
            addr = audit_result.gbp.address or ""
            # Format: "..., CityName, Department, Country" - take first city-like component
            parts = [p.strip() for p in addr.split(',')]
            for part in parts:
                # Skip road markers, departments, countries
                if any(skip in part.lower() for skip in ['vía', 'vereda', 'km', 'departamento', 'colombia', 'risaralda']):
                    continue
                # Likely the city (first significant noun phrase)
                if part and len(part) > 2 and not part.isupper():
                    hotel_data["city"] = part
                    break

        scrubber = ContentScrubber()

        # Scrub diagnostic document
        if diagnostic_path and Path(diagnostic_path).exists():
            with open(diagnostic_path, 'r', encoding='utf-8') as f:
                diag_content = f.read()
            diag_scrub = scrubber.scrub(diag_content, hotel_data, "diagnostico")
            if diag_scrub.fix_count > 0:
                print(f"   [SCRUB] Diagnostic: {diag_scrub.fix_count} fix(es) applied")
                for fix in diag_scrub.fixes_applied:
                    print(f"      - {fix}")
                with open(diagnostic_path, 'w', encoding='utf-8') as f:
                    f.write(diag_scrub.scrubbed)
                # Read back the scrubbed content for quality gate
                diag_text = diag_scrub.scrubbed
            else:
                print(f"   [OK] Diagnostic: clean, no fixes needed")
                diag_text = diag_content
        else:
            diag_text = ""
            print("   [SKIP] Diagnostic document not available for scrubbing")

        # Scrub proposal document
        prop_text = ""
        if proposal_path and Path(proposal_path).exists():
            with open(proposal_path, 'r', encoding='utf-8') as f:
                prop_content = f.read()
            prop_scrub = scrubber.scrub(prop_content, hotel_data, "propuesta")
            if prop_scrub.fix_count > 0:
                print(f"   [SCRUB] Proposal: {prop_scrub.fix_count} fix(es) applied")
                for fix in prop_scrub.fixes_applied:
                    print(f"      - {fix}")
                with open(proposal_path, 'w', encoding='utf-8') as f:
                    f.write(prop_scrub.scrubbed)
                prop_text = prop_scrub.scrubbed
            else:
                print(f"   [OK] Proposal: clean, no fixes needed")
                prop_text = prop_content
        else:
            print("   [SKIP] Proposal document not available for scrubbing")

        # Run quality gate on scrubbed documents
        gate = DocumentQualityGate()

        diag_result = gate.validate_document(diag_text, "diagnostico", hotel_data) if diag_text else None
        prop_result = gate.validate_document(prop_text, "propuesta", hotel_data) if prop_text else None

        all_issues = []
        if diag_result:
            all_issues.extend(diag_result.issues)
        if prop_result:
            all_issues.extend(prop_result.issues)

        blockers = [i for i in all_issues if i.severity == "blocker"]
        warnings = [i for i in all_issues if i.severity == "warning"]

        if all_issues:
            print(f"   [WARN] Quality gate: {len(all_issues)} issue(s) after scrubbing")
            for issue in all_issues[:5]:
                print(f"      [{issue.severity.upper()}] Line {issue.line_number}: {issue.message}")
            if blockers:
                print(f"   ⚠️  {len(blockers)} blocker(s) remain after scrubbing — document logged but delivery proceeds")
        else:
            print(f"   [OK] Quality gate: PASSED — all documents clean")

        # Store results in locals for downstream use
        quality_gate_issues = all_issues
        quality_gate_blockers = blockers
        quality_gate_warnings = warnings

    except Exception as e:
        print(f"   [WARN] Content scrubber/quality gate failed: {e}")
        quality_gate_issues = []
        quality_gate_blockers = []
        quality_gate_warnings = []

    # FASE 4: Generación de Assets con Coherencia
    print("\n📍 FASE 4: Generación de Assets Validados")
    print("-" * 70)

    from modules.asset_generation import V4AssetOrchestrator

    orchestrator = V4AssetOrchestrator(output_base_dir=str(output_dir))

    asset_result = None
    try:
        if audit_result is None:
            print("   [SKIP] Sin audit_result - generacion de assets omitida")
        else:
            asset_result = orchestrator.generate_assets(
                audit_result=audit_result,
                validation_summary=validation_summary,
                diagnostic_doc=diagnostic_doc,
                proposal_doc=proposal_doc,
                hotel_name=hotel_name,
                hotel_url=args.url,
                analytics_data=analytics_data  # ANALYTICS-FIX-01: activar pains de analytics
            )

        print(f"[OK] Assets generados: {len(asset_result.generated_assets)}")
        print(f"   Fallidos: {len(asset_result.failed_assets)}")
        print(f"   Coherencia: {asset_result.coherence_report.overall_score:.2f}")

        for asset in asset_result.generated_assets:
            print(f"   📄 {asset.asset_type}: {asset.preflight_status}")

    except Exception as e:
        print(f"⚠️  Generación de assets falló: {e}")
        asset_result = None
    
    # FASE 4.5: Publication Gates - Verificar readiness para publicación
    print("\n📍 FASE 4.5: Publication Gates (Quality Checks)")
    print("-" * 70)
    
    from modules.quality_gates.publication_gates import (
        run_publication_gates,
        check_publication_readiness,
        PublicationGateConfig
    )
    
    # Build assessment dict from all available data
    assessment = {
        "url": args.url,
        "hotel_name": hotel_name,
        "validation_summary": {
            "whatsapp_status": whatsapp_validation.confidence.name if whatsapp_validation else "UNKNOWN",
            "overall_confidence": validation_summary.overall_confidence.value if validation_summary else "UNKNOWN",
            "hard_contradictions_count": 0,
            "conflicts": validation_summary.conflicts if validation_summary else [],
        },
        "financial_data": {
            "rooms": rooms,
            "adr_cop": adr_cop,
            "occupancy_rate": occupancy_rate,
            "direct_channel_percentage": direct_channel_pct,
        },
        "coherence_score": asset_result.coherence_report.overall_score if asset_result else 0.0,
        "critical_issues": audit_result.critical_issues if audit_result else [],
        "critical_issues_detected": audit_result.critical_issues if audit_result else [],
        "evidence_coverage": 0.95,  # Default assumption
        "metrics": {
            "coherence_score": asset_result.coherence_report.overall_score if asset_result else 0.0,
        },
        "quality_gate_issues": locals().get("quality_gate_issues", []),
        "quality_gate_blockers": locals().get("quality_gate_blockers", []),
        "quality_gate_warnings": locals().get("quality_gate_warnings", []),
    }
    
    # Enrich assessment with document texts for content quality gate (FASE-B)
    if diagnostic_path and Path(diagnostic_path).exists():
        try:
            with open(diagnostic_path, 'r', encoding='utf-8') as f:
                assessment["diagnostico_text"] = f.read()
        except Exception:
            assessment["diagnostico_text"] = ""
    if proposal_path and Path(proposal_path).exists():
        try:
            with open(proposal_path, 'r', encoding='utf-8') as f:
                assessment["propuesta_text"] = f.read()
        except Exception:
            assessment["propuesta_text"] = ""
    assessment["hotel_data"] = {"region": region} if region else {}
    
    # Run publication gates
    gate_config = PublicationGateConfig()
    gate_results = run_publication_gates(assessment, gate_config)
    readiness_report = check_publication_readiness(assessment)
    
    print(f"🔒 Publication Gates:")
    for result in gate_results:
        icon = "✅" if result.passed else "❌"
        print(f"   {icon} {result.gate_name}: {result.message}")
    
    print(f"\n📋 Publication Readiness: {readiness_report['status']}")
    if readiness_report['blocking_issues']:
        print(f"   ⚠️  Bloqueos: {len(readiness_report['blocking_issues'])}")
        for issue in readiness_report['blocking_issues']:
            print(f"      - {issue['gate']}: {issue['message']}")
    else:
        print(f"   ✅ Listo para publicación")
    
    # FASE 4.6: Consistency Checker - Validación cruzada obligatoria
    print("\n📍 FASE 4.6: Consistency Checker (Validación Cruzada)")
    print("-" * 70)
    
    from data_validation.consistency_checker import ConsistencyChecker, CanonicalAssessment
    
    # Build CanonicalAssessment from audit and validation data
    claims = []
    if audit_result and audit_result.validation:
        for field_name, value in [
            ("whatsapp", audit_result.validation.phone_web),
            ("adr", audit_result.validation.adr_web),
        ]:
            if value:
                claims.append({
                    "field_name": field_name,
                    "value": str(value),
                    "confidence": audit_result.validation.whatsapp_status if field_name == "whatsapp" else "estimated"
                })
    
    canonical = CanonicalAssessment(
        assessment_id=str(uuid4()),
        hotel_name=hotel_name,
        claims=claims
    )
    
    consistency_checker = ConsistencyChecker()
    consistency_report = consistency_checker.check_assessment_consistency(canonical)
    
    print(f"🔍 Consistency Report:")
    print(f"   Estado: {'CONSISTENTE' if consistency_report.is_consistent else 'INCONSISTENTE'}")
    print(f"   Conflictos Hard: {consistency_report.hard_conflicts_count}")
    print(f"   Conflictos Soft: {consistency_report.soft_conflicts_count}")
    print(f"   Confidence Score: {consistency_report.confidence_score:.2f}")
    
    if consistency_report.inconsistencies:
        print(f"   ⚠️  Inconsistencias detectadas: {len(consistency_report.inconsistencies)}")
        for inconsistency in consistency_report.inconsistencies[:3]:
            print(f"      - {inconsistency}")
    
    # Add consistency to assessment for later use
    assessment['consistency_report'] = consistency_report.to_dict()
    
    # FASE 7: Delivery Packaging - Automated ZIP creation
    print("\n📍 FASE 7: Delivery Packaging (Automated)")
    print("-" * 70)

    delivery_zip_path = None
    try:
        from modules.delivery.delivery_packager import DeliveryPackager

        # Get hotel_id from hotel_name
        hotel_id = hotel_name.lower().replace(" ", "_").replace("-", "_").replace(".", "")

        packager = DeliveryPackager(
            base_output_dir=str(output_dir),
            deliveries_dir=str(output_dir / "deliveries")
        )

        # Find diagnostic and proposal paths
        diag_path = str(diagnostic_path) if diagnostic_path else None
        prop_path = str(proposal_path) if proposal_path else None

        # Find output directory where assets were generated
        asset_output_dir = str(output_dir / hotel_id)

        delivery_zip_path = packager.package(
            hotel_id=hotel_id,
            output_dir=asset_output_dir,
            diagnostic_path=diag_path,
            proposal_path=prop_path
        )

        print(f"   [OK] Delivery package created: {delivery_zip_path}")

    except Exception as e:
        print(f"   [WARN] Delivery packaging failed: {e}")
        delivery_zip_path = None

    # FASE 10: Health Dashboard - System Health Metrics
    print("\n📍 FASE 10: Health Dashboard (System Health Monitor)")
    print("-" * 70)

    health_dashboard_path = None
    try:
        from modules.monitoring import HealthMetricsCollector, HealthDashboardGenerator, ExecutionMetrics

        # Collect metrics from this execution
        collector = HealthMetricsCollector()
        
        if asset_result:
            # Start timing for this hotel
            collector.start_execution(hotel_id, hotel_name)
            
            # Collect metrics from asset result
            metrics = collector.collect_from_result(asset_result)
            
            # End timing
            collector.end_execution()
        else:
            # Create metrics with basic info if no asset result
            metrics = ExecutionMetrics(
                hotel_id=hotel_id,
                hotel_name=hotel_name,
                timestamp=datetime.now(),
                assets_generated=0,
                assets_failed=0,
                success_rate=0.0,
                avg_confidence=0.0,
                execution_time=0.0,
                errors=["Asset generation failed"],
                warnings=[]
            )
            collector.add_metrics(metrics)

        # Generate dashboard
        generator = HealthDashboardGenerator()
        
        # Ensure output directory exists
        health_output_dir = output_dir / "health_dashboard"
        health_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save dashboard
        dashboard_files = generator.save_dashboard(
            collector.get_all_metrics(),
            str(health_output_dir / "health_dashboard.html")
        )
        
        health_dashboard_path = dashboard_files.get("html")
        health_summary_path = dashboard_files.get("json")
        
        print(f"   [OK] Health dashboard generated: {health_dashboard_path}")
        if health_summary_path:
            print(f"   [OK] Health summary: {health_summary_path}")

    except Exception as e:
        print(f"   [WARN] Health dashboard generation failed: {e}")
        health_dashboard_path = None

    # Guardar referencia completa en Agent Harness
    memory.append_log({
        'target_id': args.url,
        'task_name': 'v4complete',
        'url': args.url,
        'hotel_name': hotel_name,
        'outcome': 'success',
        'outputs': {
            'diagnostic_path': str(diagnostic_path),
            'proposal_path': str(proposal_path),
            'audit_json': str(audit_path) if audit_path else None,
            'coherence_json': str(output_dir / 'v4_audit' / 'coherence_validation.json'),
            'assets_generated': [a.asset_type for a in asset_result.generated_assets] if asset_result else [],
            'asset_result_path': str(output_dir / 'v4_audit' / 'asset_generation_report.json') if asset_result else None,
            'delivery_zip_path': delivery_zip_path,
            'health_dashboard_path': health_dashboard_path
        },
        'timestamp': datetime.now().isoformat()
    })

    # Generate Report
    print("\n📍 FASE 5: Generación de Reporte")
    print("-" * 70)
    
    report = {
        'v4_complete': True,
        'hotel_name': hotel_name,
        'url': args.url,
        'region': region,
        'hotel_id': state.hotel_id if state else None,
        'phases': {
            'phase_1_hook': {
                'completed': state is not None,
                'progress': state.progress_percentage if state else 30
            },
            'phase_2_validation': {
                'whatsapp_status': whatsapp_validation.confidence.name if whatsapp_validation else 'UNKNOWN',
                'whatsapp_confidence': whatsapp_validation.confidence.value if whatsapp_validation else 0.0
            },
            'phase_3_scenarios': {
                'conservative': get_scenario_value(scenarios, ScenarioType.CONSERVATIVE),
                'realistic': get_scenario_value(scenarios, ScenarioType.REALISTIC),
                'optimistic': get_scenario_value(scenarios, ScenarioType.OPTIMISTIC),
                'expected': expected_monthly
            },
            'phase_4_publication_gates': {
                'ready': readiness_report['ready'],
                'status': readiness_report['status'],
                'gate_results': readiness_report['gate_results'],
                'blocking_issues': readiness_report['blocking_issues']
            },
            'phase_5_consistency_check': {
                'is_consistent': consistency_report.is_consistent,
                'hard_conflicts': consistency_report.hard_conflicts_count,
                'soft_conflicts': consistency_report.soft_conflicts_count,
                'confidence_score': consistency_report.confidence_score,
                'inconsistencies': consistency_report.inconsistencies
            }
        },
        'modules_used': [
            'orchestration_v4.OnboardingController',
            'data_validation.CrossValidator',
            'data_validation.MetadataValidator',
            'financial_engine.ScenarioCalculator',
            'auditors.V4ComprehensiveAuditor',
            'quality_gates.publication_gates'
        ],
        'coherence_score': pre_coherence_score,
        'assets_generated': [
            {
                'asset_type': a.asset_type,
                'filename': a.filename,
                'path': a.path,
                'preflight_status': a.preflight_status,
                'confidence_score': a.confidence_score
            }
            for a in asset_result.generated_assets
        ] if asset_result else [],
        'financial_data': {
            'scenarios': {
                'conservative': get_scenario_value(scenarios, ScenarioType.CONSERVATIVE),
                'realistic': get_scenario_value(scenarios, ScenarioType.REALISTIC),
                'optimistic': get_scenario_value(scenarios, ScenarioType.OPTIMISTIC),
            },
            'expected_monthly': expected_monthly,
        },
        'pricing': {
            'monthly_price_cop': pricing_result.monthly_price_cop if pricing_result else None,
            'tier': pricing_result.tier if pricing_result else None,
        },
        # ANALYTICS-01: Persistir analytics_status en v4_complete_report.json
        'analytics': (
            {
                'ga4_available': analytics_data.get('analytics_status').ga4_available,
                'ga4_status': analytics_data.get('analytics_status').ga4_status_text,
                'ga4_error': analytics_data.get('analytics_status').ga4_error,
                'profound_available': analytics_data.get('analytics_status').profound_available,
                'profound_status': analytics_data.get('analytics_status').profound_status_text,
                'semrush_available': analytics_data.get('analytics_status').semrush_available,
                'semrush_status': analytics_data.get('analytics_status').semrush_status_text,
                'missing_credentials': analytics_data.get('analytics_status').missing_credentials(),
                'is_complete': analytics_data.get('analytics_status').is_complete(),
                'timestamp': analytics_data.get('analytics_status').timestamp.isoformat(),
            }
            if analytics_data and analytics_data.get('analytics_status')
            else {'available': False, 'status': 'analytics_data no disponible'}
        )
    }
    
    report_path = output_dir / "v4_complete_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Reporte completo guardado: {report_path}")
    
    # Log to memory - v4.1.0 enriquecido con metadatos
    log_entry = {
        'target_id': args.url,
        'task_name': 'v4complete',
        'url': args.url,
        'hotel_name': hotel_name,
        'hotel_id': state.hotel_id if state else None,
        'outcome': 'success',
        'timestamp': datetime.now().isoformat(),

        # Metadatos de coherencia v4.1.0
        'coherence_score': asset_result.coherence_report.overall_score if asset_result else 0.0,
        'coherence_checks_passed': len([c for c in asset_result.coherence_report.checks if c.passed]) if asset_result else 0,
        'coherence_checks_total': len(asset_result.coherence_report.checks) if asset_result else 0,

        # Fases completadas
        'phases_completed': [
            'phase_1_hook',
            'phase_2_validation',
            'phase_3_scenarios',
            'phase_3.5_documents',
            'phase_4_assets' if asset_result else None,
            'phase_5_report'
        ],

        # Conteos
        'problems_detected': len(detected_pains) if 'detected_pains' in locals() else 0,
        'assets_planned': len(asset_plan) if 'asset_plan' in locals() else 0,
        'assets_generated': len(asset_result.generated_assets) if asset_result else 0,
        'assets_failed': len(asset_result.failed_assets) if asset_result else 0,

        # Referencias a archivos generados
        'outputs': {
            'diagnostic_path': str(diagnostic_path) if 'diagnostic_path' in locals() else None,
            'proposal_path': str(proposal_path) if 'proposal_path' in locals() else None,
            'audit_json': str(audit_path) if audit_path else None,
            'scenarios_json': str(scenarios_path),
            'report_json': str(report_path),
            'coherence_json': str(Path(asset_result.output_dir) / 'v4_audit' / 'coherence_validation.json') if asset_result and asset_result.output_dir else None,
            'assets_output_dir': str(asset_result.output_dir) if asset_result else None
        },

        # Datos financieros
        'financial': {
            'scenario_conservative': get_scenario_value(scenarios, ScenarioType.CONSERVATIVE),
            'scenario_realistic': get_scenario_value(scenarios, ScenarioType.REALISTIC),
            'scenario_optimistic': get_scenario_value(scenarios, ScenarioType.OPTIMISTIC),
            'expected_monthly': expected_monthly,
            'price_proposed': proposal_doc.price_monthly if 'proposal_doc' in locals() else None,
            'roi_projected': proposal_doc.roi_projected if 'proposal_doc' in locals() else None
        },

        # Validación cruzada
        'validation': {
            'whatsapp_status': whatsapp_validation.confidence.name if whatsapp_validation else 'UNKNOWN',
            'whatsapp_confidence': whatsapp_validation._validation_result.match_percentage if whatsapp_validation else 0.0,
            'overall_confidence': audit_result.overall_confidence if audit_result else 'UNKNOWN'
        }
    }

    memory.append_log(log_entry)

    # También guardar referencia para acceso rápido
    memory.save_analysis_reference(
        target_id=args.url,
        analysis_path=output_dir,
        metadata={
            'type': 'v4complete',
            'coherence_score': log_entry['coherence_score'],
            'hotel_name': hotel_name,
            'timestamp': log_entry['timestamp']
        }
    )
    
    # Display final summary
    print("\n" + "=" * 70)
    print("V4.0 COMPLETE - RESUMEN FINAL")
    print("=" * 70)
    print(f"\n🏨 Hotel: {hotel_name}")
    print(f"🔗 URL: {args.url}")
    print(f"🌍 Región: {region}")
    print(f"\n💰 Proyección Financiera:")
    print(f"   Rango: ${get_scenario_value(scenarios, ScenarioType.CONSERVATIVE):,.0f} - ${get_scenario_value(scenarios, ScenarioType.OPTIMISTIC):,.0f} COP/mes")
    print(f"   Valor esperado: ${expected_monthly:,.0f} COP/mes")
    print(f"\n📁 Archivos generados en: {output_dir}/")
    print(f"   - 01_DIAGNOSTICO_Y_OPORTUNIDAD.md")
    print(f"   - 02_PROPUESTA_COMERCIAL.md")
    print(f"   - v4_complete_report.json")
    print(f"   - audit_report.json")
    print(f"   - financial_scenarios.json")
    if asset_result:
        print(f"   - delivery_assets/")
        print(f"     ├── whatsapp_button/")
        print(f"     ├── faq_page/")
        print(f"     └── ...")
    
    print("\n" + "=" * 70)
    print("✨ Flujo v4.0 completado exitosamente")
    print("=" * 70)
    print("\n⚠️  NOTA: Este es un análisis preliminar.")
    print("    Para precisar las cifras, ejecute con datos operativos:")
    print(f"    python main.py onboard --url {args.url}")


def _detect_region_from_url(url: str) -> str:
    """Detecta la región basada en la URL o contenido."""
    url_lower = url.lower()
    if any(x in url_lower for x in ['visperas', 'salento', 'armenia', 'quindio', 'calarca',
          'cafetero', 'finca', 'montenegro', 'filandia', 'circasia', 'termales']):
        return 'eje_cafetero'
    elif any(x in url_lower for x in ['cartagena', 'santa marta', 'barranquilla']):
        return 'caribe'
    elif any(x in url_lower for x in ['medellin', 'antioquia', 'guatape']):
        return 'antioquia'
    elif any(x in url_lower for x in ['bogota', 'cundinamarca']):
        return 'centro'
    return 'nacional'


def _infer_region_from_address(address: str) -> str | None:
    """Infiere region turistica desde direccion del GBP."""
    if not address:
        return None
    addr_lower = address.lower()
    REGION_PATTERNS = {
        'eje_cafetero': ['armenia', 'quindio', 'quindío', 'pereira', 'risaralda',
                         'manizales', 'caldas', 'salento', 'filandia', 'calarca',
                         'montenegro', 'circasia'],
        'caribe': ['cartagena', 'barranquilla', 'santa marta', 'sincelejo'],
        'antioquia': ['medellin', 'medellín', 'antioquia', 'guatape', 'guatapé',
                       'rionegro', 'jardin', 'jardín'],
        'centro': ['bogota', 'bogotá', 'cundinamarca', 'chia', 'cajica'],
        'valle': ['cali', 'valle del cauca', 'palmira', 'buga'],
        'llanos': ['villavicencio', 'meta', 'yopal', 'casanare'],
        'san_andres': ['san andres', 'san andrés', 'providencia'],
    }
    for region_key, patterns in REGION_PATTERNS.items():
        if any(p in addr_lower for p in patterns):
            return region_key
    return None


def _load_latest_onboarding_data(hotel_url: str, hotel_name: str) -> Dict[str, Any] | None:
    """Carga datos de onboarding más recientes del hotel si existen y son frescos (< 24h).
    
    Args:
        hotel_url: URL del hotel
        hotel_name: Nombre del hotel
        
    Returns:
        Diccionario con datos de onboarding o None si no existe/no es fresco
    """
    import yaml
    from datetime import datetime, timezone, timedelta
    from modules.onboarding.data_loader import generate_slug
    
    output_dir = Path("output/clientes")
    if not output_dir.exists():
        return None
    
    hotel_slug = generate_slug(hotel_name)
    onboarding_file = output_dir / f"{hotel_slug}_onboarding.yaml"
    
    if not onboarding_file.exists():
        return None
    
    try:
        with open(onboarding_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data or 'metadatos' not in data:
            return None
        
        fecha_captura_str = data.get('metadatos', {}).get('fecha_captura')
        if not fecha_captura_str:
            return None
        
        fecha_captura = datetime.fromisoformat(fecha_captura_str.replace('Z', '+00:00'))
        ahora = datetime.now(timezone.utc)
        
        if fecha_captura.tzinfo is None:
            fecha_captura = fecha_captura.replace(tzinfo=timezone.utc)
        
        diferencia = ahora - fecha_captura
        if diferencia > timedelta(hours=24):
            return None
        
        return data
        
    except Exception as e:
        print(f"   ⚠️  Error cargando onboarding: {e}")
        return None


def _extract_hotel_name_from_url(url: str) -> str:
    """Extrae el nombre del hotel de la URL."""
    from urllib.parse import urlparse
    domain = urlparse(url).netloc.replace('www.', '').split('.')[0]
    return domain.replace('-', ' ').replace('_', ' ').title()


def _extract_rooms_from_audit(audit_result) -> int:
    """Extrae el número de habitaciones del resultado de auditoría.
    
    @deprecated: Usar _load_latest_onboarding_data() en su lugar.
    Los datos de onboarding ahora tienen precedencia sobre los de auditoría.
    """
    # Try to get from schema or default to 10
    if hasattr(audit_result, 'schema') and audit_result.schema:
        # This would need to be extended based on actual audit result structure
        pass
    return 10


def _extract_region_from_audit(audit_result) -> str:
    """Extrae la región del resultado de auditoría.
    
    @deprecated: La región ahora se detecta directamente de la URL
    en run_v4_complete_mode() usando _detect_region_from_url().
    """
    # Try to get region from various sources
    if hasattr(audit_result, 'gbp') and audit_result.gbp:
        # Could extract from GBP data
        pass
    if hasattr(audit_result, 'geo') and audit_result.geo:
        # Could extract from geo data
        pass
    return "default"


def _extract_hotel_data_from_diagnostic(content: str) -> dict:
    """Extrae datos del hotel desde el frontmatter YAML del diagnóstico."""
    import re
    hotel_data = {}

    # Extraer YAML frontmatter
    match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        yaml_content = match.group(1)
        # Parsear líneas simples key: value
        for line in yaml_content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                hotel_data[key.strip()] = value.strip()

    return hotel_data


if __name__ == "__main__":
    main()
