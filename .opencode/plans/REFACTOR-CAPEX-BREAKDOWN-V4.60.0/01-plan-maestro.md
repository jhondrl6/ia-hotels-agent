# Plan Maestro: REFACTOR-CAPEX-BREAKDOWN v4.60.0

## Origen
Contexto: `PENDIENTE-IMP-03-CAPEX-BREAKDOWN.md` (auditoría forense con 100% confianza verificada contra código vivo)
Versión base: v4.59.0
Versión objetivo: v4.60.0
Fecha de creación: 2026-05-29

---

## Resumen Ejecutivo

Refactorización de 4 findings (F1, F6, F7, F8) identificados en la auditoría del fix IMP-03 CAPEX Breakdown. El bug principal (F1) produce output corrupto al anidar una tabla markdown dentro de una celda de otra tabla markdown. Los findings secundarios son código muerto y un placeholder invisible.

---

## Findings y Soluciones

| ID | Finding | Severidad | Solución | Archivo(s) |
|----|---------|-----------|----------|------------|
| F1 | Tabla CAPEX corrupta: `${capex_breakdown_table}` embebido en celda de tabla 4-col | ALTA | Opción A: Mover placeholder a sección propia | `propuesta_v6_template.md` L152 |
| F6 | Coherence Checklist invisible: placeholder `${coherence_checklist}` no existe en templates + hardcoded `eje_cafetero` L1895 | BAJA | Eliminar método (YAGNI) o integrar al template | `v4_proposal_generator.py` L943, L1878-1927, L1895 |
| F7 | 9 keys huérfanas en dict de template data | BAJA | Eliminar keys del dict | `v4_proposal_generator.py` L791,805,905-908,938-940 |
| F8 | Fallback de `_build_capex_breakdown_table()` sin header | BAJA | Agregar header al fallback | `v4_proposal_generator.py` L201-203 |

---

## Matriz de Dependencias

```
FASE-1 (F1: template)  ──────────────────┐
                                          │
FASE-2 (F7+F8: generator) ───────────────┤  (independiente de FASE-1)
                                          │
FASE-3 (F6: coherence) ──────────────────┤  (independiente de FASE-1 y FASE-2)
                                          │
FASE-4 (v4complete + verificación) ──────┤  (DEPENDIENTE de FASE-1, FASE-2, FASE-3)
                                          │
FASE-RELEASE v4.60.0 ────────────────────┘  (DEPENDIENTE de FASE-4)
```

**Conflictos de archivos:**
- `propuesta_v6_template.md`: FASE-1 (fix F1) y FASE-3 (si se integra coherence_checklist)
  - Resolución: FASE-3 evalúa si integrar o eliminar. Si elimina, no hay conflicto.
- `v4_proposal_generator.py`: FASE-2 (F7+F8) y FASE-3 (F6)
  - Resolución: FASE-2 primero (edits en L791-940), FASE-3 después (edits en L943, L1878-1927).

---

## Estructura de Fases

| Fase | Findings | Tareas | delegate_task | Complejidad | Sesión |
|------|----------|--------|---------------|-------------|--------|
| **FASE-1** | F1 | 3: fix template + test integridad pipes + run tests | No (código puro, directo) | ⭐⭐⭐ **MAYOR** | Nueva |
| **FASE-2** | F7 + F8 | 3: cleanup keys (+F7) + fix fallback (F8) + run tests | ✅ Sí (2 tracks paralelos) | ⭐⭐ | Nueva |
| **FASE-3** | F6 | 3: decisión YAGNI vs integrar + fix hardcoded + run tests | No (decisión + simple fix) | ⭐⭐ | Nueva |
| **FASE-4** | Verificación | 2: v4complete + análisis post-imp | ✅ Sí (v4complete como subagente) | ⭐⭐ | Nueva |
| **FASE-RELEASE** | — | Docs cascade, version bump, sync | No | ⭐ | Nueva |

**Total: 5 fases + 1 release = 6 sesiones**

---

## Fase de Mayor Complejidad Técnica

### ⭐⭐⭐ FASE-1: F1 — Template CAPEX Fix

**Razones:**
1. **Edición markdown delicada**: Eliminar 1 línea de tabla (L152) e insertar 2 líneas de sección + placeholder en posición correcta
2. **Verificación de integridad**: Cada fila de la tabla CAPEX debe tener exactamente 4 pipes; la sección de desglose debe tener exactamente 3 pipes
3. **Test nuevo**: Agregar test que verifique estructura de tabla CAPEX renderizada (ningún test actual verifica esto — es la debilidad que permitió la regresión)
4. **Riesgo de regresión**: Un error en la plantilla puede romper el rendering de toda la sección de inversión

**Por qué NO usar delegate_task:**
- Código puro en archivos de template + tests
- Overhead de spawn > beneficio para 3 tareas secuenciales
- Budget directo: ~30-40 iters (fix + test + verificación), bien dentro del límite de 60

---

## Fases con delegate_task

### FASE-2: 2 tracks paralelos
- **Track A**: Eliminar 9 keys huérfanas (F7) — `v4_proposal_generator.py` L791-940
- **Track B**: Agregar header al fallback (F8) — `v4_proposal_generator.py` L201-203
- Ambos tracks editan el mismo archivo pero en secciones no superpuestas
- **Estrategia**: Subagente para Track A, agente principal para Track B + merge

### FASE-4: v4complete como subagente
- Subagente ejecuta `v4complete` para Hotel Castilla Real (5-10 min wall clock)
- Agente principal verifica output, análisis post-implementación, docs cascade
- **Protocolo de evidencia proactiva obligatorio**

---

## Métricas de Éxito (Post-Fix)

1. ✅ Tabla CAPEX principal: cada fila exactamente 4 pipes (4 celdas)
2. ✅ Desglose en sección independiente: `### Desglose del Setup Fee (CAPEX)` con tabla de 3 pipes
3. ✅ Coherence score ≥ 0.80
4. ✅ 11/11 gates PASS (o ≥ baseline de 9/11 + sin nuevas regresiones)
5. ✅ Tests existentes CAPEX pasan sin cambios
6. ✅ Nuevo test de integridad de pipes pasa
7. ✅ Sin keys huérfanas en template data
8. ✅ Fallback con header row

---

## Archivos Involucrados

| Archivo | Fases | Cambios |
|---------|-------|---------|
| `modules/commercial_documents/templates/propuesta_v6_template.md` | 1, 3 (condicional) | Fix tablas anidadas; posible integración coherence_checklist |
| `modules/commercial_documents/v4_proposal_generator.py` | 2, 3 | Eliminar keys huérfanas; fix fallback; decisión coherence_checklist |
| `tests/test_capex_rename.py` | 1 | Nuevo test de integridad de pipes |
| `config/commercial.yaml` | — | Sin cambios |
| `VERSION.yaml` | RELEASE | Bump a 4.60.0 |

---

## Reglas de Ejecución

- **R1**: 1 fase por sesión
- **R2**: Max 60 iteraciones por fase
- **R3**: Max 4 tareas o 3+1 comando largo por fase
- Cada fase ejecuta `log_phase_completion.py` al completar
- FASE-RELEASE NO registra fases anteriores (solo sync)
- Protocolo de evidencia proactiva obligatorio post-v4complete
