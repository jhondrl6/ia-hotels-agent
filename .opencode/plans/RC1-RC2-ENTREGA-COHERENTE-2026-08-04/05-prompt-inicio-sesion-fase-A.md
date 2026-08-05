# FASE-A — Triage y Cuarentena de Tests Patológicos (Prerrequisito RC1)

**ID**: RC1-RC2-ENTREGA-COHERENTE-2026-08-04 / FASE-A
**Objetivo**: Diagnosticar y aislar los 3 archivos de test patológicos para habilitar el trabajo seguro sobre el área de propuesta comercial (FASE-B).
**Dependencias**: Ninguna (primera fase)
**Duración estimada**: 1-2 horas
**Skill**: `.agents/workflows/phased_project_executor.md`
**Modo de ejecución**: Agente principal **DIRECTO** (código+tests puro — §Regla código+tests; NO delegar: los tests requieren imports del venv del proyecto).

---

## Contexto

Las lecciones L1/L11 del plan anterior documentan 3 archivos patológicos que bloquearon
el equipo 2 veces (suite completa → ~8GB RAM / cuelgue indefinido):

| Archivo | Síntoma |
|---------|---------|
| `tests/commercial_documents/test_proposal_generator.py` | Fuga de memoria ~8GB RAM |
| `tests/commercial_documents/test_price_consistency.py` | Cuelgue indefinido |
| `tests/commercial_documents/test_proposal_generator_dict.py` | 16 de 38 fallos preexistentes |

El contexto fuente (§2.6 "Pendiente CRÍTICO") los declara **PREREQUISITO de cualquier
fix de RC1** porque los tests del área de propuesta son precisamente los patológicos.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A | ⬜ En curso (esta sesión) |

### Base Técnica Disponible
- Tests baseline: 3,215 (`python -m pytest --collect-only -q`)
- Directorio de cuarentena existente: `tests/_archived_broken_tests/`
- `pytest.ini` en raíz

---

## Tareas

### T1: Diagnóstico mínimo de cada archivo patológico
**Objetivo**: Confirmar el síntoma de cada archivo SIN ejecutarlos completos.

**Método seguro**:
- Leer el código de cada test (grep/read) e identificar el patrón causante
  (ej: generación combinatoria, fixtures que instancian el generador completo, bucles).
- Si se necesita ejecutar algo: SOLO tests individuales con timeout corto
  (`pytest archivo.py::test_x -x --timeout=60 > temp/fase_a_diag.txt 2>&1`).
- NUNCA ejecutar el archivo completo sin timeout. Si algo cuelga:
  `taskkill /F /IM python.exe /T`.

**Criterios de aceptación**:
- [ ] Causa probable documentada por archivo (1-2 líneas c/u) en el plan 09-documentacion.

### T2: Aislamiento (cuarentena) de los 3 archivos
**Objetivo**: Excluirlos de la colección estándar sin perderlos.

**Acción**:
- Mover los 3 archivos a `tests/_archived_broken_tests/commercial_documents/` (crear
  subdirectorio si no existe).
- **⚠️ CRÍTICO (CR-8)**: `pytest.ini` actual NO tiene `norecursedirs`. NO añadir
  `norecursedirs = _archived_broken_tests` global porque excluiría también los 22
  archivos que YA están allí (reduciendo collected mucho más de lo esperado).
  En su lugar, añadir `--ignore` específicos en `pytest.ini`:
  ```ini
  addopts = --ignore=tests/_archived_broken_tests/commercial_documents/test_proposal_generator.py --ignore=tests/_archived_broken_tests/commercial_documents/test_price_consistency.py --ignore=tests/_archived_broken_tests/commercial_documents/test_proposal_generator_dict.py
  ```
- Dejar un `README.md` en la ubicación de cuarentena con síntoma + fecha + referencia
  a este plan.

**Criterios de aceptación**:
- [ ] `python -m pytest --collect-only -q > temp/fase_a_collect.txt 2>&1` no recoge los 3 archivos.
- [ ] El conteo collected baja exactamente en el número de tests de los 3 archivos
      (NO más — los 22 archivos que ya están en `_archived_broken_tests/` siguen recolectándose).

### T3: Verificación del subconjunto seguro del área propuesta
**Objetivo**: Establecer la lista de tests SEGUROS del área que FASE-B podrá correr.

**Acción**:
- Ejecutar en lotes pequeños secuenciales (redirigido a archivo, L6) los tests de
  `tests/commercial_documents/` que ejercitan `v4_proposal_generator.py` y NO son
  patológicos (ej: `test_fase_f_financial_placeholders.py`, `test_financial_coherence.py`).
- Registrar la "lista segura" en `dependencias-fases.md` (notas de FASE-A).

**Criterios de aceptación**:
- [ ] Lista segura documentada (≥5 archivos) con resultado PASS/FAIL de cada uno.
- [ ] 0 regresiones en el subconjunto seguro.

---

## Tests Obligatorios

| Test | Comando | Criterio |
|------|---------|----------|
| Colección completa | `python -m pytest --collect-only -q > temp/fase_a_collect.txt 2>&1` | Sin los 3 patológicos |
| Subconjunto seguro | `python -m pytest tests/commercial_documents/test_financial_coherence.py -v > temp/fase_a_safe.txt 2>&1` | PASS |
| Validaciones | `python scripts/run_all_validations.py --quick` | TOTAL PASS (conteo dinámico del script) |

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. Actualizar `dependencias-fases.md` (FASE-A ✅ + lista segura en notas).
2. Actualizar `README.md` del plan (tabla de progreso).
3. Actualizar `09-documentacion-post-proyecto.md` (Sección D: conteo tests collected
   antes/después de la cuarentena; Sección E: archivos movidos).
4. Registrar la fase:
```bash
python scripts/log_phase_completion.py --fase FASE-A --desc "Cuarentena tests patologicos area propuesta (prerrequisito RC1)" --archivos-mod "pytest.ini" --tests "0" --check-manual-docs
```
**SIN `--release`** (L3/L9 — fase intermedia).

---

## Criterios de Completitud (CHECKLIST)

- [ ] 3 archivos patológicos fuera de la colección estándar
- [ ] Conteo collected documentado (antes 3,215 → después N)
- [ ] Lista segura de tests del área propuesta verificada y documentada
- [ ] `run_all_validations.py --quick` TOTAL PASS (conteo dinámico del script)
- [ ] `log_phase_completion.py` ejecutado SIN --release
- [ ] `dependencias-fases.md` y `09-documentacion-post-proyecto.md` actualizados

## Restricciones

- Máximo 60 iteraciones (R2).
- NUNCA ejecutar la suite completa de `tests/commercial_documents` (L1/L11).
- NO modificar código de producción en esta fase (solo infraestructura de tests).
- NO usar `git stash` (denegado por sandbox); si se necesita revertir: `git checkout HEAD -- <archivo>`.
