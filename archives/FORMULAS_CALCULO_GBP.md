# Fórmulas de Cálculo - Auditoría GBP

**Versión**: 1.0  
**Fecha**: 2026-02-23  
**Autor**: IA Hoteles Agent

---

## Resumen

Este documento detalla las fórmulas utilizadas para calcular pérdidas de ingresos por deficiencias en Google Business Profile (GBP).

---

## 1. Cálculo de Geo Score

### Fórmula

```
geo_score = (rating/5 × 30) + (reviews/100 × 2) + (min(photos × 0.5, 20)) + 
            (10 if has_hours) + (10 if has_website)
```

### Desglose de Componentes

| Componente | Máximo Puntos | Fórmula | Descripción |
|------------|---------------|---------|-------------|
| Rating | 30 | `rating / 5 × 30` | Calificación de 1-5 estrellas |
| Reviews | 20 | `min(reviews / 100 × 2, 20)` | Cantidad de reseñas (cap en 1000) |
| Photos | 20 | `min(photos × 0.5, 20)` | Fotos en perfil (cap en 40) |
| Horarios | 10 | `10 if has_hours else 0` | Presencia de horarios |
| Website | 10 | `10 if has_website else 0` | Enlace a sitio web |

**Total Máximo**: 90 puntos (normalizado a 100)

### Normalización

```python
def normalize_geo_score(raw_score: float) -> int:
    """Normaliza score de 0-90 a escala 0-100."""
    return int(min(raw_score * (100 / 90), 100))
```

### Ejemplo de Cálculo

```
Hotel Visperas:
- Rating: 4.8 → 4.8/5 × 30 = 28.8 puntos
- Reviews: 156 → 156/100 × 2 = 3.12 puntos
- Photos: 12 → 12 × 0.5 = 6.0 puntos
- Horarios: Sí → 10 puntos
- Website: Sí → 10 puntos

Total: 28.8 + 3.12 + 6.0 + 10 + 10 = 57.92
Normalizado: 57.92 × (100/90) = 64 puntos
```

---

## 2. Cálculo de Pérdida por Fugas GBP

### Identificación de Fugas

El sistema detecta las siguientes fugas en GBP:

| Fuga | Factor | COP/mes Base | Descripción |
|------|--------|--------------|-------------|
| PERFIL_NO_RECLAMADO | 1.0 | 2,100,000 | Perfil no reclamado |
| FOTOS_INSUFICIENTES | 0.35 | 735,000 | Menos de 15 fotos |
| SIN_WHATSAPP | 0.30 | 630,000 | Sin WhatsApp visible |
| SIN_HORARIOS | 0.15 | 315,000 | Sin horarios publicados |
| PERFIL_ABANDONADO | 0.25 | 525,000 | Sin actividad reciente |
| SIN_FAQ | 0.20 | 420,000 | Sin Q&A |
| RATING_BAJO | 0.45 | 945,000 | Rating < 4.0 |

### Fórmula de Impacto Individual

```python
def calculate_fuga_impact(
    fuga_tipo: str,
    region: str,
    hotel_data: Dict
) -> int:
    """
    Calcula el impacto mensual de una fuga específica.
    
    Args:
        fuga_tipo: Tipo de fuga (ej: 'FOTOS_INSUFICIENTES')
        region: Código de región para benchmarks
        hotel_data: Datos del hotel (habitaciones, ADR, etc.)
        
    Returns:
        Impacto mensual en COP
    """
    # Obtener benchmark regional
    benchmark = get_regional_benchmark(region)
    
    # Base de pérdida (2.8M COP del Plan Maestro v2.2)
    base_perdida = 2_800_000
    
    # Factor de la fuga
    factor = IMPACTOS_FINANCIEROS[fuga_tipo]['factor']
    
    # Ajuste por tamaño del hotel
    habitaciones = hotel_data.get('habitaciones', 15)
    ajuste_tamano = habitaciones / 15  # Normalizado a hotel promedio
    
    # Ajuste por ADR
    adr = hotel_data.get('precio_promedio', 280000)
    adr_benchmark = benchmark.get('precio_promedio', 280000)
    ajuste_adr = adr / adr_benchmark
    
    # Cálculo final
    impacto = base_perdida * factor * ajuste_tamano * ajuste_adr
    
    return int(impacto)
```

### Corrección de Superposición

**Problema identificado**: La suma simple de fugas individuales sobrestima la pérdida total porque las fugas no son independientes.

**Solución**: Aplicar factor de corrección por superposición.

```python
def calculate_total_loss_with_correction(
    fugas: List[Dict],
    apply_correction: bool = True
) -> int:
    """
    Calcula pérdida total con corrección de superposición.
    
    Las fugas GBP tienen overlapping: un cliente que no encuentra
    el perfil por falta de fotos TAMBIÉN cuenta como pérdida por
    perfil no reclamado. No debemos sumar ambas pérdidas.
    
    Args:
        fugas: Lista de fugas detectadas con sus impactos
        apply_correction: Si True, aplica corrección de superposición
        
    Returns:
        Pérdida total mensual en COP
    """
    if not fugas:
        return 0
    
    # Suma simple (sin corrección)
    suma_simple = sum(f['impacto_estimado_COP_mes'] for f in fugas)
    
    if not apply_correction:
        return suma_simple
    
    # Factor de corrección basado en cantidad de fugas
    # Más fugas = más overlapping = menor factor de corrección
    num_fugas = len(fugas)
    
    if num_fugas <= 2:
        factor_correccion = 0.5  # 50% de la suma
    elif num_fugas <= 4:
        factor_correccion = 0.35  # 35% de la suma
    elif num_fugas <= 6:
        factor_correccion = 0.25  # 25% de la suma
    else:
        factor_correccion = 0.15  # 15% de la suma
    
    # Tomar la fuga de mayor impacto como base
    max_fuga = max(fugas, key=lambda x: x['impacto_estimado_COP_mes'])
    
    # Fórmula final: mayor fuga + (suma restante × factor)
    otras_fugas = suma_simple - max_fuga['impacto_estimado_COP_mes']
    perdida_total = max_fuga['impacto_estimado_COP_mes'] + (otras_fugas * factor_correccion)
    
    return int(perdida_total)
```

### Ejemplo de Cálculo con Corrección

```
Hotel Visperas - Fugas detectadas:
1. FOTOS_INSUFICIENTES: 10.5M/mes
2. SIN_WHATSAPP: 9.0M/mes
3. SIN_HORARIOS: 4.5M/mes
4. PERFIL_ABANDONADO (2x): 16.5M/mes
5. SIN_FAQ: 6.0M/mes

Suma simple: 46.5M COP/mes

Con corrección (4 fugas → factor 0.35):
- Mayor fuga: 16.5M
- Otras fugas: 30.0M
- Corrección: 30.0M × 0.35 = 10.5M
- Total corregido: 16.5M + 10.5M = 27M COP/mes

Pero el sistema usa la "brecha dominante" para el reporte final:
- Brecha dominante = 2.5M (pérdida por oportunidades no capturadas)
```

---

## 3. Brecha Dominante

El sistema prioriza la "brecha dominante" para el cálculo de pérdida reportada:

```python
def identify_dominant_gap(
    fugas: List[Dict],
    gbp_score: int,
    web_score: int
) -> Dict:
    """
    Identifica la brecha dominante que determina la pérdida reportada.
    
    El sistema NO suma todas las pérdidas, sino que identifica
    la oportunidad más significativa de mejora.
    
    Returns:
        Dict con la brecha dominante y su impacto
    """
    # Si GBP score es muy bajo, la pérdida es por visibilidad
    if gbp_score < 40:
        return {
            'tipo': 'GBP_VISIBILIDAD',
            'impacto': max(fugas, key=lambda x: x['impacto'])['impacto'],
            'descripcion': 'Perfil GBP suboptimizado limita captura de demanda local'
        }
    
    # Si falta motor de reservas, priorizar eso
    motor_fuga = next((f for f in fugas if 'motor' in f['tipo'].lower()), None)
    if motor_fuga:
        return motor_fuga
    
    # Default: mayor impacto individual
    return max(fugas, key=lambda x: x['impacto'])
```

---

## 4. Validación de Datos

### Nivel de Confianza

| Fuente | Confianza | Notación en informe |
|--------|-----------|---------------------|
| Onboarding confirmado | 100% | ✓ Confirmado |
| Google Places API | 95% | ★ API Real |
| Scraping directo | 85% | ◐ Scraping |
| Benchmark regional | 50% | ⚠ Estimado |

### Indicadores en Informes

Los informes generados incluyen indicadores visuales del nivel de confianza de cada dato:

```
📊 DATOS OPERATIVOS
Habitaciones: 22 ✓ Confirmado (onboarding)
Reservas/mes: 180 ✓ Confirmado (onboarding)
Valor reserva: $350,000 ✓ Confirmado (onboarding)
Canal directo: 45% ✓ Confirmado (onboarding)

📍 DATOS GBP
Rating: 4.8 ★ API Real (Google Places)
Reviews: 156 ★ API Real (Google Places)
Fotos: 12 ◐ Scraping (Playwright)
Geo Score: 64 ★ API Real (calculado)
```

---

## 5. Supuestos y Limitaciones

### Supuestos del Modelo

1. **Tasa de captura**: Se asume que el 65% de búsquedas "cerca de mí" se convierten en visitas al perfil GBP.

2. **Impacto de fotos**: Se asume que cada foto adicional incrementa la probabilidad de contacto en 0.5%.

3. **Pérdida por rating**: Se asume que hoteles con rating < 4.0 son excluidos del 40% de recomendaciones.

4. **Superposición**: Se asume que las fugas no son eventos independientes (ver sección 2.3).

### Limitaciones Conocidas

1. **Datos del hotel**: Si el hotel no proporciona datos operativos, se usan benchmarks regionales con menor precisión.

2. **Competidores**: Los geo_scores de competidores dependen de la disponibilidad de Places API y caché.

3. **Estacionalidad**: Las pérdidas no ajustan por estacionalidad turística.

4. **Mercado**: Los benchmarks se basan en datos de Colombia 2025-2026.

---

## Referencias

- Plan Maestro v2.5: `data/benchmarks/Plan_maestro_v2_5.md`
- Benchmarking: `data/benchmarks/Benchmarking.md`
- INFORME_PUNTOS_ESTIMACION.md: Análisis de estimaciones

---

*Documento v1.0 - Creado: 2026-02-23*
