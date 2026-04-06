# Dependencias de Fases — GAP-IAO-01

## Diagrama de dependencias (ACTUALIZADO v3)

```
FASE-0
   │
   ├──→ GAP-IAO-01-01 (auditoría de datos)
   │         │
   │         └──→ GAP-IAO-01-00 (auditoría runtime)
   │                   │
   │                   ▼
   │        GAP-IAO-01-02 (diagnóstico KB + Pain ID Alignment)
   │                   │
   │                   ├──→ GAP-IAO-01-02-B (integración 6 elementos)
   │                   │              │
   │                   │              └──→ GAP-IAO-01-02-C (assets IAO)
   │                   │                            │
   │                   │◄───────────────────────────┘
   │                   │
   │                   └──→ GAP-IAO-01-03 (propuesta)
   │                             │
   │                             └──→ GAP-IAO-01-04 (assets)
   │                                       │
   │                                       └──→ GAP-IAO-01-05 (GA4 opcional)
```

## Conflictos de archivos

| Fase | Archivos que modifica | Riesgo de conflicto |
|------|----------------------|-------------------|
| GAP-IAO-01-02 | `v4_diagnostic_generator.py`, `pain_solution_mapper.py`, `asset_catalog.py`, `data_structures.py` | ⚠️ MEDIO |
| GAP-IAO-01-02-B | `v4_comprehensive.py`, `cross_validator.py`, `seo_elements_detector.py` (nuevo) | ⚠️ MEDIO |
| GAP-IAO-01-02-C | `conditional_generator.py`, `asset_catalog.py` | ⚠️ MEDIO |
| GAP-IAO-01-03 | `v4_proposal_generator.py`, `data_structures.py` | ⚠️ MEDIO |
| GAP-IAO-01-04 | `conditional_generator.py`, `pain_solution_mapper.py` | ⚠️ MEDIO |
| GAP-IAO-01-05 | `modules/analytics/google_analytics_client.py` (nuevo) | BAJO |

## Estado de componentes "huérfanos"

| Componente | Status | Verificación en 01-00 |
|------------|--------|------------------------|
| IATester.test_hotel() | ✅ FUNCIONA | Implementación real, requiere API keys |
| BingProxy.test_visibility() | ✅ FUNCIONA | Scraping real a Bing con BeautifulSoup |
| AEOKPIs.calculate_composite_score() | ✅ FUNCIONA | Retorna -1 si no hay datos suficientes |

## Desconexiones cerradas (PRE-GAP-IAO-01-02 + v2 + v3)

| # | Desconexión | Solución | Versión |
|---|-------------|----------|---------|
| 1 | No existe FALTANTE_TO_PAIN_ID_MAP | Crear `ELEMENTO_KB_TO_PAIN_ID` en v4_diagnostic_generator.py | v1 |
| 2 | score_ia usa str en vez de int | Cambiar a `Optional[int]` con `-1` para N/A | v1 |
| 3 | 6 pain_ids nuevos no existen en mapper | Agregar a `PAIN_SOLUTION_MAP` | v1 |
| 4 | 5 assets nuevos no existen en ASSET_CATALOG | Agregar como `MISSING` | v1 |
| 5 | Mezcla de brechas vs faltantes | Documentar separación en código | v1 |
| 6 | Pain IDs con asset MISSING se monetizaban | Filtro `_asset_para_pain()` en generate() | v1 |
| 7 | schema_reviews → pain_id incorrecto | Crear `no_schema_reviews` separado de `missing_reviews` | v3 |
| 8 | faltantes incluye assets MISSING | Separar `faltantes_monetizables` / `faltantes_no_monetizables` | v3 |
| 9 | Dependencias desactualizadas | Actualizar diagrama con B y C | v3 |
| 10 | Restricción vs 02-C contradictoria | Aclarar: implementar assets MISSING, no agregar nuevos | v3 |
| 11 | Brechas no cubren todos elementos | Documentar asimetría como diseño intencional | v3 |

## Archivos existentes — Reglas de modificación

| Archivo | Regla | Razón |
|---------|-------|-------|
| `data_models/aeo_kpis.py` | NO crear nueva clase. Usar si funciona. | Preservar implementación existente |
| `modules/commercial_documents/data_structures.py` | Solo agregar campos (backwards compatible) | No romper código existente |
| `modules/asset_generation/asset_catalog.py` | **PERMITIDO** implementar assets con status `MISSING` | GAP-IAO-01-02-C implementa 5 assets que YA EXISTEN como MISSING |

**ACLARACIÓN sobre asset_catalog.py**:
- La restricción original era **NO AGREGAR TIPOS DE ASSET NUEVOS**
- GAP-IAO-01-02-C **IMPLEMENTA** (cambia status de MISSING a IMPLEMENTED) assets que ya están definidos
- **NO ES CONTRADICCIÓN** — es implementación de algo que ya existe en el catálogo

## Elementos KB detectables (de GAP-IAO-01-01)

| Detectables ahora | Requieren detectores nuevos |
|-------------------|---------------------------|
| 5 de 12 | 7 de 12 |

Ver `IA_MEASUREMENT_MAP.md` para detalle completo.

## Condiciones de skip

- **GAP-IAO-01-05 puede saltarse** si el pipeline básico funciona sin GA4.
- **GAP-IAO-01-00 es CRÍTICA** — no saltar. Sin ella, 01-02 implementa código con dependencias rotas.
- **GAP-IAO-01-02-B es CRÍTICA** — sin ella, GAP-IAO-01-03 no tiene datos reales para monetización.
- **GAP-IAO-01-02-C es RECOMENDADA** — sin ella, 5 pain_ids no pueden generar assets (siguen siendo MISSING).

---

## Registro de cambios vs plan anterior

| Item | Antes | Ahora |
|------|-------|-------|
| Fases totales | 5 + 1 opcional | 7 + 1 opcional |
| Fases 01-02 | Asumía 12 elementos detectables | Solo 5-6 reales + B + C |
| IATester/BingProxy/AEOKPIs | "Ya existen, usar" | Requiere verificar 01-00 |
| Elementos KB faltantes | No documentados | 7/12 requieren detectores |
| Assets MISSING | No se iban a implementar | GAP-IAO-01-02-C los implementa |
| schema_reviews | Mapeado a missing_reviews | CORREGIDO a no_schema_reviews |

---

## Registro de completitud

| Fase | Fecha | Estado |
|------|-------|--------|
| FASE-0 | 2026-03-30 | ✅ Completada |
| GAP-IAO-01-01 | 2026-03-30 | ✅ Completada |
| GAP-IAO-01-00 | 2026-03-31 | ✅ Completada |
| GAP-IAO-01-02 | 2026-03-31 | ✅ Completada |
| GAP-IAO-01-02-B | 2026-03-31 | ✅ Completada |
| GAP-IAO-01-02-C | 2026-03-31 | ✅ Completada |
| GAP-IAO-01-03 | — | ⏳ Pendiente |
| GAP-IAO-01-04 | — | ⏳ Pendiente |
| GAP-IAO-01-05 | 2026-04-01 | ✅ Completada |

---

## Validación de Integración

Después de cada fase, ejecutar test de integración:

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python -c "from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator; print('Import OK')"
python -c "from modules.auditors.v4_comprehensive import V4ComprehensiveAuditor; print('Auditor Import OK')"
```
