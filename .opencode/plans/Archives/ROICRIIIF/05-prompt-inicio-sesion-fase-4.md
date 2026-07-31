# FASE-4: v4complete Hotel Castilla Real — Verificación E2E Post-Fixes

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: ✅ SUBAGENTE (delegate_task, timeout 900s)
> **Complejidad**: 🟡 MEDIA

## Contexto previo

Las 3 fases anteriores aplicaron todos los fixes necesarios:

| Fix | Issue | Expected Result |
|-----|-------|----------------|
| FASE-1 | Gate no reconoce whatsapp existente | whatsapp_button → present_in_production |
| FASE-2 | Confidence bajo (faq_page/optimization_guide) | Al menos uno ≥ 0.7 |
| FASE-3 | "13%" artifact en propuesta | Texto eliminado/corregido |

**Baseline anterior** (FASE-6 ROICRIII, v4.57.0):
- Coherence: 0.83 pre / 0.81 post
- Proposal alignment: 62.5% → BLOCKED
- Gates: 10/11 (1 blocked: proposal_asset_alignment)
- Publication readiness: NOT_READY

**Target post-fix**:
- Coherence: ≥ 0.80 (mantener)
- Proposal alignment: ≥ 80% (desbloqueado)
- Gates: 11/11 PASSED o 10/11 con solo WARNINGs
- Publication readiness: READY_FOR_PUBLICATION

## Objetivo de esta fase

Ejecutar v4complete para Hotel Castilla Real (https://www.hotelcastillareal.com/) y verificar que los 3 issues fueron superados. Confirmar publication readiness = READY.

### Prompt para delegate_task

```
Eres un agente de ejecución de v4complete para iah-cli.

OBJETIVO: Ejecutar v4complete para Hotel Castilla Real y verificar que publication readiness = READY.

PARÁMETROS:
- URL: https://www.hotelcastillareal.com/
- Región: eje_cafetero
- Working directory: /mnt/c/Users/Jhond/Github/iah-cli/
- Python: venv/Scripts/python.exe (o el venv activo del proyecto)

EJECUCIÓN:
1. Activar venv si es necesario: cd /mnt/c/Users/Jhond/Github/iah-cli/ && source venv/bin/activate
2. Ejecutar v4complete:
   python main.py v4complete --url "https://www.hotelcastillareal.com/" --region "eje_cafetero" --output-dir evidence/roicriiif-fase-4/
   (timeout: 900 segundos, usar notify_on_complete=true si es background)

3. Verificar resultados:
   a) Coherence score ≥ 0.80 (grep coherence en output)
   b) Gate report: proposal_asset_alignment ≥ 80%
   c) whatsapp_button NO en "missing" sino en "aligned" o "present_in_production"
   d) Al menos UNO de {faq_page, optimization_guide} con confidence ≥ 0.7
   e) Propuesta comercial: NO contiene "13% del dolor priorizado" (grep en 02_PROPUESTA_*.md)
   f) Publication readiness: READY_FOR_PUBLICATION (en delivery_quality_report.json)
   g) Gates pasados: 11/11 o al menos sin BLOCKED

4. Guardar evidence:
   - Copiar todos los archivos de salida a evidence/roicriiif-fase-4/
   - gate_report_*.json
   - asset_generation_report.json
   - coherence_validation*.json
   - delivery_quality_report.json
   - 01_DIAGNOSTICO_*.md y 02_PROPUESTA_*.md
   - financial_scenarios_*.json

ENTREGABLES:
- Coherence score (pre y post)
- Proposal alignment percentage
- Publication readiness status
- Gates passed count (X/11)
- Confirmación: whatsapp_button status en gate_report
- Confirmación: confidence de faq_page y optimization_guide
- Confirmación: "13%" grep result en propuesta
- Lista de archivos en evidence/roicriiif-fase-4/
- Si ALGO FALLA: detallar qué gate/issue persiste, con evidencia

RESTRICCIONES:
- No modificar código fuente — solo ejecutar y verificar
- Si v4complete falla con error, reportar el error completo, no intentar debuggear
```

### Tareas (parent agent)

- [ ] **T1 — Preparar subagente**: Verificar que el working directory existe y el venv está disponible. Crear directorio `evidence/roicriiif-fase-4/` si no existe.

- [ ] **T2 — Delegar v4complete**: Ejecutar delegate_task con el prompt de arriba, timeout=900s.

- [ ] **T3 — Verificar resultados del subagente**: Confirmar que los entregables cumplen criterios. Si algo falla:
  - Si alignment < 80%: analizar gate_report para identificar qué asset específico falla
  - Si "13%" aún presente: verificar que FASE-3 se aplicó correctamente
  - Si coherence < 0.80: investigar regresión

- [ ] **T4 — Preservar evidence**: Confirmar que todos los archivos están en `evidence/roicriiif-fase-4/`

### Restricciones

- NO modificar código fuente — esta fase es SOLO ejecución y verificación
- Si v4complete falla con error técnico (timeout, import error, etc.), reportar pero NO intentar fixear en esta sesión
- Los criterios de aceptación son los del target post-fix (ver arriba)

### Criterios de completitud

- [ ] v4complete ejecutado exitosamente para hotelcastillareal.com
- [ ] Coherence ≥ 0.80
- [ ] Proposal alignment ≥ 80%
- [ ] Publication readiness = READY (o al menos no NOT_READY por los 3 issues originales)
- [ ] whatsapp_button NO en missing de gate_report
- [ ] Al menos uno de {faq_page, optimization_guide} ≥ 0.7 confidence
- [ ] "13% del dolor priorizado" NO en propuesta
- [ ] Evidence preservada en evidence/roicriiif-fase-4/
- [ ] Cascade de docs actualizada (dependencias-fases.md, REGISTRY.md)
- [ ] `log_phase_completion.py` ejecutado con `--fase FASE-4`

### Próxima sesión

FASE-RELEASE-4.58.0: Version bump, CHANGELOG, documentación oficial, sync_versions, pre-commit.
