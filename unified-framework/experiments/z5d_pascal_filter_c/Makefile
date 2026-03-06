# Z5D Pascal-Only Model + Thales Filter — Stage −1/0/S Filter Makefile
# ===================================================================
#
# Build system for Z5D Pascal-Only filter implementation with Thales Gate.
#
# Usage:
#   make          - Build executable (same as make build)
#   make build    - Build z5d_pascal_filter executable
#   make thales   - Build thales_filter executable
#   make run      - Build and run the filter demo
#   make run-thales - Build and run Thales filter test
#   make bench    - Run with timing benchmarks
#   make asan     - Build with AddressSanitizer
#   make ubsan    - Build with UndefinedBehaviorSanitizer
#   make clean    - Clean build artifacts
#

# Compiler and basic settings
CC := gcc
TARGET := z5d_pascal_filter
THALES_TARGET := thales_filter
SOURCE := z5d_pascal_filter.c
THALES_SOURCE := thales_filter.c

# Default compiler flags (optimized build)
CFLAGS := -O3 -march=native -std=c11 -Wall -Wextra -Werror -DNDEBUG
LDFLAGS := -lm

# MPFR/GMP flags for Thales filter
THALES_CFLAGS := $(CFLAGS) -DTHALES_FILTER_MAIN -I/opt/homebrew/opt/mpfr/include -I/opt/homebrew/Cellar/gmp/6.3.0/include
THALES_LDFLAGS := $(LDFLAGS) -L/opt/homebrew/opt/mpfr/lib -L/opt/homebrew/Cellar/gmp/6.3.0/lib -lmpfr -lgmp

# Platform detection
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    LDFLAGS += -lrt
endif

# OpenMP detection
OPENMP_AVAILABLE := $(shell $(CC) -fopenmp -E -x c /dev/null >/dev/null 2>&1 && echo yes)
ifeq ($(OPENMP_AVAILABLE),yes)
    CFLAGS += -fopenmp
    LDFLAGS += -fopenmp
else
    CFLAGS += -DNO_OPENMP
    $(warning OpenMP not available; parallelization disabled)
endif

# Default target
.PHONY: all build thales run run-thales bench asan ubsan clean help

all: build

# Build the Pascal filter executable
build: $(TARGET)

# Build the Thales filter executable  
thales: $(THALES_TARGET)

$(TARGET): $(SOURCE)
	@echo "Building $(TARGET)..."
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)
	@echo "Build complete: ./$(TARGET)"

$(THALES_TARGET): $(THALES_SOURCE) thales_filter.h
	@echo "Building $(THALES_TARGET)..."
	$(CC) $(THALES_CFLAGS) -o $@ $(THALES_SOURCE) $(THALES_LDFLAGS)
	@echo "Build complete: ./$(THALES_TARGET)"

# Run the Pascal filter demo
run: $(TARGET)
	@echo "Running Z5D Pascal Filter demo..."
	./$(TARGET)

# Run the Thales filter test
run-thales: $(THALES_TARGET)
	@echo "Running Thales Filter test..."
	./$(THALES_TARGET)

# Benchmark mode (same as run for now, timing is built-in)
bench: $(TARGET)
	@echo "Running Z5D Pascal Filter benchmarks..."
	./$(TARGET)

# AddressSanitizer build
asan: CFLAGS = -O1 -g -std=c11 -Wall -Wextra -fsanitize=address,undefined -fno-omit-frame-pointer
asan: $(TARGET)
	@echo "Built with AddressSanitizer + UndefinedBehaviorSanitizer"

# UndefinedBehaviorSanitizer build
ubsan: CFLAGS = -O1 -g -std=c11 -Wall -Wextra -fsanitize=undefined -fno-omit-frame-pointer
ubsan: $(TARGET)
	@echo "Built with UndefinedBehaviorSanitizer"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -f $(TARGET) $(THALES_TARGET)
	@echo "Clean complete"

# Help target
help:
	@echo "Z5D Pascal-Only Model + Thales Filter — Stage −1/0/S Filter Build System"
	@echo "======================================================================"
	@echo ""
	@echo "Available targets:"
	@echo "  build     - Build z5d_pascal_filter executable (default)"
	@echo "  thales    - Build thales_filter executable"
	@echo "  run       - Build and run the Pascal filter demo"
	@echo "  run-thales - Build and run the Thales filter test"
	@echo "  bench     - Run timing benchmarks"
	@echo "  asan      - Build with AddressSanitizer + UBSan"
	@echo "  ubsan     - Build with UndefinedBehaviorSanitizer"
	@echo "  clean     - Remove build artifacts"
	@echo "  help      - Show this help message"
	@echo ""
	@echo "Build flags:"
	@echo "  Pascal: $(CFLAGS)"
	@echo "  Thales: $(THALES_CFLAGS)"
	@echo ""
	@echo "Requirements:"
	@echo "  - GCC or Clang with __int128 support"
	@echo "  - POSIX-compliant system (for clock_gettime)"
	@echo "  - MPFR and GMP libraries (for Thales filter)"
	@echo "  - Optional: libomp for OpenMP (parallelization)"