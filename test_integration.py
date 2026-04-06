
import sys
sys.path.insert(0, '/mnt/c/Users/Jhond/Github/iah-cli')
from modules.asset_generation.conditional_generator import ConditionalGenerator

cg = ConditionalGenerator()
print(f"GENERATION_STRATEGIES keys: {len(cg.GENERATION_STRATEGIES)}")
print(f"  Has analytics_setup_guide: {'analytics_setup_guide' in cg.GENERATION_STRATEGIES}")
print(f"  Has indirect_traffic_optimization: {'indirect_traffic_optimization' in cg.GENERATION_STRATEGIES}")

validated_data = {
    "hotel_data": {
        "nombre": "Hotel Visperas",
        "url": "https://www.hotelvisperas.com/es",
        "ciudad": "Santa Rosa de Cabal",
    },
    "ga4_available": False,
}

result1 = cg.generate(
    asset_type="analytics_setup_guide",
    validated_data=validated_data,
    hotel_name="Hotel Visperas",
    hotel_id="hotel_test_001",
)
print(f"\nanalytics_setup_guide: status={result1['status']}, success={result1['success']}")

result2 = cg.generate(
    asset_type="indirect_traffic_optimization",
    validated_data=validated_data,
    hotel_name="Hotel Visperas",
    hotel_id="hotel_test_001",
)
print(f"indirect_traffic_optimization: status={result2['status']}, success={result2['success']}")
