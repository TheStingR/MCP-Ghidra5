#!/bin/bash
# MCP-Ghidra5 Release Preparation Script v1.1.0
# Copyright (c) 2024-2025 TechSquad Inc. - All Rights Reserved

echo "🚀 MCP-Ghidra5 v1.1.0 Release Preparation"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "MCP-Ghidra5/ghidra_gpt5_mcp.py" ]; then
    echo "❌ Error: Please run this script from the MCP-Ghidra5 repository root directory"
    exit 1
fi

echo "📋 Pre-Release Checklist:"
echo "------------------------"

# Check version consistency
echo -n "🔍 Checking version consistency... "
if grep -q "Version: 1.1.0" MCP-Ghidra5/ghidra_gpt5_mcp.py && \
   grep -q "__version__ = \"1.1.0\"" MCP-Ghidra5/ghidra_gpt5_mcp.py && \
   grep -q "version-1.1.0-blue" README.md && \
   grep -q "Version 1.1.0" CHANGELOG.md; then
    echo "✅ PASSED"
else
    echo "❌ FAILED - Version inconsistency detected"
    exit 1
fi

# Check critical files exist
echo -n "📁 Checking critical files... "
critical_files=(
    "MCP-Ghidra5/ghidra_gpt5_mcp.py"
    "MCP-Ghidra5/ai_providers.py" 
    "MCP-Ghidra5/security_utils.py"
    "README.md"
    "CHANGELOG.md"
)

for file in "${critical_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ FAILED - Missing file: $file"
        exit 1
    fi
done
echo "✅ PASSED"

# Run smoke tests
echo -n "🧪 Running smoke tests... "
cd MCP-Ghidra5
if python smoke_test_complete.py > /dev/null 2>&1; then
    echo "✅ PASSED"
else
    echo "❌ FAILED - Smoke tests failed"
    exit 1
fi
cd ..

echo ""
echo "🎯 Release Summary:"
echo "==================="
echo "📦 Package: MCP-Ghidra5"
echo "🏷️  Version: 1.1.0" 
echo "📅 Date: January 19, 2025"
echo "🚀 Type: Major Feature Release"
echo ""
echo "🌟 Key Features in v1.1.0:"
echo "- 🤖 Multi-Model AI Integration (7 providers)"
echo "- 🔄 Intelligent Fallback System"
echo "- 💰 Cost Optimization (30-50% savings)"
echo "- 🔒 Local LLM Support (Ollama)"
echo "- 📊 Usage Analytics & Monitoring"
echo "- 🛡️ Enhanced Security Controls"
echo "- ⚡ Performance Improvements"
echo ""

echo "✅ All pre-release checks passed!"
echo ""
echo "🚀 Next Steps:"
echo "1. Review CHANGELOG.md and README.md"
echo "2. Commit all changes to git"
echo "3. Create and push v1.1.0 tag"
echo "4. Create GitHub release with release notes"
echo ""
echo "📝 Suggested git commands:"
echo "git add ."
echo "git commit -m \"Release v1.1.0: Major Multi-Model AI Integration\""
echo "git tag -a v1.1.0 -m \"v1.1.0: Multi-Model AI Support with 7 providers\""
echo "git push origin main"
echo "git push origin v1.1.0"
echo ""
echo "🎉 MCP-Ghidra5 v1.1.0 is ready for release!"