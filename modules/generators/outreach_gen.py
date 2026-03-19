from pathlib import Path


class OutreachGenerator:
    def __init__(self):
        self.templates_path = Path("templates")

    def generate_all(self, hotel_data, claude_analysis, output_dir):
        """Genera todos los materiales de outreach."""

        comunicaciones_dir = output_dir / "comunicaciones"
        comunicaciones_dir.mkdir(exist_ok=True)

        self._generate_email(hotel_data, claude_analysis, comunicaciones_dir)
        self._generate_whatsapp(hotel_data, claude_analysis, comunicaciones_dir)
        self._generate_linkedin(hotel_data, claude_analysis, comunicaciones_dir)
        self._generate_followup_guide(hotel_data, comunicaciones_dir)

        print("   [OK] Materiales de comunicacion generados")

    def _generate_email(self, hotel_data, claude_analysis, output_dir):
        """Genera email de primer contacto."""

        template = self._get_default_email_template()
        try:
            with (self.templates_path / "email_primer_contacto.txt").open("r", encoding="utf-8") as template_file:
                template = template_file.read()
        except FileNotFoundError:
            pass

        brechas = claude_analysis.get("brechas_criticas", [])
        pain_points = "\n".join(
            f"[FAIL] {item['nombre']}: {item['descripcion']}"
            for item in brechas[:3]
        )

        email_content = template.format(
            hotel_nombre=hotel_data.get("nombre"),
            nombre_contacto="[Nombre del gerente]",
            hotel_url=hotel_data.get("url"),
            perdida_mensual=claude_analysis.get("perdida_mensual_total", 0),
            pain_points=pain_points,
            calendly_link="[CALENDLY_LINK]",
            tu_nombre="[Tu nombre]",
        )

        (output_dir / "email_primer_contacto.txt").write_text(email_content, encoding="utf-8")

        instrucciones = f"""# INSTRUCCIONES - Email Primer Contacto

## [WARN] Antes de enviar
- Personaliza el nombre del gerente.
- Reemplaza el link de Calendly.
- Ajusta tu nombre y cargos.

## [EMAIL] Fuentes de contacto
- Website del hotel (seccion contacto).
- LinkedIn del hotel.
- Perfil de Google Business.
- Telefono directo: {hotel_data.get('contacto', {}).get('telefono', 'Indagar')}.

## [OK] Checklist
- [ ] Nombre del contacto actualizado
- [ ] Calendly configurado
- [ ] Email del hotel verificado
- [ ] PDF adjunto
- [ ] Recordatorio de seguimiento programado

**Dato clave:** ${claude_analysis.get('perdida_mensual_total', 0):,.0f} COP perdidos cada mes.
"""

        (output_dir / "email_INSTRUCCIONES.txt").write_text(instrucciones, encoding="utf-8")

    def _generate_whatsapp(self, hotel_data, claude_analysis, output_dir):
        """Genera mensajes de WhatsApp con quick_win_gift."""

        mensaje_corto = (
            f"""Hola {hotel_data.get('nombre')}! [HELLO]

Analise su hotel y estan perdiendo ${claude_analysis.get('perdida_mensual_total', 0)//1000}K/mes \
en reservas directas por no estar visibles en Google Maps y ChatGPT.

?Disponible 20 min esta semana para mostrarle el diagnostico completo? Es gratis y muy revelador.

[Tu nombre] - IA Hoteles Agent
"Primera Recomendacion en Agentes IA"
"""
        )[:300]

        brecha1 = claude_analysis.get("brechas_criticas", [{}])[0].get("nombre", "GBP sin optimizar")
        brecha2 = claude_analysis.get("brechas_criticas", [{}, {}])[1].get("nombre", "Cero visibilidad IA")

        # Obtener quick_win_gift si está disponible en el análisis
        quick_win_gift = claude_analysis.get("quick_win_action", {})
        quick_win_text = ""
        if quick_win_gift and isinstance(quick_win_gift, dict):
            action = quick_win_gift.get("action", "sube 5 fotos a Google Maps")
            impact = quick_win_gift.get("expected_impact", "primeras mencionas en búsqueda local")
            quick_win_text = f"\nPD: Mientras decides, haz esto HOY gratis: {action}. Ganas {impact} sin gastar un peso."

        mensaje_largo = f"""Hola! Soy [Tu nombre] de IA Hoteles Agent.

Le hice un analisis a {hotel_data.get('nombre')} y encontre una oportunidad de ${claude_analysis.get('perdida_mensual_total', 0):,.0f} COP/mes porque:

-  {brecha1}
-  {brecha2}

Ya le envie el diagnostico por email, ?lo recibio?

Puede agendar una videollamada aqui: [CALENDLY_LINK]{quick_win_text}
"""

        contenido = f"""# MENSAJES WHATSAPP - {hotel_data.get('nombre')}

## [PHONE] Mensaje inicial

{mensaje_corto}

---

## [PHONE] Follow-up (CON QUICK WIN GIFT)

{mensaje_largo}

---

## [GIFT] Quick Win Action
Si el cliente no responde al diagnosis pero muestra interés:
{quick_win_text if quick_win_text else "Sube 5 fotos a Google Maps + añade horarios extendidos + pide 3 reseñas a clientes satisfechos"}

**Efecto reciprocidad**: Dar algo gratis ANTES de pedir dinero genera 3X más probabilidad de conversión.

---

## [IDEA] Tips rapidos
- Enviar martes-jueves, 10am-12pm o 3-5pm.
- Personalizar numero y nombre.
- Evitar reenviar PDF por WhatsApp.
- Esperar 48h antes de segundo mensaje.
- Si cliente pregunta por precio, mandarle quick_win ANTES de propuesta.

Numero objetivo: {hotel_data.get('contacto', {}).get('telefono', 'PENDIENTE BUSCAR')}
"""

        (output_dir / "whatsapp_mensajes.txt").write_text(contenido, encoding="utf-8")

    def _generate_linkedin(self, hotel_data, claude_analysis, output_dir):
        """Genera mensaje para LinkedIn InMail."""

        # v3.3.1: Prune LinkedIn for Eje Cafetero region
        ubicacion = str(hotel_data.get("ubicacion", "")).lower()
        region = str(hotel_data.get("region", "")).lower()
        eje_cafetero_tokens = ["risaralda", "quindio", "caldas", "santa rosa", "pereira", "armenia", "manizales", "eje cafetero"]
        
        if any(token in ubicacion for token in eje_cafetero_tokens) or any(token in region for token in eje_cafetero_tokens):
            print("   [PODA] Saltando linkedin_inmessage.txt (Región Eje Cafetero detectada)")
            return

        mensaje = f"""Asunto: Oportunidad: {hotel_data.get('nombre')} y la visibilidad en IA

Hola [Nombre],

Analice {hotel_data.get('nombre')} y note que estan dejando de percibir ${claude_analysis.get('perdida_mensual_total', 0):,.0f} COP/mes porque el hotel no es visible en Google Maps ni ChatGPT.

Preparé un diagnostico completo (15 min de lectura) y me gustaria compartirlo sin compromiso.

?Te interesa que te lo envie?

Saludos,
[Tu nombre]
IA Hoteles Agent
"""

        contenido = f"""# LINKEDIN INMAIL - {hotel_data.get('nombre')}

## [BRIEFCASE] Mensaje sugerido

{mensaje}

---

## [TARGET] Estrategia
- Investiga el perfil antes de escribir.
- Menciona puntos en comun o logros recientes.
- Adjunta preview del diagnostico si es posible.
- Respeta el tono profesional.

## [CHART] Follow-up (7 dias)
Hola [Nombre],

Reviso si alcanzaste a ver mi mensaje sobre {hotel_data.get('nombre')}.  
Quedo pendiente si deseas una revision rapida.

Gracias,
[Tu nombre]
"""

        (output_dir / "linkedin_inmessage.txt").write_text(contenido, encoding="utf-8")

    def _generate_followup_guide(self, hotel_data, output_dir):
        """Genera guia de seguimiento de contactos."""

        guia = f"""# GUIA DE SEGUIMIENTO - {hotel_data.get('nombre')}

## [DATE] Cronograma primeros 14 dias
- **Dia 0:** Email + PDF
- **Dia 2:** WhatsApp si no abre email
- **Dia 5:** Follow-up suave
- **Dia 7:** Ultimo intento directo
- **Dia 10-14:** Soft nurturing

## [TARGET] Metricas
- Apertura email objetivo: 40-50%
- Respuesta combinada: 15-20%
- Agendamiento call: 8-12%
- Cierre estimado: 3-5%

## [IDEA] Scripts utiles
- "No tenemos presupuesto": enfatiza ahorro OTA.
- "Ya tenemos agencia": explicar enfoque IA.
- "Necesito pensarlo": ofrecer resumen rapido.
- "Enviame mas info": enviar audio de 2 minutos.

**Perdida estimada:** ${hotel_data.get('perdida_mensual_total', 0):,.0f} COP/mes.
"""

        (output_dir / "guia_seguimiento.md").write_text(guia, encoding="utf-8")

    def _get_default_email_template(self):
        return (
            "Asunto: {hotel_nombre}: ${perdida_mensual:,.0f} COP que no estan llegando cada mes\n\n"
            "Hola {nombre_contacto},\n\n"
            "Analizamos {hotel_url} con nuestro sistema 2-Pilares (Google Maps + IA) y encontramos gaps\n"
            "que impiden reservas directas por ${perdida_mensual:,.0f} COP/mes.\n\n"
            "{pain_points}\n\n"
            "Adjuntamos diagnostico de 15 minutos de lectura.\n"
            "?Agendamos una llamada de 20 minutos esta semana?\n\n"
            "Agenda aqui: {calendly_link}\n\n"
            "Saludos,\n"
            "{tu_nombre}\n"
            "IA Hoteles Agent\n"
        )
