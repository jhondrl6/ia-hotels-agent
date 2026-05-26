# FASE-C: ADR scraper + Versión dinámica

**ID**: FASE-C
**Objetivo**: Conectar el ADR del web_scraper como fallback intermedio en la cadena de resolución + corregir versión hardcodeada `4.0.0` en el frontmatter del output.
**Dependencias**: FASE-1 y FASE-2 completadas (trabaja sobre generators ya modificados). **FASE-0 completada (Opción E)** — decisión comercial en `09-documentacion-post-proyecto.md` §F.
**Duración estimada**: 1-2 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

El ROI_AUDIT.md identificó dos problemas de trazabilidad:

1. **ADR del web_scraper desconectado (Fix 6, §0.8)**: `web_scraper.py` extrae `precio_promedio` del sitio web usando 4 métodos (Schema JSON-LD, meta tags, CSS selectors, regex). Pero la cadena de resolución de ADR en producción va: datos onboarding → benchmark regional → hardcode $300K. El precio scrapeado del sitio web **no se usa como fallback intermedio** entre onboarding y benchmark regional.

   **Infraestructura existente**: `adr_resolution_wrapper.py` YA tiene `_legacy_resolution_with_scraping()` (L151-159) que acepta `web_scraping_adr` y `_web_scraping_result()` (L136-149). La pregunta es si todos los callers de `main.py` están pasando el `web_scraping_adr` extraído.

2. **Versión hardcodeada (Fix 7, §0.7)**: `v4_proposal_generator.py:725` tiene `'version': '4.0.0'` hardcodeado. El frontmatter del output siempre dice `version: 4.0.0` sin importar la versión real del pipeline (actualmente v4.53.0). Esto elimina trazabilidad.

### Evidencia en código

```python
# v4_proposal_generator.py:725
'version': '4.0.0',  # ← hardcodeado, no refleja la versión real

# adr_resolution_wrapper.py:151-159 — YA existe el fallback, verificar callers
def _legacy_resolution_with_scraping(self, user_provided_adr, web_scraping_adr):
    if not user_provided_adr and web_scraping_adr and web_scraping_adr > 0:
        return self._web_scraping_result(web_scraping_adr)
    return self._legacy_resolution(user_provided_adr)
```

---

## Tareas

### Tarea 1: Verificar y conectar web_scraping ADR en main.py

**Archivo**: `main.py` — bloque de resolución de ADR (≈L1660-1760)

**Paso 1.1**: Identificar dónde `web_scraper.py` produce el `precio_promedio` y si ya se está pasando al `ADRResolutionWrapper`

**Paso 1.2**: Si NO se está pasando, agregar el paso: después del scraping, pasar `web_scraping_adr` al wrapper

**Paso 1.3**: Verificar que la cadena de fallback sea:
```
1. onboarding_data (user-provided)
2. web_scraping (precio del sitio web)     ← AGREGAR si falta
3. benchmark regional (validated_regions)
4. hardcode $300K (último recurso)
```

**Paso 1.4**: Si el wrapper YA recibe `web_scraping_adr` pero la cadena no lo prioriza correctamente, ajustar el orden en `adr_resolution_wrapper.py`

**Criterios de aceptación**:
- [ ] `web_scraping_adr` del scraper se pasa al `ADRResolutionWrapper`
- [ ] Si el scraper encuentra precio > 0, se usa como fallback antes del benchmark regional
- [ ] Si el scraper falla (precio = 0 o None), se salta al benchmark regional
- [ ] `financial_scenarios.json` refleja `adr_source: "web_scraping"` cuando corresponde

### Tarea 2: Dynamic version en vez de '4.0.0' hardcodeado

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py` L725

**Paso 2.1**: Identificar dónde se define la versión real del pipeline. Opciones:
- `agent_harness/__init__.py` → `__version__ = "3.2.0"` (NO es la versión del pipeline)
- `scripts/sync_versions.py` → maneja version bump
- Buscar `VERSION`, `version.txt`, o `setup.py`/`pyproject.toml`

**Paso 2.2**: Importar la versión real:
```python
# Opción A: Importar de un módulo central
try:
    from iah_cli import __version__ as PIPELINE_VERSION
except ImportError:
    PIPELINE_VERSION = "4.0.0"  # fallback seguro

# Opción B: Leer de archivo VERSION
# Opción C: Usar importlib.metadata
```

**Paso 2.3**: Reemplazar L725:
```python
# ANTES
'version': '4.0.0',

# DESPUÉS
'version': PIPELINE_VERSION,
```

**Criterios de aceptación**:
- [ ] Frontmatter muestra la versión real (actualmente ~v4.53.0)
- [ ] Si la versión no se puede resolver, fallback seguro (no crashea)
- [ ] Sin cambios en otros campos del frontmatter

---

## Tests Obligatorios

| Test | Comando | Criterio |
|------|---------|----------|
| Validación rápida | `python3 scripts/run_all_validations.py --quick` | 3/5+ checks pass |
| Import test version | `python3 -c "from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator; g = V4ProposalGenerator(); print('OK')"` | OK |
| ADR resolution | `python3 -c "from modules.financial_engine.adr_resolution_wrapper import ADRResolutionWrapper; print('OK')"` | OK |

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`**: Marcar FASE-C como ✅ Completada
2. **`06-checklist-implementacion.md`**: Marcar items C1-C2 como ✅
3. **`09-documentacion-post-proyecto.md`**: Agregar cambios
4. Ejecutar:
```bash
cmd.exe /c "venv\Scripts\python.exe scripts\log_phase_completion.py \
    --fase FASE-C \
    --desc \"ROI-REFACTOR: Conectar ADR web_scraper como fallback + dynamic version en frontmatter\" \
    --archivos-mod \"main.py,modules/commercial_documents/v4_proposal_generator.py,modules/financial_engine/adr_resolution_wrapper.py\" \
    --tests 0 \
    --check-manual-docs"
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] web_scraping ADR conectado a la cadena de resolución
- [ ] Orden de fallback: onboarding → web_scraping → benchmark → hardcode
- [ ] `adr_source` en JSON refleja fuente real
- [ ] `'version': '4.0.0'` → `PIPELINE_VERSION` dinámico
- [ ] Fallback seguro si versión no disponible
- [ ] `run_all_validations.py --quick` pasa
- [ ] `dependencias-fases.md` actualizado
- [ ] `06-checklist-implementacion.md` actualizado
- [ ] `09-documentacion-post-proyecto.md` actualizado
- [ ] `log_phase_completion.py` ejecutado

---

## Restricciones

- NO modificar `scenario_calculator.py` (la fórmula es correcta)
- NO ejecutar v4complete
- NO modificar `commercial_gate.py`
- NO romper la cadena de fallback existente — solo insertar web_scraping
- El orden de prioridad DEBE ser: user-provided > web_scraping > benchmark > hardcode
- Máximo 60 iteraciones de agente
