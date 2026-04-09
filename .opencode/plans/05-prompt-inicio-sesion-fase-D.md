# Prompt de Inicio de Sesion — FASE-D: Validacion E2E amaziliahotel.com

## Contexto

### Estado de Fases Anteriores
- FASE-A (WhatsApp Detection Fix): COMPLETADA
- FASE-B (Citability Narrative Fix): COMPLETADA
- FASE-C (Regional Template Fixes): COMPLETADA

### Objetivo de esta Fase
Esta fase es PURA VALIDACION. No modifica codigo. Ejecuta v4complete contra amaziliahotel.com y verifica que los 3 fixes de las fases A/B/C producen resultados correctos.

**IMPORTANTE:** Fase de validacion = NO bump de version. Agregar notas dentro de la version existente del CHANGELOG.

---

## Tareas

### T1: Preparar entorno de evidence

```bash
mkdir -p evidence/fase-d
```

### T2: Ejecutar v4complete

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/ --debug 2>&1 | tee evidence/fase-d/ejecucion.log
```

### T3: Verificar fix WhatsApp (FASE-A)

Del output del diagnostico generado (`output/v4_complete/01_DIAGNOSTICO_*.md`):

- [ ] NO aparece brecha "Sin WhatsApp" ni "Canal Directo Cerrado (Sin WhatsApp)"
- [ ] La seccion de WhatsApp muestra deteccion correcta
- [ ] Quick wins NO sugiere "Agregar Boton WhatsApp"

Si aparece "Sin WhatsApp" → FASE-A fallo, investigar.

### T4: Verificar fix Citability (FASE-B)

Del output del diagnostico:

- [ ] Si `blocks_analyzed=0`: narrativa dice "no discoverable" NO "poco estructurado"
- [ ] Si `blocks_analyzed>0` y score<30: narrativa dice "poco estructurado"
- [ ] No aparece "contenido es insuficiente o poco estructurado" cuando blocks_analyzed=0

Verificar en `output/v4_complete/audit_report.json` → citability section.

### T5: Verificar fix Regional (FASE-C)

Del output del diagnostico:

- [ ] NO aparece "yRevisan" en ningun lugar
- [ ] NO aparece "La region de Nacional" ni "Lo que esta pasando en Nacional"
- [ ] Region correcta aparece (Eje Cafetero o la que corresponda)

### T6: Verificar coherencia general

- [ ] `audit_report.json` existe y es valido JSON
- [ ] Coherence score >= 0.80
- [ ] Publication readiness = true
- [ ] No crashes ni tracebacks en el log

### T7: Capturar resultados

Guardar en `evidence/fase-d/`:
- `ejecucion.log` — output completo del v4complete
- `verificacion.txt` — checklist con resultados de T3-T6

---

## Criterios de Completitud

- [ ] v4complete ejecuta sin crashes
- [ ] Fix WhatsApp verificado (T3)
- [ ] Fix Citability verificado (T4)
- [ ] Fix Regional verificado (T5)
- [ ] Coherence >= 0.80
- [ ] Evidence capturada

---

## Post-Ejecucion

- Marcar checklist en `06-checklist-implementacion.md`
- Ejecutar `log_phase_completion.py --fase FASE-D --desc "Validacion E2E amaziliahotel.com" --check-manual-docs`
- NOTA: Como es fase de validacion sin cambios de codigo, NO crear nueva version en CHANGELOG. Agregar como subsection de la version existente.

## Comando E2E Completo

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
mkdir -p evidence/fase-d
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/ --debug 2>&1 | tee evidence/fase-d/ejecucion.log
```
