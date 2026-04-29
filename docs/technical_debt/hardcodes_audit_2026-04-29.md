# Hardcodes Audit — AmaziliaHotel Forensic

**Fecha**: 2026-04-29
**Fuente**: `.opencode/context/ContextMv2.md` §Hardcodes (H-9 → H-27)
**Severidad global**: HIGH — impactan pricing, ROI, y credibilidad comercial del entregable
**Estado**: NO CORREGIDOS — catalogados como deuda técnica para proyecto futuro
**Proyecto origen**: PATCH-AUDITORIA-FORENSE-AMAZILIA-v2 (4.36.1 → 4.37.0)

---

## Resumen Ejecutivo

La auditoría forense de la propuesta comercial AmaziliaHotel reveló 19 hardcodes en el código de producción que afectan directamente los números que ve el cliente: precio del paquete, fee de setup, ROI, escenarios financieros, benchmarks regionales, y fallbacks de scores. Estos valores están literalmente escritos en el código fuente en vez de ser configurables.

**Riesgo comercial**: Si las condiciones del mercado cambian (inflación, tipo de cambio, benchmarks regionales), todos los valores requerirían editar código fuente y re-desplegar.

**Recomendación**: Proyecto dedicado de extracción de configuración con schema YAML/JSON, migración, tests de regresión, y validación de backwards compatibility.

---

## Catálogo de Hardcodes

### Grupo 1: Pricing Comercial (H-9, H-10, H-18, H-19)

| ID | Elemento | Archivo | Línea | Valor Hardcodeado | Severidad | Recomendación |
|----|----------|---------|-------|-------------------|-----------|---------------|
| H-9 | `MONTHLY_PACKAGE_PRICE` | `modules/commercial_documents/v4_proposal_generator.py` | ~L52 | `1,200,000` COP | 🔴 HIGH | Extraer a `config/pricing.yaml` → `monthly_package_price` |
| H-10 | `SETUP_FEE` | `modules/commercial_documents/v4_proposal_generator.py` | ~L53 | `2,500,000` COP | 🔴 HIGH | Extraer a `config/pricing.yaml` → `setup_fee` |
| H-18 | Price floor / ceiling | `modules/commercial_documents/v4_proposal_generator.py` | ~L1099 | `800,000` / `2,500,000` COP | 🔴 HIGH | Extraer a `config/pricing.yaml` → `price_floor` / `price_ceiling` |
| H-19 | `TIER_CONFIG` completo | `modules/financial_engine/pricing_calculator.py` | L48-68 | Diccionario con porcentajes por tier, min/max, ratios | 🔴 HIGH | Migrar a `config/pricing.yaml` → `tiers` con schema validado. Es la base de todo el sistema de pricing. |

**Impacto**: Estos 4 hardcodes definen CUÁNTO paga el cliente. Cualquier ajuste de precios requiere editar código Python.

---

### Grupo 2: Escenarios Financieros (H-14, H-17, H-20, H-21, H-22)

| ID | Elemento | Archivo | Línea | Valor Hardcodeado | Severidad | Recomendación |
|----|----------|---------|-------|-------------------|-----------|---------------|
| H-14 | `recovery_factor` | `modules/commercial_documents/v4_proposal_generator.py` | ~L519, 486, 523 | `0.15`, `0.20`, `0.25` (conservador/realista/optimista) | 🔴 HIGH | Extraer a `config/scenarios.yaml`. Define el ROI que ve el cliente. |
| H-17 | Scenario weights | `modules/commercial_documents/v4_proposal_generator.py` | ~L1096 | `70/20/10` (ponderación conservador/realista/optimista) | 🔴 HIGH | Extraer a `config/scenarios.yaml` → `weights` |
| H-20 | `degradation_rate` | `modules/financial_engine/loss_projector.py` | ~L65 | `2%` / mes | 🔴 HIGH | Extraer a `config/scenarios.yaml` → `degradation_rate` |
| H-21 | Shift OTA → directo | `modules/financial_engine/scenario_calculator.py` | ~L178, 243, 286 | `5%`, `10%`, `20%` | 🔴 HIGH | Extraer a `config/scenarios.yaml` → `ota_shift`. Define cuánto tráfico migra de OTA a directo. |
| H-22 | IA boost | `modules/financial_engine/scenario_calculator.py` | ~L248, 287 | `5%`, `10%` | 🔴 HIGH | Extraer a `config/scenarios.yaml` → `ia_boost`. Define incremento de tráfico por optimización IA. |

**Impacto**: Estos 5 hardcodes definen CÓMO se proyecta el retorno de inversión. Son assumptions financieras que deberían ser ajustables por mercado/región.

---

### Grupo 3: Fallbacks de Scores (H-11, H-12, H-13, H-27)

| ID | Elemento | Archivo | Línea | Valor Hardcodeado | Severidad | Recomendación |
|----|----------|---------|-------|-------------------|-----------|---------------|
| H-11 | `benchmark_score` | `modules/commercial_documents/v4_proposal_generator.py` | ~L1035 | `58` | 🔴 HIGH | Extraer a `config/fallbacks.yaml` o consultar benchmark regional real. |
| H-12 | `score_tecnico` fallback | `modules/commercial_documents/v4_proposal_generator.py` | ~L568, 981 | `50` | 🔴 HIGH | Extraer a `config/fallbacks.yaml`. Si un módulo falla silenciosamente, el cliente ve "50" inventado. |
| H-13 | `coherence` fallback | `modules/commercial_documents/v4_proposal_generator.py` | ~L564 | `'70'` | 🔴 HIGH | Extraer a `config/fallbacks.yaml`. Coherence falso si el cálculo real falla. |
| H-27 | `voice_readiness` fallback | `modules/commercial_documents/v4_diagnostic_generator.py` | ~L613 | `'0'` | 🔴 HIGH | Extraer a `config/fallbacks.yaml`. Voice readiness en 0 sin evaluar. |

**Impacto**: Si un módulo de auditoría falla silenciosamente (API caída, rate limit), el cliente ve un score INVENTADO sin saber que es un fallback. Deberían ser `null` o marcarse explícitamente.

---

### Grupo 4: Límites y Garantías (H-15, H-16, H-25)

| ID | Elemento | Archivo | Línea | Valor Hardcodeado | Severidad | Recomendación |
|----|----------|---------|-------|-------------------|-----------|---------------|
| H-15 | ROI cap | `modules/commercial_documents/v4_proposal_generator.py` | ~L929 | `5.0X` | 🟡 MEDIUM | Extraer a `config/pricing.yaml` → `roi_cap`. |
| H-16 | `break_even` default | `modules/commercial_documents/v4_proposal_generator.py` | ~L936 | `6` meses | 🟡 MEDIUM | Extraer a `config/scenarios.yaml` → `break_even_months`. |
| H-25 | Guarantee terms | `modules/commercial_documents/v4_proposal_generator.py` | ~L959-974 | 90 días garantía, 10% descuento, 15 días cancelación | 🟡 MEDIUM | Extraer a `config/pricing.yaml` → `guarantee`. Términos comerciales que pueden cambiar. |

---

### Grupo 5: Templates y Placeholders Comerciales (H-23, H-24, H-26)

| ID | Elemento | Archivo | Línea | Valor Hardcodeado | Severidad | Recomendación |
|----|----------|---------|-------|-------------------|-----------|---------------|
| H-23 | Discounts | `modules/commercial_documents/templates/propuesta_v6_template.md` | ~L171-172 | `10%` trimestral, `18%` semestral | 🔴 HIGH | Extraer a `config/pricing.yaml` → `discounts`. Visible en propuesta. |
| H-24 | Cuotas sin interés | `modules/commercial_documents/templates/propuesta_v6_template.md` | ~L168 | `3` cuotas | 🟢 LOW | Extraer a `config/pricing.yaml` → `installments`. |
| H-26 | Plan text stubs | `modules/commercial_documents/v4_diagnostic_generator.py` | ~L414-417 | Textos "7 días", "30 días", "60 días" | 🔴 HIGH | Migrar a template o config. Textos de plan de acción hardcodeados en generador. |

---

## Mapeo de Archivos Reales

Los nombres abreviados en ContextMv2.md mapean a:

| Abreviatura | Archivo real |
|-------------|-------------|
| `proposal` | `modules/commercial_documents/v4_proposal_generator.py` |
| `diagnostic` | `modules/commercial_documents/v4_diagnostic_generator.py` |
| `template` | `modules/commercial_documents/templates/propuesta_v6_template.md` |
| `pricing_calculator` | `modules/financial_engine/pricing_calculator.py` |
| `loss_projector` | `modules/financial_engine/loss_projector.py` |
| `scenario_calculator` | `modules/financial_engine/scenario_calculator.py` |

---

## Estadísticas

| Métrica | Valor |
|---------|-------|
| Total hardcodes | 19 (H-9 → H-27) |
| Severidad HIGH | 15 |
| Severidad MEDIUM | 3 |
| Severidad LOW | 1 |
| Archivos afectados | 6 |
| Grupos funcionales | 5 (pricing, escenarios, fallbacks, límites, templates) |

---

## Recomendación de Abordaje

### Proyecto futuro: `FEATURE-CONFIG-EXTRACTION`

**Objetivo**: Migrar hardcodes a archivos de configuración YAML/JSON con schema validado.

**Fases sugeridas**:

| Fase | Alcance | Archivos |
|------|---------|----------|
| FASE-CONFIG-1 | Crear `config/pricing.yaml` + migrar H-9, H-10, H-18, H-19, H-23, H-24, H-25 | `pricing_calculator.py`, `v4_proposal_generator.py`, `propuesta_v6_template.md` |
| FASE-CONFIG-2 | Crear `config/scenarios.yaml` + migrar H-14, H-17, H-20, H-21, H-22, H-16 | `scenario_calculator.py`, `loss_projector.py`, `v4_proposal_generator.py` |
| FASE-CONFIG-3 | Crear `config/fallbacks.yaml` + migrar H-11, H-12, H-13, H-27, H-15 | `v4_proposal_generator.py`, `v4_diagnostic_generator.py` |
| FASE-CONFIG-4 | Migrar H-26 (plan text stubs) a template data | `v4_diagnostic_generator.py` |
| FASE-CONFIG-5 | Tests de regresión + validación de backwards compatibility | `tests/` |
| FASE-CONFIG-6 | Documentación + RELEASE | `CHANGELOG.md`, `GUIA_TECNICA.md`, `CONTRIBUTING.md` |

**Pre-requisitos**:
1. Schema YAML con tipos validados (no aceptar strings donde van números)
2. Carga con fallback: si el archivo YAML no existe, usar defaults documentados
3. Tests que verifiquen que cada valor se lee de config, no de hardcode
4. `doctor.py` debe verificar integridad de archivos de configuración

**Riesgos**:
- Romper backwards compatibility si el formato de config cambia
- Valores por defecto incorrectos si el YAML tiene errores de sintaxis
- Migración parcial (algunos hardcodes quedan sin migrar)

---

## Notas

- **Líneas aproximadas**: Las referencias de línea son del código al momento de la auditoría (2026-04-29). Pueden desplazarse con cambios posteriores. Verificar con `grep` antes de modificar.
- **No bloqueante**: Ninguno de estos hardcodes impide que el sistema funcione. El riesgo es de credibilidad comercial, no de fallo técnico.
- **Relación con PATCH-A/B**: Los fixes de PATCH-A y PATCH-B corrigen hardcodes que producían DATOS FALSOS (ej: web_score=85). Estos H-9→H-27 son hardcodes de CONFIGURACIÓN — valores legítimos pero no configurables.

---

*Catálogo generado como parte de FASE-PATCH-D del proyecto PATCH-AUDITORIA-FORENSE-AMAZILIA-v2*
