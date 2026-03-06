# Factorization Shortcut Demo - Makefile (MPFR/GMP Required)
# ==============================================================
# 
# Build system for factorization shortcut demo using Z5D predictor patterns.
# Requires MPFR/GMP libraries for exact high-precision arithmetic.
#
# Usage:
#   make          - Build factorization shortcut demo program
#   make test     - Build and run the demonstration
#   make clean    - Clean build artifacts
#   make debug    - Build with debug flags
#   make help     - Show this help
#
# @file Makefile
# @version 1.0

# Directories
SRC_DIR := .
PARENT_DIR := ..
BUILD_DIR := build
BIN_DIR := bin

# Use simplified dependency detection to avoid parent make output issues
# This follows the same pattern as other subdirectories (mersenne-predictor, lucas-index)
GMP_INCLUDE := $(shell \
    if test -f /opt/homebrew/include/gmp.h; then echo -I/opt/homebrew/include; \
    elif test -f /usr/local/include/gmp.h; then echo -I/usr/local/include; \
    elif test -f /usr/include/x86_64-linux-gnu/gmp.h; then echo -I/usr/include/x86_64-linux-gnu; \
    elif test -f /usr/include/gmp.h; then echo -I/usr/include; \
    else echo ""; fi)

MPFR_INCLUDE := $(shell \
    if test -f /opt/homebrew/include/mpfr.h; then echo -I/opt/homebrew/include; \
    elif test -f /usr/local/include/mpfr.h; then echo -I/usr/local/include; \
    elif test -f /usr/include/x86_64-linux-gnu/mpfr.h; then echo -I/usr/include/x86_64-linux-gnu; \
    elif test -f /usr/include/mpfr.h; then echo -I/usr/include; \
    else echo ""; fi)

MPFR_LDFLAGS := $(shell \
    if test -f /opt/homebrew/lib/libmpfr.dylib; then echo -L/opt/homebrew/lib -lmpfr -lgmp; \
    elif test -f /usr/local/lib/libmpfr.a; then echo -L/usr/local/lib -lmpfr -lgmp; \
    elif test -f /usr/lib/x86_64-linux-gnu/libmpfr.so; then echo -L/usr/lib/x86_64-linux-gnu -lmpfr -lgmp; \
    elif test -f /usr/lib/libmpfr.so; then echo -L/usr/lib -lmpfr -lgmp; \
    else echo -lmpfr -lgmp; fi)

$(info Factorization Shortcut Demo using detected MPFR/GMP dependencies)

# Compiler and tool configuration
CC := clang
CFLAGS := -std=c99 -Wall -Wextra -O3 $(GMP_INCLUDE) $(MPFR_INCLUDE) -I$(PARENT_DIR)

# Debug configuration
DEBUG_FLAGS := -g -DDEBUG -O0
ifeq ($(BUILD_TYPE),debug)
    CFLAGS += $(DEBUG_FLAGS)
endif

# Link flags
LDFLAGS := $(MPFR_LDFLAGS) -lm

# Source files
MAIN_SOURCE := factorization_shortcut_demo.c
TARGET := $(BIN_DIR)/factorization_shortcut_demo

# Main executable
MAIN_OBJECT := $(BUILD_DIR)/factorization_shortcut_demo.o

# Default target
.DEFAULT_GOAL := all

# Ensure directories exist
$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

$(BIN_DIR):
	@mkdir -p $(BIN_DIR)

# Main target
all: $(TARGET)

# Build the main executable
$(TARGET): $(MAIN_OBJECT) | $(BIN_DIR)
	@echo "🔗 Linking factorization shortcut demo..."
	@$(CC) $(MAIN_OBJECT) -o $@ $(LDFLAGS)
	@echo "✅ Executable built: $@"

# Compile main source
$(MAIN_OBJECT): $(MAIN_SOURCE) | $(BUILD_DIR)
	@echo "🔨 Compiling: $<"
	@$(CC) $(CFLAGS) -c $< -o $@

# Test target - build and run
test: $(TARGET)
	@echo "Running factorization shortcut demonstration..."
	@echo "=============================================="
	@$(TARGET) --samples 100

# Debug build
debug:
	@$(MAKE) BUILD_TYPE=debug all

# Test with debug build
test-debug:
	@$(MAKE) BUILD_TYPE=debug test

# Demo with different parameters
demo: $(TARGET)
	@echo "🚀 Running factorization shortcut demo with various parameters..."
	@echo ""
	@echo "=== Small scale demo (quick) ==="
	@$(TARGET) --Nmax 10000 --samples 50
	@echo ""
	@echo "=== Medium scale demo ==="
	@$(TARGET) --Nmax 100000 --samples 100
	@echo ""
	@echo "=== Large scale demo ==="
	@$(TARGET) --Nmax 1000000 --samples 200

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR) $(BIN_DIR)

# Show build information
info:
	@echo "Factorization Shortcut Demo Build Configuration (MPFR/GMP Required)"
	@echo "=================================================================="
	@echo "Compiler: $(CC)"
	@echo "C Flags: $(CFLAGS)"
	@echo "LD Flags: $(LDFLAGS)"
	@echo "Build Type: $(BUILD_TYPE)"
	@echo "Target: $(TARGET)"
	@echo ""
	@echo "Detected Dependencies:"
	@echo "  GMP Include: $(GMP_INCLUDE)"
	@echo "  MPFR Include: $(MPFR_INCLUDE)"
	@echo "  MPFR Link: $(MPFR_LDFLAGS)"

# Help target
help:
	@echo "Factorization Shortcut Demo - Build System"
	@echo "=========================================="
	@echo ""
	@echo "Available targets:"
	@echo "  all        - Build the demo executable (default)"
	@echo "  test       - Build and run basic test"
	@echo "  demo       - Build and run comprehensive demonstration"
	@echo "  debug      - Build with debug flags"
	@echo "  test-debug - Build and run test with debug flags"
	@echo "  clean      - Clean build artifacts"
	@echo "  info       - Show build configuration"
	@echo "  help       - Show this help"
	@echo ""
	@echo "Build options:"
	@echo "  make BUILD_TYPE=debug    - Build with debug flags"
	@echo ""
	@echo "Required dependencies:"
	@echo "  - MPFR library (libmpfr-dev)"
	@echo "  - GMP library (libgmp-dev)"
	@echo ""
	@echo "Example usage:"
	@echo "  make demo    # Build and run comprehensive demonstration"

# Phony targets
.PHONY: all test debug test-debug demo clean info help

# Dependencies tracking (optional)
-include $(BUILD_DIR)/*.d