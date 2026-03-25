# Evaluación blueprint capitalización V34


## Evaluación del Blueprint V34_CAPITALIZATION_BLUEPRINT.md

### Pertinencia: **Alta**

El blueprint es pertinente y responde a problemas reales del sistema:
- El **Punto 1 (ISE)** aborda correctamente la dependencia de plantillas estáticas - el `DeliveryManager` actual (manager.py:306-341) genera guías con métodos `_build_*` que son efectivamente templates hardcodeados
- El **Punto 2 (Identidad Técnica)** es necesario - `web_scraper.py` detecta schema y CMS pero NO detecta títulos genéricos como "Just another WordPress site"
- El **Punto 3 (Coherencia)** es crítico - `self_healer.py` valida contra specs pero NO hay validación cruzada entre `analisis_completo.json` y los entregables generados

### Lo que falta para perfeccionarse:

| Aspecto | Problema | Recomendación |
|---------|----------|---------------|
| **Especificidad técnica** | "Motor de Síntesis Dinámica" es vago | Definir interfaz: `generate_contextual_output(hallazgos: List[Dict], tipo: str) -> str` |
| **Criterios de aceptación** | No hay métricas de éxito | Agregar: "El SEO_FIX_KIT debe mencionar el LCP detectado en ≤2 oraciones" |
| **Priorización** | Los 4 puntos parecen iguales | Punto 3 > Punto 1 > Punto 2 > Punto 4 (por impacto en entregables) |
| **Integración con código existente** | No menciona `self_healer.py` ni el flujo actual | El Punto 3 debería extender `SelfHealer.validate_fix()` con `validate_delivery_coherence()` |
| **Estimación** | Sin story points ni esfuerzo | Agregar: Punto 1 (5 SP), Punto 2 (2 SP), Punto 3 (3 SP), Punto 4 (1 SP) |
| **Ejemplos input/output** | No muestra el "antes/después" | Incluir ejemplo del "Caso Vísperas": guía genérica vs. guía quirúrgica |

### Recomendación adicional:

El blueprint debería incluir un **diagrama de flujo** o **secuencia de ejecución** que muestre:
```
WebScraper.audit_identity_sanity() 
    → DeliveryManager.execute() con hallazgos crudos
    → SelfHealer.validate_delivery_coherence()
    → Output certificado
```


## Validación Cruzada: Blueprint vs. CHANGELOG vs. Código Real

### Alineación con Historial de Versiones

| Blueprint Punto | CHANGELOG v3.3.x | Código Actual | Estado Real |
|-----------------|------------------|---------------|-------------|
| **1. Motor ISE** | v3.3.1: "Manager.py 2.0: Reescritura completa" | Templates `_build_*` hardcodeados | ⚠️ **PARCIAL** - Reescribió estructura pero NO implementó síntesis dinámica |
| **2. Identidad Técnica** | v3.3.0: "Triple Triangulación" | `_detectar_cms()` existe, NO `audit_identity_sanity()` | ❌ **FALTA** - El blueprint es correcto |
| **3. Coherencia** | v3.1.0: "Quality Gate + validate_fix" | `self_healer.py:validate_fix()` solo valida Spec, NO coherencia entregas | ❌ **FALTA** - El blueprint es correcto |
| **4. Hospitalidad 4.0** | v3.3.1: "LodgingBusiness + FAQPage" | `schema_gen.py` ya genera esto | ✅ **YA IMPLEMENTADO** - Blueprint desactualizado |

### Problemas de Coherencia Detectados

**1. Blueprint desactualizado en Punto 4:**
El CHANGELOG v3.3.1 ya documenta:
> "Migración del tipo `Hotel` a `LodgingBusiness`... FAQPage JSON-LD"

El blueprint v3.4 propone lo que ya existe. Debería eliminarse o actualizarse.

**2. "Caso Hotel Vísperas" ya resuelto parcialmente:**
CHANGELOG v3.3.1 documenta:
> "Divi/WordPress Fix: Implementada recomendación SEO automática para desactivar sliders en móviles"

Pero el blueprint v3.4 sigue hablando de "Entregas Genéricas" sin reconocer avances.

**3. Falta de trazabilidad con versiones:**
El blueprint dice "v3.4" pero no hay v3.4 en CHANGELOG. Esto indica que es un documento de planeación no versionado.

### Lo que el Blueprint NO considera del CHANGELOG reciente:

| Mejora CHANGELOG | Impacto en Blueprint |
|------------------|---------------------|
| **ROI Guard (v3.3.2)** | La validación de coherencia (Punto 3) debería usar esta lógica |
| **PowerShell Dinámico (v3.3.2)** | Ya extrae datos de `analisis_completo.json` - base para Punto 1 |
| **Certificado de Veracidad (v3.3.0)** | El Punto 4 menciona "Certificado de Veracidad de Datos" que ya existe |

### Recomendaciones para Perfeccionar el Blueprint:

1. **Versionar contra CHANGELOG**: El blueprint debe referenciar "Post v3.3.2" en lugar de "v3.4"

2. **Eliminar Punto 4 redundante**: Schema LodgingBusiness + FAQPage ya están implementados según v3.3.1

3. **Integrar ROI Guard**: El Punto 3 (Coherencia) debería extender `DecisionEngine` (v3.3.2) en lugar de crear nuevo hook

4. **Agregar métricas de éxito**: Siguiendo el patrón del CHANGELOG que cuantifica todo:
   ```
   - Antes: Guías genéricas
   - Después: Guías específicas que mencionan LCP detectado
   ```

5. **Conectar con caso Vísperas real**: El CHANGELOG valida con Hotel Vísperas. El blueprint debería incluir ejemplo concreto de ese caso.

---

