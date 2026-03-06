# XAI Chat Streaming Client - Makefile
# ======================================
#
# Build system for XAI Chat Streaming Client implementation.
# Inherits dependencies from parent Makefile and builds shared libraries.
# Uses locally detected GMP/MPFR; follows existing pattern from parent modules.
# No new dependencies introduced as per requirements.
#
# Usage:
#   make          - Build xai chat client and mock server
#   make test     - Build and run demonstration
#   make clean    - Clean build artifacts
#   make help     - Show this help
#
# @file Makefile
# @version 1.0

# Ensure default goal is 'all' regardless of rule order
.DEFAULT_GOAL := all

# Directories
SRC_DIR := .
PARENT_DIR := ..
BUILD_DIR := build
BIN_DIR := bin

# Target executables
CLIENT_TARGET := $(BIN_DIR)/xai_chat_client
MOCK_SERVER_TARGET := $(BIN_DIR)/mock_xai_server
TEST_FS_TARGET := $(BIN_DIR)/test_fs_tools

# Source files
CLIENT_SOURCES := xai_chat_client.c xai_client.c bash_tool.c sse_parser.c fs_tools.c
MOCK_SERVER_SOURCES := mock_xai_server.c
TEST_FS_SOURCES := test_fs_tools.c fs_tools.c

# Object files
CLIENT_OBJECTS := $(addprefix $(BUILD_DIR)/, $(CLIENT_SOURCES:.c=.o))
MOCK_SERVER_OBJECTS := $(addprefix $(BUILD_DIR)/, $(MOCK_SERVER_SOURCES:.c=.o))
TEST_FS_OBJECTS := $(addprefix $(BUILD_DIR)/, $(TEST_FS_SOURCES:.c=.o))

# Headers
HEADERS := xai_client.h bash_tool.h sse_parser.h fs_tools.h

# Use simplified dependency detection to avoid parent make output issues
GMP_INCLUDE := $(shell \
    if test -f /opt/homebrew/include/gmp.h; then echo -I/opt/homebrew/include; \
    elif test -f /usr/local/include/gmp.h; then echo -I/usr/local/include; \
    elif test -f /usr/include/gmp.h; then echo -I/usr/include; \
    else echo ""; fi)

MPFR_INCLUDE := $(shell \
    if test -f /opt/homebrew/include/mpfr.h; then echo -I/opt/homebrew/include; \
    elif test -f /usr/local/include/mpfr.h; then echo -I/usr/local/include; \
    elif test -f /usr/include/mpfr.h; then echo -I/usr/include; \
    else echo ""; fi)

GMP_LDFLAGS := $(shell \
    if test -f /opt/homebrew/lib/libgmp.dylib; then echo -L/opt/homebrew/lib; \
    elif test -f /opt/homebrew/lib/libgmp.a; then echo -L/opt/homebrew/lib; \
    elif test -f /usr/local/lib/libgmp.so; then echo -L/usr/local/lib; \
    elif test -f /usr/local/lib/libgmp.a; then echo -L/usr/local/lib; \
    elif test -f /usr/lib/x86_64-linux-gnu/libgmp.so; then echo -L/usr/lib/x86_64-linux-gnu; \
    else echo ""; fi) -lgmp

MPFR_LDFLAGS := $(shell \
    if test -f /opt/homebrew/lib/libmpfr.dylib; then echo -L/opt/homebrew/lib; \
    elif test -f /opt/homebrew/lib/libmpfr.a; then echo -L/opt/homebrew/lib; \
    elif test -f /usr/local/lib/libmpfr.so; then echo -L/usr/local/lib; \
    elif test -f /usr/local/lib/libmpfr.a; then echo -L/usr/local/lib; \
    elif test -f /usr/lib/x86_64-linux-gnu/libmpfr.so; then echo -L/usr/lib/x86_64-linux-gnu; \
    else echo ""; fi) -lmpfr -lgmp

$(info XAI Chat Streaming Client using detected GMP/MPFR dependencies (no new dependencies))

# Compiler and tool configuration  
CC := clang
CFLAGS := -std=c11 -Wall -Wextra -O3 $(GMP_INCLUDE) $(MPFR_INCLUDE) -I$(PARENT_DIR)
LDFLAGS := -lm $(MPFR_LDFLAGS) -lcurl -ljson-c

# Platform detection for optimization
UNAME_S := $(shell uname -s 2>/dev/null || echo Unknown)
UNAME_M := $(shell uname -m 2>/dev/null || echo Unknown)

# Platform-specific optimizations
ifeq ($(UNAME_S),Darwin)
    # macOS optimizations - only apply ARM flags on ARM systems
    ifeq ($(UNAME_M),arm64)
        CFLAGS += -march=armv8.5-a -mcpu=apple-m1
    endif
endif

# Create directories
$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

$(BIN_DIR):
	@mkdir -p $(BIN_DIR)

# Default target
all: $(CLIENT_TARGET) $(MOCK_SERVER_TARGET)

# Invoke parent build for shared libraries (as required by problem statement)
.PHONY: parent-libs
parent-libs:
	@echo "Invoking parent to build shared libs..."
	@cd $(PARENT_DIR) && $(MAKE) shared

# Build the client executable
$(CLIENT_TARGET): $(CLIENT_OBJECTS) | $(BIN_DIR)
	@echo "🔨 Building XAI chat client executable..."
	@$(CC) $(CFLAGS) $(CLIENT_OBJECTS) -o $@ $(LDFLAGS)
	@echo "✅ Client executable built: $@"

# Build the mock server executable
$(MOCK_SERVER_TARGET): $(MOCK_SERVER_OBJECTS) | $(BIN_DIR)
	@echo "🔨 Building mock XAI server executable..."
	@$(CC) $(CFLAGS) $(MOCK_SERVER_OBJECTS) -o $@ $(LDFLAGS)
	@echo "✅ Mock server executable built: $@"

# Build the filesystem tools test executable
$(TEST_FS_TARGET): $(TEST_FS_OBJECTS) | $(BIN_DIR)
	@echo "🔨 Building filesystem tools test executable..."
	@$(CC) $(CFLAGS) $(TEST_FS_OBJECTS) -o $@ $(LDFLAGS)
	@echo "✅ Test executable built: $@"

# Build object files
$(BUILD_DIR)/%.o: %.c $(HEADERS) | $(BUILD_DIR)
	@echo "🔧 Compiling $<..."
	@$(CC) $(CFLAGS) -c $< -o $@

# Test targets
.PHONY: test test-fs
test: all
	@echo "Running XAI chat client demonstration..."
	@bash demo_xai_chat_client.sh

test-fs: $(TEST_FS_TARGET)
	@echo "Running filesystem tools tests..."
	@$(TEST_FS_TARGET)

# Clean target
.PHONY: clean
clean:
	@echo "🧹 Cleaning XAI chat client build artifacts..."
	@rm -rf $(BUILD_DIR) $(BIN_DIR)
	@echo "✅ Clean complete"

# Info target
.PHONY: info
info:
	@echo "=================================="
	@echo "  XAI Chat Streaming Client"
	@echo "=================================="
	@echo "Platform:     $(UNAME_S)"
	@echo "Architecture: $(UNAME_M)"
	@echo "Compiler:     $(CC)"
	@echo "Dependencies: GMP/MPFR/curl/json-c"
	@echo "Client:       $(CLIENT_TARGET)"
	@echo "Mock Server:  $(MOCK_SERVER_TARGET)"
	@echo "=================================="

# Help target
.PHONY: help
help:
	@echo "XAI Chat Streaming Client - Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  make          - Build XAI chat client and mock server"
	@echo "  make test     - Build and run demonstration"
	@echo "  make clean    - Clean build artifacts"
	@echo "  make info     - Show build configuration"
	@echo "  make help     - Show this help"
	@echo ""
	@echo "Requirements:"
	@echo "  - MPFR library (libmpfr-dev)"
	@echo "  - GMP library (libgmp-dev)"
	@echo "  - libcurl (libcurl4-openssl-dev)"
	@echo "  - json-c (libjson-c-dev)"
	@echo ""
	@echo "Example usage:"
	@echo "  make test   # Build and run XAI chat client demo"

# Phony targets
.PHONY: all test clean info help parent-libs

# Dependencies tracking (optional)
-include $(BUILD_DIR)/*.d
