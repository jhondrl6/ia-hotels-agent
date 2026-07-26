# FASE-3: v4complete Zi One Luxury + Verificación E2E Post-Fix

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: MIXTO — v4complete vía delegate_task (comando largo), análisis vía agente principal DIRECTO
> **Complejidad**: MEDIA
> **Iteraciones máx**: 60
> **⚠️ CONTIENE COMANDO LARGO**: v4complete (5-10 min, timeout=900s)
> **Depende de**: FASE-0 ✅, FASE-1 ✅, FASE-2 ✅
> **Bloquea a**: FASE-RELEASE

---

## Objetivo

Ejecutar `v4complete` para Zi One Luxury (https://zione.co/) y verificar que los 4 bugs corregidos en fases anteriores efectivamente se resolvieron:

1. **BUG-1**: pain_ledger se carga con 9 entries (no vacío)
2. **BUG-2**: G9 no aparece en warning_gates si está en blocking_gates
3. **BUG-3**: NO_BREACH no bloquea el delivery
4. **BUG-4 (P-04)**: El contrato unificado `AssetAlignmentMatrix` produce resultados correctos

Además, verificar que P-01, P-02, P-06 (fixes de DT-2) funcionan en un ZIP real.

---

## Contexto de Fases Anteriores

**FASE-0**: `_get_pipeline_path()` en main.py. 3 rutas flat corregidas.

**FASE-1**: `BLOCKING_GATE_NAMES` constante. G9 evalúa `status`. `actionable_services` excluye `NO_BREACH`.

**FASE-2**: `AssetAlignmentMatrix` reemplaza ProposalAssetMatrix + AlignmentReport. G9 consume `is_delivery_ready()`.

**Métricas de referencia (pre-fix, post-DT-2)**:
| Métrica | Valor |
|---------|-------|
| coherence_score | 0.82 |
| G9 status | FAIL (0/8 alineados) |
| Delivery status | BLOCKED |
| Tests | 42/42 PASS |
| ZIP generado | NO |

---

## Tareas

### T1: Ejecutar v4complete para Zi One Luxury (COMANDO LARGO)

**Ejecutar vía delegate_task** (MIXTO pattern — el subagente ejecuta el comando largo, el agente principal hace el análisis):

```bash
./venv/Scripts/python.exe main.py v4complete --url https://zione.co/
```

Timeout: 900s. El comando tarda 5-10 minutos de wall-clock. Usar `delegate_task` con `toolsets=["terminal"]` para no bloquear el agente principal.

### T2: Capturar evidencia (Protocolo de Evidencia Proactiva)

Inmediatamente después de completar v4complete, copiar los archivos de evidencia:

```bash
# Crear directorio de evidencia
mkdir -p .opencode/plans/DT-3-TECH-DEBT-2026-07-25/evidence/

# Copiar archivos clave
cp output/v4_complete/zione/v4_audit/pain_ledger.json evidence/pain_ledger.json
cp output/v4_complete/zione/v4_audit/proposal_asset_matrix.json evidence/proposal_asset_matrix.json
cp output/v4_complete/zione/v4_audit/delivery_quality_report.json evidence/delivery_quality_report.json
cp output/v4_complete/zione/v4_audit/coherence_validation.json evidence/coherence_validation.json
```

### T3: Verificación de Bugs (Matriz de Verificación)

Para cada bug, verificar contra los archivos de output:

| Bug | Qué verificar | Archivo | Esperado | ¿Superado? |
|-----|---------------|---------|----------|------------|
| BUG-1 | pain_ledger cargado | pain_ledger.json | ≥1 entry (antes: 0) | |
| BUG-1 | G1 sync ejecutado | coherence_validation.json | score = post-gen (antes: pre-gen) | |
| BUG-2 | G9 no en warning_gates | delivery_quality_report.json | "proposal_asset_alignment" NOT in warning_gates | |
| BUG-3 | NO_BREACH no bloquea | delivery_quality_report.json | passed=true si actionable_services > 0 | |
| BUG-4 | Contrato unificado funcional | proposal_asset_matrix.json | entries con status LINKED/NO_BREACH/MISSING_ASSET | |
| P-01 | README post-manifest correcto | MANIFEST.json + README.md en ZIP | Pass 3 recalculo aplicado | |
| P-02 | Advisory assets exclusión mutua | Secciones del README.md en ZIP | State-based sections correctas | |
| P-06 | proposal_asset_matrix.json per-hotel | Ruta del archivo | En zione/v4_audit/, no en v4_audit/ flat | |

---

## Criterios de Completitud

- [ ] v4complete ejecutado exitosamente para https://zione.co/
- [ ] ZIP generado (evidencia de que el delivery NO está bloqueado)
- [ ] pain_ledger.json tiene ≥1 entry (BUG-1 superado)
- [ ] G1 coherence sync funcional (coherence_validation.json tiene score post-gen)
- [ ] delivery_quality_report.json: "proposal_asset_alignment" NOT in warning_gates (BUG-2 superado)
- [ ] delivery_quality_report.json: passed=true para G9 (BUG-3 superado)
- [ ] proposal_asset_matrix.json usa taxonomía unificada (BUG-4/P-04 verificado)
- [ ] P-01, P-02, P-06 verificados en ZIP real
- [ ] Evidencia copiada a `evidence/`

---

## Restricciones

- **NO modificar código** — esta fase es solo verificación
- **NO hacer fix si algo falla** — documentar el fallo y reportar; los fixes van en nueva sesión
- **NO ejecutar v4complete para otro hotel** — solo Zi One Luxury

---

## delegate_task Prompt (para v4complete)

```
GOAL: Execute v4complete pipeline for Zi One Luxury hotel and capture the output.

CONTEXT:
Project: /mnt/c/Users/Jhond/Github/iah-cli
Command: ./venv/Scripts/python.exe main.py v4complete --url https://zione.co/
Hotel: Zi One Luxury (https://zione.co/)
Expected runtime: 5-10 minutes

TASKS:
1. Run the v4complete command with terminal(timeout=900)
2. Wait for completion (the command generates diagnostics, proposal, assets, delivery package)
3. After completion, verify the output exists:
   - output/v4_complete/ should contain zione/ directory
   - output/v4_complete/ should contain a .zip file
4. Copy key evidence files to .opencode/plans/DT-3-TECH-DEBT-2026-07-25/evidence/:
   - pain_ledger.json
   - proposal_asset_matrix.json
   - delivery_quality_report.json
   - coherence_validation.json

RESTRICTIONS:
- Do NOT modify any source code
- Do NOT run tests
- If v4complete fails or times out, report the error output and exit code
- If the output directory doesn't exist yet, create it with mkdir -p
```

---

## Post-Ejecución (OBLIGATORIO)

```bash
cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe scripts\log_phase_completion.py --fase FASE-3 --plan DT-3-TECH-DEBT-2026-07-25 --desc v4complete_ZiOne_verification"
```

---

## Próxima Sesión

**FASE-RELEASE**: Documentación, version bump a v4.64.0, CHANGELOG, git tag, pre-commit validation.
