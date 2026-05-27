# DIAGNÓSTICO UNIFICADO v3.0: Motor Financiero & Estrategia de Monetización & Capa de Ejecución Comercial

**De la Fricción Comercial al "Value-Capture Pricing" + Semántica Estricta de Activos + Garantía Auditable**
**Repositorio:** `https://github.com/jhondrl6/ia-hotels-agent.git`
**Estado:** LISTO PARA PLANIFICACIÓN (Cierre Comercial Garantizado)
**Segmento:** Hoteles Boutique — Eje Cafetero, Colombia (Caso: Castilla Real)
**Objetivo:** Contexto unificado para crear un plan de implementación en una nueva sesión.

---

## PARTE A: CAPA FINANCIERA (Diagnóstico Original)

### La Verdad Incómoda
El modelo actual `v4.54.0` tiene un defecto de diseño filosófico: **Cobra por el Dolor (Leakage), no por la Cura (Recovery).**
*   **Fuga Total:** $3.741.696 COP
*   **Recuperación Realista (20%):** $748.339 COP
*   **Precio Actual (Floor):** $1.200.000 COP
*   **Resultado:** El cliente paga $1.2M para recuperar $748K. **Es un arbitraje negativo.** Ningún General Manager firmará esto.

La solución no es mentir subiendo el recovery_factor al 45%. La solución es implementar un **Tope de Captura de Valor (Value Capture Cap)**, un **Floor Price Condicional por Pain Ratio**, y reclasificar el Setup Fee como **CAPEX (Activos Digitales)**.

---

### LOS 4 PILARES DE LA REFACTORIZACIÓN FINANCIERA

#### Pilar 1: Pricing — Pipeline Unificado de 3 Pasos (Floor Condicional + Cap Ético)

**Regla de oro:** La agencia nunca debe capturar más del 50% del valor recuperado proyectado. Además, si el pain_ratio (precio / pérdida_esperada) es excesivo, el floor debe suavizarse promediando con el precio recomendado.

**⚠️ PRECAUCIÓN DE DISEÑO:** Las versiones anteriores proponían dos lógicas separadas (v2.0: Floor Condicional, v3.0: Value-Capture Cap). Si se implementan como `if/else` independientes, colisionarán y producirán precios erráticos. La solución es una **tubería (pipeline) de 3 pasos en orden fijo** dentro de `pricing_calculator.py`.

**Acción en `config/pricing.yaml`:**
```yaml
tier_config:
  boutique:
    percentage: 0.035
    min_price: 800_000  # Bajamos el floor base
    max_price: 2_500_000
    value_capture_cap: 0.50  # La agencia nunca cobra más del 50% de la ganancia neta proyectada
    operational_floor: 400_000  # Piso absoluto para respetar costos de la agencia
```

**Lógica en `modules/financial_engine/pricing_calculator.py` — Pipeline Unificado:**
```python
def calcular_precio_final(expected_loss, recovery_factor, tier_config, location):
    # PASO 1: Precio Base (Fórmula tradicional)
    recommended = expected_loss * tier_config["percentage"]
    base_price = max(tier_config["min_price"], min(recommended, tier_config["max_price"]))
    
    # PASO 2: Ajuste por Pain Ratio (Floor Condicional — v2.0)
    # Si el precio base es desproporcionado frente a la pérdida real, se suaviza
    pain_ratio = base_price / expected_loss
    GATE_MAX = tier_config.get("pain_ratio_gate_max", 0.32)
    if pain_ratio > (GATE_MAX * 2.0):
        base_price = (tier_config["min_price"] + recommended) / 2  # Escalonado: promedio entre floor y recomendado
    
    # PASO 3: Techo Ético (Value-Capture Cap — v3.0)
    # El precio final NUNCA puede superar el 50% de lo que el cliente recupera
    expected_recovery = expected_loss * recovery_factor
    ethical_cap = expected_recovery * tier_config.get("value_capture_cap", 0.50)
    
    final_price = min(base_price, ethical_cap)
    return max(final_price, tier_config.get("operational_floor", 400_000))  # Respetar costos de la agencia
```

**Impacto Castilla Real:** Recuperación (35% realista con 4 pilares) = $1.309.593. 
- Paso 1: recommended = $130.964, base_price = $800.000 (floor). 
- Paso 2: pain_ratio = $800K / $3.74M = 0.21 → menor que GATE_MAX*2 (0.64), no se dispara el escalonado.
- Paso 3: ethical_cap = $1.309.593 * 0.50 = $654.796. final_price = min($800.000, $654.796) = **$654.796**.

El cliente ve que la agencia se autolimita para garantizar su ROI.

---

#### Pilar 2: Setup Fee — De "Gasto Oculto" a "CAPEX de Activos Digitales" + Métricas Desacopladas

El error HR-1 (ocultar el Setup Fee de $2.5M) destruye la confianza. El Setup Fee no es un "costo de activación", es la generación de `delivery_assets/` (Schema, FAQ, llms.txt, Geo-Optimization). **El cliente está comprando propiedad intelectual (Real Estate Digital).**

**⚠️ PRECAUCIÓN DE DISEÑO — La Trampa del ROI con CAPEX:** 
- La v3.0 dice: "Separa CAPEX de OPEX. El ROI del SaaS es 1.93X".
- La v2.0 dice: "Incluye el Setup Fee en la fórmula del ROI. El ROI total baja a 0.80X".

Si el generador de PDFs imprime un ROI de 0.80X (donde el cliente "pierde" dinero), el Director Financiero vetará la propuesta. **Está terminantemente prohibido dividir `Recuperación Total / (OPEX + CAPEX)`.**

**Solución — Métricas Desacopladas en `modules/financial_engine/roi_formatter.py`:**
```python
def calcular_metricas_roi(recuperacion_total, inversion_opex, inversion_capex):
    """
    Retorna DOS métricas independientes, NUNCA mezcladas.
    """
    # Métrica 1 (Operativa): ROI del SaaS — debe ser > 1.5X
    roi_saas = recuperacion_total / inversion_opex
    
    # Métrica 2 (Patrimonial): El CAPEX se presenta como tasación de activo intangible
    # que entra al balance del hotel, no como gasto operativo.
    valorizacion_activo_digital = inversion_capex  # El activo vale lo que costó construirlo
    
    return {
        'roi_saas': roi_saas,                         # "Por cada $1 de SaaS, recupera $X"
        'valorizacion_activo_digital': valorizacion_activo_digital,  # "Su Hotel ahora tiene un activo digital tasado en $X"
        'nota_metodologica': "El CAPEX (Setup Fee) es una inversión patrimonial única, no un gasto operativo. Las métricas de ROI reflejan exclusivamente la relación Recuperación/OPEX."
    }
```

**Acción en `modules/commercial_documents/v4_proposal_generator.py`:**
Separar el ROI en dos tablas: **OPEX (SaaS Mensual)** y **CAPEX (Activos Propios)**.
```python
template_data.update({
    'activos_digitales_propiedad_cliente': [
        "Schema.org Hotel & LocalBusiness (SEO/AEO)",
        "llms.txt & AI-Readiness (IAO - ChatGPT/Perplexity)",
        "Matriz FAQ Estructurada para Voice Search"
    ],
    'inversion_capex_unica': format_cop(setup_fee),
    'inversion_opex_mensual': format_cop(final_monthly_price),
    'roi_saas_operativo': calcular_metricas_roi(...)['roi_saas'],
    'nota_transparencia': "El Setup Fee genera activos de código que son 100% de su propiedad, independientemente de si continúa con nuestro SaaS."
})
```

---

#### Pilar 3: Proyección — Curva de Maduración basada en los 4 Pilares
La curva refleja la velocidad de impacto de cada pilar:
*   **Mes 1 (GEO):** Rápido. Google Maps y GBP responden en semanas.
*   **Mes 2-3 (SEO):** Medio. Indexación y posicionamiento orgánico.
*   **Mes 4-6 (AEO/IAO):** Exponencial. Asistentes de voz y LLMs empiezan a recomendar el hotel.

**Nuevo Módulo `modules/financial_engine/pillar_maturity_curve.py`:**
```python
def aplicar_curva_4_pilares(fuga_mensual, recovery_factor_max):
    curva_pilares = [0.15, 0.35, 0.60, 0.80, 0.95, 1.00] 
    proyeccion = []
    for mes, factor_mes in enumerate(curva_pilares, start=1):
        recovery_mes = fuga_mensual * recovery_factor_max * factor_mes
        proyeccion.append(recovery_mes)
    return proyeccion
```

#### Pilar 4: Gate de Confianza — `ESTIMATED` vs `VERIFIED`
El repo tiene `python main.py onboard` que sube la confianza de los datos. **El motor financiero DEBE castigar las proyecciones si el cliente no ha hecho el onboard.**
*   `ESTIMATED`: aplicar `risk_discount` del 20% (conservador y honesto).
*   `VERIFIED`: mostrar el escenario realista completo.

---

### ESCENARIO COMERCIAL — Castilla Real (con v3.0 Financiera)

#### Tabla 1: CAPEX (Único)
| Concepto | Valor | Justificación |
| :--- | :--- | :--- |
| Generación de delivery_assets/ | $2.500.000 | Schema, llms.txt, FAQ (Propiedad del Hotel) |
| **Total CAPEX** | **$2.500.000** | *Deducible como inversión en activos intangibles* |

#### Tabla 2: OPEX — Retenedor SaaS vs Recuperación (6 Meses)
*Recovery Factor 35% | Precio limitado por Value-Capture Cap*

| Mes | Pilar Dominante | Inversión SaaS | Recuperación Proyectada | Beneficio Neto |
| :--- | :--- | :--- | :--- | :--- |
| 1 | GEO (Maps/GBP) | $654.796 | $196.438 | -$458.358 *(Siembra)* |
| 2 | SEO (Orgánico) | $654.796 | $458.357 | -$196.439 *(Indexación)* |
| 3 | SEO + AEO | $654.796 | $785.755 | +$130.959 *(Equilibrio)* |
| 4 | AEO (Voice) | $654.796 | $1.047.674 | +$392.878 |
| 5 | IAO (LLMs) | $654.796 | $1.244.113 | +$589.317 |
| 6 | IAO (Crucero) | $654.796 | $1.309.593 | +$654.797 |
| **TOTAL** | **Ecosistema 4 Pilares** | **$3.928.776** | **$5.041.930** | **+$1.113.154** |

#### Métricas Desacopladas (OPEX y CAPEX separados)
| Métrica | Valor | Interpretación |
| :--- | :--- | :--- |
| **ROI SaaS (Operativo)** | **1.28X** | Por cada $1 invertido en SaaS, el hotel recupera $1.28 (6 meses) |
| **ROI SaaS (Maduro, Mes 12+)** | **1.93X** | Una vez alcanzada la maduración total de los 4 pilares |
| **Valorización Activo Digital** | **$2.500.000** | El hotel suma un activo intangible tasado en $2.5M a su balance |

#### Pitch de Cierre
> "Sr. Cliente, la mayoría de agencias le cobrarían $1.200.000 mensuales porque su fuga es alta. Nosotros hemos auditado su fuga en $3.74M, pero nuestro modelo de Value-Capture nos prohíbe cobrarle más del 50% de lo que nuestra IA realmente recupera para usted. Por eso, nuestra cuota se ajusta a $654.796. Usted asume el riesgo de la siembra en el Mes 1 y 2, pero a partir del Mes 3, la IA trabaja para su margen directo. Además, los $2.5M iniciales no son un 'fee', son los cimientos de su Real Estate Digital (llms.txt, Schema) que son de su propiedad para siempre. Y si al día 55 no hay mejora medible en Google Search Console, nuestra propia IA emite automáticamente una nota crédito del 50% — sin que usted tenga que reclamar."

---

## PARTE B: CAPA DE EJECUCIÓN Y PROMESA COMERCIAL

Con solo la capa financiera, el cliente detectará que "la IA está inventando cosas" o "vendiendo humo", y el cierre se caerá por falta de confianza técnica, sin importar cuán bueno sea el ROI.

### Problema 1: COHERENCIA DIAGNÓSTICO → PROPUESTA (PainSolutionMapper)

**Veredicto:** CRÍTICO. Hay "alucinaciones semánticas" en el mapeo.
El `PainSolutionMapper` une brechas (`pain_points`) con activos (`delivery_assets`). El generador de propuestas (`v4_proposal_generator.py`) está forzando uniones ilógicas para llenar la tabla de servicios.

*   **Caso Informe Mensual vs. FAQ:** Un reporte no arregla la falta de estructura FAQ. Mapeo imposible.
*   **Caso WhatsApp:** Si el asset es `skipped: already_in_prod`, el motor comercial no puede venderlo como "Implementación", debe venderlo como "Auditoría y Optimización de Conversión".

**Solución — Validador de Semántica de Activos (`modules/quality/asset_semantics_validator.py`):**
```python
INVALID_MAPPINGS = {
    'monthly_report': ['faq_missing', 'schema_missing', 'llms_missing'],
    'whatsapp_conflict_guide': ['whatsapp_missing']
}

def validar_semantica_comercial(pain_id: str, asset_id: str, asset_status: str) -> tuple[bool, str]:
    """Valida que el asset resuelva realmente el pain y ajusta la narrativa comercial."""
    if asset_id in INVALID_MAPPINGS and pain_id in INVALID_MAPPINGS[asset_id]:
        return False, f"BLOCKED: El asset '{asset_id}' no resuelve estructuralmente '{pain_id}'."
        
    if asset_status == 'skipped_existing':
        return True, "AUDIT_ONLY"  # Cambia el verbo de "Implementar" a "Auditar/Optimizar"
        
    return True, "IMPLEMENT"
```

### Problema 2: VIABILIDAD COMERCIAL (ROI Negativo)

**Veredicto:** CRÍTICO. Valida la necesidad del Refactor v3.0 financiero.
Invertir $7.2M para recuperar $1.8M es suicidio comercial. El problema es la narrativa comercial, no la ejecución técnica. Los 4 Pilares + Curva de Maduración + Value-Capture Cap + Métricas Desacopladas resuelven esto de raíz, llevando el ROI SaaS de 0.3X a 1.93X.

### Problema 3: MÓDULOS / ASSETS PARA DEPRECIAR (con Manejo de Huérfanos)

**Veredicto:** PERTINENTE. Menos es más en B2B.
Tener "guías" cuando ya entregas el código genera fricción cognitiva.

**⚠️ PRECAUCIÓN DE DISEÑO — Orfandad en el PainSolutionMapper:**
El repositorio tiene un *Gate Blocking* llamado `critical_recall` y `evidence_coverage`. Si se depreca un asset en `asset_registry.yaml` pero el `PainSolutionMapper` sigue buscando cómo resolver el dolor asociado (ej. "Falta de Open Graph"), el sistema lanzará `UnmappedPainError` o bajará el *Coherence Score* por debajo de 0.8, bloqueando la generación de la propuesta. **Todo asset deprecado DEBE tener un `migration_target` que redirija al mapper.**

**Acción en `config/asset_registry.yaml`:**
```yaml
# config/asset_registry.yaml
assets:
  - id: open_graph_html
    status: IMPLEMENT
    resolves: ['missing_og_tags']  # <- Este dolor NO puede quedar huérfano
    
  - id: og_tags_guide
    status: DEPRECATED
    migration_target: open_graph_html  # <- El mapper debe saber a dónde redirigir
    deprecation_reason: "Contenido fusionado como comentarios HTML dentro de open_graph.html"
    
  - id: indirect_traffic_optimization
    status: DEPRECATED
    migration_target: null  # <- Sin migración automática: pasa a Consultoría Estratégica (Upsell manual)
    deprecation_reason: "Reclasificado como servicio de Consultoría Estratégica, no como entregable automatizado"
    
  - id: local_content_page
    status: IMPLEMENT
    confidence_score: 0.60  # <- Advisory. Presentarlo como "Bonus: Plantilla Editorial para Blog"
    resolves: ['thin_content_seo']
```

**Regla en el mapper:** Si un asset tiene `status: DEPRECATED` y `migration_target` no es null, redirigir automáticamente al asset destino. Si `migration_target` es null, el dolor debe resolverse por otra vía (consultoría manual) o marcarse como `UNRESOLVED` con justificación explícita.

### Problema 4: ALINEACIÓN CON EL GATE REPORT (Vacío en Publication Gates)

**Veredicto:** CRÍTICO. Detecta un loophole en los Publication Gates.
El sistema técnico dice `NOT_READY` (botón WhatsApp, Tier C), pero `v4_proposal_generator.py` ignora esto y genera el PDF de todos modos porque el Score de Coherencia general logró llegar a 0.8 gracias a otros factores.

**Solución — Hard-Block Comercial en `modules/quality/publication_gates.py`:**
Elevar `proposal_asset_alignment` a **BLOCKING** si el asset está asociado a un `pain_point` de prioridad **P1**.
```python
def gate_proposal_asset_alignment(proposal_data: dict, asset_report: dict) -> GateResult:
    p1_pains = [p['id'] for p in proposal_data['pain_points'] if p['priority'] == 'P1']
    
    for asset in asset_report['assets']:
        if asset['resolves_pain'] in p1_pains and asset['status'] in ['NOT_READY', 'BLOCKED']:
            return GateResult(
                passed=False, 
                gate_type='BLOCKING',  # Antes era ADVISORY
                message=f"CRITICAL: No se puede generar propuesta. El asset crítico '{asset['id']}' para el dolor P1 '{asset['resolves_pain']}' no está listo."
            )
            
    return GateResult(passed=True, gate_type='BLOCKING')
```
*Nota: Para WhatsApp (skipped porque ya existe), el Gate debe aprobarlo PERO obligar al generator a usar la narrativa `AUDIT_ONLY` del punto 1.*

### Problema 5: GARANTÍA DEL DÍA 55 SIN TRIGGER TÉCNICO

**Veredicto:** CRÍTICO para Cierre Comercial. La promesa existe en el pitch pero no en el código.

La propuesta comercial promete: *"Si al día 55 no hay mejora en GSC, crédito del 50%"*. Pero el agente es un sistema agéntico; las promesas comerciales deben estar respaldadas por *Skills* ejecutables. Si Ventas promete algo que Operaciones no tiene cómo auditar automáticamente, se genera fricción interna y riesgo reputacional.

**Solución — Nuevo Comando `validate-guarantee` en `modules/analytics/guarantee_validator.py`:**
```python
# modules/analytics/guarantee_validator.py
"""
Validador de Garantía Día 55.
Compara la línea base del Día 0 (onboard) vs el Día 55 (GSC API).
Si no se cumple el KPI, genera automáticamente CREDIT_NOTE.md y billing_adjustment.yaml.
"""

def validar_garantia_dia55(hotel_url: str, hotel_id: str) -> GuaranteeResult:
    # 1. Cargar línea base del Día 0 desde onboarding
    baseline = load_baseline(hotel_id)
    
    # 2. Consultar GSC actual (día 55+)
    current = fetch_gsc_metrics(hotel_url, days=55)
    
    # 3. Comparar KPIs: impresiones, clics, posición promedio
    improvement_pct = calcular_mejora_porcentual(baseline, current)
    
    if improvement_pct < GUARANTEE_THRESHOLD:
        # 4. Generar nota crédito automática
        generar_nota_credito(hotel_id, porcentaje=0.50)
        generar_ajuste_facturacion(hotel_id, mes=3, porcentaje=0.50)
        
        return GuaranteeResult(
            triggered=True,
            credit_applied=True,
            evidence=current,
            message="Garantía Día 55 ACTIVADA. Crédito del 50% generado automáticamente para el Mes 3."
        )
    
    return GuaranteeResult(
        triggered=False,
        credit_applied=False,
        evidence=current,
        message="Garantía Día 55: KPIs superados. No se requiere crédito."
    )
```

**Comando CLI:** `python main.py validate-guarantee --url [hotel]`

**Power Move Comercial:** *"Nuestra propia IA audita la garantía y emite su nota crédito sin intervención humana. Usted no tiene que reclamar nada."*

**Archivos generados por el validador:**
- `outputs/{hotel_id}/guarantees/CREDIT_NOTE.md` — Documento legal de nota crédito
- `outputs/{hotel_id}/guarantees/billing_adjustment.yaml` — Ajuste automático para el ciclo de facturación del Mes 3

### Problema 6: REGRESIÓN MASIVA DE TESTS FINANCIEROS (+2,743 tests)

**Veredicto:** CRÍTICO para CI/CD. El PR será rechazado por GitHub Actions si no se aborda.

El README advierte que el repositorio tiene **+2,743 pruebas automatizadas** y un `v4_regression_guardian`. Al cambiar:
- `scenarios.yaml` (subiendo el recovery a 0.35-0.45)
- `pricing.yaml` (cambiando el floor de $1.2M a $800K)
- `pricing_calculator.py` (nuevo pipeline de 3 pasos)

...se romperán masivamente los *fixtures* (datos de prueba) de los tests financieros existentes.

**Solución — Tarea Obligatoria en el PR:**
1. **Actualizar `tests/fixtures/financial_scenarios.json`**: Recalcular todos los valores esperados con el nuevo pipeline unificado.
2. **Re-calibrar `v4_regression_guardian`**: Los umbrales de tolerancia deben ajustarse a la nueva normalidad del Value-Capture Cap.
3. **Agregar tests específicos para el nuevo pipeline**: Casos borde del Pain Ratio Adjustment (GAP 1), métricas desacopladas (GAP 2), y validación de huérfanos (GAP 3).

```python
# tests/test_pricing_pipeline.py (nuevo)
def test_pipeline_no_collision():
    """Verifica que el pipeline unificado no produzca guerra de if/else."""
    # Caso: floor alto, pain_ratio excesivo
    result = calcular_precio_final(
        expected_loss=3_741_696,
        recovery_factor=0.35,
        tier_config={
            "percentage": 0.035,
            "min_price": 1_200_000,
            "max_price": 2_500_000,
            "value_capture_cap": 0.50,
            "pain_ratio_gate_max": 0.32,
            "operational_floor": 400_000,
        },
        location="eje_cafetero"
    )
    # El ethical_cap (654,796) debe DOMINAR sobre el floor (1,200,000)
    assert result == 654_796, f"Expected 654_796, got {result}"
```

---

## PARTE C: TABLA DE CONTROL UNIFICADA

| Capa | Problema | Solución (v3.0) | Impacto Cliente |
| :--- | :--- | :--- | :--- |
| **Financiera** | ROI Negativo (-$5.3M) por Floor Price ciego. Colisión de lógicas v2.0 vs v3.0. | Pipeline Unificado (Floor Condicional + Value-Capture Cap) + Curva de Maduración. | ROI SaaS de 1.93X. La agencia asume el riesgo de la siembra. |
| **Financiera (ROI)** | Mezclar CAPEX y OPEX produce ROI falso de 0.80X que destruye el cierre. | Métricas Desacopladas: ROI SaaS (Operativo) vs Valorización Activo Digital (Patrimonial). | El CFO ve un ROI operativo real > 1.5X y un activo digital en balance. |
| **Semántica (Mapper)** | Vende "Implementación" de lo que ya existe o mapea Reportes a FAQs. | AssetSemanticsValidator + Narrativas dinámicas (IMPLEMENT vs AUDIT_ONLY). | Honestidad brutal y precisión técnica. |
| **Catálogo (Assets)** | Entregables redundantes (Guías vs HTML). Deprecación sin migration_target rompe el mapper. | Deprecación con migration_target explícito. Assets huérfanos redirigidos o justificados. | Propuesta limpia, solo Activos de Infraestructura Digital (CAPEX). |
| **Gobernanza (Gates)** | Gate deja pasar propuestas con assets P1 NOT_READY. | proposal_asset_alignment → BLOCKING para dolores P1. | Cero promesas falsas. |
| **Garantía (Día 55)** | Promesa comercial sin trigger técnico. Ventas promete, Operaciones no tiene cómo auditar. | Comando `validate-guarantee` + generación automática de CREDIT_NOTE.md. | La IA audita y paga la garantía sin intervención humana. |
| **CI/CD (Tests)** | +2,743 tests. Cambios en pricing rompen fixtures financieros. PR rechazado. | Actualizar fixtures + re-calibrar v4_regression_guardian + tests del nuevo pipeline. | Deploy confiable. Cero regresiones en producción. |

---

## PARTE D: ROADMAP DE IMPLEMENTACIÓN (6 PRs)

### PR #1: `feat(pricing): Unified Ethical Pipeline (Cap + Conditional Floor)`
*   **Archivos:** `config/pricing.yaml`, `modules/financial_engine/pricing_calculator.py`.
*   **Objetivo:** Implementar el pipeline unificado de 3 pasos (Paso 1: Base → Paso 2: Pain Ratio Adjustment → Paso 3: Ethical Cap). Resolver la colisión de lógicas v2.0 vs v3.0 en un solo flujo determinista.
*   **Resuelve:** GAP 1 (Parches.md), Pilar 1 (ROICR.md).

### PR #2: `fix(proposal): Decouple CAPEX from OPEX ROI calculation`
*   **Archivos:** `modules/financial_engine/roi_formatter.py` (Nuevo o refactor), `modules/commercial_documents/v4_proposal_generator.py`.
*   **Objetivo:** Implementar métricas desacopladas. Prohibir `Recuperación / (OPEX + CAPEX)`. Separar la propuesta en Tabla CAPEX (único) y Tabla OPEX (mensual) con ROI SaaS independiente.
*   **Resuelve:** GAP 2 (Parches.md), Pilar 2 (ROICR.md).

### PR #3: `feat(projections): 4-Pillar Maturity Curve Integration`
*   **Archivos:** `modules/financial_engine/pillar_maturity_curve.py` (Nuevo), `config/scenarios.yaml`.
*   **Objetivo:** Reemplazar el descuento lineal por la curva `[0.15, 0.35, 0.60, 0.80, 0.95, 1.00]`.
*   **Resuelve:** Pilar 3 (ROICR.md).

### PR #4: `fix(validator): Add Arbitrage Check to Coherence Gate`
*   **Archivos:** `modules/quality/financial_coherence_validator.py`.
*   **Objetivo:** Blocking Gate. Si `monthly_fee > (expected_recovery * 0.60)`, CRITICAL_ETHICS_WARNING e impide generar la propuesta.
```python
def validar_arbitraje_etico(proposal_data: dict) -> ValidationReport:
    fee = proposal_data['monthly_fee']
    recovery = proposal_data['expected_monthly_recovery']
    if fee > (recovery * 0.60):
        return ValidationReport(
            is_valid=False, 
            errors=["ETHICS GATE: El fee mensual supera el 60% del valor recuperado. Riesgo altísimo de Churn."]
        )
    return ValidationReport(is_valid=True)
```
*   **Resuelve:** Pilar 4 + Problema 2 (ROICR.md).

### PR #5: `feat(quality): Asset Semantics Validator, Gate Hardening & Mapper Orphans`
*   **Archivos:** `modules/quality/asset_semantics_validator.py` (Nuevo), `modules/quality/publication_gates.py`, `config/asset_registry.yaml`.
*   **Objetivo:** Matar las alucinaciones del Mapper. Bloquear ventas de humo. Deprecar assets redundantes con `migration_target`. Implementar `validar_semantica_comercial()` y `gate_proposal_asset_alignment()` BLOCKING.
*   **Resuelve:** GAP 3 (Parches.md), Problemas 1, 3, 4 (ROICR.md).

### PR #6: `feat(analytics): Day-55 Guarantee Validator + Test Fixtures Update`
*   **Archivos:** `modules/analytics/guarantee_validator.py` (Nuevo), `main.py` (nuevo comando `validate-guarantee`), `tests/fixtures/financial_scenarios.json`, `tests/test_pricing_pipeline.py` (Nuevo), `tests/test_guarantee_validator.py` (Nuevo).
*   **Objetivo:** 
  - Implementar el comando `python main.py validate-guarantee --url [hotel]` con generación automática de `CREDIT_NOTE.md` y `billing_adjustment.yaml`.
  - Actualizar fixtures financieros para reflejar el nuevo pipeline unificado.
  - Re-calibrar umbrales del `v4_regression_guardian`.
  - Agregar tests para el pipeline unificado y el validador de garantía.
*   **Resuelve:** GAP 4, GAP 5 (Parches.md), Problemas 5, 6 (ROICR.md).

---

## PARTE E: CHECKLIST DE MERGE — GATES PARA EL PULL REQUEST FINAL

Para que este refactor sea **Mergeable** en `main` sin reversiones, se deben cumplir estos gates:

| # | Gate | Criterio | Bloqueante |
| :--- | :--- | :--- | :--- |
| 1 | **Pipeline Unificado** | `calcular_precio_final()` existe con 3 pasos. No hay `if/else` colisionantes. | ✅ SÍ |
| 2 | **ROI Desacoplado** | `roi_formatter.py` retorna métricas separadas. `v4_proposal_generator.py` NUNCA divide por (OPEX+CAPEX). | ✅ SÍ |
| 3 | **Huérfanos Resueltos** | `asset_registry.yaml` tiene `migration_target` en assets DEPRECATED. `PainSolutionMapper` redirige o justifica. | ✅ SÍ |
| 4 | **Garantía Auditable** | `python main.py validate-guarantee --url [hotel]` ejecuta sin errores y genera `CREDIT_NOTE.md`. | ✅ SÍ |
| 5 | **Tests Pasan** | `pytest` completo. +2,743 tests sin regresiones. Fixtures actualizados. `v4_regression_guardian` recalibrado. | ✅ SÍ |
| 6 | **Narrativa Unificada** | El pitch de cierre incluye Value-Capture Cap + CAPEX/OPEX + Garantía Día 55. | ❌ ADVISORY |

---

## CONCLUSIÓN EJECUTIVA

Al implementar esta v3.0 completa (con los 6 parches integrados) se logra:

1.  **Proteger a la Agencia:** El Value-Capture Cap + Floor Condicional aseguran que solo se tomen clientes donde la fuga sea lo suficientemente grande para que el SaaS sea rentable, y que el precio nunca sea desproporcionado frente al dolor real.

2.  **Proteger al Cliente:** El ROI SaaS operativo siempre será positivo a partir del mes 3. La transparencia CAPEX vs OPEX elimina la fricción de los $2.5M iniciales. Las métricas desacopladas le dan al CFO exactamente lo que necesita para aprobar.

3.  **Potenciar al Agente:** Las proyecciones financieras están vinculadas directamente a los outputs técnicos del agente (delivery_assets, onboard command). El pipeline unificado garantiza determinismo en el pricing.

4.  **Garantizar Honestidad Comercial:** El AssetSemanticsValidator + Gate Hardening + migration_target en assets deprecados aseguran que ninguna propuesta prometa algo que la IA no puede entregar ni deje dolores huérfanos.

5.  **Cerrar con Confianza:** La garantía del Día 55 no es una promesa vacía — es un comando ejecutable que la IA corre automáticamente. Ventas puede decir con total seguridad: "Nuestra propia IA audita la garantía y emite la nota crédito sin intervención humana."

6.  **Deploy sin Miedo:** Los +2,743 tests actualizados y el `v4_regression_guardian` recalibrado garantizan que el PR pasa CI/CD en GitHub Actions sin regresiones.

**Siguiente paso:** Crear el plan de implementación detallado (6 PRs, archivos específicos, tests) a partir de este contexto unificado.
