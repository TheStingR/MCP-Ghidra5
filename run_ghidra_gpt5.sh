#!/bin/bash
# Ghidra GPT-5 MCP Server Startup Script
#
# Copyright (c) 2024 TechSquad Inc. - All Rights Reserved
# Proprietary Software - NOT FOR RESALE
# Coded by: TheStingR
#
# This software is the property of TechSquad Inc. and is protected by copyright law.
# Unauthorized reproduction, distribution, or sale is strictly prohibited.

# Configuration - Dynamic paths based on script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_SERVER_PATH="$SCRIPT_DIR/ghidra_gpt5_mcp.py"
LOG_FILE="$SCRIPT_DIR/ghidra_gpt5_mcp.log"
PYTHON_ENV="${PYTHON_ENV:-python3}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Ghidra GPT-5 MCP Server Startup${NC}"
echo "================================================"

# Check dependencies
check_dependency() {
    local dep=$1
    local path=$2
    
    if [[ -n "$path" && -f "$path" ]]; then
        echo -e "${GREEN}✅ $dep found: $path${NC}"
        return 0
    elif command -v "$dep" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $dep found in PATH${NC}"
        return 0
    else
        echo -e "${RED}❌ $dep not found${NC}"
        return 1
    fi
}

# Dependency checks
echo -e "${YELLOW}Checking dependencies...${NC}"

# Python environment
if [[ -f "$PYTHON_ENV" ]]; then
    echo -e "${GREEN}✅ Python environment: $PYTHON_ENV${NC}"
else
    echo -e "${YELLOW}⚠️  Custom Python env not found, using system python3${NC}"
    PYTHON_ENV=$(which python3)
fi

# OpenAI API Key
if [[ -n "$OPENAI_API_KEY" ]]; then
    echo -e "${GREEN}✅ OpenAI API key configured${NC}"
elif [[ -n "$CHATGPT_COOKIE" && "$CHATGPT_COOKIE" == sk-* ]]; then
    echo -e "${GREEN}✅ OpenAI API key found in CHATGPT_COOKIE${NC}"
    export OPENAI_API_KEY="$CHATGPT_COOKIE"
else
    echo -e "${RED}❌ OpenAI API key not found${NC}"
    echo -e "${YELLOW}💡 Set OPENAI_API_KEY environment variable${NC}"
    exit 1
fi

# Ghidra
if [[ -n "$GHIDRA_HEADLESS_PATH" && -f "$GHIDRA_HEADLESS_PATH" ]]; then
    echo -e "${GREEN}✅ Ghidra headless: $GHIDRA_HEADLESS_PATH${NC}"
elif [[ -f "/opt/ghidra/support/analyzeHeadless" ]]; then
    echo -e "${GREEN}✅ Ghidra found at default location${NC}"
    export GHIDRA_HEADLESS_PATH="/opt/ghidra/support/analyzeHeadless"
else
    echo -e "${YELLOW}⚠️  Ghidra not found - binary analysis will be limited${NC}"
    echo -e "${YELLOW}💡 Install Ghidra or set GHIDRA_HEADLESS_PATH${NC}"
fi

# MCP Python packages
echo -e "${YELLOW}Checking Python packages...${NC}"
if $PYTHON_ENV -c "import mcp, aiohttp" 2>/dev/null; then
    echo -e "${GREEN}✅ MCP packages available${NC}"
else
    echo -e "${RED}❌ MCP packages missing${NC}"
    echo -e "${YELLOW}💡 Install with: $PYTHON_ENV -m pip install mcp aiohttp${NC}"
    exit 1
fi

# Prepare environment
echo -e "${YELLOW}Preparing runtime environment...${NC}"

# Create Ghidra project directory
GHIDRA_PROJECT_DIR="${GHIDRA_PROJECT_DIR:-/tmp/ghidra_projects}"
mkdir -p "$GHIDRA_PROJECT_DIR"
echo -e "${GREEN}✅ Ghidra project directory: $GHIDRA_PROJECT_DIR${NC}"

# Export environment variables - Dynamic paths
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"
export GHIDRA_PROJECT_DIR="${GHIDRA_PROJECT_DIR:-$SCRIPT_DIR/ghidra_projects}"

echo ""
echo -e "${BLUE}🚀 Starting Ghidra GPT-5 MCP Server...${NC}"
echo -e "${YELLOW}Log file: $LOG_FILE${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo "================================================"

# Start the server
exec $PYTHON_ENV "$MCP_SERVER_PATH" 2>&1 | tee "$LOG_FILE"