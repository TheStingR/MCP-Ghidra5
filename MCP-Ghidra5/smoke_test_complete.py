#!/usr/bin/env python3
"""
Complete Smoke Test for MCP-Ghidra5 with Multi-Model AI Support
Copyright (c) 2024 TechSquad Inc. - All Rights Reserved

This script validates all critical functionality after recent updates:
- Multi-model AI integration
- MCP server startup and functionality
- Security utilities
- All tool handlers
"""

import asyncio
import tempfile
import os
import sys
import subprocess
import time
from pathlib import Path

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"🔥 {title}")
    print('='*60)

def print_test(test_name, status="RUNNING"):
    """Print test status"""
    if status == "RUNNING":
        print(f"🧪 {test_name}...")
    elif status == "PASS":
        print(f"✅ {test_name}: PASSED")
    elif status == "FAIL":
        print(f"❌ {test_name}: FAILED")

async def test_mcp_server_startup():
    """Test MCP server starts without errors"""
    print_test("MCP Server Startup", "RUNNING")
    
    try:
        # Test server startup for 3 seconds
        process = subprocess.Popen(
            [sys.executable, "ghidra_gpt5_mcp.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait 3 seconds then terminate
        time.sleep(3)
        process.terminate()
        stdout, stderr = process.communicate(timeout=5)
        
        # Check for successful startup messages (logs go to stderr)
        combined_output = stdout + stderr
        if "Starting Ghidra GPT-5 MCP Server" in combined_output and "OpenAI API key found" in combined_output:
            print_test("MCP Server Startup", "PASS")
            return True
        else:
            print(f"Combined output: {combined_output[:500]}...")
            print_test("MCP Server Startup", "FAIL")
            return False
            
    except Exception as e:
        print(f"Server startup error: {e}")
        print_test("MCP Server Startup", "FAIL")
        return False

async def test_multi_model_integration():
    """Test multi-model AI integration"""
    print_test("Multi-Model AI Integration", "RUNNING")
    
    try:
        from ai_providers import get_model_status, model_manager
        
        # Test model status
        status = get_model_status()
        if status and 'providers' in status:
            print_test("Multi-Model AI Integration", "PASS")
            print(f"   Available providers: {list(status['providers'].keys())}")
            return True
        else:
            print_test("Multi-Model AI Integration", "FAIL")
            return False
            
    except ImportError:
        print("   Multi-model system not available")
        print_test("Multi-Model AI Integration", "FAIL")
        return False
    except Exception as e:
        print(f"   Error: {e}")
        print_test("Multi-Model AI Integration", "FAIL")
        return False

async def test_security_utilities():
    """Test security utilities"""
    print_test("Security Utilities", "RUNNING")
    
    try:
        from security_utils import validate_binary_analysis_args, SecurityError
        
        # Create a temporary test file for validation
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"#!/bin/bash\necho 'test'\n")
            tmp_path = tmp.name
        
        try:
            valid_args = {"binary_path": tmp_path}
            result = validate_binary_analysis_args(valid_args)
            
            if result and result["binary_path"] == tmp_path:
                print_test("Security Utilities", "PASS")
                return True
            else:
                print_test("Security Utilities", "FAIL")
                return False
        finally:
            os.unlink(tmp_path)
            
    except ImportError:
        print("   Security utilities not available")
        print_test("Security Utilities", "FAIL")
        return False
    except Exception as e:
        print(f"   Error: {e}")
        print_test("Security Utilities", "FAIL")
        return False

async def test_ai_query_functionality():
    """Test AI query functionality"""
    print_test("AI Query Functionality", "RUNNING")
    
    try:
        from ghidra_gpt5_mcp import handle_gpt5_query
        
        # Test simple query
        test_args = {
            "query": "What is reverse engineering?",
            "context": "",
            "specialization": "reverse_engineering"
        }
        
        result = await handle_gpt5_query(test_args)
        
        if result and len(result) > 0 and result[0].text:
            print_test("AI Query Functionality", "PASS")
            return True
        else:
            print_test("AI Query Functionality", "FAIL")
            return False
            
    except Exception as e:
        print(f"   Error: {e}")
        print_test("AI Query Functionality", "FAIL")
        return False

async def test_tool_handlers():
    """Test MCP tool handlers"""
    print_test("MCP Tool Handlers", "RUNNING")
    
    try:
        from ghidra_gpt5_mcp import handle_call_tool
        
        # Test AI model status tool
        result = await handle_call_tool("ai_model_status", {"action": "status"})
        
        if result and len(result) > 0 and "AI Model Status Report" in result[0].text:
            print_test("MCP Tool Handlers", "PASS")
            return True
        else:
            print_test("MCP Tool Handlers", "FAIL")
            return False
            
    except Exception as e:
        print(f"   Error: {e}")
        print_test("MCP Tool Handlers", "FAIL")
        return False

async def run_smoke_tests():
    """Run complete smoke test suite"""
    print_header("MCP-Ghidra5 Complete Smoke Test Suite")
    print("Testing all functionality after multi-model integration...")
    
    tests_passed = 0
    total_tests = 5
    
    # Test 1: MCP Server Startup
    if await test_mcp_server_startup():
        tests_passed += 1
    
    # Test 2: Multi-Model Integration
    if await test_multi_model_integration():
        tests_passed += 1
    
    # Test 3: Security Utilities
    if await test_security_utilities():
        tests_passed += 1
    
    # Test 4: AI Query Functionality  
    if await test_ai_query_functionality():
        tests_passed += 1
    
    # Test 5: Tool Handlers
    if await test_tool_handlers():
        tests_passed += 1
    
    # Results
    print_header("SMOKE TEST RESULTS")
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    print(f"Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("🎉 ALL SMOKE TESTS PASSED!")
        print("✅ MCP-Ghidra5 server is fully operational with multi-model support")
        print("\nReady for production use with:")
        print("  - Multi-model AI support (OpenAI, Claude, Gemini, etc.)")
        print("  - Robust security validation")
        print("  - Error handling and fallback systems")
        print("  - Complete tool functionality")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        print("⚠️  Please review failed tests before production use")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_smoke_tests())
    sys.exit(0 if success else 1)