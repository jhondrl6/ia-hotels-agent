# Análisis Post-Implementación — TRIBUNAL-OFFLINE-2026-09-09

> **Estado**: 🔶 1/9 sesiones ejecutadas — FASE-T1 ⚠️ completada con reserva (auditada y corregida el 2026-09-10)
> **Plan**: TRIBUNAL-OFFLINE-2026-09-09
> **Versión objetivo**: 4.76.0

---

## Resumen de Ejecución (llenar al cierre de cada fase)

| Fase | Sesión | Estado | Iteraciones | delegate_task | Notas |
|------|--------|--------|-------------|---------------|-------|
| FASE-T1 | 2026-09-10 | ✅ | ⚠️ sin medir (R2.1) | No | Juez + contrato de acta + integración main.py; auditada y corregida D-T1.1/D-T1.2 el mismo día |
| FASE-T2-A | — | ⬜ | — | No | Bot 1: Diagnóstico (DIRECTO: tests importan el proyecto) |
| FASE-T2-B | — | ⬜ | — | No | Bot 3: Assets (DIRECTO) |
| FASE-T2-C | — | ⬜ | — | No | Limpieza S-E2/S9 (DIRECTO: toca `main.py`) |
| FASE-T4-A | — | ⬜ | — | No | Bot 2: Alineación NL + interfaz LLM |
| FASE-T4-B | — | ⬜ | — | No | Bot 4: Honestidad NL (DIRECTO) |
| FASE-E2E | — | ⬜ | — | Sí (v4complete) | Corrida Salento Real |
| FASE-VERIFY | — | ⬜ | — | No | Certificación AC1-AC16 |
| FASE-RELEASE-4.76.0 | — | ⬜ | — | Sí | Cierre + archivado |

---

## Matriz de Verificación de Hallazgos (llenar en FASE-VERIFY)

| # | AC | Expected | Real | Status | Artefacto | Clave |
|---|-----|----------|------|--------|-----------|-------|
| 1 | AC1 | `acta_revision.json` con `verdict` legible | — | ⬜ | `v4_audit/acta_revision.json` | `verdict` |
| 2 | AC2 | Tier B/C → condicional | — | ⬜ | `acta_revision.json` | `verdict` + `evidence_tier` |
| 3 | AC3 | `acta_revision.md` con 6 cláusulas P6 | — | ⬜ | `acta_revision.md` | secciones |
| 4 | AC4 | Una ruta de bloqueo, no cuarta | — | ⬜ | `main.py` | grep tribunal |
| 5 | AC5 | `revision_diagnostico.json` con `findings[]` | — | ⬜ | `revision_diagnostico.json` | `findings` |
| 6 | AC6 | Recall vacuo marcado | — | ⬜ | `revision_diagnostico.json` | `VACUOUS_RECALL` |
| 7 | AC7 | `revision_assets.json` con `coverage_by_service[]` | — | ⬜ | `revision_assets.json` | `coverage_by_service` |
| 8 | AC8 | `IMPLEMENTATION_ORDER.md` vacío señalado | — | ⬜ | `revision_assets.json` | `EMPTY_DELIVERY_TEMPLATE` |
| 9 | AC9 | `revision_alineacion.json` con `service_matrix[]` | — | ⬜ | `revision_alineacion.json` | `service_matrix` |
| 10 | AC10 | Promesa sin matriz → `PROMESA-SIN-MATRIZ` | — | ⬜ | test output | assertion |
| 11 | AC11 | `revision_honestidad.json` con `findings[]` | — | ⬜ | `revision_honestidad.json` | `findings` |
| 12 | AC12 | CG-WHATSAPP-LEAD detectado | — | ⬜ | `revision_honestidad.json` | `cg_reference` |
| 13 | AC13 | Acta + 6 cláusulas en output E2E | — | ⬜ | `acta_revision.json` | `clauses_evaluated` |
| 14 | AC14 | 4 reportes de revisión en `v4_audit/` | — | ⬜ | directorio | 4 archivos |
| 15 | AC15 | S-E2: `generate_proposal=False` sin NameError | — | ⬜ | sonda/test output | assertion |
| 16 | AC16 | S9: `INVALID_MAPPINGS` pasa contrato | — | ⬜ | test output | assertion |

---

## Lecciones Aprendidas

### Lecciones capitalizadas de planes anteriores

| Lección | Fuente | Aplicación en este plan |
|---------|--------|------------------------|
| R2.2: Sin números de línea — citar símbolos | ESTABILIZACION §14.3 | Todos los ACs citan artefacto+clave, nunca `archivo:123` |
| R2.4: AC no legible en artefacto = ⚠️ | ESTABILIZACION §14.3 | Cada AC declara artefacto + clave; tests de serialización obligatorios |
| Contrato de acta estable ANTES de revisores | CONTEXT §10.3 (regla de dependencia fina) | T1 define contrato; T2/T4 lo consumen |
| Anfitrión real = `main.py`, NO `two_phase_flow.py` | CONTEXT §15.4.3 | T1 integra en `main.py` junto a `delivery_quality_report` |
| Veredicto alimenta UNA ruta de bloqueo existente | CONTEXT §15.4.3 / ROADMAP §7.2 | AC4 verifica que no se añade cuarta ruta |
| El tribunal NO reimplementa gates | CONTEXT §5 (regla arquitectónica) | NR4: grep verifica que no importa internals de `publication_gates.py` |
| Propuesta dinámica ya cerrada (v4.75.0) | CONTEXT §14.1 | T0 no está en scope; baseline es propuesta dinámica activa |
| Residuos S-HF1/S-I1/P12/S-C4 son alcance, no sorpresa | CONTEXT §15.4.9 | Distribuidos en T1/T2-A/T2-B/T4-A explícitamente |

### Lecciones nuevas de este plan (llenar mínimo 3 por fase)

#### FASE-T1 (2026-09-10)

| # | Lección | Fuente | Aplicación futura |
|---|---------|--------|-------------------|
| L-T1.1 | `proposal_asset_matrix.json` tiene formato v2.0 (`delivery_ready` + `entries[]`) distinto al formato legacy (`alignment.passed`). El Juez debe manejar ambos formatos para ser retro-compatible con corridas pre y post-hotfix. | Artefactos FASE-I vs FASE-D | T2-B (asset_reviewer) debe usar `delivery_ready` como fuente primaria, no `alignment.passed` |
| L-T1.2 | ⚠️ **Corregida en la auditoría.** La resolución por glob funciona sin hardcodear timestamps, pero los tests retro **solo ejercen la corrida FASE-I**: `FASE_D_DELIVERIES_DIR` está definido en `test_judge.py` y nunca se usa, así que el baseline FASE-D (Tier B real, `MANIFEST.json → quality_metadata.evidence_tier`) no está cubierto. Además `sorted(glob(), key=mtime, reverse=True)[0]` **no es reproducible**: `git checkout`, copias o restauraciones cambian el `mtime`. La fecha ya va embebida en el nombre (`gate_report_YYYYMMDD_HHMMSS.json`). | Releído `judge.py` + `test_judge.py` el 2026-09-10 | T2-B y T4-B deben ordenar por la fecha del nombre, no por `mtime`; ver seguimiento abierto |
| L-T1.3 | La integración never-block (try/except que produce `acta = None`) es correcta: el tribunal no puede romper v4complete. Los veredictos negativos alimentan la Ruta 2 existente sin añadir una cuarta ruta. | Diseño de T2-A/T2-B (revisores también never-block) | Todos los revisores deben ser never-block; el Juez consolida sus outputs |
| L-T1.4 | ⚠️ **Corregida en la auditoría.** En T1 solo **P6.2** queda `NOT_EVALUABLE` (requiere LLM y se difiere a T4-A). **P6.5 no**: el Juez la evalúa de forma determinista como regla de primer piso contra `MANIFEST.json`, y devuelve `PASS` (Tier A) o `ADVISORY` (Tier B/C). El contrato de acta exige que un revisor declare su `clause` antes de escribir sobre ella. | Releído `_evaluate_p6_5` contra `05-prompt-...-T4-B.md` | **Colisión de ID**: T1 define P6.5 = primer piso, pero README/09/T4-B asignan P6.5 = honestidad NL. Ver D-T1.3 |

### Decisiones de contrato — auditoría FASE-T1 (2026-09-10)

Dos desvíos de diseño detectados al auditar T1 contra el plan, ya corregidos, más una colisión de contrato abierta que requiere decisión antes de T4-B. Todos se registran aquí porque afectan al contrato que T2/T4 consumen (RESTRICCIÓN de Tarea 4).

| # | Decisión | Símbolo afectado | Regla antes → después |
|---|--------|------------------|----------------------|
| **D-T1.1** | `DEVOLVER-CORRECCIONES` bloquea el ZIP igual que `BLOQUEADO`. Antes solo `BLOQUEADO` interceptaba, así un acta que devuelve el paquete por assets fallidos se entregaba igual. La política vive en un único punto (`BLOCKING_VERDICTS` / `blocks_delivery_zip()` en `judge.py`), exportada por `__init__.py` y consumida por `main.py` en lugar de comparar strings de veredicto en el llamador. | `blocks_delivery_zip`, `BLOCKING_VERDICTS` | 1 de 2 veredictos negativos bloqueaba → ambos bloquean |
| **D-T1.2** | Sin evidencia certificable no hay veredicto máximo. `APROBADO-PARA-ENTREGA` exige Tier **A** y que todas las cláusulas certificables de T1 estén en `PASS`; un `NOT_EVALUABLE` (artefacto ausente, p. ej. borrado por gate-blocking) degrada a condicional en vez de contar como no-bloqueante. `P6.2` queda exenta porque el plan la difiere a T4-A. | `T1_CERTIFIABLE_CLAUSES`, `_compute_verdict` | 0 artefactos + Tier A certificaba entrega → degrada a condicional |
| **D-T1.3** ⚠️ | **Abierta — requiere decisión antes de FASE-T4-B.** `P6.5` está asignada a dos cláusulas distintas dentro del mismo plan. `05-prompt-...-T1.md` y `CONTEXT-BOTS` §5 (línea 148) la definen como *regla de primer piso* (determinista, dueño Juez); `README.md`, `09-documentacion-post-proyecto.md` y `05-prompt-...-T4-B.md` la definen como *honestidad NL* (dueño Bot 4, cuyo `revision_honestidad.json` declara `"clause": "P6.5"`). T1 ocupó el slot del primer piso, así que cuando T4-B escriba sobre `P6.5` pisará la cláusula del Juez. Opciones: (a) el primer piso deja de ser cláusula y queda solo en la clave top-level `first_floor_rule`, liberando `P6.5` para Bot 4; (b) se renumera honestidad y AC3 / AC13 / `test_acta_md_has_six_clauses` se ajustan. | `T1_CERTIFIABLE_CLAUSES`, contrato de acta, AC3, AC13 | pendiente — ninguna opción aplica todavía |

**Verificado**: 17/17 tests de `tests/quality_gates/tribunal/` verdes (4 nuevos fijan D-T1.1 y D-T1.2); `3944 → 3961` colectados; `run_all_validations.py --quick` 8/8 PASS. Los 7 fallos preexistentes en `tests/test_never_block_architecture/test_never_block_integration.py` (`AssetContentValidator`, `PreflightChecker`) son ajenos a este plan: no importan ni `main.py` ni el tribunal.

**Pendiente**: D-T1.3 sin resolver. Además `modules/quality_gates/tribunal/` y la integración en `main.py` **no están commiteados**, así que a T1 le falta el corte en commit de código que exige R2.1.

---

## Seguimientos abiertos

| Tema | Estado | Acción futura |
|------|--------|---------------|
| T3 (onboarding datos reales) | Fuera de alcance | Plan separado cuando hotel entregue datos |
| T5 (deploy FTP/WP) | Fuera de alcance | Plan separado cuando haya credenciales + staging |
| T6 (throughput + gancho) | Fuera de alcance | Plan separado sobre T3+T5 cerrados |
| S-V10 (banda de palancas) | No re-medible con una corrida | Exige corpus ≥3 hoteles |
| S-E2 (NameError latente) | **En alcance** | FASE-T2-C (dueño tribunal por VERIFY) |
| S9 (`INVALID_MAPPINGS`) | **En alcance** | FASE-T2-C (dueño tribunal por VERIFY) |
| S-H2 (performance pain) | Fuera de alcance | Requiere decisión de producto previa |
| Lista blanca del ZIP (deuda P6) | Acta viaja al ZIP | Verificar en E2E que `delivery_packager.py` no excluye `acta_revision.*` |
| **D-T1.3** colisión de ID `P6.5` | ⚠️ **Abierta, bloquea T4-B** | Decidir antes de que `honesty_reviewer.py` escriba `"clause": "P6.5"` sobre la cláusula del Juez |
| **S-HF1** (criterio de narración `total_services`) | ⚠️ **Documentación contradictoria** | `decision-integracion.md` cita `alignment.promised_services_total`, que no existe en ningún artefacto real (en FASE-I `alignment` es `null`); `baseline-pre-post.md` y el código usan `summary.promised`. Además `total_services` no aparece en ningún archivo del tribunal. Unificar en `decision-integracion.md` |
| Resolución de artefactos por `mtime` | ⚠️ **No reproducible** | `_resolve_artifact` / `_resolve_manifest` ordenan por `st_mtime`; `git checkout` o una copia cambian el veredicto. Ordenar por la fecha embebida en el nombre |
| Baseline FASE-D sin cubrir en tests | ⚠️ **Deuda de test** | `FASE_D_DELIVERIES_DIR` en `test_judge.py` está definido y sin usar; conéctalo al `MANIFEST.json` real (Tier B) para validar retro contra las dos corridas |
| Versión hardcodeada en el acta | ⚠️ **Viola fuente única de versión** | `acta_writer.py` imprime `v4.76.0` con `VERSION.yaml = 4.75.0`; leer de `VERSION.yaml` o quitar el número |
| Citas de línea en `decision-integracion.md` | ⚠️ **R2.2 + ya obsoletas** | `L2997/L3217/L3293` eran exactas contra `HEAD` pre-T1; tras la integración `main.py` pasó de 3.901 a 3.933 líneas y L3217/L3293 ya no apuntan a nada. Reemplazar por símbolos |

---

## Métricas de Ejecución (llenar al cierre)

| Métrica | Valor |
|---------|-------|
| Tests pre-plan (baseline v4.75.0) | 3.934 funciones / 298 archivos |
| Tests nuevos del tribunal | 17 (13 de T1 + 4 de la auditoría) — `3944 → 3961` colectados |
| Tests totales post-plan | — |
| Coherence output E2E | — |
| Veredicto del Juez | — |
| Iteraciones totales (8 fases) | ⚠️ T1 sin medir (`evidence/FASE-D/measure_iterations.py` no ejecutado) |
| Fases con delegate_task | — |

---

## Decisiones Arquitectónicas

| ID | Decisión | Rationale | Alternativas rechazadas | Fase |
|----|----------|-----------|------------------------|------|
| DA-T1 | Anfitrión del tribunal = `main.py` junto a `delivery_quality_report` | Es donde hoy se decide el ZIP; `two_phase_flow.py` es huérfano | `two_phase_flow.py` (sin llamador de producción), módulo independiente (drift) | T1 |
| DA-T1 | Veredicto alimenta UNA de las tres rutas de bloqueo existentes | No añadir complejidad; el kill switch `GATE_BLOCKING_ENABLED` ya gobierna | Cuarta ruta propia (aísla el tribunal del flujo existente) | T1 |
| D-T1.1 / D-T1.2 / D-T1.3 | **Revisan la matriz findings → veredicto y la política ZIP.** Ver §Decisiones de contrato — auditoría FASE-T1; D-T1.3 queda abierta | La redacción original de T1 permitía certificar entrega sin evidencia y entregar paquetes devueltos por correcciones | Conservar la regla original (deja el acta sin efecto bloqueante real) | T1 |
| DA-T4 | LLM solo extrae; Juez aplica veredicto determinista | Preserva auditabilidad P3; LLM nunca es juez de registro | LLM como juez (no determinista, no testeable con pytest) | T4-A |

---

## Checklist de Cierre (llenar en FASE-RELEASE)

- [ ] Todas las fases ✅ en `06-checklist-implementacion.md`
- [ ] AC1-AC16 certificados en FASE-VERIFY
- [ ] NR1-NR5 sin violaciones
- [ ] CHANGELOG.md entrada [4.76.0]
- [ ] GUIA_TECNICA.md nota técnica
- [ ] VERSION.yaml = 4.76.0
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Plan archivado en `Archives/` (R2.5)
- [ ] `10-analisis-post-implementacion.md` completo
- [ ] Lecciones INCLUIR persistidas en memoria del proyecto
- [ ] QMind: write-back del 10-analisis — patrón local (`QMIND-WRITE-BACK.md` en `.opencode/context/`) + ingesta manual a `iah-cli-lecciones` (paso del agente principal/usuario; notebook fuera del scope del agente)
