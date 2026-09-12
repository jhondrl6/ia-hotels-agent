# Dependencias entre Fases — TRIBUNAL-ENFORCEMENT-OBS-2026-09-11

> **Regla**: FASE-RELEASE solo se ejecuta cuando TODAS las fases previas están ✅.
> **Regla heredada**: nunca sesiones paralelas sobre el mismo working tree (el plan predecesor documentó sobrescritura de evidencia). P2 y P3 comparten `judge.py`/`main.py` → **secuenciales entre sí, nunca simultáneas**.

---

## Diagrama ASCII de dependencias

```
FASE-RELEASE-4.76.0 del predecesor ✅ cumplida 2026-09-11 (`bd2bf57`)   ← PRECONDICIÓN
        │
        ▼
FASE-P1 (decisión Q1–Q4 + contrato del veredicto enriquecido)
        │
        ├──────────────────────────────┐
        ▼                              ▼
FASE-P2 (refactor ordenamiento,   FASE-P3 (fixes: AC8 + tier acta +
solo si Q1=sí; opción O1/O2/O3)   barreda D-V.1 + versión acta)
        │                              │
        └──────────┬───────────────────┘
                   ▼  (secuenciales entre sí: comparten judge.py/main.py)
        FASE-P4 (corrida observación — T3a datos + T3b analítica;
                 techo de tier según Q5: A o B_PLUS;
                 recomendada tras P3 para medir fidelidad del acta ya corregida)
                   ▼
        FASE-RELEASE-4.77.0 (cierre + archivado R2.5)
```

**Variante si Q1=(c)** (decidir enforcement tras observar): P4 se adelanta antes de P2, con veredicto provisional documentado; P3 puede ir antes de P4 (recomendado: el informe mide la fidelidad del acta ya corregida).

---

## Tabla de dependencias

| Fase | Depende de | Bloquea a | Tipo de dependencia |
|------|-----------|-----------|---------------------|
| FASE-P1 | RELEASE-4.76.0 del predecesor ✅ | P2, P3, P4 | Contrato (§15.4.1 heredada: lo decidido aquí obliga a P2/P3) — incluye Q1b, Q5 y Q6 |
| FASE-P2 | P1 (Q1=sí + opción O1/O2/O3) | P4, RELEASE | El enforcement redefine dónde corren los revisores y quién decide el ZIP |
| FASE-P3 | P1 (Q2b, Q5) | P4 (recomendado), RELEASE | Fixes localizados independientes del enforcement, pero tocan `judge.py`; si Q5=(a) toca también `main.py` |
| FASE-P4 | P1 (Q3/Q4/Q5) + **T3a datos operativos + T3b analítica** + P3 recomendado | RELEASE | Corrida de observación; sin T3a no hay dato verificado y sin T3b (o Q5=a) el techo es `B_PLUS`, no `A` |
| FASE-RELEASE-4.77.0 | P2/P3 (si aplican) + P4 ✅ | — | Cierre documental |

---

## Conflictos potenciales de archivos

| Archivo | Fases que lo modifican | Riesgo | Mitigación |
|---------|------------------------|--------|------------|
| `main.py` | P2 (ordenamiento), P3 (hoist de `ga4_available`/`gsc_available` hacia el bloque FASE-K si Q5=a) | Alto | Secuencial obligatorio: P2 y P3 nunca en la misma sesión ni en paralelo |
| `modules/quality_gates/tribunal/judge.py` | P2 (consume `reviewer_reports`), P3 (fuente del tier; `FIRST_FLOOR_TIERS`/`_apply_first_floor_rule` si Q6 o AC-F4 lo requieren) | Alto | Mismo mitigation: secuencial |
| `modules/quality_gates/tribunal/asset_reviewer.py` | P3 (AC8: ZIP o heurístico) | Bajo | Solo P3 |
| `modules/delivery/delivery_packager.py` | P2 si O1/O3 | Medio | Cambio de contrato → tests de packaging primero |
| `modules/quality_gates/tribunal/acta_writer.py` | P3 (versión desde `VERSION.yaml`) | Bajo | Solo P3 |
| `tests/quality_gates/tribunal/` | P2, P3 | Bajo | Archivos de test disjuntos; ritual de cierre: `grep` de la clase en `__init__.py` (lección del predecesor, R2) |
| `test_barreda_un_solo_emisor_de_la_clave` | P3 (whitelist test-only, D-V.1) | Bajo | Edición test-only; no tocar el emisor |

---

## Dependencias externas (fuera de alcance de código)

| Sub-fase | Precondición externa | Por qué |
|----------|---------------------|---------|
| **FASE-P4 — T3a** (datos operativos) | Hotel propio: `rooms`, `occupancy_rate`, `direct_channel_percentage`, `ADR` con fuente declarada (precondición T3 del ROADMAP) | Sin dato verificado, `_determine_evidence_tier` cae en `B`/`C` y el primer piso no se levanta |
| **FASE-P4 — T3b** (analítica) — nueva, medida 2026-09-12 | GA4 **y** GSC disponibles, y el cableado que propague esa disponibilidad al `HotelFinancialData` del bloque FASE-K (decisión Q5) | `_determine_evidence_tier` devuelve `A` solo con `ga4_enabled and gsc_enabled and has_verified_data`, y `_compute_verdict` exige `A` para `APROBADO-PARA-ENTREGA`. Con solo T3a el techo es `B_PLUS`: el régimen que motiva el plan sigue sin observarse |
| FASE-P4 (consentimiento) | El hotel/dueño acepta que la corrida use sus datos | Es una corrida de observación, no una entrega; igual requiere autorización |
| T5 / T6 (ROADMAP) | Credenciales FTP/WP + staging / escala | Fuera de alcance de este plan (igual que en el predecesor) |

**Consecuencia**: P1–P3 son ejecutables sin dato real. P4 queda condicionada a T3a **y** T3b — y T3b no es solo externa: una de sus tres opciones (Q5=a) es código en `main.py`. Si ninguna vía T3b se cierra en este plan, P4 se especifica como corrida en `B_PLUS` con el límite declarado (AC-O0), no como corrida Tier A.

---

## Nota de rutas (post-R2.5 del predecesor)

El archivado (R2.5) de TRIBUNAL-OFFLINE-2026-09-09 **ya se ejecutó** el 2026-09-11 (`bd2bf57`) y movió sólo los documentos del plan: `10-analisis-post-implementacion.md`, `06-checklist-implementacion.md` y los `05-prompt-...` viven ahora en `Archives/TRIBUNAL-OFFLINE-2026-09-09/`. La **evidencia no se mueve**: `MATRIZ-CERTIFICACION.md` sigue en `evidence/FASE-VERIFY/TRIBUNAL-OFFLINE-2026-09-09/` y `decision-integracion.md` en `evidence/FASE-T1/` (ambos rastreados, verificado con `git ls-files`).

**Convención de rutas corregida (2026-09-12)**: lo que se escribe como plantilla `<PLAN>` son las **auto-referencias** a este plan — son las que `validate_opencode_refs.py --fix` reescribe a ciegas cuando ESTE plan se archive, y las que pueden destrozar un comando documentado. Las rutas ya archivadas del predecesor (`Archives/TRIBUNAL-OFFLINE-2026-09-09/…`) **sí** se citan completas: un directorio en `Archives/` no vuelve a moverse. El checklist de RELEASE exige revisar a mano el diff de `--fix` post-archivado.

---

## Punto de partición predefinido

Si FASE-P2 agota su presupuesto (55 iteraciones):
- **P2-part1**: contrato del veredicto enriquecido implementado en `judge.py` (`_compute_verdict` consume `reviewer_reports`) + tests
- **P2-part2**: reordenamiento del flujo (`main.py` / `delivery_packager.py`) según O1/O3

El cambio se registra en `10-analisis-post-implementacion.md` §Decisiones.
