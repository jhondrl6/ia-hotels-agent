
# FASE CAUSAL-02: Reestructurar GAP Analyzer (3 pilares -> 2 pilares)

**ID**: FASE-CAUSAL-02
**Objetivo**: El GAP analyzer distribuye la perdida mensual entre 3 pilares (GBP, AEO, IAO). Como IAO = AEO, esta distorsionando la perdida y creando brechas ficticias. Se debe redistribuir entre 2 pilares: GBP y AEO.
**Dependencias**: FASE-CAUSAL-01 (debe estar completada, score AEO unificado)
**Skill**: iah-cli-phased-execution
**Contexto completo**: `.opencode/plans/context/consolidacion_context.md`

---

## Contexto

**Problema**: `modules/analyzers/gap_analyzer.py` calcula 3 gaps y distribuye la perdida proporcionalmente. Los pilares 2 (AEO) y 3 (IAO) miden la misma infraestructura, asi que la perdida se "diluye" entre dos categorias que son esencialmente la misma cosa.

**Logica actual** (aprox lineas 281-334):
```python
geo_benchmark = region_data.get('geo_score_ref', 42)
aeo_benchmark = region_data.get('aeo_score_ref', 18)
iao_benchmark = region_data.get('iao_score_ref', 8)

aeo_score = schema_data.get('score_schema', 0)
iao_score = ia_test.get('iao_score', self._calculate_iao_score(ia_test))

gap_geo = max(0, geo_benchmark - gbp_score)
gap_aeo = max(0, aeo_benchmark - aeo_score)
gap_iao = max(0, iao_benchmark - iao_score)

suma_gaps = gap_geo + gap_aeo + gap_iao
# Luego distribuye proporcionalmente
```

**Logica deseada**: Solo 2 gaps. El IAO benchmark (8) se integra al AEO benchmark (18) o se elimina. La perdida se distribuye entre GBP y AEO.

---

## Tareas

### Tarea 1: Eliminar pilar IAO de gap_analyzer.py

**Archivo**: `modules/analyzers/gap_analyzer.py`

**Cambios especificos**:

1. Eliminar la linea que obtiene benchmark IAO:
   ```python
   # ELIMINAR:
   iao_benchmark = region_data.get('iao_score_ref', 8)
   ```

2. Eliminar calculo de IAO score y gap IAO:
   ```python
   # ELIMINAR:
   iao_score = ia_test.get('iao_score', self._calculate_iao_score(ia_test))
   gap_iao = max(0, iao_benchmark - iao_score)
   ```

3. Modificar la suma de gaps (era 3, ahora es 2):
   ```python
   # ANTES:
   suma_gaps = gap_geo + gap_aeo + gap_iao
   # DESPUES:
   suma_gaps = gap_geo + gap_aeo
   ```

4. Eliminar el bloque "Pilar 3: Momentum IA" (lineas ~325-335) que agrega la brecha de IAO a `brechas_criticas`. El bloque a eliminar luce asi:
   ```python
   # Pilar 3: IAO (Momentum IA)
   if gap_iao > 0:
       peso_iao = gap_iao / suma_gaps
       brechas_criticas.append({
           "nombre": "Momentum IA pendiente",
           ...
       })
   ```

5. **IMPORTANTE**: El metodo `_calculate_iao_score()` de gap_analyzer.py (linea ~385) tambien debe eliminarse si es un metodo propio de esta clase (no confundir con el del generator). Verificar si es un metodo independiente.

### Tarea 2: Ajustar el benchmark AEO si es necesario

Como el gap IAO (benchmark 8) se elimina, hay dos opciones:

**Opcion A (recomendada)**: Dejar el benchmark AEO en 18/100. El gap IAO no contribuye al AEO, simplemente desaparece. La perdida que antes se asignaba a IAO ahora se distribuye proporcionalmente mas equitativamente entre GBP y AEO.

**Opcion B**: Si el benchmark IAO de 8 era parte de una capa adicional que ahora se pierde, se podria incorporar como un "bonus" al benchmark AEO (18 + 8 = 26). Pero esto no tiene sustento tecnico porque AEO ya mide la infraestructura completa.

Ir con Opcion A (la mas simple y honesta).

### Tarea 3: Verificar que las brechas generadas son coherentes

Despues del cambio, las brechas criticas deben ser maximo 2:
- "Pilar 1: GBP sin optimizar" (si gap_geo > 0)
- "Pilar 2: Datos JSON incompletos" (si gap_aeo > 0)

Verificar que estos nombres y descripciones sigan siendo correctos:
- Pilar 1: `GBP y reseñas insuficientes restan visibilidad en mapas y voz cercana.` -> VALIDO
- Pilar 2: `Sin Schema estructurado el hotel no entra en respuestas de IA generativa.` -> VALIDO

---

## Criterios de Aceptacion

- [ ] `gap_analyzer.py` no tiene referencias a `iao_score`, `iao_benchmark`, `gap_iao`, `Momentum IA`
- [ ] `suma_gaps = gap_geo + gap_aeo` (solo 2 componentes)
- [ ] `brechas_criticas` genera maximo 2 brechas (antes generaba 3)
- [ ] La perdida total se distribuye correctamente entre los 2 pilares restantes
- [ ] El archivo no tiene errores de sintaxis Python
- [ ] El metodo `_calculate_iao_score()` de gap_analyzer.py eliminado si existe como metodo propio

---

## Restricciones

- NO cambiar la logica de calculo de `gap_geo` o `gap_aeo`
- NO modificar los nombres de los pilares restantes
- NO tocar `v4_diagnostic_generator.py` (Fase 1)
- NO tocar `report_builder.py` (Fase 3)
- Mantener la distribucion proporcional, solo con 2 gaps en vez de 3

---

## Post-Ejecucion (OBLIGATORIO)

Al terminar esta fase, ejecutar INMEDIATAMENTE:

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python scripts/log_phase_completion.py \
    --fase FASE-CAUSAL-02 \
    --desc "GAP analyzer redistribuido: 3 pilares -> 2 pilares (GBP + AEO)" \
    --archivos-mod "modules/analyzers/gap_analyzer.py" \
    --check-manual-docs
```

---

## Checklist de Completitud

- [ ] gap_analyzer.py no referencia IAO en ninguna forma
- [ ] suma_gaps solo usa gap_geo + gap_aeo
- [ ] brechas_criticas genera maximo 2 brechas
- [ ] Python syntax valida
- [ ] `log_phase_completion.py` ejecutado sin errores
- [ ] REGISTRY.md actualizado
- [ ] No hay [GAP] en DOCUMENTATION AUDIT
