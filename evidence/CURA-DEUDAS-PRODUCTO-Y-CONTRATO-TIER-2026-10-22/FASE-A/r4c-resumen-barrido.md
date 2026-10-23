# R4c — Barrido de lectores huérfanos del refactor `1501dd8` — FASE-A

## Contratos que el refactor tocó (atributo → método/instancia)

Derivado de `git show 1501dd8 -- modules scripts` (crudo:
`r4c-contratos-retirados-1501dd8.txt`, `r4c-refactor-1501dd8-stat.txt`).

| Contrato retirado | Sustituto | Superficie |
|-------------------|-----------|------------|
| `FinancialFactors.SUPERPOSITION_FACTOR` (atributo de clase) | `get_superposition_factor()` (lee `config/financial_defaults.yaml`) | `modules/utils/financial_factors.py` |
| `FinancialFactors.DEFAULTS` (dict de clase) | `_load_defaults()` (+ `_FALLBACK_DEFAULTS`) | `modules/utils/financial_factors.py` |
| `TIER_CONFIG`, `GATE_MIN_RATIO`, `GATE_MAX_RATIO`, `GATE_IDEAL_RATIO` (attrs de clase) | attrs de instancia desde `config/pricing.yaml` en `__init__` | `modules/financial_engine/pricing_calculator.py` |
| `_build_guarantees_section` (método hardcode) | sección desde config (método retirado) | `modules/commercial_documents/v4_proposal_generator.py` |
| `_pain_to_brecha(self, pain)` (firma vieja) | `_pain_to_brecha(self, pain, region=…, …)` (firma nueva) | `modules/commercial_documents/v4_diagnostic_generator.py` |

## Superficies revisadas y veredicto

Grep repo-wide de lectores (crudo: `r4c-barrido-lectores.txt`; `git log -S`:
`r4c-git-log-S-superposition.txt`). Excluidos del barrido por rol: `venv/`,
`.venv-wsl/`, `.git/`, `__pycache__/`, `node_modules/`, `Archives/`.

| Contrato | Lectores en código vivo | Veredicto |
|----------|-------------------------|-----------|
| `SUPERPOSITION_FACTOR` | `main.py` (`_map_audit_to_spark_data`) y `modules/analyzers/gap_analyzer.py` (`_basic_analysis`) | Los 2 huérfanos vivos de este contrato: **retirado** (Tarea 1) y **reparado** (Tarea 2). 0 restantes |
| `FinancialFactors.DEFAULTS` | 0 externos (tests usan `_load_defaults`) | Sin huérfanos |
| `TIER_CONFIG` / `GATE_*` | lectores válidos sobre attrs de instancia (`self.…` / `calc.…`); tests de pricing casan | La remoción fue clase→instancia: sin lectura rota |
| `_pain_to_brecha` (firma nueva) | `self._pain_to_brecha(pain, region=…)` en el propio generador + tests con `region` por defecto | Sin huérfanos; consumidores casan con la firma viva |
| `_build_guarantees_section` | solo aparece en tests que afirman su **ausencia** | Consistente (método retirado a propósito) |

## Hallazgos adicionales (sin expansión de alcance)

1. `temp/fase_d_backup/main.py` y `temp/fase_f_recovery_backup/main.py` — copias
   de respaldo en `temp/`, fuera de las rutas del producto — conservan el lector
   roto `FinancialFactors.SUPERPOSITION_FACTOR`. **Dueño: Operador** (decidir la
   depuración de `temp/`); FASE-A no lo toca.
2. El docstring de clase de `FinancialFactors` aún nombra `SUPERPOSITION_FACTOR`
   como si fuera un atributo (fósil textual: el valor vive en
   `config/financial_defaults.yaml` vía `get_superposition_factor()`).
   **Dueño: FASE-H2** (honestidad de texto).

No se expandió alcance: ambos hallazgos van a `10-analisis` §Seguimientos con
dueño, según el criterio de aceptación de Tarea 4.
