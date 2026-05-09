# Prompt de Inicio de Sesion: FASE-RELEASE-4.43.0

> **Fase**: RELEASE — Cierre, Documentacion Oficial, Version Bump  
> **Plan maestro**: `PLAN-REFACTOR-TERMALES-20260508.md`  
> **Iteraciones max**: 60  
> **Contexto previo**: TODAS las fases de implementacion completadas (PRE, 1-A, 1-B, 2-A, 2-B, 3)  
> **Regla**: NO modifica codigo fuente. Solo documentacion y validaciones.
> **Estado**: ✅ COMPLETADA — 2026-05-08 21:15

---

## Tareas de la Fase

TAREAS DE LA FASE:
  [ ] Recopilar datos de 09-documentacion-post-proyecto.md
  [ ] Version bump (4.42.0 → 4.43.0)
  [ ] Generar CHANGELOG.md entrada oficial
  [ ] Generar/actualizar GUIA_TECNICA.md notas por fase
  [ ] Ejecutar sync_versions.py
  [ ] Ejecutar run_all_validations.py --quick
  [ ] Ejecutar log_phase_completion.py para RELEASE
  [ ] Marcar plan como COMPLETADO

CONTADOR:
  - Total tareas: 7
  - Comandos largos: 0 (scripts rapidos)
  - Estado: dentro del limite R3

---

## Contexto de Fases Anteriores

Todas las fases de implementacion completadas:
- FASE-PRE: Saneamiento
- FASE-1-A: FIX-1 + FIX-2 (template + coherence)
- FASE-1-B: FIX-3 + FIX-4 (monthly_report + scrubber)
- FASE-2-A: FIX-5 + FIX-6 + FIX-7 (deteccion + enriquecimiento)
- FASE-2-B: Verificacion E2E v4complete Termales (veredicto documentado)
- FASE-3: FIX-9 + FIX-10 (policy gates)

---

## Instrucciones Detalladas

### Paso 4.5.1: Registrar Fases en REGISTRY.md

Ejecutar para cada fase (PRE, 1-A, 1-B, 2-A, 2-B, 3):

```bash
# Ejemplo FASE-1-A
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-1-A \
    --desc "FIX-1 template conditionals + FIX-2 coherence truth source" \
    --check-manual-docs

# Ejemplo FASE-2-B
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-2-B \
    --desc "Verificacion E2E v4complete Termales: {veredicto}" \
    --check-manual-docs

# Repetir para todas las fases del plan
```

### Paso 4.5.2: Sincronizar Versiones

```bash
./venv/Scripts/python.exe scripts/sync_versions.py
./venv/Scripts/python.exe scripts/version_consistency_checker.py
```

### Paso 4.5.3: Validar CHANGELOG.md

Verificar que existe entrada `[4.43.0]` con formato:

```markdown
## [4.43.0] - Refactorizacion Termales Santa Rosa de Cabal — 2026-05-XX

### Objetivo
Corregir bugs criticos en pipeline v4complete detectados en analisis de Termales Santa Rosa de Cabal.

### Cambios Implementados
- FIX-1: Template engine procesa condicionales {{if}}...{{endif}}
- FIX-2: Coherence validator usa generated_assets como fuente de verdad
- FIX-3: Monthly report genera tabla dinamica desde asset_generation_report.json
- FIX-4: Content Scrubber Rule 6 detecta [PENDING_*] y bloquea publicacion
- FIX-5: SitePresenceChecker hardening con logging detallado y status unknown
- FIX-6: indirect_traffic generator lee audit_context para recomendaciones
- FIX-7: FAQ generator extrae servicios reales del sitio via scraping
- FIX-9: Gate proposal_asset_alignment cambia a BLOCKED cuando alignment < 50%
- FIX-10: Nuevo gate tier_c_onboarding_required para propuestas Tier C

### Archivos Nuevos
| Archivo | Descripcion |
|---------|-------------|
| tests/commercial_documents/test_template_conditionals.py | Tests para pre-procesador condicional |
| tests/commercial_documents/test_coherence_generated_assets.py | Tests para coherence con generated_assets |
| tests/postprocessors/test_pending_markers.py | Tests para scrubber [PENDING*] |
| tests/asset_generation/test_monthly_report_dynamic.py | Tests para monthly report dinamico |
| tests/asset_generation/test_site_presence_hardening.py | Tests para SitePresenceChecker hardening |
| tests/asset_generation/test_indirect_traffic_context.py | Tests para indirect_traffic con audit |
| tests/asset_generation/test_faq_site_extraction.py | Tests para FAQ con scraping |
| tests/quality_gates/test_tier_c_onboarding_gate.py | Tests para gate Tier C |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| modules/commercial_documents/v4_proposal_generator.py | FIX-1: _preprocess_conditionals |
| modules/commercial_documents/coherence_validator.py | FIX-2: _check_promised_assets_exist usa generated_assets |
| modules/postprocessors/content_scrubber.py | FIX-4: Rule 6 _fix_pending_markers |
| modules/asset_generation/monthly_report_generator.py | FIX-3: _generate_assets_table dinamica |
| modules/quality_gates/publication_gates.py | FIX-5: hardening except + FIX-9: alignment BLOCKED + FIX-10: Tier C gate |
| modules/asset_generation/site_presence_checker.py | FIX-5: investigacion y correccion de fallos |
| modules/asset_generation/indirect_traffic_generator.py | FIX-6: lectura audit_report.json |
| modules/asset_generation/faq_generator.py | FIX-7: scraping previo del sitio |

### Tests
- N tests nuevos, 0 regresiones
```

### Paso 4.5.4: Validar GUIA_TECNICA.md

Verificar que cada fase tiene nota tecnica:

```markdown
## Notas de Cambios v4.43.0

### FASE-1-A: Template + Coherence
- **Modulo**: commercial_documents
- **Problema**: string.Template no procesaba {{if}}; coherence usaba catalogo estatico
- **Solucion**: Pre-procesador regex + generated_assets como fuente de verdad
- **Backwards compatibility**: Coherence validator mantiene fallback a catalogo si generated_assets=None

### FASE-1-B: Scrubber + Monthly Report
- **Modulo**: postprocessors, asset_generation
- **Problema**: [PENDING*] pasaba limpio; monthly_report era estatico
- **Solucion**: Rule 6 con block_publication; tabla dinamica desde JSON
- **Backwards compatibility**: Monthly report usa fallback si JSON ausente

### FASE-2-A: Deteccion + Enriquecimiento
- **Modulo**: quality_gates, asset_generation
- **Problema**: SitePresenceChecker fallaba silenciosamente; generadores usaban contenido generico
- **Solucion**: Log completo + unknown status; lectura de audit y scraping del sitio
- **Backwards compatibility**: Todos los generadores mantienen fallback generico

### FASE-2-B: Verificacion E2E
- **Modulo**: pipeline v4complete
- **Problema**: N/A (verificacion)
- **Solucion**: v4complete ejecutado para Termales, veredicto: {EFECTIVA/PARCIAL/NO EFECTIVA}

### FASE-3: Policy Gates
- **Modulo**: quality_gates
- **Problema**: Gates no bloqueantes permitian publicar documentos defectuosos
- **Solucion**: Alignment <50% → BLOCKED; Tier C → requiere onboarding
- **Backwards compatibility**: Cambio de policy documentado; comportamiento anterior era intencional
```

### Paso 4.5.5: Validacion Final

```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe scripts/doctor.py --status
./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer
```

**Checklist final**:
- [ ] `run_all_validations.py --quick` pasa (4/4)
- [ ] `doctor.py --status` sin errores
- [ ] `version_consistency_checker.py` pasa
- [ ] `sync_versions.py` ejecutado
- [ ] CHANGELOG.md tiene formato correcto
- [ ] GUIA_TECNICA.md tiene notas por fase
- [ ] Todos los archivos de documentacion actualizados

---

## Post-Ejecucion (al finalizar la sesion)

1. **Marcar checklist** en `.opencode/plans/06-checklist-implementacion.md`:
   - FASE-RELEASE: `COMPLETADA`
   - Plan maestro: `COMPLETADO`

2. **Ejecutar log_phase_completion.py**:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-RELEASE-4.43.0 \
    --desc "Release: version bump 4.43.0, CHANGELOG, GUIA_TECNICA, validaciones finales" \
    --check-manual-docs
```

3. **Actualizar PLAN-MAESTRO**:
   - Estado: `COMPLETADO`
   - Fecha de cierre: hoy

---

## Criterios de Completitud

- [ ] Todos los `log_phase_completion.py` ejecutados (PRE, 1-A, 1-B, 2-A, 2-B, 3, RELEASE)
- [ ] `sync_versions.py` ejecutado
- [ ] CHANGELOG.md tiene entrada [4.43.0] con formato correcto
- [ ] GUIA_TECNICA.md tiene notas tecnicas para cada fase
- [ ] `run_all_validations.py --quick` pasa (4/4)
- [ ] `doctor.py --status` sin errores
- [ ] Plan maestro marcado como COMPLETADO
- [ ] Checklist maestro: todas las fases en COMPLETADA

---

## Restricciones

- **NO modificar codigo fuente** — esta fase es solo documentacion y validaciones.
- **NO ejecutar v4complete** — ya se ejecuto en FASE-2-B.
- **Max 60 iteraciones**.
- Si falla validacion, documentar y NO marcar como completado hasta resolver.

---

*Prompt generado por orquestador siguiendo phased_project_executor.md v2.10.0*
