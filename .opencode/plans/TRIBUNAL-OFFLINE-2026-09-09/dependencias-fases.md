# Dependencias entre Fases — TRIBUNAL-OFFLINE-2026-09-09

> **Regla**: FASE-RELEASE solo se ejecuta cuando TODAS las fases previas están ✅.
> **Orden T2**: T2-A y T2-B son independientes en contenido (cualquier orden), pero **NUNCA simultáneas**: sesiones paralelas sobre el mismo working tree sobrescribieron evidencia en el plan anterior, y ambas editan `__init__.py` + los docs compartidos del plan.

---

## Diagrama ASCII de dependencias

```
FASE-T1 (Juez + contrato de acta)
    │
    ├──→ FASE-T2-A (Bot 1: Diagnóstico)  ──┐
    │                                       │
    └──→ FASE-T2-B (Bot 3: Assets)  ───────┤
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
| FASE-T1 | — (baseline v4.75.0) | T2-A, T2-B, T4-A | Contrato de acta (T1 define el I/O que T2/T4 consumen) |
| FASE-T2-A | T1 ✅ | T4-A | Acta contract estable + `revision_diagnostico.json` schema |
| FASE-T2-B | T1 ✅ | T4-A | Acta contract estable + `revision_assets.json` schema |
| FASE-T4-A | T1 ✅, T2-A ✅, T2-B ✅ | T4-B | Interfaz de extracción LLM (patrón que T4-B replica) |
| FASE-T4-B | T4-A ✅ | E2E | Todos los revisores implementados |
| FASE-E2E | T1-T4-B ✅ | VERIFY | Pipeline completo con tribunal integrado |
| FASE-VERIFY | E2E ✅ | RELEASE | ACs certificados contra output real |
| FASE-RELEASE-4.76.0 | VERIFY ✅ | — | Cierre documental |

---

## Conflictos potenciales de archivos

| Archivo | Fases que lo modifican | Riesgo | Mitigación |
|---------|----------------------|--------|------------|
| `main.py` | T1 (integración del Juez) | T1 es la única fase que toca `main.py` | Sin conflicto: una sola fase |
| `modules/quality_gates/tribunal/__init__.py` | T1 (crea), T2-A/T2-B/T4-A/T4-B (añaden imports) | Bajo: cada fase añade su clase | T1 crea el `__init__` con estructura extensible |
| `tests/quality_gates/tribunal/` | T1, T2-A, T2-B, T4-A, T4-B | Bajo: archivos de test disjuntos | Cada fase crea su propio `test_*.py` |
| `09-documentacion-post-proyecto.md` | Todas | Acumulativo, no conflictivo | Cada fase añade su fila |
| `10-analisis-post-implementacion.md` | Todas | Acumulativo | Cada fase añade lecciones |

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
