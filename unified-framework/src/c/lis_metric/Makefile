# LIS Metric CLI - Makefile
# =========================
#
# Build system for LIS-Metric command-line interface
# Range-based filtering performance measurement with MPFR/GMP
#
# Usage:
#   make          - Build lis_metric executable
#   make clean    - Clean build artifacts
#   make help     - Show this help

# Directories
SRC_DIR := .
PARENT_DIR := ..
BUILD_DIR := build
BIN_DIR := bin

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
    if test -f /opt/homebrew/lib/libmpfr.dylib; then echo -L/opt/homebrew/lib -lmpfr -lgmp; \
    elif test -f /usr/local/lib/libmpfr.a; then echo -L/usr/local/lib -lmpfr -lgmp; \
    elif test -f /usr/lib/libmpfr.so; then echo -L/usr/lib -lmpfr -lgmp; \
    else echo -lmpfr -lgmp; fi)

$(info LIS-Metric CLI using detected MPFR/GMP dependencies)

# Compiler and tool configuration
CC := clang
CFLAGS := -std=c99 -Wall -Wextra -O3 $(GMP_INCLUDE) $(MPFR_INCLUDE) -I$(PARENT_DIR)
LDFLAGS := -lm $(MPFR_LDFLAGS)

# Target executable
TARGET := $(BIN_DIR)/lis_metric
SOURCE := $(SRC_DIR)/lis_metric.c

# Object files
MAIN_OBJECT := $(BUILD_DIR)/lis_metric.o

# Platform detection
UNAME_S := $(shell uname -s 2>/dev/null || echo Unknown)
UNAME_M := $(shell uname -m 2>/dev/null || echo Unknown)

# Platform-specific configuration
ifeq ($(UNAME_S),Darwin)
    ifeq ($(UNAME_M),arm64)
        CFLAGS += -march=armv8.5-a -mcpu=apple-m1
    endif
else ifeq ($(UNAME_S),Linux)
    CFLAGS += -fPIC
endif

# Create directories
$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

$(BIN_DIR):
	@mkdir -p $(BIN_DIR)

# Default target
all: $(TARGET)

# Build the main executable
$(TARGET): $(MAIN_OBJECT) | $(BIN_DIR)
	@echo "Linking LIS-Metric CLI: $@"
	@$(CC) $(MAIN_OBJECT) $(LDFLAGS) -o $@

# Compile main source
$(MAIN_OBJECT): $(SOURCE) | $(BUILD_DIR)
	@echo "Compiling: $<"
	@$(CC) $(CFLAGS) -c $< -o $@

# Build and run test
test: $(TARGET)
	@echo "Testing LIS-Metric CLI..."
	@echo "Test 1: Small range (3-10000)"
	@./$(TARGET) 3 10000
	@echo "Test 2: Medium range (100001-110000)"
	@./$(TARGET) 100001 110000
	@echo "Test 3: Help message"
	@./$(TARGET) --help

# Debug build
debug: CFLAGS += -g -DDEBUG -O0
debug: $(TARGET)

# Clean build artifacts
clean:
	@echo "Cleaning LIS-Metric CLI build artifacts..."
	@rm -rf $(BUILD_DIR) $(BIN_DIR)

# Show build configuration
info:
	@echo "LIS-Metric CLI Build Configuration"
	@echo "=================================="
	@echo "Platform:      $(UNAME_S)"
	@echo "Architecture:  $(UNAME_M)"
	@echo "Compiler:      $(CC)"
	@echo "CFLAGS:        $(CFLAGS)"
	@echo "LDFLAGS:       $(LDFLAGS)"
	@echo "Target:        $(TARGET)"
	@echo "Dependencies:  MPFR/GMP (detected locally)"

# Help target
help:
	@echo "LIS-Metric CLI - Build System"
	@echo "============================="
	@echo ""
	@echo "Available targets:"
	@echo "  all        - Build LIS-Metric CLI (default)"
	@echo "  test       - Build and run test cases"
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
	@echo ""
	@echo "Example usage:"
	@echo "  make test   # Build and run test cases"

# Phony targets
.PHONY: all test debug clean info help

# Dependencies tracking (optional)
-include $(BUILD_DIR)/*.d