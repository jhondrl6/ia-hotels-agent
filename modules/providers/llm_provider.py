# modules/providers/llm_provider.py

import os
from dotenv import load_dotenv

import requests

from abc import ABC, abstractmethod





def _ensure_text(value, provider_name):

    if not value:

        raise ValueError(f"{provider_name} response missing text content")

    if isinstance(value, str):

        return value

    raise TypeError(f"{provider_name} response text must be a string")



class LLMProvider(ABC):

    @abstractmethod

    def chat_completion(self, prompt, model=None, max_tokens=1000, temperature=0.7):

        pass



    @abstractmethod

    def get_provider_name(self):

        pass



class AnthropicProvider(LLMProvider):

    def __init__(self, api_key):

        from anthropic import Anthropic

        self.client = Anthropic(api_key=api_key)

    

    def chat_completion(self, prompt, model=None, max_tokens=1000, temperature=0.7):

        model = model or "claude-sonnet-4-20250514"

        response = self.client.messages.create(

            model=model,

            max_tokens=max_tokens,

            temperature=temperature,

            messages=[{"role": "user", "content": prompt}]

        )

        content_list = getattr(response, "content", [])

        if not content_list:

            raise ValueError("Anthropic response missing content list")

        text = getattr(content_list[0], "text", None)

        return _ensure_text(text, "Anthropic")

    

    def get_provider_name(self):

        return "anthropic"



class DeepSeekProvider(LLMProvider):

    def __init__(self, api_key):

        self.api_key = api_key

        self.base_url = "https://api.deepseek.com/v1"

    

    def chat_completion(self, prompt, model=None, max_tokens=1000, temperature=0.7):

        model = model or "deepseek-chat"

        headers = {

            "Authorization": f"Bearer {self.api_key}",

            "Content-Type": "application/json"

        }

        data = {

            "model": model,

            "messages": [{"role": "user", "content": prompt}],

            "max_tokens": max_tokens,

            "temperature": temperature,

            "stream": False

        }

        

        response = requests.post(

            f"{self.base_url}/chat/completions",

            headers=headers,

            json=data,

            timeout=60

        )

        response.raise_for_status()

        result = response.json()

        choices = result.get("choices")

        if not choices:

            raise ValueError("DeepSeek response missing choices")

        first_choice = choices[0]

        if not isinstance(first_choice, dict):

            raise TypeError("DeepSeek response choice must be a dict")

        message = first_choice.get("message")

        if not isinstance(message, dict):

            raise TypeError("DeepSeek response missing message dict")

        text = message.get("content")

        return _ensure_text(text, "DeepSeek")

    

    def get_provider_name(self):

        return "deepseek"



class ProviderAdapter:
    def __init__(self, provider_type=None):
        from modules.utils.secure_config_manager import SecureConfigManager
        self.config_manager = SecureConfigManager()
        self.provider = self._initialize_provider(provider_type)
        self.current_provider = self.provider.get_provider_name()
    
    def _initialize_provider(self, provider_type=None):
        # Preferencia: .env/Keychain via SecureConfigManager
        provider_type = provider_type or self.config_manager.get_key('LLM_PROVIDER') or 'auto'
        deepseek_key = self.config_manager.get_key('DEEPSEEK_API_KEY')
        anthropic_key = self.config_manager.get_key('ANTHROPIC_API_KEY')
        
        if provider_type == "deepseek" and deepseek_key:
            print("[INFO] Using DeepSeek as LLM provider")
            return DeepSeekProvider(deepseek_key)
        elif provider_type == "anthropic" and anthropic_key:
            print("[INFO] Using Anthropic as LLM provider")
            return AnthropicProvider(anthropic_key)
        elif deepseek_key:  # auto mode, prefer DeepSeek
            print("[INFO] Using DeepSeek (auto) as LLM provider")
            return DeepSeekProvider(deepseek_key)
        elif anthropic_key:
            print("[INFO] Using Anthropic (fallback) as LLM provider")
            return AnthropicProvider(anthropic_key)
        else:
            raise ValueError("No LLM API key configured. Run 'python main.py setup' to configure.")

    

    def unified_request(self, prompt, **kwargs):

        return self.provider.chat_completion(prompt, **kwargs)

    

    def switch_provider(self, provider_type):

        """Permite cambiar proveedor en tiempo de ejecucion"""

        self.provider = self._initialize_provider(provider_type)

        self.current_provider = self.provider.get_provider_name()

        return self.current_provider

    

    def get_current_provider(self):

        return self.current_provider