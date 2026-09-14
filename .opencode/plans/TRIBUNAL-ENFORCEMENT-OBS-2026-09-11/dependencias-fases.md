# Dependencias entre Fases — TRIBUNAL-ENFORCEMENT-OBS-2026-09-11

> **Regla**: FASE-RELEASE solo se ejecuta cuando TODAS las fases previas están ✅ — **o** cuando una fase no ejecutada está **oficialmente diferida por decisión registrada** (véase §Cierre válido sin P4). Un diferimiento silencioso no cierra el paso a RELEASE.
> **Regla heredada**: nunca sesiones paralelas sobre el mismo working tree (el plan predecesor documentó sobrescritura de evidencia). P2, P3-A y P3-B comparten `judge.py`/`main.py`/`acta_writer.py` y el conteo NR1 → **secuenciales entre sí, nunca simultáneas**.

---

## Estado de la Etapa 1 (Preparación) — sesión de ajuste 2026-09-14

El executor (§Aplicación) exige que la Etapa 1 genere **todos** los prompts de fase, RELEASE incluido, y los archivos `09`/`10` desde la concepción. Al concebir el plan (2026-09-11) esto no se cumplió; la sesión de ajuste lo cierra:

| Entregable Etapa 1 | Estado |
|--------------------|--------|
| `05-prompt-inicio-sesion-fase-P1.md` | ✅ (revisado en el ajuste: citas, divisiones, escenarios) |
| `05-prompt-inicio-sesion-fase-P3-A.md` · `-P3-B.md` · `-P4.md` · `-RELEASE.md` | ✅ Creados 2026-09-14 con placeholders `⟨P1 fija⟩` donde la decisión manda |
| `05-prompt-inicio-sesion-fase-P2.md` | ⏸️ **Diferido conscientemente**: P2 es la única fase condicional a una respuesta de P1 (Q1=sí + opción O1/O2/O3). Escribir su prompt antes de conocer la opción produciría un prompt falso, no incompleto. **Dueño de crearlo: FASE-P1** (Tarea 3 fija la opción; el AC correspondiente está en su prompt). Este párrafo es la declaración del desvío que exige la disciplina documental del repo. |
| `09-documentacion-post-proyecto.md` · `10-analisis-post-implementacion.md` | ✅ Creados 2026-09-14 con estructura base; el `10-` ya registra la decisión del ajuste (D-AJUST.1–.3) |
| Decisión FASE-VERIFY (§4.6) | ✅ Registrada como **condicionada** (§FASE-VERIFY abajo); su cierre definitivo es AC de FASE-P1 |
| Escenario de cierre sin P4 | ✅ Fijado (§Cierre válido sin P4 abajo) |

---

## Decisión FASE-VERIFY (§4.6 del executor) — condicionada, la cierra FASE-P1

Los tres criterios de activación se evalúan sobre la división de fases **post-ajuste** (P1 decide; P2/P3-B son condicionales):

| Criterio §4.6 | Evaluación |
|---------------|------------|
| 1. ≥3 fases de implementación | P3-A es fija; P2 (Q1=sí) y P3-B con AC-F5 (Q5=a) son condicionales; P4 cuenta como fase de ejecución **solo si no se difiere**. Escenarios: Q1=sí + P4 en pie → 4 fases ✅ · Q1=no (O4) + P4 en pie → 3 ✅ · P4 diferido y Q1=no → 2 ❌ |
| 2. Al menos una fase con ejecución E2E | P4 (corrida `v4complete`) — se cumple **solo si P4 no se difiere** (Q5=c o T3a sin cerrar → ❌) |
| 3. ACs que cruzan fases | Sí, hoy: AC-E0 (P1→P2), AC-F2 (P3-A→P4 lo verifica), AC-O0/AC-O1 (P4 depende del estado que deje P2/P3-B) |

**Decisión registrada 2026-09-14**: FASE-VERIFY **queda condicionada** a lo que salga de Q1/Q4/Q5. Si al cerrar P1 se cumplen los tres criterios, el plan gana una sesión `05-prompt-inicio-sesion-fase-VERIFY.md` (patrón del predecesor: certificación ACs contra output E2E real, sin código). Si no se cumplen, **el patrón VERIFY embebido en RELEASE (AC-V1) es el sustituto declarado** y esta sección queda como constancia de por qué no activó. FASE-P1 cierra la decisión en este archivo; no se improvisa en RELEASE.

---

## Diagrama ASCII de dependencias

```
FASE-RELEASE-4.76.0 del predecesor ✅ cumplida 2026-09-11 (`3bdc14e`)   ← PRECONDICIÓN
        │
        ▼
FASE-P1 (decisión Q1–Q6 + contrato + cierre FASE-VERIFY + prompt de P2 si Q1=sí)
        │
        ├──────────────────────────────────────┐
        ▼                                      ▼
FASE-P2 (refactor ordenamiento,        FASE-P3-A (fixes de detección y fidelidad:
solo si Q1=sí; opción O1/O2/O3)        AC8 + tier acta + AC-F4)  ← siempre se ejecuta
        │                                      │
        └──────────┬───────────────────────────┘
                   ▼  (secuenciales entre sí: comparten judge.py/main.py y conteo NR1)
        FASE-P3-B (fixes de cableado y test: barreda D-V.1 + versión acta
                   + AC-F5 solo si Q5=a)
                   ▼
        FASE-P4 (corrida observación — T3a datos + T3b analítica;   ← OPCIONAL:
                 techo de tier según Q5: A o B_PLUS;                ver §Cierre válido sin P4
                 recomendada tras P3-A/P3-B para medir fidelidad
                 del acta ya corregida)
                   ▼
        FASE-VERIFY (solo si los 3 criterios §4.6 se cumplen al cerrar P1)
                   ▼
        FASE-RELEASE-4.77.0 (cierre + archivado R2.5)
```

**Variante si Q1=(c)** (decidir enforcement tras observar): P4 se adelanta antes de P2, con veredicto provisional documentado; P3-A/P3-B pueden ir antes de P4 (recomendado: el informe mide la fidelidad del acta ya corregida).

---

## Tabla de dependencias

| Fase | Depende de | Bloquea a | Tipo de dependencia |
|------|-----------|-----------|---------------------|
| FASE-P1 | RELEASE-4.76.0 del predecesor ✅ | P2, P3-A, P3-B, P4, RELEASE | Contrato (§15.4.1 heredada: lo decidido aquí obliga a P2/P3-A/P3-B) — incluye Q1b, Q5, Q6, cierre FASE-VERIFY y creación del prompt P2 si Q1=sí |
| FASE-P2 | P1 (Q1=sí + opción O1/O2/O3) | P4, RELEASE | El enforcement redefine dónde corren los revisores y quién decide el ZIP |
| FASE-P3-A | P1 (Q2b + contrato) | P3-B, P4 (recomendado), RELEASE | Fixes de detección/fidelidad sobre `judge.py` + `asset_reviewer.py`; independientes del enforcement |
| FASE-P3-B | P1 (Q5) + P3-A (baseline NR1 y `acta_writer.py`) | P4 (recomendado), RELEASE | Barreda test-only + versión del acta; **AC-F5 solo si Q5=a** (entonces toca `main.py`) |
| FASE-P4 | P1 (Q3/Q4/Q5) + **T3a datos operativos + T3b analítica** + P3-A/P3-B recomendado | RELEASE | Corrida de observación **opcional**: sin T3a no hay dato verificado y sin T3b (o Q5≠a) el techo es `B_PLUS`, no `A`; aplica §Cierre válido sin P4 |
| FASE-VERIFY | Criterios §4.6 cumplidos al cerrar P1 | RELEASE | Condicional (§4.6); si no activa, AC-V1 de RELEASE la sustituye como patrón declarado |
| FASE-RELEASE-4.77.0 | P2/P3-A/P3-B (si aplican) + **P4 ✅ o diferida por decisión registrada** + VERIFY si activó | — | Cierre documental |

---

## Conflictos potenciales de archivos

| Archivo | Fases que lo modifican | Riesgo | Mitigación |
|---------|------------------------|--------|------------|
| `main.py` | P2 (ordenamiento), P3-B (hoist de `ga4_available`/`gsc_available` hacia el bloque FASE-K si Q5=a) | Alto | Secuencial obligatorio: P2 y P3-B nunca en la misma sesión ni en paralelo |
| `modules/quality_gates/tribunal/judge.py` | P2 (consume `reviewer_reports`), P3-A (fuente del tier AC-F2; `FIRST_FLOOR_TIERS`/`_apply_first_floor_rule` AC-F4), P3-B (solo si Q6/AC-F4 lo reabre) | Alto | Secuencial obligatorio |
| `modules/quality_gates/tribunal/asset_reviewer.py` | P3-A (AC8: ZIP o heurístico) | Bajo | Solo P3-A |
| `modules/delivery/delivery_packager.py` | P2 si O1/O3 | Medio | Cambio de contrato → tests de packaging primero |
| `modules/quality_gates/tribunal/acta_writer.py` | P3-B (versión desde `VERSION.yaml`) | Bajo | Solo P3-B |
| `tests/quality_gates/tribunal/` | P2, P3-A, P3-B | Bajo | Archivos de test disjuntos por fase; ritual de cierre: `grep` de la clase en `__init__.py` (lección del predecesor, R2) |
| `test_barreda_un_solo_emisor_de_la_clave` | P3-B (whitelist test-only, D-V.1) | Bajo | Edición test-only; no tocar el emisor |
| Conteo NR1 (suma de tests) | P2, P3-A, P3-B en secuencia | Medio | Cada fase toma su snapshot `pre` con `--ignore` de sus propios tests (L-T4B.5) y resta R2.7; nunca dos fases miden el mismo baseline |

---

## Cierre válido sin P4 (fijado en la sesión de ajuste 2026-09-14)

P4 depende de dos precondiciones que pueden no cerrarse nunca: **T3a** (hotel con datos operativos y fuente) y **T3b** (GA4+GSC, y bajo Q5=a además código en `main.py`). El plan **no queda bloqueado** por su incumplimiento:

| Disparador | Mecánica (idéntica en los tres casos) |
|------------|----------------------------------------|
| Q5=(c) decidida en P1 | Ya especificado en el prompt P1: README pasa a 5 sesiones, `dependencias-fases.md` aplaza P4 con la decisión registrada |
| **T3a no se cierra** (Q4 sin proveedor de datos con fuente, ni aparece después) | P4 se difiere con la misma mecánica: decisión fechada en `evidence/FASE-P1/decision-enforcement.md` o en el `10-analisis` si surge tras P1, README a 5 sesiones, y RELEASE ejecuta con P4 diferida |
| T3b no se cierra pero T3a sí | **No** difiere P4: la corrida se especifica en `B_PLUS` con límite declarado (AC-O0). Diferir sería tirar el único dato real disponible |

**Consecuencias del diferimiento**: (i) FASE-VERIFY pierde el criterio 2 → no activa, AC-V1 la sustituye; (ii) la decisión de enforcement Q1=(c) queda prohibida en la práctica (no hay corrida que observe) — si P1 eligió (c) y T3a luego falla, la resolución por defecto es O4 documentada, registrada como decisión; (iii) el `10-analisis` declara el régimen Tier A como **no observado por este plan**, y el sucesor de analítica hereda P4 como fase propia. Lo que NO se permite: RELEASE con P4 "en espera", ni un `—` en su fila del checklist sin decisión registrada.

---

## Dependencias externas (fuera de alcance de código)

| Sub-fase | Precondición externa | Por qué |
|----------|---------------------|---------|
| **FASE-P4 — T3a** (datos operativos) | Hotel propio: `rooms`, `occupancy_rate`, `direct_channel_percentage`, `ADR` con fuente declarada (precondición T3 del ROADMAP) | Sin dato verificado, `_determine_evidence_tier` cae en `B`/`C` y el primer piso no se levanta. Su fallo **sí** difiere P4 (§Cierre válido sin P4) |
| **FASE-P4 — T3b** (analítica) — nueva, medida 2026-09-12 | GA4 **y** GSC disponibles, y el cableado que propague esa disponibilidad al `HotelFinancialData` del bloque FASE-K (decisión Q5) | `_determine_evidence_tier` devuelve `A` solo con `ga4_enabled and gsc_enabled and has_verified_data`, y `_compute_verdict` exige `A` para `APROBADO-PARA-ENTREGA`. Con solo T3a el techo es `B_PLUS`: el régimen que motiva el plan sigue sin observarse. Su fallo **no** difiere P4: AC-O0 |
| FASE-P4 (consentimiento) | El hotel/dueño acepta que la corrida use sus datos | Es una corrida de observación, no una entrega; igual requiere autorización |
| T5 / T6 (ROADMAP) | Credenciales FTP/WP + staging / escala | Fuera de alcance de este plan (igual que en el predecesor) |

**Consecuencia**: P1–P3-A/P3-B son ejecutables sin dato real. P4 queda condicionada a T3a **y** T3b — y T3b no es solo externa: una de sus tres opciones (Q5=a) es código en `main.py`. Si T3b no se cierra, P4 se corre en `B_PLUS` con el límite declarado (AC-O0); si T3a no se cierra, aplica §Cierre válido sin P4.

---

## Nota de rutas (post-R2.5 del predecesor)

El archivado (R2.5) de TRIBUNAL-OFFLINE-2026-09-09 **ya se ejecutó** el 2026-09-11 (`3bdc14e`) y movió sólo los documentos del plan: `10-analisis-post-implementacion.md`, `06-checklist-implementacion.md` y los `05-prompt-...` viven ahora en `Archives/TRIBUNAL-OFFLINE-2026-09-09/`. La **evidencia no se mueve**: `MATRIZ-CERTIFICACION.md` sigue en `evidence/FASE-VERIFY/TRIBUNAL-OFFLINE-2026-09-09/` y `decision-integracion.md` en `evidence/FASE-T1/` (ambos rastreados, verificado con `git ls-files`).

> **Higiene de cita (sesión de ajuste 2026-09-14)**: este archivo y los prompts del plan citaban `bd2bf57` como el commit del RELEASE. Es el duplicado pre-rebase: **no está en `origin/master`** y solo sobrevive en la rama local `backup/pre-sanidad-evidence-20260912`. El commit vivo es `3bdc14e`. Las citas históricas correctas (p. ej. "executor v2.21.0 introdujo R2.6/R2.7") se mantienen; lo que se corrigió son las afirmaciones en presente ("sin push ni tag") que el rebase y el tag `v4.76.0` (creado 2026-09-14, pendiente de push) dejaron obsoletas.

**Convención de rutas corregida (2026-09-12)**: lo que se escribe como plantilla `<PLAN>` son las **auto-referencias** a este plan — son las que `validate_opencode_refs.py --fix` reescribe a ciegas cuando ESTE plan se archive, y las que pueden destrozar un comando documentado. Las rutas ya archivadas del predecesor (`Archives/TRIBUNAL-OFFLINE-2026-09-09/…`) **sí** se citan completas: un directorio en `Archives/` no vuelve a moverse. El checklist de RELEASE exige revisar a mano el diff de `--fix` post-archivado.

---

## Punto de partición predefinido

Si FASE-P2 agota su presupuesto (55 iteraciones):
- **P2-part1**: contrato del veredicto enriquecido implementado en `judge.py` (`_compute_verdict` consume `reviewer_reports`) + tests
- **P2-part2**: reordenamiento del flujo (`main.py` / `delivery_packager.py`) según O1/O3

El cambio se registra en `10-analisis-post-implementacion.md` §Decisiones.
