# Modular Geometric Progressions in Cryptographic Analysis - Makefile
# ===================================================================
#
# Build system for modular geometric progression analysis in cryptographic contexts.
# Inherits dependencies from parent Makefile and builds shared libraries.
# Uses locally detected MPFR/GMP/OpenMP; follows existing pattern from other C modules.
#
# Usage:
#   make          - Build modular geometric progressions executable
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

MPFR_LDFLAGS := $(shell \
    if test -f /opt/homebrew/lib/libmpfr.dylib; then echo -L/opt/homebrew/lib; \
    elif test -f /opt/homebrew/lib/libmpfr.a; then echo -L/opt/homebrew/lib; \
    elif test -f /usr/local/lib/libmpfr.so; then echo -L/usr/local/lib; \
    elif test -f /usr/local/lib/libmpfr.a; then echo -L/usr/local/lib; \
    elif test -f /usr/lib/x86_64-linux-gnu/libmpfr.so; then echo -L/usr/lib/x86_64-linux-gnu; \
    else echo ""; fi) -lmpfr -lgmp

# OpenMP detection for parallel processing capability
OPENMP_FLAGS := $(shell \
    if command -v clang > /dev/null && clang -fopenmp -xc /dev/null -o /dev/null 2>/dev/null; then echo -fopenmp; \
    elif command -v gcc > /dev/null && gcc -fopenmp -xc /dev/null -o /dev/null 2>/dev/null; then echo -fopenmp; \
    else echo ""; fi)

$(info Modular Geometric Progressions using detected MPFR/GMP/OpenMP dependencies)

# Compiler and tool configuration
CC := clang
CFLAGS := -std=c11 -Wall -Wextra -O3 $(GMP_INCLUDE) $(MPFR_INCLUDE) -I$(PARENT_DIR) $(OPENMP_FLAGS)
LDFLAGS := $(MPFR_LDFLAGS) $(OPENMP_FLAGS) -lm

# Target executable
TARGET := bin/modular_geometric_progressions

# Source files
MAIN_SOURCE := modular_geometric_progressions.c
CRYPTO_SOURCES := crypto_analysis.c modular_progressions.c dual_ec_analysis.c sha256_bounds.c
OBJECT_FILES := $(CRYPTO_SOURCES:.c=.o)

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
all: $(TARGET)

# Invoke parent build for shared libraries (as required by problem statement)
.PHONY: parent-libs
parent-libs:
	@echo "Invoking parent to build shared libs..."
	@cd $(PARENT_DIR) && $(MAKE) shared

# Build the main executable
$(TARGET): $(OBJECT_FILES) $(MAIN_SOURCE) | $(BIN_DIR)
	@echo "🔨 Building modular geometric progressions executable..."
	@$(CC) $(CFLAGS) $(MAIN_SOURCE) $(OBJECT_FILES) -o $@ $(LDFLAGS)
	@echo "✅ Executable built: $@"

# Build object files
%.o: %.c %.h | $(BUILD_DIR)
	@echo "🔧 Compiling $<..."
	@$(CC) $(CFLAGS) -c $< -o $@

# Test target
test: $(TARGET)
	@echo "🧪 Running modular geometric progressions demonstration..."
	@./demo_modular_geometric_progressions.sh

# Clean target
clean:
	@echo "🧹 Cleaning modular geometric progressions build artifacts..."
	@rm -rf $(BUILD_DIR) $(BIN_DIR) *.o *.out *.csv *.txt
	@echo "✅ Clean complete"

# Info target
info:
	@echo "=================================="
	@echo "  Modular Geometric Progressions"
	@echo "=================================="
	@echo "Platform:     $(UNAME_S)"
	@echo "Architecture: $(UNAME_M)"
	@echo "Compiler:     $(CC)"
	@echo "Precision:    256-bit MPFR"
	@echo "Target:       $(TARGET)"
	@echo "Dependencies: MPFR/GMP/OpenMP"
	@echo "=================================="

# Help target
help:
	@echo "Modular Geometric Progressions in Cryptographic Analysis"
	@echo "========================================================"
	@echo ""
	@echo "Available targets:"
	@echo "  make          - Build modular geometric progressions executable"
	@echo "  make test     - Build and run demonstration"
	@echo "  make clean    - Clean build artifacts"
	@echo "  make info     - Show build configuration"
	@echo "  make help     - Show this help"
	@echo ""
	@echo "Requirements:"
	@echo "  - MPFR library (libmpfr-dev)"
	@echo "  - GMP library (libgmp-dev)"
	@echo "  - OpenMP (optional, for parallel processing)"
	@echo ""
	@echo "Example usage:"
	@echo "  make test   # Build and run modular geometric progressions demo"

# Phony targets
.PHONY: all test clean info help parent-libs

# Dependencies tracking (optional)
-include $(BUILD_DIR)/*.d