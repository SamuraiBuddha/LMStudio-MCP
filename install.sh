#!/bin/bash

# LMStudio-MCP Installation Script
# Supports multiple deployment methods

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
INSTALL_METHOD=""
INSTALL_DIR="$HOME/lmstudio-mcp"
PYTHON_CMD="python3"
VENV_NAME="venv"

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}    LMStudio-MCP Installer${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_requirements() {
    print_info "Checking system requirements..."
    
    # Check Python
    if ! command -v $PYTHON_CMD &> /dev/null; then
        if command -v python &> /dev/null; then
            PYTHON_CMD="python"
        else
            print_error "Python 3.7+ is required but not found"
            exit 1
        fi
    fi
    
    # Check Python version
    if ! $PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)"; then
        print_error "Python 3.7+ is required. Found: $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION found"
    
    # Check Git
    if ! command -v git &> /dev/null; then
        print_error "Git is required but not found"
        exit 1
    fi
    print_success "Git found"
    
    # Check Docker (optional)
    if command -v docker &> /dev/null; then
        print_success "Docker found"
        DOCKER_AVAILABLE=true
    else
        print_warning "Docker not found (optional for containerized deployment)"
        DOCKER_AVAILABLE=false
    fi
}

show_menu() {
    echo ""
    print_info "Choose installation method:"
    echo "1) Local Python installation (recommended)"
    echo "2) Docker container"
    echo "3) Docker Compose"
    echo "4) Development setup"
    echo "5) Exit"
    echo ""
    read -p "Enter your choice (1-5): " choice
    
    case $choice in
        1) INSTALL_METHOD="local" ;;
        2) INSTALL_METHOD="docker" ;;
        3) INSTALL_METHOD="compose" ;;
        4) INSTALL_METHOD="dev" ;;
        5) exit 0 ;;
        *) print_error "Invalid choice"; show_menu ;;
    esac
}

install_local() {
    print_info "Installing LMStudio-MCP locally..."
    
    # Create installation directory
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # Clone repository
    if [ -d ".git" ]; then
        print_info "Repository exists, pulling latest changes..."
        git pull
    else
        print_info "Cloning repository..."
        git clone https://github.com/infinitimeless/LMStudio-MCP.git .
    fi
    
    # Create virtual environment
    print_info "Creating virtual environment..."
    $PYTHON_CMD -m venv $VENV_NAME
    
    # Activate virtual environment
    source $VENV_NAME/bin/activate
    
    # Install dependencies
    print_info "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create startup script
    cat > start_lmstudio_mcp.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python lmstudio_bridge.py "$@"
EOF
    chmod +x start_lmstudio_mcp.sh
    
    print_success "Local installation completed!"
    print_info "Installation directory: $INSTALL_DIR"
    print_info "To start: cd $INSTALL_DIR && ./start_lmstudio_mcp.sh"
}

install_docker() {
    if [ "$DOCKER_AVAILABLE" != "true" ]; then
        print_error "Docker is not available"
        exit 1
    fi
    
    print_info "Setting up Docker deployment..."
    
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # Download Docker files
    print_info "Downloading Docker configuration..."
    curl -s https://raw.githubusercontent.com/infinitimeless/LMStudio-MCP/main/Dockerfile -o Dockerfile
    curl -s https://raw.githubusercontent.com/infinitimeless/LMStudio-MCP/main/.dockerignore -o .dockerignore
    
    # Build image
    print_info "Building Docker image..."
    docker build -t lmstudio-mcp .
    
    # Create run script
    cat > run_docker.sh << 'EOF'
#!/bin/bash
docker run -it --rm --network host --name lmstudio-mcp-server lmstudio-mcp
EOF
    chmod +x run_docker.sh
    
    print_success "Docker installation completed!"
    print_info "To start: cd $INSTALL_DIR && ./run_docker.sh"
}

install_compose() {
    if [ "$DOCKER_AVAILABLE" != "true" ]; then
        print_error "Docker is not available"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is required but not found"
        exit 1
    fi
    
    print_info "Setting up Docker Compose deployment..."
    
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # Download compose files
    print_info "Downloading Docker Compose configuration..."
    curl -s https://raw.githubusercontent.com/infinitimeless/LMStudio-MCP/main/docker-compose.yml -o docker-compose.yml
    curl -s https://raw.githubusercontent.com/infinitimeless/LMStudio-MCP/main/Dockerfile -o Dockerfile
    curl -s https://raw.githubusercontent.com/infinitimeless/LMStudio-MCP/main/.dockerignore -o .dockerignore
    
    # Create management scripts
    cat > start.sh << 'EOF'
#!/bin/bash
docker-compose up -d
EOF
    chmod +x start.sh
    
    cat > stop.sh << 'EOF'
#!/bin/bash
docker-compose down
EOF
    chmod +x stop.sh
    
    cat > logs.sh << 'EOF'
#!/bin/bash
docker-compose logs -f lmstudio-mcp
EOF
    chmod +x logs.sh
    
    print_success "Docker Compose installation completed!"
    print_info "Commands:"
    print_info "  Start: cd $INSTALL_DIR && ./start.sh"
    print_info "  Stop:  cd $INSTALL_DIR && ./stop.sh"
    print_info "  Logs:  cd $INSTALL_DIR && ./logs.sh"
}

install_dev() {
    print_info "Setting up development environment..."
    
    # Create installation directory
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # Clone repository
    if [ -d ".git" ]; then
        print_info "Repository exists, pulling latest changes..."
        git pull
    else
        print_info "Cloning repository..."
        git clone https://github.com/infinitimeless/LMStudio-MCP.git .
    fi
    
    # Create virtual environment
    print_info "Creating virtual environment..."
    $PYTHON_CMD -m venv $VENV_NAME
    
    # Activate virtual environment
    source $VENV_NAME/bin/activate
    
    # Install dependencies including dev tools
    print_info "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install -e .
    
    # Install development dependencies
    pip install pytest pytest-cov black flake8 mypy
    
    # Create development scripts
    cat > dev_setup.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
echo "Development environment activated"
echo "Available commands:"
echo "  python lmstudio_bridge.py  - Run the bridge"
echo "  pytest                     - Run tests"
echo "  black .                    - Format code"
echo "  flake8 .                   - Lint code"
EOF
    chmod +x dev_setup.sh
    
    print_success "Development environment setup completed!"
    print_info "Installation directory: $INSTALL_DIR"
    print_info "To activate: cd $INSTALL_DIR && source dev_setup.sh"
}

create_mcp_config() {
    print_info "Creating MCP configuration example..."
    
    cat > mcp_config_example.json << EOF
{
  "lmstudio-mcp": {
    "command": "uvx",
    "args": [
      "https://github.com/infinitimeless/LMStudio-MCP"
    ]
  }
}
EOF
    
    if [ "$INSTALL_METHOD" = "local" ]; then
        cat > mcp_config_local.json << EOF
{
  "lmstudio-mcp-local": {
    "command": "/bin/bash",
    "args": [
      "-c",
      "cd $INSTALL_DIR && source venv/bin/activate && python lmstudio_bridge.py"
    ]
  }
}
EOF
    fi
    
    if [ "$INSTALL_METHOD" = "docker" ]; then
        cat > mcp_config_docker.json << EOF
{
  "lmstudio-mcp-docker": {
    "command": "docker",
    "args": [
      "run",
      "-i",
      "--rm",
      "--network=host",
      "lmstudio-mcp"
    ]
  }
}
EOF
    fi
    
    print_success "MCP configuration examples created"
}

main() {
    print_header
    
    check_requirements
    show_menu
    
    case $INSTALL_METHOD in
        "local") install_local ;;
        "docker") install_docker ;;
        "compose") install_compose ;;
        "dev") install_dev ;;
    esac
    
    create_mcp_config
    
    echo ""
    print_success "Installation completed successfully!"
    print_info "Next steps:"
    print_info "1. Ensure LM Studio is running on localhost:1234"
    print_info "2. Configure Claude MCP with the provided configuration"
    print_info "3. Test the connection"
    echo ""
    print_info "For troubleshooting, see: https://github.com/infinitimeless/LMStudio-MCP/blob/main/TROUBLESHOOTING.md"
}

# Run main function
main "$@"
