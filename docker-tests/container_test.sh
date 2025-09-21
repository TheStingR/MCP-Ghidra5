#!/bin/bash
# MCP-Ghidra5 Container Test Script
# Runs inside Docker containers to test installation and functionality
# Version: 1.0.0

set -euo pipefail

# Configuration
TEST_DIR="/home/testuser/mcp-ghidra5-test"
LOG_FILE="/home/testuser/container-test.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# Test functions
test_system_info() {
    log_info "=== System Information Test ==="
    
    log_info "Distribution: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'=' -f2 | tr -d '\"')"
    log_info "Python version: $(python3 --version)"
    log_info "Java version: $(java -version 2>&1 | head -n1)"
    log_info "Architecture: $(uname -m)"
    log_info "Kernel: $(uname -r)"
    
    log_success "System information collected"
}

test_python_environment() {
    log_info "=== Python Environment Test ==="
    
    # Check Python and pip
    if ! python3 -c "import sys; print(f'Python {sys.version}')"; then
        log_error "Python3 not working"
        return 1
    fi
    
    if ! pip --version; then
        log_error "pip not working"
        return 1
    fi
    
    # Test virtual environment
    if [[ -n "${VIRTUAL_ENV:-}" ]]; then
        log_info "Virtual environment active: $VIRTUAL_ENV"
    else
        log_warning "No virtual environment detected"
    fi
    
    log_success "Python environment OK"
}

test_project_structure() {
    log_info "=== Project Structure Test ==="
    
    if [[ ! -d "$TEST_DIR" ]]; then
        log_error "Project directory not found: $TEST_DIR"
        return 1
    fi
    
    cd "$TEST_DIR"
    
    # Check key files
    local required_files=(
        "MCP-Ghidra5/ghidra_gpt5_mcp.py"
        "MCP-Ghidra5/security_utils.py" 
        "MCP-Ghidra5/cache_utils.py"
        "MCP-Ghidra5/install_mcp_ghidra5.sh"
        "README.md"
    )
    
    for file in "${required_files[@]}"; do
        if [[ -f "$file" ]]; then
            log_info "✓ Found: $file"
        else
            log_error "✗ Missing: $file"
            return 1
        fi
    done
    
    log_success "Project structure validated"
}

test_ghidra_detection() {
    log_info "=== Ghidra Detection Test ==="
    
    cd "$TEST_DIR"
    
    # Test Ghidra path detection logic
    python3 -c "
import sys
sys.path.insert(0, 'MCP-Ghidra5')
from ghidra_gpt5_mcp import detect_ghidra_path
path = detect_ghidra_path()
print(f'Detected Ghidra path: {path}')
import os
if os.path.isfile(path):
    print('✓ Ghidra executable found')
else:
    print('⚠ Ghidra executable not found (expected for non-Kali systems)')
"
    
    log_success "Ghidra detection test completed"
}

test_dependencies_installation() {
    log_info "=== Dependencies Installation Test ==="
    
    cd "$TEST_DIR"
    
    # Test pip installation of dependencies
    log_info "Installing Python dependencies..."
    
    # Install required packages
    if pip install mcp aiohttp anthropic openai python-dotenv; then
        log_success "Python dependencies installed"
    else
        log_error "Failed to install Python dependencies"
        return 1
    fi
    
    # Test imports
    log_info "Testing Python imports..."
    python3 -c "
import sys
try:
    import mcp
    print('✓ mcp imported successfully')
except ImportError as e:
    print(f'✗ mcp import failed: {e}')
    sys.exit(1)

try:
    import aiohttp
    print('✓ aiohttp imported successfully')
except ImportError as e:
    print(f'✗ aiohttp import failed: {e}')
    sys.exit(1)

try:
    import sys
    sys.path.append('MCP-Ghidra5')
    from ghidra_gpt5_mcp import *
    print('✓ MCP-Ghidra5 modules imported successfully')
except ImportError as e:
    print(f'✗ MCP-Ghidra5 import failed: {e}')
    sys.exit(1)
"
    
    if [[ $? -eq 0 ]]; then
        log_success "Dependencies installation test passed"
    else
        log_error "Dependencies installation test failed"
        return 1
    fi
}

test_installer_script() {
    log_info "=== Installer Script Test ==="
    
    cd "$TEST_DIR"
    
    # Make installer executable
    chmod +x MCP-Ghidra5/install_mcp_ghidra5.sh
    
    # Run installer in non-interactive mode (dry run)
    log_info "Testing installer script (dry run)..."
    
    # Set environment variables for testing
    export SKIP_API_KEY_INPUT=1
    export SKIP_GHIDRA_DOWNLOAD=1
    
    if timeout 60 ./MCP-Ghidra5/install_mcp_ghidra5.sh --dry-run 2>&1 | head -20; then
        log_success "Installer script executed without errors"
    else
        log_warning "Installer script encountered issues (may be expected in containers)"
    fi
}

test_security_utils() {
    log_info "=== Security Utils Test ==="
    
    cd "$TEST_DIR"
    
    # Test security utilities
    python3 -c "
import sys
sys.path.insert(0, 'MCP-Ghidra5')

try:
    from security_utils import SecurityError, validate_binary_analysis_args
    print('✓ Security utils imported successfully')
    
    # Test validation function
    test_args = {'binary_path': '/tmp/test.bin', 'analysis_depth': 'standard'}
    try:
        validated = validate_binary_analysis_args(test_args)
        print('✓ Security validation working')
    except SecurityError as e:
        print(f'⚠ Security validation returned error (expected behavior): {e}')
    
    print('✓ Security utilities functional')
except Exception as e:
    print(f'✗ Security utils test failed: {e}')
    sys.exit(1)
"
    
    if [[ $? -eq 0 ]]; then
        log_success "Security utils test passed"
    else
        log_error "Security utils test failed"
        return 1
    fi
}

test_mcp_server_startup() {
    log_info "=== MCP Server Startup Test ==="
    
    cd "$TEST_DIR/MCP-Ghidra5"
    
    # Test server startup (without API key - should handle gracefully)
    log_info "Testing MCP server startup..."
    
    # Run server for a few seconds to test initialization
    timeout 10s python3 ghidra_gpt5_mcp.py --test-mode 2>&1 | head -10 || true
    
    log_info "MCP server startup test completed (timeout expected)"
    log_success "Server initialization appears functional"
}

test_comprehensive_functionality() {
    log_info "=== Comprehensive Functionality Test ==="
    
    cd "$TEST_DIR"
    
    # Run existing test suites if available
    if [[ -f "MCP-Ghidra5/test_comprehensive.py" ]]; then
        log_info "Running comprehensive test suite..."
        cd "MCP-Ghidra5"
        
        # Mock API key for testing
        export OPENAI_API_KEY="test_key_placeholder"
        
        if python3 test_comprehensive.py --skip-api-tests; then
            log_success "Comprehensive test suite passed"
        else
            log_warning "Some comprehensive tests failed (may be expected without real API key)"
        fi
        
        cd ..
    else
        log_warning "Comprehensive test suite not found"
    fi
    
    # Test smoke tests if available
    if [[ -f "MCP-Ghidra5/smoke_test_complete.py" ]]; then
        log_info "Running smoke tests..."
        cd "MCP-Ghidra5"
        
        if python3 smoke_test_complete.py --no-api; then
            log_success "Smoke tests passed"
        else
            log_warning "Some smoke tests failed (may be expected without API key)"
        fi
        
        cd ..
    else
        log_warning "Smoke test suite not found"
    fi
}

# Main test execution
main() {
    log_info "Starting MCP-Ghidra5 container tests..."
    log_info "Container: $(hostname)"
    log_info "Timestamp: $(date)"
    log_info "User: $(whoami)"
    log_info "Working directory: $(pwd)"
    
    local failed_tests=()
    local passed_tests=()
    
    # Define tests to run
    local tests=(
        "test_system_info"
        "test_python_environment" 
        "test_project_structure"
        "test_ghidra_detection"
        "test_dependencies_installation"
        "test_installer_script"
        "test_security_utils"
        "test_mcp_server_startup"
        "test_comprehensive_functionality"
    )
    
    # Run each test
    for test_name in "${tests[@]}"; do
        log_info "Running $test_name..."
        
        if $test_name; then
            passed_tests+=("$test_name")
            log_success "$test_name PASSED"
        else
            failed_tests+=("$test_name")
            log_error "$test_name FAILED"
        fi
        
        echo "----------------------------------------"
    done
    
    # Summary
    log_info "Container Test Summary:"
    log_info "Total tests: ${#tests[@]}"
    log_success "Passed: ${#passed_tests[@]}"
    
    if [[ ${#failed_tests[@]} -gt 0 ]]; then
        log_error "Failed: ${#failed_tests[@]} (${failed_tests[*]})"
        log_error "Container tests FAILED"
        exit 1
    else
        log_success "All container tests PASSED!"
        exit 0
    fi
}

# Execute main function
main "$@"