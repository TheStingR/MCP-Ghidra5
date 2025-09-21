#!/usr/bin/env python3
"""
Tier 1 Binary Analysis Tools for MCP-Ghidra5
Phase 1 Quick Wins Implementation

Copyright (c) 2024 TechSquad Inc. - All Rights Reserved
Provides strings, file, objdump, readelf, and hexdump functionality
with AI-powered analysis, caching, and JSON output support.
"""

import asyncio
import hashlib
import json
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logger = logging.getLogger(__name__)

# Cache configuration
CACHE_DIR = os.path.expanduser("~/.cache/mcp-ghidra5")
CACHE_TTL = 3600  # 1 hour cache TTL
MAX_CACHE_SIZE = 100  # Maximum number of cached results

class CacheManager:
    """Intelligent caching system for binary analysis results"""
    
    def __init__(self):
        self.cache_dir = Path(CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_file_hash(self, filepath: str) -> str:
        """Generate hash for file content and metadata"""
        try:
            stat = os.stat(filepath)
            with open(filepath, 'rb') as f:
                content_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Include file size and modification time in hash
            composite_hash = hashlib.sha256(
                f"{content_hash}:{stat.st_size}:{stat.st_mtime}".encode()
            ).hexdigest()[:16]
            
            return composite_hash
        except Exception as e:
            logger.warning(f"Failed to generate file hash: {e}")
            return hashlib.sha256(filepath.encode()).hexdigest()[:16]
    
    def _get_cache_key(self, tool: str, filepath: str, params: Dict[str, Any]) -> str:
        """Generate cache key for tool+file+parameters combination"""
        file_hash = self._get_file_hash(filepath)
        param_str = json.dumps(params, sort_keys=True)
        cache_key = f"{tool}_{file_hash}_{hashlib.sha256(param_str.encode()).hexdigest()[:8]}"
        return cache_key
    
    def get_cached_result(self, tool: str, filepath: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Retrieve cached result if valid and fresh"""
        try:
            cache_key = self._get_cache_key(tool, filepath, params)
            cache_file = self.cache_dir / f"{cache_key}.json"
            
            if not cache_file.exists():
                return None
            
            # Check if cache is still valid
            cache_age = time.time() - cache_file.stat().st_mtime
            if cache_age > CACHE_TTL:
                cache_file.unlink()  # Remove expired cache
                return None
            
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            logger.info(f"Cache hit for {tool} analysis of {filepath}")
            return cached_data
            
        except Exception as e:
            logger.warning(f"Failed to retrieve cached result: {e}")
            return None
    
    def store_result(self, tool: str, filepath: str, params: Dict[str, Any], result: Dict[str, Any]):
        """Store analysis result in cache"""
        try:
            cache_key = self._get_cache_key(tool, filepath, params)
            cache_file = self.cache_dir / f"{cache_key}.json"
            
            # Add metadata to cached result
            cached_data = {
                "timestamp": time.time(),
                "tool": tool,
                "filepath": filepath,
                "params": params,
                "result": result
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cached_data, f, indent=2)
            
            logger.info(f"Cached {tool} analysis result for {filepath}")
            
            # Clean up old cache files if necessary
            self._cleanup_cache()
            
        except Exception as e:
            logger.warning(f"Failed to cache result: {e}")
    
    def _cleanup_cache(self):
        """Remove old cache files if cache size exceeds limit"""
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            
            if len(cache_files) <= MAX_CACHE_SIZE:
                return
            
            # Sort by modification time and remove oldest files
            cache_files.sort(key=lambda f: f.stat().st_mtime)
            files_to_remove = cache_files[:-MAX_CACHE_SIZE]
            
            for cache_file in files_to_remove:
                cache_file.unlink()
            
            logger.info(f"Cleaned up {len(files_to_remove)} old cache files")
            
        except Exception as e:
            logger.warning(f"Cache cleanup failed: {e}")

# Global cache manager instance
cache_manager = CacheManager()

def validate_binary_file(filepath: str) -> bool:
    """Validate that the file exists and is readable"""
    try:
        path = Path(filepath)
        return path.exists() and path.is_file() and os.access(filepath, os.R_OK)
    except Exception:
        return False

def run_command(cmd: List[str], timeout: int = 60) -> Tuple[bool, str, str]:
    """Execute command with timeout and return success, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            errors='replace'  # Handle encoding issues gracefully
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out after {timeout} seconds"
    except Exception as e:
        return False, "", str(e)

async def run_strings_analysis(binary_path: str, min_length: int = 4, encoding: str = "all") -> Dict[str, Any]:
    """Extract strings from binary with multiple encodings"""
    
    if not validate_binary_file(binary_path):
        raise ValueError(f"Invalid binary file: {binary_path}")
    
    # Check cache first
    params = {"min_length": min_length, "encoding": encoding}
    cached_result = cache_manager.get_cached_result("strings", binary_path, params)
    if cached_result:
        return cached_result["result"]
    
    strings_results = {}
    
    # Define encoding commands
    encoding_commands = {
        "ascii": ["strings", "-a", f"-{min_length}", binary_path],
        "utf-8": ["strings", "-a", "-e", "s", f"-{min_length}", binary_path],
        "utf-16": ["strings", "-a", "-e", "l", f"-{min_length}", binary_path]
    }
    
    encodings_to_run = [encoding] if encoding != "all" else ["ascii", "utf-8", "utf-16"]
    
    for enc in encodings_to_run:
        if enc in encoding_commands:
            success, stdout, stderr = run_command(encoding_commands[enc])
            
            if success:
                strings_list = [s.strip() for s in stdout.split('\n') if s.strip()]
                strings_results[enc] = {
                    "count": len(strings_list),
                    "strings": strings_list[:1000],  # Limit to first 1000 strings
                    "sample_analysis": _analyze_strings_patterns(strings_list[:100])
                }
            else:
                strings_results[enc] = {
                    "error": f"Failed to extract {enc} strings: {stderr}",
                    "count": 0,
                    "strings": []
                }
    
    result = {
        "binary_path": binary_path,
        "min_length": min_length,
        "encoding": encoding,
        "timestamp": time.time(),
        "results": strings_results
    }
    
    # Cache the result
    cache_manager.store_result("strings", binary_path, params, result)
    
    return result

def _analyze_strings_patterns(strings: List[str]) -> Dict[str, Any]:
    """Analyze strings for interesting patterns"""
    patterns = {
        "urls": [],
        "file_paths": [],
        "crypto_keywords": [],
        "api_calls": [],
        "error_messages": [],
        "suspicious": []
    }
    
    crypto_keywords = ['encrypt', 'decrypt', 'key', 'cipher', 'hash', 'sha', 'md5', 'aes', 'rsa']
    suspicious_keywords = ['backdoor', 'keylog', 'password', 'admin', 'root', 'shell', 'exec']
    
    for string in strings[:100]:  # Analyze first 100 strings
        s_lower = string.lower()
        
        # URL detection
        if any(proto in s_lower for proto in ['http://', 'https://', 'ftp://']):
            patterns["urls"].append(string)
        
        # File path detection
        elif '/' in string and len(string) > 5:
            patterns["file_paths"].append(string)
        
        # Crypto keywords
        elif any(keyword in s_lower for keyword in crypto_keywords):
            patterns["crypto_keywords"].append(string)
        
        # Suspicious strings
        elif any(keyword in s_lower for keyword in suspicious_keywords):
            patterns["suspicious"].append(string)
        
        # Potential API calls (contains parentheses)
        elif '(' in string and ')' in string:
            patterns["api_calls"].append(string)
        
        # Error messages
        elif any(err in s_lower for err in ['error', 'failed', 'exception', 'warning']):
            patterns["error_messages"].append(string)
    
    # Limit results
    for key in patterns:
        patterns[key] = patterns[key][:10]  # Max 10 entries per category
    
    return patterns

async def run_file_analysis(binary_path: str) -> Dict[str, Any]:
    """Run file command for detailed file type analysis"""
    
    if not validate_binary_file(binary_path):
        raise ValueError(f"Invalid binary file: {binary_path}")
    
    # Check cache first
    params = {}
    cached_result = cache_manager.get_cached_result("file", binary_path, params)
    if cached_result:
        return cached_result["result"]
    
    result = {
        "binary_path": binary_path,
        "timestamp": time.time()
    }
    
    # Run different file analysis commands
    commands = {
        "basic": ["file", binary_path],
        "mime": ["file", "-i", binary_path],
        "detailed": ["file", "-L", "-b", binary_path]
    }
    
    for analysis_type, cmd in commands.items():
        success, stdout, stderr = run_command(cmd)
        
        if success:
            result[analysis_type] = {
                "output": stdout.strip(),
                "success": True
            }
        else:
            result[analysis_type] = {
                "output": stderr,
                "success": False,
                "error": stderr
            }
    
    # Add file stats
    try:
        stat = os.stat(binary_path)
        result["file_stats"] = {
            "size": stat.st_size,
            "mode": oct(stat.st_mode),
            "mtime": stat.st_mtime,
            "is_executable": os.access(binary_path, os.X_OK)
        }
    except Exception as e:
        result["file_stats"] = {"error": str(e)}
    
    # Cache the result
    cache_manager.store_result("file", binary_path, params, result)
    
    return result

async def run_objdump_analysis(binary_path: str, analysis_type: str = "all", architecture: str = "") -> Dict[str, Any]:
    """Run objdump analysis with specified options"""
    
    if not validate_binary_file(binary_path):
        raise ValueError(f"Invalid binary file: {binary_path}")
    
    # Check cache first
    params = {"analysis_type": analysis_type, "architecture": architecture}
    cached_result = cache_manager.get_cached_result("objdump", binary_path, params)
    if cached_result:
        return cached_result["result"]
    
    result = {
        "binary_path": binary_path,
        "analysis_type": analysis_type,
        "architecture": architecture,
        "timestamp": time.time(),
        "results": {}
    }
    
    # Define objdump command mappings
    objdump_commands = {
        "headers": ["-h"],
        "disassemble": ["-d"],
        "symbols": ["-t"],
        "sections": ["-h"],
        "relocs": ["-r"],
        "dynamic": ["-T"]
    }
    
    # Determine which analyses to run
    analyses_to_run = [analysis_type] if analysis_type != "all" else objdump_commands.keys()
    
    for analysis in analyses_to_run:
        if analysis in objdump_commands:
            cmd = ["objdump"] + objdump_commands[analysis]
            
            if architecture:
                cmd.extend(["-m", architecture])
                
            cmd.append(binary_path)
            
            success, stdout, stderr = run_command(cmd, timeout=120)
            
            if success:
                result["results"][analysis] = {
                    "output": stdout,
                    "success": True,
                    "summary": _summarize_objdump_output(analysis, stdout)
                }
            else:
                result["results"][analysis] = {
                    "output": stderr,
                    "success": False,
                    "error": stderr
                }
    
    # Cache the result
    cache_manager.store_result("objdump", binary_path, params, result)
    
    return result

def _summarize_objdump_output(analysis_type: str, output: str) -> Dict[str, Any]:
    """Summarize objdump output for quick analysis"""
    summary = {}
    lines = output.split('\n')
    
    if analysis_type == "headers":
        summary["section_count"] = len([line for line in lines if line.strip() and not line.startswith(('Idx', 'Section'))])
        
    elif analysis_type == "symbols":
        symbol_lines = [line for line in lines if line.strip() and not line.startswith('SYMBOL')]
        summary["symbol_count"] = len(symbol_lines)
        summary["external_symbols"] = len([line for line in symbol_lines if "*UND*" in line])
        
    elif analysis_type == "disassemble":
        summary["instruction_count"] = len([line for line in lines if ':' in line and any(c.isdigit() for c in line)])
        
    return summary

async def run_readelf_analysis(binary_path: str, analysis_type: str = "all") -> Dict[str, Any]:
    """Run readelf analysis for ELF binaries"""
    
    if not validate_binary_file(binary_path):
        raise ValueError(f"Invalid binary file: {binary_path}")
    
    # Check cache first
    params = {"analysis_type": analysis_type}
    cached_result = cache_manager.get_cached_result("readelf", binary_path, params)
    if cached_result:
        return cached_result["result"]
    
    result = {
        "binary_path": binary_path,
        "analysis_type": analysis_type,
        "timestamp": time.time(),
        "results": {}
    }
    
    # Define readelf command mappings
    readelf_commands = {
        "headers": ["-h"],
        "sections": ["-S"],
        "symbols": ["-s"],
        "relocs": ["-r"],
        "dynamic": ["-d"],
        "notes": ["-n"]
    }
    
    # Determine which analyses to run
    analyses_to_run = [analysis_type] if analysis_type != "all" else readelf_commands.keys()
    
    for analysis in analyses_to_run:
        if analysis in readelf_commands:
            cmd = ["readelf"] + readelf_commands[analysis] + [binary_path]
            
            success, stdout, stderr = run_command(cmd, timeout=60)
            
            if success:
                result["results"][analysis] = {
                    "output": stdout,
                    "success": True,
                    "summary": _summarize_readelf_output(analysis, stdout)
                }
            else:
                result["results"][analysis] = {
                    "output": stderr,
                    "success": False,
                    "error": stderr
                }
    
    # Cache the result
    cache_manager.store_result("readelf", binary_path, params, result)
    
    return result

def _summarize_readelf_output(analysis_type: str, output: str) -> Dict[str, Any]:
    """Summarize readelf output for quick analysis"""
    summary = {}
    lines = output.split('\n')
    
    if analysis_type == "headers":
        for line in lines:
            if "Class:" in line:
                summary["class"] = line.split(":")[-1].strip()
            elif "Machine:" in line:
                summary["machine"] = line.split(":")[-1].strip()
                
    elif analysis_type == "sections":
        section_lines = [line for line in lines if line.strip() and line.startswith('  [')]
        summary["section_count"] = len(section_lines)
        
    elif analysis_type == "symbols":
        symbol_lines = [line for line in lines if line.strip() and any(c.isdigit() for c in line[:5])]
        summary["symbol_count"] = len(symbol_lines)
    
    return summary

async def run_hexdump_analysis(binary_path: str, offset: int = 0, length: int = 512, format: str = "canonical") -> Dict[str, Any]:
    """Run hexdump analysis with specified parameters"""
    
    if not validate_binary_file(binary_path):
        raise ValueError(f"Invalid binary file: {binary_path}")
    
    # Check cache first
    params = {"offset": offset, "length": length, "format": format}
    cached_result = cache_manager.get_cached_result("hexdump", binary_path, params)
    if cached_result:
        return cached_result["result"]
    
    result = {
        "binary_path": binary_path,
        "offset": offset,
        "length": length,
        "format": format,
        "timestamp": time.time()
    }
    
    # Define hexdump format mappings
    format_options = {
        "canonical": ["-C"],
        "octal": ["-b"],
        "hex": ["-x"],
        "decimal": ["-d"]
    }
    
    if format in format_options:
        cmd = ["hexdump"] + format_options[format] + ["-s", str(offset), "-n", str(length), binary_path]
        
        success, stdout, stderr = run_command(cmd)
        
        if success:
            result["output"] = stdout
            result["success"] = True
            result["pattern_analysis"] = _analyze_hex_patterns(stdout)
        else:
            result["output"] = stderr
            result["success"] = False
            result["error"] = stderr
    else:
        result["error"] = f"Unknown format: {format}"
        result["success"] = False
    
    # Cache the result
    cache_manager.store_result("hexdump", binary_path, params, result)
    
    return result

def _analyze_hex_patterns(hexdump_output: str) -> Dict[str, Any]:
    """Analyze hex dump for interesting patterns"""
    patterns = {
        "null_bytes": 0,
        "printable_ratio": 0.0,
        "entropy_estimate": 0.0,
        "interesting_bytes": [],
        "magic_signatures": []
    }
    
    # Extract hex bytes from output
    hex_bytes = []
    for line in hexdump_output.split('\n'):
        if line.strip():
            parts = line.split()
            for part in parts[1:]:  # Skip offset
                if len(part) == 2 and all(c in '0123456789abcdef' for c in part.lower()):
                    hex_bytes.append(int(part, 16))
    
    if hex_bytes:
        # Count null bytes
        patterns["null_bytes"] = hex_bytes.count(0)
        
        # Calculate printable ratio
        printable_count = sum(1 for b in hex_bytes if 32 <= b <= 126)
        patterns["printable_ratio"] = printable_count / len(hex_bytes)
        
        # Simple entropy estimate
        byte_counts = {}
        for b in hex_bytes:
            byte_counts[b] = byte_counts.get(b, 0) + 1
        
        entropy = 0
        import math
        for count in byte_counts.values():
            p = count / len(hex_bytes)
            if p > 0:
                entropy -= p * math.log2(p)
        patterns["entropy_estimate"] = entropy
        
        # Look for magic signatures
        hex_str = ''.join(f'{b:02x}' for b in hex_bytes[:20])
        magic_signatures = {
            '7f454c46': 'ELF',
            '4d5a': 'PE/DOS',
            '504b0304': 'ZIP',
            'cafebabe': 'Java Class',
            '89504e47': 'PNG'
        }
        
        for magic, filetype in magic_signatures.items():
            if hex_str.lower().startswith(magic.lower()):
                patterns["magic_signatures"].append(filetype)
    
    return patterns

def format_output_as_json(tool_result: Dict[str, Any], tool_name: str) -> Dict[str, Any]:
    """Format tool output as structured JSON"""
    return {
        "tool": tool_name,
        "version": "1.2.0",
        "timestamp": time.time(),
        "data": tool_result,
        "format": "json"
    }

def format_output_as_text(tool_result: Dict[str, Any], tool_name: str) -> str:
    """Format tool output as human-readable text"""
    
    output_lines = [
        f"=== {tool_name.upper()} ANALYSIS RESULTS ===",
        f"Binary: {tool_result.get('binary_path', 'Unknown')}",
        f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tool_result.get('timestamp', time.time())))}",
        ""
    ]
    
    if tool_name == "strings":
        for encoding, data in tool_result.get("results", {}).items():
            if isinstance(data, dict) and "strings" in data:
                output_lines.extend([
                    f"--- {encoding.upper()} STRINGS ---",
                    f"Count: {data['count']}",
                    "Sample strings:"
                ])
                for string in data["strings"][:20]:  # Show first 20 strings
                    output_lines.append(f"  {string}")
                
                # Add pattern analysis
                patterns = data.get("sample_analysis", {})
                if any(patterns.values()):
                    output_lines.append("\nInteresting patterns found:")
                    for pattern_type, items in patterns.items():
                        if items:
                            output_lines.append(f"  {pattern_type}: {len(items)} found")
                            for item in items[:5]:  # Show first 5
                                output_lines.append(f"    {item}")
                output_lines.append("")
    
    elif tool_name == "file":
        for analysis_type, data in tool_result.items():
            if isinstance(data, dict) and "output" in data:
                output_lines.extend([
                    f"--- {analysis_type.upper()} ---",
                    data["output"],
                    ""
                ])
    
    elif tool_name in ["objdump", "readelf"]:
        for analysis_type, data in tool_result.get("results", {}).items():
            if isinstance(data, dict):
                output_lines.extend([
                    f"--- {analysis_type.upper()} ---",
                    f"Success: {data.get('success', False)}"
                ])
                
                if data.get("success"):
                    summary = data.get("summary", {})
                    if summary:
                        output_lines.append("Summary:")
                        for key, value in summary.items():
                            output_lines.append(f"  {key}: {value}")
                    output_lines.extend([
                        "Raw output (truncated):",
                        data.get("output", "")[:1000] + "..." if len(data.get("output", "")) > 1000 else data.get("output", ""),
                        ""
                    ])
                else:
                    output_lines.extend([
                        f"Error: {data.get('error', 'Unknown error')}",
                        ""
                    ])
    
    elif tool_name == "hexdump":
        output_lines.extend([
            f"Offset: {tool_result.get('offset', 0)}",
            f"Length: {tool_result.get('length', 0)}",
            f"Format: {tool_result.get('format', 'canonical')}",
            ""
        ])
        
        if tool_result.get("success"):
            output_lines.extend([
                "Hex dump:",
                tool_result.get("output", ""),
                ""
            ])
            
            patterns = tool_result.get("pattern_analysis", {})
            if patterns:
                output_lines.extend([
                    "Pattern Analysis:",
                    f"  Null bytes: {patterns.get('null_bytes', 0)}",
                    f"  Printable ratio: {patterns.get('printable_ratio', 0):.2%}",
                    f"  Entropy estimate: {patterns.get('entropy_estimate', 0):.2f}",
                ])
                
                if patterns.get("magic_signatures"):
                    output_lines.append(f"  Magic signatures: {', '.join(patterns['magic_signatures'])}")
        else:
            output_lines.append(f"Error: {tool_result.get('error', 'Unknown error')}")
    
    return "\n".join(output_lines)