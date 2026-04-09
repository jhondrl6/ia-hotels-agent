# CONTEXTO: Causa Raíz — Límite de 4 Brechas en Diagnóstico

**Fecha**: 2026-04-08
**Proyecto**: BRECHAS-DINAMICAS (Eliminación del hardcode "LAS 4 BRECHAS")
**Trigger**: Bloque "LAS 4 BRECHAS CRÍTICAS IDENTIFICADAS" en `01_DIAGNOSTICO_Y_OPORTUNIDAD` limita a 4 cuando el sistema puede detectar hasta 10.

---

## 1. SÍNTOMA

En `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_*.md` linea 71:
```
## 🚨 LAS 4 BRECHAS CRÍTICAS IDENTIFICADAS
```
El header y contenido muestran exactamente 4 brechas sin importar cuántas detecte el audit.

## 2. CAUSA RAÍZ — 3 CAPAS

### CAPA 1: Template estático (CAUSA PRIMARIA)
- **V6**: `modules/commercial_documents/templates/diagnostico_v6_template.md` líneas 66-87
- **V4**: `modules/commercial_documents/templates/diagnostico_v4_template.md` líneas 47-61

Ambos tienen **4 ranuras fijas** (`${brecha_1_nombre}` ... `${brecha_4_nombre}`) sin loop.
El V4 dice "LAS 4 RAZONES EXACTAS", el V6 dice "LAS 4 BRECHAS CRÍTICAS".
La tabla resumen (líneas 112-117) también tiene 4 filas fijas.

### CAPA 2: `_prepare_template_data()` solo llena 4 (CAUSA SECUNDARIA)
- **Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py` líneas 519-531, 577-590
- Construye solo `brecha_1_*` a `brecha_4_*` (nombre, costo, detalle, impacto, resumen, recuperacion).

### CAPA 3: `_inject_brecha_scores()` trunca a 4 (CAUSA TERCIARIA)
- **Archivo**: `v4_diagnostic_generator.py` línea 1934
- `for i in range(1, min(scores_count, 4) + 1):` corta cualquier score adicional.

## 3. LA CONTRADICCIÓN

`_identify_brechas()` (líneas 1726-1842) detecta HASTA 10 brechas:
1. `low_gbp_score` — Visibilidad GBP/GEO (impacto 0.30)
2. `no_hotel_schema` — Sin Schema Hotel (0.25)
3. `no_whatsapp_visible` — Canal Directo Cerrado (0.20)
4. `poor_performance` — Web Lenta (0.15)
5. `whatsapp_conflict` — Datos Inconsistentes (0.10)
6. `metadata_defaults` — Metadatos por Defecto CMS (0.10)
7. `missing_reviews` — Falta de Reviews (0.10)
8. `no_faq_schema` — Sin FAQ Rich Snippets (0.12)
9. `no_og_tags` — Sin Meta Tags Sociales (0.08)
10. `low_citability` — Contenido No Citable por IA (0.10)

Retorna TODAS ordenadas por impacto descendente, sin truncamiento.
Pero template + generator + scores solo muestran 4.

## 4. IMPACTO EN CADENA DIAGNÓSTICO → PROPUESTA → ASSETS

### Diagnóstico
- Si el hotel tiene 7 dolores y solo mostramos 4, perdemos oportunidades de detección.

### Propuesta Comercial
- `propuesta_v6_template.md` NO consume `brecha_N_*` directamente.
- Usa un paquete único "Kit Hospitalidad Digital" con servicios fijos (GEO, IAO, AEO, SEO, WhatsApp, Schema, Informe).
- NO se alimenta dinámicamente de las brechas detectadas.
- **Riesgo**: La propuesta ofrece siempre lo mismo sin importar qué brechas detectó el diagnóstico.

### Assets (PainSolutionMapper)
- `PainSolutionMapper.PAIN_SOLUTION_MAP` mapea 24+ pain_ids a assets.
- `_identify_brechas()` genera pain_ids que alimentan PainSolutionMapper.
- PainSolutionMapper.detect_pains() tiene SU PROPIA lógica de detección (umbrales distintos).
- **Riesgo de desconexion**: Si brechas del diagnóstico no coinciden con pains detectados por PainSolutionMapper, los assets generados no cubren lo que el diagnóstico reportó.

### Coherence Validator
- `coherence_config.py` rules:
  - `problems_have_solutions` (blocking): >=50% de problemas deben tener solución.
  - `assets_are_justified` (no-blocking): cada asset debe trazar a un pain_id.
- Si se muestran más brechas en diagnóstico pero los assets no cubren las nuevas, `problems_have_solutions` puede fallar.

### OpportunityScorer
- `BRECHA_SEVERITY_MAP` solo tiene 7 tipos (falta mapping para `missing_reviews`, `no_og_tags`, `low_citability`, `low_gbp_score`, `no_whatsapp_visible`).
- Los pain_ids de `_identify_brechas()` no siempre coinciden con los `type` keys del scorer.
- El mapper en `_compute_opportunity_scores()` (línea 1864-1873) tiene: `missing_reviews → gbp_incomplete`, pero faltan `no_og_tags`, `low_citability`, `low_gbp_score`, `no_whatsapp_visible`.

## 5. BUG ADICIONAL ENCONTRADO

### Duplicate key en PAIN_SOLUTION_MAP
- `low_ia_readiness` está definido DOS VECES (líneas 208 y 282 en pain_solution_mapper.py).
- La segunda definición (local_content_page) sobreescribe la primera (hotel_schema + llms_txt).
- Resultado: si se detecta low_ia_readiness, solo se genera local_content_page, no hotel_schema ni llms_txt.

### optimization_guide con promised_by="pain_solution_mapper"
- No es un pain_id real, es un catch-all. Debería ser lista vacía o pain_ids específicos.

## 6. ARCHIVOS INVOLUCRADOS

| Archivo | Rol | Cambio necesario |
|---------|-----|-----------------|
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | Template V6 diagnóstico | Reemplazar 4 ranuras fijas por `${brechas_section}` dinámico |
| `modules/commercial_documents/templates/diagnostico_v4_template.md` | Template V4 diagnóstico | Ídem |
| `modules/commercial_documents/v4_diagnostic_generator.py` | Generador | Construir brechas dinámicamente en `_prepare_template_data()` |
| `modules/commercial_documents/v4_diagnostic_generator.py` | `_inject_brecha_scores()` | Eliminar `min(..., 4)` |
| `modules/financial_engine/opportunity_scorer.py` | Scorer | Agregar mappings faltantes en SEVERITY/EFFORT/IMPACT_MAP |
| `modules/commercial_documents/pain_solution_mapper.py` | Pain→Asset mapper | Fix duplicate `low_ia_readiness` |
| `modules/asset_generation/asset_catalog.py` | Catálogo assets | Verificar que assets cubran nuevos pain_ids |
| `modules/commercial_documents/coherence_config.py` | Coherencia | Verificar que rules sigan pasando con N brechas |
| `tests/commercial_documents/test_diagnostic_brechas.py` | Tests existentes | Ampliar para N brechas dinámicas |

## 7. VALIDACIÓN: v4complete para amaziliahotel.com

Post-implementación, ejecutar:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
/mnt/c/Users/Jhond/Github/iah-cli/.venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com
```
Analizar el 01_DIAGNOSTICO generado para verificar:
- Muestra TODAS las brechas detectadas (no solo 4)
- Cada brecha tiene pain_id válido que conecta con PainSolutionMapper
- La tabla resumen tiene N filas
- La propuesta comercial refleja las brechas detectadas
