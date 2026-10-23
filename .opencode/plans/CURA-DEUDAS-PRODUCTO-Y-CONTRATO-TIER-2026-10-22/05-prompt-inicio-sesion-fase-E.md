# FASE-E — `R2`: un solo lector de benchmarks y cinco tablas derivadas o retiradas

**ID**: FASE-E · **Plan**: `CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22`
**Objetivo**: que `BenchmarkLoader` lea el JSON publicado en todos sus getters, que las cinco tablas regionales dejen de ser copias independientes y que la suite cablee el verificador que compara valores sin perder el parseo/versión.
**Dependencias**: FASE-A ✅; ejecutar antes de FASE-F y FASE-H2.
**Complejidad técnica**: ALTA · **Duración estimada**: 3-4 horas
**Modo de ejecución**: **DIRECTO** (decisión arquitectónica); la verificación de getters es delegable con `Agent`.

## Contexto

`get_regional_data` busca `regiones` en el nivel superior del JSON y nunca ve las anidadas en `v25_config`: todo consumidor recibe `DEFAULT_DATA["regiones"]["default"]` y el argumento `region` se ignora. Seis de siete getters devuelven los dicts de `DEFAULT_DATA`; solo `get_plan_versions` lee dato real. Pero la causa raíz es más ancha: `gap_analyzer.revpar_targets` conserva valores hardcodeados, `ScraperFallback._load_benchmarks` normaliza el esquema con su propio fallback regional, `report_builder` instancia los dos lectores y `validate_benchmark_sync.py` solo compara el maestro contra `v25_config`, no contra las otras tablas. Reparar solo `BenchmarkLoader` deja la divergencia viva.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A | ✅ |

### Base Técnica Disponible
- `modules/utils/benchmarks.py` (`BenchmarkLoader`, `DEFAULT_DATA`)
- `modules/scrapers/scraper_fallback.py` (`_load_benchmarks`, fallback regional)
- `modules/analyzers/gap_analyzer.py` (`revpar_targets`)
- `modules/generators/report_builder.py` (`get_owner_bundle`, los dos lectores)
- `modules/utils/financial_factors.py`, `modules/financial_engine/package_recommender.py`, `modules/utils/dynamic_impact.py`
- `data/benchmarks/plan_maestro_data.json` (`v25_config.regiones`), `data/benchmarks/regional_adr_2026.json` (`master: true`)
- `scripts/validate_benchmark_sync.py`, `scripts/run_all_validations.py` (slot `[2/13]`)

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-NC10 | Texto estático que ignora la fuente dinámica de verdad | Tarea 1 decide por escrito el destino de los cinco bloques de `DEFAULT_DATA` |
| L-QW.1 | Comprobar la clave de una operación no es verificar su contenido | Tarea 3 cablea el verificador que compara valores |
| L-ENT.9 | Un proveedor configurado no es un proveedor ejercitado | Tarea 4 prueba los getters contra el JSON y deja un solo lector |
| L-P3A.2 | La clave correcta la dicta el parser | Tarea 2 usa `v25_config.regiones`, `precio_promedio`/`ocupacion`, no nombres supuestos |
| L-SR3 | Una sola fuente de verdad | Las cinco tablas se derivan o se retiran |

## Tareas

### Tarea 1: Decisión escrita de los cinco bloques
**Objetivo**: declarar si `actividad_gbp_pesos`, `kpis_objetivo_v23`, `terminologia_cliente`, `disclaimers_cliente` y `certificados` se publican en el JSON o si `DEFAULT_DATA` es su maestro declarado. **Default**: `DEFAULT_DATA` maestro por escrito, con assert de coherencia y nota en el módulo; publicación en el JSON como seguimiento.
**Criterios de aceptación**:
- [ ] Decisión escrita en `10-analisis` §Decisiones antes de tocar el lector
- [ ] Assert/test que enumera exactamente los cinco bloques y falla si aparece un sexto sin declaración

### Tarea 2: Puente de esquema y lector único
**Objetivo**: `BenchmarkLoader` normaliza `v25_config.regiones` y el nivel superior; deriva `revpar_cop = precio_promedio × ocupacion`; `ScraperFallback` usa el mismo lector o se retira su fallback regional; `gap_analyzer.revpar_targets` se deriva o se retira; `report_builder` deja de instanciar dos lectores sin razón.
**Archivos afectados**: `modules/utils/benchmarks.py`, `modules/scrapers/scraper_fallback.py`, `modules/analyzers/gap_analyzer.py`, `modules/generators/report_builder.py`, `modules/utils/financial_factors.py`, `modules/financial_engine/package_recommender.py`, `modules/utils/dynamic_impact.py`.
**Criterios de aceptación**:
- [ ] `get_regional_data('caribe')` ≠ `default` y cada getter devuelve dato real publicado
- [ ] `revpar_cop` derivado coincide con el maestro donde el maestro lo tiene
- [ ] `gap_analyzer.revpar_targets` y el fallback de `ScraperFallback` se declaran derivados o se retiran; no quedan valores independientes
- [ ] `report_builder` usa un solo lector (o declara por escrito por qué no)

### Tarea 3: Cablear el verificador real (`N6`)
**Objetivo**: `validate_benchmark_sync.py` ocupa el chequeo de sincronización **sin eliminar** la comprobación de parseo/versión; el check compara valores y falla con un mutante.
**Archivos afectados**: `scripts/run_all_validations.py`.
**Criterios de aceptación**:
- [ ] El check en verde significa “valores comparados y coinciden” y “JSON/versión leídos”
- [ ] Mutante: corromper un ADR/ocupación → el check en rojo
- [ ] La etiqueta `[2/13]` conserva su ordinal y el denominador dinámico

### Tarea 4: Tests contra el JSON publicado
**Objetivo**: getters verificados contra el artefacto real; incluir `get_all_regions` (o eliminarlo si se decide que no tiene consumidor).
**Criterios de aceptación**:
- [ ] Test de getters por región; test del `revpar` derivado vs maestro
- [ ] Test de paridad de las cinco tablas: maestro, `v25_config`, `Benchmarking.md`, `revpar_targets`/derivado y `ScraperFallback`/derivado
- [ ] Par pre/post (R2.3) y `baseline-pre-post.md` con la resta

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| getters vs JSON publicado | `tests/` (nuevo) | Dato real por región; rojo con valor corrompido |
| paridad de cinco tablas | `tests/` (nuevo) | Las fuentes derivadas coinciden; rojo si una copia diverge |
| check de sincronización cableado | `tests/` o verificación del check | Compara valores y conserva parseo; rojo con mutante |
| `get_all_regions` | `tests/` (nuevo o retiro) | Devuelve regiones reales o se declara sin consumidor |

**Comando de validación**: `./venv/Scripts/python.exe -m pytest <tests-nuevos> -q` + `./venv/Scripts/python.exe scripts/validate_benchmark_sync.py` + `run_all_validations.py --quick`.

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md`: FASE-E ✅.
2. `README.md`: progreso por referencia a `09` §D.
3. `09-documentacion-post-proyecto.md`: B/D/E de la fase.
4. `10-analisis-post-implementacion.md`: decisión de los cinco bloques, fila, lecciones y seguimientos.
5. `00-lecciones-capitalizadas.md`: anotar las lecciones citadas.
6. `evidence/…/FASE-E/`: crudos, mutantes, paridad y `baseline-pre-post.md`.

Registro:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-E --fecha <fecha-de-cierre-de-esta-fase> \
    --desc "R2: lector único de benchmarks, cinco tablas derivadas/retiradas y verificador real cableado (D25-ter/N4/N5/N6, AC4)" \
    --archivos-nuevos "<rutas nuevas>" --archivos-mod "<rutas modificadas>" --tests "N" --check-manual-docs
```

## Criterios de Completitud (CHECKLIST)

- [ ] Destino de los cinco bloques escrito antes del fix
- [ ] Getters leen dato real; regiones distintas devuelven valores distintos donde el maestro los tiene
- [ ] Cinco tablas derivadas o retiradas; paridad en rojo si una diverge
- [ ] Check de sincronización con valores y parseo; `--quick` verde
- [ ] Cinco cortes sin commit; lecciones registradas; evidencia preservada

## Restricciones

- Presupuesto: tope **60 tool-use**; corte «listo para revisión»; instrumento legado/no comparable si no aplica.
- **No** migrar umbrales (`D25`/`D25-bis`/`D27` → FASE-F) ni `Benchmarking.md` (FASE-H2). No tocar archivos congelados ni `v4complete`. Citas por símbolos (R2.2).

## Prompt de Ejecución

```bash
Actúa como especialista en el repo iah-cli. Ejecuta únicamente FASE-E del plan .opencode/plans/CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22.
Lee 05-prompt-inicio-sesion-fase-E.md, 01-plan-maestro.md §1, §2, §4 y §5, 00-lecciones-capitalizadas.md §2, dependencias-fases.md y workflow canónico.
OBJETIVO: un solo lector de benchmarks, cinco tablas derivadas/retiradas y verificador real cableado.
TAREAS: 1 decisión de los cinco bloques, 2 puente de esquema y lector único, 3 cablear validate_benchmark_sync sin perder parseo, 4 tests de getters y paridad.
CRITERIOS: AC4 (getters reales, cinco tablas, sync con valores); mutante del check en rojo.
VALIDACIONES: pytest; validate_benchmark_sync.py; --quick; log_phase_completion.py al cierre.
```
