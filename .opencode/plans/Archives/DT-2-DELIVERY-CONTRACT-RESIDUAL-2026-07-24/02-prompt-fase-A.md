# FASE-A — Conteo README + String-vs-Enum (P-01, P-07)

> **Plan**: DT-2-DELIVERY-CONTRACT-RESIDUAL-2026-07-24
> **Fase**: A (primera fase de código)
> **Findings**: P-01 (conteo 44 vs 46), P-07 (string vs enum)
> **Ejecución**: SUBAGENTE (delegate_task)
> **Dependencias**: Ninguna (primera fase)
> **Próxima fase**: FASE-B

---

## Contexto

DT-1 implementó el delivery contract con packager dinámico y 28 tests. La auditoría
post-DT-1 encontró 2 fixes de severidad BAJA en `delivery_packager.py`:

### P-01: Inconsistencia de conteo "44 vs 46" archivos en Overview del README

**Evidencia**:
- README L13 dice: `Contents: 44 files (117.1 KB)`
- MANIFEST.json dice: `total_files: 46`, `total_size_bytes: 131697`
- ZIP real: 46 archivos

**Causa raíz**: `create_readme()` en L450 calcula `TOTAL_FILES` como
`len(delivery_context.files)`. El campo `delivery_context.files` contiene los
archivos ANTES de que el packager agregue los meta-archivos (MANIFEST.json y
README_DELIVERY.md). Por tanto el conteo es 44 (sin meta) mientras el ZIP final
tiene 46 (con meta).

**Ubicación verificada en código vivo**:
- `delivery_packager.py` L175: `self.create_readme(...)` (Pass 1, antes del manifest)
- `delivery_packager.py` L450: `content.replace("{{TOTAL_FILES}}", str(len(delivery_context.files)))`
- `delivery_packager.py` L453: `content.replace("{{TOTAL_SIZE}}", self._format_bytes(total_size))`
- `delivery_packager.py` L178-179: Pass 2 (manifest construction, DESPUÉS del README)
- `delivery_packager.py` L189-194: Pass 3 (MANIFEST.json added to manifest)

**Fix propuesto**: Opción 2 (Recalcular post-manifest) — mínimamente invasiva.
Después de Pass 3, hacer un replace de `{{TOTAL_FILES}}` y `{{TOTAL_SIZE}}`
en el README ya escrito, leyendo los conteos finales del manifest.

### P-07: Inconsistencia de comparación string vs enum en filtro

**Evidencia**:
- `delivery_packager.py` L603: `a.state.name == 'DELIVERED'` (comparación por string)
- `delivery_context.py` L408: `a.state == DeliveryAssetState.DELIVERED` (comparación por enum)

Si el enum name cambiara, L603 fallaría silenciosamente (retorna lista vacía).

**Ubicación verificada en código vivo**:
- `delivery_packager.py` L603: `delivered = [a for a in ctx.assets if getattr(a, 'state', None) and a.state.name == 'DELIVERED']`
- También L706 y L740 usan el mismo patrón `a.state.name in (...)`

**Fix propuesto**: Unificar a `a.state == DeliveryAssetState.DELIVERED` (o el
equivalente con `in` para los casos de múltiples estados).

---

## Tareas

### Tarea A-1: Fix P-01 — Recalcular conteo post-manifest en README

**Archivo**: `modules/delivery/delivery_packager.py`

1. Leer el archivo completo, localizar el método `create_readme()` (L419)
2. Localizar el bloque donde se renderiza el README con `delivery_context` (L450-453)
3. Después de Pass 3 (donde MANIFEST.json se añade al manifest, ~L189-194),
   agregar un post-procesamiento que:
   a. Lea el manifest final (con meta-archivos incluidos)
   b. Recalcule total_files y total_size incluyendo MANIFEST.json y README_DELIVERY.md
   c. Haga un replace de `{{TOTAL_FILES}}` y `{{TOTAL_SIZE}}` en el README ya escrito
4. Alternativamente, mover `create_readme()` después de `create_manifest()`
   (opción 1 del contexto) si resulta más limio en el flujo de passes
5. Mantener backward compatibility: el legacy mode (sin DeliveryContext) ya lee
   del manifest (L497-498), por lo que el fix solo afecta el dynamic mode

**Verificación**: El README debe mostrar el mismo número que MANIFEST.json `total_files`.

### Tarea A-2: Fix P-07 — Unificar comparación string vs enum

**Archivo**: `modules/delivery/delivery_packager.py`

1. L603: cambiar `a.state.name == 'DELIVERED'` → `a.state == DeliveryAssetState.DELIVERED`
2. L706: cambiar `a.state.name in ('DELIVERED', 'ESTIMATED')` → `a.state in (DeliveryAssetState.DELIVERED, DeliveryAssetState.ESTIMATED)`
3. L740: cambiar `a.state.name in ('DELIVERED', 'ESTIMATED')` → `a.state in (DeliveryAssetState.DELIVERED, DeliveryAssetState.ESTIMATED)`
4. Asegurar que `DeliveryAssetState` esté importado en delivery_packager.py
   (verificar `from .delivery_context import DeliveryAssetState` o similar)

**Verificación**: `grep -n "state.name ==\|state.name in" delivery_packager.py` retorna 0 resultados.

### Tarea A-3: Verificar que los 28 tests existentes siguen pasando

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/delivery/test_delivery_contract.py -v
```

Si pytest no está en el venv, instalarlo primero:
```bash
./venv/Scripts/python.exe -m pip install pytest
```

---

## Criterios de Completitud

- [ ] P-01: README Overview muestra el mismo `total_files` que MANIFEST.json
- [ ] P-07: 0 ocurrencias de `state.name ==` o `state.name in` en delivery_packager.py
- [ ] 28 tests existentes pasan sin modificación
- [ ] Backward compatibility: `create_readme()` legacy mode (sin DeliveryContext) funciona
- [ ] Commit con mensaje descriptivo

---

## Post-Ejecución

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-A-DT2 --desc "P-01_conteo_README_post-manifest_P-07_string_vs_enum_unified"
```

---

## Prompt para delegate_task (SUBAGENTE)

```
Goal: Fix P-01 (README file count mismatch) and P-07 (string vs enum comparison) in iah-cli's delivery_packager.py

Context:
- Repo path: /mnt/c/Users/Jhond/Github/iah-cli
- File to modify: modules/delivery/delivery_packager.py

P-01 Fix (file count 44 vs 46):
The create_readme() method at L450 computes TOTAL_FILES as len(delivery_context.files)
which is 44 (pre-meta-files). But MANIFEST.json reports 46 (including MANIFEST.json and
README_DELIVERY.md). The fix: after the manifest is fully built (Pass 3, ~L189-194),
recalculate and update the README's {{TOTAL_FILES}} and {{TOTAL_SIZE}} placeholders
with the final counts from the manifest. Keep backward compatibility: the legacy mode
(without DeliveryContext, L497-498) already reads from manifest, so only the dynamic
mode (with DeliveryContext, L450-453) needs fixing.

P-07 Fix (string vs enum):
L603: a.state.name == 'DELIVERED' → a.state == DeliveryAssetState.DELIVERED
L706: a.state.name in ('DELIVERED', 'ESTIMATED') → a.state in (DeliveryAssetState.DELIVERED, DeliveryAssetState.ESTIMATED)
L740: same as L706
Ensure DeliveryAssetState is imported from delivery_context.

After fixes, verify:
1. grep -n "state.name ==\|state.name in" delivery_packager.py → 0 results
2. Run: ./venv/Scripts/python.exe -m pytest tests/delivery/test_delivery_contract.py -v
   (install pytest first if needed: ./venv/Scripts/python.exe -m pip install pytest)
3. All 28 existing tests must pass

Commit with message: "fix(delivery): P-01 README count post-manifest + P-07 enum comparison"
```

---

## Próxima Sesión

```
Carga el plan DT-2 en /mnt/c/Users/Jhond/Github/iah-cli//.opencode/plans/Archives/DT-2-DELIVERY-CONTRACT-RESIDUAL-2026-07-24/
Ejecuta FASE-B: 03-prompt-fase-B.md (P-02: exclusión mutua advisory sections)
```
