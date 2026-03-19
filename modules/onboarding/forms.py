"""
Formulario interactivo CLI para capturar datos operativos del hotel.

Proporciona una interfaz de línea de comandos para recopilar
datos confirmados del hotel antes del análisis.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from modules.onboarding.validators import (
    validate_habitaciones,
    validate_reservas_mes,
    validate_valor_reserva,
    validate_canal_directo,
    validate_optional_field,
)
from modules.onboarding.data_loader import (
    create_onboarding_template,
    generate_slug,
)


class OnboardingForm:
    """
    Formulario interactivo para capturar datos operativos del hotel.
    
    Campos:
    - habitaciones: int (ej: 22)
    - reservas_mes: int (ej: 180)
    - valor_reserva_cop: int (ej: 350000)
    - canal_directo_pct: float (ej: 45.0)
    
    Ejemplo de uso:
        form = OnboardingForm()
        form.run_interactive()
        data = form.to_dict()
        form.save_yaml(Path("data/clientes/hotel_onboarding.yaml"))
    """
    
    FIELD_CONFIG = {
        "habitaciones": {
            "question": "Número de habitaciones del hotel",
            "example": "22",
            "validator": validate_habitaciones,
            "required": True,
        },
        "reservas_mes": {
            "question": "Reservas mensuales promedio",
            "example": "180",
            "validator": validate_reservas_mes,
            "required": True,
        },
        "valor_reserva_cop": {
            "question": "Valor promedio de reserva (en COP)",
            "example": "350000 (sin puntos ni comas)",
            "validator": validate_valor_reserva,
            "required": True,
        },
        "canal_directo_pct": {
            "question": "Porcentaje de reservas por canal directo",
            "example": "45.0 (puede incluir %)",
            "validator": validate_canal_directo,
            "required": True,
        },
    }
    
    def __init__(self, hotel_nombre: Optional[str] = None, verbose: bool = True):
        """
        Inicializa el formulario.
        
        Args:
            hotel_nombre: Nombre del hotel (opcional)
            verbose: Si mostrar mensajes de progreso
        """
        self._data: Dict[str, Any] = create_onboarding_template()
        self._verbose = verbose
        self._completed = False
        
        if hotel_nombre:
            self._data["hotel"]["nombre"] = hotel_nombre
    
    def _print(self, message: str) -> None:
        """Imprime mensaje si verbose está activado."""
        if self._verbose:
            print(message)
    
    def _show_header(self) -> None:
        """Muestra el encabezado del formulario."""
        self._print("\n" + "=" * 60)
        self._print("  CAPTURA DE DATOS OPERATIVOS - IA Hoteles Agent")
        self._print("=" * 60)
        self._print("\nEste formulario captura datos confirmados del hotel")
        self._print("para eliminar estimaciones en el análisis.\n")
        self._print("Instrucciones:")
        self._print("  - Ingrese el valor solicitado y presione Enter")
        self._print("  - Los valores deben ser reales y confirmados")
        self._print("-" * 60 + "\n")
    
    def _prompt_field(self, field_name: str, config: Dict) -> Optional[Any]:
        """
        Solicita un campo al usuario con validación.
        
        Args:
            field_name: Nombre del campo
            config: Configuración del campo
            
        Returns:
            Valor validado o None si se omitió
        """
        question = config["question"]
        example = config["example"]
        validator = config["validator"]
        required = config["required"]
        
        while True:
            prompt_text = f"\n{question}"
            if example:
                prompt_text += f" (ej: {example})"
            prompt_text += ": "
            
            try:
                user_input = input(prompt_text).strip()
            except (EOFError, KeyboardInterrupt):
                self._print("\n\nFormulario cancelado.")
                return None
            
            # Handle empty input
            if not user_input:
                if not required:
                    self._print("  → Campo omitido")
                    return None
                self._print("  ✗ Este campo es obligatorio. Intente de nuevo.")
                continue
            
            # Validate
            success, value, error = validator(user_input)
            
            if success:
                self._print(f"  ✓ Valor aceptado: {value}")
                return value
            else:
                self._print(f"  ✗ {error}")
    
    def run_interactive(self) -> bool:
        """
        Ejecuta formulario CLI interactivo.
        
        Returns:
            True si el formulario se completó exitosamente
        """
        self._show_header()
        
        # Ask for hotel name if not provided
        if not self._data["hotel"]["nombre"]:
            try:
                nombre = input("\nNombre del hotel (opcional, Enter para omitir): ").strip()
                if nombre:
                    self._data["hotel"]["nombre"] = nombre
            except (EOFError, KeyboardInterrupt):
                self._print("\nFormulario cancelado.")
                return False
        
        # Collect each field
        campos_confirmados: List[str] = []
        
        for field_name, config in self.FIELD_CONFIG.items():
            value = self._prompt_field(field_name, config)
            
            if value is None and config["required"]:
                self._print(f"\n✗ Formulario incompleto. Campo '{field_name}' es obligatorio.")
                return False
            
            if value is not None:
                self._data["datos_operativos"][field_name] = value
                campos_confirmados.append(field_name)
        
        # Update metadata
        self._data["metadatos"]["fecha_captura"] = datetime.now(timezone.utc).isoformat()
        self._data["metadatos"]["campos_confirmados"] = campos_confirmados
        
        self._completed = True
        
        # Show summary
        self._show_summary()
        
        # Ask to save
        return self._prompt_save()
    
    def _show_summary(self) -> None:
        """Muestra resumen de datos capturados."""
        self._print("\n" + "-" * 60)
        self._print("  RESUMEN DE DATOS CAPTURADOS")
        self._print("-" * 60)
        
        if self._data["hotel"]["nombre"]:
            self._print(f"  Hotel: {self._data['hotel']['nombre']}")
        
        datos = self._data["datos_operativos"]
        self._print(f"  Habitaciones: {datos['habitaciones']}")
        self._print(f"  Reservas/mes: {datos['reservas_mes']}")
        self._print(f"  Valor reserva: ${datos['valor_reserva_cop']:,} COP")
        self._print(f"  Canal directo: {datos['canal_directo_pct']}%")
        self._print("-" * 60)
    
    def _prompt_save(self) -> bool:
        """
        Pregunta si desea guardar los datos.
        
        Returns:
            True si se guardó exitosamente
        """
        try:
            response = input("\n¿Desea guardar estos datos? (s/n): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return False
        
        if response in ("s", "si", "sí", "y", "yes"):
            return self._auto_save()
        
        self._print("Datos no guardados.")
        return True
    
    def _auto_save(self) -> bool:
        """Guarda automáticamente en la ubicación predeterminada."""
        nombre = self._data["hotel"]["nombre"] or "hotel"
        slug = generate_slug(nombre)
        
        output_dir = Path("data/clientes")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / f"{slug}_onboarding.yaml"
        
        return self.save_yaml(output_path)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Retorna datos como diccionario.
        
        Returns:
            Diccionario con todos los datos capturados
        """
        return self._data.copy()
    
    def save_yaml(self, path: Path) -> bool:
        """
        Guarda datos en formato YAML.
        
        Args:
            path: Ruta del archivo de salida
            
        Returns:
            True si se guardó exitosamente
        """
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            
            content = yaml.dump(
                self._data,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False,
            )
            
            path.write_text(content, encoding="utf-8")
            self._print(f"✓ Datos guardados en: {path}")
            return True
            
        except Exception as e:
            self._print(f"✗ Error al guardar: {e}")
            return False
    
    def save_json(self, path: Path) -> bool:
        """
        Guarda datos en formato JSON.
        
        Args:
            path: Ruta del archivo de salida
            
        Returns:
            True si se guardó exitosamente
        """
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            
            content = json.dumps(
                self._data,
                ensure_ascii=False,
                indent=2,
            )
            
            path.write_text(content, encoding="utf-8")
            self._print(f"✓ Datos guardados en: {path}")
            return True
            
        except Exception as e:
            self._print(f"✗ Error al guardar: {e}")
            return False
    
    @property
    def is_completed(self) -> bool:
        """Retorna True si el formulario se completó."""
        return self._completed
    
    @property
    def datos_operativos(self) -> Dict[str, Any]:
        """Retorna solo los datos operativos."""
        return self._data.get("datos_operativos", {})
    
    @property
    def campos_confirmados(self) -> List[str]:
        """Retorna lista de campos confirmados."""
        return self._data.get("metadatos", {}).get("campos_confirmados", [])
