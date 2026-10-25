# FASE-F — `R3`: umbrales por semántica y factores con fuente única (`D25`, `D25-bis`, `D27`)

**ID**: FASE-F · **Plan**: `CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22`
**Objetivo**: declarar un vocabulario de umbrales de fotos por **semántica** (no colapsar 5/10/15/20/40 en un valor), eliminar el doble default de `recovery_factors.realistic` y renombrar las constantes de pérdida que sobrevivan a FASE-D.
**Dependencias**: FASE-D ✅ y FASE-E ✅.
**Complejidad técnica**: MEDIA · **Duración estimada**: 2-3 horas
**Modo de ejecución**: **DIRECTO** (imports + tests); el barrido mecánico de sitios es delegable con `Agent`.

## Contexto

`D25` no es “cuatro valores distintos”: son **cinco valores (5, 10, 15, 20, 40) en 11 sitios de comparación en 7 módulos**, con semánticas distintas. Un hotel con 14 fotos cobra +10 en la rúbrica, es marcado “Pocas fotos” por `gbp_auditor` y no es marcado por `dynamic_impact`. Forzar un único número sería el defecto contrario al que se cura. `D25-bis`: `recovery_factors.realistic` vale `0.20` en el dict de respaldo y en el default del `.get()`, mientras el YAML dice `0.35`. `D27`: tres `PERDIDA_MENSUAL_BASE` con tres semánticas; FASE-D puede retirar la de `gbp_leak_detector`, así que esta fase **re-mide** antes de renombrar.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A…FASE-E | ✅ |

### Base Técnica Disponible
- `config/regional_benchmarks.yaml` (destino de umbrales), `config/scenarios.yaml`, `config/settings.yaml` (header LEGACY)
- `modules/utils/dynamic_impact.py`, `modules/scrapers/gbp_auditor.py`, `modules/scrapers/gbp_leak_detector.py` (si sobrevive a D)
- `modules/financial_engine/opportunity_scorer.py`
- `modules/generators/report_builder.py`
- `modules/auditors/v4_comprehensive.py`
- `modules/commercial_documents/data_structures.py`
- `modules/commercial_documents/v4_diagnostic_generator.py`
- `modules/commercial_documents/v4_proposal_generator.py` (`_load_scenario_config`, `recovery_factors.get('realistic', 0.20)`)

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-SR3 | Una sola fuente de verdad para el estado de un servicio | Un sitio por umbral nombrado, no un valor único para todos |
| L-NC10 | Texto estático que ignora la fuente dinámica | El default duplicado se elimina o se vuelve assert contra el YAML |
| L-V2 | Quien cambia un contrato barre sus consumidores | El rename de constantes barre los módulos y tests que sobrevivan |
| L-T4A.5 | Un test puede pasar sin ejecutar la rama que dice certificar | Test de coherencia que falla si el YAML y el default divergen |
| L-P3A.2 | La clave correcta la dicta el parser | Los nombres de umbral se leen del config, no de la costumbre |

## Tareas

### Tarea 1: Vocabulario semántico de umbrales
**Objetivo**: sustituir los cinco valores sueltos por umbrales con nombre y semántica propia, por ejemplo `MIN_FOTOS_BRECHA`, `FOTOS_OPORTUNIDAD`, `FOTOS_RUBRICA_EXCELENTE` y `FOTOS_TARGET_DIAGNOSTICO`, cada uno en un sitio y con relaciones explícitas (`MIN ≤ OPORTUNIDAD ≤ TARGET`). No se colapsan en una sola clave.
**Archivos afectados**: `config/regional_benchmarks.yaml`, `modules/utils/dynamic_impact.py`, `modules/financial_engine/opportunity_scorer.py`, `modules/scrapers/gbp_auditor.py`, `modules/generators/report_builder.py`, `modules/auditors/v4_comprehensive.py`, `modules/commercial_documents/data_structures.py`, `modules/commercial_documents/v4_diagnostic_generator.py`.
**Criterios de aceptación**:
- [ ] Cada umbral tiene nombre semántico y un solo sitio de definición
- [ ] Los 11 sitios de comparación leen el umbral nombrado; no queda un literal `5/10/15/20/40` de comparación sin justificación
- [ ] `TARGET_GBP_PHOTOS=40` deja de justificarse por un módulo muerto o se retira
- [ ] La relación entre umbrales se verifica en un test; no se fuerza un valor único

### Tarea 2: `D25-bis` una sola fuente
**Objetivo**: el dict de respaldo de `_load_scenario_config` y el default del `.get()` dejan de ser dos fuentes; se elimina el duplicado o se convierte en assert de coherencia con `scenarios.yaml` (`realistic: 0.35`).
**Criterios de aceptación**:
- [ ] Un solo valor vivo para `recovery_factors.realistic`
- [ ] Test de coherencia que pone en rojo una divergencia

### Tarea 3: `D27` nombres por semántica
**Objetivo**: re-medir las constantes después de FASE-D y renombrar las que sobrevivan (`PERDIDA_BASE_SIN_PERFIL`, `PERDIDA_BASE_CARIBE_CALIBRADA`, etc.); barrer consumidores y tests.
**Criterios de aceptación**:
- [ ] Grep del nombre genérico: 0 usos en la población de código/tests
- [ ] Cada constante que sobreviva tiene una semántica distinta y documentada
- [ ] Las huérfanas se eliminan o se reclaman con su semántica real

### Tarea 4: Tests de coherencia (AC6)
**Objetivo**: test que afirme “un sitio por umbral nombrado” o el assert de coherencia; conteos como delta con la resta publicada.
**Criterios de aceptación**:
- [ ] `baseline-pre-post.md` con la resta
- [ ] Mutante (divergencia introducida) en rojo
- [ ] El test no depende de un grep global de literales

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| coherencia YAML/defaults | `tests/` (nuevo) | Rojo si divergen; verde en el árbol |
| umbrales por semántica | `tests/` (nuevo) | Cada nombre lee su sitio; relaciones verificadas |
| rename `D27` | `tests/` (extensión) | Sin usos del nombre genérico; semánticas distintas |

**Comando de validación**: `./venv/Scripts/python.exe -m pytest <tests-nuevos> -q` + `run_all_validations.py --quick`.

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md`: FASE-F ✅.
2. `README.md`: progreso por referencia a `09` §D.
3. `09-documentacion-post-proyecto.md`: B/D/E de la fase.
4. `10-analisis-post-implementacion.md`: fila, lecciones y seguimientos.
5. `00-lecciones-capitalizadas.md`: anotar las lecciones citadas.
6. `evidence/…/FASE-F/`: crudo del barrido, mutantes y `baseline-pre-post.md`.
7. **Derivados al día, como último paso del cierre** (herencia medida de FASE-A y FASE-B): re-publicar el artefacto de Wiring con `validate_wiring.py --write-report` si la fase añadió archivos versionados —un `.py` nuevo en `tests/` **o** en `evidence/` mueve contadores—, y re-publicar el par del índice con `build_lesson_index.py` si la fase anotó lecciones **citando IDs del vocabulario** en `00-lecciones` o `10-analisis` (la prosa que no cita ninguno no lo vence). Verificar los dos con `--check` y leer el exit **sin tubería**: `run_all_validations.py --quick` no goberna la frescura del índice, pero el hook `[6/8]` del pre-commit la corta y bloquea el commit.

Registro:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-F --fecha <fecha-de-cierre-de-esta-fase> \
    --desc "R3: umbrales por semántica, D25-bis una fuente y D27 con nombres semánticos (AC6)" \
    --archivos-nuevos "<rutas nuevas>" --archivos-mod "<rutas modificadas>" --tests "N" --check-manual-docs
```

## Criterios de Completitud (CHECKLIST)

- [ ] Umbrales nombrados por semántica; un sitio cada uno; relaciones verificadas
- [ ] `D25-bis` con una sola fuente; mutante de divergencia en rojo
- [ ] `D27` re-medido post-D; sin nombre genérico; semánticas distintas
- [ ] `--quick` verde; cinco cortes sin commit; lecciones registradas
- [ ] `dependencias-fases.md` actualizado; evidencia preservada
- [ ] Derivados re-publicados y verificados con `--check` como último paso (Wiring si la fase añadió archivos versionados; índice de lecciones si se citaron IDs del vocabulario), con el exit leído sin tubería

## Restricciones

- Presupuesto: tope **60 tool-use**; corte «listo para revisión»; instrumento legado/no comparable si no aplica.
- **No** cambiar el contrato de claves (FASE-D), no tocar `Benchmarking.md` (FASE-H2), no tocar `S-CST-1` ni archivos congelados. Sin `v4complete`. Citas por símbolos (R2.2).

## Prompt de Ejecución

```bash
Actúa como especialista en el repo iah-cli. Ejecuta únicamente FASE-F del plan .opencode/plans/Archives/CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22.
Lee 05-prompt-inicio-sesion-fase-F.md, 01-plan-maestro.md §1, §2, §4 y §5, 00-lecciones-capitalizadas.md §2, dependencias-fases.md y workflow canónico.
OBJETIVO: umbrales por semántica, D25-bis con una fuente y D27 con nombres semánticos tras D.
TAREAS: 1 vocabulario de umbrales, 2 coherencia de defaults, 3 rename D27 post-D, 4 tests de coherencia + par pre/post.
CRITERIOS: AC6 (un sitio por umbral nombrado, no un valor único); mutante de divergencia en rojo.
VALIDACIONES: pytest; --quick; log_phase_completion.py al cierre.
```
