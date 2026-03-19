"""
Generador de Certificados Digitales para Hoteles
Plan Maestro v2.2: Certificados de Excelencia
- Certificado "Reserva Directa Certificada"
- Certificado "Web Optimizada para IA"
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import logging


class CertificateGenerator:
    """Generador de certificados digitales según Plan Maestro v2.2"""
    
    def __init__(self, config_path: str = "config/certificates.yaml"):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        self.templates_dir = Path("templates/certificates")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
    
    def check_reserva_directa_eligible(self, hotel_metrics: dict) -> bool:
        """
        Verifica si el hotel es elegible para certificado "Reserva Directa"
        
        Umbral: ≥60% reservas directas O -10 p.p. en OTA (60 días)
        
        Args:
            hotel_metrics: {
                'reservas_directas_pct': 0.62,
                'ota_anterior_pct': 0.75,
                'ota_actual_pct': 0.65,
                'dias_en_umbral': 65
            }
        """
        reservas_directas = hotel_metrics.get('reservas_directas_pct', 0)
        ota_anterior = hotel_metrics.get('ota_anterior_pct', 1.0)
        ota_actual = hotel_metrics.get('ota_actual_pct', 1.0)
        dias_en_umbral = hotel_metrics.get('dias_en_umbral', 0)
        
        # Condición 1: ≥60% reservas directas
        if reservas_directas >= 0.60:
            if dias_en_umbral >= 60:
                return True
        
        # Condición 2: -10 p.p. OTA
        ota_reduction = (ota_anterior - ota_actual) * 100
        if ota_reduction >= 10:
            if dias_en_umbral >= 60:
                return True
        
        return False
    
    def check_web_optimizada_eligible(self, web_metrics: dict) -> bool:
        """
        Verifica si el hotel es elegible para certificado "Web Optimizada"
        
        Umbral: Score Credibilidad Web ≥80/100 (60 días)
        
        Args:
            web_metrics: {
                'score_credibilidad_web': 82,
                'dias_en_umbral': 65,
                'componentes': {
                    'titulo_optimizado': 15,
                    'https': 10,
                    'cta': 12,
                    ...
                }
            }
        """
        score = web_metrics.get('score_credibilidad_web', 0)
        dias_en_umbral = web_metrics.get('dias_en_umbral', 0)
        
        if score >= 80 and dias_en_umbral >= 60:
            return True
        
        return False
    
    def generate_reserva_directa_badge(self, hotel_data: dict) -> dict:
        """
        Genera badge SVG para certificado Reserva Directa
        
        Returns:
            {
                'badge_svg_path': 'templates/certificates/reserva_directa_HOTELID.svg',
                'html_schema': '<div itemscope...>...</div>',
                'qr_code': 'https://iahoteles.co/r/HOTELID',
                'vigencia_hasta': '2026-11-24'
            }
        """
        hotel_id = hotel_data.get('id', 'generico')
        hotel_name = hotel_data.get('nombre', 'Hotel')
        
        # Fecha de vencimiento (12 meses desde hoy)
        vigencia_hasta = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
        
        # Generar SVG
        svg_content = self._create_reserva_directa_svg(hotel_name)
        svg_path = self.templates_dir / f"reserva_directa_{hotel_id}.svg"
        
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        # Generar código HTML con schema
        html_schema = f"""
        <div itemscope itemtype="https://schema.org/Award">
            <img src="https://cdn.iahoteles.co/badges/reserva_directa_{hotel_id}.svg" 
                 alt="Reserva Directa Certificada" 
                 width="150" 
                 height="60"
                 loading="lazy">
            <meta itemprop="name" content="Reserva Directa Certificada - IA Hoteles">
            <meta itemprop="image" content="https://cdn.iahoteles.co/badges/reserva_directa_{hotel_id}.svg">
            <meta itemprop="awardDate" content="{datetime.now().strftime('%Y-%m-%d')}">
            <meta itemprop="expires" content="{vigencia_hasta}">
            <meta itemprop="issuer" content="IA Hoteles Agent">
        </div>
        """
        
        # Generar QR
        qr_url = f"https://iahoteles.co/certificado/reserva-directa/{hotel_id}"
        
        return {
            'certificado': 'reserva_directa',
            'hotel_id': hotel_id,
            'badge_svg_path': str(svg_path),
            'html_schema': html_schema.strip(),
            'qr_code': qr_url,
            'vigencia_hasta': vigencia_hasta,
            'estado': 'activo',
            'tipo_entrega': 'digital + opcional kit físico'
        }
    
    def generate_web_optimizada_badge(self, hotel_data: dict) -> dict:
        """
        Genera badge SVG para certificado Web Optimizada
        
        Returns:
            {
                'badge_svg_path': 'templates/certificates/web_optimizada_HOTELID.svg',
                'html_schema': '<div itemscope...>...</div>',
                'vigencia_hasta': '2026-11-24'
            }
        """
        hotel_id = hotel_data.get('id', 'generico')
        hotel_name = hotel_data.get('nombre', 'Hotel')
        
        # Fecha de vencimiento
        vigencia_hasta = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
        
        # Generar SVG
        svg_content = self._create_web_optimizada_svg(hotel_name)
        svg_path = self.templates_dir / f"web_optimizada_{hotel_id}.svg"
        
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        # Generar código HTML con schema
        html_schema = f"""
        <div itemscope itemtype="https://schema.org/Award">
            <img src="https://cdn.iahoteles.co/badges/web_optimizada_{hotel_id}.svg" 
                 alt="Web Optimizada para IA" 
                 width="150" 
                 height="60"
                 loading="lazy">
            <meta itemprop="name" content="Sitio Optimizado para IA - IA Hoteles">
            <meta itemprop="image" content="https://cdn.iahoteles.co/badges/web_optimizada_{hotel_id}.svg">
            <meta itemprop="awardDate" content="{datetime.now().strftime('%Y-%m-%d')}">
            <meta itemprop="expires" content="{vigencia_hasta}">
            <meta itemprop="issuer" content="IA Hoteles Agent">
        </div>
        """
        
        return {
            'certificado': 'web_optimizada',
            'hotel_id': hotel_id,
            'badge_svg_path': str(svg_path),
            'html_schema': html_schema.strip(),
            'vigencia_hasta': vigencia_hasta,
            'estado': 'activo',
            'tipo_entrega': 'digital'
        }
    
    def _create_reserva_directa_svg(self, hotel_name: str) -> str:
        """Crea SVG para Certificado Reserva Directa"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="150" height="60" viewBox="0 0 150 60" xmlns="http://www.w3.org/2000/svg">
  <!-- Background verde trust -->
  <rect width="150" height="60" fill="#10B981" rx="4"/>
  
  <!-- Border -->
  <rect width="150" height="60" fill="none" stroke="#1E3A8A" stroke-width="2" rx="4"/>
  
  <!-- Checkmark -->
  <circle cx="30" cy="30" r="18" fill="#1E3A8A"/>
  <path d="M 22 30 L 27 35 L 38 24" stroke="#10B981" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  
  <!-- Text -->
  <text x="50" y="22" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#1E3A8A">Reserva</text>
  <text x="50" y="36" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#1E3A8A">Directa</text>
  
  <!-- Subtext -->
  <text x="50" y="52" font-family="Arial, sans-serif" font-size="7" fill="#1E3A8A" opacity="0.8">Certificada</text>
</svg>
"""
    
    def _create_web_optimizada_svg(self, hotel_name: str) -> str:
        """Crea SVG para Certificado Web Optimizada"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="150" height="60" viewBox="0 0 150 60" xmlns="http://www.w3.org/2000/svg">
  <!-- Background azul trust -->
  <rect width="150" height="60" fill="#1E3A8A" rx="4"/>
  
  <!-- Border -->
  <rect width="150" height="60" fill="none" stroke="#10B981" stroke-width="2" rx="4"/>
  
  <!-- Web icon (simplified) -->
  <circle cx="30" cy="30" r="2" fill="#10B981"/>
  <circle cx="25" cy="30" r="8" fill="none" stroke="#10B981" stroke-width="1.5"/>
  <circle cx="35" cy="30" r="8" fill="none" stroke="#10B981" stroke-width="1.5"/>
  <path d="M 22 26 Q 30 20 38 26" stroke="#10B981" stroke-width="1.5" fill="none"/>
  <path d="M 22 34 Q 30 40 38 34" stroke="#10B981" stroke-width="1.5" fill="none"/>
  
  <!-- Text -->
  <text x="48" y="20" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#10B981">Optimizado</text>
  <text x="48" y="34" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#10B981">para IA</text>
  
  <!-- Subtext -->
  <text x="48" y="52" font-family="Arial, sans-serif" font-size="7" fill="#10B981" opacity="0.8">v2.2</text>
</svg>
"""
    
    def export_certificates_json(self, hotel_id: str, certificates: dict) -> str:
        """
        Exporta certificados de un hotel a JSON
        
        Args:
            hotel_id: ID del hotel
            certificates: Dict con certificados generados
        """
        export_data = {
            'hotel_id': hotel_id,
            'fecha_generacion': datetime.now().isoformat(),
            'certificados': certificates
        }
        
        export_path = Path(f"data/cache/certificates_{hotel_id}.json")
        export_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Certificados exportados: {export_path}")
        return str(export_path)


if __name__ == "__main__":
    # Test
    gen = CertificateGenerator()
    
    # Test Reserva Directa
    hotel_data = {'id': 'hotel-visperas', 'nombre': 'Hotel Vísperas'}
    cert_rd = gen.generate_reserva_directa_badge(hotel_data)
    print("Certificado Reserva Directa:", cert_rd)
    
    # Test Web Optimizada
    cert_wo = gen.generate_web_optimizada_badge(hotel_data)
    print("Certificado Web Optimizada:", cert_wo)
