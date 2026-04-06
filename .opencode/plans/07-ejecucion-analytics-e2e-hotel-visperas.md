# Plan: Ejecucion ANALYTICS E2E v4complete — Hotel Visperas

## ID: ANALYTICS-EXEC-01
## Version: 1.0 — 2026-04-02
## Objetivo: Ejecutar v4complete para Hotel Visperas y generar informe de comportamiento analitico

---

## CONTEXTO

### Modulo objetivo
`modules/analytics/` — 3 clientes:
1. `google_analytics_client.py` (175 lineas) — Cliente GA4 real con lazy init y graceful fallback
2. `profound_client.py` (168 lineas) — STUB documentado con instrucciones de activacion
3. `semrush_client.py` (121 lineas) — STUB documentado con instrucciones de activacion

### Flujo analytics en main.py
- L1958-1986: Se construye `analytics_data` dict con `AnalyticsStatus`
- L1963-1964: `GoogleAnalyticsClient()` se instancia y se verifica `is_available()`
- L1966-1977: Se completa `AnalyticsStatus` con estado de 3 fuentes (GA4 + 2 stubs)
- L1981-1986: Se crea dict `analytics_data = {"use_ga4": ga4_available, "analytics_status": analytics_status, ...}`
- L1989: Se pasa `analytics_data` a `V4DiagnosticGenerator.generate()`
- L1994: Se pasa `analytics_data` a `V4ProposalGenerator.generate()`
- L1849: Se pasa `analytics_data` a `PainSolutionMapper.detect_pains()` con deteccion de analytics pains

### Punto de chequeo del flujo
AnalyticsStatus → analytics_data → V4DiagnosticGenerator → V4ProposalGenerator → PainSolutionMapper → v4_complete_report.json

### Archivos de salida esperados en output/
- v4_complete_report.json (debe incluir seccion analytics)
- 02_PROPUESTA_COMERCIAL.md (debe incluir seccion analytics si GA4 disponible, o fallback)
- 01_DIAGNOSTICO.md (debe incluir transparencia analytics)
- Assets de analytics (guia_configuracion_ga4.md) si se detecta pain de no_analytics_configured

---

## PASOS DE EJECUCION

### Paso 1: Ejecutar v4complete
```bash
python3 main.py v4complete \
    --url https://www.visperasdecarcasalosalp.com \
    --output ./output \
    --no-browser \
    2>&1 | tee /tmp/v4complete_output_$(date +%Y%m%d_%H%M%S).log
```

**NOTA**: Si el comando `--no-browser` no existe, usar simplemente:
```bash
python3 main.py v4complete --url https://www.visperasdecarcasalosalp.com --output ./output 2>&1 | tee /tmp/v4complete_output.log
```

### Paso 2: Verificar ejecucion
Esperar a que el comando termine. Tiempo estimado: 2-5 minutos.
Capturar:
- Exit code
- Output completo del log (ya redirigido con tee)

### Paso 3: Verificar seccion analytics en v4_complete_report.json
```bash
python3 -c "
import json
report_path = './output/v4_complete_report.json'
with open(report_path, 'r', encoding='utf-8') as f:
    report = json.load(f)
analytics = report.get('analytics', {})
print('=== ANALYTICS EN v4_complete_report.json ===')
for k, v in analytics.items():
    print(f'  {k}: {v}')
print(f'\\nanalytics keys present: {list(analytics.keys())}')
print(f'is_complete: {analytics.get(\"is_complete\", \"N/A\")}')
print(f'missing_credentials: {analytics.get(\"missing_credentials\", \"N/A\")}')
"
```

**Check esperado**: Seccion `analytics` existe con campos: ga4_available, ga4_status, profound_available, profound_status, semrush_available, semrush_status, is_complete, missing_credentials, timestamp.

### Paso 4: Verificar deteccion de analytics pains
```bash
python3 -c "
import json
report_path = './output/v4_complete_report.json'
with open(report_path, 'r', encoding='utf-8') as f:
    report = json.load(f)

# Buscar pains relacionados con analytics
pain_keys = [p for p in report.get('pains', report.get('detected_pains', [])) 
             if 'analytic' in str(p).lower() or 'organic' in str(p).lower() or 'traffic' in str(p).lower()]
print('=== ANALYTICS PAINS DETECTADOS ===')
if pain_keys:
    for p in pain_keys:
        print(f'  => {p}')
else:
    print('  (Seccion pains no accesible directamente en report)')

# Verificar asset plan
plan = report.get('asset_plan', [])
analytics_assets = [a for a in plan if 'analytic' in str(a).lower() or 'traffic' in str(a).lower() or 'ga4' in str(a).lower()]
print(f'\\n=== ANALYTICS ASSETS EN PLAN ===')
if analytics_assets:
    for a in analytics_assets:
        print(f'  => {a}')
else:
    print('  (Ningun asset de analytics en plan, verificar PainSolutionMapper)')
"
```

### Paso 5: Verificar assets generados
```bash
ls -la ./output/*analytic* ./output/*ga4* ./output/*trafico* 2>/dev/null || echo "No se encontraron assets de analytics en output/"
```

Verificar tambien si se genero `guia_configuracion_ga4.md` o `optimizacion_trafico_indirecto.md`.

### Paso 6: Verificar seccion analytics en propuesta
```bash
grep -i "analytics\|ga4\|trafico indirecto\|trafico.*indirecto\|metrica" "./output/02_PROPUESTA_COMERCIAL.md" 2>/dev/null || echo "No se encontraron referencias a analytics en propuesta"
```

### Paso 7: Verificar seccion analytics en diagnostico
```bash
grep -i "analytics\|ga4\|transparencia\|fuentes de datos" "./output/01_DIAGNOSTICO.md" 2>/dev/null || echo "No se encontraron referencias a analytics en diagnostico"
```

### Paso 8: Verificar coherencia
```bash
python3 -c "
import json
report_path = './output/v4_complete_report.json'
with open(report_path, 'r', encoding='utf-8') as f:
    report = json.load(f)
coherence = report.get('coherence_score', report.get('coherence', {}))
print(f'Coherence Score: {coherence}')
print(f'Hard contradictions: {report.get(\"hard_contradictions\", \"N/A\")}')
print(f'Financial validity: {report.get(\"financial_validity\", \"N/A\")}')
"
```

### Paso 9: Verificar logs de analytics durante la ejecucion
Revisar el log capturado en el Paso 1:
```bash
cat /tmp/v4complete_output*.log | grep -i "analytics\|ga4\|profound\|semrush\|AnalyticsStatus\|analytics_data\|PainSolutionMapper" 2>/dev/null
```

### Paso 10: Verificar que pain_solution_mapper detecta analytics pains
```bash
grep -n "detect_pains\|analytics_data\|no_analytics_configured\|_detect_analytics" /tmp/v4complete_output*.log 2>/dev/null || echo "No se encontraron logs de deteccion de analytics pains"
```

---

## CHECKLIST DE DESCONEXIONES

| # | Desconexion | Como verificar | Estado esperado |
|---|-------------|----------------|-----------------|
| D1 | AnalyticsStatus no se construye antes de llamada | Revisar main.py L1958-1977 | ✅ Se construye con 3 fuentes |
| D2 | analytics_data no se pasa a V4DiagnosticGenerator | Revisar main.py L1994 | ✅ analytics_data pasado |
| D3 | analytics_data no se pasa a V4ProposalGenerator | Revisar main.py L2040 | ✅ analytics_data pasado |
| D4 | analytics_data no se pasa a PainSolutionMapper | Revisar main.py L1849 | ✅ analytics_data pasado |
| D5 | analytics no se persiste en JSON | Verificar seccion analytics en JSON | ✅ Seccion analytics existe |
| D6 | Analytics pains no se detectan | Verificar pains en report | ✅ no_analytics_configured detectado |
| D7 | Assets de analytics no se generan | Verificar archivos en output/ | ✅ guia_configuracion_ga4.md generado |
| D8 | GoogleAnalyticsClient crashea | Verificar exit code y logs | ✅ Graceful fallback (no config) |
| D9 | Profound/Semrush stubs causan error | Verificar logs | ✅ Retornan None graceful |

---

## FORMATO DE INFORME

Generar un archivo `output/ANALYTICS_EXEC_REPORT_YYYYMMDD.md` con esta estructura:

```markdown
# Informe Ejecucion ANALYTICS E2E - Hotel Visperas

## Metadata
- Fecha ejecucion: YYYY-MM-DD
- Comando: python3 main.py v4complete --url ...
- Tiempo de ejecucion: Xs
- Exit code: N
- Version del sistema: v4.15.0

## Modulo analytics: Comportamiento observado

### GoogleAnalyticsClient
- Estado: Configured / Not Configured
- Fallback graceful: Si / No
- Errores capturados: [lista]
- Latencia: Xms

### ProfoundClient (STUB)
- Comportamiento: Documentado como STUB
- Retorna None: Si
- Sin excepciones: Si/No

### SemrushClient (STUB)
- Comportamiento: Documentado como STUB
- Retorna None: Si
- Sin excepciones: Si/No

## Flujo analytics: Verificacion de puntos de integracion

| Punto | Estado | Detalle |
|-------|--------|---------|
| AnalyticsStatus construido | ✅/❌ | ... |
| analytics_data dict construido | ✅/❌ | ... |
| Pasado a V4DiagnosticGenerator | ✅/❌ | ... |
| Pasado a V4ProposalGenerator | ✅/❌ | ... |
| Pasado a PainSolutionMapper | ✅/❌ | ... |
| Persistido en JSON | ✅/❌ | ... |
| Pains de analytics detectados | ✅/❌ | ... |
| Assets de analytics generados | ✅/❌ | ... |

## Desconexiones detectadas

| # | Desconexion | Impacto | Root cause |
|---|-------------|---------|------------|
| - | - | - | - |

## Metricas finales

| Metrica | Valor | Umbral | Estado |
|---------|-------|--------|--------|
| Coherence Score | X.XX | >= 0.8 | ✅/❌ |
| Hard contradictions | N | = 0 | ✅/❌ |
| Financial validity | X% | >= 95% | ✅/❌ |
| Assets generados | N | - | - |
| Analytics pains detectados | N | >= 1 | ✅/❌ |

## Recomendaciones
- [ ] ...
```

---

## RIESGOS Y MITIGACIONES

| Riesgo | Impacto | Mitigacion |
|--------|---------|------------|
| v4complete tarda > 10 min por scraping | ALTO | --no-browser si disponible, timeout de 600s |
| Google Analytics Client hace llamadas externas | BAJO | Deberia ser graceful sin credenciales |
| Output no tiene archivos | MEDIO | Verificar directorio output/ existe |
| PainSolutionMapper no exporta detect_pains_for_analytics | BAJO | Ya implementado en ANALYTICS-04 |

## REGLAS DE EJECUCION
- NO modificar codigo del proyecto en esta sesion
- Ejecutar en modo read-only excepto generacion de reporte
- Si algun comando falla, documentar el error exacto (stderr + stdout)
- Si el v4complete crash, capturar ultima linea de output y stack trace
