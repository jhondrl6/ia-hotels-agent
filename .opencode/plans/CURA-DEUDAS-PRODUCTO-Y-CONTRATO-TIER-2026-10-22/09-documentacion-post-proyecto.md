# Documentación Post-Proyecto — CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22

> Acumulativo. **Fuente canónica del número por fase** — lo consume FASE-RELEASE. Cada fase completa su columna «Fase» al cerrar. Los demás cierres referencian este archivo, no re-transcriben cifras.

## Sección A: Módulos Nuevos

| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|
| _(ninguno previsto: todas las curas son sobre módulos existentes)_ | — | — | — |

## Sección B: Funcionalidades Nuevas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| Render condicionado al `evidence_tier` | `commercial_documents` | Los 2 claims de totalidad detectados por el revisor emiten variante honesta con tier no-A; la propuesta y el diagnóstico comparten el contrato | FASE-B |
| Veredicto condicional con causa estructurada | `quality_gates/tribunal` | `APROBADO-CONDICIONAL` + `conditional_reason`: techo de analytics, onboarding incompleto o cláusulas no certificables | FASE-C |
| Contrato GBP unificado en dos caminos | `scrapers` / `utils` / `commercial_documents` | `get_detected_issues` y `PainSolutionMapper` comparten vocabulario; “sin schema” no se convierte en abandono de perfil | FASE-D |
| Lector único de benchmarks regionales | `utils` | Puente de esquema; cinco tablas derivadas o retiradas; verificador real cableado | FASE-E |
| Umbrales por semántica | `config` / módulos consumidores | Mínimo, oportunidad, banda de rúbrica y objetivo con nombre propio, sin colapsarlos en un valor único | FASE-F |
| Guardián por existencia de atributo | `tests` (superficie pública) | Extiende el guardián estático de nombres a existencia sobre la clase importada | FASE-A |
| Retiro de la ruta `spark` | `main.py` | El comando informa su retiro y no muere por `AttributeError`; el lector latente de `gap_analyzer` se corrige | FASE-A |
| Score GBP honesto | `scrapers` | Publica sobre `/90` y retira la rama API no implementada | FASE-H1 |
| Stub de Booking retirado | `scrapers` | `found=False` con `data_status=STUB_RETIRADO`; el scraper real del producto no se toca | FASE-H1 |

## Sección D: Métricas Acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| Tests nuevos (delta, par pre/post por fase — R2.3/R2.7) | _(ver `evidence/…/FASE-X/baseline-pre-post.md` por fase)_ | — |
| Mutation checks con par rojo/verde en evidencia (R2.8) | _(contar al cierre: AC1, AC2, AC3, AC5, AC8)_ | — |
| Corridas `v4complete` de este plan | 0 / 1 prevista (después de E2E-PRE) | FASE-E2E |
| Ensayos E2E-PRE sin inferencia | 0 / 1 previsto | FASE-E2E-PRE |
| Presupuesto por fase (unidad `tool_use`, corte «listo para revisión») | _(auto-reporte por fase en `10-analisis` §Resumen; instrumento legado no comparable si el transcript no es compatible)_ | — |

## Sección E: Archivos Afiliados Actualizados

| Archivo | Cambio | Fase |
|---------|--------|------|
| _(se completa al cierre de cada fase)_ | — | — |
