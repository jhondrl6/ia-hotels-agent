"""Test rápido de v2.4.2 - Modelo logarítmico y motor GBP."""
import math
from modules.decision_engine import DecisionEngine, Diagnostico

def test_modelo_logaritmico():
    """Verificar calibración $1.6M máximo."""
    print("=== Test Modelo Logarítmico ===")
    for activity in [0, 30, 60, 90, 100]:
        if activity >= 100:
            pen = 0
        else:
            pen = math.log(101 - activity) / math.log(101) * 1_600_000
        print(f"Activity {activity:3d} → Penalización ${int(pen):,}")

def test_motor_gbp():
    """Verificar descuentos motor."""
    print("\n=== Test Motor GBP ===")
    engine = DecisionEngine()
    
    # Caso Hotel Vísperas: motor existe pero no prominente
    diag = Diagnostico(
        sin_motor_reservas=3_200_000,
        schema_ausente=2_100_000,
        gbp_score=85,
        web_score=65,
        revpar=197_120,  # Eje Cafetero v2.5.0
        region="eje_cafetero",
        gbp_activity_score=0,          # Inactivo
        gbp_motor_existe=True,          # Motor existe
        gbp_motor_prominente=False      # Pero no prominente
    )
    
    result = engine.recomendar(diag)
    print(f"Paquete: {result['paquete']}")
    print(f"Brecha dominante: {result['brecha_dominante']}")
    print(f"Confianza: {result['confianza']*100:.0f}%")
    print(f"Versión: {result['version']}")

def test_regresion_existente():
    """Verificar que tests existentes pasan."""
    print("\n=== Test Regresión ===")
    engine = DecisionEngine()
    
    # Caso original Hotel Vísperas (sin nuevos campos - defaults)
    diag = Diagnostico(3_200_000, 2_100_000, 85, 65, 171_600, "eje_cafetero")
    result = engine.recomendar(diag)
    
    expected = "Pro AEO Plus"
    actual = result["paquete"]
    status = "✓ PASS" if actual == expected else f"✗ FAIL (esperado: {expected})"
    print(f"Hotel Vísperas default: {actual} {status}")
    
    # Impacto catastrófico
    diag2 = Diagnostico(6_000_000, 3_000_000, 40, 70, 150_000, "default")
    result2 = engine.recomendar(diag2)
    expected2 = "Elite PLUS"
    status2 = "✓ PASS" if result2["paquete"] == expected2 else f"✗ FAIL"
    print(f"Impacto catastrófico: {result2['paquete']} {status2}")

if __name__ == "__main__":
    test_modelo_logaritmico()
    test_motor_gbp()
    test_regresion_existente()
    print("\n=== Tests completados ===")
