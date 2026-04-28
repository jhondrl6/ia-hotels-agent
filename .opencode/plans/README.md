# Plan Maestro — Trazabilidad Amazilia Hotel

> Version: v2.0 | Actualizado: 2026-04-27

## Indice de Archivos

| Archivo | Descripcion |
|---------|-------------|
| `README.md` | Este archivo — indice y resumen |
| `dependencias-fases.md` | Diagrama de dependencias y estado de fases |
| `06-checklist-implementacion.md` | Checklist detallado por fase |
| `05-prompt-inicio-sesion-fase-TRAZABILIDAD-VALIDATE-v2.md` | Prompt de la fase actual |
| `09-documentacion-post-proyecto.md` | Documentacion post-proyecto |

## Contexto

El proyecto "Trazabilidad Calidad Garantizada" identifico **18 hallazgos** y **5 bugs** en el pipeline v4complete de iah-cli, testeado contra Amazilia Hotel (amaziliahotel.com).

### Cadena de Fases

```
DOCS → RAIZ → VALIDATE → PATCH+SEO → REFINEMENT → PATCH Forense → VALIDATE-v2
                                                                    (actual)
```

### Estado Actual

- **Version**: v4.36.0 (PATCH Forense AmaziliaHotel)
- **Fases completadas**: 6/7
- **Fase actual**: FASE-TRAZABILIDAD-VALIDATE-v2
- **Hallazgos corregidos**: 15/18 (3 diferidos)
- **Bugs corregidos**: 5/5
- **Issues post-VALIDATE**: 4/4 (T1-T4)

### Hallazgos Diferidos (3)

1. **C10**: Benchmarks sin trace de fuente
2. **D16**: Contexto regional hardcoded
3. **D17**: Competidores stub

### Decision Diferida

- **D1**: WARNING gates deberian cambiar readiness a REQUIRES_REVIEW?

## Reglas

1. Una fase por sesion
2. Maximo 60 iteraciones por fase
3. TIER 1 documentacion inmediata post-fase
4. TIER 2 documentacion deferida a FASE-RELEASE
