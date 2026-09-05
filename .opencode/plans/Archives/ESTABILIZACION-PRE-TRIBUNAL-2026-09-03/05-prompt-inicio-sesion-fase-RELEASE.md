# FASE-RELEASE-4.75.0 — Cierre documental del plan

**ID**: ESTABILIZACION-PRE-TRIBUNAL-2026-09-03 / FASE-RELEASE-4.75.0
**Objetivo**: Bump de versión `4.74.1 → 4.75.0`, CHANGELOG en formato CONTRIBUTING, GUIA_TECNICA con nota
por fase, sync de las 6 cabeceras, regeneración de DOMAIN_PRIMER y validaciones finales — todo desde los
datos ya volcados en `09-documentacion-post-proyecto.md` y `10-analisis-post-implementacion.md`.
**Dependencias**: FASE-VERIFY ✅
**Duración estimada**: 1-1.5 horas
**Complejidad técnica**: **BAJA** — solo YAML/MD + scripts; **sin imports del proyecto**, **sin** lógica de
producción.
**Modo de ejecución**: **DELEGABLE** (subagente). Es la única fase del plan delegable por completo: no
toca código Python, no requiere el venv de Windows/WSL, y su entrada está totalmente especificada en `09`.
**Skill**: `phased_project_executor.md` v2.18.0 §FASE-RELEASE + AGENTS.md §Flujo Documental Obligatorio
**Presupuesto**: ≤25 iteraciones (R2 tope: 60) · **Comandos largos: 0**

---

## Contexto

RELEASE es el **cierre burocrático** del plan: convierte el trabajo certificado por VERIFY en documentación
oficial del repositorio y en una versión publicada. **No agrega funcionalidad ni corrige código.**

### Versión objetivo: 4.75.0

| Campo | Valor |
|-------|-------|
| Versión actual del repo | `4.74.1` (codename «Blocklist-v2») |
| Versión objetivo | **`4.75.0`** (MINOR: funcionalidad nueva — punto 8, fuente única, severidad 11+2 — sin breaking change de API pública) |
| Fuente única | `VERSION.yaml` en la raíz. **Nunca** hardcodear versiones en código (AGENTS.md). |
| Codename sugerido | «Estabilización pre-tribunal» (a confirmar con el usuario) |

### Por qué es delegable

El executor permite delegar FASE-RELEASE porque su trabajo es **transformación documental determinista**:
leer `09`/`10`, ejecutar scripts de sync, redactar CHANGELOG/GUIA_TECNICA en formato fijo. No hay decisión
arquitectónica ni cross-módulo (esa fue VERIFY, que es DIRECTA). El subagente **no** necesita importar
`bs4`/`selenium` ni el venv — solo correr scripts de validación con `./venv/Scripts/python.exe`.

---

## Tareas

### R1 — Version bump

**Objetivo**: actualizar `VERSION.yaml` a `4.75.0` con codename y `release_date`.

**Archivos afectados**:
- `VERSION.yaml` (fuente única)

**Detalle**:
- `version: 4.74.1` → `version: 4.75.0`
- `codename:` → «Estabilización pre-tribunal» (o el que confirme el usuario)
- `release_date:` → fecha de ejecución (2026-09-XX)
- Actualizar el bloque de `changes`/`highlights` si el schema de VERSION.yaml lo prevé.

**Criterios de aceptación**:
- [ ] `VERSION.yaml` marca `4.75.0` con codename y fecha.
- [ ] No queda ningún `4.74.1` hardcodeado en código Python (grep de confirmación).

---

### R2 — CHANGELOG en formato CONTRIBUTING

**Objetivo**: redactar la entrada `4.75.0` de `CHANGELOG.md` **desde los datos de
`09-documentacion-post-proyecto.md`**, con el formato exacto que exige CONTRIBUTING.

**Archivos afectados**:
- `CHANGELOG.md`

**Formato obligatorio** (AGENTS.md §Flujo Documental + `docs/contributing/documentation_rules.md`):
```markdown
## [4.75.0] - 2026-09-XX — Estabilización pre-tribunal

### Objetivo
{1-2 frases: curar la causa raíz §12.5 — contrato de detección fragmentado y sin candado}

### Cambios
- {por fase: A fuente única, B biyección, C punto 8, D severidad 11+2, E snapshot+asset_path,
   F oráculo único+skipped≠passed+is_coherent, G ceguera de gates, H quirúrgicos}

### Archivos Nuevos
- {registro canónico, contract tests, site_presence_snapshot writer, …}

### Archivos Modificados
- {pain_solution_mapper, publication_gates, proposal_asset_alignment, alignment_result,
   coherence_validator, delivery_quality_report, v4_proposal_generator, v4_diagnostic_generator, …}

### Tests
- {conteo final: baseline 848 → nuevo total; contract tests agregados}
```

**Criterios de aceptación**:
- [ ] Las 5 subsecciones (`### Objetivo / ### Cambios / ### Archivos Nuevos / ### Archivos Modificados /
      ### Tests`) están presentes y pobladas desde `09`.
- [ ] Los «Archivos Nuevos/Modificados» coinciden con la Sección E de `09`.
- [ ] El conteo de Tests coincide con la Sección D de `09` y con NR1 certificado en VERIFY.

---

### R3 — Scripts de sync + GUIA_TECNICA + DOMAIN_PRIMER

**Objetivo**: ejecutar el flujo documental oficial en orden (AGENTS.md §Flujo Documental Obligatorio).

**Archivos afectados**:
- `REGISTRY.md` (vía `log_phase_completion.py`)
- 6 cabeceras de versión: `AGENTS.md`, `README.md`, `.cursorrules`, `docs/CONTRIBUTING.md`,
  `GUIA_TECNICA.md`, `REGISTRY.md` (vía `sync_versions.py`)
- `GUIA_TECNICA.md` (nota técnica por fase)
- `DOMAIN_PRIMER.md` (**auto-regenerado**, nunca manual)

**Secuencia obligatoria**:
```bash
# 1. Registrar el release en REGISTRY
./venv/Scripts/python.exe scripts/log_phase_completion.py --release 4.75.0 \
    --desc "Estabilización pre-tribunal: fuente única + punto 8 + severidad 11+2 + fixes A1-A6/V1-V16"

# 2. Sincronizar VERSION.yaml → 6 archivos
./venv/Scripts/python.exe scripts/sync_versions.py

# 3. GUIA_TECNICA: nota técnica por fase (A-H) — redacción manual desde 09 §A/§B

# 4. DOMAIN_PRIMER: auto-regenerar (NO editar a mano)
./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer
```

**Criterios de aceptación**:
- [ ] `log_phase_completion.py --release` registró la entrada en `REGISTRY.md`.
- [ ] `sync_versions.py` actualizó las **6** cabeceras a `4.75.0` (verificar con grep que no queda `4.74.1`).
- [ ] `GUIA_TECNICA.md` tiene una nota técnica por cada fase A-H (no un resumen genérico).
- [ ] `DOMAIN_PRIMER.md` fue **regenerado por script**, no editado a mano.

---

### R4 — Validaciones finales

**Objetivo**: confirmar que el ecosistema documental y de código queda en verde tras el release.

**Comandos**:
```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick    # 4/4 o 7/7
./venv/Scripts/python.exe scripts/validate_agents_md.py             # 6 PASS / 0 FAIL
./venv/Scripts/python.exe scripts/validate_document_integration.py  # gate de no-regresión documental
```

**Criterios de aceptación**:
- [ ] `run_all_validations.py --quick` en verde (todos los checks).
- [ ] `validate_agents_md.py`: 6 PASS / 0 FAIL (coherencia AGENTS.md: gate count 11+2, module refs).
- [ ] `validate_document_integration.py` sin desincronización entre los 4 documentos clave.
- [ ] **AGENTS.md actualizado**: la tabla «Módulos Activos» (fila `quality_gates/`) y el bloque FASE 4.5
      reflejan **11 blocking + 2 advisory** (cambio de FASE-D, AC7). Si FASE-D no lo hizo, RELEASE lo
      verifica y lo corrige aquí (es documento, no código).

---

## Tests Obligatorios

RELEASE no escribe tests; corre los validadores del ecosistema como gate de cierre.

| Validación | Comando | Criterio de éxito |
|------------|---------|-------------------|
| Validaciones rápidas | `run_all_validations.py --quick` | verde (4/4 o 7/7) |
| Coherencia AGENTS.md | `validate_agents_md.py` | 6 PASS / 0 FAIL |
| Integración documental | `validate_document_integration.py` | sin errores |
| Sync de versión | `grep -rn "4.74.1" AGENTS.md README.md .cursorrules docs/CONTRIBUTING.md GUIA_TECNICA.md REGISTRY.md` | 0 coincidencias |

**Comando de validación de la fase**:
```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe scripts/validate_agents_md.py
./venv/Scripts/python.exe scripts/validate_document_integration.py
```

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️ — al finalizar RELEASE, antes de cerrar la sesión y el plan:

1. **`dependencias-fases.md`** — marcar RELEASE ✅ Completada + fecha. **Plan completo.**
2. **`README.md` del plan** — tabla de progreso: las 11 fases ✅; métricas finales; estado «COMPLETADO».
3. **`09-documentacion-post-proyecto.md`** — cerrar Sección D (métricas acumulativas finales) y E
   (archivos afiliados: CHANGELOG, GUIA_TECNICA, AGENTS, README, .cursorrules, CONTRIBUTING, REGISTRY).
4. **`10-analisis-post-implementacion.md`** — añadir el cierre: versión publicada, validadores en verde,
   write-back a QMind ejecutado (si el usuario confirmó) o pendiente.
5. **`evidence/FASE-RELEASE/`** — salidas de los 3 validadores + `git show --stat` del commit de release.

**Commit de release**: al cerrar, proponer al usuario el commit (NO ejecutar `git push` sin confirmación
explícita — memoria `feedback-commits-separados-para-archivos-ya-sucios`). Verificar `git status` antes.

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar RELEASE como ✅ COMPLETADA** ⚠️

- [ ] `VERSION.yaml` en `4.75.0` con codename y fecha (R1).
- [ ] `CHANGELOG.md` con las 5 subsecciones formato CONTRIBUTING pobladas desde `09` (R2).
- [ ] `log_phase_completion.py --release` registró en REGISTRY (R3).
- [ ] `sync_versions.py` actualizó las 6 cabeceras; grep de `4.74.1` = 0 (R3).
- [ ] `GUIA_TECNICA.md` con nota técnica por fase A-H (R3).
- [ ] `DOMAIN_PRIMER.md` regenerado por script (R3).
- [ ] `run_all_validations.py --quick` verde (R4).
- [ ] `validate_agents_md.py` 6/0 — AGENTS.md refleja 11 blocking + 2 advisory (R4).
- [ ] `validate_document_integration.py` sin errores (R4).
- [ ] `09` y `10` cerrados; `dependencias-fases.md` y `README.md` del plan en «COMPLETADO».
- [ ] Commit de release propuesto al usuario (push NO ejecutado sin confirmación).

**NO marcar RELEASE como completada si algún validador falla.** Version Sync no es fallo de código
(memoria `flujo-de-cierre-de-fase-en-iah-cli-validaciones-documentales`): si `sync_versions.py` reporta
diff, es el sync trabajando, no un error.

---

## Restricciones

- **NO ejecutar planes de documentación directamente.** SIEMPRE el flujo
  `log_phase_completion.py` → `sync_versions.py` → CHANGELOG → GUIA_TECNICA → `run_all_validations.py`
  (AGENTS.md §Flujo Documental Obligatorio, regla explícita).
- **NO editar DOMAIN_PRIMER a mano** — se regenera en RELEASE vía `doctor.py`.
- **NO tocar código de producción** en RELEASE. Si un validador falla por código, volver a la fase dueña
  (no parchar aquí).
- **NO `git push` sin confirmación explícita del usuario.** El commit se propone; el push se pregunta.
- **NO hardcodear la versión** en ningún archivo fuera del flujo de sync.

---

## Prompt de Ejecución (para el subagente delegado)

```
Actúa como responsable de release documental del plan ESTABILIZACION-PRE-TRIBUNAL-2026-09-03.

OBJETIVO: publicar la versión 4.75.0 cerrando la documentación oficial del repositorio.

CONTEXTO:
- Versión actual 4.74.1 («Blocklist-v2») → objetivo 4.75.0 («Estabilización pre-tribunal»).
- Fuente única: VERSION.yaml. Nunca hardcodear versiones.
- Datos de entrada: 09-documentacion-post-proyecto.md (secciones A-E) y 10-analisis-post-implementacion.md.
- Flujo obligatorio (AGENTS.md §Flujo Documental): log_phase_completion.py → sync_versions.py →
  CHANGELOG → GUIA_TECNICA → run_all_validations.py. NO ejecutar planes de documentación directamente.

TAREAS:
1. R1 — VERSION.yaml a 4.75.0 + codename + release_date.
2. R2 — CHANGELOG.md entrada 4.75.0 con formato CONTRIBUTING (### Objetivo / ### Cambios /
   ### Archivos Nuevos / ### Archivos Modificados / ### Tests) desde 09.
3. R3 — log_phase_completion.py --release; sync_versions.py (6 archivos); GUIA_TECNICA nota por fase A-H;
   doctor.py --regenerate-domain-primer (DOMAIN_PRIMER auto, NO manual).
4. R4 — run_all_validations.py --quick; validate_agents_md.py (6/0, AGENTS refleja 11 blocking + 2 advisory);
   validate_document_integration.py.

SALIDA: documentos oficiales actualizados + evidence/FASE-RELEASE/ con las 3 salidas de validadores.

RESTRICCIONES:
- NO tocar código de producción; NO editar DOMAIN_PRIMER a mano; NO git push sin confirmación.
- grep -rn "4.74.1" sobre las 6 cabeceras debe dar 0 coincidencias tras sync.

VALIDACIONES:
- run_all_validations.py --quick (verde)
- validate_agents_md.py (6 PASS / 0 FAIL)
- validate_document_integration.py (sin errores)
```
