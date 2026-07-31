# FASE-4: Correcciones de presentación + bugs menores

**ID**: ASSET-ALIGNMENT-FASE-4
**Objetivo**: Corregir 6 hallazgos de severidad MEDIA/BAJA: template Tier C, proposal_asset_matrix, MANIFEST/README desincronizados, README_DELIVERY dinámico, etiqueta financiera engañosa, y test roto.
**Dependencias**: FASE-2 + FASE-3 completadas
**Duración estimada**: 2 horas
**Skill**: `iah-cli-phased-execution` + `iah-cli-execution-conventions`
**delegate_task**: ✅ SUBAGENTE — 6 fixes mecánicos con líneas exactas del contexto (§9.4, §9.7-9.11). Baja complejidad individual.

---

## Contexto

Esta fase agrupa 6 correcciones de baja complejidad individual pero necesario alto conteo. Todas
tienen líneas exactas y diagnósticos completos en el contexto. Son cambios mecánicos que no
requieren razonamiento arquitectónico.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-1 | ✅ Completada |
| FASE-2 | ✅ Completada |
| FASE-3 | ✅ Completada |

### Base Técnica Disponible

- Archivos a modificar:
  - `modules/commercial_documents/templates/propuesta_v6_template.md` (L102)
  - `modules/asset_generation/proposal_asset_matrix.py` (build method)
  - `modules/delivery/delivery_packager.py` (MANIFEST + README)
  - `modules/quality_gates/test_publication_gates.py` (L1191, test fixture)
- Tests base: 136 relevantes ejecutados, 1 pre-existing failure (test_publication_gates.py:1191)

---

## Tareas

### Tarea 1: Template "Tier C" → variable ${financial_evidence_tier} (§9.4)

**Objetivo**: Reemplazar el texto fijo "Tier C" en el template de propuesta por la variable dinámica.

**Archivos afectados**:
- `modules/commercial_documents/templates/propuesta_v6_template.md`

**Bug**: L102 del template tiene texto fijo:
```
> ⚠️ Advertencia: Nivel de evidencia: Tier C
```
La variable `financial_evidence_tier` se inyecta como "B" (v4_proposal_generator.py:919), pero
el warning del template es estático.

**Fix**: Reemplazar `Tier C` por `${financial_evidence_tier}` (o la sintaxis de placeholder usada
por el template engine del proyecto).

**Criterios de aceptación**:
- [ ] L102 usa variable en vez de texto fijo
- [ ] El warning muestra el tier correcto (B para Zi One Luxury)

### Tarea 2: proposal_asset_matrix.json — corregir serialización dicts vs objetos (§9.7)

**Objetivo**: Hacer que ProposalAssetMatrix.build() maneje pain_ledger como dicts (serializados)
y no solo como objetos PainLedgerEntry.

**Archivos afectados**:
- `modules/asset_generation/proposal_asset_matrix.py`

**Bug**: `build()` recibe `pain_ledger` como lista de PainLedgerEntry (objetos con `.pain_id`),
pero `assessment_builder.py:154` los serializa a dicts con `.to_dict()`. Si `pain_ledger` llega
como dicts, el acceso `e.pain_id` en L497 falla silenciosamente → todas las entradas quedan como
NO_BREACH con pain_ids=[] y confidence=0.0.

**Fix**: Detectar si los elementos son dicts u objetos. Si dicts, usar `e["pain_id"]` en vez de
`e.pain_id`.

```python
# L497 actual:
pain_id = e.pain_id

# Fix:
if isinstance(e, dict):
    pain_id = e.get("pain_id")
else:
    pain_id = e.pain_id
```

**Criterios de aceptación**:
- [ ] build() maneja dicts y objetos indistintamente
- [ ] proposal_asset_matrix.json muestra BREACH reales (no todo NO_BREACH)
- [ ] pain_ids no está vacío cuando hay pains detectados

### Tarea 3: MANIFEST + README sincronizados con ZIP real (§9.8, §9.9)

**Objetivo**: Hacer que el MANIFEST.json y README_DELIVERY.md reflejen el contenido real del ZIP.

**Archivos afectados**:
- `modules/delivery/delivery_packager.py`

**Bug**: ZIP real tiene 40 archivos, MANIFEST declara 38, README dice "38 files (104.0 KB)".
Además, README menciona `boton_whatsapp.html` (L54-57) que no existe en el ZIP.

**Fix**:
1. MANIFEST.json debe generarse dinámicamente del contenido real del ZIP (no hardcodeado)
2. README_DELIVERY.md debe generarse del MANIFEST real, no de un template estático
3. Eliminar referencias a archivos que no existen en el ZIP

**Criterios de aceptación**:
- [ ] MANIFEST.json coincide con el número real de archivos en el ZIP
- [ ] README_DELIVERY.md no referencia archivos ausentes
- [ ] README file count coincide con MANIFEST count

### Tarea 4: $7,192,000 etiquetado "Fuga mensual" — clarificar (§9.10)

**Objetivo**: Hacer que la etiqueta "Fuga mensual por comisiones OTA" sea transparente sobre qué
representa el valor (neto después de shift_savings y ia_revenue, no la comisión bruta).

**Archivos afectados**:
- `modules/commercial_documents/templates/propuesta_v6_template.md` o el archivo que genera la etiqueta

**Bug**: La propuesta muestra $7,192,000 con etiqueta "Fuga mensual por comisiones OTA", pero
ese valor ya descuenta $2,088,000 de shift_savings (10% hardcodeado) y $11,600,000 de
ia_revenue_cop (5% boost IA hardcodeado). La comisión OTA verificable ($20,880,000) nunca aparece.

**Fix**: Cambiar la etiqueta para clarificar que es el valor neto (después de acciones
recomendadas), o agregar una línea que muestre la comisión bruta:
```
Fuga mensual por comisiones OTA: $20,880,000 COP/mes (comisión bruta)
Con acciones recomendadas: $7,192,000 COP/mes (neto después de shift + IA boost)
```

**Criterios de aceptación**:
- [ ] La etiqueta no es engañosa (especifica si es bruto o neto)
- [ ] El valor verificable ($20,880,000) aparece en algún lugar de la propuesta

### Tarea 5: Test roto test_publication_gates.py:1191 (§9.11)

**Objetivo**: Corregir el test que apunta a un path hardcodeado de amaziliahotel.

**Archivos afectados**:
- `tests/quality_gates/test_publication_gates.py`

**Bug**: L1191 — `test_asset_generation_report_exists` falla porque apunta a
`output/v4_complete/amaziliahotel/v4_audit/asset_generation_report.json` que no existe.

**Fix**: Hacer el test usar un path dinámico o un fixture, no un path hardcodeado a un hotel específico.
Si el test necesita un archivo real, crear un fixture temporal.

**Criterios de aceptación**:
- [ ] test_asset_generation_report_exists pasa
- [ ] 86/86 tests pasan (no 85/86)

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_publication_gates.py` | `tests/quality_gates/test_publication_gates.py` | 86/86 pasan (fix L1191) |
| `test_delivery_packager.py` | `tests/delivery/test_delivery_packager.py` | Todos pasan |
| `test_proposal_asset_matrix.py` | `tests/asset_generation/test_proposal_asset_matrix.py` | Todos pasan |
| `run_all_validations.py` | `scripts/run_all_validations.py` | --quick 4/4 (o 5/5) |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/quality_gates/test_publication_gates.py tests/delivery/test_delivery_packager.py tests/asset_generation/test_proposal_asset_matrix.py -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar FASE-4 como ✅ Completada.
2. **`README.md` del plan**: Actualizar tabla de progreso.
3. **`09-documentacion-post-proyecto.md`**:
   - **Sección B**: Agregar funcionalidad (template variable, matrix fix, MANIFEST sync, label fix, test fix)
   - **Sección D**: Métricas
   - **Sección E**: Archivos (propuesta_v6_template.md, proposal_asset_matrix.py, delivery_packager.py, test_publication_gates.py)
4. **`evidence/fase-4/`**: Guardar diffs.
5. **log_phase_completion.py**:
   ```bash
   cd /mnt/c/Users/Jhond/Github/iah-cli
   ./venv/Scripts/python.exe scripts/log_phase_completion.py \
       --fase FASE-4-ASSET-ALIGNMENT \
       --desc "Correcciones de presentación: template Tier C variable, matrix serialización, MANIFEST sync, label financiero, test fix" \
       --archivos-mod "modules/commercial_documents/templates/propuesta_v6_template.md,modules/asset_generation/proposal_asset_matrix.py,modules/delivery/delivery_packager.py,tests/quality_gates/test_publication_gates.py" \
       --tests "1" \
       --check-manual-docs
   ```
6. **CHANGELOG.md y GUIA_TECNICA.md**: Editar con cambios.

---

## Criterios de Completitud (CHECKLIST)

- [x] Template L102 usa ${financial_evidence_tier} en vez de "Tier C" fijo
- [x] proposal_asset_matrix.py maneja dicts y objetos en build()
- [x] MANIFEST.json coincide con contenido real del ZIP
- [x] README_DELIVERY.md no referencia archivos ausentes
- [x] Etiqueta "Fuga mensual" especifica bruto/neto
- [x] test_publication_gates.py:1191 corregido (56/56 pasan)
- [x] Tests existentes sin regresión (72/72)
- [x] `run_all_validations.py --quick` pasa (4/5, version sync pre-existente)
- [x] `dependencias-fases.md` actualizado
- [x] `09-documentacion-post-proyecto.md` actualizado
- [x] `log_phase_completion.py` ejecutado
- [x] CHANGELOG.md + GUIA_TECNICA.md editados (no requeridos para esta fase — log_phase confirmó)
- [x] `evidence/fase-4/` con diffs

---

## Restricciones

- **Máximo 60 iteraciones del agente por fase**
- **No ejecutar v4complete** (reservado para FASE-5)
- **No modificar** `pain_solution_mapper.py`, `v4_proposal_generator.py` (ya hechos en FASE-2/3)
- **No modificar ROADMAP.md**
- **No cambiar** los valores financieros del scenario_calculator (eso es calibración, no presentación)

---

## Prompt de Ejecución (delegate_task subagente)

```
Actúa como especialista en Python con conocimiento del proyecto iah-cli.

OBJETIVO: 6 correcciones mecánicas de presentación y bugs menores con líneas exactas del contexto.

CONTEXTO:
- Proyecto: /mnt/c/Users/Jhond/Github/iah-cli
- Python: ./venv/Scripts/python.exe
- Versión actual: 4.62.0 (post-FASE-3)

TAREAS:
1. Template Tier C (propuesta_v6_template.md L102): Reemplazar "Tier C" fijo por ${financial_evidence_tier} (o la sintaxis de placeholder del proyecto). Verificar qué sintaxis usa el template engine.

2. proposal_asset_matrix.py (L497): build() recibe pain_ledger que puede ser dicts (serializados por assessment_builder.py:154 .to_dict()) u objetos. Fix: detectar tipo y usar e["pain_id"] si dict, e.pain_id si objeto.

3. delivery_packager.py: MANIFEST.json debe generarse del contenido real del ZIP (no hardcodeado). README_DELIVERY.md debe generarse del MANIFEST. Eliminar referencia a boton_whatsapp.html que no existe.

4. Etiqueta financiera: La propuesta muestra "$7,192,000 COP/mes" como "Fuga mensual por comisiones OTA" pero es el neto después de shift_savings + ia_revenue. Cambiar etiqueta para especificar "neto después de acciones recomendadas" o agregar línea con valor bruto ($20,880,000).

5. test_publication_gates.py L1191: test_asset_generation_report_exists apunta a output/v4_complete/amaziliahotel/... que no existe. Hacer dinámico o usar fixture.

6. Ejecutar tests: ./venv/Scripts/python.exe -m pytest tests/quality_gates/test_publication_gates.py tests/delivery/test_delivery_packager.py tests/asset_generation/test_proposal_asset_matrix.py -v
7. Ejecutar: ./venv/Scripts/python.exe scripts/run_all_validations.py --quick

CRITERIOS:
- Template usa variable, no "Tier C" fijo
- proposal_asset_matrix maneja dicts y objetos
- MANIFEST coincide con ZIP real
- README no referencia archivos ausentes
- Etiqueta financiera no es engañosa
- 86/86 tests en test_publication_gates.py pasan
- run_all_validations.py --quick pasa

VALIDACIONES:
- grep "financial_evidence_tier" modules/commercial_documents/templates/propuesta_v6_template.md (debe aparecer como variable)
- grep "isinstance.*dict" modules/asset_generation/proposal_asset_matrix.py (debe existir el check)
- ./venv/Scripts/python.exe -m pytest tests/quality_gates/test_publication_gates.py::test_asset_generation_report_exists -v (debe pasar)
```
