# 05-prompt-inicio-sesion-fase-COPY-RELEASE

**Fase**: COPY-RELEASE — Documentación y Cierre
**Plan**: COPYWRITING-REFACTOR (Copywriting.jsonl → Refactorización Comercial)
**Sesión**: Nueva (fresh)
**Iteraciones máx**: 60
**Depende de**: COPY-C ✅ (E2E validado)
**Bloquea a**: Ninguna (fase final)

## Objetivo

Cerrar el proyecto COPYWRITING-REFACTOR con documentación oficial, version bump, validaciones finales y commit. NO se modifica código fuente.

## Contexto de Fases Anteriores

- COPY-A ✅: Templates reestructurados + generator fixes
- COPY-B ✅: Commercial gates integrados
- COPY-C ✅: E2E v4complete validado contra Copywriting.jsonl

## Tareas

### T1: Diagnóstico inicial + Sync Versions

**Paso 1a**: Verificar estado actual
```bash
./venv/Scripts/python.exe main.py --doctor
```

**Paso 1b**: Determinar nueva versión. Este es un cambio de copywriting (no funcional) que mejora la presentación comercial pero no altera lógica core. Sugerencia: **v4.51.1** (patch sobre v4.51.0).

**Paso 1c**: Actualizar VERSION.yaml:
```yaml
version: 4.51.1
release_date: [FECHA_ACTUAL]
description: "COPYWRITING-REFACTOR — Templates comerciales reestructurados para conversión hotelera colombiana"
```

**Paso 1d**: Sync versions:
```bash
./venv/Scripts/python.exe scripts/sync_versions.py
```

### T2: CHANGELOG.md + GUIA_TECNICA.md

**Paso 2a**: Actualizar CHANGELOG.md con formato CONTRIBUTING.md:

```markdown
### v4.51.1 — COPYWRITING-REFACTOR (2026-05-25)

#### Objetivo
Refactorizar templates y generadores de documentos comerciales para maximizar conversión en hoteles boutique colombianos. Basado en 12 hallazgos validados de Copywriting.jsonl.

#### Cambios
- **Templates V6 reestructurados**: Vista Gerencia (dueño) primero, Anexo Técnico después
- **Narrativa OTA**: Booking/Expedia/comisiones incorporados como dolor central
- **WhatsApp como gancho #1**: Conflicto WhatsApp lidera el diagnóstico
- **Scenario clamp**: Escenario optimista nunca negativo (validación + label condicional)
- **Tier consistency**: Fuente única de evidence_tier desde FinancialBreakdown
- **Commercial gates**: Nuevo módulo `modules/quality_gates/commercial_gate.py` con 8 gates (5 BLOCKING + 3 WARNING)
- **IA Bloqueada → IA sin guía**: Corrección determinística cuando blocked_crawlers vacío

#### Archivos Nuevos
- `modules/quality_gates/commercial_gate.py` — Commercial Gate Validator

#### Archivos Modificados
- `modules/commercial_documents/templates/diagnostico_v6_template.md` — Reordenado: dueño primero
- `modules/commercial_documents/templates/propuesta_v6_template.md` — OTA narrative, quick wins accionables
- `modules/commercial_documents/v4_diagnostic_generator.py` — Scenario clamp, tier consistency, breach sanitization
- `modules/commercial_documents/v4_proposal_generator.py` — Commercial gate integration

#### Tests
- `tests/quality/test_commercial_gate.py` — 3+ tests unitarios para gates
```

**Paso 2b**: Actualizar GUIA_TECNICA.md con nota técnica:

```markdown
### COPY-A — Template Restructuring (v4.51.1)
**Fecha**: 2026-05-25
**Descripción**: Templates V6 reestructurados con vista gerencia (dueño) en secciones 1-6 y anexo técnico en 7+. Scenario clamp en `_build_scenario_table_rows`. Tier consistency en `_build_financial_placeholders`.
**Archivos**: diagnostico_v6_template.md, propuesta_v6_template.md, v4_diagnostic_generator.py

### COPY-B — Commercial Gates (v4.51.1)
**Fecha**: 2026-05-25
**Descripción**: Nuevo módulo `modules/quality_gates/commercial_gate.py` con 8 gates (5 BLOCKING, 3 WARNING). Integrado en ambos generators. Corrección "IA Bloqueada" → "IA sin guía".
**Archivos**: modules/quality_gates/commercial_gate.py, v4_diagnostic_generator.py, v4_proposal_generator.py

### COPY-C — E2E Validation (v4.51.1)
**Fecha**: 2026-05-25
**Descripción**: v4complete Hotel Castilla Real validado contra Copywriting.jsonl. Coherence ≥ 0.80, 7/7 gates bloqueantes, 3/3 advisory.
**Archivos**: evidence/COPY-C/validation_report.md
```

### T3: Skills/Workflows + SYSTEM_STATUS.md

**Paso 3a**: Verificar que no hay skills/workflows huérfanos:
```bash
./venv/Scripts/python.exe scripts/validate_agent_ecosystem.py
```

**Paso 3b**: Regenerar SYSTEM_STATUS.md:
```bash
./venv/Scripts/python.exe scripts/doctor.py --status
```

### T4: DOMAIN_PRIMER + Validación Final + Commit

**Paso 4a**: Regenerar DOMAIN_PRIMER:
```bash
./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer
```

**Paso 4b**: Validación final:
```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```
Debe pasar 4/4.

**Paso 4c**: Validación de integración documental:
```bash
./venv/Scripts/python.exe scripts/validate_document_integration.py
```

**Paso 4d**: Commit:
```bash
git add .
git commit -m "release: v4.51.1 — COPYWRITING-REFACTOR

Templates comerciales reestructurados para conversión hotelera colombiana.

- Templates V6: Vista Gerencia primero, Anexo Técnico después
- OTA narrative (Booking/Expedia/comisiones)
- WhatsApp como gancho #1
- Scenario clamp (optimista nunca negativo)
- Tier consistency (fuente única)
- Commercial gates (8 gates: 5 BLOCKING + 3 WARNING)
- IA Bloqueada → IA sin guía

Refs: .opencode/plans/COPYWRITING-REFACTOR/"
```

## Criterios de Completitud

- [ ] VERSION.yaml actualizado a v4.51.1
- [ ] sync_versions.py ejecutado (6 archivos sincronizados)
- [ ] CHANGELOG.md actualizado con formato CONTRIBUTING.md
- [ ] GUIA_TECNICA.md con notas técnicas de las 3 fases
- [ ] validate_agent_ecosystem.py pasa
- [ ] SYSTEM_STATUS.md regenerado
- [ ] DOMAIN_PRIMER regenerado
- [ ] run_all_validations.py --quick pasa 4/4
- [ ] validate_document_integration.py pasa
- [ ] Commit realizado
- [ ] log_phase_completion.py ejecutado

## Restricciones

- **NO modificar código fuente** en esta fase
- **NO ejecutar v4complete** en esta fase
- Máximo 60 iteraciones

## Post-Ejecución (OBLIGATORIO)

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-COPY-RELEASE --desc "COPYWRITING-REFACTOR release v4.51.1: docs cascade, version bump, final validation" --check-manual-docs
```

Luego actualizar `09-documentacion-post-proyecto.md` marcando FASE-COPY-RELEASE como [x].
