# Prompt de Inicio de Sesion — FASE-F: Fix Brotli Encoding + Defensa en Profundidad

## Contexto

### Documento de referencia
`/mnt/c/Users/Jhond/Github/iah-cli/.opencode/plans/context/whatsapp_false_positive.md`

### Estado de Fases Anteriores

FASE-A a FASE-E completadas. Todos los fixes de codigo (W0-W4, R1-R3, citability, typo) estan
aplicados correctamente. Sin embargo, BRECHA 2 "Sin WhatsApp" persiste en el diagnostico generado
porque NINGUN fix tenia efecto: el HTML llega como basura binaria al pipeline.

### Causa Raiz Confirmada

`HttpClient` (`modules/utils/http_client.py:47`) envia `Accept-Encoding: gzip, deflate, br`.
Servidores LiteSpeed/nginx responden con `Content-Encoding: br` (Brotli). El venv NO tiene `brotli`
instalada. `requests` no puede decodificar y `response.text` entrega binario crudo como UTF-8.

Resultado: 33KB de basura en vez de 236KB de HTML real. TODO el pipeline de diagnostico opera
sobre HTML ilegible: deteccion WhatsApp, metadata, SEO elements, citability, schemas.

### Evidencia

```
# HttpClient actual (con br, sin libreria):
HTML length: 33190, class= count: 0, joinchat: False, Content-Encoding: br

# Sin br:
HTML length: 236640, class= count: 694, joinchat: True, Content-Encoding: gzip
```

### Principio rector

Un falso diagnostico ("Sin WhatsApp" cuando el hotel SI lo tiene) destruye credibilidad al
primer vistazo del cliente. No hay margen de error. Este fix no puede limitarse a resolver
Brotli: debe anticipar CUALQUIER causa futura de HTML corrupto/ilegible.

---

## Objetivo

1. Corregir la causa raiz inmediata (Brotli)
2. Agregar validacion de integridad HTML que detecte CUALQUIER tipo de HTML corrupto
3. Validar E2E que todos los fixes de FASE-A/E funcionan contra HTML real
4. Agregar test de regresion para que esto no vuelva a pasar

---

## Tareas

### T1: Instalar libreria brotli

```bash
venv/Scripts/pip.exe install brotli
```

Libreria local de compresion, sin API keys, sin servicios externos.
Una vez instalada, `requests`/`urllib3` decodifican `Content-Encoding: br` automaticamente.

---

### T2: Agregar _validate_html_integrity() en v4_comprehensive.py

**Archivo:** `modules/auditors/v4_comprehensive.py`
**Ubicacion:** Nuevo metodo en la clase `V4ComprehensiveAuditor`

Este metodo es el guardian que detecta CUALQUIER forma de HTML corrupto, no solo Brotli:

```python
def _validate_html_integrity(self, html: str, url: str) -> bool:
    """
    Valida que el HTML sea legible y no basura binaria/comprimida.
    
    Detecta: Brotli sin decodificar, binario crudo, paginas de error,
    respuestas vacias, JavaScript-only shells sin contenido.
    
    Returns:
        True si el HTML es valido para analisis, False si es ilegible.
    """
    if not html or len(html) < 200:
        logger.warning(f"HTML too short or empty for {url} ({len(html) if html else 0} chars)")
        return False
    
    html_lower = html.lower()
    
    # Check 1: Debe tener estructura HTML basica
    has_structure = any(tag in html_lower for tag in ['<html', '<head', '<body', '<!doctype', '<div'])
    if not has_structure:
        logger.error(
            f"HTML integrity failed for {url}: no HTML structure found. "
            f"First 100 chars: {repr(html[:100])}"
        )
        return False
    
    # Check 2: No debe tener alto ratio de caracteres no imprimibles (binario)
    sample = html[:2000]
    non_printable = sum(1 for c in sample if ord(c) < 32 and c not in '\n\r\t')
    if len(sample) > 0 and non_printable / len(sample) > 0.15:
        logger.error(
            f"HTML integrity failed for {url}: {non_printable} non-printable chars in first 2000 "
            f"({non_printable/len(sample)*100:.1f}%). Likely binary/compressed data."
        )
        return False
    
    return True
```

---

### T3: Integrar _validate_html_integrity en audit()

**Archivo:** `modules/auditors/v4_comprehensive.py`
**Linea:** despues de la 370 (donde se asigna `page_html`)

Reemplazar:

```python
page_html = html_response.text if html_response and html_response.text else ""
if not page_html:
    logger.warning(f"Empty HTML response for {url}")
```

Con:

```python
page_html = html_response.text if html_response and html_response.text else ""
if page_html and not self._validate_html_integrity(page_html, url):
    logger.error(f"HTML response for {url} is corrupted/unreadable — falling back to empty")
    page_html = ""
elif not page_html:
    logger.warning(f"Empty HTML response for {url}")
```

Cuando el HTML es ilegible por CUALQUIER causa, se usa string vacio y los downstream checks
manejan la ausencia gracefully (ya lo hacen: brechas se marcan como "no detectado", no como falsos).

---

### T4: Test de regresion para integridad HTML

**Archivo:** `tests/test_html_integrity.py` (nuevo)

```python
"""Test de regresion: HTML ilegible nunca debe generar diagnosticos falsos.

Caso original: Brotli encoding no decodificado producia basura binaria que
el pipeline trataba como HTML valido, generando falsos positivos en brechas.
"""
import pytest


class TestHtmlIntegrity:
    """Valida _validate_html_integrity contra escenarios de HTML corrupto."""

    @pytest.fixture
    def auditor(self):
        from modules.auditors.v4_comprehensive import V4ComprehensiveAuditor
        return V4ComprehensiveAuditor.__new__(V4ComprehensiveAuditor)

    def test_brotli_binary_rejected(self, auditor):
        """HTML binario (Brotli sin decodificar) debe rechazarse."""
        # Simula basura binaria real del bug original
        binary_html = '\x1f\x8b\x08\x00\x00\x00\x00\x00' + 'A' * 500
        assert auditor._validate_html_integrity(binary_html, 'https://test.com') is False

    def test_empty_html_rejected(self, auditor):
        """HTML vacio o muy corto debe rechazarse."""
        assert auditor._validate_html_integrity('', 'https://test.com') is False
        assert auditor._validate_html_integrity('<p>hi</p>', 'https://test.com') is False

    def test_valid_html_accepted(self, auditor):
        """HTML real debe aceptarse."""
        valid = '<!DOCTYPE html><html><head><title>Test</title></head><body><div class="content">Hello</div></body></html>'
        assert auditor._validate_html_integrity(valid, 'https://test.com') is True

    def test_html_with_joinchat_accepted(self, auditor):
        """HTML con plugin Joinchat debe aceptarse (caso amaziliahotel.com)."""
        html = '<html><body><div class="joinchat" data-settings=\'{"telephone":"573104019049"}\'></div></body></html>'
        assert auditor._validate_html_integrity(html, 'https://test.com') is True

    def test_error_page_rejected(self, auditor):
        """Pagina de error/redirect sin estructura debe rechazarse."""
        # Cloudflare challenge page (JavaScript only, sin HTML real)
        js_only = '<script>challenge_platform()</script>' + 'x' * 500
        assert auditor._validate_html_integrity(js_only, 'https://test.com') is False
```

---

### T5: Verificacion directa del fix

Antes de ejecutar v4complete, verificar que HttpClient ahora entrega HTML real:

```bash
venv/Scripts/python.exe -c "
import sys; sys.path.insert(0, '.')
from modules.utils.http_client import HttpClient
r, _ = HttpClient().get('https://amaziliahotel.com/')
html = r.text if r else ''
print('Length:', len(html))
print('joinchat:', ('joinchat' in html.lower()))
print('class= count:', html.lower().count('class='))
print('Content-Encoding:', r.headers.get('Content-Encoding', 'none'))
print('Has <html:', ('<html' in html.lower()))
"
```

Esperado: Length ~236000, joinchat=True, class= ~694, Has <html=True.

---

### T6: Tests de regresion

```bash
venv/Scripts/python.exe -m pytest tests/test_html_integrity.py -v
venv/Scripts/python.exe -m pytest tests/ -v --tb=short -k "whatsapp or region or pain or coherence"
```

---

### T7: Validacion E2E completa

```bash
venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/
```

Verificar en el diagnostico generado:

| Check | Esperado | Antes (roto) |
|-------|----------|--------------|
| BRECHA 2 "Sin WhatsApp" | **NO aparece** | Aparecia (falso positivo) |
| whatsapp_verified score | > 0 (0.5 o 1.0) | 0.000 |
| Region | "Eje Cafetero" | "nacional" |
| Open Graph | detectado (si existe) | False (siempre) |
| Metadata CMS defaults | detectado (si aplica) | No detectaba |
| Coherence score | >= 0.80 | 0.84 |

### T8: Verificar fixes previos contra HTML real

Confirmar que los fixes de FASE-A/E ahora tienen efecto:

- W0: `_detect_whatsapp_from_html()` encuentra "joinchat" → whatsapp_html_detected=True
- W1: ValidationSummary recibe campo whatsapp_number via rama elif
- W2: pain_solution_mapper NO genera pain no_whatsapp_visible
- W4: coherence_validator da score parcial (0.5+) en whatsapp_verified
- R1: Region inferida desde GBP address → "eje_cafetero"

---

## Criterios de Completitud

- [ ] T1: brotli instalada en venv
- [ ] T2: _validate_html_integrity() implementada en v4_comprehensive.py
- [ ] T3: audit() usa _validate_html_integrity para rechazar HTML ilegible
- [ ] T4: test_html_integrity.py creado, 5 tests pasan
- [ ] T5: HTML de amaziliahotel.com contiene "joinchat" y "class="
- [ ] T6: Tests de regresion pasan (sin regresion)
- [ ] T7: v4complete ejecuta sin crashes
- [ ] T7: BRECHA 2 "Sin WhatsApp" NO aparece en diagnostico generado
- [ ] T7: Region muestra "Eje Cafetero" (no "nacional")
- [ ] T7: Coherence >= 0.80
- [ ] T8: whatsapp_verified score > 0
- [ ] log_phase_completion.py ejecutado

---

## Archivos a Modificar

| Archivo | Cambio | Zona |
|---------|--------|------|
| `modules/auditors/v4_comprehensive.py` | Nuevo metodo `_validate_html_integrity()` + integracion en `audit()` | Clase auditor |
| `tests/test_html_integrity.py` | Nuevo archivo, 5 tests de regresion | N/A |

**Comando:** `venv/Scripts/pip.exe install brotli`

**Riesgo:** MINIMO. Metodo nuevo + 2 lineas de integracion. Sin impacto en modulos existentes.

---

## Post-Ejecucion

- Marcar checklist en `06-checklist-implementacion.md`
- Ejecutar `log_phase_completion.py --fase FASE-F`
- Actualizar `09-documentacion-post-proyecto.md`
- Actualizar contexto `whatsapp_false_positive.md` con resultado E2E
- Agregar `brotli` a requirements.txt o requirements-dev.txt si existe
