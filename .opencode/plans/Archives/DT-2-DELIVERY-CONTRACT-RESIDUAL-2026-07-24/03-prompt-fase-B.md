# FASE-B — Exclusión Mutua Advisory Sections (P-02)

> **Plan**: DT-2-DELIVERY-CONTRACT-RESIDUAL-2026-07-24
> **Fase**: B (segunda fase de código)
> **Finding**: P-02 (assets advisory en múltiples secciones del README)
> **Ejecución**: SUBAGENTE (delegate_task)
> **Dependencias**: FASE-A completada (L603 ya usa enum)
> **Próxima fase**: FASE-C

---

## Contexto

### P-02: Assets advisory aparecen en múltiples secciones del README

**Severidad**: MEDIA (AMPLIFICADO — originalmente BAJA, scope subestimado)

**Evidencia en `zione_20260724.zip` → README_DELIVERY.md**:

| Asset | Sección 1 (state-based) | Línea | Sección 2 (advisory) | Línea |
|-------|------------------------|-------|---------------------|-------|
| whatsapp_conflict_guide | Deliverable Assets | L55 | Advisory Guides | L89 |
| optimization_guide | Estimated Assets | L77 | Advisory Guides | L90 |
| analytics_setup_guide | Estimated Assets | L79 | Advisory Guides | L91 |
| og_tags_guide | Estimated Assets | L81 | Advisory Guides | L92 |

**Causa raíz (ampliada)**: Defecto sistémico de aislamiento de filtros en
`delivery_context.py`. Cada property opera independientemente sin exclusión mutua:

```python
# delivery_context.py L407-408 (verificado en código vivo)
delivered_assets → [a for a in self.assets if a.state == DeliveryAssetState.DELIVERED]
# NO excluye is_advisory

# delivery_context.py L419-420
estimated_assets → [a for a in self.assets if a.state == DeliveryAssetState.ESTIMATED]
# NO excluye is_advisory

# delivery_context.py L423-425
advisory_assets → [a for a in self.assets if a.is_advisory]
# NO excluye por state
```

`whatsapp_conflict_guide` tiene `state=DELIVERED` + `is_advisory=True` → aparece
en Deliverable Assets Y Advisory Guides.
`optimization_guide`, `analytics_setup_guide`, `og_tags_guide` tienen
`state=ESTIMATED` + `is_advisory=True` → aparecen en Estimated Assets Y Advisory Guides.

El filtro en `_generate_deliverable_instructions()` (L603) usa
`a.state == DeliveryAssetState.DELIVERED` (ya corregido en FASE-A) sin check de `is_advisory`.

**Fix propuesto**: Opción 1 (Filtros con exclusión) — mínimamente invasiva.
Modificar los properties en `delivery_context.py` para que advisory excluya de
las secciones state-based:
- `delivered_assets`: `state == DELIVERED AND NOT is_advisory`
- `estimated_assets`: `state == ESTIMATED AND NOT is_advisory`
- `advisory_assets`: sin cambio (es la sección canónica para guides)

---

## Tareas

### Tarea B-1: Modificar properties con exclusión mutua

**Archivo**: `modules/delivery/delivery_context.py`

1. Leer `delivered_assets` property (L407-408):
   ```python
   @property
   def delivered_assets(self) -> List[DeliveryAssetEntry]:
       return [a for a in self.assets if a.state == DeliveryAssetState.DELIVERED]
   ```
   Cambiar a:
   ```python
   @property
   def delivered_assets(self) -> List[DeliveryAssetEntry]:
       return [a for a in self.assets if a.state == DeliveryAssetState.DELIVERED and not a.is_advisory]
   ```

2. Leer `estimated_assets` property (L419-420):
   ```python
   @property
   def estimated_assets(self) -> List[DeliveryAssetEntry]:
       return [a for a in self.assets if a.state == DeliveryAssetState.ESTIMATED]
   ```
   Cambiar a:
   ```python
   @property
   def estimated_assets(self) -> List[DeliveryAssetEntry]:
       return [a for a in self.assets if a.state == DeliveryAssetState.ESTIMATED and not a.is_advisory]
   ```

3. `advisory_assets` (L423-425) permanece sin cambio:
   ```python
   @property
   def advisory_assets(self) -> List[DeliveryAssetEntry]:
       return [a for a in self.assets if a.is_advisory]
   ```

### Tarea B-2: Modificar filtro en _generate_deliverable_instructions

**Archivo**: `modules/delivery/delivery_packager.py`

L603 (ya corregido por FASE-A para usar enum):
```python
delivered = [a for a in ctx.assets if getattr(a, 'state', None) and a.state == DeliveryAssetState.DELIVERED]
```
Cambiar a:
```python
delivered = [a for a in ctx.assets if getattr(a, 'state', None) and a.state == DeliveryAssetState.DELIVERED and not getattr(a, 'is_advisory', False)]
```

Esto asegura que el filtro inline en `_generate_deliverable_instructions` también
excluya advisory assets, consistente con el property `delivered_assets`.

### Tarea B-3: Verificar que los 28 tests existentes siguen pasando

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/delivery/test_delivery_contract.py -v
```

Si algún test falla por el cambio de exclusión mutua, el test probablemente
asumía que advisory aparecía en delivered/estimated sections — documentar el
cambio esperado y actualizar el test assertion con justificación.

---

## Criterios de Completitud

- [ ] `delivered_assets` excluye `is_advisory == True`
- [ ] `estimated_assets` excluye `is_advisory == True`
- [ ] `advisory_assets` sin cambios (canónica)
- [ ] L603 en delivery_packager.py excluye advisory
- [ ] 28 tests existentes pasan (o se documentan cambios esperados)
- [ ] Commit con mensaje descriptivo

---

## Post-Ejecución

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-B-DT2 --desc "P-02_advisory_mutual_exclusion_delivered_estimated_sections"
```

---

## Prompt para delegate_task (SUBAGENTE)

```
Goal: Fix P-02 (advisory assets appearing in multiple README sections) in iah-cli's delivery_context.py and delivery_packager.py

Context:
- Repo path: /mnt/c/Users/Jhond/Github/iah-cli
- Files to modify: modules/delivery/delivery_context.py, modules/delivery/delivery_packager.py

Problem: Advisory assets (is_advisory=True) appear in BOTH state-based sections
(Deliverable Assets / Estimated Assets) AND Advisory Guides section in the README.
This is because the filter properties don't exclude advisory from state-based sections.

Fix — modify 2 properties in delivery_context.py:
1. delivered_assets (L407-408): add `and not a.is_advisory` to the filter
2. estimated_assets (L419-420): add `and not a.is_advisory` to the filter
3. advisory_assets (L423-425): NO CHANGE (canonical section for guides)

Also fix delivery_packager.py L603:
- Current: `delivered = [a for a in ctx.assets if getattr(a, 'state', None) and a.state == DeliveryAssetState.DELIVERED]`
- Change to: `delivered = [a for a in ctx.assets if getattr(a, 'state', None) and a.state == DeliveryAssetState.DELIVERED and not getattr(a, 'is_advisory', False)]`

After fix, verify:
1. grep -n "is_advisory" modules/delivery/delivery_context.py → should show the new exclusion filters
2. Run: ./venv/Scripts/python.exe -m pytest tests/delivery/test_delivery_contract.py -v
   (install pytest first if needed: ./venv/Scripts/python.exe -m pip install pytest)
3. All 28 existing tests must pass. If a test fails because it expected advisory assets
   in delivered/estimated sections, that's the EXPECTED change — update the test assertion
   and note the reason in the commit message.

Commit with message: "fix(delivery): P-02 advisory assets mutual exclusion in README sections"
```

---

## Próxima Sesión

```
Carga el plan DT-2 en /mnt/c/Users/Jhond/Github/iah-cli/.opencode/plans/DT-2-DELIVERY-CONTRACT-RESIDUAL-2026-07-24/
Ejecuta FASE-C: 04-prompt-fase-C.md (P-03 + P-05: quality report post-gen + G9 dead gate)
```
