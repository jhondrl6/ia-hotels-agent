# Dependencias — SOL-2-PATCH

## Diagrama de Dependencias

```
FASE-SOL2-PATCH-A (Micro-fixes codigo)
        │
        ▼
FASE-SOL2-PATCH-B (Parcheo prompts)
        │
        ▼
FASE-SOL2-PATCH-C (Investigacion + v4complete)
        │
        ▼
FASE-SOL2-PATCH-RELEASE (Docs cascade)
```

## Tabla de Conflictos Potenciales

| Fase | Archivos Modificados | Conflicto con |
|------|----------------------|---------------|
| PATCH-A | `coherence_validator.py`, `v4_asset_orchestrator.py`, `publication_gates.py` | Ninguno (lineas separadas, no solapan) |
| PATCH-B | `.opencode/plans/SOL-2-REFACTOR/05-prompt-inicio-sesion-fase-SOL2-A.md`, `SOL2-B.md` | Ninguno (archivos de plan historicos) |
| PATCH-C | Investigacion solamente (posible docstring en orchestrator) | PATCH-A (si PATCH-A ya toco orchestrator) |
| RELEASE | `REGISTRY.md`, `CHANGELOG.md`, `GUIA_TECNICA.md`, `VERSION.yaml` | Ninguno (documentacion) |

## Reglas de Orden

1. **PATCH-A antes que PATCH-C**: PATCH-A puede agregar docstring en orchestrator; PATCH-C investiga skipped_assets en el mismo archivo. Si PATCH-A ya documento el gap, PATCH-C solo verifica.
2. **PATCH-B es independiente**: Puede ejecutarse en paralelo con PATCH-A (diferentes archivos).
3. **RELEASE es siempre ultima**: Requiere que A, B, C esten completadas.

## Estados

| Fase | Estado | Fecha Inicio | Fecha Fin | Notas |
|------|--------|--------------|-----------|-------|
| PREP (diseno + baseline) | ✅ Completada | 2026-05-07 | 2026-05-07 | Plan + v4complete Termales ejecutado |
| PATCH-A | ✅ Completada | 2026-05-07 | 2026-05-07 | 3 fixes: deduplicacion coherence_validator, docstring orchestrator, logging publication_gates |
|| PATCH-B | ✅ Completada | 2026-05-07 | 2026-05-07 | 2 prompts historicos parcheados con notas POST-EJECUCION |
|| PATCH-C | ✅ Completada | 2026-05-07 | 2026-05-07 | Investigacion skipped_assets + baseline verificado. Decision: OPCION B (documentar, no deprecar). Veredicto: infraestructura preparada, gap de integracion orchestrator↔gate. |
|| RELEASE | ✅ Completada | 2026-05-07 | 2026-05-07 | Docs cascade: REGISTRY, CHANGELOG, GUIA_TECNICA, validaciones 4/4 |
