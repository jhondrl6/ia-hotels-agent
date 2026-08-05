# FASE-F — E2E: v4complete "Zi One Luxury" (zione.co) + Verificación de Fixes + Análisis Post-Implementación

**ID**: RC1-RC2-ENTREGA-COHERENTE-2026-08-04 / FASE-F
**Objetivo**: Certificar con UNA única ejecución de `v4complete` que todos los fixes de RC1/RC2 fueron superados en producción, y producir el análisis post-implementación con lecciones aprendidas.
**Dependencias**: FASE-A ✅ FASE-B ✅ FASE-C ✅ FASE-D ✅ (verificar en dependencias-fases.md; si alguna no ✅, ABORTAR)
**Duración estimada**: 2-3 horas (v4complete tarda 5-10 min)
**Skill**: `.agents/workflows/phased_project_executor.md` (§Regla v4complete + §Protocolo de Subagente + §Protocolo de Evidencia Proactiva)
**Modo de ejecución**: **`delegate_task` para el comando largo** (timeout=900, notify_on_complete=True); el agente principal usa sus iteraciones en verificación + análisis + docs.

---

## Contexto

Única ejecución E2E del plan para **Zi One Luxury**:
- **URL**: https://zione.co/
- **Onboarding real**: `output/clientes/zi-one-luxury_onboarding.yaml` (existe desde el plan anterior)
- **Output destino**: `output/v4_verify_4.71.0/` (directorio NUEVO para no mezclar con evidencia previa)

Gracias al fix S7 (FASE-D), el loader ya tiene fallback a `output/clientes`, pero por
seguridad (L13) se aplica además el workaround de copia antes del run.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A / B / C / D | ✅ Completadas (verificar; si no, ABORTAR) |
| FASE-E | Puede estar en curso (no bloquea; sus cambios son documentales) |

---

## Tareas

### T1: Preparación + ejecución de v4complete (vía delegate_task)

**Pre-run (agente principal, ~5 iteraciones)**:
```powershell
# Workaround L13 por seguridad (aunque S7 ya dé fallback):
New-Item -ItemType Directory -Force output/v4_verify_4.71.0/clientes | Out-Null
Copy-Item output/clientes/zi-one-luxury_onboarding.yaml output/v4_verify_4.71.0/clientes/
```

**CRÍTICO — Verificar S7 en aislamiento ANTES de lanzar v4complete** (lección L13/L14):
```python
# temp/verify_s7_loader.py — invocar _load_latest_onboarding_data con output_dir alternativo
# y confirmar que encuentra el YAML (no retorna None)
```

**Delegación del comando largo**:
```
delegate_task(
  goal="Ejecutar v4complete para Zi One Luxury (https://zione.co/)",
  context="Comando exacto:
    python main.py v4complete --url https://zione.co/ --output output/v4_verify_4.71.0
    Redirigir salida: > evidence/FASE-F/v4complete_run.log 2>&1
    Expected output: diagnostico, propuesta, assets, coherence >= 0.80.
    NO interpretar el resultado, solo ejecutar y reportar exit code + rutas generadas.",
  timeout=900, notify_on_complete=True, toolsets=["terminal"]
)
```

**Criterios de aceptación del run**:
- [ ] El log contiene **"Onboarding data loaded: N campos confirmados"** y NO contiene
      "Using defaults" (si aparece, el run NO sirve — clasificar causa con L14 antes de decidir).
- [ ] Diagnóstico + propuesta + assets generados en `output/v4_verify_4.71.0/`.
- [ ] Coherence ≥ 0.8.

**INMEDIATAMENTE después** — Protocolo de Evidencia Proactiva (OBLIGATORIO):
```powershell
New-Item -ItemType Directory -Force evidence/FASE-F | Out-Null
Copy-Item output/v4_verify_4.71.0/v4_complete/01_DIAGNOSTICO_*.md evidence/FASE-F/
Copy-Item output/v4_verify_4.71.0/v4_complete/02_PROPUESTA_*.md evidence/FASE-F/
Copy-Item output/v4_verify_4.71.0/v4_complete/*/v4_audit/*.json evidence/FASE-F/
```

### T2: Verificación de TODOS los fixes (scripts Python UTF-8 — L15)

Crear `temp/fase_f_verify.py` que valide contra el run nuevo:

| # | Fix verificado | Check |
|---|----------------|-------|
| V1 | **RC1/N10** | Costos por brecha en propuesta == `opportunity_scores` del `v4_complete_report.json` (8/8) |
| V2 | **RC1/N17** | Fila "SEO Local" referencia la brecha `low_seo_score` (no "Sin Schema Hotel") |
| V3 | **RC1/N18** | Fila WhatsApp: rank vivo (1), label "Conflicto de WhatsApp", costo real; grep "Brecha #5: WhatsApp" = 0 |
| V4 | **RC1/N19** | Sin fila "Schema Organization" salvo que el asset exista en el run |
| V5 | **RC2/N11** | `commercial_gates_report_diagnostic_*.json`: CG-CLAIM-VS-EVIDENCE no falla por el texto condicional |
| V6 | **RC2/N15** | CG-TIER-CONSISTENCY valida inputs reales (mensaje ≠ "Sin datos de tier para comparar") |
| V7 | **RC2/N16+N21** | ZIP de entrega: sin `commercial_gates_report*` BLOCKING junto a doc PASSED; sin artefactos de runs anteriores |
| V8 | **S5** | `financial_scenarios*.json` → `breakdown.data_sources.occupancy == "onboarding"` |
| V9 | **D10 (check de cierre OBLIGATORIO)** | Costos/numeración de brechas IDÉNTICOS en diagnóstico Y propuesta del mismo run (parseo Python UTF-8) |
| V10 | Coherencia global | `gate_report`: 0 blocking failures + readiness READY_FOR_PUBLICATION (el conteo exacto de gates depende de cuántos están activos; NO exigir "12/12" que es frágil ante adición de gates nuevos) |

**Criterios de aceptación**:
- [ ] V1-V10 → PASS (registrar resultados en `evidence/FASE-F/verificacion.md`).
- [ ] Si algún check falla: clasificar (L14/L2); fallo de código → fase ⏳ INCOMPLETA, NO retry del run.

### T3: Análisis post-implementación + lecciones aprendidas

Crear `10-analisis-post-implementacion.md` en el directorio del plan con:

1. **Matriz de fixes superados**: tabla hallazgo (N10-N21, S5, S7) → fix (fase) →
   evidencia en el run nuevo (V1-V10) → estado SUPERADO/PARCIAL/PENDIENTE.
2. **Diff cualitativo** vs run 20260804_124443 (evidencia previa): qué cambió en los
   documentos (costos de la tabla de servicios, estado del commercial gate, contenido del ZIP).
3. **Lecciones aprendidas NUEVAS** (numeradas desde L16): todo lo que falló, sorprendió o
   se descubrió durante A-F (incluye si algún delegate_task falló y por qué).
4. **Seguimientos abiertos restantes** (ej: S6 execution_trace duplicado, upgrade del
   gate N2 a BLOCKING) con severidad y candidato a próximo release.
5. Preservar evidencia completa del run (docs + JSON + ZIP) en `evidence/FASE-F/`.

---

## Tests Obligatorios

| Check | Comando | Criterio |
|-------|---------|----------|
| Script de verificación | `python temp/fase_f_verify.py > evidence/FASE-F/verificacion.txt 2>&1` | V1-V10 PASS |
| Validaciones | `python scripts/run_all_validations.py --quick` | TOTAL PASS (conteo dinámico; incluye "Prompts No Release" desde FASE-E) |

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. Actualizar `dependencias-fases.md` (FASE-F ✅) y `README.md` del plan.
2. `09-documentacion-post-proyecto.md`: Sección D (coherencia final del run, estado gates).
3. Registrar la fase:
```bash
python scripts/log_phase_completion.py --fase FASE-F --desc "E2E v4complete Zi One Luxury: RC1/RC2 verificados (V1-V10) + analisis post-implementacion" --tests "0" --check-manual-docs
```
**SIN `--release`** (L3/L9).

---

## Criterios de Completitud (CHECKLIST)

- [ ] Run único ejecutado con onboarding real cargado ("Onboarding data loaded" en log)
- [ ] Evidencia proactiva copiada ANTES de cualquier verificación
- [ ] V1-V10 PASS documentados
- [ ] `10-analisis-post-implementacion.md` con matriz de fixes + lecciones nuevas
- [ ] `run_all_validations.py --quick` TOTAL PASS (incluye "Prompts No Release")
- [ ] `log_phase_completion.py` ejecutado SIN --release

## Restricciones

- Máximo 60 iteraciones (R2). El v4complete va por subagente para reservar presupuesto.
- **UNA SOLA ejecución de v4complete en todo el plan** — si falla por código, la fase
  queda ⏳ INCOMPLETA (L14: fallo de código no habilita retry).
- NUNCA ejecutar v4complete sin notify_on_complete/subagente (executor §Advertencia).
- NO modificar código fuente en esta fase: si un fix no pasó, documentar y escalar,
  no parchar sobre la marcha.
- Verificación de texto con acentos SOLO con Python UTF-8 (L15).
