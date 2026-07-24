# Documentación Post-Proyecto — DT-1-DELIVERY-CONTRACT-2026-07-23

> **Plan**: DT-1-DELIVERY-CONTRACT-2026-07-23
> **Versión target**: v4.63.1
> **Creado**: 2026-07-23
> **Completar durante/después de FASE-E (RELEASE)**

---

## Sección A: Registro de decisiones de diseño

| # | Decisión | Justificación | Fecha |
|---|---------|---------------|-------|
| D1 | `DeliveryAssetState` como Enum, no como strings libres | Tipado fuerte evita divergencias entre capas | — |
| D2 | `covered`, `requires_action`, `requires_review` como campos independientes | Un asset puede estar cubierto pero requerir revisión (ej: WhatsApp con conflicto) | — |
| D3 | `from_skipped_asset()` detecta conflicto vía `pain_ids_affected` | No requiere nuevo campo en el schema de skipped_assets | — |
| D4 | Rutas POSIX forzadas en manifest y ZIP vía `as_posix()` | Portabilidad cross-OS; el estándar ZIP usa `/` | — |
| D5 | Manifest reescrito en 3 pasadas para tamaños reales | Evita dependencia circular (README → manifest → README) | — |
| D6 | Template completamente reescrita (no parcheada) | La template original tenía 100% contenido hardcodeado; reescribir es más seguro que parchear | — |
| D7 | `DeliveryContext` opcional en `create_readme()` | Backward compatibility: hoteles sin datos de presencia siguen funcionando | — |
| D8 | Gate de no-regresión como excepción (`DeliveryValidationError`) | Bloquea entrega de ZIP inconsistente; no permite silent failure | — |
| D9 | `DeliveryContext.from_asset_generation_report()` como puente pipeline→packager | Resuelve GAP-2: el packager no reimplementa lógica de negocio, consume un contexto pre-construido | — |
| D10 | `is_advisory` flag para distinguir guías de assets instalables | Resuelve GAP-1: whatsapp_conflict_guide no debe aparecer como instrucción de instalación | — |
| D11 | Limpieza de `output/ZiOne/v4_complete/` antes de v4complete en FASE-E | Evita evidencia stale mezclada con nueva (lección del contexto DT-1 §11) | — |
| D12 | Verificación de versión previa antes del bump en FASE-E | Evita bump incorrecto si RELEASE de ASSET-ALIGNMENT no se ejecutó | — |

## Sección B: Archivos creados

| Archivo | Tipo | Líneas estimadas |
|---------|------|-----------------|
| `tests/delivery/test_delivery_contract.py` | Tests | ~320 |
| `08-analisis-post-implementacion.md` | Análisis | ~200 líneas (template, se completa en FASE-E T4) |

## Sección C: Archivos modificados

| Archivo | Cambio | Riesgo de regresión |
|---------|--------|-------------------|
| `modules/delivery/delivery_context.py` | +DeliveryAssetState, +DeliveryAssetEntry, +DeliveryContext | Bajo: solo agrega símbolos |
| `modules/delivery/delivery_packager.py` | Rutas POSIX, tamaños reales, README dinámico, validación | Medio: cambia orden de operaciones en `package()` |
| `modules/assessment_builder.py` | +pain_ids_affected en skipped_assets | Bajo: solo agrega campo |
| `templates/delivery_readme_template.md` | Reescritura completa | Medio: cambio total de template |
| `VERSION.yaml` | Bump a 4.63.1 | Bajo: estándar |
| `CHANGELOG.md` | Entrada [4.63.1] | Bajo: estándar |
| `docs/GUIA_TECNICA.md` | Nota técnica v4.63.1 | Bajo: estándar |

## Sección D: Tests agregados

| Archivo | # Tests | Cobertura |
|---------|---------|-----------|
| `tests/delivery/test_delivery_contract.py` | 19+ | Estados canónicos, manifest, ZIP, README, validación, from_asset_generation_report, is_advisory |
| `tests/delivery/test_delivery_packager.py` | 10 (existentes, sin cambios) | Empaquetado básico |

Total: 29+ tests.

## Sección E: Lecciones aprendidas

> **Nota**: El análisis detallado está en `08-analisis-post-implementacion.md`. Esta sección contiene el resumen ejecutivo.

(Completar durante/después de la ejecución de FASE-E T4, a partir de `08-analisis-post-implementacion.md` §9)

- ¿Qué funcionó bien?
- ¿Qué fue más difícil de lo esperado?
- ¿Qué se haría diferente?
- ¿Qué deuda técnica queda?

## Sección F: Deuda técnica residual

| ID | Descripción | Severidad | Plan |
|----|------------|-----------|------|
| TD-1 | `coherence_validation_post_gen.json` todavía reporta `promised_assets_exist: false` para `whatsapp_button` aunque el gate de alignment lo considera cubierto | Media | Futuro: unificar semántica de "cubierto" entre CoherenceValidator y proposal_asset_alignment |
| TD-2 | `proposal_asset_matrix.json` tiene `NO_BREACH` para servicios que el gate considera aligned | Media | Futuro: sincronizar ProposalAssetMatrix con alignment gate |
| TD-3 | `monthly_report_generator.py` tiene tabla de "Assets Entregados" hardcodeada | Media | Fuera del alcance de este plan; requiere intervención separada |
| TD-4 | `delivery_quality_report.json` lee `coherence_validation.json` (pre-gen) en vez del post-gen | Baja | Futuro: usar score post-generación para delivery quality |

## Sección G: Verificación de aceptación

- [ ] Zi One: README no lista `boton_whatsapp.html` como entregable
- [ ] Zi One: WhatsApp en sección de presencia/revisión
- [ ] Zi One: Guía de conflicto WhatsApp en sección "Advisory Guides" (no en instrucciones de instalación)
- [ ] Manifest: rutas POSIX, tamaños reales, totales correctos
- [ ] `_validate_zip()`: sin errores
- [ ] `DeliveryContext.from_asset_generation_report()` construido automáticamente en `package()`
- [ ] 29+ tests: todos PASS
- [ ] `run_all_validations.py --quick`: PASS
- [ ] Output de Zi One limpiado antes de v4complete (no evidencia stale)
- [ ] Versión verificada antes del bump
- [ ] CHANGELOG, VERSION, GUIA_TECNICA: actualizados
- [ ] Commit: realizado con mensaje descriptivo
