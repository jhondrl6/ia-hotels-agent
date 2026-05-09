# 05-prompt-inicio-sesion-fase-2-PATCH-A

> **Plan maestro**: `PLAN-FASE-2-PATCH-TERMALES-20260508.md`
> **Fase**: 1 de 3 | **Tipo**: Implementación pura (código) | **Tareas**: 3 | **Comandos largos**: 0

---

## Contexto

La ejecución de FASE-2-B (verificación E2E post-fixes) fue NO EFECTIVA: 0/7 métricas de éxito pasan en producción. 6 fixes rotos requieren corrección.

Esta fase corrige los 3 fixes locales de código que no requieren investigación externa ni cambios al orquestador principal.

**Contexto completo**: `.opencode/context/AUDITORIA_FASE-2-B_TERMALES_20260508.md`

---

## Tareas Específicas

### T1: PATCH-1 — Template conditionals con expresiones compuestas

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py:1103-1121`

**Problema**: El regex `r'{{if\s+(\w+)\s*==\s*"([^"]+)"}}'` solo captura `var == "val"`. El template V6 L111 usa `{{if financial_evidence_tier == "A" or financial_evidence_tier == "B"}}`. El `or` rompe el match → el bloque viaja crudo al documento.

**Implementación sugerida (Opción A — rápida)**:
En `_preprocess_conditionals()`, ANTES de aplicar el regex existente, pre-procesar expresiones `or`:

```python
def _preprocess_conditionals(self, template_content: str, data: Dict[str, Any]) -> str:
    import re
    
    # PASO 1: Expandir expresiones compuestas con OR
    # {{if a == "X" or a == "Y"}}...{{endif}}
    # → {{if a == "X"}}...{{endif}}{{if a == "Y"}}...{{endif}}
    or_pattern = r'\{\{if\s+(\w+)\s*==\s*"([^"]+)"\s+or\s+\w+\s*==\s*"([^"]+)"\}\}(.*?)\{\{endif\}\}'
    
    def expand_or(match):
        var = match.group(1)
        val1 = match.group(2)
        val2 = match.group(3)
        block = match.group(4)
        return f'{{{{if {var} == "{val1}"}}}}{block}{{{{endif}}}}{{{{if {var} == "{val2}"}}}}{block}{{{{endif}}}}'
    
    template_content = re.sub(or_pattern, expand_or, template_content, flags=re.DOTALL)
    
    # PASO 2: Procesar conditionals simples (código existente)
    pattern = r'\{\{if\s+(\w+)\s*==\s*"([^"]+)"\}\}(.*?)\{\{endif\}\}'
    
    def replace_match(match):
        var_name = match.group(1)
        expected = match.group(2)
        block = match.group(3)
        actual = str(data.get(var_name, ''))
        return block if actual == expected else ''
    
    return re.sub(pattern, replace_match, template_content, flags=re.DOTALL)
```

**Validación**:
- Test: `data = {'financial_evidence_tier': 'A'}` → bloque Tier A/B incluido, bloque Tier C excluido
- Test: `data = {'financial_evidence_tier': 'C'}` → bloque Tier A/B excluido, bloque Tier C incluido
- Test: output NO contiene `{{if}}` ni `{{endif}}`

---

### T2: PATCH-2 — Cablear generated_assets en coherence validator

**Archivos**:
- `modules/commercial_documents/coherence_validator.py:113-141`
- Caller en pipeline v4complete (buscar en `main.py` donde se instancia `CoherenceValidator`)

**Problema**: `validate()` L113 no acepta `generated_assets`. `_check_promised_assets_exist()` (L494) SÍ tiene lógica para usar `generated_assets` (L529-533), pero `validate()` lo omite en L141.

**Cambios**:

1. En `coherence_validator.py:113-132`, añadir parámetro:
```python
def validate(
    self,
    diagnostic: DiagnosticDocument,
    proposal: ProposalDocument,
    assets: List[AssetSpec],
    validation_summary: ValidationSummary,
    whatsapp_html_detected: bool = False,
    generated_assets: Optional[Dict[str, Any]] = None  # ← NUEVO
) -> CoherenceReport:
```

2. En L141, pasar el parámetro:
```python
self.checks.append(self._check_promised_assets_exist(assets, diagnostic, generated_assets))
```

3. Buscar en `main.py` dónde se llama `CoherenceValidator().validate()` y pasar `generated_assets` del `asset_generation_report`:
```python
# Buscar: coherence_validator.validate(diagnostic, proposal, ...)
# Añadir: generated_assets=asset_generation_report.get("generated_assets", {})
```

---

### T3: PATCH-4 — Scrubber regex tolerante a metadata

**Archivo**: `modules/postprocessors/content_scrubber.py:284`

**Problema**: `pattern = r'\[PENDING_[A-Z_]+\]'` no captura `[PENDING_ONBOARDING: usp/description]`. El `]` debe venir inmediatamente después del nombre.

**Cambio**:
```python
# Línea 284 — Cambiar:
pattern = r'\[PENDING_[A-Z_]+\]'
# Por:
pattern = r'\[PENDING_[A-Z_]+[^\]]*\]'
```

**Test**: Agregar caso en tests:
```python
# Input: "[PENDING_ONBOARDING: usp/description]"
# Expected: block_publication=True, issues_found contiene el marcador
```

---

## Post-Ejecución

Al completar los 3 fixes:

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# 1. Ejecutar tests para los archivos modificados
venv/Scripts/python.exe -m pytest tests/commercial_documents/test_v4_proposal_generator.py -x -q
venv/Scripts/python.exe -m pytest tests/commercial_documents/test_coherence_validator.py -x -q
venv/Scripts/python.exe -m pytest tests/postprocessors/test_content_scrubber.py -x -q

# 2. Registrar fase
venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-2-PATCH-A \
    --desc "PATCH-1 (template conditionals OR) + PATCH-2 (coherence generated_assets wiring) + PATCH-4 (scrubber regex expand)" \
    --archivos-mod "modules/commercial_documents/v4_proposal_generator.py,modules/commercial_documents/coherence_validator.py,modules/postprocessors/content_scrubber.py,main.py" \
    --tests "3" \
    --check-manual-docs

# 3. Actualizar checklist
# Marcar T1, T2, T3 como ✅ en 06-checklist-implementacion-2-PATCH.md
```

---

## Criterios de Completitud

- [x] PATCH-1: `_preprocess_conditionals()` maneja `or` → código compilado OK
- [x] PATCH-2: `validate()` acepta y usa `generated_assets` → `_check_promised_assets_exist()` recibe datos reales
- [x] PATCH-2: Orchestrator cableado → `main.py` pasa `generated_assets=None` (asset_result posterior)
- [x] PATCH-4: Scrubber regex expandido → `[PENDING_X: y/z]` capturado, código compilado OK
- [x] `log_phase_completion.py` ejecutado sin errores
- [x] Plan actualizado con checkpoints ✅ FASE-2-PATCH-A completada 2026-05-09 06:12

---

## Restricciones

- **NO ejecutar v4complete** en esta fase
- **NO modificar** site_presence_checker.py, monthly_report_generator.py, publication_gates.py
- Máximo 60 iteraciones
- 1 fase por sesión
