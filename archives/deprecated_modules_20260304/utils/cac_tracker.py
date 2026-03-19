"""
CAC Tracker: Seguimiento de Costo de Adquisición de Clientes
Plan Maestro v2.2 - Fase 4: Sin data no hay estrategia, solo esperanza
"""

import json
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, Optional


class CACTracker:
    """
    Rastreador de CAC (Costo de Adquisición de Clientes)
    según Plan Maestro v2.2: CAC ≤ $800k COP
    """
    
    # Canales definidos en Plan v2.2 Sección 2.2
    CANALES = {
        'linkedin': {
            'nombre': 'LinkedIn',
            'cpl_objetivo': 80000,
            'descripcion': 'Llegar a gerentes y dueños'
        },
        'webinar': {
            'nombre': 'Webinar',
            'cpl_objetivo': 120000,
            'descripcion': '30% de asistentes piden diagnóstico'
        },
        'whatsapp': {
            'nombre': 'WhatsApp',
            'cpl_objetivo': 200000,
            'descripcion': '1 de cada 4 firma en 30 días'
        },
        'instagram': {
            'nombre': 'Instagram',
            'cpl_objetivo': 160000,
            'descripcion': '5% de alcance convierte'
        }
    }
    
    CAC_MAX = 800000  # Plan v2.2
    CAC_ALERTA_UMBRAL = 0.85  # Alertar si CAC > 85% del máximo
    
    def __init__(self, db_path: str = "data/cache/clients.json"):
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        self.db = self._load_db()
    
    def _load_db(self) -> Dict:
        """Carga la base de datos de clientes con información CAC"""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Error cargando DB: {e}. Inicializando vacía.")
        
        return {
            'clientes': [],
            'resumen': {
                'total_clientes': 0,
                'cac_promedio': 0,
                'cac_minimo': None,
                'cac_maximo': None,
                'clientes_dentro_umbral': 0
            }
        }
    
    def log_acquisition(self, 
                       hotel_id: str,
                       hotel_nombre: str,
                       canal: str,
                       costo_cop: int,
                       paquete: str = "Pro AEO",
                       notas: str = "") -> Dict:
        """
        Registra la adquisición de un nuevo cliente
        
        Args:
            hotel_id: ID único del hotel
            hotel_nombre: Nombre del hotel
            canal: Canal de adquisición (linkedin, webinar, whatsapp, instagram)
            costo_cop: Costo en COP invertido
            paquete: Paquete contratado
            notas: Notas adicionales
        
        Returns:
            {
                'status': 'registrado',
                'hotel_id': 'hotel-123',
                'cac': 650000,
                'dentro_umbral': True,
                'alerta': False
            }
        """
        if canal not in self.CANALES:
            self.logger.warning(f"Canal desconocido: {canal}")
            canal = 'otro'
        
        # Validar CAC
        dentro_umbral = costo_cop <= self.CAC_MAX
        alerta = costo_cop > (self.CAC_MAX * self.CAC_ALERTA_UMBRAL)
        
        cliente = {
            'hotel_id': hotel_id,
            'hotel_nombre': hotel_nombre,
            'fecha_adquisicion': datetime.now().isoformat(),
            'canal': canal,
            'costo_cop': costo_cop,
            'paquete': paquete,
            'notas': notas,
            'dentro_umbral_cac': dentro_umbral,
            'alerta_cac': alerta
        }
        
        # Agregar a DB
        self.db['clientes'].append(cliente)
        
        # Actualizar resumen
        self._update_resumen()
        
        # Guardar
        self._save_db()
        
        # Log
        if alerta:
            self.logger.warning(f"⚠️  CAC ALTO para {hotel_nombre}: ${costo_cop:,} COP (umbral: ${self.CAC_MAX:,})")
        else:
            self.logger.info(f"✓ Cliente registrado: {hotel_nombre} - Canal: {canal}")
        
        return {
            'status': 'registrado',
            'hotel_id': hotel_id,
            'cac': costo_cop,
            'dentro_umbral': dentro_umbral,
            'alerta': alerta
        }
    
    def validate_cac(self, costo_proyectado: int) -> Dict:
        """
        Valida si un costo proyectado está dentro del umbral
        
        Returns:
            {
                'valido': True/False,
                'costo': 750000,
                'umbral': 800000,
                'margen': 50000,
                'riesgo': 'bajo'
            }
        """
        valido = costo_proyectado <= self.CAC_MAX
        margen = self.CAC_MAX - costo_proyectado
        porcentaje_umbral = (costo_proyectado / self.CAC_MAX) * 100
        
        if porcentaje_umbral < 75:
            riesgo = 'bajo'
        elif porcentaje_umbral < 90:
            riesgo = 'medio'
        else:
            riesgo = 'alto'
        
        return {
            'valido': valido,
            'costo': costo_proyectado,
            'umbral': self.CAC_MAX,
            'margen': margen,
            'porcentaje_umbral': round(porcentaje_umbral, 1),
            'riesgo': riesgo
        }
    
    def get_cac_por_canal(self) -> Dict:
        """Retorna CAC promedio por canal de adquisición"""
        canales_stats = {}
        
        for canal in self.CANALES.keys():
            clientes_canal = [c for c in self.db['clientes'] if c['canal'] == canal]
            
            if clientes_canal:
                costos = [c['costo_cop'] for c in clientes_canal]
                canales_stats[canal] = {
                    'cantidad': len(clientes_canal),
                    'cac_promedio': round(sum(costos) / len(costos)),
                    'cac_minimo': min(costos),
                    'cac_maximo': max(costos),
                    'dentro_umbral': sum(1 for c in clientes_canal if c['dentro_umbral_cac']) / len(clientes_canal)
                }
        
        return canales_stats
    
    def get_resumen_cac(self) -> Dict:
        """Retorna resumen completo de CAC"""
        return {
            'resumen_general': self.db['resumen'],
            'cac_por_canal': self.get_cac_por_canal(),
            'umbral_v22': self.CAC_MAX,
            'fecha_consulta': datetime.now().isoformat()
        }
    
    def get_clientes_en_alerta(self) -> list:
        """Retorna clientes cuyo CAC está en alerta (>85% del máximo)"""
        return [c for c in self.db['clientes'] if c.get('alerta_cac', False)]
    
    def _update_resumen(self):
        """Actualiza el resumen de CAC"""
        if not self.db['clientes']:
            self.db['resumen'] = {
                'total_clientes': 0,
                'cac_promedio': 0,
                'cac_minimo': None,
                'cac_maximo': None,
                'clientes_dentro_umbral': 0
            }
            return
        
        costos = [c['costo_cop'] for c in self.db['clientes']]
        dentro_umbral = sum(1 for c in self.db['clientes'] if c['dentro_umbral_cac'])
        
        self.db['resumen'] = {
            'total_clientes': len(self.db['clientes']),
            'cac_promedio': round(sum(costos) / len(costos)),
            'cac_minimo': min(costos),
            'cac_maximo': max(costos),
            'clientes_dentro_umbral': dentro_umbral,
            'porcentaje_dentro_umbral': round((dentro_umbral / len(self.db['clientes'])) * 100, 1)
        }
    
    def _save_db(self):
        """Guarda la BD a archivo"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.db, f, indent=2, ensure_ascii=False)
    
    def export_report(self, output_path: str = "output/cac_report.json") -> str:
        """Exporta reporte de CAC"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            'titulo': 'Reporte CAC - Plan Maestro v2.2',
            'fecha_generacion': datetime.now().isoformat(),
            'resumen': self.get_resumen_cac(),
            'clientes_en_alerta': self.get_clientes_en_alerta(),
            'recomendaciones': self._generate_recommendations()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Reporte CAC exportado: {output_path}")
        return str(output_path)
    
    def _generate_recommendations(self) -> list:
        """Genera recomendaciones basadas en datos de CAC"""
        recomendaciones = []
        
        stats = self.get_cac_por_canal()
        
        # Identificar canales más eficientes
        if stats:
            mejor_canal = min(stats.items(), key=lambda x: x[1]['cac_promedio'])
            recomendaciones.append(
                f"💚 Canal más eficiente: {self.CANALES[mejor_canal[0]]['nombre']} "
                f"(CAC promedio ${mejor_canal[1]['cac_promedio']:,})"
            )
        
        # Alertas de clientes fuera de umbral
        en_alerta = self.get_clientes_en_alerta()
        if en_alerta:
            recomendaciones.append(
                f"⚠️  {len(en_alerta)} cliente(s) con CAC elevado (>$680k). "
                f"Revisar eficiencia del canal o renegociar inversión."
            )
        
        # Recomendación de enfoque
        if self.db['resumen']['clientes_dentro_umbral'] >= self.db['resumen']['total_clientes'] * 0.8:
            recomendaciones.append(
                "✅ El 80%+ de clientes están dentro del umbral CAC. "
                f"Continuar con estrategia actual. Incrementar inversión en canales eficientes."
            )
        else:
            recomendaciones.append(
                "🔴 Menos del 80% de clientes dentro de umbral CAC. "
                "Evaluar reducción de presupuesto en canales ineficientes."
            )
        
        return recomendaciones


if __name__ == "__main__":
    # Test
    tracker = CACTracker()
    
    # Log acquisitions
    result1 = tracker.log_acquisition(
        hotel_id="hvisperas-001",
        hotel_nombre="Hotel Vísperas",
        canal="linkedin",
        costo_cop=750000,
        paquete="Elite PLUS",
        notas="Contacto vía LinkedIn InMail"
    )
    print(f"Resultado 1: {result1}")
    
    result2 = tracker.log_acquisition(
        hotel_id="hpalacio-001",
        hotel_nombre="Hotel Palacio",
        canal="webinar",
        costo_cop=120000,
        paquete="Pro AEO"
    )
    print(f"Resultado 2: {result2}")
    
    # Validar CAC
    validation = tracker.validate_cac(850000)
    print(f"\nValidación CAC $850k: {validation}")
    
    # Resumen
    resumen = tracker.get_resumen_cac()
    print(f"\nResumen: {json.dumps(resumen, indent=2, ensure_ascii=False)}")
