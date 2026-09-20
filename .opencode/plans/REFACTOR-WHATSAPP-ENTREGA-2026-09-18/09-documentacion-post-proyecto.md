# Documentación post-proyecto — REFACTOR-WHATSAPP-ENTREGA-2026-09-18

Estado: PREPARACIÓN. Ninguna fase ejecutada. No sustituye la documentación incremental de cada fase ni permite registrar retrospectivamente todas las fases en RELEASE.

## Sección A: Módulos nuevos

| Módulo | Archivos | Descripción | Fase |
|---|---|---|---|
| Verificador AST de cableado (`scripts/`) | `scripts/validate_wiring.py` (905 líneas), `tests/test_validate_wiring.py` (464 líneas, 18 funciones canónicas), artefacto `.opencode/wiring_report.json` | Check 11 del modo rápido: descubre por AST la población de callers de los productores gobernados sin lista fija de archivos, exige las señales cuyo default cambia la conducta en silencio, prohíbe el contrato muerto retirado, y publica población, cobertura, excepciones tipadas y límites. Reporta y **no** reescribe callers | **FASE-G (2026-09-20)** |

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
| **FASE-G: rojo preexistente con causa medida** | `test_medido_contra_el_predecesor_entra_en_alcance_y_su_forma_es_conforme[2026-09-11-…]` está rojo desde `9c4a001` (archivó `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` y `clasificar_planes` solo mira hijos directos de `.opencode/plans/`). G lo conserva igual en PRE y POST, sin excluirlo ni cambiar su expectativa | FASE-G → dueño: deuda del verificador de capitalización |
| Presupuesto de iteraciones | **FUERA DE SERVICIO (R2.1) también en G** (2026-09-20): el instrumento sigue pidiendo el transcript. Auto-reporte en unidad contable (9 rutas tocadas, 2 corridas de baseline + 1 extendida, 7 mutaciones, 2 quicks) con corte de código y corte documental separados; **no se comparó con la referencia de 60 porque esa unidad no era medible** | Todas |
| Presupuesto de iteraciones | **FUERA DE SERVICIO (R2.1) en A**: el instrumento pide el transcript y su acceso no está disponible; se declara **corte documental** y auto-reporte con su unidad, sin sumarlo al instrumento | Todas |

## Sección E: Archivos afiliados actualizados

| Archivo | Cambio | Fase |
|---|---|---|
| Directorio de este plan | Diseño y prompts; sin implementación | Preparación |
| **Revisión 2 (2026-09-19): archivos del plan tocados** | `README.md`, `01-plan-maestro.md` (§1, §2, §3, §4, §5, §6, §7), `04-contrato-ejecucion.md` (límite de lectura de corridas ajenas), `00-lecciones-capitalizadas.md` (§1bis nuevo, Q7-Q10, siete filas en §2, §3bis, §4), `06-checklist-implementacion.md`, `dependencias-fases.md`, `09`, `10-analisis`, `05-…-fase-VERIFY` corregidos; **nuevo** `05-prompt-inicio-sesion-fase-0.md`; A/B/C/G/H/E2E actualizados al nuevo orden. **Sin cambios de código, tests, VERSION ni evidencia** | Revisión 2 |
| `.opencode/LECCIONES-INDEX.md` y `.opencode/lecciones_index.json` | Regenerados tras la revisión 2 (316 IDs), al cerrar G (318) y el 2026-09-20 con el write-back (319); cada fase vuelve a regenerarlos al cerrar | Revisión 2 / G / write-back |
| CHANGELOG.md / docs/GUIA_TECNICA.md / docs/contributing/REGISTRY.md | Cada fase registra su propio trabajo; no modificados en preparación ni en la revisión 2 | Pendiente |
| **FASE-0 (2026-09-20): archivos afiliados tocados** | Producto: `modules/quality_gates/publication_gates.py`, `modules/quality_gates/tribunal/outcome.py`, `main.py`. Tests: nuevo `tests/test_fase_0_ac20_evidencia_veredicto.py`; re-atados a coherencia interna `tests/quality_gates/tribunal/test_p2_veredicto_enriquecido.py` (asertaba la forma exacta de `reviewer_reports`) y corregido el fixture contradictorio `tests/quality_gates/tribunal/test_diagnosis_reviewer.py`. Evidencia: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-0/` (12 archivos: 4 instrumentos reejecutables —`pre_camino_gate.py`, `contrafactual_ac20.py`, `run_mutations.py`, `build_thresholds.py`—, 4 salidas medidas en JSON, 3 registros de tests y 1 informe). Documental: `CHANGELOG.md`, `docs/GUIA_TECNICA.md`, `docs/contributing/REGISTRY.md` (por `log_phase_completion.py`), el par del indice regenerado (319 → 320 IDs) y los siete documentos del plan (§00, §05 de la fase, §06, §09, §10, README y dependencias). La autorización de commit no se pidió durante la fase; **commit `7c6e75f` y push a `origin/master` ejecutados el mismo 2026-09-20 con instrucción literal del operador** (paridad 0/0 verificada con `git ls-remote`; los 7 checks del pre-commit pasaron sin saltar ninguno) — incluyendo índice, registro y documentos del plan | FASE-0 |
| **FASE-G (2026-09-20): archivos afiliados tocados** | `CHANGELOG.md` (subsección G bajo 4.77.3, sin anticipar versión), `docs/GUIA_TECNICA.md` (nota técnica G), `docs/contributing/REGISTRY.md` (registro por `log_phase_completion.py`), `.opencode/LECCIONES-INDEX.md` + `.opencode/lecciones_index.json` (regenerados al cerrar), `.opencode/wiring_report.json` (nuevo artefacto del AC7), y `DOMAIN_PRIMER.md` regenerado **solo por su writer** (`doctor.py --regenerate-domain-primer`), que por ser archivo versionado ensucia el árbol | FASE-G |

| **FASE-B (2026-09-20): archivos afiliados tocados** | Producto: 11 archivos de `modules/` + `main.py` (solo comentario) — detalle en la sección "Cierre incremental de FASE-B" de este documento. Tests: nuevo `tests/commercial_documents/test_fase_b_promesa_whatsapp.py` (12 funciones canónicas) y re-vinculaciones en 8 archivos, todas por cambio de forma o de ejemplo, ninguna aflojando una expectativa. Evidencia: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-B/` (9 artefactos, incluidos `run_mutations.py` reejecutable, `mutation_report.json` 6/6, los tres registros de tests y el `CHECKPOINT-autorizaciones-pendientes.md`). Documental: `CHANGELOG.md` (subsección B bajo 4.77.3, sin anticipar versión), `docs/GUIA_TECNICA.md` (nota técnica del patrón resolución ≠ conteo), `docs/contributing/REGISTRY.md` (por `log_phase_completion.py`), el par del índice regenerado y los cinco documentos del plan (§00, §05 de la fase, §06, §09, dependencias). **Commit y push NO ejecutados**: la autorización se pidió al cierre de la sesión | FASE-B |

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
537 → 539 (delta +2 explicado) → 552 con la suite nueva. Regresión completa 4 failed /
4.261 passed, tres rojos preexistentes con dueño y **uno de B con causa medida**
(`test_get_blocking_issues`, gate de alignment con servicio condicional).

**Mutaciones:** 8/8 (M1–M8) rojos causados por el guard; restauración por sha256 (tras corregir
el falso negativo de `write_text()` en Windows, que convertía los archivos a CRLF).

**Limitaciones declaradas:** (i) el servicio de preparación queda fuera del universo
contado, así que el gate de alignment no lo ve como deuda cuando es el único
comprometido — dueño A4/AC5 (D/E); (ii) `run_v4_complete_mode` sigue registrando el centinela
`detected_via_html` en el `ValidationSummary` con `can_use_in_assets=True` (fuera de la
allowlist de B; dueño C/AC6); (iii) `wa_button_gen` conserva su número de placeholder y
`local_content_generator` construye dos `wa.me/` sin guarda (C/D); (iv) umbrales de
WhatsApp (0.9 coherencia / 0.7 catálogo / 0.3 hotel nuevo / 0.5 conflicto) quedan
inventariados pero sin gobernar: AC5 es de C/D.

**Estado real:** B **INCOMPLETA**. **Commit y push sin autorización ni ejecución.**
Contador v4complete 0/1. R2 FUERA DE SERVICIO (R2.1).

## Rojo documental del PRE, cerrado por re-medición

`run_all_validations.py --quick` dio 9/10 el 2026-09-18 y **10/10** al re-medirlo el 2026-09-19. La causa medida del rojo: `AGENTS.md`, `VERSION.yaml`, `docs/GUIA_TECNICA.md` y `REGISTRY.md` estaban modificados en el árbol y hoy son idénticos a HEAD tras una reversión ajena a esta sesión. Se retracta la explicación previa por cuatro segmentos: `_check_version_sync` solo ejecuta `sync_versions.py --check`. Regla conservada: re-medir el quick al abrir cada fase y no modificar hooks, baselines de citas ni configuración para forzar un verde.
