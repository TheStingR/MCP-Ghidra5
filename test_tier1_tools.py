#!/usr/bin/env python3
"""
Test Script for Tier 1 Binary Analysis Tools
MCP-Ghidra5 v1.2.0 Phase 1 Quick Wins Validation

Copyright (c) 2024 TechSquad Inc. - All Rights Reserved
Tests strings, file, objdump, readelf, and hexdump functionality
"""

import asyncio
import json
import logging
import os
import sys
import tempfile
from pathlib import Path

# Add MCP-Ghidra5 to path
sys.path.insert(0, str(Path(__file__).parent / "MCP-Ghidra5"))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def test_tier1_tools():
    """Test all Tier 1 binary analysis tools"""
    
    # Import after path setup
    try:
        from tier1_tools import (
            run_strings_analysis,
            run_file_analysis, 
            run_objdump_analysis,
            run_readelf_analysis,
            run_hexdump_analysis,
            format_output_as_json,
            format_output_as_text
        )
        logger.info("✅ Successfully imported tier1_tools")
    except ImportError as e:
        logger.error(f"❌ Failed to import tier1_tools: {e}")
        return False
    
    # Create a simple test binary
    test_binary_content = b'\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00' + \
                         b'\x02\x00\x3e\x00\x01\x00\x00\x00' + \
                         b'Hello World Test Binary\x00' + \
                         b'password123\x00' + \
                         b'https://example.com/api\x00' + \
                         b'\x00' * 100
    
    # Write test binary to temporary file
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.elf') as f:
        f.write(test_binary_content)
        test_binary_path = f.name
    
    try:
        logger.info(f"📁 Created test binary: {test_binary_path}")
        test_results = {}
        
        # Test 1: Strings Analysis
        logger.info("🔍 Testing strings analysis...")
        try:
            strings_result = await run_strings_analysis(test_binary_path, min_length=4, encoding="all")
            
            # Validate result structure
            assert "binary_path" in strings_result
            assert "results" in strings_result
            
            # Test text formatting
            text_output = format_output_as_text(strings_result, "strings")
            assert "STRINGS ANALYSIS RESULTS" in text_output
            
            # Test JSON formatting
            json_output = format_output_as_json(strings_result, "strings")
            assert json_output["tool"] == "strings"
            assert json_output["version"] == "1.2.0"
            
            test_results["strings"] = "✅ PASSED"
            logger.info("✅ Strings analysis test passed")
            
        except Exception as e:
            test_results["strings"] = f"❌ FAILED: {str(e)}"
            logger.error(f"❌ Strings analysis test failed: {e}")
        
        # Test 2: File Analysis
        logger.info("📋 Testing file analysis...")
        try:
            file_result = await run_file_analysis(test_binary_path)
            
            # Validate result structure
            assert "binary_path" in file_result
            assert "basic" in file_result
            
            # Test formatting
            text_output = format_output_as_text(file_result, "file")
            json_output = format_output_as_json(file_result, "file")
            
            test_results["file"] = "✅ PASSED"
            logger.info("✅ File analysis test passed")
            
        except Exception as e:
            test_results["file"] = f"❌ FAILED: {str(e)}"
            logger.error(f"❌ File analysis test failed: {e}")
        
        # Test 3: Objdump Analysis
        logger.info("🔧 Testing objdump analysis...")
        try:
            objdump_result = await run_objdump_analysis(test_binary_path, analysis_type="headers")
            
            # Validate result structure
            assert "binary_path" in objdump_result
            assert "results" in objdump_result
            
            # Test formatting
            text_output = format_output_as_text(objdump_result, "objdump")
            json_output = format_output_as_json(objdump_result, "objdump")
            
            test_results["objdump"] = "✅ PASSED"
            logger.info("✅ Objdump analysis test passed")
            
        except Exception as e:
            test_results["objdump"] = f"❌ FAILED: {str(e)}"
            logger.error(f"❌ Objdump analysis test failed: {e}")
        
        # Test 4: Readelf Analysis (only if ELF file)
        logger.info("⚙️ Testing readelf analysis...")
        try:
            readelf_result = await run_readelf_analysis(test_binary_path, analysis_type="headers")
            
            # Validate result structure
            assert "binary_path" in readelf_result
            assert "results" in readelf_result
            
            # Test formatting
            text_output = format_output_as_text(readelf_result, "readelf")
            json_output = format_output_as_json(readelf_result, "readelf")
            
            test_results["readelf"] = "✅ PASSED"
            logger.info("✅ Readelf analysis test passed")
            
        except Exception as e:
            test_results["readelf"] = f"❌ FAILED: {str(e)}"
            logger.error(f"❌ Readelf analysis test failed: {e}")
        
        # Test 5: Hexdump Analysis
        logger.info("🔍 Testing hexdump analysis...")
        try:
            hexdump_result = await run_hexdump_analysis(test_binary_path, offset=0, length=256)
            
            # Validate result structure
            assert "binary_path" in hexdump_result
            assert "offset" in hexdump_result
            assert "length" in hexdump_result
            
            # Test formatting
            text_output = format_output_as_text(hexdump_result, "hexdump")
            json_output = format_output_as_json(hexdump_result, "hexdump")
            
            test_results["hexdump"] = "✅ PASSED"
            logger.info("✅ Hexdump analysis test passed")
            
        except Exception as e:
            test_results["hexdump"] = f"❌ FAILED: {str(e)}"
            logger.error(f"❌ Hexdump analysis test failed: {e}")
        
        # Print test summary
        print("\n" + "="*60)
        print("🧪 TIER 1 TOOLS TEST SUMMARY")
        print("="*60)
        
        passed = 0
        failed = 0
        
        for tool, result in test_results.items():
            print(f"{tool.capitalize():<15} {result}")
            if "PASSED" in result:
                passed += 1
            else:
                failed += 1
        
        print("-"*60)
        print(f"Total Tests: {passed + failed}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/(passed+failed)*100):.1f}%" if passed+failed > 0 else "0.0%")
        print("="*60)
        
        return failed == 0
        
    finally:
        # Cleanup test binary
        try:
            os.unlink(test_binary_path)
            logger.info(f"🗑️ Cleaned up test binary: {test_binary_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup test binary: {e}")

async def test_caching_system():
    """Test the caching system"""
    logger.info("🚀 Testing caching system...")
    
    try:
        from tier1_tools import cache_manager
        
        # Test cache operations
        test_params = {"test": "value"}
        test_result = {"output": "test output", "success": True}
        
        # Store result in cache
        cache_manager.store_result("test_tool", "/tmp/test_file", test_params, test_result)
        
        # Retrieve from cache
        cached_result = cache_manager.get_cached_result("test_tool", "/tmp/test_file", test_params)
        
        if cached_result and cached_result["result"] == test_result:
            logger.info("✅ Caching system test passed")
            return True
        else:
            logger.error("❌ Caching system test failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Caching system test failed: {e}")
        return False

def test_security_validation():
    """Test security validation functions"""
    logger.info("🔒 Testing security validation...")
    
    try:
        from security_utils import (
            validate_strings_analysis_args,
            validate_file_info_args,
            validate_objdump_analysis_args,
            validate_readelf_analysis_args,
            validate_hexdump_analysis_args,
            SecurityError
        )
        
        # Test valid arguments
        valid_args = {
            "binary_path": "/bin/ls",  # Common system binary
            "output_format": "text",
            "ai_analysis": True
        }
        
        # Test strings validation
        strings_args = valid_args.copy()
        strings_args.update({"min_length": 4, "encoding": "ascii"})
        
        try:
            validated = validate_strings_analysis_args(strings_args)
            if "/bin/ls" in validated["binary_path"] and validated["min_length"] == 4:
                logger.info("✅ Strings validation passed")
            else:
                logger.error("❌ Strings validation failed: incorrect values")
                return False
        except SecurityError as e:
            # Expected for system paths in restricted mode
            logger.info(f"✅ Strings validation correctly rejected system path: {e}")
        
        # Test invalid arguments
        invalid_args = {
            "binary_path": "/nonexistent/file",
            "min_length": -5,  # Invalid
            "encoding": "invalid_encoding"  # Invalid
        }
        
        try:
            validate_strings_analysis_args(invalid_args)
            logger.error("❌ Security validation failed: should have rejected invalid args")
            return False
        except SecurityError:
            logger.info("✅ Security validation correctly rejected invalid arguments")
        
        logger.info("✅ Security validation tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Security validation test failed: {e}")
        return False

async def main():
    """Main test runner"""
    print("🚀 MCP-GHIDRA5 v1.2.0 - TIER 1 TOOLS TEST SUITE")
    print("="*60)
    
    # Check if we're in the right directory
    if not Path("MCP-Ghidra5").exists():
        logger.error("❌ MCP-Ghidra5 directory not found. Run from project root.")
        return 1
    
    # Run tests
    test_results = []
    
    # Test 1: Core Tier 1 Tools
    tier1_result = await test_tier1_tools()
    test_results.append(("Tier 1 Tools", tier1_result))
    
    # Test 2: Caching System
    cache_result = await test_caching_system()
    test_results.append(("Caching System", cache_result))
    
    # Test 3: Security Validation
    security_result = test_security_validation()
    test_results.append(("Security Validation", security_result))
    
    # Final summary
    print("\n" + "="*60)
    print("🎯 FINAL TEST RESULTS")
    print("="*60)
    
    all_passed = True
    for test_name, passed in test_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if not passed:
            all_passed = False
    
    print("-"*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Tier 1 tools are ready for production.")
        print("🚀 MCP-Ghidra5 v1.2.0 Phase 1 Quick Wins - SUCCESS!")
        return 0
    else:
        print("❌ SOME TESTS FAILED. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))