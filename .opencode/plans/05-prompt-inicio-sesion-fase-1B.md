# FASE-1B: Ejecutar v4complete + Verificar Propuesta Corregida

**ID**: FASE-1B  
**Objetivo**: Ejecutar v4complete para Amaziliahotel y verificar que la propuesta muestra estado correcto de entregables  
**Dependencias**: FASE-1A ✅ Completada  
**Duracion estimada**: ~20-30 min (la mayor parte es tiempo de v4complete)  
**Skill**: iah-cli-phased-execution  
**Estado**: ⚠️ PARCIAL —发达的 fixes aplicados, re-ejecutar para completar

---

## Contexto

FASE-1A cerró la cadena de llamadas para site_presence_report. FASE-1B se ejecutó parcialmente:
- v4complete completó ✅
- Estados de entregables en propuesta: CORRECTOS ✅
- 5/7 bugs "COP COP" corregidos ⚠️
- Gate content_quality: BLOQUEADO — pendiente de re-ejecutar

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-1A | ✅ Completada (código implementado + tests pasando) |

### Base Técnica Disponible

- v4_proposal_generator.py: call chain cerrado con site_presence_report
- main.py: SitePresenceChecker invocado antes de generar propuesta
- Tests: 2248+ pasando, 0 regresiones

---

## Tareas

### Tarea 1: Terminar fixes "COP COP" en propuesta_v6_template.md (PENDIENTE)

**Archivos ya corregidos:**
- `v4_diagnostic_generator.py` L705: `COP/mes` → `/mes` ✅
- `diagnostico_v6_template.md` L75, L80, L102, L125 ✅

**Archivo con fixes pendientes en `modules/commercial_documents/templates/propuesta_v6_template.md`:**

```bash
# Verificar instances pendientes
grep -n "COP\b" modules/commercial_documents/templates/propuesta_v6_template.md
```

**Fixes pendientes:**
| Línea | Antes | Después |
|-------|-------|---------|
| ~30 | `${monthly_loss} COP` | `${monthly_loss}` |
| ~95-97 | `${total_investment} COP`, `${total_recovered} COP`, `${net_benefit} COP` | sin COP |

### Tarea 2: Fix "0% de confianza" en diagnóstico (PENDIENTE)

**Ubicación**: Diagnóstico generado, línea ~186
**Patrón**: "0% de confianza"
**Fix**: Buscar en `v4_diagnostic_generator.py` y corregir el texto que genera ese enunciado

```bash
# Buscar el origen
grep -rn "0% de confianza\|0%.*confianza" modules/commercial_documents/
```

### Tarea 3: Fix estructural — ContentScrubber post-T4FIX (PENDIENTE)

**Problema raíz**: El gate `content_quality` valida el diagnóstico STALE (antes de T4FIX). ContentScrubber nunca se ejecuta sobre el diagnóstico final.

**Flujo actual**:
1. FASE 3.6: ContentScrubber → diagnóstico no existe → [SKIP]
2. FASE 4: Assets
3. T4FIX: Regenera diagnóstico
4. FASE 3.5: Propuesta
5. FASE 4.5: Publication Gates → valida diagnóstico STALE

**Solución A (recomendada)**: Mover el bloque ContentScrubber a DESPUÉS de T4FIX en main.py, antes de FASE 4.5

**Búsqueda en main.py**:
```bash
grep -n "T4FIX\|FASE.*4\.5\|ContentScrubber\|diagnostic_path = diagnostic_gen.generate" main.py
```

**Zona crítica** (~L2397-2440): después de `diagnostic_path = diagnostic_gen.generate()` y antes de `run_publication_gates()` (~L2605)

### Tarea 4: Re-ejecutar v4complete (PENDIENTE)

```bash
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/
```

**Criterios de aceptación:**
- `content_quality: PASSED` en gate_report.json
- `publication_ready: true`
- 0 "COP COP" en output final

### Tarea 5: Verificación post-ejecución (OBLIGATORIO)

```bash
# Verificar gate
cat output/v4_complete/gate_report.json | grep -E '"content_quality"|"status": "NOT_READY"|"status": "READY"'

# Verificar ausencia de COP COP
grep -rn "COP COP" output/v4_complete/01_DIAGNOSTICO_*.md output/v4_complete/02_PROPUESTA_*.md

# Guardar evidencia
mkdir -p evidence/fase-1b-amazilia-verificacion/
cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/fase-1b-amazilia-verificacion/
cp output/v4_complete/02_PROPUESTA_*.md evidence/fase-1b-amazilia-verificacion/
cp output/v4_complete/gate_report.json evidence/fase-1b-amazilia-verificacion/
```

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar FASE-1B como ✅ Completada
2. **`REGISTRY.md`**: via `log_phase_completion.py`
3. **`sync_versions.py --check`**: verificar sync

---

## Criterios de Completitud (CHECKLIST)

- [ ] 5 fixes "COP COP" aplicados en generator + templates
- [ ] "0% de confianza" eliminado del diagnóstico
- [ ] ContentScrubber re-ejecutado post-T4FIX
- [ ] v4complete re-ejecutado sin errores
- [ ] `content_quality: PASSED` en gate_report.json
- [ ] `publication_ready: true`
- [ ] evidencia guardada en evidence/fase-1b-amazilia-verificacion/
- [ ] dependencias-fases.md actualizado

---

## Restricciones

- **Máximo 60 iteraciones** del agente
- **NO ejecutar docs cascade** — eso es FASE-1C
- Si v4complete falla, guardar logs en evidence/ y reportar  

---

## Contexto

FASE-1A cerro la cadena de llamadas para site_presence_report. Ahora necesitamos:
1. Ejecutar v4complete para generar una propuesta nueva
2. Verificar que los estados de entregables son correctos
3. Guardar evidencia

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-1A | ✅ Completada (codigo implementado + tests pasando) |

### Base Tecnica Disponible

- v4_proposal_generator.py: call chain cerrado con site_presence_report
- main.py: SitePresenceChecker invocado antes de generar propuesta
- Tests: 2248+ pasando, 0 regresiones

---

## Tareas

### Tarea 1: Ejecutar v4complete

**Objetivo**: Generar diagnostico + propuesta + assets para Amaziliahotel con el codigo corregido

**Comando**:
```bash
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/
```

**Presupuesto de iteraciones**:
- Gastos fijos: ~26 (leer plan, verificar estado, guardar evidencia, docs)
- Disponible: ~34 iteraciones
- v4complete cuenta como 1 tool call con timeout=600
- **Ejecutar DIRECTAMENTE** con `terminal(timeout=600, notify_on_complete=True)` (sobran >30 iteraciones para post-trabajo)

**Criterios de aceptacion**:
- [ ] v4complete ejecuta sin errores fatales
- [ ] Genera 01_DIAGNOSTICO + 02_PROPUESTA + assets

### Tarea 2: Guardar Evidencia Proactiva (OBLIGATORIO inmediatamente)

**Objetivo**: Preservar los archivos criticos antes de cualquier verificacion

**Comandos**:
```bash
mkdir -p evidence/fase-1b-amazilia-verificacion/
cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/fase-1b-amazilia-verificacion/
cp output/v4_complete/02_PROPUESTA_*.md evidence/fase-1b-amazilia-verificacion/
cp output/v4_complete/amaziliahotel/v4_audit/*.json evidence/fase-1b-amazilia-verificacion/ 2>/dev/null || true
cp output/v4_complete/v4_complete_report.json evidence/fase-1b-amazilia-verificacion/ 2>/dev/null || true
```

**Regla**: Esto se ejecuta INMEDIATAMENTE despues de que v4complete termine, ANTES de cualquier verificacion.

### Tarea 3: Verificar Propuesta contra Criterios

**Objetivo**: Confirmar que la propuesta muestra estados correctos

**Verificar en 02_PROPUESTA_COMERCIAL_*.md**:

| Servicio | Estado Esperado | Texto Esperado |
|----------|----------------|----------------|
| Boton de WhatsApp | ✅ Verificado en sitio | "Ya existe en su web" o similar |
| Datos Estructurados | ⚠️ Listo para implementar | No dice "Completo" (schema_valid=false) |
| Pagina de FAQ | ⚠️ Listo para implementar | No dice "Completo" (faq_schema_valid=false) |

**Verificaciones adicionales**:
- [ ] coherence_score >= 0.80
- [ ] No hay "COP COP" (moneda duplicada)
- [ ] No hay "0% de confianza"
- [ ] publication_ready = true

**Criterios de aceptacion**:
- [ ] WhatsApp: muestra "Verificado en sitio" o "Ya existe"
- [ ] Datos Estructurados: NO muestra "Completo" (schema_valid=false)
- [ ] FAQ: NO muestra "Completo" (faq_schema_valid=false)
- [ ] coherence_score >= 0.80

---

## Post-Ejecucion (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar FASE-1B como ✅ Completada con fecha
2. **`README.md`**: Actualizar tabla de progreso
3. **`evidence/fase-1b-amazilia-verificacion/`**: Ya guardada en Tarea 2

---

## Criterios de Completitud (CHECKLIST)

- [ ] v4complete ejecutado sin errores
- [ ] Evidencia guardada en evidence/fase-1b-amazilia-verificacion/
- [ ] WhatsApp muestra "Verificado en sitio" (no "Incluido en su kit")
- [ ] Datos Estructurados NO muestra "Completo"
- [ ] FAQ NO muestra "Completo"
- [ ] coherence >= 0.80
- [ ] dependencias-fases.md actualizado

---

## Restricciones

- **Maximo 60 iteraciones** del agente
- **NO modificar codigo fuente** — solo ejecutar v4complete y verificar
- **NO ejecutar docs cascade** — eso es FASE-1C
- **Evidencia proactiva es OBLIGATORIA** antes de cualquier verificacion
- Si v4complete falla, guardar logs de error en evidence/ y reportar

## Protocolo de Recuperacion

Si v4complete falla o se agota:
1. Guardar cualquier output parcial en evidence/fase-1b-amazilia-verificacion/
2. Actualizar dependencias-fases.md: "⏳ INCOMPLETA — v4complete fallo: [razon]"
3. Nueva sesion: reintentar desde Tarea 1 (v4complete es idempotente)
