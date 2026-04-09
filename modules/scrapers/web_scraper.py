import json
import re
import time
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import requests  # type: ignore[import-not-found]
from bs4 import BeautifulSoup  # type: ignore[import-not-found]

from modules.utils.http_client import get_default_client


class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.timeout = 15
        
        # Cliente HTTP con fallback SSL
        self.http_client = get_default_client()

        self.regiones_validas = {
            'eje_cafetero': ['armenia', 'pereira', 'manizales', 'salento', 'filandia', 'circasia'],
            'caribe': ['cartagena', 'santa marta', 'barú', 'rincón del mar', 'capurganá', 'san andrés'],
            'antioquia': ['guatapé', 'rionegro', 'el retiro', 'santa fe de antioquia', 'jardín']
        }
        self.benchmarks = {
            'eje_cafetero': {'min': 300000, 'max': 450000},
            'caribe': {'min': 380000, 'max': 750000},
            'antioquia': {'min': 250000, 'max': 400000}
        }
        self.revpar_minimos = {
            'eje_cafetero': 150000,
            'caribe': 247000,
            'antioquia': 150000
        }

    def extract_hotel_data(self, url):
        """
        Extraccion inteligente de datos del hotel
        Maneja: Schema.org, OpenGraph, HTML parsing
        Con fallback SSL para certificados expirados
        """
        try:
            # Usar HttpClient con fallback SSL
            response, fallback_info = self.http_client.get(url, headers=self.headers)
            
            if response is None:
                raise requests.RequestException(fallback_info.get('error', 'Request failed'))
            
            soup = BeautifulSoup(response.content, 'html.parser')

            precio_promedio = None

            try:
                price_selectors = [
                    '.price', '.precio', '[itemprop="price"]',
                    '.cost', '.rate', '.tarifa',
                    'meta[property="og:price:amount"]',
                    'meta[property="product:price:amount"]'
                ]

                for selector in price_selectors:
                    price_element = soup.select_one(selector)
                    if price_element:
                        precio_text = price_element.get_text().strip()
                        precio_promedio = self._parse_price(precio_text)
                        if precio_promedio:
                            break
            except Exception as e:
                print(f"⚠️  Error extrayendo precio: {e}")

            if precio_promedio is None:
                precio_result = self._extract_price(soup)
                if precio_result:
                    precio_promedio = precio_result['value']
                    precio_fuente = precio_result['source']
                    precio_confianza = precio_result['confidence']
                    precio_raw = precio_result.get('raw')
                else:
                    precio_promedio = None
                    precio_fuente = None
                    precio_confianza = None
                    precio_raw = None
            else:
                # Precio extraído de meta tags
                precio_fuente = 'meta_tag'
                precio_confianza = 'MEDIA'
                precio_raw = None

            data = {
                'url': url,
                'nombre': self._extract_name(soup, url),
                'ubicacion': self._extract_location(soup),
                'habitaciones': self._extract_rooms(soup),
                'precio_promedio': precio_promedio,
                'precio_fuente': precio_fuente,
                'precio_confianza': precio_confianza,
                'precio_raw': precio_raw,
                'servicios': self._extract_services(soup),
                'contacto': self._extract_contact(soup, response.text),
                'descripcion': self._extract_description(soup),
                'schema_data': self._extract_schema(soup),
                'confidence': self._calculate_confidence(soup),
                'metodo_obtencion': 'web_scraping_avanzado',
                'ssl_fallback_info': fallback_info  # Trazabilidad SSL
            }
            
            # Aplicar penalización SEO si SSL fue bypasseado
            if fallback_info.get('ssl_bypassed'):
                data['ssl_warning'] = 'Certificado SSL expirado o inválido'
                data['seo_penalty_applied'] = fallback_info.get('seo_penalty', 0)

            data['brechas_detectadas'] = self._auditoria_invisibilidad_ia(
                soup, data, response.text
            )
            data['score_visibilidad_ia'] = self._calcular_score_visibilidad(
                data['brechas_detectadas']
            )
            
            # Detectar CMS para guías de instalación específicas
            data['cms_detected'] = self._detectar_cms(soup, response.text)
            
            # Extraer URL del motor de reservas externo (LobbyPMS, Cloudbeds, etc.)
            motor_info = self._extraer_motor_reservas_url(soup, response.text)
            if motor_info['detected']:
                data['motor_reservas_url'] = motor_info['url']
                data['motor_reservas_nombre'] = motor_info['engine_name']
                data['motor_reservas_tipo'] = motor_info['engine_type']

            return data

        except Exception as e:
            print(f"[WARN]  Error en scraping: {e}")
            return {
                'url': url,
                'confidence': 'low',
                'error': str(e),
                'metodo_obtencion': 'fallback_requerido',
                'brechas_detectadas': [{
                    'tipo': 'ACCESO_WEB',
                    'severidad': 'CRITICA',
                    'detalle': f'No se pudo acceder al sitio web: {str(e)}',
                    'impacto_estimado': 'Pérdida total de visibilidad online - hotel invisible para todos los canales digitales'
                }]
            }

    def _auditoria_invisibilidad_ia(self, soup, data, html_text):
        brechas = []

        schema_data = data.get('schema_data', [])
        tiene_schema = len(schema_data) > 0

        if not tiene_schema:
            brechas.append({
                'tipo': 'SCHEMA_AUSENTE',
                'severidad': 'CRITICA',
                'detalle': 'No existe Schema.org → ChatGPT, Perplexity y Google Gemini no pueden "leer" este hotel',
                'impacto_estimado': '≈2.1M COP/mes en reservas directas perdidas (Plan Maestro, sec. 1.1)',
                'prioridad': 1,
                'solucion_rapida': 'Pilar 2: Implementar JSON-LD con @type:LodgingBusiness en <30 días'
            })
        else:
            schema_completo = self._validar_schema_hotel(schema_data)
            if not schema_completo['es_tipo_hotel']:
                brechas.append({
                    'tipo': 'SCHEMA_INCOMPLETO',
                    'severidad': 'ALTA',
                    'detalle': 'Schema presente pero sin @type:LodgingBusiness → los agentes IA no lo clasifican con precisión técnica (v3.3)',
                    'impacto_estimado': '≈1.5M COP/mes - hotel clasificado como "negocio genérico"',
                    'prioridad': 2,
                    'solucion_rapida': 'Migrar a @type:LodgingBusiness para mayor autoridad semántica'
                })

            if not schema_completo['tiene_direccion']:
                brechas.append({
                    'tipo': 'GEOLOCALIZACION',
                    'severidad': 'CRITICA',
                    'detalle': 'Schema sin addressLocality/addressRegion → invisible en búsquedas "cerca de mí" (65% del tráfico móvil)',
                    'impacto_estimado': '≈1.8M COP/mes - pérdida de búsquedas por proximidad',
                    'prioridad': 1,
                    'solucion_rapida': 'Pilar 1: Completar address en schema + optimizar GBP'
                })

        ubicacion = data.get('ubicacion', '').lower()
        if ubicacion == 'ubicacion no detectada' or 'colombia' in ubicacion or ubicacion == '':
            brechas.append({
                'tipo': 'UBICACION_AMBIGUA',
                'severidad': 'CRITICA',
                'detalle': f'Ubicación detectada: "{ubicacion}" → demasiado genérica para rankear localmente',
                'impacto_estimado': '≈1.4M COP/mes - pérdida de tráfico "hotel en [ciudad]"',
                'prioridad': 1,
                'solucion_rapida': 'Declarar ciudad específica en <address> y meta tags'
            })
        else:
            es_especifica = self._validar_ubicacion_especifica(ubicacion)
            if not es_especifica:
                brechas.append({
                    'tipo': 'UBICACION_VAGA',
                    'severidad': 'MEDIA',
                    'detalle': f'Ubicación "{ubicacion}" es vaga → baja prioridad en IA',
                    'impacto_estimado': '≈800K COP/mes - menor relevancia en recomendaciones contextuales',
                    'prioridad': 3,
                    'solucion_rapida': 'Especificar municipio exacto (ej: "Manizales, Caldas")'
                })

        precio = data.get('precio_promedio')
        if precio is None:
            brechas.append({
                'tipo': 'PRECIO_AUSENTE',
                'severidad': 'ALTA',
                'detalle': 'Sin precio estructurado → ChatGPT no puede comparar ni recomendar por presupuesto',
                'impacto_estimado': '≈1.2M COP/mes - exclusión de filtros por precio en agentes IA',
                'prioridad': 2,
                'solucion_rapida': 'Agregar priceRange en schema + precio visible en homepage'
            })
        else:
            region_detectada = self._detectar_region(ubicacion)
            ocupacion = data.get('ocupacion')
            alerta_precio = self._validar_precio_regional(precio, region_detectada, ocupacion)
            if alerta_precio['tipo'] != 'PRECIO_VALIDO':
                brechas.append(alerta_precio)

        if not self._detectar_whatsapp(soup, html_text):
            brechas.append({
                'tipo': 'WHATSAPP_AUSENTE',
                'severidad': 'ALTA',
                'detalle': 'No hay enlace WhatsApp directo → pérdida de 30% de conversión móvil (dato validado F4)',
                'impacto_estimado': '≈900K COP/mes - consultas perdidas por fricción de contacto',
                'prioridad': 2,
                'solucion_rapida': 'Pilar 1: Activar WhatsApp Business + botón wa.me'
            })

        if self._detectar_contenido_generico(soup):
            brechas.append({
                'tipo': 'CONTENIDO_GENERICO',
                'severidad': 'MEDIA',
                'detalle': 'Contenido repetitivo detectado → IA lo deprioritiza',
                'impacto_estimado': '≈600K COP/mes - baja en ranking de respuestas directas (AEO)',
                'prioridad': 3,
                'solucion_rapida': 'Pilar 2: Crear 5 FAQs específicas'
            })

        senales_ia = self._detectar_senales_ia_friendly(soup, data)
        if not senales_ia['tiene_faq']:
            brechas.append({
                'tipo': 'FAQ_AUSENTE',
                'severidad': 'ALTA',
                'detalle': 'Sin FAQPage schema → invisible para Google Answer Boxes',
                'impacto_estimado': '≈1.1M COP/mes - pérdida de tráfico AEO',
                'prioridad': 2,
                'solucion_rapida': 'Pilar 2: Implementar FAQPage schema con 10 preguntas'
            })

        if not senales_ia['tiene_json_ld_completo']:
            brechas.append({
                'tipo': 'DATOS_NO_ESTRUCTURADOS',
                'severidad': 'ALTA',
                'detalle': 'Datos en HTML plano sin JSON-LD → agentes IA no confían',
                'impacto_estimado': '≈1.6M COP/mes - exclusión en ChatGPT/Perplexity',
                'prioridad': 1,
                'solucion_rapida': 'Pilar 2: Crear mini-ficha JSON (15 atributos clave)'
            })

        # v2.6.5: Detección mejorada de motor de reservas
        # Distingue entre: (1) No existe, (2) Existe pero no prominente
        motor_info = self._extraer_motor_reservas_url(soup, html_text)
        motor_detectado_binario = self._detectar_motor_reservas(soup, html_text)
        
        if not motor_detectado_binario:
            if motor_info['detected']:
                # Motor existe pero no es prominente (requiere navegación)
                brechas.append({
                    'tipo': 'MOTOR_RESERVAS_NO_PROMINENTE',
                    'severidad': 'ALTA',
                    'detalle': f"Motor de reservas ({motor_info['engine_name']}) detectado pero no es fácilmente identificable. Requiere 3-4 clics, mientras OTAs convierten en 1 clic.",
                    'impacto_estimado': '≈3.2M COP/mes - abandono por fricción de navegación',
                    'prioridad': 1,
                    'solucion_rapida': f"Agregar botón 'Reservar Ahora' visible con enlace directo a {motor_info['engine_name']}. Activar CTA de WhatsApp como alternativa.",
                    'motor_detectado': motor_info['engine_name'],
                    'motor_url': motor_info['url']
                })
            else:
                # Motor realmente no existe
                brechas.append({
                    'tipo': 'SIN_MOTOR_RESERVAS',
                    'severidad': 'CRITICA',
                    'detalle': 'No se detecta motor de reservas directo → dependencia 100% de OTAs',
                    'impacto_estimado': '≈3.2M COP/mes - margen reducido 20-30%',
                    'prioridad': 1,
                    'solucion_rapida': 'Habilitar flujo de reserva/contacto medible (WhatsApp + CTA). Si se requiere motor de reservas, se recomienda proveedor'
                })

        return brechas

    def _validar_schema_hotel(self, schema_data):
        resultado = {
            'es_tipo_hotel': False,
            'tiene_direccion': False,
            'tiene_precio': False
        }

        for schema in schema_data:
            schema_type = schema.get('@type', '').lower() if isinstance(schema.get('@type'), str) else ''
            if 'hotel' in schema_type or 'lodging' in schema_type or 'resort' in schema_type:
                resultado['es_tipo_hotel'] = True

            if 'address' in schema:
                addr = schema['address']
                if isinstance(addr, dict):
                    if addr.get('addressLocality') and addr.get('addressRegion'):
                        resultado['tiene_direccion'] = True

            if 'priceRange' in schema or 'offers' in schema:
                resultado['tiene_precio'] = True

        return resultado

    def _validar_ubicacion_especifica(self, ubicacion):
        ubicacion_lower = ubicacion.lower()

        for region, ciudades in self.regiones_validas.items():
            for ciudad in ciudades:
                if ciudad in ubicacion_lower:
                    return True

        if ',' in ubicacion and len(ubicacion) > 10:
            return True

        return False

    def _detectar_region(self, ubicacion: str) -> str:
        ubicacion_lower = ubicacion.lower()

        for region, municipios in self.regiones_validas.items():
            for municipio in municipios:
                if municipio in ubicacion_lower:
                    return region

        if any(keyword in ubicacion_lower for keyword in ['eje cafetero', 'quindío', 'risaralda', 'caldas']):
            return 'eje_cafetero'
        if any(keyword in ubicacion_lower for keyword in ['caribe', 'bolívar', 'magdalena', 'san andrés']):
            return 'caribe'
        if any(keyword in ubicacion_lower for keyword in ['antioquia', 'guatapé', 'medellín']):
            return 'antioquia'

        return 'desconocida'

    def _calcular_revpar(self, precio: int, ocupacion: Optional[float]) -> int:
        if ocupacion is None:
            return 0
        return int(precio * (ocupacion / 100))

    def _validar_precio_regional(self, precio: int, region: str, ocupacion: Optional[float] = None) -> Dict[str, Any]:
        if region not in self.benchmarks:
            return {'tipo': 'REGION_NO_RECONOCIDA', 'severidad': 'MEDIA'}

        min_aceptable = self.benchmarks[region]['min']
        max_aceptable = self.benchmarks[region]['max']

        if precio < min_aceptable:
            return {
                'tipo': 'ADR_BAJO',
                'severidad': 'ALTA',
                'detalle': f'ADR {precio:,} COP por debajo del mínimo sostenible ({min_aceptable:,} COP)',
                'impacto_estimado': f'RevPAR potencial < {self.revpar_minimos[region]:,} COP',
                'prioridad': 1
            }

        if ocupacion is not None:
            revpar = self._calcular_revpar(precio, ocupacion)
            if revpar < self.revpar_minimos[region]:
                return {
                    'tipo': 'REVPAR_INSOSTENIBLE',
                    'severidad': 'CRITICA',
                    'detalle': f'RevPAR {revpar:,} COP por debajo del mínimo sostenible ({self.revpar_minimos[region]:,} COP)',
                    'impacto_estimado': 'Modelo boutique inviable según Benchmarking.md',
                    'prioridad': 1
                }

        if region == 'eje_cafetero' and ocupacion is not None:
            if ocupacion > 55 and precio < 300000:
                return {
                    'tipo': 'MODELO_INVIABLE_EJE_CAFETERO',
                    'severidad': 'CRITICA',
                    'detalle': f'ADR {precio:,} COP + ocupación {ocupacion}% → RevPAR < 150 k COP',
                    'impacto_estimado': '≈2.3 M COP/mes - modelo boutique inviable',
                    'prioridad': 1
                }

        return {'tipo': 'PRECIO_VALIDO', 'severidad': 'BAJA'}

    def _detectar_whatsapp(self, soup, html_text):
        whatsapp_patterns = [
            # Direct WhatsApp links
            r'wa\.me',
            r'api\.whatsapp\.com',
            r'whatsapp://send',
            r'web\.whatsapp\.com',
            # WordPress WhatsApp plugins (top 3: 1M+ combined installs)
            r'joinchat',                      # Joinchat/creame-whatsapp-me (500K+)
            r'creame-whatsapp-me',           # Plugin path variant
            r'ht-ctc',                        # Click to Chat for WhatsApp (200K+)
            r'click-to-chat',                 # Click to Chat variant
            r'wa-chat',                       # WA Chat widgets
            r'data-settings.*telephone',      # Joinchat stores number in data-settings JSON
        ]

        for pattern in whatsapp_patterns:
            if re.search(pattern, html_text, re.IGNORECASE):
                return True

        if soup.find(string=re.compile(r'whatsapp|contactar por whatsapp', re.IGNORECASE)):
            return True

        return False

    def _detectar_contenido_generico(self, soup):
        texto_completo = soup.get_text().lower()

        frases_genericas = [
            'mejor hotel',
            'excelente ubicación',
            'servicio de calidad',
            'atención personalizada',
            'el mejor de colombia',
            'experiencia única',
            'confort y elegancia'
        ]

        contador = sum(1 for frase in frases_genericas if frase in texto_completo)
        return contador >= 3

    def _detectar_senales_ia_friendly(self, soup, data):
        senales = {
            'tiene_faq': False,
            'tiene_json_ld_completo': False,
            'tiene_microdatos': False
        }

        for schema in data.get('schema_data', []):
            schema_type = schema.get('@type', '')
            if isinstance(schema_type, str) and 'faq' in schema_type.lower():
                senales['tiene_faq'] = True

            if len(schema.keys()) >= 10:
                senales['tiene_json_ld_completo'] = True

        if soup.find(attrs={'itemscope': True}):
            senales['tiene_microdatos'] = True

        return senales

    def _detectar_motor_reservas(self, soup, html_text: str) -> bool:
        """
        Detector v2.0: Motor de reservas con filtro anti-landing-proveedores.
        
        Flujo de 3 capas:
        1. CAPA 0: ¿Es landing de proveedor SaaS? → Rechazar inmediato
        2. CAPAS 1-8: Detección multi-señal normal
        3. CAPA 9: Validación contextual final
        
        Returns:
            bool: True si hotel tiene motor de reservas directo
        """
        
        # ════════════════════════════════════════════════════════════
        # CAPA 0: PRE-FILTRO ANTI-PROVEEDOR
        # ════════════════════════════════════════════════════════════
        if self._es_landing_proveedor_saas(soup, html_text):
            return False  # Rechazo inmediato
        
        # ════════════════════════════════════════════════════════════
        # CAPAS 1-8: DETECCIÓN MULTI-SEÑAL
        # ════════════════════════════════════════════════════════════
        score = 0
        
        # CAPA 1: iframes (50-35 puntos)
        motores_tier1 = [
            'cloudbeds.com', 'sirvoy', 'hotelogix', 'beds24',
            'myallocator', 'siteminder', 'littlehotelier', 'lobbypms.com'
        ]
        
        for iframe in soup.find_all('iframe', src=True):
            src = iframe.get('src', '').lower()
            if any(m in src for m in motores_tier1):
                # Verificar que sea un motor embebido, no un video/demo
                if '/booking' in src or '/reserva' in src or '/widget' in src:
                    score += 50  # Auto-pass para motores Tier-1 confirmados
                    break
        
        # CAPA 2: Scripts externos (35-25 puntos)
        if score < 50:
            for script in soup.find_all('script', src=True):
                src = script.get('src', '').lower()
                if any(m in src for m in motores_tier1):
                    score += 35
                    break
                if any(kw in src for kw in ['booking', 'reservation', 'calendar.js']):
                    score += 25
                    break
        
        # CAPA 3: Formularios inteligentes (35-20 puntos)
        for form in soup.find_all('form'):
            campos = ' '.join(
                inp.get('name', '').lower() + inp.get('id', '').lower() + inp.get('placeholder', '').lower()
                for inp in form.find_all(['input', 'select'])
            )
            
            tiene_checkin = any(kw in campos for kw in ['checkin', 'check-in', 'arrival'])
            tiene_checkout = any(kw in campos for kw in ['checkout', 'check-out', 'departure'])
            
            if tiene_checkin and tiene_checkout:
                texto_form = form.get_text().lower()
                # Filtrar formularios de demo/prueba
                if not any(kw in texto_form for kw in ['demo', 'prueba gratis', 'trial']):
                    score += 35
                    break
        
        # CAPA 4: Enlaces a endpoints (28 puntos)
        endpoints = ['/reserva', '/booking', '/disponibilidad', '/availability']
        otas = ['booking.com', 'expedia', 'airbnb', 'hotels.com']
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            if any(ep in href for ep in endpoints):
                # Descartar auto-referencias y popups
                if not ('#' in href or href.endswith('/motor-de-reservas/')):
                    if not any(ota in href for ota in otas):
                        score += 28
                        break
        
        # CAPA 4.5: Texto de anclaje "Reservar Ahora" (22 puntos)
        # v2.6.6: Heurística expandida - detecta CTAs por texto, no solo URL/clases
        booking_texts = ['reservar ahora', 'reservar', 'book now', 'reserva directa', 'mejor tarifa']
        for link in soup.find_all('a', href=True):
            link_text = link.get_text().lower().strip()
            if any(bt in link_text for bt in booking_texts):
                href = link.get('href', '').lower()
                # Verificar que no sea OTA
                if not any(ota in href for ota in otas):
                    score += 22
                    break
        
        # CAPA 5: Data-attributes (25 puntos)
        # v2.6.6: Incluye data-iah-* para certificacion de activos propios
        if (soup.find(attrs={'data-booking': True}) or 
            soup.find(attrs={'data-reservation': True}) or
            soup.find(attrs={'data-iah-booking': True})):
            score += 25
        
        # CAPA 6: Clases CSS (20 puntos)
        if soup.select('.booking-form, .reservation-widget, .availability-calendar'):
            score += 20
        
        # CAPA 7: JSON-LD ReserveAction (30 puntos)
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    action = data.get('potentialAction', {})
                    if isinstance(action, dict) and action.get('@type') == 'ReserveAction':
                        score += 30
                        break
            except:
                pass
        
        # ════════════════════════════════════════════════════════════
        # CAPA 9: VALIDACIÓN CONTEXTUAL FINAL
        # ════════════════════════════════════════════════════════════
        
        # Penalización si mayoría de enlaces van a OTAs
        enlaces = soup.find_all('a', href=True)
        if len(enlaces) > 5:
            links_ota = sum(1 for a in enlaces if any(
                ota in a.get('href', '').lower() for ota in otas
            ))
            ratio_ota = links_ota / len(enlaces)
            
            if ratio_ota > 0.6:
                score -= 15
        
        # ════════════════════════════════════════════════════════════
        # DECISIÓN FINAL
        # ════════════════════════════════════════════════════════════
        umbral = 50
        return score >= umbral

    def _extraer_motor_reservas_url(self, soup, html_text: str) -> Dict[str, Any]:
        """
        Extrae la URL del motor de reservas externo si existe.
        
        Busca enlaces a motores conocidos (LobbyPMS, Cloudbeds, etc.) en:
        - Enlaces <a href>
        - Iframes <iframe src>
        - Botones con data-href
        
        Returns:
            Dict con 'detected', 'url', 'engine_name', 'engine_type'
        """
        result = {
            'detected': False,
            'url': None,
            'engine_name': None,
            'engine_type': None
        }
        
        # Motores conocidos con patrones de URL
        motores_conocidos = {
            'lobbypms': {
                'pattern': 'engine.lobbypms.com',
                'name': 'LobbyPMS',
            },
            'cloudbeds': {
                'pattern': 'hotels.cloudbeds.com',
                'name': 'Cloudbeds',
            },
            'sirvoy': {
                'pattern': 'sirvoy.com',
                'name': 'Sirvoy',
            },
            'beds24': {
                'pattern': 'beds24.com',
                'name': 'Beds24',
            },
            'littlehotelier': {
                'pattern': 'littlehotelier.com',
                'name': 'Little Hotelier',
            },
            'siteminder': {
                'pattern': 'siteminder.com',
                'name': 'SiteMinder',
            },
        }
        
        # Buscar en enlaces <a href>
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            for engine_key, engine_info in motores_conocidos.items():
                if engine_info['pattern'] in href:
                    result['detected'] = True
                    result['url'] = link.get('href')  # URL original (sin lower)
                    result['engine_name'] = engine_info['name']
                    result['engine_type'] = engine_key
                    return result
        
        # Buscar en iframes
        for iframe in soup.find_all('iframe', src=True):
            src = iframe.get('src', '').lower()
            for engine_key, engine_info in motores_conocidos.items():
                if engine_info['pattern'] in src:
                    result['detected'] = True
                    result['url'] = iframe.get('src')
                    result['engine_name'] = engine_info['name']
                    result['engine_type'] = engine_key
                    return result
        
        # Buscar en HTML plano (casos donde el link está en texto)
        for engine_key, engine_info in motores_conocidos.items():
            pattern = engine_info['pattern']
            if pattern in html_text.lower():
                # Intentar extraer URL completa con regex
                import re
                url_pattern = rf'https?://[^\s"\'<>]*{re.escape(pattern)}[^\s"\'<>]*'
                match = re.search(url_pattern, html_text, re.IGNORECASE)
                if match:
                    result['detected'] = True
                    result['url'] = match.group(0)
                    result['engine_name'] = engine_info['name']
                    result['engine_type'] = engine_key
                    return result
        
        return result

    def _es_landing_proveedor_saas(self, soup, html_text: str) -> bool:
        """
        Filtro rápido: ¿Es una landing page de proveedor de software?
        
        Casos típicos:
        - lobbypms.com/motor-de-reservas/
        - cloudbeds.com/features/booking-engine/
        - sirvoy.com/es/motor-reservas/
        
        Returns:
            bool: True si es landing de proveedor
        """
        score = 0
        
        # SEÑAL 1: Title con keywords de proveedor
        title = soup.find('title')
        if title:
            title_text = title.get_text().lower()
            if any(kw in title_text for kw in [
                'software para hoteles', 'sistema de gestión', 'pms',
                'motor de reservas para', 'booking engine for'
            ]):
                score += 20
        
        # SEÑAL 2: CTAs de SaaS (3+ ocurrencias)
        texto_body = soup.get_text().lower()
        ctas_saas = [
            'prueba gratis', 'free trial', 'solicitar demo', 'request demo',
            'contratar ahora', 'ver planes', 'pricing'
        ]
        matches_cta = sum(1 for cta in ctas_saas if cta in texto_body)
        
        if matches_cta >= 3:
            score += 25
        
        # SEÑAL 3: Formularios con "nombre_establecimiento" o "company"
        for form in soup.find_all('form'):
            campos = ' '.join(inp.get('name', '').lower() for inp in form.find_all(['input', 'select']))
            if 'nombre_establecimiento' in campos or 'company' in campos:
                score += 20
                break
        
        # SEÑAL 4: Navegación corporativa
        menu_items = [link.get_text().lower() for link in soup.find_all('a')]
        secciones_corp = ['precios', 'pricing', 'clientes', 'features', 'integraciones']
        matches_menu = sum(1 for sec in secciones_corp if any(sec in item for item in menu_items))
        
        if matches_menu >= 3:
            score += 20
        
        # SEÑAL 5: NO tiene Schema.org de Hotel
        tiene_schema_hotel = False
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                schema_type = data.get('@type', '').lower() if isinstance(data, dict) else ''
                if 'hotel' in schema_type or 'lodging' in schema_type:
                    tiene_schema_hotel = True
                    break
            except:
                pass
        
        if not tiene_schema_hotel and score >= 30:
            score += 15
        
        # Umbral: 50+ puntos = landing de proveedor
        return score >= 50

    def _detectar_cms(self, soup, html_text: str) -> Dict[str, Any]:
        """
        Detecta el CMS del sitio web para guías de instalación específicas.
        
        Heurísticas priorizadas:
        1. WordPress: /wp-content/, meta generator, /wp-json/
        2. Wix: scripts/hosts típicos
        3. Squarespace: scripts y data-attributes
        4. Unknown: fallback a guía genérica
        
        Returns:
            Dict con 'cms', 'confidence', 'signals'
        """
        result = {
            'cms': 'unknown',
            'confidence': 'low',
            'signals': []
        }
        
        html_lower = html_text.lower()
        
        # ═══════════════════════════════════════════════════════════════
        # WORDPRESS (Más común ~60% de la web)
        # ═══════════════════════════════════════════════════════════════
        wp_score = 0
        
        # Señal 1: /wp-content/ en recursos (muy confiable)
        if '/wp-content/' in html_lower or '/wp-includes/' in html_lower:
            wp_score += 40
            result['signals'].append('wp-content directory detected')
        
        # Señal 2: Meta generator
        meta_gen = soup.find('meta', attrs={'name': 'generator'})
        if meta_gen and 'wordpress' in meta_gen.get('content', '').lower():
            wp_score += 35
            result['signals'].append('WordPress meta generator')
        
        # Señal 3: wp-json API endpoint
        for link in soup.find_all('link', rel='https://api.w.org/'):
            wp_score += 25
            result['signals'].append('WordPress REST API link')
            break
        
        # Señal 4: Clases CSS típicas de WP
        if soup.find(class_=lambda x: x and ('wp-' in x or 'wordpress' in x)):
            wp_score += 15
            result['signals'].append('WordPress CSS classes')
        
        if wp_score >= 40:
            result['cms'] = 'wordpress'
            result['confidence'] = 'high' if wp_score >= 60 else 'medium'
            return result
        
        # ═══════════════════════════════════════════════════════════════
        # WIX
        # ═══════════════════════════════════════════════════════════════
        wix_score = 0
        
        # Señal 1: Scripts de Wix
        if 'static.wixstatic.com' in html_lower or 'wix.com' in html_lower:
            wix_score += 45
            result['signals'].append('Wix static resources')
        
        # Señal 2: Meta Wix
        if soup.find('meta', attrs={'name': 'generator', 'content': lambda x: x and 'wix' in x.lower()}):
            wix_score += 40
            result['signals'].append('Wix meta generator')
        
        # Señal 3: Data attributes de Wix
        if soup.find(attrs={'data-mesh-id': True}) or 'wixui' in html_lower:
            wix_score += 30
            result['signals'].append('Wix data attributes')
        
        if wix_score >= 40:
            result['cms'] = 'wix'
            result['confidence'] = 'high' if wix_score >= 60 else 'medium'
            return result
        
        # ═══════════════════════════════════════════════════════════════
        # SQUARESPACE
        # ═══════════════════════════════════════════════════════════════
        sq_score = 0
        
        if 'squarespace.com' in html_lower or 'static1.squarespace.com' in html_lower:
            sq_score += 45
            result['signals'].append('Squarespace resources')
        
        if soup.find(attrs={'data-squarespace-cacheversion': True}):
            sq_score += 35
            result['signals'].append('Squarespace cache attribute')
        
        if sq_score >= 40:
            result['cms'] = 'squarespace'
            result['confidence'] = 'high' if sq_score >= 60 else 'medium'
            return result
        
        # ═══════════════════════════════════════════════════════════════
        # OTHER KNOWN PLATFORMS
        # ═══════════════════════════════════════════════════════════════
        
        # Shopify
        if 'cdn.shopify.com' in html_lower or 'shopify' in html_lower:
            result['cms'] = 'shopify'
            result['confidence'] = 'medium'
            result['signals'].append('Shopify resources')
            return result
        
        # Webflow
        if 'webflow.com' in html_lower or soup.find(attrs={'data-wf-site': True}):
            result['cms'] = 'webflow'
            result['confidence'] = 'medium'
            result['signals'].append('Webflow resources')
            return result
        
        # ═══════════════════════════════════════════════════════════════
        # UNKNOWN - Fallback
        # ═══════════════════════════════════════════════════════════════
        result['signals'].append('No known CMS detected')
        return result

    def _calcular_score_visibilidad(self, brechas):
        if not brechas:
            return 100

        penalizaciones = {
            'CRITICA': 20,
            'ALTA': 12,
            'MEDIA': 6,
            'BAJA': 3
        }

        score = 100
        for brecha in brechas:
            severidad = brecha.get('severidad', 'MEDIA')
            score -= penalizaciones.get(severidad, 6)

        return max(0, score)

    def generar_reporte_ejecutivo(self, data):
        brechas = data.get('brechas_detectadas', [])
        score = data.get('score_visibilidad_ia', 0)

        criticas = [b for b in brechas if b['severidad'] == 'CRITICA']
        altas = [b for b in brechas if b['severidad'] == 'ALTA']
        medias = [b for b in brechas if b['severidad'] == 'MEDIA']

        perdida_total = 0
        for brecha in brechas:
            impacto_str = brecha.get('impacto_estimado', '')
            match = re.search(r'([\d,.]+)\s*[MK]?\s*COP', impacto_str)
            if match:
                valor = match.group(1).replace(',', '').replace('.', '')
                if 'M' in impacto_str or 'm' in impacto_str:
                    perdida_total += float(valor)
                elif 'K' in impacto_str or 'k' in impacto_str:
                    perdida_total += float(valor) / 1000

        reporte = {
            'hotel': data.get('nombre', 'Hotel sin nombre'),
            'url': data.get('url', ''),
            'fecha_auditoria': time.strftime('%Y-%m-%d'),
            'diagnostico_general': self._generar_diagnostico(score),
            'score_visibilidad_ia': score,
            'perdida_mensual_estimada': f'{perdida_total:.1f}M COP',
            'perdida_anual_estimada': f'{perdida_total * 12:.1f}M COP',
            'resumen_ejecutivo': {
                'total_brechas': len(brechas),
                'criticas': len(criticas),
                'altas': len(altas),
                'medias': len(medias)
            },
            'brechas_criticas': criticas[:3],
            'acciones_inmediatas': self._generar_acciones_inmediatas(brechas),
            'roi_estimado_90_dias': self._calcular_roi_estimado(perdida_total),
            'tiempo_implementacion': '30-90 días (Plan 2-Pilares)',
            'cta': 'Solicita tu diagnóstico completo 2-Pilares en 15 min'
        }

        return reporte

    def _generar_diagnostico(self, score):
        if score >= 80:
            return "✅ BUENO: Tu hotel tiene visibilidad IA sólida."
        if score >= 60:
            return "⚠️ REGULAR: Tu hotel pierde reservas por brechas detectables."
        if score >= 40:
            return "🚨 CRÍTICO: Tu hotel es invisible para ChatGPT y Perplexity."
        return "❌ INVISIBLE: Tu hotel no existe para los agentes IA."

    def _generar_acciones_inmediatas(self, brechas):
        brechas_ordenadas = sorted(brechas, key=lambda x: x.get('prioridad', 99))

        acciones = []
        for i, brecha in enumerate(brechas_ordenadas[:5], 1):
            acciones.append({
                'orden': i,
                'accion': brecha.get('solucion_rapida', 'Contactar a IA Hoteles Agent'),
                'impacto': brecha.get('impacto_estimado', ''),
                'plazo': '7-30 días' if brecha['severidad'] == 'CRITICA' else '30-60 días'
            })

        return acciones

    def _calcular_roi_estimado(self, perdida_mensual):
        inversion_promedio = 3.8
        recuperacion_estimada = perdida_mensual * 0.60
        roi = (recuperacion_estimada * 3) / inversion_promedio if inversion_promedio else 0

        return {
            'inversion': f'{inversion_promedio}M COP',
            'recuperacion_90_dias': f'{recuperacion_estimada * 3:.1f}M COP',
            'roi_multiplicador': f'{roi:.1f}X',
            'punto_equilibrio': f'{int(30 / roi) if roi > 0 else 90} días'
        }

    def _extract_name(self, soup, url):
        schema = soup.find('script', type='application/ld+json')
        if schema:
            try:
                data = json.loads(schema.string)
                if 'name' in data:
                    return data['name']
            except Exception:
                pass

        og_title = soup.find('meta', property='og:title')
        if og_title:
            return og_title.get('content', '').split('|')[0].strip()

        title = soup.find('title')
        if title:
            return title.text.split('|')[0].strip()

        h1 = soup.find('h1')
        if h1:
            return h1.text.strip()

        domain = urlparse(url).netloc.replace('www.', '').split('.')[0]
        return domain.title()

    def _extract_location(self, soup):
        schema = soup.find('script', type='application/ld+json')
        if schema:
            try:
                data = json.loads(schema.string)
                if 'address' in data:
                    addr = data['address']
                    if isinstance(addr, dict):
                        city = addr.get('addressLocality', '')
                        region = addr.get('addressRegion', '')
                        return f"{city}, {region}".strip(', ')
            except Exception:
                pass

        location_patterns = [
            r'ubicado en ([^\.]+)',
            r'located in ([^\.]+)',
            r'([A-Z][a-zá-ú]+,\s*[A-Z][a-zá-ú]+)'
        ]

        text = soup.get_text()
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        return "Ubicacion no detectada"

    def _extract_rooms(self, soup):
        patterns = [
            r'(\d+)\s*habitaciones?',
            r'(\d+)\s*rooms?',
            r'(\d+)\s*suites?'
        ]

        text = soup.get_text().lower()
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))

        return None

    def _extract_price(self, soup):
        schema = soup.find('script', type='application/ld+json')
        if schema:
            try:
                data = json.loads(schema.string)
                if 'priceRange' in data:
                    price_estimate = self._parse_price(data['priceRange'])
                    if price_estimate:
                        return {
                            'value': price_estimate,
                            'source': 'schema',
                            'confidence': 'HIGH',
                            'raw': data['priceRange']
                        }
            except Exception:
                pass

        price_patterns = [
            r'\$?\s*(\d{1,3}[,.]?\d{3})\s*COP',
            r'desde\s*\$?\s*(\d{1,3}[,.]?\d{3})',
            r'precio.*\$?\s*(\d{1,3}[,.]?\d{3})'
        ]

        text = soup.get_text()
        for pattern in price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price_estimate = self._parse_price(match.group(1))
                if price_estimate:
                    return {
                        'value': price_estimate,
                        'source': 'regex_pattern',
                        'confidence': 'MEDIUM',
                        'raw': match.group(0)
                    }

        return None

    def _parse_price(self, price_text):
        """
        Limpia y extrae valor numérico de un texto de precio.
        v3.3.1: Corregido bug de concatenación de rangos (ej: $280k-$520k).
        """
        if price_text is None:
            return None
        if isinstance(price_text, (int, float)):
            return int(price_text)
            
        # Detectar múltiples números grandes (posibles rangos)
        # Busca grupos de 4+ dígitos o números con formato (1.000, 1,000)
        numbers = re.findall(r'(\d{1,3}(?:[.,]\d{3})+|\d{4,})', str(price_text))
        
        if not numbers:
            # Fallback: limpieza agresiva si no hay números grandes formateados
            cleaned = re.sub(r'[^0-9]', '', str(price_text))
            return int(cleaned) if cleaned else None
            
        # Limpiar puntos/comas y convertir a int
        clean_nums = [int(re.sub(r'[^0-9]', '', n)) for n in numbers]
        
        if len(clean_nums) >= 2:
            # Es un rango: tomamos el promedio para un RevPAR realista
            return sum(clean_nums) // len(clean_nums)
        
        return clean_nums[0]

    def _extract_services(self, soup):
        services = []

        common_services = [
            'wifi', 'piscina', 'pool', 'restaurante', 'restaurant',
            'parqueadero', 'parking', 'spa', 'gimnasio', 'gym',
            'desayuno', 'breakfast', 'bar', 'aire acondicionado',
            'jacuzzi', 'sauna', 'room service'
        ]

        text = soup.get_text().lower()

        for service in common_services:
            if service in text:
                normalized = {
                    'pool': 'piscina',
                    'restaurant': 'restaurante',
                    'parking': 'parqueadero',
                    'gym': 'gimnasio',
                    'breakfast': 'desayuno'
                }.get(service, service)

                if normalized not in services:
                    services.append(normalized)

        return services[:10]

    def _extract_contact(self, soup, html_text):
        contact = {}

        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', html_text)
        if email_match:
            contact['email'] = email_match.group(0)

        phone_patterns = [
            r'\+57\s*\d{10}',
            r'\(\d{3}\)\s*\d{3}\s*\d{4}',
            r'\d{3}[\s-]?\d{3}[\s-]?\d{4}'
        ]

        for pattern in phone_patterns:
            match = re.search(pattern, html_text)
            if match:
                contact['telefono'] = match.group(0)
                break

        # Parsear enlaces tel: que no aparecen como texto visible
        if 'telefono' not in contact:
            tel_links = soup.find_all('a', href=re.compile(r'^tel:', re.I))
            for link in tel_links:
                phone = link.get('href', '').replace('tel:', '').strip()
                if phone:
                    contact['telefono'] = phone
                    break

        return contact

    def _extract_description(self, soup):
        og_desc = soup.find('meta', property='og:description')
        if og_desc:
            return og_desc.get('content', '')

        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '')

        return ""

    def _extract_schema(self, soup):
        schemas = []

        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                schemas.append(data)
            except Exception:
                continue

        return schemas

    def _calculate_confidence(self, soup):
        score = 0

        if soup.find('script', type='application/ld+json'):
            score += 40

        if soup.find('meta', property='og:title'):
            score += 20

        if soup.find(string=re.compile(r'@|phone|tel', re.I)):
            score += 20

        if soup.find(string=re.compile(r'\$|price|precio', re.I)):
            score += 20

        if score >= 60:
            return 'alta'
        if score >= 30:
            return 'media'
        return 'baja'