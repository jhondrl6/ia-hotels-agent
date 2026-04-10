# Contribuir con la Documentacion Oficial

> Este archivo responde a **una sola pregunta**: como se actualiza la documentacion oficial del repositorio con suficiencia y claridad.
> **Version actual:** v4.26.0 | Consulta REGISTRY.md para el historial de fases completadas.

---

## Principio Central

Si quieres actualizar **cualquier documento** del repositorio, sigue este flujo:

```
1. Identifica QUE tipo de cambio estas haciendo (ver tabla abajo)
2. Ve al fragmento correspondiente en docs/contributing/
3. Sigue los pasos listados
4. Ejecuta validaciones antes del commit
5. Commit → la sincronizacion automatica actualiza VERSION en todos los archivos
```

---

## Tabla de Decision Rapida

| Si necesitas... | Ve a... | Que encuentras |
|------------------|---------|----------------|
| Cambiar version del proyecto | `docs/contributing/procedures.md` §1 | Editar VERSION.yaml → ejecutar sync_versions.py |
| Agregar o eliminar una skill | `docs/contributing/procedures.md` §2-§3 | Procedimiento paso a paso + archivos a tocar |
| Modificar Decision Engine | `docs/contributing/procedures.md` §4 | Regenerar DOMAIN_PRIMER |
| Agregar nuevo modulo Python | `docs/contributing/documentation_rules.md` §5 | Checklist de documentacion obligatoria |
| Hacer commit | `docs/contributing/validation.md` §6 | Pre-commit hooks + validaciones manuales |
| Agregar/modificar checks de coherencia | `docs/contributing/validation.md` §11 | Donde definir, implementar y testear |
|| Validar regresion | `docs/contributing/validation.md` §12 | Scripts de regresion + checklist pre-release |
|| Actualizar benchmarks regionales | `docs/contributing/procedures.md` §5 | Script update_benchmarks.py + research JSON |
|| Verificar capabilities nuevas | `docs/contributing/capabilities.md` §13 | Matriz de capacidades + gate de cierre |
| Gestionar evidencia | `docs/contributing/capabilities.md` §14 | Estructura del Evidence Ledger |

---

## Flujo Post-Fase Obligatorio

Cuando se completa una fase via `phased_project_executor.md`:

```
FASE completada
    │
    └── Paso 6: Documentacion Post-Fase
        ├── Lee docs/contributing/documentation_rules.md para checklist
        ├── Ejecuta: python scripts/log_phase_completion.py --fase N
        │   ├── Registra en docs/contributing/REGISTRY.md (auto)
        │   └── Muestra POR_HACER para docs manuales
        └── Verifica capability contracts en docs/contributing/capabilities.md
```

---

## Trigger del Usuario: "Actualizar documentacion oficial del repositorio"

**Cuando el usuario digita esta frase en el chat**, el agente **NO interpreta libremente**. Ejecuta este procedimiento obligatorio:

### Paso 1: Diagnositico inicial

```bash
# Verificar version actual (fuente de verdad)
python scripts/version_consistency_checker.py

# Verificar symlinks y ecosistema
python main.py --doctor
```

### Paso 2: Sincronizacion automatica de versiones

```bash
# Actualizar version y fecha en todos los headers
python scripts/sync_versions.py
```

Esto sincroniza VERSION.yaml → 6 archivos sin modificacion manual. Si hay discrepancia, el script la corrige.

### Paso 3: Verificar CHANGELOG.md (manual)

| Check | Accion si falla |
|-------|-----------------|
| CHANGELOG.md tiene entrada para la version actual de VERSION.yaml | Agregar entrada con formato definido en `docs/contributing/documentation_rules.md` §36-58 |
| CHANGELOG.md describe archivos nuevos/modificados de la ultima fase | Completar secciones: Objetivo, Cambios Implementados, Archivos Nuevos, Archivos Modificados, Tests |
| No hay entradas duplicadas en CHANGELOG | Eliminar duplicados |

### Paso 4: Verificar GUIA_TECNICA.md (manual)

| Check | Accion si falla |
|-------|-----------------|
| docs/GUIA_TECNICA.md tiene nota tecnica para la ultima fase | Agregar seccion "Notas de Cambios v{VERSION}" con: resumen, modulos afectados, arquitectura, backwards compatibility |
| La nota tecnica incluye los 3 escenarios probados (si aplica) | Documentar escenarios |
| La nota tecnica incluye archivos modificados con descripcion | Listar archivos y cambios |

### Paso 5: Verificar skills/workflows (manual)

```bash
# Listar skills actuales en .agents/workflows/
# Comparar con .agents/workflows/README.md
```

| Check | Accion si falla |
|-------|-----------------|
| Todos los archivos `.md` en `.agents/workflows/` estan listados en `README.md` | Regenerar `.agents/workflows/README.md` |
| Skills eliminados removidos del README | Remover entradas huérfanas |
| `python scripts/generate_system_status.py` se ejecuto | Ejecutarlo si no |

### Paso 6: Regenerar SYSTEM_STATUS.md

```bash
python main.py --doctor --status
```

### Paso 7: Verificar .agent/ vs .agents/ (symlink critico)

| Check | Accion si falla |
|-------|-----------------|
| `.agent/workflows/` es symlink que apunta a `.agents/workflows/` | Recrear: `ln -sf ../.agents/workflows .agent/workflows` |
| Doctor no reporta error de "Symlink integrity" | Ejecutar `python main.py --doctor` para diagnosticar |

### Paso 8: Validacion final pre-commit

```bash
python scripts/run_all_validations.py --quick
git diff --stat
```

### Resumen de que hace cada tipo de archivo

| Archivo | Como se actualiza | Se toca en este flujo? |
|---------|-------------------|------------------------|
| VERSION.yaml | Fuente de verdad, se edita en releases | Se LEYE, no se edita (paso 1) |
| AGENTS.md | Auto-sync desde VERSION.yaml | Se verifica (paso 2) |
| README.md | Auto-sync desde VERSION.yaml | Se verifica (paso 2) |
| .cursorrules | Auto-sync desde VERSION.yaml | Se verifica (paso 2) |
| docs/CONTRIBUTING.md | Auto-sync header + manual contenido | Header auto (paso 2) |
| docs/GUIA_TECNICA.md | Auto-sync header + manual notas tecnicas | Se VERIFICA y se ACTUALIZA (paso 4) |
| CHANGELOG.md | MANUAL | Se VERIFICA y se ACTUALIZA (paso 3) |
| docs/contributing/REGISTRY.md | Auto-sync desde log_phase_completion.py | Se verifica (paso 2) |
| .agents/workflows/README.md | MANUAL | Se VERIFICA (paso 5) |
| .agent/SYSTEM_STATUS.md | AUTO via --doctor --status | Se REGENERA (paso 6) |
| ROADMAP.md | MANUAL | NO (solo si el usuario dice especificamente que actualizar Roadmap) |
| .agent/knowledge/DOMAIN_PRIMER.md | SEMI-AUTO via --doctor --regenerate-domain-primer | Se VERIFICA (paso 5b) |

### Paso 5b: Verificar DOMAIN_PRIMER.md

```bash
# Verificar que el Domain Primer este alineado con modulos reales python
python scripts/doctor.py --context
```

| Check | Accion si falla |
|-------|-----------------|
| Todo modulo en `modules/` esta documentado en DOMAIN_PRIMER.md | Ejecutar `python scripts/doctor.py --regenerate-domain-primer` |
| Todo archivo referenciado en DOMAIN_PRIMER.md existe en disco | Corregir referencia o eliminar seccion obsoleta |
| Version y codename coinciden con VERSION.yaml | Reemplazar header del DOMAIN_PRIMER |

### Lo que este flujo NO hace

- NO modifica ROADMAP.md (estrategia de monetizacion requiere intencion explicita)
- NO edita codigo fuente de ningun modulo
- NO ejecuta `v4complete` ni analiza hoteles
- NO agrega contenido nuevo a documentos -- solo verifica y actualiza lo existente

---

## Version Sync Gate (Release)

Cuando una fase marca un **release** (nueva version), antes de decir "documentacion actualizada":

```bash
# Registrar fase + verificar que docs manuales estan al dia
python scripts/log_phase_completion.py --fase FASE-X \
    --release X.Y.0 --check-manual-docs
```

**El gate verifica:**
1. CHANGELOG.md tiene entrada `[X.Y.0]`
2. CHANGELOG.md y VERSION.yaml coinciden en version
3. GUIA_TECNICA.md menciona la fase

Si hay desincronizacion:
```bash
python scripts/version_consistency_checker.py       # Diagnosticar
python scripts/sync_versions.py --fix               # Auto-reparar si posible
```

---

## Dependencia Critica: .agent/ y .agents/

El repositorio tiene **dos directorios cuyo nombre se confunde facilmente**. Esta confusion ha causado errores en el pasado.

```
.agent/     (singular)  → Ecosistema del agente (convencion, conocimiento, memoria)
.agents/    (plural)    → Skills/workflows del agente (archivos fisicos)
```

### Que es cada uno

| Directorio | Contenido | Quien lo usa |
|------------|-----------|--------------|
| `.agent/CONVENTION.md` | Contrato de arquitectura del ecosistema | Doctor, validaciones |
| `.agent/knowledge/` | DOMAIN_PRIMER.md (glosario, reglas negocio) | Agente en runtime |
| `.agent/memory/` | Sesiones, error_catalog, current_state.json | Agente (memoria) |
| `.agent/shadow_logs/` | Logs de sombra | Observabilidad |
| `.agent/workflows/` | **SYMLINK** → `.agents/workflows/` | Codigo legacy, validadores |
| `.agents/workflows/` | Archivos fisicos de skills (`.md`) | Phased executor, Doctor |

### Symlink critico: `.agent/workflows` → `.agents/workflows/`

El symlink `.agent/workflows/` apunta al directorio real `.agents/workflows/`. El codigo del agente lee skills desde `.agent/workflows/`, pero los archivos se crean y editan en `.agents/workflows/`.

**Si se rompe el symlink:**
- El Doctor falla en "Symlink integrity" check
- Skills aparecen como "inexistentes" para el validador
- El ecosistema pierde funcionalidad

**Validacion:**
```bash
python main.py --doctor              # Check automatico del symlink
ls -la .agent/workflows              # Debe mostrar → .agents/workflows
```

**Si necesitas recrearlo (raro, pero posible):**
```bash
# WSL/Linux:
ln -sf ../.agents/workflows .agent/workflows
```

**Regla:** Todos los archivos de skills van en `.agents/workflows/`. Nunca crees `.agent/workflows/` como carpeta real.

### Doctor CLI valida esta dependencia

El comando `python main.py --doctor` incluye un check de "Symlink integrity" que verifica que `.agent/workflows` apunte correctamente a `.agents/workflows`. Si hay desync, el reporte lo marca inmediatamente.

---

## Clasificacion de Archivos

### Sincronizacion automatica desde VERSION.yaml (cada commit)

| Archivo | Que sincroniza |
|---------|---------------|
| `AGENTS.md` | Version + fecha |
| `README.md` | Version + fecha |
| `.cursorrules` | Version + fecha |
| `docs/CONTRIBUTING.md` | Version header |
| `docs/GUIA_TECNICA.md` | Version + fecha |
| `docs/contributing/REGISTRY.md` | Fecha ultima actualizacion |

### Actualizacion manual (requiere agente)

| Archivo | Cuando |
|---------|--------|
| `CHANGELOG.md` | Nueva release |
| `docs/GUIA_TECNICA.md` | Cambios de arquitectura, stack o flujos |
| `ROADMAP.md` | Cambios en estrategia de monetizacion |
| `.agents/workflows/README.md` | Agregar/eliminar skills |
| `.agent/knowledge/DOMAIN_PRIMER.md` | Agregar/eliminar modulos, cambiar clases o flujo |

---

## Vinculo con el Contexto Global

- `AGENTS.md` es la **fuente canonica** del contexto global del agente. Si cambias contexto global, edita AGENTS.md primero.
- Si el ecosistema de agentes pierde funcionalidad, revisa primero la integridad del symlink `.agent/workflows`.
- Para actualizar **documentacion del repositorio**, sigue los procedimientos de este archivo.
- El prompt **"Actualizar documentacion oficial del repositorio"** ejecuta el procedimiento documentado en la seccion del mismo nombre. No es una frase decorativa -- es un dispatch a esta seccion.

---

## Regenerable

- `.agent/SYSTEM_STATUS.md` → `python main.py --doctor --status`
- `.agent/knowledge/DOMAIN_PRIMER.md` → `python main.py --doctor --regenerate-domain-primer`

---

## Indice de Fragmentos

| Fragmento | Contenido |
|-----------|-----------|
| [procedures.md](contributing/procedures.md) | Control de versiones, skills, context policy |
| [documentation_rules.md](contributing/documentation_rules.md) | Checklist docs obligatorias, clasificacion automatico/manual |
| [validation.md](contributing/validation.md) | Pre-commit, regresion, coherencia, troubleshooting |
| [capabilities.md](contributing/capabilities.md) | Capability contracts, Evidence Ledger, SitePresenceChecker |
| [REGISTRY.md](contributing/REGISTRY.md) | Registro auto-generado de fases completadas |
