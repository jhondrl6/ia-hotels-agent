# FASE-5: Verificación E2E con v4complete (Luxorhotel)

**ID**: FASE-5
**Objetivo**: Ejecutar `v4complete` end-to-end para Luxorhotel y verificar que todos los fixes de FASE-1 a FASE-4 funcionan en el pipeline real.
**Dependencias**: FASE-1, FASE-2, FASE-3, FASE-4 (todas completadas ✅)
**Duración estimada**: 1-2 horas (5-10 min de v4complete + verificación)
**Skill**: `phased-project-executor`

---

## Contexto

Plan: BUGFIX-LUXOR-2026-07-06 v4.60.1
Contexto origen: `.opencode/context/bugs_no_onboarding_luxor_2026-07-06.md`

Esta fase ejecuta el pipeline completo contra Luxorhotel para verificar que todos los fixes de FASE-1 a FASE-4 funcionan en un entorno real. El comando `v4complete` tarda 5-10 minutos (scraping + APIs + generación de documentos + assets).

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-1 | ✅ Completada (BUG-2 + BUG-1) |
| FASE-2 | ✅ Completada (BUG-4a openrouter) |
| FASE-3 | ✅ Completada (BUG-5 scrubber) |
| FASE-4 | ✅ Completada (BUG-6 SPA) |

### Base Técnica Disponible
- Pipeline completo con todos los fixes aplicados
- URL objetivo: `http://www.luxorhotel.com.co/`
- Evidence base: `evidence/luxor-v4complete/` (ejecución original con bugs)

---

## Tareas

### T1: Ejecutar v4complete para Luxorhotel

**Objetivo**: Ejecutar el pipeline completo con todos los fixes aplicados.

**Comando:**
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe main.py v4complete --url http://www.luxorhotel.com.co/
```

**Estrategia de ejecución:**

```
SI (investigación + verificación + docs) < 30 iteraciones restantes:
    → Ejecutar v4complete DIRECTAMENTE con terminal(timeout=600)
    → Usar notify_on_complete=True para no bloquear
    → Después de verificar output y hacer docs cascade

SI no:
    → Spawn subagent via delegate_task(timeout=900, notify_on_complete=True)
    → El subagent ejecuta v4complete completo
    → El agente parent usa sus iteraciones solo en verificación + docs
```

**Pre-requisitos:**
- FASE-1 a FASE-4 completadas ✅
- `OPENROUTER_API_KEY` configurada en `.env` (para verificar BUG-4a fix)
- `GEMINI_API_KEY` opcional (BUG-4b es acción del usuario — si no está, el fix de código de FASE-2 se verifica con el test mock, y gemini seguirá dando 403 pero eso es esperado)

**Criterios de aceptación:**
- [ ] v4complete ejecuta sin errores fatales
- [ ] Output generado en `output/v4_complete/`

---

### T1.1: Protocolo de Evidencia Proactiva (OBLIGATORIO)

> [!CAUTION]
> **Inmediatamente después de que v4complete genere output**, antes de cualquier verificación:

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
mkdir -p evidence/FASE-5
cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/FASE-5/
cp output/v4_complete/02_PROPUESTA_*.md evidence/FASE-5/
cp output/v4_complete/luxorhotel/v4_audit/*.json evidence/FASE-5/
```

**Esto es OBLIGATORIO sin importar cuanto tiempo quede en el presupuesto de iteraciones.**

---

### T2: Verificar output contra criterios de éxito

**Objetivo**: Verificar que cada bug fix funcionó en el pipeline real.

**Verificaciones por bug:**

#### BUG-1: lat/lng en `_audit_competitors`
```bash
grep -n "lat:0.0, lng:0.0" evidence/FASE-5/ejecucion.log
# O en el log de la ejecución:
# NO debe aparecer "No places found for lat:0.0, lng:0.0"
# Debe mostrar coordenadas reales (lat ~4.x, lng ~-75.x para Colombia)
```

#### BUG-2: `calc_result` UnboundLocalError
```bash
grep -n "calc_result" evidence/FASE-5/ejecucion.log
# O en el log de la ejecución:
# NO debe aparecer "cannot access local variable 'calc_result'"
# NO debe aparecer "FinancialBreakdown fallo" (a menos que sea por otra razón)
```

#### BUG-4a: openrouter model
```bash
grep -n "LLM query failed for openrouter" evidence/FASE-5/ejecucion.log
# NO debe aparecer "404 Client Error: Not Found" para openrouter
# (Si GEMINI_API_KEY no está configurada, gemini 403 SÍ puede aparecer — eso es esperado y fuera del plan)
```

#### BUG-5: Content Scrubber `[SKIP]`
```bash
grep -n "\[SKIP\] Diagnostic document not available for scrubbing" evidence/FASE-5/ejecucion.log
grep -n "\[SKIP\] Proposal document not available for scrubbing" evidence/FASE-5/ejecucion.log
# NO deben aparecer warnings [SKIP] de documentos no disponibles
# Deben aparecer [SCRUB] post-T4FIX y post-gen funcionando
```

#### BUG-6: OG tags detection (SPA)
```bash
grep -n "open_graph" evidence/FASE-5/audit_report_*.json
# Verificar seo_elements.open_graph: True (si el sitio sí tiene OG tags renderizados)
# O al menos verificar que Playwright se usó para renderizar el SPA
grep -n "Playwright" evidence/FASE-5/ejecucion.log
# Debe mostrar uso de Playwright para renderizar el SPA
```

#### Métricas generales
- Coherence score ≥ 0.80
- Publication Gates: ≥ 9/11 (o baseline de 9/11 + sin nuevas regresiones)
- Sin nuevas regresiones vs. ejecución original

**Criterios de aceptación:**
- [ ] BUG-1: No aparece `lat:0.0, lng:0.0` en log
- [ ] BUG-2: No aparece `calc_result` UnboundLocalError en log
- [ ] BUG-4a: No aparece `404 Client Error` para openrouter (si API key configurada)
- [ ] BUG-5: No aparecen warnings `[SKIP]` de documentos no disponibles
- [ ] BUG-6: OG tags detectados (si el sitio los tiene) o Playwright usado para renderizar
- [ ] Coherence score ≥ 0.80
- [ ] Sin nuevas regresiones

---

## Post-Ejecución: log_phase_completion.py

**Comando (ejecutar SOLO si T1-T2 completan exitosamente):**
```bash
cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe scripts\log_phase_completion.py --fase FASE-5 --desc E2E_verification_v4complete_luxor_all_fixes --archivos-mod "" --check-manual-docs"
```

**Nota:** Si se generaron archivos de evidencia nuevos, incluirlos en `--archivos-nuevos`:
```bash
cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe scripts\log_phase_completion.py --fase FASE-5 --desc E2E_verification_v4complete_luxor_all_fixes --archivos-nuevos evidence/FASE-5/ --check-manual-docs"
```

---

## Actualizar Documentación

**Después de log_phase_completion.py:**

1. **CHANGELOG.md** (actualizar entrada):
```markdown
### FASE-5 Verificación E2E
- v4complete ejecutado para Luxorhotel con todos los fixes aplicados
- BUG-1: ✅ lat/lng reales usados en `_audit_competitors`
- BUG-2: ✅ Sin UnboundLocalError en FASE-K
- BUG-4a: ✅ openrouter usa modelo del registry (sin 404)
- BUG-5: ✅ Sin warnings [SKIP] de scrubber
- BUG-6: ✅ OG tags detectados via Playwright rendering
- Coherence score: [valor]
- Publication Gates: [valor]
```

2. **GUIA_TECNICA.md** (agregar nota técnica):
```markdown
### Notas de Cambios v4.60.1 - FASE-5

**Verificación E2E:** Ejecución v4complete para Luxorhotel post-fixes.
**Resultado:** [OK/CON_OBSERVACIONES]
**Coherence score:** [valor]
**Publication Gates:** [valor]
**Regressions:** [ninguna / lista]
```

3. **09-documentacion-post-proyecto.md** (acumular datos de métricas)

---

## Criterios de Completitud (CHECKLIST)

- [ ] **T1**: v4complete ejecutado exitosamente
- [ ] **T1.1**: Evidencia guardada en `evidence/FASE-5/`
- [ ] **T2**: BUG-1 verificado (no `lat:0.0, lng:0.0` en log)
- [ ] **T2**: BUG-2 verificado (no `calc_result` error en log)
- [ ] **T2**: BUG-4a verificado (no 404 para openrouter)
- [ ] **T2**: BUG-5 verificado (no `[SKIP]` de documentos no disponibles)
- [ ] **T2**: BUG-6 verificado (OG tags detectados o Playwright usado)
- [ ] **T2**: Coherence score ≥ 0.80
- [ ] **T2**: Sin nuevas regresiones
- [ ] **log_phase_completion.py**: Ejecutado exitosamente
- [ ] **Docs cascade**: CHANGELOG, GUIA_TECNICA, 09-documentacion actualizados

---

## Restricciones

- **NO modificar código fuente** (solo verificación)
- **NO ejecutar `sync_versions.py`** (eso es FASE-RELEASE)
- **NO modificar VERSION.yaml** (eso es FASE-RELEASE)
- **Máximo 60 iteraciones** del agente
- **Protocolo de evidencia proactiva obligatorio** post-v4complete

---

## Budget de Iteraciones Estimado

```
Fijos:
  - Leer plan + verificar estado: ~3 iters
  - Verificar FASE-1 a FASE-4 completadas: ~2 iters
  - log_phase_completion.py + docs cascade: ~10 iters
  Total fijo: ~15 iters

Específico:
  - T1 (v4complete): 1 iter (terminal con timeout=600, notify_on_complete=True)
    O delegate_task(timeout=900) si budget es ajustado
  - T1.1 (evidencia proactiva): ~3 iters
  - T2 (verificar 5 bugs + métricas): ~10-15 iters
  Total específico: ~14-19 iters

Total estimado: 29-34 iters (dentro del límite de 60)
```

**Modo de ejecución:** v4complete como subagente (delegate_task) o directo con terminal(timeout=600) según budget.

---

## Recuperación en Caso de Agotamiento

Si el agente alcanza 60 iteraciones:
1. **Si v4complete ya ejecutó:** verificar que la evidencia está guardada en `evidence/FASE-5/`
2. Marcar fase como `⏳ INCOMPLETA` en `dependencias-fases.md`
3. Documentar checkpoint:
   - ¿v4complete ejecutado? ¿Output generado?
   - ¿Evidencia guardada?
   - ¿Qué bugs se verificaron? ¿Cuáles faltan?
4. Retomar en nueva sesión: leer evidencia y continuar verificación

Si v4complete NO terminó (timeout de subagente):
1. Verificar `output/v4_complete/` para ver si hay archivos parciales
2. Re-ejecutar v4complete en nueva sesión o continuar desde output parcial

---

## Checklist Final

- [ ] v4complete ejecutado para Luxorhotel
- [ ] Evidencia guardada en `evidence/FASE-5/`
- [ ] BUG-1 verificado en log
- [ ] BUG-2 verificado en log
- [ ] BUG-4a verificado en log
- [ ] BUG-5 verificado en log
- [ ] BUG-6 verificado en log/output
- [ ] Coherence score ≥ 0.80
- [ ] Sin nuevas regresiones
- [ ] log_phase_completion.py ejecutado
- [ ] CHANGELOG.md actualizado
- [ ] GUIA_TECNICA.md actualizado
- [ ] 09-documentacion-post-proyecto.md actualizado
