# FASE-RELEASE: Cierre y Documentación Oficial v4.60.1

**ID**: FASE-RELEASE-4.60.1
**Objetivo**: Cerrar el plan BUGFIX-LUXOR-2026-07-06 con version bump a v4.60.1, sincronización de documentación, y validaciones finales.
**Dependencias**: FASE-5 completada ✅ (que a su vez requiere FASE-1 a FASE-4)
**Duración estimada**: 1 hora
**Skill**: `phased-project-executor`

---

## Contexto

Plan: BUGFIX-LUXOR-2026-07-06 v4.60.1
Esta es la fase final del plan. NO modifica código fuente. Solo documentación y validaciones.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-1 | ✅ Completada (BUG-2 + BUG-1) |
| FASE-2 | ✅ Completada (BUG-4a openrouter) |
| FASE-3 | ✅ Completada (BUG-5 scrubber) |
| FASE-4 | ✅ Completada (BUG-6 SPA) |
| FASE-5 | ✅ Completada (Verificación E2E) |

### Versión
- Base: v4.60.0
- Objetivo: v4.60.1

---

## Tareas

### E1. Diagnóstico Inicial

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/version_consistency_checker.py
./venv/Scripts/python.exe main.py --doctor
```

- [ ] version_consistency_checker.py pasa sin discrepancias
- [ ] doctor no reporta errores críticos

### E2. Version Bump

Editar `VERSION.yaml` manualmente:
```yaml
version: "4.60.1"
release_name: "Bugfixes Luxor v4complete"
release_date: "2026-07-06"
```

Luego sincronizar:
```bash
./venv/Scripts/python.exe scripts/sync_versions.py
```

Sincroniza VERSION.yaml → 6 archivos: AGENTS.md, README.md, .cursorrules, CONTRIBUTING.md, GUIA_TECNICA.md, REGISTRY.md

- [ ] VERSION.yaml actualizado a 4.60.1
- [ ] sync_versions.py ejecutado sin errores

### E3. CHANGELOG.md (MANUAL)

Verificar que el CHANGELOG tenga la entrada para 4.60.1 con el formato requerido:

```markdown
## [4.60.1] - Bugfixes Luxor v4complete — 2026-07-06

### Objetivo
Corrección de 5 bugs detectados en ejecución v4complete de Luxorhotel, no relacionados con onboarding.

### Cambios Implementados
- **FASE-1 BUG-2**: Removido `calc_result` UnboundLocalError en FASE-K (main.py)
- **FASE-1 BUG-1**: `_audit_competitors` ahora usa `gbp_result.lat/lng` en lugar de 0.0 (v4_comprehensive.py)
- **FASE-2 BUG-4a**: Externalizado modelo de OpenRouter al `provider_registry.yaml` (llm_mention_checker.py)
- **FASE-3 BUG-5**: Eliminado FASE 3.6 del content scrubber (dead code, main.py)
- **FASE-4 BUG-6**: Integrado Playwright como fallback para renderizar SPAs (v4_comprehensive.py)

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| evidence/FASE-5/ | Evidencia de verificación E2E |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| main.py | BUG-2: removida línea `calc_result`; BUG-5: eliminado FASE 3.6 dead code |
| modules/auditors/v4_comprehensive.py | BUG-1: `gbp_result.lat/lng` + validación rango; BUG-6: Playwright SPA fallback |
| modules/auditors/llm_mention_checker.py | BUG-4a: modelo leído del registry (no hardcoded) |
| config/provider_registry.yaml | BUG-4a: `default_model` verificado/actualizado |
| modules/auditors/seo_elements_detector.py | BUG-6: posible modificación de `detect()` |

### Tests
- N tests nuevos (regresión BUG-1, BUG-2, BUG-4a mock, BUG-5 scrubber, BUG-6 SPA rendering)
- 0 regresiones
```

**Checklist CHANGELOG:**
- [ ] Entrada `[4.60.1]` existe
- [ ] Tiene sección `### Objetivo`
- [ ] Tiene sección `### Cambios Implementados`
- [ ] Tiene sección `### Archivos Nuevos` (si aplica)
- [ ] Tiene sección `### Archivos Modificados`
- [ ] Tiene sección `### Tests`
- [ ] No hay entradas duplicadas

### E4. GUIA_TECNICA.md (MANUAL)

Verificar nota técnica para cada fase:

**Checklist GUIA_TECNICA:**
- [ ] Cada fase tiene una sección "Notas de Cambios v4.60.1"
- [ ] Incluye módulos afectados
- [ ] Incluye problema/solución
- [ ] Incluye backwards compatibility
- [ ] Incluye tests (si aplica)

### E5. Skills/Workflows

```bash
ls -la .agents/workflows/*.md
```

- [ ] Todos los .md en .agents/workflows/ listados en .agents/workflows/README.md
- [ ] No hay skills huérfanos

### E6. Regenerar SYSTEM_STATUS.md

```bash
./venv/Scripts/python.exe scripts/doctor.py --status
```

- [ ] SYSTEM_STATUS.md regenerado con versión 4.60.1

### E7. Regenerar DOMAIN_PRIMER.md

```bash
./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer
./venv/Scripts/python.exe scripts/doctor.py --context
```

- [ ] DOMAIN_PRIMER.md regenerado con módulos actuales
- [ ] Todo módulo en `modules/` documentado

### E8. Symlink + Validación Final

```bash
ls -la .agent/workflows    # Debe mostrar → .agents/workflows
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
git diff --stat
```

- [ ] Symlink .agent/workflows → .agents/workflows intacto
- [ ] run_all_validations.py --quick pasa sin errores
- [ ] git diff --stat muestra todos los archivos modificados

---

## Post-Ejecución: log_phase_completion.py

**Comando (ejecutar al final del RELEASE):**
```bash
cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe scripts\log_phase_completion.py --fase FASE-RELEASE-4.60.1 --desc Release_4.60.1_bugfixes_luxor --check-manual-docs"
```

**Verificar VERSION SYNC GATE:**
```bash
./venv/Scripts/python.exe scripts/version_consistency_checker.py
```
- [ ] No hay `(!)` en output — gate pasó

---

## Criterios de Completitud (CHECKLIST)

- [ ] **E1**: Diagnóstico inicial pasa
- [ ] **E2**: VERSION.yaml bump a 4.60.1 + sync_versions.py ejecutado
- [ ] **E3**: CHANGELOG.md tiene entrada [4.60.1] con formato correcto
- [ ] **E4**: GUIA_TECNICA.md tiene notas técnicas para cada fase
- [ ] **E5**: Skills/workflows verificados
- [ ] **E6**: SYSTEM_STATUS.md regenerado
- [ ] **E7**: DOMAIN_PRIMER.md regenerado
- [ ] **E8**: Symlink intacto + run_all_validations.py --quick pasa
- [ ] **log_phase_completion.py**: Ejecutado exitosamente
- [ ] **VERSION SYNC GATE**: Pasó sin `(!)`

---

## Restricciones

- **NO modificar código fuente** (solo documentación y validaciones)
- **NO ejecutar v4complete** (ya se hizo en FASE-5)
- **NO modificar ROADMAP.md**
- **NO registrar fases anteriores** — cada fase ya se registró a sí misma (§2.5 anti-deuda)
- **Máximo 60 iteraciones** del agente

---

## Budget de Iteraciones Estimado

```
Fijos:
  - Leer plan + verificar estado: ~3 iters
  - E1-E2 (diagnóstico + version bump + sync): ~5 iters
  - E3-E4 (CHANGELOG + GUIA_TECNICA): ~5-8 iters
  - E5-E8 (skills, status, domain primer, validación): ~5-8 iters
  - log_phase_completion.py: ~3 iters
  Total estimado: 21-27 iters (bien dentro del límite de 60)
```

**Modo de ejecución:** Agente principal DIRECTO (documentación y validaciones)

---

## Recuperación en Caso de Agotamiento

Si el agente alcanza 60 iteraciones:
1. Guardar estado actual de las validaciones
2. Marcar fase como `⏳ INCOMPLETA` en `dependencias-fases.md`
3. Documentar checkpoint: qué pasos E1-E8 se completaron
4. Retomar en nueva sesión desde el checkpoint

---

## Checklist Final

- [ ] VERSION.yaml en 4.60.1
- [ ] sync_versions.py ejecutado (6 archivos sincronizados)
- [ ] CHANGELOG.md con entrada [4.60.1] completa
- [ ] GUIA_TECNICA.md con notas técnicas por fase
- [ ] SYSTEM_STATUS.md regenerado
- [ ] DOMAIN_PRIMER.md regenerado
- [ ] run_all_validations.py --quick pasa
- [ ] version_consistency_checker.py pasa
- [ ] log_phase_completion.py ejecutado
- [ ] VERSION SYNC GATE pasó
