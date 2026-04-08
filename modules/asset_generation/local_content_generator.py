"""Micro-Content Local Generator (FASE-E).

Genera 3-5 paginas de contenido local orientadas a keywords long-tail
para hoteles boutique del Eje Cafetero colombiano.

Cada pagina:
- Keyword objetivo de busqueda local
- Contenido 800-1200 palabras en espanol neutro
- Schema Article JSON-LD
- Link a reservas directas (WhatsApp)
- Mencion natural del hotel (no vendedora)

Uso:
    from modules.asset_generation.local_content_generator import LocalContentGenerator

    gen = LocalContentGenerator()
    result = gen.generate_content_set(hotel_data, hotel_type="boutique",
                                       location_context={"region": "Eje Cafetero"})
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import re
from datetime import datetime
from pathlib import Path


_TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates" / "local_content"


@dataclass
class LocalContentPage:
    """Una pagina individual de contenido local."""
    keyword_target: str
    title: str
    slug: str
    content_md: str
    schema_article: dict
    internal_links: List[str]
    meta_description: str
    word_count: int


@dataclass
class LocalContentSet:
    """Conjunto completo de paginas para un hotel."""
    hotel_name: str
    location: str
    pages: List[LocalContentPage]
    total_word_count: int
    location_context: Optional[str] = None


class LocalContentGenerator:
    """Genera paginas de contenido local para hoteles boutique."""

    KEYWORD_TEMPLATES = {
        "termales": [
            "termales {location} precios",
            "hotel cerca termales {location}",
            "que llevar a termales {location}",
            "mejores termales {region}",
            "termales {location} desde {nearby_city}",
        ],
        "parque_natural": [
            "parque nacional {location} como llegar",
            "senderismo {location} recomendaciones",
            "ecoturismo {region} mejores planes",
            "fauna y flora {region}",
            "donde alojarse cerca parque {location}",
        ],
        "pueblo_patrimonio": [
            "que hacer en {location}",
            "hotel boutique {location} Colombia",
            "fin de semana en {location}",
            "gastronomia {region}",
            "visitar {location} desde {nearby_city}",
        ],
        "cafe": [
            "tour del cafe {location}",
            "finca cafetera {region} visita",
            "mejor epoca para visitar {location}",
            "hospedaje entre cafetales {region}",
            "experiencias cafeteras {location}",
        ],
        "boutique": [
            "hotel boutique {location} Colombia",
            "donde hospedarse en {location}",
            "mejor hotel boutique {region}",
            "hotel encantador {location} precio",
            "alojamiento exclusivo {location}",
        ],
        "general": [
            "que hacer en {location}",
            "como llegar a {location}",
            "restaurantes cerca de {location}",
            "sitios turisticos {region}",
            "plan turismo {location} fin de semana",
        ],
    }

    KEYWORD_PRIORITY = {
        "precios": 5,
        "hotel": 4,
        "hospedarse": 4,
        "mejor": 3,
        "que hacer": 3,
        "como llegar": 2,
        "restaurantes": 2,
        "sitios turisticos": 2,
        "fin de semana": 2,
        "tour": 3,
        "experiencias": 2,
        "gastronomia": 2,
        "senderismo": 2,
        "ecoturismo": 2,
        "fauna": 1,
    }

    CONTENT_RULES = {
        "word_count_min": 800,
        "word_count_max": 1200,
        "internal_links_min": 2,
        "heading_count_min": 4,
        "paragraph_max_sentences": 4,
    }

    AI_GENERIC_PHRASES = [
        "en el corazon de",
        "descubre la magia",
        "un mundo de",
        "vibrante destino",
        "te dejamos",
        "no te pierdas",
        "te invitamos",
        "sin duda",
        "no dudes en",
        "te esperamos",
        "en pleno",
        "te va a encantar",
    ]

    def __init__(self, templates_dir: Optional[Path] = None):
        self._current_year = datetime.now().year
        self._templates_dir = templates_dir or _TEMPLATES_DIR

    def load_template(self, name: str) -> str:
        """Carga un template markdown desde templates/local_content/."""
        path = self._templates_dir / name
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def generate_content_set(
        self,
        hotel_data: Dict[str, Any],
        hotel_type: str = "boutique",
        location_context: Optional[Dict[str, Any]] = None,
    ) -> LocalContentSet:
        keywords = self._select_keywords(hotel_data, hotel_type, location_context)
        pages: List[LocalContentPage] = []
        for kw in keywords[:5]:
            page = self._generate_page(kw, hotel_data, location_context or {})
            pages.append(page)
        return LocalContentSet(
            hotel_name=hotel_data.get("name", ""),
            location=hotel_data.get("city", ""),
            pages=pages,
            total_word_count=sum(p.word_count for p in pages),
            location_context=(location_context or {}).get("region"),
        )

    def _select_keywords(
        self, hotel_data: Dict[str, Any], hotel_type: str,
        location_context: Optional[Dict[str, Any]],
    ) -> List[str]:
        location = hotel_data.get("city", "")
        region = (location_context or {}).get("region", hotel_data.get("state", ""))
        nearby_city = (location_context or {}).get("nearby_city", "Pereira")
        templates_to_use = self._resolve_templates(hotel_type, hotel_data)

        expanded = []
        for template in templates_to_use:
            kw = template.format(
                location=location,
                region=region or location,
                nearby_city=nearby_city,
            )
            if kw not in expanded:
                expanded.append(kw)

        def priority_score(kw: str) -> int:
            kw_lower = kw.lower()
            for phrase, score in self.KEYWORD_PRIORITY.items():
                if phrase in kw_lower:
                    return score
            return 1

        expanded.sort(key=priority_score, reverse=True)
        return expanded[:5]

    def _generate_page(
        self, keyword: str, hotel_data: Dict[str, Any],
        location_context: Dict[str, Any],
    ) -> LocalContentPage:
        title = self._build_title(keyword, hotel_data)
        slug = self._build_slug(keyword)
        content = self._generate_full_content(keyword, hotel_data, location_context)
        word_count = self._count_words(content)
        meta_desc = self._build_meta_description(keyword, hotel_data)
        internal_links = self._build_internal_links(hotel_data)
        schema = self._generate_article_schema(
            LocalContentPage(
                keyword_target=keyword, title=title, slug=slug,
                content_md=content, schema_article={},
                internal_links=internal_links,
                meta_description=meta_desc, word_count=word_count,
            ), hotel_data,
        )
        return LocalContentPage(
            keyword_target=keyword, title=title, slug=slug,
            content_md=content, schema_article=schema,
            internal_links=internal_links,
            meta_description=meta_desc, word_count=word_count,
        )

    def _build_title(self, keyword: str, hotel_data: Dict[str, Any]) -> str:
        location = hotel_data.get("city", "")
        year = self._current_year
        if "precios" in keyword.lower():
            title = f"{keyword.title()} - Guia actualizada {year}"
        elif "como llegar" in keyword.lower() or "desde" in keyword.lower():
            title = f"Como llegar a {location} - Guia completa {year}"
        elif "que hacer" in keyword.lower():
            title = f"Que hacer en {location}: {year} Guia local completa"
        elif "donde hospedarse" in keyword.lower():
            title = f"Donde hospedarse en {location}: guia {year}"
        elif "mejor" in keyword.lower():
            title = f"Las mejores opciones en {location} - {year}"
        elif "hotel" in keyword.lower():
            title = f"Hotel en {location} - Lo que debes saber ({year})"
        elif "que llevar" in keyword.lower():
            title = f"Que llevar a {location} - Lista practica {year}"
        elif "restaurantes" in keyword.lower():
            title = f"Restaurantes en {location}: lo mejor del lugar ({year})"
        else:
            title = f"Guia de {keyword.title()} - Informacion {year}"
        return title

    def _build_slug(self, keyword: str) -> str:
        slug = keyword.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        return slug.strip('-')

    # ------------------------------------------------------------------
    # Content generation - expanded to reach 800-1200 words
    # ------------------------------------------------------------------

    def _generate_full_content(
        self, keyword: str, hotel_data: Dict[str, Any],
        location_context: Dict[str, Any],
    ) -> str:
        """Genera contenido completo de 800-1200 palabras con 6+ secciones."""
        hotel_name = hotel_data.get("name", "El hotel")
        city = hotel_data.get("city", "la zona")
        state = hotel_data.get("state", "Colombia")
        region = location_context.get("region", state)
        phone = hotel_data.get("phone", "")

        parts = []
        parts.append(self._intro(keyword, city))
        parts.append(self._section_contexto(keyword, city, region))
        parts.append(self._section_informacion(keyword, city, region))
        parts.append(self._section_practica(city, region))
        parts.append(self._section_recomendaciones(city, hotel_name, region))
        parts.append(self._conclusion(keyword, city, phone, hotel_name))

        return "\n\n".join(parts)

    def _intro(self, keyword: str, city: str) -> str:
        kw_clean = keyword.title()
        return (
            f"# {kw_clean}: Todo lo que necesitas saber\n\n"
            f"Si estas buscando informacion sobre {keyword} en {city}, "
            f"llegaste al lugar correcto. Esta guia recopila los datos mas "
            f"relevantes para que aproveches al maximo tu visita.\n\n"
            f"Ya sea que estes planeando un fin de semana o una estancia "
            f"mas prolongada, conocer esta zona te ayudara a tomar mejores "
            f"decisiones sobre tu hospedaje y recorrido. Hemos preparado "
            f"esta guia para que tengas toda la informacion necesaria antes "
            f"de tu viaje.\n\n"
            f"En las siguientes secciones encontras informacion practica, "
            f"recomendaciones y consejos que te facilitaran la "
            f"planificacion de tu visita a {city}. Esta guia se actualiza "
            f"periodicamente para que la informacion sea relevante y util "
            f"para quienes planean conocer esta zona del pais. Tanto si es "
            f"tu primera vez en la region como si ya has venido antes, "
            f"siempre hay algo nuevo que descubrir."
        )

    def _section_contexto(self, keyword: str, city: str, region: str) -> str:
        return (
            f"## Sobre {keyword}\n\n"
            f"{city} se ha convertido en un destino cada vez mas visitado "
            f"en {region}. Los viajeros buscan experiencias autenticas que "
            f"vayan mas alla del turismo convencional, y esta zona ofrece "
            f"exactamente eso.\n\n"
            f"La ubicacion de {city} dentro de {region} le da un acceso "
            f"privilegiado a atractivos naturales, gastronomias locales y "
            f"tradiciones culturales que valen la pena explorar con calma.\n\n"
            f"Muchos visitantes llegan atraidos precisamente por lo que "
            f"esta zona tiene para ofrecer. La reputacion de {region} como "
            f"destino turistico ha crecido en los ultimos anos gracias a "
            f"la combinacion de naturaleza, cultura y hospitalidad.\n\n"
            f"El turismo en esta zona tiene caracteristicas particulares "
            f"que lo diferencian de otros destinos del pais. Se destaca por "
            f"su enfoque en experiencias autenticas y en la conexion con el "
            f"entorno natural y cultural que rodea a {city}.\n\n"
            f"Los visitantes suelen quedarse mas tiempo del que tenian "
            f"planeado inicialmente, lo cual dice mucho sobre el atractivo "
            f"de la zona y la calidad de la experiencia que se puede vivir aqui."
        )

    def _section_informacion(self, keyword: str, city: str, region: str) -> str:
        kw_lower = keyword.lower()

        if "precios" in kw_lower:
            return (
                f"## Precios y tarifas en {city}\n\n"
                f"Los precios en {city} varian segun la temporada. "
                f"En temporada alta los costos pueden subir entre un 20 y "
                f"40 por ciento respecto a temporada baja.\n\n"
                f"Los meses de diciembre a enero y junio a julio, asi como "
                f"la semana santa, representan los picos de mayor demanda "
                f"turistica en {region}. Durante estos periodos es "
                f"recomendable reservar con anticipacion.\n\n"
                f"En temporada baja, que comprende los meses de marzo a "
                f"mayo y septiembre a noviembre, encuentras mejores tarifas "
                f"y menos aglomeraciones en los principales atractivos.\n\n"
                f"Nuestra recomendacion es reservar con tiempo y buscar "
                f"viajar fuera de los picos vacacionales para obtener "
                f"mejores tarifas. Tambien es buena idea comparar opciones "
                f"de hospedaje con varios dias de anticipacion.\n\n"
                f"Al planificar tu presupuesto, considera tanto el costo del "
                f"alojamiento como el de actividades y alimentacion. En "
                f"{city} encuentras opciones para todos los rangos de "
                f"presupuesto, desde economico hasta experiencias premium."
            )
        elif "como llegar" in kw_lower or "desde" in kw_lower:
            return (
                f"## Como llegar a {city}\n\n"
                f"{city} se encuentra en {region}, con buenas conexiones "
                f"viales desde las principales ciudades de la zona.\n\n"
                f"Si viajas en vehiculo propio, las rutas principales estan "
                f"en buen estado. El trayecto desde Pereira toma "
                f"aproximadamente entre una y dos horas dependiendo del "
                f"destino exacto.\n\n"
                f"Desde Bogota el recorrido es de aproximadamente seis horas "
                f"por carretera. Tambien existen opciones de transporte "
                f"aereo hasta el aeropuerto de Pereira o Manizales.\n\n"
                f"Si prefieres transporte publico, hay salidas regulares "
                f"desde las terminales cercanas. Los autobuses conectan "
                f"{city} con las principales ciudades de la region.\n\n"
                f"Las carreteras de la zona son en su mayoria pavimentadas, "
                f"aunque algunos tramos secundarios pueden ser de destape. "
                f"Es recomendable verificar el estado de las vias antes de "
                f"viajar, especialmente en temporada de lluvias."
            )
        elif "que hacer" in kw_lower:
            return (
                f"## Planes y actividades en {city}\n\n"
                f"{city} tiene mucho mas de lo que parece a primera vista. "
                f"Ademas de los atractivos principales, hay experiencias "
                f"que solo se disfrutan cuando sabes donde buscar.\n\n"
                f"Entre las actividades mas populares estan los recorridos "
                f"por la zona, la gastronomia local artesanal, actividades "
                f"al aire libre y la inmersion en las tradiciones de "
                f"{region}.\n\n"
                f"Cada zona tiene su propio ritmo y encanto. Los mercados "
                f"locales, las fincas productoras, los miradores naturales "
                f"y los senderos ecologicos son solo algunos de los lugares "
                f"que vale la pena visitar.\n\n"
                f"Recomendamos dedicar al menos dos dias completos para "
                f"conocer los principales atractivos y poder disfrutar "
                f"sin apuros de cada experiencia.\n\n"
                f"Para los viajeros mas aventureros, hay opciones de "
                f"senderismo, avistamiento de aves y recorridos por la "
                f"naturaleza que resultan inolvidables."
            )
        else:
            return (
                f"## Que saber sobre {keyword}\n\n"
                f"Al planear tu visita a {city} por {keyword}, hay algunos "
                f"aspectos practicos que conviene tener claros.\n\n"
                f"La zona de {region} tiene un clima templado que permite "
                f"disfrutar de actividades al aire libre casi todo el ano. "
                f"La temporada seca va de diciembre a marzo y de julio "
                f"a agosto.\n\n"
                f"Durante la temporada de lluvias, que comprende los meses "
                f"de abril a mayo y septiembre a noviembre, es recomendable "
                f"llevar impermeable y planificar actividades que no dependan "
                f"exclusivamente del clima.\n\n"
                f"La infraestructura turistica de {city} ha mejorado "
                f"significativamente en los ultimos anos, ofreciendo "
                f"mejores servicios y mas opciones para los visitantes.\n\n"
                f"En general, {city} es un destino accesible para todo tipo "
                f"de viajeros, ya sea que busquen comodidad y lujo o una "
                f"experiencia mas rustica y en contacto con la naturaleza."
            )

    def _section_practica(self, city: str, region: str) -> str:
        return (
            f"## Informacion practica para tu visita\n\n"
            f"Si estas planeando conocer {city}, hay detalles practicos "
            f"que te ayudaran a disfrutar mejor la experiencia.\n\n"
            f"El clima en {region} es bastante agradable durante la mayor "
            f"parte del ano. Las temperaturas oscilan entre los 15 y 25 "
            f"grados centigrados dependiendo de la zona exacta y de la "
            f"altitud sobre el nivel del mar.\n\n"
            f"Para desplazarte dentro de {city} y sus alrededores, puedes "
            f"utilizar transporte publico local, taxis o vehiculo propio. "
            f"Las distancias entre los principales atractivos no son muy "
            f"grandes, pero algunas rutas requieren vehiculos con buena "
            f"capacidad para carreteras de montana.\n\n"
            f"En cuanto a alimentacion, la zona ofrece una variedad "
            f"interesante de restaurantes y fondas donde probar la "
            f"gastronomia local. Los platos tipicos incluyen productos "
            f"de la region preparados con tecnicas tradicionales.\n\n"
            f"No dejes de probar la cocina local, especialmente aquellos "
            f"platos que incluyen ingredientes producidos en fincas de "
            f"la zona. El sabor de los productos frescos de {region} es "
            f"uno de los mayores atractivos culinarios de la region."
        )

    def _section_cultura(self, city: str, region: str) -> str:
        return (
            f"## Cultura y tradiciones de la region\n\n"
            f"Una de las razones por las que {city} atrae a visitantes "
            f"de todo el pais es su riqueza cultural y sus tradiciones "
            f"arraigadas.\n\n"
            f"La region tiene una historia ligada al cafe, la naturaleza "
            f"y la hospitalidad paisaca. Las fiestas locales, las ferias "
            f"artesanales y los eventos culturales ofrecen una ventana a "
            f"las costumbres que han definido a esta zona.\n\n"
            f"Los artesanos locales trabajan con materiales de la region "
            f"creando piezas unicas que reflejan la identidad cultural del "
            f"lugar. Visitar sus talleres es una experiencia que muchos "
            f"viajeros consideran de las mas memorables.\n\n"
            f"La musica, la danza y las expresiones artisticas de "
            f"{region} tambien forman parte integral de la experiencia "
            f"turistica. En epocas de festivales, la zona cobra una "
            f"energia especial que vale la pena vivir.\n\n"
            f"Muchos de los residentes son descendientes de familias que "
            f"han vivido en la zona durante generaciones, lo que les da "
            f"un conocimiento profundo del lugar y sus tradiciones."
        )

    def _section_recomendaciones(self, city: str, hotel_name: str, region: str) -> str:
        return (
            f"## Recomendaciones practicas\n\n"
            f"Aqui van algunos consejos que te seran utiles durante tu "
            f"visita a {city}:\n\n"
            f"- Lleva ropa comoda y capas, el clima puede cambiar rapido "
            f"durante el dia. Las noches suelen ser mas frias que los dias, "
            f"especialmente en zonas de mayor altitud.\n\n"
            f"- Reserva con tiempo, especialmente si viajas en fines de "
            f"semana largos o temporada alta. En {hotel_name} y otros "
            f"alojamientos de la zona, las mejores habitaciones se reservan "
            f"con varias semanas de anticipacion.\n\n"
            f"- Pregunta a los locales, ellos conocen los mejores rincones "
            f"que no aparecen en las guias turisticas.\n\n"
            f"- Si vienes de otras ciudades, considera llegar un dia antes "
            f"para adaptarte al clima y descansar.\n\n"
            f"- Lleva protector solar y repelente de insectos, especialmente "
            f"si planeas hacer actividades al aire libre o caminatas.\n\n"
            f"Con estos consejos podras aprovechar al maximo tu experiencia "
            f"en {city} y disfrutar de todo lo que {region} tiene para ofrecer."
        )

    def _section_datos_utiles(self, city: str, region: str) -> str:
        return (
            f"## Datos utiles adicionales\n\n"
            f"Ademas de lo mencionado, estos datos pueden ser utiles:\n\n"
            f"- La zona cuenta con cobertura telefonica y servicio de "
            f"internet en la mayor parte del area urbana. En zonas rurales "
            f"la conectividad puede ser limitada.\n\n"
            f"- Los cajeros automaticos se encuentran disponibles en el "
            f"centro de {city}, pero en zonas alejadas puede ser dificil "
            f"encontrarlos. Lleva efectivo suficiente para excursiones.\n\n"
            f"- La senalizacion turistica en {region} ha mejorado, pero "
            f"algunos senderos pueden requerir guia local. Pide orientacion "
            f"en tu alojamiento.\n\n"
            f"- Los horarios comerciales en {city} van de las 8 de la manana "
            f"a las 6 de la tarde. Los restaurantes sirven almuerzo entre "
            f"las 11 y las 2 de la tarde.\n\n"
            f"- Si necesitas servicio medico, {city} cuenta con puestos "
            f"de salud y farmacias. Para emergencias, los hospitales mas "
            f"cercanos se encuentran en las ciudades principales de "
            f"{region}."
        )

    def _conclusion(self, keyword: str, city: str, phone: str, hotel_name: str) -> str:
        conclusion = (
            f"## Conclusion\n\n"
            f"{keyword} es un tema que vale la pena conocer antes de "
            f"visitar {city}. Con esta informacion puedes planificar "
            f"mejor y aprovechar cada momento de tu viaje.\n\n"
            f"Esperamos que esta guia te sea util para organizar tu "
            f"visita y disfrutes la region.\n\n"
            f"Si quieres conocer mas sobre {city} y sus alrededores, "
            f"puedes contactarnos."
        )
        if phone:
            phone_clean = re.sub(r'[^\d+]', '', phone).lstrip('+')
            conclusion += f"\n\nPara reservar: [{hotel_name} - WhatsApp](https://wa.me/{phone_clean})"
        return conclusion

    def _count_words(self, text: str) -> int:
        return len(text.split())

    def _build_meta_description(self, keyword: str, hotel_data: Dict[str, Any]) -> str:
        city = hotel_data.get("city", "")
        hotel_name = hotel_data.get("name", "")
        year = self._current_year
        meta = (
            f"Guia sobre {keyword} en {city}. Informacion actualizada "
            f"{year} para planificar tu viaje."
        )
        if len(meta) > 160:
            meta = meta[:157] + "..."
        return meta

    def _build_internal_links(self, hotel_data: Dict[str, Any]) -> List[str]:
        website = hotel_data.get("website", "")
        phone = hotel_data.get("phone", "")
        hotel_name = hotel_data.get("name", "Hotel")
        links = []
        if website:
            links.append(f"Visita {hotel_name}: {website}")
        else:
            links.append(f"{hotel_name} - Pagina principal")
        if phone:
            phone_clean = re.sub(r'[^\d+]', '', phone).lstrip('+')
            links.append(f"Reservar por WhatsApp: https://wa.me/{phone_clean}")
        else:
            links.append("Reservar: contactar al hotel")
        return links

    def _generate_article_schema(
        self, page: LocalContentPage, hotel_data: Dict[str, Any]
    ) -> dict:
        hotel_name = hotel_data.get("name", "")
        website = hotel_data.get("website", "")
        city = hotel_data.get("city", "")
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": page.title,
            "description": page.meta_description,
            "author": {"@type": "Organization", "name": hotel_name},
            "publisher": {"@type": "Organization", "name": hotel_name},
            "keywords": page.keyword_target,
            "inLanguage": "es-CO",
            "datePublished": datetime.now().strftime("%Y-%m-%d"),
            "about": {
                "@type": "Place",
                "name": city,
                "address": {"@type": "PostalAddress", "addressLocality": city},
            },
        }
        if website:
            schema["mainEntityOfPage"] = {
                "@type": "WebPage",
                "@id": f"{website.rstrip('/')}/{page.slug}",
            }
        return schema

    def _resolve_templates(self, hotel_type: str, hotel_data: Dict[str, Any]) -> List[str]:
        type_map = {
            "termales": ["termales", "boutique", "general"],
            "eco": ["parque_natural", "cafe", "general"],
            "cafe": ["cafe", "boutique", "general"],
            "pueblo": ["pueblo_patrimonio", "general"],
            "boutique": ["boutique", "general"],
            "general": ["general"],
        }
        template_keys = type_map.get(hotel_type, ["general"])
        templates = []
        for key in template_keys:
            if key in self.KEYWORD_TEMPLATES:
                templates.extend(self.KEYWORD_TEMPLATES[key])
        seen = set()
        unique = []
        for t in templates:
            if t not in seen:
                seen.add(t)
                unique.append(t)
        return unique[:8]

    @staticmethod
    def content_passes_scrubber(content: str) -> bool:
        """Verifica que el contenido no contenga frases AI genericas."""
        content_lower = content.lower()
        for phrase in LocalContentGenerator.AI_GENERIC_PHRASES:
            if phrase in content_lower:
                return False
        return True
