"""
Paso de GSC opcional para el onboarding.

FASE: FASE-D (GAP-IAO-01-06)
Estado: IMPLEMENTADO

Pregunta si tiene Google Search Console y captura el site_url.
"""

from typing import Dict, Any, Optional


def ask_gsc_during_onboarding(
    verbose: bool = True,
    input_func=input,
    output_func=print,
) -> Dict[str, Any]:
    """
    Pregunta al usuario si tiene Google Search Console y captura datos.

    Args:
        verbose: Mostrar mensajes explicativos
        input_func: Funcion de entrada (para tests)
        output_func: Funcion de salida (para tests)

    Returns:
        Dict con:
        - has_gsc: bool
        - site_url: str or None
        - credentials_path: str or None
    """
    result: Dict[str, Any] = {
        "has_gsc": False,
        "site_url": None,
        "credentials_path": None,
    }

    if verbose:
        output_func("\n--- Google Search Console (Opcional) ---")
        output_func("Google Search Console proporciona datos de palabras clave,")
        output_func("posiciones en busqueda organica y CTR de su sitio web.")
        output_func("Esta informacion enriquece el diagnostico con datos reales.\n")
        output_func("El analisis de GSC es 100% gratuito.\n")

    try:
        answer = input_func("¿Tiene Google Search Console configurado para su sitio web? (s/n) [n]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return result

    if answer in ('s', 'si', 'y', 'yes'):
        result["has_gsc"] = True

        if verbose:
            output_func("\nIngrese la URL del sitio en Search Console.")
            output_func("Formato: https://www.ejemplo.com o sc-domain:ejemplo.com")

        try:
            site_url = input_func("Site URL: ").strip()
        except (EOFError, KeyboardInterrupt):
            return result

        if site_url:
            result["site_url"] = site_url
            if verbose:
                output_func(f"\nGSC configurado con site_url: {site_url}")
                output_func("Se usaran las mismas credenciales del service account configuradas para GA4.")
        else:
            if verbose:
                output_func("No se ingreso site_url, GSC no se configurara.")
            result["has_gsc"] = False
    else:
        if verbose:
            output_func("GSC sera omitido. Puede configurarse mas tarde.")

    return result


def apply_gsc_config(
    gsc_data: Dict[str, Any],
    config_path: Optional[str] = None,
    verbose: bool = True,
    output_func=print,
    save_func=None,
) -> bool:
    """
    Aplica la configuracion de GSC al archivo de config del onboarding.

    Args:
        gsc_data: Resultados de ask_gsc_during_onboarding
        config_path: Ruta al archivo de config YAML
        verbose: Mostrar mensajes
        output_func: Funcion de salida
        save_func: Funcion para guardar la config (para tests)

    Returns:
        True si se aplico config exitosamente
    """
    if not gsc_data.get("has_gsc"):
        return False

    config_update = {
        "gsc_site_url": gsc_data.get("site_url"),
        "gsc_enabled": True,
        "gsc_credentials_source": "ga4_service_account",
    }

    if save_func:
        # Permite tests con save_func simulada
        save_func(config_update)
        if verbose:
            output_func(f"Configuracion GSC guardada: site_url={config_update['gsc_site_url']}")
        return True

    # Guardar en archivo de config
    if config_path:
        try:
            import yaml
            from pathlib import Path

            path = Path(config_path)
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f) or {}
            else:
                config = {}

            config["gsc"] = config_update

            with open(path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

            if verbose:
                output_func(f"Configuracion GSC guardada en {config_path}")
            return True

        except Exception as e:
            if verbose:
                output_func(f"Error guardando config GSC: {e}")
            return False
    else:
        if verbose:
            output_func(f"Config GSC lista: {config_update}")
        return True
