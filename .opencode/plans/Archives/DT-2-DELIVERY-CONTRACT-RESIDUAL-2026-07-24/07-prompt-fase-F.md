# FASE-F — v4complete Zi One Luxury + Análisis Post-Implementación

> **Plan**: DT-2-DELIVERY-CONTRACT-RESIDUAL-2026-07-24
> **Fase**: F (verificación E2E + análisis)
> **Ejecución**: MIXTO (delegate_task para v4complete + DIRECTO para análisis)
> **Dependencias**: FASE-A, B, C, D, E completadas (todos los fixes + tests)
> **Próxima fase**: FASE-RELEASE

---

## Contexto

Esta fase ejecuta v4complete para Zi One Luxury (https://zione.co/) con los 7 fixes
aplicados, y luego verifica que cada fix se manifestó correctamente en el output.
Es la única ejecución de v4complete del plan.

**Datos reales**: `output/clientes/zi-one-luxury_onboarding.yaml`
```yaml
hotel:
  nombre: Zi One Luxury
  ubicacion: Pereira, Eje Cafetero
datos_operativos:
  habitaciones: 34
  reservas_mes: 800
  valor_reserva_cop: 290000
  canal_directo_pct: 40.0
metadatos:
  fuente: observations_tier_a
  campos_confirmados: [habitaciones, reservas_mes, valor_reserva_cop, canal_directo_pct]
  source_note: Datos reales de data/hotel_observations/observations.json (Tier A verified, confidence 0.95)
```

---

## Tareas

### Tarea F-1: Ejecutar v4complete para Zi One Luxury (SUBAGENTE)

**Ejecución**: delegate_task con timeout=900s

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe main.py v4complete --url https://zione.co/
```

**Timeout**: 900 segundos (15 minutos) — v4complete toma 5-10 minutos.

**Post-ejecución inmediata (subagent)**:
1. Guardar evidencia: copiar output a `output/v4_complete/deliveries/zione_YYYYMMDD.zip`
2. Listar archivos del ZIP: `unzip -l output/v4_complete/deliveries/zione_*.zip`
3. Leer MANIFEST.json del ZIP
4. Leer README_DELIVERY.md del ZIP
5. Leer delivery_quality_report.json de `output/v4_complete/zione/v4_audit/`
6. Reportar: archivos generados, gates status, coherence score, ZIP count

### Tarea F-2: Análisis post-implementación (DIRECTO — main agent)

El main agent tiene el contexto completo de las 7 fases anteriores. Verificar
cada finding contra el v4complete output usando la matriz de verificación:

| Finding | Verificación | Archivo de salida |
|---------|-------------|-------------------|
| P-01 | README `Contents:` == MANIFEST `total_files` | README_DELIVERY.md, MANIFEST.json |
| P-02 | 0 assets aparecen en 2 secciones simultáneamente | README_DELIVERY.md |
| P-03 | `coherence_score` == post-gen (o ambos reportados) | delivery_quality_report.json |
| P-04 | proposal_asset_matrix alineado con DeliveryContext | proposal_asset_matrix.json |
| P-05 | G9 muestra `passed: <bool>` con valor real (no default True) | delivery_quality_report.json |
| P-06 | `proposal_asset_matrix.json` aparece en ZIP entries | MANIFEST.json |
| P-07 | L603 usa `DeliveryAssetState.DELIVERED` (no string) | delivery_packager.py |

Para cada finding:
1. Leer el archivo de salida correspondiente
2. Aplicar la verificación
3. Reportar: PASS / FAIL / PARTIAL
4. Si FAIL: diagnosticar causa (¿el fix no se aplicó? ¿edge case? ¿test fixture issue?)

### Tarea F-3: Completar 10-analisis-post-implementacion.md

Llenar el template de retrospectiva (10-analisis-post-implementacion.md) con:
- Tabla de ejecución por fase (sesión, iteraciones, status, delegate_task usado)
- Análisis de la fase de mayor complejidad (FASE-C)
- Matriz de viabilidad delegate_task por fase
- Matriz de verificación de los 7 fixes
- Lecciones aprendidas

---

## Criterios de Completitud

- [ ] v4complete ejecutado sin errores para https://zione.co/
- [ ] ZIP generado en `output/v4_complete/deliveries/`
- [ ] P-01 verificado: README count == MANIFEST count (S-1, S-7)
- [ ] P-02 verificado: 0 assets en múltiples secciones (S-2, S-7)
- [ ] P-03 verificado: post-gen score usado (S-3)
- [ ] P-04 verificado: matrix alineada (S-4)
- [ ] P-05 verificado: G9 evaluado realmente (S-8)
- [ ] P-06 verificado: matrix en ZIP (S-9)
- [ ] P-07 verificado: enum usado (código)
- [ ] 10-analisis-post-implementacion.md completado con matriz de verificación
- [ ] Commit con mensaje descriptivo

---

## Post-Ejecución

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-F-DT2 --desc "v4complete_zione_post_impl_analysis_7_fixes_verified"
```

---

## Prompt para delegate_task (v4complete — SUBAGENTE)

```
Goal: Execute v4complete for Zi One Luxury and capture evidence of all 7 fixes

Context:
- Repo path: /mnt/c/Users/Jhond/Github/iah-cli
- URL: https://zione.co/
- Onboarding data: output/clientes/zi-one-luxury_onboarding.yaml (Tier A, 34 hab, 800 reservas/mes)

Steps:
1. cd /mnt/c/Users/Jhond/Github/iah-cli
2. Run: ./venv/Scripts/python.exe main.py v4complete --url https://zione.co/
   (This takes 5-10 minutes. If it fails, report the error.)
3. After completion, capture evidence:
   a. List ZIP: unzip -l output/v4_complete/deliveries/zione_*.zip | head -60
   b. Read MANIFEST.json from the ZIP (extract or use python to read)
   c. Read README_DELIVERY.md from the ZIP — specifically the "Contents:" line
   d. Read output/v4_complete/zione/v4_audit/delivery_quality_report.json
   e. Read output/v4_complete/zione/v4_audit/coherence_validation_post_gen.json (if exists)
   f. Check if proposal_asset_matrix.json appears in the ZIP file listing
   g. Read output/v4_complete/v4_audit/proposal_asset_matrix.json (if exists)
4. Report ALL findings in a structured summary:
   - Total files in ZIP
   - total_files in MANIFEST.json
   - "Contents:" count in README_DELIVERY.md
   - coherence_score in delivery_quality_report.json
   - coherence score in post_gen file (if exists)
   - proposal_asset_gate value in delivery_quality_report.json
   - Whether proposal_asset_matrix.json is in the ZIP
   - Gate status summary (how many PASS/FAIL)
```

---

## Próxima Sesión

```
Carga el plan DT-2 en /mnt/c/Users/Jhond/Github/iah-cli/.opencode/plans/DT-2-DELIVERY-CONTRACT-RESIDUAL-2026-07-24/
Ejecuta FASE-RELEASE: 08-prompt-fase-release.md (RELEASE v4.63.2)
```
