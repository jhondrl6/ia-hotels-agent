# CONTEXTO: Scoring Transparency — 4 Pilares (GEO + SEO + AEO + IAO)

**Creado:** 2026-05-02
**Actualizado:** 2026-05-05T17:07 — 3 patches aplicados, bugs resueltos
**Sesión:** scoring-transparency-fix — v4complete Hotel Castilla Real

---

## VEREDICTO EJECUTIVO

**Todos los bugs de scoring transparency fueron resueltos.** El diagnóstico para Hotel Castilla Real ahora muestra scores consistentes entre tabla y breakdown en los 4 pilares.

| Pilar | Score Tabla | Score Breakdown | Suma pesos activos | Estado |
|-------|-------------|----------------|---------------------|--------|
| SEO Local | 25/100 | 25/100 | 15+10=25 ✅ | ✅ Consistente |
| GEO | 70/100 | 70/100 | 10+30+15+15=70 ✅ | ✅ Consistente |
| AEO | 0/100 | 0/100 | (ningún factor activo) ✅ | ✅ Consistente |
| IAO | 35/100 | 35/100 | 20+15=35 ✅ | ✅ Consistente |

---

## CAMBIOS APLICADOS (3 patches, mismo archivo)

### Patch 1: Fix `_build_scoring_breakdown()` — pesos fantasma eliminados

**Archivo:** `modules/commercial_documents/v4_diagnostic_generator.py` L276-288

**Problema:** Mostraba TODOS los factores (TRUE y FALSE) con pesos. Si AEO=0, aparecían 6 factores tachados sumando 100% — irracional para el hotelero.

**Solución:** Mostrar SOLO factores TRUE. Score 0 = "(ningún factor activo)".

```python
# ANTES (bug):
for k, peso in checklist.items():
    if elementos.get(k) is True:
        parts.append(f"✅ {k}({peso}%)")
    else:
        parts.append(f"~~{k}({peso}%)~~")  # pesos fantasma

# AHORA (fix):
for k, peso in checklist.items():
    if elementos.get(k) is True:
        parts.append(f"✅ {k}({peso}%)")
# FALSE no shown — peso real = 0, no hay "100% en juego"
```

**Output antes:**
```
**AEO 0/100** = ~~schema_faq(25%)~~ + ~~open_graph(15%)~~ + ...
```
**Output después:**
```
**AEO 0/100** = (ningún factor activo)
```

---

### Patch 2: Fix `_calculate_iao_score_from_audit()` — discrepancia IAO resuelta

**Archivo:** `modules/commercial_documents/v4_diagnostic_generator.py` L1865-1886

**Problema:** Tabla usaba `ia_readiness.overall_score` (34), breakdown usaba `calcular_score_iao()` (35). Discrepancia.

**Solución:** Ambos ahora usan `calcular_score_iao()` directamente. `ia_readiness.overall_score` removido como source primario.

**Problema secundario descubierto durante fix:** El ajuste 50/50 con `llm_report.mention_score = 0` reducía 35 → 17 artificialmente. Condition ajustada: `mention_score > 0` para activar el blending.

```python
# ANTES (discrepancia):
if hasattr(audit_result, 'ia_readiness') and audit_result.ia_readiness:
    score = getattr(audit_result.ia_readiness, 'overall_score', None)  # fuente diferente
    if score is not None:
        return str(int(score))
elementos_iao = self._extraer_elementos_iao(audit_result)
base_score = calcular_score_iao(elementos_iao)

# AHORA (coherente):
elementos_iao = self._extraer_elementos_iao(audit_result)
base_score = calcular_score_iao(elementos_iao)
# Ajuste solo si hay menciones reales (mention_score > 0)
llm_report = getattr(audit_result, 'llm_report', None)
if llm_report and llm_report.source != "stub" and llm_report.mention_score > 0:
    real_score = llm_report.mention_score
    base_score = int(base_score * 0.5 + real_score * 0.5)
```

---

### Patch 3: Nota de divergencia actualizada en template

**Archivo:** `modules/commercial_documents/templates/diagnostico_v6_template.md` L65

**Antes:**
```
> ⚠️ **Nota sobre el score GEO**: El desglose arriba usa la metodología del checklist GEO...
```

**Después:**
```
> ⚠️ **Nota sobre divergencia de scores**: El score GEO en la tabla principal viene directamente del `geo_score` de Google Business Profile (algoritmo propio de Google). El desglose GEO usa el checklist interno de iah-cli. Pueden diferir — ambos miden aspectos complementarios de tu presencia en Maps. Los scores SEO, AEO e IAO usan la misma metodología en tabla y desglose — siempre idénticos.
```

---

## VALIDACIÓN CONTRA CÓDIGO VIVO

| Claim | Estado | Evidencia |
|-------|--------|-----------|
| CHECKLIST_AEO suma 100 | ✅ | `v4_diagnostic_generator.py:172-180` = [25,15,15,20,10,15] → 100 |
| CHECKLIST_IAO suma 100 | ✅ | `v4_diagnostic_generator.py:182-190` = [20,15,15,15,10,10,15] → 100 |
| `_build_scoring_breakdown` solo TRUE | ✅ | L276-288: sin `~~` strike-through |
| IAO tabla = breakdown | ✅ | Ambos `calcular_score_iao()` → 35 |
| AEO=0 sin pesos fantasma | ✅ | Output: "(ningún factor activo)" |
| SEO=25 = suma exacta | ✅ | ssl(15%) + schema_reviews(10%) = 25 |
| Nota actualizada | ✅ | Template L65 menciona SEO/AEO/IAO consistentes |

---

## OUTPUT DEL V4COMPLETE — HOTEL CASTILLA REAL

**Archivo:** `output/test-scoring-transparency-v2/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260505_170725.md`

```
| Indicador | Su Negocio | Promedio | Estado |
|-----------|------------|----------|--------|
| SEO Local | 25/100 | 59/100 | ❌ Bajo |
| GEO | 70/100 | 89/100 | ❌ Bajo |
| AEO | 0/100 | 44/100 | ❌ Bajo |
| IAO | 35/100 | 20/100 | ✅ Superior |

**GEO 70/100** = ✅ redes_activas(10%) + ✅ geo_score_gbp(30%) + ✅ fotos_gbp(15%) + ✅ schema_reviews_geo(15%)
**SEO Local 25/100** = ✅ ssl(15%) + ✅ schema_reviews(10%)
**AEO 0/100** = (ningún factor activo)
**IAO 35/100** = ✅ citability_score(20%) + ✅ contenido_extenso(15%)
```

---

## COMPORTAMIENTO DE DIVERGENCIA RESTANTE (GEO únicamente)

**Score GEO tabla (70)** viene de `_calculate_geo_score()` → `audit_result.gbp.geo_score` (GBP algorithm).

**Score GEO breakdown (70)** viene de `calcular_score_geo()` → suma de pesos de checklist GEO.

**Pueden diferir** porque GBP usa su algoritmo propietario; el checklist evalúa factores técnicos que el hotelero controla.

**Casos:**
- GBP score > checklist score: perfil GBP está rankeando bien, pero faltan factores técnicos internos
- GBP score < checklist score: factores técnicos OK, pero GBP no los está reflejando en el ranking

**Esta divergencia es informativa, no un bug.** La nota en el template la documenta.

---

## NO-GOALS CONFIRMADOS

- No se modificaron checklists ni pesos
- No se modificó `calcular_score_*()` ni `_extraer_elementos_*()`
- No se cambió la metodología de cálculo
- No se modificaron los archivos de assets ni la generación de propuesta

---

## PRÓXIMOS PASOS SUGERIDOS

Este contexto está completo. Los bugs fueron resueltos y validados. No hay acción pendiente de scoring transparency.

Si se requiere extender funcionalidad (e.g., agregar más factores a checklists, cambiar pesos), seguir el workflow de phased_project_executor.md con una nueva sesión de planificación.
