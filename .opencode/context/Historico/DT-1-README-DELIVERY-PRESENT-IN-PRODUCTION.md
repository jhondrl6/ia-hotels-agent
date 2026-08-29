# Contexto validado: Delivery Contract — README, Manifest y present_in_production

> **ID**: DT-1-README-DELIVERY-PRESENT-IN-PRODUCTION
> **Versión del contexto**: v2.0 — validación exhaustiva contra código vivo y artefactos reales
> **Fecha de actualización**: 2026-07-23
> **Origen**: ASSET-ALIGNMENT-ZIONE-2026-07-23, FASE-5, hallazgo 9.9 (residual)
> **Repositorio validado**: `/mnt/c/Users/Jhond/Github/iah-cli`
> **Commit validado**: `df75222f2b1ddce9e0761afbbea388831ea88a02`
> **Severidad revisada**: 🔴 ALTA para confiabilidad de entrega; el síntoma original era MEDIO
> **Estado**: Validado contra código, ZIP, reportes y sitio vivo; pendiente de intervención en nueva sesión
> **Hotel de prueba**: Zi One Luxury — `https://zione.co/`
> **Regla de ejecución**: Este documento NO autoriza implementación en la sesión de validación. Las macrofases son sugerencias para una sesión posterior de planificación.

---

## 0. Veredicto ejecutivo

El hallazgo central de DT-1 queda **CONFIRMADO**.

El ZIP vigente de Zi One Luxury:

`output/ZiOne/v4_complete/deliveries/zione_20260723.zip`

contiene 46 entradas y no contiene `boton_whatsapp.html`. Sin embargo, el `README_DELIVERY.md` incluido dentro del ZIP:

- lista `boton_whatsapp.html` en `Package Structure`;
- incluye instrucciones para instalarlo;
- lo incluye en el timeline;
- lo incluye en el checklist.

El cliente puede buscar un archivo que no fue entregado porque el sistema detectó que la funcionalidad ya existe en producción.

La causa raíz primaria también queda **CONFIRMADA**:

> El README se genera desde una template narrativa estática, no desde la lista final de archivos del ZIP ni desde un contrato canónico de estados de assets.

La intervención propuesta en la versión original del contexto —hacer la template condicional y leer `asset_generation_report.json`— es correcta como dirección inicial, pero **insuficiente como solución de causa raíz**.

La solución futura debe ampliarse a:

> **Delivery Contract and Cross-Artifact Consistency**: unificar estado de assets, archivos físicos, manifest, README, gates y evidencia; generar la estructura del README desde los destinos reales del ZIP; y validar automáticamente que README, MANIFEST y ZIP describan exactamente el mismo paquete.

La severidad se eleva de MEDIO a ALTA porque el problema no se limita a una línea incorrecta de WhatsApp. La validación encontró además:

1. nombres de archivos hardcodeados en el README que no coinciden con los archivos reales;
2. rutas con `\\` en el manifest frente a `/` en el ZIP;
3. tamaños `0` en el manifest para `MANIFEST.json` y `README_DELIVERY.md` aunque sí existen dentro del ZIP;
4. divergencia semántica entre `asset_generation_report`, `gate_report`, `coherence_validation` y metadata individual;
5. ausencia de tests de contrato que comparen README ↔ manifest ↔ ZIP;
6. diferencia entre “presente en producción”, “correcto” y “requiere revisión”.

No se implementó código, template, test ni plan de intervención como resultado de esta actualización.

---

## 1. Alcance y evidencia utilizada

### 1.1 Código y documentación inspeccionados

- `templates/delivery_readme_template.md`
- `modules/delivery/delivery_packager.py`
- `modules/delivery/delivery_context.py`
- `modules/asset_generation/proposal_asset_alignment.py`
- `modules/asset_generation/v4_asset_orchestrator.py`
- `modules/quality_gates/publication_gates.py`
- `modules/quality_gates/delivery_quality_report.py`
- `modules/assessment_builder.py`
- `main.py`
- `tests/delivery/test_delivery_packager.py`
- `ROADMAP.md`
- `docs/CONTRIBUTING.md`

### 1.2 Artefactos reales de Zi One inspeccionados

- `output/ZiOne/v4_complete/zione/v4_audit/asset_generation_report.json`
- `output/ZiOne/v4_complete/zione/v4_audit/gate_report_20260723_201337.json`
- `output/ZiOne/v4_complete/zione/v4_audit/coherence_validation.json`
- `output/ZiOne/v4_complete/zione/v4_audit/coherence_validation_post_gen.json`
- `output/ZiOne/v4_complete/zione/v4_audit/delivery_quality_report.json`
- `output/ZiOne/v4_complete/zione/v4_audit/pain_ledger.json`
- `output/ZiOne/v4_complete/zione/v4_audit/audit_report_20260723_201321.json`
- `output/ZiOne/v4_complete/zione/whatsapp_conflict_guide/guia_conflicto_whatsapp_20260723_201326.md`
- `output/ZiOne/v4_complete/zione/whatsapp_conflict_guide/guia_conflicto_whatsapp_20260723_201326_metadata.json`
- `evidence/fase-5/asset_generation_report.json`
- `evidence/fase-5/gate_report_20260723_201337.json`
- `evidence/fase-5/delivery_quality_report.json`
- `evidence/fase-5/proposal_asset_matrix.json`
- `output/ZiOne/v4_complete/deliveries/zione_20260723.zip`
- `output/ZiOne/v4_complete/deliveries/zi_one_luxury_20260723.zip`
- `output/ZiOne/v4_complete/deliveries/README_DELIVERY.md`

### 1.3 Validaciones ejecutadas

Test específico del packager:

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
venv/Scripts/python.exe -m pytest tests/delivery/test_delivery_packager.py -q
```

Resultado real:

```text
10 passed, 8 warnings
```

La prueba pasa, pero no cubre el contrato que está roto. La suite actual no valida `present_in_production`, el contenido del README contra el ZIP, las rutas del manifest ni los tamaños finales.

Para inspeccionar los ZIP se utilizó `zipfile` de Python porque `unzip` no está instalado en el WSL actual.

### 1.4 Sitio vivo validado

Se navegó al sitio real:

`https://zione.co/`

El navegador redirigió a:

`https://zione.co/en/zione/`

El DOM vivo confirmó enlaces WhatsApp, entre ellos:

- `https://wa.me/573116079036`
- `https://wa.me/573042476691`
- contacto Pereira: `+57 311 607 9036`
- contacto Cartagena: `+57 304 247 6691`

También se detectaron elementos con clase social WhatsApp.

La presencia física del botón/links de WhatsApp en producción queda confirmada independientemente de los reportes internos.

---

## 2. Hallazgo original validado

### 2.1 ZIP real

El ZIP `zione_20260723.zip` tiene:

- 46 entradas;
- `MANIFEST.json` con `total_files: 46`;
- ningún archivo llamado `boton_whatsapp.html`.

El `asset_generation_report.json` de la misma ejecución declara:

```json
{
  "summary": {
    "total_assets": 11,
    "generated": 10,
    "failed": 0,
    "skipped": 1,
    "can_use": 10,
    "delivery_ready_percentage": 100.0,
    "site_verification_applied": true
  },
  "skipped_assets": [
    {
      "asset_type": "whatsapp_button",
      "reason": "Asset ya implementado en sitio de producción",
      "presence_status": "exists",
      "site_verified": true,
      "pain_ids_affected": ["no_whatsapp_visible"]
    }
  ]
}
```

### 2.2 README real dentro del ZIP

El README empaquetado contiene:

```text
│   ├── boton_whatsapp.html     # WhatsApp button code
```

```text
#### WhatsApp Button (`boton_whatsapp.html`)
1. Copy the HTML code
2. Add to your CMS footer or via custom HTML widget
3. Test on mobile devices
```

```text
- [ ] Add WhatsApp button to footer
```

```text
- [ ] WhatsApp button visible on all pages
```

La evidencia original queda confirmada literalmente.

### 2.3 Segundo asset `present_in_production`

El mismo ZIP/report identifica también:

- `org_schema` — `Schema Organization` — `presence_status: exists`.

Por tanto, la observación del contexto de que el problema se replicará para otros assets presentes en producción también queda confirmada.

---

## 3. Matriz de validación de afirmaciones

| Afirmación del contexto original | Resultado contra código/artefactos |
|---|---|
| El ZIP tiene 46 archivos | ✅ Confirmada |
| `boton_whatsapp.html` no está en el ZIP | ✅ Confirmada |
| `whatsapp_button` está `present_in_production` | ✅ Confirmada en reportes y sitio vivo |
| `org_schema` también está presente | ✅ Confirmada en `gate_report` |
| El README lista `boton_whatsapp.html` | ✅ Confirmada |
| El README da instrucciones para instalarlo | ✅ Confirmada |
| Timeline y checklist también lo mencionan | ✅ Confirmada |
| La template es estática | ✅ Confirmada |
| `create_readme()` reemplaza cuatro placeholders | ✅ Confirmada |
| El caller no entrega `asset_generation_report` al packager | ✅ Confirmada |
| Leer solo `asset_generation_report.json` resolvería todo | ❌ Refutada como solución completa |
| “Presente en producción” implica “no requiere ninguna acción” | ❌ Refutada para Zi One; existe conflicto de números |
| El problema se limita a WhatsApp y `org_schema` | ❌ Refutada; afecta nombres, estructura, rutas y tamaños |
| La severidad original MEDIO es suficiente | ❌ Subestimada; la severidad sistémica es ALTA |
| Los tests existentes cubren este caso | ❌ Refutada |

---

## 4. Causa raíz validada

### 4.1 Causa raíz primaria: README narrativo y estático

Archivo:

`templates/delivery_readme_template.md`

La template hardcodea:

- estructura del paquete;
- nombres de assets;
- instrucciones de implementación;
- timeline;
- checklist.

Los únicos placeholders encontrados son:

- `{{HOTEL_ID}}`
- `{{DATE}}`
- `{{TOTAL_FILES}}`
- `{{TOTAL_SIZE}}`

No existen placeholders o bloques condicionales para:

- assets entregados;
- assets omitidos;
- assets presentes en producción;
- assets con incidencias;
- archivos reales del manifest;
- instrucciones por estado.

### 4.2 Causa raíz en `create_readme()`

Archivo:

`modules/delivery/delivery_packager.py`, método `create_readme()` alrededor de las líneas 274-302.

La implementación actual:

1. carga la template;
2. sustituye `HOTEL_ID`;
3. sustituye `DATE`;
4. sustituye `TOTAL_FILES`;
5. sustituye `TOTAL_SIZE`;
6. escribe el README.

No recibe ni consulta:

- `asset_generation_report.json`;
- `gate_report.json`;
- `source_dir`;
- `hotel_dir`;
- lista final de destinos del ZIP;
- estados canónicos de assets;
- incidencias de presencia en producción.

### 4.3 Causa raíz de arquitectura

El pipeline tiene componentes dinámicos que generan el ZIP, pero el README funciona como una pieza independiente y estática.

No existe un contrato común entre:

```text
asset generation state
        ↓
proposal/gate interpretation
        ↓
manifest
        ↓
README
        ↓
ZIP final
```

Cada capa puede tener una interpretación diferente de:

- generado;
- omitido;
- existente;
- cubierto;
- correcto;
- instalable;
- requiere revisión.

La desincronización no es accidental: es una consecuencia estructural de no tener una fuente de verdad única.

---

## 5. Hallazgos ampliados contra código y artefactos

### F-01 — README lista archivos inexistentes

**Severidad**: ALTA

Confirmado para `boton_whatsapp.html`.

La solución futura debe evitar que cualquier path textual del README exista solo en la template. Debe derivarse de la lista final de archivos del ZIP.

### F-02 — README lista nombres conceptuales que tampoco coinciden con archivos reales

**Severidad**: ALTA

La template contiene:

- `hotel-schema.json`
- `geo_playbook.md`
- `faq_page.md`
- `boton_whatsapp.html`

En el ZIP real de Zi One aparecen, entre otros:

- `ASSETS/hotel_schema/hotel_schema_20260723_201326.json`
- `ASSETS/geo_enriched/geo_fix_kit.md`
- `ASSETS/geo_enriched/hotel_schema_rich.json`
- `ASSETS/faq_page/ESTIMATED_faqs_20260723_201326.json`

No aparecen exactamente:

- `ASSETS/hotel-schema.json`
- `ASSETS/geo_playbook.md`
- `ASSETS/faq_page.md`

Por tanto, el problema real es más amplio que WhatsApp:

> El README describe una estructura conceptual/histórica, no el contenido físico del ZIP.

### F-03 — No se diferencian assets entregables, guías, estimaciones y evidencia

**Severidad**: ALTA

El reporte contiene metadata útil:

- `generated_assets`;
- `skipped_assets`;
- `failed_assets`;
- `preflight_status`;
- `confidence_score`;
- `can_use`;
- `delivery_filename`;
- `pain_ids_resolved`.

El README no utiliza esa información.

Consecuencias:

- un asset `ESTIMATED_` puede parecer final;
- un asset con `can_use: false` puede parecer instalable;
- un asset de conflicto puede parecer código de instalación;
- un asset de auditoría puede aparecer mezclado con assets para el cliente;
- un asset presente en producción puede aparecer como pendiente de implementación.

Ejemplo:

`whatsapp_conflict_guide` sí está entregado, pero no es un botón HTML. Es una guía para resolver un conflicto de números.

### F-04 — “Presente en producción” no equivale a “correcto”

**Severidad**: ALTA

El sitio confirma presencia de WhatsApp, pero el propio pipeline detecta conflicto entre números.

`audit_report_20260723_201321.json` registra:

- número web/schema terminado en `4544`;
- número GBP `311 6079036`;
- conflicto entre fuentes;
- `requires_manual_review: true`;
- `can_use: false` para la validación conflictiva.

El sitio vivo muestra múltiples números para Pereira y Cartagena.

Por tanto, la frase propuesta originalmente:

```text
✅ Ya implementado en su sitio — no requiere acción
```

es incorrecta para este caso.

La semántica mínima debe distinguir:

- `PRESENT_VERIFIED`: existe y fue verificado;
- `PRESENT_WITH_ISSUES`: existe, pero tiene conflicto o calidad insuficiente;
- `PRESENT_AND_COVERED`: existe y cubre el servicio sin acción adicional;
- `REQUIRES_REVIEW`: existe, pero requiere decisión humana;
- `DELIVERED`: archivo generado y entregado;
- `FAILED`: generación fallida;
- `INDETERMINATE`: no se pudo verificar.

Para Zi One, WhatsApp debe aparecer como:

> Existe en producción; no instale otro botón; revise la guía de conflicto antes de modificar el número.

### F-05 — Dos o más fuentes interpretan de manera diferente `exists`

**Severidad**: ALTA

El pipeline utiliza varias capas relacionadas:

1. `SitePresenceChecker` en `main.py` antes de generar la propuesta;
2. `asset_result.skipped_assets`;
3. `AssessmentBuilder.skipped_assets`;
4. construcción artificial de `site_presence_report` en `publication_gates.py`;
5. `verify_proposal_asset_alignment()`;
6. `asset_generation_report.json`;
7. `gate_report.json`;
8. `coherence_validation*.json`;
9. metadata individual de assets.

Los estados no son idénticos:

- `exists`;
- `present_in_production`;
- `skipped_existing`;
- `exists_with_issues`;
- `redundant`;
- `verification_failed`;
- `indeterminate`.

Leer únicamente `asset_generation_report.json` puede resolver el caso concreto, pero deja intacta la falta de contrato entre las capas.

### F-06 — Contradicción entre presencia en producción y coherencia post-generación

**Severidad**: ALTA

Para la misma ejecución de Zi One:

`asset_generation_report.json`:

- `whatsapp_button` skipped;
- `presence_status: exists`;
- `site_verified: true`.

`gate_report_20260723_201337.json`:

- `Botón de WhatsApp` presente en producción;
- `Schema Organization` presente en producción;
- gate de alignment pasa.

`coherence_validation_post_gen.json`:

- `promised_assets_exist`: `false`;
- mensaje: `Assets no implementados: whatsapp_button`;
- error adicional de confianza insuficiente para WhatsApp.

Esto prueba que diferentes validadores responden preguntas diferentes o tienen fuentes de verdad divergentes.

Antes de implementar el README dinámico, el plan debe decidir explícitamente qué significa “covered” para delivery:

```text
covered = archivo entregado OR funcionalidad verificada en producción
```

Pero debe conservarse el detalle de si:

- requiere instalación;
- requiere revisión;
- tiene incidencias;
- solo fue detectado con confianza parcial.

### F-07 — Conteos ambiguos en `gate_report`

**Severidad**: MEDIA-ALTA

El gate report declara:

```text
All 8 promised services have assets (8/8 aligned, 2 already in production)
```

Pero `details` contiene:

- `total_services: 6`;
- `aligned_count: 6`;
- `present_in_production`: 2.

El resultado efectivo es 8, pero `total_services` excluye los presentes en producción.

La estructura necesita campos no ambiguos:

- `promised_services_total`;
- `generated_services_total`;
- `present_in_production_total`;
- `covered_services_total`;
- `missing_services_total`;
- `indeterminate_services_total`.

El README no debe inferir conteos a partir de un campo cuyo significado cambia según la capa.

### F-08 — Rutas con backslash en `MANIFEST.json`

**Severidad**: ALTA

El ZIP real usa rutas POSIX:

```text
ASSETS/analytics_setup_guide/file.md
```

El manifest contiene rutas como:

```text
ASSETS/analytics_setup_guide\\file.md
```

La causa está en `delivery_packager.py`:

```python
dest = f"ASSETS/{rel_path}"
```

Cuando `rel_path` es un `Path` de Windows, `str(rel_path)` conserva separadores `\\`.

Resultado:

- el manifest y el ZIP contienen nombres literalmente distintos;
- consumidores Linux/macOS pueden no localizar los archivos del manifest;
- el README no puede usar el manifest de forma portable sin normalizarlo.

La solución debe utilizar rutas POSIX para el interior del ZIP, por ejemplo mediante `as_posix()` o `PurePosixPath`.

Debe existir una validación que falle si una entrada interna contiene `\\`.

### F-09 — Tamaños incorrectos para metaarchivos del paquete

**Severidad**: ALTA

El flujo actual crea entradas del manifest para `MANIFEST.json` y `README_DELIVERY.md` antes de materializarlos.

Por eso `create_manifest()` registra `size_bytes: 0` si el archivo aún no existe.

En el ZIP real:

- tamaño registrado para `MANIFEST.json`: `0`;
- tamaño real: `6433` bytes;
- tamaño registrado para `README_DELIVERY.md`: `0`;
- tamaño real: `3285` bytes.

Totales observados:

- `MANIFEST.json.total_size_bytes`: `119957`;
- suma real de bytes descomprimidos: `129675`;
- diferencia: `9718` bytes.

La entrega contiene los archivos, pero el propio inventario es factual y técnicamente incorrecto.

La solución debe incluir una pasada final de cierre:

```text
manifest entry set == ZIP entry set
manifest size == ZIP uncompressed size
manifest total == suma de tamaños reales
```

Si el README muestra el tamaño total y ese valor depende del tamaño final del propio README, debe resolverse la dependencia circular con dos pasadas o retirarse ese campo del contenido visible.

### F-10 — El README usa un nombre de ZIP distinto al real

**Severidad**: MEDIA

La template reconstruye:

```text
{{HOTEL_ID}}_{{DATE}}.zip
```

y renderiza:

```text
zione_2026-07-23.zip
```

El archivo real se llama:

```text
zione_20260723.zip
```

La fecha del nombre de archivo usa `%Y%m%d`, mientras que el README usa `%Y-%m-%d`.

La solución debe calcular el filename una única vez y pasarlo como dato `PACKAGE_FILENAME` al README.

### F-11 — Inconsistencia metadata individual vs reporte de generación

**Severidad**: ALTA

Para:

`output/ZiOne/v4_complete/zione/whatsapp_conflict_guide/guia_conflicto_whatsapp_20260723_201326_metadata.json`

la metadata declara:

- `preflight_status: WARNING`;
- `confidence_score: 0.8`;
- `can_use: false`;
- disclaimer de verificación manual.

Pero `asset_generation_report.json` para el mismo asset declara:

- `preflight_status: WARNING`;
- `confidence_score: 0.8`;
- `can_use: true`.

La inconsistencia demuestra que el delivery README no puede confiar solamente en una capa si las capas calculan `can_use` de forma diferente.

La futura intervención debe definir cuál es la fuente canónica de `can_use` y propagarla consistentemente.

### F-12 — `delivery_quality_report` no refleja todos los problemas post-generación

**Severidad**: MEDIA-ALTA

`delivery_quality_report.json` declara:

- `status: PASS`;
- `blocking: false`;
- 4/4 gates pasados;
- coherence score `0.84`.

Pero `coherence_validation_post_gen.json` tiene score `0.82` y errores:

- `whatsapp_verified` con score `0.3`;
- `promised_assets_exist` falso para `whatsapp_button`.

El delivery quality report lee `coherence_validation.json`, mientras que la evidencia post-generación conserva otro estado.

Este hallazgo no es el bug primario del README, pero afecta la confianza en cualquier estado que el README pudiera mostrar.

### F-13 — `proposal_asset_matrix.json` no coincide con el gate de alignment

**Severidad**: MEDIA-ALTA

En `evidence/fase-5/proposal_asset_matrix.json`, los ocho servicios aparecen como:

- `status: NO_BREACH`;
- `asset_path: null`;
- `confidence: 0.0`;
- `pain_ids: []`.

En cambio, `gate_report_20260723_201337.json` declara:

- 6 servicios aligned;
- 2 presentes en producción;
- 8/8 cubiertos.

Esto indica que la evidencia de propuesta, matriz y gate no está consolidada. El README futuro no debería presentar una afirmación comercial basada en una sola de estas fuentes sin resolver primero el contrato.

### F-14 — Tests unitarios pasan, pero no existe test de contrato de entrega

**Severidad**: ALTA

`tests/delivery/test_delivery_packager.py` no contiene casos para:

- `present_in_production`;
- `skipped_assets`;
- `asset_generation_report`;
- `exists_with_issues`;
- manifest ↔ ZIP;
- README ↔ ZIP;
- rutas POSIX;
- tamaños reales del manifest;
- filename real del ZIP;
- archivos hardcodeados inexistentes.

Los tests actuales prueban creación superficial del ZIP, README y manifest, pero permiten pasar aunque el README describa archivos inexistentes.

Debe crearse una suite de contrato cross-artifact.

---

## 6. Estado vivo del pipeline

### 6.1 Flujo actual

```text
main.py v4complete
  → V4AssetOrchestrator.generate_all()
    → output/.../{hotel_id}/v4_audit/asset_generation_report.json
  → SitePresenceChecker antes de generar la propuesta
  → AssessmentBuilder
  → Publication Gates
  → DeliveryQualityReport
  → DeliveryPackager.package()
      → _collect_files(source_dir)
      → create_manifest(all_files)
      → create_readme(deliveries_dir, hotel_id, manifest)
      → _create_zip(zip_path, all_files, source_dir)
```

### 6.2 Punto de desconexión

`DeliveryPackager.package()` llama actualmente:

```python
self.create_readme(self.deliveries_dir, hotel_id, manifest)
```

`create_readme()` no recibe:

- `source_dir`/`hotel_dir`;
- `asset_generation_report`;
- estados de presencia;
- nombre final del ZIP;
- lista final de destinos normalizados.

### 6.3 Riesgo de acoplar reglas de negocio al README

La solución no debería hacer que `create_readme()` vuelva a implementar:

- SitePresenceChecker;
- lógica de gates;
- CoherenceValidator;
- clasificación de pains;
- decisión de cobertura.

El packager debe recibir un contexto de delivery ya normalizado y limitarse a:

- renderizar;
- construir el manifest;
- crear el ZIP;
- verificar consistencia.

---

## 7. Solución recomendada enfocada en causa raíz

Esta sección reemplaza la solución parcial de la versión original. No es una implementación ni un plan final.

### 7.1 Definir un contrato canónico de estado de delivery

Crear conceptualmente una estructura común para cada servicio/asset:

```python
DeliveryAssetStatus(
    asset_type="whatsapp_button",
    service_name="Botón de WhatsApp",
    state="PRESENT_WITH_ISSUES",
    presence_status="exists_with_issues",
    delivery_path=None,
    generated=False,
    site_verified=True,
    covered=True,
    requires_action=True,
    requires_review=True,
    confidence=0.3,
    source_refs=[...],
    message="Existe en producción, pero hay conflicto de números"
)
```

El nombre exacto de la clase/enum queda para la sesión de planificación. Lo obligatorio es que exista una representación única y serializable.

Estados mínimos sugeridos:

- `DELIVERED`
- `PRESENT_IN_PRODUCTION`
- `PRESENT_WITH_ISSUES`
- `ESTIMATED`
- `FAILED`
- `INDETERMINATE`
- `NOT_DELIVERED`

Atributos independientes obligatorios:

- `covered`;
- `requires_action`;
- `requires_review`;
- `site_verified`;
- `confidence`;
- `delivery_path`;
- `source_refs`.

No debe inferirse `requires_action=False` solo porque `presence_status == exists`.

### 7.2 Hacer que el packager reciba datos normalizados

Preferir un contrato tipo:

```python
package(..., delivery_context=delivery_context)
```

El `delivery_context` debe contener:

- filename final del ZIP;
- lista final de archivos físicos y destinos POSIX;
- estados canónicos de assets;
- warnings e incidencias;
- reportes de soporte;
- servicios cubiertos;
- acciones requeridas.

El packager no debe reimplementar la lógica de negocio.

### 7.3 Generar `Package Structure` desde los destinos reales

La estructura del README debe derivarse de la misma lista usada por `_create_zip()`.

Reglas obligatorias:

- ningún path mencionado como entregable puede faltar en el ZIP;
- ningún asset presente en el ZIP debe aparecer con un nombre conceptual falso;
- las rutas internas deben ser POSIX;
- la estructura debe reflejar subdirectorios reales;
- el nombre del ZIP debe ser el filename real.

### 7.4 Generar secciones según estado

Estructura recomendada:

```text
## Included in this package
## Already present on your website
## Present but requires review
## Assets requiring implementation
## Estimated or advisory assets
## Validation and audit evidence
```

Para Zi One:

- `whatsapp_button`: `Present but requires review`;
- `org_schema`: `Already present` solo si la evidencia confirme que no requiere acción;
- `whatsapp_conflict_guide`: `Review guide`, no botón instalable.

### 7.5 Derivar instrucciones del asset real

Cada asset entregable debe declarar o resolver:

- archivo real;
- tipo de asset;
- acción esperada;
- si se instala o revisa;
- si es evidencia;
- si es estimado;
- si requiere validación humana.

No se deben conservar instrucciones genéricas para archivos que no existen.

### 7.6 Cerrar el ciclo manifest ↔ README ↔ ZIP

El pipeline debe ejecutar una verificación final equivalente a:

```text
manifest entry set == ZIP entry set
manifest paths use POSIX separators
manifest size == actual ZIP uncompressed size
manifest total == sum(actual file sizes)
README referenced paths ⊆ ZIP paths
README does not prescribe installation for non-delivered assets
README state matches canonical delivery context
```

La verificación debe ser bloqueante para el paquete si encuentra:

- un archivo del README que no existe;
- una ruta de manifest que no coincide con el ZIP;
- tamaño incorrecto;
- asset `PRESENT_WITH_ISSUES` presentado como completamente resuelto.

### 7.7 Consolidar la semántica entre gates y delivery

Debe definirse una regla explícita:

```text
covered = delivered_asset OR verified_present_in_production
```

Pero `covered` no equivale a:

- instalado;
- correcto;
- sin incidencias;
- sin acción humana.

La salida debe conservar las cuatro dimensiones separadas:

```text
covered
requires_action
requires_review
presence_quality
```

### 7.8 Corregir el ciclo de generación del manifest

Orden sugerido:

1. recolectar archivos de contenido;
2. normalizar destinos POSIX;
3. calcular filename final del ZIP;
4. generar README provisional desde el contexto;
5. construir manifest con tamaños reales de contenido y README provisional;
6. generar README final si depende del manifest;
7. recalcular manifest final;
8. crear ZIP;
9. volver a leer ZIP y manifest;
10. ejecutar validación de igualdad.

Si el README necesita mostrar el tamaño total final, resolver la dependencia circular con dos pasadas deterministas o retirar ese valor del README visible.

---

## 8. Tests y gates que deben existir después de la intervención

No implementar ahora. Estos son criterios de diseño para la futura sesión.

### 8.1 Tests de README dinámico

Casos mínimos:

1. asset generado y presente en ZIP;
2. asset skipped por presencia en producción;
3. asset presente con issues;
4. asset failed;
5. asset estimated;
6. múltiples assets presentes;
7. ausencia de `asset_generation_report`;
8. reporte inválido;
9. estados `verification_failed` e `indeterminate`;
10. instrucciones coherentes con el estado.

### 8.2 Tests de manifest

Validar:

- rutas internas exclusivamente POSIX;
- todas las entradas del manifest existen en ZIP;
- todos los archivos del ZIP aparecen en manifest;
- tamaños exactos;
- totals exactos;
- no hay entradas duplicadas;
- README y MANIFEST tienen tamaños reales;
- el filename del ZIP coincide con el README.

### 8.3 Tests de integración

Ejecutar el packager sobre un fixture completo y comprobar:

```text
README_DELIVERY.md ↔ MANIFEST.json ↔ ZIP ↔ delivery_context
```

Debe fallar si el README contiene:

- `boton_whatsapp.html` cuando el asset está omitido;
- `hotel-schema.json` cuando ese path no existe;
- instrucciones de instalación para un asset `PRESENT_WITH_ISSUES`.

### 8.4 Gate obligatorio de no regresión

El gate no debe ser opcional porque la causa raíz es recurrente y afecta directamente la confiabilidad comercial del paquete.

Debe bloquear la entrega si:

- el README referencia paths no presentes;
- el manifest no coincide con el ZIP;
- el estado de delivery contradice el estado canónico;
- el manifest contiene separadores de Windows;
- los tamaños no coinciden.

---

## 9. Macro-fases sugeridas para una futura sesión de planificación

Estas no son fases aprobadas ni archivos de plan. Son una propuesta de descomposición para la siguiente sesión.

### Macro-Fase A — Contrato y saneamiento de evidencia

Objetivo:

- definir estados canónicos;
- resolver semántica `covered` vs `requires_review`;
- decidir fuente de verdad entre reportes;
- documentar divergencias actuales.

No debería modificar todavía la template ni ejecutar una nueva entrega de producción.

### Macro-Fase B — Pipeline físico ZIP ↔ manifest

Objetivo:

- normalizar rutas POSIX;
- corregir cálculo de tamaños;
- asegurar filename único;
- añadir verificador final del ZIP.

### Macro-Fase C — README derivado del delivery context

Objetivo:

- eliminar nombres hardcodeados;
- generar estructura desde destinos reales;
- generar secciones por estado;
- diferenciar assets instalables, guías, evidencia y presentes en producción.

### Macro-Fase D — Tests de contrato y regresión

Objetivo:

- tests unitarios de estados;
- tests de integración README/manifest/ZIP;
- casos `present_in_production`, `exists_with_issues`, failed y estimated;
- gate bloqueante de no regresión.

### Macro-Fase E — Validación E2E y documentación

Objetivo:

- ejecutar una nueva entrega para Zi One;
- verificar ZIP real y README real;
- verificar otro hotel sin assets `present_in_production`;
- verificar hotel con múltiples estados;
- actualizar documentación y evidencia de fase.

La futura planificación debe aplicar la regla R3 del workflow y dividir estas macrofases si una fase concreta supera cuatro tareas o incluye más de un comando largo.

---

## 10. No objetivos de esta intervención

Esta deuda no debe utilizarse para:

- cambiar la lógica de negocio de `SitePresenceChecker` sin una decisión específica;
- declarar que todos los assets presentes en producción son correctos;
- ocultar conflictos de WhatsApp;
- convertir un asset `ESTIMATED` en entregable verificado;
- modificar la propuesta comercial de Zi One;
- rehacer el sistema completo de coherencia en la misma fase;
- implementar antes de aprobar el plan de intervención;
- corregir manualmente solo la línea de WhatsApp y declarar resuelta la causa raíz.

---

## 11. Riesgos de la futura implementación

| Riesgo | Impacto | Mitigación requerida |
|---|---|---|
| Leer solo `asset_generation_report` | Se mantienen divergencias con gates/coherence | Normalizar un delivery context único |
| Tratar `exists` como correcto | Oculta conflictos reales | Separar presencia, cobertura y revisión |
| Mantener nombres hardcodeados | Nuevos assets vuelven a desincronizar README | Derivar estructura desde destinos reales |
| Usar `str(Path)` en rutas ZIP | Manifest no portable | Forzar POSIX y validar `\\` ausente |
| Generar manifest antes de metaarchivos | Tamaños incorrectos | Pasada final de cierre y validación |
| No agregar tests de integración | Bug reaparece aunque unit tests pasen | Gate README ↔ manifest ↔ ZIP obligatorio |
| Error de reporte ausente | README ambiguo o falsamente completo | Estado `INDETERMINATE` y warning visible |
| Cambiar solo template | La metadata/gates sigue divergente | Corregir contrato de datos antes de renderizar |
| Ejecutar v4complete sobre outputs existentes | Evidencia mezclada/stale | Verificar timestamps, hotel_id y limpieza de output |

---

## 12. Evidencia factual resumida

### ZIP `zione_20260723.zip`

- Entradas: 46.
- `boton_whatsapp.html`: ausente.
- `README_DELIVERY.md`: presente.
- `MANIFEST.json`: presente.
- README contiene 4 referencias a WhatsApp/botón:
  - estructura;
  - instrucciones;
  - timeline;
  - checklist.
- El manifest usa `\\` en rutas anidadas.
- El ZIP usa `/` en rutas anidadas.
- `MANIFEST.json` registra tamaño cero para sí mismo y para README.

### `asset_generation_report.json`

- Total assets: 11.
- Generated: 10.
- Skipped: 1.
- Failed: 0.
- `whatsapp_button`: skipped por presencia en producción.
- `site_verification_applied: true`.

### `gate_report_20260723_201337.json`

- alignment: 8 servicios cubiertos;
- 6 generados/aligned;
- 2 presentes en producción;
- `whatsapp_button` presente;
- `org_schema` presente;
- `total_services` interno: 6, semánticamente ambiguo.

### `coherence_validation_post_gen.json`

- score: 0.82;
- `whatsapp_verified`: false, score 0.3;
- `promised_assets_exist`: false para `whatsapp_button`.

### Metadata de `whatsapp_conflict_guide`

- score: 0.8;
- preflight: WARNING;
- metadata `can_use: false`;
- reporte global `can_use: true`.

### Tests actuales

```text
10 passed, 8 warnings
```

El resultado no demuestra que el delivery sea consistente; solo demuestra que los tests actuales no detectan estos contratos rotos.

---

## 13. Prompt listo para la próxima sesión de planificación

Copiar en una sesión nueva, no ejecutar en esta sesión:

```text
Lee y valida primero el contexto:
/mnt/c/Users/Jhond/Github/iah-cli//.opencode/context/Historico/DT-1-README-DELIVERY-PRESENT-IN-PRODUCTION.md

Diseña un plan de intervención, sin implementar aún, para resolver la causa raíz completa de la desincronización entre README_DELIVERY.md, MANIFEST.json, ZIP, estados de assets y evidencia de producción.

Condiciones obligatorias:
1. No reducir el problema a ocultar boton_whatsapp.html.
2. Usar como alcance mínimo: contrato canónico de estados, rutas POSIX, tamaños reales del manifest, filename real del ZIP, README derivado de archivos reales y tests cross-artifact.
3. Diferenciar covered, delivered, present_in_production, present_with_issues, requires_action, requires_review e indeterminate.
4. Verificar las divergencias actuales entre asset_generation_report.json, gate_report, coherence_validation, metadata individual y proposal_asset_matrix antes de proponer cambios.
5. No tratar `present_in_production` como sinónimo de `correcto`.
6. Proponer un gate obligatorio de no regresión README ↔ MANIFEST ↔ ZIP.
7. Aplicar la regla R3 del workflow: máximo 4 tareas sin comando largo, o 3 tareas con un comando largo por fase.
8. Separar investigación, implementación, validación E2E y documentación.
9. No modificar código durante la fase de diseño.
10. Entregar los archivos completos del plan en .opencode/plans/ solo después de validar que el plan refleja este contexto v2.0.
```

---

## 14. Estado de actualización

Esta versión v2.0 sustituye la hipótesis limitada:

```text
README estático + present_in_production de WhatsApp
```

por la conclusión validada:

```text
No existe un contrato único de delivery que mantenga sincronizados:
asset state → evidencia → manifest → README → ZIP.
```

La deuda queda pendiente de intervención en una nueva sesión. No se implementó ninguna solución en esta actualización.
