# Prompt de Inicio de Sesión: FASE-TRAZABILIDAD-DOCS

**Proyecto**: Corrección Trazabilidad "Calidad Garantizada"  
**Fase**: 1 de 3 — Correcciones Documentales  
**Sesión**: Nueva (1 fase por sesión)

---

## Contexto

### Origen
Auditoría `.opencode/context/auditoria_calidad_garantizada_20260424.md` detectó 4 desconexiones entre el bloque "Calidad Garantizada" del README (líneas 299-307) y la realidad del código. Análisis profundizado en sesión de preparación confirmó y amplió los hallazgos:

### Hallazgos Confirmados
1. **README dice "6 Publication Gates"** → Código tiene 9 (3 adicionales son WARNING/no-bloqueantes)
2. **Workflow `v4_complete.md` paso 9** → Referencia `v4_coherence_validator`, comando que NO existe (fue mergeado en `v4_quality_validator.md` según CHANGELOG)
3. **PublicationGatesOrchestrator docstring** → Dice "5 critical gates" cuando `self.gates` tiene 9 entradas
4. **AGENTS.md** → Coherence Score dice 0.84, la ejecución más reciente muestra 0.89

### NOTA: El análisis original decía que CoherenceValidator "no se ejecuta" — esto es INCORRECTO. v4complete SÍ llama a CoherenceValidator (main.py L2181). Lo que NO se ejecuta es PublicationGatesOrchestrator con sus 9 gates.

## Tareas Específicas

### T1: Corregir README.md línea 306
- Cambiar "6 Publication Gates" → "9 Publication Gates (6 blocking + 3 advisory: content_quality, asset_confidence, proposal_asset_alignment)"
- Agregar descripción breve de los 3 gates advisory

### T2: Corregir `.agents/workflows/v4_complete.md` paso 9
- Reemplazar línea 95: `v4_coherence_validator --url {{url}}`
- Por: `CoherenceValidator.validate()` (describir la invocación real que se ejecuta en main.py)
- O alternativamente: remover el paso 9 y documentar que la validación de coherencia ocurre inline en el handler de v4complete

### T3: Corregir docstring de PublicationGatesOrchestrator
- Archivo: `modules/quality_gates/publication_gates.py`
- Líneas 5-13: Cambiar "5 critical gates" → "9 publication gates (6 blocking + 3 advisory)"
- Agregar gates 6-9 en la lista del docstring

### T4: Actualizar AGENTS.md
- Sincronizar Coherence Score con el último valor real (o añadir nota de que varía por ejecución)
- Actualizar conteo de tests si es necesario

## Criterios de Completitud

- [ ] README.md L306 muestra "9 Publication Gates"
- [ ] v4_complete.md no referencia `v4_coherence_validator`
- [ ] publication_gates.py docstring refleja 9 gates reales
- [ ] AGENTS.md actualizado

## Post-Ejecución

```bash
# 1. Registrar fase
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-TRAZABILIDAD-DOCS \
    --desc "Corrección documental: 6→9 gates, workflow v4_coherence_validator, docstring PublicationGatesOrchestrator" \
    --archivos-mod "README.md,.agents/workflows/v4_complete.md,modules/quality_gates/publication_gates.py,AGENTS.md" \
    --tests "0" \
    --check-manual-docs

# 2. Verificar cambios
git diff --stat
```

## Archivos Involucrados

| Archivo | Tipo | Cambio |
|---------|------|--------|
| `README.md:306` | Modificar | "6" → "9" |
| `.agents/workflows/v4_complete.md:95` | Modificar | Remover comando inexistente |
| `modules/quality_gates/publication_gates.py:5-13` | Modificar | Docstring 5→9 |
| `AGENTS.md` | Modificar | Sincronizar coherence score |
