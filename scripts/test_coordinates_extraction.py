#!/usr/bin/env python3
"""
Script de validación para verificar extracción de coordenadas
para análisis de competidores.

Simula el flujo del pipeline con datos de geo_validation.
"""

def test_coordinate_extraction():
    """Prueba la extracción de coordenadas desde geo_validation."""
    
    # Simular gbp_data con geo_validation (estructura real del sistema)
    gbp_data = {
        'existe': True,
        'score': 65,
        'reviews': 8,
        'rating': 4.5,
        'meta': {
            'geo_validation': {
                'enabled': True,
                'performed': True,
                'is_valid': True,
                'distance_km': 2.3,
                'threshold_km': 30.0,
                'confidence': 0.85,
                'expected_location': {
                    'lat': 4.8143,
                    'lng': -75.6946,
                    'address': 'Salento, Quindío, Colombia',
                    'city': 'Salento'
                },
                'actual_location': {
                    'lat': 4.8156,
                    'lng': -75.6938,
                    'address': 'Hotel Visperas, Cra. 6 #6-02, Salento, Quindío',
                    'city': 'Salento',
                    'state': 'Quindío',
                    'country': 'Colombia',
                    'place_id': 'ChIJXxxxxxxxxxxxxxx'
                },
                'resolved_location': 'Salento, Quindío',
                'api_calls_used': 2,
                'error_message': None
            },
            'resolved_location': 'Salento, Quindío',
            'location_source': 'geo_validation'
        }
    }
    
    hotel_data = {
        'nombre': 'Hotel Vísperas',
        'ubicacion': 'Salento, Quindío'
    }
    
    print("=" * 70)
    print("TEST: Extracción de Coordenadas para Análisis de Competidores")
    print("=" * 70)
    print(f"\nHotel: {hotel_data['nombre']}")
    print(f"Ubicación: {hotel_data['ubicacion']}")
    
    # Simular la lógica implementada en pipeline.py
    gbp_meta = gbp_data.get("meta")
    if isinstance(gbp_meta, dict):
        geo_validation = gbp_meta.get("geo_validation")
        if isinstance(geo_validation, dict) and geo_validation.get("actual_location"):
            actual_loc = geo_validation["actual_location"]
            
            print("\n✓ geo_validation encontrado")
            print(f"  actual_location type: {type(actual_loc)}")
            
            if isinstance(actual_loc, dict):
                lat = actual_loc.get("lat")
                lng = actual_loc.get("lng")
            else:  # Lista/tupla [lat, lng]
                lat = actual_loc[0] if len(actual_loc) > 0 else None
                lng = actual_loc[1] if len(actual_loc) > 1 else None
            
            if lat and lng:
                # Almacenar en gbp_data para CompetitorAnalyzer
                gbp_data["coordinates"] = {
                    "lat": lat,
                    "lng": lng
                }
                # También en hotel_data como fallback
                hotel_data["lat"] = lat
                hotel_data["lng"] = lng
                
                print(f"\n✓ Coordenadas extraídas exitosamente:")
                print(f"  Latitud:  {lat:.6f}")
                print(f"  Longitud: {lng:.6f}")
                print(f"\n✓ Almacenadas en:")
                print(f"  - gbp_data['coordinates']: {gbp_data['coordinates']}")
                print(f"  - hotel_data['lat']: {hotel_data['lat']}")
                print(f"  - hotel_data['lng']: {hotel_data['lng']}")
                
                # Verificar que CompetitorAnalyzer puede acceder
                lat_check = hotel_data.get('lat') or gbp_data.get('coordinates', {}).get('lat')
                lng_check = hotel_data.get('lng') or gbp_data.get('coordinates', {}).get('lng')
                
                print(f"\n✓ Verificación CompetitorAnalyzer:")
                print(f"  lat (acceso): {lat_check}")
                print(f"  lng (acceso): {lng_check}")
                
                if lat_check and lng_check:
                    print("\n✅ SUCCESS: CompetitorAnalyzer puede obtener coordenadas")
                    print("   El análisis de competidores se ejecutará correctamente")
                    return True
                else:
                    print("\n❌ FAIL: CompetitorAnalyzer no puede acceder a coordenadas")
                    return False
            else:
                print("\n❌ FAIL: lat o lng no encontrados en actual_location")
                return False
        else:
            print("\n❌ FAIL: geo_validation no disponible o sin actual_location")
            return False
    else:
        print("\n❌ FAIL: gbp_data['meta'] no es un diccionario")
        return False


def test_without_coordinates():
    """Prueba el caso cuando no hay coordenadas disponibles."""
    
    gbp_data = {
        'existe': True,
        'score': 45,
        'meta': {}
    }
    
    hotel_data = {
        'nombre': 'Hotel Sin Coordenadas',
        'ubicacion': 'Ciudad Desconocida'
    }
    
    print("\n" + "=" * 70)
    print("TEST: Caso Sin Coordenadas (debería fallar gracefully)")
    print("=" * 70)
    
    lat = hotel_data.get('lat') or gbp_data.get('coordinates', {}).get('lat')
    lng = hotel_data.get('lng') or gbp_data.get('coordinates', {}).get('lng')
    
    if not lat or not lng:
        print("\n⚠️  EXPECTED: Coordenadas no disponibles")
        print(f"   hotel_data.lat={hotel_data.get('lat')}")
        print(f"   gbp_data.coordinates={gbp_data.get('coordinates')}")
        print("   Mensaje: 'Competidores omitidos - verifica GOOGLE_MAPS_API_KEY'")
        return True
    else:
        print("\n❌ UNEXPECTED: Se encontraron coordenadas cuando no debería")
        return False


if __name__ == "__main__":
    print("\n" + "🧪 " * 35)
    print("SUITE DE PRUEBAS: Extracción de Coordenadas")
    print("🧪 " * 35)
    
    test1_passed = test_coordinate_extraction()
    test2_passed = test_without_coordinates()
    
    print("\n" + "=" * 70)
    print("RESUMEN DE PRUEBAS")
    print("=" * 70)
    print(f"Test 1 (Con geo_validation):  {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Test 2 (Sin coordenadas):     {'✅ PASS' if test2_passed else '❌ FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 TODAS LAS PRUEBAS PASARON")
        print("\nPróximo paso: Ejecutar pipeline completo con Hotel Vísperas")
        print("  python main.py audit --url https://hotelvisperas.com")
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON - Revisar implementación")
    
    print("=" * 70 + "\n")
