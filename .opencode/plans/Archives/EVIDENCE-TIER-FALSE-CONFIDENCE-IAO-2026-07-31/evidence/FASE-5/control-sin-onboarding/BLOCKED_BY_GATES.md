# 🚫 Publicación Bloqueada por Gates de Calidad

**Fecha**: 2026-07-31T16:49:22.520797
**Hotel**: Hotelvisperas
**URL**: https://www.hotelvisperas.com/es
**Status**: NOT_READY

## Gates Fallidos (2)

### critical_recall

- **Mensaje**: Critical recall metric not found in assessment
- **Sugerencia**: Ensure audit results include critical issue detection data

### proposal_asset_alignment

- **Mensaje**: 2 missing: Botón de WhatsApp, Schema Hotel
- **Sugerencia**: Alignment 71% (2 services missing) is below 80% threshold. Review asset generation pipeline to ensure all promised services produce deliverables before publication.
- **Valor**: 0.7142857142857143


## 🚨 Commercial Gates Bloqueantes

Los siguientes gates comerciales impidieron la generación de la propuesta. **No vuelva a ejecutar sin resolverlos** — la re-ejecución idéntica fallará igual.

- **CG-ROI-NEGATIVE**: Beneficio neto 6m negativo ($-1,330,590 COP) y ROI 0.45X sin plan de onboarding alternativo. Una propuesta que dice 'págueme para perder dinero' no cierra.
- **CG-TECH-JARGON**: Jerga técnica encontrada en vista gerencia: Schema, AEO, IAO, Open Graph, Gemini. El decisor entiende ocupación, reservas directas, comisiones, WhatsApp, reseñas y caja; no compra por leer pesos internos de scoring.

> ⚠️ Estos gates evalúan la viabilidad comercial de la propuesta. Resuélvalos antes de re-ejecutar `v4complete`.

---

**Acción requerida**: Resuelva los commercial gates bloqueantes y los publication gates fallidos antes de re-ejecutar.

El reporte `v4_complete_report.json` y `gate_report.json` se generaron
para debugging — revise esos archivos para información detallada.
