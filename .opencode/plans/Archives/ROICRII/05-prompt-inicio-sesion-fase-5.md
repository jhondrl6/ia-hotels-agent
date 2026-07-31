# FASE-5: v4complete Hotel Castilla Real + Análisis Post-Implementación

**Plan**: ROICRII
**Tipo**: Ejecución + Análisis
**Hallazgos**: Todos (verificación final)
**Prerrequisito**: FASE-4 completada
**Iteración estimada**: 35-45

---

## Objetivo

Ejecutar UNA ÚNICA vez `v4complete` para Hotel Castilla Real y verificar que los 5 niveles de éxito fueron superados. Este es el cierre del plan ROICRII — la evidencia de que los fixes estructurales funcionan.

---

## Contexto

- **Hotel**: Hotel Castilla Real
- **URL**: https://www.hotelcastillareal.com/
- **Región**: eje_cafetero
- **Versión base (pre-ROICRII)**: v4.55.0 (post-ROICR)
- **Coherencia base**: 0.826

---

## Tareas

### Tarea 5A: Pre-v4complete — pytest completo sin regresiones

Antes de ejecutar v4complete, verificar que TODOS los tests del proyecto pasan:

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
pytest --tb=short -q 2>&1 | tail -20
```

**Si hay fallos**: Corregir ANTES de v4complete. NO ejecutar v4complete con tests rotos.

**Expected**: 517+ passed, 0 failed (los tests nuevos de FASE-1 a FASE-4 deben estar incluidos).

### Tarea 5B: Ejecutar v4complete

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
timeout 900 python main.py v4complete \
  --url "https://www.hotelcastillareal.com/" \
  --region "eje_cafetero" \
  --hotel-name "Hotel Castilla Real" \
  2>&1 | tee /tmp/roicrii_v4complete_output.log
```

**Timeout**: 900s (15 min). Si timeout, revisar logs.

**Post-ejecución**: Guardar output inmediatamente:
```bash
cp -r output/v4_complete/* /tmp/roicrii_v4complete_backup/
```

### Tarea 5C: Análisis post-implementación — 5 niveles de éxito

Verificar CADA nivel contra el output real de v4complete:

#### Nivel 1 — ROI Unificado
```bash
# Buscar displays de ROI en el output
grep -i "roi\|\.X\|\.2f" output/v4_complete/02_PROPUESTA_*.md | head -10

# Verificar que NO hay métodos inline
grep -c "def _calculate_roi\b\|def _calculate_roi_saas\b" modules/commercial_documents/v4_proposal_generator.py
# Expected: 0

# Verificar formato .2f
grep "roi.*X" output/v4_complete/02_PROPUESTA_*.md | head -5
# Expected: format like "1.28X" not "1.3X" (2 decimals)
```
**PASS**: ROI muestra formato `:.2f` (2 decimales). Solo `roi_formatter.py` como motor.

#### Nivel 2 — Coherencia Financiera
```bash
# Gate ROI formula (opex-only)
grep "total_investment_opex" modules/commercial_documents/v4_proposal_generator.py

# Pipeline activa (ethical_cap en resultado)
grep "ethical_cap\|value_capture" output/v4_complete/02_PROPUESTA_*.md | head -5

# ROI coherente entre gate y documento
python -c "
# Extraer ROI del documento y comparar con gate
# Buscar líneas con ROI en el documento
"
```
**PASS**: Gate calcula ROI con opex-only. Pipeline 3 pasos produce pricing con value-capture cap.

#### Nivel 3 — Gobernanza Semántica
```bash
# pain_ratio_note clarificado
grep -i "addressable\|zona addressable" output/v4_complete/02_PROPUESTA_*.md | head -3

# operational_floor unificado
grep "operational_floor" modules/financial_engine/pricing_calculator.py | grep "400_000"
```
**PASS**: Copy diferencia addressable vs fee/loss. Floor es 400K en ambos caminos.

#### Nivel 4 — Gate Estricto
```bash
# strict_mode para externo
grep "CommercialGateBlockedError" modules/commercial_documents/v4_proposal_generator.py

# CAPEX desglose en documento
grep -i "capex\|componente\|auditoría.*inicial\|implementación.*técnica" output/v4_complete/02_PROPUESTA_*.md | head -5
```
**PASS**: Gate externo bloquea con exception. CAPEX desglosado en componentes.

#### Nivel 5 — CI/CD
```bash
# Coherencia score
grep -i "coherence\|score" output/v4_complete/delivery_quality_report.json 2>/dev/null | head -5

# Sin regresiones
pytest --tb=short -q 2>&1 | tail -5
```
**PASS**: Coherence ≥ 0.80. pytest 0 failed.

---

## Tabla de Verificación Post-Implementación

| Nivel | Criterio | Threshold | Resultado | Estado |
|-------|----------|-----------|-----------|--------|
| N1 | ROI formato `:.2f` | Solo roi_formatter | (llenar) | ⬜ |
| N1 | 0 métodos inline ROI | `grep -c def _calculate_roi` = 0 | (llenar) | ⬜ |
| N2 | Gate ROI opex-only | Sin CAPEX en denominador | (llenar) | ⬜ |
| N2 | Pipeline 3 pasos activo | ethical_cap en resultado | (llenar) | ⬜ |
| N3 | pain_ratio addressable | Copy clarificado | (llenar) | ⬜ |
| N3 | Floor unificado 400K | 2 caminos = mismo fallback | (llenar) | ⬜ |
| N4 | Gate externo bloquea | CommercialGateBlockedError | (llenar) | ⬜ |
| N4 | CAPEX desglose | ≥3 componentes | (llenar) | ⬜ |
| N5 | Coherence ≥ 0.80 | delivery_quality_report | (llenar) | ⬜ |
| N5 | pytest 0 failed | 517+ passed | (llenar) | ⬜ |

---

## Si un nivel FALLA

1. **N1 falla**: Volver a FASE-1, verificar que roi_formatter se usa correctamente
2. **N2 falla**: Volver a FASE-2, verificar gate formula y wrapper
3. **N3 falla**: Volver a FASE-3, verificar pain_ratio_note y operational_floor
4. **N4 falla**: Volver a FASE-4, verificar exception y CAPEX
5. **N5 falla**: Corregir tests inmediatamente (no volver a fase anterior)

**Regla**: NO avanzar al siguiente nivel si el actual falla. Cada nivel es prerequisito del análisis completo.

---

## Log Phase

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python scripts/log_phase.py --phase "FASE-5" --plan "ROICRII" --status "completed" --desc "v4complete_Hotel_Castilla_Real_analisis_5_niveles"
```

---

## Documentación Post-Fase

Actualizar `09-documentacion-post-proyecto.md` con:
- Output de v4complete (paths de archivos generados)
- Tabla de verificación de 5 niveles (completada con resultados)
- Coherence score comparativo (pre vs post ROICRII)
- QA score comparativo (72% → objetivo ≥90%)
- Estado FINAL de todos los hallazgos del ROICRII
- Veredicto final: ¿La propuesta es APTA PARA ENVÍO AL CLIENTE?
