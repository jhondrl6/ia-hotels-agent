# FASE-E — Entrega real revalidada y revisión con snapshot interno (2026-10-06)

**Estado:** COMPLETADA y **commiteada + empujada por orden literal del operador al cierre de la sesión** (el mandato de implementación no autorizaba el commit: los cinco cortes se sostuvieron sin él y ese fue el corte que midió R2). El sha y el rango empujado se estampan en el sello documental de FASE-RELEASE. La orden cubrió commit + L3 + push; la revisión L3 del cierre no arrojó hallazgos. **Contador v4complete: 0/1** — ninguna prueba
ejecutó `main.py v4complete`; el cable de producción se gobierna por AST sobre `main.py`.

**ACs gobernadas:** AC9, AC10, AC11, AC12 (todas **VERIFICADO OFFLINE**, con mutantes del símbolo real).
**Prerrequisito verificado antes de editar:** A, G, 0, B, C y D cerradas y con evidencia en disco; D está
commiteada y empujada (`38073a7`) y el árbol arrancó limpio.

## 1. Estado real de F-P4.1, revalidado con mutación (no con la cita del contexto)

| Medición | Resultado |
|---|---|
| Derivación `asset_zip_paths` desde los `dest` que el propio writer escribe | **VIGENTE** (P6/P6-R no se reimplementó) |
| M5: `zip_path = asset_zip_paths.get(asset, asset)` → `zip_path = asset` en la sección de assets fuera de catálogo | **EXIT=1 por la aserción nombrada** en `test_el_asset_nuevo_de_b_viaja_con_su_ruta_real_y_su_orden` |
| ¿"siempre entrega un stub de 468 bytes"? | **FALSO**, y la formulación correcta es otra: con assets planificados el orden trae `### N.` y rutas `ASSETS/...` reales; **sin assets planificados el paquete NO lleva `IMPLEMENTATION_ORDER.md`** (medido con el writer real, `test_estado_real_de_f_p4_1_sin_assets_planificados_no_hay_orden`) |
| Consecuencia para AC10 | No se certifica ni por tamaño ni por presencia de un string: la evidencia es el miembro del ZIP y su coherencia con el manifiesto |

## 2. Símbolos revalidados en disco antes de editar

`DeliveryPackager.write/publish/suppress`, `_collect_files`, `_build_manifest_in_memory`,
`_resolve_manifest_self_size`, `AssetResponsibilityContract.generate_delivery_template`,
`run_v4_complete_mode`, `artifact_paths.resolve_latest` y los cuatro revisores están donde los describía
el inventario. Dos correcciones al inventario del plan, medidas:

- El borrado de `run_v4_complete_mode` resolvía las rutas por `locals()["diagnostic_path"]` /
  `locals()["proposal_path"]` (:3061-3074). No es código muerto: funciona, pero hace invisible el
  vínculo con el punto de captura. **E lo reemplazó por la referencia directa** y anotó por AST que la
  captura precede al borrado.
- `resolve_latest` recorre 4 niveles (incluido `output/`, compartido entre hoteles) y elige por **mtime**,
  así que "el más reciente" puede ser de otro hotel. Solo `AssetReviewer._resolve_delivery_zip` abría el
  ZIP; `HonestyReviewer._resolve_manifest_path` y `TribunalJudge._resolve_manifest` buscaban
  `deliveries/*/MANIFEST.json`, inexistente en régimen ZIP-only (L-E2E.1).

## 3. Producto

| Archivo | Qué hace ahora |
|---|---|
| `modules/quality_gates/tribunal/review_inputs.py` (**nuevo**) | Copia interna no exportable + manifiesto `review_input_manifest.json` (schema 1.0: `run_id`, `original_path`, `internal_path`, `sha256`, `size_bytes`, `captured_at`, `read_status`, `disposition`, `cause`) y el **resolvedor único** `ReviewInputs` que consultan el Juez y los cuatro Bots. `run_root_for` ancla la ruta al run; sin manifiesto queda el glob histórico pero **declarado** como `legacy-ancestor-walk` |
| `modules/data_validation/whatsapp_contract.py` | `READ_NOT_READ = "NO_LEIDO"`, quinta clave del vocabulario designado en FASE-C (no se creó un enum propio) |
| `modules/quality_gates/tribunal/artifact_paths.py` | `resolve_latest(..., explicit=)`: si la ruta del run está declarada y no existe, retorna **None** en vez de caer al ascendiente compartido |
| `diagnosis_reviewer.py` (Bot 1) | El diagnóstico llega por el resolvedor. El verde silencioso de F-P4.2 se cerró: `_check_diagnostic_input` emite `REVIEW_INPUT_UNREAD` (WARNING) si el insumo es `NO_LEIDO`/`READ_ERROR`, y `REVIEW_INPUT_ABSENT` (INFO) si nunca se generó. Reporte publica `review_inputs` |
| `alignment_reviewer.py` (Bot 2) | `_load_proposal` por el resolvedor; el error-report nombra `read_status`, `source` y `cause` (antes: "No se encontró 02_PROPUESTA_COMERCIAL*.md" sin distinguir ausencia de retención) |
| `asset_reviewer.py` (Bot 3) | `review_inputs`; `_resolve_delivery_zip` respeta la ruta explícita del paquete del run antes que el mtime de `deliveries/`; `_load_manifest` lee el `MANIFEST.json` **dentro del ZIP** |
| `honesty_reviewer.py` (Bot 4) | Propuesta y MANIFEST por el resolvedor; `review_inputs` en sus dos salidas |
| `judge.py` | `_resolve_manifest` consulta primero el paquete del run. **`_compute_verdict` intacto**: la prueba de paridad compara el veredicto y el tier con y sin resolvedor |
| `main.py` | Captura los insumos **antes** del borrado, con `disposition=retained_by_gate` solo cuando el gate va a borrar; borrado por referencia directa; `review_inputs` al Juez y a los cuatro Bots |
| `delivery_packager.py` | `_INTERNAL_DOC_PREFIXES` incluye `review_input_manifest` y `_INTERNAL_DIR_NAMES = ("_review_inputs",)` corta el snapshot por nombre de directorio en el `rglob`. **`write`/`publish`/`suppress` intactos** |

**Nunca se presenta la retención como hallazgo nuevo:** con copia interna leída el revisor no emite
ningún `REVIEW_INPUT_*`; la ausencia inducida por el gate aparece una sola vez y como estado del insumo.

## 4. Mediciones

| Medición | Valor | Instrumento |
|---|---|---|
| PRE (árbol limpio, antes de editar) | **290 passed / 9 skipped / EXIT 0** | `tests_baseline_pre.txt` |
| POST (misma selección y entorno) | **321 passed / 9 skipped / EXIT 0** | `tests_baseline_post.txt` |
| Delta de casos | **+31**, todos del archivo nuevo; 0 bajas, 0 expectativas recortadas, 0 tests existentes re-anclados | conciliación §5 |
| Casos contra funciones | 299 collectados sobre 293 funciones canónicas en el PRE (6 casos de parametrización) | `grep -cE "^\s*def test_"` por archivo |
| Canónicas | **4.908 en HEAD → 4.939 en el árbol (+31)** | `git grep -c -E "^\s*def test_" HEAD -- tests` y el grep del árbol |
| Mutantes | **8 aplicados / 8 rojos por su guard / 8 restaurados por sha256** | `run_mutations.py` → `mutation_report.json`, crudo en `mutaciones_crudo.txt` |
| Validaciones rápidas | **12/13 al abrir el cierre** (rojo Wiring: el derivado vencido por los `.py` de esta fase, 702→704 en alcance y evidencia versionada 141→142) y **13/13** tras `validate_wiring.py --write-report` | `quick_pre.txt`, `quick_final.txt` |
| Snapshot fuera del paquete | Comprobado con el writer real: `source_dir` apuntando a la raíz de la corrida, `namelist()` sin `_review_inputs` ni `review_input_manifest*` | `test_el_snapshot_y_su_manifiesto_no_saluden_al_cliente` (M6 y M7 caen por él) |
| Regresión **completa** (`tests/`) | **1 failed / 5.015 passed / 41 skipped / 4 xfailed / EXIT 1** en 6 min 22 s | `tests_postfull_regresion.txt` |
| Superficie de E (delivery + tribunal + publication gates + P6-R + AC-G1 + data_validation) | **537 passed / 10 skipped** | corrida del sello, §9 |
| Rojo único del suite completo | `test_jev_pilot_deepseek_brazo.py::test_la_falta_de_deepseek_falla_antes_de_enviar_aunque_haya_clave_anthropic` — **pasa aislado** (15 passed el archivo, 1 passed el test) | §8, mismo rojo y mismo dueño que declaró FASE-D §7 |

**Reutilización declarada:** el PRE se tomó sobre el árbol limpio antes de la primera edición y no se
reutilizó para el POST; cada edición de producto posterior al primer POST (los dos ajustes de estado de
lectura y las dos pruebas AST) obligó a re-medir. Las mutaciones se aplicaron sobre el archivo vivo y se
restauraron con el blob que el propio arnés leyó al empezar — **nunca** con `git show HEAD:`, que habría
revertido el producto sin commitear de esta fase.

## 5. Mutantes (los ocho, con la causa que imprimieron)

| ID | Guard mutado | Test que cae |
|---|---|---|
| M1 | `main.py` deja de congelar los insumos antes del borrado | `test_main_congela_los_insumos_antes_de_borrar_los_documentos` |
| M2 | Bot 1 vuelve a construirse sin el resolvedor del run | `test_main_pasa_el_resolvedor_al_juez_y_a_los_cuatro_bots` |
| M3 | El insumo no leído vuelve a ser lista vacía | `test_bot1_insumo_no_leido_no_es_lista_vacia` |
| M4 | Copia interna perdida disfrazada de `READ_ERROR` en vez de `NO_LEIDO` | `test_borrado_sin_copia_interna_es_NO_LEIDO_y_no_OK_vacio` |
| M5 | El orden publica el basename en vez de la ruta real del ZIP | `test_el_asset_nuevo_de_b_viaja_con_su_ruta_real_y_su_orden` |
| M6 | El guard de directorio del snapshot en el writer | `test_el_snapshot_y_su_manifiesto_no_saluden_al_cliente` |
| M7 | El guard por nombre del manifiesto en el writer | `test_el_snapshot_y_su_manifiesto_no_saluden_al_cliente` |
| M8 | `resolve_latest` ignora la ruta explícita y vuelve al mtime entre hoteles | `test_ruta_explitica_gana_a_un_archivo_mas_reciente_de_otro_hotel` |

M7 fue **rojo de instrumento antes de ser diente**: la primera versión del test cotejaba la ruta dentro
del ZIP (`ASSETS/v4_audit/review_input_manifest.json`) contra un prefijo de nombre, y pasaba con el guard
apagado. Se re-escribió para comparar `Path(miembro).name`, y ahí el mutante cae.

## 6. Veredicto por AC

* **AC9 — VERIFICADO OFFLINE.** El lector nuevo publica `READ_OK` (incluye vacío válido), `ABSENT`,
  `READ_ERROR` y `NO_LEIDO`, siempre con `cause`, y nunca devuelve un favorable ante error
  (`test_lector_nuevo_no_devuelve_favorable_ante_un_paquete_roto`). Sobre **baseline real**
  (`output/TAREA7-2026-09-19/`) con skip visible si falta.
* **AC10 — VERIFICADO OFFLINE con el writer real.** `IMPLEMENTATION_ORDER.md` leído del ZIP que escribió
  `DeliveryPackager.write()`, con `### N.`, rutas `ASSETS/` que **existen como miembros**, manifiesto
  coherente con el `namelist()` y el asset nuevo de B (`whatsapp_setup_guide`) en su ruta real. Incluye el
  rojo exigido: capturado después de `suppress()` el hash y el conteo vuelven **None con error declarado**,
  no un verde por membresía.
* **AC11 — VERIFICADO OFFLINE.** Manifiesto con run_id/fuente/hash/ruta interna/`read_status`/`disposition`;
  los cuatro Bots **y el Juez** consumen el resolvedor (gobernado por AST en la ruta de producción y por
  lectura de estado en los cuatro unitarios); retención ≠ hallazgo nuevo; nunca generado sigue `ABSENT`;
  documento declarado e inalcanzable es `NO_LEIDO`; snapshot y manifiesto fuera del paquete.
* **AC12 — VERIFICADO OFFLINE sobre acta real.** Par permitir/bloquear con `publish()`/`suppress()` del
  packager y `ActaWriter`: el acta en disco conserva `enforcement` y `package_evidence` con sha256 y
  `member_count` en **las dos ramas**; `_compute_verdict` y los contratos de cuarentena quedan intactos
  (prueba de paridad).

## 7. Deuda declarada con dueño

1. **El resolvedor no cubre aún los artefactos JSON timestamped** (`pain_ledger.json`, `gate_report_*.json`,
   `delivery_quality_report.json`, `proposal_asset_matrix.json`, `financial_scenarios_*.json`): siguen con
   glob local de `v4_audit_dir` en Bot 1/Bot 3 y con `resolve_latest` sin `explicit` en Bot 4 y el Juez.
   Están dentro del directorio del hotel, así que no compiten entre hoteles; el hueco real es el anclaje por
   `run_id`. **Dueño: FASE-H (preflight) con contraste en VERIFY.** Ninguna fila del plan exige cerrarlo en E.
2. **`REVIEW_INPUT_ABSENT` es INFO a propósito.** Un diagnóstico nunca generado se declara pero no infla
   severidades que no midió nadie; el rojo por retención sin copia sí es WARNING. **Dueño: VERIFY** si se
   decide lo contrario.
3. **`legacy-ancestor-walk` sigue siendo el fallback sin manifiesto.** Se eligió no romper los 4+13+7 tests
   que escriben propuesta en un ascendiente; el estado queda declarado en el reporte en vez de silenciado.
   **Dueño: FASE-H/E2E**, donde el manifiesto siempre existe.

## 8. Checkpoints pendientes de autorización ajena

1. ~~**Commit** (producto + tests + evidencia) y **push**: no autorizados por el mandato.~~ **CERRADO en la misma sesión**: orden literal del operador «Git Commit + L3 + Push». El sha y el rango empujado se estampan en el sello documental de FASE-RELEASE (decisión de C: no abrir sellos recursivos por acciones git). La revisión L3 corrió sobre los commits de la fase y no arrojó hallazgos.
2. **DOMAIN_PRIMER**: no se regeneró. Está versionado y el contrato (§paso 4) exige autorización explícita
   para escribirlo; se declara el checkpoint. Su **verificación** (`doctor.py --context`) es de FASE-RELEASE.
3. **AGENTS.md §Cobertura por Modulo** (+31 en `quality_gates`) y la fila `Estado Actual`: configuración
   central protegida, pide instrucción literal.
4. **Write-back QMind** del aporte de E: operación remota con autorización propia.
5. **R2**: `measure_iterations.py` pide el transcript del cliente y su acceso sigue denegado → métrica
   **FUERA DE SERVICIO (R2.1)** desde la Tarea 1. Auto-reporte con unidad declarada: ~105 invocaciones de
   herramienta al corte «listo para revisión», por encima de la referencia de 60; el exceso se registra como
   checkpoint y **no** se partió la fase.

## 9. Rectificación y medición posterior (orden literal del operador: commit + L3 + push)

El §4 se escribió con la selección POST ya medida pero **sin** el suite completo, que seguía corriendo. Se
re-mide y se publica aquí, sobre el árbol final (tras retirar los dos imports que el cambio de Bot 2 dejó
sin uso en `alignment_reviewer.py`; la selección POST quedó idéntica: 321 passed / 9 skipped / EXIT 0, lo
que confirma que la limpieza fue inerte):

- **Regresión completa `tests/`: 1 failed / 5.015 passed / 41 skipped / 4 xfailed / EXIT 1** (382 s).
- El único rojo es **ajeno y ya declarado por FASE-D §7**:
  `tests/quality_gates/jev_pilot/test_jev_pilot_deepseek_brazo.py::test_la_falta_de_deepseek_falla_antes_de_enviar_aunque_haya_clave_anthropic`,
  contaminación de entorno entre tests del piloto JEV. **Medido en este árbol: pasa aislado** (el archivo
  completo 15 passed; el test solo, 1 passed). Ninguna ruta de E toca esos símbolos. **Dueño: piloto JEV**;
  no se cura aquí (restricción: no corregir hallazgos ajenos).
- **Superficie de E** (delivery + tribunal + publication gates + P6-R + AC-G1 + data_validation):
  **537 passed / 10 skipped**.
- Cada verde de esta fase lleva la etiqueta del árbol donde corrió: **árbol de trabajo sin commitear**. El
  `--quick` 13/13 y el `validate_document_integration.py` sin hallazgos también. El hook `[8/8]` del
  pre-commit lee el tip previo, así que avala el árbol que se stagea, no el commit resultante.
- Los dos arneses de evidencia `.py` (`run_mutations.py`, `cierre_documental.py`) vuelven a mover los
  contadores del derivado de wiring: se regeneró con `validate_wiring.py --write-report` y el quick quedó
  13/13. No se recortó ninguna aserción.

## 10. Lo que sigue siendo del operador

`briefing/` bajo `.opencode/plans/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/` llegó al árbol como material
**no propio de esta sesión** y **no viaja en este commit**; se declara para que su dueño lo estampe.
