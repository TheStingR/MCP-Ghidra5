# MCP-Ghidra5 Docker Cross-Platform Testing

This directory contains comprehensive Docker-based testing infrastructure to validate MCP-Ghidra5 installation and functionality across multiple Debian-based Linux distributions.

## 🎯 **Testing Goals**

- **Cross-Platform Compatibility**: Ensure MCP-Ghidra5 works on Ubuntu 22.04/24.04, Kali Linux, and Debian 12
- **Installation Validation**: Test installer scripts and dependency management
- **Functionality Testing**: Validate core features work correctly across platforms
- **Security Testing**: Verify security utilities and sandboxing work properly
- **Performance Testing**: Ensure acceptable performance across different environments

## 🐳 **Supported Distributions**

| Distribution | Docker Image | Ghidra | Notes |
|--------------|-------------|---------|--------|
| Ubuntu 22.04 LTS | `ubuntu:22.04` | Manual install | LTS baseline |
| Ubuntu 24.04 LTS | `ubuntu:24.04` | Manual install | Latest LTS |
| Kali Linux | `kalilinux/kali-rolling` | Package install | Pre-installed Ghidra |
| Debian 12 | `debian:12` | Manual install | Stable baseline |

## 📁 **File Structure**

```
docker-tests/
├── README.md                    # This documentation
├── run_docker_tests.sh         # Main test runner script
├── container_test.sh            # Test script that runs inside containers
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile.ubuntu22         # Ubuntu 22.04 container
├── Dockerfile.ubuntu24         # Ubuntu 24.04 container
├── Dockerfile.kali             # Kali Linux container
├── Dockerfile.debian12         # Debian 12 container
└── test-logs/                  # Test result logs (created during runs)
```

## 🚀 **Quick Start**

### Test All Distributions
```bash
cd docker-tests
./run_docker_tests.sh
```

### Test Specific Distribution
```bash
./run_docker_tests.sh ubuntu22    # Ubuntu 22.04 only
./run_docker_tests.sh kali        # Kali Linux only
./run_docker_tests.sh debian12    # Debian 12 only
```

### Using Docker Compose
```bash
# Test all distributions
docker-compose --profile all up --build

# Test specific distribution
docker-compose --profile ubuntu22 up --build
docker-compose --profile kali up --build
```

## 📋 **Test Coverage**

Each container runs the following comprehensive tests:

### 1. **System Information Test**
- Distribution version and details
- Python and Java versions
- System architecture and kernel

### 2. **Python Environment Test**
- Python 3 functionality
- pip package manager
- Virtual environment setup

### 3. **Project Structure Test**
- Validates all required MCP-Ghidra5 files
- Checks directory structure integrity
- Verifies file permissions

### 4. **Ghidra Detection Test**
- Tests Ghidra path auto-detection logic
- Validates cross-platform compatibility
- Checks Ghidra availability (where applicable)

### 5. **Dependencies Installation Test**
- Installs Python packages (mcp, aiohttp, etc.)
- Tests package imports
- Validates MCP-Ghidra5 module imports

### 6. **Installer Script Test**
- Tests installer script execution
- Validates non-interactive installation
- Checks error handling

### 7. **Security Utils Test**
- Tests security utility functions
- Validates input sanitization
- Checks path validation logic

### 8. **MCP Server Startup Test**
- Tests server initialization
- Validates graceful error handling
- Checks configuration loading

### 9. **Comprehensive Functionality Test**
- Runs existing test suites (if available)
- Validates smoke tests
- Tests core functionality without API keys

## 📊 **Test Results**

Test logs are automatically stored in `test-logs/` with timestamps:

```
test-logs/
├── docker-tests-20250121-143022.log          # Main test log
├── build-ubuntu22-20250121-143022.log        # Ubuntu 22 build log
├── test-ubuntu22-20250121-143022.log         # Ubuntu 22 test log
├── build-kali-20250121-143022.log            # Kali build log
├── test-kali-20250121-143022.log             # Kali test log
└── ...
```

## 🔧 **Configuration**

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for testing | `test_key_placeholder` |
| `SKIP_API_KEY_INPUT` | Skip API key input prompts | `1` |
| `SKIP_GHIDRA_DOWNLOAD` | Skip Ghidra download | `1` |
| `GHIDRA_HEADLESS_PATH` | Custom Ghidra path | Auto-detected |

### Docker Resources

Containers are configured with:
- **CPU**: No limits (uses host CPU)
- **Memory**: No limits (uses host memory)
- **Storage**: Project mounted as volume
- **Network**: Default Docker network

## 🐛 **Troubleshooting**

### Common Issues

#### 1. **Docker Not Running**
```bash
sudo systemctl start docker
sudo usermod -a -G docker $USER  # Add user to docker group
```

#### 2. **Permission Denied**
```bash
chmod +x docker-tests/*.sh
```

#### 3. **Image Build Failures**
- Check internet connection
- Verify Docker has enough disk space
- Try building individual images:
  ```bash
  docker build -t mcp-ghidra5-test-ubuntu22 -f Dockerfile.ubuntu22 .
  ```

#### 4. **Container Test Failures**
- Check container logs in `test-logs/`
- Run container interactively for debugging:
  ```bash
  docker run -it --rm -v $(pwd)/..:/home/testuser/mcp-ghidra5-test mcp-ghidra5-test-ubuntu22 /bin/bash
  ```

### Debug Mode

Run containers interactively for manual testing:
```bash
# Ubuntu 22.04
docker run -it --rm -v $(pwd)/..:/home/testuser/mcp-ghidra5-test mcp-ghidra5-test-ubuntu22 /bin/bash

# Kali Linux  
docker run -it --rm -v $(pwd)/..:/home/testuser/mcp-ghidra5-test mcp-ghidra5-test-kali /bin/bash
```

## 📈 **Performance Expectations**

| Distribution | Build Time | Test Time | Total Time |
|--------------|------------|-----------|------------|
| Ubuntu 22.04 | 2-3 min | 3-5 min | 5-8 min |
| Ubuntu 24.04 | 2-3 min | 3-5 min | 5-8 min |
| Kali Linux | 5-8 min | 4-6 min | 9-14 min |
| Debian 12 | 2-3 min | 3-5 min | 5-8 min |

**Total for all platforms**: ~20-35 minutes

## ✅ **Success Criteria**

A successful test run should show:
- All Docker images build successfully
- All 9 test categories pass in each container
- No critical errors in logs
- Proper cleanup of Docker resources

## 🔄 **Continuous Integration**

This Docker testing infrastructure is designed for:
- **Local Development**: Manual validation before releases
- **CI/CD Integration**: Automated testing in pipelines
- **Release Validation**: Pre-release compatibility testing
- **Regression Testing**: Ensuring changes don't break compatibility

## 📝 **Adding New Tests**

To add new test cases:

1. **Add test function** to `container_test.sh`:
   ```bash
   test_new_feature() {
       log_info "=== New Feature Test ==="
       # Test implementation
       log_success "New feature test completed"
   }
   ```

2. **Add to test list** in main() function:
   ```bash
   local tests=(
       # ... existing tests
       "test_new_feature"
   )
   ```

3. **Test your changes**:
   ```bash
   ./run_docker_tests.sh ubuntu22  # Test on single platform first
   ```

## 🤝 **Contributing**

When contributing Docker test improvements:

1. Test locally on at least 2 distributions
2. Update documentation for any new features
3. Ensure logs are properly captured
4. Maintain backward compatibility
5. Follow existing naming conventions

---

**Version**: 1.0.0  
**Last Updated**: January 21, 2025  
**Maintainer**: MCP-Ghidra5 Development Team