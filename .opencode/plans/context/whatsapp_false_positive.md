# Contexto: Falsos Positivos v4 — Historial y Estado Actual

## Fecha creacion: 2026-04-08
## Fecha actualizacion: 2026-04-09 (post-FASE-E investigacion)
## Hotel referencia: amaziliahotel.com

---

## Estado Global

| Fase | Estado | Sesion |
|------|--------|--------|
| FASE-A | Completado | 2026-04-09 |
| FASE-B | Completado | 2026-04-09 |
| FASE-C | Completado | 2026-04-09 |
| FASE-D | Completado (parcial) | 2026-04-09 |
| FASE-E | Completado | 2026-04-09 |
| **FASE-F** | **PENDIENTE** | - |

---

## CAUSA RAIZ CONFIRMADA (2026-04-09): Brotli Encoding

### Sintoma

BRECHA 2 "Sin WhatsApp" persiste en `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260409_170830.md` linea 78,
a pesar de que los fixes W0-W4 y R1-R3 fueron aplicados correctamente en FASE-A/E.

### Veredicto

El `HttpClient` pide Brotli al servidor (`Accept-Encoding: gzip, deflate, br`) pero la libreria
`brotli`/`brotlicffi` NO esta instalada en el venv. El servidor responde con `Content-Encoding: br`,
`requests` no puede decodificar y `response.text` entrega basura binaria.

### Evidencia directa

```
# Con Accept-Encoding: gzip, deflate, br (HttpClient actual):
HTML length: 33190
joinchat in HTML: False
class= count: 0
Content-Encoding: br (brotli)

# Con Accept-Encoding: gzip, deflate (sin br):
HTML length: 236640
joinchat in HTML: True
whatsapp in HTML: True
class= count: 694
Content-Encoding: gzip
```

### Impacto

TODO el pipeline que depende de HTML recibe basura:
- WhatsApp detection (BRECHA 2) — no puede detectar patrones
- Metadata validation — no ve CMS defaults
- SEO elements (Open Graph, etc.) — no detecta tags
- Citability scoring — no analiza contenido
- Schema extraction via HTML — no ve structured data

### Archivo afectado

`modules/utils/http_client.py` linea 47:
```python
'Accept-Encoding': 'gzip, deflate, br',  # 'br' causa basura sin libreria
```

### Solucion

**Fix primario:** Quitar `'br'` del Accept-Encoding. 1 linea, efecto inmediato, sin dependencias.

**Fix robusto (complementario):** `venv/Scripts/pip.exe install brotli` + agregar defensive check.

---

## Fixes Aplicados (FASE-A a FASE-E)

Estos fixes son correctos y necesarios. El problema es que NINGUNO tenia efecto porque el HTML
llegaba ilegible.

| Fix | Fase | Archivo | Estado |
|-----|------|---------|--------|
| W0 Patrones WhatsApp | A | v4_comprehensive.py, web_scraper.py | Aplicado (6 patrones Joinchat) |
| W1 ValidationSummary rama HTML | E | main.py:1766+ | Aplicado |
| W2 pain_mapper consulta html_detected | E | pain_solution_mapper.py | Aplicado |
| W3 web_scraper tel: links | E | web_scraper.py | Aplicado |
| W4 coherence_validator html_detected | E | coherence_validator.py | Aplicado |
| R1 Inferir region desde GBP | E | main.py | Aplicado |
| R2 Sanitizar "nacional" | E | v4_diagnostic_generator.py:413 | Aplicado |
| R3 Ampliar keywords URL | E | main.py:2691 | Aplicado |
| Brecha 5 Citability narrativa | B | v4_diagnostic_generator.py | Aplicado |
| Typo yRevisan | C | diagnostico_v6_template.md | Aplicado |

---

## FASE-F: Fix Brotli + Validacion E2E

Ver prompt: `.opencode/plans/05-prompt-inicio-sesion-fase-F.md`
