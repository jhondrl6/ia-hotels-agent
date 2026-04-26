# FASE-TRAZABILIDAD: Contexto Consolidado — Items Pendientes y Decisiones
# VALIDADO contra codigo vivo — 2026-04-25 (sesion de validacion exhaustiva)

**Creado**: 2026-04-25
**Origen**: Consolidacion de `d1-warning-readiness-context.md` + `fase-trazabilidad-pendientes-context.md`
**Validado**: 2026-04-25 — auditoria exhaustiva contra codigo vivo
**Estado**: Post-commit `16fa26b`
**Proxima sesion sugerida**: FASE-TRAZABILIDAD-REFINEMENT

---

## Resumen de lo completado en FASE-TRAZABILIDAD-PATCH

La fase anterior implemento 5 fixes verificados en 1 ejecucion v4complete (Amazilia Hotel):

| Fix | Resultado | Nota validacion |
|-----|-----------|-----------------|
| T1: BUG-02 financial_validity WARNING | OK Gate reporta WARNING con default_sources en details | Confirmado L358-376 publication_gates.py |
| T2A: Header "## Trazabilidad" | OK Visible en L112 del diagnostico | |
| T2B: Seccion "## Validacion de Calidad" | OK Visible en L104 del diagnostico | Template v6 L82: `${manual_attention_table}` |
| T3: seo_score persiste en JSON | OK v4_complete_report.json tiene seo_score: 25 | |
| T4: geo_flow_result timing | OK Archivo existe en amazilia_hotel/v4_audit/ | Ver NOTA D3 abajo |

**Cambio fundamental**: El sistema dejo de ocultar > ahora transparenta. Pero la credibilidad sigue limitada por datos de entrada (onboarding no ejecutado), no por codigo.

---

## VALIDACION EXHAUSTIVA: Hallazgos Nuevos

### HALLAZGO N1: Dos GateStatus enums coexisten (CONFUSION POTENCIAL)

El codebase tiene DOS clases `GateStatus` independientes:

1. **`publication_gates.py` L54**: `GateStatus(str, Enum)` con PASSED/FAILED/BLOCKED/WARNING
2. **`domain_gates.py` L20**: `GateStatus(Enum)` con PASSED/FAILED/WARNING/NOT_APPLICABLE

La version de `publication_gates.py` es la que usa `check_publication_readiness()` y todos los gates de publicacion.
La version de `domain_gates.py` es para los gates de dominio (audit tecnico).

**Impacto**: Si algun modulo importa desde el dominio equivocado, WARNING puede no detectarse. Actualmente no hay conflicto porque `publication_gates.py` define su propio enum y no importa el de `domain_gates.py`. Pero es un riesgo de mantenimiento.

### HALLAZGO N2: Template v6 es MAS sofisticado de lo que el contexto original implica

El `diagnostico_v6_template.md` ya tiene:
- L8: `financial_evidence_tier: "${evidence_tier}"` en frontmatter
- L70: `${financial_title_label}` (titulo cambia segun source_reliability)
- L72: `${estimate_asterisk}` (asterisco condicional si unverified)
- L97-103: Blockquote con Tier A/B/C completo
- L105: `${estimate_footnote}` (nota condicional)

La variable Python es `evidence_tier` (no `financial_evidence_tier`). El template mapea `${evidence_tier}` al frontmatter key `financial_evidence_tier`.

### HALLAZGO N3: geo_score tiene DOS fuentes distintas (root cause de D3)

El geo_score que ve el cliente proviene de **dos caminos**:

1. **Pilar GEO en tabla principal** (L53 del template): usa `_calculate_geo_score()` (L1393-1398) que lee `audit_result.gbp.geo_score`. Si GBP no encontro el hotel (`place_found=False`), retorna `"0"`.

2. **Salud Tecnica GEO en tabla de metricas IA** (L1252-1264): lee `geo_flow_result.json` escrito por `v4_asset_orchestrator.py` L421. Si el archivo no existe, simplemente NO muestra esa fila.

**El "0/100 unknown" del contexto D3 es el Pilar GEO (#1)**, NO la Salud Tecnica GEO (#2). La Salud Tecnica GEO probablemente ni aparecio en el diagnostico (porque geo_flow_result.json no existia al momento de generar el diagnostico).

---

## Items Pendientes

### ITEM 1: D1 — WARNING en Publication Readiness

**Estado**: PENDIENTE — requiere decision

**Descripcion**: El fix BUG-02 hace que `financial_validity` retorne `WARNING` con `passed=True`. Pero `check_publication_readiness()` en `publication_gates.py` L1000-1003 usa solo `passed` (bool), asi que el readiness sigue siendo `READY_FOR_PUBLICATION` aunque haya warnings.

**Codigo actual** (`modules/quality_gates/publication_gates.py` L1000-1003):
```python
results = run_publication_gates(assessment)

blocking_gates = [r for r in results if not r.passed]
ready = len(blocking_gates) == 0
```

**NOTA de validacion**: El contexto original citaba lineas 979-982. Las lineas correctas son 1000-1003. El contenido es exactamente igual al descrito — solo las lineas se desplazaron.

**Logica actual del gate**:
- `_financial_validity_gate()` L366-376: Retorna `passed=True, status=GateStatus.WARNING` cuando hay default_sources
- `passed=True` significa que NO entra en `blocking_gates`
- Resultado: `ready=True` > `"READY_FOR_PUBLICATION"` (L1018)
- Los strings de status son `"READY_FOR_PUBLICATION"` o `"NOT_READY"` (NO existe `"REQUIRES_REVIEW"`)

**Opciones**:

**Opcion A — WARNING = REQUIRES_REVIEW (conservador)**:
```python
# En check_publication_readiness(), reemplazar L1002-1003:
warning_gates = [r for r in results if r.status == GateStatus.WARNING]
blocking_gates = [r for r in results if not r.passed]
ready = len(blocking_gates) == 0
# Nuevo campo:
status = "READY_FOR_PUBLICATION" if ready and not warning_gates else (
    "REQUIRES_REVIEW" if warning_gates else "NOT_READY"
)
```
- Efecto: Si cualquier gate tiene WARNING, el diagnostico muestra "REQUIRES_REVIEW"
- Implicacion: Mayor rigor, mas friccion para publicacion
- NOTA: Requiere agregar "REQUIRES_REVIEW" como string de status (no existe hoy)

**Opcion B — WARNING visible pero no bloqueante (actual)**:
El gate WARNING ya mejora el mensaje individual en `gate_report.json`. El readiness sigue `READY_FOR_PUBLICATION`. No se requiere cambio de codigo.

**Opcion C — WARNING en summary pero no en readiness status**:
Mantener `ready=True` pero incluir los warnings en el JSON del readiness report para que el diagnostico los mencione.
```python
# Agregar a L1008-1014 (el summary dict):
summary["warnings"] = [
    {"gate": r.gate_name, "message": r.message}
    for r in results if r.status == GateStatus.WARNING
]
```

**Criterios de decision**:
1. Que nivel de rigor quieres para publicacion?
2. Quieres que el cliente vea "REQUIRES_REVIEW" por defaults financieros (Tier C)?
3. Un warning sobre Tier C justifica bloquear/marcar publicacion?

**Archivo a modificar**: `modules/quality_gates/publication_gates.py` — metodo `check_publication_readiness()`

---

### ITEM 2: D2 — Visibilidad del Tier C en cuerpo del documento

**Estado**: PENDIENTE — requiere decision de contenido

**Problema**: El diagnostico muestra el Tier C en frontmatter + blockquote (L97-103), pero NO lo hace visible en el encabezado de perdida financiera:

```
### Comision OTA Actual (verificable)
**$2.610.000 COP/mes**           <- Sin indicador de Tier
Desglose:
- Estimacion basada en escenario meta esperada
- Fuente del dato: benchmark
```

Un cliente que lee "$2.6M/mes de perdida" sin contexto puede inferir datos reales cuando son benchmark regional.

**NOTA de validacion**: El template YA tiene mecanismos parciales:
- L70: `${financial_title_label}` cambia el titulo (verificable vs estimada)
- L72: `${estimate_asterisk}` agrega `*` si unverified
- L97-103: Blockquote completo con Tier A/B/C
- L105: `${estimate_footnote}` con nota condicional

El codigo que alimenta estas variables esta en `v4_diagnostic_generator.py`:
- L703-707: `_build_financial_title_label()` cambia titulo segun `source_reliability`
- L759: `estimate_asterisk = "" if is_verified else "*"`
- L760-762: `estimate_footnote` con texto "Dato basado en estimaciones"
- L773: `'evidence_tier': tier` se pasa al template

**Opciones**:

**Opcion A — Disclaimer minimo en encabezado**:
Modificar template L72 para que cuando Tier C:
```markdown
**$2.610.000 COP/mes** *(estimado — Tier C: basado en benchmark regional)*
```
Requiere pasar tier al template en L72, no solo en frontmatter/footer.

**Opcion B — Banner dedicado sobre la tabla de escenarios (mas visible)**:
```markdown
> **Nivel de evidencia: Tier C**
> Estas cifras se basan en benchmark regional + datos limitados de la web.
> Para precision, ejecute onboarding con datos operativos reales.
```
Insertar entre L68 (`## Impacto Financiero`) y L70 (`### ${financial_title_label}`).

**Opcion C — Sin cambios**:
Mantener el disclaimer en footer/blockquote como esta. El codigo ya transparenta Tier en metadata. La decision de enfatizar mas es comercial.

**Criterios de decision**:
- Que nivel de visibilidad quiere para Tier C en el cuerpo?
- Debe decir explicitamente "cifras estimadas" o "basado en benchmark"?
- Cambiar "Comision OTA Actual" > "Perdida Estimada por OTA"?

**Archivos a modificar**:
- `modules/commercial_documents/templates/diagnostico_v6_template.md` (template)
- `modules/commercial_documents/v4_diagnostic_generator.py` (si necesita pasar tier adicional al encabezado)

---

### ITEM 3: D3 — geo_score = 0/100 — Timing del pipeline

**Estado**: PENDIENTE — requiere investigacion

**Problema**: El diagnostico muestra:
```
| Salud Tecnica GEO | 0/100 | unknown | :red_circle: |
```

**Validacion exhaustiva revela la raiz**:

El geo_score que el cliente ve tiene DOS fuentes:

**Fuente 1 — Pilar GEO (tabla principal, template L53)**:
- Generado por `_calculate_geo_score()` en `v4_diagnostic_generator.py` L1393-1398
- Lee `audit_result.gbp.geo_score` directamente
- Si `audit_result.gbp` es None o `place_found=False` > retorna `"0"`
- Este es el "0/100" que aparece en la tabla de 4 Pilares

**Fuente 2 — Salud Tecnica GEO (tabla metricas IA, template ~L1252-1264)**:
- Lee `geo_flow_result.json` escrito por `v4_asset_orchestrator.py` L421
- Si el archivo no existe al momento de generar el diagnostico > la fila NO aparece
- Si existe pero tiene score 0 > muestra "0/100 unknown"

**Hipotesis mas probable: TIMING del pipeline**
El diagnostico se genera ANTES de que `v4_asset_orchestrator` ejecute el GEO flow y escriba `geo_flow_result.json`. Entonces:
- El Pilar GEO muestra 0 (porque GBP no encontro el hotel o score bajo)
- La Salud Tecnica GEO ni aparece (porque el archivo no existe todavia)

**Verificacion sugerida**:
```bash
# Ver si el archivo existe AHORA (despues de la ejecucion completa)
ls -la output/v4_complete/amazilia_hotel/v4_audit/geo_flow_result.json

# Si existe, ver contenido
cat output/v4_complete/amazilia_hotel/v4_audit/geo_flow_result.json

# Ver el orden de ejecucion en main.py
grep -n "diagnostic\|asset_orchestrator\|geo_flow" main.py
```

**Decisiones segun resultado**:
- Si timing: Reordenar pipeline para que geo_flow se calcule antes del diagnostico, O hacer que el diagnostico se regenere despues del asset orchestration
- Si dato real (0 real): Cambiar "unknown" > "0/100 — Sin datos GEO detectados" en L1262
- Si GBP no encontro el hotel: Es un dato real — el hotel no tiene perfil GBP verificable

**Archivos a investigar**:
- `modules/asset_generation/v4_asset_orchestrator.py` L418-424 (escritura geo_flow_result)
- `modules/commercial_documents/v4_diagnostic_generator.py` L1252-1264 (lectura geo_flow_result)
- `modules/commercial_documents/v4_diagnostic_generator.py` L1393-1398 (_calculate_geo_score)
- `main.py` (orden de ejecucion: diagnostico vs asset orchestrator)

---

### ITEM 4: D4 — Gap entre coherence_score (0.89) y asset_confidence (8 below threshold)

**Estado**: PENDIENTE — requiere decision de display

**Problema**:
```
Gate de Coherencia:
   Score calculado: 0.89 (umbral: 0.8)
   Checks: 6/6 pasados
   [OK] Coherencia aceptable — Generando propuesta completa

Publication Gates:
   asset_confidence: 8 asset(s) below confidence threshold (0.7)
```

El diagnostico muestra coherence_score = 0.89 y dice "Coherencia aceptable". Pero 8/10 assets estan below threshold. Puede dar impresion falsa de que los assets son confiables.

**Validacion del codigo**:
- `asset_confidence` gate (L678-751): Retorna `passed=True, status=GateStatus.WARNING` (L737). Es advisory, NO bloquea.
- Threshold hardcoded: `0.7` (L696)
- El coherence gate mide coherencia entre documentos (diagnostico vs propuesta vs assets). El asset_confidence mide confianza individual de cada asset generado. Son metricas DISTINTAS.
- Un coherence_score alto es compatible con muchos assets de baja confianza — porque la coherencia mide consistencia entre documentos, no calidad individual de cada asset.

**Opciones**:

**Opcion A — No cambiar (decision de negocio)**:
El coherence gate pasa (0.89 > 0.8). Los assets con WARNING se entregan con disclaimer.
El sistema YA es consistente: coherence mide consistencia, asset_confidence mide calidad individual.

**Opcion B — Nota en diagnostico**:
Cuando `asset_confidence < threshold`, agregar linea en la seccion de calidad:
```
8 assets con confianza baja (0.7) — Incluidos con disclaimer en paquete
```

**Opcion C — Gate mas riguroso**:
Cambiar `asset_confidence` de WARNING a BLOCKED si mas de N assets estan below threshold.
```python
# En _asset_confidence_gate(), L735-751:
if len(low_confidence_assets) > len(generated_assets) * 0.5:  # >50% low
    passed = False
    status = GateStatus.BLOCKED
```

**Criterios de decision**:
- Debe el diagnostico transparentar que los assets tienen baja confianza?
- Quieres que `asset_confidence` bloquee si demasiados assets estan below threshold?

**Archivo a modificar**: `modules/quality_gates/publication_gates.py` (Opcion C) + `modules/commercial_documents/v4_diagnostic_generator.py` (Opcion B)

---

## Resumen de Decisiones

| # | Item | Tipo | Codigo o decision? | Precision original | Hallazgo validacion |
|---|------|------|---------------------|--------------------|---------------------|
| D1 | WARNING en readiness | Operativo | Codigo + decision negocio | PARCIAL: lineas 979-982 incorrectas (real: 1000-1003), no existe "REQUIRES_REVIEW" | BUG confirmado: WARNING no afecta readiness |
| D2 | Tier C en cuerpo | Comercial | Decision contenido | PARCIAL: subestima mecanismos existentes | Template YA tiene Tier en footer+asterisk+title |
| D3 | geo_score = 0 | Tecnico | Investigacion > decision | PARCIAL: confunde 2 fuentes de geo_score | Root cause: timing pipeline + GBP no encontrado |
| D4 | coherence vs asset_confidence | Comercial | Decision display | CORRECTO: metricas distintas coexisten | asset_confidence es advisory por diseno |

---

## Flujo Recomendado para Proxima Sesion

1. **D3** (investigacion, ~20 min) — verificar orden pipeline en main.py y determinar si es timing/bug/dato real
2. **D1** (codigo, ~30 min) — resolver el if/warning en readiness segun decision
3. **D2** (contenido, ~20 min) — decidir nivel de visibilidad Tier C
4. **D4** (display, ~15 min) — decidir como mostrar gap coherence/asset_confidence

D3 es PRIORIDAD porque su resultado afecta las demas decisiones. Si es timing, requiere reorden de pipeline. Si es dato real, solo requiere cambio de display.

D2 y D4 son mejoras de **credibilidad comercial**. D1 es mejora de **rigor operativo**. D3 es **investigacion**.

---

## Archivos Relevantes

```
modules/quality_gates/publication_gates.py     # D1 (L1000-1003 readiness, L318-398 financial_validity, L678-751 asset_confidence)
modules/quality_gates/domain_gates.py          # N1: GateStatus duplicado (L20)
modules/commercial_documents/templates/diagnostico_v6_template.md  # D2 (L68-105 seccion financiera)
modules/commercial_documents/v4_diagnostic_generator.py  # D2 (L703-783 tier/asterisk), D3 (L1252-1264 geo_flow, L1393-1398 geo_score)
modules/commercial_documents/data_structures.py  # evidence_tier en FinancialScenarios (L162)
modules/asset_generation/v4_asset_orchestrator.py  # D3 (L418-424 escritura geo_flow_result)
main.py                                        # D3 (orden ejecucion pipeline)
```
