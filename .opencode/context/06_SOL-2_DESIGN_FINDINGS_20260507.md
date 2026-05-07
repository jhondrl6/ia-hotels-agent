---
generated_at: 2026-05-07 17:15
updated_at: 2026-05-07 17:15
version: 1.0.0
document_type: CONTEXT_DESIGN_FINDINGS
related_plan: SOL-2-REFACTOR (FASE-SOL2-A/B/C/D completadas)
source: Post-mortem verification of SOL-2 — 2026-05-07 session
trigger: Auditoria post-implementacion del plan SOL-2. Los 6 GAPs originales estan resueltos, pero se identificaron 3 hallazgos de diseno que no requieren accion inmediata.
evidence_files:
  - modules/commercial_documents/coherence_validator.py (lineas 494-555, metodo _check_promised_assets_exist)
  - modules/asset_generation/v4_asset_orchestrator.py (lineas 144-145, site_verification_applied)
  - .opencode/plans/SOL-2-REFACTOR/05-prompt-inicio-sesion-fase-SOL2-A.md
  - .opencode/plans/SOL-2-REFACTOR/05-prompt-inicio-sesion-fase-SOL2-B.md
  - evidence/FASE-SOL2-C/analisis_ejecucion.md
---

# CONTEXTO: Hallazgos de Diseno Post SOL-2

## RESUMEN EJECUTIVO

Tras la auditoria post-implementacion del plan SOL-2 Asset Alignment Refactor (v4.42.0), el codigo y las validaciones automatizadas pasan al 100%. Sin embargo, se identificaron **3 hallazgos de diseno** que, aunque no bloquean la publicacion ni rompen funcionalidad, representan deuda tecnica o puntos de mejora que merecen decision en una sesion futura.

**Veredicto**: Los 3 hallazgos son de severidad BAJA. No requieren accion inmediata. Se recomienda abordarlos como una micro-fase de refinamiento (< 30 iteraciones) cuando el pipeline este estable tras los proximos releases.

---

## HALLAZGO D1 [BAJA] — Duplicacion en mensaje de CoherenceValidator

### Sintoma

En el metodo `_check_promised_assets_exist()` (coherence_validator.py, FASE-SOL2-B), cuando un asset type esta presente tanto en `promised_types` (del diagnostico) como en `PROPOSAL_SERVICE_TO_ASSET.values()` (del contrato estatico) y NO esta implementado, el mensaje de error lo menciona DOS veces con formatos distintos:

```
"Assets no implementados: hotel_schema; Servicios sin asset implementado: Datos Estructurados→hotel_schema"
```

### Causa

El codigo de FASE-SOL2-B unifica dos listas (`missing_types` + `missing_service_assets`) sin deduplicar para el mensaje. El score usa `set(all_missing)` asi que el calculo es correcto. Solo el mensaje es redundante.

```python
# coherence_validator.py ~L530
all_missing = missing_types + missing_service_assets  # puede tener duplicados
# El mensaje concatena ambos sin filtro:
msg_parts.append(f"Assets no implementados: {', '.join(missing_types)}")
msg_parts.append(f"Servicios sin asset implementado: {', '.join(missing_service_assets)}")
```

### Opciones

| Opcion | Descripcion | Esfuerzo | Riesgo |
|--------|-------------|----------|--------|
| D1-A: Dedeplicar mensaje | Si un asset type aparece en ambas listas, mostrarlo solo en `missing_service_assets` (formato "servicio→asset" es mas informativo). Suprimir de `missing_types`. | 2 lineas | Nulo |
| D1-B: Mantener como esta | El mensaje solo aparece en modo `severity=error`, que es raro (requiere assets no implementados en catalogo). El costo de mantenerlo es ~0. | 0 | Nulo |
| D1-C: Unificar formato | Usar SIEMPRE formato "servicio→asset" incluso para missing_types, eliminando la distincion. Requiere reverse lookup de asset_type → service_name. | ~10 lineas | Bajo |

**Recomendacion**: D1-A. Es la correccion mas simple y no introduce nueva logica. Si un asset type esta en ambas listas, el formato "servicio→asset" aporta mas contexto al desarrollador.

---

## HALLAZGO D2 [BAJA] — Plan prompts no parcheados tras descubrimiento de falsos positivos

### Sintoma

Los archivos de prompt de las fases SOL-2-A y SOL-2-B conservan su redaccion original, que asume que GAP-A (SitePresenceChecker) y GAP-B (deployment_assistant.md) son problemas REALES de severidad ALTA. La ejecucion de SOL-2-A demostro que ambos eran **falsos positivos** (los archivos existen y son funcionales desde commits anteriores).

Si un agente en una sesion futura re-ejecuta estos prompts sin contexto, perdera iteraciones re-verificando lo mismo.

### Archivos afectados

| Archivo | Lineas con claim obsoleto |
|---------|--------------------------|
| `.opencode/plans/SOL-2-REFACTOR/05-prompt-inicio-sesion-fase-SOL2-A.md` | 19-20 (GAP-A ALTA, GAP-B ALTA), 40-53 (tareas de creacion/eliminacion) |
| `.opencode/plans/SOL-2-REFACTOR/05-prompt-inicio-sesion-fase-SOL2-B.md` | 16 (dice "depende de FASE-SOL2-A completada") |

### Opciones

| Opcion | Descripcion | Esfuerzo | Riesgo |
|--------|-------------|----------|--------|
| D2-A: Parchear prompts | Agregar disclaimer al inicio de SOL2-A y SOL2-B: "NOTA POST-EJECUCION: GAP-A y GAP-B resultaron falsos positivos. SitePresenceChecker y deployment_assistant.md ya existian. Esta fase se ejecuto como validacion, no como implementacion." | 5 lineas por archivo | Nulo |
| D2-B: Archivar plan | Mover `SOL-2-REFACTOR/` a `SOL-2-REFACTOR-ARCHIVED/` y crear un README que documente lo ocurrido. | ~10 lineas | Medio (rompe referencias en REGISTRY.md) |
| D2-C: No hacer nada | El plan ya esta marcado como completado en `dependencias-fases.md`. Ningun agente deberia re-ejecutarlo. | 0 | Bajo (solo si alguien re-ejecuta manualmente) |

**Recomendacion**: D2-A. Agregar una nota de "POST-EJECUCION" al inicio de cada prompt de fase que resulto ser validacion en vez de implementacion. Es barato, no rompe nada, y protege contra re-ejecucion accidental.

---

## HALLAZGO D3 [BAJA] — Flag global site_verification_applied no se activa

### Sintoma

El reporte `asset_generation_report.json` muestra `site_verification_applied: false` a nivel global, aunque SitePresenceChecker SI se ejecuto a nivel de gate individual. Evidencia:

- `gate_report.json`: WhatsApp muestra `presence_verified: true, presence_status: not_exists` → el checker se ejecuto
- `asset_generation_report.json`: `site_verification_applied: false` → flag global no refleja la realidad

### Causa

En `v4_asset_orchestrator.py` L144-145:

```python
"delivery_ready_percentage": round(delivery_ready_pct, 2),
"site_verification_applied": len(self.skipped_assets) > 0  # FASE-CAUSAL-01
```

El flag se activa solo si hay assets **skipeados** (omitidos por presencia existente). Pero SitePresenceChecker se ejecuta en el gate (`publication_gates.py:_proposal_asset_alignment_gate`), no en el orchestrator. Si el checker detecta presencia pero el orchestrator no skipea el asset (porque la generacion ya ocurrio antes del gate), el flag queda en `false`.

Este es un **gap de timing**: el checker corre downstream (en el gate), pero el flag se evalua upstream (en el orchestrator, antes del gate).

### Opciones

| Opcion | Descripcion | Esfuerzo | Riesgo |
|--------|-------------|----------|--------|
| D3-A: Mover el flag al gate | En `_proposal_asset_alignment_gate()`, establecer `site_verification_applied = True` en el assessment cuando el checker se ejecute exitosamente. El orchestrator leeria este valor del assessment post-gate. | ~5 lineas | Bajo (cambio de orden de escritura) |
| D3-B: Ejecutar checker en el orchestrator | Mover la invocacion de SitePresenceChecker del gate al orchestrator, ANTES de generar assets. Los assets se generarian condicionalmente (skip si ya existen). | ~30 lineas | Medio (cambia el flujo de generacion) |
| D3-C: Documentar y dejar | El flag es cosmetico. El checker funciona correctamente a nivel de gate individual. Documentar el gap en el docstring y seguir. | 1 linea | Nulo |

**Recomendacion**: D3-C para AHORA (documentar). D3-A como mejora futura si el flag `site_verification_applied` llega a usarse para decisiones de negocio (ej: "no publicar sin verificacion de sitio"). Actualmente el flag no alimenta ningun gate ni decision — es puramente informativo en el JSON de reporte.

---

## ANALISIS DE IMPACTO

| Hallazgo | Afecta output del cliente? | Afecta gates? | Afecta scores? | Urgencia |
|----------|---------------------------|---------------|----------------|----------|
| D1 | No (solo mensaje de error interno) | No | No | Cuando convenga |
| D2 | No (solo documentacion de plan) | No | No | Cuando se toque el plan |
| D3 | No (flag cosmetico en JSON) | No | No | Si el flag se vuelve funcional |

---

## RECOMENDACION FINAL

**No abrir una fase dedicada ahora.** Los 3 hallazgos son de severidad BAJA y no afectan la publicacion ni la calidad del output para el cliente. Se recomienda:

1. Incluir D1-A y D2-A como tareas "bonus" en la PROXIMA fase de mantenimiento que toque `coherence_validator.py` o los planes de SOL-2.
2. Para D3, simplemente documentar el gap en el docstring de `v4_asset_orchestrator.py` L144 (1 linea: `# NOTE: site_verification_applied reflects orchestrator-level skips, not gate-level checks. See SOL-2-D3.`).

Si en el futuro el flag `site_verification_applied` se vuelve requisito funcional (ej: un gate que bloquee publicacion sin verificacion), entonces implementar D3-A.

---

## COMO INICIAR EN NUEVA SESION

```
Carga .opencode/context/06_SOL-2_DESIGN_FINDINGS_20260507.md.
Evalua los 3 hallazgos D1/D2/D3 y decide cuales implementar.
Si decides implementar, siguiendo .agents/workflows/phased_project_executor.md ejecuta UNA micro-fase
(sin v4complete, max 30 iteraciones). Si no, simplemente documenta la decision.
```

---

## REFERENCIAS CRUZADAS

- Plan SOL-2: `.opencode/plans/SOL-2-REFACTOR/`
- Codigo D1: `modules/commercial_documents/coherence_validator.py:494-555`
- Codigo D3: `modules/asset_generation/v4_asset_orchestrator.py:144-145`
- Codigo D3 (gate): `modules/quality_gates/publication_gates.py:768-817`
- Evidencia E2E: `evidence/FASE-SOL2-C/analisis_ejecucion.md`
- CHANGELOG: `CHANGELOG.md` seccion `[4.42.0]`
