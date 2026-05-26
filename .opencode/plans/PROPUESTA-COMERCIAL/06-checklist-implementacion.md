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

|| ID | Tarea | Estado | Evidencia |
||----|-------|--------|-----------|
|| C1 | Agregar columna "Su problema (Brecha #N)" a tabla de servicios en propuesta | ✅ | `v4_proposal_generator.py` L1043: header 4 columnas + BREACH_BY_ASSET dict (L1013-1022) |
|| C2 | Vincular cada servicio a su brecha del diagnóstico con costo asociado | ✅ | `v4_proposal_generator.py` L1067-1072: `brecha_col = f"Brecha #N: Nombre ($X/mes)"` |
|| C3 | Corregir "Botón de WhatsApp | Presente en sitio" → "⚠️ Requiere corrección" | ✅ | `v4_proposal_generator.py` L1053-1058: `whatsapp_conflict=True` → override + "Guía de corrección incluida"; `_prepare_template_data` L718-725: extracción `whatsapp_status == CONFLICT` |
|| C4 | Verificar que la tabla de servicios no se rompe con las nuevas columnas | ✅ | `py_compile` OK; tabla 4 columnas con separadores `|----------|--------|----------------------|-------------|` |

**Resultado FASE-C**: ✅ COMPLETADA (2026-05-26)

---

## FASE-D: V-2 + V-3 + A-1 + CROSS-5 — Credibilidad

| ID | Tarea | Estado | Evidencia |
|----|-------|--------|-----------|
| D1 | Unificar labels: 4 instancias de "⚠️ En preparación/preparacion" → un solo formato | ✅ | `v4_proposal_generator.py` L1073, L1117, L1167, L1360: "En proceso de activación — Semana 2" |
| D2 | Agregar términos al gate CG-TECH-JARGON (OpenRouter, Perplexity, Gemini, GA4, GSC, UTM, iah-cli, iahotels.co) | ✅ | `commercial_gate.py` L85-92: 8 términos nuevos agregados |
| D3 | Mover tabla IAO (L149-158) a anexo técnico en template | ✅ | `propuesta_v6_template.md` L151-161: reemplazada por referencia "Ver Anexo Técnico"; L217-232: nueva sección "Anexo Técnico: Infraestructura IAO" |
| D4 | Eliminar fallback de string search en `has_onboarding` (L359) | ✅ | `v4_proposal_generator.py` L361-366: eliminada línea `'onboarding' in document_content.lower()` |
| D5 | Vincular confidence score a cada servicio en tabla de propuesta | ✅ | `v4_proposal_generator.py` L1051-1121: columna "Confianza" + CROSS-5 ⚠️ visible para scores < 0.65 |

**Resultado FASE-D**: ✅ COMPLETADA (2026-05-26)

---

## FASE-E: A-2 + V-4/5/6 + A-3 + CROSS-6 — Paquete + Pulido + Gate

| ID | Tarea | Estado | Evidencia |
|----|-------|--------|-----------|
| E1 | Unificar umbral AEO a 30 en ambas tablas (L1035 y L1235) | ✅ | `v4_proposal_generator.py` L1105: `< 20` → `< 30` en `_generate_dynamic_services_table()`; L1313 ya era `< 30` en `_generate_technical_assets_table()` |
| E2 | Justificar "cupo limitado" con número ("2 cupos para julio") o eliminar | ✅ | `propuesta_v6_template.md` L14: "Válido por 15 días — 2 cupos disponibles para julio 2026" |
| E3 | Reformular garantía hacia tracking propio instalado en Día 7 | ✅ | `propuesta_v6_template.md` L161: "Instalamos tracking propio en el Día 7 — sin necesidad de que tengas GA4" |
| E4 | Agregar sección placeholder de prueba social en template | ✅ | `propuesta_v6_template.md` L169-173: sección "🏨 Hoteles que ya confiaron en nosotros" con placeholder de casos de éxito |
| E5 | Corregir typo "PASSO" → "PASO" (L173 template propuesta) | ✅ | `propuesta_v6_template.md` L170 + `diagnostico_v6_template.md` L193: ambos corregidos; grep confirma 0 residuales en modules/ |
| E6 | Hacer que gates NOT_READY bloqueen generación de documentos | ✅ | `main.py` L2728-2774: lógica de bloqueo con flag `GATE_BLOCKING_ENABLED`; si NOT_READY elimina docs y escribe `BLOCKED_BY_GATES.md`; `gate_report.json` y `v4_complete_report.json` se generan igual |

**Resultado FASE-E**: ✅ COMPLETADA (2026-05-26)

---

## FASE-F: v4complete + Análisis Post-Implementación

| ID | Tarea | Estado | Evidencia |
|----|-------|--------|-----------|
| F1 | Ejecutar `main.py v4complete --url https://www.hotelcastillareal.com/` | ✅ | 2026-05-26 — 92s, coherence 0.83, 12 assets, v4_complete_report.json generado |
| F2 | Copiar outputs a `evidence/FASE-F/` (diagnóstico, propuesta, assets, JSONs) | ✅ | evidence/FASE-F/ contiene todos los archivos listados en analisis_post_implementacion.md |
| F3 | Crear análisis post-implementación verificando los 5 niveles de la auditoría | ✅ | 4.5/5 niveles superados; analisis_post_implementacion.md creado |

**Resultado FASE-F**: ✅ COMPLETADA (2026-05-26)

---

## FASE-RELEASE: Documentación

|| ID | Tarea | Estado | Evidencia |
||----|-------|--------|-----------|
|| R1 | `log_phase_completion.py` para TODAS las fases A-F | ✅ | FASE-A-E registradas; FASE-F sin log (es ejecución) |
|| R2 | `sync_versions.py` — version bump a v4.53.0 | ✅ | VERSION.yaml → 4.53.0, AGENTS.md + README.md sincronizados |
|| R3 | Actualizar CHANGELOG.md con resumen PROPUESTA-COMERCIAL | ✅ | Entrada [4.53.0] — PROPUESTA-COMERCIAL (2026-05-26) al inicio |
|| R4 | Actualizar GUIA_TECNICA.md si hubo cambios de API/pipeline | ✅ | Nota v4.53.0 añadida con CROSS-6 como cambio de comportamiento |

**Resultado FASE-RELEASE**: ✅ COMPLETADA (2026-05-26)
