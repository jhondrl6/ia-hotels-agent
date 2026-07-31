# Prompt de Inicio de Sesión: FASE-3 — Decisión Producto monthly_report

**Fase**: FASE-3 — FIX-PRIORITY-4: BUG-10 monthly_report excluido de alignment counts
**Plan**: DT-4-ROOT-CAUSE-2026-07-25
**Sesión**: Nueva (fresh)
**Iteraciones máx**: 60
**Complejidad**: BAJA
**Ejecución**: **SUBAGENTE** ✅ — delegate_task viable (1-2 líneas)
**Depende de**: — (independiente)
**Bloquea a**: FASE-RELEASE

---

## Objetivo

Resolver BUG-10: `monthly_report` aparece como `NO_BREACH` en la matriz de alignment sin valor comercial real. No es un bug — es una decisión de producto pendiente. La recomendación es **Opción B**: remover `monthly_report` de `PROPOSAL_SERVICE_TO_ASSET`.

---

## Contexto

`monthly_report` se genera rutinariamente como asset "always-on" (reporting mensual). No tiene pain asociado en el ledger por diseño — no es solución a un pain, es entrega complementaria. Aparece como `NO_BREACH` con confidence 0.0 en la matriz, inflando el conteo de servicios sin aportar valor.

**Opción B (RECOMENDADA)**: Remover `monthly_report` de `PROPOSAL_SERVICE_TO_ASSET`. Se sigue generando como anexo, pero no se factura por separado ni cuenta en alignment.

**Opción A (alternativa)**: Agregar status `STANDALONE_ASSET` al enum y filtrarlo de `alignment_percentage`. Más código, mismo resultado.

---

## Tareas

### T1: Remover `monthly_report` de `PROPOSAL_SERVICE_TO_ASSET`

**Archivo**: `modules/asset_generation/proposal_asset_alignment.py`

```bash
# 1. Localizar PROPOSAL_SERVICE_TO_ASSET
grep -n "monthly_report" modules/asset_generation/proposal_asset_alignment.py
```

Si `monthly_report` está en `PROPOSAL_SERVICE_TO_ASSET`, remover esa entrada.

```python
# Si monthly_report está en PROPOSAL_SERVICE_TO_ASSET, remover la línea completa.
# El asset se sigue generando — solo se excluye del conteo de alignment.
```

### T2: Actualizar tests

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# 1. Verificar qué tests referencian monthly_report en alignment
grep -rn "monthly_report" tests/ | grep -i "align\|matrix\|proposal_asset"

# 2. Actualizar aserciones que esperaban monthly_report en la matriz
#    → ajustar conteos esperados (total_services baja en 1)

# 3. Ejecutar tests
./venv/Scripts/python.exe -m pytest tests/ -v -k "monthly_report or proposal_asset"
./venv/Scripts/python.exe -m pytest -q
```

---

## Criterios de Completitud

- [ ] `monthly_report` removido de `PROPOSAL_SERVICE_TO_ASSET` (o marcado STANDALONE_ASSET si Opción A)
- [ ] Tests actualizados reflejan el nuevo conteo
- [ ] 100 tests existentes siguen PASS
- [ ] git commit con mensaje: "fix(BUG-10): exclude monthly_report from proposal service alignment counts"

---

## delegate_task Prompt (para subagente)

```
Implement FASE-3 of DT-4 plan for iah-cli project at /mnt/c/Users/Jhond/Github/iah-cli.

GOAL: Fix BUG-10 — monthly_report appears as NO_BREACH in alignment matrix but has no commercial value (it's an always-on complement, not a pain-driven service).

FIX (Opción B — recommended): Remove monthly_report from PROPOSAL_SERVICE_TO_ASSET in proposal_asset_alignment.py. The asset still gets generated, it just doesn't count toward alignment.

TASKS:
1. grep -n "monthly_report" modules/asset_generation/proposal_asset_alignment.py
2. Remove the monthly_report entry from PROPOSAL_SERVICE_TO_ASSET dict
3. Update tests that reference monthly_report in alignment counts (adjust expected total_services down by 1)
4. Run: ./venv/Scripts/python.exe -m pytest tests/ -v -k "proposal_asset"
5. Run full suite: ./venv/Scripts/python.exe -m pytest -q
6. git add + commit: "fix(BUG-10): exclude monthly_report from proposal service alignment counts"

RESTRICTIONS:
- Do NOT modify monthly_report_generator.py
- Do NOT modify pain_ledger or pain mappings
- Keep existing tests passing
```

---

## Post-Ejecución (OBLIGATORIO)

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-3 --desc "BUG-10_monthly_report_excluido_alignment" --check-manual-docs
```

---

## Siguiente Sesión

**FASE-4** — N1: Higiene nombres gates duplicados (o directamente FASE-RELEASE si FASE-4 ya se ejecutó)
