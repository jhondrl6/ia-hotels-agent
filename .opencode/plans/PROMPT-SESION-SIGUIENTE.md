# PROMPT PARA NUEVA SESION -- GAP-IAO-01-02-B

## CONTEXTO

**Proyecto**: iah-cli -- Sistema de IA Optimization para hoteles boutique
**Repositorio**: `C:\Users\Jhond\Github\iah-cli`
**Planes**: `C:\Users\Jhond\Github\iah-cli\.opencode\plans`
**Fase a ejecutar**: GAP-IAO-01-02-B

---

## LECTURAS OBLIGATORIAS (EN ORDEN)

1. **README.md** -- Fuente de verdad del plan completo
2. **dependencias-fases.md** -- Dependencias actualizadas
3. **00-IAO-FLUJO-COMPLETO.md** -- Mapa del flujo sin desconexiones
4. **05-prompt-inicio-sesion-fase-GAP-IAO-01-02-B.md** -- Implementacion detallada

---

## ESTADO ACTUAL

| Fase | Estado |
|------|--------|
| FASE-0 | Completada |
| GAP-IAO-01-00 | Completada |
| GAP-IAO-01-01 | Completada |
| GAP-IAO-01-02 | Completada |
| **GAP-IAO-01-02-B** | **PROXIMA** |
| GAP-IAO-01-02-C | Pendiente |
| GAP-IAO-01-03 | Pendiente |
| GAP-IAO-01-04 | Pendiente |
| GAP-IAO-01-05 | Opcional |

---

## QUE HIZO GAP-IAO-01-02 (completada)

Se crearon las estructuras de soporte:

- `ELEMENTO_KB_TO_PAIN_ID`: 12 elementos KB mapeados a pain_id + asset
- `calcular_cumplimiento()`: Score 0-100 con pesos KB
- `sugerir_paquete()`: basico (<40), avanzado (40-69), premium (>=70)
- `_extraer_elementos_de_audit()`: 12 elementos desde V4AuditResult (7 con default False)
- `_asset_para_pain()`: Filtro IMPLEMENTED vs MISSING
- `_identify_brechas()`: Ahora retorna pain_id en cada brecha
- `_calculate_score_ia()`: Retorna Optional[int] (None/-1/>=0)
- 7 pain_ids nuevos en PAIN_SOLUTION_MAP
- 5 assets MISSING en ASSET_CATALOG
- 7 campos KB nuevos en DiagnosticSummary

**Archivos modificados**: pain_solution_mapper.py, asset_catalog.py, data_structures.py, v4_diagnostic_generator.py

---

## QUE HACE GAP-IAO-01-02-B

**Objetivo**: Reemplazar los 7 default False con detectores reales o stubs.

| Subfase | Elemento | Que hace | Riesgo |
|---------|----------|----------|--------|
| B1 | `ssl` | `url.startswith("https")` | NULO |
| B2 | `contenido_extenso` | Mapear CitabilityScorer (score > 50 = True) | BAJO |
| B3 | `nap_consistente` | Extender CrossValidator (address + email) | BAJO |
| B4 | `open_graph`, `imagenes_alt`, `redes_activas` | SEOElementsDetector (stubs) | BAJO |

**Archivos a modificar**:
1. `modules/auditors/seo_elements_detector.py` (CREAR)
2. `modules/data_validation/cross_validator.py`
3. `modules/auditors/v4_comprehensive.py`
4. `modules/commercial_documents/v4_diagnostic_generator.py`

---

## VERIFICACION POST-IMPLEMENTACION

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Verificar imports
python3 -c "from modules.auditors.seo_elements_detector import SEOElementsDetector, SEOElementsResult; print('SEOElementsDetector OK')"

# Verificar ssl
python3 -c "from modules.auditors.v4_comprehensive import V4ComprehensiveAuditor; a = V4ComprehensiveAuditor(None,None,None); print('SSL https:', a._check_ssl('https://test.com')); print('SSL http:', a._check_ssl('http://test.com'))"

# Verificar elementos KB ahora con datos reales
python3 -c "from modules.commercial_documents.v4_diagnostic_generator import ELEMENTO_KB_TO_PAIN_ID; print(f'{len(ELEMENTO_KB_TO_PAIN_ID)} elementos KB')"
```

---

## POST-IMPLEMENTACION (OBLIGATORIO)

```bash
python3 scripts/log_phase_completion.py \
    --fase GAP-IAO-01-02-B \
    --desc "Integracion 6 elementos: ssl trivial + contenido_extenso (CitabilityScorer) + nap_consistente (CrossValidator extendido) + 3 stubs (SEOElementsDetector)" \
    --archivos-mod "modules/auditors/seo_elements_detector.py,modules/data_validation/cross_validator.py,modules/auditors/v4_comprehensive.py,modules/commercial_documents/v4_diagnostic_generator.py" \
    --check-manual-docs
```

---

## NOTAS IMPORTANTES

1. **SEOElementsDetector es STUB** -- Los 3 elementos (open_graph, imagenes_alt, redes_activas) seguiran retornando False. La estructura esta lista para implementacion con BeautifulSoup.
2. **Orden de modificacion**: seo_elements_detector.py → cross_validator.py → v4_comprehensive.py → v4_diagnostic_generator.py
3. **CrossValidationResult** necesita campos nuevos: address_status, email_status, address_web, address_gbp
4. **Nap_consistente** ahora requiere WhatsApp + Address verificados (email es bonus)

---

**Fecha**: 2026-03-31
**Estado**: Listo para ejecutar GAP-IAO-01-02-B
