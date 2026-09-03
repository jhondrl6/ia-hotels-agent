# FASE-A / Tarea A1 — Censo de registros de identidad servicio↔asset↔pain

**Plan**: ESTABILIZACION-PRE-TRIBUNAL-2026-09-03 · **Fecha**: 2026-09-03
**Método**: uso real (import/llamada), no mención en docstring. Conteos verificados
programáticamente con `./venv/Scripts/python.exe` sobre master limpio (commit `064dcde`).
**Baseline de tests confirmado**: 848 passed / 2 skipped en `tests/quality_gates` + `tests/asset_generation`
(`evidence/FASE-A/faseA_baseline_pre.txt`) — coincide con dossier §8.6.

---

## 1. Tabla de registros (13, no 12)

| # | Registro | Ubicación exacta | Nº entradas | Universo de claves | Consumidores REALES (verificados) | Estado |
|---|----------|------------------|-------------|--------------------|-----------------------------------|--------|
| 1 | `PROPOSAL_SERVICE_TO_ASSET` | `modules/asset_generation/proposal_asset_alignment.py:22-33` | **7** | service_name → asset_type | `proposal_asset_alignment.py:219,609,792` · `publication_gates.py:878,1010,1079` · `coherence_validator.py:622,672,698,703` · `service_catalog.py:14,133` · `v4_proposal_generator.py:28,1405,1549,1749` · `main.py:2487,2494` | **VIVO** (el más consumido) |
| 1b | `ALL_PROMISED_SERVICES` | `proposal_asset_alignment.py:45` | 7 | service_name | derivado de #1 · `proposal_asset_alignment.py:195,791` · `publication_gates.py:877,905,1077` | **VIVO**, ya derivado ✓ |
| 2 | `PAIN_SOLUTION_MAP` | `modules/commercial_documents/pain_solution_mapper.py:60-309` | **27** | pain_id → {assets, name, …} | `detect_pains` (mismo archivo) · `_identify_brechas` vía DEP-03 (`v4_diagnostic_generator.py:3170-3178`) · `v4_proposal_generator.py:1273-1275` (mapa inverso) | **VIVO** — contrato de detección |
| 3 | `ASSET_NAMES` | `pain_solution_mapper.py:311-328` | 16 | asset_type → texto | `pain_solution_mapper.py:784,803` (solo `asset_name` del AssetSpec) | **VIVO**, 0 claves fantasma (todas en `ASSET_CATALOG`) |
| 4 | `ELEMENTO_KB_TO_PAIN_ID` | `modules/commercial_documents/v4_diagnostic_generator.py:135-157` | 18 | KB element → (pain_id, asset, asset2) | `v4_diagnostic_generator.py:160` (`ELEMENTOS_MONETIZABLES`, **0 consumidores**), `:3083,3086` (fuerza claves a False) · `conditional_generator.py:314,325-326` | **VIVO** por :3083-3086; **contiene los 6 IDs fantasma** |
| 5 | `PAIN_TO_ASSET` | `modules/asset_generation/conditional_generator.py:234-257` | 11 | pain_id → asset\|list | único lector: `generate_for_faltantes` (`:330`), que **no tiene ningún llamador** en `modules/` ni `main.py`. Solo tests: `tests/asset_generation/test_open_graph_generation.py:123,126,221,223` | **MUERTO en producción** (hallazgo nuevo) |
| 6 | `service_brecha_candidates` | `modules/commercial_documents/v4_proposal_generator.py:1281-1289` | 7 | asset_type → [pain_id] | `_build_dynamic_breach_map` (`:1291-1317`), llamado en `:1375` | **VIVO** — alimenta columna «Problema que resuelve» |
| 7 | `ASSET_TO_PAIN_ID` | `v4_proposal_generator.py:1365-1372` | 6 | asset_type → pain_id | local a `_generate_dynamic_services_table` | **VIVO** — contiene la perla de V3 |
| 8a | `NORMALIZATION_RULES` | `modules/asset_generation/pain_ledger.py:52-79` | **26** | nombre humano → pain_id | único lector `_normalize_pain_id` (`:99`), único llamador `from_pains` (`:118`) que pasa **`pain.id`**, no `pain.name` | **MUERTO en la ruta viva** (hallazgo nuevo) |
| 8b | `PAIN_TO_PRESENCE_ASSET` | `pain_ledger.py:87-94` | 6 | pain_id → asset_type | `apply_site_verification` | **VIVO**, subconjunto válido |
| 9 | `SERVICE_CATALOG` | `modules/commercial_documents/service_catalog.py:32-82` + `:122-127` | **8** | key → (service_name, asset_type, pain_id, description) | `v4_proposal_generator.py:30,1496,1521,1718` (modo DINÁMICO **vivo**, `:1715-1720`) | **VIVO** — único registro con la tripleta completa |
| 9b | `SERVICE_TO_ASSET_LOOKUP` | `service_catalog.py:133` | 7 | service_name → asset_type | ya derivado de #1 ✓ | **derivado** ✓ |
| 10 | `pain_to_type` | `v4_diagnostic_generator.py:3542-3553` | 10 | pain_id → brecha_type (scorer) | `:3559` con **fallback silencioso `'cms_defaults'`** | **VIVO** — puente de namespace |
| 11 | `BRECHA_{SEVERITY,EFFORT,IMPACT,CHANNEL}_MAP` | `modules/financial_engine/opportunity_scorer.py:51-139,142-162,165-185,188-204` | 17/17/17/16 | brecha_type → score | único llamador `score_brechas` desde `v4_diagnostic_generator.py:3597`, alimentado **solo** por #10 | **VIVO** con 7 entradas inalcanzables |
| 12 | `mapping` (paquetes) | `modules/analyzers/gap_analyzer.py:199-201` | 3 fantasma | tipo → paquete | universo `spark` (comando **deprecado** según AGENTS.md) | **LEGACY — no se migra** (decisión §5.5) |
| **13** | **`narratives`** | **`v4_diagnostic_generator.py:3255-3336`** (guard en **`:3338-3339`**) | **16** | pain_id → narrativa comercial | `_pain_to_brecha`, llamado por `_identify_brechas:3198` | **VIVO — hallazgo nuevo, no estaba en el censo del plan** |

**Total: 13 registros** (el plan censó 12; #13 aparece al trazar el mecanismo completo de
`_identify_brechas`, aplicando la lección *«un log de rechazo no es la causa — trazar el mecanismo»*).

---

## 2. Los 6 IDs fantasma de V2 — **CONFIRMADOS los 6**, contra el registro #2 real

`PAIN_SOLUTION_MAP` (27 claves) no contiene ninguno. Los 6 viven en `ELEMENTO_KB_TO_PAIN_ID:151-156`:

| KB element | pain_id fantasma | asset declarado | ¿Equivalente canónico en #2? | Decisión A3 |
|------------|------------------|-----------------|------------------------------|-------------|
| `speakable_schema` (:151) | `no_speakable` | `voice_guide` | **NO** | `pain_id = None` (ver §3) |
| `llms_txt_exists` (:152) | `no_llms_txt` | `llms_txt` | **SÍ** — `missing_llmstxt` → `["llms_txt"]` (:160-168) | remap a `missing_llmstxt` |
| `crawler_access` (:153) | `ia_crawler_blocked` | `optimization_guide` | **SÍ** — `ai_crawler_blocked` → `["llms_txt"]` (:198-206) | remap a `ai_crawler_blocked`; el asset canónico es `llms_txt`, no `optimization_guide` |
| `brand_signals` (:154) | `weak_brand_signals` | `org_schema` | **NO** | `pain_id = None` |
| `schema_advanced` (:155) | `no_entity_schema` | `org_schema` | **NO** | `pain_id = None` |
| `contenido_factual` (:156) | `no_factual_data` | `hotel_schema` | **NO** | `pain_id = None` |

**Hallazgo nuevo (doble fantasma)**: `voice_guide` **no es un asset_type válido**. El catálogo
(`asset_catalog.py:218-229`) declara `voice_assistant_guide` con `status=AssetStatus.DEPRECATED`
(*"FASE-5: ELIMINADO de pipeline - sin brecha real"*, `promised_by=[]`). Así que `speakable_schema`
apunta a un pain inexistente **y** a un asset inexistente/deprecado.

**Los 6 KB elements sí puntúan**: `_extraer_elementos_aeo` (`:2989,2995`) y `_extraer_elementos_iao`
(`:3024,3031,3038,3051`) los emiten, y `CHECKLIST_AEO` (`:196-197`) / `CHECKLIST_IAO` (`:205-209`)
les asignan peso (20+10 AEO, 15+15+10+15 IAO). ⟹ **el score refleja el problema pero el diagnóstico
no puede narrarlo**: el pain fantasma no llega a `PAIN_SOLUTION_MAP`, luego no hay Pain, no hay brecha,
no hay asset. Es la misma familia que las 8 caídas silenciosas del dossier §4.

**Alcance de los fantasma fuera de #4** (verificados, no asumidos):
- `opportunity_scorer.py`: `no_llms_txt` (`:113,156,179,200`), `ia_crawler_blocked` (`:118,157,180,201`),
  `weak_brand_signals` (`:123,158,181,202`) — **inalcanzables**: el único `type` que recibe el scorer
  sale de `pain_to_type` (#10), cuyo rango es `{faq_schema_missing, low_gbp_score, whatsapp_conflict,
  cms_defaults, missing_reviews, poor_performance, no_hotel_schema, no_whatsapp_visible, no_og_tags,
  low_citability}`. Nunca produce los 3 fantasma. Son entradas muertas cuyo **nombre colisiona** con
  pain_ids fantasma — que es exactamente el drift.
  Otras 4 entradas muertas del scorer (`gbp_incomplete`, `data_inconsistent`, `no_meta_descriptions`,
  `poor_heading_structure`) **no son pain_ids fantasma**: pertenecen al namespace propio del scorer.
  Se registran, **no se tocan** (fuera de AC1).
- `gap_analyzer.py:199-201`: legacy `spark` → decisión §5.5.

---

## 3. La perla de V3 (`monthly_report`) — **CONFIRMADA**

`v4_proposal_generator.py:1366`: `"monthly_report": "no_faq_schema"`.

Contradicción triple verificada:
- `SERVICE_CATALOG["informe_mensual"].pain_id == "no_monthly_report"` (`service_catalog.py:79`)
- `PAIN_SOLUTION_MAP["no_monthly_report"]["assets"] == ["monthly_report"]` (`pain_solution_mapper.py:263-271`)
- `PAIN_SOLUTION_MAP["no_faq_schema"]["assets"] == ["faq_page"]` (`:79-87`) — **nunca** `monthly_report`

⟹ `ASSET_TO_PAIN_ID["monthly_report"]` atribuye el informe mensual a la brecha de FAQ. **Resuelto a
favor del canónico: `monthly_report → no_monthly_report`** (AC3).

Nota de alcance: `monthly_report` está **excluido** de `PROPOSAL_SERVICE_TO_ASSET` (BUG-10,
`proposal_asset_alignment.py:27-29`) por ser complemento always-on. La corrección de AC3 no lo
re-incorpora al conteo de alineación — solo corrige su atribución de pain.

---

## 4. El drift «8 vs 7» de V14 — **3 copias en código + 5 aserciones fósiles en tests**

Realidad estructural medida: `SERVICE_CATALOG` = **8** (7 base + AEO, `:122-127`);
`PROPOSAL_SERVICE_TO_ASSET` = **7** (8 − «Informe Mensual», excluido por BUG-10). La diferencia
**no es un error**: es una exclusión deliberada. El error es que **ningún registro la expresa** —
vive solo como comentario en otro módulo.

| # | Copia | Ubicación | Qué dice | Realidad |
|---|-------|-----------|----------|----------|
| 1 | comentario | `proposal_asset_alignment.py:35-37` | *"All 8 services … 7 base services (SEO, WhatsApp, Schema Hotel, Schema Organization, **Monthly Report**, FAQ, Open Graph) + 1 conditional AEO"* | el dict tiene 7 y Monthly Report está comentado en `:29`. Son 6 base + 1 AEO |
| 2 | docstring | `v4_proposal_generator.py:1332` (+ `:1362` *"8 filas + header"*) | *"los 8 servicios definidos en PROPOSAL_SERVICE_TO_ASSET"* | tiene 7 |
| 3 | `SERVICE_CATALOG` | `service_catalog.py:32-82,122-127` | 8 entradas, sin flag que distinga la excluida de alineación | 8 vs 7 no expresado |

**Aserciones fósiles (L-NC10) — rojo preexistente en master limpio.**
`tests/commercial_documents/test_proposal_dynamic.py`: **8 failed / 26 passed**
(`evidence/FASE-A/faseA_predinamico.txt`, master sin cambios):

| Test | Línea | Causa | ¿Drift «8 vs 7»? |
|------|-------|-------|------------------|
| `test_asset_quality_table_empty_pains_shows_all_static` | `:87` | `assert len(service_rows) == 8` → 7 | **SÍ** |
| `test_asset_quality_table_none_pains_shows_all_static` | `:100` | `assert len(service_rows) == 8` → 7 | **SÍ** |
| `test_proposal_service_to_asset_still_present` | `:261` | `len(PROPOSAL_SERVICE_TO_ASSET) == 8` → 7 | **SÍ** |
| `test_service_to_asset_lookup_has_8_entries` | `:267` | `len(SERVICE_TO_ASSET_LOOKUP) == 8` → 7 | **SÍ** |
| `test_all_service_catalog_services_have_lookup_entry` | `:273` | «Informe Mensual» ∈ #9 pero ∉ #1 | **SÍ** (estructural) |
| `test_service_to_asset_lookup_has_8_entries` (Fase3) | `:490` | `== 8` → 7 | **SÍ** |
| `test_technical_assets_table_shows_both_assets` | `:345` | espera «Optimización de Tráfico Indirecto»; `TECHNICAL_ASSET_CATALOG` tiene 1 entrada | **NO** — fuera de alcance |
| `test_no_assets_no_presence_all_excluded` | `:463` | footnote «Servicios adicionales disponibles» (D-PF1, FASE-SR-B) | **NO** — fuera de alcance |

⟹ **6 de 8 fallos son la familia del drift**; 2 son preexistentes ajenos y se registran en
§Seguimientos abiertos sin atribuirlos al plan.

> ⚠️ **Las líneas de esta tabla son del estado PRE-cambio** (`faseA_predinamico.txt`, master sin
> cambios). FASE-A editó ese archivo de tests al invertir las 6 aserciones fósiles (L-A5), así que
> los 2 supervivientes se desplazaron: `test_technical_assets_table_shows_both_assets` `:345`→**`:376`**
> y `test_no_assets_no_presence_all_excluded` `:463`→**`:494`**. Es un caso de L-A6 dentro de la
> propia evidencia. Verificado con `faseA_s5_preexist_verify.py` (`VEREDICTO: S5 confirmado`).

Contraste: `tests/asset_generation/test_proposal_alignment.py:34,38` afirma `== 7` y está **verde** —
el mismo hecho fijado con dos valores distintos en dos suites.

---

## 5. Decisión arquitectónica: **qué registro manda**

### 5.1 Decisión

**Contrato canónico de dos capas**, no un registro único:

- **Capa 1 — universo de pains**: `PAIN_SOLUTION_MAP` (#2, 27 claves) **sigue siendo** la fuente
  canónica de `pain_id`. No se modifica su contenido (la biyección con `detect_pains` es FASE-B).
  Regla: **ningún registro del sistema puede declarar un `pain_id` que no sea clave de #2**.
- **Capa 2 — identidad de servicio**: **NUEVO** `modules/common/service_identity.py` con
  `SERVICE_IDENTITIES`: una entrada congelada por servicio vendible con la tupla completa
  `(key, service_name, asset_type, pain_id, brecha_candidates, kb_elements, counts_in_alignment,
  brecha_type, description)`.

De ella **se calculan** (dejan de ser literales mantenidos a mano):
`PROPOSAL_SERVICE_TO_ASSET` · `ALL_PROMISED_SERVICES` · `SERVICE_CATALOG` · `SERVICE_TO_ASSET_LOOKUP` ·
`service_brecha_candidates` · `ASSET_TO_PAIN_ID`.
De `PAIN_SOLUTION_MAP` **se calculan**: `NORMALIZATION_RULES` · `PAIN_TO_PRESENCE_ASSET`.

### 5.2 Por qué `modules/common/`

`modules/common/` tiene **cero imports intra-proyecto** (solo `fallback_loader.py`, `yaml_loader.py`),
y ya es importado por `commercial_documents`, `financial_engine`, `data_validation`,
`orchestration_v4` y `utils`. Es el único punto del grafo desde el que los tres paquetes afectados
(`asset_generation`, `commercial_documents`, `financial_engine`) pueden importar sin ciclo:

- La dependencia hoy corre `commercial_documents → asset_generation` (`service_catalog.py:14` importa
  `proposal_asset_alignment`). Poner el canónico en `asset_generation` obligaría a
  `v4_diagnostic_generator` a importarlo a nivel de módulo (hoy solo lo hace lazy en `:3101`).
- Ponerlo en `commercial_documents` invertiría la dependencia de `proposal_asset_alignment` y
  **cerraría un ciclo** con `service_catalog.py:14`.
- `pain_ledger.py:15` ya importa `..commercial_documents.pain_solution_mapper`, así que derivar
  `NORMALIZATION_RULES` de #2 no añade arista nueva.

### 5.3 Alternativas rechazadas

| Alternativa | Por qué se rechaza |
|-------------|--------------------|
| **Promover `SERVICE_CATALOG` (#9) in situ** | Es el único con la tripleta completa, pero (a) su `pain_id` **contradice** a `service_brecha_candidates` en 2 de 7 servicios (§5.4) — promoverlo fosilizaría la contradicción; (b) vive en `commercial_documents`, lo que obliga a `proposal_asset_alignment` a importar hacia arriba y cierra el ciclo con `service_catalog.py:14`; (c) no tiene cómo expresar la exclusión BUG-10 de «Informe Mensual». |
| **Promover `PROPOSAL_SERVICE_TO_ASSET` (#1) in situ** | Es el más consumido, pero **no tiene eje de pain** (solo service_name → asset_type). Añadirle `pain_id` lo convertiría en el registro nuevo, pero dentro del módulo que importan Gate 9, `coherence_validator` y `publication_gates` (mayor radio de explosión), y seguiría sin ser importable por el scorer de `financial_engine`. |
| **Colapsar todo en `PAIN_SOLUTION_MAP` (#2)** | 27 pains ≠ 8 servicios: la mayoría de los pains no tiene servicio vendible. Añadir `service_name`/`kb_elements`/`brecha_type` a 27 entradas mezclaría el contrato de detección con metadatos comerciales y pondría FASE-A en conflicto directo con FASE-B (biyección mapa↔emisión). |
| **Unificar el namespace del scorer al `pain_id` (eliminar `pain_to_type`)** | `gbp_incomplete`, `data_inconsistent`, `no_meta_descriptions`, `poor_heading_structure` son brecha_types sin pain equivalente. Eliminar el puente es un cambio de **semántica de scoring** (dinero), no de identidad. A registra el puente y lo hace explícito y testeado; no lo elimina. |
| **Crear una tabla canónica `pain_id → texto narrativo`** | Violación directa del guardrail **L-NC4**. El registro no lleva narrativa: solo referencia ids. `narratives` (#13) y `PAIN_SOLUTION_MAP.name/description` se quedan donde están. |

### 5.4 Contradicción nueva no censada por el plan: trigger ≠ atribución

Verificada programáticamente. Para el mismo asset, el pain que **dispara** el servicio (#9, modo
DINÁMICO vivo en `v4_proposal_generator.py:1715-1720`) y el pain que se le **atribuye** en la columna
«Problema que resuelve» (#6) no coinciden:

| asset | `SERVICE_CATALOG.pain_id` (trigger) | `service_brecha_candidates` (atribución) | ¿coinciden? |
|-------|-------------------------------------|------------------------------------------|-------------|
| `optimization_guide` | `poor_performance` | `low_seo_score`, `low_content_length` | **NO** |
| `llms_txt` | `low_ia_readiness` | `missing_llmstxt` | **NO** |
| `whatsapp_button` | `no_whatsapp_visible` | `whatsapp_conflict`, `no_whatsapp_visible` | sí |
| `hotel_schema` | `no_hotel_schema` | `no_hotel_schema` | sí |
| `org_schema` | `no_org_schema` | `no_org_schema` | sí |
| `faq_page` | `no_faq_schema` | `no_faq_schema` | sí |
| `open_graph` | `no_og_tags` | `no_og_tags` | sí |

Ambos valores están **soportados** por `PAIN_SOLUTION_MAP` (`poor_performance → [performance_audit,
optimization_guide]`; `low_ia_readiness → [hotel_schema, llms_txt, local_content_page]`), así que
ninguno es fantasma: son **dos mitades de una decisión que ningún registro expresa**.

**Decisión: preservar ambos comportamientos y hacer explícita la divergencia.** El registro canónico
declara `pain_id` (trigger) y `brecha_candidates` (atribución) como campos separados, y un contract
test exige que toda divergencia esté en `REVIEWED_TRIGGER_DIVERGENCES` (2 entradas: `seo_local`,
`optimizacion_ia_generativa`).

**Por qué no resolverla aquí**: cambiar el trigger altera qué servicios aparecen en la propuesta
(modo DINÁMICO vivo) y cambiar la atribución altera qué brecha/costo se narra — ambos son
**narrativa comercial visible**, y ambos son precisamente el objeto de FASE-C (punto 8, propuesta
dinámica). Resolverlo en A destruiría el punto de comparación de C, igual que la trampa A5 que el
prompt prohíbe tocar. **Se entrega a FASE-C como insumo: vaciar `REVIEWED_TRIGGER_DIVERGENCES`.**

### 5.5 Registros fuera de migración (decisión explícita, no grep=0)

| Registro | Decisión | Justificación |
|----------|----------|---------------|
| #12 `gap_analyzer.py:199-201` | **LEGACY — no se migra** | Universo `spark`, comando marcado ⚠️ Deprecado en AGENTS.md («Legacy, usar `v4complete`»). Fuera de `modules/commercial_documents` + `modules/asset_generation`, luego fuera del grep de AC1. |
| #11 entradas muertas no-fantasma del scorer (`gbp_incomplete`, `data_inconsistent`, `no_meta_descriptions`, `poor_heading_structure`) | **Se registran, no se tocan** | No son pain_ids fantasma; son namespace propio del scorer. Eliminarlos es cambio de scoring, no de identidad. |
| #5 `PAIN_TO_ASSET` | **Se deriva del canónico** (no se borra) | `generate_for_faltantes` no tiene llamador en producción, pero 4 aserciones de `tests/asset_generation/test_open_graph_generation.py` lo leen. Derivarlo mantiene el contrato público y elimina la copia. |
| #8a `NORMALIZATION_RULES` | **Se deriva de #2** | Nunca dispara en la ruta viva (`from_pains` pasa `pain.id`, las reglas están keyed por nombre humano). Derivarlo corrige de paso 2 defectos latentes a costo conductual cero (§6). |
| #13 `narratives` | **Se registra + contract test de subconjunto; NO se cambia su conducta** | Cambiar el guard `:3338-3339` activaría 11 brechas nuevas en el diagnóstico = narrativa comercial. Es insumo de FASE-B (§6). |

---

## 6. Hallazgos nuevos (no estaban en el dossier ni en el plan)

**N-A1 — `narratives` (#13) descarta silenciosamente 11 pain_ids.**
`v4_diagnostic_generator.py:3338-3339`: `if pain.id not in narratives: return None`.
`narratives` tiene 16 claves; `PAIN_SOLUTION_MAP` tiene 27. Los 11 descartados:

```
no_motor_reservas   low_ota_divergence   missing_llmstxt   no_ga4_enhanced
no_schema_reviews   no_ssl               missing_alt_text  no_monthly_report
no_blog_content     no_social_links      low_content_length
```

Consecuencia: un pain puede estar **en el ledger** (que se alimenta de `detect_pains` directamente en
`v4_asset_orchestrator.py:280`) y **ausente del diagnóstico** (que pasa por `_pain_to_brecha`). Es una
caída silenciosa de la misma familia que las 8 del dossier §4, pero **aguas abajo de `detect_pains`** —
el dossier las buscó aguas arriba.

**⟹ Precondición dura de FASE-B**: de los 9 pains muertos de V1, `missing_llmstxt` está en esta lista.
Si FASE-B le añade punto de emisión en `detect_pains` sin tocar #13, el pain entrará al ledger y
**seguirá sin aparecer en el diagnóstico**: el fix sería inerte. FASE-B debe tratar #13.

**N-A2 — `NORMALIZATION_RULES` tiene una clave stale y una entrada faltante.**
- `PAIN_SOLUTION_MAP["no_whatsapp_visible"]["name"] == "Sin WhatsApp Visible"`, y `detect_pains:364`
  emite `name="Sin WhatsApp Visible"`; la regla en `pain_ledger.py:53` dice **"No WhatsApp Visible"**.
  Nunca matchea.
- Falta `low_seo_score` ("SEO Local Bajo") ⟹ 26 reglas para 27 pains.
Ambos se corrigen gratis al derivar de #2 (§5.5). Costo conductual cero porque la tabla no dispara
en la ruta viva — pero si alguna vez se cablea un consumidor que pase nombres, hoy produciría
`sin_whatsapp_visible` y `seo_local_bajo`, ids inexistentes.

**N-A3 — `ELEMENTOS_MONETIZABLES` (`v4_diagnostic_generator.py:159-162`) tiene 0 consumidores.**
Se deriva de #4 filtrando por `asset is not None`, no por `pain_id`: con los 6 fantasma sigue
declarando monetizables elementos cuyo pain no existe. Muerto, pero es una trampa para quien lo use.

**N-A4 — `voice_guide` es un asset_type fantasma** (§2). El real es `voice_assistant_guide`, DEPRECADO.

**N-A5 — El mismo hecho está fijado con dos valores en dos suites**: `== 7` en
`tests/asset_generation/test_proposal_alignment.py:34,38` (verde) y `== 8` en
`tests/commercial_documents/test_proposal_dynamic.py:261,267,490` (rojo). Ninguna de las dos es un
contrato narrativa↔fuente: ambas son valores fósiles (L-NC10).

---

## 7. Verificación de premisas (lección ROADMAP v4.0→v4.1)

*«Revalidar citas de código NO revalida premisas.»* Cada afirmación de este censo se obtuvo por
ejecución o grep sobre master limpio, no por lectura del dossier:

- Conteos (27/16/7/8/26/6/25) → script Python importando los módulos reales.
- Rojo preexistente de `test_proposal_dynamic.py` → corrida real (8 failed / 26 passed).
- Consumers → grep de import/uso, excluyendo `temp/`, `Archives/`, `__pycache__`.
- Alcance del scorer → grep de `score_brechas` (1 solo llamador) + rango de `pain_to_type`.

**Correcciones al plan/dossier**: (a) son **13** registros, no 12; (b) el drift «8 vs 7» tiene
**3 copias en código + 6 aserciones fósiles en tests**, no 3; (c) la diferencia 8−7 **no es un bug**
sino una exclusión deliberada (BUG-10) que ningún registro expresa — corregirla como «unificar a 8»
habría sido el fix equivocado; (d) `ASSET_CATALOG` tiene **25** entradas.

> Las secciones 1-7 son el censo **de A1** y quedan intactas como registro histórico. Las correcciones
> halladas al ejecutar A2-A4 —y la hallada tras el cierre de A (C-5)— están en §8.

---

## 8. Correcciones post-censo (halladas al ejecutar A2-A4 y tras el cierre de A)

### 8.1 El censo de A1 se corrigió a sí mismo en 5 puntos

| # | A1 decía | Real | Cómo se detectó |
|---|----------|------|-----------------|
| C-1 | **13** registros | **14** | Apareció `modules/quality/asset_semantics_validator.INVALID_MAPPINGS` (4 entradas), fuera de los dos paquetes acotados por el grep de AC1. Su propio comentario `:23-25` documenta una auditoría FASE-2 que halló sus claves **invertidas** (asset_type donde iba pain_id) ⟹ la perla de V3 es un fósil **no corregido** de esa misma inversión. No se modificó (fuera de alcance de A) — registrado como S9 para FASE-H |
| C-2 | N-A2: «`NORMALIZATION_RULES` tiene 1 entrada faltante» | Faltan **2** (`SEO Local Bajo`→`low_seo_score`, `Sin WhatsApp Visible`→`no_whatsapp_visible`) **más 1 clave obsoleta** (`No WhatsApp Visible`) | Al derivarlo de Capa 1 y diffar contra el literal |
| C-3 | `ASSET_TO_PAIN_ID` tiene 9 entradas | **6** entradas | Al derivarlo: el consumidor único (`v4_proposal_generator.py:1410`) confirma que 6 bastan |
| C-4 | `opportunity_scorer.py` contiene IDs fantasma y hay que limpiarlo | **No son pain_id**: son claves legítimas de `brecha_type` (namespace propio de 17 entradas), puenteado por `pain_to_type` (10 entradas + fallback silencioso `'cms_defaults'`). **El archivo NO se modificó** | Al buscar el registro que legítimamente posee cada string (lección L-A3). Eliminarlos habría roto `tests/financial_engine/test_opportunity_scorer*.py` en código dinero-adyacente sin curar nada |
| C-5 | El censo enumeró **14** registros de identidad | **15** — falta `config/regional_benchmarks.yaml::pain_narratives`, con **4 copias literales** (una por región) de las **mismas 16** claves pain_id→impacto, **más 16 fallbacks hardcodeados** en Python: **80 literales de 16 valores**, todos idénticos entre sí. 0 huérfanos vs Capa 1 y **los mismos 11 ausentes**. No se modificó: cae en FASE-B, que es quien decide `narratives` ⟹ **S14** | Al auditar N-A1 (`evidence/FASE-A/faseA_yaml_narratives_audit.py`, `faseA_yaml_region_blind.py`): el dict `narratives` de `_pain_to_brecha` resulta no ser el dueño de esos números sino su **quinta copia** |

### 8.2 Resolución final de los 15 registros

| Tratamiento | Cantidad | Registros |
|-------------|----------|-----------|
| **Canónico nuevo (Capa 2)** | 1 | `modules/common/service_identity.py::SERVICE_IDENTITIES` (8 entradas congeladas) |
| **Capa 1 (universo de pain_id, intacto)** | 1 | `PainSolutionMapper.PAIN_SOLUTION_MAP` (27) |
| **DERIVADOS del canónico** | 6 | `PROPOSAL_SERVICE_TO_ASSET` · `ALL_PROMISED_SERVICES` · `SERVICE_CATALOG` · `ASSET_TO_PAIN_ID` · `service_brecha_candidates` · `NORMALIZATION_RULES` *(este último de Capa 1)* |
| **VALIDADOS contra Capa 1** (literales, con razón registrada — DA9) | 4 | `PAIN_TO_ASSET` (11, enruta generación no venta) · `ELEMENTO_KB_TO_PAIN_ID` (otra pregunta) · `PAIN_TO_PRESENCE_ASSET` (6; derivado = 13 y cambia `apply_site_verification` → S8/FASE-F) · `INVALID_MAPPINGS` (fuera de alcance → S9) |
| **Fuera de alcance de A** | 3 | `gap_analyzer` (legacy, decisión registrada en `01-plan-maestro`) · `opportunity_scorer.pain_to_type` (namespace distinto → S7) · `regional_benchmarks.yaml::pain_narratives` (4 copias + fallbacks Python; hallado post-cierre, decide FASE-B → **S14**) |

### 8.3 Contrafactual: delta cero medido

`evidence/FASE-A/faseA_contrafactual.py` → `faseA_contrafactual.txt`. Comparó cada registro derivado contra el
literal que reemplazó, **importando ambos**:

- `PROPOSAL_SERVICE_TO_ASSET`: contenido **y orden** idénticos.
- `service_brecha_candidates`: contenido **y orden** idénticos.
- `SERVICE_CATALOG`: claves y orden idénticos.
- `ASSET_TO_PAIN_ID`: 3 deltas (`open_graph`, `optimization_guide`, `org_schema`: `SKIP(sin pain)` →
  `IMPLEMENT`) pero **el render no cambia**: el consumidor solo descarta una fila cuando `is_valid is
  False`; con `pain_id is None` el bloque `if pain_id:` se salta y la fila se renderiza normal.
  `monthly_report` y `whatsapp_conflict_guide` cambian desde BLOCKED pero tienen `iterado=False`
  (nunca se alcanzan).
- **Reproducibilidad verificada el 2026-09-03**: el script se re-ejecutó desde un cwd ajeno (`temp/`)
  contra el árbol post-FASE-A y su salida es **idéntica** a `faseA_contrafactual.txt` (`diff` vacío).
  La evidencia durable es re-ejecutable, no una captura muerta.
- Tablas renderizadas: `_generate_dynamic_services_table` **7 filas** con descripciones correctas;
  `_generate_asset_quality_table` **7 filas**.
- **Bug latente corregido de paso** (S10): `monthly_report` ya valida como IMPLEMENT en vez de ser
  bloqueado por un guard anti-alucinación que lo comparaba contra `no_faq_schema`.

### 8.4 Desvíos respecto de la lista de tareas del prompt

| Desvío | Motivo |
|--------|--------|
| La copia #1 del drift (`proposal_asset_alignment.py:35`) se corrigió en **A3**, no en A4 | Vive en el mismo bloque que la derivación; separarlo habría dejado un commit intermedio incoherente |
| Los 6 IDs fantasma (tarea de A4 por archivo) se corrigieron en **A3** | El grep de AC1 tiene alcance de fase, no de tarea |
| `service_brecha_candidates` (`:1281-1289`) se derivó en A4 aunque `dependencias-fases.md` asigna esa región también a C2 | A4 solo cambió la **fuente de identidad**; la **lógica** quedó intacta, como exigía la restricción explícita de A4. C2 reescribe la lógica sobre identidad ya unificada |
| `opportunity_scorer.py` figuraba en A4 y no se tocó | Ver C-4 |
| Se modificaron 2 archivos no previstos: `service_catalog.py` y `tests/commercial_documents/test_proposal_dynamic.py` | El primero es la copia #2 del drift (AC2 lo exige). El segundo tenía 6 aserciones fósiles, una de las cuales codificaba el invariante **invertido** (L-A5) |

### 8.5 Verificación de cierre (medida, no supuesta)

| Check | Resultado |
|-------|-----------|
| Contract tests — curva TDD | ROJO **27 failed / 9 passed / 1 skipped** → post-canónico **18 failed / 29 passed** → post-A3 **8 failed / 29 passed** → final **37 passed / 0 failed** (21 funciones) |
| Grep IDs fantasma (AC1) | **OK: 0** en `modules/commercial_documents` + `modules/asset_generation` |
| Baseline NR5 | **848 passed / 2 skipped / 11 warnings** — igual al pre-cambio. ⚠️ No «byte-idéntico»: `diff faseA_baseline_{pre,post}.txt` da **1 línea**, la duración (`7.05s` → `6.02s`) |
| `run_all_validations.py --quick` | **7/7 PASSED** |
| `validate_agents_md.py` | **6 PASS / 0 FAIL** |
| Regresión amplia | `tests/financial_engine` + `data_validation` + `orchestration_v4`: **807 passed, 1 xpassed, 0 failed** |
| Suites de diagnóstico | `test_aeo_score` + `test_iao_score` + `test_diagnostic_generator` + `test_diagnostic_brechas`: **113 passed** |
| `test_proposal_dynamic.py` | 8 failed / 26 passed → **2 failed / 32 passed**. Los 2 restantes tienen la **aserción idéntica** a la evidencia pre-cambio `faseA_predinamico.txt` ⟹ preexistentes, **no atribuibles al plan** (S5). ⚠️ No «byte-idénticos»: difieren direcciones de objeto, duración y el número de línea del propio test (`:345`→`:376`, `:463`→`:494`), desplazado porque FASE-A lo editó. Reproducible: `faseA_s5_preexist_verify.py` → `VEREDICTO: S5 confirmado` |

