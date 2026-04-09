# Dependencias entre Fases

## Diagrama de Dependencias

```
FASE-A (WhatsApp Detection Fix)
  |
  +-> FASE-B (Citability Narrative Fix)     [independiente de A]
  |
  +-> FASE-C (Regional Template Fixes)      [independiente de A]
  |
  +--------+------------+
           |
      FASE-D (Validacion E2E)    [depende de A+B+C]
           |
      FASE-E (Integridad Datos)  [depende de A (usa whatsapp_html_detected)]
```

FASE-A, FASE-B y FASE-C son **independientes entre si** (modifican archivos distintos o secciones distintas del mismo archivo sin overlap).

FASE-D (validacion E2E) requiere que A+B+C esten completas.

FASE-E requiere que FASE-A este completada (usa el campo `whatsapp_html_detected` que FASE-A agrego a `CrossValidationResult`). FASE-E es independiente de FASE-B y FASE-C.

---

## Tabla de Conflictos de Archivos

### FASE-E vs fases anteriores

| Archivo | FASE-E | Fases anteriores | Conflicto? |
|---------|--------|------------------|------------|
| main.py | W1 (linea 1766+), R1 (linea 1470+, 2700+), R3 (linea 2691) | Solo lectura en D | NINGUNO |
| v4_diagnostic_generator.py | R2 (linea 413) | A: lineas 750-776, 941-944, 1005-1009, 1786-1794; B: 1850-1860; C: 1608-1627 | NINGUNO (zona distinta) |
| pain_solution_mapper.py | W2 (lineas 315, 332) | Solo lectura en A | NINGUNO |
| web_scraper.py | W3 (linea 1112+) | No tocado en fases previas | NINGUNO |
| coherence_validator.py | W4 (linea 370+) | No tocado en fases previas | NINGUNO |

### Riesgo: BAJO

Todos los fixes de FASE-E tocan zonas distintas de las fases A/B/C. No hay overlap.

### Riesgo interno FASE-E: BAJO

| Fix | Zona | Conflicto con |
|-----|------|---------------|
| R2 (v4_diagnostic_generator.py:413) | Linea 413 | Ninguno dentro de FASE-E |
| W1 (main.py:1766+) | Despues de linea 1766 | Ninguno dentro de FASE-E |
| R1 (main.py:1470+) | Antes de linea 2046 | Ninguno dentro de FASE-E |
| R3 (main.py:2691) | Lejos de las otras zonas | Ninguno dentro de FASE-E |
| W2 (pain_solution_mapper.py:315,332) | Misma funcion | Auto-contenido |
| W3 (web_scraper.py:1112+) | Funcion independiente | Ninguno |
| W4 (coherence_validator.py:370+) | Funcion independiente | Ninguno |

---

## Orden de Ejecucion Recomendado (FASE-E)

1. **R2** — 1 linea en v4_diagnostic_generator, efecto inmediato contra "nacional"
2. **W1** — ~8 lineas en main.py, desbloquea W2 y W4 (campo en ValidationSummary)
3. **R1** — Nueva funcion + llamada en main.py, elimina causa raiz regional
4. **W2** — 3 lineas en pain_solution_mapper, elimina falso positivo pain
5. **W3** — ~5 lineas en web_scraper, captura telefonos perdidos
6. **W4** — ~8 lineas en coherence_validator, coherence gate realista
7. **R3** — 1 linea en main.py, reduccion de falsos "nacional" por URL

---

## Historial de Orden Completo

1. **FASE-A** — Mayor impacto comercial (falso positivo WhatsApp)
2. **FASE-B** — Impacto narrativo (explicacion incorrecta al cliente)
3. **FASE-C** — Impacto visual/template (errores de texto)
4. **FASE-D** — Validacion E2E completa con amaziliahotel.com
5. **FASE-E** — Persistencias detectadas en FASE-D (propagacion de datos)
