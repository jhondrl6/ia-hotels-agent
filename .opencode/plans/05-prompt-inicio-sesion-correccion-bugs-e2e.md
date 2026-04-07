# Prompt de Inicio de Sesion -- Correccion de Bugs E2E de v4complete

## Contexto

Sesion de correccion de bugs criticos descubiertos durante la ejecucion v4complete con https://www.hotelvisperas.com/es. La ejecucion llego hasta FASE 4 (assets generados) pero crasheo en FASE 4.5 (Publication Gates). Hay 3 bugs criticos y 3 desconexiones entre modulos.

## Objetivo

Corregir los 3 bugs criticos (FIX-1, FIX-2, FIX-3) y verificar las 3 desconexiones reportadas. Al terminar, v4complete debe completar FASE 1 a FASE 4.6 sin crashes.

## Ejecucion E2E Inicial (antes de tocar codigo)

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe main.py v4complete --url https://www.hotelvisperas.com/es --debug 2>&1 | tee evidence/fase-correccion-bugs/ejecucion_r0.log
```

Capturar el crash exacto para confirmar los bugs documentados.

---

## FIX-1 (Bloqueante): Path type mismatch en main.py

### Problema
`V4DiagnosticGenerator.generate()` retorna `str` (confirmado en v4_diagnostic_generator.py linea 231: `return str(file_path)`), pero en main.py se usa `.exists()` como si fuera `Path`.

### Ubicaciones afectadas en main.py:
- **Linea 2120**: `if diagnostic_path and diagnostic_path.exists():`
- **Linea 2141**: `if proposal_path and proposal_path.exists():`
- **Linea 2266**: `if diagnostic_path and diagnostic_path.exists():`
- **Linea 2272**: `if proposal_path and proposal_path.exists():`

### Fix
Envolver con `Path()` en las 4 ubicaciones:
```python
# Cambiar de:
if diagnostic_path and diagnostic_path.exists():
# A:
if diagnostic_path and Path(diagnostic_path).exists():
```

**Linea 672 ya tiene el patron correcto**: `if diagnostic_path and Path(diagnostic_path).exists():`

### Impacto
Este fix desbloquea:
- FASE 3.6 (Content Scrubber) -- actualmente crashea silenciosamente
- FASE 4.5 (Publication Gates) -- actualmente crashea con AttributeError
- FASE 4.6 (Consistency Checker) -- actualmente no se ejecuta
- FASE 7 (Delivery) -- actualmente no se ejecuta
- FASE 10 (Health) -- actualmente no se ejecuta

---

## FIX-2 (Bloqueante): Region "default" propagation

### Problema
`_extract_region_from_audit()` en main.py linea 2742 siempre retorna `"default"` (ver linea 2755). En main.py linea 1511:
```python
region = _extract_region_from_audit(audit_result) if audit_result else "default"
```

Esto causa que documentos generados digan "en default", "la region de default", etc.

### Solucion
1. Ya hay deteccion de region por URL detectada en FASE 1 (detecta "eje_cafetero" correctamente)
2. Cuando no hay datos de onboarding (branch else), intentar extraer la ciudad del audit_result
3. Fallback a la region detectada de la URL
4. Si todo falla, usar "la region" en lugar de "default"

### Implementacion
Modificar la seccion ~linea 1504-1517 en main.py:

```python
# ELSE branch (no fresh onboarding data)
else:
    print(f"   ℹ️  Using defaults (no fresh onboarding data found)")
    
    # Extract operational data from audit or use defaults
    rooms = _extract_rooms_from_audit(audit_result) if audit_result else 10
    
    # FIX-2: Extract city/region from audit or fallback to URL-detected region
    if audit_result:
        # Try to get city from various sources
        city = None
        if hasattr(audit_result, 'gbp') and audit_result.gbp:
            city = audit_result.gbp.get('city') or audit_result.gbp.get('address', {}).get('city')
        if not city and hasattr(audit_result, 'geo') and audit_result.geo:
            city = audit_result.geo.get('city')
        if city:
            region = city
        elif region:  # Use URL-detected region from FASE 1
            pass  # region already set from _detect_region_from_url()
        else:
            region = "la región"  # Generic fallback instead of "default"
    else:
        region = region if region else "la región"
    
    occupancy_rate = 0.50
    direct_channel_pct = 0.20
    adr_from_onboarding = None
```

**Verificar ademas** en `_extract_region_from_audit()` que el fallback sea "la región" en vez de "default", para backward compatibility.

---

## FIX-3 (Alto): COP COP duplicado y Content Scrubber integration

### Problema
El Content Scrubber (FASE-B) DEBERIA limpiar "COP COP" pero por BUG-1 nunca se ejecuta.

### Verificacion requerida
1. Verificar que `modules/postprocessors/content_scrubber.py` tenga un pattern para "COP":
   - Buscar el pattern en las reglas del scrubber
   - Verificar que reemplace "COP COP" por "COP"
   - Verificar que reemplace "COP COP" en templates generados

2. Si el scrubber no tiene rule para "COP COP", agregar:
   ```python
   # Pattern para detectar "COP COP" (duplicado de moneda)
   (re.compile(r'\bCOP\s+COP\b', re.IGNORECASE), 'COP'),
   ```

3. Verificar que los TEMPLATES no generen "COP COP" de entrada:
   - Buscar en templates templates/ cualquier "COP COP" o patron que lo genere
   - Si el template tiene algo como "{currency} COP" donde currency ya es "COP", corregirlo

### Impacto
Sin este fix, el diagnostico entrega al cliente texto con "COP COP" duplicado y valores como "500.000 COP COP" que son inaceptables.

---

## DESCONEXION-1 (Medio): LocalContentGenerator no conectado

### Verificacion
1. Confirmar que `local_content_generator.py` existe y tiene 15 tests pasando:
   ```bash
   cd /mnt/c/Users/Jhond/Github/iah-cli
   ./venv/Scripts/python.exe -m pytest tests/asset_generation/test_local_content_generator.py -v --tb=short
   ```

2. Verificar que `asset_catalog.py` tenga entrada `local_content_page`

3. Verificar que `PainSolutionMapper` no mapea ningun pain a `local_content_page`

### Si confirmado
Documentar en el reporte final como "known gap" para futuro desarrollo. NO implementar en esta sesion (fuera de alcance).

---

## DESCONEXION-2 (Medio): OpportunityScorer no se refleja en diagnostico

### Verificacion
1. En `v4_diagnostic_generator.py`, `_inject_brecha_scores()` se ejecuta en linea 593
2. Verificar que el template use las variables `brecha_1_score`, `brecha_1_severity`, etc.
3. Verificar que el template NO use el porcentaje estatico "Por que importa: 15%"
4. Buscar en templates templates/ el texto "Por que importa"

### Si el template usa placeholders incorrectos
Corregir el template para que use las variables inyectadas:
- `{brecha_1_score}` en vez del porcentaje estatico
- Si el template usa `{brecha_1_impacto}` que es el %, verificar que esto es intencional

---

## DESCONEXION-3 (Bajo): GSC no pasa en analytics_data

### Verificacion
En main.py lineas ~1897-1903, verificar que `analytics_data` solo tiene GA4 y no GSC.

Si confirmado, documentar como "known gap" para FASE-D. NO implementar en esta sesion.

---

## Secuencia de Ejecucion

1. Ejecutar E2E baseline (r0) para capturar crashes
2. Aplicar FIX-1 + FIX-2 + FIX-3 en main.py
3. Regresion:
   ```bash
   ./venv/Scripts/python.exe -m pytest tests/postprocessors/test_document_quality_gate.py tests/postprocessors/test_content_scrubber.py -v --tb=short
   ```
4. Ejecutar E2E (r1) para verificar fixes:
   ```bash
   ./venv/Scripts/python.exe main.py v4complete --url https://www.hotelvisperas.com/es --debug 2>&1 | tee evidence/fase-correccion-bugs/ejecucion_r1.log
   ```
5. Si crash persists, fix iterative (seguir patron E2E debugging)
6. Verificar output final:
   - NO "COP COP" en diagnostico
   - NO "en default" en diagnostico
   - FASE 3.6 (Scrubber) ejecutada con logs
   - FASE 4.5 (Publication Gates) ejecutada con logs
   - FASE 4.6 (Consistency Checker) ejecutada con logs
   - Coherence Score >= 0.8
   - Publication Readiness: true o con issues explicados

---

## Notas de Arquitectura

- `v4_diagnostic_generator.py` contiene la logica de generacion de diagnosticos
- `v4_proposal_generator.py` contiene la logica de propuestas
- `content_scrubber.py` post-procesa documentos para limpiar errores
- `document_quality_gate.py` valida calidad de documentos post-scrubbing
- `publication_gates.py` gates finales para publication readiness

---

## Formato de Reporte Final

- Resumen de fixes aplicados (codigo, archivos, lineas)
- Evidencia E2E (r0 crash confirmada, r1+rN clean pass)
- Output verificado (sin COP COP, sin default, scruber ejecutado, gates ejecutados)
- Desconexiones confirmadas (1, 2, 3) con estado
- Tests de regresion (resultado)
- Archivos modificados
- Riesgos restantes
- Siguiente paso recomendado
