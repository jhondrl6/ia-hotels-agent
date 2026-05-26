# PROPUESTA-COMERCIAL — Plan de Refactorización

**Versión**: v1.0.0 (plan)
**Target Release**: v4.53.0 — PROPUESTA-COMERCIAL
**Creado**: 2026-05-26
**Origen**: Auditoría v3 de `Propuesta.md` contra código vivo (`v4_proposal_generator.py`, `commercial_gate.py`, `propuesta_v6_template.md`)
**Objetivo**: Corregir 14 hallazgos (5 bloqueantes, 4 altos, 5 medios/bajos) que impiden que la propuesta comercial para Hotel Castilla Real sea enviable al dueño.

---

## Resumen del Problema

El output de v4complete para Hotel Castilla Real (2026-05-25) fue auditado contra el código vivo, revelando desconexiones críticas entre diagnóstico y propuesta, bugs financieros que producen números contradictorios, y deficiencias de credibilidad comercial. El veredicto: **NO se puede enviar al dueño** — el gap 12:1 entre la fuga bruta reportada ($22.4M) y la recuperación ofrecida ($1.8M) destruye la confianza.

### Hallazgos Activos (14 de 19 originales)

| # | Tipo | Hallazgo | Severidad |
|---|------|----------|-----------|
| CODE-1/3/4 | Código | `recovered_6m` y `net_benefit_6m` usan base optimista (projected_monthly_gain) | 🔴 BLOQUEANTE |
| CODE-2 | Código | Gate CG-ROI-NEGATIVE no sincronizado con tabla ROI | 🔴 BLOQUEANTE |
| CROSS-1 | Cross-doc | Sin puente dual fuga bruta ($22.4M) ↔ recuperación efectiva ($1.8M) | 🔴 BLOQUEANTE |
| CROSS-2 | Cross-doc | 7 brechas → 8 servicios sin mapping verificable | 🔴 BLOQUEANTE |
| CROSS-4 | Cross-doc | WhatsApp: "Presente en sitio" contradice alerta del diagnóstico | 🟠 ALTO |
| A-1 | Código | `has_onboarding` con fallback frágil de búsqueda de string | 🟠 ALTO |
| V-2 | Código | "⚠️ En preparación" inconsistente (3 con tilde, 1 sin tilde) | 🟠 ALTO |
| V-3 | Código+Tmpl | Jerga técnica no detectada (OpenRouter, Perplexity, Gemini...) + Tabla IAO expuesta | 🟠 ALTO |
| CROSS-5 | Cross-doc | Confidence score no vinculado a servicios en propuesta | 🟡 MEDIO |
| A-2 | Código | Umbral AEO contradictorio (20 vs 30) en tablas distintas | 🟡 MEDIO |
| V-4 | Template | "Cupo limitado" sin justificación | 🟡 MEDIO |
| V-5 | Template | Garantía no medible sin GA4 | 🟡 MEDIO |
| V-6 | Template | Sin sección de prueba social | 🟡 MEDIO |
| A-3 | Template | Typo "PASSO" → "PASO" | 🟢 BAJO |
| CROSS-6 | Pipeline | Gates NOT_READY no bloquean generación de documentos | 🟢 BAJO |

### Hallazgos YA RESUELTOS (por DIAGNOSTIC-ALIGNMENT)

| # | Hallazgo | Resuelto en |
|---|----------|-------------|
| CROSS-3 | Escenarios del diagnóstico corregidos (financial_value_range) | DIAGNOSTIC-ALIGNMENT FASE-A |
| B-1 | Double pipe `\|\|` en tablas | Ya no existe en código actual |

---

## Fases del Plan

| Fase | Descripción | Tipo | Tareas | Comando Largo |
|------|-------------|------|--------|---------------|
| **FASE-A** | CODE-1/3/4 + CODE-2: Unificar variables financieras + sincronizar gate | Código | 4 | 0 |
| **FASE-B** | CROSS-1: Puente dual fuga bruta/recuperación efectiva | Templates | 4 | 0 |
| **FASE-C** | CROSS-2 + CROSS-4: Mapping brecha→servicio + WhatsApp conflict | Templates | 4 | 0 |
| **FASE-D** | V-2 + V-3 + A-1 + CROSS-5: Labels, jerga, onboarding, confidence | Código+Tmpl | 4 | 0 |
| **FASE-E** | A-2 + V-4/5/6 + A-3 + CROSS-6: AEO, paquete, pulido, gate blocking | Código+Tmpl | 4 | 0 |
| **FASE-F** | v4complete Hotel Castilla Real + análisis post-implementación | Ejecución | 3 | 1 (v4complete) |
| **FASE-RELEASE** | Documentación oficial + Version bump | Release | 4 | 0 |

**Total**: 7 sesiones. 1 fase por sesión.

---

## Métricas Base

| Métrica | Valor Actual |
|---------|-------------|
| Versión | ~4.52.x (post-DIAGNOSTIC-ALIGNMENT) |
| Coherence Score | 0.83 (Hotel Castilla Real, último baseline) |
| Publication Gates | 9/11 (2 warnings no bloqueantes) |
| Pain Ledger | 11 entries |

---

## Archivos del Plan

| Archivo | Propósito |
|---------|-----------|
| `README.md` | Este archivo — índice del plan |
| `dependencias-fases.md` | Diagrama de dependencias entre fases |
| `05-prompt-inicio-sesion-fase-A.md` | Prompt para FASE-A |
| `05-prompt-inicio-sesion-fase-B.md` | Prompt para FASE-B |
| `05-prompt-inicio-sesion-fase-C.md` | Prompt para FASE-C |
| `05-prompt-inicio-sesion-fase-D.md` | Prompt para FASE-D |
| `05-prompt-inicio-sesion-fase-E.md` | Prompt para FASE-E |
| `05-prompt-inicio-sesion-fase-F.md` | Prompt para FASE-F |
| `05-prompt-inicio-sesion-fase-RELEASE.md` | Prompt para FASE-RELEASE |
| `06-checklist-implementacion.md` | Checklist maestro de implementación |
| `09-documentacion-post-proyecto.md` | Acumulador de documentación post-fase |

---

## Criterio de Éxito Final

Al completar FASE-F, el output de v4complete para Hotel Castilla Real debe satisfacer:

- [ ] **Nivel 1 — Bloqueantes**: Puente dual visible en diagnóstico + propuesta; mapping brecha→servicio trazable; todas las variables financieras unificadas sobre `effective_monthly_gain`; gate CG-ROI-NEGATIVE sincronizado
- [ ] **Nivel 2 — Código**: Sin contradicciones internas entre `roi_6m`, `recovered_6m`, `net_benefit_6m`, `total_recovered`
- [ ] **Nivel 3 — Credibilidad**: WhatsApp refleja conflicto real; labels de estado consistentes; jerga técnica filtrada o movida a anexos
- [ ] **Nivel 4 — Paquete comercial**: Confidence score visible; justificación de cupo; garantía medible; prueba social presente
- [ ] **Nivel 5 — Pulido**: Sin typos; sin columnas fantasma en tablas; gates NOT_READY bloquean efectivamente

---

## Estrategia de Decisión de Producto (CROSS-1)

La auditoría recomienda la **Opción C — Puente dual obligatorio**: diagnóstico y propuesta muestran siempre dos columnas coordinadas: **Fuga total estimada** (`raw_loss × 6`) y **Recuperación proyectada con servicio** (`raw_loss × pain_ratio × recovery_factor × 6`). La nota `41% × 20%` pasa de nota menor en la propuesta a explicación visible en AMBOS documentos. Esta decisión de producto se implementa en FASE-B.
