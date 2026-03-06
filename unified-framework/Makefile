# Geodesic Z5D Search - Apple M1 Max Optimized Makefile
# =====================================================
#
# Seamless build system for geodesic_z5d_search.c with MPFR precision fix
# Optimized for Apple M1 Max (10-core, 32GB RAM) - Single core version
#
# Dependencies automatically handled via Homebrew
# Features: Auto-detection, M1 optimizations, dependency management
#
# Usage:
#   make          - Build optimized geodesic_z5d_search executable  
#   make test     - Build and run precision fix tests
#   make deps     - Install dependencies via Homebrew
#   make clean    - Clean build artifacts
#   make bench    - Run performance benchmark
#   make help     - Show help
#
# @author: Unified Framework Team  
# @target: Apple M1 Max (single core optimized)

# === CONFIGURATION ===
PROGRAM_NAME := geodesic_z5d_search
SOURCE_FILE := src/c/geodesic_z5d_search.c
BUILD_DIR := build
BIN_DIR := bin
TEST_DIR := tests

# === COMPILER DETECTION ===
# Prefer clang on macOS for better M1 support
CC := $(shell command -v clang >/dev/null 2>&1 && echo clang || echo gcc)

# === APPLE M1 MAX OPTIMIZATION ===
# Detect Apple Silicon and set M1-specific optimizations
UNAME_M := $(shell uname -m)
UNAME_S := $(shell uname -s)

# M1 Max specific flags
ifeq ($(UNAME_S),Darwin)
    ifeq ($(UNAME_M),arm64)
        OPT_FLAGS := -O3 -funroll-loops
        MEMORY_FLAGS := -DMEMORY_32GB=1
        AMX_FLAGS := -DZ5D_USE_AMX=1 -DZ5D_AMX_AVAILABLE=1
        PLATFORM := "Apple M1 Max"
        
        # Homebrew paths for M1 Mac
        HOMEBREW_PREFIX := /opt/homebrew
        INCLUDE_PATHS := -I$(HOMEBREW_PREFIX)/include
        LIBRARY_PATHS := -L$(HOMEBREW_PREFIX)/lib
    else
        # Intel Mac fallback
        ARCH_FLAGS := -march=native
        OPT_FLAGS := -O3
        PLATFORM := "Intel Mac"
        HOMEBREW_PREFIX := /usr/local
        INCLUDE_PATHS := -I$(HOMEBREW_PREFIX)/include
        LIBRARY_PATHS := -L$(HOMEBREW_PREFIX)/lib
    endif
else
    # Linux/other platforms
    ARCH_FLAGS := -march=native
    OPT_FLAGS := -O3
    PLATFORM := "Generic"
    INCLUDE_PATHS := 
    LIBRARY_PATHS := 
endif

# === COMPILER FLAGS ===
# Base flags
CFLAGS := -std=c99 -Wall -Wextra -Wpedantic -D_POSIX_C_SOURCE=200809L
CFLAGS += $(ARCH_FLAGS) $(OPT_FLAGS) $(MEMORY_FLAGS)
CFLAGS += $(INCLUDE_PATHS)
CFLAGS += -DMPFR_PRECISION=256
CFLAGS += -DMP_DPS=256

# AMX flags for Apple M1 Max
ifdef AMX_FLAGS
CFLAGS += $(AMX_FLAGS)
endif

# Test-specific flags (less strict for test files)
TEST_CFLAGS := -std=c99 -Wall -D_POSIX_C_SOURCE=200809L
TEST_CFLAGS += $(ARCH_FLAGS) -O2 $(INCLUDE_PATHS)

# Single-core focus (despite OpenMP availability)
CFLAGS += -DSINGLE_CORE_OPTIMIZED=1

# Debug flags (when BUILD_TYPE=debug)
DEBUG_FLAGS := -g -O0 -DDEBUG -fsanitize=address

# === LIBRARIES ===
# Required libraries for MPFR precision fix
LIBS := -lmpfr -lgmp -lm
LDFLAGS := $(LIBRARY_PATHS) $(LIBS)

# === SOURCE FILES ===
# Core Z5D library sources including AMX optimization
LIB_SOURCES := src/c/z5d_predictor.c src/c/z5d_phase2.c src/c/z5d_fft_zeta.c src/c/z5d_amx.c

# OpenMP (available but configured for single-thread by default)
#OPENMP_FLAGS := -fopenmp
LDFLAGS += $(OPENMP_FLAGS)

# === EXECUTABLES ===
EXECUTABLE := $(BIN_DIR)/$(PROGRAM_NAME)
RELEASE_EXECUTABLE := $(EXECUTABLE)
TEST_EXECUTABLE := $(BIN_DIR)/test_z5d
BENCHMARK_EXECUTABLE := $(BIN_DIR)/benchmark_z5d
PRECISION_TEST_EXECUTABLE := $(BIN_DIR)/test_precision_fix
PROBE_EXECUTABLE := $(BIN_DIR)/probe

# === BUILD TYPE ===
BUILD_TYPE ?= release
ifeq ($(BUILD_TYPE),debug)
    CFLAGS += $(DEBUG_FLAGS)
endif

# === PHONY TARGETS ===
.PHONY: all clean test test-z5d bench bench-z5d probe deps check-deps help info semiprime-nav clean-semiprime-nav
.DEFAULT_GOAL := all

# === MAIN TARGETS ===

all: info check-deps $(EXECUTABLE)
	@echo "✅ Build complete! Executable: $(EXECUTABLE)"
	@echo "🎯 Platform: $(PLATFORM)"
	@echo "🚀 Ready for high-precision Z5D search"

# Create directories
$(BUILD_DIR) $(BIN_DIR):
	@mkdir -p $@

# Build main executable
$(EXECUTABLE): $(SOURCE_FILE) | $(BIN_DIR)
	@echo "🔨 Building $(PROGRAM_NAME) with M1 Max optimizations..."
	@$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS)
	@echo "✅ Executable built: $@"

# Build Z5D test executable
$(TEST_EXECUTABLE): src/c/test_z5d.c src/c/z5d_predictor.c | $(BIN_DIR)
	@echo "🔨 Building Z5D test executable..."
	@$(CC) $(CFLAGS) -Isrc/c $^ -o $@ $(LDFLAGS)
	@echo "✅ Test executable built: $@"

# Build benchmark executable (using AMX-enhanced benchmark_z5d.c)
$(BENCHMARK_EXECUTABLE): src/c/benchmark_z5d.c src/c/z5d_phase2.c src/c/z5d_predictor.c | $(BIN_DIR)
	@echo "🔨 Building Z5D benchmark executable with AMX support..."
	@$(CC) $(CFLAGS) -Isrc/c -DZ5D_USE_OMP=0 $^ -o $@ -lm
	@echo "✅ AMX-enhanced benchmark executable built: $@"

# Build inverse Mersenne probe executable
$(PROBE_EXECUTABLE): tools/inverse_mersenne_probe.c src/c/z5d_predictor.c | $(BIN_DIR)
	@echo "🔨 Building inverse Mersenne probe executable..."
	@$(CC) $(CFLAGS) -Isrc/c $^ -o $@ $(LDFLAGS)
	@echo "✅ Probe executable built: $@"

# === TESTING ===

test: $(PRECISION_TEST_EXECUTABLE) $(TEST_EXECUTABLE) $(EXECUTABLE)
	@echo "🧪 Running precision fix tests..."
	@./$(PRECISION_TEST_EXECUTABLE)
	@echo "🧪 Running Z5D tests..."
	@./$(TEST_EXECUTABLE)
	@echo "🧪 Running comprehensive tests..."
	@bash comprehensive_test.sh

test-z5d: $(TEST_EXECUTABLE)
	@echo "🧪 Running Z5D-specific tests..."
	@./$(TEST_EXECUTABLE)

$(PRECISION_TEST_EXECUTABLE): test_precision_fix.c | $(BIN_DIR)
	@echo "🔨 Building precision test executable..."
	@$(CC) $(TEST_CFLAGS) $< -o $@

# === DEPENDENCY MANAGEMENT ===

deps: check-platform install-deps
	@echo "✅ Dependencies installed and optimized for M1 Max"

check-platform:
ifeq ($(UNAME_S),Darwin)
	@echo "🍎 Detected macOS - using Homebrew for dependencies"
	@echo "🔍 Architecture: $(UNAME_M)"
    ifeq ($(UNAME_M),arm64)
	@echo "🚀 Apple M1 Max detected - optimized build configuration enabled"
    endif
else
	@echo "🐧 Detected non-macOS - please install dependencies manually:"
	@echo "   Ubuntu/Debian: sudo apt-get install libmpfr-dev libgmp-dev libomp-dev"
	@echo "   CentOS/RHEL:   sudo yum install mpfr-devel gmp-devel libomp-devel"
endif

install-deps:
ifeq ($(UNAME_S),Darwin)
	@echo "📦 Installing dependencies via Homebrew..."
	@command -v brew >/dev/null 2>&1 || (echo "❌ Homebrew not found! Install from https://brew.sh" && exit 1)
	@echo "🔧 Installing MPFR (Multi-Precision Floating-Point)..."
	@brew list mpfr >/dev/null 2>&1 || brew install mpfr
	@echo "🔧 Installing GMP (GNU Multiple Precision)..."
	@brew list gmp >/dev/null 2>&1 || brew install gmp
	@echo "🔧 Installing OpenMP..."
	@brew list libomp >/dev/null 2>&1 || brew install libomp
    ifeq ($(UNAME_M),arm64)
	@echo "🎯 M1 Max: Configuring optimized library paths..."
	@echo "   MPFR: $(HOMEBREW_PREFIX)/lib/libmpfr.dylib"
	@echo "   GMP:  $(HOMEBREW_PREFIX)/lib/libgmp.dylib"
	@echo "   OMP:  $(HOMEBREW_PREFIX)/lib/libomp.dylib"
    endif
	@echo "✅ Dependencies installed"
else
	@echo "⚠️  Please install dependencies manually for your platform"
endif

check-deps:
	@echo "🔍 Checking dependencies..."
ifeq ($(UNAME_S),Darwin)
	@brew list mpfr >/dev/null 2>&1 || (echo "❌ mpfr not found. Run 'make deps'" && exit 1)
	@brew list gmp >/dev/null 2>&1 || (echo "❌ gmp not found. Run 'make deps'" && exit 1)
	@brew list libomp >/dev/null 2>&1 || (echo "❌ libomp not found. Run 'make deps'" && exit 1)
    ifeq ($(UNAME_M),arm64)
	@echo "✅ M1 Max dependencies verified"
    else
	@echo "✅ Intel Mac dependencies verified"
    endif
else
	@echo "⚠️  Dependency check skipped on non-macOS platform"
endif

# === BENCHMARKING ===

bench: $(EXECUTABLE)
	@echo "⚡ Running M1 Max performance benchmark..."
	@echo "📊 Testing extreme k values (k ≈ 10^16)..."
	@time ./$(EXECUTABLE) 37124508045065437 5
	@echo "📊 Benchmark complete"

bench-z5d: $(BENCHMARK_EXECUTABLE)
	@echo "⚡ Running Z5D performance benchmark..."
	@time ./$(BENCHMARK_EXECUTABLE)

# Build probe executable
probe: $(PROBE_EXECUTABLE)
	@echo "✅ Inverse Mersenne probe built: $(PROBE_EXECUTABLE)"

# === UTILITIES ===

clean:
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR) $(BIN_DIR)
	@echo "✅ Clean complete"

info:
	@echo "════════════════════════════════════════════════"
	@echo "  Geodesic Z5D Search - Apple M1 Max Build"
	@echo "════════════════════════════════════════════════"
	@echo "Platform:     $(PLATFORM)"
	@echo "Architecture: $(UNAME_M)"
	@echo "Compiler:     $(CC)"
	@echo "Build Type:   $(BUILD_TYPE)"
	@echo "Precision:    256-bit MPFR"
	@echo "Target CPU:   Single core optimized"
	@echo "Source:       $(SOURCE_FILE)"
	@echo "Output:       $(EXECUTABLE)"
	@echo "════════════════════════════════════════════════"

help:
	@echo "Geodesic Z5D Search - Apple M1 Max Optimized Build System"
	@echo "========================================================="
	@echo ""
	@echo "🎯 Optimized for Apple M1 Max (10-core, 32GB RAM)"
	@echo "🔧 Single-core version with 256-bit MPFR precision"
	@echo ""
	@echo "Available targets:"
	@echo "  make          - Build optimized executable (default)"
	@echo "  make test     - Build and run all tests"
	@echo "  make test-z5d - Build and run Z5D-specific tests"
	@echo "  make test-amx - Build and run AMX functionality tests"
	@echo "  make test-amx-integration - Build and run comprehensive AMX integration tests"
	@echo "  make probe    - Build inverse Mersenne probe for RSA factorization"
	@echo "  make deps     - Install dependencies via Homebrew (macOS)"
	@echo "  make bench    - Run performance benchmark"
	@echo "  make bench-z5d - Run Z5D-specific benchmark"
	@echo "  make bench-amx - Run AMX performance benchmark"
	@echo "  make amx-build - Build with AMX optimizations enabled"
	@echo "  make clean    - Remove build artifacts"
	@echo "  make info     - Show build configuration"
	@echo "  make help     - Show this help"
	@echo ""
	@echo "Executables built:"
	@echo "  $(RELEASE_EXECUTABLE)  - Main geodesic search"
	@echo "  $(TEST_EXECUTABLE)     - Z5D test suite with Mersenne detection"
	@echo "  $(BENCHMARK_EXECUTABLE) - Z5D performance benchmarks"
	@echo "  $(PRECISION_TEST_EXECUTABLE) - Precision validation tests"
	@echo "  $(PROBE_EXECUTABLE)    - Inverse Mersenne probe for RSA factorization"
	@echo ""
	@echo "Build options:"
	@echo "  make BUILD_TYPE=debug    - Build with debug symbols"
	@echo "  make BUILD_TYPE=release  - Build optimized (default)"
	@echo ""
	@echo "🚀 Quick start:"
	@echo "  1. make deps     # Install dependencies"
	@echo "  2. make          # Build executable" 
	@echo "  3. make test     # Verify precision fix"
	@echo ""
	@echo "Example usage:"
	@echo "  ./$(BIN_DIR)/$(PROGRAM_NAME) 37124508045065437 5"
	@echo "  ./$(TEST_EXECUTABLE) 2 10  # Find 10 primes starting from 2"

# === AMX-SPECIFIC TARGETS ===

# Build AMX test executable
$(BIN_DIR)/test_amx_functionality: src/c/test_amx_functionality.c src/c/z5d_phase2.c src/c/z5d_predictor.c | $(BIN_DIR)
	@echo "🔨 Building AMX functionality test..."
	@$(CC) $(CFLAGS) -Isrc/c -DZ5D_USE_OMP=0 $^ -o $@ -lm
	@echo "✅ AMX test built: $@"

# Build AMX performance benchmark
$(BIN_DIR)/benchmark_amx_performance: src/c/benchmark_amx_performance.c src/c/z5d_phase2.c src/c/z5d_predictor.c | $(BIN_DIR)
	@echo "🔨 Building AMX performance benchmark..."
	@$(CC) $(CFLAGS) -Isrc/c -DZ5D_USE_OMP=0 $^ -o $@ -lm
	@echo "✅ AMX benchmark built: $@"

# Build AMX integration test
$(BIN_DIR)/test_amx_integration: src/c/test_amx_integration.c src/c/z5d_phase2.c src/c/z5d_predictor.c | $(BIN_DIR)
	@echo "🔨 Building AMX integration test..."
	@$(CC) $(CFLAGS) -Isrc/c -DZ5D_USE_OMP=0 $^ -o $@ -lm
	@echo "✅ AMX integration test built: $@"

# Run AMX functionality tests
test-amx: $(BIN_DIR)/test_amx_functionality
	@echo "🧪 Running AMX functionality tests..."
	@./$(BIN_DIR)/test_amx_functionality

# Run AMX performance benchmark
bench-amx: $(BIN_DIR)/benchmark_amx_performance
	@echo "⚡ Running AMX performance benchmark..."
	@./$(BIN_DIR)/benchmark_amx_performance

# Run AMX integration tests
test-amx-integration: $(BIN_DIR)/test_amx_integration
	@echo "🧪 Running AMX integration tests..."
	@./$(BIN_DIR)/test_amx_integration

# AMX-optimized build (forces AMX compilation even on non-M1 platforms)
amx-build: CFLAGS += -DZ5D_USE_AMX=1
amx-build: LIB_SOURCES += src/c/z5d_amx.c
amx-build: all
	@echo "🚀 AMX-optimized build complete (gcc z5d_amx.c -o z5d_amx -lgmp -lmpfr -O3)"
	@echo "✅ AMX-optimized build complete"

# === DEBUG TARGET ===
debug:
	@$(MAKE) BUILD_TYPE=debug all

# === INSTALLATION (optional) ===
install: $(EXECUTABLE)
	@echo "📦 Installing to /usr/local/bin..."
	@sudo cp $(EXECUTABLE) /usr/local/bin/
	@echo "✅ Installed: /usr/local/bin/$(PROGRAM_NAME)"

uninstall:
	@echo "🗑️  Uninstalling from /usr/local/bin..."
	@sudo rm -f /usr/local/bin/$(PROGRAM_NAME)
	@echo "✅ Uninstalled"

# === SEMIPRIME NAVIGATION ===

semiprime-nav:
	@bash tools/run_semiprime_nav.sh

clean-semiprime-nav:
	rm -rf artifacts/semiprime_nav