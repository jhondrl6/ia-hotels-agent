# Documentación post-proyecto — REFACTOR-WHATSAPP-ENTREGA-2026-09-18

Estado: PREPARACIÓN. Ninguna fase ejecutada. No sustituye la documentación incremental de cada fase ni permite registrar retrospectivamente todas las fases en RELEASE.

## Sección A: Módulos nuevos

| Módulo | Archivos | Descripción | Fase |
|---|---|---|---|
| Verificador AST de cableado (`scripts/`) | `scripts/validate_wiring.py` (905 líneas), `tests/test_validate_wiring.py` (464 líneas, 18 funciones canónicas), artefacto `.opencode/wiring_report.json` | Check 11 del modo rápido: descubre por AST la población de callers de los productores gobernados sin lista fija de archivos, exige las señales cuyo default cambia la conducta en silencio, prohíbe el contrato muerto retirado, y publica población, cobertura, excepciones tipadas y límites. Reporta y **no** reescribe callers | **FASE-G (2026-09-20)** |

## Sección B: Funcionalidades nuevas

| Feature | Módulo | Descripción | Fase |
|---|---|---|---|
| Gobierna señales por productor (no fix) | `validate_wiring.py` | Refactor de guard: 4 productores en política (`PainSolutionMapper.detect_pains`, `CoherenceValidator.validate`, `AssessmentBuilder.with_validation`, `V4ProposalGenerator._generate_dynamic_services_table`) con sus señales y argumentos prohibidos. **No arregla** la divergencia: la registra con dueño | FASE-G |
| Contrato muerto retirado (F-D') | `modules/assessment_builder.py` + `main.py` | `with_validation(self, validation_summary)`: se quita `whatsapp_validation` de la firma y de sus 3 callers. El dato upstream (8 líneas de `main.py` que construyen los `ValidatedField`) se conserva: no es un fix, es limpieza de firma cross-module | FASE-G |
| Numeración del quick re-estimada | `scripts/run_all_validations.py`, `tests/test_validate_lesson_capitalization.py` | El modo rápido pasa de 10 a 11 checks y el completo a /15. El contract test que pineaba el literal `[10/10]` se reescribió a **coherencia estructural** (grupo derivado de `run_all`, ordinales exactos 1..D), que es más fuerte: detecta borrar, duplicar o re-ordenar, no solo escribir mal un número | FASE-G |

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
| Índice | 305 IDs, fresco (preparación) · **314** tras la intervención del 2026-09-19 · **316 tras la revisión 2** (nacen `L-ENT.10` y `L-ENT.11`); «citados sin definición» permanece en **43**, sin citas huérfanas nuevas | Preparación / revisiones |
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
| **FASE-G: QMind** | Consulta por el eje de cierre **permitida y respondida** (Q12); tres de sus filas se aplicaron y midieron. Sin subida | FASE-G |
| **FASE-G: rojo preexistente con causa medida** | `test_medido_contra_el_predecesor_entra_en_alcance_y_su_forma_es_conforme[2026-09-11-…]` está rojo desde `9c4a001` (archivó `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` y `clasificar_planes` solo mira hijos directos de `.opencode/plans/`). G lo conserva igual en PRE y POST, sin excluirlo ni cambiar su expectativa | FASE-G → dueño: deuda del verificador de capitalización |
| Presupuesto de iteraciones | **FUERA DE SERVICIO (R2.1) también en G** (2026-09-20): el instrumento sigue pidiendo el transcript. Auto-reporte en unidad contable (9 rutas tocadas, 2 corridas de baseline + 1 extendida, 7 mutaciones, 2 quicks) con corte de código y corte documental separados; **no se comparó con la referencia de 60 porque esa unidad no era medible** | Todas |
| Presupuesto de iteraciones | **FUERA DE SERVICIO (R2.1) en A**: el instrumento pide el transcript y su acceso no está disponible; se declara **corte documental** y auto-reporte con su unidad, sin sumarlo al instrumento | Todas |

## Sección E: Archivos afiliados actualizados

| Archivo | Cambio | Fase |
|---|---|---|
| Directorio de este plan | Diseño y prompts; sin implementación | Preparación |
| **Revisión 2 (2026-09-19): archivos del plan tocados** | `README.md`, `01-plan-maestro.md` (§1, §2, §3, §4, §5, §6, §7), `04-contrato-ejecucion.md` (límite de lectura de corridas ajenas), `00-lecciones-capitalizadas.md` (§1bis nuevo, Q7-Q10, siete filas en §2, §3bis, §4), `06-checklist-implementacion.md`, `dependencias-fases.md`, `09`, `10-analisis`, `05-…-fase-VERIFY` corregidos; **nuevo** `05-prompt-inicio-sesion-fase-0.md`; A/B/C/G/H/E2E actualizados al nuevo orden. **Sin cambios de código, tests, VERSION ni evidencia** | Revisión 2 |
| `.opencode/LECCIONES-INDEX.md` y `.opencode/lecciones_index.json` | Regenerados tras la revisión 2 (316 IDs); cada fase vuelve a regenerarlos al cerrar | Revisión 2 |
| CHANGELOG.md / docs/GUIA_TECNICA.md / docs/contributing/REGISTRY.md | Cada fase registra su propio trabajo; no modificados en preparación ni en la revisión 2 | Pendiente |
| **FASE-G (2026-09-20): archivos afiliados tocados** | `CHANGELOG.md` (subsección G bajo 4.77.3, sin anticipar versión), `docs/GUIA_TECNICA.md` (nota técnica G), `docs/contributing/REGISTRY.md` (registro por `log_phase_completion.py`), `.opencode/LECCIONES-INDEX.md` + `.opencode/lecciones_index.json` (regenerados al cerrar), `.opencode/wiring_report.json` (nuevo artefacto del AC7), y `DOMAIN_PRIMER.md` regenerado **solo por su writer** (`doctor.py --regenerate-domain-primer`), que por ser archivo versionado ensucia el árbol | FASE-G |

## Registro documental por fase

Cada cierre anota: archivos exactos, tests añadidos, PRE/POST con misma unidad, resultados de mutaciones, limitaciones, estado real y autorización de commit si existe. No elevar versión en fases intermedias. Registrar con `scripts/log_phase_completion.py --check-manual-docs` solo la fase que acaba de completarse.

## Rojo documental del PRE, cerrado por re-medición

`run_all_validations.py --quick` dio 9/10 el 2026-09-18 y **10/10** al re-medirlo el 2026-09-19. La causa medida del rojo: `AGENTS.md`, `VERSION.yaml`, `docs/GUIA_TECNICA.md` y `REGISTRY.md` estaban modificados en el árbol y hoy son idénticos a HEAD tras una reversión ajena a esta sesión. Se retracta la explicación previa por cuatro segmentos: `_check_version_sync` solo ejecuta `sync_versions.py --check`. Regla conservada: re-medir el quick al abrir cada fase y no modificar hooks, baselines de citas ni configuración para forzar un verde.
