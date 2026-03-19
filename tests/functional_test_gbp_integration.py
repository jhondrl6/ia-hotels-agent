"""Test Funcional: Auditoria GBP con PhotoAuditor integrado"""
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.scrapers.gbp_auditor import GBPAuditor
from modules.scrapers.gbp_photo_auditor import integrate_photo_auditor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def test_functional_integration():
    """Test funcional de integracion PhotoAuditor"""
    print("\n" + "="*70)
    print("TEST FUNCIONAL: Integracion PhotoAuditor")
    print("="*70)
    
    try:
        print("\n[1/3] Inicializando GBPAuditor...")
        auditor = GBPAuditor(headless=True)
        print("      [OK] Auditor inicializado")
        
        print("\n[2/3] Integrando PhotoAuditor...")
        integrate_photo_auditor(auditor)
        print("      [OK] PhotoAuditor integrado")
        
        print("\n[3/3] Validando integridad...")
        assert hasattr(auditor, '_extract_metrics')
        assert hasattr(auditor, '_original_extract_metrics')
        print("      [OK] Modulos validados")
        
        print("\n" + "="*70)
        print("[EXITO] TEST FUNCIONAL COMPLETADO")
        print("="*70)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_functional_integration()
    sys.exit(0 if success else 1)
