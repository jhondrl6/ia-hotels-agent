import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from modules.delivery.generators.faq_gen import FAQGenerator

def test_faq_generator_output_has_category_and_timestamp():
    hotel_data = {'nombre': 'Hotel Test', 'ubicacion': 'Test', 'servicios': ['wifi'], 'precio_promedio': '100'}
    generator = FAQGenerator()
    csv_content, _ = generator.generate(hotel_data, count=2, reason='Test')
    lines = csv_content.strip().split('\n')
    # Verificar header con 4 columnas
    header = any('"Pregunta","Respuesta","Categoria","Fecha_Generacion"' in l for l in lines)
    assert header, f"Header debe tener 4 columnas. Lineas: {lines[:3]}"
    # Verificar timestamp ISO 8601 con zona horaria (solo en líneas de datos, no en header)
    for line in lines:
        # Saltar el header y líneas que no parezcan datos CSV
        if line.startswith('"Pregunta","Respuesta"') or line.count(',') < 3:
            continue
        parts = line.split('","')
        if len(parts) >= 4:
            ts = parts[3].rstrip('"')
            assert 'T' in ts and ('+' in ts or '-' in ts.split('T')[1]), f"Timestamp invalido: {ts}"
    print("Test passed!")

if __name__ == '__main__':
    test_faq_generator_output_has_category_and_timestamp()