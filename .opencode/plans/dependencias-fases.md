# Dependencias entre Fases - Bugfix Sprint post-FASE-B

**Fecha creacion**: 2026-04-08
**Proyecto**: iah-cli v4.25.x Bugfix Sprint
**Base**: Contextos en `.opencode/plans/context/`

---

## Diagrama de Dependencias

```
FASE-C (CRITICOS)          FASE-E (OG Detection)
  BUG-1: import logging      Reutilizar HTML step 2.1
  BUG-2: citability attr     en vez de 2da request
  BUG-3: OG attr name           |
  BUG-4: mobile falsy           |
  |                             |
  v                             v
FASE-D (MEDIOS + Serialization)
  MED-1: metodos duplicados
  MED-2: dict claves dup
  MED-3: confidence case
  MED-4: pipe duplicado
  MED-5: aeo_score /100
  SER-1: seo_elements serialization
  |
  v
FASE-F (Zombies + Code Smells)
  ZMB-1: iao/voice zombie refs
  MEN-1..6: code smells menores
  |
  v
VALIDACION FINAL
  v4complete --url https://amaziliahotel.com/
```

---

## Tabla de Conflictos de Archivos

| Archivo | FASE-C | FASE-D | FASE-E | FASE-F |
|---------|--------|--------|--------|--------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | BUG-1,2,3,4 | MED-1,2,3,5 | - | MEN-1,4,5,6 |
| `modules/auditors/v4_comprehensive.py` | - | SER-1 | HTML reuse | - |
| `modules/auditors/seo_elements_detector.py` | - | - | read-only | - |
| `templates/diagnostico_ejecutivo.md` | - | - | - | ZMB-1 |
| `templates/diagnostico_v4_template.md` | - | - | - | ZMB-2 |
| `modules/utils/benchmarks.py` | - | - | - | ZMB-4 |

### Analisis de Conflictos

1. **v4_diagnostic_generator.py** (2147 lineas): Archivo MAS CONFLICTIVO. Tocado por FASE-C y FASE-D. FASE-F tambien. **Solucion**: Ejecutar secuencialmente C → D → F. Sin paralelismo posible sobre este archivo.

2. **v4_comprehensive.py**: Tocado por FASE-D (serializacion) y FASE-E (HTML reuse). **Solucion**: D antes que E. Sin conflicto si se ejecutan en orden.

3. **Templates**: Solo FASE-F los toca. Sin conflicto.

---

## Reglas de Secuencia

1. FASE-C DEBE ejecutarse primero (4 bugs criticos que afectan produccion)
2. FASE-D depende de FASE-C (misma funcion `_inject_brecha_scores` se limpia en C, se elimina duplicado en D)
3. FASE-E puede ejecutarse en paralelo con FASE-C o FASE-D (archivos diferentes) **PERO** el workflow exige 1 fase/sesion
4. FASE-F depende de FASE-D (confianza en que el generador esta limpio antes de tocar templates)
5. Validacion v4complete con amaziliahotel.com al final

---

## Fases Resumen

| Fase | Tipo | Descripcion | Archivos | Esfuerzo |
|------|------|-------------|----------|----------|
| FASE-C | Bugfix Criticos | 4 bugs en v4_diagnostic_generator.py | 1 archivo | ~15 lineas |
| FASE-D | Bugfix Medios | 5 medios + serializacion SEO | 2 archivos | ~25 lineas |
| FASE-E | Feature Fix | OG detection HTML reuse | 1 archivo | ~10 lineas |
| FASE-F | Limpieza | Zombies + code smells | 4 archivos | ~20 lineas |
