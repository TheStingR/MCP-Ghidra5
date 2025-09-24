# 🎯 MCP-Ghidra5 API Reference Guide

**Advanced GPT-5 Powered Reverse Engineering MCP Server**

---

## 📋 **Overview**

This comprehensive API reference covers all 17 analysis tools available in the MCP-Ghidra5 server. Each tool is designed for specific reverse engineering, malware analysis, and exploitation research tasks.

**Version:** 1.3.0  
**Compatible with:** Warp Terminal, Claude Desktop, MCP-compatible clients  
**Requirements:** OpenAI API key (GPT-4o/GPT-5), Ghidra 11.x (optional)

---

## 🛠️ **Available Analysis Tools**

### **🏗️ Core Ghidra Integration**
| Tool | Purpose | Speed | Complexity |
|------|---------|-------|------------|
| [🔬 Binary Analysis](#1-ghidra_binary_analysis) | Full executable analysis | 15-30s | ⭐⭐⭐ |
| [🎯 Function Analysis](#2-ghidra_function_analysis) | Specific function decompilation | 10-20s | ⭐⭐ |
| [💥 Exploit Development](#3-ghidra_exploit_development) | Vulnerability assessment & PoC | 20-40s | ⭐⭐⭐⭐ |
| [🦠 Malware Analysis](#4-ghidra_malware_analysis) | Threat intelligence & behavioral analysis | 25-45s | ⭐⭐⭐⭐ |
| [📡 Firmware Analysis](#5-ghidra_firmware_analysis) | IoT & embedded system security | 20-35s | ⭐⭐⭐ |
| [🔍 Pattern Search](#6-ghidra_code_pattern_search) | Vulnerability pattern detection | 15-25s | ⭐⭐ |
| [🤖 GPT-5 Queries](#7-gpt5_reverse_engineering_query) | Direct expert consultation | 5-15s | ⭐ |

### **⚡ Tier 1 Binary Tools** 🆕 **v1.2.0**
| Tool | Purpose | Speed | Complexity |
|------|---------|-------|------------|
| [📝 Strings Analysis](#8-binary_strings_analysis) | Multi-encoding string extraction | 5-15s | ⭐ |
| [📋 File Information](#9-binary_file_info) | Comprehensive file metadata | 3-8s | ⭐ |
| [🔧 Objdump Analysis](#10-binary_objdump_analysis) | Disassembly and symbol analysis | 10-20s | ⭐⭐ |
| [⚙️ Readelf Analysis](#11-binary_readelf_analysis) | ELF binary structure analysis | 5-12s | ⭐ |
| [🔍 Hexdump Analysis](#12-binary_hexdump_analysis) | Raw binary inspection | 3-10s | ⭐ |
| [🔧 AI Model Status](#13-ai_model_status) | Provider management and testing | 2-5s | ⭐ |

### **🔄 Phase 2 Binary Diffing Tools** 🆕 **v1.3.0**
| Tool | Purpose | Speed | Complexity |
|------|---------|-------|------------|
| [📊 Binary File Diff](#14-binary_diff_file) | Comprehensive binary comparison | 5-30s | ⭐⭐ |
| [📝 Strings Diff](#15-binary_diff_strings) | String-based binary comparison | 8-20s | ⭐⭐ |
| [🔧 Functions Diff](#16-binary_diff_functions) | Function-level comparison | 15-45s | ⭐⭐⭐ |
| [📋 Metadata Diff](#17-binary_diff_metadata) | Binary metadata comparison | 5-15s | ⭐⭐ |

---

## 1. **ghidra_binary_analysis**

**🔬 Comprehensive Binary Analysis using Ghidra + GPT-5**

### **Purpose**
Performs complete analysis of executable files combining Ghidra's static analysis with GPT-5's expert interpretation. Ideal for initial reconnaissance and comprehensive security assessment.

### **Input Schema**
```json
{
  "binary_path": "string (required)",
  "analysis_depth": "string (optional)",
  "focus_areas": "array[string] (optional)"
}
```

### **Parameters**

#### `binary_path` (required)
- **Type:** String
- **Description:** Absolute path to the binary file for analysis
- **Security:** Path validation, size limits (100MB), sandbox execution
- **Supported formats:** ELF, PE, Mach-O, raw binaries

#### `analysis_depth` (optional)
- **Type:** String (enum)
- **Default:** "standard"
- **Options:**
  - `"quick"` - Rapid assessment (30-60s, basic security overview)
  - `"standard"` - Comprehensive analysis (60-120s, detailed assessment)
  - `"deep"` - Exhaustive research (120-240s, advanced techniques)
  - `"exploit_focused"` - Exploitation opportunities (90-180s, attack vectors)

#### `focus_areas` (optional)
- **Type:** Array of strings
- **Description:** Specific areas to emphasize in analysis
- **Valid options:** `vulnerabilities`, `crypto`, `network`, `obfuscation`, `malware`, `exploitation`, `persistence`, `evasion`, `algorithms`, `api_calls`, `strings`, `imports`

### **Usage Examples**

#### Basic Usage
```python
call_mcp_tool("ghidra_binary_analysis", {
    "binary_path": "/path/to/suspicious.exe"
})
```

#### Advanced CTF Analysis
```python
call_mcp_tool("ghidra_binary_analysis", {
    "binary_path": "/ctf/reverse_challenge",
    "analysis_depth": "exploit_focused",
    "focus_areas": ["vulnerabilities", "crypto", "obfuscation"]
})
```

#### Malware Triage
```python
call_mcp_tool("ghidra_binary_analysis", {
    "binary_path": "/sandbox/malware_sample.bin",
    "analysis_depth": "deep",
    "focus_areas": ["malware", "evasion", "network", "persistence"]
})
```

### **Output Structure**
1. **Binary Overview** - Architecture, compilation, packing details
2. **Security Assessment** - Vulnerabilities, protections, attack surface
3. **Function Analysis** - Key functions and purposes
4. **Exploitation Opportunities** - Attack vectors and exploitability
5. **Recommendations** - Next steps and tool suggestions
6. **Technical Details** - Addresses, offsets, technical notes

---

## 2. **ghidra_function_analysis**

**🎯 Specific Function Analysis using Ghidra Decompilation + GPT-5**

### **Purpose**
Deep-dive analysis of specific functions with decompilation and expert interpretation. Perfect for understanding critical algorithms, finding vulnerabilities in specific code sections, or analyzing suspicious functions.

### **Input Schema**
```json
{
  "binary_path": "string (required)",
  "function_address": "string (required)",
  "analysis_type": "string (optional)"
}
```

### **Parameters**

#### `function_address` (required)
- **Type:** String
- **Description:** Function address or name to analyze
- **Formats:** 
  - Hexadecimal address: `"0x401000"`, `"0x1400014a0"`
  - Function name: `"main"`, `"vulnerable_function"`
  - Relative offset: `"+0x1000"`

#### `analysis_type` (optional)
- **Type:** String (enum)
- **Default:** "vulnerability_scan"
- **Options:**
  - `"vulnerability_scan"` - Security vulnerability assessment
  - `"algorithm_identification"` - Algorithm and logic analysis  
  - `"crypto_analysis"` - Cryptographic implementation review
  - `"exploit_potential"` - Exploitability assessment
  - `"behavioral_analysis"` - Function behavior and purpose

### **Usage Examples**

#### Vulnerability Assessment
```python
call_mcp_tool("ghidra_function_analysis", {
    "binary_path": "/ctf/pwn_challenge",
    "function_address": "0x401560",
    "analysis_type": "vulnerability_scan"
})
```

#### Crypto Algorithm Analysis  
```python
call_mcp_tool("ghidra_function_analysis", {
    "binary_path": "/samples/crypto_app",
    "function_address": "decrypt_data",
    "analysis_type": "crypto_analysis"
})
```

### **Output Structure**
1. **Function Purpose** - What the function does
2. **Security Analysis** - Vulnerabilities and weaknesses
3. **Parameters & Return Values** - Input/output analysis
4. **Control Flow** - Branches, loops, conditions
5. **Exploitation Assessment** - Attack potential
6. **Recommendations** - Specific testing advice

---

## 3. **ghidra_exploit_development**

**💥 Exploitation Analysis and PoC Generation**

### **Purpose**
Specialized tool for vulnerability research and exploit development. Analyzes binaries for exploitable conditions and generates exploitation strategies with optional proof-of-concept code.

### **Input Schema**
```json
{
  "binary_path": "string (required)",
  "target_platform": "string (required)",
  "exploit_type": "string (optional)",
  "generate_poc": "boolean (optional)"
}
```

### **Parameters**

#### `target_platform` (required)
- **Type:** String (enum)
- **Description:** Target platform for exploitation
- **Options:** `"linux_x64"`, `"linux_x86"`, `"windows_x64"`, `"windows_x86"`, `"arm64"`, `"arm32"`

#### `exploit_type` (optional)
- **Type:** String (enum)  
- **Default:** "buffer_overflow"
- **Options:**
  - `"buffer_overflow"` - Stack/heap buffer overflows
  - `"format_string"` - Format string vulnerabilities
  - `"use_after_free"` - UAF and memory corruption
  - `"rop_chain"` - ROP/JOP gadget analysis
  - `"heap_exploitation"` - Heap-based attacks
  - `"race_condition"` - Race condition vulnerabilities

#### `generate_poc` (optional)
- **Type:** Boolean
- **Default:** false
- **Description:** Whether to generate working exploit code

### **Usage Examples**

#### CTF Exploitation
```python
call_mcp_tool("ghidra_exploit_development", {
    "binary_path": "/ctf/pwn_easy",
    "target_platform": "linux_x64",
    "exploit_type": "buffer_overflow",
    "generate_poc": true
})
```

#### Advanced ROP Chain Analysis
```python
call_mcp_tool("ghidra_exploit_development", {
    "binary_path": "/targets/protected_app",
    "target_platform": "linux_x64", 
    "exploit_type": "rop_chain",
    "generate_poc": false
})
```

### **Output Structure**
1. **Vulnerability Assessment** - Exploitable conditions
2. **Attack Vector Analysis** - Trigger mechanisms
3. **Exploitation Strategy** - Step-by-step approach
4. **Payload Development** - Shellcode considerations
5. **ASLR/DEP Bypass** - Modern protection bypasses
6. **Exploitation Timeline** - Difficulty estimation
7. **Proof of Concept** - Working exploit code (if requested)

---

## 4. **ghidra_malware_analysis**

**🦠 Specialized Malware Reverse Engineering**

### **Purpose**
⚠️ **CAUTION: MALWARE ANALYSIS** - Secure environment required!

Advanced malware analysis combining static analysis with behavioral assessment. Provides threat intelligence, IOCs, and attribution indicators.

### **Input Schema**
```json
{
  "malware_path": "string (required)",
  "analysis_scope": "string (optional)",
  "sandbox_mode": "boolean (optional)"
}
```

### **Parameters**

#### `analysis_scope` (optional)
- **Type:** String (enum)
- **Default:** "static_only"
- **Options:**
  - `"static_only"` - Safe static analysis only
  - `"behavioral"` - Expected runtime behavior
  - `"network_analysis"` - C2 and communication patterns
  - `"persistence_mechanisms"` - Persistence and installation
  - `"evasion_techniques"` - Anti-analysis and stealth

### **Usage Examples**

#### Safe Static Analysis
```python
call_mcp_tool("ghidra_malware_analysis", {
    "malware_path": "/isolated/sample.exe",
    "analysis_scope": "static_only",
    "sandbox_mode": true
})
```

#### C2 Communication Analysis
```python
call_mcp_tool("ghidra_malware_analysis", {
    "malware_path": "/samples/trojan.bin",
    "analysis_scope": "network_analysis"
})
```

### **Output Structure**
1. **Malware Classification** - Family and variant identification
2. **Behavioral Analysis** - Runtime behavior and capabilities  
3. **Network Analysis** - C2 infrastructure and protocols
4. **Persistence Mechanisms** - Installation and survival techniques
5. **Evasion Techniques** - Anti-analysis capabilities
6. **IOCs** - Network signatures and file artifacts
7. **Mitigation Strategies** - Detection and removal
8. **Attribution Assessment** - Threat actor indicators

---

## 5. **ghidra_firmware_analysis**

**📡 IoT and Embedded Systems Security Analysis**

### **Purpose**
Specialized analysis for firmware, bootloaders, and embedded systems. Focuses on hardware security, authentication bypasses, and IoT-specific vulnerabilities.

### **Input Schema**
```json
{
  "firmware_path": "string (required)",
  "architecture": "string (optional)",
  "device_type": "string (optional)"
}
```

### **Parameters**

#### `architecture` (optional)
- **Type:** String (enum)
- **Default:** "auto_detect"
- **Options:** `"arm"`, `"mips"`, `"x86"`, `"x64"`, `"riscv"`, `"auto_detect"`

#### `device_type` (optional)
- **Type:** String (enum)
- **Default:** "unknown"  
- **Options:** `"router"`, `"iot_device"`, `"bootloader"`, `"rtos"`, `"embedded_linux"`, `"unknown"`

### **Usage Examples**

#### Router Firmware Analysis
```python
call_mcp_tool("ghidra_firmware_analysis", {
    "firmware_path": "/firmware/router.bin",
    "architecture": "mips",
    "device_type": "router"
})
```

#### IoT Device Security
```python
call_mcp_tool("ghidra_firmware_analysis", {
    "firmware_path": "/extracted/iot_firmware",
    "architecture": "arm",
    "device_type": "iot_device"
})
```

### **Output Structure**
1. **Firmware Overview** - Architecture and OS details
2. **Security Assessment** - Hardcoded credentials and keys
3. **Attack Surface** - Network services and interfaces
4. **Exploitation Opportunities** - Authentication bypasses
5. **Backdoors & Debug Features** - Hidden functionality
6. **Crypto Analysis** - Key storage and encryption
7. **Hardware Security** - Boot security mechanisms
8. **Post-Exploitation** - Persistence opportunities

---

## 6. **ghidra_code_pattern_search**

**🔍 Vulnerability Pattern Detection and Code Search**

### **Purpose**
Searches for specific code patterns, vulnerability signatures, and algorithmic implementations. Excellent for code auditing and systematic vulnerability research.

### **Input Schema**
```json
{
  "binary_path": "string (required)",
  "search_pattern": "string (required)",
  "pattern_type": "string (required)"
}
```

### **Parameters**

#### `search_pattern` (required)
- **Type:** String
- **Description:** Pattern to search for in the binary
- **Examples:** 
  - `"strcpy calls"` - Dangerous function usage
  - `"hardcoded keys"` - Cryptographic keys
  - `"debug strings"` - Development artifacts
  - `"network requests"` - Communication patterns

#### `pattern_type` (required)
- **Type:** String (enum)
- **Options:**
  - `"vulnerability_patterns"` - Common vulnerability patterns
  - `"crypto_algorithms"` - Cryptographic implementations
  - `"packer_signatures"` - Packing and obfuscation
  - `"anti_debug"` - Anti-analysis techniques
  - `"api_calls"` - System API interactions
  - `"string_patterns"` - String and configuration patterns

### **Usage Examples**

#### Vulnerability Hunting
```python
call_mcp_tool("ghidra_code_pattern_search", {
    "binary_path": "/targets/application.exe",
    "search_pattern": "buffer overflow patterns",
    "pattern_type": "vulnerability_patterns"
})
```

#### Crypto Implementation Review
```python
call_mcp_tool("ghidra_code_pattern_search", {
    "binary_path": "/samples/crypto_lib.so",
    "search_pattern": "AES constants",
    "pattern_type": "crypto_algorithms"
})
```

### **Output Structure**
1. **Pattern Matches** - Specific locations and contexts
2. **Context Analysis** - Meaning in program flow
3. **Security Implications** - Impact assessment
4. **Exploitation Potential** - Attack possibilities
5. **Related Patterns** - Additional investigation targets
6. **Recommendations** - Next steps and tools

---

## 7. **gpt5_reverse_engineering_query**

**🤖 Direct GPT-5 Expert Consultation**

### **Purpose**
Direct access to GPT-5's expertise for reverse engineering questions, methodology guidance, and technique explanations. Perfect for learning and getting expert advice.

### **Input Schema**
```json
{
  "query": "string (required)",
  "context": "string (optional)",
  "specialization": "string (optional)"
}
```

### **Parameters**

#### `query` (required)
- **Type:** String
- **Description:** Your reverse engineering or security question
- **Examples:**
  - `"How to bypass ASLR in modern Linux systems?"`
  - `"What are the best tools for ARM firmware analysis?"`
  - `"Explain ROP chain construction techniques"`

#### `context` (optional)
- **Type:** String
- **Description:** Additional context (code, assembly, hex dumps)

#### `specialization` (optional)
- **Type:** String (enum)
- **Default:** "reverse_engineering"
- **Options:**
  - `"binary_exploitation"` - Buffer overflows, ROP, heap exploitation
  - `"malware_analysis"` - Threat intelligence and behavioral analysis
  - `"firmware_hacking"` - IoT security and embedded systems
  - `"crypto_analysis"` - Cryptographic vulnerabilities
  - `"reverse_engineering"` - General RE and program analysis
  - `"vulnerability_research"` - Zero-day discovery and research

### **Usage Examples**

#### Learning Question
```python
call_mcp_tool("gpt5_reverse_engineering_query", {
    "query": "What are the key differences between heap and stack exploitation?",
    "specialization": "binary_exploitation"
})
```

#### Technical Problem
```python
call_mcp_tool("gpt5_reverse_engineering_query", {
    "query": "How can I identify custom crypto implementations?",
    "context": "Found these hex constants: 0x67452301, 0xEFCDAB89...",
    "specialization": "crypto_analysis"
})
```

#### Methodology Guidance
```python
call_mcp_tool("gpt5_reverse_engineering_query", {
    "query": "Best approach for analyzing packed malware samples?",
    "specialization": "malware_analysis"
})
```

---

## 14. **binary_diff_file**

**📊 Comprehensive Binary File Comparison**

### **Purpose**
Performs comprehensive binary-to-binary comparison analysis with AI-powered security assessment. Ideal for patch analysis, malware variant detection, and vulnerability research.

### **Input Schema**
```json
{
  "file1_path": "string (required)",
  "file2_path": "string (required)",
  "ai_analysis": "boolean (optional)"
}
```

### **Parameters**

#### `file1_path` (required)
- **Type:** String
- **Description:** Path to first binary file for comparison
- **Security:** Path validation, size limits (100MB per file)

#### `file2_path` (required) 
- **Type:** String
- **Description:** Path to second binary file for comparison
- **Security:** Path validation, size limits (100MB per file)

#### `ai_analysis` (optional)
- **Type:** Boolean
- **Default:** true
- **Description:** Enable AI-powered security analysis of differences

### **Usage Examples**

#### Malware Variant Analysis
```python
call_mcp_tool("binary_diff_file", {
    "file1_path": "/samples/malware_v1.exe",
    "file2_path": "/samples/malware_v2.exe",
    "ai_analysis": true
})
```

#### Patch Analysis
```python
call_mcp_tool("binary_diff_file", {
    "file1_path": "/bins/app_before.bin",
    "file2_path": "/bins/app_after.bin",
    "ai_analysis": true
})
```

---

## 15. **binary_diff_strings**

**📝 String-Based Binary Comparison**

### **Purpose**
Analyzes string differences between two binaries with pattern recognition and cryptographic content detection.

### **Input Schema**
```json
{
  "file1_path": "string (required)",
  "file2_path": "string (required)",
  "min_length": "integer (optional)"
}
```

### **Usage Examples**

#### Configuration Changes
```python
call_mcp_tool("binary_diff_strings", {
    "file1_path": "/config/app_v1",
    "file2_path": "/config/app_v2",
    "min_length": 4
})
```

---

## 16. **binary_diff_functions**

**🔧 Function-Level Comparison Analysis**

### **Purpose**
Performs function-level comparison using Ghidra decompilation with AI-enhanced analysis of behavioral changes.

### **Input Schema**
```json
{
  "file1_path": "string (required)",
  "file2_path": "string (required)"
}
```

### **Usage Examples**

#### Code Evolution Analysis
```python
call_mcp_tool("binary_diff_functions", {
    "file1_path": "/releases/v1.0.exe",
    "file2_path": "/releases/v1.1.exe"
})
```

---

## 17. **binary_diff_metadata**

**📋 Binary Metadata Comparison**

### **Purpose**
Compares ELF headers, sections, symbols, and other metadata between binaries with security impact assessment.

### **Input Schema**
```json
{
  "file1_path": "string (required)",
  "file2_path": "string (required)"
}
```

### **Usage Examples**

#### Security Feature Analysis
```python
call_mcp_tool("binary_diff_metadata", {
    "file1_path": "/bins/unprotected.elf",
    "file2_path": "/bins/protected.elf"
})
```

---

## 🚨 **Security and Best Practices**

### **Security Features**
- **Path Validation** - Prevents directory traversal and unsafe file access
- **File Size Limits** - 100MB maximum per analysis
- **Sandbox Execution** - Secure isolated analysis environment
- **Input Sanitization** - All parameters validated and sanitized
- **Malware Safety** - Special precautions for malware analysis

### **Best Practices**

#### For Malware Analysis
- Always use isolated VMs or dedicated analysis systems
- Never run malware analysis on production systems
- Use proper network isolation and monitoring
- Verify sandbox environment before analysis

#### For CTF Competitions
- Use `"exploit_focused"` analysis depth for faster results
- Focus on specific vulnerability types with pattern search
- Combine multiple tools for comprehensive coverage

#### For Professional Assessments
- Document all analysis results for reporting
- Use appropriate specialization settings
- Validate findings with additional tools
- Follow responsible disclosure practices

---

## 📊 **Performance Metrics**

### **Response Times** (Typical)
- **GPT-5 Query:** 5-15 seconds
- **Pattern Search:** 15-25 seconds  
- **Function Analysis:** 10-20 seconds
- **Binary Analysis:** 15-30 seconds
- **Firmware Analysis:** 20-35 seconds
- **Malware Analysis:** 25-45 seconds
- **Exploit Development:** 20-40 seconds
- **Tier 1 Tools:** 3-20 seconds
- **Binary Diffing:** 5-45 seconds

### **Cost Estimates** (GPT-4o pricing)
- **Quick Analysis:** $0.05-0.10
- **Standard Analysis:** $0.15-0.30  
- **Deep Analysis:** $0.30-0.60
- **Exploit PoC:** $0.40-0.80
- **Binary Diffing:** $0.02-0.10

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### "Security validation failed"
- **Cause:** Invalid file path or unsupported file
- **Solution:** Check file exists, is readable, and under 100MB
- **Example:** Use absolute paths like `/home/user/binary` not `~/binary`

#### "Binary file not found"
- **Cause:** File path doesn't exist or permission denied
- **Solution:** Verify file path and permissions
- **Command:** `ls -la /path/to/binary`

#### "Ghidra analysis failed"
- **Cause:** Ghidra not installed or path incorrect
- **Solution:** Install Ghidra or set `GHIDRA_HEADLESS_PATH`
- **Note:** System gracefully falls back to GPT-5 only analysis

#### "API rate limited"
- **Cause:** Too many concurrent requests to OpenAI
- **Solution:** Wait and retry - automatic exponential backoff included

#### "Cache disabled by environment"
- **Cause:** `ENABLE_MCP_CACHE=false` environment variable
- **Solution:** Set `ENABLE_MCP_CACHE=true` for better performance

### **Environment Variables**

```bash
# Required
export OPENAI_API_KEY="sk-your-api-key-here"

# Optional - Ghidra
export GHIDRA_HEADLESS_PATH="/usr/share/ghidra/support/analyzeHeadless"
export GHIDRA_PROJECT_DIR="/tmp/ghidra_projects"

# Optional - Caching
export ENABLE_MCP_CACHE="true"
export MAX_CACHE_SIZE_MB="500"
export CACHE_EXPIRY_HOURS="24"
export MCP_CACHE_DIR="/tmp/ghidra_mcp_cache"
```

---

## 🎯 **Integration Examples**

### **Warp Terminal Integration**

```json
{
  "mcpServers": {
    "ghidra-gpt5": {
      "command": "/usr/bin/python3",
      "args": ["/path/to/MCP-Ghidra5/ghidra_gpt5_mcp.py"],
      "env": {
        "OPENAI_API_KEY": "your-api-key",
        "GHIDRA_HEADLESS_PATH": "/usr/share/ghidra/support/analyzeHeadless"
      }
    }
  }
}
```

### **Automated Analysis Workflow**

```python
# CTF Binary Analysis Workflow
def analyze_ctf_binary(binary_path):
    # 1. Quick overview
    overview = call_mcp_tool("ghidra_binary_analysis", {
        "binary_path": binary_path,
        "analysis_depth": "quick"
    })
    
    # 2. Search for common vulnerabilities
    vulns = call_mcp_tool("ghidra_code_pattern_search", {
        "binary_path": binary_path,
        "search_pattern": "buffer overflow patterns",
        "pattern_type": "vulnerability_patterns"
    })
    
    # 3. Develop exploitation strategy
    exploit = call_mcp_tool("ghidra_exploit_development", {
        "binary_path": binary_path,
        "target_platform": "linux_x64",
        "exploit_type": "buffer_overflow",
        "generate_poc": True
    })
    
    return {
        "overview": overview,
        "vulnerabilities": vulns,
        "exploitation": exploit
    }
```

---

## 📚 **Additional Resources**

- **[Project Summary](GHIDRA_GPT5_PROJECT_SUMMARY.md)** - Technical specifications
- **[Deployment Guide](GHIDRA_GPT5_DEPLOYMENT_GUIDE.md)** - Installation instructions
- **[Changelog](CHANGELOG.md)** - Version history and updates
- **[Security Documentation](security_utils.py)** - Security implementation details
- **[Cache Documentation](cache_utils.py)** - Performance optimization features

---

**⚖️ Legal Notice:** This software is proprietary to TechSquad Inc. and protected by copyright law. Use only with proper authorization and for legitimate security research purposes.