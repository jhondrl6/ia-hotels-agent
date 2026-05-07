---
description: FASE-PATCH-C — Verificacion E2E con v4complete (Termales Santa Rosa de Cabal)
version: 1.0.0
plan: PROP-PATCH
---

# FASE-PATCH-C: Verificacion E2E con v4complete

**ID**: PATCH-C  
**Objetivo**: Ejecutar v4complete para Termales Santa Rosa de Cabal y verificar que los fixes de PATCH-A y PATCH-B resuelven los gaps detectados  
**Dependencias**: PATCH-A ✅, PATCH-B ✅  
**Duracion estimada**: 1.5-2 horas (incluye 5-10 min de v4complete)  
**Skill**: phased_project_executor v2.10.0  
**Iteraciones max**: 60  
**⚠️ CONTIENE COMANDO LARGO**

---

## Contexto

Esta fase ejecuta el flujo completo v4complete para el hotel Termales Santa Rosa de Cabal (http://www.termales.com.co/) y verifica que:

1. El coherence score del YAML header coincide con el del gate_report (SOL-1).
2. La propuesta no promete servicios sin assets (SOL-2).
3. El disclaimer Tier C es visible (SOL-3).
4. El price_matches_pain tiene score razonable (SOL-4).

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| PROP-A — G | ✅ Completadas |
| PATCH-A | ✅ Completada (fixes de coherencia y precio aplicados) |
| PATCH-B | ✅ Completada (alineacion de assets y disclaimers aplicados) |
| PATCH-C | 🔵 En Progreso |
| PATCH-RELEASE | ⏳ Pendiente |

### Base Tecnica Disponible

- Fixes aplicados en `main.py` y `coherence_validator.py` (PATCH-A)
- Fixes aplicados en `proposal_generator.py` y `proposal_asset_alignment.py` (PATCH-B)
- URL: `http://www.termales.com.co/`
- Comando: `./venv/Scripts/python.exe main.py v4complete --url http://www.termales.com.co/`

---

## Tareas

### T1: Ejecutar v4complete para Termales

**Objetivo**: Generar diagnostico, propuesta y assets para Termales con los fixes aplicados.

**Comando**:
```bash
./venv/Scripts/python.exe main.py v4complete --url http://www.termales.com.co/
```

**Protocolo de ejecucion**:
1. Ejecutar via `terminal(timeout=600, notify_on_complete=True)` o via subagente `delegate_task`.
2. Si se usa subagente:
   ```python
   delegate_task(
       goal="Ejecutar v4complete para Termales Santa Rosa de Cabal",
       context="URL: http://www.termales.com.co/\nComando: ./venv/Scripts/python.exe main.py v4complete --url http://www.termales.com.co/\nExpected: diagnostico, propuesta, assets, coherence >= 0.80",
       toolsets=["terminal"]
   )
   ```
3. Monitorear por errores de ejecucion.

**Criterios de aceptacion**:
- [ ] Comando termina sin excepciones no controladas
- [ ] Archivos generados en `output/v4_complete/termales/`
- [ ] `coherence_validation.json` existe
- [ ] `gate_report_*.json` existe

---

### T2: Evidencia Proactiva (OBLIGATORIO)

**Objetivo**: Copiar archivos criticos inmediatamente despues de la generacion, antes de cualquier verificacion.

**Comandos**:
```bash
mkdir -p evidence/FASE-PATCH-C/
cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/FASE-PATCH-C/
cp output/v4_complete/02_PROPUESTA_*.md evidence/FASE-PATCH-C/
cp output/v4_complete/termales/v4_audit/*.json evidence/FASE-PATCH-C/
```

**Criterios de aceptacion**:
- [ ] Directorio `evidence/FASE-PATCH-C/` creado
- [ ] Al menos 2 archivos .md copiados
- [ ] Al menos 3 archivos .json copiados

---

### T3: Verificar SOL-1 — Coherence Score Unificado

**Objetivo**: Confirmar que el YAML header y el gate_report usan el mismo coherence score.

> **Leccion de PROP-A**: Los tests unitarios no detectaron la divergencia. Es obligatorio verificar INTEGRACION: YAML vs gate_report para un hotel real. Tolerancia < 0.01.

**Pasos**:
1. Leer YAML header del diagnostico: buscar `coherence_score:`.
2. Leer `evidence/FASE-PATCH-C/gate_report_*.json`: buscar `gate_name: "coherence"` → `value`.
3. Comparar: deben coincidir con tolerancia < 0.01.
4. Verificar `gate_status` en YAML: debe coincidir con `status` en gate_report.
5. **SI NO COINCIDEN**: el fix de SOL-1 fallo. No continuar a T4. Reportar en `dependencias-fases.md` como incompleta.

**Criterios de aceptacion**:
- [ ] `coherence_score_yaml == gate_report_coherence_value` (diferencia < 0.01)
- [ ] `gate_status_yaml == gate_report_coherence_status`
- [ ] Divergencia = 0 (vs 2.67 pts pre-fix)
- [ ] **Si divergencia > 0.01**: marcar PATCH-C como ⏳ INCOMPLETA, documentar valores reales

---

### T4: Verificar SOL-2, SOL-3, SOL-4

**Objetivo**: Validar que los fixes de PATCH-A y PATCH-B se reflejan en el output.

**Pasos**:
1. **SOL-2**: Leer `gate_report_*.json` → `proposal_asset_alignment` → `missing_count` debe ser 0.
2. **SOL-3**: Leer propuesta `02_PROPUESTA_*.md` → buscar disclaimer Tier C (texto sobre benchmarks regionales).
3. **SOL-4**: Leer `coherence_validation.json` → buscar `price_matches_pain` → `score` debe ser >= 0.4.

**Criterios de aceptacion**:
- [ ] `proposal_asset_alignment.missing_count == 0`
- [ ] Disclaimer Tier C visible en propuesta
- [ ] `price_matches_pain.score >= 0.4`

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| E2E v4complete | `main.py v4complete` | Termina sin errores criticos |
| Coherence unificada | YAML vs gate_report | Divergencia 0 |
| Assets alineados | gate_report JSON | missing_count 0 |

**Comando de validacion**:
```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecucion (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`**
   - Marcar PATCH-C como ✅ Completada

2. **`06-checklist-implementacion.md`**
   - Marcar tareas de PATCH-C como completadas

3. **`09-documentacion-post-proyecto.md`**
   - **Seccion D**: Actualizar metricas con valores reales de esta ejecucion
   - **Seccion F**: Anotar cualquier anomalia observada

4. **`log_phase_completion.py`**:
   ```bash
   ./venv/Scripts/python.exe scripts/log_phase_completion.py \
       --fase PATCH-C \
       --desc "Verificacion E2E con v4complete para Termales Santa Rosa de Cabal" \
       --check-manual-docs
   ```

---

## Criterios de Completitud (CHECKLIST)

- [ ] **v4complete ejecutado**: Sin errores criticos
- [ ] **Evidencia preservada**: Archivos en `evidence/FASE-PATCH-C/`
- [ ] **Coherence unificada**: YAML == gate_report
- [ ] **Assets alineados**: missing_count == 0
- [ ] **`dependencias-fases.md` actualizado**: Estado PATCH-C marcado
- [ ] **Post-ejecucion completada**: Todos los puntos realizados

---

## Restricciones

- **Maximo 60 iteraciones**
- **NO modificar codigo fuente** en esta fase (solo verificacion)
- **NO ejecutar v4complete sin `notify_on_complete=True` o subagente**
- **NO omitir evidencia proactiva** (T2 es obligatoria antes de T3/T4)
- Si v4complete falla por timeout/API: guardar logs y reportar en `dependencias-fases.md` como incompleta
