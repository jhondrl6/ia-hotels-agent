# Dependencias entre Fases — TRIBUNAL-OFFLINE-2026-09-09

> **Regla**: FASE-RELEASE solo se ejecuta cuando TODAS las fases previas están ✅.
> **Orden T2**: T2-A, T2-B y T2-C son independientes en contenido (cualquier orden), pero **NUNCA simultáneas**: sesiones paralelas sobre el mismo working tree sobrescribieron evidencia en el plan anterior, y editan `__init__.py`/`main.py` + los docs compartidos del plan. T2-C **además** comparte `main.py` con T1 → secuencial tras T1, nunca en paralelo.

---

## Diagrama ASCII de dependencias

```
FASE-T1 (Juez + contrato de acta)
    │
    ├──→ FASE-T2-A (Bot 1: Diagnóstico)  ──┐
    │                                       │
    ├──→ FASE-T2-B (Bot 3: Assets)  ───────┤
    │                                       │
    └──→ FASE-T2-C (S-E2, S9)  ────────────┤
                                            │
                                            ▼
                                    FASE-T4-A (Bot 2: Alineación NL + interfaz LLM)
                                            │
                                            ▼
                                    FASE-T4-B (Bot 4: Honestidad NL)
                                            │
                                            ▼
                                    FASE-E2E (v4complete Salento Real)
                                            │
                                            ▼
                                    FASE-VERIFY (certificación ACs)
                                            │
                                            ▼
                                    FASE-RELEASE-4.76.0 (cierre + archivado)
```

---

## Tabla de dependencias

| Fase | Depende de | Bloquea a | Tipo de dependencia |
|------|-----------|-----------|---------------------|
| FASE-T1 ⚠️ | — (baseline v4.75.0) | T2-A, T2-B, T2-C, T4-A, **T4-B** | Contrato de acta (T1 define el I/O que T2/T4 consumen). **Vincula a T4-B**: D-T1.3 ✅ resuelta (opción a) — primer piso → `first_floor_rule`, `P6.5` liberada para Bot 4; implementación en auditoría T1 previa a T4-B. Veredictos negativos bloquean ZIP por `blocks_delivery_zip` (D-T1.1) y sin evidencia certificable no hay `APROBADO-PARA-ENTREGA` (D-T1.2) — ver `10-analisis` §Decisiones de contrato |
| FASE-T2-A ✅ | T1 ⚠️ | T4-A | Acta contract estable + `revision_diagnostico.json` schema |
| FASE-T2-B ✅ | T1 ⚠️ | T4-A | Acta contract estable + `revision_assets.json` schema |
| FASE-T2-C ⚠️ | T1 ⚠️ | E2E | Toca `main.py` (secuencial tras T1, nunca paralela); precondición S-E2 del régimen `generate_proposal=False`. ⚠️ Desvío D-T2C-A1: los bloques `presence_lookup` fueron reactivados (no retirados) y cambian la propuesta en régimen `True` — E2E debe validar la veracidad de «Presente en sitio» |
| FASE-T4-A ✅ | T1 ⚠️, T2-A ✅, T2-B ✅ | T4-B | Interfaz de extracción LLM (patrón que T4-B replica) |
| FASE-T4-B ⚠️ | T4-A ✅ | E2E | Todos los revisores **implementados** (≠ cableados). ⚠️ Desvío D-T4B-A1 (auditoría 2026-09-11): el revisor no resolvía la propuesta donde el pipeline la escribe, así que no operaba sobre artefactos reales — remediado R1–R9. El contrato de "añade imports" en `__init__.py` se cumplió en la remediación (R2) |
| FASE-E2E | T1-T4-B (T1/T2-C/T4-B ⚠️), T2-A/T2-B/T4-A ✅ | VERIFY | Pipeline completo con tribunal integrado + residuos heredados curados. **Dueña del cableado de los 4 revisores en `main.py`** (decisión Q1, Vía A): hoy solo corre el Juez, ningún `revision_*.json` existe en `output/` y `P6.5` queda `NOT_EVALUABLE`. Consume también el desvío D-T2C-A1: validar veracidad de «Presente en sitio» en la propuesta |
| FASE-VERIFY | E2E ✅ | RELEASE | ACs certificados contra output real |
| FASE-RELEASE-4.76.0 | VERIFY ✅ | — | Cierre documental |

---

## Conflictos potenciales de archivos

| Archivo | Fases que lo modifican | Riesgo | Mitigación |
|---------|----------------------|--------|------------|
| `main.py` | T1 (integración del Juez), T2-C (S-E2) | **Secuencial obligatorio**: T2-C re-verifica con `grep`/`Read` antes de editar; T1 va primero | Dependencia declarada: T2-C depende de T1 ⚠️; nunca en paralelo |
| `modules/quality_gates/tribunal/__init__.py` | T1 (crea), T2-A/T2-B/T4-A/T4-B (añaden imports) | Bajo: cada fase añade su clase | T1 crea el `__init__` con estructura extensible. ⚠️ **Auditado 2026-09-11**: T4-B no añadió la suya (`HonestyReviewer` quedó fuera del paquete y sin consumidor); cerrado en la remediación R2. Un `grep` de la clase en `__init__.py` debería añadirse al ritual de cierre de fase |
| `tests/quality_gates/tribunal/` | T1, T2-A, T2-B, T2-C, T4-A, T4-B | Bajo: archivos de test disjuntos | Cada fase crea su propio `test_*.py` |
| `09-documentacion-post-proyecto.md` | Todas | Acumulativo, no conflictivo | Cada fase añade su fila |
| `10-analisis-post-implementacion.md` | Todas | Acumulativo | Cada fase añade lecciones |
| **Claves de cláusula en `acta_revision.json`** | T1 (`P6.1`-`P6.4`, `P6.6` + `first_floor_rule`), T2-A (`P6.1`), T2-B (`P6.3`/`P6.4`), T4-A (`P6.2`), T4-B (`P6.5`) | ✅ **Resuelto (D-T1.3 opción a)**: primer piso → `first_floor_rule` (top-level), `P6.5` liberada para Bot 4. Cada revisor declara su `clause` sin pisar slots | T1 ajusta `_evaluate_p6_5` → `_apply_first_floor_rule` en auditoría previa a T4-B |

---

## Dependencias externas (tramo fuera de alcance)

| Sub-fase ROADMAP | Precondición externa | Por qué no está en este plan |
|------------------|---------------------|------------------------------|
| **T3** (Onboarding) | Datos operativos reales de un hotel (rooms, occupancy, direct_channel_pct, ADR) | Ninguna corrida sobre URL pública produce `evidence_tier: A` |
| **T5** (Deploy) | Credenciales FTP/WP-API reales + sitio de staging + deuda P1 cerrada | Sin deploy real no existe `site_verification_applied: true` |
| **T6** (Throughput) | T3 y T5 en PASS + lista de URLs propias + margen de costo verificado | Es escala sobre los dos anteriores |

**Consecuencia**: el DoD-técnico (tramo offline) es certificable al cierre de este plan. El DoD-comercial requiere T3+T5 (tramo externo).

---

## Punto de partición predefinido

Si FASE-T1 agota su presupuesto (55 iteraciones):
- **T1-part1**: Research + contrato de acta + `judge.py` sin integración en `main.py`
- **T1-part2**: Integración en `main.py` + tests retro + serialización

Si FASE-T4-A agota su presupuesto (50 iteraciones):
- **T4-A-part1**: Interfaz `llm_extractor.py` + mock
- **T4-A-part2**: `alignment_reviewer.py` + tests

El cambio se registra en `10-analisis-post-implementacion.md` §Decisiones.
