# FASE-G: Dual Source Conflict Resolution

**ID**: FASE-G
**Objetivo**: Eliminar el conflicto de fuentes duales donde `_inject_brecha_scores()` sobrescribe silenciosamente las variables `brecha_{N}_nombre/costo/detalle` que `_get_brecha_*()` ya populó, y conectar impactos reales de brechas al proposal generator
**Dependencias**: FASE-F completada (phantom cost fix en proposal generator)
**Duración estimada**: 3-4 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

### Problema Detectado

En `v4_diagnostic_generator.py` existen dos fuentes que populan las mismas variables de template:

1. **Fuente A** (líneas 510-521): `_get_brecha_nombre()`, `_get_brecha_costo()`, `_get_brecha_detalle()` — usan `_identify_brechas()` con impactos reales
2. **Fuente B** (línea 586): `_inject_brecha_scores()` (FASE-C) — usa `OpportunityScorer` con datos potencialmente diferentes

El problema: `_inject_brecha_scores()` hace `data.update(score_vars)` en líneas 2014-2015, **sobrescribiendo** los valores que la Fuente A ya estableció. Esto puede producir:
- Nombres diferentes para la misma brecha
- Costos diferentes para la misma brecha
- Detalles inconsistentes en el documento final

Además, la conexión entre diagnóstico y propuesta está rota: el proposal generator no consume los `impacto` reales de `_identify_brechas()`.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-F | ✅ Completada — phantom costs eliminados |

### Base Técnica Disponible
- Archivo: `modules/commercial_documents/v4_diagnostic_generator.py`
- `_identify_brechas()` → detecta brechas con `impacto` real (0.30, 0.25, etc.)
- `_get_brecha_costo(audit_result, financial_scenarios, index)` → calcula costo con impacto real
- `_inject_brecha_scores()` (líneas 1976-2024) → OpportunityScorer scores, SOBRESCRIBE nombres/costos
- `OpportunityScorer` en `modules/financial_engine/opportunity_scorer.py`
- Tests: `tests/commercial_documents/test_diagnostic_brechas.py`

---

## Tareas

### Tarea 1: Unificar fuentes — _inject_brecha_scores NO debe sobrescribir

**Objetivo**: Modificar `_inject_brecha_scores()` para que no sobrescriba `brecha_{N}_nombre`, `brecha_{N}_costo`, `brecha_{N}_detalle` si ya están populados por la fuente principal

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` (líneas 1976-2024)

**Estrategia**:
- `_inject_brecha_scores()` debe inyectar SOLO las variables de score: `brecha_{N}_score`, `brecha_{N}_severity`, `brecha_{N}_effort`, `brecha_{N}_priority`
- NO debe sobrescribir `nombre`, `costo`, `detalle` que ya fueron establecidos por `_get_brecha_*()`
- Si un score no existe para una brecha dada, dejar el valor existente sin tocar

**Código a modificar** (líneas ~2014-2015):
```python
# ANTES (sobrescribe):
data.update(score_vars)

# DESPUÉS (selectivo):
for key, value in score_vars.items():
    if key not in data or not data[key]:
        data[key] = value
    elif key.endswith(('_score', '_severity', '_effort', '_priority')):
        data[key] = value  # Score vars siempre se actualizan
    # nombre, costo, detalle: NO sobrescribir si ya tienen valor
```

**Criterios de aceptación**:
- [ ] `brecha_{N}_nombre` de `_get_brecha_nombre()` NO es sobrescrito por `_inject_brecha_scores()`
- [ ] `brecha_{N}_costo` de `_get_brecha_costo()` NO es sobrescrito
- [ ] `brecha_{N}_score/severity/effort/priority` SÍ se actualizan (comportamiento correcto)
- [ ] El diagnóstico generado muestra nombres y costos consistentes

### Tarea 2: Conectar impactos reales al proposal generator via DiagnosticSummary

**Objetivo**: Extender `DiagnosticSummary` para incluir brechas con impacto real, y consumirlas en el proposal generator

**Archivos afectados**:
- `modules/commercial_documents/data_structures.py` (agregar campo a DiagnosticSummary)
- `modules/commercial_documents/v4_proposal_generator.py` (consumir brechas reales)

**Implementación**:

1. En `data_structures.py`, agregar a `DiagnosticSummary`:
```python
@dataclass
class DiagnosticSummary:
    # ... campos existentes ...
    brechas_reales: Optional[List[Dict[str, Any]]] = None  # NUEVO: desde _identify_brechas
```

2. En `v4_diagnostic_generator.py`, donde se construye `DiagnosticSummary`:
```python
# Incluir brechas reales
brechas_reales = self._identify_brechas(audit_result)
diagnostic_summary = DiagnosticSummary(
    # ... campos existentes ...
    brechas_reales=brechas_reales,  # NUEVO
)
```

3. En `v4_proposal_generator.py` `_prepare_template_data()` (reemplazando el código de FASE-F):
```python
# Consumir brechas reales si están disponibles
top_problems = diagnostic_summary.top_problems or []
brechas_reales = getattr(diagnostic_summary, 'brechas_reales', None) or []
max_brechas = 4
brecha_data = {}

for i in range(max_brechas):
    slot = i + 1
    if i < len(brechas_reales):
        # Fuente primaria: impacto real de _identify_brechas
        brecha = brechas_reales[i]
        impacto = brecha.get('impacto', 1.0 / max(len(brechas_reales), 1))
        brecha_data[f'brecha_{slot}_nombre'] = brecha.get('nombre', '')
        brecha_data[f'brecha_{slot}_costo'] = format_cop(
            int(main_scenario.monthly_loss_max * impacto)
        )
    elif i < len(top_problems):
        # Fallback: top_problems sin impacto real
        brecha_data[f'brecha_{slot}_nombre'] = top_problems[i]
        brecha_data[f'brecha_{slot}_costo'] = format_cop(
            int(main_scenario.monthly_loss_max / len(top_problems))
        )
    else:
        brecha_data[f'brecha_{slot}_nombre'] = ""
        brecha_data[f'brecha_{slot}_costo'] = "$0"
```

**Criterios de aceptación**:
- [ ] `DiagnosticSummary.brechas_reales` contiene las brechas con `impacto` real
- [ ] Proposal generator usa `impacto` real cuando `brechas_reales` está disponible
- [ ] Fallback a `top_problems` cuando `brechas_reales` es None (backward compatible)
- [ ] Los costos en la propuesta reflejan los pesos reales de cada brecha
- [ ] Si low_gbp_score tiene impacto 0.30, su costo = 30% de monthly_loss_max

### Tarea 3: Tests para dual source resolution

**Tests a crear**:

1. `test_brecha_scores_dont_overwrite_nombre`: Verificar que `_inject_brecha_scores` no cambia nombres
2. `test_brecha_scores_dont_overwrite_costo`: Verificar que costos de impacto real se preservan
3. `test_diagnostic_summary_includes_brechas_reales`: DiagnosticSummary tiene brechas_reales populadas
4. `test_proposal_uses_real_impact_weights`: Proposal usa impacto real, no distribución fija
5. `test_backward_compatible_without_brechas_reales`: Sin brechas_reales, usa top_problems como fallback

**Criterios de aceptación**:
- [ ] 5 tests nuevos pasando
- [ ] Tests existentes en `test_diagnostic_brechas.py` sin regresiones

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_brecha_scores_dont_overwrite_nombre` | `tests/commercial_documents/test_diagnostic_brechas.py` | nombre preservado |
| `test_brecha_scores_dont_overwrite_costo` | `tests/commercial_documents/test_diagnostic_brechas.py` | costo preservado |
| `test_diagnostic_summary_includes_brechas_reales` | `tests/commercial_documents/test_diagnostic_brechas.py` | campo populado |
| `test_proposal_uses_real_impact_weights` | `tests/test_proposal_alignment.py` | costo = impacto * loss |
| `test_backward_compatible_without_brechas_reales` | `tests/test_proposal_alignment.py` | fallback funciona |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_diagnostic_brechas.py tests/test_proposal_alignment.py -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`**: Marcar FASE-G como ✅ Completada
2. **`06-checklist-implementacion.md`**: Marcar items de FASE-G como ✅
3. **`09-documentacion-post-proyecto.md`**: Sección A, D, E
4. **`scripts/log_phase_completion.py`**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-G \
    --desc "Dual source conflict resolution + real impact weights in proposal" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/v4_proposal_generator.py" \
    --archivos-nuevos "" \
    --tests "5" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] **Tests nuevos pasan**: 5/5 dual source tests exitosos
- [ ] **Tests existentes pasan**: 0 regresiones en suite completa
- [ ] **Validaciones del proyecto**: `run_all_validations.py --quick` pasa
- [ ] **No overwrite silencioso**: `_inject_brecha_scores` no cambia nombre/costo/detalle
- [ ] **Impactos reales conectados**: Proposal muestra costos basados en pesos reales
- [ ] **Backward compatible**: Sin brechas_reales, el sistema funciona como antes
- [ ] **Post-ejecución completada**: dependencias, checklist, docs actualizados

---

## Restricciones

- NO modificar template archivos en esta fase
- NO modificar `data_structures.py` más allá de agregar `brechas_reales` (dedup es FASE-I)
- NO modificar `OpportunityScorer` directamente — solo cómo se consumen sus resultados
- Preservar retrocompatibilidad con DiagnosticSummary existente
- El cambio debe ser transparente para el template V6 (no usa brechas)

---

## Prompt de Ejecución

```
Actúa como arquitecto Python senior especializado en integridad de datos.

OBJETIVO: Eliminar dual source conflict y conectar impactos reales de brechas al proposal.

CONTEXTO:
- v4_diagnostic_generator.py tiene 2 fuentes que populan las mismas variables
- _inject_brecha_scores() sobrescribe _get_brecha_*() silenciosamente
- FASE-F ya eliminó phantom costs en proposal generator
- DiagnosticSummary necesita campo nuevo: brechas_reales

TAREAS:
1. Modificar _inject_brecha_scores para NO sobrescribir nombre/costo/detalle
2. Agregar brechas_reales a DiagnosticSummary
3. Proposal generator consume brechas_reales.impacto para costos reales
4. Fallback a top_problems cuando brechas_reales=None
5. 5 tests nuevos

CRITERIOS:
- 0 overwrites silenciosos
- Costos reflejan pesos reales (0.30, 0.25, etc.)
- Backward compatible
- run_all_validations.py --quick pasa

VALIDACIONES:
- pytest tests/commercial_documents/test_diagnostic_brechas.py -v
- pytest tests/test_proposal_alignment.py -v
- python scripts/run_all_validations.py --quick
```
