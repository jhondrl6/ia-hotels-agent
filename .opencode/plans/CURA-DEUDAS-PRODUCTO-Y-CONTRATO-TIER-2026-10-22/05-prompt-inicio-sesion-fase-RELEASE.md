# FASE-RELEASE-4.82.0 — Cierre documental y archivado del plan

**ID**: FASE-RELEASE-4.82.0 · **Plan**: `CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22`
**Objetivo**: release 4.82.0 sincronizada, documentación oficial actualizada, write-back QMind y archivado por el orden R2.10.
**Dependencias**: FASE-A…FASE-VERIFY ✅.
**Complejidad técnica**: BAJA · **Duración estimada**: 2 horas
**Modo de ejecución**: **DIRECTO** o **subagente con `Agent`** (solo YAML/MD y scripts stdlib).

## Contexto

Última fase. **NO modifica código fuente, NO ejecuta `v4complete`.** Sí corrige la narrativa **vigente** vencida de `ROADMAP.md` y `GUIA_TECNICA.md` (H8); **no** reescribe `CHANGELOG.md`/`REGISTRY.md` como historia. Cada fase ya se registró en `docs/contributing/REGISTRY.md`; esta fase **verifica** el registro y solo escribe la entrada que falte (`log_phase_completion.py` es aditivo: re-registrar duplica). Release objetivo: **4.82.0** (comportamiento de producto cambiado: render, veredicto, score `/90`, retiro de `spark`, stub retirado).

**H8 (heredado de FASE-C)**: `docs/GUIA_TECNICA.md` (5 ocurrencias) y `ROADMAP.md` (4) conservan `APROBADO-CONDICIONAL-PENDING-ONBOARDING`. La prosa de `GUIA_TECNICA` §primer piso describe el mecanismo **vigente** y quedó falsa; no es historia. Esta fase la corrige junto con el principio vigente de `ROADMAP.md` §veredictos y sus referencias. `CHANGELOG`/`REGISTRY` conservan el literal como registro histórico y no se tocan por H8.

**Fases a verificar en el registro**: FASE-A, FASE-B, FASE-C, FASE-D, FASE-E, FASE-F, FASE-H1, FASE-H2, FASE-E2E-PRE, FASE-E2E, FASE-VERIFY. No existen FASE-G ni FASE-H única.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A…FASE-VERIFY | ✅ |

## Tareas (transcripción operativa de `docs/CONTRIBUTING.md §Trigger-Documentacion-Oficial`)

1. **E1 Diagnóstico**: `./venv/Scripts/python.exe scripts/version_consistency_checker.py` + `./venv/Scripts/python.exe main.py --doctor`.
2. **Verificación de registro (Paso 4.5.1)**: cada fase del plan tiene SU entrada en `docs/contributing/REGISTRY.md`; solo registrar en tardanza la que falte, con `--fecha` del cierre real de esa fase y `--nota` del motivo.
3. **E2 Sync**: `./venv/Scripts/python.exe scripts/sync_versions.py` (VERSION.yaml → headers; `REGISTRY.md` no entra).
4. **E3 CHANGELOG**: entrada `## [4.82.0] - Título — YYYY-MM-DD` con Objetivo / Cambios Implementados / Archivos Nuevos / Archivos Modificados / Tests (referencia a `evidence/`, no cifras re-transcritas). Datos desde `09-documentacion-post-proyecto.md` §A/B/D/E.
5. **E4 GUIA_TECNICA**: «Notas de Cambios v4.82.0» por fase (módulos afectados, problema, solución, backwards compatibility). Además, **H8**: refrescar la prosa vigente que aún publica `APROBADO-CONDICIONAL-PENDING-ONBOARDING` —`GUIA_TECNICA.md` §primer piso (descripción del mecanismo, no la historia) y `ROADMAP.md` §veredictos (principio vigente y sus referencias)— a `APROBADO-CONDICIONAL` + `conditional_reason`; la historia de `CHANGELOG`/`REGISTRY` se conserva.
6. **E5 Skills/Workflows** + **E6** `doctor.py --status` + **E7** `doctor.py --regenerate-domain-primer` y `doctor.py --context`.
7. **E8**: symlink `.agent/workflows` intacto; `run_all_validations.py --quick` verde; `git diff --stat` revisado.
8. **E8b README audit**: conteos del README medidos por comando (`pytest --collect-only` / `find modules/`), cifras desde `09` §D, nunca re-copiadas entre secciones.
9. **Cierre R2.5/R2.10 — orden fijo, no se permuta**:
```bash
# 1. write-back con el plan aún en la raíz
./venv/Scripts/python.exe scripts/validate_qmind_writeback.py --upload CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22
# 2. índice con el plan cerrado consultable
./venv/Scripts/python.exe scripts/build_lesson_index.py
# 3. archivar: git mv si el plan está versionado; mv si aún es untracked (declararlo)
git ls-files --error-unmatch .opencode/plans/CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22 >/dev/null 2>&1 \
  && git mv .opencode/plans/CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22 .opencode/plans/Archives/ \
  || mv .opencode/plans/CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22 .opencode/plans/Archives/
# 3b. el índice congela la ruta nueva
./venv/Scripts/python.exe scripts/build_lesson_index.py
./venv/Scripts/python.exe scripts/validate_opencode_refs.py --fix
./venv/Scripts/python.exe scripts/validate_plan_citations.py --update-baseline
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```
10. **Registro de la fase** (esta fase sí se registra a sí misma):
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-RELEASE-4.82.0 --fecha <fecha-de-cierre> \
    --desc "Release 4.82.0: curación de deudas de producto + contrato plantilla↔tier + E2E-PRE/E2E Don Alfonso" \
    --check-manual-docs
```
11. **Write-back de contexto**: `CONTEXT-DEUDAS-PRODUCTO-VERIFICADAS-2026-10-21.md` **no autodeclara aporte durable** → no se ingiere por el writer. Verificar con el writer; si la cura de la segunda vía del verificador se ejecutó en este ciclo, la publicación de ese contexto va con ella. `P6.5`/`D21` no se publican ni se tocan.
12. **Estado del ZIP**: AC7 exige un ZIP real; si la corrida no publicó, FASE-E2E no puede estar ✅ y RELEASE no debe ejecutarse.

## Tests Obligatorios

Ninguno nuevo. Verificación: `version_consistency_checker.py`, `run_all_validations.py --quick`, `build_lesson_index.py --check`, write-back y `git ls-files` del plan.

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md`: FASE-RELEASE ✅ + checklist de cierre completo.
2. `10-analisis-post-implementacion.md`: §Checklist de Cierre relleno; §Métricas por referencia a `09` §D.
3. `00-lecciones-capitalizadas.md` §4 actualizado al estado real del cierre.
4. Commit **opcional, posterior y separado**, con autorización expresa del Operador y pathspec explícito. El `mv`/`git mv` es trabajo en árbol; materializarlo es decisión del Operador.

## Criterios de Completitud (CHECKLIST)

- [ ] Registro de las 11 fases **verificado** (no re-registrado); solo escrita la que faltara
- [ ] `sync_versions.py` + `version_consistency_checker.py` sin discrepancias; Version Sync Gate sin `(!)`
- [ ] CHANGELOG `[4.82.0]` con secciones requeridas; GUIA_TECNICA con nota por fase; GUIA_TECNICA/ROADMAP vigentes sin el literal viejo (H8); README audit con cifras desde la fuente
- [ ] `--quick` verde; `doctor.py --status` sin errores; DOMAIN_PRIMER verificado
- [ ] Orden R2.10 ejecutado completo (write-back → índice → `mv`/`git mv` → índice → refs → citas → quick)
- [ ] `P6.5`/`D21` y `T1_CERTIFIABLE_CLAUSES` intactos
- [ ] Si `--strict` global del write-back sale `NO-EVALUABLE` o `[DUPLICADO-VIGENTE]` por una fuente ajena, se declara con dueño; no se convierte en rojo de este plan ni se fuerza un verde

## Restricciones

- **NO** modifica código fuente; **NO** ejecuta `v4complete`. **Sí** corrige la narrativa vigente de `ROADMAP.md`/`GUIA_TECNICA.md` (H8), sin tocar la historia de `CHANGELOG`/`REGISTRY`.
- Release **4.82.0** fija (el Version Sync Gate compara `CHANGELOG.md [4.82.0]` contra `VERSION.yaml`, sin prefijo `v`).
- Presupuesto: tope **60 tool-use**; instrumento legado/no comparable si no aplica; corte «listo para revisión».

## Prompt de Ejecución

```bash
Actúa como especialista en el repo iah-cli. Ejecuta únicamente FASE-RELEASE-4.82.0 del plan .opencode/plans/CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22.
Lee 05-prompt-inicio-sesion-fase-RELEASE.md, 01-plan-maestro.md §1 y §4, 00-lecciones-capitalizadas.md §4, dependencias-fases.md y workflow canónico.
OBJETIVO: cerrar la release 4.82.0 con documentación oficial sincronizada y plan archivado por el orden R2.10.
TAREAS: E1 diagnóstico, verificación de registro de 11 fases, E2 sync, E3 CHANGELOG, E4 GUIA_TECNICA + corrección H8 (ROADMAP/GUIA_TECNICA vigentes), E5-E8 docs y validaciones, E8b README audit, cierre R2.10 con mv/git mv, registro propio.
CRITERIOS: Version Sync Gate sin alertas; --quick verde; orden R2.10 completo; P6.5/D21 intactos.
VALIDACIONES: version_consistency_checker.py; run_all_validations.py --quick; build_lesson_index.py --check.
```
