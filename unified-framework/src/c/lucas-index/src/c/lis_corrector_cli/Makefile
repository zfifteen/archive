# LIS Corrector CLI (Z5D seed + LIS + MR)

CC := clang
UNAME_S := $(shell uname -s 2>/dev/null || echo Unknown)

SRC_DIR := .
BUILD_DIR := build
BIN_DIR := bin

INC := -I. -I../lis_corrector -I../lis -I..
CFLAGS := -std=c11 -O3 -Wall -Wextra $(INC)
LDFLAGS :=

# Detect MPFR/GMP locations (Homebrew/Unix fallbacks)
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
    elif test -f /usr/local/lib/libmpfr.a -o -f /usr/local/lib/libmpfr.dylib; then echo -L/usr/local/lib -lmpfr -lgmp; \
    elif test -f /usr/lib/libmpfr.so; then echo -L/usr/lib -lmpfr -lgmp; \
    else echo -lmpfr -lgmp; fi)

CFLAGS += $(GMP_INCLUDE) $(MPFR_INCLUDE)

ifeq ($(UNAME_S),Linux)
    LDFLAGS += -Wl,-rpath,../lis_corrector/lib -Wl,-rpath,../lis/lib -Wl,-rpath,../lib
else ifeq ($(UNAME_S),Darwin)
    LDFLAGS += -Wl,-rpath,../lis_corrector/lib -Wl,-rpath,../lis/lib -Wl,-rpath,/opt/homebrew/lib -Wl,-rpath,/usr/local/lib
endif

TARGET := $(BIN_DIR)/lis_corrector_cli
OBJECTS := $(BUILD_DIR)/lis_corrector_cli.o

.DEFAULT_GOAL := all

all: $(TARGET)

$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

$(BIN_DIR):
	@mkdir -p $(BIN_DIR)

$(BUILD_DIR)/%.o: %.c | $(BUILD_DIR)
	@echo "Compiling: $<"
	@$(CC) $(CFLAGS) -c $< -o $@

$(TARGET): $(OBJECTS) | $(BIN_DIR)
	@echo "Linking: $@"
	@$(CC) -o $@ $^ -L../lis_corrector/lib -llis_corrector -L../lis/lib -llis -L../lib -lz5d $(MPFR_LDFLAGS) $(LDFLAGS)

clean:
	@rm -rf $(BUILD_DIR) $(BIN_DIR)

.PHONY: all clean

