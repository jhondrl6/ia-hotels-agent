# FASE-SCORING-A: Fix del filtrado en `_build_scoring_breakdown()`

**ID**: FASE-SCORING-A
**Objetivo**: Corregir `_build_scoring_breakdown()` para mostrar TODOS los factores del checklist (TRUE y FALSE) con marcador visual, validando con Hotel Castilla Real
**Dependencias**: Ninguna (primera fase)
**Duración estimada**: 45-60 min
**Skill**: `iah-cli-phased-execution`

---

## Contexto

El sistema de scoring de iah-cli tiene 4 pilares (SEO, GEO, AEO, IAO) con checklists implementados en `v4_diagnostic_generator.py`. Sin embargo, `_build_scoring_breakdown()` (L276-285) filtra por `is True`, ocultando los factores FALSE del diagnóstico generado.

**Bug concreto:** Para Hotel Castilla Real, el diagnóstico muestra GEO 70/100 pero solo 4/6 factores. Los 30pts faltantes (`nap_consistente(15%)` + `horario_gbp(15%)`) son invisibles para el cliente.

**Contexto validado:** `.opencode/context/scoring-transparency-context.md` (2026-05-05)

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| — | Primera fase del plan |

### Base Técnica Disponible

- `modules/commercial_documents/v4_diagnostic_generator.py` — `_build_scoring_breakdown()` L276-285
- CHECKLIST_GEO: 6 items = 100pts (nap_consistente, redes_activas, geo_score_gbp, fotos_gbp, horario_gbp, schema_reviews_geo)
- `calcular_score_geo()` — calcula score correctamente (no se modifica)
- `_extraer_elementos_geo()` — extrae elementos correctamente (no se modifica)
- `modules/commercial_documents/templates/diagnostico_v6_template.md` — tiene `${geo_score_breakdown}` L60
- Test: v4complete con Hotel Castilla Real (https://www.hotelcastillareal.com/, region=eje_cafetero)

---

## Tareas

### Tarea 1: Investigar y modificar `_build_scoring_breakdown()`

**Objetivo**: Reemplazar el filtro `is True` por iteración completa con marcadores visuales

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` L276-285

**Cambio exacto**:

ANTES (L276-285):
```python
# Construir breakdown solo con elementos que contribuyeron
parts = []
for k, peso in checklist.items():
    if elementos.get(k) is True:   # ← BUG: SOLO incluye TRUE
        parts.append(f"{k}({peso}%)")
```

DESPUÉS:
```python
# Construir breakdown con todos los elementos (TRUE y FALSE) con marcador visual
parts = []
for k, peso in checklist.items():
    if elementos.get(k) is True:
        parts.append(f"✅ {k}({peso}%)")
    else:
        parts.append(f"~~{k}({peso}%)~~")
```

**Criterios de aceptación**:
- [ ] La función itera TODO el checklist (no solo los True)
- [ ] Factores True → `✅ nombre(peso%)`
- [ ] Factores False → `~~nombre(peso%)~~`
- [ ] El score calculado por `calcular_score_*()` no se modifica

### Tarea 2: Validar con v4complete (Hotel Castilla Real)

**Objetivo**: Ejecutar v4complete y verificar el breakdown en el diagnóstico generado

**Comando**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
venv/Scripts/python.exe main.py v4complete \
    --url https://www.hotelcastillareal.com/ \
    --output output/test-scoring-transparency
```

**⚠️ CORRECCIÓN (2026-05-05):** El flag `--region` no existe en v4complete. La región se detecta automáticamente. El prompt original lo incluía por error.

**Ejecutar con**: `terminal(background=true, notify_on_complete=true, timeout=600)`

**Criterios de aceptación**:
- [ ] v4complete termina sin errores
- [ ] El diagnóstico muestra GEO 70/100 con **6 factores visibles**
- [ ] Formato esperado: `✅ redes_activas(10%) + ✅ geo_score_gbp(30%) + ✅ fotos_gbp(15%) + ✅ schema_reviews_geo(15%) + ~~nap_consistente(15%)~~ + ~~horario_gbp(15%)~~`
- [ ] El score sigue siendo 70/100 (la lógica de cálculo no cambió)
- [ ] Coherence score ≥ 0.80 (gate publication)

**Verificación del output**:
```bash
grep -A2 "GEO" output/test-scoring-transparency/01_DIAGNOSTICO_Y_OPORTUNIDAD_*.md
```

---

## Tests Obligatorios

| Test | Criterio de Éxito |
|------|-------------------|
| v4complete Hotel Castilla Real | Diagnóstico muestra 6/6 factores GEO |
| `run_all_validations.py --quick` | 4/4 checks |

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase:

1. **`dependencias-fases.md`**
   - Marcar SCORING-A como ✅ Completada
   - Actualizar fecha de finalización

2. **`README.md` del plan**
   - Actualizar tabla de progreso

3. **`06-checklist-implementacion.md`**
   - Marcar items A1-A6

4. **`09-documentacion-post-proyecto.md`**
   - Marcar Sección E: Post-Fase SCORING-A

5. **Ejecutar log_phase_completion.py**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-SCORING-A \
    --desc "Fix de filtrado en _build_scoring_breakdown() para mostrar todos los factores con marcador visual" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py" \
    --tests "0" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] `_build_scoring_breakdown()` muestra TODOS los factores con marcadores ✅/~~tachado~~
- [ ] v4complete Hotel Castilla Real: diagnóstico generado sin errores
- [ ] Diagnóstico muestra GEO 70/100 con 6/6 factores (4✅ + 2~~tachado~~)
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] `log_phase_completion.py` ejecutado
- [ ] `dependencias-fases.md` actualizado
- [ ] `README.md` actualizado

---

## Restricciones

- NO modificar los checklists ni los pesos
- NO modificar `calcular_score_*()` ni `_extraer_elementos_*()`
- NO modificar `scoring_methodology.md`
- NO modificar el template v6 (eso es SCORING-B)
- NO crear tests unitarios nuevos (validación vía v4complete + inspección visual)
- Máximo 60 iteraciones del agente
- Si el agente se agota antes de completar: guardar evidencia en `evidence/SCORING-A/`, actualizar `dependencias-fases.md` con checkpoint
