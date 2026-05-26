# FASE-0: Comercial Viability — Decisión Comercial Previa a FASE-A

**ID**: FASE-0
**Objetivo**: Evaluar y resolver el desbalance estructural entre precio del servicio y recovery realista para Hotel Castilla Real — ANTES de invertir en los 10 fixes técnicos de FASE-A a FASE-D.
**Dependencias**: Ninguna (fase inicial — precede a todas las demás)
**Duración estimada**: 1 sesión (exploratoria/-decisional)
**Skill**: `iah-cli-phased-execution`

---

## Contexto

### El problema que FASE-0 resuelve

El ROI_AUDIT.md (2026-05-26) documentó un hecho comercial irreducible por código:

```
Inversión mensual:        $1,200,000 COP
Recovery realista/mes:     $305,472 COP  (pain_ratio 41% × recovery 20%)
Resultado neto/mes:         -$894,528 COP
Resultado neto/6m:        -$5,367,168 COP
ROI a 6 meses:                 0.3X
```

El recovery de ~$305K/mes es **realista para un hotel de 10 habitaciones sin GA4** según el modelo financiero. El precio mínimo de $1.2M/mes es un floor del tier boutique. El gap NO es un bug de fórmula — es estructural.

**Aplicar los 10 fixes de FASE-A a FASE-D tiene sentido solo si antes se resuelve la ecuación comercial**, porque:

1. FASE-A a FASE-D son mejoras de presentación y transparencia — no cambian el ROI
2. Si la propuesta se envía con ROI negativo ($5.3M perdidos en 6 meses), no cierra
3. Gastar 5 sesiones de implementación en technically-correct pero commercially-deadly no tiene ROI para el proyecto

### Decisiones requeridas antes de continuar

4 opciones documentadas en ROI_AUDIT.md PARTE 6. Jhond debe elegir cuál se implementa:

---

## Análisis y Recomendación del Agente

### Perfil de Hotel Castilla Real

| Factor | Valor | Implicación |
|--------|-------|-------------|
| Habitaciones | 10 | Tier boutique |
| Canal directo | ~20% | 80% de reservas via OTA |
| GA4 | No configurado | Sin datos reales de tráfico |
| Tier evidencia | B (benchmarks + web) | El recovery es estimativo |
| ADR detectado | $300K (benchmark hardcodeado) | Fallback, no dato real |
| Pain ratio | ~41% artifact del min_price floor | No es "% IAO" |
| Escenario optimistic | **Negativo** (-$270K/mes) | Incluso el mejor escenario pierde |

### Análisis de las 4 opciones

**Opción A — Lower pricing ($300-400K/mes)**
- El recovery ($305K) cubre el precio al precio de equilibrio
- Conecta GA4 enonth-2, recalcula con datos reales
- **Pros**: ROI positivo desde el mes 1; reduce riesgo percibido
- **Contras**: 4x menos revenue que el pricing actual; requiere que el cliente acepte "onboarding fee"

**Opción B — Quick wins primero (proyecto único $200-400K)**
- Vende WhatsApp fix + Schema Hotel + llms.txt como proyecto puntual
- Sin contrato mensual; upsell posterior con datos reales
- **Pros**: Cierra hoy con bajo riesgo para el cliente; genera goodwill y datos
- **Contras**: Sin retainer recurrente; revenue predecible menor

**Opción C — % del recovery real (15%)**
- Fee = 15% del recovery mensual (~$45K si recovery=$305K)
- Alinea incentivos: si el cliente no recupera, tampoco pagamos
- **Pros**: El cliente solo paga si hay resultados; cierra objeciones de ROI
- **Contras**: Requiere tracking primero; 85% del recovery se queda en el cliente

**Opción D — Transparencia total (precio actual $1.2M + tracking Day 1)**
- Mantener el precio; aceptar que el ROI proyectado es negativo
- Diferenciarse por la garantía de medición real desde el Día 1
- **Pros**: Preserva revenue completo; honestidad como ventaja competitiva
- **Contras**: Si el cliente pregunta "cuánto voy a ganar", la respuesta es "menos de lo que pagas"

---

## RECOMENDACIÓN ORIGINAL: Opción B + C combinadas

### Por qué no es una ni la otra sola

- **Opción B sola**: Entrega valor tangible (quick wins) pero no hay retainer recurring
- **Opción C sola**: Alinea incentivos pero necesita baseline de medición (sin GA4, sin historial)
- **Opción D**: Respetable comercialmente pero cierra conversaciones con clientes metric-oriented

### Estructura recomendada para Castilla Real

**Fase 1 — Activación (Opción B)**
- Precio: $250,000 COP proyecto único
- Duración: 1-2 semanas
- Entregables: WhatsApp conflict resolution + Schema Hotel + llms.txt
- Rol: Generar quick win visible + datosbaseline para recalcular

**Fase 2 — Monetización (Opción C)**
- Precio: 15% del recovery mensual real (medido post-activación)
- Trigger: Después del Día 30 con datos de GA4 o tracking instalado
- Beneficio: Si la activación generó recovery demostrable, el modelo 15% cobra por resultados
- Alineación perfecta: Incentivos 100% alineados — solo cobramos si funciona

### Por qué esta combinación funciona para Castilla Real

1. **Hotel de 10 hab, 20% canal directo**: El gap entre fuga y recovery es enorme ($3.7M vs $305K/mes). No hay pricing que cierre el ROI inmediato con el modelo actual. La estructura en fases elimina la confrontación con el ROI negativo.

2. **Sin GA4**: Empezar con un proyecto de $250K sin GA4 es apropiado — el riesgo es bajo para el cliente y genera los datos que precisamos para la Fase 2.

3. **Upsell natural**: Después de ver que el Schema Hotel y llms.txt mejoran la citabilidad en IA, el cliente tiene curiosidad por más. La Fase 2 se vende sola si la Fase 1交付a resultados.

4. **Mercado objetivo (Colombia, Eje Cafetero)**: Hoteles boutique receptivos a pitch de "usted vea resultados 먼저, después pagamos". La estructura de fases reduce la barrera de entrada.

---

## Opción E propuesta durante la ejecución

Además de las cuatro opciones iniciales y la combinación B+C, se propuso una variante comercial superior:

**Opción E — Piloto con crédito a retainer + success fee capped**
- Fase 1: activación/piloto $250K COP, 1-2 semanas
- El valor del piloto se acredita contra un retainer futuro si el hotel continúa antes de 30 días
- Fase 2: 15% del recovery mensual real atribuible, con techo sugerido hasta $1.2M/mes mientras se valida escala
- Ventaja sobre B+C: evita la objeción de "pago dos veces" y conserva upside sin prometer ROI no medido

**Decisión operativa FASE-0**: avanzar con Opción E como recomendación comercial para Hotel Castilla Real.

---

## Recursos de referencia para la decisión

El análisis completo de las 4 opciones está en:
- `.opencode/context/ROI_AUDIT.md` → PARTE 6: Opciones Comerciales

La validación del cálculo del ROI negativo:
- `.opencode/context/ROI_AUDIT.md` → PARTE 3: El ROI negativo: problema comercial, NO de fórmula
- `.opencode/context/ROI_AUDIT.md` → PARTE 0.4: Scenario Calculator (57% supuestos verificados)

---

## Tareas

### Tarea 1: Documentar la decisión

Crear/actualizar `.opencode/plans/ROI-REFACTOR/09-documentacion-post-proyecto.md` con:

```markdown
## F. Registro de Ejecución — FASE-0

| Opción evaluada | Análisis | Decisión |
|----------------|----------|----------|
| A — Lower pricing | [1 párrafo] | ✅/❌ |
| B — Quick wins | [1 párrafo] | ✅/❌ |
| C — % recovery | [1 párrafo] | ✅/❌ |
| D — Transparencia | [1 párrafo] | ✅/❌ |
| **Combinación B+C** | [1 párrafo] | **ELEGIDA** |
```

### Tarea 2: Actualizar poesía de dependencias

Actualizar `dependencias-fases.md`:
- Agregar FASE-0 al inicio de la tabla de fases
- Cambiar numeración: A→1, B→2, C→3, D→4, E→5
- Actualizar gráfica de dependencias para incluir FASE-0

### Tarea 3: Documentar el pricing de Fase 1 si decisión B+C

Si se elige B+C, documentar:
```markdown
## Pricing Preliminar — Fase 1 Activación

| componente | precio |
|------------|--------|
| WhatsApp conflict guide | Incluido |
| Schema Hotel instalación | Incluido |
| llms.txt | Incluido |
| Diagnóstico completo | Incluido |
| **Total proyecto único** | **$250,000 COP** |
| Duración estimada | 1-2 semanas |
```

---

## Post-Ejecución (OBLIGATORIO)

⚠️ NO OMITIR ⚠️

1. `ROI-REFACTOR/09-documentacion-post-proyecto.md` → Sección F (Registro FASE-0)
2. `ROI-REFACTOR/dependencias-fases.md` → FASE-0 completada
3. `ROI-REFACTOR/README.md` → actualizado con FASE-0 en tabla de fases (antes de FASE-A)

4. Ejecutar documentation cascade:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli && \
cmd.exe /c "venv\Scripts\python.exe scripts\log_phase_completion.py \
    --fase FASE-0 \
    --desc "ROI-REFACTOR FASE-0: Decisión comercial — Opción B+C (Activación $250K + % recovery Fase 2)" \
    --archivos-mod "ROI-REFACTOR/09-documentacion-post-proyecto.md,ROI-REFACTOR/dependencias-fases.md,ROI-REFACTOR/README.md" \
    --tests 0 \
    --check-manual-docs"
```

---

## Criterios de Completitud (CHECKLIST)

- [x] Análisis de las 4 opciones (+ B+C + opción E) presentado
- [x] Recomendación del agente fundamentada
- [x] Decisión operativa registrada en `09-documentacion-post-proyecto.md`
- [x] Pricing de Fase 1 documentado
- [x] `dependencias-fases.md` actualizado con numeración/estado corregido
- [x] `README.md` del plan actualizado
- [x] `log_phase_completion.py` ejecutado

---

## Restricciones

- NO modificar código de iah-cli en esta fase
- NO ejecutar v4complete — eso es FASE-E (ex Fase 5)
- NO inflar numbers ni cambiar fórmulas
- Máximo 60 iteraciones de agente
