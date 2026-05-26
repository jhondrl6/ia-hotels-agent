# Checklist Maestro de Implementación — PROPUESTA-COMERCIAL

> Actualizar después de cada fase. NO marcar ✅ sin verificación.

---

## FASE-A: CODE-1/3/4 + CODE-2 — Unificación financiera

| ID | Tarea | Estado | Evidencia |
|----|-------|--------|-----------|
|| A1 | Cambiar `recovered_6m` (L796): `projected_monthly_gain` → `effective_monthly_gain` | ✅ | `v4_proposal_generator.py` L796 |
|| A2 | Cambiar `net_benefit_6m` (L797): `projected_monthly_gain` → `effective_monthly_gain` | ✅ | `v4_proposal_generator.py` L797 |
|| A3 | Verificar que `total_recovered` (L824) ya usa `effective_monthly_gain` ✅ | ✅ | Verificado L824 → `effective_monthly_gain` |
|| A4 | Sincronizar CG-ROI-NEGATIVE: pasar `net_benefit_6m` calculado con `effective_monthly_gain` | ✅ | L339-352: now applies `pain_ratio * recovery_realistic` |

**Resultado FASE-A**: ✅ COMPLETADA (2026-05-26)

---

## FASE-B: CROSS-1 — Puente dual fuga bruta / recuperación efectiva

| ID | Tarea | Estado | Evidencia |
|----|-------|--------|-----------|
| B1 | Agregar bloque "Fuga total estimada vs Recuperación proyectada" en template diagnóstico (Sección 4) | ✅ | `diagnostico_v6_template.md` L143-157 — tabla dual después de `${scenario_table_rows}` |
| B2 | Agregar explicación `pain_ratio × recovery_factor` como puente narrativo | ✅ | `diagnostico_v6_template.md` L150-153 — nota explicativa "¿Por qué la diferencia?" |
| B3 | Replicar bloque dual en template propuesta (manteniendo nota `41% × 20%`) | ✅ | `propuesta_v6_template.md` L121-123 — bloque trazabilidad financiera + `v4_proposal_generator.py` L894-900 |
| B4 | Verificar que ambos generadores pasan los placeholders correctos a los templates | ✅ | grep: 8 asignaciones verificadas, 4 placeholders en AMBOS generadores, AMBOS templates |

**Resultado FASE-B**: ✅ COMPLETADA (2026-05-26)

---

## FASE-C: CROSS-2 + CROSS-4 — Mapping brecha→servicio + WhatsApp

| ID | Tarea | Estado | Evidencia |
|----|-------|--------|-----------|
| C1 | Agregar columna "Su problema (Brecha #N)" a tabla de servicios en propuesta | ⏳ | — |
| C2 | Vincular cada servicio a su brecha del diagnóstico con costo asociado | ⏳ | — |
| C3 | Corregir "Botón de WhatsApp \| Presente en sitio" → "⚠️ Requiere corrección" | ⏳ | — |
| C4 | Verificar que la tabla de servicios no se rompe con las nuevas columnas | ⏳ | — |

**Resultado FASE-C**: ⏳ PENDIENTE

---

## FASE-D: V-2 + V-3 + A-1 + CROSS-5 — Credibilidad

| ID | Tarea | Estado | Evidencia |
|----|-------|--------|-----------|
| D1 | Unificar labels: 4 instancias de "⚠️ En preparación/preparacion" → un solo formato | ⏳ | — |
| D2 | Agregar términos al gate CG-TECH-JARGON (OpenRouter, Perplexity, Gemini, GA4, GSC, UTM, iah-cli, iahotels.co) | ⏳ | — |
| D3 | Mover tabla IAO (L149-158) a anexo técnico en template | ⏳ | — |
| D4 | Eliminar fallback de string search en `has_onboarding` (L359) | ⏳ | — |
| D5 | Vincular confidence score a cada servicio en tabla de propuesta | ⏳ | — |

**Resultado FASE-D**: ⏳ PENDIENTE

---

## FASE-E: A-2 + V-4/5/6 + A-3 + CROSS-6 — Paquete + Pulido + Gate

| ID | Tarea | Estado | Evidencia |
|----|-------|--------|-----------|
| E1 | Unificar umbral AEO a 30 en ambas tablas (L1035 y L1235) | ⏳ | — |
| E2 | Justificar "cupo limitado" con número ("2 cupos para julio") o eliminar | ⏳ | — |
| E3 | Reformular garantía hacia tracking propio instalado en Día 7 | ⏳ | — |
| E4 | Agregar sección placeholder de prueba social en template | ⏳ | — |
| E5 | Corregir typo "PASSO" → "PASO" (L173 template propuesta) | ⏳ | — |
| E6 | Hacer que gates NOT_READY bloqueen generación de documentos | ⏳ | — |

**Resultado FASE-E**: ⏳ PENDIENTE

---

## FASE-F: v4complete + Análisis Post-Implementación

| ID | Tarea | Estado | Evidencia |
|----|-------|--------|-----------|
| F1 | Ejecutar `main.py v4complete --url https://www.hotelcastillareal.com/` | ⏳ | — |
| F2 | Copiar outputs a `evidence/FASE-F/` (diagnóstico, propuesta, assets, JSONs) | ⏳ | — |
| F3 | Crear análisis post-implementación verificando los 5 niveles de la auditoría | ⏳ | — |

**Resultado FASE-F**: ⏳ PENDIENTE

---

## FASE-RELEASE: Documentación

| ID | Tarea | Estado | Evidencia |
|----|-------|--------|-----------|
| R1 | `log_phase_completion.py` para TODAS las fases A-F | ⏳ | — |
| R2 | `sync_versions.py` — version bump a v4.53.0 | ⏳ | — |
| R3 | Actualizar CHANGELOG.md con resumen PROPUESTA-COMERCIAL | ⏳ | — |
| R4 | Actualizar GUIA_TECNICA.md si hubo cambios de API/pipeline | ⏳ | — |

**Resultado FASE-RELEASE**: ⏳ PENDIENTE
