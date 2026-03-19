#!/usr/bin/env python3
"""
Test de Integracion v2.5.0
Valida que DecisionEngine + BenchmarkLoader + Plan Maestro estan alineados

Ejecutar: python scripts/test_v23_integration.py
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.decision_engine import DecisionEngine, Diagnostico
from modules.utils.benchmarks import BenchmarkLoader


def test_benchmark_loader():
    """Test 1: Validar que BenchmarkLoader carga datos correctos v2.5.0"""
    loader = BenchmarkLoader()
    data = loader.load()
    
    version = data.get("version", "unknown")
    assert version in ["v2.3", "v2.4.2", "v2.5.0"], (
        f"[FAIL] Version esperada v2.3, v2.4.2 o v2.5.0, obtenida {version}"
    )
    
    caribe = loader.get_regional_data("caribe")
    assert caribe['revpar_cop'] == 602800, f"[FAIL] RevPAR Caribe esperado 602800, obtenido {caribe['revpar_cop']}"
    
    eje = loader.get_regional_data("eje_cafetero")
    assert eje['revpar_cop'] == 197120, f"[FAIL] RevPAR Eje esperado 197120, obtenido {eje['revpar_cop']}"
    
    print(f"[OK] BenchmarkLoader: Version {version} cargada correctamente")
    print(f"   Caribe RevPAR: ${caribe['revpar_cop']:,}")
    print(f"   Eje Cafetero RevPAR: ${eje['revpar_cop']:,}")


def test_package_info():
    """Test 2: Validar precios y estructura de paquetes v2.5.0"""
    loader = BenchmarkLoader()
    packages = loader.get_packages()
    
    expected_packages = ["Starter GEO", "Pro AEO", "Pro AEO Plus", "Elite", "Elite PLUS"]
    for pkg in expected_packages:
        assert pkg in packages, f"[FAIL] Paquete {pkg} no encontrado"
    
    pro_plus = packages['Pro AEO Plus']
    assert pro_plus['precio_cop'] == 4800000, f"[FAIL] Precio Pro AEO Plus esperado 4800000, obtenido {pro_plus['precio_cop']}"
    assert pro_plus['roi_target'] == 5.2, f"[FAIL] ROI Pro AEO Plus esperado 5.2, obtenido {pro_plus['roi_target']}"
    
    elite_plus = packages['Elite PLUS']
    assert elite_plus['precio_cop'] == 9800000, f"[FAIL] Precio Elite PLUS esperado 9800000"
    
    print(f"[OK] Paquetes v2.5.0: {len(packages)} paquetes validados")
    print(f"   Pro AEO Plus: ${pro_plus['precio_cop']:,} COP (ROI: {pro_plus['roi_target']}X)")


def test_umbrales():
    """Test 3: Validar umbrales criticos de decision v2.5.0"""
    loader = BenchmarkLoader()
    umbrales = loader.get_thresholds()
    
    assert umbrales['impacto_catastrofico'] == 6000000, f"[FAIL] Umbral catastrofico esperado 6000000"
    assert umbrales['brecha_conversion_critica'] == 2500000, f"[FAIL] Umbral conversion esperado 2500000"
    assert umbrales['revpar_premium'] == 180000, f"[FAIL] Umbral RevPAR premium esperado 180000"
    assert umbrales['web_score_alto'] == 75, f"[FAIL] Umbral web score esperado 75"
    assert umbrales['gbp_score_bajo'] == 60, f"[FAIL] Umbral GBP score esperado 60"
    
    print(f"[OK] Umbrales v2.5.0: Todos los valores correctos")
    print(f"   Impacto catastrofico: >=${umbrales['impacto_catastrofico']:,}")
    print(f"   Brecha conversion: >=${umbrales['brecha_conversion_critica']:,}")


def test_orden_reglas():
    """Test 4: Validar que REGLA 1 (impacto catastrofico) tiene prioridad y sostiene Elite PLUS"""
    engine = DecisionEngine()
    
    # REGLA 1 requiere impacto_total >= $6M para Elite/Elite PLUS
    # Capa de Viabilidad Financiera: si costo > impacto_total, ajusta paquete
    # Elite PLUS cuesta $9.8M -> impacto_total debe ser >= $9.8M para sostenerse
    # 
    # Calculo con descuento motor 45%:
    # - sin_motor_reservas = 18M * 0.55 = 9.9M (brecha conversion ajustada)
    # - schema_ausente = 2M (brecha IA)
    # - impacto_total = 9.9M + 2M = 11.9M >= 9.8M (Elite PLUS se sostiene)
    diag = Diagnostico(
        sin_motor_reservas=18_000_000,   # Con 45% descuento = 9.9M
        schema_ausente=2_000_000,        # Brecha IA = 2M
        gbp_score=45,                    # MUY bajo (< 60) -> aplica descuento motor
        web_score=70,
        revpar=150_000,
        region="default",
        gbp_motor_existe=False,          # v2.5.0: Sin motor -> descuento 45%
    )
    
    resultado = engine.recomendar(diag)
    
    # DEBE ser Elite PLUS por REGLA 1 (impacto_total = 11.9M >= 9.8M)
    assert resultado['paquete'] == 'Elite PLUS', \
        f"[FAIL] Orden incorrecto - esperado Elite PLUS por impacto, obtenido {resultado['paquete']}"
    
    print(f"[OK] Orden de reglas: REGLA 1 (impacto catastrofico) priorizada correctamente")
    print(f"   Caso: GBP={diag.gbp_score} (bajo) + Impacto total = 11.9M >= 9.8M")
    print(f"   Resultado: {resultado['paquete']} (correcto)")


def test_hotel_visperas():
    """Test 5: Caso critico Hotel Visperas - v2.5.0 con descuentos motor"""
    engine = DecisionEngine()
    # v2.5.0: RevPAR no premium (150k < 180k) para NO activar REGLA 2
    # Sin motor -> 45% descuento en brecha conversion
    diag = Diagnostico(
        sin_motor_reservas=3_200_000,
        schema_ausente=2_100_000,
        gbp_score=85,
        web_score=65,
        revpar=150_000,                  # Ajustado: no premium (< 180k)
        region="eje_cafetero",
        gbp_activity_score=25,           # Inactivo
        gbp_motor_existe=False,          # No tiene motor -> 45% descuento
        gbp_motor_prominente=False
    )
    
    resultado = engine.recomendar(diag)
    
    # v2.5.0: Con descuento motor 45%, brecha conversion baja de 3.2M a 1.76M
    # La brecha IA (2.1M) se vuelve dominante -> Pro AEO Plus por web_score < 75
    # O bien Regla 9 activa por activity < 30 -> Starter GEO + GBP Activation
    valid_packages = ['Pro AEO Plus', 'Pro AEO', 'Starter GEO + GBP Activation']
    assert resultado['paquete'] in valid_packages, \
        f"[FAIL] Hotel Visperas esperado uno de {valid_packages}, obtenido {resultado['paquete']}"
    assert resultado['confianza'] >= 0.60, \
        f"[FAIL] Confianza esperada >=0.60, obtenida {resultado['confianza']}"
    assert 'brecha_dominante' in resultado, \
        f"[FAIL] brecha_dominante no encontrada en resultado"
    assert 'IAH' in resultado['firma_marca'], \
        f"[FAIL] Firma de marca no contiene 'IAH'"
    
    print(f"[OK] Hotel Visperas v2.5.0: {resultado['paquete']} (confianza: {resultado['confianza']*100:.0f}%)")
    print(f"   Brecha dominante: {resultado['brecha_dominante']}")
    print(f"   Motor ajuste: {resultado.get('motor_ajuste', 'N/A')}")
    print(f"   Activity penalty: {resultado.get('gbp_activity_penalty', 'N/A')}")
    print(f"   Razon: {resultado['razon'][:80]}...")


def test_brecha_dominante_incluida():
    """Test 6: Verificar que brecha_dominante esta en el resultado"""
    engine = DecisionEngine()
    diag = Diagnostico(1_000_000, 500_000, 70, 60, 150_000, "default")
    
    resultado = engine.recomendar(diag)
    
    assert 'brecha_dominante' in resultado, \
        "[FAIL] Campo 'brecha_dominante' no encontrado en resultado"
    assert resultado['brecha_dominante'] in ['conversion', 'ia_visibility', 'geo'], \
        f"[FAIL] brecha_dominante invalida: {resultado['brecha_dominante']}"
    
    print(f"[OK] Campo brecha_dominante: presente y valido ({resultado['brecha_dominante']})")


def main():
    """Ejecutar todos los tests de integracion."""
    print("=" * 70)
    print("TEST DE INTEGRACION v2.5.0 - Sistema de Reglas Puras")
    print("=" * 70)
    print()
    
    tests = [
        ("1. BenchmarkLoader", test_benchmark_loader),
        ("2. Paquetes v2.5.0", test_package_info),
        ("3. Umbrales", test_umbrales),
        ("4. Orden Reglas", test_orden_reglas),
        ("5. Hotel Visperas", test_hotel_visperas),
        ("6. Campo brecha_dominante", test_brecha_dominante_incluida),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_fn in tests:
        print(f"\n--- {name} ---")
        try:
            test_fn()
            passed += 1
        except AssertionError as e:
            print(str(e))
            failed += 1
        except Exception as e:
            print(f"[ERROR INESPERADO] {type(e).__name__}: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"RESULTADOS: {passed}/{len(tests)} tests pasaron")
    print("=" * 70)
    
    if failed == 0:
        print("TODOS LOS TESTS PASARON - SISTEMA v2.5.0 LISTO PARA PRODUCCION")
        return 0
    else:
        print(f"[WARNING] {failed} tests fallaron - revisar antes de continuar")
        return 1


if __name__ == "__main__":
    sys.exit(main())
