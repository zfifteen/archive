# Makefile for LogLog MPFR Library
# C99 standard with GMP/MPFR support

CC = gcc
CFLAGS = -std=c99 -Wall -Wextra -O2 -pedantic
LDFLAGS = -lgmp -lmpfr

# Source files
SOURCES = loglog_mpfr.c
HEADERS = loglog_mpfr.h
OBJECTS = loglog_mpfr.o

# Test and benchmark files
TEST_SOURCE = test_loglog.c
TEST_BINARY = test_loglog

BENCHMARK_SOURCE = benchmark_loglog.c
BENCHMARK_BINARY = benchmark_loglog

# Library outputs
LIBRARY_STATIC = libloglog_mpfr.a

# Default target
.PHONY: all
all: $(LIBRARY_STATIC) $(TEST_BINARY) $(BENCHMARK_BINARY)

# Build static library
$(LIBRARY_STATIC): $(OBJECTS)
	ar rcs $@ $^
	@echo "Built static library: $@"

# Build object file
%.o: %.c $(HEADERS)
	$(CC) $(CFLAGS) -c $< -o $@

# Build test binary
$(TEST_BINARY): $(TEST_SOURCE) $(LIBRARY_STATIC)
	$(CC) $(CFLAGS) $< -L. -lloglog_mpfr $(LDFLAGS) -o $@
	@echo "Built test binary: $@"

# Build benchmark binary
$(BENCHMARK_BINARY): $(BENCHMARK_SOURCE) $(LIBRARY_STATIC)
	$(CC) $(CFLAGS) $< -L. -lloglog_mpfr $(LDFLAGS) -o $@
	@echo "Built benchmark binary: $@"

# Run tests
.PHONY: test
test: $(TEST_BINARY)
	@echo "Running tests..."
	./$(TEST_BINARY)

# Run benchmarks
.PHONY: benchmark
benchmark: $(BENCHMARK_BINARY)
	@echo "Running benchmarks..."
	./$(BENCHMARK_BINARY)

# Clean build artifacts
.PHONY: clean
clean:
	rm -f $(OBJECTS) $(LIBRARY_STATIC) $(TEST_BINARY) $(BENCHMARK_BINARY)
	@echo "Cleaned build artifacts"

# Help target
.PHONY: help
help:
	@echo "LogLog MPFR Library Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  all        - Build library, tests, and benchmarks (default)"
	@echo "  test       - Build and run test suite"
	@echo "  benchmark  - Build and run benchmark suite"
	@echo "  clean      - Remove all build artifacts"
	@echo "  help       - Show this help message"
	@echo ""
	@echo "Outputs:"
	@echo "  $(LIBRARY_STATIC)    - Static library"
	@echo "  $(TEST_BINARY)       - Test executable"
	@echo "  $(BENCHMARK_BINARY)  - Benchmark executable"

.PHONY: info
info:
	@echo "Compiler: $(CC)"
	@echo "C Standard: C99"
	@echo "Flags: $(CFLAGS)"
	@echo "Libraries: GMP, MPFR"
