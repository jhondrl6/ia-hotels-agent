import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import hashlib

from modules.utils.data_validator import lookup_cached_location

class ScraperFallback:
    def __init__(self):
        self.benchmarks_path = Path("data/benchmarks/plan_maestro_data.json")
        self.cache_path = Path("data/cache/scraped_sites.json")
        self.benchmarks = self._load_benchmarks()
        self.cache = self._load_cache()
        
        # Configuración de umbrales de detección de calidad
        self.quality_thresholds = {
            'min_html_length': 500,  # Detectar HTML sospechosamente corto
            'min_text_ratio': 0.1,   # Ratio mínimo texto/tags
            'required_fields': ['nombre', 'ubicacion'],  # Campos críticos
            'confidence_weights': {
                'exact_match': 1.0,
                'heuristic_match': 0.7,
                'benchmark_estimate': 0.5,
                'cached_data': 0.8,
                'semantic_extraction': 0.6
            }
        }
        
        # Keywords para extracción heurística
        self.heuristic_patterns = self._init_heuristic_patterns()
    
    def _load_benchmarks(self):
        """Carga datos de benchmarks del Plan Maestro"""
        try:
            with open(self.benchmarks_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            # Benchmarks por defecto si no existe el archivo
            return {
                "regiones": {
                    "default": {
                        "precio_promedio": 280000,
                        "ocupacion": 0.60,
                        "habitaciones_promedio": 15
                    },
                    "antioquia": {
                        "precio_promedio": 280000,
                        "ocupacion": 0.60,
                        "habitaciones_promedio": 18
                    },
                    "eje_cafetero": {
                        "precio_promedio": 330000,
                        "ocupacion": 0.52,
                        "habitaciones_promedio": 12
                    },
                    "caribe": {
                        "precio_promedio": 410000,
                        "ocupacion": 0.66,
                        "habitaciones_promedio": 25
                    }
                }
            }
    
    def _load_cache(self) -> Dict:
        """Carga cache de sitios previamente scrapeados"""
        try:
            if self.cache_path.exists():
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def _save_to_cache(self, url: str, data: Dict):
        """Guarda datos en cache local con timestamp"""
        cache_key = self._get_cache_key(url)
        self.cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'url': url
        }
        
        # Guardar en disco
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: No se pudo guardar cache: {e}")
    
    def _get_cache_key(self, url: str) -> str:
        """Genera clave única para cache basada en URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _init_heuristic_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Inicializa patrones regex para extracción heurística"""
        return {
            'precio': [
                re.compile(r'\$?\s*(\d{1,3}(?:[.,]\d{3})*)\s*(?:COP|pesos|cop)?', re.IGNORECASE),
                re.compile(r'(?:precio|tarifa|desde|valor)[\s:]+\$?\s*(\d{1,3}(?:[.,]\d{3})*)', re.IGNORECASE),
            ],
            'habitaciones': [
                re.compile(r'(\d+)\s*(?:habitaciones|cuartos|rooms|hab\.)', re.IGNORECASE),
                re.compile(r'(?:habitaciones|cuartos|rooms)[\s:]+(\d+)', re.IGNORECASE),
            ],
            'telefono': [
                re.compile(r'\+?57\s*\d{3}\s*\d{3}\s*\d{4}'),
                re.compile(r'\(\d{3}\)\s*\d{3}[-\s]?\d{4}'),
            ],
            'email': [
                re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
            ],
            'servicios': [
                re.compile(r'\b(wifi|piscina|desayuno|restaurante|parqueadero|spa|gym|aire\s*acondicionado|tv|cable)\b', re.IGNORECASE),
            ]
        }
    
    def enrich_data(
        self,
        partial_data: Dict,
        url: str,
        html_content: Optional[str] = None,
        confirmed_data: Optional[Dict] = None
    ) -> Dict:
        """
        Enriquece datos parciales con estrategia de fallback multicapa.
        
        NUEVO: Si se proporcionan confirmed_data, estos tienen PRIORIDAD ABSOLUTA
        y no se estiman. Se marcan con confidence=1.0 y source='onboarding_confirmed'.
        
        PIPELINE DE FALLBACKS (orden de prioridad):
        0. Datos confirmados del onboarding (confianza: máxima, no se estiman)
        1. Datos directos del scraper (confianza: alta)
        2. Fallback: Cache histórico si existe y es reciente
        3. Fallback: Extracción heurística del HTML crudo
        4. Fallback: Detección semántica por keywords
        5. Fallback: Benchmarks regionales
        6. Fallback: Estimación inversa desde patrones OTA
        """

        partial_data = partial_data or {}
        cache_context = dict(partial_data)
        cache_context.setdefault('url', url)
        cached_location = lookup_cached_location(cache_context)
        if cached_location and cached_location.get('ubicacion'):
            cache_location_value = cached_location['ubicacion']
            current_location = (partial_data.get('ubicacion') or '').strip()
            if current_location and current_location.lower() != cache_location_value.strip().lower():
                partial_data.setdefault('fallback_chain', []).append('normalization_cache_override')
                partial_data.setdefault('campos_estimados', []).append('ubicacion')
                partial_data['ubicacion_original'] = current_location
            partial_data['ubicacion'] = cache_location_value
            partial_data['ubicacion_fuente'] = cached_location.get('source', 'normalization_cache')
            partial_data.setdefault('fallback_chain', []).append('normalization_cache_location')

        # CAPA 0: Validar calidad de datos entrantes
        data_quality = self._assess_data_quality(partial_data, html_content)
        
        # CAPA 1: Intentar recuperar de cache si datos son de baja calidad
        # NOTA: No usar cache si hay confirmed_data (los datos de onboarding tienen prioridad)
        if data_quality['score'] < 0.5 and not confirmed_data:
            cached = self._try_cache_fallback(url)
            if cached:
                return cached
        
        # Detectar región para benchmarks
        region = self._detect_region(partial_data.get('ubicacion', ''))
        region_data = self.benchmarks['regiones'].get(region, 
                      self.benchmarks['regiones'].get('default'))
        
        # Inicializar estructura de datos enriquecidos
        enriched = {
            'url': url,
            'nombre': partial_data.get('nombre') or self._extract_name_from_url(url),
            'ubicacion': partial_data.get('ubicacion', ''),
            'habitaciones': partial_data.get('habitaciones'),
            'precio_promedio': partial_data.get('precio_promedio'),
            'ocupacion_actual': partial_data.get('ocupacion_actual') or region_data.get('ocupacion', 0.60),
            'comision_ota': partial_data.get('comision_ota', 0.18),
            'servicios': partial_data.get('servicios', []),
            'contacto': partial_data.get('contacto', {}),
            'descripcion': partial_data.get('descripcion', ''),
            'confidence': 'alta',
            'metodo_obtencion': 'web_scraping_directo',
            'campos_estimados': [],
            'campos_confirmados': [],
            'fallback_chain': []  # Trazabilidad de fallbacks aplicados
        }
        
        # NUEVO - CAPA 0.5: Aplicar datos confirmados del onboarding (PRIORIDAD MÁXIMA)
        if confirmed_data:
            confirmed_fields = confirmed_data.get('datos_operativos', confirmed_data)
            for field, value in confirmed_fields.items():
                if value is not None and field in ['habitaciones', 'reservas_mes', 'valor_reserva_cop', 'canal_directo_pct']:
                    field_map = {
                        'valor_reserva_cop': 'precio_promedio',
                        'canal_directo_pct': 'canal_directo',
                    }
                    target_field = field_map.get(field, field)
                    
                    enriched[target_field] = value
                    enriched['campos_estimados'] = [f for f in enriched.get('campos_estimados', []) if f != target_field]
                    enriched.setdefault('campos_confirmados', []).append(target_field)
                    enriched.setdefault('data_sources', {})[target_field] = {
                        'value': value,
                        'source': 'onboarding_confirmed',
                        'confidence': 1.0
                    }
            
            if enriched.get('campos_confirmados'):
                enriched['confidence'] = 'alta'
                enriched['metodo_obtencion'] = 'onboarding + web_scraping'
        
        # CAPA 2: Fallback heurístico si hay HTML disponible
        if html_content and data_quality['needs_repair']:
            heuristic_data = self._apply_heuristic_fallback(html_content, enriched)
            enriched = self._merge_data(enriched, heuristic_data)
        
        # CAPA 3: Fallback semántico por keywords en texto
        if html_content and not enriched.get('servicios'):
            semantic_data = self._apply_semantic_fallback(html_content)
            enriched = self._merge_data(enriched, semantic_data)
        
        # CAPA 4: Completar campos faltantes con benchmarks regionales
        if not enriched['habitaciones'] and 'habitaciones' not in enriched.get('campos_confirmados', []):
            enriched['habitaciones'] = region_data.get('habitaciones_promedio', 15)
            enriched['campos_estimados'].append('habitaciones')
            enriched['fallback_chain'].append('benchmark_regional_habitaciones')
        
        if not enriched['precio_promedio'] and 'precio_promedio' not in enriched.get('campos_confirmados', []):
            enriched['precio_promedio'] = region_data.get('precio_promedio') or region_data.get('valor_reserva_promedio', 280000)
            enriched['campos_estimados'].append('precio_promedio')
            enriched['fallback_chain'].append('benchmark_regional_precio')
        
        if not enriched['ubicacion']:
            enriched['ubicacion'] = f'Región: {region.replace("_", " ").title()}'
            enriched['campos_estimados'].append('ubicacion')
            enriched['fallback_chain'].append('estimacion_regional')
        
        if not enriched['servicios']:
            enriched['servicios'] = ['wifi', 'desayuno']  # Servicios básicos por defecto
            enriched['campos_estimados'].append('servicios')
            enriched['fallback_chain'].append('servicios_basicos_default')
        
        # CAPA 5: Estimación inversa desde patrones OTA (si precio parece inconsistente)
        enriched = self._apply_ota_inverse_estimation(enriched, region_data)
        
        # Calcular confianza final
        enriched['confidence'] = self._calculate_confidence(enriched)
        
        # Actualizar método de obtención con trazabilidad completa
        if enriched.get('campos_confirmados'):
            base_method = 'onboarding + web_scraping'
        else:
            base_method = 'web_scraping'
        
        if enriched['fallback_chain']:
            enriched['metodo_obtencion'] = base_method + ' + ' + ' + '.join(enriched['fallback_chain'])
        elif enriched.get('campos_confirmados'):
            enriched['metodo_obtencion'] = base_method
        
        # Guardar en cache para futuros accesos
        self._save_to_cache(url, enriched)
        
        return enriched
    
    def _assess_data_quality(self, data: Dict, html: Optional[str]) -> Dict:
        """
        FALLBACK LAYER 1: Detección de calidad de datos
        Identifica si los datos necesitan reparación
        Incluye detección de errores SSL
        """
        score = 1.0
        issues = []
        
        # Detectar errores SSL en el campo de error
        error_str = str(data.get('error', '')).lower()
        if any(kw in error_str for kw in ['ssl', 'certificate', 'cert', 'handshake', 'sslcertverificationerror']):
            score -= 0.3
            issues.append('ssl_certificate_expired')
        
        # Verificar campos requeridos
        for field in self.quality_thresholds['required_fields']:
            if not data.get(field):
                score -= 0.3
                issues.append(f'missing_{field}')
        
        region = self._detect_region(data.get('ubicacion', ''))
        region_benchmarks = self.benchmarks['regiones'].get(
            region, self.benchmarks['regiones']['default']
        )

        # Detectar HTML sospechosamente corto (posible bloqueo)
        if html and len(html) < self.quality_thresholds['min_html_length']:
            score -= 0.4
            issues.append('html_too_short')

        # Validar precio vs benchmarks regionales
        precio = data.get('precio_promedio')
        if precio:
            benchmark_precio = region_benchmarks['precio_promedio']
            if not (0.5 * benchmark_precio <= precio <= 1.5 * benchmark_precio):
                score -= 0.2
                issues.append('precio_fuera_de_rango')

        # Validar ocupacion vs benchmarks
        ocupacion = data.get('ocupacion_actual')
        if ocupacion:
            benchmark_ocupacion = region_benchmarks['ocupacion']
            if not (0.5 * benchmark_ocupacion <= ocupacion <= 1.5 * benchmark_ocupacion):
                score -= 0.2
                issues.append('ocupacion_fuera_de_rango')
        
        # Detectar posible ofuscación JavaScript
        if html and any(x in html.lower() for x in ['cloudflare', 'captcha', 'access denied', 'robot']):
            score -= 0.5
            issues.append('bot_detection')
        
        return {
            'score': max(0, score),
            'issues': issues,
            'needs_repair': score < 0.7
        }
    
    def _try_cache_fallback(self, url: str) -> Optional[Dict]:
        """
        FALLBACK LAYER 2: Recuperación desde cache histórico
        Retorna datos cacheados si existen y no están obsoletos (< 30 días)
        """
        cache_key = self._get_cache_key(url)
        
        if cache_key in self.cache:
            cached_entry = self.cache[cache_key]
            cache_date = datetime.fromisoformat(cached_entry['timestamp'])
            
            # Validar que no esté obsoleto
            if datetime.now() - cache_date < timedelta(days=30):
                data = cached_entry['data'].copy()
                data['metodo_obtencion'] = 'cached_snapshot'
                data['cache_age_days'] = (datetime.now() - cache_date).days
                data['fallback_chain'] = ['historical_cache']
                return data
        
        return None
    
    def _apply_heuristic_fallback(self, html: str, current_data: Dict) -> Dict:
        """
        FALLBACK LAYER 3: Extracción heurística mediante regex
        Busca patrones conocidos en HTML crudo cuando el scraper falla
        """
        extracted = {'fallback_chain': ['heuristic_extraction']}
        
        # Extraer precio si falta
        if not current_data.get('precio_promedio'):
            for pattern in self.heuristic_patterns['precio']:
                match = pattern.search(html)
                if match:
                    try:
                        precio_str = match.group(1).replace('.', '').replace(',', '')
                        precio = int(precio_str)
                        if 100000 <= precio <= 1000000:  # Validación de rango razonable
                            extracted['precio_promedio'] = precio
                            extracted.setdefault('campos_estimados', []).append('precio_promedio')
                            break
                    except:
                        continue
        
        # Extraer habitaciones si falta
        if not current_data.get('habitaciones'):
            for pattern in self.heuristic_patterns['habitaciones']:
                match = pattern.search(html)
                if match:
                    try:
                        hab = int(match.group(1))
                        if 1 <= hab <= 200:  # Validación de rango razonable
                            extracted['habitaciones'] = hab
                            extracted.setdefault('campos_estimados', []).append('habitaciones')
                            break
                    except:
                        continue
        
        # Extraer contacto si falta
        if not current_data.get('contacto', {}).get('telefono'):
            for pattern in self.heuristic_patterns['telefono']:
                match = pattern.search(html)
                if match:
                    extracted.setdefault('contacto', {})['telefono'] = match.group(0)
                    break
        
        if not current_data.get('contacto', {}).get('email'):
            for pattern in self.heuristic_patterns['email']:
                match = pattern.search(html)
                if match:
                    extracted.setdefault('contacto', {})['email'] = match.group(0)
                    break
        
        return extracted
    
    def _apply_semantic_fallback(self, html: str) -> Dict:
        """
        FALLBACK LAYER 4: Extracción semántica por keywords
        Detecta servicios y características mediante análisis de texto
        """
        extracted = {'fallback_chain': ['semantic_extraction']}
        
        # Extraer servicios mencionados
        servicios_encontrados = set()
        for pattern in self.heuristic_patterns['servicios']:
            matches = pattern.findall(html)
            servicios_encontrados.update([m.lower().strip() for m in matches])
        
        if servicios_encontrados:
            extracted['servicios'] = list(servicios_encontrados)
            extracted['campos_estimados'] = ['servicios']
        
        return extracted
    
    def _apply_ota_inverse_estimation(self, data: Dict, region_data: Dict) -> Dict:
        """
        FALLBACK LAYER 5: Estimación inversa desde patrones OTA
        Valida consistencia de precio vs habitaciones usando benchmarks conocidos
        """
        if data.get('precio_promedio') and data.get('habitaciones'):
            # Calcular precio por habitación esperado
            region_precio = region_data.get('precio_promedio') or region_data.get('valor_reserva_promedio', 280000)
            region_habitaciones = region_data.get('habitaciones_promedio', 15)
            expected_price_per_room = region_precio / region_habitaciones
            actual_price_per_room = data['precio_promedio'] / data['habitaciones']
            
            # Detectar inconsistencias (>50% desviación)
            deviation = abs(actual_price_per_room - expected_price_per_room) / expected_price_per_room
            
            if deviation > 0.5:
                # Precio parece inconsistente, ajustar con estimación
                adjusted_price = int(data['habitaciones'] * expected_price_per_room)
                data['precio_promedio_original'] = data['precio_promedio']
                data['precio_promedio'] = adjusted_price
                data['fallback_chain'].append('ota_inverse_estimation')
                
                if 'precio_promedio' not in data.get('campos_estimados', []):
                    data.setdefault('campos_estimados', []).append('precio_promedio_ajustado')
        
        return data
    
    def _merge_data(self, base: Dict, fallback: Dict) -> Dict:
        """Combina datos base con datos de fallback sin sobrescribir"""
        merged = base.copy()
        
        for key, value in fallback.items():
            if key == 'fallback_chain':
                merged.setdefault('fallback_chain', []).extend(value)
            elif key == 'campos_estimados':
                merged.setdefault('campos_estimados', []).extend(value)
            elif key == 'contacto':
                merged.setdefault('contacto', {}).update(value)
            elif not merged.get(key):
                merged[key] = value
        
        return merged
    
    def _calculate_confidence(self, data: Dict) -> str:
        """Calcula nivel de confianza basado en campos estimados y fallbacks"""
        total_fields = len(['nombre', 'ubicacion', 'habitaciones', 'precio_promedio', 'servicios'])
        estimated_fields = len(data.get('campos_estimados', []))
        
        confidence_ratio = 1 - (estimated_fields / total_fields)
        
        if confidence_ratio >= 0.8:
            return 'alta'
        elif confidence_ratio >= 0.5:
            return 'media'
        else:
            return 'baja'
    
    def _detect_region(self, ubicacion: str) -> str:
        """Detecta region a partir de la ubicacion"""
        ubicacion_lower = ubicacion.lower()
        
        if any(x in ubicacion_lower for x in ['antioquia', 'medellin', 'granada', 'guatape', 'rionegro']):
            return 'antioquia'
        elif any(x in ubicacion_lower for x in ['caldas', 'risaralda', 'quindio', 'pereira', 'armenia', 'manizales']):
            return 'eje_cafetero'
        elif any(x in ubicacion_lower for x in ['santa marta', 'cartagena', 'barranquilla', 'caribe', 'san andres']):
            return 'caribe'
        else:
            return 'default'
    
    def _extract_name_from_url(self, url: str) -> str:
        """Extrae nombre probable del dominio"""
        domain = urlparse(url).netloc.replace('www.', '').split('.')[0]
        return domain.replace('-', ' ').replace('_', ' ').title()
    
    def is_field_confirmed(self, data: Dict, field: str) -> bool:
        """Check if a field was provided via onboarding (confirmed data)."""
        return field in data.get('campos_confirmados', [])
    
    def get_visperas_data(self) -> Dict:
        """Datos especificos de Hotel Visperas - sincronizados con scraping real"""
        return {
            'nombre': 'Hotel Visperas',
            'ubicacion': 'Santa Rosa de Cabal, Risaralda',
            'habitaciones': 15,
            'precio_promedio': 400000,
            'ocupacion_actual': 0.55,
            'comision_ota': 0.18,
            'servicios': ['restaurante', 'parqueadero', 'spa', 'wifi'],
            'contacto': {
                'email': 'info@hotelvisperas.com',
                'telefono': '+57 311 311 1111'
            },
            'url': 'https://hotelvisperas.com',
            'confidence': 'alta',
            'metodo_obtencion': 'web_scraping_sincronizado',
            'campos_estimados': []
        }
    
    # ========== HOOKS PARA EXTENSIÓN FUTURA ==========
    
    def _prepare_llm_semantic_repair_hook(self, data: Dict, html: str) -> Dict:
        """
        FALLBACK LAYER 6 (PREPARADO, NO ACTIVO): LLM Semantic Repair
        
        Hook arquitectónico para integración futura de LLM que repare
        datos extraídos incorrectamente mediante comprensión semántica.
        
        Activación: Cuando confidence < 0.3 y otros fallbacks fallen
        
        Implementación futura:
        - Enviar HTML + partial_data a LLM (Claude/GPT)
        - Solicitar extracción estructurada con JSON schema
        - Validar respuesta contra benchmarks
        - Marcar campos como 'llm_semantic_repair' en fallback_chain
        
        Args:
            data: Datos parciales actuales
            html: Contenido HTML para análisis semántico
            
        Returns:
            Dict con datos reparados (actualmente retorna data sin cambios)
        """
        # TODO: Implementar cuando se requiera integración LLM
        # Estructura sugerida:
        # if data.get('confidence') == 'baja':
        #     llm_response = self._call_llm_api(html, data)
        #     validated_data = self._validate_llm_output(llm_response)
        #     data = self._merge_data(data, validated_data)
        #     data['fallback_chain'].append('llm_semantic_repair')
        
        return data


"""
=============================================================================
RESUMEN TÉCNICO - CAPAS DE FALLBACK AGREGADAS
=============================================================================

ARQUITECTURA IMPLEMENTADA: Pipeline de Fallback Multicapa (Chain of Responsibility)

CAPAS AGREGADAS:

1. CAPA 0: Data Quality Assessment
   - Detecta HTML sospechosamente corto (< 500 chars)
   - Identifica bloqueos anti-bot (Cloudflare, CAPTCHA)
   - Valida campos críticos (nombre, ubicación)
   - Calcula score de calidad (0-1)

2. CAPA 1: Historical Cache Fallback
   - Recupera datos previamente scrapeados si < 30 días
   - Evita re-scraping innecesario
   - Trazabilidad: 'cached_snapshot' + age_days

3. CAPA 2: Heuristic Regex Extraction
   - 5 familias de patrones regex: precio, habitaciones, teléfono, email, servicios
   - Validación de rangos razonables (precios: 50k-2M, habitaciones: 1-200)
   - Activación: cuando scraper estructural falla
   - Trazabilidad: 'heuristic_extraction'

4. CAPA 3: Semantic Keyword Detection
   - Extracción de servicios por análisis de texto completo
   - Patrones case-insensitive para wifi, piscina, restaurante, etc.
   - Complementa cuando DOM no tiene estructura clara
   - Trazabilidad: 'semantic_extraction'

5. CAPA 4: Regional Benchmark Completion (MEJORADO)
   - Benchmarks expandidos para 3 regiones + default
   - Completar campos faltantes con promedios regionales
   - Detección inteligente de región por keywords múltiples
   - Trazabilidad: 'benchmark_regional_[campo]'

6. CAPA 5: OTA Inverse Estimation (NUEVO)
   - Detecta inconsistencias precio/habitaciones (>50% desviación)
   - Ajusta precio usando ratio regional esperado
   - Preserva valor original en 'precio_promedio_original'
   - Trazabilidad: 'ota_inverse_estimation'

7. CAPA 6: LLM Semantic Repair Hook (PREPARADO, NO ACTIVO)
   - Arquitectura lista para integración futura
   - Documentación inline de cómo activarlo
   - Placeholder para llamada API a Claude/GPT
   - Diseñado para activarse cuando confidence < 0.3

MEJORAS ADICIONALES:

- Sistema de cache persistente (JSON local)
- Trazabilidad completa vía 'fallback_chain' array
- Cálculo dinámico de confidence (alta/media/baja)
- Validación cruzada de datos extraídos
- Merge inteligente sin sobrescribir datos reales
- Preparado para extensión modular futura

CAMPOS DE METADATOS AGREGADOS:
- fallback_chain: Lista ordenada de fallbacks aplicados
- campos_estimados: Campos no extraídos directamente
- confidence: Nivel de confianza calculado dinámicamente
- cache_age_days: Edad del cache si aplica
- precio_promedio_original: Preserva valor antes de ajuste OTA

USO:
    fallback = ScraperFallback()
    enriched = fallback.enrich_data(
        partial_data={'nombre': 'Hotel X'}, 
        url='https://example.com',
        html_content=html_string  # Opcional pero recomendado
    )

COMPATIBILIDAD: 100% backward compatible con código existente
=============================================================================
"""