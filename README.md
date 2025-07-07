# LMStudio-MCP Sidekick Edition

An enhanced Model Control Protocol (MCP) server that allows Claude to communicate with locally running LLM models via LM Studio, with added sidekick features for context offloading and task automation.

<img width="1881" alt="Screenshot 2025-03-22 at 16 50 53" src="https://github.com/user-attachments/assets/c203513b-28db-4be5-8c61-ebb8a24404ce" />

## 🚀 What's New in Sidekick Edition

This enhanced version combines the original LMStudio-MCP functionality with powerful sidekick features designed for:
- **Context Offloading**: Handle context-heavy operations without consuming main conversation space
- **Task Automation**: Process repetitive tasks efficiently
- **Batch Processing**: Handle multiple items with rate limiting
- **24/7 Availability**: Use local models without API limits

## Overview

LMStudio-MCP Sidekick creates a bridge between Claude (with MCP capabilities) and your locally running LM Studio instance. This allows Claude to:

### Core Features (Original)
- Check the health of your LM Studio API
- List available models with categorization
- Get the currently loaded model
- Generate completions using your local models

### Sidekick Features (New)
- **Offload Context**: Store, retrieve, summarize, and analyze large contexts
- **Automate Menial Tasks**: Format, extract, transform, validate, and generate content
- **Batch Process**: Efficiently process lists of items with automatic batching
- **Load Models**: Attempt to load specific models (LM Studio v0.3.0+)

## Prerequisites

- Python 3.7+
- [LM Studio](https://lmstudio.ai/) installed and running locally with a model loaded
- Claude with MCP access
- Recommended: 24GB+ VRAM for optimal performance with 32B models
- Required Python packages (see Installation)

## 🚀 Quick Installation

### One-Line Install (Recommended)
```bash
curl -fsSL https://raw.githubusercontent.com/SamuraiBuddha/LMStudio-MCP/main/install.sh | bash
```

### Manual Installation Methods

#### 1. Local Python Installation
```bash
git clone https://github.com/SamuraiBuddha/LMStudio-MCP.git
cd LMStudio-MCP
pip install requests "mcp[cli]" openai
```

#### 2. Using the Sidekick Version
```bash
# The sidekick version is in lmstudio_sidekick.py
python lmstudio_sidekick.py
```

## MCP Configuration

### For Sidekick Edition

**Using local installation**:
```json
{
  "lmstudio-sidekick": {
    "command": "python",
    "args": [
      "C:/path/to/LMStudio-MCP/lmstudio_sidekick.py"
    ]
  }
}
```

**Windows PowerShell**:
```json
{
  "lmstudio-sidekick": {
    "command": "cmd.exe",
    "args": [
      "/c",
      "cd /d C:\\Users\\YourName\\Documents\\GitHub\\LMStudio-MCP && venv\\Scripts\\activate.bat && venv\\Scripts\\python.exe lmstudio_sidekick.py"
    ]
  }
}
```

## Available Functions

### Core Functions

#### `health_check()`
Verify if LM Studio API is accessible and get system status.
- Shows number of available models
- Checks if recommended model is loaded
- Provides status indicators

#### `list_models()`
Get a categorized list of all available models in LM Studio.
- Groups models by type (Coding, General, Specialized)
- Highlights recommended models
- Shows model capabilities

#### `get_current_model()`
Identify which model is currently loaded with capability hints.

#### `chat_completion(prompt, system_prompt, temperature, max_tokens)`
Generate text from your local model with rate limiting protection.

### Sidekick Functions

#### `offload_context(context_id, context_data, operation)`
Manage large contexts without consuming main conversation space.

**Operations:**
- `store`: Save context for later use (up to 32k tokens)
- `retrieve`: Get previously stored context
- `summarize`: Create a concise summary using the model
- `analyze`: Extract key points and actionable items

**Example:**
```python
# Store a large document
offload_context("doc1", large_document_text, "store")

# Get a summary
offload_context("doc1", large_document_text, "summarize")
```

#### `automate_menial_task(task_type, task_data, output_format)`
Automate repetitive tasks efficiently.

**Task Types:**
- `format`: Clean up and format data
- `extract`: Pull out specific information
- `transform`: Convert data between formats
- `validate`: Check for errors or issues
- `generate`: Create content based on templates

**Output Formats:** `text`, `json`, `markdown`, `code`

**Example:**
```python
# Format messy JSON
automate_menial_task("format", messy_json_string, "json")

# Extract emails from text
automate_menial_task("extract", email_text, "text")
```

#### `batch_process(items, operation, batch_size, combine_results)`
Process multiple items efficiently with automatic batching.

**Parameters:**
- `items`: List of items to process
- `operation`: What to do with each item
- `batch_size`: Items per batch (default: 5)
- `combine_results`: Whether to merge results

**Example:**
```python
# Process a list of URLs
urls = ["url1", "url2", "url3", ...]
batch_process(urls, "extract title and description", 5, True)
```

#### `load_model(model_name)`
Attempt to load a specific model in LM Studio.
- Requires LM Studio v0.3.0+ with API support
- Falls back to manual instructions if not supported

## Recommended Models

For optimal sidekick performance with 24GB VRAM:
- **Qwen2.5-Coder-32B-Instruct-Q4_K_M** (18-20GB VRAM) - Best for coding tasks
- **Mixtral-8x7B-Instruct** - Good general purpose
- **Meta-Llama-3-8B-Instruct** - Efficient all-rounder

## Rate Limiting

The sidekick includes built-in rate limiting:
- 30 requests per 60 seconds per client
- Automatic rate limit checking
- Clear error messages when limits are reached

## Security Features

- Comprehensive error logging to stderr
- Rate limiting to prevent abuse
- Context size limits (32k tokens)
- Secure handling of sensitive data
- No data persistence between sessions (unless explicitly stored)

## Usage Examples

### Example 1: Offloading Large Context
```
User: "I have a 50-page document about project requirements. Can you help me understand it?"

Claude: "I'll use the sidekick to process this large document efficiently."
[Uses offload_context to store and summarize the document]
```

### Example 2: Batch Processing Emails
```
User: "I need to extract action items from 20 emails."

Claude: "I'll batch process these emails to extract action items."
[Uses batch_process with "extract action items" operation]
```

### Example 3: Code Formatting
```
User: "Can you clean up this messy JSON configuration?"

Claude: "I'll use the sidekick to format this properly."
[Uses automate_menial_task with "format" and "json" output]
```

## Known Limitations

- Context storage is session-based (not persistent)
- Model loading requires LM Studio v0.3.0+ API support
- Rate limits apply to all operations
- Maximum context size is 32k tokens
- Some models may have compatibility issues with certain operations

## Troubleshooting

### Sidekick-Specific Issues

**Rate Limit Errors:**
- Wait 60 seconds for the rate limit window to reset
- Reduce batch sizes if processing many items
- Consider spreading operations over time

**Context Too Large:**
- Split large contexts into smaller chunks
- Use summarization to reduce size
- Store multiple smaller contexts with different IDs

**Model Not Loading:**
- Ensure LM Studio supports API model loading
- Load models manually through LM Studio UI
- Check model names match exactly

For general troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Performance Tips

1. **Use Appropriate Models**: Coding models for code tasks, instruction models for general tasks
2. **Batch Wisely**: Larger batches are more efficient but may hit rate limits
3. **Temperature Settings**: Lower (0.3) for consistency, higher (0.7+) for creativity
4. **Context Management**: Summarize before storing very large contexts

## Contributing

Contributions are welcome! The sidekick edition particularly needs:
- Additional task types for automation
- Better model-specific optimizations
- Persistent storage options
- Enhanced rate limiting strategies

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT

## Acknowledgements

- Original LMStudio-MCP by infinitimeless
- Enhanced with sidekick features by Jordan Ehrig (SamuraiBuddha)
- Designed for the MAGI distributed AI architecture

---

**🌟 If this sidekick helps you work more efficiently, please consider giving it a star!**
