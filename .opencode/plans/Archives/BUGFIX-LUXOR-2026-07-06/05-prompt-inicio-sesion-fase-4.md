# FASE-4: BUG-6 — SPA Rendering con Playwright (MAYOR COMPLEJIDAD TÉCNICA)

## ⚠️ FASE DE MAYOR COMPLEJIDAD ⚠️
Requiere integrar Playwright como fallback para renderizar SPAs, manejar timeouts, y fallback graceful.

---

**ID**: FASE-4
**Objetivo**: Integrar Playwright como fallback para renderizar SPAs antes del SEO audit, para que los OG tags y meta tags se detecten correctamente.
**Dependencias**: Ninguna (independiente de FASE-1, FASE-2, FASE-3)
**Duración estimada**: 2-3 horas
**Skill**: `phased-project-executor`

---

## Contexto

Plan: BUGFIX-LUXOR-2026-07-06 v4.60.1
Contexto origen: `/.opencode/context/Historico/bugs_no_onboarding_luxor_2026-07-06.md`

El sitio de Luxorhotel es un SPA (JavaScript app shell). El fetcher HTTP obtiene el app shell vacío, por lo que el SEO elements detector no encuentra OG tags. Playwright está instalado pero no se usa para renderizar SPAs antes del audit.

### Estado de Fases Anteriores
- FASE-1: NO INICIADA (independiente)
- FASE-2: NO INICIADA (independiente)
- FASE-3: NO INICIADA (independiente)

### Base Técnica Disponible
- `modules/auditors/v4_comprehensive.py` — L505 `_run_seo_elements_audit(page_html)` recibe HTML del fetch HTTP inicial
- `modules/auditors/seo_elements_detector.py` — L41-87 `detect(html, url)` parsea con BeautifulSoup
- `modules/utils/http_client.py` — cliente HTTP (posiblemente necesite modificación)
- Playwright instalado: `venv/Lib/site-packages/playwright` v1.58.0
- Selenium instalado: v4.38.0 (NO se usa para renderizar SPAs)
- `tests/auditors/test_seo_elements_detector.py` — tests del detector

---

## Tareas

### T1: Verificar instalación de Playwright y capacidad de renderizado

**Objetivo**: Confirmar que Playwright está instalado y que `playwright install chromium` está disponible.

**Acción:**
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -c "from playwright.sync_api import sync_playwright; print('OK')"
# Verificar si chromium está instalado:
./venv/Scripts/python.exe -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(); print('chromium OK'); b.close(); p.stop()"
```

- Si chromium NO está instalado, documentar el comando: `./venv/Scripts/python.exe -m playwright install chromium`
- Verificar si hay otros lugares del código que ya usan Playwright (para seguir el patrón existente).

**Criterios de aceptación:**
- [ ] Playwright importable y chromium disponible (o comando de instalación documentado)
- [ ] Patrones existentes de uso de Playwright en el código identificados (si los hay)

---

### T2: Integrar Playwright como fallback para SPAs

**Objetivo**: Detectar cuando el sitio es un SPA y renderizar con Playwright antes de parsear OG tags.

**Archivos afectados:**
- `modules/auditors/v4_comprehensive.py` (~L505 `_run_seo_elements_audit`)
- `modules/auditors/seo_elements_detector.py` (~L41-87 `detect()`)
- Posiblemente `modules/utils/http_client.py`

**Causa raíz (verificada contra código vivo):**
- El fetcher HTTP obtiene el app shell vacío: `<!doctype html><html lang=en translate=no>...<script type="text/javascript">`
- `seo_elements_detector.py:41-87` — `detect(html, url)` parsea con BeautifulSoup. Funciona correctamente con HTML real, pero recibe HTML vacío del app shell.
- `v4_comprehensive.py:505` — `_run_seo_elements_audit(page_html)` recibe `page_html` del fetch HTTP inicial (app shell, no renderizado).
- Los OG tags se renderizan client-side vía JavaScript.

**Diseño del fix:**

1. **Detección de SPA (heurística):**
   - HTML con `<script>` tags pero sin og tags Y pocos meta tags → probable SPA.
   - Heurística: si el HTML tiene < N meta tags (ej. < 3) y tiene tags `<script>`, considerar SPA.

2. **Renderizado con Playwright:**
   - Si se detecta SPA, usar Playwright para renderizar la página y obtener el HTML renderizado.
   - Timeout: 10-15 segundos máximo.
   - Si Playwright falla (no instalado, timeout, error), fallback a BeautifulSoup sobre HTML estático (no crashear).

3. **Integración:**
   - Opción A: Modificar `_run_seo_elements_audit` en `v4_comprehensive.py` para detectar SPA y renderizar antes de pasar HTML al detector.
   - Opción B: Modificar `detect()` en `seo_elements_detector.py` para aceptar una URL y renderizar internamente si detecta SPA.
   - **Recomendación:** Opción A — mantiene `detect()` como función pura de parsing y mueve la lógica de renderizado al llamador.

**Ejemplo de implementación (Opción A):**
```python
def _run_seo_elements_audit(self, page_html, url):
    # Detectar SPA
    if self._is_spa(page_html):
        rendered_html = self._render_with_playwright(url)
        if rendered_html:
            page_html = rendered_html
    return SE0ElementsDetector.detect(page_html, url)

def _is_spa(self, html):
    """Detectar si el HTML es un SPA app shell."""
    soup = BeautifulSoup(html, 'html.parser')
    scripts = soup.find_all('script')
    meta_tags = soup.find_all('meta')
    og_tags = soup.find_all('meta', attrs={'property': lambda x: x and x.startswith('og:')})
    # Heurística: tiene scripts pero pocos meta tags y sin OG tags
    return len(scripts) > 0 and len(meta_tags) < 3 and len(og_tags) == 0

def _render_with_playwright(self, url, timeout=15000):
    """Renderizar página con Playwright. Retorna HTML renderizado o None si falla."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, timeout=timeout)
            page.wait_for_load_state('networkidle', timeout=timeout)
            html = page.content()
            browser.close()
            return html
    except Exception as e:
        logger.warning(f"Playwright rendering failed for {url}: {e}")
        return None
```

**Caveats:**
- Manejar timeouts (no dejar que el agente se cuelgue).
- Fallback graceful si Playwright falla (no crashear, retornar BeautifulSoup result sobre HTML estático).
- Considerar usar `wait_for_load_state('networkidle')` o `'domcontentloaded'` según el sitio.

**Verificación inmediata:**
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
grep -n 'playwright' modules/auditors/v4_comprehensive.py
# Post-fix: Debe mostrar imports y uso de Playwright
grep -n '_is_spa\|_render_with_playwright' modules/auditors/v4_comprehensive.py
# Post-fix: Debe mostrar los nuevos métodos
```

**Criterios de aceptación:**
- [ ] Detección de SPA implementada (heurística)
- [ ] Renderizado con Playwright integrado
- [ ] Fallback graceful si Playwright falla (no crashear)
- [ ] HTML renderizado se pasa al SEO elements detector

---

### T3: Agregar tests de SPA rendering

**Objetivo**: Tests que validen la detección de SPA y el renderizado con Playwright.

**Archivos afectados:**
- `tests/auditors/test_seo_elements_detector.py` (o `tests/auditors/test_v4_comprehensive.py`)

**Tests:**
1. `test_is_spa_detection`:
   - HTML de SPA vacío → `_is_spa()` retorna `True`.
   - HTML con OG tags → `_is_spa()` retorna `False`.
2. `test_render_with_playwright_mock`:
   - Mock `sync_playwright` → retorna HTML renderizado con OG tags.
   - Verificar que `detect()` encuentra los OG tags del HTML renderizado.
3. `test_fallback_when_playwright_fails`:
   - Si Playwright no disponible/falla → fallback a BeautifulSoup (no crashear).
   - Verificar que `detect()` retorna resultado sobre HTML estático.

**Criterios de aceptación:**
- [ ] Test de detección de SPA agregado y pasando
- [ ] Test de renderizado con Playwright mock agregado y pasando
- [ ] Test de fallback graceful agregado y pasando

---

### T4: Ejecutar tests de regresión

**Comando:**
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/auditors/test_seo_elements_detector.py -v
```

**Criterios de éxito:**
- ✅ Todos los tests existentes pasan sin cambios
- ✅ Nuevos tests de SPA rendering pasan
- ✅ Sin errores de importación o mock

---

## Post-Ejecución: log_phase_completion.py

**Comando (ejecutar SOLO si T1-T4 completan exitosamente):**
```bash
cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe scripts\log_phase_completion.py --fase FASE-4 --desc BUG6_spa_rendering_playwright_fallback --archivos-mod modules/auditors/v4_comprehensive.py,modules/auditors/seo_elements_detector.py --tests 3 --check-manual-docs"
```

---

## Actualizar Documentación

**Después de log_phase_completion.py:**

1. **CHANGELOG.md** (agregar entrada):
```markdown
### FASE-4 BUG-6
- Integrado Playwright como fallback para renderizar SPAs antes del SEO audit (OG tags ahora se detectan en sitios SPA)
```

2. **GUIA_TECNICA.md** (agregar nota técnica):
```markdown
### Notas de Cambios v4.60.1 - FASE-4

**Problema:** Sitios SPA (JavaScript app shell) retornaban HTML vacío al fetcher HTTP. El SEO elements detector no encontraba OG tags (falso negativo). AEO score incorrecto: 25 pts del componente Open Graph se perdían.
**Solución:** Detectar SPAs con heurística (scripts pero pocos meta tags) y renderizar con Playwright como fallback antes de parsear. Fallback graceful si Playwright falla.
**Módulos afectados:** `modules/auditors/v4_comprehensive.py`, posiblemente `modules/auditors/seo_elements_detector.py`
**Backwards compatibility:** ✅ Sin breaking changes — fallback a BeautifulSoup si Playwright falla
**Tests:** 3 tests nuevos (detección SPA, renderizado mock, fallback graceful)
**Dependencias:** Playwright ya instalado (v1.58.0), requiere `playwright install chromium`
```

3. **09-documentacion-post-proyecto.md** (acumular datos)

---

## Criterios de Completitud (CHECKLIST)

- [ ] **T1**: Playwright + chromium verificados (o instalación documentada)
- [ ] **T2**: Detección de SPA implementada
- [ ] **T2**: Renderizado con Playwright integrado
- [ ] **T2**: Fallback graceful si Playwright falla
- [ ] **T3**: Tests de SPA rendering agregados (3 tests)
- [ ] **T4**: Tests de regresión pasan
- [ ] **log_phase_completion.py**: Ejecutado exitosamente
- [ ] **Docs cascade**: CHANGELOG, GUIA_TECNICA, 09-documentacion actualizados

---

## Restricciones

- **NO ejecutar v4complete** (eso es FASE-5)
- **NO modificar `main.py`** (eso es FASE-1 y FASE-3)
- **NO modificar `llm_mention_checker.py`** (eso es FASE-2)
- **NO modificar `_audit_competitors` en v4_comprehensive.py** (eso es FASE-1 — solo tocar SEO audit)
- **Máximo 60 iteraciones** del agente
- **Verificar contra código vivo** antes de aplicar patch (los line numbers pueden estar stale)
- **NO crashear si Playwright falla** — siempre fallback graceful

---

## Budget de Iteraciones Estimado

```
Fijos:
  - Leer plan + verificar estado: ~3 iters
  - Investigar código/archivos: ~10-15 iters (mayor investigación por múltiples archivos)
  - log_phase_completion.py + docs cascade: ~10 iters
  Total fijo: ~23-28 iters

Específico:
  - T1 (verificar Playwright): ~3-5 iters
  - T2 (integrar fallback SPA): ~15-20 iters (mayor complejidad)
  - T3 (agregar tests): ~10-15 iters
  - T4 (run tests): ~2-3 iters
  Total específico: ~30-43 iters

Total estimado: 53-71 iters
```

⚠️ **Advertencia:** Si el budget estimado supera 60, considerar dividir en sub-fases:
- FASE-4A: T1 + T2 (investigación + implementación)
- FASE-4B: T3 + T4 (tests + verificación)

**Si el agente ve que va por 35+ iteraciones y T2 no ha terminado, pausar y documentar checkpoint.**

**Modo de ejecución:** Agente principal DIRECTO (código puro)

---

## Recuperación en Caso de Agotamiento

Si el agente alcanza 60 iteraciones:
1. Guardar estado actual del fix (si ya se aplicó)
2. Marcar fase como `⏳ INCOMPLETA` en `dependencias-fases.md`
3. Documentar checkpoint:
   - ¿T1 completado? (Playwright verificado)
   - ¿T2 completado? (SPA detection + render integrado)
   - ¿T3 completado? (tests agregados)
4. Retomar en nueva sesión desde el checkpoint
5. Si T2 quedó a medias, considerar dividir en FASE-4A/4B

---

## Checklist Final

- [ ] Playwright + chromium disponibles
- [ ] Detección de SPA implementada (heurística)
- [ ] Renderizado con Playwright integrado
- [ ] Fallback graceful si Playwright falla
- [ ] HTML renderizado se pasa al detector
- [ ] 3 tests nuevos agregados (detección, render mock, fallback)
- [ ] Todos los tests pasan
- [ ] log_phase_completion.py ejecutado
- [ ] CHANGELOG.md actualizado
- [ ] GUIA_TECNICA.md actualizado
- [ ] 09-documentacion-post-proyecto.md actualizado
