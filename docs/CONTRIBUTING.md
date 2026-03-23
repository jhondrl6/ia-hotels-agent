# Guia de Contribucion - IA Hoteles Agent

> **Version Actual:** v4.5.3 (Communication Update)
> **Coherence Score:** 0.91 (≥0.8) - Publication Ready
> **Tests:** 1427+ passing

## Comandos CLI Activos

| Comando | Descripcion |
|---------|-------------|
| `v4complete` | Flujo completo: diagnostico, propuesta, assets, coherencia |
| `v4audit` | Auditoria con APIs externas (Rich Results, Places, PageSpeed) |
| `spark` | Diagnostico rapido <5min + guion WhatsApp |
| `execute` | Implementa paquete, recupera analisis v4.0 con coherence ≥ 0.8 |
| `stage` | Ejecuta etapas individuales (geo, ia, seo, outputs) |
| `deploy` | Despliegue remoto via FTP/WP-API |
| `setup` | Configuracion interactiva de API keys |
| `onboard` | Captura datos operativos del hotel |
| `audit` | Legacy v3.x (deprecado, usar `v4complete`) |

## Modulos Activos (v4.5.6)

| Modulo | Funcion | Ubicacion |
|--------|---------|-----------|
| `data_validation/` | Validacion cruzada web+GBP+input | `data_validation/` |
| `evidence_ledger.py` | Almacen centralizado de evidencia | `data_validation/` |
| `contradiction_engine.py` | Deteccion de hard/soft conflicts | `data_validation/` |
| `consistency_checker.py` | Validacion inter-documento | `data_validation/` |
| `metadata_validator.py` | Deteccion de CMS defaults | `data_validation/` |
| `schema_validator_v2.py` | Coverage scoring | `data_validation/` |
| `financial_engine/` | Escenarios: conservador/realista/optimista | `modules/financial_engine/` |
| `calculator_v2.py` | FinancialCalculatorV2 con validacion | `modules/financial_engine/` |
| `no_defaults_validator.py` | Validacion "No Defaults in Money" | `modules/financial_engine/` |
| `orchestration_v4/` | Flujo dos fases: Hook → Validacion | `modules/orchestration_v4/` |
| `asset_generation/` | Generacion condicional con gates | `modules/asset_generation/` |
| `asset_catalog.py` | Catalogo centralizado de assets | `modules/asset_generation/` |
| `llmstxt_generator.py` | Generacion de llms.txt | `modules/asset_generation/` |
| `providers/` | Benchmark, Researcher, Disclaimer (NEVER_BLOCK) | `modules/providers/` |
| `benchmark_resolver.py` | Fallback con benchmark regional | `modules/providers/` |
| `autonomous_researcher.py` | Investigacion en fuentes publicas | `modules/providers/` |
| `disclaimer_generator.py` | Disclaimers honestos por confidence | `modules/providers/` |
| `auditors/` | APIs externas (Rich Results, Places, PageSpeed) | `modules/auditors/` |
| `ai_crawler_auditor.py` | Auditoria de robots.txt para IA crawlers | `modules/auditors/` |
| `citability_scorer.py` | Score de citabilidad de contenido | `modules/auditors/` |
| `ia_readiness_calculator.py` | Score compuesto IA-readiness | `modules/auditors/` |
| `commercial_documents/` | Diagnostico, propuesta, coherencia | `commercial_documents/` |
| `composer.py` | Generacion deterministica de documentos | `commercial_documents/` |
| `coherence_validator.py` | Validador de coherencia | `commercial_documents/` |
| `quality_gates/` | Gates tecnico, comercial, financiero, coherencia | `modules/quality_gates/` |
| `publication_gates.py` | Gates de publicacion | `modules/quality_gates/` |
| `coherence_gate.py` | Gate de coherencia | `modules/quality_gates/` |
| `agent_harness/` | Memoria, auto-correccion, routing | `agent_harness/` |
| `observability/dashboard.py` | Metricas y tendencias de calidad | `observability/` |
| `observability/calibration.py` | Calibracion de umbrales de confianza | `observability/` |
| `data_models/` | Modelos: CanonicalAssessment, Claim, Evidence | `data_models/` |
| `enums/` | Enumeraciones: Severity, ConfidenceLevel | `enums/` |

## Reglas Obligatorias para Documentacion Contextual

### 1. Control de Versiones

**NUNCA** modificar versiones manualmente en archivos individuales.

Procedimiento correcto:
1. Editar `VERSION.yaml` con la nueva version
2. Ejecutar `python scripts/sync_versions.py`
3. Verificar cambios con `git diff`

### 2. Nueva Skill

Cuando agregues una nueva skill:
1. Crear archivo `.md` en `.agents/workflows/`
2. Incluir frontmatter con `description` y trigger
3. Actualizar `.agents/workflows/README.md`
4. Ejecutar `python scripts/generate_system_status.py`

### 3. Eliminar Skill

Cuando elimines una skill:
1. Mover archivo a `archives/legacy_code/skills_legacy_v330/`
2. Actualizar `.agents/workflows/README.md`
3. Verificar que `error_catalog.json` no referencie la skill eliminada
4. Si la referencía, actualizar el mensaje de error con el trigger correcto

### 4. Modificar Decision Engine

Cuando modifiques `modules/financial_engine/`:
1. Hacer los cambios de codigo
2. Ejecutar `python scripts/generate_domain_primer.py`
3. Verificar que DOMAIN_PRIMER.md refleje los cambios

### 5. Nuevo Modulo o Migracion Tecnica

Cuando agregues un nuevo modulo Python o realices una migracion tecnica:

1. **Crear codigo** en el modulo correspondiente (`modules/`)
2. **Crear tests** en `tests/` con cobertura minima 80%
3. **Actualizar documentacion** segun checklist abajo
4. **Ejecutar validaciones pre-commit** (ver §6)

**Checklist de documentacion obligatoria**:

| Documento | ¿Cuando actualizar? | Contenido |
|-----------|---------------------|-----------|
| `CHANGELOG.md` | Siempre | Entrada con archivos nuevos/modificados |
| `GUIA_TECNICA.md` | Si afecta arquitectura, stack o flujos | Seccion en "Notas de Cambios" |
| `INDICE_DOCUMENTACION.md` | Si el modulo es publico/utilizado | Fila en tabla de modulos |
| `ROADMAP.md` | Si es hito relevante para monetizacion | Fila en tabla de hitos |
| `VERSION.yaml` | Si es release completo | Incrementar version |

**Checklist de Capability Contract** (ver §13):

| Item | Descripcion |
|------|-------------|
| Capacidad definida | Nueva capability en matriz-capacidades.md |
| Punto de invocacion | Identificado en flujo principal |
| Output serializable | Verificado en to_dict/export/report |
| No es huerfana | Se ejecuta, no solo existe en codigo |

**Formato de entrada en CHANGELOG**:
```markdown
## v{VERSION} - {Titulo} (Fecha)

### Objetivo
{Descripcion breve del cambio}

### Cambios Implementados
- `ruta/archivo.py` - Descripcion del cambio

### Archivos Nuevos
| Archivo | Descripcion |
|---------|-------------|
| `ruta/nuevo.py` | Descripcion |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `ruta/existente.py` | Descripcion del cambio |

### Tests
- X tests en `test_xxx.py`
```

### 6. Sistema de Validacion (v3.8.0)

El sistema ahora utiliza pre-commit hooks + Validation Engine nativo.

#### Instalacion (una vez)

```bash
pip install pre-commit
pre-commit install
```

#### Antes de cada commit

Si prefieres validacion manual:

```bash
# Validacion rapida (recomendado)
python scripts/run_all_validations.py --quick

# Validacion completa
python scripts/run_all_validations.py

# Validacion post-cambios v4complete (si se modificaron modulos v4)
python .agents/workflows/v4_regression_guardian.py --quick
```

#### Validaciones disponibles

| Comando | Descripcion |
|---------|-------------|
| `python scripts/run_all_validations.py` | Todas las validaciones (7 checks) |
| `python scripts/run_all_validations.py --quick` | Validaciones esenciales (4 checks) |
| `python scripts/validate.py --plan` | Validar coherencia Plan Maestro |
| `python scripts/validate.py --security` | Detectar secrets hardcoded |
| `python scripts/validate.py --content <file>` | Validar contenido de archivo |
| `pre-commit run --all-files` | Ejecutar todos los hooks manualmente |

Si alguna validacion falla, corregir antes de hacer commit.

## 7. Politica de Contexto Global

### WHY

- Reducir ambiguedad operativa con una sola fuente primaria de contexto global.
- Evitar divergencia entre instrucciones humanas, scripts y configuraciones de runtime.

### WHAT

- `AGENTS.md` es el archivo canónico humano-curado de contexto global.
- `.cursorrules` es un artefacto puente de compatibilidad para tooling legacy.
- Los detalles de bajo nivel deben vivir en docs/scripts (progressive disclosure), no en reglas globales extensas.

### HOW

1. Editar primero `AGENTS.md` para cualquier cambio de contexto global.
2. Mantener `.cursorrules` alineado como puente (sin reglas nuevas exclusivas ahi).
3. Actualizar scripts/configs dependientes cuando cambie la gobernanza contextual:
   - `scripts/sync_versions.py`
   - `scripts/validate_context_integrity.py`
   - `.gemini/config.yaml`
4. Ejecutar validaciones post-cambio contextual (checklist abajo).

### Migracion segura de nombre de archivo contextual

- **No renombrar en seco**: no reemplazar `.cursorrules` por `AGENTS.md` sin soporte de compatibilidad.
- **Mantener compatibilidad**: conservar `.cursorrules` como puente mientras existan dependencias legacy.
- **Actualizar dependencias**: ajustar scripts/configs que referencien archivos contextuales antes de retirar compatibilidad.

### Checklist post-cambio contextual

```bash
# 1) Validacion rapida
python scripts/run_all_validations.py --quick

# 2) Validacion completa
python scripts/run_all_validations.py
```

## Estructura de Archivos de Contexto

| Archivo | Proposito | Frecuencia de Actualizacion |
|---------|-----------|----------------------------|
| `VERSION.yaml` | Fuente unica de verdad | Cada release |
| `AGENTS.md` | Contexto global canónico humano-curado | Manual (fuente primaria) |
| `.cursorrules` | Puente de compatibilidad para tooling legacy | Sincronizado con `AGENTS.md` |
| `GEMINI.md` | Identidad/mandatos historicos del agente | Mantenimiento limitado/compatibilidad |
| `DOMAIN_PRIMER.md` | Glosario y reglas de negocio | Automatico desde codigo |
| `error_catalog.json` | Catalogo de errores para self-healing | Manual |
| `.agents/workflows/*.md` | Skills activas del sistema | Manual/semiautomatico |

## Scripts de Mantenimiento

| Script | Uso |
|--------|-----|
| `sync_versions.py` | Sincroniza versiones desde VERSION.yaml |
| `generate_domain_primer.py` | Regenera DOMAIN_PRIMER desde codigo |
| `validate_context_integrity.py` | Valida referencias cruzadas |
| `cleanup_sessions.py` | Limpia sesiones antiguas |
| `normalize_cache_filenames.py` | Normaliza nombres de cache |
| `generate_system_status.py` | Genera dashboard de estado |
| `run_all_validations.py` | Orquestador de validaciones (sin Gemini CLI) |
| `validate.py` | CLI para validaciones especificas |
| `structure_guard.py` | Detecta archivos residuales + valida Plan Maestro |
| `.agents/workflows/v4_regression_guardian.py` | Validación post-cambios para flujo v4complete |
| `extract_psi_metrics.py` | Extrae metricas de PageSpeed Insights |
| `sync_conductor_spec.py` | Sincroniza especificaciones del Conductor |
| `fill_upgrade_proposal.py` | Genera propuestas de upgrade |
| `test_coordinates_extraction.py` | Prueba extraccion de coordenadas |
| `validate_structure.py` | Valida estructura del proyecto |
| `cleanup_workdirs.py` | Limpia directorios de trabajo |
| `prune_outputs.py` | Elimina outputs antiguos |
| `config_checker.py` | Verifica configuracion del proyecto |

## 8. Clasificacion de Archivos de Documentacion

### Sistema de Sincronización (Config-Driven)

A partir de v4.5.6, el sistema de sincronización es **config-driven**:
- **Configuración**: `scripts/sync_config.yaml` - declara qué sincronizar dónde
- **Script**: `scripts/sync_versions.py` - ejecuta las reglas del config
- **Extensible**: agregar sync = agregar 4 líneas al YAML

**Flujo:**
1. Editar `VERSION.yaml` con nueva versión
2. Ejecutar `python scripts/sync_versions.py`
3. El script sincroniza automáticamente según `sync_config.yaml`

**Comandos:**
```bash
python scripts/sync_versions.py          # Sync all files
python scripts/sync_versions.py --check   # Check if sync needed
python scripts/sync_versions.py --list    # List all sync rules
python scripts/sync_versions.py --validate # Validate config
```

### Archivos sincronizados automaticamente

| Archivo | Qué sincroniza |
|---------|---------------|
| `README.md` | Version, fecha, status banner, codename |
| `AGENTS.md` | Version, codename, fecha, status table |
| `.cursorrules` | Version, fecha |
| `INDICE_DOCUMENTACION.md` | Version, fecha |

### Archivos que se actualizan manualmente

| Archivo | Cuando actualizar |
|---------|------------------|
| CHANGELOG.md | Nueva release (registro historico de cambios) |
| GUIA_TECNICA.md | Cambios arquitectonicos o tecnicos |
| ROADMAP.md | Cambios en estrategia de monetizacion |
| CONTRIBUTING.md | Nuevos procedimientos de mantenimiento |
| .agents/workflows/README.md | Agregar o eliminar skills |
| docs/PRECIOS_PAQUETES.md | Cambios en precios o paquetes |

### Casos en que NO se utiliza CONTRIBUTING

| Situacion | Accion correcta |
|-----------|-----------------|
| Agregar entrada al CHANGELOG | Editar manualmente, NO usar procedimientos de Contributing |
| Actualizar ROADMAP estrategico | Editar manualmente |
| Agregar nueva seccion a GUIA_TECNICA | Editar manualmente |
| Cambiar precios en PRECIOS_PAQUETES.md | Editar manualmente |
| Agregar nuevo template en templates/ | Editar manualmente |
| Actualizar archivos de benchmarks | Editar manualmente |

## 9. Guia de Uso Rapido

### Antes de cualquier cambio
Consulta esta tabla para determinar el procedimiento correcto:

| Si quieres... | Entonces... |
|--------------|-------------|
| Cambiar version del proyecto | Editar VERSION.yaml -> ejecutar `python scripts/sync_versions.py` |
| Agregar una nueva skill | Seguir procedimiento §2 Nueva Skill |
| Eliminar una skill | Seguir procedimiento §3 Eliminar Skill |
| Modificar Decision Engine | Seguir procedimiento §4 |
| Agregar nuevo modulo | Seguir procedimiento §5 Nuevo Modulo |
| Hacer commit | Ejecutar checklist §6 (obligatorio) |
| Actualizar CHANGELOG | Editar manualmente (NO usar procedimientos de Contributing) |
| Actualizar ROADMAP | Editar manualmente |
| Actualizar GUIA_TECNICA | Editar manualmente |
| Actualizar CONTRIBUTING | Editar manualmente |

### Flujo de trabajo tipico

```
1. Determinar el tipo de cambio -> consultar tabla arriba
2. Si requiere procedimiento -> seguir los pasos de la seccion correspondiente
3. Si es manual -> editar directamente el archivo
4. Antes de commit -> ejecutar checklist §6
5. Verificar con git diff
```

### Prompts de referencia

Cuando trabajes con el agente, puedes usar:
- "Estoy por hacer [X]. Que procedimiento sigo segun CONTRIBUTING.md?"
- "Voy a cambiar la version. Cual es el flujo correcto?"
- "Antes de hacer commit, que debo verificar?"

### Resumen de scripts

| Script | Cuando ejecutarlo |
|--------|------------------|
| `run_all_validations.py --quick` | Antes de cada commit (recomendado) |
| `run_all_validations.py` | Validacion completa antes de release |
| `pre-commit run --all-files` | Antes de cada commit (si no esta instalado) |
| `sync_versions.py` | Despues de editar VERSION.yaml |
| `generate_domain_primer.py` | Despues de modificar financial_engine/ |
| `generate_system_status.py` | Despues de agregar/eliminar skill |
| `validate.py --plan` | Despues de modificar Plan Maestro |
| `validate.py --security` | Antes de push (verificar secrets) |
| `validate_structure.py` | Validar estructura del proyecto |
| `config_checker.py` | Verificar configuracion |
| `extract_psi_metrics.py` | Extraer metricas PageSpeed |
| `.agents/workflows/v4_regression_guardian.py --quick` | Despues de cambios en modulos v4 |

## 10. Solucion de Problemas

### Error: "pre-commit not found"
```bash
pip install pre-commit
```

### Error: "pytest failed"
```bash
# Ver detalles de tests fallidos
pytest tests/ -v --tb=short
```

### Saltar validaciones (NO recomendado)
```bash
git commit -m "mensaje" --no-verify
```

### Error: "version out of sync"
```bash
python scripts/sync_versions.py
```

---

## 11. Controles de Coherencia v4.0

Al agregar nuevos checks de coherencia o modificar los existentes:

### 11.1 Definir en `.conductor/guidelines.yaml`

Todas las reglas de coherencia deben definirse en el archivo canónico:

```yaml
v4_coherence_rules:
  nuevo_check:
    confidence_threshold: 0.8
    blocking: true|false
    description: "Descripción clara del check"
```

**Convenciones:**
- `confidence_threshold`: Valor entre 0.0 y 1.0
- `blocking`: `true` si el check debe bloquear la generación de assets
- `description`: Explicación legible para el usuario

### 11.2 Implementar en `modules/commercial_documents/coherence_validator.py`

```python
def _check_nuevo_check(self, ...) -> CoherenceCheck:
    """Descripción del check."""
    # Obtener configuración
    threshold = self.config.get_threshold('nuevo_check')
    is_blocking = self.config.is_blocking('nuevo_check')
    
    # Realizar validación
    passed = ...  # Lógica de validación
    score = ...   # Score entre 0.0 y 1.0
    
    return CoherenceCheck(
        name='nuevo_check',
        passed=passed,
        score=score,
        message='...',
        severity='error' if is_blocking and not passed else 'warning'
    )
```

**Reglas:**
1. Siempre usar `self.config` para obtener umbrales (no hardcodear)
2. Respetar el flag `blocking` para determinar severidad
3. Incluir mensajes claros para el usuario

### 11.3 Agregar al método `validate()`

```python
def validate(self, ...):
    checks = [
        self._check_problems_have_solutions(...),
        self._check_assets_are_justified(...),
        # ... checks existentes
        self._check_nuevo_check(...),  # Nuevo check
    ]
```

### 11.4 Documentar en `DOMAIN_PRIMER.md`

Agregar al glosario:
```markdown
### Nuevo Check
**Definición**: Descripción del check
**Mapeo**: `coherence_validator._check_nuevo_check()`
**Umbrales**: confidence >= 0.8
**Casos de borde**: 
- Caso X: Comportamiento Y
```

### 11.5 Sincronizar con Workflow

Actualizar `.agents/workflows/v4_coherence_validator.md`:
- Agregar paso de ejecución si aplica
- Actualizar criterios de éxito
- Documentar umbral configurable

### 11.6 Tests Obligatorios

Crear tests en `tests/test_coherence_validator.py`:
```python
def test_nuevo_check_passed(self):
    """Test cuando el check pasa."""
    ...

def test_nuevo_check_failed(self):
    """Test cuando el check falla."""
    ...

def test_nuevo_check_blocking(self):
    """Test comportamiento blocking."""
    ...
```

### 11.7 Validación Pre-Commit

Antes de commit, verificar:
```bash
# 1. Regla en YAML
python -c "from modules.commercial_documents import CoherenceConfig; c = CoherenceConfig(); print(c.get_rule('nuevo_check'))"

# 2. Check implementado
python -c "from modules.commercial_documents import CoherenceValidator; v = CoherenceValidator(); assert hasattr(v, '_check_nuevo_check')"

# 3. Tests pasan
pytest tests/test_coherence_validator.py::TestNuevoCheck -v

# 4. Validaciones del proyecto
python scripts/run_all_validations.py
```

---

## 12. Sistema de Regresión v4.2.0

### 12.1 Dos Modos de Validación

El sistema soporta dos modos de validación E2E:

| Modo | Requisitos | Uso |
|------|-----------|-----|
| `url-only` | Assets >=3/5, Performance presente, GBP diagnosticado | Análisis rápido sin datos operativos |
| `with-onboarding` | Coherence >=0.8, Datos financieros VERIFIED | Análisis completo con onboarding |

### 12.2 Script de Regresión

```bash
# Modo URL-only (default)
python .opencode/plans/v4_repair_plan/scripts/regression_test.py \
    --new output/v4_complete/ \
    --mode url-only

# Modo with-onboarding
python .opencode/plans/v4_repair_plan/scripts/regression_test.py \
    --new output/v4_complete/ \
    --mode with-onboarding
```

### 12.3 Checks de Regresión

| # | Check | Validación |
|---|-------|------------|
| 1 | Assets Generated | >=3/5 assets generados |
| 2 | Coherence Score | Estructura válida (url-only) o >=0.8 (with-onboarding) |
| 3 | Performance Detected | Score presente (0-100) |
| 4 | Performance Status | "VERIFIED" o "LAB_DATA_ONLY" |
| 5 | GBP Diagnostics | `error_type` poblado si `place_found=false` |
| 6 | Diagnostic Structure | 4 secciones obligatorias |
| 7 | Proposal Structure | 5 secciones obligatorias |

### 12.4 Nuevos Assets Generables

| Asset | Tipo | Requiere | Fallback |
|-------|------|----------|----------|
| `geo_playbook` | Markdown | gbp_data | Sí (con warning) |
| `review_plan` | Markdown | gbp_reviews | Sí (con warning) |
| `review_widget` | HTML | review_data | Sí (con warning) |
| `org_schema` | JSON-LD | org_data | Sí (con warning) |

### 12.5 Tests Obligatorios para Nuevos Assets

Cuando agregues un nuevo tipo de asset:

1. **Agregar generador** en `modules/asset_generation/conditional_generator.py`
2. **Agregar test** en `tests/asset_generation/test_conditional_new_assets.py`
3. **Validar preflight** permite fallback con `block_on_failure=False`
4. **Ejecutar regresión** para validar E2E

### 12.6 Checklist Pre-Release
 
Antes de considerar una release completa:
 
```bash
# 1. Tests unitarios
python -m pytest tests/ -x --tb=short -q

# 2. Regresión url-only
python .opencode/plans/v4_repair_plan/scripts/regression_test.py \
    --new output/test_validation/v4_complete/ \
    --mode url-only

# 3. Validaciones del proyecto
python scripts/run_all_validations.py

# 4. Verificar coherencia documentación
git diff --stat
```
 
### 12.7 Validación Post-Cambios con v4_regression_guardian
 
El v4_regression_guardian es una skill que valida que cambios en código no introduzcan regresiones en el flujo v4complete.
 
#### Uso
```bash
# Validación rápida (recomendado después de cambios)
python .agents/workflows/v4_regression_guardian.py --quick

# Validación completa
python .agents/workflows/v4_regression_guardian.py --full

# Modo CI (salida mínima)
python .agents/workflows/v4_regression_guardian.py --quiet

# Directorio alternativo de trabajo
python .agents/workflows/v4_regression_guardian.py --workdir /ruta/al/proyecto

# Re-ejecutar tests que fallaron anteriormente
python .agents/workflows/v4_regression_guardian.py --retry-failed

# Combinaciones
python .agents/workflows/v4_regression_guardian.py --full --quiet
```

#### Guía de Uso

| Flag | Descripción | Cuándo Usar |
|------|-------------|--------------|
| `--quick` | Solo tests críticos + baseline | Después de cambios menores |
| `--full` | Todos los tests de módulos afectados | Cambios críticos en financial_engine, quality_gates |
| `--quiet` | Salida mínima para CI/CD | Pipelines automatizados |
| `--workdir` | Directorio alternativo | Probar en diferente ubicación |
| `--retry-failed` | Re-ejecutar tests fallidos | Después de correcciones |

#### Cuándo usar
 
#### Diferencia con regression_test.py
Mientras que `regression_test.py` valida los outputs de un análisis v4complete específico (assets generados, coherence score, etc.), el `v4_regression_guardian` valida que los cambios en el código no hayan roto las pruebas unitarias y de regresión subyacentes.
 
#### Cuándo usar
Ejecutar este guardian después de modificar cualquiera de estos módulos antes de hacer commit:
- orchestration_v4/
- data_validation/
- financial_engine/
- asset_generation/
- commercial_documents/
- modules/quality_gates/
 
#### Integración con Sistema de Capacidades
Esta skill está registrada como capability conectada en la matriz de capacidades, verificando que se invoque en runtime y produzca output observable (reportes en validation_reports/).
```


---

## 13. Sistema de Capability Contracts (v4.4.0)

### 13.1 Propósito

Detectar y prevenir "capacidades desconectadas" - módulos que existen en código pero no se invocan en runtime ni producen output observable.

### 13.2 Definición de Capability Contract

| Campo | Descripción |
|-------|-------------|
| Capability | Nombre del módulo/validador |
| Estado | conectada/desconectada/huérfana |
| Punto de Invocación | Dónde se ejecuta (archivo:método) |
| Evidencia en Output | Artefacto donde se serializa |

### 13.3 Checklist de Verificación

Cuando integres una nueva capacidad:

- [ ] **Existe en código**: Archivo con clase/función
- [ ] **Se invoca**: No solo se importa, se ejecuta en flujo
- [ ] **Produce output**: Serializa en to_dict/export/report
- [ ] **Documentada**: Punto de invocación registrado
- [ ] **Testeada**: Tests cubriendo caso normal y edge

### 13.4 Patrón de Verificación

```bash
# 1. Listar capabilities del contrato
grep -rn "class.*Validator\|class.*Checker" modules/ data_validation/

# 2. Verificar invocación en flujo principal
grep -rn "Validator()\|Checker()" main.py modules/

# 3. Verificar output en serialización
grep -rn "to_dict\|export\|report" main.py | grep -i "validator"
```

### 13.5 Matriz de Capacidades (Output)

Crear `.opencode/plans/matriz-capacidades.md`:

| Capability | Estado | Punto Invocación | Output | Severidad |
|------------|--------|-----------------|--------|-----------|
| MetadataValidator | conectada | v4_comprehensive.py:_audit_metadata() | audit_result.metadata | HIGH |
| PublicationGates | conectada | main.py:FASE 4.5 | gate_results | CRITICAL |
| ConsistencyChecker | conectada | main.py:FASE 4.6 | consistency_report | HIGH |
| FinancialCalculatorV2 |conectada | main.py:FASE 3 | scenarios | CRITICAL |
| EvidenceLedger | conectada | v4complete:FASE 2 | evidence_ledger | HIGH |
| ContradictionEngine | conectada | v4complete:FASE 2 | contradiction_report | CRITICAL |
| CoherenceValidator | conectada | commercial_documents/ | coherence_score | CRITICAL |
| NoDefaultsValidator | conectada | financial_engine/ | validation_result | CRITICAL |
| AICrawlerAuditor | conectada | v4audit/ | crawler_audit | MEDIUM |
| CitabilityScorer | conectada | v4audit/ | citability_score | MEDIUM |
| IAReadinessCalculator | conectada | v4audit/ | ia_readiness_score | MEDIUM |
| Dashboard | conectada | observability/ | metrics_report | LOW |
| Calibration | conectada | observability/ | calibration_result | LOW |

### 13.6 Gate de Cierre

Antes de marcar fase como completada:

- [ ] 0 capacidades sin invocación en runtime
- [ ] 0 capacidades sin output observable
- [ ] `matriz-capacidades.md` actualizado

### 13.7 Casos de Uso

| Situación | Acción |
|-----------|--------|
| Nuevo validador/validator | Agregar a matriz-capacidades.md |
| Nueva capability en orchestrator | Documentar punto de invocación |
| Capacidad sin output | INVESTIGAR - puede ser huérfana |
| Módulo existente sin uso | Crear capacidad o archivar |

### 13.8 Relación con phased_project_executor

Este sistema se integra con la skill `.agents/workflows/phased_project_executor.md`:

- Paso 1.5: Verificación de Capacidades Desconectadas
- Paso 7.4: Runtime Invocation & Output Evidence
- Paso 8: Disconnected Capability Gate

Ver documentación completa en `phased_project_executor.md` v1.4.0.

---

## 14. Sistema de Evidence Ledger (v4.3.0)

### 14.1 Proposito

El Evidence Ledger es el almacen centralizado de evidencia que alimenta todo el sistema de validacion cruzada.

### 14.2 Estructura

```
evidence/
├── ledger.json          # Registro central
├── claims/              # Claims por hotel
│   └── {hotel_url}/
│       └── claim_{id}.json
└── evidence/            # Evidencias raw
    └── {hotel_url}/
        ├── web_{timestamp}.json
        ├── gbp_{timestamp}.json
        └── input_{timestamp}.json
```

### 14.3 Integracion

Cuando agregues nueva evidencia:

1. **Web scraping**: Guardar en `evidence/evidence/{hotel}/web_{ts}.json`
2. **GBP API**: Guardar en `evidence/evidence/{hotel}/gbp_{ts}.json`
3. **User input**: Guardar en `evidence/evidence/{hotel}/input_{ts}.json`
4. **Ledger**: Agregar entrada en `evidence/ledger.json`

### 14.4 Scripts relacionados

| Script | Uso |
|--------|-----|
| `scripts/cleanup_sessions.py` | Limpia sesiones antiguas |
| `scripts/normalize_cache_filenames.py` | Normaliza nombres de cache |

---

## 15. Taxonomia de Confianza

| Nivel | Confidence | Criterio | Uso en Assets |
|-------|------------|----------|---------------|
| 🟢 VERIFIED | ≥ 0.9 | 2+ fuentes coinciden | Directo |
| 🟡 ESTIMATED | 0.5-0.9 | 1 fuente o benchmark | Con disclaimer |
| 🔴 CONFLICT | < 0.5 | Fuentes contradicen | Bloqueado |

### 15.1 Gates de Assets

| Asset | Threshold | Comportamiento |
|-------|-----------|----------------|
| WhatsApp | ≥ 0.9 | PASSED |
| WhatsApp | 0.5-0.9 | ESTIMATED con disclaimer |
| WhatsApp | < 0.5 | BLOCKED |
| FAQ Page | ≥ 0.7 | PASSED |
| FAQ Page | < 0.7 | ESTIMATED/BLOCKED |
| Hotel Schema | ≥ 0.8 | PASSED |
| Hotel Schema | < 0.8 | ESTIMATED/BLOCKED |

---

## 16. Quality Gates de Publicacion

Antes de marcar un analisis como `READY_FOR_CLIENT`:

| Gate | Umbral | Severidad |
|------|--------|-----------|
| hard_contradictions | = 0 | CRITICAL |
| evidence_coverage | ≥ 95% | HIGH |
| financial_validity | sin defaults | CRITICAL |
| coherence | ≥ 0.8 | CRITICAL |
| critical_recall | ≥ 90% | HIGH |

### 16.1 Estados de Publicacion

| Estado | Descripcion |
|--------|-------------|
| `DRAFT_INTERNAL` | Analisis en progreso |
| `REQUIRES_REVIEW` | Gate fallido, requiere correccion |
| `READY_FOR_CLIENT` | Todos los gates pasados |
