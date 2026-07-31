
# Contexto: Falsa Confianza en Evidence Tier A — Contradicción Interna del Diagnóstico y Bloqueo del Pilar IAO

> **Origen**: Validación cruzada de dos diagnósticos v4complete para Zi One Luxury (07-28 Tier B vs 07-30 Tier A)
> **Versión actual**: v4.66.0
> **Hotel de referencia**: Zi One Luxury (https://zione.co/)
> **Severidad**: ALTA — el documento 07-30 afirma "GA4 verificado" cuando GA4 no está conectado, creando una contradicción interna y un riesgo reputacional si se entrega al cliente
> **Fecha del contexto**: 2026-07-30
> **Outputs de referencia**:
>   - `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260730_143715.md` (Tier A — CONTRADICTORIO)
>   - `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260728_180542.md` (Tier B — CONSISTENTE)
>   - `output/v4_complete/zione/v4_audit/financial_scenarios_20260730_143703.json`
>   - `output/v4_complete/zione/v4_audit/financial_scenarios_20260728_180531.json`
>   - `output/clientes/zi-one-luxury_onboarding.yaml` (datos reales Tier A, confidence 0.95)
> **ESTADO**: Validado contra código vivo (2026-07-30). 17/19 claims factuales (89.5%), 1 parcialmente obsoleto, 1 omisión de causa raíz. +6 hallazgos nuevos amplificados. Listo para implementación. El hotel DEBE suministrar credenciales GA4/GSC — el sistema no puede acceder autónomamente.
> **Validación**: Ejecutada por Hermes Agent contra código vivo en `/mnt/c/Users/Jhond/Github/iah-cli/`. Ver sección §15 para hallazgos amplificados.

---

## 1. PILARES AFECTADOS

Este bug impacta **3 de los 4 pilares del score de Visibilidad Digital**:

| Pilar | Impacto | Severidad |
|-------|---------|-----------|
| **IAO — AI Optimization** ("Para que te RECOMIENDEN") | **PRIMARIO y DIRECTO** — `ga4_indirect: 10pts` del CHECKLIST_IAO está permanentemente en `"no_evaluado"`. El score IAO queda CAPADO sin GA4. Además, el tier A falso dice "GA4 verificado" cuando la validación de tráfico indirecto de IA es imposible sin el cliente. | **ALTA** |
| **SEO Local** ("Para que te ENCUENTREN") | **SECUNDARIO** — GSC valida tráfico de búsqueda orgánica. Sin GSC, no se puede medir si las mejoras SEO están generando resultados reales. | MEDIA |
| **AEO — Answer Engine Optimization** ("Para que te CITEN") | **SECUNDARIO** — Los datos de GA4/GSC permitirían validar si los snippets y rich results están generando tráfico real. Sin ellos, el score AEO es puramente técnico. | MEDIA |
| GEO — Google Maps | No afectado directamente. | N/A |

### Evidencia en código vivo — IAO es el pilar directamente bloqueado

**CHECKLIST_IAO** (`v4_diagnostic_generator.py:198-206`):
```python
CHECKLIST_IAO: Dict[str, int] = {
    "citability_score":     20,
    "contenido_extenso":    15,
    "llms_txt_exists":      15,
    "crawler_access":       15,
    "brand_signals":        10,
    "ga4_indirect":         10,  # ← PERMANENTEMENTE "no_evaluado" sin GA4 del cliente
    "schema_advanced":      15,
}
```

**`_extraer_elementos_iao()`** (`v4_diagnostic_generator.py:2746-2747`):
```python
# GA4 indirect — PATCH-A: marcador explícito (detección real requiere acceso a GA4 API)
elementos["ga4_indirect"] = "no_evaluado"
```

**`ia_readiness_calculator.py:23`**: `WEIGHTS["ga4_indirect"] = 0.10` — el peso ya está definido, la arquitectura acepta `ga4_indirect_score` como parámetro opcional (línea 33). **El pipeline está listo para recibir el dato; solo falta que el cliente lo provea.**

---

## 2. EL BUG: CONTRADICCIÓN INTERNA EN EL DOCUMENTO 07-30

### Evidencia lado a lado

**Línea 84 (CTA post-fuga financiera) — HONESTA:**
```
> ✅ Datos operativos verificados. Para obtener la cifra exacta al peso,
> conecte Google Analytics 4 y Search Console para datos de tráfico real
> verificable.
```
→ Implica que GA4/GSC **NO** están conectados. Es una invitación a hacerlo. ✅

**Línea 215 (disclaimer de tier en anexo técnico) — FALSA:**
```
> ⚠️ Basado en datos de Google Analytics y Search Console verificados.

> Nivel de evidencia: Tier A
> - Tier A: Basado en Google Analytics + Search Console
```
→ Afirma que GA4/GSC **YA** están conectados y verificados. ❌

**Fuentes de Datos (línea 276-279) — CONFIRMA LA FALSEDAD:**
```
- Google Analytics 4: No configurado (GA4_PROPERTY_ID no configurado)
- Google Search Console: No configurado (agregue GSC_SITE_URL)
```

**El mismo documento le dice al cliente 3 cosas contradictorias sobre GA4.** Esto destruye la credibilidad del output.

### Comparación: el 07-28 era consistente

| Posición | 07-28 (Tier B) | 07-30 (Tier A) |
|----------|---------------|----------------|
| Línea 84 | "Complete el onboarding con sus datos reales" ✅ | "Conecte GA4 y Search Console" ✅ |
| Línea 215 | "Tier B — benchmarks regionales" ✅ | "Tier A — GA4 + Search Console verificados" ❌ |
| Fuentes | GA4: No configurado ✅ | GA4: No configurado ✅ |
| Consistencia | **Consistente** | **CONTRADICTORIO** |

---

## 3. CAUSA RAÍZ: DOS RUTAS DE CÓDIGO QUE NO COMPARTEN FUENTE DE VERDAD

### Ruta A — Línea 84 (consulta `analytics_data.use_ga4`)

`main.py:2297-2329` construye `analytics_data`:
```python
ga4_client = GoogleAnalyticsClient(property_id=ga4_hotel_property_id)
ga4_available = ga4_client.is_available()        # ← False (sin credenciales)
analytics_data = {
    "use_ga4": ga4_available,                     # ← False
    ...
}
```

`v4_diagnostic_generator.py:978`:
```python
ga4_enabled = analytics_data is not None and analytics_data.get("use_ga4", False)
# → False → el generador SABE que GA4 no está conectado
```

Esta ruta produce el CTA honesto de la línea 84.

### Ruta B — Línea 215 (consulta `financial_breakdown.evidence_tier`)

`scenario_calculator.py:480-504` — `_determine_evidence_tier()`:
```python
verified_sources = [s for s in [adr_src, occ_src, ch_src]
                   if s in ('onboarding', 'verified', 'industry_standard_15pct', 'user_provided')]
# Para Zi One 07-30: adr_src="user_provided", ch_src="onboarding" → len=2

if len(verified_sources) >= 2 and len(low_quality) == 0:
    return EvidenceTier.A    # ← NUNCA verifica si GA4 está conectado
```

`data_structures.py:134-135` — `EvidenceTier.A.disclaimer`:
```python
if self == EvidenceTier.A:
    return "Basado en datos de Google Analytics y Search Console verificados."
```

**El tier se asigna por calidad de datos operativos (onboarding), pero el disclaimer asume GA4+GSC. Las dos rutas nunca se sincronizan.**

### El `precision_tier` ya existe pero no se muestra

`financial_scenarios_20260730_143703.json`:
```json
{
  "evidence_tier": "A",
  "precision_tier": "C",
  "tier_explanation": {
    "evidence_tier": "A — Datos fuente",
    "precision_tier": "C — Cálculos derivados (C = supuestos de shift y boost IA no validados con datos reales)",
    "relationship": "evidence_tier B limita precision_tier a C: sin GA4, los supuestos no son validados empíricamente"
  }
}
```

El `precision_tier: "C"` es correcto. Pero **no se muestra en el documento** — solo se entierra en el JSON interno. Y el texto `relationship` ni siquiera se actualizó cuando el tier cambió de B a A (sigue diciendo "evidence_tier B").

**CAUSA RAÍZ del texto `relationship` stale** (validación 2026-07-30): `main.py:2099` es un **string hardcodeado**:
```python
# main.py:2099 — SIEMPRE dice "evidence_tier B" sin importar el valor real
'relationship': 'evidence_tier B limita precision_tier a C: sin GA4, los supuestos no son validados empíricamente'
```
No se construye dinámicamente con `_breakdown_dict.get('evidence_tier')`. Siempre dice "B". El fix debe usar f-string con el tier real, no un literal.

---

## 4. RESTRICCIÓN ARQUITECTÓNICA: EL HOTEL DEBE SUMINISTRAR LOS DATOS

### Por qué el sistema NO puede acceder a GA4/GSC autónomamente

GA4 (`google_analytics_client.py`) requiere:
1. `GA4_PROPERTY_ID` — el ID de propiedad GA4 del hotel (solo el hotel lo conoce)
2. `GA4_CREDENTIALS_PATH` — JSON de service account de Google Cloud (puede ser provisto por IA Hoteles)
3. El hotel debe AGREGAR la service account como usuario de su propiedad GA4

GSC (`google_search_console_client.py`) requiere:
1. `GSC_SITE_URL` — la URL verificada en Search Console (solo el hotel la conoce)
2. Credenciales de service account (mismas que GA4)
3. El hotel debe VERIFICAR la propiedad en GSC

**El código está implementado y listo** (`google_analytics_client.py:171 líneas`, `google_search_console_client.py:298 líneas`). El método `is_available()` devuelve `False` hasta que las credenciales estén configuradas.

### Qué puede hacer el sistema SIN el hotel (autónomo)

| Dato | Autónomo? |
|------|-----------|
| Scraping del sitio web | ✅ Sí |
| Google Business Profile (Places API) | ✅ Sí |
| Benchmarks regionales | ✅ Sí |
| Onboarding (si el hotel responde con datos operativos) | ✅ Sí (procesa el YAML) |
| GA4 traffic data | ❌ No — requiere propiedad del hotel + OAuth |
| GSC search data | ❌ No — requiere propiedad verificada + OAuth |
| Datos de campo (Core Web Vitals) | ❌ No — requiere credenciales |

### Conclusión: Tier A real es cliente-gateado, no automatizable

El sistema puede escalar autónomamente de Tier C → Tier B → Tier B+, pero **el salto a Tier A requiere cooperación del hotel**. Esto es inherente al modelo de seguridad de Google, no una limitación del código.

---

## 5. LAS TRES CONDICIONES PARA EL FIX

### Condición 1 — Fuente de verdad unificada

**Problema**: La línea 84 y la línea 215 consultan hechos diferentes (`analytics_data.use_ga4` vs `financial_breakdown.evidence_tier`). Deben consultar LA MISMA fuente.

**Fix**: `_determine_evidence_tier()` debe recibir `ga4_available` y `gsc_available` como inputs. Sin GA4+GSC conectados, NUNCA debe devolver `EvidenceTier.A`, independientemente de la calidad del onboarding.

```python
# scenario_calculator.py — propuesta
def _determine_evidence_tier(self, hotel_data: HotelFinancialData) -> EvidenceTier:
    sources = self._trace_data_sources(hotel_data)
    ...
    ga4_enabled = getattr(hotel_data, 'ga4_enabled', False)
    gsc_enabled = getattr(hotel_data, 'gsc_enabled', False)
    has_onboarding = any(s in ('onboarding', 'user_provided') 
                         for s in [adr_src, ch_src])

    if ga4_enabled and gsc_enabled:
        return EvidenceTier.A           # GA4+GSC real

    if has_onboarding:
        return EvidenceTier.B_PLUS      # NUEVO: datos operativos reales, 
                                         # proyecciones con supuestos
    ...
```

### Condición 2 — El tier debe reflejar GA4/GSC real, no solo onboarding

**Problema**: `EvidenceTier.A` está definido como "GA4 + GSC conectados" (enum docstring) pero se asigna con ">= 2 fuentes verificadas" (onboarding/adr). Son criterios distintos.

**Fix**: Alinear el criterio de asignación con la definición del enum:

| Tier | Definición | Criterio de asignación |
|------|-----------|----------------------|
| **A** | GA4 + GSC conectados — datos y proyecciones verificables | `ga4_enabled AND gsc_enabled` |
| **B+** (NUEVO) | Onboarding verificado, proyecciones con supuestos conservadores | `has_onboarding AND NOT (ga4_enabled AND gsc_enabled)` |
| **B** | Benchmarks regionales + scraping | `NOT has_onboarding AND NOT low_quality_dominated` |
| **C** | Solo scraping básico, baja confianza | `low_quality_dominated` |

**Nuevo disclaimer para B+**:
```
Datos operativos verificados del hotel. Las proyecciones financieras usan
supuestos conservadores (shift 10%, IA boost 5%) no validados con tráfico real.
Conecte Google Analytics 4 y Search Console para cifras exactas al peso.
```

### Condición 3 — Gate de validación post-generación

**Problema**: El documento 07-30 pasó todos los gates (`gate_status: PASSED`, `coherence_score: 0.917`) a pesar de la contradicción interna. No existe un gate que detecte "dice Tier A pero también dice GA4 no configurado".

**Fix**: Agregar un gate de **coherencia interna de evidence tier** que:

1. Extraiga `financial_evidence_tier` del frontmatter del documento generado
2. Extraiga el texto de "Fuentes de Datos Usadas" (GA4: No configurado / GSC: No configurado)
3. Si `tier == "A"` Y (`GA4: No configurado` O `GSC: No configurado`) → **BLOQUEAR entrega**
4. Mensaje: "El documento afirma Tier A (GA4+GSC verificados) pero GA4/GSC no están configurados. Contradicción interna."

**Ubicación sugerida**: `modules/quality_gates/commercial_gate.py` — nuevo gate `CG-EVIDENCE-TIER-CONSISTENCY`.

---

## 6. MAPEO DE ARCHIVOS AFECTADOS (14 archivos)

### Archivos a MODIFICAR — Diagnóstico + ScenarioCalculator

| # | Archivo | Línea(s) | Cambio | Prioridad |
|---|---------|----------|--------|-----------|
| 1 | `modules/commercial_documents/data_structures.py` | 126-139 | Agregar `B_PLUS = "B+"` al enum `EvidenceTier` + nuevo disclaimer | **P0** |
| 2 | `modules/financial_engine/scenario_calculator.py` | 480-504 | `_determine_evidence_tier()` debe recibir `ga4_enabled`/`gsc_enabled`; sin GA4 → máx B+ | **P0** |
| 3 | `modules/financial_engine/scenario_calculator.py` | 438-478 | `calculate_breakdown()` debe pasar `ga4_enabled`/`gsc_enabled` desde `hotel_data` | **P0** |
| 4 | `modules/commercial_documents/data_structures.py` | 142-166 | `HotelFinancialData` dataclass: agregar campos `ga4_enabled: bool = False`, `gsc_enabled: bool = False` | **P1** |
| 5 | `main.py` | 2004-2017 | Construcción de `HotelFinancialData`: pasar `ga4_enabled=ga4_available`, `gsc_enabled=gsc_available` | **P1** |
| 6 | `modules/quality_gates/commercial_gate.py` | ~69-74 | Nuevo gate `CG-EVIDENCE-TIER-CONSISTENCY` que valide coherencia interna tier vs fuentes | **P1** |
| 7 | `modules/commercial_documents/v4_diagnostic_generator.py` | 1124-1141 | `_build_financial_placeholders()`: exponer `precision_tier` además de `evidence_tier` en el template | **P2** |
| 8 | `modules/commercial_documents/v4_diagnostic_generator.py` | 2746-2747 | `_extraer_elementos_iao()`: cuando `ga4_enabled=True`, calcular `ga4_indirect` en lugar de `"no_evaluado"` | **P2** |

### Archivos a MODIFICAR — Propuesta Comercial (NUEVOS — validación 2026-07-30)

| # | Archivo | Línea(s) | Cambio | Prioridad |
|---|---------|----------|--------|-----------|
| **9** | `modules/commercial_documents/v4_proposal_generator.py` | 943 | `'has_onboarding': 'False'` hardcodeado → debe inyectarse desde `main.py` según si `onboarding_data` existe | **P0** |
| **10** | `modules/commercial_documents/v4_proposal_generator.py` | 939-941 | El variable `financial_evidence_tier` se hereda correctamente de `financial_breakdown`, pero el texto de disclaimer fijo "usan benchmarks regionales" (línea 119 del output) debe ser condicional al tier real | **P1** |
| **11** | `main.py` | ~2550 (call a `proposal_generator.generate()`) | Pasar `has_onboarding = onboarding_data is not None` al generator | **P0** |
|| **12** | `modules/commercial_documents/v4_proposal_generator.py` | 1907 | `_get_adr_from_benchmarks()` usa `user_provided_adr=None` → debe recibir el ADR real del onboarding si existe (mismo patrón H1 de AUDIT-BUG-1-FORENSIC) | **P1** ⚠️ **PARCIALMENTE OBSOLETO** — H1-FIX ya aplicado: la función acepta `user_provided_adr: Optional[float]` con early-return si > 0 (línea 1914). El caller en línea 789 pasa `self._user_provided_adr`. Si el ADR ya fluye correctamente (caso Zi One: $290K), este archivo NO requiere modificación. Solo aplica si se descubre un flujo donde `_user_provided_adr` no esté seteado. |

### Archivos a MODIFICAR — Delivery System (NUEVOS — validación 2026-07-30)

| # | Archivo | Línea(s) | Cambio | Prioridad |
|---|---------|----------|--------|-----------|
| **13** | `modules/quality_gates/delivery_quality.py` | — | Agregar `CG-EVIDENCE-TIER-CONSISTENCY` al checklist de gates pre-delivery. El delivery_quality_report actual (5 gates, todos PASSED) no detecta contradicciones de tier. | **P1** |
| **14** | `main.py` | 3038 (delivery assembly) | Incluir `evidence_tier`, `precision_tier`, `ga4_available`, `onboarding_used` en el MANIFEST.json para trazabilidad post-mortem del delivery | **P2** |

### Archivos que se MANTIENEN (sin cambios)

| Archivo | Razón |
|---------|-------|
| `modules/analytics/google_analytics_client.py` | Ya implementado. `is_available()` funciona correctamente. |
| `modules/analytics/google_search_console_client.py` | Ya implementado. Requiere credenciales del hotel. |
| `modules/auditors/ia_readiness_calculator.py` | Ya acepta `ga4_indirect_score` como param opcional. Arquitectura lista. |
| `modules/financial_engine/scenario_calculator.py` (resto) | Las fórmulas de cálculo son correctas. El bug es de labeling, no de math. |
| `output/clientes/zi-one-luxury_onboarding.yaml` | Los datos operativos son reales y correctos (Tier A, confidence 0.95). |
| `modules/commercial_documents/v4_proposal_generator.py` (resto) | La curva de maduración, ROI, y lógica financiera son correctas. Solo se ajusta el wiring de `has_onboarding` y el disclaimer. |

---

## 7. IMPACTO EN EL SCORE IAO

### Situación actual (sin fix)

Zi One 07-30 tiene IAO = 50/100 — marcado como "✅ Superior" vs promedio regional de 20/100. Pero:

- `ga4_indirect` = `"no_evaluado"` → 0 de 10 pts
- El score IAO está efectivamente capado en 90/100 máximo
- Sin GA4, el sistema NO PUEDE validar si las recomendaciones de IA están generando tráfico real
- La etiqueta "Tier A: GA4 verificado" es una PROMESA INCUMPLIDA al hotel sobre lo que el score IAO realmente mide

### Después del fix (con Tier B+ honesto)

El diagnóstico diría:
```
> 📊 CALIDAD DE ESTE DIAGNÓSTICO
>
> ✅ Datos operativos: VERIFICADOS (34 hab, $290K ADR, 40% directo)
> ⚠️ Score IAO: CAPADO en 90/100 — el componente de tráfico IA (10pts)
>    requiere Google Analytics 4 para ser evaluado
>
> 📋 Para desbloquear el score completo:
> ☐ Conectar Google Analytics 4 → necesitamos su GA4 Property ID
> ☐ Conectar Search Console → necesitamos la URL verificada en GSC
```

### Después de que el hotel conecte GA4+GSC (Tier A real)

- `ga4_indirect` se calcularía con datos reales de tráfico → score IAO completo 0-100
- `precision_tier` subiría de C a B o A (dependiendo de la calidad de los datos de tráfico)
- El `evidence_tier` reflejaría fielmente "A = GA4+GSC conectados"
- El sistema sería 100% honesto con el hotel sobre lo que mide y lo que no

---

## 8. DISCLAIMERS Y CTAs — PLANTILLA HONESTA

### Tier A (GA4+GSC conectados)
```
> ✅ Basado en datos de Google Analytics 4 y Search Console verificados.
> Tráfico real, proyecciones calibradas con datos de su hotel.
```

### Tier B+ (NUEVO — Onboarding sin GA4/GSC)
```
> ✅ Datos operativos verificados de su hotel (habitaciones, ADR, ocupación, canal directo).
> ⚠️ Las proyecciones financieras usan supuestos conservadores (shift 10%, IA boost 5%)
> no validados con su tráfico real.
>
> 📋 Para cifras exactas al peso (72h):
> ☐ Conectar Google Analytics 4 → necesitamos su GA4 Property ID
> ☐ Conectar Search Console → necesitamos la URL verificada en GSC
```

### Tier B (Benchmarks regionales)
```
> ⚠️ Estimación basada en benchmarks regionales y datos de su web.
> Para mayor precisión, complete el onboarding con sus datos operativos
> y conecte Google Analytics 4.
```

### Tier C (Solo scraping)
```
> ⚠️ Estimación basada en datos limitados de su web.
> Recomendamos completar el onboarding y conectar Google Analytics 4
> para un diagnóstico preciso.
```

---

## 9. VERIFICACIÓN POST-IMPLEMENTACIÓN

### Tests a ejecutar

```bash
# 1. Unit test: _determine_evidence_tier con ga4_enabled=False → B+ (no A)
cd /mnt/c/Users/Jhond/Github/iah-cli
venv/Scripts/python.exe -m pytest tests/ -k "evidence_tier" -v

# 2. Unit test: _determine_evidence_tier con ga4_enabled=True + gsc_enabled=True → A
venv/Scripts/python.exe -m pytest tests/ -k "evidence_tier_ga4" -v

# 3. Integration test: v4complete con onboarding pero sin GA4 → genera Tier B+
venv/Scripts/python.exe main.py v4complete --url https://zione.co/ --force-new
# Verificar que el frontmatter diga financial_evidence_tier: "B+"

# 4. Gate test: CG-EVIDENCE-TIER-CONSISTENCY debe bloquear si tier=A pero GA4=False
venv/Scripts/python.exe -m pytest tests/quality_gates/ -k "evidence_tier_consistency" -v
```

### Checklist de verificación manual

- [ ] `financial_evidence_tier: "B+"` en el frontmatter del diagnóstico (no "A")
- [ ] El disclaimer en línea 215 ya NO dice "Google Analytics y Search Console verificados"
- [ ] El CTA en línea 84 es consistente con el tier mostrado en línea 215
- [ ] La sección "Fuentes de Datos" refleja honestamente GA4: No configurado
- [ ] El gate `CG-EVIDENCE-TIER-CONSISTENCY` bloquea la entrega si hay contradicción
- [ ] `precision_tier` aparece en el documento (no solo en el JSON interno)
- [ ] El score IAO muestra explícitamente que `ga4_indirect` está pendiente de GA4

---

## 10. CONTEXTO ARQUITECTÓNICO — Relación con otros contextos

| Contexto | Relación |
|----------|----------|
| `CONTEXT-ONBOARDING-INJECTION-GAP-2026-07-28.md` | El gap de inyección de onboarding fue RESUELTO (07-30 ya carga onboarding). Pero al resolverse, **expuso este bug**: el tier saltó de B a A sin que GA4 esté conectado. Este contexto es la CAPA SIGUIENTE del pipeline. |
| `Historico/AUDIT-BUG-1-FORENSIC-2026-07-22.md` | H3 (falsa confianza en ValidationSummary) es el MISMO patrón: `confidence=VERIFIED` derivado de existencia, no de provenance real. Este contexto extiende H3 al tier de evidencia. |
| `Historico/BUGS-ONBOARDING-ADR-TEMPLATE-2026-07-22.md` | El fix de inyección de onboarding (BUG-1) es prerequisito para que este contexto tenga sentido. Sin onboarding, el tier nunca hubiera llegado a A. |

---

## 11. RIESGOS

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| El hotel recibe un diagnóstico que dice "GA4 verificado" y pregunta "¿cómo accedieron a mi GA4?" | **ALTA** (con el código actual) | Crítico — pérdida de confianza, posible reclamo legal | No entregar diagnósticos Tier A hasta que el fix esté implementado |
| El fix rompe el tiering para hoteles que SÍ tienen GA4 | BAJA | Medio — hoteles con GA4 real bajarían a B+ | El gate check `ga4_enabled AND gsc_enabled` debe ser preciso; testear con hotel real que tenga GA4 |
| El nuevo tier B+ confunde a los vendedores | MEDIA | Bajo — es un tier nuevo en el vocabulario | Documentar en AGENTS.md y en la guía de ventas |
| La service account de Google Cloud no está creada | ALTA | Medio — el CTA "conecte GA4" no se puede cumplir | Crear la service account ANTES de enviar diagnósticos con CTAs de GA4 |

---

## 12. NOTAS PARA LA IMPLEMENTACIÓN

1. **No tocar `financial_scenarios.json` ni las fórmulas de cálculo** — los valores financieros son correctos. El bug es de labeling, no de math.

2. **El precision_tier ya existe** en el JSON (`financial_scenarios_*.json:precision_tier`). Solo hay que exponerlo en el template del diagnóstico. Es un cambio de 5 líneas en `v4_diagnostic_generator.py`.

3. **El `ia_readiness_calculator.py` ya está listo** para recibir `ga4_indirect_score`. Cuando el hotel conecte GA4, el pipeline de scoring IAO se completa sin cambios adicionales.

4. **El orden de implementación debe ser**: Condición 1 (unificar fuente) → Condición 2 (tier honesto) → Condición 3 (gate de validación). No se puede implementar el gate sin antes haber corregido el tiering.

5. **La service account de Google Cloud es un prerequisito operacional** para que el CTA "conecte GA4" sea accionable. Si no existe, el diagnóstico ofrecerá algo que no se puede cumplir.

---

## 13. HALLAZGOS EN LA PROPUESTA COMERCIAL (validación 2026-07-30)

La propuesta 07-30 tiene **3 bugs independientes** que no estaban en el análisis original del diagnóstico:

### 13.1 Bug P1 — `has_onboarding` hardcodeado a `False`

**Archivo**: `v4_proposal_generator.py:943`

```python
'has_onboarding': 'False',  # Conservative default; caller can override with actual value
```

**Efecto**: la propuesta SIEMPRE muestra CTAs de "complete el onboarding" aunque el hotel YA lo completó. Nadie sobreescribe este valor desde `main.py`.

**Evidencia en el documento (línea 119)**:
```
> ⚠️ Advertencia: Nivel de evidencia: A. Estas proyecciones usan benchmarks
> regionales. Para precisión exacta, ejecute el onboarding con datos reales.
```

Zi One YA tiene onboarding cargado (34 habitaciones, $290K ADR, 40% canal directo). La propuesta le dice que haga algo que ya hizo. **Confuso y contraproducente.**

**También en línea 121**:
```
> Los activos listados en esta propuesta se generan a partir de benchmarks
> regionales (Tier C) y datos públicos del sitio web.
```
Esto es falso: los datos financieros provienen de onboarding (Tier A), no de benchmarks.

### 13.2 Bug P2 — Contradicción "Tier A" + "benchmarks regionales"

Línea 119: "Nivel de evidencia: **A**" + "estas proyecciones usan **benchmarks regionales**"

Son dos claims mutuamente excluyentes en la misma oración. El tier A se hereda correctamente de `financial_breakdown` (vía `financial_evidence_tier` en línea 941), pero el texto del disclaimer es fijo y no se adapta al tier real.

### 13.3 Bug P3 — `_get_adr_from_benchmarks()` bypasses onboarding

**Archivo**: `v4_proposal_generator.py:1907`

```python
def _get_adr_from_benchmarks(self, region: str) -> Optional[float]:
    resolver = RegionalADRResolver()
    result = resolver.resolve(region=region, rooms=0, user_provided_adr=None)
    return result.adr_cop
```

Este es el **mismo patrón H1** documentado en `AUDIT-BUG-1-FORENSIC-2026-07-22.md`. La propuesta tiene su propio resolver de ADR que ignora el onboarding. Si el hotel tiene `adr_cop=290,000` por onboarding pero el benchmark regional es `$420,000`, la propuesta puede mostrar un ADR divergente del diagnóstico.

**Nota**: En el caso de Zi One 07-30, la propuesta muestra correctamente `$290,000 COP` (línea 38). Esto sugiere que la línea 1907 NO se ejecutó en este caso porque el ADR ya venía del diagnóstico. Pero el código muerto persiste y podría activarse en otro flujo.

---

## 14. HALLAZGOS EN EL DELIVERY SYSTEM (validación 2026-07-30)

### 14.1 El MANIFEST es ciego a la calidad del contenido

`deliveries/zione_20260730_MANIFEST.json`:
```json
{
  "version": "1.0.0",
  "hotel_id": "zione",
  "generated_at": "2026-07-30T14:37:15.593080",
  "package_type": "automated_delivery",
  "files": [
    {"name": "DIAGNOSTICO.md", "type": "diagnostic"},
    {"name": "PROPUESTA_COMERCIAL.md", "type": "proposal"},
    ...
  ]
}
```

**No incluye**: `evidence_tier`, `precision_tier`, `ga4_available`, `onboarding_used`, `coherence_score`, ni ninguna metadata de calidad. El manifest solo lista archivos — es imposible auditar post-mortem si un delivery contenía datos verificados o estimados.

### 14.2 El delivery_quality_report no tiene gate de coherencia de tier

`delivery_quality_report.json` — 5 gates, todos `"passed": true`:
- G7: asset coverage failure rate (0%)
- G9: proposal asset alignment (7/7)
- G8: asset specificity (avg confidence 0.88)
- EVIDENCE: coherence score 0.92
- (1 adicional)

**Ninguno verifica**: ¿el `evidence_tier` del frontmatter es coherente con las fuentes configuradas? El sistema entregaría un documento con Tier A falso sin advertirlo.

### 14.3 El commercial_gates_report SÍ bloqueó — pero por otra razón

```json
{
  "gate_id": "CG-ROI-NEGATIVE",
  "passed": false,
  "severity": "BLOCKING",
  "message": "Beneficio neto 6m negativo ($-1,906,530 COP) y ROI 0.36X"
}
```

El delivery fue bloqueado por ROI negativo — un problema financiero distinto (pain_ratio 7.24% es muy bajo). Pero **el sistema no detectó la contradicción de evidence tier**. Si el ROI fuera positivo, el delivery se habría enviado con Tier A falso.

### 14.4 Fix requerido en delivery

1. Agregar `CG-EVIDENCE-TIER-CONSISTENCY` al `delivery_quality.py` — mismo gate propuesto para `commercial_gate.py`, ejecutado también en pre-delivery
2. Enriquecer el MANIFEST.json con metadata de calidad:
```json
{
  "quality_metadata": {
    "evidence_tier": "A",
    "precision_tier": "C",
    "ga4_configured": false,
    "gsc_configured": false,
    "onboarding_used": true,
    "coherence_score": 0.917,
    "contradictions_detected": ["TIER_A_BUT_NO_GA4"]
  }
}
```
3. Si `contradictions_detected` no está vacío → `delivery_quality_report.status = "FAIL"`

---

## 15. HALLAZGOS AMPLIFICADOS (validación 2026-07-30 contra código vivo)

Validación exhaustiva ejecutada por Hermes Agent contra el código vivo en `/mnt/c/Users/Jhond/Github/iah-cli/`. Se verificaron 19 claims, 22 ubicaciones de código, 10 archivos de output en disco. 17/19 claims factuales (89.5%).

### 15.1 NUEVO-1 (CAUSA RAÍZ): Hardcoded relationship text en main.py:2099

```python
# main.py:2099 — SIEMPRE dice "evidence_tier B" sin importar el valor real
'relationship': 'evidence_tier B limita precision_tier a C: sin GA4, los supuestos no son validados empíricamente'
```

**Severidad**: MEDIA (afecta el JSON interno `financial_scenarios.json`, no el documento visible).  
**Impacto**: El `tier_explanation.relationship` en `financial_scenarios_20260730_143703.json:51` dice "evidence_tier B" cuando el tier real es A.  
**Fix**: Usar f-string: `f'evidence_tier {_breakdown_dict.get("evidence_tier", "C")} limita precision_tier a {_precision_tier}: ...'`

### 15.2 NUEVO-2: Comentario engañoso en v4_proposal_generator.py:944

```python
'has_onboarding': 'False',  # Conservative default; caller can override with actual value
```

**Severidad**: ALTA. El comentario dice "caller can override" pero búsqueda exhaustiva en todo el codebase muestra **CERO ocurrencias** de `has_onboarding` seteado a `'True'`. Nadie sobreescribe este valor. Es un TODO disfrazado de API.  
**Fix**: `main.py` debe pasar `'has_onboarding': str(onboarding_data is not None)` al generator.

### 15.3 NUEVO-3: Tres sistemas de precision_tier no unificados

| Sistema | Ubicación | Valores |
|---------|-----------|---------|
| `PrecisionTier` enum | `financial_evidence.py:74` | MEASURED / REGIONAL / ESTIMATED |
| `determine_precision_tier()` | `no_defaults_validator.py:79` | Strings "A"/"B"/"C" |
| `_precision_tier` string | `main.py:2051-2064` | String "C" default → override vía PrecisionValidator |

Son **TRES implementaciones independientes** de la misma métrica con diferentes conjuntos de valores. El enum en financial_evidence.py ni siquiera usa los mismos nombres que el resto del sistema.

**Severidad**: MEDIA (no causa bugs visibles pero es deuda arquitectónica que confunde futuros audits).  
**Fix**: Unificar en una sola fuente de verdad. Mantener `PrecisionTier` enum y que `determine_precision_tier()` devuelva miembros del enum.

### 15.4 NUEVO-4: Líneas 161-163 del template son hardcodeadas

```markdown
# diagnostico_v6_template.md:161-163
> - Tier A: Basado en Google Analytics + Search Console
> - Tier B: Basado en benchmarks regionales + datos web
> - Tier C: Basado en datos limitados de su web
```

Estas descripciones NO son condicionales. Siempre muestran las 3 definiciones aunque solo una aplique. Si se agrega `Tier B+`, el template debe actualizarse manualmente.

**Severidad**: BAJA (cosmético, pero crea inconsistencia si se agregan nuevos tiers).  
**Fix**: Agregar `- Tier B+: Datos operativos verificados, proyecciones con supuestos conservadores` al template.

### 15.5 NUEVO-5: precision_tier se inyecta en data dict pero el template NO lo renderiza

`v4_diagnostic_generator.py:1386` retorna `'precision_tier': precision_tier` pero el template `diagnostico_v6_template.md` no contiene `${precision_tier}`. El dato se computa (vía `PrecisionValidator.validate()`) y se inyecta en el dict, pero el template nunca lo muestra al cliente.

**Severidad**: BAJA (el dato existe en `financial_scenarios.json` pero no en el documento visible).  
**Fix**: Agregar `${precision_tier}` al template en la sección de evidencia (~línea 158-163).

### 15.6 NUEVO-6: La propuesta dice 3 tiers diferentes en el mismo documento

Output `02_PROPUESTA_COMERCIAL_20260730_143715.md`:

| Línea | Texto | Tier implicado |
|-------|-------|---------------|
| 119 | "Nivel de evidencia: **A**" | A (GA4 verificado) |
| 119 | "Estas proyecciones usan **benchmarks regionales**" | B (benchmarks) |
| 121 | "a partir de benchmarks regionales **(Tier C)**" | C (scraping) |

Tres tiers diferentes en 3 líneas consecutivas. Zi One tiene datos de onboarding (equivalente a B+), pero el documento dice A, B, y C en el mismo párrafo.

**Severidad**: ALTA (confunde al cliente y destruye credibilidad).  
**Fix**: Derivado de la Condición 2 (tier honesto). Cuando el tier sea B+, el disclaimer debe decir "Datos operativos verificados" sin mencionar "benchmarks regionales" ni "Tier C".

### 15.7 NUEVO-7: Service account de Google Cloud — prerequisito operacional

El contexto menciona este riesgo en §11 (línea 415). Verificación: `google_analytics_client.py` (171 líneas) y `google_search_console_client.py` (298 líneas) están implementados y listos. Pero `is_available()` siempre devuelve `False` porque:

1. `GA4_CREDENTIALS_PATH` no está configurado → service account JSON no existe
2. `GA4_PROPERTY_ID` solo puede proveerlo el hotel

**Severidad**: ALTA (el CTA "conecte GA4" en el diagnóstico no es accionable sin la service account).  
**Fix**: Crear la service account en Google Cloud Console y configurar `GA4_CREDENTIALS_PATH` en `.env` ANTES de enviar diagnósticos con CTAs de GA4.

### 15.8 Tabla de verificación de claims del contexto

| # | Claim | Ubicación verificada | Veredicto |
|---|-------|---------------------|-----------|
| 1 | CHECKLIST_IAO dict en :198-206 | `v4_diagnostic_generator.py:198-206` | ✅ FACTUAL |
| 2 | ga4_indirect = "no_evaluado" en :2747 | `v4_diagnostic_generator.py:2747` | ✅ FACTUAL |
| 3 | WEIGHTS["ga4_indirect"] = 0.10 en :23 | `ia_readiness_calculator.py:23` | ✅ FACTUAL |
| 4 | ga4_indirect_score Optional en :33 | `ia_readiness_calculator.py:33` | ✅ FACTUAL |
| 5 | analytics_data.use_ga4 en main.py:2297-2329 | `main.py:2306, 2324` | ✅ FACTUAL |
| 6 | ga4_enabled check en :978 | `v4_diagnostic_generator.py:978` | ✅ FACTUAL |
| 7 | _determine_evidence_tier en :480-504 | `scenario_calculator.py:499` | ✅ FACTUAL |
| 8 | EvidenceTier.A.disclaimer en :134-135 | `data_structures.py:135` | ✅ FACTUAL |
| 9 | HotelFinancialData sin ga4_enabled | `scenario_calculator.py:77-102` | ✅ FACTUAL |
| 10 | financial_scenarios.json tier A + precision C | `financial_scenarios_*.json:27,46` | ✅ FACTUAL |
| 11 | Contradicción líneas 84 vs 215 vs 276 | `01_DIAGNOSTICO_*_143715.md` | ✅ FACTUAL |
| 12 | has_onboarding='False' hardcodeado :943 | `v4_proposal_generator.py:944` | ✅ FACTUAL |
| 13 | Propuesta dice "benchmarks Tier C" + "Tier A" | `02_PROPUESTA_*_143715.md:119-121` | ✅ FACTUAL |
| 14 | delivery_quality_report sin gate de tier | `delivery_quality_report.json` | ✅ FACTUAL |
| 15 | commercial_gates_report CG-ROI-NEGATIVE | `commercial_gates_report.json` | ✅ FACTUAL |
| 16 | MANIFEST sin metadata de calidad | `MANIFEST.json` | ✅ FACTUAL |
| 17 | precision_tier no visible en template | `diagnostico_v6_template.md` | ✅ FACTUAL |
| 18 | relationship text stale en JSON | `financial_scenarios_*.json:51` | ✅ FACTUAL |
| 19 | _get_adr_from_benchmarks en :1907 | `v4_proposal_generator.py:1906-1919` | ⚠️ PARC. OBSOLETO (H1-FIX aplicado) |
| 20 | Causa raíz del relationship stale | `main.py:2099` (hardcodeado) | 🔍 OMITIDO en contexto original |

---

## Anexo A — Archivos Verificados en Este Análisis

- ✅ `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260730_143715.md` (300 líneas) — verificado line-by-line §2
- ✅ `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260728_180542.md` (300 líneas)
- ✅ `output/v4_complete/02_PROPUESTA_COMERCIAL_20260730_143715.md` (348 líneas) — verificado §13 + NUEVO-6
- ✅ `output/v4_complete/zione/v4_audit/financial_scenarios_20260730_143703.json` (52 líneas) — verificado §3 + §15.1
- ✅ `output/v4_complete/zione/v4_audit/financial_scenarios_20260728_180531.json` (52 líneas)
- ✅ `output/v4_complete/zione/v4_audit/delivery_quality_report.json` (62 líneas) — verificado §14.2
- ✅ `output/v4_complete/zione/v4_audit/commercial_gates_report.json` (30 líneas) — verificado §14.3
- ✅ `output/v4_complete/deliveries/zione_20260730_MANIFEST.json` (734 líneas) — verificado §14.1
- ✅ `output/v4_complete/deliveries/zione_20260728_MANIFEST.json` (614 líneas)
- ✅ `output/clientes/zi-one-luxury_onboarding.yaml` (19 líneas)
- ✅ `modules/commercial_documents/data_structures.py:126-166` (EvidenceTier, FinancialBreakdown) — verificado §2
- ✅ `modules/financial_engine/scenario_calculator.py:77-102, 438-504` (HotelFinancialData, _determine_evidence_tier, calculate_breakdown) — verificado §2-3
- ✅ `modules/commercial_documents/v4_diagnostic_generator.py:198-206, 978, 1386, 2746-2747` (CHECKLIST_IAO, ga4_enabled, precision_tier, ga4_indirect) — verificado §1-3
- ✅ `modules/commercial_documents/v4_proposal_generator.py:789, 939-944, 1906-1919` (has_onboarding, _get_adr_from_benchmarks) — verificado §13 + NUEVO-2
- ✅ `modules/auditors/ia_readiness_calculator.py:18-66` (WEIGHTS, IAReadinessInput) — verificado §1
- ✅ `modules/analytics/google_analytics_client.py` (171 líneas) — verificado §4
- ✅ `modules/analytics/google_search_console_client.py` (298 líneas) — verificado §4
- ✅ `main.py:2004-2017, 2051-2100, 2297-2329, 2978-3053` (HotelFinancialData, tier_explanation, analytics_data, delivery) — verificado §2-3, §14, NUEVO-1
- ✅ `modules/commercial_documents/templates/diagnostico_v6_template.md:156-163` — verificado NUEVO-4, NUEVO-5
- ✅ `modules/quality_gates/commercial_gate.py:194-240` — verificado §14.3
- ✅ `modules/financial_engine/financial_evidence.py:74` — verificado NUEVO-3
- ✅ `modules/financial_engine/no_defaults_validator.py:79` — verificado NUEVO-3
