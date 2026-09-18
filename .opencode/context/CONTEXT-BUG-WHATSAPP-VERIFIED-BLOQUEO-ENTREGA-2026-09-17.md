# CONTEXT-BUG-WHATSAPP-VERIFIED-BLOQUEO-ENTREGA-2026-09-17

> **Tipo**: Contexto de decisión con evidencia medida (insumo para sesión de orquestación → plan).
> **Disparador**: la corrida de observación FASE-P4 (`v4complete` sobre hoteldonalfonso.com, 2026-09-14) produjo `NOT_READY_FOR_PUBLICATION` y el tribunal **suprimió el ZIP**. La prueba del enforcement es válida, pero no dejó entregables. Al ahondar en las causas aparece un bug determinista: **con la ruta de datos del warehouse, cualquier hotel real queda bloqueado de fábrica.**
> **Tesis (una línea)**: `_check_whatsapp_verified` no distingue *"el hotel no tiene WhatsApp"* de *"esta ruta de datos nunca lo pregunta"* — y trata el segundo caso como error bloqueante.
> **Estado**: **SIN IMPLEMENTAR.** Esta sesión NO toca código. Los §5-§9 son insumo; la decisión de qué fix queda para la sesión de plan.
> **Re-verificación (primera pasada)**: todos los anchors `archivo:línea` fueron releídos contra HEAD `e8010ce` (v4.77.0), no copiados de la auditoría. Correcciones respecto al informe original en §2d.
> **Re-verificación (segunda pasada, 2026-09-17, contra HEAD `38796da`)**: el código no cambió desde `e8010ce` (`git diff --stat e8010ce..HEAD` = solo docs), pero la lectura completa de la cadena de decisión **refutó la mekanika** de este documento en tres puntos y su claim de novedad en uno. Marcados con ⚠️ y desarrollados en §2e:
> - **F-A (la recomendación original) es un no-op**: la rama de rescate `:437-444` es inalcanzable en *toda* ruta de producción, con o sin kwarg cableado.
> - **El defecto de cableado real está en `v4_asset_orchestrator.py:286`** (`detect_pains`), que este documento no mencionaba.
> - **El bug NO es un hallazgo nuevo**: está triajado desde 2026-09-14 como **F-P4.3** con dueño, y diagnosticado desde 2026-07-25 como **HALLAZGO-N4/BUG-6** (Zione.co). Ver §7 y §10.
> - Las rutas de evidencia de §3 estaban mal (`corrida/output/…` no existe; es `corrida/run/…`).

---

## 1. Resumen ejecutivo — cinco defectos apilados, no uno

> ⚠️ **Corregido en la segunda pasada.** Este §1 anunciaba tres defectos. Medidos contra el código vivo, D1/D3 se mantienen, **D2 queda reubicado** (el cable que decide no es el que se reportó) y aparecen **D4 y D5**, que son los que explican por qué el bloqueo es determinista.

| # | Defecto | Ubicación | Efecto |
|---|---------|-----------|--------|
| **D1 — Adaptador** | La ruta `observations.json → onboarding` no puede transportar WhatsApp en **ninguna** de sus tres capas: el instrumento de recolección no lo pregunta, el esquema lo prohíbe, y el adaptador lo mapea con 4 claves | `data/hotel_observations/forms/contact_form_ES.md:233-238` (privacidad: "NO pedir ni almacenar… teléfono directo"), `hotel_observations.schema.json` `$defs/observation` (21 propiedades, **sin** propiedad de contacto, `additionalProperties: False`), `main.py:3877-3882` (`_FIELD_MAP` = 4 claves) | `whatsapp_number` nunca se anexa a `ValidationSummary` → el check cae en la rama de error |
| **D2 — Cableado (REUBICADO)** | El orquestador reconstruye su propio conjunto de pains **sin** la señal de detección HTML: `detect_pains()` se llama sin el kwarg, cuyo default es `False` | **`modules/asset_generation/v4_asset_orchestrator.py:286`** → `pain_solution_mapper.py:338` (default `False`) → `:355` crea el pain `no_whatsapp_visible` → `:61-62` lo mapea a `whatsapp_button` → `coherence_validator.py:420-421` dispara. Las dos llamadas a `validate()` (`:309-312`, `:447-451`) **también** omiten el kwarg, pero eso ya no decide nada (ver D2-bis) | El orquestador y `main.py:2446` (que sí pasa la señal) **ven conjuntos de pains distintos para el mismo hotel**, y el `pain_ledger.json` guardado en `:301` nace con el pain fantasma |
| **D2-bis — Rescate muerto** | La rama de rescate por HTML (`coherence_validator.py:437-444`) exige `whatsapp_field is None` **y** `whatsapp_html_detected=True`; el único `ValidationSummary` de producción (`main.py:2338`, construido en `2232-2275`) anexa el campo en cuanto el HTML detecta el botón (`:2266`) | `coherence_validator.py:437-444` es **inalcanzable en toda ruta**, con o sin kwarg | Cablear el kwarg a `validate()` (la old F-A) **no cambia el resultado**: el campo llega presente con ESTIMATED 0.7 y cae en `:469` → `severity="error"` → bloqueo igual |
| **D3 — Recuperación imposible** | `AssessmentBuilder.with_validation()` recibe `whatsapp_validation` y lo **descarta** | `modules/assessment_builder.py:116-122` (el parámetro no se usa; llamado desde `main.py:2938`) | Aguas abajo del builder no hay forma de reconstruir la confianza de WhatsApp |
| **D4 — Conflicto de políticas** | El catálogo **ordena** prometer y generar el botón aunque falte el número, y la regla de coherencia **prohíbe** publicarlo sin número verificado | `asset_catalog.py:63-67` (`required_confidence=0.7`, `block_on_failure=False  # NEVER_BLOCK`, `promised_by=["no_whatsapp_visible","whatsapp_conflict"]`) vs `coherence_config.py:60-65` (`blocking=True`, umbral 0.9) | El bloqueo no es un caso límite: es la colisión de dos contratos incompatibles ejecutados en serie. `whatsapp_verified` **cumple** su parte |
| **D5 — Dos reglas de decisión** | El pre-gate decide por **score**; el gate canónico decide por **veredicto** | `main.py:2566` (`if pre_coherence_score < threshold`) ignora `is_coherent`; la única definición canónica es `coherence_gate.py:536-558` (`coherence_verdict_passes`) | La corrida gasta los 13 assets y solo muere en FASE 4.5. Fail-fast imposible; el bloqueo llega después de pagar el coste |

**Consecuencia combinada**: el veredicto de coherencia de WhatsApp queda reducido a **una pregunta de red** — ¿el sitio era alcanzable y `SitePresenceChecker` vio el botón (`:458-459`, boost a 0.95)? Las otras dos salidas son "el botón no está en el plan" (`:424-431`) y **código muerto**. No es una garantía de calidad del dato. Y **no es exclusivo del warehouse**: en la ruta de auditoría en vivo, un hotel cuyo número solo aparece en su propio sitio queda en ESTIMATED 0.7 (`main.py:2257`), y 0.7 < 0.9 con `blocking=True` → mismo `severity="error"` → ZIP suprimido. El falso positivo estructural es **más ancho** de lo que este documento reportaba.

**Lo que NO es este bug** (importante para no sobredimensionar el fix): el tribunal hizo lo correcto **con el veredicto**. El pipeline le entregó un `is_coherent=False` con un check `severity="error"` abierto, y bloqueó. El defecto está **aguas arriba del tribunal**, en la producción del veredicto. Arreglar `whatsapp_verified` no cambia ninguna garantía del enforcement.

> **Matiz medido (segunda pasada)**: "hizo lo correcto" aplica al **fallo**, no al **recuento**. El gate de coherencia borró `01_`/`02_` **antes** de la revisión, así que 2 de los 4 correctivos del acta (`MISSING_ARTIFACT`, `BLOQUEAR`) son derivados de una causa ya resuelta — eso es **F-P4.2**, registrado en el informe P4, no un hallazgo de esta sesión. Ver §3 (última fila) y §7.

---

## 2. La cadena trazada, capa por capa

### 2a. Quién produce el dato

`ValidatedField(field_name="whatsapp_number", …)` se anexa en **un solo lugar** del repo: `main.py:2232-2275`, una cadena de 4 ramas, todas dependientes de la auditoría en vivo:

| Rama | Condición | Confidence |
|------|-----------|------------|
| `main.py:2240` | `whatsapp_validation.confidence == VERIFIED` (Web + GBP coinciden) | VERIFIED |
| `main.py:2249` | `== CONFLICT` | CONFLICT |
| `main.py:2257` | `elif whatsapp_web` (una sola fuente) | ESTIMATED 0.5 |
| `main.py:2266` | `elif whatsapp_html_detected` | ESTIMATED 0.6 (`value="detected_via_html"`) |

Ninguna rama se dispara desde la ruta del warehouse: `whatsapp_validation`, `whatsapp_web` y `whatsapp_html_detected` vienen del auditor (`modules/auditors/v4_comprehensive.py:161, 695, 1852`), no de `onboarding_data`. Y `modules/onboarding/` tiene **0 coincidencias** en `whatsapp|tel[eé]fono` (verificado por grep, 2026-09-17). El formulario de onboarding tampoco captura canales de contacto.

**Tres hechos añadidos en la segunda pasada (2026-09-17), todos medidos:**

1. **Solo hay un `ValidationSummary` en producción**: `main.py:2338`, alimentado por el bloque `2232-2275`. Todo el pipeline (pre-gate, orquestador, gates) consume ese mismo objeto. No hay una segunda fuente que pudiera dejar el campo ausente.
2. **La rama `:2266` anexa el campo cuando el HTML detecta el botón** — es decir, `whatsapp_html_detected=True` y `whatsapp_field is None` **no pueden coexistir**. Toda la arquitectura de "rescate" (§2b rama 2) descansa sobre una combinación de entradas que el propio productor del dato se encarga de hacer imposible.
3. **El valor anexado es un centinela, no un número**: `value="detected_via_html"` con `can_use_in_assets=True` (`main.py:2270-2274`). Sus únicos consumidores en el repo son ese constructor y `modules/asset_generation/conditional_generator.py:427-429`, que lo reusa como teléfono: `_generate_whatsapp_button` (`:711`) hace `''.join(c for c in str(phone_number) if c.isdigit())` → **cadena vacía → `https://wa.me/` sin destino**. No hay ninguna guarda contra el centinela en el repo (grep `detected_via_html`: 1 coincidencia en código no-test). Cualquier fix que habilite esa ruta sin cerrar este punto entrega al cliente un botón roto.

### 2b. Quién decide

`coherence_validator.py:392-484` (el rango correcto; `:461` era corte prematuro), tabla de ramas medida línea por línea:

| Condición | Línea | score | severity | passed |
|-----------|-------|-------|----------|--------|
| No hay asset `whatsapp_button` **en el plan** | `:424-431` | 1.0 | info | True |
| Sin campo **y** `whatsapp_html_detected` | `:437-444` | 0.5 | `is_blocking` → **info** / no-blocking → warning | `not is_blocking` |
| **Sin campo, sin HTML** | `:446-453` | **0.0** | **error** | `not is_blocking` → **False** |
| Campo confidence ≥ 0.9 | `:461-468` | 1.0 | info | True |
| Campo confidence ∈ [0.7, 0.9) → **ESTIMATED = 0.7 exacto** | `:469-476` | 0.7 | **error** | **False** |
| Campo confidence < 0.7 → CONFLICT=0.3 / UNKNOWN=0.0 | `:477-484` | 0.3 / 0.0 | **error** | **False** |

La conversión de nivel a número está en `:764-772`: `VERIFIED 0.95 · ESTIMATED 0.7 · CONFLICT 0.3 · UNKNOWN 0.0`. Con umbral 0.9 (`coherence_config.py:60-65`), el umbral **cae en el hueco de la escala discreta**: ninguna rama por debajo de VERIFIED puede pasar. Como VERIFIED exige Web+GBP (`main.py:1788`), y el botón solo entra al plan si el campo está ausente/UNKNOWN/CONFLICT (`pain_solution_mapper.py:355,366` + `asset_catalog.py:67`), **la rama verde `:461-468` es código muerto** salvo por el boost.

De los dos escapes que el documento original contaba, **uno no existe**:

1. ~~`whatsapp_html_detected` → anulado por D2.~~ **Anulado por construcción, no por D2**: la rama `:437-444` es inalcanzable en toda ruta de producción (§2a punto 2). Y ningún test vivo la ejercita — `grep whatsapp_html_detected=True tests/` no produce ni un paso por `CoherenceValidator.validate()`; el mensaje `"WhatsApp detectado en HTML"` no aparece en `tests/`.
2. `site_presence_report["whatsapp_button"].presence_status == "exists"` → boost a 0.95 en `:458-459`. **Es el único escape vivo.** Sí se cableó (`v4_asset_orchestrator.py:311, 450`), pero exige que el **sitio sea alcanzable**. En la corrida P4 devolvió `status: "verification_failed"`, `confidence: 0.3`, `site_verified: false` (`evidence/FASE-P4/corrida/run/v4_complete/hoteldonalfonso/v4_audit/site_presence_snapshot.json`).

**Aritmética real de la corrida P4** (pesos en `:101-108`, denominador = **7.5**, no 6): `(1.5·1.0 + 1.0·1.0 + 1.5·0.95 + 0.5·0.0 + 1.0·0.8 + 2.0·1.0) / 7.5 = 0.8966666`. El peso del check culpable es 0.5 de 7.5 (6.7 %).

### 2c. Cómo se vuelve bloqueo

```python
# coherence_validator.py:176-185  (PARÁFRASIS; el código real es un `for` en :173-180)
errors = [c for c in self.checks if c.severity == "error" and not c.passed]
...
is_coherent = len(errors) == 0 and overall_score >= threshold
```

**Un solo** check `severity="error"` sin pasar fuerza `is_coherent=False` **independientemente del score**. Peso del check en el score: 0.5 de 7.5 (ver §2b) — de ahí la "paradoja" reportada: score 0.8966 con veredicto negativo. **Aclaración: no es una paradoja**, es el diseño declarado de `:176-185`. Lo contraintuitivo de verdad es D5: el mismo concepto tiene **dos reglas de decisión** según quién mire.

Y el gate que lo consume:

```python
# publication_gates.py:604-608
passed = coherence_verdict_passes(coherence_score, self.config.coherence_threshold,
                                  assessment.get("is_coherent"))
# publication_gates.py:624-649  → BLOCKED con mensaje "meets threshold ... but validator declared is_coherent=False"
```

`coherence_verdict_passes` vive en `modules/quality_gates/coherence_gate.py:536-558` y es la **única** definición del veredicto de publicación. **D5 (nuevo)**: el pre-gate de `main.py:2566` no la usa — decide con `pre_coherence_score < threshold` y descarta `pre_coherence_report.is_coherent`. Por eso la corrida P4 pasó el portillo de FASE 3.5 con el check ya en `error`, generó 13 assets, y murió en FASE 4.5. La regla que la FASE-F impuso en el gate canónico nunca se propagó al pre-gate.

`publication_gates.py` tiene **0 referencias a `whatsapp_verified`** (verificado por `grep -c`, 2026-09-17). La puerta FASE-F solo lee el veredicto binario. **Precisión**: el mensaje del gate **sí** divulga la clase (`"error-severity checks unresolved (see coherence_validation.json)"`, `:632-636` + `suggestion`), pero **no el nombre del check** — que es lo que obliga a abrir el JSON para saber el culpable. AC-4 (§6) sigue en pie, pero es un fix de legibilidad, no de datos perdidos. Eso explica por qué el bloqueo tardó en diagnosticarse.

### 2d. Correcciones al informe original

| Claim previo | Verificado 2026-09-17 |
|--------------|----------------------|
| "el orquestador pierde el rescate; `main.py` lo preserva" | **Corregido en la segunda pasada.** La observación de fondo es cierta (`v4_asset_orchestrator.py:500` hace `final_coherence_report = post_coherence_report if post_coherence_report else coherence`, y **ambas** ramas vienen de llamadas sin el kwarg), pero la consecuencia era falsa: `main.py` tampoco preserva el rescate, porque la rama `:437-444` es inalcanzable **en las dos rutas** (§2e N2). No hay ninguna "ruta de fallback que conserve el rescate" que perder. |
| "el warehouse tiene 21 propiedades" | Confirmado, pero están en `$defs/observation` (el nivel raíz tiene 6). `whatsapp` no aparece en **ninguna** capa del archivo; `observations.json` tampoco lo contiene (6 observaciones, 0 coincidencias). |
| "`contacto` aparece en el esquema" | Falso positivo de grep: es el valor de enum `source: "contacto_directo"` (`:122`), no un campo de contacto. La afirmación "el esquema no tiene propiedad de contacto" se mantiene. |

### 2e. Correcciones y hallazgos de la segunda pasada (HEAD `38796da`, 2026-09-17)

**Correcciones factuales a este propio documento:**

| # | Claim de este documento | Medido |
|---|--------------------------|--------|
| C1 | Rutas `evidence/FASE-P4/corrida/output/v4_complete/...` (4 filas de §3) | **No existen.** La ruta real es `evidence/FASE-P4/corrida/**run**/v4_complete/hoteldonalfonso/v4_audit/`. Los comandos de §9 llevaban a un directorio fantasma |
| C2 | "`corrida.log:4` = Empty HTML response" | `Empty HTML response` está en **`corrida.log:1`**; la **línea 4** es el 403 de Gemini con la key. Dos filas usaban el mismo anchor para hechos distintos |
| C3 | "Score pre-gen 0.8966 vs 0.9 canónico (**dos cifras del mismo concepto**)" | **No son dos cálculos.** `CoherenceReport.to_dict` hace `round(overall_score, 2)` (`coherence_validator.py:49`); el gate report guarda el float crudo. 0.8966666 → 0.9 por serialización. No hay divergencia entre gates en el score |
| C4 | "el check está en `coherence_config.py:60-65`" | Correcto pero ambiguo: el archivo es **`modules/commercial_documents/coherence_config.py`**, no `quality_gates/` |
| C5 | "los dos `_check_whatsapp_verified`": dominio en `domain_gates.py:348-384` | El método cierra en **`:389`**; su severidad de fallo es **`warning`, nunca `error`** (`:358`, `:387`) — es decir, el duplicado muerto es *más permisivo* que el vivo. Confirmado **0 importadores en producción** (`grep DomainGate`) y **0 tests** cubriendo la rama HTML del vivo |
| C6 | "L-VERIFY.3 registró: cada fase certificó su alcance y nadie midió el extremo a extremo" | La lección **L-VERIFY.3** en `.opencode/LECCIONES-INDEX.md:184` trata de otra cosa (caché sin redacción en `google_places_client.py:_save_cache`). La idea que el §7 invoca está registrada en otra parte; la cita está vencida |
| C7 | "este bug **no está triajeado** … es un hallazgo **nuevo** de esta sesión" | **FALSO.** Ver §7 corregido: es **F-P4.3** (2026-09-14, con dueño) y **HALLAZGO-N4/BUG-6** de DT-3/DT-4 (2026-07-25, Zione.co) |

**Hallazgos nuevos (N1-N7), todos medidos contra código vivo:**

| # | Hallazgo | Anchor |
|---|----------|--------|
| **N1** | El cableado que decide está en `detect_pains`, no en `validate()`: el orquestador llama `pain_mapper.detect_pains(audit_result, validation_summary, analytics_data)` **sin** `whatsapp_html_detected`, y de ahí nacen a la vez el pain fantasma, el `whatsapp_button` del plan y el `pain_ledger.json` contaminado | `v4_asset_orchestrator.py:286` → `pain_solution_mapper.py:338,355,61-62` → `coherence_validator.py:420-421`; ledger en `:301` |
| **N2** | La rama de rescate `:437-444` es **inalcanzable en toda ruta de producción** (no solo en la canónica): el único `ValidationSummary` de producción anexa el campo en cuanto el HTML detecta el botón. **Consecuencia: F-A, la recomendación de este documento, es un no-op** | `main.py:2266-2275`, `main.py:2338`; `coherence_validator.py:437` |
| **N3** | `_check_whatsapp_verified` es **insatisfacible por construcción**: su disparador (`whatsapp_button` en el plan ⟸ pain de ausencia o conflicto) y su condición de paso (confidence ≥ 0.9 ⟸ VERIFIED) son mutuamente excluyentes. La única salida real es el boost de SitePresence, que depende de que el sitio responda | `asset_catalog.py:67`, `pain_solution_mapper.py:355,366`, `coherence_validator.py:764-772`, `coherence_config.py:60-65` |
| **N4** | **Conflicto de políticas** (la causa raíz): el catálogo ordena prometer y generar el botón sin número (`block_on_failure=False  # NEVER_BLOCK`, `promised_by=["no_whatsapp_visible", …]`, `required_confidence=0.7`) y la regla de coherencia prohíbe publicarlo sin número verificado (0.9). Dos contratos incompatibles en serie; el check no está roto, cumple su parte | `asset_catalog.py:58-68` vs `coherence_config.py:60-65` |
| **N5** | El umbral 0.9 **cae en el hueco de la taxonomía discreta** (0.0/0.3/0.7/0.95). Cualquier regla `≥0.9` sobre ese enum significa "exige VERIFIED", y VERIFIED exige GBP → Places API. Cuatro barras para el mismo hecho: 0.9 (coherencia + `domain_gates.py:313`), 0.7 (catálogo), 0.3 (`preflight_checks.py:48`, new hotel), 0.5/0.6 (`match_percentage` en `main.py:2263,2273`) | `coherence_validator.py:764-772` |
| **N6** | **D5**: el pre-gate de `main.py` decide por score e ignora el veredicto canónico → corrida completa gastada antes del bloqueo | `main.py:2554-2578` vs `coherence_gate.py:536-558` |
| **N7** | El centinela `"detected_via_html"` viaja con `can_use_in_assets=True` y el generador lo trata como teléfono: `wa.me/` vacío, sin guarda en el repo | `main.py:2270`, `conditional_generator.py:427-429,711` |

---

## 3. Evidencia de la corrida P4 (Don Alfonso, 2026-09-14)

Rutas verificadas en disco el 2026-09-17 (el prefijo correcto de la corrida es `evidence/FASE-P4/corrida/**run**/…`; el `output/…` que figuraba aquí era inexistente):

| Hecho | Artefacto |
|-------|-----------|
| Sitio inalcanzable: `Empty HTML response for https://hoteldonalfonso.com/` | `evidence/FASE-P4/corrida/corrida.log:1` |
| `WhatsApp: Datos insuficientes para validación` → `whatsapp_validation = None` | `corrida.log:157`; mecanismo en `main.py:1786-1808` (requiere web **y** GBP para validar) |
| Origen warehouse de los financieros (`adr_cop: user_provided`, `occupancy_rate: onboarding`, `direct_channel_percentage: onboarding`) | `…/run/v4_complete/hoteldonalfonso/v4_audit/gate_report_20260914_183821.json` |
| Check culpable, literal y único error: `{"name":"whatsapp_verified","passed":false,"score":0.0,"message":"WhatsApp button requiere validación pero no hay campo 'whatsapp_number'","severity":"error"}` | `…/v4_audit/coherence_validation.json` (`is_coherent: false`, `overall_score: 0.9` redondeado, 5/6 checks pasan). **El `coherence_validation_post_gen.json` reporta exactamente la misma rama** (`0.0 / error / False`), lo que confirma por lectura de código que el post-gen recibe `asset_specs`, no los assets realmente generados |
| `whatsapp_status: "UNKNOWN"`, `whatsapp_confidence: 0.0` | `…/v4_complete_report.json` |
| `site_presence_snapshot`: los 5 assets en `status: "verification_failed"`, `confidence: 0.3`, `site_verified: false` | `…/v4_audit/site_presence_snapshot.json` → el único escape vivo (§2b) estaba cerrado por la caída del sitio, no por el bug |
| Score único `0.8966666`; el JSON muestra `0.9` | `gate_report_20260914_183821.json` vs `coherence_validation.json` — **diferencia de redondeo de `to_dict`, no dos cálculos** (corrección C3 en §2e) |
| Bloqueo final: NOT_READY → **se borran los documentos cliente** → tribunal revisa sin ellos → `⛔ ZIP SUPPRIMIDO` | `corrida.log:279-287, 310, 331, 342`. De los 4 correctivos del acta, **2 (`MISSING_ARTIFACT` + `BLOQUEAR`) son consecuencia del borrado previo**, no hallazgos independientes → el acta infla el recuento (esto ya estaba registrado como **F-P4.2**) |

**Nota de honestidad sobre la causalidad**: en esa corrida el bloqueo estuvo **sobredeterminado** — fallaron las dos salidas de forma independiente (sitio caído ⇒ `whatsapp_html_detected=False`; `verification_failed` ⇒ sin boost). Por tanto **la corrida P4 no prueba el defecto de cableado por sí sola**. Y tras la segunda pasada hay que decirlo con más fuerza: **ninguna corrida lo probaría**, porque la rama que el kwarg habilita es inalcanzable por construcción (§2e N2). Lo que la corrida P4 sí prueba es la ruta `:446-453` (campo ausente sin HTML), y esa se abre sola en cuanto el plan promete el botón sin número (D4/N4) — con sitio alcanzable o no.

**Hallazgo asociado a mantener en el alcance**: `corrida.log:4` contiene una API key de Gemini en texto plano (finding **F-P4.5**, §8 no-negociable 5). Verificado 2026-09-17: el archivo está excluido por `.gitignore:161` (`evidence/FASE-P4/corrida/`) y `git ls-files evidence/FASE-P4/corrida/` devuelve vacío, así que **no está publicado** — pero sí en disco. **Actualizado al re-verificar el anchor**: al citarlo, la key quedó además **en el transcript de la sesión de análisis**, de modo que la rotación dejó de ser "un trabajo aparte" y pasó a ser el cierre obligatorio de este hallazgo (§8.5 reescrito).

---

## 4. Por qué esto importa ahora (contexto de producto)

- El enforcement O1-cuarentena se certificó en v4.77.0 sobre **esta** corrida como único caso real. Si la única corrida real del sistema está bloqueada por un falso positivo, el tribunal nunca ha bloqueado *ni dejado pasar* un caso representativo: la certificación es sólida como mecánica, **ciega como calibración**.
- La ruta del warehouse es la que el plan eligió para operar sin auditoría en vivo (observación → `v4complete`). Su caso de uso queda inutilizado por D1.
- **Amplificación medida (segunda pasada)**: el problema **no es exclusivo del warehouse**. En la ruta de auditoría en vivo, un hotel cuyo número aparece en su propio sitio queda en ESTIMATED 0.7 (`main.py:2257`) y 0.7 < 0.9 con `blocking=True` → `severity="error"` → mismo ZIP suprimido; y VERIFIED exige GBP (`main.py:1788`), o sea Places API. La única salida real es que el sitio responda y `SitePresenceChecker` vea el botón (§2b). **El caso Don Alfonso es la versión warehouse de un defecto general**, y eso es lo que hace urgente F-F sobre F-B: F-B arregla un hotel, F-F arregla la clase.
- El umbral de coherencia (0.8) **no está en discusión** y no debe moverse (ver §8).

---

## 5. Direcciones de fix, con tradeoffs

> ⚠️ Actualizado en la segunda pasada: F-A quedó **rechazada por medición** (no-op) y la lista pasó a seis direcciones (F-A′, F-B, F-C, F-D/D′, F-E, **F-F** nueva, que es la que ataca la causa raíz). Son independientes y **componibles**; la recomendación va al final.

### F-A — ~~Cablear `whatsapp_html_detected` a `validate()`~~ → **RECHAZADA tal como estaba planteada; versión corregida en F-A′**
~~Añadir el kwarg en `v4_asset_orchestrator.py:309-312` y `:447-451`, alineándose con `main.py:2544`.~~
- **Medición que la invalida**: la rama que ese kwarg habilita (`coherence_validator.py:437-444`) exige campo ausente **y** HTML detectado, combinación que el único `ValidationSummary` de producción hace imposible (`main.py:2266`, `:2338`). Cablearlo **no cambia el veredicto en ninguna entrada producible**: con HTML detectado el campo llega con ESTIMATED 0.7 y cae en `:469` → `error`. **F-A es un no-op con tests verdes**, y AC-1 (§6) lo premiaría igual.
- **Riesgo añadido**: habilitar mentalmente esa ruta sin cerrar N7 entrega un botón `wa.me/` vacío.

### F-A′ — Cablear la señal donde sí decide: `detect_pains` del orquestador
Derivar `whatsapp_html_detected` **una vez dentro de `generate_assets()`** desde `audit_result.validation` (el objeto ya se recibe en `main.py:2623-2631`) y pasarlo en `v4_asset_orchestrator.py:286`.
- **+**: 1 línea y corrige D2/N1 de verdad. Con HTML detectado, el pain `no_whatsapp_visible` **no se crea** → no hay `whatsapp_button` en `asset_specs` → el check corta en `:424-431` con `score 1.0` → `is_coherent` intacto. Y de paso elimina la divergencia pains-orquestador-vs-main (`:2446` sí la pasa) y el pain fantasma del `pain_ledger.json` (`:301`).
- **−**: no toca el caso Don Alfonso (allí el HTML no se pudo leer, así que la señal es `False` por honestidad, no por cableado). No abre la ruta warehouse sin D1.
- **Riesgo**: bajo. No amplía superficie de datos; alineación con `main.py:2446`.
- **Nota de coste**: no exige cambiar la firma de `generate_assets()` si se deriva internamente; la estimación "2 líneas" del texto original era correcta en tamaño y **incorrecta en ubicación**.

### F-B — Transportar WhatsApp por la ruta del warehouse
Propiedad de contacto en `$defs/observation` + clave en `_FIELD_MAP` (`main.py:3877-3882`) + campo en el formulario.
- **+**: ataca D1 de frente; es la única vía que desbloquea el modo "sin auditoría en vivo".
- **−**: **choca con una decisión documentada**, no con un olvido. `contact_form_ES.md:233-234` prohíbe "pedir ni almacenar… teléfono directo del dueño", y `:237-238` restringe publicar el archivo en repos públicos sin consentimiento. Un número de WhatsApp comercial publicado en el sitio del hotel **no es** "teléfono directo del dueño", pero la línea no traza esa distinción: hay que escribirla explícitamente o el cambio es una violación apparent del contrato de privacidad.
- **Riesgo**: medio-alto. `additionalProperties: False` → cualquier writer/validador existente rechaza la clave nueva hasta actualizar el esquema; y `observations.json` es contenido versionado.
- **Requiere decisión de producto** (del usuario, no del plan): ¿qué se considera canal almacenable?

### F-C — Degradar `whatsapp_verified` a `blocking=False`
`coherence_config.py:60-65`.
- **+**: un valor de config, destraba todo inmediatamente.
- **−**: **pierde la protección que justifica la existencia del check**. El check se escribió contra un incidente concreto (botón de WhatsApp inventado). Hoy, con `blocking=False`, la rama `:446-453` pasa a `severity="warning"` y un `whatsapp_button` sin ninguna evidencia podría publicarse. Es el peor tradeoff del conjunto: cura el falso positivo introduciendo falsos negativos, que es la clase de fallo que el tribunal fue construido para cazar.
- **Riesgo**: alto desde el punto de vista de garantía de producto.

### F-D — Reconectar `whatsapp_validation` en `with_validation`
`assessment_builder.py:116-122`.
- **+**: elimina un parámetro muerto que hoy es una trampa para quien lea el código.
- **−**: **no está claro que deba reconectarse**. Puede ser residuo de una simplificación deliberada (el commentario vecino de `with_coherence:173` indica que hubo barridos de payload sin consumidores). Antes de escribirle comportamiento hay que preguntar por qué se vació.
- **Riesgo**: medio (podría re-introducir doble fuente de verdad).
- **Alternativa F-D'**: **borrar** el parámetro y su argumento en `main.py:2938`. Más honesto si la respuesta a la pregunta anterior es "ya no se usa".

### F-E — Separar "ausencia estructural" de "verificación fallida"
El check codifica *dos* estados distintos como un solo `severity="error"`.

- "Pregunté el número en dos fuentes y no concuerdan / no alcanzan umbral" → **error, bloqueante** (protección legítima, conservarla intacta).
- "Esta ruta de datos nunca pregunta el número" → **no evaluable**, no un fallo.

Mecánica propuesta: el check recibe la señal de **disponibilidad de la fuente** (no solo el HTML) y emite un estado `not_evaluable` — score neutro, `severity="info"`, y **el check se excluye del denominador del score** en vez de contar como 0.0 (factible: `total_weight` se calcula sobre `self.checks`, `:165`). Esto es coherente con la disciplina que el propio repo ya declaró dos veces: AC-G2 en `main.py:3873-3876` ("la ausencia de un campo no se convierte en valor inventado"), y el anti-patrón `contact_form_ES.md:257-259` ("Si no tienes el dato, deja el campo ausente"). Hoy el sistema **respeta** la ausencia en el dato y la **castiga** en la coherencia.
- **Coste**: toca el modelo de `CoherenceCheck` (necesita un estado no-binario) y por tanto su contrato de serialización (`to_dict`, `:45-65`) y los consumidores del acta.
- **Cambio de estatus en la segunda pasada**: **deja de ser "el único fix que cierra el bug"** — F-F lo cierra sin tocar el modelo. Pasa a **deuda registrada con AC propia** (semántica del check), no a pre-requisito de la fase.

### F-F — **NUEVA (causa raíz): que el plan no prometa lo que no puede llenar**
`asset_catalog.py:58-68`: `whatsapp_button` sale de `promised_by=["no_whatsapp_visible", …]` y queda prometido solo por pains donde **hay** número (`whatsapp_conflict`). El dolor "sin WhatsApp visible" se resuelve con un asset de **setup/solicitud del canal** (no necesita el número para ser entregable).
- **+**: ataca N4/D4, que es la raíz. Con este cambio la rama culpable `:446-453` **deja de ser alcanzable por construcción** (no hay botón en el plan si no hay dato que lo llene), el dolor sigue divulgado, `coverage_no_silent_drop` sigue cuadrado, y **AC-3 sobrevive sin tocar umbrales ni config**. Es barato comparado con F-E: una línea de catálogo + un generador auxiliar, contra el cambio de modelo de `CoherenceCheck` que exige F-E.
- **−**: toca el contrato de promesa→asset que la FASE-5 ya corrigió una vez (`"always" ELIMINADO - bug sistemico`, `:67`) — hay que pasar los tests de catálogo/promised-assets y puede mover el recuento de `proposal_asset_alignment`.
- **Riesgo**: medio. Superficie: catálogo, `pain_solution_mapper.SOLUTION_MAP`, `delivery_template`.
- **Compañero obligatorio (N7)**: guardar el centinela `detected_via_html` con `can_use_in_assets=False` (`main.py:2274`) y validar forma de número antes de `_generate_whatsapp_button` (`conditional_generator.py:427-429`). Sin esto, cualquier ruta "rescatada" entrega `https://wa.me/` vacío.
- **Compañero barato (N6/D5)**: que el pre-gate de `main.py:2566` consuma `coherence_verdict_passes()` (`coherence_gate.py:536-558`) en vez de comparar el score → fail-fast antes de gastar 13 assets.

### Recomendación (actualizada; para que la sesión de plan la confirme o la rechace)

**F-F + F-A′ + un verificador automático (V-1). F-E como deuda registrada con AC propia. F-B diferido con decisión de producto explícita. F-C y F-A descartadas** (F-C por falsos negativos; **F-A por medida: no-op**).

1. **F-F** cierra la raíz: deja de prometer un asset cuyo dato-required no existe. Es la única dirección que hace que el bloqueo desaparezca **sin** tocar el umbral, sin tocar `CoherenceCheck` y sin ampliar la superficie de datos personales.
2. **F-A′** (1 línea en `:286`) elimina la segunda fuente del falso positivo y el pain fantasma en el ledger.
3. **V-1 — el verificador, no el parche.** Los tres casos conocidos de este bug son de la misma clase: *parámetro que existe, productor que lo tiene, caller que no lo pasa* — `L-NC6` (whatsapp_conflict), `DT4-R2` (`site_presence_report` en estos mismos sitios de llamada) y ahora `whatsapp_html_detected`. DT4-R2 cableó **un** hermano de la firma y nadie verificó el resto. Receta: un chequeo en `scripts/run_all_validations.py` que **enumere por AST** los llamadores de `CoherenceValidator.validate()` y falle si alguno omite un parámetro declarado obligatorio en una matriz `caller × kwarg`. La matriz **no puede listarse a mano**: una lista fija es exactamente lo que venció en DT4-R2 (lección del repo: *la cobertura del verificador se mide; la cura es un verificador, no el edit*).
4. **Secuencia de decisión**: F-F + F-A′ + V-1 en una fase; F-B y F-E salen de esta fase con dueño y AC, no como notas al pie.

**Lo que esta recomendación NO arregla** (hay que decirlo en el título de la fase): con D4/D1 cerrados, la corrida de observación sigue sin entregar paquete por **F-P4.1** (`IMPLEMENTATION_ORDER.md` stub). Ver §7.

---

## 6. Verificación propuesta (pares verde/rojo, metodo NR7)

NR7 exige que cada AC de bloqueo tenga un check que **prende en rojo al romper** y verde al arreglar — no solo un test unitario del camino feliz. Cada fila es un par medible:

| AC | Verde | Rojo (inyección de falla) |
|----|-------|---------------------------|
| ~~**AC-1**~~ **INVALIDADO** | ~~Corrida con HTML con el botón + sin campo en `ValidationSummary` → score 0.5, `is_coherent True`~~ | **Ese estado no es producible** (§2a punto 2, §2e N2): el único `ValidationSummary` de producción anexa el campo cuando el HTML lo ve. Un fixture lo satisface y el pipeline sigue roto → **verde falso**. Reemplazado por AC-1′ |
| **AC-1′ — El orquestador no fabrica el pain** | Hotel con botón visible en HTML y sin número en schema → `detect_pains` del orquestador **no** emite `no_whatsapp_visible` → no hay `whatsapp_button` en `asset_specs` → el check corta en `:424-431`, `is_coherent == True`, y `pain_ledger.json` no contiene el pain | Quitar el kwarg en `v4_asset_orchestrator.py:286` → el mismo fixture da pain + botón + `is_coherent == False`. **Y además**: el `pain_ledger.json` del fixture debe coincidir con los pains que computa `main.py:2446` para la misma entrada |
| **AC-2 — El plan no promete sin dato (F-F)** | Entrada sin ninguna señal de WhatsApp → `whatsapp_button` **no** está en el plan, el dolor `no_whatsapp_visible` sigue divulgado vía su asset de setup, `coverage_no_silent_drop` pasa | Devolver `no_whatsapp_visible` a `promised_by` de `whatsapp_button` (`asset_catalog.py:67`) → vuelve a aparecer el `error` de `:446-453` |
| **AC-3 — La protección real sigue viva** | `whatsapp_button` generado + `whatsapp_number` con confidence < 0.9 → `severity="error"`, `is_coherent == False` | **Este par no se reversiona**: prueba que el fix no degradó la garantía. Si AC-3 pasa a verde con el fix, el fix es F-C encubierto |
| **AC-4 — El culpable es legible** | `gate_report.json` del coherence gate incluye el **nombre del check** que originó el bloqueo (hoy solo dice "error-severity checks unresolved", `publication_gates.py:632-636`) | Fixture con dos checks en error → el reporte debe nombrar **ambos** y señalar el de WhatsApp por nombre |
| **AC-5 — No regresión de umbral** | `coherence_threshold` sigue en 0.8 y `whatsapp_verified` en 0.9 y `blocking=True`, en las tres capas de config | — (assert de constante, no par) |
| **AC-6 — Ningún botón sin destino (N7)** | Render con `value="detected_via_html"` o con un valor sin dígitos → el generador **no** emite el asset (o emite el de setup); el ZIP no puede contener `href="https://wa.me/"` | Quitar la guarda de forma en `_generate_whatsapp_button` → el fixture produce el enlace vacío y el test prende rojo |
| **AC-7 — La matriz caller×kwarg se enumera sola (V-1)** | El verificador **descubre por AST** los llamadores de `CoherenceValidator.validate()` (hoy: `v4_asset_orchestrator.py:309,447`, `main.py:2539`, `coherence_gate.py:289`) y cada uno declara qué parámetros semánticamente obligatorios pasa | Añadir un cuarto llamador que omita un kwarg declarado → el verificador debe romper. **Si la lista de llamadores está escrita a mano, AC-7 no vale**: eso es justo lo que venció en DT4-R2 |
| **AC-8 — Fail-fast (D5)** | `main.py:2566` usa `coherence_verdict_passes()` → con un check en `error` el pre-gate aborta **antes** de FASE 4 y el log nombra el check | Restaurar la comparación por score → la corrida gasta los assets y muere en FASE 4.5 (comportamiento de la corrida P4) |

**Tests que hoy fijan el comportamiento actual** y hay que revisar antes de tocar (inventario, no sentencia): `tests/regression/test_whatsapp_conflicts.py` (4 functions), `tests/regression/test_hotel_visperas_conflicts.py`, `tests/commercial_documents/test_coherence_generated_assets.py`, `tests/commercial_documents/test_promised_assets_production.py`, `tests/asset_generation/test_site_presence_adapter.py`, `tests/quality_gates/test_domain_gates.py`.

**Medición de cobertura que el inventario original no decía (2026-09-17)**: **ningún test vivo del repo ejercita la rama `:437-444`** — `grep -r "WhatsApp detectado en HTML" tests/` → 0 coincidencias, y ningún paso por `validate()` pasa `whatsapp_html_detected=True` (las coincidencias `=True` están en `test_diagnostic_brechas.py` y `test_pain_solution_mapper.py`, que prueban **`detect_pains`/`_identify_brechas`**, no la coherencia). Es decir: la rama que F-A pretendía "reactivar" no tiene verde que la proteja, y reactivarla no movería ningún test. Esto es lo que hace que AC-1′ y AC-7 sean obligatorios: **el par verde/rojo tiene que anclarse a `detect_pains` y a la matriz de llamadores, no a la rama muerta**.

**Advertencia de alcance**: `modules/quality_gates/domain_gates.py:348-389` contiene un **segundo** `_check_whatsapp_verified`, que lee `assessment["contact"]["whatsapp"]` — un campo que el builder nunca popula. El módulo tiene **0 importadores en producción** (verificado 2026-09-17 con `grep DomainGate`: solo auto-referencias) y mantiene tests vivos en `test_domain_gates.py`. Su severidad de fallo es **`warning`, nunca `error`** (`:358`, `:387`), o sea es **más permisivo** que el check real: un plan que "arregle" este y deje pasar sus tests no habrá tocado nada. Decisión explícita requerida: archivar, o documentar por qué existe.

---

## 7. Alcance: arreglar esto NO produce entregables todavía

Bloqueo **independiente**, documentado en F-P4.1 (`evidence/FASE-P4/informe-observacion.md`): **`IMPLEMENTATION_ORDER.md` es un stub de 468 bytes** en los 4 paquetes del corpus baseline medidos por ese finding (medición propia 2026-09-17 sobre `evidence/FASE-P4/corrida/baseline-snapshot/deliveries/hotelsalentoreal_20260911_unpacked/IMPLEMENTATION_ORDER.md`). Los 4 revisores lo reportan y producen `EMPTY_DELIVERY_TEMPLATE`.

> Precisión que conviene llevar al plan: en la corrida de Don Alfonso **no** se observó ese artefacto entregado — el ZIP fue suprimido antes, por el gate de coherencia. Así que F-P4.1 está probado sobre el corpus baseline, no sobre la corrida de observación; para Don Alfonso es una sospecha razonable (mismo writer) pero sin medir. Los dos bloqueos están en serie, no en paralelo: resuelto D1/D2, el pipeline llegará al revisor y ahí puede aparecer el segundo.

Por tanto el orden importa: **con solo este fix, la corrida de observación sigue sin entregar paquete.** La sesión de plan debe decidir si (i) este plan es *precondition* de una corrida de observación posterior, o (ii) se fusiona con la causa F-P4.1 en una sola fase que sí prometa un `READY_FOR_PUBLICATION` real. La opción (i) repite el patrón que el propio informe P4 registró en **F-P4.2** (el gate borra los documentos y el acta infla CRITICALs derivados) y el que el repo generalizó en **L23/L19**: *agregar el parámetro al consumer sin cablear el producer es un fix incompleto*.

### ⚠️ Corrección mayor de §7 (segunda pasada): **este bug SÍ estaba triajeado, dos veces**

El párrafo anterior de esta sección afirmaba que el hallazgo era **nuevo** de esta sesión y que el plan debía abrirle fila propia. **Eso es falso y acaba de medirse.** La consecuencia práctica no es cosmética: hay dueño, severidad y evidencia previos, y por tanto el plan debe **reabrir** una fila existente en lugar de duplicarla.

| Cuándo | Dónde | Qué dice |
|--------|-------|----------|
| **2026-09-14** | `evidence/FASE-P4/informe-observacion.md`, **F-P4.3** | *"El gate que bloqueó es `coherence`: score 0,8967 ≥ umbral 0,8 pero `is_coherent=False` por **un** check de severidad error, `whatsapp_verified`… El campo no está porque la ruta `observations.json → onboarding` no carga WhatsApp, no porque el hotel no lo tenga. Un **hueco del adaptador** bloquea la publicación"* — **dueño ya asignado**: `modules/onboarding` / adaptador `_observation_to_onboarding_format` |
| **2026-09-14** | mismo informe, **F-P4.2** | El borrado previo de documentos hace que Bots 2 y 4 emitan CRITICAL "por una causa ya resuelta por el gate" → el recuento de 4 correctivos de §3 está inflado (ya lo reportaba el informe, no es hallazgo de esta sesión) |
| **2026-07-25** | `.opencode/context/Historico/CONTEXT-DT-4*.md` (Zione.co), **HALLAZGO-N4 / BUG-6**, write-back en QMind | *"Cualquier hotel con WhatsApp detectado con confidence < 0.9 tendrá delivery bloqueado aunque el botón **EXISTA** en el sitio. Esto es un **falso positivo sistémico, no un caso aislado**"* y lo nombra con patrón: *"ghost module / signature-only wiring"*. Su FIX-PRIORITY-1 punto 5 es literalmente el boost de SitePresence que **sí se implementó después** (DT4-R2, cableado en `:311`/`:450`) |

**Lo que sí es nuevo de esta sesión**: D4/N4 (la colisión de contratos `asset_catalog.py:63-67` ↔ `coherence_config.py:60-65`), N2 (la rama de rescate es inalcanzable por construcción, no por cableado ⇒ **F-A es no-op**), N1 (`detect_pains` en `:286`), N5 (el umbral cae en el hueco de la escala), N6/D5 (pre-gate por score), N7 (centinela → `wa.me/` vacío), y la medición de que ningún test vivo cubre `:437-444`.

**Sobre `evidence/FASE-VERIFY/T4-triaje.md`**: revisado entero (B1-B5, C1-C9), ninguna fila lo menciona — pero eso solo prueba que **el triaje de VERIFY no cubría el informe de P4**, que es donde sí estaba. La lectura correcta del estado del hallazgo es: **F-P4.3 abierta con dueño `modules/onboarding`, sin plan que la haya ejecutado**; B2 registró su consecuencia y B1 explica por qué nadie la vio (no hubo más corridas).

---

## 8. No-negociables para el plan

1. **No tocar el umbral de coherencia (0.8)** ni el de WhatsApp (0.9). Un umbral más bajo no distingue ausencia de verificación; es F-C con otro nombre. **Ampliado**: tampoco "bajar a 0.7 para que ESTIMATED pase", porque eso convertiría en verde el mismo estado que originó el incidente del botón inventado. La palanca correcta es **qué se promete**, no con qué número se juzga (F-F).
2. **No inventar el dato.** Cualquier fix que ponga `whatsapp_number` a partir de un benchmark o un valor por defecto viola la política "No Defaults" del repo y AC-G2. **Incluye** usar `presence_status == "exists"` como si fuera el número.
3. **AC-3 no se reversiona** (§6). La protección contra botón fantasma es la razón de ser del check.
4. **F-B exige decisión de privacidad escrita por el usuario** antes de codificarse (`contact_form_ES.md:233-238`). No reinterpretar la restricción en silencio.
5. **Rotar la API key de Gemini de `corrida.log:4` (F-P4.5) — ya no es "trabajo aparte".** La key está en disco, excluida de git (`.gitignore:161`), y **además quedó expuesta en el transcript de la sesión de análisis de 2026-09-17** al re-verificar el anchor. Regla operativa: **leer los anchors de secretos con máscara** (`sed 's/AIzaSy[A-Za-z0-9_-]*/***/'`) o por línea sin imprimir el valor. Continúa vigente: no propagar el valor a ningún artefacto nuevo (fixtures, evidencia, docs); referenciar solo por finding ID y máscara. El verificador de secretos sigue mirando asignaciones `*.py` y no formatos de key (F-P4.5).
6. **No modificar el árbol `evidence/FASE-P4/`** — es la evidencia de este análisis. Nuevas mediciones, en subdirectorio propio por plan (convención ya registrada en memoria del proyecto).
7. **Ningún fix puede dejar un botón `wa.me/` vacío en el ZIP** (N7/AC-6). Si una ruta "rescata" la verificación sin número, el entregable tiene que ser un asset que no dependa del número, no un enlace muerto.
8. **Prohibido verificar el fix contra la rama `:437-444`.** Es inalcanzable por construcción (§2e N2); cualquier verde obtenido ahí no describe el sistema (AC-1 invalidado).
9. **No abrir fila nueva de triaje**: esto es **F-P4.3** (2026-09-14, dueño `modules/onboarding`) y **HALLAZGO-N4/BUG-6** (2026-07-25). Reabrir y enlazar, no duplicar (§7).

---

## 9. Cómo verificar este contexto por cuenta propia

```bash
# Defecto D2-bis — ni una sola aparición del kwarg en el orquestador
grep -n "whatsapp_html_detected" modules/asset_generation/v4_asset_orchestrator.py   # → 0 coincidencias
grep -n "whatsapp_html_detected" main.py                                            # → 2446, 2544, 2766, 3646

# N1/D2 (el cable que sí decide) — detect_pains del orquestador sin el kwarg
sed -n '286p;301p' modules/asset_generation/v4_asset_orchestrator.py                # → sin whatsapp_html_detected
grep -n "whatsapp_html_detected" modules/commercial_documents/pain_solution_mapper.py # → 338 (default False), 355

# N2 — la rama de rescate es inalcanzable: solo hay un ValidationSummary y :2266 anexa el campo
grep -rn "ValidationSummary(" --include=*.py . | grep -v tests/ | grep -v evidence/  # → main.py:2338
sed -n '2266,2275p' main.py                                                          # → anexa whatsapp_number con el centinela
grep -rn "WhatsApp detectado en HTML" tests/                                          # → 0 (ningún test cubre la rama)

# N7 — el centinela viaja como si fuera teléfono
grep -rn "detected_via_html" --include=*.py . | grep -v tests/ | grep -v evidence/    # → main.py:2270
sed -n '711p' modules/asset_generation/conditional_generator.py                       # → ''.join(... if c.isdigit())

# N3/N5 — el check es insatisfacible: la escala discreta y el umbral 0.9
sed -n '764,772p' modules/commercial_documents/coherence_validator.py                  # → 0.95 / 0.7 / 0.3 / 0.0
grep -n -A5 '"whatsapp_verified"' modules/commercial_documents/coherence_config.py      # → 0.9, blocking=True
grep -n "promised_by" modules/asset_generation/asset_catalog.py | grep whatsapp_button   # → no_whatsapp_visible

# D4 — el conflicto de contratos, cara a cara
sed -n '58,68p' modules/asset_generation/asset_catalog.py
sed -n '60,65p' modules/commercial_documents/coherence_config.py

# D5 — el pre-gate decide por score, el gate canónico por veredicto
sed -n '2554,2578p' main.py
sed -n '536,558p' modules/quality_gates/coherence_gate.py

# Defecto D1 — la propiedad de contacto no existe en el warehouse
python -c "import json;s=json.load(open('data/hotel_observations/hotel_observations.schema.json',encoding='utf-8'));print(sorted(s['\$defs']['observation']['properties']),s['\$defs']['observation']['additionalProperties'])"
grep -ril whatsapp data/hotel_observations/ modules/onboarding/                       # → 0 coincidencias

# Defecto D3 — parámetro muerto
grep -n -A6 "def with_validation" modules/assessment_builder.py                       # → solo asigna validation_summary
grep -n "builder.with_validation(" main.py                                           # → 2938

# El gate no conoce el nombre del check
grep -c "whatsapp_verified" modules/quality_gates/publication_gates.py                 # → 0

# Los dos _check_whatsapp_verified (trampa de alcance) + el muerto es más permisivo
grep -rn "def _check_whatsapp_verified" --include=*.py modules/
grep -rn "DomainGate" --include=*.py . | grep -v tests/ | grep -v domain_gates.py      # → 0 importadores

# Evidencia P4 (ruta real: run/, no output/) y su aritmética
python -c "print((1.5*1.0+1.0*1.0+1.5*0.95+0.5*0.0+1.0*0.8+2.0*1.0)/7.5)"             # → 0.8966666666666666
ls evidence/FASE-P4/corrida/run/v4_complete/hoteldonalfonso/v4_audit/
sed -n '1p' evidence/FASE-P4/corrida/corrida.log                                       # → Empty HTML (línea 1, no 4)
sed -n '4p' evidence/FASE-P4/corrida/corrida.log | sed 's/AIzaSy[A-Za-z0-9_-]*/****MASKED****/'
grep -n "F-P4.3" evidence/FASE-P4/informe-observacion.md                               # → el triaje previo que §7 negaba
```

Estructura del check, para no re-leer 90 líneas: `coherence_validator.py:392-484`; la regla del veredicto en `:173-185`; los pesos (0.5 de un total de **7.5**) en `:101-108`; la config bloqueante en **`modules/commercial_documents/coherence_config.py:60-65`**; el redondeo que explica el "0.9" del JSON en `coherence_validator.py:49`.

---

## 10. Knowledge Center: lecciones aplicables (consultado 2026-09-17; fuentes entre 2026-07-25 y 2026-09-15)

Dos capas, ambas consultadas: el índice local `.opencode/LECCIONES-INDEX.md` y el notebook QMind `iah-cli-lecciones` (`01a04d98-b7bd-778c-8441-26fdc7e35f45`). **Nota operativa**: el plugin MCP no ve ese notebook (scope server-side); la consulta funcional es `qmind retrieve --nb 01a04d98 …` por Bash.

| Lección / fuente | Qué dice | Por qué aplica a este bug |
|------------------|----------|---------------------------|
| **L19 → L23** (`10-analisis: RC1-RC2-ENTREGA-COHERENTE`) | *"El caller debe cablear los parámetros del gate, no el gate inventar defaults… Agregar el parámetro al consumer sin cablear el producer es un fix incompleto (como L19)"* | Es **la clase exacta de D2/N1**, generalizada. Y su "qué lo previene" es literalmente V-1: trazar quién produce el dato al añadir un parámetro, y cablearlo en el caller |
| **L-NC6** (`.opencode/LECCIONES-INDEX.md:91`) | *"Cableado de parámetro existente: `whatsapp_conflict` ya se extraía pero no se pasaba a `_build_30_day_plan()`"* | **Segunda recidiva** en el mismo dominio (WhatsApp) y la misma forma (parámetro que existe, no se pasa). Una lección registrada no produjo un verificador ⇒ la tercera recidiva es esta |
| **DT4-R2** (`.opencode/context/Historico/CONTEXT-DT4-RESIDUAL-FIXES.md`, Veredicto "CONFIRMADO Y AMPLIADO", severidad ALTA) | *"Se debe corregir el flujo completo, no solamente agregar texto a una llamada aislada"* — y enumera los mismos sitios de llamada que este documento volvió a encontrar | El plan DT4 **sí** cableó `site_presence_report` a los 3 sitios y **no** miró el hermano de firma `whatsapp_html_detected`. Ese es el mecanismo por el que D2 sobrevivió a un plan que trató este mismo código |
| **HALLAZGO-N4 / BUG-6** (`.opencode/context/Historico/CONTEXT-DT-4.md`, Zione.co 2026-07-25) | *"Cualquier hotel con WhatsApp detectado con confidence < 0.9 tendrá delivery bloqueado aunque el botón EXISTA en el sitio. Esto es un falso positivo sistémico, no un caso aislado"* + *"mismo patrón ghost module / signature-only wiring"* | **Refuta la pretensión de novedad de §7** y aporta el caso de contraste: en Zione el sitio **sí** respondía y el check falló igual (score 0.3) — la prueba de que el bloqueo no es del warehouse sino de la escala y de la promesa (N5/N4) |
| **F-P4.2 / F-P4.3 / F-P4.5 / F-P4.9** (`evidence/FASE-P4/informe-observacion.md:151-159`) | Doble conteo de CRITICALs, hueco del adaptador con dueño, key en el log, y `suppress()` borrando su propia evidencia | §3 y §7 de este documento debían enlazarse a estas filas desde la primera versión; ahora lo hacen. F-P4.9 además explica por qué la única evidencia en disco del paquete suprimido es el baseline |
| **L-VUP-13 / F-P4.7** | La condición de equivalencia prohíbe pasar por alto un consumo "en defaults en silencio" | Límite duro sobre F-B: la ruta warehouse no puede resolverse con un valor por defecto de contacto (refuerza §8.2) |
| **"vacío ≠ ausente"** (`coherence_gate.py:546-548`, L-SR5) | `declared_is_coherent=None` conserva el comportamiento por score; solo un `False` explícito bloquea | Es la misma distinción que F-E quiere para el check: **ausencia de fuente ≠ verificación fallida**. Ya hay precedente de diseño en el repo para imitarlo |

**Qué no encontró esta consulta**: ninguna lección registra **la promesa de un asset sin su dato-required** (N4/D4) como clase. El repo ya la corrigió una vez "a mano" (`asset_catalog.py:67`: `"always" ELIMINADO - bug sistemico`, FASE-5) y no la generalizó. Si el plan ejecuta F-F, su cierre debe dejar **una lección nueva** para esa clase (verificador de catálogo: todo `promised_by` debe tener `required_field` obtenible), o la cuarta recidiva estará escrita.

---

**Creado**: 2026-09-17 · **HEAD de la primera pasada**: `e8010ce` (v4.77.0) · **Segunda pasada**: 2026-09-17 contra HEAD `38796da` (código idéntico; ver §2e) · **Sesión de origen**: análisis post-corrida FASE-P4, sin implementación.
**Estado de implementación**: **ninguna**. Este archivo es el único artefacto tocado; no se modificó código, tests, docs gobernados ni `evidence/`.
**Uso previsto**: abrir una sesión nueva con `phased_project_executor` y este archivo como insumo único de partida. La primera decisión de esa sesión es §5 (qué fix: **F-F + F-A′ + V-1**, con F-E y F-B como deuda con dueño) y §7 (alcance con F-P4.1, y **reabrir F-P4.3 en vez de abrir fila nueva**); ambas son del usuario.
