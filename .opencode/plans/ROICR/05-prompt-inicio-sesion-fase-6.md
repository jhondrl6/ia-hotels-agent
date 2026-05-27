# FASE-6: v4complete Hotel Castilla Real + Análisis Post-Implementación

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: SUBAGENTE (v4complete) + DIRECTA (análisis)
> **Plan**: ROICR
> **Prerrequisito**: FASE-5 completada (tests pasando, fixtures actualizados)

## Contexto previo

FASE-1: Validator semántico + migration_target. FASE-2: Gate P1 BLOCKING. FASE-3: Pipeline unificado 3 pasos + CAPEX/OPEX desacoplado + curva 4 pilares. FASE-4: Arbitraje ético + Garantía Día 55. FASE-5: Fixtures + tests actualizados, pytest green.

Esta es la fase final: la **única ejecución de v4complete** en todo el plan. El objetivo es validar que todos los cambios del motor financiero v3.0 se reflejan correctamente en el output comercial para Hotel Castilla Real.

## Objetivo de esta fase

Ejecutar v4complete para Hotel Castilla Real y verificar que los 6 niveles de éxito están superados.

### Tareas

- [ ] **6A**: Ejecutar v4complete Hotel Castilla Real
  - URL: `https://www.hotelcastillareal.com/`
  - Región: `eje_cafetero`
  - Comando: `python main.py v4complete --url https://www.hotelcastillareal.com/`
  - Timeout: 900s via `delegate_task`
  - Guardar outputs inmediatamente después de completar

- [ ] **6B**: Verificar los 6 niveles de éxito

  **Nivel 1 — Pricing Ético:**
  - [ ] El precio mensual en la propuesta es ≤ $654,796 COP (o el valor que produzca el pipeline real)
  - [ ] El Value-Capture Cap se aplicó (precio < recovery * 0.50)
  - [ ] No hay arbitraje negativo (precio < recovery)

  **Nivel 2 — CAPEX/OPEX Desacoplado:**
  - [ ] La propuesta tiene tabla CAPEX separada ($2.5M setup fee)
  - [ ] La propuesta tiene tabla OPEX separada (mensual)
  - [ ] El ROI mostrado es SaaS-only, NO mezcla CAPEX+OPEX

  **Nivel 3 — Curva 4 Pilares:**
  - [ ] La proyección muestra recuperación creciente por mes
  - [ ] Mes 1 = ~15% del recovery total, Mes 6 = 100%
  - [ ] Punto de equilibrio visible (Mes 3 aproximado)

  **Nivel 4 — Gobernanza Comercial:**
  - [ ] Sin alucinaciones semánticas (assets mapeados lógicamente)
  - [ ] Assets DEPRECATED con migration_target no rompen el mapper
  - [ ] Gate P1 funciona (o documentar si no hay P1 NOT_READY activo)

  **Nivel 5 — Garantía Auditable:**
  - [ ] `python main.py validate-guarantee --url https://www.hotelcastillareal.com/` ejecuta sin errores
  - [ ] Output incluye referencia a CREDIT_NOTE (triggered o no)

  **Nivel 6 — CI/CD:**
  - [ ] Coherence Score ≥ 0.80
  - [ ] Publication Gates sin BLOCKING issues nuevos
  - [ ] Todos los archivos de output generados correctamente

- [ ] **6C**: Análisis comparativo pre/post ROICR
  - Tabla comparativa de métricas:
    | Métrica | Pre-ROICR | Post-ROICR |
    |---------|-----------|------------|
    | Pricing | $1,200,000 | (valor real) |
    | ROI SaaS | 0.3X | (valor real) |
    | CAPEX/OPEX | Mezclados | Desacoplados |
    | Coherence | 0.83 | (valor real) |
    | Gates | 10/11 | (valor real) |

- [ ] **6D**: Documentar en `09-documentacion-post-proyecto.md`
  - Llenar todas las secciones de FASE-6
  - Análisis post-implementación con evidencia de cada nivel
  - Veredicto final: ¿La propuesta es comercialmente viable?

### Restricciones

- **ÚNICA ejecución de v4complete en todo el plan** — no hay v4complete intermedio
- Guardar outputs inmediatamente después de v4complete (evidence protocol)
- Si v4complete falla: diagnosticar ANTES de re-ejecutar. Timeout máximo: 900s.
- Si un nivel no se supera: documentar QUÉ falta y POR QUÉ, no fixear en esta fase

### Criterios de completitud

- [ ] v4complete completó sin errores fatales
- [ ] Output files generados (diagnóstico + propuesta + financial_scenarios)
- [ ] Los 6 niveles verificados con evidencia
- [ ] Análisis comparativo documentado
- [ ] Veredicto final escrito
- [ ] Checklist `06-checklist-implementacion.md` actualizado con métricas finales

### Criterio de Éxito del Plan Completo

> La propuesta de Hotel Castilla Real debe ser **comercialmente viable**: el cliente ve un ROI SaaS positivo a partir del Mes 3, la agencia se autolimita con el Value-Capture Cap, CAPEX y OPEX están claramente separados, y la garantía del Día 55 es auditable por comando CLI.

### Próxima sesión

FASE-7: RELEASE v4.55.0 — Version bump, CHANGELOG, REGISTRY, domain primer, pre-commit. Fase final del plan.
