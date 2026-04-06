"""Generador de guía de Texto Alternativo para el Acelerador IAO."""

from typing import Any, Dict


class AltTextGuideGenerator:
    """Genera guía de texto alternativo para imágenes."""

    def generate(self, hotel_data: Dict[str, Any], audit_result: Any = None) -> str:
        """
        Genera guía de texto alternativo para imágenes.
        
        Args:
            hotel_data: Datos del hotel
            audit_result: Resultado de auditoría (opcional)
        """
        nombre = hotel_data.get("nombre") or hotel_data.get("name", "Hotel")
        
        # Obtener datos de SEOElements si disponible
        images_count = 0
        images_without_alt = 0
        if audit_result and hasattr(audit_result, 'seo_elements') and audit_result.seo_elements:
            images_count = getattr(audit_result.seo_elements, 'images_analyzed', 0)
            images_without_alt = audit_result.seo_elements.images_without_alt or 0
        
        sections = [
            f"# Guía de Texto Alternativo (Alt Text) - {nombre}",
            "",
            "## ¿Qué es el Texto Alternativo?",
            "",
            "El atributo `alt` describe una imagen para:",
            "- Personas con discapacidad visual (lectores de pantalla)",
            "- Cuando la imagen no carga",
            "- Indexación por IA y SEO en Google Images",
            "",
            "## Estado Actual del Sitio",
            f"- Imágenes analizadas: {images_count if images_count > 0 else 'No disponible'}",
            f"- Imágenes sin alt: {images_without_alt if images_without_alt > 0 else 'No disponible'}",
            "",
            "## Reglas de Escritura",
            "",
            "### ✅ HAGA:",
            "1. Describa lo que muestra la imagen",
            "2. Incluya el nombre del hotel cuando sea relevante",
            "3. Sea específico: 'Habitación doble con vista al jardín' no 'habitación'",
            "4. Mantenga entre 50-125 caracteres",
            "",
            "### ❌ NO HAGA:",
            "1. No comience con 'Imagen de' o 'Foto de'",
            "2. No use palabras genéricas como 'imagen' o 'foto'",
            "3. No haga spam de palabras clave (keyword stuffing)",
            "",
            "## Ejemplos para Hoteles",
            "",
            "| Tipo de Imagen | ❌ MAL | ✅ BIEN |",
            "|---------------|--------|---------|",
            "| Habitación | 'habitacion' | 'Habitación doble con cama king y vista al jardín tropical' |",
            "| Restaurante | 'comida' | 'Desayuno tropical con frutas frescas y café colombiano' |",
            "| Fachada | 'hotel' | 'Fachada del Hotel Visperas con arquitectura colonial' |",
            "| Piscina | 'piscina' | 'Piscina infinity con vista al valle cafetero al atardecer' |",
            "| Spa | 'spa' | 'Área de masajes al aire libre rodeada de plantas nativas' |",
            "",
            "## Implementación Técnica",
            "",
            "```html",
            "<!-- Con alt descriptivo -->",
            '<img src="/images/habitacion-doble.jpg" alt="Habitación doble con cama king, balcón privado y vista al jardín tropical" />',
            "",
            "<!-- Imagen decorativa (puede ir vacía) -->",
            '<img src="/images/borde-decorativo.png" alt="" />',
            "```",
            "",
            "## Herramientas de Verificación",
            "",
            "1. **WAVE** (WebAIM): https://wave.webaim.org/",
            "2. **axe DevTools**: Extensión de Chrome",
            "3. **Google Search Console**: Informe de Accesibilidad",
            "",
            "## Checklist de Auditoría",
            "",
            "- [ ] Todas las imágenes de contenido tienen alt",
            "- [ ] Los alt no comienzan con 'Imagen de' o 'Foto de'",
            "- [ ] Los alt describen específicamente el contenido",
            "- [ ] Las imágenes decorativas tienen alt=''",
            "- [ ] El alt incluye nombre del hotel cuando es relevante",
        ]
        
        return "\n".join(sections)


__all__ = ["AltTextGuideGenerator"]
