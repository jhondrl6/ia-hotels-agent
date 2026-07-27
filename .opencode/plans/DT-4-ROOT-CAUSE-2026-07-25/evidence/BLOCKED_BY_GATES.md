# 🚫 Publicación Bloqueada por Gates de Calidad

**Fecha**: 2026-07-27T14:04:59.827278
**Hotel**: Zione
**URL**: https://zione.co/
**Status**: NOT_READY

## Gates Fallidos (1)

### coverage_no_silent_drop

- **Mensaje**: Brecha(s) sin cobertura ni justificacion: no_whatsapp_visible
- **Sugerencia**: Agregar las brechas faltantes al diagnostico, justificarlas como JUSTIFIED_SKIP/BLOCKED/MAPPED_TO_SERVICE, o incluirlas en la propuesta.
- **Valor**: 0.8888888888888888


## 🚨 Commercial Gates Bloqueantes

Los siguientes gates comerciales impidieron la generación de la propuesta. **No vuelva a ejecutar sin resolverlos** — la re-ejecución idéntica fallará igual.

- **CG-ROI-NEGATIVE**: Beneficio neto 6m negativo ($-1,330,590 COP) y ROI 0.45X sin plan de onboarding alternativo. Una propuesta que dice 'págueme para perder dinero' no cierra.
- **CG-TECH-JARGON**: Jerga técnica encontrada en vista gerencia: Schema, AEO, IAO, Open Graph, Gemini. El decisor entiende ocupación, reservas directas, comisiones, WhatsApp, reseñas y caja; no compra por leer pesos internos de scoring.

> ⚠️ Estos gates evalúan la viabilidad comercial de la propuesta. Resuélvalos antes de re-ejecutar `v4complete`.

---

**Acción requerida**: Resuelva los commercial gates bloqueantes y los publication gates fallidos antes de re-ejecutar.

El reporte `v4_complete_report.json` y `gate_report.json` se generaron
para debugging — revise esos archivos para información detallada.
