# FASE-C — Quality Report Post-Gen + G9 Dead Gate (P-03, P-05)

> **Plan**: DT-2-DELIVERY-CONTRACT-RESIDUAL-2026-07-24
> **Fase**: C (tercera fase de código — MAYOR COMPLEJIDAD TÉCNICA)
> **Findings**: P-03 (score pre-gen), P-05 (G9 dead gate)
> **Ejecución**: DIRECTA (no subagent — decisión arquitectónica requerida)
> **Dependencias**: FASE-A y FASE-B completadas
> **Próxima fase**: FASE-D

---

## Contexto

Esta es la fase de MAYOR COMPLEJIDAD TÉCNICA del plan. Combina un fix de
severidad ALTA (P-05: dead gate) con un fix de severidad MEDIA (P-03: score
pre-gen), ambos en el mismo archivo, y requiere una decisión arquitectónica.

### P-03: delivery_quality_report no refleja score post-generación (TD-4)

**Severidad**: MEDIA

**Evidencia**:
- `delivery_quality_report.json` reporta `coherence_score: 0.84`
- `coherence_validation.json` (pre-gen): `overall_score: 0.84`
- `coherence_validation_post_gen.json` (post-gen): `overall_score: 0.82`
- `asset_generation_report.json`: `coherence_score_pre: 0.84`, `coherence_score_post: 0.82`

El quality report usa el score PRE-generación (0.84) en vez del POST-generación (0.82).

**Causa raíz verificada en código vivo**:
`delivery_quality_report.py` L122:
```python
coherence_data = self._load_json(v4_audit_path / "coherence_validation.json")
```
No existe lógica para buscar `coherence_validation_post_gen.json`.

### P-05: proposal_asset_gate es un DEAD GATE en delivery_quality_report

**Severidad**: ALTA

**Evidencia**:
```json
"proposal_asset_gate": {"passed": true, "gate": "G9"}
```
Pero este gate **nunca es evaluado**. Es un default hardcodeado.

**Causa raíz verificada en código vivo**:
L238:
```python
proposal_asset_gate=gate_results.get("proposal_asset_alignment", {"passed": True, "gate": "G9"}),
```
El diccionario `gate_results` se popula con claves: `"coherence"`, `"coverage"`,
`"asset_specificity"`, `"evidence"`. La clave `"proposal_asset_alignment"` **nunca
se inserta**. El `.get()` siempre retorna el default.

L205:
```python
blocking_gates = [
    name for name, result in gate_results.items()
    if not result["passed"] and name in ("coherence", "coverage", "evidence", "proposal_asset_alignment")
]
```
`"proposal_asset_alignment"` está listado como potencialmente bloqueante, pero como
nunca existe en `gate_results`, nunca puede fallar.

**Impacto**: El quality report puede dar "PASS" con "4/4 gates" aunque la
alineación propuesta→asset esté rota.

---

## Decisión Arquitectónica: Implementar vs Eliminar G9

### Opción 1: Implementar G9 (RECOMENDADA)
- Después de cargar `coverage_data`, evaluar la alineación usando
  `ProposalAssetMatrix` o `AlignmentReport`
- Poblar `gate_results["proposal_asset_alignment"]` con el resultado real
- Ventaja: el reporte refleja la realidad comercial
- Desventaja: acopla `delivery_quality_report.py` con `proposal_asset_alignment.py`

### Opción 2: Eliminar G9 del reporte
- Eliminar el campo del dataclass (L44: `proposal_asset_gate: dict`)
- Eliminar la referencia en L205 (`blocking_gates`)
- Eliminar el default en L238
- Ventaja: no mentir en el reporte
- Desventaja: pierde la capacidad de reportar alineación comercial

**Decisión del plan**: Implementar G9 (Opción 1) por valor a largo plazo.
Si la implementación resulta demasiado compleja para la fase, fallback a
eliminación (Opción 2) como deuda técnica documentada.

---

## Tareas

### Tarea C-1: Fix P-03 — Leer coherence_validation_post_gen.json con fallback

**Archivo**: `modules/quality_gates/delivery_quality_report.py`

1. Leer el método `generate()` (L118-244)
2. En L122, donde carga `coherence_validation.json`:
   ```python
   coherence_data = self._load_json(v4_audit_path / "coherence_validation.json")
   ```
3. Cambiar a lógica de fallback post-gen:
   ```python
   # Intentar post-gen primero, fallback a pre-gen
   post_gen_path = v4_audit_path / "coherence_validation_post_gen.json"
   pre_gen_path = v4_audit_path / "coherence_validation.json"

   coherence_post_data = None
   if post_gen_path.exists():
       coherence_post_data = self._load_json(post_gen_path)
   coherence_pre_data = self._load_json(pre_gen_path)

   # Usar post-gen si existe, sino pre-gen
   coherence_data = coherence_post_data or coherence_pre_data
   ```
4. Reportar ambos scores si existen (transparencia):
   - En el dataclass, considerar campos `coherence_score_pre` y `coherence_score_post`
   - Si solo existe uno, mantener el campo actual `coherence_score`
5. Actualizar `_extract_coherence()` (L269-279) para manejar ambos escenarios

### Tarea C-2: Fix P-05 — Implementar G9 proposal_asset_alignment gate

**Archivo**: `modules/quality_gates/delivery_quality_report.py`

1. Después de evaluar G6, G7, G8 (coherence, coverage, evidence), agregar
   evaluación de G9:
   ```python
   # G9: Proposal-Asset Alignment
   # Intentar cargar proposal_asset_matrix.json desde el v4_audit path
   matrix_path = v4_audit_path / "proposal_asset_matrix.json"
   if matrix_path.exists():
       matrix_data = self._load_json(matrix_path)
       # Evaluar: ¿todos los servicios propuestos tienen assets alineados?
       aligned = matrix_data.get("aligned_services", 0)
       total = matrix_data.get("total_services", 0)
       passed = aligned == total if total > 0 else True
       gate_results["proposal_asset_alignment"] = {
           "passed": passed,
           "gate": "G9",
           "aligned": aligned,
           "total": total
       }
   else:
       # Si no hay matrix, no evaluar — pero NO usar default True
       gate_results["proposal_asset_alignment"] = {
           "passed": True,  # Sin matrix, no hay forma de evaluar
           "gate": "G9",
           "skipped": True,
           "reason": "proposal_asset_matrix.json not found"
       }
   ```
2. El default en L238 (`gate_results.get("proposal_asset_alignment", {"passed": True, "gate": "G9"})`)
   ya no se alcanzará porque la clave siempre existirá en `gate_results`
3. Verificar que el campo `proposal_asset_gate` en el dataclass (L44) refleje
   el resultado real, no el default

**NOTA**: Si la implementación de G9 con ProposalAssetMatrix resulta demasiado
compleja (imports cruzados, dependencias circulares, schema desconocido), fallback
a Opción 2 (eliminar G9) documentado como deuda técnica:
- Eliminar `proposal_asset_gate: dict` del dataclass L44
- Eliminar `"proposal_asset_alignment"` de L205 blocking_gates list
- Eliminar L238 default
- Documentar en commit: "fix(delivery): P-05 G9 gate eliminated (debt: implement in v4.64.0)"

### Tarea C-3: Verificar que los 28 tests existentes siguen pasando

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/delivery/test_delivery_contract.py -v
```

---

## Criterios de Completitud

- [ ] P-03: `delivery_quality_report.py` lee `coherence_validation_post_gen.json` cuando existe
- [ ] P-03: Si ambos scores existen, se reportan ambos (pre y post) para transparencia
- [ ] P-05: G9 se evalúa realmente (gate_results["proposal_asset_alignment"] se popula)
- [ ] P-05: O G9 se elimina del dataclass + blocking_gates + default (opción 2, documentada)
- [ ] 28 tests existentes pasan
- [ ] Commit con mensaje descriptivo indicando qué opción se tomó para G9

---

## Post-Ejecución

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-C-DT2 --desc "P-03_post_gen_coherence_score_P-05_G9_gate_implemented_or_removed"
```

---

## Próxima Sesión

```
Carga el plan DT-2 en /mnt/c/Users/Jhond/Github/iah-cli/.opencode/plans/DT-2-DELIVERY-CONTRACT-RESIDUAL-2026-07-24/
Ejecuta FASE-D: 05-prompt-fase-D.md (P-04 + P-06: proposal_asset_matrix path + packaging)
```
