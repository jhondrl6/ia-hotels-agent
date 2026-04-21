# Prompt de Inicio de Sesion — FASE-PATCH-2
## Fix Scrubber Timing — Re-scrub Proposal Post-Generation (Persistencia G14)

**Fecha**: 2026-04-20
**Tipo**: PATCH (fix de persistencia, NO re-escribir FASE-3)
**Depende de**: FASE-1 a FASE-8 completadas
**Bloquea**: FASE-RELEASE

---

## Contexto

FASE-3 importó ContentScrubber en main.py pero el E2E sigue mostrando:
- 5x "COP COP" en proposal (líneas 30, 40, 105, 106, 107)
- Log: `[SKIP] Proposal document not available for scrubbing`

**Causa raíz confirmada** (ROOT_CAUSE_ANALYSIS.md):
- `main.py:2274` — `proposal_path = None` (inicialización)
- `main.py:2277-2346` — FASE 3.6 ejecuta scrubber, pero `proposal_path` sigue siendo None → SKIP
- `main.py:2463-2476` — La propuesta se genera ~150 líneas DESPUÉS del scrubber

El scrubber se ejecuta ANTES de que exista el archivo de propuesta. FIX-D7 movió la generación de propuesta después de los assets, pero el scrubber no se movió.

---

## Objetivo

Que la propuesta entregada al cliente tenga 0 ocurrencias de "COP COP".

---

## Tareas

### T1: Agregar re-scrub post-generación de propuesta

**Archivo**: `main.py`
**Ubicación**: Inmediatamente después de la línea donde se asigna `proposal_path` (~L2476)

Buscar la línea exacta:
```python
proposal_path = proposal_gen.generate(...)
```

Insertar DESPUÉS de esa asignación:
```python
# FIX-PATCH-2: Re-scrub proposal now that it exists
# Creamos scrubber fresco — NO dependemos del del try block (L2307)
from modules.postprocessors.content_scrubber import ContentScrubber
from pathlib import Path
postscrubber = ContentScrubber()
if proposal_path and Path(proposal_path).exists():
    try:
        with open(proposal_path, 'r', encoding='utf-8') as f:
            prop_content = f.read()
        prop_scrub = postscrubber.scrub(prop_content, hotel_data, "propuesta")
        if prop_scrub.fix_count > 0:
            print(f"   [SCRUB] Proposal (post-gen): {prop_scrub.fix_count} fix(es) applied")
            with open(proposal_path, 'w', encoding='utf-8') as f:
                f.write(prop_scrub.scrubbed)
    except Exception as e:
        print(f"   [WARN] Post-gen scrub failed: {e}")
```

NOTA: La variable `scrubber` se crea en L2307 DENTRO del try block (L2281-2381). Python try/except NO crea scope — si el try completa sin excepción, `scrubber` SÍ es accesible en L2476. SIN embargo, si una excepción ocurre entre L2281 y L2307, `scrubber` no existiría. Para robustez, se re-crea explícitamente en el re-scrub.

**Defecto original**: El plan decía "la variable scrubber ya existe en scope" como si fuera un guarantee absoluto. En realidad es condicional: existe solo si el try block (L2281-2381) completó sin excepción antes de L2307. El fix defensivo re-crea el scrubber para no depender de este supuesto.

---

## Verificación

### V1: Tests de regresión
```bash
./venv/Scripts/python.exe -m pytest tests/ -k "scrub" -v --tb=short
```

### V2: Grep verification
```bash
# Debe existir el bloque de re-scrub post-gen
grep 'Re-scrub proposal' main.py  # debe dar 1 match

# La variable postscrubber debe existir en el bloque re-scrub
grep -n 'postscrubber = ContentScrubber' main.py  # debe estar después de L2476
```

### V3: Syntax check
```bash
./venv/Scripts/python.exe -m py_compile main.py
```

---

## Restricciones

- NO ejecutar v4complete (eso es FASE-RELEASE)
- NO modificar v4_comprehensive.py (ya se arregló en FASE-PATCH-1)
- NO modificar conditional_generator.py (ya se arregló en FASE-PATCH-1)
- NO modificar v4_proposal_generator.py (eso es FASE-PATCH-3)
- SOLO tocar: `main.py` (1 bloque de código, ~10 líneas)

---

## Pitfalls conocidos

- `scrubber` del try block puede NO existir si el try falló antes de L2307. El fix crea `postscrubber` fresco para no depender de este supuesto.
- `Path` debe estar importado (`from pathlib import Path`). El bloque re-scrub importa explícitamente.
- El re-scrub NO debe duplicar fixes (ContentScrubber es idempotente).

---

## Criterios de Completitud

- [ ] Bloque de re-scrub post-generación agregado en main.py
- [ ] `postscrubber` está en scope (no depende del try block L2281-2381)
- [ ] `Path` está importado
- [ ] Tests de regresión pasan
- [ ] Syntax check pasa
- [ ] Grep verification confirma el bloque existe
