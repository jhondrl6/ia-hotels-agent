"""Generador de guía SSL/HTTPS para el Acelerador IAO."""

from typing import Any, Dict


class SSLGuideGenerator:
    """Genera guía de implementación SSL/HTTPS."""

    def generate(self, hotel_data: Dict[str, Any], audit_result: Any = None) -> str:
        """
        Genera guía de implementación SSL/HTTPS.
        
        Args:
            hotel_data: Datos del hotel
            audit_result: Resultado de auditoría (opcional)
        """
        nombre = hotel_data.get("nombre") or hotel_data.get("name", "Hotel")
        url = hotel_data.get("url", "") or ""
        
        # Verificar SSL actual
        has_ssl = url.startswith("https") if url else False
        
        sections = [
            f"# Guía de Implementación SSL/HTTPS - {nombre}",
            "",
            f"## Estado Actual",
            f"{'✅ Su sitio YA tiene SSL instalado' if has_ssl else '❌ Su sitio NO tiene SSL'}",
            "",
            "## ¿Por qué SSL es importante?",
            "",
            "1. **Seguridad**: Cifra la comunicación entre el usuario y su sitio",
            "2. **SEO**: Google penaliza sitios sin HTTPS en los resultados de búsqueda",
            "3. **IAO**: Los crawlers de IA prefieren sitios seguros para indexar contenido",
            "",
            "## Pasos de Implementación",
            "",
            "### Paso 1: Verificar Certificado",
        ]
        
        if url:
            clean_url = url.replace("https://", "").replace("http://", "")
            sections.append(f"Visite: https://www.ssllabs.com/ssltest/analyze.html?d={clean_url}")
        else:
            sections.append("Visite: https://www.ssllabs.com/ssltest/analyze.html?d=su-dominio.com")
        
        sections.extend([
            "",
            "### Paso 2: Forzar HTTPS",
            "Agregue en su .htaccess o configuración del servidor:",
            "",
            "```apache",
            "RewriteEngine On",
            "RewriteCond %{HTTPS} off",
            "RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]",
            "```",
            "",
            "### Paso 3: Actualizar Enlaces Internos",
            "Asegúrese que todos los enlaces internos usen https://",
            "",
            "### Paso 4: Verificar en Google Search Console",
            "1. Vaya a Google Search Console",
            "2. Seleccione su propiedad",
            "3. Vaya a Configuración → Configuración de dominio",
            "4. Verifique que el dominio esté verificado con https://",
            "",
            "## Checkpoint Final",
            "Su sitio debe mostrar candado verde en el navegador.",
        ])
        
        if has_ssl:
            sections.extend([
                "",
                "## Recomendaciones Adicionales",
                "- Considere implementar HSTS (HTTP Strict Transport Security) para mayor seguridad",
                "- Renueve su certificado SSL antes de la fecha de expiración",
            ])
        
        return "\n".join(sections)


__all__ = ["SSLGuideGenerator"]
