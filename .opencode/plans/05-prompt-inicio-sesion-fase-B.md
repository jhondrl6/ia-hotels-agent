# FASE-B: v4complete Hotel Castilla Real + Verificación Advisory Warnings

**ID**: FASE-B
**Objetivo**: Ejecutar v4complete para Hotel Castilla Real y verificar que los advisory warnings implementados en FASE-A aparecen correctamente en el output
**Dependencias**: FASE-A ✅ (código de advisory warnings debe estar implementado)
**Duración estimada**: 2-3 horas (v4complete tarda 5-10 min)
**Skill**: `iah-cli-phased-execution`

---

## Contexto

FASE-A implementó:
1. Alerta advisory en DIAGNOSTICO.md cuando IA-Readiness < 50
2. Campo `advisory_warnings` en `delivery_quality_report.json`

Esta fase verifica que ambas funcionalidades funcionan correctamente en un caso real: **Hotel Castilla Real** (https://www.hotelcastillareal.com/).

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada (asumido al iniciar esta fase) |

### Base Técnica Disponible
- FASE-A implementada: `v4_diagnostic_generator.py`, `delivery_quality_report.py` modificados
- Tests de FASE-A pasan
- URL del hotel: https://www.hotelcastillareal.com/

---

## Tareas

### T1: Ejecutar v4complete para Hotel Castilla Real
**Objetivo**: Generar diagnóstico completo, propuesta, assets y reportes para el hotel

**Comando**:
```bash
./venv/Scripts/python.exe main.py v4complete --url https://www.hotelcastillareal.com/
```

**⚠️ REGLA DE EJECUCIÓN**: Usar `delegate_task` con timeout=900 y notify_on_complete=True. Ver `iah-cli-phased-execution` skill §Protocolo de Subagente para v4complete.

**Criterios de aceptación**:
- [ ] v4complete termina sin errores fatales
- [ ] Se genera `DIAGNOSTICO.md` en `output/v4_complete/`
- [ ] Se genera `PROPUESTA.md` en `output/v4_complete/`
- [ ] Se generan assets en `output/v4_complete/{hotel_id}/`
- [ ] Se genera `delivery_quality_report.json`
- [ ] Coherence score ≥ 0.80 (pasa el gate)

---

### T2: Verificar advisory warning en DIAGNOSTICO.md
**Objetivo**: Confirmar que la alerta IA-Readiness aparece en el diagnóstico si el score es < 50

**Verificación**:
1. Leer `output/v4_complete/01_DIAGNOSTICO_*.md`
2. Buscar sección `### Métricas de Acceso para IA`
3. Verificar si el score IA-Readiness es < 50
4. Si < 50: verificar que aparece el bloquequote:
   ```
   > ⚠️ **Alerta IA-Readiness Critical**: este score no bloquea la entrega...
   ```
5. Si ≥ 50: verificar que NO aparece el bloquequote de alerta

**Criterios de aceptación**:
- [ ] Documento contiene sección `### Métricas de Acceso para IA`
- [ ] La alerta advisory aparece SI Y SOLO SI el score es < 50
- [ ] La alerta está en formato blockquote (`> ⚠️`)
- [ ] La tabla de métricas sigue presente y completa

---

### T3: Verificar advisory warning en delivery_quality_report.json
**Objetivo**: Confirmar que el campo `advisory_warnings` existe y contiene la entrada correcta

**Verificación**:
1. Leer `output/v4_complete/{hotel_id}/v4_audit/delivery_quality_report.json`
2. Verificar que existe campo `advisory_warnings`
3. Si IA-Readiness es Critical: verificar que contiene:
   ```json
   {
     "code": "IA_READINESS_CRITICAL",
     "severity": "WARNING",
     "blocking": false,
     "message": "IA-Readiness Critical: ..."
   }
   ```
4. Verificar que `status` del reporte NO es `FAIL` por causa de advisory warnings
5. Verificar que ZIP no fue abortado por advisory warnings

**Criterios de aceptación**:
- [ ] `delivery_quality_report.json` existe
- [ ] Campo `advisory_warnings` presente (lista, aunque vacía)
- [ ] Si IA-Readiness Critical → contiene `IA_READINESS_CRITICAL` con `blocking: false`
- [ ] `status` no es `FAIL` por advisory warnings
- [ ] ZIP se generó correctamente (si aplica)

---

### T4: Análisis de ejecución y documentación
**Objetivo**: Documentar resultados de la verificación y generar reporte de análisis

**Entregable**: Nota de análisis en `evidence/fase-B/analysis.md` con:
- Score IA-Readiness obtenido para Hotel Castilla Real
- ¿Apareció la alerta en diagnóstico? (sí/no y por qué)
- ¿Apareció advisory_warning en delivery_quality_report? (sí/no y por qué)
- ¿Coherence score pasó el gate?
- Observaciones sobre el comportamiento del pipeline

**Criterios de aceptación**:
- [ ] Análisis documentado en `evidence/fase-B/analysis.md`
- [ ] Evidencia copiada a `evidence/fase-B/` (DIAGNOSTICO.md, PROPUESTA.md, delivery_quality_report.json)
- [ ] Conclusión clara: ¿los advisory warnings funcionan correctamente?

---

## Tests Obligatorios

| Verificación | Método | Criterio |
|-------------|--------|----------|
| Alerta en diagnóstico | Leer DIAGNOSTICO.md | Bloquequote presente si score < 50 |
| advisory_warnings en JSON | Leer delivery_quality_report.json | Campo existe, entry correcta |
| ZIP no bloqueado | Verificar output | ZIP generado a pesar de advisory |
| Coherence gate | Leer coherence_validation.json | Score ≥ 0.80 |

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

```bash
# 1. Guardar evidencia (OBLIGATORIO - inmediatamente después de v4complete)
mkdir -p evidence/fase-B
cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/fase-B/
cp output/v4_complete/02_PROPUESTA_*.md evidence/fase-B/
cp output/v4_complete/*/v4_audit/delivery_quality_report.json evidence/fase-B/ 2>/dev/null || true
cp output/v4_complete/*/v4_audit/coherence_validation.json evidence/fase-B/ 2>/dev/null || true

# 2. Registrar en REGISTRY.md
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-B \
    --desc "v4complete Hotel Castilla Real + verificación advisory warnings" \
    --archivos-mod "evidence/fase-B/analysis.md" \
    --tests "0" \
    --coherence 0.80 \
    --check-manual-docs

# 3. Actualizar dependencias-fases.md (FASE-B → ✅)
# 4. Actualizar 09-documentacion-post-proyecto.md (Sección A, B, D, E)
# 5. Actualizar 06-checklist-implementacion.md
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] T1: v4complete ejecutado exitosamente para Hotel Castilla Real
- [ ] T2: Alerta en diagnóstico verificada (presente/ausente según score)
- [ ] T3: advisory_warnings en delivery_quality_report.json verificado
- [ ] T4: Análisis de ejecución documentado en `evidence/fase-B/analysis.md`
- [ ] Evidencia copiada a `evidence/fase-B/`
- [ ] `dependencias-fases.md` actualizado (FASE-B → ✅)
- [ ] `09-documentacion-post-proyecto.md` actualizado
- [ ] `log_phase_completion.py` ejecutado

---

## Restricciones

- **NO modificar código fuente** en esta fase (solo verificación)
- **NO modificar ROADMAP.md**
- **NO ejecutar más de 1 v4complete** (regla R3: máximo 1 comando largo por fase)
- **Máximo 60 iteraciones del agente**
- **Guardar evidencia ANTES de cualquier verificación** (Protocolo de Evidencia Proactiva)
- **Si el agente se agota**, la evidencia ya está a salvo en `evidence/fase-B/`
