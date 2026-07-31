# Dependencias entre fases — DT-1-DELIVERY-CONTRACT-2026-07-23

> **Plan**: DT-1-DELIVERY-CONTRACT-2026-07-23
> **Actualizado**: 2026-07-23

---

## Diagrama de dependencias

```
FASE-A (contrato canónico)
  │
  │  Define DeliveryAssetState, DeliveryAssetEntry, DeliveryContext
  │  Sin dependencias previas. Es la base de todo.
  │
  └── FASE-B (pipeline físico)
       │
       │  Depende de: FASE-A (usa DeliveryContext para el manifest)
       │  Modifica: create_manifest(), _create_zip(), package()
       │  Agrega: validación post-zip
       │
       └── FASE-C (README dinámico)
            │
            │  Depende de: FASE-A (usa DeliveryAssetState), FASE-B (rutas POSIX)
            │  Modifica: create_readme(), delivery_readme_template.md
            │  Agrega: _generate_package_structure(), _generate_state_sections()
            │
            └── FASE-D (tests + gate)
                 │
                 │  Depende de: FASE-A, FASE-B, FASE-C
                 │  Modifica: test_delivery_packager.py
                 │  Agrega: test_delivery_contract.py, _validate_delivery_zip()
                 │
                 └── FASE-E (E2E + RELEASE + Análisis)
                      │
                      │  Depende de: FASE-A, FASE-B, FASE-C, FASE-D
                      │  T0: Verifica datos operativos (output/clientes)
                      │  T1: Ejecuta v4complete --url https://zione.co/
                      │  T2: Verifica ZIP, README, manifest, cross-artifact
                      │  T3: RELEASE: CHANGELOG, VERSION, sync, commit
                      │  T4: Análisis post-implementación: 14 hallazgos + lecciones
```

## Tabla de conflictos de archivos

| Archivo | FASE-A | FASE-B | FASE-C | FASE-D | FASE-E | Conflicto? |
|---------|--------|--------|--------|--------|--------|------------|
| `modules/delivery/delivery_packager.py` | — | MOD (create_manifest, _create_zip, package T5) | MOD (create_readme, package call) | — | — | Secuencial: B define estructura + carga context, C reemplaza llamada create_readme |
| `modules/delivery/delivery_context.py` | MOD (enum + dataclasses + from_asset_generation_report) | — | — | — | — | Solo A |
| `templates/delivery_readme_template.md` | — | — | MOD (template + Advisory Guides) | — | — | Solo C |
| `tests/delivery/test_delivery_packager.py` | — | — | — | MOD (tests) | — | Solo D |
| `tests/delivery/test_delivery_contract.py` | — | — | — | NEW | — | Solo D |
| `main.py` | — | — | — | — | — | No se modifica |
| `modules/assessment_builder.py` | MOD (skipped_assets propagation) | — | — | — | — | Solo A |

## Evaluación R3 por fase

| Fase | T1 | T2 | T3 | T4 | T5 | Cmd largo | Total tareas | R3 |
|------|----|----|----|----|----|-----------|-------------|-----|
| A | Definir enum | Resolver semántica | Crear dataclass + from_report | Propagar en builder | — | 0 | 4 | ✅ |
| B | Rutas POSIX | Tamaños reales | Filename único | Verificador post-zip | Carga DeliveryContext | 0 | 5 | ✅ |
| C | Template modular | Package Structure | Secciones por estado + Advisory | Adaptar create_readme | — | 0 | 4 | ✅ |
| D | Tests estados + report missing/invalid | Tests manifest | Tests cross-artifact | Gate no-regresión | — | 0 | 4 | ✅ |
| E | T0: Verificar output/clientes | T1: v4complete Zi One | T2: Verificación delivery | T3: RELEASE (docs+sync) | T4: Análisis post-implementación | 1 (v4complete) | 5 | ✅ |

## Estimación de iteraciones por fase

| Fase | Fixed costs | Phase work | Total estimado | Budget (60) |
|------|------------|------------|----------------|-------------|
| A | ~28 | ~24 | ~52 | ✅ |
| B | ~28 | ~22 | ~50 | ✅ |
| C | ~28 | ~22 | ~50 | ✅ |
| D | ~28 | ~24 | ~52 | ✅ |
| E | ~28 | ~35 (incluye v4complete + análisis) | ~63 | ✅ |

## Orden de ejecución recomendado

FASE-A → FASE-B → FASE-C → FASE-D → FASE-E

Cada fase en una sesión nueva. No adelantar trabajo de fases posteriores.
