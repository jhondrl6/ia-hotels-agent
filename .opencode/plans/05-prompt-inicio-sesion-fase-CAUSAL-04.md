
# FASE RELEASE-4.21.0: Documentacion final y sincronizacion de version

**ID**: FASE-RELEASE-4.21.0
**Objetivo**: Ejecutar el workflow completo de release segun CONTRIBUTING.md — actualizar VERSION.yaml, sync automatico, CHANGELOG, GUIA_TECNICA, DOMAIN_PRIMER, SYSTEM_STATUS, y registro post-fase.
**Dependencias**: FASE-CAUSAL-01, FASE-CAUSAL-02, FASE-CAUSAL-03 (TODAS completadas)
**Skill**: iah-cli-phased-execution
**Contexto completo**: `.opencode/plans/context/consolidacion_context.md`
**Workflow documental**: `docs/CONTRIBUTING.md` §55-186

---

## Contexto

Version actual en VERSION.yaml: 4.20.0 (codename: "Agent Harness v3.2.0 Refactor")
Version target: 4.21.0

El ecosistema de documentacion de iah-cli tiene un flujo explicito que mi plan original ignoro. Este prompt implementa el flujo correcto segun CONTRIBUTING.md.

**VERSION.yaml** es la fuente unica de verdad. De ahi se sincronizan headers en 6 archivos. CHANGELOG.md y GUIA_TECNICA.md requieren edicion manual adicional. El release debe pasar por el Version Sync Gate.

---

## Tareas

### Tarea 1: Actualizar VERSION.yaml

**Archivo**: `VERSION.yaml`

Editar la version y agregar el release note al tope del bloque de comentarios:

```yaml
version: "4.21.0"
codename: "Consolidacion AEO/IAO"
release_date: "YYYY-MM-DD"
```

Agregar al tope de los comentarios de versiones:

```yaml
# v4.21.0 - CONSOLIDACION AEO/IAO
# - Scorecard V6: 5 filas -> 4 filas (GEO, GBP, AEO, SEO)
# - Eliminado score redundante IAO ("Optimizacion ChatGPT")
# - Eliminado Voice Readiness (retornaba "--" hardcodeado, nunca midio nada)
# - Eliminado "_calculate_iao_score()" de v4_diagnostic_generator.py
# - Eliminado "_calculate_score_ia()" de v4_diagnostic_generator.py
# - Eliminado "_calculate_voice_readiness_score()" de v4_diagnostic_generator.py
# - Renombrado _calculate_schema_infra_score() -> _calculate_aeo_score()
# - Eliminado IAO de gap_analyzer.py: 3 pilares -> 2 pilares (GBP + AEO)
# - Eliminado IAO de report_builder.py: scorecards y metodos duplicados
# - Regla: sin Asset = sin score en el diagnostico
# - aeo_metrics_gen.py se mantiene como modulo tecnico interno
```

### Tarea 2: Ejecutar sync automatico de versiones

**Ejecutar**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python scripts/sync_versions.py
```

Esto actualiza automaticamente los headers de:
- AGENTS.md
- README.md
- .cursorrules
- docs/CONTRIBUTING.md
- docs/GUIA_TECNICA.md
- docs/contributing/REGISTRY.md (solo fecha)

**Verificar**:
```bash
python scripts/version_consistency_checker.py
```

Debe pasar sin discrepancias. Si falla, diagnosticar y corregir antes de continuar.

### Tarea 3: Actualizar CHANGELOG.md

**Archivo**: `CHANGELOG.md`

Agregar al INICIO (despues de `# Changelog`) antes de la entrada 4.20.0:

```markdown
## [4.21.0] - YYYY-MM-DD

### ELIMINADO - Redundancia AEO/IAO en scorecard diagnostico
- Template V6: eliminadas filas "Visibilidad en IA (AEO)" y "Optimizacion ChatGPT (IAO)"
- Scorecard unificado bajo "AEO - Infraestructura para IAs" (XX/100) — dato 100% medible del audit web
- Regla de negoco: sin Asset = sin score en el diagnostico

### ELIMINADO - Metodos IAO/Voice de modulos internos
- v4_diagnostic_generator.py: eliminados _calculate_iao_score(), _calculate_score_ia(), _calculate_voice_readiness_score()
- v4_diagnostic_generator.py: renombrado _calculate_schema_infra_score() -> _calculate_aeo_score()
- gap_analyzer.py: eliminado pilar "Momentum IA", redistribucion 3->2 pilares (GBP + AEO)
- report_builder.py: eliminado _calculate_iao_score() y filas IAO de scorecards

### LIMPIEZA - Dead code
- Voice readiness eliminado (retornaba "--" hardcodeado)
- IATester wrapper eliminado (requiere GA4 real, no funciona en produccion actual)

### NOTAS
- aeo_metrics_gen.py se mantiene como modulo tecnico interno (no comercial)
- GA4 no modificado: puede enriquecer mediciones AEO en el futuro pero no genera score separado
```

### Tarea 4: Verificar y actualizar GUIA_TECNICA.md

**Archivo**: `docs/GUIA_TECNICA.md`

Segun CONTRIBUTING.md §86-93, la GUIA_TECNICA.md debe tener notas tecnicas para cambios de arquitectura.

Verificar si existe una seccion de "Notas de Cambios" o similar. Si existe, agregar:

```markdown
### Notas de Cambios v4.21.0

**Modulos afectados:**
- v4_diagnostic_generator.py: eliminacion de 3 metodos, renombramiento 1
- gap_analyzer.py: eliminacion de 1 pilar, redistribucion de perdida
- report_builder.py: eliminacion de metodo duplicado y referencias IAO
- diagnostico_v6_template.md: scorecard de 5 a 4 filas

**Backwards compatibility:**
- Variables de template eliminadas (iao_score, iao_status, voice_readiness_score, voice_readiness_status)
  Si algun template personalizado las referencia, fallara con KeyError en Template.safe_substitute()
- Metodos eliminados son internos, no son API publica del modulo
- El score AEO (_calculate_aeo_score) mantiene la misma logica de calculo que el anterior schema_infra_score
```

Si NO existe una seccion de notas tecnicas, crearla al final del archivo siguiendo el formato existente.

### Tarea 5: Verificar DOMAIN_PRIMER.md

**Ejecutar**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python scripts/doctor.py --context
```

Verificar que DOMAIN_PRIMER.md no referencie metodos que eliminamos:
- No debe mencionar `_calculate_iao_score()`
- No debe mencionar `_calculate_voice_readiness_score()`
- Si los menciona, ejecutar: `python scripts/doctor.py --regenerate-domain-primer`

No hubo modulos nuevos ni eliminados, solo cambios internos en metodos existentes. El DOMAIN_PRIMER deberia no necesitar regeneracion, pero verificar.

### Tarea 6: Regenerar SYSTEM_STATUS.md

**Ejecutar**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python main.py --doctor --status
```

Esto regenera `.agent/SYSTEM_STATUS.md` con el estado actualizado del ecosistema.

### Tarea 7: Ejecutar log_phase_completion.py

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python scripts/log_phase_completion.py \
    --fase FASE-RELEASE-4.21.0 \
    --desc "Release 4.21.0: Consolidacion AEO/IAO - eliminacion scores redundantes" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/templates/diagnostico_v6_template.md,modules/analyzers/gap_analyzer.py,modules/generators/report_builder.py" \
    --archivos-nuevos "" \
    --check-manual-docs
```

### Tarea 8: Verificar integridad de symlink

**Ejecutar**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python main.py --doctor
```

Verificar que no reporte errores de "Symlink integrity" en `.agent/workflows`.

### Tarea 9: Validacion final pre-commit

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python scripts/run_all_validations.py --quick 2>/dev/null || echo "Validacion completa no disponible"
git diff --stat
```

---

## Criterios de Aceptacion

- [ ] VERSION.yaml: version = "4.21.0", codename actualizado, fecha correcta
- [ ] sync_versions.py ejecutado sin errores
- [ ] version_consistency_checker.py paso sin discrepancias
- [ ] CHANGELOG.md tiene entrada [4.21.0] con cambios documentados
- [ ] docs/GUIA_TECNICA.md tiene notas tecnicas de v4.21.0
- [ ] DOMAIN_PRIMER.md no referencia metodos eliminados
- [ ] SYSTEM_STATUS.md regenerado via --doctor --status
- [ ] log_phase_completion.py ejecutado con --check-manual-docs
- [ ] Version Sync Gate paso (sin `(!)` en output del script)
- [ ] No hay [GAP] en DOCUMENTATION AUDIT
- [ ] `git diff --stat` muestra todos los archivos modificados

---

## Restricciones

- NO modificar codigo fuente de modulos (eso ya se hizo en Fases 1-3)
- NO tocar ROADMAP.md
- Solo documentacion, version y sincronizacion
- El sync_versions.py es la fuente automatica de headers — no editar headers manualmente

---

## Post-Ejecucion (OBLIGATORIO)

El `log_phase_completion.py` en Tarea 7 YA incluye la documentacion post-fase.

Verificar adicionalmente:
```bash
# Verificar que la entrada existe en REGISTRY
grep "FASE-RELEASE-4.21.0" docs/contributing/REGISTRY.md

# Verificar que CHANGELOG tiene la entrada
grep "4.21.0" CHANGELOG.md
```

---

## Checklist de Completitud

- [ ] VERSION.yaml actualizado a 4.21.0
- [ ] sync_versions.py ejecutado sin errores
- [ ] CHANGELOG.md con entrada 4.21.0
- [ ] GUIA_TECNICA.md con notas tecnicas
- [ ] DOMAIN_PRIMER.md verificado
- [ ] SYSTEM_STATUS.md regenerado
- [ ] log_phase_completion.py ejecutado con --check-manual-docs
- [ ] Version Sync Gate paso
- [ ] No hay [GAP] en DOCUMENTATION AUDIT
- [ ] Symlink integrity verifica
- [ ] `git add -A && git commit` realizado
