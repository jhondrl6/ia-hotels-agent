# Procedimientos: Version, Skills, Modulos

> Este documento contiene los procedimientos de mantenimiento segun CONTRIBUTING.md §1-§4.

---

## 1. Control de Versiones

**NUNCA** modificar versiones manualmente en archivos individuales.

Procedimiento correcto:
1. Editar `VERSION.yaml` con la nueva version
2. Ejecutar `python scripts/sync_versions.py`
3. Verificar cambios con `git diff`

---

## 2. Nueva Skill

Cuando agregues una nueva skill:
1. Crear archivo `.md` en `.agents/workflows/`
2. Incluir frontmatter con `description` y trigger
3. Actualizar `.agents/workflows/README.md`
4. Ejecutar `python scripts/generate_system_status.py`

---

## 3. Eliminar Skill

Cuando elimines una skill:
1. Mover archivo a `archives/legacy_code/skills_legacy_v330/`
2. Actualizar `.agents/workflows/README.md`
3. Verificar que `error_catalog.json` no referencie la skill eliminada
4. Si la referencia, actualizar el mensaje de error con el trigger correcto

---

## 4. Modificar Decision Engine

Cuando modifiques `modules/financial_engine/`:
1. Hacer los cambios de codigo
2. Ejecutar `python scripts/generate_domain_primer.py`
3. Verificar que DOMAIN_PRIMER.md refleje los cambios

---

## 7. Politica de Contexto Global

### WHY

- Reducir ambiguedad operativa con una sola fuente primaria de contexto global.
- Evitar divergencia entre instrucciones humanas, scripts y configuraciones de runtime.

### WHAT

- `AGENTS.md` es el archivo canonico humano-curado de contexto global.
- `.cursorrules` es un artefacto puente de compatibilidad para tooling legacy.
- Los detalles de bajo nivel deben vivir en docs/scripts (progressive disclosure), no en reglas globales extensas.

### HOW

1. Editar primero `AGENTS.md` para cualquier cambio de contexto global.
2. Mantener `.cursorrules` alineado como puente (sin reglas nuevas exclusivas ahi).
3. Actualizar scripts/configs dependientes cuando cambie la gobernanza contextual:
   - `scripts/sync_versions.py`
   - `scripts/validate_context_integrity.py`
   - `.gemini/config.yaml`
4. Ejecutar validaciones post-cambio contextual.

### Migracion Segura de Nombre de Archivo Contextual

- **No renombrar en seco**: no reemplazar `.cursorrules` por `AGENTS.md` sin soporte de compatibilidad.
- **Mantener compatibilidad**: conservar `.cursorrules` como puente mientras existan dependencias legacy.
- **Actualizar dependencias**: ajustar scripts/configs que referencien archivos contextuales antes de retirar compatibilidad.

### Checklist Post-Cambio Contextual

```bash
# 1) Validacion rapida
python scripts/run_all_validations.py --quick

# 2) Validacion completa
python scripts/run_all_validations.py
```

---

## Estructura de Archivos de Contexto

| Archivo | Proposito | Frecuencia de Actualizacion |
|---------|-----------|----------------------------|
| `VERSION.yaml` | Fuente unica de verdad | Cada release |
| `AGENTS.md` | Contexto global canonico humano-curado | Manual (fuente primaria) |
| `.cursorrules` | Puente de compatibilidad para tooling legacy | Sincronizado con `AGENTS.md` |
| `GEMINI.md` | Identidad/mandatos historicos del agente | Mantenimiento limitado/compatibilidad |
| `DOMAIN_PRIMER.md` | Glosario y reglas de negocio | Automatico desde codigo |
| `error_catalog.json` | Catalogo de errores para self-healing | Manual |
| `.agents/workflows/*.md` | Skills activas del sistema | Manual/semiautomatico |
| `docs/contributing/REGISTRY.md` | Registro de fases completadas | Automatico via log_phase_completion.py |

---

## Conexion con phased_project_executor.md

El executor de proyectos por fases (`.agents/workflows/phased_project_executor.md`) utiliza estos procedimientos:

- Paso 1: Analiza plan y detecta conflictos
- Paso 2-3: Crea prompts y checklist por fase
- **Paso 6**: Documentacion Post-Fase
  - Lee `documentation_rules.md` para checklist
  - Ejecuta `log_phase_completion.py` para registrar en `REGISTRY.md`
  - Verifica capability contracts segun `capabilities.md`

---

## Scripts de Mantenimiento

| Script | Uso |
|--------|-----|
| `sync_versions.py` | Sincroniza versiones desde VERSION.yaml |
| `generate_domain_primer.py` | Regenera DOMAIN_PRIMER desde codigo |
| `validate_context_integrity.py` | Valida referencias cruzadas |
| `cleanup_sessions.py` | Limpia sesiones antiguas |
| `normalize_cache_filenames.py` | Normaliza nombres de cache |
| `generate_system_status.py` | Genera dashboard de estado |
| `log_phase_completion.py` | Registra fase completada en REGISTRY.md |
