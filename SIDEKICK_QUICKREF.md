# LM Studio Sidekick Quick Reference

## 🚀 New Sidekick Features

### Context Offloading
```python
# Store large context
offload_context("doc1", large_text, "store")

# Retrieve stored context
offload_context("doc1", "", "retrieve")

# Summarize context
offload_context("doc1", large_text, "summarize")

# Analyze for key points
offload_context("doc1", large_text, "analyze")
```

### Task Automation
```python
# Format messy data
automate_menial_task("format", messy_json, "json")

# Extract information
automate_menial_task("extract", email_text, "text")

# Transform data
automate_menial_task("transform", csv_data, "markdown")

# Validate data
automate_menial_task("validate", config_file, "text")

# Generate content
automate_menial_task("generate", template, "code")
```

### Batch Processing
```python
# Process list of items
items = ["item1", "item2", "item3", ...]
batch_process(items, "extract summary", 5, True)

# Get separate results
batch_process(items, "analyze", 3, False)
```

## 🔧 Remote Configuration

### Connect to Remote LM Studio
```bash
# Set environment variable
set LMSTUDIO_HOST=192.168.50.30
set LMSTUDIO_PORT=1234

# Or in config.json
"args": ["/c", "cd /d C:\\path\\to\\LMStudio-MCP && set LMSTUDIO_HOST=192.168.50.30 && python lmstudio_sidekick.py"]
```

### MAGI System IPs
- Melchior: `192.168.50.30` (RTX A5000 24GB)
- Balthazar: `192.168.50.20` (RTX A4000 16GB)  
- Caspar: `192.168.50.21` (RTX 3090 24GB)

## 📊 Rate Limits & Constraints

| Feature | Limit | Configurable |
|---------|-------|--------------|
| Rate Limit | 30 req/60s | Yes (env vars) |
| Context Size | 32k tokens | Yes (env vars) |
| Batch Size | 5 items | Yes (parameter) |
| Max Tokens | 1024 default | Yes (parameter) |

## 🎯 Task Type Reference

### Format Tasks
- Clean up messy JSON/XML
- Standardize data formats
- Fix indentation and structure

### Extract Tasks  
- Pull out emails, URLs, names
- Extract key information
- Parse structured data

### Transform Tasks
- Convert between formats
- Restructure data
- Apply transformations

### Validate Tasks
- Check for errors
- Verify data integrity
- Find inconsistencies

### Generate Tasks
- Create from templates
- Generate test data
- Produce documentation

## 💡 Best Practices

1. **Model Selection**
   - Coding models for code tasks
   - Instruction models for general tasks
   - Load before heavy usage

2. **Context Management**
   - Store frequently used contexts
   - Summarize before storing large texts
   - Use meaningful context IDs

3. **Batch Processing**
   - Group similar items
   - Use smaller batches for complex operations
   - Monitor rate limits

4. **Remote Usage**
   - Place sidekick close to LM Studio
   - Use wired connections when possible
   - Monitor network latency

## 🔥 Common Commands

```bash
# Check connection
"Is the sidekick connected?"

# List available models  
"What models are available?"

# Store document
"Store this document as 'project_spec'"

# Batch process emails
"Extract action items from these 20 emails"

# Format code
"Format this JSON properly"
```

## 🛠️ Environment Variables

```bash
LMSTUDIO_HOST=192.168.50.30      # Remote host
LMSTUDIO_PORT=1234               # Port (default)
RATE_LIMIT_WINDOW=60             # Seconds
RATE_LIMIT_MAX_REQUESTS=30       # Per window
MAX_CONTEXT_SIZE=32000           # Tokens
```

## 📈 Performance Tips

- **Local > Remote**: ~10ms vs ~50-100ms latency
- **Batch Operations**: 5-10x faster than individual
- **Context Caching**: Reuse stored contexts
- **Model Preload**: Load models before batch operations

---

**Remember**: The sidekick is designed to handle the grunt work so Claude can focus on complex reasoning! 🎯
