<div align="center">

![MCP-Ghidra5 Logo](mcp-ghidra5.png)

# MCP-Ghidra5

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-linux-lightgrey.svg)
![License](https://img.shields.io/badge/license-proprietary-red.svg)
![Status](https://img.shields.io/badge/status-stable-green.svg)
![Version](https://img.shields.io/badge/version-1.3.0-blue.svg)
![MCP](https://img.shields.io/badge/MCP-Server-purple.svg)
![Ghidra](https://img.shields.io/badge/Ghidra-Compatible-orange.svg)
![GPT](https://img.shields.io/badge/GPT--5-Powered-brightgreen.svg)

</div>

## 🎯 **Advanced GPT-5 Powered Ghidra Reverse Engineering MCP Server**

**MCP-Ghidra5** is a cutting-edge **Model Context Protocol (MCP) server** that seamlessly integrates **Ghidra's powerful reverse engineering capabilities** with **advanced multi-model AI technology**. Supporting **7 major AI providers** including OpenAI GPT-5, Anthropic Claude, Google Gemini, xAI Grok, and local LLMs via Ollama, this professional-grade tool transforms binary analysis from a manual, time-intensive process into an **automated, intelligent workflow** with **cost optimization** and **automatic fallback systems**.

---

## 🚀 **Key Features**

### **🤖 Multi-Model AI Suite**
- **🧠 7 AI Provider Support** - OpenAI GPT-5, Claude 3.5, Gemini, Grok, DeepSeek, Perplexity, Ollama
- **🔄 Intelligent Fallback** - Automatic provider switching for 99.9% uptime reliability
- **💰 Cost Optimization** - Smart model selection saving 30-50% on AI costs
- **📊 Usage Analytics** - Comprehensive tracking of API calls, costs, and performance
- **🔒 Local LLM Support** - Ollama integration for 100% private offline analysis
- **⚡ Model Testing** - Built-in tools to test and validate AI provider configurations
- **🎯 Provider Management** - Dynamic switching between models mid-session

### **🔬 Advanced Analysis Tools**
- **📊 Binary Analysis** - Comprehensive executable analysis with multi-AI interpretation  
- **🔍 Function Decompilation** - Intelligent function analysis with contextual explanations
- **🛡️ Malware Detection** - AI-powered behavioral and structural malware analysis
- **⚡ Exploit Development** - Automated PoC generation with vulnerability insights
- **🔧 Firmware Analysis** - IoT and embedded systems reverse engineering
- **🎯 Pattern Recognition** - Vulnerability detection across multiple architectures

### **🏗️ Professional Integration**
- **🔗 MCP Client Integration** - Seamless MCP server deployment
- **📋 Multi-Architecture Support** - x86, x64, ARM, MIPS, RISC-V compatibility
- **⚙️ Automated Installation** - One-command setup with dependency management
- **🔑 API Key Management** - Secure OpenAI API key configuration
- **📁 Project Management** - Organized analysis workspace with logging

---

## 📦 **Installation**

### **Prerequisites**
- **Python 3.8+** with pip/pipx
- **Linux Environment** (Kali Linux, Ubuntu, RHEL, etc.)
- **OpenAI API Key** for GPT-5/GPT-4o access
- **Ghidra** (REQUIRED - core functionality depends on this)

### **Quick Install**
```bash
# 1. Install Ghidra (REQUIRED)
# Download from: https://github.com/NationalSecurityAgency/ghidra/releases
# Extract to /opt/ghidra/ (recommended)
sudo mkdir -p /opt/ghidra
sudo tar -xzf ghidra_*.zip -C /opt/ && sudo mv /opt/ghidra_* /opt/ghidra

# 2. Download MCP-Ghidra5
wget https://github.com/TheStingR/MCP-Ghidra5/archive/main.zip
unzip main.zip && cd MCP-Ghidra5-main

# 3. Navigate to the MCP-Ghidra5 directory and run installer
cd MCP-Ghidra5
./install_mcp_ghidra5.sh
# Follow prompts: Accept terms → Enter API key → Done!

# 4. Test installation
./test_ghidra_gpt5.py

# 5. Add to MCP Client (use generated config)
# Configure your MCP-compatible client with the generated settings
```

### **Manual Setup**
```bash
# 1. INSTALL GHIDRA FIRST (MANDATORY)
# Download: https://github.com/NationalSecurityAgency/ghidra/releases
# Extract to /opt/ghidra/

# 2. Install Python dependencies
pip3 install --user mcp aiohttp

# 3. Configure environment
export OPENAI_API_KEY="your-api-key-here"
export GHIDRA_HEADLESS_PATH="/opt/ghidra/support/analyzeHeadless"

# 4. Verify Ghidra installation
$GHIDRA_HEADLESS_PATH -help || echo "ERROR: Ghidra not found!"

# 5. Navigate to MCP-Ghidra5 directory and run server
cd MCP-Ghidra5
python3 ghidra_gpt5_mcp.py
```

---

## 🛠️ **Usage Examples**

### **Binary Analysis**
```python
call_mcp_tool("ghidra_binary_analysis", {
    "binary_path": "/path/to/executable",
    "analysis_depth": "deep"
})
```

### **Function Analysis**
```python
call_mcp_tool("ghidra_function_analysis", {
    "binary_path": "/path/to/binary",
    "function_name": "main",
    "include_decompilation": true
})
```

### **Exploit Development**
```python
call_mcp_tool("ghidra_exploit_development", {
    "binary_path": "/path/to/vulnerable_app",
    "vulnerability_type": "buffer_overflow"
})
```

### **Multi-Model AI Queries**
```python
call_mcp_tool("gpt5_reverse_engineering_query", {
    "query": "How to bypass ASLR in modern Linux systems?",
    "preferred_model": "claude-3-5-sonnet"
})
```

### **AI Model Management**
```python
# Check available AI providers
call_mcp_tool("ai_model_status", {"action": "status"})

# Test specific model
call_mcp_tool("ai_model_status", {
    "action": "test_model",
    "model_name": "grok-beta"
})
```

### **Tier 1 Binary Analysis Tools** 🆕 **v1.2.0**
```python
# Strings extraction with AI analysis
call_mcp_tool("binary_strings_analysis", {
    "binary_path": "/path/to/binary",
    "min_length": 6,
    "encoding": "all",
    "output_format": "json",
    "ai_analysis": True
})

# File information and metadata
call_mcp_tool("binary_file_info", {
    "binary_path": "/path/to/binary",
    "detailed": True
})

# Objdump disassembly analysis
call_mcp_tool("binary_objdump_analysis", {
    "binary_path": "/path/to/binary",
    "analysis_type": "all",
    "ai_analysis": True
})

# ELF binary analysis with readelf
call_mcp_tool("binary_readelf_analysis", {
    "binary_path": "/path/to/elf_binary",
    "analysis_type": "all"
})

# Hex dump with pattern recognition
call_mcp_tool("binary_hexdump_analysis", {
    "binary_path": "/path/to/binary",
    "offset": 0,
    "length": 1024,
    "format": "canonical"
})
```

### **Phase 2 Binary Diffing Tools** 🆕 **v1.3.0**
```python
# Comprehensive binary file comparison
call_mcp_tool("binary_diff_file", {
    "file1_path": "/path/to/original.bin",
    "file2_path": "/path/to/modified.bin",
    "ai_analysis": True
})

# String-based binary comparison
call_mcp_tool("binary_diff_strings", {
    "file1_path": "/path/to/binary1",
    "file2_path": "/path/to/binary2",
    "min_length": 4
})

# Function-level comparison
call_mcp_tool("binary_diff_functions", {
    "file1_path": "/path/to/v1.exe",
    "file2_path": "/path/to/v2.exe"
})

# Metadata comparison
call_mcp_tool("binary_diff_metadata", {
    "file1_path": "/path/to/elf1",
    "file2_path": "/path/to/elf2"
})
```

---

## 🎯 **17 Advanced Analysis Tools** 🆕

### **🏗️ Core Ghidra Integration**
| Tool | Description | Use Case |
|------|-------------|----------|
| **🔬 Binary Analysis** | Comprehensive Ghidra + Multi-AI analysis | Full executable examination |
| **🎯 Function Analysis** | Specific function decompilation | Targeted code analysis |
| **💥 Exploit Development** | PoC generation with AI selection | Vulnerability research |
| **🦠 Malware Analysis** | Behavioral and structural analysis | Threat intelligence |
| **📡 Firmware Analysis** | IoT and embedded systems | Hardware security |
| **🔍 Pattern Search** | Vulnerability detection | Code auditing |

### **⚡ Tier 1 Binary Tools** 🆕 **v1.2.0**
| Tool | Description | Features |
|------|-------------|----------|
| **📝 Strings Analysis** | Multi-encoding string extraction | AI pattern recognition, crypto detection |
| **📋 File Information** | Comprehensive file metadata | Type detection, security assessment |
| **🔧 Objdump Analysis** | Disassembly and symbol analysis | Cross-architecture, AI interpretation |
| **⚙️ Readelf Analysis** | ELF binary structure analysis | Security features, dependency analysis |
| **🔍 Hexdump Analysis** | Raw binary inspection | Pattern recognition, magic signatures |

### **🔄 Phase 2 Binary Diffing Tools** 🆕 **v1.3.0**
| Tool | Description | Features |
|------|-------------|----------|
| **📊 Binary File Diff** | Comprehensive binary comparison | AI-powered security analysis, metadata comparison |
| **📝 Strings Diff** | String-based binary comparison | Multi-encoding support, pattern analysis |
| **🔧 Functions Diff** | Function-level comparison analysis | Decompilation diff with AI insights |
| **📋 Metadata Diff** | Binary metadata comparison | ELF headers, sections, symbols analysis |

### **🤖 AI & Management**
| Tool | Description | Use Case |
|------|-------------|----------|
| **🤖 Multi-Model Queries** | Expert assistance with 7 AI providers | Knowledge base |
| **🔧 AI Model Status** | Provider management and testing | System monitoring |

---

## 🔄 **Binary Diffing Capabilities** 🆕 **v1.3.0**

**Phase 2** introduces advanced binary comparison and diffing tools with AI-powered security analysis:

### **🎯 Core Diffing Features**
- **📊 File-Level Comparison** - Complete binary diff with security impact analysis
- **📝 String Diffing** - Multi-encoding string comparison with pattern detection
- **🔧 Function Analysis** - Decompilation-based function comparison
- **📋 Metadata Diffing** - ELF headers, sections, and symbol analysis

### **🤖 AI-Enhanced Analysis**
- **🛡️ Security Impact Assessment** - Automated vulnerability risk analysis
- **🔍 Pattern Recognition** - Intelligent change detection and categorization
- **⚡ Async Processing** - High-performance concurrent analysis
- **💾 Smart Caching** - Intelligent caching with automatic cleanup

### **🏗️ Technical Specifications**
- **⚡ Performance**: 5-30 seconds for typical binary pairs
- **💰 Cost Efficient**: $0.02-0.10 per comparison with AI analysis
- **🔒 Secure Processing**: Local analysis with optional AI enhancement
- **📊 Structured Output**: JSON format for programmatic consumption

---

## 🏆 **Performance Specifications**

- **⚡ Quick Analysis**: 30-60 seconds
- **🔍 Deep Analysis**: 120-240 seconds  
- **💰 Cost Efficient**: $0.05-0.80 per analysis
- **🎯 Multi-Platform**: Linux distributions supported
- **🔒 Secure**: No data retention, API key protection

---

## 📚 **Documentation**

- **📖 [Deployment Guide](GHIDRA_GPT5_DEPLOYMENT_GUIDE.md)** - Complete setup instructions
- **🔧 [Project Summary](GHIDRA_GPT5_PROJECT_SUMMARY.md)** - Technical specifications
- **✅ [Installation Verification](verify_setup.sh)** - Test your setup
- **🏢 [Copyright Information](COPYRIGHT.txt)** - Legal terms and licensing

---

## 🎯 **Target Audience**

- **🔐 Cybersecurity Professionals** - Advanced threat analysis
- **🎮 CTF Competitors** - Rapid binary reverse engineering  
- **🛡️ Penetration Testers** - Exploit development and analysis
- **🦠 Malware Analysts** - Threat intelligence and research
- **🏭 Security Researchers** - Vulnerability discovery
- **🎓 Educators & Students** - Learning reverse engineering

---

## 🔧 **System Requirements**

| Component | Requirement |
|-----------|-------------|
| **OS** | Linux (Kali, Ubuntu, RHEL, CentOS, etc.) |
| **Python** | 3.8+ with pip |
| **Memory** | 4GB+ RAM recommended |
| **Storage** | 2GB+ free space |
| **Network** | Internet access for API calls |
|| **Ghidra** | REQUIRED - Download from NSA GitHub |

---

## 🛡️ **Security & Legal**

### **⚖️ Legal Notice**
- **🏢 Property**: TechSquad Inc. proprietary software
- **❌ Not For Resale**: Commercial distribution prohibited  
- **✅ Legal Use Only**: Authorized for legitimate security research
- **🔒 Disclaimer**: Neither TechSquad Inc. nor TheStingR is responsible for improper use

### **🔐 Security Features**
- **🔑 API Key Protection** - Secure credential management
- **🗑️ No Data Retention** - Analysis results not stored remotely
- **🔒 Local Processing** - Ghidra analysis performed locally
- **📝 Audit Logging** - Complete operation logging

---

## 🙏 **Acknowledgments**

### **Issue Reporting & Testing**
- **[PurpleTeam-TechSquad](https://github.com/PurpleTeam-TechSquad)** - Critical bug discovery and comprehensive testing
  - Identified Python version detection failure on Python 3.13+ systems
  - Discovered Ghidra path hardcoding issues on Debian/Ubuntu/Kali systems
  - Reported API key validation limitations for project-based keys
  - Provided detailed testing environment and reproduction steps
  - Testing Environment: Kali GNU/Linux Rolling 2025.3
  - Test Duration: 45 minutes comprehensive installation and functionality testing

### **Special Thanks**
We sincerely thank PurpleTeam-TechSquad for their thorough external testing that identified critical compatibility issues, enabling us to make MCP-Ghidra5 truly production-ready across multiple Linux distributions.

---

## 🤝 **Contributing**

This is **TechSquad Inc. proprietary software**. For feature requests, bug reports, or collaboration inquiries:

1. **📧 Contact**: Via GitHub issues
2. **🐛 Bug Reports**: Include system details and logs
3. **💡 Feature Requests**: Describe use case and requirements
4. **📋 Pull Requests**: Contact maintainers first

---

## 🏷️ **Version History**

### **v1.3.0** (September 2025) - **PHASE 2 BINARY DIFFING** 🆕
- 🔄 **4 New Binary Diffing Tools** - file, strings, functions, metadata comparison
- 🤖 **AI-Powered Security Analysis** - Intelligent vulnerability impact assessment
- ⚡ **Async Engine Architecture** - High-performance concurrent processing
- 💾 **Smart Caching System** - Optimized performance with automatic cleanup
- 🛡️ **Enhanced Security** - Advanced validation for binary comparison operations
- 📊 **Structured JSON Output** - Programmatic access to comparison results
- 🧪 **Comprehensive Testing** - Full test suite with 100% pass rate
- 🔧 **Repository Optimization** - Clean structure with docs/ and tests/ organization

### **v1.2.0** (September 2025) - **TIER 1 TOOLS UPDATE** 🆕
- ⚡ **5 New Tier 1 Binary Tools** - strings, file, objdump, readelf, hexdump analysis
- 📊 **JSON Output Support** - Structured data output for programmatic consumption  
- 🚀 **Intelligent Caching** - 1-hour TTL cache system with automatic cleanup
- 🔒 **Enhanced Security** - Advanced input validation for all new tools
- 🤖 **AI-Powered Analysis** - Each tool includes optional AI security assessment
- 📝 **Pattern Recognition** - Automated detection of crypto, URLs, suspicious content
- 🎯 **Cross-Platform Tested** - Validated on Ubuntu 22.04/24.04, Kali Linux, Debian 12
- 📦 **Docker Ready** - Complete containerized testing infrastructure

### **v1.1.0** (January 2025) - **MAJOR UPDATE** 🚀
- 🤖 **Multi-Model AI Integration** - 7 AI providers with intelligent fallback
- 💰 **Cost Optimization** - Smart model selection saving 30-50% on costs  
- 🔒 **Local LLM Support** - Ollama integration for private offline analysis
- 📊 **Usage Analytics** - Comprehensive tracking and monitoring
- 🔧 **AI Model Management** - Built-in testing and configuration tools
- ⚡ **Performance Improvements** - Full async processing and caching
- 🛡️ **Enhanced Security** - Advanced input validation and path controls
- 📈 **99.9% Uptime** - Automatic fallback ensures continuous availability

### **v1.0.1** (September 2024)
- 🔧 **Critical Bug Fixes** (Thanks to PurpleTeam-TechSquad!)
- ✅ Fixed Python version detection for Python 3.13+ systems
- ✅ Added Ghidra path auto-detection for Debian/Ubuntu/Kali
- ✅ Enhanced API key validation for project-based keys
- ✅ Improved Python package management for externally-managed environments
- ✅ Added comprehensive AI provider compatibility testing
- ✅ Enhanced cross-platform Linux distribution support

### **v1.0.0** (September 2024)
- ✅ Initial public release
- ✅ 7 advanced analysis tools
- ✅ GPT-5 integration
- ✅ Comprehensive installer
- ✅ Terminal Terminal support
- ✅ Multi-architecture compatibility

---

## 📞 **Support**

- **📚 Documentation**: See included guides and README files
- **🐛 Issues**: GitHub Issues tab
- **💬 Community**: Cybersecurity forums and Discord
- **⚡ Emergency**: Critical security research support available

---

## ⭐ **Star This Repository**

If **MCP-Ghidra5** helps your security research, please **⭐ star this repository** to support continued development!

---

<div align="center">

**🏢 Copyright © 2024 TechSquad Inc. - All Rights Reserved**  
**👨‍💻 Coded by: [TheStingR](https://github.com/TheStingR)**  
**🔒 Proprietary Software - NOT FOR RESALE**

*Licensed for legal cybersecurity research and education*

</div>

---

<div align="center">

[![GitHub stars](https://img.shields.io/github/stars/TheStingR/MCP-Ghidra5.svg)](https://github.com/TheStingR/MCP-Ghidra5/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/TheStingR/MCP-Ghidra5.svg)](https://github.com/TheStingR/MCP-Ghidra5/network)
[![GitHub issues](https://img.shields.io/github/issues/TheStingR/MCP-Ghidra5.svg)](https://github.com/TheStingR/MCP-Ghidra5/issues)

</div>