#!/usr/bin/env python3
"""
Security Utilities for Ghidra GPT-5 MCP Server
Provides input validation, path sanitization, and security checks

Copyright (c) 2024 TechSquad Inc. - All Rights Reserved
Proprietary Software - NOT FOR RESALE
Coded by: TheStingR
"""

import os
import re
import tempfile
import shutil
import hashlib
import logging
from pathlib import Path
from typing import Union, Optional, List

logger = logging.getLogger(__name__)

# Security configuration
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB limit
ALLOWED_EXTENSIONS = {
    '.exe', '.dll', '.so', '.bin', '.elf', '.mach-o', '.pe', '.coff',
    '.o', '.obj', '.lib', '.a', '.dylib', '.sys', '.com', '.scr',
    '.msi', '.pkg', '.deb', '.rpm', '.apk', '.jar', '.war', '.ear',
    '.firmware', '.rom', '.img', '.iso'
}

DANGEROUS_PATHS = {
    '/etc', '/usr/bin', '/usr/sbin', '/bin', '/sbin', '/boot',
    '/proc', '/sys', '/dev', '/root', '/home'
}

class SecurityError(Exception):
    """Security-related error"""
    pass

class PathValidator:
    """Validates and sanitizes file paths"""
    
    @staticmethod
    def is_safe_path(path: Union[str, Path], allow_system_dirs: bool = False) -> bool:
        """
        Check if a path is safe for binary analysis
        
        Args:
            path: Path to validate
            allow_system_dirs: Whether to allow system directories (default: False)
        
        Returns:
            True if path is safe, False otherwise
        """
        try:
            path = Path(path).resolve()
            
            # Check if path exists and is a file
            if not path.exists():
                logger.warning(f"Path does not exist: {path}")
                return False
            
            if not path.is_file():
                logger.warning(f"Path is not a file: {path}")
                return False
            
            # Check file size
            if path.stat().st_size > MAX_FILE_SIZE:
                logger.warning(f"File too large: {path} ({path.stat().st_size} bytes)")
                return False
            
            # Check for dangerous system paths (unless explicitly allowed)
            if not allow_system_dirs:
                str_path = str(path)
                for dangerous_path in DANGEROUS_PATHS:
                    if str_path.startswith(dangerous_path + '/') or str_path == dangerous_path:
                        logger.warning(f"Dangerous system path: {path}")
                        return False
            
            # Check file extension (allow unknown extensions for binary analysis)
            # This is informational only, not restrictive
            suffix = path.suffix.lower()
            if suffix not in ALLOWED_EXTENSIONS and suffix:
                logger.info(f"Unknown file extension: {suffix} for {path}")
            
            return True
            
        except (OSError, ValueError, TypeError) as e:
            logger.error(f"Path validation error: {e}")
            return False
    
    @staticmethod
    def sanitize_path(path: Union[str, Path]) -> Optional[str]:
        """
        Sanitize and return safe absolute path
        
        Args:
            path: Input path to sanitize
            
        Returns:
            Sanitized absolute path string, or None if unsafe
        """
        try:
            path = Path(path).resolve()
            
            if PathValidator.is_safe_path(path):
                return str(path)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Path sanitization error: {e}")
            return None

class FileValidator:
    """Validates file contents and properties"""
    
    @staticmethod
    def calculate_file_hash(file_path: Union[str, Path], algorithm: str = 'sha256') -> str:
        """Calculate file hash for integrity checking"""
        try:
            hash_func = getattr(hashlib, algorithm)()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            logger.error(f"Hash calculation error: {e}")
            return ""
    
    @staticmethod
    def is_executable_file(file_path: Union[str, Path]) -> bool:
        """Check if file appears to be an executable"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)
                
            # Check for common executable headers
            if header.startswith(b'\x7fELF'):  # ELF
                return True
            elif header.startswith(b'MZ'):  # PE/DOS
                return True
            elif header.startswith(b'\xfeedface') or header.startswith(b'\xfeedfacf'):  # Mach-O
                return True
            elif header.startswith(b'\xcafebabe'):  # Java class/universal binary
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Executable check error: {e}")
            return False
    
    @staticmethod
    def scan_for_malware_signatures(file_path: Union[str, Path]) -> List[str]:
        """Basic signature-based malware scanning"""
        suspicious_patterns = []
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read(1024 * 1024)  # Read first 1MB
                
            # Check for suspicious strings (basic heuristics)
            suspicious_strings = [
                b'eval(',
                b'exec(',
                b'system(',
                b'shell_exec',
                b'CreateProcess',
                b'WinExec',
                b'VirtualAlloc',
                b'GetProcAddress',
                b'LoadLibrary',
                b'keylogger',
                b'backdoor',
                b'trojan'
            ]
            
            for pattern in suspicious_strings:
                if pattern in content:
                    suspicious_patterns.append(pattern.decode('utf-8', errors='ignore'))
                    
        except Exception as e:
            logger.error(f"Malware scan error: {e}")
            
        return suspicious_patterns

class SandboxEnvironment:
    """Manages secure analysis environment"""
    
    def __init__(self, temp_dir: Optional[str] = None):
        """Initialize sandbox environment"""
        if temp_dir:
            self.temp_dir = Path(temp_dir)
        else:
            self.temp_dir = Path(tempfile.mkdtemp(prefix='ghidra_analysis_'))
        
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.created_files = []
        logger.info(f"Sandbox initialized: {self.temp_dir}")
    
    def copy_file_to_sandbox(self, source_path: Union[str, Path]) -> Optional[str]:
        """
        Copy file to sandbox for safe analysis
        
        Args:
            source_path: Source file to copy
            
        Returns:
            Path to sandboxed file, or None if failed
        """
        try:
            source_path = Path(source_path)
            if not PathValidator.is_safe_path(source_path, allow_system_dirs=True):
                raise SecurityError(f"Source path validation failed: {source_path}")
            
            # Create unique filename in sandbox
            file_hash = FileValidator.calculate_file_hash(source_path)[:16]
            sandbox_name = f"{source_path.stem}_{file_hash}{source_path.suffix}"
            sandbox_path = self.temp_dir / sandbox_name
            
            # Copy file
            shutil.copy2(source_path, sandbox_path)
            self.created_files.append(sandbox_path)
            
            logger.info(f"File copied to sandbox: {source_path} -> {sandbox_path}")
            return str(sandbox_path)
            
        except Exception as e:
            logger.error(f"Sandbox copy error: {e}")
            return None
    
    def cleanup(self):
        """Clean up sandbox environment"""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                logger.info(f"Sandbox cleaned up: {self.temp_dir}")
        except Exception as e:
            logger.error(f"Sandbox cleanup error: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

class InputValidator:
    """Validates user inputs and parameters"""
    
    @staticmethod
    def validate_analysis_depth(depth: str) -> bool:
        """Validate analysis depth parameter"""
        valid_depths = ['quick', 'standard', 'deep', 'exploit_focused']
        return depth in valid_depths
    
    @staticmethod
    def validate_architecture(arch: str) -> bool:
        """Validate architecture parameter"""
        valid_archs = ['arm', 'mips', 'x86', 'x64', 'riscv', 'auto_detect']
        return arch in valid_archs
    
    @staticmethod
    def validate_platform(platform: str) -> bool:
        """Validate target platform parameter"""
        valid_platforms = ['linux_x64', 'linux_x86', 'windows_x64', 'windows_x86', 'arm64', 'arm32']
        return platform in valid_platforms
    
    @staticmethod
    def sanitize_query(query: str) -> str:
        """Sanitize user query input"""
        if not query or not isinstance(query, str):
            return ""
        
        # Remove excessive whitespace
        query = re.sub(r'\s+', ' ', query.strip())
        
        # Limit length
        max_length = 4000
        if len(query) > max_length:
            query = query[:max_length] + "..."
            logger.warning(f"Query truncated to {max_length} characters")
        
        return query
    
    @staticmethod
    def validate_focus_areas(areas: List[str]) -> List[str]:
        """Validate and filter focus areas"""
        valid_areas = [
            'vulnerabilities', 'crypto', 'network', 'obfuscation', 
            'malware', 'exploitation', 'persistence', 'evasion',
            'algorithms', 'api_calls', 'strings', 'imports'
        ]
        
        if not areas or not isinstance(areas, list):
            return []
        
        return [area for area in areas if area in valid_areas]

def secure_binary_analysis(binary_path: str, analysis_function, **kwargs):
    """
    Wrapper for secure binary analysis operations
    
    Args:
        binary_path: Path to binary file
        analysis_function: Function to call for analysis
        **kwargs: Additional arguments for analysis function
        
    Returns:
        Analysis result or raises SecurityError
    """
    try:
        # Validate path
        safe_path = PathValidator.sanitize_path(binary_path)
        if not safe_path:
            raise SecurityError(f"Binary path validation failed: {binary_path}")
        
        # Check if file is executable
        if not FileValidator.is_executable_file(safe_path):
            logger.warning(f"File may not be a valid executable: {safe_path}")
        
        # Scan for obvious malware signatures
        suspicious_patterns = FileValidator.scan_for_malware_signatures(safe_path)
        if suspicious_patterns:
            logger.warning(f"Suspicious patterns detected: {suspicious_patterns}")
            # Continue analysis but log warning
        
        # Use sandbox for analysis
        with SandboxEnvironment() as sandbox:
            sandbox_path = sandbox.copy_file_to_sandbox(safe_path)
            if not sandbox_path:
                raise SecurityError("Failed to create sandbox copy")
            
            # Call analysis function with sandboxed file
            kwargs['binary_path'] = sandbox_path
            return analysis_function(**kwargs)
            
    except SecurityError:
        raise
    except Exception as e:
        logger.error(f"Security wrapper error: {e}")
        raise SecurityError(f"Security analysis failed: {str(e)}")

# Security check functions for MCP handlers
def validate_binary_analysis_args(args: dict) -> dict:
    """Validate arguments for binary analysis"""
    validated = {}
    
    # Required: binary_path
    if 'binary_path' not in args:
        raise SecurityError("binary_path is required")
    
    binary_path = PathValidator.sanitize_path(args['binary_path'])
    if not binary_path:
        raise SecurityError(f"Invalid binary path: {args.get('binary_path')}")
    validated['binary_path'] = binary_path
    
    # Optional: analysis_depth
    if 'analysis_depth' in args:
        if not InputValidator.validate_analysis_depth(args['analysis_depth']):
            raise SecurityError(f"Invalid analysis depth: {args['analysis_depth']}")
        validated['analysis_depth'] = args['analysis_depth']
    
    # Optional: focus_areas
    if 'focus_areas' in args:
        validated['focus_areas'] = InputValidator.validate_focus_areas(args['focus_areas'])
    
    return validated

def validate_gpt5_query_args(args: dict) -> dict:
    """Validate arguments for GPT-5 query"""
    validated = {}
    
    # Required: query
    if 'query' not in args:
        raise SecurityError("query is required")
    
    query = InputValidator.sanitize_query(args['query'])
    if not query:
        raise SecurityError("Query cannot be empty")
    validated['query'] = query
    
    # Optional: context
    if 'context' in args:
        context = InputValidator.sanitize_query(args.get('context', ''))
        validated['context'] = context
    
    # Optional: specialization
    if 'specialization' in args:
        valid_specs = ['binary_exploitation', 'malware_analysis', 'firmware_hacking', 
                      'crypto_analysis', 'reverse_engineering', 'vulnerability_research']
        if args['specialization'] not in valid_specs:
            raise SecurityError(f"Invalid specialization: {args['specialization']}")
        validated['specialization'] = args['specialization']
    
    return validated

# Tier 1 Tool Validation Functions (Phase 1 Quick Wins)
def validate_tier1_binary_args(args: dict, tool_name: str) -> dict:
    """Validate arguments for Tier 1 binary analysis tools"""
    validated = {}
    
    # Required: binary_path
    if 'binary_path' not in args:
        raise SecurityError("binary_path is required")
    
    binary_path = PathValidator.sanitize_path(args['binary_path'])
    if not binary_path:
        raise SecurityError(f"Invalid binary path: {args.get('binary_path')}")
    validated['binary_path'] = binary_path
    
    # Tool-specific validations
    if tool_name == "strings":
        # Validate min_length
        min_length = args.get('min_length', 4)
        if not isinstance(min_length, int) or min_length < 1 or min_length > 100:
            raise SecurityError(f"Invalid min_length: {min_length} (must be 1-100)")
        validated['min_length'] = min_length
        
        # Validate encoding
        valid_encodings = ['ascii', 'utf-8', 'utf-16', 'all']
        encoding = args.get('encoding', 'all')
        if encoding not in valid_encodings:
            raise SecurityError(f"Invalid encoding: {encoding}")
        validated['encoding'] = encoding
        
    elif tool_name == "objdump":
        # Validate analysis_type
        valid_types = ['headers', 'disassemble', 'symbols', 'sections', 'relocs', 'dynamic', 'all']
        analysis_type = args.get('analysis_type', 'all')
        if analysis_type not in valid_types:
            raise SecurityError(f"Invalid analysis_type: {analysis_type}")
        validated['analysis_type'] = analysis_type
        
        # Validate architecture
        architecture = args.get('architecture', '')
        if architecture:
            valid_archs = ['i386', 'x86-64', 'arm', 'aarch64', 'mips', 'powerpc', 'sparc']
            if architecture not in valid_archs:
                raise SecurityError(f"Invalid architecture: {architecture}")
            validated['architecture'] = architecture
            
    elif tool_name == "readelf":
        # Validate analysis_type
        valid_types = ['headers', 'sections', 'symbols', 'relocs', 'dynamic', 'notes', 'all']
        analysis_type = args.get('analysis_type', 'all')
        if analysis_type not in valid_types:
            raise SecurityError(f"Invalid analysis_type: {analysis_type}")
        validated['analysis_type'] = analysis_type
        
    elif tool_name == "hexdump":
        # Validate offset
        offset = args.get('offset', 0)
        if not isinstance(offset, int) or offset < 0:
            raise SecurityError(f"Invalid offset: {offset} (must be >= 0)")
        validated['offset'] = offset
        
        # Validate length
        length = args.get('length', 512)
        if not isinstance(length, int) or length < 1 or length > 1024 * 1024:  # Max 1MB
            raise SecurityError(f"Invalid length: {length} (must be 1-1048576)")
        validated['length'] = length
        
        # Validate format
        valid_formats = ['canonical', 'octal', 'hex', 'decimal']
        format_type = args.get('format', 'canonical')
        if format_type not in valid_formats:
            raise SecurityError(f"Invalid format: {format_type}")
        validated['format'] = format_type
    
    # Common validations for all Tier 1 tools
    # Validate output_format
    valid_outputs = ['text', 'json']
    output_format = args.get('output_format', 'text')
    if output_format not in valid_outputs:
        raise SecurityError(f"Invalid output_format: {output_format}")
    validated['output_format'] = output_format
    
    # Validate ai_analysis flag
    ai_analysis = args.get('ai_analysis', True)
    if not isinstance(ai_analysis, bool):
        raise SecurityError(f"Invalid ai_analysis: {ai_analysis} (must be boolean)")
    validated['ai_analysis'] = ai_analysis
    
    return validated

def validate_strings_analysis_args(args: dict) -> dict:
    """Validate arguments for strings analysis"""
    return validate_tier1_binary_args(args, "strings")

def validate_file_info_args(args: dict) -> dict:
    """Validate arguments for file info analysis"""
    validated = validate_tier1_binary_args(args, "file")
    
    # Additional validation for detailed flag
    detailed = args.get('detailed', True)
    if not isinstance(detailed, bool):
        raise SecurityError(f"Invalid detailed flag: {detailed} (must be boolean)")
    validated['detailed'] = detailed
    
    return validated

def validate_objdump_analysis_args(args: dict) -> dict:
    """Validate arguments for objdump analysis"""
    return validate_tier1_binary_args(args, "objdump")

def validate_readelf_analysis_args(args: dict) -> dict:
    """Validate arguments for readelf analysis"""
    return validate_tier1_binary_args(args, "readelf")

def validate_hexdump_analysis_args(args: dict) -> dict:
    """Validate arguments for hexdump analysis"""
    return validate_tier1_binary_args(args, "hexdump")
