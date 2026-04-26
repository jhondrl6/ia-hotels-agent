# FASE-RELEASE-4.36.0: Cierre + Documentacion

**ID**: FASE-RELEASE-4.36.0
**Objetivo**: Cerrar el ciclo de intervencion forense con documentacion completa, version bump, y validaciones finales.
**Dependencias**: FASE-A (completada), FASE-B (completada), FASE-C (completada), FASE-D (completada)
**Duracion estimada**: 1-1.5 horas
**Skill**: phased_project_executor v2.4.0

---

## Contexto

Esta fase cierra las intervenciones de los 4 hallazgos del Veredicto forense de AmaziliaHotel:
- Hallazgo 3 (ALTO): hotel_schema dual → FASE-A
- Hallazgo 5 (MEDIO): Comision OTA mal etiquetada → FASE-B
- Hallazgo 2b (MEDIO): open_graph asset roto → FASE-C
- gate_report presence (MEDIO): falsos missing → FASE-D

Las 4 fases de implementacion estan completadas y se necesita la documentacion oficial del repositorio.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A | Completada |
| FASE-B | Completada |
| FASE-C | Completada |
| FASE-D | Completada |

---

## Tareas

### Tarea 1: Version bump a 4.36.0

**Objetivo**: Actualizar VERSION.yaml y sincronizar.

**Pasos**:
1. Editar `VERSION.yaml`: bump version a 4.36.0
2. Agregar entrada de changelog en VERSION.yaml
3. Ejecutar: `./venv/Scripts/python.exe scripts/sync_versions.py`
4. Verificar: `./venv/Scripts/python.exe scripts/version_consistency_checker.py`

**Criterios de aceptacion**:
- [ ] VERSION.yaml dice 4.36.0
- [ ] sync_versions.py ejecuta sin errores
- [ ] version_consistency_checker.py pasa

### Tarea 2: Registrar fases en REGISTRY.md

**Objetivo**: Log phase completion para las 4 fases de implementacion.

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-A \
    --desc "Unificar hotel_schema dual: schema enriquecido como asset oficial" \
    --archivos-mod "modules/asset_generation/conditional_generator.py,modules/asset_generation/v4_asset_orchestrator.py" \
    --tests "N" \
    --check-manual-docs

./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-B \
    --desc "Corregir etiquetado Comision OTA en diagnostico comercial" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py" \
    --tests "N" \
    --check-manual-docs

./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-C \
    --desc "Reparar asset open_graph: template + cableado pain_id no_og_tags" \
    --archivos-nuevos "modules/asset_generation/templates/open_graph_template.html" \
    --archivos-mod "modules/pain_solution_mapper.py,modules/asset_generation/conditional_generator.py" \
    --tests "N" \
    --check-manual-docs

./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-D \
    --desc "gate_report con verificacion de presencia en sitio real" \
    --archivos-mod "modules/quality_gates/" \
    --tests "N" \
    --check-manual-docs
```

**Criterios de aceptacion**:
- [ ] REGISTRY.md tiene entradas para FASE-A, B, C, D
- [ ] No hay [GAP] en DOCUMENTATION AUDIT

### Tarea 3: CHANGELOG.md

**Objetivo**: Agregar entrada 4.36.0 con formato CONTRIBUTING.md.

```markdown
## [4.36.0] - PATCH Forense AmaziliaHotel (2026-04-XX)

### Objetivo
Corregir 4 hallazgos del audit forense: hotel_schema dual, etiquetado incorrecto de Comision OTA, asset open_graph roto, y gate_report con falsos missing.

### Cambios Implementados
- `conditional_generator.py` - Preferencia por schema enriquecido (geo_enriched) como asset oficial
- `v4_asset_orchestrator.py` - Bridge geo_enriched siempre aplica para hotel_schema
- `v4_diagnostic_generator.py` - Labels financieros semanticamente correctos
- `diagnostico_v6_template.md` - Variables alineadas con semantica correcta
- `pain_solution_mapper.py` - Cableado pain_id no_og_tags desde audit_report
- `modules/asset_generation/templates/open_graph_template.html` - Template OG tags (NUEVO)
- Gate report generator - Integracion SitePresenceChecker para presence verification

### Archivos Nuevos
| Archivo | Descripcion |
|---------|-------------|
| open_graph_template.html | Template HTML con OG tags y placeholders dinamicos |
| tests/asset_generation/test_open_graph_generation.py | Tests end-to-end de open_graph |
| tests/quality_gates/test_gate_presence.py | Tests de presence verification en gate |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| conditional_generator.py | Pre-check schema rico + rama open_graph |
| v4_asset_orchestrator.py | Bridge siempre aplica para hotel_schema |
| v4_diagnostic_generator.py | Labels financieros corregidos |
| diagnostico_v6_template.md | Variables alineadas |
| pain_solution_mapper.py | Cableado no_og_tags desde audit_report |
| Gate report generator | Presence verification con SitePresenceChecker |

### Tests
- N tests nuevos, 0 regresiones
```

**Criterios de aceptacion**:
- [ ] Entrada [4.36.0] existe en CHANGELOG.md
- [ ] Secciones Objetivo, Cambios, Archivos Nuevos, Modificados, Tests presentes
- [ ] No entradas duplicadas

### Tarea 4: GUIA_TECNICA.md

**Objetivo**: Agregar nota tecnica para 4.36.0.

| Campo | Contenido |
|-------|-----------|
| Modulos afectados | asset_generation, commercial_documents, pain_solution_mapper, quality_gates |
| Problema | 4 hallazgos: schema dual, label financiero, OG asset roto, gate_report falsos missing |
| Solucion | Bridge siempre aplica + labels semanticos + template OG + cableado pain_id + presence check |
| Backwards compatibility | Si (campos antiguos siguen existiendo, JSON backward compatible) |

**Criterios de aceptacion**:
- [ ] GUIA_TECNICA.md tiene seccion "Notas de Cambios v4.36.0"
- [ ] Incluye modulos, problema, solucion, backwards compatibility

### Tarea 5: Validacion final

```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe scripts/doctor.py --status
./venv/Scripts/python.exe scripts/doctor.py --context
```

**Criterios de aceptacion**:
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] `doctor.py --status` sin errores criticos
- [ ] `doctor.py --context` sin gaps

### Tarea 6: Log phase completion del RELEASE

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-RELEASE-4.36.0 \
    --desc "Release 4.36.0: PATCH Forense AmaziliaHotel" \
    --archivos-mod "VERSION.yaml,CHANGELOG.md,GUIA_TECNICA.md" \
    --check-manual-docs
```

**Criterios de aceptacion**:
- [ ] VERSION SYNC GATE pasa (no hay `(!)`)
- [ ] REGISTRY.md actualizado con RELEASE

---

## Criterios de Completitud (CHECKLIST)

- [ ] **Version bump**: 4.36.0 en VERSION.yaml
- [ ] **Sync**: sync_versions.py pasa, 6 archivos sincronizados
- [ ] **REGISTRY**: FASE-A, B, C, D, RELEASE registradas
- [ ] **CHANGELOG**: Entrada 4.36.0 con formato correcto
- [ ] **GUIA_TECNICA**: Notas de cambios v4.36.0
- [ ] **Validaciones**: run_all_validations.py --quick 4/4
- [ ] **Doctor**: status y context sin errores
- [ ] **dependencias-fases.md**: Las 5 fases marcadas como completadas

---

## Restricciones

- NO modificar codigo fuente (ya hecho en FASE-A, B, C, D)
- NO ejecutar v4complete
- NO modificar ROADMAP.md
- Solo documentacion y validaciones
- Maximo 60 iteraciones del agente en esta fase
