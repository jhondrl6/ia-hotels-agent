# 05-prompt-inicio-sesion-fase-RELEASE-4.39.0.md

> **FASE:** FASE-RELEASE-4.39.0
> **Objetivo:** Release 4.39.0 — Scoring Transparency
> **Contexto previo:** FASE-SCORING-1 ✅, FASE-SCORING-2 ✅, FASE-SCORING-3 ✅ completadas
> **Estado:** ✅ COMPLETADA (2026-05-02)

---

## NOTA PREVIA

Este es el flujo RELEASE según `phased_project_executor.md §7` + `CONTRIBUTING.md §55-163`.  
**NO modifica código fuente.** Solo documentación y validaciones.

---

## TAREAS (E1-E8)

### E1. Diagnóstico Inicial

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/version_consistency_checker.py
./venv/Scripts/python.exe main.py --doctor
```

- [ ] version_consistency_checker.py pasa sin discrepancias
- [ ] doctor no reporta errores críticos

### E2. Sincronización Automática

```bash
./venv/Scripts/python.exe scripts/sync_versions.py
```

- [ ] sync_versions.py ejecutado sin errores

### E3. CHANGELOG.md

Formato según `docs/contributing/documentation_rules.md §36-58`:

```markdown
## [4.39.0] - Scoring Transparency (2026-05-XX)

### Objetivo
Agregar transparencia al scoring GEO/AEO/SEO/IAO: breakdown visible, sección "Este score NO mide", y documento scoring_methodology.md linkado.

### Cambios Implementados
- `modules/commercial_documents/v4_diagnostic_generator.py` - Agregadas funciones `_build_scoring_breakdown()` y `_build_excluded_factors_section()`
- `modules/commercial_documents/templates/diagnostico_v6_template.md` - Actualizado frontmatter y template con nuevas variables de transparencia

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `docs/scoring_methodology.md` | Metodología completa de scoring con breakdown por pilar y factores excluidos |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | +2 funciones de transparencia, +3 template vars |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | Frontmatter + breakdown + sección metodología |

### Tests
- Tests existentes en `tests/commercial_documents/` pasan sin regresiones
```

- [ ] CHANGELOG.md tiene entrada `[4.39.0]`
- [ ] Entrada describe archivos nuevos y modificados
- [ ] No hay entradas duplicadas

### E4. GUIA_TECNICA.md

Agregar sección "Notas de Cambios v4.39.0":

```markdown
## Notas de Cambios v4.39.0 — Scoring Transparency

**Fecha:** 2026-05-XX
**Tipo:** Feature (no breaking change)

### Módulos afectados
- `modules/commercial_documents/v4_diagnostic_generator.py`
- `modules/commercial_documents/templates/diagnostico_v6_template.md`

### Problema
El scoring GEO/AEO/SEO/IAO no era transparente sobre qué factores mide y cuáles excluye. Un hotel con 203 reviews y respuesta <24h podía bajar su score por fotos faltantes — el owner no entendía por qué.

### Solución
- Agregada función `_build_scoring_breakdown()` que muestra breakdown por pilar: "GEO 62/100 = Fotos(15%) + NAP(15%) + ..."
- Agregada función `_build_excluded_factors_section()` que lista factores NO medidos por pilar
- Template actualizado para mostrar breakdown debajo de tabla de scores y sección "Este score NO mide"
- Nuevo documento `docs/scoring_methodology.md` con metodología completa linkado desde frontmatter

### Backwards Compatibility
✅ Compatible hacia atrás. No cambia la lógica de cálculo de scores. Solo agrega transparencia al output.

### Tests
- Tests existentes en `tests/commercial_documents/` sin regresiones
```

- [ ] GUIA_TECNICA.md tiene nota técnica para v4.39.0
- [ ] Nota incluye módulos, problema, solución, backwards compatibility

### E5. Skills/Workflows

```bash
ls -la .agents/workflows/*.md
```

- [ ] Todos los .md en `.agents/workflows/` listados en `.agents/workflows/README.md`
- [ ] No hay skills huérfanos

### E6. Regenerar SYSTEM_STATUS.md

```bash
./venv/Scripts/python.exe scripts/doctor.py --status
```

- [ ] SYSTEM_STATUS.md regenerado con versión 4.39.0

### E7. Verificar DOMAIN_PRIMER.md

```bash
./venv/Scripts/python.exe scripts/doctor.py --context
```

- [ ] Todos los módulos documentados
- [ ] Referencias en DOMAIN_PRIMER existen en disco

### E8. Symlink + Validación Final

```bash
ls -la .agent/workflows
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
git diff --stat
```

- [ ] Symlink `.agent/workflows` → `.agents/workflows` intacto
- [ ] run_all_validations.py --quick pasa (4/4)
- [ ] git diff --stat muestra todos los archivos modificados

### E9. git commit

```bash
git add -A && git commit -m "feat: scoring transparency — breakdown visible + excluded factors + methodology doc (v4.39.0)"
```

- [ ] Commit realizado con mensaje descriptivo

---

## RESTRICCIONES

- NO modificar código fuente
- NO ejecutar v4complete
- Máximo 60 iteraciones

---

## CHECKLIST FINAL

- [ ] E1: version_consistency_checker.py pasa
- [ ] E1: doctor sin errores críticos
- [ ] E2: sync_versions.py sin errores
- [ ] E3: CHANGELOG.md [4.39.0] existe y con formato correcto
- [ ] E4: GUIA_TECNICA.md nota v4.39.0 presente
- [ ] E5: workflows/README.md actualizado
- [ ] E6: SYSTEM_STATUS.md regenerado
- [ ] E7: DOMAIN_PRIMER verificado
- [ ] E8: run_all_validations.py --quick pasa 4/4
- [ ] E8: git diff muestra archivos correctos
- [ ] E9: git commit realizado
