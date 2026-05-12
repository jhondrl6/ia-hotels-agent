# Plan: REFACTOR-COHERENCIA-CASTILLAREAL

> **Proyecto**: Refactorización de Coherencia y Calidad — Hotel Castilla Real
> **Versión base**: v4.44.0
> **Versión target**: v4.45.0
> **Contexto fuente**: `.opencode/context/AUDITORIA_COHERENCIA_HOTELCASTILLAREAL_20260511.md`
> **Workflow**: `phased_project_executor.md` v2.11.0
> **Regla de sesión**: 1 fase por sesión, sin excepciones

---

## Resumen Ejecutivo

El pipeline v4complete produce **5 valores distintos de coherence_score** para el mismo delivery porque:
1. `CoherenceGate.execute()` ignora `_validator` (H10 FIX es un facade)
2. `open_graph_generator.py` tiene **defaults hardcodeados de otro hotel** ('Amazilia Hotel Campestre')
3. `local_content_generator.py` genera contenido con location vacía
4. `evidence_tier` es inconsistente entre `financial_scenarios.json` y diagnóstico YAML
5. `asset_confidence` gate es demasiado permisivo (WARNING en vez de BLOCKED para 100% ESTIMATED)

Este plan corrige las causas raíz P0-P3 en 5 fases de implementación + 1 fase RELEASE, con una única ejecución de v4complete en FASE-5-VERIFY para Hotel Castilla Real.

---

## Fases

| # | ID | Nombre | Tipo | Tareas | Comando largo | Dependencias |
|---|-----|--------|------|--------|---------------|--------------|
| 1 | FASE-1-COH | Unificar CoherenceValidator ↔ CoherenceGate | Implementación | 4 | No | — |
| 2 | FASE-2-DEFAULT | Eliminar hardcoded defaults cross-hotel | Implementación | 4 | No | FASE-1-COH |
| 3 | FASE-3-CONTENT | Fix local_content + evidence_tier + all_aligned | Implementación | 4 | No | FASE-2-DEFAULT |
| 4 | FASE-4-GATE | Gate asset_confidence hardening | Implementación | 3 | No | FASE-3-CONTENT |
| 5 | FASE-5-VERIFY | v4complete Hotel Castilla Real + análisis | Verificación | 3 | Sí (v4complete) | FASE-4-GATE |
| 6 | FASE-RELEASE-4.45.0 | Documentación oficial y cierre | Release | 8 | No | Todas las anteriores ✅ |

---

## Hotel de verificación

- **Nombre**: Hotel Castilla Real
- **URL**: https://www.hotelcastillareal.com/
- **hotel_id**: `hotelcastillareal`
- **Región**: eje_cafetero

---

## Garantías Post-Fix (G1-G10)

| Gate | Verificación | Target |
|------|-------------|--------|
| G1 | `coherence_validation.overall_score == gate.coherence.value` | ✅ Iguales |
| G2 | `diagnostic_YAML.coherence_score == gate.coherence.value` | ✅ Mantener |
| G3 | `v4_complete_report` sin scores duplicados ni inexplicables | ✅ 1 score, trazable |
| G4 | `open_graph_meta.html` sin "Amazilia" | ✅ 0 matches |
| G5 | `local_content_*.md` sin "Hotel en  -" | ✅ 0 matches |
| G6 | `hotel_schema.json` con campos poblados | ✅ Poblados (requiere onboarding) |
| G7 | `whatsapp_conflict_guide` con confidence >= 0.7 | ✅ >= 0.7 |
| G8 | `financial_scenarios.evidence_tier == diagnostic.financial_evidence_tier` | ✅ Iguales |
| G9 | `CoherenceGate.execute()` llama a `_validator.validate()` | ✅ >= 1 llamada |
| G10 | Ningún generator con defaults hardcodeados de otro hotel | ✅ 0 defaults cross-hotel |

---

## Artefactos del Plan

```
.opencode/plans/
├── README.md                                    (este archivo)
├── 05-prompt-inicio-sesion-fase-1-COH.md
├── 05-prompt-inicio-sesion-fase-2-DEFAULT.md
├── 05-prompt-inicio-sesion-fase-3-CONTENT.md
├── 05-prompt-inicio-sesion-fase-4-GATE.md
├── 05-prompt-inicio-sesion-fase-5-VERIFY.md
├── 05-prompt-inicio-sesion-fase-RELEASE-4.45.0.md
├── 06-checklist-implementacion.md
├── 09-documentacion-post-proyecto.md
└── dependencias-fases.md
```

---

## Modo de Ejecución por Fase

| Fase | Modo | Justificación |
|------|------|---------------|
| FASE-1-COH | DIRECTO | Código puro: investigación + fix + tests. Sin comandos externos. |
| FASE-2-DEFAULT | DIRECTO | Código puro: fix en 2 archivos + auditoría grep + tests. |
| FASE-3-CONTENT | DIRECTO | Código puro: 3 fixes relacionados + tests. |
| FASE-4-GATE | DIRECTO | Código puro: hardening de gate + tests + compatibilidad. |
| FASE-5-VERIFY | DIRECTO con notify_on_complete | v4complete es comando largo (5-10 min). Ejecutar DIRECTO con terminal(timeout=600, notify_on_complete=True) si quedan >= 30 iteraciones tras prep. Si no, subagente. |
| FASE-RELEASE | DIRECTO | Documentación y validaciones. Sin comandos largos. |

---

## Notas de Diseño

### R3 Compliance
Cada fase de implementación tiene **max 4 tareas** y **0 comandos largos**, excepto FASE-5-VERIFY que tiene **3 tareas + 1 comando largo** (v4complete). Esto respeta la regla R3 del executor.

### v4complete Único
Solo FASE-5-VERIFY ejecuta v4complete. No hay ejecuciones previas ni intermedias. La fase incluye el Protocolo de Evidencia Proactiva inmediatamente después de la ejecución.

### Documentación Incremental
Cada fase de implementación ejecuta `log_phase_completion.py` al terminar (misma sesión). FASE-RELEASE NO registra fases anteriores — solo hace sync, CHANGELOG, GUIA_TECNICA y validaciones.
