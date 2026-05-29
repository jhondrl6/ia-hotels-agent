# Documentación Post-Proyecto — REFACTOR-PENDIENTE-V4.58.0

## Propósito

Registro de documentación incremental para la refactorización de 5 gaps de propuesta
comercial + 2 bugs + 1 deuda técnica. Verificado con v4complete en Hotel Castilla Real.

---

## Sección A: Módulos Nuevos

Ninguno. Este plan no crea módulos nuevos, solo funciones helper nuevas:

| Función | Módulo | Propósito |
|---------|--------|-----------|
| `_build_status_quo_table()` | `v4_proposal_generator.py` | Tabla Sin IAO vs Con IAO |
| `_build_closing_pitch()` | `v4_proposal_generator.py` | Pitch dinámico basado en ROICR |
| `_get_adr_from_benchmarks()` | `v4_proposal_generator.py` | Leer ADR de benchmarks YAML |

---

## Sección B: Módulos Modificados

| Módulo | Cambio |
|--------|--------|
| `modules/commercial_documents/v4_proposal_generator.py` | 3 métodos nuevos + data dict + dead code eliminado |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | 4 placeholders nuevos + sección Status Quo + Closing |
| `modules/quality_gates/publication_gates.py` | `financial_validity` usa `evidence_tier` formal |
| `config/regional_benchmarks.yaml` | ADR añadido a todas las regiones |

---

## Sección C: Cambios Arquitecturales

Ninguno. Los cambios son de tipo:
- **Template fix**: añadir placeholders consumidos
- **Pipeline extension**: nuevos métodos que alimentan el template
- **Data enrichment**: YAML config con nuevos campos
- **Gate correction**: lógica consistente entre gates

No se modifican interfaces públicas ni contratos entre módulos.

---

## Sección D: Métricas Acumulativas

| Métrica | Valor |
|---------|-------|
| Archivos modificados | 4 |
| Funciones nuevas | 3 |
| Placeholders nuevos en template | 4 |
| Líneas de código añadidas | ~80 |
| Líneas de código eliminadas | ~30 (dead code) |
| Tests nuevos/modificados | 0 (regresión existente) |
| Fases ejecutadas | 10 |
| Hotel de verificación | Hotel Castilla Real |
| Baseline coherence | 0.83 |
| Post-fix coherence | 0.85 |
| Baseline gates | 9/11 |
| Post-fix gates | 11/11 |

---

## Sección E: Archivos Afiliados Actualizados

Post-ejecución del RELEASE:

- [ ] `docs/contributing/REGISTRY.md` — entrada de fase registrada
- [ ] `CHANGELOG.md` — entrada MINOR con cambios completos
- [ ] `docs/GUIA_TECNICA.md` — nota técnica agregada
- [ ] `VERSION.yaml` — versión incrementada
- [ ] `AGENTS.md` — sincronizado (last_update)
- [ ] `README.md` — sincronizado
- [ ] `.cursorrules` — sincronizado
- [ ] `CONTRIBUTING.md` — sincronizado
- [ ] `evidence/FASE-PENDIENTE-V4COMPLETE/` — evidencia E2E guardada

---

## Sección F: Lecciones Aprendidas

### Técnicas

| # | Lección | Aplicabilidad |
|---|---------|---------------|
| 1 | Triple capa YAML+código+template es el patrón más riesgoso — no delegar | Futuros planes con MIN-* gaps |
| 2 | Dict literal insertion pitfall: pre-computar ANTES del `data = {` | Cualquier método que construya data dicts grandes |
| 3 | Gate discrepancy: verificar siempre si 2 gates miden lo mismo | Auditorías de publication_gates |
| 4 | Dead code: verificar 0 referencias ANTES de eliminar | FASE-5 pattern |
| 5 | Cascada de fuentes (validated_data → benchmarks → None) es pattern defensivo reutilizable | Cualquier campo que "siempre es None" |

### Procesales

| # | Lección | Aplicabilidad |
|---|---------|---------------|
| 1 | FASE-0 de verificación es obligatoria — claims de auditorías pueden ser stale | Todos los planes desde contexto |
| 2 | v4complete único al final reduce riesgo de regressions invisibles | Planes con múltiples gaps |
| 3 | Evidencia obligatoria (T2) SIN importar tiempo restante | Cualquier fase con v4complete |
| 4 | Post-análisis con tabla explícita (esperado vs encontrado) | FASE-6 pattern |

---

## Sección G: Gaps Resueltos vs Nuevos

### Resueltos (7)

| ID | Severidad | Gap | Estado |
|----|-----------|-----|--------|
| IMP-03 | 🟡 | CAPEX breakdown sin consumir | ✅ Template fix |
| MIN-01 | 🔴 | Sin tabla Status Quo | ✅ Nuevo método + template |
| MIN-02 | 🔴 | ADR no evidenciado | ✅ YAML+código+template |
| MIN-03 | 🔴 | Closing pitch ausente | ✅ Nuevo método + template |
| F5 | 🔴 | ADR checklist siempre [PENDING] | ✅ Bug fix cascada |
| F7 | 🟡 | Discrepancia entre gates | ✅ Lógica unificada |
| Debt | 🟡 | Template embebido muerto | ✅ Eliminado |

### Nuevos descubiertos durante implementación

|| ID | Descripción | Acción tomada |
|----|-------------|---------------|
| NEW-1 | `adr_status: unknown` en audit_report — benchmark ADR no llega al cross-validator del auditor | FASE-7: investigación + fix o wontfix |

---

## Sección H: Checklist de Cierre

- [ ] Todas las fases (0 a RELEASE) marcadas ✅ en `06-checklist-implementacion.md`
- [ ] Evidencia de v4complete en `evidence/FASE-PENDIENTE-V4COMPLETE/`
- [ ] Post-análisis muestra 7/7 fixes superados (o documentar los parciales)
- [ ] Documentación cascade completada sin GAPs
- [ ] Versión sincronizada en todos los archivos
- [ ] README.md del plan actualizado con estado final
