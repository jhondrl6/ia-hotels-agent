# FASE-PATCH-C: v4complete Verification Run

**ID**: FASE-PATCH-C
**Objetivo**: Ejecutar v4complete para AmaziliaHotel y verificar que TODOS los fixes de PATCH-A y PATCH-B se reflejan correctamente en el output
**Dependencias**: FASE-PATCH-A ✅ + FASE-PATCH-B ✅
**Duración estimada**: ~15-20 min (más 5-10 min de v4complete)
**Skill**: iah-cli-phased-execution
**⚠️ CONTIENE COMANDO DE LARGA DURACIÓN (v4complete)**

---

## Contexto

Las fases PATCH-A y PATCH-B corrigieron 9 hallazgos en el código. Esta fase verifica que los fixes se materializan correctamente en una ejecución real de v4complete.

**Fixes a verificar**:

| Fase | Fix | Verificación esperada en output |
|------|-----|-------------------------------|
| PATCH-A | BUG-1 (ROI X) | Propuesta muestra `ROI: 0.2X` (con X) |
| PATCH-A | BUG-2 (pain_ratio) | Proyección explica pain_ratio o beneficio > $0 |
| PATCH-A | H-3 (blog_activo) | Diagnóstico NO muestra "blog_activo: false" fijo |
| PATCH-A | H-4 (speakable) | Diagnóstico NO muestra "speakable: false" fijo |
| PATCH-A | H-5 (ga4) | Diagnóstico NO muestra "ga4_indirect: false" fijo |
| PATCH-B | H-1 (web_score) | Propuesta NO muestra web_score "85" |
| PATCH-B | H-2 (phone) | Sin placeholder "+57 300 123 4567" |
| PATCH-B | H-6 (Evidence Tier) | Tier no es "C" fijo sin justificación |

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-1-AMAZILIA-CORRECCION (1A/1B/1C) | ✅ Completada |
| FASE-PATCH-A | ✅ Completada |
| FASE-PATCH-B | ✅ Completada |

---

## Tareas

### Tarea 1: Ejecutar v4complete (COMANDO LARGO)

**Objetivo**: Generar diagnóstico + propuesta + assets para AmaziliaHotel con los fixes aplicados.

```bash
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/
```

**⚠️ Estrategia de iteraciones**: 
- Si el presupuesto de iteraciones lo permite (>30 restantes), ejecutar DIRECTAMENTE con `terminal(..., timeout=600)`
- Si el presupuesto es ajustado (<30 restantes), usar subagente via `delegate_task`:
  ```
  delegate_task(
    goal="Ejecutar v4complete para amaziliahotel.com",
    context="Comando: ./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/",
    toolsets=["terminal"]
  )
  ```

**Criterios de aceptación**:
- [ ] v4complete termina sin errores
- [ ] Se generan: 01_DIAGNOSTICO, 02_PROPUESTA, assets, gate_report

### Tarea 2: Guardar evidencia proactiva (OBLIGATORIO — INMEDIATAMENTE post-v4complete)

**Objetivo**: Preservar el output antes de cualquier verificación, por si el agente se agota.

```bash
mkdir -p evidence/fase-patch-auditoria-v2/
cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/fase-patch-auditoria-v2/
cp output/v4_complete/02_PROPUESTA_*.md evidence/fase-patch-auditoria-v2/
cp output/v4_complete/amaziliahotel/v4_audit/*.json evidence/fase-patch-auditoria-v2/ 2>/dev/null
cp output/v4_complete/gate_report.json evidence/fase-patch-auditoria-v2/ 2>/dev/null
cp output/v4_complete/v4_complete_report.json evidence/fase-patch-auditoria-v2/ 2>/dev/null
cp output/v4_complete/financial_scenarios.json evidence/fase-patch-auditoria-v2/ 2>/dev/null
```

**⚠️ Esto es OBLIGATORIO sin importar el presupuesto de iteraciones.**

**Criterios de aceptación**:
- [ ] Archivos copiados a `evidence/fase-patch-auditoria-v2/`
- [ ] Directorio contiene al menos: 01_DIAGNOSTICO, 02_PROPUESTA

### Tarea 3: Verificar output contra criterios de aceptación

**Objetivo**: Leer los archivos generados y verificar que cada fix se refleja.

**Verificaciones puntuales**:

```bash
# 1. BUG-1: ROI debe mostrar "X"
grep -n "ROI.*0\.2" output/v4_complete/02_PROPUESTA_*.md

# 2. BUG-2: Proyección debe explicar pain_ratio o beneficio > 0
grep -n -A5 "Beneficio neto\|pain_ratio\|Recupera" output/v4_complete/02_PROPUESTA_*.md

# 3. H-1: web_score NO debe ser "85"
grep -n "web_score\|85" output/v4_complete/01_DIAGNOSTICO_*.md

# 4. H-3/H-4/H-5: No deben mostrar "false" fijo sin contexto
grep -n "blog_activo\|speakable_schema\|ga4_indirect" output/v4_complete/01_DIAGNOSTICO_*.md

# 5. H-2: No debe aparecer el placeholder de teléfono
grep -n "+57 300 123 4567" output/v4_complete/02_PROPUESTA_*.md

# 6. H-6: Evidence Tier
grep -n "Tier\|evidence_tier" output/v4_complete/01_DIAGNOSTICO_*.md

# 7. Coherence + gates
./venv/Scripts/python.exe -c "
import json
with open('output/v4_complete/v4_complete_report.json') as f:
    r = json.load(f)
print(f'Coherence: {r.get(\"coherence_score\", \"N/A\")}')
with open('output/v4_complete/gate_report.json') as f:
    g = json.load(f)
print(f'Ready: {g.get(\"ready\", \"N/A\")}')
"
```

**Criterios de aceptación por fix**:
- [ ] BUG-1 ✅: `ROI: 0.2X` (con X) o formato correcto
- [ ] BUG-2 ✅: Proyección NO muestra beneficio neto $0 sin explicación
- [ ] H-3/H-4/H-5 ✅: blog/speakable/ga4 no son "false" sin evaluación
- [ ] H-1 ✅: web_score no es "85" hardcodeado
- [ ] H-2 ✅: Sin placeholder de teléfono falso
- [ ] H-6 ✅: Evidence Tier no es "C" sin justificación
- [ ] Coherence >= 0.80
- [ ] Gates: ready = true (o documentar qué gate falla y por qué)

---

## Post-Ejecución (OBLIGATORIO)

1. Actualizar `dependencias-fases-v2.md`
2. Actualizar `06-checklist-implementacion-v2.md`
3. Actualizar `README-v2.md`

---

## Criterios de Completitud (CHECKLIST)

- [ ] v4complete ejecutado sin errores
- [ ] Evidencia guardada en `evidence/fase-patch-auditoria-v2/`
- [ ] BUG-1 verificado en propuesta
- [ ] BUG-2 verificado en propuesta
- [ ] H-3/H-4/H-5 verificados en diagnóstico
- [ ] H-1 verificado (no "85")
- [ ] H-2 verificado (no placeholder)
- [ ] H-6 verificado (no "C" fijo)
- [ ] Coherence >= 0.80

---

## Restricciones

- **NO modificar código fuente** — solo verificar
- **Máximo 60 iteraciones**
- **Evidencia proactiva OBLIGATORIA** inmediatamente post-v4complete
- Si algún fix NO se refleja, documentar el gap en vez de intentar arreglarlo en esta fase
