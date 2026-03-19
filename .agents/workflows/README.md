# Meta-Skills Index (Agente Auto-Evolutivo v3.9.0)

> [!CAUTION]
> **El codigo rigido esta deprecado**. IA Hoteles Guardian Nivel 3 opera mediante Workflows Semanticos basados en Frontmatter y Triggers explicitos.
> Todo nuevo conocimiento del Agente DEBE ser documentado como una `skill` usando el `skill-creator`.

## Workflows de Analisis y Negocio (Core)

| Trigger (Cuando usar) | Meta-Skill | Estado |
|-----------------------|-------------|--------|
| "Aprende a...", "Crea una skill para..." | [meta_skill_creator.md](meta_skill_creator.md) | Estable |
| "Materializa la propuesta", "genera entregables" | [delivery_wizard.md](delivery_wizard.md) | Estable |
| "Integrar nueva tecnologia", "evaluar cambio" | [audit_guardian.md](audit_guardian.md) | Estable |

## Workflows v4.1.0 - v4.2.0

| Trigger (Cuando usar) | Meta-Skill | Estado |
|-----------------------|-------------|--------|
| "Análisis completo v4", reemplazo de `audit` | [v4_complete.md](v4_complete.md) | Estable v4.1.0 |
| "Validar coherencia" entre diagnóstico y propuesta | [v4_coherence_validator.md](v4_coherence_validator.md) | Estable v4.1.0 |
| "Calcular escenarios financieros" | [v4_financial_scenarios.md](v4_financial_scenarios.md) | Estable v4.1.0 |
| "Generar assets condicionalmente" | [v4_asset_conditional.md](v4_asset_conditional.md) | Estable v4.1.0 |
| "Cálculo financiero" vía Agent Harness | [v4_financial_calculation.md](v4_financial_calculation.md) | Estable v4.2.0 |
| "Resolución regional ADR" vía Agent Harness | [v4_regional_resolver.md](v4_regional_resolver.md) | Estable v4.2.0 |
| "Validar v4complete post-cambios" | [v4_regression_guardian.md](v4_regression_guardian.md) | Estable v4.3.0 |


## Workflows Protectores (Safeguards)

| Trigger (Cuando usar) | Meta-Skill | Estado |
|-----------------------|-------------|--------|
| "Evalua/Valida/Revisa este hotel", Inicio de Auditoria | [truth_protocol.md](truth_protocol.md) | Estable |
| "Valida los entregables", "QA post-venta" | [qa_guardian.md](qa_guardian.md) | Estable |
| "Audita el sistema de skills", "verifica consistencia" | [maintenance_autopilot.md](maintenance_autopilot.md) | Estable |
| "Escaner ligero", "vigila este perfil" | [watchdog_check.md](watchdog_check.md) | Estable |

## Workflows de Operacion (IT / Dev)

| Trigger (Cuando usar) | Meta-Skill | Estado |
|-----------------------|-------------|--------|
| "Ayudame a instalar", "despliegue en WordPress" | [deployment_assistant.md](deployment_assistant.md) | Estable |
| "Fallo de API key", "No LLM API key configured" | [env_rerun.md](env_rerun.md) | Estable |
| "Monitorea tareas", "procesos en background" | [monitor_bg.md](monitor_bg.md) | Estable |
| "Mejorar velocidad", "arreglar LCP" | [seo_technical.md](seo_technical.md) | Estable |

---

## Workflows de Gestión de Proyectos

| Trigger (Cuando usar) | Meta-Skill | Estado |
|-----------------------|-------------|--------|
| "Ejecuta por fases", "Continúa en nueva sesión", "Divide en sprints" | [phased_project_executor.md](phased_project_executor.md) | Estable v1.3.0 |

**Nota**: `phased_project_executor` incluye un [template de prompts obligatorio](templates/prompt-fase-template.md) para estandarizar documentación entre fases.

---

## Sistema de Validacion v3.8.0 (NUEVO)

El sistema ahora incluye validacion nativa independiente de Gemini CLI:

| Comando | Uso |
|---------|-----|
| `python scripts/run_all_validations.py` | Validacion completa |
| `python scripts/run_all_validations.py --quick` | Validacion esencial |
| `python scripts/validate.py --plan` | Validar Plan Maestro |
| `python scripts/validate.py --security` | Detectar secrets |
| `python scripts/validate.py --content <file>` | Validar contenido |
| `pre-commit run --all-files` | Ejecutar hooks manuales |

---

### Mantenimiento Evolutivo
Para proponer una mejora en un workflow, no crees codigo nuevo. Ejecuta el protocolo: `skill-creator aprende a mejorar [nombre]`.
