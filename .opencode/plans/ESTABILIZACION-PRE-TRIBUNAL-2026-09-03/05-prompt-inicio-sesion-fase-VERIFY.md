# FASE-VERIFY — Certificación formal + análisis post-implementación

**ID**: ESTABILIZACION-PRE-TRIBUNAL-2026-09-03 / FASE-VERIFY
**Objetivo**: Certificar **AC1-AC12** y **NR1-NR12** contra evidencia real (no contra citas de código),
y producir el **análisis post-implementación explícito de que los fixes fueron superados** + las
**lecciones aprendidas** que pidió el usuario.
**Dependencias**: FASE-I ✅ (y a través de ella, A-H ✅)
**Duración estimada**: 1.5-2 horas
**Complejidad técnica**: **MEDIA** — no se escribe código de producción; el trabajo es juicio,
triangulación de evidencia y redacción estructurada.
**Modo de ejecución**: **DIRECTO y NO delegable** (executor §4.6: requiere contexto completo del plan y
criterio transversal — un subagente no puede certificar lo que no vivió).
**Skill**: `phased_project_executor.md` v2.18.0 §4.6
**Presupuesto**: ≤40 iteraciones (R2 tope: 60) · **Comandos largos: 0**
**Salida**: `10-analisis-post-implementacion.md` completo (secciones §Verificación, §Fixes superados,
§Lecciones, §Métricas, §Seguimientos, §Decisiones) + `06-checklist-implementacion.md` con ACs/NRs marcados.

---

## Contexto

Esta fase es el **cierre de garantía** del plan. No agrega funcionalidad: **demuestra** que la que se
agregó funciona, sobre artefactos reales de la corrida FASE-I.

### Por qué VERIFY existe y es directa

El executor §4.6 activa FASE-VERIFY cuando se cumplen **las tres** condiciones — y este plan las cumple:

1. **≥3 fases de implementación** → son 8 (A-H).
2. **Ejecución E2E** → FASE-I (única corrida `v4complete`).
3. **ACs cross-fase** → AC5/AC6 atraviesan C+E+F; AC12 atraviesa C+F; NR1-NR12 atraviesan todo el plan.

Es **no delegable** porque certificar exige el contexto completo: un subagente que solo ve la corrida I
no puede juzgar si `no_breach = 0` es la cura del punto 8 (FASE-C) o un colapso accidental del oráculo
(FASE-F). Esa distinción **es** el trabajo de VERIFY.

### La regla de oro de esta fase

> **La verificación formal da falsa confianza** (lección ROADMAP v4.0→v4.1, memoria
> `revalidar-citas-de-c-digo-no-revalida-premisas`). Los validadores en verde verifican **forma**, no
> premisas. Revalidar que una cita de código sigue en su línea **no** revalida que el comportamiento
> cambió.

Por eso **cada AC se certifica contra una salida real** de `evidence/FASE-I/` o `evidence/FASE-*/`,
triangulada con el test que la fija. Un AC cuyo único respaldo es «el código dice X en la línea Y» se
marca **NO CERTIFICADO** aunque el string esté ahí.

---

## Tareas

### V1 — Certificar AC1-AC12 contra evidencia real

**Objetivo**: llenar la matriz §Verificación de `10-analisis-post-implementacion.md` con el estado de
cada AC, su evidencia concreta (archivo + campo + valor observado) y el test que lo fija.

**Archivos de entrada (evidencia, solo lectura)**:
- `evidence/FASE-I/` — la corrida real (fuente primaria de AC5, AC6, AC9, AC12)
- `evidence/FASE-A/` · `FASE-B/` · `FASE-C/` · `FASE-D/` · `FASE-E/` · `FASE-F/` · `FASE-G/` · `FASE-H/`
- `output/FASE-D_salentoreal_post_guard/v4_complete/` — **baseline** (solo lectura, para el delta)

**Archivos de salida**:
- `10-analisis-post-implementacion.md` §Verificación
- `06-checklist-implementacion.md` (tablas AC1-12 → ✅/❌)

**Los 12 ACs a certificar** (definición completa en `README.md` §ACs y en cada prompt de fase):

| AC | En una línea | Evidencia esperada en FASE-I | Fase dueña |
|----|--------------|------------------------------|------------|
| AC1 | Existe **una** fuente canónica de identidad servicio↔asset↔pain | Un único registro importado; grep de duplicados = 0 | A |
| AC2 | Drift «8 vs 7» corregido en sus **tres** copias + contract test | Ningún doc/string dice «8 servicios»; contract test narrativa↔fuente verde | A |
| AC3 | `ASSET_TO_PAIN_ID["monthly_report"]` resuelto a favor del registro canónico | test de contrato verde; `monthly_report` ya no apunta a `no_faq_schema` | A |
| AC4 | Biyección mapa↔emisión: cada pain del mapa o se emite o está justificado | test AST de biyección verde; 9 pains muertos resueltos | B |
| AC5 | **Punto 8**: la propuesta solo promete servicios con brecha detectada → `no_breach = 0` **por construcción** | `proposal_asset_matrix.json`: conteo NO_BREACH = 0 | C |
| AC6 | Disuelta la tautología de coverage y el `is_coherent = false` estructural | `coverage_ratio` ya no es 1.000 algebraico; `is_coherent: true` en los 3 artefactos (6 copias) que hoy lo declaran false | C (+F) |
| AC7 | Estructura de severidad: **11 blocking + 2 advisory** | `get_blocking_gates` devuelve 11; advisory = {content_quality, proposal_asset_alignment} | D |
| AC8 | Advisory tiene **piso explícito** + WARNING con consumidor nombrado (`human_checklist`) | WARNING de advisory aparece en `human_checklist.md` | D |
| AC9 | A2: `site_presence_snapshot` **persistido en disco** + A6: `asset_path` poblado | archivo snapshot existe en FASE-I; `asset_path != null` donde hay asset | E |
| AC10 | A4: **un único oráculo** de presencia decide y escribe el mensaje | no hay divergencia decisión/mensaje (V15 curado) | F |
| AC11 | A1: `skipped != passed` — gate no evaluado reporta `NOT_EVALUATED` | delivery_quality_report no suma skipped a passed_count | F |
| AC12 | N11/P9: el gate **respeta `is_coherent`** (no es ciego a él) | veredicto de publicación coherente con `is_coherent` del artefacto | F |

**Criterios de aceptación de V1**:
- [ ] Cada AC tiene una fila con: estado (✅ CERTIFICADO / ⚠️ PARCIAL / ❌ NO CERTIFICADO), evidencia
      concreta (archivo + campo + valor), test que lo fija, y fase dueña.
- [ ] Los ACs cuyo respaldo es solo «el string está en el código» se marcan **❌ NO CERTIFICADO** con la
      razón (regla de oro).
- [ ] AC5 y AC6 se certifican con el **valor numérico real** de la corrida I, no con el del test fixture.
- [ ] Todo AC ⚠️ o ❌ genera un **seguimiento abierto** en §Seguimientos (no se barre bajo la alfombra).

---

### V2 — Certificar NR1-NR12 (no-regresión)

**Objetivo**: demostrar que el plan **no rompió** lo que ya funcionaba, comparando la corrida I contra el
baseline `FASE-D_salentoreal_post_guard`.

> **Dos familias de NR** (corregido 2026-09-03 tras la auditoría del plan: antes había dos taxonomías
> NR1-NR6 incompatibles entre `README.md`/`06-checklist` y este archivo):
> - **NR1-NR6** («de hallazgo») — definidos en `README.md` §ACs de no-regresión; cubren los fixes de
>   FASE-G (doc_audit, critical_issues, escotillas V5/V9), el baseline de tests y la corrida I.
> - **NR7-NR12** («de producto») — la tabla de abajo; cubren no-regresión de entrega.

**Definiciones NR de producto (NR7-NR12)**:

| NR | En una línea | Cómo se certifica |
|----|--------------|-------------------|
| NR7 | No regresó el conteo de tests (≥ baseline 848 passed / 2 skipped en quality_gates+asset_generation) | `pytest` de las suites tocadas, conteo ≥ baseline |
| NR8 | `coherence` no cayó por debajo del baseline (0.88) **por causa del plan** | `coherence_validation.json` de I vs baseline |
| NR9 | Los 13 gates siguen ejecutándose (ahora 11+2), ninguno desapareció | `gate_report_*.json`: 13 resultados presentes |
| NR10 | El ZIP de delivery sigue generándose cuando corresponde | `deliveries/*.zip` presente si el régimen lo pide |
| NR11 | `asset_confidence` **sigue siendo blocking** (no se degradó a advisory) | estructura de severidad de D; V10 confirmado |
| NR12 | La corrida I no introdujo **nuevas** anomalías vs el baseline | clasificación de anomalías de I4 (FASE-I) |

**Criterios de aceptación de V2**:
- [ ] Cada NR tiene estado + delta medido (valor I vs valor baseline) + interpretación.
- [ ] Las anomalías **preexistentes** (gemini 403, PageSpeed key inválida, etc.) se clasifican como tales
      y **no** cuentan como regresión del plan (misma regla que FASE-D del plan anterior).
- [ ] NR11 se certifica explícitamente: `asset_confidence` NO está en el set advisory.

---

### V3 — Análisis post-implementación de que los fixes fueron superados

> **Esta tarea es la petición literal del usuario**: *«análisis post implementación de que los diferentes
> fixes fueron superados»*. Es el corazón de VERIFY.

**Objetivo**: por **cada hallazgo del dossier**, documentar el estado final (superado / parcial / no
aplica), la evidencia y qué test lo fija. El dossier enumeró:

- **§4** — 8 caídas silenciosas (pains detectados que nunca llegan al ledger)
- **§3** — 3 candados rotos (biyección, narrativa, severidad)
- **§9.1** — A1-A6 (seis huecos vivos)
- **§9.2** — B1-B5 (cinco mecanismos del síntoma)
- **§12.3** — V1-V16 (dieciséis validaciones externas)
- **ROADMAP §13** — deudas P9, P10, P11, P12, H7, H8, H9, H10

**Formato obligatorio de cada fila** (sección §Fixes superados de `10-analisis-post-implementacion.md`):

```
| Hallazgo | Qué era | Estado final | Evidencia | Test que lo fija |
|----------|---------|--------------|-----------|------------------|
| A1       | skipped contaba como passed en delivery_quality_report | ✅ Superado | gate_report FASE-I: G9 = NOT_EVALUATED | tests/.../test_skipped_not_passed.py |
```

**Reglas de V3**:
- **Todo** hallazgo del dossier aparece en la tabla — incluso los que se decidieron **no tocar** en este
  plan (tribunal, S2.3, octavo servicio, P11, `.env`). Esos van con estado **«No aplica — diferido»** y
  un puntero al seguimiento abierto correspondiente.
- Los estados posibles son exactamente: **✅ Superado**, **⚠️ Parcial**, **❌ No superado**,
  **➖ No aplica (diferido)**.
- Un hallazgo **⚠️ Parcial** o **❌ No superado** **obliga** a abrir un seguimiento con causa y próximo paso.
- La **causa raíz** del dossier (§12.5: *«contrato de detección fragmentado y sin candado — ≥9 registros
  no canónicos, consumidores derivan de copias parciales, 0 tests fijan la biyección»*) se evalúa **como
  un todo** al final de la tabla: ¿quedó fijada por contract tests? Ese es el veredicto global del plan.

**Criterios de aceptación de V3**:
- [ ] Las 6 familias del dossier (§4, §3, §9.1, §9.2, §12.3, ROADMAP §13) tienen su tabla completa.
- [ ] Ningún hallazgo queda sin estado.
- [ ] El veredicto global sobre la causa raíz §12.5 está escrito y justificado con los contract tests de
      A y B.
- [ ] Los «No aplica — diferido» coinciden exactamente con la lista «Lo que NO está en este plan» del
      `README.md` (consistencia interna del plan).

---

### V4 — Lecciones aprendidas + write-back a QMind

> **Segunda petición literal del usuario**: *«lecciones aprendidas»*.

**Objetivo**: capitalizar la experiencia del plan en formato duradero, y decidir qué se propaga a la
memoria del proyecto y al notebook QMind `iah-cli-lecciones`.

**Formato obligatorio de cada lección** (executor §4, sección 4 de `10-analisis-post-implementacion.md`):

```
**L-{id} — {título corto}**
- **Qué pasó**: {el hecho observable}
- **Por qué**: {la causa, no el síntoma}
- **Qué lo previene**: {el mecanismo: test, validador, regla de proceso}
- **Pertinencia**: INCLUIR en {memoria/QMind} | EXCLUIR porque {razón}
```

**Reglas de V4**:
- Las lecciones se extraen de **todo** el ciclo, no solo de FASE-I: decisiones de orden (fuente única
  antes que punto 8), interacciones entre fases (C↔F, C↔D), restricciones delicadas (V5/BUG-6
  anti-reversión), y lo que **no** funcionó.
- **Criterio de pertinencia** (memoria auto): una lección es durable si es **generalizable** más allá de
  este plan y **no derivable** del código actual. Si el fix ya vive en el código y el commit lo explica,
  la lección es **EXCLUIR** de memoria (no duplicar lo que `git log` ya dice).
- **Write-back a QMind** (ciclo de capitalización v2.18.0, memoria
  `ciclo-de-capitalizacion-de-lecciones-qmind-memory`): solo las lecciones marcadas **INCLUIR** se
  proponen al notebook `iah-cli-lecciones`. VERIFY **propone** el write-back; la ingestión la confirma el
  usuario (no se auto-ingiere).
- **Paso 0 inverso**: cada lección INCLUIR se redacta de forma que el próximo Paso 0 la recupere con
  keywords claras (mismo formato que las que se consumieron al concebir este plan).

**Criterios de aceptación de V4**:
- [ ] ≥1 lección por fase con desviación o decisión no trivial (mínimo esperado: orden A/B antes que C,
      interacción C↔F, anti-reversión V5, degradación silenciosa como familia).
- [ ] Cada lección tiene pertinencia explícita INCLUIR/EXCLUIR con razón.
- [ ] Las INCLUIR están redactadas en formato recuperable por Paso 0.
- [ ] Se lista (sin ejecutar) el write-back pendiente a QMind para confirmación del usuario.

---

## Tests Obligatorios

VERIFY **no escribe tests nuevos de producción** — los lee y los corre para certificar.

| Verificación | Comando | Criterio de éxito |
|--------------|---------|-------------------|
| Suites tocadas sin regresión | `./venv/Scripts/python.exe -m pytest tests/quality_gates tests/asset_generation -q > temp/verify_nr1.txt 2>&1` | ≥ baseline (848 passed / 2 skipped) |
| Contract tests de A y B | `./venv/Scripts/python.exe -m pytest tests/ -k "canonical_registry or bijection or contract" -q > temp/verify_ac124.txt 2>&1` | todos verdes |
| Validadores del ecosistema | `./venv/Scripts/python.exe scripts/run_all_validations.py --quick` | 4/4 (o 7/7 según versión) |

> **Seguridad pytest** (memoria `ejecuci-n-segura-de-suites-pytest-y-ramas-condicionales-en-i`): salidas a
> archivo en `temp/`, lotes pequeños, **NUNCA** la suite completa `tests/commercial_documents` (fuga ~8GB).
> Si un lote se cuelga, `taskkill` y reducir el chunk.

**Comando de validación de la fase**:
```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates tests/asset_generation -q > temp/verify_nr1.txt 2>&1
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️ — al finalizar VERIFY, antes de cerrar la sesión:

1. **`dependencias-fases.md`** — marcar VERIFY ✅ Completada + fecha.
2. **`README.md` del plan** — actualizar tabla de progreso (VERIFY ✅) y métricas.
3. **`09-documentacion-post-proyecto.md`** — **Sección C (E2E)**: volcar el resultado certificado de la
   corrida I (valores reales de AC5/AC6/AC9/AC12); **Sección D**: métricas acumulativas finales.
4. **`10-analisis-post-implementacion.md`** — **esta fase ES su contenido principal**: §Verificación,
   §Fixes superados, §Lecciones, §Métricas, §Seguimientos, §Decisiones deben quedar completos.
5. **`evidence/FASE-VERIFY/`** — copiar la matriz de certificación firmada + los `temp/verify_*.txt`
   (salidas de pytest y validadores que respaldan NR1).

**NO esperar a RELEASE para documentar.** RELEASE consume `09` y `10`; si VERIFY no los llena, RELEASE
genera CHANGELOG/GUIA_TECNICA vacíos.

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar VERIFY como ✅ COMPLETADA** ⚠️

- [ ] **AC1-AC12 certificados** contra evidencia real (no contra strings de código) — V1.
- [ ] **NR1-NR12 certificados** con delta medido vs baseline — V2.
- [ ] **§Fixes superados** cubre las 6 familias del dossier sin huecos — V3.
- [ ] **Veredicto global** sobre la causa raíz §12.5 escrito y justificado — V3.
- [ ] **≥1 lección por fase** con desviación, formato qué/porqué/previene + pertinencia — V4.
- [ ] Todo ⚠️/❌ tiene **seguimiento abierto** con causa y próximo paso.
- [ ] `pytest` de suites tocadas ≥ baseline (NR1) — salida en `evidence/FASE-VERIFY/`.
- [ ] `run_all_validations.py --quick` en verde.
- [ ] `09` y `10` actualizados (secciones C y D de 09; todas las de 10).
- [ ] `dependencias-fases.md` y `README.md` del plan al día.
- [ ] Write-back a QMind **listado** (no ejecutado) para confirmación del usuario.

**NO marcar VERIFY como completada si algún AC queda ❌ sin seguimiento abierto.**

---

## Restricciones

- **NO escribir código de producción.** Si VERIFY descubre un fix incompleto, lo documenta como ❌ +
  seguimiento; **no** lo parcha en esta fase (rompería la trazabilidad y el presupuesto).
- **NO re-ejecutar `v4complete`.** La corrida única fue FASE-I. VERIFY trabaja sobre `evidence/FASE-I/`.
- **NO delegar.** §4.6 es explícito: certificación requiere contexto completo del plan.
- **NO auto-ingerir a QMind.** VERIFY propone; el usuario confirma.
- **Baseline de solo lectura.** `output/FASE-D_salentoreal_post_guard/` no se modifica.

---

## Prompt de Ejecución

```
Actúa como verificador formal del plan ESTABILIZACION-PRE-TRIBUNAL-2026-09-03.

OBJETIVO: certificar que los fixes fueron superados sobre evidencia real y capitalizar lecciones.

CONTEXTO:
- 8 fases de implementación (A-H) + 1 corrida E2E (FASE-I) completadas.
- Evidencia en evidence/FASE-I/ (corrida real) y evidence/FASE-{A..H}/.
- Baseline de solo lectura: output/FASE-D_salentoreal_post_guard/v4_complete/ (coherence 0.88, 13 gates, 2026-08-31 12:28).
- REGLA DE ORO: los validadores en verde verifican forma, no premisas. Cada AC se certifica contra una
  salida real, no contra la presencia de un string en el código.

TAREAS:
1. V1 — Certificar AC1-AC12: estado + evidencia (archivo+campo+valor) + test que lo fija.
2. V2 — Certificar NR1-NR12: delta medido I vs baseline; anomalías preexistentes NO son regresión.
3. V3 — Tabla §Fixes superados por cada hallazgo del dossier (§4, §3, §9.1 A1-A6, §9.2 B1-B5,
   §12.3 V1-V16, ROADMAP §13 P9/P10/P11/P12/H7/H8/H9/H10) + veredicto global sobre la causa raíz §12.5.
4. V4 — Lecciones (qué pasó/por qué/qué lo previene + pertinencia INCLUIR/EXCLUIR) y write-back a
   QMind iah-cli-lecciones LISTADO para confirmación.

SALIDA: 10-analisis-post-implementacion.md completo + 06-checklist con ACs/NRs marcados + evidence/FASE-VERIFY/.

RESTRICCIONES:
- NO escribir código de producción; NO re-ejecutar v4complete; NO delegar; NO auto-ingerir a QMind.
- Todo AC ⚠️/❌ abre un seguimiento con causa y próximo paso.

VALIDACIONES:
- pytest tests/quality_gates tests/asset_generation -q  (≥ baseline 848/2)
- run_all_validations.py --quick  (verde)
```
