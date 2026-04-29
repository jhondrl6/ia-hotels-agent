# Plan: PATCH-AUDITORIA-FORENSE-AMAZILIA-v2

**Versión proyecto**: 4.36.1 → 4.37.0
**Fecha creación**: 2026-04-29
**Workflow**: phased_project_executor v2.9.0
**Contexto fuente**: `.opencode/context/ContextMv2.md` + `.opencode/context/ContextMM.md`

---

## Resumen

Intervención PATCH priorizada basada en la auditoría forense completa de la propuesta comercial AmaziliaHotel. La auditoría (ContextMv2.md) reveló 28 hallazgos: 2 bugs críticos, 6 hardcodes/stubs que producen datos falsos, 2 gaps documentales, y 20+ hardcodes de pricing/config. La trazabilidad (ContextMM.md) confirmó línea por línea el origen de cada dato en la propuesta.

Adicionalmente, se incluyen 2 fixes de infraestructura:
- 🔧 `version_consistency_checker.py` crashea con UnicodeEncodeError en cp1252
- 🔄 VERSION.yaml (4.36.0) desincronizado de CHANGELOG.md (4.36.1)

---

## Progreso

| Fase | ID | Descripción | Hallazgos | Estado | Prompt |
|------|----|-------------|-----------|--------|--------|
| PATCH-A | FASE-PATCH-A | Critical Bugs + Diagnostic Stubs + Unicode Fix | BUG-1, BUG-2, H-3, H-4, H-5, 🔧unicode | ✅ Completada 2026-04-29 | [05-prompt-inicio-sesion-fase-PATCH-A.md](05-prompt-inicio-sesion-fase-PATCH-A.md) |
|| PATCH-B | FASE-PATCH-B | Placeholders + Evidence Integrity | H-1, H-2, H-6 | ✅ Completada 2026-04-29 | [05-prompt-inicio-sesion-fase-PATCH-B.md](05-prompt-inicio-sesion-fase-PATCH-B.md) |
| PATCH-C | FASE-PATCH-C | v4complete Verification | (verificación) | ✅ Completada 2026-04-29 | [05-prompt-inicio-sesion-fase-PATCH-C.md](05-prompt-inicio-sesion-fase-PATCH-C.md) |
| PATCH-D | FASE-PATCH-D | Documentation + Version Sync + Deuda Técnica | H-7, H-8, H-9→H-27, 🔄drift | ✅ Completada 2026-04-29 | [05-prompt-inicio-sesion-fase-PATCH-D.md](05-prompt-inicio-sesion-fase-PATCH-D.md) |
| RELEASE | FASE-RELEASE-4.37.0 | Cierre Oficial | (documentación) | ⬜ Pendiente | [05-prompt-inicio-sesion-fase-RELEASE-4.37.0.md](05-prompt-inicio-sesion-fase-RELEASE-4.37.0.md) |

---

## Estructura de Archivos

```
.opencode/plans/
├── README-v2.md                              ← Este archivo
├── dependencias-fases-v2.md                  ← Diagrama + conflictos + scope R3
├── 06-checklist-implementacion-v2.md         ← Estado global
├── 05-prompt-inicio-sesion-fase-PATCH-A.md   ← BUG-1/2 + H-3/4/5 + unicode
├── 05-prompt-inicio-sesion-fase-PATCH-B.md   ← H-1/2/6
├── 05-prompt-inicio-sesion-fase-PATCH-C.md   ← v4complete + verificación
├── 05-prompt-inicio-sesion-fase-PATCH-D.md   ← Docs + drift + deuda técnica
└── 05-prompt-inicio-sesion-fase-RELEASE-4.37.0.md ← Cierre oficial
```

---

## Reglas de Ejecución

1. **Una fase por sesión** — sin excepciones (R1)
2. **Máximo 60 iteraciones** por fase (R2)
3. **Orden estricto**: PATCH-A → PATCH-B → PATCH-C → PATCH-D → RELEASE-4.37.0
4. **Evidencia proactiva** en FASE-PATCH-C (obligatorio inmediatamente post-v4complete)
5. **Cierre obligatorio** siempre (incluso si la fase no completa)
6. **Scope R3**: máx 4 tareas + 0 comandos largos, o 3 tareas + 1 comando largo

---

## Hallazgos Cubiertos (28 total)

### Prioridad 1 — Bloquea credibilidad del entregable
| ID | Descripción | Archivo | Fase |
|----|-------------|---------|------|
| BUG-1 | ROI sin "X" (.replace en L556) | `v4_proposal_generator.py` | PATCH-A |
| BUG-2 | Beneficio neto $0 (double discount pain_ratio) | `v4_proposal_generator.py` | PATCH-A |

### Prioridad 2 — Datos falsos en entregable
| ID | Descripción | Archivo | Fase |
|----|-------------|---------|------|
| H-1 | web_score "85" hardcodeado | `v4_proposal_generator.py` | PATCH-B |
| H-2 | Teléfono placeholder "+57 300 123 4567" | `two_phase_flow.py` | PATCH-B |
| H-3 | blog_activo = False SIEMPRE | `v4_diagnostic_generator.py` | PATCH-A |
| H-4 | speakable_schema = False SIEMPRE | `v4_diagnostic_generator.py` | PATCH-A |
| H-5 | ga4_indirect = False SIEMPRE | `v4_diagnostic_generator.py` | PATCH-A |
| H-6 | Evidence Tier SIEMPRE "C" | `scenario_calculator.py` | PATCH-B |

### Prioridad 3 — Documentación
| ID | Descripción | Archivo | Fase |
|----|-------------|---------|------|
| H-7 | AGENTS.md test count incorrecto | `AGENTS.md` | PATCH-D |
| H-8 | Gates documentados: 5 vs 9 reales | `AGENTS.md` | PATCH-D |

### Deuda Técnica Documentada (sin fix en este PATCH)
| IDs | Descripción | Acción | Fase |
|-----|-------------|--------|------|
| H-9→H-27 | 20+ hardcodes en pricing, escenarios, fallbacks | Catalogar en `docs/technical_debt/` | PATCH-D |

### Infraestructura
| ID | Descripción | Archivo | Fase |
|----|-------------|---------|------|
| 🔧 | UnicodeEncodeError en cp1252 | `version_consistency_checker.py` | PATCH-A |
| 🔄 | Version drift 4.36.0 vs 4.36.1 | `VERSION.yaml` + nuevo script | PATCH-D |

---

## Cómo Iniciar en Nueva Sesión

1. Abrir terminal en el proyecto: `cd /mnt/c/Users/Jhond/Github/iah-cli`
2. Cargar el prompt de la fase actual:
   ```
   Lee y ejecuta .opencode/plans/05-prompt-inicio-sesion-fase-PATCH-A.md
   ```
3. Cada prompt es autocontenido — incluye contexto, tareas, criterios y post-ejecución
4. Al terminar la fase, la documentación queda actualizada para la siguiente sesión
