# PLAN-FASE-2-PATCH-TERMALES-20260508

> **Origen**: AUDITORIA_FASE-2-B_TERMALES_20260508.md (v1.0.0)
> **Veredicto ejecutivo**: 0/7 métricas pasan en producción. 6 patches requeridos.
> **Creado**: 2026-05-08 | **Versión plan**: v1.0.0
> **Tipo**: PATCH (bugfixes, sin cambios arquitectónicos) → Sin FASE-RELEASE

---

## Objetivo

Restaurar las 7 métricas de éxito definidas en `PLAN-REFACTOR-TERMALES-20260508.md §Métricas de Exito`,
corrigiendo los 6 fixes rotos/deficientes de FASE-2-B.

**Target**: 7/7 métricas pasan → v4complete efectivo.

---

## Arquitectura de Fases (R3-compliant)

```
FASE-2-PATCH-A ──→ FASE-2-PATCH-B ──→ FASE-2-PATCH-C
  (3 fixes code)     (3 fixes orch)     (v4complete + verify)
```

| Fase | Fixes | Tareas | Comandos largos | R3 |
|------|-------|--------|-----------------|-----|
| FASE-2-PATCH-A | PATCH-1, PATCH-2, PATCH-4 | 3 | 0 | ✓ |
| FASE-2-PATCH-B | PATCH-3, PATCH-5, PATCH-6 | 3 | 0 | ✓ |
| FASE-2-PATCH-C | v4complete + verificación + docs | 2 | 1 | ✓ |

**Dependencias**: A → B (coherence wiring en A debe estar listo antes de que B toque el orchestrator). B → C (todos los fixes deben estar en su lugar antes de ejecutar v4complete).

---

## FASE-2-PATCH-A: Fixes locales de código (3 patches)

### PATCH-1: Template conditionals con expresiones compuestas

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py:1103-1121`

**Problema**: Regex `r'{{if\s+(\w+)\s*==\s*"([^"]+)"}}'` solo captura `var == "val"`. El template V6 L111 usa `{{if financial_evidence_tier == "A" or financial_evidence_tier == "B"}}`. El `or` rompe el match → el bloque viaja crudo al documento.

**Solución recomendada (Opción A — rápida)**:
Pre-procesar `or` dividiendo en bloques separados antes del regex. Para `{{if a == "X" or a == "Y"}}...{{endif}}`, expandir a:
```
{{if a == "X"}}...{{endif}}
{{if a == "Y"}}...{{endif}}
```

Si ambos evalúan true, el bloque aparece duplicado (aceptable para templates pequeños). Si se necesita más robustez, implementar Opción B (parser con AST o evaluación dinámica).

### PATCH-2: Cablear generated_assets en coherence validator

**Archivos**: 
- `modules/commercial_documents/coherence_validator.py:113-141`
- Caller en pipeline v4complete (main.py)

**Problema**: `validate()` no acepta `generated_assets`. `_check_promised_assets_exist()` (L494) SÍ tiene el parámetro `generated_assets` en su firma y lógica (L529-533), pero `validate()` lo omite en L141: `self._check_promised_assets_exist(assets, diagnostic)` en vez de `(assets, diagnostic, generated_assets)`.

**Cambios**:
1. `validate()` acepta `generated_assets: Optional[Dict[str, Any]] = None`
2. L141: `self._check_promised_assets_exist(assets, diagnostic, generated_assets)`
3. En el pipeline (buscar donde se instancia CoherenceValidator), pasar `asset_generation_report["generated_assets"]`

### PATCH-4: Scrubber regex tolerante a metadata en marcadores

**Archivo**: `modules/postprocessors/content_scrubber.py:284`

**Problema**: `pattern = r'\[PENDING_[A-Z_]+\]'` no captura `[PENDING_ONBOARDING: usp/description]` porque hay texto entre `ONBOARDING` y `]`.

**Cambio**: `pattern = r'\[PENDING_[A-Z_]+[^\]]*\]'`

---

## FASE-2-PATCH-B: Fixes de orquestador + investigación (3 patches)

### PATCH-3: Cablear asset_report_path en monthly_report

**Archivos**:
- `modules/asset_generation/monthly_report_generator.py:236-266` (lógica OK, cable roto)
- Orquestador v4complete (donde se invoca `MonthlyReportGenerator.generate()`)

**Problema**: `_generate_assets_table()` busca `asset_generation_report.json` en `output_dir` que viene de `hotel_data["output_dir"]`. Si el pipeline no inyecta `output_dir` en `hotel_data`, el path queda vacío → tabla vacía.

**Cambio**: Pasar `asset_report_path` explícitamente al `generate()` con la ruta absoluta al `asset_generation_report.json`.

### PATCH-5: SitePresenceChecker contra DOM real

**Archivos**:
- `modules/asset_generation/site_presence_checker.py:413-437` (`_check_html_element`)
- `modules/quality_gates/publication_gates.py:800-826`

**Problema**: `_check_html_element()` busca `fallback_text` SOLO en `soup.text.lower()` (texto visible). Los enlaces WhatsApp (`href="wa.me/..."`) y las clases CSS (`icon-whatsapp`) NUNCA se detectan porque el texto del href no está en `soup.text`.

**Investigación requerida**: Navegar `termales.com.co` con browser para obtener DOM real, confirmar selectores.

**Cambios propuestos**:
1. Ampliar `_check_html_element` para buscar en atributos `href` (patrones `wa.me/`, `api.whatsapp.com`)
2. Buscar en clases CSS (`whatsapp-button`, `icon-whatsapp`, `joinchat`)
3. Para Schema: considerar `Organization` schema como válido para hoteles sin `Hotel` schema explícito

### PATCH-6: Enriquecer hotel_data con GBP phone

**Archivos**:
- `modules/commercial_documents/templates/propuesta_v6_template.md:197` (hardcode)
- Orquestador v4complete

**Problema**: Template tiene `WhatsApp: +57 300 000 0000` hardcodeado. No hay código que wire `audit_report["gbp"]["phone"]` al template.

**Cambio**: 
1. En el pipeline, si `hotel_data.get("phone")` es null/placeholder, usar `audit_report["gbp"]["phone"]`
2. Agregar regla al ContentScrubber para detectar `+57 300 000 0000` como placeholder telefónico

---

## FASE-2-PATCH-C: Verificación E2E con v4complete

**Comando**: `./venv/Scripts/python.exe main.py v4complete --url http://www.termales.com.co/`

**Propósito**: Determinar si la implementación de PATCH-1 a PATCH-6 fue efectiva.

### Métricas de Éxito (Post-Patch)

| # | Métrica | Verificación | Target |
|---|---------|-------------|--------|
| M1 | Sin `{{if}}...{{endif}}` crudos | `grep -c "{{if" evidence/fase-2-PATCH-C/02_PROPUESTA_*.md` | 0 |
| M2 | Coherence refleja assets reales | `jq '.promised_assets_exist.score' coherence_validation.json` | < 1.0 si faltan assets |
| M3 | monthly_report tabla dinámica | Verificar que la tabla muestra assets con estados reales | No vacía |
| M4 | Sin `[PENDING_*]` en documentos | `grep -r "\[PENDING_" evidence/fase-2-PATCH-C/` | 0 |
| M5 | WhatsApp detectado | `gate_report.json` → `present_in_production` contiene `whatsapp_button` | Presente |
| M6 | Schema detectado | `audit_report.json` → `hotel_schema_detected` = true | true |
| M7 | Sin placeholder telefónico | `grep -c "+57 300 000 0000" evidence/fase-2-PATCH-C/02_PROPUESTA_*.md` | 0 |

### Veredicto

| Score | Clasificación | Acción |
|-------|--------------|--------|
| 7/7 | EFECTIVA | Release ready |
| 4-6 | PARCIAL | Otra iteración PATCH |
| <4 | NO EFECTIVA | Re-auditar causas raíz |

---

## Evidencia Post-Ejecución (OBLIGATORIO)

Inmediatamente después de v4complete en FASE-2-PATCH-C:

```bash
mkdir -p evidence/fase-2-PATCH-C
cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/fase-2-PATCH-C/
cp output/v4_complete/02_PROPUESTA_*.md evidence/fase-2-PATCH-C/
cp output/v4_complete/{hotel_id}/v4_audit/*.json evidence/fase-2-PATCH-C/
```

---

## Prompt Copy-Paste para Iniciar

```
Carga .opencode/plans/05-prompt-inicio-sesion-fase-2-PATCH-A.md.
Siguiendo phased_project_executor.md, ejecuta FASE-2-PATCH-A:
PATCH-1 (template conditionals OR) + PATCH-2 (coherence wiring) + PATCH-4 (scrubber regex).
No ejecutes v4complete. Implementa, testea, y ejecuta log_phase_completion.py.
```
