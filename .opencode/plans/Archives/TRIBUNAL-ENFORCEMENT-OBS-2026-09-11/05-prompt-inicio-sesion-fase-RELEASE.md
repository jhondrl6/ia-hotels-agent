# FASE-RELEASE-4.77.0: Cierre documental + archivado

**ID**: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11 / FASE-RELEASE-4.77.0
**Objetivo**: Preparar v4.77.0 con la documentación oficial sincronizada, **verificar y citar** la matriz de certificación que produjo FASE-VERIFY (AC-V1 reducido por D-AJUST.4), y cerrar el plan según §R2.10. **Solo documentación: no corrige código, no remedia incidentes, no produce la certificación ni habilita entregas por excepción.** Commit, tag y publicación se realizan únicamente con su autorización correspondiente.
**Dependencias**: P1/P3-A/P3-B/P2/P4 cerradas + **P5 y P6 certificadas** + **FASE-VERIFY ✅ con su matriz completa** + puerta de seguridad AC-S4 resuelta. No se invoca el antiguo diferimiento de P4. La fase anterior a esta es VERIFY, no P6 (D-AJUST.4 revierte la exclusión de la sesión que había cerrado P1).
**Presupuesto**: 30 iteraciones (R2.1, corte = commit de docs autorizado; D-V2.1: auto-reporte con unidad declarada si el instrumento no alcanza el transcript).
**Complejidad técnica**: BAJA
**Modo de ejecución**: DELEGABLE (con revisión final del orquestador)
**Skill**: `phased_project_executor.md` v2.24.0

---

## Contexto

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-P1 / P2 / P3-A / P3-B | ⟨P1 fija: Q1; el resto se rellena al cerrar cada fase⟩ |
| FASE-P4 | ⟨✅ o Diferida por decisión registrada⟩ |
| FASE-VERIFY | 🔁 **Reabierta por D-AJUST.4 (2026-09-15) → sesión propia ya ejecutada antes de esta**. Su producto es `evidence/FASE-VERIFY/MATRIZ-CERTIFICACION.md`; AC-V1 **cita** esa matriz, no la produce. Decisión y rationale en `dependencias-fases.md` §D-AJUST.4 |
| FASE-RELEASE-4.77.0 | ← ESTA FASE |

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-R.1 | R2.1 era medible y no se midió en 8 de 9 fases | Antes de dar el ✅ global: **ninguna** fila de `06-checklist-implementacion.md` puede quedar en `—` sin que su fase esté diferida por decisión |
| L-R.3 / `validate_plan_closure.py` | La regla de forma de los cierres solo cubre 1 de 8 planes | El cierre de ESTE plan pasa el verificador a mano: `python scripts/validate_plan_closure.py` y revisar su salida contra este checklist |
| L-R.4 | Una regla sin verificador se publica declarándolo | El `10-analisis` declara qué gates del §Deuda se resolvieron, cuáles siguen y quién es el dueño nuevo |
| Lección del predecesor (tag) | v4.76.0 cerró sin tag y el hash citado quedó fuera de origin tras un rebase | El tag `v4.77.0` se crea **en el mismo cierre**, sobre el commit final, y se empuja junto con master solo con autorización (el déficit de `v4.76.0` ya no existe: creado y empujado 2026-09-14) |
| R2.5 + convención `<PLAN>` | `validate_opencode_refs.py --fix` reescribe a ciegas y destrozó comandos archivados | Las auto-referencias de este plan ya son plantilla `<PLAN>`; tras el archivado, el diff del `--fix` se revisa a mano antes del commit único |

---

## Tareas (R3: 4 tareas, 0 comandos largos)

### Tarea 1: Verificar y citar la matriz de FASE-VERIFY (AC-V1 reducido por D-AJUST.4)
- **No producir certificación**: leer `evidence/FASE-VERIFY/MATRIZ-CERTIFICACION.md` y comprobar que (a) tiene las **25 filas** de AC con `Real` + `Status` + nivel RE-V/CIT/CON, (b) ninguna fila quedó en `—` sin fase diferida por decisión registrada (L-R.1), (c) los ❌ abrieron seguimiento con dueño y ninguno se cerró tocando código en VERIFY, y (d) la tabla de 6 cruces cross-fase y el riesgo residual "sin corrida real posterior a P5" están declarados.
- Citarla desde el `10-analisis` §Matriz de certificación (con el enlace a la evidencia) y reportar al orquestador cualquier fila que no se sostenga: **RELEASE no remedia un ❌ de VERIFY**, lo devuelve como sesión de recuperación.
- Depende de: `python scripts/validate_plan_closure.py` (L-R.3 — el verificador no cubre este plan, se pasa a mano y se revisa su salida contra este checklist).

### Tarea 2: Version bump y sincronía documental
- `VERSION.yaml` → 4.77.0 → `python scripts/sync_versions.py` (6 archivos) → CHANGELOG (formato Objetivo/Cambios/Archivos Nuevos/Modificados/Tests) + GUIA_TECNICA por fase → `python scripts/log_phase_completion.py --fase FASE-RELEASE-4.77.0 --release 4.77.0`.
- Actualizar estado de tests canónico en AGENTS.md (incl. `test_barreda_un_solo_emisor_de_la_clave`: D-V.1 quedó cerrado en P3-B → la nota de "deuda propia" cambia).

### Tarea 3: Cierre de documentación acumulada
- Volcar `09-documentacion-post-proyecto.md` en los documentos oficiales si algo quedó pendiente por fase; completar `10-analisis-post-implementacion.md` (lecciones, decisiones, métricas, sección "Lecciones capitalizadas" + tabla del §9 del maestro actualizada con lo que pasó tras P1).
- **Write-back QMind ANTES de archivar**: `python scripts/validate_qmind_writeback.py --upload <PLAN>` — `--upload` recibe el **stem** del nombre, y la idempotencia es por **título**: si el contenido del `10-analisis` cambió tras la concepción, usar título nuevo.

### Tarea 4: Tag + archivado R2.5 + commit único
- Orden §R2.10: docs → write-back → `--quick` TOTAL PASS → archivado del plan en `Archives/` → revisión manual del diff de `validate_opencode_refs.py --fix` → **tag anotado `v4.77.0`** sobre el commit final → commit único de cierre.
- El push de master **y del tag nuevo** queda solo con confirmación explícita del usuario (preflight de push: medir alcance antes de empujar). `v4.76.0` **ya se empujó el 2026-09-14** (ver `10-analisis` §Seguimientos) — de esta fase solo sale `v4.77.0`; se comprueba que `v4.76.0` sigue en origin y no se vuelve a empujar.

**Criterios de aceptación**:
- [ ] **FASE-VERIFY ✅** y su matriz citada desde el `10-analisis` con las 25 filas completas (AC-V1 reducido — D-AJUST.4); ningún ❌ remediado en RELEASE
- [ ] P4: ✅ o Diferida con decisión registrada — nunca "en espera"
- [ ] `sync_versions.py` + `version_consistency_checker.py` en verde; CHANGELOG/GUIA_TECNICA completos
- [ ] `run_all_validations.py --quick` TOTAL PASS (10/10 desde FASE-P5; el denominador completo es 14)
- [ ] Write-back QMind ejecutado antes del archivado
- [ ] Plan archivado + diff del `--fix` revisado a mano
- [ ] Tag `v4.77.0` creado; `v4.76.0` presente localmente

---

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md` y `README.md`: plan ✅ completo (o con las diferencias del cierre)
2. `06-checklist-implementacion.md`: §Cierre del plan marcado ítem a ítem
3. `evidence/FASE-RELEASE/`: **comprobación de completitud** de la matriz de `evidence/FASE-VERIFY/MATRIZ-CERTIFICACION.md` (no se reproduce aquí) + salida del write-back + `git tag -n` del par de tags
4. Reportar al usuario: commits listos, tags pendientes de push (listar exactamente cuáles)

**NO esperar a la siguiente sesión.**

---

## Criterios de Completitud (CHECKLIST)

- [ ] Todos los ítems de `06-checklist-implementacion.md` §FASE-RELEASE-4.77.0 y §Cierre del plan
- [ ] Iteraciones de RELEASE medidas y escritas (L-R.1)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Post-ejecución completada

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- **NO modifica código fuente** (ni un fix "de paso"; hallazgo → seguimiento con dueño en el `10-analisis`).
- NO empujar master ni tags sin confirmación explícita del usuario.
- NO modificar ROADMAP.md.
- NO archivar antes del write-back QMind (invierte el aprendizaje del plan).
