# ROI-REFACTOR — Plan de Refactorización Post-Auditoría

**Versión**: v1.1.0 (plan)
**Target Release**: v4.54.0 — ROI-REFACTOR
**Creado**: 2026-05-26
**Actualizado**: 2026-05-26
**Origen**: `ROI_AUDIT.md` — auditoría contra código vivo del ROI.md original
**Objetivo**: Corregir 10 hallazgos post-PROPUESTA-COMERCIAL que impiden que la propuesta para Hotel Castilla Real sea comercialmente impecable.

---

## Resumen del Problema

El plan PROPUESTA-COMERCIAL (FASE-A a FASE-RELEASE, v4.53.0) corrigió 14 hallazgos técnicos. Sin embargo, el `ROI_AUDIT.md` reveló que el ROI.md original contenía **3 errores factuales** (triple descuento inexistente, fórmula fraudulenta con $7.7M, pain_ratio malinterpretado) y que persisten **10 problemas no cubiertos** por las fases anteriores:

1. 🔴 "⚠️ Alertas Comerciales" se inyectan en el output del cliente sin `document_audience` switch
2. 🔴 Placeholder `[Espacio para casos de éxito...]` hardcodeado sin condicional
3. 🔴 Nota de pain_ratio dice "porción del dolor abordable con IAO" (falso — es artifact del min_price)
4. 🟡 Jerga técnica (AEO, UTMs, P1/P2/P3) sin traducir a lenguaje de negocio
5. 🟡 Tabla de entregables muestra % de confianza en vez de "Momento de entrega"
6. 🟡 ADR del web_scraper desconectado del financial engine
7. 🟡 Versión hardcodeada `4.0.0` en frontmatter del output
8. 🟢 Anexo Técnico APIs visible al cliente (ruido)
9. 🟢 evidence_tier vs precision_tier sin documentar
10. 🟢 Sin nota explicativa pain_ratio 20% vs 41% (diagnóstico vs propuesta)

**Veredicto del ROI_AUDIT.md**: La fórmula del ROI es correcta. El ROI negativo es un hecho comercial, no un bug. Los fixes son de presentación, trazabilidad y transparencia — NO de manipulación de números.

---

## FASE-0: Decisión Comercial (NUEVA)

⚠️ **Esta fase es prerrequisito para todas las demás.** Antes de invertir en implementar los 10 fixes técnicos, es necesario resolver el desbalance estructural entre precio del servicio ($1.2M/mes) y recovery realista ($305K/mes). De lo contrario, la propuesta seguirá siendo comercialmente invendible sin importar cuánto pulimento técnico se aplique.

**Scope**: Evaluar opciones comerciales A/B/C/D (ROI_AUDIT PARTE 6) + opción combinada B+C + alternativa E propuesta por el agente. Presentar análisis y registrar decisión operativa. **Decisión FASE-0**: Opción E — piloto pagado de $250K con crédito a retainer futuro + success fee capped post-tracking.

---

## Fases del Plan

|| Fase | Descripción | Tipo | Fixes | Prerrequisito |
|------|-------------|------|-------|----------------|
| **FASE-0** | Decisión comercial: pricing/estructura — Opción E elegida | Decisión | 0 | Ninguno |
| **FASE-1** | Bloqueantes de output: ocultar alertas, eliminar placeholder testimonios, corregir nota pain_ratio | Código+Tmpl | 3 (🔴) | FASE-0 |
| **FASE-2** | Jerga técnica + entregables: traducir AEO/UTMs/P1-P3, cambiar tabla a "Momento de entrega" | Código+Tmpl | 2 (🟡) | FASE-0 |
| **FASE-3** | ADR scraper + versión: conectar web_scraper como fallback, dynamic version | Código | 2 (🟡) | FASE-1, FASE-2 |
| **FASE-4** | Pulido final: simplificar anexo APIs, documentar tiers, nota pain_ratio | Código+Tmpl | 3 (🟢) | FASE-3 |
| **FASE-5** | v4complete Hotel Castilla Real + análisis post-implementación | Ejecución | 1 comando + informe | FASE-0 a FASE-4 |

**Total**: 6 sesiones. 1 fase por sesión. FASE-0 debe ejecutarse primero.

---

## Métricas Base (post-PROPUESTA-COMERCIAL)

|| Métrica | Valor Actual |
|---------|-------------|
| Versión | v4.53.0 |
| Coherence Score | 0.83 |
| Publication Gates | 10/11 (1 warning no bloqueante) |
| Pain Ledger | 11 entries |
| ROI Castilla Real | -$5,367,168 COP / 0.3X (negativo — esperado, no bug) |

---

## Archivos del Plan

|| Archivo | Propósito |
|---------|---------|
| `README.md` | Este archivo — índice del plan |
| `dependencias-fases.md` | Diagrama de dependencias entre fases |
| `05-prompt-inicio-sesion-fase-0.md` | Prompt para FASE-0 (DECISIÓN COMERCIAL) |
| `05-prompt-inicio-sesion-fase-A.md` | Prompt para FASE-1 (ex-FASE-A) |
| `05-prompt-inicio-sesion-fase-B.md` | Prompt para FASE-2 (ex-FASE-B) |
| `05-prompt-inicio-sesion-fase-C.md` | Prompt para FASE-3 (ex-FASE-C) |
| `05-prompt-inicio-sesion-fase-D.md` | Prompt para FASE-4 (ex-FASE-D) |
| `05-prompt-inicio-sesion-fase-E.md` | Prompt para FASE-5 (ex-FASE-E) |
| `06-checklist-implementacion.md` | Checklist maestro de implementación |
| `09-documentacion-post-proyecto.md` | Acumulador de documentación post-fase |

---

## Criterio de Éxito Final (FASE-5)

Al completar FASE-5, el output de v4complete para Hotel Castilla Real debe satisfacer:

- [ ] **Nivel 1 — Bloqueantes**: Sin "⚠️ Alertas Comerciales" en output cliente; sin placeholder vacío de testimonios; nota de pain_ratio corregida semánticamente
- [ ] **Nivel 2 — Jerga y entregables**: Sin términos AEO/UTMs/P1/P2/P3 sin traducir; tabla de entregables muestra "Momento de entrega", no % confianza
- [ ] **Nivel 3 — Trazabilidad**: ADR del sitio web usado como fallback; versión real del pipeline en frontmatter
- [ ] **Nivel 4 — Pulido**: Anexo APIs simplificado a párrafo de transparencia; tiers documentados
- [ ] **Nivel 5 — Transparencia**: Nota pain_ratio 20% vs 41% explicada en diagnóstico; output listo para entrega comercial

**Prerrequisito FASE-0**: ✅ Decisión comercial documentada. Para Castilla Real, la recomendación operativa es Opción E: piloto/activación $250K con crédito a retainer futuro + success fee capped solo después de tracking/baseline.

---

## Lo que este plan NO hace

- ❌ NO cambia la fórmula del ROI (es correcta)
- ❌ NO infla números para hacer el ROI positivo
- ❌ NO implementa cambios de pricing sin decisión de Jhond (FASE-0)
- ❌ NO modifica `commercial_gate.py` (el validador funciona bien; es el caller quien decide renderizar)

---

## Lo que SÍ se preserva del plan PROPUESTA-COMERCIAL

- ✅ Puente dual CROSS-1 (fuga bruta ↔ recuperación efectiva)
- ✅ Mapping brecha→servicio CROSS-2
- ✅ WhatsApp conflict visibility CROSS-4
- ✅ Labels de estado unificados (FASE-D)
- ✅ CG-TECH-JARGON expandido (FASE-D)
- ✅ Cupo, garantía, prueba social (FASE-E)
- ✅ Gate blocking CROSS-6 (FASE-E)
