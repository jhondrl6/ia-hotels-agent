# Documentación post-proyecto — REFACTOR-WHATSAPP-ENTREGA-2026-09-18

Estado al 2026-09-24: **cuatro fases cerradas con su documentación incremental propia** (A, G, 0 y B; B con deuda AC5 → dueño C-D). Punto de reanudación: FASE-C. ⟦Reconciliado por el bloque C de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`; la línea anterior decía «PREPARACIÓN. Ninguna fase ejecutada», que es el retrato de la concepción y quedó vencido⟧. Este archivo **no** sustituye la documentación incremental de cada fase ni permite registrar retrospectivamente todas las fases en RELEASE, y **no re-transcribe** métricas que ya viven en su fase: las referencia.

## Sección A: Módulos nuevos

| Módulo | Archivos | Descripción | Fase |
|---|---|---|---|
| Verificador AST de cableado (`scripts/`) | `scripts/validate_wiring.py` (905 líneas), `tests/test_validate_wiring.py` (464 líneas, 18 funciones canónicas), artefacto `.opencode/wiring_report.json` | Check 11 del modo rápido: descubre por AST la población de callers de los productores gobernados sin lista fija de archivos, exige las señales cuyo default cambia la conducta en silencio, prohíbe el contrato muerto retirado, y publica población, cobertura, excepciones tipadas y límites. Reporta y **no** reescribe callers | **FASE-G (2026-09-20)** |

| Contrato de WhatsApp (`modules/data_validation/`) | `modules/data_validation/whatsapp_contract.py` (nuevo, ~190 líneas), `tests/asset_generation/test_fase_c_boton_seguro.py` (24 funciones canónicas / 39 casos) | Hoja única para los dos lectores de WhatsApp: designación de roles (presencia vs dolor), vocabulario de patrones compartido, clasificación de evidencia, estados de lectura y contrato de forma del número con causas nombradas | **FASE-C (2026-10-06)** |

## Sección B: Funcionalidades nuevas

| Feature | Módulo | Descripción | Fase |
|---|---|---|---|
| Anotacion de recall en el productor (`modules/quality_gates/`) | `PublicationGatesOrchestrator._critical_recall_details` (nuevo metodo, ~40 lineas) y su llamada desde la rama PASSED de `_critical_recall_gate`; `tests/test_fase_0_ac20_evidencia_veredicto.py` (21 funciones canonicas) | Devoluciona la serie de confianza del recall favorable: `critical_issues_count` + `recall_basis` para los caminos fundados (`all_critical_issues_detected`, `evident_critical_issues_missed`) y conserva la serie SR-H2; los casos no fundamentados siguen con `details: {}` porque ahi la ausencia es la senal que L-SR5 manda preservar | **FASE-0 (2026-09-20)** |
| Evidencia del paquete entregado (`main.py`) | `main._record_published_package_evidence` (nuevo, never-block por dentro) y su llamada tras cada `packager.publish(` en las dos ramas de publicacion | El ZIP entregado queda con `sha256`, `member_count`, `path` y `suppressed: False` en el acta; `publish()` es `rename`, asi que el hash se calcula sobre la ruta publicada (mismos bytes) | **FASE-0 (2026-09-20)** |
| Gobierna señales por productor (no fix) | `validate_wiring.py` | Refactor de guard: 4 productores en política (`PainSolutionMapper.detect_pains`, `CoherenceValidator.validate`, `AssessmentBuilder.with_validation`, `V4ProposalGenerator._generate_dynamic_services_table`) con sus señales y argumentos prohibidos. **No arregla** la divergencia: la registra con dueño | FASE-G |
| Contrato muerto retirado (F-D') | `modules/assessment_builder.py` + `main.py` | `with_validation(self, validation_summary)`: se quita `whatsapp_validation` de la firma y de sus 3 callers. El dato upstream (8 líneas de `main.py` que construyen los `ValidatedField`) se conserva: no es un fix, es limpieza de firma cross-module | FASE-G |
| Numeración del quick re-estimada | `scripts/run_all_validations.py`, `tests/test_validate_lesson_capitalization.py` | El modo rápido pasa de 10 a 11 checks y el completo a /15. El contract test que pineaba el literal `[10/10]` se reescribió a **coherencia estructural** (grupo derivado de `run_all`, ordinales exactos 1..D), que es más fuerte: detecta borrar, duplicar o re-ordenar, no solo escribir mal un número | FASE-G |
| Causas legibles en el acta | `modules/quality_gates/tribunal/outcome.py` | `ReviewerReport.to_dict()` proyecta los hallazgos (`finding_type`, `severity`, `clause`, `description`) con lista blanca, truncado a 240 y tope de 20 por revisor con `findings_omitted`. Un acta con `critical_count >= 1` ya no puede quedarse sin causa (AC12/AC20). Medido sobre la corrida real: JSON +1.151 bytes, MD +0 bytes | FASE-0 |
| Recall fundado autoportante | `PublicationGatesOrchestrator` + `DiagnosisReviewer` | La correccion vive en el **productor del dato**, no en el detector: `_check_vacuous_recall` queda intacto y conserva su defensa del caso genuinamente vacuo (SR-H2 / L-SR5). Un `details` sin conteo sigue siendo inequivoco y sigue siendo denunciado | FASE-0 |
| Botón con destino validado (`modules/asset_generation/` + `modules/data_validation/`) | `whatsapp_contract.py` (nuevo), `conditional_generator.py` (`_campo_whatsapp_validado`, guard en `_generate_whatsapp_button`, rama de rechazo en `generate`), `v4_asset_orchestrator.py` (FIX-A2 curado), `coherence_validator.py` (boost retirado), `main.py` (centinela no utilizable), `site_presence_checker.py` + `site_presence_adapter.py` (AC19a aditivo) | El botón recibe exclusivamente el campo validado y normalizado; una entrada inutilizable se rechaza **antes** de emitir href, con causa y destino reportados. La presencia deja de promocionar a VERIFIED | **FASE-C (2026-10-06)** |

| Veredicto canónico del pre-gate y causas serializadas (`main.py` + `modules/quality_gates/` + `modules/commercial_documents/`) | `main._coherence_pre_gate_decision`, `main._persist_coherence_pre_gate`, `main._run_asset_generation` (nuevos), `coherence_validator.failed_error_checks` + `read_coherence_report` + `mask_telephone_digits` (nuevos), `assessment_builder.with_coherence` (fallback con el reporte propio + campo `coherence_failed_checks`), `publication_gates._coherence_cause_details`, `v4_asset_orchestrator.assert_pre_generation_coherence` | El pre-gate decide por `coherence_verdict_passes` y no por score suelto; un check de severidad error sin resolver impide entrar a generar assets y propuesta, persiste `coherence_pre_gate_<ts>.json` con los culpables enmascarados y los publica en `gate_report_*.json` (`details.failed_check_names` y mensajes) sin whitelist. La entrada directa del orquestador corta igual. Umbral 0.8 y flag `blocking` intactos (AC5) | **FASE-D (2026-10-06)** |

## Sección D: Métricas acumulativas

| Métrica | Valor | Fase |
|---|---|---|
| HEAD de preparación | `7d91c9f` (v4.77.0) · **HEAD de la revisión 2: `938f59f` (v4.77.3)** | Preparación / revisión 2 |
| Corridas v4complete de este plan | 0; presupuesto total 1 | Preparación |
| Validaciones rápidas PRE | 9/10 el 2026-09-18 (rojo Version Sync por cuatro documentos sucios en el árbol) y 10/10 al re-medir el 2026-09-19 | Preparación |
| Causa del rojo Version Sync | **Causa real, medida 2026-09-19:** el quick del 2026-09-18 fallaba porque `AGENTS.md`, `VERSION.yaml`, `docs/GUIA_TECNICA.md` y `REGISTRY.md` estaban modificados en el árbol; hoy esos cuatro archivos son idénticos a HEAD (revertidos fuera de esta sesión, mtime 11:06-11:10) y el quick da 10/10. `_check_version_sync` se limita a invocar `sync_versions.py --check`, así que la hipótesis de un desacuerdo verificador↔escritor queda retractada: era estado transitorio del working tree, ya resuelto. | Preparación |
| Sitio del hotel verificado en preparación | NXDOMAIN en la URL del warehouse; 200 en la del usuario. **Rectificado en la revisión 2:** el detector **sí observa** el canal en la raíz — medición con `SitePresenceChecker._check_html_element` devuelve `found=True` vía `css_class: joinchat …` y la corrida real archivó `whatsapp_button: exists / 0.85`. Lo que no aporta es número. La redacción anterior ("ausente del HTML estático que lee el detector") queda retractada | Preparación + revisión 2 |
| **Nueva (revisión 2): corrida de referencia ya archivada** | `output/TAREA7-2026-09-19/` — v4complete del 2026-09-19 15:01 sobre el hotel y la URL del §5: readiness `READY_FOR_PUBLICATION`, 13/13 gates, **veredicto `BLOQUEADO` y ZIP suprimido** por un único CRITICAL `VACUOUS_RECALL`; `pain_ledger` sin pain de WhatsApp; `whatsapp_verified` en verde vacuo. Es baseline medido del plan, no consume el intento | Revisión 2 |
| **Nueva (revisión 2): contrafactual de AC20** | `TribunalJudge._compute_verdict` ejecutado en memoria sobre esa acta: con el hallazgo → `BLOQUEADO`; con `details.critical_issues_count` fundado y recomendación recalculada → `APROBADO-CONDICIONAL-PENDING-ONBOARDING` (no bloqueante). Intermedio falso descartado: zero de `critical_count` sin recalcular `recommendation` no volta el veredicto | Revisión 2 |
| **Nueva (revisión 2): blast radius de AC19** | 8 consumidores del reporte canónico de presencia; 816 funciones de test canónicas en 52 archivos del vecindario (866 casos collectados), **545 de ellas en 31 archivos que citan `status`/`site_verified`/`presence_status` entre comillas dobles**, 4 asserts de igualdad exacta de forma. Dos cifras de pasadas anteriores quedan refutadas y trazadas en el anexo: 50/779/328/2 (subagente sin re-medir) y 26/476 (anotada sin criterio reproducible; trece criterios medidos dan una banda 22/427 → 32/552). La división AC19a/AC19b se apoya en las cifras reproducidas | Revisión 2 |
| Índice | 305 IDs, fresco (preparación) · **314** tras la intervención del 2026-09-19 · **316** tras la revisión 2 (nacen `L-ENT.10` y `L-ENT.11`) · **318** al cerrar G (nacen `L-ENT.12` y `L-ENT.13`) · **319** el 2026-09-20 tras el write-back (nace `L-ENT.14`, la medición de ausencia recortada por un `head`). «Citados sin definición»: 43 hasta la revisión 2 y **48** hoy — cuatro son `L-QW.1` a `L-QW.4`, reservadas por el mini-plan que aún no tiene `10-analisis`, y la restante es el prefijo de esa serie, que el indexador captura del comando literal de conteo registrado en el Paso 0 del propio mini-plan | Preparación / revisiones / G / write-back |
| **FASE-0: par contrafactual medido sobre el artefacto real** | `TribunalJudge._compute_verdict` en memoria sobre copia temporal del acta archivada: con el hallazgo `BLOQUEADO`; con la anotacion del productor y la recomendacion recalculada `APROBADO-CONDICIONAL-PENDING-ONBOARDING`, que no esta en `BLOCKING_VERDICTS`. Tercera confirmacion del mismo par (revision 2 lo midio primero, FASE-0 lo reproduce con el codigo ya cambiado) y novedad medida: el mutante de hacer cero del conteo **sin** recalcular la recomendacion sigue `BLOQUEADO` | FASE-0 |
| **FASE-0: conteo real del recall fundado** | El `audit_report` de la corrida lista 3 `critical_issues`, pero el assessment que llega al gate lleva **4**: `AssessmentBuilder.with_geo_flow` (FASE-G) anexa el de banda GEO. El numero que publicara `details` es el de la lista efectiva al momento del gate, no el del audit | FASE-0 (O1/O2 en `resultados-y-observaciones.md`) |
| **FASE-0: crecimiento del acta** | JSON 1.362 -> 2.513 bytes (+1.151, +84 %); MD +0 bytes; los cuatro `revision_*.json` de la corrida suman 9.155 bytes, asi que la proyeccion no es una copia | FASE-0 |
| **FASE-0: tests, quick y regresiones** | Seleccion literal de 12 archivos: PRE 189/1 skipped y POST-B 189 (**delta 0**); POST-A 210 con las 21 pruebas nuevas; funciones canonicas 4.264 -> **4.285**; regresion completa 3 failed / 4.247 passed / 41 skipped / 4 xfailed (los 3, preexistentes y con dueño); quick **11/11**; 6/6 mutaciones rojas por el guard con restauracion por sha256 | FASE-0 |
| Tests nuevos / casos recogidos / passed | No medidos; no confundir funciones con casos parametrizados | Pendiente |
| Coherencia / veredicto / ZIP | **Ninguna corrida de este plan.** Baseline leído de una corrida ajena ya archivada: coherencia 0.8633, `readiness: READY_FOR_PUBLICATION`, veredicto `BLOQUEADO`, ZIP suprimido tras `member_count: 52` | Revisión 2 (lectura de `output/TAREA7-2026-09-19/`) |
| **FASE-A: gates de la corrida de referencia, re-medidos** | **Rectificación de P3:** los "13/13 gates verdes" son en realidad **10 PASSED + 3 WARNING** (`financial_validity`, `asset_confidence`, `pricing_compliance`), **0 fallidos** y `blocks_publication=False` en los 13. El razonamiento no cambia — el ZIP se suprimió sin ningún gate fallido— pero la cifra publicada era imprecisa | FASE-A (lectura de `gate_report_20260919_150131.json`) |
| **FASE-A: tercera ruta de publicación sin evidencia** | `package_evidence` se escribe solo en la rama `_outcome.blocks_publish` de `main.py`; **además** del `packager.publish()` que ya conocía el plan, el `except` "Tribunal enrichment failed (never-block)" publica una segunda vez sin hash ni conteo. AC20 (iii) la incorpora | FASE-A → FASE-0 |
| **FASE-A: superficies de tests pertinentes** | 7 archivos, **130 funciones canónicas** → **134 casos** recolectados, **133 passed + 1 skipped**, exit 0, sin red (0 coincidencias de `requests/urllib/socket`). Incluye las dos superficies que gobernará FASE-0 | FASE-A (`tests_pertinentes_pre.txt`) |
| **FASE-A: blast radius de AC19, tercera medición** | Reproduce el método canónico y da **52 archivos / 816 funciones** y **31 / 545**, idéntico a lo publicado en `d4dacb4`; los 4 asserts de igualdad exacta localizados por símbolo | FASE-A |
| **FASE-A: QMind** | Consulta **recuperada** tras la denegación de la revisión 2; 6 aportes, 3 ya cerrados en código vivo. Sin subida | FASE-A |
| **FASE-G: población medida por el verificador** | 611 archivos en alcance, **169 llamadas descubiertas**, **70 gobernadas** (14 conformes, 3 omisiones con dueño), 74 exclusiones por clase (71 de ellas a un método que se llama `validate` en clase ajena), 25 receptores sin resolver de los cuales **0 en producción** | FASE-G |
| **FASE-G: quick y firmas** | Quick **10/10 al abrir** y **11/11 al cerrar**; 4.246 → **4.264** funciones canónicas del repo (+18); par PRE/POST con selección literal: PRE 1.313 passed / 1 failed / 2 skipped, POST-A idéntico (delta 0), POST-B 1.331 (+18); 7/7 mutaciones con rojo causado por el guard | FASE-G |
| **FASE-G: precisión nueva sobre la fila F-A'** | El maestro §1 describe **una** invocación divergente; el AST midió **tres** en `v4_asset_orchestrator.py` (286 `detect_pains`, 309 y 447 `CoherenceValidator.validate`), todas omitiendo `whatsapp_html_detected`. Segunda confirmación interna de `L-V.3` sobre una premisa del propio plan | FASE-G |
| **FASE-G: QMind** | Consulta por el eje de cierre **permitida y respondida** (Q12); tres de sus filas se aplicaron y midieron. **Write-back ejecutado el 2026-09-20** con autorización literal separada: instantánea saneada del `10-analisis` (5 identidades del cliente sustituidas; `Alfonso` → 0 coincidencias en lo subido), fuente `01a0bfc9-…` verificada por **descarga byte a byte (39.422 B) y sha256**, no por título. Límite registrado: `--upload` sube el archivo crudo; su modo verificación solo mira `Archives/` y, a diferencia de lo que una afirmación anterior de esta sesión sostenía, **sí** está invocado por `run_all_validations.py` como [15/15] en el modo completo — pero decide por título, así que da verde con contenido obsoleto | FASE-G |
| **FASE-G: rojo preexistente con causa medida** | `test_medido_contra_el_predecesor_entra_en_alcance_y_su_forma_es_conforme[2026-09-11-…]` está rojo desde `9c4a001` (archivó `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` y `clasificar_planes` solo mira hijos directos de `.opencode/plans/`). G lo conserva igual en PRE y POST, sin excluirlo ni cambiar su expectativa | FASE-G → dueño: deuda del verificador de capitalización ⟦— **cerrada la deuda el 2026-09-27 y con ella esta fila**: `clasificar_planes()` dejó de saltar `Archives/` (decisión (a-prima) de S29, fuente única `…/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/dependencias-fases.md` §S29). El test pasó con su aserción intacta; la medición PRE/POST por población está en `evidence/…/CIERRE-ORDEN-2026-09-25/S29-A-PRIMA-2026-09-27/`⟧ |
| Presupuesto de iteraciones | **FUERA DE SERVICIO (R2.1) también en G** (2026-09-20): el instrumento sigue pidiendo el transcript. Auto-reporte en unidad contable (9 rutas tocadas, 2 corridas de baseline + 1 extendida, 7 mutaciones, 2 quicks) con corte de código y corte documental separados; **no se comparó con la referencia de 60 porque esa unidad no era medible** | Todas |
| Presupuesto de iteraciones | **FUERA DE SERVICIO (R2.1) en A**: el instrumento pide el transcript y su acceso no está disponible; se declara **corte documental** y auto-reporte con su unidad, sin sumarlo al instrumento | Todas |
| **FASE-E2E: sello de regresión y denominadores** | Regresión completa **1 failed / 5.134 passed / 41 skipped / 4 xfailed en 392,32 s (EXIT 1)**, crudo con su `EXIT=` dentro del comando; el único rojo es el ajeno y dependiente del orden del piloto JEV, que **pasa 15/15 aislado**. **Reconciliación medida con el método canónico** (`grep -rE "^\s*def test_" tests --include=*.py`): **5.040 en `1c20695` → 5.045 en `d571277` → 5.049 en `6fd39c2` y en el árbol**, o sea **+9 funciones** desde H y no +12: b1 aportó 5 funciones / 8 casos (un `parametrize` suma 3) y b1-bis 4 funciones / 4 casos. Las baterías de H son **67 funciones / 70 casos**, así que el «70 passed» citado es **conteo de casos** | FASE-E2E |
| **FASE-E2E: corrida única consumida** | **1 de 1**, el 2026-10-07 a las 14:32:13Z. `run_control.json`: `attempts: 1`, `estado: FINALIZADO`, `exit_code: 0`, `pid: 30576`, 116 s, argv literal de 11 piezas con `--permission-mode auto` y `argv_sha256 b5748891…`. Un solo `--spawn`, sin lanzamiento manual del argv y sin segunda corrida | FASE-E2E |
| **FASE-E2E: coherencia, veredicto y ZIP observados** | Coherencia **0.9172**; veredicto **`APROBADO-CONDICIONAL-PENDING-ONBOARDING`** con tier **B+** y `first_floor_rule` aplicado (evidence_tier B+ capado a condicional); **13 gates = 11 PASSED + 2 WARNING, 0 fallidos, 0 bloqueantes**; `readiness: READY_FOR_PUBLICATION`; **ZIP publicado** `hotel_don_alfonso_20261007.zip`, 70.191 bytes, sha `487f5800…`, **57 entradas**, `package_evidence.suppressed: false`. Diferencia de fondo contra el baseline: allí READY convivió con supresión; aquí convive con entrega | FASE-E2E |
| **FASE-E2E: AC20 en flujo real** | Los tres puntos sobre artefactos vivos: `critical_recall` con `value: 1.0` **y** `details` fundado (`critical_issues_count: 3`, `recall_basis: all_critical_issues_detected`); `reviewer_reports[].findings` con causas (0 critical); `package_evidence` en la rama publish con hash y conteo. El par del contrafactual de FASE-0 se observó tal cual | FASE-E2E (confirma FASE-0) |
| **FASE-E2E: lo que NO se ejercitó** | **Medición IAO del `LLMMentionChecker`: NO EJERCITADO** — la unidad cae con un `AttributeError` dentro de `def _parse_mentions`, porque `def check_mentions` toma `result["text"]` sin guarda de None y la rama devolvió nulo; por eso el `audit_report` de hoy **no lleva** `providers_used`, a diferencia del del baseline. **Rama WhatsApp: NO EJERCITADA**, predicho por el maestro y observado (`[RC1] whatsapp_button: ninguna brecha candidata`). **Proveedor de LLM por unidad: no acreditable** — el campo es agregado de una sola unidad, nunca por revisor (premisa falsa del prompt, S-E2E-2) | FASE-E2E → VERIFY |
| **FASE-E2E: tests, quick y derivados** | **0 funciones de test nuevas** (la fase no edita producto ni tests); quick **13/13** antes del spawn y **13/13** al cerrar, con las baterías de H en **70 passed** tras la re-emisión del preflight — **re-ejecutadas después del spawn dieron 2 failed / 68 passed**: dos guardas asertaban que el control productivo no existía y el consumo legítimo del intento las venció. **Re-ancladas con autorización del operador a revisión fija + caracterización, 70 passed de nuevo, con dientes medidos (5/5 mutantes atrapados)**. El quick **no ejecuta pytest**, así que no veía esos dos rojos. Commit, L3 y push **en la orden literal del operador del 2026-10-07**, con `captura_stdout.txt` excluido del versionado y el sha al sello de RELEASE. **Sin tag, QMind ni `DOMAIN_PRIMER`** | FASE-E2E |
| Presupuesto de iteraciones | **FUERA DE SERVICIO (R2.1) también en E2E**: el instrumento pide el transcript y su acceso no estuvo disponible. Auto-reporte con unidad propia: 1 spawn, 1 re-emisión de preflight, 2 quicks, 1 batería de H, 1 sonda de conectividad, 7 artefactos de evidencia. El corte de esta fase es **documental**, no de código, y la ausencia de commit no es un corte «no consumado» | FASE-E2E |

## Sección E: Archivos afiliados actualizados

| Archivo | Cambio | Fase |
|---|---|---|
| Directorio de este plan | Diseño y prompts; sin implementación | Preparación |
| **Revisión 2 (2026-09-19): archivos del plan tocados** | `README.md`, `01-plan-maestro.md` (§1, §2, §3, §4, §5, §6, §7), `04-contrato-ejecucion.md` (límite de lectura de corridas ajenas), `00-lecciones-capitalizadas.md` (§1bis nuevo, Q7-Q10, siete filas en §2, §3bis, §4), `06-checklist-implementacion.md`, `dependencias-fases.md`, `09`, `10-analisis`, `05-…-fase-VERIFY` corregidos; **nuevo** `05-prompt-inicio-sesion-fase-0.md`; A/B/C/G/H/E2E actualizados al nuevo orden. **Sin cambios de código, tests, VERSION ni evidencia** | Revisión 2 |
| `.opencode/LECCIONES-INDEX.md` y `.opencode/lecciones_index.json` | Regenerados tras la revisión 2 (316 IDs), al cerrar G (318) y el 2026-09-20 con el write-back (319); cada fase vuelve a regenerarlos al cerrar | Revisión 2 / G / write-back |
| CHANGELOG.md / docs/GUIA_TECNICA.md / docs/contributing/REGISTRY.md | Cada fase registra su propio trabajo; no modificados en preparación ni en la revisión 2 | Pendiente |
| **FASE-0 (2026-09-20): archivos afiliados tocados** | Producto: `modules/quality_gates/publication_gates.py`, `modules/quality_gates/tribunal/outcome.py`, `main.py`. Tests: nuevo `tests/test_fase_0_ac20_evidencia_veredicto.py`; re-atados a coherencia interna `tests/quality_gates/tribunal/test_p2_veredicto_enriquecido.py` (asertaba la forma exacta de `reviewer_reports`) y corregido el fixture contradictorio `tests/quality_gates/tribunal/test_diagnosis_reviewer.py`. Evidencia: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-0/` (12 archivos: 4 instrumentos reejecutables —`pre_camino_gate.py`, `contrafactual_ac20.py`, `run_mutations.py`, `build_thresholds.py`—, 4 salidas medidas en JSON, 3 registros de tests y 1 informe). Documental: `CHANGELOG.md`, `docs/GUIA_TECNICA.md`, `docs/contributing/REGISTRY.md` (por `log_phase_completion.py`), el par del indice regenerado (319 → 320 IDs) y los siete documentos del plan (§00, §05 de la fase, §06, §09, §10, README y dependencias). La autorización de commit no se pidió durante la fase; **commit `7c6e75f` y push a `origin/master` ejecutados el mismo 2026-09-20 con instrucción literal del operador** (paridad 0/0 verificada con `git ls-remote`; los 7 checks del pre-commit pasaron sin saltar ninguno) — incluyendo índice, registro y documentos del plan | FASE-0 |
| **FASE-G (2026-09-20): archivos afiliados tocados** | `CHANGELOG.md` (subsección G bajo 4.77.3, sin anticipar versión), `docs/GUIA_TECNICA.md` (nota técnica G), `docs/contributing/REGISTRY.md` (registro por `log_phase_completion.py`), `.opencode/LECCIONES-INDEX.md` + `.opencode/lecciones_index.json` (regenerados al cerrar), `.opencode/wiring_report.json` (nuevo artefacto del AC7), y `DOMAIN_PRIMER.md` regenerado **solo por su writer** (`doctor.py --regenerate-domain-primer`), que por ser archivo versionado ensucia el árbol | FASE-G |

| **FASE-B (2026-09-20): archivos afiliados tocados** | Producto: 11 archivos de `modules/` + `main.py` (solo comentario) — detalle en la sección "Cierre incremental de FASE-B" de este documento. Tests: nuevo `tests/commercial_documents/test_fase_b_promesa_whatsapp.py` (12 funciones canónicas) y re-vinculaciones en 8 archivos, todas por cambio de forma o de ejemplo, ninguna aflojando una expectativa. Evidencia: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-B/` (9 artefactos, incluidos `run_mutations.py` reejecutable, `mutation_report.json` **8/8 (M1–M8)**, `A4-decision.md`, los cuatro registros de tests y el `CHECKPOINT-autorizaciones-pendientes.md`). Documental: `CHANGELOG.md` (subsección B bajo 4.77.3, sin anticipar versión), `docs/GUIA_TECNICA.md` (nota técnica del patrón resolución ≠ conteo), `docs/contributing/REGISTRY.md` (por `log_phase_completion.py`), el par del índice regenerado y los cinco documentos del plan (§00, §05 de la fase, §06, §09, dependencias). **Commit `473ed0f` ejecutado el 2026-09-20 con instrucción literal del operador** (42 archivos,
+1.907/−266; los 7 checks del pre-commit pasaron sin saltar ninguno) más el commit de A4
(test re-anclado + registro documental); **push a `origin/master` ejecutado el 2026-09-20 con instrucción literal del operador (`cf3ddc2..05d0cc6`; paridad 0/0 verificada con `git ls-remote`)** | FASE-B |
| **FASE-C (2026-10-06): archivos afiliados tocados** | Producto: 8 archivos — `modules/data_validation/whatsapp_contract.py` (**nuevo**), `site_presence_checker.py`, `site_presence_adapter.py`, `conditional_generator.py`, `v4_asset_orchestrator.py`, `coherence_validator.py`, `v4_comprehensive.py`, `main.py` (solo el centinela). Tests: 6 — `tests/asset_generation/test_fase_c_boton_seguro.py` (**nuevo**, 24 funciones canónicas) y nueve re-anclajes en `test_site_presence_adapter.py`, `test_whatsapp_button.py`, `test_conditional_generator.py`, `test_never_block_architecture/test_phase5_integration.py` y `test_datasource_gap.py`, cada uno con su justificación escrita dentro del test. Evidencia: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-C/` (8 artefactos: informe, selección, PRE/POST, quick PRE, regresión, `run_mutations.py`+`mutation_report.json` 9/9 con sha256, `build_thresholds.py`+`thresholds.json`). Documental: `CHANGELOG.md` (subsección C bajo `## [Sin publicar]`, sin anticipar versión), `docs/GUIA_TECNICA.md`, `docs/contributing/REGISTRY.md` (por `log_phase_completion.py`), el par del índice regenerado, los packs (`build_phase_briefing.py --plan`), el baseline de citas (`validate_plan_citations.py --update-baseline`, acto visible) y los cinco documentos del plan (§00, §05 de la fase, §06, §09, §10, dependencias). **Sin commit ni push: el mandato no los autorizó** — los cinco cortes se sostienen sin ellos | FASE-C |

| **FASE-D (2026-10-06): archivos afiliados tocados** | Producto: 6 archivos — `main.py` (tres funciones nuevas y el pre-gate/FASE 4 re-escritos), `modules/assessment_builder.py`, `modules/quality_gates/publication_gates.py`, `modules/commercial_documents/coherence_validator.py`, `modules/asset_generation/v4_asset_orchestrator.py`, `modules/data_validation/whatsapp_contract.py` (solo `READ_ABSENT`). Tests: 1 archivo nuevo — `tests/quality_gates/test_fase_d_veredicto_canonico.py` (33 funciones canónicas); **0 re-anclajes**: las 241 pruebas del PRE siguieron verdes sin tocar ninguna expectativa. Evidencia: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-D/` (informe, selección, PRE/POST, regresión, `run_mutations.py` + `mutation_report.json` + crudo 6/6 con sha256, `build_evidencia_pre_gate.py` con los tres artefactos escritos por los writers reales + `resumen_escritura.json`, quick PRE y final). Documental: `CHANGELOG.md` (subsección D bajo `## [Sin publicar]`, sin anticipar versión), `docs/GUIA_TECNICA.md`, `docs/contributing/REGISTRY.md` (por `log_phase_completion.py`), los cinco documentos del plan (§00, §05 de la fase, §06, §09, §10, dependencias) y los derivados regenerados con sus writers. **Commiteada y empujada por orden literal del operador al cerrar la sesión; el sha y el rango van en el sello documental de RELEASE** | FASE-D |

## Registro documental por fase

Cada cierre anota: archivos exactos, tests añadidos, PRE/POST con misma unidad, resultados de mutaciones, limitaciones, estado real y autorización de commit si existe. No elevar versión en fases intermedias. Registrar con `scripts/log_phase_completion.py --check-manual-docs` solo la fase que acaba de completarse.

## Cierre incremental de FASE-B (2026-09-20)

**Archivos exactos de producto (12):** `modules/asset_generation/v4_asset_orchestrator.py`,
`pain_ledger.py`, `asset_catalog.py`, `conditional_generator.py`,
`whatsapp_conflict_guide.py`, `whatsapp_setup_guide.py` (nuevo),
`modules/commercial_documents/pain_solution_mapper.py`, `v4_diagnostic_generator.py`,
`modules/common/service_identity.py`, `modules/asset_generation/proposal_asset_alignment.py`
(A1 autorizado en la misma sesión), `scripts/validate_wiring.py`, `main.py` (solo el
comentario `FIX-D7`).

**Tests:** nuevos `tests/commercial_documents/test_fase_b_promesa_whatsapp.py` con 12
funciones canónicas; re-vinculaciones en 8 archivos existentes (forma o ejemplo, nunca
expectativa aflojada). Mismo unidad PRE/POST: selección literal de 25 archivos,
537 → 539 (delta +2 explicado) → 552 con la suite nueva. Regresión completa tras B: 4 failed /
4.261 passed, tres rojos preexistentes con dueño y **uno de B con causa medida**
(`test_get_blocking_issues`, gate de alignment con servicio condicional) — **cerrado por A4
en la misma sesión**. Regresión tras A4: **3 failed / 4.263 passed / 41 skipped / 4 xfailed**
en 196,5 s, con los tres rojos idénticos a los de la evidencia de FASE-0. A4 medido con la
selección extendida (las mismas 25 + `test_publication_gates.py`) y el mismo instrumento:
PRE sobre `473ed0f` en `git worktree --detach` = 1 failed / 619 passed / 1 skipped; POST =
0 failed / 621 passed / 1 skipped. Canónicas 4.299 → **4.300**. Quick **11/11** re-medido al
cerrar A4, `validate_document_integration.py` en verde y `build_lesson_index.py --check`
regenerado (320 IDs, fresco).

**Mutaciones:** 8/8 (M1–M8) rojos causados por el guard; restauración por sha256 (tras corregir
el falso negativo de `write_text()` en Windows, que convertía los archivos a CRLF).

**Limitaciones declaradas:** (i) el servicio de preparación queda fuera del universo
contado, así que el gate de alignment no lo ve como deuda cuando es el único
comprometido — **A4 decidido con O5**: el punto ciego queda assertionado en
`test_deuda_ac5_ledger_solo_condicional_pasa_trivial` y su gobernanza es **AC5, dueño C-D**
(`A4-decision.md`); (ii) `run_v4_complete_mode` sigue registrando el centinela
`detected_via_html` en el `ValidationSummary` con `can_use_in_assets=True` (fuera de la
allowlist de B; dueño C/AC6); (iii) `wa_button_gen` conserva su número de placeholder y
`local_content_generator` construye dos `wa.me/` sin guarda (C/D); (iv) umbrales de
WhatsApp (0.9 coherencia / 0.7 catálogo / 0.3 hotel nuevo / 0.5 conflicto) quedan
inventariados pero sin gobernar: AC5 es de C/D.

**Estado real:** B **CERRADA CON DEUDA REGISTRADA (AC5 → C-D)**. **Commit `473ed0f`
ejecutado con autorización del operador** (42 archivos, +1.907/−266, 7/7 checks del
pre-commit sin saltar ninguno) y commit de A4 con `tests/quality_gates/test_publication_gates.py`
más su registro documental; **push a `origin/master` ejecutado el 2026-09-20 con instrucción literal del operador (`cf3ddc2..05d0cc6`; paridad 0/0 verificada con `git ls-remote`)**. Tras A4 la regresión completa
es **3 failed / 4.263 passed / 41 skipped / 4 xfailed** y los 3 rojos son los mismos que ya
estaban en la evidencia de FASE-0 — ninguno atribuible a B. Contador v4complete 0/1. R2
FUERA DE SERVICIO (R2.1).

## Rojo documental del PRE, cerrado por re-medición

`run_all_validations.py --quick` dio 9/10 el 2026-09-18 y **10/10** al re-medirlo el 2026-09-19. La causa medida del rojo: `AGENTS.md`, `VERSION.yaml`, `docs/GUIA_TECNICA.md` y `REGISTRY.md` estaban modificados en el árbol y hoy son idénticos a HEAD tras una reversión ajena a esta sesión. Se retracta la explicación previa por cuatro segmentos: `_check_version_sync` solo ejecuta `sync_versions.py --check`. Regla conservada: re-medir el quick al abrir cada fase y no modificar hooks, baselines de citas ni configuración para forzar un verde.

## Cierre incremental de FASE-E (2026-10-06)

**Que se cerro.** Un resolvedor unico de insumos (`modules/quality_gates/tribunal/review_inputs.py`) con
copia interna **no exportable** antes del borrado del gate, y sus cinco consumidores: los cuatro Bots del
Tribunal y el Juez. El vocabulario `read_status` gano `NO_LEIDO` en `whatsapp_contract.py`, que es donde
FASE-C lo designo; `artifact_paths.resolve_latest` acepta la ruta `explicit` del run y **no** cae al
ascendiente compartido entre hoteles cuando esa ruta esta declarada y no existe.

**Metricas de la fase (medidas, no previstas).**

| Concepto | Valor |
|---|---|
| Funciones de test nuevas | 31 en `tests/quality_gates/tribunal/test_fase_e_snapshot_resolvedor.py` |
| Canonicas | 4.908 en HEAD -> 4.939 en el arbol (+31) |
| PRE / POST (misma seleccion) | 290 passed + 9 skipped / 321 passed + 9 skipped, ambos EXIT 0 |
| Mutantes | 8/8 caen por la asercion de su guard; 8/8 restaurados por sha256 |
| Quick | 12/13 con rojo de derivado (Wiring) y 13/13 tras regenerar con su writer |
| Archivos tocados | 9 modificados + 2 nuevos de producto/tests, mas la evidencia |
| Contador v4complete | 0/1 |

**Deuda que deja E (con dueno, en `resultados-y-observaciones.md` §7):** el resolvedor no ancla todavia los
JSON timestamped (`pain_ledger`, `gate_report_*`, `delivery_quality_report`, `proposal_asset_matrix`,
`financial_scenarios`), que siguen con glob local del directorio del hotel; `REVIEW_INPUT_ABSENT` es INFO
por decision escrita; y el fallback `legacy-ancestor-walk` sigue vivo donde no hay manifiesto, declarado en
el reporte en vez de silencioso.

## Cierre incremental de FASE-F (2026-10-06)

**Que se cerro.** Sumidero unico de redaccion nuevo (`modules/utils/redaction.py`): define una sola vez las
formas de credencial, los params `key=`, las cabeceras `x-goog-api-key`/`api-key`/`authorization` y los tokens
`Bearer`, redacta **antes** de consola y de disco, y recorta **despues** de redactar. Nueve rutas de salida
quedan calificadas o cerradas sobre el: `LLMMentionChecker._sanitize_text`/`_sanitize_error` y la rama de
agotamiento de `_query_gemini` (AC13 nombra los tres simbolos), `HttpClient._sanitize_error`,
`HttpClient._log_ssl_bypass` y `fallback_info['error']`, `SSLLogger._sanitize_for_log` (la unica escritura real
bajo `logs/`, ruta que ningun check leia), `PageSpeedClient._make_request` (la key viaja en los params), tres
ramas de `GooglePlacesClient`, el artefacto nuevo de D `coherence_pre_gate_<ts>.json` bajo `output/` y el print
nuevo de E en la rama `never-block`. `ValidationRunner._check_no_secrets` ahora lee `output/` y `logs/`, caza
`sk-or-`/`sk-ant-` y su rama de >5 MB dej6 de reventar en NameError. No se reimplement6 ningun provider, no se
cambi6 autenticacion, modelos, configuracion central ni politica de reintentos, y no se roto nada.

**Metricas de la fase (medidas, no previstas).**

| Concepto | Valor |
|---|---|
| Funciones de test nuevas | 40 en `tests/utils/test_fase_f_sumidero_redaccion.py` (47 casos con parametrizacion) + 1 en AC-S1 = 41 |
| Canonicas | 4.939 en HEAD -> **4.980** en el arbol (+41) |
| PRE / POST (misma seleccion de 6 rutas) | 372 passed + 10 skipped / 373 passed + 10 skipped, ambos EXIT 0; POST extendido 419 passed + 10 skipped |
| Mutantes | 9/9 caen por fuga detectada; 9/9 restaurados por sha256; 9/9 verdes tras restaurar |
| Re-anclajes | 1 asercion de AC-S1 (`test_none_keys_is_noop` pineaba la noop de `_sanitize_text`) y 2 literales de fixture re-anclados por concatenacion |
| Medicion antes de activar la pata nueva del verificador | 1.041 archivos bajo `output/` y `logs/`, 0 hallazgos (el rojo no se heredo del historial) |
| Quick y REGISTRY | quick final 13/13 con EXIT 0 sobre el arbol definitivo (`quick_final.txt`); REGISTRY sin GAP por el propio escritor; el denominador lo imprime la corrida y no se copia aqui |
| Sello de regresion completa | **1 failed / 5.064 passed / 41 skipped / 4 xfailed en 390,64 s (EXIT 1)** sobre el arbol definitivo. El unico rojo es ajeno y orden-dependiente: `jev_pilot/test_jev_pilot_deepseek_brazo.py`, que en su archivo aislado pasa 15/15 (el mismo rojo que declararon C y D). Existio una primera corrida (1 failed / 5.062 passed) declarada **vencida por edicion propia** a mitad de la fase: ver `regresion_1_vencida_por_edicion_propia.txt` |
| Contador v4complete | 0/1 (AC13 verificado offline, con transporte sustituido) |
| Archivos tocados | **39 medidos** con `git status --porcelain` (excluyendo `briefing/`, que por decision del plan no se versiona): 23 modificados (9 de producto, 1 de tests, 8 de docs del plan, CHANGELOG, GUIA_TECNICA y 4 derivados regenerados por su escritor) + 2 nuevos de producto/tests + 14 de evidencia. El registro publico `--archivos-mod 32` porque el escritor corrio a mitad del cierre y no tiene bandera de correccion: la errata va en el sello de RELEASE (S-F7, mismo caso que C) |

**Revocacion: no es un resultado de test.** `credential_status.json` registra la rotacion de 2026-09-18 como
**afirmacion del operador** con su referencia no secreta (`evidence/FASE-P5/AC-S3-S4-inventario-superficie.md`)
y deja el resto de proveedores en `PENDIENTE-SIN-EVIDENCIA-OPERATIVA` con dueño. La redaccion perfecta no retira
acceso a una credencial filtrada: esa es la pata que AC13 no deja certificar por esta fase.

**Deuda que deja F (con dueño, en `10-analisis-post-implementacion.md` §Seguimientos abiertos por F).** S-F1
`scripts/preload_prospects_gbp.py` persiste `PlaceData.error_message` (fuera de allowlist); S-F2
`_query_perplexity` sin `try/except` propio ni diente de consola; S-F3 el escaneo nuevo cubre el instante de la
validacion, no un watch; S-F4 la allowlist de cuarentena de P5 queda intacta. Y una separacion que sigue
vigente: la integracion con captura/snapshot del runner es prueba de **H**. ⟦**Cerrada por H el 2026-10-06**: la
boca de captura del runner (`run_once.redactar_salida`) llama `redact_secrets` y `assert_redacted` del contrato de
F antes de escribir o mostrar, y `preflight.json` pasa el mismo guard. S-F5 y S-F8 quedan cerradas; S-F6
(revocación) y S-F7 (errata de registro) siguen con su dueño⟧.

## Cierre incremental de FASE-H (2026-10-06)

**Qué se cerró.** El onboarding de la corrida se derivó con el transformador real del repo
(`main._observation_to_onboarding_format`), cambiando **una sola** clave del resultado (`hotel.url`, atribuida al
operador en `onboarding_provenance.json`) y declarando el resto con productor por campo. Se recorrió el flujo
productivo **offline** —parser, puerta de permisos, loader, frescura, pre-gate de D, lector AC9 de D sobre el
baseline real, resolvedor de E y snapshot previo de `.agent/memory`— con la red cortada y con prueba de que el
corte tiene diente. Y se implementó el runner stdlib previsto:
`evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-H/run_once.py`, con reserva por creación exclusiva antes del
spawn, máquina de estados terminales, vigilancia del PID sin relanzamiento, captura redactada por el sumidero
calificado en F y preservación de evidencia con hash. **0 archivos de producto modificados**: el allowlist de H
acota el código nuevo al runner. Nada de la fase ejecutó `main.py v4complete` y el control productivo de FASE-E2E
no se creó (lo assertiona un test de la batería).

**El veredicto del preflight es NO FAVORABLE, y ese es el resultado de la fase.** 12 requisitos favorables y 1 en
contra (`consentimiento_datado_sobre_la_url_viva`), un acto que FASE-A reservó al operador. Consecuencia
gobernable: `run_once.py --spawn` se niega **antes** de reservar, la arista a E2E queda cerrada y el contador
sigue en **0/1**.

**Métricas de la fase (medidas, no previstas).** Canónicas **4.982 → 5.040 (+58)** en dos baterías nuevas
(`tests/test_fase_h_intento_unico.py` 30 y `tests/test_fase_h_onboarding_procedencia.py` 28). PRE S1 (10 rutas
literales) **367 passed / EXIT 0** → POST S1 **367 passed / EXIT 0 (delta 0)**; POST extendido **425 / EXIT 0**.
S2 (`tests/e2e`) medida aparte por la contaminación de `selenium` de su conftest: 17 passed / 4 skipped / EXIT 0
idéntica en PRE y POST. **13/13 mutantes rojos por su guard con la causa impresa, 13/13 restaurados por sha256,
0 por import o sintaxis.** Rama del loader `YAML_DE_DIR_CLIENTES`, medida dos veces y decidida por contenido.
Edad del dato **76 días** con `ONBOARDING_FRESHNESS_HOURS` ausente (medido por presencia, nunca por valor).
Snapshot previo: 21 archivos de `.agent/memory` con sha256 y **8 de 10** sesiones que el spawn borraría.
Quick de apertura **13/13 / EXIT 0** y quick de cierre **13/13 / EXIT 0** (`quick_final.txt`).
**Sello de regresión completa: 1 failed / 5.122 passed / 41 skipped / 4 xfailed en 359,83 s (EXIT 1)** sobre el
árbol definitivo; el único rojo es el ajeno del piloto JEV, que pasa 15/15 en su archivo aislado y 141/141 en su
directorio. Cuatro corridas anteriores quedaron desechadas (dos por superponerse entre sí, dos vencidas por ediciones
documentales de la propia fase) y se archivan en
`evidence/…/FASE-H/descartados_por_superposicion_de_corridas/` con su número real: no se reutilizan como verde
y las cuatro devuelven el mismo conteo, 1 failed / 5.122 passed, con el mismo rojo ajeno.

**Rectificaciones medidas por H** (detalle en `evidence/…/FASE-H/resultados-y-observaciones.md` §1 y en la fila H
de `10-analisis`): el `hotel_id` del reporte lo produce `OnboardingController.generate_hotel_id`, no
`"hotel_id": args.url`; y el análisis previo, medido por AST, solo se imprime en `run_v4_complete_mode` — la
reutilización vive en `run_execution_mode`. Ninguna exigencia del preflight se retiró: se re-anccló a la razón
medida, y se abrió **S-H7** porque lo que devuelve el índice de sesiones es un **directorio**.

**Archivos afiliados tocados por H.** Producto: ninguno. Tests: 2 archivos nuevos. Evidencia: 16 artefactos bajo
`evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-H/` (runner, derivación, recorrido offline + JSON, procedencia,
preflight, informe, selección, 5 crudos de pytest, arnés de mutaciones + JSON + crudo). Docs del plan: `00`
(§Aplicación efectiva H + `L-H-RES` y `L-H-ARGV`), `05-prompt-inicio-sesion-fase-H.md` (estado, dos premisas
rectificadas y los casilleros del presupuesto), `06-checklist-implementacion.md` (cabecera, fila H, filas
AC9/AC12/AC13/AC14/AC15/AC17 y cuatro casilleros de prerrequisitos/controles), `dependencias-fases.md` (filas F,
H y E2E + cierre documental), `09` y `10` (secciones y fila de la fase), `CHANGELOG.md` bajo `## [Sin publicar]`
y `docs/GUIA_TECNICA.md`. Derivados regenerados con su escritor al cerrar: packs, índice de lecciones + `--check`,
referencias, citas y `wiring_report.json`.

## Cierre incremental de FASE-E2E (2026-10-07)

**La fase se abrió con un bloqueo medido y se cerró con la corrida hecha.** Antes del spawn, el check libre
`run_once.py --preflight` fallaba con `DivergenciaDeHash` en **el propio runner**: el preflight había congelado el
blob de `run_once.py` en `d571277` (`ff114aff…`) y el commit `6fd39c2` (b1-bis) enmendó ese mismo archivo
(`1efa6cd1…`). Como `ARCHIVOS_CONGELADOS` incluye al runner, **editar el instrumento vence su propio preflight**. El
rechazo caía antes de `reservar`, así que el intento sobrevivió; la cura fue preservar el crudo versionado
(`preflight_2026-10-07_emision_b1_hash_vencido.json`, sha `a0947be1…` idéntico en disco y en el blob de HEAD) y
re-emitir con `--emitir-preflight`. **Medición de la re-emisión: se movieron exactamente 2 campos** — `emitido_el` y
el hash del runner; argv, identidades, snapshot, los otros 9 hashes y las pruebas de cero lanzamiento quedaron
idénticos. Después: `--preflight` EXIT 0, baterías de H 70 passed, quick 13/13.

**Sonda de red con hallazgo sobre el propio instrumento.** La resolución DNS local del host destino es inestable: al
re-medir, **0/5 fetches** resolvieron, y sin embargo la corrida obtuvo datos reales de la página. Dos correcciones
que se hicieron en camino: una primera sonda usó `pagespeed.googleapis.com`, que no es el host del producto
(`PageSpeedClient.__init__` usa `www.googleapis.com/pagespeedonline/v5/runPagespeed`, vivo), y se reportó mal el recuento
de la tanda de la sonda («200 dos veces» cuando la medición sostenible es un 200 observado y una re-medición 0/5).
**Se retracta y se re-emplace en la evidencia.**

**Resultado observado: la meta de entrega se alcanzó.** Ver §1 a §6 de
`evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-E2E/resultados-y-observaciones.md`. Lo que interesa al acumulado:
`APROBADO-CONDICIONAL-PENDING-ONBOARDING` con tier B+, 11 PASSED + 2 WARNING y 0 fallidos, y **ZIP publicado con 57
entradas**. AC20, que FASE-0 había cerrado offline sobre el acta archivada, se ejercitó en el flujo real en sus tres
puntos; el `VACUOUS_RECALL` que suprimió el baseline no reapareció.

**Deuda abierta por la corrida, con dueño (S-E2E-1 a S-E2E-10 en el informe).** La más cara: el `LLMMentionChecker`
cayó y se llevó consigo la medición IAO del único intento permitido. Le siguen el `finding_type` que se pierde al
proyectar el acta (el revisor escribe `type`), un ZIP publicado sobre un revisor que pedía `DEVOLVER-PRUEBAS`,
`preflight.sha256` nulo en el control, y **material de credencial enmascarado en `captura_stdout.txt`** impreso por
`config_checker._check_env_variables` que el sumidero de F no reconoce — esa captura no debe comitearse sin decisión del operador.
Y la deuda heredada que la corrida **materializó**: las 8 sesiones de `.agent/memory/sessions/` que el snapshot
anunciaba se borraron; el inventario con sha256 prueba que existieron, `.gitignore:38` impide restaurarlas.

**Archivos afiliados tocados por E2E.** Producto: **ninguno** (la fase no diseña ni repara). Tests: **ninguno**.
Evidencia: 7 artefactos bajo `evidence/…/FASE-E2E/` (informe, preflight verificado, `run_control.json`, inventario
post-corrida, dos capturas redactadas y crudo del spawn) más `FASE-H/preflight.json` re-emitido y su crudo preservado.
Docs del plan: `05-prompt-inicio-sesion-fase-E2E.md` (estado y los seis casilleros), `06-checklist-implementacion.md`
(fila E2E, filas AC12/AC17/AC20 y cuatro casilleros de controles), `dependencias-fases.md` (fila E2E), `09` (Sección D
y esta sección) y `10` (fila de la fase). Sin write-back a QMind, sin `DOMAIN_PRIMER`, sin tag.

## Cierre incremental de FASE-VERIFY (2026-10-07)

**Qué hizo la fase:** certificación transversal de **AC1–AC20** (AC19 en sus dos mitades) sobre la evidencia preservada,
en ejecución **directa y sin delegación**, sin código, sin tests, sin `v4complete` y sin remediación (L-V.4).

| Métrica de VERIFY | Valor | Cómo se midió |
|---|---|---|
| ACs dictaminados | 20 (AC19a y AC19b por separado) | matriz en `evidence/…/FASE-VERIFY/certificacion.json` |
| Con pata E2E superada | 7 (AC9, AC11, AC12, AC15, AC17, AC19a, AC20) | artefacto de la corrida citado por símbolo/ruta |
| Offline superado | 9 (AC1, AC2, AC3, AC4, AC7, AC8, AC13, AC14, AC16) + 1 parcial (AC5) | mutantes restaurados por sha256 en cada fase |
| **FALLA** | **2 (AC6, AC10)** | `wa.me` fabricado desde `gbp.phone` en el ZIP y `IMPLEMENTATION_ORDER` con secciones vacías |
| NO EJERCITADO | 1 (AC19b) | diferido a maestro §6 con dueño |
| Integridad del intento único | 10/10 `source_hashes` casan; `argv_sha256` recomputado casa; `attempts=1`, PID 30576, exit 0, 116 s | `sha256sum` + `run_once.argv_sha256` |
| Paquete entregado | sha `487f5800…`, 70.191 bytes, 57 miembros, `testzip() → None`, 0 `.zip.tmp`, sin snapshot interno ni documentos retenidos | `zipfile` sobre el miembro y coteje bilateral con `MANIFEST.json` |
| Evidencia del plan | **153 rutas en disco, 150 versionadas** (3 = `captura_stdout.txt` + 2 `.pyc`); **0 ABSENT, 0 READ_ERROR** | `find … \| wc -l` y `git ls-files … \| wc -l` |
| Hallazgos nuevos | 8 (V-1…V-8), **todos con dueño y disparador, ninguno cerrado aquí** | `certificacion.json .hallazgos_nuevos` |
| Lecciones nuevas | **Ninguna de producto**; dos confirmaciones medidas (L-T4A.5 en AC10, L-VUP-17 en la matriz) y una de proceso ya registrada | sin cuota (contrato §2) |

**Contratos que VERIFY no ejecutó y por qué no son verde:** revocación de credenciales (S-F6, solo afirmación del
operador), AC1/AC2/AC3/AC6 en la rama WhatsApp (el hotel no produce el pain), AC19b (diferido), medición IAO (perdida
con el `LLMMentionChecker` caído en el único intento).

**Docs tocados por esta fase:** `evidence/…/FASE-VERIFY/certificacion.json` y su `resultados-y-observaciones.md` (nuevos);
`05-prompt-inicio-sesion-fase-VERIFY.md` (estado), `06-checklist-implementacion.md` (fila VERIFY, fila RELEASE y
cabecera), `dependencias-fases.md` (filas VERIFY y RELEASE), `README.md` (índice), `10-analisis-post-implementacion.md`
(matriz dictaminada, comparación con baseline, sección de la fase y once filas de seguimientos),
`00-lecciones-capitalizadas.md` (aplicación efectiva), `CHANGELOG.md` (subsección bajo `## [Sin publicar]`) y
`docs/GUIA_TECNICA.md` (nota técnica).

**R2:** `measure_iterations.py` sigue **FUERA DE SERVICIO (R2.1)** — pide el transcript del cliente y su acceso está
denegado. Auto-reporte con unidad declarada (invocaciones de herramienta de esta sesión): **≈90**, recuento propio y
no medición por instrumento del plan; por encima de la referencia de 60 del prompt se declara el exceso como checkpoint y **no** se partió la
fase ni se delegó nada (executor §4.6: FASE-VERIFY no delegable).

**Sin commit, push, tag, QMind write-back ni `DOMAIN_PRIMER`** — no autorizados. `DOMAIN_PRIMER` acumula checkpoint
desde FASE-C (C, D, E, F, H, E2E y VERIFY). RELEASE es sesión y autorización separadas, y **no puede declararse éxito
integral** mientras AC6 y AC10 consten en FALLA (maestro §4, condición de honestidad).

## Cierre incremental de FASE-RELEASE (2026-10-07) — release **4.79.0**, write-back y archivado

**Qué hizo la fase:** cierre documental y versionado del plan. Sin `v4complete` (contador **1/1** intacto), sin código
de producto y sin rehacer VERIFY. Los permisos se resolvieron con el operador antes de ejecutarlos: bump con
propagación a configuración central, regeneración de DOMAIN_PRIMER, **dos commits separados**, write-back y push con
L3 previa. **Tag: no autorizado**, declarado como opción rechazada.

| Métrica de FASE-RELEASE | Valor | Cómo se midió |
|---|---|---|
| Versión autorizada | **4.79.0** · codename *WhatsApp verificado, orden real y entrega única de Don Alfonso* · 2026-10-07 | mandato de la sesión con el operador; base medida al abrir: 4.78.0/2026-09-25 en `VERSION.yaml` |
| Archivos gobernados por el sync | 5 (`README.md`, `AGENTS.md`, `.cursorrules`, `docs/CONTRIBUTING.md`, `docs/GUIA_TECNICA.md`) | `sync_versions.py` en modo escritura + `version_consistency_checker.py` (TODO SINCRONIZADO); el diff de esos archivos es **solo** el sello de versión y fecha |
| DOMAIN_PRIMER | **verificado** y **regenerado con su writer** (7/7 líneas del sello) | `doctor.py --regenerate-domain-primer`, luego `--context` (5 PASS) y `--status` (`SYSTEM_STATUS.md` regenerado) |
| Rojo propio de la fase | `[6/13] Document Integration` tras el bump | no se heredó ni se absorbió: se curó con el writer, con instrucción expresa, y se re-midió |
| CHANGELOG | 7 bloques del plan re-encabezados bajo `## [4.79.0]` + 2 subsecciones nuevas (recuperación y RELEASE); **0** bloques de otros planes tocados | transformación con `temp/release-2026-10-07/reordena_changelog.py`, con `assert` de unicidad por encabezado; numstat 205/12 |
| GUIA_TECNICA | 2 notas nuevas: recuperación AC6/AC10 y FASE-RELEASE | las siete notas por fase ya existían |
| REGISTRY | 2 filas por el escritor: `RECUPERACION-AC6-AC10` (registro tardío, con `--nota` y su unidad declarada) y `FASE-RELEASE` con `--release 4.79.0` | `log_phase_completion.py`; se declara que sus columnas «Archivos» **imprimen el conteo como si fuera ruta** (`| 17 | 17 |`), así que el inventario real vive en el CHANGELOG |
| Write-back | 2 publicaciones: la primera **marcada** `reemplazada`, la vigente con sha `1f0ee6e52f00…`; **nada borrado** | `validate_qmind_writeback.py --upload … --file --title`; copia saneada con 6 identidades sustituidas y **prueba de fidelidad** (revertida reproduce `3d2184fb2822…`, byte a byte) |
| Archivado | orden R2.10 respetado | write-back → `build_lesson_index.py` → `git mv` a `Archives/` → `build_lesson_index.py` → `validate_opencode_refs.py --fix` (18 referencias, 2 archivos fuera del plan) → `validate_plan_citations.py --update-baseline` (81 archivos, 745 citas) |
| Índice de lecciones | **348 IDs** fresco | `build_lesson_index.py --check` con EXIT 0 antes y después del `git mv` |
| Derivado vencido por la propia fase | `wiring_report.json` DIVERGE (EXIT 3) al versionar los dos `.py` de la evidencia | regenerado con `validate_wiring.py --write-report` (evidence 153→155, exclusión 165→167) y re-corrído el `--check` en verde |
| Validaciones | quick de apertura **13/13**; quick de cierre y **modo completo** sobre el árbol commiteado: su crudo en `evidence/…/FASE-RELEASE/crudos/` (la corrida que certifica se corre después del write-back y del `git mv`, como manda el prompt) | `run_all_validations.py` (rápido y completo, con notificación de término) |
| **Rojo estructural declarado** | `[17/18]` **VENCIDO por diseño del instrumento** | `verificar_contenido()` compara `sha(instantánea)` con `sha(cuerpo del plan)`: solo se satisface subiendo el cuerpo **sin sanear**. Contrafactual ejecutado en `tmp` sin tocar el árbol (`contrafactual_1718.py`). Dueño: `scripts/validate_qmind_writeback.py` (mini-plan `VERIFICADOR-ESCRITURA-QMIND-2026-09-20`). **Por eso esta fase se cierra INCOMPLETA con el rojo listado, no como TOTAL PASS** |
| Contador v4complete | **1/1 consumido** | ninguna fase posterior a E2E ejecutó el comando |
| R2 | **FUERA DE SERVICIO (R2.1)** con auto-reporte por unidad | `measure_iterations.py` sigue pidiendo el transcript del cliente y su acceso está denegado |

**Lo que queda residuo deliberado, declarado:** los 12 packs de `briefing/` del plan siguen **sin versionar** (estaban
así desde antes de esta fase y ningún verificador los pide); `evidence/…/FASE-E2E/captura_stdout.txt` sigue
**retenido** por S-E2E-6 y no se commitea; y los `.pyc` de la evidencia quedan fuera por `.gitignore`.

**Dictamen que esta release no suaviza.** AC6 y AC10 constan en **FALLA** en el certificado de VERIFY; la recuperación
los cerró **offline y sin corrida nueva**, así que el ZIP entregado el 2026-10-07 conserva ambos defectos y el código
corrector no está ejercitado por ninguna salida del pipeline. AC19b no se intentó. Una muestra de un hotel y una
corrida no certifica todos los hoteles (L-R.4). Deudas vivas con dueño: V-3, V-4, V-6, V-7, V-8, S-F6, S-H2, S-E2E-11,
F-B y F-E, más los tres hallazgos del instrumento de write-back publicados en
`evidence/…/FASE-RELEASE/qmind-writeback-RELEASE.md`.
