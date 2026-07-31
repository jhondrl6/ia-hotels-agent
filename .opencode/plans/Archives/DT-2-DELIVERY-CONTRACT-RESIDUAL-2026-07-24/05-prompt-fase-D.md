# FASE-D — proposal_asset_matrix Path + Packaging (P-04, P-06)

> **Plan**: DT-2-DELIVERY-CONTRACT-RESIDUAL-2026-07-24
> **Fase**: D (cuarta fase de código)
> **Findings**: P-04 (matrix diverge + no empaquetado), P-06 (matrix no se empaqueta)
> **Ejecución**: DIRECTA (no subagent — tracing de path mismatch entre 3 archivos)
> **Dependencias**: FASE-A, B, C completadas
> **Próxima fase**: FASE-E

---

## Contexto

### P-04: proposal_asset_matrix diverge del alignment gate (TD-2)

**Severidad**: MEDIA (AMPLIFICADO)

**Evidencia**:
- `proposal_asset_matrix.json` **NO existe en el ZIP** (`zione_20260724.zip`)
- La matrix se genera en `v4_proposal_generator.py` L642 con ruta
  `output_path / "v4_audit" / "proposal_asset_matrix.json"` = `output/v4_complete/v4_audit/`
- El packager opera sobre `source_dir = output/v4_complete/zione/`, que NO incluye
  la ruta `output/v4_complete/v4_audit/`
- El proposal_asset_matrix tiene definición de cobertura diferente al alignment gate:
  - `proposal_asset_matrix`: "¿el servicio cumple la propuesta comercial?"
  - alignment gate: "¿el asset existe (generated OR present in production)?"

**Causa raíz verificada en código vivo**:
- `v4_proposal_generator.py` L642: `matrix_path = output_path / "v4_audit" / "proposal_asset_matrix.json"`
- `proposal_asset_alignment.py` L562: `def save(self, entries, path)`
- `delivery_packager.py` L103-117: `source_dir` se construye de `output_dir` o `hotel_id` subdir
- `_collect_files` (L233-261) recoge archivos de `source_dir.rglob("*")`

### P-06: proposal_asset_matrix.json no se empaqueta en el delivery

**Severidad**: MEDIA

**Causa raíz**: Path mismatch entre el generador de la matrix y el packager.
La matrix se genera en el directorio flat `output/v4_complete/v4_audit/` mientras
el packager recoge archivos del subdirectorio del hotel `output/v4_complete/zione/v4_audit/`.

**Fix propuesto**:
1. Asegurar que la matrix se guarde en la misma ruta que `_collect_files()` recoge
   (`source_dir / "v4_audit" / "proposal_asset_matrix.json"`)
2. O incluir la ruta del directorio flat en `_collect_files()`

---

## Tareas

### Tarea D-1: Fix P-06 — Corregir path de guardado de proposal_asset_matrix

**Archivos**: `modules/commercial_documents/v4_proposal_generator.py`, `modules/asset_generation/proposal_asset_alignment.py`

1. Leer `v4_proposal_generator.py` L642:
   ```python
   matrix_path = output_path / "v4_audit" / "proposal_asset_matrix.json"
   ```
2. `output_path` para v4complete es `output/v4_complete/` (flat), dando:
   `output/v4_complete/v4_audit/proposal_asset_matrix.json`
3. El packager `_collect_files()` opera sobre `source_dir = output/v4_complete/zione/`
4. **Fix**: Cambiar L642 para que la matrix se guarde en el subdirectorio del hotel:
   ```python
   # Construir ruta dentro del subdirectorio del hotel
   hotel_dir = output_path / hotel_id  # hotel_id = "zione" o el slug
   matrix_path = hotel_dir / "v4_audit" / "proposal_asset_matrix.json"
   ```
   O alternativamente, si `output_path` ya incluye el hotel_id:
   ```python
   matrix_path = output_path / "v4_audit" / "proposal_asset_matrix.json"
   ```
   y asegurar que `output_path` apunte a `output/v4_complete/zione/` (no al flat)

5. Verificar con `grep -n "output_path" v4_proposal_generator.py` cómo se construye
   `output_path` — si ya recibe el hotel subdir, el fix es solo asegurar consistencia

### Tarea D-2: Fix P-04 — Unificar modelo de cobertura con DeliveryContext

**Archivos**: `modules/asset_generation/proposal_asset_alignment.py`, `modules/delivery/delivery_context.py`

1. Leer `ProposalAssetMatrix` y `AlignmentReport` en `proposal_asset_alignment.py`
2. Actualmente la matrix compara contra la propuesta comercial usando
   `PainSolutionMapper.PAIN_SOLUTION_MAP`
3. El alignment gate compara contra el estado de assets usando
   `PROPOSAL_SERVICE_TO_ASSET`
4. **Fix mínimo**: Asegurar que la matrix se guarde en la ruta correcta (Tarea D-1)
   y documentar la divergencia semántica como deuda técnica
5. **Fix completo (si hay tiempo)**: Hacer que `ProposalAssetMatrix` consuma
   `DeliveryContext.assets` como fuente de verdad (ahora que existe el contrato
   canónico post-DT-1), unificando ambos sistemas

**Decisión del plan**: Priorizar P-06 (path fix) para que la matrix se empaquete.
Para P-04, documentar la divergencia semántica y unificar en un futuro v4.64.0
salvo que la unificación sea trivial (< 10 líneas de cambio).

### Tarea D-3: Verificar que los 28 tests existentes siguen pasando

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/delivery/test_delivery_contract.py -v
```

---

## Criterios de Completitud

- [ ] P-06: `proposal_asset_matrix.json` se guarda en ruta que `_collect_files()` recoge
- [ ] P-04: Divergencia semántica documentada (o unificada si fue trivial)
- [ ] 28 tests existentes pasan
- [ ] Commit con mensaje descriptivo

---

## Post-Ejecución

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-D-DT2 --desc "P-04_P-06_proposal_asset_matrix_path_fix_and_packaging"
```

---

## Próxima Sesión

```
Carga el plan DT-2 en /mnt/c/Users/Jhond/Github/iah-cli/.opencode/plans/DT-2-DELIVERY-CONTRACT-RESIDUAL-2026-07-24/
Ejecuta FASE-E: 06-prompt-fase-E.md (Tests nuevos P-01..P-07)
```
