# Documentación Post-Proyecto — TRIBUNAL-ENFORCEMENT-OBS-2026-09-11

> **Versión objetivo**: 4.77.0
> **Propósito**: Acumular datos por fase para que FASE-RELEASE genere CHANGELOG y GUIA_TECNICA oficiales.
> **Creado**: 2026-09-14 en la sesión de ajuste (el executor lo exigía desde la concepción; se instala vacío y se acumula al cierre de cada fase — no se rellena de memoria al final).

---

## Sección A: Módulos Nuevos / Modificados

| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|
| **_(ninguno — P1 es fase de decisión: sin assets, sin código de producción)_** | — | Verificable en `git status` del commit de cierre: solo `.opencode/plans/…` y `evidence/FASE-P1/` | P1 |
| Tribunal certificador P6 — Bot 3 (assets) | `modules/quality_gates/tribunal/asset_reviewer.py` | AC-F1 dos capas: `_resolve_delivery_dir` ya no devuelve un `.zip` como `Path` (raíz DA-P1.5); nuevos `_resolve_delivery_zip` + `_read_implementation_order` (dir-first, luego `zipfile.read("IMPLEMENTATION_ORDER.md")`) con 4 estados `OK`/`ARTIFACT_MISSING`/`READER_FAILED`/`NOT_RUN` publicados en `_impl_order_check`; `_is_template_stub` reescrito a criterio estructural (secciones con 0 contenido real, excluyendo boilerplate). Commit `0d4d072` | P3-A |
| Tribunal certificador P6 — Juez | `modules/quality_gates/tribunal/judge.py` | AC-F2: `_read_evidence_tier` reescrito (scenarios-first vía `FINANCIAL_SCENARIOS_PATTERN` → `breakdown.evidence_tier`, MANIFEST solo fallback, `"C"` por defecto). AC-F4: `FIRST_FLOOR_TIERS` extendido a `{"B","B+","C"}` (la clave es `"B+"`, como serializa `EvidenceTier.B_PLUS`). Commit `0d4d072` | P3-A |
| Tests del tribunal | `tests/quality_gates/tribunal/test_p3a_zip_tier_firstfloor.py` (nuevo, 21 tests) · `tests/quality_gates/tribunal/test_judge.py` (fixture `tmp_audit_dir` poda `financial_scenarios_*.json` para que los tests de tier por MANIFEST ejerciten el fallback) | Cobertura AC-F1 (capa1 ZIP-aware + capa2 estructural + R2.6 sobre baseline real), AC-F2 (scenarios/fallback/sonda real) y AC-F4 (`B+`). Tribunal pasa de 114 a 135 tests | P3-A |
| Orquestación v4 — bloque FASE-K | `main.py` | AC-F5 (Q5=a): disponibilidad real de analítica calculada **por encima** del bloque FASE-K (`ga4_available` por `is_available()`, `gsc_available` por `is_configured()` — este último **no existía**, nadie lo computaba en `v4complete`) y propagada a `HotelFinancialData(ga4_enabled=…, gsc_enabled=…)`, que llevaba dos literales `False`. Hoist al nivel del cuerpo de la función, fuera de todo `try` con handler ancho (L-T2C.2) y antes del guard `if generate_proposal:`. El `gsc_configured` del MANIFEST, que leía un campo jamas asignado, pasa a leer la misma variable (L-SR3). La segunda computación de `ga4_available` del bloque de analítica se eliminó: una sola evaluación por corrida. Commit `bad0a5e` | P3-B |
| Tribunal certificador P6 — acta | `modules/quality_gates/tribunal/acta_writer.py` | AC-F6: `_read_project_version()` lee `VERSION.yaml` (fuente única del repo) **en cada escritura**; el footer `TribunalJudge v4.76.0` deja de ser un literal. Sin YAML legible publica `version-no-disponible`, nunca una versión plausible Commit `bad0a5e` | P3-B |
| Tests de cableado y acta | `tests/quality_gates/tribunal/test_p3b_analytics_flags_wiring.py` (nuevo, 14) · `tests/quality_gates/tribunal/test_acta_version_desde_yaml.py` (nuevo, 4) · `tests/quality_gates/tribunal/test_s_e2_generate_proposal_false.py` (ampliado, +5) · `tests/test_asset_path_clave_canonica.py` (edición **test-only** de la whitelist, +0) | Cobertura AC-F5 (cableado por AST + regla FASE-1 conductual + régimen `generate_proposal=False`), AC-F6 (versión contra `VERSION.yaml`) y AC-F3 (barreda con barra viva). Tribunal pasa de 135 a 158 tests (recolectados por pytest); con el barreda, la suite suma **+23 recolectados / +17 funciones** Commit `bad0a5e` | P3-B |

| Tribunal certificador P6 — contrato en DTO | `modules/quality_gates/tribunal/outcome.py` **(nuevo, 345 líneas)** | Materializa el §2.3 del contrato P1: `ReviewerStatus` (los cuatro de Q6 + `OK_WITH_FINDINGS`, ver DA-P2.2), `ReviewerReport`, `CorrectiveAction`, `EnforcementState`, `TribunalOutcome`, `EXPECTED_REVIEWERS` y `collect_reviewer_reports`. El Juez decide sobre estos objetos y el acta se deriva de ellos: ningún consumidor hace `json.loads` del acta para decidir. `blocks_publish = blocks ∧ GATE_BLOCKING_ENABLED` (Q7) Commit `df60c24` | P2 |
| Tribunal certificador P6 — Juez | `modules/quality_gates/tribunal/judge.py` | `_compute_verdict(clauses, evidence_tier, first_floor, reviewer_reports)` con la matriz §2.1 **en su orden contractual**; `evaluate()` ya no fija `"reviewer_reports": []` sino los cuatro `NOT_RUN`; nuevas `collect_reviewer_reports()` / `enrich()` (segunda pasada sobre el mismo acta) / `finalize()` (escribe `enforcement` y `corrective_actions` y devuelve el outcome con `blocks` ya resuelto por el llamador, NR3). `_read_evidence_tier` publica `_evidence_tier_source` y `first_floor_rule.source_artifact` cierra el seguimiento del literal obsoleto Commit `df60c24` | P2 |
| Tribunal certificador P6 — acta | `modules/quality_gates/tribunal/acta_writer.py` | Se quitan **dos** omisiones: el guard `if reviewer_reports:` (la sección `Reportes de Revisores` se renderiza **siempre**, una fila por Bot con su estado — DA-P1.6 regla 1) y el literal `**Artefacto fuente**: MANIFEST.json`, que describe un mecanismo que AC-F2 ya no usa. Nacen las secciones `Acciones correctivas` y `Enforcement` (con `suppressed_by_operator` explícito) Commit `df60c24` | P2 |
| Tribunal certificador P6 — Bot 3 | `modules/quality_gates/tribunal/asset_reviewer.py` | `_resolve_delivery_zip` acepta la **cuarentena** (`.zip.tmp`) además del `.zip`: sin eso, el paquete que sí está en disco en el momento de revisar se publicaría como `ARTIFACT_MISSING`. Es la resolución medida de la tensión que el plan heredaba (Q2b asumía ZIP publicado, Q2 pone los revisores sobre el `.tmp`) Commit `df60c24` | P2 |
| Delivery packager | `modules/delivery/delivery_packager.py` | **O1-cuarentena**: `package()` = `write()` + `publish()`. `write()` serializa y deja `<hotel>_<fecha>.zip.tmp` **sin renombrar**; `publish()` hace el rename atómico; `suppress()` borra la cuarentena y lanza `QuarantineSuppressionError` si el borrado falla (contrato §3.4: no es éxito, es infraestructura). `_validate_zip` corre sobre el `.tmp` (DA-P2.3). `_is_excluded_from_zip` excluye el acta del paquete de cliente (DA-P2.1, medido: viajaban 2 miembros) Commit `df60c24` | P2 |
| Orquestación v4 — bloque FASE 7 / T1 / T1b / T2-T4 | `main.py` | Reordenamiento: FASE-T1 corre la **primera pasada**; FASE 7 **escribe** la cuarentena; FASE-T2/T4 corre los 4 Bots **sobre ese ZIP** y registra `revisor → ruta|None`; **FASE-T1b** enriquece el acta, consulta `blocks_delivery_zip` **una sola vez** (NR3), escribe el acta enriquecida y **después** decide `publish()` o `suppress()`, imprimiendo ruta del acta + acciones + dueño. **Sin reintento y sin entrega parcial** (Q1b). Bajo el knob apagado publica y avisa Commit `df60c24` | P2 |
| Tests del tribunal y del delivery | `tests/quality_gates/tribunal/test_p2_veredicto_enriquecido.py` (nuevo, 19) · `tests/delivery/test_p2_cuarentena_zip.py` (nuevo, 9, **contra ZIP real**) · `tests/quality_gates/tribunal/test_judge.py` y `test_acta_serialization.py` (3 tests migrados con causa) | AC-E0 por estado con nombres de test que son la causa del estado; AC-E1 longitud 4 poblada desde el DTO; AC-E2 bloqueo por revisor (cuatro tests + el de ZIP real dirigido por NR7); AC-E3 never-block; AC-E4 par knob apagado/forzado; AC-E5 `corrective_actions` con dueño + supresión del ZIP. Tribunal **158 → 177** recolectados; `tests/delivery/` **69 → 78** Commit `df60c24` | P2 |
| Seguridad y privacidad (P5) — tests | `tests/auditors/test_p5_ac_s1_secret_sanitization.py` (nuevo, 11) · `tests/config/test_p5_ac_s2_secret_checker.py` (nuevo/n ampliado) | Cobertura AC-S1 (sanitización de secrets en providers LLM) y AC-S2 (checker de secretos tracked+staged con NO_CUBIERTO bloqueante). Cero cambios en `main.py`/`judge.py`/`acta_writer.py` | P5 |
| Generación multi-hotel — contrato de rutas ZIP | `modules/geo_enrichment/asset_responsibility_contract.py` | AC-G1: `asset_zip_paths` canonicaliza las rutas de assets dentro del ZIP por hotel; sección de unknown assets para assets sin contrato de ruta. El consumidor (Bot 3) lee rutas normalizadas, no paths ad-hoc | P6 |
| Generación multi-hotel — empaquetado | `modules/delivery/delivery_packager.py` | AC-G1: `write()` acepta `asset_zip_paths` para canonicalizar rutas; AC-G2: `_load_latest_onboarding_data` con fallback independiente por hotel (sin acoplar al último YAML del directorio) | P6 |
| Generación multi-hotel — orquestación | `main.py` | AC-G1: propaga `asset_zip_paths` al packager; AC-G2: fallback de onboarding independiente por URL; AC-G3: `_compute_package_evidence` captura SHA256 + `member_count` del `.zip.tmp` antes de `suppress()` | P6 |
| Generación multi-hotel — acta | `modules/quality_gates/tribunal/acta_writer.py` | AC-G3: `_render_package_evidence` publica SHA256 y `member_count` del paquete en el acta, incluso si el ZIP se suprime después — la evidencia del paquete sobrevive a la supresión | P6 |
| Tests multi-hotel | `tests/test_ac_g1_implementation_order.py` (nuevo, 5) · `tests/test_ac_g2_onboarding_fallback.py` (nuevo, 4) · `tests/test_ac_g3_package_evidence.py` (nuevo, 6) · `tests/test_ac_g4_g5_multi_hotel_matrix.py` (nuevo, 5) | Cobertura AC-G1 (rutas canónicas + unknown assets), AC-G2 (fallback de onboarding independiente), AC-G3 (evidencia de paquete SHA256/member_count), AC-G4 (matriz offline ≥3 perfiles) y AC-G5 (3 caminos causales con NR7). **20 tests nuevos**, 4 archivos | P6 |
**Guía por fase**: P1 no produce filas (decisión). P2: `judge.py`/`main.py`/`delivery_packager.py` según O elegida. P3-A: `asset_reviewer.py`/`judge.py`. P3-B: `acta_writer.py`/`main.py` (solo Q5=a)/test barreda. P4: ninguna (observación). P5: ninguna producción (tests de seguridad). P6: `main.py`/`delivery_packager.py`/`asset_responsibility_contract.py`/`acta_writer.py`. RELEASE: docs.

## Sección B: Funcionalidades Nuevas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| **Contrato del veredicto enriquecido** (documento, no código) | `evidence/FASE-P1/` | Matriz recomendación→veredicto de 8 pasos, consecuencia del bloqueo (escalar: ZIP suprimido + `corrective_actions` + humano decide), **cuatro** estados por revisor y kill switch heredado. **Vinculante** para P2/P3-A/P3-B | P1 |
| **Prompt de FASE-P2** | `.opencode/plans/<PLAN>/` | `05-prompt-inicio-sesion-fase-P2.md`, con O1-cuarentena y la cláusula "no re-decidir" | P1 |
| **Enforcement del tribunal (los dientes)** | `tribunal/`, `main.py`, `delivery/` | **Implementado por P2**: la decisión del Juez **gatea el rename del ZIP**. Un CRITICAL verificado por un Bot o su recomendación `BLOQUEAR` producen `BLOQUEADO` y el `.zip.tmp` se **suprime**: no existe ningún `*.zip` para el `hotel_id` de la corrida. **Sin reintento automático y sin entrega parcial** (Q1b): el operador ve acta + acciones + dueño y decide un humano | P2 |
| **Cuatro estados por revisor, siempre visibles** | `outcome.py`, `acta_writer.py` | `reviewer_reports` pasa de `[]` a cuatro entradas tipadas con `status ∈ {OK_NO_FINDINGS, OK_WITH_FINDINGS, ARTIFACT_MISSING, READER_FAILED, NOT_RUN}` y la sección del MD **nunca se omite**: «no corrió», «sin hallazgos», «con hallazgos», «no había artefacto» y «no se pudo leer» son distinguibles en el documento (NR8/DA-P1.6). Un fallo de lectura **jamás** bloquea, pero sí hace `APROBADO-PARA-ENTREGA` imposible | P2 |
| **Paquete en cuarentena** | `delivery_packager.py` | El nombre definitivo del ZIP es un **acto de publicación**, no un subproducto de la escritura: `write()` → `.zip.tmp`, `publish()` → rename, `suppress()` → unlink. `_validate_zip` corre antes del rename, así que un paquete inválido nunca existe con nombre de entrega | P2 |
| **Kill switch con escape honesto** | `outcome.py`, `acta_writer.py`, `main.py` | El bloqueo del tribunal hereda `GATE_BLOCKING_ENABLED` (un solo knob para todo lo que suprime entrega). Cuando está apagado se publica, **pero el acta lo declara**: `enforcement.{blocking_env, enabled, suppressed_by_operator}` y el stdout avisa. Un CI que lo apague no puede reportar el enforcement como ejercitado | P2 |
| **`blocks_delivery_zip` sigue siendo el único predicado** | `main.py` | NR3 verificada por grep (1 llamada) y por forma: el booleano se calcula una vez y se pasa a `finalize(blocks=…)`, en lugar de dejar que el tribunal vuelva a leer el veredicto. El packager no importa el acta ni consulta `verdict` | P2 |
| **El acta deja de viajar dentro del ZIP de cliente** | `delivery_packager.py` | Medido en la verificación obligatoria de P2: el paquete contenía `ASSETS/v4_audit/acta_revision.{json,md}`. Bajo cuarentena eso fija un acta **pre-veredicto** dentro del objeto que ese acta decide, y la versión enriquecida es inalcanzable por círculo estricto → se excluye por nombre. **Cambio visible para el cliente: el paquete pierde 2 miembros → publicar en CHANGELOG** | P2 |
| **Detección ZIP-only de plantilla vacía** (AC-F1) | `asset_reviewer.py` | `EMPTY_DELIVERY_TEMPLATE` ahora dispara leyendo `IMPLEMENTATION_ORDER.md` **desde el ZIP** en el régimen single-write ZIP-only real (antes el resolutor caía al `.zip` como `Path` fantasma y nunca leía). Distingue 4 estados (NR8): hallazgo OK / `ARTIFACT_MISSING` / `READER_FAILED` / `NOT_RUN`; un fallo de lectura **nunca** publica "vacío" | P3-A |
| **Stub estructural, no conteo de líneas** (AC-F1) | `asset_reviewer.py` | `_is_template_stub` decide por estructura (≥1 sección declarada y todas con 0 contenido real, excluyendo `---` y boilerplate Fecha/Score/footer; ó 0 bytes) en vez de `non_empty_lines <= 3` — el stub real de 468 bytes pasaba por contenido válido | P3-A |
| **Tier del acta desde la fuente pre-packaging** (AC-F2) | `judge.py` | El acta lee `evidence_tier` de `financial_scenarios_*.json → breakdown.evidence_tier` (la fuente que existe antes del packaging), con MANIFEST solo de fallback; antes leía un `MANIFEST.json` que en el flujo real aún no existe y caía a `"C"` en silencio. Sonda sobre artefacto real: acta `"B"` == pipeline `"B"` | P3-A |
| **Primer piso coherente en B+** (AC-F4) | `judge.py` | `FIRST_FLOOR_TIERS` incluye `"B+"` (serialización de `EvidenceTier.B_PLUS`); `first_floor_rule.reason` ya no declara "sin restricción de primer piso" en un caso cuyo veredicto sale condicional | P3-A |
| **Tier A alcanzable: el pipeline propaga la conectividad real** (AC-F5, Q5=a) | `main.py` | El bloque FASE-K construía `HotelFinancialData(ga4_enabled=False, gsc_enabled=False)` mientras `ga4_client.is_available()` se calculaba más abajo y se descartaba: la regla FASE-1 de `_determine_evidence_tier` nunca veía su input verdadero y `APROBADO-PARA-ENTREGA` era **código muerto por construcción**. Desde `bad0a5e` la disponibilidad (GA4 por `is_available()`, GSC por `is_configured()`) se calcula antes de FASE-K y alimenta el tier. **La regla no se tocó**: cambió su input. ⚠️ **Comportamiento visible → el CHANGELOG de 4.77.0 debe declararlo**: una corrida con credenciales GA4+GSC y onboarding verificado puede subir de `B+` a `A`, y con ello el disclaimer del tier y el primer piso del acta. **Qué NO promete**: con fuentes no verificadas el techo sigue siendo el dato — medido sobre el baseline real de FASE-I, da `B` con las cuatro combinaciones de banderas | P3-B |
| **Manifiesto y tier comparten la fuente de la conectividad** | `main.py` | `gsc_configured` del `MANIFEST.json` leía `analytics_status.gsc_available`, un campo que `v4complete` **jamás asigna** (siempre `False`). Sin este cambio, propagar la bandera real habría dejado al ZIP declarando "sin GSC" mientras su propio tier decía `A` — la divergencia de dos fuentes para un hecho (L-SR3) que este plan denuncia desde su Problema | P3-B |
| **Barreda de `asset_path` con whitelist contratada** (AC-F3, cierra **D-V.1**) | `tests/test_asset_path_clave_canonica.py` | `test_barreda_un_solo_emisor_de_la_clave` llevaba en rojo desde v4.76.0 con la limitación declarada. Se cierra **editando solo el test**: `EMISORES_LEGITIMOS`/`CONSUMIDORES_LEGITIMOS` autorizan a Bot 3 con el contrato de §5.1 del contrato de P1 (re-publica la ruta que ya resolvió, no afirma un hecho nuevo). La barra sigue siendo **igualdad de conjuntos**, no contención, y tiene dos mutaciones: retirar la autorización y **que aparezca un emisor no contratado**. Hallazgo medido: la aserción de `consumidores` nunca se había ejecutado — la de `emisores` fallaba antes — y también estaba rota | P3-B |
| **Versión del acta desde la fuente única** (AC-F6) | `modules/quality_gates/tribunal/acta_writer.py` | El footer `TribunalJudge v4.76.0` estaba fijado a mano, así que el acta de certificación podía declarar una versión que ya no era la del pipeline. `_read_project_version()` lee `VERSION.yaml` en cada escritura (sin constante de módulo: nada que se quede cacheado) y, si no lo encuentra, dice `version-no-disponible` antes que inventar una versión plausible | P3-B |
| **Sanitización de secrets en providers LLM** (AC-S1) | `modules/auditors/` (providers) | Dos capas en `LLMMentionChecker`: `_sanitize_text` sustituye el valor de cada key conocida por `***`; `_sanitize_error` redacta `?key=`/`&key=` en el mensaje de error. Todo `logger.warning` de los tres providers pasa por ambas. La key de Gemini viaja en header `x-goog-api-key`, **nunca** en la URL. 11 tests con token sintético, sin red | P5 |
| **Checker de secretos tracked+staged** (AC-S2) | `scripts/` / `config/client_material_policy.yaml` | Alcance = tracked (`git ls-files`) + staged (`git diff --cached`), no workspace completo. Clasificación por sniff NUL, no por whitelist de extensiones. Estados: `SIN_HALLAZGOS` / `BLOCKING` / `NO_LEGIBLE` / `NO_CUBIERTO` (bloqueante). Política de material de cliente separada del detector de claves: check `[5/10]` con marcadores × cuarentena × grandfathered | P5 |
| **Rutas canónicas de assets en el ZIP** (AC-G1) | `asset_responsibility_contract.py`, `delivery_packager.py` | `asset_zip_paths` canonicaliza la ruta de cada asset dentro del ZIP por hotel; el contrato del consumidor (Bot 3) publica las rutas normalizadas. Los assets sin ruta contratada van a una sección `unknown assets` visible en el acta, no se mezclan con los contratados | P6 |
| **Onboarding fallback independiente por hotel** (AC-G2) | `main.py`, `delivery_packager.py` | `_load_latest_onboarding_data` resuelve los datos de onboarding por URL normalizada sin acoplar al último YAML cargado para otro hotel. El fallback `observations.json` se consulta por `hotel_id`, no por posición en el directorio. Una corrida multi-hotel no contamina los datos de un hotel con los de otro | P6 |
| **Evidencia de paquete incluso suprimido** (AC-G3) | `main.py`, `acta_writer.py` | `_compute_package_evidence` captura SHA256 y `member_count` del `.zip.tmp` **antes** de `suppress()`. `_render_package_evidence` publica ambos en el acta. Consecuencia: un ZIP suprimido deja evidencia de qué contenía y de su integridad, sin necesitar el archivo | P6 |
| **Tres caminos causales del veredicto** (AC-G4/AC-G5) | `main.py`, `outcome.py` | (1) Gates permiten + revisores permiten → `publish()`; (2) Gates permiten + revisores objetan → `suppress()`; (3) Gates bloquean por tier C → conditional + `blocks=True` del caller. Los tres con par NR7 verde/rojo (5 pares en total). La matriz offline de AC-G4 valida ≥3 perfiles de hotel sin dependencia estadística | P6 |

## Sección D: Métricas Acumulativas

| Métrica | Pre-plan (v4.76.0) | Al cerrar P1 | Al cerrar P2 | Al cerrar P3-A | Al cerrar P3-B | Al cerrar P4 | Al cerrar P5 | Al cerrar P6 | Final (v4.77.0) |
|---------|--------------------|--------------|--------------|----------------|----------------|--------------|--------------|--------------|------------------|
| Funciones test (canónico `grep -rE "^\s*def test_" tests --include=*.py`) | 4.063 | **4.063** (sin cambio) | **4.174** (+28 propios de P2: 19 en `test_p2_veredicto_enriquecido.py` y 9 en `test_p2_cuarentena_zip.py`; sin parametrizar, así que funciones == recolectados) | **4.129** (+21 propios de P3-A; el salto desde 4.063 incluye **+45 ajenos** del plan PASO0-VERIFICADOR-CAPITALIZACION entrados entre v4.76.0 y P3-A — `test_build_lesson_index.py` + `test_validate_lesson_capitalization.py`) | **4.146** (+17 funciones propias: 10 en `test_p3b_analytics_flags_wiring.py`, 4 en `test_acta_version_desde_yaml.py`, 3 en `test_s_e2_generate_proposal_false.py`). **Reconciliación de bases**: pytest recolecta **4.153** porque 6 de esas 17 funciones están parametrizadas con 2 casos (12 tests) y las otras 11 aportan 1 cada una → `12 + 11 = 23 = delta R2.7`. AC-F3 fue edición **test-only** de una función ya contada, no función nueva | — | **~4.180** (+11 propios de P5: `test_p5_ac_s1_secret_sanitization.py`) | **~4.226** (+20 propios de P6: 5+4+6+5 en cuatro archivos `test_ac_g*.py`); pytest `passed` 4.189, 2 failed, 41 skipped, 4 xfailed | — |
| Archivos `test_*.py` | 293 | **293** (sin cambio) | **300** (+2 propios: `test_p2_veredicto_enriquecido.py`, `test_p2_cuarentena_zip.py`; además se **migraron** 3 tests en 2 archivos preexistentes, sin crear ninguno) | **296** (+1 propio `test_p3a_zip_tier_firstfloor.py`; +2 ajenos PASO0) | **298** (+2 propios: `test_p3b_analytics_flags_wiring.py`, `test_acta_version_desde_yaml.py`; `test_s_e2_generate_proposal_false.py` se amplió, no se creó) | — | **~299** (+1 propio: `test_p5_ac_s1_secret_sanitization.py`) | **~302** (+4 propios: `test_ac_g1_implementation_order.py`, `test_ac_g2_onboarding_fallback.py`, `test_ac_g3_package_evidence.py`, `test_ac_g4_g5_multi_hotel_matrix.py`) | — |
| Fallos conocidos (suite en HEAD) | 3 (2 ajenos + barreda/D-V.1) | **3** (sin cambio) | **2** en PRE y POST, **idénticos** (`test_function_default_flags` flaky declarado, `test_diagnostic_includes_geo_metrics` ajeno) → **0 regresiones de P2**. Delta R2.7 **4.153→4.181 = +28**, `passed` 4.116→4.144 = +28 exactos (ninguna migración changed de categoría: los 3 tests migrados ya estaban verdes y siguen verdes). **El POST se repitió**: el primero dio +27 y una edición posterior añadió un test → L-P2.4 | **4** idénticos en PRE y POST (`test_faq_generator_output_is_jsonld`, `test_function_default_flags` flaky, `test_barreda_un_solo_emisor_de_la_clave` [deuda P3-B], `test_diagnostic_includes_geo_metrics`) → **0 regresiones de P3-A**; delta R2.7 +21 íntegro en `passed` (4.070→4.091) | **3** — `test_barreda…` **ya no está**: se cerró **D-V.1**, el fallo que v4.76.0 publicó con limitación declarada. Quedan `test_faq_generator_output_is_jsonld`, `test_function_default_flags` (flaky, L-VUP-1) y `test_diagnostic_includes_geo_metrics`, **los tres ajenos a este plan y presentes idénticos en el PRE**. Delta R2.7 **+23** (4.130→4.153) con `passed` 4.091→4.115 = **+24**: los 23 nuevos **más** el barreda que migró de rojo a verde (una migración no cambia la suma) → **0 regresiones de P3-B** | — | **3** — mismos 3 ajenos (`test_faq_generator_output_is_jsonld`, `test_function_default_flags` flaky, `test_diagnostic_includes_geo_metrics`); P5 no tocó código de producción. NR1 R2.7 **4.155→4.169 = +14** (tras remediación: +10 sobre el POST auditoría); 0 regresiones | **3** — mismos 3 ajenos en PRE y POST; NR1 R2.7 **4.169→4.189 = +20**, `passed` 4.189; 0 regresiones. Los 20 nuevos corren los 3 caminos causales + 5 pares NR7 | — |
| `--quick` checks | 9/9 | **9/9** (2026-09-14 14:00, medido en el cierre; re-verificado por los 7 hooks de `fd8e4f4`) | **9/9** (743 citas históricas, **0 nuevas y 0 crecimientos** — P2 escribió con símbolos, R2.2) y pre-commit **7/7** en `df60c24` tras regenerar el par de índice que `[6/7]` volvió a exigir | **9/9** (743 citas históricas, 0 nuevas, 0 crecimientos; hooks 7/7 en `0d4d072`) | **9/9** (743 citas históricas, **0 nuevas y 0 crecimientos** — P3-B escribió con símbolos y sin números de línea, R2.2; hooks **7/7** en `bad0a5e`, con `[6/7]` frescura del índice de lecciones y `[7/7]` capitalización) | — | **10/10** (P5 añadió el check de material de cliente `[5/10]`; modo completo 13→**14**; etiquetas full homogeneizadas con contract test) | **10/10** (sin nuevos checks; modo completo 14 mantenido) | — |
| Iteraciones de fase (unidad declarada, D-V2.1) | — | ≈30 `ids` / ≈58 `tool_use` | **≈65 `tool_use` / ≈60 `ids` — auto-reporte con unidad declarada**. **D-V2.1 SÍ se reprodujo** (a diferencia de P3-A/P3-B): el instrumento pide un transcript `.jsonl` cuyo directorio está fuera del workspace y el acceso fue **rechazado por el clasificador**. Corte = commit de código `df60c24`. **Presupuesto de 55 superado = cuarta fase seguida** → L-P2.4, que añade la regla de orden (cero ediciones tras iniciado el POST) | **106 `ids` / 126 `tool_use`** — medido con `measure_iterations.py`, corte = commit `0d4d072`. **El instrumento SÍ alcanzó el transcript → D-V2.1 NO se reprodujo.** Presupuesto 20 superado → L-P3A.1 | **120 `ids` / 120 `tool_use`** — medido con `measure_iterations.py` sobre el transcript de sesión, corte = commit de código `bad0a5e`. **El instrumento volvió a alcanzar el transcript** (segunda fase seguida: D-V2.1 no se reprodujo; su vigencia como limitación queda **en observación**, no confirmada). **Presupuesto 25 superado = tercera fase seguida** → causa y cura en L-P3B.1, que propone el cambio de regla (presupuestar por coste de verificación) y no solo la nota | — | Presupuesto FUERA DE SERVICIO (R2.1/D-V2.1); medida real auto-reportada con unidad declarada = commits de ejecución: 1 (`b25b63a`) + 1 remediación; D-V2.1 reproducido | Presupuesto FUERA DE SERVICIO (R2.1/D-V2.1); medida real auto-reportada con unidad declarada; D-V2.1 reproducido | — |

> La nota original ("la fila de barreda asume que P3-B se ejecuta con Q5≠(a) o (a)") queda **resuelta por medición**: P3-B corrió con **Q5=(a)** y cerró la barreda → `failed` pasó de 4 a 3. Lo que sigue abierto es la columna P4: si T3a no cierra con proveedor y fuente, se marca `Diferida` con referencia a la decisión (§Cierre válido sin P4 en `dependencias-fases.md`).

## Sección E: Archivos Afiliados Actualizados

| Archivo | Actualizado en | Nota |
|---------|----------------|------|
| `REGISTRY.md` vía `log_phase_completion.py --fase FASE-P2 --check-manual-docs` (**sin** `--release`) | P2 | Registro de fase de ejecución; `CHANGELOG`/`GUIA_TECNICA` siguen acumulándose en este `09` §A/§B/§D/§E hasta RELEASE |
| `evidence/FASE-P2/` (NR1 `nr1_baseline_pre.txt`/`nr1_baseline_post.txt`/`nr1_delta_r2_7.md`, **8 pares NR7** `NR7-AC-E0-a.txt`, `-b.txt`, `NR7-AC-E1.txt`, `NR7-AC-E2.txt`, `NR7-AC-E3.txt`, `NR7-AC-E4.txt`, `NR7-AC-E5-a.txt`, `-b.txt` + runner `nr7_mutation_checks.py`, sonda de retro `verify_retro_fase_e2e.py` + `retro-estructural-FASE-E2E.md`, `constancia-verificacion-acta-en-zip.md`) | P2 | Evidencia de cierre: delta R2.7 (+28, resta verificada contra el PRE propio), **ocho** mutation checks verde/rojo — dos por AC donde el contrato pedía una —, el diff estructural sobre la corrida E2E del predecesor (mismo artefacto, `APROBADO-CONDICIONAL…` → `BLOQUEADO`, cláusulas intactas) y la **verificación obligatoria de la Tarea 1 medida**, que resultó ser un círculo y produjo DA-P2.1. Commit de código `df60c24` |
| `.opencode/LECCIONES-INDEX.md` · `.opencode/lecciones_index.json` | P2 | Par regenerado con `build_lesson_index.py` porque el hook `[6/7]` **volvió a rechazar** el primer intento de commit (editar los `.md` del plan vence el índice). Artefacto generado, no editado a mano |
| `06-checklist-implementacion.md` · `dependencias-fases.md` · `README.md` · este `09` · `10-analisis-post-implementacion.md` · `00-lecciones-capitalizadas.md` | P2 | Cierre documental: fila 2 ✅ + iteraciones con unidad declarada, diagrama/tabla de dependencias y **todos los conflictos de archivo** actualizados, progreso **4/6**, §A/§B/§D/§E, fila de Resumen de Ejecución + DA-P2.1…P2.4 + L-P2.1…L-P2.4, **dos seguimientos cerrados** (el del literal `MANIFEST.json` que P1 asignaba a P2 y la tensión Q2b↔Q2) y el bloque «Estado al cerrar FASE-P2» en §2 del `00-` |
| `REGISTRY.md` vía `log_phase_completion.py --fase FASE-P3-B --check-manual-docs` (**sin** `--release`) | P3-B | Registro de fase de ejecución; `CHANGELOG`/`GUIA_TECNICA` siguen acumulándose en este `09` §A/§B/§E hasta RELEASE |
| `evidence/FASE-P3-B/` (NR1 `nr1_baseline_pre.txt`/`nr1_baseline_post.txt`/`nr1_delta_r2_7.md`, **6 pares NR7** `NR7-AC-F3-a.txt`/`-b.txt`, `NR7-AC-F5-a.txt`/`-b.txt`/`-c.txt`, `NR7-AC-F6.txt` + runner `nr7_mutation_checks.py`, `constancia-Q5.md`, sonda `verify_probe_ac_f5_techo_tier.py` + `probe-post-fix.txt`) | P3-B | Evidencia de cierre: delta R2.7 (+23, resta verificada), mutation checks verde/rojo por AC, la rama del condicional Q5 que corrió, y el techo de tier con su dueño medido sobre el baseline real de FASE-I. Commit de código `bad0a5e` |
| `06-checklist-implementacion.md` · `dependencias-fases.md` · `README.md` · este `09` · `10-analisis-post-implementacion.md` · `00-lecciones-capitalizadas.md` | P3-B | Cierre documental: fila 3b ✅ + iteraciones medidas, diagrama/tabla de dependencias y conflictos, progreso **3/6**, §A/§B/§D/§E, fila de Resumen de Ejecución + L-P3B.1/.2/.3, y el bloque "Estado al cerrar FASE-P3-B" en §2 del `00-` |
| `REGISTRY.md` vía `log_phase_completion.py --fase FASE-P1` (**sin** `--release`) | P1 | Registro de fase de decisión |
| `REGISTRY.md` vía `log_phase_completion.py --fase FASE-P3-A --check-manual-docs` (**sin** `--release`) | P3-A | Registro de fase de ejecución; `CHANGELOG`/`GUIA_TECNICA` siguen acumulándose en este `09` §A/§B hasta RELEASE |
| `evidence/FASE-P3-A/` (NR1 `nr1_baseline_pre.txt`/`nr1_baseline_post.txt`/`nr1_delta_r2_7.md`, 4 pares NR7 `NR7-AC-F1-capa1.txt`/`-capa2.txt`/`NR7-AC-F2.txt`/`NR7-AC-F4.txt` + runner `nr7_mutation_checks.py`, sonda `verify_probe_ac_f1_f2_f4.py` + `probe-post-fix.txt`) | P3-A | Evidencia de cierre: delta R2.7 (+21) y mutation checks verde/rojo por AC (NR7). Commit `0d4d072` |
| `06-checklist-implementacion.md` · `dependencias-fases.md` · `README.md` · este `09` · `10-analisis-post-implementacion.md` · `00-lecciones-capitalizadas.md` | P3-A | Cierre documental: fila 3a ✅ + iteraciones, tabla/diagrama de dependencias, progreso 2/6, §A/§B/§D/§E, Resumen de Ejecución + L-P3A.1, "Estado al cerrar P3-A" en §2 |
| `01-plan-maestro.md` | P1 | §1 orden y presupuesto · §2.1 confirmado y agravado · §3 O1-cuarentena · §6 **ACs finales** (17 filas + columna NR7) |
| `06-checklist-implementacion.md` | P1 | Estado Global, checklist de P1 cerrado, y P3-A/P3-B/P2 reescritos con lo decidido |
| `dependencias-fases.md` | P1 | Diagrama y tabla reordenados (P3→P2) · **FASE-VERIFY cerrada en no activa** · prompt de P2 marcado como creado |
| `README.md` · `00-lecciones-capitalizadas.md` · `10-analisis-post-implementacion.md` · este `09` | P1 | Progreso 1/6 · §3.b resuelto · DA-P1.1…DA-P1.10 + 5 lecciones · aporte de fase |
| `evidence/FASE-P5/` (NR1 `nr1_baseline_pre.txt`/`nr1_baseline_post.txt`/`nr1_delta_r2_7.md`, 1 par NR7, `REMEDIACION-auditoria-2026-09-15.md`, `AC-S3-S4-inventario-superficie.md`) | P5 | Evidencia de cierre: delta R2.7 (+10 tras remediación), mutation check verde/rojo, auditoría + remediación del mismo día, inventario de superficie de cliente. Commit `b25b63a` + remediación |
| `06-checklist-implementacion.md` · `dependencias-fases.md` · este `09` · `10-analisis-post-implementacion.md` · `00-lecciones-capitalizadas.md` | P5 | Cierre documental: fila P5 ✅, §A/§B/§D/§E, L-P5.1/.2/.3, bloque "Estado al cerrar FASE-P5" en §2 del `00-`. `--quick` 9/9 → **10/10** |
| `evidence/FASE-P6/` (NR1 `nr1_baseline_pre.txt`/`nr1_baseline_post.txt`/`nr1_delta_r2_7.md`, **5 pares NR7** `nr7_mutation_checks.md`) | P6 | Evidencia de cierre: delta R2.7 (+20, resta verificada contra el PRE propio de P5), 5 mutation checks verde/rojo (uno por AC-G), 0 regresiones |
| `06-checklist-implementacion.md` · `dependencias-fases.md` · este `09` · `10-analisis-post-implementacion.md` · `00-lecciones-capitalizadas.md` | P6 | Cierre documental: fila P6 ✅, §A/§B/§D/§E, L-P6.1/.2/.3, seguimientos F-P4.1/F-P4.3/F-P4.7/F-P4.9 cerrados, bloque "Estado al cerrar FASE-P6" en §2 del `00-`. Progreso **7/8** |
| **`AGENTS.md` / `CHANGELOG.md` / `GUIA_TECNICA.md` / `VERSION.yaml`** | **P1: NO · P3-A: NO · P3-B: NO** | Ninguna fase del plan toca documentos versionados; el bump y su propagación son de RELEASE. Lo que **RELEASE debe publicar** al cerrar 4.77.0: (1) la decisión de enforcement y su consecuencia; (2) el orden P3→P2 y por qué; (3) que **no hubo sesión FASE-VERIFY** y AC-V1 la sustituyó; (4) **AC-F5 cambia el `evidence_tier` de corridas reales** — comportamiento visible, se declara (DA-P1.8) y **ya está redactado en §B de este `09`**: una corrida con GA4+GSC configurados **y** onboarding verificado puede salir `A` donde antes salía `B+`, con el disclaimer del tier y el primer piso del acta cambiando con él; (5) el acta deja de omitir la sección de revisores y pasa a listar **cuatro** estados; (6) **la fila de Tests de `AGENTS.md` queda desactualizada por este plan** — `test_barreda_un_solo_emisor_de_la_clave` ya no falla (**D-V.1 cerrada** en `bad0a5e`), así que los fallos conocidos pasan de cuatro a tres y el conteo canónico es **4.146 funciones / 4.153 recolectados / 298 archivos**; actualizarla es de RELEASE junto con el bump, no de esta fase; (7) el acta ya no fija su versión a mano: lee `VERSION.yaml`, así que el footer `TribunalJudge v…` sigue al bump automáticamente **(8) el tribunal enforcea** — P2 cableó los dientes que v4.76.0 dejó como auditoría: `BLOQUEADO`/`DEVOLVER-CORRECCIONES` **suprimen el ZIP** y el acta trae `corrective_actions[]` con dueño; hay que decirlo porque cambia el resultado que recibe el operador, no solo su documento; **(9) el ZIP de cliente deja de contener el acta** (`ASSETS/v4_audit/acta_revision.{json,md}` ya no viajan) — cambio material en el artefacto entregado, con su causa en DA-P2.1; **(10) el acta gana tres claves** (`reviewer_reports` poblada y con cuatro estados visibles, `enforcement`, `corrective_actions`) y **`NOT_RUN` post-P2 es un defecto**, no un resultado; **(11) la fila de Tests de `AGENTS.md` vuelve a quedar desactualizada**: el conteo canónico es **4.174 funciones / 4.181 recolectados / 300 archivos** (P3-B publicó 4.146/4.153/298) y los fallos conocidos pasan de tres a **dos** (`test_faq_generator_output_is_jsonld` ya no falla), con `test_function_default_flags` declarado flaky. |

## Aporte de FASE-P1 para GUIA_TECNICA

- **Técnico**: `_read_evidence_tier` depende de un `MANIFEST.json` que en el flujo real aún no existe, así que el acta operaba con `"C"` por fallback silencioso; `_is_template_stub` contaba frontmatter como contenido; `acta_writer` suprimía la sección de revisores cuando estaba vacía. Los tres son de la misma familia —**ausencia publicada como hallazgo**— que NR8/`DA-C3` prohíben.
- **De proceso**: el Paso 0 de P1 cumplió en producir evidencia propia — los tres hechos del párrafo anterior no estaban en el plan y cambiaron dos ACs (nace AC-F6; AC-F2 se re-enuncia). Contraste honesto: **la misma tarea re-afirmó lo que ya decía §2.1**; confirmar no es descubrir.
- **Comercial**: G0 queda **encarrilado, no cerrado**. P1 quita la objeción de diseño; el dato sigue dependiendo de T3a/T3b (un hotel que dé sus números y su analítica), y este plan ya no finge tenerlo.

## Aporte de FASE-P3-A para GUIA_TECNICA

- **Técnico**: AC-F1 y AC-F2 eran **el mismo defecto con dos víctimas** (DA-P1.5): `_resolve_delivery_dir` (Bot 3) y `_read_evidence_tier` (Juez) estaban escritos contra un directorio descomprimido que el packaging single-write ZIP-only nunca produce, y ambos caían a un fallback silencioso (el `.zip` como `Path`, o `"C"` como tier). La cura no fue una función compartida sino **una única fuente de verdad por hecho**: el resolutor de entrega lee un ZIP sea miembro del ZIP o directorio (4 estados NR8, un fallo de lectura nunca publica "vacío"), y el tier se lee de `financial_scenarios_*.json` que existe **antes** del packaging. Detalle que muerde: `EvidenceTier.B_PLUS` **serializa como `"B+"`**, no `"B_PLUS"` — `FIRST_FLOOR_TIERS` llevaba la clave equivocada y por eso el primer piso no se aplicaba en `B+`.
- **De proceso**: el presupuesto era 20 iteraciones y se midieron **106 `ids` / 126 `tool_use`** (corte = commit `0d4d072`). Causa medida: una fase de detección/fidelidad cuyo NR1 (R2.7) es la **suite completa** (4.130 tests, ~7-9 min por corrida, dos corridas pre/post) más **4 pares NR7** de mutation check no cabe en un presupuesto pensado para una fase de código acotada. El instrumento `measure_iterations.py` **sí alcanzó el transcript** — la limitación D-V2.1 ("no alcanza bajo el cliente actual") **no se reprodujo**, así que la cifra es medida, no auto-reportada.
- **Comercial**: el acta deja de decir `evidence_tier C` cuando el pipeline dice `B` (sonda sobre artefacto real FASE-I: acta `"B"` == pipeline `"B"`), y deja de callar el defecto de entrega vacía en régimen ZIP-only. **Fidelidad restaurada**; el *enforcement* (que el veredicto consuma estos hallazgos y suprima el ZIP) sigue pendiente en P2 — P3-A arregla lo que el acta **dice**, no todavía lo que **hace**.

## Aporte de FASE-P3-B para GUIA_TECNICA

- **Técnico**: AC-F5 es un fix de **honestidad del input**, no de la regla. `_determine_evidence_tier` nunca estuvo mal: su guard `ga4_enabled and gsc_enabled and has_verified_data` jamás pudo ser cierto porque el llamador le pasaba `False, False` fijos mientras el mismo `main.py` calculaba `ga4_client.is_available()` unas líneas más abajo y lo tiraba. Al propagarlo aparecieron dos hechos que el plan no tenía: **(i)** GSC no tenía valor real que hoistear — `AnalyticsStatus.gsc_available` se declara en `False` y nadie lo asigna en `v4complete`, así que hubo que computarlo (`GoogleSearchConsoleClient().is_configured()`, que no hace red: credenciales + propiedad); propagar solo GA4 habría dejado el Tier A igual de inalcanzable. **(ii)** `gsc_configured` del `MANIFEST.json` leía justo ese campo muerto, así que quedó apuntado a la misma variable hoisteada para que el ZIP no contradiga a su propio tier (una sola fuente de verdad por hecho). Dos verificaciones de cableado se hacen **por AST sobre `main.py`** — la forma de certificar que un nombre se asigna antes de su consumidor, que no está bajo un guard que el consumidor no esté, y que ningún `except Exception` lo envuelve, sin ejecutar una corrida que no se puede ejecutar en un test.
- **De proceso**: **tercera fase seguida que revienta su presupuesto** (25 declarados, **120 `ids` / 120 `tool_use`** medidos con el instrumento, corte = `bad0a5e`). La causa ya no es una anomalía de esta fase sino un patrón del plan: el presupuesto se declara por **tamaño del entregable** y lo que domina el coste es la **verificación** — dos corridas completas de 4.130+ tests para el par NR1 (~7-10 min cada una, y el PRE hay que tomarlo *antes* de tocar nada) más 6 pares NR7 que relanzan subsets. La diferencia con P1 es que el instrumento **volvió a alcanzar el transcript**, así que la cifra es medida y no auto-reportada → D-V2.1 queda **en observación**, no confirmada. También deja lección propia la barreda: un test que falla por su primera aserción **deja sin vigilar todo lo que está después** — la de `consumidores` nunca se había ejecutado y estaba igual de rota.
- **Comercial**: con `bad0a5e` el pipeline **ya puede certificar Tier A**, así que la conversación sobre por qué una corrida salió `B+` se separa en dos preguntas con dueño distinto: *¿quién dio el dato verificado?* (T3a — el operador) y *¿el hotel tiene GA4+GSC?* (T3b — credenciales). Lo que ya **no** cabe decir es "el pipeline no propaga las banderas": esa excusa estaba en el plan y se cerró. Y el techo **no** sube solo: medido sobre el baseline real de FASE-I, el tier sigue siendo `B` con las cuatro combinaciones de banderas porque sus fuentes son `regional_v410`/`default`. AC-F5 abre la puerta; no la cruza por el hotel.

---

## Aporte de FASE-P2 para GUIA_TECNICA

- **Técnico**: el punto de decisión del delivery se movió del *write* al **rename**.
  `DeliveryPackager.write()` produce `<hotel>_<fecha>.zip.tmp` con todos los bytes ya
  finalizados (single-write ZIP-only intacto); los 4 Bots leen **ese** archivo; el Juez
  corre su segunda pasada sobre los DTOs de `outcome.py` y `blocks_delivery_zip` decide
  `publish()` o `suppress()`. Consecuencia no obvia: `_validate_zip` tuvo que correr
  **antes** del rename, porque el contrato exige que el nombre definitivo no exista ni un
  instante para un paquete inválido. Y el acta dejó de viajar dentro del ZIP: medido, ya
  contenía `ASSETS/v4_audit/acta_revision.{json,md}`, y pedir que contenga la versión
  enriquecida es pedir un objeto que contiene su propia consecuencia.
- **Contrato vs código**: la matriz §2.1 se implementó **en su orden** y el orden es parte
  del contrato — por eso hay un test (`test_el_orden_de_la_matriz_es_parte_del_contrato`)
  que fija que un CRITICAL de revisor manda sobre un `P6.3` en FAIL. La fila 4 se
  implementó como guard del veredicto, no como reescritura de la cláusula que publicaron
  los gates (DA-P2.4): el efecto exigido es el mismo y las cláusulas siguen diciendo lo
  que midió el gate.
- **Cómo leer el acta a partir de 4.77.0**: `reviewer_reports[]` con `status` por Bot,
  `enforcement` con el estado real del knob, `corrective_actions[]` con `owner`. Con
  `GATE_BLOCKING_ENABLED=false` el ZIP se publica pero el acta dice
  `suppressed_by_operator: true`: **un CI apagado no puede reportar el enforcement como
  ejercitado**. Y `NOT_RUN` en una corrida post-P2 es un defecto de cableado, no un
  resultado.
- **Efecto visible para el cliente**: el paquete pierde los dos miembros del acta. El
  primer `BLOQUEADO` real del tribunal **suprime el ZIP**: no hay entrega parcial.

## Aporte de FASE-P4 para GUIA_TECNICA

> Una corrida de observación **no genera módulos**: su aporte es lo que demostró del pipeline y los
> hallazgos que deja con dueño. Cero `.py` de producción tocados (restricción del prompt + L-V.4).

- **Lo que quedó demostrado en el pipeline real** (hasta ahora solo visto en tests): el veredicto del
  tribunal **suprime el ZIP** de una corrida de verdad — `write()` deja `<hotel>_<fecha>.zip.tmp`, los
  4 Bots lo leen, `BLOQUEADO` → `suppress()`, y `deliveries/` queda sin `*.zip` ni `*.zip.tmp`. En el
  acta real: `reviewer_reports` de **longitud 4**, `corrective_actions[]` con `owner`, `enforcement`
  con el knob declarado. Y **AC-F2/AC-F4 observados en vivo**: `evidence_tier "B+"` con
  `first_floor_rule.applied=true` y `source_artifact` apuntando a `financial_scenarios_*.json` — la
  divergencia C↔B del plan anterior ya no es alcanzable por su ruta vieja.
- **Reproducir una observación equivalente** (los detalles que no son evidentes):
  `python main.py v4complete --url <URL-del-hotel> --output output/<dir-de-la-fase>` — **sin**
  `--permission-mode` (el default `auto` es el que usó el baseline; `chat` omitiría la auditoría
  externa y la corrida quedaría en defaults) y **sin** `--force-new` (esa bandera la lee `execute`, no
  `v4complete`). `v4complete` solo consume `--url/--output/--nombre/--debug`. Un solo parser global:
  `X --help` imprime el help completo para cualquier subcomando.
- **Cómo llega el dato de un hotel sin YAML**: `_load_latest_onboarding_data` matchea por URL
  normalizada, y si no hay YAML cae al warehouse `data/hotel_observations/observations.json` vía
  `_observation_to_onboarding_format`. **Fragilidad medida (F-P4.7)**: ese camino depende de que el
  fallback S7 se active, y S7 exige que `output/clientes/` contenga **al menos un** YAML ajeno. Con el
  directorio vacío, la corrida usa defaults **en silencio**. Verificar siempre en el log:
  `✅ Onboarding data loaded: N campos confirmados`.
- **Por qué la evidencia de esta fase está partida en dos**: el remoto es **público**. Lo versionado es
  informe, consentimiento, sondas, scripts y el manifiesto de hashes del baseline ajeno; la corrida
  completa (62 archivos), su log y el detalle con cifras COP viven en `evidence/FASE-P4/corrida/`,
  excluido en `.gitignore` con el mismo criterio que ya excluye `evidence/FASE-E2E/`.
- **Límites que RELEASE debe publicar, no esconder**: (i) **Tier A no observado** — el techo `B_PLUS`
  lo puso la analítica del hotel (`ga4_available`/`gsc_available` medidos en `False`), no el cableado
  que AC-F5 cerró; (ii) **el contrafactual del enforcement no se ejercitó** — los gates ya daban
  `BLOQUEADO` antes de los revisores, y mientras F-P4.1 siga abierto ninguna corrida real puede dar el
  caso "gates aprueban + un revisor objeta"; (iii) **una sola corrida de un solo hotel** — S-V10 pide
  ≥3 hoteles para confianza estadística.
- **Los 9 hallazgos con dueño** (F-P4.1…F-P4.9 en `evidence/FASE-P4/informe-observacion.md` §3), de los
  cuales dos piden decisión antes de volver a correr: **F-P4.1** `IMPLEMENTATION_ORDER.md` es un stub de
  ~470 B en todos los paquetes medidos → con los dientes puestos bloquea el 100 % de las corridas
  reales, y hay que decidir si un stub debe bloquear; **F-P4.5** el log de corrida imprime una clave de
  API en texto plano y el repo es público — el check de secretos `[4/9]` **sí** corre en pre-commit (vía
  `validate-plan`), pero su cobertura medida es solo `*.py` con 4 patrones de *asignación*, así que una
  clave escrita en un `.log` o un `.md` queda fuera (la cura es extender el barrido y secar el error del
  provider) — a la vez, `evidence/FASE-I/corrida/` ya tiene 59 archivos
  versionados en `origin/master` con material de un cliente real.
- **Pendiente documental heredado**: la fila de **Tests** de `AGENTS.md` sigue desactualizada (declara
  la barreda como fallo conocido y cuatro fallos; hoy son 3, todos ajenos). Su actualización es de
  RELEASE con el bump, no de esta fase.

## Aporte de FASE-P5 para GUIA_TECNICA

> Sin módulos nuevos de negocio: el aporte son **dos controles** sobre el árbol de
> validaciones (`run_all_validations.py`) y su remediación post-auditoría del mismo
> día. Cero cambios en `main.py`/`judge.py`/`acta_writer.py`.

- **Sanitización de errores del provider LLM (AC-S1)**: la key de Gemini viaja en
  header `x-goog-api-key`, **nunca** en la URL (los `HTTPError` de requests incluyen
  la URL). Dos capas en `LLMMentionChecker`: `_sanitize_text` (sustituye el valor de
  cada key conocida por `***`) y `_sanitize_error` (redacta `?key=`/`&key=` en el
  mensaje). Todo `logger.warning` de los tres providers pasa por ambas. Reproducir:
  `python -m pytest tests/auditors/test_p5_ac_s1_secret_sanitization.py` (11 tests,
  token sintético, sin red).
- **Checker de secretos (AC-S2, remendado)**: alcance = lo que se prepara para
  publicar (**tracked** vía `git ls-files` **+ staged** vía `git diff --cached`), no
  el workspace completo. Clasificación por **sniff NUL**, no por whitelist de
  extensiones: `.cursorrules`, hooks sin sufijo, `.ps1`/`.diff` se leen; binarios
  conocidos se excluyen **declarados en el mensaje**; lo no clasificable es
  `NO_CUBIERTO` y **bloquea**. Estados visibles: `SIN_HALLAZGOS` / `BLOCKING` /
  `NO_LEGIBLE` / `NO_CUBIERTO`. La cuarentena `archives/`, `evidence/`, `.opencode/`
  queda fuera del barrido de workspace (documentado; el staged se escanea sin
  excepción). **Hallazgo de la auditoría**: en b25b63a el escaneo staged estaba muerto
  (`re` importado dentro de otra función → `NameError` tragado por `except Exception`)
  — ver `evidence/FASE-P5/REMEDIACION-auditoria-2026-09-15.md` §1 y L-P5.1.
- **Política de material de cliente (separada del detector de claves)**: check
  `[5/10]` `_check_client_material` lee `config/client_material_policy.yaml`
  (marcadores × cuarentena × grandfathered con dueño). Impide **versionar** rutas con
  marcador de cliente fuera de cuarentena; lo ya publicado en `origin/master`
  (p. ej. `tests/fixtures/donalfonsohotel_onboarding.yaml`) queda grandfathered con
  disposición pendiente de la **puerta AC-S4** — no es condonación, es inventario
  vigilado: borrar la fila reactiva el bloqueo.
- **Denominadores**: `--quick` pasó de 9 a **10** checks; modo completo 13 → **14**
  (las etiquetas full venían mezclando denominadores desde antes de P5; homogeneizado
  con contract test en `test_validate_lesson_capitalization.py`). `AGENTS.md` aún dice
  "9/9 rápidos; 13 en el completo" — su actualización es de RELEASE con el bump
  (archivo bajo instrucción explícita de commit).
- **Lo que P5 NO cerró (publicar en RELEASE, no esconder)**: la rotación de las 3
  keys, la retirada/saneamiento de los blobs de cliente y la visibilidad del repo son
  **acciones del operador** registradas en `evidence/FASE-P5/AC-S3-S4-inventario-superficie.md`;
  mientras no haya resolución verificable o aceptación explícita del riesgo, **la
  puerta AC-S4 bloquea el RELEASE público** aunque el cierre técnico esté ✅.

## Aporte de FASE-P6 para GUIA_TECNICA

> Cuatro archivos de producción tocados (`main.py`, `delivery_packager.py`,
> `asset_responsibility_contract.py`, `acta_writer.py`); cero cambios en `judge.py`.

- **Técnico**: el pipeline deja de asumir un solo hotel por corrida. `asset_zip_paths`
  canonicaliza la ruta de cada asset dentro del ZIP por `hotel_id`, y los assets sin
  ruta contratada van a una sección `unknown assets` visible en el acta — no se
  mezclan con los contratados ni se pierden en silencio. El onboarding fallback
  (`observations.json`) se consulta por URL normalizada, no por posición en el
  directorio, así que una corrida multi-hotel no contamina los datos de un hotel con
  los de otro.
- **Evidencia de paquete sobreviviente**: `_compute_package_evidence` captura SHA256 y
  `member_count` del `.zip.tmp` **antes** de `suppress()`, y `_render_package_evidence`
  los publica en el acta. Consecuencia: un ZIP suprimido deja evidencia de qué
  contenía y de su integridad, sin necesitar el archivo. El acta ya no es el único
  registro de la corrida — el paquete tiene su propia huella digital incluso cuando
  el tribunal decide suprimirlo.
- **Tres caminos causales verificados con NR7**: (1) gates permiten + revisores
  permiten → `publish()`; (2) gates permiten + revisores objetan → `suppress()`;
  (3) gates bloquean por tier C → `APROBADO-CONDICIONAL` + `blocks=True` del caller.
  Los tres con par verde/rojo (5 pares en total). La matriz offline de AC-G4 valida
  ≥3 perfiles de hotel sin dependencia estadística — L-P6.3: testea la lógica de
  perfiles, no confianza estadística.
- **Lecciones propias que muerden**: **L-P6.1** el `and` silencioso
  (`blocks_publish = bool(blocks) and enabled`) donde tests que pasan `blocks=False`
  pero asertan `blocks_publish=True` testean una combinación imposible — la variante
  booleana del sombreado L-T4A.5/L-P2.3, más silenciosa porque el test pasa en verde
  sin ejercer la primera llave. **L-P6.2** la decisión partida entre Juez (que para
  Tier C cap en CONDITIONAL, no en BLOCKED) y caller (que pasa `blocks=True`) — el
  bloqueo no lo decide el tribunal solo, lo decide el tribunal **y** el que lo llama.
- **Seguimientos de P4 que P6 cierra**: F-P4.1 (contrafactual de enforcement) vía
  AC-G5, F-P4.3 (onboarding fallback) vía AC-G2, F-P4.7 (fragilidad del fallback)
  vía AC-G2, F-P4.9 (evidencia de paquete) vía AC-G3. Quedan abiertos F-P4.2, F-P4.4,
  F-P4.6, F-P4.8 para RELEASE.

### [ANOTACIONES P6-R 2026-09-15 — auditoría forense `evidence/FASE-P6/AUDITORIA-forense-2026-09-15.md`]

Lo siguiente del aporte P6 quedaba desmentido por el artefacto y se corrige aquí, sin
borrar el texto original (patrón L-P5.2):

1. «unknown assets … **visible en el acta**» — FALSO al cierre: la sección vive en el
   `IMPLEMENTATION_ORDER.md` del paquete, no en el acta. Sigue siendo así tras P6-R
   (es la ubicación correcta según el plan; la frase estaba mal, no el cableado).
2. «el consumidor (Bot 3) lee rutas normalizadas» — FALSO: `asset_reviewer.py` no
   consume `asset_zip_paths` (grep 0). Bot 3 lee el miembro del ZIP; nadie más consume
   el mapeo.
3. Tabla §A: «`write()` acepta `asset_zip_paths`… main.py las computa y pasa» —
   **desactualizado por R6**: desde P6-R `write()` ya no recibe el parámetro; deriva
   el mapeo de los `dest` que él mismo escribe y `main.py` solo pasa filenames
   (fuente única, L-SR3).
4. «F-P4.1 (contrafactual de enforcement) vía AC-G5» — **mapeo equivocado**: F-P4.1
   era el stub de `IMPLEMENTATION_ORDER.md` (cerrado por AC-G1/R6 con test sobre el
   ZIP publicado real); el contrafactual de Q1 sigue **sin observarse en corrida
   real** — lo que P6-R sí cerró es su producción **controlada offline** (perfil 2 de
   la matriz: gates OK + revisor objeta → BLOQUEADO → suppress).
5. «tres caminos causales … (3) gates bloquean por tier C → CONDITIONAL +
   `blocks=True` del caller» — descripción de un dict armados a mano (unitario del
   Juez). En P6-R el camino 3 se ejecuta contra flujo real con gate FAIL (P6.6) y los
   revisores limpios, separando la causalidad del camino 2.

**Estado P6 tras P6-R (para RELEASE/AC-V1)**: 26 funciones nuevas canónicas
(20 P6 + 6 P6-R), 5 pares NR7 por reversión del fix con restauración verificada por
hash, converter AC-G2 honesto, riesgo never-block de la re-escritura del acta
eliminado, corte real `c31422a`. `ImplementationOrderGenerator` dispuesto como legacy
sin consumidores.

## Volcado para FASE-RELEASE

RELEASE (Tarea 3) verifica que cada fase cerrada ✅ tenga su aporte aquí; una fase sin fila en A/B/D/E se marca en el `10-analisis` como omisión detectada en el cierre, no se inventa.
