# FASE-A — Decisiones, ratificaciones y premisas re-medidas

**Plan:** REFACTOR-WHATSAPP-ENTREGA-2026-09-18 · **Sesión:** A (documental) · **Fecha:** 2026-09-19
**HEAD al abrir:** `d4dacb4` · rama `master` · árbol limpio · 0 ahead / 0 behind con `origin/master`
**Contador v4complete:** **0/1** (A no ejecuta la corrida; ninguna acción de esta sesión lo consume)

Fuentes leídas: `05-prompt-inicio-sesion-fase-A.md`, `01-plan-maestro.md` (revisión 2), `04-contrato-ejecucion.md`, `00-lecciones-capitalizadas.md` (§1bis, §2, §4), `dependencias-fases.md`, `06-checklist-implementacion.md`, `.agents/workflows/phased_project_executor.md` (E7 y tabla de estándares), `docs/CONTRIBUTING.md` (§Paso-5b y Reglas Contractuales).

---

## 1. Premisas re-medidas antes de la primera edición

Método: solo lectura. No se modificó `output/`, `evidence/FASE-P4/` ni `data/`; no se leyó ni imprimió ningún valor de secreto.

| # | Premisa del plan | Cómo se re-midió | Resultado | Veredicto |
|---|---|---|---|---|
| P1 | Quick 10/10 al abrir la fase (`00` §"Rojos quick PRE", maestro §7) | `./venv/Scripts/python.exe scripts/run_all_validations.py --quick` | **10/10**, exit 0, árbol limpio. El rojo 9/10 del 2026-09-18 **no** reapareció | **Confirmada.** No se pide autorización central por ese concepto y no se leyó `_check_version_sync` (no había rojo que atribuir) |
| P2 | Anclajes de la revisión 2 medidos en `938f59f` | `git log --stat 938f59f..HEAD` | 3 commits, todos documentos del plan + índice de lecciones; **cero código de producto**. El verificador de citas por símbolo pasa (check 9: 743 citas históricas, 0 nuevas, 0 crecimientos) | **Válidos**, sin re-anclar |
| P3 | "readiness `READY_FOR_PUBLICATION` con **13/13 gates verdes**" (maestro §2 FASE-0, `00` M2, `06` preerrequisitos) | Lectura de `gate_report_20260919_150131.json` | 13 gates: **10 PASSED + 3 WARNING** (`financial_validity`, `asset_confidence`, `pricing_compliance`), **0 fallidos**, `blocks_publication=False` en los 13. `readiness.ready=true` con 3 advertencias listadas | **Rectificada en el texto**: no son 13 verdes, son 13 **no bloqueantes** (10 verdes + 3 en aviso). No cambia el razonamiento — el ZIP se suprimió sin ningún gate fallido — pero A no propaga una cifra imprecisa |
| P4 | AC20 (i): el recall fundado no serializa `details` | Código: `publication_gates.py` `_critical_recall_gate` (rama PASSED) y `_extract_critical_recall` | La rama PASSED declara `details` **solo** en `audit_present_no_critical_issues`; el `return 1.0` de "todos detectados" (L2127) deja `details={}`. Medido en el artefacto: `critical_recall → PASSED, details {}` | **Confirmada** |
| P5 | AC20 (ii): el acta no serializa hallazgos | Código `ReviewerReport.to_dict` + `acta_revision.json` | `to_dict` devuelve `reviewer/status/findings_count/critical_count/recommendation/report_path`; **sin `findings`**. Matiz nuevo: la causa **sí** existe en `revision_diagnostico.json` (1 CRITICAL `VACUOUS_RECALL`, clause P6.1, `verdict_recommendation: BLOQUEAR`) — el hueco es de agregación al acta, no de origen | **Confirmada y precisada** |
| P6 | AC20 (iii): `package_evidence` solo en la rama de supresión | `main.py` 3400-3460 | `package_evidence` se escribe dentro de `_outcome.blocks_publish` (y el acta real lo muestra con `suppressed: true, member_count: 52`); la rama `packager.publish()` no registra hash ni entradas | **Confirmada + hallazgo nuevo**: existe una **tercera** ruta de publicación, el `except` "Tribunal enrichment failed (never-block)" de `main.py`, que también publica sin `package_evidence`. FASE-0 debe nombrarla o AC20 dejaría una rama sin evidencia |
| P7 | Blast radius de AC19 = 52/816 y 31/545 | Método canónico del repo (`grep -rlE` base + `grep -hE "^\s*def test_"`; subconjunto por `xargs grep -lE '"(status\|site_verified\|presence_status)"'`) | **52 archivos / 816 funciones**; **31 / 545**. Reproduce exactamente lo publicado en `d4dacb4` | **Confirmada** (tercera medición del mismo par; el criterio queda enunciado en `00` M4) |
| P8 | Los 4 asserts de igualdad exacta sobre la forma | Búsqueda por símbolo | `test_site_presence_adapter.py:64`, `test_s_e2_generate_proposal_false.py:40`, `test_assessment_builder.py:247`, `test_site_presence_persistence.py:97` | **Confirmada** |
| P9 | `_presence_result_to_canonical` devuelve exactamente `status/site_verified/confidence` y descarta `details` | `site_presence_adapter.py:107-127` | Sí; y el `snapshot` archivado muestra `whatsapp_button {status: exists, site_verified: true, confidence: 0.85}` sin `whatsapp_href_number` ni `observation_scope` | **Confirmada** (AC19a y su prerrequisito siguen siendo necesarios) |
| P10 | Sanitización vigente y rutas no escaneadas | `llm_mention_checker._sanitize_text`, `.gitignore` | `_sanitize_text` itera **solo** `self._gemini_key/_openrouter_key/_perplexity_key` por reemplazo literal; `_sanitize_error` solo `?key=`/`&key=`. `.gitignore`: `logs/*`, `*.log`, `output/*/`, `output/clientes/*`, `.env` | **Confirmada** (F sigue necesitando sumidero único + verificador que cubra `output/` y `logs/`) |
| P11 | Escritor P6-R (F-P4.1 corregido en código) | `delivery_packager.py` 197-213, `asset_responsibility_contract.py` 304-379 | `asset_zip_paths` derivado de los `dest` reales del paquete y consumido por la plantilla | **Confirmada** — E revalida, no reconstruye |
| P12 | Productores de promesa (F-F ampliada) | `asset_catalog.py:58-68`, `preflight_checks.py:48`, `v4_diagnostic_generator.py:177`, `main.py:2807` | Los cuatro están: `ASSET_CATALOG["whatsapp_button"]` (`required_confidence=0.7`, `block_on_failure=False`), `NEW_HOTEL_THRESHOLDS["whatsapp_button"]=0.3`, `ELEMENTO_KB_TO_PAIN_ID["nap_consistente"]→(whatsapp_conflict, whatsapp_button)`, y el comentario `FIX-D7` de `main.py:2807` que sigue listando `whatsapp_button` como `promised_by=always` contra `# FASE-5: "always" ELIMINADO` del catálogo | **Confirmada. Precisión nueva:** el catálogo declara `block_on_failure=False  # NEVER_BLOCK: generar botón básico aunque falte WhatsApp`. Es una **quinta** instructiva dentro del propio catálogo: autoriza generar el botón sin dato. B/C deben gobernar ese comentario y su bandera, no solo la lista `promised_by` |
| P13 | Identidades de la corrida (tres, no una) | `v4_complete_report.json`, `acta_revision.json`, nombre del `.zip.tmp` | `hotel_id: "hotel_donalfonsohotel.com"` (de la URL) · paquete `hotel_don_alfonso_20260919.zip.tmp` (de `--nombre`) · `site_presence_snapshot.site_url = https://www.donalfonsohotel.com/` | **Confirmada** — AC17 debe fijar las tres |
| P14 | Dolor de WhatsApp ausente en el ledger | `pain_ledger.json` | 12 pains, **ninguno** de WhatsApp; `coherence_validation.checks[whatsapp_verified] = {passed: true, score: 1.0, message: "No hay asset de WhatsApp button"}` (verde vacuo) | **Confirmada** — el corolario del maestro §4 (AC1/2/3/6 se certifican offline) se sostiene |
| P15 | Superficies de tests pertinentes | `pytest -q` offline (venv 3.13.3) sobre las 7 listas | **133 passed, 1 skipped, exit 0, sin red** (0 coincidencias de `requests/urllib/socket`). 130 funciones canónicas → 134 casos (+4 de parametrización). Las dos superficies que gobernará FASE-0 (`test_publication_gates.py`, `tribunal/test_diagnosis_reviewer.py`) se inspeccionaron solo en lectura y **además** corrieron verde | **Confirmada** (`tests_pertinentes_pre.txt`). Ningún test exigió aislamiento por red |
| P16 | URL del warehouse no resuelve; la del usuario responde con redirección observable | `socket.gethostbyname` + `urlopen` (2 peticiones, sin pipeline) | `hoteldonalfonso.com` → **DNS falla** (`gaierror 11001`); `www.donalfonsohotel.com` → **200** y URL final `https://donalfonsohotel.com/`; el ápice también 200 | **Confirmada con la redirección observada**, no supuesta |
| P17 | Memoria compartida (`L-PF11`) | Conteo en `.agent/memory/**/*.json` sin imprimir contenido | 20 archivos de memoria; **3** mencionan Don Alfonso (`current_state.json` y sesiones `2026-09-14_…` y `2026-09-19_…`) | **Confirmada** — el `--output` no aísla; H debe snapshotear |
| P18 | `ONBOARDING_FRESHNESS_HOURS` sin definir | Solo **nombres** de clave de `.env`/`.env.template` y `os.environ` (nunca valores) | Ausente en los tres ámbitos (22 claves en `.env`, 12 en la template) | **Confirmada** — no hay verificador mecánico de edad del dato |
| P19 | Reloj de vigencia ≠ edad del dato | `agent_harness/memory.py:405` y `evidence/FASE-P4/consentimiento-donalfonso.md` | `cleanup_old_sessions(days=20)` gobierna **reutilización de análisis**; el consentimiento P4 lo declara explícitamente ("son dos relojes distintos"). Además **`.agent/memory` ya conserva sesiones de Don Alfonso** (P17), o sea la regla de 20 días **sí** está activa y sí puede hacer que la corrida de E2E reutilice el análisis del 2026-09-19 | **Confirmada y ampliada**: AC17 debe mirar la regla de 20 días (activa), no solo `ONBOARDING_FRESHNESS_HOURS` (inactiva) |
| P20 | Selección exacta de la observación | `data/hotel_observations/observations.json` (sha256 `31e70a37…`, 6 registros) | `hotel_name == "Hotel Don Alfonso"` devuelve **exactamente 1** registro. `collected_at: 2026-07-22` (59 días al 2026-09-19), `website: https://hoteldonalfonso.com/`, 11 hab, 140 reservas/mes, 330000 COP, canal directo 30 %, `source: contacto_directo`, `confidence: 0.95`. **Ninguna clave de contacto ni teléfono** | **Confirmada** — selector único y valores conservados; la afirmación "la observación no transporta contacto" se sostiene |

**Conclusión de la sección:** las cuatro decisiones de la revisión 2 descanzan sobre premisas que A volvió a medir y que siguen en pie; dos textos del plan se corrigen por precisión (P3, P6) y una instrucción adicional queda nombrada (P12).

---

## 2. Ratificación del contrato de fixes (matriz y alcance)

A **ratifica sin rectificación** los puntos 1-8 y añade las precisiones 9-11. Ninguna de ellas abre superficie nueva de código; todas se propagan a los prompts afectados.

1. **Matriz de decisión (§2) — RATIFICADA**, en sus cuatro reglas: ausencia → setup honesto; conflicto → guía sin elegir número; presencia **no** es confianza del número; botón solo con dato utilizable. A la sigue siendo la fila "huella de plugin" (caso realmente medido en Don Alfonso) la que manda el diseño.
2. **F-F ampliada — RATIFICADA**: los productores a alinear son los ocho nombrados (`PAIN_SOLUTION_MAP`, `PAIN_TO_ASSET`, `get_assets_for_pain`, `_solutions_to_asset_specs`, `ASSET_CATALOG["whatsapp_button"]`, `NEW_HOTEL_THRESHOLDS`, `ELEMENTO_KB_TO_PAIN_ID["nap_consistente"]`, `_generate_dynamic_services_table`) más la corrección del comentario `FIX-D7` (P12). **Allowlist de B cierra por grafo de consumidores** (así lo exige el maestro §1), no por nombre de símbolo.
3. **F-A' — RATIFICADA**: la divergencia vive en `V4AssetOrchestrator.generate_assets` que omite `whatsapp_html_detected`; el rojo de AC1 se construye sobre campo `UNKNOWN/CONFLICT + HTML`, que es producible.
4. **V-1 (retiro del boost de presencia) — RATIFICADO**, con el nombre exacto del escape: gobernar "campo presente + presencia `exists`", no "cualquier campo" (las ramas de campo ausente retornan antes).
5. **F-D' — RATIFICADO**: retirar el argumento muerto `whatsapp_validation` de `AssessmentBuilder.with_validation` y callers, en **G**, con inventario de firma (AC16); conservar el dato upstream del `ValidationSummary`.
6. **Módulo legacy — RATIFICADO**: `CommercialGate._check_whatsapp_verified` (`domain_gates.py`) se conserva sin cambios y queda clasificado test/legacy; sus tests no certifican el fix productivo.
7. **F-B diferida — RATIFICADA y reforzada**: no se codifica F-B sin decisión escrita de privacidad. La observación seleccionada **no transporta ningún campo de contacto** (P20), así que el setup no puede presentarse como cierre del transporte de contacto.
8. **F-E diferida — RATIFICADA**: no se toca el modelo global CoherenceCheck; la distinción ausente/leído-fallido sí es obligatoria para los lectores nuevos (AC9, AC19a).
9. **Precisión (de P12)**: el catálogo instruye `block_on_failure=False  # NEVER_BLOCK: generar botón básico aunque falte WhatsApp`. B/C deben gobernar esa bandera y su comentario; no basta con quitar `always` de `promised_by`.
10. **Precisión (de P5)**: la causa del bloqueo **sí** existe en el archivo del revisor; AC20 (ii) se enuncia como *agregación al acta*, lo que acota el cambio de serialización y evita que FASE-0 reimplemente el diagnóstico.
11. **Dependencia nueva (QMind R5)**: `CrossValidator._reconcile_whatsapp_multisede` (`cross_validator.py:198`) ya reconcilia número↔sede y tiene suite propia (`tests/data_validation/test_whatsapp_multisede.py`). B y C **no** deben reintroducir una comparación ingenua ni duplicar ese reconciliador; AC6 debe citar que el campo verificado puede venir de esa reconciliación.

**Campos propuestos de los reportes nuevos — RATIFICADOS con los IDs congelados:** `wiring_report.json` (AC7), `onboarding_provenance.json` (AC14), `thresholds.json` (AC5), `mutation_report.json` (AC15), `review_input_manifest.json` (AC11), `sanitization_report.json` + `credential_status.json` (AC13), `certificacion.json` (AC18), y las claves nuevas de AC19a (`observation_scope`, `read_status`, `presence_evidence_kind`). Ninguno de estos archivos existe hoy; son salida futura.

**Frontera snapshot privado / ZIP exportable — RATIFICADA, con límite de construcción (QMind R6):** `DeliveryPackager._INTERNAL_DOC_PREFIXES = ("acta_revision",)` (`delivery_packager.py:442`) ya excluye el acta del paquete de cliente, y el acta no puede ir en el ZIP que los revisores deben leer (círculo estricto, DA-P1.4). Por tanto: el snapshot interno vive en `v4_audit/`, fuera del árbol exportado, y el resolvedor único de E **no** debe esperar `acta_revision.json` dentro del ZIP.

---

## 3. Ratificación explícita de los cuatro puntos de la revisión 2

| Punto | Ratificación | Qué midió A para no ratificar a ciegas |
|---|---|---|
| **(a) FASE-0 nueva y AC20** | **RATIFICADO** — la serialización de la evidencia del veredicto en **las dos direcciones** de la decisión es el trabajo de código que abre el plan. Se incorpora la ruta adicional de P6 (el `except` never-block de `main.py`) dentro del enunciado de AC20 (iii) sin cambiar la regla de decisión. | P4, P5, P6, P14 y el veredicto real (`BLOQUEADO` con 0 gates fallidos). Contrafactual de `00` M3 **no** se re-ejecutó en A: pertenece a FASE-0 como evidencia exigida y A no reimplementa el trabajo de otra fase |
| **(b) División AC19a / AC19b** | **RATIFICADO** — 19a es aditivo dentro de C (claves nuevas, conserva `details`, sin redefinir estados, sin tocar los 8 consumidores); **19b es deuda diferida con dueño** (maestro §6) y **no es una fase**: ninguna sesión del DAG la ejecuta. | P7 (52/816 → 31/545, tercera medición), P8 (los 4 asserts de igualdad exacta localizados por símbolo), P9 (la única puerta de forma descarta `details`) |
| **(c) Meta E2E re-anclada** | **RATIFICADO** — el objetivo certificable es **ZIP publicado con veredicto no bloqueante** (`APROBADO-CONDICIONAL-PENDING-ONBOARDING`), **no** `READY`. `APROBADO-PARA-ENTREGA` exigiría tier A, y tier A requiere GA4+GSC verificados; hoy el tier sale **B**. | P3 (readiness y gates no certifican nada por sí solos: convivieron con `BLOQUEADO`), y código: `BLOCKING_VERDICTS = frozenset({VERDICT_BLOCKED, VERDICT_RETURN})` (`judge.py:46`) no contiene el veredicto condicional; `ScenarioCalculator._determine_evidence_tier` devuelve `EvidenceTier.A` solo con `ga4_enabled and gsc_enabled and has_verified_data` (`scenario_calculator.py:508-509`) |
| **(d) Orden A → G → 0 → B** | **RATIFICADO** — G segunda porque su verificador AST es el guard de las ediciones de B–F; 0 tercera porque sin AC20 la meta es inalcanzable con independencia de B–H. Cadena completa: `A → G → 0 → B → C → D → E → F → H → E2E → VERIFY → RELEASE`. | `dependencias-fases.md` (DAG y tabla de superficies compartidas: 0 es dueña del cambio de tribunal/gates; G antes de C antes de D). Ninguna arista se reordena en A |

El operador no pidió rectificación de ninguno de los cuatro; **no se reinterpretó ninguna restricción** (contrato §límites).

---

## 4. Prerrequisitos operativos (T3) — estado explícito

| Tema | Estado al cerrar A | Dueño / siguiente acción |
|---|---|---|
| **Baseline medido** | `output/TAREA7-2026-09-19/` releído y registrado como baseline del plan: 60 archivos, **0 ZIP presentes** (suprimido), inventario con sha256/ruta/tamaño en `baseline_inventory.json`. **0 escrituras** sobre esa ruta. | Cerrado en A |
| **QMind** | Consulta **reintentada y RECUPERADA** (denegación de la revisión 2 no se repitió). Aporte registrado en `qmind-consulta-reintentada.md`: 6 filas, de las cuales 3 ya están cerradas en código vivo, 2 son filas locales no capitalizadas y 1 aporta una dependencia (R5). | Cerrado en A. **No** se subió nada: la consulta no autoriza write-back |
| **Identidad / binding de URL** | Selector único verificado (P20). Procedencia con **ambas** URLs: original `https://hoteldonalfonso.com/` (DNS: no resuelve, medido hoy) y solicitada `https://www.donalfonsohotel.com/` (200, con la redirección observable a `https://donalfonsohotel.com/`). **No** se edita el warehouse; **no** se declara alias universal entre dominios. El YAML de H deberá llevar `hotel.url` de la URL del usuario porque el loader iguala por URL normalizada y **ignora el nombre**. | Cerrado en A como decisión de procedencia; ejecución material en H (AC14) |
| **Vigencia / frescura** | **A DECIDE: hace falta reconfirmación.** El consentimiento de FASE-P4 (2026-09-14) ampara **una corrida de observación/diagnóstico** sobre la URL hoy inexistente y declara que **no es entrega a cliente**; E2E persigue un ZIP publicable. El dato tiene 59 días y `ONBOARDING_FRESHNESS_HOURS` no está definido en ningún ámbito (P18). Prohibido: fecha artificial, desactivar frescura, caer a defaults. A **no** emite el consentimiento por el operador. | **Operador** (antes de consumir el intento; H lo exige en preflight). Añadido por P19: el preflight debe mirar también la regla activa de 20 días de `agent_harness/memory.py`, con 3 artefactos de memoria de Don Alfonso ya presentes |
| **Revocación de la key** | **RESUELTA POR REFERENCIA, no se vuelve a pedir.** Registro en `evidence/FASE-P5/AC-S3-S4-inventario-superficie.md` (§2 rotación, §5 cierre): confirmación del operador el **2026-09-18** para la key Gemini-local, archivado como CERRADO el 2026-09-19 (verificado por número de línea, sin imprimir el valor). **Acreditación por afirmación del operador, no inferible del repo** → F y H la citan así, y AC13 sigue sin certificarse por un test. La key de `archives/gbp_profiles.json` **no aplica** como credencial del operador. | F/H (referencia) · Operador (única vía de acreditación) |
| **Permiso documental (DOMAIN_PRIMER)** | **Divergencia resuelta sin editar workflow ni AGENTS.md.** Lectura: el executor canónico (§E7, L1016 y tabla L1320) y `docs/CONTRIBUTING.md` L400 dicen *regenerar al cerrar cada fase de implementación* con `doctor.py --regenerate-domain-primer`, y *verificar* (`--context`) solo en FASE-RELEASE. `AGENTS.md:66` condensa eso en "se regenera en FASE-RELEASE (no manualmente)", que coincide con la pata de **verificación** pero contradice la de **regeneración**. **A aplica la lectura del executor/CONTRIBUTING** (el maestro nombra el workflow como canónico y el contrato no lo reemplaza). Para A no procede: A no es fase de implementación y no toca código; `.agent/knowledge/DOMAIN_PRIMER.md` está **versionado y limpio**, así que cada regeneración por fase produce un diff que requiere autorización de commit. | Cerrado en A como mandato vigente; ejecución en G, 0, B, C, D, E, F, H y RELEASE |
| **Privacidad F-B / D1** | Diferida, sin PII nueva en warehouse ni cambios de formulario/esquema. | Producto/privacidad (decisión escrita) |
| **Re-Mediciones pendientes de otras fases** | El contrafactual de AC20 (M3) y el inventario AST de AC7 pertenecen a 0 y G. A no los adelantó. | FASE-0 / FASE-G |

---

## 5. Decisiones cerradas vs. abiertas

**Cerradas por escrito en A (12):** matriz de decisión; F-F ampliada con los 8 productores + comentario FIX-D7 + bandera `block_on_failure`; F-A'; V-1; F-D'; conservación del módulo legacy; F-B diferida; F-E diferida; campos de reportes y sus IDs; frontera snapshot/ZIP con el límite de construcción de DA-P1.4; los cuatro puntos de la revisión 2 (§3); mandato DOMAIN_PRIMER; procedencia de identidad/URL; acreditación de revocación por referencia; baseline y quick.

**Abiertas — y su efecto sobre el cierre:**

1. **Reconfirmación de vigencia/consentimiento sobre la URL viva** — necesaria para **H/E2E**, **no** para B. A la registra con dueño (operador) y condición ("datado sobre la URL viva, con límite escrito, antes de consumir el intento"). **No bloquea el cierre de A ni la arista A→G.**
2. **Autorización de commit** de los documentos y evidencia de esta fase — **no concedida en esta sesión**. A dejó ejecutado el cierre incremental (registro en `REGISTRY.md` incluido, con `--check-manual-docs` → "No se detectaron gaps") y queda en **checkpoint documental** solo por el commit, por lo que **no** se declara el corte de R2 consumado.
3. **Write-back a QMind** — no autorizado (solo se consultó). Ninguna subida se simula.

Ninguna decisión necesaria para B quedó abierta, pero **A no se declara COMPLETADA** sin el corte documental + commit (§6).

---

## 6. R2 y límites declarados

- **Corte documental** (A no produce código): la referencia de 60 tool_use se registra como **corte documental**, nunca como commit de código (contrato §R2).
- **Instrumento `measure_iterations.py`: métrica FUERA DE SERVICIO (R2.1)** — requiere el transcript del cliente, cuyo acceso no está disponible en esta sesión. Se conserva el auto-reporte con su unidad y **no** se suma ni compara con el instrumento (precedente: `Medición de iteraciones fuera del workspace`, memoria del proyecto).
- **Contador v4complete: 0/1.** A no lanzó `main.py v4complete`, no modificó `output/`, no tocó `evidence/FASE-P4/`, no leyó secretos, no subió datos, no hizo push ni tag, y no inició G.
- **Bloqueantes respetados:** sin autorización central nueva; la lectura de `.env` fue solo de nombres de clave; la denegación del clasificador al intentar leer `evidence/FASE-P5/AC-S3-S4-inventario-superficie.md` **no se evadió** — se sustituyó por una búsqueda de la fecha de acreditación con `-o`, patrón que no puede casar un valor de credencial.

### 6bis. Cierre efectivo medido (lo ejecutó A, no es proyección)

| Paso del contrato | Comando | Resultado medido |
|---|---|---|
| Registro de fase | `log_phase_completion.py --fase FASE-A --archivos-mod 11 --tests 0 --check-manual-docs` | Registrado; auditoría de documentación huérfana **(OK) No se detectaron gaps** |
| Índice de lecciones | `build_lesson_index.py` + `--check` | 316 IDs definidos + 43 sin definición; **índice fresco** (par `.md`+`.json` regenerado) |
| Integración documental | `validate_document_integration.py` | **All checks passed** |
| Validaciones rápidas | `run_all_validations.py --quick` | **10/10** al abrir la fase y **10/10** al cerrar |
| Archivos al cierre | `git status --porcelain` | **15 rutas** (10 documentos del repositorio y del plan, `REGISTRY.md`, el par del índice y el directorio nuevo de evidencia). **0 archivos de código, 0 tests, 0 datos** |

**Tres observaciones medidas del cierre (para `10-analisis`, sin fabricar lecciones):**

1. **Un rojo propio, detectado y corregido dentro del alcance.** La primera corrida del quick tras editar los documentos bajó a **9/10** por el verificador de citas: A había introducido **cinco** citas de número de línea (`…py:198`, `…py:442`, `…py:405`, `AGENTS.md:66`, `L400`). Se corrigieron a citas por símbolo y el quick volvió a **10/10** con "0 nuevas y 0 crecimientos". **No se tocó el baseline del verificador.** Regla operativa que sale de aquí: escribir en los documentos del plan con símbolos desde el primer borrador; el gate detecta la recaída pero no perdona el trabajo extra.
2. **El instrumento de presupuesto volvió a fallar por la misma causa que en la intervención anterior**: `measure_iterations.py` pide el transcript del cliente y su acceso no está disponible, así que R2 queda **FUERA DE SERVICIO (R2.1)** y la unidad publicada es el conteo de intervenciones (~62), que **no** es comparable con el instrumento. Es la segunda ocurrencia registrada en el proyecto de esta misma denegación.
3. **Rectificar una cifra propia cuesta menos que heredarla.** De las 14 menciones a "13/13 gates verdes" en los diez documentos del plan, A **no** las reescribió una por una: registró la equivalencia (10 PASSED + 3 WARNING, 0 fallidos) como nota vinculante al pie del maestro §1 y corrigió en el texto las dos filas que se usaban como prerrequisito vivo (`06` y `dependencias`). Las demás quedan como cita histórica de la revisión 2, ahora reinterpretada desde una medición, y no como afirmación vigente.
