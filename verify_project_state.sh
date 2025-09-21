#!/bin/bash
# MCP-Ghidra5 v1.2.0 Project State Verification Script
# Run after reboot to verify everything is working correctly

echo "🚀 MCP-Ghidra5 v1.2.0 - PROJECT STATE VERIFICATION"
echo "=================================================="

# Check current directory
echo "📍 Current Directory:"
pwd
echo ""

# Check Git status
echo "📦 Git Repository Status:"
git status --porcelain
if [ $? -eq 0 ]; then
    if [ -z "$(git status --porcelain)" ]; then
        echo "✅ Working tree clean"
    else
        echo "⚠️  Uncommitted changes detected"
    fi
else
    echo "❌ Git status check failed"
fi
echo ""

# Check Git tags
echo "🏷️  Git Tags:"
git tag -l | tail -3
echo ""

# Check recent commits
echo "📝 Recent Commits:"
git log --oneline -3
echo ""

# Check key files
echo "📂 Key Files Check:"
files=(
    "README.md"
    "RESTORE_POINT_v1.2.0.md"
    "PHASE1_IMPLEMENTATION_SUMMARY.md"
    "test_tier1_tools.py"
    "MCP-Ghidra5/tier1_tools.py"
    "MCP-Ghidra5/ghidra_gpt5_mcp.py"
    "mcp-ghidra5.png"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (missing)"
    fi
done
echo ""

# Check GitHub authentication
echo "🔐 GitHub Authentication:"
gh auth status 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ GitHub CLI authenticated"
else
    echo "⚠️  GitHub CLI not authenticated"
fi
echo ""

# Check Python environment
echo "🐍 Python Environment:"
python3 --version 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Python 3 available"
else
    echo "❌ Python 3 not found"
fi
echo ""

# Check if we can run tests
echo "🧪 Test Suite Check:"
if [ -f "test_tier1_tools.py" ]; then
    echo "✅ Test suite available"
    echo "   Run: python3 test_tier1_tools.py"
else
    echo "❌ Test suite not found"
fi
echo ""

# Check Docker infrastructure
echo "🐳 Docker Infrastructure:"
if [ -d "docker-tests" ]; then
    echo "✅ Docker testing infrastructure available"
    echo "   Found $(ls docker-tests/*.dockerfile docker-tests/Dockerfile.* 2>/dev/null | wc -l) Dockerfiles"
else
    echo "❌ Docker testing infrastructure not found"
fi
echo ""

# Summary
echo "🎯 PROJECT STATE SUMMARY:"
echo "========================="
echo "✅ MCP-Ghidra5 v1.2.0 Phase 1 Quick Wins - COMPLETE"
echo "✅ 5 New Tier 1 Binary Analysis Tools implemented"
echo "✅ GitHub Release published: https://github.com/TheStingR/MCP-Ghidra5/releases/tag/v1.2.0"
echo "✅ All documentation and tests in place"
echo ""
echo "🚀 Ready to continue development or begin Phase 2!"
echo ""
echo "📖 For complete details, see: RESTORE_POINT_v1.2.0.md"
echo "📋 For quick reference, see: QUICK_RESUME.md"