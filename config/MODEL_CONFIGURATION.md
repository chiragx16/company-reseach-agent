# Pipeline Model Configuration Guide

This pipeline supports flexible model assignment for each stage. You can choose any supported model (Gemini, OpenAI, Cohere, Mistral, or Groq) for any stage without changing the code. You can even use **different models from the same provider**.

## Quick Start

1. **Edit `config/settings.py`**
2. **Modify the `STAGE_MODELS` dictionary** to assign models to stages
3. **Run the pipeline** - it will automatically use your configured models

## Configuration File Location

`config/settings.py` - Look for the `STAGE_MODELS` dictionary:

```python
STAGE_MODELS = {
    "stage_1_gather_details": "gemini",                            # Options: provider or provider:model
    "stage_2_generate_questions": "groq:llama-3.3-70b-versatile",  # Examples shown below
    "stage_3_answer_questions": "groq:openai/gpt-oss-120b",         
    "stage_4_score_results": "cohere",           
}
```

## Format

Two formats supported:

1. **Provider only** (uses configured default):
   ```python
   "stage_1_gather_details": "gemini"
   ```
   Uses: `gemini-3-flash-preview` (from MODELS_CONFIG)

2. **Provider with specific model**:
   ```python
   "stage_2_generate_questions": "groq:llama-3.3-70b-versatile"
   ```
   Uses: `llama-3.3-70b-versatile` on Groq

## Available Models

All models can be used for any stage with any provider:

- **Gemini** - Google's Gemini model
- **OpenAI** - OpenAI's GPT models
- **Cohere** - Cohere's command models
- **Mistral** - Mistral AI models
- **Groq** - Groq's fast inference models

## Enable/Disable Models

To enable or disable a model, edit the `MODELS_CONFIG` dictionary in `config/settings.py`:

```python
MODELS_CONFIG = {
    "gemini": {
        "enabled": True,              # Set to False to disable
        "provider": "google",
        "model_name": "gemini-3-flash-preview",
        "temperature": 0,
    },
    "openai": {
        "enabled": False,             # Set to True to enable
        "provider": "openai",
        "model_name": "gpt-4",
        "temperature": 0,
    },
    # ... other models
}
```

## Configuration Examples

### Example 1: Different Groq Models for Each Stage
```python
STAGE_MODELS = {
    "stage_1_gather_details": "gemini",
    "stage_2_generate_questions": "groq:llama-3.3-70b-versatile",
    "stage_3_answer_questions": "groq:openai/gpt-oss-120b",
    "stage_4_score_results": "groq:qwen/qwen3-32b",
}
```

### Example 2: Multiple Cohere Models
```python
STAGE_MODELS = {
    "stage_1_gather_details": "cohere:command-r-plus-2024",
    "stage_2_generate_questions": "cohere:command-a-03-2025",
    "stage_3_answer_questions": "cohere:command-light-2024",
    "stage_4_score_results": "cohere",  # uses command-a-03-2025 (default)
}
```

### Example 3: Different Mistral Models
```python
STAGE_MODELS = {
    "stage_1_gather_details": "mistral:mistral-large-latest",
    "stage_2_generate_questions": "mistral:mistral-medium-latest",
    "stage_3_answer_questions": "mistral:mistral-small-latest",
    "stage_4_score_results": "mistral:open-mistral-7b",
}
```

### Example 4: All Same Provider, All Gemini
```python
STAGE_MODELS = {
    "stage_1_gather_details": "gemini",
    "stage_2_generate_questions": "gemini",
    "stage_3_answer_questions": "gemini",
    "stage_4_score_results": "gemini",
}
```

### Example 5: Mixed Providers and Models
```python
STAGE_MODELS = {
    "stage_1_gather_details": "openai:gpt-4",
    "stage_2_generate_questions": "cohere:command-r-plus-2024",
    "stage_3_answer_questions": "mistral:mistral-large-latest",
    "stage_4_score_results": "groq:llama-3.3-70b-versatile",
}
```

## Use Cases

### Cost Optimization
Use cheaper models for simple tasks, expensive models for complex ones:
```python
STAGE_MODELS = {
    "stage_1_gather_details": "groq:llama-3.3-70b-versatile",     # Fast & cheap
    "stage_2_generate_questions": "openai:gpt-4",                  # Most capable
    "stage_3_answer_questions": "groq:openai/gpt-oss-120b",        # Balanced
    "stage_4_score_results": "cohere:command-a-03-2025",           # Good scoring
}
```

### Model Comparison / A/B Testing
Compare different models on the same task:
```python
# Run 1: With Groq
"stage_3_answer_questions": "groq:llama-3.3-70b-versatile"

# Run 2: With Mistral
"stage_3_answer_questions": "mistral:mistral-large-latest"

# Run 3: With OpenAI
"stage_3_answer_questions": "openai:gpt-4"
```

### Fallback Strategy
Have backups ready (by changing one line):
```python
# Primary setup
"stage_2_generate_questions": "groq:llama-3.3-70b-versatile"

# If Groq is down, just change to:
"stage_2_generate_questions": "openai:gpt-4"
```

## Model Customization

You can also modify the model names and parameters in `MODELS_CONFIG`:

```python
MODELS_CONFIG = {
    "groq": {
        "enabled": True,
        "provider": "groq",
        "model_name": "mixtral-8x7b-32768",    # Change default Groq model
        "temperature": 0.5,                    # Adjust temperature
    },
}
```

## Verification

When you run the pipeline, you'll see confirmation output:

```
✓ Pipeline initialized with 4 providers
  Available: gemini, cohere, groq, mistral

✓ Configured Stage Models:
  Stage 1 (Gather Details):      gemini
  Stage 2 (Generate Questions):  groq:llama-3.3-70b-versatile
  Stage 3 (Answer Questions):    groq:openai/gpt-oss-120b
  Stage 4 (Score Results):       cohere
```

This confirms your configuration is correct before the pipeline runs.

## API Keys Required

Make sure you have the API keys for enabled models in your `.env` file:

```
GOOGLE_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
COHERE_API_KEY=your_cohere_key
MISTRAL_API_KEY=your_mistral_key
GROQ_API_KEY=your_groq_key
```

## Troubleshooting

**Error: "Configured model 'xxx:yyy' not available"**
- Check that the provider name (before `:`) is correct
- Check that the provider is set to `"enabled": True` in `MODELS_CONFIG`
- Check that the required API key is in your `.env` file
- Check Groq provider documentation for valid model names

**Error: "No models could be initialized"**
- At least one model must be enabled in `MODELS_CONFIG`
- Check your API keys in the `.env` file

