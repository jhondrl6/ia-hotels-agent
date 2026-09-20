# Checkpoint de FASE-G — cierre ejecutado, commiteado y empujado el mismo día

**Plan:** REFACTOR-WHATSAPP-ENTREGA-2026-09-18 · **Fase:** G · **Fecha:** 2026-09-20
**HEAD de partida:** `d7ff932` (paridad 0/0 con `origin/master` al abrir)
**HEAD al cerrar la sesión:** `66e17bd` — **32 rutas, +10.074 / −217**, empujado a `origin/master`
y en **paridad 0/0**. El usuario autorizó commit y push con texto literal («Git Commit y push») en
una petición separada; tag y write-back no se pidieron y siguen sin autorización.

## Estado de la fase

**CERRADA en contenido y en corte de versionado.** Las cuatro tareas del prompt están ejecutadas y
medidas. Contador **v4complete 0/1** (intacto).

| Requisito del prompt | Estado | Dónde se ve |
|---|---|---|
| T1 PRE e inventario de firmas | ✅ | `tests_baseline_pre.txt` (selección literal), `inventario-callers.md` |
| T2 Verificador AST (V-1) | ✅ | `scripts/validate_wiring.py`, `.opencode/wiring_report.json`, check 11 del quick |
| T3 Retiro del contrato muerto (F-D') | ✅ | `modules/assessment_builder.py`, `main.py`, `inventario-callers.md` §3 |
| T4 POST, mutaciones y cierre | ✅ | `tests_baseline_post.txt`, `mutation_report.json`, `resultados-y-observaciones.md` |
| Rojo de AC7 sobre la divergencia **antes** de corregirla | ✅ demostrado sobre el código tal como está hoy | `--ignore-known` → 3 `SENAL_OMITIDA` en `v4_asset_orchestrator.py` |
| QMind por el eje de cierre | ✅ permitida y respondida (6 aportes, 3 aplicados y medidos) | `qmind-eje-cierre.md` |
| Cierre incremental completo | ✅ | ver lista abajo |
| Commit / push | ✅ ejecutados el 2026-09-20 con autorización literal | `66e17bd` → `origin/master` (paridad 0/0) |
| Tag / write-back a QMind | ⛔ **sin autorización** (no pedidos) | §Autorizaciones pendientes |

## Validaciones al cerrar (medidas, no previstas)

| Check | Resultado |
|---|---|
| `run_all_validations.py --quick` | **11/11 ALL VALIDATIONS PASSED** (10 checks al abrir → 11 con `Wiring`) |
| `validate_document_integration.py` | All checks passed |
| `validate_plan_closure.py` | ningún plan vivo declara cierre con filas pendientes |
| `build_lesson_index.py --check` | índice fresco, **318 IDs** (316 → +`L-ENT.12`, `L-ENT.13`), 43 citados sin definición (sin cambio) |
| `sync_versions.py --check` | **7/7 in sync** (tras `--rule registry_last_update`; ver §5bis de `resultados-y-observaciones.md`) |
| `pytest tests/test_validate_wiring.py` | **18 passed** |
| Par PRE/POST (misma selección) | 1.313/1/2 → 1.313/1/2 (**delta 0**) → POST-B 1.331/1/2 (**+18**) |
| `mutation_report.json` | **7/7 rojo por el guard, 0 por syntax/import**, árbol restaurado por sha256 |
| Funciones canónicas del repo | 4.246 → **4.264** |
| rojo preexistente (no de G) | `test_medido_contra_el_predecesor_entra_en_alcance…`, causa: `9c4a001` archivó el plan; conservado en PRE y POST, con dueño registrado |
| Pre-commit hooks del commit `66e17bd` | **7/7 PASSED** (consistencia de versión, sincronización de 7 archivos, referencias `.opencode`, citas de plan, filas de cierre, frescura del índice, capitalización). Ningún hook se saltó y ninguno modificó el árbol después del commit |

## Superficie commiteada (la misma que se midió en el pre-flight)

32 rutas en `66e17bd` — **19 modificadas y 13 nuevas**, +10.074 / −217 líneas (medido con
`git show --name-status` y `--shortstat`, no con el conteo del árbol). El pre-flight del working tree
daba 12 rutas sin trackear porque `git status` agrupa el directorio de evidencia en una sola entrada.

- **Código de producto (4):** `scripts/validate_wiring.py` (nuevo, 905 l), `modules/assessment_builder.py`,
  `main.py` (1 línea), `scripts/run_all_validations.py`.
- **Tests (3):** `tests/test_validate_wiring.py` (nuevo, 18 funciones), `tests/test_assessment_builder.py`,
  `tests/test_validate_lesson_capitalization.py`.
- **Artefacto del AC7 (1):** `.opencode/wiring_report.json` (nuevo).
- **Evidencia (10):** `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-G/`.
- **Documentación (14):** CHANGELOG, GUIA_TECNICA, REGISTRY, `.last_doc_phase.json`,
  DOMAIN_PRIMER (por su writer), LECCIONES-INDEX + `lecciones_index.json` (par regenerado por
  `build_lesson_index.py`) y los 7 documentos del plan.
- **No tocado, a propósito:** `AGENTS.md`, `.cursorrules`, el workflow canónico, `VERSION.yaml`,
  hooks, `domain_gates.py`, Tribunal, umbrales y `write/publish/suppress`.

El stageo fue explícito por ruta (`git add <32 rutas>`), no `git add -A`; el pre-flight midió
paridad 0/0 antes del commit, así que el push quedó en exactamente 1 commit por delante y no
arrastró trabajo ajeno.

## Lo que la siguiente sesión (FASE-0) necesita saber

1. El quick **son 11 checks**, no 10: `_check_wiring` corre en el modo rápido. Su verde publica
   población; su rojo nombra archivo, línea y señal.
2. **El árbol está limpio y en paridad con `origin/master`**: nada que no revertir, y nada pendiente
   de stagear. Partir de `66e17bd`, no de `d7ff932`.
3. `modules/asset_generation/v4_asset_orchestrator.py` tiene **tres** invocaciones con señal
   omitida (286, 309, 447), amparadas por excepción tipada con dueño FASE-B/AC1. No son de FASE-0.
4. AC20 cubre **dos** ramas de publicación sin `package_evidence` (`packager.publish()` y el `except`
   never-block de `main.py`) — propiedad de FASE-0, no tocada ni declarada cubierta por G.
5. Cada fase intermedia re-abrirá el rojo `Version Sync` en `registry_last_update` al registrar con
   `log_phase_completion.py`; la cura usada por G fue `sync_versions.py --rule registry_last_update`
   (el escritor oficial, acotado). La cura de fondo tiene dueño: RELEASE/operador.

## Autorizaciones pendientes (se piden por separado)

- **Tag** — no corresponde en fase intermedia (no se cambió `VERSION.yaml`).
- **Write-back a QMind** — requiere autorización expresa y título nuevo si el aporte cambió
  (`--upload` es idempotente por título).

Commit y push **ya ejecutados** el 2026-09-20. FASE-0 sigue sin iniciar (R1).
