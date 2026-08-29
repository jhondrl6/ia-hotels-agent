# FASE-E — Tests Nuevos P-01..P-07 (7 Fixes)

> **Plan**: DT-2-DELIVERY-CONTRACT-RESIDUAL-2026-07-24
> **Fase**: E (fase de tests)
> **Findings**: Tests para P-01 a P-07
> **Ejecución**: DIRECTA (no subagent — WSL import cascade para pytest)
> **Dependencias**: FASE-A, B, C, D completadas (todos los fixes aplicados)
> **Próxima fase**: FASE-F

---

## Contexto

Las fases A-D implementaron los 7 fixes. Esta fase agrega tests de contrato
que validan cada fix y previenen regresiones. Los 28 tests existentes deben
seguir pasando sin modificación (o con modificaciones documentadas en FASE-B).

**Ejecución DIRECTA**: Los tests requieren importar módulos del proyecto
(`delivery_context`, `delivery_packager`, `delivery_quality_report`). En WSL,
los subagents no pueden importar módulos del Windows venv (import cascade).
Usar `subprocess.run` con `venv/Scripts/python.exe` para ejecutar tests
fuera de proceso.

---

## Tareas

### Tarea E-1: Tests para P-01 (conteo README post-manifest)

**Archivo**: `tests/delivery/test_delivery_contract.py`

Agregar tests:
```python
def test_readme_total_files_matches_manifest(self, tmp_path):
    """P-01: README {{TOTAL_FILES}} debe coincidir con MANIFEST.json total_files."""
    # Crear DeliveryContext con N archivos
    # Ejecutar packager
    # Leer README_DELIVERY.md y MANIFEST.json del ZIP
    # Assert: README Contents count == MANIFEST total_files
    # (debe incluir meta-archivos: MANIFEST.json + README_DELIVERY.md)

def test_readme_total_size_matches_manifest(self, tmp_path):
    """P-01: README {{TOTAL_SIZE}} debe coincidir con MANIFEST.json total_size_bytes."""
    # Mismo setup, verificar size bytes
```

### Tarea E-2: Tests para P-02 (exclusión mutua advisory)

```python
def test_advisory_asset_not_in_delivered_section(self):
    """P-02: Asset con is_advisory=True y state=DELIVERED NO aparece en delivered_assets."""
    # Crear DeliveryContext con asset: state=DELIVERED, is_advisory=True
    # Assert: asset NOT in ctx.delivered_assets
    # Assert: asset IN ctx.advisory_assets

def test_advisory_asset_not_in_estimated_section(self):
    """P-02: Asset con is_advisory=True y state=ESTIMATED NO aparece en estimated_assets."""
    # Crear DeliveryContext con asset: state=ESTIMATED, is_advisory=True
    # Assert: asset NOT in ctx.estimated_assets
    # Assert: asset IN ctx.advisory_assets

def test_non_advisory_asset_still_in_state_section(self):
    """P-02: Asset con is_advisory=False y state=DELIVERED SI aparece en delivered_assets."""
    # Crear DeliveryContext con asset: state=DELIVERED, is_advisory=False
    # Assert: asset IN ctx.delivered_assets
    # Assert: asset NOT in ctx.advisory_assets

def test_advisory_partition_is_disjoint(self):
    """P-02: delivered_assets ∩ advisory_assets == vacío. estimated_assets ∩ advisory_assets == vacío."""
    # Crear contexto con mix de assets (algunos advisory, algunos no)
    # Verificar que no hay intersección entre las 3 secciones
```

### Tarea E-3: Tests para P-03 (post-gen coherence) y P-05 (G9 gate)

```python
def test_quality_report_uses_post_gen_coherence(self, tmp_path):
    """P-03: delivery_quality_report usa coherence_validation_post_gen.json cuando existe."""
    # Crear v4_audit dir con:
    #   coherence_validation.json (pre-gen, score 0.84)
    #   coherence_validation_post_gen.json (post-gen, score 0.82)
    #   asset_generation_report.json
    # Generar quality report
    # Assert: coherence_score == 0.82 (post-gen) o ambos scores reportados

def test_quality_report_falls_back_to_pre_gen(self, tmp_path):
    """P-03: Si no hay post-gen, usa pre-gen (backward compatible)."""
    # Crear v4_audit con solo coherence_validation.json
    # Assert: coherence_score == pre-gen value

def test_g9_gate_is_evaluated_not_default(self, tmp_path):
    """P-05: G9 proposal_asset_alignment se evalúa, no es default True."""
    # Crear v4_audit con proposal_asset_matrix.json mostrando misalignment
    # Generar quality report
    # Assert: proposal_asset_gate["passed"] == False (si hay misalignment)
    # Assert: proposal_asset_gate no es el default hardcodeado

def test_g9_gate_passes_when_aligned(self, tmp_path):
    """P-05: G9 pasa cuando todos los servicios están alineados."""
    # Crear v4_audit con proposal_asset_matrix.json mostrando alignment completo
    # Assert: proposal_asset_gate["passed"] == True
```

### Tarea E-4: Tests para P-06 (matrix empaquetada) y P-07 (enum)

```python
def test_proposal_asset_matrix_in_zip(self, tmp_path):
    """P-06: proposal_asset_matrix.json debe aparecer en el ZIP de entrega."""
    # Crear output con proposal_asset_matrix.json en v4_audit/
    # Ejecutar packager
    # Abrir ZIP y listar archivos
    # Assert: algún path contiene "proposal_asset_matrix"

def test_packager_uses_enum_not_string(self):
    """P-07: delivery_packager usa DeliveryAssetState enum, no string comparison."""
    # Este es un test de código estático: leer el archivo y verificar
    # que no hay `state.name ==` o `state.name in`
    # Alternativamente, test funcional: crear contexto con asset DELIVERED
    # y verificar que aparece en delivered list
```

---

## Criterios de Completitud

- [ ] 7 tests nuevos agregados (1 por finding mínimo, idealmente 9-11)
- [ ] Tests P-01: README count == MANIFEST count
- [ ] Tests P-02: advisory partition es disjunta
- [ ] Tests P-03: post-gen coherence usado cuando existe
- [ ] Tests P-05: G9 evaluado (no default)
- [ ] Tests P-06: matrix en ZIP
- [ ] Tests P-07: enum usado (no string)
- [ ] Total tests: 28 existentes + 7+ nuevos = 35+ todos pasan
- [ ] Commit con mensaje descriptivo

---

## Post-Ejecución

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-E-DT2 --desc "7_new_tests_for_P01_to_P07_contract_validation"
```

---

## Próxima Sesión

```
Carga el plan DT-2 en /mnt/c/Users/Jhond/Github/iah-cli//.opencode/plans/Archives/DT-2-DELIVERY-CONTRACT-RESIDUAL-2026-07-24/
Ejecuta FASE-F: 07-prompt-fase-F.md (v4complete Zi One + análisis post-implementación)
```
