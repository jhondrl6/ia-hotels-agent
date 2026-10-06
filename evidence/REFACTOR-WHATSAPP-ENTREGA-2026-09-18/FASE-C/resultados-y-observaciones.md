# FASE-C — resultados y observaciones medidas (2026-10-06)

**Estado: COMPLETADA, sin commit** (el mandato del prompt no autoriza commit; los cinco
cortes se sostienen sin él — `04-contrato-ejecucion.md §Límites y precedencias`).
HEAD de partida: `5398a3a`. Contador v4complete: **0/1** (no se ejecutó ninguna corrida;
el intento sigue reservado a E2E).

## 1. Qué se cambió

| # | Archivo | Cambio | AC |
|---|---|---|---|
| 1 | `modules/data_validation/whatsapp_contract.py` (nuevo) | Un vocabulario para los dos lectores (`WHATSAPP_HTML_PATTERNS`, `WA_HREF_TOKENS`, `PLUGIN_FINGERPRINT_TOKENS`), clasificación de evidencia (`clasificar_evidencia`), estados de lectura (`OK`/`READ_ERROR`/`NO-APLICABLE`) y el **contrato de forma** del número (`rechazo_numero_whatsapp`: dígitos ASCII explícitos, banda 8–15, separadores, centinelas; sin inferir país ni completar partes). Docstring con la **designación expresa** de los dos lectores | AC6, AC19a, prerrequisito |
| 2 | `modules/asset_generation/site_presence_checker.py` | `PresenceCheckResult` publica `observation_scope`/`read_status`/`presence_evidence_kind` (claves nuevas, con default). `_check_html_element` deja de colapsar la excepción a `{"found": False}`: devuelve `READ_ERROR` y clasifica la evidencia con el vocabulario compartido. `_check_asset_presence`: un `READ_ERROR` produce `VERIFICATION_FAILED` (desconocido), **no** `NOT_EXISTS` (ausencia); el `exists` por HTML sale con su tipo de evidencia y su alcance; el fallthrough declara `observation_scope` y `read_status` | AC19a, L-PF6 |
| 3 | `modules/asset_generation/site_presence_adapter.py` | `_presence_result_to_canonical` y `_asset_data_to_canonical` **conservan `details`** y publican las tres claves nuevas. `_add_observacion` añade solo lo que el lector trajó: un resultado sin observación mantiene la forma exacta `status/site_verified/confidence` | AC19a |
| 4 | `modules/asset_generation/conditional_generator.py` | El botón lee **exclusivamente el campo validado** (`_campo_whatsapp_validado`, orden por nombre, nunca `phone_web`; respeta `can_use_in_assets`). `_generate_whatsapp_button` valida la forma y **rechaza antes de emitir href**. `generate()` captura `NumeroWhatsAppNoUtilizable` y devuelve `status=blocked` con `reason_code`, `rejection{causa,origen}`, `can_use=False`, `destino` y `setup_alternativo` | AC3, AC6 |
| 5 | `modules/asset_generation/v4_asset_orchestrator.py` | FIX-A2 curado: `validated_data["whatsapp"]` deja de ser `phone_web` y pasa a ser **alias del campo validado** (mismo objeto), así el preflight conserva su `required_field` sin mantener un número paralelo (L-NC6) | AC6 |
| 6 | `modules/commercial_documents/coherence_validator.py` | **Retirado el boost** `max(confidence, 0.95)` por mero `exists`. Umbral 0.9 y `blocking=True` intactos. La firma sigue recibiendo `site_presence_report` (los llamadores la propagan) pero ya no interviene en la barra | AC3 |
| 7 | `main.py` | El centinela `detected_via_html` pasa a `can_use_in_assets=False` (antes `True`: viajaba como teléfono) | AC6 |
| 8 | `modules/auditors/v4_comprehensive.py` | `_detect_whatsapp_from_html` delega el vocabulario en el módulo compartido. Lista copiada-idéntica (13 patrones): ninguna ruta cambia su decisión por la unificación. Su docstring nombra al lector (**dolor**) y al hermano (**presencia**) | prerrequisito AC19a |

Tests: nuevo `tests/asset_generation/test_fase_c_boton_seguro.py` (24 funciones canónicas,
39 casos) y **cuatro re-anclajes** en archivos existentes (§4).

## 2. Mediciones

| Qué | Comando o instrumento | Resultado |
|---|---|---|
| PRE (16 archivos de la selección) | `pytest $(cat FASE-C/seleccion_pertinente.txt) -q` | **201 passed / 1 skipped**, EXIT 0 → `tests_baseline_pre.txt` |
| Quick PRE | `scripts/run_all_validations.py --quick` | **ALL VALIDATIONS PASSED (13/13)** → `quick_pre.txt` |
| POST (misma selección + batería nueva) | igual que PRE, más `test_fase_c_boton_seguro.py` | **238 passed / 1 skipped**, EXIT 0 → `tests_baseline_post.txt`. Delta **+37 casos**: 24 funciones nuevas con 3 parametrizaciones (9+5+3). Ninguna selección previa cambió de resultado |
| Rojo intermedio medido tras el blindaje y antes de re-anclar | misma selección | **4 failed / 197 passed** — los cuatro son las aserciones que legitimaban el defecto (§4) |
| Regresión completa | `pytest tests/ -q -p no:randomly` | **1 failed / 4.951 passed / 41 skipped / 4 xfailed** en 406,62 s → `tests_postfull_regresion.txt`. El único rojo es `tests/quality_gates/jev_pilot/test_jev_pilot_deepseek_brazo.py::test_la_falta_de_deepseek_falla_antes_de_enviar_aunque_haya_clave_anthropic`, del **plan hermano JEV**: en la corrida aislada de su directorio pasan **141/141**, así que es dependencia de orden/estado entre pruebas y no un rojo de C (dueño: piloto JEV; ver §5.6). Los 5 rojos que C sí produjo (4 de `test_phase5_integration.py` y 1 de `test_datasource_gap.py`) quedaron re-anclados y verdes en esta corrida |
| Funciones canónicas | `grep -rE "^\s*def test_" tests --include=*.py \| wc -l` | **4.873** (4.850 antes de C → **+23**) |
| Barras de WhatsApp | `build_thresholds.py` → `thresholds.json` | 0.9 coherencia (blocking=True) · 0.9 `no_whatsapp_visible` · 0.5 `whatsapp_conflict` · 0.7 catálogo (`block_on_failure=False`) · 0.3 `NEW_HOTEL_THRESHOLDS` · 0.9 `CommercialGate` |
| Mutantes | `run_mutations.py` → `mutation_report.json` | **9/9 rojos causados por el guard** (M1 1 prueba, M2 2, M3 1, M4 5, M5 1, M6 1, M7 2, M8 4, M9 2 — cada mutante rompe un grupo distinto, ningún verde persistente), **9/9 restaurados y verificados por sha256** |
| R2 | `measure_iterations.py` | **FUERA DE SERVICIO (R2.1)**: el instrumento pide el transcript del cliente y su acceso se deniega. Auto-reporte con su unidad declarada: **≈150 tool_use** hasta «listo para revisión» sobre un presupuesto de referencia de 60 → **exceso medido, no cumplido**. El corte usado fue **«hasta listo para revisión»** (commit no autorizado al momento de medir; el commit se autorizó después, ver §8) |

## 3. ACs: síntoma original → resultado

| AC | Síntoma que gobernaba | Qué se obtuvo |
|---|---|---|
| AC3 | Botón forzado con confianza <0.9, CONFLICT, UNKNOWN o centinela quedaba en verde porque la presencia lo promocionaba | Bloqueo demostrado **con y sin presencia** (parametrizado sobre las tres confianzas, 6 corridas) y el `VERIFIED` válido pasa. Umbral y `blocking` intactos. Mutante M4 (restaurar el boost) rompe la batería |
| AC5 | «El umbral de WhatsApp» publicado como uno solo | Seis barras leídas del código en `thresholds.json`, cada una con fuente y consumidor. El rojo medible (0.3 de hotel nuevo planifica el botón contra la barra 0.9) **no se resolvió bajando ni subiendo barras**: se ancló el destino. Dueño C-D; la gobernanza de esa ruta sigue en deuda registrada |
| AC6 | `phone_web` ganaba por precedencia; el centinela viajaba como teléfono; `''.join(isdigit)` fabricaba `wa.me/5734567` de un valor enmascarado y `wa.me/` vacío de un valor sin dígitos | Rechazo por causa nombrada (VACIO / CENTINELA / TIPO_NO_TEXTO / SIN_DIGITOS / DIGITOS_NO_ASCII / CARACTERES_NO_PERMITIDOS / LONGITUD_INVALIDA / CAMPO_NO_UTILIZABLE / SIN_CAMPO_VALIDADO), href solo con dígitos ASCII 8–15, sin completar partes. El HTML **escrito por el writer real** se releyó de disco: `https://wa.me/573104019049?` presente y `wa.me/?text=` ausente. Producibilidad: el botón se planifica por la ruta viva (`whatsapp_conflict` con barra 0.5) y **ese** botón planificado con centinela resulta bloqueado — no se inyectó el asset a mano |
| AC19a | El lector veía una huella de plugin y el reporte la entregaba como `exists` sin tipo de evidencia; la excepción de transporte se leía como ausencia; `_presence_result_to_canonical` tiraba `details` con el `whatsapp_href_number` | Claves nuevas **solo aditivas**: `observation_scope` (raíz, `crawl: False`), `read_status`, `presence_evidence_kind`, y `details` conservado. `status`/`site_verified`/`confidence` sin redefinir; los 4 asserts de igualdad exacta siguen verdes (se mide en §4 y en la batería: `test_reporte_sin_observacion_conserva_la_forma_exacta`). Excepción de transporte → `READ_ERROR` + `VERIFICATION_FAILED`, nunca `not_exists`. Sobreviven al writer del snapshot leyéndolos de disco |
| Prerrequisito | Dos lectores con patrones propios decidían aparte | **Designación expresa** en `whatsapp_contract.py` (presencia vs dolor) y vocabulario único compartido. El auditor delega; la lista quedó copiada-idéntica y hay un test de caracterización que rompe si la delegación pierde un patrón |

**Ninguna ruta del lector afirma "no tiene WhatsApp"**: la ausencia observada se
acompaña de `observation_scope.nivel = "raiz"` y `crawl = False`; el fallo de fetch es
estado desconocido. No se amplió el alcance de inspección (sin crawls, sin dependencias nuevas).

## 4. Los cuatro re-anclajes (rojos deliberados del blindaje)

| Test | Qué afirmaba | Qué afirma ahora | Por qué no es "forzar verde" |
|---|---|---|---|
| `test_site_presence_adapter.py::test_whatsapp_exists_boost` → renombrado `test_whatsapp_exists_no_promociona_a_verified` | `score >= 0.95` gracias al boost | `score < 0.9`, `passed is False`, `severity == "error"` | Era el diente del boost que AC3 ordena retirar. La expectativa se **invirtió** porque el plan la define al revés, y se reforzó con dos aserciones nuevas |
| `test_whatsapp_button.py::test_whatsapp_generates_without_data` → `test_whatsapp_sin_numero_utilizable_bloquea_sin_producir_href` | éxito con warning pese a no haber número | `success False`, `status "blocked"`, causa `SIN_CAMPO_VALIDADO`, sin `file_path` | El "fallback" que promocionaba era la ruta del `wa.me/` vacío. NEVER_BLOCK sigue vigente para los demás assets y para confianza baja; `block_on_failure=False` del catálogo no se tocó |
| `test_whatsapp_button.py::test_whatsapp_generates_with_data` | mismo, con fixture `"+573****4567"` | mismo, con fixture `"+57 310 401 9049"` y clave `whatsapp_number` | El fixture llevaba un valor **enmascarado**: antes el generador borraba los `*` y emitía 7 dígitos. La aserción de éxito no cambió; cambió la entrada, que era inválida por contrato |
| `test_conditional_generator.py::test_generate_with_blocked_returns_error` | `success True`, `can_use True`, "NUNCA blocked" | `success False`, `status "blocked"`, `reason_code` | Mismo mandato AC3. Se dejó constancia escrita dentro del test de por qué cede la expectativa vieja |

## 5. Observaciones medidas (no corregidas, con dueño)

1. **`fallback="generate_basic_whatsapp"` sigue en `ASSET_CATALOG` sin implementador.** Solo lo
   lee un test de catálogo. No puede saltar por él un botón vacío — pero es una promesa de
   catálogo sin ruta. Dueño: catálogo (FASE-H o RELEASE lo declara).
2. **`presence_evidence_kind` tiene cuatro valores, no tres.** El plan enumeraba
   `wa.me_href`/`plugin_fingerprint`/`ninguna`; la sonda de texto visible ya existía y produce
   `found=True` hoy. Reducirla a `plugin_fingerprint` la mal-atribuiría y a `ninguna` la
   contradice, así que C publicó `texto_visible`. Desviación declarada del literal del plan.
3. **`destino`/`setup_alternativo` viajan en el resultado del generador, no en un artefacto
   de reporte propio.** `FailedAsset.reason` los lleva al reporte de generación; la
   serialización completa del `rejection` queda en el dict del generador. Si VERIFY exige el
   `rejection` en el JSON final, hace falta una pata de writer (dueño: VERIFY/RELEASE).
4. **La barra 0.3 de `NEW_HOTEL_THRESHOLDS` sigue permitiendo planificar el botón** en hotel
   nuevo con confianza 0.4. C lo gobernó anclando el destino (test
   `test_la_barra_baja_de_un_hotel_nuevo_no_autoriza_un_destino_inventado`), no la barra.
   AC5 completo sigue siendo deuda C-D.
5. **`observation_scope` declara el alcance, no lo amplía.** El hueco de diseño original
   (canal solo en página interna) sigue existiendo como *no observado*; la diferencia es que
   ahora se lee en el reporte. Su migración a tri-estado en los consumidores es **AC19b**
   (deuda §6 del maestro), no se intentó.

## 6. Cortes

Implementación terminada ✓ · Verificación terminada ✓ (POST 238, mutantes §2) · Cierre
documental ✓ (§7) · Listo para revisión ✓ · **Espera de autorización**: commit, push, L3,
write-back QMind y regeneración de `DOMAIN_PRIMER` — ninguno ejecutado, ninguno asumido.

## 8. Sellado posterior: orden del derivado, errata de registro y el commit autorizado

**6.º observación (rojo ajeno, con dueño).** `test_jev_pilot_deepseek_brazo.py::
test_la_falta_de_deepseek_falla_antes_de_enviar_aunque_haya_clave_anthropic` falla **solo** en la corrida
completa; su directorio aislado pasa **141/141** (medido con `pytest tests/quality_gates/jev_pilot/ -q
-p no:randomly`). Es dependencia de orden/estado entre pruebas del plan hermano `EVALUACION-JEV-TYPESAFE`, no
un rojo de C: ninguno de los ocho archivos de producto toca proveedores ni el piloto. Dueño: piloto JEV.

**Rojo propio que C produjo y curó — el orden del derivado.** La primera y la segunda corrida completa dieron
**18 failed + 27 errors**, todos en `tests/quality_gates/lesson_relevance/` (triaje) y `jev_pilot`. La causa
no fue el código de C: fue el **orden de cierre**. Se editaron documentos del plan (`05-prompt-C`, `09`, `10`)
*después* de regenerar `.opencode/lecciones_index.json`, y `triage_lesson_relevance.leer_suelo()` recalcula el
suelo y lo contrasta con el disco → `SueloNoLeible: VENCIDO: el disco y el calculo propio difieren`. Con el
`build_lesson_index.py --check` corriendo antes de esas ediciones, el check propio daba **[OK] Índice fresco**
mientras el consumidor real estaba rojo: un verde de un verificador que no mira al lector que lo consume.
Cure ejecutada con los writers, en el orden canónico y sin volver a editar el corpus después:
`build_phase_briefing.py --plan` → `build_lesson_index.py` → `--check` → `validate_opencode_refs.py --fix` →
`validate_plan_citations.py --update-baseline` → `validate_wiring.py --write-report`. Verificación:
`tests/quality_gates/lesson_relevance/` + el caso de `jev_pilot` → **77 passed**; y la corrida completa
final → **1 failed / 4.951 passed** con el único rojo ya atribuido a la hermana.

**Errata del registro.** `log_phase_completion.py` se corrió con `--archivos-mod 30`, cifra redactada antes de
finalizar documentos y derivados. El conteo **medido** de esta fase es **40 archivos**: 8 de producto (1
nuevo), 6 de tests (1 nuevo), 10 documentales (`CHANGELOG.md`, `docs/GUIA_TECNICA.md`,
`docs/contributing/REGISTRY.md`, `docs/contributing/.last_doc_phase.json` y cinco documentos del plan: §00,
§05-C, §06, §09, §10 y `dependencias-fases.md`), 4 derivados regenerados por su writer
(`.opencode/LECCIONES-INDEX.md`, `.opencode/lecciones_index.json`,
`.opencode/plans/plan_citations_baseline.json`, `.opencode/wiring_report.json`) y 11 artefactos de evidencia.
La fila de `REGISTRY.md` **no se re-escribe**: el escritor es aditivo y volver a correrlo apilaría una entrada
duplicada (§4.5.1 del executor). Queda esta errata como fuente de la cifra corregida.

**Commit.** El operador lo autorizó después de medido todo («Git Commit + L3», 2026-10-06). Viajan con C:
producto, tests, evidencia, los documentos de cierre, los cuatro derivados y `REGISTRY.md`. **No** se stagea
el trabajo ajeno que ya estaba sucio al abrir la sesión: `01-plan-maestro.md`, `04-contrato-ejecucion.md`,
los prompts D/E/E2E/F/H/RELEASE/VERIFY, los tres archivos del plan hermano
`VERIFICADOR-ESCRITURA-QMIND-2026-09-20/` y `evidence/…/PUESTA-AL-DIA-2026-10-06/`. Tres archivos del cierre
de C **sí vienen mezclados** (`05-...-fase-C.md`, `10-analisis`, `dependencias-fases.md`) porque la puesta al
día del 2026-10-06 que ya estaba en el árbol sostiene instrucciones que C cita (`--fecha` obligatoria y el
re-anclaje del CHANGELOG bajo `## [Sin publicar]`): esa procedencia se declara en el mensaje del commit.
Tampoco se versiona `.opencode/plans/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/briefing/`: los packs de este plan
nunca estuvieron en el árbol commiteado (solo los del plan archivado), y versionarlos ampliaría el gate
`[8/8]` más allá del mandato de C. Se declara como decisión de alcance, no como olvido.
**Push: no autorizado** (el operador pidió commit y L3).

**Procedencia de esta cifra:** medida sobre el árbol con el código y los tests de C ya re-anclados, **antes** de
la edición documental del §8 y de su re-generación de derivados. Después de esa edición la superficie afectada
se re-midió directamente — `tests/quality_gates/lesson_relevance/` + `tests/quality_gates/jev_pilot/` →
**203 passed** — y los derivados se regeneraron en el orden canónico; la corrida completa sobre el árbol final
se re-estampa en el commit de sello si difiere de esta fila.

## 9. Cortes con su medición

| Corte | Estado |
|---|---|
| Implementación terminada | ✅ 8 archivos de producto, con el contrato compartido y el guard en el límite de emisión |
| Verificación terminada | ✅ PRE 201/1 skipped · POST 238/1 skipped · regresión 1 failed/4.951 passed con el rojo ajeno atribuido · 9/9 mutantes rojos y restaurados por sha256 · quick 13/13 |
| Cierre documental | ✅ §7, con la errata de §8 |
| Listo para revisión | ✅ este informe |
| Espera de autorización | commit ✅ autorizado y ejecutado · push ❌ no autorizado · L3 ✅ autorizada (se corre sobre el rango commiteado) · write-back QMind ❌ no autorizado · `DOMAIN_PRIMER` ❌ checkpoint declarado |

## 7. Cierre documental ejecutado

`CHANGELOG.md` (subsección FASE-C bajo `## [Sin publicar]`), `docs/GUIA_TECNICA.md`,
`05-prompt-inicio-sesion-fase-C.md` (estado), `06-checklist-implementacion.md` (filas C y
AC3/AC5/AC6/AC19a), `dependencias-fases.md`, `09-documentacion-post-proyecto.md`,
`10-analisis-post-implementacion.md`, `00-lecciones-capitalizadas.md` (aplicación efectiva),
`log_phase_completion.py --fase FASE-C`, `build_lesson_index.py`,
`run_all_validations.py --quick` y `validate_document_integration.py`.
**DOMAIN_PRIMER**: no regenerado — el mandato de esta sesión no autoriza escribir
`.agent/knowledge/DOMAIN_PRIMER.md`; se declara el checkpoint (`04-contrato-ejecucion.md` paso 4).
