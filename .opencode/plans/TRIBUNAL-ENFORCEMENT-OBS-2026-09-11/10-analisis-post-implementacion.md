# Análisis Post-Implementación — TRIBUNAL-ENFORCEMENT-OBS-2026-09-11

> **Estado**: 🔄 en curso (0 fases cerradas)
> **Plan**: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11 · **Versión objetivo**: 4.77.0 (confirmar en P1)
> **Creado**: 2026-09-14 en la sesión de ajuste — el executor lo exige **desde la concepción** del plan (v1.4.0+ del template); este plan lo debió desde el 2026-09-11 y la deuda queda aquí registrada, no retrodatada. Se actualiza al cierre de **cada** fase.

---

## Resumen de Ejecución (llenar al cierre de cada fase)

| Fase | Sesión | Estado | Iteraciones (ids + tool_use, corte = commit) | delegate_task | Notas |
|------|--------|--------|----------------------------------------------|---------------|-------|
| Ajuste de preparación *(orquestación, fuera de presupuesto de fase)* | 2026-09-14 | ✅ | auto-reporte (D-V2.1: el instrumento no alcanza el transcript bajo el cliente actual; unidad declarada) | No | Etapa 1 completada: prompts P3-A/P3-B/P4/RELEASE + 09/10 creados; P2 diferido a Q1 con declaración; P3 dividida por R3; FASE-VERIFY condicionada; cierre sin P4 fijado; citas `3bdc14e`/origin/tag `v4.76.0` corregidas |
| FASE-P1 | — | ⬜ | — | No | Decisión Q1–Q6 + contrato + cierre FASE-VERIFY + prompt P2 si Q1=sí |
| FASE-P2 | — | ⬜ (condicional Q1) | — | No | ⟨—⟩ |
| FASE-P3-A | — | ⬜ | — | No | ⟨—⟩ |
| FASE-P3-B | — | ⬜ | — | No | ⟨—⟩ |
| FASE-P4 | — | ⬜ (opcional: §Cierre válido sin P4) | — | Sí (corrida) | ⟨—⟩ |
| FASE-VERIFY | — | ⬜ (condicional §4.6) | — | No | ⟨—⟩ |
| FASE-RELEASE-4.77.0 | — | ⬜ | — | Sí | ⟨—⟩ |

**Regla L-R.1 (vigente para este archivo)**: una fila en `⬜` con celda de iteraciones en `—` **no bloquea**; lo que bloquea el ✅ de fase cerrada es `—` **después** de cerrada. Una fase diferida (P2 por Q1=no, P4 por cierre sin P4) se marca `Diferida` con la decisión como causa, nunca `—`.

---

## Decisiones Arquitectónicas / de Proceso

### D-AJUST.1 — División de FASE-P3 en P3-A / P3-B (2026-09-14)
- **Decisión**: P3 empaquetaba 6 fixes (AC8, tier del acta, AC-F4, AC-F5, barreda, versión) y excedía el máximo de R3 (≤4 tareas). Se divide: **P3-A** = AC-F1 (AC8) + AC-F2 (tier acta) + AC-F4 (primer piso `B_PLUS`) sobre `judge.py`/`asset_reviewer.py`; **P3-B** = AC-F3 (barreda, test-only) + versión del acta + AC-F5 solo condicional a Q5=(a), sobre tests/`acta_writer.py`/`main.py`.
- **Rationale**: la división es por naturaleza de cambio (detección/fidelidad del acta vs cableado/test), no por tamaño: P3-A no toca `main.py` ni `acta_writer.py`; P3-B solo toca `main.py` bajo Q5=a. Cada fase nace dentro de R3 y con baseline NR1 propio.
- **Alternativas rechazadas**: (i) agrupar "tier acta + versión acta" en una sola tarea para caber en 4 — rechaza medir R3 con agrupaciones convenientes, que es como la regla muere; (ii) dejar P3 inteira "porque son fixes chicos" — R3 existe precisamente contra el agotamiento por acumulación (la regla lo dice: el orquestador que crea fases grandes es responsable del agotamiento de las sesiones siguientes).

### D-AJUST.2 — FASE-VERIFY condicionada, no decidida en la preparación (2026-09-14)
- **Decisión**: los 3 criterios de §4.6 no son evaluables hoy porque el conteo de fases de implementación depende de Q1 (P2), Q5 (AC-F5 en P3-B) y Q4/T3a (P4). Se registra la evaluación condicional en `dependencias-fases.md` y **FASE-P1 la cierra**.
- **Rationale**: activar o excluir VERIFY con una decisión no tomada sería el gesto que L-V.4 prohíbe (decidir en la fase equivocada); el plan ya tenía el patrón embebido en RELEASE (AC-V1) sin declararlo sustituto.
- **Alternativas rechazadas**: (i) fijar "no activa" (conteo P2+P3=2) — omitía que P4 es fase con ejecución E2E y que el conteo cambia con Q1; (ii) crear ya el prompt VERIFY — prompt condicional a una decisión pendiente es un entregable falso.

### D-AJUST.3 — Escenario de cierre sin P4 (2026-09-14)
- **Decisión**: si T3a no se cierra (con Q5≠c), P4 se difiere con la misma mecánica que Q5=(c) — §Cierre válido sin P4 en `dependencias-fases.md`. El fallo de T3b no difiere: AC-O0 (`B_PLUS` con límite). Si P1 eligió Q1=(c) y T3a falla después, la resolución por defecto es O4 documentada.
- **Rationale**: sin esto, RELEASE quedaba bloqueada por una precondición externa que quizá nunca llega; con esto, el diferimiento es una decisión con rastro, no un `—`.

### ⟨P1 añade sus DA-* aquí al cerrar⟩

---

## Lecciones Aprendidas (mínimo 3 por fase con aprendizaje; al cerrar cada fase)

| ID | Pasó / Qué | Por qué | Cura (y si es regla sin verificador, declarada — L-R.4) | Pertinencia |
|----|-----------|---------|----------------------------------------------------------|-------------|
| L-AJUST.1 | Un plan citaba como viva (`bd2bf57`, "local sin push", "sin tag") una verdad que un rebase y un push posteriores invalidaron | Las citas de commit se escribieron en presente en la concepción y ningún check las contra-verifica al re-verificar el plan | Higiene aplicada 2026-09-14: citar el commit **vivo en origin** y distinguir en el texto lo histórico ("existen desde v2.21.0") de lo presente. Sin verificador mecánico → límite declarado (L-R.4) | INCLUIR — aplicable a todo plan largo con predecesor |
| ⟨más lecciones al cerrar fases⟩ | | | | |

---

## Métricas de Ejecución (al cerrar cada fase)

- Tests canonónicos: pre-plan 4.063 / 293 archivos (medido 2026-09-11, v4.76.0) — actualizar con delta R2.7 por fase.
- `--quick`: 9 checks desde `4ac139a` (eran 8 al cierre del predecesor).
- Coherence / publicación: al cerrar.

---

## Seguimientos Abiertos

- Empujar el tag `v4.76.0` (creado local 2026-09-14 sobre `3bdc14e`) junto con el push que autorice el usuario — no se empuja solo.
- La rama local `backup/pre-sanidad-evidence-20260912` conserva el objeto `bd2bf57`: candidata a podar cuando el usuario confirme que nada la referencia (no borrar desde un agente sin pedirlo).
- ⟨P1 añade: decisión sobre la cola de 78 adyacentes (Q7) y §3.b⟩

---

## Lecciones capitalizadas de planes anteriores

Fuente canónica: `00-lecciones-capitalizadas.md` (Paso 0 horizontal del 2026-09-12 + capa fría del índice). Su tabla §2 (19 lecciones con dueño y efecto) **es** esta sección; no se duplica. Lo que aquí se registra es el contraste promesa↔realidad al cerrar cada fase:

| Fase | Lecciones que la gobernavan | Se aplicó de verdad (evidencia) | No aplicó / parcial (causa) |
|------|-----------------------------|----------------------------------|------------------------------|
| ⟨P1…⟩ | | | |

Capa fría y consultas literales: §1 de `00-lecciones-capitalizadas.md`. Límite declarado (L-R.4): la **forma** del Paso 0 la verifica `scripts/validate_lesson_capitalization.py` desde `e02a688`; su **pertinencia** sigue disciplinada por lectura humana — este plan no debe dar por verificado lo que ningún check mira.
