# Análisis Post-Implementación — TRIBUNAL-OFFLINE-2026-09-09

> **Estado**: 🔶 6/9 sesiones ejecutadas — FASE-T1 ⚠️ + FASE-T2-A ✅ + FASE-T2-B ✅ + FASE-T2-C ⚠️ + FASE-T4-A ✅ + FASE-T4-B ⚠️ completadas (T1 con reserva: S-HF1 y corte R2.1 sin cerrar; D-T1.3 ✅ resuelta opción a; T2-C con reserva: desvío D-T2C-A1 — AC no-regresión régimen `True`; **T4-B con reserva: desvío D-T4B-A1 — el revisor no operaba sobre los artefactos reales, remediado R1–R9 el 2026-09-11; T4-A heredaba el mismo defecto de resolución, también corregido**)
> **Plan**: TRIBUNAL-OFFLINE-2026-09-09
> **Versión objetivo**: 4.76.0

---

## Resumen de Ejecución (llenar al cierre de cada fase)

| Fase | Sesión | Estado | Iteraciones | delegate_task | Notas |
|------|--------|--------|-------------|---------------|-------|
| FASE-T1 | 2026-09-10 | ✅ | ⚠️ sin medir (R2.1) | No | Juez + contrato de acta + integración main.py; auditada y corregida D-T1.1/D-T1.2 el mismo día |
| FASE-T2-A | 2026-09-10 | ✅ | ⚠️ sin medir (R2.1) | No | Bot 1: DiagnosisReviewer — trazabilidad pain_id, fuente declarada, recall vacuo S-I1; 10 tests verdes |
| FASE-T2-B | 2026-09-10 | ✅ | ⚠️ sin medir (R2.1) | No | Bot 3: AssetReviewer — cobertura por servicio, P12, IMPLEMENTATION_ORDER vacío; 12 tests verdes |
| FASE-T2-C | 2026-09-10 | ⚠️ | ⚠️ sin medir (R2.1) | No | Limpieza S-E2/S9 — NameError hoisted + presence_lookup corregido (dict+dataclass) + fósil V3 cerrado + 7 tests (+11 remediación D-T2C-A1 el 2026-09-11 = 18). Evidencia: `evidence/FASE-T2-C/`. Reserva: desvío D-T2C-A1 (auditoría 2026-09-11) — ver §Desvío registrado |
| FASE-T4-A | 2026-09-11 | ✅ | ⚠️ sin medir (R2.1) | No | Bot 2: AlignmentReviewer — protocolo PromiseExtractor + extracción LLM + clasificación determinista + S-C4; 28 tests verdes (incl. fix post-auditoría). **Nota 2026-09-11**: arrastraba el mismo defecto de resolución de `02_PROPUESTA_COMERCIAL*` que D-T4B-A1 (sobre el baseline real devolvía `MISSING_ARTIFACT` y veredicto BLOQUEAR); corregido por el resolutor compartido de la remediación de T4-B |
| FASE-T4-B | 2026-09-11 | ⚠️ | ⚠️ sin medir (R2.1) | No | Bot 4: HonestyReviewer — lee CG-* en 2 archivos (canónico + diagnóstico) + sobre-presentación vs tier + 3 escenarios; 7 tests de fase + 22 de remediación. **Reserva D-T4B-A1**: la fase certificó ✅ con 7/7 verdes sobre un fixture que no replicaba la ubicación real de la propuesta, así que el revisor no operaba sobre los artefactos del pipeline. Remediado R1–R9 el 2026-09-11 |
| FASE-E2E | — | ⬜ | — | Sí (v4complete) | Corrida Salento Real |
| FASE-VERIFY | — | ⬜ | — | No | Certificación AC1-AC16 |
| FASE-RELEASE-4.76.0 | — | ⬜ | — | Sí | Cierre + archivado |

---

## Matriz de Verificación de Hallazgos (llenar en FASE-VERIFY)

| # | AC | Expected | Real | Status | Artefacto | Clave |
|---|-----|----------|------|--------|-----------|-------|
| 1 | AC1 | `acta_revision.json` con `verdict` legible | — | ⬜ | `v4_audit/acta_revision.json` | `verdict` |
| 2 | AC2 | Tier B/C → condicional | — | ⬜ | `acta_revision.json` | `verdict` + `evidence_tier` |
| 3 | AC3 | `acta_revision.md` con 6 cláusulas P6 | — | ⬜ | `acta_revision.md` | secciones |
| 4 | AC4 | Una ruta de bloqueo, no cuarta | — | ⬜ | `main.py` | grep tribunal |
| 5 | AC5 | `revision_diagnostico.json` con `findings[]` | — | ⬜ | `revision_diagnostico.json` | `findings` |
| 6 | AC6 | Recall vacuo marcado | — | ⬜ | `revision_diagnostico.json` | `VACUOUS_RECALL` |
| 7 | AC7 | `revision_assets.json` con `coverage_by_service[]` | — | ⬜ | `revision_assets.json` | `coverage_by_service` |
| 8 | AC8 | `IMPLEMENTATION_ORDER.md` vacío señalado | — | ⬜ | `revision_assets.json` | `EMPTY_DELIVERY_TEMPLATE` |
| 9 | AC9 | `revision_alineacion.json` con `service_matrix[]` | — | ⬜ | `revision_alineacion.json` | `service_matrix` |
| 10 | AC10 | Promesa sin matriz → `PROMESA-SIN-MATRIZ` | — | ⬜ | test output | assertion |
| 11 | AC11 | `revision_honestidad.json` con `findings[]` | test-level: el acta se escribe y se re-leé con datos del baseline real | ⬜ **E2E + VERIFY** | `revision_honestidad.json` (no existe aún en `output/`) | `findings` |
| 12 | AC12 | CG-WHATSAPP-LEAD detectado | `cg_reference == "CG-WHATSAPP-LEAD"` sobre la **propuesta real** de la corrida FASE-D (`test_honesty_reviewer_retro_reales.py`); antes de la remediación fallaba por dos vías (D1 y D5) | ⚠️ **verificado a nivel test; falta el artefacto E2E** | `revision_honestidad.json` | `cg_reference` |
| 13 | AC13 | Acta + 6 cláusulas en output E2E | — | ⬜ | `acta_revision.json` | `clauses_evaluated` |
| 14 | AC14 | 4 reportes de revisión en `v4_audit/` | — | ⬜ | directorio | 4 archivos |
| 15 | AC15 | S-E2: `generate_proposal=False` sin NameError | ✅ T2-C | `evidence/FASE-T2-C/evidencia-final.md` | `test_site_presence_snapshot_initialized_before_proposal_gate` |
| 16 | AC16 | S9: `INVALID_MAPPINGS` pasa contrato | ✅ T2-C | `evidence/FASE-T2-C/evidencia-final.md` | `test_invalid_mappings_valida_contra_capa1` (preexistente) |

---

## Lecciones Aprendidas

### Lecciones capitalizadas de planes anteriores

| Lección | Fuente | Aplicación en este plan |
|---------|--------|------------------------|
| R2.2: Sin números de línea — citar símbolos | ESTABILIZACION §14.3 | Todos los ACs citan artefacto+clave, nunca `archivo:123` |
| R2.4: AC no legible en artefacto = ⚠️ | ESTABILIZACION §14.3 | Cada AC declara artefacto + clave; tests de serialización obligatorios |
| Contrato de acta estable ANTES de revisores | CONTEXT §10.3 (regla de dependencia fina) | T1 define contrato; T2/T4 lo consumen |
| Anfitrión real = `main.py`, NO `two_phase_flow.py` | CONTEXT §15.4.3 | T1 integra en `main.py` junto a `delivery_quality_report` |
| Veredicto alimenta UNA ruta de bloqueo existente | CONTEXT §15.4.3 / ROADMAP §7.2 | AC4 verifica que no se añade cuarta ruta |
| El tribunal NO reimplementa gates | CONTEXT §5 (regla arquitectónica) | NR4: grep verifica que no importa internals de `publication_gates.py` |
| Propuesta dinámica ya cerrada (v4.75.0) | CONTEXT §14.1 | T0 no está en scope; baseline es propuesta dinámica activa |
| Residuos S-HF1/S-I1/P12/S-C4 son alcance, no sorpresa | CONTEXT §15.4.9 | Distribuidos en T1/T2-A/T2-B/T4-A explícitamente |

### Lecciones nuevas de este plan (llenar mínimo 3 por fase)

#### FASE-T1 (2026-09-10)

| # | Lección | Fuente | Aplicación futura |
|---|---------|--------|-------------------|
| L-T1.1 | `proposal_asset_matrix.json` tiene formato v2.0 (`delivery_ready` + `entries[]`) distinto al formato legacy (`alignment.passed`). El Juez debe manejar ambos formatos para ser retro-compatible con corridas pre y post-hotfix. | Artefactos FASE-I vs FASE-D | T2-B (asset_reviewer) debe usar `delivery_ready` como fuente primaria, no `alignment.passed` |
| L-T1.2 | ⚠️ **Corregida en la auditoría.** La resolución por glob funciona sin hardcodear timestamps, pero los tests retro **solo ejercen la corrida FASE-I**: `FASE_D_DELIVERIES_DIR` está definido en `test_judge.py` y nunca se usa, así que el baseline FASE-D (Tier B real, `MANIFEST.json → quality_metadata.evidence_tier`) no está cubierto. Además `sorted(glob(), key=mtime, reverse=True)[0]` **no es reproducible**: `git checkout`, copias o restauraciones cambian el `mtime`. La fecha ya va embebida en el nombre (`gate_report_YYYYMMDD_HHMMSS.json`). | Releído `judge.py` + `test_judge.py` el 2026-09-10 | T2-B y T4-B deben ordenar por la fecha del nombre, no por `mtime`; ver seguimiento abierto |
| L-T1.3 | La integración never-block (try/except que produce `acta = None`) es correcta: el tribunal no puede romper v4complete. Los veredictos negativos alimentan la Ruta 2 existente sin añadir una cuarta ruta. | Diseño de T2-A/T2-B (revisores también never-block) | Todos los revisores deben ser never-block; el Juez consolida sus outputs |
| L-T1.4 | ⚠️ **Corregida en la auditoría.** En T1 solo **P6.2** queda `NOT_EVALUABLE` (requiere LLM y se difiere a T4-A). **P6.5** también queda `NOT_EVALUABLE` tras resolver D-T1.3 (opción a: primer piso → `first_floor_rule`, P6.5 liberada para Bot 4). El contrato de acta exige que un revisor declare su `clause` antes de escribir sobre ella. | Releído `_evaluate_p6_5` contra `05-prompt-...-T4-B.md` | **Resuelto (D-T1.3 opción a)**: primer piso vive en `first_floor_rule`; `P6.5` = honestidad NL (Bot 4) |

#### FASE-T2-A (2026-09-10)

| # | Lección | Fuente | Aplicación futura |
|---|---------|--------|-------------------|
| L-T2A.1 | El regex de extracción de `pain_id` del markdown debe manejar el formato `**pain_id:**` (bold+colon). El patrón inicial `pain_id[\`:\s]+` no capturaba el `*` de markdown bold. Se corrigió a `pain_id[\*\`:\s]+`. | Test `test_untraceable_pain_detected` (primer run: 0 findings; segundo run: 1 finding) | T2-B y T4-A deben manejar formatos markdown variados al extraer IDs de documentos comerciales |
| L-T2A.2 | La distinción recall fundado vs vacuo (S-I1) se certifica con test de fixture, no con corrida E2E. En la corrida real el gate ya serializa `details.critical_issues_count`, así que el finding `VACUOUS_RECALL` no aparece. El AC6 es test-level. | Plan maestro §T2-A (nota de auditoría 2026-09-09) | VERIFY debe documentar que AC6 se verifica via tests, no via output E2E |
| L-T2A.3 | El patrón never-block del Juez (T1) se replica naturalmente en Bot 1: `_load_json` retorna `None` sin excepción, los checks retornan listas vacías si el artefacto no existe. El veredicto final (`APROBADO`/`DEVOLVER`/`BLOQUEAR`) se computa sobre hallazgos, no sobre ausencia de datos. | Diseño de `DiagnosisReviewer` (mismo patrón que `TribunalJudge`) | T2-B y T4-A/B deben seguir el mismo patrón never-block |

#### FASE-T2-B (2026-09-10)

| # | Lección | Fuente | Aplicación futura |
|---|---------|--------|-------------------|
| L-T2B.1 | La detección de `IMPLEMENTATION_ORDER.md` vacío requiere dos niveles: 0 bytes (trivial) y plantilla stub (secciones ORDEN/GUÍA/CHECKLIST sin contenido por-hotel). El stub baseline pesa ~468 B, así que solo verificar `size == 0` es insuficiente. El detector cuenta líneas de contenido no-encabezado bajo secciones clave; si el total es ≤5, es stub. | Test `test_empty_implementation_order_detected` (primer run: stub de 468 B no detectado con check de 0 bytes) | T4-A/B que lean archivos de entrega deben manejar el caso "plantilla vacía" con heurística de contenido, no solo tamaño |
| L-T2B.2 | P12 se discrimina por la fuente declarada en el `message` del check `promised_assets_exist`, no por el `score`. Un `score=1.0` post-gen verificado es legítimo; `via catalogo_estatico` indica que el check corrió sin `generated_assets` (pre-gen). La detección busca substrings `via catalogo_estatico` y `via PROPOSAL_SERVICE_TO_ASSET` en el message. | Test `test_p12_catalog_source_detected` + `test_p12_generated_assets_not_flagged` | T4-B debe discriminar por fuente declarada en messages, no por valores numéricos de score |
| L-T2B.3 | La clasificación de assets genéricos requiere que el check de contenido lea el archivo real en disco (no solo metadata). El regex de hotel keywords (`hotel|hostal|boutique|...`) y breach keywords (`brecha|gap|problema|...`) busca en los primeros 1000 caracteres. El orden de checks importa: primero estimated-no-etiquetado (confidence < 0.9 sin prefijo ESTIMATED_), luego genérico. | Test `test_generic_asset_flagged` (primer run: asset con confidence 0.8 se clasificaba como unlabeled_estimated antes de llegar al check genérico) | T4-A/B que lean contenido de assets deben considerar el orden de checks y la interacción entre metadata y contenido |

#### FASE-T2-C (2026-09-10)

| # | Lección | Fuente | Aplicación futura |
|---|---------|--------|-------------------|
| L-T2C.1 | El `hasattr(obj, 'results')` como guard de tipo es frágil cuando el consumidor canónico es un dict. `normalize_site_presence()` retorna un dict con clave `"results"`, pero tres bloques en `v4_proposal_generator.py` usaban `hasattr(site_presence_report, 'results')` que siempre era `False` contra dicts. El fix dual (dict + dataclass) cubre ambos formatos sin romper tests existentes que pasan el dataclass directo. | S-E2: 3 bloques `presence_lookup` muertos desde FASE-SR-E | Al escribir guards de tipo, verificar qué formato retorna la fuente canónica; `isinstance(x, dict)` + `hasattr(x, attr)` en cascada cubre ambos mundos |
| L-T2C.2 | Un `NameError` latente puede sobrevivir meses si el consumidor está bajo un `except Exception` amplio. `site_presence_report` se asignaba solo dentro de `if generate_proposal:` pero se usaba fuera; el `try/except` en `delivery_quality_report` enmascaraba el error. El hoist de la asignación antes del bloque condicional es la cura mínima que no altera el régimen `True`. | S-E2: `main.py` — variable asignada en bloque condicional, consumida fuera | Cuando se inicializan variables dentro de bloques condicionales, verificar todos los consumidores aguas abajo (fuera del bloque); los `except Exception` amplios son máscaras de NameErrors |
| L-T2C.3 | S9 ya estaba certificado por tests existentes (`test_invalid_mappings_valida_contra_capa1` en `test_service_identity_registry.py`). El fósil V3 (`ASSET_TO_PAIN_ID["monthly_report"] = "no_faq_schema"`) fue corregido por FASE-A y solo sobrevivía como docstring en `service_identity.py`. No se necesitó código nuevo para S9 — solo verificación con `grep` y declaración de cierre. | S9: `INVALID_MAPPINGS` certificado sin cambios de código | Antes de escribir tests nuevos, verificar si el contrato ya está fijado por tests existentes en otros directorios; el censo de `test_service_identity_registry.py` ya cubría los 14 registros |
| L-T2C.4 | Un fix que reactiva código muerto cambia comportamiento de producción y por tanto NO es «sin regresión»: exige un delta fijado por test contra el símbolo real. Los 7 tests originales de S-E2 re-implementaban la lógica del lookup o leían `main.py` como texto — pasaban sin tocar `_generate_*_table`. La auditoría lo detectó y la remediación (`TestPresenceLookupLiveConsumers`, 11 tests, 2026-09-11) importó el generador real y ejecutó los tres métodos. | Auditoría forense FASE-T2-C + remediación D-T2C-A1 | Ningún AC de no-regresión se cierra con tests que duplican la lógica bajo prueba; el test debe importar el módulo de producción y asertar sobre su salida |

#### FASE-T4-A (2026-09-11)

| # | Lección | Fuente | Aplicación futura |
|---|---------|--------|-------------------|
| L-T4A.1 | El protocolo `PromiseExtractor` debe ser `runtime_checkable` para permitir `isinstance(extractor, PromiseExtractor)` en tests y validaciones. Sin `@runtime_checkable`, solo se puede verificar con `hasattr()` que es frágil ante cambios de nombre. El protocolo define `extract_verbal_promises(proposal_text: str) -> list[VerbalPromise]` y ambas implementaciones (LLM + Mock) pasan el check. | Diseño de `llm_extractor.py` (Protocol pattern) | T4-B debe replicar el patrón: protocolo `runtime_checkable` + implementación LLM + implementación Mock para tests |
| L-T4A.2 | El parsing de respuestas LLM debe manejar bloques markdown con indentación variable. El código inicial `lines[1:-1]` fallaba cuando el bloque iniciaba con ````json` indentado o cuando el cierre ```` ` no estaba en la última línea. La solución computa `start_idx` y `end_idx` dinámicamente: si la primera línea inicia con `````, `start_idx=1`; si la última es `````, `end_idx=-1`. Esto cubre todos los formatos que el LLM puede generar. | Test `test_llm_extractor_parses_json_with_markdown` (primer run: JSON parse error; segundo run: PASS tras fix) | T4-B y cualquier consumidor de respuestas LLM deben usar el mismo patrón de parsing robusto; considerar extraer a utilidad compartida si hay terceros consumidores |
| L-T4A.3 | La cache SHA256 de extracciones LLM debe usar `tmp_path` en tests para evitar colisiones entre corridas. Los tests compartían el directorio `.cache/tribunal/` y hits de cache de pruebas anteriores enmascaraban fallos del mock provider. Pasar `cache_dir=tmp_path` al constructor de `LLMPromiseExtractor` aísla cada test. | Tests `test_llm_extractor_cache_hit/miss` (primer run: 5 fallos por cache stale; segundo run: PASS tras agregar `tmp_path`) | Cualquier test que use cache en disco debe inyectar `tmp_path`; la cache de producción puede usar el default `.cache/tribunal/` |
| L-T4A.4 | La clasificación de promesas verbales contra la matriz requiere matching difuso por `service_hint`. El LLM puede generar hints como `"Optimización para asistentes de voz"` mientras la matriz usa `"voice_readiness"`. El método `_find_matrix_entry()` normaliza ambos lados (lowercase, reemplaza guiones bajos y guiones por espacios, busca substrings) y compara. Sin fuzzy matching, varias promesas caían en `PROMESA-SIN-MATRIZ` falso. | Test `test_aligned_service_not_flagged` (primer run: finding `PROMESA-SIN-MATRIZ` para servicio que sí tenía entrada en matriz) | T4-B debe replicar el patrón de matching difuso al buscar referencias a CG-* en el diagnóstico; los nombres de secciones en markdown varían según el generador |
| L-T4A.5 | Un test puede pasar sin ejecutar la rama que dice certificar: el `test_no_breach_not_a_finding` original usaba un extractor vacío y la clasificación nunca recorría entradas NO_BREACH, por lo que la aserción era trivialmente cierta. Además, `service_matrix` iteraba solo promesas (`verbal_promise_found` hardcodeado a `true`), dejando sin auditar las entradas de matriz. La auditoría forense post-ejecución detectó ambos patrones. | Auditoría FASE-T4-A: test vacuo + cruce unidireccional | Todo AC de clasificación exige un test cuyos datos alcancen esa rama; el cruce de artefactos debe cubrir ambas direcciones (promesa→matriz y matriz→promesa) |

#### FASE-T4-B (2026-09-11)

| # | Lección | Fuente | Aplicación futura |
|---|---------|--------|-------------------|
| L-T4B.1 | Los commercial gates están split en DOS archivos: `commercial_gates_report.json` (3 gates: `CG-ROI-NEGATIVE` BLOCKING, `CG-OTA-NARRATIVE` WARNING, `CG-TECH-JARGON` WARNING) y `commercial_gates_report_diagnostic_<ts>.json` (9 entradas, incluyendo `CG-WHATSAPP-LEAD` WARNING con `passed: False`). Leer solo el canónico pierde el único gate que falló en la corrida real. `_merge_commercial_gates()` carga ambos y consolida antes de reportar. ⚠️ **Corregida en la auditoría 2026-09-11**: esta lección nombraba dos archivos y tres gate_ids inexistentes (ver R5.2/R5.3 del dossier, que los conserva como evidencia), y ni esa lista coincide con el fixture de la propia fase. Añadido por la remediación: la corrida real tiene **12 entradas = 10 gate_ids distintos** (`CG-OTA-NARRATIVE` y `CG-TECH-JARGON` viven en ambos archivos), así que la cifra "12 CG-*" del plan es de entradas, no de distintos. | Test `test_reads_both_commercial_files` + `test_honesty_reviewer_retro_reales.py` sobre el baseline real | Cualquier consumidor de commercial gates debe leer ambos archivos **y** deduplicar por `gate_id` antes de emitir hallazgos; el conteo debe declarar si cuenta entradas o distintos |
| L-T4B.2 | Los patrones regex de detección de sobre-presentación deben manejar variaciones de género y número en español. El patrón inicial `r"\b(verificado|confirmado|dato real|cifra exacta|validado)\b"` no capturaba "verificadas" (plural femenino) en "soluciones verificadas". La solución usa clases de caracteres: `r"\b(verificad[oa]s?\|confirmad[oa]s?\|dato real\|cifra exacta\|validad[oa]s?)\b"` para cubrir todas las formas. | Test `test_over_presentation_detected` (primer run: 0 findings; segundo run: 1 finding tras actualizar el regex) | Cualquier detector de texto en español debe usar clases de caracteres `[oa]` y `s?` para cubrir género/número |
| L-T4B.3 | La detección de CG warnings no divulgados no puede decidirse con palabras sueltas ni con el `gate_id` literal. Tokens como `whatsapp`/`número`/`mensaje` aparecen en menciones legítimas de contacto (la propuesta real cita `WhatsApp: 316 6296142`), así que el heurístico clasificaba el warning como divulgado y AC12 fallaba aunque el revisor cargara la propuesta. Y un `gate_id` casi nunca aparece en prosa comercial: buscarlo literal haría que **nunca** se divulgue nada. **Solución implementada (decisión Q2)**: `DISCLOSURE_PHRASES_BY_GATE` mapea `gate_id → frases que nombran el problema detectado`; un `gate_id` sin entrada no se juzga. ⚠️ **Corregida en la auditoría 2026-09-11**: esta lección concluía "buscar el ID del gate en la propuesta" y `evidencia-final.md` declaraba esa solución aplicada, pero el código seguía con palabras sueltas y el test pasaba solo por azar del fixture. | `test_mencion_legitima_de_contacto_no_divulga_el_problema` + `test_divulgacion_expresa_cierra_el_hallazgo` + el retro sobre la propuesta real | Toda heurística de divulgación debe expresarse como tabla auditable de frases del problema, con criterio explícito para gates no cubiertos; un test que pasa "por azar del fixture" no certifica el criterio |
| L-T4B.4 | **Un fixture que replica el contenido de los artefactos pero no su estructura de directorios no prueba el contrato de lectura.** Los 7/7 tests verdes de T4-B usaban un fixture clon fiel de los artefactos reales (mismos `gate_id`, mismos valores) pero ponían la propuesta **dentro** de `v4_audit_dir`; el pipeline la escribe en `v4_complete/`, dos niveles arriba. Ese fue exactamente el requisito que el plan marcó ⚠️ CRÍTICO, y el defecto pasó las tres verificaciones de la fase. T4-A (`AlignmentReviewer`) arrastraba la misma resolución defectuosa: la fase anterior replicó un patrón y la siguiente lo heredó, cubiertas ambas por una sola suite verde. Cure: `artifact_paths.resolve_latest()` como única fuente, más un test retro sobre `output/FASE-D_salentoreal_post_guard/` con skip explícito si falta el baseline. | Auditoría forense FASE-T4-B (D1/D5/S1/S2/S3, causa común §6.1 del dossier) | **Gate de sonda retro** propuesto para `phased_project_executor.md` (FASE-VERIFY/RELEASE): toda fase que escriba un lector de artefactos del pipeline debe tener ≥1 test contra el baseline real, y el ✅ de fase lo exige |
| L-T4B.5 | Un baseline `pre` tomado **después** de crear el archivo de tests de la fase contamina NR1 de forma invisible: pre y post sumaban idéntico 4.037 y el delta correcto (+7) se publicó como "+5 con 2 que dejaron de fallar", inventando una causalidad ("la implementación corrigió indirectamente algún comportamiento") para tapar la aritmética. La firma de la contaminación es una resta de sumas igual a 0. Cure: snapshot real medido con `--ignore` del archivo de la fase (3.991 passed) + `rectificacion-NR1.md` conservando el registro original. | Auditoría FASE-T4-B (D3) + `evidence/FASE-T4-B/rectificacion-NR1.md` | El verifier de NR1 debe comprobar `passed_post = passed_pre + tests_nuevos` **y** que la suma de contados difiera en `tests_nuevos`; si no, el criterio no se declara |

### Desvío registrado — auditoría FASE-T4-B (2026-09-11)

**D-T4B-A1 — la fase certificó ✅ con una suite verde que nunca ejerció el contrato de lectura sobre artefactos reales.** `HonestyReviewer` devolvía `total_cg_count: 0`, `propuesta cargada: False` y un veredicto `BLOQUEAR` espurio por `MISSING_ARTIFACT` cuando se le apuntaba al baseline del pipeline: `_load_proposal()` buscaba en `v4_audit_dir` y su padre, pero el pipeline escribe `02_PROPUESTA_COMERCIAL_<ts>.md` en `v4_complete/`, dos niveles arriba (`v4_audit_dir.parent` es `<hotel>/`, no `v4_complete/`). Las tres verificaciones de la fase (7 tests, serialización, `run_all_validations --quick`) no observaban ese ángulo, y R2.4 se interpretó como "test de serialización verde".

| Aspecto | Registro |
|---------|----------|
| Sonda pre-fix (baseline real, `MockPromiseExtractor`) | `propuesta cargada: False` · `{"canonical_file": null, "diagnostic_file": null, "total_cg_count": 0, "warnings_found": []}` · veredicto `BLOQUEAR` por `MISSING_ARTIFACT` |
| Sonda post-fix, mismo comando | `propuesta cargada: True` · 12 entradas / 10 distintos / duplicados `CG-OTA-NARRATIVE`, `CG-TECH-JARGON` · `warnings_found: ["CG-WHATSAPP-LEAD"]` · `evidence_tier_declared: "B"` · veredicto `DEVOLVER-PRUEBAS` por un hallazgo real |
| Amplitud | **T4-A presentaba el defecto idéntico** (matriz 0, `MISSING_ARTIFACT`, `BLOQUEAR`). Una sola suite verde cubrió ambas fases. La premisa "⚠️ CRÍTICO" del plan era verdadera: el único gate que falló en la corrida real (`CG-WHATSAPP-LEAD`) vive en el archivo de diagnóstico — lo que falló fue el mecanismo |
| Cure aplicada | `modules/quality_gates/tribunal/artifact_paths.py` como única fuente de resolución (ascendientes + `deliveries_dir`, más reciente por mtime), usada por `HonestyReviewer` y `AlignmentReviewer`; resolución una sola vez para que el nombre reportado sea el archivo leído; 22 tests nuevos, 7 de ellos contra el baseline real con skip explícito si falta |
| Decisión NO tomada por la fase | El cableado de los 4 revisores en `main.py` se diferiría a FASE-E2E (Q1, Vía A). `judge.py`, `main.py`, `llm_extractor.py` y `ROADMAP.md` siguen intactos: la restricción del plan no se reinterpreta en silencio |
| Residuo conocido | R2.1 (presupuesto de 30 iteraciones) sigue sin medir, declarado ⚠️ en las tres fuentes; AC11 no puede certificarse hasta que exista `revision_honestidad.json` en un output real |
| Evidencia | `evidence/FASE-T4-B/rectificacion-NR1.md`, `evidence/FASE-T4-B/remediacion-d-t4b-a1.md`, `evidence/FASE-T4-B/tests_baseline_pre_T4B_fase_real.txt`, `evidence/FASE-T4-B/tests_baseline_post_T4B_remediacion.txt`, `evidence/FASE-T4-B/sonda_contraste_pre_post.py` |

### Desvío registrado — auditoría FASE-T2-C (2026-09-11)

**D-T2C-A1 — el AC de no-regresión del régimen `generate_proposal=True` no se cumplió tal como fue redactado.** Los 3 bloques `presence_lookup` de `v4_proposal_generator.py` no se retiraron ni permanecieron muertos: el guard insatisfacible (`hasattr(site_presence_report, 'results')` contra el dict canónico de `normalize_site_presence`) fue corregido a cascada dict+dataclass, reactivando a los consumidores vivos de la tabla de servicios y de la rama AEO («ℹ️ Presente en sitio»). Sonda de auditoría: con el dict canónico, `presence_lookup` pasa de vacío a poblado, por lo que el contenido de la propuesta comercial cambia en el régimen `True`. La fase documentó el cambio como «corregido» en esta sección y en `evidence/FASE-T2-C/`, pero el checklist (06) cerró el ítem bajo la rama «retirados (o justificada su permanencia)» — rama que no ocurrió — y los Criterios de aceptación del prompt quedaron sin marcar.

| Aspecto | Registro |
|---------|----------|
| Decisión conservada | No se revierte: el plan condicionaba el retiro a que los bloques no tuvieran consumidor vivo vía `grep`; sí lo tienen. La reactivación alinea `v4_proposal_generator` con `CoherenceValidator._check_promised_assets_exist`, que ya consumía el dict canónico |
| Estado residual | ~~Sin test que fije la nueva salida contra el código real~~ → **CERRADO 2026-09-11**: `TestPresenceLookupLiveConsumers` (11 tests) ejecuta directo los tres métodos que construyen `presence_lookup` con dict canónico (`exists`/`exists_with_issues`/`not_exists`), `None`, `results` vacíos, objeto tipo dataclass y objeto sin `results`. Antes: los 7 tests de la fase re-implementaban la lógica o leían `main.py` como texto |
| Riesgo | Acotado a FASE-E2E: validar la veracidad de las filas «Presente en sitio» contra el sitio real, no solo el diff contra un output pre-T2-C (cuyo estado anterior era el incorrecto) |
| Remediación | ✅ **EJECUTADA 2026-09-11**: test dirigido a los métodos reales de `v4_proposal_generator.py` que construyen `presence_lookup`, con dict canónico y con `None` — `tests/quality_gates/tribunal/test_s_e2_generate_proposal_false.py` 7→18 tests; colectados 4,018→4,029 |
| Evidencia | Conservada íntegra en `evidence/FASE-T2-C/`; esta corrección ajusta el cierre documental, no el código |
| Instrumento NR1 (D5) | La fase declaró NR1 con el par de **colectados**, no de `passed` (hallazgo D5). Remedido el 2026-09-11 con suite completa: `3,991 passed / 3 failed / 32 skipped / 4 xfailed`; los 3 fallos son ajenos a la fase (ver Seguimientos) y cancelan en ambos lados del par, así que el delta +11 se cumple en `passed` (3,980 + 11 = 3,991 por resta directa, no medición retroactiva). Anotado en el criterio NR1 del prompt de la fase; `baseline-pre-post.md` intacto |

### Decisiones de contrato — auditoría FASE-T1 (2026-09-10)

Dos desvíos de diseño detectados al auditar T1 contra el plan, ya corregidos, más una colisión de contrato (D-T1.3) resuelta con opción (a): primer piso → `first_floor_rule`, P6.5 liberada para Bot 4. Todos se registran aquí porque afectan al contrato que T2/T4 consumen (RESTRICCIÓN de Tarea 4).

| # | Decisión | Símbolo afectado | Regla antes → después |
|---|--------|------------------|----------------------|
| **D-T1.1** | `DEVOLVER-CORRECCIONES` bloquea el ZIP igual que `BLOQUEADO`. Antes solo `BLOQUEADO` interceptaba, así un acta que devuelve el paquete por assets fallidos se entregaba igual. La política vive en un único punto (`BLOCKING_VERDICTS` / `blocks_delivery_zip()` en `judge.py`), exportada por `__init__.py` y consumida por `main.py` en lugar de comparar strings de veredicto en el llamador. | `blocks_delivery_zip`, `BLOCKING_VERDICTS` | 1 de 2 veredictos negativos bloqueaba → ambos bloquean |
| **D-T1.2** | Sin evidencia certificable no hay veredicto máximo. `APROBADO-PARA-ENTREGA` exige Tier **A** y que todas las cláusulas certificables de T1 estén en `PASS`; un `NOT_EVALUABLE` (artefacto ausente, p. ej. borrado por gate-blocking) degrada a condicional en vez de contar como no-bloqueante. `P6.2` queda exenta porque el plan la difiere a T4-A. | `T1_CERTIFIABLE_CLAUSES`, `_compute_verdict` | 0 artefactos + Tier A certificaba entrega → degrada a condicional |
| **D-T1.3** ✅ | **Resuelta — opción (a).** `P6.5` estaba asignada a dos cláusulas distintas: T1 la usaba como *regla de primer piso* (determinista, Juez), mientras T4-B la declaraba como *honestidad NL* (Bot 4). Decisión: el primer piso **deja de ser cláusula P6.5** y queda exclusivamente en la clave top-level `first_floor_rule` (que ya existe en el contrato de acta). `P6.5` queda liberada para Bot 4 (`honesty_reviewer.py` declara `"clause": "P6.5"` sin colisión). Implementación: `_evaluate_p6_5` en `judge.py` se renombra a `_apply_first_floor_rule` y su lógica se integra en `_compute_verdict` via `first_floor_rule`; `T1_CERTIFIABLE_CLAUSES` deja de incluir `P6.5`; `clauses` del acta reserva `P6.5` como `NOT_EVALUABLE` hasta que T4-B la certifique. | `T1_CERTIFIABLE_CLAUSES`, `_apply_first_floor_rule`, `first_floor_rule`, contrato de acta | implementada en auditoría T1 previa a T4-B |

**Verificado**: 17/17 tests de `tests/quality_gates/tribunal/` verdes (4 nuevos fijan D-T1.1 y D-T1.2); `3944 → 3961` colectados; `run_all_validations.py --quick` 8/8 PASS. Los 7 fallos preexistentes en `tests/test_never_block_architecture/test_never_block_integration.py` (`AssetContentValidator`, `PreflightChecker`) son ajenos a este plan: no importan ni `main.py` ni el tribunal.

**Pendiente**: D-T1.3 ✅ implementada (código + docs). Además `modules/quality_gates/tribunal/` y la integración en `main.py` **no están commiteados**, así que a T1 le falta el corte en commit de código que exige R2.1.

---

## Seguimientos abiertos

| Tema | Estado | Acción futura |
|------|--------|---------------|
| T3 (onboarding datos reales) | Fuera de alcance | Plan separado cuando hotel entregue datos |
| T5 (deploy FTP/WP) | Fuera de alcance | Plan separado cuando haya credenciales + staging |
| T6 (throughput + gancho) | Fuera de alcance | Plan separado sobre T3+T5 cerrados |
| S-V10 (banda de palancas) | No re-medible con una corrida | Exige corpus ≥3 hoteles |
| S-E2 (NameError latente) | ✅ **Cerrado** FASE-T2-C | `site_presence_report` hoisted fuera del bloque `if generate_proposal:`; 3 bloques `presence_lookup` corregidos (dict+dataclass); `SitePresenceChecker` muerto retirado de `v4_asset_orchestrator.py` |
| S9 (`INVALID_MAPPINGS`) | ✅ **Cerrado** FASE-T2-C | Test de contrato existente (`test_invalid_mappings_valida_contra_capa1`) ya certificaba keys ⊆ PAIN_SOLUTION_MAP + values ⊆ ASSET_CATALOG; fósil V3 declarado cerrado (solo docstring en `service_identity.py`, no código vivo) |
| S-H2 (performance pain) | Fuera de alcance | Requiere decisión de producto previa |
| Lista blanca del ZIP (deuda P6) | Acta viaja al ZIP | Verificar en E2E que `delivery_packager.py` no excluye `acta_revision.*` |
| **D-T1.3** colisión de ID `P6.5` | ✅ **Implementada** | `_evaluate_p6_5` eliminado; `P6.5` reservada como `NOT_EVALUABLE` en `_evaluate_clauses`; `T1_CERTIFIABLE_CLAUSES` = (`P6.1`, `P6.3`, `P6.4`, `P6.6`); `acta_writer` título P6.5 → "Honestidad Comercial (NL) — reservada Bot 4"; `first_floor_rule` section en MD referencia `MANIFEST.json` |
| **D-T2C-A1** (AC no-regresión régimen `True` en T2-C) | ⚠️ **Desvío registrado — remediación ejecutada 2026-09-11** | `presence_lookup` reactivado con decisión conservada; estado residual cerrado con `TestPresenceLookupLiveConsumers` (11 tests contra los métodos reales); pendiente solo en E2E: verificación de veracidad «Presente en sitio» en sitio real |
| 3 fallos full-suite hallados al medir D5 (2026-09-11) | ⚠️ **Preexistentes, ajenos a la remediación** | (a) `test_barreda_un_solo_emisor_de_la_clave`: `quality_gates/tribunal/asset_reviewer.py` (T2-B) es un segundo emisor de la clave canónica `asset_path` — deuda del propio plan, decidir en T4-B/VERIFY si autorizar el emisor o delegar la lectura en `proposal_asset_alignment`; (b) `test_diagnostic_includes_geo_metrics`: `_build_geo_problems_table` ya no produce la cabecera esperada; (c) `test_function_default_flags`: flaky por orden de recolección (pasa aislado) |
| **S-HF1** (criterio de narración `total_services`) | ⚠️ **Documentación contradictoria** | `decision-integracion.md` cita `alignment.promised_services_total`, que no existe en ningún artefacto real (en FASE-I `alignment` es `null`); `baseline-pre-post.md` y el código usan `summary.promised`. Además `total_services` no aparece en ningún archivo del tribunal. Unificar en `decision-integracion.md` |
| Resolución de artefactos por `mtime` | ⚠️ **No reproducible** | `_resolve_artifact` / `_resolve_manifest` ordenan por `st_mtime`; `git checkout` o una copia cambian el veredicto. Ordenar por la fecha embebida en el nombre |
| Baseline FASE-D sin cubrir en tests | ⚠️ **Deuda de test** | `FASE_D_DELIVERIES_DIR` en `test_judge.py` está definido y sin usar; conéctalo al `MANIFEST.json` real (Tier B) para validar retro contra las dos corridas |
| Versión hardcodeada en el acta | ⚠️ **Viola fuente única de versión** | `acta_writer.py` imprime `v4.76.0` con `VERSION.yaml = 4.75.0`; leer de `VERSION.yaml` o quitar el número |
| Citas de línea en `decision-integracion.md` | ⚠️ **R2.2 + ya obsoletas** | `L2997/L3217/L3293` eran exactas contra `HEAD` pre-T1; tras la integración `main.py` pasó de 3.901 a 3.933 líneas y L3217/L3293 ya no apuntan a nada. Reemplazar por símbolos |
| **D-T4B-A1 — cableado de los 4 revisores en `main.py`** (Q1: Vía A) | ⚠️ **Diferido a FASE-E2E, dueño E2E** | Ninguno de los 4 revisores se ejecuta en el pipeline (`main.py` solo cablea al Juez), así que no existe `revision_*.json` en `output/` y `P6.5` queda `NOT_EVALUABLE`: la liberación de P6.5 (D-T1.3 opción a) no tiene beneficiario hasta E2E, donde se certifican AC11 y AC14. La remediación cumplió lo que sí le tocaba a T4-B: exportar `HonestyReviewer` en `__init__.py`. `review()`/`write_report()` exigen ahora el extractor, para que el cableado de E2E decida el proveedor y no herede una llamada al LLM real por default |
| **Responsabilidades §5.1 / §5.4 / §5.5 de Bot 4** (Q3) | ⚠️ **Diferidas con dueño y AC nuevo** | **§5.1** (cifras de fuga y proyecciones con `evidence_tier` declarado) → dueño **FASE-E2E**, AC propuesto **AC17**. **§5.4** (claims de "recuperación en X meses" con base de cálculo visible) y **§5.5** (contradicción propuesta ↔ gates financieros) → dueño **FASE-VERIFY**, ACs propuestos **AC18/AC19**. Ninguna de las tres está en los 5 checkboxes de aceptación del plan de T4-B: la fase no violó sus AC, el defecto era el vacío documental, que esta fila cierra. **No "arreglar" §5.3**: el artefacto real no declara probabilidades 70/20/10 — `conservative`/`realistic`/`optimistic` son valores monetarios y la verificación de presencia es la interpretación correcta; `SCENARIO_LABELS` es solo etiqueta de presentación |
| **Gate de sonda retro en `phased_project_executor.md`** | ⚠️ **Endurecimiento pendiente, dueño FASE-VERIFY/RELEASE** | Añadir al executor: (1) toda fase que escriba un lector de artefactos del pipeline debe tener ≥1 test contra `output/FASE-D_salentoreal_post_guard/` con skip explícito si falta el baseline, y el ✅ de fase lo exige; (2) el verifier de NR1 debe comprobar que la suma `failed+passed+skipped+xfailed` del `pre` **difiere** de la del `post` en exactamente `tests_nuevos` (resta 0 = baseline contaminado). Es la causa común de D1/D5/S1/S2/S3 y ya causó el desvío D-T2C-A1 |
| Acta de Bot 4 no legible en artefacto (R2.4) | ⚠️ **Pendiente FASE-E2E** | AC11 permanece ⬜ en la matriz AC1–AC16: no pasa a ✅ mientras `revision_honestidad.json` no exista en un output real, por muchos tests verdes que haya |

---

## Métricas de Ejecución (llenar al cierre)

| Métrica | Valor |
|---------|-------|
| Tests pre-plan (baseline v4.75.0) | 3.934 funciones / 298 archivos |
| Tests nuevos del tribunal (T1) | 17 (13 de T1 + 4 de la auditoría) — `3944 → 3961` colectados |
| Tests nuevos del tribunal (T2-A) | 10 (DiagnosisReviewer) — `3961 → 3971` colectados |
| Tests nuevos del tribunal (T2-B) | 12 (AssetReviewer) — `3971 → 3983` colectados |
| Tests nuevos del tribunal (T2-C) | 7 (S-E2 presence_lookup + hoist) — `3983 → 3990` colectados |
| Tests nuevos del tribunal (T4-A) | 28 (15 llm_extractor + 13 alignment_reviewer) — `3990 → 4018` colectados |
| Tests de la remediación D-T2C-A1 (2026-09-11) | 11 (`TestPresenceLookupLiveConsumers`) — `4018 → 4029` colectados |
| Tests nuevos del tribunal (T4-B) | 7 (HonestyReviewer) — **`4029 → 4036` colectados** (⚠️ rectificado: la fase registró `4018 → 4025`, que omitía los +11 de D-T2C-A1 y no coincide con la medición) |
| Tests de la remediación D-T4B-A1 (2026-09-11) | 22 (7 retro sobre baseline real + 4 contrato de ubicación + 11 fidelidad de salida) — `4036 → 4058` colectados; `3998 → 4020` passed |
| Tests totales tribunal acumulados | **92** defs en 8 archivos al cierre de T4-B (17 T1 + 10 T2-A + 12 T2-B + 18 T2-C + 28 T4-A + 7 T4-B) → **114** defs en 10 archivos tras la remediación. ⚠️ El mensaje de commit de T4-B dijo "81" con una descomposición que suma 92 |
| Funciones de test en el repo (método canónico `AGENTS.md`) | 4.038 al cierre de T4-B → **4.060** tras la remediación (`grep -rE "^\s*def test_" tests --include=*.py \| wc -l`) |
| Tests totales post-plan | — |
| Coherence output E2E | — |
| Veredicto del Juez | — |
| Iteraciones totales (8 fases) | ⚠️ T1 sin medir (`evidence/FASE-D/measure_iterations.py` no ejecutado) |
| Fases con delegate_task | — |

---

## Decisiones Arquitectónicas

| ID | Decisión | Rationale | Alternativas rechazadas | Fase |
|----|----------|-----------|------------------------|------|
| DA-T1 | Anfitrión del tribunal = `main.py` junto a `delivery_quality_report` | Es donde hoy se decide el ZIP; `two_phase_flow.py` es huérfano | `two_phase_flow.py` (sin llamador de producción), módulo independiente (drift) | T1 |
| DA-T1 | Veredicto alimenta UNA de las tres rutas de bloqueo existentes | No añadir complejidad; el kill switch `GATE_BLOCKING_ENABLED` ya gobierna | Cuarta ruta propia (aísla el tribunal del flujo existente) | T1 |
| D-T1.1 / D-T1.2 / D-T1.3 | **Revisan la matriz findings → veredicto y la política ZIP.** Ver §Decisiones de contrato — auditoría FASE-T1; D-T1.3 ✅ resuelta (opción a: primer piso → `first_floor_rule`, P6.5 liberada para Bot 4) | La redacción original de T1 permitía certificar entrega sin evidencia y entregar paquetes devueltos por correcciones | Conservar la regla original (deja el acta sin efecto bloqueante real) | T1 |
| DA-T4 | LLM solo extrae; Juez aplica veredicto determinista | Preserva auditabilidad P3; LLM nunca es juez de registro | LLM como juez (no determinista, no testeable con pytest) | T4-A |
| DA-T4A | Protocolo `PromiseExtractor` como interfaz de extracción | Permite intercambiar LLM real vs mock sin cambiar el llamador; `runtime_checkable` habilita validación de tipo en tests | Hardcodear `LLMPromiseExtractor` en `AlignmentReviewer` (acopla tests a provider real, imposible CI offline) | T4-A |
| DA-T4A.2 | Política de veredicto post-auditoría: un hallazgo sustantivo (PROMESA-SIN-MATRIZ o SIN-BRECHA-ASOCIADA) → DEVOLVER-PRUEBAS; S-C4 pasa a severity INFO y no altera el veredicto | Con el umbral arbitrario «≥3 warnings», una sola promesa fantasma quedaba certificada como APROBADO | Umbral `warning>=3` (política original de la primera ejecución de T4-A, detectada en auditoría) | T4-A |
| **DA-T4B.1 (Q1)** | El cableado de los 4 revisores en `main.py` **no** se ejecuta en la remediación: queda como entregable de FASE-E2E con fila de seguimiento y dueño. `HonestyReviewer` sí queda exportado por `__init__.py` (R2) y T4-B degrada a ⚠️ | La restricción del plan ("NO modificar `main.py`") sigue vigente y ampliar alcance sin pedirlo repite el patrón que la auditoría detectó; el bucle `P6.5` `NOT_EVALUABLE` se cierra donde se ejecuta la corrida real | Vía B: cablear ahora los 4 revisores (viola la restricción y amplía el alcance de T4-B) | T4-B remediación |
| **DA-T4B.2 (Q2)** | "CG warning divulgado" = la propuesta contiene una **frase que nombra el problema detectado** por el gate (`DISCLOSURE_PHRASES_BY_GATE`); un `gate_id` sin entrada no se juzga | Fijado con la propuesta real, que cita `WhatsApp: 316 6296142`: una mención legítima de contacto no divulga nada. El `gate_id` literal casi nunca aparece en prosa comercial, y los tokens sueltos producen el falso negativo que causó D5 | Buscar el `gate_id` literal (nunca se divulgaría nada) · bajar el hallazgo a INFO (debilita AC12) · dejar de derivar divulgación del texto (abandona la responsabilidad) | T4-B remediación |
| **DA-T4B.3 (Q3)** | Las responsabilidades §5.1, §5.4 y §5.5 del plan se **difieren con dueño y fase** (FASE-E2E / VERIFY), registradas en §Seguimientos y con nota en `06-checklist` | Ninguno de los tres está en los 5 checkboxes de aceptación del plan, así que implementarlos ahora excedería el alcance; el problema real era el vacío documental, no el recorte | Implementar los tres en la remediación (excede los AC de la fase) | T4-B remediación |
| **DA-T4B.4 (Q4)** | `total_cg_count` reporta **entradas** (12) y se añaden `distinct_cg_count` (10) y `duplicate_gate_ids` como campos explícitos; los hallazgos y `warnings_found` se deduplican por `gate_id` | La corrida real desmiente el supuesto del plan ("los 12 CG-*" distintos). Resolver la ambigüedad por silencio volvería a publicar una cifra no verificada | Cambiar `total_cg_count` a distintos (contradice la cifra del plan y el test de la fase) · deduplicar sin exponer el conteo | T4-B remediación |
| DA-T4B.5 | `all_gates` del acta se reduce a `gate_id`/`severity`/`passed`; se conservan `timestamp` y `artifacts_read` y se registran `MISSING_ARTIFACT` y las claves extra de `summary` como extensiones del schema | El superset es defendible pero infla el artefacto que lee un humano; el detalle completo ya vive en los archivos fuente | Embutir los gates completos con `message`/`suggestion` (duplica los artefactos en el acta) | T4-B remediación |
| DA-T4B.6 | NR4 se interpreta así: **verificar consistencia** (leer el veredicto del gate y confrontarlo con el texto) está permitido; **recalcular el gate** está prohibido. Fijado con `test_no_rejulga_un_gate_que_paso` y `test_no_reimplementa_logica_de_publication_gates` | `TIER_MISMATCH` y `CG_WARNING_UNDISCLOSED` rozan `CG-TIER-CONSISTENCY`; sin nota ni grep de defensa la tensión quedaba indeterminada (S7) | Dejar la tensión sin documentar (VERIFY la leería como violación de NR4) | T4-B remediación |

---

## Checklist de Cierre (llenar en FASE-RELEASE)

- [ ] Todas las fases ✅ en `06-checklist-implementacion.md`
- [ ] AC1-AC16 certificados en FASE-VERIFY
- [ ] NR1-NR5 sin violaciones
- [ ] CHANGELOG.md entrada [4.76.0]
- [ ] GUIA_TECNICA.md nota técnica
- [ ] VERSION.yaml = 4.76.0
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Plan archivado en `Archives/` (R2.5)
- [ ] `10-analisis-post-implementacion.md` completo
- [ ] Lecciones INCLUIR persistidas en memoria del proyecto
- [ ] QMind: write-back del 10-analisis — patrón local (`QMIND-WRITE-BACK.md` en `.opencode/context/`) + ingesta manual a `iah-cli-lecciones` (paso del agente principal/usuario; notebook fuera del scope del agente)
