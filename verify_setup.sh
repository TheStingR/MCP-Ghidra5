#!/bin/bash
# TechSquad Inc. - Setup Verification and Troubleshooting Script
#
# Copyright (c) 2024 TechSquad Inc. - All Rights Reserved
# Proprietary Software - NOT FOR RESALE
# Coded by: TheStingR
#
# This software is the property of TechSquad Inc. and is protected by copyright law.
# Unauthorized reproduction, distribution, or sale is strictly prohibited.

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BOLD}${BLUE}🔍 TechSquad Inc. - Setup Verification${NC}"
echo "========================================"
echo -e "${YELLOW}Copyright (c) 2024 TechSquad Inc. - All Rights Reserved${NC}"
echo ""

ISSUES_FOUND=0

# Check 1: Required files
echo -e "${BLUE}📋 Checking TechSquad files...${NC}"
REQUIRED_FILES=(
    "ghidra_gpt5_mcp.py"
    "run_ghidra_gpt5.sh" 
    "test_ghidra_gpt5.py"
    "install_techsquad.sh"
    "COPYRIGHT.txt"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [[ -f "$SCRIPT_DIR/$file" ]]; then
        echo -e "${GREEN}  ✅ $file${NC}"
    else
        echo -e "${RED}  ❌ $file (MISSING)${NC}"
        ((ISSUES_FOUND++))
    fi
done

# Check 2: Python environment
echo -e "\n${BLUE}🐍 Checking Python environment...${NC}"

if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version 2>/dev/null | cut -d' ' -f2)
    echo -e "${GREEN}  ✅ Python 3 found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}  ❌ Python 3 not found${NC}"
    ((ISSUES_FOUND++))
fi

if command -v pip3 >/dev/null 2>&1; then
    echo -e "${GREEN}  ✅ pip3 available${NC}"
else
    echo -e "${RED}  ❌ pip3 not found${NC}"
    ((ISSUES_FOUND++))
fi

# Check 3: Python packages
echo -e "\n${BLUE}📦 Checking Python packages...${NC}"

PYTHON_PACKAGES=("mcp" "aiohttp")
for package in "${PYTHON_PACKAGES[@]}"; do
    if python3 -c "import $package" >/dev/null 2>&1; then
        echo -e "${GREEN}  ✅ $package installed${NC}"
    else
        echo -e "${RED}  ❌ $package missing${NC}"
        echo -e "${YELLOW}     Install with: pip3 install --user $package${NC}"
        ((ISSUES_FOUND++))
    fi
done

# Check 4: OpenAI API Key
echo -e "\n${BLUE}🔑 Checking OpenAI API Key...${NC}"

API_KEY=""
if [[ -n "$OPENAI_API_KEY" ]]; then
    API_KEY="$OPENAI_API_KEY"
    echo -e "${GREEN}  ✅ OPENAI_API_KEY found in environment${NC}"
elif [[ -n "$CHATGPT_COOKIE" && "$CHATGPT_COOKIE" == sk-* ]]; then
    API_KEY="$CHATGPT_COOKIE"
    echo -e "${GREEN}  ✅ API key found in CHATGPT_COOKIE${NC}"
else
    echo -e "${RED}  ❌ OpenAI API key not found${NC}"
    echo -e "${YELLOW}     Set with: export OPENAI_API_KEY=\"sk-your-key\"${NC}"
    ((ISSUES_FOUND++))
fi

if [[ -n "$API_KEY" ]]; then
    if [[ "$API_KEY" =~ ^sk-[A-Za-z0-9]{48,}$ ]]; then
        echo -e "${GREEN}  ✅ API key format looks correct${NC}"
    else
        echo -e "${YELLOW}  ⚠️  API key format may be incorrect${NC}"
    fi
fi

# Check 5: Ghidra (optional)
echo -e "\n${BLUE}🔧 Checking Ghidra installation (optional)...${NC}"

GHIDRA_PATHS=(
    "/opt/ghidra/support/analyzeHeadless"
    "/usr/local/ghidra/support/analyzeHeadless"
    "$GHIDRA_HEADLESS_PATH"
)

GHIDRA_FOUND=false
for path in "${GHIDRA_PATHS[@]}"; do
    if [[ -n "$path" && -f "$path" ]]; then
        echo -e "${GREEN}  ✅ Ghidra found: $path${NC}"
        GHIDRA_FOUND=true
        break
    fi
done

if [[ "$GHIDRA_FOUND" == false ]]; then
    echo -e "${YELLOW}  ⚠️  Ghidra not found (optional for some features)${NC}"
    echo -e "${YELLOW}     Set with: export GHIDRA_HEADLESS_PATH=/path/to/analyzeHeadless${NC}"
fi

# Check 6: File permissions
echo -e "\n${BLUE}🔒 Checking file permissions...${NC}"

EXECUTABLE_FILES=(
    "ghidra_gpt5_mcp.py"
    "run_ghidra_gpt5.sh"
    "test_ghidra_gpt5.py"
    "install_techsquad.sh"
    "generate_warp_config.sh"
    "verify_setup.sh"
)

for file in "${EXECUTABLE_FILES[@]}"; do
    if [[ -f "$SCRIPT_DIR/$file" ]]; then
        if [[ -x "$SCRIPT_DIR/$file" ]]; then
            echo -e "${GREEN}  ✅ $file (executable)${NC}"
        else
            echo -e "${YELLOW}  ⚠️  $file (not executable)${NC}"
            echo -e "${YELLOW}     Fix with: chmod +x $SCRIPT_DIR/$file${NC}"
        fi
    fi
done

# Check 7: Test MCP server import
echo -e "\n${BLUE}🧪 Testing MCP server import...${NC}"

cd "$SCRIPT_DIR"
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

if python3 -c "import ghidra_gpt5_mcp; print('Success')" >/dev/null 2>&1; then
    echo -e "${GREEN}  ✅ MCP server imports successfully${NC}"
else
    echo -e "${RED}  ❌ MCP server import failed${NC}"
    echo -e "${YELLOW}     Check Python dependencies and paths${NC}"
    ((ISSUES_FOUND++))
fi

# Summary
echo ""
echo -e "${BOLD}📊 Verification Summary:${NC}"
echo "========================"

if [[ $ISSUES_FOUND -eq 0 ]]; then
    echo -e "${BOLD}${GREEN}🎉 All checks passed! TechSquad setup is ready.${NC}"
    echo ""
    echo -e "${BOLD}🚀 Next steps:${NC}"
    echo -e "${GREEN}1. Run: ./test_ghidra_gpt5.py (to test functionality)${NC}"
    echo -e "${GREEN}2. Run: ./generate_warp_config.sh (to create Warp config)${NC}"
    echo -e "${GREEN}3. Add the configuration to Warp Terminal${NC}"
    echo -e "${GREEN}4. Restart Warp Terminal${NC}"
else
    echo -e "${BOLD}${RED}⚠️  Found $ISSUES_FOUND issue(s) that need attention.${NC}"
    echo ""
    echo -e "${BOLD}🔧 Troubleshooting:${NC}"
    echo -e "${YELLOW}1. Install missing Python packages: pip3 install --user mcp aiohttp${NC}"
    echo -e "${YELLOW}2. Set OpenAI API key: export OPENAI_API_KEY=\"sk-your-key\"${NC}"
    echo -e "${YELLOW}3. Fix file permissions: chmod +x *.sh *.py${NC}"
    echo -e "${YELLOW}4. Re-run this script to verify fixes${NC}"
fi

echo ""
echo -e "${BOLD}⚖️  TechSquad Inc. - All Rights Reserved${NC}"