# FASE-1: BookingScraper Real

**ID**: FASE-1  
**Objetivo**: Implementar scraping real en `modules/scrapers/booking_scraper.py` para reemplazar el STUB actual  
**Dependencias**: Ninguna (Fase inicial)  
**Duración estimada**: 2-3 horas  
**Skill**: `systematic-debugging` + `iah-cli-spark-command-fix`

---

## Contexto

El proyecto Amaziliahotel v4complete tiene un **score forense de 16/100** (umbral: 80). La causa raíz del 83% de los bugs es que `BookingScraper.scrape()` es un STUB que retorna datos vacíos.

**Impacto de resolver FASE-1** (resuelve 5/12 hallazgos por cascada):
- H1: research.json vacio → se resuelve solo
- H2: hotel_schema generico → requiere FASE-2A post-FASE-1
- H6: monthly_report vacio → requiere FASE-2B post-FASE-1
- H9: 75% assets ESTIMATED → se resuelve solo (confidence sube)
- H11: delivery_ready 25% → se resuelve solo (gate pasa)

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| Preparación (esta sesión) | ✅ Completada |

### Base Técnica Disponible
- `modules/scrapers/booking_scraper.py` (STUB líneas 33-81)
- `modules/providers/benchmark_resolver.py` (referencia para APIs)
- Tests actuales: ~2224 funciones, 140 archivos
- Output existente: `output/v4_complete/amaziliahotel/research_e2623f16b1ee_Amaziliahotel.json` (vacío)

---

## Tareas

### Tarea 1: Diagnosticar el STUB actual
**Objetivo**: Entender exactamente qué retorna el STUB y por qué

**Archivos afectados**:
- `modules/scrapers/booking_scraper.py`

**Criterios de aceptación**:
- [ ] Leer líneas 33-81 de `booking_scraper.py`
- [ ] Documentar qué datos retorna actualmente (research.json está vacio)
- [ ] Identificar qué datos REALES necesita el pipeline (hotel_schema, faq_page, etc.)

### Tarea 2: Implementar scraping real o fuente alternativa
**Objetivo**: Reemplazar el STUB con datos reales verificados

**Opciones válidas** (elegir una):
1. **Google SerpAPI** (recomendado para hotels): scrapea Google Maps/Places
2. **Playwright + web scraping**: scrapeo directo del sitio del hotel
3. **Datos del GBP verificados**: usar datos conocidos ya verificados en auditoría

**Datos verificados disponibles** (para fallback):
```
nombre: Amazilia Hotel Campestre
rating: 4.5 | reviews: 202 | photos: 10
phone: 310 4019049
address: mts a la derecha, Via Pereira a #Entrada 8 Cafelia, 600, CERRITOS, Pereira, Risaralda
geo_score: 62/100
```

**Archivos afectados**:
- `modules/scrapers/booking_scraper.py`
- `modules/providers/benchmark_resolver.py` (si usa SerpAPI)

**Criterios de aceptación**:
- [ ] `research.json` contiene datos reales (no vacio)
- [ ] `confidence` > 0.5 (datos verificados de fuentes reales)
- [ ] `sources_checked` no está vacío
- [ ] `data_found` tiene campos: nombre, rating, reviews, phone, address, geo

### Tarea 3: Validar cascada en pipeline
**Objetivo**: Verificar que al resolver H1, los hallazgos H9 y H11 se resuelven automáticamente

**Archivos afectados**:
- `modules/asset_generation/v4_asset_orchestrator.py`
- `modules/publication/publication_gates.py`

**Criterios de aceptación**:
- [ ] Regenerar `research.json` con datos reales
- [ ] Verificar que confidence sube de 0.5 a > 0.7
- [ ] Verificar que delivery_ready pasa de 25% a > 80%

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_booking_scraper_returns_data` | `tests/scrapers/test_booking_scraper.py` | Debe pasar con datos reales |
| `test_research_json_not_empty` | `tests/asset_generation/test_research_json.py` | `data_found` no vacío |
| `test_confidence_above_threshold` | `tests/asset_generation/test_confidence.py` | `confidence > 0.5` |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/scrapers/test_booking_scraper.py -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Restricciones

- NO modificar otros scrapers (google_travel.py, etc.) en esta fase
- NO cambiar la firma del método `scrape()` — mantener backwards compatibility
- Los datos verificados del GBP pueden usarse como fallback si scraping falla

---

## Para Iniciar

1. **Leer** `FASE-1: BookingScraper Real` (este archivo)
2. **Ejecutar** en nueva sesión (workflow `phased_project_executor.md` §1 - Preparación)
3. **Siguiente** fase según `dependencias-fases.md`: FASE-2A, 2B, 2C (paralelas, dependen de FASE-1)

**Recordatorio**: Una fase por sesión. No ejecutar múltiples fases en la misma sesión.

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`**
   - Marcar FASE-1 como ✅ Completada
   - Actualizar fecha de finalización
   - Agregar método usado (SerpAPI/Playwright/GBP fallback)

2. **`09-documentacion-post-proyecto.md`**
   - **Sección A**: Agregar módulos tocados
   - **Sección D**: Actualizar score forense (debería subir de 16)
   - **Sección E**: Archivos afiliados actualizados

3. **Ejecutar**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-1 \
    --desc "BookingScraper real implementado - reemplazo STUB por scraping real" \
    --archivos-mod "modules/scrapers/booking_scraper.py" \
    --tests "3" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] **Tests nuevos pasan**: `test_booking_scraper_returns_data` pasa
- [ ] **Validaciones del proyecto**: `python scripts/run_all_validations.py --quick` pasa 4/4
- [ ] **`dependencias-fases.md` actualizado**: FASE-1 marcada ✅
- [ ] **research.json no vacío**: `data_found` tiene datos reales
- [ ] **confidence > 0.5**: Verificado en `research.json`
- [ ] **Sources no vacío**: `sources_checked` tiene al menos 1 fuente
- [ ] **Documentación afiliada**: log_phase_completion.py ejecutado
- [ ] **Post-ejecución completada**: Todos los puntos de la sección anterior realizados

**NO marcar la fase como completada si algún criterio falla.**
