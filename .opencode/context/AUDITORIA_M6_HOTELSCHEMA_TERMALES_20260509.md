# Auditoría M6: Divergencia hotel_schema_detected ↔ SitePresenceChecker

> **Contexto generado**: 2026-05-09 — Validación exhaustiva de `evidence/M6_HOTELSCHEMA_ANALYSIS.md`
> **Hotel**: Termales Santa Rosa de Cabal — http://www.termales.com.co/
> **Veredicto**: El documento original acierta en superficie pero no identifica la causa raíz real
> **Origen**: Sesión 2026-05-09 — Hermes Agent (deepseek-v4-pro)
> **Última actualización**: 2026-05-09 — Iteración 2: Auditoría cruzada completa contra código vivo

---

## Veredicto Ejecutivo

El documento `M6_HOTELSCHEMA_ANALYSIS.md` es PARCIALMENTE correcto: identifica bien que `hotel_schema_detected=false` NO es un bug del detector sino una característica real del sitio. PERO falla en identificar la causa raíz de la discrepancia entre audit y gate, **y además no detecta que LocalBusiness también causa el mismo falso positive que Organization**.

**Causa raíz real**: Dos code paths definen "hotel_schema" de forma diferente:
- **Audit path** (`rich_results_client.py:537`): `has_hotel_schema = Hotel OR LodgingBusiness` → correcto, estricto
- **Gate/SitePresenceChecker path** (`site_presence_checker.py:364-365`): cuando `schema_type == "Hotel"`, expande a `["LodgingBusiness", "LocalBusiness", "Organization"]` → **INCORRECTO**, incluye Organization y LocalBusiness

El SitePresenceChecker encuentra `Organization` (y potencialmente `LocalBusiness`) en termales.com.co → reporta `hotel_schema` como EXISTS → el asset `hotel_schema` es SKIPPEADO → el pain `no_hotel_schema` se marca falsamente como resuelto.

**Adicionalmente**: No existe ningún mecanismo de coherencia entre el audit path y el presence path, por lo que el gate reporta `is_coherent: true` cuando el sistema es fundamentalmente incoherente.

---

## Validación de Afirmaciones del Documento Original

| Claim | Veredicto | Evidencia |
|-------|-----------|-----------|
| `hotel_schema_detected: false` | ✅ CORRECTO | `audit_report_20260509_071924.json` L6. Sitio no tiene Hotel ni LodgingBusiness. |
| `org_schema_detected: true` | ✅ CORRECTO | `audit_report` L12. Campo existe en `SchemaAuditResult` L54. |
| `total_schemas: 5` | ⚠️ Valor correcto, descripción imprecisa | No son "5 scripts JSON-LD" sino 1 script con `@graph` de 5 tipos. Tipos: WebPage, ImageObject, BreadcrumbList, WebSite, Organization. Verificado con `browser_console`. |
| `faq_schema_detected: false` | ✅ CORRECTO | No hay FAQPage en el @graph. |
| "El detector funciona correctamente" | ✅ CORRECTO para audit path | `rich_results_client.get_hotel_schema_report()` L508-514 distingue correctamente. |
| `hotel_schema` en `present_in_production` | ✅ El valor es correcto pero la interpretación NO | `asset_generation_report.json` L80-82: SKIPPED con razón "Asset ya implementado". NO es "nomenclatura confusa" — es un bug de definición divergente. |
| Path `modules/asset_generation/hotel_schema_generator.py` | ❌ INCORRECTO | No existe. El archivo real es `modules/geo_enrichment/hotel_schema_enricher.py`. |
| "M6" como gate ID | ❌ INEXISTENTE | Los gates tienen nombres descriptivos: `proposal_asset_alignment` (Gate 9, advisory). "M6" no existe en el código. |

---

## Hallazgos Amplificados (No Cubiertos por el Documento Original)

### H1 — CRÍTICO: Doble definición de "hotel_schema" (causa raíz)

**Code Path A — Audit (ESTRICTO)**:
```
v4_comprehensive.py L668-685 → rich_results_client.py L497-547
  has_hotel_schema = Hotel OR LodgingBusiness  (L537)
  NO incluye Organization NI LocalBusiness
```
Resultado: `hotel_schema_detected = false` ✅

**Code Path B — Gate/SitePresenceChecker (EXPANSIVO)**:
```
publication_gates.py L761-900 → site_presence_checker.py L353-376
  _check_schema_exists("Hotel", report)
  L364-365: if schema_type == "Hotel":
              target_types.extend(["LodgingBusiness", "LocalBusiness", "Organization"])
```
Resultado: encuentra Organization → `presence_status = "exists"` → `hotel_schema` SKIPPED ❌

La línea `site_presence_checker.py:365` es el origen exacto del falso positivo.

### H2 — CRÍTICO: False positive encadenado con consecuencias en cascada

1. `v4_comprehensive.py` L1537: "No Hotel schema detected - critical for SEO" → crítico real
2. `pain_solution_mapper.py` L105: activa `no_hotel_schema` → debería generar `hotel_schema`
3. `site_presence_checker.py` L364-365: encuentra Organization → reporta `hotel_schema` como EXISTS
4. `asset_generation_report.json` L78-88: `hotel_schema` SKIPPED con razón "Asset ya implementado"
5. `pain_solution_mapper.py` L105: `no_hotel_schema` marcado falsamente como resuelto
6. `v4_diagnostic_generator.py` L1439-1440: diagnóstico sigue diciendo "Sin Schema de Hotel — Crítica"
7. Propuesta comercial: ofrece "Datos Estructurados" como servicio pero el asset NO se genera

**El hotel se queda sin schema Hotel real, el sistema cree que está resuelto, pero el diagnóstico sigue reportándolo como crítico.**

### H3 — MEDIO: `org_schema` existe como asset separado pero no se usa

`asset_catalog.py` L131-141: `org_schema` con `promised_by=["no_org_schema"]` — asset independiente.
`pain_solution_mapper.py` L414-419: verifica `org_schema_detected` para activar `no_org_schema`.

Para termales.com.co, `org_schema_detected = true` → `no_org_schema` NO se activa (correcto). La expansión Hotel→Organization en SitePresenceChecker es redundante porque `org_schema` ya tiene su propio tracking.

### H4 — MEDIO: Impacto en scores SEO/GEO

`CHECKLIST_SEO` L153: `schema_hotel: 20` → pierde 20pts del SEO score.
`_calculate_geo_score` L319: `schema_hotel: 15` → pierde 15pts del GEO score.
El falso positive del gate no corrige estos scores — el hotel sigue penalizado en diagnóstico.

### H5 — BAJO: `schema_validator_v2.py` sin coverage Organization

`modules/data_validation/schema_validator_v2.py` (454 líneas) solo cubre Hotel y LodgingBusiness. No tiene `SCHEMA_ORGANIZATION_COVERAGE`. Si se implementara un gate de "schema_coverage", habría que extender este validador.

**Nota**: `schema_validator_v2.py` SÍ define `SCHEMA_ORGANIZATION_COVERAGE` (L57-61) pero no lo usa en `COVERAGE_MAP` para detección de schema_type principal — solo lo usa si se pasa explícitamente `schema_type="Organization"`.

---

## Hallazgos Nuevos — Iteración 2 (Auditoría cruzada contra código vivo)

### F-1 — CRÍTICO: `LocalBusiness` también causa falso positive (NO documentado previamente)

**Causa raíz**: `site_presence_checker.py:364-365` expande a `["LodgingBusiness", "LocalBusiness", "Organization"]`, pero el audit path (`rich_results_client.py:537`) solo acepta Hotel y LodgingBusiness para `has_hotel_schema`:

```python
# rich_results_client.py:537
"has_hotel_schema": has_hotel_schema or has_lodgingbusiness,
```

**LocalBusiness NO cuenta como `has_hotel_schema` en el audit, pero SÍ en el `_check_schema_exists` del SitePresenceChecker.** Si un sitio tiene `LocalBusiness` pero no `Hotel` ni `LodgingBusiness`:
- Audit dice: `hotel_schema_detected = false`
- Presence dice: `hotel_schema = EXISTS` ← **falso positive idéntico al de Organization**

**Evidencia de código**:
- `site_presence_checker.py:365` incluye `"LocalBusiness"` en la expansión
- `rich_results_client.py:537` NO lo incluye en `has_hotel_schema`
- Además, `rich_results_client.py:528-530` asigna `schema_data` al LocalBusiness con confidence `ESTIMATED` aunque `has_hotel_schema` sea `false`, lo que puede confundir a consumidores del reporte

**Para termales.com.co**: El sitio actual NO tiene LocalBusiness en su `@graph`, por lo que este bug no se manifiesta HOY, pero se manifestará en cualquier sitio que use LocalBusiness sin Hotel.

### F-2 — CRÍTICO: `coherence_report` dice `is_coherent: true` cuando el sistema es incoherente

**Evidencia**: `asset_generation_report.json:90-93`:
```json
"coherence_report": {
    "is_coherent": true,
    "checks": [{
        "name": "promised_assets_exist",
        "passed": true,
        "message": "Todos los assets prometidos están implementados (7 servicios verificados via PROPOSAL_SERVICE_TO_ASSET)"
    }]
}
```

El gate pasa con `"all_aligned": true` porque `SitePresenceChecker` reporta `hotel_schema=EXISTS`. Pero `audit_report` dice `hotel_schema_detected=false`. **No existe ningún chequeo de coherencia entre ambos sistemas**.

En `proposal_asset_alignment.py:218-229`: cuando presence dice `EXISTS`, se marca como `present_in_production` con `is_aligned: true`. No se contrasta contra el audit.

**Esto es la causa de que el bug pase desapercibido en producción** — el gate de publicación aprueba la entrega como "coherente" cuando hay una divergencia fundamental.

### F-3 — MEDIO: No existen tests unitarios para `_check_schema_exists`

**Evidencia**: Búsqueda de archivos con patrón `test.*presence|presence.*test` arrojó 0 resultados. No existe infraestructura de test para `SitePresenceChecker`. El documento propone verificar con test unitario (FASE-HOTELSCHEMA-A) pero no existe la cobertura.

### F-4 — BAJO: Dos implementaciones de parsing JSON-LD con comportamiento divergente

- `schema_finder.py` (usado por SitePresenceChecker): Extrae todos los items de `@graph` sin priorización
- `schema_validator_v2.py` (usado por audit path): Extrae y prioriza por tipo (`Hotel > LodgingBusiness > LocalBusiness > Organization`)

Ambos podrían clasificar el mismo schema de forma diferente para sitios con múltiples tipos en `@graph`.

### F-5 — BAJO: `schema_finder.py` no está alineado con `schema_validator_v2.py` en tipos requeridos

`schema_finder.py:90` define:
```python
required_schemas = ['Hotel', 'LodgingBusiness']
```

Pero `schema_validator_v2.py:191` prioriza:
```python
type_priority = ["Hotel", "LodgingBusiness", "LocalBusiness", "Organization"]
```

El `schema_finder` reporta `tiene_hotel_schema: false` correctamente para termales.com.co (solo tiene Organization), pero no distingue entre "no tiene schema de hotel" y "tiene schema de hotel incompleto".

---

## Evaluación de Soluciones del Documento Original

### Opción 1 (Documento): Fusionar hotel_schema_detected con org_schema_detected

```python
hotel_schema_detected = (
    schema_data.get("hotel_schema_detected", False) or
    schema_data.get("org_schema_detected", False)
)
```

**Veredicto**: ❌ NO RECOMENDADA. Ya está implementada en SitePresenceChecker y ES la causa del problema. Fusionar los campos destruiría la distinción semántica entre schema Hotel y schema Organization, inflaría artificialmente el SEO score, y ocultaría la carencia real de schema Hotel.

### Opción 2 (Documento): Contactar al cliente para implementar Hotel schema

**Veredicto**: ✅ Técnicamente correcta. El asset `ESTIMATED_hotel_schema_20260508_203338.json` ya fue generado en ejecución anterior. Si no se hubiera skippeado, estaría disponible.

### Opción 3 (Documento): Crear gate "schema_coverage"

**Veredicto**: ⚠️ Interesante pero alto costo. Requiere extender `schema_validator_v2.py` con Organization coverage, nuevo gate, actualizar PROPOSAL_SERVICE_TO_ASSET.

### Opción 4 (Documento): Dejar M6 estricto y documentar limitación

**Veredicto**: ⚠️ Conserva la inconsistencia. No resuelve el false positive.

---

## Solución Propuesta (Corregida — v2)

### SOL-1 (RECOMENDADA — INMEDIATA): Eliminar expansión Hotel→{LocalBusiness, Organization} en SitePresenceChecker

**Archivo**: `modules/asset_generation/site_presence_checker.py` L364-365

```python
# ACTUAL:
if schema_type == "Hotel":
    target_types.extend(["LodgingBusiness", "LocalBusiness", "Organization"])

# CORREGIDO:
if schema_type == "Hotel":
    target_types.extend(["LodgingBusiness"])
    # Organization NO es subtipo de Hotel — tiene su propio asset type (org_schema).
    # LocalBusiness NO es equivalente a Hotel — el audit path no lo incluye en has_hotel_schema.
```

**Justificación**: `org_schema` ya tiene su propio asset type y pain_id. La expansión causa false positives. LocalBusiness tampoco debería incluirse porque el audit path no lo considera hotel schema válido.

**Costo**: 1 línea eliminada. Sin efectos colaterales en otros módulos.

**Riesgo**: Hoteles con solo Organization ahora reportarán `hotel_schema` como NOT_EXISTS — comportamiento CORRECTO, porque el sitio realmente no tiene schema Hotel.

**¿Qué pasa con LodgingBusiness?** LodgingBusiness SÍ se mantiene porque:
1. El audit path (`rich_results_client.py:537`) lo acepta como equivalente funcional de Hotel
2. Schema.org define LodgingBusiness como parent de Hotel
3. El validador de schema (`schema_validator_v2.py`) le aplica el mismo coverage que Hotel

### SOL-2 (CORTO PLAZO — CRÍTICO): Coherence gate verifique consistencia audit↔presence

**Archivo**: `modules/quality_gates/coherence_validator.py` o `modules/asset_generation/proposal_asset_alignment.py`

Agregar check: si `hotel_schema_detected=false` en audit Y `site_presence` dice `hotel_schema=EXISTS` → flag INCONSISTENCY.

Implementación sugerida en `proposal_asset_alignment.py`:

```python
# En verify_proposal_asset_alignment(), antes de marcar present_in_production:
if expected_asset_type == "hotel_schema" and presence_status == "exists":
    # Verificar si audit realmente detectó hotel schema
    audit_report = assessment.get("audit_report", {})
    schema_data = audit_report.get("schema", {})
    if not schema_data.get("hotel_schema_detected", False):
        # DIVERGENCIA: presence dice exists pero audit dice false
        report.missing.append(ServiceAlignment(
            service_name=service_name,
            asset_type=expected_asset_type,
            is_aligned=False,
            status="missing",
            message=f"DIVERGENCIA: SitePresenceChecker reporta EXISTS pero audit reporta hotel_schema_detected=false. "
                    f"El asset '{expected_asset_type}' NO se debe considerar presente.",
            presence_verified=True,
            presence_status="divergent"  # Nuevo estado
        ))
        continue
```

**Costo**: ~20-30 líneas.

**Previene**: Recurrencia del problema si alguien reintroduce la expansión, o si el SitePresenceChecker tiene cualquier otro falso positive.

### SOL-3 (MEDIANO PLAZO — OPCIONAL): Separar servicios en propuesta

**Archivo**: `modules/asset_generation/proposal_asset_alignment.py`

```python
PROPOSAL_SERVICE_TO_ASSET = {
    ...
    "Schema Hotel": "hotel_schema",
    "Schema Organization": "org_schema",   # Ya existe en asset_catalog
    ...
}
```

**Costo**: ~5 líneas + actualizar templates de propuesta y pain_solution_mapper.

**Beneficio**: Transparencia para el cliente — "Ya tienes Organization, necesitas Hotel schema".

### SOL-4 (COMPLEMENTARIO): Agregar tests unitarios para `_check_schema_exists`

Crear `tests/test_site_presence_checker.py` con cobertura para:
- Hotel schema presente → found
- Solo Organization → NOT_FOUND (después de fix)
- Solo LocalBusiness → NOT_FOUND (después de fix)
- LodgingBusiness presente → found
- Hotel + Organization mix → found (Hotel match priorizado)
- Schema vacío → NOT_FOUND

---

## Archivos Clave Referenciados

| Archivo | Rol | Línea Clave |
|---------|-----|-------------|
| `modules/asset_generation/site_presence_checker.py` | **Causa raíz** — expansión Hotel→{LodgingBusiness, LocalBusiness, Organization} | L364-365 |
| `modules/data_validation/external_apis/rich_results_client.py` | Audit — detección estricta | L508-514, L537 |
| `modules/auditors/v4_comprehensive.py` | SchemaAuditResult + _audit_schemas | L45-58, L668-685 |
| `modules/quality_gates/publication_gates.py` | Gate 9 (proposal_asset_alignment) | L761-900 |
| `modules/asset_generation/proposal_asset_alignment.py` | PROPOSAL_SERVICE_TO_ASSET + verify_proposal_asset_alignment | L20-28, L215-229 |
| `modules/commercial_documents/v4_diagnostic_generator.py` | Scores + checklist SEO/GEO | L151-158, L318-320, L1439-1447 |
| `modules/commercial_documents/pain_solution_mapper.py` | no_hotel_schema + no_org_schema | L100-109, L119-123, L414-419 |
| `modules/asset_generation/asset_catalog.py` | hotel_schema + org_schema assets | L87-97, L131-141 |
| `modules/scrapers/schema_finder.py` | Parser JSON-LD usado por SitePresenceChecker | L64-70, L90 |
| `modules/data_validation/schema_validator_v2.py` | Parser JSON-LD usado por audit path | L82-87, L191 |
| `output/v4_complete/termales/v4_audit/asset_generation_report.json` | Evidencia: hotel_schema SKIPPED, coherence=true | L78-88, L90-93 |
| `output/v4_complete/termales/v4_audit/audit_report_20260509_071924.json` | Evidencia: valores de schema | L5-17 |

---

## Verificación del Sitio Real (termales.com.co)

Visitado con browser el 2026-05-09. El sitio tiene **1 script JSON-LD** con `@graph` de 5 tipos:
1. `WebPage`
2. `ImageObject`
3. `BreadcrumbList`
4. `WebSite`
5. `Organization`

No tiene: `Hotel`, `LodgingBusiness`, `LocalBusiness`, `FAQPage`, `HotelRoom`.

---

## Propuesta de Macro-Fases para Implementación (v2)

### FASE-HOTELSCHEMA-A: Fix causa raíz (SOL-1)
- [ ] Eliminar `"LocalBusiness"` y `"Organization"` de `site_presence_checker.py` L365
- [ ] Crear `tests/test_site_presence_checker.py` (SOL-4)
- [ ] Verificar con test unitario que `_check_schema_exists("Hotel", report_with_org)` retorna `found=False`
- [ ] Ejecutar `v4complete` para termales.com.co y verificar que `hotel_schema` ahora se genera (no se skippea)
- [ ] Ejecutar `python scripts/run_all_validations.py --quick` para verificar no-regresión

### FASE-HOTELSCHEMA-B: Coherence gate (SOL-2)
- [ ] Agregar check de consistencia audit↔presence en `proposal_asset_alignment.py` o `coherence_validator.py`
- [ ] Test: verificar que detecta divergencia cuando audit dice false y presence dice exists
- [ ] Ejecutar `v4complete` para termales.com.co y verificar que el gate reporta divergencia en vez de `is_coherent: true`

### FASE-HOTELSCHEMA-C: Separación de servicios (SOL-3 — OPCIONAL)
- [ ] Modificar `PROPOSAL_SERVICE_TO_ASSET` para separar Schema Hotel y Schema Organization
- [ ] Actualizar `pain_solution_mapper.py`
- [ ] Actualizar templates de propuesta

---

## Prompt para Próxima Sesión

```
Carga el contexto .opencode/context/AUDITORIA_M6_HOTELSCHEMA_TERMALES_20260509.md.

FASE-HOTELSCHEMA-A (SOL-1):
1. Elimina "LocalBusiness" y "Organization" de la expansión Hotel en
   modules/asset_generation/site_presence_checker.py L365.
   → Queda: target_types.extend(["LodgingBusiness"])

2. Ejecuta v4complete para http://www.termales.com.co/ y verifica que
   hotel_schema ahora se genera (no se skippea).

3. Ejecuta log_phase_completion.py --fase FASE-HOTELSCHEMA-A
   --desc "Fix expansion Hotel→LodgingBusiness en SitePresenceChecker (eliminada Organization y LocalBusiness)"

FASE-HOTELSCHEMA-B (SOL-2):
4. Agrega coherence check en proposal_asset_alignment.py: si audit dice
   hotel_schema_detected=false y presence dice EXISTS → flag DIVERGENT.

5. Ejecuta v4complete para verificar que el gate ahora detecta la divergencia.
```