# 📚 Domain Primer — IA Hoteles Agent

> [!NOTE]
> **Propósito**: Base de conocimiento comprimida del dominio "hotelería digital".
> Consultar para entender conceptos de negocio y su mapeo a código.
> 
> **Versión del sistema**: 4.0.0 | **Codename**: Sistema de Confianza | **Generado desde**: `modules/`

---

## Nueva Arquitectura v4.0

La versión 4.0 representa una transformación fundamental: de "generador de diagnósticos" a "sistema de inteligencia con niveles de certeza explícitos".

### Módulos Principales

| Módulo | Responsabilidad | Clases/Funciones Clave |
|--------|-----------------|------------------------|
| **data_validation** | Validación cruzada de datos entre múltiples fuentes | `CrossValidator`, `ConfidenceLevel`, `WhatsAppValidator`, `ADRValidator` |
| **financial_engine** | Cálculo de escenarios financieros en lugar de cifras exactas | `ScenarioCalculator`, `HotelFinancialData`, `FinancialScenario` |
| **orchestration_v4** | Flujo de onboarding en dos fases | `TwoPhaseOrchestrator`, `OnboardingController`, `OnboardingState` |
| **asset_generation** | Generación condicional de assets con gates de calidad | `ConditionalGenerator`, `PreflightChecker`, `AssetGenerator` |
| **commercial_documents** | Generación de diagnóstico y propuesta comercial v4.1.0 | `V4DiagnosticGenerator`, `V4ProposalGenerator`, `CoherenceValidator`, `PainSolutionMapper` |

### Tipos de Escenario Financiero

| Escenario | Probabilidad | Base de Cálculo |
|-----------|--------------|-----------------|
| Conservador | 70% | Peor caso plausible |
| Realista | 20% | Meta esperada |
| Optimista | 10% | Mejor caso |

---

## Taxonomía de Confianza

Todos los datos procesados por el sistema se clasifican según su nivel de confiabilidad:

| Level | Icon | Sources | Confidence | Use in Assets |
|-------|------|---------|------------|---------------|
| **VERIFIED** | 🟢 | 2+ fuentes coinciden | ≥ 0.9 | Yes - usar directamente |
| **ESTIMATED** | 🟡 | 1 fuente o benchmark | 0.5 - 0.9 | Yes con disclaimer |
| **CONFLICT** | 🔴 | Fuentes contradictorias | < 0.5 | No - requiere revisión manual |

### Uso en Código

```python
from modules.data_validation import CrossValidator, ConfidenceLevel

cv = CrossValidator()
result = cv.validate_whatsapp(
    web_value="+573113973744",
    gbp_value="+573113973744"
)
# Resultado: ConfidenceLevel.VERIFIED (confidence=1.0)
```

---

## Flujo de Dos Fases (Two-Phase Flow)

```
FASE 1: HOOK (Automático)
─────────────────────────
Input: URL del hotel
  ↓
Benchmark Regional → Rango Estimado ($X - $Y)
  ↓
Output: Hook con disclaimer de estimación
        "¿Quiere precisar esta cifra?"
        Progreso: 30%

FASE 2: INPUT (Usuario + Validación)
─────────────────────────────────────
Input: 5 datos mínimos del hotel
  - Habitaciones
  - Tarifa promedio real (ADR)
  - % Ocupación
  - Presencia en OTAs
  - % Canal Directo
  ↓
Validación Cruzada OBLIGATORIA:
  - WhatsApp: web vs GBP vs input
  - ADR: benchmark vs input
  - Datos operativos: input usuario
  ↓
¿Conflictos detectados?
  ├─ SÍ → Reporte detallado, revisión manual
  └─ NO → Escenarios financieros calculados
  ↓
Output: Proyecciones con intervalos
        Progreso: 100%
        Listo para assets: SÍ/NO
```

### Estados del Onboarding

| Estado | Descripción | Progreso |
|--------|-------------|----------|
| `INIT` | Inicialización | 0% |
| `PHASE_1_HOOK` | Hook generado con benchmark | 30% |
| `PHASE_2_INPUT` | Esperando datos del usuario | 60% |
| `VALIDATION` | Validando datos cruzados | 75% |
| `CALCULATION` | Calculando escenarios | 90% |
| `COMPLETE` | Listo para assets | 100% |

---

## Glosario del Dominio

### Conceptos de Negocio v4.0

| Término | Definición | Mapeo a Código |
|---------|------------|----------------|
| **Hook** | Fase 1: Estimación inicial basada en benchmarks. Rango amplio con disclaimer. | `orchestration_v4.OnboardingController.start_onboarding()` |
| **Validación Cruzada** | Comparación de datos entre múltiples fuentes (web, GBP, input usuario). | `data_validation.CrossValidator` |
| **Escenario Financiero** | Proyección con probabilidad asignada (Conservador/Realista/Optimista). | `financial_engine.ScenarioCalculator.calculate_scenarios()` |
| **Preflight Check** | Gate de calidad antes de generar assets. Verifica confianza mínima. | `asset_generation.PreflightChecker` |
| **Plan Maestro** | Contexto de benchmark (ya no input directo). Define rangos esperados. | `data/benchmarks/` |
| **GBP Activation** | Add-on para hoteles con Perfil de Negocio Google inactivo. | Regla de validación GBP |
| **Motor de Reservas** | Sistema de booking integrado. Su ausencia es fuga crítica. | `web_scraper._detectar_motor_reservas()` |
| **Optimización de Cercanía** | Técnica SEO local vinculando hotel con atracciones cercanas. | Schema.org `description`, `keywords` |
| **Entrenamiento 3 Agentes** | Proceso de optimización para ChatGPT, Perplexity y Gemini. | `hotel-schema.json`, FAQs validadas |

### Conceptos Técnicos v4.0

| Término | Definición | Ubicación |
|---------|------------|-----------|
| **Confidence Score** | Valor 0.0-1.0 indicando confiabilidad del dato. | `data_validation` |
| **Dry-Run** | Modo validación sin aplicar cambios reales. | `deployer/manager.py` |
| **WPCode** | Plugin WordPress requerido para inyectar código vía API. | Externo |
| **Factor de Captura** | % del mercado digital capturable (contexto, no input). | Benchmarks regionales |

---

## Mapeo de Módulos (v3.x → v4.0)

| Componente v3.x | Componente v4.0 | Notas |
|-----------------|-----------------|-------|
| `decision_engine.py` | `financial_engine/` | De motor de reglas a calculadora de escenarios |
| `delivery/manager.py` | `asset_generation/` | Generación condicional con preflight checks |
| `web_scraper.py` (solo) | `data_validation/` | Validación cruzada obligatoria |
| `onboarding.py` | `orchestration_v4/` | Flujo explícito de dos fases |
| Benchmarks como input | Benchmarks como contexto | Rangos, no cifras exactas |
| Generación automática | Generación condicional | Gates de calidad antes de assets |

---

## Generación Condicional de Assets

Los assets solo se generan si pasan los gates de calidad:

### Preflight Checks

| Asset | Confianza Mínima | Status si pasa | Status si falla |
|-------|------------------|----------------|-----------------|
| WhatsApp Button | ≥ 0.9 | `boton_whatsapp.html` | `ESTIMATED_boton_whatsapp.html` o bloqueado |
| FAQ Page | ≥ 0.7 | `faq_page.html` | `ESTIMATED_faq_page.html` |
| Hotel Schema | ≥ 0.8 | `hotel_schema.json` | Bloqueado |

### Nomenclatura de Archivos

- **PASSED**: `boton_whatsapp.html`
- **WARNING**: `ESTIMATED_boton_whatsapp.html` (con disclaimer)
- **BLOCKED**: No generar, requiere revisión manual

---

## Casos de Borde Importantes

### Caso 1: Conflicto de WhatsApp
**Comportamiento**: Web muestra +57, GBP muestra diferente.
**Resultado**: ConfidenceLevel.CONFLICT, asset bloqueado, reporte generado.

### Caso 2: ADR fuera de rango benchmark
**Comportamiento**: Usuario reporta ADR $800k, benchmark dice $300k-$400k.
**Resultado**: Flag de conflicto, solicitar confirmación.

### Caso 3: Fase 2 sin datos suficientes
**Comportamiento**: Usuario no proporciona % canal directo.
**Resultado**: Usar benchmark regional como ESTIMATED, marcar en metadata.

### Caso 4: Landing de proveedor SaaS
**Comportamiento**: Filtro Anti-SaaS descarta como falso positivo.
**Código**: `web_scraper._es_landing_proveedor_saas()`

### Caso 5: Confianza insuficiente para assets
**Comportamiento**: Datos conflictivos detectados.
**Resultado**: Onboarding completo pero `can_proceed_to_assets = False`.

---

## Testing

### Cobertura Actual

- **Total de tests**: 338 passing (v4.0.0)
- **Distribución**:
  - `tests/data_validation/` - Validación cruzada
  - `tests/financial_engine/` - Cálculo de escenarios
  - `tests/orchestration_v4/` - Flujo de dos fases
  - `tests/asset_generation/` - Generación condicional

### Ejecución

```bash
# Validación rápida
python scripts/run_all_validations.py --quick

# Validación completa
python scripts/run_all_validations.py

# Tests específicos
python -m pytest tests/data_validation/
python -m pytest tests/financial_engine/
```

---

## FAQ Técnico-Comercial

**Q: ¿Por qué ya no damos cifras exactas de pérdida?**
A: v4.0 usa escenarios con rangos. Una cifra exacta ($2.5M) se reemplaza por rango ($800k-$3.2M) con probabilidades asignadas.

**Q: ¿Qué pasa si hay conflictos en la validación?**
A: El sistema genera un reporte detallado y bloquea generación de assets hasta revisión manual. Nunca usamos datos conflictivos.

**Q: ¿Cómo se calculan los escenarios financieros?**
A: `ScenarioCalculator` usa datos validados + probabilidades: 70% conservador, 20% realista, 10% optimista.

**Q: ¿Puedo forzar generación de assets con datos ESTIMATED?**
A: Sí, pero el archivo incluirá disclaimer y prefijo `ESTIMATED_` en el nombre.

**Q: ¿Qué datos mínimos necesita la Fase 2?**
A: 5 campos: habitaciones, ADR, % ocupación, presencia OTAs, % canal directo.

---

## Referencias Cruzadas

| Si busco... | Ir a |
|-------------|------|
| Lógica de validación | [modules/data_validation/](../modules/data_validation/) |
| Cálculo de escenarios | [modules/financial_engine/](../modules/financial_engine/) |
| Flujo de onboarding | [modules/orchestration_v4/](../modules/orchestration_v4/) |
| Generación de assets | [modules/asset_generation/](../modules/asset_generation/) |
| Factores por región | [data/benchmarks/](../data/benchmarks/) |
| Metodología de cálculo | [GUIA_TECNICA.md](../docs/GUIA_TECNICA.md) |
| Precios comerciales | [PRECIOS_PAQUETES.md](../docs/PRECIOS_PAQUETES.md) |
| Contexto global del agente | [AGENTS.md](../AGENTS.md) |

---

## Cambios v3.x → v4.0 Resumen

| Aspecto | Antes (v3.x) | Después (v4.0) |
|---------|--------------|----------------|
| Precisión financiera | Cifra exacta | Escenarios con rangos |
| Datos de entrada | Benchmarks como input | Benchmarks como contexto |
| Validación | Ninguna | Validación cruzada obligatoria |
| Confianza | Implícita | Taxonomía VERIFIED/ESTIMATED/CONFLICT |
| Assets | Generación automática | Generación condicional con gates |
| Metadata | Opcional | Obligatoria en todos los assets |
| Transparencia | Baja | Explicación de fórmulas incluida |

---

*Última actualización: 2026-02-27 | v4.0.0 Sistema de Confianza*

---

## Controles de Coherencia v4.1.0

### Módulos Comerciales

| Módulo | Responsabilidad | Clases/Funciones Clave |
|--------|-----------------|------------------------|
| **commercial_documents** | Generación de diagnóstico y propuesta comercial | `V4DiagnosticGenerator`, `V4ProposalGenerator`, `DiagnosticDocument`, `ProposalDocument` |
| **coherence_validator** | Validación de alineación entre diagnóstico, propuesta y assets | `CoherenceValidator`, `CoherenceConfig`, `CoherenceCheck`, `CoherenceReport` |
| **pain_solution_mapper** | Mapeo de problemas detectados a assets de solución | `PainSolutionMapper`, `Pain`, `Solution`, `AssetSpec` |

### Checks de Coherencia

| Check | Descripción | Umbral | Blocking |
|-------|-------------|--------|----------|
| `problems_have_solutions` | Cada problema tiene al menos un asset | ≥ 50% | ✅ Sí |
| `assets_are_justified` | Cada asset está justificado por un problema | ≥ 80% | ❌ No |
| `financial_data_validated` | Datos financieros tienen confianza suficiente | ≥ 0.7 | ❌ No |
| `whatsapp_verified` | WhatsApp validado cruzando 2+ fuentes | ≥ 0.9 | ✅ Sí |
| `price_matches_pain` | Precio propuesto es coherente con dolor | 3x-6x | ❌ No |
| `overall_coherence` | Score global de coherencia | ≥ 0.8 | ❌ No |

### Configuración

Ubicación: `.conductor/guidelines.yaml`

```yaml
v4_coherence_rules:
  whatsapp_verified:
    confidence_threshold: 0.9
    blocking: true
  price_validation:
    min_ratio: 3.0
    max_ratio: 6.0
    ideal_ratio: 4.5
```

### Casos de Borde

1. **WhatsApp válido pero GBP contradictorio**
   - Entrada: `phone_web="+57A"`, `phone_gbp="+57B"`
   - Resultado: `ConfidenceLevel.CONFLICT`, `confidence=0.0`
   - Acción: Bloquear assets que requieran WhatsApp

2. **Schema presente pero inválido**
   - Entrada: Schema Hotel con campos faltantes
   - Resultado: `ESTIMATED` con warning en diagnóstico
   - Acción: Generar asset schema con disclaimer

3. **Datos financieros parciales**
   - Entrada: Solo `rooms` conocido, resto estimado
   - Resultado: Todos los escenarios `ESTIMATED`
   - Acción: Incluir disclaimer en proyecciones

4. **Escenario con rango negativo**
   - Entrada: Optimista resulta en valor negativo
   - Resultado: Mostrar como "potencial de mejora"
   - Acción: Narrativa ajustada en diagnóstico

5. **Asset bloqueado por conflicto**
   - Entrada: Asset requiere VERIFIED pero hay CONFLICT
   - Resultado: `FailedAsset` con `status=BLOCKED`
   - Acción: No generar, reportar en coherencia

---

