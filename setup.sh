#!/bin/bash

# BrainSAIT AI Business Discovery System - Setup Script
# This script automates the setup process for new installations

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     BrainSAIT AI Business Discovery System Setup          ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check Python version
check_python() {
    print_info "Checking Python version..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        REQUIRED_VERSION="3.11"
        
        if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
            print_success "Python $PYTHON_VERSION found"
            return 0
        else
            print_error "Python 3.11+ required, found $PYTHON_VERSION"
            return 1
        fi
    else
        print_error "Python 3 not found"
        return 1
    fi
}

# Create virtual environment
create_venv() {
    print_info "Creating virtual environment..."
    if [ -d "venv" ]; then
        print_info "Virtual environment already exists"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
            python3 -m venv venv
            print_success "Virtual environment recreated"
        else
            print_info "Using existing virtual environment"
        fi
    else
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
}

# Activate virtual environment
activate_venv() {
    print_info "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_info "Installing dependencies..."
    pip install --upgrade pip setuptools wheel
    pip install -e ".[dev]"
    print_success "Dependencies installed"
}

# Setup environment file
setup_env() {
    print_info "Setting up environment configuration..."
    if [ -f ".env" ]; then
        print_info ".env file already exists"
        read -p "Do you want to edit it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} .env
        fi
    else
        cp .env.example .env
        print_success ".env file created from template"
        print_info "Please edit .env with your API keys:"
        echo ""
        echo "  - GOOGLE_MAPS_API_KEY (required)"
        echo "  - OPENAI_API_KEY (optional)"
        echo ""
        read -p "Open .env for editing now? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            ${EDITOR:-nano} .env
        fi
    fi
}

# Run tests
run_tests() {
    print_info "Running test suite..."
    if pytest -v; then
        print_success "All tests passed!"
    else
        print_error "Some tests failed"
        return 1
    fi
}

# Main setup process
main() {
    print_header
    
    # Check prerequisites
    if ! check_python; then
        print_error "Setup failed: Python 3.11+ required"
        exit 1
    fi
    
    echo ""
    
    # Create and activate virtual environment
    create_venv
    activate_venv
    
    echo ""
    
    # Install dependencies
    install_dependencies
    
    echo ""
    
    # Setup environment
    setup_env
    
    echo ""
    
    # Ask about running tests
    print_info "Setup complete!"
    read -p "Do you want to run tests now? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo ""
        run_tests
    fi
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    Setup Complete! 🎉                      ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Activate the virtual environment:"
    echo "   source venv/bin/activate"
    echo ""
    echo "2. Run your first discovery:"
    echo "   brainsait-discover restaurant clinic --location \"24.7136,46.6753\""
    echo ""
    echo "3. View configuration:"
    echo "   brainsait-discover config"
    echo ""
    echo "4. Read the documentation:"
    echo "   https://fadil369.github.io/brainsait-ai-automation/"
    echo ""
    echo -e "${BLUE}Happy discovering! 🚀${NC}"
}

# Run main function
main
