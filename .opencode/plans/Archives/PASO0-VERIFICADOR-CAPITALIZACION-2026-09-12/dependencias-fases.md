# dependencias-fases — PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12

## Diagrama

```
Paso 0  00-lecciones-capitalizadas.md        [✅ 2026-09-12, ANTES del maestro]
   │      (gate §2.5 del executor: sin archivo lleno no hay prompts de fase)
   ▼
FASE-V1 decisión Q1–Q5 + contrato C0–C8      [✅ commits de docs]
   │      AC-A1…AC-A5 · evidence/FASE-V1/decision-verificador.md
   ▼
FASE-V2 script + tests + NR7 + cableado      [pendiente]
   │      AC-B1…AC-B5 · toca: scripts/, tests/, scripts/git_hooks/pre-commit,
   │      scripts/run_all_validations.py
   ▼
FASE-V3 cierre documental + archivado        [pendiente]
          AC-C1, AC-C2, AC-A5 · toca: template, executor, CHANGELOG,
          .opencode/plans/Archives/TRIBUNAL-ENFORCEMENT-OBS-2026-09-11/06-checklist-implementacion.md
          y el cierre en orden R2.10: write-back → índice → git mv → índice otra vez
```

## Tabla de conflictos potenciales

| Archivo | Lo tocan | Conflicto con | Mitigación |
|---------|----------|---------------|------------|
| `scripts/git_hooks/pre-commit` | V2 (`[7/7]` y renumeración) | El hook se ejecuta **contra el commit que lo modifica**: si el `[7/7]` nuevo está mal, el propio commit de V2 queda bloqueado | Probar el script contra el árbol real **antes** de cablearlo; `--no-verify` queda prohibido por restricción de fase |
| `scripts/run_all_validations.py` | V2 (check `[9/9]`, renumeración `[n/8]`→`[n/9]`, `[9/11]`→`[10/13]`… ) | El plan `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` no toca este archivo (perímetro: judge/acta/revisores) | Sin conflicto real; registrado para que no se descubra tarde |
| `.opencode/plans/Archives/TRIBUNAL-ENFORCEMENT-OBS-2026-09-11/06-checklist-implementacion.md` | V3 (cierre del ítem (i) de su §Deuda) | Es un plan **vivo** de otro perímetro, y su FASE-P1 sigue pendiente | Solo se anota el cierre de ese ítem con fecha y dueño; no se toca ningún AC ni decisión suya |
| `.opencode/LECCIONES-INDEX.md` y su JSON | V1 (generado), V3 (dos veces, por R2.10) | `[6/6]` bloquea cualquier commit que edite un `.md` de `plans/` sin regenerarlo | Regenerar el índice **en el mismo commit** (invariante verificado de R2.10) |
| `AGENTS.md` | V3 si menciona el conteo de checks | Pre-commit `agent-ecosystem` y `version-sync` | No editar versiones a mano; `sync_versions.py` si hace falta |
| `VERSION.yaml` | **nadie** (decisión Q5) | Choque con la reserva de `4.77.0` del predecesor | AC-A5 verifica que su diff esté vacío |

## Precondiciones externas

- Ninguna corrida de `v4complete` ni de `onboard` es necesaria: este plan no toca el pipeline (por eso
  R2.6 está en §3 del `00-` como descartado con motivo).
- El notebook QMind `iah-cli-lecciones` está accesible (medido: 3 `retrieve` con `total:` > 0), así que el
  write-back de FASE-V3 no necesita el fallback de indisponibilidad.
