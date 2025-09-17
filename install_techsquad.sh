#!/bin/bash
# TechSquad Inc. - Ghidra GPT-5 MCP Server Comprehensive Installer
#
# Copyright (c) 2024 TechSquad Inc. - All Rights Reserved
# Proprietary Software - NOT FOR RESALE
# Coded by: TheStingR
#
# This software is the property of TechSquad Inc. and is protected by copyright law.
# Unauthorized reproduction, distribution, or sale is strictly prohibited.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="$HOME/mcp-servers/techsquad-ghidra-gpt5"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_CMD="python3"

echo -e "${BOLD}${BLUE}🏢 TechSquad Inc. - Ghidra GPT-5 MCP Server Installer${NC}"
echo "=============================================================="
echo -e "${YELLOW}Copyright (c) 2024 TechSquad Inc. - All Rights Reserved${NC}"
echo -e "${YELLOW}Coded by: TheStingR${NC}"
echo ""

# Check if user agrees to TechSquad terms
echo -e "${BOLD}${RED}⚖️  IMPORTANT LEGAL NOTICE:${NC}"
echo -e "${YELLOW}By proceeding, you acknowledge that:${NC}"
echo -e "${YELLOW}    - This is proprietary TechSquad Inc. software${NC}"
echo -e "${YELLOW}    - NOT FOR RESALE or unauthorized distribution${NC}"
echo -e "${YELLOW}    - Use requires proper TechSquad authorization${NC}"
echo -e "${YELLOW}    - Unauthorized use may result in legal action${NC}"
echo ""
read -p "Do you agree to these terms and have proper authorization? (yes/no): " AGREE

if [[ "$AGREE" != "yes" ]]; then
    echo -e "${RED}❌ Installation cancelled. Terms not accepted.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Terms accepted. Proceeding with TechSquad installation...${NC}"
echo ""

# System compatibility check
echo -e "${BLUE}🔍 Checking system compatibility...${NC}"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1,2)
if [[ -z "$PYTHON_VERSION" ]]; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.8 or later.${NC}"
    exit 1
elif [[ $(echo "$PYTHON_VERSION >= 3.8" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then
    echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
else
    echo -e "${RED}❌ Python $PYTHON_VERSION found, but 3.8+ required${NC}"
    exit 1
fi

# Check for pip
if ! command -v pip3 >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  pip3 not found. Attempting to install...${NC}"
    if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update && sudo apt-get install -y python3-pip
    elif command -v yum >/dev/null 2>&1; then
        sudo yum install -y python3-pip
    else
        echo -e "${RED}❌ Unable to install pip3. Please install manually.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ System compatibility check passed${NC}"
echo ""

# OpenAI API Key Configuration
echo -e "${BOLD}${BLUE}🔑 OpenAI API Key Configuration${NC}"
echo -e "${YELLOW}This MCP server requires an OpenAI API key for GPT-5/GPT-4o access.${NC}"
echo ""

# Check if API key already exists
EXISTING_KEY=""
if [[ -n "$OPENAI_API_KEY" ]]; then
    EXISTING_KEY="$OPENAI_API_KEY"
elif [[ -n "$CHATGPT_COOKIE" && "$CHATGPT_COOKIE" == sk-* ]]; then
    EXISTING_KEY="$CHATGPT_COOKIE"
fi

if [[ -n "$EXISTING_KEY" ]]; then
    echo -e "${GREEN}✅ OpenAI API key found in environment${NC}"
    echo -e "${YELLOW}Current key: ${EXISTING_KEY:0:10}...${NC}"
    read -p "Use existing key? (y/n): " USE_EXISTING
    
    if [[ "$USE_EXISTING" =~ ^[Yy]$ ]]; then
        API_KEY="$EXISTING_KEY"
    else
        echo ""
        read -p "Enter your OpenAI API key: " -s API_KEY
        echo ""
    fi
else
    echo -e "${YELLOW}No existing OpenAI API key found.${NC}"
    echo ""
    read -p "Enter your OpenAI API key: " -s API_KEY
    echo ""
fi

# Validate API key format
if [[ ! "$API_KEY" =~ ^sk-[A-Za-z0-9]{48,}$ ]]; then
    echo -e "${YELLOW}⚠️  Warning: API key format doesn't match expected OpenAI format${NC}"
    read -p "Continue anyway? (y/n): " CONTINUE
    if [[ ! "$CONTINUE" =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ Installation cancelled${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ API key configured${NC}"
echo ""

# Create installation directory
echo -e "${BLUE}📁 Creating TechSquad installation directory...${NC}"
mkdir -p "$INSTALL_DIR"
echo -e "${GREEN}✅ Directory created: $INSTALL_DIR${NC}"

# Copy TechSquad files
echo -e "${BLUE}📋 Installing TechSquad proprietary files...${NC}"

# List of files to copy
FILES=(
    "ghidra_gpt5_mcp.py"
    "run_ghidra_gpt5.sh"
    "test_ghidra_gpt5.py"
    "GHIDRA_GPT5_DEPLOYMENT_GUIDE.md"
    "COPYRIGHT.txt"
)

for file in "${FILES[@]}"; do
    if [[ -f "$SCRIPT_DIR/$file" ]]; then
        cp "$SCRIPT_DIR/$file" "$INSTALL_DIR/"
        echo -e "${GREEN}  ✅ Copied $file${NC}"
    else
        echo -e "${YELLOW}  ⚠️  Warning: $file not found${NC}"
    fi
done

# Make scripts executable
chmod +x "$INSTALL_DIR/run_ghidra_gpt5.sh"
chmod +x "$INSTALL_DIR/test_ghidra_gpt5.py"
chmod +x "$INSTALL_DIR/ghidra_gpt5_mcp.py"

echo -e "${GREEN}✅ Files installed and permissions set${NC}"

# Create Warp Terminal configuration
echo -e "${BLUE}🔧 Creating Warp Terminal configuration...${NC}"

# Detect Python path
PYTHON_PATH=$(which python3)
if command -v pipx >/dev/null 2>&1; then
    PIPX_PYTHON="/home/$USER/.local/share/pipx/venvs/mcp/bin/python"
    if [[ -f "$PIPX_PYTHON" ]]; then
        PYTHON_PATH="$PIPX_PYTHON"
    fi
fi

# Create Warp config
cat > "$INSTALL_DIR/ghidra_gpt5_warp_config.json" << EOF
{
  "mcpServers": {
    "techsquad-ghidra-gpt5": {
      "command": "$PYTHON_PATH",
      "args": ["$INSTALL_DIR/ghidra_gpt5_mcp.py"],
      "env": {
        "OPENAI_API_KEY": "$API_KEY",
        "GHIDRA_HEADLESS_PATH": "/opt/ghidra/support/analyzeHeadless",
        "GHIDRA_PROJECT_DIR": "$INSTALL_DIR/ghidra_projects",
        "PYTHONPATH": "$INSTALL_DIR"
      },
      "working_directory": "$INSTALL_DIR"
    }
  }
}
EOF

echo -e "${GREEN}✅ Warp configuration created with your API key${NC}"

# Install Python dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"

# Try pipx first
if command -v pipx >/dev/null 2>&1; then
    echo -e "${YELLOW}Using pipx for isolated installation...${NC}"
    pipx install mcp --force 2>/dev/null || true
    pipx inject mcp aiohttp 2>/dev/null || true
    echo -e "${GREEN}  ✅ Dependencies installed via pipx${NC}"
else
    echo -e "${YELLOW}Using pip3 for user installation...${NC}"
    pip3 install --user mcp aiohttp
    echo -e "${GREEN}  ✅ Dependencies installed via pip3${NC}"
fi

# Set up environment variables
echo -e "${BLUE}🌍 Setting up environment variables...${NC}"

# Determine shell config file
SHELL_CONFIG=""
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_CONFIG="$HOME/.bashrc"
else
    SHELL_CONFIG="$HOME/.profile"
fi

# Add API key to shell config
if ! grep -q "OPENAI_API_KEY" "$SHELL_CONFIG" 2>/dev/null; then
    echo "" >> "$SHELL_CONFIG"
    echo "# TechSquad Inc. - Ghidra GPT-5 MCP Server" >> "$SHELL_CONFIG"
    echo "export OPENAI_API_KEY=\"$API_KEY\"" >> "$SHELL_CONFIG"
    echo -e "${GREEN}✅ API key added to $SHELL_CONFIG${NC}"
else
    echo -e "${YELLOW}⚠️  API key already exists in $SHELL_CONFIG - not modified${NC}"
fi

# Test the installation
echo -e "${BLUE}🧪 Testing TechSquad installation...${NC}"

# Set temporary environment
export OPENAI_API_KEY="$API_KEY"
export PYTHONPATH="$INSTALL_DIR:$PYTHONPATH"

# Test import
cd "$INSTALL_DIR"
if python3 -c "import ghidra_gpt5_mcp; print('Import successful')" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ MCP server import test passed${NC}"
else
    echo -e "${YELLOW}⚠️  MCP server import test failed - dependencies may need manual attention${NC}"
fi

# Create project directories
mkdir -p "$INSTALL_DIR/ghidra_projects"
mkdir -p "$INSTALL_DIR/logs"

echo ""
echo -e "${BOLD}${GREEN}🎉 TechSquad Inc. Ghidra GPT-5 MCP Server installed successfully!${NC}"
echo ""
echo -e "${BOLD}📍 Installation Details:${NC}"
echo -e "${YELLOW}  Installation Directory: $INSTALL_DIR${NC}"
echo -e "${YELLOW}  Configuration File: $INSTALL_DIR/ghidra_gpt5_warp_config.json${NC}"
echo -e "${YELLOW}  API Key: Configured and saved${NC}"
echo -e "${YELLOW}  Documentation: $INSTALL_DIR/GHIDRA_GPT5_DEPLOYMENT_GUIDE.md${NC}"
echo -e "${YELLOW}  Copyright Info: $INSTALL_DIR/COPYRIGHT.txt${NC}"
echo ""
echo -e "${BOLD}🚀 Next Steps:${NC}"
echo -e "${GREEN}1. Restart your terminal to load environment variables${NC}"
echo -e "${GREEN}2. Test the installation:${NC}"
echo -e "${BLUE}   cd $INSTALL_DIR && ./test_ghidra_gpt5.py${NC}"
echo -e "${GREEN}3. Add to Warp Terminal:${NC}"
echo -e "${BLUE}   - Open Warp Terminal Settings${NC}"
echo -e "${BLUE}   - Go to Features → Agent Mode → MCP Servers${NC}"
echo -e "${BLUE}   - Click 'Add MCP Server'${NC}"
echo -e "${BLUE}   - Use the configuration from: $INSTALL_DIR/ghidra_gpt5_warp_config.json${NC}"
echo -e "${GREEN}4. Restart Warp Terminal${NC}"
echo ""
echo -e "${BOLD}🔧 Usage Examples:${NC}"
echo -e "${YELLOW}call_mcp_tool(\"ghidra_binary_analysis\", {\"binary_path\": \"/path/to/binary\"})${NC}"
echo -e "${YELLOW}call_mcp_tool(\"gpt5_reverse_engineering_query\", {\"query\": \"How to bypass ASLR?\"})${NC}"
echo ""
echo -e "${BOLD}⚖️  Legal Reminder:${NC}"
echo -e "${RED}This is TechSquad Inc. proprietary software.${NC}"
echo -e "${RED}Unauthorized distribution or resale is prohibited.${NC}"
echo ""
echo -e "${BOLD}${GREEN}Installation Complete! 🎯${NC}"