#!/bin/bash
# Create deployment package for Ghidra GPT-5 MCP Server
#
# Copyright (c) 2024 TechSquad Inc. - All Rights Reserved
# Proprietary Software - NOT FOR RESALE
# Coded by: TheStingR
#
# This software is the property of TechSquad Inc. and is protected by copyright law.
# Unauthorized reproduction, distribution, or sale is strictly prohibited.

PACKAGE_NAME="ghidra-gpt5-mcp-server"
PACKAGE_DIR="/tmp/${PACKAGE_NAME}"
ARCHIVE_NAME="${PACKAGE_NAME}-$(date +%Y%m%d).tar.gz"

echo "📦 Creating Ghidra GPT-5 MCP Server Deployment Package"
echo "======================================================="

# Clean up any existing package
rm -rf "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR"

# Copy core files
echo "📋 Copying core files..."
cp ghidra_gpt5_mcp.py "$PACKAGE_DIR/"
cp run_ghidra_gpt5.sh "$PACKAGE_DIR/"
cp test_ghidra_gpt5.py "$PACKAGE_DIR/"
cp ghidra_gpt5_warp_config.json "$PACKAGE_DIR/"
cp GHIDRA_GPT5_DEPLOYMENT_GUIDE.md "$PACKAGE_DIR/"

# Create installation script
echo "🔧 Creating installation script..."
cat > "$PACKAGE_DIR/install.sh" << 'EOF'
#!/bin/bash
# Ghidra GPT-5 MCP Server Installation Script

set -e

INSTALL_DIR="$HOME/mcp-servers/ghidra-gpt5"
# TechSquad Inc. Storage Location
TECHSQUAD_DIR="/mnt/storage/MCP-Ghidra5"
PYTHON_CMD="python3"

echo "🚀 Installing Ghidra GPT-5 MCP Server"
echo "====================================="

# Create installation directory
echo "📁 Creating installation directory..."
mkdir -p "$INSTALL_DIR"

# Copy files
echo "📋 Copying server files..."
cp ghidra_gpt5_mcp.py "$INSTALL_DIR/"
cp run_ghidra_gpt5.sh "$INSTALL_DIR/"
cp test_ghidra_gpt5.py "$INSTALL_DIR/"
cp ghidra_gpt5_warp_config.json "$INSTALL_DIR/"
cp GHIDRA_GPT5_DEPLOYMENT_GUIDE.md "$INSTALL_DIR/"

# Make scripts executable
chmod +x "$INSTALL_DIR/run_ghidra_gpt5.sh"
chmod +x "$INSTALL_DIR/test_ghidra_gpt5.py"
chmod +x "$INSTALL_DIR/ghidra_gpt5_mcp.py"

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

# Environment setup
echo "🔧 Environment setup..."
echo "Please set your OpenAI API key:"
echo "export OPENAI_API_KEY=\"sk-your-api-key-here\""
echo ""
echo "Add to ~/.bashrc or ~/.zshrc for persistence"

echo ""
echo "✅ Installation complete!"
echo "📍 Server installed at: $INSTALL_DIR"
echo "📖 Read the deployment guide: $INSTALL_DIR/GHIDRA_GPT5_DEPLOYMENT_GUIDE.md"
echo ""
echo "Next steps:"
echo "1. Set your OpenAI API key: export OPENAI_API_KEY=\"sk-...\""
echo "2. Test the server: cd $INSTALL_DIR && ./test_ghidra_gpt5.py"
echo "3. Add to Warp Terminal using ghidra_gpt5_warp_config.json"
EOF

chmod +x "$PACKAGE_DIR/install.sh"

# Create README
echo "📄 Creating README..."
cat > "$PACKAGE_DIR/README.md" << 'EOF'
# Ghidra GPT-5 MCP Server

**Copyright (c) 2024 TechSquad Inc. - All Rights Reserved**  
**Proprietary Software - NOT FOR RESALE**  
**Coded by: TheStingR**  

Advanced reverse engineering with GPT-5 integration for Warp Terminal.

## Quick Start

1. **Install**: `./install.sh`
2. **Configure API Key**: `export OPENAI_API_KEY="sk-your-key"`
3. **Test**: `./test_ghidra_gpt5.py`
4. **Deploy**: Add to Warp Terminal using `ghidra_gpt5_warp_config.json`

## Features

- 🔧 Ghidra headless integration
- 🧠 GPT-5 advanced analysis
- 🎯 CTF competition ready
- 🛡️ Malware analysis support
- 📱 IoT firmware analysis
- 🔍 Pattern search capabilities

## Documentation

See `GHIDRA_GPT5_DEPLOYMENT_GUIDE.md` for complete setup and usage instructions.

## Support

For issues or questions, contact your deployment team.
EOF

# Create checksums
echo "🔐 Creating checksums..."
cd "$PACKAGE_DIR"
sha256sum *.py *.sh *.json *.md > checksums.txt
cd - > /dev/null

# Create archive
echo "📦 Creating archive..."
cd /tmp
tar -czf "$ARCHIVE_NAME" "$PACKAGE_NAME"
cd - > /dev/null

# Package info
echo ""
echo "✅ Package created successfully!"
echo "📦 Archive: /tmp/$ARCHIVE_NAME"
echo "📊 Size: $(du -h /tmp/$ARCHIVE_NAME | cut -f1)"
echo "🔐 SHA256: $(sha256sum /tmp/$ARCHIVE_NAME | cut -d' ' -f1)"
echo ""
echo "📋 Package contents:"
ls -la "$PACKAGE_DIR/"
echo ""
echo "🚀 Ready to send to remote pentester!"
echo "💡 They can extract and run: ./install.sh"