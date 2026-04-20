# FASE-3: Activar Content Scrubber en Pipeline (código muerto → integrar)
**Proyecto**: Amaziliahotel E2E Refactor v2
**Anterior**: Ninguna (FASE-3 es independiente — NO depende de FASE-1)
**Siguiente**: Cualquiera

---

## Contexto

**NG1 (CRÍTICO)**: Publication gate bloqueado por "COP COP" en propuesta.

**NG5 (CRÍTICO)**: Content Scrubber NUNCA se ha ejecutado en el pipeline.

**Hallazgo post-forense (crítico)**: `ContentScrubber` es **código muerto**:
- Archivo real: `modules/postprocessors/content_scrubber.py` (NO `modules/content_scrubber.py`)
- La clase `ContentScrubber` con método `.scrub()` existe y tiene lógica de limpieza
- PERO: **0 imports en todo el codebase**. Nunca es importado ni invocado por ningún módulo.
- No aplica a diagnóstico NI a propuesta. El problema no es "scope dual" sino que simplemente no se usa.

**Esto explica**: "COP COP" aparece en ambos documentos porque NADIE lo limpia.

---

## Tareas de la Fase

### 1. Confirmar estado del scrubber

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Verificar que el archivo existe en postprocessors/
cat modules/postprocessors/content_scrubber.py | head -50

# Confirmar 0 imports (debe retornar vacío)
grep -rn "ContentScrubber\|content_scrubber\|\.scrub(" \
    modules/ --include="*.py" | grep -v "postprocessors/content_scrubber.py" | grep -v __pycache__
```

### 2. Entender la API del ContentScrubber

```bash
# Ver qué hace, qué parámetros acepta
grep -n "def scrub\|def __init__\|class ContentScrubber\|doc_type\|patterns" \
    modules/postprocessors/content_scrubber.py
```

Revisar si `ContentScrubber.scrub()` acepta:
- `content` (string) o `filepath` (path a archivo)?
- `doc_type` (diagnóstico/propuesta)?
- Qué patrones limpia (COP COP, blanks, defaults)?

### 3. Integrar en el pipeline v4complete

El punto de integración es `modules/orchestration_v4/v4_complete_orchestrator.py`:

```bash
# Entender el flujo del orquestador
grep -n "def.*run\|def.*execute\|def.*generate\|diagnostico\|propuesta\|output" \
    modules/orchestration_v4/v4_complete_orchestrator.py | head -30
```

**Integración necesaria**:

```python
# En v4_complete_orchestrator.py, después de generar diagnóstico y propuesta:

from modules.postprocessors.content_scrubber import ContentScrubber

scrubber = ContentScrubber()

# Aplicar a diagnóstico
diagnostico_path = outputs_dir / "diagnostico.md"
if diagnostico_path.exists():
    content = diagnostico_path.read_text(encoding="utf-8")
    cleaned = scrubber.scrub(content, doc_type="diagnostico")
    diagnostico_path.write_text(cleaned, encoding="utf-8")

# Aplicar a propuesta
propuesta_path = outputs_dir / "propuesta.md"
if propuesta_path.exists():
    content = propuesta_path.read_text(encoding="utf-8")
    cleaned = scrubber.scrub(content, doc_type="propuesta")
    propuesta_path.write_text(cleaned, encoding="utf-8")
```

**Ubicación exacta**: Buscar dónde se escribe el archivo de propuesta/diagnóstico y agregar el scrub INMEDIATAMENTE DESPUÉS.

### 4. Verificar que el scrubber tiene las reglas necesarias

El scrubber debe limpiar:
- `COP COP` → `COP` (moneda duplicada)
- `_____` (blanks de templates) → "Por confirmar" o eliminar
- Valores por defecto en dinero

Si falta alguna regla, agregarla al scrubber.

### 5. Verificar fix

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Ejecutar v4complete y verificar que el scrubber se invoca
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/ 2>&1 | grep -i "scrub\|clean\|COP"

# Verificar que NO hay COP COP en ningún output
grep -r "COP COP" outputs/amaziliahotel.com/ 2>/dev/null || echo "OK: No hay COP COP"

# Verificar publication_ready
grep -r "publication_ready\|NOT_READY" outputs/amaziliahotel.com/ 2>/dev/null
```

---

## Post-Ejecución

### Checklist de completitud

- [ ] `ContentScrubber` importado en `v4_complete_orchestrator.py`
- [ ] Scrubber invocado DESPUÉS de escribir diagnóstico
- [ ] Scrubber invocado DESPUÉS de escribir propuesta
- [ ] "COP COP" = 0 en diagnóstico
- [ ] "COP COP" = 0 en propuesta
- [ ] "_____" blanks reducidos en propuesta
- [ ] publication_ready = true
- [ ] Tests pasando: `pytest tests/ -k "scrubber" -v`

### Actualizar estado

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-3 \
    --desc "Activar Content Scrubber — integrar código muerto en pipeline v4complete (diagnóstico + propuesta)" \
    --archivos-mod "modules/postprocessors/content_scrubber.py,modules/orchestration_v4/v4_complete_orchestrator.py" \
    --tests "4" \
    --check-manual-docs
```

---

## Criterios de Aprobación

| Criterio | Estado |
|----------|--------|
| ContentScrubber importado en orquestador | [ ] |
| "COP COP" = 0 en diagnóstico | [ ] |
| "COP COP" = 0 en propuesta | [ ] |
| publication_ready = true | [ ] |
| Tests pasando | [ ] |
