# TRIBUNAL-ENFORCEMENT-OBS-2026-09-11

> **Versión objetivo**: 4.77.0 (a confirmar en FASE-P1) · **Workflow**: `phased_project_executor.md` v2.21.0 al concebir el plan; la revisión del 2026-09-12 se hizo bajo **v2.22.0**; **la ejecución corre bajo v2.24.0** (v2.23.0 ascendió NR7/NR8 a §R2.8/§R2.9; R2.6/R2.7 siguen sin verificador mecánico)
> **Estado**: ✅ **3/6 sesiones cerradas — FASE-P1, FASE-P3-A y FASE-P3-B completadas 2026-09-14** (orden de ejecución reordenado a **P3-A → P3-B → P2 → P4 → RELEASE** por DA-P1.3; FASE-VERIFY **sin sesión**; contrato en `evidence/FASE-P1/decision-enforcement.md`: enforcement **sí**, consecuencia **escalar sin reintento**, ordenamiento **O1-cuarentena**, AC8 en **dos capas**, T3a con **el hotel** como proveedor, **Q5=a** emparejada con AC-F2, **cuatro** estados de revisor y kill switch **heredado** de `GATE_BLOCKING_ENABLED`. P3-A cerrada: AC-F1 ZIP-aware + stub estructural, AC-F2 tier desde `financial_scenarios`, AC-F4 primer piso en `B+`; R2.7 +21, 4 pares NR7. **P3-B cerrada: AC-F5 ejecutado** — `main.py` propaga las banderas reales de GA4/GSC al `HotelFinancialData` de FASE-K y el Tier A deja de ser inalcanzable por construcción (Q5=a), **AC-F3** cierra la deuda **D-V.1** con whitelist test-only justificada por §5.1 del contrato, **AC-F6** lee la versión del acta de `VERSION.yaml`; R2.7 +23 (4.130→4.153, 0 regresiones), **6 pares NR7**. Sigue **P2**) · ~~⬜ 0/6 sesiones~~ — plan esqueleto creado como handoff de FASE-VERIFY del plan TRIBUNAL-OFFLINE-2026-09-09 (certificación `e6161a3`) · **revisado 2026-09-12** tras el Paso 0 horizontal sobre el notebook `iah-cli-lecciones` (ver `01-plan-maestro.md` §9): precondición T3 desdoblada en T3a/T3b, preguntas ampliadas a Q1–Q6, nacen NR7/NR8 y AC-F4/AC-F5/AC-D1/AC-E0/AC-O0 · **ajustado 2026-09-14 (sesión de preparación, sin tocar diseño)**: Etapa 1 completada (prompts P3-A/P3-B/P4/RELEASE + `09`/`10` creados; P2 diferido a Q1 con declaración), FASE-P3 dividida para cumplir R3, decisión FASE-VERIFY registrada como condicionada, escenario de cierre sin P4 fijado, y citas corregidas (`3bdc14e`, v4.76.0 ya en origin, tag `v4.76.0` creado) — ver `dependencias-fases.md` §Estado de la Etapa 1
> **Predecesor**: TRIBUNAL-OFFLINE-2026-09-09 **cerrado 9/9** el 2026-09-11 (`3bdc14e` en `origin/master`; el hash `bd2bf57` citado en la concepción es su duplicado pre-rebase), v4.76.0 publicada y con tag `v4.76.0` (creado 2026-09-14) — certificación 15 ✅ + **AC8 ❌**, que abre este plan
> **Fuentes verticales**: `10-analisis-post-implementacion.md` del predecesor → L-E2E.1, L-E2E.3, L-V.1–L-V.4, D-V.1–D-V.4, L-R.1–L-R.4, §Seguimientos abiertos; `evidence/FASE-VERIFY/TRIBUNAL-OFFLINE-2026-09-09/MATRIZ-CERTIFICACION.md`; `05-prompt-inicio-sesion-fase-T1.md` del predecesor (matriz findings→veredicto)
> **Fuentes horizontales (Paso 0 sobre el notebook `iah-cli-lecciones`, 46 fuentes)**: L-SR5/L-PF3 (gate que solo loggea no previene), L-PF6/L-PF10 (ausencia verificada ≠ detección fallida; vacío vs ausente), L-T4A.5/L-T2C.4/L-VUP-5 (test vacuo y mutation check), L-VUP-1/L-VUP-9/L-VUP-13/L-VUP-14 (baseline por combinación, `--help` antes de delegar, defaults de onboarding, diff estructural) — ver `01-plan-maestro.md` §9 para el mapeo lección→punto del plan.
> **Canónica del Paso 0**: `00-lecciones-capitalizadas.md` (instanciado 2026-09-12) — las 8 consultas con su comando literal y resultado medido, 19 lecciones con dueño y efecto sobre este plan, 5 descartes motivados y 4 hallazgos de la capa fría **sin efecto aplicado** (§3.b: `D-T1.1`, `L-SR3`, `DA-C3`, `L-B4` + la cola de adyacentes que mide Q7). Su capa fría es `.opencode/LECCIONES-INDEX.md`.
> **Anclaje**: ROADMAP v4.2 §7.2 tramo externo (T3 onboarding con datos reales)
> ⚠️ **Convención de rutas (aclarada 2026-09-12)**: lo que `validate_opencode_refs.py --fix` reescribe a ciegas son las referencias con el nombre de **este** plan cuando se archive (R2.5) — esas se escriben como plantilla `<PLAN>`, nunca literales. Las rutas ya archivadas del predecesor (`Archives/TRIBUNAL-OFFLINE-2026-09-09/…`) son estables y **sí** se citan completas. La evidencia no se mueve con el archivado.

## Problema

v4.76.0 cierra el tramo offline del tribunal como **capa de auditoría** (Sentido A: funciona — el acta dual y los 4 reportes se producen en el pipeline real y detectaron defectos vivos: `VACUOUS_RECALL`, `CG-WHATSAPP-LEAD`). Pero **no enforcea** (Sentido B): el Juez corre **antes** del packaging y `_compute_verdict` solo consume gates; los 4 revisores corren **después** (necesitan `MANIFEST.json`/`ASSETS/`, que solo existen tras `packager.package()` — single-write ZIP-only, L-E2E.1); `reviewer_reports` queda `[]` y las recomendaciones BLOQUEAR/DEVOLVER-PRUEBAS no afectan ni veredicto ni ZIP (L-E2E.3).

Completan el cuadro:
- **AC8 ❌**: `EMPTY_DELIVERY_TEMPLATE` no detecta en régimen ZIP-only real (causa raíz en 2 capas fijada por sonda: `_resolve_delivery_dir()` cae al `.zip` + `_is_template_stub()` cuenta `---`/boilerplate como contenido).
- **Fidelidad del acta**: reporta `evidence_tier C` cuando el MANIFEST real es `B` (timing Juez/packaging, L-E2E.1). Veredicto invariante, documento menos preciso.
- **Régimen Tier A nunca ejercitado**: con dato real el primer piso se levanta y `APROBADO-PARA-ENTREGA` se vuelve alcanzable — **precisamente el régimen donde el hueco advisory tiene consecuencias** (el veredicto puede decir "entrega" sin reflejar objeciones de los revisores).
- **Y hoy el Tier A es inalcanzable por construcción, no por falta de dato** (medido 2026-09-12): `_compute_verdict` exige `evidence_tier == "A"`, `_determine_evidence_tier` devuelve `A` solo con `ga4_enabled` **y** `gsc_enabled` **y** dato verificado, y en el bloque FASE-K de `main.py` el constructor de `HotelFinancialData` fija ambas banderas en `False` mientras la disponibilidad real se calcula más abajo (`ga4_client.is_available()` → `analytics_data["use_ga4"]`). Con onboarding completo y analítica ausente el resultado es `B_PLUS`, no `A`. P4 no puede observar el régimen que justifica el plan sin un cambio de cableado que hoy no está en ninguna fase.

## Solución (dos vías, una decisión)

| Vía | Qué | Depende de |
|-----|-----|-----------|
| **E — Enforcement** | Decisión de producto (¿debe el tribunal bloquear?) + refactor del ordenamiento de delivery si la respuesta es sí (opciones O1–O3, ver plan maestro) | Solo código (P1–P2) |
| **O — Observación** | Corrida con hotel de **datos reales** (Tier A) como diagnóstico, no como entrega a cliente; `APROBADO-PARA-ENTREGA` tratado como provisional hasta cerrar E | Datos operativos reales (T3a) **+ analítica conectada GA4/GSC (T3b) + cableado de banderas en el bloque FASE-K** (decisión Q5) |

**Secuenciación recomendada**: decidir E antes de correr O **si el acta va a un cliente real** — Tier A es el único régimen donde el veredicto tiene dientes, y hoy no consume las objeciones de sus propios revisores.

## Progreso

| # | Fase | Objetivo | Complejidad | Modo | Estado |
|---|------|----------|-------------|------|--------|
| 1 | **FASE-P1** | Decisión de enforcement (**Q1=sí**, Q1b=escalar, Q2=O1-cuarentena, Q2b=ambas capas, Q3=P3→P2, Q4=el hotel, Q5=a, Q6=**4** estados, Q7=knob heredado) + contrato del veredicto enriquecido + ACs finales + FASE-VERIFY cerrado (**no activa**) + prompt de P2 creado | MEDIA | DIRECTO | ✅ **Cerrada 2026-09-14** |
| 3a | **FASE-P3-A** | Detección y fidelidad: AC-F1 (dos capas, lectura **desde el ZIP** + stub estructural), AC-F2 (fuente del tier pre-packaging), AC-F4 (primer piso en `B+`) — **primera fase de ejecución** (orden DA-P1.3) | MEDIA | DIRECTO | ✅ **Cerrada 2026-09-14** |
| 3b | **FASE-P3-B** | Cableado y test: **AC-F5 disparado** (banderas reales de analítica, toca `main.py`), AC-F3 (whitelist barreda justificada), AC-F6 (versión del acta desde `VERSION.yaml`) | MEDIA (era BAJA; Q5=a la sube) | DIRECTO | ✅ **Cerrada 2026-09-14** |
| 2 | **FASE-P2** | Enforcement: `package()` partido en write/publish (**O1-cuarentena**), `reviewer_reports` tipado y poblado, `_compute_verdict` con el cuarto argumento, AC-E0…AC-E5. **Su prompt existe**: `05-prompt-inicio-sesion-fase-P2.md`. Depende ahora de P3-A y P3-B | **ALTA** | DIRECTO | ⬜ Pendiente |
| 4 | **FASE-P4** | Corrida de observación (T3a: el hotel, por contacto del operador; techo de tier con **dueño declarado** — cableado vs analítica) + informe — **opcional**: si no hay dato con fuente, aplica "cierre válido sin P4" | MEDIA | MIXTO | ⬜ Pendiente |
| — | **FASE-VERIFY** | ❌ **No activa** (decidido en P1): el criterio §4.6-2 depende de una precondición comercial externa. El patrón VERIFY se ejecuta como **AC-V1 dentro de RELEASE**, anclado al par NR7 por fase | — | — | ❌ Cerrada sin sesión |
| 5 | **FASE-RELEASE-4.77.0** | Cierre documental + version bump + tag anotado + **AC-V1** + archivado (R2.5) | BAJA | DELEGABLE | ⬜ Pendiente |

## Alcance

**Dentro**: decisión de enforcement, refactor de ordenamiento (si procede), fixes localizados heredados, corrida de observación con datos reales, certificación formal (patrón VERIFY) y release.

**Fuera**: T5 (deploy FTP/WP + staging), T6 (throughput + gancho), corpus multi-hotel (S-V10 exige ≥3 hoteles — una corrida valida el camino Tier A, no da confianza estadística), decisión de producto sobre S-H2 (performance pain).

## Residuos heredados y su disposición

| Residuo | Disposición en este plan |
|---------|--------------------------|
| AC8 ❌ (detección de plantilla vacía rota en ZIP-only) | FASE-P3-A — opción a fijar en P1 (Q2b): leer `IMPLEMENTATION_ORDER.md` del ZIP **o** recalibrar `_is_template_stub()` |
| Acta `evidence_tier C` vs MANIFEST `B` | FASE-P3-A (leer tier de `financial_scenarios.breakdown.evidence_tier` — precedente: `_extract_evidence_tier` de `honesty_reviewer.py` ya lo hace) — converge con P2 si hay reordenamiento |
| Barreda `asset_path` (D-V.1: whitelist test-only) | **FASE-P3-B ✅ CERRADA 2026-09-14** (`bad0a5e`) — `EMISORES_LEGITIMOS`/`CONSUMIDORES_LEGITIMOS` justificados por el contrato §5.1, con la igualdad de conjuntos intacta y dos mutaciones (`NR7-AC-F3-a/b.txt`). **Medido al cerrarla**: la aserción de `consumidores` nunca se había evaluado porque la de `emisores` fallaba antes, y también estaba rota. El emisor (`asset_reviewer.py`) quedó intacto |
| Versión hardcodeada en el acta (`acta_writer.py`) | **FASE-P3-B ✅ CERRADA 2026-09-14** (`bad0a5e`, AC-F6) — `_read_project_version()` lee `VERSION.yaml` en cada escritura; si no lo encuentra publica `version-no-disponible` en vez de una versión plausible. 4 tests, uno de ellos con un YAML falso distinto (mata hardcode y caché de import) |
| Endurecimiento del executor (D-V.3) | **Ejecutado** en RELEASE-4.76.0: executor v2.21.0 con R2.6 y R2.7. Lo pendiente es la otra mitad — ninguna de las dos tiene verificador mecánico → P1 |
| Deuda de gates medida en el R2.5 del predecesor | FASE-P1 — ver §Deuda de proceso en `06-checklist-implementacion.md` (**9 ítems** desde 2026-09-12: 6 del R2.5 — verificadores R2.6/R2.7, cobertura 12,5 % de `validate_plan_closure.py`, campo `Version actual` del REGISTRY, reescrito ciego de `validate_opencode_refs.py --fix`, punto ciego de `version_consistency_checker.py` ante `FASE-RELEASE-x.y.z`, y L-R.1 ya aplicada a este plan — más 3 del Paso 0 horizontal: Paso 0 sin verificador, verificador R2.7 debe normalizar el flaky de orden, y Tier A inalcanzable en `v4complete`) |
| S-HF1, resolución por `mtime`, `FASE_D_DELIVERIES_DIR` sin usar, citas de línea en `decision-integracion.md` | Backlog — P1 decide si entran al alcance (NR6 cubre `mtime` si se toca el resolutor) |
| Banderas `ga4_enabled`/`gsc_enabled` fijas en `False` en `HotelFinancialData` del bloque FASE-K → Tier A inalcanzable en `v4complete` | **FASE-P1 (Q5) → (a) propagar · FASE-P3-B ✅ EJECUTADO 2026-09-14 (`bad0a5e`, AC-F5)** — `ga4_available`/`gsc_available` se calculan por encima del bloque FASE-K y alimentan el constructor; la regla FASE-1 queda intacta, lo que cambió es que su input dejó de mentir. **Medido**: GSC no tenía valor real que hoistear (nadie lo computaba en `v4complete`), así que hubo que calcularlo con `GoogleSearchConsoleClient().is_configured()`, y `gsc_configured` del MANIFEST se apuntó a esa misma variable para no divergir del tier. **El techo sigue sin ser solo cableado**: sobre el baseline real de FASE-I la sonda da `B` con las cuatro combinaciones de banderas, porque sus fuentes no son verificadas (`adr=regional_v410`, `canal=default`) — AC-O0 pide nombrar ese dueño |
| Semántica de `reviewer_reports`: hoy `[]` significa "nadie se los pasó al Juez"; tras el refactor puede significar "sin hallazgos" o "los 4 revisores fallaron y el never-block los tragó" | **FASE-P1** — el contrato debe exigir tres estados distinguibles en el acta (NR8); no deja en P2 una decisión no tomada |
| `first_floor_rule.reason` en `B_PLUS`: `FIRST_FLOOR_TIERS` = {`B`,`C`} → el acta declara "sin restricción de primer piso" en un caso cuyo veredicto sale condicional igual (por el guard `evidence_tier == "A"`) | **FASE-P3-A** — corrección de fidelidad del acta, misma familia que el tier (lección L-PF6/L-PF10: "vacío" ≠ "ausente") |

## Reglas transversales (heredadas del predecesor)

1. R1: una fase por sesión. Sin excepciones.
2. R2.1: presupuesto medido con instrumento (`evidence/FASE-D/measure_iterations.py`), corte en commit.
3. R2.2: sin números de línea — citar símbolos.
4. R2.3: no-regresión como delta con par pre/post.
5. R2.4: AC no legible en artefacto = ⚠️, nunca ✅.
6. R2.5: RELEASE termina archivando el plan.
7. R2.6: todo lector de artefactos del pipeline se prueba contra el baseline real (`output/FASE-D_salentoreal_post_guard/`), con `skipif` explícito y la evidencia declarando si el test corrió o se saltó.
8. R2.7: el delta NR1 se valida por resta — `suma_post − suma_pre == tests_nuevos`; diferencia 0 = baseline contaminado.
   ⚠️ R2.6 y R2.7 existen desde v2.21.0 y **ninguna tiene verificador mecánico** (deuda de P1).
9. R3: ≤4 tareas + 0 comandos largos, ó ≤3 tareas + 1 comando largo.
10. NR2: el tribunal NO reimplementa lógica de gates (verificar consistencia sí, recalcular no).
11. NR3: una sola ruta de bloqueo — el enforcement se integra en la existente (`blocks_delivery_zip` → ZIP-skip), nunca una cuarta.
12. NR5: el LLM extrae, el Juez decide (veredicto determinista).
13. R4: el Paso 0 consulta el **corpus completo** del notebook `iah-cli-lecciones` (no solo el predecesor) con 2-3 queries acotadas, y el prompt de fase registra las queries ejecutadas y las lecciones retenidas. **Sin verificador mecánico** — vale L-R.4: se publica como límite declarado (§Deuda de proceso).
14. NR7 (de L-T4A.5/L-T2C.4/L-VUP-5): todo AC de detección o de bloqueo se cierra con **mutation check** — desactivar la detección o el guard y comprobar que el test se pone rojo. Un test que no puede fallar no certifica el AC.
15. NR8 (de L-PF6/L-PF10): un lector de artefactos distingue en el artefacto **sin hallazgos / artefacto ausente / lector fallido**. Colapsar los tres estados convierte una mejora upstream en bloqueo, o un fallo de lectura en aprobación.
