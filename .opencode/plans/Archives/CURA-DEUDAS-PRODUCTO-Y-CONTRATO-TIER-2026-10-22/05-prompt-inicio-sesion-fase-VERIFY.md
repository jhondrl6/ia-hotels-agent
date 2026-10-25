# FASE-VERIFY — Certificación formal de AC1–AC8 contra artefactos reales

**ID**: FASE-VERIFY · **Plan**: `CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22`
**Objetivo**: certificar que los ACs del plan se cumplen **en los artefactos que el sistema produjo** (E2E-PRE + E2E + evidencia de fases), no solo en los tests.
**Dependencias**: FASE-A…FASE-E2E ✅.
**Complejidad técnica**: MEDIA · **Duración estimada**: 2-3 horas
**Modo de ejecución**: **DIRECTO — NO DELEGABLE en la certificación** (§4.6 del executor): el AC se lee en el artefacto y quien certifica no puede escribir la matriz desde el resumen de un tercero (R2.4 · `L-CIM.12` · `L-T4A.5`); un reporte ajeno se re-verifica, así que delegar el juicio cuesta dos lecturas. **Excepción condicional, solo si el tope de 60 `tool_use` aprieta**: un único `Agent` de **solo lectura** para **enumerar** los cuatro greps residuales de la tarea 4 —el encargo lleva comandos y poblaciones verbatim—, sin escribir evidencia ni emitir veredictos; el agente principal **re-ejecuta** el predicado decisivo de cada grep antes de publicarlo y declara en `pre-vuelo` si usó la excepción o no. Ausencia de la declaración = se ejecutó directo.

## Contexto

Cada fase verificó sus criterios locales; esta fase certifica la integración coherente. El baseline de antes/después es la corrida del 2026-10-12 (`BLOQUEADO`, 2 `OVER_PRESENTATION`, 3.511.200 COP/mes, 11 brechas de `PainSolutionMapper`). El 39.600.000 COP/mes del reproductor sintético no es un criterio de esta fase.

**Claves exactas**: `revision_honestidad.json` trae `summary.over_presentations` y `findings[]`; **no** trae `critical_count`. El acta trae `verdict` y `conditional_reason`. El ZIP se lee en `deliveries/` con `suppressed:false`, sha y tamaño.

**Fuera del alcance de esta certificación** — hallazgos declarados al cerrar E2E el 2026-10-24, con dueño **Operador**, y que **no** se certifican, corrigen ni re-litigan aquí:

1. **El ZIP de la corrida mezcla dos generaciones.** Medido: 82 miembros, 26 con timestamp `20261012`, 28 con `20261024` y 22 assets en dos versiones dentro de `ASSETS/`; el `DeliveryPackager` barre el directorio de salida del hotel, que conserva la corrida anterior. Queda como `L33`. **AC7 se lee sobre el ZIP real publicado —existencia, `suppressed:false`, sha y tamaño—, no sobre su composición: la mezcla no invalida AC7 y no es criterio de esta fase.**
2. **`v4_complete_report.hotel_name` sale del slug de la URL** (`Donalfonsohotel`) en vez del `hotel.nombre` del YAML inyectado (`Hotel Don Alfonso`). Cosmético de marca; identidad y URL del run son correctas.

Los dos viven en `evidence/…/FASE-E2E/tabla-antes-despues.md` y en `10-analisis` §Seguimientos abiertos. Se **citan**; si se observan al leer los artefactos, se reportan como ya declarados, no como hallazgo nuevo.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A…FASE-E2E | ✅ |

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-T4A.5 | Un test puede pasar sin ejecutar la rama que dice certificar | Certificación por artefacto real, no por verde de tests |
| L-CIM.12 | Un control verde puede no medir la propiedad | Si un AC solo tiene “el string está en el código”, queda ⚠️ |
| L-R.4 | Regla sin verificador solo publicable si lo declara | Los huecos sin verificador mecánico se declaran |
| L-PF10 | Vacío ≠ ausente | “0 brechas” se cruza con el estado del detector, no se asume |

## Tareas (metodología mínima, sin código)

1. **Leer el output post-fix y el baseline**: `evidence/…/FASE-E2E-PRE/` y `evidence/…/FASE-E2E/` contra `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/`.
2. **Verificar cada AC contra artefacto real** (R2.4: AC sin clave legible = ⚠️, nunca ✅):
   - **AC1** → `revision_honestidad.json` → `summary.over_presentations == 0` en propuesta y diagnóstico + par rojo/verde de FASE-B.
   - **AC2** → `acta_revision.json` → `verdict`, `conditional_reason` (3 causas) + grep del literal viejo en la población declarada. **`P6.5` no se certifica aquí.**
   - **AC3** → diente de FASE-D (0 brechas en `get_detected_issues` y `PainSolutionMapper`; 0 COP; mutante) + `pain_ledger.json` → `entries` y `revision_alineacion.json` → `info.brechas_en_ledger` (errata `L34`, segunda pasada 2026-10-24: la clave no vive en el ledger ni bajo `summary`).
   - **AC4** → salida del check de sincronización cableado + test de getters y paridad de cinco tablas.
   - **AC5** → test de retiro de `spark` (exit 0, sin `AttributeError`) + par del guardián + `gap_analyzer` sin lector roto.
   - **AC6** → grep por símbolo de umbrales + tests de coherencia y `D27` post-D.
   - **AC7** → acta + `v4_complete_report.json` + `pain_ledger.json` + **ZIP real** (`suppressed:false`, sha/tamaño) + 0 `OVER_PRESENTATION` + pérdida 3.511.200/re-medida + 11 brechas re-medidas + **onboarding cargado desde una fuente que casa por URL**: `preflight.json` → `onboarding_source`, `rama_efectiva_del_loader` = `YAML_DE_DIR_CLIENTES`, `loader_devolvio` = `Hotel Don Alfonso`, `domain_confirmed: true`. El plan define AC7 con esta cláusula: si falta la clave del preflight, AC7 queda ⚠️ **aunque el ZIP sea real**.
   - **AC8** → score GBP `/90`; stub `found=False`/`STUB_RETIRADO`; `settings.yaml` sin claves muertas; `validar_arbitraje_etico` sin consumidor; docstring de `D23` = código; `Benchmarking.md` con fuente.
3. **Comparar antes/después**: tabla narrativo-técnica en evidencia.
4. **Greps residuales con población declarada**:
   - literal `APROBADO-CONDICIONAL-PENDING-ONBOARDING`: 0 en `modules/`, `tests/` y `main.py`; históricos en allowlist.
   - `SUPERPOSITION_FACTOR`: 0 lecturas ejecutables (AST), no 0 menciones; docstrings/config quedan como históricos.
   - claves inglesas del perfil GBP: 0 en los dos caminos.
   - `found=True` vacío del stub: 0.
5. **Completar la matriz** del `10-analisis` (todas las filas con Real/Status).
6. **Lecciones de la verificación** (o “sin lecciones nuevas”).
7. **Registro + validación**: `log_phase_completion.py` **SIN** `--release` + `run_all_validations.py --quick`.

## Tests Obligatorios

Ninguno (fase sin código). Verificación por lectura, comparación y grep con población.

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md`: FASE-VERIFY ✅.
2. `README.md`: progreso por referencia a `09` §D.
3. `09-documentacion-post-proyecto.md`: D/E de la verificación.
4. `10-analisis-post-implementacion.md`: matriz completa, lecciones y seguimientos.
5. `00-lecciones-capitalizadas.md`: anotar las lecciones citadas.
6. `evidence/…/FASE-VERIFY/`: matriz, greps, antes/después y `pre-vuelo` de la certificación.
7. **Derivados al día, como último paso del cierre** (herencia medida de FASE-A y FASE-B): re-publicar el artefacto de Wiring con `validate_wiring.py --write-report` si la fase añadió archivos versionados —un `.py` nuevo en `tests/` **o** en `evidence/` mueve contadores—, y re-publicar el par del índice con `build_lesson_index.py` si la fase anotó lecciones **citando IDs del vocabulario** en `00-lecciones` o `10-analisis` (la prosa que no cita ninguno no lo vence). Verificar los dos con `--check` y leer el exit **sin tubería**: `run_all_validations.py --quick` no goberna la frescura del índice, pero el hook `[6/8]` del pre-commit la corta y bloquea el commit.

Registro:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-VERIFY --fecha <fecha-de-cierre-de-esta-fase> \
    --desc "Certificación formal AC1-AC8 contra artefactos reales de E2E-PRE y E2E" \
    --check-manual-docs
```

## Criterios de Completitud (CHECKLIST)

- [ ] Matriz con todas las filas AC1–AC8 en Real/Status
- [ ] AC7 leído en ZIP real, no en un registro
- [ ] AC1 leído en `summary.over_presentations`, no en `critical_count`
- [ ] Greps residuales con población y allowlist; residuo declarado si existe
- [ ] `P6.5`/`D21` no certificados ni modificados
- [ ] `--quick` verde; cinco cortes sin commit; lecciones registradas
- [ ] Derivados re-publicados y verificados con `--check` como último paso (Wiring si la fase añadió archivos versionados; índice de lecciones si se citaron IDs del vocabulario), con el exit leído sin tubería

## Restricciones

- **NO** modifica código ni templates. **NO** ejecuta `v4complete`. **NO** toca `P6.5`, `T1_CERTIFIABLE_CLAUSES` ni archivos congelados.
- Un ✅ cuyo único respaldo es “el string está en el código” **no existe** (R2.4).
- Presupuesto: tope **60 tool-use**; corte «listo para revisión»; instrumento legado/no comparable si no aplica.

## Prompt de Ejecución

```bash
Actúa como especialista en el repo iah-cli. Ejecuta únicamente FASE-VERIFY del plan .opencode/plans/Archives/CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22.
Lee 05-prompt-inicio-sesion-fase-VERIFY.md, 01-plan-maestro.md §1, 00-lecciones-capitalizadas.md §2, dependencias-fases.md y workflow canónico.
OBJETIVO: certificar AC1-AC8 contra artefactos reales de E2E-PRE y E2E.
TAREAS: lectura de artefactos, verificación por AC, antes/después, greps con población, matriz del 10-analisis, lecciones, registro.
CRITERIOS: matriz completa; AC1 en summary.over_presentations; AC7 en ZIP real; P6.5 intacta.
VALIDACIONES: log_phase_completion.py sin --release; run_all_validations.py --quick.
```
