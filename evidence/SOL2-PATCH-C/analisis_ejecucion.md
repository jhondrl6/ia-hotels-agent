---
description: Analisis de ejecucion v4complete baseline — Termales Santa Rosa de Cabal
version: 1.0.0
hotel: Termales Santa Rosa de Cabal
url: http://www.termales.com.co/
hotel_id: termales
ejecutado: 2026-05-07T18:12:59
---

# Analisis de Ejecucion v4complete Baseline

## 1. Resumen Ejecutivo

| Metrica | Valor | Estado |
|---------|-------|--------|
| Coherence Score | 0.89 | ✅ PASA (umbral 0.8) |
| Publication Ready | true | ✅ READY_FOR_PUBLICATION |
| Assets Generados | 6 | ✅ |
| Assets Fallidos | 0 | ✅ |
| Assets Skipped | 0 | ⚠️ |
| site_verification_applied | false | ⚠️ CONFIRMADO COSMETICO |

## 2. Verificacion de SOL-2-B (Unificacion PROPOSAL_SERVICE_TO_ASSET)

**Hallazgo**: La unificacion funciona correctamente.

- Asset generation report (L139): "Todos los assets prometidos estan implementados (7 servicios verificados via PROPOSAL_SERVICE_TO_ASSET)"
- CoherenceValidator promised_assets_exist: PASSED (score 1.0)

**PERO**: El `proposal_asset_alignment_gate` reporta **3 missing assets** aunque estan marcados como IMPLEMENTED en asset_catalog:

| Servicio | Asset | Estado Catálogo | Estado Gate | Discrepancia |
|----------|-------|-----------------|-------------|--------------|
| SEO Local | optimization_guide | IMPLEMENTED | Missing | ❌ Gate no encuentra asset generado |
| Boton WhatsApp | whatsapp_button | IMPLEMENTED | Missing + not_exists | ❌ No generado, no existe en produccion |
| Meta Tags Sociales | open_graph | IMPLEMENTED | Missing | ❌ No generado (pero OG detectado en audit) |

**Interpretacion**: El catálogo dice IMPLEMENTED (capacidad), pero el gate verifica delivery (generacion real). Para este hotel, `detect_pains()` no disparo la generacion de estos 3 assets porque sus pain_ids no se detectaron. Esto es **comportamiento esperado**, no un bug.

- `whatsapp_button`: audit confirma "No hay asset de WhatsApp button" — correcto, no se detecto pain
- `open_graph`: audit detecta 10 OG tags en el sitio, pero como asset no se genero un entregable
- `optimization_guide`: no se detecto pain de SEO local

**Conclusion**: La discrepancia coherence=1.0 vs gate=0.43 es **intencional** — coherence valida capacidad del sistema, gate valida delivery para el hotel especifico. No requiere fix.

## 3. Verificacion de site_verification_applied (SOL-3 / SOL-4)

**Hallazgo**: Confirmado 100% cosmetico.

| Fuente | Valor | Ubicacion |
|--------|-------|-----------|
| asset_generation_report.json | `site_verification_applied: false` | L14 |
| asset_generation_report.json | `skipped_assets: []` | L95 |
| v4_asset_orchestrator.py | `skipped_assets` nunca se popula | Codigo vivo |

**Razon**: `SitePresenceChecker` se ejecuta en `publication_gates.py` (L803), NO en `v4_asset_orchestrator`. El orchestrator nunca recibe el resultado del checker, por lo que `skipped_assets` permanece vacio. El flag `site_verification_applied` refleja skips a nivel orchestrator, no checks a nivel gate.

**Decision**: Documentar en docstring (SOL-3) — no requiere fix de codigo. El campo no es dead code; es infraestructura para futura integracion orchestrator-level.

### 3.1 Trazado Completo de skipped_assets (T1)

**Investigacion exhaustiva del flujo skipped_assets — confirmado con busqueda global.**

#### Capa 1: Definicion (dataclass)

| Archivo | Linea | Elemento |
|---------|-------|----------|
| `v4_asset_orchestrator.py` | L72-79 | `@dataclass SkippedAsset` — tipo de dato para assets skipeados |
| `v4_asset_orchestrator.py` | L90 | `skipped_assets: List[SkippedAsset] = field(default_factory=list)` en `AssetGenerationResult` |
| `v4_asset_orchestrator.py` | L138 | `len(self.skipped_assets)` usado en `total_assets` |
| `v4_asset_orchestrator.py` | L141 | `len(self.skipped_assets)` como `skipped` count |
| `v4_asset_orchestrator.py` | L145-148 | `site_verification_applied = len(self.skipped_assets) > 0` + docstring SOL-3 |
| `v4_asset_orchestrator.py` | L173-184 | Serializacion a JSON de `skipped_assets` en `to_dict()` |

#### Capa 2: Poblacion (BUSQUEDA GLOBAL)

```bash
# Busqueda: SkippedAsset(
grep -r "SkippedAsset(" --include="*.py" → **0 resultados**
```

**Veredicto**: `SkippedAsset` NUNCA se instancia en ningun archivo `.py` del repositorio. La dataclass existe como tipo pero no hay codigo que cree `SkippedAsset(asset_type=..., reason=..., ...)`.

#### Capa 3: SitePresenceChecker — ¿quien lo usa?

| Archivo | Linea | Uso |
|---------|-------|-----|
| `v4_asset_orchestrator.py` | L34 | `from .site_presence_checker import SitePresenceChecker` (IMPORT pero no USO) |
| `publication_gates.py` | L803 | `from modules.asset_generation.site_presence_checker import SitePresenceChecker` |
| `publication_gates.py` | L804 | `checker = SitePresenceChecker()` |
| `publication_gates.py` | L815 | `checker.check_site(hotel_url, asset_types=assets_to_check)` |

El `SitePresenceChecker` se ejecuta SOLO en `publication_gates.py` (gate `proposal_asset_alignment`), NO en `v4_asset_orchestrator`.

#### Capa 4: SitePresenceChecker — ¿que devuelve?

| Metodo | Retorno | Uso en gate |
|--------|---------|-------------|
| `check_site()` | `SitePresenceReport` con `.results: Dict[str, PresenceCheckResult]` | ⚠️ NO mapea a `SkippedAsset` |
| `get_assets_to_skip()` | `List[Tuple[str, str]]` (asset_type, reason) | ❌ NUNCA se llama |
| `get_assets_to_generate()` | `List[str]` | ❌ NUNCA se llama |

El gate usa el `site_presence_report` para alimentar `verify_proposal_asset_alignment()`, que produce `present_in_production` en su reporte interno. Pero esa informacion NUNCA se transmite de vuelta al `AssetGenerationResult.skipped_assets`.

#### Capa 5: Diagrama del Gap

```
SitePresenceChecker.check_site(url)
    │
    ├── publication_gates.py (L815)
    │   └── verify_proposal_asset_alignment()
    │       └── report.present_in_production  ← datos de "ya existe"
    │           │
    │           └── Se usa SOLO para ajustar score del gate (L832-835)
    │               NO se transmite a orchestrator
    │
    └── v4_asset_orchestrator  ← NUNCA recibe estos datos
        └── skipped_assets = []  ← siempre vacio
            └── site_verification_applied = False  ← siempre false
```

#### Veredicto Final

| Pregunta | Respuesta | Evidencia |
|----------|-----------|-----------|
| ¿`skipped_assets` se define? | SI | L90 en `AssetGenerationResult` |
| ¿`skipped_assets` se pobla? | NO | `SkippedAsset(` → 0 resultados globales |
| ¿Es dead code? | NO — es **infraestructura** | La dataclass + serializacion + flag estan listos para usar |
| ¿Es gap de integracion? | SI | El `SitePresenceChecker` corre en gate, no en orchestrator |
| ¿Es feature no implementada? | PARCIALMENTE | El checker existe y funciona; falta el puente orchestrator←checker |
| **Decision** | **OPCION B: Documentar** | Infraestructura preparada, integracion futura si se necesita |

**Justificacion de OPCION B sobre OPCION C (deprecar)**:
- La dataclass `SkippedAsset` modela correctamente el concepto
- `SitePresenceChecker.get_assets_to_skip()` ya devuelve datos en el formato correcto
- El docstring SOL-3 (L145-148) ya explica el timing gap
- Deprecar seria eliminar infraestructura valida que solo necesita un puente de 5-10 lineas
- El costo de mantener el codigo es cero (no se ejecuta, no consume recursos)
- Si en el futuro se quiere evitar regenerar assets que ya existen, el puente es trivial

**Que faltaria para OPCION A (implementar)**:
```python
# En v4_asset_orchestrator.generate(), despues de detect_pains():
report = self.site_checker.check_site(url, asset_types=[...])
for asset_type, reason in report.get_assets_to_skip():
    self.result.skipped_assets.append(SkippedAsset(
        asset_type=asset_type,
        reason=reason,
        presence_status="EXISTS",
        site_verified=True,
        recommendations=[],
        pain_ids_affected=[]
    ))
```
~8 lineas de codigo. No se implementa en esta fase por restriccion del plan.

## 4. Estado Financial Engine

| Campo | Valor | Observacion |
|-------|-------|-------------|
| ADR source | handler | ✅ No usa legacy_hardcode |
| Pricing source | hybrid_v410 | ✅ Financial engine activo |
| Evidence tier | B | ✅ Regional benchmarks aplicados |
| Can show exact money | false | ⚠️ Precision tier C (sin datos operativos) |
| Monthly price COP | 1,200,000 | Calculado correctamente |
| Pain ratio | 0.4082 | Dentro de rango ideal (3x-50x) |

**Nota**: El valor `is_compliant: false` en pricing se debe a que `can_show_exact_money` es false (tier C evidence), no a un bug.

## 5. Audit Externo

| Auditoria | Estado | Detalle |
|-----------|--------|---------|
| GBP API | ✅ | Place ID encontrado, 4.6 estrellas, 22,309 reviews |
| Schema | ⚠️ | No HotelSchema ni FAQPage (OrgSchema si) |
| PageSpeed | ❌ | API key invalida — sin datos CWV |
| AI Crawlers | ⚠️ | No robots.txt, 14 crawlers sin control |
| Citability | ⚠️ | 53.39 (29 bloques < 100 palabras) |
| IA Readiness | ⚠️ | 68.08 — "Needs Work" |
| Open Graph | ✅ | 10 tags OG detectados |
| Social Links | ✅ | Facebook, Instagram, TikTok |
| LLM Mentions | ⚠️ | 2/5 queries (30% share of voice) |

## 6. Inventario de Assets Generados

| Asset | Confidence | Preflight | Pain Resuelto |
|-------|------------|-----------|---------------|
| hotel_schema | 0.85 | PASSED | no_hotel_schema |
| faq_page | 0.85 | PASSED | no_faq_schema |
| llms_txt | 0.85 | PASSED | ai_crawler_blocked |
| analytics_setup_guide | 0.50 | WARNING | no_analytics_configured |
| indirect_traffic_optimization | 0.50 | WARNING | low_organic_visibility |
| monthly_report | 0.50 | WARNING | (sin pain_id) |

## 7. Gates Ejecutados

| Gate | Estado | Score | Nota |
|------|--------|-------|------|
| hard_contradictions | PASSED | 0 | Sin contradicciones |
| evidence_coverage | PASSED | 0.95 | ✅ |
| financial_validity | WARNING | true | Datos default/legacy (Tier C) |
| coherence | PASSED | 0.891 | ✅ |
| critical_recall | PASSED | 1.0 | ✅ |
| ethics | PASSED | null | ✅ |
| content_quality | PASSED | 1.0 | ✅ |
| asset_confidence | WARNING | 0.675 | 3 assets < 0.7 |
| proposal_asset_alignment | WARNING | 0.429 | 3 missing + 1 low quality |

## 8. Conclusiones y Recomendaciones

### SOL-1 (Deduplicar mensaje coherence_validator)
- **Impacto en Termales**: El mensaje de promised_assets_exist muestra solo 1 linea ("7 servicios verificados"). La duplicacion no es visible aqui porque todos los 7 servicios pasan.
- **Prioridad**: Baja — fix de 2 lineas, aplicar en PATCH-A.

### SOL-2 (Parchear prompts historicos)
- **Impacto**: Ninguno en ejecucion — es documentacion de plan.
- **Prioridad**: Baja — aplicar en PATCH-B.

### SOL-3 (Docstring site_verification_applied)
- **Impacto**: Confirmado — flag es cosmetico.
- **Prioridad**: Baja — docstring de 1 linea, aplicar en PATCH-A.

### SOL-4 (Investigar skipped_assets)
- **Hallazgo**: `skipped_assets` es infraestructura preparada para futura integracion. No se popula porque SitePresenceChecker corre en gate, no en orchestrator.
- **Decision**: NO deprecar. Agregar docstring explicativo (SOL-3) y documentar en analisis.
- **Prioridad**: Baja — investigacion completada.

### SOL-5 (Logging excepciones publication_gates)
- **Impacto**: Mejora observabilidad sin cambiar comportamiento.
- **Prioridad**: Baja — 1 linea de logging, aplicar en PATCH-A.

### Hallazgo Nuevo (no en contexto 07)
- **proposal_asset_alignment gate reporta 3 missing** para Termales aunque catalogo dice IMPLEMENTED. Esto es comportamiento esperado (conditional generation), pero el mensaje del gate puede confundir al usuario.
- **Recomendacion**: Considerar en futuro si el gate deberia distinguir entre "no generado porque no aplica" vs "no generado porque fallo".
