# Checklist de Implementación — Amaziliahotel Refactor v2
**Corregido post-forense**

## Resumen

| Fase | Descripción | Estado | Depende de | Archivo Real |
|------|-------------|--------|------------|--------------|
| FASE-1 | Fix Google Maps query en v4_comprehensive | ✅ Completada | - | `modules/auditors/v4_comprehensive.py` |
| FASE-2 | Fix hotel_schema con datos reales | ✅ Completada | FASE-1 | `modules/asset_generation/conditional_generator.py` + `v4_asset_orchestrator.py` |
| FASE-3 | Activar Content Scrubber (dead code) | ⏳ Pendiente | - | `modules/postprocessors/content_scrubber.py` + `v4_complete_orchestrator.py` |
| FASE-4 | Fix ROI — eliminar 24X hardcodeado template V6 | ⏳ Pendiente | - | `templates/propuesta_v6_template.md` + `v4_proposal_generator.py` |
| FASE-5 | Fix faq_page JSON-LD + monthly_report blanks | ⏳ Pendiente | - | `modules/asset_generation/conditional_generator.py` |
| FASE-6 | Fix Voice/AEO deprecated en propuesta | ⏳ Pendiente | - | `templates/propuesta_v6_template.md` + `proposal_asset_alignment.py` |
| FASE-7 | Fix capitalización region → .title() | ⏳ Pendiente | - | `modules/commercial_documents/v4_proposal_generator.py` |
| FASE-8 | Validación E2E + Documentación | ⏳ Pendiente | FASE-1 a FASE-7 | Varios |

## Estados

- ⏳ Pendiente: No iniciada
- 🔄 En progreso: Siendo ejecutada
- ✅ Completada: Verificada y registrada
- ❌ Bloqueada: Dependencia no cumplida

## Dependencias Reales (post-forense)

```
FASE-1 ─────► FASE-2 ──────────────────────────────┐
                                                     │
FASE-3 ──────────────────────────────────────────────┤
FASE-4 ──────────────────────────────────────────────┤
FASE-5 ──────────────────────────────────────────────┤  ──► FASE-8
FASE-6 ──────────────────────────────────────────────┤
FASE-7 ──────────────────────────────────────────────┘
```

**Ruta crítica**: FASE-1 → FASE-2 → FASE-8 (3 fases secuenciales)
**Paralelizables**: FASE-3, FASE-4, FASE-5, FASE-6, FASE-7 (entre sí, coordinar merge)

## Dependencias Detalladas

| Fase | Puede iniciar cuando | Bloqueada por |
|------|---------------------|---------------|
| FASE-1 | Siempre | - |
| FASE-2 | FASE-1 completada | FASE-1 |
| FASE-3 | Siempre | - |
| FASE-4 | Siempre | - |
| FASE-5 | Siempre | - |
| FASE-6 | Siempre | - |
| FASE-7 | Siempre | - |
| FASE-8 | FASE-1 a FASE-7 completadas | Todas |

## Criterios de Avance

| Fase | Criterio de éxito |
|------|-------------------|
| FASE-1 | geo_score > 0, lat/lng != 0.0, query usa nombre parseado |
| FASE-2 | hotel_schema con tel, addr, geo.lat con datos reales |
| FASE-3 | ContentScrubber importado en orquestador, COP COP = 0 en ambos docs |
| FASE-4 | Template V6 sin "24X", propuesta muestra ROI dinámico único |
| FASE-5 | faq_page.json existe (JSON-LD), monthly_report sin blanks |
| FASE-6 | Voice/AEO NO en propuesta, WhatsApp SÍ sigue activo |
| FASE-7 | "eje_cafetero" = 0, "Eje Cafetero" con mayúsculas |
| FASE-8 | Score >= 80, 4/4 validaciones, docs actualizadas |

## Registro de Ejecución

| Fase | Fecha | Sesión | Registrado |
|------|-------|--------|------------|
| FASE-1 | 2026-04-20 | 134 tests | ✅ Completada |
| FASE-2 | 2026-04-20 | 28 tests | ✅ Completada |
| FASE-3 | - | - | [ ] |
| FASE-4 | - | - | [ ] |
| FASE-5 | - | - | [ ] |
| FASE-6 | - | - | [ ] |
| FASE-7 | - | - | [ ] |
| FASE-8 | - | - | [ ] |
