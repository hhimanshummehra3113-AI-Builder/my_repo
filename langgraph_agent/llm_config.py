"""
LLM Configuration - Ollama Integration
"""
from langchain_community.llms import Ollama
from typing import Optional


def get_ollama_llm(model: str = "llama2", temperature: float = 0.3) -> Optional[Ollama]:
    """
    Initialize Ollama LLM
    
    Args:
        model: Model name (llama2, mistral, neural-chat, etc.)
        temperature: Temperature for generation (0.0-1.0)
    
    Returns:
        Initialized Ollama LLM instance
    """
    try:
        return Ollama(
            model=model,
            base_url="http://localhost:11434",
            temperature=temperature,
            num_predict=500,  # Max tokens
        )
    except Exception as e:
        print(f"⚠ Warning: Could not initialize Ollama LLM: {e}")
        return None


def get_available_models() -> list:
    """Get list of available Ollama models"""
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [m["name"] for m in models]
    except Exception as e:
        print(f"Error fetching models: {e}")
    return []


# Initialize default LLM
try:
    llm = get_ollama_llm(model="llama2", temperature=0.3)
    if llm:
        print("✓ Ollama LLM initialized successfully")
except Exception as e:
    print(f"⚠ Warning: Could not initialize Ollama LLM: {e}")
    llm = None
