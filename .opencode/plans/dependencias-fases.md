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
           |
      FASE-F (Fix Brotli)        [descubre causa raiz: fixes E no tenian efecto]
```

FASE-A, FASE-B y FASE-C son **independientes entre si**.

FASE-D requiere A+B+C completas.

FASE-E requiere FASE-A completada.

FASE-F descubre que la causa raiz de todas las persistencias es Brotli encoding:
los fixes de FASE-A/E son correctos pero operaban sobre HTML ilegible.

---

## Archivos Tocados por Fase

| Archivo | A | B | C | E | F |
|---------|---|---|---|---|---|
| v4_comprehensive.py | W0 patrones | | | | defensive check |
| v4_diagnostic_generator.py | brecha condicion | narrativa | region contexts, sanitizacion | | |
| main.py | | | | W1, R1, R3 | |
| pain_solution_mapper.py | | | | W2 | |
| coherence_validator.py | | | | W4 | |
| web_scraper.py | | | | W3 | |
| data_structures.py | whatsapp_html_detected | | | | |
| diagnostico_v6_template.md | | | typo | | |
| **http_client.py** | | | | | **Accept-Encoding** |

**Riesgo FASE-F:** MINIMO. Solo toca http_client.py linea 47. No hay overlap con ninguna fase previa.

---

## Historial de Ejecucion

1. **FASE-A** — Mayor impacto comercial (falso positivo WhatsApp)
2. **FASE-B** — Impacto narrativo (explicacion incorrecta al cliente)
3. **FASE-C** — Impacto visual/template (errores de texto)
4. **FASE-D** — Validacion E2E con amaziliahotel.com (region "nacional" persiste)
5. **FASE-E** — Propagacion de datos (W0-W4, R1-R3 aplicados)
6. **FASE-F** — Fix Brotli encoding (causa raiz: HTML binario hace inefectivos todos los fixes)
