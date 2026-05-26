# FASE-F: v4complete Hotel Castilla Real + Análisis Post-Implementación por Niveles

**ID**: FASE-F
**Objetivo**: Ejecutar v4complete para Hotel Castilla Real con todos los fixes aplicados (FASE-A a FASE-E) y verificar que los 5 niveles de la auditoría son superados.
**Dependencias**: FASE-A, FASE-B, FASE-C, FASE-D, FASE-E (TODAS completadas)
**Duración estimada**: 1-2 horas (ejecución) + 1 hora (análisis)
**Skill**: `iah-cli-phased-execution`
**Tipo**: Ejecución (3 tareas + 1 comando largo)

---

## Contexto

Después de 5 fases de implementación (A-E), todos los hallazgos de la auditoría `Propuesta.md` deben estar corregidos. Esta fase ejecuta v4complete y verifica que el output generado para Hotel Castilla Real supera los 5 niveles de calidad definidos en la auditoría.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada (asumido) |
| FASE-B | ✅ Completada (asumido) |
| FASE-C | ✅ Completada (asumido) |
| FASE-D | ✅ Completada (asumido) |
| FASE-E | ✅ Completada (asumido) |

### Baseline de Referencia

| Métrica | Valor Pre-Fixes |
|---------|----------------|
| Coherence Score | 0.83 |
| Publication Gates | 9/11 (2 warnings) |
| Gap diagnóstico↔propuesta | 12:1 (fuga bruta vs recuperación) |
| Brecha→servicio mapping | Inexistente |
| CG-ROI-NEGATIVE | Desincronizado |

---

## Tareas

### Tarea 1: Ejecutar v4complete para Hotel Castilla Real

**Comando**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli && \
  ./venv/Scripts/python.exe main.py v4complete --url https://www.hotelcastillareal.com/
```

**Timeout**: 900 segundos (15 minutos)
**Ejecución**: `delegate_task` para no bloquear el agente principal.

**Criterios de aceptación**:
- [ ] v4complete termina sin errores fatales
- [ ] Se generan `01_DIAGNOSTICO_*.md` y `02_PROPUESTA_*.md`
- [ ] Se generan 12 assets en `hotelcastillareal/`
- [ ] `v4_complete_report.json` generado
- [ ] `coherence_validation.json` generado

### Tarea 2: Copiar evidencia a `evidence/FASE-F/`

**Inmediatamente después del v4complete** (los outputs pueden ser sobrescritos):

```bash
mkdir -p evidence/FASE-F/v4_audit
cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/FASE-F/
cp output/v4_complete/02_PROPUESTA_*.md evidence/FASE-F/
cp output/v4_complete/hotelcastillareal/v4_audit/*.json evidence/FASE-F/v4_audit/
cp output/v4_complete/hotelcastillareal/coherence_validation.json evidence/FASE-F/
cp output/v4_complete/hotelcastillareal/gate_report_*.json evidence/FASE-F/
cp output/v4_complete/v4_complete_report.json evidence/FASE-F/
```

**Criterios de aceptación**:
- [ ] Todos los archivos copiados exitosamente
- [ ] `evidence/FASE-F/` contiene diagnóstico, propuesta, assets JSONs, gate report

### Tarea 3: Crear análisis post-implementación por niveles

**Archivo**: `evidence/FASE-F/analisis_post_implementacion.md`

**Estructura del análisis**:

```markdown
# Análisis Post-Implementación — Hotel Castilla Real
# PROPUESTA-COMERCIAL (v4.53.0)

## ✅ Nivel 1 — Bloqueantes (Cross-documento)

### CROSS-1: Puente dual fuga bruta / recuperación efectiva
- **Esperado**: Ambos documentos muestran fuga total ($22.4M) + recuperación proyectada ($1.8M) con explicación 41% × 20%
- **Real**: [VERIFICAR EN OUTPUT]
- **Estado**: ✅/❌

### CROSS-2: Mapping brecha→servicio
- **Esperado**: Cada servicio en propuesta referencia su brecha del diagnóstico
- **Real**: [VERIFICAR EN OUTPUT]
- **Estado**: ✅/❌

### CODE-1/3/4: Variables financieras unificadas
- **Esperado**: recovered_6m = total_recovered = effective_monthly_gain × 6
- **Real**: [VERIFICAR EN OUTPUT]
- **Estado**: ✅/❌

### CODE-2: Gate CG-ROI-NEGATIVE sincronizado
- **Esperado**: Gate y tabla ROI usan misma base (effective_monthly_gain)
- **Real**: [VERIFICAR EN gate_report]
- **Estado**: ✅/❌

## ✅ Nivel 2 — Código (Contradicciones internas)

### Consistencia financiera
- **Esperado**: roi_6m, recovered_6m, net_benefit_6m, total_recovered todos coherentes
- **Real**: [VERIFICAR cálculos en output]
- **Estado**: ✅/❌

## ✅ Nivel 3 — Credibilidad

### CROSS-4: WhatsApp conflict reflejado
- **Esperado**: "⚠️ Requiere corrección" en propuesta si hay conflicto
- **Real**: [VERIFICAR EN OUTPUT]
- **Estado**: ✅/❌

### V-2: Labels unificados
- **Esperado**: "En proceso de activación — Semana 2" en lugar de "⚠️ En preparación"
- **Real**: [VERIFICAR EN OUTPUT]
- **Estado**: ✅/❌

### V-3: Jerga técnica filtrada
- **Esperado**: Sin OpenRouter, Perplexity, Gemini, etc. en vista gerencia
- **Real**: [VERIFICAR EN OUTPUT]
- **Estado**: ✅/❌

## ✅ Nivel 4 — Paquete comercial

### CROSS-5: Confidence score visible
- **Esperado**: Cada servicio muestra confidence; <0.65 marcado con ⚠️
- **Real**: [VERIFICAR EN OUTPUT]
- **Estado**: ✅/❌

### V-4/5/6: Cupo, garantía, prueba social
- **Esperado**: Cupo justificado, garantía con tracking Día 7, placeholder testimonios
- **Real**: [VERIFICAR EN OUTPUT]
- **Estado**: ✅/❌

## ✅ Nivel 5 — Pulido

### A-3: Sin typos
- **Esperado**: "SIGUIENTE PASO" sin doble S
- **Real**: [VERIFICAR EN OUTPUT]
- **Estado**: ✅/❌

## 📊 Métricas Finales

| Métrica | Pre-Fix | Post-Fix | Delta |
|---------|---------|----------|-------|
| Coherence Score | 0.83 | [MEDIR] | — |
| Publication Gates | 9/11 | [MEDIR] | — |
| Gap fuga/recup | 12:1 sin puente | Con puente dual | — |
| CG-TECH-JARGON | 9 términos | 17 términos | +8 |
| Assets con confidence <0.65 | optimization_guide (0.5) | [MEDIR] | — |

## 🏁 Veredicto Final

**¿Se puede enviar al dueño de Hotel Castillo Real?**
- [RESPUESTA]

**Niveles superados**: X/5
**Niveles pendientes**: [LISTA]
```

**Criterios de aceptación**:
- [ ] Análisis cubre los 5 niveles de la auditoría
- [ ] Cada hallazgo tiene verificación contra el output real
- [ ] Métricas pre-fix vs post-fix documentadas
- [ ] Veredicto final claro (✅ enviable o ❌ no enviable)

---

## Tests Obligatorios

| Test | Comando | Criterio |
|------|---------|----------|
| v4complete exit | Verificar `v4_complete_report.json` | Sin errores fatales |
| Coherence score | Leer `coherence_validation.json` | ≥ 0.80 |
| Publication gates | Leer `gate_report_*.json` | Bloqueantes = 0 |

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar FASE-F como ✅ Completada
2. **`06-checklist-implementacion.md`**: Marcar items F1-F3 como ✅
3. **`09-documentacion-post-proyecto.md`**: Agregar métricas en Sección D, evidencia en Sección C
4. **NO ejecutar `log_phase_completion.py`** — FASE-RELEASE lo hará para todas las fases

---

## Criterios de Completitud (CHECKLIST)

- [ ] v4complete ejecutado exitosamente para hotelcastillareal.com
- [ ] Outputs copiados a `evidence/FASE-F/`
- [ ] Análisis post-implementación creado con verificación de 5 niveles
- [ ] Veredicto final documentado
- [ ] `dependencias-fases.md` actualizado
- [ ] `06-checklist-implementacion.md` actualizado
- [ ] `09-documentacion-post-proyecto.md` actualizado

---

## Restricciones

- NO modificar código — solo ejecutar y analizar
- NO ejecutar `log_phase_completion.py` (eso es para RELEASE)
- El v4complete debe ejecutarse con `delegate_task` (timeout=900)
- Si el v4complete falla, documentar el error y NO marcar la fase como completada
- Máximo 60 iteraciones de agente
