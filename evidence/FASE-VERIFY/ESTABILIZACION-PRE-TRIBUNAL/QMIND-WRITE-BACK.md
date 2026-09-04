# 10-analisis: ESTABILIZACION-PRE-TRIBUNAL-2026-09-03 — lecciones aprendidas y decisiones

**Plan**: `ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` (11 fases, v4.74.1 → 4.75.0)
**Fase que capitaliza**: FASE-VERIFY (2026-09-04)
**Nota QMind**: `iah-cli-lecciones`
**Fuente en el repo**: `.opencode/plans/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/10-analisis-post-implementacion.md` §6, §8, §9
**Evidencia de certificación**: `evidence/FASE-VERIFY/ESTABILIZACION-PRE-TRIBUNAL/`

**Balance del write-back (corregido, ver §9)**: 41 lecciones en el ciclo (36 de fases + L-I1 + L-V1…L-V4) ⟹
**32 con texto propio en esta fuente**, **7 fusionadas** en 4 destinos (L-A6+L-V4+L-H4 → `revalidar-citas…`;
L-B5+L-D1 → `concurrencia-sesiones…`; L-D3 → `conteos-tests…`; L-E1 → L-H2) y **2 exclusiones** (L-D5, L-H5).
**32 + 7 + 2 = 41.** El notebook guarda una fuente consolidada por plan: **esta es esa fuente**.

---

## 6. Decisiones Arquitectónicas

> Decisiones no triviales tomadas durante el plan, con rationale y alternativas rechazadas.

| # | Decisión | Rationale | Alternativa rechazada | Fase |
|---|----------|-----------|----------------------|------|
| DA1 | Fuente única (A/B) **antes** que punto 8 (C) | ROADMAP §7.2: «decidir cuál registro manda es precondición de la propuesta dinámica»; reconcilia con §10 del dossier (un «orden sugerido», no mandatorio) **adelantando deliberadamente H10** (independiente de B/C, insumo de F3 y del tratamiento de ledger vacío — ver matiz en `README.md` §Por qué este orden) | Ejecutar §10 literal (punto 8 primero) — rechazado porque el punto 8 sobre registros fragmentados reproduciría el drift | Concepción |
| DA2 | H10 documental y conductual en el **mismo commit** (AC7+AC8) | Memoria `decision-advisory-gates-2-no-3`: los docstrings sueltos se desincronizan del código | Commits separados — rechazado | D |
| DA3 | Punto de partición C1'/C2' **predefinido** | C es la única fase con riesgo real de agotar R2 (60); un C a medias produce artefactos que se contradicen (patrón de los 3 artefactos SalenteReal con `is_coherent: false`) | Improvisar la partición — rechazado | C |
| DA4 | V5 se cierra **sin reversar** BUG-6 | Anti-reversión Zione 2026-07-25: cerrar la escotilla exige distinguir «asset generado y mencionado» de «generado y silencioso», no revertir el status | Revertir `ASSET_GENERATED` de `_JUSTIFIED_STATUSES` — rechazado (segundo péndulo D2→tautología) | G |
| DA5 | V12 se **documenta**, no se edita `.env` | Es decisión OPS; editar `.env` en una fase de refactorización mezcla responsabilidades | Editar `.env` — rechazado | H |
| DA6 | **Arquitectura de dos capas**: Capa 1 = `PainSolutionMapper.PAIN_SOLUTION_MAP` (27 pains) como **universo de pain_id**, contenido intacto. Capa 2 = **nuevo** `SERVICE_IDENTITIES` (8 entradas) como identidad servicio↔asset↔pain | El dossier pedía «decidir cuál registro manda». La respuesta honesta es que **mandan dos, preguntas distintas**: `PAIN_SOLUTION_MAP` responde «qué pains existen y cómo se narran» (27, universo de detección); `SERVICE_IDENTITIES` responde «qué se vende, qué asset lo entrega y qué pain lo hace vendible» (8). Un solo registro no puede servir a las dos sin arrastrar 19 pains no vendibles a la propuesta ni podar el universo de detección. Regla que queda fijada: **ningún registro del repo puede declarar un pain_id ausente de Capa 1** | (a) Promover `PAIN_SOLUTION_MAP` a único canónico y derivar todo de él — rechazado: obliga a la propuesta a recorrer 27 pains y re-introduce por otra vía el `no_breach` que C debe llevar a 0. (b) Promover `PROPOSAL_SERVICE_TO_ASSET` — rechazado: es un dict plano `service→asset` sin pain_id ni descripción, habría que ensancharlo y romper su consumidor de alignment. (c) Crear el canónico dentro de `asset_generation/` y que los demás importen de ahí — rechazado: `commercial_documents` ya importa de `asset_generation` y `financial_engine` también; un canónico ahí convierte una hoja en raíz de ciclo | A |
| DA7 | Ubicación: **`modules/common/service_identity.py`**, con **cero imports del proyecto** | `modules/common/` ya es el hogar de loaders compartidos sin dependencias (YAML/fallback). Un canónico sin imports puede ser consumido por `asset_generation`, `commercial_documents` y `financial_engine` a la vez sin crear un solo ciclo — que es exactamente lo que impediría la adopción y empujaría a alguien a re-copiar la tabla (L-NC4) | Ponerlo en `modules/asset_generation/` (lo que predecía `09` §A) — rechazado por DA6(c). Ponerlo en `data_models/` — rechazado: son modelos Pydantic de dominio, no registros de identidad, y ya tienen sus propios consumidores | A |
| DA8 | **`opportunity_scorer.py` NO se modifica**, aunque figuraba en A4 | Sus claves `no_llms_txt`, `ia_crawler_blocked`, `weak_brand_signals` **no son pain_id**: pertenecen al namespace `brecha_type` (17 entradas propias del scorer), puenteado a pain_id por `pain_to_type` (10 entradas). El grep de AC1 está acotado a `commercial_documents` + `asset_generation` precisamente por eso. Borrarlas rompería `tests/financial_engine/test_opportunity_scorer*.py`, es código dinero-adyacente, y no curaría nada: son dos universos legítimamente distintos | Tratarlos como IDs fantasma y eliminarlos — rechazado: confundir dos namespaces es el mismo error de categoría que produjo la perla `monthly_report → no_faq_schema`. Unificar `brecha_type` y `pain_id` en un solo enum — rechazado para A: es decisión de producto sobre priorización de brechas, excede el presupuesto de la fase y toca dinero; queda como S7 | A |
| DA9 | Criterio **derivar vs validar**: 6 registros se **derivan** del canónico; 6 se **mantienen literales y se validan contra Capa 1** con razón registrada en el propio código y en el suite | Derivar todo es falso rigor: un registro que responde **otra pregunta** no puede derivarse sin cambiar esa respuesta. Ejemplos medidos: `PAIN_TO_ASSET` (11) enruta qué asset *generar* — derivarlo haría que `poor_performance` generara `optimization_guide` en vez de `performance_audit`; `ELEMENTO_KB_TO_PAIN_ID` responde «qué elemento del KB dispara qué pain»; `PAIN_TO_PRESENCE_ASSET` (6) derivado produce 13 y cambia `apply_site_verification`. **Validar contra Capa 1 es suficiente** para impedir el próximo ID fantasma, que es el defecto real de V2/V3 | Derivar los 14 — rechazado: 4 cambios de comportamiento no pedidos en una fase cuyo éxito se mide por delta cero. Dejarlos literales sin validación — rechazado: es el estado que produjo V2 (6 IDs fantasma vivieron años porque nada los contrastaba) | A |
| DA10 | `counts_in_alignment=False` para `informe_mensual` en vez de excluirlo del canónico | BUG-10/FASE-3 excluyó `monthly_report` de `PROPOSAL_SERVICE_TO_ASSET` a propósito: es complemento siempre-activo, no pain-driven. La exclusión vivía como **una omisión en un literal** — invisible e indistinguible de un olvido. Como campo explícito del canónico, la decisión queda **declarada y testeada**, y `PROPOSAL_SERVICE_TO_ASSET` se deriva filtrando por ella | Seguir excluyéndolo del canónico — rechazado: `SERVICE_CATALOG` y `ASSET_TO_PAIN_ID` sí lo necesitan, y esa asimetría era justamente la que fabricó la perla de V3 | A |
| DA11 | **Trigger ≠ atribución**, expresado en dos campos (`pain_id` vs `brecha_candidates`) + un conjunto explícito `REVIEWED_TRIGGER_DIVERGENCES` | Dos mitades de una decisión que ningún registro previo expresaba: `pain_id` es lo que hace **vendible** un servicio; `brecha_candidates` es lo que se le **imputa** en la tabla con su costo. Divergen en 2 de 8 (`seo_local`, `optimizacion_ia_generativa`) y la divergencia es **correcta**. El conjunto declarado la vuelve revisable: el test es bidireccional y falla tanto si aparece una divergencia no declarada como si se declara una que ya no existe | Un solo campo `pain_id` usado para ambas cosas — rechazado: es la causa directa de V4 («la atribución de brechas excluye por diseño el pain real») que C debe curar. Dejar la divergencia implícita — rechazado: el próximo lector la «corrige» y rompe la atribución | A |
| DA12 | **El orden de inserción es parte del contrato** — documentado en el canónico y verificado por contrafactual | `PROPOSAL_SERVICE_TO_ASSET` se recorre en orden de inserción para construir la tabla de servicios de la propuesta. Una dict-comprehension sobre una tupla ordenada preserva el orden, pero nada lo **garantizaba**: si el canónico hubiera sido un `set` o un `dict` reordenado, la propuesta cambiaría el orden de sus filas sin que ningún test fallara. Se verificó midiendo: contenido **y orden** idénticos al literal previo | Usar `frozenset` para las identidades — rechazado por esto mismo. Fijar el orden con un test de valores — rechazado (L-NC10): se probó por contrafactual y se documentó la invariant en el canónico | A |
| DA13 | Cura de AC2: **prohibir la forma numeral** `\b\d+\s+servic` en la narrativa, no comparar contra un número | L-NC10: un test que fija `len(...) == 7` fosiliza el conteo en vez de curar el drift — cuando C cambie el conjunto, el test fallará por la razón equivocada y alguien lo actualizará a 8, re-fosilizándolo. Prohibir la **forma** («8 services», «7 servicios») ataca el mecanismo real del drift: un número escrito a mano en prosa que nadie sincroniza. El test pasa hoy y seguirá pasando tras C sin edits | Comparar el conteo de la narrativa contra el del canónico — rechazado: es L-NC10 literal. Dejarlo solo en la derivación — rechazado: la derivación cura los 3 registros, no los comentarios y docstrings donde el drift también vivía | A |
| DA14 | **Criterio de decisión de los 11 pains muertos**: IMPLEMENTAR solo con **señal verificable en el audit**; sin señal, **DIFERIR con registro**; sin hecho real que narrar, **RETIRAR** | Las 11 decisiones (tabla completa con señal y rationale por pain en `evidence/FASE-B/decision-pains-muertos.md` §3.1-§3.11 y §5): **IMPLEMENTAR** `missing_llmstxt` (`ia_readiness.components["llms_txt"] == 0`, sonda HTTP), `missing_alt_text` (`seo_elements.imagenes_alt is False`), `no_social_links` (`seo_elements.redes_activas is False`), `low_ota_divergence` (solo narrativa; el guard V7 es de H). **RETIRAR** `no_ga4_enhanced`. **DIFERIR** `no_ssl`, `no_schema_reviews`, `no_blog_content`, `low_content_length`, `no_motor_reservas`, `no_monthly_report`. El criterio es uno solo y es el que hace auditable el resultado: un pain que no puede probar su hecho con un dato del audit es **ruido comercial**, no una brecha — emitir sin señal habría convertido el descarte silencioso en **emisión falsa**, que es peor porque aparece en el documento del cliente | Narrar los 11 a mano para «cerrar» la biyección — rechazado: produce 11 brechas inventadas en el diagnóstico y es exactamente el patrón que el plan vino a curar. Retirar los 11 — rechazado: 4 tienen hecho real y solo les faltaba cable; `no_motor_reservas` es el de mayor valor comercial (priority 1, impact high). Retirar los 6 diferidos de Capa 1 — rechazado: exige editar archivos que B tiene prohibidos (`asset_catalog.py` sí se tocó solo para no huérfanizar; Capa 2 no) | B |
| DA15 | **Peso de impacto derivado del `estimated_impact` que Capa 1 ya declara**, declarado en las **4 regiones** del YAML, con fallback Python también derivado (cierra S14/C-5) | Había que decidir explícitamente de dónde sale el peso de cada pain nuevo (petición del prompt, S14). La banda se **leyó** de los 16 valores existentes, no se inventó: `high`→0.20-0.30, `medium`→0.10-0.15, `low`→0.08, y cada peso nuevo tiene un referente en la banda (`low_ota_divergence` `high`→**0.20**, igual que `no_whatsapp_visible` y `low_seo_score`; `missing_alt_text` `medium`→**0.10**; `missing_llmstxt` y `no_social_links` `low`→**0.08**). El fallback dejó de ser un literal mudo: `pain_narratives.get(pain.id, impacto_por_estimado.get(entrada_capa1.get('estimated_impact'), 0.08))`. Las 4 regiones se **preservaron** aunque hoy sean idénticas: son la costura de regionalización diseñada | Inventar pesos nuevos — rechazado: es dinero-adyacente y rompería la comparabilidad con las «4 Razones con impacto monetario». Colapsar las 4 copias regionales en una — rechazado: es decisión de producto, no de refactorización; capturar el beneficio sin perder la costura es **S-B8** (lint de sincronía del key-set). Dejar el fallback en `0.20` — rechazado: es el default mudo de la familia V6/P11/S7 que el plan persigue | B |
| DA16 | **La capa narrativa es TOTAL sobre Capa 1**: el dict `narratives` se queda en sus **16 literales** y el complemento se **deriva** de `PAIN_SOLUTION_MAP` dentro de `_pain_to_brecha` | Petición explícita del prompt: elegir entre derivar, validar o mantener literal con candado. Rellenar el dict a mano hasta 26 construye una **tabla paralela pain_id→texto** (L-NC4) con 10 entradas nuevas que nadie sincroniza; derivarlo **todo** habría borrado 16 narrativas redactadas a mano que son mejores que el `description` de Capa 1. La solución es híbrida y es la única que no duplica: el literal conserva la prosa curada, la derivación garantiza la **totalidad** (`nombre` ← `name`, `detalle` ← `description`, `impacto` ← peso declarado o `estimated_impact`). Medido: `narratives` literal **16→16**, cobertura **26/26**, y `test_narrativa_derivada_sale_de_capa1` lo prueba con un `Pain(name="", description="")` para que la narrativa no pueda estar saliendo del objeto Pain | Rellenar el dict a 26 — rechazado: L-NC4 literal, y es el mecanismo que produjo los 80 literales de S14. Derivar las 26 — rechazado: pierde prosa curada y cambia el texto de 16 brechas ya publicadas. Dejarlo literal con un candado que exija 26 claves — rechazado: L-NC10, fija el conteo en vez de curar la relación | B |
| DA17 | **La partición vive en la EMISIÓN, no en la narrativa**: `Capa 1 = pains emitidos ⊎ PAINS_DIFERIDOS`, con el registro de diferidos declarando motivo y seguimiento | El candado nació con la forma equivocada (partición *narrativa*: `narrados ⊎ diferidos = Capa 1`) y B2 demostró que era falsa — al derivar el complemento, la narrativa pasó a ser total y la partición narrativa quedó vacía. La forma correcta es la que refleja el defecto real: lo que un pain diferido **no tiene** es emisión, no relato. `test_diferidos_forman_particion_con_emisiones` es **bidireccional** (falla si un diferido se emite y si un emitido se difiere), así que la lista no puede pudrirse en silencio ni crecer sin decisión | Mantener la partición narrativa — rechazado: contradice DA16 y dejaba el candado en verde con una afirmación falsa sobre el código. Un candado que solo cuente pains muertos — rechazado: L-NC10, fosiliza el número. Dejar los 6 diferidos implícitos (como estaban) — rechazado: es indistinguible de un olvido, el mismo defecto que DA10 corrigió para `informe_mensual` | B |
| DA18 | **Retirar `no_ga4_enhanced` de Capa 1** (27 → **26**) en vez de darle narrativa | B1 midió que la rama `elif status and hasattr(status, "is_enhanced")` es **insatisfacible**: `is_enhanced` no existe en `AnalyticsStatus` ni se puebla en ningún punto del repo. El pain **nunca disparó**, así que no era una caída silenciosa viva (como afirmaba N-A1) sino el **décimo pain muerto**. Darle narrativa habría dejado en Capa 1 un pain que ningún dato puede producir — basura declarativa. Verificado que no huérfaniza assets: `asset_catalog.py:298` quedó con `promised_by=["no_analytics_configured"]` | Darle narrativa y dejarlo en Capa 1 — rechazado: es lo que el prompt sugería, pero la premisa era falsa (S-B7). Dejarlo en Capa 1 sin narrativa — rechazado: reproduce el dolor de los 9 de V1. Borrar también la entrada de `ELEMENTO_KB_TO_PAIN_ID` — no aplicaba: ese registro no la tiene | B |
| DA19 | **Las 3 emisiones nuevas llevan guard de «medido» explícito**, no solo de valor falso | `seo_medido = bool(seo_elements) and getattr(seo_elements, 'confidence', None) == "high"` y `isinstance(componentes, dict)` antes de leer `llms_txt`. Sin eso, un audit que no midió `seo_elements` emitiría `missing_alt_text` y `no_social_links` por **ausencia de dato**, no por hecho — el patrón «vacío colapsado con ausente» de la memoria del proyecto, y el mismo defecto de forma que V11 y S-B9. `missing_alt_text` además exige `images_without_alt > 0`, para que el pain no se emita sobre un sitio sin imágenes | Emitir con el solo flag en `False` — rechazado: 9 de los 18 tests nuevos son **negativos** precisamente para fijar que no se emite sobre dato ausente. Usar `confidence != "low"` — rechazado: es más laxo y dejaría pasar datos estimados a un pain que se narra como hecho verificado (`confidence=0.9`) | B |
| DA20 | **`low_ota_divergence`: narrativa ahora, guard en H** — el orden forzoso B→H se cumple **sin tocar V7** | El prompt prohíbe arreglar el guard `__iter__` (es de H1/V7) pero exige darle narrativa a este pain ahora, porque si H arreglaba el guard sin narrativa previa el pain pasaba de «nunca dispara» a «dispara y se desvanece». B cumplió las dos puntas: narrativa derivada + peso 0.20 declarado en las 4 regiones, guard intacto en `:447`. Consecuencia más fuerte de lo pedido: como la capa narrativa es total (DA16), cuando H arregle el guard la brecha aparece en el documento **sin editar ninguna segunda tabla** | Arreglar el guard en B — rechazado: violación explícita del perímetro y solapamiento con H. No darle narrativa y confiar en que H lo haga — rechazado: es exactamente el riesgo que S13 documentó. Retirarlo de Capa 1 — rechazado: el hecho es real y la señal (`direct_channel_percentage`) es alcanzable; solo el guard la bloquea | B |
| DA21 | **Un advisory degrada a blocking por la *naturaleza* de su fallo**, no por su severidad declarada (`advisory_degrades_to_blocking`) | Decisión del usuario al elegir entre las opciones de piso. El régimen advisory existe para «ruido que vale la pena divulga pero no frena»; pero hay fallos de un gate advisory que **no son ruido**: `content_quality` con blockers («COP COP», región «default», «0% confianza») es texto invendible, y `proposal_asset_alignment` con `coverage_ratio < 0.8` es una promesa sin respaldo. El criterio es **estructural vs superficial**, y queda expresado en el mismo predicado que decide la publicación | (a) **Advisory nunca bloquea** — rechazado: publicaría un documento con «COP COP» visible. (b) **Devolver `content_quality` a blocking** — rechazado: re-abriría el régimen 10+3 que H10 cierra y castigaría con name-mangling los warnings legítimos. (c) **Umbral numérico inventado** — rechazado: `0.8` no se creó acá, es **el umbral de coherencia que el repo ya usa** (Criterios de Éxito de `AGENTS.md`) ⟹ el piso hereda una decisión existente en vez de fabricar una paralela (L-NC4). Medido: **0 flips de `ready`** sobre las corridas reales disponibles (`evidence/FASE-D/faseD_contrafactual.txt`) ⟹ la degradación fija una semántica para el futuro, no un cambio del resultado de hoy | D |
| DA22 | **`is_ready_for_publication()` se CONECTA al predicado, no se elimina** | Convivía un tercer criterio de decisión con `check_publication_readiness`: `is_ready_for_publication` hacía `any(not r.passed)` plano. Eliminarlo habría sido la cura «obvia» (una función redundante menos), pero **tiene 11 call sites en `tests/quality_gates/` y se muestra en el docstring de la clase (`:241`)** ⟹ es API pública. Se reescribió su cuerpo para delegar en `gate_blocks_publication()`: los **tres caminos** (`check_publication_readiness`, `get_blocking_gates`, `is_ready_for_publication`) deciden ahora con la misma función y no pueden divergir | Borrar la función y actualizar 11 tests — rechazado: rompe API por estética y convierte a D en un cambio breaking no pedido. Dejarla con `not r.passed` y cubrirla con un test — rechazado: es el patrón que el plan persigue (dos oráculos para el mismo hecho, A4/V15); el candado AST `test_check_publication_readiness_no_decide_con_not_passed_plano` habría quedado mintiendo por omisión | D |
| DA23 | **`delivery_quality_report.py::BLOCKING_GATE_NAMES` se deja intacta** — una lista por **régimen**, no una lista global | El repo tiene **cuatro** regímenes que describen la misma severidad (dossier §8.1: docstrings 10+3, código blocking-con-13, `AGENTS.md`, y el de delivery/ZIP). D unificó **el de publicación** y no el de entrega porque las preguntas son distintas: «¿puede salir este documento?» vs «¿se empaqueta este ZIP?». Fusionarlas convertiría un gate de calidad de contenido en un bloqueo de empaquetado, y el régimen de delivery tiene **fase dueña propia (E→F)** — que además es la que toca `alignment_result.py` | Unificar las cuatro listas en una — rechazado: excede el perímetro de D y pisaría trabajo de E/F en el mismo commit. Borrar la de delivery — rechazado: rige el ZIP. Dejar un `TODO` — rechazado: es el estado que produjo el drift. Lo que sí se fijó es la **frontera**: `test_no_hay_tercera_lista_de_severidad_en_el_regimen_de_publicacion` prohíbe una tercera lista **en el régimen de publicación**, sin fingir prohibir la de otro régimen | D |
| DA24 | **`asset_confidence` sigue siendo blocking** — se revierte la premisa del plan que lo contaba como advisory | El plan arrastraba un «10 blocking + 3 advisory» donde el tercer advisory era `asset_confidence`. Medido: es el **único** mecanismo que vuelve no-entregable un paquete Tier C con 100% de assets `ESTIMATED` (dossier §8.2). Hacerlo advisory quitaría el último freno sobre «entregar inventos como verificados», que es el defecto fundacional del proyecto (la transformación v3→v4 es literalmente sobre niveles de certeza). Quedan **2 advisory**: `content_quality` y `proposal_asset_alignment`. La decisión ya estaba tomada antes de D (memoria `decision-advisory-gates-2-no-3`); D la implementó y la fijó con `test_asset_confidence_no_es_advisory` | Tratarlo como advisory con piso — rechazado: no hay piso que preserve el sentido, porque su señal (proporción de assets estimados) **es** el riesgo que representa, no un síntoma de otra cosa. Hacerlo blocking solo en Tier C — rechazado: introduciría una severidad condicional por tier, un quinto régimen, y el candado de una sola fuente lo prohíbe | D |
| DA25 | **Fail-fast en `__init__` si la clasificación no cubre el registro de gates** (`publication_gates.py:268-278`) | Un gate nuevo puede existir en `self.gates` (`:253-267`) sin estar en ninguna de las dos listas. Con `gate_blocks_publication` escrito como `if result.gate_name not in ADVISORY_GATE_NAMES: return True`, ese gate heredaría **blocking por omisión** — conservador pero invisible: nadie habría declarado su severidad. Ahora el orquestador **no se construye** si las listas no son disjuntas o si `set(self.gates) != BLOCKING ∪ ADVISORY`, y el mensaje nombra qué falta (`sin clasificar=[…]`, `fantasma=[…]`) | Default a advisory — rechazado: un gate sin clasificar que no bloquea es una fuga. Default a blocking (lo que hacía el código) — rechazado: es la fuente del régimen 13 plano que H10 denuncia. Solo un test que cuente 13 — rechazado (L-NC10): fija el número, no la relación, y cuando el número cambie por una razón válida alguien lo actualizará y re-fosilizará. El `RuntimeError` no admite verde fingido: se activa al construir | D |
| DA-C1 | **Una sola partición compartida** (`classify_promised_services()`) en vez de duplicar la cura en los dos builders gemelos | El defecto A5 era *independencia* entre gemelos: cada uno con su propio `# Unknown service — skip silently`. Parchear el skip dos veces reproduce la estructura que produce el drift — la próxima edición cambiaría un builder y no el otro, otra vez en silencio. Con la partición como único punto, los builders no pueden divergir (y `TestAmbosBuildersIdenticos` lo fija). Hallazgo del cierre: en producción solo uno estaba vivo (`ProposalAssetMatrix` 0 call sites → S-C7), pero la cura blindó a los dos igual — el muerto puede revivir sin reintroducir el silencio | Parchear el `return None`/`continue` de cada builder por separado — rechazado: es exactamente el patrón «N copias, sin oráculo» que el plan persigue. Dejar solo el builder vivo y borrar el otro — rechazado: eliminar API cubierta por tests en la fase de mayor complejidad, sin ser pedido | C |
| DA-C2 | El complemento always-active sale del denominador **dentro** de `_check_assets_are_justified`, no filtrando `asset_specs` en el orquestador | `_solutions_to_asset_specs` alimenta **dos** consumidores: la coherencia y la **generación** de assets (los `promised_by=["always"]` de D4-FIX). Filtrar arriba habría sacado `monthly_report` de la generación — bajaría `assets_are_justified` de 4 a 2 y perdería entrega real, el defecto exacto que S-C2 documenta para los huérfanos. La exclusión local deja los dientes intactos para cualquier otro asset sin pain (el lado negativo `test_asset_sin_pain_que_no_es_complemento_sigue_restando`: 0.5, `passed=False`) | Filtrar `asset_specs` en el llamador — rechazado: un filtro compartido no puede servir a dos preguntas distintas (misma lección que L-A4/DA9). Relajar el umbral 0.8 — prohibido por el plan (AC6 debe cerrarse por el punto 8, no por el gate) | C |
| DA-C3 | **`vacío ≠ ausente` como contrato**: `pain_ledger=[]` (resuelto, 0 brechas) no colapsa con `None` (sin fuente → catálogo estático legacy) | SR-H2/L-SR5: los 3 sitios que colapsaban (`publication_gates.py` extracción `or []`, derivación `if pain_ledger:`, `v4_proposal_generator.py:1201` `return None`) convertían «el hotel no tiene brechas» en «no sabemos qué prometer» y viceversa. Con la distinción, `no_breach` **dejó de emitirse** cuando hay ledger resuelto — la categoría desapareció, no se filtró (verificado: sin ledger el comportamiento legacy se conserva) | Normalizar `None` a `[]` en la frontera — rechazado: pierde la distinción y re-fosiliza el colapso. Documentarlo sin candado — rechazado: es el estado que produjo el defecto; `TestVacioNoEsAusente` fija los 3 sitios | C |
| DA-C4 | **El punto de partición C1'/C2' predefinido en DA3 no se usó** — C cerró completo | La partición existía por si R2 (60) se agotaba a medias. Medido: C usó 142 iteraciones (2,4× el presupuesto) **y aun así cerró ambas mitades en un solo tramo** — la cadena causal C2↔C3 resultó indivisible (la matriz y el gate consumen la misma partición; partir el commit habría dejado artefactos que se contradicen, que es justo lo que DA3 quería evitar). La red de seguridad no se activó, pero su existencia no fue inútil: permitió decidir el corte sin negociar bajo presión | Partir el commit en C1'/C2' al agotar el presupuesto — descartado *en caliente*: un commit con la matriz dinámica y el gate leyendo la vieja habría re-producido los 3 artefactos SalenteReal que se contradicen. La lección operativa queda para VERIFY: el costo real de la fase MÁXIMA (142) recalibra los presupuestos (S22) | C |
| DA-E1 | **El writer persiste el snapshot como passthrough versionado** — `{"snapshot_version": "1.0", "snapshot": <ya normalizado>}`, sin llamar a `normalize_site_presence()` ni tocar campos | DT4-N2 manda «calcular una vez, propagar el snapshot normalizado — gates validan, no reconstruyen». Normalizar en el punto de persistencia instalaría un **segundo oráculo exactamente delante del archivo** que existe para certificar el primero. La no-reconstrucción no queda como intención: la sonda de `tests/test_site_presence_persistence.py` persiste un snapshot con campos de probe falsificados y afirma que salen **idénticos** al disco | Normalizar dentro del writer «por seguridad» — rechazado: convertiría la persistencia en una tercera capa de normalización con drift silencioso si `normalize` cambia. Escribir el JSON ad-hoc en `main.py` — rechazado: formato sin dueño ni versión; el consumidor de FASE-F (A4) necesita una versión estable del artefacto | E |
| DA-E2 | **La persistencia es best-effort** — `try/except` con `[WARN]`, sin bloquear la corrida — y el punto usa `site_presence_snapshot` (incondicional), no `site_presence_report` | El oráculo en disco es evidencia auditable, no precondición de entrega: un fallo de escritura no invalida el análisis ni los documentos ya producidos — abortar por un problema de disco rompería la arquitectura never-block. Y el snapshot existe siempre (`main.py:2490/:2496/:2500`); el report solo dentro de `if generate_proposal:` (`:2833`) — usarlo habría muerto en el `[WARN]` de cada corrida sin propuesta (el defecto latente de S-E2a, que la elección de E no toca) | Propagar la excepción (fail-fast) — rechazado: el resto de artefactos auditables sigue la convención no-bloqueante y la evidencia no vale una corrida abortada. Delegar la persistencia al camino condicional del report — rechazado: acoplaría el oráculo a `generate_proposal` y dejaría sin snapshot las corridas de solo-diagnóstico, que son las que más lo necesitan | E |
| DA-F1 | **Decisión (a) de N11/P9: se RESPETA `is_coherent`** — el veredicto queda definido **una sola vez** en `coherence_verdict_passes(score, threshold, declared_is_coherent)` (`coherence_gate.py`): `None` = vacío ≠ ausente (legacy score-only para artefactos que no declaran veredicto), solo `False` explícito bloquea, umbral 0.8 intacto. El gate de publicación (`_coherence_gate`, import en `publication_gates.py:56`) y `CoherenceGate.execute`/`execute_from_validator` consumen esa única definición — con degradación CERTIFIED→REVIEW + `can_certify=False` cuando el veredicto veta | El repro del plan (score 0.88 + `is_coherent=false` ⟹ bloqueado) es el defecto «un oráculo decide y otro narra» en su forma horizontal: score continuo y veredicto binario afirman lo mismo y ningún consumidor puede sobreponer al otro. F4 midió que el campo está poblado y es significativo en el corpus (4 flips READY→NOT_READY) ⟹ es el único volteador de veredicto, no un campo muerto | Decisión (b) — eliminar `is_coherent` y dejar solo el score — rechazada: F4 muestra que el campo es el portador del veredicto; borrarlo devolvería al score la última palabra (el defecto de los 3 artefactos SalentoReal). Dejar el gate leyendo el score y divulgar la discrepancia — rechazado: es el estado actual que el plan declara defecto (N11/P9) | F |
| DA-F2 | **A4 se cierra a nivel de CRITERIO, no de copia**: el segundo oráculo (`proposal_asset_alignment.py` ~`:206-220`) consume `is_present_in_production()` del módulo canónico en vez de redefinir la lista de estados; el veto FASE-12B se extiende a `exists_with_issues`; **H7/L-SR3 queda intacto** — decisión (d): NO modificado; el cross-reference V15 de `AlignmentResult` se conserva para artefactos pre-C | «Quién consulta el criterio» cambia; «el criterio» no. Tocar `PRODUCTION_PRESENT_STATUSES` (`site_presence_checker.py`) habría re-abierto la certificación H7/L-SR3 de FASE-SR-E por una fase que no la necesitaba, y redefinir el criterio dentro del segundo módulo era exactamente el defecto A4. V15 se conserva porque los artefactos pre-C tienen presencia con otras formas | Redefinir `PRODUCTION_PRESENT_STATUSES` — rechazado: viola la decisión (d) del prompt. Reescribir `alignment_result._presence_resolved` — rechazado: era la predicción de archivo del plan y resultó **falsa (3ª consecutiva)**: el oráculo que decide vive en `proposal_asset_alignment.py`. Retirar el cross-reference V15 — rechazado: rompería la lectura de artefactos pre-C | F |
| DA-F3 | **Decisiones (b) y (c) de N11/P9: `coherence_gate.py` se CONECTA (no se elimina) y `publication_state.py` se ELIMINA** (675 → 0 líneas, 0 importers verificados por grep antes de borrar) | La clase legacy `CoherenceGate` + el camino `execute_from_validator` son consumidores reales (tests + la degradación CERTIFIED→REVIEW): conectarlos al veredicto los vuelve coherentes con la decisión (a) en ambos regímenes. `publication_state.py` era un duplicado huérfano del régimen de severidad — resucitarlo sería mantener una tercera lista de severidad, el defecto H8 que el dossier censó | Eliminar `coherence_gate.py` — rechazado: perdería el único lugar donde el veredicto tiene definición única. Resucitar `publication_state.py` cableándolo — rechazado: un oráculo muerto revivido es una copia nueva esperando drift (H8 era exactamente eso) | F |
| DA-F4 | **A1 (`skipped ≠ passed`): estado nuevo `NOT_EVALUATED` que no bloquea pero es visible**; los 2 defaults G9 se unifican en `_not_evaluated_g9()` (`delivery_quality_report.py:25`) y el estado se divulga en `human_review_items` (`:287-291`); el régimen de severidad de delivery queda intacto (H10/DA23) | Contar un gate no-evaluado como passed era la mitad conductual de H10 que quedaba viva en delivery: un gate que nunca corrió no es evidencia de calidad. La divulgación es la cura mínima sin cambiar qué bloquea el ZIP — coherente con DA-E2 (evidencia auditable, no precondición) | Bloquear el ZIP con un gate `NOT_EVALUATED` — rechazado: endurecería el régimen de delivery sin decisión de producto. Dejarlo contando como passed sin divulgación — rechazado: es el defecto A1 literal. Dejar los 2 defaults separados — rechazado: 2 copias del default es el patrón «N copias sin oráculo» que el plan persigue | F |
| DA-G1 | **`NOT_EVALUATED` entra al régimen de publicación**: `doc_audit_consistency` sin insumo (sin `diagnostico_text` o sin `audit_data`) reporta `NOT_EVALUATED` — no passed ni failed — y no bloquea (excluido por `gate_blocks_publication`, coherente con A1/DA-F4) | El gate vivía pasando en verde con datos ausentes (SalentoReal 2026-08-31: PASSED con `value=None` y `audit_report` en disco) — exactamente la mitad conductual de A1 que F curó solo en delivery. La inyección es la otra mitad del mismo defecto: `AssessmentPayload.audit_data` + `main.py` cablea `audit_result.to_dict()`; sin cable, el gate no puede dejar de pasar en verde porque nunca ve nada. Un dato contradictorio confirmado sí falla (FAILED, gate blocking desde FASE-D; el modo WARNING legacy se retira) | Dejarlo como PASSED con `value=None` (el defecto NR1 literal) — rechazado. Reportar BLOCKED por datos ausentes — rechazado: castigaría una corrida que no ejecutó la auditoría como si hubiera contradicciones; «no evaluado» es una tercera semántica, la misma que DA-F4 estableció para G9 en delivery. Silenciar el estado en `summary` — rechazado: `test_not_evaluated_gate_divulged_in_summary` lo hace visible (confirma V10) | G |
| DA-G2 | **El atajo favorable de SR-H2 se condiciona a datos primarios del audit**: `critical_issues=[]` + audit ejecutado → recall 1.0 **solo si** `performance.status != "ERROR"`; con el eje caído y nada reportado, recall = 0.0 y el gate bloquea | El atajo de SR-H2 (preservar vacío≠ausente: «no hay críticos» ≠ «no sabemos») era vacuo en la corrida real: PageSpeed ERROR + GEO 29/100 y sin embargo `critical_recall = 1.0`. La cura no es endurecer el default (recall 0 siempre) — es exigir al audit **una señal primaria** de que el detector funcionó antes de creerle la lista vacía. `recall = registrados/(registrados+no-reportados)` y los 4 criterios viejos quedan intactos | Endurecer el default (recall 0 sin lista no-vacía) — rechazado: revertiría SR-H2 para las corridas sanas, el péndulo exacto que L-G1 documenta. Confiar en el atajo sin condición — rechazado: es el defecto NR2 (G2) literal. Marcar PageSpeed ERROR como advisory — rechazado: toca la severidad, territorio de D/DA21-DA25 | G |
| DA-G3 | **El estrechamiento V5 vive en la regla de mención, no en la lista de estados**: `ASSET_GENERATED` permanece en `_JUSTIFIED_STATUSES`, pero solo justifica junto a **mención en el documento**; generado+silencioso = uncovered. El caso «existe en producción» es `VERIFIED_IN_SITE` (primera clase P1-D, preservada por el reconciler) y justifica sin mención. Fixture anti-reversión contra el **gate real** en `evidence/FASE-G/` | Implementación de DA4 (que la declaró en la concepción): los dos regímenes que comparten el status son distintos — «generado y mencionado» (bien) vs «generado y silencioso» (la escotilla V5) vs «verificado en producción» (BUG-6, bien). Revertir el status castigaría al régimen sano de BUG-6 y re-crearía el péndulo D2→tautología; distinguirlos por la segunda dimensión (mención) cura la escotilla sin tocar el fix anterior. Los huérfanos SalentoReal (`indirect_traffic_optimization`, `analytics_setup_guide`) pasan de justificar en falso a FAILED 0.0 | Sacar `ASSET_GENERATED` de `_JUSTIFIED_STATUSES` — rechazado: reversión de BUG-6/N2, el segundo péndulo que DA4 prohíbe. Exigir mención también a `VERIFIED_IN_SITE` — rechazado: un asset verificado en producción no necesita mención para existir; exigírsela re-crearía la tautología inversa. Prohibir el bloqueo de la escotilla con un mock del gate — rechazado: el fixture corre el gate REAL, un mock certificaría un mundo que producción no ejercita | G |
| DA-G4 | **El tratamiento del ledger vacío se unifica tras la normalización** (extiende DA-C3 del diagnóstico al gate de cobertura): fallback/resolved vacíos → PASSED con `coverage_basis` trazado; resolved vacío con original no-vacío → BLOCKED (`reconciler_dropped_entries`), incluida la ruta dict. 4 combinaciones {fallback,resolved}×{vacío,ausente} con test | La escotilla V9 (ledger vacío ≠ PASS trivial, S-C3/C1 DEFINE G4 IMPLEMENTA) no se cierra endureciendo la rama: se cierra **clasificando** — un ledger resuelto con 0 entradas es «resuelto, 0 brechas» (legítimo); un resolved vacío que **perdió** entradas del original es un drop del reconciler (bloquea). La unificación tras normalización es la misma regla que L-F1 fijó para fixtures: una rama por semántica, no por forma de entrada | PASSED incondicional con ledger vacío (el defecto V9 literal) — rechazado. BLOCKED incondicional con ledger vacío — rechazado: re-fosiliza el colapso vacío≠ausente que DA-C3 disolvió y castigaría el caso legítimo. Dejar la 4ª combinación (dict) sin test — rechazado: la ruta dict es la que producción ejercita | G |
| DA-V1 | **AC8 se certifica con la definición (a)** (docstrings + `AGENTS.md` en el mismo commit); la **(b)** del prompt-VERIFY queda como *trabajo de D con candado propio*, no como AC | **S25** era un defecto del plan, no del código: dos definiciones del mismo AC en cuatro documentos. Elegir (a) es coherente con DA2 (el riesgo real que motivó el AC era la desincronización documental) y es la única definición con un test que la reclame (`test_docstrings_no_prometen_el_regimen_antiguo`). Elegir (b) habría dejado ese test **huérfano de AC**. Como (b) además **no es ejercitable sobre artefactos** con una corrida sana (**S-V4**), partirla es la única salida que no infla la certificación | Dejar las dos vivas — rechazado: es la duplicación que el plan persigue (S23/DA13). Reescribir el AC del plan para que fuera (b) y así poder certificarlo — rechazado: **es la regla de oro al revés** | VERIFY |
| DA-V2 | **NR5 se reformula como regla de delta**: `post − pre == tests nuevos de la fase`, `skipped` idéntico, 0 fallos ajenos | **S26**: con el número literal, cinco fases (C, D, E, F, G) «violaron» la NR **por cumplir el plan**. Un invariante que se rompe al trabajar no mide no-regresión, mide inacción. Medido por VERIFY: 848 → **944**, delta +96 atribuible 1:1 a los contract tests, 0 fallos en las dos suites | Conservar 848 con una nota de excepción — rechazado: la nota sería la sexta y destruye el señal/ruido. Contar el árbol completo — rechazado: `tests/` incluye los rojos preexistentes (S5, S27, S-H16) y **la unidad de corrida cambia el resultado** | VERIFY |
| DA-V3 | **Un AC se certifica por mitades: régimen (código+tests) y artefacto (salida real). Si el artefacto no puede expresar el régimen, el AC queda ⚠️ y no ✅** | AC7 y AC6 tienen el diagnóstico opuesto al que el plan esperaba: en código son impecables y en el `gate_report` son **invisibles** (`severity`: 0 ocurrencias; `coverage_ratio`: clave inexistente en la matriz). Marcarlos ✅ porque los tests pasan sería **exactamente la falla que el dossier denunció** (gates que pasan en verde sin ver los datos). Los cuatro ⚠️ del plan comparten forma: régimen correcto, JSON mudo o contradictorio | Certificar ✅ con nota — rechazado (regla de oro). Certificar ❌ — rechazado: el comportamiento **sí** existe y se mide en runtime (11+2, disjuntas, `asset_confidence` blocking, 2 advisories FAILED ⟹ 0 bloqueadores) | VERIFY |
| DA-V4 | **S-F2 se cierra como divergencia de regímenes declarada, no cableada** (G6-delivery sigue leyendo solo score) | Extiende DA23 al punto que F dejó abierto: «¿se empaqueta este ZIP?» y «¿puede publicarse?» son preguntas distintas y el plan ya decidió no fusionarlas. Conectar el veredicto al ZIP endurecería la entrega sin decisión de producto que lo pida. La ventana que abre (score ≥0.8 + `is_coherent=false`) **no ocurrió en la única corrida**: en el artefacto ambas fuentes coinciden (0.8333 + `true`), en los dos sentidos del check | Cablear `coherence_verdict_passes` a G6-delivery — rechazado: un verificador no endurece régimen de entrega. Dejar la fila 🟡 sin dueño — rechazado: es lo que este plan vino a prohibir | VERIFY |
| DA-V5 | **Ningún seguimiento se re-asigna a FASE-RELEASE por inercia**, aunque RELEASE sea la fase que sigue | La evidencia está en el propio plan: **S-C3, S-C4, S-C6, S-E2, S-F2 y S9** llevan re-asignadas C→F→G→H y **ninguna** se ejecutó. Re-asignarlas otra vez «a la fase siguiente» produciría el mismo resultado. RELEASE recibe solo lo que le pertenece por contrato (S11/S-I6 conteos; S-H15/S-H16/S-H17/S-I8 documental e indicadores) | «Que lo cierre RELEASE, que toca docs» — rechazado con el dato de las 6 filas re-asignadas y jamás ejecutadas | VERIFY |
| DA-V6 | **El presupuesto por fase se declara no-verificable bajo sandbox y se recalibra ×3 o se retira** (recomendación formal al executor) | **S22**: nueve fases, nueve excesos (8.6×, 2.4×, 3.3×, 2.4×, 4.0×, 3.1×, ≥4.4×, ≈3×, y VERIFY no pudo medir la suya). El instrumento canónico (`measure_iterations.py`) **no funciona en las sesiones delegadas ni bajo la política de permisos actual**, así que la métrica se auto-reporta con unidad distinta en cada fase ⟹ no es comparable ni auditable, que era su propósito | Seguir sumando cifras de unidades distintas — rechazado: el total «≥1.219/≤440» mezcla `tool_use` con `ids únicos` (H/I) y un tope auto-reportado (A) | VERIFY |

---


---

## 8. Lecciones Aprendidas

> **Petición literal del usuario**: *«lecciones aprendidas»*. La llena **FASE-VERIFY** (V4).
> Formato obligatorio: qué pasó / por qué / qué lo previene + pertinencia INCLUIR/EXCLUIR.
> Las INCLUIR se **proponen** al notebook QMind `iah-cli-lecciones` (el usuario confirma; no se auto-ingiere).

**L-A1 — Un grep de IDs fantasma también cuenta la prosa** *(FASE-A)*
- **Qué pasó**: con el código ya limpio, el grep de AC1 seguía dando 2 positivos. Los habían reintroducido
  **mis propios comentarios explicativos** en `v4_diagnostic_generator.py:160,162`, que nombraban los IDs
  eliminados para explicar qué se había corregido.
- **Por qué**: el criterio de aceptación es textual y no distingue código de comentario. Documentar el
  «antes» en el sitio del «después» vuelve a escribir el string prohibido.
- **Qué lo previene**: el comentario en el sitio debe enunciar **la regla**, no el historial
  («ningún pain_id fuera de `PAIN_SOLUTION_MAP`»); el antes/después pertenece a `evidence/FASE-A/`.
  Al cerrar una fase cuyo AC es un grep, **re-correr el grep después de escribir la documentación**.
- **Pertinencia**: INCLUIR en QMind `iah-cli-lecciones` — aplica a todo AC basado en ausencia de string
  (V11 residuos D6 en FASE-H, V13 en FASE-H).

**L-A2 — El regex del censo se ancla a la raíz, no a la palabra de un idioma** *(FASE-A)*
- **Qué pasó**: el primer escaneo del drift «8 vs 7» usó `\b\d+\s+servicio` y halló **2 de las 3 copias**.
  La tercera decía «8 services» en inglés.
- **Por qué**: `servicio` (servic+io) y `services` (servic+es) comparten raíz pero no terminación. Un
  censo que depende del idioma del comentario no es un censo.
- **Qué lo previene**: anclar a la raíz (`\b\d+\s+servic`) y **validar el escáner contra un conteo conocido
  por otra vía** antes de confiar en su resultado. El contract test definitivo quedó anclado a la raíz.
- **Pertinencia**: INCLUIR en QMind — misma familia que `sondas-url-derivadas-deben-anclarse-al-origen`:
  un derivado que no se ancla al origen real corrompe el resultado.

**L-A3 — Dos namespaces parecidos no son un drift** *(FASE-A)*
- **Qué pasó**: `opportunity_scorer.py` figuraba en A4 por contener `no_llms_txt`, `ia_crawler_blocked` y
  `weak_brand_signals` — los mismos strings que AC1 declara fantasma. **No se modificó**: son claves
  legítimas de `brecha_type` (17 entradas propias del scorer), no pain_id.
- **Por qué**: el dossier censó por **string**, no por **namespace**. Dos universos que comparten nombres
  parecen uno fragmentado. Eliminarlos habría roto `tests/financial_engine/test_opportunity_scorer*.py`,
  en código dinero-adyacente, sin curar nada.
- **Qué lo previene**: antes de declarar un ID «fantasma», **encontrar el registro que legítimamente lo
  posee**. El censo de FASE-A registra namespace y pregunta-que-responde por cada registro, no solo el
  string. Es el mismo error de categoría que produjo la perla `monthly_report → no_faq_schema`.
- **Pertinencia**: INCLUIR en QMind — crítico para FASE-H (V13 gemelos) y para cualquier auditoría futura.

**L-A4 — Derivar no es sinónimo de unificar** *(FASE-A)*
- **Qué pasó**: de 14 registros censados solo **6** se derivaron del canónico. Los otros 6 se mantuvieron
  literales y se **validan contra Capa 1**. Derivar `PAIN_TO_ASSET` habría hecho que `poor_performance`
  generara `optimization_guide` en vez de `performance_audit`; derivar `PAIN_TO_PRESENCE_ASSET` produce 13
  entradas frente a 6 y cambia `apply_site_verification`.
- **Por qué**: un registro que responde **otra pregunta** no puede derivarse sin cambiar esa respuesta.
  La presión por «unificar todo» confunde eliminar la duplicación con eliminar la distinción.
- **Qué lo previene**: el criterio **derivar vs validar** (DA9) + **contrafactual medido** que pruebe delta
  cero en contenido y orden antes de declarar la migración cerrada. Validar contra Capa 1 basta para
  impedir el próximo ID fantasma, que es el defecto real.
- **Pertinencia**: INCLUIR en QMind — insumo directo de FASE-C (los 2 builders) y FASE-F (oráculo único).

**L-A5 — Un test fosilizado puede estar codificando el invariante invertido** *(FASE-A)*
- **Qué pasó**: `test_all_service_catalog_services_have_lookup_entry` falló al unificar. No pedía un número
  desactualizado: exigía que **todo** servicio del catálogo tuviera entrada en el lookup de alignment —
  es decir, codificaba como requisito exactamente el drift que el plan corrige. Se renombró a
  `test_solo_servicios_alineables_tienen_lookup_entry` y se invirtió la aserción.
- **Por qué**: cuando una invariant se rompe durante años, los tests escritos en ese periodo la capturan
  como «lo correcto». Actualizarles el número los deja defendiendo el bug con más fuerza.
- **Qué lo previene**: ante un test fosilizado que falla tras una unificación, **leer qué invariant
  codifica antes de tocar su valor esperado**. Si la invariant es el defecto, se invierte y se renombra;
  si es legítima, se deriva su expectativa del canónico. 6 aserciones de `test_proposal_dynamic.py` se
  trataron así.
- **Pertinencia**: INCLUIR en QMind — complementa `conteos-tests-documentados-metodo-def_test` y aplica a
  FASE-C/D/F, que también desfossilizarán tests.

**L-A6 — Una cita de línea en un plan se vuelve falsa con la primera edición de código** *(FASE-A)*
- **Qué pasó**: al inyectar N-A1 en el prompt de FASE-B se verificaron contra el código las citas que el
  plan hace de las regiones a editar y **4 resultaron falsas** (ver S15). La peor: V6 cita
  `v4_diagnostic_generator.py:3189-3194`, que hoy es la **llamada a `detect_pains`**; el
  `except Exception: return brechas` real está en `:3197-3202`. Esa cita falsa se repetía **12 veces en
  6 archivos** del plan, incluidas **3 en el prompt de FASE-H** — la fase que iba a editarla. También
  V11 estaba corrido en 1 (`:1952`→`:1953`), `dependencias-fases.md` §3 le atribuía a
  `v4_proposal_generator.py` un método que ese archivo **no define** (`_identify_brechas`), y
  `regional_benchmarks.yaml` cita `L2240-2311` para un dict que vive en `:3263-3344`.
- **Por qué**: el plan se escribió contra un snapshot del código y **cada fase que edita desplaza las
  líneas** que las fases posteriores citan. Nadie re-verifica: la cita se copia de archivo en archivo y
  el número sobrevive al hecho que lo hacía cierto. La copia propaga el error más rápido de lo que la
  edición lo produce — 1 caso real se convirtió en 12 apariciones.
- **Qué lo previene**: (1) **regla operativa para cada fase restante**: antes de editar una región
  citada, `grep`/`Read` para confirmar que la línea contiene lo que el plan dice; si no, corregir la cita
  en el plan y avisar. (2) **Preferir símbolos a números de línea** en los prompts de fase:
  `def _pain_to_brecha` no se desplaza, `:3246` sí. (3) FASE-VERIFY audita las citas de los ACs que
  certifique. Complementa `revalidar-citas-de-código-no-revalida-premisas` en el sentido inverso: allá las
  citas eran correctas y las premisas falsas; acá **las citas mismas ya eran falsas**.
- **Pertinencia**: INCLUIR en QMind — aplica a los 9 planes de fase que quedan por ejecutarse y a cualquier
  plan multi-fase que cite código; es una clase de defecto, no un caso aislado.

**L-B1 — Un candado que nace con la forma equivocada falla en rojo aunque el código esté bien** *(FASE-B)*
- **Qué pasó**: B3 escribió el candado de biyección como una **partición narrativa** (`narrados ⊎ diferidos
  = Capa 1`) y lo vio fallar en ROJO, como exige TDD. Pero al implementar B2 — derivando el complemento de
  Capa 1 en vez de rellenar el dict literal — la capa narrativa pasó a ser **total** y la partición quedó
  vacía: el candado seguía en rojo **con el código correcto**. Hubo que reescribir la **forma** del candado
  (narrativa total + partición en la emisión), no el código.
- **Por qué**: el candado se escribió contra la *descripción del defecto* («11 pains sin narrativa») en vez
  de contra el *invariante que la cura iba a establecer*. Cuando la cura elegida (derivar) cambia la forma
  del invariante (totalidad en vez de partición), el test escrito antes la contradice. TDD-rojo no protege
  de esto: el rojo era legítimo, pero por la razón equivocada.
- **Qué lo previene**: decidir la **cura** (DA16) antes de fijar la forma del candado, y escribir el
  invariante que la cura establece, no el que el defecto sugiere. Regla práctica: si un candado afirma una
  **partición**, comprobar que los dos conjuntos no puedan volverse `todo ⊎ vacío` tras la cura — si pueden,
  la partición pertenece a otra capa. Complementa L-NC10 (verificar la relación, no el conteo) y L-A5 (un
  test puede codificar el invariante invertido): acá codificaba un invariante **que la cura iba a disolver**.
- **Pertinencia**: INCLUIR en QMind `iah-cli-lecciones` — aplica a FASE-C (candado `no_breach = 0`),
  FASE-F (oráculo único) y FASE-G (escotillas): las tres escriben candados antes de conocer la forma de la cura.

**L-B2 — Un censo por regex cuenta puntos del fuente, no hechos alcanzables** *(FASE-B)*
- **Qué pasó**: la premisa N-A1 de FASE-A afirmaba que **2 de los 11** pains ausentes (`no_ga4_enhanced`,
  `low_ota_divergence`) «SÍ se emiten y SÍ se descartan hoy». Medido en B1, **ninguno de los dos se
  emitía**: `is_enhanced` no existe en ningún `AnalyticsStatus` del repo y el guard `__iter__` hace al otro
  no-disparable con valor numérico. Los 11 eran pains muertos, no «9 + 2 caídas vivas».
- **Por qué**: `evidence/FASE-A/faseA_narratives_audit.py` contó **puntos de emisión en el fuente** por
  regex. Un `Pain(id="x")` dentro de una rama insatisfacible cuenta igual que uno alcanzable. El número
  «18 emitidos» era verdadero sobre el texto y falso sobre el programa. Es
  `revalidar-citas-de-código-no-revalida-premisas` un nivel más hondo: allá las citas eran correctas y las
  premisas falsas; acá **la medición misma medía otra cosa**.
- **Qué lo previene**: la alcanzabilidad se prueba **ejecutando**, no grepeando. B lo hizo con
  `TestNoGa4EnhancedRetirado`, que le entrega al mapper exactamente el objeto que la rama muerta necesitaba
  y afirma que no aparece. Regla: cuando un argumento depende de «esto sí se emite», **construir el input
  que lo dispararía y observar**. Si no se puede construir, la rama es muerta.
- **Pertinencia**: INCLUIR en QMind — crítica para FASE-H (V6 `except Exception`, V7 guard `__iter__`, V8
  dedup son todas preguntas de alcanzabilidad) y para cualquier fase que herede un censo de otra.

**L-B3 — Un presupuesto sin instrumento de medida no restringe nada, y un instrumento sin corte definido mide una foto** *(FASE-B)*
- **Qué pasó**: el prompt de B fijó ≤40 iteraciones. B usó **345 medidas** al corte de su commit de código
  (`e6d28b8`): **8.6×**. No hubo ningún momento en que la fase «decidiera» excederse — al cerrar B no
  existía ningún contador consultable, así que no hubo señal que atender. Y encima **B publicó mal su propia
  cifra**: escribió **151**, que era el conteo a las 16:38 locales, **antes de terminar el cierre
  documental**, y lo presentó como la medición de la fase. La sesión paralela de D la reprodujo con la misma
  unidad y, en vez de limitarse a confirmarla, la comparó contra su propio corte y dejó escrito «la cifra de
  B al cierre real de su fase es mayor que 151». B lo verificó después y lo corrigió
  (`evidence/FASE-B/faseB_iteraciones.txt`).
- **Por qué**: R2 del executor fija el **tope** pero no el **instrumento** ni el **corte**. Sin instrumento,
  cada fase reporta lo que puede: la cifra de A (55) coincide exactamente con su presupuesto, lo que sugiere
  un tope alcanzado y no una medición. Y con instrumento pero sin corte definido, una sesión que mide a
  mitad del cierre publica un número verdadero sobre el instante y falso sobre la fase — exactamente
  `revalidar-citas-de-código-no-revalida-premisas` aplicado a una métrica: la cita (#151 existe en
  `2026-09-03T21:38:54Z`) era correcta y la premisa («eso es lo que B usó») no.
- **Qué lo previene**: definir **instrumento y corte** juntos, o retirar la métrica del plan. Lo que no sirve
  es mantenerla **simbólica**: un tope que nadie mide no cambia ninguna decisión y su violación no se
  detecta hasta que alguien la reconstruye a posteriori, como acá. **Parcialmente cerrado por D**, que midió
  su propia fase con la misma unidad que B (ids de mensaje de asistente únicos del transcript) y la dejó como
  artefacto re-ejecutable: `evidence/FASE-D/measure_iterations.py <transcript> [corte-ISO]`. El corte
  comparable es **«hasta el commit de código»**, porque el cierre documental añade 14 a B y 133 a D y
  mezclarlos vuelve a hacer las cifras incomparables. Falta (1) adoptarlo como **instrumento canónico del
  plan** y no como utilidad de una fase, (2) fijar ese corte en el executor, (3) resolver qué hacer con A,
  cuya cifra no es reconstruible con ese método, y (4) que **VERIFY** decida si el presupuesto se mantiene
  como métrica o se retira — con las dos fases medidas excediendo en 3.3× y 8.6×, los presupuestos por fase
  están sistemáticamente subdimensionados o la unidad no significa lo que las fases creen. Registrado como
  **S22**.
- **Pertinencia**: INCLUIR en QMind — aplica al executor `phased_project_executor.md` en sí, no a este plan:
  cualquier fase de cualquier plan con R2 tiene el mismo hueco.

**L-B4 — Dos planes distintos pueden compartir el nombre de una carpeta de evidencia** *(FASE-B)*
- **Qué pasó**: `evidence/FASE-B/` tiene **20** archivos, de los cuales solo **13** son de este plan. Los
  otros 7 (`fase_b_preexist.txt`, `fase_b_safe1/2/3.txt`, `fase_b_test.txt`,
  `verify_breach_consistency_static.py` + su salida) son de **otro plan**, commiteados en `d2a9700` («tabla
  de servicios dinámica desde opportunity_scores»), cuya fase también se llamó FASE-B.
- **Por qué**: el nombre de la carpeta de evidencia se deriva del **nombre de la fase**, que no es único
  entre planes, y `evidence/` no tiene un nivel intermedio por plan. B llegó a documentar «12 archivos»
  como el contenido del directorio; un lector futuro puede atribuir a este plan evidencia que no lo es.
- **Qué lo previene**: al cerrar una fase, `ls` + `git log --diff-filter=A -- evidence/FASE-X/` **antes** de
  afirmar qué archivos son propios. Y prefijar los artefactos con una marca distinguible: los de este plan
  son `faseB_*` (camelCase), los del otro `fase_b_*`. Registrado en `09-documentacion-post-proyecto.md` §A
  con la advertencia explícita. Solución de fondo: `evidence/<PLAN>/FASE-X/`, que requiere migrar lo existente.
- **Pertinencia**: INCLUIR en QMind — aplica a FASE-VERIFY, que consolida evidencia de todas las fases y
  puede mezclar planes.

**L-B5 — Dos sesiones del mismo plan sobre el mismo directorio se contradicen entre sí** *(FASE-B)*
- **Qué pasó**: mientras B terminaba su post-ejecución, una **sesión paralela de FASE-D** sobrescribió la
  línea de estado del `README.md` del plan con «⚠️ Esta línea decía "FASE-B ✅": era falso, B sigue
  pendiente». Conclusión **correcta para el repo que esa sesión veía** (el trabajo de B aún no estaba
  commiteado) y falsa para el real. El archivo quedó auto-contradictorio: encabezado vs tabla de Progreso.
  **Resuelto en la segunda pasada de D**, que esta vez **fusionó en vez de sobrescribir**: conservó el ✅ de
  B, agregó el suyo, mantuvo la advertencia de concurrencia que B había escrito, y re-midió por su cuenta las
  iteraciones de B llegando al mismo número con la misma unidad. Esa corroboración externa es el único dato de
  la post-ejecución de B que no verificó B mismo.
- **Por qué**: el estado del plan vive en archivos compartidos y cada sesión lo deriva de `git status` y de
  los tests, no de un canal coordinado. Una sesión que no ve el trabajo sin commitear de otra concluye,
  razonablemente, que ese trabajo no existe — y lo escribe en la **fuente única de estado**. Un `Edit` llegó
  a fallar con «File has been modified since read» porque la otra sesión estaba escribiendo el mismo archivo.
- **Qué lo previene**: (1) **commitear al cierre de cada fase** — R1 del executor ya lo pide y es la
  mitigación real; (2) no correr dos fases del mismo plan en paralelo sobre el mismo directorio; (3) si se
  corre en paralelo, **worktrees**. Al documentar, verificar el estado por **medición propia** (el código
  está en el árbol, el candado pasa, la evidencia es re-ejecutable) y no por lo que otro archivo afirma; y al
  corregir un archivo compartido, **leerlo inmediatamente antes y fusionar**, no sobrescribir.
  Registrado como **S21/S-B15**; el commit de B excluye explícitamente los archivos de D.
- **Pertinencia**: INCLUIR en QMind — es la primera vez que el proyecto corre dos fases en paralelo, y va a
  repetirse con las 8 fases que quedan.

**L-D1 — «Una fase por sesión» no es «una sesión por repo»: lo que se comparte es el índice de git** *(FASE-D)*
- **Qué pasó**: D y B corrieron **a la vez sobre el mismo working tree** (violando R1 del executor). No
  chocaron en código porque `dependencias-fases.md` §3 les asigna archivos disjuntos — pero el commit de D
  tuvo que construirse con `git add` de **15 rutas explícitas** para no arrastrar el trabajo en vuelo de B, y
  un `git add -A` o un `git stash` de cualquiera de las dos sesiones habría mezclado las fases.
- **Por qué**: R1 está formulado como regla de *atención* (una fase por sesión) y el riesgo real es de
  **estado compartido**: un árbol y un índice. Dos sesiones pueden editar archivos distintos y aun así
  corromperse mutuamente al commitear, porque `git add` no pregunta a quién pertenece una ruta. L-B5
  documentó la mitad *documental* del mismo hecho (dos sesiones escribiendo el mismo `README.md`); esta es la
  mitad *de índice*, que es la que puede perder trabajo.
- **Qué lo previene**: (1) en un árbol compartido, **nunca** `git add -A` / `git add .` / `git stash` — rutas
  explícitas y `git status` inmediatamente antes del `add` (no del commit: el índice cambia entre los dos);
  (2) commitear al cierre de cada fase, que es lo que convierte el árbol en una foto estable; (3) si el plan
  exige paralelismo, **worktrees**, no dos sesiones en el mismo directorio.
- **Pertinencia**: INCLUIR en QMind `iah-cli-lecciones` — se va a repetir en las 8 fases que quedan y en
  cualquier plan multi-fase; es una regla del workflow, no de este plan. Complementa L-B5, que ataca la
  duplicación del *estado* y no la del *índice*.

**L-D2 — La evidencia también se fosiliza: un log capturado antes de estabilizar los tests miente** *(FASE-D)*
- **Qué pasó**: el commit de código de D (`76e0257`) incluyó `evidence/FASE-D/faseD_severity_lists.txt`
  registrando **18 tests** del candado de severidad. El archivo commiteado en la misma ruta tiene **8**. El log
  era de una versión anterior del archivo. Se detectó al re-leer la evidencia para documentar, y se regeneró
  (`pytest -v` → 8 passed).
- **Por qué**: todo el plan existe porque los artefactos describían un estado que ya no era. La categoría
  «evidencia» no es inmune: un `.txt` capturado en el minuto 40 describe el código del minuto 40, y el commit
  puede salir en el 120. Un artefacto durable **falso** es peor que uno ausente, porque se cita con confianza.
- **Qué lo previene**: (1) **regenerar todos los logs de evidencia inmediatamente antes del commit**, no
  cuando se ejecutó el test por primera vez; (2) si una fase no produjo artefacto ROJO, decirlo explícitamente
  — D **no** tiene un `tdd-*-ROJO.txt` y por tanto **no puede afirmar** que sus 24 tests «se vieron fallar»;
  lo que puede afirmar es que 8 guardianes AST + 12 conductuales + 4 de checklist pasan, y que el criterio
  anterior (`not r.passed` plano) quedó prohibido por
  `test_check_publication_readiness_no_decide_con_not_passed_plano`.
- **Pertinencia**: INCLUIR en QMind — aplica a las 8 fases restantes y a VERIFY, que consolida evidencia ajena.
  Misma familia que `revalidar-citas-de-código-no-revalida-premisas`.

**L-D3 — Un baseline numérico hace que cumplir el plan cuente como violación** *(FASE-D)*
- **Qué pasó**: NR5 ordena a **todas** las fases preservar «**848 passed / 2 skipped**» en
  `tests/quality_gates` + `tests/asset_generation`. D agregó 24 tests legítimos en `tests/quality_gates` y la
  corrida pasó a **872 passed / 2 skipped / 0 failed** — una «violación» del no-regresión que es exactamente lo
  que la fase debía hacer.
- **Por qué**: la NR está escrita como **invariante de estado** cuando la propiedad que quiere cuidar es
  **ausencia de regresión**. Un número de tests aprobados solo es invariante si nadie agrega tests; en un plan
  que agrega **74 funciones** en tres fases, es incompatible con el propio plan. El ruido resultante es peor
  que el drift: la próxima fase puede concluir que «la NR ya está rota, no importa».
- **Qué lo previene**: formular los no-regresión como **delta**: `passed = baseline + tests nuevos de esta
  fase`, `skipped idéntico`, **0 fallos ajenos a la fase**, y exigir el par pre/post
  (`faseD_baseline_pre.txt` / `faseD_baseline_post.txt`) para que el delta sea verificable y no una
  afirmación. Registrado como **S26**.
- **Pertinencia**: INCLUIR en QMind — es un defecto del *template* de plan (executor §4), no de este plan:
  cualquier fase que agregue tests lo reproduce. Aplica ya a C, E, F, G, H, I.

**L-D4 — Cuatro regímenes para el mismo hecho: cerrar H10 exigió contarlos, no elegir uno** *(FASE-D)*
- **Qué pasó**: para «cuántos gates bloquean» el repo tenía **cuatro respuestas distintas conviviendo**: los
  docstrings decían 10+3, el código bloqueaba los 13 planos, `AGENTS.md` declaraba 10+3 — y su bloque de flujo
  FASE 4.5 nombraba solo **12 de los 13** gates (`grep -c doc_audit_consistency` sobre ese bloque en
  `AGENTS.md` en `76e0257^` = **0**; hoy aparece una vez, en `AGENTS.md:276`). Más un cuarto régimen: el de
  delivery/ZIP en `delivery_quality_report.py::BLOCKING_GATE_NAMES`.
- **Por qué**: cada copia se actualizó en la fase que tocó su capa y nadie tocó las otras tres. La omisión de
  `doc_audit_consistency` en el flujo es el caso puro: el gate existe, está en la tabla de módulos, y sin
  embargo el diagrama del proceso lo ignora — quien use el diagrama para saber qué se ejecuta queda corto.
  Unificar «la severidad» sin enumerar los regímenes habría dejado tres de los cuatro intactos y habría creado
  la ilusión de cierre.
- **Qué lo previene**: (1) **enumerar los regímenes antes de unificar** (la lista de cuatro va a
  `06-checklist` §H10); (2) una sola fuente **por régimen**, declarado en el candado
  (`test_no_hay_tercera_lista_de_severidad_en_el_regimen_de_publicacion` prohíbe una tercera lista **de
  publicación**, sin fingir prohibir la de delivery); (3) el fail-fast de DA25 impide que la clasificación
  quede incompleta. Lo que **nada** de esto previene es la omisión en un diagrama de documentación: esa copia
  no tiene oráculo, por eso `09` §D pide que RELEASE re-lea el flujo completo.
- **Pertinencia**: INCLUIR en QMind — misma familia que `unificar-conteos-derivados-en-dtos-multi-consumer` y
  L-A4; es la evidencia empírica de que el patrón «N copies, no oracle» del dossier no era retórica.

**L-D5 — Un instrumento de medición sin verificar devolvió 0 y casi lo reporto como resultado** *(FASE-D)*
- **Qué pasó**: para cerrar el hueco que B registró como L-B3/S22 («no hay contador de iteraciones»), D dejó
  `evidence/FASE-D/measure_iterations.py`. Su primera corrida con corte por timestamp devolvió **0 ids**. La
  tentación era reportar «0 en el tramo de implementación». Causa: el transcript **mezcla formatos** de
  timestamp (epoch en ms e ISO-8601 UTC) y el corte comparaba cadenas — `'1788468421646' > '2026-09-03T…'`
  lexicamente, así que **todos** los records epoch quedaban fuera. Corregido a segundos UTC, el número en el
  corte del commit de D reproduce exactamente los **114** publicados, y el **151** de B se reproduce con
  instante exacto: su id único #151 aparece en `2026-09-03T21:38:54Z`. ⚠️ **Eso valida el instrumento, no
  la cifra**: 151 era una foto tomada a las 16:38 locales, antes de que B terminara su cierre documental; al
  corte del commit de código de B (`e6d28b8`) el mismo instrumento da **345** → S22 y L-B3.
- **Por qué**: un instrumento nuevo mide casi siempre algo distinto a «0» cuando devuelve 0 sobre datos que se
  ven no-vacíos; el fallo se disfrazó de «el corte está mal puesto» y era una comparación de tipos. Es el
  sesgo inverso al de L-B2: allá el número era verdadero sobre el texto y falso sobre el programa.
- **Qué lo previene**: (1) **validar el instrumento contra una cifra conocida por otra vía** antes de publicar
  lo que produzca (acá: los 151 que B ya había auto-reportado) — la misma regla que L-A2 aplicó a un regex de
  censo. ⚠️ **Y el ancla también tiene que estar verificada**: 151 era una foto a las 16:38, así que el
  instrumento quedó «validado» contra un número verdadero sobre un instante y falso sobre la fase. Un ancla
  mal cortada hace que la validación pase y esconde el error en vez de sacarlo;
  (2) tratar `0` y `todo` como salidas sospechosas por defecto; (3) dejar el instrumento **en el repo,
  re-ejecutable y con su corrección anotada** (`evidence/FASE-D/faseD_iteraciones.txt`): lo que no está en el
  árbol no es auditable por VERIFY.
- **Pertinencia**: INCLUIR en QMind — aplica a cualquier métrica derivada de un artefacto de terceros (logs,
  transcripts, JSON de otra herramienta) y cierra parcialmente L-B3.

---

**L-C1 — Un parafraseo de una fuente en tu propia evidencia se convierte en premisa** *(FASE-C)*
- **Qué pasó**: C escribió dos secciones de evidencia afirmando que «el dossier B5 atribuía el
  `is_coherent=false` a los cerrojos de `promised_assets_exist` y estaba equivocado». Al releer el
  §9.2-B5 **verbatim** al cierre, el dossier decía exactamente lo correcto: *«Causa única:
  `_check_assets_are_justified` = 3/4 = 0.75 … 1 (`monthly_report`) always-on sin pain»* — acertó check,
  fracción, asset y causa común. La premisa falsa la había introducido **el parafraseo de C**, no la
  fuente. Lo que el dossier de verdad no previó (que hacer dinámica la promesa de **servicios** no saca
  a `monthly_report` de la lista de **assets** que el check recorre) era otra observación, no la que C
  le atribuyó.
- **Por qué**: un parafraseo propio, una vez escrito en evidencia, gana autoridad al ser **repetido**
  (4 archivos) en vez de al ser verificado. Cada copia nueva se escribe leyendo la copia anterior, nunca
  el original — el mismo mecanismo de fosilización de L-A6, pero sobre una premisa en vez de una cita.
  Es la **primera instancia en dirección inversa** de `revalidar-citas-de-código-no-revalida-premisas`:
  allá las citas eran correctas y las premisas falsas; acá la premisa falsa era **del parafraseador**.
- **Qué lo previene**: al cerrar una fase, **releer las fuentes originales que la evidencia cita de
  segunda mano** (dossier, ROADMAP, prompts de otras fases) antes de certificar lo que «dicen». Si una
  afirmación sobre una fuente externa va a soportar una decisión, copiarla **verbatim entre comillas**,
  no parafrasearla. La corrección costó reescribir 4 documentos; la regla cuesta un `grep` del original.
- **Pertinencia**: INCLUIR en QMind `iah-cli-lecciones` — aplica a VERIFY (certifica ACs leyendo
  evidencia de segunda mano) y a cualquier informe que resuma una fuente para justificar una decisión.

**L-C2 — Un test rojo heredado entre fases puede contradecir un candado más nuevo: buscar el contract test antes de «arreglar» código** *(FASE-C)*
- **Qué pasó**: S-B11 llegaba a C como un test rojo (`test_proposal_dynamic.py`) que parecía pedir
  «actualizar el test a la baja». Leído el candado de B7 que B había fijado **en ambos sentidos**
  (`test_no_menciona_servicios_adicionales_con_brecha`), el test rojo contradecía el cerrojo, no al
  revés: sus dos premisas eran falsas y la cura fue **corregir el test** (28+/5−), no el código. En
  cambio S-B10 (los 2 assets técnicos) se cerró **re-incorporando el comportamiento** — el test sí
  codificaba una relación vigente.
- **Por qué**: en un plan multi-fase, cada fase hereda rojos de fases anteriores **sin saber si el rojo
  es un defecto del código o un candado que ya ganó el argumento**. Decidir por el síntoma («está rojo,
  arreglemos lo más barato») resuelve el rojo de la forma equivocada la mitad de las veces — y ambas
  direcciones ocurrieron en la misma fase, con la misma superficie de código.
- **Qué lo previene**: ante un rojo heredado, (1) grep de qué **contract test** toca la misma relación;
  (2) si existe y fija lo contrario, el rojo cede — corregir el test y registrar por qué; (3) si no
  existe, decidir cuál invariante manda y fijarlo con test, no solo con el cambio de código. C registra
  las dos decisiones (S-B10 re-incorporar, S-B11 corregir test) con su justificación.
- **Pertinencia**: INCLUIR en QMind — todo plan multi-fase genera rojos heredados; FASE-H va a recibir
  los de S-B12/S-C4/S-C6 exactamente en esta situación.

**L-C3 — Un contrato escrito antes de la implementación puede prometer algo que contradice los tests de aceptación de otra fase** *(FASE-C)*
- **Qué pasó**: la cláusula 5(b) del contrato de C1 (`evidence/FASE-C/contrato-propuesta-dinamica.md`)
  prometía «hacer la tabla técnica dinámica». Al implementar, resultó que **contradice los dos tests**
  que FASE-B le entregó a C en verde (S-B10): hacerla dinámica dejaría de mostrar assets que un
  contract test exige ver. La cláusula no se implementó y la no-implementación quedó **anotada en el
  propio contrato** con la causa, no en silencio.
- **Por qué**: el contrato se escribió contra la descripción del defecto («la tabla es una cuarta
  superficie de promesa estática») sin verificar que el comportamiento «estático» fuera el que los
  tests vigentes exigían. Los contratos tempranos heredan el mismo riesgo que los candados de L-B1:
  fijan la forma antes de conocer todas las restricciones.
- **Qué lo previene**: (1) antes de prometer un cambio, **grep de los tests que cubren la superficie** —
  un test en verde es una restricción con la misma autoridad que el requisito; (2) si el contrato
  resulta incumplible, la corrección va **en el contrato**, con fecha y causa — un contrato silenciosamente
  incumplido es exactamente el patrón «docstring que promete lo que el código no hace» que este plan
  persigue (H10); (3) la decisión de cuál invariante manda es de fase con contexto (→ S-C4, dueño H).
- **Pertinencia**: INCLUIR en QMind — aplica a cualquier contrato/plantilla escrita en la Etapa 1 de un
  plan, y complementa L-B1 (candado con la forma equivocada) desde el lado del contrato.

**L-C4 — Promesa de servicios y lista de assets son superficies distintas: hacer dinámica una no limpia la otra** *(FASE-C)*
- **Qué pasó**: el punto 8 («la propuesta solo promete servicios con brecha») se implementó completo y
  **el `3/4 = 0.75` sobrevivió**: `_check_assets_are_justified` recorre su argumento
  `assets: List[AssetSpec]`, y `monthly_report` se genera incondicionalmente (`promised_by=["always"]`,
  D4-FIX) con `pain_ids=[]` — un servicio que deja de prometerse no deja de generarse. AC6 exigió una
  **segunda decisión** (sacar el complemento del denominador, DA-C2) que ni el dossier ni el plan
  enunciaban como superficie separada.
- **Por qué**: «punto 8» suena a una propiedad («nada se promete sin brecha») pero opera sobre **tres
  superficies con vidas propias**: la tabla de servicios, la matriz/gate, y la lista de assets que
  coherence justifica. El defecto era el mismo (prometer sin respaldo) en las tres, así que parecería
  bastar una cura — pero cada superficie consume su propio conjunto (`services`, `matrix entries`,
  `asset_specs`), y la cura hay que aplicarla donde consume, no donde se decide.
- **Qué lo previene**: al cerrar un defecto «global» (prometer sin respaldo, emitir sin hecho,
  degradar en silencio), **enumerar las superficies que lo materializan** y medir el delta en cada una —
  la misma disciplina que L-D4 aplicó a los regímenes de severidad (4 copias del mismo hecho). Y la
  tercera superficie (tabla técnica, S-C4) quedó como recordatorio: el censo de superficies hay que
  **cerrarlo**, no solo curar las dos primeras.
- **Pertinencia**: INCLUIR en QMind — FASE-F (oráculo único) y FASE-G (escotillas V5/V9) cierran defectos
  «globales» con múltiples superficies; el patrón se repite seguro.

**L-E1 — La paralelización de tracks se decide contra los archivos reales, no contra la tabla del plan** *(FASE-E)*
- **Qué pasó**: §4 y el prompt de E declaraban E1 (snapshot) y E2 (asset_path) paralelizables porque
  «no comparten archivo». La primera lectura de `main.py` mostró que **ambos editan el mismo archivo**
  (persistencia en FASE 0E `:3158-3169`; dicts de `assets_for_quality` `:2798-2817`). E ejecutó los dos
  tracks **secuenciales** y corrigió §4 — la predicción falsa nunca produjo un conflicto de escritura
  porque se detectó antes de delegar.
- **Por qué**: la tabla de paralelización se escribió contra la **descripción de los dominios**
  (persistencia vs serialización), no contra los archivos que cada track toca. Dos problemas disjuntos
  pueden converger en el mismo hub (`main.py`), y en un working tree compartido dos escritores sobre el
  mismo archivo se corrompen (L-D1/S-B15). Es la misma familia de S15, solo que esta premisa ni siquiera
  era una cita de línea: era una afirmación de arquitectura sin verificar.
- **Qué lo previene**: antes de delegar tracks en paralelo, **grep de los archivos que cada uno edita** —
  la unidad de conflicto es el archivo, no el requisito. Si comparten archivo, son un track secuencial
  aunque sus dominios sean disjuntos. La verificación cuesta un grep; el conflicto cuesta una fase.
- **Pertinencia**: INCLUIR en QMind — F/G/H quedan por ejecutar y sus prompts contienen predicciones de
  archivos escritas en la concepción; VERIFY audita.

**L-E2 — La causa raíz de un campo null puede vivir en el caller, no en el módulo que lo serializa** *(FASE-E)*
- **Qué pasó**: A6 decía «`asset_path` se serializa como null aun para entradas LINKED». La matriz y su
  serializador estaban **bien**: los dicts de `assets_for_quality` en `main.py` no incluían la clave
  `path`. Tocar `proposal_asset_alignment.py` (lo que el síntoma sugería) habría curado el módulo
  equivocado y añadido un fallback que disfraza la omisión real.
- **Por qué**: el síntoma se observa en el punto más visible de la cadena (el JSON final), pero la
  omisión ocurrió aguas arriba donde se construyen los dicts. Un campo ausente y un campo null se ven
  idénticos en el consumidor — y la corrección intuitiva ataca el punto donde el problema **se ve**, no
  donde **se produce**.
- **Qué lo previene**: ante un campo null/ausente en un artefacto, **trazar el flujo de datos desde el
  constructor hasta el serializador** antes de editar: grep de dónde se construye cada dict. La prueba
  de causalidad (añadir la clave en el caller y medir el delta) es más barata que editar el módulo
  equivocado. Es la versión de datos de `un-log-de-rechazo-no-es-la-causa`.
- **Pertinencia**: INCLUIR en QMind — FASE-F reescribe el oráculo de presencia (A4) y su primer riesgo
  es tocar el punto visible (gates) en vez del punto de construcción.

**L-E3 — La «no-reconstrucción» de un oráculo no se declara, se hace observable con un test sonda** *(FASE-E)*
- **Qué pasó**: DT4-N2 manda «calcular una vez, propagar el snapshot normalizado — gates validan, no
  reconstruyen». El writer pudo escribirse llamando a `normalize_site_presence()` «por seguridad» y
  ningún test preexistente lo habría detectado. E fijó la propiedad con una **sonda**: el test persiste
  un snapshot con campos de probe falsificados y afirma que salen **idénticos** al disco.
- **Por qué**: una intención arquitectónica que solo vive en la documentación muere en la primera
  edición «defensiva» — el mismo mecanismo que convirtió los docstrings de severidad en el defecto H10.
  La única forma durable de impedir que la persistencia reconstruya es que reconstruir **falle un
  test**: el mismo principio que DA21 (la degradación vive en el predicado) y L-NC4 (la narrativa
  derivada sale de Capa 1, probado con un `Pain` irreconstruible).
- **Qué lo previene**: cada vez que una decisión «X no debe recomputar Y» atraviese una frontera de
  módulo, escribir la sonda que entrega un valor **irreconstruible** y afirma la identidad. El wrapper
  versionado (`snapshot_version: "1.0"`) la complementa: si el formato cambia, la versión delata la
  reconstrucción.
- **Pertinencia**: INCLUIR en QMind — FASE-F (A4 oráculo único) es la fase con mayor presión para
  «normalizar de nuevo»: exactamente la reconstrucción que la sonda prohíbe.

**L-F1 — Un fixture en forma tolerada pero no canónica probaba un defecto que producción no puede producir** *(FASE-F)*
- **Qué pasó**: el fixture de presencia que F escribió para ejercitar el oráculo de alineación
  (`{"results": {...}}`) pasaba `_presence_exists` (que tolera varias formas de entrada) pero era
  invisible para `alignment_result._presence_resolved` (que lee claves de nivel superior) — el test
  reproducía A4 dentro de sí mismo: dos lectores del mismo fixture no se ponían de acuerdo.
- **Por qué**: la forma tolerada del primer oráculo existe para entrada cruda; la forma canónica
  (`normalize_site_presence`) es el contrato entre módulos. Un fixture en forma intermedia prueba el
  camino que producción no ejercita, y su verde no certifica nada sobre el camino real.
- **Qué lo previene**: los fixtures que alimentan a más de un consumidor se construyen con el
  **normalizador canónico**, no a mano en la forma que acepta el primero. El arreglo fue en el TEST
  (fixture → `normalize_site_presence`), no en producción — el código estaba bien; la auto-aplicación
  de L-A1 (re-correr el candado después de escribir el test).
- **Pertinencia**: INCLUIR en QMind — aplica a todo artefacto con forma tolerada (validadores con
  múltiples shapes) y a VERIFY al certificar AC10 con el fixture canónico.

**L-F2 — Score continuo y veredicto binario son dos representaciones del mismo hecho** *(FASE-F)*
- **Qué pasó**: `_coherence_gate` decidía `passed` con el score (≥0.8) mientras el artefacto que
  consume declara además `is_coherent` — score 0.88 con veredicto false se publicaba como coherente.
  F unificó ambos en `coherence_verdict_passes()` y el repro (0.88 + false ⟹ bloqueado) pasó.
- **Por qué**: cuando dos representaciones del mismo hecho coexisten sin definición única, el proxy
  numérico (score) termina sobreponiéndose a la afirmación binaria (veredicto) en algún consumidor —
  es el gemelo horizontal del defecto A4 (dos oráculos verticales para la presencia).
- **Qué lo previene**: cuando un artefacto lleva un valor continuo y un flag derivado de él, **todos**
  los consumidores deciden con una sola función que recibe ambos (`None` = vacío ≠ ausente para el
  legado); el score no decide solo donde existe veredicto. El candado `TestFaseFCoherenceRespetaIsCoherent`
  fija la familia.
- **Pertinencia**: INCLUIR en QMind — la familia «N representaciones sin oráculo» suma su variante
  horizontal, junto a `unificar-conteos-derivados-en-dtos-multi-consumer`.

**L-F3 — La re-evaluación de artefactos persistidos debe reproducir la lectura del consumidor de producción** *(FASE-F)*
- **Qué pasó**: el modelo de medición de F4 se corrigió dos veces: (1) la primera pasada usaba un
  fallback de score pre-gen y pintaba READY corridas ESTIMADAS que producción veía con
  `coherence_score_final=None` (siempre bloqueadas); (2) comparar el veredicto de **un solo gate**
  en vez del veredicto del **paquete** (coherence AND asset_confidence) hacía ver sobre-permisivas
  las corridas ESTIMADAS. Corregidas las dos: **0 corridas liberadas, 4 flips READY→NOT_READY**.
- **Por qué**: una re-evaluación que no reproduce la semántica exacta del consumidor de producción
  (misma fuente del score, misma presencia del veredicto, misma conjunción de gates) mide un mundo
  distinto y su delta es ficción — familia `validar-recomendaciones-contra-outputs-reales` y
  `un-log-de-rechazo-no-es-la-causa`.
- **Qué lo previene**: antes de declarar un delta sobre artefactos persistidos, listar **qué ve el
  consumidor de producción** y hacer que el modelo de lectura derive de esa lista, no de los JSON
  crudos. El delta conservador (0 liberadas, flips que solo bloquean) es la firma de un modelo correcto.
- **Pertinencia**: INCLUIR en QMind — VERIFY certifica AC12/NR8 contra el barrido F4 y debe leer esta
  lección antes de re-medir cualquier corpus.

**L-G1 — Un péndulo (fix A → defecto B → «curar B» parece exigir revertir A) se cura distinguiendo estados, no revirtiendo el fix anterior** *(FASE-G)*
- **Qué pasó**: cerrar la escotilla V5 (assets generados y silenciosos justificaban coherence) tenía
  como cura obvia sacar `ASSET_GENERATED` de `_JUSTIFIED_STATUSES` — que es exactamente la reversión
  de BUG-6/N2 (Zione 2026-07-25) que el plan prohíbe. G la cerró sin tocar la lista: el status
  permanece y el estrechamiento vive en la **regla de mención** del loop de coverage; el caso moderno
  «existe en producción» es `VERIFIED_IN_SITE` (primera clase P1-D) y justifica sin mención.
- **Por qué**: dos regímenes distintos compartían un mismo status. «Generado y mencionado» (bien),
  «generado y silencioso» (escotilla V5) y «verificado en producción» (BUG-6, bien) son tres hechos
  que un solo flag no puede distinguir — revertir el flag castiga al régimen sano y re-crea el
  péndulo: D2→tautología→V5→(si se revierte) BUG-6 de nuevo. La cura es añadir la **segunda
  dimensión** (mención) que separa los casos que el flag colapsa.
- **Qué lo previene**: ante un péndulo, buscar la tercera dimensión que distingue los casos en
  conflicto en vez de mover el flag compartido; y fijar ambos lados con un test anti-reversión que
  corra **el gate real** (el fixture de G usa `publication_gates` sin mocks — un mock certificaría
  un mundo que producción no ejercita). Implementado como DA4/DA-G3.
- **Pertinencia**: INCLUIR en QMind `iah-cli-lecciones` — el patrón es general: dos regímenes
  comparten un dato, curar uno parece romper el otro, la salida es distinguir, no revertir. Gemelo
  de L-F2 (dos representaciones del mismo hecho sin oráculo): acá son dos hechos que comparten
  una representación.

**L-G2 — Un atajo favorable-vacuo se cura contrastándolo con datos primarios del audit, no endureciendo el default** *(FASE-G)*
- **Qué pasó**: el atajo de SR-H2 (critical_issues=[] + audit ejecutado → recall 1.0) daba **1.0 en
  la corrida real** con PageSpeed ERROR y GEO 29/100 — un gate de recall vacuo. Endurecer el default
  (recall 0 sin lista no-vacía) habría roto las corridas sanas: el péndulo de L-G1 por la otra cara.
  La cura condicionó el atajo: `performance.status != "ERROR"` antes de creerle la lista vacía.
- **Por qué**: la ausencia de la lista era **vacío ≠ ausente** (la memoria
  `extractores-de-m-trica-que-colapsan-vac-o-con-ausente-causan` aplicada a un gate): el gate no
  puede distinguir «no hay críticos» de «el eje que los detecta cayó» mirando solo la lista —
  necesita una **señal primaria** del audit que demuestre que el detector funcionó.
- **Qué lo previene**: cada default favorable de un gate se amarra a una señal primaria del insumo
  que acredite su premisa; si la señal falta, el estado es «no evaluado», no «sin hallazgos».
  Consecuencia registrada: FASE-I verá `critical_recall` BLOCKED en la corrida real post-G — es el
  **perfil esperado** del refactor (el defecto quedaba oculto antes), comparar contra esto y no
  contra un 13/13.
- **Pertinencia**: INCLUIR en QMind — extiende la familia vacío≠ausente del extractor al gate que
  consume el extractor; aplica a G9/`NOT_EVALUATED` (DA-G1) y a cualquier gate con default
  favorable.

**L-G3 — Los tests de integración codifican el contrato vigente: al cambiar un contrato, reescribir sus tests en el mismo commit y con registro (patrón S-B11)** *(FASE-G)*
- **Qué pasó**: 3 archivos de tests (`test_doc_audit_consistency_gate.py`, `test_publication_gates.py`
  y un test de integración de sesión previa) codificaban el contrato **pre-G**: pasaban en verde con
  datos ausentes y contaban skipped como passed. G reescribió 12 funciones al contrato post-G
  **en el mismo commit** que el código, con el cambio de contrato registrado — no como
  «arreglar tests que se rompieron».
- **Por qué**: en un plan multi-fase, el test de una fase anterior es **cliente** del contrato que
  esta fase cambia — no un obstáculo. Actualizarlo en silencio esconde el cambio de contrato y deja
  al lector creyendo que el contrato nunca fue otro; dejarlo rojo los llama «regresiones» cuando son
  migraciones. Es la tercera aplicación del patrón S-B11 (C corrigió tests heredados con registro;
  G lo planificó de antemano: 12 reescritas anunciadas en la fila de tests).
- **Qué lo previene**: al cambiar un contrato (nuevo estado de gate, nueva semántica de falla,
  nuevo insumo), grep de los tests que lo codifican **antes** de editar código, y reescribirlos en
  el mismo commit con anotación explícita del cambio. El «12 reescriben el contrato pre-G» del
  README de la fase es la huella que VERIFY necesita para distinguir migración de regresión.
- **Pertinencia**: INCLUIR en QMind — toda fase que cambia un contrato lo reproducirá (H cambiará
  el guard V7 y el mensaje de S-C3; I correrá el sistema entero). Complementa L-A5 (test fosilizado
  codifica el invariante invertido): acá el test era correcto para su época y hay que **migrarlo**,
  no invertirlo.

**L-H1 — Un subagente puede reportar cambios que aún no están en el árbol: el parent debe validar con `git diff --stat` ANTES de dar por perdido un track** *(FASE-H)*
- **Qué pasó**: con dos subagentes trabajando, el parent leyó el árbol, no encontró los cambios de uno de
  los tracks y **lo declaró perdido**. El trabajo existía: la escritura llegó con retraso y apareció
  después. El coste real de la falsa alarma fue **la duplicación de constantes** que el parent había
  escrito por su cuenta para cubrir el hueco, y que hubo que **deduplicar a mano**.
- **Por qué**: en una delegación concurrente, «no lo veo en el árbol» y «no existe» son dos afirmaciones
  distintas. El árbol es un snapshot en un instante; el estado del subagente es asíncrono. El parent
  actuó sobre la ausencia de evidencia como si fuera evidencia de ausencia — el mismo error de categoría
  que el plan persigue en el código (vacío ≠ ausente, SR-H2), aplicado esta vez al **proceso**.
- **Qué lo previene**: antes de decidir que un track falló, `git diff --stat` (y `git status --short`)
  **y volver a mirarlo tras el siguiente punto de sincronización**; y si el parent va a escribir algo
  para «cubrir» un hueco, escribirlo de forma **idempotente con el plan del subagente** (mismos nombres,
  mismo archivo) para que la duplicación sea trivial de detectar y deduplicar.
- **Pertinencia**: INCLUIR en QMind `iah-cli-lecciones` — general a cualquier delegación con subagentes
  sobre el mismo working tree. Gemelo procesal de L-D1/S-B15 (el índice de git es compartido) y de la
  memoria `extractores-de-m-trica-que-colapsan-vac-o-con-ausente-causan`: **la ausencia de señal no es
  señal de ausencia**.

**L-H2 — Dos actores con reescritura completa del archivo sobre el mismo archivo es una condición de carrera, no «regiones distintas»** *(FASE-H)*
- **Qué pasó**: `dependencias-fases.md` §4 declaraba para H dos tracks paralelos, pero **H1 y H3 comparten
  `pain_solution_mapper.py`** y **H2 y H3 comparten `v4_diagnostic_generator.py`**. La fase se ejecutó
  con **2 subagentes + parent**, pero **no en paralelo sobre los mismos archivos**: el reparto final fue
  por **archivos disjuntos** (Subagente 1 = mapper; Subagente 2 = generador; parent = `v4_comprehensive.py`,
  `metadata_validator.py` y V12) y la verificación de solapamiento quedó a cargo del parent, sin conflicto
  de regiones.
- **Por qué**: «dos hunks en regiones que no se tocan» solo es seguro si nadie reescribe el archivo
  completo. Las herramientas de leer-modificar-escribir **materializan el archivo entero** desde la vista
  de quien las usa: si dos actores lo hacen, el que escribe último **publica la foto del árbol que leyó**,
  y las ediciones intermedias del otro desaparecen sin conflicto visible — git no puede avisar porque no
  hay dos commits, hay dos escrituras.
- **Qué lo previene**: regla de reparto para fases delegadas: **paralelizable solo si los archivos son
  disjuntos**; si hay un archivo compartido, ese archivo **lo asume el parent** (o se ejecutan secuenciales
  con `git diff` entre tracks). Es la **segunda vez** que el plan se equivoca aquí (E1/E2 sobre `main.py`
  → **S-E1** / L-E1), así que la corrección debe ser de `phased_project_executor.md`, no de una fase.
- **Pertinencia**: INCLUIR en QMind — aplica a cualquier delegación multi-agente y a la redacción de
  planes: la matriz de conflictos de archivo **es** la condición de paralelización, y hay que re-verificarla
  contra los archivos reales, no contra la tabla de la concepción (→ §5 **S-E1**, **L-E1**, **L-D1**).

**L-H3 — Un estado «del último intento» solo es verificable por render si el render ocurre DENTRO del parche que provoca el fallo** *(FASE-H)*
- **Qué pasó**: el estado `_brechas_detection_state` de V6 se setea en el `except` de `_identify_brechas`.
  El primer test de render falló **dos iteraciones** antes de entender por qué: si el test fuerza el fallo
  y **luego** pide el documento, el propio generador **reintenta** la detección en el camino de render y
  restaura `EVALUATED` — el aviso nunca aparece, no porque falte el aviso sino porque **la condición se
  borró antes de mirarla**.
- **Por qué**: hay dos semánticas posibles para el atributo y el fix las mezclaba: «el último intento de
  detección falló» (estado mutable, vivo, se puede restaurar) vs «la sección que se imprimió se imprimió
  sin datos» (estado de publicación). Un test que ejercita la segunda con el mecanismo de la primera
  produce un rojo que **parece** un bug de render y es un bug de montaje del test.
- **Qué lo previene**: para probar un estado de «no evaluado» que se ve en el documento, el test debe
  **forzar el fallo y renderizar dentro del mismo parche** (mismo objeto, sin llamada intermedia que
  reintente); y si el generador puede reintentar, el estado debe resetearse **por corrida** — como hace
  ahora en `generate()`, que es lo que además evita que el aviso de una corrida contamine la siguiente.
- **Pertinencia**: INCLUIR en QMind — patrón general de los «estados de fase» introducidos por A1/F, G1 y
  ahora V6: el estado solo es auditable si el punto de lectura está **entre** la caída y el reset.

**L-H4 — El prompt de una fase puede llegar con citas fósiles y con un archivo de test que no existe: la regla de re-verificar sigue siendo load-bearing** *(FASE-H)*
- **Qué pasó**: el prompt de FASE-H traía **cinco citas de línea desfasadas** (`:453`→`:447`→`:444`,
  `:694`→`:733`, `:1952`→`:1960`, `:1841`→`:1901`) y **un archivo de test que no existe con ese nombre**
  (`test_v4_diagnostic_generator.py`; los reales: `test_diagnostic_generator.py` y
  `test_diagnostic_brechas.py`). Además el **baseline que citaba («848/2») ya no era el vigente (944/2)**.
- **Por qué**: el plan se escribió contra un árbol que **las siete fases anteriores fueron deformando**:
  cada edición desplaza lo posterior (B +50/+20, D +117, G +60, H +95/+128/+80) y nadie re-sincroniza las
  citas de los prompts ya redactados. El caso del archivo de test es la misma clase de defecto pero en el
  **nombre**: una premisa de concepción que nadie verificó porque «el plan la escribió».
- **Qué lo previene**: la regla que el plan ya tiene (L-A6 / S15: `grep`/`Read` antes de editar, preferir
  **símbolos** a números) se aplica **también al propio prompt de la fase**, y al baseline numérico: medir
  el «pre» sobre **el árbol propio** y no citar el del dossier. Es el **sexto caso** de la clase y el
  primero en el que el fósil estaba en el prompt **de la fase que lo iba a editar**.
- **Pertinencia**: INCLUIR en QMind — refuerza la memoria `revalidar-citas-de-código-no-revalida-premisas`
  en su versión procesal: **toda cifra heredada de un documento es una premisa, no un dato**, incluidas las
  de la propia orden de trabajo (→ **S15**, **S26**).

**L-H5 — Cuando solo necesitas un literal, replicarlo con test anti-deriva es más barato que re-arquitectar el grafo de imports** *(FASE-H)*
- **Qué pasó**: V6 necesitaba el mismo string `NOT_EVALUATED` que definen los gates de publicación. Importarlo
  de `GateStatus` es lo «correcto», pero el import top-level de `modules.quality_gates.publication_gates`
  desde `commercial_documents` produce `ImportError` **por ciclo de paquete** (`publication_gates →
  coherence_gate → commercial_documents.coherence_validator → __init__` del paquete), verificado
  empíricamente. La fase **replicó el valor** y lo amarró con `test_v6_estado_not_evaluated_reutiliza_literal_canonico_del_gate`.
- **Por qué**: el riesgo de replicar no es el valor, es la **deriva silenciosa** del valor. Un test que
  afirma «el literal del generador == el literal del gate» convierte la copia en un **contrato observable**:
  si alguien cambia uno, el test estalla. Romper el ciclo de imports habría tocado el grafo de dependencias
  de dos subpaquetes en una fase catalogada **BAJA-MEDIA**, con riesgo de romper consumidores de F/G — el
  remedio más caro para un defecto de un string.
- **Qué lo previene**: regla de decisión explícita: **(i)** si el criterio es **lógica**, se extrae a un
  módulo sin dependencias (como se hizo aquí mismo con `modules/common/performance_status.py`, donde el
  documento y el audit sí necesitaban compartir **un predicado**); **(ii)** si el criterio es **un literal**,
  replicar + **test de identidad** entre las dos vistas. La diferencia entre (i) y (ii) es si hay comportamiento
  o solo una cadena.
- **Pertinencia**: INCLUIR en QMind — gemelo constructivo de L-NC4 (no crear tablas paralelas): cuando el
  ciclo de imports lo impide, la copia **con candado** es la tercera vía, y hay que decir por escrito que
  lo es. Aplicada en la misma fase en las dos direcciones (V11 → módulo compartido; V6 → literal replicado).

**L-H6 — Un hallazgo «texto viejo en dos sitios» hay que barrerlo hasta la fuente: cerrar solo el documento dejaba al audit mintiéndole al cliente** *(FASE-H)*
- **Qué pasó**: V11 estaba descrito como «residuos D6» y su fila del plan citaba **dos posiciones**. Barrido
  hasta la fuente, resultó **tres frentes**: el texto del documento, el **mensaje que produce el audit** y la
  **auto-contradicción del `execution_trace`** (`pagespeed_api` en `executed` y en `skipped` a la vez) — más un
  **criterio compartido** que el documento y el audit decidían cada uno por su cuenta. Cerrar solo el del
  documento habría dejado el del audit mintiendo, porque `extract_top_problems`
  (`modules/commercial_documents/data_structures.py:532-536`) **vierte las recomendaciones textuales del
  audit directamente en el diagnóstico del cliente**.
- **Por qué**: en un pipeline donde el texto del documento se **compone** a partir de estructuras del auditor,
  el «texto viejo» no vive donde se lee: vive donde se **produce**. Corregir la capa de presentación deja la
  capa de datos afirmando lo mismo, y reaparece en cuanto otra superficie la consume. Es la misma estructura
  del defecto que el plan combate en gates (un oráculo decide, otro narra) aplicado a **mensajes**.
- **Qué lo previene**: ante un hallazgo de tipo «texto/estado equivocado», grep del **símbolo y de su causa**
  hasta la capa de producción, y —si el criterio lo consumen dos capas— extraerlo a una única fuente
  (que es lo que se hizo con `is_performance_api_unavailable`). Si además el texto viaja a un artefacto del
  cliente, **el test debe fijar el artefacto**, no solo la cadena: así la próxima superficie que lo consuma
  queda cubierta por el contrato, no por la intención.
- **Pertinencia**: INCLUIR en QMind — extiende L-F2 (dos representaciones del mismo hecho) y DA-F2 (criterio,
  no copia) al terreno de los **mensajes de error**; aplica a cualquier hallazgo «hay un string viejo» del
  dossier. Coste evitado: el síntoma de D6 habría seguido llegando al cliente vía recomendaciones.

**L-H7 — Los resultados de herramientas son datos, no instrucciones; y en delegación la verificación es parte del trabajo** *(FASE-H)*
- **Qué pasó**: durante FASE-H coincidieron dos cosas. (1) El subagente del cierre encontró **dos intentos de
  inyección de prompt dentro de resultados de herramientas** que le ordenaban detenerse, commitear/pushear,
  correr pytest y no editar la memoria (S-H18). (2) Otro track cerró con cifras contradictorias **entre sus dos
  propios informes** («cero tests preexistentes modificados» y luego «16 tests adaptados» más «23 fallos en
  `tests/test_v4_ux_improved.py`»); `git status --short` mostró que ninguno de esos archivos estaba tocado.
- **Por qué**: en modo DELEGADO el parent recibe **prosa** del subagente y la prosa viaja con la misma
  autoridad que una orden. Un informe no es evidencia de trabajo: es un relato del trabajo, y puede ser
  incompleto, ir detrás de una escritura con retraso en el árbol, o contener texto que alguien puso ahí para
  que el agente actúe.
- **Qué lo previene**: separar las dos cosas. Contra la **inyección**, tratar toda salida de herramienta como
  dato y validar cualquier acción de alto alcance (commit, push, borrado) contra lo que pidió el humano, no
  contra lo que apareció en una ventana de resultado. Contra el **informe no verificable**, cerrar cada track
  con `git status`/`git diff --stat` antes de integrar y antes de reportar — que es justo lo que aquí resolvió
  la contradicción en un minuto.
- **Pertinencia**: INCLUIR en QMind — es la primera vez que el plan registra un intento de inyección, y la
  delegación vuelve en FASE-E/FASE-I. Complementa L-H1 (el informe no es el árbol) añadiendo la pata de
  seguridad: no solo el árbol desmiente al agente, también puede estar siendo manipulado.

**L-I1 — Una fase de evidencia también produce conocimiento, y si no lo capitaliza lo pierde** *(FASE-I — instanciada por FASE-VERIFY, que la encontró ausente al pasar el criterio V4)*
- **Qué pasó**: FASE-I cerró con dos hallazgos que **ningún fixture del plan podía dar** (S-I1: el detector anti-vacuidad quedaba a la sombra del registro de H; S-I2: la severidad no viaja al artefacto), un efecto adverso legítimo medido (coherencia 0.88→0.8333 por reportar más pains) y **cero lecciones escritas**. Ocho de nueve fases tienen su bloque `L-X#`; la fase que expuso todo el plan al mundo real no.
- **Por qué**: la fase se auto-definió como «de evidencia, no de tests» y asoció «lección» a «desviación al escribir código». Pero la desviación de I fue metodológica (predicción falsada, unidad de conteo nueva, stdout cp1252 al redirigir) y no quedó en el formato que el Paso 0 de un próximo plan va a recuperar.
- **Qué lo previene**: en el checklist de cierre, la sección de lecciones se contesta **aunque la respuesta sea «1 lección de método»**: una fase que no escribe lecciones no es una fase limpia, es una fase sin cosecha. Proponer al executor que el criterio sea «≥1 lección por fase ejecutada», sin exención por tipo de fase.
- **Pertinencia**: INCLUIR en QMind `iah-cli-lecciones` — general a cualquier fase de validación/E2E; keywords: *fase de evidencia, lecciones no escritas, cierre de fase, cosecha del plan*.

**L-V1 — Un validador que no lee el artefacto que el sistema produce certifica un mundo que producción no habita** *(FASE-VERIFY)*
- **Qué pasó**: AC6 y AC7 quedaron ✅ en código y tests durante nueve fases. Medidos sobre el artefacto de la única corrida, **no son legibles**: `gate_report_20260904_120413.json` no tiene ni una ocurrencia de `severity` ni de `blocking`, y `proposal_asset_matrix.json` no tiene clave `coverage_ratio`. AC8(b) tampoco es ejercitable: ningún advisory falló y el `human_checklist.md` del run pertenece a otro régimen (delivery).
- **Por qué**: el plan formuló los ACs sobre la **configuración** del sistema (qué listas existen, qué devuelve qué función) y no sobre su **salida**. Un contract test de código no puede detectar la ausencia de una clave en un JSON que nadie lee.
- **Qué lo previene**: exigir en cada AC **el artefacto y la clave donde se lee su valor**, y un test de serialización por cada propiedad de régimen que deba viajar a disco. Regla operativa: si un AC no puede responder «¿dónde lo vería un humano que solo tiene el ZIP?», está incompleto.
- **Pertinencia**: INCLUIR en QMind `iah-cli-lecciones` — general a cualquier plan con gates/validadores; keywords: *AC verificable sobre artefacto, severidad no serializada, gate_report, test de serialización, régimen vs salida*.

**L-V2 — Quien cambia un contrato barre sus tests espejo en TODO el repo, no solo en el directorio de su fase** *(FASE-VERIFY)*
- **Qué pasó**: FASE-F cambió el contrato de G9 (`skipped: true` → `state: NOT_EVALUATED`), reescribió los 2 tests que le incomodaban en `tests/quality_gates/` y dejó **rojo en HEAD** `tests/delivery/test_delivery_contract.py::TestP05G9Gate::test_g9_gate_skipped_when_no_matrix`. Causa probada con `git log -S`: la clave desapareció en `23d0978` y el test no se toca desde `568a9c8` (pre-plan).
- **Por qué**: el instrumento de no-regresión de la fase (NR5) cuenta **dos directorios concretos**; un test fuera de esa ventanilla no puede aparecer en el informe, así que «suite verde» significó «mis dos suites verdes». Es la asimetría entre *cambio de contrato* (global) y *verificación de contrato* (local).
- **Qué lo previene**: antes de cerrar, `grep -rn '<clave modificada>' tests/` sobre el repo entero y correr los contratos de otras fases (`pytest -k "contract"` los encuentra). Aquí eso habría dado el rojo en 4 segundos. Refuerza **L-G3** con el caso en que el test espejo vive en otro directorio.
- **Pertinencia**: INCLUIR en QMind `iah-cli-lecciones` — extiende **L-G3**; keywords: *contrato de clave, tests espejo, grep de la clave, ventanilla de NR, test rojo heredado*.

**L-V3 — La prosa de un artefacto que llega al cliente es superficie de contrato, no comentario** *(FASE-VERIFY)*
- **Qué pasó**: en el `asset_generation_report.json` de la corrida, `promised_assets_exist` afirma *«7 servicios verificados via PROPOSAL_SERVICE_TO_ASSET»* cuando la matriz dinámica promete **4** y excluye **3** nombrándolas. En el mismo run, el gate `proposal_asset_alignment` escribe `«4/4 servicios comprometidos cubiertos»` con `details.total_services: 1`. Dos números, mismo objeto, mismo día.
- **Por qué**: el plan curó las **tablas** de identidad y dejó intactos los **mensajes que citan sus conteos**. Un mensaje con número literal es una copia más del registro — y la causa raíz del dossier («consumidores derivan de copias parciales») describe exactamente eso, solo que en prosa.
- **Qué lo previene**: derivar los conteos del texto de la misma fuente que los datos (DA13 aplicado a artefactos) o prohibir el número; y un candado de consistencia mensaje↔`details`.
- **Pertinencia**: INCLUIR en QMind `iah-cli-lecciones` — misma familia que `unificar-conteos-derivados-en-dtos-multi-consumer`; keywords: *mensaje con conteo literal, 7 servicios verificados, message vs details, divulgación en artefactos*.

**L-V4 — Una cita de línea caduca antes de que se certifique el fix: 14 de 16 ya estaban desfasadas** *(FASE-VERIFY)*
- **Qué pasó**: al auditar las citas que los ACs usan (criterio L-A6 de la V1), **solo 2 de 16** seguían en su número (`delivery_quality_report.py:25`, `publication_gates.py:56`); las otras 14 están entre −88 y +104 líneas de desplazamiento (**S-V6**). El plan las heredó del dossier y de sus propios prompts, y cada fase que editó esos archivos movió las siguientes.
- **Por qué**: el plan es un documento **multi-fase** que cita posiciones en archivos que las mismas fases reescriben. Una cita de línea es un recurso con fecha de caducidad escrita en el propio plan.
- **Qué lo previene**: citar **símbolos** (`def classify_promised_services`, `BLOCKING_GATE_NAMES`) — no se desplazan — y llevar la re-verificación como **tarea de certificación**, no como nota. Cambio de plantilla propuesto al executor (`phased_project_executor.md` §2): prohibir números de línea en criterios de aceptación.
- **Pertinencia**: INCLUIR en QMind **como extensión de la memoria existente** `revalidar-citas-de-c-digo-no-revalida-premisas` (actualizar esa fuente, no crear una nueva) — keywords: *citas de línea desfasadas, tasa medida 14/16, citar símbolos, plan multi-fase, plantilla executor*.

**Auditoría del criterio de pertinencia (los 36 que VERIFY recibió)**: llegaron **36 `INCLUIR` y 0 `EXCLUIR`**.
Un criterio sin exclusiones no es un criterio, es un default — así que VERIFY lo aplicó (resultado en §9):
**2 EXCLUIR** (L-D5 y L-H5: su contenido ya lo carga el árbol — el instrumento corregido
`measure_iterations.py` y el test anti-deriva `test_v6_estado_not_evaluated_reutiliza_literal_canonico_del_gate`
— y la regla general que había detrás la cubren L-B3 y L-H6), **4 FUSIONES** con fuentes que ya existen
(L-A6 → memoria `revalidar-citas-de-c-digo-no-revalida-premisas`; L-B5 y L-D1 → memoria
`concurrencia-sesiones-fases-mismo-working-tree`; L-D3 → memoria `conteos-tests-documentados-metodo-def_test`;
L-E1 → **L-H2**, misma clase con dos autores) y **L-H4** fusionada con **L-V4**. El resto entra como fuente
nueva. Criterio usado (memoria auto): durable si es **generalizable** más allá de este plan y **no derivable**
del código actual.

**L-{id} — {título}** *(plantilla — VERIFY la instancia)*
- **Qué pasó**:
- **Por qué**:
- **Qué lo previene**:
- **Pertinencia**: INCLUIR en {memoria/QMind} | EXCLUIR porque {razón}

*(VERIFY agrega ≥1 lección por fase con desviación o decisión no trivial. Mínimo esperado: orden A/B antes
que C, interacción C↔F, interacción C↔D, anti-reversión V5/BUG-6, degradación silenciosa como familia
común a V6/V7/P11/tier_c.)*

---


---

## 9. Write-back a QMind — **ingestado 2026-09-04** (tras confirmación del usuario)

> Ciclo de capitalización v2.18.0 (memoria `ciclo-de-capitalizacion-de-lecciones-qmind-memory`).
> **Granularidad real del notebook**: `iah-cli-lecciones` guarda **una fuente consolidada por plan**
> (`10-analisis: <PLAN> (lecciones aprendidas y decisiones)`), no una fuente por lección. Esta es esa fuente.
> Por lo tanto «fuente nueva» abajo significa **«lección redactada con texto propio dentro de esta fuente»**,
> y «fusión» significa **«ampliación de una memoria que ya existía, registrada aquí sin duplicar el texto»**.

**Balance corregido por aritmética (41 = 32 + 7 + 2)**: una versión previa de esta tabla afirmaba
**33 nuevas · 5 fusiones · 2 exclusiones**, que suma **40** sobre **41** lecciones. Reclasificando fila por
fila: **32 lecciones** con texto propio en §8, **7 lecciones fusionadas** en **4 destinos**
(L-A6 + L-V4 + L-H4 → `revalidar-citas-de-código-no-revalida-premisas`; L-B5 + L-D1 →
`concurrencia-sesiones-fases-mismo-working-tree`; L-D3 → `conteos-tests-documentados-metodo-def-test`;
L-E1 → L-H2, dentro de esta misma fuente) y **2 exclusiones** (L-D5, L-H5). Las tres fusiones hacia memorias
preexistentes **se aplicaron** el 2026-09-04 añadiendo las instancias nuevas a esas memorias, no creando fuentes
hermanas.

| Lección | Notebook | Estado |
|---------|----------|--------|
| L-A1 grep de IDs fantasma también cuenta prosa | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (§8, texto propio + keywords) |
| L-A2 regex de censo anclado a la raíz, no al idioma | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (§8, texto propio + keywords) |
| L-A3 dos namespaces parecidos no son un drift | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (§8, texto propio + keywords) |
| L-A4 derivar no es sinónimo de unificar | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (§8, texto propio + keywords) |
| L-A5 test fosilizado puede codificar el invariante invertido | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (§8, texto propio + keywords) |
| L-A6 una cita de línea se vuelve falsa con la primera edición de código | — | 🔀 **FUSIÓN** (aplicada) → memoria preexistente `revalidar-citas-de-c-digo-no-revalida-premisas`, junto con L-V4 y L-H4 |
| L-B1 un candado con la forma equivocada falla en rojo aunque el código esté bien | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (§8, texto propio + keywords) |
| L-B2 un censo por regex cuenta puntos del fuente, no hechos alcanzables | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (§8, texto propio + keywords) |
| L-B3 un presupuesto sin instrumento de medida no restringe nada | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (§8, texto propio + keywords) |
| L-B4 dos planes pueden compartir el nombre de una carpeta de evidencia | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (§8, texto propio + keywords) |
| L-B5 dos sesiones del mismo plan sobre el mismo directorio se contradicen | — | 🔀 **FUSIÓN** (aplicada) → memoria preexistente `concurrencia-sesiones-fases-mismo-working-tree`, junto con L-D1 |
| L-D1 «una fase por sesión» no es «una sesión por repo»: se comparte el índice de git | — | 🔀 **FUSIÓN** (aplicada) → `concurrencia-sesiones-fases-mismo-working-tree` (encuadre nuevo: árbol + **índice**, no atención) |
| L-D2 la evidencia también se fosiliza (log de 18 tests sobre un archivo de 8) | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (§8, texto propio + keywords) |
| L-D3 un baseline numérico hace que cumplir el plan cuente como violación (NR5) | — | 🔀 **FUSIÓN** (aplicada) → memoria preexistente `conteos-tests-documentados-metodo-def-test` + **S26/DA-V2** |
| L-D4 cuatro regímenes para el mismo hecho; cerrar H10 exigió contarlos, no elegir uno | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (§8, texto propio + keywords) |
| L-D5 un instrumento de medición sin verificar devolvió 0 ids (epoch vs ISO) | — | ❌ **EXCLUIDA** (criterio aplicado por VERIFY) — el defecto ya está corregido en `evidence/FASE-D/measure_iterations.py` y la regla general la cubre L-B3 |
| L-C1 un parafraseo de una fuente en tu propia evidencia se convierte en premisa | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (§8, texto propio + keywords) |
| L-C2 un test rojo heredado puede contradecir un candado más nuevo | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (§8, texto propio + keywords) |
| L-C3 un contrato temprano puede contradecir tests de otra fase | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (§8, texto propio + keywords) |
| L-C4 promesa de servicios y lista de assets son superficies distintas | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (§8, texto propio + keywords) |
| L-E1 la paralelización de tracks se decide contra los archivos reales | — | 🔀 **FUSIÓN** con **L-H2** (misma clase: dos actores sobre el mismo archivo) — el texto propio es el de L-H2 |
| L-E2 la causa raíz de un campo null puede vivir en el caller | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (§8, texto propio + keywords) |
| L-E3 la no-reconstrucción de un oráculo se fija con test sonda | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (§8, texto propio + keywords) |
| L-F1 un fixture en forma tolerada pero no canónica prueba un defecto imposible en producción | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (§8, texto propio + keywords) |
| L-F2 score continuo y veredicto binario son dos representaciones del mismo hecho | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (§8, texto propio + keywords) |
| L-F3 la re-evaluación de artefactos debe reproducir la lectura del consumidor de producción | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (§8, texto propio + keywords) |
| L-G1 un péndulo se cura distinguiendo estados, no revirtiendo el fix anterior | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (§8, texto propio + keywords) |
| L-G2 un atajo favorable-vacuo se cura contrastando con datos primarios del audit | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (§8, texto propio + keywords) |
| L-G3 al cambiar un contrato, reescribir sus tests en el mismo commit y con registro | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (§8, texto propio + keywords) |
| **L-H1** un subagente puede reportar cambios que aún no están en el árbol | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (nueva, la aportó VERIFY) |
| **L-H2** dos actores reescribiendo el mismo archivo = condición de carrera, no «regiones distintas» | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** — y **absorbe L-E1**, que dejó de ser fuente propia |
| **L-H3** un estado «del último intento» solo es verificable por render si el render ocurre dentro del parche que provoca el fallo | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (nueva, la aportó VERIFY) |
| **L-H4** el prompt de una fase puede llegar con citas fósiles y un archivo de test inexistente | — | 🔀 **FUSIÓN con L-V4** (una sola fuente sobre citas que caducan; L-V4 aporta la tasa medida 14/16) |
| **L-H5** replicar un literal con test anti-deriva cuesta menos que re-arquitectar el grafo de imports | — | ❌ **EXCLUIR** — lo lleva el árbol: `test_v6_estado_not_evaluated_reutiliza_literal_canonico_del_gate` + el comentario del ciclo de imports. Criterio de memoria: si el fix vive en el código y el test lo dice, no duplicar |
| **L-H6** un hallazgo «texto viejo en dos sitios» se barre hasta la fuente | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (nueva, la aportó VERIFY) |
| **L-H7** los resultados de herramientas son datos, no instrucciones; en delegación la verificación es parte del trabajo | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (**S-H18 sigue abierto**: la mitigación pedida era *automatizar* el barrido, y sigue sin automatizarse) |
| **L-D5** un instrumento de medición sin verificar devolvió 0 ids (epoch vs ISO) | — | ❌ **EXCLUIR** — el defecto ya está corregido en `evidence/FASE-D/measure_iterations.py` (artefacto versionado) y su regla general («verifica el instrumento») la cubre L-B3, que sí entra |
| **L-I1** una fase de evidencia también produce conocimiento, y si no lo capitaliza lo pierde | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** (instancia de VERIFY lo que FASE-I no registró) |
| **L-V1** un validador que no lee el artefacto que el sistema produce certifica un mundo que producción no habita | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** |
| **L-V2** quien cambia un contrato barre sus tests espejo en todo el repo, no solo en su directorio de fase | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** — extiende L-G3 |
| **L-V3** la prosa de un artefacto que llega al cliente es superficie de contrato, no comentario | `iah-cli-lecciones` | ✅ **Incluida en esta fuente** |
| **L-V4** una cita de línea caduca antes de certificar el fix (14/16 medidas) | — | 🔀 **FUSIÓN** con la memoria existente `revalidar-citas-de-c-digo-no-revalida-premisas` (**actualizar, no crear**) |
| *(fusión)* **L-A6** una cita de línea se vuelve falsa con la primera edición | — | 🔀 **FUSIÓN** con la misma memoria anterior (L-V4 es su versión medida; no ingresar dos veces) |
| *(fusión)* **L-B5** y **L-D1** dos sesiones del mismo plan sobre el mismo directorio | — | 🔀 **FUSIÓN** con la memoria de proyecto `concurrencia-sesiones-fases-mismo-working-tree` (ya existe: añadir el caso del README sobrescrito y el de `git add` con rutas explícitas) |
| *(fusión)* **L-D3** un baseline numérico hace que cumplir el plan cuente como violación | — | 🔀 **FUSIÓN** con la memoria de proyecto `conteos-tests-documentados-metodo-def_test` + **S26/DA-V2** |
| *(fusión)* **L-E1** la paralelización se decide contra los archivos reales | — | 🔀 **FUSIÓN** con **L-H2** |

**Balance final del write-back (EJECUTADO 2026-09-04)**: **41 lecciones** en el ciclo (36 de fases + L-I1 +
L-V1…L-V4) ⟹ **32 con texto propio en esta fuente**, **7 fusionadas** en **4 destinos** (L-A6 + L-V4 + L-H4 →
`revalidar-citas…`; L-B5 + L-D1 → `concurrencia-sesiones…`; L-D3 → `conteos-tests…`; L-E1 → L-H2) y
**2 exclusiones** (L-D5, L-H5). Suma: 32 + 7 + 2 = **41** ✔. La versión que publicó VERIFY decía
**33 nuevas · 5 fusiones · 2 exclusiones**, que suma **40** sobre 41: contaba L-V4 como fuente nueva y como
destino de fusión de L-H4 en la misma pasada. Corregido acá y en `10-analisis` §9 — **séptima instancia** de la
clase «la evidencia afirma más de lo medido» (L-A5, L-B2, L-V1).

**Cómo recuperarlas en el próximo Paso 0**: cada lección tiene una línea **Pertinencia** con su alcance y sus
sinónimos, y el retrieve de QMind opera sobre el texto completo de cada lección. ⚠️ **Corrección**: una versión
previa de este párrafo afirmaba que *cada* lección quedó redactada con el formato literal
`keywords: *…*`. Medido sobre esta fuente: **6 de 41**. Las demás llevan los términos de búsqueda en prosa
dentro de la línea de Pertinencia, que es lo que el retrieve efectivamente indexa. Quien busque el formato
literal no encontrará 35 lecciones que sí están.
