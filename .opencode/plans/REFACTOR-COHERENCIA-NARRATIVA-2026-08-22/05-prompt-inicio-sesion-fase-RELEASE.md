# FASE-RELEASE-4.72.1: Cierre y Documentación Oficial — "Coherencia Narrativa Dinámica"

**ID**: REFACTOR-COHERENCIA-NARRATIVA-2026-08-22 / FASE-RELEASE-4.72.1
**Objetivo**: Version bump 4.72.0 → 4.72.1 (patch), sincronización de versión en los 6 archivos, CHANGELOG y GUIA_TECNICA oficiales (desde los datos acumulados en `09-documentacion-post-proyecto.md`), regeneración de SYSTEM_STATUS/DOMAIN_PRIMER, validaciones finales y cierre del plan. **NO modifica código fuente.**
**Dependencias**: TODAS las fases de implementación ✅ (regla de dependencia del executor): FASE-R0-A, R0-B, R0-C, R0-D, R0-E, R0-F.
**Duración estimada**: 1 sesión (~30-45 min directo; ~4 min si se delega — histórico: 18 tool calls)
**Skill**: `phased_project_executor.md` §Paso-7 (pasos E1-E8b) — **fase DELEGABLE vía `delegate_task`**

---

## Modo de Ejecución — delegate_task (VIABLE aquí, decisión del plan maestro §6)

Según el TIP del executor (v2.12.0 GAP 2): FASE-RELEASE es delegable — solo edita YAML/MD y ejecuta scripts stdlib (`sync_versions.py`, `run_all_validations.py`, `doctor.py`), **sin imports del proyecto**. Confirmado históricamente: ~18 tool calls / ~4 min (BUGS-ONBOARDING-ADR 2026-07-22).

**Protocolo de delegación** (elección según presupuesto de iteraciones del agente principal):

```
SI el agente principal tiene presupuesto limitado de iteraciones:
  → delegate_task(
      goal="Ejecutar FASE-RELEASE-4.72.1 del plan REFACTOR-COHERENCIA-NARRATIVA-2026-08-22",
      context="""
        Seguir .agents/workflows/phased_project_executor.md §Paso-7 (E1-E8b).
        Version objetivo: 4.72.1 (patch). Codename: "Coherencia Narrativa Dinámica".
        Datos acumulados en
        .opencode/plans/REFACTOR-COHERENCIA-NARRATIVA-2026-08-22/09-documentacion-post-proyecto.md
        (fuente para CHANGELOG y GUIA_TECNICA).
        Tests esperados: 3,372 funciones (3,360 base + 12 nuevos de R0-A/R0-B/R0-C/R0-D).
        REGLAS:
        - NO modificar codigo fuente (solo VERSION.yaml, CHANGELOG.md, GUIA_TECNICA.md, README.md).
        - NO ejecutar v4complete (la unica corrida ya ocurrio en FASE-R0-E).
        - NO registrar fases anteriores (cada fase ya ejecuto log_phase_completion.py al cerrar).
        - Al final: log_phase_completion.py --fase FASE-RELEASE-4.72.1 (auto-detect activa
          el Version Sync Gate).
        Retornar: version final, resultados de run_all_validations.py --quick, veredicto
        del Version Sync Gate, checklist de cierre completado (si/no por item).
      """,
      timeout=600,
      notify_on_complete=True,
      toolsets=["file", "terminal"]
    )
  → Agente principal VERIFICA al retorno (no confiar ciegamente):
     1. VERSION.yaml == "4.72.1"
     2. ./venv/Scripts/python.exe scripts/run_all_validations.py --quick → TOTAL PASS
     3. ./venv/Scripts/python.exe scripts/version_consistency_checker.py → sin discrepancias

SI presupuesto suficiente → ejecución DIRECTA (pasos E1-E8b abajo).
```

> **FALLO DELEGATION NO DISPONIBLE**: si `delegate_task` no existe en el entorno, ejecutar directo — nunca bloquear.

**Regla anti-deuda (executor §2.5)**: FASE-RELEASE **NO registra las fases R0-A a R0-F** — cada una ya ejecutó `log_phase_completion.py` al terminar. RELEASE solo sincroniza y valida. Si T1 de esta fase fuera "registrar R0-A a R0-F" → ERROR de diseño.

---

## Contexto

Cierre oficial del plan REFACTOR-COHERENCIA-NARRATIVA-2026-08-22. El plan eliminó la **fosilización narrativa** (causa raíz única de 7 bugs B1-B7): textos hardcoded de WhatsApp en diagnóstico y propuesta que ignoraban `whatsapp_status=VERIFIED` y el pain_ledger. Es un **patch** (4.72.1): no cambia lógica core ni API pública, solo condicionales de narrativa en documentos comerciales — backwards compatible.

Los datos de todas las fases (funcionalidades, métricas, archivos) están acumulados en `09-documentacion-post-proyecto.md`. El análisis post-implementación (matriz B1-B7/AC1-AC12, lecciones, métricas E2E) está en `10-analisis-post-implementacion.md` — completado en FASE-R0-F.

### Estado de Fases Anteriores (gate de entrada — verificar ANTES de iniciar)

| Fase | Estado requerido |
|------|------------------|
| FASE-R0-A (B2 Quick Win) | ✅ |
| FASE-R0-B (B1+B4 Sección 4 dinámica) | ✅ |
| FASE-R0-C (B3+B5 títulos/contadores) | ✅ |
| FASE-R0-D (B6+B7 propuesta condicional) | ✅ |
| FASE-R0-E (E2E v4complete Zione) | ✅ (smoke 7/7) |
| FASE-R0-F (verificación AC1-AC12) | ✅ (12/12 PASA — o fallas documentadas con plan de recuperación cerrado) |

**Si alguna NO está ✅ en `06-checklist-implementacion.md` → ABORTAR** (Plan de Recuperación del executor: RELEASE sin implementaciones completadas → abortar).

### Resumen de cambios para documentación oficial

- **FASE-R0-A**: Quick Win Schema/WhatsApp condicionado a `whatsapp_conflict` (B2) — `v4_diagnostic_generator.py` + 1 test.
- **FASE-R0-B**: Sección 4 "Fugas" derivada del pain_ledger (B1) + título "LAS {N} FUGAS" dinámico (B4) — template + generator + 4 tests.
- **FASE-R0-C**: Título Sección 1 condicional (B3) + contador Sección 6 "Detecta las {N} fugas" (B5) — template + 3 tests.
- **FASE-R0-D**: Plan 30 días condicional a `whatsapp_conflict` (B6) + botón de WhatsApp fuera de servicios adicionales cuando no hay brecha (B7) — `v4_proposal_generator.py` + 4 tests.
- **FASE-R0-E**: E2E única corrida `v4complete` Zi One Luxury post-fix + evidencia (baseline anómalo preservado + output nuevo).
- **FASE-R0-F**: Certificación AC1-AC12 (12/12 PASA esperado) + análisis post-implementación completo.

---

## Tareas (E1-E8b del executor §Paso-7)

### E1: Diagnóstico inicial

```bash
./venv/Scripts/python.exe scripts/version_consistency_checker.py
./venv/Scripts/python.exe main.py --doctor
```

- [ ] version_consistency_checker pasa sin discrepancias
- [ ] doctor sin errores críticos

### E2: Version bump + sincronización

1. Actualizar `VERSION.yaml`:
   - `version: "4.72.1"`
   - `codename: "Coherencia Narrativa Dinámica"`
   - `release_date: "<fecha actual>"`
   - Agregar bloque de comentarios del release (patrón: ver bloque `# v4.72.0 - ...` L8-21):

```yaml
# v4.72.1 - REFACTOR-COHERENCIA-NARRATIVA (2026-08-XX)
# FASE-R0-A: Quick Win Schema condicionado a whatsapp_conflict (B2)
# FASE-R0-B: Seccion 4 fugas derivada del pain_ledger (B1) + titulo LAS {N} FUGAS dinamico (B4)
# FASE-R0-C: Titulo Seccion 1 condicional (B3) + contador Seccion 6 dinamico (B5)
# FASE-R0-D: Plan 30 dias condicional (B6) + boton WhatsApp fuera de servicios adicionales sin brecha (B7)
# FASE-R0-E: E2E v4complete Zi One Luxury post-fix — smoke 7/7
# FASE-R0-F: Certificacion AC1-AC12 (12/12 PASA)
# 12 tests nuevos (3,372 total); 0 regresiones
# Backwards compatible: narrativa condicional en documentos comerciales, no logica core
```

2. Ejecutar sincronización:

```bash
./venv/Scripts/python.exe scripts/sync_versions.py
```

- [ ] sync_versions ejecutado sin errores (sincroniza AGENTS.md, README.md, .cursorrules, CONTRIBUTING.md, GUIA_TECNICA.md, REGISTRY.md)

### E3: CHANGELOG.md (formato CONTRIBUTING §Formato-CHANGELOG)

Entrada nueva (este plan SÍ modifica código → entrada `[4.72.1]` propia, NO subsección):

```markdown
## [4.72.1] - Coherencia Narrativa Dinámica — YYYY-MM-DD

### Objetivo
{Eliminación de la fosilización narrativa: 7 bugs B1-B7 donde documentos comerciales
mostraban "fugas de WhatsApp" hardcoded pese a whatsapp_status=VERIFIED. La narrativa
ahora se deriva dinámicamente del pain_ledger.}

### Cambios Implementados
- `modules/commercial_documents/v4_diagnostic_generator.py` - Quick Win Schema/WhatsApp condicionado a whatsapp_conflict (B2); Sección 4 de fugas derivada del pain_ledger reutilizando narrativa dinámica de `_pain_to_brecha()` (B1); título "LAS {N} FUGAS PRINCIPALES" dinámico (B4)
- `modules/commercial_documents/templates/diagnostico_v6_template.md` - Título Sección 1 condicional (B3); placeholders dinámicos para contador de fugas (B4, B5)
- `modules/commercial_documents/v4_proposal_generator.py` - Plan 30 días condicional a whatsapp_conflict (B6); botón de WhatsApp fuera de servicios adicionales cuando no hay brecha ni conflicto (B7)

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| (ninguno — refactor de módulos existentes) | |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| {completar desde 09-documentacion-post-proyecto.md Sección E} | |

### Tests
- 12 tests nuevos: {desglosar por archivo desde 09-documentacion-post-proyecto.md}
- E2E: v4complete Zi One Luxury post-fix (FASE-R0-E), certificación AC1-AC12 (FASE-R0-F)
```

- [ ] Entrada `[4.72.1]` existe, sin duplicados, describe archivos de cada fase
- [ ] Usar los datos reales de `09-documentacion-post-proyecto.md` (Secciones A/B/D/E)

### E4: GUIA_TECNICA.md

Agregar sección "Notas de Cambios v4.72.1" con los 4 campos requeridos:

| Campo requerido | Contenido esperado |
|----------------|--------------------|
| Módulos afectados | `modules/commercial_documents/` (generator, template, proposal) |
| Problema | Fosilización narrativa: 7 textos hardcoded de WhatsApp que ignoraban pain_ledger y whatsapp_status |
| Solución | Condicionales de narrativa cableadas a whatsapp_conflict + Sección 4 derivada del pain_ledger |
| Backwards compatibility | Sí — no cambia API pública ni lógica core; firmas con defaults conservadores |

- [ ] Nota técnica presente con los 4 campos

### E5: Skills/Workflows

```bash
ls -la .agents/workflows/*.md
```

- [ ] Todos los `.md` en `.agents/workflows/` listados en `.agents/workflows/README.md` (sin skills huérfanos)
- [ ] Symlink `.agent/workflows` → `.agents/workflows` intacto

### E6: Regenerar SYSTEM_STATUS.md

```bash
./venv/Scripts/python.exe scripts/doctor.py --status
```

- [ ] SYSTEM_STATUS.md regenerado con versión 4.72.1

### E7: Regenerar DOMAIN_PRIMER.md

```bash
./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer
./venv/Scripts/python.exe scripts/doctor.py --context   # SOLO en FASE-RELEASE (cierre final)
```

- [ ] DOMAIN_PRIMER regenerado con módulos actuales; todo módulo en `modules/` documentado

### E8: Symlink + Validación final

```bash
ls -la .agent/workflows    # debe apuntar a .agents/workflows
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe scripts/validate_agents_md.py
git diff --stat
```

- [ ] Symlink intacto
- [ ] `run_all_validations.py --quick` **TOTAL PASS** (conteo dinámico del script, NO fijar "4/4")
- [ ] `validate_agents_md.py` pasa (gate count de AGENTS.md == código; el conteo de tests en "Estado Actual" se corrige en E8b)
- [ ] `git diff --stat` muestra todos los archivos del plan modificados

### E8b: README.md + AGENTS.md line-by-line audit (MANUAL)

> [!WARNING]
> Los conteos numéricos se desincronizan silenciosamente entre releases (lección DT-3: test count stale por 56 tests).

```bash
# Test count real
./venv/Scripts/python.exe -m pytest --collect-only -q 2>&1 | tail -1

# Module count real
find modules/ -name '*.py' ! -path '*__pycache__*' | wc -l
```

**Checklist README/AGENTS audit**:
- [ ] Test count en README.md (banner `v4.72.1`, `## Estado del Proyecto`, `## Calidad Garantizada`) coincide con `pytest --collect-only` — **esperado: 3,372** (3,360 + 12 del plan)
- [ ] Test count en AGENTS.md tabla "Estado Actual" ("3,360 funciones, 261 archivos") actualizado a 3,372 (y conteo de archivos de tests si cambió: 261 → verificar)
- [ ] Conteo por módulo en AGENTS.md: `commercial_documents` (251 → 251+12=263 si los tests van ahí; verificar)
- [ ] Module count en README.md coincide con `find modules/`
- [ ] Fecha de actualización en el banner = fecha actual
- [ ] Si hay discrepancia → corregir y commit separado post-release

---

## Registro de RELEASE (último paso)

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-RELEASE-4.72.1 \
    --desc "Release 4.72.1 - Coherencia Narrativa Dinamica: 7 fixes B1-B7 fosilizacion narrativa, 12 tests, E2E Zione certificado AC1-AC12" \
    --check-manual-docs
```

> El AUTO-DETECT del script detecta `FASE-RELEASE-4.72.1` y activa el **Version Sync Gate** automáticamente (valida CHANGELOG ↔ VERSION.yaml sincronizados). Si el gate FALLA: `python scripts/sync_versions.py` + re-ejecutar el registro.

```bash
./venv/Scripts/python.exe scripts/version_consistency_checker.py
```

- [ ] Version Sync Gate pasó (no hubo `(!)`)
- [ ] version_consistency_checker final sin discrepancias

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`**: marcar FASE-RELEASE-4.72.1 ✅ — plan COMPLETADO.
2. **`06-checklist-implementacion.md`**: fila FASE-RELEASE ✅.
3. **`README.md` del plan**: marcar plan COMPLETADO (fecha de cierre).
4. **`10-analisis-post-implementacion.md`**: llenar **Checklist de Cierre** (última sección) + Métricas de Ejecución finales.
5. **`git add -A && git commit`** con mensaje de release:
   ```
   release: v4.72.1 Coherencia Narrativa Dinámica (REFACTOR-COHERENCIA-NARRATIVA)

   - Fixes B1-B7: fosilización narrativa eliminada en documentos comerciales
   - Sección 4 fugas derivada del pain_ledger (no hardcoded)
   - 12 tests nuevos (3,372 total)
   - E2E Zi One Luxury certificado AC1-AC12
   ```

---

## Criterios de Completitud (CHECKLIST)

⚠️ Verificar ANTES de marcar como ✅ COMPLETADA ⚠️

- [ ] VERSION.yaml == "4.72.1" y sync_versions aplicado a los 6 archivos
- [ ] CHANGELOG `[4.72.1]` con formato CONTRIBUTING completo (Objetivo/Cambios/Nuevos/Modificados/Tests)
- [ ] GUIA_TECNICA con nota "Notas de Cambios v4.72.1" (4 campos)
- [ ] SYSTEM_STATUS y DOMAIN_PRIMER regenerados (`--context` ejecutado)
- [ ] `run_all_validations.py --quick` TOTAL PASS + `validate_agents_md.py` pasa
- [ ] README/AGENTS audit: test count 3,372 verificado contra `pytest --collect-only`
- [ ] Version Sync Gate OK (registro FASE-RELEASE-4.72.1 sin `(!)`)
- [ ] Checklist de Cierre en `10-analisis-post-implementacion.md` completado
- [ ] Commit de release ejecutado

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- Máximo 60 iteraciones (R2). Si se alcanza: `⏳ INCOMPLETA` + checkpoint + cerrar sesión.
- **NO modifica código fuente** (solo YAML/MD + scripts de sincronización).
- **NO edita ROADMAP.md** (executor §Paso-7 "Qué NO hace").
- **NO ejecuta `v4complete`** (la única corrida del plan ya ocurrió en FASE-R0-E).
- **NO registra fases anteriores** (regla anti-deuda §2.5 — cada fase ya se registró a sí misma).
- NO crea entrada de CHANGELOG duplicada; NO modifica bloques de releases anteriores en VERSION.yaml (solo agrega el bloque nuevo 4.72.1).
