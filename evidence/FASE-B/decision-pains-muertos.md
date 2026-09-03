# FASE-B / B1 — Decisión por pain muerto (11 filas)

**Plan**: ESTABILIZACION-PRE-TRIBUNAL-2026-09-03 / FASE-B
**Fecha**: 2026-09-03
**AC que cierra**: AC4 (biyección triple `PAIN_SOLUTION_MAP` ↔ `detect_pains` ↔ `narratives`)
**Estado**: 11/11 filas decididas

> ⚠️ Los archivos `fase_b_preexist.txt`, `fase_b_safe*.txt`, `fase_b_test.txt` y
> `verify_breach_consistency_static*` que ya estaban en `evidence/FASE-B/` pertenecen a la
> FASE-B de **otro plan** (commit `d2a9700`, 2026-08-05, «tabla de servicios dinámica desde
> opportunity_scores»). **No son evidencia de esta fase** y no se citan aquí.

---

## 0. Punto de partida medido

Re-ejecutado `evidence/FASE-A/faseA_narratives_audit.py` antes de decidir (mismos números que
`faseA_narratives_audit.txt`):

| Conjunto | Cardinal | Fuente |
|----------|----------|--------|
| Capa 1 — `PAIN_SOLUTION_MAP` | **27** | `pain_solution_mapper.py:60` |
| `narratives` en `_pain_to_brecha` | **16** | `v4_diagnostic_generator.py:3263-3344` |
| Puntos de emisión en `detect_pains` + `_detect_analytics_pains` | **18** | `pain_solution_mapper.py:339`, `:664` |
| Capa 1 − `narratives` | **11** | — |
| `narratives` − Capa 1 (huérfanos) | **0** ✅ | — |

Los 18 emitidos: `no_whatsapp_visible` `:362`, `whatsapp_conflict` `:373`, `no_faq_schema` `:384`,
`no_hotel_schema` `:395`, `low_gbp_score` `:406`, `poor_performance` `:418`, `no_org_schema` `:429`,
`missing_reviews` `:440`, `low_ota_divergence` `:457`, `metadata_defaults` `:477`,
`ai_crawler_blocked` `:497`, `low_citability` `:509`, `low_ia_readiness` `:521`, `no_og_tags` `:535`/`:548`,
`low_seo_score` `:561`, `no_analytics_configured` `:684`, `low_organic_visibility` `:694`/`:716`,
`no_ga4_enhanced` `:705`. 18 + 9 muertos = 27 ✅.

---

## 1. Corrección a la premisa de N-A1 (medida en B1)

N-A1 parte los 11 ausentes en «9 muertos» + «**2 vivos que se emiten y se descartan hoy en
producción**». La segunda mitad **no se sostiene**: el script de FASE-A cuenta *puntos de emisión
en el fuente* por regex (`Pain(id="...")`), no *emisiones alcanzables*. Medido contra la verdad
del mundo, los dos están muertos:

### `no_ga4_enhanced` — muerto por guardia insatisfacible

```python
# pain_solution_mapper.py:703-704
elif status and hasattr(status, "is_enhanced"):
    if not status.is_enhanced:
```

`is_enhanced` **no existe en el repositorio**. Grep repo-wide (excluyendo `venv/` y `temp/`)
devuelve exactamente dos líneas: `:703` y `:704`, las dos del propio guardia.

- `data_models/analytics_status.py` — `AnalyticsStatus` declara `ga4_available`, `ga4_error`,
  `ga4_status_text`, `profound_*`, `semrush_*`, `gsc_*`, `timestamp`. **Sin `is_enhanced`.**
- `main.py:2408-2419` — única construcción de `AnalyticsStatus` en el pipeline; asigna
  `ga4_available`, `ga4_status_text`, `profound_available`, `profound_status_text`,
  `semrush_available`, `semrush_status_text`. **Nunca `is_enhanced`.**

⟹ `hasattr(status, "is_enhanced")` es **siempre False** ⟹ el pain **nunca dispara**.
Es el **décimo pain muerto**, no una caída silenciosa viva.

### `low_ota_divergence` — muerto por el guard `__iter__` de V7 (ya documentado)

```python
# pain_solution_mapper.py:447  (era :453 al medirse en B1; B2 desplazó el archivo
#                               al añadir las 3 ramas de emisión nuevas — L-A6)
if direct_field and hasattr(direct_field.value, '__iter__'):
```

El valor es **siempre float**: `main.py:1865` `direct_channel_pct = canal_directo / 100`,
`main.py:1890` `= 0.20`, `main.py:2161` `float(direct_channel_pct)`; se carga en
`ValidatedField(value=direct_channel_pct)` en `main.py:2309-2315`. Un `float` no tiene
`__iter__` ⟹ la rama nunca entra. V7 (FASE-H) es quien lo arregla; **no se toca aquí**.

**Consecuencia para B1**: la pregunta del grupo (b) cambia. Para `no_ga4_enhanced` ya no es
«narrativa o retiro» sino «retiro o inventar una señal que no existe». Para `low_ota_divergence`
la conclusión de N-A1 **sí se mantiene intacta**: hay que darle narrativa **ahora**, porque cuando
FASE-H arregle el guard el pain empezará a disparar y rebotaría en `:3346`.

---

## 2. Restricción estructural descubierta: el retiro está bloqueado para 6 de los 11

El registro canónico de FASE-A **no es editable en esta fase** (`05-prompt` §Restricciones:
«Dependencia que no se puede modificar»). Tres contratos lo protegen:

| Contrato | Qué exige | Efecto sobre un retiro |
|---|---|---|
| `tests/common/test_service_identity_registry.py:540` `test_elemento_kb_valida_contra_capa1` | todo `ELEMENTO_KB_TO_PAIN_ID[k][0]` no-None ∈ Capa 1 | bloquea retirar pains referidos en `v4_diagnostic_generator.py:139-165` — **región fuera del alcance permitido** (`:3246-3347`) |
| ídem `:552` `test_pain_to_asset_valida_contra_capa1` | todo `PAIN_TO_ASSET[k]` ∈ Capa 1 | bloquea retirar pains referidos en `conditional_generator.py:244-263` |
| ídem `:242` `test_pain_ids_canonicos_existen_en_pain_solution_map` | `SERVICE_IDENTITIES[*].pain_id` y `.brecha_candidates` ∈ Capa 1 | bloquea retirar pains referidos en `modules/common/service_identity.py` — **archivo prohibido** |

Mapa de referencias (verificado por grep, una por una):

| pain_id | `ELEMENTO_KB_TO_PAIN_ID` | `PAIN_TO_ASSET` | Capa 2 `service_identity.py` | ¿Retirable sin tocar archivo prohibido/fuera de región? |
|---|---|---|---|---|
| `no_motor_reservas` | — | — | — | ✅ sí (pero huérfaniza `barra_reserva_movil`, ver §3.8) |
| `no_ssl` | `"ssl"` `:142` | `:244` | — | ❌ no |
| `no_schema_reviews` | `"schema_reviews"` `:144` | `:247` | — | ❌ no |
| `missing_alt_text` | `"imagenes_alt"` `:151` | `:259` | — | ❌ no |
| `no_monthly_report` | — | — | `pain_id="no_monthly_report"` `:127` | ❌ no |
| `no_blog_content` | `"blog_activo"` `:152` | `:261` | — | ❌ no |
| `no_social_links` | `"redes_activas"` `:153` | `:263` | — | ❌ no |
| `low_content_length` | — | — | `brecha_candidates` de `seo_local` `:78` | ❌ no |
| `missing_llmstxt` | `"llms_txt_exists"` `:160` | — | `brecha_candidates` de `optimizacion_ia_generativa` `:138` | ❌ no |
| `no_ga4_enhanced` | — | — | — | ✅ sí |
| `low_ota_divergence` | — | — | — | ✅ sí |

⟹ **Solo 3 de los 11 son retirables limpiamente.** Para los demás, la decisión honesta es
*implementar* (si hay señal real) o *diferir* (con seguimiento abierto). Ninguno puede marcarse
«retirar» sin violar una restricción explícita del prompt.

---

## 3. Las 11 decisiones

Regla de severidad adoptada para toda emisión nueva (no se inventan valores): la severidad se
deriva del `estimated_impact` que **Capa 1 ya declara** para ese pain (`high`→`high`,
`medium`→`medium`, `low`→`low`).

### Grupo (a) — los 9 pains muertos de V1

#### 3.1 `missing_llmstxt` → **IMPLEMENTAR** ✅

- **Señal de dato (verificable)**: `audit_result.ia_readiness.components["llms_txt"] == 0`.
  El componente se pobla con una **sonda HTTP real**: `v4_comprehensive.py:1295-1296`
  `http_client.get(f"{probe_base}/llms.txt")` → `has_llmstxt = status_code == 200`, y
  `ia_readiness_calculator.py:53` `components["llms_txt"] = 100 if has_llmstxt else 0`.
  `ia_readiness` se cablea al audit result en `v4_comprehensive.py:688`. **Caso confirmado**
  en la corrida SalenteReal (`llms_txt=0`).
- **Justificación**: es la caída #4 del dossier §4 y el caso más claro de V1 — había una brecha
  real, el asset `llms_txt` se generó, y el diagnóstico no la mencionó. Capa 2 ya le atribuye la
  brecha al servicio `optimizacion_ia_generativa` (`service_identity.py:138`); sin emisión, esa
  atribución está muerta.
- **Narrativa que requiere**: sí. `nombre` = «Sin llms.txt», `detalle` = «No existe archivo
  /llms.txt para indexación IA» (ambos ya en Capa 1 `:166-167`). Severidad `low`
  (`estimated_impact: "low"` `:165`).
- **Peso de impacto**: 0.08 (ver §4).
- **Asset**: `llms_txt` IMPLEMENTED (`asset_catalog.py:207-215`), no se huérfaniza.
- **Nota — señal rival defectuosa**: `ELEMENTO_KB_TO_PAIN_ID["llms_txt_exists"]` se alimenta de
  `_extraer_elementos_iao:3032-3036`, que busca la subcadena `'llms_txt'` en
  `str(audit_result.schema.properties)` — un proxy sin relación con la existencia del archivo.
  La emisión nueva usa la sonda HTTP real, **no** ese proxy. Ver seguimiento S-B3.

#### 3.2 `missing_alt_text` → **IMPLEMENTAR** ✅

- **Señal de dato (verificable)**: `audit_result.seo_elements.imagenes_alt is False`, con
  `seo_elements.images_without_alt` como recuento para la descripción. Detección real con
  BeautifulSoup: `seo_elements_detector.py:21` (`imagenes_alt`) y `:26` (`images_without_alt`),
  cableada al audit result en `v4_comprehensive.py:533`/`:689`.
- **Justificación**: señal existente, ya consumida por `CHECKLIST_SEO["imagenes_alt"]` (15 pts)
  y por `ELEMENTO_KB_TO_PAIN_ID["imagenes_alt"]` — el KB ya declara que este gap corresponde a
  este pain; solo faltaba la emisión.
- **Narrativa que requiere**: sí. `nombre` = «Imágenes sin Texto Alternativo», `detalle` =
  «Las imágenes no tienen atributo alt descriptivo» (Capa 1 `:260-261`). Severidad `medium`
  (`estimated_impact: "medium"` `:259`).
- **Peso de impacto**: 0.10 (ver §4).
- **Anti-falso-positivo**: solo emite cuando `seo_elements` **existe** (página realmente
  descargada y parseada), mismo patrón que `no_og_tags` en `:532`. Si `seo_elements is None`
  no hay medición y no se emite — no se colapsa «ausente» con «vacío».
- **Asset**: `alt_text_guide` IMPLEMENTED (`asset_catalog.py:256-264`).

#### 3.3 `no_social_links` → **IMPLEMENTAR** ✅

- **Señal de dato (verificable)**: `audit_result.seo_elements.redes_activas is False`, con
  `social_links_found` (lista de URLs) para la descripción. Detección real:
  `seo_elements_detector.py:22` y `:27`, cableada igual que 3.2.
- **Justificación**: idéntica a 3.2 — señal existente y ya declarada por
  `ELEMENTO_KB_TO_PAIN_ID["redes_activas"]` y por `CHECKLIST_GEO["redes_activas"]` (10 pts).
- **Narrativa que requiere**: sí. `nombre` = «Sin Presencia en Redes Sociales», `detalle` =
  «No se detectan enlaces a redes sociales» (Capa 1 `:287-288`). Severidad `low`
  (`estimated_impact: "low"` `:286`).
- **Peso de impacto**: 0.08 (ver §4).
- **Anti-falso-positivo**: mismo guard de presencia que 3.2.
- **Asset**: `social_strategy_guide` IMPLEMENTED (`asset_catalog.py:278-286`).

#### 3.4 `no_ssl` → **DIFERIR** ⏸

- **Señal de dato disponible**: **ninguna verificable.** El único candidato en el código es
  `audit_result.url.startswith('https')` (`_extraer_elementos_seo:2919`, replicado en
  `_compute_web_score:599`) — que mide **la URL de entrada escrita por el usuario**, no el
  certificado del sitio. El campo `ssl_detected` que declara Capa 1 (`:240`) no existe en ningún
  auditor; grep repo-wide solo lo encuentra en `asset_catalog.py:235` (`required_field`) y en el
  propio mapa.
- **Por qué no se implementa**: el pipeline descarga la página con éxito por HTTPS en toda corrida
  real, lo que ya demuestra que el sitio tiene SSL. El proxy solo dispararía cuando el usuario
  escribió `http://`, produciendo un «Sin SSL/HTTPS» **falso** sobre un sitio que sí lo tiene. Es
  exactamente la clase de defecto que prohíbe la regla dura (el `ai_crawler_blocked` con score
  0.50 EXACTO del dossier §3).
- **Por qué no se retira**: bloqueado por §2 — `ELEMENTO_KB_TO_PAIN_ID["ssl"]` (`:142`, fuera de
  la región editable) y `PAIN_TO_ASSET["no_ssl"]` (`conditional_generator.py:244`).
- **Asset**: `ssl_guide` IMPLEMENTED, `promised_by=["no_ssl"]` (`asset_catalog.py:232-240`).
  Queda inalcanzable — igual que hoy; no se huérfaniza porque no se retira el pain.
- **Señal que haría falta**: sonda TLS real (intentar `http://` y verificar ausencia de
  redirección a HTTPS, o inspeccionar el certificado). → **Seguimiento S-B1**.

#### 3.5 `no_schema_reviews` → **DIFERIR** ⏸

- **Señal de dato disponible**: **ninguna verificable.** El único proxy es
  `bool(audit_result.gbp.rating)` (`_extraer_elementos_seo:2939`, replicado en
  `_compute_web_score:625`) — mide la calificación **en Google**, no el markup `aggregateRating`
  **en el sitio**. Grep repo-wide: ningún auditor detecta `aggregateRating`; las únicas apariciones
  son de *generación* (`conditional_generator.py:939-954`, `open_graph_generator.py:355`) y de
  validación de assets (`geo_enriched_bridge.py:181`). `SchemaValidation.properties`
  (`data_structures.py:187`) se llena desde `report.get("properties", {})`
  (`v4_comprehensive.py:741`) sin rastro de `aggregateRating`.
- **Por qué no se implementa**: el proxy **invierte la verdad**. SalenteReal tiene 986 reseñas y
  4.5 en Google ⟹ `bool(gbp.rating)` es True ⟹ el elemento se marcaría cumplido en un sitio que
  no tiene ningún markup de reseñas. Implementar sobre esa base produce un falso negativo
  garantizado en el caso real que originó el plan.
- **Por qué no se retira**: bloqueado por §2 (`ELEMENTO_KB_TO_PAIN_ID["schema_reviews"]` `:144`
  y `PAIN_TO_ASSET` `:247`).
- **Asset**: `hotel_schema` IMPLEMENTED y reachable vía `no_hotel_schema`; no se huérfaniza.
- **Hallazgo colateral (no se arregla aquí)**: `CHECKLIST_SEO["schema_reviews"]` (10 pts) y
  `CHECKLIST_GEO["schema_reviews_geo"]` (15 pts) puntúan hoy sobre ese proxy equivocado, así que
  25 puntos del score SEO/GEO se otorgan por tener reseñas **en Google**. Alimenta `low_seo_score`
  y el score mostrado al cliente. → **Seguimiento S-B2**.

#### 3.6 `no_blog_content` → **DIFERIR** ⏸

- **Señal de dato disponible**: **ninguna.** El código lo declara explícitamente:
  `elementos["blog_activo"] = "no_evaluado"` (`_extraer_elementos_seo:2937`) con el comentario
  «PATCH-A: marcador explícito (detección real requiere HTML scrapeo)». El campo `blog_detected`
  que declara Capa 1 (`:276`) no existe en ningún auditor.
- **Por qué no se implementa**: no hay nada que leer. `"no_evaluado"` es un marcador de
  *no-medicón*, no un False; emitir sobre él inventaría la brecha.
- **Por qué no se retira**: bloqueado por §2 (`ELEMENTO_KB_TO_PAIN_ID["blog_activo"]` `:152`,
  `PAIN_TO_ASSET` `:261`).
- **Asset**: `blog_strategy_guide` IMPLEMENTED (`asset_catalog.py:267-275`), inalcanzable — igual
  que hoy.
- **Hallazgo colateral**: `CHECKLIST_SEO["blog_activo"]` (10 pts) **nunca** se puede ganar
  (`"no_evaluado" is not True` ⟹ `calcular_cumplimiento` y `_compute_web_score:630` no lo suman),
  así que el score SEO de todo hotel está topado a 90/100. No cambia el disparo de `low_seo_score`
  (umbral 40) pero sí el número que se le muestra al cliente. → incluido en **S-B2**.

#### 3.7 `low_content_length` → **DIFERIR** ⏸ (decisión preferida: retirar, bloqueada)

- **Señal de dato disponible**: derivable en principio (`CitabilityScore.block_scores[*]["word_count"]`,
  `citability_scorer.py:22`/`:38`), **pero el código ya enruta esa señal a otro pain**:
  - `ELEMENTO_KB_TO_PAIN_ID["contenido_extenso"] = ("low_citability", "optimization_guide", None)`
    (`:147`) — el elemento de KB «contenido extenso» apunta a `low_citability`, no a
    `low_content_length`.
  - `_extraer_elementos_iao:3025-3029` calcula `contenido_extenso` con la **expresión idéntica**
    a `citability_score` (`:3018-3022`): `citability.overall_score > 50`.
  - `low_citability` ya emite en `:509` sobre `citability.overall_score < 50` y mapea al **mismo
    asset** (`optimization_guide`, Capa 1 `:210` y `:291`).
- **Por qué no se implementa**: sería **reportar la misma brecha dos veces con dos nombres**.
  Infla `brechas_detectadas`, distorsiona `coverage_ratio` y el denominador del gate
  `coverage_no_silent_drop` — números dinero-adyacentes.
- **Por qué no se retira** (aunque es lo correcto): bloqueado por §2 —
  `service_identity.py:78` `brecha_candidates=("low_seo_score", "low_content_length")` del
  servicio `seo_local`, y Capa 2 es archivo prohibido. Además `REVIEWED_TRIGGER_DIVERGENCES`
  (`:147-154`) documenta explícitamente esa atribución como revisada a mano.
- **Asset**: `optimization_guide` IMPLEMENTED con `promised_by` de 5 pains
  (`asset_catalog.py:192`); retirar no lo huérfanizaría.
- **Resolución propuesta para el seguimiento**: cambio en Capa 2 que elimine
  `low_content_length` de `brecha_candidates` y permita retirarlo de Capa 1 como duplicado de
  `low_citability`; **o** darle una señal genuinamente distinta (word-count total con umbral
  propio) y un asset propio. → **Seguimiento S-B4**.

#### 3.8 `no_motor_reservas` → **DIFERIR** ⏸ (el de mayor valor comercial de los 9)

- **Señal de dato disponible**: el detector **existe** pero **no es alcanzable** desde
  `detect_pains`.
  - Existe: `web_scraper._detectar_motor_reservas(soup, html_text) -> bool`
    (`modules/scrapers/web_scraper.py:470`) y `_extraer_motor_reservas_url` (`:605`), que producen
    `motor_reservas_url`/`_nombre`/`_tipo` (`:141-145`) y los gaps `SIN_MOTOR_RESERVAS` (`:302`) y
    `MOTOR_RESERVAS_NO_PROMINENTE` (`:290`).
  - No es alcanzable: `v4_comprehensive.py` **no importa ni usa `web_scraper`** (grep: 0
    referencias). La señal fluye hacia `modules/delivery/` (etapa de implementación:
    `delivery_context.py:142`, `manager.py:1419`, `booking_bar_gen.py:39`), no hacia el audit.
    Y `booking_engine_detected` —el campo que Capa 1 declara (`:101`)— **nunca** se pobla:
    `main.py:2216-2327` construye el `ValidationSummary` con exactamente 5 campos
    (`whatsapp_number`, `rooms`, `adr_cop`, `occupancy_rate`, `direct_channel_percentage`).
- **Por qué no se implementa**: exigiría cablear un scraper nuevo a través del auditor y del CLI
  (cambiar la firma de `detect_pains` **y** sus dos call sites: `v4_diagnostic_generator.py:3186`
  y `v4_asset_orchestrator.py:280`). Eso excede «cambios confinados a `detect_pains`» y toca un
  archivo que FASE-G/H también tocarán.
- **Por qué no se retira**: huérfanizaría un asset implementado — `barra_reserva_movil`
  IMPLEMENTED con `promised_by=["no_motor_reservas"]` como **único** promotor
  (`asset_catalog.py:150-158`), lo que viola el criterio de B1 («retirar el pain no debe
  huérfanizar un asset implementado»).
- **Asset**: `barra_reserva_movil` IMPLEMENTED, hoy inalcanzable.
- **Resolución propuesta**: cablear la detección de motor de reservas de `web_scraper` a
  `V4AuditResult` (nuevo campo) y emitir desde ahí. Es el de mayor valor: `priority: 1`,
  `estimated_impact: "high"` (Capa 1 `:99-102`). → **Seguimiento S-B5**.

#### 3.9 `no_monthly_report` → **DIFERIR** ⏸ (decisión preferida: retirar, bloqueada)

- **Señal de dato disponible**: **ninguna, y no puede existir.** `monthly_report_requested`
  (Capa 1 `:267`) no aparece en ningún auditor ni validador. No es una propiedad del sitio del
  hotel: es un **entregable propio**.
- **Por qué no se implementa**: no hay nada que detectar. Un pain «Sin Informe Mensual» describe
  una carencia del proveedor, no del cliente.
- **Por qué no se retira** (aunque es lo correcto): el asset `monthly_report` tiene
  `promised_by=["always"]` (`asset_catalog.py:336`, con el comentario «SIEMPRE generar - la
  propuesta SIEMPRE lo promete» y la nota FASE-SOL2-B en `:337-343`) — es decir, **siempre se
  entrega**, así que la brecha nunca existe. Pero Capa 2 lo declara como disparador:
  `service_identity.py:127` `pain_id="no_monthly_report"` para el servicio `informe_mensual`
  (con `counts_in_alignment=False` y `brecha_candidates=()`). Retirarlo de Capa 1 rompería
  `test_pain_ids_canonicos_existen_en_pain_solution_map` y exigiría editar el registro canónico,
  expresamente prohibido en esta fase.
- **Asset**: `monthly_report` IMPLEMENTED y siempre generado; **no** se huérfaniza con un retiro.
- **Resolución propuesta**: cambio en Capa 2 para que `informe_mensual` no dependa de un pain
  ficticio (el docstring de `ServiceIdentity` define `pain_id` como «qué pain hace vendible el
  servicio»; para un complemento siempre-activo no hay ninguno, igual que
  `voice_assistant_guide` con `promised_by=[]`), y entonces retirar el pain de Capa 1.
  → **Seguimiento S-B6**.

### Grupo (b) — los 2 pains que N-A1 llamó «vivos»

#### 3.10 `no_ga4_enhanced` → **RETIRAR del mapa** ❌

- **Emisión real**: **ninguna.** Medido en §1: el guardia `hasattr(status, "is_enhanced")`
  (`:703`) es insatisfacible porque `is_enhanced` no existe en el repositorio. No es una caída
  silenciosa viva: es el **décimo pain muerto**.
- **Decisión**: retirar de Capa 1 (`:188-196`) y limpiar la referencia huérfana en
  `asset_catalog.py:298` (`analytics_setup_guide.promised_by`).
- **Por qué retirar y no implementar**: implementar exigiría añadir `is_enhanced` a
  `AnalyticsStatus` **y** una inspección real de eventos de conversión / enhanced ecommerce en
  GA4 que ningún cliente hace (`google_analytics_client.py` lee tráfico, es ADVISORY). Darle
  narrativa sin señal anunciaría una brecha que el pipeline no puede diagnosticar — viola la
  regla dura de B1.
- **Por qué el retiro es limpio** (§2): no lo referencia `ELEMENTO_KB_TO_PAIN_ID`, ni
  `PAIN_TO_ASSET`, ni Capa 2.
- **Asset**: `analytics_setup_guide` IMPLEMENTED con
  `promised_by=["no_analytics_configured", "no_ga4_enhanced"]` (`asset_catalog.py:298`).
  **No se huérfaniza**: `no_analytics_configured` sí emite (`:684`) y sí tiene narrativa
  (`:3329-3333`). Se elimina únicamente la referencia colgada.
- **Corrección al plan**: N-A1 lo presentó como «novena caída silenciosa viva» y hallazgo nuevo
  fuera del dossier. Es real que está fuera del dossier, pero **no está vivo**. Se registra como
  corrección de premisa → **Seguimiento S-B7**.

#### 3.11 `low_ota_divergence` → **IMPLEMENTAR narrativa** (mantener en el mapa; NO tocar el guard) ✅

- **Emisión real**: el punto existe (`:457`) y la señal **sí es alcanzable**:
  `ValidationSummary.get_field("direct_channel_percentage")`, poblado en `main.py:2306-2315`
  desde onboarding o default. Hoy no dispara por el guard `__iter__` de V7 sobre un float (§1) —
  **ese guard es de FASE-H y no se toca aquí**.
- **Decisión**: darle entrada de narrativa **ahora**, exactamente como ordena N-A1. Es el único
  de los 11 cuyo arreglo de emisión ya está planificado en otra fase: si FASE-H arregla el guard
  sin que B le haya dado narrativa, el pain pasa de «nunca dispara» a «dispara y se desvanece»
  en `:3346`, con el test de V7 en verde — peor para auditabilidad.
- **Narrativa que requiere**: sí. `nombre` = «Alta Dependencia OTAs», `detalle` = «Bajo porcentaje
  de reservas por canal directo» (Capa 1 `:148-149`). Severidad `high` (`:461`, ya fijada en la
  emisión existente).
- **Peso de impacto**: 0.20 (ver §4) — `estimated_impact: "high"`, `priority: 1` (Capa 1 `:99-102`).
- **Asset**: `direct_booking_campaign` es **`AssetStatus.MANUAL_ONLY`** (`asset_catalog.py:196-205`),
  no IMPLEMENTED. Consecuencia material: `map_to_solutions` (`:748-759`) **no lo genera** — lo
  deriva a `manual_only_assets` con un warning. Así que cuando FASE-H destrabe la emisión, la
  brecha «Alta Dependencia OTAs» aparecerá correctamente en el diagnóstico pero **sin asset
  generado**, como acción manual. Eso es coherente con `required_field="ota_data"` (el pipeline no
  tiene datos de OTA) y no bloquea la decisión: lo que B debe garantizar es que la brecha sea
  *visible*, no que tenga entregable automático. No se huérfaniza nada (no se retira el pain).
- **Nota**: al no tocar el guard, esta narrativa queda **latente** hasta FASE-H. El candado de B3
  la verifica estructuralmente (existe entrada) aunque hoy no haya emisión reachable — que es
  precisamente el orden forzoso B→H.

---

## 4. Decisión sobre los pesos de impacto (S14 / C-5)

**Hecho medido por FASE-A** (`faseA_yaml_narratives_audit.txt`, `faseA_yaml_region_blind.txt`):
`config/regional_benchmarks.yaml` tiene **4 copias literales idénticas** de las mismas 16 claves
(`eje_cafetero` `:29-45`, `caribe` `:101-117`, `bogota` `:141-…`, `antioquia`), **0 divergencias**
entre regiones, y los 16 fallbacks hardcodeados en Python coinciden 16/16 con ellas. Son **80
literales para 16 valores**.

**Decisión adoptada**:

1. **Los 5 pains narrados nuevos reciben peso explícito en las 4 regiones del YAML** + fallback
   Python explícito. Ninguno vive solo de un default en silencio (eso es la degradación
   V6/P11/S7 que el prompt señala).
2. **Los pesos se derivan del `estimated_impact` que Capa 1 ya declara**, no se inventan. La
   escala se lee de los 16 valores existentes: `high` → 0.20-0.30, `medium` → 0.10-0.15,
   `low` → 0.08-0.10. Se toma el extremo conservador de cada banda para no inflar brechas nuevas
   frente a las ya establecidas:

   | pain_id | `estimated_impact` en Capa 1 | Peso asignado | Referente en la banda |
   |---|---|---|---|
   | `low_ota_divergence` | `high` (`:147`) | **0.20** | `no_whatsapp_visible` 0.20, `low_seo_score` 0.20 |
   | `missing_alt_text` | `medium` (`:259`) | **0.10** | `metadata_defaults` 0.10, `missing_reviews` 0.10 |
   | `missing_llmstxt` | `low` (`:165`) | **0.08** | `no_og_tags` 0.08, `no_org_schema` 0.08 |
   | `no_social_links` | `low` (`:286`) | **0.08** | ídem |

3. **NO se colapsan las 4 copias en anclajes YAML en esta fase.** Decisión explícita, no omisión:
   hoy son idénticas, pero la estructura de 4 regiones es la costura de regionalización diseñada
   del archivo; colapsarla elimina esa capacidad sobre configuración dinero-adyacente
   (`impacto` alimenta `_normalize_weights:3389-3416` → los porcentajes que se imprimen en el
   diagnóstico). El beneficio real (que no puedan divergir en silencio) se captura con un lint de
   sincronía, no borrando la costura. → **Seguimiento S-B8**.

**Efecto conductual esperado y aceptado**: `_normalize_weights` reparte 100% entre las brechas
presentes, así que al entrar brechas nuevas los porcentajes de las existentes **bajan**. Es el
efecto buscado (las brechas reales dejan de estar mudas), pero cambia el documento comercial →
se valida contra el baseline.

---

## 5. Resumen de decisiones

| # | pain_id | Decisión | Señal | Narrativa | Peso |
|---|---|---|---|---|---|
| 1 | `missing_llmstxt` | **IMPLEMENTAR** | ✅ `ia_readiness.components["llms_txt"] == 0` (sonda HTTP) | requerida → derivada de Capa 1 | 0.08 |
| 2 | `missing_alt_text` | **IMPLEMENTAR** | ✅ `seo_elements.imagenes_alt is False` | requerida → derivada de Capa 1 | 0.10 |
| 3 | `no_social_links` | **IMPLEMENTAR** | ✅ `seo_elements.redes_activas is False` | requerida → derivada de Capa 1 | 0.08 |
| 4 | `no_ssl` | **DIFERIR** (S-B1) | ❌ proxy mide la URL de entrada, no el certificado | n/a | n/a |
| 5 | `no_schema_reviews` | **DIFERIR** (S-B2) | ❌ proxy mide rating de Google, no markup del sitio | n/a | n/a |
| 6 | `no_blog_content` | **DIFERIR** (S-B2) | ❌ `"no_evaluado"` hardcodeado | n/a | n/a |
| 7 | `low_content_length` | **DIFERIR** (S-B4) | ⚠️ duplicado de `low_citability` (misma expresión, mismo asset) | n/a | n/a |
| 8 | `no_motor_reservas` | **DIFERIR** (S-B5) | ⚠️ detector existe en `web_scraper` pero no alcanza el audit | n/a | n/a |
| 9 | `no_monthly_report` | **DIFERIR** (S-B6) | ❌ no es un gap del sitio; asset `promised_by=["always"]` | n/a | n/a |
| 10 | `no_ga4_enhanced` | **RETIRAR** | ❌ `is_enhanced` no existe en el repo ⟹ nunca disparó | n/a (sale del mapa) | n/a |
| 11 | `low_ota_divergence` | **IMPLEMENTAR narrativa** (guard → FASE-H) | ✅ `direct_channel_percentage` alcanzable; guard V7 lo bloquea | requerida → derivada de Capa 1 | 0.20 |

**Totales**: 4 con narrativa nueva (3 emisión+narrativa, 1 solo narrativa) · 1 retiro · 6 diferidos.

**Conteo del mapa post-B2**: 27 − 1 (`no_ga4_enhanced`) = **26**.

**Los 6 diferidos necesitan un registro explícito en el candado de B3** (`PAINS_DIFERIDOS` con
motivo + seguimiento), porque permanecen en Capa 1 **sin emisión** y §2 demuestra que no pueden
retirarse en esta fase sin editar archivos prohibidos. Sin ese registro el candado no puede
ponerse en verde; con él, el candado sigue fallando fuerte ante cualquier drift **no registrado**
— que es lo que AC4 pide («0 pains muertos **sin decisión**»).

> ⚠️ **Corrección post-B2 (ver §7.2)**: este párrafo se escribió cuando el candado fijaba una
> *partición narrativa* (`Capa 1 = narratives ⊎ PAINS_DIFERIDOS`), que suponía a los diferidos
> «sin narrativa». La implementación real derivó el complemento de Capa 1 y volvió la capa
> narrativa **total**: los 6 diferidos **sí** tienen narrativa. Lo que no tienen es **emisión**, y
> ahí es donde vive la partición (`Capa 1 = emitidos ⊎ PAINS_DIFERIDOS`). Tener narrativa sin
> emisión es inocuo —un pain que no se emite nunca llega a `_pain_to_brecha`— y es lo que permite
> que el día que un diferido gane señal, la brecha aparezca en el documento sin tocar una segunda
> tabla.

---

## 6. Seguimientos abiertos para `10-analisis-post-implementacion.md` §5

| ID | Contenido | Fase sugerida |
|---|---|---|
| **S-B1** | `no_ssl`: añadir sonda TLS real (o retirar el pain junto con `ELEMENTO_KB_TO_PAIN_ID["ssl"]` y `PAIN_TO_ASSET["no_ssl"]`) | post-tribunal |
| **S-B2** | Proxies equivocados en los checklists de scoring: `schema_reviews`/`schema_reviews_geo` (25 pts) puntúan sobre `gbp.rating` en vez de markup `aggregateRating` del sitio; `blog_activo` (10 pts) es `"no_evaluado"` y nunca se gana ⟹ score SEO topado a 90. Afecta el número mostrado al cliente y `low_seo_score` | **FASE-D/G** (tocan scoring y gates) |
| **S-B3** | `ELEMENTO_KB_TO_PAIN_ID["llms_txt_exists"]` se alimenta de `_extraer_elementos_iao:3032-3036` (búsqueda de subcadena en `schema.properties`), no de la sonda HTTP de `ia_readiness`. Dos señales rivales para el mismo hecho; la del KB es la falsa | post-tribunal |
| **S-B4** | `low_content_length`: retirar de Capa 2 (`seo_local.brecha_candidates`) y de Capa 1 como duplicado de `low_citability`, o darle señal y asset propios | requiere cambio en Capa 2 |
| **S-B5** | `no_motor_reservas`: cablear `web_scraper._detectar_motor_reservas` a `V4AuditResult` y emitir. Mayor valor comercial de los 9 (priority 1, impact high) | fase propia |
| **S-B6** | `no_monthly_report`: cambiar Capa 2 para que `informe_mensual` no dependa de un pain ficticio y retirar el pain de Capa 1 | requiere cambio en Capa 2 |
| **S-B7** | **Corrección de premisa N-A1**: `no_ga4_enhanced` no era una caída silenciosa viva; `is_enhanced` no existe en el repo y el pain nunca disparó. El script `faseA_narratives_audit.py` cuenta puntos de emisión por regex, no emisiones alcanzables — sus «18 emitidos» son *puntos en el fuente*. Re-medir con criterio de alcanzabilidad | inmediato (documental) |
| **S-B8** | `regional_benchmarks.yaml`: lint de sincronía del key-set de `pain_narratives` entre las 4 regiones (capturar el beneficio sin colapsar la costura de regionalización) | post-tribunal |
| **S-B9** | `v4_diagnostic_generator._extraer_elementos_de_audit:3066` es **código muerto**: 0 call sites repo-wide (solo lo mencionan dos docstrings deprecated en `:340`/`:345`). Es además la única función que combina los 4 pilares y la que rellena los elementos faltantes con `False` | limpieza |
| **S-B10** | `test_proposal_dynamic.py::test_technical_assets_table_shows_both_assets` **falla y es preexistente**: espera 2 assets técnicos pero `TECHNICAL_ASSET_CATALOG` (`service_catalog.py:102-108`) tiene 1 sola entrada desde `9623a44` (ROICRIII FASE-4, limpieza de assets deprecados). El loop de `_generate_technical_assets_table:1625` es incondicional, así que el test está desactualizado, no el código. Decidir: re-incorporar `indirect_traffic_optimization` (existe en `ASSET_CATALOG:301`, IMPLEMENTED, prometido por `low_organic_visibility`) o actualizar el test | **FASE-C** (propuesta dinámica) |
| **S-B11** | `test_proposal_dynamic.py::test_no_assets_no_presence_all_excluded` **falla y es preexistente**: el footnote omite `Botón de WhatsApp` aunque el test recorre `PROPOSAL_SERVICE_TO_ASSET` esperando los 8 servicios. Vive en `proposal_asset_alignment.py`, archivo que FASE-B tiene **prohibido** tocar | **FASE-C** (dueña del archivo) |
| **S-B12** | Los 5 tests de `test_proposal_confidence_disclosure.py::TestAssetQualityTable` **fallan y son preexistentes**: exigen las columnas `\| Nivel \|` y `\| Que significa \|`, pero `_generate_asset_quality_table:1727` produce `\| Entregable \| Momento de entrega \| Qué incluye \|` desde el commit `44b702e`. El test quedó desactualizado frente al refactor de la tabla | **FASE-C** (propuesta dinámica) |
| **S-B13** | **Caída silenciosa #3 del dossier NO es cerrable por B**: `llm_report` mention_rate 0.0 / `aeo_snippets` 0/5 no tienen pain_id en Capa 1 (verificado: los 26 pain_ids post-B no incluyen ninguno de esas dos señales). La biyección de AC4 opera sobre el universo *existente*; crear pain_id nuevos es extender Capa 1. Requiere decisión previa: ¿pain nuevo (`low_llm_mention_rate`, `no_aeo_snippets`) o umbral dentro de `low_ia_readiness`/`low_citability`? | **VERIFY** (asignar dueño) o fase propia |
| **S-B14** | **Caída silenciosa #5 del dossier NO es cerrable por B**: los 4 pains de schema de Capa 1 (`no_hotel_schema`, `no_faq_schema`, `no_org_schema`, `no_schema_reviews`) son de **ausencia**. Un schema *presente con warnings* no tiene pain_id que narrar, así que la biyección no lo alcanza. Requiere decidir si los warnings merecen pain propio o una severidad advisory | **VERIFY** (asignar dueño) o fase propia |
| **S-B15** | **Conflicto de concurrencia entre sesiones**: mientras FASE-B terminaba su post-ejecución, una **sesión paralela de FASE-D** sobrescribió la línea de estado del `README.md` del plan con «FASE-B ✅ era falso, B sigue pendiente» — conclusión correcta *para el repo que esa sesión veía* (el trabajo de B aún no estaba commiteado) y falsa para el real. El archivo quedó auto-contradictorio (encabezado vs tabla de Progreso). También hay trabajo de D sin commitear en el árbol (`AGENTS.md`, `main.py`, `publication_gates.py`, `human_checklist_generator.py`, `evidence/FASE-D/`, 24 tests). **Mitigación**: (1) commitear al cierre de cada fase — R1 del executor ya lo pide; (2) no correr dos fases del mismo plan en paralelo sobre el mismo directorio; (3) si se corre en paralelo, usar worktrees. Corregido el encabezado; el commit de B excluye los archivos de D | proceso / VERIFY |

**Prueba de causalidad de S-B10/S-B11/S-B12** (para que nadie las re-investigue como
regresión de FASE-B): `git diff --stat` sobre `proposal_asset_alignment.py`,
`v4_proposal_generator.py`, `service_catalog.py`, `test_proposal_dynamic.py` y
`test_proposal_confidence_disclosure.py` devuelve **vacío** — FASE-B no modificó ninguno.
Y los tests que fallan invocan `_generate_dynamic_services_table(assets_generated=[])` /
`_generate_asset_quality_table(None)` directamente: sin audit, sin `detect_pains`, sin
`_pain_to_brecha`, sin `regional_benchmarks`. Ninguno de los 5 archivos que FASE-B sí tocó
está en esas rutas. Los 7 fallos son del área de propuesta dinámica, territorio de FASE-C.

### 6.1 Desviación respecto a la tabla de Tests del prompt

El prompt de FASE-B (`05-prompt-inicio-sesion-fase-B.md`) pedía un test que verificara que
**`no_ga4_enhanced` llega a `brechas`**. Esa fila quedó **obsoleta por decisión de B1**: el
análisis demostró que el pain nunca disparó (`is_enhanced` no existe en ningún `AnalyticsStatus`
del repo, §3.10), así que se **retiró de Capa 1** en vez de darle narrativa.

El test pedido se sustituyó por `TestNoGa4EnhancedRetirado` (3 casos), que fija la dirección
contraria y es más fuerte: entrega al mapper exactamente el objeto que la rama muerta necesitaba
para disparar (`StatusConCampo` con `is_enhanced = False`) y afirma que **no** aparece. Si alguien
reintroduce la rama, el test falla.

---

## 7. Verificación medida (post-B2)

Todo número de esta sección sale de un comando re-ejecutable, no de memoria. Logs en este
mismo directorio.

| Qué | Comando | Resultado | Log |
|---|---|---|---|
| Candado de biyección (B3) | `pytest tests/commercial_documents/test_pain_map_bijection.py -v` | **28 passed** | `faseB_bijection.txt` |
| Ramas de emisión nuevas (B2) | `pytest tests/commercial_documents/test_detect_pains_emisiones_faseB.py -v` | **18 passed** | `faseB_emisiones.txt` |
| Mapper + contratos FASE-A | `pytest tests/commercial_documents/test_pain_solution_mapper.py tests/common/test_service_identity_registry.py -q` | **42 passed** | `faseB_mapper.txt` |
| Baseline del prompt | `pytest tests/quality_gates tests/asset_generation -q` | **848 passed, 2 skipped** — idéntico al baseline | `faseB_baseline.txt` |
| Barrido ancho | `pytest tests/financial_engine tests/config tests/common tests/data_validation tests/orchestration_v4 tests/auditors tests/regression -q` | **1121 passed, 2 skipped, 1 xpassed** | `faseB_broad.txt` |
| `tests/commercial_documents` completo | archivo por archivo (el prompt prohíbe correrlo de una vez, ~8GB) | 7 fallos, **todos preexistentes** (S-B10/11/12) | `faseB_commercial_documents_barrido.txt` |
| Validaciones del repo | `python scripts/run_all_validations.py --quick` | **7/7** | `faseB_validations.txt` |
| Delta de la biyección | `python evidence/FASE-B/faseB_narratives_audit.py` | **DESCARTE REAL 2 → 0** | `faseB_bijeccion_audit.txt` |

### 7.1 El delta que cierra AC4

| Métrica | FASE-A | FASE-B | Lectura |
|---|---|---|---|
| Capa 1 (`PAIN_SOLUTION_MAP`) | 27 | **26** | −1: `no_ga4_enhanced` retirado (guardia insatisfacible, §3.10) |
| Emisiones (AST, funciones emisoras) | 18 | **20** | +3 implementados, −1 retirado |
| `narratives` **literal** | 16 | **16** | **Sin cambio**: no se escribió ni una entrada a mano (L-NC4) |
| `narratives` **efectivo** (sonda conductual) | no medible | **26 / 26** | Cobertura total sobre Capa 1 |
| **DESCARTE REAL** (emitido Y rebotado) | **2** | **0** | El defecto de N-A1 está cerrado |

Que la columna *literal* no crezca mientras la *efectiva* llega a 26 es la prueba de que no
se creó una tabla paralela pain_id→texto: el complemento se deriva de Capa 1.

### 7.2 Dos cosas que la verificación corrigió sobre la marcha

1. **El candado nació con la forma equivocada y B2 lo demostró.** La primera versión fijaba
   `Capa 1 = narratives ⊎ PAINS_DIFERIDOS` (partición narrativa). Falló en rojo contra la
   implementación real, y tenía razón el código: la derivación de B2 cubre los 26, incluidos
   los 6 diferidos. La partición correcta es del lado de la **emisión**
   (`Capa 1 = emitidos ⊎ PAINS_DIFERIDOS`), y la cobertura narrativa es **total sin
   excepciones** — postura estrictamente más fuerte, porque vuelve inalcanzable el
   `return None` para cualquier pain de Capa 1.

2. **Re-ejecutar el script de FASE-A ahora informa un número peor (4 en vez de 2) y es un
   artefacto.** Mide `narratives` leyendo el dict literal por AST; como B2 derivó el
   complemento en vez de inflarlo, el literal sigue en 16. El archivo
   `narratives_post_B2.txt` conserva esa salida —el prompt pedía ese comando— con una nota
   que explica por qué no debe leerse como retroceso. La medición válida es la conductual.

### 7.3 Los guards de las emisiones nuevas son load-bearing (verificado sin mutar código)

Los 18 tests incluyen 9 negativos. Para probar que no son decorativos se evaluó la expresión
del guard contra el objeto real, sin tocar producción:

```
SEOElementsResult(confidence="low", imagenes_alt=False, redes_activas=False, images_without_alt=0)
  bool(seo_elements)          = True     <- sin la cláusula confidence, EMITIRÍA
  imagenes_alt is False       = True     <- dispararía missing_alt_text
  redes_activas is False      = True     <- dispararía no_social_links

IAReadinessReport(components={"schema_quality": 80})   # sin clave llms_txt
  components.get("llms_txt")  = None     <- None, no 0: NO dispara
```

Ese `confidence="low"` con todos los flags en False es exactamente lo que devuelve
`seo_elements_detector.py:70-74` cuando BeautifulSoup lanza excepción. Sin el guard, un sitio
cuyo HTML no se pudo parsear recibiría dos brechas falsas — y con ellas un cobro indebido.
