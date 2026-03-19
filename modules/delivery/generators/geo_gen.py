"""Generadores para activar el pilar GEO (GBP + directorios + reseñas)."""

from __future__ import annotations

from io import StringIO
from typing import Any, Dict, List


class GeoContentGenerator:
    """Construye playbooks accionables para Starter GEO.
    
    NOTA IMPORTANTE (2026-01):
    Google deshabilitó la función Q&A para perfiles de hoteles.
    Ver informe técnico completo: docs/Q&A_DEPRECATION_REPORT.md
    Las instrucciones Q&A han sido actualizadas para pivotear a FAQs en web.
    """

    DIRECTORY_CATALOG: List[Dict[str, str]] = [
        {"platform": "Google Business Profile", "url": "https://www.google.com/business/", "action": "Optimizar ficha, subir 3 posts, actualizar atributos"},
        {"platform": "Google Maps Q&A", "url": "https://maps.google.com", "action": "BLOQUEADO: Publicar FAQs en web /preguntas-frecuentes (Q&A deshabilitado Ene 2026)"},
        {"platform": "Bing Places", "url": "https://www.bingplaces.com", "action": "Clonar información GBP"},
        {"platform": "Tripadvisor", "url": "https://www.tripadvisor.com/Owners", "action": "Actualizar servicios, subir imágenes 2025"},
        {"platform": "Expedia Partner Central", "url": "https://www.expediapartnercentral.com", "action": "Sincronizar tarifas directas"},
        {"platform": "Despegar Hoteliers", "url": "https://www.despegar.com.co/hoteliers", "action": "Alinear CTA y WhatsApp"},
        {"platform": "Hoteles.com", "url": "https://www.hoteles.com/", "action": "Actualizar amenities clave"},
        {"platform": "Booking.com", "url": "https://admin.booking.com", "action": "Reforzar narrativa mascotas y termales"},
        {"platform": "Airbnb", "url": "https://www.airbnb.com/host/homes", "action": "Duplicar copy para escapadas pareja"},
        {"platform": "Apple Business Register", "url": "https://register.apple.com/business", "action": "Asegurar consistencia NAP"},
    ]

    def generate(self, hotel_data: Dict[str, Any]) -> Dict[str, str]:
        nombre = hotel_data.get("nombre") or hotel_data.get("name", "Hotel")
        ubicacion = hotel_data.get("ubicacion") or hotel_data.get("city", "Colombia")
        servicios = hotel_data.get("servicios") or hotel_data.get("amenities", [])
        tono = hotel_data.get("tono", "escapada de naturaleza")

        posts_md = self._render_posts_md(nombre, ubicacion, servicios, tono)
        directories_csv = self._render_directories_csv()
        review_playbook = self._render_review_playbook(nombre, ubicacion, servicios)

        return {
            "geo_playbook": posts_md,
            "directories_csv": directories_csv,
            "review_playbook": review_playbook,
        }

    # ------------------------------------------------------------------
    def _render_posts_md(self, nombre: str, ubicacion: str, servicios: List[str], tono: str) -> str:
        amenity_a = servicios[0] if servicios else "spa termal"
        amenity_b = servicios[1] if len(servicios) > 1 else "experiencia gastronómica local"

        posts = [
            {
                "titulo": "Post 1 · Escapada Termal Semana 1",
                "copy": f"Descubre {nombre} en {ubicacion}. Incluye acceso ilimitado a {amenity_a} y late checkout. CTA: Reserva directo y recibe bebida de bienvenida.",
            },
            {
                "titulo": "Post 2 · Viaja con Mascotas",
                "copy": f"Somos pet friendly: espacios verdes, kit de cortesía y rutas guiadas. CTA: Agenda por WhatsApp y asegura tu cupo con tarifa flexible.",
            },
            {
                "titulo": "Post 3 · Experiencia Gastronómica",
                "copy": f"Chef local + ingredientes del Eje Cafetero. Menú degustación con vista a las montañas. CTA: Reserva la mesa al confirmar tu habitación.",
            },
        ]

        qnas = [
            ("¿Aceptan mascotas en todas las habitaciones?", "Sí, tenemos habitaciones diseñadas para viajes con mascota, con áreas verdes asignadas."),
            ("¿El desayuno está incluido?", "Incluimos desayuno campesino con ingredientes locales servido entre 7 a.m. y 10 a.m."),
            ("¿Cuál es el horario de check-in/check-out?", "Check-in 3 p.m. · Check-out 12 m. Ofrecemos late checkout sin costo sujeto a ocupación."),
            ("¿Tienen termales o spa cercano?", "Estamos a 15 minutos de Termales Santa Rosa; coordinamos transporte y reservas."),
            ("¿Cuentan con parqueadero?", "Sí, parqueadero privado cubierto sin costo."),
        ]

        checklist = [
            "[ ] Subir 3 posts con CTA directos",
            "[x] ~~Publicar 5 Q&A oficiales~~ → BLOQUEADO (Google deshabilitó Q&A para hoteles Ene 2026). Publicar FAQs en web /preguntas-frecuentes",
            "[ ] Cargar 15 fotos verticales actualizadas",
            "[ ] Activar mensajes y respuesta automática en GBP",
        ]

        md_lines = [
            f"# Playbook GEO - {nombre}",
            f"Ubicación: {ubicacion} · Enfoque: {tono}\n",
            "## Posts recomendados",
        ]
        for post in posts:
            md_lines.append(f"- **{post['titulo']}**: {post['copy']}")

        md_lines.append("\n## Preguntas y Respuestas semilla")
        for question, answer in qnas:
            md_lines.append(f"- **{question}** → {answer}")

        md_lines.append("\n## Checklist GBP (Semana 1)")
        md_lines.extend(checklist)

        return "\n".join(md_lines)

    def _render_directories_csv(self) -> str:
        buffer = StringIO()
        fieldnames = ["platform", "url", "action", "status"]
        buffer.write(",".join(fieldnames) + "\n")
        for entry in self.DIRECTORY_CATALOG:
            row = [
                entry["platform"],
                entry["url"],
                entry["action"],
                "pending",
            ]
            buffer.write(",".join(f'"{value}"' if "," in value else value for value in row) + "\n")
        return buffer.getvalue().strip()

    def _render_review_playbook(self, nombre: str, ubicacion: str, servicios: List[str]) -> str:
        destacado = servicios[0] if servicios else "tu experiencia favorita"
        steps = [
            "Recolectar WhatsApp de cada huésped al check-in.",
            "Enviar mensaje automatizado 2 horas después del checkout con enlace directo a reseña.",
            "Responder cada reseña en menos de 24 horas resaltando el motivo del viaje.",
            "Publicar resumen semanal de reseñas positivas en redes/GBP.",
        ]

        scripts = [
            f"Hola {{nombre}}, gracias por elegirnos para tu estancia en {ubicacion}. ¿Podrías contarnos tu experiencia aquí? Tu reseña nos ayuda a seguir siendo la recomendación #1 en IA.",
            f"Fue un gusto recibirte. Si disfrutaste del {destacado}, cuéntalo aquí: {{link reseña}}",
        ]

        lines = [
            f"# Plan de Reseñas · {nombre}",
            "## Objetivo",
            "Conseguir 20 reseñas verificadas en 30 días con puntaje ≥4.6.",
            "\n## Pasos operativos",
        ]
        lines.extend([f"- {step}" for step in steps])

        lines.append("\n## Script sugerido")
        lines.extend([f"- {script}" for script in scripts])

        lines.append("\n## Métricas a monitorear")
        lines.append("- % huéspedes que reciben el link")
        lines.append("- Reseñas nuevas por semana")
        lines.append("- Puntaje promedio GBP")

        return "\n".join(lines)

    def generate_gbp_audit_checklist(self, hotel_data: Dict[str, Any]) -> str:
        """Genera checklist de auditoría de integridad de datos GBP.
        
        Basado en sección 6.1 del informe Q&A Deprecation (Enero 2026):
        'Si un servicio no está marcado en el backend, no existe para la IA.'
        
        Args:
            hotel_data: Datos del hotel con servicios/amenities a verificar.
            
        Returns:
            Markdown con checklist de auditoría de atributos GBP.
        """
        nombre = hotel_data.get("nombre") or hotel_data.get("name", "Hotel")
        servicios = hotel_data.get("servicios") or hotel_data.get("amenities", [])
        
        # Atributos críticos para hoteles (Google Hotel Attributes API)
        critical_attributes = [
            # Amenities de infraestructura
            ("Amenities", "Wi-Fi gratuito", "wifi" in str(servicios).lower()),
            ("Amenities", "Piscina", "piscina" in str(servicios).lower() or "pool" in str(servicios).lower()),
            ("Amenities", "Parking privado", "parking" in str(servicios).lower() or "parqueadero" in str(servicios).lower()),
            ("Amenities", "Spa / Zona húmeda", "spa" in str(servicios).lower() or "termal" in str(servicios).lower()),
            ("Amenities", "Gimnasio", "gym" in str(servicios).lower() or "gimnasio" in str(servicios).lower()),
            ("Amenities", "Restaurante on-site", "restaurante" in str(servicios).lower()),
            ("Amenities", "Carga EV", "eléctrico" in str(servicios).lower() or "ev" in str(servicios).lower()),
            # Servicios especiales
            ("Servicios", "Pet-friendly", "mascota" in str(servicios).lower() or "pet" in str(servicios).lower()),
            ("Servicios", "Accesibilidad reducida", "accesib" in str(servicios).lower()),
            ("Servicios", "Desayuno incluido", "desayuno" in str(servicios).lower()),
            ("Servicios", "Room service 24h", "room service" in str(servicios).lower()),
            # Políticas (deben estar explícitas)
            ("Políticas", "Check-in / Check-out", True),  # Siempre requerido
            ("Políticas", "Política mascotas", "mascota" in str(servicios).lower()),
            ("Políticas", "Política cancelación", True),  # Siempre requerido
            ("Políticas", "Edad mínima huéspedes", False),  # Verificar manualmente
        ]
        
        lines = [
            f"# Checklist de Integridad de Datos GBP - {nombre}",
            "",
            "> **Prioridad máxima (2026)**: Los atributos del perfil alimentan directamente",
            "> las respuestas de IA en Google Maps. Si un servicio no está marcado, no existe.",
            "",
            "## Referencia",
            "Basado en: [Q&A Deprecation Report - Sección 6.1](../docs/Q&A_DEPRECATION_REPORT.md)",
            "",
            "## Auditoría de Atributos Críticos",
            "",
            "| Categoría | Atributo | Auto-detectado | Verificar en GBP |",
            "| :--- | :--- | :---: | :---: |",
        ]
        
        for category, attr_name, detected in critical_attributes:
            status = "✅" if detected else "⚠️"
            check = "[ ]"  # Siempre pendiente de verificación manual
            lines.append(f"| {category} | {attr_name} | {status} | {check} |")
        
        lines.extend([
            "",
            "## Acciones Recomendadas",
            "",
            "1. **Revisar Panel GBP** → Detalles del Hotel → Marcar TODOS los atributos aplicables",
            "2. **Sincronizar con web**: Cada atributo debe tener página/sección correspondiente con Schema.org",
            "3. **Auditoría mensual**: Los atributos desactualizados generan respuestas incorrectas de IA",
            "",
            "## Atributos Adicionales a Considerar",
            "",
            "- [ ] Horarios de amenidades (piscina, spa, restaurante)",
            "- [ ] Idiomas del personal",
            "- [ ] Métodos de pago aceptados",
            "- [ ] Certificaciones (sostenibilidad, calidad)",
            "",
            "---",
            "*Generado por IAH CLI · Data Integrity Audit v1.0*",
        ])
        
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # GEO Content Formats (v2.6.4 - Aligned with content_standards_geo)
    # ------------------------------------------------------------------

    def generate_geo_strategy_guide(self, hotel_data: Dict[str, Any]) -> str:
        """Genera la guía estratégica GEO/AEO para inclusión en delivery."""
        nombre = hotel_data.get("nombre") or hotel_data.get("name", "Hotel")
        ubicacion = hotel_data.get("ubicacion") or hotel_data.get("city", "Colombia")
        
        return f'''# Guía Estratégica: GEO & AEO (Optimización para Motores Generativos)

> **"Rank in search. Get cited by AI. Sound like a human wrote it."**

## 1. SEO vs. GEO: El Cambio de Paradigma

| Variable | SEO (Tradicional) | GEO (IA/LLM) |
| :--- | :--- | :--- |
| **Objetivo** | Ranking Página 1 | Ser citado ("Según {nombre}...") |
| **Estilo** | Exhaustivo, largo | Conciso, definitivo, denso |
| **Métrica** | Clics y permanencia | Cita en AI Overview |

## 2. Formatos de Contenido Ganadores

### A. Página de Definición (500-1K palabras)
- Definición directa en primer párrafo (máx 40 palabras)
- Tabla comparativa obligatoria

### B. Data & Research (1-2K palabras)
- Tablas de datos locales ({ubicacion})
- Distancias exactas en Km y minutos

### C. Expert Take (800-1.5K palabras)
- Primera persona ("Yo recomiendo...")
- Historias reales de huéspedes

### D. Structured FAQ (1-2K palabras)
- Respuestas binarias "Sí/No" + Why
- Sin rodeos

## 3. Condiciones de Victoria

| Indicador | Meta |
| :--- | :--- |
| Cita en AI Overview | 1 en 30 días |
| Mención ChatGPT/Perplexity | 2 en 60 días |
| Link fuente en Perplexity | 1 en 45 días |

---
*Generado por IAH CLI v2.6.4 · content_standards_geo v1.0*
'''

    def render_structured_faq(self, hotel_data: Dict[str, Any], faqs: List[tuple]) -> str:
        """Genera FAQs estructuradas con respuestas binarias (Formato GEO D)."""
        nombre = hotel_data.get("nombre") or hotel_data.get("name", "Hotel")
        
        lines = [
            f"# Todo lo que necesitas saber antes de reservar en {nombre}",
            "",
            "## Logística de Llegada y Salida",
            "| Servicio | Horario | Observación |",
            "| :--- | :--- | :--- |",
            "| **Check-in** | 3:00 PM | Si llegas antes, guardamos tu equipaje gratis. |",
            "| **Check-out** | 12:00 PM | Late check-out sujeto a disponibilidad. |",
            "",
            "## Preguntas Frecuentes",
            ""
        ]
        
        for question, answer in faqs:
            lines.append(f"### {question}")
            lines.append(answer)
            lines.append("")
        
        return "\n".join(lines)

    def render_expert_take(self, hotel_data: Dict[str, Any], topic: str, opinion: str) -> str:
        """Genera contenido Expert Take en primera persona (Formato GEO C)."""
        nombre = hotel_data.get("nombre") or hotel_data.get("name", "Hotel")
        ubicacion = hotel_data.get("ubicacion") or hotel_data.get("city", "Colombia")
        gerente = hotel_data.get("gerente", "el equipo local")
        
        return f'''# {topic}

> *"{opinion}"* — {gerente}, {nombre}

## La Perspectiva de un Local

Como hoteleros en {ubicacion}, hemos visto de todo...

## Datos que Respaldan Nuestra Opinión

| Dato | Valor |
| :--- | :--- |
| Años de experiencia | 10+ |
| Huéspedes atendidos | 5,000+ |

---
*Generado por IAH CLI v2.6.4 · Formato Expert Take*
'''

    def render_data_research(self, hotel_data: Dict[str, Any], data_points: Dict[str, str]) -> str:
        """Genera contenido Data/Research con tablas de datos (Formato GEO B)."""
        nombre = hotel_data.get("nombre") or hotel_data.get("name", "Hotel")
        ubicacion = hotel_data.get("ubicacion") or hotel_data.get("city", "Colombia")
        
        lines = [
            f"# Guía de Datos: {ubicacion}",
            "",
            "## Información Clave para tu Viaje",
            "",
            "| Dato | Valor |",
            "| :--- | :--- |",
        ]
        
        for key, value in data_points.items():
            lines.append(f"| **{key}** | {value} |")
        
        lines.extend([
            "",
            f"## Distancias desde {nombre}",
            "",
            "| Destino | Distancia | Tiempo |",
            "| :--- | :--- | :--- |",
            "| Aeropuerto más cercano | 45 km | 1 hora |",
            "| Terminal de buses | 5 km | 10 min |",
            "| Centro histórico | 2 km | 5 min |",
            "",
            "---",
            "*Generado por IAH CLI v2.6.4 · Formato Data/Research*"
        ])
        
        return "\n".join(lines)
