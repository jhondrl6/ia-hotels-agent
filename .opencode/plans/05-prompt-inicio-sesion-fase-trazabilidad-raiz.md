# Prompt de Inicio de Sesión: FASE-TRAZABILIDAD-RAIZ

**Proyecto**: Corrección Trazabilidad "Calidad Garantizada" + Reconección Módulos→Diagnóstico
**Fase**: 2 de 3 — Unificación + Cableado + Reconección Template + Deprecaciones
**Sesión**: Nueva (1 fase por sesión)
**Dependencia**: FASE-TRAZABILIDAD-DOCS completada (documentos ya reflejan 9 gates)
**Auditoría origen**: `.opencode/context/auditoria_calidad_garantizada_20260424.md` (10 hallazgos originales + 8 nuevos hallazgos de auditoría profundizada 2026-04-25)
**Decisiones deprecación**: `00-decisiones-deprecacion.md`

---

## Contexto Ampliado

### Problema Raíz (detección dual)
El sistema tiene DOS detectores paralelos con criterios divergentes:

| Detector | Archivo | Output | Consumido por |
|----------|---------|--------|---------------|
| `detect_pains()` | `pain_solution_mapper.py:323` | `List[Pain]` (13 tipos) | `main.py` → `asset_plan` |
| `_identify_brechas()` | `v4_diagnostic_generator.py:2001` | `List[Dict]` (10 tipos) | Template del diagnóstico |

### Problema Template (datos producidos pero ignorados)
La auditoría profundizada descubrió que el template V6 ELIMINÓ secciones críticas:
- `${geo_table}` — tabla de métricas IA que el generador SÍ computa (crawlers bloqueados, citability, ia_readiness). **14 bots de IA bloqueados NUNCA aparecen en el diagnóstico.**
- Sin sección de hallazgos positivos (WhatsApp detectado, HTTPS, redes sociales, 202 reviews)
- `geo_flow_result` (score 23, "critical") existe pero es invisible para el cliente

### Problemas de Dualidad (módulos que compiten)
- SEO: `_calculate_web_score()` = 10 vs `calcular_score_seo()` = 25 → **DEP-01: deprecar el primero**
- IAO: CHECKLIST_IAO = 17 vs `ia_readiness.overall_score` = 33.2 → **DEP-02: deprecar CHECKLIST_IAO standalone**
- GEO primario: 62 (GBP) vs geo_flow = 23 (técnico) → **RES-03: ambos, complementarios**

### Lo que YA funciona (NO TOCAR)
- `CoherenceValidator.validate()` → se ejecuta en main.py ✓
- `detect_pains()` → retorna `List[Pain]` correctamente ✓
- `SERVICE_CATALOG` → mapea `pain_id → ServiceEntry` ✓
- `PROPOSAL_SERVICE_TO_ASSET` → existe ✓

---

## Tareas Específicas

### T0: UNIFICAR sistemas de detección (RAÍZ — CRÍTICA #2)

**Objetivo**: Una sola fuente de verdad. `_identify_brechas()` debe basarse en `detect_pains()`, no duplicar lógica con umbrales diferentes.

**Archivo A**: `modules/commercial_documents/v4_diagnostic_generator.py`

1. Refactorizar `_identify_brechas()` (línea 2001):
   - Llamar a `detect_pains()` internamente para obtener `List[Pain]`
   - Traducir cada `Pain` a formato brecha (agregar `nombre`, `impacto`, `detalle` comercial)
   - ELIMINAR los umbrales duplicados (L2027 geo<60, L2061 mobile<70, L2116 citability<30)
   - Los umbrales ahora vienen de `detect_pains()` (geo<70, mobile<50, citability<50)

2. Agregar traducción Pain→Brecha para los pain_ids NUEVOS:
   - `no_org_schema` → brecha: "Sin Schema Organization (Entidad no verificable)"
   - `no_analytics_configured` → brecha: "Sin Analytics (Decisiones a ciegas)"
   - `ai_crawler_blocked` → brecha: "IA Bloqueada (Invisible para ChatGPT)"
   - `low_ia_readiness` → brecha: "Baja Preparación para IA"

**Archivo B**: `modules/commercial_documents/pain_solution_mapper.py`

3. Agregar detección de `no_og_tags` en `detect_pains()` (línea ~410, después de org_schema):
   ```python
   # Check Open Graph tags
   if audit_result.seo_elements and not getattr(audit_result.seo_elements, 'open_graph', False):
       pains.append(Pain(
           id="no_og_tags",
           name="Sin Meta Tags Open Graph",
           description="No se detectan metadatos og:title/og:image/og:description",
           severity="medium",
           detected_by="seo_elements",
           confidence=1.0
       ))
   ```

4. Verificar que cada pain_id de brechas tenga entrada en `PAIN_SOLUTION_MAP`
5. Verificar que cada pain_id tenga entrada en `SERVICE_CATALOG`

**Verificación T0**:
```bash
# Comparar pain_ids de ambos detectores
grep "id=" modules/commercial_documents/pain_solution_mapper.py | grep -oP '"([^"]+)"' | head -20
grep "pain_id" modules/commercial_documents/v4_diagnostic_generator.py | grep -oP "'([^']+)'" | sort -u
```

---

### T1-T2: Cablear PublicationGatesOrchestrator en main.py

(SIN CAMBIOS respecto al plan original — ver plan anterior para detalles)

**Puntos clave**:
- Insertar después de FASE 4 (Coherence Gate) y ANTES de regenerar diagnóstico
- Construir `assessment` dict con TODAS las keys que los 9 gates necesitan
- Incluir `financial_sources` para T1.1
- Generar `gate_report.json`

---

### T1.1: Reforzar gate financial_validity (CRÍTICA #1 + BUG-02)

(SIN CAMBIOS — ver plan original)

---

### T4.1: Unificar cálculo SEO — REVISADO (DEP-01)

**Decisión**: `calcular_score_seo()` vía CHECKLIST_SEO es el algoritmo autoritativo.
`_calculate_web_score()` se DEPRECA.

**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py`

1. Modificar `_calculate_web_score()` (línea 1373) para que delegue en CHECKLIST_SEO:
   ```python
   def _calculate_web_score(self, audit_result: V4AuditResult) -> str:
       """Calculate Web/SEO score using CHECKLIST_SEO (4-pilar framework).
       
       Deprecated: old custom algorithm replaced by CHECKLIST_SEO for consistency
       with GEO/AEO/IAO pilar calculations.
       """
       elementos = self._extraer_elementos_seo(audit_result)
       score = calcular_score_seo(elementos)
       return str(score)
   ```

2. El antiguo algoritmo custom (líneas 1375-1393) se ELIMINA.
3. `calcular_score_seo()` ya se usa en `_calculate_score_global_from_audit()` — sin cambios.
4. Efecto: SEO mostrado en diagnóstico = SEO usado en score_global. Sin dualidad.

**Verificación**: grep `_calculate_web_score` y confirmar que solo existe la versión wrapper.

---

### T4.2: Unificar IAO vs ia_readiness — REVISADO (DEP-02)

**Decisión**: `ia_readiness.overall_score` es el valor autoritativo.
CHECKLIST_IAO standalone se DEPRECA como fuente primaria (mantener como fallback).

**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py`

1. Modificar `_calculate_iao_score_from_audit()` (línea 1424):
   ```python
   def _calculate_iao_score_from_audit(self, audit_result: V4AuditResult) -> str:
       """Calculate IAO score from ia_readiness module (primary) or CHECKLIST_IAO (fallback).
       
       Source of truth: ia_readiness.overall_score (granular, multi-component).
       """
       # Primary: ia_readiness module
       if hasattr(audit_result, 'ia_readiness') and audit_result.ia_readiness:
           score = getattr(audit_result.ia_readiness, 'overall_score', None)
           if score is not None:
               return str(int(score))
       
       # Fallback: CHECKLIST_IAO
       elementos_iao = self._extraer_elementos_iao(audit_result)
       base_score = calcular_score_iao(elementos_iao)
       
       llm_report = getattr(audit_result, 'llm_report', None)
       if llm_report and llm_report.source != "stub":
           real_score = llm_report.mention_score
           base_score = int(base_score * 0.5 + real_score * 0.5)
       
       return str(min(100, max(0, base_score)))
   ```

2. `_extraer_elementos_iao()` se mantiene como fallback interno (NO se depreca el código, solo se degrada a secundario).
3. Efecto: IAO ≈ 33 (desde ia_readiness) en vez de 17. Coincide con audit_report.json.

---

### T7: RESTAURAR tabla de métricas IA en template V6 (D11, D13, RES-01)

**Objetivo**: La información que `_build_geo_problems_table()` ya computa DEBE ser visible para el cliente.

**Archivo A**: `modules/commercial_documents/templates/diagnostico_v6_template.md`

1. Insertar `${ia_metrics_table}` después de la tabla de 4 pilares (línea 57, después de `${regional_transparency}`):

```markdown
### Métricas de Acceso para IA

${ia_metrics_table}
```

**Archivo B**: `modules/commercial_documents/v4_diagnostic_generator.py`

2. Renombrar variable en `_prepare_template_data()` (línea 458):
   - Cambiar `'geo_table':` → `'ia_metrics_table':` (nombre más descriptivo)
   - O mantener ambos nombres para backward compat

3. Expandir `_build_geo_problems_table()` (línea 1154) para incluir geo_flow_result:
   - Agregar 4ta fila: "Salud Técnica GEO" con score de `geo_flow_result.json` si existe
   - Si no existe geo_flow_result, mostrar solo las 3 filas existentes

4. La tabla generada debe verse así:
```markdown
| Métrica | Score | Detalle | Estado |
|---------|-------|---------|--------|
| Accesibilidad IA | 0.50/1.00 | 14 crawlers bloqueados | 🔴 |
| Citabilidad | 51.7/100 | 3 bloques analizados | 🟢 |
| IA-Readiness | 33.2/100 | Critical | 🟡 |
| Salud Técnica GEO | 23/100 | Crisis técnica | 🔴 |
```

---

### T8: CORREGIR bug escala crawler_access (MENOR #7 → incluido, BUG-01)

**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py` línea 1927

```python
# ANTES (BUG):
and audit_result.ai_crawlers.overall_score > 50

# DESPUÉS (CORRECTO):
and audit_result.ai_crawlers.overall_score > 0.5
```

Efecto: restaura ~15pts al cálculo IAO cuando se use CHECKLIST_IAO como fallback.

---

### T9: AGREGAR sección de hallazgos positivos (D15, RES-02)

**Objetivo**: El diagnóstico no debe ser solo problemas. Mostrar lo que YA funciona genera confianza.

**Archivo A**: `modules/commercial_documents/v4_diagnostic_generator.py`

Nueva función (insertar antes de `_build_quick_wins`, ~línea 1108):

```python
def _build_positive_findings(self, audit_result: V4AuditResult) -> str:
    """Build list of positive findings from audit data."""
    findings = []
    
    # HTTPS
    if audit_result.url and audit_result.url.startswith('https'):
        findings.append("✅ **HTTPS activo** — Sitio seguro con certificado SSL")
    
    # WhatsApp
    if audit_result.validation:
        ws = getattr(audit_result.validation, 'whatsapp_status', None)
        if ws == 'verified':
            phone = getattr(audit_result.validation, 'phone_web', '')
            findings.append(f"✅ **WhatsApp verificado** — Canal directo funcional ({phone})")
    
    # GBP presence
    if audit_result.gbp and audit_result.gbp.place_found:
        rating = audit_result.gbp.rating
        reviews = audit_result.gbp.reviews
        findings.append(f"✅ **Google Business Profile activo** — {reviews} reviews, {rating}/5 rating")
    
    # Social media
    if hasattr(audit_result, 'seo_elements') and audit_result.seo_elements:
        social = getattr(audit_result.seo_elements, 'social_links_found', [])
        if social:
            platforms = []
            for link in social[:3]:
                if 'facebook' in link: platforms.append('Facebook')
                elif 'instagram' in link: platforms.append('Instagram')
                elif 'youtube' in link: platforms.append('YouTube')
            if platforms:
                findings.append(f"✅ **Redes sociales activas** — {' ,'.join(platforms)}")
    
    if not findings:
        return ""  # No section if nothing positive
    
    return "### ✅ Lo que ya funciona\n\n" + "\n".join(findings) + "\n"
```

**Archivo B**: Agregar `${positive_findings}` en `_prepare_template_data()`:
```python
'positive_findings': self._build_positive_findings(audit_result),
```

**Archivo C**: Insertar `${positive_findings}` en template V6, justo después de la tabla de 4 pilares y antes de "Impacto Financiero".

---

### T10: REFERENCIAR geo_flow_result como métrica complementaria (D12, RES-03)

**Objetivo**: El cliente ve GEO=62 (Google Maps) pero el sistema sabe que la salud técnica es 23 (critical). Ambos deben ser visibles.

Ya cubierto por T7 (agregar fila a `_build_geo_problems_table()`).

Adicionalmente, en `_prepare_template_data()` (línea ~467), agregar nota en `${regional_transparency}` si geo_flow_result existe y su score es < 40:
```python
geo_flow_note = ""
geo_flow_path = Path(output_dir) / "amaziliahotel" / "v4_audit" / "geo_flow_result.json"
if geo_flow_path.exists():
    # Add note about technical GEO health
    ...
```

---

### T5: Tests para PublicationGatesOrchestrator

(SIN CAMBIOS — 12 tests como en plan original, expandir a 14 con tests para T0 y T8)

Tests adicionales:
- 13. `test_identify_brechas_uses_detect_pains` — verifica que brechas vienen de detect_pains()
- 14. `test_crawler_scale_fix` — verifica que 0.5 > 0.5 (no > 50)
- 15. `test_positive_findings_generated` — verifica sección de hallazgos positivos
- 16. `test_ia_metrics_table_in_output` — verifica que `${ia_metrics_table}` existe en output

---

### T11: LIMPIEZA de código muerto (D14)

1. Si `${geo_table}` se renombra a `${ia_metrics_table}`, eliminar asignación antigua
2. Si V4 template ya no se usa, considerar deprecarlo
3. Agregar comentario `# DEPRECATED` en `_calculate_web_score()` wrapper
4. Agregar comentario `# FALLBACK only` en `_extraer_elementos_iao()`

---

### T6: CHANGELOG.md y documentación

Actualizar CHANGELOG.md con formato CONTRIBUTING.md:
- Objetivo: Unificación detectores + reconección template + deprecaciones
- DEP-01, DEP-02, DEP-03 documentados
- BUG-01, BUG-02 corregidos
- RES-01, RES-02, RES-03 implementados

---

## Criterios de Completitud

### Detección unificada
- [ ] T0: `_identify_brechas()` delega en `detect_pains()` (no duplica umbrales)
- [ ] T0: `detect_pains()` ahora detecta `no_og_tags` (bidireccional)
- [ ] T0: Pain_ids nuevos agregados: `no_org_schema`, `no_analytics_configured`, `ai_crawler_blocked`, `low_ia_readiness`
- [ ] T0: Todo pain_id de brechas existe en `PAIN_SOLUTION_MAP` y `SERVICE_CATALOG`

### Cableado de gates
- [ ] T1-T2: `PublicationGatesOrchestrator` cableado en `main.py` v4complete
- [ ] T1.1: Gate `financial_validity` inspecciona `financial_sources` (BUG-02)
- [ ] T2: `gate_report.json` se genera junto al diagnóstico

### Unificación de scores
- [ ] T4.1: `_calculate_web_score()` es wrapper de `calcular_score_seo()` (DEP-01)
- [ ] T4.1: Algoritmo custom antiguo ELIMINADO
- [ ] T4.2: IAO usa `ia_readiness.overall_score` como primario (DEP-02)
- [ ] T4.2: CHECKLIST_IAO es solo fallback

### Reconección template
- [ ] T7: `${ia_metrics_table}` insertado en template V6 (RES-01)
- [ ] T7: `_build_geo_problems_table()` incluye fila geo_flow_result (RES-03)
- [ ] T8: Bug escala crawler corregido: `> 50` → `> 0.5` (BUG-01)
- [ ] T9: `${positive_findings}` insertado en template V6 (RES-02)
- [ ] T9: `_build_positive_findings()` implementada

### Tests y docs
- [ ] T5: 16 tests total (12 originales + 4 nuevos)
- [ ] T11: Código muerto limpiado/etiquetado
- [ ] T6: CHANGELOG.md actualizado con deprecaciones

## Post-Ejecución

```bash
# 1. Ejecutar tests
./venv/Scripts/python.exe -m pytest tests/quality_gates/test_publication_gates.py -v

# 2. Test de integración rápida (solo generación, sin APIs)
./venv/Scripts/python.exe -m pytest tests/ -k "test_identify_brechas or test_crawler or test_positive or test_ia_metrics" -v

# 3. Registrar fase
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-TRAZABILIDAD-RAIZ \
    --desc "Unificacion detectores + cableado 9 gates + financial_source validation + DEP-01(SEO unificado CHECKLIST_SEO) + DEP-02(IAO=ia_readiness) + DEP-03(brechas delegan en detect_pains) + RES-01(ia_metrics_table V6) + RES-02(positive_findings) + RES-03(geo_flow ref) + BUG-01(crawler scale) + BUG-02(financial sources) + 16 tests" \
    --archivos-mod "main.py,modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/pain_solution_mapper.py,modules/commercial_documents/service_catalog.py,modules/commercial_documents/templates/diagnostico_v6_template.md,modules/quality_gates/publication_gates.py,CHANGELOG.md" \
    --tests "16" \
    --check-manual-docs

# 4. Commit
git add -A && git commit -m "FASE-TRAZABILIDAD-RAIZ: Unify pain/brecha detection + wire 9 gates + financial source validation + DEP-01-03 deprecations + RES-01-03 template reconnections + BUG-01-02 fixes"
```

## Archivos Involucrados

| Archivo | Tipo | Cambio |
|---------|------|--------|
| `v4_diagnostic_generator.py` | Modificar | T0 (refactor brechas) + T4.1 (SEO wrapper) + T4.2 (IAO primario) + T7 (ia_metrics_table) + T8 (crawler fix) + T9 (positive_findings) + T11 (limpieza) |
| `pain_solution_mapper.py` | Modificar | T0 (agregar no_og_tags detección) |
| `service_catalog.py` | Verificar | T0 (ServiceEntry por cada pain_id) |
| `diagnostico_v6_template.md` | Modificar | T7 (ia_metrics_table) + T9 (positive_findings) + T3-T4 (gate section + trazabilidad) |
| `publication_gates.py` | Modificar | T1.1 (financial_validity source check) |
| `main.py` | Modificar | T1-T2 (cablear gates + financial_sources) |
| `tests/quality_gates/test_publication_gates.py` | Nuevo/Expandir | T5 (16 tests) |
| `CHANGELOG.md` | Modificar | T6 (documentar cambios + deprecaciones) |

---

## Decisiones de Deprecación (referencia rápida)

Ver `00-decisiones-deprecacion.md` para detalle completo.

| DEP # | Qué | Acción |
|-------|-----|--------|
| DEP-01 | `_calculate_web_score()` custom | → wrapper de `calcular_score_seo()` |
| DEP-02 | CHECKLIST_IAO standalone | → `ia_readiness.overall_score` primario |
| DEP-03 | Umbrales duplicados brechas | → delegar en `detect_pains()` |

| RES # | Qué | Acción |
|-------|-----|--------|
| RES-01 | IA metrics en V6 | RESTAURAR `${ia_metrics_table}` |
| RES-02 | Hallazgos positivos | CREAR `${positive_findings}` |
| RES-03 | geo_flow_result | AGREGAR a métricas IA |

| BUG # | Qué | Acción |
|-------|-----|--------|
| BUG-01 | crawler scale 0-1 vs 50 | `> 50` → `> 0.5` |
| BUG-02 | financial sources ignorados | Pasar `sources` a validator |
