"""WhatsAppSetupGuideGenerator - guia de preparacion y validacion del canal WhatsApp.

FASE-B (plan REFACTOR-WHATSAPP-ENTREGA-2026-09-18, AC2).

Que es y por que existe
----------------------
Cuando la auditoria NO puede confirmar un numero de WhatsApp utilizable, lo que se
promete al cliente no puede ser un boton operativo: seria una promesa falsa (el
 boton se publica apuntando a `https://wa.me/` vacio, o a un numero inventado). Este
generador produce el entregable honesto para ese caso: una guia de preparacion y
solicitud de validacion.

Tres reglas duras, verificadas por tests:

1. No contiene NINGUN numero de telefono: ni real, ni de ejemplo, ni placeholder
   numerico. El unico valor que se imprime es el nombre del hotel y su URL, que ya
   son datos de la corrida.
2. No contiene enlaces `wa.me` ni `api.whatsapp.com`: sin numero verificado no hay
   destino que enlazar.
3. No afirma que el hotel NO tenga WhatsApp. Dice que el canal no fue verificado en
   la ruta inspeccionada y pide confirmacion. `L-PF6`: ausencia observada y lector
   fallido no son equivalentes; afirmar ausencia confirmada es el error que esta
   guia prohibe.

No sustituye a `WhatsAppConflictGuideGenerator`, que es para el caso de numeros en
disputa (`whatsapp_conflict`), ni a `wa_button_gen` (legacy: emite un numero de
placeholder, ver `modules/delivery/generators/wa_button_gen.py`).
"""

from typing import Optional


class WhatsAppSetupGuideGenerator:
    """Genera la guia de preparacion/validacion del canal WhatsApp (sin numero)."""

    #: Marco que la guia ofrece al hotel para comunicar el numero. No es un numero.
    _CAMPO_PENDIENTE = "<Numero WhatsApp a confirmar por el hotel>"

    def generate(
        self,
        hotel_name: str,
        site_url: Optional[str] = None,
        observation_note: Optional[str] = None,
    ) -> str:
        """Devuelve el Markdown de la guia.

        Args:
            hotel_name: nombre comercial del hotel (unico dato identificativo que
                se imprime).
            site_url: URL inspeccionada, para que el lector sepa de donde parte la
                observacion. Opcional: si falta, la guia dice que no se registro.
            observation_note: nota de lo observado en el sitio (p. ej. que existe
                una huella del widget pero no un enlace con numero). Opcional.

        Returns:
            Texto Markdown de la guia.
        """
        nombre = (hotel_name or "el hotel").strip() or "el hotel"
        url = (site_url or "").strip()
        linea_url = f"`{url}`" if url else "_(no se registro en esta corrida)_"
        nota = (observation_note or "").strip()
        bloque_observado = (
            f"\n**Qué observamos en el sitio:** {nota}\n" if nota else ""
        )

        return f"""# Configuración de WhatsApp — {nombre}

**Estado del canal: NO VERIFICADO. Esta guía no instala nada.**

Servicio: preparación y validación del canal de WhatsApp de {nombre}.
Sitio inspeccionado: {linea_url}
{bloque_observado}
## Por qué recibes esta guía y no un botón

Un botón de WhatsApp solo funciona si apunta a un número concreto y confirmado. En la
auditoría no pudimos confirmar un número utilizable para {nombre}, y un botón sin
número verificable se publica roto: el huésped que lo pulsa no llega a ninguna parte.

Por eso esta entrega es una solicitud de validación, no una instalación. Cuando
confirmes el número, el botón se genera e instala como paso siguiente.

Qué **no** afirma este documento: no afirma que {nombre} no tenga WhatsApp. Afirmar
eso exigiría haber verificado todas las rutas y todos los mecanismos del sitio, y eso
no ocurrió. Lo que afirma es que el número no quedó verificado en lo inspeccionado, y
por tanto no puede publicarse como canal operativo.

## Qué necesitamos de tu parte

Un solo dato, con tu confirmación explícita:

- **Número de WhatsApp que debe quedar público**, en formato internacional
  (indicativo del país + número), con el campo: {self._CAMPO_PENDIENTE}
- **Quién responde** a ese número (recepción, reservas, o un tercero) y en qué
  horario, porque el botón promete una respuesta.
- **Si el número ya está en Google Business Profile**, dínoslo igual: comparamos
  ambas fuentes y, si difieren, te lo mostramos antes de publicar nada.

Con ese dato confirmado, la entrega del botón pasa a la fase siguiente y este
documento queda cerrado como resuelto.

## Pasos para dejar el canal listo

1. **Confirmar el número** que se va a publicar (el campo de arriba). Sin esta
   confirmación no se genera el botón.
2. **Elegir el mecanismo de publicación**, según cómo opere {nombre} hoy:
   - *Enlace directo*: un enlace simple en la cabecera o el pie de la web. Es lo que
     instalamos por defecto.
   - *Widget flotante*: un componente de terceros. Si ya tienes uno, dinos cuál: lo
     auditamos en lugar de duplicarlo.
3. **Definir el mensaje pre-rellenado** que abre el chat (por ejemplo una saludo con
   la intención de reserva), para que la conversación entre clasificable.
4. **Decidir la métrica**: si quieres medir cuántos llegan por este canal, se configura
   el evento de clic junto con la analítica del paquete.
5. **Validación humana obligatoria antes de publicar**: una persona del equipo revisa
   que el enlace abre el chat del número correcto. Hasta esa validación, el canal se
   reporta como preparación pendiente, no como instalación realizada.

## Qué se entrega y qué queda pendiente

| Elemento | Estado en esta entrega |
|---|---|
| Guía de preparación y solicitud del número | Entregada |
| Número de WhatsApp publicado | Pendiente de tu confirmación |
| Botón / enlace operativo | No generado a propósito |
| Verificación en el sitio publicado | Pendiente, tras la confirmación |
"""
