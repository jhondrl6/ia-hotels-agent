# AUDITORIA FASE-2-B: Verificacion E2E v4complete Termales
## URL: http://www.termales.com.co/ | Fecha: 2026-05-08
### Auditoria post-ejecucion contra codigo vivo + evidencia fase-2-B
### Version: 1.0.0 | Estado: BLOQUEANTE — 0/7 metricas pasan

---

## VEREDICTO EJECUTIVO

La ejecucion de FASE-2-B (verificacion E2E post-fixes FASE-1-A, 1-B, 2-A) fue **NO EFECTIVA**. De 7 metricas de exito definidas en `PLAN-REFACTOR-TERMALES-20260508.md §Metricas de Exito`, **NINGUNA funciona correctamente en produccion**. La release 4.43.0 se cerro sobre fixes rotos.

> ⚠️ **ALERTA CRITICA**: El `06-checklist-implementacion.md` documenta FASE-2-B como "PARCIAL — 2/7 metricas". Esta auditoria demuestra que el verdadero score es **0/7**. Los fixes existen en disco pero no estan cableados al pipeline v4complete, o sus implementaciones son insuficientes para los casos reales de Termales.

---

## EVIDENCIA DE REFERENCIA

### Archivos de evidencia (FASE-2-B)
```
evidence/fase-2-B/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260508_203338.md   → Diagnostico generado
evidence/fase-2-B/02_PROPUESTA_COMERCIAL_20260508_203347.md         → Propuesta con bugs
evidence/fase-2-B/asset_generation_report.json                     → 6 assets, confidence=0.5
evidence/fase-2-B/audit_report_20260508_203332.json                → Schema: false, WhatsApp: estimated
evidence/fase-2-B/coherence_validation.json                        → promised_assets_exist: 1.0 (FALSO)
evidence/fase-2-B/gate_report_20260508_203357.json                 → 3 WARNINGs, present_in_production: []
evidence/fase-2-B/ESTIMATED_informe_mensual_20260508_203338.md     → Tabla vacia
evidence/fase-2-B/ESTIMATED_llms_20260508_203338.txt               → [PENDING_ONBOARDING]
evidence/fase-2-B/geo_flow_result.json                             → 10 geo assets generados
```

### Archivos de codigo auditados
```
modules/commercial_documents/v4_proposal_generator.py:1103-1121   → _preprocess_conditionals (FIX-1)
modules/commercial_documents/coherence_validator.py:113-141        → validate() NO pasa generated_assets (FIX-2)
modules/commercial_documents/coherence_validator.py:494-550        → _check_promised_assets_exist (logica OK, API rota)
modules/asset_generation/monthly_report_generator.py:236-266       → _generate_assets_table (logica OK, cable roto)
modules/postprocessors/content_scrubber.py:274-295                 → _fix_pending_markers regex restrictivo (FIX-4)
modules/quality_gates/publication_gates.py:810-826                 → SitePresenceChecker invocacion + except (FIX-5)
modules/asset_generation/site_presence_checker.py                  → Logica de deteccion WhatsApp/Schema (no auditada en detalle)
```

---

## METRICAS DE EXITO — RESULTADO DETALLADO

### M1: Sin `{{if}}...{{endif}}` en propuesta comercial
| Campo | Valor |
|-------|-------|
| Esperado | 0 ocurrencias de `{{if` en propuesta |
| Real | `grep -c "{{if" evidence/fase-2-B/02_PROPUESTA_*.md` → **1** (linea 114) |
| Bloque crudo en output | `{{if financial_evidence_tier == "A" or financial_evidence_tier == "B"}}` |

**Causa raiz (FIX-1 insuficiente)**:
`v4_proposal_generator.py:1112`:
```python
pattern = r'\{\{if\s+(\w+)\s*==\s*"([^"]+)"\}\}(.*?)\{\{endif\}\}'
```
El regex solo captura `var == "value"` (una sola condicion). El template V6 usa `tier == "A" or tier == "B"`. El `or` rompe el match. El blocondicional viaja crudo al documento final.

**Fix requerido**: El pre-procesador debe manejar expresiones booleanas (`or`, `and`), o el template debe simplificarse, o debe usarse un motor de templates real (Jinja2, mustache) en vez de regex casero.

---

### M2: Coherence refleja assets REALMENTE generados
| Campo | Valor |
|-------|-------|
| Esperado | `promised_assets_exist.score` refleje assets faltantes (~0.57 si 3/7 faltan) |
| Real | `coherence_validation.json` → `promised_assets_exist: score=1.0, passed=true` |
| Mensaje | "Todos los assets prometidos estan implementados (7 servicios verificados via PROPOSAL_SERVICE_TO_ASSET)" |

**Causa raiz (FIX-2 fantasma)**:
`coherence_validator.py:141`:
```python
self.checks.append(self._check_promised_assets_exist(assets, diagnostic))
```
El tercer argumento (`generated_assets`) NUNCA se pasa. La funcion `_check_promised_assets_exist` SI tiene logica para usar `generated_assets` (L529-533), pero `validate()` no la invoca con ese parametro.

**Evidencia de codigo muerto**:
L498: `generated_assets: Optional[Dict[str, Any]] = None`  ← parametro definido
L141: `self._check_promised_assets_exist(assets, diagnostic)`  ← parametro omitido

**Fix requerido**:
1. `validate()` debe aceptar `generated_assets: Optional[Dict] = None` y pasarlo.
2. El caller en el pipeline (v4complete orchestrator) debe extraer `generated_assets` de `asset_generation_report.json` y pasarlo a `validate()`.

---

### M3: monthly_report muestra tabla dinamica basada en asset_generation_report.json
| Campo | Valor |
|-------|-------|
| Esperado | Tabla con 6 assets reales, estados basados en `can_use` |
| Real | `ESTIMATED_informe_mensual_20260508_203338.md:111` → "No se generaron assets en esta ejecucion" |

**Causa raiz (FIX-3 desacoplado)**:
`monthly_report_generator.py:253-254`:
```python
if asset_report_path is None and output_dir:
    asset_report_path = os.path.join(output_dir, 'asset_generation_report.json')
```
`output_dir` viene de `hotel_data.get("output_dir", "")`. Si el pipeline no inyecta `output_dir` en `hotel_data`, el path queda vacio → no encuentra JSON → tabla vacia.

**Fix requerido**:
El orquestador v4complete debe pasar `asset_report_path` explicitamente al generador, o asegurar que `hotel_data["output_dir"]` contenga la ruta real del pipeline.

---

### M4: Sin `[PENDING_*]` en documentos finales
| Campo | Valor |
|-------|-------|
| Esperado | 0 ocurrencias de `[PENDING_` en evidence/fase-2-B/ |
| Real | `grep -r "\[PENDING_" evidence/fase-2-B/` → **1** (`ESTIMATED_llms_20260508_203338.txt:3`) |

**Causa raiz (FIX-4 regex restrictivo)**:
`content_scrubber.py:284`:
```python
pattern = r'\[PENDING_[A-Z_]+\]'
```
El marcador real es `[PENDING_ONBOARDING: usp/description]`. Entre `ONBOARDING` y `]` hay `: usp/description`, por lo que el regex (que espera `]` inmediatamente despues del nombre) nunca coincide.

**Fix requerido**:
Cambiar regex a `r'\[PENDING_[A-Z_]+[^\]]*\]'` o `r'\[PENDING_[A-Z_]+.*?'` para tolerar contenido adicional dentro del marcador.

---

### M5: WhatsApp detectado correctamente
| Campo | Valor |
|-------|-------|
| Esperado | `gate_report` marca `whatsapp_button` como `present_in_production` |
| Real | `gate_report:135-138` → `"presence_status": "not_exists"`, `present_in_production: []` |

**Causa raiz (FIX-5 solo endurecio el `except`)**:
`publication_gates.py:817-826`: El `except Exception` ahora retorna `presence_status: 'unknown'` (FIX-5 aplicado). PERO el `SitePresenceChecker` se ejecuta sin lanzar excepcion; simplemente no encuentra el boton. El resultado es `"presence_verified": true, "presence_status": "not_exists"`.

**Evidencia del sitio real** (confirmada en ANALISIS v2.0.0):
- WhatsApp real: `wa.me/573012674459`
- Clases CSS detectadas: `whatsapp-button`, `icon-whatsapp` (footer)
- El pipeline reporta `"not_exists"` → falso negativo

**Fix requerido**:
Auditar `site_presence_checker.py` contra el HTML real de termales.com.co. Posibles causas:
1. Selector CSS busca `.whatsapp-button` pero el boton esta en footer con clase diferente.
2. Boton cargado via JavaScript (no en HTML estatico) → necesita renderizado.
3. Heuristica de deteccion de numero (busca `wa.me/` o `api.whatsapp.com`) no alcanza.

**Accion recomendada**: Ejecutar `browser_navigate` + `browser_console` para obtener el DOM real y comparar con los selectores del checker.

---

### M6: Schema detectado correctamente
| Campo | Valor |
|-------|-------|
| Esperado | `audit_report` → `hotel_schema_detected: true` |
| Real | `audit_report:6-7` → `hotel_schema_detected: false, hotel_schema_valid: false` |

**Causa raiz (misma que M5)**:
El sitio tiene schema JSON-LD (confirmado por navegador: `ld_json_count: 1`), pero el pipeline no lo detecta. `audit_report:12` dice `org_schema_detected: true` — detecta Organization pero no Hotel schema.

**Fix requerido**:
El checker debe considerar `Organization` schema como valido (o al menos parcial) para hoteles que no tienen `Hotel` schema explicito. O debe detectar que SI hay schema presente y no reportar "no tiene schema" al cliente.

---

### M7: Sin placeholders genericos en documentos finales
| Campo | Valor |
|-------|-------|
| Esperado | 0 ocurrencias de `+57 300 000 0000` en propuesta |
| Real | `grep -c "+57 300 000 0000" evidence/fase-2-B/02_PROPUESTA_*.md` → **1** (linea 228) |

**Causa raiz (no hubo fix)**:
El telefono real del GBP es `(606) 3653421` (`audit_report:25`). El WhatsApp real es `+57 301 267 4459` (confirmado en sitio). La propuesta muestra `+57 300 000 0000` (placeholder generico del template).

**Contexto**: Pipeline Tier C sin onboarding → `hotel_data` no tiene telefono real. El template usa fallback generico.

**Fix requerido**:
Opcion A: Cablear `phone_gbp` del `audit_report.json` a `hotel_data` cuando `phone_web` es null.
Opcion B: Agregar regla al ContentScrubber para detectar placeholders telefonicos genericos (`+57 300 000 0000`, `+1 000 000 0000`).
Opcion C (recomendada): Ambas. El pipeline debe enriquecer hotel_data con GBP data, Y el scrubber debe ser la ultima linea de defensa.

---

## CAUSAS RAIZ CONSOLIDADAS

```
CLIENTE RECIBE DOCUMENTO CON ERRORES (FASE-2-B)
│
├── R1: Regex de conditionals no maneja expresiones compuestas [FIX-1 insuficiente]
│   └── v4_proposal_generator.py:1112 — pattern solo captura `var == "val"`
│       └── Template V6 usa `tier == "A" or tier == "B"` → viaja crudo
│
├── R2: Coherence validator tiene codigo muerto [FIX-2 fantasma]
│   └── _check_promised_assets_exist() acepta generated_assets, pero
│       validate() nunca lo pasa (L141 omite 3er argumento)
│       └── Coherence siempre reporta 1.0 (catalogo estatico = todo implementado)
│
├── R3: monthly_report desacoplado del pipeline [FIX-3 cable roto]
│   └── _generate_assets_table() OK, pero hotel_data["output_dir"] vacio
│       └── Tabla vacia: "No se generaron assets en esta ejecucion"
│
├── R4: Scrubber regex no tolera metadata en marcadores [FIX-4 restrictivo]
│   └── pattern = r'\[PENDING_[A-Z_]+\]' no captura `[PENDING_X: detalle]`
│       └── [PENDING_ONBOARDING: usp/description] pasa sin bloqueo
│
├── R5: SitePresenceChecker logica de deteccion rota [FIX-5 solo manejo de errores]
│   └── except Exception ahora retorna 'unknown', pero el checker NO FALLA
│       └── Simplemente no encuentra WhatsApp/Schema → "not_exists" falso
│
├── R6: Datos de contacto reales no llegan a propuesta [SIN FIX]
│   └── Tier C sin onboarding → hotel_data sin telefono → placeholder generico
│       └── phone_gbp existe en audit_report pero no se usa
```

---

## SOLUCIONES PARA FASE-2-PATCH

### Prioridad 1 — Bugs que llegan al cliente

**PATCH-1: Template conditionals con expresiones compuestas**
- Archivo: `modules/commercial_documents/v4_proposal_generator.py:1103-1121`
- Problema: Regex `{{if\s+(\w+)\s*==\s*"([^"]+)"}}` no maneja `or`.
- Solucion exploratoria (2 opciones):
  - **Opcion A (rapida)**: Pre-procesar `or` dividiendo en bloques separados antes del regex. Ej: `{{if a == "X" or a == "Y"}}` → dividir en 2 conditionals individuales con mismo bloque.
  - **Opcion B (robusta)**: Reemplazar regex por parser con `ast.parse()` o libreria `pyparsing` que evalue expresiones booleanas con variables de `data`.
  - **Opcion C (arquitectura)**: Migrar template V6 a Jinja2 real. Cambio mas grande pero elimina la deuda tecnica permanentemente.
- Recomendacion: Opcion A para patch inmediato, Opcion C para roadmap tecnico.

**PATCH-2: Cablear generated_assets en coherence validator**
- Archivos: `modules/commercial_documents/coherence_validator.py:113-141` + caller en pipeline v4complete
- Cambio:
  1. `validate()` recibe `generated_assets: Optional[Dict[str, Any]] = None`
  2. L141: `self._check_promised_assets_exist(assets, diagnostic, generated_assets)`
  3. En el pipeline (buscar donde se instancia `CoherenceValidator`), pasar `asset_generation_report["generated_assets"]`
- Verificacion: Re-ejecutar v4complete → coherence_validation.json debe mostrar `promised_assets_exist.score < 1.0` si faltan assets.

**PATCH-3: Cablear asset_report_path en monthly_report**
- Archivo: Orquestador v4complete (buscar invocacion de `MonthlyReportGenerator.generate()`)
- Cambio: Pasar `asset_report_path` explicitamente con la ruta absoluta al `asset_generation_report.json` generado en esta ejecucion.
- Alternativa: Asegurar que `hotel_data["output_dir"]` se setea antes de invocar el generador.

**PATCH-4: Scrubber regex tolerante a metadata en marcadores**
- Archivo: `modules/postprocessors/content_scrubber.py:284`
- Cambio: `pattern = r'\[PENDING_[A-Z_]+[^\]]*\]'`
- Test: Agregar caso `test_scrub_detects_pending_with_metadata()` con input `[PENDING_ONBOARDING: usp/description]`.

**PATCH-5: SitePresenceChecker contra DOM real**
- Archivo: `modules/asset_generation/site_presence_checker.py`
- Accion requerida: Navegar termales.com.co con browser, obtener DOM completo, comparar con selectores/heuristicas del checker.
- Posibles ajustes:
  - WhatsApp: ampliar busqueda a `icon-whatsapp`, `wa.me/` en hrefs, `api.whatsapp.com`
  - Schema: contar cualquier schema JSON-LD como "schema presente", no solo `Hotel`
- Verificacion: Re-ejecutar v4complete → `gate_report` debe tener `present_in_production` con whatsapp_button y schema_hotel.

**PATCH-6: Enriquecer hotel_data con GBP phone**
- Archivo: Orquestador v4complete o `modules/asset_generation/proposal_generator.py`
- Cambio: Si `hotel_data.get("phone")` es vacio/null, usar `audit_report["gbp"]["phone"]`.
- Tambien: Agregar regla al ContentScrubber (Rule 7?) para detectar `+57 300 000 0000` como placeholder telefonico.

---

## METRICAS DE EXITO PARA POST-PATCH

1. `grep -c "{{if" evidence/fase-NEXT/02_PROPUESTA_*.md` → **0**
2. `coherence_validation.json` → `promised_assets_exist.score` refleja gaps reales (<1.0 si faltan assets)
3. `ESTIMATED_informe_mensual_*.md` muestra tabla con 6 assets y estados reales (no vacia)
4. `grep -r "\[PENDING_" evidence/fase-NEXT/` → **0**
5. `gate_report_*.json` → `present_in_production` contiene `whatsapp_button`
6. `audit_report_*.json` → `hotel_schema_detected` = **true** (o al menos no falso negativo)
7. `grep -c "+57 300 000 0000" evidence/fase-NEXT/02_PROPUESTA_*.md` → **0**

**Veredicto post-patch**:
- 7/7 → EFECTIVA → Permitir release
- 4-6 → PARCIAL → Otra iteracion PATCH
- <4 → NO EFECTIVA → Re-auditar causas raiz

---

## MACRO-FASES SUGERIDAS

```
FASE-2-PATCH — Correccion de fixes rotos (6 patches)
├── PATCH-1: Template conditionals con "or" (v4_proposal_generator)
├── PATCH-2: Cablear generated_assets en coherence (validator + caller)
├── PATCH-3: Cablear asset_report_path en monthly_report (orquestador)
├── PATCH-4: Scrubber regex tolerante (content_scrubber)
├── PATCH-5: SitePresenceChecker DOM real (site_presence_checker + gates)
├── PATCH-6: Enriquecer phone desde GBP (orquestador o scrubber)
└── Verificacion: Re-ejecutar v4complete → 7/7 metricas
```

---

## PROXIMO PASO — COPY-PASTE PARA NUEVA SESION

```
Carga .opencode/context/AUDITORIA_FASE-2-B_TERMALES_20260508.md (v1.0.0).
Siguiendo iah-cli-context-audit-to-plan y phased_project_executor.md,
disenia el plan de intervencion en .opencode/plans/FASE-2-PATCH-TERMALES.md
con los 6 patches listados arriba, prompts por patch, dependencias,
checklist y R3 scope. No implementes aun — solo diseña el plan.
```

---

*Auditoria ejecutada: 2026-05-08*
*Evidencia base: evidence/fase-2-B/ (timestamps 20260508_2033xx)*
*Contexto original: ANALISIS_V4COMPLETE_TERMALES_20260508.md (v2.0.0)*
*Plan maestro: PLAN-REFACTOR-TERMALES-20260508.md*
*6 patches requeridos | 0/7 metricas actuales | Target: 7/7*
