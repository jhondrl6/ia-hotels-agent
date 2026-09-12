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
        FASE-P4 (corrida observación Tier A — requiere datos reales T3;
                 recomendada tras P3 para medir fidelidad del acta ya corregida)
                   ▼
        FASE-RELEASE-4.77.0 (cierre + archivado R2.5)
```

**Variante si Q1=(c)** (decidir enforcement tras observar): P4 se adelanta antes de P2, con veredicto provisional documentado; P3 puede ir antes de P4 (recomendado: el informe mide la fidelidad del acta ya corregida).

---

## Tabla de dependencias

| Fase | Depende de | Bloquea a | Tipo de dependencia |
|------|-----------|-----------|---------------------|
| FASE-P1 | RELEASE-4.76.0 del predecesor ✅ | P2, P3, P4 | Contrato (§15.4.1 heredada: lo decidido aquí obliga a P2/P3) |
| FASE-P2 | P1 (Q1=sí + opción O1/O2/O3) | P4, RELEASE | El enforcement redefine dónde corren los revisores y quién decide el ZIP |
| FASE-P3 | P1 (Q2b) | P4 (recomendado), RELEASE | Fixes localizados independientes del enforcement, pero tocan `judge.py` |
| FASE-P4 | P1 (Q3/Q4) + **datos reales (T3)** + P3 recomendado | RELEASE | Corrida de observación; sin dato real no hay `evidence_tier: A` ni primer piso levantado |
| FASE-RELEASE-4.77.0 | P2/P3 (si aplican) + P4 ✅ | — | Cierre documental |

---

## Conflictos potenciales de archivos

| Archivo | Fases que lo modifican | Riesgo | Mitigación |
|---------|------------------------|--------|------------|
| `main.py` | P2 (ordenamiento), P3 (posible hoist) | Alto | Secuencial obligatorio: P2 y P3 nunca en la misma sesión ni en paralelo |
| `modules/quality_gates/tribunal/judge.py` | P2 (consume `reviewer_reports`), P3 (fuente del tier) | Alto | Mismo mitigation: secuencial |
| `modules/quality_gates/tribunal/asset_reviewer.py` | P3 (AC8: ZIP o heurístico) | Bajo | Solo P3 |
| `modules/delivery/delivery_packager.py` | P2 si O1/O3 | Medio | Cambio de contrato → tests de packaging primero |
| `modules/quality_gates/tribunal/acta_writer.py` | P3 (versión desde `VERSION.yaml`) | Bajo | Solo P3 |
| `tests/quality_gates/tribunal/` | P2, P3 | Bajo | Archivos de test disjuntos; ritual de cierre: `grep` de la clase en `__init__.py` (lección del predecesor, R2) |
| `test_barreda_un_solo_emisor_de_la_clave` | P3 (whitelist test-only, D-V.1) | Bajo | Edición test-only; no tocar el emisor |

---

## Dependencias externas (fuera de alcance de código)

| Sub-fase | Precondición externa | Por qué |
|----------|---------------------|---------|
| **FASE-P4** (corrida observación) | Datos operativos reales de un hotel propio: `rooms`, `occupancy_rate`, `direct_channel_percentage`, `ADR` con fuente declarada (precondición T3 del ROADMAP) | Sin dato real, `evidence_tier` no alcanza `A`, el primer piso no se levanta y `APROBADO-PARA-ENTREGA` sigue inalcanzable — la corrida no ejercitaría el régimen objetivo |
| FASE-P4 (consentimiento) | El hotel/dueño acepta que la corrida use sus datos | Es una corrida de observación, no una entrega; igual requiere autorización |
| T5 / T6 (ROADMAP) | Credenciales FTP/WP + staging / escala | Fuera de alcance de este plan (igual que en el predecesor) |

**Consecuencia**: P1–P3 son ejecutables sin dato real; P4 queda condicionada a que el usuario provea el hotel y sus datos.

---

## Nota de rutas (post-R2.5 del predecesor)

El archivado (R2.5) de TRIBUNAL-OFFLINE-2026-09-09 **ya se ejecutó** el 2026-09-11 (`bd2bf57`) y movió sólo los documentos del plan: `10-analisis-post-implementacion.md`, `06-checklist-implementacion.md` y los `05-prompt-...` viven ahora en `Archives/TRIBUNAL-OFFLINE-2026-09-09/`. La **evidencia no se mueve**: `MATRIZ-CERTIFICACION.md` sigue en `evidence/FASE-VERIFY/TRIBUNAL-OFFLINE-2026-09-09/` y `decision-integracion.md` en `evidence/FASE-T1/` (ambos rastreados, verificado con `git ls-files`). Este plan cita los documentos del predecesor por **nombre de archivo**, nunca por ruta completa — resolver al cargar.

---

## Punto de partición predefinido

Si FASE-P2 agota su presupuesto (55 iteraciones):
- **P2-part1**: contrato del veredicto enriquecido implementado en `judge.py` (`_compute_verdict` consume `reviewer_reports`) + tests
- **P2-part2**: reordenamiento del flujo (`main.py` / `delivery_packager.py`) según O1/O3

El cambio se registra en `10-analisis-post-implementacion.md` §Decisiones.
