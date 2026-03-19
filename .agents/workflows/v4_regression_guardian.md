---
description: Ejecutor de validación post-implementación para el flujo v4complete. 
             Detecta cambios y verifica que v4complete funcione correctamente.
---

# Skill: V4 Regression Guardian

> [!NOTE]
> **Trigger**: "validar v4complete", "tests post-implementación", 
>               "verificar después de cambios", "regresión v4".

## Pre-requisitos (Contexto)
- [ ] Cambios en código (git diff detectable)
- [ ] Entorno Python activo con pytest
- [ ] APIs configuradas (o modo mock para CI)

## Fronteras (Scope)
- **Hará**: 
  - Detectar módulos v4 modificados vía git diff
  - Ejecutar tests de regresión específicos de v4complete
  - Validar outputs generados (coherencia, assets, documentos)
  - Generar reporte estandarizado
- **NO Hará**: 
  - No modifica código
  - No hace commits
  - No ejecuta v4complete en producción (solo validación)

## Pasos de Ejecución

### 1. Detección de Cambios
```bash
git diff --name-only HEAD~1
```
Mapear archivos a módulos v4 usando `.agents/workflows/v4_module_test_map.yaml`

*Validación*: Módulos afectados identificados.

### 2. Ejecución de Tests Unitarios
Ejecutar tests correspondientes a módulos afectados:
```bash
pytest tests/<modulo_afectado>/ -v --tb=short
```

*Validación*: Todos los tests unitarios pasan.

### 3. Test de Regresión Permanente
Ejecutar test de regresión del Hotel Visperas (caso real):
```bash
pytest tests/regression/test_hotel_visperas.py -v
```

*Validación*: Sin regresiones en caso base.

### 4. Validación de Estructura de Salida (Opcional)
Si cambios afectan orchestration o commercial_documents:
- Ejecutar v4complete con URL de prueba (mock mode)
- Verificar estructura de outputs:
  - `01_DIAGNOSTICO_Y_OPORTUNIDAD.md` presente
  - `coherence_validation.json` con score ≥ 0
  - `financial_scenarios.json` con 3 escenarios

*Validación*: Outputs generados correctamente.

### 5. Generación de Reporte
Crear `.validation_reports/[timestamp]_v4_regression.md`:
- Archivos modificados
- Tests ejecutados y resultado
- Módulos afectados
- Veredicto: PASS/FAIL

*Validación*: Reporte guardado.

## Criterios de Éxito
- [ ] Tests unitarios de módulos afectados: PASS
- [ ] Test de regresión Hotel Visperas: PASS
- [ ] Sin errores en imports de módulos v4
- [ ] Reporte generado correctamente

## Plan de Recuperación (Fallback)
- Si tests fallan: mostrar diff de cambios, sugerir revisión específica
- Si módulo crítico afectado (financial_engine, coherence): mostrar advertencia
- Si regresión detectada: bloquear y sugerir rollback
