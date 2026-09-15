# 01 — Plan Maestro: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11

> **Origen**: síntesis de FASE-VERIFY del plan TRIBUNAL-OFFLINE-2026-09-09 (certificación 2026-09-11, commit `e6161a3`). Este documento desarrolla lo que sus lecciones y seguimientos apuntan pero no cierran: L-E2E.1 (timing), L-E2E.3 (advisory de facto), AC8 ❌ (D-V.4), D-V.1, D-V.3.
> **Precondición global**: ✅ cumplida el 2026-09-11 — FASE-RELEASE-4.76.0 del predecesor cerró en `3bdc14e` (corregido 2026-09-14: el `bd2bf57` citado en la concepción es el duplicado pre-rebase, fuera de `origin`). v4.76.0 **está en `origin/master`** y lleva tag anotado `v4.76.0` (creado y empujado a origin el 2026-09-14); plan archivado por R2.5; `--quick` 8/8 el día del cierre (hoy son 9 checks).
> **Arrastre del predecesor para P1**: a los residuos técnicos de este plan se suman **9 ítems de deuda** (ver §Deuda de proceso de `06-checklist-implementacion.md`): 6 de gates medidos en el R2.5 del predecesor (verificador de R2.6/R2.7, cobertura 12,5 % de `validate_plan_closure.py`, campo `Version actual` del REGISTRY, reescrito ciego de `validate_opencode_refs.py --fix`, punto ciego de `version_consistency_checker.py`, y L-R.1 — ya aplicada a este plan) + 3 añadidos por el Paso 0 horizontal de 2026-09-12 (§9: Paso 0 sin verificador, normalización del flaky de orden en R2.7, y Tier A inalcanzable en `v4complete`).

---

## 1. Secuencia y presupuesto

| Fase | Depende de | Presupuesto (iter) | delegate_task | Código |
|------|-----------|--------------------|---------------|--------|
| FASE-P1 | RELEASE-4.76.0 ✅ | 30 | No | No (decisión) — **✅ cerrada 2026-09-14** |
| FASE-P3-A | P1 (Q2b=ambas capas) | 20 | No | Sí |
| FASE-P3-B | P1 (Q5=a) + P3-A | 25 | No | Sí |
| FASE-P2 | **P3-A ✅ + P3-B ✅** (orden DA-P1.3) + contrato de P1 (Q1=sí, Q2=O1-cuarentena) | 55 | No | Sí |
| FASE-P4 | P2 + T3a — cerrada 2026-09-14; T3b ausente, techo B+ declarado | 40 (histórico) | Sí (corrida) | No |
| FASE-P5 — Seguridad y privacidad | P4 cerrada; inventario y límites de autorización de §4 | Fuera de servicio (R2.1, D-PRE.1) | No | Sí, en su futura sesión |
| FASE-P6 — Generación y validación multi-hotel | Cierre técnico P5; no requiere Tier A real | Fuera de servicio (R2.1, D-PRE.1) | No | Sí, en su futura sesión |
| FASE-VERIFY | **NO activa** (cerrado en P1, §7 de `evidence/FASE-P1/decision-enforcement.md`) | — | — | — |
| FASE-RELEASE-4.77.0 | P2 + P3-A + P3-B + P4 cerradas; P5 + P6 certificadas y puerta de seguridad resuelta (§6.1) | 30 | Sí | Solo documentación |

Presupuesto medido con `evidence/FASE-D/measure_iterations.py` (R2.1); corte en commit autorizado. La división P3-A/P3-B conserva sus presupuestos históricos. Para P5/P6 se retira la métrica numérica no calibrada (R2.1, D-V2.1): no se inventa una estimación comparable; se registra medición instrumental o auto-reporte con unidad y limitación explícitas, sin declarar cumplimiento estimado. El alcance sí queda limitado: cuatro tareas y cero comandos largos por fase.

> **Orden vigente (D-PRE.1, 2026-09-15)**: **P1 → P3-A → P3-B → P2 → P4 → P5 → P6 → RELEASE**, cinco de ocho fases cerradas. El tramo completado conserva DA-P1.3; P4 no se reabre. La solicitud de actualizar el plan autoriza esta preparación documental, no la implementación ni actuaciones sobre credenciales, datos publicados o historial.

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
- **(c)** Efecto colateral útil: el `first_floor_rule` no cubre `B_PLUS` (`FIRST_FLOOR_TIERS = {B, C}`), así que un acta en `B_PLUS` declara "sin restricción de primer piso" mientras el veredicto sale condicional por el guard de Tier A. Es un defecto de fidelidad de la familia de AC-F2 → **FASE-P3-A**.

> ✅ **Confirmado en FASE-P1 (Tarea 1, 2026-09-14)** re-leyendo los tres símbolos (`_compute_verdict`,
> `_determine_evidence_tier`, y la construcción de `HotelFinancialData` en el bloque FASE-K de `main.py`),
> tal como exigía L-V.2. Detalle con símbolos en `evidence/FASE-P1/research-estado.md` §2.
> **Agravante medido, no previsto en la concepción**: en régimen ZIP-only el Juez **nunca** ve el tier
> real, porque `_read_evidence_tier` depende de un `MANIFEST.json` que el packager aún no ha escrito y su
> fallback literal es `"C"`. Por eso **Q5=(a) no es una decisión aislada sino un par**: AC-F5 (banderas
> reales) + AC-F2 (fuente del tier del acta) cierran juntos o no cierran nada — ver DA-P1.8 en
> `evidence/FASE-P1/decision-enforcement.md`.

---

## 3. Opciones de refactor — **decidido en FASE-P1: O1-cuarentena**

> **Decisión (DA-P1.4, 2026-09-14)**: **O1-cuarentena**, una variante de O1 que la medición hizo posible.
> `DeliveryPackager` ya escribe `deliveries/<hotel_id>_<fecha>.zip.tmp` y lo renombra de forma atómica, y
> `_create_zip_single_write` recibe `manifest_bytes`/`implementation_order_bytes` **ya finalizados**. La
> decisión se mueve entonces del *write* al **publish**: escribir el `.tmp` → los 4 revisores leen **ese ZIP
> real** → el Juez decide sobre sus hallazgos → el rename publica o el `unlink` suprime.
> Single-write ZIP-only intacto, sin serialización duplicada y sin staging que el cliente no ve.
> **Descartadas**: O1-staging de metadatos (crea un layout fantasma y obligaría a que AC-F1 lea staging, no ZIP),
> O2-estado en memoria (rompe el contrato de que los revisores leen artefactos y fragiliza sus tests),
> O3-dos pasadas (abandona el single-write ZIP-only, que este plan declaró inmutable), O4 (ver DA-P1.1).
> Coste honesto: `package()` deja de ser un método de un solo paso; partirlo en write/publish es el blast
> radius real de la opción y va en el presupuesto de P2.

| Opción | Idea | Pros | Contras | Blast radius |
|--------|------|------|---------|--------------|
| **O1 — metadata pre-ZIP** | Serializar MANIFEST/ASSETS-metadata **antes** de escribir el ZIP; revisores corren pre-decisión; el ZIP se escribe al final | Un solo pase; los revisores siguen leyendo archivos reales (contrato intacto) | Serialización duplicada; riesgo de drift entre staging y ZIP final | `main.py`, `delivery_packager.py` |
| **O2 — estado en memoria** | Los revisores consumen objetos runtime pre-packaging | Sin archivos staging | Rompe el contrato "leen artefactos del disco"; acopla revisores a objetos runtime; tests más frágiles | revisores + `main.py` |
| **O3 — dos pasadas** | `package()` → staging; revisores leen staging; decisión final ship/suppress | El más limpio y auditable; el ZIP final solo nace si pasa | Cambia el contrato de `delivery_packager.py`; mayor superficie de cambio | `delivery_packager.py`, `main.py` |
| **O4 — sin refactor** | Mantener auditoría-only; decisión de producto explícita y documentada | Cero riesgo técnico | El gap advisory persiste; Tier A diría "entrega" ignorando objeciones | ninguno |

**Restricción transversal (NR3)**: O1/O2/O3 deben integrar el enforcement en la ruta existente — la decisión final sigue pasando por `blocks_delivery_zip()`/ZIP-skip. Nunca una cuarta ruta de bloqueo.

**Hueco común a las cuatro opciones (lección cruzada L-SR5 / L-PF3)**: ninguna define qué pasa **aguas abajo** del bloqueo. `L-PF3` ya validó la cura en este repo para un gate de contenido: regenerar con el `suggestion` del detector como restricción, **un** reintento con guard anti-bucle, y si persiste, escalar a bloqueo real con DTO tipado (no parseando JSON). El contrato de P1 debe fijar las dos mitades — *decisión* (matriz recomendación→veredicto) **y** *consecuencia* (qué recibe el operador cuando el veredicto es `DEVOLVER-CORRECCIONES` o `BLOQUEADO`: ¿se re-genera?, ¿se entrega diagnóstico sin ZIP?, ¿se aborta en seco?). Sin la segunda mitad, el enforcement propuesto replica el defecto que denuncia: un veredicto que bloquea y deja al cliente sin paquete y al operador sin ciclo de reparación.

**Precedente aprovechable**: `_extract_evidence_tier` de `honesty_reviewer.py` ya lee `financial_scenarios.breakdown.evidence_tier` — la fuente de tier pre-packaging existe para el fix de fidelidad (P3-A) y como entrada del Juez si se elige reordenarlo.

---

## 4. Fases (detalle)

### FASE-P1 — Decisión y contrato (MEDIA · DIRECTO · sin código)
- **Tarea 1 — Research (solo lectura)**: confirmar el mapa con símbolos: `TribunalJudge.evaluate` / `_compute_verdict` (`judge.py`), `blocks_delivery_zip` + condición ZIP-skip (`main.py`), bloque FASE 7 de revisores (`main.py`) y **el punto exacto donde `reviewer_reports` se inicializa y jamás se puebla**, `package()` (`delivery_packager.py`), `_resolve_delivery_dir` / `_is_template_stub` (`asset_reviewer.py`), `_extract_evidence_tier` (`honesty_reviewer.py`). **Nuevo (§2.1)**: re-verificar `_compute_verdict` (guard `evidence_tier == "A"`), `_determine_evidence_tier` (`scenario_calculator.py`) y la construcción de `HotelFinancialData` en el bloque FASE-K de `main.py` antes de decidir Q5. Verificar si D-V.3 (endurecimiento del executor) ya se ejecutó en RELEASE-4.76.0 — **resuelto: sí**, executor v2.21.0 con R2.6 y R2.7; lo abierto es su verificador mecánico y que el baseline que exige R2.6 vive bajo `output/`, excluido por `.gitignore`. Entregable: `evidence/FASE-P1/research-estado.md`.
- **Tarea 2 — Decisión con el usuario (una tanda de preguntas)**: Q1–Q6 (ver prompt de inicio). **Q1b** (consecuencia del bloqueo) y **Q5** (cableado de banderas de analítica) **no son opcionales**: sin Q1b el contrato queda incompleto (§3) y sin Q5 la fase P4 no puede especificarse (§2.1). **Q6** fija el esquema de tri-estado que NR8 exige.
- **Tarea 3 — Contrato + ACs finales**: `evidence/FASE-P1/decision-enforcement.md` con: decisión, opción elegida, matriz recomendación→veredicto propuesta (hereda la de T1: finding CRITICAL o veredicto BLOQUEAR de revisor → DEVOLVER-CORRECCIONES/BLOQUEADO; WARNING no degrada bajo el primer piso; never-block preservado), **comportamiento aguas abajo del bloqueo** (ciclar/escalar/entregar-parcial, según §3), **tri-estado de `reviewer_reports`** (NR8: sin hallazgos / artefacto ausente / lector fallido, con las claves del acta que lo expresan), y ACs finales con artefacto+clave (R2.4) **cada uno con su verificación por mutation check cuando sea de detección o bloqueo** (NR7).
- **Regla heredada (§15.4.1)**: el contrato fijado aquí obliga a P2/P3-A/P3-B; cambios posteriores requieren decisión registrada.

### FASE-P2 — Refactor de ordenamiento (ALTA · solo si Q1=sí y opción ≠ O4)
- Implementar O1/O2/O3 manteniendo never-block, NR2 y NR3.
- Tests obligatorios: camino de bloqueo ejercitado (recomendación BLOQUEAR de un revisor → ZIP no emitido), camino aprobado, never-block (fallo de un revisor no rompe la corrida), retro sobre `output/` vivo y sobre la corrida E2E del predecesor (`evidence/FASE-E2E/`).
- **NR7 (mutation check)**: para AC-E2, desactivar el consumo de `reviewer_reports` en `_compute_verdict` y confirmar que el test de bloqueo se pone rojo; un test que emite el acta a mano y pasa con el guard quitado no certifica el enforcement (precedente: L-T4A.5, L-T2C.4).
- **NR8**: el tri-estado exige un test nombrado por su causa — `los 4 revisores fallan` ≠ `los 4 revisores no hallan nada` ≠ `los revisores no corrieron`. Prohibido cerrar el AC con un fixture que solo pueda producir uno de los tres estados (L-PF10).
- **Baseline NR1**: snapshot `pre` tomado con `--ignore` del archivo de tests de la fase (L-T4B.5) y verificación por resta R2.7 (`suma_post − suma_pre == tests_nuevos`; diferencia 0 = baseline contaminado).
- Si Q1=no (O4): la fase se sustituye por documentación de la decisión y se cierra sin código.

### FASE-P3-A — Detección y fidelidad del acta (MEDIA · 3 tareas, R3)
Dividida de la P3 original en la sesión de ajuste 2026-09-14: la suma de 6 fixes excedía el máximo de 4 tareas/fase de R3 (decisión D-AJUST.1 en `10-analisis`).
- **AC8**: opción a fijar en P1 (Q2b) — (a) `_resolve_delivery_dir()` lee `IMPLEMENTATION_ORDER.md` del ZIP vía `zipfile`, o (b) recalibrar `_is_template_stub()` (excluir `---` y boilerplate Fecha/Score/footer del conteo). **Cierre con mutation check (NR7)**: con el fixture del caso real, desactivar el fix y ver el test en rojo — AC8 ya falló por heurístico que "pasaba" sobre un layout que no existía (L-V.1).
- **Tier del acta**: el Juez lee el tier de una fuente disponible pre-packaging (`financial_scenarios.breakdown.evidence_tier`) o se reordena — converger con P2 si hay reordenamiento.
- **AC-F4 · Fidelidad del primer piso en `B_PLUS`**: `FIRST_FLOOR_TIERS` = {`B`,`C`} deja pasar `B_PLUS`, así que el acta afirma "sin restricción de primer piso" en un caso que sale condicional por el guard de Tier A. El `reason` debe decir por qué el veredicto es el que es (o `FIRST_FLOOR_TIERS` debe cubrir todo lo que no sea `A` — decidir en P1 y fijar en el contrato, no improvisar aquí).

### FASE-P3-B — Cableado y test (BAJA, o MEDIA si Q5=a · 2–3 tareas, R3)
- **Whitelist barreda (D-V.1)**: test-only — autorizar a Bot 3 como emisor legítimo de `asset_path` en `test_barreda_un_solo_emisor_de_la_clave`.
- **Versión del acta**: `acta_writer.py` lee de `VERSION.yaml` (fuente única).
- **AC-F5 · Banderas de analítica (solo si Q5=(a))**: propagar la disponibilidad real (`ga4_available`, `gsc_available`) al `HotelFinancialData` del bloque FASE-K, lo que exige **hoist** de esas variables por encima del bloque. L-T2C.2 es la advertencia directa: un hoist en `main.py` con un `except Exception` ancho alrededor puede enmascarar un `NameError` y cambiar el tier de corridas reales. Test obligatorio: `tier` con analítica disponible y sin ella, más delta NR1 con par pre/post. Si Q5≠(a), la fase ejecuta solo las dos tareas fijas y AC-F5 queda registrado como condicional no disparado.

### FASE-P4 — Corrida de observación (MEDIA · MIXTO · opcional)
- **Cierre válido sin P4**: si T3a no se cierra (nadie provee el dato con fuente), P4 se difiere con la mecánica de `dependencias-fases.md` §Cierre válido sin P4 — decisión registrada, no precondición "en espera". El fallo de T3b **no** difiere la fase: AC-O0 (`B_PLUS` con límite declarado).
- **Precondición T3a (datos operativos)**: hotel propio — `rooms`, `occupancy_rate`, `direct_channel_percentage`, `ADR` con fuente declarada. Sin esto el tier queda en `B`/`C` y no se levanta el primer piso.
- **Precondición T3b (analítica) — nueva, medido 2026-09-12**: `evidence_tier: A` exige además GA4 **y** GSC disponibles **y** que el bloque FASE-K propague las banderas (Q5, §2.1). Si Q5=(b), **el techo de esta fase es `B_PLUS` y el `APROBADO-PARA-ENTREGA` no es observable**: el informe debe declararlo como límite, no como corrida fallida.
- **Antes de redactar el brief delegado (L-VUP-9)**: verificar `--help` de `onboard` y `v4complete` y usar solo argumentos reales; un prompt con un argumento inexistente produce un FAIL que no evalúa ningún AC.
- **Antes de la corrida (L-VUP-13)**: `ls output/clientes/` y el log de onboarding. Si el hotel no está poblado, el pipeline cae a defaults y el tier/pricing cambian: la condición de equivalencia se declara en el informe, no se infiere.
- **Orden del paso (L-VUP-12)**: (1) corrida delegada, (2) **copia de evidencia antes de analizar**, (3) comparación con script versionado en la propia carpeta de evidencia, (4) análisis.
- **Delta (R2.3) con diff estructural, no visual (L-VUP-14)**: parsear los JSON del predecesor (`evidence/FASE-E2E/`) y comparar por clave numerada; probar el parseo contra el baseline **antes** de lanzar la corrida costosa.
- **Encuadre**: corrida de observación/diagnóstico, NO entrega a cliente. `APROBADO-PARA-ENTREGA` = provisional si el enforcement no está cerrado.
- Entregable: `evidence/FASE-P4/informe-observacion.md` (checklist §5) + delta vs corrida E2E del predecesor (R2.3).

### FASE-P5 — Seguridad y privacidad (pendiente · DIRECTO · 4 tareas, sin comandos largos)

Prioridad anterior a nuevas corridas o publicaciones. Dueños: mantenimiento de validaciones/providers (controles técnicos) y operador (credenciales, autorización y disposición de datos).

1. **Inventario y decisiones operativas (AC-S3/AC-S4):** medir la superficie pública por commit, ruta y clase de material; registrar estado de rotación preventiva de la clave y contención de datos con dueño y evidencia no secreta. Comparar retirada de HEAD con saneamiento del historial y sus consecuencias antes de pedir autorización específica. No ejecutar estas acciones por haber aprobado el plan.
2. **Sanear errores del provider (AC-S1):** corregir `_query_gemini`/`_query_provider` en `modules/auditors/llm_mention_checker.py` para que secretos de URL, headers o excepciones no lleguen a logs ni stderr; probar el error HTTP 403 con un token sintético, sin llamada de red.
3. **Controlar lo que se prepara para publicar (AC-S2):** ampliar `_check_no_secrets` de `scripts/run_all_validations.py` sobre contenido staged, no solo asignaciones en Python; incluir textos de cualquier extensión y tests, salida redactada y estados explícitos para archivos no legibles/no cubiertos. Separar detección de claves de la política que impide versionar material de cliente. Verificar la conexión del control con los hooks existentes; cambios de hooks/configuración o dependencias requieren alcance autorizado, nunca un bypass.
4. **Certificar los controles:** pares NR7, baseline NR1 pre/post, pruebas staged/worktree divergentes y registro de la puerta operativa AC-S4. No escaneo en nube, rotación automática, subida de evidencia, retirada ni reescritura de historial en esta tarea.

Prompt: `05-prompt-inicio-sesion-fase-P5.md`. El cierre técnico permite P6 sin esperar acceso a cuentas externas; **no habilita RELEASE público** mientras rotación/contención sigan pendientes sin resolución verificable o aceptación explícita del riesgo por el operador.

### FASE-P6 — Generación y validación multi-hotel (pendiente · DIRECTO · 4 tareas, sin comandos largos)

Dueños: equipo-assets (G1), mantenimiento onboarding (G2), mantenimiento tribunal/delivery (G3/G5) y QA del pipeline (G4). Se corrige el productor, no un archivo de Don Alfonso ni el detector para hacerlo pasar.

1. **Instrucciones desde la entrega real (AC-G1):** revisar el paso de `Path(a.path).name` en `main.py`, `AssetResponsibilityContract.get_implementation_order`/`generate_delivery_template`, `ImplementationOrderGenerator` y `DeliveryPackager.write`; relacionar identidad de asset con su ruta real dentro del ZIP, preservando fecha y prefijo `ESTIMATED_`. Los tipos fuera del catálogo fijo deben tener disposición explícita, nunca desaparecer en silencio. No rellenar la plantilla ni ampliar una whitelist de nombres por hotel.
2. **Entrada de datos independiente del entorno (AC-G2):** corregir `_load_latest_onboarding_data` y su invocación FASE-D para resolver `observations.json` aunque falte `clientes/` o no haya YAML ajeno, tanto en output por defecto como alternativo. Rastrear WhatsApp fuente → `_observation_to_onboarding_format` → validación: propagar solo evidencia realmente disponible; ausencia de dato no se convierte en teléfono inventado, `verified` ni aprobación automática.
3. **Identidad del paquete suprimido (AC-G3):** guardar `package_evidence.sha256` y `package_evidence.member_count` en el acta desde el `.zip.tmp` real leído por los revisores, antes de `suppress()`. Mantener la supresión y el contrato single-write; no conservar/publicar el ZIP bloqueado. La huella identifica el objeto, no reconstruye su contenido.
4. **Matriz multi-hotel y causalidad (AC-G4/AC-G5):** reproducir al menos tres perfiles, incluido el caso Don Alfonso sin datos sensibles y dos perfiles adicionales sintéticos/anonimizados, en un entorno limpio. Probar el productor, ZIP real, revisores y Juez juntos en los tres caminos separados: gates permiten/revisores permiten; mismos gates permiten/revisor objeta; gates ya bloquean. Conservar NR1 y NR7; no escribir un acta a mano como sustituto del flujo ni debilitar los gates para obtener un ZIP.

Prompt: `05-prompt-inicio-sesion-fase-P6.md`. La matriz offline no es una muestra estadística ni tres corridas reales; una nueva corrida de red exige otra sesión y consentimiento/frescura/coste explícitos. Tier A real sigue pendiente de GA4/GSC del hotel. Funcionar para cualquier hotel significa decidir correctamente según su evidencia, no aprobar siempre.

### FASE-RELEASE-4.77.0 (solo documental · DELEGABLE)
- Dependencia obligatoria: P5/P6 certificadas y puerta AC-S4 resuelta; no remediar aquí F-P4.1/F-P4.5/F-P4.9 ni otros defectos descubiertos.
- AC-V1 certifica AC-E*/AC-F* y los nuevos AC-S*/AC-G* contra sus artefactos y pares NR7; distingue prueba offline de observación real. P4 conserva su cierre y sus límites.
- Flujo documental estándar: `log_phase_completion.py --release`, `sync_versions.py`, CHANGELOG, GUIA_TECNICA, doctor, write-back e índice antes del archivado R2.5.
- Commit final y tag anotado `v4.77.0` solo con autorización; el tag apunta al commit final, no se crea antes de él. Push requiere confirmación propia. `v4.76.0` ya se publicó el 2026-09-14, no se presume pendiente.

---

## 5. Checklist de observación (P4) — qué mirar en la corrida real

1. `evidence_tier` resultante con dato real (¿A?) y `first_floor_rule` levantado.
2. Veredicto: ¿alcanza `APROBADO-PARA-ENTREGA`? (provisional si E no cerrado).
3. Comportamiento de Bots 1–4 con dato rico: nuevos findings, falsos positivos/negativos.
4. Fidelidad del acta: `evidence_tier` del acta vs MANIFEST (post-P3-A debe coincidir).
5. Gap advisory: recomendaciones de revisores vs veredicto (si P2 cerró enforcement, ya no debe existir).
6. AC17/AC19 del predecesor con cifras reales: `precision_tier`, `can_show_exact_money`, bases de pérdida (`expected_loss_cop` vs fuga mensual).
7. Delta vs corrida E2E del predecesor (R2.3: par pre/post).
8. **Estado real de `reviewer_reports` (NR8)**: cuántos revisores corrieron, cuántos fallaron y fueron tragados por el never-block, y cuáles produjeron cero hallazgos. Si el acta no permite distinguir los tres, AC-E0 no está cerrado aunque el veredicto se vea razonable.
9. **Techo de tier de la corrida**: `ga4_available`/`gsc_available` efectivos y el `evidence_tier` resultante. Si la corrida quedó en `B_PLUS`, el informe lo declara como límite de la fase (no como hotel con datos malos).

---

## 6. ACs FINALES (fijados en FASE-P1, 2026-09-14 — R2.4: artefacto + clave)

Versión canónica con el enunciado completo: §5 de `evidence/FASE-P1/decision-enforcement.md`.

| AC | Fase | Enunciado | Artefacto + clave (R2.4) | NR7 |
|----|------|-----------|--------------------------|-----|
| **AC-D1** | P1 ✅ | Matriz recomendación→veredicto **y** consecuencia aguas abajo del bloqueo **y** cuatro estados, fijados antes de cualquier implementador | `evidence/FASE-P1/decision-enforcement.md` → §2 Matriz, §3 Consecuencia, §4 Cuatro estados | n/a |
| **AC-E0** | P1→P2 | El acta distingue **cuatro** estados por revisor (`OK_NO_FINDINGS`/`ARTIFACT_MISSING`/`READER_FAILED`/`NOT_RUN`) y la sección **nunca** se omite del MD | `acta_revision.json` → `reviewer_reports[].status`; `acta_revision.md` → sección `Reportes de Revisores` siempre presente | 4 tests nombrados por causa + 1 que colapsa los estados y debe romperse; vetado el fixture de un solo estado (L-PF10) |
| **AC-E1** | P2 | `reviewer_reports` refleja a los 4 revisores cuando corrieron | `acta_revision.json` → `reviewer_reports` (longitud 4) | Quitar el poblado desde el DTO → rojo |
| **AC-E2** | P2 | CRITICAL verificado o `BLOQUEAR` de un revisor → el ZIP no se publica, por una sola ruta | test output + `acta_revision.json` → `verdict` | Quitar el consumo de `reviewer_reports` en `_compute_verdict` → rojo. Un acta escrita a mano **no** certifica el AC |
| **AC-E3** | P2 | Never-block: un revisor que revienta no rompe la corrida y queda como `READER_FAILED` | test output | Hacer que el `except` relance → rojo |
| **AC-E4** | P2 | El bloqueo del tribunal respeta `GATE_BLOCKING_ENABLED` y el acta declara el estado del knob (escape honesto, no silencioso) | `acta_revision.json` → `enforcement.{blocking_env,enabled,suppressed_by_operator}` | knob apagado → se publica y el acta lo dice; test con knob forzado a on → el bloqueo sigue ejercitado |
| **AC-E5** | P2 | Con veredicto bloqueante no existe ZIP publicado y el acta trae acciones correctivas con dueño; **sin reintento automático y sin entrega parcial** | glob sobre `deliveries/` (ningún `*.zip` del `hotel_id`) + `acta_revision.json` → `corrective_actions[]` con `owner` | Sustituir `unlink` por `rename` → rojo; vaciar `corrective_actions` con veredicto bloqueante → rojo |
| **AC-F1** | P3-A | `EMPTY_DELIVERY_TEMPLATE` dispara en régimen ZIP-only real leyendo **desde el ZIP** y con criterio **estructural** (no conteo de líneas) | `revision_assets.json` → `findings[].finding_type` | Dos mutaciones, una por capa, con par de salidas en `evidence/FASE-P3-A/` |
| **AC-F2** | P3-A | `evidence_tier` del acta == el del pipeline, leído de fuente disponible pre-packaging | `acta_revision.json` → `evidence_tier` vs `financial_scenarios_*.json` → `breakdown.evidence_tier` | Volver a `MANIFEST` en ZIP-only → el acta dice `C` y el test rojo |
| **AC-F3** | P3-B | `test_barreda_un_solo_emisor_de_la_clave` verde con la whitelist **justificada** por el contrato del emisor de `asset_path` | test output | Quitar la autorización de `asset_reviewer` → rojo; prohibido cerrarlo como `xfail` |
| **AC-F4** | P3-A | En `B_PLUS` el `reason` del primer piso describe por qué el veredicto es condicional | `acta_revision.json` → `first_floor_rule.reason` | Dejar `FIRST_FLOOR_TIERS` sin cubrir `B_PLUS` → el `reason` vuelve a mentir → rojo |
| **AC-F5** | P3-B | **Disparado por Q5=(a)**: con GA4+GSC disponibles el `HotelFinancialData` del bloque FASE-K recibe las banderas reales y el tier puede ser `A` | `financial_scenarios_*.json` → `breakdown.evidence_tier` | 4 casos: `A` con analítica / `B_PLUS` sin ella / sin `NameError` con `generate_proposal=False` (amplía `tests/quality_gates/tribunal/test_s_e2_generate_proposal_false.py`) / delta NR1 |
| **AC-F6** | P3-B | El acta ya no hardcodea la versión: `acta_writer.py` lee `VERSION.yaml` | `acta_revision.md` → footer `TribunalJudge vX.Y.Z` | Fijar la versión a mano en el writer → rojo |
| **AC-O0** | P4 | El informe declara el techo de tier **y a quién pertenece ese techo** (cableado ya arreglado por AC-F5, o T3b del hotel sin resolver) | `evidence/FASE-P4/informe-observacion.md` → §Techo de tier | n/a |
| **AC-O1** | P4 | Corrida con acta enriquecida y veredicto (provisionalidad registrada si algo de P2 queda abierto) | `acta_revision.json` → `verdict` + `evidence_tier` + `reviewer_reports` | n/a |
| **AC-O2** | P4 | Informe con los 9 puntos del §5 + **snapshot del baseline ajeno** dentro de la carpeta propia (cura de `L-B4`) | `evidence/FASE-P4/informe-observacion.md` + `evidence/FASE-P4/baseline-predecesor/` | n/a |
| **AC-V1** | RELEASE | Patrón VERIFY embebido: certificación de AC-E*/AC-F* contra artefacto de fase + los pares NR7, **sin exigir corrida P4** | matriz en `10-analisis-post-implementacion.md` | cada AC trae el suyo |

> **Verificación NR7 (mutación)**: los AC de detección o bloqueo (**AC-E0, AC-E2, AC-E3, AC-E4, AC-E5, AC-F1, AC-F2, AC-F3, AC-F4, AC-F5, AC-F6**) no se cierran solo con el test verde — la evidencia guarda el **par de salidas**: con la detección/guard activo (verde) y con él desactivado (rojo). Sin el segundo lado, el AC queda ⚠️ y no ✅ (R2.4 + L-VUP-5).
> **AC retirados en P1**: ninguno. **Cambios respecto al borrador**: AC-E0 de tres a cuatro estados (DA-P1.6); nacen AC-E4 (Q7), AC-E5 (Q1b) y AC-F6 (versión del acta, que estaba en el plan de fase sin AC propio); AC-F5 deja de ser condicional porque Q5=(a); AC-O2 incorpora el snapshot de `L-B4`.

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

Objetivo **4.77.0** (confirmar en P1). Fuente única: `VERSION.yaml`. Nunca hardcodear versiones en código — incluye `acta_writer.py` (fix P3-B). Tags: `v4.76.0` creado y empujado el 2026-09-14 sobre `3bdc14e`; `v4.77.0` se crea al cerrar RELEASE — la omisión del anterior es la lección.

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
