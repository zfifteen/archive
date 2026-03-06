# Z5D nth-Prime Predictor - Makefile
# ===================================
#
# Build system for Z5D nth-prime predictor using C/MPFR.
# Inherits dependencies from parent Makefile without introducing new dependencies.
# Uses existing GMP/MPFR detection mechanism.
#
# Usage:
#   make          - Build all executables and library
#   make test     - Build and run tests
#   make bench    - Build and run benchmark
#   make demo     - Build and run demonstration
#   make clean    - Clean build artifacts
#   make help     - Show this help
#
# @file Makefile
# @version 1.0

# Ensure default goal
.DEFAULT_GOAL := all

# Directories
SRC_DIR := src
INCLUDE_DIR := include
TEST_DIR := tests
BUILD_DIR := build
BIN_DIR := bin
PARENT_DIR := ..

# Compiler
CC := clang

# Platform detection (for compatibility)
UNAME_S := $(shell uname -s 2>/dev/null || echo Windows)

# GMP/MPFR detection - inherit from parent's sophisticated mechanism
PKG_CONFIG_EXISTS := $(shell command -v pkg-config >/dev/null 2>&1 && echo 1 || echo 0)

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

# Fallback manual detection
ifeq ($(GMP_AVAILABLE),0)
    GMP_INCLUDE := $(shell \
        if test -f /opt/homebrew/include/gmp.h; then echo -I/opt/homebrew/include; \
        elif test -f /usr/local/include/gmp.h; then echo -I/usr/local/include; \
        elif test -f /usr/include/x86_64-linux-gnu/gmp.h; then echo -I/usr/include/x86_64-linux-gnu; \
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

# Check if dependencies are satisfied
ifeq ($(GMP_AVAILABLE)$(MPFR_AVAILABLE),11)
    CFLAGS := -O3 -march=native -Wall -Wextra -I$(INCLUDE_DIR) $(GMP_INCLUDE) $(MPFR_INCLUDE)
    LDFLAGS := $(GMP_LIB) $(MPFR_LIB) -lm
    LIB_STATUS := Full_MPFR_GMP_support
else
    $(error GMP/MPFR not found. Please install libgmp-dev and libmpfr-dev)
endif

# Debug flags
DEBUG_CFLAGS := -O0 -g3 -fno-omit-frame-pointer -DDEBUG

# Source files
LIB_SOURCES := $(SRC_DIR)/z5d_predictor.c $(SRC_DIR)/z5d_math.c
LIB_OBJECTS := $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.o,$(LIB_SOURCES))

CLI_SOURCE := $(SRC_DIR)/z5d_cli.c
CLI_OBJECT := $(BUILD_DIR)/z5d_cli.o

BENCH_SOURCE := $(SRC_DIR)/z5d_bench.c
BENCH_OBJECT := $(BUILD_DIR)/z5d_bench.o

TEST_KNOWN_SOURCE := $(TEST_DIR)/test_known.c
TEST_KNOWN_OBJECT := $(BUILD_DIR)/test_known.o

TEST_MEDIUM_SOURCE := $(TEST_DIR)/test_medium_scale.c
TEST_MEDIUM_OBJECT := $(BUILD_DIR)/test_medium_scale.o

# Output files
STATIC_LIB := $(BUILD_DIR)/libz5d_predictor.a
CLI_EXECUTABLE := $(BIN_DIR)/z5d_cli
BENCH_EXECUTABLE := $(BIN_DIR)/z5d_bench
TEST_KNOWN_EXECUTABLE := $(BIN_DIR)/test_known
TEST_MEDIUM_EXECUTABLE := $(BIN_DIR)/test_medium_scale

# Info message
$(info Z5D nth-prime predictor: $(LIB_STATUS))

# Create directories
$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

$(BIN_DIR):
	@mkdir -p $(BIN_DIR)

# Build library objects
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c | $(BUILD_DIR)
	@echo "🔧 Compiling $<..."
	@$(CC) $(CFLAGS) -c $< -o $@

# Build static library
$(STATIC_LIB): $(LIB_OBJECTS) | $(BUILD_DIR)
	@echo "📦 Creating static library..."
	@ar rcs $@ $^

# Build CLI
$(CLI_OBJECT): $(CLI_SOURCE) | $(BUILD_DIR)
	@echo "🔧 Compiling CLI..."
	@$(CC) $(CFLAGS) -c $< -o $@

$(CLI_EXECUTABLE): $(CLI_OBJECT) $(STATIC_LIB) | $(BIN_DIR)
	@echo "🔗 Linking CLI executable..."
	@$(CC) $(CLI_OBJECT) $(STATIC_LIB) $(LDFLAGS) -o $@

# Build benchmark
$(BENCH_OBJECT): $(BENCH_SOURCE) | $(BUILD_DIR)
	@echo "🔧 Compiling benchmark..."
	@$(CC) $(CFLAGS) -c $< -o $@

$(BENCH_EXECUTABLE): $(BENCH_OBJECT) $(STATIC_LIB) | $(BIN_DIR)
	@echo "🔗 Linking benchmark executable..."
	@$(CC) $(BENCH_OBJECT) $(STATIC_LIB) $(LDFLAGS) -o $@

# Build test executables
$(TEST_KNOWN_OBJECT): $(TEST_KNOWN_SOURCE) | $(BUILD_DIR)
	@echo "🔧 Compiling test_known..."
	@$(CC) $(CFLAGS) -c $< -o $@

$(TEST_KNOWN_EXECUTABLE): $(TEST_KNOWN_OBJECT) $(STATIC_LIB) | $(BIN_DIR)
	@echo "🔗 Linking test_known executable..."
	@$(CC) $(TEST_KNOWN_OBJECT) $(STATIC_LIB) $(LDFLAGS) -o $@

$(TEST_MEDIUM_OBJECT): $(TEST_MEDIUM_SOURCE) | $(BUILD_DIR)
	@echo "🔧 Compiling test_medium_scale..."
	@$(CC) $(CFLAGS) -c $< -o $@

$(TEST_MEDIUM_EXECUTABLE): $(TEST_MEDIUM_OBJECT) $(STATIC_LIB) | $(BIN_DIR)
	@echo "🔗 Linking test_medium_scale executable..."
	@$(CC) $(TEST_MEDIUM_OBJECT) $(STATIC_LIB) $(LDFLAGS) -o $@

# Targets
.PHONY: all lib cli bench test-executables clean help test demo info shared

all: lib cli bench test-executables
	@echo "✅ Build complete!"

lib: $(STATIC_LIB)

cli: $(CLI_EXECUTABLE)

bench: $(BENCH_EXECUTABLE)

test-executables: $(TEST_KNOWN_EXECUTABLE) $(TEST_MEDIUM_EXECUTABLE)

# Run tests
test: test-executables
	@echo ""
	@echo "🧪 Running known values test..."
	@$(TEST_KNOWN_EXECUTABLE)
	@echo ""
	@echo "🧪 Running medium scale test..."
	@$(TEST_MEDIUM_EXECUTABLE)

# Run benchmark
benchmark: $(BENCH_EXECUTABLE)
	@echo ""
	@echo "⚡ Running benchmark..."
	@$(BENCH_EXECUTABLE)

# Run demo
demo: $(CLI_EXECUTABLE)
	@echo ""
	@echo "🚀 Running demonstration..."
	@./scripts/demo.sh

# Info
info:
	@echo "Z5D nth-Prime Predictor Build Information"
	@echo "========================================="
	@echo "Status:         $(LIB_STATUS)"
	@echo "GMP Available:  $(GMP_AVAILABLE)"
	@echo "MPFR Available: $(MPFR_AVAILABLE)"
	@echo "GMP Include:    $(GMP_INCLUDE)"
	@echo "GMP Lib:        $(GMP_LIB)"
	@echo "MPFR Include:   $(MPFR_INCLUDE)"
	@echo "MPFR Lib:       $(MPFR_LIB)"
	@echo "CFLAGS:         $(CFLAGS)"
	@echo "LDFLAGS:        $(LDFLAGS)"

# Check for parent shared library (invoke parent make)
shared:
	@echo "🔍 Checking parent shared library..."
	@if [ -f "$(PARENT_DIR)/Makefile" ]; then \
		echo "📦 Building parent shared library..."; \
		cd $(PARENT_DIR) && $(MAKE) shared 2>/dev/null || echo "⚠️  Parent shared library build not available"; \
	else \
		echo "⚠️  Parent Makefile not found"; \
	fi

# Clean
clean:
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR) $(BIN_DIR)

# Help
help:
	@echo "Z5D nth-Prime Predictor - Build System"
	@echo "======================================"
	@echo ""
	@echo "Available targets:"
	@echo "  all           - Build library, CLI, benchmark, and tests (default)"
	@echo "  lib           - Build static library only"
	@echo "  cli           - Build CLI tool"
	@echo "  bench         - Build benchmark tool"
	@echo "  test          - Build and run all tests"
	@echo "  benchmark     - Run performance benchmark"
	@echo "  demo          - Run demonstration script"
	@echo "  clean         - Remove build artifacts"
	@echo "  info          - Show build configuration"
	@echo "  shared        - Invoke parent to build shared libraries"
	@echo "  help          - Show this help"
	@echo ""
	@echo "Requirements:"
	@echo "  - GMP library (libgmp-dev)"
	@echo "  - MPFR library (libmpfr-dev)"
	@echo ""
	@echo "Example usage:"
	@echo "  make test     # Build and run tests"
	@echo "  make cli      # Build CLI tool"
	@echo "  ./bin/z5d_cli 1000000  # Predict 1,000,000th prime"

# Dependencies tracking
-include $(BUILD_DIR)/*.d
