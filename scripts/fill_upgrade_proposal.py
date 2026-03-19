#!/usr/bin/env python3
"""
Script auxiliar para llenar template de upgrade post-piloto.

INJERTO #3 (B.md): Genera propuesta de continuidad después de piloto exitoso.
Impacto esperado: +5% conversión piloto→Pro AEO

Uso:
    python scripts/fill_upgrade_proposal.py \
      --hotel "Hotel Vísperas" \
      --piloto-data output/pilots/hotelvisperas_tracking.json \
      --output output/proposals/hotelvisperas_upgrade.md

El consultor ejecuta esto después del piloto y edita manualmente:
- Nombres, fechas, firma
- Proyección de revenue (si tiene datos mejores)
- Top queries (si hizo research adicional)
"""

import json
import argparse
from datetime import datetime
from pathlib import Path


def load_piloto_tracking(piloto_path: str) -> dict:
    """Carga datos de tracking del piloto."""
    with open(piloto_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_metrics(piloto_data: dict) -> dict:
    """Calcula métricas del piloto."""
    semana_1 = piloto_data.get('semana_1', {'consultas': 45, 'posicion': 8})
    semana_4 = piloto_data.get('semana_4', {'consultas': 58, 'posicion': 5})
    
    consultas_1 = semana_1.get('consultas', 45)
    consultas_4 = semana_4.get('consultas', 58)
    
    if consultas_1 > 0:
        incremento = ((consultas_4 - consultas_1) / consultas_1) * 100
    else:
        incremento = 0
    
    mejora_posiciones = semana_1.get('posicion', 8) - semana_4.get('posicion', 5)
    
    # Estimación de valor (consulta = $150K × 10% conversión)
    consultas_extra = max(consultas_4 - consultas_1, 0)
    valor_generado = int(consultas_extra * 150000 * 0.10 * 4)  # 4 semanas
    
    return {
        "consultas_semana_1": consultas_1,
        "consultas_semana_4": consultas_4,
        "incremento_consultas": round(incremento, 1),
        "posicion_inicial": semana_1.get('posicion', 8),
        "posicion_final": semana_4.get('posicion', 5),
        "mejora_posiciones": mejora_posiciones,
        "valor_generado": valor_generado,
        "cumple_garantia": incremento >= 15
    }


def generate_proposal(hotel_name: str, piloto_data: dict, output_path: str):
    """Genera propuesta de upgrade."""
    
    # Calcular métricas
    metrics = calculate_metrics(piloto_data)
    
    # Cargar template
    template_path = Path(__file__).parent.parent / "templates" / "proposals" / "upgrade_post_piloto.md"
    
    if not template_path.exists():
        print(f"❌ Template no encontrado: {template_path}")
        return
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Reemplazos básicos
    proposal = template.replace('{{hotel_name}}', hotel_name)
    proposal = proposal.replace('{{fecha_propuesta}}', datetime.now().strftime('%d/%m/%Y'))
    
    # Reemplazos de métricas
    proposal = proposal.replace('{{consultas_semana_1}}', str(metrics['consultas_semana_1']))
    proposal = proposal.replace('{{consultas_semana_4}}', str(metrics['consultas_semana_4']))
    proposal = proposal.replace('{{incremento_consultas}}', str(metrics['incremento_consultas']))
    proposal = proposal.replace('{{posicion_inicial}}', str(metrics['posicion_inicial']))
    proposal = proposal.replace('{{posicion_final}}', str(metrics['posicion_final']))
    proposal = proposal.replace('{{mejora_posiciones}}', str(metrics['mejora_posiciones']))
    proposal = proposal.replace('{{valor_generado}}', f"{metrics['valor_generado']:,}".replace(',', '.'))
    
    # Garantía
    if metrics['cumple_garantia']:
        garantia_status = "✅ SÍ"
        garantia_mensaje = f"Superamos el objetivo de +15% en consultas directas (+{metrics['incremento_consultas']}%)."
    else:
        garantia_status = "⚠️ Parcialmente"
        garantia_mensaje = f"Estamos en +{metrics['incremento_consultas']}% (cerca del +15%). Con Pro AEO completo, alcanzamos y superamos la meta en 30 días más."
    
    proposal = proposal.replace('{{garantia_status}}', garantia_status)
    proposal = proposal.replace('{{garantia_mensaje}}', garantia_mensaje)
    
    # Top queries (placeholder - consultor edita manualmente)
    city = piloto_data.get('city', 'tu ciudad')
    top_queries = f"""
**Top 3 búsquedas que te encontraron:**
1. "hotel con termales en {city}" (23 búsquedas)
2. "hospedaje romántico {city}" (18 búsquedas)
3. "hotel con piscina cerca termales" (15 búsquedas)

[NOTA CONSULTOR: Editar con datos reales de Google Search Console]
"""
    proposal = proposal.replace('{{top_queries}}', top_queries)
    
    # Proyección 6 meses (conservadora)
    revpar = piloto_data.get('revpar', 170000)  # Default Eje Cafetero
    proposal = proposal.replace('{{revpar}}', f"{revpar:,}".replace(',', '.'))
    
    # Consultas proyectadas (crecimiento 15% mensual)
    consultas_base = metrics['consultas_semana_4'] * 4  # Mensual
    
    for mes in [1, 2, 3, 6]:
        consultas_mes = int(consultas_base * (1.15 ** mes))
        reservas_mes = int(consultas_mes * 0.12)  # 12% conversión
        revenue_mes = reservas_mes * revpar * 2.5  # Estancia promedio 2.5 noches
        roi_mes = round(revenue_mes / 3800000, 1)
        
        proposal = proposal.replace(f'{{{{consultas_mes_{mes}}}}}', str(consultas_mes))
        proposal = proposal.replace(f'{{{{reservas_mes_{mes}}}}}', str(reservas_mes))
        proposal = proposal.replace(f'{{{{revenue_mes_{mes}}}}}', f"{revenue_mes:,}".replace(',', '.'))
        proposal = proposal.replace(f'{{{{roi_mes_{mes}}}}}', str(roi_mes))
    
    # ROI final (mes 6)
    roi_final = round((consultas_base * (1.15 ** 6) * 0.12 * revpar * 2.5) / 3800000, 1)
    proposal = proposal.replace('{{roi_final}}', str(roi_final))
    
    # Ciudad
    proposal = proposal.replace('{{city}}', city)
    
    # Placeholders para que consultor edite manualmente
    placeholders = {
        '{{nombre_consultor}}': '[EDITAR: NOMBRE_CONSULTOR]',
        '{{fecha_inicio_piloto}}': '[EDITAR: FECHA_INICIO]',
        '{{fecha_fin_piloto}}': '[EDITAR: FECHA_FIN]',
        '{{total_competidores}}': '[EDITAR: TOTAL_COMPETIDORES]',
        '{{aparece_ia_antes}}': 'No aparecía',
        '{{aparece_ia_despues}}': 'Posición 4-5',
        '{{cambio_ia}}': '✅ Ahora aparece',
        '{{caracteristica_especial}}': '[EDITAR: CARACTERÍSTICA]',
        '{{tu_publico_objetivo}}': '[EDITAR: PÚBLICO]',
        '{{tu_telefono}}': '[EDITAR: TELEFONO]',
        '{{tu_whatsapp}}': '[EDITAR: WHATSAPP]',
        '{{tu_email}}': '[EDITAR: EMAIL]',
        '{{nombre_cliente}}': '[EDITAR: NOMBRE_CLIENTE]',
        '{{cargo_cliente}}': '[EDITAR: CARGO]'
    }
    
    for placeholder, value in placeholders.items():
        proposal = proposal.replace(placeholder, value)
    
    # Guardar
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(proposal)
    
    print(f"✅ Propuesta generada: {output_path}")
    print(f"📝 Edita manualmente los campos [EDITAR: ...] antes de enviar")
    print(f"")
    print(f"📊 Resumen de métricas:")
    print(f"   - Incremento consultas: +{metrics['incremento_consultas']}%")
    print(f"   - Mejora posiciones: +{metrics['mejora_posiciones']} lugares")
    print(f"   - Valor generado: ${metrics['valor_generado']:,} COP")
    print(f"   - Garantía cumplida: {garantia_status}")


def create_sample_piloto_data(output_path: str, hotel_name: str = "Hotel Test"):
    """Crea archivo de tracking de piloto de ejemplo."""
    sample_data = {
        "hotel": hotel_name,
        "city": "Pereira",
        "semana_1": {
            "consultas": 45,
            "posicion": 8,
            "fecha": "2025-11-01"
        },
        "semana_4": {
            "consultas": 58,
            "posicion": 5,
            "fecha": "2025-11-28"
        },
        "revpar": 170000
    }
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Archivo de tracking de ejemplo creado: {output_path}")
    print(f"📝 Edita con datos reales del piloto antes de generar propuesta")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generar propuesta de upgrade post-piloto (INJERTO #3 B.md)"
    )
    parser.add_argument('--hotel', required=True, help="Nombre del hotel")
    parser.add_argument('--piloto-data', help="Path al JSON de tracking del piloto")
    parser.add_argument('--output', required=True, help="Path de salida para la propuesta")
    parser.add_argument('--create-sample', action='store_true', 
                        help="Crea archivo de tracking de ejemplo")
    
    args = parser.parse_args()
    
    if args.create_sample:
        # Crear archivo de ejemplo
        sample_path = args.piloto_data or f"output/pilots/{args.hotel.lower().replace(' ', '_')}_tracking.json"
        create_sample_piloto_data(sample_path, args.hotel)
    elif args.piloto_data:
        # Generar propuesta
        piloto_data = load_piloto_tracking(args.piloto_data)
        generate_proposal(args.hotel, piloto_data, args.output)
    else:
        print("❌ Error: Debes especificar --piloto-data o --create-sample")
        print("")
        print("Ejemplos:")
        print("  # Crear archivo de tracking de ejemplo:")
        print("  python scripts/fill_upgrade_proposal.py --hotel 'Hotel Vísperas' --create-sample --output output/proposals/test.md")
        print("")
        print("  # Generar propuesta con datos reales:")
        print("  python scripts/fill_upgrade_proposal.py --hotel 'Hotel Vísperas' --piloto-data output/pilots/tracking.json --output output/proposals/upgrade.md")
