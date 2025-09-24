#!/usr/bin/env python3
"""
Ghidra GPT-5 MCP Server for Advanced Reverse Engineering
Version: 1.3.0-dev
Specialized for binary analysis, exploitation research, and malware reverse engineering

Copyright (c) 2024 TechSquad Inc. - All Rights Reserved
Proprietary Software - NOT FOR RESALE
Coded by: TheStingR

This software is the property of TechSquad Inc. and is protected by copyright law.
Unauthorized reproduction, distribution, or sale is strictly prohibited.
For licensing inquiries, contact TechSquad Inc.

CHANGELOG:
v1.3.0-dev (2025-09-24) - Phase 2: Advanced Binary Diffing Tools
  - Added binary diffing engine for version comparison
  - Implemented patch analysis for security assessment
  - Added version evolution tracking across multiple binaries
  - Enhanced reporting capabilities with visualization
  - Integrated AI-powered security analysis for binary changes
v1.2.0 (2025-09-21) - Phase 1 Quick Wins: Tier 1 Binary Analysis Tools
  - Added 5 new Tier 1 binary analysis tools
  - Implemented intelligent caching system
  - Added comprehensive security validation
  - Supported JSON output format for automation
v1.1.0 (2025-01-19) - Major Multi-Model AI Integration
  - Added comprehensive multi-model AI support (OpenAI, Claude, Gemini, Grok, DeepSeek, Ollama)
  - Implemented AI model status and testing tools
  - Added cost tracking and usage statistics
  - Enhanced error handling and automatic fallback systems
v1.0.1 (2025-09-18) - Critical bug fixes reported by PurpleTeam-TechSquad
  - Added Ghidra path auto-detection for multiple Linux distributions
  - Enhanced cross-platform compatibility
v1.0.0 (2025-09-15) - Initial release

ACKNOWLEDGMENTS:
- Issue reporting and testing: PurpleTeam-TechSquad (https://github.com/PurpleTeam-TechSquad)
"""

import asyncio
import logging
import os
import sys
import json
import tempfile
import subprocess
from typing import Any, Dict, List, Optional
from pathlib import Path

import aiohttp
from mcp.server.stdio import stdio_server
from mcp.server import Server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Version and metadata
__version__ = "1.3.0-dev"
__author__ = "TheStingR"
__copyright__ = "Copyright (c) 2024 TechSquad Inc. - All Rights Reserved"
__license__ = "Proprietary - NOT FOR RESALE"
__acknowledgments__ = "Issue reporting: PurpleTeam-TechSquad (https://github.com/PurpleTeam-TechSquad)"

# OpenAI API Configuration
OPENAI_BASE_URL = "https://api.openai.com/v1"
OPENAI_CHAT_ENDPOINT = f"{OPENAI_BASE_URL}/chat/completions"
GPT_MODEL = "gpt-4o"  # Will use GPT-5 when available

# Performance settings optimized for binary analysis
MAX_RETRIES = 3
RETRY_DELAY = 2
MAX_TOKENS_DEFAULT = 2000
MAX_TOKENS_ANALYSIS = 4000
MAX_TOKENS_EXPLOIT = 3000
REQUEST_TIMEOUT = 120  # Longer timeout for complex analysis

# Ghidra configuration - FIXED: Support multiple installation paths
def detect_ghidra_path():
    """Auto-detect Ghidra installation path"""
    paths = [
        '/usr/share/ghidra/support/analyzeHeadless',  # Debian/Ubuntu/Kali package
        '/opt/ghidra/support/analyzeHeadless',        # Manual install
        '/usr/local/ghidra/support/analyzeHeadless',  # Alternative manual
        '/usr/local/share/ghidra/support/analyzeHeadless'  # Homebrew/alternative
    ]
    
    for path in paths:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    
    return '/opt/ghidra/support/analyzeHeadless'  # Default fallback

GHIDRA_HEADLESS_PATH = os.environ.get('GHIDRA_HEADLESS_PATH', detect_ghidra_path())
GHIDRA_PROJECT_DIR = os.environ.get('GHIDRA_PROJECT_DIR', '/tmp/ghidra_projects')

# Create server instance
app = Server("ghidra-gpt5-mcp-server")

@app.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available Ghidra + GPT-5 tools"""
    return [
        Tool(
            name="ghidra_binary_analysis",
            description="Comprehensive binary analysis using Ghidra + GPT-5 for reverse engineering",
            inputSchema={
                "type": "object",
                "properties": {
                    "binary_path": {
                        "type": "string",
                        "description": "Path to binary file for analysis"
                    },
                    "analysis_depth": {
                        "type": "string",
                        "description": "Analysis depth level",
                        "enum": ["quick", "standard", "deep", "exploit_focused"]
                    },
                    "focus_areas": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific areas to focus on (e.g., 'vulnerabilities', 'crypto', 'network', 'obfuscation')"
                    }
                },
                "required": ["binary_path"]
            }
        ),
        Tool(
            name="ghidra_function_analysis",
            description="Analyze specific functions in a binary using Ghidra decompilation + GPT-5",
            inputSchema={
                "type": "object",
                "properties": {
                    "binary_path": {
                        "type": "string",
                        "description": "Path to binary file"
                    },
                    "function_address": {
                        "type": "string",
                        "description": "Function address (e.g., '0x401000') or function name"
                    },
                    "analysis_type": {
                        "type": "string",
                        "description": "Type of function analysis",
                        "enum": ["vulnerability_scan", "algorithm_identification", "crypto_analysis", "exploit_potential", "behavioral_analysis"]
                    }
                },
                "required": ["binary_path", "function_address"]
            }
        ),
        Tool(
            name="ghidra_exploit_development",
            description="Analyze binary for exploitation opportunities and generate exploit strategies",
            inputSchema={
                "type": "object",
                "properties": {
                    "binary_path": {
                        "type": "string",
                        "description": "Path to target binary"
                    },
                    "target_platform": {
                        "type": "string",
                        "description": "Target platform (e.g., 'linux_x64', 'windows_x86', 'arm64')"
                    },
                    "exploit_type": {
                        "type": "string",
                        "description": "Exploitation approach to focus on",
                        "enum": ["buffer_overflow", "format_string", "use_after_free", "rop_chain", "heap_exploitation", "race_condition"]
                    },
                    "generate_poc": {
                        "type": "boolean",
                        "description": "Whether to generate proof-of-concept exploit code",
                        "default": False
                    }
                },
                "required": ["binary_path", "target_platform"]
            }
        ),
        Tool(
            name="ghidra_malware_analysis",
            description="Specialized malware analysis using Ghidra + GPT-5 for behavioral and structural analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "malware_path": {
                        "type": "string",
                        "description": "Path to malware sample (CAUTION: Ensure safe environment)"
                    },
                    "analysis_scope": {
                        "type": "string",
                        "description": "Scope of malware analysis",
                        "enum": ["static_only", "behavioral", "network_analysis", "persistence_mechanisms", "evasion_techniques"]
                    },
                    "sandbox_mode": {
                        "type": "boolean",
                        "description": "Whether to assume sandbox/VM environment",
                        "default": True
                    }
                },
                "required": ["malware_path"]
            }
        ),
        Tool(
            name="ghidra_firmware_analysis",
            description="Firmware and embedded system analysis using Ghidra + GPT-5",
            inputSchema={
                "type": "object",
                "properties": {
                    "firmware_path": {
                        "type": "string",
                        "description": "Path to firmware image or extracted binary"
                    },
                    "architecture": {
                        "type": "string",
                        "description": "Target architecture if known",
                        "enum": ["arm", "mips", "x86", "x64", "riscv", "auto_detect"]
                    },
                    "device_type": {
                        "type": "string",
                        "description": "Type of device/firmware",
                        "enum": ["router", "iot_device", "bootloader", "rtos", "embedded_linux", "unknown"]
                    }
                },
                "required": ["firmware_path"]
            }
        ),
        Tool(
            name="ghidra_code_pattern_search",
            description="Search for specific code patterns, vulnerabilities, or algorithms in binaries",
            inputSchema={
                "type": "object",
                "properties": {
                    "binary_path": {
                        "type": "string",
                        "description": "Path to binary file"
                    },
                    "search_pattern": {
                        "type": "string",
                        "description": "Pattern to search for (e.g., 'strcpy calls', 'crypto constants', 'shellcode patterns')"
                    },
                    "pattern_type": {
                        "type": "string",
                        "description": "Type of pattern search",
                        "enum": ["vulnerability_patterns", "crypto_algorithms", "packer_signatures", "anti_debug", "api_calls", "string_patterns"]
                    }
                },
                "required": ["binary_path", "search_pattern"]
            }
        ),
        Tool(
            name="gpt5_reverse_engineering_query",
            description="Direct GPT-5 query for reverse engineering, exploitation, or malware analysis questions",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Reverse engineering or exploitation question"
                    },
                    "context": {
                        "type": "string",
                        "description": "Additional context (assembly code, decompiled code, hex dumps, etc.)",
                        "default": ""
                    },
                    "specialization": {
                        "type": "string",
                        "description": "Area of specialization to focus on",
                        "enum": ["binary_exploitation", "malware_analysis", "firmware_hacking", "crypto_analysis", "reverse_engineering", "vulnerability_research"]
                    },
                    "preferred_model": {
                        "type": "string",
                        "description": "Preferred AI model (optional: gpt-4o, claude-3-5-sonnet, gemini-1.5-pro, grok-beta, llama3.2, etc.)",
                        "default": ""
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="ai_model_status",
            description="Check AI model availability, usage statistics, and configure AI preferences",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform",
                        "enum": ["status", "list_models", "usage_stats", "test_model"]
                    },
                    "model_name": {
                        "type": "string",
                        "description": "Model name for test_model action (optional)",
                        "default": ""
                    }
                },
                "required": ["action"]
            }
        ),
        # Tier 1 Binary Analysis Tools (Phase 1 Quick Wins)
        Tool(
            name="binary_strings_analysis",
            description="Extract and analyze strings from binary files with AI-powered interpretation",
            inputSchema={
                "type": "object",
                "properties": {
                    "binary_path": {
                        "type": "string",
                        "description": "Path to binary file for strings extraction"
                    },
                    "min_length": {
                        "type": "integer",
                        "description": "Minimum string length (default: 4)",
                        "default": 4
                    },
                    "encoding": {
                        "type": "string",
                        "description": "String encoding to search for",
                        "enum": ["ascii", "utf-8", "utf-16", "all"],
                        "default": "all"
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Output format",
                        "enum": ["text", "json"],
                        "default": "text"
                    },
                    "ai_analysis": {
                        "type": "boolean",
                        "description": "Enable AI-powered string analysis",
                        "default": True
                    }
                },
                "required": ["binary_path"]
            }
        ),
        Tool(
            name="binary_file_info",
            description="Get comprehensive file type information and metadata analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "binary_path": {
                        "type": "string",
                        "description": "Path to binary file"
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Output format",
                        "enum": ["text", "json"],
                        "default": "text"
                    },
                    "detailed": {
                        "type": "boolean",
                        "description": "Enable detailed analysis with AI interpretation",
                        "default": True
                    }
                },
                "required": ["binary_path"]
            }
        ),
        Tool(
            name="binary_objdump_analysis",
            description="Disassemble binary with objdump and provide AI-powered analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "binary_path": {
                        "type": "string",
                        "description": "Path to binary file"
                    },
                    "analysis_type": {
                        "type": "string",
                        "description": "Type of objdump analysis",
                        "enum": ["headers", "disassemble", "symbols", "sections", "relocs", "dynamic", "all"],
                        "default": "all"
                    },
                    "architecture": {
                        "type": "string",
                        "description": "Target architecture (auto-detected if not specified)",
                        "default": ""
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Output format",
                        "enum": ["text", "json"],
                        "default": "text"
                    },
                    "ai_analysis": {
                        "type": "boolean",
                        "description": "Enable AI-powered disassembly analysis",
                        "default": True
                    }
                },
                "required": ["binary_path"]
            }
        ),
        Tool(
            name="binary_readelf_analysis",
            description="Analyze ELF binaries with readelf and AI-powered interpretation",
            inputSchema={
                "type": "object",
                "properties": {
                    "binary_path": {
                        "type": "string",
                        "description": "Path to ELF binary file"
                    },
                    "analysis_type": {
                        "type": "string",
                        "description": "Type of readelf analysis",
                        "enum": ["headers", "sections", "symbols", "relocs", "dynamic", "notes", "all"],
                        "default": "all"
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Output format",
                        "enum": ["text", "json"],
                        "default": "text"
                    },
                    "ai_analysis": {
                        "type": "boolean",
                        "description": "Enable AI-powered ELF analysis",
                        "default": True
                    }
                },
                "required": ["binary_path"]
            }
        ),
        Tool(
            name="binary_hexdump_analysis",
            description="Generate hex dumps with pattern recognition and AI analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "binary_path": {
                        "type": "string",
                        "description": "Path to binary file"
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Starting offset (default: 0)",
                        "default": 0
                    },
                    "length": {
                        "type": "integer",
                        "description": "Number of bytes to dump (default: 512)",
                        "default": 512
                    },
                    "format": {
                        "type": "string",
                        "description": "Hex dump format",
                        "enum": ["canonical", "octal", "hex", "decimal"],
                        "default": "canonical"
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Output format",
                        "enum": ["text", "json"],
                        "default": "text"
                    },
                    "ai_analysis": {
                        "type": "boolean",
                        "description": "Enable AI-powered hex pattern analysis",
                        "default": True
                    }
                },
                "required": ["binary_path"]
            }
        ),
        # Phase 2: Binary Diffing Tools
        Tool(
            name="binary_diff_analysis",
            description="Compare two binary files with comprehensive diffing capabilities and AI security analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "binary_path_1": {
                        "type": "string",
                        "description": "Path to first binary file"
                    },
                    "binary_path_2": {
                        "type": "string",
                        "description": "Path to second binary file"
                    },
                    "diff_type": {
                        "type": "string",
                        "description": "Type of binary diffing to perform",
                        "enum": ["file", "strings", "functions", "metadata", "comprehensive"],
                        "default": "comprehensive"
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Output format",
                        "enum": ["text", "json", "html"],
                        "default": "text"
                    },
                    "ai_analysis": {
                        "type": "boolean",
                        "description": "Enable AI-powered security analysis of binary differences",
                        "default": True
                    }
                },
                "required": ["binary_path_1", "binary_path_2"]
            }
        ),
        Tool(
            name="patch_security_analysis",
            description="Analyze security implications of binary changes with patch analysis and vulnerability tracking",
            inputSchema={
                "type": "object",
                "properties": {
                    "original_binary": {
                        "type": "string",
                        "description": "Path to original (unpatched) binary file"
                    },
                    "patched_binary": {
                        "type": "string",
                        "description": "Path to patched binary file"
                    },
                    "analysis_depth": {
                        "type": "string",
                        "description": "Depth of security analysis",
                        "enum": ["quick", "standard", "comprehensive"],
                        "default": "standard"
                    },
                    "focus_areas": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Areas to focus analysis on",
                        "default": ["security", "performance", "functionality"]
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Output format",
                        "enum": ["text", "json", "html"],
                        "default": "text"
                    }
                },
                "required": ["original_binary", "patched_binary"]
            }
        ),
        Tool(
            name="version_evolution_analysis",
            description="Track changes across multiple binary versions with timeline and feature evolution tracking",
            inputSchema={
                "type": "object",
                "properties": {
                    "binary_versions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Paths to binary versions in chronological order"
                    },
                    "tracking_mode": {
                        "type": "string",
                        "description": "Type of evolution tracking",
                        "enum": ["timeline", "features", "security", "dependencies"],
                        "default": "timeline"
                    },
                    "comparison_baseline": {
                        "type": "string",
                        "description": "Baseline for comparison",
                        "enum": ["first", "previous", "specified"],
                        "default": "previous"
                    },
                    "generate_report": {
                        "type": "boolean",
                        "description": "Generate comprehensive evolution report",
                        "default": True
                    }
                },
                "required": ["binary_versions"]
            }
        ),
        Tool(
            name="binary_diff_report",
            description="Generate comprehensive binary difference reports with visualizations and security analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "diff_results": {
                        "type": "string",
                        "description": "Path to previous diff results JSON file"
                    },
                    "report_format": {
                        "type": "string",
                        "description": "Report output format",
                        "enum": ["html", "pdf", "markdown"],
                        "default": "html"
                    },
                    "include_visualizations": {
                        "type": "boolean",
                        "description": "Include graphical visualizations in report",
                        "default": True
                    },
                    "executive_summary": {
                        "type": "boolean",
                        "description": "Include executive summary with key findings",
                        "default": True
                    }
                },
                "required": ["diff_results"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    try:
        if name == "ghidra_binary_analysis":
            return await handle_binary_analysis(arguments)
        elif name == "ghidra_function_analysis":
            return await handle_function_analysis(arguments)
        elif name == "ghidra_exploit_development":
            return await handle_exploit_development(arguments)
        elif name == "ghidra_malware_analysis":
            return await handle_malware_analysis(arguments)
        elif name == "ghidra_firmware_analysis":
            return await handle_firmware_analysis(arguments)
        elif name == "ghidra_code_pattern_search":
            return await handle_pattern_search(arguments)
        elif name == "gpt5_reverse_engineering_query":
            return await handle_gpt5_query(arguments)
        elif name == "ai_model_status":
            return await handle_ai_model_status(arguments)
        # Tier 1 Binary Analysis Tools (Phase 1 Quick Wins)
        elif name == "binary_strings_analysis":
            return await handle_strings_analysis(arguments)
        elif name == "binary_file_info":
            return await handle_file_info(arguments)
        elif name == "binary_objdump_analysis":
            return await handle_objdump_analysis(arguments)
        elif name == "binary_readelf_analysis":
            return await handle_readelf_analysis(arguments)
        elif name == "binary_hexdump_analysis":
            return await handle_hexdump_analysis(arguments)
        # Phase 2 Binary Diffing Tools
        elif name == "binary_diff_analysis":
            return await handle_binary_diff_analysis(arguments)
        elif name == "patch_security_analysis":
            return await handle_patch_security_analysis(arguments)
        elif name == "version_evolution_analysis":
            return await handle_version_evolution_analysis(arguments)
        elif name == "binary_diff_report":
            return await handle_binary_diff_report(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        logger.error(f"Error handling tool call {name}: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

def get_openai_api_key() -> str:
    """Get OpenAI API key from environment or config"""
    # Try multiple environment variable names
    key_vars = ['OPENAI_API_KEY', 'CHATGPT_COOKIE']  # CHATGPT_COOKIE from your env
    
    for var in key_vars:
        key = os.environ.get(var)
        if key and key.strip():
            # Extract API key if it's in the format of your CHATGPT_COOKIE
            if key.startswith('sk-'):
                return key.strip()
    
    raise RuntimeError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable")

async def query_gpt5_with_retry(messages: List[Dict[str, str]], operation_type: str = "analysis") -> str:
    """Enhanced multi-model AI query with automatic fallback support"""
    
    # Try to use multi-model system first
    try:
        from ai_providers import query_ai_with_fallback
        
        # Get preferred model from environment
        preferred_model = os.environ.get('AI_MODEL_PREFERENCE')
        
        response, metadata = await query_ai_with_fallback(messages, operation_type, preferred_model)
        
        # Log model used and cost
        model = metadata.get('model', 'unknown')
        provider = metadata.get('provider', 'unknown')
        cost = metadata.get('estimated_cost', 0)
        
        logger.info(f"AI response received: {model} ({provider}) - ${cost:.4f} (attempt 1)")
        return response
        
    except ImportError:
        logger.warning("Multi-model system unavailable, falling back to OpenAI")
    except Exception as e:
        logger.warning(f"Multi-model query failed: {e}, falling back to OpenAI")
    
    # Fallback to original OpenAI-only implementation
    api_key = get_openai_api_key()
    
    # Determine max tokens based on operation type
    max_tokens = {
        "analysis": MAX_TOKENS_ANALYSIS,
        "exploit": MAX_TOKENS_EXPLOIT,
        "query": MAX_TOKENS_DEFAULT
    }.get(operation_type, MAX_TOKENS_DEFAULT)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": GPT_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.1,  # Lower temperature for more focused technical analysis
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(OPENAI_CHAT_ENDPOINT, headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        if 'choices' in result and len(result['choices']) > 0:
                            content = result['choices'][0]['message']['content']
                            logger.info(f"OpenAI response received for {operation_type} (attempt {attempt + 1})")
                            return content
                        else:
                            raise Exception("Empty response from OpenAI")
                    elif response.status == 429:
                        # Rate limit - wait longer
                        wait_time = RETRY_DELAY * (2 ** attempt)
                        logger.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        error_text = await response.text()
                        raise Exception(f"HTTP {response.status}: {error_text}")
                        
        except asyncio.TimeoutError:
            logger.warning(f"Request timeout on attempt {attempt + 1}")
            if attempt == MAX_RETRIES - 1:
                raise Exception("Request timed out after all retries")
            await asyncio.sleep(RETRY_DELAY)
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt == MAX_RETRIES - 1:
                raise Exception(f"All retry attempts failed. Last error: {str(e)}")
            await asyncio.sleep(RETRY_DELAY)
    
    raise Exception("Unexpected error in retry logic")

def run_ghidra_headless(binary_path: str, script_path: str = None, additional_args: List[str] = None) -> str:
    """Run Ghidra in headless mode for binary analysis"""
    
    if not os.path.exists(binary_path):
        raise Exception(f"Binary file not found: {binary_path}")
    
    # Ensure project directory exists
    os.makedirs(GHIDRA_PROJECT_DIR, exist_ok=True)
    
    # Create temporary project name
    import uuid
    project_name = f"ghidra_analysis_{uuid.uuid4().hex[:8]}"
    project_path = os.path.join(GHIDRA_PROJECT_DIR, project_name)
    
    # Basic Ghidra headless command
    cmd = [
        GHIDRA_HEADLESS_PATH,
        project_path,
        project_name,
        "-import", binary_path,
        "-analyzeAll",
        "-scriptPath", "/opt/ghidra/Ghidra/Features/Python/ghidra_scripts",
        "-deleteProject"  # Clean up after analysis
    ]
    
    # Add custom script if provided
    if script_path and os.path.exists(script_path):
        cmd.extend(["-postScript", script_path])
    
    # Add additional arguments
    if additional_args:
        cmd.extend(additional_args)
    
    try:
        logger.info(f"Running Ghidra analysis on {binary_path}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            return result.stdout
        else:
            error_msg = f"Ghidra analysis failed (return code {result.returncode}):\n{result.stderr}"
            logger.error(error_msg)
            return error_msg
            
    except subprocess.TimeoutExpired:
        return "Ghidra analysis timed out after 5 minutes"
    except Exception as e:
        return f"Error running Ghidra: {str(e)}"

async def handle_binary_analysis(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle comprehensive binary analysis using Ghidra + GPT-5"""
    # Import security utilities
    try:
        from security_utils import validate_binary_analysis_args, SecurityError
        # Validate and sanitize inputs
        validated_args = validate_binary_analysis_args(arguments)
        binary_path = validated_args["binary_path"]
        analysis_depth = validated_args.get("analysis_depth", "standard")
        focus_areas = validated_args.get("focus_areas", [])
    except (ImportError, SecurityError) as e:
        logger.error(f"Security validation failed: {e}")
        return [TextContent(type="text", text=f"Security validation failed: {str(e)}")]
    except Exception as e:
        # Fallback to basic validation if security module unavailable
        logger.warning(f"Security module unavailable, using basic validation: {e}")
        binary_path = arguments["binary_path"]
        analysis_depth = arguments.get("analysis_depth", "standard")
        focus_areas = arguments.get("focus_areas", [])
    
    # Run Ghidra analysis
    ghidra_output = run_ghidra_headless(binary_path)
    
    # Build specialized prompt based on analysis depth
    depth_prompts = {
        "quick": "Provide a rapid assessment focusing on high-level structure and obvious security issues.",
        "standard": "Perform comprehensive analysis including function analysis, security assessment, and architectural overview.",
        "deep": "Conduct exhaustive analysis including advanced vulnerability research, algorithm identification, and exploitation assessment.",
        "exploit_focused": "Focus specifically on exploitation opportunities, vulnerability chains, and attack surface analysis."
    }
    
    focus_context = ""
    if focus_areas:
        focus_context = f"\nPay special attention to these areas: {', '.join(focus_areas)}"
    
    system_prompt = f"""You are an expert reverse engineer and binary analyst using GPT-5 for advanced binary analysis. 
    
Analyze the following Ghidra output for a binary analysis with {analysis_depth} depth.
{depth_prompts.get(analysis_depth, "Perform standard analysis.")}
{focus_context}

Provide your analysis in the following structure:
1. **Binary Overview** - Architecture, packing, compilation details
2. **Security Assessment** - Identified vulnerabilities and security features
3. **Function Analysis** - Key functions and their purposes  
4. **Exploitation Opportunities** - Potential attack vectors and exploitability
5. **Recommendations** - Next steps for further analysis or exploitation
6. **Technical Details** - Important addresses, offsets, and technical notes

Be specific, actionable, and focus on information useful for penetration testing and security research."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Binary: {binary_path}\n\nGhidra Analysis Output:\n{ghidra_output}"}
    ]
    
    response = await query_gpt5_with_retry(messages, "analysis")
    return [TextContent(type="text", text=response)]

async def handle_function_analysis(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle specific function analysis using Ghidra decompilation + GPT-5"""
    binary_path = arguments["binary_path"]
    function_address = arguments["function_address"]
    analysis_type = arguments.get("analysis_type", "vulnerability_scan")
    
    # Create custom Ghidra script for function-specific analysis
    script_content = f"""
# Ghidra script for function analysis
from ghidra.program.model.address import *
from ghidra.program.model.listing import *

def analyze_function():
    fm = currentProgram.getFunctionManager()
    addr = toAddr("{function_address}")
    func = fm.getFunctionAt(addr)
    
    if func is None:
        print(f"No function found at address {function_address}")
        return
    
    print(f"Function: {{func.getName()}} at {{func.getEntryPoint()}}")
    print(f"Parameters: {{func.getParameterCount()}}")
    
    # Get decompiled code
    from ghidra.app.decompiler import DecompInterface
    decomp_ifc = DecompInterface()
    decomp_ifc.openProgram(currentProgram)
    
    result = decomp_ifc.decompileFunction(func, 30, None)
    if result.decompileCompleted():
        print("DECOMPILED_CODE:")
        print(result.getDecompiledFunction().getC())
    else:
        print("Decompilation failed")

analyze_function()
"""
    
    # Write temporary script
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script_content)
        script_path = f.name
    
    try:
        # Run Ghidra with custom script
        ghidra_output = run_ghidra_headless(binary_path, script_path)
        
        analysis_prompts = {
            "vulnerability_scan": "Focus on identifying security vulnerabilities, buffer overflows, format string bugs, and other exploitable conditions.",
            "algorithm_identification": "Identify the algorithm or cryptographic function being implemented.",
            "crypto_analysis": "Analyze cryptographic implementations for weaknesses, hardcoded keys, or implementation flaws.",
            "exploit_potential": "Assess the exploitability of this function and potential attack vectors.",
            "behavioral_analysis": "Analyze the behavior and purpose of this function in the overall program flow."
        }
        
        system_prompt = f"""You are an expert reverse engineer analyzing a specific function using GPT-5.
        
Function Analysis Type: {analysis_type}
{analysis_prompts.get(analysis_type, "Perform general function analysis.")}

Provide detailed analysis including:
1. **Function Purpose** - What does this function do?
2. **Security Analysis** - Vulnerabilities, weaknesses, security implications
3. **Parameters & Return Values** - Analysis of input/output
4. **Control Flow** - Important branches, loops, conditions  
5. **Exploitation Assessment** - How this function could be exploited
6. **Recommendations** - Specific advice for penetration testing or exploitation

Be technical, specific, and actionable."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Function at {function_address} in {binary_path}:\n\nGhidra Analysis:\n{ghidra_output}"}
        ]
        
        response = await query_gpt5_with_retry(messages, "analysis")
        return [TextContent(type="text", text=response)]
        
    finally:
        # Clean up temporary script
        try:
            os.unlink(script_path)
        except:
            pass

async def handle_exploit_development(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle exploit development analysis"""
    binary_path = arguments["binary_path"]
    target_platform = arguments["target_platform"]
    exploit_type = arguments.get("exploit_type", "buffer_overflow")
    generate_poc = arguments.get("generate_poc", False)
    
    # Run targeted Ghidra analysis for exploitation
    ghidra_output = run_ghidra_headless(binary_path)
    
    system_prompt = f"""You are an expert exploit developer using GPT-5 for advanced exploitation research.

Target Platform: {target_platform}
Exploitation Focus: {exploit_type}
Generate PoC: {generate_poc}

Analyze the binary for exploitation opportunities focusing on {exploit_type} vulnerabilities.

Provide comprehensive exploitation analysis:
1. **Vulnerability Assessment** - Identify exploitable conditions
2. **Attack Vector Analysis** - How to trigger and exploit vulnerabilities  
3. **Exploitation Strategy** - Step-by-step exploitation approach
4. **Payload Development** - Shellcode and ROP chain considerations
5. **ASLR/DEP Bypass** - Techniques to bypass modern protections
6. **Exploitation Timeline** - Difficulty and time estimation
{'7. **Proof of Concept** - Complete working exploit code' if generate_poc else '7. **PoC Outline** - Detailed steps to create working exploit'}

Focus on practical, working exploitation techniques for {target_platform}."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Target Binary: {binary_path}\nPlatform: {target_platform}\n\nGhidra Analysis:\n{ghidra_output}"}
    ]
    
    response = await query_gpt5_with_retry(messages, "exploit")
    return [TextContent(type="text", text=response)]

async def handle_malware_analysis(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle malware analysis using Ghidra + GPT-5"""
    malware_path = arguments["malware_path"]
    analysis_scope = arguments.get("analysis_scope", "static_only")
    sandbox_mode = arguments.get("sandbox_mode", True)
    
    # Safety warning
    safety_warning = "⚠️  MALWARE ANALYSIS MODE - Ensure you are in a secure, isolated environment!"
    
    # Run Ghidra analysis
    ghidra_output = run_ghidra_headless(malware_path)
    
    scope_prompts = {
        "static_only": "Focus on static analysis without executing the malware.",
        "behavioral": "Analyze expected runtime behavior, network connections, and system modifications.",
        "network_analysis": "Focus on network communication, C2 infrastructure, and data exfiltration.",
        "persistence_mechanisms": "Identify how the malware maintains persistence and avoids detection.",
        "evasion_techniques": "Analyze anti-analysis, anti-debug, and evasion techniques."
    }
    
    system_prompt = f"""You are an expert malware analyst using GPT-5 for advanced malware reverse engineering.

Analysis Scope: {analysis_scope}
Sandbox Environment: {sandbox_mode}
{scope_prompts.get(analysis_scope, "Perform comprehensive malware analysis.")}

Provide detailed malware analysis:
1. **Malware Classification** - Type, family, variant identification
2. **Behavioral Analysis** - Expected runtime behavior and capabilities
3. **Network Analysis** - C2 communication, data exfiltration methods
4. **Persistence Mechanisms** - How malware maintains presence
5. **Evasion Techniques** - Anti-analysis and stealth capabilities  
6. **IOCs (Indicators of Compromise)** - Network signatures, file artifacts
7. **Mitigation Strategies** - Detection and removal recommendations
8. **Attribution Assessment** - Possible threat actor indicators

Focus on actionable intelligence for incident response and threat hunting."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Malware Sample: {malware_path}\n\n{safety_warning}\n\nGhidra Analysis:\n{ghidra_output}"}
    ]
    
    response = await query_gpt5_with_retry(messages, "analysis")
    return [TextContent(type="text", text=f"{safety_warning}\n\n{response}")]

async def handle_firmware_analysis(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle firmware analysis using Ghidra + GPT-5"""
    firmware_path = arguments["firmware_path"]
    architecture = arguments.get("architecture", "auto_detect")
    device_type = arguments.get("device_type", "unknown")
    
    # Run Ghidra analysis
    ghidra_output = run_ghidra_headless(firmware_path)
    
    system_prompt = f"""You are an expert firmware security researcher using GPT-5 for IoT and embedded system analysis.

Architecture: {architecture}
Device Type: {device_type}

Analyze the firmware for security vulnerabilities and exploitation opportunities:

1. **Firmware Overview** - Architecture, OS, compilation details
2. **Security Assessment** - Hardcoded credentials, crypto keys, vulnerabilities  
3. **Attack Surface** - Network services, web interfaces, update mechanisms
4. **Exploitation Opportunities** - Buffer overflows, authentication bypasses
5. **Backdoors & Debug Features** - Hidden functionality, debug interfaces
6. **Crypto Analysis** - Key storage, encryption implementations
7. **Hardware Security** - Boot security, secure boot bypass
8. **Post-Exploitation** - Persistence, lateral movement opportunities

Focus on practical attack vectors for IoT penetration testing and hardware hacking."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Firmware: {firmware_path}\nArch: {architecture}\nDevice: {device_type}\n\nGhidra Analysis:\n{ghidra_output}"}
    ]
    
    response = await query_gpt5_with_retry(messages, "analysis")
    return [TextContent(type="text", text=response)]

async def handle_pattern_search(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle code pattern search using Ghidra + GPT-5"""
    binary_path = arguments["binary_path"]
    search_pattern = arguments["search_pattern"]
    pattern_type = arguments["pattern_type"]
    
    # Run Ghidra analysis
    ghidra_output = run_ghidra_headless(binary_path)
    
    pattern_prompts = {
        "vulnerability_patterns": "Search for common vulnerability patterns like buffer overflows, format strings, race conditions.",
        "crypto_algorithms": "Identify cryptographic algorithms, constants, and implementations.",
        "packer_signatures": "Look for packing, obfuscation, or anti-analysis techniques.",
        "anti_debug": "Find anti-debugging and evasion mechanisms.",
        "api_calls": "Analyze Windows/Linux API calls and system interactions.",
        "string_patterns": "Search for specific string patterns, URLs, file paths, or configurations."
    }
    
    system_prompt = f"""You are an expert code pattern analyst using GPT-5 for binary analysis.

Search Pattern: {search_pattern}
Pattern Type: {pattern_type}
{pattern_prompts.get(pattern_type, "Search for the specified pattern.")}

Analyze the binary and provide:
1. **Pattern Matches** - Specific locations where patterns were found
2. **Context Analysis** - What these patterns mean in the overall program
3. **Security Implications** - Security impact of identified patterns
4. **Exploitation Potential** - How patterns could be exploited
5. **Related Patterns** - Additional patterns to investigate
6. **Recommendations** - Next steps for investigation or exploitation

Be specific about addresses, function names, and exploitation potential."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Binary: {binary_path}\nSearch for: {search_pattern}\n\nGhidra Analysis:\n{ghidra_output}"}
    ]
    
    response = await query_gpt5_with_retry(messages, "analysis")
    return [TextContent(type="text", text=response)]

async def handle_gpt5_query(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle direct GPT-5 queries for reverse engineering"""
    # Import security utilities for input validation
    try:
        from security_utils import validate_gpt5_query_args, SecurityError
        # Validate and sanitize inputs
        validated_args = validate_gpt5_query_args(arguments)
        query = validated_args["query"]
        context = validated_args.get("context", "")
        specialization = validated_args.get("specialization", "reverse_engineering")
        preferred_model = validated_args.get("preferred_model", "")
    except (ImportError, SecurityError) as e:
        logger.error(f"Security validation failed: {e}")
        return [TextContent(type="text", text=f"Input validation failed: {str(e)}")]
    except Exception as e:
        # Fallback to basic validation if security module unavailable
        logger.warning(f"Security module unavailable, using basic validation: {e}")
        query = arguments["query"]
        context = arguments.get("context", "")
        specialization = arguments.get("specialization", "reverse_engineering")
        preferred_model = arguments.get("preferred_model", "")
    
    specialization_prompts = {
        "binary_exploitation": "Expert in buffer overflows, ROP chains, heap exploitation, and modern exploit mitigation bypasses.",
        "malware_analysis": "Specialist in malware reverse engineering, behavioral analysis, and threat intelligence.",
        "firmware_hacking": "Expert in IoT security, embedded systems, and hardware hacking techniques.",
        "crypto_analysis": "Cryptographic implementation analysis, key recovery, and cryptographic vulnerabilities.",
        "reverse_engineering": "General reverse engineering, disassembly, and program analysis expertise.",
        "vulnerability_research": "Zero-day discovery, vulnerability analysis, and security research methodologies."
    }
    
    system_prompt = f"""You are a world-class cybersecurity expert using GPT-5 with deep specialization in {specialization}.

{specialization_prompts.get(specialization, "Expert in reverse engineering and binary analysis.")}

Provide detailed, technical, and actionable responses. Include:
- Specific techniques and methodologies
- Tool recommendations and usage
- Code examples where appropriate  
- Step-by-step procedures
- Common pitfalls and how to avoid them
- Advanced techniques for experienced practitioners

Always assume the user has proper authorization for any security testing activities."""

    additional_context = f"\n\nAdditional Context:\n{context}" if context else ""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{query}{additional_context}"}
    ]
    
    response = await query_gpt5_with_retry(messages, "query")
    return [TextContent(type="text", text=response)]

async def handle_ai_model_status(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle AI model status, configuration, and testing"""
    action = arguments["action"]
    model_name = arguments.get("model_name", "")
    
    try:
        from ai_providers import get_model_status, model_manager
        
        if action == "status":
            # Get comprehensive status
            status = get_model_status()
            
            output = "🤖 **AI Model Status Report**\n\n"
            output += f"**Current Configuration:**\n"
            output += f"- Default Model: {status['model_manager']['default_model']}\n"
            output += f"- Available Models: {len(status['model_manager']['available_models'])}/{status['model_manager']['total_models']}\n"
            output += f"- Total API Calls: {status['model_manager']['total_calls']}\n\n"
            
            output += "**Provider Status:**\n"
            for provider, models in status['providers'].items():
                api_key_status = "✅" if status['environment_keys'].get(provider, False) else "❌"
                output += f"- {provider.title()}: {api_key_status}\n"
                for model in models:
                    output += f"  - {model}\n"
            
            output += "\n**Environment Variables:**\n"
            env_vars = {
                'OPENAI_API_KEY': 'OpenAI GPT-4o/GPT-5',
                'ANTHROPIC_API_KEY': 'Claude 3.5 Sonnet', 
                'GEMINI_API_KEY': 'Google Gemini',
                'GROK_API_KEY': 'xAI Grok',
                'PERPLEXITY_API_KEY': 'Perplexity',
                'DEEPSEEK_API_KEY': 'DeepSeek',
                'AI_MODEL_PREFERENCE': 'Preferred model override'
            }
            
            for env_var, description in env_vars.items():
                value = os.environ.get(env_var, 'Not set')
                if env_var.endswith('_API_KEY') and value != 'Not set':
                    value = f"{value[:10]}..." if len(value) > 10 else value
                output += f"- {env_var}: {value} ({description})\n"
            
            return [TextContent(type="text", text=output)]
            
        elif action == "list_models":
            # List all available models
            providers = model_manager.list_providers()
            
            output = "🔍 **Available AI Models**\n\n"
            for provider, models in providers.items():
                output += f"**{provider.title()} Provider:**\n"
                for model in models:
                    output += f"  {model}\n"
                output += "\n"
            
            output += "**Usage Instructions:**\n"
            output += "```python\n"
            output += 'call_mcp_tool("gpt5_reverse_engineering_query", {\n'
            output += '    "query": "Your question here",\n'
            output += '    "preferred_model": "claude-3-5-sonnet"  # Optional\n'
            output += '})\n'
            output += "```\n"
            
            return [TextContent(type="text", text=output)]
            
        elif action == "usage_stats":
            # Get usage statistics
            stats = model_manager.get_usage_stats()
            
            output = "📊 **AI Model Usage Statistics**\n\n"
            output += f"- Total API Calls: {stats['total_calls']}\n"
            output += f"- Available Models: {len(stats['available_models'])}\n"
            output += f"- Most Used Model: {stats.get('most_used_model', 'None')}\n\n"
            
            if stats['usage_by_model']:
                output += "**Usage by Model:**\n"
                for model, count in sorted(stats['usage_by_model'].items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / stats['total_calls']) * 100 if stats['total_calls'] > 0 else 0
                    output += f"- {model}: {count} calls ({percentage:.1f}%)\n"
            else:
                output += "No usage data available yet.\n"
            
            return [TextContent(type="text", text=output)]
            
        elif action == "test_model":
            # Test specific model
            if not model_name:
                return [TextContent(type="text", text="Error: model_name required for test_model action")]
            
            if not model_manager.is_model_available(model_name):
                return [TextContent(type="text", text=f"Error: Model '{model_name}' is not available. Check API keys and installation.")]
            
            # Test the model with a simple query
            test_messages = [
                {"role": "system", "content": "You are a helpful AI assistant. Respond concisely."},
                {"role": "user", "content": "Please respond with 'Test successful!' to confirm this model is working."}
            ]
            
            try:
                response, metadata = await model_manager.query_model(test_messages, model_name, 50)
                
                output = f"🧪 **Model Test Results: {model_name}**\n\n"
                output += f"✅ **Status:** Working\n"
                output += f"📡 **Provider:** {metadata.get('provider', 'unknown')}\n"
                output += f"💰 **Estimated Cost:** ${metadata.get('estimated_cost', 0):.4f}\n"
                output += f"📝 **Response:** {response[:100]}...\n\n"
                output += "This model is ready for reverse engineering tasks!\n"
                
                return [TextContent(type="text", text=output)]
                
            except Exception as e:
                output = f"❌ **Model Test Failed: {model_name}**\n\n"
                output += f"**Error:** {str(e)}\n\n"
                output += "**Troubleshooting:**\n"
                output += "- Check API key configuration\n"
                output += "- Verify network connectivity\n"
                output += "- Ensure model name is correct\n"
                
                return [TextContent(type="text", text=output)]
        
        else:
            return [TextContent(type="text", text=f"Unknown action: {action}")]
            
    except ImportError:
        return [TextContent(type="text", text="❌ Multi-model system not available. Only OpenAI GPT-4o is supported.")]
    except Exception as e:
        logger.error(f"AI model status error: {e}")
        return [TextContent(type="text", text=f"Error getting AI model status: {str(e)}")]

# ===== TIER 1 BINARY ANALYSIS TOOL HANDLERS (Phase 1 Quick Wins) =====

async def handle_strings_analysis(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle strings extraction and analysis"""
    try:
        from tier1_tools import run_strings_analysis, format_output_as_json, format_output_as_text
        
        binary_path = arguments["binary_path"]
        min_length = arguments.get("min_length", 4)
        encoding = arguments.get("encoding", "all")
        output_format = arguments.get("output_format", "text")
        ai_analysis = arguments.get("ai_analysis", True)
        
        # Run strings analysis
        result = await run_strings_analysis(binary_path, min_length, encoding)
        
        # Format output
        if output_format == "json":
            formatted_result = format_output_as_json(result, "strings")
            output_text = json.dumps(formatted_result, indent=2)
        else:
            output_text = format_output_as_text(result, "strings")
        
        # Add AI analysis if requested
        if ai_analysis and result.get("results"):
            # Extract interesting strings for AI analysis
            all_patterns = {}
            total_strings = 0
            
            for enc_result in result["results"].values():
                if isinstance(enc_result, dict) and "sample_analysis" in enc_result:
                    patterns = enc_result["sample_analysis"]
                    for pattern_type, items in patterns.items():
                        if items:
                            all_patterns.setdefault(pattern_type, []).extend(items)
                    total_strings += enc_result.get("count", 0)
            
            if all_patterns and any(all_patterns.values()):
                ai_prompt = f"""Analyze the following strings extracted from a binary file and provide security insights:

Binary: {binary_path}
Total strings found: {total_strings}

Interesting patterns found:
"""
                for pattern_type, items in all_patterns.items():
                    if items:
                        ai_prompt += f"\n{pattern_type.upper()}:\n"
                        for item in items[:10]:  # Limit to 10 items per category
                            ai_prompt += f"  - {item}\n"
                
                ai_prompt += "\n\nProvide analysis focusing on:\n1. Security implications of these strings\n2. Potential attack vectors or vulnerabilities\n3. Information disclosure risks\n4. Suspicious or interesting findings\n5. Recommendations for further investigation"
                
                messages = [
                    {"role": "system", "content": "You are a cybersecurity expert analyzing binary strings for security implications."},
                    {"role": "user", "content": ai_prompt}
                ]
                
                try:
                    ai_response = await query_gpt5_with_retry(messages, "analysis")
                    output_text += f"\n\n=== AI SECURITY ANALYSIS ===\n{ai_response}"
                except Exception as e:
                    logger.warning(f"AI analysis failed: {e}")
                    output_text += f"\n\n=== AI ANALYSIS UNAVAILABLE ===\nError: {str(e)}"
        
        return [TextContent(type="text", text=output_text)]
        
    except Exception as e:
        logger.error(f"Strings analysis failed: {e}")
        return [TextContent(type="text", text=f"Strings analysis failed: {str(e)}")]

async def handle_file_info(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle file information analysis"""
    try:
        from tier1_tools import run_file_analysis, format_output_as_json, format_output_as_text
        
        binary_path = arguments["binary_path"]
        output_format = arguments.get("output_format", "text")
        detailed = arguments.get("detailed", True)
        
        # Run file analysis
        result = await run_file_analysis(binary_path)
        
        # Format output
        if output_format == "json":
            formatted_result = format_output_as_json(result, "file")
            output_text = json.dumps(formatted_result, indent=2)
        else:
            output_text = format_output_as_text(result, "file")
        
        # Add AI analysis if detailed analysis is requested
        if detailed and result.get("basic", {}).get("success"):
            file_info = result["basic"]["output"]
            mime_info = result.get("mime", {}).get("output", "")
            file_stats = result.get("file_stats", {})
            
            ai_prompt = f"""Analyze this file information and provide security assessment:

File: {binary_path}
File command output: {file_info}
MIME type: {mime_info}
File size: {file_stats.get('size', 'unknown')} bytes
Executable: {file_stats.get('is_executable', 'unknown')}

Provide analysis focusing on:
1. File type and architecture implications
2. Potential security risks or concerns
3. Interesting characteristics or anomalies
4. Recommended analysis approaches
5. Exploitation potential assessment"""
            
            messages = [
                {"role": "system", "content": "You are a cybersecurity expert analyzing file metadata for security implications."},
                {"role": "user", "content": ai_prompt}
            ]
            
            try:
                ai_response = await query_gpt5_with_retry(messages, "analysis")
                output_text += f"\n\n=== AI SECURITY ANALYSIS ===\n{ai_response}"
            except Exception as e:
                logger.warning(f"AI analysis failed: {e}")
                output_text += f"\n\n=== AI ANALYSIS UNAVAILABLE ===\nError: {str(e)}"
        
        return [TextContent(type="text", text=output_text)]
        
    except Exception as e:
        logger.error(f"File analysis failed: {e}")
        return [TextContent(type="text", text=f"File analysis failed: {str(e)}")]

async def handle_objdump_analysis(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle objdump disassembly and analysis"""
    try:
        from tier1_tools import run_objdump_analysis, format_output_as_json, format_output_as_text
        
        binary_path = arguments["binary_path"]
        analysis_type = arguments.get("analysis_type", "all")
        architecture = arguments.get("architecture", "")
        output_format = arguments.get("output_format", "text")
        ai_analysis = arguments.get("ai_analysis", True)
        
        # Run objdump analysis
        result = await run_objdump_analysis(binary_path, analysis_type, architecture)
        
        # Format output
        if output_format == "json":
            formatted_result = format_output_as_json(result, "objdump")
            output_text = json.dumps(formatted_result, indent=2)
        else:
            output_text = format_output_as_text(result, "objdump")
        
        # Add AI analysis if requested
        if ai_analysis and result.get("results"):
            # Summarize results for AI analysis
            analysis_summary = f"Objdump analysis results for {binary_path}:\n\n"
            
            for analysis_name, analysis_data in result["results"].items():
                if analysis_data.get("success"):
                    summary = analysis_data.get("summary", {})
                    analysis_summary += f"{analysis_name.upper()}:\n"
                    if summary:
                        for key, value in summary.items():
                            analysis_summary += f"  - {key}: {value}\n"
                    
                    # Include first few lines of output for context
                    output = analysis_data.get("output", "")
                    if output:
                        lines = output.split('\n')[:10]  # First 10 lines
                        analysis_summary += f"  Sample output:\n"
                        for line in lines:
                            if line.strip():
                                analysis_summary += f"    {line}\n"
                    analysis_summary += "\n"
            
            ai_prompt = f"""{analysis_summary}

Provide comprehensive binary analysis focusing on:
1. Architecture and compilation characteristics
2. Security features and mitigations present
3. Potential vulnerabilities or attack vectors
4. Function analysis and entry points
5. Exploitation assessment and recommendations
6. Suspicious patterns or anomalies"""
            
            messages = [
                {"role": "system", "content": "You are a cybersecurity expert analyzing objdump output for security implications."},
                {"role": "user", "content": ai_prompt}
            ]
            
            try:
                ai_response = await query_gpt5_with_retry(messages, "analysis")
                output_text += f"\n\n=== AI SECURITY ANALYSIS ===\n{ai_response}"
            except Exception as e:
                logger.warning(f"AI analysis failed: {e}")
                output_text += f"\n\n=== AI ANALYSIS UNAVAILABLE ===\nError: {str(e)}"
        
        return [TextContent(type="text", text=output_text)]
        
    except Exception as e:
        logger.error(f"Objdump analysis failed: {e}")
        return [TextContent(type="text", text=f"Objdump analysis failed: {str(e)}")]

async def handle_readelf_analysis(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle readelf ELF analysis"""
    try:
        from tier1_tools import run_readelf_analysis, format_output_as_json, format_output_as_text
        
        binary_path = arguments["binary_path"]
        analysis_type = arguments.get("analysis_type", "all")
        output_format = arguments.get("output_format", "text")
        ai_analysis = arguments.get("ai_analysis", True)
        
        # Run readelf analysis
        result = await run_readelf_analysis(binary_path, analysis_type)
        
        # Format output
        if output_format == "json":
            formatted_result = format_output_as_json(result, "readelf")
            output_text = json.dumps(formatted_result, indent=2)
        else:
            output_text = format_output_as_text(result, "readelf")
        
        # Add AI analysis if requested
        if ai_analysis and result.get("results"):
            # Summarize results for AI analysis
            analysis_summary = f"Readelf ELF analysis results for {binary_path}:\n\n"
            
            for analysis_name, analysis_data in result["results"].items():
                if analysis_data.get("success"):
                    summary = analysis_data.get("summary", {})
                    analysis_summary += f"{analysis_name.upper()}:\n"
                    if summary:
                        for key, value in summary.items():
                            analysis_summary += f"  - {key}: {value}\n"
                    
                    # Include relevant lines from output
                    output = analysis_data.get("output", "")
                    if output and analysis_name == "headers":
                        lines = [line for line in output.split('\n')[:20] if line.strip()]  # First 20 lines
                        analysis_summary += f"  Key information:\n"
                        for line in lines:
                            if any(keyword in line for keyword in ["Class:", "Data:", "Machine:", "Entry point:"]):
                                analysis_summary += f"    {line.strip()}\n"
                    analysis_summary += "\n"
            
            ai_prompt = f"""{analysis_summary}

Provide ELF-specific security analysis focusing on:
1. ELF structure and format analysis
2. Security mitigations and protections
3. Dynamic linking and library dependencies
4. Entry points and execution flow
5. Potential exploitation vectors
6. Suspicious sections or symbols
7. Recommendations for further analysis"""
            
            messages = [
                {"role": "system", "content": "You are a cybersecurity expert analyzing ELF binaries for security implications."},
                {"role": "user", "content": ai_prompt}
            ]
            
            try:
                ai_response = await query_gpt5_with_retry(messages, "analysis")
                output_text += f"\n\n=== AI SECURITY ANALYSIS ===\n{ai_response}"
            except Exception as e:
                logger.warning(f"AI analysis failed: {e}")
                output_text += f"\n\n=== AI ANALYSIS UNAVAILABLE ===\nError: {str(e)}"
        
        return [TextContent(type="text", text=output_text)]
        
    except Exception as e:
        logger.error(f"Readelf analysis failed: {e}")
        return [TextContent(type="text", text=f"Readelf analysis failed: {str(e)}")]

async def handle_hexdump_analysis(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle hexdump analysis with pattern recognition"""
    try:
        from tier1_tools import run_hexdump_analysis, format_output_as_json, format_output_as_text
        
        binary_path = arguments["binary_path"]
        offset = arguments.get("offset", 0)
        length = arguments.get("length", 512)
        format_type = arguments.get("format", "canonical")
        output_format = arguments.get("output_format", "text")
        ai_analysis = arguments.get("ai_analysis", True)
        
        # Run hexdump analysis
        result = await run_hexdump_analysis(binary_path, offset, length, format_type)
        
        # Format output
        if output_format == "json":
            formatted_result = format_output_as_json(result, "hexdump")
            output_text = json.dumps(formatted_result, indent=2)
        else:
            output_text = format_output_as_text(result, "hexdump")
        
        # Add AI analysis if requested
        if ai_analysis and result.get("success") and result.get("pattern_analysis"):
            patterns = result["pattern_analysis"]
            hex_output = result.get("output", "")
            
            ai_prompt = f"""Analyze this hex dump from a binary file:

File: {binary_path}
Offset: {offset}, Length: {length} bytes

Pattern Analysis:
- Null bytes: {patterns.get('null_bytes', 0)}
- Printable ratio: {patterns.get('printable_ratio', 0):.2%}
- Entropy estimate: {patterns.get('entropy_estimate', 0):.2f}
- Magic signatures found: {patterns.get('magic_signatures', [])}

Hex dump (first 10 lines):
{chr(10).join(hex_output.split(chr(10))[:10])}

Provide analysis focusing on:
1. Data structure patterns and format identification
2. Potential embedded files or resources
3. Cryptographic signatures or keys
4. Suspicious or anomalous patterns
5. File format verification
6. Security implications of the data
7. Recommendations for further investigation"""
            
            messages = [
                {"role": "system", "content": "You are a cybersecurity expert analyzing hex dumps for security implications and data patterns."},
                {"role": "user", "content": ai_prompt}
            ]
            
            try:
                ai_response = await query_gpt5_with_retry(messages, "analysis")
                output_text += f"\n\n=== AI PATTERN ANALYSIS ===\n{ai_response}"
            except Exception as e:
                logger.warning(f"AI analysis failed: {e}")
                output_text += f"\n\n=== AI ANALYSIS UNAVAILABLE ===\nError: {str(e)}"
        
        return [TextContent(type="text", text=output_text)]
        
    except Exception as e:
        logger.error(f"Hexdump analysis failed: {e}")
        return [TextContent(type="text", text=f"Hexdump analysis failed: {str(e)}")]

# ===== END TIER 1 HANDLERS =====

# ===== PHASE 2 BINARY DIFFING HANDLERS =====

async def handle_binary_diff_analysis(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle comprehensive binary diffing analysis"""
    try:
        from binary_diff_engine import BinaryDiffEngine
        
        binary1 = arguments["binary_path_1"]
        binary2 = arguments["binary_path_2"]
        diff_type = arguments.get("diff_type", "comprehensive")
        output_format = arguments.get("output_format", "text")
        ai_analysis = arguments.get("ai_analysis", True)
        
        # Map diff_type to diff_types list
        if diff_type == "comprehensive":
            diff_types = ["file", "strings", "functions", "metadata"]
        else:
            diff_types = [diff_type]
        
        # Perform binary diff analysis
        with BinaryDiffEngine() as engine:
            results = await engine.comprehensive_diff(
                binary1, binary2, 
                diff_types=diff_types,
                ai_analysis=ai_analysis
            )
        
        # Format output
        if output_format == "json":
            output_text = json.dumps(results, indent=2)
        elif output_format == "html":
            output_text = format_diff_results_as_html(results)
        else:
            output_text = format_diff_results_as_text(results)
        
        return [TextContent(type="text", text=output_text)]
        
    except Exception as e:
        logger.error(f"Binary diff analysis failed: {e}")
        return [TextContent(type="text", text=f"Binary diff analysis failed: {str(e)}")]

async def handle_patch_security_analysis(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle patch security analysis with vulnerability tracking"""
    try:
        from binary_diff_engine import BinaryDiffEngine
        
        original = arguments["original_binary"]
        patched = arguments["patched_binary"]
        depth = arguments.get("analysis_depth", "standard")
        focus = arguments.get("focus_areas", ["security", "performance", "functionality"])
        output_format = arguments.get("output_format", "text")
        
        # Determine diff types based on analysis depth
        if depth == "quick":
            diff_types = ["file", "strings"]
        elif depth == "comprehensive":
            diff_types = ["file", "strings", "functions", "metadata"]
        else:  # standard
            diff_types = ["file", "strings", "functions"]
        
        # Enhanced AI analysis for patch security
        ai_analysis = True
        
        with BinaryDiffEngine() as engine:
            results = await engine.comprehensive_diff(
                original, patched,
                diff_types=diff_types,
                ai_analysis=ai_analysis
            )
            
            # Add patch-specific analysis
            results["patch_analysis"] = {
                "analysis_depth": depth,
                "focus_areas": focus,
                "security_assessment": "enabled"
            }
        
        # Format output with security focus
        if output_format == "json":
            output_text = json.dumps(results, indent=2)
        else:
            output_text = format_patch_analysis_as_text(results)
        
        return [TextContent(type="text", text=output_text)]
        
    except Exception as e:
        logger.error(f"Patch security analysis failed: {e}")
        return [TextContent(type="text", text=f"Patch security analysis failed: {str(e)}")]

async def handle_version_evolution_analysis(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle multi-version binary evolution analysis"""
    try:
        from binary_diff_engine import BinaryDiffEngine
        
        versions = arguments["binary_versions"]
        tracking_mode = arguments.get("tracking_mode", "timeline")
        baseline = arguments.get("comparison_baseline", "previous")
        generate_report = arguments.get("generate_report", True)
        
        if len(versions) < 2:
            return [TextContent(type="text", text="Error: At least 2 binary versions required for evolution analysis")]
        
        evolution_results = {
            "analysis_type": "version_evolution",
            "version": "1.3.0-dev",
            "tracking_mode": tracking_mode,
            "comparison_baseline": baseline,
            "binary_versions": versions,
            "timestamp": datetime.now().isoformat(),
            "comparisons": []
        }
        
        # Perform pairwise comparisons
        with BinaryDiffEngine() as engine:
            for i in range(1, len(versions)):
                if baseline == "first":
                    binary1 = versions[0]
                    binary2 = versions[i]
                    comparison_name = f"v1_vs_v{i+1}"
                elif baseline == "previous":
                    binary1 = versions[i-1]
                    binary2 = versions[i]
                    comparison_name = f"v{i}_vs_v{i+1}"
                else:  # specified - use previous for now
                    binary1 = versions[i-1]
                    binary2 = versions[i]
                    comparison_name = f"v{i}_vs_v{i+1}"
                
                logger.info(f"Comparing {comparison_name}: {binary1} vs {binary2}")
                
                diff_result = await engine.comprehensive_diff(
                    binary1, binary2,
                    diff_types=["file", "strings", "functions"],
                    ai_analysis=True
                )
                
                evolution_results["comparisons"].append({
                    "comparison_name": comparison_name,
                    "binary1": binary1,
                    "binary2": binary2,
                    "results": diff_result
                })
        
        # Generate summary
        evolution_results["summary"] = generate_evolution_summary(evolution_results)
        
        # Format output
        if generate_report:
            output_text = format_evolution_analysis_as_text(evolution_results)
        else:
            output_text = json.dumps(evolution_results, indent=2)
        
        return [TextContent(type="text", text=output_text)]
        
    except Exception as e:
        logger.error(f"Version evolution analysis failed: {e}")
        return [TextContent(type="text", text=f"Version evolution analysis failed: {str(e)}")]

async def handle_binary_diff_report(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle binary diff report generation"""
    try:
        diff_results_path = arguments["diff_results"]
        report_format = arguments.get("report_format", "html")
        include_viz = arguments.get("include_visualizations", True)
        exec_summary = arguments.get("executive_summary", True)
        
        # Load diff results
        try:
            with open(diff_results_path, 'r') as f:
                diff_results = json.load(f)
        except Exception as e:
            return [TextContent(type="text", text=f"Error loading diff results: {str(e)}")]
        
        # Generate report
        report_content = generate_diff_report(
            diff_results, 
            report_format=report_format,
            include_visualizations=include_viz,
            executive_summary=exec_summary
        )
        
        # Save report to temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{report_format}', delete=False) as f:
            f.write(report_content)
            report_path = f.name
        
        output_text = f"""Binary Diff Report Generated Successfully!

Report Details:
- Format: {report_format.upper()}
- Visualizations: {'Included' if include_viz else 'Not included'}
- Executive Summary: {'Included' if exec_summary else 'Not included'}
- Report Path: {report_path}

Report Preview:
{report_content[:1000]}{'...' if len(report_content) > 1000 else ''}
"""
        
        return [TextContent(type="text", text=output_text)]
        
    except Exception as e:
        logger.error(f"Binary diff report generation failed: {e}")
        return [TextContent(type="text", text=f"Binary diff report generation failed: {str(e)}")]

# Helper functions for formatting diff results

def format_diff_results_as_text(results: Dict[str, Any]) -> str:
    """Format diff results as human-readable text"""
    output = f"""🔄 BINARY DIFF ANALYSIS RESULTS
{'='*50}

Analysis Type: {results.get('analysis_type', 'Unknown')}
Version: {results.get('version', 'Unknown')}
Timestamp: {results.get('timestamp', 'Unknown')}

Binaries Compared:
- Binary 1: {results.get('binary1', 'Unknown')}
- Binary 2: {results.get('binary2', 'Unknown')}

Diff Types Performed: {', '.join(results.get('diff_types_performed', []))}
AI Analysis: {'Enabled' if results.get('ai_analysis_enabled') else 'Disabled'}

"""
    
    # Add results for each diff type
    diff_results = results.get('results', {})
    
    if 'file_level' in diff_results:
        file_result = diff_results['file_level']
        output += f"""📁 FILE-LEVEL ANALYSIS
{'-'*30}
Identical: {file_result.get('identical', False)}
Similarity Score: {file_result.get('similarity_score', 0):.2%}
Size Difference: {file_result.get('size_diff', 0)} bytes
Byte Differences: {file_result.get('byte_diff_count', 0)}

"""
    
    if 'string_level' in diff_results:
        string_result = diff_results['string_level']
        output += f"""📝 STRING-LEVEL ANALYSIS
{'-'*30}
Strings in Binary 1: {string_result.get('strings1_count', 0)}
Strings in Binary 2: {string_result.get('strings2_count', 0)}
Added Strings: {len(string_result.get('added_strings', []))}
Removed Strings: {len(string_result.get('removed_strings', []))}
String Similarity: {string_result.get('string_similarity_score', 0):.2%}

"""
    
    if 'function_level' in diff_results:
        func_result = diff_results['function_level']
        output += f"""🔧 FUNCTION-LEVEL ANALYSIS
{'-'*30}
Functions in Binary 1: {func_result.get('functions1_count', 0)}
Functions in Binary 2: {func_result.get('functions2_count', 0)}
Added Functions: {len(func_result.get('added_functions', []))}
Removed Functions: {len(func_result.get('removed_functions', []))}
Changed Functions: {len(func_result.get('changed_functions', []))}
Function Similarity: {func_result.get('function_similarity_score', 0):.2%}

"""
    
    # Add AI analysis if available
    if results.get('ai_analysis'):
        ai_result = results['ai_analysis']
        output += f"""🤖 AI SECURITY ANALYSIS
{'-'*30}
Provider: {ai_result.get('provider', 'Unknown')}
Model: {ai_result.get('model', 'Unknown')}

Analysis:
{ai_result.get('analysis', 'No analysis available')}

"""
    
    return output

def format_diff_results_as_html(results: Dict[str, Any]) -> str:
    """Format diff results as HTML report"""
    # Basic HTML template - can be enhanced with CSS/JS
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Binary Diff Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #007acc; }}
        .result-good {{ color: green; }}
        .result-warning {{ color: orange; }}
        .result-critical {{ color: red; }}
        pre {{ background-color: #f5f5f5; padding: 10px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔄 Binary Diff Analysis Report</h1>
        <p><strong>Generated:</strong> {results.get('timestamp', 'Unknown')}</p>
        <p><strong>Analysis Type:</strong> {results.get('analysis_type', 'Unknown')}</p>
    </div>
    
    <div class="section">
        <h2>📁 Binary Information</h2>
        <p><strong>Binary 1:</strong> {results.get('binary1', 'Unknown')}</p>
        <p><strong>Binary 2:</strong> {results.get('binary2', 'Unknown')}</p>
        <p><strong>Diff Types:</strong> {', '.join(results.get('diff_types_performed', []))}</p>
    </div>"""
    
    # Add sections for each diff type
    diff_results = results.get('results', {})
    
    if 'file_level' in diff_results:
        file_result = diff_results['file_level']
        similarity = file_result.get('similarity_score', 0)
        css_class = 'result-good' if similarity > 0.8 else 'result-warning' if similarity > 0.5 else 'result-critical'
        
        html += f"""
    <div class="section">
        <h2>📁 File-Level Analysis</h2>
        <p class="{css_class}"><strong>Similarity Score:</strong> {similarity:.2%}</p>
        <p><strong>Size Difference:</strong> {file_result.get('size_diff', 0)} bytes</p>
        <p><strong>Byte Differences:</strong> {file_result.get('byte_diff_count', 0)}</p>
    </div>"""
    
    if results.get('ai_analysis'):
        ai_result = results['ai_analysis']
        html += f"""
    <div class="section">
        <h2>🤖 AI Security Analysis</h2>
        <p><strong>Provider:</strong> {ai_result.get('provider', 'Unknown')} - {ai_result.get('model', 'Unknown')}</p>
        <pre>{ai_result.get('analysis', 'No analysis available')}</pre>
    </div>"""
    
    html += """</body>
</html>"""
    
    return html

def format_patch_analysis_as_text(results: Dict[str, Any]) -> str:
    """Format patch analysis with security focus"""
    output = format_diff_results_as_text(results)
    
    # Add patch-specific information
    patch_info = results.get('patch_analysis', {})
    output += f"""🛡️  PATCH SECURITY ASSESSMENT
{'-'*30}
Analysis Depth: {patch_info.get('analysis_depth', 'Unknown')}
Focus Areas: {', '.join(patch_info.get('focus_areas', []))}
Security Assessment: {patch_info.get('security_assessment', 'Unknown')}

"""
    
    return output

def format_evolution_analysis_as_text(results: Dict[str, Any]) -> str:
    """Format version evolution analysis as text"""
    output = f"""📈 BINARY VERSION EVOLUTION ANALYSIS
{'='*50}

Tracking Mode: {results.get('tracking_mode', 'Unknown')}
Comparison Baseline: {results.get('comparison_baseline', 'Unknown')}
Binary Versions: {len(results.get('binary_versions', []))}
Total Comparisons: {len(results.get('comparisons', []))}

"""
    
    # Add summary
    summary = results.get('summary', {})
    if summary:
        output += f"""📊 EVOLUTION SUMMARY
{'-'*30}
"""
        for key, value in summary.items():
            output += f"{key}: {value}\n"
        output += "\n"
    
    # Add individual comparisons
    for comparison in results.get('comparisons', []):
        output += f"""🔄 {comparison.get('comparison_name', 'Unknown')}
{'-'*30}
"""
        comp_results = comparison.get('results', {})
        if 'results' in comp_results:
            diff_results = comp_results['results']
            if 'file_level' in diff_results:
                file_result = diff_results['file_level']
                output += f"Similarity: {file_result.get('similarity_score', 0):.2%}\n"
            if 'string_level' in diff_results:
                string_result = diff_results['string_level']
                output += f"String changes: +{len(string_result.get('added_strings', []))} -{len(string_result.get('removed_strings', []))}\n"
        output += "\n"
    
    return output

def generate_evolution_summary(results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate summary for evolution analysis"""
    comparisons = results.get('comparisons', [])
    summary = {
        "total_comparisons": len(comparisons),
        "average_similarity": 0.0,
        "total_function_changes": 0,
        "total_string_changes": 0
    }
    
    if comparisons:
        similarities = []
        func_changes = 0
        string_changes = 0
        
        for comp in comparisons:
            comp_results = comp.get('results', {})
            if 'results' in comp_results:
                diff_results = comp_results['results']
                
                # Collect similarities
                if 'file_level' in diff_results:
                    similarities.append(diff_results['file_level'].get('similarity_score', 0))
                
                # Count function changes
                if 'function_level' in diff_results:
                    func_result = diff_results['function_level']
                    func_changes += len(func_result.get('added_functions', []))
                    func_changes += len(func_result.get('removed_functions', []))
                    func_changes += len(func_result.get('changed_functions', []))
                
                # Count string changes
                if 'string_level' in diff_results:
                    string_result = diff_results['string_level']
                    string_changes += len(string_result.get('added_strings', []))
                    string_changes += len(string_result.get('removed_strings', []))
        
        if similarities:
            summary["average_similarity"] = sum(similarities) / len(similarities)
        summary["total_function_changes"] = func_changes
        summary["total_string_changes"] = string_changes
    
    return summary

def generate_diff_report(results: Dict[str, Any], report_format: str = "html", 
                        include_visualizations: bool = True, 
                        executive_summary: bool = True) -> str:
    """Generate comprehensive diff report"""
    if report_format == "html":
        return format_diff_results_as_html(results)
    elif report_format == "markdown":
        return format_diff_results_as_markdown(results)
    elif report_format == "pdf":
        # PDF generation would require additional libraries
        return "PDF generation not implemented yet. Use HTML format instead."
    else:
        return format_diff_results_as_text(results)

def format_diff_results_as_markdown(results: Dict[str, Any]) -> str:
    """Format diff results as Markdown report"""
    md = f"""# 🔄 Binary Diff Analysis Report

**Analysis Type:** {results.get('analysis_type', 'Unknown')}  
**Version:** {results.get('version', 'Unknown')}  
**Timestamp:** {results.get('timestamp', 'Unknown')}  

## 📁 Binary Information

- **Binary 1:** `{results.get('binary1', 'Unknown')}`
- **Binary 2:** `{results.get('binary2', 'Unknown')}`
- **Diff Types:** {', '.join(results.get('diff_types_performed', []))}
- **AI Analysis:** {'✅ Enabled' if results.get('ai_analysis_enabled') else '❌ Disabled'}

"""
    
    # Add results sections
    diff_results = results.get('results', {})
    
    if 'file_level' in diff_results:
        file_result = diff_results['file_level']
        md += f"""## 📁 File-Level Analysis

| Metric | Value |
|--------|-------|
| Identical | {'✅ Yes' if file_result.get('identical') else '❌ No'} |
| Similarity Score | {file_result.get('similarity_score', 0):.2%} |
| Size Difference | {file_result.get('size_diff', 0)} bytes |
| Byte Differences | {file_result.get('byte_diff_count', 0)} |

"""
    
    if results.get('ai_analysis'):
        ai_result = results['ai_analysis']
        md += f"""## 🤖 AI Security Analysis

**Provider:** {ai_result.get('provider', 'Unknown')} - {ai_result.get('model', 'Unknown')}

```
{ai_result.get('analysis', 'No analysis available')}
```

"""
    
    return md

# ===== END PHASE 2 HANDLERS =====

import datetime

async def main():
    """Run the MCP server"""
    logger.info("Starting Ghidra GPT-5 MCP Server...")
    
    # Verify OpenAI API key
    try:
        get_openai_api_key()
        logger.info("✅ OpenAI API key found")
    except Exception as e:
        logger.error(f"❌ OpenAI API key error: {e}")
        sys.exit(1)
    
    # Check for Ghidra installation
    if not os.path.exists(GHIDRA_HEADLESS_PATH):
        logger.warning(f"⚠️  Ghidra not found at {GHIDRA_HEADLESS_PATH}")
        logger.warning("Set GHIDRA_HEADLESS_PATH environment variable or install Ghidra")
    else:
        logger.info("✅ Ghidra headless found")
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, {})

if __name__ == "__main__":
    asyncio.run(main())
