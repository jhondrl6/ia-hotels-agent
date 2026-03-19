"""
Validadores para campos del formulario de onboarding.

Cada validador retorna una tupla con:
- bool: Si la validación fue exitosa
- Optional[T]: El valor validado y convertido al tipo correcto
- Optional[str]: Mensaje de error si la validación falló
"""

from typing import Any, Optional, Tuple


def validate_habitaciones(value: Any) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Valida número de habitaciones del hotel.
    
    Args:
        value: Valor a validar (puede ser str, int, etc.)
        
    Returns:
        Tupla con (éxito, valor_validado, mensaje_error)
        
    Rango válido: 1-500 habitaciones
    """
    try:
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return False, None, "El campo no puede estar vacío"
        
        num = int(str(value).strip())
        
        if num < 1:
            return False, None, "El número de habitaciones debe ser al menos 1"
        
        if num > 500:
            return False, None, "El número de habitaciones no puede exceder 500"
        
        return True, num, None
        
    except (ValueError, TypeError):
        return False, None, f"'{value}' no es un número válido. Ingrese un número entero."


def validate_reservas_mes(value: Any) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Valida reservas mensuales del hotel.
    
    Args:
        value: Valor a validar
        
    Returns:
        Tupla con (éxito, valor_validado, mensaje_error)
        
    Rango válido: 1-10000 reservas/mes
    """
    try:
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return False, None, "El campo no puede estar vacío"
        
        num = int(str(value).strip().replace(",", "").replace(".", ""))
        
        if num < 1:
            return False, None, "El número de reservas debe ser al menos 1"
        
        if num > 10000:
            return False, None, "El número de reservas no puede exceder 10,000"
        
        return True, num, None
        
    except (ValueError, TypeError):
        return False, None, f"'{value}' no es un número válido. Ingrese un número entero."


def validate_valor_reserva(value: Any) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Valida valor promedio de reserva en COP.
    
    Args:
        value: Valor a validar
        
    Returns:
        Tupla con (éxito, valor_validado, mensaje_error)
        
    Rango válido: $50,000 - $5,000,000 COP
    """
    try:
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return False, None, "El campo no puede estar vacío"
        
        # Clean common formats: "350.000", "350,000", "$350000"
        clean_str = str(value).strip()
        clean_str = clean_str.replace("$", "").replace(" ", "")
        clean_str = clean_str.replace(".", "").replace(",", "")
        
        num = int(clean_str)
        
        if num < 50000:
            return False, None, "El valor de reserva debe ser al menos $50,000 COP"
        
        if num > 5000000:
            return False, None, "El valor de reserva no puede exceder $5,000,000 COP"
        
        return True, num, None
        
    except (ValueError, TypeError):
        return False, None, f"'{value}' no es un valor válido. Ingrese el valor en COP (ej: 350000)"


def validate_canal_directo(value: Any) -> Tuple[bool, Optional[float], Optional[str]]:
    """
    Valida porcentaje de reservas por canal directo.
    
    Args:
        value: Valor a validar
        
    Returns:
        Tupla con (éxito, valor_validado, mensaje_error)
        
    Rango válido: 0-100%
    """
    try:
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return False, None, "El campo no puede estar vacío"
        
        # Clean common formats: "45%", "45.0", "45,5"
        clean_str = str(value).strip().replace("%", "").replace(",", ".")
        
        num = float(clean_str)
        
        if num < 0:
            return False, None, "El porcentaje no puede ser negativo"
        
        if num > 100:
            return False, None, "El porcentaje no puede exceder 100%"
        
        return True, round(num, 1), None
        
    except (ValueError, TypeError):
        return False, None, f"'{value}' no es un porcentaje válido. Ingrese un número entre 0 y 100."


def validate_optional_field(
    value: Any, 
    validator_func: callable,
    allow_skip: bool = True
) -> Tuple[bool, Optional[Any], Optional[str]]:
    """
    Wrapper para validar campos opcionales.
    
    Args:
        value: Valor a validar
        validator_func: Función validadora a usar
        allow_skip: Si permite omitir el campo (Enter para saltar)
        
    Returns:
        Tupla con (éxito, valor_validado, mensaje_error)
        Si se omite, retorna (True, None, None)
    """
    if value is None or (isinstance(value, str) and value.strip() == ""):
        if allow_skip:
            return True, None, None
        return False, None, "Este campo es obligatorio"
    
    return validator_func(value)
