# Dependencias entre Fases — ROICR

```
FASE-1 ──→ FASE-2 ──→ FASE-3 ──→ FASE-4 ──→ FASE-5 ──→ FASE-6 ──→ FASE-7
(Semántica)  (Gates)   (Pricing)   (Garantía)  (Tests)    (v4complete)  (RELEASE)
```

## Detalle de dependencias

| Fase | Depende de | Razón |
|------|-----------|-------|
| FASE-1 | Ninguna | Base: crea AssetSemanticsValidator + migration_target en registry |
| FASE-2 | FASE-1 | Gate usa AssetSemanticsValidator para evaluar narrativas |
| FASE-3 | FASE-2 | Pipeline unificado alimenta propuesta que Gate valida |
| FASE-4 | FASE-3 | Garantía necesita pipeline + pricing correctos como baseline |
| FASE-5 | FASE-4 | Tests necesitan todos los módulos implementados para fixtures |
| FASE-6 | FASE-5 | v4complete requiere tests pasando para ejecutar con confianza |
| FASE-7 | FASE-6 | RELEASE valida docs post-v4complete |

## Reglas

- **1 fase = 1 sesión**. No saltar fases.
- **No v4complete intermedio**. Solo FASE-6 ejecuta v4complete.
- **Cada fase documenta** su resultado en `09-documentacion-post-proyecto.md`.
