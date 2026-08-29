# FASE-2: BUG-4a — Resiliencia LLM (openrouter model externalization)

**ID**: FASE-2
**Objetivo**: Externalizar el modelo de OpenRouter hardcoded en `llm_mention_checker.py` al `provider_registry.yaml`, restaurando la resiliencia del pipeline LLM.
**Dependencias**: Ninguna (independiente de FASE-1)
**Duración estimada**: 1-2 horas
**Skill**: `phased-project-executor`

---

## Contexto

Plan: BUGFIX-LUXOR-2026-07-06 v4.60.1
Contexto origen: `/.opencode/context/Historico/bugs_no_onboarding_luxor_2026-07-06.md`

El pipeline LLM tiene un modelo hardcoded (`google/gemini-2.0-flash-001`) que fue removido/renombrado en OpenRouter (404). El `provider_registry.yaml` ya declara `default_model: qwen/qwen3.6-plus:free` pero NO se usa — el modelo está hardcoded en el `.py`.

### Estado de Fases Anteriores
- FASE-1: NO INICIADA (independiente — puede estar en cualquier estado)

### Base Técnica Disponible
- `modules/auditors/llm_mention_checker.py` — L239 hardcodea el modelo, L100 lee `GEMINI_API_KEY`
- `config/provider_registry.yaml` — declara `default_model` (no se usa)
- `.env` — tiene `OPENROUTER_API_KEY`, `DEEPSEEK_API_KEY`, `OPENAI_API_KEY`

---

## Tareas

### T1: Verificar catálogo OpenRouter actual

**Objetivo**: Confirmar qué modelo vigente reemplaza a `google/gemini-2.0-flash-001` en OpenRouter.

**Acción:**
- Consultar https://openrouter.ai/models para ver el catálogo actual.
- Verificar si `google/gemini-2.0-flash-001` sigue existiendo o fue renombrado.
- Identificar el modelo vigente que se debe usar como default.
- Verificar el `default_model` declarado en `provider_registry.yaml` (`qwen/qwen3.6-plus:free` o similar) — ¿existe en OpenRouter?

**Criterios de aceptación:**
- [ ] Modelo vigente identificado y documentado
- [ ] `default_model` del registry verificado como válido en OpenRouter (o actualizado)

---

### T2: Externalizar modelo al `provider_registry.yaml`

**Objetivo**: Hacer que `llm_mention_checker.py` lea el modelo del registry en lugar de hardcodearlo.

**Archivos afectados:**
- `modules/auditors/llm_mention_checker.py` (~L239)
- `config/provider_registry.yaml` (verificar/actualizar `default_model`)

**Causa raíz (verificada contra código vivo):**
- `llm_mention_checker.py:239` hardcodea `"model": "google/gemini-2.0-flash-001"`.
- El 404 indica que ese modelo fue removido/renombrado en OpenRouter.
- El `provider_registry.yaml` declara `default_model` pero NO se usa.

**Cambio esperado:**
1. grep para `google/gemini-2.0-flash-001` en `modules/auditors/llm_mention_checker.py` (NO confiar en L239 — stale).
2. Cargar el modelo desde `provider_registry.yaml`:
   - Leer el archivo YAML.
   - Obtener `default_model` para openrouter.
   - Usar ese valor en el payload del API call.
3. Verificar que `provider_registry.yaml` tiene el `default_model` correcto (actualizado en T1).

**Verificación inmediata:**
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
grep -n 'google/gemini-2.0-flash-001' modules/auditors/llm_mention_checker.py
# Post-fix: NO debe mostrar resultados
grep -n 'default_model' config/provider_registry.yaml
# Debe mostrar el modelo vigente
```

**Criterios de aceptación:**
- [ ] `google/gemini-2.0-flash-001` no aparece hardcoded en `llm_mention_checker.py`
- [ ] El modelo se lee dinámicamente desde `provider_registry.yaml`
- [ ] `provider_registry.yaml` tiene un `default_model` válido para openrouter

---

### T3: Agregar test mock verificando que el payload usa el modelo del registry

**Objetivo**: Test que valide que el modelo NO está hardcoded y se lee del registry.

**Archivos afectados:**
- `tests/auditors/test_llm_mention_checker.py` (o donde existan tests del módulo — verificar)

**Test:**
- Mock `_query_openrouter` verificando que el payload usa el modelo del `registry` (no hardcoded).
- Test de integración: requiere `OPENROUTER_API_KEY` real — marcar `@pytest.mark.skipif`.

**Criterios de aceptación:**
- [ ] Test mock agregado y pasando
- [ ] Test verifica que el modelo en el payload viene del registry

---

## Post-Ejecución: log_phase_completion.py

**Comando (ejecutar SOLO si T1-T3 completan exitosamente):**
```bash
cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe scripts\log_phase_completion.py --fase FASE-2 --desc BUG4a_openrouter_model_externalized_to_registry --archivos-mod modules/auditors/llm_mention_checker.py,config/provider_registry.yaml --tests 1 --check-manual-docs"
```

---

## Actualizar Documentación

**Después de log_phase_completion.py:**

1. **CHANGELOG.md** (agregar entrada):
```markdown
### FASE-2 BUG-4a
- Externalizado modelo de OpenRouter al `provider_registry.yaml` (antes hardcoded `google/gemini-2.0-flash-001`)
```

2. **GUIA_TECNICA.md** (agregar nota técnica):
```markdown
### Notas de Cambios v4.60.1 - FASE-2

**Problema:** Modelo `google/gemini-2.0-flash-001` hardcoded en `llm_mention_checker.py` fue removido de OpenRouter (404).
**Solución:** Externalizar modelo al `provider_registry.yaml`. El módulo ahora lee `default_model` del registry.
**Módulos afectados:** `modules/auditors/llm_mention_checker.py`, `config/provider_registry.yaml`
**Backwards compatibility:** ✅ Sin breaking changes — el registry ya declaraba `default_model`
**Tests:** 1 test mock nuevo
```

3. **09-documentacion-post-proyecto.md** (acumular datos)

---

## Criterios de Completitud (CHECKLIST)

- [ ] **T1**: Modelo vigente de OpenRouter identificado y documentado
- [ ] **T2**: `google/gemini-2.0-flash-001` no aparece hardcoded en `llm_mention_checker.py`
- [ ] **T2**: Modelo se lee dinámicamente desde `provider_registry.yaml`
- [ ] **T3**: Test mock agregado y pasando
- [ ] **log_phase_completion.py**: Ejecutado exitosamente
- [ ] **Docs cascade**: CHANGELOG, GUIA_TECNICA, 09-documentacion actualizados

---

## Restricciones

- **NO ejecutar v4complete** (eso es FASE-5)
- **NO configurar `GEMINI_API_KEY`** (eso es acción manual del usuario, fuera del plan)
- **NO modificar `main.py`** (eso es FASE-1 y FASE-3)
- **NO modificar `v4_comprehensive.py`** (eso es FASE-1 y FASE-4)
- **NO modificar `seo_elements_detector.py`** (eso es FASE-4)
- **Máximo 60 iteraciones** del agente
- **Verificar contra código vivo** antes de aplicar patch

---

## Budget de Iteraciones Estimado

```
Fijos:
  - Leer plan + verificar estado: ~3 iters
  - Investigar código/archivos: ~5-10 iters
  - log_phase_completion.py + docs cascade: ~10 iters
  Total fijo: ~18-23 iters

Específico:
  - T1 (verificar catálogo OpenRouter): ~3-5 iters (web_search)
  - T2 (externalizar modelo): ~8-12 iters
  - T3 (agregar test mock): ~8-12 iters
  Total específico: ~19-29 iters

Total estimado: 37-52 iters (dentro del límite de 60)
```

**Modo de ejecución:** Agente principal DIRECTO (código puro + web_search para catálogo)

---

## Recuperación en Caso de Agotamiento

Si el agente alcanza 60 iteraciones:
1. Guardar estado actual del fix (si ya se aplicó)
2. Marcar fase como `⏳ INCOMPLETA` en `dependencias-fases.md`
3. Documentar checkpoint
4. Retomar en nueva sesión

---

## Nota sobre BUG-4b (gemini 403)

**BUG-4b NO está en este plan.** Es configuración de credenciales:
- **Acción del usuario:** crear `GEMINI_API_KEY` en Google AI Studio (https://aistudio.google.com/apikey) y añadirla a `.env`.
- El código ya lee `GEMINI_API_KEY` correctamente (`llm_mention_checker.py:100`).
- **Prueba manual post-config:** ejecutar `python main.py v4complete --url http://www.luxorhotel.com.co/` y verificar que el log NO muestre `LLM query failed for gemini: 403`.

---

## Checklist Final

- [ ] Modelo OpenRouter vigente identificado
- [ ] `provider_registry.yaml` actualizado con modelo válido
- [ ] `llm_mention_checker.py` lee modelo del registry (no hardcoded)
- [ ] Test mock agregado
- [ ] Todos los tests pasan
- [ ] log_phase_completion.py ejecutado
- [ ] CHANGELOG.md actualizado
- [ ] GUIA_TECNICA.md actualizado
- [ ] 09-documentacion-post-proyecto.md actualizado
