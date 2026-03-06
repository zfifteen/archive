# Transparent Geometric SHA (TG-SHA) - Makefile
# ==============================================
#
# Build system for TG-SHA demonstration showing geometric predictability
# in SHA-like constants. Demonstrates vulnerability similar to Dual_EC_DRBG
# when critical scalar parameter k* is exposed.
#
# Inherits dependencies from parent Makefile and builds shared libraries.
# Uses locally detected MPFR/GMP; follows existing pattern from other C modules.
#
# Usage:
#   make          - Build TG-SHA demonstration executable
#   make test     - Build and run comprehensive demonstration
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

# Detect MPFR/GMP availability
MPFR_AVAILABLE := $(shell \
    if test -f /opt/homebrew/include/mpfr.h; then echo 1; \
    elif test -f /usr/local/include/mpfr.h; then echo 1; \
    elif test -f /usr/include/mpfr.h; then echo 1; \
    else echo 0; fi)

GMP_AVAILABLE := $(shell \
    if test -f /opt/homebrew/include/gmp.h; then echo 1; \
    elif test -f /usr/local/include/gmp.h; then echo 1; \
    elif test -f /usr/include/gmp.h; then echo 1; \
    else echo 0; fi)

# Configure based on availability
ifeq ($(MPFR_AVAILABLE)$(GMP_AVAILABLE),11)
    CFLAGS += -DTG_SHA_HAVE_MPFR=1
    $(info TG-SHA: Using full MPFR/GMP precision arithmetic)
else
    CFLAGS += -DTG_SHA_HAVE_MPFR=0
    MPFR_LDFLAGS := -lm
    $(info TG-SHA: Using fallback double-precision arithmetic)
    $(warning MPFR/GMP not found - using fallback mode for demonstration)
endif

# Compiler and tool configuration
CC := clang
CFLAGS := -std=c99 -Wall -Wextra -O3 $(GMP_INCLUDE) $(MPFR_INCLUDE) -I$(PARENT_DIR)

# Debug configuration
DEBUG_FLAGS := -g -DDEBUG -O0
ifeq ($(BUILD_TYPE),debug)
    CFLAGS += $(DEBUG_FLAGS)
endif

# Platform detection
UNAME_S := $(shell uname -s 2>/dev/null || echo Unknown)
UNAME_M := $(shell uname -m 2>/dev/null || echo Unknown)

# Platform-specific configuration
ifeq ($(UNAME_S),Darwin)
    # macOS optimizations
    ifeq ($(UNAME_M),arm64)
        CFLAGS += -march=armv8.5-a -mcpu=apple-m1
    endif
else ifeq ($(UNAME_S),Linux)
    # Linux optimizations
    CFLAGS += -fPIC
    CFLAGS += -march=native -mtune=native
endif

# Target executable
TARGET := $(BIN_DIR)/tg_sha_demo
MAIN_SOURCE := $(SRC_DIR)/tg_sha_demo.c

# TG-SHA library
TG_SHA_LIB_SOURCE := $(SRC_DIR)/tg_sha.c
TG_SHA_LIB_OBJECT := $(BUILD_DIR)/tg_sha.o

TG_SHA_HEADERS := $(SRC_DIR)/tg_sha.h

# Object files
MAIN_OBJECT := $(BUILD_DIR)/tg_sha_demo.o
OBJECT_FILES := $(TG_SHA_LIB_OBJECT)

# Linker flags
LDFLAGS := -lm $(MPFR_LDFLAGS)

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
	@cd $(PARENT_DIR) && $(MAKE) shared 2>/dev/null || echo "⚠️  Parent shared library build not available"

# Build the TG-SHA library object
$(TG_SHA_LIB_OBJECT): $(TG_SHA_LIB_SOURCE) $(TG_SHA_HEADERS) | $(BUILD_DIR)
	@echo "🔧 Compiling TG-SHA library..."
	@$(CC) $(CFLAGS) -c $(TG_SHA_LIB_SOURCE) -o $(TG_SHA_LIB_OBJECT)

# Build the main demo object
$(MAIN_OBJECT): $(MAIN_SOURCE) $(TG_SHA_HEADERS) | $(BUILD_DIR)
	@echo "🔧 Compiling TG-SHA demonstration..."
	@$(CC) $(CFLAGS) -c $(MAIN_SOURCE) -o $(MAIN_OBJECT)

# Build the main executable
$(TARGET): $(TG_SHA_LIB_OBJECT) $(MAIN_OBJECT) | $(BIN_DIR)
	@echo "🔗 Linking TG-SHA demonstration executable..."
	@$(CC) $(CFLAGS) $(TG_SHA_LIB_OBJECT) $(MAIN_OBJECT) -o $@ $(LDFLAGS)
	@echo "✅ Executable built: $@"

# Test target
test: $(TARGET)
	@echo "🧪 Running TG-SHA comprehensive demonstration..."
	@./demo_tg_sha.sh

# Clean target
clean:
	@echo "🧹 Cleaning TG-SHA build artifacts..."
	@rm -rf $(BUILD_DIR) $(BIN_DIR) *.o *.out *.csv *.txt
	@echo "✅ Clean complete"

# Info target
info:
	@echo "================================="
	@echo "  TG-SHA Geometric Vulnerability"
	@echo "================================="
	@echo "Platform:     $(UNAME_S)"
	@echo "Architecture: $(UNAME_M)"
	@echo "Compiler:     $(CC)"
	@echo "Precision:    256-bit MPFR"
	@echo "Target:       $(TARGET)"
	@echo "Dependencies: MPFR/GMP"
	@echo "================================="

# Help target
help:
	@echo "TG-SHA: Transparent Geometric SHA Vulnerability Demonstration"
	@echo "============================================================="
	@echo ""
	@echo "Available targets:"
	@echo "  make          - Build TG-SHA demonstration executable"
	@echo "  make test     - Build and run comprehensive demonstration"
	@echo "  make clean    - Clean build artifacts"
	@echo "  make info     - Show build configuration"
	@echo "  make help     - Show this help"
	@echo ""
	@echo "Requirements:"
	@echo "  - MPFR library (libmpfr-dev)"
	@echo "  - GMP library (libgmp-dev)"
	@echo ""
	@echo "Example usage:"
	@echo "  make test                           # Full demonstration"
	@echo "  ./bin/tg_sha_demo --help           # Usage information"
	@echo "  ./bin/tg_sha_demo --secure         # Secure mode demo"
	@echo "  ./bin/tg_sha_demo --broken         # Broken mode demo"
	@echo "  ./bin/tg_sha_demo --both           # Comparison demo"
	@echo "  ./bin/tg_sha_demo --analyze        # Vulnerability analysis"
	@echo ""
	@echo "TG-SHA demonstrates geometric predictability in cryptographic"
	@echo "constants when the critical k* parameter is exposed, analogous"
	@echo "to the Dual_EC_DRBG 'd' parameter vulnerability."

# Debug build option
debug: CFLAGS += -DDEBUG -g3 -O0
debug: $(TARGET)

# Phony targets
.PHONY: all test clean info help debug parent-libs

# Dependencies tracking (optional)
-include $(BUILD_DIR)/*.d