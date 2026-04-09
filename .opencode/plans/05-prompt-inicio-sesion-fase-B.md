# Prompt de Inicio de Sesion — FASE-B: Citability Narrative Fix

## Contexto

### Documento de referencia
`/mnt/c/Users/Jhond/Github/iah-cli/.opencode/plans/context/whatsapp_false_positive.md` (seccion "BRECHA 5 - Narrativa Imprecisa")

### Estado de Fases Anteriores
- FASE-A (WhatsApp Detection Fix): Completada en sesion previa

### Problema
El diagnostico dice "contenido es insuficiente o poco estructurado" cuando el score de citability es 0. Pero ese score viene de `blocks_analyzed: 0` — el auditor no pudo analizar contenido. El score es un default por ausencia, no una evaluacion real.

La recomendacion del propio audit lo confirma: "Content structure is good. Maintain current paragraph lengths."

---

## Objetivo

Corregir la narrativa para que distinga entre:
- "contenido poco estructurado" (score real bajo, ej: 15/100) → narrativa actual correcta
- "contenido no discoverable por IA" (blocks_analyzed=0) → nueva narrativa: "IA no puede descubrir ni citar el contenido"

---

## Tareas

### T1: Diferenciar score=0 real vs ausencia en _detect_brechas

**Archivo:** `modules/commercial_documents/v4_diagnostic_generator.py` (lineas 1850-1860)

Logica actual:
```python
citability_score = getattr(audit_result, 'citability', None)
if citability_score is not None:
    score_val = getattr(citability_score, 'overall_score', None)
    if isinstance(score_val, (int, float)) and score_val < 30:
        brechas.append({'pain_id': 'low_citability', ...})
```

Nueva logica:
```python
citability_score = getattr(audit_result, 'citability', None)
if citability_score is not None:
    score_val = getattr(citability_score, 'overall_score', None)
    blocks = getattr(citability_score, 'blocks_analyzed', None)
    
    if isinstance(score_val, (int, float)) and score_val < 30:
        if blocks == 0 or blocks is None:
            # Caso: contenido ausente/no discoverable
            brechas.append({
                'pain_id': 'low_citability',
                'nombre': 'Contenido No Discoverable por IA',
                'impacto': 0.10,
                'narrativa': 'ChatGPT y Perplexity no pueden recomendar su hotel porque el contenido no es discoverable para crawlers de IA.'
            })
        else:
            # Caso: contenido existe pero de baja calidad
            brechas.append({
                'pain_id': 'low_citability',
                'nombre': 'Contenido Poco Estructurado para IA',
                'impacto': 0.10,
                'narrativa': 'ChatGPT y Perplexity no recomiendan su hotel porque el contenido es insuficiente o poco estructurado.'
            })
```

### T2: Actualizar narrativa del diagnostico (seccion IA readiness)

**Archivo:** `modules/commercial_documents/v4_diagnostic_generator.py` (lineas ~1044-1061)

Donde se genera la seccion de IA readiness/citability, verificar si la narrativa usa "poco estructurado" cuando deberia decir "no discoverable".

Buscar `citability` en la generacion del texto del diagnostico y ajustar para que use la narrativa correcta segun `blocks_analyzed`.

### T3: Verificar pain_solution_mapper alignment

**Archivo:** `modules/commercial_documents/pain_solution_mapper.py`

Verificar que `low_citability` en el mapper genera el asset correcto (`llms.txt` o `local_content_page`) independientemente de si el contenido es "poco estructurado" o "no discoverable" — el asset sugerido es el mismo.

---

## Criterios de Completitud

- [ ] Brecha `low_citability` con `blocks_analyzed=0` genera narrativa "no discoverable"
- [ ] Brecha `low_citability` con `blocks_analyzed>0` y score<30 genera narrativa "poco estructurado"
- [ ] pain_id `low_citability` sigue mapeando al mismo asset
- [ ] Tests existentes pasan

---

## Archivos a Modificar

| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | Lineas 1850-1860 (logica brecha), ~1044-1061 (narrativa) |

## Post-Ejecucion

- Marcar checklist en `06-checklist-implementacion.md`
- Ejecutar `log_phase_completion.py --fase FASE-B`
- Actualizar `09-documentacion-post-proyecto.md`

## Evidence

```bash
mkdir -p evidence/fase-b
./venv/Scripts/python.exe -m pytest tests/commercial_documents/ tests/asset_generation/ -v --tb=short 2>&1 | tee evidence/fase-b/regression_pre.log
```
