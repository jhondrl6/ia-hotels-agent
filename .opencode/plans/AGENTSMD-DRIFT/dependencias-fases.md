# Dependencias y Conflictos — AGENTSMD-DRIFT

## Grafo de dependencias

```
FASE-A-01a (AGENTS.md editorial)
    │
    └──→ FASE-A-01b (validate_agents_md.py + CONTRIBUTING.md) ✅ 2026-05-26
            │
            └──→ FASE-A-01c (v4complete Hotel Castilla Real)
                    │
                    └──→ FASE-RELEASE-4.49.0 (docs cascade)
```

## Tabla de conflictos

| Archivo | FASE-A-01a | FASE-A-01b | FASE-A-01c | FASE-RELEASE | ¿Conflicto? |
|---------|-----------|-----------|-----------|-------------|-------------|
| `AGENTS.md` | ✏️ Edita (9 pasos) | 🔍 Lee (validación) | — | 🔄 sync_versions | Secuencial OK |
| `scripts/validate_agents_md.py` | — | ✨ Crea | — | — | Sin conflicto |
| `docs/CONTRIBUTING.md` | — | ✏️ Edita (§Post-Fase) | — | 🔄 sync_versions | Secuencial OK |
| `CHANGELOG.md` | — | — | — | ✏️ Edita | Sin conflicto |
| `docs/GUIA_TECNICA.md` | — | — | — | ✏️ Edita | Sin conflicto |
| `VERSION.yaml` | — | — | — | ✏️ Edita | Sin conflicto |
| `output/v4_complete/` | — | — | 📁 Genera | 🔍 Lee | Secuencial OK |

## Notas

- **A-01a → A-01b**: A-01b valida AGENTS.md corregido por A-01a. Si A-01a no completa, A-01b valida datos stale.
- **A-01c**: Independiente en código, pero depende conceptualmente de que AGENTS.md ya esté corregido (el v4complete usa AGENTS.md como guía del agente).
- **RELEASE**: Solo se ejecuta si TODAS las fases A-01a, A-01b, A-01c están ✅.
