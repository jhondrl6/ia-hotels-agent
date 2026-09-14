# FASE-RELEASE-4.77.0: Cierre documental + archivado

**ID**: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11 / FASE-RELEASE-4.77.0
**Objetivo**: Publicar v4.77.0 con la documentación oficial sincronizada, certificar los ACs por la vía que decidió P1 (FASE-VERIFY propia o AC-V1 dentro de esta fase), crear el tag anotado, y archivar el plan (R2.5) en el orden de cierre que fija §R2.10 del executor. **NO modifica código fuente.**
**Dependencias**: P2 (si Q1=sí), P3-A, P3-B ✅ + **P4 ✅ o oficialmente diferida** (§Cierre válido sin P4 en `dependencias-fases.md` — "en espera" no abre esta puerta) + FASE-VERIFY ✅ si activó.
**Presupuesto**: 30 iteraciones (R2.1, corte = commit de docs; D-V2.1: auto-reporte con unidad declarada si el instrumento no alcanza el transcript).
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
| FASE-VERIFY | ⟨activa o sustituida por AC-V1 — decisión de P1 en `dependencias-fases.md`⟩ |
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

### Tarea 1: Certificación pendiente (AC-V1) si FASE-VERIFY no activó
- Matriz de certificación AC→artefacto real en el `10-analisis` (patrón VERIFY del predecesor: `evidence/FASE-VERIFY/<PLAN>/MATRIZ-CERTIFICACION.md`), con NR7 (pares verde/rojo) en cada AC de detección/bloqueo. Si FASE-VERIFY **sí** activó, esta tarea solo verifica que su matriz esté citada desde el `10-analisis`.

### Tarea 2: Version bump y sincronía documental
- `VERSION.yaml` → 4.77.0 → `python scripts/sync_versions.py` (6 archivos) → CHANGELOG (formato Objetivo/Cambios/Archivos Nuevos/Modificados/Tests) + GUIA_TECNICA por fase → `python scripts/log_phase_completion.py --fase FASE-RELEASE-4.77.0 --release 4.77.0`.
- Actualizar estado de tests canónico en AGENTS.md (incl. `test_barreda_un_solo_emisor_de_la_clave`: D-V.1 quedó cerrado en P3-B → la nota de "deuda propia" cambia).

### Tarea 3: Cierre de documentación acumulada
- Volcar `09-documentacion-post-proyecto.md` en los documentos oficiales si algo quedó pendiente por fase; completar `10-analisis-post-implementacion.md` (lecciones, decisiones, métricas, sección "Lecciones capitalizadas" + tabla del §9 del maestro actualizada con lo que pasó tras P1).
- **Write-back QMind ANTES de archivar**: `python scripts/validate_qmind_writeback.py --upload <PLAN>` — `--upload` recibe el **stem** del nombre, y la idempotencia es por **título**: si el contenido del `10-analisis` cambió tras la concepción, usar título nuevo.

### Tarea 4: Tag + archivado R2.5 + commit único
- Orden §R2.10: docs → write-back → `--quick` TOTAL PASS → archivado del plan en `Archives/` → revisión manual del diff de `validate_opencode_refs.py --fix` → **tag anotado `v4.77.0`** sobre el commit final → commit único de cierre.
- El push de master **y de los tags** (`v4.76.0` pendiente desde 2026-09-14 + `v4.77.0`) se hace solo con confirmación explícita del usuario (preflight de push: medir alcance antes de empujar).

**Criterios de aceptación**:
- [ ] Cada AC final certificado contra artefacto real, por la vía decidida en P1 (declarada en `dependencias-fases.md`)
- [ ] P4: ✅ o Diferida con decisión registrada — nunca "en espera"
- [ ] `sync_versions.py` + `version_consistency_checker.py` en verde; CHANGELOG/GUIA_TECNICA completos
- [ ] `run_all_validations.py --quick` TOTAL PASS (9/9)
- [ ] Write-back QMind ejecutado antes del archivado
- [ ] Plan archivado + diff del `--fix` revisado a mano
- [ ] Tag `v4.77.0` creado; `v4.76.0` presente localmente

---

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md` y `README.md`: plan ✅ completo (o con las diferencias del cierre)
2. `06-checklist-implementacion.md`: §Cierre del plan marcado ítem a ítem
3. `evidence/FASE-RELEASE/`: matriz de certificación + salida del write-back + `git tag -n` del par de tags
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
