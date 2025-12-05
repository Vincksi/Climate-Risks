from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from ollama import AsyncClient
import logging
import asyncio
from enum import Enum
from typing import List
import json

# --- Configuration and Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server")

app = FastAPI(title="Ollama Multi-Model Analysis Server")

# --- Predefined Analyst Roles (System Prompts) ---

class AnalystRole(str, Enum):
    """Enumeration of predefined analyst roles."""
    FINANCIAL_EXPERT = "FINANCIAL_EXPERT"
    RISK_ADVISOR = "RISK_ADVISOR"
    MARKETING_STRATEGIST = "MARKETING_STRATEGIST"
    SIMPLE_SUMMARY = "SIMPLE_SUMMARY"

SYSTEM_PROMPTS = {
    AnalystRole.FINANCIAL_EXPERT: (
        "You are an expert financial market analyst. Analyze the provided data "
        "using industry standards. Focus on valuation, profitability, and growth."
    ),
    AnalystRole.RISK_ADVISOR: (
        "You are a professional risk management advisor. Identify financial and "
        "operational risks in the data. Provide a clear assessment."
    ),
    AnalystRole.MARKETING_STRATEGIST: (
        "You are a market strategist. Infer market positioning, competitive landscape, "
        "and potential strategic moves based on the data."
    ),
    AnalystRole.SIMPLE_SUMMARY: (
        "Provide a simple, brief, non-technical summary of the data using bullet points."
    )
}

# --- Pydantic Models for Requests ---

class AnalysisRequest(BaseModel):
    models: List[str] = Field(
        default=["llama3"],
        description="List of Ollama models to query (e.g., ['tinyllama', 'llama3'])"
    )
    system_prompt: str = Field(
        description="System prompt used to configure the model's role"
    )
    row: List[dict] = Field(
        ..., 
        description="Structured business/company data (list of rows for multi-company comparison)"
    )
    question: str = Field(
        ..., 
        description="User question about the given data"
    )


# --- Utility: Clean Data for JSON Serialization ---
def clean_data_for_json(data):
    """
    Replace NaN, Infinity, and other non-JSON-compliant values with None.
    
    Args:
        data: List of dictionaries or single dictionary
        
    Returns:
        Cleaned data structure safe for JSON serialization
    """
    import math
    
    def clean_value(value):
        """Clean a single value."""
        if isinstance(value, float):
            if math.isnan(value) or math.isinf(value):
                return None
        return value
    
    def clean_dict(d):
        """Clean all values in a dictionary."""
        return {k: clean_value(v) for k, v in d.items()}
    
    if isinstance(data, list):
        return [clean_dict(item) if isinstance(item, dict) else item for item in data]
    elif isinstance(data, dict):
        return clean_dict(data)
    return data


# --- Utility: Normalize Ollama Model List Structure ---
def normalize_model_list(raw):
    """
    Ollama Python SDK sometimes returns:
    - a dict: {"models": [...]}
    - an object with .models
    This function unifies both formats and keeps the full model name with tag.
    """
    if isinstance(raw, dict):
        models = raw.get("models", [])
    elif hasattr(raw, "models"):
        models = raw.models
    else:
        logger.warning(f"Unexpected Ollama response type for model list: {type(raw)}")
        models = []

    normalized = []
    for m in models:
        # Keep the full name with tag (e.g., "phi3:mini", "llama3:latest")
        name = m.get("name") or m.get("model") or None
        if name:
            normalized.append(name)
    return normalized


# --- Utility: Call Ollama Chat (Single Model) ---
async def run_ollama_query(model_name: str, messages: list):
    """
    Execute a chat query on a single Ollama model.
    
    Args:
        model_name: Name of the Ollama model
        messages: List of message dictionaries for the chat
        
    Returns:
        Dictionary with model name, response, and status
    """
    try:
        # Use the model name as-is if it already contains a tag, otherwise don't add one
        # Ollama will use the default tag automatically
        full_model_name = model_name
        
        client = AsyncClient(host="http://localhost:11434")
        response = await client.chat(model=full_model_name, messages=messages)

        return {
            "model": model_name,
            "response": response["message"]["content"],
            "status": "success"
        }

    except Exception as e:
        logger.error(f"Ollama query failed for model '{model_name}': {e}")
        # Simplify error message for client readability
        error_msg = str(e).split('\n')[0].replace('httpx.ConnectError: ', '')
        return {
            "model": model_name,
            "response": None,
            "status": f"error: {error_msg}"
        }


# --- Health Check Endpoint ---
@app.get("/health")
async def health_check():
    """
    Check the health status of FastAPI and Ollama connection.
    
    Returns:
        Dictionary with status, connection info, and available models
    """
    try:
        client = AsyncClient(host="http://localhost:11434")
        raw = await client.list()

        available_models = normalize_model_list(raw)

        return {
            "status": "ok",
            "ollama_connection": "successful",
            "available_models": available_models
        }

    except Exception as e:
        logger.error(f"Ollama health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Ollama server unreachable on http://localhost:11434. Check if Ollama is running. Error: {str(e).split('\n')[0].replace('httpx.ConnectError: ', '')}"
        )


# --- Main Analysis Endpoint (Multi-Model) ---
@app.post("/analyze")
async def analyze_multiple(request: AnalysisRequest):
    """
    Execute analysis in parallel across multiple Ollama models.
    
    Args:
        request: AnalysisRequest containing models, system prompt, data, and question
        
    Returns:
        Dictionary with analysis_results list containing results from each model
    """
    
    system_prompt = request.system_prompt
    
    # Clean the data to remove NaN and Infinity values before serialization
    cleaned_data = clean_data_for_json(request.row)
    
    # Serialize list of dictionaries to formatted JSON string for LLM
    data_context_json = json.dumps(cleaned_data, indent=2)

    user_content = f"""
DATA CONTEXT (analyze ALL available metrics, this is a list of companies for comparison):
{data_context_json}

QUESTION:
{request.question}
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

    # Create tasks for parallel execution
    tasks = [run_ollama_query(model_name, messages) for model_name in request.models]
    
    # Execute and await all results
    results = await asyncio.gather(*tasks)
    
    # Return list of results
    return {"analysis_results": results}


# --- Roles Endpoint ---
@app.get("/roles")
def get_roles():
    """
    Get list of predefined analyst roles and their prompts.
    
    Returns:
        List of dictionaries with role_key and prompt
    """
    return [
        {"role_key": key.value, "prompt": prompt}
        for key, prompt in SYSTEM_PROMPTS.items()
    ]