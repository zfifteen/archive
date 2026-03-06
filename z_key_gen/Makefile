# Makefile for z5d_secure_key_gen — Z5D RSA-4096 Secure Key Generator
#
# **Z5D SECURE RSA KEY GENERATOR** - Creates cryptographically secure RSA keys
# using Z5D predictor with high-entropy seed generation.

CC = clang
CFLAGS = -Wall -Wextra -Wno-deprecated-declarations -O3 -std=c99 -mcpu=apple-m1 -ffast-math -fstrict-aliasing -funroll-loops -DZ5D_USE_AMX=1
OPENSSL_PREFIX = $(shell brew --prefix openssl@3 2>/dev/null || brew --prefix openssl 2>/dev/null || echo "/opt/homebrew/opt/openssl@3")
GMP_PREFIX = $(shell brew --prefix gmp 2>/dev/null || echo "/opt/homebrew/opt/gmp")
MPFR_PREFIX = $(shell brew --prefix mpfr 2>/dev/null || echo "/opt/homebrew/opt/mpfr")
LIBOMP_PREFIX = $(shell brew --prefix libomp 2>/dev/null || echo "/opt/homebrew/opt/libomp")
PKG_CONFIG = $(shell which pkg-config 2>/dev/null || echo "/opt/homebrew/bin/pkg-config")

# Directories
SRC_DIR = src
INCLUDE_DIR = include
BUILD_DIR = build
BIN_DIR = bin

INCLUDES = -I$(INCLUDE_DIR) -I$(OPENSSL_PREFIX)/include -I$(GMP_PREFIX)/include -I$(MPFR_PREFIX)/include
LDFLAGS = -L$(OPENSSL_PREFIX)/lib -L$(GMP_PREFIX)/lib -L$(MPFR_PREFIX)/lib
LIBS = -lmpfr -lgmp -lssl -lcrypto -lm

LIBOMP_LIB_PATH := $(LIBOMP_PREFIX)/lib
LIBOMP_INCLUDE_PATH := $(LIBOMP_PREFIX)/include

ifneq ("$(wildcard $(LIBOMP_LIB_PATH))","")
OPENMP_CFLAGS := -Xpreprocessor -fopenmp -I$(LIBOMP_INCLUDE_PATH)
OPENMP_LDFLAGS := -L$(LIBOMP_LIB_PATH) -lomp
CFLAGS += $(OPENMP_CFLAGS)
LDFLAGS += $(OPENMP_LDFLAGS)
OPENMP_ENABLED := 1
else
$(warning "libomp not found via Homebrew — building without OpenMP support")
OPENMP_ENABLED := 0
endif

# Source files
MAIN_SRC = $(SRC_DIR)/z5d_key_gen.c
Z5D_SRC = $(SRC_DIR)/z5d_predictor.c
OBJC_SRC = $(SRC_DIR)/gpu_info.m
SOURCES = $(MAIN_SRC) $(Z5D_SRC)

# Object files
OBJC_OBJ = $(BUILD_DIR)/$(notdir $(OBJC_SRC:.m=.o))
OBJS = $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.o,$(SOURCES))

# Target binary
TARGET = $(BIN_DIR)/z5d_secure_key_gen

# Default target
all: $(TARGET)

# Build the main target
$(TARGET): $(OBJS) $(OBJC_OBJ) | $(BIN_DIR)
	$(CC) $(CFLAGS) $(INCLUDES) $(LDFLAGS) -o $@ $^ $(LIBS) -framework Metal -framework Foundation

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

$(OBJC_OBJ): $(OBJC_SRC) | $(BUILD_DIR)
	$(CC) -fobjc-arc -ObjC $(CFLAGS) $(INCLUDES) -c $< -o $@

# Create directories
$(BUILD_DIR) $(BIN_DIR):
	mkdir -p $@

# Test the build
test: $(TARGET)
	@echo "=== Testing Z5D Secure Key Generator ==="
	$(TARGET) --quiet
	@echo ""
	@echo "=== Generated files ==="
	@ls -la generated/z5d_key_gen-*.key generated/z5d_key_gen-*.crt 2>/dev/null || echo "No output files found"

# Clean build artifacts and generated keys
clean:
	rm -rf $(BIN_DIR) $(BUILD_DIR) generated/

# Show help
help:
	@echo "Z5D Secure RSA Key Generator - Standalone Build"
	@echo ""
	@echo "Available targets:"
	@echo "  all          Build the z5d_secure_key_gen tool"
	@echo "  test         Build and test with secure entropy"
	@echo "  clean        Remove build artifacts and generated keys"
	@echo "  help         Show this help"
	@echo ""
	@echo "Dependencies (install with Homebrew):"
	@echo "  brew install openssl gmp mpfr libomp"
	@echo ""
	@echo "Usage: ./bin/z5d_secure_key_gen [OPTIONS]"
	@echo "Run './bin/z5d_secure_key_gen --help' for option details"

.PHONY: all test clean help
