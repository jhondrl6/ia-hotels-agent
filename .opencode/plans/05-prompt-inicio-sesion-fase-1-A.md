# Prompt de Inicio de Sesion: FASE-1-A

> **Fase**: 1-A — Bugs Criticos: Template Engine + Coherence Validator  
> **Plan maestro**: `PLAN-REFACTOR-TERMALES-20260508.md`  
> **Iteraciones max**: 60  
> **Contexto previo**: FASE-PRE completada (saneamiento base realizado)  
> **Fixes**: FIX-1, FIX-2  

---

## Tareas de la Fase

TAREAS DE LA FASE:
  [ ] Investigacion de codigo existente (v4_proposal_generator.py, coherence_validator.py)
  [ ] Implementar FIX-1: Procesar {{if}}...{{endif}} en template engine
  [ ] Implementar FIX-2: coherence_validator usa generated_assets, no catalogo estatico
  [ ] Verificar con tests unitarios (tests existentes + nuevos)
  [ ] Documentacion post-fase

CONTADOR:
  - Total tareas: 4
  - Comandos largos: 0
  - Estado: dentro del limite R3

---

## Contexto de Fases Anteriores

FASE-PRE completada. Estado base verificado:
- Validaciones pre-refactor: documentadas
- Line endings: normalizados (o OK)
- Estructura evidence/ lista

---

## Instrucciones Detalladas

### FIX-1: Template Engine Conditional

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py` (~L1103-1106)  
**Problema**: `string.Template.safe_substitute()` no procesa `{{if cond}}...{{endif}}`. Los bloques pasan crudos al cliente.  
**Solucion**: Implementar pre-procesador ligero antes de `safe_substitute()`.

**Implementacion sugerida**:
```python
def _preprocess_conditionals(self, template_content, data):
    """Elimina bloques {{if cond}}...{{endif}} cuando cond es False."""
    import re
    pattern = r'\{\{if\s+(\w+)\s*==\s*"([^"]+)"\}\}(.*?)\{\{endif\}\}'
    
    def replace_match(match):
        var_name = match.group(1)
        expected = match.group(2)
        block = match.group(3)
        actual = data.get(var_name, '')
        return block if str(actual) == expected else ''
    
    return re.sub(pattern, replace_match, template_content, flags=re.DOTALL)

# En _render_template:
def _render_template(self, template_content, data):
    preprocessed = self._preprocess_conditionals(template_content, data)
    template = Template(preprocessed)
    return template.safe_substitute(data)
```

**Validacion**:
- Crear test en `tests/commercial_documents/test_v4_proposal_generator.py` (o equivalente)
- Input: template con `{{if financial_evidence_tier == "C"}}warning{{endif}}`, data `{'financial_evidence_tier': 'C'}` → debe incluir warning
- Input: data `{'financial_evidence_tier': 'B'}` → debe excluir warning
- Input: data `{'financial_evidence_tier': 'C'}` → output NO debe contener `{{if}}` ni `{{endif}}`

### FIX-2: Coherence Validator Fuente de Verdad

**Archivo**: `modules/commercial_documents/coherence_validator.py` (~L518-538)  
**Problema**: `_check_promised_assets_exist()` usa `is_asset_implemented()` que verifica el catalogo estatico, no los assets realmente generados.  
**Solucion**: Recibir `generated_assets` del pipeline y verificar contra ellos.

**Implementacion sugerida**:
```python
# Modificar la firma o acceso para usar generated_assets
def _check_promised_assets_exist(self, generated_assets=None):
    """
    generated_assets: dict de asset_generation_report.json 
                      (e.g. {'seo_checklist': {'can_use': True}, ...})
    """
    missing = []
    for service_name, asset_type in PROPOSAL_SERVICE_TO_ASSET.items():
        if generated_assets:
            # Fuente de verdad: assets realmente generados
            asset_info = generated_assets.get(asset_type, {})
            if not asset_info.get('can_use', False):
                missing.append(service_name)
        else:
            # Fallback (legacy): catalogo estatico
            if not is_asset_implemented(asset_type):
                missing.append(service_name)
    
    score = 1.0 if not missing else (len(PROPOSAL_SERVICE_TO_ASSET) - len(missing)) / len(PROPOSAL_SERVICE_TO_ASSET)
    return score, missing
```

**Nota**: `asset_generation_report.json` tiene forma:
```json
{
  "generated_assets": {
    "seo_checklist": {"confidence_score": 0.5, "can_use": true},
    ...
  }
}
```

**Validacion**:
- Test: `generated_assets` con 4 de 7 assets → score = 4/7 = ~0.57
- Test: `generated_assets` con 7 de 7 → score = 1.0
- Test: `generated_assets=None` → usa catalogo (comportamiento legacy)

---

## Post-Ejecucion (al finalizar la sesion)

1. **Marcar checklist** en `.opencode/plans/06-checklist-implementacion.md`:
   - FASE-1-A: estado y tareas completadas

2. **Ejecutar log_phase_completion.py**:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-1-A \
    --desc "FIX-1 template engine conditionals + FIX-2 coherence validator generated_assets" \
    --archivos-nuevos "tests/commercial_documents/test_template_conditionals.py,tests/commercial_documents/test_coherence_generated_assets.py" \
    --archivos-mod "modules/commercial_documents/v4_proposal_generator.py,modules/commercial_documents/coherence_validator.py" \
    --tests "N" \
    --check-manual-docs
```

3. **Actualizar 09-documentacion-post-proyecto.md**:

```markdown
## Seccion B: Funcionalidades Nuevas
| Feature | Modulo | Descripcion | Fase |
|---------|--------|-------------|------|
| Template conditionals | v4_proposal_generator | Pre-procesador {{if}}...{{endif}} | FASE-1-A |
| Coherence truth source | coherence_validator | Usa generated_assets en vez de catalogo estatico | FASE-1-A |

## Seccion D: Metricas Acumulativas
| Metrica | Valor | Fase |
|---------|-------|------|
| Tests nuevos FASE-1-A | N | FASE-1-A |
```

4. **Guardar evidencia**:
```bash
cp modules/commercial_documents/v4_proposal_generator.py evidence/fase-1-A/
cp modules/commercial_documents/coherence_validator.py evidence/fase-1-A/
```

---

## Criterios de Completitud

- [ ] FIX-1 implementado: `_preprocess_conditionals` procesa `{{if}}...{{endif}}` correctamente
- [ ] FIX-1 testeado: 3 casos de test pasan (incluir, excluir, sin residuos de template)
- [ ] FIX-2 implementado: `_check_promised_assets_exist` usa `generated_assets`
- [ ] FIX-2 testeado: score refleja assets realmente generados (0.57 para 4/7)
- [ ] `run_all_validations.py --quick` pasa (o solo fallas preexistentes)
- [ ] `log_phase_completion.py` ejecutado
- [ ] Checklist maestro actualizado

---

## Restricciones

- **NO ejecutar v4complete** — reservado para FASE-2.
- **Max 60 iteraciones**.
- **NO modificar otros modulos** (monthly_report, scrubber, etc.) — reservado para FASE-1-B.
- Si un fix requiere mas iteraciones de lo previsto, priorizar FIX-1 y dejar FIX-2 para sesion de recuperacion.

---

*Prompt generado por orquestador siguiendo phased_project_executor.md v2.10.0*
