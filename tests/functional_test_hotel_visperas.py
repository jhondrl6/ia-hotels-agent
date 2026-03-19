"""Test Funcional: Hotel Visperas - Auditoria completa GBP"""
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.scrapers.gbp_auditor import GBPAuditor
from modules.scrapers.gbp_photo_auditor import integrate_photo_auditor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def save_results(profile_data, output_path):
    """Guardar resultados en JSON"""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(profile_data, f, indent=2, ensure_ascii=False)
    logger.info(f"Resultados guardados en: {output_file}")


def test_hotel_visperas():
    """Test funcional para Hotel Visperas"""
    print("\n" + "="*70)
    print("TEST FUNCIONAL: HOTEL VISPERAS")
    print("="*70)
    
    hotel_config = {
        'nombre': 'Hotel Visperas',
        'ubicacion_input': 'Salento, Quindio',
    }
    
    print(f"\nConfiguracion:")
    print(f"   Hotel: {hotel_config['nombre']}")
    print(f"   Ubicacion: {hotel_config['ubicacion_input']}")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f"tests/results/visperas_audit_{timestamp}.json"
    
    try:
        print("\n[1/5] Inicializando GBPAuditor...")
        auditor = GBPAuditor(headless=True)
        print("      [OK]")
        
        print("\n[2/5] Integrando PhotoAuditor...")
        integrate_photo_auditor(auditor)
        print("      [OK]")
        
        print(f"\n[3/5] Ejecutando auditoria para '{hotel_config['nombre']}'...")
        print("      (Esto puede tomar 60-120 segundos...)")
        
        profile = auditor.check_google_profile(
            hotel_name=hotel_config['nombre'],
            location=hotel_config['ubicacion_input']
        )
        print("      [OK] Auditoria completada")
        
        print("\n[4/5] Analizando resultados...")
        
        existe = profile.get('existe', False)
        rating = profile.get('rating', 0)
        reviews = profile.get('reviews', 0)
        fotos = profile.get('fotos', 0)
        score = profile.get('score', 0)
        
        meta = profile.get('meta', {})
        scrape_debug = meta.get('scrape_debug', {})
        photos_method = scrape_debug.get('photos_method', 'N/A')
        photos_confidence = scrape_debug.get('photos_confidence', 0)
        
        print("\n" + "="*70)
        print("RESULTADOS - HOTEL VISPERAS")
        print("="*70)
        
        print(f"\nDatos Generales:")
        print(f"   Perfil existe: {'[OK]' if existe else '[NO]'}")
        print(f"   Score GBP: {score}/100")
        print(f"   Rating: {rating}/5.0")
        print(f"   Reviews: {reviews}")
        print(f"   Fotos: {fotos}")
        
        print(f"\nExtraccion de Fotos (PhotoAuditor):")
        print(f"   Metodo: {photos_method}")
        print(f"   Confianza: {photos_confidence}%")
        print(f"   Fotos detectadas: {fotos}")
        
        print("\n[5/5] Validaciones...")
        
        validations = {
            "Perfil encontrado": existe,
            "Rating valido": rating > 0,
            "Reviews presentes": reviews > 0,
            "Fotos extraidas": fotos > 0,
            "Confianza >= 70%": photos_confidence >= 70,
            "Metodo PhotoAuditor usado": photos_method != 'N/A',
        }
        
        print("\nResultado de validaciones:")
        passed_count = 0
        for check, passed in validations.items():
            status = "[PASS]" if passed else "[FAIL]"
            print(f"   {status} {check}")
            if passed:
                passed_count += 1
        
        print(f"\nTasa de exito: {passed_count}/{len(validations)}")
        
        save_results(profile, output_path)
        
        print("\n" + "="*70)
        if passed_count >= len(validations) - 1:
            print("[EXITO] TEST FUNCIONAL HOTEL VISPERAS: EXITOSO")
            print(f"Fotos: {fotos} | Confianza: {photos_confidence}% | Metodo: {photos_method}")
            print("="*70)
            return True
        else:
            print("[ADVERTENCIA] TEST CON FALLOS")
            print("="*70)
            return False
        
    except Exception as e:
        logger.error(f"ERROR critico: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_hotel_visperas()
    sys.exit(0 if success else 1)
