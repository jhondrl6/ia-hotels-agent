"""
Módulo de onboarding para captura de datos operativos del hotel.

Este módulo proporciona herramientas interactivas para recopilar
datos operativos confirmados del hotel antes del análisis.
"""

from modules.onboarding.forms import OnboardingForm
from modules.onboarding.validators import (
    validate_habitaciones,
    validate_reservas_mes,
    validate_valor_reserva,
    validate_canal_directo,
)
from modules.onboarding.data_loader import (
    load_onboarding_data,
    merge_with_hotel_data,
)

__all__ = [
    "OnboardingForm",
    "validate_habitaciones",
    "validate_reservas_mes",
    "validate_valor_reserva",
    "validate_canal_directo",
    "load_onboarding_data",
    "merge_with_hotel_data",
]
