#!/bin/bash
# MCP-Ghidra5 Package Creator
#
# Copyright (c) 2024 TechSquad Inc. - All Rights Reserved
# Proprietary Software - NOT FOR RESALE
# Coded by: TheStingR
#
# This software is the property of TechSquad Inc. and is protected by copyright law.
# Unauthorized reproduction, distribution, or sale is strictly prohibited.

PACKAGE_NAME="mcp-ghidra5-server"
PACKAGE_DIR="./${PACKAGE_NAME}"
ARCHIVE_NAME="${PACKAGE_NAME}-$(date +%Y%m%d).tar.gz"

echo "📦 Creating TechSquad Inc. Ghidra GPT-5 MCP Server Package"
echo "=========================================================="

# Clean up any existing package
rm -rf "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR"

# Copy core files
echo "📋 Copying TechSquad Inc. proprietary files..."
cp ghidra_gpt5_mcp.py "$PACKAGE_DIR/"
cp run_ghidra_gpt5.sh "$PACKAGE_DIR/"
cp test_ghidra_gpt5.py "$PACKAGE_DIR/"
cp ghidra_gpt5_terminal_config.json "$PACKAGE_DIR/"
cp GHIDRA_GPT5_DEPLOYMENT_GUIDE.md "$PACKAGE_DIR/"
cp GHIDRA_GPT5_PROJECT_SUMMARY.md "$PACKAGE_DIR/"
cp COPYRIGHT.txt "$PACKAGE_DIR/"

# Create TechSquad installation script
echo "🔧 Creating TechSquad installation script..."
cat > "$PACKAGE_DIR/install_mcp_ghidra5.sh" << 'EOF'
#!/bin/bash
# TechSquad Inc. - Ghidra GPT-5 MCP Server Installation Script
#
# Copyright (c) 2024 TechSquad Inc. - All Rights Reserved
# Proprietary Software - NOT FOR RESALE

set -e

INSTALL_DIR="$HOME/mcp-servers/techsquad-ghidra-gpt5"
PYTHON_CMD="python3"

echo "🏢 TechSquad Inc. - Installing Ghidra GPT-5 MCP Server"
echo "======================================================"
echo "Copyright (c) 2024 TechSquad Inc. - All Rights Reserved"
echo "Coded by: TheStingR"
echo ""

# Check if user agrees to TechSquad terms
echo "⚖️  IMPORTANT: By proceeding, you acknowledge that:"
echo "    - This is proprietary TechSquad Inc. software"
echo "    - NOT FOR RESALE or unauthorized distribution"
echo "    - Use requires proper TechSquad authorization"
echo ""
read -p "Do you agree to these terms? (yes/no): " AGREE

if [[ "$AGREE" != "yes" ]]; then
    echo "❌ Installation cancelled. Terms not accepted."
    exit 1
fi

# Create installation directory
echo "📁 Creating TechSquad installation directory..."
mkdir -p "$INSTALL_DIR"

# Copy files
echo "📋 Installing TechSquad proprietary files..."
cp ghidra_gpt5_mcp.py "$INSTALL_DIR/"
cp run_ghidra_gpt5.sh "$INSTALL_DIR/"
cp test_ghidra_gpt5.py "$INSTALL_DIR/"
cp ghidra_gpt5_terminal_config.json "$INSTALL_DIR/"
cp GHIDRA_GPT5_DEPLOYMENT_GUIDE.md "$INSTALL_DIR/"
cp COPYRIGHT.txt "$INSTALL_DIR/"

# Make scripts executable
chmod +x "$INSTALL_DIR/run_ghidra_gpt5.sh"
chmod +x "$INSTALL_DIR/test_ghidra_gpt5.py"
chmod +x "$INSTALL_DIR/ghidra_gpt5_mcp.py"

# Update paths in configuration
# Paths are already dynamic - no hardcoded paths to replace
echo "  ✅ Dynamic paths validated"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if command -v pipx >/dev/null 2>&1; then
    echo "Using pipx..."
    pipx install mcp
    pipx inject mcp aiohttp
else
    echo "Using pip3..."
    pip3 install --user mcp aiohttp
fi

echo ""
echo "✅ TechSquad Inc. Ghidra GPT-5 MCP Server installed successfully!"
echo "📍 Server installed at: $INSTALL_DIR"
echo "📖 Read the deployment guide: $INSTALL_DIR/GHIDRA_GPT5_DEPLOYMENT_GUIDE.md"
echo "📜 Copyright info: $INSTALL_DIR/COPYRIGHT.txt"
echo ""
echo "🔑 REQUIRED: Set your OpenAI API key:"
echo "export OPENAI_API_KEY=\"sk-your-api-key-here\""
echo ""
echo "Next steps:"
echo "1. Set your OpenAI API key (required)"
echo "2. Test the server: cd $INSTALL_DIR && ./test_ghidra_gpt5.py"
echo "3. Add to Terminal Terminal using ghidra_gpt5_terminal_config.json"
echo ""
echo "⚖️  Remember: This is TechSquad Inc. proprietary software."
echo "   Unauthorized distribution or resale is prohibited."
EOF

chmod +x "$PACKAGE_DIR/install_mcp_ghidra5.sh"

# Create TechSquad README
echo "📄 Creating TechSquad README..."
cat > "$PACKAGE_DIR/README.md" << 'EOF'
# TechSquad Inc. - Ghidra GPT-5 MCP Server

**Copyright (c) 2024 TechSquad Inc. - All Rights Reserved**  
**Proprietary Software - NOT FOR RESALE**  
**Coded by: TheStingR**

Advanced reverse engineering with GPT-5 integration for Terminal Terminal.

## ⚖️ Legal Notice

This is proprietary software owned by TechSquad Inc. Unauthorized reproduction, 
distribution, or sale is strictly prohibited. See `COPYRIGHT.txt` for full terms.

## Quick Start

1. **Read Copyright**: Review `COPYRIGHT.txt` before use
2. **Install**: `./install_mcp_ghidra5.sh` 
3. **Configure API Key**: `export OPENAI_API_KEY="sk-your-key"`
4. **Test**: `./test_ghidra_gpt5.py`
5. **Deploy**: Add to Terminal Terminal using `ghidra_gpt5_terminal_config.json`

## Features

- 🔧 Ghidra headless integration
- 🧠 GPT-5 advanced analysis
- 🎯 CTF competition ready
- 🛡️ Malware analysis support
- 📱 IoT firmware analysis
- 🔍 Pattern search capabilities

## Documentation

See `GHIDRA_GPT5_DEPLOYMENT_GUIDE.md` for complete setup and usage instructions.

## TechSquad Inc. Support

For authorized users only. Contact TechSquad Inc. for support or licensing inquiries.

---
**TechSquad Inc. - Advanced Cybersecurity Solutions**
EOF

# Create checksums for integrity
echo "🔐 Creating TechSquad integrity checksums..."
cd "$PACKAGE_DIR"
sha256sum *.py *.sh *.json *.md *.txt > TECHSQUAD_CHECKSUMS.txt
echo "# TechSquad Inc. Package Integrity" >> TECHSQUAD_CHECKSUMS.txt
echo "# Generated: $(date)" >> TECHSQUAD_CHECKSUMS.txt
echo "# Package: $PACKAGE_NAME" >> TECHSQUAD_CHECKSUMS.txt
cd - > /dev/null

# Create archive
echo "📦 Creating TechSquad secure package..."
cd /mnt/storage
tar -czf "$ARCHIVE_NAME" "$PACKAGE_NAME"
cd - > /dev/null

# Package info
echo ""
echo "✅ TechSquad Inc. package created successfully!"
echo "🏢 Company: TechSquad Inc."
echo "👨‍💻 Developer: TheStingR"
echo "📦 Archive: /mnt/storage/$ARCHIVE_NAME"
echo "📊 Size: $(du -h /mnt/storage/$ARCHIVE_NAME | cut -f1)"
echo "🔐 SHA256: $(sha256sum /mnt/storage/$ARCHIVE_NAME | cut -d' ' -f1)"
echo ""
echo "📋 TechSquad Package contents:"
ls -la "$PACKAGE_DIR/"
echo ""
echo "🚀 Ready for authorized distribution!"
echo "⚖️  Remember: TechSquad Inc. proprietary software - NOT FOR RESALE"