# FASE-D: Ejecutar v4complete Hotel Castilla Real + Verificación Contra Prospección.md

**ID**: FASE-D
**Objetivo**: Ejecutar v4complete para Hotel Castilla Real con todos los fixes de FASE-A/B/C aplicados, verificar que el output satisface TODOS los criterios de `Prospección.md`, preservar evidencia.
**Dependencias**: FASE-A ✅, FASE-B ✅, FASE-C ✅ (OBLIGATORIO — las 3 deben estar completadas)
**Duración estimada**: 2-3 horas (v4complete tarda 5-10 min)
**Skill**: `phased_project_executor`
**Tipo**: 3 tareas + 1 comando largo (v4complete)

---

## Contexto

Después de implementar los 6 fixes (E1, E2, F1, F2, F3, F4) en las fases A, B, C, se debe verificar que el pipeline completo produce un diagnóstico que satisface los criterios de prospección B2B definidos en `.opencode/context/Prospección.md`.

Hotel objetivo: **Hotel Castilla Real** — https://www.hotelcastillareal.com/

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada |
| FASE-B | ✅ Completada |
| FASE-C | ✅ Completada |

### Línea Base (output 2026-05-25, pre-fixes)

| Métrica | Valor |
|---------|-------|
| Coherence Score | 0.826 |
| Gate Status | PASSED (con warnings) |
| Problemas detectados | 6 (E1, E2, F1, F2, F3, F4) |

---

## Tareas

### Tarea 1: Pre-vuelo — verificar que los fixes están en su lugar

**Objetivo**: Antes de ejecutar v4complete, confirmar que los archivos modificados en FASE-A/B/C contienen los cambios esperados.

**Verificaciones**:
- [ ] `_build_scenario_table_rows()` en `v4_diagnostic_generator.py` — clamp eliminado, usa `financial_value_range`
- [ ] `diagnostico_v6_template.md` Sección 1 — tabla "Antes vs Ahora" presente
- [ ] `_build_quick_wins()` — texto en lenguaje de dueño
- [ ] `_prepare_financial_template_vars()` — `precision_warning` reformulado como gancho
- [ ] `diagnostico_v6_template.md` Sección 4 — texto puente presente
- [ ] `_build_brechas_resumen_section()` — encabezado "Fuga mensual estimada"

### Tarea 2: Ejecutar v4complete para Hotel Castilla Real

**Objetivo**: Ejecutar el pipeline completo y generar nuevo output.

**Comando**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli && ./venv/Scripts/python.exe main.py v4complete --url https://www.hotelcastillareal.com/
```

**Ejecución**: Usar `terminal(timeout=600, notify_on_complete=True, background=True)`.

Si el presupuesto de iteraciones es ajustado, usar `delegate_task` con el comando.

**Resultado esperado**:
- `01_DIAGNOSTICO_Y_OPORTUNIDAD_*.md` generado
- `02_PROPUESTA_COMERCIAL_*.md` generado
- `coherence_score >= 0.80`
- Assets generados

### Tarea 3: Verificar output contra criterios de Prospección.md

**Objetivo**: Leer el diagnóstico generado y verificar los 6 criterios:

| # | Criterio | Verificación |
|---|----------|-------------|
| E1 | Conservador ($2.99M) < Realista ($3.74M) < Optimista ($4.49M) | Leer tabla de escenarios en output |
| E2 | Tabla "Antes (2023) vs Ahora (2026)" presente en Sección 1 | Buscar en output |
| F1 | Quick Wins: "HOY (5 min)", "ESTA SEMANA", "DELEGAR" | Leer Sección 5 |
| F2 | "OPORTUNIDAD DE AUDITORÍA PROFUNDA" en vez de "Precisión limitada" | Leer Sección 3 |
| F3 | "De las 7 brechas técnicas..." al inicio de Sección 4 | Buscar en output |
| F4 | Encabezado "Fuga mensual estimada" en tabla resumen | Leer tabla final |

**Criterios de aceptación**:
- [ ] 6/6 criterios satisfechos
- [ ] Coherence score ≥ 0.80
- [ ] Sin regresiones en gates

**Si algún criterio falla**: Documentar cuál, analizar causa, y determinar si se necesita FASE-D-HOTFIX o si es aceptable para release.

---

## Protocolo de Evidencia (OBLIGATORIO)

Inmediatamente después de que v4complete genere output:

```bash
mkdir -p /mnt/c/Users/Jhond/Github/iah-cli/evidence/fase-D
cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/fase-D/
cp output/v4_complete/02_PROPUESTA_*.md evidence/fase-D/
cp output/v4_complete/hotelcastillareal/v4_audit/*.json evidence/fase-D/
cp output/v4_complete/v4_complete_report.json evidence/fase-D/
```

---

## Post-Ejecución (OBLIGATORIO)

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-D \
    --desc "v4complete Hotel Castilla Real post-fixes — verificación 6/6 criterios Prospección.md" \
    --archivos-mod "output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_*.md,output/v4_complete/02_PROPUESTA_COMERCIAL_*.md" \
    --tests "0" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] v4complete ejecutado exitosamente para Hotel Castilla Real
- [ ] E1: Tabla de escenarios correcta (Conservador < Realista < Optimista)
- [ ] E2: Tabla "Antes vs Ahora" presente
- [ ] F1: Quick Wins en lenguaje de dueño
- [ ] F2: Disclaimer convertido en gancho comercial
- [ ] F3: Texto puente 7 brechas → 3 fugas
- [ ] F4: Encabezado "Fuga mensual estimada"
- [ ] Coherence score ≥ 0.80
- [ ] Evidencia preservada en `evidence/fase-D/`
- [ ] `dependencias-fases.md` actualizado
- [ ] `06-checklist-implementacion.md` actualizado
- [ ] `09-documentacion-post-proyecto.md` actualizado
- [ ] `log_phase_completion.py` ejecutado

---

## Restricciones

- NO modificar código fuente — solo ejecutar y verificar
- Si algún fix no funciona, documentar y pasar a FASE-RELEASE con nota
- Máximo 60 iteraciones de agente
- Usar `delegate_task` para v4complete si el presupuesto de iteraciones es < 30
