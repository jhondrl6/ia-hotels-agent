# FASE-2-DEFAULT: Eliminar hardcoded defaults cross-hotel

**ID**: FASE-2-DEFAULT
**Objetivo**: Eliminar defaults hardcodeados de 'Amazilia Hotel Campestre' en open_graph_generator.py y corregir conditional_generator.py para usar la API pública.
**Dependencias**: FASE-1-COH (✅)
**Duración estimada**: 1.5-2 horas
**Skill**: `phased-workflow-self-improvement` (reglas de ejecución directa)
**Modo de ejecución**: DIRECTO — código puro, sin comandos externos ni subagentes.

---

## Contexto

`open_graph_generator.py` tiene **defaults hardcodeados de otro hotel** en 3 lugares:
- L87: `hotel_data.get('hotel_name', 'Amazilia Hotel Campestre')`
- L94: `rating = hotel_data.get('rating', 4.5)` y `review_count = hotel_data.get('review_count', 202)`
- L107: `website_url = hotel_data.get('website_url', hotel_data.get('website', 'https://amaziliahotel.com/'))`

Esto NO es LLM hallucination — es código Python determinístico. Cuando el pipeline pasa `hotel_data` con key `'name'` en vez de `'hotel_name'`, el fallback es literalmente otro hotel.

Además, `conditional_generator.py` L523 llama métodos privados de OpenGraphGenerator directamente (`generator._generate_html(generator._extract_og_data(...))`), bypassando la lógica de validación y escritura del generator público.

**Causa raíz**: R2, R3 — defaults cross-hotel + uso de métodos privados.

---

## Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-1-COH | ✅ Completada |

---

## Base Técnica Disponible

- `modules/asset_generation/open_graph_generator.py` — L87, L94, L107 con defaults hardcodeados
- `modules/asset_generation/conditional_generator.py` — L523 llama métodos privados
- Tests existentes en `tests/asset_generation/`

---

## Tareas

### T1: Eliminar defaults cross-hotel en open_graph_generator.py
**Objetivo**: Quitar todos los fallbacks de 'Amazilia Hotel Campestre' y validar explícitamente.

**Cambios**:
1. L87: Reemplazar `hotel_data.get('hotel_name', 'Amazilia Hotel Campestre')` por:
   ```python
   hotel_name = hotel_data.get('hotel_name') or hotel_data.get('name', '')
   if not hotel_name or hotel_name.strip() == '':
       raise ValueError(f"open_graph_generator requiere hotel_name válido. Keys recibidas: {list(hotel_data.keys())}")
   ```
2. L94: Eliminar defaults 4.5 y 202. Usar `hotel_data.get('rating')` y `hotel_data.get('review_count')` sin fallback. Si no existen, omitir del markup o usar valores vacíos según corresponda.
3. L107: Eliminar default 'https://amaziliahotel.com/'. Usar:
   ```python
   website_url = hotel_data.get('website_url') or hotel_data.get('website') or hotel_data.get('url', '')
   if not website_url:
       raise ValueError("open_graph_generator requiere website_url válido")
   ```

**Criterios de aceptación**:
- [ ] `grep -c "Amazilia" modules/asset_generation/open_graph_generator.py` → 0
- [ ] `grep -c "amaziliahotel" modules/asset_generation/open_graph_generator.py` → 0
- [ ] Validación explícita de hotel_name y website_url presente

### T2: Corregir conditional_generator.py para usar API pública
**Objetivo**: Eliminar llamada a métodos privados de OpenGraphGenerator.

**Cambios**:
1. L523: Reemplazar `generator._generate_html(generator._extract_og_data(...))` por una llamada pública. Evaluar si `generator.generate()` ya existe y cumple el propósito. Si no, crear un método público `generate_from_data()` que exponga la lógica necesaria sin exponer internals.
2. Asegurar que el output escrito a archivo sea idéntico (o mejor) que antes.

**Criterios de aceptación**:
- [ ] `grep "_generate_html\|_extract_og_data" modules/asset_generation/conditional_generator.py` → 0
- [ ] conditional_generator usa solo métodos públicos de OpenGraphGenerator

### T3: Auditoría grep por otros defaults cross-hotel
**Objetivo**: Confirmar que no hay otros generators con defaults de hotel específico.

**Pasos**:
1. `grep -r "Amazilia\|amaziliahotel\|Visperas\|hotelvisperas" modules/asset_generation/` — buscar nombres de hoteles conocidos.
2. `grep -r "get(.*, '.*Hotel" modules/asset_generation/` — buscar patrones `.get('key', 'Hotel Name')` sospechosos.
3. Si se encuentran otros casos, documentarlos. Si son triviales, corregirlos en esta misma tarea. Si son complejos, reportar para plan de fase futuro.

**Criterios de aceptación**:
- [ ] Auditoría completada con resultado documentado
- [ ] 0 defaults cross-hotel restantes en modules/asset_generation/

### T4: Tests para open_graph_generator
**Objetivo**: Validar que el generator rechaza datos incompletos y no produce output con nombres de hotel incorrectos.

**Tests**:
1. `test_rejects_missing_hotel_name`: `hotel_data={'name': ''}` → ValueError
2. `test_rejects_missing_website_url`: `hotel_data={'hotel_name': 'X'}` → ValueError
3. `test_accepts_valid_data`: datos completos → output sin "Amazilia"
4. `test_uses_name_when_hotel_name_missing`: `hotel_data={'name': 'Hotel X'}` → output contiene "Hotel X"

**Criterios de aceptación**:
- [ ] 4 tests nuevos pasan
- [ ] 0 regresiones en tests existentes de asset_generation/
- [ ] `run_all_validations.py --quick` pasa 4/4

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`** — Marcar FASE-2-DEFAULT como ✅ Completada.
2. **`06-checklist-implementacion.md`** — Marcar todos los items de FASE-2-DEFAULT como ✅.
3. **`09-documentacion-post-proyecto.md`** — Sección E: agregar archivos modificados. Sección D: actualizar métricas.
4. **Evidencia**: si hay outputs de auditoría grep, guardar en `evidence/FASE-2-DEFAULT/`.
5. **`log_phase_completion.py`**:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-2-DEFAULT \
    --desc "Eliminar defaults hardcodeados cross-hotel en open_graph_generator.py y fix conditional_generator.py para usar API publica" \
    --archivos-mod "modules/asset_generation/open_graph_generator.py,modules/asset_generation/conditional_generator.py" \
    --tests "4" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] **T1 completo**: 0 ocurrencias de "Amazilia" o "amaziliahotel" en open_graph_generator.py
- [ ] **T2 completo**: conditional_generator ya no llama métodos privados
- [ ] **T3 completo**: Auditoría grep completada, 0 defaults cross-hotel restantes
- [ ] **T4 completo**: 4 tests nuevos pasan, 0 regresiones
- [ ] **Validaciones del proyecto**: `python scripts/run_all_validations.py --quick` pasa 4/4
- [ ] **`dependencias-fases.md` actualizado**: Estado de FASE-2-DEFAULT marcado ✅
- [ ] **Documentación afiliada**: `09-documentacion-post-proyecto.md` actualizado
- [ ] **log_phase_completion.py ejecutado**: REGISTRY.md tiene entrada FASE-2-DEFAULT

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- **NO ejecutar v4complete** en esta fase.
- **NO modificar ROADMAP.md** — solo en FASE-RELEASE.
- **Máximo 60 iteraciones**.
- **Presupuesto estimado**: ~25-35 iteraciones trabajo + ~15 docs/verificación.
