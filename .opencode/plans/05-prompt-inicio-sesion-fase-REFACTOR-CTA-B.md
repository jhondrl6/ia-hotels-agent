# Prompt de Inicio de Sesion — FASE-REFACTOR-CTA-B (v4complete + Verificacion)

## Contexto

La fase A ya refactorizo el CTA de onboarding en `v4_diagnostic_generator.py` y actualizo los tests. Esta fase B ejecuta un **v4complete real** sobre Hotel Castilla Real para verificar que el CTA refactorizado renderiza correctamente en un documento vivo.

**Hotel:** Hotel Castilla Real  
**URL:** https://www.hotelcastillareal.com/  
**Comando:** `v4complete`

## Tareas Especificas

### Tarea 1: Ejecutar v4complete

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe main.py v4complete --url https://www.hotelcastillareal.com/
```

- Usar `terminal(timeout=600)` para el comando
- Esperar a que complete (5-10 minutos)
- Si falla por timeout, reintentar una vez

### Tarea 2: Guardar evidencia proactiva (OBLIGATORIO)

Inmediatamente despues de que v4complete genere output:

```bash
mkdir -p evidence/FASE-REFACTOR-CTA-B
cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/FASE-REFACTOR-CTA-B/
cp output/v4_complete/02_PROPUESTA_*.md evidence/FASE-REFACTOR-CTA-B/
cp output/v4_complete/*/v4_audit/*.json evidence/FASE-REFACTOR-CTA-B/ 2>/dev/null || true
```

Esto es obligatorio sin importar cuanto tiempo quede en el presupuesto.

### Tarea 3: Verificar CTA en el diagnostico generado

1. Identificar el hotel_id usado (probablemente `hotelcastillareal` o similar) buscando en `output/v4_complete/`.
2. Leer el archivo `01_DIAGNOSTICO_*.md` generado.
3. Buscar la seccion **Impacto Financiero** (donde aparece el CTA).
4. Verificar que el CTA contiene los 4 datos especificos:
   - "habitaciones"
   - "reservas"
   - "reserva" (valor promedio de reserva)
   - "canal directo"
5. Si el hotel resulto ser Tier A/B (can_show_exact=True), el CTA estara vacio (``). Esto es correcto; documentarlo.
6. Si el hotel es Tier C y el CTA NO contiene los 4 datos, reportar como bug y detener.

**Comando util para verificar:**
```bash
grep -n "habitaciones\|reservas\|canal directo" evidence/FASE-REFACTOR-CTA-B/01_DIAGNOSTICO_*.md
```

## Criterios de Completitud

- [x] v4complete ejecutado exitosamente para Hotel Castilla Real
- [x] Evidencia copiada a `evidence/FASE-REFACTOR-CTA-B/`
- [x] CTA verificado en el diagnostico generado (Tier C confirmado)
- [x] Los 4 datos estan presentes en el CTA (habitaciones, reservas, reserva, canal directo)
- [x] Estado anotado en este prompt/plan

## Resultado de Verificacion

**Hotel:** Hotel Castilla Real (hotelcastillareal)
**Tier:** C (datos insuficientes — sin onboarding)
**CTA:** ✅ PRESENTE con los 4 datos
- Linea 120: "Complete el onboarding con sus datos reales: número de habitaciones, reservas mensuales promedio, valor promedio de reserva (COP) y porcentaje de canal directo."
**Content Scrubber:** 3 fixes aplicados (COP COP->COP, passo->paso, booking->reserva)
**Coherence:** 0.74 (debajo de umbral 0.8 — modo no-bloqueante)
**Fecha:** 2026-05-05 20:27

## Restricciones

- **Maximo 60 iteraciones** por sesion (R2)
- **No modificar codigo fuente** en esta fase — solo verificar
- **No ejecutar tests** — eso fue en fase A
- Si v4complete falla por error de red/API, guardar logs y reportar

## Archivos Involucrados

| Archivo | Tipo | Accion |
|---------|------|--------|
| `output/v4_complete/01_DIAGNOSTICO_*.md` | Output generado | Leer y verificar |
| `evidence/FASE-REFACTOR-CTA-B/` | Directorio nuevo | Crear y copiar evidencia |

## Post-Ejecucion

1. Marcar esta fase como ✅ en `.opencode/plans/06-checklist-implementacion.md`
2. Anotar resultado de la verificacion (Tier detectado, CTA presente/ausente, paso/fallo)
3. La siguiente sesion ejecutara **FASE-REFACTOR-CTA-C** (docs cascade)
