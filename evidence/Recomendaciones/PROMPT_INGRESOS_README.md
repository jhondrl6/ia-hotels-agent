# Cómo usar PROMPT_INGRESOS.md con Hermes

## 1. Cambiar de modelo en Hermes (hacer UNA vez)

```bash
# Opción A — Menú interactivo (recomendado):
hermes model

# Opción B — Directo (ejemplo con DeepSeek):
hermes config set model.default deepseek/deepseek-chat
hermes config set model.provider deepseek

# Opción C — En sesión, sin salir de Hermes:
/model deepseek/deepseek-chat
```

Asegúrate de tener el API key en `~/.hermes/.env`:
```
DEEPSEEK_API_KEY=sk-...
```

## 2. Lo que hace diferente a este prompt

No es un prompt genérico de "¿cómo monetizo mi SaaS?". Está calibrado con datos reales extraídos del repositorio:

| Dato en el contexto | De dónde sale |
|---------------------|---------------|
| Nicho: boutique 10-25 hab, Eje Cafetero | `data/benchmarks/regional_adr_2026.json` |
| ADR $420K, ocupación 51.2% | `regional_adr_2026.json` § eje_cafetero.boutique_10_25 |
| Caso Luxorhotel: $3.7M fuga, ROI 2.10X, $400K+$2.5M | `output/v4_complete/01_DIAGNOSTICO...` + `02_PROPUESTA_COMERCIAL...` |
| Competencia: GEO 77 vs 61, SEO 59 vs 25 | `01_DIAGNOSTICO...` § Score de Visibilidad Digital |
| Propuesta de valor: "Nosotros implementamos, usted atiende huéspedes" | `02_PROPUESTA_COMERCIAL...` § LA SOLUCIÓN |

El prompt aprovecha esto para que el modelo responda con precisión de consultor, no con generalidades.

## 3. Flujo de uso (estrategia cache)

### Sesión de CONSULTORÍA (modelo a $10/$50/$1)

```
1. Abre Hermes
2. Pega el BLOQUE DE CONTEXTO de PROMPT_INGRESOS.md (líneas 1-9)
3. Pega el PROMPT PRINCIPAL (líneas 11-25) — puede ir en el mismo mensaje
4. El modelo responde P1 (gap + modelo + roadmap + riesgos). El contexto queda cacheado.
5. Pega P2 → respuesta
6. Pega P3 → respuesta
7. Pega P4 → respuesta
```

NO cierres la sesión entre preguntas — perderías el cache y pagarías $10/Mtok de nuevo por el contexto.

### Costos estimados (sesión completa, 4 turnos)

| Turno | Input (cache) | Output | Costo |
|-------|--------------|--------|-------|
| Contexto + P1 | ~400 tok × $1 | ~800 tok × $50 | ~$0.040 |
| P2 | ~35 tok × $1 | ~250 tok × $50 | ~$0.013 |
| P3 | ~45 tok × $1 | ~350 tok × $50 | ~$0.018 |
| P4 | ~35 tok × $1 | ~200 tok × $50 | ~$0.010 |
| **TOTAL** | | | **~$0.081** |

Sin estrategia de cache: ~$0.40 (5× más). Con el prompt original sin datos de mercado: mismo costo pero respuestas genéricas — el verdadero desperdicio.

### Después de la consultoría

El plan estratégico está definido. Vuelve a tu modelo principal de Hermes para ejecutar (generar assets, código, propuestas a clientes reales).

## 4. Opcional: System prompt fijo

Si vas a iterar variaciones de este prompt, configura instrucciones fijas para no repetirlas:

```bash
hermes config set agent.instructions "Responde en español. Formato tablas y bullets. Sé directo, sin prosa ni saludos."
```

Esto se inyecta en el system prompt (no consume tokens de input de conversación).

## 5. Opcional: Crear un skill con el contexto

Para reutilizar el contexto entre sesiones sin volver a pegarlo:

```bash
mkdir -p ~/.hermes/skills/iah-cli/iah-cli-context
```

Copia el BLOQUE DE CONTEXTO (líneas 1-9 de PROMPT_INGRESOS.md) a un SKILL.md en ese directorio. Luego en sesión:

```
/skill iah-cli-context
```

El skill se carga en system prompt, no quema tokens de conversación y se cachea.

## Referencia rápida de comandos Hermes

| Qué quieres | Comando |
|-------------|---------|
| Cambiar modelo | `hermes model` o `/model` |
| Ver tokens usados | `/usage` |
| Ver configuración | `hermes config` |
| Nueva sesión | `/new` |
| Cargar un skill | `/skill nombre` |
| Salir | `/quit` |
