# ROICRIII — Dependencias de Fases

**Proyecto:** Financial Coherence & Asset Semantics Rescue
**Versión target:** 4.57.0 (desde 4.56.0)
**Contexto:** .opencode/context/ROICRIII.md
**Score cumplimiento actual:** 44% → target 96%
**Fecha creación:** 2026-05-28

---

## Diagrama de Dependencias

```
FASE-1 (Motor Financiero: A1+A2+A3)
    │
    ├──→ FASE-2 (Pain Ratio + Trazabilidad: A4+A5)
    │        │
    │        └──→ FASE-3 (Validator + BREACH + WhatsApp: B1+B2+B6)
    │                 │
    │                 └──→ FASE-4 (Assets Deprecados: B3+B4+B5+F5)
    │                          │
    │                          └──→ FASE-5 (Features: C1+C2+C3)
    │                                   │
    │                                   └──→ FASE-6 (v4complete Hotel Castilla Real)
    │                                            │
    └─────────────────────────────────────────────┴──→ FASE-RELEASE-4.57.0
```

**Regla:** Todas las fases son secuenciales. Cada fase depende de la anterior.

---

## Tabla de Conflictos de Archivos

| Archivo | FASE-1 | FASE-2 | FASE-3 | FASE-4 | FASE-5 |
|---------|--------|--------|--------|--------|--------|
| `v4_proposal_generator.py` (_prepare_template_data) | ✅ A1,A2,A3 | ✅ A4,A5 | — | — | — |
| `v4_proposal_generator.py` (_generate_dynamic_services_table) | — | — | ✅ B1,B2,B6 | — | — |
| `v4_proposal_generator.py` (_build_activos_digitales_lista) | — | — | — | ✅ B3,B5 | — |
| `v4_proposal_generator.py` (nuevo método _build_pilot_section) | — | — | — | — | ✅ C1 |
| `v4_proposal_generator.py` (data dict + garantía) | — | — | — | — | ✅ C2,C3 |
| `propuesta_v6_template.md` | ✅ A3 | — | — | — | ✅ C1,C2,C3 |
| `service_catalog.py` (TECHNICAL_ASSET_CATALOG) | — | — | — | ✅ B4 | — |
| `config/commercial.yaml` | — | — | — | — | ✅ C1 |

**Riesgo:** `v4_proposal_generator.py` es modificado en TODAS las fases (excepto FASE-4 parcialmente). La ejecución estrictamente secuencial es OBLIGATORIA.

---

## Estado de Fases

| Fase | Estado | Fecha | Notas |
|------|--------|-------|-------|
| FASE-1 (Motor Financiero) | ✅ Completada | 2026-05-28 | Código ya unificado; 6/6 tests nuevos pasan; smoke OK |
| FASE-2 (Pain Ratio + Trazabilidad) | ⏳ Pendiente | — | Depende de FASE-1 |
| FASE-3 (Validator + BREACH + WhatsApp) | ✅ Completada | 2026-05-28 | Código + tests + docs cascade |
| FASE-4 (Assets Deprecados: B3+B4+B5+F5) | ✅ Completada | 2026-05-28 | DEPRECATED_ASSETS en generator + removed from TECHNICAL_ASSET_CATALOG + test |
| FASE-5 (Features) | ✅ Completada | 2026-05-28 | Piloto 30 días + CAPEX breakdown + Garantía KPI (C1+C2+C3); 3 tests nuevos pasan |
| FASE-6 (v4complete) | ⏳ Pendiente | — | delegate_task + verificación |
| FASE-RELEASE-4.57.0 | ⏳ Pendiente | — | Documentación oficial |

---

## Matriz de Complejidad

| Fase | Complejidad Técnica | Riesgo | delegate_task | Iteraciones estimadas |
|------|-------------------|--------|---------------|----------------------|
| FASE-1 | 🔴 ALTA | Unificar 2 motores en método de 700+ L | No (código+tests directo) | ~45-55 |
| FASE-2 | 🟡 MEDIA | Corregir texto dinámico en data dict | No | ~30-40 |
| FASE-3 | 🟡 MEDIA | Integrar validator existente en nuevo scope | No | ~35-45 |
| FASE-4 | 🟡 MEDIA | Filtrar assets en 2 archivos | No | ~30-40 |
| FASE-5 | 🟡 MEDIA | Nuevos métodos + config + template | Posible (parallel tracks) | ~40-50 |
| FASE-6 | 🟡 MEDIA | v4complete + verificar 5 niveles | ✅ Sí (subagente) | ~25-35 parent |
| RELEASE | 🟢 BAJA | Docs only, no code changes | No | ~30-40 |
