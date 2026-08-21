# FASE-P0-A: Fuente Única de Pricing + Precio Dinámico en Hook PDF (F1)

**ID**: CREDIBILIDAD-NUMERICA-2026-08-20 / FASE-P0-A
**Objetivo**: Eliminar las constantes de pricing hardcodeadas del generador del Hook PDF y hacer que TODO el pipeline consuma `config/pricing.yaml` como fuente única.
**Dependencias**: Ninguna (primera fase)
**Duración estimada**: 1 sesión (≤60 iteraciones)
**Skill**: `phased_project_executor.md` (Regla código+tests → ejecución DIRECTA)

## Modo de Ejecución

**DIRECTO con el agente principal.** Incluye decisión arquitectónica (qué fuente es master y cómo se expone a los consumidores) → el executor prohíbe delegar decisiones cross-module a subagentes.

## Contexto

CONTEXT (`CONTEXT-VALIDACION-COMERCIAL-CODIGO-VIVO-2026-08-19.md`) §2, fallo **F1**:
el cliente vería $400K en el Hook PDF y $500K en la propuesta del mismo output, porque
`hook_pdf_generator.py` define constantes Python (`PRECIO_EXPRESS`, `PRECIO_MENSUAL`, `SETUP_FEE`,
zona L118-121 — verificar leyendo el archivo completo) mientras el motor financiero calcula un
pricing dinámico ($500K en la corrida real). P0 es prerrequisito absoluto del primer cliente.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| (ninguna) | Primera fase del plan |

### Base Técnica Disponible
- `config/pricing.yaml` (tiers, gates min/max ratio, packages: monthly_default 1.2M, setup_fee_default 2.5M)
- `modules/commercial_documents/hook_pdf_generator.py` (641 líneas, tests en `tests/commercial_documents/test_hook_pdf_generator.py`)
- `modules/commercial_documents/v4_proposal_generator.py` — **segunda fuente de constantes detectada en revisión**: `MONTHLY_PACKAGE_PRICE = 1200000` / `SETUP_FEE = 2500000` (L136-138), usados como fallback en L548/L840/L922/L1005-1008/L1760. Valores hoy coinciden con pricing.yaml `packages` pero duplican la fuente (mismo anti-patrón F1)
- Tests base: 3,233 funciones (v4.71.0) — **línea base con 22 fallos preexistentes** (ver 01-plan-maestro §6)

## Tareas

### T0: Capturar línea base de tests (ANTES de cualquier cambio)
```powershell
.\venv\Scripts\python.exe -m pytest tests/commercial_documents tests/financial_engine tests/quality_gates tests/data_validation tests/orchestration_v4 -q --tb=no *> evidence/BASELINE-TESTS-v4.71.0.txt
```
- [ ] Archivo `evidence/BASELINE-TESTS-v4.71.0.txt` creado (22 fallos esperados: 12 commercial_documents [5 disclosure + 7 dynamic] + 10 financial_engine [2 calculator_v2 + 8 pricing_resolution] — ver 01-plan-maestro §6)
- [ ] Regla de la fase: "sin regresiones" = sin fallos NUEVOS vs ese archivo (lección L1/L11 RC1-RC2: tests preexistentes NO se arreglan aquí)

### T1: Investigar la cadena completa del pricing (ANTES de modificar nada)
**Objetivo**: trazar TODOS los consumidores y productores de precios: constantes del hook PDF,
ruta que produce `pricing.monthly_price_cop` en `financial_scenarios.json` (incógnita §4.2 del
CONTEXT: la cadena exacta del $500K no fue trazada a fondo), y cualquier otra fuente (docs, templates).
**Regla**: leer archivos completos; nunca declarar bug desde grep recortado (lección §1.3).
**Criterios de aceptación**:
- [ ] Inventario escrito de productores/consumidores de pricing (guardar en notas de la fase)
- [ ] Ruta productora del precio dinámico identificada con archivo+función

### T2: Refactor — pricing.yaml como master, hook PDF dinámico
**Objetivo**: las constantes del hook PDF desaparecen (o quedan como fallback explícito con
warning) y el precio mostrado se resuelve desde `config/pricing.yaml` con la misma lógica que
el motor financiero (o directamente del valor ya calculado en el output de v4complete cuando exista).
**Archivos afectados**:
- `modules/commercial_documents/hook_pdf_generator.py` (PRECIO_EXPRESS/PRECIO_MENSUAL/SETUP_FEE, L116-121 y uso en L359-362)
- `modules/commercial_documents/v4_proposal_generator.py` (MONTHLY_PACKAGE_PRICE/SETUP_FEE, L136-138 + 5 usos fallback — dejar de leer las constantes, leer pricing.yaml via `_load_pricing_config()['packages']` o equivalente)
- `config/pricing.yaml` (extensión mínima si falta un campo, ej. precio Express $120K)
**Criterios de aceptación**:
- [ ] Hook PDF muestra el mismo precio que `financial_scenarios.json` para el mismo hotel
- [ ] Sin constantes de precio hardcodeadas usadas en render — verificación grep en AMBOS módulos:
  `grep -n "PRECIO_EXPRESS\|PRECIO_MENSUAL\|SETUP_FEE\|MONTHLY_PACKAGE_PRICE" modules/commercial_documents/hook_pdf_generator.py modules/commercial_documents/v4_proposal_generator.py`
  → 0 usos en ruta de render (lección L28: fix cubre TODOS los sitios de construcción)
- [ ] Tests existentes del hook PDF siguen pasando (sin nuevos fallos vs línea base T0)

### T3: Tests de contrato anti-regresión
**Criterios de aceptación**:
- [ ] Test nuevo: precio del hook == precio de pricing.yaml/escenarios (contrato F1)
- [ ] Test nuevo: ausencia de constantes hardcodeadas en ruta de render
- [ ] Suite afectada pasa sin fallos NUEVOS vs línea base (T0)

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Pricing dinámico hook | `tests/commercial_documents/test_hook_pdf_generator.py` (extender) o nuevo | Contrato F1 pasa |
| Regresión módulo | `pytest tests/commercial_documents/ -v` | Sin fallos NUEVOS vs `evidence/BASELINE-TESTS-v4.71.0.txt` (línea base: 12 fallos preexistentes en esa suite — 5 test_proposal_confidence_disclosure + 7 test_proposal_dynamic) |

**Comando de validación**:
```powershell
.\venv\Scripts\python.exe -m pytest tests/commercial_documents/ -v
.\venv\Scripts\python.exe scripts/run_all_validations.py --quick
```

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. `dependencias-fases.md` y `06-checklist-implementacion.md`: marcar FASE-P0-A ✅.
2. `README.md` del plan: actualizar tabla de progreso.
3. `09-documentacion-post-proyecto.md`: secciones A/B/D/E con datos de esta fase.
4. `10-analisis-post-implementacion.md`: fila de ejecución + mínimo 3 lecciones aprendidas + **decisión D6 documentada** (pricing.yaml fuente única: constantes eliminadas, consumidores migrados).
5. **Registrar la fase** (NO se delega a RELEASE):
```powershell
.\venv\Scripts\python.exe scripts/log_phase_completion.py --fase FASE-P0-A --desc "Fuente unica de pricing + hook PDF dinamico (F1)" --archivos-mod "modules/commercial_documents/hook_pdf_generator.py,modules/commercial_documents/v4_proposal_generator.py,config/pricing.yaml" --tests "<N>" --check-manual-docs
```
6. Editar CHANGELOG.md y GUIA_TECNICA.md con los cambios de esta fase (template §6).

## Criterios de Completitud (CHECKLIST)

- [ ] Línea base capturada en `evidence/BASELINE-TESTS-v4.71.0.txt` (T0)
- [ ] Tests nuevos pasan y suite comercial sin fallos NUEVOS vs línea base
- [ ] `run_all_validations.py --quick` pasa (TOTAL PASS)
- [ ] Checklist del plan actualizado
- [ ] Post-ejecución completada (incluye log_phase_completion.py)

## Restricciones

- Máximo 60 iteraciones.
- NO crear el gate `pricing_compliance` (es FASE-P0-B).
- NO tocar encoding de archivos (es FASE-P0-C) salvo el `open()` estrictamente necesario del refactor.
- NO modificar ROADMAP.md ni ejecutar v4complete.
