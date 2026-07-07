## Contexto

BUG-4a fue detectado originalmente en v4complete de Luxorhotel (v4.60.0): OpenRouter devolvia 404 porque el modelo estaba hardcodeado en llm_mention_checker.py. FASE-2 externalizo el modelo al provider_registry.yaml, pero FASE-5 (verificacion E2E) revelo que el 404 persiste.

## Hallazgo (FASE-5 — 2026-07-06)

v4complete ejecutado para Luxorhotel mostro 5 ocurrencias de:

  LLM query failed for openrouter: 404 Client Error: Not Found

El modelo configurado en config/provider_registry.yaml es:

  openrouter:
    default_model: qwen/qwen3.6-plus:free

El codigo en llm_mention_checker.py (linea 245) lee correctamente del registry. El fix de externalizacion funciona — el modelo en si es el que no existe en OpenRouter.

## Causa probable

El modelo qwen/qwen3.6-plus:free no existe, no esta disponible en el plan gratuito, o el endpoint requiere parametros adicionales.

## Impacto

- No bloquea el pipeline: DeepSeek se usa como fallback exitoso
- Afecta solo a llm_mention_checker: las menciones de LLM (IAO score) se pierden
- IA Readiness score subestimado sin datos de LLM mentions

## Posible fix

1. Validar modelos disponibles en OpenRouter para el API key actual
2. Actualizar default_model en provider_registry.yaml a uno vigente
3. Agregar fallback dentro de _query_openrouter() para intentar otro modelo si el default da 404

## Referencias

- Archivo: modules/auditors/llm_mention_checker.py (linea 226-245)
- Config: config/provider_registry.yaml (linea 109)
- Commit FASE-2: 3ab2800
- Evidencia: evidence/FASE-5/
