# Golden Spiral for Z5D Candidates - Makefile
# ==========================================
#
# Build system for Golden Spiral Z5D candidate screening implementation.
# Inherits dependencies from parent Makefile and builds shared libraries.
# Uses locally detected MPFR/GMP; follows existing pattern from parent modules.
# MPFR ONLY - no new dependencies introduced as per requirements.
#
# Usage:
#   make          - Build golden spiral demo executable
#   make test     - Build and run demonstration
#   make clean    - Clean build artifacts
#   make help     - Show this help
#
# @file Makefile
# @author D.A.L. III (Dionisio Alberto Lopez III)  
# @version 1.0

# Ensure default goal is 'all' regardless of rule order
.DEFAULT_GOAL := all

# Directories
SRC_DIR := .
PARENT_DIR := ..
BUILD_DIR := build
BIN_DIR := bin

# Target executable
TARGET := $(BIN_DIR)/golden_spiral_demo

# Source files
SOURCES := golden_spiral_demo.c z_golden_lucas.c
OBJECTS := $(addprefix $(BUILD_DIR)/, $(SOURCES:.c=.o))
HEADERS := z_golden_lucas.h z_framework_params_golden.h

# Use simplified dependency detection to avoid parent make output issues
# This follows the same pattern as lucas-index and mersenne-predictor
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

$(info Golden Spiral using detected MPFR/GMP dependencies (no new dependencies))

# Compiler and tool configuration  
CC := clang
CFLAGS := -std=c11 -Wall -Wextra -O3 $(GMP_INCLUDE) $(MPFR_INCLUDE) -I$(PARENT_DIR)
LDFLAGS := -lm $(MPFR_LDFLAGS)

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
$(TARGET): $(OBJECTS) | $(BIN_DIR)
	@echo "Linking Golden Spiral demo: $@"
	@$(CC) $(OBJECTS) $(LDFLAGS) -o $@

# Compile source files
$(BUILD_DIR)/%.o: %.c $(HEADERS) | $(BUILD_DIR)
	@echo "Compiling: $<"
	@$(CC) $(CFLAGS) -c $< -o $@

# Build and run test
test: $(TARGET)
	@echo "Testing Golden Spiral for Z5D Candidates..."
	@echo "Test 1: Known Mersenne exponents"
	@./$(TARGET) --known
	@echo ""
	@echo "Test 2: Golden spiral scaling demonstration"
	@./$(TARGET) --spiral
	@echo ""
	@echo "Test 3: Single exponent test (p=127)"
	@./$(TARGET) --exp 127 --verbose
	@echo ""
	@echo "Test 4: Performance benchmark"
	@./$(TARGET) --benchmark

# Debug build
debug: CFLAGS += -g -DDEBUG -O0
debug: $(TARGET)

# Clean build artifacts
clean:
	@echo "Cleaning Golden Spiral build artifacts..."
	@rm -rf $(BUILD_DIR) $(BIN_DIR)

# Show build configuration
info:
	@echo "Golden Spiral for Z5D Candidates - Build Configuration"
	@echo "====================================================="
	@echo "Compiler:        $(CC)"
	@echo "CFLAGS:          $(CFLAGS)"
	@echo "LDFLAGS:         $(LDFLAGS)"
	@echo "Target:          $(TARGET)"
	@echo "Sources:         $(SOURCES)"
	@echo "Platform:        $(UNAME_S) $(UNAME_M)"
	@echo "GMP Include:     $(GMP_INCLUDE)"
	@echo "MPFR Include:    $(MPFR_INCLUDE)"
	@echo "MPFR/GMP Libs:   $(MPFR_LDFLAGS)"

# Show help
help:
	@echo "Golden Spiral for Z5D Candidates - Build System"
	@echo "=============================================="
	@echo ""
	@echo "Targets:"
	@echo "  all        - Build golden spiral demo executable (default)"
	@echo "  test       - Build and run comprehensive tests"
	@echo "  debug      - Build with debug symbols"
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
	@echo "  - No new dependencies introduced"
	@echo ""
	@echo "Example usage:"
	@echo "  make test   # Build and run test cases"
	@echo "  ./bin/golden_spiral_demo --help"
	@echo "  ./bin/golden_spiral_demo --exp 127 --verbose"
	@echo "  ./bin/golden_spiral_demo --spiral --benchmark"

# Phony targets
.PHONY: all test debug clean info help parent-libs

# Dependencies tracking (optional)
-include $(BUILD_DIR)/*.d