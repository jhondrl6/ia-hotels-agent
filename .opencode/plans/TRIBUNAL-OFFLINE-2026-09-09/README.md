# TRIBUNAL-OFFLINE-2026-09-09

> **Versión objetivo**: 4.76.0 · **Workflow**: `phased_project_executor.md` v2.20.0
> **Estado**: ⬜ PREPARACIÓN COMPLETADA — pendiente de ejecución (8 sesiones)
> **Contexto fuente**: `.opencode/context/Historico/CONTEXT-BOTS-POTENCIALIZACION-IAH-CLI-2026-09-01.md` §5, §14, §15 (movido a Historico el 2026-09-09; lecciones QMind: notebook `iah-cli-lecciones` — write-back automatizado vía `scripts/validate_qmind_writeback.py`)
> **Anclaje estratégico**: `ROADMAP.md` v4.2 §7.2 (FASE T, tramo offline: T1/T2/T4)
> **Baseline**: v4.75.0 «Estabilización pre-tribunal» — precondiciones T0.1-T0.4 ✅ CERRADAS (§14.1)
> **Corrida de referencia**: `evidence/FASE-I/` (coherence 0.8333, `is_coherent: true`, 5 pains)
> **Baseline solo-lectura**: `output/FASE-D_salentoreal_post_guard/` (Tier B, 2026-08-31)

## Problema

El pipeline v4complete genera diagnóstico + propuesta + assets + gates, pero **nadie certifica las 6 cláusulas P6 como un todo** ni produce evidencia legible de la revisión. Los gates internos deciden publicar o no, pero no generan un acta independiente que un humano (o el cliente) pueda auditar. El tribunal es la capa de accountability que falta entre "paquete generado" y "paquete entregable con responsabilidad".

## Solución

Módulos deterministas en `modules/quality_gates/tribunal/` (gate-family), ejecutados en `main.py` junto a `delivery_quality_report`. **NO son agentes ni bots autónomos** (§15.1): son clases Python que leen artefactos existentes y producen `acta_revision.json` + `acta_revision.md`.

| Bot | Módulo | LLM | Cláusulas P6 |
|-----|--------|-----|--------------|
| Bot 5 (Juez) | `tribunal/judge.py` | No | P6.1-P6.6 + P7 |
| Bot 1 (Diagnóstico) | `tribunal/diagnosis_reviewer.py` | No | P6.1 |
| Bot 3 (Assets) | `tribunal/asset_reviewer.py` | No | P6.3, P6.4 |
| Bot 2 (Alineación) | `tribunal/alignment_reviewer.py` | Sí (extracción) | P6.2 |
| Bot 4 (Honestidad) | `tribunal/honesty_reviewer.py` | Sí (extracción) | P6.5 |

**Regla arquitectónica inviolable**: el tribunal NO reimplementa lógica de gates. Lee outputs como revisor independiente.

## Progreso

| # | Fase | Objetivo | Complejidad | Modo | Estado |
|---|------|----------|-------------|------|--------|
| 1 | FASE-T1 | Juez certificador + contrato de acta + integración main.py | **ALTA** | DIRECTO | ⬜ Pendiente |
| 2 | FASE-T2-A | Revisor de Diagnóstico (Bot 1) | MEDIA | DELEGADO | ⬜ Pendiente |
| 3 | FASE-T2-B | Revisor de Assets (Bot 3) | MEDIA | DELEGADO | ⬜ Pendiente |
| 4 | FASE-T4-A | Revisor de Alineación NL (Bot 2) + interfaz de extracción LLM | **ALTA** | DIRECTO | ⬜ Pendiente |
| 5 | FASE-T4-B | Revisor de Honestidad NL (Bot 4) | MEDIA | DELEGADO | ⬜ Pendiente |
| 6 | FASE-E2E | v4complete Hotel Salento Real + evidencia + acta en output | BAJA | MIXTO | ⬜ Pendiente |
| 7 | FASE-VERIFY | Certificación formal de ACs contra output E2E real | MEDIA | DIRECTO | ⬜ Pendiente |
| 8 | FASE-RELEASE-4.76.0 | Cierre documental + version bump + archivado (R2.5) | BAJA | DELEGABLE | ⬜ Pendiente |

## Alcance

**Dentro**: T1 (Juez) → T2 (revisores mecánicos) → T4 (revisores NL, LLM mockeado) → E2E → VERIFY → RELEASE.

**Fuera (tramo externo, documentado en `dependencias-fases.md`)**: T3 (onboarding datos reales), T5 (deploy FTP/WP + staging), T6 (throughput + gancho).

## Residuos heredados (§14.2) en alcance

| Residuo | Fase que lo aborda |
|---------|-------------------|
| S-HF1 (`message «4/4»` vs `details.total_services = 1`) | FASE-T1 (criterio de narración del Juez) |
| S-I1 (`critical_recall = 1.0` con `details: {}`) | FASE-T2-A (Bot 1 distingue recall fundado de vacuo) |
| P12 (promised_assets_exist verifica via catálogo estático pre-gen — P6.3 no verificable desde el artefacto) | FASE-T2-B (Bot 3 detecta la fuente declarada en el `message`, no el score) |
| S-C4 (tabla assets técnicos imprime catálogo incondicional) | FASE-T4-A (tercera superficie de promesa) |

## Reglas transversales (heredadas de §14.3 + executor v2.20.0)

1. R1: Una fase por sesión. Sin excepciones.
2. R2.1: Presupuesto medido con instrumento, corte en commit de código.
3. R2.2: Sin números de línea — citar símbolos.
4. R2.3: No-regresión como delta con par pre/post.
5. R2.4: AC no legible en artefacto = ⚠️, nunca ✅.
6. R2.5: RELEASE termina archivando el plan.
7. R3: ≤4 tareas + 0 comandos largos, Ó ≤3 tareas + 1 comando largo.
8. §15.4.1: Contrato de acta determinista fija en T1, ANTES de T2/T4.
9. §15.4.3: Anfitrión real = `main.py` junto a `delivery_quality_report`; NO `two_phase_flow.py`.
10. §15.4.4: Cada AC declara artefacto + clave donde se lee su valor.
