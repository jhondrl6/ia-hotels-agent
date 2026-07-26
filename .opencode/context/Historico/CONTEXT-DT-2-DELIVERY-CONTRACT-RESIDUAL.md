# Contexto: DT-2 — Delivery Contract Residual Fixes (Post-DT-1)

> **Origen**: Evaluación post-DT-1 (sesión 2026-07-24)
> **Versión evaluada**: v4.63.1 (Delivery-Contract, commit acf943b)
> **Hotel de referencia**: Zi One Luxury (https://zione.co/)
> **ZIP evaluado**: `output/v4_complete/deliveries/zione_20260724.zip`
> **ZIP comparación (pre-DT-1)**: `output/ZiOne/v4_complete/deliveries/zione_20260723.zip`
> **Severidad**: MEDIA-ALTA — no bloquea entrega, pero el "4/4 gates PASS" es factualmente incorrecto
> **Fecha del contexto**: 2026-07-24
> **Última auditoría contra código vivo**: 2026-07-24 (auditoría exhaustiva con amplificaciones)

---

## 1. Evaluación de DT-1

El plan DT-1-DELIVERY-CONTRACT-2026-07-23 ejecutó 5 fases (A→E) en 6 commits
(b1651dd → aff4308). La evaluación sistemática concluyó:

- **10/14 hallazgos CONFIRMED** (F-01 a F-06, F-09 a F-11, F-14)
- **2/14 hallazgos PARCIAL** (F-12, F-13 — documentados como deuda técnica TD-2 y TD-4)
- **2/14 NO TESTABLE** (F-07, F-08 — no se manifestaban en esta ejecución)

**Calificación DT-1**: 7.5/10 como evolución del delivery contract.

Los componentes implementados (DeliveryAssetState, DeliveryAssetEntry,
DeliveryContext, packager dinámico, 28 tests de contrato) son sólidos.
El gap a 10/10 se compone de 4 problemas específicos documentados a
continuación, ampliados a 7 findings tras auditoría exhaustiva contra código vivo.

---

## 2. Problemas residuales (7 findings: 4 originales + 3 nuevos)

### P-01: Inconsistencia de conteo "44 vs 46" archivos en Overview del README

**Severidad**: BAJA
**Hallazgo DT-1 relacionado**: F-02, F-10 (README derivado de datos reales)
**Estado**: CONFIRMADO en auditoría código vivo. Línea real: L450 (no L452 como se estimó inicialmente).

**Evidencia**:
- README L13 dice: `**Contents:** 44 files (117.1 KB)`
- MANIFEST.json dice: `total_files: 46`, `total_size_bytes: 131697`
- ZIP real: 46 archivos

**Causa raíz**:
`create_readme()` en `delivery_packager.py` L450 calcula `TOTAL_FILES` como
`len(delivery_context.files)`. El campo `delivery_context.files` se construye
a partir del parámetro `files` pasado a `DeliveryContext.from_asset_generation_report()`,
que contiene los archivos ANTES de que el packager agregue los meta-archivos
(MANIFEST.json y README_DELIVERY.md). Por tanto el conteo es 44 (sin meta)
mientras el ZIP final tiene 46 (con meta).

```python
# delivery_packager.py L450
content = content.replace("{{TOTAL_FILES}}", str(len(delivery_context.files)))
```

El `TOTAL_SIZE` también se calcula de `delivery_context.files` (117.1 KB)
mientras el manifest reporta 131,697 bytes (128.6 KB). Hay una triple
inconsistencia: README dice 44 archivos/117.1 KB, manifest dice 46/131,697,
ZIP real tiene 46/131,697.

El README se renderiza en Pass 1 (L175), el manifest se construye en Pass 2
(L178-179), y el MANIFEST.json se añade al manifest en Pass 3 (L189-194).
La información correcta existe pero en el orden equivocado.

**Fix propuesto** (dos opciones):
1. **Reordenar passes**: Mover `create_readme()` después de `create_manifest()`
   para que el README pueda leer los conteos finales del manifest.
2. **Recalcular post-manifest**: Después de Pass 3, hacer un replace de
   `{{TOTAL_FILES}}` y `{{TOTAL_SIZE}}` en el README ya escrito, leyendo
   del manifest final.

La opción 1 es más limpia conceptualmente. La opción 2 es mínimamente invasiva.

**Archivo**: `modules/delivery/delivery_packager.py` (método `create_readme`, L450)
**Archivo**: `modules/delivery/delivery_packager.py` (passes L173-196)
**Archivo**: `modules/delivery/delivery_context.py` (campo `files`, L150)

---

### P-02: Assets advisory aparecen en múltiples secciones del README

**Severidad**: MEDIA (AMPLIFICADO — originalmente BAJA, scope subestimado)
**Hallazgo DT-1 relacionado**: F-03 (diferenciación por tipo de asset)
**Estado**: CONFIRMADO + AMPLIFICADO en auditoría. El documento original reportaba
solo 1 asset duplicado; la realidad son 4 assets duplicados.

**Evidencia** en `zione_20260724.zip` → README_DELIVERY.md:

El documento original reportaba solo `whatsapp_conflict_guide` en dos secciones.
Auditoría contra el ZIP real reveló que **TODOS los assets advisory aparecen en
dos secciones simultáneamente**:

| Asset | Sección 1 (state-based) | Línea | Sección 2 (advisory) | Línea |
|-------|------------------------|-------|---------------------|-------|
| whatsapp_conflict_guide | Deliverable Assets | L55 | Advisory Guides | L89 |
| optimization_guide | Estimated Assets | L77 | Advisory Guides | L90 |
| analytics_setup_guide | Estimated Assets | L79 | Advisory Guides | L91 |
| og_tags_guide | Estimated Assets | L81 | Advisory Guides | L92 |

**Causa raíz (ampliada)**:
El problema es un **defecto sistémico de aislamiento de filtros** en
`delivery_context.py`. Cada property opera independientemente sin exclusión mutua:

```python
# delivery_context.py L408
delivered_assets → [a for a in self.assets if a.state == DELIVERED]
# NO excluye is_advisory

# delivery_context.py L420
estimated_assets → [a for a in self.assets if a.state == ESTIMATED]
# NO excluye is_advisory

# delivery_context.py L425
advisory_assets → [a for a in self.assets if a.is_advisory]
# NO excluye por state
```

`whatsapp_conflict_guide` tiene `state=DELIVERED` + `is_advisory=True` → aparece
en Deliverable Assets Y Advisory Guides.
`optimization_guide`, `analytics_setup_guide`, `og_tags_guide` tienen
`state=ESTIMATED` + `is_advisory=True` → aparecen en Estimated Assets Y Advisory Guides.

El filtro en `_generate_deliverable_instructions()` (L603) usa
`a.state.name == 'DELIVERED'` sin check de `is_advisory`:

```python
# delivery_packager.py L603
delivered = [a for a in ctx.assets if getattr(a, 'state', None) and a.state.name == 'DELIVERED']
```

**Fix propuesto** (dos opciones):
1. **Filtros con exclusión**: Modificar los properties en `delivery_context.py` para
   que advisory excluya de las secciones state-based:
   - `delivered_assets`: `state==DELIVERED AND NOT is_advisory`
   - `estimated_assets`: `state==ESTIMATED AND NOT is_advisory`
   - `advisory_assets`: sin cambio (es la sección canónica para guides)
2. **Partición canónica**: Implementar un método `get_section_assignment()` que
   asigna cada asset a UNA sección exacta, garantizando partición disjunta.

La opción 1 es mínimamente invasiva. La opción 2 es más robusta a futuro.

**Archivo**: `modules/delivery/delivery_packager.py` (método `_generate_deliverable_instructions`, L601-613)
**Archivo**: `modules/delivery/delivery_context.py` (properties L407-425)
**Archivo**: `modules/delivery/delivery_context.py` (enum DeliveryAssetState, L15)

---

### P-03: delivery_quality_report no refleja score post-generación (TD-4)

**Severidad**: MEDIA
**Hallazgo DT-1 relacionado**: F-12
**Estado**: CONFIRMADO en auditoría. Ubicación exacta resuelta.

**Evidencia**:
- `delivery_quality_report.json` reporta `coherence_score: 0.84`
- `coherence_validation.json` (pre-gen): `overall_score: 0.84`
- `coherence_validation_post_gen.json` (post-gen): `overall_score: 0.82`
- `asset_generation_report.json`: `coherence_score_pre: 0.84`, `coherence_score_post: 0.82`

El quality report usa el score PRE-generación (0.84) en vez del
POST-generación (0.82). La diferencia de 0.02 indica que la generación
de assets degradó ligeramente la coherencia, pero el quality report no
lo refleja.

**Causa raíz**:
`delivery_quality_report.py` L122 lee `coherence_validation.json` (pre-gen)
y nunca intenta leer `coherence_validation_post_gen.json`:

```python
# delivery_quality_report.py L122
coherence_data = self._load_json(v4_audit_path / "coherence_validation.json")
```

No existe lógica para buscar el archivo post-gen. El módulo `_extract_coherence()`
(L269-279) extrae `overall_score` del archivo cargado, sin saber si es pre o post.

**Archivo**: `modules/quality_gates/delivery_quality_report.py` (método `generate`, L122)
**Archivo**: `modules/quality_gates/delivery_quality_report.py` (helper `_extract_coherence`, L269-279)

**Fix propuesto**: Leer `coherence_validation_post_gen.json` cuando exista,
con fallback a `coherence_validation.json`. Reportar ambos scores
(pre y post) para transparencia.

---

### P-04: proposal_asset_matrix diverge del alignment gate (TD-2)

**Severidad**: MEDIA (AMPLIFICADO)
**Hallazgo DT-1 relacionado**: F-13
**Estado**: CONFIRMADO + AMPLIFICADO. Además de la divergencia semántica,
el archivo no se empaqueta en el ZIP.

**Evidencia**:
- `proposal_asset_matrix.json` **NO existe en el ZIP** (`zione_20260724.zip`)
  ni en disco bajo `output/v4_complete/` ni `output/v4_complete/zione/v4_audit/`.
- La matrix se genera en `v4_proposal_generator.py` L642 con ruta
  `output_path / "v4_audit" / "proposal_asset_matrix.json"` = `output/v4_complete/v4_audit/`.
- El packager opera sobre `source_dir = output/v4_complete/zione/`, que NO incluye
  la ruta `output/v4_complete/v4_audit/`.
- El proposal_asset_matrix tiene definición de cobertura diferente al alignment gate:
  - `proposal_asset_matrix`: "¿el servicio cumple la propuesta comercial?"
  - alignment gate: "¿el asset existe (generated OR present in production)?"

**Causa raíz**:
1. **Path mismatch**: La matrix se escribe en `output/v4_complete/v4_audit/`
   mientras el packager recoge archivos de `output/v4_complete/zione/`.
2. **Dos sistemas independientes**: El matrix compara contra la propuesta comercial
   usando `PainSolutionMapper.PAIN_SOLUTION_MAP`; el gate compara contra el estado
   de assets usando `PROPOSAL_SERVICE_TO_ASSET`. No hay un contrato compartido.

**Archivo**: `modules/asset_generation/proposal_asset_alignment.py` (L450, save path)
**Archivo**: `modules/commercial_documents/v4_proposal_generator.py` (L642, output_path)
**Archivo**: `modules/delivery/delivery_packager.py` (`_collect_files`, source_dir)

**Fix propuesto**:
1. Asegurar que `ProposalAssetMatrix.save()` escriba a la ruta que `_collect_files()` recoge.
2. Unificar el modelo de cobertura: hacer que `proposal_asset_matrix` consuma
   `DeliveryContext.assets` como fuente de verdad (ahora que existe el contrato
   canónico post-DT-1).

---

### P-05 (NUEVO): proposal_asset_gate es un DEAD GATE en delivery_quality_report

**Severidad**: ALTA
**Hallazgo DT-1 relacionado**: Ninguno directo (descubierto en auditoría amplificada)
**Estado**: NUEVO — no existía en el documento original.

**Evidencia**:
El `delivery_quality_report.json` en el ZIP reporta:
```json
"proposal_asset_gate": {"passed": true, "gate": "G9"}
```
Pero este gate **nunca es evaluado**. Es un default hardcodeado.

En `delivery_quality_report.py` L238:
```python
proposal_asset_gate=gate_results.get("proposal_asset_alignment", {"passed": True, "gate": "G9"}),
```

El diccionario `gate_results` se popula con claves: `"coherence"`, `"coverage"`,
`"asset_specificity"`, `"evidence"`. La clave `"proposal_asset_alignment"` **nunca
se inserta**. El `.get()` siempre retorna el default `{"passed": True, "gate": "G9"}`.

Además, en L205:
```python
blocking_gates = [
    name for name, result in gate_results.items()
    if not result["passed"] and name in ("coherence", "coverage", "evidence", "proposal_asset_alignment")
]
```

`"proposal_asset_alignment"` está listado como potencialmente bloqueante, pero como
nunca existe en `gate_results`, nunca puede fallar. El gate tiene la **apariencia**
de estar implementado (está en el dataclass, en el JSON, en la lógica de bloqueo)
pero funcionalmente es un passthrough silencioso.

**Causa raíz**:
El `generate()` evalúa 4 gates (G6 coherence, G7 coverage, G8 specificity, EVIDENCE)
pero NO implementa la evaluación de G9 (proposal_asset_alignment). El campo existe
en el dataclass `DeliveryQualityReport` (L44: `proposal_asset_gate: dict`) y se
reporta en el JSON, pero la lógica de evaluación nunca se escribió.

**Impacto**: El quality report puede dar "PASS" con "4/4 gates" aunque la
alineación propuesta→asset esté rota. El cliente recibe un paquete con
status "PASS" sin que la cobertura comercial haya sido verificada.
Esto vacía de significado el "4/4 gates PASS" del delivery_quality_report.

**Archivo**: `modules/quality_gates/delivery_quality_report.py` (L118-244, método `generate`)
**Archivo**: `modules/quality_gates/delivery_quality_report.py` (L205, blocking_gates logic)
**Archivo**: `modules/quality_gates/delivery_quality_report.py` (L238, dead default)

**Fix propuesto** (dos opciones):
1. **Implementar G9**: Después de cargar `coverage_data`, evaluar la alineación
   usando `ProposalAssetMatrix` o `AlignmentReport`. Poblar
   `gate_results["proposal_asset_alignment"]` con el resultado real.
2. **Eliminar G9 del reporte**: Si el gate no tiene sentido en el contexto actual
   del delivery quality report, eliminar el campo del dataclass, la referencia en
   L205, y el default en L238. No reportar un gate que no se evalúa.

La opción 1 es correcta a largo plazo. La opción 2 es la mínima para no mentir
en el reporte.

---

### P-06 (NUEVO): proposal_asset_matrix.json no se empaqueta en el delivery

**Severidad**: MEDIA
**Hallazgo DT-1 relacionado**: Relacionado con F-13 (TD-2)
**Estado**: NUEVO — no existía en el documento original.

**Evidencia**:
- `proposal_asset_matrix.json` NO aparece en `zione_20260724.zip` (46 entradas,
  ninguna contiene "proposal_asset_matrix").
- NO existe en disco bajo `output/v4_complete/` ni `output/v4_complete/zione/`.
- `ProposalAssetMatrix.save()` escribe a ruta relativa `v4_audit/proposal_asset_matrix.json`.
- El llamador `v4_proposal_generator.py` L642 construye: `output_path / "v4_audit" / "proposal_asset_matrix.json"`.
- `output_path` para v4complete es `output/v4_complete/`, dando: `output/v4_complete/v4_audit/proposal_asset_matrix.json`.
- El packager `_collect_files()` opera sobre `source_dir = output/v4_complete/zione/`.
- La ruta `output/v4_complete/v4_audit/` NO está bajo `output/v4_complete/zione/`, por lo que `_collect_files()` nunca la recoge.

**Causa raíz**:
Path mismatch entre el generador de la matrix y el packager. La matrix se genera
en el directorio flat `v4_audit/` mientras el packager recoge archivos del
subdirectorio del hotel `zione/v4_audit/`.

**Archivo**: `modules/asset_generation/proposal_asset_alignment.py` (L450, save path)
**Archivo**: `modules/commercial_documents/v4_proposal_generator.py` (L642, output_path)
**Archivo**: `modules/delivery/delivery_packager.py` (`_collect_files`, L233-281)

**Fix propuesto**: Asegurar que la matrix se guarde en la misma ruta que el
packager recoge (`source_dir / "v4_audit" / "proposal_asset_matrix.json"`),
o incluir la ruta del directorio flat en `_collect_files()`.

---

### P-07 (NUEVO): Inconsistencia de comparación string vs enum en filtro

**Severidad**: BAJA
**Hallazgo DT-1 relacionado**: Ninguno
**Estado**: NUEVO — fragilidad de código, sin impacto hoy.

**Evidencia**:
En `delivery_packager.py` L603:
```python
delivered = [a for a in ctx.assets if getattr(a, 'state', None) and a.state.name == 'DELIVERED']
```

Mientras en `delivery_context.py` L408:
```python
return [a for a in self.assets if a.state == DeliveryAssetState.DELIVERED]
```

L603 usa comparación por string (`a.state.name == 'DELIVERED'`).
L408 usa comparación por enum (`a.state == DeliveryAssetState.DELIVERED`).

Si el enum name cambiara (ej: `DELIVERED` → `GENERATED`), L603 fallaría
silenciosamente (retorna lista vacía) mientras L408 seguiría funcionando.

**Archivo**: `modules/delivery/delivery_packager.py` (L603)

**Fix propuesto**: Unificar a `a.state == DeliveryAssetState.DELIVERED`.

---

## 3. Estado del código post-DT-1

### Archivos relevantes (existentes)

| Archivo | Líneas | Rol |
|---------|--------|-----|
| `modules/delivery/delivery_context.py` | 534 | DeliveryAssetState, DeliveryAssetEntry, DeliveryContext |
| `modules/delivery/delivery_packager.py` | 810 | Empaquetado, README dinámico, validación |
| `modules/quality_gates/delivery_quality_report.py` | 408 | Quality gates G6/G7/G8/G9 (G9 dead) |
| `modules/asset_generation/proposal_asset_alignment.py` | 598 | ProposalAssetMatrix, AlignmentReport |
| `tests/delivery/test_delivery_contract.py` | 613 | 28 tests de contrato cross-artifact |
| `templates/delivery_readme_template.md` | 63 | Template sin hardcodeos |

### Tests existentes

28 tests en `test_delivery_contract.py` cubriendo:
- DeliveryAssetEntry: from_skipped (6 variantes), from_generated (4 variantes)
- DeliveryContext: properties, from_missing_report, from_invalid_report, advisory, empty
- Cross-artifact: manifest paths POSIX, zip paths POSIX, total_files match,
  total_size match, readme size ≠ 0, entry set equality, zip filename match,
  package structure from real files, no hardcoded whatsapp, no phantom files,
  valid/invalid zip validation

### DeliveryAssetState (7 estados)

```
DELIVERED              # Archivo generado y en ZIP
PRESENT_IN_PRODUCTION  # Existe en sitio web, no requiere instalación
PRESENT_WITH_ISSUES    # Presente pero con problemas (ej: conflicto WhatsApp)
ESTIMATED              # Generado con datos estimados
FAILED                 # Generación fallida
INDETERMINATE          # Estado no determinable
NOT_DELIVERED          # No generado y no en producción
```

### Lecciones DT-1 aplicables

| # | Lección | Aplica a |
|---|---------|----------|
| L1 | DIRECTA para cambios de código localizado | P-01, P-02, P-07 |
| L2 | Safety guard WSL bloquea rm -rf | Cualquier limpieza de output |
| L3 | Verificar path de output real antes de diseñar prompt E2E | P-03, P-04, P-05, P-06 |
| L4 | El MIXTO pattern funciona pero necesita path adaptation | P-03, P-04, P-05 |
| L5 | Tests de contrato previenen regresiones | Todos los fixes |

---

## 4. Archivos de salida relevantes

### Zi One (post-DT-1)

```
output/v4_complete/
├── v4_complete_report.json
├── 01_DIAGNOSTICO_Y_OPORTUNIDAD_20260724_141546.md
├── 02_PROPUESTA_COMERCIAL_20260724_141600.md
├── deliveries/
│   ├── zione_20260724.zip          ← ZIP de entrega
│   └── README_DELIVERY.md
├── v4_audit/
│   └── proposal_asset_matrix.json  ← P-06: existe aquí pero NO se empaqueta
└── zione/
    ├── v4_audit/
    │   ├── asset_generation_report.json
    │   ├── audit_report_20260724_141541.json
    │   ├── coherence_validation.json           (pre-gen, score 0.84)
    │   ├── coherence_validation_post_gen.json  (post-gen, score 0.82)
    │   ├── delivery_quality_report.json        (usa pre-gen 0.84 ← P-03, G9 dead ← P-05)
    │   ├── financial_scenarios_20260724_141541.json
    │   ├── gate_report_20260724_141600.json
    │   ├── geo_flow_result.json
    │   ├── human_checklist.md
    │   ├── ia_readiness_report.json
    │   └── pain_ledger.json
    ├── geo_enriched/
    ├── hotel_schema/
    ├── whatsapp_conflict_guide/
    ├── monthly_report/
    ├── llms_txt/
    ├── open_graph/
    ├── optimization_guide/
    ├── faq_page/
    ├── analytics_setup_guide/
    ├── indirect_traffic_optimization/
    ├── og_tags_guide/
    └── research_0dfa6e9b3f64_Zione.json
```

### Metricas clave (idénticas entre pre y post DT-1)

| Métrica | Valor |
|---------|-------|
| coherence_score | 0.8424242424242424 |
| coherence_validation (pre-gen) | 0.84, is_coherent=False |
| coherence_validation (post-gen) | 0.82 |
| delivery_quality_report | 4/4 gates PASS (⚠️ G9 es dead gate → P-05) |
| asset_generation | 11 total, 10 generated, 1 skipped, 0 failed |
| avg_confidence | 0.88 |
| ZIP file count | 46 |
| ZIP total size | 131,697 bytes |

---

## 5. Criterios de éxito para el plan DT-2

| # | Criterio | Verificable en |
|---|----------|---------------|
| S-1 | README Overview muestra conteo de archivos y tamaño que coinciden con MANIFEST.json | ZIP → README_DELIVERY.md |
| S-2 | Ningún asset aparece en sección state-based Y "Advisory Guides" simultáneamente | ZIP → README_DELIVERY.md |
| S-3 | delivery_quality_report refleja score post-generación (o ambos scores) | output/v4_complete/zione/v4_audit/ |
| S-4 | proposal_asset_matrix usa DeliveryContext como fuente de verdad (o alinea semántica con alignment gate) | output/v4_complete/v4_audit/ |
| S-5 | Tests existentes (28) siguen pasando | test_delivery_contract.py |
| S-6 | Tests nuevos cubren los 7 fixes (P-01 a P-07) | test_delivery_contract.py |
| S-7 | ZIP de Zi One post-fix cumple S-1 y S-2 | zione_YYYYMMDD.zip |
| S-8 | G9 proposal_asset_alignment se evalúa realmente o se elimina del reporte | delivery_quality_report.json |
| S-9 | proposal_asset_matrix.json empaquetado en el ZIP | zione_YYYYMMDD.zip |

---

## 6. Restricciones

1. **No tocar el pipeline de producción**: SitePresenceChecker, CoherenceValidator,
   scenario_calculator.py están fuera de alcance.
2. **No romper backward compatibility**: `create_readme()` debe seguir funcionando
   sin DeliveryContext (legacy mode).
3. **Safety guard WSL**: No usar `rm -rf` directamente. Ver skill
   `wsl-safety-guard-bypass` para workarounds.
4. **Una fase = una sesión**: Cada fase se ejecuta en una sesión independiente.
5. **Output path**: v4complete escribe a `output/v4_complete/` (flat), no a
   `output/<hotel_id>/v4_complete/`.
6. **pytest no disponible en .venv-wsl**: El venv tiene python 3.11 pero no pytest.
   Usar `.venv/Scripts/python.exe` (Windows) o instalar pytest antes de correr tests.

---

## 7. Análisis de causa raíz (consolidado)

Todas las causas raíz convergen en 3 categorías:

### RAÍZ-1: Orden de construcción (P-01)

El README se renderiza ANTES de que el manifest exista (Pass 1),
mientras el manifest se construye DESPUÉS (Pass 2-3). El README
consume `delivery_context.files` (pre-meta, 44 archivos) mientras
el manifest refleja el estado final (46 archivos). La información
correcta existe pero en el orden equivocado.

Punto de pérdida: `delivery_packager.py` L175-176 (Pass 1: README)
vs L178-179 (Pass 2: manifest).

### RAÍZ-2: Filtros sin contrato de exclusión mutua (P-02, P-06)

Cada sección del README tiene su propio filtro independiente:
  - `delivered_assets`: `state == DELIVERED`
  - `estimated_assets`: `state == ESTIMATED`
  - `advisory_assets`: `is_advisory == True`

Ninguno excluye lo que el otro captura. No hay un modelo canónico
de "este asset va en ESTA sección y solo en esta." El diseño asume
que las categorías son disjuntas, pero `is_advisory` corta
horizontalmente los estados (DELIVERED, ESTIMATED).

Punto de pérdida: `delivery_context.py` L407-425. Los properties
son independientes sin contrato de partición.

### RAÍZ-3: Gates declarados pero no implementados (P-03, P-04, P-05)

El `delivery_quality_report` tiene 4 gates (G6, G7, G8, G9):
  - G6 (coherence): IMPLEMENTADO — lee `coherence_validation.json`
  - G7 (coverage): IMPLEMENTADO — lee `asset_generation_report.json`
  - G8 (specificity): IMPLEMENTADO — lee `asset_generation_report.json`
  - G9 (proposal_asset_alignment): **NO IMPLEMENTADO** — default `True`

G9 está declarado en el dataclass, en el reporte JSON, y en la
lógica de bloqueo (L205), pero nunca se evalúa. Además, G6 lee
el score PRE-generación cuando existe uno POST-generación.

Punto de pérdida: `delivery_quality_report.py` L122 (lee pre-gen)
y L238 (default para G9). El módulo tiene la estructura de un
sistema de 4 gates pero solo implementa 3.
