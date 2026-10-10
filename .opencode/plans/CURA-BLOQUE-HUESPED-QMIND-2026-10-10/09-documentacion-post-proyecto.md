# Documentación post-proyecto — CURA-BLOQUE-HUESPED-QMIND-2026-10-10

Plan de una fase (FASE-1), ejecutado el 2026-10-10 sobre HEAD `01013ef`. Los números de esta sección D son la
fuente única; el análisis y el maestro los referencian.

## Sección A: Módulos nuevos

Ninguno. El plan no crea módulos ni paquetes: cura un símbolo existente y lo dientes.

Archivos nuevos que no son código: el directorio del plan (`.opencode/plans/CURA-BLOQUE-HUESPED-QMIND-2026-10-10/`
con `00-lecciones-capitalizadas.md`, `01-plan-maestro.md`, `05-prompt-inicio-sesion-fase-1.md`, `README.md`,
`09-documentacion-post-proyecto.md`, `10-analisis-post-implementacion.md`) y su evidencia
(`evidence/CURA-BLOQUE-HUESPED-QMIND-2026-10-10/FASE-1/`).

## Sección B: Funcionalidades nuevas

| AC | Qué cambia en el comportamiento observable | Diente que lo fija |
|---|---|---|
| **AC-N1** | El hallazgo de contabilidad (`[DUPLICADO-VIGENTE]` por fuente huésped) se evalúa en las **doce** rutas del bucle de `verificar_contenido()`. Una descarga que falla ya no suprime el rojo de su entrada ni cambia el EXIT de la corrida por esa vía: antes pasaba de 1 a 2 | `test_una_bajada_que_falla_no_suprime_a_su_huesped_de_contabilidad` (nuevo) y `test_un_vencido_por_cuerpo_en_la_mesma_entrada_tambien_evalua_a_su_huesped` (re-anclado) |
| **AC-N2** | El `[CONTADOR]` publica su denominador de observación: `N/M entrada(s) con su bloque huesped recorrido`, contado en el sitio donde el bloque corre. Un `0 fuente(s) huesped(s)` ya no puede salir de una corrida que no miró | `test_el_contador_publica_su_denominador_de_observacion` (nuevo) |

## Sección D: Métricas acumulativas — aquí vive el número

| Métrica | Valor | Instrumento |
|---|---|---|
| Tests PRE (selección literal de las dos familias) | **65 passed**, EXIT=0, Python 3.13.3 | `evidence/CURA-BLOQUE-HUESPED-QMIND-2026-10-10/FASE-1/01-pre_seleccion_dos_familias.txt` |
| Tests POST, primer intento | 1 failed / 66 passed, EXIT=1 — el rojo era del **montaje del diente nuevo**, no de la cura | `…/FASE-1/02-post_seleccion_dos_familias.txt` |
| Tests POST final | **67 passed**, EXIT=0, Python 3.13.3 | `…/FASE-1/03-post_seleccion_final.txt` |
| Resta R2.7 (POST − PRE) | **2** = dientes nuevos (2). Coincide exactamente: ningún diente existente se perdió y el re-anclado sigue siendo uno | los dos crudos anteriores |
| Mutation checks R2.8 | **2 mutantes, 2 rojos, 2 restauraciones verificadas por sha256** (M1 exit=1, M2 exit=1, verde exit=0; sha final idéntico al original) | `…/FASE-1/04-mutantes_m1_m2.txt` |
| Rutas del bucle que evalúan a la huésped | **12 de 12** (antes 4 de 12); `continue` dentro de `verificar_contenido()`: **0** (antes 9) | `grep -cE "^\s+continue\s*$"` sobre el símbolo y lectura del ámbito nuevo `_dictaminar()` |
| Quick | 13/13, EXIT=0 (PRE y POST, y otra vez tras escribir el registro) | `…/FASE-1/06-quick_post.txt`, `…/FASE-1/07-quick_post_registro.txt` |
| Modo completo | **16/18**, EXIT=1: los dos rojos son `Tests` (deprecación de Pydantic, preexistente) y `QMind Write-back` (el `DUPLICADO-VIGENTE` deseado de la era G). Ningún check documental salió vencido pese a que la corrida empezó antes de existir los documentos del plan | `…/FASE-1/05-modo_completo_post.txt` |
| Confirmación en vivo del verificador curado | 1 `source list` + sus bajadas, **0 escrituras remotas**; una descarga fallida y aun así `5 fuente(s) huesped(s)` con denominador `4/4 entrada(s) con su bloque huesped recorrido` | `…/FASE-1/08-verificador_curado_en_vivo.txt` |
| **Inventario final de la fase, dos commits** | **21** archivos únicos: 20 en `c6a47c2` más el crudo del sello en `700945e` (el maestro, el análisis y el par del índice fueron re-editados por el sello) | `git show --name-only` sobre los dos commits |
| **Fila del registro vs árbol, delta declarado** | La fila `## FASE-1 - 2026-10-10` declara **17** rutas y el árbol tiene **21**: faltan `docs/contributing/.last_doc_phase.json` y los crudos `07-quick_post_registro.txt`, `08-verificador_curado_en_vivo.txt` y `09-sello_del_commit_c6a47c2.txt`. La fila **no se re-estampa**: `log_phase_completion.py` es aditivo y se niega si la cabecera ya existe, y editar el registro fuera de su escritor está prohibido. Este delta queda aquí como la fuente del dato final | comparación de las rutas de la tabla de la entrada contra `git ls-files` de los directorios de la fase, re-ejecutable |
| Quick del sello | 13/13, EXIT=0, con el árbol del sello y el delta ya declarado | `…/FASE-1/10-quick_del_sello.txt` |

## Sección E: Archivos afiliados actualizados

- `scripts/validate_qmind_writeback.py` — `verificar_contenido()` (ámbito nuevo `_dictaminar()`, bloque huésped
  universal, denominador en el `[CONTADOR]`) y la docstring de `_huespedes_sin_contabilidad()`, que describía el
  estado anterior.
- `tests/test_validate_qmind_writeback_escritura.py` — dos dientes nuevos y un re-anclaje gobernado.
- `.opencode/LECCIONES-INDEX.md` y `.opencode/lecciones_index.json` — regenerados por
  `scripts/build_lesson_index.py` en el mismo árbol que los `.md` del plan (invariante R2.10).
- `docs/contributing/REGISTRY.md` — escrito por `scripts/log_phase_completion.py --fase FASE-1`, que es su único
  escritor.
- **No actualizados, con motivo:** `VERSION.yaml` y `CHANGELOG.md` (sin bump: deuda `S-BH-3`, decisión del
  operador), `AGENTS.md` y `.cursorrules` (no cambian capacidades ni comandos), y ningún documento de planes
  archivados ni la instantánea publicada del plan hermano (frozen por diseño; la equivalencia del diente
  renombrado se declara en el análisis).
