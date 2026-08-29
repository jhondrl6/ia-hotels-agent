# Plan Maestro: DELIVERY-ZIP-SINGLE-WRITE

**ID**: DELIVERY-ZIP-SINGLE-WRITE-2026-08-01
**Version objetivo**: v4.69.0
**Contexto**: `/.opencode/context/Historico/CONTEXT-DELIVERY-ZIP-PACKAGING-BROKEN-2026-08-01.md`
**Hotel de verificacion**: Zi One Luxury (https://zione.co/)
**Onboarding**: `output/clientes/zi-one-luxury_onboarding.yaml`
**Fecha**: 2026-08-01
**Skill**: `phased_project_executor.md` v2.13.0

---

## 1. Resumen Ejecutivo

El pipeline `v4complete` genera contenido correcto (gates PASSED, coherence 0.92) pero **NUNCA materializa el ZIP de entrega** al cliente. La causa raiz es un defecto de ordering arquitectonico: el sistema modifica archivos DESPUES de que sus tamanos fueron registrados como compromisos contractuales en el MANIFEST (diseno "measure-then-mutate-then-validate" en 3-pass).

**Solucion elegida**: Opcion C — Rewrite arquitectonico single-write con iteracion fija. Calcula todo en memoria, escribe UNA sola vez al final, elimina la inestabilidad de multi-pass.

---

## 2. Bugs y Fallos a Resolver

| ID | Severidad | Estado | Descripcion |
|----|-----------|--------|-------------|
| Bug 1 | PRIMARIO | ACTIVO | README cambia de tamano DESPUES de que MANIFEST lo mide (-18 bytes) |
| Bug 2 | SECUNDARIO | LATENTE | Self-reference del MANIFEST es inherentemente inestable |
| Bug 3 | AMPLIFICADOR | ACTIVO | Tests usan tolerancia 5%, produccion exige exactitud por archivo |
| NF-1 | CRITICO | ACTIVO | Cobertura de tests CERO para path FASE-C (produccion real) |
| NF-2 | ALTO | ACTIVO | Fallback silencioso `except Exception: pass` |
| NF-3 | ALTO | ACTIVO | Catch silencioso en main.py: fallo de entrega es WARN, no ERROR |
| NF-4 | MEDIO | ACTIVO | Sin cleanup de artefactos en camino de error |
| NF-5 | BAJO | ACTIVO | Doble llamada a `datetime.now()` — divergencia potencial |
| NF-6 | BAJO | ACTIVO | FASE-5 (IMPLEMENTATION_ORDER) feature muerto en integracion |

---

## 3. Fases del Plan

| Fase | Nombre | Tipo | Delegable | Complejidad |
|------|--------|------|-----------|-------------|
| **FASE-A** | Test Infrastructure + Bug 3 Fix | Implementacion | SI (delegate_task) | Media |
| **FASE-B** | Core Rewrite: Single-Write Architecture | Implementacion | NO (decision arquitectonica) | **ALTA** ★ |
| **FASE-C** | Error Handling + Cleanup + NF-5/NF-6 | Implementacion | SI (delegate_task) | Media |
| **FASE-D** | E2E Verification: v4complete Zi One Luxury | Verificacion | NO (comando largo + verificacion) | Media |
| **FASE-RELEASE-4.69.0** | Release + Documentacion Oficial | Release | SI (delegate_task) | Baja |

**★ Fase de mayor complejidad tecnica**: **FASE-B** — Requiere reescribir la logica central de `delivery_packager.py` (833 lineas) con un nuevo paradigma de single-write + fixed-point iteration para la self-reference del MANIFEST. Decision arquitectonica cross-module que afecta `_create_zip()`, `_validate_zip()`, `create_manifest()`, `create_readme()`, y el flujo P-01. NO delegable segun §Regla de Decision del executor.

---

## 4. Dependencias

```
FASE-A (tests first, TDD)
    │
    ▼
FASE-B (core rewrite, requiere tests de FASE-A como red de seguridad)
    │
    ▼
FASE-C (error handling sobre la nueva arquitectura)
    │
    ▼
FASE-D (v4complete E2E, requiere A+B+C completas)
    │
    ▼
FASE-RELEASE-4.69.0 (requiere A+B+C+D completas)
```

---

## 5. Estrategia de Delegacion (delegate_task)

| Fase | Modo | Razon |
|------|------|-------|
| FASE-A | `delegate_task` viable | Puro codigo/tests, sin decision arquitectonica. 2 tracks paralelas: (1) fix tests existentes, (2) crear fixture FASE-C |
| FASE-B | **Agente principal DIRECTO** | Decision arquitectonica cross-module. Afecta multiples consumidores. Requiere contexto completo. |
| FASE-C | `delegate_task` viable | Fixes puntuales bien acotados (NF-2 a NF-6), sin decisiones de diseno |
| FASE-D | Agente principal + `delegate_task` para v4complete | v4complete via subagente (timeout=900), verificacion directa |
| FASE-RELEASE | `delegate_task` viable | Solo edita YAML/MD + scripts, sin imports del proyecto |

---

## 6. Criterios de Aceptacion Globales (del Contexto §10)

1. ZIP se materializa: `v4complete` para Zione produce `deliveries/zione_YYYYMMDD.zip`
2. Validacion exacta pasa: `_validate_zip()` retorna `[]` sin tolerancia
3. MANIFEST limpio: No persisten MANIFESTs huerfanos
4. README coherente: dentro del ZIP referencia el ZIP correcto con tamanos reales
5. quality_metadata presente: `evidence_tier = "B+"`
6. Tests actualizados: sin 5% tolerancia que enmascara
7. No regresion: 3,158+ tests existentes siguen pasando
8. Control de caso: hotel sin onboarding tambien produce ZIP valido
9. Test FASE-C (NF-1): fixture con `asset_generation_report.json`
10. Test legacy: sin `asset_generation_report.json` (no regresion)
11. Logging de fallback (NF-2): `logger.warning()` con flag visible
12. Cleanup en error (NF-4): camino de error limpia MANIFEST y README
13. Verificacion end-to-end: `v4complete` real con Zione produce ZIP valido

---

## 7. Archivos Clave

| Archivo | Rol en el fix |
|---------|---------------|
| `modules/delivery/delivery_packager.py` (833L) | Core a reescribir (FASE-B) |
| `modules/delivery/delivery_context.py` (535L) | DeliveryContext (no modificar, consumer) |
| `main.py` L3020-3077 | FASE 7 caller (NF-3, NF-6) |
| `templates/delivery_readme_template.md` | Template con placeholders |
| `tests/delivery/test_delivery_packager.py` | Tests unitarios (NF-1) |
| `tests/delivery/test_delivery_contract.py` | Tests de contrato (Bug 3) |

---

## 8. Estructura del Plan

```
/.opencode/plans/Archives/DELIVERY-ZIP-SINGLE-WRITE-2026-08-01/
├── 01-plan-maestro.md                    (este archivo)
├── 02-prompt-fase-A.md                   (Test Infrastructure)
├── 03-prompt-fase-B.md                   (Core Rewrite)
├── 04-prompt-fase-C.md                   (Error Handling)
├── 05-prompt-fase-D.md                   (E2E v4complete)
├── 06-prompt-fase-RELEASE.md             (Release)
├── 07-checklist-implementacion.md        (Checklist maestro)
├── 08-analisis-post-implementacion.md    (Analisis post-implementacion por fase)
├── 09-documentacion-post-proyecto.md     (Docs acumulativas)
├── dependencias-fases.md                 (Dependencias + conflictos)
└── README.md                             (Indice del plan)
```

---

## 9. Lecciones Aplicadas (del Contexto §13)

| Leccion | Aplicacion |
|---------|-----------|
| "grep exhaustivo de consumers" | FASE-A: antes de modificar, grep todos los consumers de `_validate_zip`, `create_readme`, `create_manifest` |
| "T0/T0b como pre-requisito" | FASE-A: limpiar tests PRIMERO (eliminar tolerancia, agregar fixture FASE-C) |
| "NP8: control de caso default" | FASE-A: test con hotel SIN `asset_generation_report.json` (legacy) Y con el (FASE-C) |
| "NP5: fallback silencioso" | FASE-C: `except Exception: pass` → `logger.warning()` + flag |
| "Verificar integracion completa" | FASE-D: `v4complete` real con Zione, no solo tests unitarios |
| "NP1/NP2: consumers downstream" | FASE-B: verificar que no rompe `hook_pdf_generator.py`, `delivery_quality_report.py` |
