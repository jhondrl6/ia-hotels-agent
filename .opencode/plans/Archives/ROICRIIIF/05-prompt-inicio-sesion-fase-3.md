# FASE-3: Proposal Semantic Cleanup (SEMANTIC-13)

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: ✅ SUBAGENTE (delegate_task) — cambio localizado
> **Complejidad**: 🟢 BAJA

## Contexto previo

FASE-1 y FASE-2 completadas. Publication readiness aún depende de verificación E2E (FASE-4), pero los fixes principales están aplicados. Queda un issue semántico menor:

**Issue SEMANTIC-13**: La línea ~128 de la propuesta comercial contiene:
```
(13% del dolor priorizado × 35% de recuperación conservadora)
```

El "13%" es un artifact del `pain_ratio` (0.1361) del pricing calculator — NO es un factor de la fórmula de recuperación. La fórmula real ya está correctamente expresada en la línea ~129:
> Fuga mensual × Curva de Maduración × Recovery Factor 35%

La línea ~128 introduce confusión al implicar que el "13% del dolor" es un multiplicador real.

## Objetivo de esta fase

Eliminar o corregir la referencia al "13%" en la plantilla de propuesta para que no presente un artifact de pricing como factor de la fórmula de recuperación.

### Tareas

- [ ] **T1 — Localizar plantilla y generador**: Identificar dónde se genera la línea problemática:
  - Buscar en `modules/commercial_documents/templates/propuesta_v6_template.md` (o similar)
  - Buscar en `modules/commercial_documents/v4_proposal_generator.py` el data dict que alimenta el placeholder
  - Grep: `pain_ratio`, `13%`, `dolor priorizado` en ambos archivos

- [ ] **T2 — Aplicar fix** (una de):
  - **Opción A (eliminar)**: Remover la línea con "13% × 35%" y dejar que la trazabilidad real (línea siguiente con Fuga × Curva × Recovery) hable sola
  - **Opción B (corregir)**: Reemplazar con texto correcto: `(Recuperación proyectada = Σ[Fuga mensual × % Maduración × 35%])`
  - Preferir Opción A (más limpia, la trazabilidad ya existe en línea siguiente)

- [ ] **T3 — Verificar**: Grep del template y generador para confirmar que "13%" y "dolor priorizado" ya no aparecen en output de propuesta

### Prompt para delegate_task

```
Eres un agente especializado en templates de propuestas comerciales para iah-cli.

OBJETIVO: Eliminar el artifact "13% del dolor priorizado" de la plantilla de propuesta comercial.

CONTEXTO:
- Proyecto: /mnt/c/Users/Jhond/Github/iah-cli/
- La línea problemática está en propuesta_v6_template.md (o archivo similar de templates)
- El texto actual es aproximadamente: "(13% del dolor priorizado × 35% de recuperación conservadora)"
- El "13%" viene de pain_ratio (0.1361) del pricing calculator, NO es un factor real de la fórmula
- La fórmula correcta ya está en la línea siguiente: "Fuga mensual × Curva Maduración × Recovery 35%"

TAREAS:
1. Buscar en modules/commercial_documents/templates/ el template de propuesta (propuesta_v6_template.md o similar)
2. Grep por "pain_ratio", "13%", "dolor priorizado" en templates y en v4_proposal_generator.py
3. Eliminar la línea con "13% × 35%" (Opción A preferida — la trazabilidad real ya existe en línea siguiente)
4. Si hay placeholder en el generador que alimenta ese texto, eliminarlo también del data dict
5. Verificar con grep que "13%" ya no aparece en template ni generador
6. Si encuentras tests que referencien ese texto, actualizarlos

RESTRICCIONES:
- Solo modificar archivos en modules/commercial_documents/
- No tocar publication_gates.py ni conditional_generator.py
- No ejecutar v4complete

ENTREGABLES:
- Archivos modificados con diff
- Resultado del grep de verificación
- Lista de tests actualizados (si alguno)
```

### Restricciones

- Solo modificar archivos en `modules/commercial_documents/`
- NO tocar publication_gates.py ni conditional_generator.py
- NO ejecutar v4complete (eso es FASE-4)
- Este fix tiene prioridad BAJA — si T1 revela que el texto ya fue corregido en versión actual, documentar como "already resolved" y cerrar fase

### Criterios de completitud

- [ ] "13% del dolor priorizado" no aparece en template ni generador (verificado con grep)
- [ ] Trazabilidad correcta (Fuga × Curva × Recovery) sigue presente
- [ ] No regresión en formato de propuesta (tablas y secciones intactas)
- [ ] Cascade de docs actualizada (dependencias-fases.md, REGISTRY.md)
- [ ] `log_phase_completion.py` ejecutado con `--fase FASE-3`

### Próxima sesión

FASE-4: v4complete Hotel Castilla Real E2E — ejecución completa con verificación de que los 3 issues fueron superados. Usa delegate_task.
