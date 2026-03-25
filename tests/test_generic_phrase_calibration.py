"""
TDD Gate: Generic Phrase Calibration

Estos tests verifican que el AssetContentValidator NO marque como errores
las frases legítimas en guías de optimización SEO.

FASES ANTERIORES: FASE 1 y FASE 2 completadas.
FASE 3: Content Validation y Documentación.

PROBLEMA A RESOLVER:
- "verificar", "revisar", "personalizar" eran marcados como generic_phrase
- PERO son contenido legítimo para guías de optimización SEO
- optimization_guide.md tiene falsos positivos

COMPORTAMIENTO ESPERADO:
- "verificar", "revisar", "personalizar" NO son marcados como generic_phrase
- "no configurado", "por definir", "pendiente" SÍ son marcados (son placeholders reales)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from modules.asset_generation.asset_content_validator import (
    AssetContentValidator,
    ContentStatus
)


class TestSEOGuideLegitimatePhrases:
    """Verifica que frases legítimas de guías SEO no son marcadas como error."""
    
    def test_verificar_is_not_generic_phrase(self):
        """La palabra 'verificar' en guías SEO es legítima, no es generic_phrase."""
        validator = AssetContentValidator()
        
        # Content con "verificar" en contexto de guía SEO
        content = """
        # Guía de Optimización SEO
        
        ## Checklist de Verificación
        
        - [ ] Verificar meta tags
        - [ ] Verificar estructura de headers
        - [ ] Revisar contenido duplicado
        
        ## Recomendaciones
        
        Es importante verificar la velocidad del sitio.
        """
        
        result = validator.validate_markdown(content)
        
        # NO debe haber generic_phrase para "verificar"
        generic_issues = [i for i in result.issues if i.issue_type == "generic_phrase"]
        verificar_issues = [i for i in generic_issues if "verificar" in i.detected_value.lower()]
        
        assert len(verificar_issues) == 0, \
            f"'verificar' NO debe ser marcado como generic_phrase, pero se encontró: {verificar_issues}"
    
    def test_revisar_is_not_generic_phrase(self):
        """La palabra 'revisar' en guías SEO es legítima, no es generic_phrase."""
        validator = AssetContentValidator()
        
        content = """
        # Guía de Optimización
        
        ## Acciones Requeridas
        
        - [ ] Revisar backlinks rotos
        - [ ] Revisar imágenes sin alt text
        - [ ] Personalizar meta descriptions
        
        Para mejorar el SEO, debe revisar constantemente los resultados.
        """
        
        result = validator.validate_markdown(content)
        
        generic_issues = [i for i in result.issues if i.issue_type == "generic_phrase"]
        revisar_issues = [i for i in generic_issues if "revisar" in i.detected_value.lower()]
        
        assert len(revisar_issues) == 0, \
            f"'revisar' NO debe ser marcado como generic_phrase"
    
    def test_personalizar_is_not_generic_phrase(self):
        """La palabra 'personalizar' en guías SEO es legítima."""
        validator = AssetContentValidator()
        
        content = """
        # Guía de SEO On-Page
        
        ## Personalización Required
        
        - [ ] Personalizar título para cada página
        - [ ] Personalizar descripción meta
        - [ ] Configurar schema markup
        
        Siempre debe personalizar el contenido para su audiencia.
        """
        
        result = validator.validate_markdown(content)
        
        generic_issues = [i for i in result.issues if i.issue_type == "generic_phrase"]
        personalizar_issues = [i for i in generic_issues if "personalizar" in i.detected_value.lower()]
        
        assert len(personalizar_issues) == 0, \
            f"'personalizar' NO debe ser marcado como generic_phrase"
    
    def test_configurar_is_not_generic_phrase(self):
        """La palabra 'configurar' en guías SEO es legítima."""
        validator = AssetContentValidator()
        
        content = """
        # Configurar Google Search Console
        
        Pasos:
        1. Configurar cuenta
        2. Configurar propiedad
        3. Verificar ownership
        """
        
        result = validator.validate_markdown(content)
        
        generic_issues = [i for i in result.issues if i.issue_type == "generic_phrase"]
        configurar_issues = [i for i in generic_issues if "configurar" in i.detected_value.lower()]
        
        assert len(configurar_issues) == 0, \
            f"'configurar' NO debe ser marcado como generic_phrase"
    
    def test_optimizar_is_not_generic_phrase(self):
        """La palabra 'optimizar' en guías SEO es legítima."""
        validator = AssetContentValidator()
        
        content = """
        # Cómo Optimizar Su Sitio Web
        
        - [ ] Optimizar imágenes
        - [ ] Optimizar velocidad de carga
        - [ ] Optimizar contenido para keywords
        
        La optimización continua es clave para el SEO.
        """
        
        result = validator.validate_markdown(content)
        
        generic_issues = [i for i in result.issues if i.issue_type == "generic_phrase"]
        optimizar_issues = [i for i in generic_issues if "optimizar" in i.detected_value.lower()]
        
        assert len(optimizar_issues) == 0, \
            f"'optimizar' NO debe ser marcado como generic_phrase"


class TestActualGenericPhrasesStillDetected:
    """Verifica que frases realmente genéricas SÍ son detectadas."""
    
    def test_no_configurado_still_detected(self):
        """'no configurado' es un placeholder real y DEBE ser detectado."""
        validator = AssetContentValidator()
        
        content = "El campo teléfono muestra: no configurado"
        
        result = validator.validate_markdown(content)
        
        generic_issues = [i for i in result.issues if i.issue_type == "generic_phrase"]
        assert any("no configurado" in i.detected_value.lower() for i in generic_issues), \
            "'no configurado' SÍ debe ser detectado como generic_phrase"
    
    def test_por_definir_still_detected(self):
        """'por definir' es un placeholder real y DEBE ser detectado."""
        validator = AssetContentValidator()
        
        content = "El precio aparece como: por definir"
        
        result = validator.validate_markdown(content)
        
        generic_issues = [i for i in result.issues if i.issue_type == "generic_phrase"]
        assert any("por definir" in i.detected_value.lower() for i in generic_issues), \
            "'por definir' SÍ debe ser detectado"
    
    def test_pendiente_still_detected(self):
        """'pendiente' en contexto de datos faltantes SÍ debe ser detectado."""
        validator = AssetContentValidator()
        
        content = "La dirección aparece como: pendiente"
        
        result = validator.validate_markdown(content)
        
        generic_issues = [i for i in result.issues if i.issue_type == "generic_phrase"]
        assert any("pendiente" in i.detected_value.lower() for i in generic_issues), \
            "'pendiente' como placeholder SÍ debe ser detectado"


class TestRealWorldSEOGuide:
    """Test con contenido realista de guía de optimización SEO."""
    
    def test_optimization_guide_content(self):
        """Verifica que una guía de optimización SEO real no tiene falsos positivos."""
        validator = AssetContentValidator()
        
        # Content realista de guía SEO para hotel
        content = """
        # Guía de Optimización SEO para Hoteles
        
        ## Meta Tags
        
        Es importante personalizar las meta tags para cada página del hotel.
        
        - [ ] Revisar que el title-tag no exceda 60 caracteres
        - [ ] Personalizar la meta description para cada página
        - [ ] Verificar que los headers H1 sean únicos
        
        ## Velocidad del Sitio
        
        Para mejorar el SEO, debe optimizar las imágenes y verificar el tiempo de carga.
        
        - [ ] Optimizar imágenes con compresión
        - [ ] Configurar cache del navegador
        - [ ] Revisar redirecciones 301
        
        ## Schema Markup
        
        - [ ] Configurar Hotel schema
        - [ ] Verificar datos estructurados
        - [ ] Personalizar información de contacto
        
        ## Google Business Profile
        
        - [ ] Verificar información del perfil
        - [ ] Revisar fotos y horarios
        - [ ] Configurar posts regulares
        
        ## Recomendaciones Finales
        
        Recuerde verificar mensualmente los rankings y personalizar el contenido
        basándose en los datos de Search Console.
        """
        
        result = validator.validate_markdown(content)
        
        # Solo debe haber warnings por content length (si es corto)
        # NO debe haber generic_phrase para ninguna de las palabraslegítimas
        generic_phrase_issues = [i for i in result.issues if i.issue_type == "generic_phrase"]
        
        legitimate_words = ['verificar', 'revisar', 'personalizar', 'configurar', 'optimizar']
        false_positives = [
            i for i in generic_phrase_issues 
            if any(word in i.detected_value.lower() for word in legitimate_words)
        ]
        
        assert len(false_positives) == 0, \
            f"NO debe haber falsos positivos para SEO legítimas, pero se encontró: {false_positives}"


class TestValidatorClassStructure:
    """Verifica que la estructura del validador es correcta."""
    
    def test_seo_guide_legitimate_phrases_list_exists(self):
        """AssetContentValidator debe tener SEO_GUIDE_LEGITIMATE_PHRASES."""
        validator = AssetContentValidator()
        
        assert hasattr(AssetContentValidator, 'SEO_GUIDE_LEGITIMATE_PHRASES'), \
            "Debe existir SEO_GUIDE_LEGITIMATE_PHRASES"
        
        expected_phrases = ['verificar', 'revisar', 'personalizar', 'configurar', 'optimizar']
        for phrase in expected_phrases:
            assert phrase in AssetContentValidator.SEO_GUIDE_LEGITIMATE_PHRASES, \
                f"'{phrase}' debe estar en SEO_GUIDE_LEGITIMATE_PHRASES"
    
    def test_verificar_and_revisar_removed_from_generic_phrases(self):
        """'verificar' y 'revisar' NO deben estar en GENERIC_PHRASES."""
        assert 'verificar' not in AssetContentValidator.GENERIC_PHRASES, \
            "'verificar' NO debe estar en GENERIC_PHRASES"
        assert 'revisar' not in AssetContentValidator.GENERIC_PHRASES, \
            "'revisar' NO debe estar en GENERIC_PHRASES"
