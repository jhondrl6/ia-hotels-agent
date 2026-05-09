# Prompt de Inicio de Sesion: FASE-3

> **Fase**: 3 — Policy y Gates  
> **Plan maestro**: `PLAN-REFACTOR-TERMALES-20260508.md`  
> **Iteraciones max**: 60  
> **Contexto previo**: FASE-PRE + FASE-1-A + FASE-1-B + FASE-2-A + FASE-2-B completadas  
> **Fixes**: FIX-9, FIX-10  

---

## Tareas de la Fase

TAREAS DE LA FASE:
  [ ] Investigacion de codigo existente (publication_gates.py)
  [ ] Implementar FIX-9: Evaluar proposal_asset_alignment WARNING→BLOCKED
  [ ] Implementar FIX-10: Onboarding gate para Tier C
  [ ] Documentar decisiones de producto
  [ ] Verificar con tests unitarios
  [ ] Documentacion post-fase

CONTADOR:
  - Total tareas: 5
  - Comandos largos: 0
  - Estado: dentro del limite R3

---

## Contexto de Fases Anteriores

- FASE-PRE: Saneamiento completado
- FASE-1-A: Template engine + Coherence validator corregidos
- FASE-1-B: Content Scrubber + monthly_report corregidos
- FASE-2-A: SitePresenceChecker + indirect_traffic + FAQ corregidos
- FASE-2-B: v4complete ejecutado para Termales, verificacion completada

---

## Instrucciones Detalladas

### FIX-9: proposal_asset_alignment — WARNING a BLOCKED

**Archivo**: `modules/quality_gates/publication_gates.py` (~L863)  
**Problema**: El gate es `passed=True, # WARNING, not blocking` por diseno.  
**Solucion**: Cambiar a BLOCKED cuando `alignment_percentage < 0.5`.

**Implementacion sugerida**:
```python
# Antes:
passed=True,  # WARNING, not blocking

# Despues:
alignment = assessment.get('alignment_percentage', 0.0)
if alignment < 0.5:
    passed = False
    status = GateStatus.BLOCKED
    reason = f"Alignment {alignment:.0%} < 50%: {missing_count} assets missing"
else:
    passed = True
    status = GateStatus.WARNING
    reason = f"Alignment {alignment:.0%}: {missing_count} assets missing (non-blocking)"
```

**Documentacion obligatoria**: Este es un cambio de POLICY, no bugfix. Documentar en:
- Comentario en el codigo explicando la regla de negocio
- Nota en GUIA_TECNICA (acumular en 09-documentacion-post-proyecto.md)

**Validacion**:
- Test: `alignment=0.3` → `passed=False, status=BLOCKED`
- Test: `alignment=0.6` → `passed=True, status=WARNING`
- Test: `alignment=0.5` → `passed=True, status=WARNING` (limite inclusive)

### FIX-10: Onboarding gate para Tier C

**Archivo**: `modules/quality_gates/publication_gates.py` (nuevo metodo/gate)  
**Problema**: Clientes Tier C reciben propuestas preliminares sin datos reales.  
**Solucion**: Nuevo gate que marca propuestas Tier C como "Preliminar".

**Implementacion sugerida**:
```python
def _check_tier_c_onboarding(self, assessment):
    """Gate: Si Tier C, la propuesta es preliminar y requiere onboarding."""
    tier = assessment.get('financial_evidence_tier', 'B')
    
    if tier == 'C':
        return GateResult(
            passed=False,
            status=GateStatus.BLOCKED,
            gate_name='tier_c_onboarding_required',
            reason='Tier C: Propuesta preliminar. Requiere datos reales para activacion.',
            details={'tier': 'C', 'required_action': 'onboarding'}
        )
    
    return GateResult(
        passed=True,
        status=GateStatus.PASSED,
        gate_name='tier_c_onboarding_required',
        reason='Tier B o superior: datos suficientes.',
        details={'tier': tier}
    )
```

**Nota**: Este gate DEBE ser bloqueante. Una propuesta Tier C sin onboarding es literalmente no publicable (todos los datos son estimados/placeholders).

**Validacion**:
- Test: `tier='C'` → `passed=False, status=BLOCKED`
- Test: `tier='B'` → `passed=True`
- Test: `tier='A'` → `passed=True`

---

## Post-Ejecucion (al finalizar la sesion)

1. **Marcar checklist** en `.opencode/plans/06-checklist-implementacion.md`:
   - FASE-3: estado y tareas completadas

2. **Ejecutar log_phase_completion.py**:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-3 \
    --desc "FIX-9 proposal_asset_alignment WARNING→BLOCKED + FIX-10 Tier C onboarding gate" \
    --archivos-nuevos "tests/quality_gates/test_tier_c_onboarding_gate.py" \
    --archivos-mod "modules/quality_gates/publication_gates.py" \
    --tests "N" \
    --check-manual-docs
```

3. **Actualizar 09-documentacion-post-proyecto.md**:

```markdown
## Seccion B: Funcionalidades Nuevas
| Feature | Modulo | Descripcion | Fase |
|---------|--------|-------------|------|
| Alignment gate policy | publication_gates | BLOCKED cuando alignment < 50% | FASE-3 |
| Tier C onboarding gate | publication_gates | Bloquea propuestas Tier C sin datos reales | FASE-3 |

## Seccion E: Archivos Afiliados Actualizados
| Archivo | Cambio | Fase |
|---------|--------|------|
| modules/quality_gates/publication_gates.py | FIX-9 + FIX-10 | FASE-3 |
```

4. **Guardar evidencia**:
```bash
cp modules/quality_gates/publication_gates.py evidence/fase-3/
```

---

## Criterios de Completitud

- [ ] FIX-9 implementado: `alignment < 0.5` → `BLOCKED`
- [ ] FIX-9 testeado: 3 casos de test pasan
- [ ] FIX-9 documentado como cambio de policy
- [ ] FIX-10 implementado: gate `tier_c_onboarding_required` bloquea Tier C
- [ ] FIX-10 testeado: 3 casos de test pasan
- [ ] `run_all_validations.py --quick` pasa (o solo fallas preexistentes)
- [ ] `log_phase_completion.py` ejecutado
- [ ] Checklist maestro actualizado

---

## Restricciones

- **NO ejecutar v4complete** — ya se ejecuto en FASE-2-B.
- **Max 60 iteraciones**.
- **NO revertir fixes previos**.
- Los cambios de policy deben estar claramente documentados; no son bugfixes silenciosos.

---

*Prompt generado por orquestador siguiendo phased_project_executor.md v2.10.0*
