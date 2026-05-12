# FASE-5-VERIFY: v4complete Hotel Castilla Real + análisis de ejecución

**ID**: FASE-5-VERIFY
**Objetivo**: Ejecutar v4complete para Hotel Castilla Real, verificar las 10 garantías post-fix (G1-G10), y generar análisis de ejecución con veredicto.
**Dependencias**: FASE-4-GATE (✅)
**Duración estimada**: 2-3 horas
**Skill**: `phased-workflow-self-improvement` (regla v4complete: 3 tareas + 1 comando largo)
**Modo de ejecución**: DIRECTO con `notify_on_complete=True` — v4complete consume 5-10 minutos (1 tool call). Presupuesto: ~10 iteraciones prep + 1 comando + ~20 iteraciones verificación + ~10 docs.

---

## Contexto

Esta es la única ejecución de v4complete del proyecto. Su propósito es verificar que los fixes de FASE-1 a FASE-4 resuelven los problemas identificados en la auditoría.

**Hotel de verificación**:
- **Nombre**: Hotel Castilla Real
- **URL**: https://www.hotelcastillareal.com/
- **hotel_id**: `hotelcastillareal`
- **Región**: eje_cafetero

**Garantías a verificar** (G1-G10):
| Gate | Verificación | Target |
|------|-------------|--------|
| G1 | `coherence_validation.overall_score == gate.coherence.value` | ✅ Iguales |
| G2 | `diagnostic_YAML.coherence_score == gate.coherence.value` | ✅ Mantener |
| G3 | `v4_complete_report` sin scores duplicados ni inexplicables | ✅ 1 score, trazable |
| G4 | `open_graph_meta.html` sin "Amazilia" | ✅ 0 matches |
| G5 | `local_content_*.md` sin "Hotel en  -" | ✅ 0 matches |
| G6 | `hotel_schema.json` con campos poblados | ✅ Poblados (requiere onboarding) |
| G7 | `whatsapp_conflict_guide` con confidence >= 0.7 | ✅ >= 0.7 |
| G8 | `financial_scenarios.evidence_tier == diagnostic.financial_evidence_tier` | ✅ Iguales |
| G9 | `CoherenceGate.execute()` llama a `_validator.validate()` | ✅ >= 1 llamada |
| G10 | Ningún generator con defaults hardcodeados de otro hotel | ✅ 0 defaults cross-hotel |

---

## Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-1-COH | ✅ Completada |
| FASE-2-DEFAULT | ✅ Completada |
| FASE-3-CONTENT | ✅ Completada |
| FASE-4-GATE | ✅ Completada |

---

## Base Técnica Disponible

- Fixes implementados en FASE-1 a FASE-4
- Contexto de auditoría: `AUDITORIA_COHERENCIA_HOTELCASTILLAREAL_20260511.md`
- Comando v4complete: `./venv/Scripts/python.exe main.py v4complete --url https://www.hotelcastillareal.com/`

---

## Tareas

### T1: Ejecutar v4complete para Hotel Castilla Real
**Objetivo**: Generar delivery completo con los fixes aplicados.

**Comando exacto**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe main.py v4complete --url https://www.hotelcastillareal.com/
```

**Configuración**:
- `timeout=600` (10 minutos)
- `notify_on_complete=True`
- Si el agente agota iteraciones antes de que termine v4complete, la fase queda ⏳ INCOMPLETA y se retoma en nueva sesión.

**Criterios de aceptación**:
- [ ] v4complete termina sin errores críticos (exit code 0)
- [ ] Se generan: diagnóstico, propuesta, assets, audit JSONs

### T2: Protocolo de Evidencia Proactiva
**Objetivo**: Preservar los archivos críticos ANTES de cualquier análisis.

**Pasos** (ejecutar INMEDIATAMENTE después de que v4complete termine):
```bash
mkdir -p evidence/FASE-5-VERIFY/v4_audit
cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/FASE-5-VERIFY/
cp output/v4_complete/02_PROPUESTA_*.md evidence/FASE-5-VERIFY/
cp output/v4_complete/hotelcastillareal/v4_audit/*.json evidence/FASE-5-VERIFY/v4_audit/
cp output/v4_complete/hotelcastillareal/coherence_validation.json evidence/FASE-5-VERIFY/
cp output/v4_complete/v4_complete_report.json evidence/FASE-5-VERIFY/
```

**Criterios de aceptación**:
- [ ] Todos los archivos críticos copiados a `evidence/FASE-5-VERIFY/`
- [ ] ZIP delivery copiado si existe

### T3: Verificar G1-G10 contra el nuevo output
**Objetivo**: Validar cada garantía con comandos concretos.

**Probes**:
```bash
# G1, G2, G3: Coherence scores
./venv/Scripts/python.exe -c "
import json, glob

cv = json.load(open('evidence/FASE-5-VERIFY/coherence_validation.json'))
gr = json.load(open(glob.glob('evidence/FASE-5-VERIFY/v4_audit/gate_report_*.json')[-1]))
vr = json.load(open('evidence/FASE-5-VERIFY/v4_complete_report.json'))

cv_score = cv['overall_score']
gr_score = [g['value'] for g in gr['gate_results'] if g['gate_name'] == 'coherence'][0]
vr_scores = [vr.get('coherence_score'), vr.get('coherence_score_post')]

print(f'G1: cv={cv_score:.4f} vs gate={gr_score:.4f} -> {"PASS" if abs(cv_score-gr_score) < 0.01 else "FAIL"}')
print(f'G3: v4_complete_report scores -> {vr_scores} (target: 1 score trazable)')
"

# G4: open_graph sin Amazilia
./venv/Scripts/python.exe -c "
import glob, re
files = glob.glob('output/v4_complete/hotelcastillareal/open_graph/*.html')
amazilia = sum(1 for f in files if 'Amazilia' in open(f, encoding='utf-8', errors='replace').read())
print(f'G4: Amazilia matches in open_graph = {amazilia} (target: 0)')
"

# G5: local_content sin location vacía
./venv/Scripts/python.exe -c "
import glob
files = glob.glob('output/v4_complete/hotelcastillareal/local_content_page/*.md')
empty = sum(1 for f in files if 'Hotel en  -' in open(f, encoding='utf-8', errors='replace').read())
print(f'G5: empty location matches = {empty} (target: 0)')
"

# G8: evidence_tier consistency
./venv/Scripts/python.exe -c "
import json, glob, re
fs = json.load(open(glob.glob('output/v4_complete/hotelcastillareal/v4_audit/financial_scenarios_*.json')[0]))
tier_json = fs.get('breakdown', {}).get('evidence_tier', 'MISSING')

# Extract from diagnostic YAML frontmatter
diag = open(glob.glob('output/v4_complete/01_DIAGNOSTICO_*.md')[0], encoding='utf-8', errors='replace').read()
tier_yaml = re.search(r'financial_evidence_tier:\s*"?([^"\n]+)"?', diag)
tier_yaml = tier_yaml.group(1) if tier_yaml else 'MISSING'

print(f'G8: JSON tier={tier_json} vs YAML tier={tier_yaml} -> {\"PASS\" if tier_json == tier_yaml else \"FAIL\"}')
"
```

**Criterios de aceptación**:
- [ ] G1-G10 verificados individualmente con PASS/FAIL documentado
- [ ] Al menos 7/10 garantías en PASS para considerar la refactorización exitosa

### T4: Generar análisis de ejecución
**Objetivo**: Documentar el resultado de la verificación con conclusiones primero.

**Archivo**: `evidence/FASE-5-VERIFY/analisis_ejecucion.md`

**Estructura obligatoria**:
```markdown
# Análisis de Ejecución — FASE-5-VERIFY
## Veredicto: [EFECTIVA / PARCIAL / NO EFECTIVA]

## Resumen (3-5 frases)

## Tabla G1-G10

## Assets generados

## Divergencias encontradas

## Recomendaciones
```

**Criterios de aceptación**:
- [ ] Archivo `analisis_ejecucion.md` generado con veredicto claro
- [ ] Conclusiones primero, evidencia después (R5 del executor)
- [ ] Referencias a commits de FASE-1 a FASE-4 si aplica

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`** — Marcar FASE-5-VERIFY como ✅ Completada.
2. **`06-checklist-implementacion.md`** — Marcar todos los items de FASE-5-VERIFY como ✅.
3. **`09-documentacion-post-proyecto.md`** — Sección D: actualizar "Coherence score post-fix" y "Assets con confidence < 0.7 post-fix".
4. **`log_phase_completion.py`**:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-5-VERIFY \
    --desc "v4complete Hotel Castilla Real post-refactor: verificacion G1-G10 y analisis de ejecucion" \
    --archivos-nuevos "evidence/FASE-5-VERIFY/analisis_ejecucion.md" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] **T1 completo**: v4complete ejecutado exitosamente
- [ ] **T2 completo**: Evidencia proactiva copiada a `evidence/FASE-5-VERIFY/`
- [ ] **T3 completo**: G1-G10 verificados con PASS/FAIL
- [ ] **T4 completo**: `analisis_ejecucion.md` generado con veredicto
- [ ] **`dependencias-fases.md` actualizado**: Estado de FASE-5-VERIFY marcado ✅
- [ ] **Documentación afiliada**: `09-documentacion-post-proyecto.md` actualizado
- [ ] **log_phase_completion.py ejecutado**: REGISTRY.md tiene entrada FASE-5-VERIFY

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- **NO modificar código fuente** en esta fase. Es verificación pura.
- **NO modificar ROADMAP.md** — solo en FASE-RELEASE.
- **Máximo 60 iteraciones**.
- **Presupuesto estimado**: ~10 iteraciones prep + 1 comando largo + ~20 verificación + ~10 docs.
- Si v4complete falla o produce errores críticos, documentar en `analisis_ejecucion.md` y decidir si requiere FASE-6 de hotfix.
