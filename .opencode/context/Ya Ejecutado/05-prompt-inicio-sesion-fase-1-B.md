# Prompt de Inicio de Sesion: FASE-1-B

> **Fase**: 1-B — Bugs de Contenido: Content Scrubber + Monthly Report  
> **Plan maestro**: `PLAN-REFACTOR-TERMALES-20260508.md`  
> **Iteraciones max**: 60  
> **Contexto previo**: FASE-PRE + FASE-1-A completadas  
> **Fixes**: FIX-4, FIX-3  

---

## Tareas de la Fase

TAREAS DE LA FASE:
  [ ] Investigacion de codigo existente (content_scrubber.py, monthly_report_generator.py)
  [ ] Implementar FIX-4: Content Scrubber Rule 6 [PENDING*]
  [ ] Implementar FIX-3: monthly_report data-driven
  [ ] Verificar con tests unitarios
  [ ] Documentacion post-fase

CONTADOR:
  - Total tareas: 4
  - Comandos largos: 0
  - Estado: dentro del limite R3

---

## Contexto de Fases Anteriores

- FASE-PRE: Saneamiento completado
- FASE-1-A: Template engine + Coherence validator corregidos
  - `v4_proposal_generator.py` ahora pre-procesa `{{if}}...{{endif}}`
  - `coherence_validator.py` ahora verifica `generated_assets`

---

## Instrucciones Detalladas

### FIX-4: Content Scrubber Rule 6 — [PENDING*] Detection

**Archivo**: `modules/postprocessors/content_scrubber.py` (~L76-104)  
**Problema**: Solo 5 reglas. Ninguna detecta marcadores `[PENDING_ONBOARDING]` o similares.  
**Solucion**: Agregar `_fix_pending_markers()` como Rule 6.

**Implementacion sugerida**:
```python
def _fix_pending_markers(self, text, context):
    """Rule 6: Detecta y bloquea marcadores [PENDING_*]."""
    import re
    pattern = r'\[PENDING_[A-Z_]+\]'
    matches = re.findall(pattern, text)
    
    if matches:
        return {
            'fixed_text': text,  # No se reemplaza automaticamente — requiere intervencion
            'issues_found': [f"Pending marker found: {m}" for m in matches],
            'block_publication': True,
            'severity': 'CRITICAL'
        }
    return {'fixed_text': text, 'issues_found': [], 'block_publication': False}
```

**Integracion**: Llamar `_fix_pending_markers` dentro del pipeline de scrubbing (similar a las otras 5 reglas).

**Validacion**:
- Test: texto con `[PENDING_ONBOARDING]` → `block_publication=True`, issues_found no vacio
- Test: texto con `[PENDING_USP]` → mismo resultado
- Test: texto sin marcadores → `block_publication=False`
- Test: texto con `PENDING` sin corchetes → no debe detectar

### FIX-3: Monthly Report Data-Driven

**Archivo**: `modules/asset_generation/monthly_report_generator.py` (~L170-182)  
**Problema**: Tabla "Resumen de Assets Entregados" es texto hardcodeado. Siempre muestra 9 assets como "Entregado", incluyendo los que nunca se generaron.  
**Solucion**: Leer `asset_generation_report.json` y generar tabla dinamicamente.

**Implementacion sugerida**:
```python
def _generate_assets_table(self, asset_report_path=None):
    """Genera tabla dinamica basada en asset_generation_report.json."""
    import json, os
    
    # Path por defecto
    if asset_report_path is None:
        asset_report_path = os.path.join(self.output_dir, 'asset_generation_report.json')
    
    assets_data = {}
    if os.path.exists(asset_report_path):
        with open(asset_report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
            assets_data = report.get('generated_assets', {})
    
    # Mapeo de nombres display
    rows = []
    for asset_type, info in assets_data.items():
        status = "✅ Entregado" if info.get('can_use', False) else "⚠️ No disponible"
        confidence = info.get('confidence_score', 0.0)
        rows.append(f"| {asset_type} | {status} | {confidence} |")
    
    # Si no hay assets, tabla vacia con nota
    if not rows:
        return "| No se generaron assets en esta ejecucion |\n"
    
    header = "| Asset | Estado | Confianza |\n|-------|--------|----------|\n"
    return header + "\n".join(rows)
```

**Notas**:
- Usar nombres del catalogo real, NO "Geo Playbook" ni "Voice Assistant Guide" (no existen en el catalogo).
- Reemplazar la tabla hardcodeada en `generate()` por llamada a `_generate_assets_table()`.

**Validacion**:
- Test: `asset_generation_report.json` con 6 assets, 3 `can_use=True`, 3 `can_use=False` → tabla refleja estados reales
- Test: archivo JSON ausente → tabla con nota "No se generaron assets"
- Test: output NO contiene "Geo Playbook" ni "Voice Assistant Guide"

---

## Post-Ejecucion (al finalizar la sesion)

1. **Marcar checklist** en `.opencode/plans/06-checklist-implementacion.md`:
   - FASE-1-B: estado y tareas completadas

2. **Ejecutar log_phase_completion.py**:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-1-B \
    --desc "FIX-4 Content Scrubber Rule 6 [PENDING*] + FIX-3 monthly_report data-driven" \
    --archivos-nuevos "tests/postprocessors/test_pending_markers.py,tests/asset_generation/test_monthly_report_dynamic.py" \
    --archivos-mod "modules/postprocessors/content_scrubber.py,modules/asset_generation/monthly_report_generator.py" \
    --tests "N" \
    --check-manual-docs
```

3. **Actualizar 09-documentacion-post-proyecto.md**:

```markdown
## Seccion B: Funcionalidades Nuevas
| Feature | Modulo | Descripcion | Fase |
|---------|--------|-------------|------|
| Pending marker detection | content_scrubber | Rule 6: detecta [PENDING_*] y bloquea publicacion | FASE-1-B |
| Dynamic monthly report | monthly_report_generator | Tabla generada desde asset_generation_report.json | FASE-1-B |

## Seccion D: Metricas Acumulativas
| Metrica | Valor | Fase |
|---------|-------|------|
| Tests nuevos FASE-1-B | N | FASE-1-B |
```

4. **Guardar evidencia**:
```bash
cp modules/postprocessors/content_scrubber.py evidence/fase-1-B/
cp modules/asset_generation/monthly_report_generator.py evidence/fase-1-B/
```

---

## Criterios de Completitud

- [ ] FIX-4 implementado: `_fix_pending_markers` detecta `[PENDING_*]` y activa `block_publication=True`
- [ ] FIX-4 testeado: 4 casos de test pasan
- [ ] FIX-3 implementado: `_generate_assets_table` lee `asset_generation_report.json`
- [ ] FIX-3 testeado: tabla refleja estados reales de assets
- [ ] `run_all_validations.py --quick` pasa (o solo fallas preexistentes)
- [ ] `log_phase_completion.py` ejecutado
- [ ] Checklist maestro actualizado

---

## Restricciones

- **NO ejecutar v4complete** — reservado para FASE-2.
- **Max 60 iteraciones**.
- **NO modificar SitePresenceChecker, FAQ, indirect_traffic** — reservado para FASE-2.
- **NO modificar gates de policy** — reservado para FASE-3.

---

*Prompt generado por orquestador siguiendo phased_project_executor.md v2.10.0*
