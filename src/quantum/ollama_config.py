"""
Configuration file for Ollama integration
"""

import os
from typing import Dict, Any

class OllamaConfig:
    """Configuration class for Ollama settings"""
    
    def __init__(self):
        # Default Ollama settings
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.default_model = os.getenv("OLLAMA_MODEL", "llama2:7b")
        self.default_temperature = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
        self.default_max_tokens = int(os.getenv("OLLAMA_MAX_TOKENS", "2000"))
        
        # Model-specific configurations
        self.model_configs = {
            "llama2:7b": {
                "temperature": 0.7,
                "max_tokens": 2000,
                "top_p": 0.9,
                "top_k": 40
            },
            "mistral:7b": {
                "temperature": 0.7,
                "max_tokens": 2000,
                "top_p": 0.9,
                "top_k": 40
            },
            "codellama:7b": {
                "temperature": 0.3,
                "max_tokens": 2000,
                "top_p": 0.9,
                "top_k": 40
            },
            "deepseek-r1:7b": {
                "temperature": 0.7,
                "max_tokens": 2000,
                "top_p": 0.9,
                "top_k": 40
            }
        }
    
    def get_model_config(self, model_name: str = None) -> Dict[str, Any]:
        """Get configuration for a specific model"""
        model = model_name or self.default_model
        return self.model_configs.get(model, self.model_configs["llama2:7b"])
    
    def get_available_models(self) -> list:
        """Get list of available models"""
        return list(self.model_configs.keys())
    
    def update_model_config(self, model_name: str, config: Dict[str, Any]):
        """Update configuration for a specific model"""
        self.model_configs[model_name] = config

# Global configuration instance
config = OllamaConfig() 