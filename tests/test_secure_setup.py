import pytest
import os
from unittest.mock import patch, MagicMock
from modules.utils.secure_config_manager import SecureConfigManager

# IA Hoteles Agent - Test de Onboarding Seguro (v2.11.0)

@pytest.fixture
def mock_keyring():
    with patch('keyring.get_password') as mock_get:
        with patch('keyring.set_password') as mock_set:
            with patch('keyring.delete_password') as mock_del:
                
                # Simulamos un almacén en memoria para el test
                vault = {}
                
                def _get(service, key):
                    return vault.get(f"{service}:{key}")
                    
                def _set(service, key, value):
                    vault[f"{service}:{key}"] = value
                    
                mock_get.side_effect = _get
                mock_set.side_effect = _set
                
                yield {"get": mock_get, "set": mock_set, "del": mock_del, "vault": vault}

def test_secure_config_manager_keychain_priority(mock_keyring):
    """Verifica que el keychain tiene prioridad sobre el entorno."""
    key_name = "TEST_API_KEY"
    secret_value = "keychain_secret"
    env_value = "env_secret"
    
    # Configuramos ambos
    mock_keyring["set"](SecureConfigManager.SERVICE_NAME, key_name, secret_value)
    
    with patch.dict(os.environ, {key_name: env_value}):
        retrieved = SecureConfigManager.get_key(key_name)
        assert retrieved == secret_value
        assert retrieved != env_value

def test_secure_config_manager_fallback_to_env(mock_keyring):
    """Verifica que si no hay keychain, busca en el entorno."""
    key_name = "ENV_ONLY_KEY"
    env_value = "env_secret"
    
    # Keychain vacío para esta clave
    with patch.dict(os.environ, {key_name: env_value}):
        retrieved = SecureConfigManager.get_key(key_name)
        assert retrieved == env_value

@patch('modules.utils.secure_config_manager.set_key')
@patch('modules.utils.secure_config_manager.Path.touch')
def test_secure_config_manager_set_env_fallback(mock_touch, mock_set_key, mock_keyring):
    """Verifica el guardado en .env cuando se desactiva keychain."""
    key_name = "LOCAL_KEY"
    value = "local_secret"
    
    success, location = SecureConfigManager.set_key_secure(key_name, value, use_keychain=False)
    
    assert success is True
    assert location == ".env"
    mock_set_key.assert_called_once()

def test_setup_integration_logic():
    """Valida la lógica de inicialización del ProviderAdapter con el nuevo manager."""
    from modules.providers.llm_provider import ProviderAdapter
    
    with patch.object(SecureConfigManager, 'get_key') as mock_get:
        # Simulamos que encuentra la clave en el manager
        mock_get.side_effect = lambda k: "sk-test-123" if "KEY" in k else "deepseek"
        
        adapter = ProviderAdapter(provider_type="deepseek")
        assert adapter.current_provider == "deepseek"
        mock_get.assert_any_call("DEEPSEEK_API_KEY")
