"""
Test de Integracion: GBPPhotoAuditor
Valida que la integracion con GBPAuditor funciona correctamente
"""
import pytest
from modules.scrapers.gbp_auditor import GBPAuditor
from modules.scrapers.gbp_photo_auditor import (
    GBPPhotoAuditor, 
    integrate_photo_auditor,
    PhotoAuditResult
)


class MockDriver:
    """Driver simulado para testing sin Selenium"""
    
    def __init__(self, photo_count=42, format_type='simple'):
        self.photo_count = photo_count
        self.format_type = format_type
        self.page_source = self._build_html()
    
    def _build_html(self):
        if self.format_type == 'simple':
            return f"<div>{self.photo_count} fotos</div>"
        elif self.format_type == 'abbreviated':
            k_value = self.photo_count / 1000
            return f"<div>{k_value}k fotos</div>"
        elif self.format_type == 'modal':
            return f"<div>1 de {self.photo_count} fotos</div>"
        return ""
    
    def find_elements(self, by, selector):
        """Simula find_elements retornando aria-labels con fotos"""
        class MockElement:
            def __init__(self, label):
                self._label = label
            
            def get_attribute(self, attr):
                if attr == 'aria-label':
                    return self._label
                return None
            
            @property
            def text(self):
                return self._label
        
        if 'foto' in selector.lower() or 'photo' in selector.lower():
            if self.format_type == 'abbreviated':
                k_value = self.photo_count / 1000
                # Formatear el valor flotante correctamente
                if k_value == int(k_value):
                    label = f"Ver {int(k_value)}k fotos"
                else:
                    label = f"Ver {k_value:.1f}k fotos"
                return [MockElement(label)]
            return [MockElement(f"Ver {self.photo_count} fotos")]
        return []
    
    def find_element(self, by, selector):
        raise Exception("Element not found (mock)")
    
    def get_log(self, log_type):
        return []
    
    def execute_script(self, script, *args):
        pass
    
    def quit(self):
        pass


def test_photo_auditor_extracts_simple_count():
    """Test: PhotoAuditor extrae contador simple 'X fotos'"""
    mock_driver = MockDriver(photo_count=120, format_type='simple')
    auditor = GBPPhotoAuditor(driver=mock_driver, max_wait=5)
    
    result = auditor._extract_counter_from_aria()
    
    assert result is not None
    count, evidence = result
    assert count == 120
    assert evidence['method'] == 'aria_label'


def test_photo_auditor_extracts_abbreviated_count():
    """Test: PhotoAuditor extrae contador abreviado '2.5k fotos'"""
    mock_driver = MockDriver(photo_count=2500, format_type='abbreviated')
    auditor = GBPPhotoAuditor(driver=mock_driver, max_wait=5)
    
    result = auditor._extract_counter_from_aria()
    
    assert result is not None
    count, evidence = result
    assert count == 2500
    assert evidence['method'] == 'aria_label'


def test_photo_auditor_returns_photoauditresult():
    """Test: audit_photos() retorna PhotoAuditResult completo"""
    mock_driver = MockDriver(photo_count=87, format_type='simple')
    auditor = GBPPhotoAuditor(driver=mock_driver, max_wait=5)
    
    result = auditor.audit_photos()
    
    assert isinstance(result, PhotoAuditResult)
    assert result.count == 87
    assert result.confidence >= 70
    assert result.method in ['aria_label', 'modal_scroll', 'dom_image_count', 'network_analysis']
    assert isinstance(result.evidence, dict)
    assert isinstance(result.warnings, list)


def test_integrate_photo_auditor_monkey_patches_correctly():
    """Test: integrate_photo_auditor() modifica _extract_metrics sin romper GBPAuditor"""
    auditor = GBPAuditor(headless=True)
    auditor.driver = MockDriver(photo_count=150, format_type='simple')
    
    original_method = auditor._extract_metrics
    
    integrate_photo_auditor(auditor)
    
    assert auditor._extract_metrics != original_method
    assert hasattr(auditor, '_original_extract_metrics')
    assert auditor._original_extract_metrics == original_method
    
    profile = auditor._base_profile()
    html = "<div>4.5 estrellas en 200 reseñas</div>"
    
    try:
        auditor._extract_metrics(html, profile)
        integration_success = True
    except Exception as e:
        integration_success = False
        pytest.fail(f"integrate_photo_auditor() rompio _extract_metrics: {e}")
    
    assert integration_success
    assert 'fotos' in profile
    assert 'meta' in profile
    assert 'data_confidence' in profile['meta']


def test_integrated_auditor_adds_metadata():
    """Test: El auditor integrado agrega metadata de PhotoAuditor"""
    auditor = GBPAuditor(headless=True)
    auditor.driver = MockDriver(photo_count=95, format_type='simple')
    
    integrate_photo_auditor(auditor)
    
    profile = auditor._base_profile()
    html = "<div>4.7 estrellas</div>"
    auditor._extract_metrics(html, profile)
    
    meta = profile.get('meta', {})
    scrape_debug = meta.get('scrape_debug', {})
    
    assert 'photos_method' in scrape_debug
    assert 'photos_confidence' in scrape_debug
    assert 'photos_evidence' in scrape_debug
    assert isinstance(scrape_debug['photos_warnings'], list)


def test_low_confidence_adds_issue_warning():
    """Test: Confianza baja (<50%) agrega warning a issues[]"""
    auditor = GBPAuditor(headless=True)
    auditor.driver = MockDriver(photo_count=0, format_type='simple')
    
    integrate_photo_auditor(auditor)
    
    profile = auditor._base_profile()
    html = ""
    auditor._extract_metrics(html, profile)
    
    issues = profile.get('issues', [])
    has_low_confidence_warning = any(
        'Contador de fotos poco confiable' in issue 
        for issue in issues
    )
    assert has_low_confidence_warning


def test_parse_numeric_value_handles_multipliers():
    """Test: _parse_numeric_value maneja multiplicadores k, M"""
    mock_driver = MockDriver(photo_count=0)
    auditor = GBPPhotoAuditor(driver=mock_driver, max_wait=5)
    
    assert auditor._parse_numeric_value("2.5k") == 2500
    assert auditor._parse_numeric_value("1.2K") == 1200
    assert auditor._parse_numeric_value("1.5m") == 1500000
    assert auditor._parse_numeric_value("750") == 750
    assert auditor._parse_numeric_value("invalid") is None


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
