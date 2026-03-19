import unicodedata

from modules.scrapers.scraper_fallback import ScraperFallback


class ROICalculator:
    def __init__(self):
        self._fallback_helper = ScraperFallback()
        self._region_profiles = self._fallback_helper.benchmarks.get('regiones', {})
        self._default_profile = self._region_profiles.get('default', {
            'precio_promedio': 280000,
            'precio_min': 280000,
            'ocupacion': 0.58,
            'comision_ota': 0.18,
            # Factores optimizados para proyección comercial (Growth)
            'recuperacion_factores': [0.40, 0.65, 0.90, 1.20, 1.50, 1.80],
        })
        self.comision_ota_default = self._default_profile.get('comision_ota', 0.18)
        self.ocupacion_promedio = self._default_profile.get('ocupacion', 0.53)
        self.margen_operativo = 0.35

    def _detect_region(self, hotel_data):
        ubicacion = hotel_data.get('ubicacion') or hotel_data.get('region') or ''
        if not ubicacion:
            return 'default'
        normalized = unicodedata.normalize('NFKD', ubicacion)
        normalized = normalized.encode('ascii', 'ignore').decode('ascii')
        return self._fallback_helper._detect_region(normalized.lower())

    def _get_region_profile(self, region):
        return self._region_profiles.get(region, self._default_profile)

    def calculate(self, hotel_data, claude_analysis, seo_data=None, decision_result=None):
        """Calcula ROI detallado y proyecciones a 6 meses.

        "claude_analysis" se mantiene por compatibilidad, pero el paquete puede ser
        sobreescrito por "decision_result" (reglas puras v2.3).
        """

        region = self._detect_region(hotel_data)
        region_profile = self._get_region_profile(region)

        precio_base = hotel_data.get('precio_promedio')
        if not isinstance(precio_base, (int, float)) or precio_base <= 0:
            precio_base = 0
        precio_min = region_profile.get('precio_min', region_profile.get('precio_promedio', 180000))
        precio_promedio = max(precio_base, precio_min)

        ocupacion_actual = hotel_data.get('ocupacion_actual')
        if not isinstance(ocupacion_actual, (int, float)) or ocupacion_actual <= 0:
            ocupacion_actual = region_profile.get('ocupacion', self.ocupacion_promedio)

        comision_ota = hotel_data.get('comision_ota')
        if not isinstance(comision_ota, (int, float)) or comision_ota <= 0:
            comision_ota = region_profile.get('comision_ota', self.comision_ota_default)

        recuperacion_factores = region_profile.get('recuperacion_factores', self._default_profile.get('recuperacion_factores', [0.40, 0.65, 0.90, 1.20, 1.50, 1.80]))

        perdida_mensual_base = claude_analysis.get('perdida_mensual_total', 0)
        
        # Integrar perdida SEO si existe para un analisis holistico
        perdida_seo = 0
        if seo_data:
             perdida_seo = seo_data.get('estimated_revenue_loss', 0) or 0
        
        # Usamos la mayor de las dos o una combinacion ponderada
        # Estrategia comercial: Mostrar el impacto total combinado
        perdida_mensual = perdida_mensual_base + (perdida_seo * 0.5) # Asumimos solapamiento del 50%
        
        paquete = 'Pro AEO'
        if decision_result and isinstance(decision_result, dict):
            paquete = decision_result.get('paquete', paquete)
        else:
            paquete = claude_analysis.get('paquete_recomendado', paquete)

        costos_paquetes = {
            'Starter GEO': 1_800_000,
            'Pro AEO': 3_800_000,
            'Pro AEO Plus': 4_800_000,
            'Elite': 7_500_000,
            'Elite PLUS': 9_800_000,
            'Elite IAO': 7_500_000,  # legacy mapping
        }

        inversion_mensual = costos_paquetes.get(paquete, 3800000)

        proyeccion_6_meses = []
        recuperacion_acumulada = 0

        for mes in range(1, 7):
            if recuperacion_factores:
                factor_recuperacion = recuperacion_factores[min(mes - 1, len(recuperacion_factores) - 1)]
            else:
                factor_recuperacion = 0.35

            ingreso_recuperado = perdida_mensual * factor_recuperacion
            beneficio_neto = ingreso_recuperado - inversion_mensual
            recuperacion_acumulada += beneficio_neto

            proyeccion_6_meses.append({
                'mes': mes,
                'inversion': inversion_mensual,
                'ingreso_recuperado': int(ingreso_recuperado),
                'beneficio_neto': int(beneficio_neto),
                'acumulado': int(recuperacion_acumulada),
            })

        inversion_total_6m = inversion_mensual * 6
        ingreso_total_6m = sum(p['ingreso_recuperado'] for p in proyeccion_6_meses)
        roas = ingreso_total_6m / inversion_total_6m if inversion_total_6m > 0 else 0

        mes_recuperacion = None
        for proyeccion in proyeccion_6_meses:
            if proyeccion['acumulado'] >= 0:
                mes_recuperacion = proyeccion['mes']
                break

        reservas_denominador = precio_promedio * comision_ota
        if reservas_denominador <= 0:
            reservas_denominador = 1

        return {
            'inversion_mensual': inversion_mensual,
            'paquete': paquete,
            'proyeccion_6_meses': proyeccion_6_meses,
            'totales_6_meses': {
                'inversion_total': inversion_total_6m,
                'ingreso_recuperado': int(ingreso_total_6m),
                'beneficio_neto': int(ingreso_total_6m - inversion_total_6m),
                'roas': round(roas, 1),
            },
            'mes_recuperacion': mes_recuperacion or 'Post mes 6',
            'roi_porcentaje': round(((ingreso_total_6m - inversion_total_6m) / inversion_total_6m * 100), 1) if inversion_total_6m > 0 else 0,
            'metricas_adicionales': {
                'reservas_directas_potenciales_mes': int(perdida_mensual / reservas_denominador) if perdida_mensual else 0,
                'ahorro_comisiones_6m': int(ingreso_total_6m),
                'valor_cliente_6m': int(precio_promedio * 3),
                'region_referencia': region,
                'benchmark_comision': comision_ota,
                'benchmark_ocupacion': ocupacion_actual,
            },
        }
