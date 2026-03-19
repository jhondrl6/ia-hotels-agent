import os
import keyring
from dotenv import load_dotenv, set_key
from pathlib import Path

# IA Hoteles Agent - Secure Config Manager (v2.11.0)
# Prioriza Keychain (Sistema) > .env (Local) > Env Vars

class SecureConfigManager:
    SERVICE_NAME = "iah-cli"
    
    @staticmethod
    def get_key(key_name):
        """
        Obtiene una clave buscando en:
        1. Keychain (Sistema)
        2. Variables de entorno (incluyendo .env)
        """
        # 1. Intentar desde el Keychain del sistema
        try:
            stored_key = keyring.get_password(SecureConfigManager.SERVICE_NAME, key_name)
            if stored_key:
                return stored_key
        except Exception:
            pass # Fallback silencioso al entorno
            
        # 2. Intentar desde variables de entorno / .env
        load_dotenv()
        return os.getenv(key_name)

    @staticmethod
    def set_key_secure(key_name, value, use_keychain=True):
        """
        Guarda una clave de forma segura.
        Si use_keychain es True, usa el sistema de credenciales.
        Si no, usa el archivo .env local.
        """
        if use_keychain:
            try:
                keyring.set_password(SecureConfigManager.SERVICE_NAME, key_name, value)
                return True, "Keychain"
            except Exception as e:
                # Si falla el keychain, fallback forzado a .env
                pass

        # Fallback a .env
        env_path = Path('.env')
        if not env_path.exists():
            env_path.touch()
            
        set_key(str(env_path), key_name, value)
        return True, ".env"

    @staticmethod
    def delete_key(key_name):
        """Elimina una clave del sistema."""
        try:
            keyring.delete_password(SecureConfigManager.SERVICE_NAME, key_name)
        except Exception:
            pass
        
        # Opcionalmente se podría limpiar del .env, pero por ahora manejamos solo sistema
