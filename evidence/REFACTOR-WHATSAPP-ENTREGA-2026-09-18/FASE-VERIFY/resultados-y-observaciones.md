# FASE-VERIFY — certificación transversal sobre evidencia existente (2026-10-07)

**Plan:** REFACTOR-WHATSAPP-ENTREGA-2026-09-18. **Fase:** VERIFY, ejecución **DIRECTA** (no delegable, executor §4.6).
**Sin código, sin tests, sin `v4complete`, sin remediación** (L-V.4). Entregable: `certificacion.json` en este directorio.

**Dictamen global:** la **meta de entrega se demostró** (ZIP publicado + acta favorable + AC20 en flujo real), pero la
certificación del plan **no es íntegra**: **AC6 y AC10 quedan en FALLA en régimen E2E**, sobre superficies que el plan
nunca modificó. 14 ACs con pata offline superada, 5 con ejercicio vivo, 1 diferido (AC19b), 2 en FALLA.

## 1. Tarea 1 — integridad e inventario

### 1.1 Hashes y control de la corrida única

| Verificación | Instrumento | Resultado |
|---|---|---|
| Los 10 `source_hashes` de `run_control.json` contra el árbol vivo | `sha256sum` sobre las 10 rutas | **10/10 casan** (runner en `1efa6cd1…`, tras la re-emisión de b1-bis) |
| `argv_sha256` | recomputado con la fórmula del propio runner: `run_once.argv_sha256("\0".join(argv))` | `b5748891…` **igual al publicado**; argv de 11 piezas con `--permission-mode auto` |
| Capturas | sha256 de `captura_stdout.txt` (16.931 B) y `captura_stderr.txt` (732 B) | **ambas casan** con `run_control.capturas` |
| `attempts`, PID, timestamps, exit code | lectura del control | `attempts: 1`, `pid 30576`, `estado FINALIZADO`, `exit_code 0`, creado→terminado **116 s**, monotonía verificada |
| `preflight.sha256` | lectura del control | **`null`** — la ruta queda consignada, su integridad no (S-E2E-8 sigue abierto) |
| ZIP publicado contra acta | `zipfile` + `hashlib` | sha `487f5800…` **igual** en disco y en `package_evidence`; 57 miembros = `member_count`; `testzip() → None`; **0 `.zip.tmp`** residantes |
| ZIP sin snapshot interno ni documentos retenidos | `namelist()` de los 57 miembros | **ningún** `_review_inputs`, `review_input_manifest`, `acta_revision` ni `revision_*.json`; `ASSETS/v4_audit/` solo reporta de auditoría |
| MANIFEST contra membresía | coteje bilateral + tamaño de cada miembro leído | 57/57, **0** entradas sin miembro, **0** miembros sin entrada, **0** discrepancias de bytes |

### 1.2 Inventario de evidencia por fase (`read_status` y disposición)

Comando: `find evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18 -type f | wc -l` y `git ls-files <dir> | wc -l` (medido 2026-10-07).

| Fase | En disco | Versionados | `read_status` | Disposición y observaciones |
|---|---|---|---|---|
| FASE-0 | 13 | 13 | READ_OK | publicado; incluye `thresholds.json`, `baseline_vs_contrafactual.json`, 6/6 mutantes |
| FASE-A | 5 | 5 | READ_OK | publicado; `decisiones.md` (P16, dueño del consentimiento) |
| FASE-B | 11 | 11 | READ_OK | publicado; 8 mutaciones con exit code de pytest **y** wiring |
| FASE-C | 13 | 13 | READ_OK | publicado; 9/9 rojos por el guard y 9/9 restaurados por sha256 |
| FASE-D | 17 | 17 | READ_OK | publicado; 6/6 por causa correcta, árbol intacto por sha |
| FASE-E | 13 | 13 | READ_OK | publicado; 8/8 mutantes; `cierre_documental.py` y `rectifica_sello.py` (autores de sellos) |
| FASE-E2E | 11 | **10** | READ_OK | **1 retenido sin versionar por decisión declarada**: `captura_stdout.txt` (S-E2E-6). Su sha sigue casando con el control |
| FASE-F | 14 | 14 | READ_OK | publicado; 9/9 mutantes; `credential_status.json` deja la revocación como afirmación del operador |
| FASE-G | 12 | 12 | READ_OK | publicado; `wiring_report.json` + 7/7 mutaciones |
| FASE-H | 37 | **35** | READ_OK | 2 `.pyc` de `__pycache__` generados; **4 crudos retenidos** en `descartados_por_superposicion_de_corridas/` (versión = retención deliberada); 2 preflights preservados por sha |
| PUESTA-AL-DIA-2026-10-06 | 5 | 5 | READ_OK | ajeno al plan (otro dueño), commiteado en `c996e47` |
| REVISION-2 | 2 | 2 | READ_OK | anclajes del 2026-09-19, leídos como historia |
| **Total** | **153** | **150** | — | **0 ABSENT, 0 READ_ERROR**; la diferencia 3 = `captura_stdout.txt` + 2 `.pyc` |

También se verificó el árbol de salida de la corrida: **70 archivos** en `output/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/`,
misma cantidad que declara `inventario_post_corrida.json` (`errores: []`, `faltantes_declarados: []`).

**Árbol git al abrir VERIFY:** `HEAD == origin/master == 21ade6c`, 13 rutas sin trackear (12 `briefing/` + `captura_stdout.txt`),
ambas exclusiones ya declaradas por sus fases. Sin secretos impresos: las lecturas de la corrida se hicieron por campos
nombrados, no por volcado de `.env` ni de valores.

## 2. Tarea 2 — dictamen por AC

La matriz completa con evidencia por símbolo/ruta está en `certificacion.json`. Resumen:

| Dictamen | ACs |
|---|---|
| **SUPERADO con pata E2E** | AC9 (vocabulario de 5 estados observado en vivo), AC11 (los cuatro revisores por el resolvedor), AC12 (rama publish con sha y conteo), AC15 (7 fases con mutación), AC17 (el control es el artefacto), AC19a (huella de plugin observada sin producir botón), AC20 (tres puntos en vivo) |
| **SUPERADO OFFLINE** | AC1, AC2, AC3, AC4, AC7, AC8, AC13, AC14, AC16 |
| **OFFLINE PARCIAL con deuda vigente** | AC5 (la barra 0,3 de `NEW_HOTEL_THRESHOLDS` sigue sin gobernar la ruta; dueño C-D, S-D4) |
| **NO EJERCITADO** | AC19b (diferido a maestro §6 con dueño) |
| **FALLA en régimen E2E** | **AC6** y **AC10** (ver §3) |

### 2.1 Las tres obligaciones de la revisión 2

**(i) AC20 y el par readiness/veredicto.** AC20 se cumplió en sus tres puntos. El par peligroso **no se repitió**: la
corrida viva da `READY_FOR_PUBLICATION` con 11 PASSED + 2 WARNING y veredicto **no** bloqueante, mientras el baseline
del 2026-09-19 daba READY + `BLOQUEADO` + ZIP suprimido. Medido el mecanismo, no el síntoma: `readiness_report` se
calcula en `main.py:3014` a partir de los gates y el veredicto del Tribunal en `main.py:3311`; **los dos vocabularios
nunca se cruzan** (hallazgo V-6). `exit_code == 0` no interviene en ninguno de los dos cálculos y no se usó como
argumento.

**(ii) AC1/AC2/AC3/AC6 y el verde vacuo.** Declarado con su medida: `coherence_validation.json` → `whatsapp_verified`
`passed=true, score=1.0, message "No hay asset de WhatsApp button"`; stderr de la corrida → `[RC1] whatsapp_button:
ninguna brecha candidata ['whatsapp_conflict'] presente en opportunity_scores`; `pain_ledger.json` → 13 pains, ninguno
de WhatsApp. Su régimen propio es OFFLINE y **NO EJERCITADO en E2E no es un fracaso, es un límite**. Con la salvedad
que modifica AC6: el ZIP **sí** llevó un destino de WhatsApp al cliente, por una puerta que no es el botón (§3.1).

**(iii) Comparación contra el baseline, no contra la expectativa.** Tabla completa en `certificacion.json
.comparacion_baseline`. Resumen: veredicto `BLOQUEADO → APROBADO-CONDICIONAL-PENDING-ONBOARDING`; tier `B → B+` con
`first_floor_rule` aplicado; `reviewer_reports[].findings` ausente → presente; `package_evidence` en supresión → en
publicación; coherencia 0.8967 con bloqueo por `whatsapp_verified` → 0.9172 con cero checks en error. **El baseline no
tenía `wa.me` en el paquete** (no se generó `local_content_page`) y su `IMPLEMENTATION_ORDER` no es comparable porque
`suppress()` lo borró (F-P4.9, deuda vigente con consecuencia de certificación).

## 3. Los dos ACs en FALLA

### 3.1 AC6 — un destino de WhatsApp fabricado fuera del contrato viaja en el ZIP publicado

`ASSETS/local_content_page/contenido_local__20261007_093402.md` publica `https://wa.me/6063146139` en las líneas
**73, 147, 221, 295 y 369**. El número es el **teléfono GBP**: `audit_report_20261007_093348.json` registra
`gbp.phone = "(606) 3146139"`, `validation.phone_web = null` y `validation.whatsapp_status = "estimated"`. El canal
verificado como WhatsApp **no existe**: la presencia del canal es `presence_evidence_kind: plugin_fingerprint`
(`css_class:joinchat joinchat--left joinchat--btn`), sin `href` `wa.me` ni número.

Causa por símbolo: `modules/asset_generation/local_content_generator.py:528-530` (`_conclusion`) y `:557-559`
construyen `f"https://wa.me/{phone_clean}"` desde `hotel_data.get("phone", "")`, siendo `phone_clean` el resultado de
`re.sub` sobre el teléfono (deja solo lo que no es dígito ni signo más) seguido de `lstrip` del signo más inicial — es
decir, el número normalizado **desde el teléfono**, sin ninguna otra validación de canal. El módulo **no** importa `whatsapp_contract`, no consulta `confidence` ni `presence_evidence_kind`
(medido por grep del archivo). AC6 exige "sin sustitución por `phone_web`" y "destino de botón igual al canal verificado
normalizado": aquí el destino WhatsApp sale de un teléfono de otro canal y sin gate de confianza.

Atribución medida: **preexistente al plan**. `git log --since=2026-09-18 -- modules/asset_generation/local_content_generator.py`
está vacío. Lo que cambió en esta corrida es que el asset **sí** se generó (en el baseline no existe `local_content_page`).
Dueño: `asset_generation`. Disparador: sesión de recuperación autorizada. No se tocó aquí (L-V.4).

**Compañero del mismo hallazgo (V-5):** `modules/commercial_documents/templates/propuesta_v6_template.md:252` renderiza
`WhatsApp: ${hotel_phone}` dentro del bloque **CONTACTO de IA Hoteles**, es decir el teléfono del hotel publicado como
WhatsApp de la agencia. Idéntico en el baseline (`02_PROPUESTA_COMERCIAL_20260919…:336`) y en la corrida viva
(`:330`). Dueño: `commercial_documents` (plantillas).

### 3.2 AC10 — IMPLEMENTATION_ORDER con las tres secciones de tarea vacías

El miembro `IMPLEMENTATION_ORDER.md` del ZIP publicado (2.586 caracteres) tiene **vacías** las tres secciones de trabajo:
entre `## 📋 ORDEN DE IMPLEMENTACIÓN`, `## 🔗 GUÍA DE RELACIONES ENTRE ARCHIVOS` y `## ✅ CHECKLIST DE IMPLEMENTACIÓN`
no hay ninguna línea antes del siguiente separador; **no existe ningún `### N.`** ni ninguna ruta emparejada. Las 13
rutas reales aparecen solo bajo "ASSETS ADICIONALES (fuera del catálogo CORE/GEO)" con la fórmula repetida
"Asset adicional sin par conocido. Revisar contenido para determinar propósito."

Causa por símbolo: `AssetResponsibilityContract.CORE_TO_GEO_MAP` (`asset_responsibility_contract.py:94-98`) casa **tres**
nombres canónicos (`hotel_schema.json`, `faq_schema.json`, `boton_whatsapp.html`), mientras `DeliveryPackager` pasa
`core_assets`/`geo_assets` con los basenames timestamped (`ESTIMATED_guia_optimizacion_20261007_093402.md` y compañía).
`get_implementation_order(...)` devuelve vacío y el resto cae en `unknown_assets` (`:326-329`). Atribución: **preexistente**
(`git log --since=2026-09-18 -- modules/geo_enrichment/asset_responsibility_contract.py` = vacío).

Lo que esto le dice al proceso, no solo al producto: **L-T4A.5 confirmado en vivo**. FASE-E certificó AC10 "con el writer
real" y su arnés pasó nombres del catálogo; la rama de producción con nombres reales nunca estuvo cubierta. El verde
offline era cierto y aun así el paquete entregado incumple el contrato. Y el revisor que debía verlo no lo ve:
`revision_assets.json` publica `implementation_order_check = {"status": "OK", "source": "zip"}` — registra la **fuente**
del documento, no que el orden esté vacío. Dueños: `delivery` + `geo_enrichment` + `tribunal` (Bot 3). AC10 sí cumple en
su otra pata: manifiesto coherente con el `namelist()` (57/57, tamaños exactos).

## 4. Tarea 3 — triaje, deudas y límites

Bloque completo en `certificacion.json .triaje`. Lo sustantivo:

- **F-P4.1 recalificado, no reescrito.** El informe de P4 (2026-09-14) lo describía como "stub de ~470 bytes con
  secciones vacías". E corrigió la formulación (con assets planificados el orden trae `### N.`; sin assets no hay archivo).
  Medido hoy por VERIFY: en la corrida real el archivo **existe y mide 2.586 bytes**, y **aun así** sus secciones de tarea
  están vacías. El defecto sobrevivió a ambas correcciones cambiando de unidad: ya no es tamaño, es contenido. Queda en
  FALLA vía AC10.
- **F-P4.2 confirmado curado en su cláusula literal:** en la corrida los cuatro revisores leyeron sus insumos por el
  resolvedor (`review_inputs.source = snapshot`, `read_status OK`) y no hubo CRITICAL inflados (`critical_count 0` en los
  cuatro). Su re-enfoque vive en AC11 y se dictamina SUPERADO.
- **F-P4.3 reabierto por su mismo ID**, sin duplicar ni reescribir `evidence/FASE-P4/informe-observacion.md §3`. Su
  condición de contorno cambió de signo (el hotel ya no produce el pain y la coherencia pasa con 0.9172), pero el
  mecanismo que señalaba — un check de severidad `error` decidiendo bloqueo por un campo que la ruta de datos no carga —
  **no está gobernado**: el transporte de contacto sigue sin ruta. **Cierre de la causa original: NO CERTIFICADO por
  VERIFY**, porque la muestra no tiene el caso. Dueño: Generación/orquestación (maestro §6).
- **F-P4.5 confirmado en estado documental:** revocación acreditada solo como afirmación del operador (2026-09-18), resto
  `PENDIENTE-SIN-EVIDENCIA-OPERATIVA` (S-F6). Y S-E2E-14 sigue abierto: la propia fila F-P4.5 de `10-analisis` publica un
  fragmento de credencial real que el patrón del gate no caza.
- **F-B y F-E mantienen su diferimiento con la condición escrita** en maestro §6. AC19b es la cara visible de F-E y sigue
  NO EJERCITADO.
- **S-E2E-4 dictaminado aquí (era de VERIFY):** el ZIP se publicó con un revisor recomendando `DEVOLVER-PRUEBAS`. **No es
  un defecto de esta corrida y la formulación de S-E2E-4 es una categoría equivocada:** `DEVOLVER-PRUEBAS` es un valor del
  vocabulario de **recomendaciones** (`outcome.py:16 RECOMMENDATION_RETURN_TESTS`) y `DEVOLVER-CORRECCIONES` es el del
  vocabulario de **veredictos** (`judge.py:27`, y sí está en `BLOCKING_VERDICTS`, `judge.py:46`). La elevación exige
  `verified_critical` o `verified_block` (`judge.py:511`); el Bot 4 emitió `critical_count: 0`. Consecuencia que sí debe
  escribirse: **un revisor que recomienda devolver pruebas no puede, por contrato, detener la entrega**. Es límite del
  Tribunal, no fallo de AC12, y la frase de S-E2E-4 va al sello de RELEASE como errata (V-7).
- **Deuda E-1 / S-H2 vigente:** el anclaje por `run_id` no cubre los JSON timestamped (`pain_ledger`, `gate_report_*`,
  `delivery_quality_report`, `proposal_asset_matrix`, `financial_scenarios`); Bot 1 y Bot 3 usan glob local. No viola la
  letra de AC11 pero acota la trazabilidad multi-run. Dueño: H/RELEASE.

**Ocho hallazgos nuevos** con dueño y disparador en `certificacion.json .hallazgos_nuevos` (V-1 … V-8). Ninguno se cerró
en esta sesión.

**Límites de la muestra** (L-R.4): un hotel y una corrida. Nada aquí certifica otra rama, otro tier, otro proveedor de
LLM ni otro estado de red. La medición IAO se perdió con el `LLMMentionChecker` caído (S-E2E-1): `providers_used` no
existe en el `audit_report` de hoy y **sí** existía en el baseline; el prompt de E2E pedía además una imposibilidad
(S-E2E-2). Un fallo de red no probó ausencia de canal (L-PF6).

## 5. Mediciones propias de VERIFY, incluidas dos falsas alarmas desactivadas midiendo

1. **"Using defaults" en `logs/` no es de esta corrida.** `logs/fase_e2e_v4complete.log:159` dice
   `Using defaults (no fresh onboarding data found)` y habría tirado AC14. Medido: el archivo es del **2026-09-11** y su
   URL es `https://www.hotelsalentoreal.com/` (líneas 84 y 316), otro hotel y otro mes. Se descartó por identidad y
   fecha, no por suposición. La corroboración viva de AC14 es `captura_stdout_saneada.txt:157`
   ("Onboarding data loaded: 4 campos confirmados"), coherente con los cuatro campos del `_FIELD_MAP`.
2. **Bot 4 sin tipo en el acta, confirmado en el artefacto.** El hallazgo del acta lleva `severity` y `description` pero
   no `finding_type` porque el revisor escribe la clave `type` (S-E2E-3): AC20(ii) se cumple en la causa, no en el tipo.
3. **Cuatro cláusulas certificables, seis evaluadas.** `clauses P6.2` y `P6.5` siguen `NOT_EVALUABLE` mientras
   `alignment_reviewer` y `honesty_reviewer` emiten reporte con hallazgos: la acta certifica 4 cláusulas y divulga 4
   revisores; leer `clauses_evaluated: 6` como seis verificaciones es un error de población (V-8, refuerza la corrección
   ya registrada en AC12).
4. **La ausencia fantasma con HTML visible sí se observó en vivo y se gobernó:** `pain_ledger.json` registra
   `no_org_schema` con `status: VERIFIED_IN_SITE`, severidad bajada a LOW y `evidence_refs:
   ["site_verification:org_schema:exists"]`, contra un `org_schema` real con propiedades leídas del ápice. Es el caso que
   AC1 perseguía, ocurrido por otra vía (no por WhatsApp), y no se promueve a SUPERADO EN E2E de AC1: la rama del AC sigue
   sin ejercitarse.

## 6. R2 — presupuesto y auto-reporte

`evidence/FASE-D/measure_iterations.py` pide el transcript del cliente y su acceso sigue denegado: **FUERA DE SERVICIO
(R2.1)**, con auto-reporte por unidad separada, como en E, F, H y E2E. Unidad declarada: invocaciones de herramienta de
esta sesión. Recuento propio al cerrar el corte documental: **≈90**, por encima de la referencia de 60 del prompt. Es
recuento, no medición por instrumento, y se declara como checkpoint **sin partir la fase ni delegar nada** (executor
§4.6: FASE-VERIFY no delegable — ningún `Agent`/`Explore` en esta sesión).

## 6b. Conteo de la sesión, con su comando y su momento

- `git status --porcelain -uall | grep -v "briefing/"` → **12** rutas, de las cuales **11 versionables**: las 12 incluyen
  `FASE-E2E/captura_stdout.txt`, que sigue excluido por decisión de S-E2E-6.
- El registro se escribió con **`--archivos-mod 11`**, el dato medido **antes** de invocar al escritor (noveno precedente
  del mismo mecanismo en este plan: C, D, F, H y E2E).
- Después del escritor y del índice: `git status --porcelain -uall | grep -v briefing/ | grep -v captura_stdout.txt` →
  **15** rutas versionables. El delta es 11 → +2 del propio `log_phase_completion.py` (`docs/contributing/REGISTRY.md` y
  `docs/contributing/.last_doc_phase.json`) → +2 del índice regenerado por su escritor (`.opencode/LECCIONES-INDEX.md` y
  `.opencode/lecciones_index.json`). La cifra del registro queda en 11 porque el escritor es **aditivo**: re-correrlo
  apilaría una fila duplicada, así que la corrección 11 → 15 viaja al sello de RELEASE con las erratas S-F7, S-H11 y la
  de E2E (18 → 26).
- Los 12 `briefing/` siguen sin versionarse, por decisión declarada del plan.

## 6c. Validaciones ejecutadas, con su código leído sin tubería

| Validación | Resultado |
|---|---|
| `build_lesson_index.py` + `--check` | regenerado y **fresco (344 IDs), EXIT 0** |
| `log_phase_completion.py --fase FASE-VERIFY --fecha 2026-10-07 --archivos-mod 11 --tests 0 --check-manual-docs` | `(R) Fase registrada exitosamente` y auditoría documental **`No se detectaron gaps`** (REGISTRY sin GAP); ejecutado **una** vez |
| `validate_lesson_capitalization.py` | **EXIT 0**, `[OK]` forma y trazabilidad (declara que **no** verifica pertinencia) |
| `validate_document_integration.py` | **EXIT 0**, `All checks passed` |
| `run_all_validations.py --quick` | **13/13, EXIT 0** al cerrar (tras gobernar `[9/13]` y tras el escritor) |
| `[9/13] Plan Citations` | cayó con **4 documentos** por citas numéricas que **yo introduje**; se gobernó **convirtiendo cada cita a su símbolo** (`check_publication_readiness`/`TribunalJudge`, `judge.VERDICT_RETURN`/`BLOCKING_VERDICTS`, `outcome.RECOMMENDATION_RETURN_TESTS`, `LocalContentGenerator._conclusion`/`_build_internal_links`, `AssetResponsibilityContract.CORE_TO_GEO_MAP`, `whatsapp_contract.READ_OK/READ_ABSENT/READ_NOT_READ`), **no** con `--update-baseline`. Resultado: `745 citas historicas, 0 nuevas y 0 crecimientos`, inventario de 81 archivos intacto. Los números de línea quedan donde deben: en la evidencia de esta carpeta, en `CHANGELOG.md` y en `docs/GUIA_TECNICA.md` |
| Regresión | **no ejecutada**: VERIFY tiene prohibido correr pytest; el árbol de producto no cambió (los 10 `source_hashes` casan con disco), así que no hay deuda de regresión abierta por esta fase |

## 6d. Error propio de esta sesión, declarado con su recuento final

Al escribir los dos entregables con la herramienta de escritura, el contenido salió corrompido en tres formas:
**cinco caracteres cirílicos** en `certificacion.json` (cuatro U+043E y uno U+041E, en lugar de la `o` latina dentro de
palabras españolas), **cuatro seudonúmeros** en ese mismo archivo (`ó` sustituida por el dígito 6: `pro`, `decisi`,
`alcanz`, `modific` + el dígito) y **una secuencia con barra invertida partida en un salto de línea** en el snippet de
`re.sub` de §3.1, que quedó roto y se reparó describiéndolo en palabras. Este informe también salió con un cirílico y un
seudonúmero más. Ninguna marca es visible al leer: el JSON **parseaba igual**, el `--quick` no recorre `evidence/`, y el
eco de la consola cp1252 imprime los caracteres extraños como sustitutos.

Se detectaron **midiendo, no releyendo**: `json.load` + barrido de puntos de código no ASCII (se imprimen los
**codepoints**, nunca el glifo, que aborta el bucle por cp1252) + `grep -oE` de letra-múltiple-6 excluyendo los
identificadores legítimos del proyecto (`AC6`, `PF6`). Estado final medido tras reparar: **0 cirílicos/CJK, 0
seudonúmeros, 0 CR** en ambos archivos y JSON válido.

**Y el barrido se mordió la cola, declarado aquí:** la primera pasada de reparación reescribió también **la prosa que
documentaba la corrupción**, así que dejó esta sección afirmando «tres `o` cirílicas» y «dos palabras con … (`probó`, …)»
— descripciones que ya no contenían lo que describían. La segunda pasada separó las dos cosas: **el archivo se repara
por codepoint y la nota se redacta nombrando los codepoints, nunca reproduciendo el carácter dañado.** Lección para
cualquier artefacto generado con prosa española y literales de escape: verificar codificación e integridad de las
cadenas **en el mismo paso en que se escribe**, no solo que parse. El barrido final es posterior al último `--quick`
(13/13, EXIT 0) y tocó únicamente archivos de esta carpeta, que no son corpus de los validadores.

## 7. Cierre documental

- Lecciones: **sin lecciones nuevas de producto** y **dos confirmaciones medidas** de lecciones existentes (L-T4A.5 en
  AC10 y L-VUP-17 en toda la matriz), más una de proceso que ya estaba en memoria y volvió a aplicar (un "rojo" que era
  evidencia de otro hotel). Registro en `10-analisis-post-implementacion.md §Lecciones` y en `00-lecciones-capitalizadas.md`.
- CHANGELOG bajo `## [Sin publicar]` (fechar una release es acto de RELEASE).
- Sin commit, push, tag, QMind write-back ni `DOMAIN_PRIMER` (no autorizados). Erratas y checkpoints al sello de RELEASE.
- **Corte R2 documental, declarado por separado:** la fase termina en "listo para revisión"; la autorización de RELEASE
  sigue siendo acto de otra sesión.
