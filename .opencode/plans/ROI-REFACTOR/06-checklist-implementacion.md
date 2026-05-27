# Checklist de Implementación — ROI-REFACTOR

**Plan**: ROI-REFACTOR
**Target**: v4.54.0
**Origen**: ROI_AUDIT.md (2026-05-26)
**Actualizado**: 2026-05-26 (FASE-0 añadida)

---

## FASE-0: Decisión Comercial (Prerrequisito)

⚠️ FASE-0 debe completarse ANTES de cualquier otra fase. Sin esta decisión, las fases técnicas carecen de sentido comercial.

|| ID | Tarea | Estado | Verificación |
|----|-------|--------|-------------|
| 0A | Analizar opciones comerciales A/B/C/D + B+C + opción E | ✅ | Análisis en 09-documentacion-post-proyecto.md §F |
| 0B | Presentar recomendación del agente | ✅ | Opción E recomendada |
| 0C | Registrar decisión operativa | ✅ | En 09-documentacion-post-proyecto.md |
| 0D | Documentar pricing Fase 1 | ✅ | Piloto/activación $250K |
| 0E | Actualizar dependencias-fases.md (numeración/estado) | ✅ | Todas las fases referenciadas |

---

## FASE-1: Bloqueantes de output (3 fixes 🔴) [ex-FASE-A]

| ID | Tarea | Estado | Verificación |
|----|-------|--------|-------------|
| A1 | `document_audience` switch en `v4_proposal_generator.py:generate()` | ✅ | Sin alertas en output cliente |
| A2 | `document_audience` switch en `v4_diagnostic_generator.py:generate()` | ✅ | Sin alertas en output cliente |
| A3 | Eliminar placeholder testimonios — `{% if testimonials %}` en template | ✅ | Sin `[Espacio para...]` en output |
| A4 | Corregir nota pain_ratio: "porción IAO" → "relación inversión/pérdida" | ✅ | Nota corregida en output |

---

## FASE-2: Jerga + Entregables (2 fixes 🟡) [ex-FASE-B]

|| ID | Tarea | Estado | Verificación |
|----|-------|--------|-------------|
| B1 | Traducir AEO, UTMs, P1/P2/P3 en template | ✅ | Sin jerga técnica en output |
| B2 | Tabla entregables: "Estado" → "Momento de entrega", sin % confianza | ✅ | Headers correctos en output |

---

## FASE-3: ADR scraper + Versión (2 fixes 🟡) [ex-FASE-C]

|| ID | Tarea | Estado | Verificación |
|----|-------|--------|-------------|
| C1 | Conectar web_scraping ADR como fallback intermedio | ✅ | `adr_source: "web_scraping"` en JSON (ya existía, se agregó adr_source explícito) |
| C2 | Dynamic version → `PIPELINE_VERSION` en L725 | ✅ | Frontmatter = v4.53.0 (desde VERSION.yaml); también en v4_diagnostic_generator.py |

---

## FASE-4: Pulido final (3 fixes 🟢) [ex-FASE-D]

|| ID | Tarea | Estado | Verificación |
|----|-------|--------|-------------|
| D1 | Simplificar Anexo APIs → párrafo de transparencia | ⬜ | Sin tabla de APIs en output |
| D2 | Documentar evidence_tier vs precision_tier | ⬜ | `tier_explanation` en JSON |
| D3 | Nota explicativa pain_ratio 20% vs 41% en diagnóstico | ⬜ | Nota en diagnóstico |

---

## FASE-5: v4complete + Análisis [ex-FASE-E]

|| ID | Tarea | Estado | Verificación |
|----|-------|--------|-------------|
| E1 | Ejecutar v4complete Hotel Castilla Real | ⬜ | Output files generados |
| E2 | Análisis post-implementación 5 niveles | ⬜ | `analisis_post_implementacion.md` |
| E3 | Veredicto comercial + comparativa pre/post | ⬜ | Veredicto documentado |

---

## Métricas Finales (post FASE-5)

|| Métrica | Pre-ROI-REFACTOR | Post-ROI-REFACTOR |
|---------|-----------------|-------------------|
| Coherence Score | 0.83 | [ ] |
| Publication Gates | 10/11 | [ ] |
| Blocking Issues | 0 | [ ] |
| Alertas visibles al cliente | Sí | No |
| Placeholder testimonios | Sí | No |
| Nota pain_ratio correcta | No | Sí |
| Jerga técnica | Presente | Traducida |
| Entregables | % confianza | Momento de entrega |
| ADR fuente | Benchmark | [ ] |
| Versión frontmatter | 4.0.0 | [dinámica] |
| APIs visibles | Sí | No |
| Tiers documentados | No | Sí |
| Decisión comercial | ❌ No tomada | ✅ Opción E documentada |
| ROI 6m | -$5,367,168 COP | [ ] (sin cambio — deuda comercial) |

---

## Veredicto Esperado

**FASE-0 resuelve la deuda comercial ANTES de la ejecución técnica.**

Si la decisión es B+C (Combinada):
> ✅ VIABLE — Estructura en 2 fases: Activación $250K → % recovery en Fase 2

Si la decisión es E (Piloto con crédito + success fee capped):
> ✅ RECOMENDADA — Mantiene activación $250K, reduce objeción de pago doble y conserva upside con medición real

Si la decisión es A (Lower pricing):
> ✅ VIABLE — ROI positivo con onboarding fee bajo

Si la decisión es C (% recovery directo):
> ⚠️ VIABLE CON CONDICIÓN — Necesita baseline de tracking primero

Si la decisión es D (Transparencia total):
> ⚠️ VIABLE CON DEUDAS — El ROI negativo se documenta pero se mantiene pricing

** Independientemente de la decisión técnica, el output de FASE-5 debe estar técnicamente impecable (niveles 1-4 superados).
