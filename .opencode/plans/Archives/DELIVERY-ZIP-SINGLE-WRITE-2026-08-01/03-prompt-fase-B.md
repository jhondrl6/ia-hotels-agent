# FASE-B: Core Rewrite — Single-Write Architecture

**ID**: FASE-B-CORE-REWRITE
**Objetivo**: Reescribir `DeliveryPackager.package()` con arquitectura single-write: calcular todo en memoria, escribir UNA sola vez, eliminar el defecto de ordering "measure-then-mutate-then-validate".
**Dependencias**: FASE-A ✅ (tests como red de seguridad)
**Duracion estimada**: 2.5-3 horas
**Skill**: `phased_project_executor.md`
**Modo de ejecucion**: **Agente principal DIRECTO** (decision arquitectonica cross-module, NO delegable)

> [!CAUTION]
> **FASE DE MAYOR COMPLEJIDAD TECNICA DEL PLAN**
> Esta fase reescribe la logica central de un archivo de 833 lineas con un nuevo paradigma.
> Requiere entender el contexto completo de: `_create_zip()`, `_validate_zip()`, `create_manifest()`, `create_readme()`, P-01, y la self-reference del MANIFEST.
> Un subagente carece del contexto para tomar las decisiones de diseno correctas.

---

## Contexto

### Causa Raiz a Eliminar

```
Pass 2 mide README (S1=5795) → P-01 muta README (S2=5777) → ZIP incluye S2 → Validacion compara S2 vs S1 → MISMATCH
```

El diseno actual viola el **principio de inmutabilidad entre medicion y empaquetado**.

### Solucion: Opcion C (Single-Write con Fixed-Point Iteration)

Nuevo flujo:
1. Collect files → calcular tamanos en memoria
2. Calcular totals preliminares (sin README ni MANIFEST)
3. Generar README FINAL en memoria (con totals calculados, SIN placeholders)
4. Medir README final (bytes exactos en memoria)
5. Recalcular totals incluyendo README
6. Construir MANIFEST completo en memoria (self-reference por iteracion fija)
7. Escribir MANIFEST una sola vez a disco
8. Assert: MANIFEST en disco == MANIFEST en memoria
9. Crear ZIP desde archivos en disco (todos ya finales)
10. Validar ZIP ↔ MANIFEST (exact match, 0 tolerancia)

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada (tests infrastructure lista) |
| FASE-B | ⏳ En progreso (esta fase) |

### Base Tecnica Disponible
- Tests de delivery actualizados (FASE-A): sin tolerancia, con fixture FASE-C
- Tests `xfail` que se convertiran en `pass` tras esta fase
- `delivery_packager.py` (833L), `delivery_context.py` (535L)

---

## Tareas

### T1: Investigar estructura actual de package() (5-10 iteraciones)

**Objetivo**: Mapear exactamente el flujo actual antes de reescribir.

**Acciones**:
1. Leer `delivery_packager.py` completo (833 lineas)
2. Identificar todos los metodos auxiliares: `_collect_files()`, `_create_zip()`, `_validate_zip()`, `_format_bytes()`, `_make_zip_filename()`
3. Mapear que datos fluyen entre metodos
4. Verificar consumers downstream: `hook_pdf_generator.py`, `delivery_quality_report.py`
5. Documentar que NO debe cambiar (API publica: `package()` retorna `zip_path`)

**Output**: Notas internas de mapeo (no archivo separado, usar contexto de sesion)

### T2: Implementar single-write en package() (15-20 iteraciones)

**Objetivo**: Reescribir el flujo interno de `package()` manteniendo la API publica.

**Archivos afectados**:
- `modules/delivery/delivery_packager.py` (L58-251: metodo `package()` y auxiliares)

**Diseno del nuevo flujo**:

```python
def package(self, source_dir, hotel_id, delivery_context=None, quality_metadata=None, ...):
    # 1. Collect files (sin cambios)
    files = self._collect_files(source_dir)

    # 2. Calcular totals preliminares (sin README ni MANIFEST)
    preliminary_total = sum(f["size_bytes"] for f in files)
    preliminary_count = len(files)

    # 3. Generar README FINAL en memoria (SIN placeholders)
    readme_content = self._render_readme_final(
        hotel_id=hotel_id,
        total_files=preliminary_count + 2,  # +README +MANIFEST
        total_size=preliminary_total,        # se ajustara despues
        delivery_context=delivery_context,
        quality_metadata=quality_metadata
    )
    readme_bytes = readme_content.encode('utf-8')
    readme_size = len(readme_bytes)

    # 4. Recalcular totals incluyendo README
    final_total = preliminary_total + readme_size
    final_count = preliminary_count + 1  # +README (MANIFEST se agrega en paso 5)

    # 5. Construir MANIFEST en memoria con self-reference por fixed-point
    manifest = self._build_manifest_fixed_point(
        files=files,
        readme_size=readme_size,
        total_size=final_total,
        quality_metadata=quality_metadata
    )

    # 6. Escribir README a disco (contenido final, inmutable desde aqui)
    readme_path.write_text(readme_content, encoding='utf-8')

    # 7. Escribir MANIFEST a disco (UNA sola vez)
    manifest_json = json.dumps(manifest, indent=2, ensure_ascii=False)
    manifest_path.write_text(manifest_json, encoding='utf-8')

    # 8. Assert: disco == memoria
    assert manifest_path.stat().st_size == len(manifest_json.encode('utf-8'))

    # 9. Crear ZIP (todos los archivos son finales)
    zip_path = self._create_zip(files, readme_path, manifest_path)

    # 10. Validar ZIP ↔ MANIFEST (exact, 0 tolerancia)
    errors = self._validate_zip(zip_path, manifest)
    if errors:
        self._cleanup_on_error(zip_path, manifest_path, readme_path)
        raise DeliveryValidationError(errors)

    # 11. Cleanup MANIFEST externo (ya esta dentro del ZIP)
    manifest_path.unlink(missing_ok=True)
    return zip_path
```

**Fixed-point iteration para self-reference**:
```python
def _build_manifest_fixed_point(self, files, readme_size, total_size, quality_metadata):
    """Construye MANIFEST con self-reference estable por iteracion fija."""
    # Estimacion inicial: N entradas * ~85 bytes + overhead JSON
    estimated_manifest_size = len(files) * 85 + 500

    for iteration in range(3):  # Maximo 3 iteraciones (convergencia garantizada)
        manifest = {
            "files": [...],  # todas las entradas + MANIFEST con estimated_size
            "total_files": len(files) + 2,  # +README +MANIFEST
            "total_size_bytes": total_size + estimated_manifest_size,
            "quality_metadata": quality_metadata
        }
        actual_json = json.dumps(manifest, indent=2, ensure_ascii=False)
        actual_size = len(actual_json.encode('utf-8'))

        if actual_size == estimated_manifest_size:
            break  # Convergencia alcanzada
        estimated_manifest_size = actual_size

    return manifest
```

**Criterios de aceptacion**:
- [ ] `package()` mantiene API publica (retorna `zip_path`)
- [ ] README se genera SIN placeholders `{{TOTAL_FILES}}`/`{{TOTAL_SIZE}}`
- [ ] MANIFEST se escribe UNA sola vez a disco
- [ ] Fixed-point converge en <=3 iteraciones
- [ ] Assert de integridad disco==memoria presente

### T3: Eliminar P-01 y el 3-pass (5 iteraciones)

**Objetivo**: Remover el codigo obsoleto que causaba el bug.

**Eliminar**:
- L221-227: P-01 README placeholder fixup (ya no existe placeholder)
- L190-214: Self-reference correction multi-pass (reemplazado por fixed-point)
- L177-181: Pass 1/Pass 2 como pasos separados (unificados en single-write)

**Verificar**:
- [ ] Sin referencias a `{{TOTAL_FILES}}` o `{{TOTAL_SIZE}}` en `delivery_packager.py`
- [ ] `templates/delivery_readme_template.md` puede conservar placeholders (otros consumers) pero `delivery_packager.py` ya no los usa

### T4: Verificar no-regresion + activar xfail tests (5-10 iteraciones)

**Objetivo**: Confirmar que el fix funciona y que los tests FASE-C ahora pasan.

**Acciones**:
1. Ejecutar `pytest tests/delivery/ -v` → todos pasan (incluyendo los antes `xfail`)
2. Remover decoradores `@pytest.mark.xfail` de los tests FASE-C
3. Ejecutar suite completa: `pytest tests/ -x -q` → 0 fallos
4. Verificar consumers: `hook_pdf_generator.py` no afectado

**Criterios de aceptacion**:
- [ ] Tests FASE-C pasan sin `xfail`
- [ ] Suite completa sin regresion
- [ ] `_validate_zip()` retorna `[]` en modo FASE-C

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| Delivery suite completa | `tests/delivery/` | 60+/60+ pasan |
| FASE-C mode (antes xfail) | `tests/delivery/test_delivery_packager.py` | PASA (sin xfail) |
| Legacy mode | `tests/delivery/test_delivery_packager.py` | PASA (no regresion) |
| Per-file size accuracy | `tests/delivery/test_delivery_contract.py` | PASA |
| Suite global | `tests/` | 3,158+ pasan |

**Comando de validacion**:
```bash
./venv/Scripts/python.exe -m pytest tests/delivery/ -v
./venv/Scripts/python.exe -m pytest tests/ -x -q --tb=short
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecucion (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar FASE-B como ✅ Completada
2. **`09-documentacion-post-proyecto.md`**: Seccion A (modulo modificado), B (funcionalidad), D (metricas)
3. **Ejecutar**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-B --desc "Core Rewrite: single-write architecture con fixed-point iteration. Elimina Bug 1 (README post-medicion) y Bug 2 (self-reference inestable)" \
    --archivos-mod "modules/delivery/delivery_packager.py,tests/delivery/test_delivery_packager.py,tests/delivery/test_delivery_contract.py" \
    --tests "60" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] `package()` reescrito con flujo single-write (10 pasos)
- [ ] Fixed-point iteration implementado y convergiendo en <=3 ciclos
- [ ] P-01 eliminado (sin placeholders en packager)
- [ ] 3-pass eliminado (sin measure-then-mutate)
- [ ] Assert disco==memoria presente
- [ ] Tests FASE-C pasan sin xfail
- [ ] Tests legacy pasan (no regresion)
- [ ] Suite completa: 0 fallos
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] `log_phase_completion.py` ejecutado

---

## Restricciones

- Maximo 60 iteraciones del agente
- NO modificar `main.py` (NF-3/NF-6 son FASE-C)
- NO modificar `delivery_context.py` (consumer, no cambia)
- La API publica de `package()` NO debe cambiar (mismos parametros, mismo return)
- NO ejecutar v4complete (eso es FASE-D)
- NO agregar tolerancia a `_validate_zip()` (exactitud es el objetivo)
