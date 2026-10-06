# FASE-D — Veredicto canónico y causa legible del bloqueo (2026-10-06)

**Estado:** COMPLETADA y **commiteada + empujada por orden literal del operador al cierre de la sesión**
(el mandato de implementación no autorizaba el commit: los cinco cortes se sostuvieron sin él y ese fue el
corte que midió R2). El sha y el rango empujado se estampan en el sello documental de FASE-RELEASE.
**ACs gobernadas:** AC4, AC8, AC9 y AC5-intacto, medidas en disco.
**Contador v4complete:** 0/1 (no se ejecutó `main.py v4complete`; la prueba de fail-fast recorre
la ruta de producción con funciones extraídas y `MagicMock`, nunca el CLI real).

## 1. Símbolos revalidados antes de editar

El prompt nombraba `PublicationGateEngine` y su `_check_coherence`. **Medido contra el código
vivo, esos símbolos no existen**: la clase es `PublicationGatesOrchestrator`
(`modules/quality_gates/publication_gates.py:239`) y la gate es `_coherence_gate` (:560), que ya
consumía `coherence_verdict_passes` desde FASE-F. Lo que quedaba por unificar era **la ruta del
pre-gate en `main.py`** y **la entrada directa del orquestador**, que no pasaban por esa
definición.

## 2. Qué se encontró (cuatro defectos, no uno)

| # | Hallazgo medido | Consecuencia |
|---|---|---|
| 1 | `main.py` decidía el pre-gate con `pre_coherence_score >= threshold` (:2563) y volvía a comparar `< threshold` para el aviso (:2571). El veredicto `is_coherent` del reporte **no se leía**. | Un 0.88 con `is_coherent=False` pasaba el pre-gate y entraba a generar assets. |
| 2 | El reporte del pre-gate **no se persistía en ninguna ruta**; solo el orquestador guardaba `coherence_validation.json` (pre-gen suyo) y `coherence_validation_post_gen.json`. | El bloqueo no era legible desde un artefacto (AC8 lo pide). |
| 3 | `AssessmentBuilder.with_coherence` **recibía `pre_coherence_report` y nunca lo leía**: si `asset_result` no traía reporte, fijaba `coherence_score = 0.0` e `is_coherent = None`. | El camino de fallback publicaba un cero fabricado y perdía las causas (L-NC6: el cable estaba en el caller). |
| 4 | `v4_asset_orchestrator.py:333` cortaba con `not is_coherent and overall_score < 0.5`. | La entrada directa dejaba pasar el mismo 0.88 con veredicto False que el pre-gate dejaba pasar. |

Y una restricción que gobierna la solución: `overall_coherence` tiene **`blocking=False`** en
`CoherenceConfig.DEFAULT_RULES`. **D no tocó ese flag ni la barra 0.8** (AC5, dueño C-D): el
bloqueo nuevo no viene de subir el flag, sino de que haya **checks de severidad error sin
resolver**. El score bajo sin errores conserva el régimen documentado (aviso, no bloqueo).

## 3. Producto

* `main.py::_coherence_pre_gate_decision` — **única decisión del pre-gate**: veredicto canónico
  (`coherence_verdict_passes`), culpables (`failed_error_checks`), `blocks_asset_generation`,
  `generate_proposal` y `status`. Aguas abajo no se re-compara el score (aserto por AST).
* `main.py::_persist_coherence_pre_gate` — escribe `v4_audit/coherence_pre_gate_<ts>.json` con la
  serialización canónica del reporte (`to_dict`) + `gate` (decisión, no segunda comparación) +
  `failed_error_check_names` / `failed_error_checks`. Se persiste **antes** de las consecuencias.
* `main.py::_run_asset_generation` — **única entrada a FASE 4**. Con `pre_gate_blocked=True` no
  invoca `orchestrator.generate_assets` y declara el skip; el otro skip sigue siendo
  `audit_result is None`.
* `v4_asset_orchestrator.py::assert_pre_generation_coherence` — corte de la **entrada directa**;
  conserva el suelo `score < 0.5` y añade el corte por culpables, con los nombres en el mensaje.
  `generate_assets` llama a este guard antes de generar (aserto por AST sobre la función real).
* `coherence_validator.failed_error_checks` — **única boca de las causas**: lee el reporte real,
  sin whitelist de nombres, y sanea el mensaje (`mask_telephone_digits`).
* `coherence_validator.read_coherence_report` — lector AC9: `READ_OK` (incluye `checks: []`),
  `ABSENT`, `READ_ERROR`, siempre con `cause`; sin default favorable. El vocabulario vive en
  `whatsapp_contract` (designación de FASE-C); se añadió `READ_ABSENT = "ABSENT"` allí, no en un
  enum propio del lector.
* `assessment_builder` — payload nuevo `coherence_failed_checks` (None = fuente ausente, [] =
  reporte sin errores). Score, veredicto y causas salen **del mismo reporte**:
  `final_coherence_report` → `coherence_report` → `pre_coherence_report` (fallback con su propio
  reporte, ya no un 0.0 inventado).
* `publication_gates._coherence_gate` + `_coherence_cause_details` — publica
  `details.failed_check_names` y `details.failed_check_messages` en las cuatro ramas; el campo
  **no aparece** si el assessment no trae reporte (no se disfraza ausencia con lista vacía). El
  writer `_build_gate_report_payload` ya serializaba `details` entero: no hizo falta tocarlo.

## 4. Mediciones

| Medición | Valor | Instrumento |
|---|---|---|
| PRE (11 archivos, árbol limpio) | **241 passed / 1 skipped / EXIT 0** | `tests_baseline_pre.txt` |
| POST (misma selección + archivo nuevo de D) | **274 passed / 1 skipped / EXIT 0** | `tests_baseline_post.txt` |
| Delta de casos | **+33**, todos del archivo nuevo; 0 bajas, 0 expectativas recortadas | conciliación §5 |
| Canónicas | **4.875 en HEAD → 4.908 en el árbol (+33)**; la fila de AGENTS.md (4.850) sigue vencida y se declara en §9.3 | `git grep -c -E "^\s*def test_" HEAD -- tests` (commiteadas) y `grep -rE "^\s*def test_" tests --include=*.py | wc -l` (árbol) |
| Mutantes | **6 aplicados / 6 rojos por causa correcta / árbol intacto por sha256** | `run_mutations.py` → `mutation_report.json`, crudo en `mutaciones_crudo.txt` |
| Regresión completa | **1 failed / 4.984 passed / 41 skipped / 4 xfailed / EXIT 1** sobre el árbol del sello (`tests_postfull_sello.txt`); el único rojo es el ajeno de §7. Corrida intermedia (antes del saneado en la boca de causas y de la 33ª prueba): 2 failed / 4.982, y ese segundo rojo era el derivado de wiring vencido por los arneses `.py` de esta fase — cerrado regenerando con `validate_wiring.py --write-report`, no recortando la aserción | `tests_postfull_regresion.txt`, `tests_postfull_sello.txt` |
| Validaciones rápidas | **12/13 al abrir el cierre** (rojo Wiring por el derivado vencido) y **13/13 tras regenerar los derivados**; `validate_document_integration.py` All checks passed; `log_phase_completion.py` registró la fase sin GAP | `quick_pre.txt`, `quick_final.txt` |
| Saneado | el número `+573001234567` **no aparece** en el log ni en `gate_report_*.json`; sale como `+573****` | `log_saneado_pre_gate.txt`, `resumen_escritura.json` |

**Reutilización declarada:** POST se re-midió tras cada edición de producto (saneado y 33ª
prueba), no se heredó el verde del PRE. Las mutaciones se aplicaron sobre el archivo vivo, con
ancla única verificada por conteo de ocurrencias, y restauración comprobada por sha256; ningún
rojo deliberado quedó en el árbol.

## 5. Conciliación de casos (delta explicado)

33 funciones nuevas en `tests/quality_gates/test_fase_d_veredicto_canonico.py`: 8 de veredicto del
pre-gate (AC8 + AC5 intacto), 3 de persistencia (AC8), 4 de transporte al assessment (AC4), 5 del
gate report (AC4, incluida la del mensaje que baja ya saneado), 4 de entrada directa del
orquestador (AC8), 5 del lector AC9, 2 del cable de la ruta de producción (AST) y 2 de saneado.
Ninguna prueba existente se re-ancló: las 241 del PRE siguieron verdes con el producto cambiado,
lo que descarta que D haya recortado expectativas ajenas.

## 6. Veredicto por AC

* **AC4 — VERIFICADO OFFLINE.** Dos checks en error aparecen **ambos** en el JSON del writer real
  (`gate_report_coherence_ejemplo.json`, generado por `_build_gate_report_payload`), con nombres
  y mensajes. Sin whitelist: `test_ninguna_whitelist_de_whatsapp_filtra_los_nombres` provoca un
  nombre inexistente (`cobertura_de_geo`) y exige que aparezca. Vacío ≠ ausente:
  `test_gate_pasado_con_reporte_sano_publica_lista_vacia` y
  `test_assessment_legacy_sin_reporte_no_fabrica_lista_vacia`. M2 (no propagar) y M3 (no
  publicar) caen por la aserción respectiva.
* **AC8 — VERIFICADO OFFLINE.** Score 0.88 con veredicto False: `blocks_asset_generation=True`,
  spy de `generate_assets` **no invocado** (`_run_asset_generation`, que es la función que llama
  producción), causas persistidas y log con los culpables. El verde complementario sí entra.
  Cubierta también la **entrada directa del orquestador** y el cable por AST. M1 (volver a la
  comparación solo-score) y M4 (quitar el guard) y M5 (neutralizar el guard del orquestador) y M6
  (no firmar el artefacto) caen cada uno por su aserción.
* **AC9 — VERIFICADO OFFLINE sobre el lector nuevo.** `READ_OK` sobre **baseline real**
  (`output/TAREA7-2026-09-19/.../coherence_validation.json`, 6 checks), `ABSENT`, `READ_ERROR`
  (JSON roto y raíz no-objeto) y el vacío válido como `READ_OK`. Con skip visible si falta el
  baseline. La **retención deliberada** se registra aparte: el payload sigue sin llevar el objeto
  `coherence_report` completo (contrato = score + veredicto + causas), y el comentario queda en
  `with_coherence`.
* **AC5 — INTACTO, deuda C-D sin cerrar por D.** No se bajó ni subió ninguna barra:
  `get_threshold("overall_coherence") == 0.8` y el 0.3 de `NEW_HOTEL_THRESHOLDS` siguen como
  estaban, y `is_blocking("overall_coherence")` sigue **False** (D no lo cambió; gobernar la ruta
  del hotel nuevo no era mandato de D). Las cinco barras de `FASE-C/thresholds.json` no se
  re-transcriben aquí.

## 7. Rojo ajeno declarado, no curado

`tests/quality_gates/jev_pilot/test_jev_pilot_deepseek_brazo.py::test_la_falta_de_deepseek_falla_antes_de_enviar_aunque_haya_clave_anthropic`
falló en la corrida completa con `RedProhibida` en vez de `CredencialAusente` y **pasa aislado
(1 passed)** -- re-ejecutado sobre el arbol del sello, el archivo completo pasa 15/15 y la superficie
de D (gates + builder + bateria nueva) pasa 151 passed / 1 skipped. Es contaminación de entorno entre tests del piloto JEV (el guard de credencial ve
una clave que otro test dejó), sin ruta alguna por los símbolos que tocó D. **Dueño: piloto JEV.**
Se declara y no se cura (restricción: no corregir hallazgos ajenos). El segundo rojo de esa
corrida (`test_validate_wiring_check_derivado_versionado`) sí es consecuencia de esta fase: los
arneses `.py` de evidencia mueven los contadores del derivado, y se resuelve regenerando
`validate_wiring.py --write-report`, no recortando la aserción.

## 8. Lecciones de esta sesión

* **L-NC6 aplicada donde el plan la pedía y donde no la nombraba.** El cable perdido no estaba en
  los gates: estaba en `with_coherence`, que recibía el reporte del pre-gate y no lo leía. La cura
  fue leer el caller, no crear una segunda fuente.
* **L-PF10 gobernó dos sitios distintas veces.** `coherence_failed_checks` distingue None de [];
  y el lector de AC9 trata `checks: []` como lectura buena.
* **L-T4A.5 cazó un verde que no llegaba a la rama.** La primera versión de la prueba de cable
  buscaba un literal en el volcado del AST; pasaba con el guard destruido y fallaba con el texto
  intacto. Se re-escribió comparando nodos `Compare`.
* **Lección nueva (L-D-SAN, formulada al medir):** *el saneado se pone en la boca que produce el
  dato, no en cada salida.* Con el mask llamado desde la consola y desde el artefacto, la tercera
  salida —el `details` del gate report que AC4 exigía publicar— seguía llevando el número
  completo. Movido el mask a `failed_error_checks`, las tres salidas son saneadas a la vez y el
  criterio tiene un solo dueño.
* **Lección nueva (L-D-FLG):** *gobernar un bloqueo sin tocar el flag.* El mandate de AC8 («un
  error debe impedir entrar a la generación») se cumplía también subiendo `blocking=True` en
  `overall_coherence`; se hizo bloqueando **por culpables de severidad error** y dejando la barra
  y su flag como los encontró D. El rojo que eso evita: el régimen no-bloqueante del score bajo,
  que es de AC5 y tiene dueño propio.

## 9. Checkpoints pendientes de autorización ajena

1. ~~**Commit** del producto + tests + evidencia~~ **CERRADO en la misma sesión**: orden literal del
   operador («Commit + L3 + Push»). El sha y el rango empujado se estampan en el sello documental de
   FASE-RELEASE (decisión de C: no abrir sellos recursivos por acciones git).
2. **DOMAIN_PRIMER**: no se regeneró. Está versionado y el prompt condiciona la regeneración a
   autorización explícita de escritura; se declara el checkpoint.
3. **AGENTS.md §Cobertura por Modulo** (+33 en `quality_gates`) y la fila de `Estado Actual`:
   configuración central protegida; pide instrucción literal.
4. **Write-back QMind** del aporte de D: operación remota, requiere autorización propia.
5. **Piloto JEV**: rojo de contaminación de entorno con dueño declarado (§7).
