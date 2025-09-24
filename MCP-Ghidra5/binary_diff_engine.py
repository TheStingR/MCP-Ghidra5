#!/usr/bin/env python3
"""
MCP-Ghidra5 Binary Diffing Engine
====================================

Phase 2 Core Implementation: Advanced binary comparison and analysis engine
that leverages existing Tier 1 tools for comprehensive binary diffing.

Author: TheStingR @ TechSquad Inc.
Version: 1.3.0-dev
License: MIT

Features:
- File-level binary comparison
- Section-level ELF/PE diffing  
- Function-level disassembly comparison
- String extraction and comparison
- Metadata and header diffing
- AI-powered security analysis
- Intelligent caching integration
"""

import os
import sys
import json
import hashlib
import difflib
import tempfile
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime

# Import existing MCP-Ghidra5 modules
try:
    from .tier1_tools import (
        run_strings_analysis,
        run_file_analysis, 
        run_objdump_analysis,
        run_readelf_analysis,
        run_hexdump_analysis
    )
    from .security_utils import (
        validate_binary_path,
        sanitize_input_string,
        check_file_size
    )
    from .cache_utils import AnalysisCache
    from .ai_providers import query_ai_with_fallback
except ImportError:
    # Fallback for standalone testing
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from tier1_tools import *
    from security_utils import *
    from cache_utils import AnalysisCache
    from ai_providers import query_ai_with_fallback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BinaryDiffEngine:
    """
    Core binary diffing engine that provides comprehensive comparison capabilities
    """
    
    def __init__(self, cache_enabled: bool = True):
        """Initialize the binary diffing engine"""
        self.cache_enabled = cache_enabled
        self.temp_dir = tempfile.mkdtemp(prefix="mcp_diff_")
        if cache_enabled:
            self.cache = AnalysisCache()
        else:
            self.cache = None
        
    def __enter__(self):
        """Context manager entry"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        self.cleanup()
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp directory: {e}")
    
    def validate_inputs(self, binary1: str, binary2: str) -> Tuple[bool, str]:
        """
        Validate binary paths and ensure files are accessible
        
        Args:
            binary1: Path to first binary
            binary2: Path to second binary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Validate first binary
            if not validate_binary_path(binary1):
                return False, f"Invalid binary path: {binary1}"
            
            # Validate second binary  
            if not validate_binary_path(binary2):
                return False, f"Invalid binary path: {binary2}"
                
            # Check file sizes (100MB limit per file)
            if not check_file_size(binary1, 100 * 1024 * 1024):
                return False, f"Binary too large: {binary1}"
                
            if not check_file_size(binary2, 100 * 1024 * 1024):
                return False, f"Binary too large: {binary2}"
                
            # Ensure files exist and are readable
            if not os.path.isfile(binary1) or not os.access(binary1, os.R_OK):
                return False, f"Cannot read binary: {binary1}"
                
            if not os.path.isfile(binary2) or not os.access(binary2, os.R_OK):
                return False, f"Cannot read binary: {binary2}"
                
            return True, ""
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def generate_diff_hash(self, binary1: str, binary2: str, diff_params: Dict) -> str:
        """Generate unique hash for diff operation caching"""
        try:
            # Get file hashes
            hash1 = self._get_file_hash(binary1)
            hash2 = self._get_file_hash(binary2)
            
            # Create parameter hash
            param_str = json.dumps(diff_params, sort_keys=True)
            param_hash = hashlib.md5(param_str.encode()).hexdigest()
            
            # Combine hashes
            combined = f"{hash1}_{hash2}_{param_hash}"
            return hashlib.md5(combined.encode()).hexdigest()
            
        except Exception as e:
            logger.warning(f"Failed to generate diff hash: {e}")
            return hashlib.md5(f"{binary1}_{binary2}_{datetime.now()}".encode()).hexdigest()
    
    def _get_file_hash(self, filepath: str) -> str:
        """Get SHA256 hash of file content"""
        try:
            sha256_hash = hashlib.sha256()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.warning(f"Failed to hash file {filepath}: {e}")
            return ""
    
    def file_level_diff(self, binary1: str, binary2: str) -> Dict[str, Any]:
        """
        Perform file-level binary comparison
        
        Args:
            binary1: Path to first binary
            binary2: Path to second binary
            
        Returns:
            Dictionary containing diff results
        """
        try:
            results = {
                "diff_type": "file_level",
                "binary1": binary1,
                "binary2": binary2,
                "timestamp": datetime.now().isoformat(),
                "identical": False,
                "size_diff": 0,
                "byte_diff_count": 0,
                "diff_positions": [],
                "similarity_score": 0.0
            }
            
            # Get file sizes
            size1 = os.path.getsize(binary1)
            size2 = os.path.getsize(binary2)
            results["size_diff"] = size2 - size1
            
            # Quick hash comparison
            hash1 = self._get_file_hash(binary1)
            hash2 = self._get_file_hash(binary2)
            
            if hash1 == hash2:
                results["identical"] = True
                results["similarity_score"] = 1.0
                return results
            
            # Byte-by-byte comparison for similarity
            diff_count = 0
            diff_positions = []
            
            with open(binary1, 'rb') as f1, open(binary2, 'rb') as f2:
                pos = 0
                while True:
                    byte1 = f1.read(1)
                    byte2 = f2.read(1)
                    
                    if not byte1 and not byte2:
                        break
                    
                    if byte1 != byte2:
                        diff_count += 1
                        if len(diff_positions) < 1000:  # Limit stored positions
                            diff_positions.append({
                                "position": pos,
                                "byte1": byte1.hex() if byte1 else None,
                                "byte2": byte2.hex() if byte2 else None
                            })
                    
                    pos += 1
            
            # Calculate similarity score
            total_bytes = max(size1, size2)
            if total_bytes > 0:
                results["similarity_score"] = 1.0 - (diff_count / total_bytes)
            
            results["byte_diff_count"] = diff_count
            results["diff_positions"] = diff_positions
            
            return results
            
        except Exception as e:
            logger.error(f"File-level diff failed: {e}")
            return {"error": str(e), "diff_type": "file_level"}
    
    async def string_level_diff(self, binary1: str, binary2: str) -> Dict[str, Any]:
        """
        Compare strings extracted from both binaries
        
        Args:
            binary1: Path to first binary
            binary2: Path to second binary
            
        Returns:
            Dictionary containing string diff results
        """
        try:
            # Extract strings from both binaries
            strings1_result = await run_strings_analysis(binary1, min_length=4, encoding="all")
            strings2_result = await run_strings_analysis(binary2, min_length=4, encoding="all")
            
            if not strings1_result or not strings2_result:
                return {"error": "Failed to extract strings", "diff_type": "string_level"}
            
            # Parse strings from tier1_tools result format
            strings1 = self._parse_tier1_strings_result(strings1_result)
            strings2 = self._parse_tier1_strings_result(strings2_result)
            
            # Compute string differences
            added_strings = set(strings2) - set(strings1)
            removed_strings = set(strings1) - set(strings2)
            common_strings = set(strings1) & set(strings2)
            
            results = {
                "diff_type": "string_level",
                "binary1": binary1,
                "binary2": binary2,
                "timestamp": datetime.now().isoformat(),
                "strings1_count": len(strings1),
                "strings2_count": len(strings2),
                "added_strings": list(added_strings)[:100],  # Limit output size
                "removed_strings": list(removed_strings)[:100],
                "common_strings_count": len(common_strings),
                "string_similarity_score": len(common_strings) / max(len(strings1), len(strings2), 1)
            }
            
            return results
            
        except Exception as e:
            logger.error(f"String-level diff failed: {e}")
            return {"error": str(e), "diff_type": "string_level"}
    
    def _parse_strings_output(self, output: str) -> List[str]:
        """Parse strings command output to extract strings"""
        strings = []
        for line in output.split('\n'):
            line = line.strip()
            if line and not line.startswith('[') and len(line) > 3:
                strings.append(line)
        return strings
    
    def _parse_tier1_strings_result(self, result: Dict[str, Any]) -> List[str]:
        """Parse tier1_tools strings result format"""
        all_strings = []
        if result and "results" in result:
            for encoding, data in result["results"].items():
                if isinstance(data, dict) and "strings" in data:
                    all_strings.extend(data["strings"])
        return all_strings
    
    async def function_level_diff(self, binary1: str, binary2: str) -> Dict[str, Any]:
        """
        Compare disassembled functions between binaries
        
        Args:
            binary1: Path to first binary
            binary2: Path to second binary
            
        Returns:
            Dictionary containing function diff results
        """
        try:
            # Get objdump analysis for both binaries
            objdump1_result = await run_objdump_analysis(binary1, analysis_type="disassemble", architecture="auto")
            objdump2_result = await run_objdump_analysis(binary2, analysis_type="disassemble", architecture="auto")
            
            if not objdump1_result or not objdump2_result:
                return {"error": "Failed to disassemble binaries", "diff_type": "function_level"}
            
            # Parse functions from tier1_tools objdump result format
            functions1 = self._parse_tier1_objdump_result(objdump1_result)
            functions2 = self._parse_tier1_objdump_result(objdump2_result)
            
            # Compare functions
            func_names1 = set(functions1.keys())
            func_names2 = set(functions2.keys())
            
            added_functions = func_names2 - func_names1
            removed_functions = func_names1 - func_names2
            common_functions = func_names1 & func_names2
            
            # Analyze changed functions
            changed_functions = []
            for func_name in common_functions:
                if functions1[func_name] != functions2[func_name]:
                    changed_functions.append({
                        "function": func_name,
                        "instructions1": len(functions1[func_name]),
                        "instructions2": len(functions2[func_name])
                    })
            
            results = {
                "diff_type": "function_level",
                "binary1": binary1,
                "binary2": binary2,
                "timestamp": datetime.now().isoformat(),
                "functions1_count": len(functions1),
                "functions2_count": len(functions2),
                "added_functions": list(added_functions)[:50],
                "removed_functions": list(removed_functions)[:50],
                "changed_functions": changed_functions[:50],
                "function_similarity_score": len(common_functions) / max(len(functions1), len(functions2), 1)
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Function-level diff failed: {e}")
            return {"error": str(e), "diff_type": "function_level"}
    
    def _parse_objdump_functions(self, output: str) -> Dict[str, List[str]]:
        """Parse objdump output to extract function disassembly"""
        functions = {}
        current_function = None
        current_instructions = []
        
        for line in output.split('\n'):
            line = line.strip()
            
            # Function start pattern
            if '<' in line and '>:' in line:
                # Save previous function
                if current_function and current_instructions:
                    functions[current_function] = current_instructions
                
                # Start new function
                func_match = line.split('<')[1].split('>')[0] if '<' in line else None
                if func_match:
                    current_function = func_match
                    current_instructions = []
            
            # Instruction line
            elif current_function and ':' in line and any(c.isdigit() for c in line):
                current_instructions.append(line)
        
        # Save final function
        if current_function and current_instructions:
            functions[current_function] = current_instructions
            
        return functions
    
    def _parse_tier1_objdump_result(self, result: Dict[str, Any]) -> Dict[str, List[str]]:
        """Parse tier1_tools objdump result format"""
        if result and "results" in result and "disassemble" in result["results"]:
            disasm_data = result["results"]["disassemble"]
            if disasm_data.get("success") and "output" in disasm_data:
                return self._parse_objdump_functions(disasm_data["output"])
        return {}
    
    async def metadata_diff(self, binary1: str, binary2: str) -> Dict[str, Any]:
        """
        Compare file metadata and ELF/PE headers
        
        Args:
            binary1: Path to first binary
            binary2: Path to second binary
            
        Returns:
            Dictionary containing metadata diff results
        """
        try:
            # Get file metadata
            file1_result = await run_file_analysis(binary1)
            file2_result = await run_file_analysis(binary2)
            
            # Get ELF analysis if applicable
            readelf1_result = await run_readelf_analysis(binary1, analysis_type="headers")
            readelf2_result = await run_readelf_analysis(binary2, analysis_type="headers")
            
            results = {
                "diff_type": "metadata",
                "binary1": binary1,
                "binary2": binary2,
                "timestamp": datetime.now().isoformat(),
                "file_type_changed": False,
                "architecture_changed": False,
                "entry_point_changed": False,
                "sections_changed": False,
                "differences": []
            }
            
            # Compare file types from tier1_tools file result format
            file1_type = self._extract_file_type_from_tier1_result(file1_result)
            file2_type = self._extract_file_type_from_tier1_result(file2_result)
            
            if file1_type != file2_type:
                results["file_type_changed"] = True
                results["differences"].append({
                    "category": "file_type",
                    "binary1": file1_type,
                    "binary2": file2_type
                })
            
            # Compare ELF headers if available
            if readelf1_result and readelf2_result:
                elf_diff = self._compare_elf_headers(readelf1_result, readelf2_result)
                results.update(elf_diff)
            
            return results
            
        except Exception as e:
            logger.error(f"Metadata diff failed: {e}")
            return {"error": str(e), "diff_type": "metadata"}
    
    def _compare_elf_headers(self, elf1: Dict, elf2: Dict) -> Dict[str, Any]:
        """Compare ELF header information"""
        differences = []
        
        # Compare key ELF fields (simplified)
        output1 = elf1.get("output", "")
        output2 = elf2.get("output", "")
        
        # Simple line-by-line comparison for headers
        lines1 = output1.split('\n')[:20]  # First 20 lines contain headers
        lines2 = output2.split('\n')[:20]
        
        for i, (line1, line2) in enumerate(zip(lines1, lines2)):
            if line1.strip() != line2.strip():
                differences.append({
                    "line": i + 1,
                    "binary1": line1.strip(),
                    "binary2": line2.strip()
                })
        
        return {
            "elf_header_differences": differences,
            "sections_changed": len(differences) > 0
        }
    
    def _extract_file_type_from_tier1_result(self, result: Dict[str, Any]) -> str:
        """Extract file type from tier1_tools file analysis result"""
        if result and "basic" in result:
            basic_data = result["basic"]
            if basic_data.get("success") and "output" in basic_data:
                return basic_data["output"].split('\n')[0]
        return ""
    
    async def comprehensive_diff(
        self, 
        binary1: str, 
        binary2: str,
        diff_types: List[str] = None,
        ai_analysis: bool = False
    ) -> Dict[str, Any]:
        """
        Perform comprehensive binary diff analysis
        
        Args:
            binary1: Path to first binary
            binary2: Path to second binary  
            diff_types: List of diff types to perform
            ai_analysis: Whether to include AI-powered analysis
            
        Returns:
            Dictionary containing comprehensive diff results
        """
        if diff_types is None:
            diff_types = ["file", "strings", "functions", "metadata"]
        
        # Check cache first
        cache_params = {
            "diff_types": diff_types,
            "ai_analysis": ai_analysis
        }
        cache_key = self.generate_diff_hash(binary1, binary2, cache_params)
        
        if self.cache_enabled and self.cache:
            cached = self.cache.get_cached_result(binary1, "comprehensive_diff", {"binary2": binary2, "diff_types": diff_types, "ai_analysis": ai_analysis})
            if cached:
                logger.info(f"Using cached comprehensive diff result")
                return cached
        
        # Validate inputs
        valid, error = self.validate_inputs(binary1, binary2)
        if not valid:
            return {"error": error}
        
        results = {
            "analysis_type": "comprehensive_binary_diff",
            "version": "1.3.0-dev",
            "binary1": binary1,
            "binary2": binary2,
            "timestamp": datetime.now().isoformat(),
            "diff_types_performed": diff_types,
            "ai_analysis_enabled": ai_analysis,
            "results": {}
        }
        
        try:
            # Perform requested diff types
            if "file" in diff_types:
                logger.info("Performing file-level diff...")
                results["results"]["file_level"] = self.file_level_diff(binary1, binary2)
            
            if "strings" in diff_types:
                logger.info("Performing string-level diff...")
                results["results"]["string_level"] = await self.string_level_diff(binary1, binary2)
            
            if "functions" in diff_types:
                logger.info("Performing function-level diff...")
                results["results"]["function_level"] = await self.function_level_diff(binary1, binary2)
            
            if "metadata" in diff_types:
                logger.info("Performing metadata diff...")
                results["results"]["metadata_level"] = await self.metadata_diff(binary1, binary2)
            
            # AI analysis if requested
            if ai_analysis:
                logger.info("Performing AI-powered diff analysis...")
                results["ai_analysis"] = await self._ai_security_analysis(results)
            
            # Cache results
            if self.cache_enabled and self.cache:
                self.cache.cache_result(binary1, "comprehensive_diff", {"binary2": binary2, "diff_types": diff_types, "ai_analysis": ai_analysis}, results)
                
            return results
            
        except Exception as e:
            logger.error(f"Comprehensive diff failed: {e}")
            return {"error": str(e), "analysis_type": "comprehensive_binary_diff"}
    
    async def _ai_security_analysis(self, diff_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform AI-powered security analysis of diff results
        
        Args:
            diff_results: Results from binary diff analysis
            
        Returns:
            AI analysis results
        """
        try:
            # Prepare analysis prompt
            prompt = self._build_ai_analysis_prompt(diff_results)
            
            # Query AI provider with fallback
            messages = [
                {"role": "system", "content": "You are a cybersecurity expert analyzing binary differences for security implications."},
                {"role": "user", "content": prompt}
            ]
            
            ai_response_text, metadata = await query_ai_with_fallback(
                messages, "analysis", "gpt-4o"
            )
            
            return {
                "provider": metadata.get("provider", "openai"),
                "model": metadata.get("model", "gpt-4o"),
                "analysis": ai_response_text,
                "timestamp": datetime.now().isoformat()
            }
                
        except Exception as e:
            logger.warning(f"AI analysis failed: {e}")
            return {"error": str(e)}
    
    def _build_ai_analysis_prompt(self, diff_results: Dict[str, Any]) -> str:
        """Build AI analysis prompt from diff results"""
        prompt = """Analyze the following binary diff results for security implications:

Binary Comparison Summary:
- Binary 1: {binary1}
- Binary 2: {binary2}
- Analysis Types: {diff_types}

""".format(
            binary1=diff_results.get("binary1", "unknown"),
            binary2=diff_results.get("binary2", "unknown"),
            diff_types=", ".join(diff_results.get("diff_types_performed", []))
        )
        
        # Add specific results summaries
        results = diff_results.get("results", {})
        
        if "file_level" in results:
            file_result = results["file_level"]
            prompt += f"""
File-Level Changes:
- Similarity Score: {file_result.get('similarity_score', 0):.2f}
- Size Difference: {file_result.get('size_diff', 0)} bytes
- Byte Differences: {file_result.get('byte_diff_count', 0)}
"""
        
        if "string_level" in results:
            string_result = results["string_level"]
            prompt += f"""
String Changes:
- Added Strings: {len(string_result.get('added_strings', []))}
- Removed Strings: {len(string_result.get('removed_strings', []))}
- String Similarity: {string_result.get('string_similarity_score', 0):.2f}
"""
        
        if "function_level" in results:
            func_result = results["function_level"]
            prompt += f"""
Function Changes:
- Added Functions: {len(func_result.get('added_functions', []))}
- Removed Functions: {len(func_result.get('removed_functions', []))}
- Changed Functions: {len(func_result.get('changed_functions', []))}
"""
        
        prompt += """
Please provide a security analysis focusing on:
1. Potential security implications of the changes
2. Risk assessment (Low/Medium/High)
3. Specific areas of concern
4. Recommended follow-up analysis
5. Exploitation potential

Keep the analysis concise and focused on actionable security insights.
"""
        
        return prompt


def main():
    """Main function for testing"""
    if len(sys.argv) < 3:
        print("Usage: python binary_diff_engine.py <binary1> <binary2>")
        sys.exit(1)
    
    binary1 = sys.argv[1]
    binary2 = sys.argv[2]
    
    async def run_analysis():
        with BinaryDiffEngine() as engine:
            results = await engine.comprehensive_diff(binary1, binary2, ai_analysis=True)
            print(json.dumps(results, indent=2))
    
    import asyncio
    asyncio.run(run_analysis())


if __name__ == "__main__":
    main()