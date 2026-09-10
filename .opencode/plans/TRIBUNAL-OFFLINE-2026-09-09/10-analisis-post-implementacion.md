# Análisis Post-Implementación — TRIBUNAL-OFFLINE-2026-09-09

> **Estado**: Preparación completada — pendiente de ejecución
> **Plan**: TRIBUNAL-OFFLINE-2026-09-09
> **Versión objetivo**: 4.76.0

---

## Resumen de Ejecución (llenar al cierre de cada fase)

| Fase | Sesión | Estado | Iteraciones | delegate_task | Notas |
|------|--------|--------|-------------|---------------|-------|
| FASE-T1 | — | ⬜ | — | No | Juez + contrato de acta |
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

*(Se llenará conforme avancen las fases)*

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

---

## Métricas de Ejecución (llenar al cierre)

| Métrica | Valor |
|---------|-------|
| Tests pre-plan (baseline v4.75.0) | 3.934 funciones / 298 archivos |
| Tests nuevos del tribunal | — |
| Tests totales post-plan | — |
| Coherence output E2E | — |
| Veredicto del Juez | — |
| Iteraciones totales (8 fases) | — |
| Fases con delegate_task | — |

---

## Decisiones Arquitectónicas

| ID | Decisión | Rationale | Alternativas rechazadas | Fase |
|----|----------|-----------|------------------------|------|
| DA-T1 | Anfitrión del tribunal = `main.py` junto a `delivery_quality_report` | Es donde hoy se decide el ZIP; `two_phase_flow.py` es huérfano | `two_phase_flow.py` (sin llamador de producción), módulo independiente (drift) | T1 |
| DA-T1 | Veredicto alimenta UNA de las tres rutas de bloqueo existentes | No añadir complejidad; el kill switch `GATE_BLOCKING_ENABLED` ya gobierna | Cuarta ruta propia (aísla el tribunal del flujo existente) | T1 |
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
