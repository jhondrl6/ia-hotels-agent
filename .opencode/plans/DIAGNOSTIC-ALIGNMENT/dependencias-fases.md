# Dependencias entre Fases — DIAGNOSTIC-ALIGNMENT

```
┌─────────────────────────────────────────────────────────┐
│              DIAGNOSTIC-ALIGNMENT v4.52.0                 │
│         Refactorización de Diagnóstico Comercial          │
└─────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
      ┌──────────┐   ┌──────────┐   ┌──────────┐
      │  FASE-A  │   │  FASE-B  │   │  FASE-C  │
      │ E1 + E2  │   │ F1 + F2  │   │ F3 + F4  │
      │  (CRIT)  │   │ (FRICC)  │   │ (FRICC)  │
      └────┬─────┘   └────┬─────┘   └────┬─────┘
           │              │              │
           └──────────────┼──────────────┘
                          │
                          ▼
                   ┌──────────────┐
                   │   FASE-D     │
                   │  v4complete  │
                   │ + Verificar  │
                   └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │ FASE-RELEASE │
                   │   Docs +     │
                   │ Version bump │
                   └──────────────┘
```

## Tabla de Dependencias

|| Fase | Depende de | Archivos en conflicto potencial | Notas | Estado |
||------|-----------|-------------------------------|-------|--------|
|| **FASE-A** | — (inicio) | `v4_diagnostic_generator.py` (L934-979, L999-1101), `diagnostico_v6_template.md` (L28-32) | Independiente | ✅ Completada 2026-05-25 |
| **FASE-B** | — (inicio) | `v4_diagnostic_generator.py` (L672, F1), `config/commercial.yaml` (F1), `_prepare_financial_template_vars` (F2) | Independiente de A | ✅ Completada 2026-05-25 |
| **FASE-C** | — (inicio) | `diagnostico_v6_template.md` (L58-68, F3), `v4_diagnostic_generator.py` (_build_brechas_resumen_section, F4) | Independiente de A y B | ⬜ PENDIENTE |
| **FASE-D** | FASE-A ✅, FASE-B ✅, FASE-C ✅ | — (solo ejecuta v4complete) | Requiere las 3 fases previas completadas | ⬜ PENDIENTE |
| **FASE-RELEASE** | FASE-D ✅ | `VERSION.yaml`, `CHANGELOG.md`, `GUIA_TECNICA.md`, `REGISTRY.md` | Solo documentación | ⬜ PENDIENTE |

## Conflictos entre Fases

| Archivo | FASE-A | FASE-B | FASE-C | Resolución |
|---------|--------|--------|--------|------------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | L934-979, L999-1101 | _build_quick_wins (L672 area), _prepare_financial_template_vars | _build_brechas_resumen_section | Modifican métodos distintos → sin conflicto |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | L28-32 (Section 1) | — | L58-68 (Section 4) | Modifican secciones distintas → sin conflicto |
| `config/commercial.yaml` | — | Quick Wins text | — | Solo FASE-B toca |

**Conclusión**: Las fases A, B, C modifican métodos y secciones diferentes. No hay conflictos de merge. Pueden ejecutarse en paralelo si se deseara, aunque el executor impone secuencialidad (1 fase/sesión).

## Orden Recomendado de Ejecución

1. **FASE-A** primero (críticos — mayor impacto comercial)
2. **FASE-B** segundo (fricciones de copy)
3. **FASE-C** tercero (fricciones de template)
4. **FASE-D** cuarto (ejecución + verificación)
5. **FASE-RELEASE** quinto (documentación)
