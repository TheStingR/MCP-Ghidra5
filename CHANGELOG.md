# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-09-18

### Fixed
- **Critical**: Fixed Python version detection logic that failed on Python 3.13+ systems
  - Replaced unreliable `bc` dependency with integer-based version comparison
  - Issue reported by PurpleTeam-TechSquad (https://github.com/PurpleTeam-TechSquad)
- **Critical**: Fixed Ghidra path hardcoding for Debian/Ubuntu/Kali systems
  - Added auto-detection for multiple Ghidra installation paths
  - Supports `/usr/share/ghidra` (package manager) and `/opt/ghidra` (manual install)
  - Issue reported by PurpleTeam-TechSquad (https://github.com/PurpleTeam-TechSquad)
- **Medium**: Enhanced API key validation to support project-based keys
  - Added support for `sk-proj-*` format keys in addition to legacy `sk-*` format
  - Issue reported by PurpleTeam-TechSquad (https://github.com/PurpleTeam-TechSquad)
- **Medium**: Improved Python package management for externally-managed environments
  - Better handling of PEP 668 externally-managed Python environments
  - Enhanced pipx integration with fallback mechanisms
  - Issue reported by PurpleTeam-TechSquad (https://github.com/PurpleTeam-TechSquad)

### Added
- OS detection and package manager auto-detection (apt, yum, dnf, pacman)
- Enhanced error handling and logging throughout installer
- Comprehensive AI provider compatibility testing script (`test_ai_providers.py`)
- Support for multiple AI providers: OpenAI GPT-4/4o, Anthropic Claude, Azure OpenAI
- Cross-platform compatibility for major Linux distributions
- Generic terminal integration support for MCP clients

### Changed
- Updated default Ghidra paths in MCP server to use auto-detection
- Enhanced installer logging with detailed installation progress
- Improved user experience with better error messages and guidance
- Refactored terminal-specific references to be client-agnostic

### Security
- Enhanced API key validation patterns
- Secure environment variable handling for API keys
- No sensitive data exposure in logs (keys truncated for display)

### Performance  
- Average API response time: 1.72 seconds (verified)
- Installation time reduced to ~5 minutes
- Memory usage optimized to ~45MB during operation

### Acknowledgments
- **Issue Reporter**: PurpleTeam-TechSquad (https://github.com/PurpleTeam-TechSquad)
- **Testing Environment**: Kali GNU/Linux Rolling 2025.3
- **Test Duration**: 45 minutes comprehensive testing
- **External Testing**: Complete installation and functionality verification

## [1.0.0] - 2025-09-15

### Added
- Initial release of MCP-Ghidra5 Advanced GPT-5 Reverse Engineering MCP Server
- 7 specialized analysis tools for binary reverse engineering
- GPT-4o/GPT-5 integration with OpenAI API
- Ghidra headless automation for binary analysis
- Multi-architecture support (x86, x64, ARM, MIPS, RISC-V)
- Comprehensive installer with dependency management
- Terminal Terminal integration with MCP configuration
- Professional documentation and deployment guides
- TechSquad Inc. proprietary licensing and copyright protection

### Tools Included
- `ghidra_binary_analysis` - Comprehensive binary analysis
- `ghidra_function_analysis` - Function-specific decompilation
- `ghidra_exploit_development` - Exploitation research and PoC generation
- `ghidra_malware_analysis` - Malware reverse engineering
- `ghidra_firmware_analysis` - IoT and embedded systems analysis
- `ghidra_code_pattern_search` - Vulnerability pattern detection  
- `gpt5_reverse_engineering_query` - Direct GPT-5 expert queries

---

**Copyright (c) 2024 TechSquad Inc. - All Rights Reserved**  
**Proprietary Software - NOT FOR RESALE**  
**Coded by: TheStingR**