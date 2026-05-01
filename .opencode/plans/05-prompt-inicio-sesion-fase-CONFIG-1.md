# FASE-CONFIG-1: Corrección Bug sync_versions (CR-1, CR-2, CR-3)

**Plan:** FEATURE-CONFIG-EXTRACTION v1.0.0
**Workflow:** `.agents/workflows/phased_project_executor.md` v2.9.0
**Presupuesto:** 60 iteraciones max | **Estimado esta fase:** ~40 iteraciones
**Dependencias:** Ninguna (primera fase)
**Fase siguiente:** FASE-CONFIG-2

---

## Contexto

**Fuente:** `.opencode/context/TECHNICAL_DEBT_2026-04-29.md` §HALLAZGO 1 (líneas 30-105)

### Problema

`scripts/sync_versions.py --check` reporta "All files in sync" pero la regla `guia_tecnica_header` NUNCA actualiza `GUIA_TECNICA.md`. Falso positivo porque el pattern regex no matchea.

### Causas Raíz a Corregir

#### CR-1: Doble escape YAML en sync_config.yaml (L101-103)
Los patterns usan `\\\\*\\\\*` (doble escape). YAML lo parsea como `\\*\\*` literal en vez de `\*\*` (regex escaped star). Resultado: regex nunca matchea `**Versión:**`.

**Fix:** Cambiar `\\\\*\\\\*` → `\\*\\*` en las 2 reglas de `guia_tecnica_header`.

#### CR-2: Ausencia de validación post-reemplazo (L131-133)
`sync_versions.py` asume "in sync" si `_apply_replacements` retorna `changed=False`. Pero un pattern roto siempre retorna `changed=False` → falso positivo.

**Fix:** Tras `re.sub`, verificar que el valor interpolado existe en el contenido.

#### CR-3: Inconsistencia "v" en template de GUIA_TECNICA
- Template inserta `4.37.0` SIN "v"
- Archivo real tiene `v4.37.0` CON "v"
- Pattern busca `[\\d]+\\.[\\d]+\\.[\\d]+` SIN `v?`

**Fix:** Agregar `v?` al pattern y `v{version}` al template.

---

## Tareas Específicas

### Tarea 1: Investigar y confirmar estado actual
- Leer `scripts/sync_config.yaml` L95-110 (confirmar doble escape)
- Leer `scripts/sync_versions.py` L120-145 (entender flujo `_apply_replacements`)
- Leer `docs/GUIA_TECNICA.md` L3 (confirmar formato con "v")
- Leer `docs/CONTRIBUTING.md` L4 (confirmar formato con "v" — este SÍ funciona)

### Tarea 2: Corregir doble escape + inconsistencia "v"
- **sync_config.yaml L101-103:** Cambiar `\\\\*\\\\*` → `\\*\\*` en ambos patterns
- **sync_config.yaml L103:** Cambiar pattern de `[\\d]+\\.[\\d]+\\.[\\d]+` → `v?[\\d]+\\.[\\d]+\\.[\\d]+`
- **sync_config.yaml L103:** Cambiar template de `{version} ({codename})` → `v{version} ({codename})`
- Verificar con `grep` que las otras 6 reglas usan escape simple (no tocar)

### Tarea 3: Agregar validación post-reemplazo
- **sync_versions.py L131-133:** Después de `re.sub`, agregar verificación:
  ```python
  # Verificar que el valor interpolado existe post-reemplazo
  expected = template.format(version=self.version, ...)
  if expected not in new_content:
      self.results[rule_id] = "PATTERN_MISMATCH"
      print(f"WARN: {rule['file']} ({rule_id}) - pattern matched but value not found")
      return False
  ```
- Asegurar que el warning sea visible en output de `--check`

### Tarea 4: Test de integración con VERSION.yaml dummy
- Cambiar `VERSION.yaml` → version: "99.99.99", codename: "TEST"
- Ejecutar: `venv/Scripts/python.exe scripts/sync_versions.py`
- Verificar que los 6 archivos se actualizan a 99.99.99:
  - AGENTS.md, README.md, .cursorrules, CONTRIBUTING.md, GUIA_TECNICA.md, REGISTRY.md
- Ejecutar: `venv/Scripts/python.exe scripts/sync_versions.py --check`
- Debe reportar "All files in sync" (ahora REAL, no falso positivo)
- Restaurar VERSION.yaml a 4.37.0
- Ejecutar sync nuevamente para restaurar archivos

---

## Archivos Involucrados

| Archivo | Tipo de Cambio | Líneas |
|---------|---------------|--------|
| `scripts/sync_config.yaml` | MODIFICAR (2 patterns) | L101-103 |
| `scripts/sync_versions.py` | MODIFICAR (agregar validación) | L131-133 |
| `VERSION.yaml` | TEMPORAL (test, restaurar después) | — |
| `docs/GUIA_TECNICA.md` | VERIFICAR (test) | L3 |

---

## Criterios de Completitud

- [ ] CR-1: Doble escape corregido en sync_config.yaml (2 reglas)
- [ ] CR-3: "v" consistente entre pattern, template y archivo real
- [ ] CR-2: Validación post-reemplazo agregada en sync_versions.py
- [ ] Test dummy VERSION 99.99.99 → sync propaga a 6 archivos
- [ ] Test dummy VERSION → --check reporta "All in sync" (real)
- [ ] Restaurado VERSION.yaml a 4.37.0 + sync ejecutado
- [ ] No se tocaron las otras 6 reglas de sync_config.yaml
- [ ] No se tocaron archivos fuera del scope

---

## Restricciones

- **NO modificar** ROADMAP.md
- **NO ejecutar** v4complete o v4audit
- **NO modificar** archivos de módulos (`modules/`)
- **NO crear** archivos YAML de configuración nuevos
- **Máximo 60 iteraciones del agente** (R2)
- Si se alcanza el límite → marcar INCOMPLETA, guardar progreso

---

## Post-Ejecución (OBLIGATORIO)

Al finalizar (completada o incompleta):

### 1. Guardar evidencia
```bash
mkdir -p evidence/fase-config-1
cp scripts/sync_config.yaml evidence/fase-config-1/
cp scripts/sync_versions.py evidence/fase-config-1/
```

### 2. Actualizar checklist
Marcar items completados en `06-checklist-implementacion.md`

### 3. Ejecutar log_phase_completion.py
```bash
venv/Scripts/python.exe scripts/log_phase_completion.py     --fase FASE-CONFIG-1     --desc "Corrección bug sync_versions: doble escape YAML + validación post-reemplazo + consistencia v"     --archivos-mod "scripts/sync_config.yaml,scripts/sync_versions.py"     --tests "3"     --check-manual-docs
```

### 4. Para iniciar la siguiente fase
```
Carga y ejecuta .opencode/plans/05-prompt-inicio-sesion-fase-CONFIG-2.md siguiendo .agents/workflows/phased_project_executor.md
```
