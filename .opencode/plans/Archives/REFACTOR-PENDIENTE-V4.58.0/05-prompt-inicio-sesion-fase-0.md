# FASE-0: Verificación y Preparación

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DELEGAR vía `delegate_task` con toolsets `['terminal', 'file']`

## Contexto previo

Primera fase del plan REFACTOR-PENDIENTE-V4.58.0. No hay fases previas.

El contexto del plan está en `/.opencode/context/Historico/Pendiente.md` y reporta:
- 5 gaps confirmados (IMP-03, MIN-01, MIN-02, MIN-03, F5)
- 1 bug de gates (F7)
- 1 deuda técnica (template embebido muerto)
- 2 gaps ya resueltos (F0, F4)

## Objetivo de esta fase

Confirmar el estado actual del código contra los claims del documento `Pendiente.md`,
verificando línea por línea que cada hallazgo sigue vigente antes de intervenir.

## Verificación pre-ejecución

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
git status
git log --oneline -5
```

---

### Tareas

- [ ] **T1: Verificar IMP-03 (CAPEX breakdown sin consumir)**
  ```bash
  # Verificar que _build_capex_breakdown_table() existe pero no se consume
  grep -n "capex_breakdown_table" modules/commercial_documents/v4_proposal_generator.py
  grep -n "capex_breakdown_table" modules/commercial_documents/templates/propuesta_v6_template.md
  # Debe aparecer en el .py pero NO en el template (eso es el bug)
  ```
  
- [ ] **T2: Verificar F7 (discrepancia entre gates)**
  ```bash
  # Verificar que financial_validity usa heurística propia
  grep -n "financial_validity" modules/quality_gates/publication_gates.py
  grep -n "default.*legacy\|legacy.*default" modules/quality_gates/publication_gates.py
  # Verificar que tier_c_onboarding_required usa _determine_evidence_tier()
  grep -n "tier_c_onboarding_required\|_determine_evidence_tier" modules/quality_gates/publication_gates.py
  ```

- [ ] **T3: Verificar MIN-02 (ADR no evidenciado)**
  ```bash
  # Verificar que adr no existe en benchmarks
  grep -n "adr" config/regional_benchmarks.yaml
  # Verificar adr siempre None en coherence checklist
  grep -n "adr" modules/commercial_documents/v4_proposal_generator.py
  # Verificar que _extract_adr_from_audit existe en diagnostic
  grep -n "_extract_adr_from_audit" modules/commercial_documents/v4_diagnostic_generator.py
  ```

- [ ] **T4: Verificar MIN-01, MIN-03 y dead code**
  ```bash
  # MIN-01: status_quo no existe
  grep -rn "status_quo" modules/commercial_documents/
  # MIN-03: _build_closing_pitch no existe
  grep -n "_build_closing_pitch" modules/commercial_documents/v4_proposal_generator.py
  # Texto duro en template L214-220
  grep -n "SIGUIENTE PASO\|closing_pitch" modules/commercial_documents/templates/propuesta_v6_template.md
  # Dead code: template embebido
  grep -n "EMBEDDED_TEMPLATE\|embedded_template\|template_embebido" modules/commercial_documents/v4_proposal_generator.py
  ```

### Verificación de tests existentes

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/ --timeout=60 -x -q 2>&1 | tail -20
```

Documentar cuántos tests pasan actualmente (baseline).

### Tabla de verificación (completar durante la fase)

| Gap | Claim del Pendiente.md | Verificado | Estado actual |
|-----|----------------------|------------|---------------|
| IMP-03 | capex_breakdown_table producido pero no consumido | ? | ? |
| F7 | financial_validity usa heurística != _determine_evidence_tier | ? | ? |
| MIN-02 | adr no en benchmarks, siempre None en coherence | ? | ? |
| MIN-01 | status_quo no existe en ningún lado | ? | ? |
| MIN-03 | _build_closing_pitch no existe, texto duro | ? | ? |
| Dead code | Template embebido L575-605 nunca usado | ? | ? |
| F5 | adr siempre "Pendiente" en checklist | ? | ? |

### Restricciones

- **NO modificar código** en esta fase — solo lectura y verificación
- **NO ejecutar v4complete** — solo grep y lectura
- **NO ejecutar log_phase_completion** — esta fase es preparación
- Máximo 60 iteraciones (R2)
- Documentar cualquier discrepancia entre claims y código actual

### Criterios de completitud

- [ ] Los 7 gaps verificados contra código vivo
- [ ] Tabla de verificación completada
- [ ] Baseline de tests documentado (N passed, M failed)
- [ ] Cualquier discrepancia con Pendiente.md documentada
- [ ] Confirmación: el plan es ejecutable tal como está, o necesita ajustes

### Próxima sesión

```
Carga y ejecuta /.opencode/plans/Archives/REFACTOR-PENDIENTE-V4.58.0/05-prompt-inicio-sesion-fase-1A.md
```

Esa fase implementa IMP-03 (añadir `${capex_breakdown_table}` al template) y F7 (unificar lógica de gates).
