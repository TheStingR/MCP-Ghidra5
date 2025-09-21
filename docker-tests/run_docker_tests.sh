#!/bin/bash
# MCP-Ghidra5 Docker Cross-Platform Testing Script
# Version: 1.0.0
# Tests installation and functionality across Ubuntu 22/24, Kali, and Debian 12

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEST_LOG_DIR="$SCRIPT_DIR/test-logs"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configurations
declare -A DISTRIBUTIONS=(
    ["ubuntu22"]="Ubuntu 22.04 LTS"
    ["ubuntu24"]="Ubuntu 24.04 LTS"
    ["kali"]="Kali Linux"
    ["debian12"]="Debian 12"
)

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$TEST_LOG_DIR/docker-tests-$TIMESTAMP.log"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$TEST_LOG_DIR/docker-tests-$TIMESTAMP.log"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$TEST_LOG_DIR/docker-tests-$TIMESTAMP.log"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$TEST_LOG_DIR/docker-tests-$TIMESTAMP.log"
}

# Setup function
setup_test_environment() {
    log_info "Setting up Docker test environment..."
    
    # Create log directory
    mkdir -p "$TEST_LOG_DIR"
    
    # Check Docker availability
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    log_success "Docker test environment ready"
}

# Build Docker image function
build_docker_image() {
    local distro=$1
    local image_name="mcp-ghidra5-test-$distro"
    
    log_info "Building Docker image for $distro..."
    
    if docker build -t "$image_name" -f "$SCRIPT_DIR/Dockerfile.$distro" "$SCRIPT_DIR" 2>&1 | tee "$TEST_LOG_DIR/build-$distro-$TIMESTAMP.log"; then
        log_success "Successfully built Docker image for $distro"
        return 0
    else
        log_error "Failed to build Docker image for $distro"
        return 1
    fi
}

# Run test in container function
run_container_test() {
    local distro=$1
    local image_name="mcp-ghidra5-test-$distro"
    local container_name="mcp-ghidra5-test-$distro-$TIMESTAMP"
    
    log_info "Running tests in $distro container..."
    
    # Run container with project mounted
    local docker_cmd="docker run -it --rm --name $container_name \
        -v $PROJECT_ROOT:/home/testuser/mcp-ghidra5-test \
        -e OPENAI_API_KEY=test_key_placeholder \
        $image_name \
        /home/testuser/mcp-ghidra5-test/docker-tests/container_test.sh"
    
    log_info "Executing: $docker_cmd"
    
    if eval "$docker_cmd" 2>&1 | tee "$TEST_LOG_DIR/test-$distro-$TIMESTAMP.log"; then
        log_success "Container tests passed for $distro"
        return 0
    else
        log_error "Container tests failed for $distro"
        return 1
    fi
}

# Main test execution function
run_tests() {
    local target_distro=${1:-"all"}
    local failed_tests=()
    local passed_tests=()
    
    log_info "Starting MCP-Ghidra5 Docker cross-platform tests..."
    log_info "Target: $target_distro"
    log_info "Timestamp: $TIMESTAMP"
    
    # Test specific distribution or all
    if [[ "$target_distro" == "all" ]]; then
        local distros_to_test=(${!DISTRIBUTIONS[@]})
    else
        if [[ -n "${DISTRIBUTIONS[$target_distro]:-}" ]]; then
            local distros_to_test=("$target_distro")
        else
            log_error "Unknown distribution: $target_distro"
            log_info "Available distributions: ${!DISTRIBUTIONS[*]}"
            exit 1
        fi
    fi
    
    # Run tests for each distribution
    for distro in "${distros_to_test[@]}"; do
        log_info "Testing ${DISTRIBUTIONS[$distro]} ($distro)..."
        
        # Build image
        if build_docker_image "$distro"; then
            # Run tests
            if run_container_test "$distro"; then
                passed_tests+=("$distro")
            else
                failed_tests+=("$distro")
            fi
        else
            failed_tests+=("$distro")
        fi
        
        echo "----------------------------------------"
    done
    
    # Summary
    log_info "Docker Testing Summary:"
    log_info "Tested distributions: ${#distros_to_test[@]}"
    log_success "Passed: ${#passed_tests[@]} (${passed_tests[*]})"
    
    if [[ ${#failed_tests[@]} -gt 0 ]]; then
        log_error "Failed: ${#failed_tests[@]} (${failed_tests[*]})"
        return 1
    else
        log_success "All tests passed!"
        return 0
    fi
}

# Cleanup function
cleanup() {
    log_info "Cleaning up Docker resources..."
    
    # Remove test containers (if any remain)
    docker ps -a --format "table {{.Names}}" | grep "mcp-ghidra5-test-.*-$TIMESTAMP" | xargs -r docker rm -f
    
    # Optionally remove test images (uncomment if desired)
    # docker images --format "table {{.Repository}}" | grep "mcp-ghidra5-test-" | xargs -r docker rmi -f
    
    log_success "Cleanup completed"
}

# Help function
show_help() {
    echo "MCP-Ghidra5 Docker Cross-Platform Testing Script"
    echo ""
    echo "Usage: $0 [DISTRIBUTION]"
    echo ""
    echo "DISTRIBUTION options:"
    for distro in "${!DISTRIBUTIONS[@]}"; do
        echo "  $distro    - ${DISTRIBUTIONS[$distro]}"
    done
    echo "  all       - Test all distributions (default)"
    echo ""
    echo "Examples:"
    echo "  $0                  # Test all distributions"
    echo "  $0 ubuntu22         # Test only Ubuntu 22.04"
    echo "  $0 kali             # Test only Kali Linux"
    echo ""
    echo "Logs will be stored in: $TEST_LOG_DIR"
}

# Main execution
main() {
    # Handle command line arguments
    case "${1:-}" in
        -h|--help|help)
            show_help
            exit 0
            ;;
        *)
            setup_test_environment
            
            # Set up cleanup trap
            trap cleanup EXIT
            
            # Run tests
            if run_tests "${1:-all}"; then
                log_success "Docker testing completed successfully!"
                exit 0
            else
                log_error "Docker testing failed!"
                exit 1
            fi
            ;;
    esac
}

# Execute main function
main "$@"