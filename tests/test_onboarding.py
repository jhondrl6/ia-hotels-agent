"""
Tests para el módulo de onboarding.

Cubre:
- Validadores (casos válidos e inválidos)
- Carga de archivos YAML/JSON
- Merge de datos
"""

import json
import tempfile
from pathlib import Path

import pytest
import yaml

from modules.onboarding import (
    OnboardingForm,
    validate_habitaciones,
    validate_reservas_mes,
    validate_valor_reserva,
    validate_canal_directo,
    load_onboarding_data,
    merge_with_hotel_data,
)
from modules.onboarding.data_loader import (
    create_onboarding_template,
    generate_slug,
)


class TestValidateHabitaciones:
    """Tests para validate_habitaciones."""

    @pytest.mark.parametrize("input_value,expected_value", [
        (22, 22),
        ("50", 50),
        (1, 1),
        (500, 500),
    ])
    def test_valid_values(self, input_value, expected_value):
        success, value, error = validate_habitaciones(input_value)
        assert success is True
        assert value == expected_value
        assert error is None

    @pytest.mark.parametrize("input_value,error_substring", [
        (0, "al menos 1"),
        (501, "500"),
        (-5, None),
    ])
    def test_invalid_values(self, input_value, error_substring):
        success, value, error = validate_habitaciones(input_value)
        assert success is False
        assert value is None
        if error_substring:
            assert error_substring in error

    @pytest.mark.parametrize("input_value,error_substring", [
        ("abc", "no es un número válido"),
        ("", None),
    ])
    def test_invalid_strings(self, input_value, error_substring):
        success, value, error = validate_habitaciones(input_value)
        assert success is False
        assert value is None
        if error_substring:
            assert error_substring in error

    def test_invalid_none(self):
        success, value, error = validate_habitaciones(None)
        assert success is False


class TestValidateReservasMes:
    """Tests para validate_reservas_mes."""

    @pytest.mark.parametrize("input_value,expected_value", [
        (180, 180),
        ("1,500", 1500),
        (1, 1),
        (10000, 10000),
    ])
    def test_valid_values(self, input_value, expected_value):
        success, value, error = validate_reservas_mes(input_value)
        assert success is True
        assert value == expected_value
        assert error is None

    @pytest.mark.parametrize("input_value,error_substring", [
        (10001, "10,000"),
        (0, None),
    ])
    def test_invalid_values(self, input_value, error_substring):
        success, value, error = validate_reservas_mes(input_value)
        assert success is False
        assert value is None
        if error_substring:
            assert error_substring in error


class TestValidateValorReserva:
    """Tests para validate_valor_reserva."""

    @pytest.mark.parametrize("input_value,expected_value", [
        (350000, 350000),
        ("350000", 350000),
        ("350.000", 350000),
        ("350,000", 350000),
        ("$350000", 350000),
        (50000, 50000),
        (5000000, 5000000),
    ])
    def test_valid_values(self, input_value, expected_value):
        success, value, error = validate_valor_reserva(input_value)
        assert success is True
        assert value == expected_value
        assert error is None

    @pytest.mark.parametrize("input_value,error_substring", [
        (49999, "$50,000"),
        (5000001, "$5,000,000"),
    ])
    def test_invalid_values(self, input_value, error_substring):
        success, value, error = validate_valor_reserva(input_value)
        assert success is False
        assert value is None
        assert error_substring in error


class TestValidateCanalDirecto:
    """Tests para validate_canal_directo."""

    @pytest.mark.parametrize("input_value,expected_value", [
        (45, 45.0),
        (45.5, 45.5),
        ("45%", 45.0),
        ("45.5", 45.5),
        ("45,5", 45.5),
        (0, 0.0),
        (100, 100.0),
    ])
    def test_valid_values(self, input_value, expected_value):
        success, value, error = validate_canal_directo(input_value)
        assert success is True
        assert value == expected_value
        assert error is None

    @pytest.mark.parametrize("input_value,error_substring", [
        (101, "100%"),
        (-5, "negativo"),
    ])
    def test_invalid_values(self, input_value, error_substring):
        success, value, error = validate_canal_directo(input_value)
        assert success is False
        assert value is None
        assert error_substring in error


class TestLoadOnboardingData:
    """Tests para load_onboarding_data."""
    
    def test_load_yaml(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({
                "hotel": {"nombre": "Test Hotel"},
                "datos_operativos": {"habitaciones": 22}
            }, f)
            f.flush()
            
            data = load_onboarding_data(Path(f.name))
            
            assert data["hotel"]["nombre"] == "Test Hotel"
            assert data["datos_operativos"]["habitaciones"] == 22
    
    def test_load_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({
                "hotel": {"nombre": "Test Hotel"},
                "datos_operativos": {"habitaciones": 22}
            }, f)
            f.flush()
            
            data = load_onboarding_data(Path(f.name))
            
            assert data["hotel"]["nombre"] == "Test Hotel"
    
    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_onboarding_data(Path("nonexistent_file.yaml"))
    
    def test_unsupported_format(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("some content")
            f.flush()
            
            with pytest.raises(ValueError) as exc_info:
                load_onboarding_data(Path(f.name))
            
            assert "Formato no soportado" in str(exc_info.value)
    
    def test_invalid_yaml_content(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            f.flush()
            
            with pytest.raises(ValueError):
                load_onboarding_data(Path(f.name))
    
    def test_invalid_json_content(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{invalid json}")
            f.flush()
            
            with pytest.raises(ValueError):
                load_onboarding_data(Path(f.name))


class TestMergeWithHotelData:
    """Tests para merge_with_hotel_data."""
    
    def test_basic_merge(self):
        onboarding = {
            "datos_operativos": {
                "habitaciones": 22,
                "reservas_mes": 180,
            },
            "metadatos": {
                "campos_confirmados": ["habitaciones", "reservas_mes"],
                "fecha_captura": "2026-02-23T18:00:00Z"
            }
        }
        
        hotel_data = {
            "nombre": "Hotel Test",
            "habitaciones": 20,  # Will be overwritten
            "ubicacion": "Cartagena"
        }
        
        result = merge_with_hotel_data(onboarding, hotel_data)
        
        assert result["habitaciones"] == 22
        assert result["habitaciones_fuente"] == "onboarding_confirmado"
        assert result["habitaciones_confianza"] == 1.0
        assert result["nombre"] == "Hotel Test"
        assert result["ubicacion"] == "Cartagena"
        assert "habitaciones" in result["campos_confirmados"]
    
    def test_empty_onboarding(self):
        hotel_data = {"nombre": "Hotel Test", "habitaciones": 20}
        
        result = merge_with_hotel_data({}, hotel_data)
        
        assert result["habitaciones"] == 20
        assert "habitaciones_fuente" not in result
    
    def test_merge_preserves_scraper_data(self):
        onboarding = {
            "datos_operativos": {
                "habitaciones": 22,
            },
            "metadatos": {"campos_confirmados": ["habitaciones"]}
        }
        
        hotel_data = {
            "habitaciones": 20,
            "reservas_mes": 150,  # Not in onboarding, should be preserved
            "valor_reserva_cop": 300000
        }
        
        result = merge_with_hotel_data(onboarding, hotel_data)
        
        assert result["habitaciones"] == 22
        assert result["reservas_mes"] == 150
        assert result["valor_reserva_cop"] == 300000
    
    def test_merge_hotel_info(self):
        onboarding = {
            "hotel": {
                "nombre": "Onboarding Hotel Name",
                "ubicacion": "Santa Marta"
            },
            "datos_operativos": {},
            "metadatos": {}
        }
        
        hotel_data = {
            "nombre": "Existing Name",  # Won't be overwritten (setdefault)
        }
        
        result = merge_with_hotel_data(onboarding, hotel_data)
        
        assert result["nombre"] == "Existing Name"
        assert result["ubicacion"] == "Santa Marta"


class TestCreateOnboardingTemplate:
    """Tests para create_onboarding_template."""
    
    def test_template_structure(self):
        template = create_onboarding_template()
        
        assert "hotel" in template
        assert "datos_operativos" in template
        assert "metadatos" in template
        
        assert template["hotel"]["nombre"] is None
        assert template["datos_operativos"]["habitaciones"] is None
        assert template["metadatos"]["fuente"] == "onboarding_interactivo"


class TestGenerateSlug:
    """Tests para generate_slug."""
    
    def test_simple_name(self):
        assert generate_slug("Hotel Paradise") == "hotel-paradise"
    
    def test_special_characters(self):
        assert generate_slug("Hotel's Paradise!") == "hotels-paradise"
    
    def test_multiple_spaces(self):
        assert generate_slug("Hotel    Paradise    Resort") == "hotel-paradise-resort"
    
    def test_accents_removed(self):
        # Accents are stripped (non-ASCII removed)
        result = generate_slug("Hotel Páramo")
        assert result == "hotel-pramo"
    
    def test_empty_string(self):
        assert generate_slug("") == "hotel"


class TestOnboardingForm:
    """Tests para OnboardingForm class."""
    
    def test_init_default(self):
        form = OnboardingForm(verbose=False)
        
        assert form.is_completed is False
        assert isinstance(form.to_dict(), dict)
    
    def test_init_with_hotel_name(self):
        form = OnboardingForm(hotel_nombre="Test Hotel", verbose=False)
        
        data = form.to_dict()
        assert data["hotel"]["nombre"] == "Test Hotel"
    
    def test_to_dict_returns_copy(self):
        form = OnboardingForm(verbose=False)
        
        data1 = form.to_dict()
        data2 = form.to_dict()
        
        assert data1 is not data2
    
    def test_datos_operativos_property(self):
        form = OnboardingForm(verbose=False)
        
        datos = form.datos_operativos
        assert "habitaciones" in datos
        assert datos["habitaciones"] is None
    
    def test_save_yaml(self):
        form = OnboardingForm(hotel_nombre="Test Hotel", verbose=False)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.yaml"
            
            result = form.save_yaml(path)
            
            assert result is True
            assert path.exists()
            
            loaded = yaml.safe_load(path.read_text())
            assert loaded["hotel"]["nombre"] == "Test Hotel"
    
    def test_save_json(self):
        form = OnboardingForm(hotel_nombre="Test Hotel", verbose=False)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            
            result = form.save_json(path)
            
            assert result is True
            assert path.exists()
            
            loaded = json.loads(path.read_text())
            assert loaded["hotel"]["nombre"] == "Test Hotel"
