# 10 — Análisis Post-Implementación

> **Plan**: ESTABILIZACION-PRE-TRIBUNAL-2026-09-03
> **Estado**: 🟡 EN CURSO — archivo creado **desde la concepción** del plan (executor §4), no al final.
> **Propósito**: capitalizar la experiencia (lecciones), certificar los ACs contra evidencia real y dar
> trazabilidad de que los fixes del dossier fueron superados. Lo llena principalmente **FASE-VERIFY**.
> **Regla**: cada fase actualiza su fila de Resumen de Ejecución al cierre; VERIFY consolida el resto.

---

## 1. Resumen de Ejecución

> Una fila por fase. Se actualiza al cierre de cada sesión (Post-Ejecución punto 4).

| # | Fase | Objetivo | Complejidad | Modo | Iter (presup./usadas) | Estado | Notas |
|---|------|----------|-------------|------|----------------------|--------|-------|
| 1 | FASE-A | Fuente única identidad servicio↔asset↔pain | ALTA | DIRECTO | 55 / — | ⬜ Pendiente | |
| 2 | FASE-B | Biyección mapa↔emisión `detect_pains` | MEDIA-ALTA | DIRECTO | 40 / — | ⬜ Pendiente | |
| 3 | FASE-C | **Punto 8** propuesta dinámica | **MÁXIMA** | DIRECTO | 60 / — | ⬜ Pendiente | Punto de partición predefinido C1'/C2' si R2 se agota |
| 4 | FASE-D | Severidad 11 blocking + 2 advisory | MEDIA | MIXTO | 35 / — | ⬜ Pendiente | D3 documental delegable, mismo commit |
| 5 | FASE-E | A2 snapshot + A6 `asset_path` | MEDIA | DELEGADO | 30 / — | ⬜ Pendiente | 2 tracks paralelos |
| 6 | FASE-F | A4 oráculo único + A1 skipped≠passed + N11 | MEDIA-ALTA | DIRECTO | 45 / — | ⬜ Pendiente | |
| 7 | FASE-G | Ceguera de gates (Nivel 3.7) | MEDIA-ALTA | DIRECTO | 50 / — | ⬜ Pendiente | V5 anti-reversión BUG-6 |
| 8 | FASE-H | Quirúrgicos (Nivel 3.8) | BAJA-MEDIA | DELEGADO | 35 / — | ⬜ Pendiente | 2 subagentes, regiones distintas |
| 9 | FASE-I | E2E única `v4complete` Salento Real | BAJA | MIXTO | 25 / — | ⬜ Pendiente | 1 comando largo |
| 10 | FASE-VERIFY | Certificación + análisis post-implementación | MEDIA | DIRECTO | 40 / — | ⬜ Pendiente | No delegable (§4.6) |
| 11 | FASE-RELEASE-4.75.0 | Cierre documental | BAJA | DELEGABLE | 25 / — | ⬜ Pendiente | |

**Total presupuestado**: ≤440 iteraciones (R2 tope por fase: 60).

---

## 2. Verificación de Criterios de Aceptación (AC1-AC12)

> La llena **FASE-VERIFY** (V1). Regla de oro: certificar contra **salida real**, no contra la presencia de
> un string en el código (lección `revalidar-citas-de-c-digo-no-revalida-premisas`).

| AC | En una línea | Estado | Evidencia (archivo + campo + valor) | Test que lo fija | Fase |
|----|--------------|--------|-------------------------------------|------------------|------|
| AC1 | Una fuente canónica de identidad servicio↔asset↔pain | ⬜ | *(pendiente)* | *(pendiente)* | A |
| AC2 | Drift «8 vs 7» corregido en sus **tres** copias + contract test | ⬜ | *(pendiente)* | *(pendiente)* | A |
| AC3 | `ASSET_TO_PAIN_ID["monthly_report"]` resuelto a favor del registro canónico | ⬜ | *(pendiente)* | *(pendiente)* | A |
| AC4 | Biyección mapa↔emisión (9 pains muertos resueltos) | ⬜ | *(pendiente)* | *(pendiente)* | B |
| AC5 | Punto 8: `no_breach = 0` por construcción | ⬜ | *(pendiente)* | *(pendiente)* | C |
| AC6 | Tautología de coverage + `is_coherent` estructural disueltas | ⬜ | *(pendiente)* | *(pendiente)* | C+F |
| AC7 | Severidad 11 blocking + 2 advisory | ⬜ | *(pendiente)* | *(pendiente)* | D |
| AC8 | Advisory con piso explícito + WARNING a `human_checklist` | ⬜ | *(pendiente)* | *(pendiente)* | D |
| AC9 | A2 snapshot persistido + A6 `asset_path` poblado | ⬜ | *(pendiente)* | *(pendiente)* | E |
| AC10 | A4 oráculo único decide y escribe el mensaje | ⬜ | *(pendiente)* | *(pendiente)* | F |
| AC11 | A1 `skipped != passed` (`NOT_EVALUATED`) | ⬜ | *(pendiente)* | *(pendiente)* | F |
| AC12 | N11/P9 gate respeta `is_coherent` | ⬜ | *(pendiente)* | *(pendiente)* | F |

**Estados posibles**: ✅ CERTIFICADO · ⚠️ PARCIAL · ❌ NO CERTIFICADO. Todo ⚠️/❌ abre un seguimiento (§5).

---

## 3. Verificación de No-Regresión (NR7-NR12 — familia «de producto»)

> La llena **FASE-VERIFY** (V2) con delta medido contra el baseline `FASE-D_salentoreal_post_guard`.
> Hay **dos familias** de NRs: **NR1-NR6 «de hallazgo»** (doc_audit_consistency con datos, critical_issues,
> escotillas V5/V9, suite 848, perfil de corrida — definidas en `README.md` §ACs de no-regresión) y
> **NR7-NR12 «de producto»** (tabla siguiente — lo que el plan no debe romper). VERIFY certifica ambas.

| NR | En una línea | Baseline | Corrida I | Delta | Estado |
|----|--------------|----------|-----------|-------|--------|
| NR7 | Conteo de tests no regresó | 848 passed / 2 skipped | *(pendiente)* | *(pendiente)* | ⬜ |
| NR8 | `coherence` no cayó por causa del plan | 0.88 | *(pendiente)* | *(pendiente)* | ⬜ |
| NR9 | Los 13 gates siguen ejecutándose (11+2) | 13 | *(pendiente)* | *(pendiente)* | ⬜ |
| NR10 | ZIP de delivery sigue generándose | generado | *(pendiente)* | *(pendiente)* | ⬜ |
| NR11 | `asset_confidence` sigue blocking | blocking | *(pendiente)* | *(pendiente)* | ⬜ |
| NR12 | Sin nuevas anomalías vs baseline | — | *(pendiente)* | *(pendiente)* | ⬜ |

**Anomalías preexistentes** (NO cuentan como regresión): gemini 403, PageSpeed key inválida (V12),
cualquier otra que ya estuviera en el baseline. FASE-I las clasifica; VERIFY las confirma.

---

## 4. Fixes superados — análisis post-implementación

> **Petición literal del usuario**: *«análisis post implementación de que los diferentes fixes fueron
> superados»*. La llena **FASE-VERIFY** (V3). Una tabla por familia del dossier.

### 4.1 §9.1 — Huecos vivos A1-A6

| Hallazgo | Qué era | Estado final | Evidencia | Test que lo fija |
|----------|---------|--------------|-----------|------------------|
| A1 | `skipped` contaba como `passed` en delivery_quality_report (`:250-257`) | ⬜ | *(pendiente)* | *(pendiente)* |
| A2 | `site_presence_snapshot` nunca persistido en disco (0 resultados en historial) | ⬜ | *(pendiente)* | *(pendiente)* |
| A3 | `promised_assets_exist` solo pre-gen (`:670`), peso 2.0, `score=1.0` hardcode | ⬜ | *(pendiente)* | *(pendiente)* |
| A4 | Dos oráculos de presencia: permisivo decide, estricto escribe (V15) | ⬜ | *(pendiente)* | *(pendiente)* |
| A5 | Dos builders silenciosamente distintos; skip sin estado `NO_ASSET_MAPPED` | ⬜ | *(pendiente)* | *(pendiente)* |
| A6 | `asset_path = null` en entradas LINKED de proposal_asset_matrix | ⬜ | *(pendiente)* | *(pendiente)* |

### 4.2 §9.2 — Mecanismos del síntoma B1-B5

| Hallazgo | Qué era | Estado final | Evidencia | Test que lo fija |
|----------|---------|--------------|-----------|------------------|
| B1 | Matriz 7 servicios: 6 NO_BREACH + 1 LINKED; ledger resolved = 3 | ⬜ | *(pendiente)* | *(pendiente)* |
| B2 | Registro estático 7/7 vs runtime 4 assets; intersección {llms_txt} | ⬜ | *(pendiente)* | *(pendiente)* |
| B4 | Palancas de coverage 0.125-0.714; 7 permisivo = 0.571 | ⬜ | *(pendiente)* | *(pendiente)* |
| B5 | Δcoherence +0.0000 exacto; 2 candados (`score=1.0` + unión `:703`) | ⬜ | *(pendiente)* | *(pendiente)* |

### 4.3 §4 — 8 caídas silenciosas · §3 — 3 candados rotos

| Hallazgo | Qué era | Estado final | Evidencia | Test que lo fija |
|----------|---------|--------------|-----------|------------------|
| §4 caídas | 8 pains detectados que nunca llegan al ledger | ⬜ | *(pendiente)* | *(pendiente)* |
| §3 biyección | 0 tests fijan la biyección mapa↔emisión | ⬜ | *(pendiente)* | *(pendiente)* |
| §3 narrativa | Doc/propuesta venden lo no diagnosticado | ⬜ | *(pendiente)* | *(pendiente)* |
| §3 severidad | Estructura de severidad declarada ≠ implementada | ⬜ | *(pendiente)* | *(pendiente)* |

### 4.4 §12.3 — Validaciones externas V1-V16

| Hallazgo | Qué era | Estado final | Evidencia |
|----------|---------|--------------|-----------|
| V1 | 9 pains muertos (mapa declara 27, `detect_pains` ~18) | ⬜ | *(pendiente)* |
| V2 | 6 IDs fantasma en `ELEMENTO_KB_TO_PAIN_ID` | ⬜ | *(pendiente)* |
| V3 | ≥9 registros no canónicos | ⬜ | *(pendiente)* |
| V5 | `_JUSTIFIED_STATUSES` incluye `ASSET_GENERATED` (anti-reversión BUG-6) | ⬜ | *(pendiente)* |
| V6 | `except Exception: return brechas` + caché (`v4_diagnostic_generator.py:3189-3194`) | ⬜ | *(pendiente)* |
| V7 | Guard `__iter__` hace `low_ota_divergence` no-disparable (triple defecto) | ⬜ | *(pendiente)* |
| V8 | `low_organic_visibility` emitido dos veces | ⬜ | *(pendiente)* |
| V9 | `pain_ledger` vacío = PASS pero `pain_ledger_resolved` vacío = BLOCKED | ⬜ | *(pendiente)* |
| V10 | G8 «some below threshold» → WARNING → ZIP procede (confirmación, sin acción) | ➖ No aplica | Confirmado en FASE-G |
| V11 | Residuos D6 en `v4_diagnostic_generator.py:1952` y `v4_comprehensive.py:1841` | ⬜ | *(pendiente)* |
| V12 | `.env`: `GOOGLE_PAGESPEED_API_KEY` 3 chars inválido (trampa) | ➖ No aplica (OPS) | Documentado, `.env` no editado |
| V13 | Dos `MetadataValidator` gemelos | ⬜ | *(pendiente)* |
| V14 | Drift «8 vs 7» tercera copia en `v4_proposal_generator.py:1332` | ⬜ | *(pendiente)* |
| V15 | Matriz 6 NO_BREACH pero gate reporta 3 (`_presence_resolved` absorbió 3) | ⬜ | *(pendiente)* |
| V16 | `is_coherent: false` en 3 artefactos / 6 copias (`assets_are_justified 3/4 = 0.75`) | ⬜ | *(pendiente)* |

### 4.5 ROADMAP §13 — Deudas

| Deuda | Qué era | Estado final | Evidencia |
|-------|---------|--------------|-----------|
| P9 | Gate ignora `is_coherent` (la más grave) | ⬜ | *(pendiente)* — AC12 |
| P10 | Registros dispersos sin fuente única | ⬜ | *(pendiente)* — AC1 |
| P11 | `precision_tier` degrada a «C» en silencio | ➖ No aplica (diferido) | Seguimiento abierto |
| P12 | `promised_assets_exist` solo pre-gen | ⬜ | *(pendiente)* — A3 |
| H7 | Nombres timestamped + oráculo no persistido | ⬜ | *(pendiente)* — A2 |
| H8 | `publication_state.py` huérfano | ⬜ | *(pendiente)* — FASE-F |
| H9 | 3 rutas blocking + G9 green skip | ⬜ | *(pendiente)* — A1 |
| H10 | Docstrings 10+3 vs código 13 | ⬜ | *(pendiente)* — AC7 |

### 4.6 Veredicto global sobre la causa raíz §12.5

> *«contrato de detección fragmentado y sin candado — ≥9 registros no canónicos, consumidores derivan de
> copias parciales, 0 tests fijan la biyección»*

**Estado**: ⬜ Pendiente — VERIFY responde: ¿quedó la causa raíz fijada por contract tests (A + B) de modo
que no pueda volver a fragmentarse? Ese es el veredicto global del plan.

*(VERIFY redacta aquí el juicio final justificado con los contract tests de A y B y el guardián AST de B.)*

---

## 5. Seguimientos abiertos

> Temas detectados que requieren acción futura pero **no** bloquean el cierre del plan. Todo AC ⚠️/❌ y
> todo «No aplica — diferido» del §4 aterriza aquí con causa y próximo paso.

| # | Tema | Origen | Por qué se difiere | Próximo paso |
|---|------|--------|--------------------|--------------|
| S1 | Tribunal multi-bot | Fuera de alcance del plan | Plan paralelo anclado en P6 (memoria `plan-tribunal-bots-anclado-en-p6`) | Retomar tras estabilización |
| S2 | Premisa de brecha de analytics (57% de $4.04M/mes deriva de nuestra credencial faltante) | FASE-H V8 | V8 es solo dedup; reescribir la premisa excede el alcance | Evaluar en plan financiero |
| S3 | P11 `precision_tier` degrada a «C» | ROADMAP §13 | No es causa raíz del dossier | Plan de degradación silenciosa |
| S4 | `.env` placeholder inválido de PageSpeed | V12 | Decisión OPS, no de código | OPS: sembrar clave canónica |
| S5 | *(agregar los que abran VERIFY y las fases)* | | | |

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
| DA6 | *(agregar las que tomen las fases)* | | | |

---

## 7. Métricas de Ejecución

> Datos reales consolidados al cierre (VERIFY + RELEASE).

| Métrica | Valor |
|---------|-------|
| Fases completadas | 0 / 11 |
| Iteraciones totales usadas | *(pendiente)* / ≤440 |
| Tests al inicio | 3,689 (`def test_`) |
| Tests al cierre | *(pendiente)* |
| Contract tests agregados | *(pendiente)* |
| Versión publicada | 4.74.1 → *(4.75.0 al cierre)* |
| ACs certificados | 0 / 12 |
| NRs certificados | 0 / 12 |
| Hallazgos del dossier superados | 0 / (6+4+8/3+16+8) |
| Lecciones capitalizadas | *(pendiente)* |
| Coherence baseline → final | 0.88 → *(pendiente)* |

---

## 8. Lecciones Aprendidas

> **Petición literal del usuario**: *«lecciones aprendidas»*. La llena **FASE-VERIFY** (V4).
> Formato obligatorio: qué pasó / por qué / qué lo previene + pertinencia INCLUIR/EXCLUIR.
> Las INCLUIR se **proponen** al notebook QMind `iah-cli-lecciones` (el usuario confirma; no se auto-ingiere).

**L-{id} — {título}** *(plantilla — VERIFY la instancia)*
- **Qué pasó**:
- **Por qué**:
- **Qué lo previene**:
- **Pertinencia**: INCLUIR en {memoria/QMind} | EXCLUIR porque {razón}

*(VERIFY agrega ≥1 lección por fase con desviación o decisión no trivial. Mínimo esperado: orden A/B antes
que C, interacción C↔F, interacción C↔D, anti-reversión V5/BUG-6, degradación silenciosa como familia
común a V6/V7/P11/tier_c.)*

---

## 9. Write-back a QMind (pendiente de confirmación)

> Ciclo de capitalización v2.18.0 (memoria `ciclo-de-capitalizacion-de-lecciones-qmind-memory`).

| Lección | Notebook | Estado |
|---------|----------|--------|
| *(las INCLUIR de §8)* | `iah-cli-lecciones` | ⬜ Propuesto — el usuario confirma la ingestión |
