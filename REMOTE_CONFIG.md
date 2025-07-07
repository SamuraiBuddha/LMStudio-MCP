# Remote LM Studio Configuration Guide

The LM Studio Sidekick MCP now supports connecting to remote LM Studio instances, perfect for distributed setups like your MAGI system.

## Environment Variables

The sidekick uses the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `LMSTUDIO_HOST` | LM Studio server hostname/IP | `localhost` |
| `LMSTUDIO_PORT` | LM Studio server port | `1234` |
| `RATE_LIMIT_WINDOW` | Rate limit time window (seconds) | `60` |
| `RATE_LIMIT_MAX_REQUESTS` | Max requests per window | `30` |
| `MAX_CONTEXT_SIZE` | Maximum context tokens | `32000` |

## Configuration Examples

### 1. Connect to Remote LM Studio (e.g., Melchior at 192.168.50.30)

**Windows (cmd.exe):**
```json
{
  "lmstudio-sidekick": {
    "command": "cmd.exe",
    "args": [
      "/c",
      "cd /d C:\\Users\\JordanEhrig\\Documents\\GitHub\\LMStudio-MCP && set LMSTUDIO_HOST=192.168.50.30 && venv\\Scripts\\python.exe lmstudio_sidekick.py"
    ]
  }
}
```

**Windows (PowerShell):**
```json
{
  "lmstudio-sidekick": {
    "command": "powershell.exe",
    "args": [
      "-Command",
      "cd C:\\Users\\JordanEhrig\\Documents\\GitHub\\LMStudio-MCP; $env:LMSTUDIO_HOST='192.168.50.30'; .\\venv\\Scripts\\python.exe lmstudio_sidekick.py"
    ]
  }
}
```

**Linux/Mac:**
```json
{
  "lmstudio-sidekick": {
    "command": "bash",
    "args": [
      "-c",
      "cd ~/LMStudio-MCP && LMSTUDIO_HOST=192.168.50.30 python lmstudio_sidekick.py"
    ]
  }
}
```

### 2. Multiple Remote Instances (Different Configs)

For Melchior (Coding Tasks):
```json
{
  "lmstudio-melchior": {
    "command": "cmd.exe",
    "args": [
      "/c",
      "cd /d C:\\Users\\JordanEhrig\\Documents\\GitHub\\LMStudio-MCP && set LMSTUDIO_HOST=192.168.50.30 && set LMSTUDIO_PORT=1234 && venv\\Scripts\\python.exe lmstudio_sidekick.py"
    ]
  }
}
```

For Balthazar (General Tasks):
```json
{
  "lmstudio-balthazar": {
    "command": "cmd.exe",
    "args": [
      "/c",
      "cd /d C:\\Users\\JordanEhrig\\Documents\\GitHub\\LMStudio-MCP && set LMSTUDIO_HOST=192.168.50.20 && set LMSTUDIO_PORT=1234 && venv\\Scripts\\python.exe lmstudio_sidekick.py"
    ]
  }
}
```

For Caspar (Specialized Tasks):
```json
{
  "lmstudio-caspar": {
    "command": "cmd.exe",
    "args": [
      "/c",
      "cd /d C:\\Users\\JordanEhrig\\Documents\\GitHub\\LMStudio-MCP && set LMSTUDIO_HOST=192.168.50.21 && set LMSTUDIO_PORT=1234 && venv\\Scripts\\python.exe lmstudio_sidekick.py"
    ]
  }
}
```

### 3. Custom Rate Limits for Heavy Usage

```json
{
  "lmstudio-sidekick-heavy": {
    "command": "cmd.exe",
    "args": [
      "/c",
      "cd /d C:\\Users\\JordanEhrig\\Documents\\GitHub\\LMStudio-MCP && set LMSTUDIO_HOST=192.168.50.30 && set RATE_LIMIT_WINDOW=120 && set RATE_LIMIT_MAX_REQUESTS=60 && venv\\Scripts\\python.exe lmstudio_sidekick.py"
    ]
  }
}
```

### 4. Using .env File (Alternative Method)

Create a `.env` file in your LMStudio-MCP directory:
```env
LMSTUDIO_HOST=192.168.50.30
LMSTUDIO_PORT=1234
RATE_LIMIT_WINDOW=60
RATE_LIMIT_MAX_REQUESTS=30
MAX_CONTEXT_SIZE=32000
```

Then use python-dotenv:
```bash
pip install python-dotenv
```

And update the script to load it (add at the top of lmstudio_sidekick.py):
```python
from dotenv import load_dotenv
load_dotenv()
```

## MAGI System Example Configuration

For your MAGI distributed system, you could set up three different sidekicks:

```json
{
  "mcps": {
    // Melchior - RTX A5000 24GB - Coding Tasks
    "lm-melchior": {
      "command": "cmd.exe",
      "args": [
        "/c",
        "cd /d C:\\Users\\JordanEhrig\\Documents\\GitHub\\LMStudio-MCP && set LMSTUDIO_HOST=192.168.50.30 && venv\\Scripts\\python.exe lmstudio_sidekick.py"
      ]
    },
    
    // Balthazar - RTX A4000 16GB - General Tasks
    "lm-balthazar": {
      "command": "cmd.exe",
      "args": [
        "/c",
        "cd /d C:\\Users\\JordanEhrig\\Documents\\GitHub\\LMStudio-MCP && set LMSTUDIO_HOST=192.168.50.20 && venv\\Scripts\\python.exe lmstudio_sidekick.py"
      ]
    },
    
    // Caspar - RTX 3090 24GB - Specialized Tasks
    "lm-caspar": {
      "command": "cmd.exe",
      "args": [
        "/c",
        "cd /d C:\\Users\\JordanEhrig\\Documents\\GitHub\\LMStudio-MCP && set LMSTUDIO_HOST=192.168.50.21 && venv\\Scripts\\python.exe lmstudio_sidekick.py"
      ]
    }
  }
}
```

## Testing Your Configuration

After setting up, test the connection:

1. In Claude, use the health_check tool:
   ```
   "Check if the sidekick is connected to the remote LM Studio"
   ```

2. The response should show:
   ```
   ✅ LM Studio API is running and accessible at 192.168.50.30:1234
   📊 X models available
   ```

## Performance Tips

1. **Network Latency**: Remote connections will have higher latency than localhost
2. **Model Loading**: Load models directly on the remote machine for best performance
3. **Rate Limiting**: Adjust rate limits based on your network and server capacity
4. **Context Size**: Larger contexts take longer over network connections

## Security Considerations

1. **Network Security**: Ensure your LM Studio instances are on a secure network
2. **Firewall**: Only allow connections from trusted sources
3. **VPN**: Consider using a VPN for remote connections
4. **API Keys**: LM Studio doesn't support API keys by default, so network security is crucial

## Troubleshooting

### Connection Refused
- Verify LM Studio is running on the remote machine
- Check that the server is enabled in LM Studio settings
- Ensure the port (default 1234) is not blocked by firewall

### Timeout Errors
- Increase timeout values in the code if needed
- Check network connectivity with `ping 192.168.50.30`
- Verify no proxy is interfering

### Model Not Found
- Ensure the model is loaded on the remote LM Studio instance
- Use `list_models()` to see available models
- Load models directly on the remote machine, not through the MCP
