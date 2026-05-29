# FASE-RELEASE: Documentación y Sincronización

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DIRECTA — **NO DELEGAR**. Los scripts de documentación
> (log_phase_completion, sync_versions) tienen particularidades de WSL que un
> subagent puede no manejar correctamente (quoting, paths).

## Contexto previo

- **FASE-0 a FASE-7** ✅: TODOS los gaps implementados + v4complete verificado + FASE-7 pendiente.
- Evidencia guardada en `evidence/FASE-PENDIENTE-V4COMPLETE/`.
- Post-análisis documentado con tabla de fixes PASSED/FAILED.
- Tests pasando.

## Objetivo de esta fase

Ejecutar el **cascade documental obligatorio** según `phased_project_executor.md` §4.5
y `AGENTS.md`. Este incluye registro de TODAS las fases en REGISTRY, bump de versión,
sincronización de archivos de documentación, y validación final.

---

### Tareas

- [ ] **T1: Registrar fases en REGISTRY.md**

  **IMPORTANTE — WSL quoting:** `cmd.exe /c` con rutas relativas falla.
  Usar ruta completa de Windows.

  ```bash
  cd /mnt/c/Users/Jhond/Github/iah-cli

  # Registrar el plan completo (una sola entrada)
  cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe scripts\log_phase_completion.py ^
      --fase REFACTOR-PENDIENTE-V4.58.0 ^
      --desc Refactorizacion_5_gaps_propuesta_comercial:_CAPEX_breakdown_ADR_Status_Quo_Closing_Pitch_gate_unification_dead_code_cleanup_Plus_FASE-7_ADR_audit_status.Verified_con_v4complete_Hotel_Castilla_Real_coherence0.85_11gates. ^
      --archivos-mod modules/commercial_documents/v4_proposal_generator.py,modules/commercial_documents/templates/propuesta_v6_template.md,modules/quality_gates/publication_gates.py,config/regional_benchmarks.yaml,modules/auditors/v4_comprehensive.py ^
      --tests 0 ^
      --check-manual-docs"
  ```

  **Nota:** `--desc` DEBE usar underscores (sin espacios) o argparse rechaza
  palabras extra como args no reconocidos.

  Verificar que NO haya `[GAP]` en el DOCUMENTATION AUDIT del output.

- [ ] **T2: Bump de versión + sync**

  **Edición manual de VERSION.yaml** (sync_versions.py NO acepta --bump):
  ```bash
  # Leer versión actual
  cat VERSION.yaml | head -10

  # Editar: incrementar MINOR (ej: 4.58.0 → 4.59.0)
  # Esto es un cambio MINOR porque añade features nuevas (5 gaps comercialmente visibles)
  ```

  Ejecutar sync:
  ```bash
  cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe scripts\sync_versions.py"
  cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe scripts\version_consistency_checker.py"
  ```

  **Nota sobre fechas:** `sync_versions.py` usa `datetime.now()` — ignora
  `release_date` en VERSION.yaml. `last_update` en AGENTS.md será hoy.

- [ ] **T3: CHANGELOG.md + GUIA_TECNICA.md**

  **CHANGELOG.md** — Añadir entrada MINOR:
  ```markdown
  ## [4.59.0] - YYYY-MM-DD

  ### Objetivo
  Resolver 5 gaps comerciales confirmados en la propuesta comercial v4,
  1 bug de gates y 1 deuda técnica. Verificado con v4complete en Hotel Castilla Real.

  ### Cambios Implementados
  - **IMP-03**: CAPEX breakdown ahora se renderiza en propuesta (template fix)
  - **F7**: Unificada lógica de evidence tier entre publication gates
  - **F5**: ADR en coherence checklist usa fuente real (benchmarks regionales)
  - **MIN-02**: ADR evidenciado en benchmarks + propuesta comercial
  - **MIN-01**: Nueva tabla Status Quo vs Implementación IAO
  - **MIN-03**: Closing pitch dinámico basado en ROICR, payback y recuperación
  - **Debt**: Eliminado template embebido muerto en v4_proposal_generator.py

  ### Archivos Modificados
  - `modules/commercial_documents/v4_proposal_generator.py`
  - `modules/commercial_documents/templates/propuesta_v6_template.md`
  - `modules/quality_gates/publication_gates.py`
  - `config/regional_benchmarks.yaml`

  ### Tests
  - Regresión completa: todos los tests existentes pasan
  - v4complete Hotel Castilla Real: [X]/11 gates, coherence [X.XX]
  ```

  **GUIA_TECNICA.md** — Añadir nota técnica:
  ```markdown
  ### Notas de Cambios v4.59.0

  **Modulos afectados:** `v4_proposal_generator`, `publication_gates`, `regional_benchmarks`

  **Problema:** 5 gaps comerciales donde datos se producían pero no se renderizaban
  (CAPEX), no existían (Status Quo, Closing Pitch), o se mostraban como placeholders
  vacíos (ADR). Además, 2 gates evaluaban evidence tier inconsistente.

  **Solucion:**
  - Template fix: añadir placeholder `${capex_breakdown_table}`
  - Pipeline fix: método `_build_status_quo_table()`, `_build_closing_pitch()`
  - Data fix: ADR en `regional_benchmarks.yaml` + cascada en coherence checklist
  - Gate fix: `financial_validity` usa `evidence_tier` formal
  - Debt: template embebido L575-605 eliminado

  **Backwards compatibility:** Si. Nuevos placeholders son opcionales — si no se
  producen, el template los ignora. Gates más precisos no cambian FAIL/PASS umbral.
  ```

- [ ] **T4: Validación final**

  ```bash
  cd /mnt/c/Users/Jhond/Github/iah-cli

  # Validaciones rápidas
  cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe scripts\run_all_validations.py --quick"

  # Doctor status
  cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe scripts\doctor.py --status"

  # Tests finales (opcional, si hay tiempo)
  ./venv/Scripts/python.exe -m pytest tests/ --timeout=60 -q 2>&1 | tail -10
  ```

  **Resultados esperados:**
  - `run_all_validations.py --quick`: 4/4 pasan (o pre-existing failures aceptables)
  - `doctor.py --status`: sin errores críticos
  - `version_consistency_checker.py`: sin discrepancias
  - Tests: mismo número de passed que al inicio (o más si se añadieron)

  Marcar T1-T4 como completadas en `06-checklist-implementacion.md`.

### Restricciones

- **NO ejecutar v4complete** — ya ejecutado en FASE-6
- **FASE-7 DEBE ejecutarse ANTES de RELEASE** — FASE-7 resuelve adr_status cosmetic
- **NO modificar código fuente** — solo documentación
- Máximo 60 iteraciones (R2)
- Si `run_all_validations.py --quick` falla, verificar si son pre-existing
  failures (no introducidos por este plan)
- `sync_versions.py` README.md WARN es esperado e inofensivo

### Criterios de completitud

- [ ] REFACTOR-PENDIENTE-V4.58.0 registrado en REGISTRY.md (sin GAPs)
- [ ] VERSION.yaml incrementado (MINOR bump)
- [ ] AGENTS.md, README.md, .cursorrules, CONTRIBUTING.md sincronizados
- [ ] CHANGELOG.md con entrada completa
- [ ] GUIA_TECNICA.md con nota técnica
- [ ] `run_all_validations.py --quick` ejecutado
- [ ] `doctor.py --status` ejecutado
- [ ] Estado actualizado en checklist
- [ ] **Todas las fases del plan marcadas como completadas**

### Archivos involucrados

| Archivo | Cambio |
|---------|--------|
| `docs/contributing/REGISTRY.md` | Entrada de fase |
| `VERSION.yaml` | Bump minor |
| `CHANGELOG.md` | Entrada nueva |
| `docs/GUIA_TECNICA.md` | Nota técnica |
| `AGENTS.md`, `README.md`, `.cursorrules`, `CONTRIBUTING.md` | Sync versión |

### Post-Ejecución

Este es el **FIN DEL PLAN**. Resumen de logros esperados:

```
REFACTOR-PENDIENTE-V4.58.0: COMPLETADO
├── 5 gaps comerciales resueltos
├── 2 bugs corregidos (F5 + F7)
├── 1 deuda técnica eliminada
├── 1 cosmetic fix (adr_status)
├── v4complete Hotel Castilla Real verificado (coherence 0.85, 11/11 gates)
└── Documentación sincronizada
```
