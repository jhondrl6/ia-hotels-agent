# Análisis Post-Implementación — VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

> Se crea **desde la concepción** del plan, no al final. Cada fase actualiza su fila, sus lecciones,
> sus métricas y sus seguimientos al cerrar. FASE-RELEASE consolida la matriz.

## Resumen de Ejecución

| Fase | Estado | Iteraciones medidas (unidad e instrumento) | Cortes autorizados | Notas |
|---|---|---|---|---|
| FASE-A | PENDIENTE | — | — | — |
| FASE-B | PENDIENTE | — | — | — |
| FASE-C | PENDIENTE | — | — | — |
| FASE-D | PENDIENTE | — | — | — |
| FASE-RELEASE | PENDIENTE | — | — | — |

**FASE-VERIFY no aplica** (criterio 2 de §4.6 cae: no existe fase con ejecución E2E, y además este
plan no hace llamadas de red). Por tanto ningún AC de este plan puede alcanzar `SUPERADO EN E2E`.

## Matriz de Verificación de Hallazgos

| Hallazgo | Medición que lo sostiene | Qué lo previene ahora | ¿Verificable en el artefacto? |
|---|---|---|---|
| A1 — el workflow afirma que `validate_plan_citations.py` es el check 8 del quick | El método `def _check_plan_citations` imprime `[9/11]` | `validate_governance_numbers.py` (FASE-A) | Sí — `findings[]` |
| A2 — el workflow afirma `[9/9]` para la capitalización | `def _check_lesson_capitalization` imprime `[10/11]` | ídem | Sí |
| A3 — el workflow afirma `[12/12]` en el modo completo | **Rectificada el 2026-09-20**: la etiqueta real del write-back es `[15/15]` (la imprime `def _check_qmind_writeback`). La primera versión de esta fila decía `[12/15]`, que es la etiqueta de `def _check_dependencies` — el total (15) sí era correcto y el emisor no | ídem | Sí — y es el ejemplo vivo de por qué AC1 exige emparejar etiqueta ↔ método |
| A4 — el template de lecciones afirma `[10/10]` | La etiqueta real es `[10/11]`; su `[7/7]` del hook **sí** coincide | ídem | Sí |
| A5 — un grep de término devuelve 0 sobre un corpus que sí contiene lo buscado con otras palabras | `grep -icE "verificador mec"` devolvió 0 al concebir el plan | `triage_lesson_relevance.py` publica términos y ceros (AC15) | Sí — `coverage.json` |
| A6 — **las cifras del propio plan vencieron al crearse el plan**: decía 14 análisis / 49 IDs sin definición / 389 `.md` y el índice regenerado pasó a 15 / 50 / 401 | `build_lesson_index.py` contra `head -18 .opencode/LECCIONES-INDEX.md`, medido el 2026-09-20 al verificar este plan | Toda cifra copiada de una fuente dinámica se publica **con su comando y su fecha** y se re-mide al cerrar la fase; no se le cree a la salida de otro verificador | Sí — `00-…` Q4 y maestro §1 |
| A7 — una sesión de fase declara **263.973 bytes ≈ 65.993 tokens** de lectura antes de tocar código, en ocho lecturas, contra un presupuesto de 60 `tool_use` | `stat -c %s` sobre los **siete** documentos que suma la tabla (el octavo que declara leer la fase es un archivo de `evidence/` excluido de la suma), re-medido el 2026-09-20; al concebir dio 254.010 y creció +9.963 con los cierres del propio plan medido; tokens estimados por divisor 4 | `build_phase_briefing.py` (FASE-D) unifica las lecturas declaradas en un pack derivado; **AC20 mide el delta y lo publica aunque sea cero** | Sí — `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/carga.json` |
| A8 — la población bajo el patrón de conteo es mayor que las cuatro aserciones: **22 instancias `[N/M]` en 17 líneas** más 2 formas «check N» en los documentos de gobierno | `grep -rnoE '\[[0-9]+/[0-9]+\]' .agents/` y `grep -rnoE 'check [0-9]+' .agents/`, medido el 2026-09-20; el propio workflow declara en su entrada `v2.24.0` que cuatro de esas menciones son históricas y «se conservan literales» | AC1 con regla de población (viva / histórica congelada publicada / vigente-correcta) y `findings[]` por aserción con `occurrences[]` | Sí — `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/informe.json` → `findings[]`, `historical_excluded[]` |

**Lo que A7 no afirma.** No dice que la lentitud sea solo de tokens: la cadena del otro plan es de
doce fases secuenciales de una sesión y cada fase re-mide once validaciones. Nada de eso lo toca este
plan, y decirlo aquí es parte del cierre honesto.

## Lecciones Aprendidas

Mínimo 3 por fase completada (regla del executor). Formato: **qué pasó / por qué / qué lo previene** +
pertinencia **INCLUIR** o **EXCLUIR** para el siguiente plan.

### Lecciones capitalizadas de planes anteriores (espejo de `00-lecciones-capitalizadas.md` §2)

**Catorce filas** capitalizadas: once al concebir (L-R.1, L-R.3, L-R.4, L-NC10, L-PF6, L-PF10, L-D3,
L-V2.3, L-T4A.5, L-VUP-5, L-HF1) más tres que aportó la **capa tibia consultada en la auditoría del
2026-09-20** (L-V2.1, L-V2.2, D-V2.1), sobre **6 dueños distintos** con su efecto concreto nombrado en
la columna «Qué cambia» del propio §2 — no aquí. *(Doble corrección del 2026-09-20: la fila publicaba
**7** dueños cuando las once originales ya tenían **6**, y las tres nuevas no suman ninguno porque
`D-V2.1` está definida en `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` — `TRIBUNAL-ENFORCEMENT-OBS`
es donde la **reproducen**, en cuatro fases seguidas. Lo detectó
`validate_lesson_capitalization.py` por `C7`, es decir: el verificador de forma del corpus cazó la
atribución vencida del documento de este propio plan, y el conteo se corrigió re-midiéndolo.)*

### Lecciones nuevas de este plan (L-VCF-1+)

- *(pendiente — se llenan al cerrar cada fase)*

## Seguimientos abiertos

| # | Tema | Dueño | Disparador |
|---|---|---|---|
| S1 | D1: corregir o retirar las aserciones A1–A4 en `.agents/` | FASE-RELEASE de este plan | Decisión escrita del operador; configuración central |
| S2 | D2/D3: promover el verificador al `--quick` y rebanar el workflow | Plan propio posterior | Sesión previa a `FASE-RELEASE` de `REFACTOR-WHATSAPP-ENTREGA-2026-09-18` |
| S3 | **D6: lint de contradicciones semánticas** (`validate_plan_semantics.py`) | Plan propio posterior; entra en **este** directorio si el disparador se cumple vigente este plan | El `acceptance` que publique AC15 en FASE-C. Si el triaje sale inaceptable, **no se activa** |
| S4 | **D7: activar el proveedor de decisiones ya habilitado** y correr la comparación | Plan propio posterior | Decisión del operador del 2026-09-20 de no entrar ahora; AC9 ya dejó la costura probada |
| S5 | D8: la consulta Q7 de QMind **sí se ejecutó** en la auditoría del 2026-09-20 (cuatro `retrieve`; el comando válido usa el ID del notebook, no su nombre) | FASE-RELEASE | Re-correr solo si el corpus del notebook cambió desde la auditoría, y verificar que las citas de L-V2.1/L-V2.2/D-V2.1 siguen en pie |
| S7 | **D10: re-leer la interfaz del write-back antes del cierre** — `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` declara dentro de su alcance `validate_qmind_writeback.py` y su conexión en `run_all_validations.py`, y piensa añadir `--title`/`--file` | FASE-RELEASE de este plan | Al llegar el cierre: `--help` contra el árbol vigente y re-escribir el orden de `04-contrato-ejecucion.md` si la firma cambió |
| S6 | D4/D5: verificadores de la resta pre/post (R2.7) y del par verde/rojo (R2.8) | `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` §Deuda | Ya asignados antes que este plan; no se reasignan |

## Métricas de Ejecución

- [ ] Tests de la fase, en la **misma base de medición** que su par pre/post (R2.3).
- [ ] Coherencia del índice de lecciones al commitear.
- [ ] **Carga de lectura por fase, antes y después del pack (AC20)** — con su comando y su divisor.
- [ ] Aceptabilidad del triaje (AC15): propuestos pertinentes / total propuestos.

## Decisiones Arquitectónicas

- [ ] El pack se genera dentro del plan y **no** sustituye ninguna lectura canónica (alternativa
  descartada: rebanar `.agents/`, que es D3 y exige tocar configuración central en vuelo).
- [ ] FASE-B deja un solo proveedor configurable y **no** compara (alternativa descartada: mantener el
  AC9 de comparación, que con un solo proveedor se cerraba declarando `NO-EJERCITADO` y certificaba
  humo).
- [ ] El triaje es aditivo y no filtro, con el coste de esa elección medido en FASE-C.
- [ ] Forma de descubrir aserciones en los documentos: patrón sobre la fuente, no lista fija.

## Checklist de Cierre (llenar en FASE-RELEASE)

- [ ] Los cuatro scripts en `scripts/`, con sus tests y su evidencia de mutation check.
- [ ] Ningún AC promocionado sin respaldo legible en el artefacto (R2.4).
- [ ] `--quick` en 11 checks y hook en 7, composición intacta (AC16).
- [ ] S1–S7 con dueño y disparador vigentes; **D6 resuelta con el número de FASE-C, no con opinión**.
- [ ] Write-back → índice → `git mv` → índice, en ese orden (R2.5, R2.10).
