# FASE-B — Ítem A: render condicionado al `evidence_tier` para los 2 hallazgos reales

**ID**: FASE-B · **Plan**: `CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22`
**Objetivo**: neutralizar los **2** claims de totalidad que el revisor emitió en la propuesta, con variante honesta para tier no-A, y aplicar el mismo contrato al diagnóstico; el verde de Bot 4 pasa a ser estructural.
**Dependencias**: FASE-A ✅.
**Complejidad técnica**: ALTA · **Duración estimada**: 3-4 horas
**Modo de ejecución**: **DIRECTO** (invoca el revisor real; decisión de copy comercial).

## Contexto

El baseline del 2026-10-12 emitió **2** `OVER_PRESENTATION` CRITICAL sobre `02_PROPUESTA_COMERCIAL.md` en «Protección total para usted» y «Transparencia total». La medición del revisor es **10 literales → 6 descartados por filtro estructural → 2 emitidos**. El grep de 7 líneas de la plantilla incluye labels financieros legítimos («Fuga total estimada», «Total recuperación proyectada», «100% suyo»); **no se reescriben las 7**: se corrigen los 2 claims emitidos y se documentan los 5 descartados. El diagnóstico viaja en el mismo paquete y también debe cumplir el contrato.

La propuesta ya tiene `{{if ...}}` y `_preprocess_conditionals` en `v4_proposal_generator.py`. El diagnóstico **no** preprocesa condicionales: `v4_diagnostic_generator.py` usa `Template.safe_substitute` directo y su plantilla tiene 0 `{{if}}`. La fase debe elegir: añadir el mismo preprocesador o precomputar dos strings (`garantias_titulo`, `garantias_cuerpo`) desde Python.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A | ✅ |

### Base Técnica Disponible
- `modules/commercial_documents/v4_proposal_generator.py` (`_preprocess_conditionals`, `_render_template`, `financial_evidence_tier`)
- `modules/commercial_documents/v4_diagnostic_generator.py` (`_render_template`, datos de `evidence_tier`/`financial_disclaimer`)
- `modules/commercial_documents/templates/propuesta_v6_template.md` y `diagnostico_v6_template.md`
- `modules/quality_gates/tribunal/honesty_reviewer.py` (`coincidencias_lenguaje_de_verificacion`, grupo de cuantificadores, filtro estructural)

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-P3A.2 | La clave correcta la dicta el parser del lector | La condición se evalúa sobre el tier tal como lo serializa el motor |
| L-T4A.5 | Un test puede pasar sin ejecutar la rama que dice certificar | Mutation check: desactivar la condición → el revisor vuelve a emitir los 2 claims |
| L-VUP-5 | Una fase que no produce ni un rojo es falso verde potencial | El primer verde se reporta sospechoso hasta que el mutante produce el rojo |
| L-R.4 | Regla sin verificador solo publicable si lo declara | El par rojo/verde se declara en el cierre |

## Tareas

### Tarea 1: Inventario con la función real del revisor
**Objetivo**: publicar las líneas candidatas con el barrido que invoca la función del revisor (bandera `re.IGNORECASE` incluida), no el grep suelto.
**Criterios de aceptación**:
- [ ] Crudo en `evidence/…/FASE-B/inventario-candidatas.txt` con las dos pasadas y el contraste (8 vs 10, falso 0 documentado)
- [ ] La tabla separa **2 emitidos** de **6 descartados**; los 5 labels financieros quedan marcados como “no tocar”

### Tarea 2: Variantes honestas en propuesta y diagnóstico
**Objetivo**: con tier A se emite la variante respaldada por evidencia; con tier no-A se emite la variante honesta, sin “Protección total” ni “Transparencia total”. La propuesta usa `{{if}}`; el diagnóstico recibe el mismo contrato mediante preprocesador o strings precomputados.
**Archivos afectados**: `modules/commercial_documents/v4_proposal_generator.py`, `modules/commercial_documents/v4_diagnostic_generator.py`, `modules/commercial_documents/templates/propuesta_v6_template.md`, `modules/commercial_documents/templates/diagnostico_v6_template.md`.
**Criterios de aceptación**:
- [ ] Los 2 claims tienen variante por tier en **ambos** documentos
- [ ] Los labels “Fuga total”, “Total recuperación” y “100% suyo” siguen renderizados sin cambios
- [ ] La decisión de copy queda escrita en `10-analisis` §Decisiones (DA-PLAN-2)

### Tarea 3: Diente con el revisor real (AC1)
**Objetivo**: test que renderice propuesta y diagnóstico con tier B+ y afirme `summary.over_presentations == 0`; con tier A, la variante de totalidad es la única posible y el escáner sigue apagado por diseño.
**Criterios de aceptación**:
- [ ] El test invoca `HonestyReviewer` sobre el texto renderizado; no busca strings sueltos
- [ ] Par rojo/verde en evidencia: condición del render desactivada → el revisor emite los 2 claims
- [ ] La resta `10 → 6 → 2` se documenta como “antes” y `0 emitidos` como “después”

### Tarea 4: Diagnóstico y tests existentes
**Objetivo**: el diagnóstico no queda como excepción; se re-ejecuta el fixture de `test_evidence_tier_precedencia_unica_ac11.py` que usa “Transparencia total” como prosa de prueba, para confirmar que no se está confundiendo un fixture con la plantilla.
**Criterios de aceptación**:
- [ ] El diagnóstico tiene su propio test de render B+/A
- [ ] El fixture existente se re-ejecuta y, si la frase cambió de contrato, se actualiza con justificación

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| render B+ sin sobre-presentación | `tests/` (nuevo) | `summary.over_presentations == 0` con el revisor real, en propuesta y diagnóstico |
| render A con variante respaldada | `tests/` (nuevo) | La variante de tier A es la única posible; el escáner sigue apagado por diseño |
| labels financieros intactos | `tests/` (nuevo) | “Fuga total”/“Total recuperación”/“100% suyo” siguen presentes |

**Comando de validación**: `./venv/Scripts/python.exe -m pytest <tests-nuevos> -q` + `run_all_validations.py --quick`. Par pre/post (R2.3).

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md`: FASE-B ✅.
2. `README.md`: progreso por referencia a `09` §D.
3. `09-documentacion-post-proyecto.md`: B/D/E de la fase.
4. `10-analisis-post-implementacion.md`: fila, lecciones, decisión de copy, métricas por referencia.
5. `00-lecciones-capitalizadas.md`: anotar el resultado de las lecciones citadas.
6. `evidence/…/FASE-B/`: inventario, pares rojo/verde y `baseline-pre-post.md` con la resta.

Registro:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-B --fecha <fecha-de-cierre-de-esta-fase> \
    --desc "Ítem A: 2 claims neutralizados por tier en propuesta y diagnóstico; revisor real y diente (AC1)" \
    --archivos-mod "<rutas>" --tests "N" --check-manual-docs
```

## Criterios de Completitud (CHECKLIST)

- [ ] Inventario con la función real del revisor y la resta 10→6→2
- [ ] Solo los 2 claims emitidos se neutralizan; los labels financieros siguen
- [ ] Propuesta y diagnóstico con variante por tier
- [ ] `summary.over_presentations == 0` con B+; mutante rojo; par en evidencia
- [ ] `--quick` verde; cinco cortes sin commit; lecciones registradas

## Restricciones

- Presupuesto: tope **60 tool-use**; corte «listo para revisión»; instrumento legado/no comparable si no aplica.
- **No** ejecutar `v4complete` (la prueba es E2E-PRE/E2E). **No** tocar `judge.py`/`acta_writer.py` (FASE-C), `P6.5`, `T1_CERTIFIABLE_CLAUSES`, umbrales (FASE-F) ni archivos congelados.
- **No** reescribir las 7 líneas del grep; solo los 2 claims emitidos. Citas por símbolos (R2.2).

## Prompt de Ejecución

```bash
Actúa como especialista en el repo iah-cli. Ejecuta únicamente FASE-B del plan .opencode/plans/CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22.
Lee 05-prompt-inicio-sesion-fase-B.md, 01-plan-maestro.md §1, §2, §4 y §5, 00-lecciones-capitalizadas.md §2, dependencias-fases.md y workflow canónico.
OBJETIVO: neutralizar los 2 claims de totalidad con variante por tier en propuesta y diagnóstico; verde estructural de Bot 4.
TAREAS: 1 inventario con el revisor real, 2 variantes en propuesta y diagnóstico, 3 diente AC1 + mutation, 4 diagnóstico y fixture existente.
CRITERIOS: AC1 (summary.over_presentations == 0 con B+; labels financieros intactos; mutante rojo).
VALIDACIONES: pytest; --quick; log_phase_completion.py al cierre.
```
