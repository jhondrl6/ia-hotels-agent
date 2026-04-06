
# FASE CAUSAL-01: Eliminar IAO/Voice del scorecard y unificar AEO

**ID**: FASE-CAUSAL-01
**Objetivo**: Eliminar scores redundantes IAO y Voice Readiness del scorecard del diagnostico V6. Unificar todo bajo un solo score AEO (Infraestructura para IAs) basado en datos medibles del audit web.
**Dependencias**: Ninguna (primera fase del proyecto)
**Skill**: iah-cli-phased-execution
**Contexto completo**: `.opencode/plans/context/consolidacion_context.md`

---

## Contexto

**Problema**: El diagnostico V6 presenta AEO e IAO como scores separados cuando miden lo mismo. IAO sin GA4 hace fall back a `_calculate_schema_infra_score()` que es exactamente AEO. Voice Readiness retorna `"--"` hardcodeado. El hotelero ve scores redundantes y el sistema no puede explicar la diferencia.

**Regla de negocio**: Si no hay un Asset para resolver un dolor, no va en el diagnostico. Si no se puede medir con datos reales del audit, no se genera score.

**Contexto completo disponible en**: `/mnt/c/Users/Jhond/Github/iah-cli/.opencode/plans/context/consolidacion_context.md`

---

## Tareas

### Tarea 0: Referenciar BASELINE existente

El baseline ya existe: `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260402_184117.md`

**Verificar en el baseline actual**:
- [ ] Scorecard tiene 5 filas actual (GEO, GBP, AEO, IAO, SEO)
- [ ] AEO muestra "--" (sin valor numerico)
- [ ] IAO muestra "25/100" (fallback a schema_infra)
- [ ] SEO muestra score < 65
- [ ] Generacion exitosa sin errores (exit code 0)

Este baseline es la referencia contra la cual se comparan TODAS las fases posteriores.

### Tarea 1: Eliminar metodos IAO/Voice de v4_diagnostic_generator.py

**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py`

**Que eliminar**:
1. Metodo `_calculate_voice_readiness_score()` (linea ~1137) - retorna `"--"` hardcodeado, nunca midio nada
2. Metodo `_calculate_iao_score()` (linea ~1145) - sin GA4 es identico a schema_infra_score
3. Metodo `_calculate_score_ia()` (linea ~1163) - wrapper de IATester que no aporta sin GA4 real
4. En `_prepare_template_data()`, eliminar las variables:
   - `'iao_score'` (linea ~497)
   - `'iao_status'` (linea ~498)
   - `'voice_readiness_score'` (linea ~495)
   - `'voice_readiness_status'` (linea ~496)
5. En `_inject_analytics()`: eliminar cualquier referencia a `"iao_score"` en el dict de retorno (lineas ~605, ~615)

**Verificacion**:
- [ ] `grep -n "iao_score\|voice_readiness" modules/commercial_documents/v4_diagnostic_generator.py` no devuelve nada en el codigo activo
- [ ] El archivo sigue siendo sintacticamente valido Python

### Tarea 2: Renombrar _calculate_schema_infra_score a _calculate_aeo_score

**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py`

**Que hacer**:
1. Renombrar metodo `_calculate_schema_infra_score()` -> `_calculate_aeo_score()`
2. Actualizar TODAS las referencias internas (hay al menos en linea 493-494 y 542-543 en `_prepare_template_data`)
3. Mantener exactamente la misma logica de calculo (es el score legitimo que mide Schema Hotel, FAQ, Reviews, OG)

**Verificacion**:
- [ ] `grep -n "_calculate_schema_infra_score\|_calculate_aeo_score" modules/commercial_documents/v4_diagnostic_generator.py` solo muestra el nombre nuevo
- [ ] El metodo funciona sin cambios en su logica interna

### Tarea 3: Actualizar diagnostico_v6_template.md

**Archivo**: `modules/commercial_documents/templates/diagnostico_v6_template.md`

**Cambios en la tabla de scorecard (lineas ~45-51)**:

ANTES (lo que hay ahora):
```
|| Indicador                          | Su Negocio | Promedio Regional | Estado |
||-----------------------------------|------------|-------------------|--------|
|| **Google Maps** (GEO)             | ${geo_score}/100 | 55/100 | ${geo_status} |
|| **Perfil de Google Business**     | ${gbp_score}/100 | 30/100 | ${gbp_status} |
|| **Visibilidad en IA** (AEO)       | ${aeo_score} | 15/100 | ${aeo_status} |
|||| **Optimizacion ChatGPT**        | ${iao_score}/100 | 10/100 | ${iao_status} |
|||| **SEO Local**                   | ${seo_score}/100 | 65/100 | ${seo_status} |
```

DESPUES (lo que debe quedar):
```
|| Indicador                          | Su Negocio | Promedio Regional | Estado |
||-----------------------------------|------------|-------------------|--------|
|| **Google Maps** (GEO)             | ${geo_score}/100 | 55/100 | ${geo_status} |
|| **Perfil de Google Business**     | ${gbp_score}/100 | 30/100 | ${gbp_status} |
|| **AEO - Infraestructura para IAs**| ${aeo_score}/100 | 15/100 | ${aeo_status} |
|| **SEO Local**                     | ${seo_score}/100 | 65/100 | ${seo_status} |
```

Puntos clave:
- La fila de AEO ahora usa `${aeo_score}/100` (agregar `/100` que faltaba en el template actual)
- Eliminar la fila de "Optimizacion ChatGPT" (IAO)
- Eliminar "Visibilidad en IA (AEO)" como fila separada
- Quedan 4 filas, no 5
- El benchmark de AEO es 15/100 (se mantiene el que ya existia)

**NO tocar**:
- El resto del template (brechas, quick wins, urgencia, etc.)
- Las secciones de analytics transparency

### Tarea 4: Verificar template V4 legacy (opcional)

### Tarea 5: VALIDACION POST-CAMBIO - v4complete comparativo

**DESPUES de todos los cambios**, volver a ejecutar v4complete con Hotel Visperas:

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
venv/Scripts/python.exe main.py \
    --v4complete \
    --hotel-name "Hotel Visperas" \
    --hotel-url "https://www.hotelvisperas.com/es" \
    --output-dir "output/v4_complete" \
    --no-analytics
```

**Comparar con baseline (Tarea 0)**:
- [ ] Scorecard tiene 4 filas ahora (GEO, GBP, AEO, SEO) — ANTES tenia 5
- [ ] No hay fila de "Optimizacion ChatGPT" — ANTES estaba
- [ ] No hay fila de "Visibilidad en IA" — ANTES estaba
- [ ] AEO muestra un score numerico `XX/100` (no "--") — ANTES era "--"
- [ ] No hay KeyError ni errores de template (variables eliminadas no se usan)
- [ ] El diagnostico se genera exitosamente (exit code 0)
- [ ] Guardar comparacion en `.opencode/plans/context/comparacion_fase_1.md`

Si hay errores, revertir los cambios y diagnosticar antes de marcar completada.

---

## Criterios de Aceptacion

- [ ] El scorecard en diagnostico_v6_template.md tiene exactamente 4 filas (GEO, GBP, AEO, SEO)
- [ ] No hay referencias a `iao_score`, `iao_status`, `voice_readiness`, `Optimizacion ChatGPT` en el template V6
- [ ] `_calculate_iao_score()` y `_calculate_voice_readiness_score()` eliminados de v4_diagnostic_generator.py
- [ ] `_calculate_schema_infra_score()` renombrado a `_calculate_aeo_score()` con todas sus referencias actualizadas
- [ ] `_inject_analytics()` no retorna `iao_score` en ningun caso (ni GA4 ni fallback)
- [ ] El archivo `v4_diagnostic_generator.py` no tiene errores de sintaxis Python
- [ ] Si se ejecuta un diagnostico de prueba, el scorecard muestra el score AEO con formato `XX/100`

---

## Restricciones

- NO tocar la logica de GA4 ni `_inject_analytics()` mas alla de eliminar referencias a `iao_score`
- NO modificar `gap_analyzer.py` (esto es Fase 2)
- NO modificar `report_builder.py` (esto es Fase 3)
- NO agregar nuevas funcionalidades, solo eliminar/renombrar lo redundante
- El score AEO (antes schema_infra) debe mantener EXACTAMENTE la misma logica de calculo

---

## Post-Ejecucion (OBLIGATORIO)

Al terminar esta fase, ejecutar INMEDIATAMENTE:

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python scripts/log_phase_completion.py \
    --fase FASE-CAUSAL-01 \
    --desc "Eliminacion IAO/Voice del scorecard, unificacion bajo AEO" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/templates/diagnostico_v6_template.md" \
    --check-manual-docs
```

---

## Checklist de Completitud

- [ ] Scorecard tiene 4 filas (GEO, GBP, AEO, SEO)
- [ ] Sin referencias a iao/voice en generator ni template V6
- [ ] `_calculate_aeo_score()` funciona como reemplazo de `_calculate_schema_infra_score()`
- [ ] Python syntax valida en todos los archivos modificados
- [ ] `log_phase_completion.py` ejecutado sin errores
- [ ] REGISTRY.md actualizado (automatico por el script)
- [ ] No hay [GAP] en DOCUMENTATION AUDIT
