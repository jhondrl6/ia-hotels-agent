# Veredicto Final — AMH_REFACTOR_V2 RELEASE

## Ejecucion
- Fecha: 2026-04-20 19:02 -05
- Comando: `main.py v4complete --url https://amaziliahotel.com/`
- Duracion: ~58 segundos
- Costo API: ~$0.05 USD (Places API + LLM)

---

## Scorecard

| GAP | Criterio | Resultado | Evidencia |
|-----|----------|-----------|-----------|
| G2 | hotel_schema: tel, addr, geo reales | ❌ FAIL | telephone/streetAddress/latitude MISSING en schema |
| G4 | faq_page genera .json (JSON-LD) | ✅ PASS | JSON-LD generado, CSV heredado de ejecucion anterior |
| G7 | monthly_report: 0 blanks "_____" | ✅ PASS | 0 blanks |
| G10 | Propuesta sin "(24X)" | ✅ PASS | 0 instancias en latest proposal |
| G13 | Region en Title Case | ❌ FAIL | "eje_cafetero" lowercase en audit_report.json |
| G14 | Cero "COP COP" en ambos docs | ❌ FAIL | 5x COP COP en proposal (scrubber lo saltó) |
| NG4 | geo_score > 0 | ✅ PASS | geo_score=62 (GBP verified) |
| NG5 | Scrubber ejecutado (COP COP = 0) | ⚠️ PARTIAL | Diagnostic limpio, proposal NO scrapeado |
| -- | publication_ready = true | ❌ FAIL | false — content_quality BLOCKED |
| -- | coherence >= 0.8 | ✅ PASS | 0.89 |
| -- | asset_confidence >= 0.7 avg | ❌ FAIL | 3/10 above 0.7 |
| -- | Region = "Eje Cafetero" | ❌ FAIL | "eje_cafetero" lowercase |

---

## Metricas Pipeline
- publication_ready: **false**
- coherence: **0.89** (umbral: 0.8) ✅
- gates_passed: **8/9** (1 blocked: content_quality)
- assets_generated: 10 (3 above 0.7 confidence)
- alignment: 1/5 aligned, 1 missing (Botón de WhatsApp)

---

## Veredicto: ❌ RECHAZADO

**Razones CRITICAS (GATE-BREAKING)**:

1. **G14 (CRITICO)**: COP COP persiste en proposal. El ContentScrubber tiene bypass para proposal: `"[SKIP] Proposal document not available for scrubbing"`. La hipotesis de FASE-3 era que el scrubber limpiaria la propuesta, pero NO se ejecuto sobre ella.

2. **publication_ready = false**: Gate content_quality bloqueado por 5x COP COP en lineas 30, 40, 105, 106, 107 de la propuesta.

3. **G2 (ALTO)**: hotel_schema genera estructura vacia. FASE-2 prometia datos reales de audit/GBP pero el schema recibe lat:0.0, lng:0.0 en la consulta Places.

4. **G13 (ALTO)**: Region "eje_cafetero" en lowercase en audit_report.json — FASE-7 aplico .title() en proposal_generator.py pero no hay evidencia de que el audit reporte haya sido regenerado con este fix.

---

## Lecciones

**Lo que funciono**:
- Pre-flight verification correcta (codigo tiene los fixes de FASE-1 a FASE-7)
- coherence_score 0.89 supera umbral 0.8
- G4 (faq_page JSON-LD): FASE-5 funciono correctamente
- G7 (monthly_report blanks): FASE-8 sin blanks funciono
- G10 (24X): Template V6 sin 24X funciono

**Lo que NO funciono como se esperaba**:
- **Scrubber bypass en proposal**: El scrubber detecto "proposal not available" y lo ignoro. El codigo tiene los fixes (ContentScrubber importado, 2 instancias en main.py) pero en tiempo de ejecucion no se aplico a la propuesta.
- **hotel_schema con lat:0.0**: El Places API se consulto con coordenadas invalidas, resultando en place_found=false y datos vacios en schema. La deduplicacion de queries Places no funciono para este caso.
- **Region capitalization**: El fix de FASE-7 (.title()) esta en proposal_generator.py pero el audit_report.json que se compara en el scorecard fue generado ANTES de este fix (o region viene del audit, no del generator).

**Hipotesis del plan**:
- PARCIALMENTE CORRECTA: Las fases 3-7 introdujeron los fixes correctos en el codigo, pero no todos se ejecutaron correctamente en el pipeline E2E de esta ejecucion.

---

## Siguiente paso
- **RECHAZADO**: Re-diagnosticar el problema raiz del scrubber bypass y la consulta Places con lat:0.0.
- NO iterar el mismo plan — las lecciones indican que se necesita un nuevo diagnostico de por que el scrubber no alcanza la propuesta y por que las coordenadas no se resuelven.
