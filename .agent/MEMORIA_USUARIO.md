# 🧠 Blueprint: Siguiente Fase - IA Hoteles Agent v3.3.1

> **Propósito**: Documento de transferencia de contexto. Contiene exclusivamente el punto de partida y los objetivos arquitectónicos para la próxima sesión de desarrollo.

---

## 🚀 Estado Actual: "Meta-Arquitectura Nivel 3" Completada en Workflows
1. Las 11 habilidades core han sido migradas a `.agents/workflows/` como Meta-Skills (archivos Markdown con frontmatter, triggers, constraints y fallbacks).
2. El enrutador semántico (`AgentHarness` / `SkillRouter`) funciona perfectamente: es capaz de leer un prompt (ej. "evalúa este hotel") e invocar directamente al workflow correspondiente (ej. `truth_protocol.md`).
3. **El Problema (Deuda Técnica):** El pipeline principal ejecutado desde consola (`python main.py audit` a través de `AnalysisPipeline`) **sigue utilizando importaciones rígidas de Python** (código duro) para orquestar la extracción (GEO), el análisis (IA/SEO) y la generación de entregables, ignorando por completo las nuevas Meta-Skills. El comando local `ps audit` está obsoleto funcionalmente bajo el nuevo paradigma.

---

## 🎯 Objetivo de la Próxima Sesión: Nivel 3 Profundo en `main.py`

**Misión:** Refactorizar el orquestador nativo (`AnalysisPipeline` en `modules/orchestrator/pipeline.py`) y el CLI (`main.py`) para que **deleguen la carga de trabajo a las Meta-Skills vía `AgentHarness`**, eliminando la lógica de negocio "hardcodeada" en Python.

### Pasos Propuestos:
1. **Rediseño del subcomando `audit`**: En lugar de ejecutar procesos monolíticos, `main.py` debe instanciar `AgentHarness` y despachar tareas secuenciales que apunten a los workflows.
2. **Promoción de Fases a Meta-Skills**: Modularizar el análisis GEO, IA y SEO para que dependan de la configuración declarativa de las Meta-Skills, permitiendo que el Agente decida dinámicamente qué workflow usar.
3. **Mantenimiento o Eliminación de `ps audit`**: Decidir si se adapta `scripts/run_hotel_visperas_audit.ps1` para disparar el agente natural (`execute "inicia auditoría..."`) en lugar del monolito `audit`, o si se acopla el flag `audit` al `AgentHarness`.

---

**Prompt Directo para la Próxima Sesión:**

> "Acabamos de migrar IA Hoteles a la Meta-Arquitectura Nivel 3 (`.agents/workflows`). El router semántico funciona genial, pero tenemos deuda técnica: `main.py audit` y `AnalysisPipeline` siguen operando con código duro y esquivan las Meta-Skills al hacer pruebas locales. Lee el blueprint en `.agent/MEMORIA_USUARIO.md` y arranca con la Fase 1 del Nivel 3 Profundo: Refactorizar `main.py` y el pipeline para que consuman `agent_harness/core.py` como único motor subyacente de la lógica de negocio. Avísame cuándo y cómo empezamos a abstraer las fases GEO y SEO."
