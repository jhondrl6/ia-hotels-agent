# FASE-B: Quick Wins en Lenguaje de Dueño (F1) + Disclaimer Tier C → Gancho (F2)

**ID**: FASE-B
**Objetivo**: Corregir 2 fricciones de copywriting: (F1) Quick Wins actualmente en lenguaje técnico/desarrollador, (F2) disclaimer Tier C apologético que erosiona confianza del dueño.
**Dependencias**: FASE-A ✅ (deseable pero no bloqueante — modifican archivos distintos)
**Duración estimada**: 1-2 horas
**Skill**: `phased_project_executor`

---

## Contexto

La validación de `Prospección.md` contra el output de v4complete detectó 2 fricciones en el copywriting del diagnóstico:

- **F1**: Los Quick Wins (Sección 5) dicen "Implementar Schema de Hotel", "Crear Schema FAQ", "Subir Fotos a GBP". El dueño lee "Schema" y "Rich Snippets" y piensa "esto lo tiene que hacer mi técnico". Lo pospone.
- **F2**: La Sección 3 muestra "⚠️ Precisión limitada — Tier C / Datos insuficientes para cálculo preciso / ADR basado en estimado". Suena a "no estamos seguros de nuestro propio número". El dueño huele la duda.

Ambos se generan en `v4_diagnostic_generator.py`:
- `_build_quick_wins()` genera F1
- `_prepare_financial_template_vars()` emite el `precision_warning` de F2

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A | ⏳ Pendiente |

### Base Técnica Disponible
- `modules/commercial_documents/v4_diagnostic_generator.py` — `_build_quick_wins()` y `_prepare_financial_template_vars()`
- `config/commercial.yaml` — posible fuente de texto de Quick Wins
- `modules/commercial_documents/templates/diagnostico_v6_template.md` — placeholders `${quick_wins_content}` y `${precision_warning}`
- Output referencia: `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260525_150325.md` L82-87 (F2), L113-118 (F1)

---

## Tareas

### Tarea 1: Investigar `_build_quick_wins` y `_prepare_financial_template_vars` (F1+F2)

**Objetivo**: Localizar exactamente dónde se genera el texto de Quick Wins y el precision_warning.

**Archivos a investigar**:
- `modules/commercial_documents/v4_diagnostic_generator.py` — buscar `_build_quick_wins`, `quick_wins_content`, `precision_warning`
- `config/commercial.yaml` — verificar si Quick Wins se configuran aquí
- `modules/commercial_documents/templates/diagnostico_v6_template.md` — confirmar placeholders

**Criterios de aceptación**:
- [ ] Localizada la fuente exacta del texto de Quick Wins
- [ ] Localizada la fuente exacta del `precision_warning`
- [ ] Identificado si usa `commercial.yaml` o está hardcodeado

### Tarea 2: Reformular Quick Wins en lenguaje de dueño (F1)

**Objetivo**: Cambiar el output de Quick Wins de acciones técnicas a acciones del dueño + delegación.

**Texto actual**:
```
1. Implementar Schema de Hotel - Impacto SEO inmediato (1-2 días)
2. Crear Schema FAQ - Capturar rich snippets (2-3 días)
3. Subir Fotos a GBP - Mejorar visibilidad local (1 día)
```

**Texto objetivo**:
```
1. HOY (5 minutos): Corregir el número de WhatsApp en Google Maps.
   → Usted mismo puede hacerlo desde su celular.
2. ESTA SEMANA (1 hora): Subir 10 fotos REALES y RECIENTES a Google Maps.
   → El algoritmo premia hoteles con fotos nuevas.
3. DELEGAR A IA HOTELES AGENT: Instalar el "Traductor para IAs" en su web.
   → Nosotros nos encargamos. En 72h ChatGPT y Google podrán recomendar su hotel.
```

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` — método `_build_quick_wins()` o equivalente
- `config/commercial.yaml` — si los textos se configuran aquí

**Criterios de aceptación**:
- [ ] Cada Quick Win incluye: timeframe + acción concreta + quién la ejecuta
- [ ] Lenguaje no técnico (sin "Schema", "Rich Snippets", "GBP")
- [ ] Al menos 1 item es delegable ("nosotros nos encargamos")
- [ ] El primer item es algo que el dueño PUEDE hacer hoy

### Tarea 3: Convertir disclaimer Tier C en "Oportunidad de Auditoría Profunda" (F2)

**Objetivo**: Reemplazar el mensaje apologético de precisión limitada por un gancho comercial que convierte la limitación en oportunidad.

**Texto actual**:
```
⚠️ Precisión limitada — Tier C
- Datos insuficientes para cálculo preciso
- ADR basado en estimado
- Los valores mostrados son estimaciones
```

**Texto objetivo**:
```
💡 OPORTUNIDAD DE AUDITORÍA PROFUNDA

La cifra de $3.7M COP/mes está calculada con benchmarks reales del Eje Cafetero.
En la Fase 2 (Propuesta Comercial), conectaremos su motor de reservas y GA4
para entregarle la CIFRA EXACTA al peso, con evidencia verificable.
```

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` — `_prepare_financial_template_vars()`, variable `precision_warning`

**Criterios de aceptación**:
- [ ] El mensaje NO dice "precisión limitada" ni "datos insuficientes"
- [ ] Convierte la limitación en oportunidad ("conectaremos su motor de reservas")
- [ ] Menciona la Fase 2 como siguiente paso concreto
- [ ] Mantiene honestidad (no promete precisión que no tiene)

### Tarea 4: Verificar fixes con tests existentes

**Objetivo**: Ejecutar tests relacionados.

**Comandos**:
```bash
pytest tests/commercial_documents/ -v -k "quick_win or precision or financial_placeholder" 2>/dev/null || echo "No specific tests found"
python scripts/run_all_validations.py --quick
```

**Criterios de aceptación**:
- [ ] Sin regresiones en tests existentes
- [ ] `run_all_validations.py --quick` pasa 4/4

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_fase_f_financial_placeholders.py` | `tests/commercial_documents/` | Sin regresiones |
| `run_all_validations.py --quick` | `scripts/run_all_validations.py` | 4/4 checks |

---

## Post-Ejecución (OBLIGATORIO)

Al finalizar esta fase:

1. **`dependencias-fases.md`**: Marcar FASE-B como ✅ Completada
2. **`06-checklist-implementacion.md`**: Marcar items F1 y F2 como completados
3. **`09-documentacion-post-proyecto.md`**: Actualizar secciones A, B, D, E

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-B \
    --desc "Fix F1 (Quick Wins lenguaje dueño) + F2 (Disclaimer Tier C → Oportunidad Auditoría)" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py,config/commercial.yaml" \
    --tests "0" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] F1: Quick Wins reformulados con acciones del dueño + delegación
- [ ] F2: Disclaimer Tier C convertido en "Oportunidad de Auditoría Profunda"
- [ ] Tests existentes pasan sin regresiones
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] `dependencias-fases.md` actualizado
- [ ] `06-checklist-implementacion.md` actualizado
- [ ] `09-documentacion-post-proyecto.md` actualizado
- [ ] `log_phase_completion.py` ejecutado

---

## Restricciones

- NO modificar la lógica de Tier (el cálculo de A/B/C es correcto)
- NO modificar `scenario_calculator.py`
- NO ejecutar v4complete
- Máximo 60 iteraciones de agente
