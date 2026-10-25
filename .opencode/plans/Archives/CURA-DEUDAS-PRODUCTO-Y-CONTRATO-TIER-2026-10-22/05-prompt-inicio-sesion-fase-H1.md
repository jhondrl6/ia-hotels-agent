# FASE-H1 — `D16` y `D24`: score honesto y stub retirado

**ID**: FASE-H1 · **Plan**: `CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22`
**Objetivo**: publicar el score GBP sobre `/90` y retirar la rama API que nunca se implementó (`D16`); declarar retirado el stub de Booking sin tocar el scraper real del producto (`D24`).
**Dependencias**: FASE-E ✅ y FASE-F ✅.
**Complejidad técnica**: MEDIA · **Duración estimada**: 2-3 horas
**Modo de ejecución**: **DIRECTO** (decisiones de producto ya registradas; imports + tests).

## Contexto

`D16`: `_calculate_gbp_score` suma un máximo de **90** puntos, pero el reporte publica `score/100`; el mismo competidor puede puntuarse por API (`_calculate_gbp_score`) o por estimación (`min(100, int((reviews / 10) * rating * 2))`). La rama API llama `_places_api_lookup`, que lanza `NotImplementedError`: la única varilla viva es la estimación. **Decisión del Operador: publicar `/90` y eliminar la rama API muerta.** No se renormaliza a 100 sin declararlo.

`D24`: `modules/scrapers/booking_scraper.py` es un stub que arma `found=True` con `rating`, `review_count` y `price_range` en `None` y `photos` vacío. El producto usa `autonomous_researcher.BookingScraper` (scraping real + fallback verificado); el stub solo lo consumen algunos tests. **Decisión del Operador: declarar muerto el stub y no tocar el scraper real.**

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A…FASE-F | ✅ |

### Base Técnica Disponible
- `modules/scrapers/gbp_auditor.py` (`_calculate_gbp_score`, `get_competitor_score`, `_places_api_lookup`, reporte `Score actual GBP`)
- `modules/scrapers/booking_scraper.py` (stub: método `scrape`, no `scrape_hotel`)
- `modules/scrapers/__init__.py` (exporta el stub)
- `modules/providers/autonomous_researcher.py` (`BookingScraper` real; no tocar)
- Tests: `tests/scrapers/test_booking_scraper.py` (scraper real), `tests/providers/test_autonomous_research_fase8.py` (importa el stub)

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-SR3 | Una sola fuente de verdad | Un denominador (`/90`) y una varilla viva; el stub no compite con el scraper real |
| L-NC10 | Texto estático que ignora la fuente dinámica | El reporte publica el denominador del cálculo, no un `/100` heredado |
| DA-C3 | vacío ≠ ausente | El stub publica `data_status=STUB_RETIRADO`, no `found=True` vacío |
| L-T4A.5 | Un test puede pasar sin ejecutar la rama que dice certificar | El test del stub afirma el estado retirado; el de D16 afirma `/90` y el techo 90 |

## Tareas

### Tarea 1: `D16` — denominador y rama API
**Objetivo**: el reporte GBP publica `score/90`; la rama API se retira o se declara no implementada, y la estimación se etiqueta como métrica distinta, no comparable con la rúbrica. Antes de cambiar el denominador, medir los consumidores de `score`/`geo_score` que asuman `/100`.
**Archivos afectados**: `modules/scrapers/gbp_auditor.py` (y consumidores que se midan).
**Criterios de aceptación**:
- [ ] El reporte publica `/90`; ningún texto publica `/100` para el score propio
- [ ] `get_competitor_score` no intenta una API inexistente; la estimación tiene `score_source=estimation` y una metodología explícita
- [ ] Los consumidores que asumían `/100` quedan corregidos o declarados
- [ ] Test: score 90 → `/90`; competidor por estimación ≠ rúbrica; mutante `/100` en rojo

### Tarea 2: `D24` — stub retirado, scraper real intacto
**Objetivo**: el stub de `modules/scrapers/booking_scraper.py` deja de presentarse como dato; se marca como retirado y sus tests se actualizan. No se toca `autonomous_researcher.BookingScraper`.
**Archivos afectados**: `modules/scrapers/booking_scraper.py`, `modules/scrapers/__init__.py`, tests que importan el stub.
**Criterios de aceptación**:
- [ ] `scrape` devuelve `found=False`, `data={}` y `data_status=STUB_RETIRADO`; nunca `found=True` vacío
- [ ] El export se marca legacy/deprecado o se retira, con test que lo declare
- [ ] `autonomous_researcher.BookingScraper` no cambia; sus tests siguen verdes
- [ ] Mutation: restaurar `found=True` vacío → test en rojo; par en evidencia

### Tarea 3: Tests y evidencia (AC8)
**Objetivo**: cubrir las dos decisiones con tests que lean el artefacto real.
**Criterios de aceptación**:
- [ ] Test del reporte GBP `/90` y del competidor por estimación
- [ ] Test del stub retirado y del scraper real intacto
- [ ] Par rojo/verde en `evidence/…/FASE-H1/`; `baseline-pre-post.md` con la resta

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| score `/90` | `tests/` (nuevo) | Reporte y cálculo usan el mismo denominador; rojo con `/100` |
| competidor por estimación | `tests/` (nuevo) | No hay API inexistente; la estimación se etiqueta |
| stub retirado | `tests/` (actualiza `test_autonomous_research_fase8.py` o nuevo) | `found=False` + `STUB_RETIRADO`; rojo con `found=True` |
| scraper real intacto | `tests/scrapers/test_booking_scraper.py` | Sigue verde sin cambios de producto |

**Comando de validación**: `./venv/Scripts/python.exe -m pytest tests/scrapers tests/providers <tests-nuevos> -q` + `run_all_validations.py --quick`.

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md`: FASE-H1 ✅.
2. `README.md`: progreso por referencia a `09` §D.
3. `09-documentacion-post-proyecto.md`: B/D/E de la fase.
4. `10-analisis-post-implementacion.md`: decisiones `D16`/`D24`, fila y lecciones.
5. `00-lecciones-capitalizadas.md`: anotar las lecciones citadas.
6. `evidence/…/FASE-H1/`: pares rojo/verde y `baseline-pre-post.md`.
7. **Derivados al día, como último paso del cierre** (herencia medida de FASE-A y FASE-B): re-publicar el artefacto de Wiring con `validate_wiring.py --write-report` si la fase añadió archivos versionados —un `.py` nuevo en `tests/` **o** en `evidence/` mueve contadores—, y re-publicar el par del índice con `build_lesson_index.py` si la fase anotó lecciones **citando IDs del vocabulario** en `00-lecciones` o `10-analisis` (la prosa que no cita ninguno no lo vence). Verificar los dos con `--check` y leer el exit **sin tubería**: `run_all_validations.py --quick` no goberna la frescura del índice, pero el hook `[6/8]` del pre-commit la corta y bloquea el commit.

Registro:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-H1 --fecha <fecha-de-cierre-de-esta-fase> \
    --desc "D16 score /90 sin API muerta y D24 stub retirado sin tocar el scraper real (AC8)" \
    --archivos-nuevos "<rutas nuevas>" --archivos-mod "<rutas modificadas>" --tests "N" --check-manual-docs
```

## Criterios de Completitud (CHECKLIST)

- [ ] Reporte `/90`; rama API retirada/declarada; consumidores medidos
- [ ] Stub retirado con `found=False`/`STUB_RETIRADO`; scraper real intacto
- [ ] Pares rojo/verde; `--quick` verde; cinco cortes sin commit
- [ ] Lecciones registradas; evidencia preservada
- [ ] Derivados re-publicados y verificados con `--check` como último paso (Wiring si la fase añadió archivos versionados; índice de lecciones si se citaron IDs del vocabulario), con el exit leído sin tubería

## Restricciones

- Presupuesto: tope **60 tool-use**; corte «listo para revisión»; instrumento legado/no comparable si no aplica.
- No tocar `autonomous_researcher.BookingScraper`, el contrato de claves GBP (FASE-D), los umbrales (FASE-F) ni archivos congelados. Sin `v4complete`. Citas por símbolos (R2.2).

## Prompt de Ejecución

```bash
Actúa como especialista en el repo iah-cli. Ejecuta únicamente FASE-H1 del plan .opencode/plans/Archives/CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22.
Lee 05-prompt-inicio-sesion-fase-H1.md, 01-plan-maestro.md §1, §2, §4 y §5, 00-lecciones-capitalizadas.md §2, dependencias-fases.md y workflow canónico.
OBJETIVO: D16 con score /90 y sin API muerta; D24 con stub retirado y scraper real intacto.
TAREAS: 1 denominador/rama API, 2 stub retirado y tests, 3 pares rojo/verde y evidencia.
CRITERIOS: AC8 (score /90, stub STUB_RETIRADO, scraper real intacto); mutantes en rojo.
VALIDACIONES: pytest; --quick; log_phase_completion.py al cierre.
```
