# FASE 0: Primer Piso — Entrega Confiable al Cliente

> **Plan ID:** FASE-0-DELIVERY-QUALITY  
> **ROADMAP v3.3 ref:** §7 FASE 0 (0-01 .. 0-05)  
> **Repo baseline:** v4.45.0 — TERMALES-GATE-HARDENING  
> **Created:** 2026-05-13  
> **Constraint:** 1 fase/sesión. No ejecutar `v4complete` salvo en fase 0G-E2E dedicada.

---

## Objetivo

Asegurar que `v4complete` entregue un paquete autoconsistente donde:

- Toda brecha detectada tiene trazabilidad (`pain_id`, fuente, severidad, confianza, estado).
- Ninguna brecha desaparece sin explicación entre diagnóstico, oportunidad, propuesta y assets.
- Cada servicio vendido responde a una brecha real y tiene asset específico.
- Existe un artifact bloqueante `delivery_quality_report.json` antes de ZIP/publicación.
- El humano revisa excepciones y decisión comercial, no reconstruye coherencia (<= 10 min).

---

## Alcance

| ID | Entregable | Estado actual | Acción planificada |
|----|------------|---------------|--------------------|
| 0-01 | `pain_ledger` operativo | No existe nominalmente. Existe `PainSolutionMapper` + `Pain` dataclass + `pain_ids_resolved` en assets. | Crear `PainLedger` facade/wrapper sobre estructura existente; normalizar campos; serializar JSON. |
| 0-02 | Coverage diagnóstico/oportunidad | Parcial: assets tienen `pain_ids_resolved`, pero no hay gate que verifique cobertura 1:1. | Crear `CoverageGate` + tests: `brechas_en_diagnostico + brechas_justificadas == brechas_detectadas`. |
| 0-03 | Matriz propuesta → brecha → asset | Parcial: `PROPOSAL_SERVICE_TO_ASSET` es estático; proposal generator filtra dinámicamente. | Crear `ProposalAssetMatrix` que vincule servicios vendidos a `pain_ids` y assets generados con evidencia. |
| 0-04 | `delivery_quality_report.json` bloqueante | **Inexistente**. No se encontró artifact ni código. | Crear módulo `delivery_quality_report.py`, integrar en pipeline post-generación, bloquear ZIP si FAIL. |
| 0-05 | Checklist humano reducido | No existe checklist derivado automáticamente del reporte. | Crear `HumanChecklistGenerator` que derive checklist <= 10 items desde `delivery_quality_report.json`. |

---

## No-Alcance

- No modificar `ROADMAP.md` (documento estratégico manual).
- No ejecutar `v4complete` durante fases de código (salvo 0G-E2E).
- No crear UI, dashboard, SaaS, multiusuario.
- No implementar FASE A/B/C/D del ROADMAP.
- No disparar docs cascade automático por cambios en este plan (solo en RELEASE).

---

## Decisiones arquitectónicas

| # | Decisión | Opciones | Veredicto | Justificación |
|---|----------|----------|-----------|---------------|
| D1 | ¿Crear `pain_ledger` nuevo o formalizar existente? | Nuevo módulo / Extender mapper / Adapter sobre existente | **Adapter + rename** | `PainSolutionMapper.detect_pains()` ya produce `List[Pain]`. Se crea `PainLedger` como facade que normaliza, serializa y expone estado. Evita duplicar lógica de detección. |
| D2 | ¿Dónde vive `delivery_quality_report.json`? | `v4_audit/` / raíz hotel / deliveries | **`v4_audit/`** | Consistente con `asset_generation_report.json`, `coherence_validation.json`, `gate_report_*.json`. |
| D3 | ¿Qué bloquea publicación? | Solo FAIL / WARNING fuerte / thresholds | **FAIL bloquea; WARNING no bloquea** | `check_publication_readiness()` ya usa `status in (FAILED, BLOCKED)`. FASE 0 respeta este contrato. Se documenta explícitamente. |
| D4 | ¿`can_use=True` significa entregable final? | Sí / No / Depende | **No** | `can_use = preflight_status != "BLOCKED"` (v4_asset_orchestrator.py:933). Un asset ESTIMATED puede ser `can_use=True`. FASE 0 introduce `delivery_ready` flag separado: confidence >= 0.8, status != ESTIMATED, preflight == PASSED. |
| D5 | ¿Propuesta se valida contra servicios estáticos o dinámicos? | Estático / Dinámico / Híbrido | **Híbrido** | Mantener `PROPOSAL_SERVICE_TO_ASSET` para backward compat. Enriquecer con pain_ids detectados dinámicamente. Gate valida que todo servicio vendido tenga brecha + asset. |
| D6 | ¿Baseline usa output existente o nuevo E2E? | Existente / Nuevo | **Existente** | Output de `hotelcastillareal` (2026-05-12) disponible con 13 assets, coherence 0.81. Sin costo de API. |
| D7 | ¿Reporte se integra antes o después de ZIP? | Antes / Después | **Antes** | `delivery_quality_report.json` debe generarse y validarse antes de `create_delivery_package()`. FAIL bloquea ZIP. |

---

## Fases

| Fase | Nombre | Tipo | Comando largo | Dependencias |
|------|--------|------|---------------|--------------|
| 0A | Baseline real | Investigación | No | Ninguna |
| 0B | Pain ledger | Código + tests | No | 0A |
| 0C | Coverage gate | Código + tests | No | 0B |
| 0D | Proposal-asset matrix | Código + tests | No | 0C |
| 0E | Delivery quality report | Código + tests | No | 0D |
| 0F | Human checklist | Código + tests | No | 0E |
| 0G | E2E controlado | Verificación | Sí (`v4complete`) | 0A-0F |
| 0H | G8 Root-Cause Hardening | Código + tests | No | 0G |
| RELEASE | Docs cascade | Documentación | No | 0A-0H |

---

## Criterios de éxito (G0/G6/G7/G8)

| Gate | Pregunta | Evidencia esperada |
|------|----------|-------------------|
| G0 | ¿El pipeline entrega diagnóstico, oportunidad, propuesta y assets autoconsistentes para un hotel real? | E2E 0G produce `delivery_quality_report.json` con `status: PASS`. |
| G6 | ¿Diagnóstico, oportunidad, propuesta y assets cuentan la misma historia? | `coherence_score_final >= 0.8` y `coverage_gate == PASS`. |
| G7 | ¿Todas las brechas detectadas aparecen, se agrupan o se justifican explícitamente? | `pain_ledger.json` muestra 100% de pains con estado != `UNTRACKED`. |
| G8 | ¿Cada asset resuelve un problema real del hotel y no es plantilla genérica? | `asset_specificity_gate == PASS`; ningún asset con `GENERIC_DRAFT` sin justificación. **Resuelto en FASE-0H.** |

---

## Baseline verificado (2026-05-13)

### Outputs existentes
```
output/v4_complete/hotelcastillareal/v4_audit/asset_generation_report.json
output/v4_complete/hotelcastillareal/v4_audit/coherence_validation.json
output/v4_complete/hotelcastillareal/v4_audit/coherence_validation_post_gen.json
output/v4_complete/hotelcastillareal/v4_audit/gate_report_*.json
output/v4_complete/hotelcastillareal/v4_audit/geo_flow_result.json
output/v4_complete/deliveries/hotelcastillareal_20260512.zip
```

### Gaps confirmados
- ❌ `delivery_quality_report.json` — inexistente
- ❌ `pain_ledger` nominal — inexistente; estructura equivalente parcial (`PainSolutionMapper`)
- ⚠️ `delivery_ready_percentage` = 25% (hotelcastillareal) con 12/13 `can_use=True` pero 9 `estimated`
- ⚠️ `PROPOSAL_SERVICE_TO_ASSET` estático vs generación dinámica

### Tests actuales
- 2491 funciones, 192 archivos, 0 regresión (según AGENTS.md)
- Validaciones: 3/5 passed (version sync y document integration fallan — preexistente)
