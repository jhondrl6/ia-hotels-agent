import json
import os
import re

def sync_spec():
    json_path = 'data/benchmarks/plan_maestro_data.json'
    md_path = 'data/benchmarks/Plan_maestro_v2_5.md'
    output_path = '.conductor/spec.md'

    print(f"Sincronizando {output_path} desde fuentes de verdad...")

    if not os.path.exists(json_path) or not os.path.exists(md_path):
        print("Error: No se encontraron los archivos del Plan Maestro.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    umbrales = data.get('umbrales_decision', {})
    
    spec_content = f"""# Conductor Specification: IA Hoteles Agent
> Generado automáticamente desde el Plan Maestro. NO EDITAR MANUALMENTE.

## 🎯 Reglas de Negocio y Umbrales (Canónicos)
Toda refactorización técnica debe respetar los siguientes umbrales definidos en el Plan Maestro:

| Umbral | Valor | Descripción |
| :--- | :--- | :--- |
| Impacto Catastrófico | ${umbrales.get('impacto_catastrofico', 'N/A')} | Umbral para Elite PLUS |
| Brecha Conversión Crítica | ${umbrales.get('brecha_conversion_critica', 'N/A')} | Umbral para Pro AEO Plus |
| RevPAR Premium | ${umbrales.get('revpar_premium', 'N/A')} | Umbral para Elite tier |
| Web Score Alto | {umbrales.get('web_score_alto', 'N/A')} | Punto de corte para calidad web |
| GBP Score Bajo | {umbrales.get('gbp_score_bajo', 'N/A')} | Punto de corte para optimización GEO |

## 🛠️ Estándares de Contenido (v2.6.4)
El contenido generado debe cumplir con las reglas de estilo de IA Hoteles:
- Párrafo inicial: Máximo 40 palabras.
- Tablas de datos: Obligatorias en formatos de investigación y expertos.
- Palabras prohibidas: delve, comprehensive, in today's landscape, integral, profundicemos.

## 🛡️ Seguridad y Cumplimiento
- No permitir hardcoding de llaves API (DEEPSEEK, ANTHROPIC, GOOGLE).
- Validar que el `SelfHealer` no degrade la lógica del `DecisionEngine`.
- Asegurar que los activos de delivery se organicen según la estructura de roles v2.5.0.
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"Sincronización completada. {output_path} actualizado.")

if __name__ == "__main__":
    sync_spec()
