# FASE-H2 — Limpieza: `D18`, `D22`, `D23` y `D20`

**ID**: FASE-H2 · **Plan**: `CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22`
**Objetivo**: retirar la configuración LEGACY sin lector, retirar el dead code de `validar_arbitraje_etico`, alinear el docstring de `_check_claim_vs_evidence` con su rama y declarar la fuente de `Benchmarking.md` frente al JSON maestro.
**Dependencias**: FASE-H1 ✅; FASE-E ✅ (las cinco tablas ya están derivadas/retiradas).
**Complejidad técnica**: BAJA · **Duración estimada**: 1-2 horas
**Modo de ejecución**: **DIRECTO**; `D20` (documental) es delegable con `Agent`.

## Contexto

`D18`: los `thresholds` de `config/settings.yaml` (`gbp_min_score`, `schema_required`, `min_reviews`, `min_photos`) están declarados LEGACY y ningún lector de producción los consume; el único consumo del archivo es `scrapers.requests`. `D22`: `validar_arbitraje_etico` está definido y testeado sin consumidor de producción; el gate ético que corre es `EthicsGate` vía `run_publication_gates`. `D23`: el docstring de `_check_claim_vs_evidence` dice `or`/`>` y el código hace `and`/`>=` (dos divergencias). `D20`: `Benchmarking.md` y las tablas regionales divergen; FASE-E ya derivó/retiró las copias, así que esta fase solo documenta la fuente.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A…FASE-H1 | ✅ |

### Base Técnica Disponible
- `config/settings.yaml` (cabecera LEGACY y `thresholds`)
- `tests/test_audit_alignment.py` (consumidor de los thresholds)
- `modules/quality/financial_coherence_validator.py` (`validar_arbitraje_etico`)
- `tests/quality_gates/test_financial_coherence_validator.py`
- `modules/quality_gates/commercial_gate.py` (`_check_claim_vs_evidence`)
- `data/benchmarks/Benchmarking.md`, `data/benchmarks/regional_adr_2026.json` (MASTER), `data/benchmarks/plan_maestro_data.json`

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-CST-7 | Curar el texto de una cláusula no cura la forma del defecto en sus hermanas | `D23` tiene dos divergencias; se corrigen ambas, no solo el `or`/`and` |
| L-NC10 | Texto estático que ignora la fuente dinámica | `Benchmarking.md` declara su fuente y no compite con el JSON |
| L-P3A.2 | La clave correcta la dicta el parser | El test de `D23` usa la frontera real (`rating == 4.0`) |
| L-R.4 | Regla sin verificador solo publicable si lo declara | `D20` documental se declara sin mutante |

## Tareas

### Tarea 1: `D18` — retirar thresholds LEGACY
**Objetivo**: quitar de `config/settings.yaml` las cuatro claves `thresholds` sin lector de producción; conservar `scrapers.requests` y el resto de la configuración activa; actualizar el test que las consumía.
**Criterios de aceptación**:
- [ ] Las cuatro claves ya no existen o están marcadas como no configuración, con motivo
- [ ] `scrapers.requests` y los lectores de producción siguen funcionando
- [ ] `tests/test_audit_alignment.py` se actualiza; no queda un test que certifique la configuración muerta

### Tarea 2: `D22` — retirar el dead code
**Objetivo**: retirar `validar_arbitraje_etico` y su test si no tiene consumidor de producción, o declararla muerta con dueño. No recablear `EthicsGate`.
**Criterios de aceptación**:
- [ ] Grep de producción: 0 consumidores de `validar_arbitraje_etico`
- [ ] La función y su test se retiran, o se declara su estado con dueño; no se deja como gate aparente
- [ ] El gate ético real (`EthicsGate` vía `run_publication_gates`) no cambia

### Tarea 3: `D23` — docstring y frontera
**Objetivo**: el docstring de `_check_claim_vs_evidence` describe `place_found and gbp_rating >= 4.0`; el caso frontera `rating == 4.0` se juzga como el código.
**Criterios de aceptación**:
- [ ] Docstring sin `or` ni `>`; coincide con la rama real
- [ ] Test de frontera: `place_found=True`, `rating=4.0` → el comportamiento es el del código (`>=`), no el del texto viejo
- [ ] No se cambia la lógica del gate, solo la prosa y el test de frontera

### Tarea 4: `D20` — fuente de `Benchmarking.md`
**Objetivo**: `Benchmarking.md` se actualiza o se marca frente al JSON maestro; las tablas que FASE-E derivó/retiró se declaran; no se mueven valores del JSON MASTER.
**Criterios de aceptación**:
- [ ] Cada tabla regional declara MASTER / derivada / retirada
- [ ] La divergencia que persista por diseño queda documentada, con su motivo
- [ ] No se modifican valores de `regional_adr_2026.json` ni de `plan_maestro_data.json`

### Tarea 5: Evidencia (AC8)
**Objetivo**: par pre/post y crudo de los greps; tests verdes.
**Criterios de aceptación**:
- [ ] `baseline-pre-post.md` con la resta
- [ ] Grep de `validar_arbitraje_etico` y de los thresholds LEGACY con 0 en producción
- [ ] Test de frontera de `D23` verde

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| thresholds LEGACY | `tests/test_audit_alignment.py` (actualizado) | No certifica las claves retiradas |
| `validar_arbitraje_etico` | test propio (retirado o actualizado) | 0 consumidores de producción |
| frontera `D23` | `tests/quality_gates/` (nuevo) | `rating=4.0` se juzga como `>=` |
| `D20` | documental | Cada tabla declara su fuente |

**Comando de validación**: `./venv/Scripts/python.exe -m pytest tests/test_audit_alignment.py tests/quality_gates <tests-nuevos> -q` + `run_all_validations.py --quick`.

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md`: FASE-H2 ✅.
2. `README.md`: progreso por referencia a `09` §D.
3. `09-documentacion-post-proyecto.md`: B/D/E de la fase.
4. `10-analisis-post-implementacion.md`: fila, lecciones y seguimientos.
5. `00-lecciones-capitalizadas.md`: anotar las lecciones citadas.
6. `evidence/…/FASE-H2/`: crudos, par pre/post y `baseline-pre-post.md`.

Registro:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-H2 --fecha <fecha-de-cierre-de-esta-fase> \
    --desc "D18 thresholds LEGACY retirados, D22 dead code retirado, D23 docstring honesto y D20 fuente declarada (AC8)" \
    --archivos-nuevos "<rutas nuevas>" --archivos-mod "<rutas modificadas>" --tests "N" --check-manual-docs
```

## Criterios de Completitud (CHECKLIST)

- [ ] `settings.yaml` sin las cuatro claves muertas; `scrapers.requests` intacto
- [ ] `validar_arbitraje_etico` sin consumidor de producción y retirado/declarado
- [ ] Docstring de `D23` = código; frontera 4.0 probada
- [ ] `Benchmarking.md` con fuente declarada; JSON MASTER intacto
- [ ] `--quick` verde; cinco cortes sin commit; lecciones registradas

## Restricciones

- Presupuesto: tope **60 tool-use**; corte «listo para revisión»; instrumento legado/no comparable si no aplica.
- **No** tocar el contrato GBP (FASE-D), umbrales (FASE-F), `autonomous_researcher.BookingScraper`, `EthicsGate`, `S-CST-1` ni archivos congelados. Sin `v4complete`. Citas por símbolos (R2.2).

## Prompt de Ejecución

```bash
Actúa como especialista en el repo iah-cli. Ejecuta únicamente FASE-H2 del plan .opencode/plans/CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22.
Lee 05-prompt-inicio-sesion-fase-H2.md, 01-plan-maestro.md §1, §2, §4 y §5, 00-lecciones-capitalizadas.md §2, dependencias-fases.md y workflow canónico.
OBJETIVO: D18 thresholds LEGACY, D22 dead code, D23 docstring/frontera y D20 fuente declarada.
TAREAS: 1 thresholds, 2 dead code, 3 docstring y frontera, 4 Benchmarking.md, 5 evidencia.
CRITERIOS: AC8 (config limpia, dead code retirado, docstring honesto, fuente declarada); --quick verde.
VALIDACIONES: pytest; --quick; log_phase_completion.py al cierre.
```
