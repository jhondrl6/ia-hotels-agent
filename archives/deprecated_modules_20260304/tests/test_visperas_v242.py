"""
Test diagnóstico v2.4.2 - Simula escenario Hotel Vísperas con datos reales.
Genera output completo para validación de Regla 9 y modelo logarítmico.
"""
import math
import json
from modules.decision_engine import DecisionEngine, Diagnostico

def run_hotel_visperas_diagnostic():
    """Ejecuta diagnóstico completo simulando Hotel Vísperas."""
    print("=" * 60)
    print("DIAGNÓSTICO HOTEL VÍSPERAS - v2.4.2")
    print("=" * 60)
    
    engine = DecisionEngine()
    
    # Datos reales Hotel Vísperas según auditoría
    diag = Diagnostico(
        sin_motor_reservas=3_200_000,   # Brecha conversión original
        schema_ausente=2_100_000,        # Brecha IA
        gbp_score=85,                    # GBP optimizado
        web_score=65,                    # Web mejorable
        revpar=197_120,                  # Eje Cafetero v2.5.0
        region="eje_cafetero",
        menciones_ia=0,
        gbp_activity_score=12,           # Inactivo (0 posts, 0 fotos, 50% reviews)
        gbp_motor_existe=True,           # Motor lobbypms detectado
        gbp_motor_prominente=False       # Requiere 3-4 clics
    )
    
    print("\n📊 DATOS DE ENTRADA:")
    print(f"   sin_motor_reservas: ${diag.sin_motor_reservas:,}")
    print(f"   schema_ausente: ${diag.schema_ausente:,}")
    print(f"   gbp_score: {diag.gbp_score}/100")
    print(f"   gbp_activity_score: {diag.gbp_activity_score}/100")
    print(f"   gbp_motor_existe: {diag.gbp_motor_existe}")
    print(f"   gbp_motor_prominente: {diag.gbp_motor_prominente}")
    print(f"   web_score: {diag.web_score}/100")
    print(f"   revpar: ${diag.revpar:,}")
    print(f"   region: {diag.region}")
    
    # Calcular penalización manual para verificar
    if diag.gbp_activity_score >= 100:
        penalizacion = 0
    else:
        penalizacion = math.log(101 - diag.gbp_activity_score) / math.log(101) * 1_600_000
    
    print("\n📐 CÁLCULOS INTERMEDIOS:")
    print(f"   Penalización inactividad (logarítmica): ${int(penalizacion):,}")
    
    # Ajuste motor
    brecha_conv = diag.sin_motor_reservas
    if not diag.gbp_motor_existe:
        brecha_conv = int(brecha_conv * (1 - 0.45))
        print(f"   Brecha conversión (motor inexistente -45%): ${brecha_conv:,}")
    elif not diag.gbp_motor_prominente:
        brecha_conv = int(brecha_conv * (1 - 0.18))
        print(f"   Brecha conversión (motor oculto -18%): ${brecha_conv:,}")
    else:
        print(f"   Brecha conversión (motor prominente): ${brecha_conv:,}")
    
    # Ejecutar motor de decisión
    result = engine.recomendar(diag)
    
    print("\n🎯 RESULTADO DECISIONENGINE v2.4.2:")
    print(f"   Paquete recomendado: {result['paquete']}")
    print(f"   Brecha dominante: {result['brecha_dominante']}")
    print(f"   Confianza: {result['confianza']*100:.0f}%")
    print(f"   Razón: {result['razon']}")
    print(f"   Versión: {result['version']}")
    
    print("\n📦 INPUTS USADOS:")
    for k, v in result['inputs'].items():
        print(f"   {k}: {v:,}" if isinstance(v, int) else f"   {k}: {v}")
    
    # Validar Regla 9
    print("\n✅ VALIDACIÓN REGLA 9:")
    if "Activation" in result['paquete']:
        print("   ✓ Regla 9 aplicada correctamente (Starter GEO + GBP Activation)")
    elif result['brecha_dominante'] != 'geo':
        print(f"   ⚠ Regla 9 no aplica: brecha dominante es '{result['brecha_dominante']}', no 'geo'")
    else:
        print(f"   ⚠ Regla 9 no aplicada. GBP Score: {diag.gbp_score}, Activity: {diag.gbp_activity_score}")
    
    # Guardar resultado JSON
    output_path = "outputs/visperas_v242_diagnostico.json"
    try:
        import os
        os.makedirs("outputs", exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                "hotel": "Hotel Vísperas",
                "version": result['version'],
                "diagnostico": {
                    "gbp_score": diag.gbp_score,
                    "gbp_activity_score": diag.gbp_activity_score,
                    "gbp_motor_existe": diag.gbp_motor_existe,
                    "gbp_motor_prominente": diag.gbp_motor_prominente,
                    "sin_motor_reservas": diag.sin_motor_reservas,
                    "schema_ausente": diag.schema_ausente,
                    "web_score": diag.web_score,
                    "revpar": diag.revpar,
                    "region": diag.region,
                },
                "calculos": {
                    "penalizacion_inactividad": int(penalizacion),
                    "brecha_conversion_ajustada": brecha_conv,
                },
                "resultado": result,
            }, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Diagnóstico guardado en: {output_path}")
    except Exception as e:
        print(f"\n⚠ Error guardando JSON: {e}")
    
    print("\n" + "=" * 60)
    print("FIN DIAGNÓSTICO")
    print("=" * 60)
    
    return result

if __name__ == "__main__":
    run_hotel_visperas_diagnostic()
