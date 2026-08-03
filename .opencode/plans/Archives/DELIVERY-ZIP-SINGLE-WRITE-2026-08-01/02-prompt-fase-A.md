# FASE-A: Test Infrastructure + Bug 3 Fix

**ID**: FASE-A-TEST-INFRA
**Objetivo**: Preparar la red de seguridad TDD: eliminar tolerancia 5% que enmascara bugs, crear fixture FASE-C (path de produccion), y agregar tests de tamano por archivo.
**Dependencias**: Ninguna (primera fase)
**Duracion estimada**: 1.5-2 horas
**Skill**: `phased_project_executor.md`
**Modo de ejecucion**: `delegate_task` viable (2 tracks paralelas de puro codigo/tests)

---

## Contexto

El pipeline de delivery tiene 3 bugs confirmados y 6 nuevos fallos. Los tests actuales NO pueden detectar el Bug 1 (README post-medicion) porque:
1. El fixture nunca crea `asset_generation_report.json` → modo legacy → P-01 es no-op
2. La tolerancia del 5% en `test_delivery_contract.py:428` enmascara cualquier mismatch
3. No hay comparacion de tamano POR ARCHIVO (solo total)

Esta fase crea la infraestructura de tests que FASE-B usara como red de seguridad para el rewrite.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A | ⏳ En progreso (esta fase) |

### Base Tecnica Disponible
- Tests existentes: 3,158 funciones, 253 archivos
- Tests de delivery: `tests/delivery/test_delivery_packager.py`, `tests/delivery/test_delivery_contract.py`
- Modulo objetivo: `modules/delivery/delivery_packager.py` (833 lineas)

---

## Tareas

### T1: Grep exhaustivo de consumers (PRE-REQUISITO)

**Objetivo**: Identificar TODOS los consumers de las funciones a modificar antes de tocar tests.

**Comando**:
```bash
grep -rn "_validate_zip\|create_readme\|create_manifest\|_create_zip\|DeliveryPackager" modules/ tests/ main.py --include="*.py"
```

**Output esperado**: Lista de archivos que consumen estas funciones. Documentar en evidencia.

### T2: Eliminar tolerancia 5% en test_delivery_contract.py (Bug 3)

**Objetivo**: Reemplazar la asercion con tolerancia por validacion exacta.

**Archivos afectados**:
- `tests/delivery/test_delivery_contract.py` (L413-429)

**Cambio**:
```python
# ANTES (L428):
assert abs(manifest["total_size_bytes"] - actual_total) <= actual_total * 0.05

# DESPUES:
assert manifest["total_size_bytes"] == actual_total, \
    f"Total size mismatch: manifest={manifest['total_size_bytes']}, actual={actual_total}"
```

**Adicional**: Agregar test de tamano POR ARCHIVO (no solo total):
```python
def test_manifest_per_file_size_accuracy(self, sample_hotel_output):
    """Bug 3: Production validates per-file exact match. Tests must too."""
    # ... packager.package() ...
    for entry in manifest["files"]:
        actual_path = deliveries_dir / entry["name"]
        assert actual_path.stat().st_size == entry["size_bytes"], \
            f"Per-file mismatch {entry['name']}: manifest={entry['size_bytes']}, actual={actual_path.stat().st_size}"
```

**Criterios de aceptacion**:
- [ ] Tolerancia 5% eliminada
- [ ] Test de tamano por archivo agregado
- [ ] Tests existentes siguen pasando (modo legacy no afecta)

### T3: Crear fixture FASE-C (NF-1)

**Objetivo**: Crear un fixture que ejercite el path de produccion real (modo DeliveryContext).

**Archivos afectados**:
- `tests/delivery/test_delivery_packager.py` (nuevo fixture)
- `tests/delivery/test_delivery_contract.py` (nuevo fixture)

**Implementacion**:
```python
@pytest.fixture
def sample_hotel_output_fase_c(tmp_path):
    """Fixture FASE-C: incluye asset_generation_report.json para activar DeliveryContext."""
    hotel_dir = tmp_path / "test_hotel"
    hotel_dir.mkdir()
    # Archivos base (igual que fixture existente)
    for i in range(5):
        (hotel_dir / f"asset_{i}.html").write_text(f"<html>content {i}</html>")
    # CRITICO: crear v4_audit/asset_generation_report.json
    audit_dir = hotel_dir / "v4_audit"
    audit_dir.mkdir()
    report = {
        "hotel_id": "test_hotel",
        "assets_generated": [...],
        "quality_metadata": {"evidence_tier": "B+", "coherence_score": 0.92}
    }
    (audit_dir / "asset_generation_report.json").write_text(json.dumps(report))
    return tmp_path
```

**Criterios de aceptacion**:
- [ ] Fixture crea `v4_audit/asset_generation_report.json`
- [ ] `DeliveryContext.from_asset_generation_report()` carga exitosamente con este fixture
- [ ] Test con fixture FASE-C ejercita modo produccion (P-01 activo)

### T4: Tests de control dual (legacy + FASE-C)

**Objetivo**: Garantizar cobertura de AMBOS paths (NP8: control de caso default).

**Tests nuevos**:
```python
class TestDualModeCoverage:
    """NF-1: Cobertura dual legacy + FASE-C."""

    def test_legacy_mode_produces_valid_zip(self, sample_hotel_output):
        """Sin asset_generation_report.json → modo legacy → ZIP valido."""

    def test_fase_c_mode_produces_valid_zip(self, sample_hotel_output_fase_c):
        """Con asset_generation_report.json → modo FASE-C → ZIP valido."""
        # NOTA: Este test FALLARA hasta que FASE-B implemente el fix.
        # Marcar con @pytest.mark.xfail(reason="Bug 1: README post-medicion")

    def test_fase_c_readme_has_real_totals(self, sample_hotel_output_fase_c):
        """README en modo FASE-C debe tener totales reales, no placeholders."""
```

**Criterios de aceptacion**:
- [ ] Test legacy pasa (no regresion)
- [ ] Test FASE-C marcado como `xfail` con razon clara (fallara hasta FASE-B)
- [ ] Ambos tests documentan el comportamiento esperado

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| Tests delivery existentes | `tests/delivery/` | 54/54 pasan (sin tolerancia 5%) |
| Nuevo: per-file size | `tests/delivery/test_delivery_contract.py` | Pasa en modo legacy |
| Nuevo: dual mode | `tests/delivery/test_delivery_packager.py` | Legacy pasa, FASE-C xfail |

**Comando de validacion**:
```bash
./venv/Scripts/python.exe -m pytest tests/delivery/ -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecucion (OBLIGATORIO)

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`**: Marcar FASE-A como ✅ Completada
2. **`09-documentacion-post-proyecto.md`**: Seccion D (metricas: tests nuevos)
3. **Ejecutar**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-A --desc "Test Infrastructure: eliminar tolerancia 5%, fixture FASE-C, dual mode coverage" \
    --archivos-mod "tests/delivery/test_delivery_contract.py,tests/delivery/test_delivery_packager.py" \
    --tests "6" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] Tolerancia 5% eliminada de `test_delivery_contract.py`
- [ ] Test de tamano por archivo agregado y pasando
- [ ] Fixture FASE-C creado con `asset_generation_report.json`
- [ ] Tests duales (legacy + FASE-C) implementados
- [ ] Test FASE-C marcado `xfail` (fallara hasta FASE-B)
- [ ] `pytest tests/delivery/ -v` pasa (xfail no cuenta como fallo)
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] `dependencias-fases.md` actualizado
- [ ] `log_phase_completion.py` ejecutado

---

## Restricciones

- Maximo 60 iteraciones del agente
- NO modificar `modules/delivery/delivery_packager.py` (eso es FASE-B)
- NO modificar `main.py`
- Los tests nuevos que ejerciten FASE-C DEBEN marcarse `xfail` (el bug aun existe)
- NO ejecutar v4complete
