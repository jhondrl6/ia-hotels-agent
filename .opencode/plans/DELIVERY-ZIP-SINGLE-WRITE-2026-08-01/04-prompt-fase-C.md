# FASE-C: Error Handling + Cleanup + NF-5/NF-6

**ID**: FASE-C-ERROR-HANDLING
**Objetivo**: Endurecer el manejo de errores del delivery pipeline: logging de fallback (NF-2), severidad en main.py (NF-3), cleanup en camino de error (NF-4), unificar datetime (NF-5), y conectar params FASE-5 (NF-6).
**Dependencias**: FASE-B ✅ (core rewrite completado)
**Duracion estimada**: 1.5-2 horas
**Skill**: `phased_project_executor.md`
**Modo de ejecucion**: `delegate_task` viable (fixes puntuales bien acotados, sin decisiones de diseno)

---

## Contexto

Tras el rewrite de FASE-B, el packaging funciona correctamente. Pero el pipeline aun tiene:
- Fallback silencioso que enmascara errores (NF-2)
- Fallo de entrega tratado como WARN en vez de ERROR (NF-3)
- Artefactos huerfanos acumulandose en `deliveries/` (NF-4)
- Doble `datetime.now()` con riesgo de divergencia (NF-5)
- Feature FASE-5 implementado pero nunca activado (NF-6)

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada |
| FASE-B | ✅ Completada |
| FASE-C | ⏳ En progreso (esta fase) |

### Base Tecnica Disponible
- `delivery_packager.py` reescrito con single-write (FASE-B)
- Tests de delivery actualizados y pasando
- Suite completa: 3,158+ tests, 0 fallos

---

## Tareas

### T1: Logging de fallback (NF-2)

**Objetivo**: Reemplazar `except Exception: pass` con logging visible.

**Archivos afectados**:
- `modules/delivery/delivery_packager.py` (L161-162 o equivalente post-rewrite)

**Cambio**:
```python
# ANTES:
except Exception:
    pass  # Legacy mode: no DeliveryContext available

# DESPUES:
except Exception as e:
    logger.warning(
        "DeliveryContext load failed, falling back to legacy mode: %s", e,
        exc_info=True
    )
    self.legacy_mode = True  # Flag visible para debugging
```

**Criterios de aceptacion**:
- [ ] `except Exception: pass` eliminado
- [ ] `logger.warning()` con mensaje descriptivo y exc_info
- [ ] Flag `legacy_mode` accesible para tests

### T2: Severidad en main.py (NF-3)

**Objetivo**: Elevar fallo de delivery de WARN a ERROR con exit code.

**Archivos afectados**:
- `main.py` (L3075-3077 o equivalente)

**Cambio**:
```python
# ANTES:
except Exception as e:
    print(f"   [WARN] Delivery packaging failed: {e}")
    delivery_zip_path = None

# DESPUES:
except Exception as e:
    print(f"   [ERROR] Delivery packaging FAILED: {e}")
    print(f"   [ERROR] Content is ready but ZIP delivery could not be created.")
    print(f"   [ERROR] Review deliveries/ directory for orphaned artifacts.")
    delivery_zip_path = None
    delivery_error = str(e)  # Preservar para report final
```

**Nota**: NO hacer `sys.exit(1)` — el contenido esta listo y el operador puede querer recuperarlo. Pero el mensaje debe ser inequivoco: `[ERROR]`, no `[WARN]`.

**Criterios de aceptacion**:
- [ ] Mensaje usa `[ERROR]` (no `[WARN]`)
- [ ] Instruccion de recovery visible
- [ ] `delivery_error` preservado para report

### T3: Cleanup en camino de error (NF-4)

**Objetivo**: Que el camino de error limpie TODOS los artefactos, no solo el ZIP.

**Archivos afectados**:
- `modules/delivery/delivery_packager.py` (metodo de cleanup)

**Implementacion**:
```python
def _cleanup_on_error(self, zip_path, manifest_path, readme_path):
    """Limpia TODOS los artefactos en camino de error (NF-4)."""
    for artifact in [zip_path, manifest_path, readme_path]:
        if artifact and artifact.exists():
            artifact.unlink()
            logger.info("Cleaned up orphaned artifact: %s", artifact)
    # Tambien limpiar IMPLEMENTATION_ORDER.md si existe
    impl_order = self.deliveries_dir / "IMPLEMENTATION_ORDER.md"
    if impl_order.exists():
        impl_order.unlink()
```

**Adicional**: Cleanup de MANIFESTs anteriores al inicio de cada ejecucion:
```python
def _cleanup_stale_artifacts(self, hotel_id):
    """Limpia MANIFESTs huerfanos de ejecuciones anteriores."""
    for stale in self.deliveries_dir.glob(f"{hotel_id}_*_MANIFEST.json"):
        stale.unlink()
        logger.info("Removed stale MANIFEST: %s", stale)
```

**Criterios de aceptacion**:
- [ ] Camino de error limpia ZIP + MANIFEST + README + IMPLEMENTATION_ORDER
- [ ] Cleanup de MANIFESTs anteriores al inicio
- [ ] Test verifica que no quedan artefactos tras fallo

### T4: Unificar datetime (NF-5) + Conectar FASE-5 (NF-6)

**Objetivo**: Fix de los dos fallos de baja severidad.

**NF-5**: Pasar `date_str` a `_make_zip_filename()`:
```python
# ANTES:
def _make_zip_filename(self, hotel_id):
    return f"{hotel_id}_{datetime.now().strftime('%Y%m%d')}.zip"

# DESPUES:
def _make_zip_filename(self, hotel_id, date_str):
    return f"{hotel_id}_{date_str}.zip"
```

**NF-6**: Conectar params FASE-5 desde main.py:
```python
# main.py L3066-3071: pasar parametros a package()
zip_path = packager.package(
    source_dir=hotel_output_dir,
    hotel_id=hotel_id,
    hotel_name=hotel_name,          # ← NUEVO
    delivery_context=delivery_ctx,
    quality_metadata=quality_meta,
)
```

**Criterios de aceptacion**:
- [ ] Una sola llamada a `datetime.now()` por ejecucion de packaging
- [ ] MANIFEST y ZIP filename usan la misma fecha
- [ ] `hotel_name` pasado a `package()` desde main.py

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| NF-2: fallback logging | `tests/delivery/test_delivery_packager.py` | Warning log visible |
| NF-4: cleanup on error | `tests/delivery/test_delivery_packager.py` | 0 artefactos tras fallo |
| NF-5: datetime unity | `tests/delivery/test_delivery_packager.py` | Mismo date en ZIP y MANIFEST |
| Suite delivery | `tests/delivery/` | Todos pasan |

**Comando de validacion**:
```bash
./venv/Scripts/python.exe -m pytest tests/delivery/ -v
./venv/Scripts/python.exe -m pytest tests/ -x -q --tb=short
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecucion (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar FASE-C como ✅ Completada
2. **`09-documentacion-post-proyecto.md`**: Seccion B (funcionalidades), D (metricas)
3. **Ejecutar**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-C --desc "Error Handling: logging fallback NF-2, severidad ERROR NF-3, cleanup NF-4, datetime NF-5, FASE-5 params NF-6" \
    --archivos-mod "modules/delivery/delivery_packager.py,main.py,tests/delivery/test_delivery_packager.py" \
    --tests "4" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] NF-2: `except Exception: pass` reemplazado por `logger.warning()` + flag
- [ ] NF-3: `[WARN]` reemplazado por `[ERROR]` en main.py
- [ ] NF-4: Cleanup completo en camino de error (ZIP + MANIFEST + README + IMPL_ORDER)
- [ ] NF-4b: Cleanup de MANIFESTs stale al inicio
- [ ] NF-5: `date_str` unificado (una sola llamada `datetime.now()`)
- [ ] NF-6: `hotel_name` pasado a `package()` desde main.py
- [ ] Tests nuevos para NF-2, NF-4, NF-5 pasando
- [ ] Suite completa: 0 fallos
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] `log_phase_completion.py` ejecutado

---

## Restricciones

- Maximo 60 iteraciones del agente
- NO modificar la logica de single-write de FASE-B (solo agregar manejo de errores alrededor)
- NO hacer `sys.exit(1)` en main.py (el contenido debe ser recuperable)
- NO ejecutar v4complete (eso es FASE-D)
- NO modificar `delivery_context.py`
