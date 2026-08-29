# FASE-RELEASE-4.71.0 — Cierre Oficial, Version Bump y Documentación

**ID**: RC1-RC2-ENTREGA-COHERENTE-2026-08-04 / FASE-RELEASE-4.71.0
**Objetivo**: Release 4.71.0 — version bump, CHANGELOG, GUIA_TECNICA, sync y validaciones finales. NO modifica código fuente.
**Dependencias**: FASE-A ✅ FASE-B ✅ FASE-C ✅ FASE-D ✅ FASE-E ✅ FASE-F ✅ (verificar en dependencias-fases.md; si alguna no ✅, ABORTAR)
**Duración estimada**: 1-1.5 horas
**Skill**: `.agents/workflows/phased_project_executor.md` §Paso-7 (E1-E8b)
**Modo de ejecución**: ✅ **DELEGABLE vía `delegate_task`** (solo edita YAML/MD y ejecuta scripts, sin imports del proyecto — confirmado en BUGS-ONBOARDING-ADR: 18 tool calls, ~4 min).

---

## Delegación (delegate_task)

```
delegate_task(
  goal="FASE-RELEASE-4.71.0 del plan RC1-RC2-ENTREGA-COHERENTE-2026-08-04: pasos E1-E8b
        del phased_project_executor.md §Paso-7. Detalle completo en
        /.opencode/plans/Archives/RC1-RC2-ENTREGA-COHERENTE-2026-08-04/05-prompt-inicio-sesion-fase-RELEASE.md",
  context="Version objetivo 4.71.0 (VERSION.yaml es la fuente unica). Datos acumulados en
           09-documentacion-post-proyecto.md del plan. Python del venv para scripts.",
  timeout=900, notify_on_complete=True
)
```

El agente principal verifica el resultado (git diff + validaciones) antes del commit final.

---

## Tareas (E1-E8b del executor)

### E1. Diagnóstico inicial
```bash
python scripts/version_consistency_checker.py
python main.py --doctor
```

### E2. Version bump + sincronización
1. Editar `VERSION.yaml`: 4.70.0 → **4.71.0** (fuente única de verdad).
2. `python scripts/sync_versions.py` (sincroniza → AGENTS.md, README.md, .cursorrules,
   CONTRIBUTING.md, GUIA_TECNICA.md, REGISTRY.md).
3. `python scripts/version_consistency_checker.py` (debe pasar).

### E3. CHANGELOG.md (MANUAL, formato CONTRIBUTING)
Entrada `## [4.71.0] - Coherencia Propuesta-Diagnostico, Gates Comerciales y Entrega — YYYY-MM-DD` con:
- **Objetivo**: fixes RC1 (tabla de servicios dinámica), RC2 (gates + política ZIP), RC3 (higiene documental), S5/S7.
- **Cambios Implementados**: por fase (A-F), referenciando hallazgos N10-N21.
- **Archivos Nuevos / Modificados**: desde `git diff --stat` acumulado (L8 — fuente viva).
- **Tests**: +N tests nuevos (desde `git diff tests/` de las fases B/C/D), 0 regresiones.

### E4. GUIA_TECNICA.md (MANUAL)
Sección "Notas de Cambios v4.71.0": módulos afectados, problema/solución por RC,
backwards compatibility (la firma de `validate_diagnostic` recibe nuevos parámetros —
verificar compatibilidad), tests.

### E5. Skills/Workflows
Todos los `.agents/workflows/*.md` listados en `.agents/workflows/README.md` (sin huérfanos).

### E6. SYSTEM_STATUS.md
```bash
python scripts/doctor.py --status
```

### E7. DOMAIN_PRIMER
```bash
python scripts/doctor.py --regenerate-domain-primer
python scripts/doctor.py --context   # solo en RELEASE
```

### E8. Symlink + validaciones finales + gate AGENTS.md
```bash
python scripts/validate_agents_md.py          # Paso 5.5 CONTRIBUTING — SI FAIL, corregir ANTES de seguir
python scripts/validate_document_integration.py
python scripts/run_all_validations.py --quick # TOTAL PASS (conteo dinámico; incluye "Prompts No Release")
git diff --stat
```

### E8b. README.md line-by-line audit
Conteos en vivo (L8): `pytest --collect-only -q` y conteo de módulos; corregir README si
hay drift (test count incluye la cuarentena de FASE-A — registrar el conteo real post-cuarentena).

### Cierre
```bash
python scripts/log_phase_completion.py --fase FASE-RELEASE-4.71.0 --desc "Release 4.71.0: coherencia propuesta-diagnostico + gates comerciales + politica de entrega" --archivos-mod "VERSION.yaml,CHANGELOG.md,docs/GUIA_TECNICA.md" --check-manual-docs --release 4.71.0
```
**AQUÍ SÍ va `--release`** (es la fase RELEASE; el Version Sync Gate exige la entrada
`[4.71.0]` en CHANGELOG creada en E3).

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. `10-analisis-post-implementacion.md`: marcar el **Checklist de Cierre** (todos los checks en ✅) y cerrar la sección de Métricas con el conteo final de tests collected.
2. Commit final (git add + commit con mensaje "release: 4.71.0 ...").

---

## Criterios de Completitud (CHECKLIST)

- [ ] VERSION.yaml = 4.71.0 y 6 archivos sincronizados
- [ ] CHANGELOG `[4.71.0]` con las 5 secciones del formato CONTRIBUTING
- [ ] GUIA_TECNICA con nota v4.71.0
- [ ] `validate_agents_md.py` PASS + `validate_document_integration.py` PASS
- [ ] `run_all_validations.py --quick` TOTAL PASS (incluye "Prompts No Release")
- [ ] README audit con conteos en vivo
- [ ] `10-analisis-post-implementacion.md` completo (Checklist de Cierre con todos los checks marcados)
- [ ] `log_phase_completion.py --release 4.71.0` ejecutado con VERSION SYNC GATE en verde
- [ ] Commit final

## Restricciones

- NO modifica código fuente. NO ejecuta `v4complete`. NO edita ROADMAP.md.
- Las fases A-F DEBEN haberse registrado a sí mismas (anti-deuda §2.5): si el REGISTRY
  no tiene entradas de A-F, la deuda es de las fases, NO de RELEASE — abortar y exigir.
