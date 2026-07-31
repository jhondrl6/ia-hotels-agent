# FASE-4 — Assets Deprecados Cleanup (B3+B4+B5+F5)

**ID**: ROICRIII-FASE-4
**Objetivo**: Filtrar assets deprecados de la lista de activos digitales y del catálogo técnico.
**Dependencias**: FASE-3 ✅ (validator + BREACH corregidos)
**Complejidad**: 🟡 MEDIA — Cambios en 2 archivos (generator + service_catalog)
**Skill**: `iah-cli-phased-execution`

---

## Contexto

La lista "Activos digitales que quedan en su propiedad" incluye 4 assets deprecados:
- `og_tags_guide` → fusionado con `open_graph`
- `indirect_traffic_optimization` → movido a consultoría upsell manual
- `local_content_page` → bonus advisory, no infraestructura
- `optimization_guide` → genérico, sin propósito claro

`_build_activos_digitales_lista` (v4_proposal_generator.py) itera sobre `asset_plan` sin filtrar.
`TECHNICAL_ASSET_CATALOG` (service_catalog.py) incluye `indirect_traffic_optimization`.

---

## Tareas

### T1: Filtrar deprecados en _build_activos_digitales_lista [B3]

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py`

Grep para `_build_activos_digitales_lista` o `def _build_activos`.

**Añadir constante al inicio del método o a nivel de clase**:
```python
DEPRECATED_ASSETS = {
    "og_tags_guide",
    "indirect_traffic_optimization",
    "local_content_page",
    "optimization_guide",
}
```

**Modificar el loop** que construye la lista para filtrar:
```python
for asset in asset_plan:
    name = getattr(asset, 'asset_type', '') or getattr(asset, 'name', '') or str(asset)
    if name and name not in DEPRECATED_ASSETS:
        activos.append(f"- {name}")
```

**Criterios**:
- [ ] `DEPRECATED_ASSETS` set existe con los 4 assets
- [ ] El loop filtra correctamente

### T2: Remover indirect_traffic_optimization de TECHNICAL_ASSET_CATALOG [B4+F5]

**Archivo**: `modules/commercial_documents/service_catalog.py`

Grep para `indirect_traffic_optimization` en el archivo.

**ACCIÓN**: Eliminar la entrada completa de `TECHNICAL_ASSET_CATALOG`. Grep primero para verificar que la entrada existe y su formato exacto (TechnicalAssetEntry).

**Verificar**: Grep para `indirect_traffic_optimization` en TODO el codebase para confirmar que no hay otros consumidores.
```bash
grep -rn "indirect_traffic_optimization" modules/ tests/ config/
```

**Criterios**:
- [ ] `indirect_traffic_optimization` NO está en TECHNICAL_ASSET_CATALOG
- [ ] Otros assets en el catálogo no afectados
- [ ] No import errors

### T3: Verificar que asset_plan no inyecta deprecados desde config [B5]

**Archivo**: `config/commercial.yaml` o donde se defina el asset_plan

Grep para `og_tags_guide`, `local_content_page`, `optimization_guide` en config/ y modules/.

**SI se encuentran en config**: Comentar o eliminar las entradas.
**SI no se encuentran**: La protección de T1 (filtro en el loop) es suficiente. Documentar hallazgo.

**Criterios**:
- [ ] Los 4 assets deprecados no aparecen en config/
- [ ] O el filtro T1 los captura si vienen del asset_plan

---

## Tests Obligatorios

| Test | Archivo | Criterio |
|------|---------|----------|
| `test_activated_assets_filtered` | `tests/commercial_documents/test_financial_coherence.py` o nuevo | 4 deprecados excluidos |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/commercial_documents/ -v
./venv/Scripts/python.exe -m pytest tests/ -v --tb=short
```

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`** — Marcar FASE-4 como ✅ Completada
2. **`06-checklist-implementacion.md`** — Actualizar estado
3. **`09-documentacion-post-proyecto.md`** — Sección C
4. **log_phase_completion.py**:
```bash
cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe" scripts/log_phase_completion.py --fase FASE-4 --desc "Assets_deprecados_cleanup_B3_B4_B5_F5" --archivos-mod "modules/commercial_documents/v4_proposal_generator.py,modules/commercial_documents/service_catalog.py" --tests "1" --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] 4 assets deprecados filtrados de la lista de activos
- [ ] `indirect_traffic_optimization` removido de TECHNICAL_ASSET_CATALOG
- [ ] grep global confirma 0 apariciones de deprecados en output
- [ ] Test nuevo pasa + no regresiones
- [ ] run_all_validations.py --quick pasa
- [ ] Post-ejecución completada

---

## Restricciones

- NO modificar lógica de generación de assets (`v4_asset_orchestrator.py` etc.)
- Solo filtrar en el render/output, no en el pipeline de generación
- Grep global ANTES de eliminar para no romper otros consumidores
- Límite: 60 iteraciones
