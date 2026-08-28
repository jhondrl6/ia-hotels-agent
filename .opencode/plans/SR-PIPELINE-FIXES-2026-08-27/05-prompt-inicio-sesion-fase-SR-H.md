# FASE-SR-H — E2E Única: v4complete Hotel Salento Real (DELEGABLE)

**ID**: FASE-SR-H
**Objetivo**: Ejecutar LA ÚNICA corrida E2E del plan (§9 del plan maestro): `v4complete` para Hotel Salento Real con URL canónica limpia (L-SR2), contra el baseline pre-registrado de la corrida C. Aplicar el Protocolo de Evidencia Proactiva INMEDIATAMENTE tras la corrida (la evidencia se copia antes de cerrar la sesión, nunca "después"). Smoke de 7 checks sobre el output.
**Dependencias**: FASE-SR-A…SR-G ✅ (todas las fases de implementación completadas).
**Complejidad**: Media · **Delegación**: ✅ DELEGABLE (Protocolo de Subagente del executor §Paso-6 — la corrida se ejecuta via `delegate_task`; el smoke y la evidencia son del orquestador, síncronos)
**Duración estimada**: 30-45 min (corrida ~10-15 min) · **Presupuesto**: 3 tareas + 1 comando largo (R3 — la corrida v4complete ES el comando largo)

## Reglas de Sesión (MANDATORIO)

- R1: Una fase por sesión. R2: máx. 60 iteraciones. R3: **3 tareas + 1 comando largo**.
- **DELEGACIÓN OBLIGATORIA de la corrida**: `delegate_task(timeout=900, notify_on_complete=True, toolsets=["terminal"])`. El prompt del subagente debe ser COMPLETO e incondicional (no tiene el contexto de esta conversación): comando exacto, cwd del repo, y qué capturar si falla.
- Python: `./venv/Scripts/python.exe`.

## Contexto

**Lectura previa obligatoria**: plan maestro §9 (corrida única) + CONTEXT-SALENTOREAL §9.5 (L-SR2).

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-SR-A…SR-G | ✅ Completadas |

### Baseline (corrida C, 2026-08-27 — pre-registrado en `10-analisis` §Métricas)
12/13 gates PASSED · coherencia 0.8644 · alignment 43% (3/7) · unresolved divergente (4 vs 1) · `hotel_schema` NO generado → `promised_assets_exist` FAILED · veredicto NOT_READY · financiera $6.57M / $4.04M / $1.26M COP/mes (idéntica entre corridas).

### L-SR2 (URL canónica)
Usar EXACTAMENTE `https://www.hotelsalentoreal.com/` — sin UTM, sin fragmento, con trailing slash. La URL con parámetros fragmenta la identidad en memoria (H2/N3) y la comparación contra baseline.

## Tareas

### T1: Preparar baseline y evidencia (ANTES de la corrida)
**Criterios**:
- [ ] Copiar el output de la corrida C (`output/test_salentoreal_v4c/`) → `evidence/FASE-SR-H/baseline/` (comparación antes/después, L-NC12)
- [ ] Verificar URL exacta del comando: `https://www.hotelsalentoreal.com/` (sin parámetros)
- [ ] Confirmar que SR-A…SR-G están ✅ en `README.md` del plan (la corrida es válida solo con el pipeline completo parcheado)

### T2: Corrida única v4complete (comando largo — DELEGAR)
**Criterios**:
- [ ] Ejecutar (delegado, en el directorio del repo):
```bash
./venv/Scripts/python.exe main.py v4complete --url "https://www.hotelsalentoreal.com/" --output output/salentoreal_final_v4c
```
- [ ] **1 corrida = 1 diagnóstico del pipeline completo. Si falla: NO reintentar en bucle.** Capturar el error completo → `evidence/FASE-SR-H/failure.log` y escalar a decisión (post-mortem documentado en `10-analisis`); un fallo aquí es información valiosa (L-SR5: los gates deben ciclar o escalar, nunca silenciarse).
- [ ] Timeout 900s vía delegate_task; si el subagente reporta timeout, tratarlo como fallo documentado (no como "reintentar más").

### T3: Protocolo de Evidencia Proactiva + Smoke 7 checks (DESPUÉS, síncrono del orquestador)
**Criterios**:
- [ ] Copiar INMEDIATAMENTE `output/salentoreal_final_v4c/` → `evidence/FASE-SR-H/final/` (antes de cualquier análisis extenso — la evidencia primero)
- [ ] Smoke de 7 checks, comparando contra baseline:
  1. Veredicto final READY_FOR_PUBLICATION (sin BLOCKED_BY_GATES)
  2. Coherence score ≥ 0.8
  3. `promised_assets_exist` PASS (hotel_schema generado — AC6/AC7)
  4. Unresolved idéntico gate vs delivery (AC3)
  5. `01_DIAGNOSTICO_Y_OPORTUNIDAD.md` + `02_PROPUESTA_COMERCIAL.md` presentes (AC12)
  6. ZIP de entrega generado
  7. Escenarios financieros idénticos al baseline ($6.57M/$4.04M/$1.26M — AC10)
- [ ] Resultado del smoke (7/7 o detalle de fallas) registrado en `10-analisis` §Resumen E2E (la certificación formal AC por AC es de FASE-VERIFY)

## Tests Obligatorios

| Test | Artefacto | Criterio de Éxito |
|------|-----------|-------------------|
| Smoke 7 checks | `evidence/FASE-SR-H/final/` | 7/7 contra baseline (o fallas documentadas con causa) |

## Post-Ejecución (OBLIGATORIO — antes de cerrar la sesión)

1. `dependencias-fases.md` §2 → ✅. 2. `README.md` → ✅. 3. `06-checklist` → SR-H. 4. `09-documentacion` → B/E + Notas. 5. `10-analisis` → §Resumen E2E (Observed real vs baseline). 6. `evidence/FASE-SR-H/` → `baseline/` + `final/` (+ `failure.log` si aplica). 7. Registro (SIN `--release`):
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-SR-H --desc "E2E unica v4complete Salento Real ejecutada; evidencia proactive capturada (baseline + final); smoke 7 checks" --archivos-mod "(ninguno - fase de ejecucion)" --tests "7 smoke checks" --check-manual-docs
```
8. NO regenerar DOMAIN_PRIMER aquí (es del RELEASE).

## Criterios de Completitud (CHECKLIST)

- [ ] Corrida ejecutada exactamente 1 vez; output completo (o fallo documentado con failure.log)
- [ ] Evidencia copiada (baseline + final) ANTES de cerrar la sesión
- [ ] Smoke 7/7 o fallas documentadas con causa y fase responsable
- [ ] Docs post-fase completos (1-7)

## Restricciones

- **UNA sola corrida de v4complete en TODO el plan** (§9 del plan maestro). Prohibido: v4audit, scrapers sueltos, re-corridas, corridas "de prueba".
- URL EXACTA: `https://www.hotelsalentoreal.com/` (canónica, limpia — L-SR2).
- NO modificar código en esta fase (es de ejecución y evidencia).
- La corrida SE DELEGA (Protocolo de Subagente); el smoke y la evidencia los ejecuta el orquestador (no delegables — son la garantía de trazabilidad).
- NO usar `--release` en log_phase_completion.
- AC10: si la financiera NO coincide con el baseline, es una regresión bloqueante → documentar y detener antes de VERIFY.
