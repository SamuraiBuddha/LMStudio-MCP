#!/usr/bin/env python3
"""
LM Studio Sidekick MCP Server
Enhanced version combining existing functionality with sidekick features
for context offloading and menial task automation.

Supports both local and remote LM Studio instances.
"""

from mcp.server.fastmcp import FastMCP
import requests
import json
import sys
import os
import time
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import re

# Initialize FastMCP server
mcp = FastMCP("lmstudio-sidekick")

# LM Studio settings - now configurable via environment variables
LMSTUDIO_HOST = os.getenv("LMSTUDIO_HOST", "localhost")
LMSTUDIO_PORT = os.getenv("LMSTUDIO_PORT", "1234")
LMSTUDIO_API_BASE = f"http://{LMSTUDIO_HOST}:{LMSTUDIO_PORT}/v1"

DEFAULT_MODEL = "default"  # Will be replaced with whatever model is currently loaded
RECOMMENDED_MODEL = "qwen2.5-coder-32b-instruct-q4_k_m"  # Optimized for A5000 24GB

# Rate limiting configuration
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "30"))  # max requests per window
rate_limiter = defaultdict(list)

# Context management
context_store = {}
MAX_CONTEXT_SIZE = int(os.getenv("MAX_CONTEXT_SIZE", "32000"))  # tokens

def log_error(message: str):
    """Log error messages to stderr for debugging"""
    print(f"[{datetime.now().isoformat()}] ERROR: {message}", file=sys.stderr)

def log_info(message: str):
    """Log informational messages to stderr for debugging"""
    print(f"[{datetime.now().isoformat()}] INFO: {message}", file=sys.stderr)

def check_rate_limit(client_id: str = "default") -> bool:
    """Check if client has exceeded rate limit"""
    now = time.time()
    # Clean up old entries
    rate_limiter[client_id] = [t for t in rate_limiter[client_id] if now - t < RATE_LIMIT_WINDOW]
    
    if len(rate_limiter[client_id]) >= RATE_LIMIT_MAX_REQUESTS:
        return False
    
    rate_limiter[client_id].append(now)
    return True

def estimate_tokens(text: str) -> int:
    """Rough estimation of token count (4 chars ≈ 1 token)"""
    return len(text) // 4

@mcp.tool()
async def health_check() -> str:
    """Check if LM Studio API is accessible and get system status.
    
    Returns:
        A message indicating the LM Studio API status and current configuration.
    """
    try:
        log_info(f"Checking LM Studio at {LMSTUDIO_API_BASE}")
        response = requests.get(f"{LMSTUDIO_API_BASE}/models", timeout=5)
        if response.status_code == 200:
            models = response.json().get("data", [])
            model_count = len(models)
            
            # Check if recommended model is available
            has_recommended = any(RECOMMENDED_MODEL in model.get('id', '') for model in models)
            
            status = f"✅ LM Studio API is running and accessible at {LMSTUDIO_HOST}:{LMSTUDIO_PORT}\n"
            status += f"📊 {model_count} models available\n"
            
            if has_recommended:
                status += f"✨ Recommended model '{RECOMMENDED_MODEL}' is available!"
            else:
                status += f"ℹ️ Recommended model '{RECOMMENDED_MODEL}' not found. Consider loading it for optimal performance."
            
            return status
        else:
            return f"⚠️ LM Studio API at {LMSTUDIO_HOST}:{LMSTUDIO_PORT} returned status code {response.status_code}."
    except requests.exceptions.ConnectionError:
        return f"❌ Cannot connect to LM Studio at {LMSTUDIO_HOST}:{LMSTUDIO_PORT}. Make sure LM Studio is running and the server is started."
    except Exception as e:
        return f"❌ Error connecting to LM Studio API at {LMSTUDIO_HOST}:{LMSTUDIO_PORT}: {str(e)}"

@mcp.tool()
async def list_models() -> str:
    """List all available models in LM Studio with recommendations.
    
    Returns:
        A formatted list of available models with sidekick recommendations.
    """
    try:
        response = requests.get(f"{LMSTUDIO_API_BASE}/models", timeout=5)
        if response.status_code != 200:
            return f"Failed to fetch models from {LMSTUDIO_HOST}:{LMSTUDIO_PORT}. Status code: {response.status_code}"
        
        models = response.json().get("data", [])
        if not models:
            return f"No models found in LM Studio at {LMSTUDIO_HOST}:{LMSTUDIO_PORT}."
        
        result = f"🤖 Available models in LM Studio ({LMSTUDIO_HOST}:{LMSTUDIO_PORT}):\n\n"
        
        # Categorize models
        coding_models = []
        general_models = []
        specialized_models = []
        
        for model in models:
            model_id = model['id']
            if 'code' in model_id.lower() or 'coder' in model_id.lower():
                coding_models.append(model_id)
            elif any(x in model_id.lower() for x in ['db', 'os', 'math', 'embedding']):
                specialized_models.append(model_id)
            else:
                general_models.append(model_id)
        
        # Display categorized models
        if coding_models:
            result += "💻 **Coding Models** (Great for sidekick tasks):\n"
            for model in coding_models:
                if RECOMMENDED_MODEL in model:
                    result += f"  - {model} ⭐ RECOMMENDED\n"
                else:
                    result += f"  - {model}\n"
            result += "\n"
        
        if general_models:
            result += "🌐 **General Models**:\n"
            for model in general_models:
                result += f"  - {model}\n"
            result += "\n"
        
        if specialized_models:
            result += "🔧 **Specialized Models**:\n"
            for model in specialized_models:
                result += f"  - {model}\n"
        
        return result
    except Exception as e:
        log_error(f"Error in list_models: {str(e)}")
        return f"Error listing models from {LMSTUDIO_HOST}:{LMSTUDIO_PORT}: {str(e)}"

@mcp.tool()
async def get_current_model() -> str:
    """Get the currently loaded model in LM Studio.
    
    Returns:
        Information about the currently loaded model and its capabilities.
    """
    try:
        # Test with a minimal completion request
        response = requests.post(
            f"{LMSTUDIO_API_BASE}/chat/completions",
            json={
                "messages": [{"role": "user", "content": "Hi"}],
                "temperature": 0.1,
                "max_tokens": 5
            },
            timeout=10
        )
        
        if response.status_code != 200:
            return f"❌ No model currently loaded at {LMSTUDIO_HOST}:{LMSTUDIO_PORT}. Status code: {response.status_code}"
        
        # Extract model info from response
        model_info = response.json().get("model", "Unknown")
        
        result = f"🎯 Currently loaded model at {LMSTUDIO_HOST}:{LMSTUDIO_PORT}: {model_info}\n\n"
        
        # Add recommendations based on model type
        if 'coder' in model_info.lower():
            result += "💡 This is a coding model - perfect for:\n"
            result += "  • Code generation and refactoring\n"
            result += "  • Debugging and optimization\n"
            result += "  • Documentation tasks\n"
        elif 'instruct' in model_info.lower():
            result += "💡 This is an instruction-following model - great for:\n"
            result += "  • General Q&A and explanations\n"
            result += "  • Task automation\n"
            result += "  • Content generation\n"
        
        return result
    except Exception as e:
        log_error(f"Error in get_current_model: {str(e)}")
        return f"❌ Error identifying current model at {LMSTUDIO_HOST}:{LMSTUDIO_PORT}: {str(e)}"

@mcp.tool()
async def chat_completion(
    prompt: str, 
    system_prompt: str = "", 
    temperature: float = 0.7, 
    max_tokens: int = 1024
) -> str:
    """Generate a completion from the current LM Studio model.
    
    Args:
        prompt: The user's prompt to send to the model
        system_prompt: Optional system instructions for the model
        temperature: Controls randomness (0.0 to 1.0)
        max_tokens: Maximum number of tokens to generate
        
    Returns:
        The model's response to the prompt
    """
    # Check rate limit
    if not check_rate_limit():
        return "⚠️ Rate limit exceeded. Please wait a moment before trying again."
    
    try:
        messages = []
        
        # Add system message if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add user message
        messages.append({"role": "user", "content": prompt})
        
        log_info(f"Sending request to LM Studio at {LMSTUDIO_HOST}:{LMSTUDIO_PORT} with {len(messages)} messages")
        
        response = requests.post(
            f"{LMSTUDIO_API_BASE}/chat/completions",
            json={
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            timeout=30
        )
        
        if response.status_code != 200:
            log_error(f"LM Studio API error: {response.status_code}")
            return f"Error: LM Studio at {LMSTUDIO_HOST}:{LMSTUDIO_PORT} returned status code {response.status_code}"
        
        response_json = response.json()
        log_info(f"Received response from LM Studio")
        
        # Extract the assistant's message
        choices = response_json.get("choices", [])
        if not choices:
            return "Error: No response generated"
        
        message = choices[0].get("message", {})
        content = message.get("content", "")
        
        if not content:
            return "Error: Empty response from model"
        
        return content
    except Exception as e:
        log_error(f"Error in chat_completion: {str(e)}")
        return f"Error generating completion: {str(e)}"

@mcp.tool()
async def offload_context(
    context_id: str,
    context_data: str,
    operation: str = "store"
) -> str:
    """Offload conversation context to the sidekick for processing.
    
    This allows the main Claude conversation to stay focused while the sidekick
    handles context-heavy operations like summarization or analysis.
    
    Args:
        context_id: Unique identifier for this context
        context_data: The context data to offload
        operation: What to do with the context ('store', 'summarize', 'analyze', 'retrieve')
        
    Returns:
        Result of the context operation
    """
    try:
        if operation == "store":
            # Store context for later use
            estimated_tokens = estimate_tokens(context_data)
            if estimated_tokens > MAX_CONTEXT_SIZE:
                return f"⚠️ Context too large ({estimated_tokens} tokens). Maximum is {MAX_CONTEXT_SIZE} tokens."
            
            context_store[context_id] = {
                "data": context_data,
                "timestamp": datetime.now().isoformat(),
                "tokens": estimated_tokens
            }
            return f"✅ Context stored successfully. ID: {context_id} ({estimated_tokens} tokens)"
        
        elif operation == "retrieve":
            if context_id not in context_store:
                return f"❌ Context ID '{context_id}' not found."
            
            ctx = context_store[context_id]
            return f"📋 Context retrieved:\n\n{ctx['data']}\n\n(Stored: {ctx['timestamp']}, {ctx['tokens']} tokens)"
        
        elif operation == "summarize":
            # Use the model to summarize the context
            system_prompt = "You are a helpful assistant that creates concise summaries. Summarize the following context, preserving key information."
            
            response = await chat_completion(
                prompt=f"Please summarize this context:\n\n{context_data}",
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=500
            )
            
            # Store the summary
            context_store[f"{context_id}_summary"] = {
                "data": response,
                "timestamp": datetime.now().isoformat(),
                "tokens": estimate_tokens(response)
            }
            
            return f"📝 Summary created:\n\n{response}"
        
        elif operation == "analyze":
            # Analyze the context for key points
            system_prompt = "You are an analytical assistant. Extract key points, entities, and actionable items from the context."
            
            response = await chat_completion(
                prompt=f"Analyze this context and extract key information:\n\n{context_data}",
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=800
            )
            
            return f"🔍 Analysis:\n\n{response}"
        
        else:
            return f"❌ Unknown operation: {operation}. Use 'store', 'retrieve', 'summarize', or 'analyze'."
            
    except Exception as e:
        log_error(f"Error in offload_context: {str(e)}")
        return f"Error processing context: {str(e)}"

@mcp.tool()
async def automate_menial_task(
    task_type: str,
    task_data: str,
    output_format: str = "text"
) -> str:
    """Automate repetitive or menial tasks using the sidekick model.
    
    Perfect for tasks like formatting, data extraction, simple transformations,
    and other repetitive work that doesn't need the main Claude's attention.
    
    Args:
        task_type: Type of task ('format', 'extract', 'transform', 'validate', 'generate')
        task_data: The data to process
        output_format: Desired output format ('text', 'json', 'markdown', 'code')
        
    Returns:
        Processed result based on the task type
    """
    # Check rate limit
    if not check_rate_limit():
        return "⚠️ Rate limit exceeded. Please wait a moment before trying again."
    
    try:
        # Define system prompts for different task types
        task_prompts = {
            "format": f"You are a formatting assistant. Format the following data as clean {output_format}. Be precise and consistent.",
            "extract": f"You are a data extraction assistant. Extract relevant information and present it as {output_format}.",
            "transform": f"You are a data transformation assistant. Transform the input according to common patterns and output as {output_format}.",
            "validate": "You are a validation assistant. Check the data for errors, inconsistencies, or issues. Report findings clearly.",
            "generate": f"You are a content generation assistant. Generate appropriate content based on the input, formatted as {output_format}."
        }
        
        if task_type not in task_prompts:
            return f"❌ Unknown task type: {task_type}. Available types: {', '.join(task_prompts.keys())}"
        
        system_prompt = task_prompts[task_type]
        
        # Add output format hints
        format_hints = {
            "json": "\n\nOutput valid JSON only.",
            "markdown": "\n\nUse proper Markdown formatting.",
            "code": "\n\nOutput clean, properly formatted code.",
            "text": "\n\nOutput plain text."
        }
        
        if output_format in format_hints:
            system_prompt += format_hints[output_format]
        
        # Process the task
        response = await chat_completion(
            prompt=f"Task: {task_type}\n\nData:\n{task_data}",
            system_prompt=system_prompt,
            temperature=0.3,  # Lower temperature for consistency
            max_tokens=2048
        )
        
        return response
        
    except Exception as e:
        log_error(f"Error in automate_menial_task: {str(e)}")
        return f"Error automating task: {str(e)}"

@mcp.tool()
async def batch_process(
    items: List[str],
    operation: str,
    batch_size: int = 5,
    combine_results: bool = True
) -> str:
    """Process multiple items in batches using the sidekick model.
    
    Efficient for processing lists of similar items without overwhelming
    the model or hitting rate limits.
    
    Args:
        items: List of items to process
        operation: The operation to perform on each item
        batch_size: Number of items to process at once (default: 5)
        combine_results: Whether to combine results into one response
        
    Returns:
        Processed results from all batches
    """
    try:
        if not items:
            return "❌ No items provided for batch processing."
        
        results = []
        total_items = len(items)
        
        log_info(f"Starting batch processing of {total_items} items in batches of {batch_size}")
        
        # Process in batches
        for i in range(0, total_items, batch_size):
            batch = items[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_items + batch_size - 1) // batch_size
            
            # Check rate limit for each batch
            if not check_rate_limit():
                results.append(f"⚠️ Rate limit hit at batch {batch_num}. Processed {i} items.")
                break
            
            # Create batch prompt
            batch_prompt = f"Process these {len(batch)} items with operation: {operation}\n\n"
            for idx, item in enumerate(batch, 1):
                batch_prompt += f"{idx}. {item}\n"
            
            # Process batch
            response = await chat_completion(
                prompt=batch_prompt,
                system_prompt="You are a batch processing assistant. Process each item according to the specified operation. Be consistent across all items.",
                temperature=0.3,
                max_tokens=1024
            )
            
            results.append(f"**Batch {batch_num}/{total_batches}:**\n{response}")
            
            # Small delay between batches to avoid overwhelming the API
            if i + batch_size < total_items:
                await asyncio.sleep(0.5)
        
        # Combine or return separate results
        if combine_results:
            return "\n\n---\n\n".join(results)
        else:
            return json.dumps({
                "total_items": total_items,
                "processed_items": min(len(results) * batch_size, total_items),
                "results": results
            }, indent=2)
            
    except Exception as e:
        log_error(f"Error in batch_process: {str(e)}")
        return f"Error in batch processing: {str(e)}"

@mcp.tool()
async def load_model(model_name: str) -> str:
    """Attempt to load a specific model in LM Studio.
    
    Note: This requires LM Studio API v0.3.0+ with model loading support.
    May not work with all LM Studio versions.
    
    Args:
        model_name: Name or path of the model to load
        
    Returns:
        Status of the model loading operation
    """
    try:
        # Try the model load endpoint (may not be available in all versions)
        response = requests.post(
            f"{LMSTUDIO_API_BASE}/models/load",
            json={"model": model_name},
            timeout=30
        )
        
        if response.status_code == 200:
            return f"✅ Model '{model_name}' loaded successfully at {LMSTUDIO_HOST}:{LMSTUDIO_PORT}!"
        elif response.status_code == 404:
            return f"⚠️ Model loading not supported in this LM Studio version. Please load '{model_name}' manually through the LM Studio UI."
        else:
            return f"❌ Failed to load model. Status: {response.status_code}"
            
    except Exception as e:
        log_error(f"Error in load_model: {str(e)}")
        return f"❌ Model loading failed: {str(e)}\n\nPlease load the model manually through LM Studio."

def main():
    """Entry point for the package when installed via pip"""
    log_info("Starting LM Studio Sidekick MCP Server")
    log_info(f"Connecting to LM Studio at {LMSTUDIO_HOST}:{LMSTUDIO_PORT}")
    log_info(f"Recommended model: {RECOMMENDED_MODEL}")
    log_info(f"Rate limit: {RATE_LIMIT_MAX_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds")
    
    # Display environment variable info
    if LMSTUDIO_HOST != "localhost":
        log_info(f"Using remote LM Studio instance at {LMSTUDIO_HOST}")
    
    mcp.run(transport='stdio')

if __name__ == "__main__":
    # Initialize and run the server
    main()
