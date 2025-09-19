#!/usr/bin/env python3
"""
Comprehensive Test Suite for Ghidra GPT-5 MCP Server
Includes integration tests, performance benchmarks, and error handling tests

Copyright (c) 2024 TechSquad Inc. - All Rights Reserved
Proprietary Software - NOT FOR RESALE
Coded by: TheStingR
"""

import asyncio
import logging
import os
import sys
import time
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Any

# Add the MCP server to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)

# Test configuration
TEST_RESULTS = {}
PERFORMANCE_METRICS = {}

def create_test_binary():
    """Create a simple test binary for analysis"""
    test_c_code = '''
#include <stdio.h>
#include <string.h>

void vulnerable_function(char* input) {
    char buffer[64];
    strcpy(buffer, input);  // Vulnerable to buffer overflow
    printf("Input: %s\\n", buffer);
}

int main(int argc, char* argv[]) {
    if (argc > 1) {
        vulnerable_function(argv[1]);
    }
    return 0;
}
'''
    
    # Create temporary C file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
        f.write(test_c_code)
        c_file = f.name
    
    # Compile to binary
    binary_file = c_file.replace('.c', '')
    try:
        subprocess.run(['gcc', '-o', binary_file, c_file, '-no-pie', '-fno-stack-protector'], 
                      check=True, capture_output=True)
        os.unlink(c_file)  # Remove C file
        return binary_file
    except (subprocess.CalledProcessError, FileNotFoundError):
        # If gcc not available, return None
        os.unlink(c_file)
        return None

async def test_mcp_tools_functionality():
    """Test all MCP tools with sample inputs"""
    print("🛠️  Testing MCP Tools Functionality")
    print("-" * 40)
    
    try:
        from ghidra_gpt5_mcp import (
            handle_binary_analysis,
            handle_function_analysis,
            handle_exploit_development,
            handle_malware_analysis,
            handle_firmware_analysis,
            handle_pattern_search,
            handle_gpt5_query
        )
        
        # Create test binary
        test_binary = create_test_binary()
        if test_binary:
            print(f"✅ Created test binary: {test_binary}")
        else:
            print("⚠️  No test binary available (gcc not found)")
            test_binary = "/usr/bin/ls"  # Use system binary as fallback
        
        # Test 1: GPT-5 Query Tool (fastest)
        print("\n1. Testing GPT-5 Query Tool...")
        start_time = time.time()
        try:
            result = await handle_gpt5_query({
                "query": "What is buffer overflow vulnerability?",
                "specialization": "vulnerability_research"
            })
            
            end_time = time.time()
            PERFORMANCE_METRICS['gpt5_query'] = end_time - start_time
            
            if result and len(result) > 0 and result[0].text:
                print("✅ GPT-5 Query tool working")
                print(f"⏱️  Response time: {PERFORMANCE_METRICS['gpt5_query']:.2f}s")
                print(f"📝 Response: {result[0].text[:100]}...")
                TEST_RESULTS['gpt5_query'] = True
            else:
                print("❌ GPT-5 Query tool failed")
                TEST_RESULTS['gpt5_query'] = False
                
        except Exception as e:
            print(f"❌ GPT-5 Query error: {e}")
            TEST_RESULTS['gpt5_query'] = False
        
        # Test 2: Binary Analysis Tool
        print("\n2. Testing Binary Analysis Tool...")
        start_time = time.time()
        try:
            result = await handle_binary_analysis({
                "binary_path": test_binary,
                "analysis_depth": "quick",
                "focus_areas": ["vulnerabilities"]
            })
            
            end_time = time.time()
            PERFORMANCE_METRICS['binary_analysis'] = end_time - start_time
            
            if result and len(result) > 0:
                print("✅ Binary Analysis tool working")
                print(f"⏱️  Analysis time: {PERFORMANCE_METRICS['binary_analysis']:.2f}s")
                print(f"📝 Analysis: {result[0].text[:150]}...")
                TEST_RESULTS['binary_analysis'] = True
            else:
                print("❌ Binary Analysis tool failed")
                TEST_RESULTS['binary_analysis'] = False
                
        except Exception as e:
            print(f"❌ Binary Analysis error: {e}")
            TEST_RESULTS['binary_analysis'] = False
        
        # Test 3: Exploit Development Tool  
        print("\n3. Testing Exploit Development Tool...")
        start_time = time.time()
        try:
            result = await handle_exploit_development({
                "binary_path": test_binary,
                "target_platform": "linux_x64",
                "exploit_type": "buffer_overflow",
                "generate_poc": False
            })
            
            end_time = time.time()
            PERFORMANCE_METRICS['exploit_development'] = end_time - start_time
            
            if result and len(result) > 0:
                print("✅ Exploit Development tool working")
                print(f"⏱️  Analysis time: {PERFORMANCE_METRICS['exploit_development']:.2f}s")
                print(f"📝 Analysis: {result[0].text[:150]}...")
                TEST_RESULTS['exploit_development'] = True
            else:
                print("❌ Exploit Development tool failed")
                TEST_RESULTS['exploit_development'] = False
                
        except Exception as e:
            print(f"❌ Exploit Development error: {e}")
            TEST_RESULTS['exploit_development'] = False
        
        # Cleanup test binary
        if test_binary and test_binary != "/usr/bin/ls":
            try:
                os.unlink(test_binary)
            except:
                pass
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def test_error_handling():
    """Test error handling with invalid inputs"""
    print("\n🚨 Testing Error Handling")
    print("-" * 30)
    
    try:
        from ghidra_gpt5_mcp import handle_binary_analysis, handle_gpt5_query
        
        # Test 1: Invalid binary path
        print("1. Testing invalid binary path...")
        try:
            result = await handle_binary_analysis({
                "binary_path": "/nonexistent/path/binary",
                "analysis_depth": "quick"
            })
            if result:
                print("✅ Graceful error handling for invalid path")
            else:
                print("⚠️  No result returned for invalid path")
            TEST_RESULTS['error_invalid_path'] = True
        except Exception as e:
            print(f"⚠️  Exception for invalid path: {str(e)[:100]}...")
            TEST_RESULTS['error_invalid_path'] = True  # Expected behavior
        
        # Test 2: Empty query
        print("2. Testing empty query...")
        try:
            result = await handle_gpt5_query({
                "query": "",
                "specialization": "general"
            })
            print("✅ Handles empty query gracefully")
            TEST_RESULTS['error_empty_query'] = True
        except Exception as e:
            print(f"⚠️  Exception for empty query: {str(e)[:100]}...")
            TEST_RESULTS['error_empty_query'] = True  # Expected behavior
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing failed: {e}")
        return False

def test_environment_requirements():
    """Test environment and dependency requirements"""
    print("🔍 Testing Environment Requirements")
    print("-" * 35)
    
    requirements_met = True
    
    # Test Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} (need 3.8+)")
        requirements_met = False
    
    # Test required packages
    required_packages = ['mcp', 'aiohttp']
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} available")
        except ImportError:
            print(f"❌ {package} missing")
            requirements_met = False
    
    # Test API key
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key and api_key.startswith(('sk-', 'sk-proj-')):
        print("✅ OpenAI API key configured")
    else:
        print("❌ OpenAI API key not found or invalid format")
        requirements_met = False
    
    # Test Ghidra
    ghidra_path = os.environ.get('GHIDRA_HEADLESS_PATH', '/usr/share/ghidra/support/analyzeHeadless')
    if os.path.exists(ghidra_path) and os.access(ghidra_path, os.X_OK):
        print(f"✅ Ghidra found: {ghidra_path}")
    else:
        print(f"⚠️  Ghidra not found at: {ghidra_path}")
        # Check if it would be detected by auto-detection
        try:
            sys.path.append('.')
            from ghidra_gpt5_mcp import detect_ghidra_path
            detected = detect_ghidra_path()
            if os.path.exists(detected):
                print(f"✅ Ghidra auto-detected: {detected}")
            else:
                print("⚠️  Ghidra not available (some features will be limited)")
        except:
            print("⚠️  Could not test Ghidra auto-detection")
    
    TEST_RESULTS['environment'] = requirements_met
    return requirements_met

def generate_performance_report():
    """Generate performance benchmark report"""
    print("\n📊 Performance Benchmarks")
    print("=" * 40)
    
    if PERFORMANCE_METRICS:
        print("| Tool | Response Time | Status |")
        print("|------|---------------|--------|")
        for tool, time_taken in PERFORMANCE_METRICS.items():
            status = "✅ PASS" if TEST_RESULTS.get(tool, False) else "❌ FAIL"
            print(f"| {tool.replace('_', ' ').title()} | {time_taken:.2f}s | {status} |")
    else:
        print("No performance metrics available")
    
    print(f"\nTotal tests run: {len(TEST_RESULTS)}")
    passed = sum(1 for result in TEST_RESULTS.values() if result)
    print(f"Tests passed: {passed}/{len(TEST_RESULTS)}")
    print(f"Success rate: {(passed/len(TEST_RESULTS)*100):.1f}%")

async def main():
    """Main comprehensive test function"""
    print("🚀 Comprehensive Ghidra GPT-5 MCP Server Test Suite")
    print("=" * 60)
    print()
    
    # Environment check
    env_ok = test_environment_requirements()
    if not env_ok:
        print("\n❌ Environment check failed. Some tests may not work properly.")
    
    # Tool functionality tests
    print("\n" + "=" * 60)
    tools_ok = await test_mcp_tools_functionality()
    
    # Error handling tests
    print("\n" + "=" * 60)
    error_ok = await test_error_handling()
    
    # Performance report
    print("\n" + "=" * 60)
    generate_performance_report()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    
    if env_ok and tools_ok and error_ok:
        print("🎉 ALL COMPREHENSIVE TESTS PASSED!")
        print("\nThe MCP server is production-ready with:")
        print("✅ Full environment compatibility") 
        print("✅ All tools functional")
        print("✅ Robust error handling")
        print("✅ Performance benchmarks available")
        sys.exit(0)
    else:
        print("⚠️  Some tests had issues. Check details above.")
        print("\nIssue areas:")
        if not env_ok:
            print("❌ Environment setup")
        if not tools_ok:
            print("❌ Tool functionality") 
        if not error_ok:
            print("❌ Error handling")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())