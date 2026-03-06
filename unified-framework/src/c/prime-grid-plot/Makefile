# Prime Grid Plot - C Implementation Makefile
# ==========================================
# 
# Build system for Prime Grid Plot C implementation using GMP.
# Inherits dependencies from parent makefile without adding new ones.
#
# Usage:
#   make          - Build prime grid plot executable
#   make test     - Build and run demonstration
#   make clean    - Clean build artifacts
#   make help     - Show this help
#
# @file Makefile
# @version 2.0

# Ensure default goal is 'all' regardless of rule order
.DEFAULT_GOAL := all

# Directories
SRC_DIR := .
PARENT_DIR := ..
BUILD_DIR := build
BIN_DIR := bin

# Detect platform for shared library extension
UNAME_S := $(shell uname -s 2>/dev/null || echo Windows)
ifeq ($(UNAME_S),Darwin)
    SHARED_LIB_EXT := .dylib
else ifeq ($(UNAME_S),Linux)
    SHARED_LIB_EXT := .so
endif

# Parent headers (always needed for compilation dependencies)
Z5D_HEADERS := $(PARENT_DIR)/z5d_predictor.h $(PARENT_DIR)/z5d_phase2.h $(PARENT_DIR)/z_framework_params.h

# Use simplified dependency detection to avoid parent make output issues
GMP_INCLUDE := $(shell \
    if test -f /opt/homebrew/include/gmp.h; then echo -I/opt/homebrew/include; \
    elif test -f /usr/local/include/gmp.h; then echo -I/usr/local/include; \
    elif test -f /usr/include/gmp.h; then echo -I/usr/include; \
    elif test -f /usr/include/x86_64-linux-gnu/gmp.h; then echo -I/usr/include/x86_64-linux-gnu; \
    else echo ""; fi)

GMP_LDFLAGS := $(shell \
    if test -f /opt/homebrew/lib/libgmp.dylib; then echo -L/opt/homebrew/lib; \
    elif test -f /usr/local/lib/libgmp.so; then echo -L/usr/local/lib; \
    elif test -f /usr/lib/x86_64-linux-gnu/libgmp.so; then echo -L/usr/lib/x86_64-linux-gnu; \
    else echo ""; fi)

# Compiler and flags
CC := clang
CFLAGS := -std=c99 -Wall -Wextra -O2 $(GMP_INCLUDE) -I$(PARENT_DIR)
LDFLAGS := $(GMP_LDFLAGS) -lgmp -lm

# Source and object files
MAIN_SOURCE := prime_grid_plot.c
MAIN_OBJECT := $(BUILD_DIR)/prime_grid_plot.o
TARGET := $(BIN_DIR)/prime_grid_plot

# Create directories
$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

$(BIN_DIR):
	@mkdir -p $(BIN_DIR)

# Default target
all: $(TARGET)

# Build the main executable
$(TARGET): $(MAIN_OBJECT) | $(BIN_DIR)
	@echo "Building prime grid plot executable: $@"
	$(CC) $(MAIN_OBJECT) -o $@ $(LDFLAGS)

# Compile main source
$(MAIN_OBJECT): $(MAIN_SOURCE) | $(BUILD_DIR)
	@echo "Compiling: $<"
	$(CC) $(CFLAGS) -c $< -o $@

# Test target - build and run demonstration
test: $(TARGET)
	@echo "Running prime grid plot demonstration..."
	@echo ""
	@echo "Test 1: Small scale demonstration (10^3)"
	./$(TARGET) --scale "10^3" --x-start 1 --x-end 2 --y-start 0 --y-end 100 --out-csv test_small.csv --verbose
	@echo ""
	@echo "Test 2: Medium scale with probes (10^6)"
	./$(TARGET) --scale "10^6" --x-start 1 --x-end 3 --y-start 0 --y-end 10000 --probes 50 --seed 42 --out-csv test_medium.csv --verbose
	@echo ""
	@echo "Generated CSV files:"
	@ls -la test_*.csv 2>/dev/null || echo "No CSV files found"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR) $(BIN_DIR)
	@rm -f test_*.csv

# Help target
help:
	@echo "Prime Grid Plot - C Implementation Build System"
	@echo "=============================================="
	@echo ""
	@echo "Available targets:"
	@echo "  all       - Build prime grid plot executable (default)"
	@echo "  test      - Build and run demonstration"
	@echo "  clean     - Remove build artifacts"
	@echo "  help      - Show this help message"
	@echo ""
	@echo "Dependencies: GMP library"
	@echo "  Install libgmp-dev (Debian/Ubuntu) or gmp (Homebrew/macOS)"
	@echo ""
	@echo "Usage examples:"
	@echo "  ./$(BIN_DIR)/prime_grid_plot --scale \"10^6\" --x-start 1 --x-end 5 --y-start 0 --y-end 1000 --out-csv output.csv"
	@echo "  ./$(BIN_DIR)/prime_grid_plot --scale \"10^9\" --x-start 1 --x-end 3 --y-start 0 --y-end 1000000 --probes 1000"

# Phony targets
.PHONY: all test clean help