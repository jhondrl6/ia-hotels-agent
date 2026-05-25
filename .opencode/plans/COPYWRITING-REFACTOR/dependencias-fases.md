# Dependencias y Conflictos — COPYWRITING REFACTOR

## Diagrama de Dependencias

```
COPY-A (Templates + Generators)
  │
  ▼
COPY-B (Commercial Gates + Content Rules)
  │
  ▼
COPY-C (E2E v4complete Validation)
  │
  ▼
COPY-RELEASE (Docs Cascade)
```

## Tabla de Conflictos de Archivos

| Archivo | COPY-A | COPY-B | COPY-C | COPY-RELEASE |
|---------|--------|--------|--------|--------------|
| `diagnostico_v6_template.md` | **MODIFICA** | — | — | — |
| `propuesta_v6_template.md` | **MODIFICA** | — | — | — |
| `v4_diagnostic_generator.py` | **MODIFICA** | — | — | — |
| `v4_proposal_generator.py` | **MODIFICA** | — | — | — |
| `modules/quality_gates/commercial_gate.py` | — | **CREA** | — | — |
| `CHANGELOG.md` | — | — | — | **MODIFICA** |
| `GUIA_TECNICA.md` | — | — | — | **MODIFICA** |
| `VERSION.yaml` | — | — | — | **MODIFICA** |
| `REGISTRY.md` | — | — | — | **AUTO** |

**Sin conflictos**: Ningún archivo es modificado por más de una fase (excepto REGISTRY.md que es auto-actualizado por `log_phase_completion.py`).

## Regla de No-Block

- COPY-A no depende de ninguna fase previa
- COPY-B depende de COPY-A completada (templates y generators modificados)
- COPY-C depende de COPY-B completada (commercial gates integrados)
- COPY-RELEASE depende de COPY-C completada (E2E validado)
