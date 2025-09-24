#!/bin/bash
"""
MCP-Ghidra5 Update Module
========================

Seamless update system for MCP-Ghidra5 installations.
Preserves user configuration while updating core components.

Author: TheStingR @ TechSquad Inc.
Version: 1.3.0
"""

set -euo pipefail

# Colors and formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Update configuration
GITHUB_REPO="TheStingR/MCP-Ghidra5"
GITHUB_API="https://api.github.com/repos/$GITHUB_REPO"
CURRENT_VERSION_FILE="VERSION"
BACKUP_DIR="$HOME/.mcp-ghidra5-backups"
UPDATE_LOG="$HOME/.mcp-ghidra5-update.log"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$UPDATE_LOG"
}

print_banner() {
    echo -e "${BLUE}${BOLD}"
    echo "🔄 MCP-Ghidra5 Update System"
    echo "============================"
    echo -e "${NC}"
}

get_current_version() {
    if [[ -f "$CURRENT_VERSION_FILE" ]]; then
        cat "$CURRENT_VERSION_FILE"
    else
        echo "unknown"
    fi
}

get_latest_version() {
    log "Checking latest release..."
    latest=$(curl -s "$GITHUB_API/releases/latest" | grep '"tag_name"' | sed -E 's/.*"([^"]+)".*/\1/')
    if [[ -z "$latest" ]]; then
        echo "unknown"
    else
        echo "$latest"
    fi
}

compare_versions() {
    local current="$1"
    local latest="$2"
    
    if [[ "$current" == "$latest" ]]; then
        return 0  # Same version
    elif [[ "$current" == "unknown" ]]; then
        return 1  # Update needed (unknown current)
    else
        # Use version comparison
        printf '%s\n%s\n' "$current" "$latest" | sort -V | head -n1 | grep -q "^$current$"
        if [[ $? -eq 0 ]]; then
            return 1  # Update available
        else
            return 2  # Current is newer
        fi
    fi
}

backup_current_installation() {
    local backup_name="mcp-ghidra5-backup-$(date +%Y%m%d-%H%M%S)"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    log "Creating backup: $backup_path"
    mkdir -p "$backup_path"
    
    # Backup core files (preserve user configs)
    cp -r *.py "$backup_path/" 2>/dev/null || true
    cp -r *.json "$backup_path/" 2>/dev/null || true
    cp -r *.sh "$backup_path/" 2>/dev/null || true
    cp VERSION "$backup_path/" 2>/dev/null || true
    
    # Backup user configurations
    if [[ -f "ghidra_gpt5_terminal_config.json" ]]; then
        cp "ghidra_gpt5_terminal_config.json" "$backup_path/user_config.json"
        log "User configuration backed up"
    fi
    
    echo "$backup_path"
}

download_latest_release() {
    local version="$1"
    local temp_dir=$(mktemp -d)
    local download_url="https://github.com/$GITHUB_REPO/archive/$version.zip"
    
    log "Downloading $version from GitHub..."
    
    cd "$temp_dir"
    if ! curl -L -o "mcp-ghidra5.zip" "$download_url"; then
        log "ERROR: Failed to download release $version"
        rm -rf "$temp_dir"
        return 1
    fi
    
    if ! unzip -q "mcp-ghidra5.zip"; then
        log "ERROR: Failed to extract release archive"
        rm -rf "$temp_dir"
        return 1
    fi
    
    echo "$temp_dir"
}

update_core_files() {
    local source_dir="$1"
    local backup_path="$2"
    
    log "Updating core files..."
    
    # Find the extracted directory
    local extracted_dir=$(find "$source_dir" -maxdepth 1 -name "MCP-Ghidra5-*" -type d | head -n1)
    if [[ -z "$extracted_dir" ]]; then
        log "ERROR: Could not find extracted MCP-Ghidra5 directory"
        return 1
    fi
    
    local mcp_source="$extracted_dir/MCP-Ghidra5"
    
    # Update Python files
    for file in "$mcp_source"/*.py; do
        if [[ -f "$file" ]]; then
            local basename=$(basename "$file")
            log "Updating: $basename"
            cp "$file" "./"
        fi
    done
    
    # Update shell scripts
    for file in "$mcp_source"/*.sh; do
        if [[ -f "$file" ]]; then
            local basename=$(basename "$file")
            log "Updating: $basename"
            cp "$file" "./"
            chmod +x "$basename"
        fi
    done
    
    # Update VERSION file
    if [[ -f "$extracted_dir/VERSION" ]]; then
        cp "$extracted_dir/VERSION" "./"
        log "Version file updated"
    fi
    
    # Update documentation (optional)
    if [[ -f "$extracted_dir/README.md" ]]; then
        cp "$extracted_dir/README.md" "../" 2>/dev/null || true
    fi
}

preserve_user_config() {
    local backup_path="$1"
    
    if [[ -f "$backup_path/user_config.json" ]]; then
        log "Restoring user configuration..."
        cp "$backup_path/user_config.json" "ghidra_gpt5_terminal_config.json"
    fi
    
    # Preserve API keys from environment
    if [[ -n "${OPENAI_API_KEY:-}" ]]; then
        log "API key environment variable preserved"
    fi
}

run_post_update_tests() {
    log "Running post-update validation..."
    
    # Test MCP server startup
    if [[ -f "test_ghidra_gpt5.py" ]]; then
        log "Running basic functionality test..."
        if python3 test_ghidra_gpt5.py --quick-test 2>/dev/null; then
            log "✅ Basic functionality test passed"
            return 0
        else
            log "⚠️ Basic functionality test failed - manual verification recommended"
            return 1
        fi
    fi
    
    return 0
}

cleanup_update() {
    local temp_dir="$1"
    if [[ -d "$temp_dir" ]]; then
        rm -rf "$temp_dir"
        log "Cleanup completed"
    fi
}

show_update_summary() {
    local old_version="$1"
    local new_version="$2"
    local backup_path="$3"
    
    echo -e "${GREEN}${BOLD}"
    echo "✅ Update completed successfully!"
    echo "=============================="
    echo -e "${NC}"
    echo -e "Previous version: ${YELLOW}$old_version${NC}"
    echo -e "Current version:  ${GREEN}$new_version${NC}"
    echo -e "Backup location:  ${BLUE}$backup_path${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Verify your configuration: ./verify_setup.sh"
    echo "2. Test functionality: python3 test_ghidra_gpt5.py"
    echo "3. Restart your MCP client if running"
    echo ""
}

main() {
    print_banner
    
    # Check if we're in the right directory
    if [[ ! -f "ghidra_gpt5_mcp.py" ]]; then
        echo -e "${RED}ERROR: Please run this script from the MCP-Ghidra5 directory${NC}"
        exit 1
    fi
    
    # Check for internet connectivity
    if ! curl -s --head "$GITHUB_API" > /dev/null; then
        echo -e "${RED}ERROR: Cannot connect to GitHub. Check internet connection.${NC}"
        exit 1
    fi
    
    # Get version information
    local current_version=$(get_current_version)
    local latest_version=$(get_latest_version)
    
    if [[ "$latest_version" == "unknown" ]]; then
        echo -e "${RED}ERROR: Could not fetch latest version information${NC}"
        exit 1
    fi
    
    echo "Current version: $current_version"
    echo "Latest version:  $latest_version"
    echo ""
    
    # Compare versions
    compare_versions "$current_version" "$latest_version"
    local version_status=$?
    
    case $version_status in
        0)
            echo -e "${GREEN}✅ You have the latest version installed${NC}"
            exit 0
            ;;
        2)
            echo -e "${YELLOW}⚠️ Your version ($current_version) is newer than the latest release${NC}"
            echo "This might be a development version."
            exit 0
            ;;
        1)
            echo -e "${YELLOW}🔄 Update available: $current_version → $latest_version${NC}"
            ;;
    esac
    
    # Confirm update
    echo ""
    read -p "Do you want to update to version $latest_version? [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Update cancelled."
        exit 0
    fi
    
    log "Starting update from $current_version to $latest_version"
    
    # Create backup
    local backup_path=$(backup_current_installation)
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}ERROR: Backup failed${NC}"
        exit 1
    fi
    
    # Download latest release
    local temp_dir=$(download_latest_release "$latest_version")
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}ERROR: Download failed${NC}"
        exit 1
    fi
    
    # Update files
    if ! update_core_files "$temp_dir" "$backup_path"; then
        echo -e "${RED}ERROR: Update failed${NC}"
        cleanup_update "$temp_dir"
        exit 1
    fi
    
    # Preserve user configuration
    preserve_user_config "$backup_path"
    
    # Run post-update tests
    run_post_update_tests
    
    # Cleanup
    cleanup_update "$temp_dir"
    
    # Show summary
    show_update_summary "$current_version" "$latest_version" "$backup_path"
    
    log "Update completed successfully"
}

# Show help
if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
    print_banner
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --help, -h     Show this help message"
    echo "  --check        Check for updates without installing"
    echo "  --force        Force update even if versions are the same"
    echo ""
    echo "Examples:"
    echo "  $0              # Interactive update"
    echo "  $0 --check     # Check for updates only"
    echo ""
    exit 0
fi

# Check only mode
if [[ "${1:-}" == "--check" ]]; then
    current_version=$(get_current_version)
    latest_version=$(get_latest_version)
    
    echo "Current: $current_version"
    echo "Latest:  $latest_version"
    
    compare_versions "$current_version" "$latest_version"
    case $? in
        0) echo "Status: Up to date" ;;
        1) echo "Status: Update available" ;;
        2) echo "Status: Development version" ;;
    esac
    exit 0
fi

# Run main update process
main "$@"