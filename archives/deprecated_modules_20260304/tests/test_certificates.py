from modules.generators.certificate_gen import CertificateGenerator

gen = CertificateGenerator()

# Test Reserva Directa
hotel_data = {'id': 'hvisperas-001', 'nombre': 'Hotel Vísperas'}
cert_rd = gen.generate_reserva_directa_badge(hotel_data)
print('✓ Certificado Reserva Directa:')
print(f'  - Tipo: {cert_rd["certificado"]}')
print(f'  - Estado: {cert_rd["estado"]}')
print(f'  - Vigencia: {cert_rd["vigencia_hasta"]}')

# Test Web Optimizada
cert_wo = gen.generate_web_optimizada_badge(hotel_data)
print('✓ Certificado Web Optimizada:')
print(f'  - Tipo: {cert_wo["certificado"]}')
print(f'  - Estado: {cert_wo["estado"]}')
print(f'  - Vigencia: {cert_wo["vigencia_hasta"]}')
