# Contexto: Clasificación de Bugs vs DT-3 — Conclusión de Sesión 2026-07-25

> **Origen**: Sesión cerrada "Análisis v4complete Zione.co" (20260725_210646_571283) — mensaje assistant 111900
> **Fecha**: 2026-07-25
> **Modelo origen**: deepseek-v4-pro (68 mensajes)
> **Trigger original**: Ejecución fresca de v4complete para Zione.co reveló 5 bugs no cubiertos por DT-3
> **Documento principal**: `.opencode/plans/DT-3-TECH-DEBT-2026-07-25/08-analisis-post-implementacion.md` (20.7 KB)
> **Contexto DT-3**: `.opencode/context/CONTEXT-DT-3-TECH-DEBT-POST-DT2.md`
> **Evidencia ejecución**: `output/clientes/v4_complete/zione/v4_audit/`

---

## Pregunta del usuario (verbatim)

> "En conclusión los Bugs son nuevos? y podría inferirse que fueron ocasionados durante la implementación de DT-3?"

## Conclusión (tabla)

| Bug | ¿Nuevo? | Relación con DT-3 |
|-----|---------|-------------------|
| BUG-6 | Preexistente | DT-3 lo clasificó mal (falso negativo en el diagnóstico) |
| BUG-7 | Incierto | DT-3 lo expuso al destapar el pipeline |
| BUG-8 | Preexistente | DT-3 lo expuso al darle datos reales al motor financiero |
| BUG-9 | Agravado | DT-3 hizo unificación parcial → creó divergencia donde antes había consistencia |
| BUG-10 | Preexistente | Sin relación con DT-3 |

## Justificación por bug

### BUG-6 — Preexistente, mal clasificado por DT-3

El coverage gate ya estaba en la ejecución de DT-3 (FASE-3), pero se clasificó como "legítimo, no falso positivo". El error fue de diagnóstico: DT-3 no cruzó `gate_report.json` contra `asset_generation_report.json`. Si lo hubiera hecho, habría visto `whatsapp_button` en `skipped_assets` con `presence_verified: true, site_verified: true`. El bug es del coverage gate, no de DT-3. DT-3 simplemente no lo vio.

### BUG-7 — Incierto, expuesto por DT-3

No hay evidencia de que existiera antes, pero tampoco de que no. Razón: antes de DT-3, el pipeline nunca llegaba a la generación de propuesta (BUG-1: pain_ledger vacío hacía fallar el pipeline en FASE-3 con datos default → G9 FAIL → delivery bloqueado). Nunca se ejecutaba `v4_proposal_generator.py`. DT-3, al fixear BUG-1, destapó esta parte. Los commercial gates probablemente siempre existieron en el código pero nunca se ejercitaron con datos reales.

### BUG-8 — Preexistente, documentado, expuesto por DT-3

Documentado en skill `iah-cli-v4complete-flow-validation` §"Scenarios Financial Logic: Optimista Can Be Negative":

> "The 'optimistic' scenario can produce a negative value representing equilibrium/break-even"

DT-3 no tocó `scenario_calculator.py`. Antes de DT-3, los escenarios se calculaban con datos fantasma (pain_ledger vacío → 0 entries → sin pain → sin costos). Con BUG-1 fixeado, ahora hay 9 pains reales que el motor procesa, y el optimista se va a negativo porque los costos superan el upside. Bug viejo; DT-3 lo expuso al darle datos reales.

### BUG-9 — Agravado por DT-3 (único con responsabilidad directa)

DT-3 FASE-2 creó `AssetAlignmentMatrix` (nuevo contrato unificado) y lo conectó al publication gate G9, pero NO migró el consumidor en `delivery_quality_report.py`.

| Antes de DT-3 | Después de DT-3 |
|---------------|-----------------|
| Ambos G9 usaban ProposalAssetMatrix → consistente (aunque incorrecto) | Publication G9 = AssetAlignmentMatrix (8/8), delivery quality G9 = ProposalAssetMatrix (5/8) → divergente |

Unificación parcial agravó el problema: donde antes había consistencia (un solo sistema), ahora hay divergencia (dos).

### BUG-10 — Preexistente, sin relación con DT-3

`PainSolutionMapper` asigna `monthly_report` a un pain que no existe en el ledger del hotel. DT-3 no tocó ese mapper. Bug de mapping preexistente que simplemente no se había observado porque antes no se generaban suficientes assets para notarlo.

---

## Patrón dominante

DT-3 fue un **destapador de bugs**, no un generador. Al fixear la causa raíz (BUG-1: pain_ledger vacío), el pipeline empezó a llegar a partes del código que nunca se ejercitaban con datos reales. Los bugs que emergieron son en su mayoría preexistentes. Excepción: BUG-9, donde DT-3 dejó trabajo a medias.

Esto es esperable en cualquier refactor: arreglar el eslabón más temprano de la cadena revela los eslabones siguientes que también estaban rotos pero nunca se alcanzaban.

---

## Orden de ataque recomendado (heredado del documento principal)

```
BUG-8 (scenario optimista negativo) → fix: clamp max(0, calculated)
   └── Desbloquea CG-SCENARIO-ORDER + CG-SCENARIO-NEGATIVE + CG-ROI-NEGATIVE
       └── BUG-6 (coverage gate falso positivo WhatsApp)
           └── Fix: coverage gate debe consultar SitePresenceChecker
               └── BUG-9 (divergencia G9)
                   └── Fix: migrar delivery_quality_report G9 a AssetAlignmentMatrix
                       └── BUG-7 (commercial gates visibilidad en gate_report)
                           └── BUG-10 (AssetSemantics monthly_report huérfano)
```

## Restricción crítica heredada

> NO modificar `scenario_calculator.py` sin N≥5 observaciones (mismo principio que PAIN_SOLUTION_MAP). Evaluar si el fix de BUG-8 califica como "bug fix" (cálculo incorrecto → optimista no puede ser negativo) vs "class-level change" (cambia la fórmula para todos los hoteles).

---

## Referencias en disco

- **Análisis completo (20.7 KB)**: `/mnt/c/Users/Jhond/Github/iah-cli/.opencode/plans/DT-3-TECH-DEBT-2026-07-25/08-analisis-post-implementacion.md`
- **Contexto DT-3 origen**: `/mnt/c/Users/Jhond/Github/iah-cli/.opencode/context/CONTEXT-DT-3-TECH-DEBT-POST-DT2.md`
- **Evidencia ejecución fresca**: `/mnt/c/Users/Jhond/Github/iah-cli/output/clientes/v4_complete/zione/v4_audit/`
- **BLOCKED_BY_GATES.md**: `/mnt/c/Users/Jhond/Github/iah-cli/output/clientes/v4_complete/BLOCKED_BY_GATES.md`
- **Sesión origen**: 20260725_210646_571283 (deepseek-v4-pro, 68 mensajes, terminada 21:23)

---

*Contexto preservado el 2026-07-25 desde sesión cerrada. Listo para ser cargado en una nueva sesión de planificación DT-4 sin perder la clasificación de bugs.*
