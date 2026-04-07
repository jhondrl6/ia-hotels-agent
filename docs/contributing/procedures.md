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

## 4. Modificar Financial Engine o agregar modulos nuevos

Cuando modifiques `modules/financial_engine/` o agregues/elimines un modulo dentro de `modules/`:
1. Hacer los cambios de codigo
2. Verificar que DOMAIN_PRIMER.md refleje los cambios:
   - Modulo documentado en tabla de modulos
   - Clases clave listadas
   - Pipeline actualizado si cambio flujo
3. Si hubo cambios estructurales significativos:
   `python main.py --doctor --regenerate-domain-primer`

---

## 5. Actualizar Benchmarks Regionales

**Periodicidad recomendada:** Cada 3-6 meses.

Los benchmarks regionales (GEO, AEO, SEO) se usan en el diagnostico como "Promedio Regional" en la tabla de visibilidad. Se actualizan con datos reales de investigacion de mercado via LLM deep research.

### Flujo completo

```
1. Investigacion
   ├── Ejecutar prompt de deep research (ver abajo)
   └── LLM devuelve JSON con datos de 15+ hoteles por region

2. Guardar resultado
   └── Guardar como: data/benchmarks/research_output.json

3. Calcular y aplicar
   ├── Revisar:  python scripts/update_benchmarks.py --dry-run
   └── Aplicar:  python scripts/update_benchmarks.py

4. Verificar
   └── El script actualiza plan_maestro_data.json y reporta cambios
```

### Archivos involucrados

| Archivo | Rol |
|---------|-----|
| `data/benchmarks/research_output.json` | Input: datos crudos del LLM (se sobrescribe cada vez) |
| `data/benchmarks/plan_maestro_data.json` | Output: valores calculados que el sistema consume |
| `modules/scrapers/scraper_fallback.py` | Fallback si plan_maestro no carga (sincronizar manualmente si se actualiza) |
| `scripts/update_benchmarks.py` | Script que calcula promedios y actualiza plan_maestro |

### Que calcula el script

Aplica las mismas formulas del sistema a cada hotel de la muestra:

- **GEO**: Identica a `google_places_client.calculate_geo_score()` - rating, reviews, fotos, horarios, website
- **AEO**: Proxy basado en schema_hotel + schema_faq + open_graph + robots_ai
- **SEO**: Proxy basado en has_own_website + schema_hotel + schema_faq + mobile_speed

Luego promedia por region y actualiza los campos `geo_score_ref`, `aeo_score_ref`, `seo_score_ref` en cada region de `plan_maestro_data.json`.

### Prompt de deep research

Usar el siguiente prompt con un LLM con capacidad de deep research (Gemini, ChatGPT, Claude):

```
Investiga el estado promedio de visibilidad digital de hoteles boutique y
pequenos en 3 regiones turísticas de Colombia.

REGIONES: Eje Cafetero, Antioquia, Caribe colombiano.

Para cada región, consulta Google Maps/Places para 15-20 hoteles boutique
(10-60 habitaciones). Para CADA hotel registra:

A) GEO: nombre, ciudad, rating (0-5), reviews, fotos, has_hours, has_website
B) AEO: schema_hotel, schema_faq, open_graph, robots_ai_friendly
C) SEO: has_own_website, mobile_speed (buena/regular/mala)

FORMATO DE ENTREGA - JSON:
{
  "regiones": {
    "eje_cafetero": { "hotels": [/* objs con campos A+B+C */] },
    "antioquia":   { "hotels": [...] },
    "caribe":      { "hotels": [...] }
  }
}

REGLAS: Solo hoteles independientes (no cadenas). Si no puedes verificar un
campo, omitelo (no inventes). Mínimo 10 hoteles por región.
```

### Nota sobre el fallback

`scraper_fallback.py` tiene los mismos valores hardcoded como safety net. Si actualizas benchmarks via `update_benchmarks.py`, esos valores quedan desincronizados. Para sincronizar manualmente:

```bash
# Verificar diferencia entre plan_maestro y fallback
grep "geo_score_ref\|aeo_score_ref\|seo_score_ref" \
  data/benchmarks/plan_maestro_data.json \
  modules/scrapers/scraper_fallback.py
```

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
| `doctor.py` | Diagnostico del ecosistema + regenerar DOMAIN_PRIMER (`--regenerate-domain-primer`) |
| `validate_context_integrity.py` | Valida referencias cruzadas (incluye DOMAIN_PRIMER) |
| `validate_agent_ecosystem.py` | Valida integridad del ecosistema (knowledge, skills, symlinks) |
| `cleanup_sessions.py` | Limpia sesiones antiguas |
| `normalize_cache_filenames.py` | Normaliza nombres de cache |
| `generate_system_status.py` | Genera dashboard de estado |
| `log_phase_completion.py` | Registra fase completada en REGISTRY.md |
| `update_benchmarks.py` | Actualiza benchmarks regionales desde research JSON |
