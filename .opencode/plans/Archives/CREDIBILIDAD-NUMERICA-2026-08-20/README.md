# PLAN: CREDIBILIDAD-NUMERICA-2026-08-20

> **ID**: CREDIBILIDAD-NUMERICA-2026-08-20
> **Fuente de hallazgos**: `/.opencode/context/Historico/CONTEXT-VALIDACION-COMERCIAL-CODIGO-VIVO-2026-08-19.md` (fallos F1-F14)
> **Workflow**: `.agents/workflows/phased_project_executor.md` v2.15.0 (R1: una fase por sesión, R2: max 60 iteraciones, R3: max 4 tareas + 1 comando largo por fase)
> **Versión objetivo**: v4.72.0 — "Credibilidad Numérica y Verdad del Sitio Vivo"
> **Cierre del plan**: ÚNICA ejecución de `v4complete` para **Zi One Luxury** (https://zione.co/) con onboarding real (`output/clientes/zi-one-luxury_onboarding.yaml`) + análisis post-implementación de fixes superados + lecciones aprendidas.

---

## Objetivo del Plan

Implementar las soluciones P0/P1/P2 identificadas en la validación comercial contra código vivo:
unificar la credibilidad numérica del pipeline (pricing, benchmarks, comisión OTA, rango del hook),
propagar la verdad del sitio vivo (WhatsApp multi-sede, verificación de assets en producción),
corregir encoding de artefactos y cerrar el bucle Hook→Express. Todo como **prerrequisito del
primer cliente** (condición dura 1 del contexto: "el primer cliente no puede ver cifras
contradictorias ni brechas falsas").

## Patrón de causa raíz dominante (hilo conductor)

Violación del principio **"una fuente de verdad por concepto"**: pricing (F1), benchmarks (F2/F4),
comisión OTA (F5), occupancy (F8), docs (F10) y estado del sitio vivo (F12/F13/F14) tienen
múltiples fuentes no sincronizadas. Cada fase restaura una fuente única para un concepto.

## Tabla Maestra de Fases

| # | Fase | Fallos cubiertos | Modo de ejecución | delegate_task | Sesión |
|---|------|------------------|-------------------|---------------|--------|
| 1 | `FASE-P0-A` Fuente única de pricing | F1 (constantes) | DIRECTO (decisión arquitectónica) | No | ✅ 2026-08-20 |
| 2 | `FASE-P0-B` Gate pricing_compliance | F1 (gate) | DIRECTO | No | ✅ 2026-08-21 |
| 3 | `FASE-P0-C` Encoding utf-8 global | F7 | **DELEGABLE** (fix mecánico) | Sí (opcional) | ✅ 2026-08-21 |
| 4 | `FASE-P1-A` Benchmark maestro único | F2, F4 | DIRECTO (decisión arquitectónica) | No | ✅ 2026-08-21 |
| 5 | `FASE-P1-B` Fallback región + comisión OTA | F3, F5 | **DELEGABLE** (2 tracks independientes) | Sí | ✅ 2026-08-21 |
| 6 | `FASE-P1-C` Cap plausibilidad + trazabilidad rango | F6, F11 | DIRECTO (decisión arquitectónica) | No | ✅ 2026-08-21 |
| 7 | `FASE-P1-D` Verdad del sitio vivo | F12, F13 | DIRECTO — **FASE DE MAYOR COMPLEJIDAD TÉCNICA** | No | ✅ 2026-08-21 |
| 8 | `FASE-P2-A` Coherence vs gate + occupancy label | F14, F8 residual | DIRECTO | No | ✅ 2026-08-21 |
| 9 | `FASE-P2-B` Pre-carga prospectos + higiene docs | F9, F10 | DIRECTO | No | ✅ 2026-08-21 |
| 10 | `FASE-E2E-ZIONE` v4complete Zi One Luxury | Verificación E2E de todos los fixes | **delegate_task para v4complete** (timeout=900) | Sí (obligatorio) | ✅ 2026-08-21 |
| 11 | `FASE-RELEASE-4.72.0` Cierre oficial | — | **DELEGABLE** (solo docs/scripts) | Sí (opcional) | ✅ 2026-08-21 |

**Total: 11 sesiones** (9 de implementación + 1 E2E + 1 RELEASE).

## Fase de Mayor Complejidad Técnica: `FASE-P1-D`

**Razón**: es la única fase con decisión arquitectónica cross-module sobre un concepto nuevo
("estado de verdad del sitio vivo") con 3+ consumidores que hoy discrepan:

1. `F12`: `cross_validator.py` compara GBP contra el primer `wa.me`/tel del DOM sin mapear
   número→sede (falso positivo de conflicto, BRECHA 1 inexistente que infla la fuga $1.198.906/mes).
2. `F13`: `site_verification` ya existe y la consumen el asset layer (skip) y el gate
   ("verified in production"), pero NO el pain_ledger ni el diagnóstico (brecha DETECTED HIGH falsa).
3. El scanner no reconoce widgets Elementor no estándar (`e-fab-whatsapp`).

No es delegable a subagente (regla del executor: decisión arquitectónica cross-module → agente
principal con contexto completo). Si en ejecución se detecta que excede el presupuesto, dividir
en `FASE-P1-D-A` (F12) y `FASE-P1-D-B` (F13) según §Recuperación del executor.

## Política de delegate_task (ajustada por solicitud del propietario)

| Fase | Uso de delegate_task | Justificación según reglas del executor |
|------|---------------------|------------------------------------------|
| P0-C | Opcional: subagente ejecuta el fix mecánico `encoding='utf-8'` en writers; parent verifica diff + tests | Fix que replica un patrón existente, sin decisión de diseño (análogo a la rama v2.14.0 de scripts stdlib) |
| P1-B | Sí: 2 subagentes en paralelo (track F3 → `modules/auditors/`; track F5 → 5 sitios en `modules/financial_engine/` + `modules/orchestration_v4/two_phase_flow.py` + `modules/utils/benchmarks.py`, decisión D2 pre-resuelta); parent integra y testa | Trabajo paralelo (2+ tracks) sin decisión de diseño abierta (D2 ya resuelta en el maestro §7). **Advertencia venv**: si los subagentes no comparten el venv Windows del proyecto, ejecutar DIRECTO |
| E2E | Obligatorio: `delegate_task(goal=..., timeout=900, notify_on_complete=True)` ejecuta `v4complete`; parent guarda evidencia y verifica matriz de fixes | Comando de larga duración (5-10 min); el parent reserva iteraciones para verificación + lecciones aprendidas |
| RELEASE | Opcional: delegable según TIP del executor (solo edita YAML/MD + scripts stdlib, sin imports del proyecto) | Confirmado históricamente: ~18 tool calls / ~4 min |
| Resto | DIRECTO | Puro código con decisión arquitectónica → regla del executor prohíbe delegar |

## Reglas Obligatorias (recordatorio por sesión)

- **R1**: una fase por sesión, sin excepciones.
- **R2**: máximo 60 iteraciones (tool calls) por fase.
- **R3**: cada fase ≤ 4 tareas de investigación/fix, ≤ 1 comando de larga duración.
- Cada fase de implementación ejecuta `log_phase_completion.py` AL TERMINAR (anti-deuda §2.5 — NO se delega a RELEASE).
- Protocolo de Evidencia Proactiva obligatorio en FASE-E2E-ZIONE (copiar output a `evidence/E2E-ZIONE/` ANTES de cualquier verificación).

## Revisión de Exactitud (2026-08-20, contra código vivo)

Verificación integral del plan contra código en ejecución (pytest, greps de consumidores,
lectura de módulos). Correcciones aplicadas a 01-plan-maestro.md y a los prompts:

1. **Línea base de tests (§6 del maestro)**: las suites tocadas por el plan tienen **22 fallos
   preexistentes** (12 commercial_documents + 10 financial_engine; 1274 passed) — verificado por
   ejecución. "Sin regresiones" = "sin fallos NUEVOS vs línea base". P0-A captura la evidencia en
   `evidence/BASELINE-TESTS-v4.71.0.txt`; P1-B captura aparte la baseline de auditors.
2. **Decisiones de diseño pre-resueltas (§7, D1-D6; D7/D8 se deciden en fase)**: gate
   pricing_compliance floor-aware (D1 — si no, V12 es matemáticamente inalcanzable para Zione),
   comisión OTA usa campo existente `comision_ota` (D2), benchmark master con 3 fuentes y 9+
   consumidores (D3), cableado del hook ANTES del cap (D4), AGENTS.md gate count 12→13 en P0-B
   (D5), pricing.yaml fuente única (D6). Numeración unificada con el 10-analisis.
3. **Alcance F5 ampliado**: 0.15 hardcodeado en 5 sitios y 3 módulos (no 1 archivo); incluye
   `two_phase_flow.py` L245/L318 y `utils/benchmarks.py` L28.
4. **F6 causa raíz**: `_get_regional_benchmarks` (two_phase_flow.py L215-230) devuelve defaults
   porque `OnboardingController` (L58-61) nunca pasa `plan_maestro_data`; P1-C cablea ANTES de
   capear (T1 nueva).
5. **Callers de `validate_whatsapp`** (F12): 3 callers productivos listados en P1-D
   (main.py L1735, v4_comprehensive.py L1557, two_phase_flow.py L371).
6. **E2E**: protocolo de evidencia reescrito en PowerShell (la sintaxis bash no funciona en
   pwsh — lección L6); V13 = "tiempo con caches cálidos" (caches globales); V12 con regla de
   línea base; V2 exige PASSED floor-aware.
7. **RELEASE**: E8 ejecuta `validate_agents_md.py` explícito (`--quick` no lo incluye); E8b
   audita también el conteo de tests de AGENTS.md.
8. **P0-C**: `--archivos-mod` sin wildcards (rutas reales del inventario T1).

## Archivos del Plan

```
/.opencode/plans/Archives/CREDIBILIDAD-NUMERICA-2026-08-20/
├── README.md                                    (este archivo)
├── 01-plan-maestro.md                           (mapeo F1-F14 → fases, alcance)
├── dependencias-fases.md                        (diagrama + conflictos de archivos)
├── 06-checklist-implementacion.md               (estados por fase)
├── 09-documentacion-post-proyecto.md            (acumulativo → FASE-RELEASE)
├── 10-analisis-post-implementacion.md           (creado DESDE LA CONCEPCIÓN)
├── 05-prompt-inicio-sesion-fase-P0-A.md
├── 05-prompt-inicio-sesion-fase-P0-B.md
├── 05-prompt-inicio-sesion-fase-P0-C.md
├── 05-prompt-inicio-sesion-fase-P1-A.md
├── 05-prompt-inicio-sesion-fase-P1-B.md
├── 05-prompt-inicio-sesion-fase-P1-C.md
├── 05-prompt-inicio-sesion-fase-P1-D.md
├── 05-prompt-inicio-sesion-fase-P2-A.md
├── 05-prompt-inicio-sesion-fase-P2-B.md
├── 05-prompt-inicio-sesion-fase-E2E-ZIONE.md
└── 05-prompt-inicio-sesion-fase-RELEASE.md
```
