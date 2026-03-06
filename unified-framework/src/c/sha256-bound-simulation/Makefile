# SHA-256 Fractional Bound Simulation - Makefile
# ===============================================
#
# Build system for SHA-256 Fractional Bound Simulation implementation.
# Inherits dependencies from parent Makefile and builds shared libraries.
# Uses locally detected MPFR/GMP; follows existing pattern from mersenne-predictor.
#
# Usage:
#   make          - Build SHA-256 bound analyzer executable
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

# Inherit dependency detection from parent Makefile to avoid introducing new dependencies
PARENT_MAKE_VARS := $(shell cd $(PARENT_DIR) && $(MAKE) --no-print-directory -s echo-vars 2>/dev/null || echo "")

# Use simplified dependency detection from parent
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

MPFR_LDFLAGS := $(shell \
    if test -f /opt/homebrew/lib/libmpfr.dylib; then echo -L/opt/homebrew/lib; \
    elif test -f /opt/homebrew/lib/libmpfr.a; then echo -L/opt/homebrew/lib; \
    elif test -f /usr/local/lib/libmpfr.so; then echo -L/usr/local/lib; \
    elif test -f /usr/local/lib/libmpfr.a; then echo -L/usr/local/lib; \
    elif test -f /usr/lib/x86_64-linux-gnu/libmpfr.so; then echo -L/usr/lib/x86_64-linux-gnu; \
    else echo ""; fi) -lmpfr -lgmp

$(info SHA-256 Bound Analyzer using detected MPFR/GMP dependencies)

# Compiler and tool configuration
CC := clang
CFLAGS := -std=c99 -Wall -Wextra -O3 $(GMP_INCLUDE) $(MPFR_INCLUDE) -I$(PARENT_DIR)
LDFLAGS := -lm $(MPFR_LDFLAGS)

# Source files
MAIN_SOURCE := sha256_bound_analyzer.c

# Target executable
TARGET := $(BIN_DIR)/sha256_bound_analyzer

# Platform detection for optimization
UNAME_S := $(shell uname -s 2>/dev/null || echo Windows)
UNAME_M := $(shell uname -m 2>/dev/null || echo unknown)

# Platform-specific optimizations
ifeq ($(UNAME_S),Darwin)
    # macOS optimizations
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
all: $(TARGET)

# Invoke parent build for shared libraries (as required by problem statement)
.PHONY: parent-libs
parent-libs:
	@echo "Invoking parent to build shared libs..."
	@cd $(PARENT_DIR) && $(MAKE) shared

# Build the main executable
$(TARGET): $(MAIN_SOURCE) | $(BIN_DIR)
	@echo "🔨 Building SHA-256 bound analyzer executable..."
	@$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS)
	@echo "✅ Executable built: $@"

# Test target (runs demonstration)
test: $(TARGET)
	@echo "🧪 Running SHA-256 bound simulation demonstration..."
	@./demo_sha256_bounds.sh

# Demo target (builds and runs small test)
demo: $(TARGET)
	@echo "🎯 Running quick demo with N=100..."
	@$(TARGET) -n 100 -v

# Build configuration information
info:
	@echo "SHA-256 Bound Analyzer Build Configuration"
	@echo "=========================================="
	@echo "Compiler:     $(CC)"
	@echo "Platform:     $(UNAME_S) $(UNAME_M)"
	@echo "CFLAGS:       $(CFLAGS)"
	@echo "LDFLAGS:      $(LDFLAGS)"
	@echo "Target:       $(TARGET)"
	@echo "Source:       $(MAIN_SOURCE)"

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR) $(BIN_DIR)
	@echo "✅ Clean complete"

# Help target
help:
	@echo "SHA-256 Fractional Bound Simulation - Build System"
	@echo "=================================================="
	@echo ""
	@echo "Available targets:"
	@echo "  all        - Build SHA-256 bound analyzer executable (default)"
	@echo "  test       - Build and run full demonstration"
	@echo "  demo       - Build and run quick demo"
	@echo "  parent-libs - Invoke parent to build shared libraries"
	@echo "  clean      - Clean build artifacts"
	@echo "  info       - Show build configuration"
	@echo "  help       - Show this help"
	@echo ""
	@echo "Build options:"
	@echo "  make debug  - Build with debug flags"
	@echo ""
	@echo "Dependencies:"
	@echo "  - MPFR library (libmpfr-dev)"
	@echo "  - GMP library (libgmp-dev)"
	@echo ""
	@echo "Example usage:"
	@echo "  make test   # Build and run demonstration"
	@echo "  ./$(TARGET) -n 10000 -v  # Run with 10,000 primes (verbose)"

# Phony targets
.PHONY: all test demo parent-libs clean info help

# Dependencies tracking (optional)
-include $(BUILD_DIR)/*.d