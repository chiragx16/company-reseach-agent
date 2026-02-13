"""
Model initialization for all AI providers.
Supports: Google Gemini, OpenAI, Cohere, Mistral, and Groq.
"""

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

try:
    from langchain_cohere import ChatCohere
except ImportError:
    ChatCohere = None

try:
    from langchain_mistralai import ChatMistralAI
except ImportError:
    ChatMistralAI = None

try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None

from config.settings import MODELS_CONFIG


def get_model_by_spec(model_spec):
    """
    Get or create a model based on specification.
    
    Args:
        model_spec: "provider" or "provider:model_name"
                   e.g., "gemini" or "groq:llama-3.3-70b-versatile"
    
    Returns:
        Model instance or None if failed
    """
    if not model_spec:
        return None
    
    # Parse model spec
    if ":" in model_spec:
        provider, model_name = model_spec.split(":", 1)
    else:
        provider = model_spec
        model_name = None
    
    # If no specific model name provided, use default from config
    if not model_name:
        if provider not in MODELS_CONFIG:
            print(f"!! Provider '{provider}' not found in MODELS_CONFIG")
            return None
        if not MODELS_CONFIG[provider].get("enabled"):
            print(f"!! Provider '{provider}' is not enabled")
            return None
        model_name = MODELS_CONFIG[provider]["model_name"]
    
    # Create model based on provider
    try:
        if provider == "gemini" and ChatGoogleGenerativeAI:
            temp = MODELS_CONFIG.get(provider, {}).get("temperature", 0)
            return ChatGoogleGenerativeAI(model=model_name, temperature=temp)
        
        elif provider == "openai" and ChatOpenAI:
            temp = MODELS_CONFIG.get(provider, {}).get("temperature", 0)
            return ChatOpenAI(model=model_name, temperature=temp)
        
        elif provider == "cohere" and ChatCohere:
            temp = MODELS_CONFIG.get(provider, {}).get("temperature", 0)
            return ChatCohere(model=model_name, temperature=temp)
        
        elif provider == "mistral" and ChatMistralAI:
            temp = MODELS_CONFIG.get(provider, {}).get("temperature", 0)
            return ChatMistralAI(model=model_name, temperature=temp)
        
        elif provider == "groq" and ChatGroq:
            temp = MODELS_CONFIG.get(provider, {}).get("temperature", 0)
            return ChatGroq(model=model_name, temperature=temp)
        
        else:
            print(f"!! Provider '{provider}' not available or not installed")
            return None
    
    except Exception as e:
        print(f"!! Failed to initialize {provider}:{model_name} - {e}")
        return None


def get_models():
    """
    Initialize and return ALL available models based on configuration.
    Only initializes models that are enabled.
    Returns a dict with model_name as key and model instance as value.
    """
    models = {}
    
    # Google Gemini
    if MODELS_CONFIG.get("gemini", {}).get("enabled") and ChatGoogleGenerativeAI:
        try:
            models["gemini"] = ChatGoogleGenerativeAI(
                model=MODELS_CONFIG["gemini"]["model_name"],
                temperature=MODELS_CONFIG["gemini"]["temperature"],
            )
            # print(f"[ Gemini initialized: {MODELS_CONFIG['gemini']['model_name']} ]")
        except Exception as e:
            print(f"!! Gemini initialization failed: {e}")
    
    # OpenAI
    if MODELS_CONFIG.get("openai", {}).get("enabled") and ChatOpenAI:
        try:
            models["openai"] = ChatOpenAI(
                model=MODELS_CONFIG["openai"]["model_name"],
                temperature=MODELS_CONFIG["openai"]["temperature"],
            )
            # print(f"[ OpenAI initialized: {MODELS_CONFIG['openai']['model_name']} ]")
        except Exception as e:
            print(f"!! OpenAI initialization failed: {e}")
    
    # Cohere
    if MODELS_CONFIG.get("cohere", {}).get("enabled") and ChatCohere:
        try:
            models["cohere"] = ChatCohere(
                model=MODELS_CONFIG["cohere"]["model_name"],
                temperature=MODELS_CONFIG["cohere"]["temperature"],
            )
            # print(f"[ Cohere initialized: {MODELS_CONFIG['cohere']['model_name']} ]")
        except Exception as e:
            print(f"!! Cohere initialization failed: {e}")
    
    # Mistral
    if MODELS_CONFIG.get("mistral", {}).get("enabled") and ChatMistralAI:
        try:
            models["mistral"] = ChatMistralAI(
                model=MODELS_CONFIG["mistral"]["model_name"],
                temperature=MODELS_CONFIG["mistral"]["temperature"],
            )
            # print(f"[ Mistral initialized: {MODELS_CONFIG['mistral']['model_name']} ]")
        except Exception as e:
            print(f"!! Mistral initialization failed: {e}")
    
    # Groq
    if MODELS_CONFIG.get("groq", {}).get("enabled") and ChatGroq:
        try:
            models["groq"] = ChatGroq(
                model=MODELS_CONFIG["groq"]["model_name"],
                temperature=MODELS_CONFIG["groq"]["temperature"],
            )
            # print(f"[ Groq initialized: {MODELS_CONFIG['groq']['model_name']} ]")
        except Exception as e:
            print(f"!! Groq initialization failed: {e}")
    
    if not models:
        raise Exception("No models could be initialized. Please enable at least one model and check your API keys.")
    
    return models
