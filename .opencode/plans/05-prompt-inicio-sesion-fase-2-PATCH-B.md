# 05-prompt-inicio-sesion-fase-2-PATCH-B

> **Plan maestro**: `PLAN-FASE-2-PATCH-TERMALES-20260508.md`
> **Fase**: 2 de 3 | **Tipo**: Implementación + investigación | **Tareas**: 3 | **Comandos largos**: 0

---

## Contexto

FASE-2-PATCH-A completada (PATCH-1, PATCH-2, PATCH-4). Ahora corregimos los 3 fixes que requieren:
- Cablear el orquestador v4complete (PATCH-3, PATCH-6)
- Investigar el DOM real de termales.com.co (PATCH-5)

**Contexto completo**: `.opencode/context/AUDITORIA_FASE-2-B_TERMALES_20260508.md`
**Fase anterior**: `.opencode/plans/05-prompt-inicio-sesion-fase-2-PATCH-A.md` (asumir ✅ completada)

---

## Tareas Específicas

### T1: PATCH-3 — Cablear asset_report_path en monthly_report

**Archivos**:
- `modules/asset_generation/monthly_report_generator.py:236-266` (lógica OK, solo verificar)
- `main.py` (orquestador v4complete — donde se invoca `MonthlyReportGenerator.generate()`)

**Problema**: `_generate_assets_table()` busca `asset_generation_report.json` en `output_dir` de `hotel_data["output_dir"]`. Si el pipeline no inyecta `output_dir`, el path queda vacío → tabla vacía: "No se generaron assets en esta ejecucion".

**Cambio**: Localizar en `main.py` dónde se llama `MonthlyReportGenerator.generate(hotel_data)` y pasar `asset_report_path` explícitamente:

```python
# Buscar: monthly_gen.generate(hotel_data, ...)
# Cambiar a:
asset_report_path = os.path.join(output_dir, hotel_id, "v4_audit", "asset_generation_report.json")
monthly_report = monthly_gen.generate(
    hotel_data, 
    asset_report_path=asset_report_path
)
```

**Verificación**: `grep -rn "MonthlyReportGenerator\|monthly_report_generator" main.py --include="*.py"` para encontrar todos los puntos de invocación.

---

### T2: PATCH-5 — SitePresenceChecker contra DOM real

**Archivos**:
- `modules/asset_generation/site_presence_checker.py:413-437` (`_check_html_element`)
- `modules/quality_gates/publication_gates.py:800-826`

**Problema**: `_check_html_element()` busca `fallback_text` SOLO en `soup.text.lower()`. Los enlaces WhatsApp (`href="wa.me/..."`) y clases CSS NO se detectan. Resultado: WhatsApp y Schema reportados como `not_exists` cuando SÍ existen en el sitio.

**PASO 1 — Investigar DOM real** (OBLIGATORIO antes de implementar):

```
Usa browser_navigate("http://www.termales.com.co/")
Luego browser_console con expresión:
  document.querySelectorAll('[href*="wa.me"], [href*="api.whatsapp"], [href*="whatsapp"], [class*="whatsapp"], [class*="joinchat"]')
  
También:
  document.querySelectorAll('script[type="application/ld+json"]')
```

Esto confirmará:
- Qué selectores CSS están presentes en el sitio real
- Si el botón WhatsApp está en HTML estático o cargado vía JS
- Qué tipos de Schema JSON-LD existen

**PASO 2 — Ampliar _check_html_element**:

Basado en los hallazgos del DOM real, ampliar el método para:

```python
def _check_html_element(self, site_url, search_texts):
    """Verifica presencia de elemento en HTML (texto + atributos + clases)."""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(site_url, headers=headers, timeout=self.timeout)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        found_texts = []
        
        # 1. Buscar en texto visible (existente)
        for text in search_texts:
            if text.lower() in soup.text.lower():
                found_texts.append(text)
        
        # 2. Buscar en atributos href
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if any(pattern in href.lower() for pattern in ['wa.me', 'api.whatsapp.com', 'whatsapp']):
                found_texts.append(f"whatsapp_link:{href}")
                break
        
        # 3. Buscar en clases CSS
        for element in soup.find_all(class_=True):
            classes = ' '.join(element.get('class', []))
            if any(pattern in classes.lower() for pattern in ['whatsapp', 'joinchat']):
                found_texts.append(f"css_class:{classes}")
                break
        
        return {
            "found": len(found_texts) > 0,
            "matched_texts": found_texts
        }
    except Exception:
        return {"found": False}
```

**PASO 3 — Schema detection**: En `_check_schema_exists()` (L353-393), considerar `Organization` o `LocalBusiness` como válido para hoteles sin `Hotel` schema. Ya existe lógica parcial en L364-365:

```python
if schema_type == "Hotel":
    target_types.extend(["LodgingBusiness", "LocalBusiness"])
```

Verificar que esto funciona para el caso real de Termales (que tiene `Organization` schema). Si el sitio tiene `Organization` pero no `Hotel`/`LodgingBusiness`/`LocalBusiness`, reportar al menos como `EXISTS_WITH_ISSUES` en vez de `NOT_EXISTS`.

---

### T3: PATCH-6 — Enriquecer hotel_data con GBP phone

**Archivos**:
- `modules/commercial_documents/templates/propuesta_v6_template.md:197` (hardcode `+57 300 000 0000`)
- `main.py` (donde se prepara `hotel_data` antes de generar la propuesta)
- `modules/postprocessors/content_scrubber.py` (nueva regla opcional)

**Problema**: Template tiene teléfono placeholder hardcodeado. Tier C sin onboarding → `hotel_data` sin phone real → placeholder en propuesta final. El `audit_report.json` SÍ tiene `gbp.phone` (ej: `(606) 3653421`).

**Cambio**:

1. En `main.py`, antes de invocar el generador de propuesta, enriquecer `hotel_data`:
```python
# Si hotel_data no tiene phone real, usar GBP phone del audit_report
if not hotel_data.get("phone") or hotel_data.get("phone") == "+57 300 000 0000":
    gbp_phone = audit_report.get("gbp", {}).get("phone", "")
    if gbp_phone:
        hotel_data["phone"] = gbp_phone
```

2. En `propuesta_v6_template.md:197`, cambiar el placeholder hardcodeado por variable:
```markdown
WhatsApp: ${phone}
```

O mantener el fallback, pero asegurarse que `phone` llega al template desde `hotel_data`.

3. (Opcional, mejora defensiva) Agregar regla al ContentScrubber para detectar `+57 300 000 0000` como placeholder telefónico genérico.

---

## Post-Ejecución

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# 1. Ejecutar tests
venv/Scripts/python.exe -m pytest tests/asset_generation/test_monthly_report_generator.py -x -q
venv/Scripts/python.exe -m pytest tests/asset_generation/test_site_presence_checker.py -x -q
venv/Scripts/python.exe -m pytest tests/commercial_documents/ -x -q

# 2. Registrar fase
venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-2-PATCH-B \
    --desc "PATCH-3 (monthly report asset_report_path) + PATCH-5 (SitePresenceChecker HTML real) + PATCH-6 (GBP phone enrichment)" \
    --archivos-mod "modules/asset_generation/site_presence_checker.py,modules/asset_generation/monthly_report_generator.py,main.py,modules/commercial_documents/templates/propuesta_v6_template.md" \
    --tests "3" \
    --check-manual-docs

# 3. Actualizar checklist
```

---

## Criterios de Completitud

- [x] PATCH-3: `monthly_report` recibe `asset_report_path` explícito del orchestrator
- [x] PATCH-5: DOM real de termales.com.co investigado con browser
- [x] PATCH-5: `_check_html_element` busca en href + clases CSS + texto
- [x] PATCH-5: Schema detection tolera Organization/LocalBusiness para hoteles
- [x] PATCH-6: `hotel_data["phone"]` se enriquece con GBP phone
- [x] PATCH-6: Template propuesta usa variable dinámica para teléfono
- [x] `log_phase_completion.py` ejecutado
- [x] Plan actualizado

---

## Restricciones

- **NO ejecutar v4complete** en esta fase
- Máximo 60 iteraciones
- Browser investigation (T2 PASO 1) es OBLIGATORIA antes de implementar
