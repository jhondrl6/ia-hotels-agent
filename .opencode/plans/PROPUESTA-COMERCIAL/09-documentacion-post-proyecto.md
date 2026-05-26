# Documentación Post-Proyecto — PROPUESTA-COMERCIAL

> Acumulador incremental. Actualizar después de cada fase.

---

## Sección A: Módulos Modificados

| Fase | Módulo | Archivo | Cambio |
|------|--------|---------|--------|
|| FASE-A | `v4_proposal_generator.py` | `modules/commercial_documents/v4_proposal_generator.py` | CODE-1: `recovered_6m` → `effective_monthly_gain` (L796); CODE-3: `net_benefit_6m` → `effective_monthly_gain` (L797); CODE-2: CG-ROI-NEGATIVE gate sync — `monthly_gain` ahora usa `pain_ratio × recovery_realistic` (L339-352) |
|| FASE-B | `v4_diagnostic_generator.py` + `v4_proposal_generator.py` + templates | `modules/commercial_documents/v4_diagnostic_generator.py` + `modules/commercial_documents/templates/diagnostico_v6_template.md` + `modules/commercial_documents/templates/propuesta_v6_template.md` | CROSS-1: Puente dual fuga bruta/recuperación — 4 placeholders nuevos (`fuga_total_6m`, `recuperacion_proyectada_6m`, `pain_pct`, `recov_pct`) en ambos generadores; tabla dual en diagnóstico + bloque trazabilidad en propuesta; diagnóstico usa defaults 20%/20%, propuesta usa pain_ratio real del pricing |
|| FASE-C | `v4_proposal_generator.py` | `modules/commercial_documents/v4_proposal_generator.py` | CROSS-2: BREACH_BY_ASSET dict (L1013-1022) mapea cada asset_type a `(brecha_num, nombre, costo_mensual)`; columna "Problema que resuelve" en tabla de servicios (L1043, L1067-1072) — 4 columnas: Servicio | Estado | Problema que resuelve | Qué obtiene |; AEO row con "—" en columna brecha (L1105). CROSS-4: `whatsapp_conflict` extraído de `audit_result.validation.whatsapp_status == CONFLICT` (L718-725) antes de `data = {}`; passed a `_generate_dynamic_services_table(whatsapp_conflict=...)` (L983); override para whatsapp_button → "⚠️ Requiere corrección" + "Guía de corrección incluida" (L1053-1058). |

---

## Sección B: Funcionalidades Agregadas/Modificadas

| Fase | Funcionalidad | Descripción |
|------|--------------|-------------|
| FASE-A | Unificación financiera en propuesta | `recovered_6m` y `net_benefit_6m` ahora usan `effective_monthly_gain` (post-recovery) sincronizados con `total_recovered`; gate CG-ROI-NEGATIVE ahora calcula con `pain_ratio × recovery` alineado a la tabla ROI |
| FASE-B | Puente dual fuga bruta/recuperación efectiva | Diagnóstico y propuesta ahora muestran AMBOS: "Fuga total estimada" y "Recuperación proyectada con servicio", con explicación visible del mecanismo `pain_ratio × recovery_factor`. Diagnóstico usa defaults conservadores (20%/20%); propuesta usa pain_ratio real del hotel (~41%) del pricing. Divergencia numérica intencional: el diagnóstico comunica urgencia con estimaciones conservadoras, la propuesta entrega precisión financiera. |
| FASE-C | Mapping brecha→servicio + WhatsApp conflict en propuesta | CROSS-2: Cada servicio en la tabla de propuesta ahora muestra qué brecha del diagnóstico resuelve y su costo mensual etiquetado — mejora trazabilidad para el cliente. CROSS-4: Si audit_result.validation.whatsapp_status == CONFLICT, el botón de WhatsApp muestra "⚠️ Requiere corrección (guía incluida)" en lugar de "ℹ️ Presente en sitio", reflejando honestamente el conflicto detectado. |

---

## Sección C: Evidencia

| Fase | Tipo | Ruta |
|------|------|------|
| — | — | — |

---

## Sección D: Métricas

| Fase | Métrica | Antes | Después |
|------|---------|-------|---------|
| — | — | — | — |

---

## Sección E: Archivos del Plan

| Archivo | Estado |
|---------|--------|
| `README.md` | ✅ Creado |
| `dependencias-fases.md` | ✅ Creado |
| `06-checklist-implementacion.md` | ✅ Creado |
| `09-documentacion-post-proyecto.md` | ✅ Creado |
| `05-prompt-inicio-sesion-fase-A.md` | ✅ Completada |
| `05-prompt-inicio-sesion-fase-B.md` | ✅ Completada |
| `05-prompt-inicio-sesion-fase-C.md` | ✅ Completada |
| `05-prompt-inicio-sesion-fase-D.md` | ⏳ |
| `05-prompt-inicio-sesion-fase-E.md` | ⏳ |
| `05-prompt-inicio-sesion-fase-F.md` | ⏳ |
| `05-prompt-inicio-sesion-fase-RELEASE.md` | ⏳ |
