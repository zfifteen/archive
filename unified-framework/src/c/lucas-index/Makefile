# Lucas Index System (LIS) - Makefile
# =====================================
# 
# Build system for Lucas Index System (LIS) demo (Lucas filter + MR).
# Uses locally detected MPFR/GMP/OpenMP; no parent project linkage required.
#
# Usage:
#   make          - Build Lucas-index demonstration program
#   make test     - Build and run the demonstration
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

######## Parent library detection ########
# Prefer linking against the parent shared library when available.
PARENT_SHARED_LIB := $(PARENT_DIR)/lib/libz5d.dylib  # unused, retained for compatibility

# Fallback for Linux systems
ifeq ($(shell uname -s),Linux)
PARENT_SHARED_LIB := $(PARENT_DIR)/lib/libz5d.so
endif

# Detect presence of parent shared library
ifneq ("$(wildcard $(PARENT_SHARED_LIB))","")
    HAVE_PARENT_LIB := 1
else
    HAVE_PARENT_LIB := 0
endif

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
    if test -f /opt/homebrew/lib/libmpfr.dylib; then echo -L/opt/homebrew/lib -lmpfr -lgmp; \
    elif test -f /usr/local/lib/libmpfr.a; then echo -L/usr/local/lib -lmpfr -lgmp; \
    elif test -f /usr/lib/libmpfr.so; then echo -L/usr/lib -lmpfr -lgmp; \
    else echo -lmpfr -lgmp; fi)

$(info LIS demo using detected MPFR/GMP/OpenMP dependencies)

# Compiler and tool configuration
CC := clang
CFLAGS := -std=c11 -Wall -Wextra -O3 $(GMP_INCLUDE) $(MPFR_INCLUDE) -I$(PARENT_DIR)
LDFLAGS := -lm $(MPFR_LDFLAGS)

# Parent lib directory and rpath for runtime
PARENT_LIB_DIR := $(PARENT_DIR)/lib
UNAME_S := $(shell uname -s 2>/dev/null || echo Unknown)
ifeq ($(UNAME_S),Darwin)
    RPATH_FLAG := -Wl,-rpath,$(PARENT_LIB_DIR)
else ifeq ($(UNAME_S),Linux)
    RPATH_FLAG := -Wl,-rpath,$(PARENT_LIB_DIR)
endif

# Target executable
TARGET := $(BIN_DIR)/lucas_demo
SOURCE := $(SRC_DIR)/lucas_demo.c

# Lucas-index library
LUCAS_LIB_SOURCE := $(SRC_DIR)/lucas_index.c
LUCAS_LIB_OBJECT := $(BUILD_DIR)/lucas_index.o

LUCAS_HEADERS := $(SRC_DIR)/lucas_index.h

# Object files
MAIN_OBJECT := $(BUILD_DIR)/lucas_demo.o

# Platform detection
UNAME_M := $(shell uname -m 2>/dev/null || echo Unknown)

# Platform-specific configuration
ifeq ($(UNAME_S),Darwin)
    # macOS optimizations - only apply ARM flags on ARM systems
    ifeq ($(UNAME_M),arm64)
        CFLAGS += -march=armv8.5-a -mcpu=apple-m1
    endif
    SHARED_LIB_EXT := .dylib
    SHARED_LDFLAGS := -dynamiclib
else ifeq ($(UNAME_S),Linux)
    SHARED_LIB_EXT := .so
    SHARED_LDFLAGS := -shared -fPIC
    CFLAGS += -fPIC
endif

# Parent shared library build removed: LIS demo is self-contained

# Create directories
$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

$(BIN_DIR):
	@mkdir -p $(BIN_DIR)

# Default target
all: $(TARGET)

# Parent headers (always needed for compilation dependencies)
Z5D_HEADERS := $(PARENT_DIR)/z5d_predictor.h $(PARENT_DIR)/z5d_phase2.h $(PARENT_DIR)/z_framework_params.h

## LIS demo is self-contained: no parent Z5D objects are compiled or linked

# Build the main executable (choose link strategy)
$(TARGET): $(MAIN_OBJECT) $(LUCAS_LIB_OBJECT) | $(BIN_DIR)
	@echo "Linking Lucas-index demonstration (LIS-only): $@"
	@$(CC) $(MAIN_OBJECT) $(LUCAS_LIB_OBJECT) $(LDFLAGS) -o $@

# Compile main source
$(MAIN_OBJECT): $(SOURCE) $(LUCAS_HEADERS) | $(BUILD_DIR)
	@echo "Compiling: $<"
	@$(CC) $(CFLAGS) -c $< -o $@

# Compile Lucas-index library
$(LUCAS_LIB_OBJECT): $(LUCAS_LIB_SOURCE) $(LUCAS_HEADERS) | $(BUILD_DIR)
	@echo "Compiling: $<"
	@$(CC) $(CFLAGS) -c $< -o $@

## No parent objects needed

# Build and run test
test: $(TARGET)
	@echo "Running Lucas-index demonstration..."
	@./$(TARGET)

# Debug build
debug: CFLAGS += -g -DDEBUG -O0
debug: $(TARGET)

# Build parent shared library target
# Clean build artifacts
clean:
	@echo "Cleaning Lucas-index build artifacts..."
	@rm -rf $(BUILD_DIR) $(BIN_DIR)

# Show build configuration

info:
	@echo "LIS Build Configuration"
	@echo "======================="
	@echo "Platform:      $(UNAME_S)"
	@echo "Architecture:  $(UNAME_M)"
	@echo "Compiler:      $(CC)"
	@echo "CFLAGS:        $(CFLAGS)"
	@echo "LDFLAGS:       $(LDFLAGS)"
	@echo "Target:        $(TARGET)"
	@echo "Deps:          MPFR/GMP (OpenMP optional)"

# Help target
help:
	@echo "Lucas Index System (LIS) - Build System"
	@echo "========================================"
	@echo ""
	@echo "Available targets:"
	@echo "  all        - Build LIS demo (default)"
	@echo "  test       - Build and run the demo"
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
	@echo "  - OpenMP (libomp-dev, optional)"
	@echo ""
	@echo "Example usage:"
	@echo "  make test   # Build and run LIS demo"

# Phony targets
.PHONY: all test debug clean info help

# Dependencies tracking (optional)
-include $(BUILD_DIR)/*.d
