# Prompt de Inicio de Sesion: FASE-2-B

> **Fase**: 2-B — Verificacion E2E con v4complete  
> **Plan maestro**: `PLAN-REFACTOR-TERMALES-20260508.md`  
> **Iteraciones max**: 60  
> **Contexto previo**: FASE-PRE + FASE-1-A + FASE-1-B + FASE-2-A completadas  
> **Comando largo**: v4complete (1 unico del plan)  

---

## Tareas de la Fase

TAREAS DE LA FASE:
  [ ] Revisar estado de fixes previos (confirmar FASE-1-A, 1-B, 2-A aplicados)
  [ ] Ejecutar v4complete para Termales Santa Rosa de Cabal
  [ ] Guardar evidencia proactiva (OBLIGATORIO, inmediatamente post-ejecucion)
  [ ] Verificar outputs contra metricas de exito
  [ ] Documentacion post-fase

CONTADOR:
  - Total tareas: 4 (revision + v4complete + verificacion + docs)
  - Comandos largos: 1 (v4complete)
  - Estado: dentro del limite R3 (max 3 tareas + 1 comando largo; revision cuenta como 1)

---

## Contexto de Fases Anteriores

- FASE-PRE: Saneamiento completado
- FASE-1-A: Template engine (`{{if}}` pre-procesado) + Coherence validator (usa generated_assets)
- FASE-1-B: Content Scrubber Rule 6 ([PENDING*] bloquea) + monthly_report (tabla dinamica)
- FASE-2-A: SitePresenceChecker hardening + indirect_traffic (audit-aware) + FAQ (site scraping)

Todos los fixes aplicados. Esta fase verifica si funcionan en conjunto.

---

## Instrucciones Detalladas

### 1. Revisar Estado de Fixes (checkpoint rapido)

Antes de ejecutar v4complete, confirmar que los cambios estan en disco:

```bash
# Verificar que los archivos modificados existen y tienen los cambios
grep -n "_preprocess_conditionals" modules/commercial_documents/v4_proposal_generator.py
grep -n "generated_assets" modules/commercial_documents/coherence_validator.py
grep -n "_fix_pending_markers" modules/postprocessors/content_scrubber.py
grep -n "_generate_assets_table" modules/asset_generation/monthly_report_generator.py
grep -n "presence_status.*unknown" modules/quality_gates/publication_gates.py
```

Si alguno falta, reportar en checklist y NO ejecutar v4complete. La fase queda bloqueada.

### 2. Ejecutar v4complete

**Comando**:
```bash
./venv/Scripts/python.exe main.py v4complete --url http://www.termales.com.co/
```

**Regla de decision: directo vs subagente**:

```
Presupuesto total: 60 iteraciones
Gastos fijos:
  - Revision checkpoint: ~3 iteraciones
  - v4complete (terminal call): ~1 iteracion
  - Guardar evidencia: ~2 iteraciones
  - Verificacion: ~10-15 iteraciones
  - log_phase + docs: ~10 iteraciones
  Total fijo: ~26-31 iteraciones

Margen: 29-34 iteraciones para trabajo especifico.

SI margen >= 30:
  → Ejecutar DIRECTAMENTE con terminal(timeout=600, notify_on_complete=True)
SI margen < 30:
  → Spawn subagente via delegate_task(
      goal="Ejecutar v4complete para Termales y guardar evidencia",
      context="URL: http://www.termales.com.co/, comando: ./venv/Scripts/python.exe main.py v4complete --url http://www.termales.com.co/",
      timeout=900,
      notify_on_complete=True,
      toolsets=["terminal"]
    )
  → Agente principal usa iteraciones solo para verificacion + docs
```

**Timeout**: 600 segundos (10 min). v4complete tarda 5-10 min.

### 3. Guardar Evidencia Proactiva (OBLIGATORIO)

**Inmediatamente despues de que v4complete termine**, ANTES de cualquier verificacion:

```bash
mkdir -p evidence/fase-2-B

# Diagnosticos y propuestas
cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/fase-2-B/ 2>/dev/null || true
cp output/v4_complete/02_PROPUESTA_*.md evidence/fase-2-B/ 2>/dev/null || true

# Audits y reportes JSON (hotel_id para Termales: termales)
cp output/v4_complete/termales/v4_audit/*.json evidence/fase-2-B/ 2>/dev/null || true

# Assets
cp output/v4_complete/termales/monthly_report/*.md evidence/fase-2-B/ 2>/dev/null || true
cp output/v4_complete/termales/llms_txt/*.txt evidence/fase-2-B/ 2>/dev/null || true

# Listar lo que se copio
ls -la evidence/fase-2-B/
```

**Esta regla no tiene excepciones.** Si el agente se agota despues, la evidencia ya esta a salvo.

### 4. Verificar Outputs contra Metricas de Exito

**Criterios de aceptacion** (basados en ANALISIS_V4COMPLETE_TERMALES_20260508.md):

| # | Metrica | Como verificar | Aceptable |
|---|---------|---------------|-----------|
| 1 | Sin `{{if}}...{{endif}}` en propuesta | `grep -c "{{if" evidence/fase-2-B/02_PROPUESTA_*.md` | 0 |
| 2 | Coherence refleja assets reales | `jq '.overall_score' evidence/fase-2-B/coherence_validation.json` | <= 0.85 (esperado ~0.57 si 3 faltan) |
| 3 | monthly_report dinamico | `grep -c "Geo Playbook" evidence/fase-2-B/*informe_mensual*.md` | 0 |
| 4 | Sin [PENDING*] en documentos | `grep -r "\[PENDING_" evidence/fase-2-B/ | wc -l` | 0 |
| 5 | WhatsApp detectado | `jq '.whatsapp_button.present_in_production' evidence/fase-2-B/gate_report_*.json` | true |
| 6 | Schema detectado | `jq '.schema_hotel.present_in_production' evidence/fase-2-B/gate_report_*.json` | true |
| 7 | Sin placeholders genericos | `grep -c "+57 300 000 0000" evidence/fase-2-B/02_PROPUESTA_*.md` | 0 |

**Veredicto**:
- Si 6+ metricas pasan: "Implementacion EFECTIVA"
- Si 4-5 metricas pasan: "Implementacion PARCIAL — revisar gaps"
- Si <4 metricas pasan: "Implementacion NO EFECTIVA — requiere nueva iteracion"

**Documentar resultado** en `.opencode/plans/PLAN-REFACTOR-TERMALES-20260508.md` bajo nueva seccion `## Resultado Verificacion FASE-2-B`.

---

## Post-Ejecucion (al finalizar la sesion)

1. **Marcar checklist** en `.opencode/plans/06-checklist-implementacion.md`:
   - FASE-2-B: estado y tareas completadas
   - Incluir veredicto: EFECTIVA / PARCIAL / NO EFECTIVA

2. **Ejecutar log_phase_completion.py**:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-2-B \
    --desc "Verificacion E2E v4complete Termales: {veredicto}" \
    --archivos-nuevos "" \
    --archivos-mod "" \
    --tests "0" \
    --check-manual-docs
```

3. **Actualizar 09-documentacion-post-proyecto.md**:

```markdown
## Seccion D: Metricas Acumulativas
| Metrica | Valor | Fase |
|---------|-------|------|
| v4complete metricas pasadas | X/7 | FASE-2-B |
| Veredicto E2E | {EFECTIVA/PARCIAL/NO EFECTIVA} | FASE-2-B |

## Seccion E: Archivos Afiliados Actualizados
| Archivo | Cambio | Fase |
|---------|--------|------|
| evidence/fase-2-B/ | Evidencia v4complete Termales | FASE-2-B |
```

4. **Si la sesion se agota**: la evidencia ya fue guardada en paso 3. Marcar fase como `⏳ INCOMPLETA` con checkpoint en verificacion.

---

## Criterios de Completitud

- [ ] Fixes previos confirmados en disco
- [ ] v4complete ejecutado (exit code 0)
- [ ] Evidencia copiada a `evidence/fase-2-B/` (lista de archivos verificada)
- [ ] 7 metricas verificadas con conteo/grep/jq
- [ ] Veredicto documentado: EFECTIVA / PARCIAL / NO EFECTIVA
- [ ] `log_phase_completion.py` ejecutado
- [ ] Checklist maestro actualizado

---

## Restricciones

- **UNICA ejecucion de v4complete en todo el plan**. No ejecutar de nuevo en otra fase.
- **Evidencia proactiva es OBLIGATORIA** — ejecutar inmediatamente post-v4complete, antes de cualquier otra cosa.
- **Max 60 iteraciones**. Si se agota, guardar evidencia y marcar incompleta.
- **NO implementar codigo nuevo** — esta fase es solo verificacion.
- **NO modificar fixes previos** durante la verificacion; si un fix no funciona, documentar para nueva fase PATCH.

---

*Prompt generado por orquestador siguiendo phased_project_executor.md v2.10.0*
