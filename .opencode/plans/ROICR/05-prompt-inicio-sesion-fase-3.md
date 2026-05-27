# FASE-3: Pipeline Unificado de Pricing + CAPEX/OPEX Desacoplado + Curva 4 Pilares

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DIRECTA (código)
> **Plan**: ROICR
> **Prerrequisito**: FASE-2 completada (Gate P1 BLOCKING activo)

## Contexto previo

FASE-1 y FASE-2 establecieron la gobernanza semántica (validator + gate). Ahora atacamos el corazón financiero: el pricing produce $1.2M (arbitraje negativo), CAPEX/OPEX están mezclados en el ROI, y la proyección usa descuento lineal en vez de curva de maduración por pilares.

El ROICR.md advierte: NO implementar el Value-Capture Cap y el Floor Condicional como if/else separados — deben ser un **pipeline de 3 pasos en orden fijo** dentro de `pricing_calculator.py`.

## Objetivo de esta fase

Implementar el motor financiero v3.0: pipeline unificado de 3 pasos, métricas CAPEX/OPEX desacopladas, y curva de maduración basada en los 4 pilares.

### Tareas

- [ ] **3A**: Actualizar `config/pricing.yaml`
  - Agregar campos nuevos al tier `boutique`:
    ```yaml
    value_capture_cap: 0.50
    operational_floor: 400_000
    pain_ratio_gate_max: 0.32
    ```
  - Bajar `min_price` de 1,200,000 a 800,000
  - **Verificar formato real del YAML** — puede tener estructura diferente a la del ROICR.md

- [ ] **3B**: Refactorizar `modules/financial_engine/pricing_calculator.py`
  - Implementar `calcular_precio_final()` con pipeline de 3 pasos:
    - **Paso 1**: Precio Base = `max(min_price, min(expected_loss * percentage, max_price))`
    - **Paso 2**: Pain Ratio Adjustment — si `pain_ratio > GATE_MAX * 2.0`, promediar entre floor y recommended
    - **Paso 3**: Ethical Cap — `final_price = min(base_price, expected_recovery * value_capture_cap)`
    - Floor final: `max(final_price, operational_floor)`
  - **CRÍTICO**: Verificar el código existente ANTES de parchear. El ROICR.md es un diseño, no código real. Adaptar al código vivo.

- [ ] **3C**: Crear `modules/financial_engine/roi_formatter.py`
  - Función `calcular_metricas_roi(recuperacion_total, inversion_opex, inversion_capex)`
  - Retorna dict con:
    - `roi_saas`: `recuperacion_total / inversion_opex` (NUNCA dividir por OPEX+CAPEX)
    - `valorizacion_activo_digital`: igual a `inversion_capex`
    - `nota_metodologica`: texto explicativo
  - **PROHIBIDO**: `Recuperación / (OPEX + CAPEX)` — esto produce ROI falso de 0.80X

- [ ] **3D**: Crear `modules/financial_engine/pillar_maturity_curve.py`
  - Función `aplicar_curva_4_pilares(fuga_mensual, recovery_factor_max)`
  - Curva: `[0.15, 0.35, 0.60, 0.80, 0.95, 1.00]` (6 meses)
  - Cada mes: `fuga_mensual * recovery_factor_max * factor_mes`

- [ ] **3E**: Integrar en `v4_proposal_generator.py`
  - Importar `calcular_metricas_roi` y `aplicar_curva_4_pilares`
  - Renderizar 2 tablas separadas: CAPEX (único $2.5M) y OPEX (mensual)
  - Mostrar `roi_saas` independiente
  - Incluir lista de `activos_digitales_propiedad_cliente`

- [ ] **3F**: Actualizar `config/scenarios.yaml` — recovery_factor a 0.35 (realista con 4 pilares)

- [ ] **3G**: Actualizar narrativa comercial — Pitch & 4-Pillar Maturity Narrative
  - Actualizar textos del pitch de cierre en templates/markdown con:
    - Value-Capture Cap: "nuestro modelo nos prohíbe cobrarle más del 50% de lo que recuperamos"
    - CAPEX/OPEX: "los $2.5M no son un fee, son Real Estate Digital de su propiedad"
    - Garantía Día 55: "nuestra propia IA audita y emite nota crédito sin intervención humana"
    - Curva 4 Pilares: explicar GEO (Mes 1) → SEO (Mes 2-3) → AEO/IAO (Mes 4-6) en lenguaje de negocio
  - Verificar que el template de propuesta renderice las 2 tablas (CAPEX/OPEX) con narrativa unificada
  - **Commit resultante**: `docs(commercial): Update Pitch & 4-Pillar Maturity Narrative`

### Restricciones

- El ROICR.md dice "Castilla Real → $654,796" pero eso depende de los valores reales de expected_loss y recovery_factor en el código. Verificar con datos reales, no asumir el número exacto.
- NO tocar publication_gates.py (ya está en FASE-2)
- NO crear tests todavía (FASE-5)
- Si `config/pricing.yaml` tiene estructura diferente, adaptar — no forzar la estructura del ROICR.md

### Criterios de completitud

- [ ] `pricing.yaml` tiene `value_capture_cap`, `operational_floor`, `pain_ratio_gate_max`
- [ ] `pricing_calculator.py` tiene `calcular_precio_final()` con 3 pasos
- [ ] `roi_formatter.py` existe y retorna métricas desacopladas
- [ ] `pillar_maturity_curve.py` existe con curva `[0.15, 0.35, 0.60, 0.80, 0.95, 1.00]`
- [ ] `grep "roi_saas" modules/commercial_documents/v4_proposal_generator.py` muestra integración
- [ ] `grep "Recuperación.*OPEX.*CAPEX\|OPEX.*CAPEX.*Recuperación" modules/` retorna 0 matches (prohibido)
- [ ] Documentar resultado en `09-documentacion-post-proyecto.md` §FASE-3

### Próxima sesión

FASE-4: Arbitraje ético gate (fee > recovery * 0.60 → BLOCK) + Garantía Día 55 con comando `validate-guarantee`.
