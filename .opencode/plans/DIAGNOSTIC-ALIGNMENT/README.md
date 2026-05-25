# DIAGNOSTIC-ALIGNMENT — Plan de Refactorización

**Versión**: v1.0.0 (plan)  
**Target Release**: v4.52.0 — DIAGNOSTIC-ALIGNMENT  
**Creado**: 2026-05-25  
**Origen**: Validación de Prospección.md contra output/v4_complete (Hotel Castilla Real)  
**Objetivo**: Corregir 6 hallazgos (2 críticos + 4 fricciones) detectados en el output de v4complete para alinear el diagnóstico comercial con las expectativas de prospección B2B hotelera.

---

## Resumen del Problema

El output de v4complete para Hotel Castilla Real (2026-05-25) fue validado contra `Prospección.md`, revelando:

| # | Tipo | Hallazgo | Impacto |
|---|------|----------|---------|
| E1 | 🔴 Crítico | Tabla de Escenarios lógicamente invertida | Dueño detecta contradicción financiera |
| E2 | 🔴 Crítico | Tabla "Antes (2023) vs Ahora (2026)" ausente | Pierde el "momento ajá" pedagógico |
| F1 | 🟡 Fricción | Quick Wins en lenguaje de desarrollador | Dueño pospone acción |
| F2 | 🟡 Fricción | Disclaimer Tier C apologético | Dueño desconfía del número |
| F3 | 🟡 Fricción | Sin puente 7 brechas → 3 fugas | Dueño se pregunta por las otras 4 |
| F4 | 🟡 Fricción | "+$" confuso en tabla resumen | Dueño no sabe si es pérdida o ganancia |

---

## Fases del Plan

| Fase | Descripción | Tipo | Tareas | Comando Largo |
|------|-------------|------|--------|---------------|
| **FASE-A** | Fix E1 (Escenarios) + E2 (Antes/Ahora) | Implementación | 4 | 0 |
| **FASE-B** | Fix F1 (Quick Wins) + F2 (Disclaimer→Gancho) | Implementación | 4 | 0 |
| **FASE-C** | Fix F3 (Puente) + F4 (Encabezado "+$") | Implementación | 4 | 0 |
| **FASE-D** | v4complete Hotel Castilla Real + Verificación | Ejecución | 3 | 1 (v4complete) |
| **FASE-RELEASE** | Documentación oficial + Version bump | Release | 4 | 0 |

**Total**: 5 sesiones. 1 fase por sesión.

---

## Métricas Base

| Métrica | Valor Actual |
|---------|-------------|
| Versión | 4.51.1 |
| Tests | 2743 funciones, 211 archivos |
| Coherence Score | 0.826 (Hotel Castilla Real 2026-05-25) |

---

## Archivos del Plan

| Archivo | Propósito |
|---------|-----------|
| `README.md` | Este archivo — índice del plan |
| `dependencias-fases.md` | Diagrama de dependencias entre fases |
| `05-prompt-inicio-sesion-fase-A.md` | Prompt para FASE-A |
| `05-prompt-inicio-sesion-fase-B.md` | Prompt para FASE-B |
| `05-prompt-inicio-sesion-fase-C.md` | Prompt para FASE-C |
| `05-prompt-inicio-sesion-fase-D.md` | Prompt para FASE-D |
| `05-prompt-inicio-sesion-fase-RELEASE.md` | Prompt para FASE-RELEASE |
| `06-checklist-implementacion.md` | Checklist maestro de implementación |
| `09-documentacion-post-proyecto.md` | Acumulador de documentación post-fase |

---

## Criterio de Éxito Final

Al completar FASE-D, el output de v4complete para Hotel Castilla Real debe satisfacer TODOS los criterios de `Prospección.md`:

- [ ] Tabla de Escenarios: Conservador < Realista < Optimista (usando financial_value_range)
- [ ] Tabla "Antes vs Ahora" presente en Sección 1
- [ ] Quick Wins con acciones del dueño + delegación
- [ ] Disclaimer Tier C convertido en "Oportunidad de Auditoría Profunda"
- [ ] Texto puente entre 7 brechas y 3 fugas en Sección 4
- [ ] Encabezado de columna "Fuga mensual estimada" en tabla resumen
