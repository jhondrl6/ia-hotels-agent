# FASE-B — resultados y observaciones medidas (2026-09-20)

**Estado de la fase: CERRADA CON DEUDA REGISTRADA (AC5 → dueño C-D).** El producto de AC1 y
AC2 está implementado y medido; el cierre se había detenido por un bloqueo de alcance medido
(§Bloqueo) y por falta de autorización de commit, y **ambos se resolvieron en la misma
sesión**: A1 autorizado y ejecutado (§3 y §7), A4 decidido con O5 (§7), commit
`473ed0f` con autorización literal. Solo queda pendiente el push (A3). Contador v4complete:
**0/1** (no se ejecutó ninguna corrida).

HEAD de partida: `cf3ddc2` (árbol limpio, paridad 0/0 con `origin/master`). Código de
FASE-0 (`7c6e75f`) y de FASE-G (`66e17bd`) ya estaban en `master`, como declaraba el
prompt: no hubo nada que revertir ni rescatar.

## 1. Qué se cambió (todos los archivos dentro de la allowlist de B)

| # | Archivo | Cambio | AC |
|---|---|---|---|
| 1 | `modules/asset_generation/v4_asset_orchestrator.py` | `generate_assets` deriva **una vez** `whatsapp_html_detected` desde `audit_result.validation` y la propaga a `PainSolutionMapper.detect_pains` y a las **dos** llamadas de `CoherenceValidator.validate` (pre-gen y post-gen) | AC1 |
| 2 | `scripts/validate_wiring.py` | Retiradas las tres excepciones tipadas (`HALLAZGO_CONOCIDO`, dueño FASE-B/AC1) que amparaban esas omisiones; sin hallazgo que amparar habrían caído en `EXCEPCION_VAGA` | AC1, AC7 |
| 3 | `modules/commercial_documents/pain_solution_mapper.py` | `no_whatsapp_visible` promete `whatsapp_setup_guide` (ya no `whatsapp_button`); retirado el `can_generate = True` forzado para `whatsapp_conflict`; nombre comercial del servicio nuevo en `ASSET_NAMES`; docstring/`description` reescritos para no afirmar ausencia | AC1, AC2 |
| 4 | `modules/asset_generation/asset_catalog.py` | Entrada `whatsapp_setup_guide` (`required_field="hotel_data"`, `required_confidence=0.4`, `block_on_failure=False`, `promised_by=["no_whatsapp_visible"]`) | AC2 |
| 5 | `modules/asset_generation/whatsapp_setup_guide.py` | **Nuevo**: generador de la guía de preparación/validación. Sin número, sin `wa.me`, sin placeholder numérico; no afirma que el hotel no tenga WhatsApp | AC2, AC19a |
| 6 | `modules/asset_generation/conditional_generator.py` | `PAIN_TO_ASSET["no_whatsapp_visible"] = "whatsapp_setup_guide"` (pain y asset dejaron de decidir aparte, fila F-F) + rama de dispatch en `_generate_content` | AC2 |
| 7 | `modules/asset_generation/pain_ledger.py` | `STATUS_NOT_VERIFIED_IN_SITE = "NO_VERIFICADO_EN_SITIO"` y `PAINS_QUE_PIDEN_CONFIRMACION`; `PAIN_TO_PRESENCE_ASSET["no_whatsapp_visible"]` pasa a `whatsapp_setup_guide` (una huella de plugin ya no promociona a `VERIFIED_IN_SITE`); `apply_site_verification` registra la acción pendiente cuando no hay evidencia verificada | AC19a, L-PF6 |
| 8 | `modules/asset_generation/whatsapp_conflict_guide.py` | `_build_recommendation` **deja de elegir número** por cantidad de reseñas (>=10) ni por precedencia web: presenta candidatos y exige validación humana; sin candidatos lo declara explícito | AC2 |
| 9 | `modules/common/service_identity.py` | Nuevo servicio `guia_configuracion_whatsapp`; `boton_whatsapp` mueve su disparador a `whatsapp_conflict` (única vía que queda para planificar el botón) | AC2 |
| 10 | `modules/commercial_documents/v4_diagnostic_generator.py` | Narrativa de `no_whatsapp_visible`: «Canal Directo Cerrado (Sin WhatsApp)» → «Canal de WhatsApp sin verificar», con texto que pide confirmación | AC19a |
| 11 | `main.py` | Comentario `FIX-D7` corregido (presentaba `whatsapp_button` como `promised_by=always`, condición que el catálogo eliminó en FASE-5). Único cambio en `main.py`, según la allowlist | — |

Tests: nuevo `tests/commercial_documents/test_fase_b_promesa_whatsapp.py` (11 funciones
canónicas / 12 casos) y re-vinculaciones en seis archivos existentes (§4).

## 2. Mediciones

| Qué | Comando o instrumento | Resultado |
|---|---|---|
| PRE (selección literal de 25 archivos) | `pytest $(cat FASE-B/seleccion_pertinente.txt) -q` | **537 passed**, exit 0, 49.98 s → `tests_baseline_pre.txt` |
| Quick PRE | `scripts/run_all_validations.py --quick` | **11/11** → `quick_pre.txt` |
| POST-A (misma selección literal) | igual que PRE | **539 passed**, delta **+2**, explicado: dos tests nuevos en `test_site_verification_propagation.py` (casos WhatsApp de AC19a) |
| POST-B (selección + suite nueva) | + `test_fase_b_promesa_whatsapp.py` | **551 passed** (+12 casos por 11 funciones, una parametrizada en 2) |
| POST-C (superficie de matriz, fuera de allowlist) | `test_fase_c_propuesta_dinamica.py`, `test_proposal_asset_matrix.py` | **7 failed / 31 passed** → §3 |
| Regresión completa | `pytest tests/ -q` | 18 failed / 4246 passed / 41 skipped / 4 xfailed en 229.74 s, medida **antes** de las últimas dos re-vinculaciones; 15 de esos 18 eran la superficie de matriz/gate (ver decisión de `counts_in_alignment`) y 3 son los rojos preexistentes con dueño |
| Funciones canónicas | `grep -rE "^\s*def test_" tests --include=*.py \| wc -l` | **4 298** (4 285 al cerrar FASE-0 → **+13**) |
| Guard de cableado | `scripts/validate_wiring.py` | 169 llamadas / 613 archivos; gobernadas 70 con **conformes 17, omisiones 0, excepciones amparando 0, violaciones 0** |
| Mutantes | `FASE-B/run_mutations.py` → `mutation_report.json` | **8/8 rojos causados por el guard (M1-M8)**, ninguno verde persistente, **8/8 restaurados y verificados por sha256** |

Los mutantes y su efecto medido (M1-M6 en el primer cierre; M7 y M8 se anadieron al ejecutarse A1, y el reporte se re-ejecuto completo: 8/8): M1 quitar el kwarg en `detect_pains` (pytest 1,
wiring 1); M2 quitarlo solo en la pasada pre-gen (pytest 1, wiring 1 — confirma que el
guard exige las tres, no una); M3 reintroducir `can_generate=True` para conflicto
(pytest 1); M4 devolver `whatsapp_button` al pain de ausencia (pytest 1); M5 hacer que
la guía emita un número (pytest 1); M6 dejar una excepción tipada sin hallazgo (pytest
1, wiring 1 por `EXCEPCION_VAGA`). **M7** contar el servicio condicional dentro del universo contado del gate (pytest 1); **M8** hacer que la tabla de resolucion vuelva a ser copia del universo contado (pytest 1).

## 3. Bloqueo de alcance (medido en la fase; resuelto dentro de la misma sesión con A1 y A4)

`modules/asset_generation/proposal_asset_alignment.py` **no está en la allowlist de B**
y es a la vez (i) el universo de servicios que el gate `proposal_asset_alignment`
exige ver entregados en **toda** corrida y (ii) la tabla con la que
`AssetAlignmentMatrix` resuelve servicio→brecha→asset. Propagar un servicio
**condicional** al dolor de WhatsApp exige tocar ese doble uso y no hay forma de
hacerlo sin cambiar el denominador del gate, que el contrato asigna a 0/D/E.

Las dos opciones fueron medidas, no elegidas por comodidad:

- `counts_in_alignment=True` (propagación completa): el gate pasa a pedir la guía en
  corridas de hoteles sin ninguna brecha de WhatsApp → **15 rojos** en
  `test_proposal_alignment_gate`, `test_alignment_result`, `test_alignment_contract`,
  `test_publication_gates_presence`, `test_fase_c_propuesta_dinamica`,
  `test_proposal_asset_matrix`, `test_phase4_guardrails`. Rojo de producto real, no de
  literal: cambiaría la contabilidad de cobertura de todos los hoteles.
- `counts_in_alignment=False` (estado actual): esos gate/matrix vuelven a verde y queda
  **1 rojo de guard de confianza** resuelto subiendo el catálogo a 0.4 (el piso 0.4 del
  guard se respetó, no se le bajó) y **7 rojos** en la superficie de matriz, que son los
  de §2 POST-C. Estos siete son la evidencia del bloqueo: la matriz no puede resolver
  `Configuración de WhatsApp` porque no está en su tabla, y lo reporta como
  `unknown_services`.

**Decisión:** detener aquí en vez de editar el gate (contrato: «La tabla no amplía
allowlists. Si un cambio exige otra superficie, detener y resolver alcance»). Opción
recomendada para la sesión que reanude B: autorizar explícitamente
`modules/asset_generation/proposal_asset_alignment.py` dentro de B, separando «tabla de
resolución» de «universo contado» (cambio pequeño, con tests propios), o reasignar esa
propagación a D/E según la tabla de dependencias.

## 4. Re-vinculaciones de tests ajenos (todas por cambio de forma, ninguna por expectativa aflojada)

- `test_proposal_alignment.py` (5 asserts) y `test_proposal_dynamic.py` (3): los
  literales `7`, `8` y `9` se re-ataron al registro (`len(PROPOSAL_SERVICE_TO_ASSET)`,
  conteo de `SERVICE_IDENTITIES`, `SERVICE_CATALOG` menos la condición AEO), siguiendo
  `L-V2.3`. Siguen siendo aserciones exactas: lo que cambió es la fuente del esperado.
- `test_promised_assets_production.py` (C1, C3) y `test_coherence_generated_assets.py`:
  los fixtures enumeraban «todos los assets planificados» a mano; ahora uno de ellos se
  deriva del propio plan. El gate `promised_assets_exist` detectó el asset nuevo y **no
  se le modificó**: fue el fixture el que quedó incompleto.
- `test_site_verification_propagation.py`: los tres casos que usaban
  `no_whatsapp_visible` + `whatsapp_button` para probar el mecanismo genérico de
  propagación se re-ancoraron a `no_hotel_schema` + `hotel_schema` (mismo mecanismo,
  asset que sí es verificable en sitio). **No** se cambió ninguna expectativa: se cambió
  el ejemplo. Como compensación se añadieron dos tests propios de la regla nueva
  (`test_whatsapp_fingerprint_no_verifica_el_pain_de_ausencia`,
  `test_whatsapp_sin_reporte_de_presencia_registra_pendiente`).
- `test_validate_wiring.py` (3): G ancló estas pruebas a la divergencia **viva** del
  repo (tres omisiones). Al cerrarse AC1, el anclaje quedó falso. Se re-ataron: una
  afirma ahora que las omisiones están cerradas y que no sobrevive excepción; otra
  produce el rojo del CLI en un árbol sintético (`tmp_path`) en vez de depender del
  estado del repo, para que no vuelva a caducar.
- `test_proposal_dynamic.py::test_servicios_adicionales_con_brecha_whatsapp`: la brecha
  que compromete el botón pasó a ser `whatsapp_conflict` y se añadió el caso negativo
  (brecha de ausencia ⇒ el botón **no** se ofrece), que es la exigencia de AC2.

## 5. Observaciones medidas (tres o más, sin lecciones fabricadas)

- **O1 — la divergencia F-A' era de cable, no de política.** Con `whatsapp_html_detected`
  propagado, `detect_pains` emite `no_whatsapp_visible` **solo** sin HTML y con campo
  UNKNOWN/CONFLICT. Medido con el par de fixtures producibles; un fixture «hay HTML» sin
  campo no-touching no discrimina nada (`L-T4A.5`).
- **O2 — `PAIN_TO_PRESENCE_ASSET` estaba casado con Capa 1 por un test, y eso salvó el
  diseño.** `test_pain_to_presence_asset_valida_contra_capa1` exige
  `assets[0]`, así que cambiar la promesa de ausencia obligó a cambiar también qué
  verifica la presencia; sin ese guard, la huella de plugin habría seguido
  promocionando el pain a `VERIFIED_IN_SITE` con severidad LOW, que es el falso positivo
  medido en Don Alfonso (`exists`/0.85 sin número).
- **O3 — el residuo de promesa que B no gobernar.** `wa_button_gen`
  (`modules/delivery/generators/wa_button_gen.py:30-41`) sigue fabricando
  `573001234567` cuando no hay número, y `local_content_generator.py:530/559` construye
  dos `wa.me/` sin guarda. Inventarios de la Tarea 1 que B no toca (el plan prohíbe
  reutilizar el generador legacy; eliminarlo es alcance de C/D con AC6).
- **O4 — `main.py:2266-2275` sigue marcando `can_use_in_assets=True` al centinela
  `detected_via_html`.** La matriz del maestro §2 lo pide en `False`, pero ese bloque
  está fuera de la allowlist de B (en `main.py` B solo podía corregir el comentario
  `FIX-D7`). B lo defendió aguas abajo en la capa de promesa (guía en vez de botón, y
  ninguna ruta de ausencia planifica el botón); el fix en el origen queda con dueño
  C/AC6.
- **O5 — la métrica R2 quedó FUERA DE SERVICIO (R2.1)**: el instrumento
  (`measure_iterations.py`) exige el transcript de la sesión y su acceso no está
  disponible. Auto-reporte en unidad propia: ~155 intervenciones de herramienta hasta
  este cierre, **muy por encima** de la referencia de 60 hasta el corte de código. El
  exceso produjo checkpoint, no un salto de fase (contrato §R2).

## 7. A1 autorizado y ejecutado en la misma sesión (2026-09-20, segunda parte)

El operador autorizó extender la allowlist de B a `proposal_asset_alignment.py` con un
único cambio: separar la tabla de resolución del universo contado.

- Nacen `RESOLUCION_SERVICIO_A_ASSET` y `ALL_RESOLVABLE_SERVICES` (todos los servicios
  del registro canónico). `PROPOSAL_SERVICE_TO_ASSET` / `ALL_PROMISED_SERVICES` quedan
  igual: mismo filtro `counts_in_alignment`, mismo denominador del gate, mismos
  umbrales, mismo `BLOCKING_VERDICTS`, mismo Juez, mismos contratos
  `write/publish/suppress`.
- Las dos búsquedas (`verify_proposal_asset_alignment` y
  `classify_promised_services`) resuelven contra la tabla completa, así que
  `Configuración de WhatsApp` deja de caer a `unknown_services` cuando se lo pide
  explícitamente.
- **Descartado por medición, no por gusto:** ampliar el universo de la matriz con los
  servicios condicionales comprometidos por el ledger (implementado y re-medido) hizo
  que `ProposalAssetMatrix.build(["Servicio Inexistente", "Botón de WhatsApp"], …)`
  devolviera filas de servicios que nadie pidió y rompió el par anti-A5
  `test_particion_identica` (13 rojos en lugar de 7). Se revirtió; gobernar el universo
  de la matriz es AC5, cuyo dueño vinculante es **C-D** (maestro §4 y filas C y D de la
  matriz; donde este archivo decía "D/E" estaba mal atribuido).
- Los 7 rojos de matriz se cerraron **re-ancorando el dolor de los fixtures**, no la
  aserción: `no_whatsapp_visible` → `whatsapp_conflict` en
  `test_proposal_asset_matrix.py` (3 sitios) y en el fixture compartido de
  `test_fase_c_propuesta_dinamica.py` (2 sitios), porque AC2 movió exactamente esa
  promesa. POST-C: **83 passed / 0 failed**.

**Rojo residual, con causa medida y dueño declarado.** Regresión completa tras A1:
**4 failed / 4.261 passed / 41 skipped / 4 xfailed** en 244 s. Tres son preexistentes
con dueño (`test_function_default_flags` flaky, `test_diagnostic_includes_geo_metrics`,
`test_medido_contra_el_predecesor_entra_en_alcance…`). El cuarto es nuevo y es de B:
`tests/quality_gates/test_publication_gates.py::TestPublicationGatesOrchestrator::test_get_blocking_issues`
espera 3 gates bloqueantes y ve 2. Causa: el assessment del test pone
`no_whatsapp_visible` en el ledger sin assets entregados; tras AC2 el único servicio
que responde ese dolor es condicional y no está en el universo contado, así que
`committed` queda vacío y `_proposal_asset_alignment_gate` toma el
`PASS trivial (never-block)`. **Posición inicial (se retracta abajo):** no re-anclar el test
porque su propósito —una brecha sin asset entregado debe verse como deuda— seguía vigente, y
cambiarlo podía leerse como debilitar un guard del gate desde una fase que no lo posee.

**Retractación y decisión (A4, misma sesión, O5 en `A4-decision.md`):** al medir el fixture se
vio que el propósito del test es otro —`get_blocking_gates` devuelve **solo** los gates
fallidos— y que su tercer bloqueante era incidental: venía de que `no_whatsapp_visible`
prometía `whatsapp_button`, servicio contado antes de B. Se re-ancló el dolor a
`whatsapp_conflict` (sigue prometiendo `boton_whatsapp`: `actionable_total=1`,
`coverage_ratio=0.0`, `BLOCKED`), se **reforzó** la aserción con
`assert "proposal_asset_alignment" in blocking_names`, y la denuncia del punto ciego no se
perdió: vive en `test_deuda_ac5_ledger_solo_condicional_pasa_trivial`, que aserta el pase
trivial de hoy y **debe ponerse rojo cuando AC5 lo gobierne**. El gate no se tocó. Superficie
**AC5, dueño C-D** (el "D/E" escrito aquí era un error de registro: E no posee AC5; maestro §4
y filas C y D de la matriz).

**Cierre ejecutado tras A1:** CHANGELOG (subsección FASE-B bajo 4.77.3), nota técnica en
`docs/GUIA_TECNICA.md`, aplicación efectiva de lecciones en `00`, estados en `05`/`06`/
`dependencias`, `log_phase_completion.py --fase FASE-B`, `build_lesson_index.py` +
`--check`, quick y `validate_document_integration.py`. **Commit y push sin ejecutar.**
Medidas finales: selección PRE 537 → POST-A 539 → POST-B 552; canónicas
**4.285 → 4.299 (+14)**; mutantes 8/8 (M1-M8); quick **11/11**.

## 6. Pendientes declarados antes de A1 (histórico de la misma sesión)

1. Resolver el bloqueo de §3 (autorizar `proposal_asset_alignment.py` en B o reasignar
   la propagación a D/E) y dejar los 7 rojos de matriz en verde sin tocar el gate.
2. POST completo de nuevo (regresión entera con las dos últimas re-vinculaciones) y
   recuento final de funciones canónicas.
3. Cierre incremental del contrato: `log_phase_completion.py --fase FASE-B …`,
   CHANGELOG + GUIA_TECNICA, `00`/`06`/`09`/`10`/`dependencias`/`README`,
   `build_lesson_index.py` + `--check`, quick y `validate_document_integration.py`.
   **Nada de esto se ejecutó**: registraría como cerrada una fase con rojos en su
   superficie.
4. Commit y push: requieren instrucción literal del operador (no estaban autorizados).
