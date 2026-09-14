# FASE-P1 · Tareas 2–3 — Decisión de Enforcement y Contrato del Veredicto Enriquecido

> **Plan**: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11 · **Fecha**: 2026-09-14
> **Sesión de decisión**: cero código de producción modificado.
> **Este documento obliga a FASE-P2 / P3-A / P3-B** (regla §15.4.1 heredada). Cambiar lo fijado aquí exige decisión explícita registrada, no interpretación en la fase.
> **Fuente de los símbolos citados**: `research-estado.md` (misma carpeta), que re-leyó cada símbolo en el artefacto (L-V.2). Sin números de línea (R2.2).

---

## 0. Tabla de decisiones

| # | Pregunta | Decisión | Dueño de la ejecución |
|---|----------|----------|------------------------|
| Q1 | ¿Enforcear? | **SÍ — enforcement** | P2 |
| Q1b | ¿Qué pasa aguas abajo del bloqueo? | **ESCALAR**: ZIP suprimido (el `.tmp` no se renombra) + acta con acciones correctivas + decide el humano. Sin reintento automático, sin entrega parcial | P2 |
| Q2 | ¿Qué ordenamiento? | **O1-cuarentena** (write → revisar → decidir → *publish* o suprimir). El punto de decisión se mueve del *write* al **rename atómico** | P2 |
| Q2b | ¿Remedio de AC8? | **Ambas capas** (el "o" del plan era un "y"): lectura desde el ZIP + detección **estructural** del stub | P3-A |
| Q3 | ¿Secuenciación? | **P3-A → P3-B → P2 → P4** (substrato confiable antes que dientes) | — |
| Q4 | ¿Quién provee T3a? | **El hotel, por contacto directo del operador** — jerarquía Salento Real → Don Alfonso/Luxor → Zi-One. Si nadie provee con fuente: **P4 diferida** | externo (operador) |
| Q5 | ¿Tier A inalcanzable? | **(a) Propagar las banderas**, como **par inseparable con AC-F2** | P3-B (AC-F5) + P3-A (AC-F2) |
| Q6 | ¿Cuántos estados por revisor? | **CUATRO**, no tres: `OK_NO_FINDINGS` / `ARTIFACT_MISSING` / `READER_FAILED` / `NOT_RUN`, y **la sección nunca se omite del MD** | P2 (acta) + P1 fija claves (este doc §4) |
| Q7 | ¿Kill switch? (nace de la verificación pedida) | **(a) Hereda `GATE_BLOCKING_ENABLED`** + cláusula de escape honesto: el acta declara que el enforcement estuvo apagado | P2 |
| — | ¿FASE-VERIFY propia? | **NO activa.** AC-V1 en RELEASE ejecuta el patrón; la certificación queda anclada al par NR7 por fase, no a una corrida condicional | RELEASE |

---

## 1. Rationale y alternativas rechazadas (formato DA-*)

### DA-P1.1 — Enforcement sí (Q1)

- **Decisión**: el tribunal enforcea. Las objeciones verificadas de sus revisores impiden publicar el ZIP.
- **Rationale (estructural, no de preferencia)**: `ROADMAP.md` §9 fija **G0** = diagnóstico en Tier A con acta `APROBADO-PARA-ENTREGA`, y su regla de gobierno es "no escalar comercialmente si G0 no está en PASS". `_compute_verdict` solo emite ese veredicto con `evidence_tier == "A"` **y** todas las `T1_CERTIFIABLE_CLAUSES` en `PASS`; hoy `P6.2`/`P6.5` salen `NOT_EVALUABLE` porque el Juez nunca recibe a los revisores. Un tribunal que audita sin alimentar el veredicto deja **G0 incerrable por diseño**: no es la opción conservadora, es cancelar el norte del producto.
- **Segundo argumento**: solo existen dos estados coherentes. Alimentar a los revisores al veredicto **y** bloquear, o no alimentarlos. El intermedio (alimentar sin bloquear) produce un acta que puede decir `DEVOLVER-CORRECCIONES` mientras el paquete existe.
- **Alternativas rechazadas**:
  - **(b) O4 auditoría-only** — congela el producto en pre-entrega. Rechazada.
  - **(c) decidir tras P4** — hoy **inobservable**: con el cableado actual la corrida no puede producir Tier A (§2.1 confirmado), así que "observar antes de decidir" no muestra el caso que motiva la decisión. Rechazada.
- **Riesgo real y dónde se gestiona**: no está en la decisión sino en la **calibración al cablear**. Se gestiona con el orden P3→P2 (DA-P1.3) y con el kill switch (DA-P1.7), no renunciando al enforcement. Cablear dientes sobre detecciones rotas (AC8) produce bloqueos que el operador no puede evaluar, y el desenlace natural es que alguien apague el tribunal y este quede desacreditado.

### DA-P1.2 — Escalar, no ciclar (Q1b)

- **Decisión**: en `DEVOLVER-CORRECCIONES` o `BLOQUEADO`: (i) el ZIP **no se publica** (se suprime el `.zip.tmp`), (ii) el acta lleva `corrective_actions` con el artefacto, la instrucción y el dueño de cada hallazgo, (iii) **decide un humano**.
- **Descartados**:
  - **Ciclar con el `suggestion` del revisor + 1 reintento** (la cura de `L-PF3` en su forma literal) — no aplica: los defectos que motivan el bloqueo son **estructurales** (p. ej. `IMPLEMENTATION_ORDER.md` stub, asset ausente). Regenerar produce el mismo stub porque no hay `suggestion` aplicable como restricción de re-generación. La lección se conserva en su espíritu — un bloqueo sin camino de reparación replica el defecto que denuncia — pero el camino aquí es **la acción correctiva documentada**, no el reintento.
  - **Entrega parcial** (ZIP sin el asset bloqueado) — contradice el acta y re-introduce la incoherencia de DA-P1.1.
- **Precedente en el repo**: la rama de `GATE_BLOCKING_ENABLED` ya borra documentos cliente y escribe `BLOCKED_BY_GATES.md`. La supresión de un artefacto ya generado no es un mecanismo nuevo.
- **Alineación con el ROADMAP**: "el agente prepara y documenta; el humano decide".

### DA-P1.3 — Orden P3 → P2 (Q3)

- **Decisión**: `P3-A → P3-B → P2 → P4`.
- **Rationale**: P3-A arregla las dos detecciones en las que P2 va a apoyarse (AC8/AC-F1 y la fuente del tier/AC-F2). Sin ellas, el primer bloqueo real del tribunal podría deberse a un falso positivo y nadie sabría distinguirlo. `AC-F2` además es **precondición** de que Tier A sea observable, así que P2 hereda de P3-A aunque no lo declare.
- **Consecuencias registradas**: la tabla de dependencias y el diagrama de `dependencias-fases.md` se reordenan; P2 pasa a **depender** de P3-A y P3-B (baseline NR1 propio, `judge.py` ya corregido por P3-A antes del reordenamiento).
- **Descartado**: P2 primero (cablear sobre detecciones rotas); P4 primero (DA-P1.1 rechaza (c)).

### DA-P1.4 — O1-cuarentena (Q2)

- **Decisión**: los revisores siguen leyendo artefactos de disco; lo que cambia es **dónde cae la decisión**. Secuencia contractual:
  1. `DeliveryPackager` construye los bytes ya finalizados y escribe `deliveries/<hotel_id>_<fecha>.zip.tmp` — **sin renombrar** (el patrón `tmp → Atomic rename` existe hoy; se expone como dos pasos).
  2. Los 4 revisores leen **ese ZIP real** (`zipfile`, con los miembros in-memory `MANIFEST.json` / `IMPLEMENTATION_ORDER.md` / `ASSETS/` adentro). Su contrato de "leen artefactos del disco" queda intacto.
  3. El Juez corre su **segunda pasada de veredicto** sobre el mismo objeto `acta`, ahora con `reviewer_reports` poblados → acta enriquecida.
  4. `blocks_delivery_zip(acta)` — **único predicado, sin cuarta ruta (NR3)** — decide: `rename` (publicado) o `unlink` (suprimido) + `corrective_actions`.
- **Por qué no las otras**:
  - **O1-staging de metadatos**: materializar `MANIFEST.json`/`IMPLEMENTATION_ORDER.md` en un staging que el cliente nunca ve crea un layout con riesgo de drift frente al ZIP, y obligaría a que AC-F1 lea staging, no ZIP — contradiciendo la raíz medida de AC8 (un resolutor escrito contra un layout que el packager ZIP-only jamás produce).
  - **O2-estado en memoria**: rompe el contrato de que los revisores leen artefactos y fragiliza los tests existentes de los 4 revisores.
  - **O3-dos pasadas**: cambia el contrato del packager (abandona single-write ZIP-only), que es el diseño que este plan declaró inmutable.
- **Coste honesto**: `package()` deja de ser un método atómico de un solo paso; P2 debe partirlo en *write* y *publish* con API explícita. Es el blast radius real de la opción, y va en el presupuesto de P2.
- **Verificación obligatoria en P2 (abierta aquí, no improvisable)**: comprobar si el ZIP empaqueta el acta (`ActaWriter` escribe en `v4_audit_dir`). **Si la contuviera, el acta publicada debe ser la enriquecida, nunca la pre-veredicto** — otro modo el ZIP se contradice a sí mismo (el defecto que DA-P1.1 usa como argumento).

### DA-P1.5 — AC8 en dos capas, con raíz común a AC-F2 (Q2b)

- **Decisión**: arreglar **las dos capas**, y reconocer que AC8 y AC-F2 son el mismo defecto con dos víctimas: `_resolve_delivery_dir` (Bot 3) y `_resolve_manifest` (Juez) están escritos contra un **directorio descomprimido** que el packaging single-write ZIP-only nunca produce; ambos caen a un fallback silencioso (el `.zip` como `Path`, o `"C"` como tier).
- **Capa 1 — lectura desde el ZIP**: `zipfile.ZipFile(...).read("IMPLEMENTATION_ORDER.md")` y `.read("MANIFEST.json")`. **Prohibido devolver "vacío sin error"**: si el miembro no está → `ARTIFACT_MISSING`; si el ZIP es ilegible → `READER_FAILED` (DA-P1.6). Precedente de apertura del ZIP ya en el packager (`_validate_zip`).
- **Capa 2 — criterio estructural, no conteo de líneas**: el umbral `non_empty_lines <= 3` ya falló calibrado contra un layout inexistente (`L-V.1`). Nuevo criterio: **stub ⟺ (0 bytes) O (≥1 sección declarada Y todas las secciones con 0 líneas de contenido real, excluyendo `---` y las líneas boilerplate de Fecha/Score/footer)**. `_is_template_stub` ya construye `section_content_lines`; el cambio es usar esa estructura en vez del conteo global.
- **Descartado**: (b) sola — deja pasar el stub porque el archivo nunca se lee; (a) sola — un heurístico frágil sigue decidiendo; "dejarlo caer porque el reordenamiento lo resuelve" — falso con O1-cuarentena, donde los revisores siguen leyendo un ZIP.

### DA-P1.6 — Cuatro estados, no tres (Q6)

- **Decisión**: el tri-estado de NR8 (`sin hallazgos / artefacto ausente / lector fallido`) **omite el estado que la corrida real ya exhibe**: `NOT_RUN`. Hoy `evaluate()` fija `"reviewer_reports": []` y los revisores escriben sus JSON en un bloque posterior e independiente — ese `[]` **es** `NOT_RUN`, y colapsarlo con "lector fallido" escondería exactamente el defecto que P2 viene a arreglar.
- **Reglas del contrato (no negociables)**:
  1. **La sección nunca se omite del acta MD.** `acta_writer` hoy renderiza `## Reportes de Revisores` solo `if reviewer_reports:` — inaceptable en un documento cuya función es evidenciar rigor: una sección ausente se lee como "no se revisó" cuando el estado real puede ser otro. La sección se imprime **siempre**, con los cuatro estados por revisor.
  2. **Ausencia jamás es PASS.** `ARTIFACT_MISSING` / `READER_FAILED` / `NOT_RUN` producen cláusula `NOT_EVALUABLE`. El verde solo existe con `OK_NO_FINDINGS` o con hallazgos evaluados (`L-PF6`, `L-PF10`, `DA-C3`).
  3. **Un fallo de lectura no bloquea.** Estos tres estados **nunca** degradan a `BLOQUEADO` ni a `DEVOLVER-CORRECCIONES`: impiden `APROBADO-PARA-ENTREGA` (por el guard de `NOT_EVALUABLE`), pero no suprimen un paquete cuyo problema no fue verificado. Bloquear solo con hallazgo verificado.
  4. **`NOT_RUN` es canario post-P2.** Si aparece tras el reordenamiento, el cableado está roto.

### DA-P1.7 — El tribunal hereda `GATE_BLOCKING_ENABLED` (Q7, nace de la verificación pedida)

- **Medición pedida y su respuesta**: **NO**. `_gate_blocking_enabled` gobierna únicamente la rama `readiness_report["status"] == "NOT_READY" or _claim_escalated` (borrado de documentos cliente + `BLOCKED_BY_GATES.md`). La condición del ZIP-skip que consume `_tribunal_blocks` está **fuera** de esa región y es incondicional. Hoy el tribunal no tiene forma de desactivarse salvo que el propio Juez reviente y caiga en su `except Exception` never-block.
- **Decisión**: el bloqueo del tribunal pasa a respetar **la misma variable** (`GATE_BLOCKING_ENABLED`, default on, `"false"` para CI/tests), con dos condiciones:
  1. **Un solo knob para todo lo que suprime entrega client-facing.** Dos variables de bloqueo confundibles son la semilla del siguiente bypass.
  2. **Escape honesto, no silencioso (extensión de NR8 al propio gate):** cuando el knob esté apagado, el acta debe declararlo. Clave nueva `enforcement` con `{"blocking_env": "GATE_BLOCKING_ENABLED", "enabled": <bool>, "suppressed_by_operator": <bool>}`. Un CI que lo apague no puede reportar el enforcement como ejercitado.
  - Y un test propio que **fuerce** el knob a on y ejercite el camino de bloqueo, para que el `false` de CI no deje el AC-E2 sin cobertura.
- **Descartado**: (b) sin kill switch — sin vía de escape documentada frente a una mala calibración, que es justo el escenario de desacreditación del tribunal; (c) knob propio `TRIBUNAL_BLOCKING_ENABLED` — granularidad a costa de dos switches que alguien puede confundir.

### DA-P1.8 — Q5=(a) como par inseparable con AC-F2

- **Decisión**: propagar las banderas reales, **y** arreglar la fuente del tier del Juez en la misma cadena de cierre.
- **Rationale**: es un **fix de honestidad, no una feature**. El pipeline calcula `ga4_client.is_available()` y luego la descarta fijando `ga4_enabled=False` al construir `HotelFinancialData` en el bloque FASE-K. La regla FASE-1 de `_determine_evidence_tier` ("sin GA4+GSC, nunca A") queda **intacta**: lo que cambia es que su input deja de ser falso.
- **Por qué el par**: propagar banderas sin arreglar la fuente del tier es invisible — `_read_evidence_tier` seguiría leyendo `"C"` porque su única fuente es un `MANIFEST.json` que aún no existe. `AC-F5` (P3-B) + `AC-F2` (P3-A) cierran juntos o no cierran.
- **Descartado**: (b) `B_PLUS` con límite declarado — válido como **fallback de P4** si el hotel no tiene analítica (T3b es externa), no como decisión de producto: dejaría `APROBADO-PARA-ENTREGA` como código muerto y G0 incerrable. (c) diferir P4 — no resuelve el defecto, solo lo pospone, y con Q5=c el plan pierde su régimen objetivo sin arreglarlo.
- **Líneas rojas (L-T2C.2)**: el hoist de `ga4_available`/`gsc_available` por encima del bloque FASE-K vive dentro de un `try/except Exception` que solo imprime un warning: un `NameError` enmascarado degradaría el tier de corridas reales **en silencio**. Tests obligatorios: tier `A` con analítica / `B_PLUS` sin ella / sin `NameError` en régimen `generate_proposal=False` (**ampliar `tests/quality_gates/tribunal/test_s_e2_generate_proposal_false.py`, que ya existe para el hoist S-E2**) / delta NR1. Y el cambio de tier en corridas reales es comportamiento visible → **se declara en CHANGELOG**, no en silencio.

### DA-P1.9 — Proveedor de T3a (Q4)

- **Decisión**: el dato lo aporta **el hotel, por contacto directo del operador**. Jerarquía de candidatos: **Salento Real** (recolección nueva → delta limpio y ensayo del motion comercial) → **Don Alfonso / Luxor** (T3a satisfecha hoy, pero delta confundido con el cambio de cableado → declarado) → **Zi-One**.
- **Tres líneas rojas**: (i) **el agente jamás llena el YAML** de onboarding; (ii) **nada de datos plausibles "para destrabar"** — un dato inventado sube el tier mintiendo, que es el defecto que este plan acaba de documentar en DA-P1.8; (iii) **consentimiento y frescura registrados** antes de la corrida. Sin proveedor con fuente: P4 se difiere por §Cierre válido sin P4, con decisión fechada, no "en espera".
- **Bandera (única que se añade al registro)**: el techo honesto `B_PLUS` **depende de que Q5=(a) esté cerrado en P3-B**. Si Q5 se difiriera, ni un hotel con GA4+GSC alcanzaría Tier A, porque las banderas siguen falsas por construcción. Por tanto: **"techo B_PLUS de Q4" va atado a "Q5=a cerrado en P3-B"**, para que nadie lea un `B_PLUS` como "el hotel dio malos datos" cuando es "el cableado no propaga las banderas". Son dos conversaciones distintas: quién da el dato (comercial) y si el pipeline puede certificar A (Q5/P3-B).

---

## 2. Contrato del veredicto enriquecido

### 2.1 Matriz recomendación → veredicto (hereda T1 sin cambios graduales)

Orden de evaluación en `_compute_verdict` — el orden **es** parte del contrato:

| # | Condición (sobre `clauses` + `reviewer_reports`) | Veredicto | ¿Publica ZIP? |
|---|---------------------------------------------------|-----------|----------------|
| 1 | Gate blocking fallido (`P6.1` o `P6.6` en `FAIL`) | `BLOQUEADO` | No |
| 2 | **CRITICAL verificado** por un revisor: `ReviewerReport.status == OK_*` con `critical_count ≥ 1`, **o** su `recommendation == BLOQUEAR` | `BLOQUEADO` | No |
| 3 | **CRITICAL de consistencia**: `recommendation == DEVOLVER-PRUEBAS` con hallazgo CRITICAL, o cláusula `P6.3`/`P6.4` en `FAIL` | `DEVOLVER-CORRECCIONES` | No |
| 4 | `ARTIFACT_MISSING` / `READER_FAILED` / `NOT_RUN` de cualquier revisor | **no cambia el veredicto**; fuerza `NOT_EVALUABLE` en su cláusula → `APROBADO-PARA-ENTREGA` imposible | Sí, si nada de 1–3 disparó |
| 5 | Solo `WARNING`/`INFO` (con o sin `OK_NO_FINDINGS`) | **nunca degrada** por debajo del primer piso | según 6–7 |
| 6 | `first_floor["applied"]` (tier en `FIRST_FLOOR_TIERS`) | `APROBADO-CONDICIONAL-PENDING-ONBOARDING` | Sí |
| 7 | `evidence_tier == "A"` **y** `T1_CERTIFIABLE_CLAUSES` todas en `PASS` | `APROBADO-PARA-ENTREGA` | Sí |
| 8 | Cualquier otro caso | `APROBADO-CONDICIONAL-PENDING-ONBOARDING` | Sí |

**Invariants del contrato**:
- **NR5 intacto**: el LLM propone (`LLMPromiseExtractor`, los `recommendation` de los Bots), el Juez decide de forma determinista. Ningún revisor escribe `acta["verdict"]`.
- **Never-block por Bot intacto** (AC-E3): el fallo de un revisor se registra como `READER_FAILED`, jamás aborta la corrida.
- **NR2 intacto**: el tribunal no recalcula gates; consume lo que los gates ya publicaron.
- **NR3 intacto**: `blocks_delivery_zip` sigue siendo el **único** predicado que decide la entrega. P2 **no** introduce una segunda consulta al veredicto en `main.py` ni en el packager: el packager recibe el booleano.

### 2.2 Firma del consumo

`_compute_verdict(clauses, evidence_tier, first_floor)` → **`_compute_verdict(clauses, evidence_tier, first_floor, reviewer_reports)`**, con `reviewer_reports` tipado (no `list[dict]` crudo — `L-PF3` exige DTO, no parsing de JSON). `evaluate()` pasa a poblar la clave desde el DTO; el literal `"reviewer_reports": []` desaparece del código.

### 2.3 DTO tipado (superficie nueva; P2 la implementa en `judge.py`/nuevo módulo del paquete `tribunal`)

```
ReviewerStatus   (enum)  OK_NO_FINDINGS | ARTIFACT_MISSING | READER_FAILED | NOT_RUN
ReviewerReport   (dataclass) reviewer, status, findings_count, critical_count,
                              recommendation, report_path
CorrectiveAction (dataclass) finding_type, severity, artifact, instruction, owner
TribunalOutcome  (dataclass) verdict, blocks_publish: bool,
                             corrective_actions: list[CorrectiveAction],
                             enforcement: EnforcementState
EnforcementState (dataclass) blocking_env: str, enabled: bool,
                             suppressed_by_operator: bool
```

`TribunalOutcome` es lo que `main.py` consume. Nada de `json.loads` del acta para decidir: se decide sobre el DTO y el acta se deriva del DTO (serie→documento, nunca al revés).

---

## 3. Consecuencia del bloqueo (Q1b) — cláusula AC-D1/E5

Expresada por `TribunalOutcome.blocks_publish` y `corrective_actions`:

1. **No publicar**: el `.zip.tmp` se `unlink()`. El ZIP final nunca existe para el cliente, ni siquiera momentáneamente con nombre definitivo.
2. **Decir por qué**: el acta (JSON y MD) incluye la sección `Acciones correctivas` con un `CorrectiveAction` por hallazgo bloqueante: `finding_type`, `severity`, `artifact` (ruta concreta), `instruction`, `owner`.
3. **Que decida un humano**: el operador ve en stdout la ruta del acta y de `delivery_blocked.md`, con la lista de acciones. **No hay reintento automático ni entrega parcial.**
4. **No dejar el paquete huérfano**: si el `.tmp` no se borra por un fallo del propio borrado, se reporta como error de infraestructura, no como éxito de la supresión.
5. **Kill switch**: con `GATE_BLOCKING_ENABLED=false` los pasos 1–3 no se ejecutan, y el acta declara `enforcement.suppressed_by_operator: true` (paso 2 **sí** se escribe siempre).

---

## 4. Cuatro estados de revisor (Q6) — claves del acta

```
"reviewer_reports": [
  { "reviewer": "diagnosis_reviewer",
    "status": "OK_NO_FINDINGS | ARTIFACT_MISSING | READER_FAILED | NOT_RUN",
    "findings_count": 1, "critical_count": 1,
    "recommendation": "DEVOLVER-PRUEBAS",
    "report_path": "revision_diagnostico.json" }
]
"enforcement": { "blocking_env": "GATE_BLOCKING_ENABLED",
                 "enabled": true, "suppressed_by_operator": false }
"corrective_actions": [ { "finding_type": "...", "severity": "CRITICAL",
                          "artifact": "...", "instruction": "...", "owner": "..." } ]
```

- Cuatro entradas, una por Bot (`diagnosis_reviewer`, `asset_reviewer`, `alignment_reviewer`, `honesty_reviewer`), **siempre presentes**, con `status` incluso cuando `findings_count == 0`.
- **El MD renderiza la sección siempre** (se elimina el guard `if reviewer_reports:` de `acta_writer`).
- `NOT_RUN` post-P2 es un defecto: su sola aparición debe poder reclamarse en la revisión.

---

## 5. ACs finales (R2.4: artefacto + clave; NR7: par de salidas donde detecta o bloquea)

| AC | Fase | Enunciado | Artefacto + clave | NR7 (mutation check) |
|----|------|-----------|-------------------|----------------------|
| **AC-D1** | P1 ✅ | Este documento fija matriz, consecuencia del bloqueo y cuatro estados | `evidence/FASE-P1/decision-enforcement.md` → §2, §3, §4 | n/a (decisión, no detección) |
| **AC-E0** | P1→P2 | El acta distingue **cuatro** estados por revisor y la sección nunca se omite del MD | `acta_revision.json` → `reviewer_reports[].status`; `acta_revision.md` → sección `Reportes de Revisores` siempre presente | **Cuatro tests nombrados por causa**, uno por estado, y un quinto que colapsa los cuatro en una sola clave → debe romperse. Prohibido cerrar con fixture que solo produzca un estado (`L-PF10`) |
| **AC-E1** | P2 | `reviewer_reports` refleja a los 4 revisores cuando corrieron | `acta_revision.json` → `reviewer_reports` (longitud 4) | Quitar el poblado desde el DTO → rojo |
| **AC-E2** | P2 | CRITICAL verificado o `BLOQUEAR` de un revisor → el ZIP no se publica (única ruta) | test output + `acta_revision.json` → `verdict` | Desactivar el consumo de `reviewer_reports` en `_compute_verdict` → el test de bloqueo en rojo. Un test que emita el acta a mano **no** certifica el AC |
| **AC-E3** | P2 | Never-block: un revisor que revienta no rompe la corrida y queda como `READER_FAILED` | test output | Hacer que el `except` relance → rojo |
| **AC-E4** | P2 (nuevo, Q7) | El bloqueo del tribunal respeta `GATE_BLOCKING_ENABLED`, y el acta declara el estado del knob | `acta_revision.json` → `enforcement.{blocking_env,enabled,suppressed_by_operator}` | Apagar el knob con un veredicto bloqueante → el ZIP se publica **y** el acta dice `suppressed_by_operator: true`; forzar el knob a on en CI → el test de bloqueo sigue ejercitándose |
| **AC-E5** | P2 (nuevo, Q1b) | En `DEVOLVER-CORRECCIONES`/`BLOQUEADO` no existe ZIP publicado y el acta trae acciones correctivas con dueño | `deliveries/` (glob: ningún `*.zip` para el `hotel_id` de la corrida) + `acta_revision.json` → `corrective_actions[]` con `owner` | Sustituir `unlink` por `rename` → rojo; vaciar `corrective_actions` con veredicto bloqueante → rojo |
| **AC-F1** | P3-A | `EMPTY_DELIVERY_TEMPLATE` dispara en ZIP-only real, leyendo **desde el ZIP** y con criterio **estructural** | `revision_assets.json` → `findings[].finding_type` | **Dos mutaciones, una por capa**: (1) desactivar la lectura `zipfile` → rojo; (2) volver al conteo `non_empty_lines <= 3` sobre el stub real → rojo. Par de salidas en `evidence/FASE-P3-A/` |
| **AC-F2** | P3-A | `evidence_tier` del acta == el del pipeline en corrida real; fuente pre-packaging | `acta_revision.json` → `evidence_tier` vs `financial_scenarios_*.json` → `breakdown.evidence_tier` | Volver a `_read_evidence_tier` sobre `MANIFEST` en régimen ZIP-only → el acta dice `C` y el test rojo |
| **AC-F3** | P3-B | `test_barreda_un_solo_emisor_de_la_clave` verde con la whitelist **justificada** | test output | Quitar la autorización de `asset_reviewer` → rojo. La whitelist se documenta con el contrato de §5.1, no como `xfail` |
| **AC-F4** | P3-A | En `B_PLUS` el `reason` del primer piso explica por qué el veredicto es condicional | `acta_revision.json` → `first_floor_rule.reason` | Dejar `FIRST_FLOOR_TIERS` sin cubrir `B_PLUS` y verificar que el `reason` vuelve a mentir → rojo |
| **AC-F5** | P3-B | Con GA4+GSC disponibles, `HotelFinancialData` recibe las banderas reales y el tier puede ser `A` | `financial_scenarios_*.json` → `breakdown.evidence_tier` | Cuatro casos: A con analítica / `B_PLUS` sin ella / **sin `NameError` con `generate_proposal=False`** (amplía `test_s_e2_generate_proposal_false.py`) / delta NR1 con par pre/post |
| **AC-F6** | P3-B | `acta_writer.py` lee la versión de `VERSION.yaml` | `acta_revision.md` → footer `TribunalJudge vX.Y.Z` | Fijar la versión a mano en el writer → el test contra `VERSION.yaml` rojo |
| **AC-O0** | P4 | El informe declara el techo de tier **y a quién pertenece ese techo** (cableado ya arreglado por AC-F5 vs hotel sin analítica = T3b) | `evidence/FASE-P4/informe-observacion.md` → §Techo de tier | n/a (informe) |
| **AC-O1** | P4 | Corrida con el acta enriquecida y veredicto (provisionalidad registrada si algo de P2 sigue abierto) | `acta_revision.json` → `verdict` + `evidence_tier` + `reviewer_reports` | n/a (observación) |
| **AC-O2** | P4 | Informe con los 9 puntos del §5 del maestro, más el snapshot del baseline ajeno (L-B4) | `evidence/FASE-P4/informe-observacion.md` + `evidence/FASE-P4/baseline-predecesor/` | n/a |
| **AC-V1** | RELEASE | Patrón VERIFY ejecutado dentro de RELEASE: certificación de AC-E*/AC-F* contra artefacto de fase + los pares NR7, **sin exigir corrida P4** | matriz en `10-analisis-post-implementacion.md` | cada AC ya trae el suyo |

### 5.1 Contrato del segundo emisor de `asset_path` (justifica la whitelist de AC-F3)

`test_barreda_un_solo_emisor_de_la_clave` afirma que un solo módulo emite `"asset_path":`. Hoy emiten dos: `asset_generation/proposal_asset_alignment.py` y `quality_gates/tribunal/asset_reviewer.py`. **No es un falso positivo del test**: el test existe para impedir una segunda superficie del mismo hecho sin contrato. Contrato fijado aquí: **Bot 3 emite la ruta del artefacto tal como ya la resolvió el revisor (`report_path` del `ReviewerReport`), no un hecho nuevo sobre la producción del asset**; el emisor canónico de la ruta prometida sigue siendo `proposal_asset_alignment`. Con eso la whitelist de P3-B es un acto documentado y no una rendición.

---

## 6. Deuda de proceso: qué entra y qué queda como límite declarado

| Ítem | Disposición de P1 |
|------|-------------------|
| R2.6 / R2.7 sin verificador mecánico | **Fuera del alcance de código de este plan.** Quedan como límite declarado (L-R.4). R2.7 sí se cumple por método en P2/P3-A/P3-B: snapshot `pre` con `--ignore` de los tests propios y resta `suma_post − suma_pre == tests_nuevos` |
| Baseline R2.6 fuera del repo (`output/` en `.gitignore`) | **Límite declarado**, con causa verificada en `research-estado.md` §4. No se versiona fixture en este plan |
| Cobertura 1/8 de `validate_plan_closure.py` | **Límite declarado**; no toca los ACs de este plan |
| Campo `Version actual` del REGISTRY escrito a mano | **Límite declarado.** La cura es un writer, no un edit (regla de este repo); no es dueño de este plan |
| `validate_opencode_refs.py --fix` reescribe a ciegas | **Workaround vigente se mantiene** (plantilla `<PLAN>`) + revisión manual del diff post-archivado. Límite declarado |
| `version_consistency_checker.py` y `FASE-RELEASE-x.y.z` | **Límite declarado**, informativo |
| L-R.1 (columna `Iteraciones`) | **Aplicada**: la celda de P1 queda medida en `06-checklist` con unidad declarada (D-V2.1) |
| Normalizar el flaky de orden en R2.7 | **Condicional operativa**: el par pre/post de P2/P3 se declara con la **combinación exacta de archivos** y la lista de flaky conocidos (`test_function_default_flags`) nombrada en la evidencia |
| Tier A inalcanzable | **CERRADO por decisión**: Q5=(a) → AC-F5 + AC-F2 (DA-P1.8) |
| **"Verificador de conteos declarados en §4"** (llegó del plan PASO0 con premisa corregida) | **RETIRADO con evidencia**: el §4 de `00-lecciones-capitalizadas.md` declara 19 lecciones y el §2 tiene 19 filas (conteo manual en Tarea 1). No hay caso real en este plan → no se hereda ni se abre AC |

### 6.1 Resolución de §3.b de `00-lecciones-capitalizadas.md`

| Hallazgo | Resolución en P1 |
|----------|------------------|
| `D-T1.1` ("DEVOLVER-CORRECCIONES bloquea igual que BLOQUEADO; la política vive en un único punto") | **VIGENTE en código** (`BLOCKING_VERDICTS` incluye `VERDICT_RETURN`; único consumidor `blocks_delivery_zip`, llamado una vez). Por tanto AC-D1 **no define una consecuencia nueva**: registra la causa medida de no observación — `_compute_verdict` no recibía los hallazgos, así que el veredicto salió condicional por gates + primer piso. Capitalizado en DA-P1.1 |
| `L-SR3` (una sola fuente de verdad para el estado de un servicio) | **Aplica y se nombra**: es la causa estructural de AC-F2 (§3.1 de `research-estado.md`) y de la raíz común AC8↔AC-F2 de DA-P1.5. No es un detalle de lectura, es la razón por la que ambos lectores discrepan |
| `DA-C3` (`vacío ≠ ausente` como contrato) | **NR8/Q6 lo subsume**, con nombre: §4 de este documento y la regla 1 de DA-P1.6 (la sección nunca se omite). Fila añadida al `00-` |
| `L-B4` (dos planes comparten nombre de carpeta de evidencia) | **Confirmado**: `evidence/` es raíz global y P4 lee `evidence/FASE-E2E/`, `-VERIFY`, `-T1`, `-D` de otros planes. Cura fijada: **snapshot del baseline ajeno dentro de `evidence/FASE-P4/baseline-predecesor/`** → AC-O2. Solo produce efecto si P4 no se difiere |
| Cola de **78** adyacentes sin evaluar (Q7 del Paso 0) | **Fuera de alcance**, con razón: ninguno de los 78 toca los símbolos que este plan modifica (judge, acta, resolutor de entrega, bloque FASE-K), y la pasada no se hace por volumen sino por síntoma — los cinco hallazgos reales del corpus ya están capitalizados. Queda declarada en `10-analisis` como límite, no borrada |

---

## 7. Decisión FASE-VERIFY (§4.6) — **cerrada: NO activa**

| Criterio §4.6 | Evaluación con las decisiones de P1 |
|---------------|--------------------------------------|
| 1. ≥3 fases de implementación | **Sí**: P3-A, P3-B y P2 (Q1=sí). P4 no cuenta |
| 2. Al menos una fase con ejecución E2E | **No garantizable**: P4 depende de T3a, que es una precondición comercial externa (DA-P1.9). Atar la certificación del plan a que un hotel responda es convertir el cierre en un `—` indefinido |
| 3. ACs que cruzan fases | Sí: AC-E0 (P1→P2), AC-F2↔AC-F5 (P3-A↔P3-B), AC-O0 (P4 sobre lo que deje P3-B) |

**Decisión**: **no se crea sesión FASE-VERIFY propia**; el patrón VERIFY se ejecuta como **AC-V1 dentro de FASE-RELEASE**, con dos sustituciones explícitas que reemplazan lo que VERIFY habría aportado:

1. La certificación no depende de una corrida real sino del **par NR7 por AC** (verde/rojo), obligatorio en la evidencia de P2, P3-A y P3-B. Un AC sin su par queda `⚠️`, nunca `✅`.
2. Si P4 **llega** a ejecutarse (Q4 cierra con dato del hotel), su evidencia entra al matriz de AC-V1 y el informe responde los 9 puntos del §5 del maestro. Si no, AC-V1 certifica contra los artefactos de P2/P3-A/P3-B y **declara la ausencia de corrida como límite de esta decisión**, no como fallo.

Esta sección es el cierre del ítem; no se improvisa en RELEASE.

---

## 8. Plan de fases actualizado (lo que ejecuta cada una)

| Fase | Presupuesto | Hace | No hace |
|------|------------|------|---------|
| **P3-A** | 20 | AC-F1 (dos capas, raíz ZIP-aware), AC-F2 (fuente del tier pre-packaging), AC-F4 (razón del primer piso en `B_PLUS`). AC8 y AC-F2 se implementan como un mismo cambio de resolutor (DA-P1.5) | No toca `main.py` ni el orden del flujo |
| **P3-B** | 25 (Q5=a) | AC-F5 (hoist de banderas + test S-E2 ampliado), AC-F3 (whitelist barreda justificada por §5.1), AC-F6 (versión desde `VERSION.yaml`). CHANGELOG declara el cambio de tier | No decide el ordenamiento |
| **P2** | 55 | O1-cuarentena: partir `package()` en write/publish, `reviewer_reports` tipado y poblado, `_compute_verdict` con el cuarto argumento, AC-E0/E1/E2/E3/E4/E5, verificación de si el ZIP contiene el acta | No re-decide Q1b/Q2/Q5/Q6/Q7 (cerradas aquí); sin reintento automático |
| **P4** | 40, **opcional** | Corrida delegada según T3a; techo de tier declarado con su dueño (AC-O0); snapshot del baseline ajeno (AC-O2) | No es entrega a cliente. Diferible por §Cierre válido sin P4 |
| **RELEASE** | 30 | Cierre documental + 4.77.0 + **tag anotado** + AC-V1 (patrón VERIFY embebido) + archivado R2.5 | No abre sesión VERIFY propia |

**Orden de ejecución**: P3-A → P3-B → P2 → P4* → RELEASE. Nunca dos fases sobre `judge.py`/`main.py` en la misma sesión.

---

## 9. Versión

Objetivo **4.77.0** (confirmado). `AC-F6` en P3-B elimina la versión hardcodeada del acta; el bump se propaga por `sync_versions.py` y la fuente única sigue siendo `VERSION.yaml`.
