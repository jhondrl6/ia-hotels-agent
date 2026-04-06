# Prompt: FASE-H-04 - Fix Optimization Guide + ROI

## Proyecto: iah-cli | hotelvisperas.com
## Fecha: 2026-03-26

---

## Pre-requisito

**FASE-H-03 DEBE estar completada.**
Debes haber identificado la causa raíz de los placeholders en optimization_guide.

---

## Contexto

### Problema 1: Optimization Guide

El asset `optimization_guide` falla validación porque usa placeholders genéricos.

**Términos rechazados por `asset_content_validator`**:
- `...` (ellipsis)
- `pendiente`
- `no configurado`
- `por definir`
- `no disponible`
- `N/A`

**Solución**: Reemplazar estos placeholders con contenido DESCRIPTIVO que aporte valor:
- En vez de `...` → Usar descripción real del meta a generar
- En vez de `pendiente` → Usar `⚠️ Requiere configuración manual` (sin la palabra "pendiente")
- En vez de `no configurado` → Usar `⚠️ Sin datos del hotel` (sin "no configurado")

### Problema 2: ROI 292X

El cálculo de ROI muestra 292X cuando debería ser ~3.9X.

**Cálculo correcto**:
- Inversión total: $800.000 × 6 meses = $4.800.000
- Ingreso recuperado: $3.132.000 × 6 meses = $18.792.000
- ROI = $18.792.000 / $4.800.000 = 3.91X

**El valor 292X sugiere**:
- ¿Se multiplicó por 100 en vez de dividir?
- ¿Se mostró porcentaje en vez de ratio?
- ¿Error en formato de número?

---

## Tareas de FASE-H-04

### 1. Fix Optimization Guide

**En `modules/asset_generation/conditional_generator.py`**:

Eliminar todos los placeholders problemáticos. Asegurarse de que:
- No haya `...` (ellipsis)
- No haya palabras de la lista negra
- El contenido sea descriptivo y útil

### 2. Fix ROI Calculator

**Buscar y corregir el cálculo de ROI**:
```bash
grep -rn "292\|ROI\|roi" modules/ --include="*.py" | head -30
```

Verificar:
- El numerador y denominador son correctos
- El formato de salida es correcto (ratio, no porcentaje)
- No hay multiplicación_extra por 100

### 3. Verificación

```bash
# Suite de regresión
python -m pytest tests/commercial_documents/test_pain_solution_mapper.py tests/asset_generation/ -v

# Verificar que optimization_guide pasa validación
python -c "
from modules.asset_generation.asset_content_validator import AssetContentValidator
validator = AssetContentValidator()
# Testear que el contenido no tiene placeholders
"
```

---

## Post-Ejecución

1. **Marcar checklist**: Editar `06-checklist-GAPS-V4COMPLETE.md`:
   - [x] FASE-H-04 completada
   - Fixes aplicados

2. **Documentar**: Crear documento `FIXES_APPLIED.md` con:
   - Qué se cambió en optimization_guide
   - Qué se cambió en ROI calculator
   - Tests pasando

3. **Siguiente paso**: FASE-H-05 (E2E Certification)

---

## Criterios de Completitud

- [ ] optimization_guide pasa content validation
- [ ] ROI muestra ~3.9X (no 292X)
- [ ] Suite de regresión pasando
- [ ] Documentación de fixes creada
- [ ] Checklist actualizado

---

## Notas

- FASE-H-02 y FASE-H-04 pueden ejecutarse en paralelo si hay capacidad
- Ambas son fases de implementación de fixes

---

*Prompt creado: 2026-03-26*
*Proyecto: iah-cli | hotelvisperas.com*
*Depende de: FASE-H-03*
