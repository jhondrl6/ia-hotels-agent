# FASE-H1 - pares rojo/verde de los mutantes (R2.8, AC8)

Instrumento: reemplazo a nivel de BYTES (rb/wb) sobre el arbol de trabajo; restauracion verificada por sha256.
Seleccion: `tests/scrapers/test_fase_h1_gbp_score_denominador.py` + `tests/scrapers/test_fase_h1_booking_stub_retirado.py` (25 funciones).

## M1 — restore /100 en el reporte GBP
- archivo: modules\scrapers\gbp_auditor.py
- sha256 PRE : 9ed92e18e281c4f9fa39dac4afc93ad388904ed7da3a9faaad8aa55910e79f66
- sha256 POST: 9ed92e18e281c4f9fa39dac4afc93ad388904ed7da3a9faaad8aa55910e79f66
- arbol intacto: True
- ROJO con el mutante (2):
    FAILED tests/scrapers/test_fase_h1_gbp_score_denominador.py::TestDenominadorDeRubrica::test_reporte_publica_el_denominador_de_la_rubrica
    FAILED tests/scrapers/test_fase_h1_gbp_score_denominador.py::TestDenominadorDeRubrica::test_un_score_intermedio_no_se_renorma_a_cien
    resumen: 2 failed, 23 passed in 0.76s
- VERDE restaurado: 25 passed in 0.64s

## M2 — found=True vacio restaurado en el stub
- archivo: modules\scrapers\booking_scraper.py
- sha256 PRE : 6aebc5a43b9377bf78ebad04c3498b10bbc0903ef87682939f20b4e89b6e49e4
- sha256 POST: 6aebc5a43b9377bf78ebad04c3498b10bbc0903ef87682939f20b4e89b6e49e4
- arbol intacto: True
- ROJO con el mutante (4):
    FAILED tests/scrapers/test_fase_h1_booking_stub_retirado.py::TestStubRetirado::test_scrape_devuelve_el_estado_retirado
    FAILED tests/scrapers/test_fase_h1_booking_stub_retirado.py::TestStubRetirado::test_nunca_publica_found_true_vacio[Hotel Test-None]
    FAILED tests/scrapers/test_fase_h1_booking_stub_retirado.py::TestStubRetirado::test_nunca_publica_found_true_vacio[Hotel Gran Medellin-https://www.booking.com/hotel/co/gran-medellin.html]
    FAILED tests/scrapers/test_fase_h1_booking_stub_retirado.py::TestStubRetirado::test_nunca_publica_found_true_vacio[-None]
    resumen: 4 failed, 21 passed in 0.74s
- VERDE restaurado: 25 passed in 0.63s

## M3 — rubrica duplicada re-introducida en _scrape_maps_profile
- archivo: modules\scrapers\gbp_auditor.py
- sha256 PRE : 9ed92e18e281c4f9fa39dac4afc93ad388904ed7da3a9faaad8aa55910e79f66
- sha256 POST: 9ed92e18e281c4f9fa39dac4afc93ad388904ed7da3a9faaad8aa55910e79f66
- arbol intacto: True
- ROJO con el mutante (2):
    FAILED tests/scrapers/test_fase_h1_gbp_score_denominador.py::TestDenominadorDeRubrica::test_rubrica_define_un_solo_productor_en_el_modulo
    FAILED tests/scrapers/test_fase_h1_gbp_score_denominador.py::TestDenominadorDeRubrica::test_scrape_maps_profile_delega_en_el_productor_unico
    resumen: 2 failed, 23 passed in 0.75s
- VERDE restaurado: 25 passed in 0.81s
