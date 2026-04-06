
# FASE CAUSAL-03: Eliminar IAO de report_builder.py y cleanup dead code

**ID**: FASE-CAUSAL-03
**Objetivo**: Eliminar referencias a IAO en report_builder.py (que tiene su propia implementacion duplicada de `_calculate_iao_score()`). Eliminar codigo muerto relacionado con voice readiness en otros modulos si aplica.
**Dependencias**: FASE-CAUSAL-01 y FASE-CAUSAL-02 (ambas deben estar completadas)
**Skill**: iah-cli-phased-execution
**Contexto completo**: `.opencode/plans/context/consolidacion_context.md`

---

## Contexto

`modules/generators/report_builder.py` tiene implementaciones propias e independientes de `_calculate_iao_score()` ademas de las que ya estan en `v4_diagnostic_generator.py`. Estas generan scorecards alternativos que tambien incluyen IAO como fila separada. Todo esto debe eliminarse para mantener coherencia con el cambio del scorecard V6.

Adicionalmente, `modules/delivery/generators/aeo_metrics_gen.py` tiene referencias a `voice_readiness` pero es un modulo tecnico interno (no comercial). NO se elimina, solo se verifica que no dependa de codigo eliminado en Fase 1.

---

## Tareas

### Tarea 1: Eliminar IAO de report_builder.py

**Archivo**: `modules/generators/report_builder.py`

Buscar y eliminar/ajustar:

1. Metodo `_calculate_iao_score()` (linea ~1592). Eliminar completamente.

2. Variables que calculan `iao_score`:
   - Linea ~773: `iao_score = self._calculate_iao_score(ia_test)`
   - Linea ~1160: `iao_score = self._calculate_iao_score(ia_test)`
   
3. Variable `iao_benchmark`/`iao_ref`:
   - Linea ~780: `iao_ref = region_profile.get('iao_score_ref', 20)`
   - Linea ~906: `iao_ref = region_profile.get('iao_score_ref', 20)`
   - Linea ~1168: `iao_ref = region_profile.get('iao_score_ref', 20)`
   
4. Calculo de `iao_diff`:
   - Linea ~784: `iao_diff = iao_score - iao_ref`
   - Linea ~1172: `iao_diff = iao_score - iao_ref`
   
5. Scorecard que incluye IAO (linea ~1298):
   ```python
   | **Score IA Avanzado (IAO)** | {iao_score}/100 | {iao_ref}/100 | {iao_icon} |
   ```
   Eliminar esta fila del scorecard generado.

6. Referencia de texto IAO (linea ~1025):
   ```python
   **Score IAO: {self._calculate_iao_score(ia_test)}/100**
   ```
   Eliminar esta linea o reemplazar con referencia al score AEO si existe en ese contexto.

7. Variables `iao_score` en dicts de contexto:
   - Linea ~847: `iao_score=iao_score,` en algun dict de contexto
   Verificar que el dict se usa para renderizar templates y eliminar la variable si es el caso.

**IMPORTANTE**: Para cada eliminacion, verificar que las lineas de contexto que usan esas variables tambien se ajusten. Si una variable se pasaba a un template, el template correspondiente debe actualizarse.

### Tarea 2: Verificar aeo_metrics_gen.py

**Archivo**: `modules/delivery/generators/aeo_metrics_gen.py`

Este modulo genera reportes tecnicos de AEO usando AEOKPIs. Incluye `voice_readiness` pero como dato de modelo, no como score fantasma.

**Solo verificar**:
- Que `VoiceReadinessScore` (importado de `data_models.aeo_kpis`) no fue eliminado en Fase 1
- Que `kpis.voice_readiness` no causa error si el objeto viene de mock data

**NO modificar** este archivo a menos que haya un error de compilacion/imports.

### Tarea 3: Verificar data_models/aeo_kpis.py

**Archivo**: `data_models/aeo_kpis.py` (si existe)

Verificar que:
- La clase `AEOKPIs` no depende de IAO score
- La clase `VoiceReadinessScore` existe y funciona (se usa en aeo_metrics_gen.py)

Si `AEOKPIs` tiene un campo `iao_score` o similar, marcarlo como deprecado pero NO eliminarlo (podria usarse en otras partes del sistema que no hemos tocado).

---

## Criterios de Aceptacion

- [ ] `report_builder.py` no tiene `_calculate_iao_score()` ni referencias a `iao_score`, `iao_ref`, `iao_diff`
- [ ] Los scorecards generados por report_builder.py no incluyen fila de IAO
- [ ] `aeo_metrics_gen.py` no genera errores de import ni runtime
- [ ] `data_models/aeo_kpis.py` sigue siendo importable sin errores
- [ ] Python syntax valida en todos los archivos modificados

---

## Restricciones

- NO eliminar `aeo_metrics_gen.py` (modulo tecnico interno valido)
- NO modificar la estructura de `AEOKPIs` o `VoiceReadinessScore` en data_models
- Solo eliminar IAO de report_builder.py
- Si report_builder.py tiene logica de distribucion de perdida similar a gap_analyzer, redistribuir igual (2 pilares), pero solo si la logica es identica

---

## Post-Ejecucion (OBLIGATORIO)

Al terminar esta fase, ejecutar INMEDIATAMENTE:

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python scripts/log_phase_completion.py \
    --fase FASE-CAUSAL-03 \
    --desc "Eliminacion IAO de report_builder.py y verificacion de modulos tecnicos" \
    --archivos-mod "modules/generators/report_builder.py" \
    --check-manual-docs
```

---

## Checklist de Completitud

- [ ] report_builder.py limpio de referencias IAO
- [ ] aeo_metrics_gen.py sin errores de import
- [ ] data_models/aeo_kpis.py importable sin errores
- [ ] Python syntax valida
- [ ] `log_phase_completion.py` ejecutado sin errores
- [ ] REGISTRY.md actualizado
- [ ] No hay [GAP] en DOCUMENTATION AUDIT
