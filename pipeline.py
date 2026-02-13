import os
import json
import time
from datetime import datetime
from config.models import get_models, get_model_by_spec
from config.settings import STAGE_MODELS
from langchain_core.messages import HumanMessage

def extract_text_content(content):
    """Extract pure text content from different response formats."""
    if isinstance(content, str):
        return content
    
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                if 'text' in item:
                    text_parts.append(item['text'])
                elif 'content' in item:
                    text_parts.append(item['content'])
            elif isinstance(item, str):
                text_parts.append(item)
        return '\n'.join(text_parts) if text_parts else str(content)
    
    if isinstance(content, dict):
        if 'text' in content:
            return content['text']
        elif 'content' in content:
            return content['content']
    
    return str(content)


def clean_json_string(json_str):
    """
    Remove markdown code block markers from JSON strings.
    Handles: ```json ... ``` and other variations.
    """
    if not isinstance(json_str, str):
        return json_str
    
    # Remove markdown code block markers
    json_str = json_str.strip()
    
    # Remove opening backticks and language identifier
    if json_str.startswith('```json'):
        json_str = json_str[7:]  # Remove '```json'
    elif json_str.startswith('```'):
        json_str = json_str[3:]  # Remove '```'
    
    # Remove closing backticks
    if json_str.endswith('```'):
        json_str = json_str[:-3]
    
    return json_str.strip()


def try_parse_json(json_str, stage_name=""):
    """
    Try multiple strategies to parse JSON string.
    Returns: parsed JSON object if successful, otherwise falls back to original string.
    """
    if isinstance(json_str, dict):
        return json_str
    
    if not isinstance(json_str, str):
        return json_str
    
    original_str = json_str
    
    # Strategy 1: Direct parse (may succeed if already clean)
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Clean markdown code blocks and retry
    cleaned = clean_json_string(json_str)
    if cleaned != json_str:
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
    
    # Strategy 3: Find and extract JSON block (handles extra text around JSON)
    try:
        first_brace = cleaned.find('{')
        last_brace = cleaned.rfind('}')
        
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            extracted = cleaned[first_brace:last_brace + 1]
            return json.loads(extracted)
    except (json.JSONDecodeError, ValueError):
        pass
    
    # Strategy 4: Find first '[' and try to extract array
    try:
        first_bracket = cleaned.find('[')
        last_bracket = cleaned.rfind(']')
        
        if first_bracket != -1 and last_bracket != -1 and last_bracket > first_bracket:
            extracted = cleaned[first_bracket:last_bracket + 1]
            return json.loads(extracted)
    except (json.JSONDecodeError, ValueError):
        pass
    
    # Strategy 5: Try to parse line by line and reconstruct
    try:
        lines = cleaned.split('\n')
        json_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
        json_str_reconstructed = '\n'.join(json_lines)
        return json.loads(json_str_reconstructed)
    except (json.JSONDecodeError, ValueError):
        pass
    
    # Strategy 6: Last resort - ensure we return a valid JSON object/array
    # Try to extract any valid JSON structures and wrap in an object
    try:
        # Try to find balanced braces or brackets
        for start_idx in range(len(cleaned)):
            for end_idx in range(start_idx + 1, len(cleaned) + 1):
                try:
                    result = json.loads(cleaned[start_idx:end_idx])
                    if isinstance(result, (dict, list)):
                        return result
                except (json.JSONDecodeError, ValueError):
                    continue
    except Exception:
        pass
    
    # All strategies failed, return original string
    return original_str


def invoke_model_with_retry(model, prompt, model_name="Model", max_retries=3, initial_wait=2):
    """
    Invoke a model with retry logic and timeout handling.
    
    Args:
        model: The LangChain model to invoke
        prompt: The prompt to send to the model
        model_name: Name of the model for logging
        max_retries: Maximum number of retry attempts
        initial_wait: Initial wait time in seconds before retry
    
    Returns:
        Model response or None if all retries failed
    """
    for attempt in range(max_retries):
        try:
            print(f"  [{model_name}] Attempt {attempt + 1}/{max_retries}...")
            response = model.invoke([HumanMessage(content=prompt)])
            print(f"  {model_name} responded successfully")
            return response
        except Exception as e:
            error_msg = str(e)
            print(f"  !! {model_name} error (Attempt {attempt + 1}): {error_msg[:100]}")
            
            if attempt < max_retries - 1:
                wait_time = initial_wait * (2 ** attempt)  # Exponential backoff
                print(f"  Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"  {model_name} failed after {max_retries} attempts")
                return None
    
    return None


class CompanyAuditPipeline:
    def __init__(self, company_name="Open AI"):
        """Initialize the pipeline with a company name."""
        self.company_name = company_name
        self.models = get_models()
        self.stage_results = {}
        
        # Get configured model specifications for each stage
        self.stage_1_spec = STAGE_MODELS.get("stage_1_gather_details", "gemini")
        self.stage_2_spec = STAGE_MODELS.get("stage_2_generate_questions", "groq")
        self.stage_3_spec = STAGE_MODELS.get("stage_3_answer_questions", "groq")
        self.stage_4_spec = STAGE_MODELS.get("stage_4_score_results", "cohere")
        
        # Get actual model instances for each stage
        self.stage_1_model = get_model_by_spec(self.stage_1_spec)
        self.stage_2_model = get_model_by_spec(self.stage_2_spec)
        self.stage_3_model = get_model_by_spec(self.stage_3_spec)
        self.stage_4_model = get_model_by_spec(self.stage_4_spec)
        
        # Validate all models are available
        if not all([self.stage_1_model, self.stage_2_model, self.stage_3_model, self.stage_4_model]):
            print("\n!! Error: Not all configured models could be initialized")
            print("  Check your STAGE_MODELS configuration and API keys")
            raise Exception("Model initialization failed")
        
        print(f"^ Pipeline initialized with {len(self.models)} available providers")
        print(f"  Available: {', '.join(self.models.keys())}")
        print(f"\n^ Configured Stage Models:")
        print(f"  Stage 1 (Gather Details):      {self.stage_1_spec}")
        print(f"  Stage 2 (Generate Questions):  {self.stage_2_spec}")
        print(f"  Stage 3 (Answer Questions):    {self.stage_3_spec}")
        print(f"  Stage 4 (Score Results):       {self.stage_4_spec}")
    
    def stage_1_company_details(self):
        """
        Stage 1: Gather company details using configured model
        """
        print("\n" + "-"*80)
        print(f"STAGE 1: {self.stage_1_spec} - Getting Company Details")
        print("-"*80)
        
        if self.stage_1_model is None:
            print(f"Configured model '{self.stage_1_spec}' is not available")
            return None
        
        prompt = f"""Role: You are a prospective evaluator of firms for a digital transformation project. You’ve shortlisted {self.company_name} and need unbiased, detailed, and actionable information to decide.
 
Prioritize clarity, specificity, and decision-useful insights (e.g., differentiators, risks, industry fit). Use bullet points, tables, or concise paragraphs where helpful.

STRICT INSTRUCTION: do not include emojis or json in the response

Provide detailed information under the following sections:

What is {self.company_name}?
Tell me about {self.company_name}
What does {self.company_name} do?
List the key services offered by {self.company_name}
Who are the main competitors of {self.company_name}
Compare {self.company_name} with its competitors
How large is {self.company_name} as a company?
What industries does {self.company_name} primarily serve
What are {self.company_name}'s strengths and weaknesses?
Summarize online sentiment about {self.company_name}
What are the reported strengths and weaknesses of {self.company_name}'s service
How is {self.company_name} positioned compared to other top competitors in 2026
Why should I choose {self.company_name}?
Why should I NOT choose {self.company_name}?
Tell me about leadership team members of {self.company_name} and their roles
How is Life/Environment at {self.company_name}?
Are their any partner or sponsers of {self.company_name}?
Who are the notable customers of {self.company_name}?
Mention any awards or achievement if they have?
Give Employee perception of {self.company_name}

Provide thorough, factual, and comprehensive information for each section."""
        
        try:
            response = invoke_model_with_retry(
                self.stage_1_model,
                prompt,
                model_name=self.stage_1_spec,
                max_retries=3,
                initial_wait=2
            )
            
            if response is None:
                print(f"{self.stage_1_spec} failed to respond after retries")
                return None
            
            details = extract_text_content(response.content)
            self.stage_results["company_details"] = details
            
            print(f"Received company details ({len(details)} characters)")
            return details
        except Exception as e:
            print(f"Error in Stage 1: {e}")
            return None
    
    def stage_2_generate_questions(self, company_details):
        """
        Stage 2: Generate questions using configured model
        """
        print("\n" + "-"*80)
        print(f"STAGE 2: {self.stage_2_spec} - Generating All Possible Questions")
        print("-"*80)
        
        if self.stage_2_model is None:
            print(f"Configured model '{self.stage_2_spec}' is not available")
            return None
        
        if not company_details:
            print("No company details provided")
            return None
        
        prompt = f"""You are simulating real human curiosity.

Based on the company profile below:

{company_details}

Generate realistic questions that real people would naturally ask in real-life situations.

Important constraints:
- Questions must sound natural and conversational.
- Avoid academic, overly technical, or MBA-style language.
- Do not assume access to internal financial metrics unless publicly obvious.
- Keep questions grounded in what a person could realistically know or care about.
- Limit to 5–7 strong, natural questions per stakeholder.

1. Investor
2. Customer
3. Competitor
4. Regulator
5. Journalist
6. Potential Employee
7. Industry Analyst

Focus on:
- Practical concerns
- Reputation
- Growth
- Stability
- Trust
- Personal impact

Return output strictly in structured JSON format like:
```json
{{
  "investor_questions": [],
  "customer_questions": [],
  "competitor_questions": [],
  "regulator_questions": [],
  "journalist_questions": [],
  "employee_questions": [],
  "analyst_questions": []
}}
```
"""
        
        try:
            response = invoke_model_with_retry(
                self.stage_2_model,
                prompt,
                model_name=self.stage_2_spec,
                max_retries=3,
                initial_wait=2
            )
            
            if response is None:
                print(f"{self.stage_2_spec} failed to respond after retries")
                return None
            
            questions_text = extract_text_content(response.content)
            
            # Parse JSON with multiple strategies
            questions_json = try_parse_json(questions_text, f"Stage 2 - {self.stage_2_spec} Questions")
            self.stage_results["questions"] = questions_json
            
            # Count total questions from stakeholder perspectives
            if isinstance(questions_json, dict):
                total = sum(len(v) for v in questions_json.values() if isinstance(v, list))
                stakeholders = [k for k in questions_json.keys() if k.endswith('_questions')]
                print(f"Generated {total} questions from {len(stakeholders)} stakeholder perspectives")
                print(f"  Stakeholders: {', '.join([s.replace('_questions', '') for s in stakeholders])}")
            else:
                print(f"Generated questions ({len(str(questions_json))} characters)")
            
            return self.stage_results["questions"]
        except Exception as e:
            print(f"Error in Stage 2: {e}")
            return None
    
    def stage_3_answer_questions(self, company_details, questions):
        """
        Stage 3: Answer questions using configured model
        """
        print("\n" + "-"*80)
        print(f"STAGE 3: {self.stage_3_spec} - Answering All Questions")
        print("-"*80)
        
        if self.stage_3_model is None:
            print(f"Configured model '{self.stage_3_spec}' is not available")
            return None
        
        if not questions or not company_details:
            print("Missing company details or questions")
            return None
        
        # Format questions for the prompt
        if isinstance(questions, dict):
            questions_text = json.dumps(questions, indent=2)
        else:
            questions_text = str(questions)
        
        prompt = f"""
You are a seasoned business analyst with extensive experience in evaluating companies. Your task is to respond to a structured interrogation about a company based on the provided information. 
Your answers should be thorough, objective, and professional, yet written in a natural, human-like tone.

**Given:**

1. **Company Profile:**  
   {company_details}  

2. **Stakeholder Questions:**  
   {questions_text}  

**Task:**

Answer ALL questions in a way that mimics human analysis. Ensure responses are detailed, objective, and based solely on the provided information. 
If data is missing, clearly state this without speculation.

**Rules:**

- Base answers ONLY on the provided company profile.  
- Do not invent new facts.  
- If information is missing, state: "Insufficient information in provided profile."  
- Use a professional yet conversational tone.  
- Avoid overly robotic or formulaic language.  
- If making an inference, clearly mark it as such (e.g., "Based on the available data, it can be inferred that...").  

**For each answer, include:**

- **"answer"**: Detailed, human-like response.  
- **"confidence"**: High / Medium / Low  
- **"risk_flag"**: None / Low / Medium / High  
- **"sentiment"**: Positive / Neutral / Negative  
- **"reasoning_summary"**: 1–2 sentence explanation of how you derived the answer.  

**Output Format:**

```json
{{
  "responses": [
    {{
      "stakeholder": "",
      "question": "",
      "answer": "",
      "confidence": "",
      "risk_flag": "",
      "sentiment": "",
      "reasoning_summary": ""
    }}
  ]
}}
```

Additional Guidance:

Use transitional phrases and varied sentence structures to make responses flow naturally.
Avoid repetitive phrasing or overly technical jargon unless necessary.
When stating "Insufficient information," follow it with a brief explanation of why the information is critical (e.g., "Insufficient information in provided profile to assess market share, which is crucial for understanding competitive positioning.").
Tailor the tone to match the context of the question (e.g., more cautious for risk-related questions, more optimistic for growth-related questions).

Example of a more human-like response:

Question: What is the company's current market share?
Answer: "Insufficient information in provided profile to determine the company's market share. This data is critical for assessing its competitive position and growth potential in the industry."
Confidence: Low
Risk_flag: Medium
Sentiment: Neutral
Reasoning_summary: The company profile does not include market share data, making it impossible to evaluate this aspect.
"""
        
        try:
            response = invoke_model_with_retry(
                self.stage_3_model, 
                prompt, 
                model_name=self.stage_3_spec,
                max_retries=3,
                initial_wait=3
            )
            
            if response is None:
                print(f"{self.stage_3_spec} failed to respond after retries")
                return None
            
            answers_text = extract_text_content(response.content)
            
            # Parse JSON with multiple strategies
            answers_json = try_parse_json(answers_text, f"Stage 3 - {self.stage_3_spec} Answers")
            self.stage_results["answers"] = answers_json
            
            if isinstance(answers_json, dict):
                total = len(answers_json.get("responses", []))
                print(f"Answered {total} questions with detailed metadata")
            else:
                print(f"Generated answers ({len(str(answers_json))} characters)")
            
            return self.stage_results["answers"]
        except Exception as e:
            print(f"Error in Stage 3: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def stage_4_score_results(self, questions, answers):
        """
        Stage 4: Score and evaluate results using configured model
        """
        print("\n" + "-"*80)
        print(f"STAGE 4: {self.stage_4_spec} - Scoring Results & Evaluation")
        print("-"*80)
        
        if self.stage_4_model is None:
            print(f"Configured model '{self.stage_4_spec}' is not available")
            return None
        
        if not answers:
            print("No answers to score")
            return None
        
        # Format answers for the prompt
        if isinstance(answers, dict):
            answers_text = json.dumps(answers, indent=2)
        else:
            answers_text = str(answers)
        
        if isinstance(questions, dict):
            questions_text = json.dumps(questions, indent=2)
        else:
            questions_text = str(questions)
        
        prompt = f"""You are an independent AI auditor.

You are given structured question-answer data about a company.

Your role is NOT to rewrite answers.
Your role is to evaluate and score them objectively.

Input:
{answers_text}

Your task:

For EACH response, evaluate:

1. Logical consistency (1–10)
2. Completeness (1–10)
3. Clarity (1–10)
4. Hallucination risk (Low / Medium / High)
5. Bias presence (None / Mild / Moderate / Strong)
6. Sentiment validation (Does the stated sentiment match the answer? Yes / No)
7. Risk exposure level (Low / Medium / High)

Additionally:
- Identify if the answer overstates certainty.
- Flag any speculative language.
- Detect internal contradictions.

Return strictly structured JSON in this format:
```json
{{
  "evaluation_results": [
    {{
      "stakeholder": "",
      "question": "",
      "scores": {{
        "logical_consistency": 0,
        "completeness": 0,
        "clarity": 0
      }},
      "hallucination_risk": "",
      "bias_level": "",
      "sentiment_alignment": "",
      "risk_exposure": "",
      "overconfidence_flag": true/false,
      "speculation_flag": true/false,
      "notes": ""
    }}
  ],
  "overall_summary": {{
    "average_logical_score": 0,
    "average_completeness_score": 0,
    "average_clarity_score": 0,
    "dominant_sentiment_trend": "",
    "overall_company_risk_signal": "",
    "model_behavior_observations": ""
  }}
}}
```
"""
        
        try:
            response = invoke_model_with_retry(
                self.stage_4_model,
                prompt,
                model_name=self.stage_4_spec,
                max_retries=3,
                initial_wait=2
            )
            
            if response is None:
                print(f"{self.stage_4_spec} failed to respond after retries")
                return None
            
            scores_text = extract_text_content(response.content)
            
            # Parse JSON with multiple strategies
            scores_json = try_parse_json(scores_text, f"Stage 4 - {self.stage_4_spec} Scores")
            self.stage_results["scores"] = scores_json
            
            if isinstance(scores_json, dict):
                if "overall_summary" in scores_json:
                    summary = scores_json["overall_summary"]
                    avg_logic = summary.get("average_logical_score", "N/A")
                    risk_signal = summary.get("overall_company_risk_signal", "N/A")
                    print(f"  Evaluation complete")
                    print(f"  Average Logical Consistency Score: {avg_logic}/10")
                    print(f"  Overall Risk Signal: {risk_signal}")
                else:
                    print(f" Evaluation complete")
            else:
                print(f" Evaluation complete ({len(str(scores_json))} characters)")
            
            return self.stage_results["scores"]
        except Exception as e:
            print(f"Error in Stage 4: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def run_full_pipeline(self):
        """Run the complete 4-stage pipeline."""
        print("\n" + "="*100)
        print(f"STARTING COMPLETE PIPELINE FOR: {self.company_name}".center(100))
        print("="*100)
        
        # Stage 1: Get company details
        company_details = self.stage_1_company_details()
        if not company_details:
            print("\nPipeline failed at Stage 1")
            return False
        
        # Stage 2: Generate questions
        questions = self.stage_2_generate_questions(company_details)
        if not questions:
            print("\nPipeline failed at Stage 2")
            return False
        
        # Stage 3: Answer questions
        answers = self.stage_3_answer_questions(company_details, questions)
        if not answers:
            print("\nPipeline failed at Stage 3")
            return False
        
        # Stage 4: Score results
        scores = self.stage_4_score_results(questions, answers)
        if not scores:
            print("\nPipeline failed at Stage 4")
            return False
        
        print("\n" + "="*100)
        print(" PIPELINE COMPLETED SUCCESSFULLY".center(100))
        print("="*100)
        
        return True
    
    def save_results(self, filename=None):
        """Save pipeline results to a file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pipeline_results_{timestamp}.json"
        
        try:
            if not os.path.exists("output"):
                os.makedirs("output")
                print("^ Created output directory")
            
            filepath = os.path.join("output", filename)
            
            # Prepare results for serialization - ensure JSON fields are properly parsed
            results_to_save = {}
            
            for key, value in self.stage_results.items():
                if isinstance(value, str):
                    # Try to parse JSON strings one more time
                    parsed = try_parse_json(value, key)
                    
                    # If still a string, wrap it as a string value in a dict for valid JSON
                    if isinstance(parsed, str):
                        results_to_save[key] = {"raw_content": parsed, "_note": "Failed to parse JSON, stored as string"}
                    else:
                        results_to_save[key] = parsed
                else:
                    results_to_save[key] = value
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results_to_save, f, indent=2, ensure_ascii=False)
            
            # Verify file was created
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                print(f"\n^ Results saved successfully!")
                print(f"  File: {filepath}")
                print(f"  Size: {file_size} bytes")
                return filepath
            else:
                print(f"!! File was not created at {filepath}")
                return None
        except Exception as e:
            print(f"\n!! Error saving results: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def print_summary(self):
        """Print a summary of pipeline results."""
        print("\n" + "="*80)
        print("PIPELINE RESULTS SUMMARY")
        print("="*80)
        
        if "company_details" in self.stage_results:
            print(f"\n[Stage 1 - Company Details]")
            print(f"  • Received {len(self.stage_results['company_details'])} characters of company information")
        
        if "questions" in self.stage_results:
            print(f"\n[Stage 2 - Generated Questions]")
            questions = self.stage_results["questions"]
            if isinstance(questions, dict):
                stakeholders = questions.keys()
                total_questions = sum(len(v) for v in questions.values() if isinstance(v, list))
                print(f"  • Stakeholder perspectives: {', '.join(stakeholders)}")
                print(f"  • Total questions generated: {total_questions}")
            else:
                print(f"  • Generated {len(str(questions))} characters of questions")
        
        if "answers" in self.stage_results:
            print(f"\n[Stage 3 - Answers]")
            answers = self.stage_results["answers"]
            if isinstance(answers, dict):
                responses = answers.get("responses", [])
                total = len(responses)
                
                # Count by sentiment
                sentiments = {}
                confidences = {}
                for resp in responses:
                    sentiment = resp.get("sentiment", "Unknown")
                    confidence = resp.get("confidence", "Unknown")
                    sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
                    confidences[confidence] = confidences.get(confidence, 0) + 1
                
                print(f"  • Total answers provided: {total}")
                print(f"  • Sentiment distribution: {sentiments}")
                print(f"  • Confidence levels: {confidences}")
            else:
                print(f"  • Generated {len(str(answers))} characters of answers")
        
        if "scores" in self.stage_results:
            print(f"\n[Stage 4 - Evaluation & Scores]")
            scores = self.stage_results["scores"]
            if isinstance(scores, dict):
                if "overall_summary" in scores:
                    summary = scores["overall_summary"]
                    print(f"  • Average Logical Consistency: {summary.get('average_logical_score', 'N/A')}/10")
                    print(f"  • Average Completeness: {summary.get('average_completeness_score', 'N/A')}/10")
                    print(f"  • Average Clarity: {summary.get('average_clarity_score', 'N/A')}/10")
                    print(f"  • Overall Risk Signal: {summary.get('overall_company_risk_signal', 'N/A')}")
                    print(f"  • Dominant Sentiment Trend: {summary.get('dominant_sentiment_trend', 'N/A')}")
        
        print("\n" + "="*80)


if __name__ == "__main__":
    # Run the pipeline
    pipeline = CompanyAuditPipeline(company_name="Open AI")
    
    # Execute all 4 stages
    success = pipeline.run_full_pipeline()
    
    if success:
        # Print summary
        pipeline.print_summary()
        
        # Save results
        pipeline.save_results()
    else:
        print("\nPipeline execution failed")
