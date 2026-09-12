# 01 — Plan Maestro: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11

> **Origen**: síntesis de FASE-VERIFY del plan TRIBUNAL-OFFLINE-2026-09-09 (certificación 2026-09-11, commit `e6161a3`). Este documento desarrolla lo que sus lecciones y seguimientos apuntan pero no cierran: L-E2E.1 (timing), L-E2E.3 (advisory de facto), AC8 ❌ (D-V.4), D-V.1, D-V.3.
> **Precondición global**: ✅ cumplida el 2026-09-11 — FASE-RELEASE-4.76.0 del predecesor cerró en `bd2bf57` (v4.76.0 publicada **localmente, sin push ni tag**; plan archivado por R2.5; `--quick` 8/8).
> **Arrastre del predecesor para P1**: a los residuos técnicos de este plan se suman **9 ítems de deuda** (ver §Deuda de proceso de `06-checklist-implementacion.md`): 6 de gates medidos en el R2.5 del predecesor (verificador de R2.6/R2.7, cobertura 12,5 % de `validate_plan_closure.py`, campo `Version actual` del REGISTRY, reescrito ciego de `validate_opencode_refs.py --fix`, punto ciego de `version_consistency_checker.py`, y L-R.1 — ya aplicada a este plan) + 3 añadidos por el Paso 0 horizontal de 2026-09-12 (§9: Paso 0 sin verificador, normalización del flaky de orden en R2.7, y Tier A inalcanzable en `v4complete`).

---

## 1. Secuencia y presupuesto

| Fase | Depende de | Presupuesto (iter) | delegate_task | Código |
|------|-----------|--------------------|---------------|--------|
| FASE-P1 | RELEASE-4.76.0 ✅ | 30 | No | No (decisión) |
| FASE-P2 | P1 (Q1=sí + opción elegida) | 55 | No | Sí |
| FASE-P3 | P1 (Q2b, Q5) | 30 | No | Sí |
| FASE-P4 | P1 (Q3/Q4/Q5) + P3 recomendado + **T3a datos operativos + T3b analítica** | 40 | Sí (corrida) | No |
| FASE-RELEASE-4.77.0 | P2/P3 (si aplican) + P4 | 30 | Sí | Docs |

Presupuesto medido con `evidence/FASE-D/measure_iterations.py` (R2.1); corte en commit.

> ⚠️ **Revisión 2026-09-12**: P4 no puede alcanzar Tier A con el cableado actual (ver §2.1). Si Q5 = (a) propagar banderas, el cambio toca `main.py` y **debe entrar en el presupuesto de P3**, que hoy no lo contempla.

---

## 2. El nudo técnico (estado certificado en FASE-VERIFY)

```
main.py (v4complete)
├── FASE 4.5–5: publication gates + delivery_quality_report
├── Juez: TribunalJudge(v4_audit_dir, deliveries_dir)      ← ANTES del packaging
│        └─ acta = judge.evaluate()
│             └─ blocks_delivery_zip(acta) → condición ZIP-skip (única ruta del tribunal)
├── FASE 6: packager.package()                             ← single-write ZIP-only
│        └─ zf.writestr: MANIFEST.json, IMPLEMENTATION_ORDER.md, ASSETS/ — solo existen DESPUÉS
└── FASE 7: los 4 revisores (post-packaging, never-block por Bot, LLMPromiseExtractor compartido)
         └─ revision_diagnostico / assets / alineacion / honestidad .json  ← llegan TARDE para el Juez
```

**Consecuencia certificada**: `reviewer_reports` en el acta queda `[]`; en la corrida real Bot 1 recomendó BLOQUEAR y Bot 4 DEVOLVER-PRUEBAS y el ZIP se emitió igual (veredicto `APROBADO-CONDICIONAL-PENDING-ONBOARDING`, gates-only).

**Catch-22**: los revisores con hallazgos más bloqueantes (Bot 3 completitud de assets, Bot 4 honestidad) leen artefactos que solo existen tras `packager.package()`; la decisión del ZIP es anterior al packaging.

**El gap importa más en Tier A**: con B/C el primer piso acota el veredicto a condicional. Con dato real (Tier A) `APROBADO-PARA-ENTREGA` es alcanzable — y hoy ese veredicto ignoraría las objeciones de los revisores.

### 2.1 El Tier A es inalcanzable en `v4complete` con el cableado actual (medido 2026-09-12, no certificado por VERIFY)

Cadena leída en tres símbolos, en orden inverso al veredicto:

1. `_compute_verdict` (`judge.py`): `APROBADO-PARA-ENTREGA` exige `evidence_tier == "A"` **y** todas las `T1_CERTIFIABLE_CLAUSES` en `PASS`.
2. `_determine_evidence_tier` (`scenario_calculator.py`): devuelve `A` solo si `ga4_enabled and gsc_enabled and has_verified_data`; con dato verificado y sin analítica devuelve `B_PLUS`.
3. `main.py`, bloque FASE-K: construye `HotelFinancialData(..., ga4_enabled=False, gsc_enabled=False)` **fijos**, mientras la disponibilidad real se calcula más adelante en el mismo modo (`ga4_client.is_available()` → `analytics_data["use_ga4"]`).

**Consecuencias para este plan**:
- **(a)** La precondición T3 de P4 está incompleta tal como está redactada: `rooms`/`occupancy_rate`/`direct_channel_percentage`/`ADR` con fuente no bastan. Falta **T3b** (GA4 **y** GSC conectados) y el cableado de banderas (decisión Q5).
- **(b)** El argumento de secuenciación ("decidir E antes de correr O porque Tier A es el único régimen con dientes") **se sostiene** — solo Tier A puede decir "entrega" — pero se vuelve **inobservable** dentro de este plan si Q5 se difiere: P4 no podría mostrar el caso que motiva la decisión.
- **(c)** Efecto colateral útil: el `first_floor_rule` no cubre `B_PLUS` (`FIRST_FLOOR_TIERS = {B, C}`), así que un acta en `B_PLUS` declara "sin restricción de primer piso" mientras el veredicto sale condicional por el guard de Tier A. Es un defecto de fidelidad de la familia de AC-F2 → **FASE-P3**.

> ⚠️ Esto es una lectura de código de la concepción del plan, **no** un AC certificado. Tarea 1 de P1 debe re-verificar los tres símbolos antes de decidir Q5 (L-V.2: VERIFY/P1 re-lee artefactos, no hereda conclusiones).

---

## 3. Opciones de refactor (a decidir en FASE-P1, Q2)

| Opción | Idea | Pros | Contras | Blast radius |
|--------|------|------|---------|--------------|
| **O1 — metadata pre-ZIP** | Serializar MANIFEST/ASSETS-metadata **antes** de escribir el ZIP; revisores corren pre-decisión; el ZIP se escribe al final | Un solo pase; los revisores siguen leyendo archivos reales (contrato intacto) | Serialización duplicada; riesgo de drift entre staging y ZIP final | `main.py`, `delivery_packager.py` |
| **O2 — estado en memoria** | Los revisores consumen objetos runtime pre-packaging | Sin archivos staging | Rompe el contrato "leen artefactos del disco"; acopla revisores a objetos runtime; tests más frágiles | revisores + `main.py` |
| **O3 — dos pasadas** | `package()` → staging; revisores leen staging; decisión final ship/suppress | El más limpio y auditable; el ZIP final solo nace si pasa | Cambia el contrato de `delivery_packager.py`; mayor superficie de cambio | `delivery_packager.py`, `main.py` |
| **O4 — sin refactor** | Mantener auditoría-only; decisión de producto explícita y documentada | Cero riesgo técnico | El gap advisory persiste; Tier A diría "entrega" ignorando objeciones | ninguno |

**Restricción transversal (NR3)**: O1/O2/O3 deben integrar el enforcement en la ruta existente — la decisión final sigue pasando por `blocks_delivery_zip()`/ZIP-skip. Nunca una cuarta ruta de bloqueo.

**Hueco común a las cuatro opciones (lección cruzada L-SR5 / L-PF3)**: ninguna define qué pasa **aguas abajo** del bloqueo. `L-PF3` ya validó la cura en este repo para un gate de contenido: regenerar con el `suggestion` del detector como restricción, **un** reintento con guard anti-bucle, y si persiste, escalar a bloqueo real con DTO tipado (no parseando JSON). El contrato de P1 debe fijar las dos mitades — *decisión* (matriz recomendación→veredicto) **y** *consecuencia* (qué recibe el operador cuando el veredicto es `DEVOLVER-CORRECCIONES` o `BLOQUEADO`: ¿se re-genera?, ¿se entrega diagnóstico sin ZIP?, ¿se aborta en seco?). Sin la segunda mitad, el enforcement propuesto replica el defecto que denuncia: un veredicto que bloquea y deja al cliente sin paquete y al operador sin ciclo de reparación.

**Precedente aprovechable**: `_extract_evidence_tier` de `honesty_reviewer.py` ya lee `financial_scenarios.breakdown.evidence_tier` — la fuente de tier pre-packaging existe para el fix de fidelidad (P3) y como entrada del Juez si se elige reordenarlo.

---

## 4. Fases (detalle)

### FASE-P1 — Decisión y contrato (MEDIA · DIRECTO · sin código)
- **Tarea 1 — Research (solo lectura)**: confirmar el mapa con símbolos: `TribunalJudge.evaluate` / `_compute_verdict` (`judge.py`), `blocks_delivery_zip` + condición ZIP-skip (`main.py`), bloque FASE 7 de revisores (`main.py`) y **el punto exacto donde `reviewer_reports` se inicializa y jamás se puebla**, `package()` (`delivery_packager.py`), `_resolve_delivery_dir` / `_is_template_stub` (`asset_reviewer.py`), `_extract_evidence_tier` (`honesty_reviewer.py`). **Nuevo (§2.1)**: re-verificar `_compute_verdict` (guard `evidence_tier == "A"`), `_determine_evidence_tier` (`scenario_calculator.py`) y la construcción de `HotelFinancialData` en el bloque FASE-K de `main.py` antes de decidir Q5. Verificar si D-V.3 (endurecimiento del executor) ya se ejecutó en RELEASE-4.76.0 — **resuelto: sí**, executor v2.21.0 con R2.6 y R2.7; lo abierto es su verificador mecánico y que el baseline que exige R2.6 vive bajo `output/`, excluido por `.gitignore`. Entregable: `evidence/FASE-P1/research-estado.md`.
- **Tarea 2 — Decisión con el usuario (una tanda de preguntas)**: Q1–Q6 (ver prompt de inicio). **Q1b** (consecuencia del bloqueo) y **Q5** (cableado de banderas de analítica) **no son opcionales**: sin Q1b el contrato queda incompleto (§3) y sin Q5 la fase P4 no puede especificarse (§2.1). **Q6** fija el esquema de tri-estado que NR8 exige.
- **Tarea 3 — Contrato + ACs finales**: `evidence/FASE-P1/decision-enforcement.md` con: decisión, opción elegida, matriz recomendación→veredicto propuesta (hereda la de T1: finding CRITICAL o veredicto BLOQUEAR de revisor → DEVOLVER-CORRECCIONES/BLOQUEADO; WARNING no degrada bajo el primer piso; never-block preservado), **comportamiento aguas abajo del bloqueo** (ciclar/escalar/entregar-parcial, según §3), **tri-estado de `reviewer_reports`** (NR8: sin hallazgos / artefacto ausente / lector fallido, con las claves del acta que lo expresan), y ACs finales con artefacto+clave (R2.4) **cada uno con su verificación por mutation check cuando sea de detección o bloqueo** (NR7).
- **Regla heredada (§15.4.1)**: el contrato fijado aquí obliga a P2/P3; cambios posteriores requieren decisión registrada.

### FASE-P2 — Refactor de ordenamiento (ALTA · solo si Q1=sí y opción ≠ O4)
- Implementar O1/O2/O3 manteniendo never-block, NR2 y NR3.
- Tests obligatorios: camino de bloqueo ejercitado (recomendación BLOQUEAR de un revisor → ZIP no emitido), camino aprobado, never-block (fallo de un revisor no rompe la corrida), retro sobre `output/` vivo y sobre la corrida E2E del predecesor (`evidence/FASE-E2E/`).
- **NR7 (mutation check)**: para AC-E2, desactivar el consumo de `reviewer_reports` en `_compute_verdict` y confirmar que el test de bloqueo se pone rojo; un test que emite el acta a mano y pasa con el guard quitado no certifica el enforcement (precedente: L-T4A.5, L-T2C.4).
- **NR8**: el tri-estado exige un test nombrado por su causa — `los 4 revisores fallan` ≠ `los 4 revisores no hallan nada` ≠ `los revisores no corrieron`. Prohibido cerrar el AC con un fixture que solo pueda producir uno de los tres estados (L-PF10).
- **Baseline NR1**: snapshot `pre` tomado con `--ignore` del archivo de tests de la fase (L-T4B.5) y verificación por resta R2.7 (`suma_post − suma_pre == tests_nuevos`; diferencia 0 = baseline contaminado).
- Si Q1=no (O4): la fase se sustituye por documentación de la decisión y se cierra sin código.

### FASE-P3 — Fixes localizados (MEDIA)
- **AC8**: opción a fijar en P1 (Q2b) — (a) `_resolve_delivery_dir()` lee `IMPLEMENTATION_ORDER.md` del ZIP vía `zipfile`, o (b) recalibrar `_is_template_stub()` (excluir `---` y boilerplate Fecha/Score/footer del conteo). **Cierre con mutation check (NR7)**: con el fixture del caso real, desactivar el fix y ver el test en rojo — AC8 ya falló por heurístico que "pasaba" sobre un layout que no existía (L-V.1).
- **Tier del acta**: el Juez lee el tier de una fuente disponible pre-packaging (`financial_scenarios.breakdown.evidence_tier`) o se reordena — converger con P2 si hay reordenamiento.
- **AC-F4 · Fidelidad del primer piso en `B_PLUS`**: `FIRST_FLOOR_TIERS` = {`B`,`C`} deja pasar `B_PLUS`, así que el acta afirma "sin restricción de primer piso" en un caso que sale condicional por el guard de Tier A. El `reason` debe decir por qué el veredicto es el que es (o `FIRST_FLOOR_TIERS` debe cubrir todo lo que no sea `A` — decidir en P1 y fijar en el contrato, no improvisar aquí).
- **AC-F5 · Banderas de analítica (solo si Q5=(a))**: propagar la disponibilidad real (`ga4_available`, `gsc_available`) al `HotelFinancialData` del bloque FASE-K, lo que exige **hoist** de esas variables por encima del bloque. L-T2C.2 es la advertencia directa: un hoist en `main.py` con un `except Exception` ancho alrededor puede enmascarar un `NameError` y cambiar el tier de corridas reales. Test obligatorio: `tier` con analítica disponible y sin ella, más delta NR1 con par pre/post.
- **Whitelist barreda (D-V.1)**: test-only — autorizar a Bot 3 como emisor legítimo de `asset_path` en `test_barreda_un_solo_emisor_de_la_clave`.
- **Versión del acta**: `acta_writer.py` lee de `VERSION.yaml` (fuente única).

### FASE-P4 — Corrida de observación (MEDIA · MIXTO)
- **Precondición T3a (datos operativos)**: hotel propio — `rooms`, `occupancy_rate`, `direct_channel_percentage`, `ADR` con fuente declarada. Sin esto el tier queda en `B`/`C` y no se levanta el primer piso.
- **Precondición T3b (analítica) — nueva, medido 2026-09-12**: `evidence_tier: A` exige además GA4 **y** GSC disponibles **y** que el bloque FASE-K propague las banderas (Q5, §2.1). Si Q5=(b), **el techo de esta fase es `B_PLUS` y el `APROBADO-PARA-ENTREGA` no es observable**: el informe debe declararlo como límite, no como corrida fallida.
- **Antes de redactar el brief delegado (L-VUP-9)**: verificar `--help` de `onboard` y `v4complete` y usar solo argumentos reales; un prompt con un argumento inexistente produce un FAIL que no evalúa ningún AC.
- **Antes de la corrida (L-VUP-13)**: `ls output/clientes/` y el log de onboarding. Si el hotel no está poblado, el pipeline cae a defaults y el tier/pricing cambian: la condición de equivalencia se declara en el informe, no se infiere.
- **Orden del paso (L-VUP-12)**: (1) corrida delegada, (2) **copia de evidencia antes de analizar**, (3) comparación con script versionado en la propia carpeta de evidencia, (4) análisis.
- **Delta (R2.3) con diff estructural, no visual (L-VUP-14)**: parsear los JSON del predecesor (`evidence/FASE-E2E/`) y comparar por clave numerada; probar el parseo contra el baseline **antes** de lanzar la corrida costosa.
- **Encuadre**: corrida de observación/diagnóstico, NO entrega a cliente. `APROBADO-PARA-ENTREGA` = provisional si el enforcement no está cerrado.
- Entregable: `evidence/FASE-P4/informe-observacion.md` (checklist §5) + delta vs corrida E2E del predecesor (R2.3).

### FASE-RELEASE-4.77.0 (BAJA · DELEGABLE)
- Flujo documental estándar: `log_phase_completion.py --release`, `sync_versions.py`, CHANGELOG, GUIA_TECNICA, doctor, R2.5 archivado de este plan.

---

## 5. Checklist de observación (P4) — qué mirar en la corrida real

1. `evidence_tier` resultante con dato real (¿A?) y `first_floor_rule` levantado.
2. Veredicto: ¿alcanza `APROBADO-PARA-ENTREGA`? (provisional si E no cerrado).
3. Comportamiento de Bots 1–4 con dato rico: nuevos findings, falsos positivos/negativos.
4. Fidelidad del acta: `evidence_tier` del acta vs MANIFEST (post-P3 debe coincidir).
5. Gap advisory: recomendaciones de revisores vs veredicto (si P2 cerró enforcement, ya no debe existir).
6. AC17/AC19 del predecesor con cifras reales: `precision_tier`, `can_show_exact_money`, bases de pérdida (`expected_loss_cop` vs fuga mensual).
7. Delta vs corrida E2E del predecesor (R2.3: par pre/post).
8. **Estado real de `reviewer_reports` (NR8)**: cuántos revisores corrieron, cuántos fallaron y fueron tragados por el never-block, y cuáles produjeron cero hallazgos. Si el acta no permite distinguir los tres, AC-E0 no está cerrado aunque el veredicto se vea razonable.
9. **Techo de tier de la corrida**: `ga4_available`/`gsc_available` efectivos y el `evidence_tier` resultante. Si la corrida quedó en `B_PLUS`, el informe lo declara como límite de la fase (no como hotel con datos malos).

---

## 6. ACs borrador (fijar definitivos en P1)

| AC | Fase | Enunciado borrador | Artefacto + clave (R2.4) |
|----|------|--------------------|--------------------------|
| AC-D1 | P1 | `decision-enforcement.md` fija la matriz recomendación→veredicto **y** la consecuencia aguas abajo del bloqueo (ciclar/escalar/entregar-parcial) | `evidence/FASE-P1/decision-enforcement.md` → secciones "Matriz" y "Consecuencia del bloqueo" |
| AC-E0 | P1→P2 | El acta distingue los tres estados de un revisor: sin hallazgos / artefacto ausente / lector fallido | `acta_revision.json` → claves fijadas por el contrato de P1 (NR8) |
| AC-E1 | P2 | El acta refleja `reviewer_reports` (no vacío cuando los 4 revisores corrieron) | `acta_revision.json` → `reviewer_reports` |
| AC-E2 | P2 | Recomendación BLOQUEAR de un revisor → ZIP no emitido (una sola ruta) | `main.py` (grep) + corrida/test |
| AC-E3 | P2 | Never-block: fallo de un revisor no rompe la corrida | test output |
| AC-F1 | P3 | `EMPTY_DELIVERY_TEMPLATE` dispara en régimen ZIP-only real | `revision_assets.json` → `finding_type` |
| AC-F2 | P3 | `evidence_tier` del acta == MANIFEST en corrida real | `acta_revision.json` vs `MANIFEST.json` |
| AC-F3 | P3 | Barreda `asset_path` verde (whitelist test-only) | test output |
| AC-F4 | P3 | En `B_PLUS` el `reason` del primer piso describe por qué el veredicto es condicional | `acta_revision.json` → `first_floor_rule.reason` |
| AC-F5 | P3 (solo Q5=a) | Con GA4+GSC disponibles el pipeline produce `evidence_tier: A` (hoy imposible: banderas fijas en `False`) | `financial_scenarios_*.json` → `breakdown.evidence_tier` |
| AC-O0 | P4 | El informe declara el techo de tier de la corrida y las banderas efectivas | `evidence/FASE-P4/informe-observacion.md` → §Techo de tier |
| AC-O1 | P4 | Corrida Tier A real produce acta + veredicto (provisionalidad registrada) | `acta_revision.json` → `verdict` + `evidence_tier` |
| AC-O2 | P4 | Informe de observación con los 9 puntos de §5 | `evidence/FASE-P4/informe-observacion.md` |
| AC-V1 | RELEASE | Certificación formal de todos los ACs contra artefacto real (patrón VERIFY) | matriz en `10-analisis` |

> **Verificación NR7 (mutación)**: los AC de detección o bloqueo (AC-E2, AC-F1, AC-F3, AC-F5) no se cierran solo con el test verde — la evidencia guarda el **par de salidas**: test con el guard/detección activo (verde) y con él desactivado (rojo). Sin el segundo lado, el AC queda ⚠️ y no ✅ (R2.4 + L-VUP-5).

---

## 7. No-Regresiones (NR)

| NR | Regla | Verificación |
|----|-------|--------------|
| NR1 | Sin regresión: `passed_post = passed_pre + tests nuevos` (par pre/post con instrumento) | medición pre/post por fase |
| NR2 | El tribunal no reimplementa gates (verificar sí, recalcular no) | grep `import.*publication_gates` en `tribunal/*.py` = 0 |
| NR3 | Una sola ruta de bloqueo (no cuarta) | grep en `main.py` + decisión documentada |
| NR4 | Coherence ≥ 0.80 en toda corrida nueva | `coherence_score_final` del reporte |
| NR5 | El LLM extrae, el Juez decide (veredicto determinista) | tests del contrato (precedente: `test_no_rejulga_un_gate_que_paso`) |
| NR6 | Resolución de artefactos por fecha embebida, no `mtime` (si se toca el resolutor) | tests del resolutor |
| NR7 | Todo AC de detección o de bloqueo se cierra con **mutation check**: desactivar la detección/guard y ver el test en rojo (origen: L-T4A.5, L-T2C.4, L-VUP-5) — **ascendida a regla global §R2.8 del executor v2.23.0** | par de salidas en la evidencia de la fase (verde/rojo); verificador mecánico **aún no existe** → §Deuda de `06-checklist-implementacion.md` |
| NR8 | Un lector de artefactos expresa los tres estados — sin hallazgos / artefacto ausente / lector fallido — y ningún camino los colapsa (origen: L-PF6, L-PF10) — **ascendida a regla global §R2.9 del executor v2.23.0** | tests nombrados por causa, uno por estado; verificador mecánico **aún no existe** → mismo tramo de deuda |

> **Trazabilidad de NR7/NR8 (2026-09-12).** Las dos subieron a global en executor v2.23.0 porque la
> medición que las fundó no es particular de este plan: **NR7 → §R2.8**, **NR8 → §R2.9**. Lo que
> sigue siendo de FASE-P1 **no es la norma sino el verificador** — ninguna de las dos nació con check
> mecánico y ambas lo declaran en su propio texto (L-R.4), en el mismo tramo de deuda que R2.6 y
> R2.7. Por tanto P1 **no** debe re-implementarlas como AC local: decide si instrumenta el check o si
> lo reasigna con dueño explícito. La regla §R2.9 ya nombra **DA-C3** (`vacío ≠ ausente`) como el
> contrato que NR8 subsume, que es lo que pedía §3.b de `00-lecciones-capitalizadas.md`.

---

## 8. Versión

Objetivo **4.77.0** (confirmar en P1). Fuente única: `VERSION.yaml`. Nunca hardcodear versiones en código — incluye `acta_writer.py` (fix P3).

---

## 9. Paso 0 horizontal — corpus cruzado del notebook `iah-cli-lecciones` (2026-09-12)

Las §1–§8 se escribieron heredando solo el `10-analisis` del predecesor. Esta sección registra la pasada por el corpus completo (46 fuentes, CLI `qmind retrieve --nb 01a04d98-…`), que es lo que el executor exige en Paso 0 y antes faltaba.

| Consulta ejecutada | Devolvió | Tocó qué punto del plan |
|--------------------|----------|-------------------------|
| "gate BLOCKING que solo loggea no previene, ciclar o escalar" | L-SR5 / L-PF3 (score 0.97) | §3 — el contrato de P1 debe incluir la consecuencia del bloqueo (AC-D1) |
| "test que pasa sin ejecutar la rama que certifica, mutation check, contrato vacuo" | ESTABILIZACION + L-T4A.5/L-T2C.4 + L-VUP-5 | NR7, y los cierres de AC-E2/AC-F1/AC-F3/AC-F5 |
| "ausencia verificada vs detección fallida en extractores de métricas" | L-PF6 / L-PF10 | NR8, AC-E0 y AC-F4 |
| "onboarding datos reales, defaults del loader, evidencia tier A" | EVIDENCE-TIER-FALSE-CONFIDENCE + ONBOARDING-INJECTION-GAP + L-VUP-13 | §2.1, Q5, precondición T3b, AC-F5 y AC-O0 |
| "baseline de tests, orden-dependencia y diff estructural E2E" | L-VUP-1 / L-VUP-14 | FASE-P2 baseline (R2.7 + `--ignore`) y FASE-P4 (diff con script versionado) |

**Lo que cambió respecto a la versión original del plan**: (i) la precondición T3 de P4 se divide en T3a/T3b y resulta insuficiente tal como estaba redactada; (ii) el contrato de P1 gana dos cláusulas que no existían (consecuencia del bloqueo, tri-estado); (iii) nacen NR7 y NR8 con ACs asignados; (iv) se detecta un residuo nuevo de fidelidad del acta (`B_PLUS` → AC-F4).

> ⚠️ **Límite declarado (L-R.4)**: el Paso 0 sigue sin verificador mecánico. Esta pasada es disciplinada por la sección que la registra, no por un check que falle si se omite. La cura candidata está en §Deuda de proceso de `06-checklist-implementacion.md`: validar que un prompt de fase cite al menos una fuente que no sea el predecesor y liste sus consultas.
