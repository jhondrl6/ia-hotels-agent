# Issue: OG detection retorna falso negativo por HTML transitorio

## Fecha
2026-04-08 (detectado) | 2026-04-08 (diagnostico corregido)

## Prioridad
Media — No bloqueante, mejora incremental (+25pts AEO por hotel tipico)

## Estado
Pendiente (diagnostico corregido post-investigacion)

## Contexto

FASE-A (2026-04-08) implemento deteccion real de Open Graph en
`modules/auditors/seo_elements_detector.py` con BeautifulSoup:
- `_detect_open_graph()`: detecta `og:title`, `og:description`, `og:image`
- `_detect_images_alt()`: cuenta imagenes sin atributo alt
- `_detect_social_links()`: detecta 8 dominios sociales

**9 tests pasan** confirmando que el modulo funciona correctamente.

## Diagnostico anterior (INCORRECTO)

> "El modulo existe pero nunca es invocado durante la ejecucion de v4complete"

Esto es **FALSO**. La investigacion demostro que el detector SI corre:

1. `v4_comprehensive.py` L404: `seo_elements = self._run_seo_elements_audit(html_content, url)`
2. `v4_comprehensive.py` L500: `seo_elements=seo_elements` (asignado al V4AuditResult)
3. Log E2E confirma ejecucion:
   ```
   [2.9/5] Detecting SEO elements...
         Open Graph: False
   ```

El wiring **existe y funciona**. El detector corre y retorna un resultado.

## Diagnostico correcto

**El detector corre pero recibe HTML sin OG tags**, aunque el sitio los tiene.

### Evidencia

**El sitio SI tiene OG tags** (verificado con curl y Python/BeautifulSoup):
```
og:type        = "website"
og:url         = "https://hotelvisperas.com/"
og:title       = "Hotel Visperas | Luxury Nature Experience"
og:description = "Descubre el arte de descansar..."
og:image       = (supabase URL)
```

**Pero el log E2E reporta False:**
```
[2.9/5] Detecting SEO elements...
      Open Graph: False
      Images with Alt: True
      Active Social: False
```

### Causa raiz

El HTML que llega al detector en tiempo de ejecucion no contiene los OG tags.
El flujo es:

```
v4_comprehensive.py L391-393:
  HttpClient().get(url)  -->  html_for_citability
  html_content = html_for_citability.text

L404:
  seo_elements = self._run_seo_elements_audit(html_content, url)
```

El HttpClient hace una **segunda request** independiente (la primera fue en
step 2.1 para schema validation). El servidor puede devolver HTML diferente
entre requests, especialmente en sitios SPA/JS-rendered.

**Evidencia corroborativa:** Citability tambien dio 0.0/100 con **0 bloques
analizados** (linea 112 del log), usando el mismo `html_content`. Esto confirma
que el HTML recibido era minimal/sin contenido renderizado.

### Posibles causas del HTML transitorio

1. Sitio JS-rendered (SPA) que sirve shell HTML sin metadatos en primera carga
2. Rate limiting o cache del servidor que devuelve version reducida
3. Redireccion no seguida correctamente (og:url apunta a hotelvisperas.com
   sin www, pero el audit usa www.hotelvisperas.com/es)

## Impacto en scorecard

### Score AEO actual (OG no detectado):
```
Schema Hotel valido  -> +25pts  OK
FAQ Schema           ->   0pts  (no existe)
Open Graph           ->   0pts  (falso negativo)
Citabilidad          ->   0pts  (sin datos)
TOTAL: 25/100
```

### Score AEO potencial (OG detectado correctamente):
```
Schema Hotel valido  -> +25pts  OK
FAQ Schema           ->   0pts  (no existe)
Open Graph           -> +25pts  OK (hotel tipico tiene OG tags)
Citabilidad          ->   0pts  (sin datos)
TOTAL: 50/100
```

**Diferencia**: +25pts por hotel tipico. Pasaria de "Superior marginal" (25 vs bench 20)
a "Superior solido" (50 vs bench 20).

## Que falta

1. **Reutilizar HTML** del step 2.1 (schema audit) en vez de hacer segunda
   request en step 2.8. Asi el detector opera sobre el mismo HTML ya validado.
2. **Logging defensivo**: guardar HTML recibido por el detector para diagnostico
   cuando `open_graph=False` pero el sitio deberia tenerlo.
3. **Fallback de URL**: verificar si la redireccion www vs non-www afecta el
   HTML recibido (og:url apunta a hotelvisperas.com, audit usa www.hotelvisperas.com/es)

## Archivos involucrados

| Archivo | Rol | Estado |
|---------|-----|--------|
| `modules/auditors/seo_elements_detector.py` | Detector OG | OK (FASE-A) |
| `modules/auditors/v4_comprehensive.py` | Orchestrador del audit | L391-404: hace 2da request innecesaria |
| `modules/commercial_documents/v4_diagnostic_generator.py` | Consumidor del score | OK (L1358-1361 ya maneja datos) |
| `main.py` | Pipeline principal | OK (pasa audit_result directamente) |

## Riesgo de sobre-engineering

- El fix principal (eliminar "Pendiente de datos") ya esta resuelto
- Conectar OG es un incremento de 25pts, no una correccion de bug
- Beneficio comercial marginal: el diagnostico ya muestra score real
- Complejidad baja: reutilizar HTML existente en vez de segunda request

## Recomendacion

Incluir en la siguiente fase de feature work, NO como hotfix.
No requiere cambios en `_calculate_aeo_score()` (ya tiene el guard).
El fix principal es reutilizar el HTML del schema audit (step 2.1) en vez
de hacer una segunda request HTTP en step 2.8/2.9.

## Verificacion post-fix

```bash
# Ejecutar v4complete y verificar OG detectado correctamente
./venv/Scripts/python.exe main.py v4complete --url https://www.hotelvisperas.com/es --debug
grep "Open Graph" evidence/*/ejecucion.log
# Esperado: "Open Graph: True" (NO False)

grep "open_graph" output/v4_complete/audit_report.json
# Esperado: "open_graph": true (NO {} ni false)
```
