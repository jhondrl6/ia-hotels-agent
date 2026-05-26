# FASE-RELEASE: Documentación + Version Bump — PROPUESTA-COMERCIAL

**ID**: FASE-RELEASE
**Objetivo**: Cerrar formalmente el proyecto PROPUESTA-COMERCIAL: log de fases, sync de versiones, CHANGELOG, y GUIA_TECNICA.
**Dependencias**: FASE-F (resultados de v4complete incluidos en docs)
**Duración estimada**: 1 hora
**Skill**: `iah-cli-phased-execution`

---

## Contexto

El proyecto PROPUESTA-COMERCIAL corrigió 14 hallazgos en 5 fases de implementación + 1 fase de verificación. La documentación oficial debe reflejar todos los cambios para el release v4.53.0.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada |
| FASE-B | ✅ Completada |
| FASE-C | ✅ Completada |
| FASE-D | ✅ Completada |
| FASE-E | ✅ Completada |
| FASE-F | ✅ Completada |

---

## Tareas

### Tarea 1: Ejecutar `log_phase_completion.py` para TODAS las fases

**Comandos** (uno por fase):

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# FASE-A
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-A --desc "CODE-1/3/4+CODE-2: Unificación financiera + gate sync" \
    --archivos-mod "v4_proposal_generator.py,commercial_gate.py" --tests "0"

# FASE-B
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-B --desc "CROSS-1: Puente dual fuga bruta/recuperación efectiva" \
    --archivos-mod "diagnostico_v6_template.md,propuesta_v6_template.md,v4_diagnostic_generator.py,v4_proposal_generator.py" --tests "0"

# FASE-C
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-C --desc "CROSS-2+4: Mapping brecha→servicio + WhatsApp conflict" \
    --archivos-mod "v4_proposal_generator.py" --tests "0"

# FASE-D
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-D --desc "V-2+V-3+A-1+CROSS-5: Labels, jargon, onboarding, confidence" \
    --archivos-mod "v4_proposal_generator.py,commercial_gate.py,propuesta_v6_template.md" --tests "0"

# FASE-E
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-E --desc "A-2+V-4/5/6+A-3+CROSS-6: AEO, paquete, typo, gate blocking" \
    --archivos-mod "v4_proposal_generator.py,propuesta_v6_template.md,publication_gates.py" --tests "0"

# FASE-F (sin log_phase — es ejecución, no código)
```

**Criterios de aceptación**:
- [ ] 5 fases registradas (A-E, F no lleva log por ser ejecución)
- [ ] Sin errores en `log_phase_completion.py`

### Tarea 2: Version bump con `sync_versions.py`

**Comando**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/sync_versions.py --bump minor --release-name "PROPUESTA-COMERCIAL"
```

**Criterios de aceptación**:
- [ ] VERSION.yaml actualizado a 4.53.0
- [ ] AGENTS.md actualizado con nueva versión
- [ ] README.md actualizado (si aplica)

### Tarea 3: Actualizar CHANGELOG.md

**Agregar entrada**:

```markdown
## [4.53.0] — PROPUESTA-COMERCIAL (2026-05-26)

### Arreglado
- **BREAKING**: Unificadas todas las variables financieras del template de propuesta sobre `effective_monthly_gain` (CODE-1/3/4)
- Gate CG-ROI-NEGATIVE sincronizado con tabla ROI (CODE-2)
- Puente dual fuga bruta/recuperación efectiva en diagnóstico y propuesta (CROSS-1)
- Mapping brecha→servicio con trazabilidad en tabla de propuesta (CROSS-2)
- Indicador de WhatsApp refleja conflicto real detectado (CROSS-4)
- Labels de estado unificados: "⚠️ En preparación" → "En proceso de activación — Semana 2" (V-2)
- Gate CG-TECH-JARGON expandido con 8 nuevos términos (V-3)
- Tabla de costos IAO movida a anexo técnico (V-3)
- Eliminado fallback frágil de búsqueda de string en `has_onboarding` (A-1)
- Confidence score visible en tabla de servicios de propuesta (CROSS-5)
- Umbral AEO unificado a 30 en ambas tablas (A-2)
- Cupo limitado justificado con número (V-4)
- Garantía incluye mecanismo de tracking propio Día 7 (V-5)
- Placeholder de prueba social agregado al template (V-6)
- Typo "PASSO" → "PASO" corregido (A-3)
- Gates NOT_READY ahora bloquean generación de documentos cliente (CROSS-6)
```

**Criterios de aceptación**:
- [ ] CHANGELOG.md actualizado con entrada 4.53.0
- [ ] Todas las fases referenciadas

### Tarea 4: Actualizar GUIA_TECNICA.md (si aplica)

**Verificar si hay cambios de API/pipeline**:
- CROSS-6 (gate blocking) es un cambio de comportamiento del pipeline → documentar
- Nuevos placeholders en templates → documentar

**Criterios de aceptación**:
- [ ] GUIA_TECNICA.md actualizado si hubo cambios de API
- [ ] Si no hubo cambios de API, marcar como "Sin cambios de API pública"

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar FASE-RELEASE como ✅ Completada
2. **`06-checklist-implementacion.md`**: Marcar items R1-R4 como ✅
3. **`09-documentacion-post-proyecto.md`**: Sección E — marcar todos los archivos como ✅
4. **`README.md` del plan**: Actualizar target release si es necesario

---

## Criterios de Completitud (CHECKLIST)

- [ ] `log_phase_completion.py` ejecutado para fases A-E
- [ ] `sync_versions.py` ejecutado → v4.53.0
- [ ] CHANGELOG.md actualizado con entrada PROPUESTA-COMERCIAL
- [ ] GUIA_TECNICA.md verificado/actualizado
- [ ] `dependencias-fases.md` — RELEASE ✅
- [ ] `06-checklist-implementacion.md` — todos los items ✅
- [ ] `09-documentacion-post-proyecto.md` — archivos del plan ✅

---

## Restricciones

- NO modificar código — solo documentación
- NO ejecutar v4complete
- NO modificar tests
- El version bump es `minor` (4.52.x → 4.53.0) porque hay cambios de comportamiento (CROSS-6 gate blocking)
- Máximo 60 iteraciones de agente
