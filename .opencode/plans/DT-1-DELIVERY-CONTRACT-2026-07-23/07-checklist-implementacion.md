# Checklist de Implementación — DT-1-DELIVERY-CONTRACT-2026-07-23

> **Plan**: DT-1-DELIVERY-CONTRACT-2026-07-23
> **Última actualización**: 2026-07-24
> **Estado**: En curso (FASE-A ✅, FASE-B ✅, FASE-C pendiente)

---

## Tabla de progreso

| Fase | Estado | Fecha cierre | Verificación |
|------|--------|-------------|-------------|
| FASE-A — Contrato canónico | ✅ COMPLETADA | 2026-07-24 | ✅ 10/10 tests |
| FASE-B — Pipeline físico | ✅ COMPLETADA | 2026-07-24 | ✅ 10/10 tests, 8/8 criteria |
| FASE-C — README dinámico | 🔒 BLOQUEADA (requiere B) | — | — |
| FASE-D — Tests de contrato | 🔒 BLOQUEADA (requiere C) | — | — |
| FASE-E — E2E + RELEASE | 🔒 BLOQUEADA (requiere D) | — | — |

---

## FASE-A — Contrato canónico y saneamiento de evidencia

### Estado: ✅ COMPLETADA

- [x] T1: `DeliveryAssetState` enum definido en `delivery_context.py` (7 valores)
- [x] T2: `DeliveryAssetEntry` dataclass con `from_skipped_asset()` y `from_generated_asset()`
- [x] T2.1: `from_skipped_asset()` asigna PRESENT_WITH_ISSUES si hay pain_ids con "conflict"
- [x] T2.1: `covered`, `requires_action`, `requires_review` son campos independientes
- [x] T2.2: `is_advisory` flag en `DeliveryAssetEntry`; `from_generated_asset()` detecta guías
- [x] T3: `DeliveryContext` dataclass con propiedades de agrupación por estado
- [x] T3.1: `DeliveryContext.from_asset_generation_report()` classmethod implementado
- [x] T3.2: `from_asset_generation_report()` retorna contexto vacío si el reporte no existe
- [x] T3.3: `DeliveryContext.advisory_assets` propiedad implementada
- [x] T4: `AssessmentBuilder.with_assets()` propaga `pain_ids_affected` en `skipped_assets`
- [x] T4.1: Import limpio de los nuevos símbolos
- [x] Verif: 10 tests existentes del packager PASS

---

## FASE-B — Pipeline físico ZIP ↔ manifest

### Estado: ✅ COMPLETADA

- [x] T1: `_collect_files()` usa `as_posix()` en todos los destinos
- [x] T1.1: ZIP generado no contiene rutas con `\\`
- [x] T2: `create_manifest()` registra tamaños reales (>0) para metaarchivos
- [x] T2.1: `total_size_bytes` coincide con suma real (margen ±1%)
- [x] T2.2: `total_files` coincide con `len(zipfile.namelist())`
- [x] T3: `_make_zip_filename()` produce nombres consistentes
- [x] T4: `_validate_zip()` implementado y llamado en `package()`
- [x] T4.1: ZIP válido → `_validate_zip()` retorna lista vacía
- [x] T5: `package()` carga `asset_generation_report.json` y construye `DeliveryContext` cuando `hotel_dir` disponible
- [x] T5.1: Sin `hotel_dir` o sin reporte, `delivery_context` queda None (legacy)
- [x] Verif: 10 tests existentes del packager PASS

---

## FASE-C — README derivado del delivery context

### Estado: 🔒 BLOQUEADA (requiere B)

- [ ] T1: Template `delivery_readme_template.md` sin nombres de archivo hardcodeados
- [ ] T1.1: NO contiene `boton_whatsapp.html`, `hotel-schema.json`, `geo_playbook.md`, `faq_page.md`
- [ ] T2: `_generate_package_structure()` produce estructura desde `files` reales
- [ ] T3: Sección "Already Present" generada para assets PRESENT_IN_PRODUCTION
- [ ] T3.1: Sección "Present but Requires Review" generada para PRESENT_WITH_ISSUES
- [ ] T3.2: Sección "Estimated Assets" generada para ESTIMATED
- [ ] T3.3: Sección "Advisory Guides" generada para assets con `is_advisory=True`
- [ ] T4: `create_readme()` acepta `DeliveryContext` y genera secciones dinámicas
- [ ] T4.1: Sin `DeliveryContext` → comportamiento legacy preservado
- [ ] T4.2: `{{PACKAGE_FILENAME}}` coincide con nombre real del ZIP
- [ ] Verif: 10 tests existentes del packager PASS

---

## FASE-D — Tests de contrato y gate de no-regresión

### Estado: 🔒 BLOQUEADA (requiere C)

- [ ] T1: `test_delivery_contract.py` creado con tests de `DeliveryAssetEntry`
- [ ] T1.1: Tests para PRESENT_IN_PRODUCTION, PRESENT_WITH_ISSUES, DELIVERED, ESTIMATED, FAILED, INDETERMINATE, verification_failed
- [ ] T1.2: Tests de DeliveryContext.from_asset_generation_report: reporte ausente, reporte inválido
- [ ] T1.3: Tests de is_advisory: guía detectada, requires_action=False, requires_review=True
- [ ] T2: Tests de manifest ZIP: rutas POSIX, total_files, tamaños, entradas idénticas
- [ ] T2.1: `test_manifest_paths_posix` pasa
- [ ] T2.2: `test_manifest_total_files_matches_zip` pasa
- [ ] T2.3: `test_readme_size_not_zero` pasa
- [ ] T3: Tests de README ↔ ZIP: no missing refs, filename, estructura real, sin hardcodeos
- [ ] T3.1: `test_readme_does_not_reference_missing_files` pasa
- [ ] T3.2: `test_readme_no_hardcoded_whatsapp_button` pasa
- [ ] T4: `DeliveryValidationError` integrado como gate obligatorio
- [ ] T4.1: ZIP inválido → excepción lanzada
- [ ] Verif: Suite completa `pytest tests/delivery/ -v` PASS (29+ tests)

---

## FASE-E — E2E (Zi One) + RELEASE

### Estado: 🔒 BLOQUEADA (requiere D)

- [ ] T1: `v4complete --url https://zione.co/` ejecutado exitosamente
- [ ] T0: Datos operativos de `output/clientes/zi-one-luxury_onboarding.yaml` verificados
- [ ] T1.0: Directorio `output/ZiOne/v4_complete/` limpiado antes de la ejecución
- [ ] T1.1: ZIP generado en `output/ZiOne/v4_complete/deliveries/`
- [ ] T1.2: Evidencia copiada a `evidence/fase-E/`
- [ ] T2: Verificación post-v4complete del delivery
- [ ] T2.1: WhatsApp NO está en ZIP como archivo entregable
- [ ] T2.2: WhatsApp aparece en sección de presencia/revisión
- [ ] T2.3: Manifest rutas POSIX, tamaños reales, total_files correcto
- [ ] T2.4: `_validate_zip()` pasa sin errores
- [ ] T2.5: README no contiene hardcodeos
- [ ] T2.6: ZIP filename correcto en README
- [ ] T3: RELEASE
- [ ] T3.1: VERSION.yaml bump (verificando versión previa antes)
- [ ] T3.2: CHANGELOG.md entrada de versión completa
- [ ] T3.3: `sync_versions.py` ejecutado
- [ ] T3.4: GUIA_TECNICA.md nota técnica
- [ ] T3.5: DOMAIN_PRIMER.md regenerado
- [ ] T3.6: `run_all_validations.py --quick` PASS
- [ ] T3.7: Commit realizado
- [ ] T4: Análisis post-implementación
- [ ] T4.1: `08-analisis-post-implementacion.md` completado sin placeholders
- [ ] T4.2: Matriz de verificación 14/14 hallazgos (F-01 a F-14) completada
- [ ] T4.3: Lecciones aprendidas de TODAS las fases documentadas en §9
- [ ] T4.4: Sección E de `09-documentacion-post-proyecto.md` actualizada

---

## Leyenda de estados

| Símbolo | Significado |
|---------|------------|
| ⬜ | PENDIENTE — No iniciado |
| 🔄 | EN CURSO — Trabajando activamente |
| ✅ | COMPLETADO — Todos los checks pasan |
| ❌ | FALLIDO — Bloqueado por error |
| 🔒 | BLOQUEADA — Depende de fase anterior |
| ⏭️ | SALTADA — Decisión explícita de no ejecutar |

## Dependencias

```
A ✅ → B ✅ → C 🔒 → D 🔒 → E 🔒
```
