# modules/analyzers/gap_analyzer.py
import os
import json
import time
from pathlib import Path

# Import provider adapter
try:
    from modules.providers.llm_provider import ProviderAdapter
    from modules.scrapers.scraper_fallback import ScraperFallback
    from modules.utils.financial_factors import FinancialFactors
except ImportError:
    # Fallback para compatibilidad
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    from providers.llm_provider import ProviderAdapter
    from scrapers.scraper_fallback import ScraperFallback
    from utils.financial_factors import FinancialFactors

class GapAnalyzer:
    def __init__(self, provider_type=None):
        self.llm_adapter = ProviderAdapter(provider_type)
    
    def analyze_with_llm(self, hotel_data, gbp_data, schema_data, ia_test):
        """Run full gap analysis using configured LLM provider."""
        
        # Prepare context for LLM
        context = self._prepare_context(hotel_data, gbp_data, schema_data, ia_test)
        
        # Prompt afinado para reforzar el modelo "2 Pilares"
        prompt = (
            "Eres un experto en posicionamiento digital para hoteles boutique en Colombia, "
            "especializado en el modelo 2-Pilares del Plan Maestro (Pilar 1: GBP & Voz Cercana / Pilar 2: Datos JSON-LD para IA).\n\n"
            "Analiza este hotel y genera un diagnostico comercial consistente con el Plan Maestro 2024-2025:\n\n"
            "DATOS DEL HOTEL:\n"
            f"{json.dumps(context, indent=2, ensure_ascii=False)}\n\n"
            "INSTRUCCIONES:\n"
            "1. Identifica las 3 brechas criticas MAS costosas (cada una con impacto en COP/mes)\n"
            "2. Propone 3 Quick Wins ejecutables en 30 dias\n"
            "3. Calcula perdida mensual estimada realista\n"
            "4. Recomienda paquete (Starter GEO / Pro AEO / Pro AEO Plus / Elite / Elite PLUS)\n"
            "5. Genera propuesta de valor personalizada para el gerente\n"
            "6. Usa las 'top_brechas' de scraper_alerts para reforzar las brechas criticas y cita el paquete sugerido\n"
            "7. Justifica la urgencia con el score_visibilidad_ia y cierra con el CTA: 'Solicita tu diagnóstico 2-Pilares en 15 min'\n\n"
            "CONTEXTO DEL PLAN MAESTRO:\n"
            "- Benchmarking 2024-2025 (RevPAR minimo sostenible): Eje Cafetero 150000 COP, Caribe 247000 COP, Antioquia 150000 COP\n"
            "- ADR objetivo: Eje 300000 COP, Caribe 380000 COP, Antioquia 250000 COP\n"
            "- Ocupacion objetivo: Eje 55%, Caribe 70%, Antioquia 60%\n"
            "- Comision OTA promedio: 18%\n"
            "- Meta: reducir dependencia OTA en -25% (6 meses) activando 2 Pilares en paralelo\n"
            "- KPIs Oro: ACS >=40%, AOIR >=60%, DVL +35%, ROAS 8X\n\n"
            "FORMATO DE RESPUESTA (JSON estructurado):\n"
            "{\n"
            "  \"brechas_criticas\": [\n"
            "    {\n"
            "      \"nombre\": \"string\",\n"
            "      \"impacto_mensual\": number,\n"
            "      \"descripcion\": \"string\",\n"
            "      \"prioridad\": 1-3\n"
            "    }\n"
            "  ],\n"
            "  \"perdida_mensual_total\": number,\n"
            "  \"quick_wins\": [\"string\"],\n"
            "  \"paquete_recomendado\": \"Starter|Pro|Elite|Elite PLUS\",\n"
            "  \"justificacion_paquete\": \"string\",\n"
            "  \"propuesta_valor\": \"string (2-3 lineas, tono ejecutivo)\",\n"
            "  \"roi_6meses\": \"string (ej: 5.2X)\",\n"
            "  \"recuperacion_inversion\": \"string (ej: Mes 2)\",\n"
            "  \"metricas_clave\": {\n"
            "    \"reservas_perdidas_mes\": number,\n"
            "    \"reservas_potenciales_recuperadas\": number,\n"
            "    \"ahorro_comisiones_6meses\": number\n"
            "  }\n"
            "}\n\n"
            "IMPORTANTE:\n"
            "- Se especifico con cifras en COP\n"
            "- Usa datos reales del hotel cuando esten disponibles\n"
            "- Integra las brechas del scraper sin duplicar descripciones, aprovechando su impacto_estimado y paquete sugerido\n"
            "- Marca claramente si algo es \"estimado\" vs \"real\"\n"
            "- Tono: ejecutivo pero cercano, enfocado en ROI\n"
        )

        try:
            content = self.llm_adapter.unified_request(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.7
            )
            
            # Extract JSON snippet from response (compatible with both providers)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            if not isinstance(content, str):
                raise TypeError("LLM response content must be a string")

            analysis = json.loads(content)
            
            # Enrich with metadata
            analysis['confianza_datos'] = hotel_data.get('confidence', 'media')
            analysis['campos_estimados'] = hotel_data.get('campos_estimados', [])
            analysis['fecha_analisis'] = time.strftime('%Y-%m-%d')
            analysis['proveedor_llm'] = self.llm_adapter.get_current_provider()
            
            return analysis
            
        except json.JSONDecodeError as exc:
            print(f"[ERROR] Unable to parse LLM response as JSON: {exc}")
            return self._basic_analysis(hotel_data, gbp_data, schema_data, ia_test)
        except Exception as exc:
            print(f"[ERROR] LLM analysis failure: {exc}")
            # Fallback to basic analysis
            return self._basic_analysis(hotel_data, gbp_data, schema_data, ia_test)
    
    # Keep helper methods unchanged
    def _prepare_context(self, hotel_data, gbp_data, schema_data, ia_test):
        """Prepare structured context for LLM."""
        return {
            "hotel": {
                "nombre": hotel_data.get('nombre'),
                "ubicacion": hotel_data.get('ubicacion'),
                "habitaciones": hotel_data.get('habitaciones'),
                "precio_promedio": hotel_data.get('precio_promedio'),
                "servicios": hotel_data.get('servicios', []),
                "confianza_datos": hotel_data.get('confidence'),
                "campos_estimados": hotel_data.get('campos_estimados', [])
            },
            "gbp": {
                "score": gbp_data.get('score', 0),
                "existe": gbp_data.get('existe', False),
                "reviews": gbp_data.get('reviews', 0),
                "rating": gbp_data.get('rating', 0),
                "issues": gbp_data.get('issues', [])
            },
            "schema": {
                "score": schema_data.get('score_schema', 0),
                "tiene_hotel_schema": schema_data.get('tiene_hotel_schema', False),
                "schemas_faltantes": schema_data.get('schemas_faltantes', []),
                "campos_faltantes": schema_data.get('campos_faltantes', [])
            },
            "ia_visibility": {
                "perplexity_menciones": ia_test.get('perplexity', {}).get('menciones', 0),
                "chatgpt_menciones": ia_test.get('chatgpt', {}).get('menciones', 0),
                "total_queries": ia_test.get('total_queries', 0)
            },
            "scraper_alerts": self._summarize_scraper_alerts(hotel_data)
        }

    def _summarize_scraper_alerts(self, hotel_data):
        brechas = hotel_data.get('brechas_detectadas') or []
        score = hotel_data.get('score_visibilidad_ia')

        if not brechas and score in (None, ""):
            return {}

        def sort_key(brecha):
            return brecha.get('prioridad', 99), brecha.get('severidad', 'Z')

        top_alerts = []
        for brecha in sorted(brechas, key=sort_key)[:5]:
            top_alerts.append({
                "tipo": brecha.get('tipo'),
                "severidad": brecha.get('severidad'),
                "impacto": brecha.get('impacto_estimado'),
                "paquete_recomendado": self._map_brecha_to_paquete(brecha.get('tipo')),
                "solucion_rapida": brecha.get('solucion_rapida')
            })

        return {
            "score_visibilidad_ia": score,
            "top_brechas": top_alerts
        }

    def _map_brecha_to_paquete(self, tipo: str) -> str:
        """
        Mapea tipo de brecha detectada al paquete sugerido.
        
        Args:
            tipo: Tipo de brecha (gbp_incompleto, schema_faltante, etc.)
        
        Returns:
            str: Nombre del paquete recomendado
        """
        mapping = {
            "gbp_incompleto": "Starter GEO",
            "gbp_sin_optimizar": "Starter GEO",
            "reviews_insuficientes": "Starter GEO",
            "schema_faltante": "Pro AEO",
            "json_ld_incompleto": "Pro AEO",
            "ia_invisibilidad": "Pro AEO",
            "web_obsoleta": "Elite PLUS",
            "sin_automatizacion": "Elite",
            "conversion_baja": "Elite PLUS"
        }
        return mapping.get(tipo, "Pro AEO")

    def _basic_analysis(self, hotel_data, gbp_data, schema_data, ia_test):
        """
        Genera análisis básico usando lógica local (fallback sin LLM).
        
        Alineado con Plan Maestro v2.2 y BenchmarkingV2.
        Factores de captura calibrados por región para producir Costo de Inacción defendible.
        """
        # Import centralizado de recomendación de paquetes
        from modules.utils.package_recommender import determine_package
        
        # Obtener datos de fallback para la región
        fallback_helper = ScraperFallback()
        region = fallback_helper._detect_region(
            hotel_data.get('ubicacion', '')
        )
        
        region_data = fallback_helper.benchmarks['regiones'].get(
            region, fallback_helper.benchmarks['regiones']['default']
        )

        # Priorizar habitaciones reales sobre promedio regional
        habitaciones_real = hotel_data.get('habitaciones')
        fuente_habitaciones = 'real' if habitaciones_real and habitaciones_real > 0 else 'estimado'
        habitaciones = habitaciones_real if habitaciones_real and habitaciones_real > 0 else region_data.get('habitaciones_promedio', 15)
        
        precio = hotel_data.get('precio_promedio') or region_data.get('precio_promedio', 280000)
        ocupacion = hotel_data.get('ocupacion_actual') or region_data.get('ocupacion', 0.6)
        if not precio:
            precio = region_data.get('precio_promedio', 280000)
        if not ocupacion:
            ocupacion = region_data.get('ocupacion', 0.6)

        # RevPAR targets actualizados según BenchmarkingV2
        revpar_targets = {
            'eje_cafetero': 171600,  # BM v2 Sec 3.1
            'caribe': 270600,        # BM v2 Sec 3.2
            'antioquia': 168000,     # BM v2 Sec 3.3
            'default': int(region_data.get('precio_promedio', 280000) * region_data.get('ocupacion', 0.6))
        }
        revpar_objetivo = revpar_targets.get(region, revpar_targets['default'])
        
        # Usar FinancialFactors para valores centralizados desde plan_maestro_data.json
        financial = FinancialFactors()
        config = financial.get_config(region)
        
        factor_aila = config.factor_captura_aila
        COMISION_OTA_MIN = config.comision_ota_min
        COMISION_OTA_BASE = config.comision_ota_base
        COMISION_OTA_MAX = config.comision_ota_max
        PENALIZACION_INVISIBILIDAD_IA = config.penalizacion_invisibilidad_ia
        
        factor_perdida_base = financial.calculate_factor_perdida(region)
        factor_perdida_min = (1 - factor_aila) * (COMISION_OTA_MIN + PENALIZACION_INVISIBILIDAD_IA)
        factor_perdida_max = (1 - factor_aila) * (COMISION_OTA_MAX + PENALIZACION_INVISIBILIDAD_IA)

        perdida_mensual = int(revpar_objetivo * habitaciones * 30 * factor_perdida_base)
        perdida_min = int(revpar_objetivo * habitaciones * 30 * factor_perdida_min)
        perdida_max = int(revpar_objetivo * habitaciones * 30 * factor_perdida_max)
        reservas_perdidas = max(int(perdida_mensual / max(precio, 1)), 6)

        # Extraer métricas para determinar paquete
        reviews = gbp_data.get('reviews', 0)
        gbp_score = gbp_data.get('score', 0)
        schema_score = schema_data.get('score_schema', 0)
        tiene_schema = schema_data.get('tiene_hotel_schema', False)
        total_mentions = (
            ia_test.get('perplexity', {}).get('menciones', 0)
            + ia_test.get('chatgpt', {}).get('menciones', 0)
        )

        # Usar módulo centralizado para recomendación de paquete
        paquete_recomendado, justificacion_paquete = determine_package(
            region=region,
            reviews=reviews,
            gbp_score=gbp_score,
            schema_score=schema_score,
            tiene_schema=tiene_schema,
            total_mentions=total_mentions,
            precio_promedio=precio,
            hotel_data=hotel_data
        )

        # Distribución dinámica de brechas basada en gaps reales vs benchmarks regionales
        # En lugar de distribución fija 40%/35%/25%, calcular proporcionalmente
        geo_benchmark = region_data.get('geo_score_ref', 42)
        aeo_benchmark = region_data.get('aeo_score_ref', 18)
        iao_benchmark = region_data.get('iao_score_ref', 8)
        
        aeo_score = schema_data.get('score_schema', 0)
        iao_score = ia_test.get('iao_score', self._calculate_iao_score(ia_test))
        
        # Calcular gaps (máximo 0 si score > benchmark)
        gap_geo = max(0, geo_benchmark - gbp_score)
        gap_aeo = max(0, aeo_benchmark - aeo_score)
        gap_iao = max(0, iao_benchmark - iao_score)
        
        # Distribuir proporcionalmente solo si hay gaps
        suma_gaps = gap_geo + gap_aeo + gap_iao
        
        brechas_criticas = []
        
        if suma_gaps > 0:
            # Pilar 1: GBP
            if gap_geo > 0:
                peso_geo = gap_geo / suma_gaps
                brechas_criticas.append({
                    "nombre": "Pilar 1: GBP sin optimizar",
                    "impacto_mensual": int(perdida_mensual * peso_geo),
                    "descripcion": "GBP y reseñas insuficientes restan visibilidad en mapas y voz cercana.",
                    "prioridad": 1,
                    "gap_actual": f"{gbp_score}/100",
                    "benchmark_regional": f"{geo_benchmark}/100"
                })
            
            # Pilar 2: AEO (JSON)
            if gap_aeo > 0:
                peso_aeo = gap_aeo / suma_gaps
                brechas_criticas.append({
                    "nombre": "Pilar 2: Datos JSON incompletos",
                    "impacto_mensual": int(perdida_mensual * peso_aeo),
                    "descripcion": "Sin Schema estructurado el hotel no entra en respuestas de IA generativa.",
                    "prioridad": 1,
                    "gap_actual": f"{aeo_score}/100",
                    "benchmark_regional": f"{aeo_benchmark}/100"
                })
            
            # Pilar 3: IAO (Momentum IA)
            if gap_iao > 0:
                peso_iao = gap_iao / suma_gaps
                brechas_criticas.append({
                    "nombre": "Momentum IA pendiente",
                    "impacto_mensual": int(perdida_mensual * peso_iao),
                    "descripcion": "Perplexity y ChatGPT no mencionan al hotel; oportunidad de voz/comparadores IA.",
                    "prioridad": 2,
                    "gap_actual": f"{iao_score}/100",
                    "benchmark_regional": f"{iao_benchmark}/100"
                })
        else:
            # Si no hay gaps, retornar lista vacía (hotel ya cumple benchmarks)
            brechas_criticas = []

        return {
            "brechas_criticas": brechas_criticas,
            "perdida_mensual_total": perdida_mensual,
            "quick_wins": [
                "Optimizar GBP (Pilar 1) con fotos, Q&A y reseñas verificadas en 7 dias.",
                "Implementar JSON-LD Hotel + FAQ para abrir Pilar 2 en 15 dias.",
                "Publicar ficha 2-Pilares en Perplexity/ChatGPT.",
                "Califica al Certificado Reserva Directa al alcanzar 60% de reservas propias."
            ],
            "paquete_recomendado": paquete_recomendado,
            "justificacion_paquete": justificacion_paquete,
            "propuesta_valor": "Activamos los 2 Pilares (GBP + JSON-LD) para recuperar reservas directas y reducir comisiones en 90 dias.",
            "roi_6meses": "5.0X",
            "recuperacion_inversion": "Mes 2",
            "metricas_clave": {
                "reservas_perdidas_mes": reservas_perdidas,
                "reservas_potenciales_recuperadas": max(int(reservas_perdidas * 0.65), 6),
                "ahorro_comisiones_6meses": int(perdida_mensual * 0.18 * 6),
                "revpar_objetivo": revpar_objetivo
            },
            "region_detectada": region,
            "gbp_data": {"reviews": reviews, "score": gbp_score},
            "schema_data": {"score_schema": schema_score, "tiene_hotel_schema": tiene_schema},
            "ia_test": {"total_mentions": total_mentions},
            "confianza_datos": hotel_data.get('confidence', 'media'),
            "campos_estimados": hotel_data.get('campos_estimados', []),
            "fecha_analisis": time.strftime('%Y-%m-%d'),
            "proveedor_llm": "fallback",
            "modelo_pilares": "2 Pilares GEO + JSON",
            "fuente_habitaciones": fuente_habitaciones,
            "factor_captura_regional": factor_perdida_base,
"modelo_perdidas": {
                "perdida_mensual_total": perdida_mensual,
                "perdida_intervalo_confianza": [perdida_min, perdida_max],
                "factor_captura_aila": factor_aila,
                "factor_perdida_aplicado": factor_perdida_base,
                "factor_superposicion": FinancialFactors.SUPERPOSITION_FACTOR,
                "nota_superposicion": "Factor 0.7 aplicado para evitar doble conteo de pérdidas superpuestas (estándar industria)",
                "comision_ota_base": COMISION_OTA_BASE,
                "penalizacion_invisibilidad_ia": PENALIZACION_INVISIBILIDAD_IA,
                "fuente": "Indice AILA Colombia - Guia Benchmarking Nacional 2026",
                "formula": "RevPAR x hab x 30 x (1 - AILA) x (comision + penalizacion)"
            }
        }

    def _calculate_iao_score(self, ia_test: dict) -> int:
        """Calculate IAO score based on mentions in Perplexity and ChatGPT."""
        total_menciones = (
            ia_test.get('perplexity', {}).get('menciones', 0) +
            ia_test.get('chatgpt', {}).get('menciones', 0)
        )
        total_queries = ia_test.get('total_queries', 1) * 2
        score = (total_menciones / max(total_queries, 1)) * 100
        return int(score)

    def analyze_with_claude(self, hotel_data, gbp_data, schema_data, ia_test):
        """Alias retained for backwards compatibility with main.py."""
        return self.analyze_with_llm(hotel_data, gbp_data, schema_data, ia_test)

    def get_quick_win_action(self, hotel_data: dict, gbp_data: dict, schema_data: dict, ia_test: dict) -> dict:
        """
        Selecciona una acción gratuita inmediata basada en el análisis.
        Devuelve un dict con action, expected_impact, time_to_complete, difficulty, reason.
        
        INJERTO #2 (B.md): Añade campo 'reason' para explicar POR QUÉ este tip es 
        específico para este hotel. Impacto esperado: +10% reciprocidad percibida.
        
        Lógica:
        - Si GBP score < 50: Sube fotos (problema: invisibilidad crítica)
        - Si no hay Schema.org: Añade horarios (problema: IA no te entiende)
        - Si reviews < 10: Pide reseñas (problema: poca prueba social)
        - Si amenities no documentadas: Documenta servicios
        - Default: Mejora descripción
        """
        gbp_score = gbp_data.get('score', 0)
        reviews = gbp_data.get('reviews', 0)
        tiene_schema = schema_data.get('tiene_hotel_schema', False)
        
        # Caso 1: GBP Score bajo - INVISIBILIDAD CRÍTICA
        if gbp_score < 50:
            return {
                "case": "LOW_GBP_PHOTOS",
                "action": "Sube 5 fotos NUEVAS a tu perfil de Google Maps esta semana. Usa fotos claras de: (1) fachada del hotel, (2) recepción, (3) habitación, (4) piscina/área común, (5) desayuno. Asegúrate de que cada foto tenga título y descripción.",
                "expected_impact": "+15% en consultas desde 'cerca de mí'",
                "time_to_complete": "20 minutos",
                "difficulty": "Muy Fácil",
                "priority": "MÁXIMA",
                "reason": f"Tu Score GBP es {gbp_score}/100 (crítico). Antes de traerte clientes, tu perfil debe existir visualmente. Las fotos son lo primero que mejora tu visibilidad."
            }
        
        # Caso 2: Sin Schema.org - IA NO TE ENTIENDE
        if not tiene_schema:
            return {
                "case": "MISSING_SCHEMA",
                "action": "Añade horarios de atención y disponibilidad a tu web principal. Incluye: horario recepción (24/7), check-in (15:00), check-out (11:00), teléfono de emergencia. Los asistentes IA necesitan esta información para recomendarte.",
                "expected_impact": "+20% en menciones ChatGPT/Perplexity",
                "time_to_complete": "15 minutos",
                "difficulty": "Muy Fácil",
                "priority": "ALTA",
                "reason": "Tu web no tiene datos estructurados (Schema). Esto significa que ChatGPT y Perplexity no entienden qué eres ni qué ofreces. Añadir horarios es el primer paso para que las IAs te lean."
            }
        
        # Caso 3: Pocas reseñas - POCA PRUEBA SOCIAL
        if reviews < 10:
            return {
                "case": "LOW_REVIEWS",
                "action": f"Pide reseñas a 3 clientes satisfechos esta semana. Usa esta plantilla por WhatsApp: 'Don/Doña [nombre], fue un placer recibirte. ¿Te animas a dejar una reseña en Google? Toma 30 segundos y ayuda mucho a otros viajeros a encontrarnos. Aquí el link: [URL Google Reviews]'",
                "expected_impact": "+10 reseñas en 2 semanas, +30% en confianza GBP",
                "time_to_complete": "10 minutos",
                "difficulty": "Muy Fácil",
                "priority": "ALTA",
                "reason": f"Solo tienes {reviews} reseñas. Hoteles con menos de 10 reseñas pierden 40% de clientes potenciales porque Google no confía en perfiles sin prueba social."
            }
        
        # Caso 4: Amenities no documentadas
        hotel_amenities = hotel_data.get('amenidades', [])
        if not hotel_amenities or len(hotel_amenities) < 3:
            return {
                "case": "MISSING_AMENITIES",
                "action": "Haz una lista de TODO lo que ofreces: piscina, WiFi, estacionamiento, desayuno, vista, etc. Añádelo a tu web en una sección visible llamada 'Servicios'. Los asistentes IA buscan esto para recomendarte vs. competencia.",
                "expected_impact": "+25% en apariciones de IA",
                "time_to_complete": "30 minutos",
                "difficulty": "Moderado",
                "priority": "MEDIA",
                "reason": "Tu web no lista servicios claramente. Cuando alguien pregunta a ChatGPT '¿hotel con piscina en tu ciudad?', no puedes aparecer porque la IA no sabe qué ofreces."
            }
        
        # Default: Mejora descripción
        return {
            "case": "WEAK_DESCRIPTION",
            "action": "Reescribe la descripción de tu hotel en 2 párrafos: (1) Quiénes somos + ubicación + 2-3 servicios únicos. (2) Experiencia del cliente. Usa palabras clave de tu mercado (ej: 'familiar', 'romántico', 'descanso', 'naturaleza').",
            "expected_impact": "+18% en clicks desde Google Maps",
            "time_to_complete": "25 minutos",
            "difficulty": "Fácil",
            "priority": "MEDIA",
            "reason": "Tu descripción actual es genérica. Las IAs priorizan hoteles que describen claramente su propuesta de valor y público objetivo."
        }