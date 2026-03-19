# Conductor Specification: IA Hoteles Agent
> Generado automáticamente desde el Plan Maestro. NO EDITAR MANUALMENTE.

## 🎯 Reglas de Negocio y Umbrales (Canónicos)
Toda refactorización técnica debe respetar los siguientes umbrales definidos en el Plan Maestro:

| Umbral | Valor | Descripción |
| :--- | :--- | :--- |
| Impacto Catastrófico | $6000000 | Umbral para Elite PLUS |
| Brecha Conversión Crítica | $2500000 | Umbral para Pro AEO Plus |
| RevPAR Premium | $180000 | Umbral para Elite tier |
| Web Score Alto | 75 | Punto de corte para calidad web |
| GBP Score Bajo | 60 | Punto de corte para optimización GEO |

## 🛠️ Estándares de Contenido (v2.6.4)
El contenido generado debe cumplir con las reglas de estilo de IA Hoteles:
- Párrafo inicial: Máximo 40 palabras.
- Tablas de datos: Obligatorias en formatos de investigación y expertos.
- Palabras prohibidas: delve, comprehensive, in today's landscape, integral, profundicemos.

## 🛡️ Seguridad y Cumplimiento
- No permitir hardcoding de llaves API (DEEPSEEK, ANTHROPIC, GOOGLE).
- Validar que el `SelfHealer` no degrade la lógica del `DecisionEngine`.
- Asegurar que los activos de delivery se organicen según la estructura de roles v2.5.0.
