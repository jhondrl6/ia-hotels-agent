---
description: Prompt de inicio para FASE-VALIDATE-RC — Hotfix + limpieza dead code + re-ejecucion v4complete Amazilia Hotel
version: 1.0.0
---

# FASE-VALIDATE-RC: Hotfix Causa Raiz + Re-ejecucion v4complete Amazilia Hotel

**ID**: FASE-VALIDATE-RC  
**Objetivo**: Corregir TypeError en `_build_60_day_plan()` eliminando dead code legacy y cubriendo con test de regresion; re-ejecutar v4complete una unica vez para validacion completa de bugs pendientes.  
**Dependencias**: FASE-A, FASE-B, FASE-C, FASE-D (COMPLETADAS); FASE-VALIDATE (PARCIAL-FALLA — diagnostico ya generado)  
**Duracion estimada**: 45-60 minutos  
**Skill**: phased_project_executor v2.4.0, iah-cli-phased-execution  

---

## Contexto

La fase FASE-VALIDATE ejecuto `v4complete --url https://amaziliahotel.com/` y genero diagnostico, escenarios financieros y audit report correctamente, pero crasheo en la generacion de la propuesta comercial con:

```
TypeError: V4ProposalGenerator._build_60_day_plan() missing 1 required positional argument: 'asset_plan'
```

El bug esta en `modules/commercial_documents/v4_proposal_generator.py` lineas 559-560 donde `_build_60_day_plan()` y `_build_90_day_plan()` se llaman sin pasar `asset_plan`, a diferencia de las lineas 557-558 (`_build_7_day_plan`, `_build_30_day_plan`) que SI lo pasan.

Auditoria previa revelo que las variables `plan_7d`, `plan_30d`, `plan_60d`, `plan_90d` son **dead code**: no existen consumidores en todo el repositorio (sin referencias en templates ni en codigo Python). El template activo es V6 que usa `plan_*_days`. Las variables legacy son residuo del template V4 que fue eliminado.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A | COMPLETADA |
| FASE-B | COMPLETADA |
| FASE-C | COMPLETADA |
| FASE-D | COMPLETADA |
| FASE-VALIDATE | PARCIAL-FALLA ( diagnostico generado, propuesta no ) |

### Base Tecnica Disponible

- Archivos existentes: `v4_proposal_generator.py`, `propuesta_v6_template.md`, `financial_scenarios.json` (generado), `audit_report.json` (generado)
- Tests base: 533 passed, 1 xpassed (pre-flight)
- Modulos disponibles: `commercial_documents/`, `financial_engine/`, `asset_generation/`

---

## Tareas

### Tarea 1: Hotfix Critico — Pasar asset_plan en lineas 559-560
**Objetivo**: Eliminar el TypeError que bloquea la generacion de propuesta.

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py`

**Cambio exacto**:
```python
# Linea 559
'plan_60d': self._build_60_day_plan(asset_plan),
# Linea 560
'plan_90d': self._build_90_day_plan(asset_plan),
```

**Criterios de aceptacion**:
- [ ] Diff muestra solo las 2 lineas modificadas (sin cambios de formato adicionales)
- [ ] `pytest tests/commercial_documents/ -v` pasa sin regresiones

### Tarea 2: Causa Raiz — Eliminar Variables Legacy Muertas
**Objetivo**: Reducir superficie de error eliminando 4 claves del dict que no tienen consumidor.

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py`

**Procedimiento de seguridad**:
1. ANTES de eliminar, ejecutar: `grep -r "plan_60d\|plan_90d\|plan_7d\|plan_30d" modules/ tests/ --include="*.py" --include="*.md"`
2. Si hay 0 referencias (se espera 0), eliminar las 4 claves del dict en `_prepare_template_data()`:
   - `'plan_7d': self._build_7_day_plan(asset_plan),`
   - `'plan_30d': self._build_30_day_plan(asset_plan),`
   - `'plan_60d': self._build_60_day_plan(asset_plan),`
   - `'plan_90d': self._build_90_day_plan(asset_plan),`
3. Dejar intactas las claves V6: `plan_7_days`, `plan_30_days`, `plan_60_days`, `plan_90_days`

**Criterios de aceptacion**:
- [ ] grep confirma 0 referencias a las variables legacy
- [ ] Las 4 claves legacy eliminadas del dict
- [ ] `pytest tests/commercial_documents/ -v` pasa sin regresiones
- [ ] `run_all_validations.py --quick` pasa 4/4

### Tarea 3: Test de Regresion — Dict Completo sin TypeError
**Objetivo**: Cubrir con tests la zona que tenia 0 cobertura, evitando que un cambio futuro de firma vuelva a romper la construccion del dict.

**Archivo nuevo**:
- `tests/commercial_documents/test_proposal_generator_dict.py`

**Comportamiento del test**:
- Instanciar `V4ProposalGenerator` con mocks minimos
- Llamar `_prepare_template_data()` con un `asset_plan` de prueba (lista de `AssetSpec`)
- Verificar que el dict resultante contiene las claves V6 (`plan_7_days`, `plan_30_days`, `plan_60_days`, `plan_90_days`) y que sus valores son strings no vacios
- Verificar que el dict NO contiene las claves legacy (`plan_7d`, etc.) despues de la limpieza

**Criterios de aceptacion**:
- [ ] Test pasa con `pytest tests/commercial_documents/test_proposal_generator_dict.py -v`
- [ ] El test ejecuta `_prepare_template_data()` sin lanzar TypeError

### Tarea 4: Validacion Interna Pre-v4complete
**Objetivo**: Confirmar que el sistema esta sano antes de gastar API calls.

**Comandos**:
```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe -m pytest tests/commercial_documents/ tests/financial_engine/ tests/delivery/ -v
```

**Criterios de aceptacion**:
- [ ] run_all_validations.py --quick: 4/4 PASS
- [ ] pytest: 0 regresiones (533+ tests passed)

### Tarea 5: Ejecucion Final v4complete — Amazilia Hotel (UNICA)
**Objetivo**: Generar el kit completo para Amazilia Hotel y evaluar todos los bugs pendientes.

**Parametros del hotel**:
- Nombre segun sitio web: **Amazilia** (subtitulo: Hotel campestre en Pereira)
- URL: `https://amaziliahotel.com/`
- Direccion: Via Pereira a Cerritos Entrada 8 Cafelia, Risaralda
- Telefono: +57 310 401 9049
- Correo: gerencia@amaziliahotel.com
- RNT: 56217

**Comando exacto**:
```bash
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/
```

**Regla de costo**: Esta es la UNICA ejecucion v4complete de esta sesion. NO repetir salvo que falle por errores tecnicos no relacionados con el codigo (ej: timeout de red).

**Criterios de aceptacion**:
- [ ] Comando completa sin TypeError ni crash
- [ ] Se genera `02_PROPUESTA_COMERCIAL_*.md`
- [ ] Se generan todos los archivos de salida esperados

### Tarea 6: Evaluacion Completa de Bugs Pendientes
**Objetivo**: Verificar todos los bugs que antes eran NO EVALUABLE por el crash.

**Checklist de evaluacion** (usar archivos generados en Tarea 5):

| Bug | Criterio | Veredicto |
|-----|----------|-----------|
| BUG-1 | Seccion "Esto es lo que hacemos" no vacia | [ ] PASS / [ ] FAIL |
| BUG-3 | ROI <= 5.0X en propuesta | [ ] PASS / [ ] FAIL |
| BUG-4 | 0 items "No generado" / "Requiere datos" visibles al cliente | [ ] PASS / [ ] FAIL |
| BUG-8 | Ortografia corregida (hoteles, brille, proveer, Absorbido, proteccion) | [ ] PASS / [ ] FAIL |
| D-1 | AEO incluido condicionalmente si aplica | [ ] PASS / [ ] FAIL / [ ] N/A |
| D-4 | Timeline 7/30/60/90 dias realista | [ ] PASS / [ ] FAIL |
| D-7 | 0 items "No generado" en entregables | [ ] PASS / [ ] FAIL |

**Criterios de aceptacion**:
- [ ] Todos los bugs evaluables tienen veredicto PASS o FAIL documentado
- [ ] Cualquier FAIL nuevo se documenta en `evidence/fase-VALIDATE-RC/validacion_checklist.md`

### Tarea 7: Documentacion Post-Fase
**Objetivo**: Cumplir flujo documental obligatorio segun CONTRIBUTING.md.

**Pasos**:
1. Ejecutar `log_phase_completion.py`:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-VALIDATE-RC \
    --desc "Hotfix TypeError _build_60_day_plan + limpieza dead code + test regresion + re-ejecucion v4complete Amazilia Hotel" \
    --archivos-nuevos "tests/commercial_documents/test_proposal_generator_dict.py" \
    --archivos-mod "modules/commercial_documents/v4_proposal_generator.py" \
    --tests "1" \
    --check-manual-docs
```
2. Actualizar `06-checklist-implementacion.md`: marcar FASE-VALIDATE-RC como COMPLETADA
3. Actualizar `09-documentacion-post-proyecto.md`: agregar resultados de validacion a Seccion D
4. Guardar evidencia en `evidence/fase-VALIDATE-RC/`:
   - `validacion_checklist.md`
   - `02_PROPUESTA_COMERCIAL_*.md` (si se genero)
   - `financial_scenarios.json` (nueva version si cambio)

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| `test_proposal_generator_dict.py` | `tests/commercial_documents/test_proposal_generator_dict.py` | Debe pasar con 1/1 tests |
| Commercial documents suite | `tests/commercial_documents/` | 0 regresiones |
| Full quick validation | `scripts/run_all_validations.py --quick` | 4/4 checks PASS |

**Comando de validacion**:
```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_proposal_generator_dict.py -v
```

---

## Post-Ejecucion (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase, actualizar INMEDIATAMENTE (antes de cerrar la sesion):

1. **`dependencias-fases.md`**
   - Marcar FASE-VALIDATE-RC como COMPLETADA
   - Actualizar fecha de finalizacion
   - Agregar nota: "Bug TypeError resuelto, dead code eliminado, v4complete re-ejecutado"

2. **`06-checklist-implementacion.md`**
   - Marcar FASE-VALIDATE-RC como COMPLETADA
   - Llenar columnas Fecha Fin, Tests, Commit
   - Evaluar si el proyecto esta en estado FINALIZADO

3. **`09-documentacion-post-proyecto.md`**
   - **Seccion B**: Agregar `v4_proposal_generator.py` como modificado (dead code eliminado)
   - **Seccion C**: Agregar `test_proposal_generator_dict.py` como test nuevo
   - **Seccion D**: Actualizar metricas acumulativas (tests +1, dead code -4 variables)
   - **Seccion D (resultado validacion)**: Actualizar con veredicto final v4complete
   - **Seccion E**: Marcar evidence/fase-VALIDATE-RC/ como preservada

4. **`evidence/fase-VALIDATE-RC/`**
   - Crear directorio si no existe
   - Copiar checklist de validacion con veredictos de bugs
   - Copiar propuesta generada (02_PROPUESTA_COMERCIAL_*.md)

**NO esperar a la siguiente sesion para documentar.** La documentacion incremental evita perdida de contexto.

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como COMPLETADA** ⚠️

- [ ] **Hotfix aplicado**: Lineas 559-560 pasan `asset_plan`
- [ ] **Dead code eliminado**: 4 variables legacy removidas del dict (verificado con grep)
- [ ] **Test nuevo pasa**: `test_proposal_generator_dict.py` ejecuta sin errores
- [ ] **Validaciones del proyecto**: `run_all_validations.py --quick` pasa 4/4
- [ ] **v4complete ejecutado**: Comando completo sin crash, propuesta generada
- [ ] **Bugs evaluados**: Todos los bugs antes NO EVALUABLE ahora tienen veredicto
- [ ] **`dependencias-fases.md` actualizado**: Estado de FASE-VALIDATE-RC marcado
- [ ] **Documentacion afiliada**: CHANGELOG.md, GUIA_TECNICA.md, REGISTRY.md revisados (si log_phase_completion.py indica gaps)
- [ ] **Evidencia preservada**: Archivos en `evidence/fase-VALIDATE-RC/` si aplica
- [ ] **Post-ejecucion completada**: Todos los puntos de la seccion anterior realizados

**NO marcar la fase como completada si algun criterio falla.**

---

## Restricciones

- **UNICA ejecucion v4complete**: Solo se permite ejecutar `main.py v4complete` una vez en esta sesion para control de costos API. Si falla por bug de codigo, NO reintentar; en su lugar documentar el nuevo bug y planear FASE-VALIDATE-RC2.
- **No modificar templates**: `propuesta_v6_template.md` es inmutable en esta fase.
- **No modificar logica financiera**: FASE-B ya corrigio escenarios; esta fase no toca `calculator_v2.py`.
- **Backward compat**: Si grep revela que alguna variable legacy SI se usa (improbable pero posible), NO eliminarla; solo aplicar el hotfix y documentar la excepcion.

---

## Prompt de Ejecucion

```
Actua como ingeniero de software enfocado en calidad y control de costos API.

OBJETIVO: Ejecutar FASE-VALIDATE-RC — resolver TypeError en v4_proposal_generator.py de forma sistémica (hotfix + limpieza dead code + test de regresion) y re-ejecutar v4complete para Amazilia Hotel una unica vez.

CONTEXTO:
- Fases A-D completadas. FASE-VALIDATE fallo con TypeError en linea 559.
- Auditoria previa: variables plan_7d/30d/60d/90d son dead code (0 referencias en repo).
- Template activo: V6 (usa plan_*_days).
- Tests base: 533 passed. La zona rota no tenia cobertura.

TAREAS:
1. Aplicar hotfix en v4_proposal_generator.py lineas 559-560 (pasar asset_plan).
2. Verificar con grep que plan_7d/30d/60d/90d no tienen consumidores.
3. Eliminar las 4 claves legacy del dict si grep confirma 0 uso.
4. Crear tests/commercial_documents/test_proposal_generator_dict.py que verifique construccion del dict sin TypeError.
5. Ejecutar run_all_validations.py --quick y pytest.
6. Ejecutar v4complete --url https://amaziliahotel.com/ (UNICA vez).
7. Evaluar todos los bugs pendientes usando archivos generados.
8. Ejecutar log_phase_completion.py y actualizar documentacion.

CRITERIOS:
- 0 regresiones en tests existentes.
- v4complete genera propuesta sin crash.
- Todos los bugs tienen veredicto documentado.

VALIDACIONES:
- run_all_validations.py --quick: 4/4 PASS.
- pytest commercial_documents: 0 fallas.
- evidence/fase-VALIDATE-RC/ creado con checklist de validacion.
```
