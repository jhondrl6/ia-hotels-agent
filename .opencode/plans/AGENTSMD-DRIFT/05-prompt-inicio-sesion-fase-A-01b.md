# 05-prompt-inicio-sesion-fase-A-01b

**Fase:** A-01b — validate_agents_md.py + integración (Solución 2+4)
**Plan:** AGENTSMD-DRIFT
**Sesión:** Nueva (fresh)
**Iteraciones máx:** 60
**Depende de:** FASE-A-01a ✅
**Bloquea a:** FASE-A-01c

## Objetivo

Crear `scripts/validate_agents_md.py` — un script de validación automática que audita AGENTS.md contra código vivo y ROADMAP.md. Luego integrarlo en `docs/CONTRIBUTING.md` como paso obligatorio del flujo post-fase.

## Contexto de Fases Anteriores

**FASE-A-01a completada:** AGENTS.md corregido con 9 pasos editoriales. Conteo de tests: 2,743. Gates: 11. Módulos FASE-0: listados. evidence_ledger: marcado DEPRECADO. Árbol data_validation: refleja estructura real. AGENTS.md ahora es fuente confiable para que este script valide contra él.

**Problema que resolvemos:** El drift de AGENTS.md ocurrió porque `version-sync` actualiza el header pero no audita el body. Sin un gate automático, el drift volverá a ocurrir en futuras fases. La Solución 2 crea el gate; la Solución 4 lo integra al flujo obligatorio.

## Tareas

### T1: Investigar estructura de publication_gates.py y AGENTS.md

Cargar `modules/quality_gates/publication_gates.py` y entender:
- Dónde se define `self.gates` (L157-169)
- Cómo extraer programáticamente el número de gates y sus nombres

Cargar `AGENTS.md` (ya corregido por A-01a) y mapear:
- Dónde se declaran los conteos de tests (L123, L365, L380, L457)
- Dónde se declara el número de gates (L198)
- Dónde se listan los módulos FASE-0 (§Módulos Activos)
- Dónde se referencia evidence_ledger
- Dónde se listan scripts de validación (L28-31, L113)

Cargar `ROADMAP.md` L321-341 (FASE-0) y L304-311 (tabla gates) para entender qué módulos deben aparecer.

### T2: Crear scripts/validate_agents_md.py

Crear el script con 6 checks obligatorios. Estructura:

```python
#!/usr/bin/env python3
"""validate_agents_md.py — Audit AGENTS.md contra código vivo + ROADMAP.md

Uso: python scripts/validate_agents_md.py [--fix]
Salida: JSON con resultados + exit code (0=PASS, 1=FAIL)
"""

import os, re, json, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

def check_1_modules_exist():
    """Checks que módulos citados en AGENTS.md existen en las rutas especificadas.
    Escanea AGENTS.md en busca de paths tipo `modules/...` y verifica con os.path.exists."""
    ...

def check_2_test_count():
    """Conteo de tests: pytest --collect-only -q vs AGENTS.md (tolerancia ±5%).
    Extrae el número de AGENTS.md (ej: '2,743 funciones') y lo compara con pytest real."""
    ...

def check_3_gate_count():
    """Conteo de gates: len(self.gates) en publication_gates.py vs AGENTS.md.
    Extrae '11 publication gates' de AGENTS.md y compara con len() del dict."""
    ...

def check_4_fase0_modules():
    """Componentes FASE-0 listados en ROADMAP.md aparecen en AGENTS.md §Módulos.
    Verifica pain_ledger, delivery_quality_report, human_checklist, data_derivation_layer."""
    ...

def check_5_no_deprecated_active():
    """Módulos en archives/deprecated_* NO aparecen como activos en AGENTS.md.
    Escanea archives/ y verifica que AGENTS.md los marca como DEPRECADO."""
    ...

def check_6_scripts_exist():
    """Scripts referenciados en AGENTS.md §Validaciones existen en scripts/."""
    ...

def main():
    results = {
        "modules_exist": check_1_modules_exist(),
        "test_count": check_2_test_count(),
        "gate_count": check_3_gate_count(),
        "fase0_modules": check_4_fase0_modules(),
        "no_deprecated_active": check_5_no_deprecated_active(),
        "scripts_exist": check_6_scripts_exist(),
    }
    passed = all(r.get("status") == "PASS" for r in results.values())
    print(json.dumps(results, indent=2, ensure_ascii=False))
    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
```

**Implementación detallada de cada check:**

**Check 1 — modules_exist:**
- Escanear AGENTS.md con regex: `` `([a-z_/]+\.py)` `` (backtick-wrapped paths)
- Para cada match, resolver contra BASE y verificar `os.path.exists()`
- Ignorar paths con `[DEPRECADO]`
- Reportar PASS si todos existen, FAIL con lista de ausentes

**Check 2 — test_count:**
- Ejecutar `subprocess.run([sys.executable, '-m', 'pytest', '--collect-only', '-q'], capture_output=True, cwd=BASE)`
- Parsear "XXXX tests collected" del stderr/stdout
- Extraer número de AGENTS.md: buscar patrón `(\d{1,3}(?:,\d{3})*) funciones` o `(\d+) funciones`
- Comparar con tolerancia ±5%
- Si pytest falla, reportar SKIP (no FAIL — puede ser entorno)

**Check 3 — gate_count:**
- Leer `modules/quality_gates/publication_gates.py`
- Encontrar el bloque `self.gates: Dict[str, Callable] = {` ... `}`
- Contar entradas del dict
- Extraer "N publication gates" de AGENTS.md
- Comparar exacto (no tolerancia — los gates no cambian sin querer)

**Check 4 — fase0_modules:**
- Lista hardcodeada de módulos FASE-0: `['pain_ledger', 'delivery_quality_report', 'human_checklist', 'data_derivation_layer']`
- Verificar que cada uno aparece en AGENTS.md (case-insensitive)
- También verificar en ROADMAP.md L321-341 que sigan listados

**Check 5 — no_deprecated_active:**
- Listar archivos .py en `archives/deprecated_modules_*/`
- Para cada uno, verificar que AGENTS.md NO lo lista como activo (sin `[DEPRECADO]`)
- Si aparece sin `[DEPRECADO]`, FAIL

**Check 6 — scripts_exist:**
- Escanear AGENTS.md en busca de `` `scripts/...` ``
- Verificar existencia con `os.path.exists()`
- Reportar PASS si todos existen

### T3: Test manual del script

1. Ejecutar el script contra el AGENTS.md recién corregido:
   ```bash
   cd /mnt/c/Users/Jhond/Github/iah-cli
   ./venv/Scripts/python.exe scripts/validate_agents_md.py
   ```
   Esperado: 6/6 PASS, exit code 0.

2. Probar que detecta drift: temporalmente cambiar "11 publication gates" → "9 publication gates" en AGENTS.md, ejecutar script, verificar que check_3 reporta FAIL. Luego revertir.

3. Probar tolerancia ±5%: verificar que con 2,743 vs 2,700 (1.6% diff) da PASS, y con 2,743 vs 2,200 (19.8% diff) da FAIL.

### T4: Integrar en docs/CONTRIBUTING.md

Localizar `docs/CONTRIBUTING.md` §Flujo Post-Fase (aproximadamente L39-52). Insertar `validate_agents_md.py` como paso obligatorio entre Paso 5 y Paso 6 del flujo post-fase:

```markdown
### Paso 5.5: Validar AGENTS.md (OBLIGATORIO)

Ejecutar el validador de coherencia de AGENTS.md:

```bash
./venv/Scripts/python.exe scripts/validate_agents_md.py
```

Si el script reporta FAIL, corregir AGENTS.md **antes** de continuar.
Este paso previene el drift documental detectado en FASE-A-01.
```

Ejecutar log_phase_completion.py:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-A-01b \
    --desc "validate_agents_md.py: 6 checks automáticos (modules, tests, gates, FASE-0, deprecated, scripts) + integración en CONTRIBUTING.md §Post-Fase" \
    --archivos-nuevos "scripts/validate_agents_md.py" \
    --archivos-mod "docs/CONTRIBUTING.md" \
    --tests "0" \
    --check-manual-docs
```

Actualizar `09-documentacion-post-proyecto.md`:
- Sección A: `validate_agents_md | scripts/validate_agents_md.py | Script de 6 checks que audita AGENTS.md contra código vivo | FASE-A-01b`
- Sección E: `docs/CONTRIBUTING.md | Agregado Paso 5.5: validate_agents_md.py en flujo post-fase | FASE-A-01b`

## Criterios de Completitud

- [x] `scripts/validate_agents_md.py` existe y es ejecutable
- [x] Los 6 checks están implementados y documentados
- [ ] El script da 6/6 PASS contra AGENTS.md corregido (exit code 0) — **4/6 PASS: 2 FAIL por drift residual en AGENTS.md**
- [x] El script detecta drift cuando se introduce artificialmente (verificado: 11→9 gates → FAIL)
- [x] `docs/CONTRIBUTING.md` incluye Paso 5.5 con validate_agents_md.py
- [x] log_phase_completion.py ejecutado exitosamente
- [x] 09-documentacion-post-proyecto.md actualizado
- [x] dependencias-fases.md, 06-checklist, README.md actualizados

## Restricciones

- Máximo 60 iteraciones
- **NO modificar AGENTS.md** (ya fue corregido en A-01a)
- **NO modificar publication_gates.py ni ROADMAP.md**
- **NO ejecutar v4complete ni v4audit**
- **NO modificar CHANGELOG.md ni GUIA_TECNICA.md** (eso es FASE-RELEASE)
