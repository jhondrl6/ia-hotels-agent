# FASE-3-CONTENT: Fix local_content + evidence_tier + all_aligned

**ID**: FASE-3-CONTENT
**Objetivo**: Corregir local_content_generator para validar location pre-LLM, unificar evidence_tier en todo el delivery, y renombrar all_aligned → all_covered con alias deprecado.
**Dependencias**: FASE-2-DEFAULT (✅)
**Duración estimada**: 2-3 horas
**Skill**: `phased-workflow-self-improvement` (reglas de ejecución directa)
**Modo de ejecución**: DIRECTO — código puro, sin comandos externos ni subagentes.

---

## Contexto

**Problema 1 (R4)**: `local_content_generator.py` genera títulos como `"Hotel en  - Lo que debes saber"` porque `hotel_data.get("city")` está vacío y no hay validación pre-LLM.

**Problema 2 (R9)**: `financial_scenarios.json` dice `evidence_tier: "B"` mientras el diagnóstico YAML dice `financial_evidence_tier: "C"`. El tier real (adr=handler, occupancy=regional, direct_channel=default) es C. El JSON está inflado porque se computa en momentos distintos con lógica diferente.

**Problema 3 (R5)**: `proposal_asset_alignment.py` tiene `all_aligned = len(missing)==0` (mide cobertura) pero el nombre induce a error. Debería llamarse `all_covered`.

---

## Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-1-COH | ✅ Completada |
| FASE-2-DEFAULT | ✅ Completada |

---

## Base Técnica Disponible

- `modules/asset_generation/local_content_generator.py` — generador basado en LLM, ~609 líneas
- `modules/financial_engine/` — financial_scenarios.json writer y diagnostic generator
- `modules/quality_gates/proposal_asset_alignment.py` — L76-85, `all_aligned` property
- Tests existentes en `tests/asset_generation/`, `tests/quality_gates/`, `tests/financial_engine/`

---

## Tareas

### T1: Validación de location en local_content_generator.py
**Objetivo**: Evitar que el LLM genere contenido con location vacía.

**Cambios**:
1. Antes de pasar datos al LLM, validar location:
   ```python
   location = (hotel_data.get("city") or hotel_data.get("state") 
               or hotel_data.get("region") or "")
   if not location or location.strip() == "":
       location = "Colombia"  # fallback genérico pero informativo
   ```
2. Asegurar que `location` se pasa al template/prompt del LLM.
3. Si el generador usa `hotel_data["city"]` directamente en el prompt, reemplazar por `location`.

**Criterios de aceptación**:
- [ ] `grep "Hotel en  -" output/*/local_content_page/*.md` → 0 matches (después de prueba manual)
- [ ] Tests unitarios: `city` vacío → usa fallback "Colombia"; `city` presente → usa city

### T2: Unificar evidence_tier en todo el delivery
**Objetivo**: Computar evidence_tier UNA sola vez y propagar a JSON y YAML.

**Cambios**:
1. Encontrar dónde se computa `evidence_tier` para `financial_scenarios.json` y dónde para el diagnóstico YAML.
2. Extraer la lógica de computación a un único método helper (o reutilizar el existente).
3. Asegurar que tanto el JSON writer como el diagnostic generator usen el mismo helper.
4. El tier debe basarse en `financial_sources` real (adr, occupancy, direct_channel).

**Criterios de aceptación**:
- [ ] `financial_scenarios.json.breakdown.evidence_tier` == `diagnostic YAML financial_evidence_tier`
- [ ] Tests: mock de financial_sources → tier consistente en ambos outputs

### T3: Renombrar all_aligned → all_covered
**Objetivo**: Clarificar semántica sin romper backwards compatibility.

**Cambios**:
1. En `proposal_asset_alignment.py` L76-85:
   ```python
   @property
   def all_covered(self) -> bool:
       """True si todos los servicios están cubiertos (generado o en producción)."""
       return len(self.missing) == 0
   
   @property
   def all_aligned(self) -> bool:
       """DEPRECATED: Use all_covered instead."""
       return self.all_covered
   ```
2. Actualizar referencias internas en `proposal_asset_alignment.py` para usar `all_covered`.
3. Buscar con grep otros consumidores de `all_aligned` y evaluar si deben migrarse a `all_covered`.

**Criterios de aceptación**:
- [ ] `all_covered` property existe y retorna correctamente
- [ ] `all_aligned` sigue funcionando como alias deprecado (backwards compat)
- [ ] 0 usages internos de `all_aligned` en proposal_asset_alignment.py

### T4: Tests para los 3 cambios
**Objetivo**: Validar local_content location, evidence_tier consistency, y all_covered.

**Tests**:
1. `test_local_content_fallback_location`: city vacío → location = "Colombia"
2. `test_local_content_uses_city_when_present`: city = "Pereira" → location = "Pereira"
3. `test_evidence_tier_consistent_json_vs_yaml`: mismo input → mismo tier en ambos formatos
4. `test_all_covered_returns_same_as_old_all_aligned`: alias funciona

**Criterios de aceptación**:
- [ ] 4 tests nuevos pasan
- [ ] 0 regresiones en tests existentes de los módulos afectados
- [ ] `run_all_validations.py --quick` pasa 4/4

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`** — Marcar FASE-3-CONTENT como ✅ Completada.
2. **`06-checklist-implementacion.md`** — Marcar todos los items de FASE-3-CONTENT como ✅.
3. **`09-documentacion-post-proyecto.md`** — Sección E: agregar archivos modificados. Sección D: actualizar métricas.
4. **`log_phase_completion.py`**:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-3-CONTENT \
    --desc "Fix local_content location validation, unificar evidence_tier, renombrar all_aligned a all_covered con alias deprecado" \
    --archivos-mod "modules/asset_generation/local_content_generator.py,modules/financial_engine/,modules/quality_gates/proposal_asset_alignment.py" \
    --tests "4" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] **T1 completo**: local_content valida location pre-LLM, fallback a "Colombia"
- [ ] **T2 completo**: evidence_tier consistente entre JSON y YAML
- [ ] **T3 completo**: `all_covered` existe, `all_aligned` funciona como alias deprecado
- [ ] **T4 completo**: 4 tests nuevos pasan, 0 regresiones
- [ ] **Validaciones del proyecto**: `python scripts/run_all_validations.py --quick` pasa 4/4
- [ ] **`dependencias-fases.md` actualizado**: Estado de FASE-3-CONTENT marcado ✅
- [ ] **Documentación afiliada**: `09-documentacion-post-proyecto.md` actualizado
- [ ] **log_phase_completion.py ejecutado**: REGISTRY.md tiene entrada FASE-3-CONTENT

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- **NO ejecutar v4complete** en esta fase.
- **NO modificar ROADMAP.md** — solo en FASE-RELEASE.
- **Máximo 60 iteraciones**.
- **Presupuesto estimado**: ~30-40 iteraciones trabajo + ~20 docs/verificación.
