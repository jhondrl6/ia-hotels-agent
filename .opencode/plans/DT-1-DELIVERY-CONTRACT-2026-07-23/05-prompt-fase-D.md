# 05-prompt-fase-D — Tests de contrato y gate de no-regresión

**Fase**: FASE-D — Tests cross-artifact + gate obligatorio post-zip
**Plan**: DT-1-DELIVERY-CONTRACT-2026-07-23
**Sesión**: Nueva (fresh)
**Iteraciones máx**: 60
**Depende de**: FASE-A ✅, FASE-B ✅, FASE-C ✅
**Bloquea a**: FASE-E
**Tipo**: DIRECTA (TDD: escribir tests, verificar que pasan)

---

## Objetivo

Crear tests de integración que validen el contrato de entrega completo (README ↔ manifest ↔ ZIP) y añadir un gate de no-regresión post-zip obligatorio. Los 10 tests existentes del packager deben seguir pasando.

## Contexto de fases anteriores

- FASE-A: `DeliveryAssetState`, `DeliveryAssetEntry`, `DeliveryContext` definidos.
- FASE-B: Rutas POSIX, tamaños reales, filename único, `_validate_zip()`.
- FASE-C: README dinámico con secciones por estado y Package Structure real.
- El packager ahora puede recibir un `DeliveryContext` y generar un README preciso.

## Tareas

### T1: Tests de estados canónicos y presencia

**Archivo**: `tests/delivery/test_delivery_contract.py` (CREAR)

Crear tests para `DeliveryAssetEntry.from_skipped_asset()` y `from_generated_asset()`:

```python
import pytest
from modules.delivery.delivery_context import (
    DeliveryAssetState,
    DeliveryAssetEntry,
    DeliveryContext
)

class TestDeliveryAssetEntry:
    """Tests para construcción de entradas canónicas de assets."""

    def test_from_skipped_exists(self):
        """Asset skipped por presencia verificada → PRESENT_IN_PRODUCTION."""
        skipped = {
            "asset_type": "whatsapp_button",
            "presence_status": "exists",
            "site_verified": True,
            "reason": "Asset ya implementado en sitio de producción",
            "pain_ids_affected": ["no_whatsapp_visible"]
        }
        entry = DeliveryAssetEntry.from_skipped_asset(skipped, "Botón de WhatsApp")
        assert entry.state == DeliveryAssetState.PRESENT_IN_PRODUCTION
        assert entry.covered is True
        assert entry.requires_action is False
        assert entry.site_verified is True

    def test_from_skipped_with_conflict(self):
        """Asset skipped por presencia pero con conflicto → PRESENT_WITH_ISSUES."""
        skipped = {
            "asset_type": "whatsapp_button",
            "presence_status": "exists",
            "site_verified": True,
            "reason": "Asset ya implementado",
            "pain_ids_affected": ["no_whatsapp_visible", "whatsapp_conflict"]
        }
        entry = DeliveryAssetEntry.from_skipped_asset(skipped, "Botón de WhatsApp")
        assert entry.state == DeliveryAssetState.PRESENT_WITH_ISSUES
        assert entry.covered is False  # No cubierto porque requiere revisión
        assert entry.requires_action is True
        assert entry.requires_review is True

    def test_from_skipped_exists_with_issues(self):
        """presence_status=exists_with_issues → PRESENT_WITH_ISSUES."""
        skipped = {
            "asset_type": "org_schema",
            "presence_status": "exists_with_issues",
            "site_verified": True,
            "reason": "Schema detected but may be incorrect type",
            "pain_ids_affected": []
        }
        entry = DeliveryAssetEntry.from_skipped_asset(skipped, "Schema Organization")
        assert entry.state == DeliveryAssetState.PRESENT_WITH_ISSUES

    def test_from_skipped_unknown(self):
        """presence_status desconocido → INDETERMINATE."""
        skipped = {
            "asset_type": "unknown_asset",
            "presence_status": "unknown",
            "site_verified": False,
            "reason": "",
            "pain_ids_affected": []
        }
        entry = DeliveryAssetEntry.from_skipped_asset(skipped, "Unknown")
        assert entry.state == DeliveryAssetState.INDETERMINATE
        assert entry.requires_review is True

    def test_from_generated_delivered(self):
        """Asset generado con PASSED → DELIVERED."""
        asset = {
            "asset_type": "hotel_schema",
            "confidence_score": 1.0,
            "can_use": True,
            "preflight_status": "PASSED",
            "filename": "hotel_schema_20260723_201326.json"
        }
        entry = DeliveryAssetEntry.from_generated_asset(
            asset, "Schema Hotel", "ASSETS/hotel_schema/hotel_schema_20260723_201326.json"
        )
        assert entry.state == DeliveryAssetState.DELIVERED
        assert entry.covered is True
        assert entry.requires_action is True

    def test_from_generated_estimated(self):
        """Asset generado con ESTIMATED → ESTIMATED."""
        asset = {
            "asset_type": "optimization_guide",
            "confidence_score": 0.8,
            "can_use": True,
            "preflight_status": "WARNING",
            "filename": "ESTIMATED_guia_optimizacion_20260723_201326.md"
        }
        entry = DeliveryAssetEntry.from_generated_asset(
            asset, "SEO Local", "ASSETS/optimization_guide/ESTIMATED_guia_optimizacion.md"
        )
        assert entry.state == DeliveryAssetState.ESTIMATED
        assert entry.requires_review is True

    def test_from_generated_blocked(self):
        """Asset con preflight BLOCKED → FAILED."""
        asset = {
            "asset_type": "failed_asset",
            "confidence_score": 0.0,
            "can_use": False,
            "preflight_status": "BLOCKED",
            "filename": "failed_asset.html"
        }
        entry = DeliveryAssetEntry.from_generated_asset(asset, "Failed", "")
        assert entry.state == DeliveryAssetState.FAILED
        assert entry.covered is False

    def test_delivery_context_properties(self):
        """DeliveryContext agrupa correctamente por estado."""
        ctx = DeliveryContext(
            hotel_id="test_hotel",
            zip_filename="test_20260723.zip",
            assets=[
                DeliveryAssetEntry(
                    "a1", "S1", DeliveryAssetState.DELIVERED,
                    delivery_path="ASSETS/a1.md", covered=True, requires_action=True
                ),
                DeliveryAssetEntry(
                    "a2", "S2", DeliveryAssetState.PRESENT_IN_PRODUCTION,
                    site_verified=True, covered=True
                ),
                DeliveryAssetEntry(
                    "a3", "S3", DeliveryAssetState.PRESENT_WITH_ISSUES,
                    site_verified=True, covered=False, requires_action=True, requires_review=True
                ),
                DeliveryAssetEntry(
                    "a4", "S4", DeliveryAssetState.ESTIMATED,
                    covered=False, requires_review=True
                ),
            ]
        )
        assert len(ctx.delivered_assets) == 1
        assert len(ctx.present_assets) == 1
        assert len(ctx.present_with_issues_assets) == 1
        assert len(ctx.estimated_assets) == 1
        assert ctx.covered_count == 2  # DELIVERED + PRESENT_IN_PRODUCTION
        assert ctx.total_services == 4

    def test_from_skipped_verification_failed(self):
        """presence_status=verification_failed → INDETERMINATE con requires_review."""
        skipped = {
            "asset_type": "org_schema",
            "presence_status": "verification_failed",
            "site_verified": False,
            "reason": "Could not verify schema on live site",
            "pain_ids_affected": []
        }
        entry = DeliveryAssetEntry.from_skipped_asset(skipped, "Schema Organization")
        assert entry.state == DeliveryAssetState.INDETERMINATE
        assert entry.requires_review is True
        assert entry.site_verified is False

    def test_delivery_context_from_missing_report(self):
        """from_asset_generation_report() con reporte inexistente → contexto vacío."""
        ctx = DeliveryContext.from_asset_generation_report(
            report_path=Path("/nonexistent/asset_generation_report.json"),
            hotel_id="test_hotel",
            zip_filename="test_20260723.zip",
            files=[]
        )
        assert ctx.assets == []
        assert ctx.hotel_id == "test_hotel"
        assert ctx.zip_filename == "test_20260723.zip"

    def test_delivery_context_from_invalid_report(self, tmp_path):
        """from_asset_generation_report() con reporte JSON inválido → contexto vacío (graceful)."""
        import json
        bad_report = tmp_path / "bad_report.json"
        bad_report.write_text("{ invalid json content", encoding="utf-8")
        ctx = DeliveryContext.from_asset_generation_report(
            report_path=bad_report,
            hotel_id="test_hotel",
            zip_filename="test_20260723.zip",
            files=[]
        )
        # Debe manejar el error gracefulmente: assets vacío, no crash
        assert ctx.assets == []

    def test_from_generated_advisory_guide(self):
        """Asset con asset_type terminado en 'guide' → is_advisory=True."""
        asset = {
            "asset_type": "whatsapp_conflict_guide",
            "confidence_score": 0.8,
            "can_use": True,
            "preflight_status": "WARNING",
            "filename": "guia_conflicto_whatsapp_20260723.md"
        }
        entry = DeliveryAssetEntry.from_generated_asset(
            asset, "Guía de Conflicto WhatsApp", "ASSETS/whatsapp_conflict_guide/guia_conflicto_whatsapp.md"
        )
        assert entry.is_advisory is True
        assert entry.requires_action is False  # Las guías no requieren instalación
        assert entry.requires_review is True   # Pero sí revisión
```

### T2: Tests de manifest ZIP

**Archivo**: `tests/delivery/test_delivery_contract.py` (modificar)

Agregar tests que validen el manifest contra el ZIP real:

```python
class TestManifestZipConsistency:
    """Tests de consistencia manifest ↔ ZIP."""

    def test_manifest_paths_posix(self, sample_hotel_output):
        """Todas las rutas del manifest usan /, no \\."""
        packager = DeliveryPackager(...)
        zip_path = packager.package(...)
        
        with zipfile.ZipFile(zip_path, 'r') as z:
            manifest = json.loads(z.read("MANIFEST.json"))
        
        for f in manifest["files"]:
            assert "\\" not in f["name"], f"Non-POSIX path: {f['name']}"

    def test_zip_paths_posix(self, sample_hotel_output):
        """Todas las rutas del ZIP usan /."""
        packager = DeliveryPackager(...)
        zip_path = packager.package(...)
        
        with zipfile.ZipFile(zip_path, 'r') as z:
            for name in z.namelist():
                assert "\\" not in name, f"Non-POSIX ZIP path: {name}"

    def test_manifest_total_files_matches_zip(self, sample_hotel_output):
        """total_files == len(zip.namelist())."""
        packager = DeliveryPackager(...)
        zip_path = packager.package(...)
        
        with zipfile.ZipFile(zip_path, 'r') as z:
            manifest = json.loads(z.read("MANIFEST.json"))
            assert manifest["total_files"] == len(z.namelist())

    def test_manifest_total_size_matches_zip(self, sample_hotel_output):
        """total_size_bytes ≈ sum(tamaños reales)."""
        packager = DeliveryPackager(...)
        zip_path = packager.package(...)
        
        with zipfile.ZipFile(zip_path, 'r') as z:
            manifest = json.loads(z.read("MANIFEST.json"))
            actual_total = sum(len(z.read(n)) for n in z.namelist())
            # Margen de 5% para diferencias de compresión/metadata
            assert abs(manifest["total_size_bytes"] - actual_total) <= actual_total * 0.05

    def test_readme_size_not_zero(self, sample_hotel_output):
        """README_DELIVERY.md tiene size_bytes > 0 en manifest."""
        packager = DeliveryPackager(...)
        zip_path = packager.package(...)
        
        with zipfile.ZipFile(zip_path, 'r') as z:
            manifest = json.loads(z.read("MANIFEST.json"))
            readme_entry = next(
                (f for f in manifest["files"] if f["name"] == "README_DELIVERY.md"), None
            )
            assert readme_entry is not None, "README_DELIVERY.md not in manifest"
            assert readme_entry["size_bytes"] > 0, f"README size is {readme_entry['size_bytes']}"

    def test_manifest_entry_set_equals_zip_entry_set(self, sample_hotel_output):
        """Cada entrada del manifest existe en ZIP y viceversa."""
        packager = DeliveryPackager(...)
        zip_path = packager.package(...)
        
        with zipfile.ZipFile(zip_path, 'r') as z:
            manifest = json.loads(z.read("MANIFEST.json"))
            zip_names = set(z.namelist())
            manifest_names = {f["name"] for f in manifest["files"]}
            assert zip_names == manifest_names, \
                f"ZIP-only: {zip_names - manifest_names}, Manifest-only: {manifest_names - zip_names}"
```

### T3: Tests de README ↔ ZIP

**Archivo**: `tests/delivery/test_delivery_contract.py` (modificar)

```python
class TestReadmeZipConsistency:
    """Tests de consistencia README ↔ ZIP."""

    def test_readme_does_not_reference_missing_files(self, sample_hotel_output):
        """README no referencia archivos que no están en el ZIP."""
        packager = DeliveryPackager(...)
        zip_path = packager.package(...)
        
        with zipfile.ZipFile(zip_path, 'r') as z:
            zip_names = set(z.namelist())
            readme = z.read("README_DELIVERY.md").decode("utf-8")
        
        # Extraer referencias a archivos del README
        import re
        # Buscar patrones como `filename.ext` en contexto de instrucciones
        refs = set(re.findall(r'`([\w./-]+\.[\w]+)`', readme))
        # También buscar paths ASSETS/ mencionados
        asset_paths = set(re.findall(r'ASSETS/[\w./-]+', readme))
        refs.update(asset_paths)
        
        for ref in refs:
            # Normalizar: quitar backticks, verificar existencia
            clean_ref = ref.strip('`')
            if '.' in clean_ref and '/' in clean_ref:
                # Es un path → debe estar en el ZIP
                assert any(clean_ref in zn for zn in zip_names), \
                    f"README references '{clean_ref}' but not found in ZIP"

    def test_readme_package_structure_from_real_files(self, sample_hotel_output):
        """Package Structure refleja archivos reales del ZIP."""
        packager = DeliveryPackager(...)
        zip_path = packager.package(...)
        
        with zipfile.ZipFile(zip_path, 'r') as z:
            readme = z.read("README_DELIVERY.md").decode("utf-8")
        
        # La estructura debe mencionar ASSETS/ si hay assets
        if any(n.startswith("ASSETS/") for n in z.namelist()):
            assert "ASSETS/" in readme, "Package Structure missing ASSETS/"

    def test_readme_zip_filename_matches_actual(self, sample_hotel_output):
        """El filename en README coincide con el nombre real del ZIP."""
        packager = DeliveryPackager(...)
        zip_path = packager.package(...)
        zip_filename = Path(zip_path).name
        
        with zipfile.ZipFile(zip_path, 'r') as z:
            readme = z.read("README_DELIVERY.md").decode("utf-8")
        
        assert zip_filename in readme, \
            f"README does not contain actual ZIP filename '{zip_filename}'"

    def test_readme_no_hardcoded_whatsapp_button(self, sample_hotel_output):
        """README no contiene 'boton_whatsapp.html' hardcodeado."""
        packager = DeliveryPackager(...)
        zip_path = packager.package(...)
        
        with zipfile.ZipFile(zip_path, 'r') as z:
            readme = z.read("README_DELIVERY.md").decode("utf-8")
        
        # Si boton_whatsapp.html NO está en el ZIP, no debe estar en el README
        zip_names = z.namelist()
        if not any("boton_whatsapp.html" in n for n in zip_names):
            assert "boton_whatsapp.html" not in readme, \
                "README references boton_whatsapp.html but file is not in ZIP"
```

### T4: Gate de no-regresión obligatorio

**Archivo**: `modules/delivery/delivery_packager.py` (modificar)

Integrar `_validate_zip()` (creado en FASE-B) como gate obligatorio en `package()`. Si la validación falla, el ZIP NO debe generarse (o debe marcarse como inválido):

```python
# En package(), después de _create_zip():
validation_errors = self._validate_zip(zip_path, manifest)
if validation_errors:
    error_msg = "ZIP validation failed:\n" + "\n".join(f"  - {e}" for e in validation_errors)
    logger.error(f"[DeliveryPackager] {error_msg}")
    # Eliminar ZIP inválido
    if zip_path.exists():
        zip_path.unlink()
    raise DeliveryValidationError(error_msg)
```

Crear excepción personalizada:

```python
class DeliveryValidationError(Exception):
    """Error de validación del delivery package."""
    pass
```

Los tests deben verificar que un ZIP con errores de validación no se entrega:

```python
def test_validation_blocks_invalid_zip(self, sample_hotel_output):
    """Un ZIP que no pasa validación lanza DeliveryValidationError."""
    # ... setup que produzca un error de validación ...
    with pytest.raises(DeliveryValidationError):
        packager.package(...)
```

## Criterios de Completitud

- [ ] `test_delivery_contract.py` existe con ≥ 19 tests
- [ ] 10 tests existentes en `test_delivery_packager.py` siguen pasando
- [ ] Tests de estados canónicos cubren: PRESENT_IN_PRODUCTION, PRESENT_WITH_ISSUES, DELIVERED, ESTIMATED, FAILED, INDETERMINATE, verification_failed
- [ ] Tests de DeliveryContext.from_asset_generation_report: reporte ausente, reporte inválido
- [ ] Tests de is_advisory: guía detectada correctamente, requires_action=False, requires_review=True
- [ ] Tests de manifest ZIP: rutas POSIX, total_files, total_size, tamaños > 0 para metaarchivos, entradas idénticas
- [ ] Tests de README: no referencia archivos ausentes, filename correcto, Package Structure real, sin hardcodeos
- [ ] Gate de no-regresión: `DeliveryValidationError` se lanza si manifest ↔ ZIP inconsistente
- [ ] Suite completa: `pytest tests/delivery/ -v` pasa sin errores

## Restricciones

- NO modificar `delivery_context.py` (FASE-A)
- NO modificar la template (FASE-C)
- NO modificar `create_readme()` o `create_manifest()` (salvo para integrar el gate de validación)
- Los tests existentes NO deben modificarse (solo agregar nuevos)

## Archivos involucrados

| Archivo | Tipo de cambio |
|---------|---------------|
| `tests/delivery/test_delivery_contract.py` | CREAR (nuevo archivo de tests) |
| `modules/delivery/delivery_packager.py` | MODIFICAR: integrar `_validate_zip()` como gate obligatorio + AGREGAR: `DeliveryValidationError` |

## Post-Ejecución (OBLIGATORIO)

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/delivery/ -v
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-D --desc "DT1_cross_artifact_tests_validation_gate"
```
