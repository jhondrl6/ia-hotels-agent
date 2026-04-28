# FASE-1-B-AMAZILIA-CORRECCION: T4 Fix + v4complete + Verificacion

**ID**: FASE-1-B-AMAZILIA-CORRECCION
**Sub-fase de**: FASE-1-AMAZILIA-CORRECCION (plan padre)
**Objetivo**: Corregir el timing GEO (T4) y verificar todos los hallazgos en output regenerado
**Dependencias**: FASE-1-A completada
**Duracion estimada**: 1 sesion (~45 min wall-clock incluyendo v4complete)
**Skill**: `phased_project_executor.md` v2.9.0

---

## Estado del Plan Padre

| Sub-fase | Estado |
|----------|--------|
| FASE-1-A (fixes) | ✅ Completada |
| **FASE-1-B (esta)** | ⏳ En progreso |
| FASE-1-C (docs) | ⏳ Pendiente |

---

## Contexto

**Problema T4 confirmado**: El diagnostico se genera ANTES de que `geo_flow_result.json` exista.

**Arquitectura actual del flujo** (main.py):
```
L2233: diagnostic_gen.generate() → diagnostico SIN geo_flow (09:22:02)
L2416: orchestrator = V4AssetOrchestrator()
L2423: orchestrator.generate_assets() → geo_flow_result.json (09:22:04)
L2448: propuesta se genera
```

**Evidencia**: `geo_flow_result.json` tiene `total_score: 23, band: "critical"` pero el diagnostico `01_DIAGNOSTICO_Y_OPORTUNIDAD_20260428_092202.md` NO tiene row "Salud Tecnica GEO" en su ia_metrics_table.

**Codigo que deberia encontrarlo** (`v4_diagnostic_generator.py` L1288-1302): busca `geo_flow_result.json` si existe. El archivo existe al final de la ejecucion, pero se genero 2 segundos DESPUES del diagnostico.

---

## Tareas

### Tarea 1: T4 — Implementar Segunda Pasada del Diagnostico

**Opcion elegida**: (b) Regenerar diagnostico DESPUES de FASE 4

**Pasos**:
1. Identificar en `main.py` donde se genera la propuesta (L2448) y agregar una segunda llamada a `diagnostic_gen.generate()` DESPUES de que `asset_result` este disponible
2. Reutilizar el mismo `V4DiagnosticGenerator` pero pasando `output_dir` que ya contiene `geo_flow_result.json`
3. El archivo de diagnostico original NO se sobreescribe — se genera con sufijo `_T4FIX` para comparacion

**Alternativa simple**: Modificar el flujo para que la regeneracion del diagnostico (L2233) ocurra DESPUES de L2423 en vez de antes. Esto requiere mover el bloque de regeneracion diagnostico de antes de FASE 4 a despues.

**Archivos afectados**:
- `main.py` (mover regeneracion diagnostico a despues de FASE 4)

**Criterios de aceptacion**:
- [ ] `geo_flow_result.json` existe ANTES de que `diagnostic_gen.generate()` se llame
- [ ] El diagnostico regenerado tiene "Salud Tecnica GEO" en ia_metrics_table
- [ ] v4complete completo ejecuta sin errores

---

### Tarea 2: Ejecutar v4complete

**Protocolo**: Ejecutar directo con `terminal(timeout=600, notify_on_complete=True)`

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/
```

**Inmediatamente despues del output** (protocolo de evidencia proactiva v2.8.0):

```bash
mkdir -p evidence/fase-1-amazilia-correccion
cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/fase-1-amazilia-correccion/
cp output/v4_complete/02_PROPUESTA_*.md evidence/fase-1-amazilia-correccion/
cp output/v4_complete/amaziliahotel/v4_audit/*.json evidence/fase-1-amazilia-correccion/
```

**Criterios de aceptacion**:
- [ ] Ejecucion completa sin errores fatales
- [ ] coherence >= 0.80
- [ ] Publication Readiness: READY

---

### Tarea 3: Verificar Hallazgos en Output

| Finding | Que verificar | Resultado |
|---------|--------------|-----------|
| T4 | "Salud Tecnica GEO" aparece en ia_metrics_table del diagnostico | Buscar row con `Salud Tecnica GEO` en el MD |
| N1 | Solo un header en seccion metricas IA | No debe haber header duplicado "Metricas de Acceso para IA" + "## [NEW] Metricas de Optimizacion para IA" |
| M3 | `can_use` consistente | Comparar can_use en metadata de cada asset vs summary del report |
| M4 | Paths usan `/` en JSON | Verificar que no haya backslashes `\\` en asset_generation_report.json |

**Evidencia a guardar en `evidence/fase-1-amazilia-correccion/`**:
- Nuevo diagnostico regenerado
- Nuevo asset_generation_report.json
- Nuevo coherence_validation.json

---

## Scope R3 — Verificacion

Esta sesion tiene:
- [x] Investigar T4 (1 tarea)
- [x] Implementar fix T4 (1 tarea)
- [x] Ejecutar v4complete (1 comando largo)
- [x] Verificar 4 hallazgos (1 tarea)
- [x] Guardar evidencia proactiva (1 tarea)

**Total**: 4 tareas + 1 comando largo = dentro del limite R3 ✅

---

## Restricciones

- **Maximo 60 iteraciones**. Si se agota, marcar incompleta, guardar evidencia, retomar en sesion nueva.
- **Evidencia obligatoria**: guardar ANTES de cualquier verificacion adicional.
- **NO ejecutar FASE-1-C** hasta que esta fase muestre ✅ en todos los criterios.

---

## Cierre de Sesion (OBLIGATORIO — sin excepciones)

Antes de cerrar, SIEMPRE:

1. **Guardar evidencia** en `evidence/fase-1-amazilia-correccion/`
2. **Actualizar plan padre** `05-prompt-inicio-sesion-fase-1-amazilia-correccion.md`:
   - Si T4 funcionando: marcar FASE-1-B como ✅
   - Si incompleto: marcar como `⏳ INCOMPLETA — checkpoint: X`
3. **Solo entonces** cerrar sesion

---

## Como Iniciar la Nueva Sesion

```
Ejecutar FASE-1-B-AMAZILIA-CORRECCION:
  archivo: C:\Users\Jhond\Github\iah-cli\.opencode\plans\05-prompt-inicio-sesion-fase-1-B-amazilia-correccion.md
```

**Dependencias**:
- FASE-1-A debe estar completada (✅)
- Evidence de sesion anterior en `evidence/fase-1-amazilia-correccion/`
- Output v4complete previo en `output/v4_complete/`

**Checkpoint si se retom a**: leer `05-prompt-inicio-sesion-fase-1-amazilia-correccion.md` (plan padre) para estado global, luego continuar desde Tarea 1 o 2 segun donde se detuvo.
