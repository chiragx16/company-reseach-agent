import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ============================================
# MODEL CONFIGURATIONS
# All available models with their settings
# ============================================
MODELS_CONFIG = {
    "gemini": {
        "enabled": True,
        "provider": "google",
        "model_name": "gemini-3-flash-preview",
        "temperature": 0,
    },
    "openai": {
        "enabled": False,
        "provider": "openai",
        "model_name": "gpt-4",
        "temperature": 0,
    },
    "cohere": {
        "enabled": True,
        "provider": "cohere",
        "model_name": "command-a-03-2025",
        "temperature": 0,
    },
    "mistral": {
        "enabled": False,
        "provider": "mistral",
        "model_name": "mistral-large-latest",
        "temperature": 0,
    },
    "groq": {
        "enabled": True,
        "provider": "groq",
        "model_name": "llama-3.3-70b-versatile",
        "temperature": 0,
    },
}

# ============================================
# PIPELINE STAGE CONFIGURATION
# CUSTOMIZE THIS TO CHANGE WHICH MODEL RUNS EACH STAGE
# ============================================
# Format: "provider" or "provider:model_name"
# Examples:
#   "gemini" - uses default gemini model from MODELS_CONFIG
#   "groq:llama-3.3-70b-versatile" - uses specific Groq model
#   "groq:openai/gpt-oss-120b" - uses different Groq model
#   "cohere:command-a-03-2025" - uses specific Cohere model
# ============================================
STAGE_MODELS = {
    "stage_1_gather_details": "gemini",                            # Uses: gemini-3-flash-preview
    "stage_2_generate_questions": "groq:llama-3.3-70b-versatile",  # Uses: llama-3.3-70b-versatile
    "stage_3_answer_questions": "groq:openai/gpt-oss-120b",         # Uses: openai/gpt-oss-120b
    "stage_4_score_results": "cohere",                             # Uses: command-a-03-2025
}

# Output settings
OUTPUT_DIR = "output"
MARKDOWN_FORMAT = True

# Logging
LOG_LEVEL = "INFO"
