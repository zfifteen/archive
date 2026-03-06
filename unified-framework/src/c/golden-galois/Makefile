# Multi-Base Golden Analysis and Galois Link - Makefile
# ====================================================
#
# Build system for Multi-Base Golden Analysis with Galois field extensions.
# Inherits dependencies from parent Makefile and builds shared libraries.
# Uses locally detected MPFR/GMP/OpenMP; follows existing pattern from mersenne-predictor.
#
# Usage:
#   make          - Build golden-galois analysis executable
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

$(info Golden-Galois analysis using detected MPFR/GMP/OpenMP dependencies)

# Compiler and tool configuration
CC := clang
CFLAGS := -std=c11 -Wall -Wextra -O3 $(GMP_INCLUDE) $(MPFR_INCLUDE) -I$(PARENT_DIR) $(OPENMP_FLAGS)
LDFLAGS := $(MPFR_LDFLAGS) $(OPENMP_FLAGS)

# Target executable
TARGET := bin/golden_galois_analysis

# Source files
MAIN_SOURCE := golden_galois_analysis.c
GOLDEN_SOURCES := golden_ratios.c galois_field.c mersenne_golden_link.c
OBJECT_FILES := $(GOLDEN_SOURCES:.c=.o)

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
	@echo "🔨 Building golden-galois analysis executable..."
	@$(CC) $(CFLAGS) $(MAIN_SOURCE) $(OBJECT_FILES) -o $@ $(LDFLAGS)
	@echo "✅ Executable built: $@"

# Build object files
%.o: %.c %.h
	@echo "🔨 Compiling $<..."
	@$(CC) $(CFLAGS) -c $< -o $@

# Test target
.PHONY: test
test: $(TARGET)
	@echo "🧪 Running golden-galois demonstration..."
	@./demo_golden_galois.sh

# Information target
.PHONY: info
info:
	@echo "Golden-Galois Analysis Build Configuration"
	@echo "=========================================="
	@echo "Compiler: $(CC)"
	@echo "CFLAGS: $(CFLAGS)"
	@echo "LDFLAGS: $(LDFLAGS)"
	@echo "Target: $(TARGET)"
	@echo "Platform: $(UNAME_S) $(UNAME_M)"
	@echo "GMP Include: $(GMP_INCLUDE)"
	@echo "MPFR Include: $(MPFR_INCLUDE)"
	@echo "OpenMP: $(OPENMP_FLAGS)"

# Clean target
.PHONY: clean
clean:
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR) $(BIN_DIR) *.o
	@echo "✅ Clean complete"

# Help target
.PHONY: help
help:
	@echo "Multi-Base Golden Analysis and Galois Link - Build System"
	@echo "========================================================"
	@echo ""
	@echo "Available targets:"
	@echo "  make          - Build golden-galois analysis executable"
	@echo "  make test     - Build and run demonstration"
	@echo "  make info     - Show build configuration"
	@echo "  make clean    - Clean build artifacts"
	@echo "  make help     - Show this help"
	@echo ""
	@echo "Dependencies (auto-detected):"
	@echo "  - MPFR library (libmpfr-dev)"
	@echo "  - GMP library (libgmp-dev)"
	@echo "  - OpenMP (optional, for parallel processing)"
	@echo ""
	@echo "Example usage:"
	@echo "  ./$(TARGET) --ratio phi --mersenne 31 --verbose"

# Phony targets
.PHONY: all test info clean help parent-libs