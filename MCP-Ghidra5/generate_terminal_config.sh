#!/bin/bash
# TechSquad Inc. - Terminal Terminal Configuration Generator
#
# Copyright (c) 2024 TechSquad Inc. - All Rights Reserved
# Proprietary Software - NOT FOR RESALE
# Coded by: TheStingR
#
# This software is the property of TechSquad Inc. and is protected by copyright law.
# Unauthorized reproduction, distribution, or sale is strictly prohibited.

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BOLD}${BLUE}🔧 TechSquad Inc. - Terminal Configuration Generator${NC}"
echo "================================================="
echo -e "${YELLOW}Copyright (c) 2024 TechSquad Inc. - All Rights Reserved${NC}"
echo ""

# Check if OpenAI API key is available
API_KEY=""
if [[ -n "$OPENAI_API_KEY" ]]; then
    API_KEY="$OPENAI_API_KEY"
elif [[ -n "$CHATGPT_COOKIE" && "$CHATGPT_COOKIE" == sk-* ]]; then
    API_KEY="$CHATGPT_COOKIE"
else
    echo -e "${YELLOW}⚠️  OpenAI API key not found in environment${NC}"
    read -p "Enter your OpenAI API key: " -s API_KEY
    echo ""
fi

# Detect Python path
PYTHON_PATH=$(which python3)
if command -v pipx >/dev/null 2>&1; then
    PIPX_PYTHON="$HOME/.local/share/pipx/venvs/mcp/bin/python"
    if [[ -f "$PIPX_PYTHON" ]]; then
        PYTHON_PATH="$PIPX_PYTHON"
        echo -e "${GREEN}✅ Using pipx Python environment${NC}"
    fi
fi

# Generate configuration
CONFIG_FILE="$SCRIPT_DIR/ghidra_gpt5_terminal_config.json"

echo -e "${BLUE}📝 Generating Terminal Terminal configuration...${NC}"

cat > "$CONFIG_FILE" << EOF
{
  "mcpServers": {
    "techsquad-ghidra-gpt5": {
      "command": "$PYTHON_PATH",
      "args": ["$SCRIPT_DIR/ghidra_gpt5_mcp.py"],
      "env": {
        "OPENAI_API_KEY": "$API_KEY",
        "GHIDRA_HEADLESS_PATH": "/opt/ghidra/support/analyzeHeadless",
        "GHIDRA_PROJECT_DIR": "$SCRIPT_DIR/ghidra_projects",
        "PYTHONPATH": "$SCRIPT_DIR"
      },
      "working_directory": "$SCRIPT_DIR"
    }
  }
}
EOF

echo -e "${GREEN}✅ Configuration generated: $CONFIG_FILE${NC}"
echo ""
echo -e "${BOLD}🚀 How to use this configuration:${NC}"
echo -e "${YELLOW}1. Open Terminal Terminal Settings${NC}"
echo -e "${YELLOW}2. Go to Features → Agent Mode → MCP Servers${NC}"
echo -e "${YELLOW}3. Click 'Add MCP Server'${NC}"
echo -e "${YELLOW}4. Copy the contents from: $CONFIG_FILE${NC}"
echo -e "${YELLOW}5. Paste into the configuration field${NC}"
echo -e "${YELLOW}6. Save and restart Terminal Terminal${NC}"
echo ""
echo -e "${BOLD}📋 Configuration Details:${NC}"
echo -e "${GREEN}  Server Name: techsquad-ghidra-gpt5${NC}"
echo -e "${GREEN}  Python Path: $PYTHON_PATH${NC}"
echo -e "${GREEN}  Working Directory: $SCRIPT_DIR${NC}"
echo -e "${GREEN}  API Key: Configured${NC}"
echo ""
echo -e "${BOLD}${GREEN}Configuration ready! 🎯${NC}"