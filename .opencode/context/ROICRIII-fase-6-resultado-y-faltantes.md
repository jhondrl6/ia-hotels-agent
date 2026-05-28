# ROICRIII — FASE-6 Resultado y Faltantes

**Fecha**: 2026-05-28
**Estado**: ⏳ INCOMPLETA — Publication readiness: NOT_READY
**Última actualización análisis**: 2026-05-28 (post-auditoría contra código vivo)

---

## Resumen Ejecutivo

v4complete para Hotel Castilla Real se ejecutó exitosamente con coherencia 0.83 (≥ 0.80 threshold). Se generaron los 5 niveles de verificación y la mayoría pasaron. Sin embargo, **publication readiness está bloqueado** por un gate de alineación de assets y persisten 2 issues menores.

**Aclaración crítica del usuario**: https://hotelcastillareal.com/ **SÍ tiene botón de WhatsApp**. Esto transforma el Issue 1 de "pipeline no genera asset" a "el asset fue correctamente detectado como existente y SKIPPED, pero el publication gate no lo reconoce como present_in_production".

---

## Lo que PASÓ bien

| Aspecto | Resultado |
|---------|-----------|
| Coherence score | ✅ 0.83 (pre), 0.81 (post) — ambas ≥ 0.80 |
| ROI único | ✅ 2.10X en documento (sin dualidad 0.45X/2.10X) |
| Beneficio neto | ✅ +$5.04M COP positivo |
| % inversión/fuga | ✅ 10.7% (no 14% ni 41%) |
| Trazabilidad origen | ✅ Fuga × Curva × Recovery Factor presente |
| Assets deprecados | ✅ 0 generados (og_tags_guide, indirect_traffic, local_content_page, voice_assistant_guide — todos DEPRECATED en catálogo, promised_by=[], status=DEPRECATED) |
| Piloto 30 días | ✅ Secciones "Quick Wins" + "Piloto de Validación" presentes |
| CAPEX breakdown | ✅ Setup fee $2.5M COP (suyo) + OPEX $400K/mes |
| Garantía KPI | ✅ Día 55: +15% clics directos vs línea base GSC |
| WhatsApp narrativa | ✅ "Auditoría y Optimización de Conversión" en propuesta (línea 47: "📋 Auditoría incluida") |
| Mapeo semántico | ✅ "Informe Mensual" ya no fuerza "→ FAQ" como equivalencia |
| SitePresenceChecker | ✅ Correctamente detectó whatsapp_button como EXISTS y lo SKIPPEÓ (asset_generation_report.json: presence_status="exists", site_verified=true) |
| Gates pasados | ✅ 10/11 (8 PASSED + 2 WARNING con passed=true) |

---

## Lo que FALTA (Issues Abiertos)

### Issue 1 — BLOQUEANTE: proposal_asset_alignment < 80% (62.5%)

**Gate**: `proposal_asset_alignment`
**Estado**: ❌ BLOCKED
**Valor**: 62.5% (threshold: 80%)
**Gate report**: `gate_report_20260528_151039.json` línea 100

**Detalle del gate_report**:
- 8 services totales
- 5 aligned: Schema Hotel (1.0), Schema Organization (0.8), Informe Mensual (1.0), Meta Tags OG (1.0), Optimización IA (1.0)
- 1 missing: Botón de WhatsApp → `whatsapp_button`
- 2 low_quality: SEO Local → `optimization_guide` (0.5), Página FAQ → `faq_page` (0.5)

**Impacto**: Publication readiness = NOT_READY. El documento no puede publicarse sin resolver esto.

---

#### Causa Raíz VERIFICADA (Auditoría 2026-05-28)

> ⚠️ **CORRECCIÓN DE DIAGNÓSTICO PREVIO**: El documento anterior atribuía el Issue 1 a un "falso negativo del detector de WhatsApp". Esto es **INCORRECTO** verificado contra código vivo.

**Evidencia** (`asset_generation_report.json` líneas 173-183):
```json
"skipped_assets": [{
    "asset_type": "whatsapp_button",
    "reason": "Asset ya implementado en sitio de producción",
    "presence_status": "exists",
    "site_verified": true,
    "pain_ids_affected": ["no_whatsapp_visible"]
}]
```

**El detector de WhatsApp FUNCIONA correctamente**:
1. `ConditionalGenerator` ejecuta `SitePresenceChecker.check_site()` antes de generar
2. `SitePresenceChecker._check_html_element()` busca hrefs `wa.me`, clases CSS `whatsapp`/`joinchat`, y texto "whatsapp" en el HTML
3. Para Hotel Castilla Real → detectó el botón → `PresenceStatus.EXISTS`
4. `ConditionalGenerator` lo SKIPPEÓ correctamente (no generar algo que ya existe)

**La causa raíz REAL es un bug de integración en el publication gate**:
- `_proposal_asset_alignment_gate` (publication_gates.py L797-1097) tiene su propio `SitePresenceChecker`
- El gate debería marcar `whatsapp_button` como `present_in_production` (proposal_asset_alignment.py L261-272)
- Pero el gate_report muestra `whatsapp_button` en `missing` SIN `presence_verified` — significa que el presence check del gate NO procesó este asset correctamente
- El `site_presence_report` SÍ se pasa al assessment (main.py L2770: `builder.with_site_presence(site_presence_report)`)
- Hipótesis: el gate falló silenciosamente (try/except L872-881 traga errores) o el checker del gate no encontró el botón por diferencia de URL/cache

**Archivo clave**: `modules/quality_gates/publication_gates.py` L857-881 (gate's SitePresenceChecker invocation)

**Impacto de alignment corregido** (si whatsapp → present_in_production):
- Current: 5 aligned / (5+2+1) = 62.5% → BLOCKED
- Fixeado: (5+1) / (5+2) = 75.0% → **SIGUE BLOQUEADO** (< 80%)
- Para desbloquear: NECESITA TAMBIÉN resolver low_quality (Issue 3)

---

#### Opciones de solución (CORREGIDAS)

| Opción | Descripción | Pros | Cons | Recomendación |
|--------|-------------|------|------|---------------|
| **A. Fix del gate (no del detector)** | Debuggear `_proposal_asset_alignment_gate` L857-881: por qué SitePresenceChecker del gate no marca whatsapp_button como present_in_production. Verificar URL, cache, error silencioso. | Ataca la raíz real; alinea gate con ConditionalGenerator | Requiere debug del gate | **PRINCIPAL** |
| **B. Pasar site_presence_report pre-built** | El `site_presence_report` del assessment (main.py L2693-2700) ya tiene whatsapp_button=EXISTS. Verificar que el gate lo use en vez de re-ejecutar checker. | Reutiliza trabajo existente; evita re-chequeo | Puede tener stale data si URL difiere | **PRINCIPAL (complementario a A)** |
| **C. Bypass temporal manual** | En `proposal_asset_alignment`, forzar marcado de `whatsapp_button` como "present_in_production" para este caso | Desbloquea publicación rápido | Mascarada; se repite en otros sitios | **NO recomendada** |

**Preguntas para diagnosticar**:
1. ¿El gate's SitePresenceChecker devolvió NOT_EXISTS o falló silenciosamente? (revisar logs)
2. ¿El `site_presence_report` del assessment tiene whatsapp_button en results? (debería, main.py L2698 lo incluye)
3. ¿El gate prefiere su propio checker sobre el report del assessment? (L855-857: `assessment.get("site_presence_report")` debería tenerlo)

---

### Issue 2 — SEMÁNTICO: "13% del dolor priorizado" es un ARTIFACTO de pricing

**Ubicación**: Línea 128 de `02_PROPUESTA_COMERCIAL_*.md`
```
(13% del dolor priorizado × 35% de recuperación conservadora)
```

#### Causa Raíz VERIFICADA (Auditoría 2026-05-28)

**El "13%" NO es un factor de la fórmula de recuperación.** Viene del `pain_ratio` del pricing calculator:

**Evidencia** (`financial_scenarios_20260528_151025.json`):
```json
"pricing": {
    "pain_ratio": 0.1361
}
```

El `pain_ratio` = `monthly_price / expected_monthly_loss` = $400K / $3.74M ≈ 0.107. El valor 0.1361 puede incluir setup amortizado u otro denominador. De cualquier forma, es un **indicador de pricing**, no un insumo de la fórmula de recuperación.

**Verificación matemática**:
- Si "13% × 35% × dolor_priorizado = $5,041,935", entonces dolor_priorizado = $110.8M
- Pero la fuga total 6 meses = $22.45M → ratio 4.9x ← **IMPOSIBLE**
- La fórmula REAL es: `Σ(mensual $3.74M × maturity% × 35%) = $5,041,935`
- Porcentaje real de recuperación/dolor = 22.5%, no 13%

**La trazabilidad correcta** (ya presente en línea 129):
> Fuga mensual ($3,741,696) × Curva de Maduración 4 Pilares (GEO→SEO→AEO→IAO) × Recovery Factor 35%

La línea 129 ES correcta. La línea 128 es la que introduce confusión al presentar "13%" como si fuera un factor multiplicativo.

#### Opciones de solución (CORREGIDAS)

| Opción | Descripción | Pros | Cons | Recomendación |
|--------|-------------|------|------|---------------|
| **A. Eliminar línea 128** | Dejar SOLO la trazabilidad de línea 129 que ya es correcta | Elimina el número mágico; la trazabilidad real ya existe | Pierde el "resumen ejecutivo" de una línea | **PRINCIPAL** |
| **B. Corregir línea 128** | Cambiar a: `(Recuperación proyectada = Σ[Fuga mensual × % Maduración × 35%])` | Mantiene resumen pero con fórmula correcta | Un poco verboso | **Viable** |
| **C. Tabla de parámetros** | Añadir tabla "Supuestos y parámetros" debajo con: fuga mensual, curva de maduración por mes, recovery factor 35% | Transparencia máxima; confianza del cliente | Cambio de layout en propuesta | **RECOMENDADA como complemento** |

**Nota**: La tabla de maduración ya existe en el documento (líneas 139-145). La corrección mínima es eliminar la línea 128 y dejar que la tabla + línea 129 hablen por sí solas.

---

### Issue 3 — CRÍTICO (re-clasificado): asset_confidence bajo threshold

**Assets bajo 0.7**:
- `faq_page`: 0.5
- `optimization_guide`: 0.5

**Detalle del gate_report**:
```json
"2 asset(s) below confidence threshold (0.7)"
"services: SEO Local (optimization_guide), Página de FAQ (faq_page)"
```

#### Corrección de error previo

> ⚠️ **CORRECCIÓN**: El documento anterior listaba `optimization_guide` como "ausente" (línea 26). Esto es **INCORRECTO**. `optimization_guide` SÍ fue generado (`asset_generation_report.json` líneas 44-55: confidence=0.5, pain_ids_resolved=["metadata_defaults"]). Es un asset de **baja calidad**, no ausente.

#### Re-clasificación de severidad

> ⚠️ **CORRECCIÓN**: El documento anterior clasificaba Issue 3 como "Warning, no bloqueante". Esto es **INCORRECTO**. Con el fix de Issue 1 (whatsapp → present_in_production), alignment sube a 75% — sigue bajo 80%. Los 2 low_quality items están en el denominador del alignment pero NO cuentan como "satisfied". Por tanto, **Issue 3 es CO-BLOQUEANTE** junto con Issue 1.

**Impacto real**:
- Sin fix Issue 3: alignment = (5+1) / (5+2+0) = 75% → BLOCKED
- Con Issue 3 fixeado (ambos a ≥ 0.7): alignment = (5+2+1) / (5+2+0) = 100% → PASSED
- Necesita solo UNO de los dos ≥ 0.7 para llegar a 87.5% → PASSED

#### Opciones de solución (CORREGIDAS)

| Opción | Descripción | Pros | Cons | Recomendación |
|--------|-------------|------|------|---------------|
| **A. Enriquecer datos DOM** | Extraer más metadatos de secciones FAQ/Contacto/Local al scrapear para que los generadores tengan más datos | Fix real y sostenible | Requiere más análisis DOM | **PRINCIPAL** |
| **B. Ajustar required_confidence en catálogo** | `faq_page.required_confidence` ya es 0.5 (asset_catalog.py L85). El threshold 0.7 viene del gate, no del catálogo. Alinear. | Rápido | Riesgo de aceptar assets de dudosa calidad | **Condicional** |
| **C. Flag "parcial" en vez de número bajo** | Reportar estado `PARTIAL` con explicación contextual | Honestidad comercial | Cambio en formatter | **Complemento** |

---

## Síntesis Ejecutiva de Decisiones (CORREGIDA)

| Issue | Severidad | Recomendación Principal | Esfuerzo | Bloquea publicación |
|-------|-----------|------------------------|----------|---------------------|
| 1 — Gate no reconoce whatsapp existente | 🔴 Bloqueante | Fix gate integration (no detector) | Media | **SÍ** (necesario pero insuficiente) |
| 2 — "13%" artifact de pricing | 🟡 Semántico | Eliminar línea 128 (trazabilidad real ya en línea 129) | Baja | NO |
| 3 — Confidence bajo (0.5) | 🔴 Co-bloqueante | Enriquecer DOM para optimization_guide Y/O faq_page | Media | **SÍ** (co-requerido con Issue 1) |

**Para desbloquear publication readiness**:
1. **OBLIGATORIO (Issue 1)**: Fix del publication gate para reconocer whatsapp_button como present_in_production → alignment sube a 75%
2. **OBLIGATORIO (Issue 3)**: Elevar confidence de UNO de {optimization_guide, faq_page} a ≥ 0.7 → alignment sube a ≥ 87.5%
3. **RECOMENDADO (Issue 2)**: Eliminar o corregir línea 128 del documento

**Secuencia**: P1 + P2 en paralelo → re-ejecutar v4complete → verificar alignment ≥ 80%.

---

## Métricas Comparativas

| Métrica | Baseline (v4.56.0) | Post-Fix (v4.57.0) | Delta |
|---------|-------------------|---------------------|-------|
| Coherence | 0.83 | 0.83 | → |
| ROI en doc | Dual (0.45X + 2.10X) | Único (2.10X) | ✅ Fix |
| % fuga | 14% (wrong) | 10.7% (correct) | ✅ Fix |
| Assets deprecados | 4 | 0 | ✅ Fix |
| "13% número mágico" | Sí (aislado) | En fórmula (parcial) | ⚠️ Partial — VER ERROR 2 |
| Piloto/CAPEX/Garantía | No | Sí | ✅ Fix |
| Gates pasados | Unknown | 10/11 | ⚠️ VERIFICADO: no 9/10 |
| Publication ready | Unknown | NOT_READY | ❌ Bloqueado |

---

## Errores del Diagnóstico Previo (Auditoría 2026-05-28)

| # | Error | Decía | Realidad (evidencia viva) |
|---|-------|-------|--------------------------|
| 1 | Causa raíz WhatsApp | "Falso negativo del detector" | Detector FUNCIONA (SitePresenceChecker skipped asset con EXISTS). Bug es del gate. |
| 2 | "13% del dolor" | Factor de fórmula | Artifact de `pain_ratio` (0.1361) en financial_scenarios.json |
| 3 | Gates pasados | "9/10" | 10/11 (8 PASSED + 2 WARNING con passed=true) |
| 4 | optimization_guide | "Ausente" | Generado con confidence 0.5 (low_quality, no ausente) |
| 5 | Issue 3 severidad | "Warning, no bloqueante" | Co-bloqueante (alignment 75% con Issue 1 fixeado sigue < 80%) |

---

## Contexto Técnico para Planificación (Nueva Sesión)

### Ground Truth Verificado por Usuario
- **URL**: https://hotelcastillareal.com/
- **WhatsApp**: ✅ PRESENTE (botón visible en sitio)
- **v4complete SitePresenceChecker**: ✅ CORRECTAMENTE detectó EXISTS (asset_generation_report.json)

### Archivos de Evidencia Disponibles
- `/mnt/c/Users/Jhond/Github/iah-cli/evidence/roicriii-fase-6/`
  - `01_DIAGNOSTICO_Y_OPORTUNIDAD_20260528_151028.md`
  - `02_PROPUESTA_COMERCIAL_20260528_151039.md`
  - `gate_report_20260528_151039.json` ← **fuente de verdad para alignment**
  - `asset_generation_report.json` ← **fuente de verdad para skipped/generated**
  - `coherence_validation.json` (pre: 0.83)
  - `coherence_validation_post_gen.json` (post: 0.81)
  - `audit_report_20260528_151025.json`
  - `financial_scenarios_20260528_151025.json` ← **fuente de truth para pain_ratio (0.1361)**
  - `pain_ledger.json`

### Archivos de Código a Inspeccionar

**Para Issue 1 (gate integration)**:
- `modules/quality_gates/publication_gates.py` L797-1097 — `_proposal_asset_alignment_gate`
  - L855: `site_presence_report = assessment.get("site_presence_report")`
  - L857-881: Gate's SitePresenceChecker (fallback si no hay report pre-built)
  - L883-889: `verify_proposal_asset_alignment()` call
- `modules/asset_generation/proposal_asset_alignment.py` L157-330 — `verify_proposal_asset_alignment()`
  - L220-305: Missing asset handling con SitePresenceChecker
- `modules/assessment_builder.py` L228-232 — `with_site_presence()`
- `main.py` L2693-2700 — SitePresenceChecker invocation (pre-gate)

**Para Issue 3 (confidence)**:
- `modules/asset_generation/conditional_generator.py` — confidence calculation
- `modules/asset_generation/asset_catalog.py` L80-90 — `faq_page` (required_confidence=0.5)
- `modules/asset_generation/asset_catalog.py` L182-192 — `optimization_guide` (required_confidence=0.5)

### Supuestos para el Plan
- El fix de Issue 1 debe validarse re-ejecutando v4complete sobre Hotel Castilla Real
- Issue 3 DEBE resolverse junto con Issue 1 (co-bloqueante)
- Límite de iteraciones por sesión: 60 (convención del proyecto)

---

## Próximos Pasos para Nueva Sesión (Checklist de Planificación)

- [ ] **P1**: Inspeccionar `_proposal_asset_alignment_gate` (publication_gates.py L857-881) — por qué SitePresenceChecker del gate no marca whatsapp_button como present_in_production
- [ ] **P2**: Verificar si `assessment["site_presence_report"]` ya tiene whatsapp_button=EXISTS (main.py L2693-2700 lo genera para TODOS los PROPOSAL_SERVICE_TO_ASSET)
- [ ] **P3**: Implementar fix del gate — asegurar que assets skipped por ConditionalGenerator se reconozcan como present_in_production
- [ ] **P4**: Diagnosticar por qué optimization_guide y faq_page tienen confidence 0.5 — ¿faltan datos DOM? ¿el generador no tiene suficiente input?
- [ ] **P5**: Implementar fix de confidence para UNO de {optimization_guide, faq_page} (alcanza ≥ 0.7)
- [ ] **P6**: Corregir línea 128 de propuesta — eliminar "13% × 35%" (trazabilidad real ya en línea 129)
- [ ] **P7**: Re-ejecutar v4complete para Hotel Castilla Real y verificar alignment ≥ 80%
- [ ] **P8**: Verificar todos los gates post-fix y confirmar publication readiness (11/11 o 10/11 con solo WARNINGs)
- [ ] **P9**: Actualizar `dependencias-fases.md`, `06-checklist-implementacion.md`, y evidence (cascade completa)

**Dependencias**: P1 → P3 → P7 (secuencial para Issue 1). P4 → P5 → P7 (secuencial para Issue 3). P1+P4 pueden ir en paralelo. P6 independiente.

---

## Notas para el Agente en Nueva Sesión

1. **NO asumir** que WhatsApp fue "falso negativo". El detector FUNCIONA. El bug es del gate.
2. **Verificar citas técnicas verbatim** — no asumir nada sobre el código sin leerlo.
3. **Priorizar valor comercial** sobre métricas técnicas puras (convención del usuario).
4. **Antes de ejecutar cambios**, preguntar: "¿patch directo o plan primero?"
5. **Post-ejecución**: actualizar REGISTRY.md + checklist + evidence (cascade completa).
6. **Issue 1 Y Issue 3 son CO-BLOQUEANTES** — resolver solo uno NO desbloquea publicación.
7. El `pain_ratio` (0.1361) NO es un factor de fórmula de recuperación — es un indicador de pricing.
