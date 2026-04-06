# Plan: FIX CRITICO analytics_data + Analisis de Assets de Analytics

## ID: ANALYTICS-FIX-01
## Version: 2.0 — 2026-04-02
## Objetivo: Corregir UnboundLocalError en L1851, reordenar flujo analytics, analizar rol de analytics en el asset pipeline

---

## CONTEXTO DEL BUG

### Error encontrado
```
UnboundLocalError: cannot access local variable 'analytics_data' where it is not associated with a value
  File "main.py", line 1851
    detected_pains = pain_mapper.detect_pains(audit_result, validation_summary, analytics_data)
```

### Root Cause: Orden invertido de definicion vs uso

| Linea | Contenido | Estado |
|-------|-----------|--------|
| 1851 | `pain_mapper.detect_pains(..., analytics_data)` | ERROR: variable no existe |
| 1852 | `elif analytics_data:` | ERROR: variable no existe |
| 1958-1989 | Bloque de construccion `analytics_data` | DEFINICION REAL (130 lineas despues) |
| 2000 | V4DiagnosticGenerator recibe analytics_data | OK si antes se define |
| 2046 | V4ProposalGenerator recibe analytics_data | OK si antes se define |

### Impacto
- v4complete CRASH antes de generar documentos
- 0 archivos de output comercial creados
- Analytics nunca se instancia ni prueba
- Pipeline truncado al 40%

---

## ANALISIS: Rol de Analytics en el Asset Pipeline

### Flujo completo de datos analytics en el sistema

```
analytics_data dict (main.py L1981)
  │
  ├── detect_pains() → PainSolutionMapper (L1851) [CRASH AQUI]
  │     └── _detect_analytics_pains()
  │          ├── pain: "no_analytics_configured" → si ga4_available = False
  │          ├── pain: "no_ga4_enhanced" → si ga4_available = False
  │          └── pain: "no_organic_traffic_insights" → si organic_traffic no disponible
  │               ↓
  ├── generate_asset_plan() → AssetSpec[] (L1873)
  │     └── no_analytics_configured → "analytics_setup_guide"
  │     └── no_ga4_enhanced → "analytics_setup_guide"
  │     └── no_organic_traffic_insights → "indirect_traffic_optimization"
  │               ↓
  ├── V4DiagnosticGenerator (L2000) → _inject_analytics() en diagnostico
  │          └── usa use_ga4 (True/False) para decidir fuentes de datos
  │               ↓
  ├── V4ProposalGenerator (L2046) → analytics en propuesta
  │               ↓
  ├── V4AssetOrchestrator.generate_assets() (L2072+)
  │     └── PainSolutionMapper.detect_pains() SE LLAMA DE NUEVO sin analytics_data
  │     └── Resultado: NO se detectan pains de analytics en pipeline de assets
  │          [DESCONECION ADICIONAL: main.py L1851 pasa analytics_data pero L2072+ no]
  │               ↓
  └── Persistencia JSON (L2390-2402)
        └── analytics en v4_complete_report.json
```

### Catalogo de Assets vinculados a Analytics

| Asset | Template | Output | Pain trigger | Campo requerido | Estado |
|-------|----------|--------|--------------|-----------------|--------|
| `analytics_setup_guide` | `analytics_setup_guide_template.md` | `{prefix}guia_configuracion_ga4{suffix}.md` | `no_analytics_configured`, `no_ga4_enhanced` | `ga4_available` | IMPLEMENTED |
| `indirect_traffic_optimization` | `indirect_traffic_optimization_template.md` | `{prefix}guia_optimizacion_trafico_indirecto{suffix}.md` | `no_organic_traffic_insights` | `organic_traffic` | IMPLEMENTED |

### Desconexion CRITICA en V4AssetOrchestrator

En `main.py L1851`, `analytics_data` se pasa a `pain_mapper.detect_pains()` para detectar pains y generar el asset plan. Esto funciona DESPUES del fix.

PERO en `V4AssetOrchestrator.generate_assets()` (L2072-2103), se llama `self.pain_mapper.detect_pains(audit_result, validation_summary)` en la linea 219 **SIN analytics_data**. Esto significa que:

1. El asset plan (L1873) se genera correctamente con analytics_data del main.py
2. PERO el V4AssetOrchestrator regenera sus propios pains SIN analytics_data
3. Los assets de analytics que dependen de estos pains podrian no generarse en fase 4

**Verificar**: El asset plan se pasa al orchestrator via `asset_specs` (L2074+_generate_with_coherence_check), asi que los assets de analytics YA estan en el plan y no dependen del segundo detect_pains. Pero si el ConditionalGenerator necesita datos de analytics para validar preflight checks, eso es un problema.

### Analisis de `_generate_content` en ConditionalGenerator

**Hallazgo clave**: Los assets `analytics_setup_guide` e `indirect_traffic_optimization` tienen templates y estan en el catalogo, pero NO tienen handlers en `_generate_content()` de ConditionalGenerator. No hay `elif asset_type == "analytics_setup_guide"` ni `elif asset_type == "indirect_traffic_optimization"`.

Esto significa que cuando el ConditionalGenerator intenta generar estos assets, no encuentra un handler especifico. Hay que verificar:
1. Si usa fallback a template generico
2. Si genera un error silencioso
3. Si el asset se llena desde template estatico

### Resumen: Cadena de dependencias analytics → assets

| Nivel | Componente | Rol de Analytics | Funciona hoy? |
|-------|------------|-----------------|---------------|
| 1 | PainSolutionMapper.detect_pains() |analytics_data como parametro | ❌ Crash L1851 |
| 2 | generate_asset_plan() | Usa pains detectados #1 | ❌ Dependiente |
| 3 | V4DiagnosticGenerator._inject_analytics() | usa analytics_data dict | ❌ Nunca alcanza |
| 4 | V4ProposalGenerator.generate() | usa analytics_data dict | ❌ Nunca alcanza |
| 5 | V4AssetOrchestrator.generate_assets() | No recibe analytics_data | ⚠️ Llama detect_pains sin analytics_data |
| 6 | ConditionalGenerator._generate_content() | No maneja analytics_setup_guide | ⚠️ No tiene handler |
| 7 | Persistencia JSON | analytics en v4_complete_report.json | ❌ Nunca alcanza |

### Desconexiones adicionales detectadas

| ID | Desconexion | Nivel | Impacto |
|----|-------------|-------|---------|
| D-A | V4AssetOrchestrator detect_pains() sin analytics_data | L219 en orchestrator | MEDIO - Los pains de analytics se pierden en fase 4 |
| D-B | ConditionalGenerator no maneja analytics_setup_guide | _generate_content() | ALTO - Asset no se genera su contenido |
| D-C | ConditionalGenerator no maneja indirect_traffic_optimization | _generate_content() | ALTO - Asset no genera su contenido |

---

## PLAN DE ACCION

### FASE A: Fix critico de orden en main.py

### Paso A1: Mover bloque analytics_data antes de PainSolutionMapper

**Bloque a MOVER** (actual L1958-1989):
```python
# Construir analytics_data para V4DiagnosticGenerator
from modules.analytics.google_analytics_client import GoogleAnalyticsClient
from data_models.analytics_status import AnalyticsStatus

ga4_client = GoogleAnalyticsClient()
ga4_available = ga4_client.is_available()

analytics_status = AnalyticsStatus()
analytics_status.ga4_available = ga4_available
analytics_status.ga4_status_text = (
    "✅ Conectado — datos de GA4 incluidos"
    if ga4_available
    else "⚠️ No configurado (ver GA4_PROPERTY_ID)"
)
analytics_status.profound_available = False
analytics_status.profound_status_text = "⚠️ No disponible en esta version (API pendiente)"
analytics_status.semrush_available = False
analytics_status.semrush_status_text = "⚠️ No disponible en esta version (API pendiente)"

analytics_data = {
    "use_ga4": ga4_available,
    "analytics_status": analytics_status,
    "hotel_data": None,
}
```

**Destino**: Justo despues de `print("[INFO] Diagnóstico se generará después de validación de coherencia...")` y ANTES de `print("\n Generando plan de assets...")` (antes de PainSolutionMapper L1851).

### Paso A2: Eliminar definicion original (L1958-1989)

Eliminar el bloque duplicado en su ubicacion original para evitar sobrescritura.

### Paso A3: Verificar que imports no se duplican

Verificar si `from modules.analytics.google_analytics_client import GoogleAnalyticsClient` y `from data_models.analytics_status import AnalyticsStatus` ya existen en el tope de main.py. Si existen, solo mover la logica de inicializacion (no los imports).

---

### FASE B: Analisis de Assets de Analytics (diagnostico)

### Paso B1: Verificar como se generan analytics_setup_guide e indirect_traffic_optimization

```bash
# Buscar si existe handling generico para assets sin handler especifico
grep -n 'else:\|fallback\|default\|template' modules/asset_generation/conditional_generator.py
```

Verificar en el metodo `_generate_content()` y `_generate_with_coherence_check()` como se manejan assets que NO tienen un `elif` especifico.

### Paso B2: Verificar preflight checks para assets de analytics

```bash
grep -n 'analytics_setup_guide\|indirect_traffic_optimization\|ga4_available\|organic_traffic' modules/asset_generation/preflight_checks.py
```

Verificar que los preflight checks validen correctamente los campos `ga4_available` y `organic_traffic`.

### Paso B3: Verificar si V4AssetOrchestrator necesita analytics_data

Revisar la linea 219 del orchestrator (`pain_mapper.detect_pains(audit_result, validation_summary)`). Si los analytics pains ya vienen en `asset_specs` (del paso A1), quizas no sea critico. Pero si el orchestrator regenera pains para validar coherencia, necesita analytics_data.

### Paso B4: Documentar hallazgos de analisis de assets

Para cada asset de analytics (`analytics_setup_guide`, `indirect_traffic_optimization`), documentar:
- Template que usa y si se llena correctamente
- Si tiene handler en ConditionalGenerator o usa fallback
- Si los preflight checks son apropiados
- Si se genera contenido real o queda vacio

---

### FASE C: Verificacion post-fix

### Ejecucion de validacion
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
venv/Scripts/python.exe main.py v4complete --url https://www.hotelvisperas.com/es --output ./output
```

### Checklist de verificacion (10 pasos)
1. ✅ v4complete completa sin crash
2. ✅ audit_report.json generado
3. ✅ v4_complete_report.json creado con seccion analytics
4. ✅ 01_DIAGNOSTICO.md generado con transparencia analytics
5. ✅ 02_PROPUESTA_COMERCIAL.md generado con seccion analytics
6. ✅ analytics_status en JSON tiene campos: ga4_available, profound_available, semrush_available
7. ✅ PainSolutionMapper detecta analytics pains (no_analytics_configured)
8. ✅ Assets de analytics generados en output/
9. ✅ Coherence Score disponible
10. ✅ Contenido de guia_configuracion_ga4.md NO esta vacio ni con placeholders

### Checklist de desconexiones (completo, incluyendo D-A, D-B, D-C)

| # | Desconexion | Verificacion | Estado esperado |
|---|-------------|--------------|-----------------|
| D1 | analytics_data definido antes de L1851 | Verificar main.py post-fix | ✅ Definido antes de usar |
| D2 | analytics_data llega a PainSolutionMapper | Logs de detect_pains | ✅ Recibe dict valido |
| D3 | analytics_data pasa a V4DiagnosticGenerator | Ver JSON output | ✅ Incluido |
| D4 | analytics_data pasa a V4ProposalGenerator | Ver propuesta | ✅ Incluido |
| D5 | analytics se persiste en JSON | Seccion analytics en JSON | ✅ Preservada |
| D6 | Analytics pains detectados | Pain list contiene analytics pain | ✅ detectado |
| D7 | Assets de analytics generados | Archivos en output/ | ✅ Generados |
| D8 | GoogleAnalyticsClient graceful fallback | Logs sin excepcion | ✅ Fallback ok |
| D9 | Profound/Semrush stubs graceful | Logs sin excepcion | ✅ Retorna None sin error |
| D-A | V4AssetOrchestrator detect_pains sin analytics_data | Verificar si afecta | ⚠️ Diagnosticado |
| D-B | ConditionalGenerator sin handler analytics_setup_guide | Verificar si genera contenido | ⚠️ Diagnosticado |
| D-C | ConditionalGenerator sin handler indirect_traffic | Verificar si genera contenido | ⚠️ Diagnosticado |

---

## RIESGOS Y MITIGACIONES

| Riesgo | Impacto | Mitigacion |
|--------|---------|------------|
| Import duplicado al mover bloque | BAJO | Verificar imports existentes; si existen, solo mover logica |
| Variable analytics_status con scope issue | BAJO | Todo dentro de run_v4_complete_mode |
| GoogleAnalyticsClient tarda en is_available() | MEDIO | Cliente tiene lazy init y graceful fallback |
| Assets de analytics quedan vacios (D-B, D-C) | ALTO | Diagnosticar en FASE B; si hay problema, incluir en siguiente plan |
| V4AssetOrchestrator regenera pains sin analytics_data | MEDIO | Los asset_specs ya vienen del plan; verificar si el paso de coherencia los elimina |

---

## FORMATO DE REPORTE POST-FIX

Generar `output/ANALYTICS_FIX_REPORT_YYYYMMDD.md` con:
- Cambios realizados (diff de main.py)
- Lineas modificadas antes y despues
- Resultados de analisis de assets (FASE B)
- Resultado de ejecucion con URL de Hotel Visperas
- Checklist de desconexiones completo (D1-D9 + D-A, D-B, D-C)
- Archivos generados (lista y tamanos)
- Recomendaciones para siguiente sesion (fix de D-B/D-C si aplica)

---

## REGLAS DE EJECUCION
- FASE A: SOLO modificar main.py (reorden de bloques)
- FASE B: READ-ONLY — solo lectura y diagnostico de modulos
- NO cambiar logica de los clientes de analytics
- NO modificar modulos en modules/ (solo diagnosticar en FASE B)
- Ejecutar v4complete con Hotel Visperas para validar fix
- Documentar cambios en CHANGELOG.md y REGISTRY.md
- Log de phase completion con log_phase_completion.py
