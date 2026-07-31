import sys
from pathlib import Path

project_root = Path(r"C:\Users\Jhond\Github\iah-cli")
sys.path.insert(0, str(project_root))

try:
    from main import _normalize_url, _observation_to_onboarding_format, _load_latest_onboarding_data
    print("OK: Todas las funciones importadas")
    
    # Test _normalize_url
    cases = [
        ("https://zione.co/", "zione.co"),
        ("https://www.zione.co/", "zione.co"),
        ("http://zione.co", "zione.co"),
        ("https://www.hotel.com/es/", "hotel.com"),
        ("https://hotel.co?lang=es", "hotel.co"),
        ("https://ZIONE.CO/", "zione.co"),
        ("https://www.sub.domain.co/", "sub.domain.co"),
        ("http://simple-hotel.co", "simple-hotel.co"),
        ("zione.co", "zione.co"),
        ("https://www.hotel.com.co/path?q=1#frag", "hotel.com.co"),
    ]
    
    for url, expected in cases:
        result = _normalize_url(url)
        status = "PASS" if result == expected else "FAIL"
        print(f"  {status} _normalize_url({url!r}) = {result!r} (expected {expected!r})")
    
    # Test _observation_to_onboarding_format
    obs = {
        "hotel_name": "Zi One Luxury",
        "website": "https://zione.co/",
        "region": "eje_cafetero",
        "rooms": 34,
        "monthly_reservations": 800,
        "avg_reservation_cop": 290000,
        "direct_channel_percentage": 40.0,
        "collected_at": "2026-07-22",
        "confidence": 0.95,
        "epistemic_status": "verified",
    }
    result = _observation_to_onboarding_format(obs)
    print(f"\n_observation_to_onboarding_format OK: habitaciones={result['datos_operativos']['habitaciones']}")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
