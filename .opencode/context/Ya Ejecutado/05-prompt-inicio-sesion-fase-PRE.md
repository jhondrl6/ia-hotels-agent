# Prompt de Inicio de Sesion: FASE-PRE

> **Fase**: PRE — Saneamiento y Preparacion  
> **Plan maestro**: `PLAN-REFACTOR-TERMALES-20260508.md`  
> **Iteraciones max**: 60  
> **Contexto previo**: Ninguno (primera fase)  

---

## Tareas de la Fase

TAREAS DE LA FASE:
  [x] Investigacion de codigo existente (contexto ya cargado en plan maestro)
  [ ] Verificar CHANGELOG vs VERSION.yaml drift
  [ ] Normalizar line endings (CRLF→LF) si aplica
  [ ] Ejecutar run_all_validations.py --quick
  [ ] Crear estructura de directorios evidence/{fase-id}/
  [ ] Preparar estado base para fases siguientes

CONTADOR:
  - Total tareas: 5
  - Comandos largos: 0
  - Estado: dentro del limite R3

---

## Instrucciones Detalladas

### 1. Verificar CHANGELOG vs VERSION.yaml drift

```bash
# Leer version actual
head -5 VERSION.yaml
grep -E "^## \[" CHANGELOG.md | head -5
```

- Si VERSION.yaml dice `4.42.0` y CHANGELOG no tiene entrada `## [4.42.0]`, reportar drift.
- No corregir aun — solo reportar en el checklist.

### 2. Normalizar line endings

```bash
# Detectar archivos con CRLF
find modules/ -type f -name "*.py" | xargs file | grep CRLF
```

- Si hay archivos con CRLF, convertir:
```bash
find modules/ -type f -name "*.py" | xargs sed -i 's/\r$//'
```
- Si no hay, marcar como "OK".

### 3. Ejecutar run_all_validations.py --quick

```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

- Capturar output completo.
- Si falla algun check, reportar cuales.
- No bloquear la fase — solo documentar.

### 4. Crear estructura evidence/

```bash
mkdir -p evidence/fase-PRE evidence/fase-1-A evidence/fase-1-B evidence/fase-2 evidence/fase-3
```

### 5. Preparar estado base

- Verificar que los archivos del plan maestro existen:
  - `.opencode/plans/PLAN-REFACTOR-TERMALES-20260508.md`
  - `.opencode/plans/06-checklist-implementacion.md`
  - `.opencode/plans/09-documentacion-post-proyecto.md`
- Si no existen, crear skeleton (el orquestador deberia haberlo hecho, pero verificar).

---

## Post-Ejecucion (al finalizar la sesion)

1. **Marcar checklist** en `.opencode/plans/06-checklist-implementacion.md`:
   - FASE-PRE: estado `COMPLETADA` o `INCOMPLETA`
   - Si incompleta: iteracion donde se agoto y que falta

2. **Ejecutar log_phase_completion.py**:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-PRE \
    --desc "Saneamiento: validaciones base, line endings, estructura evidence" \
    --check-manual-docs
```

3. **Actualizar 09-documentacion-post-proyecto.md** (Seccion D: metricas base):

```markdown
## Seccion D: Metricas Acumulativas
| Metrica | Valor | Fase |
|---------|-------|------|
| Validaciones pre-refactor | X/4 checks | FASE-PRE |
| Archivos CRLF normalizados | N | FASE-PRE |
```

4. **Guardar evidencia** (si hubo output de validaciones):
```bash
cp scripts/run_all_validations_output.log evidence/fase-PRE/ 2>/dev/null || true
```

---

## Criterios de Completitud

- [ ] `run_all_validations.py --quick` ejecutado (output capturado)
- [ ] Estructura `evidence/` creada para todas las fases
- [ ] Drift CHANGELOG/VERSION documentado en checklist
- [ ] Line endings normalizados (o confirmados OK)
- [ ] `log_phase_completion.py` ejecutado
- [ ] Checklist maestro actualizado

---

## Restricciones

- **NO implementar codigo de fix** — esta fase es solo saneamiento.
- **NO ejecutar v4complete** — reservado para FASE-2.
- **Max 60 iteraciones** — si se agota, guardar estado y marcar incompleta.
- **NO modificar ROADMAP.md**.

---

*Prompt generado por orquestador siguiendo phased_project_executor.md v2.10.0*
