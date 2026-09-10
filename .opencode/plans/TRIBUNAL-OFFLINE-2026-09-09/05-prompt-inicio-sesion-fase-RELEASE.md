# FASE-RELEASE-4.76.0: Cierre y Documentación Oficial

**ID**: TRIBUNAL-OFFLINE-2026-09-09 / FASE-RELEASE-4.76.0
**Objetivo**: Version bump a 4.76.0, sincronización documental (CHANGELOG, GUIA_TECNICA, README, AGENTS.md), validaciones finales, y archivado del plan (R2.5).
**Dependencias**: FASE-VERIFY ✅ (todas las fases previas completas)
**Complejidad técnica**: **BAJA** — solo documentación y validaciones, sin código fuente
**Modo de ejecución**: **DELEGABLE** a subagente (per executor §7 TIP: solo edita YAML/MD + scripts, sin imports del proyecto).
**Skill**: `phased_project_executor.md` v2.20.0 §Paso-7

---

## Contexto

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-T1 | ✅ |
| FASE-T2-A | ✅ |
| FASE-T2-B | ✅ |
| FASE-T4-A | ✅ |
| FASE-T4-B | ✅ |
| FASE-E2E | ✅ |
| FASE-VERIFY | ✅ |
| FASE-RELEASE-4.76.0 | ← ESTA FASE |

### Datos acumulados (desde `09-documentacion-post-proyecto.md`)

- **Módulos nuevos**: `modules/quality_gates/tribunal/` (8 archivos: `__init__`, `judge`, `acta_writer`, `diagnosis_reviewer`, `asset_reviewer`, `llm_extractor`, `alignment_reviewer`, `honesty_reviewer`)
- **Tests nuevos**: ~36 (7-8 por fase × 5 fases de implementación)
- **Versión**: 4.75.0 → 4.76.0
- **Feature**: Tribunal certificador del contrato P6+P7 (tramo offline)

---

## Tareas

### Tarea 1: E1-E2 — Diagnóstico + Sincronización

```bash
# E1: Diagnóstico inicial
./venv/Scripts/python.exe scripts/version_consistency_checker.py
./venv/Scripts/python.exe main.py --doctor

# E2: Bump VERSION.yaml a 4.76.0 y sincronizar
# Editar VERSION.yaml: version: 4.76.0
./venv/Scripts/python.exe scripts/sync_versions.py
./venv/Scripts/python.exe scripts/version_consistency_checker.py
```

- [ ] VERSION.yaml = 4.76.0
- [ ] `sync_versions.py` sincroniza 6 archivos (AGENTS, README, .cursorrules, CONTRIBUTING, GUIA_TECNICA, REGISTRY)
- [ ] `version_consistency_checker.py` pasa sin discrepancias

### Tarea 2: E3-E4 — CHANGELOG + GUIA_TECNICA

**CHANGELOG.md** (formato `docs/CONTRIBUTING.md §Formato-CHANGELOG`):

```markdown
## [4.76.0] - Tribunal certificador del contrato P6+P7 (tramo offline) — 2026-09-XX

### Objetivo
Implementar el tribunal de revisión como módulos deterministas en `modules/quality_gates/tribunal/`, integrados en el pipeline v4complete junto a `delivery_quality_report`. El tribunal certifica las 6 cláusulas P6 y produce un acta de revisión dual (JSON + MD) como evidencia legible de auditoría.

### Cambios Implementados
- `modules/quality_gates/tribunal/judge.py` - Juez certificador determinista (veredicto + regla de primer piso)
- `modules/quality_gates/tribunal/acta_writer.py` - Writer de acta dual (JSON machine-readable + MD human-readable)
- `modules/quality_gates/tribunal/diagnosis_reviewer.py` - Bot 1: revisor de diagnóstico interno (P6.1)
- `modules/quality_gates/tribunal/asset_reviewer.py` - Bot 3: revisor de completitud de assets (P6.3, P6.4)
- `modules/quality_gates/tribunal/llm_extractor.py` - Interfaz de extracción LLM (protocolo + mock)
- `modules/quality_gates/tribunal/alignment_reviewer.py` - Bot 2: revisor de alineación NL (P6.2)
- `modules/quality_gates/tribunal/honesty_reviewer.py` - Bot 4: revisor de honestidad comercial (P6.5)
- `main.py` - Integración del Juez junto a delivery_quality_report

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `modules/quality_gates/tribunal/__init__.py` | Paquete del tribunal |
| `modules/quality_gates/tribunal/judge.py` | Juez certificador P6+P7 |
| `modules/quality_gates/tribunal/acta_writer.py` | Acta dual JSON+MD |
| `modules/quality_gates/tribunal/diagnosis_reviewer.py` | Bot 1 |
| `modules/quality_gates/tribunal/asset_reviewer.py` | Bot 3 |
| `modules/quality_gates/tribunal/llm_extractor.py` | Extracción LLM |
| `modules/quality_gates/tribunal/alignment_reviewer.py` | Bot 2 |
| `modules/quality_gates/tribunal/honesty_reviewer.py` | Bot 4 |
| `tests/quality_gates/tribunal/` | Suite de tests del tribunal (~35 tests) |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `main.py` | Llamada al TribunalJudge tras delivery_quality_report |
| `AGENTS.md` | Nuevo módulo tribunal/ en tabla de Módulos Activos |

### Tests
- ~35 tests nuevos en `tests/quality_gates/tribunal/`, 0 regresiones
```

**GUIA_TECNICA.md** — sección "Notas de Cambios v4.76.0":
- Módulos afectados: `modules/quality_gates/tribunal/`, `main.py`
- Problema: nadie certificaba las 6 cláusulas P6 como un todo ni producía evidencia legible
- Solución: tribunal de 5 módulos deterministas + acta dual integrada en el pipeline
- Backwards compatibility: aditivo (no cambia API existente; el acta es un artefacto nuevo en `v4_audit/`)

### Tarea 3: E5-E8 — Validaciones finales

```bash
# E5: Skills/workflows
ls -la .agents/workflows/*.md

# E6: SYSTEM_STATUS
./venv/Scripts/python.exe scripts/doctor.py --status

# E7: DOMAIN_PRIMER
./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer
./venv/Scripts/python.exe scripts/doctor.py --context

# E8: Symlink + validación final
ls -la .agent/workflows
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
git diff --stat

# E8b: README audit
./venv/Scripts/python.exe -m pytest --collect-only -q 2>&1 | tail -1
find modules/ -name '*.py' ! -path '*__pycache__*' | wc -l
```

- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] `doctor.py --status` sin errores
- [ ] DOMAIN_PRIMER regenerado
- [ ] Symlink intacto
- [ ] README.md: test count + module count + fecha actualizados

### Tarea 4: R2.5 — Archivado del plan + log

```bash
# Registrar RELEASE
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-RELEASE-4.76.0 \
    --desc "Release 4.76.0: Tribunal certificador P6+P7 (tramo offline)" \
    --archivos-mod "main.py,AGENTS.md,VERSION.yaml,CHANGELOG.md,docs/GUIA_TECNICA.md,README.md" \
    --check-manual-docs

# R2.5: Archivar el plan (mismo commit)
git mv .opencode/plans/TRIBUNAL-OFFLINE-2026-09-09 .opencode/plans/Archives/
./venv/Scripts/python.exe scripts/validate_opencode_refs.py --fix
./venv/Scripts/python.exe scripts/validate_plan_citations.py --update-baseline
./venv/Scripts/python.exe scripts/run_all_validations.py --quick

# Commit único: RELEASE + archivado
# adds EXPLÍCITOS — NO usar `git add -A` (regla: commits separados para archivos ya sucios;
# el árbol debe estar limpio al entrar a RELEASE)
git add VERSION.yaml CHANGELOG.md AGENTS.md README.md .cursorrules \
    docs/CONTRIBUTING.md docs/GUIA_TECNICA.md docs/contributing/REGISTRY.md \
    .agent/SYSTEM_STATUS.md .agent/knowledge/DOMAIN_PRIMER.md \
    .opencode/plans/
git commit -m "chore(RELEASE): v4.76.0 — Tribunal certificador P6+P7 (tramo offline) + archivado del plan"
```

- [ ] Plan movido a `Archives/TRIBUNAL-OFFLINE-2026-09-09/`
- [ ] `validate_opencode_refs.py --fix` ejecutado (promoción "archived")
- [ ] `validate_plan_citations.py --update-baseline` ejecutado
- [ ] `run_all_validations.py --quick` verde POST-archivado
- [ ] Commit único cierra RELEASE + archivado

---

## Post-Ejecución (OBLIGATORIO)

1. **`06-checklist-implementacion.md`**: marcar FASE-RELEASE ✅ + Cierre del plan ✅
2. **`10-analisis-post-implementacion.md`**: Checklist de Cierre completo + métricas finales
3. **Write-back de lecciones**: lecciones INCLUIR → memoria del proyecto. QMind `iah-cli-lecciones` está FUERA del scope del agente (`permission_denied` verificado; notebook id `01a04d98-...`) → este paso lo ejecuta el agente principal o el usuario con el patrón ya probado: escribir `QMIND-WRITE-BACK.md` en `.opencode/context/` e ingesta manual desde la UI de QMind (el subagente delegado NO puede hacerlo — no tiene ese toolset ni acceso al notebook)
4. **CONTEXT**: ¿el CONTEXT-BOTS tiene un aporte durable nuevo tras la ejecución? Si sí → etiquetar + write-back

---

## Criterios de Completitud (CHECKLIST)

- [ ] VERSION.yaml = 4.76.0
- [ ] 6 archivos sincronizados por `sync_versions.py`
- [ ] CHANGELOG.md entrada [4.76.0] con formato CONTRIBUTING (Objetivo / Cambios / Archivos Nuevos / Modificados / Tests)
- [ ] GUIA_TECNICA.md nota técnica v4.76.0
- [ ] AGENTS.md: módulo `tribunal/` en tabla de Módulos Activos
- [ ] README.md: test count + module count + fecha correctos (E8b)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] `doctor.py --status` sin errores
- [ ] DOMAIN_PRIMER regenerado
- [ ] Symlink `.agent/workflows` intacto
- [ ] Plan en `Archives/` (R2.5)
- [ ] Commit único RELEASE + archivado
- [ ] `10-analisis-post-implementacion.md` Checklist de Cierre completo
- [ ] Write-back de lecciones ejecutado

---

## Restricciones

- **Presupuesto**: 25 iteraciones, corte en commit de código (R2.1)
- **NO modifica código fuente** (solo documentación y validaciones)
- **NO ejecuta v4complete**
- **NO modificar ROADMAP.md**
- **DELEGABLE**: si el agente principal tiene presupuesto limitado, delegar con:
  ```
  delegate_task(
      goal="Ejecutar FASE-RELEASE-4.76.0: version bump + docs + validaciones + archivado",
      context="Plan: .opencode/plans/TRIBUNAL-OFFLINE-2026-09-09/. Versión: 4.75.0 → 4.76.0. Feature: Tribunal certificador P6+P7. Datos acumulados en 09-documentacion-post-proyecto.md. R2.5: archivar plan en Archives/ con git mv + refs --fix + citas --update-baseline + --quick verde. Commit único.",
      timeout=600,
      notify_on_complete=True,
      toolsets=["terminal", "file"]
  )
  ```
