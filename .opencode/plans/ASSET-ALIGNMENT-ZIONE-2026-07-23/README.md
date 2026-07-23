# Plan: ASSET-ALIGNMENT-ZIONE-2026-07-23

> **Fecha**: 2026-07-23
> **Contexto**: `.opencode/context/ZIONE-PROPOSAL-ASSET-ALIGNMENT-BLOCK-2026-07-23.md`
> **Hotel**: Zi One Luxury (https://zione.co/)
> **Versión**: 4.62.0 → 4.63.0
> **Convención**: 1 fase = 1 sesión. Sin excepciones.

## Resumen

Reparar el bloqueo de `proposal_asset_alignment` (Gate 9) detectado en v4complete para Zi One Luxury.
Cadena de bypass de 3 capas + 13 hallazgos adicionales. Solución híbrida (Opciones A + C + E + F).
Validación final: única ejecución de v4complete para zione.co con análisis post-implementación.

## Estructura del Plan

```
.opencode/plans/ASSET-ALIGNMENT-ZIONE-2026-07-23/
├── 01-plan-maestro.md                    # Plan maestro con hallazgos, dependencias, DoD
├── 02-prompt-fase-1.md                    # Bypass de seguridad (CRÍTICO)
├── 03-prompt-fase-2.md                    # Gaps Pain→Asset (MAYOR COMPLEJIDAD)
├── 04-prompt-fase-3.md                    # Propuesta condicional + unificación fuentes
├── 05-prompt-fase-4.md                    # Correcciones de presentación + bugs menores
├── 06-prompt-fase-5.md                    # v4complete + análisis post-implementación
├── 07-prompt-fase-6-release.md            # RELEASE 4.63.0
├── 08-checklist-implementacion.md        # Tracking
├── 09-documentacion-post-proyecto.md     # Acumulativo para RELEASE
├── dependencias-fases.md                  # Dependencias y conflictos
└── README.md                              # Este archivo
```

## Progreso

| Fase | Descripción | Estado | delegate_task | Sesión | Iteraciones | Commit |
|------|-------------|--------|---------------|--------|-------------|--------|
| FASE-1 | Bypass de seguridad | ✅ Completada | DIRECTA* | Sesión 2026-07-23 | ~24 iteraciones | — |
| FASE-2 | Gaps Pain→Asset + OG generator (MAYOR) | ⏳ Pendiente | ✅ SUBAGENTE | — | — | — |
| FASE-3 | Propuesta condicional | ⏳ Pendiente | ✅ SUBAGENTE | — | — | — |
| FASE-4 | Correcciones presentación | ⏳ Pendiente | ✅ SUBAGENTE | — | — | — |
| FASE-5 | v4complete + análisis | ⏳ Pendiente | ⚠️ MIXTO | — | — | — |
| FASE-RELEASE | Release 4.63.0 | ⏳ Pendiente | ✅ SUBAGENTE | — | — | — |

## Fase de Mayor Complejidad: FASE-2

FASE-2 (Gaps Pain→Asset + OG generator enhance_existing) es la fase de mayor complejidad técnica porque:
1. Modifica lógica de detección de pains (no solo agregar entradas)
2. Cambia el contrato de `detect_pains()` de binario a graduated (no_og_tags)
3. Agrega un pain type nuevo con validación de campos
4. Cascada semántica pain→asset→proposal
5. Eliminación de clave duplicada puede romper consumidores
6. Extiende OpenGraphGenerator con modo enhance_existing (no produce tags duplicados)

## delegate_task — Matriz

| Fase | Viable | Tipo |
|------|--------|------|
| FASE-1 | ✅ | SUBAGENTE |
| FASE-2 | ✅ | SUBAGENTE |
| FASE-3 | ✅ | SUBAGENTE |
| FASE-4 | ✅ | SUBAGENTE |
| FASE-5 | ⚠️ | MIXTO (v4complete subagente + análisis directo) |
| FASE-RELEASE | ✅ | SUBAGENTE |
