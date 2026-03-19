from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import json
import csv
from datetime import datetime

from modules.delivery.delivery_context import DeliveryContext
from modules.delivery.generators.schema_gen import SchemaGenerator
from modules.validation import PlanValidator, ContentValidator
from modules.delivery.generators.faq_gen import FAQGenerator
from modules.delivery.generators.geo_gen import GeoContentGenerator
from modules.delivery.generators.seo_fix_gen import SEOFixGenerator
from modules.delivery.generators.report_gen import IAReportGenerator
from modules.delivery.generators.wa_button_gen import WhatsAppButtonGenerator
from modules.delivery.generators.content_gen import ContentGenerator
from modules.delivery.generators.booking_bar_gen import BookingBarGenerator
from modules.delivery.generators.deploy_instructions_gen import DeployInstructionsGenerator
from modules.delivery.generators.certificate_gen import CertificateGenerator
from modules.utils.data_validator import normalize_hotel_data

@dataclass
class AssetSpec:
    """Especificación de un asset a generar."""
    type: str
    required: bool = False
    reason: str = ""
    data: Dict[str, Any] = field(default_factory=dict)

class DeliveryManager:
    """Orchestrates the delivery of assets based on the selected package."""
    
    def __init__(self, output_dir: Path, provider_type: str = "auto"):
        self.output_dir = output_dir
        self.provider_type = provider_type
        self.schema_gen = SchemaGenerator()
        self.faq_gen = FAQGenerator(provider_type)
        self.geo_gen = GeoContentGenerator()
        self.seo_fix_gen = SEOFixGenerator()
        self.report_gen = IAReportGenerator()
        self.wa_button_gen = WhatsAppButtonGenerator()
        self.content_gen = ContentGenerator(provider_type)
        self.booking_bar_gen = BookingBarGenerator()
        self.deploy_instructions_gen = DeployInstructionsGenerator()
        self.certificate_gen = CertificateGenerator()

    def execute(self, package: str, hotel_data: Dict[str, Any], 
                context: Optional[DeliveryContext] = None,
                recommended_package: Optional[str] = None) -> None:
        """Ejecuta el pipeline de delivery con generación selectiva.
        
        Args:
            package: Nombre del paquete (starter_geo, pro_aeo, elite)
            hotel_data: Datos básicos del hotel
            context: Contexto enriquecido con brechas/fugas (NUEVO v3.5)
        """
        print(f"\n[DELIVERY v3.5] Iniciando ejecución para paquete: {package.upper()}")
        
        # NUEVO: Si hay contexto, mostrar resumen de brechas
        if context:
            self._print_context_summary(context)
        else:
            print("   [INFO] Sin contexto de diagnóstico - generando assets base")
        
        # Store package for use in implementation guide
        self.current_package = package
        self.recommended_package = recommended_package
        
        delivery_dir = self.output_dir / "delivery_assets"
        delivery_dir.mkdir(exist_ok=True)

        hotel_data = normalize_hotel_data(hotel_data)
        normalized_location = hotel_data.get("ubicacion") or "N/D"
        location_source = hotel_data.get("ubicacion_fuente", "desconocida")
        print(f"   [DATA] Ubicacion normalizada -> {normalized_location} (fuente: {location_source})")
        
        package_lower = package.lower()
        include_plus_assets = "plus" in package_lower or "elite" in package_lower
        
        # Construir cola de generación dinámica
        generation_queue = self._build_generation_queue(package, context)
        
        print(f"\n   [QUEUE] {len(generation_queue)} assets programados:")
        for asset in generation_queue:
            status = "✓" if asset.required else "?"
            reason_display = asset.reason[:50] + "..." if len(asset.reason) > 50 else asset.reason
            print(f"      [{status}] {asset.type}: {reason_display}")
        
        # Lógica de piloto_30d: paquete limitado
        if package_lower == "piloto_30d":
            print(f"   [PILOTO] Modo limitado: 30 días, $800K COP")
            include_geo = True
            include_pro = False
            include_piloto = True
            max_faqs = 10
        else:
            include_geo = any(key in package_lower for key in ("starter", "geo", "pro", "aeo", "elite"))
            include_pro = any(key in package_lower for key in ("pro", "aeo", "elite"))
            include_piloto = False
            max_faqs = 50

        if include_pro:
            # v3.3.1: FAQPage Integration - Generate FAQs first to inject into Schema
            print(f"   [v3.3.1] Generando FAQs para integración en Schema (count: {max_faqs})...")
            faqs_list = self.faq_gen.generate_list(hotel_data, count=max_faqs)
            hotel_data["faqs"] = faqs_list
            
            self._generate_schema(hotel_data, delivery_dir)
            
            # Persist CSV for the client
            filename = "10_optimized_faqs.csv" if max_faqs == 10 else "50_optimized_faqs.csv"
            faqs_csv = "Pregunta,Respuesta\n" + "\n".join([f'"{f["pregunta"]}","{f["respuesta"]}"' for f in faqs_list])
            (delivery_dir / filename).write_text(faqs_csv, encoding="utf-8")
            print(f"   [OK] {filename} created")

            self._generate_transversal_assets(hotel_data, delivery_dir)

            if include_plus_assets:
                self._generate_wa_button(hotel_data, delivery_dir)
                self._generate_conversion_article(hotel_data, delivery_dir)
                self._generate_posts_placeholders(delivery_dir)
                self._generate_photos_brief(delivery_dir)

                # Barra de reserva móvil (si hay motor detectado)
                self._generate_booking_bar(hotel_data, delivery_dir)
        
        # Certificados solo para Elite PLUS
        if "elite" in package_lower and "plus" in package_lower:
            self._generate_certificates(hotel_data, delivery_dir)
        else:
            print("   [SKIP] Schema y FAQs completas reservados para paquetes Pro/Elite")
        
        if include_piloto:
            self._generate_piloto_assets(hotel_data, delivery_dir)

        if include_geo:
            self._generate_geo_assets(hotel_data, delivery_dir)

        # Instrucciones de despliegue específicas para CMS (después de generar todos los assets)
        if include_pro and include_plus_assets:
            assets_for_instructions = [
                p.name
                for p in delivery_dir.rglob("*")
                if p.is_file() and p.name != "manifest.json"
            ]
            self._generate_deploy_instructions(hotel_data, delivery_dir, sorted(set(assets_for_instructions)))

        # Organizar archivos en carpetas por roles (v2.5) al final
        self._organize_by_roles(delivery_dir)

        # Checklist y manifest deben generarse post-organización
        self._generate_validation_checklist(delivery_dir, package, include_geo, include_pro, include_piloto)
        
        # v3.1.0: Automated Review Quality Gate
        review_status = self._validate_delivery_assets(delivery_dir)
        
        self._generate_manifest(hotel_data, delivery_dir, assets_generated=[], package=package, review_status=review_status, recommended_package=self.recommended_package)

        print(f"[DELIVERY] Activos generados y validados en: {delivery_dir}")

    def _validate_delivery_assets(self, delivery_dir: Path) -> Dict[str, Any]:
        """Valida activos de delivery usando Validation Engine local."""
        print("   [GUARD] Iniciando Quality Gate (Validation Engine)...")
        
        findings: List[Dict[str, Any]] = []
        severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        
        # Validación de coherencia de paquete
        if self.recommended_package and hasattr(self, 'current_package'):
            normalized_generated = self.current_package.lower().replace(" ", "_")
            normalized_recommended = self.recommended_package.lower().replace(" ", "_")
            if normalized_generated != normalized_recommended:
                findings.append({
                    "severity": "HIGH",
                    "message": f"PAQUETE_MISMATCH: Recomendado '{self.recommended_package}' pero se generó '{self.current_package}'. Inconsistencia detectada."
                })
                severity_counts["HIGH"] += 1
        
        try:
            plan_validator = PlanValidator()
            plan_result = plan_validator.validate()
            
            if not plan_result.passed:
                for err in plan_result.errors:
                    findings.append({"severity": "HIGH", "message": f"Plan Maestro: {err}"})
                    severity_counts["HIGH"] += 1
                for warn in plan_result.warnings:
                    findings.append({"severity": "MEDIUM", "message": f"Plan Maestro: {warn}"})
                    severity_counts["MEDIUM"] += 1
            
            content_validator = ContentValidator()
            
            for file_path in delivery_dir.rglob("*.md"):
                try:
                    content = file_path.read_text(encoding="utf-8")
                    content_result = content_validator.validate(content)
                    
                    for err in content_result.errors:
                        findings.append({
                            "severity": "HIGH",
                            "message": f"{file_path.name}: {err}"
                        })
                        severity_counts["HIGH"] += 1
                    
                    for warn in content_result.warnings:
                        findings.append({
                            "severity": "MEDIUM",
                            "message": f"{file_path.name}: {warn}"
                        })
                        severity_counts["MEDIUM"] += 1
                except Exception as e:
                    findings.append({
                        "severity": "LOW",
                        "message": f"{file_path.name}: Error al leer - {e}"
                    })
                    severity_counts["LOW"] += 1
            
            if severity_counts["HIGH"] > 0:
                print(f"   [WARN] Se detectaron {severity_counts['HIGH']} problemas criticos.")
            else:
                print("   [OK] Kit de entrega certificado por Validation Engine.")
            
            return {
                "status": "completed",
                "severity_counts": severity_counts,
                "findings": findings,
                "checks_run": plan_result.checks_run + sum(
                    content_validator.validate(f.read_text(encoding="utf-8")).checks_run
                    for f in delivery_dir.rglob("*.md")
                    if f.is_file()
                ) if list(delivery_dir.rglob("*.md")) else plan_result.checks_run
            }
        except Exception as e:
            print(f"   [WARN] Error en Quality Gate: {e}")
            return {"status": "error", "message": str(e), "severity_counts": severity_counts, "findings": findings}

    def _print_context_summary(self, context: DeliveryContext) -> None:
        """Muestra resumen del contexto de diagnóstico."""
        perdida = context.get_total_perdida_mensual()
        print(f"   [CONTEXT] Pérdida mensual detectada: ${perdida:,.0f} COP")
        if context.brechas_criticas:
            print(f"   [CONTEXT] {len(context.brechas_criticas)} brechas críticas")
        if context.fugas_gbp:
            print(f"   [CONTEXT] {len(context.fugas_gbp)} fugas GBP")
        if context.seo_issues:
            criticos = len([i for i in context.seo_issues if i.get("priority") == "CRÍTICO"])
            print(f"   [CONTEXT] {len(context.seo_issues)} issues SEO ({criticos} críticos)")

    def _build_generation_queue(self, package: str, 
                                context: Optional[DeliveryContext]) -> List[AssetSpec]:
        """Construye cola dinámica de assets basada en contexto."""
        
        queue = []
        package_lower = package.lower()
        
        # === ASSETS BASE (siempre incluidos según paquete) ===
        queue.append(AssetSpec(type="schema", required=True, reason="Base del paquete"))
        
        if "pro" in package_lower or "elite" in package_lower or "starter" in package_lower:
            queue.append(AssetSpec(type="geo_playbook", required=True, reason="Base del paquete"))
            queue.append(AssetSpec(type="review_plan", required=True, reason="Base del paquete"))
        
        # === ASSETS CONDICIONALES (v3.5: generación selectiva) ===
        
        if context:
            # SEO Fix Kit: solo si hay issues SEO detectados
            should_seo, reason = context.should_generate("seo_fix_kit")
            if should_seo:
                queue.append(AssetSpec(type="seo_fix_kit", required=False, reason=reason,
                                       data={"seo_issues": context.seo_issues}))
            
            # WhatsApp Button: solo si hay fuga SIN_WHATSAPP_VISIBLE
            should_wa, reason = context.should_generate("whatsapp_button")
            if should_wa:
                fuga = context.get_whatsapp_fuga()
                queue.append(AssetSpec(type="whatsapp_button", required=False, reason=reason,
                                       data={"fuga": fuga} if fuga else {}))
            
            # Booking Bar: solo si hay motor detectado
            should_bar, reason = context.should_generate("booking_bar")
            if should_bar:
                queue.append(AssetSpec(type="booking_bar", required=False, reason=reason))
            
            # FAQs: solo si hay brecha FAQ
            should_faq, reason = context.should_generate("faqs")
            if should_faq:
                queue.append(AssetSpec(type="faqs", required=False, reason=reason))
            
            # Photos Brief: solo si hay fuga de fotos
            should_photos, reason = context.should_generate("photos_brief")
            if should_photos:
                queue.append(AssetSpec(type="photos_brief", required=False, reason=reason))
            
            # Content: basado en brechas de conversión
            if context.has_brecha_type("conversión") or context.has_brecha_type("conversion"):
                queue.append(AssetSpec(type="content", required=False, 
                                       reason="Brecha de conversión detectada"))
        else:
            # Fallback: generar assets básicos (comportamiento anterior)
            queue.append(AssetSpec(type="seo_fix_kit", required=False, reason="Sin contexto"))
            queue.append(AssetSpec(type="whatsapp_button", required=False, reason="Sin contexto"))
            queue.append(AssetSpec(type="booking_bar", required=False, reason="Sin contexto"))
        
        return queue

    def _generate_asset_with_context(self, spec: AssetSpec, hotel_data: Dict[str, Any],
                                      context: Optional[DeliveryContext]) -> Optional[str]:
        """Genera un asset con contexto y justificación."""
        
        reason = spec.reason
        extra_data = spec.data
        
        try:
            if spec.type == "seo_fix_kit":
                seo_issues = extra_data.get("seo_issues", []) if extra_data else []
                return self._generate_seo_fix_kit(hotel_data, seo_issues=seo_issues, reason=reason)
            
            elif spec.type == "whatsapp_button":
                fuga = extra_data.get("fuga") if extra_data else None
                return self._generate_wa_button(hotel_data, fuga=fuga, reason=reason)
            
            elif spec.type == "booking_bar":
                return self._generate_booking_bar(hotel_data)
            
            elif spec.type == "faqs":
                return self._generate_faqs(hotel_data, reason=reason)
            
            elif spec.type == "photos_brief":
                self._generate_photos_brief(self.output_dir)
                return "fotos_brief.md"
            
            elif spec.type == "content":
                return self._generate_content(hotel_data, reason=reason)
            
        except Exception as e:
            print(f"   [ERROR] Falló generación de {spec.type}: {e}")
            if spec.required:
                raise
            return None
        
        return None

    def _generate_piloto_assets(self, hotel_data: Dict[str, Any], output_dir: Path):
        """Genera activos específicos para el piloto de 30 días."""
        print("   Generando activos del piloto 30 días...")
        
        # Schema básico (sin propiedades avanzadas)
        schema_json = self.schema_gen.generate(hotel_data)
        (output_dir / "hotel-schema-basic.json").write_text(schema_json, encoding="utf-8")
        print("   [OK] hotel-schema-basic.json (Schema simplificado)")
        
        # 10 FAQs
        faqs_csv = self.faq_gen.generate(hotel_data, count=10)
        (output_dir / "10_faqs_piloto.csv").write_text(faqs_csv, encoding="utf-8")
        print("   [OK] 10_faqs_piloto.csv")
        
        # GEO reducido
        geo_assets = self.geo_gen.generate(hotel_data)
        basic_geo = f"""# Playbook GEO - Piloto 30 Días

## Optimizaciones Básicas de Google Business Profile

### Semana 1-2: Fotos y Descripción
1. Sube 5 fotos de calidad (fachada, recepción, habitación, amenidades, servicio)
2. Actualiza descripción en 2 párrafos (quiénes eres + experiencia del cliente)
3. Verifica categoría correcta

### Semana 2-3: Preguntas y Respuestas
1. Responde todas las preguntas existentes
2. Añade 5 nuevas preguntas frecuentes (usa el archivo de FAQs)

### Semana 4: Tracking
1. Anota el número de consultas directas (puedes verlas en Google Search Console)
2. Compara con la semana 1

### Resultado esperado
- +15% en consultas directas desde "cerca de mí"
- Mayor aparición en búsquedas locales
"""
        (output_dir / "geo_playbook_basic.md").write_text(basic_geo, encoding="utf-8")
        print("   [OK] geo_playbook_basic.md")
        
        # GEO Strategy Guide (v2.6.4 - content_standards_geo)
        geo_strategy = self.geo_gen.generate_geo_strategy_guide(hotel_data)
        (output_dir / "guia_estrategia_geo_aeo.md").write_text(geo_strategy, encoding="utf-8")
        print("   [OK] guia_estrategia_geo_aeo.md (Estrategia GEO/AEO)")
        
        # Template de tracking semanal
        tracking_template = """# Tracking Semanal - Piloto 30 Días

## Instrucciones
Completa esta tabla cada viernes con los datos de tu Google Business Profile y Google Search Console.

| Métrica | Semana 1 | Semana 2 | Semana 3 | Semana 4 | Meta |
|---------|----------|----------|----------|----------|------|
| Consultas directas | _ | _ | _ | _ | +15% |
| Llamadas | _ | _ | _ | _ | +10 |
| Solicitudes de indicaciones | _ | _ | _ | _ | +20% |
| Visitas a web | _ | _ | _ | _ | +15% |
| Google Maps: Posición promedio | _ | _ | _ | _ | Top 5 |
| ChatGPT: ¿Apareces? | No | _ | _ | _ | Sí |

## Análisis
- Si semana 4 ≥ meta: Excelente. Hablamos del plan Pro AEO.
- Si semana 4 < meta: Revisamos qué faltó y se ajusta.
"""
        (output_dir / "weekly_tracking_template.md").write_text(tracking_template, encoding="utf-8")
        print("   [OK] weekly_tracking_template.md")

    def _generate_schema(self, hotel_data: Dict[str, Any], output_dir: Path):
        print("   Generating JSON-LD Schema...")
        schema_json = self.schema_gen.generate(hotel_data)
        (output_dir / "hotel-schema.json").write_text(schema_json, encoding="utf-8")
        print("   [OK] hotel-schema.json created")

    def _generate_faqs(self, hotel_data: Dict[str, Any], output_dir: Path = None, 
                        max_count: int = 50, reason: str = None) -> str:
        if output_dir is None:
            output_dir = self.output_dir / "delivery_assets"
            output_dir.mkdir(exist_ok=True)
        
        print(f"   Generating AI-Optimized FAQs (count: {max_count})...")
        faqs_csv = self.faq_gen.generate(hotel_data, count=max_count, reason=reason)
        filename = "10_optimized_faqs.csv" if max_count == 10 else "50_optimized_faqs.csv"
        (output_dir / filename).write_text(faqs_csv, encoding="utf-8")
        print(f"   [OK] {filename} created")
        return filename

    def _generate_transversal_assets(self, hotel_data: Dict[str, Any], output_dir: Path,
                                      seo_issues: List[Dict] = None, reason: str = None):
        self._generate_implementation_guide(output_dir, hotel_data)
        seo_fix = self.seo_fix_gen.generate(hotel_data, seo_issues=seo_issues, reason=reason)
        (output_dir / "seo_fix_kit.md").write_text(seo_fix, encoding="utf-8")
        print("   [OK] seo_fix_kit.md created")

        ia_report = self.report_gen.generate(hotel_data)
        (output_dir / "dashboard_visibilidad_ia.md").write_text(ia_report, encoding="utf-8")
        print("   [OK] dashboard_visibilidad_ia.md created")

    def _generate_seo_fix_kit(self, hotel_data: Dict[str, Any], 
                              seo_issues: List[Dict] = None,
                              reason: str = None) -> str:
        """Genera SEO Fix Kit con contexto opcional."""
        delivery_dir = self.output_dir / "delivery_assets"
        delivery_dir.mkdir(exist_ok=True)
        
        seo_fix = self.seo_fix_gen.generate(hotel_data, seo_issues=seo_issues, reason=reason)
        (delivery_dir / "seo_fix_kit.md").write_text(seo_fix, encoding="utf-8")
        print("   [OK] seo_fix_kit.md created")
        return "seo_fix_kit.md"

    def _generate_wa_button(self, hotel_data: Dict[str, Any], output_dir: Path = None,
                            fuga: Dict = None, reason: str = None) -> str:
        """Genera código de botón WhatsApp flotante con tracking (sin LLM)."""
        if output_dir is None:
            output_dir = self.output_dir / "delivery_assets"
            output_dir.mkdir(exist_ok=True)
        
        print("   Generando botón WhatsApp con tracking...")
        result = self.wa_button_gen.generate(hotel_data, fuga=fuga, reason=reason)

        (output_dir / "boton_whatsapp_codigo.html").write_text(result["html_code"], encoding="utf-8")
        print("   [OK] boton_whatsapp_codigo.html created")

        # v3.3.1: wa_gtm_snippet.json removed (Obsolete/Sin IT focus)

        (output_dir / "guia_boton_whatsapp.md").write_text(result["implementation_guide"], encoding="utf-8")
        print("   [OK] guia_boton_whatsapp.md created")
        
        return "boton_whatsapp_codigo.html"

    def _generate_conversion_article(self, hotel_data: Dict[str, Any], output_dir: Path,
                                      reason: str = None) -> str:
        """Genera artículo de conversión usando LLM (Pro AEO Plus / Elite)."""
        print("   Generando artículo de conversión con LLM...")
        
        try:
            result = self.content_gen.generate_conversion_article(hotel_data, reason=reason)
            
            # Write main article
            (output_dir / "articulo_reserva_directa.md").write_text(
                result["article_md"], encoding="utf-8"
            )
            print("   [OK] articulo_reserva_directa.md created")
            
            # Write metadata for SEO
            meta_content = f"""# Metadata para SEO
            
**Título**: {result["title"]}

**Meta Description**: {result["meta_description"]}

**Uso**: Copiar estos valores al CMS al publicar el artículo.
"""
            (output_dir / "articulo_seo_metadata.md").write_text(meta_content, encoding="utf-8")
            print("   [OK] articulo_seo_metadata.md created")
            
            return "articulo_reserva_directa.md"
            
        except Exception as e:
            print(f"   [WARN] Error generando artículo: {e}")
            return None

    def _generate_content(self, hotel_data: Dict[str, Any], reason: str = None) -> str:
        """Genera contenido basado en brechas de conversión."""
        delivery_dir = self.output_dir / "delivery_assets"
        delivery_dir.mkdir(exist_ok=True)
        return self._generate_conversion_article(hotel_data, delivery_dir, reason=reason)

    def _generate_certificates(self, hotel_data: Dict[str, Any], output_dir: Path) -> None:
        """Genera certificados para Elite PLUS (Reserva Directa + Web Optimizada)."""
        print("   Generando certificados Elite PLUS...")
        
        try:
            generated = self.certificate_gen.generate_all(hotel_data, output_dir)
            for filename in generated:
                print(f"   [OK] {filename} created")
        except Exception as e:
            print(f"   [WARN] Error generando certificados: {e}")

    def _generate_implementation_guide(self, output_dir: Path, hotel_data: Dict[str, Any] = None):
        """Generate comprehensive unified implementation guide (v2.6.3).
        
        This guide is SELF-CONTAINED and requires NO external documents.
        It integrates content from GUIA_OPERATIVA_FREELANCER and GUIA_OPERATIVA_GBP
        into a single sequential flow organized by implementation day.
        """
        hotel_name = hotel_data.get("nombre", "Hotel") if hotel_data else "Hotel"
        hotel_url = hotel_data.get("url", "https://sitio-del-hotel.com") if hotel_data else "https://sitio-del-hotel.com"
        package = getattr(self, 'current_package', 'unknown')
        package_lower = package.lower() if package else ""
        
        # Determine if GBP content should be included (Elite packages)
        include_gbp = "elite" in package_lower or "plus" in package_lower
        
        # Build the unified guide
        lines = self._build_guide_header(hotel_name, hotel_url, package, include_gbp)
        lines.extend(self._build_prerequisites_section(hotel_url))
        lines.extend(self._build_phase0_exploration(hotel_url))
        lines.extend(self._build_phase1_wpcode_installation())
        lines.extend(self._build_phase2_code_injection(hotel_name))
        lines.extend(self._build_phase3_immediate_verification(hotel_url))
        lines.extend(self._build_phase4_blog_article(hotel_name))
        lines.extend(self._build_phase5_faq_page(hotel_name))
        
        if include_gbp:
            lines.extend(self._build_phase6_gbp_optimization(hotel_name))
        
        lines.extend(self._build_phase7_impact_verification(hotel_url, include_gbp))
        lines.extend(self._build_troubleshooting_section())
        lines.extend(self._build_final_checklist(include_gbp))
        lines.extend(self._build_guide_footer(hotel_name))
        
        guide_content = "\n".join(lines)
        (output_dir / "GUIA_IMPLEMENTACION_COMPLETA.md").write_text(guide_content, encoding="utf-8")
        print("   [OK] GUIA_IMPLEMENTACION_COMPLETA.md created (unified guide v2.6.3)")

    def _build_guide_header(self, hotel_name: str, hotel_url: str, package: str, include_gbp: bool) -> List[str]:
        """Build the header section of the unified guide."""
        total_time = 345 if include_gbp else 180  # minutes
        total_phases = 7 if include_gbp else 5
        
        return [
            f"# Guía de Implementación Completa: {hotel_name}",
            "",
            f"> **Versión**: 2.6.3 (Guía Unificada)",
            f"> **Generado**: {self._get_timestamp()}",
            f"> **Paquete**: {package.upper()}",
            f"> **Tiempo total estimado**: ~{total_time} minutos (~{total_time // 60}h {total_time % 60}m)",
            f"> **Fases**: {total_phases} (Día 1 → Día 2-3 → Semana 2 → Verificación)",
            "",
            "> [!IMPORTANT]",
            "> **Esta guía es AUTO-CONTENIDA**. Sigue los pasos en orden secuencial.",
            "> No necesitas consultar documentos externos.",
            "",
            "---",
            "",
            "## 🚦 Reglas de Seguridad (Leer Primero)",
            "",
            "1. **No compartas credenciales** (ni por chat, ni capturas, ni documentos).",
            "2. Si no entiendes un paso, **detente** y consulta antes de improvisar.",
            "3. **Incógnito** se usa para validar el sitio público (evita caché).",
            "4. Tu \"botón de pánico\" es: **borrar el código pegado en WPCode y guardar**.",
            "",
            "---",
            "",
        ]

    def _build_prerequisites_section(self, hotel_url: str) -> List[str]:
        """Build the prerequisites section."""
        return [
            "## ⚠️ Pre-Requisitos (Verificar ANTES de Empezar)",
            "",
            "### A. Accesos Necesarios",
            "",
            "| Requisito | Descripción | ¿Lo tienes? |",
            "|-----------|-------------|-------------|",
            f"| Credenciales WP | Usuario/contraseña de `{hotel_url}/wp-admin` | ☐ |",
            "| Rol Administrador | Permiso para instalar plugins | ☐ |",
            "| Cuenta Google GBP | Acceso de propietario al perfil de Google Business | ☐ |",
            "| Navegador actualizado | Chrome, Firefox o Edge reciente | ☐ |",
            "| 1-2 horas libres | Sin interrupciones | ☐ |",
            "",
            "### B. Archivos de Esta Carpeta que Usarás",
            "",
            "| Archivo | Carpeta | Qué Hace |",
            "|---------|---------|----------|",
            "| `boton_whatsapp_codigo.html` | `02_PARA_EL_SITIO_WEB/` | Botón flotante WhatsApp |",
            "| `barra_reserva_movil.html` | `02_PARA_EL_SITIO_WEB/` | Barra fija en móviles |",
            "| `hotel-schema.json` | `03_PARA_TU_WEBMASTER/` | Datos estructurados Google |",
            "| `seo_fix_kit.md` | `03_PARA_TU_WEBMASTER/` | Mejoras técnicas SEO |",
            "| `articulo_reserva_directa.md` | `01_PARA_EL_DUEÑO_HOY/` | Artículo para blog |",
            "| `50_optimized_faqs.csv` | Raíz | FAQs para página web |",
            "",
            "> **Si algún requisito está pendiente, DETENTE y resuélvelo primero.**",
            "",
            "---",
            "",
        ]

    def _build_phase0_exploration(self, hotel_url: str) -> List[str]:
        """Build Phase 0: Exploration and baseline capture."""
        return [
            "## Fase 0: Exploración y Captura de Estado Base",
            "📅 **Cuándo**: Antes de tocar nada | ⏱️ **Tiempo**: 15 min",
            "",
            "> [!IMPORTANT]",
            "> **NO modifiques nada aún.** Esta fase es solo para reconocer el terreno.",
            "",
            "### Paso 0.1: Captura el Estado Actual (ANTES)",
            "",
            f"1. Abre `{hotel_url}` en tu navegador",
            "2. Toma **capturas de pantalla** de:",
            "   - Página de inicio (vista desktop)",
            "   - Página de inicio (vista móvil: F12 → ícono de móvil)",
            "   - Footer (parte inferior)",
            "3. Guarda en carpeta `evidencias_ANTES/`",
            "",
            "### Paso 0.2: Verificación Técnica Base",
            "",
            "| Verificar | URL | ¿Funciona? |",
            "|-----------|-----|------------|",
            f"| robots.txt | `{hotel_url}/robots.txt` | ☐ Sí / ☐ No (404) |",
            f"| sitemap.xml | `{hotel_url}/sitemap.xml` | ☐ Sí / ☐ No (404) |",
            f"| PageSpeed | pagespeed.web.dev → ingresar URL | Score: ___/100 |",
            "",
            "1. **Ctrl+U** (ver código fuente) → **Ctrl+F** → buscar \"canonical\"",
            "2. ¿Existe `<link rel=\"canonical\">`? ☐ Sí / ☐ No",
            "",
            "**Guarda estos datos en** `evidencias_ANTES/diagnostico_tecnico.txt`",
            "",
            "### Paso 0.3: Accede al Panel de WordPress",
            "",
            f"1. Abre: `{hotel_url}/wp-admin`",
            "2. Ingresa usuario y contraseña",
            "3. Deberías ver el **Escritorio de WordPress**",
            "",
            "| Elemento | Dónde Buscarlo | Para Qué |",
            "|----------|----------------|----------|",
            "| Plugins activos | Menú lateral → Plugins | Ver si WPCode existe |",
            "| Tema activo | Apariencia → Temas | Por si hay conflictos |",
            "",
            "---",
            "",
        ]

    def _build_phase1_wpcode_installation(self) -> List[str]:
        """Build Phase 1: WPCode installation."""
        return [
            "## Fase 1: Instalación de WPCode",
            "📅 **Cuándo**: Día 1 | ⏱️ **Tiempo**: 10 min",
            "",
            "### Paso 1.1: Verificar si WPCode ya Existe",
            "",
            "1. En el menú lateral izquierdo, busca: **\"WPCode\"**, **\"Code Snippets\"** o **\"Headers & Footers\"**",
            "2. **Si lo encuentras** → Salta al Paso 1.3",
            "3. **Si NO lo encuentras** → Continúa al Paso 1.2",
            "",
            "### Paso 1.2: Instalar WPCode",
            "",
            "1. Ve a **Plugins → Añadir nuevo**",
            "2. En el buscador escribe: **WPCode**",
            "3. Busca: **\"WPCode – Insert Headers and Footers\"** (Autor: WPCode)",
            "4. Haz clic en **Instalar ahora**",
            "5. Espera 5-10 segundos → Haz clic en **Activar**",
            "",
            "> [!WARNING]",
            "> **Si no puedes instalar plugins**, tu usuario no es Administrador.",
            "> DETENTE y solicita permisos al dueño del hotel.",
            "",
            "> [!NOTE]",
            "> Para instalación alternativa sin WPCode, consulta `02_PARA_EL_SITIO_WEB/guia_instalacion_wordpress.md`.",
            "",
            "### Paso 1.3: Prueba de Viabilidad (Cero Riesgo)",
            "",
            "Esta prueba confirma que WPCode **sí inyecta** en el HTML público.",
            "",
            "1. Ve a **Code Snippets → Headers & Footers**",
            "2. En la sección **Footer**, pega esto:",
            "",
            "```html",
            "<!-- IAH_TEST_WPCODE_OK -->",
            "```",
            "",
            "3. Haz clic en **Save Changes**",
            "4. Abre una ventana de **incógnito**",
            f"5. Ve al sitio del hotel",
            "6. Clic derecho → **Ver código fuente**",
            "7. **Ctrl+F** → buscar: `IAH_TEST_WPCODE_OK`",
            "",
            "**✅ Resultado esperado**: Debe aparecer el comentario.",
            "",
            "**❌ Si NO aparece**:",
            "1. Reintenta en incógnito + Ctrl+F5",
            "2. Si hay plugin de caché → busca \"Purge Cache\" y vuelve a probar",
            "3. Si persiste → DETENTE y escala al responsable",
            "",
            "**Limpieza**: Borra el comentario `IAH_TEST_WPCODE_OK` antes de continuar.",
            "",
            "---",
            "",
        ]


    def _build_phase2_code_injection(self, hotel_name: str) -> List[str]:
        """Build Phase 2: Code injection (WhatsApp, Booking Bar, Schema)."""
        return [
            "## Fase 2: Inyección de Código",
            "📅 **Cuándo**: Día 1 | ⏱️ **Tiempo**: 30 min",
            "",
            "### Paso 2.1: Inyectar Botón de WhatsApp (FOOTER)",
            "",
            "1. En tu computadora, abre:",
            "   `02_PARA_EL_SITIO_WEB/boton_whatsapp_codigo.html`",
            "2. Abre con un editor de texto (Notepad, VS Code)",
            "3. Selecciona TODO (**Ctrl+A**) y copia (**Ctrl+C**)",
            "4. En WordPress → **Code Snippets → Headers & Footers**",
            "5. En la sección **\"Footer\"**, pega el código (**Ctrl+V**)",
            "",
            "**Vista previa del código:**",
            "```html",
            f"<!-- IAH: Botón WhatsApp Flotante (sin IT) -->",
            f"<!-- Hotel: {hotel_name} -->",
            "<!-- Tracking: GA4 event 'whatsapp_click' -->",
            "<style>",
            "  #iah-whatsapp-cta { position: fixed; ...",
            "```",
            "",
            "> [!TIP]",
            "> Si necesitas personalización avanzada del botón, consulta `02_PARA_EL_SITIO_WEB/guia_boton_whatsapp.md`.",
            "",
            "### Paso 2.2: Inyectar Barra de Reserva Móvil (FOOTER)",
            "",
            "1. Abre: `02_PARA_EL_SITIO_WEB/barra_reserva_movil.html`",
            "2. Selecciona TODO y copia",
            "3. En WordPress → **Code Snippets → Headers & Footers**",
            "4. En **\"Footer\"**, posiciona el cursor **AL FINAL** del código anterior",
            "5. Presiona **Enter** dos veces (línea en blanco)",
            "6. Pega el nuevo código",
            "",
            "### Paso 2.3: Inyectar Schema.org (HEADER)",
            "",
            "1. Abre: `03_PARA_TU_WEBMASTER/hotel-schema.json`",
            "2. Selecciona TODO y copia",
            "3. En WordPress → **Code Snippets → Headers & Footers**",
            "4. En la sección **\"Header\"**, pega el código **ENVUELTO** así:",
            "",
            "```html",
            "<script type=\"application/ld+json\">",
            "AQUÍ PEGAS EL CONTENIDO DEL ARCHIVO hotel-schema.json",
            "</script>",
            "```",
            "",
            "> **No edites el JSON** si no es estrictamente necesario.",
            "",
            "### Paso 2.4: Guardar Todos los Cambios",
            "",
            "1. Revisa que tengas código en:",
            "   - **Header**: Schema.json envuelto en `<script>`",
            "   - **Footer**: Botón WhatsApp + Barra de Reserva",
            "2. Haz clic en **Save Changes**",
            "3. Espera confirmación: \"Settings Saved\"",
            "",
            "### Paso 2.5: Delegación al Webmaster (Opcional)",
            "",
            "Si no tienes acceso o el sitio no es WordPress, usa:",
            "- `03_PARA_TU_WEBMASTER/email_para_webmaster.txt`: Copia este texto y envíalo con los archivos adjuntos.",
            "- `03_PARA_TU_WEBMASTER/seo_fix_kit.md`: Lista de tareas técnicas para que el webmaster optimice el SEO base.",
            "",
            "---",
            "",
        ]

    def _build_phase3_immediate_verification(self, hotel_url: str) -> List[str]:
        """Build Phase 3: Immediate verification."""
        return [
            "## Fase 3: Verificación Inmediata",
            "📅 **Cuándo**: Día 1, inmediatamente después | ⏱️ **Tiempo**: 15 min",
            "",
            "### Paso 3.1: Verificar en Desktop",
            "",
            "1. Abre una **ventana de incógnito** (Ctrl+Shift+N)",
            f"2. Ve a: `{hotel_url}`",
            "3. **Busca el botón de WhatsApp**:",
            "   - Debe aparecer en la esquina inferior derecha",
            "   - Es un círculo verde con el ícono de WhatsApp",
            "4. Haz clic → Debe abrir wa.me con un mensaje predefinido",
            "",
            "**¿No aparece?** → Salta a la sección **Troubleshooting**.",
            "",
            "### Paso 3.2: Verificar en Móvil",
            "",
            "1. En Chrome, presiona **F12** (DevTools)",
            "2. Haz clic en el ícono de **dispositivo móvil** (o Ctrl+Shift+M)",
            "3. Selecciona \"iPhone 12\" o \"Pixel 5\"",
            "4. Recarga la página (F5)",
            "5. **Busca la barra de reservas**:",
            "   - Debe aparecer fija en la parte inferior",
            "   - Dice \"📅 Mejor Tarifa Garantizada\" y \"Reservar Ahora\"",
            "6. El botón WhatsApp debe estar un poco más arriba que la barra",
            "",
            "### Paso 3.3: Verificar Schema con Rich Results Test",
            "",
            "1. Abre: https://search.google.com/test/rich-results",
            f"2. Pega la URL: `{hotel_url}`",
            "3. Haz clic en **Probar URL**",
            "4. Espera 30-60 segundos",
            "",
            "**✅ Resultado esperado**: Detecta \"Hotel\" o datos estructurados.",
            "",
            "**❌ Si no detecta nada**:",
            "1. Ctrl+U → Ctrl+F → buscar `application/ld+json`",
            "2. Si no aparece → el código no se guardó en Header",
            "3. Vuelve a WPCode y verifica",
            "",
            "---",
            "",
        ]

    def _build_phase4_blog_article(self, hotel_name: str) -> List[str]:
        """Build Phase 4: Blog article publication."""
        return [
            "## Fase 4: Publicar Artículo de Blog",
            "📅 **Cuándo**: Día 2 | ⏱️ **Tiempo**: 20 min",
            "",
            "### Paso 4.1: Crear Nuevo Post",
            "",
            "1. En WordPress, ve a **Entradas → Añadir nueva**",
            "2. Si te pregunta por el editor, elige **\"Editor clásico\"** o continúa con Gutenberg",
            "",
            "### Paso 4.2: Copiar el Contenido",
            "",
            "1. Abre: `01_PARA_EL_DUEÑO_HOY/articulo_reserva_directa.md`",
            "2. Copia TODO el contenido",
            "",
            "> [!TIP]",
            "> Los metadatos SEO adecuados (Title/Description) están en `articulo_seo_metadata.md`.",
            "",
            "### Paso 4.3: Pegar y Formatear",
            "",
            "**Si usas Editor Clásico**:",
            "1. Pega el contenido en el área de edición",
            "2. El formato Markdown puede convertirse automáticamente",
            "3. Si no se convierte: ajusta manualmente títulos y negritas",
            "",
            "**Si usas Gutenberg (editor de bloques)**:",
            "1. Haz clic en el área de edición",
            "2. Pega el contenido",
            "3. WordPress convertirá cada párrafo en un bloque",
            "",
            "### Paso 4.4: Configurar el Post",
            "",
            "| Campo | Valor |",
            "|-------|-------|",
            f"| **Título** | Por qué reservar directamente en {hotel_name} es tu mejor decisión |",
            "| **Categoría** | Crea: \"Reserva Directa\" o \"Tips de Viaje\" |",
            "| **Imagen destacada** | Foto del hotel (opcional) |",
            f"| **Slug/URL** | `reservar-directo-{hotel_name.lower().replace(' ', '-')}` |",
            "",
            "### Paso 4.5: Redes Sociales",
            "",
            "Una vez publicado, usa el contenido de `01_PARA_EL_DUEÑO_HOY/post_facebook_semana1.txt` para anunciarlo en tus redes sociales.",
            "",
            "### Paso 4.6: Publicar",
            "",
            "1. Haz clic en **Publicar** → Confirma",
            "2. Copia la URL del artículo publicado",
            "",
            "**✅ Verificación**: El artículo es accesible públicamente.",
            "",
            "---",
            "",
        ]

    def _build_phase5_faq_page(self, hotel_name: str) -> List[str]:
        """Build Phase 5: FAQ page publication."""
        return [
            "## Fase 5: Publicar Página de Preguntas Frecuentes",
            "📅 **Cuándo**: Día 2-3 | ⏱️ **Tiempo**: 45 min",
            "",
            "### Paso 5.1: Crear Nueva Página",
            "",
            "1. En WordPress, ve a **Páginas → Añadir nueva**",
            f"2. Título: **Preguntas Frecuentes sobre {hotel_name}**",
            "3. Plantilla: \"Por defecto\" o \"Página completa\"",
            "",
            "### Paso 5.2: Copiar Contenido desde CSV",
            "",
            "1. Abre: `50_optimized_faqs.csv`",
            "2. El archivo tiene dos columnas: **Pregunta** y **Respuesta**",
            "3. Para cada fila:",
            "   - Copia la **Pregunta** → pégala como **H3** o negrita",
            "   - Copia la **Respuesta** → pégala como párrafo",
            "",
            "**Ejemplo de formato:**",
            "```",
            f"### ¿{hotel_name} permite mascotas?",
            "Sí, somos pet-friendly. Te recomendamos informarnos con anticipación...",
            "",
            "### ¿A qué hora es el check-in?",
            "El check-in es a partir de las 3:00 PM...",
            "```",
            "",
            "> [!TIP]",
            "> Si tu tema tiene bloque \"Acordeón\" o \"FAQ\", úsalo para mejor UX.",
            "",
            "### Paso 5.3: Configurar URL y Publicar",
            "",
            "1. En **Enlace permanente** (Slug), escribe: `preguntas-frecuentes`",
            "2. Haz clic en **Publicar**",
            f"3. Verifica que sea accesible en: `[URL del hotel]/preguntas-frecuentes`",
            "",
            "### Paso 5.4: Agregar al Menú (Opcional)",
            "",
            "1. Ve a **Apariencia → Menús**",
            "2. Selecciona el menú principal",
            "3. En **Páginas**, marca \"Preguntas Frecuentes\"",
            "4. Haz clic en **Añadir al menú** → **Guardar menú**",
            "",
            "**✅ Verificación**:",
            "- [ ] Página `/preguntas-frecuentes` publicada",
            "- [ ] Al menos 20 FAQs visibles",
            "- [ ] Enlace en menú o footer",
            "",
            "---",
            "",
        ]

    def _build_phase6_gbp_optimization(self, hotel_name: str) -> List[str]:
        """Build Phase 6: GBP Optimization (Elite packages only)."""
        return [
            "## Fase 6: Optimización de Google Business Profile",
            "📅 **Cuándo**: Semana 2 | ⏱️ **Tiempo**: 2-3 horas (distribuidas)",
            "",
            "> [!IMPORTANT]",
            "> Esta fase se ejecuta en Google Business Profile, NO en WordPress.",
            "> Los cambios pueden tardar **24-72 horas** en reflejarse públicamente.",
            "",
            "### 6.1: Acceder a Google Business Profile",
            "",
            "1. Abre: https://business.google.com/",
            "2. Inicia sesión con la cuenta Google del hotel",
            f"3. Selecciona \"{hotel_name}\"",
            "4. Verifica que puedas ver el botón \"Editar perfil\"",
            "",
            "> **Si no puedes editar**, solicita al propietario que te agregue como administrador.",
            "",
            "### 6.2: Subir Fotos (10 Mínimo)",
            "",
            "1. En el menú lateral, haz clic en **\"Fotos\"**",
            "2. Haz clic en **\"Agregar fotos\"**",
            "3. Sube las fotos según categorías en `fotos_shotlist.md`:",
            "",
            "| Categoría | Cantidad | Ejemplos |",
            "|-----------|----------|----------|",
            "| Exterior | 2 | Fachada, entrada |",
            "| Habitaciones | 3 | Diferentes tipos |",
            "| Áreas comunes | 2 | Lobby, piscina |",
            "| Gastronomía | 3 | Restaurante, desayuno |",
            "",
            "> [!TIP]",
            "> Consulta `fotos_brief.md` y `fotos_checklist.md` para asegurar la calidad de las tomas antes de subirlas.",
            "",
            "### 6.3: Publicar Posts (4/mes)",
            "",
            "Usa las plantillas en `post_plantilla_1.txt` a `post_plantilla_4.txt`",
            "y el contenido expandido en `04_GUIA_MOTOR_RESERVAS/geo_playbook.md`.",
            "",
            "1. En el menú lateral, haz clic en **\"Agregar actualización\"**",
            "2. Selecciona tipo: \"Agregar actualización\" o \"Agregar oferta\"",
            "3. Completa:",
            "   - **Texto**: Copia de `geo_playbook.md` (sección Posts)",
            "   - **Foto**: Adjunta una foto relevante",
            "   - **Botón CTA**: \"Reservar\" con enlace al sitio",
            "4. Haz clic en **Publicar**",
            "",
            "**Calendario:**",
            "| Semana | Post | Fecha |",
            "|--------|------|-------|",
            "| 1 | Escapada/Oferta | Lunes próximo |",
            "| 2 | Amenidad destacada | +7 días |",
            "| 3 | Testimonio | +14 días |",
            "| 4 | Evento/Temporada | +21 días |",
            "",
            "### 6.4: Preguntas Frecuentes (FAQs)",
            "",
            "> [!CAUTION]",
            "> **GBP Q&A DESHABILITADO (Enero 2026)**: Google eliminó la función de Preguntas y Respuestas para hoteles.",
            "> Las 5 preguntas semilla de `geo_playbook.md` deben publicarse en la página web `/preguntas-frecuentes`.",
            "> Ver informe técnico completo en `docs/Q&A_DEPRECATION_REPORT.md`.",
            "",
            "Las 5 preguntas semilla están en `geo_playbook.md`. **Publicarlas en la WEB, no en GBP.**",
            "",
            "1. En WordPress, ve a **Páginas → Preguntas Frecuentes**",
            "2. Agrega las 5 preguntas de `geo_playbook.md` al final de la página",
            "3. Guarda y verifica que sean visibles",
            "",
            "### 6.5: Directorios Locales",
            "",
            "Sincronizar información NAP (Nombre, Dirección, Teléfono) consistente en perfiles externos como TripAdvisor y Bing Places.",
            "",
            "### 6.6: Activar Mensajería",
            "",
            "1. En Business Profile Manager → **Mensajes**",
            "2. Haz clic en **\"Activar mensajes\"**",
            "3. Configura respuesta automática:",
            f"   > ¡Hola! Gracias por contactar a {hotel_name}. Te responderemos en menos de 10 minutos.",
            "",
            "### 6.7: Implementar Plan de Reseñas",
            "",
            "Sigue el plan en `04_GUIA_MOTOR_RESERVAS/review_plan.md`:",
            "",
            "1. **Check-in**: Recolecta WhatsApp del huésped",
            "2. **2h después del checkout**: Envía mensaje con enlace a reseña",
            "3. **Meta**: 20 reseñas nuevas en 30 días",
            "",
            "**Script sugerido (WhatsApp):**",
            "```",
            "Hola {nombre}, gracias por elegirnos.",
            "¿Podrías contarnos tu experiencia aquí?",
            "👉 [Enlace a reseña de Google]",
            "```",
            "",
            "**✅ Verificación Fase 6:**",
            "- [ ] 10+ fotos subidas",
            "- [ ] 4 posts publicados",
            "- [x] ~~5 Q&A publicados~~ → BLOQUEADO: Publicados como FAQs en web",
            "- [ ] Mensajería activada",
            "- [ ] Plan de reseñas en ejecución",
            "",
            "---",
            "",
        ]

    def _build_phase7_impact_verification(self, hotel_url: str, include_gbp: bool) -> List[str]:
        """Build Phase 7: Impact verification (Day 7, 14, 30)."""
        lines = [
            "## Fase 7: Verificación de Impacto",
            "📅 **Cuándo**: Día 7, 14, 30 | ⏱️ **Tiempo**: 30 min por verificación",
            "",
            "### Día 7: Verificación Técnica",
            "",
            "- [ ] Rich Results Test sigue mostrando \"Hotel\" ✓",
            "- [ ] Botón WhatsApp funcional (hacer prueba real)",
            "- [ ] PageSpeed Score: ___/100 (comparar con baseline)",
            "- [ ] Primer clic en WhatsApp registrado (si hay GA4)",
            "",
            "> [!NOTE]",
            "> Puedes monitorear la visibilidad en IA detallada en `dashboard_visibilidad_ia.md`.",
            "",
            "**Evidencia**: Captura de Rich Results + Screenshot de WhatsApp.",
            "",
            "### Día 14: Verificación de Actividad",
            "",
            "- [ ] Clics en WhatsApp (GA4 o tracking manual): ___",
            "- [ ] Mensajes recibidos (preguntar al hotel): ___",
            "- [ ] Artículo indexado en Google:",
            f"   - Buscar: `site:{hotel_url.replace('https://', '').replace('http://', '')} reservar`",
            "   - ¿Aparece? ☐ Sí / ☐ No",
        ]
        
        if include_gbp:
            lines.extend([
                "- [ ] Posts GBP publicados esta semana: ___",
                "- [ ] Nuevas reseñas: ___",
                "- [ ] Mensajes GBP recibidos: ___",
            ])
        
        lines.extend([
            "",
            "### Día 30: Reporte de Impacto Final",
            "",
            "Genera tabla comparativa para el cliente:",
            "",
            "| Métrica | Día 0 | Día 30 | Cambio |",
            "|---------|-------|--------|--------|",
            "| PageSpeed Score | ___ | ___ | +/- ___ |",
            "| Schema detectado | ☐ No | ☑ Sí | ✓ |",
            "| Clics WhatsApp | 0 | ___ | +___ |",
            "| Artículo indexado | ☐ No | ☐ Sí | |",
        ])
        
        if include_gbp:
            lines.extend([
                "| Visualizaciones GBP | ___ | ___ | +___% |",
                "| Clics web desde GBP | ___ | ___ | +___% |",
                "| Reseñas nuevas | ___ | ___ | +___ |",
            ])
        
        lines.extend([
            "",
            "**Enviar al hotel:**",
            "1. Reporte completo (tabla arriba)",
            "2. Capturas comparativas ANTES/DESPUÉS",
            "3. Próximos pasos recomendados",
            "",
            "> Al terminar, verifica el cumplimiento de la promesa en `proposal_delivery_checklist.md`.",
            "",
            "---",
            "",
        ])
        
        return lines

    def _build_troubleshooting_section(self) -> List[str]:
        """Build the troubleshooting section."""
        return [
            "## 🔧 Troubleshooting (Si Algo Sale Mal)",
            "",
            "### 🔴 No puedo instalar plugins",
            "",
            "**Síntoma**: \"No tienes permisos suficientes\"",
            "",
            "**Solución**:",
            "1. Contacta al dueño del hotel",
            "2. Pídele que vaya a **Usuarios → Todos los usuarios**",
            "3. Que edite tu usuario → Cambie rol a **Administrador**",
            "",
            "---",
            "",
            "### 🔴 El botón de WhatsApp no aparece",
            "",
            "**Diagnóstico**:",
            "1. ¿Abriste en incógnito? (evita caché)",
            "2. F12 → Consola → ¿Hay errores en rojo?",
            "",
            "**Soluciones**:",
            "| Causa | Solución |",
            "|-------|----------|",
            "| Código no guardado | Vuelve a WPCode, verifica Footer |",
            "| Caché de WP | Busca \"Purge Cache\" en plugin de caché |",
            "| Conflicto CSS | Revisa errores en Consola |",
            "",
            "---",
            "",
            "### 🔴 La barra de reservas no aparece en móvil",
            "",
            "1. ¿Estás en vista móvil de DevTools?",
            "2. Inspecciona `#iah-booking-bar`",
            "3. ¿Tiene `display: none` o `display: flex`?",
            "",
            "**Si tiene `display: none`**: El código no detectó que es móvil. Revisa sintaxis.",
            "",
            "---",
            "",
            "### 🔴 Rich Results Test no detecta el Hotel",
            "",
            "1. Ctrl+U → Ctrl+F → buscar `application/ld+json`",
            "2. ¿Aparece? → Si no, el código no está en Header",
            "3. ¿Aparece pero con errores? → https://jsonlint.com/ para validar",
            "",
            "---",
            "",
            "### 🔴 El sitio se ve raro después de guardar (ROLLBACK)",
            "",
            "**Acción inmediata:**",
            "1. Ve a **Code Snippets → Headers & Footers**",
            "2. **Borra TODO** el código de Header y Footer",
            "3. Haz clic en **Save Changes**",
            "4. Recarga el sitio — debe volver a la normalidad",
            "",
            "> Si después del rollback sigue con problemas, **DETENTE** y contacta al responsable.",
            "",
            "---",
            "",
        ]

    def _build_final_checklist(self, include_gbp: bool) -> List[str]:
        """Build the final implementation checklist."""
        lines = [
            "## ☑️ Checklist Final de Implementación",
            "",
            "```",
            "PRE-REQUISITOS",
            "☐ Credenciales WP verificadas",
            "☐ Capturas ANTES guardadas",
            "☐ Diagnóstico técnico base documentado",
            "",
            "FASE 1-2: INSTALACIÓN WEB",
            "☐ WPCode instalado y activado",
            "☐ Botón WhatsApp en Footer",
            "☐ Barra de Reservas en Footer",
            "☐ Schema.org en Header (con tags <script>)",
            "☐ Cambios guardados",
            "",
            "FASE 3: VERIFICACIÓN INMEDIATA",
            "☐ Botón WA visible en desktop (incógnito)",
            "☐ Barra visible en móvil (DevTools)",
            "☐ Rich Results Test detecta \"Hotel\"",
            "",
            "FASE 4-5: CONTENIDO",
            "☐ Artículo publicado (no borrador)",
            "☐ Página FAQs con 20+ preguntas",
            "☐ URLs copiadas para reporte",
        ]
        
        if include_gbp:
            lines.extend([
                "",
                "FASE 6: GOOGLE BUSINESS PROFILE",
                "☐ 10+ fotos subidas",
                "☐ 4 posts publicados (o programados)",
                "☑ 5 Q&A → BLOQUEADO: Publicados como FAQs en web",
                "☐ Mensajería activada",
                "☐ Plan de reseñas en ejecución",
            ])
        
        lines.extend([
            "",
            "VERIFICACIÓN DE IMPACTO",
            "☐ Día 7: Verificación técnica",
            "☐ Día 14: Verificación de actividad",
            "☐ Día 30: Reporte enviado al hotel",
            "",
            "EVIDENCIAS",
            "☐ Capturas DESPUÉS guardadas",
            "☐ Reporte de entrega enviado",
            "```",
            "",
            "---",
            "",
        ])
        
        return lines

    def _build_guide_footer(self, hotel_name: str) -> List[str]:
        """Build the guide footer."""
        return [
            "## 📞 Contacto de Soporte",
            "",
            "Si encuentras un problema no cubierto en esta guía:",
            "",
            "1. **Documenta**: Toma captura del error",
            "2. **No improvises**: No intentes soluciones no documentadas",
            "3. **Escala**: Contacta al responsable con:",
            "   - Descripción del problema",
            "   - Fase donde ocurrió",
            "   - Captura del error",
            "",
            "---",
            "",
            f"*Guía generada automáticamente por IA Hoteles Agent v2.6.3 para {hotel_name}*",
            "*\"Primera Recomendación en Agentes IA\"*",
        ]
    
    def _get_timestamp(self) -> str:
        """Return current timestamp string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M")

    def _generate_geo_assets(self, hotel_data: Dict[str, Any], output_dir: Path):
        print("   Generating GEO activation assets...")
        geo_assets = self.geo_gen.generate(hotel_data)
        (output_dir / "geo_playbook.md").write_text(geo_assets["geo_playbook"], encoding="utf-8")
        # v3.3.1: directory_submission_list.csv removed (Obsolete)
        (output_dir / "review_plan.md").write_text(geo_assets["review_playbook"], encoding="utf-8")
        
        # New in v2.10.2: GBP Data Integrity Audit
        gbp_audit = self.geo_gen.generate_gbp_audit_checklist(hotel_data)
        (output_dir / "gbp_data_integrity.md").write_text(gbp_audit, encoding="utf-8")
        
        print("   [OK] geo_playbook.md, review_plan.md, gbp_data_integrity.md created")

    def _generate_validation_checklist(self, delivery_dir: Path, package: str, include_geo: bool, include_pro: bool, include_piloto: bool = False) -> None:
        proposal_path = self._locate_proposal(delivery_dir.parent)
        checklist_items = []

        package_lower = (package or "").lower()
        include_plus_assets = "plus" in package_lower or "elite" in package_lower
        
        if include_piloto:
            checklist_items.extend([
                ("Schema básico instalado", delivery_dir / "hotel-schema-basic.json"),
                ("10 FAQs para piloto", delivery_dir / "10_faqs_piloto.csv"),
                ("Playbook GEO reducido", delivery_dir / "geo_playbook_basic.md"),
                ("Template tracking semanal", delivery_dir / "weekly_tracking_template.md"),
            ])
        elif include_pro:
            checklist_items.extend([
                ("Schema.org instalado", self._resolve_in_roles(delivery_dir, "hotel-schema.json")),
                ("FAQs IA publicadas", self._resolve_in_roles(delivery_dir, "50_optimized_faqs.csv")),
                ("Kit de fixes SEO", self._resolve_in_roles(delivery_dir, "seo_fix_kit.md")),
                ("Dashboard IA mínimo", self._resolve_in_roles(delivery_dir, "dashboard_visibilidad_ia.md")),
            ])

            if include_plus_assets:
                checklist_items.extend([
                    ("Botón WhatsApp (1 clic) instalado", self._resolve_in_roles(delivery_dir, "boton_whatsapp_codigo.html")),
                    ("Guía botón WhatsApp", self._resolve_in_roles(delivery_dir, "guia_boton_whatsapp.md")),
                    ("Barra de reserva móvil", self._resolve_in_roles(delivery_dir, "barra_reserva_movil.html")),
                    ("Guía CMS", self._resolve_in_roles(delivery_dir, "guia_instalacion_wordpress.md")),
                    ("Post Semana 1", self._resolve_in_roles(delivery_dir, "post_facebook_semana1.txt")),
                    ("Posts (4 plantillas)", self._resolve_in_roles(delivery_dir, "post_plantilla_1.txt")),
                    ("Brief/shotlist fotos", self._resolve_in_roles(delivery_dir, "fotos_brief.md")),
                ])
        
        if include_geo:
            checklist_items.extend([
                ("Playbook GEO y Q&A", self._resolve_in_roles(delivery_dir, "geo_playbook.md")),
                # v3.3.1: removed directory_submission_list.csv
                ("Plan de reseñas", self._resolve_in_roles(delivery_dir, "review_plan.md")),
                ("Auditoría integridad GBP", self._resolve_in_roles(delivery_dir, "gbp_data_integrity.md")),
            ])

        lines = ["# Checklist de Validación", f"Paquete ejecutado: {package}"]
        if proposal_path:
            try:
                rel = proposal_path.relative_to(self.output_dir)
            except ValueError:
                rel = proposal_path
            lines.append(f"Propuesta comercial evaluada: `{rel}`")
        else:
            lines.append("[WARN] No se encontró `02_propuesta_comercial.md` en el directorio base")

        lines.append("\n| Elemento Prometido | Archivo Entregado | Estado |")
        lines.append("|--------------------|-------------------|--------|")
        for label, path in checklist_items:
            state = "[x]" if path.exists() else "[ ]"
            rel_path = path.relative_to(self.output_dir) if path.exists() else path.name
            lines.append(f"| {label} | {rel_path} | {state} |")

        (delivery_dir / "proposal_delivery_checklist.md").write_text("\n".join(lines), encoding="utf-8")
        print("   [OK] proposal_delivery_checklist.md created")

    def _locate_proposal(self, base_dir: Path) -> Path | None:
        candidates = list(base_dir.rglob("02_propuesta_comercial.md"))
        if not candidates:
            return None
        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return candidates[0]

    def _resolve_in_roles(self, delivery_dir: Path, filename: str) -> Path:
        """Busca un archivo dentro de las carpetas por rol; cae en raíz si no existe."""
        direct = delivery_dir / filename
        if direct.exists():
            return direct
        for folder in delivery_dir.iterdir():
            if folder.is_dir():
                candidate = folder / filename
                if candidate.exists():
                    return candidate
        return direct

    # ═══════════════════════════════════════════════════════════════════
    # v2.5: Nuevos métodos para "Sin IT" Profundo
    # ═══════════════════════════════════════════════════════════════════

    def _generate_booking_bar(self, hotel_data: Dict[str, Any], output_dir: Path = None,
                               reason: str = None) -> str | None:
        """Genera barra de reserva móvil sticky (si hay motor detectado)."""
        if output_dir is None:
            output_dir = self.output_dir / "delivery_assets"
            output_dir.mkdir(exist_ok=True)
        
        print("   Generando barra de reserva móvil...")
        
        result = self.booking_bar_gen.generate(hotel_data)
        if result is None:
            print("   [SKIP] No se detectó motor de reservas para barra")
            return None
        
        filepath = output_dir / "barra_reserva_movil.html"
        filepath.write_text(result["html_code"], encoding="utf-8")
        print(f"   [OK] barra_reserva_movil.html created (Motor: {result['engine_detected']['name']})")
        
        return "barra_reserva_movil.html"

    def _generate_deploy_instructions(self, hotel_data: Dict[str, Any], output_dir: Path, 
                                       assets_generated: List[str]) -> Dict[str, str]:
        """Genera guías de instalación específicas para el CMS detectado."""
        print("   Generando instrucciones de despliegue...")
        
        result = self.deploy_instructions_gen.generate(hotel_data, assets_generated)
        cms_type = result["cms_type"]
        
        # Write CMS-specific guide
        guide_filename = f"guia_instalacion_{cms_type}.md"
        (output_dir / guide_filename).write_text(result["cms_guide"], encoding="utf-8")
        print(f"   [OK] {guide_filename} created")
        
        # Write delegation email
        (output_dir / "email_para_webmaster.txt").write_text(result["delegation_email"], encoding="utf-8")
        print("   [OK] email_para_webmaster.txt created")
        
        return result

    def _generate_manifest(self, hotel_data: Dict[str, Any], output_dir: Path, 
                           assets_generated: List[str], package: str, 
                           review_status: Dict[str, Any] = None,
                           recommended_package: Optional[str] = None) -> None:
        """Genera manifest.json con trazabilidad del kit y estado de revisión."""
        print("   Generando manifest.json...")
        
        cms_info = hotel_data.get("cms_detected", {})
        cms_type = cms_info.get("cms", "unknown") if isinstance(cms_info, dict) else "unknown"
        
        # Detect booking engine from data
        booking_engine = "none"
        if hotel_data.get("booking_engine_url") or hotel_data.get("motor_reservas_url"):
            booking_engine = "detected"
        
        manifest = {
            "version": "3.1.0",
            "generated_at": datetime.now().isoformat(),
            "cli_version": "3.1.0",
            "package": package,
            "recommended_package": recommended_package,
            "package_coherence": recommended_package is None or package.lower() == recommended_package.lower() or package.lower().replace(" ", "_") == recommended_package.lower().replace(" ", "_"),
            "target_url": hotel_data.get("url", ""),
            "hotel_name": hotel_data.get("nombre", "Hotel"),
            "cms_detected": cms_type,
            "cms_confidence": cms_info.get("confidence", "low") if isinstance(cms_info, dict) else "low",
            "booking_engine": booking_engine,
            "automated_review": {
                "status": "completed" if review_status and review_status.get("status") != "error" else "failed/missing",
                "high_severity_issues": review_status.get("severity_counts", {}).get("HIGH", 0) if review_status else 0,
                "summary": review_status.get("summary", "No review data available") if review_status else "No review performed"
            },
            "files_generated": self._build_manifest_files(output_dir, assets_generated)
        }
        
        (output_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), 
            encoding="utf-8"
        )
        print("   [OK] manifest.json created")

    def _organize_by_roles(self, delivery_dir: Path) -> None:
        """Organiza archivos existentes en subcarpetas por roles (v2.5)."""
        print("   Organizando carpetas por roles...")
        
        # Define role mappings
        role_folders = {
            "01_PARA_EL_DUEÑO_HOY": [
                "articulo_reserva_directa.md",
                "post_facebook_semana1.txt",
            ],
            "02_PARA_EL_SITIO_WEB": [
                "barra_reserva_movil.html",
                "boton_whatsapp_codigo.html",
                "guia_instalacion_wordpress.md",
                "guia_instalacion_wix.md",
                "guia_instalacion_squarespace.md",
                "guia_instalacion_unknown.md",
                "guia_boton_whatsapp.md",
            ],
            "03_PARA_TU_WEBMASTER": [
                "email_para_webmaster.txt",
                "hotel-schema.json",
                "seo_fix_kit.md",
            ],
            "04_GUIA_MOTOR_RESERVAS": [
                "geo_playbook.md",
                "review_plan.md",
                "gbp_data_integrity.md",
            ],
        }
        
        # Create folders and move files
        moved_count = 0
        for folder_name, files in role_folders.items():
            folder_path = delivery_dir / folder_name
            for filename in files:
                src = delivery_dir / filename
                if src.exists():
                    folder_path.mkdir(exist_ok=True)
                    dest = folder_path / filename
                    src.rename(dest)
                    moved_count += 1
        
        if moved_count > 0:
            print(f"   [OK] Organizados {moved_count} archivos en carpetas por roles")
        else:
            print("   [INFO] No hay archivos para organizar aún")

    def _build_manifest_files(self, delivery_dir: Path, assets_generated: List[str]) -> List[Dict[str, Any]]:
        """Construye lista de archivos con rutas finales (post-organización)."""
        if not assets_generated:
            discovered: List[Path] = [
                p
                for p in delivery_dir.rglob("*")
                if p.is_file() and p.name != "manifest.json"
            ]
            discovered.sort(key=lambda p: str(p.relative_to(delivery_dir)).lower())
            return [
                {"path": p.relative_to(delivery_dir).as_posix(), "exists": True}
                for p in discovered
            ]

        files: List[Dict[str, Any]] = []
        for asset in assets_generated:
            path = delivery_dir / asset
            if not path.exists():
                for folder in delivery_dir.iterdir():
                    if folder.is_dir():
                        candidate = folder / asset
                        if candidate.exists():
                            path = candidate
                            break
            files.append({"path": path.relative_to(delivery_dir).as_posix(), "exists": path.exists()})
        return files

    def _generate_posts_placeholders(self, output_dir: Path) -> None:
        """Crea plantillas de posts (4) y un post rápido semana 1."""
        posts = {
            "post_facebook_semana1.txt": "Post Semana 1 - Gancho rápido para reservas directas.\nCTA: Reserva directo en el sitio.\n",
            "post_plantilla_1.txt": "Post 1 - Oferta escapada. CTA: Reserva directa.",
            "post_plantilla_2.txt": "Post 2 - Amenidad destacada. CTA: Escribe por WhatsApp.",
            "post_plantilla_3.txt": "Post 3 - Testimonio / review. CTA: Reserva ahora.",
            "post_plantilla_4.txt": "Post 4 - Evento/temporada. CTA: Reserva con tarifa directa.",
        }
        for name, content in posts.items():
            (output_dir / name).write_text(content, encoding="utf-8")
        print("   [OK] Plantillas de posts creadas (4 + semana1)")

    def _generate_photos_brief(self, output_dir: Path) -> None:
        """Crea brief/shotlist/checklist para 10 fotos (capacidad, no fotos reales)."""
        brief = """# Brief de Fotos (10 tomas)

## Objetivo
Incrementar conversión en web/GBP con 10 fotos nuevas alineadas a CTA de reserva directa.

## Guidelines
- Formato: 4:5 y 1:1, luz natural, sin filtros pesados.
- Mostrar: fachada, lobby, habitación estrella, baño, desayuno, vista, amenidad clave, staff.
"""
        shotlist = """# Shotlist (10)
1) Fachada día
2) Lobby / recepción
3) Habitación tipo A (wide + detalle)
4) Baño habitación tipo A
5) Desayuno / F&B
6) Vista destacada
7) Amenidad clave (spa/piscina/...)
8) Staff en servicio
9) Área común (cowork/terraza)
10) Detalle de marca (amenities / welcome)
"""
        checklist = """# Checklist de entrega
- Resolución mínima 2000px lado mayor
- Formato JPG/WEBP optimizado
- Nombres con palabras clave (hotel-ciudad-tipo-n).jpg
- Variantes verticales para GBP/IG
"""
        (output_dir / "fotos_brief.md").write_text(brief, encoding="utf-8")
        (output_dir / "fotos_shotlist.md").write_text(shotlist, encoding="utf-8")
        (output_dir / "fotos_checklist.md").write_text(checklist, encoding="utf-8")
        print("   [OK] Brief/shotlist/checklist de fotos creados")
