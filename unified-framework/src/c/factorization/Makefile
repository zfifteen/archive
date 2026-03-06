# RSA-100 Geometric Factorization Test - Makefile (MPFR/GMP Required)
# =======================================================================
# 
# Build system for RSA-100 factorization test using Z5D predictor.
# Requires MPFR/GMP libraries for exact high-precision arithmetic.
#
# Usage:
#   make          - Build factorization test program
#   make test     - Build and run the test
#   make clean    - Clean build artifacts
#   make debug    - Build with debug flags
#   make help     - Show this help
#
# @file Makefile
# @version 2.0

# Directories
SRC_DIR := .
PARENT_DIR := ..
BUILD_DIR := build
BIN_DIR := bin

# Inherit dependencies from parent Makefile by calling parent's dependency detection
# This ensures we use the same library paths that work in the parent build
PARENT_MAKE_VARS := $(shell cd $(PARENT_DIR) && $(MAKE) --no-print-directory -s echo-vars 2>/dev/null || echo "")

# If parent vars not available, extract them directly
ifeq ($(PARENT_MAKE_VARS),)
GMP_INCLUDE := $(shell cd $(PARENT_DIR) && $(MAKE) --no-print-directory -f Makefile print-GMP_INCLUDE 2>/dev/null || echo -I/opt/homebrew/include)
MPFR_INCLUDE := $(shell cd $(PARENT_DIR) && $(MAKE) --no-print-directory -f Makefile print-MPFR_INCLUDE 2>/dev/null || echo -I/opt/homebrew/include)
MPFR_LDFLAGS := $(shell cd $(PARENT_DIR) && $(MAKE) --no-print-directory -f Makefile print-MPFR_LDFLAGS 2>/dev/null || echo -L/opt/homebrew/lib -lmpfr -lgmp)
else
# Use simplified fallback detection for common paths
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
    if test -f /opt/homebrew/lib/libmpfr.dylib; then echo -L/opt/homebrew/lib -lmpfr -lgmp; \
    elif test -f /usr/local/lib/libmpfr.a; then echo -L/usr/local/lib -lmpfr -lgmp; \
    elif test -f /usr/lib/libmpfr.so; then echo -L/usr/lib -lmpfr -lgmp; \
    else echo -lmpfr -lgmp; fi)
endif

$(info Using MPFR/GMP for exact arithmetic)

# Compiler and tool configuration
CC := clang
CFLAGS := -std=c11 -Wall -Wextra -O3 $(GMP_INCLUDE) $(MPFR_INCLUDE)
LDFLAGS := -lm $(MPFR_LDFLAGS)

# Target executable
TARGET := $(BIN_DIR)/rsa100_factorization
SOURCE := $(SRC_DIR)/rsa100_factorization.c

# Z5D library dependencies from parent directory
Z5D_SOURCES := $(PARENT_DIR)/z5d_predictor.c $(PARENT_DIR)/z5d_phase2.c
Z5D_HEADERS := $(PARENT_DIR)/z5d_predictor.h $(PARENT_DIR)/z5d_phase2.h $(PARENT_DIR)/z_framework_params.h

# Object files (MPFR/GMP required)
Z5D_OBJECTS := $(BUILD_DIR)/z5d_predictor.o $(BUILD_DIR)/z5d_phase2.o
MAIN_OBJECT := $(BUILD_DIR)/rsa100_factorization.o

# Platform detection
UNAME_S := $(shell uname -s 2>/dev/null || echo Unknown)
UNAME_M := $(shell uname -m 2>/dev/null || echo Unknown)

# Platform-specific configuration
ifeq ($(UNAME_S),Darwin)
    # macOS optimizations - only apply ARM flags on ARM systems
    ifeq ($(UNAME_M),arm64)
        CFLAGS += -march=armv8.5-a -mcpu=apple-m1
    endif
    # OpenMP may not be available by default on macOS
    HAS_OPENMP := $(shell echo 'int main(){return 0;}' | $(CC) -x c - -fopenmp >/dev/null 2>&1 && echo 1 || echo 0)
    ifeq ($(HAS_OPENMP),1)
        CFLAGS += -fopenmp
        LDFLAGS += -fopenmp
    else
        CFLAGS += -DZ5D_NO_OPENMP
    endif
else ifeq ($(UNAME_S),Linux)
    # Linux optimizations
    CFLAGS += -march=native -mavx2 -mfma
    # Check if OpenMP is available for linking
    HAS_OPENMP := $(shell echo 'int main(){return 0;}' | $(CC) -x c - -fopenmp >/dev/null 2>&1 && echo 1 || echo 0)
    ifeq ($(HAS_OPENMP),1)
        CFLAGS += -fopenmp
        LDFLAGS += -fopenmp
    else
        CFLAGS += -DZ5D_NO_OPENMP
    endif
else
    # Generic Unix/Windows
    CFLAGS += -DZ5D_NO_OPENMP
endif

# Debug build configuration
DEBUG_CFLAGS := -g -O0 -DDEBUG -fsanitize=address
DEBUG_LDFLAGS := -fsanitize=address
ifeq ($(BUILD_TYPE),debug)
    CFLAGS := $(filter-out -O3,$(CFLAGS)) $(DEBUG_CFLAGS)
    LDFLAGS += $(DEBUG_LDFLAGS)
endif

# Include paths
CFLAGS += -I$(PARENT_DIR)

# Create directories
$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

$(BIN_DIR):
	@mkdir -p $(BIN_DIR)

# Default target
all: $(TARGET)

# Build the main executable
$(TARGET): $(MAIN_OBJECT) $(Z5D_OBJECTS) | $(BIN_DIR)
	@echo "Linking: $@"
	@$(CC) $(MAIN_OBJECT) $(Z5D_OBJECTS) $(LDFLAGS) -o $@

# Compile main source
$(MAIN_OBJECT): $(SOURCE) $(Z5D_HEADERS) | $(BUILD_DIR)
	@echo "Compiling: $<"
	@$(CC) $(CFLAGS) -c $< -o $@

# Compile Z5D predictor (required)
$(BUILD_DIR)/z5d_predictor.o: $(PARENT_DIR)/z5d_predictor.c $(PARENT_DIR)/z5d_predictor.h | $(BUILD_DIR)
	@echo "Compiling: $<"
	@$(CC) $(CFLAGS) -c $< -o $@

# Compile Z5D phase2 (required)
$(BUILD_DIR)/z5d_phase2.o: $(PARENT_DIR)/z5d_phase2.c $(PARENT_DIR)/z5d_phase2.h | $(BUILD_DIR)
	@echo "Compiling: $<"
	@$(CC) $(CFLAGS) -c $< -o $@

# Test target - build and run
test: $(TARGET)
	@echo "Running RSA-100 factorization test..."
	@echo "======================================"
	@$(TARGET)

# Debug build
debug:
	@$(MAKE) BUILD_TYPE=debug all

# Test with debug build
test-debug:
	@$(MAKE) BUILD_TYPE=debug test

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR) $(BIN_DIR)

# Show build information
info:
	@echo "RSA-100 Factorization Test Build Configuration (MPFR/GMP Required)"
	@echo "=================================================================="
	@echo "Platform:      $(UNAME_S)"
	@echo "Compiler:      $(CC)"
	@echo "CFLAGS:        $(CFLAGS)"
	@echo "LDFLAGS:       $(LDFLAGS)"
	@echo "Target:        $(TARGET)"
	@echo "Z5D Sources:   $(Z5D_SOURCES)"
	@echo "MPFR/GMP:      Required and available"

# Help target
help:
	@echo "RSA-100 Geometric Factorization Test - Build System (MPFR/GMP Required)"
	@echo "======================================================================="
	@echo ""
	@echo "Available targets:"
	@echo "  all        - Build factorization test program (default)"
	@echo "  test       - Build and run the factorization test"
	@echo "  debug      - Build with debug symbols and sanitizers"
	@echo "  test-debug - Build with debug flags and run the test"
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
	@echo "  - Z5D predictor implementation (../z5d_predictor.c)"
	@echo "  - Z5D phase2 parallel/SIMD (../z5d_phase2.c)"
	@echo "  - OpenMP (optional, auto-detected)"
	@echo ""
	@echo "Example usage:"
	@echo "  make test    # Build and run RSA-100 test with MPFR exact arithmetic"

# Phony targets
.PHONY: all test debug test-debug clean info help

# Dependencies tracking (optional)
-include $(BUILD_DIR)/*.d