# FASE-CONFIG-5: Extracción de Umbrales y Narrativas de Impacto (CR-7)

**Plan:** FEATURE-CONFIG-EXTRACTION v1.0.0
**Workflow:** `.agents/workflows/phased_project_executor.md` v2.9.0
**Presupuesto:** 60 iteraciones max | **Estimado esta fase:** ~48 iteraciones
**Dependencias:** FASE-CONFIG-3B (patrón YAML establecido). Puede ejecutarse en paralelo con CONFIG-4.
**Fase siguiente:** FASE-CONFIG-6

---

## Contexto

**Fuente:** `.opencode/context/TECHNICAL_DEBT_2026-04-29.md` §HALLAZGO 3 Grupos F, G (líneas 220-269)

### Hardcodes a Extraer (8 IDs, pero N-05 contiene 14 valores individuales)

| ID | Elemento | Archivo | Línea | Cantidad |
|----|----------|---------|-------|----------|
| N-05 | Pain narrative impacts (CRÍTICO) | v4_diagnostic_generator.py | L2208-2279 | 14 valores |
| N-02 | Confidence thresholds | v4_proposal_generator.py | L890-900 | 3 valores |
| N-03 | Coherence multipliers | v4_diagnostic_generator.py | L847-853 | 4 valores |
| N-06 | GBP geo_score threshold | v4_diagnostic_generator.py | L1992 | 1 valor |
| N-07 | Mobile score threshold | v4_diagnostic_generator.py | L1709 | 1 valor |
| N-08 | Citability thresholds | v4_diagnostic_generator.py | L1681-1685 | 2 valores |
| N-09 | IAO label thresholds | v4_diagnostic_generator.py | L1717-1719 | 2 valores |
| N-10 | Score status multipliers | v4_diagnostic_generator.py | L1741-1743 | 2 valores |

**Total: 29 valores hardcodeados.** N-05 es el más crítico porque impulsa las "4 Razones" con impacto monetario mostrado al cliente.

---

## Tareas Específicas

### Tarea 1: Crear config/regional_benchmarks.yaml

Estructura con soporte multi-región:
```yaml
version: "1.0.0"
description: "Umbrales de scoring y narrativas de impacto por región"

default_region: "eje_cafetero"

regions:
  eje_cafetero:
    pain_narratives:
      no_whatsapp_visible: 0.20
      no_hotel_schema: 0.25
      low_gbp_score: 0.30
      poor_performance: 0.15
      no_faq_schema: 0.12
      no_og_tags: 0.08
      low_citability: 0.10
      ai_crawler_blocked: 0.15
      no_org_schema: 0.08
      # + 5 más (completar del código L2208-2279)

    thresholds:
      confidence:
        high: 0.85
        medium: 0.70
        low: 0.40
      coherence_multipliers:
        verified: 100
        estimated: 70
        partial: 30
        unknown: 0
      gbp_geo_score: 70
      mobile_score: 50
      citability:
        adequate: 50
        low: 30
      iao_labels:
        high: 60
        medium: 35
      score_status:
        superior_multiplier: 1.1
        promedio_multiplier: 0.9

  # Otras regiones se agregan después
```

### Tarea 2: Parametrizar pain narratives (N-05)
- **v4_diagnostic_generator.py L2208-2279:** Los 14 valores de impacto están en un diccionario de narrativas
- Extraer CADA valor a `regional_benchmarks.yaml → regions.{region}.pain_narratives`
- Implementar `_load_benchmarks(region)` que carga la región correcta
- Fallback: si la región no existe en YAML, usar `default_region`
- Verificar que los 14 valores son exactamente los del código (leer L2208-2279)

### Tarea 3: Parametrizar umbrales de scoring (N-02, N-03, N-06 a N-10)
- **N-02 (confidence thresholds):** v4_proposal_generator.py L890-900 → YAML
- **N-03 (coherence multipliers):** v4_diagnostic_generator.py L847-853 → YAML
- **N-06 (GBP threshold):** v4_diagnostic_generator.py L1992 → YAML
- **N-07 (mobile threshold):** v4_diagnostic_generator.py L1709 → YAML
- **N-08 (citability thresholds):** v4_diagnostic_generator.py L1681-1685 → YAML
- **N-09 (IAO labels):** v4_diagnostic_generator.py L1717-1719 → YAML
- **N-10 (status multipliers):** v4_diagnostic_generator.py L1741-1743 → YAML

### Tarea 4: Tests
- Test: benchmarks.yaml presente → todos los umbrales de YAML
- Test: benchmarks.yaml ausente → fallback a defaults
- Test: región específica (eje_cafetero) → valores correctos
- Test: pain_narratives con valores personalizados → reflejados en diagnóstico
- Test: cambio de umbral → cambio en scoring cualitativo
- Verificar: `grep -rn "0\.20\|0\.25\|0\.30\|0\.15\|0\.12\|0\.08\|0\.10" modules/commercial_documents/v4_diagnostic_generator.py` no retorna hardcodes de N-05

---

## Archivos Involucrados

| Archivo | Tipo | Hardcodes |
|---------|------|-----------|
| `config/regional_benchmarks.yaml` | NUEVO | N-02, N-03, N-05, N-06, N-07, N-08, N-09, N-10 |
| `modules/commercial_documents/v4_diagnostic_generator.py` | MODIFICAR | N-03, N-05, N-06, N-07, N-08, N-09, N-10 |
| `modules/commercial_documents/v4_proposal_generator.py` | MODIFICAR | N-02 |

---

## Criterios de Completitud

- [ ] `config/regional_benchmarks.yaml` creado con schema multi-región
- [ ] N-05: 14 pain narrative impacts → YAML (verificado uno por uno)
- [ ] N-02, N-03, N-06, N-07, N-08, N-09, N-10 → YAML (7 hardcodes)
- [ ] Soporte multi-región: `_load_benchmarks("eje_cafetero")` funciona
- [ ] Tests: YAML presente, ausente, región específica, valores personalizados
- [ ] v4_diagnostic_generator.py sin hardcodes de N-05, N-03, N-06-N-10
- [ ] v4_proposal_generator.py sin hardcodes de N-02

---

## Restricciones

- **NO modificar** financial engines (ya refactorizados)
- **NO modificar** templates
- **NO ejecutar** v4complete
- **NO crear** YAML que no sea regional_benchmarks.yaml
- **Máximo 60 iteraciones** (R2)

---

## Post-Ejecución

```bash
mkdir -p evidence/fase-config-5
cp config/regional_benchmarks.yaml evidence/fase-config-5/
cp modules/commercial_documents/v4_diagnostic_generator.py evidence/fase-config-5/
cp modules/commercial_documents/v4_proposal_generator.py evidence/fase-config-5/

venv/Scripts/python.exe scripts/log_phase_completion.py     --fase FASE-CONFIG-5     --desc "Extracción de umbrales y narrativas: 14 pain narrative impacts + 7 umbrales de scoring a regional_benchmarks.yaml con soporte multi-región"     --archivos-nuevos "config/regional_benchmarks.yaml"     --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/v4_proposal_generator.py"     --tests "5"     --check-manual-docs
```

**Siguiente fase:**
```
Carga y ejecuta .opencode/plans/05-prompt-inicio-sesion-fase-CONFIG-6.md siguiendo .agents/workflows/phased_project_executor.md
```
