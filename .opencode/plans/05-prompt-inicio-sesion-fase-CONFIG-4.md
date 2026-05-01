# FASE-CONFIG-4: Template Parametrizado + Términos Comerciales (CR-5, Grupos C/D)

**Plan:** FEATURE-CONFIG-EXTRACTION v1.0.0
**Workflow:** `.agents/workflows/phased_project_executor.md` v2.9.0
**Presupuesto:** 60 iteraciones max | **Estimado esta fase:** ~44 iteraciones
**Dependencias:** FASE-CONFIG-3B (pricing YAML ya disponible para template)
**Fase siguiente:** FASE-CONFIG-5 (puede ejecutarse en paralelo con CONFIG-5)

---

## Contexto

**Fuente:** `.opencode/context/TECHNICAL_DEBT_2026-04-29.md` §HALLAZGO 2 Grupos C, D + §HALLAZGO 3 Grupo E (N-04)

### Hardcodes a Extraer (8 valores en 3 archivos)

| ID | Elemento | Archivo | Línea | Valor Actual |
|----|----------|---------|-------|-------------|
| H-15 | ROI cap | v4_proposal_generator.py | L934 | 5.0X |
| H-16 | break_even default | v4_proposal_generator.py | L941 | 6 meses |
| H-23 | Descuentos template | propuesta_v6_template.md | L170-172 | 10% trimestral, 18% semestral |
| H-24 | Cuotas sin interés | propuesta_v6_template.md | L168 | 3 cuotas |
| H-25 | Garantías (DUPLICADAS) | v4_proposal_generator.py L964-979 + propuesta_v6_template.md L142-153 | "90 días", "10%", "15 días" |
| H-26 | Plan stubs genéricos | v4_diagnostic_generator.py | L414-417 | Strings fijos 7d/30d/60d/90d |
| N-04 | Descuento pago único | v4_proposal_generator.py | L602 | 0.9 (10%) |
| N-04b | Descuento trimestral | v4_proposal_generator.py | L605 | 0.95 (5%) |

### CR-5: Duplicación de garantías
Las garantías existen en el método Python `_build_guarantees_section()` Y en el template MD. Editar uno sin el otro produce inconsistencia. Fix: ELIMINAR el método, mantener solo template con variables.

---

## Tareas Específicas

### Tarea 1: Eliminar duplicación de garantías (CR-5)
- **Eliminar** método `_build_guarantees_section()` en v4_proposal_generator.py L964-979
- **Consolidar** todas las garantías en `config/commercial.yaml` (ver abajo)
- **Template** propuesta_v6_template.md L142-153: reemplazar valores hardcodeados con `${guarantee_*}`
- Verificar que el generator inyecta las variables desde YAML al template
- Verificar que NO queda código duplicado de garantías

### Tarea 2: Crear config/commercial.yaml
```yaml
version: "1.0.0"
description: "Términos comerciales para propuestas"

roi:
  cap: 5.0
  description: "ROI máximo mostrado al cliente (múltiplo X)"

break_even:
  default_months: 6
  description: "Meses estimados para punto de equilibrio"

payment_options:
  single_payment_discount: 0.90   # 10% descuento
  quarterly_discount: 0.95         # 5% descuento
  installments: 3                  # cuotas sin interés
  installment_label: "3 cuotas sin interés"

discounts:
  quarterly: 10    # porcentaje
  semiannual: 18   # porcentaje

guarantees:
  satisfaction_days: 90
  satisfaction_text: "Garantía de satisfacción de 90 días"
  improvement_percent: 10
  improvement_text: "Compromiso de mejora del 10% en métricas clave"
  delivery_days: 15
  delivery_text: "Primeros resultados visibles en 15 días"

plans:
  plan_7d: "Revisar y optimizar Google Business Profile"
  plan_30d: "Implementar quick wins identificados y comenzar plan de contenido"
  plan_60d: "Desarrollar presencia en asistentes de IA y monitorear resultados"
  plan_90d: "Consolidar estrategia de IA y evaluar retorno de inversión"
```

### Tarea 3: Parametrizar hardcodes comerciales
- **H-15 (ROI cap):** v4_proposal_generator.py L934 → `commercial.yaml → roi.cap`
- **H-16 (break_even):** v4_proposal_generator.py L941 → `commercial.yaml → break_even.default_months`
- **H-23 (descuentos):** propuesta_v6_template.md L170-172 → `${quarterly_discount}`, `${semiannual_discount}`
- **H-24 (cuotas):** propuesta_v6_template.md L168 → `${installments}`
- **N-04/N-04b (payment discounts):** v4_proposal_generator.py L602,605 → `commercial.yaml → payment_options`
- **H-26 (plan stubs):** v4_diagnostic_generator.py L414-417 → `commercial.yaml → plans`
- Inyectar todas las variables desde el generator al template

### Tarea 4: Tests
- Test: commercial.yaml presente → template usa valores de YAML
- Test: commercial.yaml ausente → fallback a defaults
- Test: Garantías NO duplicadas (confirmar que `_build_guarantees_section` no existe)
- Test: Plan stubs configurables (cambiar YAML → cambiar diagnóstico)
- Test: Payment discounts aplicados correctamente en propuesta
- Verificar: `grep -rn "_build_guarantees_section" modules/` no retorna resultados

---

## Archivos Involucrados

| Archivo | Tipo | Hardcodes |
|---------|------|-----------|
| `config/commercial.yaml` | NUEVO | H-15, H-16, H-23, H-24, H-25, H-26, N-04, N-04b |
| `modules/commercial_documents/v4_proposal_generator.py` | MODIFICAR | H-15, H-16, H-25 (eliminar método), N-04, N-04b |
| `modules/commercial_documents/v4_diagnostic_generator.py` | MODIFICAR | H-26 |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | MODIFICAR | H-23, H-24, H-25 |

---

## Criterios de Completitud

- [ ] CR-5: `_build_guarantees_section()` ELIMINADO
- [ ] `config/commercial.yaml` creado con schema validado
- [ ] H-15, H-16, H-23, H-24, H-25, H-26 → YAML (6 hardcodes originales)
- [ ] N-04, N-04b → YAML (2 hardcodes nuevos)
- [ ] Garantías existen SOLO en template + YAML (no duplicadas)
- [ ] Plan stubs configurables vía YAML
- [ ] Tests: YAML presente, ausente, garantías no duplicadas
- [ ] `grep -rn "_build_guarantees_section" modules/` = 0 resultados

---

## Restricciones

- **NO modificar** pricing_calculator.py, scenario_calculator.py (ya refactorizados)
- **NO eliminar** variables del template, solo reemplazar hardcodes por placeholders
- **NO ejecutar** v4complete
- **Máximo 60 iteraciones** (R2)

---

## Post-Ejecución

```bash
mkdir -p evidence/fase-config-4
cp config/commercial.yaml evidence/fase-config-4/
cp modules/commercial_documents/v4_proposal_generator.py evidence/fase-config-4/
cp modules/commercial_documents/v4_diagnostic_generator.py evidence/fase-config-4/
cp modules/commercial_documents/templates/propuesta_v6_template.md evidence/fase-config-4/

venv/Scripts/python.exe scripts/log_phase_completion.py     --fase FASE-CONFIG-4     --desc "Parametrización de template comercial: garantías unificadas, ROI cap, break_even, descuentos, cuotas, plan stubs. Eliminada duplicación CR-5."     --archivos-nuevos "config/commercial.yaml"     --archivos-mod "modules/commercial_documents/v4_proposal_generator.py,modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/templates/propuesta_v6_template.md"     --tests "5"     --check-manual-docs
```

**Siguiente fase (elegir una):**
```
Carga y ejecuta .opencode/plans/05-prompt-inicio-sesion-fase-CONFIG-5.md siguiendo .agents/workflows/phased_project_executor.md
```
