# Prompt: FASE-H-07 - Fix ROI Calculation

## Proyecto: iah-cli | hotelvisperas.com
## Fecha: 2026-03-26

---

## Pre-requisito

**FASE-H-06 DEBE estar completada.**

---

## Contexto

El ROI en la propuesta comercial muestra "24.0XX" en vez del ratio correcto (~2.6X).

**Error observado:**
```
### ROI Proyectado
**24.0XX en 6 meses**
```

El valor "24.0" es claramente un error de cálculo o formato. El ROI correcto debería ser aproximadamente 2.6X (basado en $1.2M/mes inversión vs ~$3.1M/mes ganancia).

---

## Tareas de FASE-H-07

### 1. Localizar el cálculo del ROI

Buscar en `modules/commercial_documents/v4_proposal_generator.py`:

```bash
grep -n "roi" modules/commercial_documents/v4_proposal_generator.py
```

Buscar también en el template `propuesta_v4_template.md`.

### 2. Analizar el problema

El problema podría estar en:
- El cálculo: `roi_ratio = total_gain / total_investment`
- El formato: `f"{roi_ratio:.1f}X"` debería mostrar "~2.6X"
- La variable del template: `${roi_6m}` que podría estar mal calculada

### 3. Verificar la fórmula correcta

Según `FIXES_APPLIED.md`:
```python
roi_ratio = total_gain / total_investment
return f"{roi_ratio:.1f}X"
```

Con:
- Inversión mensual: $1.200.000 COP
- Ganancia proyectada: $3.132.000 COP/mes
- Inversión total (6 meses): $7.200.000 COP
- Ganancia total (6 meses): $18.792.000 COP
- ROI ratio = 18.792.000 / 7.200.000 = 2.6X

### 4. Implementar el fix

El problema probablemente es que el valor "24.0" viene de un cálculo errado en el template o de una variable diferente.

Verificar:
1. Que la fórmula usa `ganancia_total / inversión_total` (NO diferencia)
2. Que el formato es `.1f` para mostrar 1 decimal
3. Que el sufijo "X" se añade correctamente

### 5. Verificar

Después del fix, ejecutar:
```bash
python main.py v4complete --url https://www.hotelvisperas.com/es --nombre "Hotel Vísperas" --debug
```

Verificar en la propuesta comercial que:
- El ROI muestra "~2.6X" (o "2.6X")
- NO muestra "24.0XX"

### 6. Ejecutar pytest

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/commercial_documents/ -v
```

---

## Criterio de Completitud

- [ ] Cálculo del ROI corregido
- [ ] Formato correcto (~2.6X)
- [ ] Tests de regresión pasando
- [ ] Documentación del fix en `FIXES_APPLIED.md`

---

## Post-Ejecución

### 1. Documentar en `FIXES_APPLIED.md`
### 2. Actualizar `06-checklist-GAPS-V4COMPLETE.md`
### 3. Proceder a FASE-H-08

---

*Prompt creado: 2026-03-26*
*Depende de: FASE-H-06*
