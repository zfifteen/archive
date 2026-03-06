# Lucas-Lehmer Convergence Prediction - Makefile
# ===============================================
#
# Build system for Lucas-Lehmer Test convergence prediction.
# Inherits dependencies from parent Makefile and builds shared libraries.
# Uses locally detected MPFR/GMP; follows existing pattern from other implementations.
#
# Usage:
#   make          - Build Lucas-Lehmer predictor executable
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

# Enhanced dependency detection with fallback support
PKG_CONFIG_EXISTS := $(shell command -v pkg-config >/dev/null 2>&1 && echo 1 || echo 0)

# Try pkg-config first, then manual detection
ifeq ($(PKG_CONFIG_EXISTS),1)
    GMP_AVAILABLE := $(shell pkg-config --exists gmp && echo 1 || echo 0)
    MPFR_AVAILABLE := $(shell pkg-config --exists mpfr && echo 1 || echo 0)
    
    ifeq ($(GMP_AVAILABLE),1)
        GMP_INCLUDE := $(shell pkg-config --cflags gmp)
        GMP_LIB := $(shell pkg-config --libs gmp)
    endif
    
    ifeq ($(MPFR_AVAILABLE),1)
        MPFR_INCLUDE := $(shell pkg-config --cflags mpfr)
        MPFR_LIB := $(shell pkg-config --libs mpfr)
    endif
else
    GMP_AVAILABLE := 0
    MPFR_AVAILABLE := 0
endif

# Fallback manual detection if pkg-config failed
ifeq ($(GMP_AVAILABLE),0)
    GMP_INCLUDE := $(shell \
        if test -f /opt/homebrew/include/gmp.h; then echo -I/opt/homebrew/include; \
        elif test -f /usr/local/include/gmp.h; then echo -I/usr/local/include; \
        elif test -f /usr/include/gmp.h; then echo -I/usr/include; \
        else echo ""; fi)
    GMP_LIB := $(shell \
        if test -f /opt/homebrew/lib/libgmp.dylib; then echo -L/opt/homebrew/lib -lgmp; \
        elif test -f /usr/local/lib/libgmp.so; then echo -L/usr/local/lib -lgmp; \
        elif test -f /usr/lib/x86_64-linux-gnu/libgmp.so; then echo -lgmp; \
        else echo ""; fi)
    ifneq ($(GMP_INCLUDE),)
        GMP_AVAILABLE := 1
    endif
endif

ifeq ($(MPFR_AVAILABLE),0)
    MPFR_INCLUDE := $(shell \
        if test -f /opt/homebrew/include/mpfr.h; then echo -I/opt/homebrew/include; \
        elif test -f /usr/local/include/mpfr.h; then echo -I/usr/local/include; \
        elif test -f /usr/include/mpfr.h; then echo -I/usr/include; \
        else echo ""; fi)
    MPFR_LIB := $(shell \
        if test -f /opt/homebrew/lib/libmpfr.dylib; then echo -L/opt/homebrew/lib -lmpfr; \
        elif test -f /usr/local/lib/libmpfr.so; then echo -L/usr/local/lib -lmpfr; \
        elif test -f /usr/lib/x86_64-linux-gnu/libmpfr.so; then echo -lmpfr; \
        else echo ""; fi)
    ifneq ($(MPFR_INCLUDE),)
        MPFR_AVAILABLE := 1
    endif
endif

# Set library flags based on availability
ifeq ($(GMP_AVAILABLE)$(MPFR_AVAILABLE),11)
    CFLAGS_EXTRA := $(GMP_INCLUDE) $(MPFR_INCLUDE) -DLLT_HAVE_MPFR=1
    LDFLAGS_EXTRA := $(GMP_LIB) $(MPFR_LIB)
    LIB_STATUS := Full_MPFR_GMP_support
else
    CFLAGS_EXTRA := -DLLT_HAVE_MPFR=0
    LDFLAGS_EXTRA := 
    LIB_STATUS := Fallback_mode_limited_precision
endif

# OpenMP detection for parallel processing capability
OPENMP_FLAGS := $(shell \
    if test -f /opt/homebrew/lib/libomp.dylib; then echo -I/opt/homebrew/include -L/opt/homebrew/lib -lomp; \
    elif test -f /usr/local/lib/libomp.so; then echo -I/usr/local/include -L/usr/local/lib -lomp; \
    elif command -v gcc > /dev/null && gcc -fopenmp -x c -E - < /dev/null > /dev/null 2>&1; then echo -fopenmp; \
    else echo ""; fi)

$(info Lucas-Lehmer predictor: $(LIB_STATUS))

# Compiler and tool configuration
CC := clang
CFLAGS := -std=c11 -Wall -Wextra -O3 $(CFLAGS_EXTRA) -I$(PARENT_DIR)
LDFLAGS := -lm $(LDFLAGS_EXTRA)

# Target executable and sources
TARGET := $(BIN_DIR)/lucas_lehmer_predictor
DEMO_TARGET := $(BIN_DIR)/lucas_lehmer_demo
MAIN_SOURCE := $(SRC_DIR)/lucas_lehmer_predictor.c
CONVERGENCE_SOURCE := $(SRC_DIR)/llt_convergence.c
DEMO_SOURCE := $(SRC_DIR)/lucas_lehmer_demo.c

# Object files
MAIN_OBJECT := $(BUILD_DIR)/lucas_lehmer_predictor.o
CONVERGENCE_OBJECT := $(BUILD_DIR)/llt_convergence.o
DEMO_OBJECT := $(BUILD_DIR)/lucas_lehmer_demo.o

# Platform detection
UNAME_S := $(shell uname -s 2>/dev/null || echo Unknown)
UNAME_M := $(shell uname -m 2>/dev/null || echo Unknown)

# Platform-specific configuration
ifeq ($(UNAME_S),Darwin)
    ifeq ($(UNAME_M),arm64)
        CFLAGS += -march=armv8.5-a -mcpu=apple-m1
    endif
    LDFLAGS += -Wl,-rpath,/opt/homebrew/lib
else ifeq ($(UNAME_S),Linux)
    CFLAGS += -fPIC
    ifneq ($(OPENMP_FLAGS),)
        CFLAGS += $(OPENMP_FLAGS)
        LDFLAGS += $(OPENMP_FLAGS)
    endif
endif

# Create directories
$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

$(BIN_DIR):
	@mkdir -p $(BIN_DIR)

# Default target - build working demo
all: $(DEMO_TARGET)

# Build demo object file
$(DEMO_OBJECT): $(DEMO_SOURCE) | $(BUILD_DIR)
	@echo "🔨 Compiling demo..."
	@$(CC) $(CFLAGS) -c $< -o $@

# Build the demo executable (working version)
$(DEMO_TARGET): $(DEMO_OBJECT) | $(BIN_DIR)
	@echo "🔗 Linking Lucas-Lehmer demo..."
	@$(CC) $(DEMO_OBJECT) -o $@ $(LDFLAGS)
	@echo "✅ Demo build complete: $@"

# Build the main executable
$(TARGET): $(MAIN_OBJECT) $(CONVERGENCE_OBJECT) | $(BIN_DIR)
	@echo "🔗 Linking Lucas-Lehmer predictor..."
	@$(CC) $(MAIN_OBJECT) $(CONVERGENCE_OBJECT) -o $@ $(LDFLAGS)
	@echo "✅ Build complete: $@"

# Build main object file
$(MAIN_OBJECT): $(MAIN_SOURCE) lucas_lehmer_predictor.h llt_convergence.h | $(BUILD_DIR)
	@echo "🔨 Compiling main program..."
	@$(CC) $(CFLAGS) -c $< -o $@

# Build convergence object file
$(CONVERGENCE_OBJECT): $(CONVERGENCE_SOURCE) llt_convergence.h | $(BUILD_DIR)
	@echo "🔨 Compiling convergence prediction..."
	@$(CC) $(CFLAGS) -c $< -o $@

# Build and run demonstration
test: $(DEMO_TARGET)
	@echo "🧪 Running Lucas-Lehmer convergence prediction test..."
	@echo ""
	@if [ -f "demo_lucas_lehmer.sh" ]; then \
		chmod +x demo_lucas_lehmer.sh && ./demo_lucas_lehmer.sh; \
	else \
		echo "⚡ Quick validation tests:"; \
		echo ""; \
		echo "🔬 Testing known Mersenne prime 2^13 - 1:"; \
		$(DEMO_TARGET) 13; \
		echo ""; \
		echo "🔬 Testing composite candidate 2^11 - 1:"; \
		$(DEMO_TARGET) 11; \
		echo ""; \
		echo "🔬 Running full demonstration:"; \
		$(DEMO_TARGET); \
	fi

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR) $(BIN_DIR)
	@rm -f lucas_lehmer_demo lucas_lehmer_simple simple_test
	@echo "✅ Clean complete"

# Show build configuration
info:
	@echo "📋 Lucas-Lehmer Convergence Predictor Build Configuration"
	@echo "========================================================"
	@echo "Target:           $(TARGET)"
	@echo "Compiler:         $(CC)"
	@echo "Platform:         $(UNAME_S) $(UNAME_M)"
	@echo "CFLAGS:           $(CFLAGS)"
	@echo "LDFLAGS:          $(LDFLAGS)"
	@echo "Library Support:  $(LIB_STATUS)"
	@echo "GMP Available:    $(if $(filter 1,$(GMP_AVAILABLE)),Yes,No)"
	@echo "MPFR Available:   $(if $(filter 1,$(MPFR_AVAILABLE)),Yes,No)"
	@echo "OpenMP:           $(if $(OPENMP_FLAGS),$(OPENMP_FLAGS),Not detected)"
	@echo ""
	@echo "Dependencies status:"
	@echo "  GMP:            $(if $(filter 1,$(GMP_AVAILABLE)),Found,Not found)"
	@echo "  MPFR:           $(if $(filter 1,$(MPFR_AVAILABLE)),Found,Not found)"
	@echo "  OpenMP:         $(if $(OPENMP_FLAGS),Available,Optional)"

# Show help
help:
	@echo "Lucas-Lehmer Convergence Prediction - Build System"
	@echo "=================================================="
	@echo ""
	@echo "Targets:"
	@echo "  all        - Build the Lucas-Lehmer predictor executable (default)"
	@echo "  test       - Build and run demonstration"
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
	@echo "  - OpenMP (optional, for parallel processing)"
	@echo ""
	@echo "Example usage:"
	@echo "  make test   # Build and run demonstration"
	@echo "  make info   # Show configuration"

# Debug build
debug: CFLAGS += -g -DDEBUG -O0
debug: $(TARGET)

# Phony targets
.PHONY: all test clean info help debug

# Dependencies tracking (optional)
-include $(BUILD_DIR)/*.d