# config/env_validator.py
import os
import sys
from pathlib import Path

class EnvValidator:
    REQUIRED_VARS = ['DEEPSEEK_API_KEY']
    OPTIONAL_VARS = ['ANTHROPIC_API_KEY', 'PERPLEXITY_API_KEY', 'OPENAI_API_KEY']
    
    @classmethod
    def validate(cls):
        """Validar que todas las variables requeridas estén configuradas"""
        missing = []
        
        for var in cls.REQUIRED_VARS:
            if not os.getenv(var):
                missing.append(var)
        
        if missing:
            print(f"❌ ERROR: Variables de entorno requeridas no configuradas: {missing}")
            print("   Configura estas variables en tu archivo .env")
            sys.exit(1)
        
        # Verificar que al menos un proveedor LLM esté configurado
        if not os.getenv('DEEPSEEK_API_KEY') and not os.getenv('ANTHROPIC_API_KEY'):
            print("❌ ERROR: Debes configurar al menos DEEPSEEK_API_KEY o ANTHROPIC_API_KEY")
            sys.exit(1)
        
        print("✅ Configuración de entorno validada correctamente")
        
        # Mostrar configuración actual (sin valores sensibles)
        provider = os.getenv('LLM_PROVIDER', 'auto')
        print(f"   🔧 Proveedor LLM: {provider}")
        print(f"   📊 Nivel de log: {os.getenv('LOG_LEVEL', 'INFO')}")

# Uso en main.py - agregar al inicio
from config.env_validator import EnvValidator
EnvValidator.validate()