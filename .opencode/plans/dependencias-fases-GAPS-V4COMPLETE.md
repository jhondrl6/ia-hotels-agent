# Dependencias de Fases - GAPS V4COMPLETE Hotel Vísperas

## Proyecto: iah-cli | Target: hotelvisperas.com
## Fecha: 2026-03-26 | Prioridad: CRÍTICA

---

## Diagrama de Dependencias

```
DESCONEXIÓN 1: whatsapp_button no se genera
┌─────────────────────────────────────────────────────────────────┐
│ AUDITOR          → VALIDATOR         → PAIN_MAPPER    → ASSETS│
│ V4Comprehensive  → CrossValidator     → detect_pains()  → Gen   │
│                                                                  │
│ ¿Qué pasa?                                                       │
│ 1. Auditor detecta 2 números WhatsApp diferentes                 │
│ 2. CrossValidator.calculate_whatsapp_confidence() → ¿CONFLICT?  │
│ 3. PainMapper.detect_pains() → ¿recibe CONFLICT?                │
│ 4. PainMapper.detect_pains() → ¿agrega whatsapp_conflict?       │
│ 5. AssetOrchestrator.generate_assets() → ¿planifica whatsapp_button?│
└─────────────────────────────────────────────────────────────────┘

DESCONEXIÓN 2: optimization_guide falla con placeholders
┌─────────────────────────────────────────────────────────────────┐
│ CONDITIONAL_GENERATOR  → CONTENT_VALIDATOR  → ASSET_ORCHESTRATOR│
│ genera optimization_guide → valida contenido  → marca como BLOCKED │
│                                                                  │
│ ¿Qué pasa?                                                       │
│ 1. conditional_generator.py → usa "..." o "pendiente"          │
│ 2. asset_content_validator.py → rechaza placeholders genéricos   │
│ 3. Asset se marca como BLOCKED                                   │
│ 4. Propuesta promete asset que NO se puede entregar             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tabla de Conflictos Potenciales

| # | Fase/Problema | Archivo(s) | Modificación | Riesgo |
|---|---------------|------------|--------------|--------|
| 1 | Validación WhatsApp | `cross_validator.py` | `calculate_whatsapp_confidence()` | AUDITOR no devuelve CONFLICT |
| 2 | Pain Detection | `pain_solution_mapper.py` | `detect_pains()` | No recibe/processa CONFLICT |
| 3 | Asset Planning | `pain_solution_mapper.py` | `generate_asset_plan()` | No incluye whatsapp_button |
| 4 | Content Gen | `conditional_generator.py` | placeholders | Usa "..." o "pendiente" |
| 5 | ROI Calculation | `roi_calculator.py` | `calculate_roi()` | 292X en vez de 3.9X |

---

## Análisis de Causa Raíz

### Desconexión 1: WhatsApp Button

**Hipótesis**: El `V4ComprehensiveAuditor` no está devolviendo `ConfidenceLevel.CONFLICT` para WhatsApp.

**Puntos de verificación**:
1. `modules/auditors/v4_comprehensive_auditor.py` - ¿Detecta conflicto de números?
2. `modules/data_validation/cross_validator.py:calculate_whatsapp_confidence()` - ¿Convierte a CONFLICT?
3. `modules/commercial_documents/pain_solution_mapper.py:detect_pains()` - ¿Procesa CONFLICT?
4. `modules/commercial_documents/pain_solution_mapper.py:489-495` - ¿Mapea a whatsapp_button?

**Verificación crítica**:
```python
# En cross_validator.py - ¿Qué confidence se devuelve?
if phone_web != phone_gbp:
    return ConfidenceLevel.CONFLICT  # <-- ¿Está así?
```

### Desconexión 2: Optimization Guide

**Hipótesis**: El `conditional_generator.py` está usando placeholders genéricos.

**Puntos de verificación**:
1. `modules/asset_generation/conditional_generator.py` - ¿Contiene "..." o "pendiente"?
2. `modules/asset_generation/asset_content_validator.py` - ¿Lista negra incluye estos?
3. El fix BUG-02 de FASE-G (2026-03-25 16:37) - ¿Se aplicó correctamente?

---

## Fases Propuestas

| Fase | ID | Descripción | Depende de | Archivos a modificar |
|------|----|-------------|------------|----------------------|
| 1 | FASE-H-01 | Diagnóstico causa raíz WhatsApp | ninguna | N/A (solo lectura) |
| 2 | FASE-H-02 | Fix cause raíz WhatsApp | FASE-H-01 | TBD |
| 3 | FASE-H-03 | Verificación optimization_guide | ninguna | TBD |
| 4 | FASE-H-04 | Fix placeholders + ROI | FASE-H-03 | TBD |
| 5 | FASE-H-05 | E2E Certification | FASE-H-02, FASE-H-04 | N/A |

---

## Verificación de Estado Previo (FASE-G 2026-03-25)

Según sesión 20260325_163747_684790:
- DESCONEXION-04: Fix aplicado en main.py línea 1702-1712 ✅
- BUG-02: Fix aplicado en conditional_generator.py ✅

**PERO** en ejecución actual (2026-03-26) los problemas persisten.

**Pregunta**: ¿Hubo regression o el entorno de ejecución es diferente?

---

## Archivos Críticos a Investigar

1. `modules/auditors/v4_comprehensive_auditor.py` - ¿Qué confidence devuelve?
2. `modules/data_validation/cross_validator.py` - ¿calculate_whatsapp_confidence()?
3. `modules/commercial_documents/pain_solution_mapper.py` - Líneas 489-500
4. `modules/asset_generation/conditional_generator.py` - placeholders

---

*Creado: 2026-03-26*
*Proyecto: iah-cli | hotelvisperas.com*
