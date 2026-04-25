# Contexto para Plan: FASE-VALIDATE-HOTFIX

## Resumen del Fracaso

**Fecha**: 2026-04-24
**Fase**: FASE-VALIDATE (prueba v4complete única para Amazilia Hotel)
**Resultado**: PARCIAL-FALLA — NO-GO
**Hotel**: Amazilia Hotel (https://amaziliahotel.com/)

El comando `python main.py v4complete --url https://amaziliahotel.com/` crasheo en la fase de generación de propuesta comercial con un TypeError. El diagnóstico, financial_scenarios.json y audit_report.json se generaron correctamente. La propuesta comercial NO fue creada.

---

## Error Crítico Exacta

```
TypeError: V4ProposalGenerator._build_60_day_plan() missing 1 required positional argument: 'asset_plan'

  File ".../modules/commercial_documents/v4_proposal_generator.py", line 559
      'plan_60d': self._build_60_day_plan(),
```

---

## Análisis del Bug

### Ubicación del código defectuoso

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py`
**Líneas**: 559-560

```python
'plan_7d': self._build_7_day_plan(asset_plan),    # OK - pasa asset_plan
'plan_30d': self._build_30_day_plan(asset_plan), # OK - pasa asset_plan
'plan_60d': self._build_60_day_plan(),           # BUG - falta asset_plan
'plan_90d': self._build_90_day_plan(),           # BUG - falta asset_plan
```

### Por qué crashea

Python evalúa los argumentos de una función ANTES de llamar la función. Aunque `${plan_60d}` y `${plan_90d}` NO se usan en `propuesta_v6_template.md`, Python igual intenta ejecutar `self._build_60_day_plan()` para construir el dict, y como el método requiere `asset_plan` como argumento posicional obligatorio, lanza TypeError.

### Qué métodos están involucrados

| Método | Línea definición | Parámetro | ¿Requiere asset_plan? |
|--------|-------------------|-----------|----------------------|
| `_build_7_day_plan()` | 1112 | `asset_plan: Optional[List[AssetSpec]]` | Sí (opcional, tiene default None) |
| `_build_30_day_plan()` | 1158 | `asset_plan: Optional[List[AssetSpec]]` | Sí (opcional, tiene default None) |
| `_build_60_day_plan()` | 1200 | `asset_plan: Optional[List[AssetSpec]]` | Sí (opcional, tiene default None) |
| `_build_90_day_plan()` | 1236 | `asset_plan: Optional[List[AssetSpec]]` | Sí (opcional, tiene default None) |

Todos los métodos tienen `Optional` con default `None` — es decir, tolerate `asset_plan=None`. El bug es solo que no se pasa el argumento.

### Qué variables usa el template V6

Template `propuesta_v6_template.md` NO usa `${plan_60d}` ni `${plan_90d}`.
Usa `${plan_60_days}` y `${plan_90_days}` (líneas 587-588 en el dict):

```python
'plan_60_days': self._build_60_day_plan(asset_plan),  # OK
'plan_90_days': self._build_90_day_plan(asset_plan),  # OK
```

Las variables `plan_60d` y `plan_90d` (sin `_days`) son del template V4 heredado (propuesta_v4_template.md líneas 73-76) y probablemente nunca se usan en producción si el generador siempre usa V6.

### Fix requerido

```python
# Línea 559: cambiar
'plan_60d': self._build_60_day_plan(),
# por
'plan_60d': self._build_60_day_plan(asset_plan),

# Línea 560: cambiar
'plan_90d': self._build_90_day_plan(),
# por
'plan_90d': self._build_90_day_plan(asset_plan),
```

---

## Estado de Pre-flight

| Validación | Resultado |
|------------|-----------|
| `run_all_validations.py --quick` | PASS (4/4) |
| `pytest tests/commercial_documents/ tests/financial_engine/ tests/delivery/` | PASS (533 passed, 1 xpassed, 0 regresiones) |

---

## Archivos generados antes del crash

| Archivo | Estado |
|---------|--------|
| `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260424_120549.md` | ✅ Generado |
| `output/v4_complete/financial_scenarios.json` | ✅ Generado |
| `output/v4_complete/audit_report.json` | ✅ Generado |
| `output/v4_complete/02_PROPUESTA_COMERCIAL_*.md` | ❌ NO generado |

---

## Bugs evaluables desde archivos generados

| Bug | Resultado |
|-----|-----------|
| BUG-2 (escenarios ordenados) | **PASS** — conservative (5,076,000) > realistic (2,610,000) > optimistic (-189,000) |
| D-3 (ADR disclaimer) | **PASS** — disclaimer presente en financial_scenarios.json |

### Detalle BUG-2
El escenario "optimista" es NEGATIVO (-189,000 COP/mes). Esto representa equilibrio/pérdida, no un escenario optimista. El naming es semánticamente invertido aunque numéricamente el orden es correcto.

---

## Bugs NO evaluables (propuesta no generada)

- BUG-1: Sección "Esto es lo que hacemos" — NO EVALUABLE
- BUG-3: ROI <= 5.0X — NO EVALUABLE
- BUG-4: 0 items "No generado" — NO EVALUABLE
- BUG-5: Template V6 — NO EVALUABLE
- BUG-8: Ortografía — NO EVALUABLE
- D-1: AEO condicional — NO EVALUABLE
- D-4: Timeline realista — NO EVALUABLE
- D-7: 0 items "No generado" — NO EVALUABLE

---

## Documentación ya actualizada

- ✅ `06-checklist-implementacion.md` — FASE-VALIDATE marcada PARCIAL-FALLA con nota de bug
- ✅ `09-documentacion-post-proyecto.md` — Sección D (resultado) + Sección E (evidencia)
- ✅ `REGISTRY.md` — entrada FASE-VALIDATE registrada

---

## Evidencia preservada

```
.opencode/plans/evidence/fase-VALIDATE/
├── validacion_checklist.md
├── 01_DIAGNOSTICO_Y_OPORTUNIDAD_20260424_120549.md
└── financial_scenarios.json
```

---

## Recomendacion

El hotfix es trivial: agregar `asset_plan` a las lineas 559 y 560. Sin embargo, dado el patron de bugs superficiales que ocultan problemas sistémicos (FASE-CAUSAL documentó que se aplicó parche estático cuando el plan especificaba Opción C de refactorizacion), se recomienda:

1. **Hotfix minimo** (1 linea): corregir lineas 559-560 para permitir ejecucion
2. **Auditoria**: verificar si hay otros sitios donde se llama `_build_*_plan()` sin `asset_plan`
3. **Re-ejecucion**: ejecutar v4complete nuevamente para validar la propuesta completa

---

## PLANIFICACION EJECUTADA (2026-04-24)

Se creo FASE-VALIDATE-RC siguiendo el workflow `phased_project_executor.md` v2.4.0.

### Artefactos creados

| Artefacto | Ruta | Estado |
|-----------|------|--------|
| Prompt de fase | `.opencode/plans/05-prompt-inicio-sesion-fase-VALIDATE-RC.md` | ✅ Creado |
| Checklist maestro | `.opencode/plans/06-checklist-implementacion.md` | ✅ Actualizado |
| Dependencias | `.opencode/plans/dependencias-fases.md` | ✅ Actualizado |
| Doc post-proyecto | `.opencode/plans/09-documentacion-post-proyecto.md` | ✅ Preparado |

### Datos del hotel validados

- **Nombre**: Amazilia (Hotel campestre en Pereira)
- **URL**: https://amaziliahotel.com/
- **Direccion**: Via Pereira a Cerritos Entrada 8 Cafelia, Risaralda
- **Telefono**: +57 310 401 9049
- **Correo**: gerencia@amaziliahotel.com
- **RNT**: 56217

### Proximo paso

Iniciar nueva sesion con el prompt `05-prompt-inicio-sesion-fase-VALIDATE-RC.md`.
