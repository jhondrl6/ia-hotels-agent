from datetime import datetime, timedelta
from typing import List, Optional

from modules.utils.benchmarks import BenchmarkLoader


class ProposalGenerator:
    def __init__(self):
        pass

    def _normalize_markdown(self, content: str) -> str:
        if not content:
            return ""
        lines = []
        for raw in content.splitlines():
            keep_two_spaces = raw.endswith("  ")
            line = raw.rstrip()
            if keep_two_spaces and not line.endswith("  "):
                line = line + "  "
            lines.append(line)
        out = []
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
                out.append(line)
                previous_blank = False
            else:
                if not previous_blank:
                    out.append("")
                previous_blank = True
        normalized = "\n".join(out).strip()
        return normalized + "\n" if normalized else ""

    def _format_date_es(self, dt: datetime) -> str:
        months = {
            1: "enero",
            2: "febrero",
            3: "marzo",
            4: "abril",
            5: "mayo",
            6: "junio",
            7: "julio",
            8: "agosto",
            9: "septiembre",
            10: "octubre",
            11: "noviembre",
            12: "diciembre",
        }
        return f"{dt.day:02d} de {months.get(dt.month, str(dt.month))} de {dt.year}"

    def _apply_addon_to_proyeccion(self, proyeccion: list, addon_precio: int) -> list:
        if not addon_precio or not proyeccion:
            return proyeccion

        updated = []
        acumulado = 0
        for row in proyeccion:
            if not isinstance(row, dict):
                updated.append(row)
                continue
            inversion = int(row.get("inversion", 0) or 0) + int(addon_precio)
            ingreso = int(row.get("ingreso_recuperado", 0) or 0)
            beneficio = ingreso - inversion
            acumulado += beneficio
            new_row = dict(row)
            new_row["inversion"] = inversion
            new_row["beneficio_neto"] = beneficio
            new_row["acumulado"] = acumulado
            updated.append(new_row)

        return updated

    def create_pdf(self, hotel_data, claude_analysis, roi_data, output_dir, seo_data=None):
        """Genera propuesta comercial en Markdown (convertible a PDF).
        
        Args:
            hotel_data: Datos del hotel desde GBP
            claude_analysis: Análisis LLM (claude_analysis es alias de llm_analysis para compatibilidad)
            roi_data: Datos ROI
            output_dir: Directorio de salida
            seo_data: Opcional. Datos del audit SEO para include en propuesta (upsell)
        """

        paquete = claude_analysis.get("paquete_recomendado", "Pro AEO")
        region = claude_analysis.get("region") or hotel_data.get("region") or "default"
        loader = BenchmarkLoader()
        data = loader.load()

        paquetes_info = loader.get_packages()
        if paquete not in paquetes_info:
            raise ValueError(
                f"Paquete '{paquete}' no es canonico. Use uno de: {', '.join(paquetes_info.keys())}"
            )

        paquete_info = paquetes_info[paquete]
        componentes_cliente = paquete_info.get("componentes_cliente") or paquete_info.get("componentes") or []
        terminologia = loader.get_client_terminology()
        componentes_render = [self._apply_terminologia(c, terminologia) for c in componentes_cliente]

        # Datos GBP para evaluar addon de actividad (ya viene pre-procesado desde pipeline)
        gbp_data = claude_analysis.get('gbp_data', {}) or {}
        
        # Addon ya viene pre-procesado desde pipeline._apply_addon_to_roi()
        addon = roi_data.get('addon_aplicado')
        addon_precio = roi_data.get('addon_precio', 0)
        addon_componentes = []
        if addon:
            addons = loader.get_addons()
            terminologia = loader.get_client_terminology()
            addon_data = addons.get(addon, {})
            addon_componentes = [self._apply_terminologia(c, terminologia) for c in addon_data.get('componentes', [])]
        paquete_final = f"{paquete} + {addon}" if addon else paquete


        precio_base = int(paquete_info.get('precio_cop') or paquete_info.get('precio', 0))
        precio_mensual = precio_base + addon_precio

        inversion_breakdown = ""
        if addon and addon_precio:
            inversion_breakdown = (
                f"\n\n**Desglose:** ${precio_base:,.0f} COP/mes base ({paquete}) + "
                f"${addon_precio:,.0f} COP/mes addon ({addon})"
            )

        # Calculo dinámico de ROI esperado basado en proyección real
        roas_valor = roi_data.get('totales_6_meses', {}).get('roas', 0)
        roi_text = f"{roas_valor}X en 6 meses" if roas_valor else "Proyección positiva"

        # Owner-friendly bundle (regional) para el Plan Maestro
        owner_bundle = loader.get_owner_bundle(paquete, region)
        owner_plan = self._format_owner_block(
            owner_bundle.get("plan_7_30_60_90"),
            "Plan 7/30/60/90 se entrega en onboarding (perfil regional por defecto).",
        )
        owner_kpis = self._format_owner_block(
            owner_bundle.get("kpis_cliente"),
            "KPIs se definen en kickoff con benchmarks regionales.",
        )
        owner_dependencias = self._format_owner_block(
            owner_bundle.get("dependencias_cliente"),
            "Solo necesitamos punto de contacto y accesos GBP/Analytics.",
        )
        owner_implementacion = self._render_implementacion_section(paquete_info, hotel_data, loader)
        owner_cadencia = self._format_owner_block(
            owner_bundle.get("cadencia_mensual"),
            "Cadencia mensual estándar (kickoff + 2 checkpoints).",
        )
        owner_playbook = self._format_owner_block(
            owner_bundle.get("playbook_cierre"),
            "Playbook de cierre se comparte en el primer hito.",
        )
        owner_upgrade = self._format_owner_block(
            owner_bundle.get("triggers_upgrade"),
            "Escalamos de paquete cuando agotamos acciones del plan base.",
        )
        region_label = str(region).replace("_", " ").title()

        # Incluir sección SEO solo si hay datos disponibles Y el score es bajo (< 70)
        seo_section = ""
        if seo_data:
            credibility_score = seo_data.get('score', 0)
            # CONDICIÓN CLAVE: Solo integrar si el score es menor a 70
            if credibility_score < 70:
                issues = seo_data.get('issues', [])
                revenue_loss = seo_data.get('estimated_revenue_loss', 0)
                
                # Tono dinamico basado en score
                if credibility_score < 60:
                    status_icon = "🚨"
                    status_text = "CRÍTICO"
                    intro_text = "Su sitio web presenta bloqueos técnicos graves que impiden la conversión de visitantes."
                else:
                    status_icon = "⚠️"
                    status_text = "MEJORABLE"
                    intro_text = "Su sitio web tiene una base funcional pero pierde reservas por fricciones técnicas evitables."

                seo_section = f"""
---

## {status_icon} DIAGNÓSTICO TÉCNICO WEB (SEO ACCELERATOR)

**Score de Credibilidad: {credibility_score}/100 ({status_text})**
**Impacto Financiero: ${revenue_loss:,.0f} COP/mes en riesgo**

{intro_text}

### Principales Fugas de Dinero Detectadas:
"""
                # Añadir hasta 4 problemas más críticos
                display_issues = issues[:4]
                for issue in display_issues:
                    title = issue.get('title', 'Problema detectado')
                    priority = issue.get('priority', 'ALTO')
                    
                    # Mapear prioridad a iconos
                    prio_icon = "🔴" if priority in ["CRÍTICO", "CRITICO", "ALTO"] else "🟡"
                    
                    seo_section += f"\\n- {prio_icon} **{title}**"
                
                seo_section += f"""

### 💡 Solución Incluida en {paquete}
El paquete **{paquete}** incluye la corrección prioritaria de estos {len(display_issues)} puntos de fricción para asegurar que cada visita generada tenga la máxima probabilidad de convertirse en reserva directa.

---

"""
        
        # ... (resto del código)

        # Justificación enriquecida con addon si aplica
        justificacion = claude_analysis.get('justificacion_paquete', 'Evaluación según arquitectura 4-Pilares del Plan Maestro (GEO + AEO + SEO + IAO), alineada con benchmarking')
        if addon:
            activity_score = gbp_data.get('gbp_activity_score', gbp_data.get('activity_score', 0))
            justificacion += (
                f"\n\n**Addon recomendado:** {addon} (+${addon_precio:,} COP/mes) por inactividad crítica "
                f"(activity {activity_score}/100)."
            )

        content = f"""# PROPUESTA COMERCIAL
    ## {hotel_data.get('nombre')}

    **Fecha**: {self._format_date_es(datetime.now())}  
    **Valido hasta**: {self._format_date_es(datetime.now() + timedelta(days=30))}

---

## [TARGET] RESUMEN EJECUTIVO

Su hotel esta dejando de percibir aproximadamente **${claude_analysis.get('perdida_mensual_total', 0):,.0f} COP al mes** en reservas directas debido a brechas criticas en visibilidad digital.

**Nuestra propuesta:** Implementar el modelo 4-Pilares (GEO + AEO + SEO + IAO) para capturar estas reservas perdidas y reducir su dependencia de OTAs en un 25% en 6 meses. SEO se activa cuando detectamos brecha; si el score es sólido, solo monitoreamos.
{seo_section}
---

## [CLIP] PAQUETE RECOMENDADO: {paquete_final}

### Inversion Mensual
**${precio_mensual:,.0f} COP/mes**{inversion_breakdown}

### Componentes Incluidos
{chr(10).join([f"[OK] {comp}" for comp in componentes_render + addon_componentes])}

{self._render_disclaimers(paquete_info, loader)}

### ROI Proyectado
**{roi_text}**

---

## [CHECK] JUSTIFICACION DE RECOMENDACION

**Paquete seleccionado:** {paquete}

**Metricas de decision:**
- Resenas Google: {claude_analysis.get('gbp_data', {}).get('reviews', 0)} reviews
- Score GBP: {claude_analysis.get('gbp_data', {}).get('score', 0)}/100
- Schema.org: {'[OK] Implementado' if claude_analysis.get('schema_data', {}).get('tiene_hotel_schema', False) else '[NO] Faltante'}
- Menciones IA: {claude_analysis.get('ia_test', {}).get('perplexity', {}).get('menciones', 0) + claude_analysis.get('ia_test', {}).get('chatgpt', {}).get('menciones', 0)} en ChatGPT/Perplexity

**Razonamiento:**
{justificacion}

---

## [MONEY] PROYECCION FINANCIERA (6 MESES)

| Mes | Inversion | Ingreso Recuperado | Beneficio Neto | Acumulado |
|-----|-----------|-------------------|----------------|-----------|
{self._format_proyeccion_propuesta(roi_data.get('proyeccion_6_meses', []))}

**RESUMEN 6 MESES:**
- [MONEY] Inversion Total: ${roi_data.get('totales_6_meses', {}).get('inversion_total', 0):,.0f} COP
- [MONEY] Ingreso Recuperado: ${roi_data.get('totales_6_meses', {}).get('ingreso_recuperado', 0):,.0f} COP
- [MONEY] Beneficio Neto: ${roi_data.get('totales_6_meses', {}).get('beneficio_neto', 0):,.0f} COP

---

## 🧭 PLAN DEL DUEÑO (REGIÓN {region_label.upper()})

### [PLAN] 7/30/60/90 días
{owner_plan}

### [KPIS] Lo que mediremos cada mes
{owner_kpis}

### [NECESITAMOS] Responsables y accesos del hotel
{owner_dependencias}

### [IMPLEMENTACION] Cómo se instala (sin IT)
{owner_implementacion}

### [CADENCIA] Reuniones y entregables
{owner_cadencia}

### [CIERRE] Playbook para cerrar ventas
{owner_playbook}

### [UPGRADE] Cuándo subir de paquete
{owner_upgrade}

---

## [OK] GARANTIAS

### 1. Resultados Medibles
Si no ve un incremento minimo del 10% en consultas directas en los primeros 90 dias, **extendemos el servicio 1 mes gratis**.

### 2. Transparencia Total
Acceso a reportes y métricas acordadas durante el servicio.

### 3. Sin Permanencia Forzada
Contrato mes a mes. Cancela cuando quieras sin penalizaciones.
{self._render_certificate_guarantee(paquete, loader)}

---

## [PHONE] COMO EMPEZAMOS

### 1 Aprobacion Propuesta
- [OK] Acepta terminos aqui mismo
- [OK] Firma digital o documento fisico

### 2 Kickoff (Dia 1)
- [OK] Reunion 30 min equipo
- [OK] Acceso a plataformas
- [OK] Definicion KPIs clave

### 3 Implementacion (Dias 2-30)
- [OK] Setup GBP avanzado
- [OK] Implementacion Schema.org
- [OK] Configuracion FAQs

### 4 Primeros Resultados (Semana 1)
- [OK] Visibilidad en mapas mejora
- [OK] Comienzan consultas directas
- [OK] Resumen de KPIs y próximos pasos

### 5 Optimizacion Continua (Mes 1+)
- [OK] Analisis semanal desempeño
- [OK] Ajustes basados en datos
- [OK] Escalado de lo que funciona

---

## [CARD] FORMAS DE PAGO

[OK] Transferencia bancaria  
[OK] PSE  
[OK] Tarjeta credito (hasta 3 cuotas sin interes)  
[OK] Cheque (empresas)

**Descuentos:**
- Pago trimestral adelantado: 10% descuento
- Pago semestral adelantado: 18% descuento

---

## [CLIP] TERMINOS Y CONDICIONES

1. **Duracion contrato**: Mes a mes con renovacion automatica
2. **Cancelacion**: Aviso 15 dias antes del siguiente ciclo
3. **Entregables**: Segun cronograma acordado en kickoff
4. **Propiedad intelectual**: Todo el contenido creado es suyo
5. **Confidencialidad**: NDA incluido en contrato
6. **Soporte**: Lunes a viernes 9am-6pm, WhatsApp prioritario

---

## [WRITE] ACEPTACION

Acepto los terminos de esta propuesta y autorizo el inicio de servicios:

**Nombre completo**: ___________________________  
**Cargo**: ___________________________  
**Cedula/NIT**: ___________________________  
**Fecha**: ___________________________  
**Firma**: ___________________________

---

## [PHONE] CONTACTO

**IA Hoteles Agent**  
"Primera Recomendacion en Agentes IA"

[EMAIL] Email: contacto@iahoteles.co  
[PHONE] WhatsApp: +57 300 000 0000  
 Web: www.iahoteles.co  
[DATE] Agendar call: [calendly.com/iahoteles]

---

*Esta propuesta fue generada especificamente para {hotel_data.get('nombre')} basada en analisis real de su situacion digital actual.*
"""

        output_path = output_dir / "02_PROPUESTA_COMERCIAL.md"
        output_path.write_text(self._normalize_markdown(content), encoding="utf-8")
        print("   [OK] Propuesta comercial generada")

    def _format_proyeccion_propuesta(self, proyeccion):
        """Formatea tabla de proyeccion para propuesta."""

        if not proyeccion:
            return "| - | - | - | - | - |"

        rows = ""
        for row in proyeccion:
            rows += (
                f"| {row['mes']} | ${row['inversion']:,.0f} | "
                f"${row['ingreso_recuperado']:,.0f} | ${row['beneficio_neto']:,.0f} | "
                f"${row['acumulado']:,.0f} |\n"
            )
        return rows

    def _format_owner_block(self, items: Optional[List[str]], fallback: str) -> str:
        """Renderiza bullets owner-friendly con fallback explícito."""
        if not items:
            return f"- {fallback}"
        return "\n".join([f"- {item}" for item in items])

    def _apply_terminologia(self, texto: str, mapping: dict) -> str:
        """Reemplaza terminos tecnicos por alternativas cliente-friendly."""
        if not texto:
            return ""
        for term, replacement in (mapping or {}).items():
            texto = texto.replace(term, replacement)
        return texto

    def _render_disclaimers(self, paquete_info: dict, loader: BenchmarkLoader) -> str:
        disclaimers_map = loader.get_client_disclaimers()
        disclaimers_ids = paquete_info.get("disclaimers_cliente", []) or []
        disclaimers_txt = [disclaimers_map.get(d) for d in disclaimers_ids if disclaimers_map.get(d)]
        if not disclaimers_txt:
            return ""
        return "\n" + "\n".join([f"*Nota*: {txt}" for txt in disclaimers_txt]) + "\n"

    def _render_certificate_guarantee(self, paquete: str, loader: BenchmarkLoader) -> str:
        cfg = loader.get_certificates_config()
        allowed = cfg.get("allowed_packages", []) or []
        items = cfg.get("items", []) or []
        if paquete not in allowed:
            return ""
        items_text = ", ".join(items) if items else "Certificados de Reserva Directa y Web Optimizada"
        return (
            "\n\n### 4. Certificados"
            f"\nIncluimos: {items_text}. Se activan al cumplir los umbrales definidos en onboarding."
        )

    def _render_implementacion_section(self, paquete_info: dict, hotel_data: dict, loader: BenchmarkLoader) -> str:
        """Renderiza una sección operativa post-propuesta para hoteles sin IT.

        Regla de diseño: no prometer despliegue automático. Solo clarificar el "cómo" y el "quién".
        """

        paquete_requiere_web = bool(paquete_info.get("requiere_cambio_web"))
        impl_data = paquete_info.get("implementacion_sin_it", {}) or {}

        if not paquete_requiere_web and not impl_data:
            return "- No requiere cambios técnicos adicionales en la web (solo publicación/ajustes guiados)."

        terminology = loader.get_client_terminology() or {}

        providers_cost = impl_data.get("proveedores_estimado_cop", {}) or {}
        min_cost = int(providers_cost.get("min", 200_000) or 200_000)
        max_cost = int(providers_cost.get("max", 500_000) or 500_000)

        cms = (hotel_data.get("cms_platform") or "").strip()
        cms_hint = f" (CMS detectado: {cms})" if cms else ""

        bullets = [
            "- Entregamos archivos listos para copiar/pegar y una guía paso a paso.",
            f"- Si tienes proveedor web{cms_hint}: le envías los archivos y la checklist de validación.",
            f"- Si NO tienes proveedor web: puedes contratar un freelancer (estimado ${min_cost:,.0f}–${max_cost:,.0f} COP) para pegar los snippets.",
            "- Medición: el botón de WhatsApp registra clics en GA4 (evento `whatsapp_click`) o via GTM.",
        ]

        # Make terminology client-friendly where relevant.
        rendered = "\n".join([self._apply_terminologia(line, terminology) for line in bullets])
        return rendered
