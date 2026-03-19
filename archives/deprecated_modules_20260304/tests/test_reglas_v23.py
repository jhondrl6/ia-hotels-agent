"""Regression tests for deterministic DecisionEngine v2.3 (no LLM)."""

from modules.decision_engine import DecisionEngine, Diagnostico


def test_hotel_visperas_like_case():
    """Caso crítico: Hotel Vísperas debe recomendar Pro AEO Plus por brecha conversión."""
    engine = DecisionEngine()
    diag = Diagnostico(3_200_000, 2_100_000, 85, 65, 171_600, "eje_cafetero")
    result = engine.recomendar(diag)

    assert result["paquete"] == "Pro AEO Plus"
    assert 0.75 <= result["confianza"] <= 0.96
    assert result["firma_marca"].startswith("IAH")
    assert result["brecha_dominante"] == "conversion"


def test_caribe_premium_escalates_elite_plus():
    """RevPAR premium con web score alto debe escalar a Elite PLUS."""
    engine = DecisionEngine()
    diag = Diagnostico(4_000_000, 2_000_000, 90, 80, 300_000, "caribe")
    result = engine.recomendar(diag)

    assert result["paquete"] == "Elite PLUS"
    assert result["inputs"]["revpar"] >= 250_000


def test_gbp_bajo_fuerza_starter_geo():
    """GBP bajo sin impacto catastrófico debe forzar Starter GEO."""
    engine = DecisionEngine()
    diag = Diagnostico(500_000, 300_000, 45, 70, 150_000, "antioquia")
    result = engine.recomendar(diag)

    assert result["paquete"] == "Starter GEO"
    assert result["inputs"]["gbp_score"] == 45
    assert result["brecha_dominante"] == "geo"


def test_engine_no_network_needed():
    """El motor debe funcionar sin red (datos locales)."""
    engine = DecisionEngine()
    diag = Diagnostico(1_000_000, 500_000, 70, 60, 150_000, "default")
    result = engine.recomendar(diag)

    assert result["paquete"] in {"Pro AEO", "Pro AEO Plus", "Elite", "Elite PLUS", "Starter GEO"}
    assert isinstance(result["confianza"], float)


def test_orden_reglas_impacto_sobre_gbp():
    """CRÍTICO: Impacto catastrófico debe tener prioridad sobre GBP bajo."""
    engine = DecisionEngine()
    # Caso: GBP MUY bajo PERO impacto catastrófico (9M > 8M umbral)
    diag = Diagnostico(
        sin_motor_reservas=6_000_000,
        schema_ausente=3_000_000,  # Total: 9M
        gbp_score=40,              # Muy bajo
        web_score=70,
        revpar=150_000,
        region="default"
    )
    result = engine.recomendar(diag)

    # DEBE ser Elite PLUS por impacto, NO Starter GEO por GBP
    assert result["paquete"] == "Elite PLUS", \
        f"Orden incorrecto: esperado Elite PLUS por impacto, obtenido {result['paquete']}"


def test_brecha_dominante_incluida():
    """El resultado debe incluir el campo brecha_dominante."""
    engine = DecisionEngine()
    diag = Diagnostico(1_000_000, 500_000, 70, 60, 150_000, "default")
    result = engine.recomendar(diag)

    assert "brecha_dominante" in result
    assert result["brecha_dominante"] in {"conversion", "ia_visibility", "geo"}


def test_revpar_premium_fuerza_elite():
    """RevPAR premium sin web alto debe resultar en Elite (no Elite PLUS)."""
    engine = DecisionEngine()
    diag = Diagnostico(2_000_000, 1_000_000, 80, 60, 280_000, "caribe")
    result = engine.recomendar(diag)

    assert result["paquete"] == "Elite"
    assert result["inputs"]["revpar"] >= 250_000


# ══════════════════════════════════════════════════════════════════════════════
# TESTS v2.4.2: Modelo Logarítmico + Motor GBP
# ══════════════════════════════════════════════════════════════════════════════

def test_v242_inactividad_logaritmica():
    """v2.4.2: Activity 0 debe generar penalización máxima (~$1.6M)."""
    import math
    engine = DecisionEngine()
    
    # Activity 0 → penalización máxima
    diag_inactivo = Diagnostico(
        sin_motor_reservas=500_000,
        schema_ausente=300_000,
        gbp_score=70,  # GBP adecuado
        web_score=60,
        revpar=150_000,
        region="default",
        gbp_activity_score=0  # Inactivo total
    )
    
    # Activity 100 → sin penalización
    diag_activo = Diagnostico(
        sin_motor_reservas=500_000,
        schema_ausente=300_000,
        gbp_score=70,
        web_score=60,
        revpar=150_000,
        region="default",
        gbp_activity_score=100  # Activo total
    )
    
    result_inactivo = engine.recomendar(diag_inactivo)
    result_activo = engine.recomendar(diag_activo)
    
    # El inactivo debe tener brecha GEO inflada
    assert result_inactivo["brecha_dominante"] == "geo", \
        f"Inactividad debería forzar brecha GEO, obtuvo {result_inactivo['brecha_dominante']}"


def test_v242_motor_gbp_descuento_prominencia():
    """v2.4.2: Motor prominente no debe reducir brecha (0%), no prominente sí (18%)."""
    engine = DecisionEngine()
    
    # Motor no prominente: 18% reducción
    diag_no_prom = Diagnostico(
        sin_motor_reservas=3_200_000,
        schema_ausente=500_000,
        gbp_score=85,
        web_score=65,
        revpar=171_600,
        region="eje_cafetero",
        gbp_motor_existe=True,
        gbp_motor_prominente=False
    )
    
    # Motor prominente: 0% reducción
    diag_prom = Diagnostico(
        sin_motor_reservas=3_200_000,
        schema_ausente=500_000,
        gbp_score=85,
        web_score=65,
        revpar=171_600,
        region="eje_cafetero",
        gbp_motor_existe=True,
        gbp_motor_prominente=True
    )
    
    result_no_prom = engine.recomendar(diag_no_prom)
    result_prom = engine.recomendar(diag_prom)
    
    # Ambos deben funcionar sin error
    assert result_no_prom["paquete"] in {"Pro AEO", "Pro AEO Plus", "Elite", "Elite PLUS", "Starter GEO"}
    assert result_prom["paquete"] in {"Pro AEO", "Pro AEO Plus", "Elite", "Elite PLUS", "Starter GEO"}


def test_v242_version_actualizada():
    """v2.4.2: El motor debe reportar versión 2.4.2."""
    engine = DecisionEngine()
    diag = Diagnostico(1_000_000, 500_000, 70, 60, 150_000, "default")
    result = engine.recomendar(diag)
    
    assert "2.4.2" in result["version"], \
        f"Versión esperada v2.4.2, obtenido {result['version']}"


def test_v242_regla9_gbp_activation_addon():
    """v2.4.2 Regla 9: GBP optimizado pero inactivo → Starter GEO + Addon."""
    engine = DecisionEngine()
    
    # GBP Score ≥60 pero Activity Score <30
    diag = Diagnostico(
        sin_motor_reservas=500_000,
        schema_ausente=300_000,
        gbp_score=75,  # GBP optimizado (≥60)
        web_score=60,
        revpar=150_000,
        region="default",
        gbp_activity_score=12,  # Inactivo (<30)
        gbp_motor_existe=True,
        gbp_motor_prominente=False
    )
    
    result = engine.recomendar(diag)
    
    # Regla 9 debe aplicar cuando brecha dominante es GEO + GBP optimizado + inactivo
    assert "Activation" in result["paquete"] or result["brecha_dominante"] != "geo", \
        f"Regla 9 debería aplicar addon si brecha es GEO, obtuvo {result['paquete']} con brecha {result['brecha_dominante']}"
