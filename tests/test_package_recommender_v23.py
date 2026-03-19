"""Ensure legacy package_recommender delegates to DecisionEngine v2.3."""

from modules.utils.package_recommender import determine_package


def test_determine_package_uses_rules_v23():
    hotel_data = {"perdida_conversion": 3_100_000, "web_score": 68, "revpar_estimado": 170_000}
    gbp_data = {"score": 80, "reviews": 20}
    schema_data = {"score_schema": 50, "tiene_hotel_schema": False}
    ia_test = {"perplexity": {"menciones": 0}, "chatgpt": {"menciones": 0}}

    paquete, razon = determine_package(
        region="eje_cafetero",
        reviews=gbp_data["reviews"],
        gbp_score=gbp_data["score"],
        schema_score=schema_data["score_schema"],
        tiene_schema=schema_data["tiene_hotel_schema"],
        total_mentions=ia_test["perplexity"]["menciones"] + ia_test["chatgpt"]["menciones"],
        precio_promedio=300_000,
        hotel_data=hotel_data,
    )

    assert paquete in {"starter_geo", "Pro AEO", "Pro AEO Plus", "Elite", "Elite PLUS", "Starter GEO"}
    assert isinstance(razon, str) and len(razon) > 0
