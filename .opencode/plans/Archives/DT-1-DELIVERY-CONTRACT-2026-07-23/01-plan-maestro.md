# Plan Maestro: DT-1 — Delivery Contract and Cross-Artifact Consistency

> **ID del plan**: DT-1-DELIVERY-CONTRACT-2026-07-23
> **Versión del plan**: v1.0
> **Fecha de diseño**: 2026-07-23
> **Origen**: Contexto validado DT-1-README-DELIVERY-PRESENT-IN-PRODUCTION.md v2.0
> **Repositorio**: `/mnt/c/Users/Jhond/Github/iah-cli`
> **Commit base**: `df75222f2b1ddce9e0761afbbea388831ea88a02`
> **Severidad**: ALTA — confiabilidad de entrega al cliente

---

## 0. Veredicto del contexto

El ZIP de entrega contiene 46 archivos y `boton_whatsapp.html` no está presente (el pipeline correctamente lo omitió por `present_in_production`). Sin embargo, el `README_DELIVERY.md` dentro del mismo ZIP:

- lista `boton_whatsapp.html` en `Package Structure`;
- incluye instrucciones para instalarlo;
- lo incluye en el timeline y checklist.

El cliente busca un archivo que no fue entregado. Causa raíz confirmada:

> El README se genera desde una template narrativa estática, no desde la lista final de archivos del ZIP ni desde un contrato canónico de estados de assets.

Además, la validación encontró 14 hallazgos adicionales (F-01 a F-14) que amplían el alcance sistémico:
rutas `\\` en manifest, tamaños `0` para metaarchivos, divergencia semántica entre 6+ capas del pipeline, tests que pasan pero no validan el contrato de entrega, y presencia en producción que no equivale a correcto.

## 1. Objetivo del plan

Resolver la causa raíz arquitectónica completa, no solo el síntoma de WhatsApp:

> Establecer un **Delivery Contract** que unifique estado de assets, archivos físicos, manifest, README, gates y evidencia; generar la estructura del README desde los destinos reales del ZIP; y validar automáticamente que README, MANIFEST y ZIP describan exactamente el mismo paquete.

### Alcance mínimo

1. Contrato canónico de estados de assets (enum `DeliveryAssetState`)
2. Rutas POSIX en manifest y ZIP
3. Tamaños reales en manifest (incluyendo metaarchivos)
4. Filename real del ZIP en el README
5. Package Structure derivada de los destinos reales del ZIP
6. Secciones por estado: delivered, present_in_production, present_with_issues, estimated, evidence
7. Tests cross-artifact (README ↔ manifest ↔ ZIP)
8. Gate obligatorio de no-regresión post-zip

### No-objetivos

- NO modificar `SitePresenceChecker` ni su lógica de detección
- NO modificar `CoherenceValidator` ni su modelo de pesos
- NO cambiar la propuesta comercial de Zi One
- NO rehacer el sistema completo de coherencia
- NO modificar `scenario_calculator.py` ni el motor financiero
- NO implementar cambios que requieran re-ejecutar el pipeline de producción completo

## 2. Arquitectura de la solución

```
┌─────────────────────────────────────────────┐
│         DeliveryAssetState (enum)           │  ← FASE-A
│  DELIVERED | PRESENT_IN_PRODUCTION |        │
│  PRESENT_WITH_ISSUES | ESTIMATED |          │
│  FAILED | INDETERMINATE | NOT_DELIVERED     │
├─────────────────────────────────────────────┤
│         DeliveryContext (dataclass)         │  ← FASE-A
│  assets: List[DeliveryAssetEntry]           │
│  zip_filename: str                          │
│  files: List[ZipEntry]                      │
│  totals: ManifestTotals                     │
├─────────────────────────────────────────────┤
│  Pipeline: POSIX paths + real sizes         │  ← FASE-B
│  Manifest: build AFTER all files written    │
│  ZIP: deterministic two-pass                │
├─────────────────────────────────────────────┤
│  README: sections by state                  │  ← FASE-C
│  Package Structure from real dest paths     │
│  No hardcoded asset names                   │
├─────────────────────────────────────────────┤
│  Cross-artifact validation                  │  ← FASE-D
│  README ⊆ ZIP ⊆ Manifest                   │
│  Sizes match, paths POSIX, states coherent  │
├─────────────────────────────────────────────┤
│  E2E: Zi One + RELEASE                      │  ← FASE-E
│  v4complete → verify ZIP/README/manifest    │
└─────────────────────────────────────────────┘
```

## 3. Estructura de fases

| Fase | Descripción | Tareas | Cmd largo | delegate_task | R3 |
|------|------------|--------|-----------|---------------|-----|
| A | Contrato canónico y saneamiento de evidencia | 4 | 0 | DIRECTA (dataclasses + propagación) | ✅ |
| B | Pipeline físico ZIP ↔ manifest (POSIX, tamaños, DeliveryContext) | 5 | 0 | DIRECTA (modificaciones quirúrgicas) | ✅ |
| C | README derivado del delivery context | 4 | 0 | DIRECTA (template + renderizado) | ✅ |
| D | Tests de contrato y gate de no-regresión | 4 | 0 | DIRECTA (TDD) | ✅ |
| E | E2E (Zi One) + RELEASE + Análisis post-implementación | 5 | 1 (v4complete) | MIXTO (subagente para v4complete, directo para RELEASE + análisis) | ✅ |

## 4. Dependencias entre fases

```
FASE-A (contrato)
  └── FASE-B (pipeline físico)
       └── FASE-C (README dinámico)
            └── FASE-D (tests + gate)
                 └── FASE-E (E2E + RELEASE)
```

**Archivos compartidos con riesgo de conflicto:**

| Archivo | Fases que lo modifican | Resolución |
|---------|----------------------|------------|
| `modules/delivery/delivery_packager.py` | B, C | B modifica `create_manifest()`, `_create_zip()`, `package()` (T5: carga DeliveryContext); C modifica `create_readme()` y la llamada en `package()`. Secuencial: B primero, C reemplaza la llamada legacy. |
| `tests/delivery/test_delivery_packager.py` | D | Solo D agrega tests. Sin conflicto. |
| `templates/delivery_readme_template.md` | C | Solo C modifica. Sin conflicto. |

## 5. Matriz de riesgos

| Riesgo | Prob | Impacto | Mitigación |
|--------|------|---------|------------|
| Romper compatibilidad con hoteles sin `present_in_production` | Baja | Alto | FASE-C: template vacía si no hay assets presentes. Test incluido en FASE-D. |
| Cambios en `create_readme()` rompen generación de ZIP | Baja | Alto | FASE-B: ZIP se construye independientemente del README. Orden: manifest → ZIP → README. |
| `asset_generation_report.json` ausente o corrupto | Media | Medio | FASE-A: fallback a estado INDETERMINATE. Warning visible en README. |
| Regresión en tests existentes (10 tests del packager) | Baja | Medio | FASE-D incluye ejecución de suite completa antes de commit. |
| Divergencia entre `can_use` del reporte y metadata individual | Media | Medio | FASE-A: definir fuente canónica única. El reporte global prevalece sobre metadata individual. |
| v4complete timeout en FASE-E | Media | Bajo | FASE-E usa `terminal(timeout=900, notify_on_complete=True)` en background. |

## 6. Criterios de aceptación (DoD global)

Al finalizar FASE-E, debe cumplirse:

1. `README_DELIVERY.md` en el ZIP de Zi One **no menciona** `boton_whatsapp.html` como archivo entregable.
2. `README_DELIVERY.md` muestra WhatsApp en sección "Presente en producción — requiere revisión" (por conflicto de números).
3. `MANIFEST.json` usa exclusivamente rutas POSIX (sin `\\`).
4. `MANIFEST.json` registra tamaños reales para `README_DELIVERY.md` y `MANIFEST.json` (> 0 bytes).
5. `MANIFEST.json.total_size_bytes` coincide con la suma real de tamaños descomprimidos del ZIP.
6. `MANIFEST.json.total_files` coincide con `len(zip.namelist())`.
7. Package Structure del README deriva de los destinos reales del ZIP (no de nombres hardcodeados).
8. El nombre del ZIP en el README coincide con el filename real del archivo.
9. 10 tests existentes del packager siguen pasando.
10. Nuevos tests cross-artifact pasan (mínimo 19 tests).
11. Gate de no-regresión bloquea ZIP si README referencia archivos inexistentes o manifest tiene rutas no-POSIX.
12. `run_all_validations.py --quick` pasa.
13. Sección "Advisory Guides" en README para assets con `is_advisory=True` (ej: whatsapp_conflict_guide).
14. `DeliveryContext.from_asset_generation_report()` construido automáticamente en `package()` cuando `hotel_dir` disponible.
15. CHANGELOG, VERSION.yaml (verificando versión previa) y documentación post-proyecto actualizados.
16. Datos operativos de `output/clientes/zi-one-luxury_onboarding.yaml` verificados pre-v4complete.
17. `08-analisis-post-implementacion.md` completado con datos reales (matriz 14/14 hallazgos, lecciones aprendidas de todas las fases).

## 7. Archivos del plan

```
/.opencode/plans/Archives/DT-1-DELIVERY-CONTRACT-2026-07-23/
├── README.md                         ← Este archivo (índice)
├── dependencias-fases.md             ← Diagrama de dependencias + conflictos
├── 01-plan-maestro.md                ← Este archivo (maestro)
├── 02-prompt-fase-A.md               ← Contrato canónico y saneamiento
├── 03-prompt-fase-B.md               ← Pipeline físico ZIP ↔ manifest
├── 04-prompt-fase-C.md               ← README derivado del delivery context
├── 05-prompt-fase-D.md               ← Tests de contrato y gate de no-regresión
├── 06-prompt-fase-E.md               ← E2E (Zi One) + RELEASE + análisis post-implementación
├── 07-checklist-implementacion.md    ← Master checklist con tracking
├── 08-analisis-post-implementacion.md ← Análisis post-implementación (template, completar en FASE-E)
└── 09-documentacion-post-proyecto.md ← Post-project doc plan
```

## 8. Comando para iniciar la primera fase

Copiar en una **nueva sesión**:

```text
Ejecuta FASE-A del plan DT-1-DELIVERY-CONTRACT-2026-07-23:
/mnt/c/Users/Jhond/Github/iah-cli//.opencode/plans/Archives/DT-1-DELIVERY-CONTRACT-2026-07-23/02-prompt-fase-A.md
```
