"""FASE-H1 (`D24`) — AC8: el stub de Booking se declara retirado sin tocar el scraper real.

El stub de `modules/scrapers/booking_scraper.py` armaba `found=True` con `rating`,
`review_count` y `price_range` en `None` y `photos` vacío (`DA-C3`: un "no medí nada" que se
leía como "medí y no hay nada"). Hoy publica `found=False`, `data={}` y
`data_status=STUB_RETIRADO`. El scraper real del producto,
`modules/providers/autonomous_researcher.BookingScraper`, no se toca y su suite
(`tests/scrapers/test_booking_scraper.py`) sigue verde.
"""

import inspect
from pathlib import Path

import pytest

from modules.scrapers import booking_scraper
from modules.scrapers.booking_scraper import (
    ESTADO_STUB_RETIRADO,
    BookingScraper,
    create_booking_scraper,
)

RAIZ_REPO = Path(__file__).resolve().parents[2]
FUENTE_STUB = (RAIZ_REPO / 'modules' / 'scrapers' / 'booking_scraper.py').read_text(encoding='utf-8')
FUENTE_EXPORT = (RAIZ_REPO / 'modules' / 'scrapers' / '__init__.py').read_text(encoding='utf-8')


@pytest.fixture
def stub():
    return BookingScraper()


class TestStubRetirado:
    def test_scrape_devuelve_el_estado_retirado(self, stub):
        resultado = stub.scrape('Hotel Test')
        assert resultado['found'] is False
        assert resultado['data'] == {}
        assert resultado['data_status'] == ESTADO_STUB_RETIRADO == 'STUB_RETIRADO'

    @pytest.mark.parametrize('hotel,url', [
        ('Hotel Test', None),
        ('Hotel Gran Medellin', 'https://www.booking.com/hotel/co/gran-medellin.html'),
        ('', None),
    ])
    def test_nunca_publica_found_true_vacio(self, stub, hotel, url):
        assert stub.scrape(hotel, url)['found'] is False

    def test_el_molde_de_datos_fossilizado_quedo_retirado(self):
        """Sin scraping no se arma la plantilla con campos en None."""
        assert "'review_count': None" not in FUENTE_STUB
        assert "result['found'] = True" not in FUENTE_STUB

    def test_la_factory_legay_devuelve_el_stub_retirado(self):
        resultado = create_booking_scraper().scrape('Hotel Test')
        assert resultado['data_status'] == ESTADO_STUB_RETIRADO


class TestExportLegacyDeclarado:
    def test_el_export_de_modules_scrapers_es_el_stub(self):
        import modules.scrapers as scrapers_paquete
        assert scrapers_paquete.BookingScraper is BookingScraper
        assert 'BookingScraper' in scrapers_paquete.__all__

    def test_el_export_se_declara_legacy_en_su_sitio(self):
        assert 'LEGACY' in FUENTE_EXPORT
        assert ESTADO_STUB_RETIRADO in FUENTE_EXPORT, (
            'El export dejó de declarar que lo que entrega es el stub retirado'
        )


class TestScraperRealIntacto:
    def test_el_scraper_real_es_otra_clase(self, stub):
        from modules.providers.autonomous_researcher import BookingScraper as ScraperReal
        assert ScraperReal is not BookingScraper
        assert not issubclass(ScraperReal, BookingScraper)

    def test_la_retirada_no_se_filtra_al_scraper_real(self):
        from modules.providers.autonomous_researcher import BookingScraper as ScraperReal
        fuente_real = inspect.getsource(ScraperReal)
        assert ESTADO_STUB_RETIRADO not in fuente_real
        assert 'VERIFIED_HOTELS' in fuente_real, (
            'El scraper real perdió su API: la fase no debía tocarlo'
        )

    def test_evidencia_textual_de_la_retirada_en_el_stub(self):
        assert ESTADO_STUB_RETIRADO in inspect.getsource(booking_scraper.BookingScraper)
