# T6 — sellos datados de las seis divergencias medidas el 2026-09-30

Regla con la que se escribieron: **texto original intacto**, un sello por item, anclas **por seccion** y no por
numero de linea, y **ninguna** introduccion de `archivo:linea` en documentos del corpus (la prosa viaja a los
packs y dispara el gate de citas: `validate_plan_citations.py`). Los sellos van entre `⟦ ... ⟧`, que es como esta
biblioteca marca una anotacion posterior sin reescribir el registro.

Balance de los caracter de marco comprobado despues de escribir: **54 abre / 54 cierra** en
`dependencias-fases.md` del plan VCF y balance correcto en los otros seis archivos tocados.

| # | Documento | Seccion anclada | Divergencia medida hoy | Lo que dice el sello |
|---|---|---|---|---|
| 1 | VCF `README.md` | cabecera, los cuatro momentos de la RELEASE | los cuatro siguen leydose pendientes | remite la vigencia a la **fila 5 de §Cadena** de `dependencias-fases.md` (seis miembros, cinco corridos el 2026-09-27 y el sexto en el archivado), y anade la medicion que lo confirma: `git ls-files` de la raiz del plan = **0** rutas, bajo `Archives/` = **18**, `CHANGELOG.md` abre con `[4.78.0]` y `VERSION.yaml` dice `4.78.0` |
| 2 | VCF `06-checklist-implementacion.md` | §Estado del cierre de FASE-RELEASE (2026-09-25), las dos casillas sin marcar | Q7/D8 y `--upload`/D9 figuran `PENDIENTE-AUTORIZACION`; archivado/commit/push figuran pendientes y «el plan sigue en `.opencode/plans/`» | dos sellos: uno por cada casilla. **Las casillas no se marcan** (la fuente unica del estado es la fila 5; marcarlas seria re-registrar con el instrumento de otra sesion), y el segundo corrige la ruta: el plan esta versionado **solo** bajo `Archives/` |
| 3 | VCF `09-documentacion-post-proyecto.md` | fila de FASE-RELEASE en §D y las cuatro casillas de §Seccion E | «Lo que **no** cerro: D8, D9, archivado, `--fix`/`--update-baseline`, commit y push» y `CHANGELOG`/`GUIA_TECNICA`/`REGISTRY`/`VERSION` sin marcar | sello en la fila (cinco de seis corridos, `--update-baseline` es el unico vivo y su turno era el archivado) y sello en el bloque de casillas con lo medido en disco: `VERSION.yaml` `4.78.0` con `release_date: 2026-09-25`, `CHANGELOG.md` con su entrada `[4.78.0]`, `docs/GUIA_TECNICA.md` con **1** mencion a 4.78.0 y `REGISTRY.md` con su entrada `## FASE-RELEASE (...) - 2026-09-25` escrita por su unico escritor |
| 4 | JEV `01-plan-maestro.md` | §Objetivo, premisa **P2**, las tres filas de §6 (`decision_client`, `tests/quality_gates/jev_pilot/`, `evidence/...`) y la frase de §7 | «`triage_lesson_relevance.py` ... todavia no implementado», «No existen `decision_client.py` ni `triage...`», «Ausente al ajustar», «NUEVO, no implementado», «No existe al ajustar», «no se toca la costura inexistente» | cuatro sellos. Medido con `ls`/`find` sobre el arbol de trabajo: `scripts/decision_client.py` **69.503 B**, `scripts/triage_lesson_relevance.py` **42.378 B** (lo entrego FASE-C del hermano, cerrada en su parte offline el 2026-09-24), `tests/quality_gates/jev_pilot/` existe con `test_jev_pilot_offline.py`, y `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/` tiene sus tres JSON mas `FASE-A/`; **no** existen `FASE-B/`, `FASE-C/` ni `FASE-RELEASE/`. Cada sello dice que «existe» no es «hito verificado» y que la restriccion («no crearlo anticipadamente», «no se toca la costura») sigue vigente y se respet en esta tanda |
| 5 | JEV `dependencias-fases.md` | §Hitos y evidencia de entrada, dos filas, y la linea que la orden sealaba como «no se toca la costura inexistente» | «PENDIENTE; archivo ausente» dos veces | **el archivo esta protegido y no se toco** (prohibicion expresa de la orden y decision del operador del 2026-09-21). El sello va en `10-analisis-post-implementacion.md` de JEV con la medicion y con **la deriva de la ancla declarada**: la frase «no se toca la costura inexistente» no esta en ese `dependencias-fases.md` (buscada, 0 coincidencias) sino en el `01-plan-maestro.md` del mismo plan, y ahi se sello |
| 6 | JEV `README.md` y `04-contrato-ejecucion.md` | las dos notas datadas del 2026-09-28 | ambas remiten su rectificacion a la seccion «Cierre formal de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22` (2026-09-27)» **dentro del `dependencias-fases.md` de JEV**, que no tiene esa seccion | sello que **corrige el DESTINO sin borrar la frase**: medido con `grep -c "Cierre formal"`, el archivo citado da **0** y el del hermano VCF da **1** con su cabecera. Crudo: `08-cita-rota-destino-medido.txt` |

## Lo que los sellos no hacen

- No marcan casillas, no cambian estados de AC, no re-escriben ninguna frase anterior. Un sello anade y
  referencia; el registro lo sigue escribiendo su dueno.
- No re-miden veredictos: la evaluacion del 2026-09-30 viaja como ancla y esta tanda la ejecuto, no la re-abrio.
- No introdujeron cifras estaticas ahi donde la corrida es la fuente: el unico numero nuevo que se publica en
  corpus es el conteo de rutas versionadas (0 y 18), que es un hecho de identidad verifiable con el comando que
  el propio sello nombra.

## Efecto secundario de la firma 2, declarado y corregido

El sello del archivado escribio literalmente la raiz `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`
para decir que devuelve 0 rutas. Esa ruta **no existe**, y `validate_opencode_refs.py` la corto como referencia
rota: el quick paso a **12/13** y el pack `FASE-RELEASE.md` - que proyecta el checklist - heredo la misma
referencia. Es la familia de «la metrica de un derivado no va en su propio corpus» y «la prosa viaja a los
packs», con un giro nuevo: aqui lo que viaj6 fue una **ruta** metida dentro de un sello. Se corrigio redactando
la medicion sin invocar la ruta inexistente (`.opencode/plans/` sin el segmento `Archives/`), y se re-correra la
cola. Ningn gate lo cortaba antes: `--quick` si lo corto, y es la razon por la que la cola canonica se corre
entera y no de memoria.
