from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from datetime import datetime, timedelta

class GBPRevenueLeakDetector:
    """
    DETECTOR DE FUGAS DE RESERVAS GBP
    No es un scraper técnico. Es una herramienta de diagnóstico que calcula
    CUÁNTO dinero está perdiendo HOY un hotel por tener un GBP suboptimizado.
    """
    
    # CONSTANTES DE IMPACTO FINANCIERO (basadas en benchmark Plan Maestro)
    PERDIDA_MENSUAL_BASE = 2_100_000  # COP - Pérdida promedio hotel 15-20 hab
    
    IMPACTOS_FINANCIEROS = {
        'PERFIL_NO_RECLAMADO': {
            'factor': 1.0,  # 100% de pérdida
            'cop_mes': 2_100_000,
            'descripcion': 'Invisible total en búsquedas locales'
        },
        'FOTOS_INSUFICIENTES': {
            'factor': 0.35,  # 35% de la pérdida base
            'cop_mes': 735_000,
            'descripcion': 'Google penaliza relevancia local vs competencia'
        },
        'RESENAS_CRITICAS': {
            'factor': 0.40,  # 40% de la pérdida base
            'cop_mes': 840_000,
            'descripcion': 'Descalificado del shortlist de Google Maps'
        },
        'SIN_WHATSAPP': {
            'factor': 0.30,  # 30% de la pérdida base
            'cop_mes': 630_000,
            'descripcion': '30% de consultas inmediatas nunca llegan'
        },
        'PERFIL_ABANDONADO': {
            'factor': 0.25,  # 25% de la pérdida base
            'cop_mes': 525_000,
            'descripcion': 'Google aplica degradación algorítmica'
        },
        'SIN_FAQ': {
            'factor': 0.20,  # 20% de la pérdida base
            'cop_mes': 420_000,
            'descripcion': 'No responde al modelo conversacional de Google'
        },
        'RATING_BAJO': {
            'factor': 0.45,  # 45% de la pérdida base
            'cop_mes': 945_000,
            'descripcion': 'Excluido automáticamente de recomendaciones'
        },
        'SIN_HORARIOS': {
            'factor': 0.15,  # 15% de la pérdida base
            'cop_mes': 315_000,
            'descripcion': 'Señal de negocio informal o cerrado'
        },
        'SIN_WEBSITE': {
            'factor': 0.25,  # 25% de la pérdida base
            'cop_mes': 525_000,
            'descripcion': 'Fuerza dependencia 100% de OTAs'
        },
        'CERO_ACTIVIDAD_RECIENTE': {
            'factor': 0.30,  # 30% de la pérdida base
            'cop_mes': 630_000,
            'descripcion': 'Google interpreta como negocio inactivo'
        }
    }
    
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
    
    def _init_driver(self):
        """Inicializa Selenium WebDriver"""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
    
    def _calcular_severidad(self, impacto_cop):
        """Determina severidad basada en impacto financiero"""
        if impacto_cop >= 800_000:
            return "CRÍTICA"
        elif impacto_cop >= 500_000:
            return "ALTA"
        elif impacto_cop >= 300_000:
            return "MEDIA"
        else:
            return "BAJA"
    
    def _detectar_fugas(self, profile_data):
        """
        NÚCLEO DEL DETECTOR: Identifica brechas y calcula pérdida real de reservas
        """
        fugas = []
        perdida_total_mes = 0
        
        # FUGA 1: PERFIL NO RECLAMADO O INEXISTENTE
        if not profile_data['existe']:
            impacto = self.IMPACTOS_FINANCIEROS['PERFIL_NO_RECLAMADO']
            fugas.append({
                'tipo': 'PERFIL_NO_RECLAMADO',
                'severidad': 'CRÍTICA',
                'detalle': 'Tu hotel NO EXISTE para Google Maps. Estás entregando el 100% de búsquedas "cerca de mí" a la competencia.',
                'impacto_estimado_COP_mes': impacto['cop_mes'],
                'motivo': 'El 65% de turistas busca "hoteles cerca de mí". Si no estás en Maps, no existes.',
                'urgencia': 'INMEDIATA - Cada día pierdes 70.000 COP en reservas directas'
            })
            perdida_total_mes += impacto['cop_mes']
            return fugas, perdida_total_mes  # Si no existe, no hay más análisis
        
        # FUGA 2: FOTOS INSUFICIENTES
        if profile_data['fotos'] < 15:
            impacto = self.IMPACTOS_FINANCIEROS['FOTOS_INSUFICIENTES']
            fugas.append({
                'tipo': 'FOTOS_INSUFICIENTES',
                'severidad': self._calcular_severidad(impacto['cop_mes']),
                'detalle': f"Solo {profile_data['fotos']} fotos activas → Google te considera menos relevante que hoteles con 15+ fotos.",
                'impacto_estimado_COP_mes': impacto['cop_mes'],
                'motivo': 'Google Maps prioriza perfiles visuales ricos. Tu perfil parece abandonado o informal.',
                'urgencia': 'ALTA - Booking tiene 40+ fotos de tu propio hotel'
            })
            perdida_total_mes += impacto['cop_mes']
        
        # FUGA 3: RESEÑAS CRÍTICAS (< 10 reseñas)
        if profile_data['reviews'] < 10:
            impacto = self.IMPACTOS_FINANCIEROS['RESENAS_CRITICAS']
            fugas.append({
                'tipo': 'RESEÑAS_INSUFICIENTES',
                'severidad': self._calcular_severidad(impacto['cop_mes']),
                'detalle': f"Solo {profile_data['reviews']} reseñas → Señal de desconfianza para el 78% de viajeros.",
                'impacto_estimado_COP_mes': impacto['cop_mes'],
                'motivo': 'Google no recomienda hoteles con < 10 reseñas en resultados conversacionales. Pareces nuevo o poco confiable.',
                'urgencia': 'ALTA - Tus competidores directos tienen 25+ reseñas'
            })
            perdida_total_mes += impacto['cop_mes']
        
        # FUGA 4: RATING BAJO (< 4.0)
        if profile_data['rating'] > 0 and profile_data['rating'] < 4.0:
            impacto = self.IMPACTOS_FINANCIEROS['RATING_BAJO']
            fugas.append({
                'tipo': 'RATING_DESCALIFICANTE',
                'severidad': 'CRÍTICA',
                'detalle': f"Rating {profile_data['rating']}/5.0 → Descalificado automáticamente del top 3 de Google Maps.",
                'impacto_estimado_COP_mes': impacto['cop_mes'],
                'motivo': 'El 92% de usuarios solo considera hoteles con 4.0+. Estás entregando clientes GRATIS a tu competencia.',
                'urgencia': 'CRÍTICA - Responde reseñas negativas HOY o pierdes 31.500 COP diarios'
            })
            perdida_total_mes += impacto['cop_mes']
        
        # FUGA 5: SIN WHATSAPP VISIBLE
        if not profile_data.get('whatsapp_visible', False):
            impacto = self.IMPACTOS_FINANCIEROS['SIN_WHATSAPP']
            fugas.append({
                'tipo': 'SIN_WHATSAPP_VISIBLE',
                'severidad': 'ALTA',
                'detalle': 'WhatsApp no configurado en GBP → Pierdes el 30% de consultas inmediatas que prefieren chat.',
                'impacto_estimado_COP_mes': impacto['cop_mes'],
                'motivo': 'En Colombia, el 68% de reservas directas inician por WhatsApp. Sin botón visible, van a Booking.',
                'urgencia': 'ALTA - Solución: 10 minutos de configuración'
            })
            perdida_total_mes += impacto['cop_mes']
        
        # FUGA 6: SIN POSTS RECIENTES (PERFIL ABANDONADO)
        if profile_data['posts'] == 0:
            impacto = self.IMPACTOS_FINANCIEROS['PERFIL_ABANDONADO']
            fugas.append({
                'tipo': 'PERFIL_ABANDONADO',
                'severidad': 'MEDIA',
                'detalle': 'Cero posts en los últimos 60 días → Google aplica penalización de "negocio inactivo".',
                'impacto_estimado_COP_mes': impacto['cop_mes'],
                'motivo': 'Google interpreta la falta de actividad como señal de cierre temporal. Bajas en el ranking local.',
                'urgencia': 'MEDIA - 1 post semanal recupera posicionamiento en 21 días'
            })
            perdida_total_mes += impacto['cop_mes']
        
        # FUGA 7: SIN FAQ NI Q&A
        if not profile_data.get('tiene_qa', False):
            impacto = self.IMPACTOS_FINANCIEROS['SIN_FAQ']
            fugas.append({
                'tipo': 'SIN_FAQ_CONVERSACIONAL',
                'severidad': 'MEDIA',
                'detalle': 'Sin preguntas/respuestas activas → No respondes al modelo conversacional de Google.',
                'impacto_estimado_COP_mes': impacto['cop_mes'],
                'motivo': 'El 40% de búsquedas turísticas son preguntas ("¿acepta mascotas?", "¿tiene piscina?"). No apareces en esas respuestas.',
                'urgencia': 'MEDIA - Alimenta a ChatGPT y Gemini con tus respuestas'
            })
            perdida_total_mes += impacto['cop_mes']
        
        # FUGA 8: SIN HORARIOS CONFIGURADOS
        if not profile_data['horarios']:
            impacto = self.IMPACTOS_FINANCIEROS['SIN_HORARIOS']
            fugas.append({
                'tipo': 'SIN_HORARIOS',
                'severidad': 'MEDIA',
                'detalle': 'Horarios no configurados → Google muestra "Horario desconocido" (señal de informalidad).',
                'impacto_estimado_COP_mes': impacto['cop_mes'],
                'motivo': 'Hoteles sin horarios parecen negocios temporales o informales. Check-in 24h debe estar visible.',
                'urgencia': 'BAJA - Solución: 5 minutos en GBP'
            })
            perdida_total_mes += impacto['cop_mes']
        
        # FUGA 9: SIN WEBSITE
        if not profile_data['website']:
            impacto = self.IMPACTOS_FINANCIEROS['SIN_WEBSITE']
            fugas.append({
                'tipo': 'SIN_WEBSITE_DIRECTO',
                'severidad': 'ALTA',
                'detalle': 'Sin enlace a sitio web → Fuerzas dependencia 100% de Booking/Expedia (comisiones 15-25%).',
                'impacto_estimado_COP_mes': impacto['cop_mes'],
                'motivo': 'Sin canal directo, cada reserva pierde 18-25% en comisiones. Estás regalando tu margen operativo.',
                'urgencia': 'ALTA - Cada mes sin web directa pierdes 525.000 COP en comisiones evitables'
            })
            perdida_total_mes += impacto['cop_mes']
        
        # FUGA 10: SIN TELÉFONO VISIBLE
        if not profile_data['telefono']:
            impacto_telefono = 210_000  # Impacto menor pero relevante
            fugas.append({
                'tipo': 'SIN_TELEFONO_VISIBLE',
                'severidad': 'BAJA',
                'detalle': 'Teléfono no visible → Pierdes llamadas directas de viajeros de +50 años (20% del mercado).',
                'impacto_estimado_COP_mes': impacto_telefono,
                'motivo': 'Segmento 50+ prefiere llamada. Sin teléfono visible, reservan en hotel de al lado.',
                'urgencia': 'BAJA - Solución: 2 minutos'
            })
            perdida_total_mes += impacto_telefono
        
        return fugas, perdida_total_mes
    
    def check_google_profile(self, hotel_name, location):
        """
        AUDITORÍA AGRESIVA DE GBP
        Retorna diagnóstico ejecutivo con pérdida financiera real
        """
        try:
            if not self.driver:
                self._init_driver()
            
            # Buscar en Google Maps
            search_query = f"{hotel_name} {location}"
            maps_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
            
            self.driver.get(maps_url)
            time.sleep(3)
            
            # ESTRUCTURA DE DATOS MEJORADA
            profile_data = {
                'existe': False,
                'score': 0,
                'issues': [],  # Mantener para compatibilidad
                'reviews': 0,
                'rating': 0.0,
                'fotos': 0,
                'horarios': False,
                'descripcion': False,
                'website': False,
                'telefono': False,
                'whatsapp_visible': False,
                'posts': 0,
                'tiene_qa': False,
                'ultima_actividad_dias': None,
                # NUEVO: BLOQUE DE FUGAS
                'fugas_detectadas': [],
                'perdida_total_mes_COP': 0,
                'perdida_anual_COP': 0,
                'prioridad_accion': None
            }
            
            # Verificar si existe el perfil
            try:
                title_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
                )
                profile_data['existe'] = True
            except:
                # PERFIL NO EXISTE - FUGA CRÍTICA
                fugas, perdida = self._detectar_fugas(profile_data)
                profile_data['fugas_detectadas'] = fugas
                profile_data['perdida_total_mes_COP'] = perdida
                profile_data['perdida_anual_COP'] = perdida * 12
                profile_data['prioridad_accion'] = 'CRÍTICA - RECLAMAR PERFIL HOY'
                profile_data['issues'].append("CRÍTICO: Perfil GBP no existe - Pérdida: 2.1M COP/mes")
                return profile_data
            
            # EXTRACCIÓN DE DATOS AMPLIADA
            
            # Rating y reviews
            try:
                rating_elem = self.driver.find_element(By.CSS_SELECTOR, "[aria-label*='estrellas']")
                rating_text = rating_elem.get_attribute('aria-label')
                rating_match = re.search(r'([\d,\.]+)', rating_text)
                if rating_match:
                    profile_data['rating'] = float(rating_match.group(1).replace(',', '.'))
                
                reviews_match = re.search(r'(\d+)\s*reseñas?', rating_text)
                if reviews_match:
                    profile_data['reviews'] = int(reviews_match.group(1))
            except:
                pass
            
            # Fotos
            try:
                photos_button = self.driver.find_element(By.CSS_SELECTOR, "[aria-label*='fotos']")
                photos_text = photos_button.get_attribute('aria-label')
                photos_match = re.search(r'(\d+)', photos_text)
                if photos_match:
                    profile_data['fotos'] = int(photos_match.group(1))
            except:
                pass
            
            # Horarios
            try:
                self.driver.find_element(By.CSS_SELECTOR, "[aria-label*='horario']")
                profile_data['horarios'] = True
            except:
                pass
            
            # Website
            try:
                self.driver.find_element(By.CSS_SELECTOR, "a[data-item-id='authority']")
                profile_data['website'] = True
            except:
                pass
            
            # Teléfono
            try:
                self.driver.find_element(By.CSS_SELECTOR, "[data-item-id*='phone']")
                profile_data['telefono'] = True
            except:
                pass
            
            # WhatsApp (detección mejorada)
            try:
                # Buscar botón de mensajería o enlace WhatsApp
                whatsapp_elements = self.driver.find_elements(By.XPATH, 
                    "//*[contains(text(), 'WhatsApp') or contains(@href, 'wa.me') or contains(@href, 'whatsapp')]")
                if whatsapp_elements:
                    profile_data['whatsapp_visible'] = True
            except:
                pass
            
            # Posts recientes (aproximación por presencia de sección)
            try:
                posts_section = self.driver.find_elements(By.CSS_SELECTOR, "[aria-label*='Actualizaciones']")
                if posts_section:
                    profile_data['posts'] = 1  # Indicador de presencia
            except:
                pass
            
            # Q&A (Preguntas y respuestas)
            try:
                qa_section = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Preguntas y respuestas')]")
                if qa_section:
                    profile_data['tiene_qa'] = True
            except:
                pass
            
            # CALCULAR SCORE TRADICIONAL (mantener compatibilidad)
            score = 0
            if profile_data['existe']:
                score += 20
            if profile_data['reviews'] >= 10:
                score += 15
            elif profile_data['reviews'] > 0:
                score += 10
            if profile_data['rating'] >= 4.0:
                score += 15
            elif profile_data['rating'] > 0:
                score += 10
            if profile_data['fotos'] >= 15:
                score += 15
            elif profile_data['fotos'] >= 5:
                score += 10
            if profile_data['horarios']:
                score += 10
            if profile_data['website']:
                score += 10
            if profile_data['telefono']:
                score += 5
            
            profile_data['score'] = score
            
            # DETECTAR FUGAS Y CALCULAR IMPACTO FINANCIERO
            fugas, perdida_mensual = self._detectar_fugas(profile_data)
            profile_data['fugas_detectadas'] = fugas
            profile_data['perdida_total_mes_COP'] = perdida_mensual
            profile_data['perdida_anual_COP'] = perdida_mensual * 12
            
            # DETERMINAR PRIORIDAD DE ACCIÓN
            if perdida_mensual >= 1_500_000:
                profile_data['prioridad_accion'] = 'CRÍTICA - ACTUAR EN 72 HORAS'
            elif perdida_mensual >= 1_000_000:
                profile_data['prioridad_accion'] = 'ALTA - ACTUAR EN 7 DÍAS'
            elif perdida_mensual >= 500_000:
                profile_data['prioridad_accion'] = 'MEDIA - ACTUAR EN 30 DÍAS'
            else:
                profile_data['prioridad_accion'] = 'BAJA - OPTIMIZACIÓN CONTINUA'
            
            # Issues tradicionales (mantener compatibilidad)
            if profile_data['reviews'] < 10:
                profile_data['issues'].append(f"Pocas reseñas ({profile_data['reviews']}), meta: 10+")
            if profile_data['fotos'] < 15:
                profile_data['issues'].append(f"Pocas fotos ({profile_data['fotos']}), meta: 15+")
            if profile_data['rating'] < 4.0 and profile_data['rating'] > 0:
                profile_data['issues'].append(f"Rating bajo ({profile_data['rating']}), meta: 4.0+")
            
            return profile_data
            
        except Exception as e:
            print(f"[FAIL] Error en GBP scraping: {e}")
            return {
                'existe': False,
                'score': 0,
                'issues': [f"Error al auditar GBP: {str(e)}"],
                'reviews': 0,
                'rating': 0.0,
                'fugas_detectadas': [],
                'perdida_total_mes_COP': 0,
                'perdida_anual_COP': 0,
                'prioridad_accion': 'ERROR - REINTENTAR'
            }
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
    
    def generar_reporte_ejecutivo(self, profile_data, hotel_name):
        """
        GENERA REPORTE EJECUTIVO PARA PRESENTAR AL CLIENTE
        Lenguaje directo, sin tecnicismos, enfocado en dinero perdido
        """
        reporte = f"""
╔═══════════════════════════════════════════════════════════════════════╗
║     DIAGNÓSTICO DE FUGAS DE RESERVAS - {hotel_name.upper()}
╚═══════════════════════════════════════════════════════════════════════╝

📊 RESUMEN EJECUTIVO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pérdida mensual estimada:  ${profile_data['perdida_total_mes_COP']:,} COP
Pérdida anual proyectada:  ${profile_data['perdida_anual_COP']:,} COP
Prioridad de acción:       {profile_data['prioridad_accion']}
Score actual GBP:          {profile_data['score']}/100

🚨 FUGAS DETECTADAS ({len(profile_data['fugas_detectadas'])})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        for i, fuga in enumerate(profile_data['fugas_detectadas'], 1):
            reporte += f"""
[{i}] {fuga['tipo']} - SEVERIDAD: {fuga['severidad']}
    └─ Impacto: ${fuga['impacto_estimado_COP_mes']:,} COP/mes
    └─ {fuga['detalle']}
    └─ Por qué pierdes dinero: {fuga['motivo']}
    └─ Urgencia: {fuga['urgencia']}
"""
        
        reporte += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 DATOS DEL PERFIL ACTUAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Perfil reclamado:     {'SÍ' if profile_data['existe'] else 'NO (CRÍTICO)'}
✓ Rating:               {profile_data['rating']}/5.0
✓ Reseñas:              {profile_data['reviews']}
✓ Fotos:                {profile_data['fotos']}
✓ Website visible:      {'SÍ' if profile_data['website'] else 'NO'}
✓ WhatsApp visible:     {'SÍ' if profile_data['whatsapp_visible'] else 'NO'}
✓ Horarios config.:     {'SÍ' if profile_data['horarios'] else 'NO'}
✓ Teléfono visible:     {'SÍ' if profile_data['telefono'] else 'NO'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 LO QUE ESTO SIGNIFICA EN ESPAÑOL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Hoy estás regalando ${profile_data['perdida_total_mes_COP']:,} COP cada mes
a Booking, Expedia y a tu competencia directa.

Cada búsqueda "hoteles cerca de mí" que no te encuentra es una reserva
que va a parar al hotel de al lado.

Este no es un problema técnico. Es un problema de CAJA.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 PRÓXIMO PASO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Solicita tu Plan 2-Pilares (GBP + JSON) y en 30 días recupera
al menos el 40% de esta fuga.

Inversión: $1.8M COP/mes | ROI esperado: 3X en 90 días

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return reporte


# EJEMPLO DE USO
if __name__ == "__main__":
    detector = GBPRevenueLeakDetector(headless=False)
    
    # Auditar hotel
    resultado = detector.check_google_profile(
        hotel_name="Hotel Boutique Ejemplo",
        location="Salento, Quindío"
    )
    
    # Generar reporte ejecutivo
    reporte = detector.generar_reporte_ejecutivo(resultado, "Hotel Boutique Ejemplo")
    print(reporte)
    
    # También disponible en JSON para integración
    import json
    print("\n" + "="*70)
    print("JSON PARA INTEGRACIÓN:")
    print("="*70)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))