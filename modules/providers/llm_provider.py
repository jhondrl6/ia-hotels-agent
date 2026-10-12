# modules/providers/llm_provider.py

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

import requests

from abc import ABC, abstractmethod





def _ensure_text(value, provider_name):

    if not value:

        raise ValueError(f"{provider_name} response missing text content")

    if isinstance(value, str):

        return value

    raise TypeError(f"{provider_name} response text must be a string")



def _usage_a_dict(usage):
    """Normaliza el usage de ambos proveedores a un dict serializable en el recibo."""
    if usage is None:
        return None
    if isinstance(usage, dict):
        return usage
    volcado = getattr(usage, "model_dump", None)
    if callable(volcado):
        return volcado()
    return None



@dataclass
class ChatCompletionDetail:
    """Resultado de una llamada con los metadatos de serving que el recibo registra.

    Via aditiva (DEC-A3): chat_completion sigue devolviendo solo el texto.
    """

    text: str
    finish_reason: Optional[str] = None
    model_requested: Optional[str] = None
    model_served: Optional[str] = None
    usage: Optional[dict] = None
    provider_name: Optional[str] = None



class LLMProvider(ABC):

    @abstractmethod

    def chat_completion(self, prompt, model=None, max_tokens=1000, temperature=0.7):

        pass


    def chat_completion_detailed(self, prompt, model=None, max_tokens=1000, temperature=0.7):
        """Version con metadatos: un proveedor que no la sobrescribe no reporta serving."""
        return ChatCompletionDetail(
            text=self.chat_completion(prompt, model=model, max_tokens=max_tokens, temperature=temperature),
            model_requested=model,
            provider_name=self.get_provider_name(),
        )



    @abstractmethod

    def get_provider_name(self):

        pass



class AnthropicProvider(LLMProvider):

    def __init__(self, api_key):

        from anthropic import Anthropic

        self.client = Anthropic(api_key=api_key)

    

    def _request(self, prompt, model=None, max_tokens=1000, temperature=0.7):
        """Una sola definicion del viaje al servicio, compartida por las dos vias."""
        model_resuelta = model or "claude-sonnet-4-20250514"
        response = self.client.messages.create(
            model=model_resuelta,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return response, model_resuelta


    def chat_completion(self, prompt, model=None, max_tokens=1000, temperature=0.7):
        response, _ = self._request(prompt, model, max_tokens, temperature)
        content_list = getattr(response, "content", [])
        if not content_list:
            raise ValueError("Anthropic response missing content list")
        text = getattr(content_list[0], "text", None)
        return _ensure_text(text, "Anthropic")


    def chat_completion_detailed(self, prompt, model=None, max_tokens=1000, temperature=0.7):
        response, model_resuelta = self._request(prompt, model, max_tokens, temperature)
        content_list = getattr(response, "content", [])
        if not content_list:
            raise ValueError("Anthropic response missing content list")
        text = _ensure_text(getattr(content_list[0], "text", None), "Anthropic")
        return ChatCompletionDetail(
            text=text,
            finish_reason=getattr(response, "stop_reason", None),
            model_requested=model_resuelta,
            model_served=getattr(response, "model", None),
            usage=_usage_a_dict(getattr(response, "usage", None)),
            provider_name=self.get_provider_name(),
        )

    

    def get_provider_name(self):

        return "anthropic"



class DeepSeekProvider(LLMProvider):

    def __init__(self, api_key):

        self.api_key = api_key

        self.base_url = "https://api.deepseek.com/v1"

    

    def _post(self, prompt, model=None, max_tokens=1000, temperature=0.7):
        """Una sola definicion del viaje al servicio, compartida por las dos vias."""
        model_resuelta = model or "deepseek-chat"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model_resuelta,
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
        return result, message, model_resuelta


    def chat_completion(self, prompt, model=None, max_tokens=1000, temperature=0.7):
        _, message, _ = self._post(prompt, model, max_tokens, temperature)
        text = message.get("content")
        return _ensure_text(text, "DeepSeek")


    def chat_completion_detailed(self, prompt, model=None, max_tokens=1000, temperature=0.7):
        """Expone finish_reason: sin ella un recorte por max_tokens llega como JSON inválido."""
        result, message, model_resuelta = self._post(prompt, model, max_tokens, temperature)
        text = _ensure_text(message.get("content"), "DeepSeek")
        return ChatCompletionDetail(
            text=text,
            finish_reason=result["choices"][0].get("finish_reason"),
            model_requested=model_resuelta,
            model_served=result.get("model"),
            usage=_usage_a_dict(result.get("usage")),
            provider_name=self.get_provider_name(),
        )

    

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