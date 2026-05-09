# CONTEXTO: ANALISIS v4COMPLETE — TERMALES SANTA ROSA DE CABAL
## http://www.termales.com.co/ | Fecha: 2026-05-08
### Validado contra código vivo + sitio real | Versión: 2.0.0

---

## VEREDICTO EJECUTIVO

El pipeline v4complete para Termales Santa Rosa de Cabal entrega documentos **no publicables** por 3 razones estructurales: (1) la propuesta comercial muestra marcadores de template `{{if}}...{{endif}}` sin procesar — el motor `string.Template` es incompatible con la sintaxis Jinja2 del template V6, (2) el `coherence_validator` da un falso positivo en `promised_assets_exist` porque verifica el catálogo estático en vez de los assets realmente generados, y (3) el `monthly_report` miente sistemáticamente sobre entregas porque su tabla es una plantilla hardcodeada que siempre muestra "✅ Entregado". Adicionalmente, el pipeline reporta falsamente que el sitio no tiene WhatsApp ni Schema cuando AMBOS existen en producción.

De 12 hallazgos originales del contexto v1: 7 confirmados, 3 refinados, 2 refutados por evidencia del sitio real. Se descubrieron 6 hallazgos nuevos no detectados en el análisis original.

---

## HALLAZGOS VALIDADOS

### SECCIÓN A — CONFIRMADOS (código y outputs coinciden con el contexto original)

| ID | Hallazgo Original | Evidencia de Código/Sitio | Severidad |
|----|-------------------|---------------------------|-----------|
| A1 | 6 assets generados con confidence=0.5 | `asset_generation_report.json`: todos tienen `confidence_score: 0.5, can_use: True` | ALTA |
| A2 | 3 assets NO generados: optimization_guide, whatsapp_button, open_graph | `asset_catalog.py` L54, L176, L335: definidos como IMPLEMENTED. `asset_generation_report.json`: ausentes de `generated_assets`. | ALTA |
| A3 | monthly_report afirma "Botón WhatsApp ✅ Entregado" | `monthly_report_generator.py` L170-182: tabla HARDCODEADA. El generador nunca consulta `asset_generation_report.json`. SIEMPRE dice "✅ Entregado" para todo. | ALTA |
| A4 | llms_txt contiene `[PENDING_ONBOARDING: usp/description]` | `llmstxt_generator.py` L101: inyecta marcador cuando `hotel_data` no tiene `usp` ni `description`. | ALTA |
| A5 | Content Scrubber no detecta marcadores [PENDING*] | `modules/postprocessors/content_scrubber.py` L76-104: solo 5 reglas (region_placeholders, duplicate_currency, confidence_statement, mixed_language, generic_ai_phrases). NINGUNA busca `[PENDING_*]`. | ALTA |
| A6 | Tier C sin enriquecimiento — contenido genérico | Confirmado: el pipeline usa benchmarks regionales sin datos operativos del hotel. Sin onboarding previo, todos los assets son ESTIMATED (0.5). | MEDIA |
| A7 | FAQ genérica: 3 preguntas template sin especificidad | `faq_page` output: preguntas universales aplicables a cualquier hotel, sin referencia a termas, cascadas, spa, o experiencias únicas. | MEDIA |

### SECCIÓN B — REFINADOS (el contexto original era parcialmente correcto)

| ID | Claim Original | Realidad Verificada | Corrección |
|----|---------------|---------------------|------------|
| B1 | "Los tres scores de coherencia coinciden (0.891111)" | Diagnostic YAML header: `coherence_score: 0.8911111111111112` (L5 del .md). Gate report coherence gate: `value: 0.8911111111111112`. Coherence validation JSON: `overall_score: 0.89`. Los dos primeros coinciden EXACTAMENTE. El tercero está redondeado en el JSON (0.89 ≠ 0.891111...). | PROP-A SÍ funciona. La discrepancia es de presentación (redondeo en JSON), no de cálculo. |
| B2 | "7 servicios prometidos en la propuesta comercial" | La propuesta generada solo MUESTRA 4 servicios (líneas 44-49 del .md). `PROPOSAL_SERVICE_TO_ASSET` (`proposal_asset_alignment.py` L20-28) tiene 7. La propuesta visible al cliente y el contrato interno DIVERGEN. El generador (`_generate_dynamic_services_table`) filtra dinámicamente según pain_ids — muestra 4, pero el gate espera 7. | El contexto confunde lo que dice el MAPEO ESTÁTICO (7 servicios) con lo que MUESTRA la propuesta al cliente (4 servicios). Esto es un bug de diseño, no de documentación. |
| B3 | "Gate proposal_asset_alignment contradice READY_FOR_PUBLICATION" | `modules/quality_gates/publication_gates.py` L863: `passed=True, # WARNING, not blocking`. El gate es EXPLÍCITAMENTE diseñado como no bloqueante. `check_publication_readiness()` L1074-1075: `ready = len(blocking_gates) == 0`. Como `passed=True`, el gate no cuenta como bloqueante → `READY_FOR_PUBLICATION`. | No es un bug. Es una DECISIÓN DE DISEÑO documentada en el código. La pregunta correcta no es "¿por qué no bloquea?" sino "¿debería bloquear?" — es un debate de producto, no técnico. |

### SECCIÓN C — REFUTADOS (la evidencia del sitio real contradice el contexto)

| ID | Claim Original | Realidad en Producción | Evidencia |
|----|---------------|----------------------|-----------|
| C1 | "Sin Schema Hotel" / "no se detectó" | El sitio **SÍ tiene schema** JSON-LD. | `browser_console`: `ld_json_count: 1`. El pipeline reportó un FALSE NEGATIVE. |
| C2 | "Sin botón de WhatsApp" / "no hay WhatsApp en el sitio" | El sitio **SÍ tiene WhatsApp** con número real y botón visible. | `browser_console`: `wa.me/573012674459`, clases CSS `whatsapp-button` + `icon-whatsapp`, visible en footer. Número real: +57 301 267 4459. El pipeline produjo un FALSE NEGATIVE en la detección de presencia. |

### SECCIÓN D — NUEVOS HALLAZGOS (no detectados en el análisis original)

#### D1 [CRÍTICO] — Template engine incompatible: `{{if}}...{{endif}}` visible en propuesta

**Síntoma**: `02_PROPUESTA_COMERCIAL_20260508_175032.md` L93-98 y L119-121 muestran marcadores de template sin procesar:
```
{{if financial_evidence_tier == "C"}}
> **⚠️ Advertencia:** Nivel de evidencia: Tier C...
{{endif}}
```

**Causa raíz**: `modules/commercial_documents/v4_proposal_generator.py` L1103-1106:
```python
def _render_template(self, template_content, data):
    template = Template(template_content)  # string.Template
    return template.safe_substitute(data)   # SOLO soporta $var / ${var}
```
El template V6 (`propuesta_v6_template.md` L85-90) usa sintaxis tipo Jinja2 (`{{if cond}}...{{endif}}`) pero el motor es `string.Template` que NO procesa condicionales. Los bloques pasan intactos al output.

**Impacto**: Todo cliente Tier C recibe un documento comercial con marcadores de código crudos visibles.

**Archivos involucrados**:
- `modules/commercial_documents/v4_proposal_generator.py:1103-1106` (motor)
- `modules/commercial_documents/templates/propuesta_v6_template.md:85-90,111-113` (template)

#### D2 [CRÍTICO] — coherence_validator da PASS falso en `promised_assets_exist`

**Síntoma**: `coherence_validation.json` reporta `promised_assets_exist: score=1.0` ("Todos los assets prometidos están implementados"). Pero `gate_report.json` reporta `proposal_asset_alignment: value=0.0` ("3 missing"). Dos componentes del mismo pipeline producen datos CONTRADICTORIOS.

**Causa raíz**: `modules/commercial_documents/coherence_validator.py` L518-525:
```python
for service_name, asset_type in PROPOSAL_SERVICE_TO_ASSET.items():
    if not is_asset_implemented(asset_type):  # ← Verifica CATÁLOGO ESTÁTICO
        missing_service_assets.append(...)
```
`is_asset_implemented()` (de `asset_catalog.py`) verifica si el asset está DEFINIDO en el catálogo, NO si fue GENERADO en esta ejecución. Los 3 assets faltantes están en el catálogo como `IMPLEMENTED` → coherence dice "todo bien". Pero el gate (`publication_gates.py:795`) verifica `assessment.get("generated_assets")` — los assets REALMENTE generados → 3 faltantes.

**Dos fuentes de verdad para la misma pregunta producen respuestas opuestas.**

**Archivos involucrados**:
- `modules/commercial_documents/coherence_validator.py:518-538` (usa catálogo)
- `modules/quality_gates/publication_gates.py:795-828` (usa generated_assets)
- `modules/asset_generation/asset_catalog.py:54,176,335` (catálogo estático)

#### D3 [ALTO] — monthly_report es 100% plantilla estática

**Síntoma**: La tabla "Resumen de Assets Entregados" siempre muestra 9 assets como "✅ Entregado", incluyendo assets que NUNCA se generaron (Botón WhatsApp, Geo Playbook, Voice Assistant Guide) y assets con nombres que no coinciden con el catálogo real.

**Causa raíz**: `modules/asset_generation/monthly_report_generator.py` L170-182 es texto hardcodeado en el método `generate()`. El generador NUNCA lee `asset_generation_report.json`. No es que "infle" estados — es que la tabla es ESTÁTICA. El mismo output para cualquier hotel, cualquier ejecución.

**Archivos involucrados**:
- `modules/asset_generation/monthly_report_generator.py:170-182` (tabla hardcodeada)

#### D4 [ALTO] — WhatsApp detection FALSE NEGATIVE sistémico

**Síntoma**: El pipeline reporta que el sitio no tiene WhatsApp ni Schema. Ambos existen en producción.

**Causa raíz**: `modules/quality_gates/publication_gates.py` L816-821:
```python
except Exception as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"SitePresenceChecker error: {e}")
    site_presence_report = None  # ← Silencio: se asume "no detectado = no existe"
```
El `SitePresenceChecker` falla silenciosamente. El catch-all `except Exception` traga cualquier error y el gate procede como si el asset no existiera en producción. Esto produce:
- Diagnóstico dice "no tiene WhatsApp" (falso)
- Propuesta dice "No hay botón de WhatsApp" (falso)
- monthly_report recomienda "Implementar botón WhatsApp" (redundante)
- Gate marca `whatsapp_button` como "missing" (falso — está `present_in_production`)

**Archivos involucrados**:
- `modules/quality_gates/publication_gates.py:798-821` (invocación + catch-all)
- `modules/asset_generation/site_presence_checker.py` (checker que falla)

#### D5 [MEDIO] — Teléfono placeholder en propuesta

**Síntoma**: `02_PROPUESTA_COMERCIAL...md` L233: `WhatsApp: +57 300 000 0000`. El teléfono real es `(606) 3653421` y el WhatsApp real es `+57 301 267 4459`.

**Causa**: Template no recibe el dato real del hotel porque no hay onboarding (Tier C). El valor por defecto es un placeholder genérico.

#### D6 [MEDIO] — IAO Transparency muestra "—" en todos los valores

**Síntoma**: Propuesta L174-184: queries=0, costos="— USD", total="— USD". La sección de transparencia está vacía pero no se detecta como problema.

**Causa**: Sin datos de onboarding, el generador no tiene valores reales paraIAO queries ni costos. El Content Scrubber no tiene regla para detectar placeholders "—".

---

## CAUSAS RAÍZ (CONSOLIDADAS Y CORREGIDAS)

```
CLIENTE RECIBE DOCUMENTO CON MÚLTIPLES ERRORES
│
├── R1: Template engine incompatible [NUEVO - D1]
│   └── string.Template no procesa {{if}} (v4_proposal_generator.py:1106)
│       └── Template V6 usa sintaxis Jinja2 incompatible con el motor
│
├── R2: Coherence validator usa fuente de verdad equivocada [NUEVO - D2]
│   └── is_asset_implemented() mira catálogo estático, no generated_assets
│       └── SOL-2 unificó PROPOSAL_SERVICE_TO_ASSET pero no la fuente de verificación
│
├── R3: monthly_report es plantilla estática [AMPLIADO - D3]
│   └── Tabla "Assets Entregados" hardcodeada, nunca lee asset_generation_report.json
│       └── El generador no es data-driven; miente por diseño, no por bug
│
├── R4: SitePresenceChecker falla silenciosamente [NUEVO - D4]
│   └── catch-all except Exception traga errores (publication_gates.py:816)
│       └── "No detectado" se interpreta como "no existe"
│
├── R5: Content Scrubber sin regla para [PENDING*] [CONFIRMADO - A5]
│   └── Solo 5 reglas, ninguna busca marcadores de desarrollo
│
├── R6: Gate WARNING no bloquea por diseño, no por bug [CORREGIDO - B3]
│   └── publication_gates.py:863: passed=True, "# WARNING, not blocking"
│       └── Cambiar requiere decisión de producto, no fix técnico
│
└── R7: Generadores no acceden a datos contextuales [CONFIRMADO - A6, A7]
    ├── indirect_traffic no lee audit_context
    ├── FAQ no extrae datos del sitio
    └── llms_txt inyecta [PENDING_ONBOARDING] sin validación posterior
```

---

## SOLUCIONES (CORREGIDAS CON PATHS REALES)

### Prioridad 1 — Bugs que afectan al cliente final

**FIX-1: Procesar condicionales en template engine**
- Archivo real: `modules/commercial_documents/v4_proposal_generator.py:1103-1106`
- Cambio: Reemplazar `string.Template.safe_substitute()` con pre-procesador que evalúe `{{if cond}}...{{endif}}` antes del substitute. Alternativa ligera: regex pre-pass que elimine bloques cuando la condición no se cumple.
- NOTA: El archivo indicado en el contexto original (`modules/validation/gate_validator.py`) no existe.

**FIX-2: coherence_validator debe verificar generated_assets, no el catálogo**
- Archivo real: `modules/commercial_documents/coherence_validator.py:518-538`
- Cambio: `_check_promised_assets_exist()` debe recibir `generated_assets` del pipeline y verificar contra ellos, no contra `is_asset_implemented()` que solo mira el catálogo estático. Si 3 de 7 assets no se generaron, el score debe reflejarlo (4/7 = 0.57, no 1.0).

**FIX-3: monthly_report data-driven**
- Archivo real: `modules/asset_generation/monthly_report_generator.py:170-182`
- Cambio: Reemplazar tabla hardcodeada por generación dinámica que lea `asset_generation_report.json`. Solo marcar "✅ Entregado" assets con `can_use=True`. Marcar "⚠️ No disponible" los que no se generaron. Usar nombres del catálogo real (no "Geo Playbook", "Voice Assistant Guide" que no existen en el catálogo).
- NOTA: El archivo indicado en el contexto original (`generators/monthly_report_generator.py`) tiene path incorrecto.

**FIX-4: Content Scrubber — Rule 6 para [PENDING*]**
- Archivo real: `modules/postprocessors/content_scrubber.py:76-104`
- Cambio: Agregar `_fix_pending_markers()` como Rule 6. Regex: `\[PENDING_[A-Z_]+\]`. Si se detecta, el documento debe marcarse como NO publicable (scrub_result con `block_publication=True`).
- NOTA: El archivo indicado en el contexto original (`modules/content_scrubber.py`) tiene path incorrecto.

**FIX-5: SitePresenceChecker hardening**
- Archivo real: `modules/quality_gates/publication_gates.py:816-821`
- Cambio: El `except Exception` debe: (a) loguear el error completo con traceback, (b) retornar `presence_status: "unknown"` en vez de `None`. Si el checker falla, el gate debe reportar "indeterminado" y no asumir "no existe".
- El `SitePresenceChecker` mismo (`modules/asset_generation/site_presence_checker.py`) debe investigarse para entender por qué falla en Termales.

### Prioridad 2 — Mejoras de enriquecimiento

**FIX-6: indirect_traffic lea audit_context**
- El generador debe consultar `audit_report.json` antes de recomendar acciones. Si GBP tiene >1000 reseñas, NO sugerir "reclama tu GBP" ni "optimiza tu perfil".

**FIX-7: FAQ generator extraiga datos del sitio**
- Antes de generar FAQ, hacer web scraping de la página del hotel para extraer servicios reales (termas, spa, cascadas, experiencias, avistamiento de aves).

**FIX-8: llms_txt — Content Scrubber debe bloquear [PENDING_ONBOARDING]**
- Incluido en FIX-4. El marcador nunca debe llegar al cliente.

### Prioridad 3 — Policy y flujo (requiere decisión de producto)

**FIX-9: Gate proposal_asset_alignment — evaluar cambio de WARNING a BLOCKED**
- Archivo real: `modules/quality_gates/publication_gates.py:863`
- Cambio: `passed=False, status=GateStatus.BLOCKED` cuando `alignment_percentage < 0.5`. Esto es un cambio de POLICY, no un bugfix. El código actual es intencional.

**FIX-10: Onboarding gate para Tier C**
- Si `financial_evidence_tier == "C"`, la propuesta debe marcarse como "Preliminar" y requerir datos reales para activación.

---

## ARCHIVOS VERIFICADOS

### Outputs de la ejecución (todos existen en disco)
```
output/v4_complete/termales/v4_audit/coherence_validation.json     → overall_score: 0.89 (redondeado)
output/v4_complete/termales/v4_audit/asset_generation_report.json  → 6 assets, todos confidence=0.5
output/v4_complete/termales/v4_audit/gate_report_20260508_175039.json → 9 gates, 3 WARNINGs
output/v4_complete/termales/v4_audit/geo_flow_result.json
output/v4_complete/termales/v4_audit/audit_report_20260508_175016.json
output/v4_complete/02_PROPUESTA_COMERCIAL_20260508_175032.md       → {{if}}...{{endif}} visible, 4 servicios
output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260508_175021.md → coherence_score: 0.8911111111111112
output/v4_complete/termales/llms_txt/ESTIMATED_llms_20260508_175021.txt → [PENDING_ONBOARDING]
output/v4_complete/termales/monthly_report/ESTIMATED_informe_mensual_20260508_175021.md → tabla hardcodeada
```

### Código fuente verificado
```
modules/commercial_documents/v4_proposal_generator.py:1103-1106   → _render_template con string.Template
modules/commercial_documents/templates/propuesta_v6_template.md:85 → {{if}} conditional blocks
modules/commercial_documents/coherence_validator.py:518-538        → is_asset_implemented() vs catálogo
modules/asset_generation/monthly_report_generator.py:170-182       → tabla hardcodeada
modules/postprocessors/content_scrubber.py:69-104                  → 5 reglas, sin PENDING detection
modules/quality_gates/publication_gates.py:760-873                 → proposal_asset_alignment gate (WARNING)
modules/quality_gates/publication_gates.py:1074-1075               → ready = len(blocking_gates) == 0
modules/asset_generation/proposal_asset_alignment.py:20-28         → PROPOSAL_SERVICE_TO_ASSET (7 entries)
modules/asset_generation/asset_catalog.py:54,176,335               → whatsapp_button, optimization_guide, open_graph = IMPLEMENTED
modules/asset_generation/llmstxt_generator.py:101                  → [PENDING_ONBOARDING] injection
```

### Sitio real (verificado con browser_navigate + browser_console)
```
https://termales.com.co/
  - WhatsApp: wa.me/573012674459, clases whatsapp-button + icon-whatsapp (VISIBLE)
  - Schema: 1 script JSON-LD presente
  - Teléfono real: (606) 3653421
  - WordPress: Contact Form 7, WPML, Sassy Social Share, CF7 Conditional Fields
  - Sin robots.txt, sin llms.txt
```

---

## MÉTRICAS DE ÉXITO (POST-REFACTOR)

1. `_render_template` procesa `{{if}}...{{endif}}` → propuesta sin marcadores crudos
2. `coherence_validator._check_promised_assets_exist()` refleja assets REALMENTE generados
3. `monthly_report` muestra tabla dinámica basada en `asset_generation_report.json`
4. `ContentScrubber` detecta y bloquea documentos con `[PENDING_*]`
5. `SitePresenceChecker` reporta `unknown` en vez de fallar silenciosamente
6. `whatsapp_button` se marca como `present_in_production` cuando existe en el sitio
7. Gate `proposal_asset_alignment` evaluado para cambio de WARNING→BLOCKED (decisión de producto)
8. Assets reflejan datos reales del hotel, no templates universales
9. Sin placeholders genéricos ("+57 300 000 0000", "—", "Por confirmar") en documentos finales

---

## MACRO-FASES SUGERIDAS (para próxima sesión de diseño de plan)

```
FASE-PRE — Saneamiento
├── Verificar CHANGELOG vs VERSION.yaml drift
├── Normalizar line endings (CRLF→LF)
└── run_all_validations.py --quick

FASE-1-A — Bugs críticos (template + coherence)
├── FIX-1: Procesar {{if}}...{{endif}} en template engine
├── FIX-2: coherence_validator usa generated_assets
└── Verificar con re-run v4complete en Termales

FASE-1-B — Bugs de contenido (scrubber + monthly_report)
├── FIX-4: Content Scrubber Rule 6 [PENDING*]
├── FIX-3: monthly_report data-driven
└── Verificar con re-run

FASE-2 — Detección y enriquecimiento
├── FIX-5: SitePresenceChecker hardening
├── FIX-6: indirect_traffic lee audit_context
├── FIX-7: FAQ extrae datos del sitio
└── Verificar con re-run

FASE-3 — Policy y gates (requiere decisiones de producto)
├── FIX-9: Evaluar proposal_asset_alignment WARNING→BLOCKED
├── FIX-10: Onboarding gate para Tier C
└── Documentar decisiones
```

---

## PRÓXIMO PASO — COPY-PASTE PARA NUEVA SESIÓN

```
Carga .opencode/context/ANALISIS_V4COMPLETE_TERMALES_20260508.md (v2.0.0 — validado).
Siguiendo iah-cli-context-audit-to-plan y phased_project_executor.md, diseña el plan de intervención
en .opencode/plans/ con fases FASE-PRE, FASE-1-A, FASE-1-B, FASE-2, FASE-3.
No implementes aún — solo diseña el plan con prompts por fase, dependencias, checklist y R3 scope.
```

---

*Contexto original: 2026-05-08*
*Validación exhaustiva contra código vivo + sitio real: 2026-05-08 (v2.0.0)*
*6 hallazgos nuevos (D1-D6) | 2 claims refutados (C1-C2) | 3 claims refinados (B1-B3) | 8 paths de archivo corregidos*
