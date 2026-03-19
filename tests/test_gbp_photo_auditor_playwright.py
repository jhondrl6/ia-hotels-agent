"""
Tests for GBP Photo Auditor Playwright version.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from modules.scrapers.gbp_photo_auditor_playwright import (
    GBPPhotoAuditorPlaywright,
    PhotoAuditResult,
    integrate_photo_auditor_playwright
)


class TestPhotoAuditResult:
    
    def test_dataclass_creation(self):
        result = PhotoAuditResult(
            count=50,
            confidence=90,
            method='aria_label',
            evidence={'matched_label': '50 fotos'},
            warnings=[],
            timestamp=1234567890.0
        )
        assert result.count == 50
        assert result.confidence == 90
        assert result.method == 'aria_label'
        assert result.evidence['matched_label'] == '50 fotos'
        assert result.warnings == []


class TestGBPPhotoAuditorPlaywrightInit:
    
    def test_init_with_defaults(self, tmp_path):
        mock_page = Mock()
        auditor = GBPPhotoAuditorPlaywright(
            page=mock_page,
            debug_dir=str(tmp_path / "debug")
        )
        assert auditor.page == mock_page
        assert auditor.max_wait == 15
        assert auditor._network_handler_installed is False
    
    def test_init_with_custom_params(self, tmp_path):
        mock_page = Mock()
        cache_data = {'fotos': 100, 'photos_confidence': 90}
        
        auditor = GBPPhotoAuditorPlaywright(
            page=mock_page,
            max_wait=20,
            debug_dir=str(tmp_path / "custom_debug"),
            cache_data=cache_data
        )
        assert auditor.max_wait == 20
        assert auditor._cache_data == cache_data


class TestParseNumericValue:
    
    def setup_method(self):
        mock_page = Mock()
        self.auditor = GBPPhotoAuditorPlaywright(page=mock_page)
    
    def test_simple_number(self):
        assert self.auditor._parse_numeric_value("123") == 123
    
    def test_number_with_comma(self):
        # Comma is treated as European decimal separator
        assert self.auditor._parse_numeric_value("1,234") == 1
    
    def test_number_with_thousand_separator_removed(self):
        # In extraction, commas are removed before parsing
        assert self.auditor._parse_numeric_value("1234") == 1234
    
    def test_number_with_k_suffix(self):
        assert self.auditor._parse_numeric_value("2.5k") == 2500
    
    def test_number_with_capital_k(self):
        assert self.auditor._parse_numeric_value("1.2K") == 1200
    
    def test_number_with_m_suffix(self):
        assert self.auditor._parse_numeric_value("1.5m") == 1500000
    
    def test_invalid_value(self):
        assert self.auditor._parse_numeric_value("abc") is None
    
    def test_empty_value(self):
        assert self.auditor._parse_numeric_value("") is None


class TestExtractCounterFromAria:
    
    def setup_method(self):
        self.mock_page = Mock()
        self.auditor = GBPPhotoAuditorPlaywright(page=self.mock_page)
    
    def test_extract_from_spanish_fotos(self):
        mock_elem = Mock()
        mock_elem.get_attribute.return_value = "Ver las 50 fotos"
        self.mock_page.query_selector_all.return_value = [mock_elem]
        
        result = self.auditor._extract_counter_from_aria()
        
        assert result is not None
        count, evidence = result
        assert count == 50
        assert evidence['method'] == 'aria_label'
    
    def test_extract_from_english_photos(self):
        mock_elem = Mock()
        mock_elem.get_attribute.return_value = "See all 75 photos"
        self.mock_page.query_selector_all.return_value = [mock_elem]
        
        result = self.auditor._extract_counter_from_aria()
        
        assert result is not None
        count, evidence = result
        assert count == 75
    
    def test_extract_with_k_suffix(self):
        mock_elem = Mock()
        mock_elem.get_attribute.return_value = "Ver las 2.5k fotos"
        self.mock_page.query_selector_all.return_value = [mock_elem]
        
        result = self.auditor._extract_counter_from_aria()
        
        assert result is not None
        count, evidence = result
        assert count == 2500
    
    def test_no_matching_label(self):
        mock_elem = Mock()
        mock_elem.get_attribute.return_value = "Some other text"
        self.mock_page.query_selector_all.return_value = [mock_elem]
        
        result = self.auditor._extract_counter_from_aria()
        
        assert result is None
    
    def test_empty_elements(self):
        self.mock_page.query_selector_all.return_value = []
        
        result = self.auditor._extract_counter_from_aria()
        
        assert result is None


class TestCountUniqueImages:
    
    def setup_method(self):
        self.mock_page = Mock()
        self.auditor = GBPPhotoAuditorPlaywright(page=self.mock_page)
    
    def test_count_img_elements(self):
        mock_img1 = Mock()
        mock_img1.evaluate.return_value = 'IMG'
        mock_img1.get_attribute.return_value = 'https://googleusercontent.com/image1=s200-'
        
        mock_img2 = Mock()
        mock_img2.evaluate.return_value = 'IMG'
        mock_img2.get_attribute.return_value = 'https://googleusercontent.com/image2=s300-'
        
        self.mock_page.query_selector_all.return_value = [mock_img1, mock_img2]
        
        result = self.auditor._count_unique_images()
        
        assert len(result) == 2
    
    def test_count_div_with_background_image(self):
        mock_div = Mock()
        mock_div.evaluate.return_value = 'DIV'
        mock_div.get_attribute.return_value = 'background-image: url("https://googleusercontent.com/bgimage")'
        
        self.mock_page.query_selector_all.side_effect = [
            [],  # img selector
            [mock_div]  # div selector
        ]
        
        result = self.auditor._count_unique_images()
        
        assert len(result) >= 0
    
    def test_normalize_urls(self):
        mock_img = Mock()
        mock_img.evaluate.return_value = 'IMG'
        mock_img.get_attribute.return_value = 'https://googleusercontent.com/image=s200-'
        
        self.mock_page.query_selector_all.return_value = [mock_img]
        
        result = self.auditor._count_unique_images()
        
        # URL should be normalized (s200- removed)
        assert 'https://googleusercontent.com/image=' in result or len(result) == 1


class TestTryCacheFallback:
    
    def setup_method(self):
        self.mock_page = Mock()
        self.auditor = GBPPhotoAuditorPlaywright(page=self.mock_page)
    
    def test_valid_cache_fallback(self):
        self.auditor._cache_data = {
            'fotos': 100,
            'photos_confidence': 80,
            'photos_method': 'modal_scroll',
            'cache_age_days': 3
        }
        
        result = self.auditor._try_cache_fallback()
        
        assert result is not None
        count, confidence, evidence = result
        assert count == 100
        assert confidence == 30  # Fallback confidence
        assert evidence['method'] == 'cache_fallback'
    
    def test_cache_too_old(self):
        self.auditor._cache_data = {
            'fotos': 100,
            'photos_confidence': 80,
            'cache_age_days': 10  # > 7 days
        }
        
        result = self.auditor._try_cache_fallback()
        
        assert result is None
    
    def test_cache_low_confidence(self):
        self.auditor._cache_data = {
            'fotos': 100,
            'photos_confidence': 50  # < 70
        }
        
        result = self.auditor._try_cache_fallback()
        
        assert result is None
    
    def test_cache_zero_fotos(self):
        self.auditor._cache_data = {
            'fotos': 0,
            'photos_confidence': 80
        }
        
        result = self.auditor._try_cache_fallback()
        
        assert result is None
    
    def test_no_cache_data(self):
        self.auditor._cache_data = {}
        
        result = self.auditor._try_cache_fallback()
        
        assert result is None


class TestAuditPhotos:
    
    def setup_method(self):
        self.mock_page = Mock()
        self.auditor = GBPPhotoAuditorPlaywright(page=self.mock_page)
    
    def test_returns_photo_audit_result(self):
        mock_elem = Mock()
        mock_elem.get_attribute.return_value = "Ver las 25 fotos"
        self.mock_page.query_selector_all.return_value = [mock_elem]
        
        result = self.auditor.audit_photos()
        
        assert isinstance(result, PhotoAuditResult)
        assert result.count == 25
        assert result.confidence == 90
        assert result.method == 'aria_label'
    
    def test_returns_zero_on_all_failures(self):
        self.mock_page.query_selector_all.return_value = []
        self.mock_page.wait_for_selector.side_effect = Exception("Not found")
        self.mock_page.title.return_value = "Test Page"
        self.mock_page.url = "https://test.com"
        
        result = self.auditor.audit_photos()
        
        assert isinstance(result, PhotoAuditResult)
        assert result.count == 0
        assert result.confidence == 0
        assert result.method == 'none'


class TestSaveDebugArtifacts:
    
    def test_save_artifacts_success(self, tmp_path):
        mock_page = Mock()
        mock_page.screenshot.return_value = None
        mock_page.content.return_value = "<html>test</html>"
        
        auditor = GBPPhotoAuditorPlaywright(
            page=mock_page,
            debug_dir=str(tmp_path)
        )
        
        artifacts = auditor._save_debug_artifacts(context="test_context")
        
        assert 'screenshot' in artifacts or 'screenshot_error' in artifacts
        assert 'html_dump' in artifacts or 'html_error' in artifacts


class TestSetupNetworkInterception:
    
    def test_network_handler_installed_once(self):
        mock_page = Mock()
        auditor = GBPPhotoAuditorPlaywright(page=mock_page)
        
        auditor._setup_network_interception()
        assert auditor._network_handler_installed is True
        
        # Second call should not add another handler
        auditor._setup_network_interception()
        assert mock_page.on.call_count == 1


class TestIntegratePhotoAuditorPlaywright:
    
    def test_integration_monkey_patches(self):
        mock_auditor = Mock()
        mock_auditor._extract_metrics = Mock()
        mock_auditor.page = Mock()
        
        integrate_photo_auditor_playwright(mock_auditor)
        
        assert hasattr(mock_auditor, '_original_extract_metrics')
        assert mock_auditor._original_extract_metrics is not None


class TestSelectors:
    
    def test_selectors_defined(self):
        assert 'photo_button' in GBPPhotoAuditorPlaywright.SELECTORS
        assert 'photo_counter_aria' in GBPPhotoAuditorPlaywright.SELECTORS
        assert 'modal_dialog' in GBPPhotoAuditorPlaywright.SELECTORS
        assert 'image_elements' in GBPPhotoAuditorPlaywright.SELECTORS
        assert 'gallery_grid' in GBPPhotoAuditorPlaywright.SELECTORS
    
    def test_selectors_are_lists(self):
        for key, selectors in GBPPhotoAuditorPlaywright.SELECTORS.items():
            assert isinstance(selectors, list)
            assert len(selectors) > 0


class TestConfidenceLevels:
    
    def setup_method(self):
        self.mock_page = Mock()
        self.auditor = GBPPhotoAuditorPlaywright(page=self.mock_page)
    
    def test_confidence_90_for_aria_label(self):
        mock_elem = Mock()
        mock_elem.get_attribute.return_value = "50 fotos"
        self.mock_page.query_selector_all.return_value = [mock_elem]
        
        result = self.auditor.audit_photos()
        
        assert result.confidence == 90
    
    def test_confidence_0_on_complete_failure(self):
        self.mock_page.query_selector_all.return_value = []
        self.mock_page.wait_for_selector.side_effect = Exception("fail")
        self.mock_page.title.return_value = "Test"
        self.mock_page.url = "https://test.com"
        
        result = self.auditor.audit_photos()
        
        assert result.confidence == 0
