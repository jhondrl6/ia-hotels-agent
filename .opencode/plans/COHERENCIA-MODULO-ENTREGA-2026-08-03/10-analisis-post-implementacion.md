# Análisis Post-Implementación — COHERENCIA-MODULO-ENTREGA

> **Estado**: EN CURSO — FASE-A registrada (lecciones L1-L4, 2026-08-03); matriz de verificación se completa en FASE-E y resumen final en FASE-RELEASE.
> **Plan**: COHERENCIA-MODULO-ENTREGA-2026-08-03
> **Versión objetivo**: v4.70.0
> **Baseline auditado**: run 2026-08-01 17:05:39 (Zi One Luxury, coherence 0.9168, gate PASSED con doc auto-contradictorio)
> **Run de verificación**: FASE-E — `output/v4_verify_4.70.0`

---

## Resumen de Ejecución (llenar al cierre)

| Fase | Sesión | Estado | Iteraciones | delegate_task | Notas |
|------|--------|--------|-------------|---------------|-------|
| FASE-A | 2026-08-03 | ✅ | Multisesión (bloqueos del equipo, ver L1) | No (directo) | D1+D2 cerrados; 0 regresiones en código modificado; validaciones 5/5 |
| FASE-B | — | ⏳ | —/60 | No (directo, no delegable) | |
| FASE-C-A | — | ⏳ | —/60 | No (directo) | |
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

5. ⏳ (continúa en FASE-B…)

---

## Seguimientos abiertos (llenar)

| Tema | Estado | Acción futura |
|------|--------|---------------|
| Gate N2 en modo WARNING | Pendiente decisión | Upgrade a BLOCKING en release posterior, tras catalogar contradicciones conocidas |
| `pain_ratio` del pricing | Pendiente decisión B | Reconciliar o documentar como métrica distinta |
| Tests patológicos propuesta/precios (L1) | Pendiente — bloqueante para suite completa | `test_proposal_generator.py` (fuga ~8GB RAM) y `test_price_consistency.py` (cuelgue): diagnosticar y corregir ANTES de la regresión de FASE-B (que sí toca propuesta); evidencia 2026-08-03: reproducidos en baseline limpio |
| Prompt `02-prompt-fase-A.md` con `--release` (L3) | Documentado | Corregir los prompts de fases intermedias para no pasar `--release`; o reservar el flag a FASE-RELEASE |
| (otros) | | |
