# FASE-B — baseline pre/post (R2.3 / R2.7)

**Plan**: `CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22` · **Fase**: FASE-B
**Método**: todo conteo es delta con par; el verificador mecánico de la resta **no existe** y se declara así (`L-R.4`).

## 1. Sobre-presentación del revisor (antes → después)

| Paso | Medición | Fuente |
|------|----------|--------|
| **Antes** (baseline real) | propuesta renderizada 2026-10-12: **10 literales crudos → 8 descartados por filtro estructural (6 filas de tabla + 2 líneas con monto) → 2 emitidos** | `evidence/…/FASE-B/inventario-candidatas.txt` (dos pasadas: regex crudo del módulo vs `coincidencias_lenguaje_de_verificacion`) |
| **Antes** (medición congelada) | `10 → 6 → 2` | `CONTEXT-CONTRATO-PLANTILLA-TIER-2026-10-12.md` (medición 2026-10-14, solo lectura) |
| **Después** | render B+ con el contrato activo: **0 emitidos** (`summary.over_presentations == 0` con el revisor real) | `par-rojo-verde-claims.txt` [VERDE]; `tests/commercial_documents/test_fase_b_claims_tier_render.py` |

**Resta publicada**: **2 emitidos → 0 emitidos** (los 2 claims «Protección total para usted» y
«Transparencia total» neutralizados con variante por tier).

**Divergencia declarada (8 vs 6 descartados)**: la medición en vivo con la función real del
revisor descarta **8** de los 10 literales crudos (contraste *8 vs 10* del prompt); la medición
congelada del contexto citaba **6**. La diferencia son las 2 líneas con monto («fuga total
estimada… $21.067.200 COP» y «Total recuperación proyectada… $4.731.342 COP»), hoy filtradas por
`MONTO_DECLARADO`. El resultado operativo es idéntico en ambas mediciones: **2 emitidos**, los
mismos. El contexto es congelado y no se edita; la divergencia queda aquí.

**Taxonomía reconciliada de Tarea 1** («la tabla separa **2 emitidos** de **6 descartados**; los 5
labels financieros quedan marcados como *no tocar*»): son **tres poblaciones distintas** que
comparten la palabra «descartados»; la tabla las separa por población:

| Categoría | Población | Cifra | Fuente |
|-----------|-----------|-------|--------|
| Emitidos (los 2 claims) | literales que el revisor **emitía** en la propuesta renderizada | **2** | §1 (resta 2 → 0); `par-rojo-verde-claims.txt` |
| Descartados por filtro estructural — medición CONGELADA (la «**6**» de Tarea 1) | los 10 literales crudos del baseline 2026-10-12 | **6** | `CONTEXT-CONTRATO-PLANTILLA-TIER-2026-10-12.md` (congelado, solo lectura) |
| Descartados por filtro estructural — medición EN VIVO con la función real | los mismos 10 literales crudos | **8** | `inventario-candidatas.txt` (divergencia 8-vs-6 declarada arriba) |
| Labels «no tocar» (los «5 descartados» del Contexto del prompt) | las 7 líneas del grep de la plantilla = 2 claims + 5 | **5** | `inventario-candidatas.txt` (tabla NO_TOCAR); `test_labels_financieros_intactos` |

## 1b. Suite completa — punto medido, atribución de rojos y verde final (cierre FASE-B)

| Punto | Resultado real | Fuente |
|-------|----------------|--------|
| Suite completa (corrida de la auditoría forense previa que hereda esta sesión; **antes** de la reparación B1) | **4 failed / 5462 passed / 37 skipped / 4 xfailed** | medición heredada de la auditoría previa (2026-10-23); los 4 rojos = H5 + los 3 rojos R |
| H5 (4.º rojo) | `test_validate_wiring_check_derivado_versionado` fallaba por el derivado `.opencode/wiring_report.json` vencido (los 2 `.py` de `evidence/` y el test nuevo movieron 3 contadores); **curado en fase** por `validate_wiring.py --write-report` (B1). **No** es preexistente | `quick-post-reparacion-wiring.txt` (`--check` limpio; `--quick` 13/13) |
| Atribución de los 3 rojos R (por mecanismo, S1) | `test_all_config_files_have_description` → **PREEXISTENTE** (`config/secret_fragment_policy.yaml` sin `description`) · `test_la_falta_de_deepseek_falla_antes_de_enviar_aunque_haya_clave_anthropic` → **AMBIENTAL** (clave `DEEPSEEK_API_KEY` sembrada desde `.env` al importar `main` en colección combinada; pasa solo) · `test_el_preflight_recalculado_no_inventa_el_consentimiento` → **PREEXISTENTE** (vencido por calendario: 93 días contra techo 90) | `atribucion-rojos-r.txt` (trazas, greps y `sys.modules`) |
| Verde final de cierre | `run_all_validations.py --quick` = **13/13**, `EXIT=0` leído sin tubería | `quick-post-reparacion-wiring.txt` |

**Par pass/fail de la suite completa: NO EXISTE** — se declara (`L-R.4` / R2.7). Solo existe el
punto medido de la tabla (una corrida previa), no un par pre/post de pass/fail de la suite completa.
Los pares que sí existen y se conservan: el conteo recolectado pre/post (§3) y el par rojo/verde del
revisor (§2). La resta ya publicada en §1 (2 emitidos → 0 emitidos) no se toca.

**Descuadre de 1 declarado (C2)**: los desenlaces de la corrida heredada suman 5507
(4+5462+37+4) frente a los **5506** recolectados de §3; sin verificador mecánico que lo resuelva
(`L-R.4`), queda declarado. El par recolectado se re-midió en vivo en este cierre: **5498** sin el
archivo nuevo y **5506** con él (delta **+8**, confirmado).

**Medición propia de la suite completa (2026-10-23, post-cierre documental)**:
`pytest tests/ -q` → **26 failed / 5413 passed / 37 skipped / 4 xfailed / 27 errors** (489.60 s,
crudo `suite-completa-post-cierre.txt`) — **no** reproduce el punto heredado (4 failed / 5462
passed / 37 skipped / 4 xfailed). Atribución por mecanismo de la diferencia: de los 26 failed, **23**
son de `tests/quality_gates/lesson_relevance/*` y **los 27 errors son todos de ese paquete**; los
otros 3 failed son los rojos R ya atribuidos (§1b) y H5 ya no falla (curado por B1). El guard
`comprobar_frescura` de `scripts/triage_lesson_relevance.py` compara `lecciones_index.json` del
disco contra su re-cálculo sobre `plans_dir`+`context_dir` y lanza `SueloNoLeible: VENCIDO` cuando
difieren: el par derivado quedó **vencido por los propios documentos de cierre de FASE-B** (el par
estaba fresco al cierre de FASE-A — regenerado 2026-10-23 07:45, precedente de que el cierre de
fase lo re-publica — y la corrida de la auditoría posterior solo tuvo los 4 rojos conocidos). Ninguno
de los **50 nodos caídos** (23 failed + 27 errors, re-medido dos veces) referencia los archivos de
FASE-B (token-scan vacío): la dependencia es por el corpus de planes, no por los módulos del
producto. *Corrección de agregado: esta nota decía «37 nodos problemáticos» y `10-analisis` decía
«34»; ninguno de los dos lo imprime una corrida. La medida es 23 failed + 27 errors. Los dos 37 del
vecindario —los `37 skipped` de la suite y los `37.61 s` de la corrida aislada— son la hipótesis más
barata del desliz, pero queda como hipótesis: el hecho es que la suma correcta es 50.*

**Disposición: PARADO primero y CURADO después, con autorización expresa del Operador** (2026-10-23).
El fix es un solo comando de re-publicación del derivado (`python scripts/build_lesson_index.py`),
mismo patrón que `validate_wiring.py --write-report`. Verificación, en el orden en que se corrió:

| Corte | Antes | Después |
|-------|-------|---------|
| `build_lesson_index.py --check` | `EXIT=1` — `[FAIL] Índice de lecciones vencido: LECCIONES-INDEX.md, lecciones_index.json` | `EXIT=0` — `[OK] Índice de lecciones fresco (398 IDs)` |
| `tests/quality_gates/lesson_relevance` (aislada) | 23 failed / 18 passed / 27 errors | **68 passed**, `EXIT=0` |
| Pre-vuelo en directorio temporal vs lo escrito | — | sha256 idénticos: `LECCIONES-INDEX.md` `d6e01b38…`, `lecciones_index.json` `fa1d6113…` |
| Definiciones / citas sin definición / redefiniciones | 398 / 113 / 33 | 398 / 113 / 33 — **0 nuevos en los tres cortes** |

El orden del cierre queda fijado por medición, no por preferencia: el índice solo barre
`plans_dir.rglob("*.md")` y `context_dir.rglob("*.md")` (los dos `rglob` de
`scripts/build_lesson_index.py`), así que **`docs/contributing/REGISTRY.md` no es fuente del índice**
y re-editarlo no lo re-vence.

**Falsado propio, medido en este mismo cierre**: la versión inicial de esta nota afirmaba que
*cualquier* edit en `plans/*.md` re-vence el índice. **No.** Después de editar `10-analisis`,
`dependencias-fases.md` y los 8 prompts de fase, `--check` siguió en `EXIT=0` y el sha256 del par
quedó idéntico al de la re-publicación anterior (`d6e01b38…` y `fa1d6113…`). El disparador real es lo
que el extractor **registra** por lección — `enunciado`, `seccion`, `fecha_plan`, `total_citas` y
`planes_que_lo_citan` —: el índice se vence cuando el edit **cita IDs del vocabulario** (las cuatro
familias que admite `ID_RE`) o añade definiciones, y la prosa que no cita ninguna no lo toca. Los
documentos de cierre de FASE-B sí lo vencieron porque §5.1 de `00-lecciones` cita lecciones ya
definidas; la fila de seguimientos escrita después, no.

Consecuencia para las fases restantes: re-publicar el índice **después** de los documentos de plan y
verificar con `--check`, pero sin asumir que cada párrafo nuevo exige la re-publicación. Ninguno de
estos pasos crea archivos nuevos —el par regenerado ya estaba versionado—, así que los contadores de
Wiring no se mueven (`validate_wiring.py --check` en `EXIT=0`, 727 archivos en alcance).

## 2. Mutation check (R2.8) — par rojo/verde

| Escenario | Resultado real | Archivo |
|-----------|----------------|---------|
| Verde: render B+ con la condición del render activa | `summary.over_presentations = 0` | `par-rojo-verde-claims.txt` |
| Rojo: condición desactivada (A-bloque siempre visible) | `summary.over_presentations = 2` — el revisor real vuelve a emitir los 2 claims | `par-rojo-verde-claims.txt` |
| Verde: strings del diagnóstico B+ (variante honesta) | 0 hallazgos de la función real | `par-rojo-verde-claims.txt` |
| Rojo: strings del diagnóstico forzados a variante A en B+ | 2 hallazgos (los 2 claims) | `par-rojo-verde-claims.txt` |

Re-ejecutable: `./venv/Scripts/python.exe evidence/…/FASE-B/mutation_pair_runner.py`.
El mismo par está codificado como tests (afirman el rojo del mutante):
`test_mutante_condicion_desactivada_reemite_los_2_claims` y
`test_mutante_strings_diagnostico_forzados_a_reemite_claims`.

## 3. Conteo de tests (delta, par pre/post)

| Par | Valor |
|-----|-------|
| `*_baseline_pre.txt` (sin el archivo nuevo de FASE-B) | **5498** tests recolectados |
| `*_baseline_post.txt` (con `test_fase_b_claims_tier_render.py`) | **5506** tests recolectados |
| **Delta FASE-B** | **+8** |

Comandos: `./venv/Scripts/python.exe -m pytest tests/ --collect-only -q` (con y sin
`--ignore=tests/commercial_documents/test_fase_b_claims_tier_render.py`).

## 4. Qué NO cambió (superficie «no tocar»)

- Las 5 líneas no-claim del grep de 7 (labels financieros y «Resultados garantizados») siguen
  renderizadas sin cambios (`test_labels_financieros_intactos`).
- `honesty_reviewer.py`, `judge.py`, `acta_writer.py`, `P6.5`, `T1_CERTIFIABLE_CLAUSES` y
  umbrales: intactos (fuera de alcance de FASE-B).
- Ningún commit (ningún prompt autoriza commit).

## 5. Pase de cierre autorizado por el Operador (2026-10-23, después del informe de re-auditoría)

Qué se ejecutó, en el orden que la medición impuso: `build_lesson_index.py` (re-publicación del par
derivado) → corrección a mano de la sección FASE-B en `docs/contributing/REGISTRY.md` → parche del
bloque `Registro` en los 8 prompts de fase pendientes → re-verificación de gates. No se creó ningún
archivo en este pase: todo lo nuevo se escribió dentro de `baseline-pre-post.md`, ya declarado.

| Gate (medido, exit leído sin tubería) | Resultado |
|---|---|
| `build_lesson_index.py --check` | `EXIT=0` — `[OK] Índice de lecciones fresco (398 IDs)` |
| `validate_wiring.py --check` | `EXIT=0` — 174 llamadas en 727 archivos, violaciones 0 |
| `run_all_validations.py --quick` | `EXIT=0` — **13/13** |
| `tests/commercial_documents/test_fase_b_claims_tier_render.py` + `lesson_relevance` + `commercial_documents` + `quality_gates/tribunal` | `EXIT=0` — **807 passed, 9 skipped** |
| `pytest tests/ -q` (suite completa, 520.91 s, exit leído sin tubería) | **3 failed, 5463 passed, 37 skipped, 4 xfailed**, `EXIT=1` — los únicos rojos son los tres **R** ya atribuidos al Operador. Contra el punto con el derivado vencido (26 failed + 27 errors) y contra el punto heredado de la auditoría (4 failed): desaparecen los 23 failed y los 27 errors de `lesson_relevance` y desaparece el rojo de Wiring. **Ningún rojo es de FASE-B.** Salva: esta corrida arrancó antes de los últimos tres edits documentales (`10-analisis`, este archivo, `09`), que no toman código; los paquetes sensibles al corpus se re-verificaron después de todos los edits con la fila anterior |
| Cotejo del registro contra Git (`git cat-file -e HEAD:<ruta>` por fila declarada) | **11 nuevos / 7 modificados, COHERENTE**: ninguna ruta declarada como nueva existe en HEAD y ninguna declarada como modificada falta |
| EOL de los archivos editados (paridad CR contra líneas) | **PARIDAD** en `10-analisis`, `dependencias-fases`, este archivo, `REGISTRY.md` (12870/12870) y los prompts |

Dos cosas que este pase corrigió del propio cierre, no de la implementación:

1. **El agregado de nodos caídos por el derivado era 50**, no 34 ni 37 (§1b arriba).
2. **La regla de cuándo se vence el índice estaba mal escrita** y se falsó en el mismo pase: editar
   `10-analisis`, `dependencias-fases.md` y los 8 prompts dejó `--check` en `EXIT=0` con el sha256 del
   par intacto (§1b, «falsado propio»). El disparador es la cita de IDs del vocabulario o una
   definición nueva, no cualquier párrafo.

Queda pendiente del Operador: el **commit con pathspec explícito**. Superficie medida en el árbol:
**35 rutas (11 `A` + 24 `M`)**. El registro declara **18** de esas 35 (11 nuevos / 7 modificados)
porque la convención del plan no lista los documentos de plan ni `docs/contributing/.last_doc_phase.json`
—precedente: la entrada de FASE-A declaró 6 rutas y tampoco listó las suyas—, así que las 17
diferencias son `.md` de plan y el archivo de estado del escritor, no un olvido del registro. Sin
tocar la cabecera de `REGISTRY.md` ni `AGENTS.md`. Quedan también las letras **H7** (deuda de
instrumento, dueño FASE-H2) y los tres rojos **R** (dueño Operador). FASE-C no se abre: la fase
cierra en espera de autorización.
