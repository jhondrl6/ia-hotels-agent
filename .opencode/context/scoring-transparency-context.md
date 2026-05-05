# CONTEXTO: Scoring Transparency — 4 Pilares (GEO + SEO + AEO + IAO)

**Creado:** 2026-05-02
**Actualizado:** 2026-05-05 (post-validación contra código vivo)
**Sesión de validación:** 2026-05-05 — validación completa del contexto + hallazgo de extensión a 4 pilares
**Problema referenciado:** `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260505_112219.md` línea 60
**Bug concreto:** `_build_scoring_breakdown()` filtra `is True` y oculta factores FALSE (afecta los 4 pilares, pero solo GEO lo usa actualmente)

---

## VEREDICTO EJECUTIVO

**El contexto original era correcto en su diagnóstico del bug GEO, pero incompleto en alcance.**

1. **Bug confirmado:** `_build_scoring_breakdown()` en `v4_diagnostic_generator.py` solo muestra factores con valor `True`, ocultando los `False`. Para `hotelcastillareal` esto significa que `nap_consistente(15%)` y `horario_gbp(15%)` no aparecen en el output.

2. **Nuevo hallazgo:** `_build_scoring_breakdown()` ya es genérica (soporta `seo`, `geo`, `aeo`, `iao`), pero el generator **solo la invoca para GEO**. Los otros 3 pilares tienen extractores, calculadores y checklists implementados, pero **cero transparencia en el diagnóstico generado**. Esto contradice lo que promete `docs/scoring_methodology.md` ("breakdown de 4 pilares").

3. **Recomendación:** Dividir en dos tareas ordenadas — (A) corregir el filtrado del bug para que muestre TODOS los factores con marcador visual, y (B) extender el breakdown a los 4 pilares (SEO, AEO, IAO) agregando las variables al template y al generator. El costo de B es ~10 líneas de código porque la infraestructura ya existe.

---

## VALIDACION DE CLAIMS DEL CONTEXTO ORIGINAL

| Claim original | Estado | Evidencia viva |
|---------------|--------|----------------|
| `_build_scoring_breakdown()` filtra `is True` | ✅ CORRECTO | `v4_diagnostic_generator.py:276-283` |
| CHECKLIST_GEO = 6 items, 100pts | ✅ CORRECTO | `v4_diagnostic_generator.py:162-170` |
| `_extraer_elementos_geo()` existe | ✅ CORRECTO | `v4_diagnostic_generator.py:2311-2343` |
| Template tiene `${geo_score_breakdown}` | ✅ CORRECTO | `diagnostico_v6_template.md:60` |
| `_build_excluded_factors_section()` existe | ✅ CORRECTO | `v4_diagnostic_generator.py:288-296` |
| `scoring_methodology_url` en frontmatter | ✅ CORRECTO | `v4_diagnostic_generator.py:699` |
| `docs/scoring_methodology.md` existe | ✅ CORRECTO | 145 líneas, 4 pilares documentados |
| Output real muestra 4/6 factores GEO | ✅ CONFIRMADO | `evidence/FIN-4/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260504_144810.md` muestra `**GEO 70/100** = redes_activas(10%) + geo_score_gbp(30%) + fotos_gbp(15%) + schema_reviews_geo(15%)` |
| Números de línea citados | ⚠️ APROXIMADOS | Desviación <5 líneas, usables |

---

## NUEVO HALLAZGO: INFRAESTRUCTURA DE 4 PILARES, PERO SOLO GEO USA BREAKDOWN

### Checklists implementados (v4_diagnostic_generator.py:151-191)

```python
CHECKLIST_SEO:  7 items = 100pts  (ssl, schema_hotel, LCP_ok, CLS_ok, imagenes_alt, blog_activo, schema_reviews)
CHECKLIST_GEO:  6 items = 100pts  (nap_consistente, redes_activas, geo_score_gbp, fotos_gbp, horario_gbp, schema_reviews_geo)
CHECKLIST_AEO:  6 items = 100pts  (schema_faq, open_graph, schema_hotel_aeo, contenido_factual, speakable_schema, imagenes_alt_aeo)
CHECKLIST_IAO:  7 items = 100pts  (citability_score, contenido_extenso, llms_txt_exists, crawler_access, brand_signals, ga4_indirect, schema_advanced)
```

### Calculadores implementados (v4_diagnostic_generator.py:194-224)

- `calcular_score_seo(elementos)` → línea 194
- `calcular_score_geo(elementos)` → línea 201
- `calcular_score_aeo(elementos)` → línea 208
- `calcular_score_iao(elementos)` → línea 215

### Extractores implementados (v4_diagnostic_generator.py:2280-2432)

- `_extraer_elementos_seo(audit_result)` → línea 2280
- `_extraer_elementos_geo(audit_result)` → línea 2311
- `_extraer_elementos_aeo(audit_result)` → línea 2345
- `_extraer_elementos_iao(audit_result)` → línea 2375

### PERO: Solo GEO tiene breakdown en el template data (v4_diagnostic_generator.py:697)

```python
'geo_score_breakdown': _build_scoring_breakdown('geo', self._extraer_elementos_geo(audit_result)),
```

**No existen:** `seo_score_breakdown`, `aeo_score_breakdown`, `iao_score_breakdown` en el diccionario de template data.

**No existen:** placeholders `${seo_score_breakdown}`, `${aeo_score_breakdown}`, `${iao_score_breakdown}` en `diagnostico_v6_template.md`.

### Impacto del doble problema

1. **Para GEO:** El usuario ve score 70/100 pero no sabe que faltan 30pts (`nap_consistente + horario_gbp`). Esto genera la pregunta: "¿debería incluir el resto de los indicadores?"
2. **Para SEO/AEO/IAO:** El usuario ve los scores en la tabla principal pero **nunca ve qué factores contribuyen o faltan**. Transparencia cero.
3. **Para `scoring_methodology.md`:** El documento promete "breakdown de 4 pilares" pero el diagnóstico solo entrega 1. Desalineación documentación ↔ output.

---

## CAUSA RAÍZ DEL BUG DE FILTRADO

**Archivo:** `/mnt/c/Users/Jhond/Github/iah-cli/modules/commercial_documents/v4_diagnostic_generator.py`

**Función `_build_scoring_breakdown()` líneas 276-283:**

```python
# Construir breakdown solo con elementos que contribuyeron
parts = []
for k, peso in checklist.items():
    if elementos.get(k) is True:   # ← BUG: SOLO incluye TRUE
        parts.append(f"{k}({peso}%)")
```

La función es intencionalmente genérica (`pilar` como parámetro), pero el filtrado por `is True` hace que los factores `False` desaparezcan completamente del output. Para transparencia al cliente, todos los factores deben ser visibles.

---

## SOLUCION RECOMENDADA (Dos tareas ordenadas)

### Tarea A — Fix del filtrado (Bug, prioridad)

**Objetivo:** Modificar `_build_scoring_breakdown()` para que muestre TODOS los factores del checklist con marcador visual para los ausentes.

**Output deseado para GEO 70/100 (hotelcastillareal):**
```
**GEO 70/100** = ✅ redes_activas(10%) + ✅ geo_score_gbp(30%) + ✅ fotos_gbp(15%) + ✅ schema_reviews_geo(15%) + ~~nap_consistente(15%)~~ + ~~horario_gbp(15%)~~
```

**Cambio mínimo en `_build_scoring_breakdown()`:**
- Iterar TODO el checklist (no solo los True)
- Para cada factor: si `True` → `✅ nombre(peso%)`, si `False` → `~~nombre(peso%)~~`
- Mantener score calculado por `calcular_score_*()`

**Archivo a modificar:**
- `modules/commercial_documents/v4_diagnostic_generator.py` — `_build_scoring_breakdown()` líneas 276-285

### Tarea B — Extensión a 4 pilares (Feature parity)

**Objetivo:** Agregar breakdowns de SEO, AEO, IAO al diagnóstico generado.

**Cambios necesarios:**
1. `v4_diagnostic_generator.py` línea ~697: agregar 3 asignaciones:
   ```python
   'seo_score_breakdown': _build_scoring_breakdown('seo', self._extraer_elementos_seo(audit_result)),
   'aeo_score_breakdown': _build_scoring_breakdown('aeo', self._extraer_elementos_aeo(audit_result)),
   'iao_score_breakdown': _build_scoring_breakdown('iao', self._extraer_elementos_iao(audit_result)),
   ```
2. `diagnostico_v6_template.md`: agregar 3 placeholders después de `${geo_score_breakdown}` (línea 60) o en una sección de desglose unificada.
3. Considerar si los 4 breakdowns deben ir uno tras otro o en una tabla compacta.

**Archivos a modificar:**
- `modules/commercial_documents/v4_diagnostic_generator.py` — template data dict (~3 líneas)
- `modules/commercial_documents/templates/diagnostico_v6_template.md` — placeholders (~3 líneas)

**Nota:** `scoring_methodology.md` NO requiere cambios. Ya documenta los 4 pilares correctamente.

---

## MACRO-FASES SUGERIDAS (para planificación en nueva sesión)

Estas son sugerencias para la sesión de planificación. NO son fases ejecutadas todavía.

```
FASE-SCORING-A: Fix del filtrado en _build_scoring_breakdown()
  └─ Corregir para mostrar TODOS los factores con marcador visual
  └─ Test con hotelcastillareal (v4complete rápido)
  └─ Validar: run_all_validations.py --quick

FASE-SCORING-B: Extensión de breakdown a 4 pilares
  └─ Agregar seo/aeo/iao_score_breakdown al generator
  └─ Agregar placeholders al template v6
  └─ Test con hotelcastillareal (v4complete rápido)
  └─ Validar: run_all_validations.py --quick

FASE-SCORING-C: Documentación y sincronización
  └─ Actualizar CHANGELOG.md (si aplica versión)
  └─ Verificar scoring_methodology.md sigue alineado
  └─ REGISTRY.md vía log_phase_completion.py
  └─ run_all_validations.py --quick
```

**R3 Scope evaluation estimado:**
- FASE-SCORING-A: 2-3 tareas + 1 comando largo (v4complete) → Ajusta a sub-fases si excede
- FASE-SCORING-B: 2-3 tareas + 1 comando largo (v4complete)
- FASE-SCORING-C: 2-3 tareas + 0 comandos largos (docs cascade)

**Dependencias:** A → B → C. No hay conflictos de archivos entre A y B (líneas distintas del mismo archivo, no se solapan).

---

## CRITERIOS DE ÉXITO

1. Output del diagnóstico muestra TODOS los factores del checklist GEO (6/6), no solo los TRUE
2. Factores ausentes marcados visualmente (~~tachado~~ o ❌)
3. Score sigue siendo 70/100 pero con breakdown visible: 4✅ + 2❌
4. Los 4 pilares (SEO, GEO, AEO, IAO) tienen breakdown visible en el diagnóstico generado
5. `python scripts/run_all_validations.py --quick` pasa
6. `scoring_methodology.md` y el output del diagnóstico están alineados (ambos prometen 4 pilares, ambos entregan 4 pilares)

---

## NON-GOALS Y RIESGOS

**Non-goals:**
- No modificar los checklists ni los pesos (ya están validados)
- No modificar `calcular_score_*()` ni `_extraer_elementos_*()` (funcionan correctamente)
- No modificar `scoring_methodology.md` (ya está completo)
- No cambiar la metodología de cálculo del score (solo la presentación del breakdown)

**Riesgos:**
- **Divergencia dual-score GEO:** El score en la tabla principal (`${geo_score}`) viene de `_calculate_geo_score()` → GBP raw. El breakdown usa `calcular_score_geo()` → CHECKLIST_GEO. Esta divergencia YA está documentada en el template (línea 62) y en `scoring_methodology.md` (línea 72). No es un riesgo nuevo, pero el fix del breakdown hará que la divergencia sea más visible. Verificar que la nota explicativa sigue presente.
- **Ruido visual:** Mostrar 4 breakdowns completos puede hacer el diagnóstico muy largo. Considerar formato compacto (tabla o lista) en lugar de línea de texto corrido.

---

## COMANDOS DE REFERENCIA

```bash
# Test rápido del pipeline (para validar fix)
cd /mnt/c/Users/Jhond/Github/iah-cli
venv/Scripts/python.exe main.py v4complete --url https://hotelcastillareal.com --region eje_cafetero --output output/test-scoring-fix

# Validaciones
venv/Scripts/python.exe scripts/run_all_validations.py --quick

# Ver output generado
cat output/test-scoring-fix/01_DIAGNOSTICO_Y_OPORTUNIDAD_*.md | grep -A3 "GEO\|SEO\|AEO\|IAO"
```

---

## PROMPT PARA LA SIGUIENTE SESIÓN

Copiar y pegar en una nueva sesión para diseñar el plan de fases:

```
Carga el contexto de scoring transparency en /mnt/c/Users/Jhond/Github/iah-cli/.opencode/context/scoring-transparency-context.md

Basado en ese contexto validado, diseña un plan de fases siguiendo .agents/workflows/phased_project_executor.md con:
1. FASE-SCORING-A: Fix del filtrado en _build_scoring_breakdown() para mostrar todos los factores (TRUE y FALSE) con marcador visual
2. FASE-SCORING-B: Extensión del breakdown a los 4 pilares (SEO, GEO, AEO, IAO)
3. FASE-SCORING-C: Documentación cascade (CHANGELOG, REGISTRY, validaciones)

Requisitos del plan:
- R3 scope evaluation para cada fase (max 4 tareas + 0 comandos largos, o 3 tareas + 1 comando largo)
- Dependencia diagram (ASCII)
- Iteration budget estimate por fase
- Archivos involucrados con tipo de cambio
- Post-ejecución: log_phase_completion.py command exacto por fase

Guarda el plan en .opencode/plans/SCORING-TRANSPARENCY/ siguiendo la estructura de references/phased_plan_structure_example.md.
```
