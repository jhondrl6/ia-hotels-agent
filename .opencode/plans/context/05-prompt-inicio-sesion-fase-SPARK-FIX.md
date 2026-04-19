# Prompt de Inicio de Sesión — FASE-SPARK-FIX

## Contexto

El comando `spark` (diagnóstico rápido, stages geo+ia) no funciona. Este comando es crítico para el plan de outreach del ROADMAP v2.0: se usa para pre-ejecutar diagnósticos sobre prospectos antes de contactarlos (~$0.05/prospecto).

### Problemas encontrados

**BUG-1: Módulo `modules/orchestrator/` no existe**
- `main.py` línea 21: `from modules.orchestrator.pipeline import AnalysisPipeline, PipelineOptions`
- El directorio `modules/orchestrator/` fue eliminado/archivado
- Import falla silenciosamente → `ORCHESTRATOR_AVAILABLE = False`, `PipelineOptions = None`, `AnalysisPipeline = None`
- Esto afecta a TODOS los comandos que usan el pipeline legacy, no solo spark

**BUG-2: Harness traga errores de spark**
- `run_spark_mode()` (línea 344) ejecuta via `AgentHarness.run_task()`
- `_spark_handler` (línea 298) verifica `ORCHESTRATOR_AVAILABLE` y retorna error si False
- Pero el harness devuelve `success=True` con datos vacíos en 0.07s
- Resultado: spark dice "OK" pero no produce diagnóstico real

**BUG-3: Modo legacy falla con TypeError**
- `--bypass-harness` llama a `_run_spark_legacy()` (línea 404)
- `_run_spark_legacy` llama a `build_pipeline_options()` (línea 872)
- `build_pipeline_options` ejecuta `PipelineOptions(...)` pero `PipelineOptions = None`
- Resultado: `TypeError: 'NoneType' object is not callable`

### Módulos relevantes

| Archivo | Estado |
|---------|--------|
| `modules/orchestrator/pipeline.py` | NO EXISTE (archivado) |
| `modules/orchestration_v4/two_phase_flow.py` | EXISTE — tiene `TwoPhaseOrchestrator` |
| `modules/generators/spark_generator.py` | EXISTE (genera reportes spark) |
| `main.py` línea 21 | Import roto de `modules.orchestrator.pipeline` |
| `main.py` línea 298 | `_spark_handler` depende de ORCHESTRATOR_AVAILABLE |
| `main.py` línea 344 | `run_spark_mode` usa harness |
| `main.py` línea 404 | `_run_spark_legacy` usa PipelineOptions=None |
| `main.py` línea 868 | `build_pipeline_options` usa PipelineOptions=None |

---

## Objetivo

Que `spark` funcione correctamente: ejecutar stages geo+ia sobre una URL de hotel y generar los 4 archivos de output (`spark_report.md`, `whatsapp_script.txt`, `quick_win_action.md`, `metrics_summary.json`) con datos reales.

**Criterio de éxito**: Ejecutar `python main.py spark --url "https://maps.app.goo.gl/A5nMzpFVj2h1urNG6"` y obtener:
- Tiempo de ejecución > 30s (iéndo un diagnóstico real, no 0.07s)
- `gbp_score > 0`
- Los 4 archivos existen en disco con contenido real

---

## Investigación requerida

### T1: Mapear qué reemplazó a `modules.orchestrator`

```bash
# Buscar AnalysisPipeline y PipelineOptions en todo el repo
grep -rn 'class AnalysisPipeline\|class PipelineOptions' modules/ --include='*.py'
# Buscar imports de estos nombres
grep -rn 'from.*orchestrator.*import\|AnalysisPipeline\|PipelineOptions' modules/ main.py --include='*.py'
# Ver qué usa v4complete en su lugar
grep -n 'TwoPhaseOrchestrator\|run.*pipeline\|AnalysisPipeline' main.py
```

### T2: Verificar si spark_generator.py funciona independientemente

```bash
# spark_generator.py genera los 4 archivos a partir de geo_result + ia_result
# Verificar qué inputs necesita realmente
grep -n 'def generate_spark_report\|def __init__' modules/generators/spark_generator.py
```

### T3: Decidir estrategia de fix

Opciones:
- **A)** Fix mínimo: hacer que spark use `TwoPhaseOrchestrator` de `orchestration_v4` en vez de `AnalysisPipeline` del orchestrator archivado
- **B)** Crear un spark standalone que no dependa del pipeline: llamar directamente a los módulos geo e ia
- **C)** Restaurar `modules/orchestrator/` desde git history

---

## Secuencia de ejecución

1. **T1**: Mapear la arquitectura actual (qué existe vs qué referencia spark)
2. **T2**: Verificar spark_generator.py independientemente
3. **Decidir** estrategia A, B o C según hallazgos
4. **Implementar** el fix
5. **Verificar** con `python main.py spark --url <url> --bypass-harness`
6. **Tests de regresión**: `python -m pytest tests/ -k spark -v` (si existen)
7. **Documentación**: CHANGELOG, GUIA_TECNICA, log_phase_completion

---

## Restricciones

- NO ejecutar `v4complete` — solo spark
- NO modificar archivos fuera de `main.py`, `modules/generators/`, y módulos de pipeline relevantes
- Si se crea nuevo código, agregar tests correspondientes
- Presupuesto API: spark usa solo geo + ia (~$0.05/ejecución), máximo 5 ejecuciones de prueba

---

## Evidencia

Capturar en `evidence/fase-spark-fix/`:
- `r0_baseline.log` — ejecución actual que falla (ya capturada)
- `r1_post_fix.log` — ejecución después del fix
- `diff.txt` — cambios realizados
