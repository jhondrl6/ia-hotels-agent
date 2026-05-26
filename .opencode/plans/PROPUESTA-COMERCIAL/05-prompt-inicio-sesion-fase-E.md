# FASE-E: Paquete comercial + Pulido + Gate blocking (A-2, V-4/5/6, A-3, CROSS-6)

**ID**: FASE-E
**Objetivo**: Unificar umbral AEO, completar el paquete comercial (cupo, garantía, prueba social), corregir typo, y hacer que gates NOT_READY bloqueen la generación de documentos.
**Dependencias**: FASE-D (pipeline ya limpio para que CROSS-6 sea efectivo)
**Duración estimada**: 2-3 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

Última fase de implementación antes del v4complete. Agrupa los hallazgos restantes:

- **A-2**: El umbral AEO es 20 en `_generate_dynamic_services_table()` (L1035) pero 30 en `_generate_technical_assets_table()` (L1235). Hotel con score_aeo=25 ve fila AEO en una tabla pero no en la otra.
- **V-4**: "Válido por 15 días (cupo limitado)" — sin lógica que controle, justifique o cuantifique.
- **V-5**: Garantía de "10% más consultas directas" no medible si el cliente no tiene GA4 configurado.
- **V-6**: Sin sección de testimonios/casos de éxito en el template.
- **A-3**: Typo "PASSO" en template propuesta L173.
- **CROSS-6**: Gates `NOT_READY` no bloquean la generación — los documentos se crean igual con bugs conocidos.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada (asumido) |
| FASE-B | ✅ Completada (asumido) |
| FASE-C | ✅ Completada (asumido) |
| FASE-D | ✅ Completada (asumido) |

---

## Tareas

### Tarea 1: Unificar umbral AEO a 30 (A-2)

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py`

**Cambios**:
- L1035: `< 20` → `< 30`
- L1235: Ya es `< 30` ✅ (solo verificar)

**Criterios de aceptación**:
- [ ] Ambas tablas usan el mismo umbral (30)
- [ ] Hotel con score_aeo=25 ve fila AEO en AMBAS tablas
- [ ] Hotel con score_aeo=35 no ve fila AEO en NINGUNA

### Tarea 2: Completar paquete comercial (V-4, V-5, V-6)

**Archivos**:
- `modules/commercial_documents/templates/propuesta_v6_template.md`

**Cambio V-4 — Justificar cupo limitado**:
```markdown
# ANTES
**Válido por 15 días** (cupo limitado)

# DESPUÉS
**Válido por 15 días** — 2 cupos disponibles para julio 2026
```

**Cambio V-5 — Garantía medible**:
```markdown
# ANTES (L162-163)
Garantizamos un 10% más de consultas directas en 90 días

# DESPUÉS
Garantizamos un 10% más de consultas directas en 90 días.  
Instalamos tracking propio en el Día 7 — sin necesidad de que tengas GA4.
```

**Cambio V-6 — Prueba social (placeholder)**:
Agregar después de la sección de garantías:
```markdown
### 🏨 Hoteles que ya confiaron en nosotros

> *[Espacio para casos de éxito — hoteles del Eje Cafetero con resultados medibles]*
```

**Criterios de aceptación**:
- [ ] Cupo limitado tiene justificación numérica
- [ ] Garantía incluye mecanismo de medición (tracking propio Día 7)
- [ ] Placeholder de prueba social presente sin romper el layout

### Tarea 3: Corregir typo "PASSO" → "PASO" (A-3)

**Archivo**: `modules/commercial_documents/templates/propuesta_v6_template.md` L173

**Cambio**: `SIGUIENTE PASSO` → `SIGUIENTE PASO`

**Criterios de aceptación**:
- [ ] Sin "PASSO" residual en ningún template o generador
- [ ] Verificar con grep: `grep -rn 'PASSO' modules/`

### Tarea 4: Hacer que gates NOT_READY bloqueen generación (CROSS-6)

**Archivo**: `modules/quality_gates/publication_gates.py` — donde se evalúa `NOT_READY` vs `READY_FOR_PUBLICATION`

**Investigación previa**: El archivo `publication_gates.py` tiene la lógica en L1225-1264. `status: "NOT_READY"` se asigna pero no bloquea la escritura de archivos.

**Objetivo**: Si `publication_gates.status == "NOT_READY"`, el pipeline debe:
1. NO escribir `01_DIAGNOSTICO_*.md` ni `02_PROPUESTA_*.md`
2. Escribir un `BLOCKED_BY_GATES.md` con la lista de gates fallidos
3. El `v4_complete_report.json` sigue generándose (para debugging)

**Criterios de aceptación**:
- [ ] Gates NOT_READY → no se escriben documentos cliente
- [ ] Se genera `BLOCKED_BY_GATES.md` con diagnóstico
- [ ] Gates READY → comportamiento normal (sin cambios)

---

## Tests Obligatorios

| Test | Comando | Criterio |
|------|---------|----------|
| Tests AEO | `pytest tests/commercial_documents/ -v -k "aeo" --timeout=60` | Umbral unificado |
| Tests publication gates | `pytest tests/quality_gates/ -v -k "publication" --timeout=60` | Bloqueo funciona |
| Validación rápida | `python scripts/run_all_validations.py --quick` | 4/4+ checks |

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar FASE-E como ✅ Completada
2. **`06-checklist-implementacion.md`**: Marcar items E1-E6 como ✅
3. **`09-documentacion-post-proyecto.md`**: Agregar cambios
4. Ejecutar:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-E \
    --desc "A-2: umbral AEO 30 + V-4/5/6: cupo/garantía/prueba social + A-3: typo PASSO + CROSS-6: gate blocking" \
    --archivos-mod "modules/commercial_documents/v4_proposal_generator.py,modules/commercial_documents/templates/propuesta_v6_template.md,modules/quality_gates/publication_gates.py" \
    --tests "0" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] A-2: Umbral AEO = 30 en ambas tablas
- [ ] V-4: Cupo limitado justificado ("2 cupos para julio 2026")
- [ ] V-5: Garantía incluye tracking propio Día 7
- [ ] V-6: Placeholder de prueba social presente
- [ ] A-3: "PASSO" corregido a "PASO"
- [ ] CROSS-6: Gates NOT_READY bloquean generación de documentos
- [ ] `run_all_validations.py --quick` pasa
- [ ] `dependencias-fases.md` actualizado
- [ ] `06-checklist-implementacion.md` actualizado
- [ ] `09-documentacion-post-proyecto.md` actualizado
- [ ] `log_phase_completion.py` ejecutado

---

## Restricciones

- NO modificar `scenario_calculator.py`
- NO ejecutar v4complete
- NO eliminar la garantía existente — solo complementarla con tracking propio
- CROSS-6: el bloqueo debe ser configurable (flag) para no romper CI/tests
- Máximo 60 iteraciones de agente
