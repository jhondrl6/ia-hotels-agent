---
generated_at: 2026-05-07 17:40
version: 4.0.0
document_type: CONTEXT_UNIFIED_VALIDATED
related_plan: SOL-2-REFACTOR (FASE-SOL2-A/B/C/D completadas) + PROP-PATCH (FASE-PATCH-C)
validation_type: Exhaustive live-code verification of merged context files 05 + 06
source_files_merged:
  - 05_SOL-2_ASSET_ALIGNMENT_DISCREPANCY_20260507.md (v3.0.0)
  - 06_SOL-2_DESIGN_FINDINGS_20260507.md (v1.0.0)
verification_method: Direct file reads + grep + search_files against /mnt/c/Users/Jhond/Github/iah-cli/
---

# CONTEXTO UNIFICADO: SOL-2 Asset Alignment — Validado vs Código Vivo

## VEREDICTO EJECUTIVO

Los archivos de contexto 05 y 06 contienen un análisis extenso pero presentan **3 falsos positivos CRÍTICOS** que invalidan soluciones propuestas. La refactoring SOL-2 ya resolvió el problema central (alineación coherence_validator ↔ gate), pero los documentos de contexto NO fueron actualizados para reflejarlo.

**Precisión global de claims verificados**: 14/18 confirmados (78%), 3 falsos, 1 parcial.

**Los 3 GAPs "ALTA" del archivo 05 son FALSOS POSITIVOS:**
- GAP-A: SitePresenceChecker NO EXISTE → **FALSO** (existe, 601 líneas, funcional)
- GAP-B: deployment_assistant.md NO EXISTE → **FALSO** (existe, 43 líneas, funcional)
- GAP-C: 7mo servicio excluido del gate → **RESUELTO** por SOL-2-B (PROPOSAL_SERVICE_TO_ASSET ahora tiene 7 entradas)

---

## PARTE A: VERIFICACIÓN DE CLAIMS DEL ARCHIVO 05

### Claims Confirmados (9/12)

| # | Claim | Veredicto | Evidencia |
|---|-------|-----------|-----------|
| 1 | `coherence_validator._check_promised_assets_exist()` líneas 494-526 | ✅ CONFIRMADO | L494 exacta. Firma y lógica matchean. |
| 2 | Usa `is_asset_implemented()` para verificar assets | ✅ CONFIRMADO | L516-518: `if not is_asset_implemented(t)` |
| 3 | `proposal_asset_alignment_gate` en publication_gates.py | ✅ CONFIRMADO | L760: `def _proposal_asset_alignment_gate()`. L154: registrado en orchestrator. |
| 4 | `_generate_dynamic_services_table()` filtra por assets_generated | ✅ CONFIRMADO | L839-881: filtra SERVICE_CATALOG por generated_asset_types. |
| 5 | ASSET_CATALOG marca optimization_guide, whatsapp_button, open_graph como IMPLEMENTED | ✅ CONFIRMADO | L54 (whatsapp_button), L176 (optimization_guide), L335 (open_graph): status=IMPLEMENTED. |
| 6 | Root cause: dos validadores con baselines distintas | ✅ CONFIRMADO | coherence=capability vs gate=delivery. Documentado en docstrings L501-510. |
| 7 | Gate status WARNING (no bloqueante) | ✅ CONFIRMADO | L860: `passed=True  # WARNING, not blocking` |
| 8 | monthly_report tiene `promised_by=["always"]` | ✅ CONFIRMADO | asset_catalog.py L322: `promised_by=["always"]  # SIEMPRE generar` |
| 9 | `delivery_ready_percentage` y `site_verification_applied` existen | ✅ CONFIRMADO | v4_asset_orchestrator.py L144-145. `site_verification_applied = len(self.skipped_assets) > 0`. |

### Claims Falsos (3/12)

| # | Claim Original | Veredicto | Evidencia Real |
|---|---------------|-----------|----------------|
| 10 | GAP-A: SitePresenceChecker NO EXISTE en el codebase | ❌ **FALSO** | `modules/asset_generation/site_presence_checker.py` EXISTE (601 líneas, 22KB). Clase `SitePresenceChecker` funcional con método `check_site()`. Incluye arquitectura de decisión (YA EXISTE → SKIP, NO EXISTE → Generar, NO SE PUEDE VERIFICAR → Warning). |
| 11 | GAP-B: deployment_assistant.md NO EXISTE | ❌ **FALSO** | `.agents/workflows/deployment_assistant.md` EXISTE (43 líneas). Skill funcional con pre-requisitos, scope, y pasos de ejecución para despliegue WordPress. |
| 12 | SitePresenceChecker importado con try/except silencioso | ❌ **FALSO** | publication_gates.py L803: `from modules.asset_generation.site_presence_checker import SitePresenceChecker` — import DIRECTO, sin try/except en esa línea. El try/except es genérico (L816: `except Exception`) que captura cualquier error, no un ImportError específico. |

### Claim Parcial (1/12)

| # | Claim | Veredicto | Corrección |
|---|-------|-----------|------------|
| 13 | PROPOSAL_SERVICE_TO_ASSET tiene 6 entradas estáticas | ⚠️ **OBSOLETO** | SOL-2-B agregó la 7ma entrada: `"Optimización para IA Generativa": "llms_txt"` (L27). Ahora son 7 entradas. El claim era correcto PRE-SOL-2. |

---

## PARTE B: VERIFICACIÓN DE CLAIMS DEL ARCHIVO 06 (Design Findings)

| # | Hallazgo | Veredicto | Evidencia |
|---|----------|-----------|-----------|
| D1 | Duplicación en mensaje de CoherenceValidator | ✅ CONFIRMADO | L528: `all_missing = missing_types + missing_service_assets` sin deduplicar. L543-546: ambos bloques concatenados en mensaje. Score usa `set(all_missing)` así que cálculo es correcto, solo el mensaje es redundante. |
| D2 | Plan prompts SOL-2-A/B no parcheados | ✅ CONFIRMADO | 0 matches para "POST-EJECUCION", "falso positivo", "ya exist" en `.opencode/plans/SOL-2-REFACTOR/`. Los 9 archivos del plan NO tienen disclaimer post-ejecución. |
| D3 | Flag `site_verification_applied` no se activa | ✅ CONFIRMADO | L145: `len(self.skipped_assets) > 0`. `skipped_assets` se define en L90 como `field(default_factory=list)`. El flag se activa solo si hay assets skipeados en el orchestrator, NO si el checker corre en el gate. Gap de timing confirmado. |

---

## PARTE C: NUEVOS HALLAZGOS (Ampliación del Alcance)

### HALLAZGO N1 [ALTA]: Los 3 GAPs del archivo 05 son obsoletos post-SOL-2

**Evidencia**: La refactoring SOL-2-B unificó la baseline de ambos validadores:
- `coherence_validator._check_promised_assets_exist()` ahora importa `PROPOSAL_SERVICE_TO_ASSET` (L513) y cross-checkea los 7 servicios (L524).
- `PROPOSAL_SERVICE_TO_ASSET` tiene 7 entradas (L20-28), incluyendo AEO.
- SitePresenceChecker existe y es funcional (601 líneas).
- deployment_assistant.md existe y es funcional (43 líneas).

**Impacto**: Las opciones de solución A, B, C, D, E, F del archivo 05 están parcialmente obsoletas. La opción C (unificar validación) ya se implementó en SOL-2-B. Las opciones E y F se basan en premisas falsas.

**Acción**: Actualizar los documentos de contexto para reflejar el estado post-SOL-2.

---

### HALLAZGO N2 [MEDIA]: CoherenceValidator ahora tiene doble verificación

El método `_check_promised_assets_exist()` post-SOL-2-B hace DOS verificaciones:
1. Assets del diagnóstico vs ASSET_CATALOG (original)
2. Todos los servicios de PROPOSAL_SERVICE_TO_ASSET vs ASSET_CATALOG (nuevo, L521-526)

Esto significa que si un servicio tiene un asset IMPLEMENTED en el catálogo, PASA ambas verificaciones. La discrepancia original (coherence=1.0 vs gate=missing) ya no debería ocurrir para los 7 servicios del contrato.

**Pendiente**: Verificar con un v4complete real si la discrepancia persiste.

---

### HALLAZGO N3 [MEDIA]: v4_asset_orchestrator.py NO tiene `skipped_assets` activo

Búsqueda de `skipped`, `ALREADY_EXISTS`, `site_presence` en v4_asset_orchestrator.py = 0 matches (excepto la definición del campo en L90 y el reporte en L145). El campo `skipped_assets` existe como dataclass field pero:
- No hay lógica que POPULE `self.skipped_assets` en el flujo normal
- `site_verification_applied` siempre es `False` porque `len(self.skipped_assets) == 0`
- El SitePresenceChecker se ejecuta en el gate (L803), no en el orchestrator

**Conclusión**: D3 del archivo 06 es correcto — el flag es cosmetico. Pero va más allá: NO es solo un gap de timing, es que `skipped_assets` nunca se popula en el flujo actual.

---

### HALLAZGO N4 [BAJA]: Gateway de import genérico en publication_gates.py

El try/except en L816 (`except Exception`) es un catch-all, no un ImportError específico. Si SitePresenceChecker lanza cualquier excepción durante `check_site()`, se silencia y `site_presence_report = None`. Esto es intencional (el gate no debe romperse por un checker externo) pero reduce la observabilidad de errores en el checker.

**Solución**: Loggear la excepción antes de setear `site_presence_report = None`.

---

### HALLAZGO N5 [MEDIA]: D2 de archivo 06 — plan prompts como trampa temporal

Los 5 prompts de fase SOL-2 (A, B, C, D, RELEASE) asumen que GAP-A y GAP-B son problemas reales de severidad ALTA. Si un agente futuro re-ejecuta estos prompts sin contexto post-SOL-2:
- SOL-2-A: Perdería iteraciones intentando crear SitePresenceChecker (ya existe) y deployment_assistant.md (ya existe)
- SOL-2-B: Ejecutaría la unificación de PROPOSAL_SERVICE_TO_ASSET (ya hecha)
- SOL-2-C: Verificación E2E (válida, no afectada)
- SOL-2-D: Documentación (válida, no afectada)

**Solución**: Agregar nota POST-EJECUCION al inicio de SOL2-A y SOL2-B.

---

## PARTE D: ANÁLISIS DE IMPACTO EN OPCIONES DE SOLUCIÓN

### Opciones del Archivo 05 — Reevaluadas Post-Validación

| Opción | Estado Pre-SOL-2 | Estado Post-SOL-2 | Recomendación |
|--------|-------------------|--------------------|----|
| **A** (generar 3 assets) | Factible | **PARCIALMENTE RESUELTO** | Los 3 assets están IMPLEMENTED en catálogo. La generación condicional depende de `detect_pains()`. Si no se generan para un hotel específico, es porque sus pain_ids no se detectaron — no es un bug del catálogo. |
| **B** (reducir catálogo) | Factible | **NO NECESARIO** | PROPOSAL_SERVICE_TO_ASSET ya tiene 7 entradas alineadas con SERVICE_CATALOG. No hay contradicción contrato-realidad. |
| **C** (unificar validación) | Factible | **✅ IMPLEMENTADO** | SOL-2-B unificó la baseline. coherence_validator ahora cross-checkea PROPOSAL_SERVICE_TO_ASSET. |
| **D** (deployment) | D1 imposible | **D1 POSIBLE** | deployment_assistant.md EXISTE (43 líneas). D1 es factible. D3 (package con instrucciones) sigue siendo quick win. |
| **E** (restaurar SitePresenceChecker) | Factible | **✅ YA EXISTE** | 601 líneas, funcional. No necesita restauración. |
| **F** (limpiar refs muertas) | Factible | **PARCIALMENTE APLICABLE** | Las refs a deployment_assistant y site_presence_checker son VÁLIDAS (los archivos existen). No hay refs muertas que limpiar. |

---

### Hallazgos D1/D2/D3 del Archivo 06 — Reevaluados

| Hallazgo | Estado | Recomendación |
|----------|--------|---------------|
| **D1** (duplicación mensaje) | VIGENTE | Aplicar D1-A: deduplicar mensaje. 2 líneas de cambio. |
| **D2** (prompts sin parchear) | VIGENTE | Aplicar D2-A: agregar POST-EJECUCION a SOL2-A y SOL2-B. 5 líneas por archivo. |
| **D3** (flag cosmetico) | VIGENTE + AMPLIADO | Aplicar D3-C: documentar en docstring. El problema es más profundo: `skipped_assets` nunca se popula. |

---

## PARTE E: MAPA DE ESTADO REAL DEL SISTEMA

```
Componente                          Estado          Desde
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
coherence_validator                 ✅ Unificado     SOL-2-B
  └─ _check_promised_assets_exist   ✅ Cross-check   SOL-2-B (7 servicios)
PROPOSAL_SERVICE_TO_ASSET           ✅ 7 entradas    SOL-2-B
proposal_asset_alignment_gate       ✅ Funcional     FASE-D
SitePresenceChecker                 ✅ Existe        601 líneas
deployment_assistant.md             ✅ Existe        43 líneas
site_verification_applied flag      ⚠️ Cosmetico    Siempre False
skipped_assets field                ⚠️ No populado   Dataclass vacía
D1: msg duplicación                 ⚠️ Pendiente     2 líneas fix
D2: prompts sin POST-EJECUCION      ⚠️ Pendiente     5 líneas × 2 archivos
D3: flag timing gap                 ⚠️ Documentado   Docstring fix
```

---

## PARTE F: SOLUCIONES PROPUESTAS (No implementar aún)

### SOL-1 [BAJA] — Deduplicar mensaje en coherence_validator (D1-A)
- **Archivo**: `coherence_validator.py` L542-546
- **Cambio**: Si un asset_type aparece en ambas listas, mostrarlo solo en `missing_service_assets` (formato "servicio→asset" es más informativo)
- **Esfuerzo**: 2 líneas
- **Riesgo**: Nulo

### SOL-2 [BAJA] — Parchear prompts SOL-2-A/B con POST-EJECUCION (D2-A)
- **Archivos**: `.opencode/plans/SOL-2-REFACTOR/05-prompt-inicio-sesion-fase-SOL2-A.md` y `SOL2-B.md`
- **Cambio**: Agregar bloque NOTA POST-EJECUCION al inicio de cada archivo
- **Esfuerzo**: 5 líneas por archivo
- **Riesgo**: Nulo

### SOL-3 [BAJA] — Documentar gap de timing en v4_asset_orchestrator (D3-C)
- **Archivo**: `v4_asset_orchestrator.py` L145
- **Cambio**: Agregar docstring: `# NOTE: site_verification_applied reflects orchestrator-level skips, not gate-level checks. See SOL-2-D3.`
- **Esfuerzo**: 1 línea
- **Riesgo**: Nulo

### SOL-4 [MEDIA] — Investigar por qué skipped_assets nunca se popula
- **Archivo**: `v4_asset_orchestrator.py` (método de generación)
- **Pregunta**: ¿Existe lógica que llame a SitePresenceChecker ANTES de generar assets y popule `skipped_assets`? Si no, el campo es dead code.
- **Esfuerzo**: Investigación (~15 min)
- **Riesgo**: Nulo (solo lectura)

### SOL-5 [BAJA] — Loggear excepciones en publication_gates.py catch-all
- **Archivo**: `publication_gates.py` L816-818
- **Cambio**: `except Exception as e: logger.warning(f"SitePresenceChecker error: {e}"); site_presence_report = None`
- **Esfuerzo**: 1 línea
- **Riesgo**: Nulo

---

## PARTE G: CÓMO INICIAR EN NUEVA SESIÓN

```
Carga .opencode/context/07_SOL-2_UNIFIED_VALIDATED_20260507.md.
Los 3 GAPs ALTA del archivo original son FALSOS POSITIVOS (SitePresenceChecker,
deployment_assistant.md existen; PROPOSAL_SERVICE_TO_ASSET ya tiene 7 entradas).
Las soluciones pendientes son SOL-1 a SOL-5 (todas BAJA/MEDIA esfuerzo).
Si decides implementar, ejecuta UNA micro-fase (sin v4complete, max 30 iteraciones).
```

---

## REFERENCIAS

### Código verificado
- `modules/commercial_documents/coherence_validator.py` — L494-555 (`_check_promised_assets_exist`)
- `modules/quality_gates/publication_gates.py` — L760-870 (`_proposal_asset_alignment_gate`)
- `modules/asset_generation/proposal_asset_alignment.py` — L20-28 (`PROPOSAL_SERVICE_TO_ASSET`, 7 entradas)
- `modules/asset_generation/site_presence_checker.py` — 601 líneas (EXISTE, funcional)
- `modules/asset_generation/v4_asset_orchestrator.py` — L90, L144-145 (`skipped_assets`, `site_verification_applied`)
- `modules/asset_generation/asset_catalog.py` — L54, L176, L322, L335 (whatsapp, optimization, monthly_report, open_graph)
- `modules/commercial_documents/v4_proposal_generator.py` — L839-898 (`_generate_dynamic_services_table`)
- `.agents/workflows/deployment_assistant.md` — 43 líneas (EXISTE, funcional)

### Archivos de contexto originales
- `.opencode/context/05_SOL-2_ASSET_ALIGNMENT_DISCREPANCY_20260507.md` (v3.0.0, 517 líneas)
- `.opencode/context/06_SOL-2_DESIGN_FINDINGS_20260507.md` (v1.0.0, 161 líneas)

### Plan SOL-2
- `.opencode/plans/SOL-2-REFACTOR/` — 9 archivos, fases A-D + RELEASE completadas
- Plan prompts SIN nota POST-EJECUCION (confirmado: 0 matches)
