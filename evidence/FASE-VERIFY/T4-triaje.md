# T4 — Triaje de Seguimientos Abiertos + Lecciones Aprendidas

> Fecha: 2026-09-15
> Modo: DIRECTO (sin delegación)
> Fuente: Seguimientos Abiertos en `10-analisis-post-implementacion.md` + hallazgos de T2/T3

---

## Triaje en 3 Categorías

### Categoría A: Bloquea RELEASE

| # | Seguimiento | Por qué bloquea | Dueño | AC asociado |
|---|-------------|-----------------|-------|-------------|
| — | *(ninguno)* | — | — | — |

**Justificación**: AC-S4 (puerta de publicación) ya tiene resolución técnica verificable: la key pública fue rotada (está invalidada en origin). La prevención complementaria (`_save_cache` redacción en `google_places_client.py`) es deuda técnica menor, no bloqueante. El tag 4.77.0 puede proceder sin esperar al operador.

---

### Categoría B: Se documenta como límite

| # | Seguimiento | Límite que declara | Fase que lo hereda |
|---|-------------|--------------------|--------------------|
| B1 | Tier A no observado | El pipeline no volvió a correrse desde P5; P6/P6-R certificaron offline. Tier A requiere GA4+GSC del hotel (T3b, precondición externa) | RELEASE lo declara en CHANGELOG y AGENTS.md |
| B2 | Contrafactual del enforcement no observado | Gates bloquearon antes que los revisores en la única corrida real (P4/Don Alfonso). La rama "gates aprueban + revisor objeta" solo existe en tests NR7, no en corrida real | RELEASE lo declara como límite de certificación |
| B3 | P6.2/P6.5 cláusulas dicen NOT_EVALUABLE pero revisores corrieron | Las cláusulas del acta no se actualizan post-enforcement; el veredicto sí consume los 4 reportes correctamente. Límite de fidelidad clause→verdict | Conocido; no requiere acción |
| B4 | Matriz offline ≠ confianza estadística (L-P6.3) | Los ≥3 perfiles de AC-G4 prueban lógica de cableado, no validez para hotel concreto | La certificación contra datos reales sigue siendo P4 |
| B5 | `analytics_status.gsc_available` sin asignar en `v4complete` | El pipeline no consume datos GSC; poner la bandera sin consumir el dato produciría afirmación falsa | Plan de analítica sucesor (T3b) |

---

### Categoría C: Va a plan sucesor

| # | Seguimiento | Dueño propuesto | Prioridad | Origen |
|---|-------------|-----------------|-----------|--------|
| C1 | `google_places_client.py:_save_cache` sin redacción de secretos | Plan de seguridad sucesor | Media | T2 cruce P5×todo |
| C2 | F-P4.2: doble conteo Bot 2/Bot 4 (mismo hecho, dos CRITICAL) | Plan de analítica o RELEASE si se abre AC | Baja | P4 informe §3 |
| C3 | F-P4.4: `ia_readiness_report.json` deja de escribirse | Plan sucesor | Baja | P4 informe §3 |
| C4 | F-P4.6: deriva de provider (DeepSeek→Gemini) | Observacional, sin acción | Baja | P4 informe §3 |
| C5 | F-P4.8: baseline excluido de git, solo hashes durables | Plan sucesor si se requiere reproducibilidad | Baja | P4 informe §3 |
| C6 | Inventario grandfathered de material de cliente (`donalfonsohotel_onboarding.yaml` + blobs `evidence/FASE-I/`) | Operador (AC-S4 puerta de publicación) | Media | P5 remediación |
| C7 | Rama local `backup/pre-sanidad-evidence-20260912` | Operador (confirmar que nada la referencia → podar) | Baja | Higiene git |
| C8 | Corrección documental: docs del plan mencionan `GATE_ENFORCEMENT_ENABLED` pero código solo tiene `GATE_BLOCKING_ENABLED` | RELEASE (cambio en CHANGELOG/AGENTS.md) | Alta | T3 Grep 1 / CON-1 |
| C9 | Cola de 78 adyacentes sin evaluar (Q7 Paso 0) | Fuera de alcance declarado en P1 | N/A | P1 §6.1 |

---

## Lecciones Aprendidas de FASE-VERIFY (≥3)

### L-VERIFY.1 — La documentación puede afirmar dos interruptores cuando el código tiene uno

**Pasó**: Los documentos del plan (D-AJUST.4, `01-plan-maestro.md`) mencionan `GATE_BLOCKING_ENABLED` y `GATE_ENFORCEMENT_ENABLED` como dos llaves del bloqueo. Medido con grep: solo `GATE_BLOCKING_ENABLED` existe en código de producción. DA-P1.7 había decidido correctamente "un solo botón", pero la documentación posterior no se actualizó.

**Por qué**: La documentación se escribió en sesiones distintas (P1, D-AJUST.4) y ninguna contra-verificó los nombres de variables contra el código. Es L-P1.2 aplicada a documentos de plan en vez de docstrings.

**Cura**: Todo documento que nombre un símbolo de código debe verificar su existencia con grep antes de publicarlo. Sin verificador mecánico → declarada (L-R.4).

**Pertinencia**: INCLUIR — aplicable a todo plan largo con múltiples sesiones de decisión.

---

### L-VERIFY.2 — Los campos DTO no son campos JSON serializados

**Pasó**: La matriz de certificación T1 buscaba `blocks_publish` en el acta JSON (`actaRevision.json`) y no lo encontró. El campo existe en `TribunalOutcome` (outcome.py L153) como atributo del DTO, pero `acta_writer.py` no lo serializa. El acta comunica el bloqueo via `verdict` y `enforcement`, no via `blocks_publish`.

**Por qué**: La distinción entre "campo del modelo interno" y "campo del artefacto publicado" no estaba explícita en los documentos del plan. Un certificador que lee el plan puede esperar encontrar en el JSON todo lo que existe en el DTO.

**Cura**: Al citar un campo como evidencia, verificar que el writer lo serializa (grep en `acta_writer.py`), no solo que el DTO lo declara. La matriz de certificación debe distinguir "campo DTO" de "clave JSON".

**Pertinencia**: INCLUIR — aplicable a todo sistema con modelo interno + artefacto publicado.

---

### L-VERIFY.3 — La certificación cross-fase revela gaps que la certificación por fase no ve

**Pasó**: El cruce P5×todo (T2) reveló que `google_places_client.py:_save_cache` persiste caché sin redacción de secretos, mientras `gbp_auditor.py:_save_cache` sí redacta. P5 había certificado AC-S2 (checker de secretos) y AC-S4 (inventario), pero ninguno cubría la redacción en cachés de scrapers. El gap solo se hizo visible al cruzar la ruta de delivery completa.

**Por qué**: Cada fase certifica sus ACs en aislamiento. P5 miró el checker de secretos (pre-commit) y el inventario de superficie pública, pero no auditó todos los `_save_cache` del sistema. La integración cross-fase es el único momento que puede ver "¿hay otro writer que persista datos sensibles sin redacción?"

**Cura**: FASE-VERIFY debe incluir siempre un cruce de integración que audite la ruta completa de datos, no solo los ACs individuales. Este hallazgo (C1) va a plan sucesor con prioridad media.

**Pertinencia**: INCLUIR — es la razón de ser de FASE-VERIFY (§4.6 del executor).

---

### L-VERIFY.4 — Las cláusulas del acta no se actualizan post-enforcement

**Pasó**: El acta de Don Alfonso muestra cláusulas P6.2 y P6.5 con estado `NOT_EVALUABLE`, pero los revisores de esos cláusulas (Bot 2 alignment, Bot 4 honesty) sí corrieron y produjeron hallazgos (`OK_WITH_FINDINGS`, `BLOQUEAR`). El veredicto final (`BLOQUEADO`) consume correctamente los 4 reportes, pero las cláusulas individuales no reflejan que los revisores evaluaron.

**Por qué**: DA-P2.4 decidió que la fila 4 de la matriz se implementa como guard del veredicto, no como mutación de la cláusula. Esto preserva la fidelidad de los gates (que sí se evaluaron y pasaron), pero deja las cláusulas de revisores en `NOT_EVALUABLE` incluso cuando los revisores corrieron. Es una limitación de diseño, no un bug.

**Cura**: Documentar como límite conocido (B3). Si se requiere fidelidad clause→verdict completa, el sucesor debe decidir si las cláusulas de revisores se actualizan post-enforcement o si el veredicto basta como fuente de verdad.

**Pertinencia**: INCLUIR — es la tensión entre "preservar la verdad del gate" y "preservar la verdad del revisor".

---

## Resumen Ejecutivo

| Categoría | Cantidad | Acción |
|-----------|----------|--------|
| A — Bloquea RELEASE | 0 | RELEASE puede proceder |
| B — Límite declarado | 5 | RELEASE los documenta en CHANGELOG |
| C — Plan sucesor | 9 | Se registran con dueño y prioridad |

**Lecciones aprendidas**: 4 (L-VERIFY.1 a L-VERIFY.4), todas marcadas INCLUIR.

**Hallazgos CON de la matriz T1**: 2 (CON-1: dos interruptores vs uno; CON-2: cláusulas NOT_EVALUABLE post-enforcement). Ambos documentados en B3/C8 y en las lecciones.

**Hallazgos incoherentes de T2/T3**: 2 (cruce P5×todo: `_save_cache` sin redacción; Grep 5: mismo hallazgo). Va a C1.

**Estado final**: FASE-VERIFY puede cerrar con ✅. Ningún bloqueante para RELEASE.
