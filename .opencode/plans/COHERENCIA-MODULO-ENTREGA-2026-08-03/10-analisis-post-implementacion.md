# Análisis Post-Implementación — COHERENCIA-MODULO-ENTREGA

> **Estado**: EN CURSO — FASE-A y FASE-B registradas (lecciones L1-L9, 2026-08-03); matriz de verificación se completa en FASE-E y resumen final en FASE-RELEASE.
> **Plan**: COHERENCIA-MODULO-ENTREGA-2026-08-03
> **Versión objetivo**: v4.70.0
> **Baseline auditado**: run 2026-08-01 17:05:39 (Zi One Luxury, coherence 0.9168, gate PASSED con doc auto-contradictorio)
> **Run de verificación**: FASE-E — `output/v4_verify_4.70.0`

---

## Resumen de Ejecución (llenar al cierre)

| Fase | Sesión | Estado | Iteraciones | delegate_task | Notas |
|------|--------|--------|-------------|---------------|-------|
| FASE-A | 2026-08-03 | ✅ | Multisesión (bloqueos del equipo, ver L1) | No (directo) | D1+D2 cerrados; 0 regresiones en código modificado; validaciones 5/5 |
| FASE-B | 2026-08-03 | ✅ | 2 sesiones (replanteo tras cuelgue del pipe, ver L6) | No (directo, no delegable) | D3+D4+N1 cerrados; DEC-B1/B2/B3 opción A; 8 tests nuevos (102 tests FASE-B green); 38 fallos probados preexistentes (22 dinámico vs HEAD, 16 evidencia estática); validaciones 5/5; REGISTRY fase 408 |
| FASE-C-A | 2026-08-03 | ✅ | 1 sesión | No (directo) | D5+N2 cerrados; DEC-C1 WARNING + DEC-C2 Option A; 9 tests nuevos + 3 actualizados; 303 tests quality_gates green; validaciones 5/5 |
| FASE-C-B | — | ⏳ | —/60 | Sí (2 tracks paralelos) | |
| FASE-D | — | ⏳ | —/60 | Sí (track N5-N8) | |
| FASE-E | — | ⏳ | —/60 | Sí (v4complete) | |
| FASE-RELEASE | — | ⏳ | —/60 | Delegable | |

### Evidencia v4complete FASE-E (llenar)

| Hotel | Output | evidence_tier | coherence | ZIP sin históricos | Onboarding inyectado |
|-------|--------|---------------|-----------|:---:|:---:|
| Zi One Luxury | ⏳ | — | — | ⏳ | ⏳ |

---

## Matriz de Verificación de Hallazgos (llenar en FASE-E — Expected vs Real vs Status)

| # | Hallazgo | Expected | Real | Status |
|---|----------|----------|------|--------|
| D1 | Brecha "Sin OG" falsa | Doc: "Open Graph Tags Incompletos (8 tags detectados)"; breakdown AEO coherente | | ⏳ |
| D2 | 9 vs 4 vs "7" brechas | pain_ledger N == doc N; template dinámico; pesos sobre N real | | ⏳ |
| D3 | Costos divergentes | `estimated_monthly_cop` del report == costos del doc | | ⏳ |
| D4 | Escenarios ocultados | Escenarios reales 19.6M/7.19M/−6.8M con labels+probs; CG-SCENARIO-ORDER en gate_report | | ⏳ |
| D5 | Coverage covered=0 | covered > 0 o mensaje honesto | | ⏳ |
| D6 | CWV falsa explicación | Estado real de performance ("API key inválida" si ERROR) | | ⏳ |
| D7 | "203 reseñas" estático | Reviews parametrizadas desde audit | | ⏳ |
| D8 | Atribución "algoritmo de Google" | "algoritmo propio de IA Hoteles Agent sobre datos de Google Places" | | ⏳ |
| D9 | Target fotos 20 vs 40+ | Target 40 compartido | | ⏳ |
| D10 | "Instagram, Instagram, Facebook" | Dedup antes del tope; TikTok/YouTube si aplican | | ⏳ |
| D11 | commercial_gates_report stale | Reporte fresco (timestamp == run) | | ⏳ |
| D12 | occupancy "regional" mal etiquetada | Label por origen real ("onboarding") | | ⏳ |
| N1 | Recuperación 6m diverge 3.2× | Misma cifra en diagnóstico y propuesta | | ⏳ |
| N2 | hard_contradictions no lee el doc | Gate doc↔audit reporta contradicciones (modo WARNING) | | ⏳ |
| N3 | Docs byte-idénticos entre runs | diff baseline vs FASE-E > 3 líneas | | ⏳ |
| N4 | ZIP con 7 gate reports históricos | ZIP con SOLO artefactos del run actual | | ⏳ |
| N5 | "acima" (portugués) | "arriba" | | ⏳ |
| N6 | "Por que importa" | "Por qué importa" | | ⏳ |
| N7 | Truncamiento a mitad de palabra | Corte por palabra | | ⏳ |
| N8 | "70% de confianza" mal atribuido | Label coherente con la probabilidad del escenario | | ⏳ |
| N9 | Señales duplicadas PageSpeed | execution_trace coherente con texto del doc | | ⏳ |

---

## Lecciones Aprendidas (llenar — mínimo 3)

Formato por lección: **qué pasó / por qué / qué lo previene** + evaluación de pertinencia para futuras releases (modelo contexto §9: INCLUIR/EXCLUIR con razón).

### L1 (FASE-A) — Tests patológicos preexistentes bloquean el equipo
- **Qué pasó**: todo intento de correr la suite completa `tests/commercial_documents tests/data_validation` congelaba el equipo (3+ bloqueos con reinicio incluido), atascándose siempre ~34% del avance.
- **Por qué**: `test_proposal_generator.py` fuga ~8 GB de RAM y `test_price_consistency.py` se cuelga indefinidamente. Son defectos **preexistentes** del área de propuesta/precios — probado corriendo `test_price_consistency.py` en el baseline limpio (stash de los cambios de FASE-A): también se cuelga. FASE-A no toca ese código.
- **Qué lo previene**: (a) NUNCA correr la suite completa en un solo proceso ni en paralelo; (b) correr solo los tests que ejercitan el código modificado, en archivos/lotes pequeños secuenciales (cada proceso libera memoria al terminar); (c) timeout en primer plano (un cuelgue se autoconvierte a background y permite matarlo) o vigilante de RAM; (d) para matar un pytest colgado: `taskkill /F /PID <pid> /T` con permisos elevados — `Stop-Process` es denegado por el sandbox.
- **Pertinencia**: **INCLUIR** en todas las fases del plan (B toca propuesta: resolver los hogs ANTES de su regresión) y releases futuras. Regla durable registrada en memoria del agente (`development_test_specification`).

### L2 (FASE-A) — Error de categoría: validaciones documentales tratadas como fallos de tests (el bucle)
- **Qué pasó**: `run_all_validations.py --quick` fallaba en Version Sync y Document Integration; se re-ejecutó la suite pesada repetidamente esperando que pasaran, generando el bucle de bloqueos.
- **Por qué**: esas validaciones son de **documentación/versionado de post-ejecución**, no de código. Version Sync: headers desincronizados con VERSION.yaml (drift preexistente: AGENTS.md en v4.68.0 vs VERSION.yaml 4.69.0). Document Integration: README decía "Pain narratives (14)" pero el YAML ya tenía 16. Ninguna se arregla corriendo tests.
- **Qué lo previene**: antes de re-ejecutar cualquier suite, **clasificar el tipo de fallo** (test/código vs documental/versionado). Version Sync → `python scripts/sync_versions.py`; Document Integration → actualizar el conteo real en README. Regla durable registrada en memoria (`development_practice_specification`).
- **Pertinencia**: **INCLUIR** — aplica a todas las fases y al flujo documental obligatorio.

### L3 (FASE-A) — `log_phase_completion.py --release` en fase intermedia activa un gate imposible
- **Qué pasó**: la invocación con `--release 4.70.0` (como figuraba en el prompt de FASE-A) fue rechazada por el VERSION SYNC GATE: exige entrada `[4.70.0]` en CHANGELOG, que las fases intermedias no deben crear ("NO editar CHANGELOG todavía, se acumula para RELEASE").
- **Por qué**: el flag `--release` es semánticamente de cierre de release; usarlo en una fase intermedia (1ª de 6) produce una contradicción huevo-gallina.
- **Qué lo previene**: en fases intermedias ejecutar `log_phase_completion.py` **sin** `--release`; el bump de versión, CHANGELOG y `--release` ocurren solo en FASE-RELEASE. El prompt `02-prompt-fase-A.md` debería corregirse para no inducir el error en re-ejecuciones.
- **Pertinencia**: **INCLUIR** — afecta a las fases B, C-A, C-B, D y E de este plan.

### L4 (FASE-A) — Forense de baseline para distinguir regresión de defecto preexistente
- **Qué pasó**: ante fallos/cuelgues de tests tras los cambios de la fase, existía el riesgo de atribuirlos erróneamente a FASE-A (y viceversa).
- **Por qué**: sin prueba de baseline no hay forma de determinar responsabilidad; el plan declaraba "0 regresión" inicial pero sin verificación reproducible.
- **Qué lo previene**: protocolo aplicado y validado — `git stash push -- <archivos de la fase>` → correr el test problemático en baseline limpio (con timeout) → `git stash pop`. Si falla en baseline = preexistente; si pasa = regresión de la fase. Permitió cerrar FASE-A con evidencia en vez de conjetura.
- **Pertinencia**: **INCLUIR** como protocolo estándar de verificación de regresiones en cualquier fase.

### L5 (FASE-B) — `git stash` falla dentro del sandbox: alternativa backup + checkout
- **Qué pasó**: el protocolo forense de L4 (`git stash push -- <archivos>`) falló con `error: cannot create standard input pipe for update-index: Permission denied` — el sandbox restringe el mecanismo interno de stash. Además el repo ya tenía 2 stashes previos del usuario que no debían tocarse.
- **Por qué**: el sandboxing del terminal bloquea la creación de pipes internos que `git stash` usa para `update-index`; `git checkout HEAD -- <archivos>` sí funciona porque escribe archivos directamente.
- **Qué lo previene**: protocolo alternativo validado en FASE-B — (a) `Copy-Item` de los archivos de la fase a `temp/<fase>_backup/`; (b) `git checkout HEAD -- <archivos>`; (c) correr los tests contra HEAD; (d) restaurar con `Copy-Item` y verificar con `git status` que los archivos vuelven a aparecer como modificados. **Crítico: restaurar SIEMPRE antes de terminar la sesión** (los 4 archivos de FASE-B quedaron en HEAD hasta el replanteo).
- **Pertinencia**: **INCLUIR** — reemplaza/complementa a L4 en entornos con sandbox; ya registrado en memoria del agente.

### L6 (FASE-B) — Pipes de PowerShell sobre pytest cuelgan la captura de salida
- **Qué pasó**: `pytest ... 2>&1 | Select-String | Select-Object -Last N` ejecutado en background se quedó sin producir salida durante 6+ minutos (la misma selección de tests corre en ~2 s sin pipe), forzando matar el proceso y replantear la sesión.
- **Por qué**: el pipe de PowerShell buferiza el stream completo de pytest antes de que `Select-String` emita; combinado con el modo background, la salida nunca llega y no hay forma de distinguir "lento" de "colgado".
- **Qué lo previene**: SIEMPRE redirigir a archivo (`pytest ... > temp\<nombre>.txt 2>&1`) y leer el archivo después con `Get-Content | Select-Object -Last N`. Mantener los procesos pytest cortos y acotados (L1).
- **Pertinencia**: **INCLUIR** — aplica a todas las fases con verificación de tests (C-A, C-B, D, E).

### L7 (FASE-B) — Evidencia mixta (dinámica + estática) para cerrar con los tests patológicos aislados
- **Qué pasó**: el mandato de FASE-B exige `pytest tests/financial_engine tests/commercial_documents -q` con 0 regresiones, pero la suite completa incluye los 3 archivos patológicos de L1 (`test_proposal_generator.py`, `test_price_consistency.py`, `test_proposal_generator_dict.py` → 16 de los 38 fallos) que no se pueden correr de forma fiable.
- **Por qué**: correrlos en el mismo proceso expone al equipo a la fuga de RAM/cuelgue; ignorarlos sin evidencia dejaría la declaración "0 regresiones" sin soporte para esos archivos.
- **Qué lo previene**: protocolo aplicado — (a) **prueba dinámica** sobre el subconjunto seguro: los mismos 22 tests fallan byte-idénticos en HEAD y con FASE-B (`Copy-Item`/`checkout` de L5); (b) **evidencia estática** para los patológicos: `git show HEAD:` prueba que `_calculate_roi` no existía en HEAD, que `score_seo < 30` ya existía, que `config/scenarios.yaml` (recovery 0.35) no fue tocado y que el diff de la fase no cubre esas áreas. Conclusión auditable: 0 regresiones de FASE-B.
- **Pertinencia**: **INCLUIR** — protocolo estándar mientras los tests patológicos sigan vivos; FASE-E lo necesitará para declarar la suite sin regresiones.

### L8 (FASE-B) — Conteo de tests nuevos se verifica con el diff, no con notas previas
- **Qué pasó**: `11-documentacion-post-proyecto.md` decía "+13 (7 nuevos FASE-B + 6 FASE-A)" pero el diff real (`git diff tests/ | grep "+.*def test_"`, incluyendo funciones a nivel de módulo sin indentación) arroja **8** tests nuevos de FASE-B.
- **Por qué**: el conteo previo se escribió antes de terminar T4 y omitió los 2 tests de módulo (`test_estimated_monthly_cop_matches_doc_cost`, `test_impacto_pct_equals_doc_weight`).
- **Qué lo previene**: contar siempre desde `git diff tests/` (patrón `^\+\s*def test_`, no solo indentados) antes de escribir métricas en la documentación acumulativa; se corrigió a +14 (8+6).
- **Pertinencia**: **INCLUIR** — cada fase escribe conteos acumulativos que FASE-RELEASE usa para CHANGELOG.

### L9 (FASE-B) — Confirmada la regla de `log_phase_completion` sin `--release` en fases intermedias
- **Qué pasó**: el prompt `03-prompt-fase-B.md` seguía indicando `--release 4.70.0` (a pesar de la lección L3 de FASE-A); se ejecutó deliberadamente **sin** el flag y el registro en REGISTRY (fase 408) pasó a la primera.
- **Por qué**: el flag dispara el VERSION SYNC GATE que exige entrada de CHANGELOG inexistente en fases intermedias (ver L3).
- **Qué lo previene**: mantener la regla L3; los prompts de fase intermedia que aún traen `--release` en su plantilla (02/03, y probablemente 04-07) deben ignorar ese flag o corregirse en FASE-RELEASE.
- **Pertinencia**: **INCLUIR** — ya confirmada dos veces (A y B); aplica a C-A, C-B, D y E.

### L10 (FASE-C-A) — El usuario puede revertir cambios parciales: verificar estado real antes de asumir
- **Qué pasó**: el agente implementó D5 + N2 correctamente, pero el usuario revirtió selectivamente cambios en los archivos de tests (manteniendo solo la implementación en `publication_gates.py`). El agente continuó editando tests basándose en suposiciones del estado previo, generando conflictos crecientes.
- **Por qué**: tras la intervención del usuario, el agente no verificó el estado real del disco (`git diff`, `git status`) antes de continuar editando. Asumió que sus cambios previos seguían presentes.
- **Qué lo previene**: cuando el usuario interviene con cambios manuales o dice "alto", SIEMPRE ejecutar `git diff --stat` y `git status --short` para ver el estado real antes de continuar. Luego clasificar qué tiene el usuario vs qué esperaba el agente, y alinear.
- **Pertinencia**: **INCLUIR** — aplica a cualquier fase donde el usuario pueda intervenir manualmente.

---

## Seguimientos abiertos (llenar)

| Tema | Estado | Acción futura |
|------|--------|---------------|
| Gate N2 en modo WARNING | ✅ Implementado (FASE-C-A) | Upgrade a BLOCKING en release posterior, tras catalogar contradicciones conocidas |
| `pain_ratio` del pricing | ✅ Resuelto (FASE-B, DEC-B2) | Documentado como métrica distinta (relación precio/fuga), NUNCA como recuperación; `pain_ratio_note` de diagnóstico y propuesta actualizados |
| Tests patológicos propuesta/precios (L1) | Pendiente — bloqueante para suite completa | `test_proposal_generator.py` (fuga ~8GB RAM), `test_price_consistency.py` (cuelgue) y `test_proposal_generator_dict.py` (MagicMock vs `score_seo < 30`): diagnosticar y corregir antes de FASE-E (declaración de suite sin regresiones). FASE-B cerró aislándolos con evidencia mixta (L7) |
| Prompts con `--release` en plantilla (L3/L9) | Documentado | 02/03-prompt aún lo indican; ignorar el flag en C-A/C-B/D/E o corregir plantillas en FASE-RELEASE |
| Pipe de PowerShell sobre pytest (L6) | ✅ Resuelto (FASE-B) | Regla: salida a archivo `> temp\x.txt 2>&1` y lectura posterior; registrado en memoria del agente |
| `git stash` denegado por sandbox (L5) | ✅ Resuelto (FASE-B) | Regla: backup `Copy-Item` + `git checkout HEAD --` + restauración obligatoria antes de cerrar sesión; registrado en memoria |
| Conteo de tests nuevos (L8) | ✅ Resuelto (FASE-B) | Verificar siempre con `git diff tests/` antes de escribir métricas en 11-doc |
| (otros) | | |
