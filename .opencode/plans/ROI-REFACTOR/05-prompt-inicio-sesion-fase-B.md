# FASE-B: Jerga técnica + Entregables

**ID**: FASE-B
**Objetivo**: Traducir jerga técnica a lenguaje de negocio + cambiar tabla de entregables de "% confianza" a "Momento de entrega".
**Dependencias**: FASE-1 (ex-FASE-A) — bloqueantes de output. ⬜ Puede ejecutarse en paralelo con FASE-1 si es urgente (archivos distintos). **FASE-0 completada (Opción E)** — decisión comercial registrada en `09-documentacion-post-proyecto.md` §F.
**Duración estimada**: 1-2 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

El ROI_AUDIT.md identificó dos problemas de credibilidad que sobrevivieron al plan PROPUESTA-COMERCIAL:

1. **Jerga técnica sin traducir (Fix 4)**: El gate `CG-TECH-JARGON` en `commercial_gate.py` ya detecta términos como WARNING, pero la FASE-D de PROPUESTA-COMERCIAL solo expandió la lista de términos detectados — NO los tradujo en el output. El cliente sigue viendo "AEO", "UTMs", "P1/P2/P3".

2. **Tabla de entregables con % confianza (Fix 5)**: `_generate_asset_quality_table()` muestra "⚠️ 50% confianza" y estados de incertidumbre. El ROI_AUDIT recomienda cambiar a "Momento de entrega" con fechas concretas.

### Evidencia en código

```markdown
<!-- output actual — línea 75: "Nota sobre AEO: AEO (Answer Engine Optimization)..." -->
<!-- output actual — línea 162: "UTMs, conversiones" -->

<!-- Template L46, L67-69: entregables con % confianza -->
| Schema Hotel | ⚠️ Listo para implementar | Requiere confirmacion post-firma |
| Página FAQ   | En proceso de activación  | Datos pendientes del cliente     |
```

---

## Tareas

### Tarea 1: Traducir AEO, UTMs, P1/P2/P3 en template

**Archivo**: `modules/commercial_documents/templates/propuesta_v6_template.md`

**Términos a reemplazar**:

| Término actual | Reemplazo | Dónde aparece |
|----------------|-----------|---------------|
| "AEO (Answer Engine Optimization)" | "Optimización para asistentes de voz (Siri, Alexa, Google Assistant)" | Nota en output |
| "UTMs, conversiones" | "Sistema de rastreo para medir de dónde viene cada reserva" | Plan 7/30/60/90 |
| "P1 / P2 / P3" | "Fase 1: WhatsApp y datos para IA", "Fase 2: Contenido y FAQs", "Fase 3: Guías locales" | Plan de fases |

**NOTA**: El gate `CG-TECH-JARGON` en `commercial_gate.py:84-91` YA detecta estos términos como WARNING. No modificar el gate — solo traducir en el template.

**Criterios de aceptación**:
- [ ] Ningún output contiene "AEO" sin explicación en lenguaje de negocio
- [ ] "UTMs" reemplazado por descripción funcional
- [ ] "P1/P2/P3" reemplazados por nombres descriptivos

### Tarea 2: Cambiar tabla de entregables a "Momento de entrega"

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py` — método `_generate_asset_quality_table()` (L1190+)

**Cambio conceptual**:

```markdown
<!-- ANTES (columnas) -->
| Entregable | Estado | Nota |

<!-- DESPUÉS (columnas) -->
| Entregable | Momento de entrega | Qué incluye |
```

**Mapeo de estados**:

| Estado actual | Nuevo "Momento de entrega" |
|---------------|---------------------------|
| "⚠️ Listo para implementar" | "Día 1 (Activación inicial)" |
| "En proceso de activación — Semana 2" | "Semana 2 (Configuración)" |
| "Requiere confirmación post-firma" | "Semana 1 (Con sus datos)" |
| Cualquier % confianza | ELIMINAR — no mostrar % |

**Paso 2.1**: Ubicar `_generate_asset_quality_table()` en L1190 del generator

**Paso 2.2**: Cambiar headers de columna: "Estado" → "Momento de entrega", "Nota" → "Qué incluye"

**Paso 2.3**: Mapear los valores de estado a fechas concretas según el tipo de asset

**Paso 2.4**: Eliminar cualquier referencia a porcentajes de confianza en esta tabla

**Criterios de aceptación**:
- [ ] Headers: "Entregable | Momento de entrega | Qué incluye"
- [ ] Sin "% confianza" en el output
- [ ] Fechas concretas (Día N, Semana N) en vez de "En preparación"
- [ ] Consistente con el Plan 7/30/60/90

---

## Tests Obligatorios

| Test | Comando | Criterio |
|------|---------|----------|
| Validación rápida | `python3 scripts/run_all_validations.py --quick` | 3/5+ checks pass |
| Import test | `python3 -c "from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator; print('OK')"` | OK |
| CG-TECH-JARGON | `python3 -c "from modules.quality_gates.commercial_gate import CommercialGateValidator; print('OK')"` | OK — gate intacto |

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`**: Marcar FASE-B como ✅ Completada
2. **`06-checklist-implementacion.md`**: Marcar items B1-B2 como ✅
3. **`09-documentacion-post-proyecto.md`**: Agregar cambios en Secciones A y B
4. Ejecutar:
```bash
cmd.exe /c "venv\Scripts\python.exe scripts\log_phase_completion.py \
    --fase FASE-B \
    --desc \"ROI-REFACTOR: Traducir AEO/UTMs/P1-P3 + cambiar tabla entregables a Momento de entrega\" \
    --archivos-mod \"modules/commercial_documents/templates/propuesta_v6_template.md,modules/commercial_documents/v4_proposal_generator.py\" \
    --tests 0 \
    --check-manual-docs"
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] "AEO" reemplazado por descripción de negocio en template
- [ ] "UTMs" reemplazado por descripción funcional
- [ ] "P1/P2/P3" reemplazados por "Fase 1/2/3" con nombres descriptivos
- [ ] Tabla de entregables: headers "Momento de entrega" + "Qué incluye"
- [ ] Sin % confianza en tabla de entregables
- [ ] `run_all_validations.py --quick` pasa
- [ ] `dependencias-fases.md` actualizado
- [ ] `06-checklist-implementacion.md` actualizado
- [ ] `09-documentacion-post-proyecto.md` actualizado
- [ ] `log_phase_completion.py` ejecutado

---

## Restricciones

- NO modificar `commercial_gate.py` (el gate funciona bien)
- NO ejecutar v4complete
- NO modificar `_generate_asset_quality_table()` fuera de los headers y mapeo de estados
- NO eliminar la tabla completa — solo reformatear
- Máximo 60 iteraciones de agente
