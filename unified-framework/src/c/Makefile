# Z5D Prime Predictor - C Implementation Makefile
# ===============================================
# 
# Cross-platform build system for Z5D predictor C implementation.
# Requires GMP/MPFR/libomp (GNU Multiple Precision Arithmetic and OpenMP Libraries).
# Supports Linux, macOS, and Windows (with MinGW).
#
# Usage:
#   make          - Build library and test program
#   make test     - Build and run tests
#   make gen      - Build and run prime generator
#   make clean    - Clean build artifacts
#   make install  - Install library (requires sudo on Unix)
#   make benchmark - Run performance benchmarks
#   make validate - Validate against Python reference
#   make all      - Build everything
#
# Dependencies:
#   Install GMP/MPFR/libomp headers (libgmp-dev/libmpfr-dev/libomp-dev on Debian/Ubuntu, gmp/mpfr/libomp via Homebrew on macOS)
#   Override paths via GMP_INCLUDE/GMP_LIB/MPFR_INCLUDE/MPFR_LIB/OPENMP_LIB if needed:
#     make GMP_INCLUDE=/custom/include GMP_LIB=/custom/lib ...
#
# @file Makefile
# @author Unified Framework Team (Updated by D.A.L. III for header rule fix)
# @version 1.6

# Compiler and tool configuration
CC := clang  # Explicitly use Clang for macOS compatibility
AR := ar
INSTALL := install

# Platform-specific configuration - moved earlier for OpenMP detection
UNAME_S := $(shell uname -s 2>/dev/null || echo Windows)

# Directories
SRC_DIR := .
BUILD_DIR := build
BIN_DIR := bin
LIB_DIR := lib
INCLUDE_DIR := include

# Installation directories
PREFIX := /usr/local
INSTALL_LIB_DIR := $(PREFIX)/lib
INSTALL_INCLUDE_DIR := $(PREFIX)/include
INSTALL_BIN_DIR := $(PREFIX)/bin

# Source files
LIB_SOURCES := z5d_predictor.c z5d_phase2.c z5d_early_exit_mr.c z5d_crypto_prediction.c

# z5d_early_exit_mr.c has fallback implementations when GMP/MPFR are not available
# Always include it and set the MR flag
CFLAGS += -DZ5D_PHASE2_HAS_MR=1

# Add FFTW support if available
ifeq ($(FFTW_AVAILABLE),1)
    LIB_SOURCES += z5d_fft_zeta.c
endif

# LIB_OBJECTS will be calculated later after FFT configuration
TEST_SOURCES := test_z5d.c
TEST_OBJECTS := $(addprefix $(BUILD_DIR)/, $(TEST_SOURCES:.c=.o))
TEST2_SOURCES := test_z5d_phase2.c
TEST2_OBJECTS := $(addprefix $(BUILD_DIR)/, $(TEST2_SOURCES:.c=.o))
TEST_FFT_SOURCES := test_z5d_fft_zeta.c
TEST_FFT_OBJECTS := $(addprefix $(BUILD_DIR)/, $(TEST_FFT_SOURCES:.c=.o))
GEN_SOURCES := z5d_prime_gen.c
GEN_OBJECTS := $(addprefix $(BUILD_DIR)/, $(GEN_SOURCES:.c=.o))
BENCH_SOURCES := bench_z5d_phase2.c
BENCH_OBJECTS := $(addprefix $(BUILD_DIR)/, $(BENCH_SOURCES:.c=.o))
CRYPTO_TEST_SOURCES := test_crypto_scale.c
CRYPTO_TEST_OBJECTS := $(addprefix $(BUILD_DIR)/, $(CRYPTO_TEST_SOURCES:.c=.o))
CRYPTO_DEMO_SOURCES := demo_crypto_prediction.c
CRYPTO_DEMO_OBJECTS := $(addprefix $(BUILD_DIR)/, $(CRYPTO_DEMO_SOURCES:.c=.o))
DEMO_SOURCES := demo_phase2.c
DEMO_OBJECTS := $(addprefix $(BUILD_DIR)/, $(DEMO_SOURCES:.c=.o))
PERFORMANCE_TEST_SOURCES := performance_test.c
PERFORMANCE_TEST_OBJECTS := $(addprefix $(BUILD_DIR)/, $(PERFORMANCE_TEST_SOURCES:.c=.o))
PRIME_GENERATOR_ENHANCED_SOURCES := prime_generator_enhanced.c
PRIME_GENERATOR_ENHANCED_OBJECTS := $(addprefix $(BUILD_DIR)/, $(PRIME_GENERATOR_ENHANCED_SOURCES:.c=.o))
DEMO_ENHANCEMENTS_SOURCES := demo_enhancements.c
DEMO_ENHANCEMENTS_OBJECTS := $(addprefix $(BUILD_DIR)/, $(DEMO_ENHANCEMENTS_SOURCES:.c=.o))
Z5D_MERSENNE_SOURCES := z5d_mersenne.c
Z5D_MERSENNE_OBJECTS := $(addprefix $(BUILD_DIR)/, $(Z5D_MERSENNE_SOURCES:.c=.o))

# Output files
STATIC_LIB := $(LIB_DIR)/libz5d.a
SHARED_LIB := $(LIB_DIR)/libz5d.dylib  # Explicit .dylib for macOS
TEST_EXECUTABLE := $(BIN_DIR)/test_z5d
TEST_PHASE2_EXECUTABLE := $(BIN_DIR)/test_z5d_phase2
TEST_FFT_EXECUTABLE := $(BIN_DIR)/test_z5d_fft_zeta
BENCHMARK_EXECUTABLE := $(BIN_DIR)/benchmark_z5d
BENCH_PHASE2_EXECUTABLE := $(BIN_DIR)/bench_z5d_phase2
DEMO_PHASE2_EXECUTABLE := $(BIN_DIR)/demo_phase2
GEN_EXECUTABLE := $(BIN_DIR)/z5d_prime_gen
CRYPTO_TEST_EXECUTABLE := $(BIN_DIR)/test_crypto_scale
CRYPTO_DEMO_EXECUTABLE := $(BIN_DIR)/demo_crypto_prediction
PRIME_GEN_EXECUTABLE := $(BIN_DIR)/prime_generator
ULTRA_BENCHMARK_EXECUTABLE := $(BIN_DIR)/ultra_prime_benchmark
Z5D_BENCH_EXECUTABLE := $(BIN_DIR)/z5d_bench
TEST_AMX_FUNCTIONALITY_EXECUTABLE := $(BIN_DIR)/test_amx_functionality
TEST_AMX_INTEGRATION_EXECUTABLE := $(BIN_DIR)/test_amx_integration  
BENCHMARK_AMX_EXECUTABLE := $(BIN_DIR)/benchmark_amx_performance
PERFORMANCE_TEST_EXECUTABLE := $(BIN_DIR)/performance_test
PRIME_GENERATOR_ENHANCED_EXECUTABLE := $(BIN_DIR)/prime_generator_enhanced
DEMO_ENHANCEMENTS_EXECUTABLE := $(BIN_DIR)/demo_enhancements
Z5D_MERSENNE_EXECUTABLE := $(BIN_DIR)/z5d_mersenne

# GMP/MPFR configuration (optional)
# Try to detect if libraries are available, otherwise build without them
PKG_CONFIG_EXISTS := $(shell command -v pkg-config >/dev/null 2>&1 && echo 1 || echo 0)
GMP_AVAILABLE := $(shell if [ "$(PKG_CONFIG_EXISTS)" = "1" ]; then pkg-config --exists gmp && echo 1 || echo 0; \
    else \
        (test -f /usr/include/gmp.h -o -f /usr/local/include/gmp.h -o -f /opt/homebrew/include/gmp.h) && echo 1 || echo 0; \
    fi)
MPFR_AVAILABLE := $(shell if [ "$(PKG_CONFIG_EXISTS)" = "1" ]; then pkg-config --exists mpfr && echo 1 || echo 0; \
    else \
        (test -f /usr/include/mpfr.h -o -f /usr/local/include/mpfr.h -o -f /opt/homebrew/include/mpfr.h) && echo 1 || echo 0; \
    fi)

ifeq ($(GMP_AVAILABLE)$(MPFR_AVAILABLE),11)
    ifeq ($(PKG_CONFIG_EXISTS),1)
        GMP_INCLUDE ?= $(shell pkg-config --cflags gmp 2>/dev/null || echo -I/opt/homebrew/include)
        GMP_LIB ?= $(shell pkg-config --libs gmp 2>/dev/null || echo -L/opt/homebrew/lib )
        MPFR_INCLUDE ?= $(shell pkg-config --cflags mpfr 2>/dev/null || echo -I/opt/homebrew/include)
        MPFR_LIB ?= $(shell pkg-config --libs mpfr 2>/dev/null || echo -L/opt/homebrew/lib -lmpfr)
    else
        GMP_INCLUDE ?= $(shell \
            if test -f /usr/include/gmp.h; then echo -I/usr/include; \
            elif test -f /usr/local/include/gmp.h; then echo -I/usr/local/include; \
            elif test -f /opt/homebrew/include/gmp.h; then echo -I/opt/homebrew/include; \
            else echo ""; fi)
        GMP_LIB ?= $(shell \
            if test -f /usr/lib/libgmp.a -o -f /usr/lib/libgmp.so; then echo -L/usr/lib ; \
            elif test -f /usr/local/lib/libgmp.a -o -f /usr/local/lib/libgmp.so; then echo -L/usr/local/lib ; \
            elif test -f /opt/homebrew/lib/libgmp.a -o -f /opt/homebrew/lib/libgmp.dylib; then echo -L/opt/homebrew/lib ; \
            else echo ""; fi)
        MPFR_INCLUDE ?= $(shell \
            if test -f /usr/include/mpfr.h; then echo -I/usr/include; \
            elif test -f /usr/local/include/mpfr.h; then echo -I/usr/local/include; \
            elif test -f /opt/homebrew/include/mpfr.h; then echo -I/opt/homebrew/include; \
            else echo ""; fi)
        MPFR_LIB ?= $(shell \
            if test -f /usr/lib/libmpfr.a -o -f /usr/lib/libmpfr.so; then echo -L/usr/lib -lmpfr; \
            elif test -f /usr/local/lib/libmpfr.a -o -f /usr/local/lib/libmpfr.so; then echo -L/usr/local/lib -lmpfr; \
            elif test -f /opt/homebrew/lib/libmpfr.a -o -f /opt/homebrew/lib/libmpfr.dylib; then echo -L/opt/homebrew/lib -lmpfr; \
            else echo "-lmpfr"; fi)
    endif
    CFLAGS += -DZ5D_HAVE_MPFR=1
    MPFR_LDFLAGS := $(GMP_LIB) $(MPFR_LIB)
else
    GMP_INCLUDE := 
    GMP_LIB := 
    MPFR_INCLUDE := 
    MPFR_LIB := 
    CFLAGS += -DZ5D_HAVE_MPFR=0
    MPFR_LDFLAGS := 
    $(warning "MPFR/GMP not found - using fallback implementations")
endif

# OpenMP configuration for macOS
ifeq ($(UNAME_S),Darwin)
    # Use Homebrew's keg-only paths for libomp
    # Note: `brew --prefix libomp` often fails, so we hardcode the path.
    OPENMP_LIB_DIR := /opt/homebrew/opt/libomp/lib
    OPENMP_INCLUDE_DIR := /opt/homebrew/opt/libomp/include
    OPENMP_LIB := -lomp

    # Test for libomp directory existence to determine availability
    ifeq ($(wildcard $(OPENMP_LIB_DIR)),)
        OMP_AVAILABLE := 0
    else
        OMP_AVAILABLE := 1
    endif

    ifeq ($(OMP_AVAILABLE),1)
        # Apple Clang requires -Xpreprocessor for OpenMP directives
        # Link to the brew-installed library explicitly
        OPENMP_CFLAGS := -Xpreprocessor -fopenmp -I$(OPENMP_INCLUDE_DIR) -Wno-pedantic
        OPENMP_LDFLAGS := -L$(OPENMP_LIB_DIR) $(OPENMP_LIB)
        $(info "OpenMP detected via Homebrew for macOS.")
    else
        OPENMP_CFLAGS :=
        OPENMP_LDFLAGS :=
        $(warning "OpenMP (libomp) not found in Homebrew prefix. Build will be single-threaded.")
    endif
else
    # Configuration for Linux and other platforms
    OPENMP_CFLAGS := -fopenmp
    OPENMP_LDFLAGS := -fopenmp
    OMP_AVAILABLE := 1
    $(info "OpenMP configuration for non-macOS platform.")
endif

# Ensure flags are added to CFLAGS and LDFLAGS
CFLAGS += $(OPENMP_CFLAGS)
LDFLAGS += $(OPENMP_LDFLAGS)

# FFTW configuration (optional, GPL licensed - enable with USE_FFTW=1)
USE_FFTW ?= 0
FFTW_AVAILABLE := $(shell if [ "$(USE_FFTW)" = "1" ]; then \
    if [ "$(PKG_CONFIG_EXISTS)" = "1" ]; then pkg-config --exists fftw3 && echo 1 || echo 0; \
    else (test -f /usr/include/fftw3.h -o -f /usr/local/include/fftw3.h -o -f /opt/homebrew/include/fftw3.h) && echo 1 || echo 0; \
    fi; else echo 0; fi)

ifeq ($(FFTW_AVAILABLE),1)
    ifeq ($(PKG_CONFIG_EXISTS),1)
        FFTW_INCLUDE ?= $(shell pkg-config --cflags fftw3 2>/dev/null || echo -I/opt/homebrew/include)
        FFTW_LIB ?= $(shell pkg-config --libs fftw3 2>/dev/null || echo -L/opt/homebrew/lib -lfftw3)
    else
        FFTW_INCLUDE ?= $(shell \
            if test -f /usr/include/fftw3.h; then echo -I/usr/include; \
            elif test -f /usr/local/include/fftw3.h; then echo -I/usr/local/include; \
            elif test -f /opt/homebrew/include/fftw3.h; then echo -I/opt/homebrew/include; \
            else echo ""; fi)
        FFTW_LIB ?= $(shell \
            if test -f /usr/lib/libfftw3.a -o -f /usr/lib/libfftw3.so; then echo -L/usr/lib -lfftw3; \
            elif test -f /usr/local/lib/libfftw3.a -o -f /usr/local/lib/libfftw3.so; then echo -L/usr/local/lib -lfftw3; \
            elif test -f /opt/homebrew/lib/libfftw3.a -o -f /opt/homebrew/lib/libfftw3.dylib; then echo -L/opt/homebrew/lib -lfftw3; \
            else echo "-lfftw3"; fi)
    endif
    FFTW_LDFLAGS := $(FFTW_LIB)
else
    FFTW_INCLUDE := 
    FFTW_LIB := 
    FFTW_LDFLAGS := 
    ifeq ($(USE_FFTW),1)
        $(error FFTW requested with USE_FFTW=1 but libfftw3 not found. Install FFTW3 development library or remove USE_FFTW=1)
    endif
endif

# Primesieve configuration (optional) - Enhanced with pkg-config + Homebrew fallback
PKGCONFIG ?= pkg-config
PRIMESIEVE_CFLAGS ?= $(shell $(PKGCONFIG) --cflags libprimesieve 2>/dev/null)
PRIMESIEVE_LIBS   ?= $(shell $(PKGCONFIG) --libs   libprimesieve 2>/dev/null)

# Homebrew fallback on Apple Silicon
ifneq ("$(wildcard /opt/homebrew/include/primesieve.h)","")
  PRIMESIEVE_CFLAGS += -I/opt/homebrew/include
  PRIMESIEVE_LIBS   += -L/opt/homebrew/lib -lprimesieve
endif

# Check if primesieve is available
PRIMESIEVE_AVAILABLE := $(shell if [ "$(PKG_CONFIG_EXISTS)" = "1" ]; then pkg-config --exists libprimesieve && echo 1 || echo 0; \
    else (test -f /usr/include/primesieve.h -o -f /usr/local/include/primesieve.h -o -f /opt/homebrew/include/primesieve.h) && echo 1 || echo 0; \
    fi)

ifeq ($(PRIMESIEVE_AVAILABLE),1)
    PRIMESIEVE_LDFLAGS := $(PRIMESIEVE_LIBS)
    CFLAGS += -DHAVE_PRIMESIEVE=1
else
    PRIMESIEVE_CFLAGS := 
    PRIMESIEVE_LIBS := 
    PRIMESIEVE_LDFLAGS := 
    CFLAGS += -DHAVE_PRIMESIEVE=0
    $(info "Primesieve not found - Z5D benchmark will use fallback implementations")
endif

# Compiler flags
CFLAGS := -std=c11 -Wall -Wextra -Wno-deprecated-declarations -O3 -fPIC \
  $(GMP_INCLUDE) $(MPFR_INCLUDE) $(PRIMESIEVE_CFLAGS) $(OPENMP_CFLAGS)
CFLAGS += -D_POSIX_C_SOURCE=200809L  # For POSIX compliance

# Add FFTW support if available
ifeq ($(FFTW_AVAILABLE),1)
    CFLAGS += $(FFTW_INCLUDE) -DZ5D_USE_FFTW
endif

DEBUG_CFLAGS := -g -O0 -DDEBUG
RELEASE_CFLAGS := -O3 -DNDEBUG

# Linker flags will be set per platform to avoid duplicates
# Initialize base linker flags
ifneq ($(OPENMP_LIB_DIR),)
    LDFLAGS += -L$(OPENMP_LIB_DIR)
endif

ifeq ($(UNAME_S),Linux)
    SHARED_LIB := $(LIB_DIR)/libz5d.so
    SHARED_LDFLAGS := -shared
    LDFLAGS := -lm $(MPFR_LDFLAGS) $(OMP_LDFLAGS)
    ifeq ($(FFTW_AVAILABLE),1)
        LDFLAGS += $(FFTW_LDFLAGS)
    endif
    RELEASE_CFLAGS := -O3 -DNDEBUG -march=native -mavx2 -mfma -ffast-math -fno-math-errno
endif
ifeq ($(UNAME_S),Darwin)
    SHARED_LIB := $(LIB_DIR)/libz5d.dylib
    SHARED_LDFLAGS := -dynamiclib -install_name @rpath/libz5d.dylib
    LDFLAGS += -lm $(MPFR_LDFLAGS) $(OMP_LDFLAGS)
    ifeq ($(FFTW_AVAILABLE),1)
        LDFLAGS += $(FFTW_LDFLAGS)
    endif
    RELEASE_CFLAGS := -O3 -DNDEBUG -march=armv8.5-a -mcpu=apple-m1
    CFLAGS += -D_DARWIN_C_SOURCE
endif
ifeq ($(UNAME_S),Windows)
    SHARED_LIB := $(LIB_DIR)/libz5d.dll
    SHARED_LDFLAGS := -shared
    LDFLAGS := -lm $(MPFR_LDFLAGS) $(OMP_LDFLAGS)
    ifeq ($(USE_FFTW),1)
        LDFLAGS += $(FFTW_LIB)
    endif
    CC := gcc.exe
endif

# Build configuration
BUILD_TYPE := release
ifeq ($(BUILD_TYPE),debug)
    CFLAGS += $(DEBUG_CFLAGS)
else
    CFLAGS += $(RELEASE_CFLAGS)
endif
# --- FFT-zeta toggle (after platform configuration) ------------------------
# Default OFF. Build with `make FFT_ZETA_ENHANCE=1` to enable.
FFT_ZETA_ENHANCE ?= 0

# If the generator is built with FFT-zeta, we also need the FFT module & libs.
ifeq ($(FFT_ZETA_ENHANCE),1)
  USE_FFTW := 1
  CFLAGS   += -DFFT_ZETA_ENHANCE=1
else
  CFLAGS   += -DFFT_ZETA_ENHANCE=0
endif

# Where the FFT implementation lives (adjust path if different)
Z5D_FFT_SRCS ?= z5d_fft_zeta.c

# Link flags when FFTW is requested (threaded variant optional)
ifeq ($(USE_FFTW),1)
  CFLAGS   += -DUSE_FFTW=1
  LIB_SOURCES += $(Z5D_FFT_SRCS)
  LDFLAGS  += -lfftw3 -lm
  # or, for threaded: LDFLAGS += -lfftw3_threads -lfftw3 -lm
endif

# Calculate LIB_OBJECTS after FFT configuration
LIB_OBJECTS := $(addprefix $(BUILD_DIR)/, $(LIB_SOURCES:.c=.o))
# Phony targets
.PHONY: all clean test test-phase2 test-fft gen install uninstall benchmark validate help phase2
.PHONY: debug release static shared test-amx test-amx-integration bench-amx amx-build
.PHONY: lis-corrector lis-metric lis-phase-a lis-all lis-clean lis-test
.DEFAULT_GOAL := all

# Main targets
all: directories static shared test gen phase2 test-phase2 prime-gen ultra-benchmark demo $(INCLUDE_DIR)/z5d_predictor.h $(INCLUDE_DIR)/z5d_phase2.h
ifeq ($(USE_FFTW),1)
all: $(INCLUDE_DIR)/z5d_fft_zeta.h test-fft
endif

static: $(STATIC_LIB)

shared: $(SHARED_LIB)

test: $(TEST_EXECUTABLE)
	@echo "Running Z5D test suite..."
	@$(TEST_EXECUTABLE)

test-phase2: $(TEST_PHASE2_EXECUTABLE)
	@echo "Running Z5D Phase 2 test suite..."
	@$(TEST_PHASE2_EXECUTABLE)

test-parity: $(BIN_DIR)/test_phase2_parity
	@echo "Running Phase 2 parity test..."
	@$(BIN_DIR)/test_phase2_parity

test-parity-debug: $(BIN_DIR)/test_phase2_parity_debug
	@echo "Running Phase 2 parity test with debug residues..."
	@$(BIN_DIR)/test_phase2_parity_debug

test-fft: $(TEST_FFT_EXECUTABLE)
ifeq ($(USE_FFTW),1)
	@echo "Running Z5D FFT-zeta test suite..."
	@$(TEST_FFT_EXECUTABLE)
else
	@echo "FFT-zeta tests disabled. Enable with USE_FFTW=1"
endif

gen: $(GEN_EXECUTABLE)
	@echo "Running Z5D prime generator example..."
	@$(GEN_EXECUTABLE)

test-crypto: $(CRYPTO_TEST_EXECUTABLE)
	@echo "Running Z5D crypto scale test..."
	@$(CRYPTO_TEST_EXECUTABLE) --capabilities
	@echo ""
	@$(CRYPTO_TEST_EXECUTABLE) --bit-length 512 --trials 5 --benchmark --verbose

demo-crypto: $(CRYPTO_DEMO_EXECUTABLE)
	@echo "Running Z5D crypto prediction demonstration..."
	@$(CRYPTO_DEMO_EXECUTABLE)

prime-gen: $(PRIME_GEN_EXECUTABLE)
	@echo "Ultra-Large Scale Z5D Prime Generator ready. Run with:"
	@echo "  $(PRIME_GEN_EXECUTABLE) --help"

ultra-benchmark: $(ULTRA_BENCHMARK_EXECUTABLE)
	@echo "Ultra-Large Scale Z5D Benchmark ready. Run with:"
	@echo "  $(ULTRA_BENCHMARK_EXECUTABLE) --help"

z5d-bench: $(Z5D_BENCH_EXECUTABLE)
	@echo "Running Z5D vs primesieve benchmark..."
	@$(Z5D_BENCH_EXECUTABLE) --verbose

z5d-bench-help: $(Z5D_BENCH_EXECUTABLE)
	@echo "Z5D vs primesieve benchmark ready. Run with:"
	@echo "  $(Z5D_BENCH_EXECUTABLE) --help"

demo: z5d_demonstration
	@echo "Running Z5D compute reduction demonstration..."
	@./z5d_demonstration --validate

phase2: $(BENCH_PHASE2_EXECUTABLE) $(DEMO_PHASE2_EXECUTABLE)
	@echo "Phase 2 ready. Run benchmarks with:"
	@echo "  $(BENCH_PHASE2_EXECUTABLE) --help"
	@echo "Or see comprehensive demo:"
	@echo "  $(DEMO_PHASE2_EXECUTABLE)"

# AMX functionality tests  
test-amx: $(TEST_AMX_FUNCTIONALITY_EXECUTABLE)
	@echo "Running AMX functionality tests..."
	@$(TEST_AMX_FUNCTIONALITY_EXECUTABLE)

# AMX integration tests
test-amx-integration: $(TEST_AMX_INTEGRATION_EXECUTABLE)
	@echo "Running AMX integration tests..."
	@$(TEST_AMX_INTEGRATION_EXECUTABLE)

# AMX performance benchmark
bench-amx: $(BENCHMARK_AMX_EXECUTABLE)
	@echo "Running AMX performance benchmark..."
	@$(BENCHMARK_AMX_EXECUTABLE)

# AMX-optimized build
amx-build:
	@echo "Building with AMX optimization enabled..."
	@$(MAKE) CFLAGS="$(CFLAGS) -DZ5D_USE_AMX=1" all test-amx
	@echo "AMX-optimized build complete"

# Create necessary directories
directories:
	@mkdir -p $(BUILD_DIR) $(LIB_DIR) $(BIN_DIR) $(INCLUDE_DIR)

# Header copy rules
$(INCLUDE_DIR)/z5d_predictor.h: z5d_predictor.h | directories
	@cp $< $@

$(INCLUDE_DIR)/z5d_phase2.h: z5d_phase2.h | directories
	@cp $< $@

# FFT-zeta header only copied if FFTW is enabled
ifeq ($(USE_FFTW),1)
$(INCLUDE_DIR)/z5d_fft_zeta.h: z5d_fft_zeta.h | directories
	@cp $< $@
endif

# Static library
$(STATIC_LIB): $(LIB_OBJECTS) | directories
	@echo "Creating static library: $@"
	@$(AR) rcs $@ $^

# Shared library
$(SHARED_LIB): $(LIB_OBJECTS) | directories
	@echo "Creating shared library: $@"
	@$(CC) $(SHARED_LDFLAGS) -o $@ $^ $(LDFLAGS)

# Test executables
$(TEST_EXECUTABLE): $(TEST_OBJECTS) $(STATIC_LIB) | directories
	@echo "Building test executable: $@"
	@$(CC) -o $@ $^ $(LDFLAGS)

$(TEST_PHASE2_EXECUTABLE): $(TEST2_OBJECTS) $(STATIC_LIB) | directories
	@echo "Building Phase 2 test executable: $@"
	@$(CC) -o $@ $^ $(LDFLAGS)

# Parity test executable
$(BIN_DIR)/test_phase2_parity: ../../tests/test_phase2_parity.c $(STATIC_LIB) | directories
	@echo "Building Phase 2 parity test executable: $@"
	@$(CC) $(CFLAGS) -o $@ $< $(STATIC_LIB) $(LDFLAGS)

# Parity test with debug residues
$(BIN_DIR)/test_phase2_parity_debug: ../../tests/test_phase2_parity.c $(STATIC_LIB) | directories
	@echo "Building Phase 2 parity test executable (with debug residues): $@"
	@$(CC) $(CFLAGS) -DZ5D_DEBUG_RESIDUES -o $@ $< $(STATIC_LIB) $(LDFLAGS)

# Parity demo executable
$(BIN_DIR)/demo_phase2_parity: ../../tests/demo_phase2_parity.c $(STATIC_LIB) | directories
	@echo "Building Phase 2 parity demo executable: $@"
	@$(CC) $(CFLAGS) -o $@ $< $(STATIC_LIB) $(LDFLAGS)

demo-parity: $(BIN_DIR)/demo_phase2_parity
	@echo "Running Phase 2 parity fix demonstration..."
	@$(BIN_DIR)/demo_phase2_parity

# FFT test executable only built if FFTW is enabled
ifeq ($(USE_FFTW),1)
$(TEST_FFT_EXECUTABLE): $(TEST_FFT_OBJECTS) $(STATIC_LIB) | directories
	@echo "Building FFT-zeta test executable: $@"
	@$(CC) -o $@ $^ $(LDFLAGS)
else
$(TEST_FFT_EXECUTABLE):
	@echo "FFT-zeta test requires FFTW. Build with USE_FFTW=1"
	@false
endif

# Generator executable
$(GEN_EXECUTABLE): $(GEN_OBJECTS) $(STATIC_LIB) | directories
	@echo "Building generator executable: $@"
	@$(CC) -o $@ $^ $(LDFLAGS)

# Crypto test executable
$(CRYPTO_TEST_EXECUTABLE): $(CRYPTO_TEST_OBJECTS) $(STATIC_LIB) | directories
	@echo "Building crypto scale test executable: $@"
	@$(CC) -o $@ $^ $(LDFLAGS)

# Crypto demo executable
$(CRYPTO_DEMO_EXECUTABLE): $(CRYPTO_DEMO_OBJECTS) $(STATIC_LIB) | directories
	@echo "Building crypto prediction demo executable: $@"
	@$(CC) -o $@ $^ $(LDFLAGS)

# Enhanced prime generator executable (Apple M1 Max only)
$(PRIME_GEN_EXECUTABLE): prime_generator.c $(STATIC_LIB) | directories
	@echo "Building enhanced prime generator executable for Apple M1 Max: $@"
	@$(CC) $(CFLAGS) -mcpu=apple-m1 -o $@ $< $(STATIC_LIB) $(LDFLAGS)

# Ultra benchmark executable  
$(ULTRA_BENCHMARK_EXECUTABLE): ultra_prime_benchmark.c $(STATIC_LIB) | directories
	@echo "Building ultra benchmark executable: $@"
	@$(CC) $(CFLAGS) -o $@ $< $(STATIC_LIB) $(LDFLAGS)

# Z5D vs primesieve benchmark executable
$(Z5D_BENCH_EXECUTABLE): z5d_bench.c $(STATIC_LIB) | directories
	@echo "Building Z5D vs primesieve benchmark executable: $@"
	@$(CC) $(CFLAGS) -o $@ $< $(STATIC_LIB) $(LDFLAGS) $(PRIMESIEVE_LDFLAGS)

# Demonstration executable
z5d_demonstration: z5d_demonstration.c $(STATIC_LIB) | directories
	@echo "Building Z5D demonstration: $@"
	@$(CC) $(CFLAGS) -o $@ $< $(STATIC_LIB) $(LDFLAGS)

# Phase 2 executables
$(BENCH_PHASE2_EXECUTABLE): $(BENCH_OBJECTS) $(STATIC_LIB) | directories
	@echo "Building Phase 2 benchmark executable: $@"
	@$(CC) -o $@ $^ $(LDFLAGS)

$(DEMO_PHASE2_EXECUTABLE): $(DEMO_OBJECTS) $(STATIC_LIB) | directories
	@echo "Building Phase 2 demo executable: $@"
	@$(CC) -o $@ $^ $(LDFLAGS)

# AMX functionality test executable
$(TEST_AMX_FUNCTIONALITY_EXECUTABLE): test_amx_functionality.c $(STATIC_LIB) | directories
	@echo "Building AMX functionality test executable: $@"
	@$(CC) $(CFLAGS) -DZ5D_USE_OMP=0 -o $@ $< $(STATIC_LIB) $(LDFLAGS)

# AMX integration test executable  
$(TEST_AMX_INTEGRATION_EXECUTABLE): test_amx_integration.c $(STATIC_LIB) | directories
	@echo "Building AMX integration test executable: $@"
	@$(CC) $(CFLAGS) -DZ5D_USE_OMP=0 -o $@ $< $(STATIC_LIB) $(LDFLAGS)

# AMX performance benchmark executable
$(BENCHMARK_AMX_EXECUTABLE): benchmark_amx_performance.c $(STATIC_LIB) | directories
	@echo "Building AMX performance benchmark executable: $@"
	@$(CC) $(CFLAGS) -DZ5D_USE_OMP=0 -o $@ $< $(STATIC_LIB) $(LDFLAGS)

# Performance test executable
$(PERFORMANCE_TEST_EXECUTABLE): $(PERFORMANCE_TEST_OBJECTS) $(STATIC_LIB) | directories
	@echo "Building performance test executable: $@"
	@$(CC) -o $@ $^ $(LDFLAGS)

# Prime generator enhanced executable
$(PRIME_GENERATOR_ENHANCED_EXECUTABLE): $(PRIME_GENERATOR_ENHANCED_OBJECTS) $(STATIC_LIB) | directories
	@echo "Building prime generator enhanced executable: $@"
	@$(CC) -o $@ $^ $(LDFLAGS)

# Demo enhancements executable
$(DEMO_ENHANCEMENTS_EXECUTABLE): $(DEMO_ENHANCEMENTS_OBJECTS) $(STATIC_LIB) | directories
	@echo "Building demo enhancements executable: $@"
	@$(CC) -o $@ $^ $(LDFLAGS)

# Z5D Mersenne executable
$(Z5D_MERSENNE_EXECUTABLE): $(Z5D_MERSENNE_OBJECTS) $(STATIC_LIB) | directories
	@echo "Building Z5D Mersenne executable: $@"
	@$(CC) -o $@ $^ $(LDFLAGS)

# Object files
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c | directories
	@echo "Compiling: $<"
	@$(CC) $(CFLAGS) -c $< -o $@

# Benchmark target
benchmark: $(BENCHMARK_EXECUTABLE)
	@echo "Running Z5D performance benchmarks..."
	@$(BENCHMARK_EXECUTABLE)

$(BENCHMARK_EXECUTABLE): benchmark_z5d.c $(STATIC_LIB) | directories
	@echo "Building benchmark executable: $@"
	@$(CC) $(CFLAGS) -o $@ $< $(STATIC_LIB) $(LDFLAGS)

# Create a simple benchmark program
benchmark_z5d.c:
	@echo "Creating benchmark program..."
	@echo '#include "z5d_predictor.h"' > $@
	@echo '#include <time.h>' >> $@
	@echo 'int main(void) {' >> $@
	@echo '    printf("Z5D Performance Benchmark\\n");' >> $@
	@echo '    printf("========================\\n");' >> $@
	@echo '    clock_t start = clock();' >> $@
	@echo '    for (int i = 0; i < 100000; i++) {' >> $@
	@echo '        z5d_prime(1000 + i, 0.0, 0.0, 0.3, 1);' >> $@
	@echo '    }' >> $@
	@echo '    clock_t end = clock();' >> $@
	@echo '    double elapsed = ((double)(end - start)) / CLOCKS_PER_SEC;' >> $@
	@echo '    printf("100,000 predictions in %.3f seconds\\n", elapsed);' >> $@
	@echo '    printf("Average: %.2f μs per prediction\\n", elapsed / 100000.0 * 1000000.0);' >> $@
	@echo '    return 0;' >> $@
	@echo '}' >> $@

# Validation against Python reference
validate: $(TEST_EXECUTABLE)
	@echo "Validating C implementation against Python reference..."
	@cd ../.. && python -c "\
import sys; sys.path.append('src'); \
from z_framework.discrete.z5d_predictor import z5d_prime; \
print('Python reference values:'); \
for k in [10, 100, 1000, 10000]: \
    print(f'z5d_prime({k}) = {z5d_prime(k):.6f}'); \
"
	@echo "\nC implementation values:"
	@./$(TEST_EXECUTABLE) | grep "C implementation"

# Installation
install: all $(INCLUDE_DIR)/z5d_predictor.h $(INCLUDE_DIR)/z5d_phase2.h
	@echo "Installing Z5D library to $(PREFIX)..."
	@$(INSTALL) -d $(INSTALL_LIB_DIR) $(INSTALL_INCLUDE_DIR) $(INSTALL_BIN_DIR)
	@$(INSTALL) -m 644 $(STATIC_LIB) $(INSTALL_LIB_DIR)/
	@$(INSTALL) -m 755 $(SHARED_LIB) $(INSTALL_LIB_DIR)/
	@$(INSTALL) -m 644 $(INCLUDE_DIR)/z5d_predictor.h $(INSTALL_INCLUDE_DIR)/
	@$(INSTALL) -m 644 $(INCLUDE_DIR)/z5d_phase2.h $(INSTALL_INCLUDE_DIR)/
	@$(INSTALL) -m 755 $(TEST_EXECUTABLE) $(INSTALL_BIN_DIR)/
	@$(INSTALL) -m 755 $(GEN_EXECUTABLE) $(INSTALL_BIN_DIR)/
	@$(INSTALL) -m 755 $(BENCH_PHASE2_EXECUTABLE) $(INSTALL_BIN_DIR)/
	@echo "Installation complete."

# Uninstallation
uninstall:
	@echo "Uninstalling Z5D library from $(PREFIX)..."
	@rm -f $(INSTALL_LIB_DIR)/libz5d.a
	@rm -f $(INSTALL_LIB_DIR)/libz5d.dylib
	@rm -f $(INSTALL_INCLUDE_DIR)/z5d_predictor.h
	@rm -f $(INSTALL_INCLUDE_DIR)/z5d_phase2.h
	@rm -f $(INSTALL_BIN_DIR)/test_z5d
	@rm -f $(INSTALL_BIN_DIR)/z5d_prime_gen
	@rm -f $(INSTALL_BIN_DIR)/bench_z5d_phase2
	@echo "Uninstallation complete."

# Cleanup
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR) $(LIB_DIR) $(BIN_DIR) $(INCLUDE_DIR)
	@rm -f benchmark_z5d.c z5d_demonstration performance_validation

# Help target
help:
	@echo "Z5D Prime Predictor - C Implementation Build System"
	@echo "=================================================="
	@echo ""
	@echo "Available targets:"
	@echo "  all        - Build library and test program (default)"
	@echo "  static     - Build static library only"
	@echo "  shared     - Build shared library only"
	@echo "  test       - Build and run test suite"
	@echo "  gen        - Build and run prime generator"
	@echo "  test-parity - Build and run Phase 2 parity leak test"
	@echo "  test-parity-debug - Build and run parity test with debug residue counters"
	@echo "  benchmark  - Build and run performance benchmarks"
	@echo "  z5d-bench  - Build and run Z5D vs primesieve benchmark"
	@echo "  validate   - Validate against Python reference"
	@echo "  test-amx   - Build and run AMX functionality tests"
	@echo "  test-amx-integration - Build and run AMX integration tests"
	@echo "  bench-amx  - Build and run AMX performance benchmarks"
	@echo "  amx-build  - Build with AMX optimization enabled"
	@echo "  install    - Install library and headers"
	@echo "  uninstall  - Remove installed files"
	@echo "  clean      - Remove build artifacts"
	@echo "  debug      - Build with debug symbols"
	@echo "  release    - Build with optimizations"
	@echo "  help       - Show this help message"
	@echo ""
	@echo "Platform: $(UNAME_S)"
	@echo "Compiler: $(CC)"
	@echo "Build type: $(BUILD_TYPE)"
	@echo "FFT-zeta enhance: $(FFT_ZETA_ENHANCE)"
	@echo ""
	@echo "FFT-zeta enhancement:"
	@echo "  Build with 'make FFT_ZETA_ENHANCE=1' to enable FFT-based zeta enhancement"
	@echo "  Requires FFTW3 library (libfftw3-dev on Debian/Ubuntu, fftw via Homebrew on macOS)"
	@echo ""
	@echo "AMX support (Apple M1 Max):"
	@echo "  test-amx, test-amx-integration, bench-amx - Run AMX-specific tests and benchmarks"
	@echo "  amx-build - Build with AMX optimization enabled"
	@echo "  Note: For comprehensive AMX builds, run 'make' from the main project directory"
	@echo ""
	@echo "Dependencies: GMP, MPFR, and libomp are required."
	@echo "  Install libgmp-dev/libmpfr-dev/libomp-dev (Debian/Ubuntu), gmp/mpfr/libomp (Homebrew/macOS), or provide custom paths:"
	@echo "    make GMP_INCLUDE=/custom/include GMP_LIB=/custom/lib ..."
	@echo "  Ensure libomp is installed (e.g., brew install libomp on macOS)."
	@echo "  If errors about 'gmp.h', 'mpfr.h', or OpenMP occur, verify paths and installations."
	@echo ""
	@echo "Optional FFTW3 support (GPL licensed):"
	@echo "  Enable with USE_FFTW=1 (adds FFT-zeta enhancement)"
	@echo "  WARNING: FFTW3 is GPL licensed - commercial license may be required for some uses"
	@echo ""
	@echo "LIS CLI Tools:"
	@echo "  lis-corrector  - Build LIS Corrector CLI (single nth prime)"
	@echo "  lis-metric     - Build LIS Metric CLI (range filtering performance)"
	@echo "  lis-phase-a    - Build LIS Phase A CLI (bootstrap confidence intervals)"
	@echo "  lis-all        - Build all LIS CLI tools"
	@echo "  lis-test       - Build and test all LIS CLI tools"
	@echo "  lis-clean      - Clean all LIS CLI build artifacts"

# LIS CLI Tools targets
lis-corrector:
	@echo "Building LIS Corrector CLI..."
	@$(MAKE) -C lis_corrector_cli all

lis-metric:
	@echo "Building LIS Metric CLI..."
	@$(MAKE) -C lis_metric all

lis-phase-a:
	@echo "Building LIS Phase A CLI..."
	@$(MAKE) -C lis_phase_a all

lis-all: lis-corrector lis-metric lis-phase-a
	@echo "All LIS CLI tools built successfully"

lis-test: lis-all
	@echo "Testing LIS CLI tools..."
	@$(MAKE) -C lis_corrector_cli test
	@$(MAKE) -C lis_metric test
	@$(MAKE) -C lis_phase_a test
	@echo "All LIS CLI tools tested successfully"

lis-clean:
	@echo "Cleaning LIS CLI tools..."
	@$(MAKE) -C lis_corrector_cli clean
	@$(MAKE) -C lis_metric clean
	@$(MAKE) -C lis_phase_a clean
	@echo "All LIS CLI build artifacts cleaned"

# Dependency tracking
-include $(LIB_OBJECTS:.o=.d)
-include $(TEST_OBJECTS:.o=.d)
-include $(TEST2_OBJECTS:.o=.d)
-include $(GEN_OBJECTS:.o=.d)
-include $(BENCH_OBJECTS:.o=.d)
-include $(DEMO_OBJECTS:.o=.d)
-include $(PERFORMANCE_TEST_OBJECTS:.o=.d)
-include $(PRIME_GENERATOR_ENHANCED_OBJECTS:.o=.d)
-include $(DEMO_ENHANCEMENTS_OBJECTS:.o=.d)
-include $(Z5D_MERSENNE_OBJECTS:.o=.d)

# Generate dependency files
$(BUILD_DIR)/%.d: $(SRC_DIR)/%.c | directories
	@$(CC) $(CFLAGS) -MM -MT $(BUILD_DIR)/$*.o $< -MF $@
