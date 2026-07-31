# 03-prompt-fase-B — Pipeline físico ZIP ↔ manifest

**Fase**: FASE-B — Rutas POSIX, tamaños reales, filename único, verificación post-zip, carga de DeliveryContext
**Plan**: DT-1-DELIVERY-CONTRACT-2026-07-23
**Sesión**: Nueva (fresh)
**Iteraciones máx**: 60
**Depende de**: FASE-A ✅
**Bloquea a**: FASE-C
**Tipo**: DIRECTA (modificaciones quirúrgicas en delivery_packager.py)

---

## Objetivo

Corregir el pipeline físico del empaquetado para que:
1. Todas las rutas internas del ZIP y MANIFEST usen separadores POSIX (`/`).
2. `MANIFEST.json` registre tamaños reales (> 0) para metaarchivos.
3. El filename del ZIP se calcule una sola vez y se comparta con el README.
4. Exista una validación post-zip que compare manifest vs ZIP real.

## Contexto de FASE-A

FASE-A definió `DeliveryAssetState`, `DeliveryAssetEntry` y `DeliveryContext` en `modules/delivery/delivery_context.py`. FASE-B usará `DeliveryContext` como parámetro opcional en `package()`. Los cambios en FASE-B son incrementales: no requieren que `DeliveryContext` esté completamente poblado; el comportamiento legacy (sin `DeliveryContext`) debe preservarse.

## Tareas

### T1: Normalizar rutas internas a POSIX

**Archivo**: `modules/delivery/delivery_packager.py` (modificar)

El bug está en `_collect_files()` (líneas ~158-205). La línea problemática es:

```python
dest = f"ASSETS/{rel_path}"
```

Cuando `rel_path` es un `Path` de Windows, `str(rel_path)` produce backslashes.

**Fix**: Usar `as_posix()` en todas las rutas de destino:

```python
# En _collect_files(), reemplazar TODAS las construcciones de dest:
# Antes:
dest = f"ASSETS/{rel_path}"
# Después:
dest = f"ASSETS/{rel_path.as_posix()}"
```

También en `package()` (líneas ~128-136), los `meta_entries` usan strings directos. Verificar que todos usen `/`:

```python
meta_entries = [
    {"source": str(manifest_path), "dest": "MANIFEST.json"},
]
readme_path = self.deliveries_dir / "README_DELIVERY.md"
meta_entries.append({"source": str(readme_path), "dest": "README_DELIVERY.md"})
```

Estos ya usan strings planos, que son correctos. Pero por consistencia, asegurar que ningún `dest` contenga `\\`.

**Verificación**: Después del fix, inspeccionar el ZIP generado: `python3 -c "import zipfile; z=zipfile.ZipFile('test.zip'); print([n for n in z.namelist() if '\\\\' in n])"` debe devolver lista vacía.

### T2: Corregir cálculo de tamaños en create_manifest

**Archivo**: `modules/delivery/delivery_packager.py` (modificar)

El bug está en `create_manifest()` (líneas ~216-248). El manifest se genera antes de que `README_DELIVERY.md` y `MANIFEST.json` existan en disco, por lo que `stat()` devuelve tamaño 0 o falla.

**Fix — estrategia de dos pasadas**:

```python
def create_manifest(self, hotel_id: str, files: List[Dict[str, Any]], 
                    extra_files: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Genera manifest con tamaños reales de todos los archivos.
    
    Args:
        hotel_id: Hotel identifier
        files: Lista de archivos YA escritos (assets + documentos)
        extra_files: Metaarchivos que se escribirán después (MANIFEST, README).
                     Si se pasan, sus tamaños se calculan desde el contenido final.
    """
    manifest = {
        "version": "1.0.0",
        "hotel_id": hotel_id,
        "generated_at": datetime.now().isoformat(),
        "package_type": "automated_delivery",
        "files": []
    }
    
    all_files = list(files)
    if extra_files:
        all_files.extend(extra_files)
    
    for f in all_files:
        file_path = Path(f["source"])
        stat = file_path.stat() if file_path.exists() else None
        size = stat.st_size if stat else f.get("_size_bytes", 0)
        
        manifest["files"].append({
            "name": f["dest"],
            "size_bytes": size,
            "type": self._classify_file(f["dest"])
        })
    
    manifest["total_files"] = len(manifest["files"])
    manifest["total_size_bytes"] = sum(f["size_bytes"] for f in manifest["files"])
    
    return manifest
```

Y en `package()`, cambiar el orden para que el manifest se genere DESPUÉS de escribir los metaarchivos, o pasar tamaños calculados previamente a `extra_files`.

**Alternativa más simple** (recomendada para minimizar cambios):

En `package()`, después de escribir el README, recalcular el manifest con tamaños reales:

```python
# Después de create_readme() y ANTES de _create_zip():
# Reconstruir manifest con tamaños reales (README y MANIFEST ya existen)
manifest = self.create_manifest(hotel_id, all_files)  # all_files incluye meta_entries
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
```

El MANIFEST.json temporal se reescribe con tamaños reales (incluyendo el tamaño del README ya generado). El tamaño del propio MANIFEST.json seguirá siendo 0 porque no puede leerse a sí mismo antes de escribirse, pero el README sí tendrá tamaño real.

Para el MANIFEST.json: después de escribirlo, hacer `manifest_path.stat().st_size` y actualizar el JSON. Esto requiere una tercera pasada mínima.

**Implementación final recomendada (tres pasos)**:

> **Contrato B→C**: FASE-B escribe un README provisional (legacy, sin `DeliveryContext`) para poder medir su tamaño en el manifest. FASE-C reemplazará `create_readme()` para que acepte un `DeliveryContext` opcional. Cuando FASE-C se implemente, la llamada `create_readme()` en `package()` recibirá el `delivery_context` construido por T5 (ver abajo), produciendo el README dinámico. FASE-B NO debe modificar el contenido de `create_readme()`, solo garantizar que el README se escribe antes de medirlo. FASE-C modificará la llamada (pasar `delivery_context`) pero no el orden de escritura.

```python
# Paso 1: Escribir README (provisional — FASE-C reemplazará con delivery_context)
# FASE-B: llamada legacy (sin delivery_context). FASE-C: misma llamada + delivery_context kwarg.
self.create_readme(self.deliveries_dir, hotel_id, manifest=None)

# Paso 2: Construir manifest con tamaños de contenido + README (ya existe)
manifest = self.create_manifest(hotel_id, all_files)  # README ya tiene tamaño real
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

# Paso 3: Releer manifest para obtener su tamaño real, reescribir
manifest_size = manifest_path.stat().st_size
manifest["total_size_bytes"] += manifest_size
manifest["files"].append({
    "name": "MANIFEST.json",
    "size_bytes": manifest_size,
    "type": "other"
})
manifest["total_files"] = len(manifest["files"])
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
```

**Verificación**: Ejecutar `test_package_creates_zip` y verificar que `MANIFEST.json` dentro del ZIP tiene `size_bytes > 0` para README y MANIFEST.

### T3: Calcular filename del ZIP una sola vez

**Archivo**: `modules/delivery/delivery_packager.py` (modificar)

Actualmente el filename se calcula en `package()`:

```python
zip_filename = f"{hotel_id}_{date_str}.zip"
```

Y el README usa `{{HOTEL_ID}}_{{DATE}}.zip` que produce un formato distinto (`-` vs sin `-`).

**Fix**: Calcular una sola vez y exponerlo:

```python
# En __init__() o como propiedad:
def _make_zip_filename(self, hotel_id: str) -> str:
    date_str = datetime.now().strftime("%Y%m%d")
    return f"{hotel_id}_{date_str}.zip"

# En package():
zip_filename = self._make_zip_filename(hotel_id)
zip_path = self.deliveries_dir / zip_filename
```

Y en `create_readme()`, aceptar el filename como parámetro o como placeholder `{{PACKAGE_FILENAME}}`.

**Para esta fase**: Solo implementar el método `_make_zip_filename()` y guardar el filename resultante. La integración con README se hará en FASE-C.

### T4: Agregar validador post-zip

**Archivo**: `modules/delivery/delivery_packager.py` (modificar)

Agregar un método `_validate_zip()` que se ejecute después de `_create_zip()`:

```python
def _validate_zip(self, zip_path: Path, manifest: Dict[str, Any]) -> List[str]:
    """Valida consistencia ZIP ↔ manifest. Retorna lista de errores (vacía = OK)."""
    errors = []
    
    try:
        import zipfile as zf
        with zf.ZipFile(zip_path, 'r') as z:
            zip_names = set(z.namelist())
            manifest_names = {f["name"] for f in manifest.get("files", [])}
            
            # 1. Mismas entradas
            only_zip = zip_names - manifest_names
            only_manifest = manifest_names - zip_names
            if only_zip:
                errors.append(f"Entries in ZIP but not in manifest: {only_zip}")
            if only_manifest:
                errors.append(f"Entries in manifest but not in ZIP: {only_manifest}")
            
            # 2. Rutas POSIX
            for name in zip_names:
                if "\\" in name:
                    errors.append(f"Non-POSIX path in ZIP: {name}")
            
            # 3. Tamaños
            manifest_sizes = {f["name"]: f.get("size_bytes", 0) for f in manifest.get("files", [])}
            for name in zip_names:
                actual_size = len(z.read(name))
                declared_size = manifest_sizes.get(name, 0)
                if actual_size != declared_size:
                    errors.append(
                        f"Size mismatch for '{name}': manifest={declared_size}, actual={actual_size}"
                    )
            
            # 4. Totales
            declared_total = manifest.get("total_files", 0)
            actual_total = len(zip_names)
            if declared_total != actual_total:
                errors.append(f"Total files mismatch: manifest={declared_total}, actual={actual_total}")
            
            declared_size_total = manifest.get("total_size_bytes", 0)
            actual_size_total = sum(len(z.read(n)) for n in zip_names)
            if declared_size_total != actual_size_total:
                errors.append(
                    f"Total size mismatch: manifest={declared_size_total}, actual={actual_size_total}"
                )
    
    except Exception as e:
        errors.append(f"ZIP validation failed: {e}")
    
    return errors
```

Llamar en `package()` después de `_create_zip()`:

```python
zip_path = self.deliveries_dir / zip_filename
self._create_zip(zip_path, all_files, source_dir)

# Validar
validation_errors = self._validate_zip(zip_path, manifest)
if validation_errors:
    for err in validation_errors:
        logger.error(f"[DeliveryPackager] {err}")
    # Opcional: bloquear si hay errores críticos
    # raise DeliveryValidationError(validation_errors)
```

**Verificación**: Ejecutar `test_package_creates_zip` y verificar que no hay errores de validación.

### T5: Cargar `asset_generation_report` y construir `DeliveryContext` en `package()`

**Archivo**: `modules/delivery/delivery_packager.py` (modificar)

FASE-A definió `DeliveryContext.from_asset_generation_report()`. FASE-B debe usarlo en `package()` para que el README dinámico (FASE-C) tenga datos disponibles.

**Implementación**: Agregar al principio de `package()`, después de calcular `zip_filename` y antes de escribir el README:

```python
def package(self, source_dir: Path, hotel_id: str, hotel_dir: Optional[Path] = None, 
             delivery_context: Optional[DeliveryContext] = None) -> Path:
    # ... código existente ...
    zip_filename = self._make_zip_filename(hotel_id)
    zip_path = self.deliveries_dir / zip_filename
    
    # Si no se pasó un DeliveryContext, intentar construirlo desde asset_generation_report
    if delivery_context is None and hotel_dir is not None:
        report_path = hotel_dir / "v4_audit" / "asset_generation_report.json"
        if report_path.exists():
            delivery_context = DeliveryContext.from_asset_generation_report(
                report_path=report_path,
                hotel_id=hotel_id,
                zip_filename=zip_filename,
                files=all_files,  # lista final de archivos a empaquetar
            )
    
    # El delivery_context se pasa a create_readme() en FASE-C.
    # En FASE-B, create_readme() aún no lo usa (legacy), pero queda disponible.
    self._delivery_context = delivery_context  # cache para FASE-C
```

**Regla de compatibilidad**: Si `hotel_dir` es None o el reporte no existe, `delivery_context` queda None. El packager funciona en modo legacy (README sin secciones dinámicas). Esto garantiza backward compatibility.

**Verificación**: Ejecutar `test_package_creates_zip` y verificar que `self._delivery_context` no es None cuando el reporte existe. Verificar también que el test funciona sin `hotel_dir` (modo legacy).

## Criterios de Completitud

- [ ] `zipfile.namelist()` no contiene ninguna entrada con `\\`
- [ ] `MANIFEST.json` dentro del ZIP tiene `size_bytes > 0` para `README_DELIVERY.md`
- [ ] `MANIFEST.json` dentro del ZIP tiene `size_bytes > 0` para `MANIFEST.json`
- [ ] `total_size_bytes` del manifest coincide con la suma real de tamaños del ZIP (margen ± 1%)
- [ ] `total_files` del manifest coincide con `len(zipfile.namelist())`
- [ ] `_make_zip_filename()` produce nombres consistentes con el ZIP real
- [ ] `_validate_zip()` retorna lista vacía para un ZIP bien construido
- [ ] T5: `package()` carga `asset_generation_report.json` y construye `DeliveryContext` cuando `hotel_dir` está disponible
- [ ] T5: Sin `hotel_dir` o sin reporte, `delivery_context` queda None (legacy)
- [ ] 10 tests existentes del packager siguen pasando
- [ ] ZIP de prueba manual no tiene errores de validación

## Restricciones

- NO modificar `delivery_context.py` (FASE-A)
- NO modificar la template (FASE-C)
- NO modificar el contenido de `create_readme()` (FASE-C) — solo garantizar que se llama antes de medir el manifest
- Mantener compatibilidad hacia atrás: el packager debe funcionar sin `DeliveryContext` y sin `hotel_dir`

## Archivos involucrados

| Archivo | Tipo de cambio |
|---------|---------------|
| `modules/delivery/delivery_packager.py` | MODIFICAR: `_collect_files()` (rutas POSIX), `create_manifest()` (tamaños), `package()` (orden + filename + validación + carga DeliveryContext), AGREGAR: `_make_zip_filename()`, `_validate_zip()`, integración `DeliveryContext.from_asset_generation_report()` |

## Post-Ejecución (OBLIGATORIO)

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-B --desc "DT1_POSIX_paths_real_sizes_zip_filename_validation"
```
