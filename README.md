![Python](https://img.shields.io/badge/-Python-F7DF1E?style=flat-square&logo=python&logoColor=black)
![LangChain](https://img.shields.io/badge/-LangChain-3178C6?style=flat-square&logo=langchain&logoColor=white)
![Gemini](https://img.shields.io/badge/-Gemini-8E75FF?style=flat-square&logo=googlegemini&logoColor=white)	
![Cohere](https://img.shields.io/static/v1?style=flat-square&message=Cohere&color=339933&logo=cohere&logoColor=white&label=)
![Mistral](https://img.shields.io/badge/-Mistral-FD6F00?style=flat-square&logo=mistralai&logoColor=white)	
![Groq](https://img.shields.io/static/v1?style=flat-square&message=Groq&color=4285F4&logo=groq&logoColor=white&label=)	
![OpenAI](https://custom-icon-badges.demolab.com/badge/ChatGPT-0062D3?style=flat-square&logo=openai&logoColor=white)	
![LLAMA](https://img.shields.io/badge/-LLAMA-04100B?style=flat-square&logo=meta&logoColor=white)
# Company Audit Pipeline 🚀

A sophisticated 4-stage AI pipeline that orchestrates multiple LLMs to conduct comprehensive company analysis.

## Pipeline Architecture

```
Stage 1                    Stage 2                    Stage 3                    Stage 4
┌──────────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
│ Gather Company       │   │ Generate All         │   │ Answer All           │   │ Score & Evaluate     │
│ Details              │──>│ Possible Questions   │──>│ Questions            │──>│ Results              │
│                      │   │                      │   │                      │   │                      │
│ Uses:                │   │ Uses:                │   │ Uses:                │   │ Uses:                │
│ Default: Gemini      │   │ Default: Groq        │   │ Default: Groq        │   │ Default: Cohere      │
│ Choices: Any Model   │   │ Choices: Any Model   │   │ Choices: Any Model   │   │ Choices: Any Model   │
│                      │   │                      │   │                      │   │                      │
│ Output:              │   │ Output:              │   │ Output:              │   │ Output:              │
│ - Overview           │   │ - Questions JSON     │   │ - Q&A Pairs          │   │ - Scores (1-10)      │
│ - Services           │   │ - Categories         │   │ - Confidence         │   │ - Red Flags          │
│ - Competitors        │   │ - Metadata           │   │ - Metadata           │   │ - Assessment         │
└──────────────────────┘   └──────────────────────┘   └──────────────────────┘   └──────────────────────┘
```

## Pipeline Stages

### Stage 1: Gather Company Details
- **Default Model**: Gemini
- **Configurable**: Use any available model (Gemini, OpenAI, Cohere, Mistral, Groq)
- **Purpose**: Gather comprehensive information about the company
- **tasks**:
  - Company overview and background
  - Core services offered
  - Target industries
  - Strength and weaknesses
  - Market position

### Stage 2: Generate Questions
- **Default Model**: Groq `llama-3.3-70b-versatile`
- **Configurable**: Use any available model or different Groq models
- **Purpose**: Create exhaustive list of evaluation questions
- **Tasks**:
  - Generate realistic questions from stakeholder perspectives
  - Investor, Customer, Competitor, Regulator, Journalist, Employee, Analyst
  - Output as structured JSON

### Stage 3: Answer Questions
- **Default Model**: Groq `openai/gpt-oss-120b`
- **Configurable**: Use any available model or different Groq models
- **Purpose**: Provide comprehensive answers to all generated questions
- **Tasks**:
  - Answer each question thoroughly
  - Rate confidence level (High/Medium/Low)
  - State unknowns clearly
  - Output as Q&A pairs with metadata

### Stage 4: Score & Evaluate
- **Default Model**: Cohere `command-a-03-2025`
- **Configurable**: Use any available model
- **Purpose**: Analyze, score, and evaluate the company
- **Tasks**:
  - Rate answer quality (1-10)
  - Score company credibility
  - Identify red flags and strengths
  - Output comprehensive scoring JSON

## Installation & Setup

### Prerequisites
```bash
pip install langchain 
pip install langchain-core 
pip install langchain-google-genai        # For Gemini
pip install langchain-openai              # For OpenAI
pip install langchain-cohere              # For Cohere  
pip install langchain-mistralai           # For Mistral 
pip install langchain-groq                # For Groq
pip install python-dotenv                 # For environment variables
```

### Environment Variables
Create a `.env` file in the project root:
```env
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
COHERE_API_KEY=your_cohere_api_key
MISTRAL_API_KEY=your_mistral_api_key   
GROQ_API_KEY=your_groq_api_key
```

## Quick Configuration

**See `config/README.md` for complete documentation on model setup and customization.**

Edit `config/settings.py` to choose models for each stage:

```python
STAGE_MODELS = {
    "stage_1_gather_details": "gemini",                    # Use default Gemini
    "stage_2_generate_questions": "groq:llama-3.3-70b-versatile",
    "stage_3_answer_questions": "groq:openai/gpt-oss-120b", # Different Groq model!
    "stage_4_score_results": "cohere",                     # Use default Cohere
}
```

### Format Options:
- `"gemini"` - Uses configured default (Gemini 3 Flash)
- `"groq:llama-3.3-70b-versatile"` - Uses specific Groq model
- `"cohere:command-r-plus-2024"` - Uses specific Cohere model

## Usage

### Basic Usage with run_pipeline.py (Recommended)

```bash
python run_pipeline.py
```

The script will:
1. Initialize the pipeline
2. Run all 4 stages
3. Display results summary
4. Save to `output/pipeline_results_YYYYMMDD_HHMMSS.json`


## Future Enhancements

- [ ] Add Company domain to crawl basic pages(home, about-us, career, achievement, etc.) to extract info.
- [ ] Add caching to avoid re-running stages
- [ ] Batch analysis of multiple companies
- [ ] Generate human-readable markdown report
- [ ] Add visualization dashboard so user can run and edit output of each stage
- [ ] Export to Excel/PDF reports
