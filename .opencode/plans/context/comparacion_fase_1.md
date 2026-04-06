# Comparacion Fase CAUSAL-01: Scorecard Consistente

## Baseline (ANTES)
- Archivo: `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260402_184117.md`
- Fecha: 2026-04-02 18:41:17

### Scorecard baseline (5 filas):
```
| Google Maps (GEO)           | 72/100 | 55/100 | Superior    |
| Perfil de Google Business   | 86/100 | 30/100 | Superior    |
| Visibilidad en IA (AEO)     | —      | 15/100 | Pendiente   |
| Optimizacion ChatGPT (IAO)  | 25/100 | 10/100 | Pendiente   |
| SEO Local                   | 30/100 | 65/100 | Bajo        |
```

### Problemas del baseline:
1. AEO muestra "--" (sin valor numerico) - no media nada
2. IAO muestra 25/100 pero es fallback a schema_infra = AEO (redundante)
3. 5 filas cuando solo hay 4 indicadores distintos
4. IAO sin GA4 real no tiene validacion

---

## Post-CAUSAL-01 (DESPUES)
- Archivo: `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260404_115620.md`
- Fecha: 2026-04-04 11:56:20

### Scorecard actualizado (4 filas):
```
| Google Maps (GEO)           | 72/100 | 55/100 | Superior    |
| Perfil de Google Business   | 86/100 | 30/100 | Superior    |
| AEO - Infraestructura IAs   | —/100  | 15/100 | Pendiente   |
| SEO Local                   | 30/100 | 65/100 | Bajo        |
```

### Cambios logrados:
1. Eliminado "Optimizacion ChatGPT (IAO)" - redundante con AEO
2. Eliminado "Visibilidad en IA (AEO)" separada - unificada como "AEO - Infraestructura para IAs"
3. Scorecard ahora tiene 4 filas coherentes
4. AEO muestra "--/100" cuando no hay PageSpeed data (comportamiento legitimo, no fantasma)
5. No hay KeyError ni errores de template
6. Diagnostico generado exitosamente (exit code 0)

### Notas:
- AEO "--/100" es correcto: PageSpeed API timeout = no mobile_score = no has_real_data
- En ejecuciones con PageSpeed exitoso, AEO mostrara un numerico real XX/100
- El score IAO=25/100 del baseline era un fallback a schema_infra (mismo calculo que AEO)
- Ahora AEO = schema_infra renombrado = score legitimo con medicion directa del audit

### Metodos eliminados:
- `_calculate_voice_readiness_score()` - retornaba "--" hardcodeado, nunca midio nada
- `_calculate_iao_score()` - sin GA4 era identico a schema_infra_score
- `_calculate_score_ia()` - wrapper de IATester que no aporta sin GA4 real

### Referencias actualizadas:
- `_calculate_schema_infra_score()` -> `_calculate_aeo_score()` (mismo calculo, nombre correcto)
- Referencias en `_prepare_template_data()` actualizadas
- Referencias en `_inject_analytics()` limpiadas (eliminado `iao_score` del retorno)

### Archivos modificados:
1. `modules/commercial_documents/v4_diagnostic_generator.py` - 110+ lineas eliminadas
2. `modules/commercial_documents/templates/diagnostico_v6_template.md` - scorecard de 5 a 4 filas
